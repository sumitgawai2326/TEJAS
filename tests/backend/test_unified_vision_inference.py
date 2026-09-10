import io
import os
import glob
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app
from app.core.config import settings
from app.db.database import init_db, SessionLocal
from app.db.models import Farm, Field, Scan, SoilReading, RiskAssessment, Advisory
from app.ai.inference.disease_engine import disease_engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def get_real_sample_image_bytes() -> bytes:
    dataset_samples = glob.glob('ml/data/processed/tomato_cls/test/*/*.*')
    if not dataset_samples:
        dataset_samples = glob.glob('../ml/data/processed/tomato_cls/test/*/*.*')
    if dataset_samples:
        with open(dataset_samples[0], 'rb') as f:
            return f.read()
    img = Image.new('RGB', (256, 256), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format='JPEG')
    return buf.getvalue()

def test_disease_engine_direct_prediction():
    img_bytes = get_real_sample_image_bytes()
    res = disease_engine.predict(img_bytes)
    assert res['success'] is True
    assert res['model'] == 'tejas_tomato_yolo11n'
    assert 'prediction' in res
    assert 'class_name' in res['prediction']
    assert len(res['top_predictions']) == 3

def test_unified_prediction_across_endpoints():
    img_bytes = get_real_sample_image_bytes()

    # 1. Standalone predict endpoint
    r1 = client.post('/api/v1/disease/predict', files={'file': ('leaf.jpg', img_bytes, 'image/jpeg')})
    assert r1.status_code == 200
    d1 = r1.json()
    assert d1['success'] is True
    assert d1['model'] == 'tejas_tomato_yolo11n'
    top1_class = d1['prediction']['class_name']
    top1_conf = d1['prediction']['confidence']

    # 2. Alias predict endpoint
    r2 = client.post('/api/disease/predict', files={'file': ('leaf.jpg', img_bytes, 'image/jpeg')})
    assert r2.status_code == 200
    d2 = r2.json()
    assert d2['prediction']['class_name'] == top1_class
    assert d2['prediction']['confidence'] == top1_conf

    # 3. Vision analyze endpoint (used by Wizard)
    r3 = client.post('/api/vision/analyze', files={'file': ('leaf.jpg', img_bytes, 'image/jpeg')})
    assert r3.status_code == 200
    d3 = r3.json()
    assert d3['model_name'] == 'tejas_tomato_yolo11n'
    assert d3['status'] == 'accepted'
    assert d3['prediction'] == top1_class.replace('_', ' ')
    assert abs(d3['confidence'] - top1_conf) < 0.01
    assert 'top_predictions' in d3
    assert len(d3['top_predictions']) == 3

def test_fields_analyze_uses_disease_engine():
    db = SessionLocal()
    farm = Farm(name='Unification Test Farm', location_name='Maharashtra')
    db.add(farm)
    db.commit()
    db.refresh(farm)
    field = Field(name='Tomato South Plot', farm_id=farm.id, area=2.0, soil_type='Black Cotton')
    db.add(field)
    db.commit()
    db.refresh(field)
    field_id = field.id
    db.close()

    img_bytes = get_real_sample_image_bytes()
    r = client.post(
        f'/api/fields/{field_id}/analyze',
        files={'file': ('leaf.jpg', img_bytes, 'image/jpeg')},
        data={'trigger_soil_read': 'true'}
    )
    assert r.status_code == 200
    data = r.json()
    assert data['vision']['model_name'] == 'tejas_tomato_yolo11n'
    assert data['vision']['status'] == 'accepted'
    assert 'risk' in data
    assert data['risk']['risk_level'] in ['LOW', 'MODERATE', 'HIGH', 'CRITICAL']
    assert len(data['advisories']) > 0

def test_confidence_gating_in_unified_vision():
    db = SessionLocal()
    farm = Farm(name='Gating Test Farm')
    db.add(farm)
    db.commit()
    db.refresh(farm)
    field = Field(name='Gating Field', farm_id=farm.id, area=1.0)
    db.add(field)
    db.commit()
    db.refresh(field)
    field_id = field.id
    db.close()

    img_bytes = get_real_sample_image_bytes()
    r_low = client.post(
        '/api/vision/analyze',
        files={'file': ('leaf.jpg', img_bytes, 'image/jpeg')},
        data={'field_id': str(field_id), 'confidence_override': '0.55'}
    )
    assert r_low.status_code == 200
    d_low = r_low.json()
    assert d_low['status'] == 'low_confidence'
    assert d_low['confidence_tier'] == 'LOW'
    assert d_low['prediction'] == 'Unknown / Low Confidence'

    r_high = client.post(
        '/api/vision/analyze',
        files={'file': ('leaf.jpg', img_bytes, 'image/jpeg')},
        data={'field_id': str(field_id), 'confidence_override': '0.92'}
    )
    assert r_high.status_code == 200
    d_high = r_high.json()
    assert d_high['status'] == 'accepted'
    assert d_high['confidence_tier'] == 'HIGH'
