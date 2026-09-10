"""
Comprehensive Unit & Integration Tests for Phase 4: Offline Edge AI Vision Pipeline.
Validates:
1. Image Quality Validator (Blur, Exposure, Resolution, Farmer-friendly Guidance)
2. Image Preprocessor (Resizing, Normalization, NCHW Tensor Output)
3. Vision Model Manager & Strict Confidence Gating
4. Zero Hardware Hallucination in Real Hardware Mode (Missing Model = AI_NOT_READY)
5. Vision API Routes (/api/vision/analyze, /api/vision/status) and SQLite Persistence
"""
import os
import io
import cv2
import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from ai.preprocessing.quality import ImageQualityValidator
from ai.preprocessing.preprocessor import ImagePreprocessor
from ai.inference.manager import VisionModelManager
from ai.inference.backends import DemoModelBackend
from app.db.database import get_db, Base, engine, SessionLocal, init_db
from app.db.models import Farm, Field, Scan

@pytest.fixture(autouse=True)
def setup_db():
    init_db()


client = TestClient(app)

def create_synthetic_image(width=300, height=300, brightness=128, sharp=True) -> np.ndarray:
    """Helper creating a test image with controllable sharpness and brightness."""
    img = np.full((height, width, 3), brightness, dtype=np.uint8)
    if sharp:
        # Draw high-contrast patterns/lines to provide rich edges/Laplacian variance
        for i in range(10, min(width, height) - 10, 20):
            cv2.rectangle(img, (i, i), (width - i, height - i), (0, 255, 0), 2)
            cv2.putText(img, "LEAF VEIN", (i + 5, i + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)
    return img

def encode_image_bytes(img: np.ndarray, ext=".jpg") -> bytes:
    """Helper encoding numpy BGR image to bytes."""
    success, buffer = cv2.imencode(ext, img)
    assert success
    return buffer.tobytes()

# ---------------------------------------------------------
# 1. Image Quality Validator Tests
# ---------------------------------------------------------

def test_image_quality_valid_leaf():
    validator = ImageQualityValidator()
    img = create_synthetic_image(300, 300, brightness=130, sharp=True)
    res = validator.validate(img)
    
    assert res.valid is True
    assert res.score > 0.6
    assert len(res.issues) == 0
    assert "optimal" in res.message.lower()
    assert res.resolution == "300x300"
    assert res.blur_score >= 18.0

def test_image_quality_blurry():
    validator = ImageQualityValidator()
    # A flat, uniform image has zero edge variance (blurry / out of focus)
    img = create_synthetic_image(300, 300, brightness=130, sharp=False)
    res = validator.validate(img)
    
    assert res.valid is False
    assert "IMAGE_TOO_BLURRY" in res.issues
    assert res.blur_score < 18.0
    assert "blurry" in res.message.lower()

def test_image_quality_too_dark():
    validator = ImageQualityValidator()
    img = np.full((200, 200, 3), 10, dtype=np.uint8) # mean brightness = 10 (< 20)
    res = validator.validate(img)
    
    assert res.valid is False
    assert "IMAGE_TOO_DARK" in res.issues
    assert "too dark" in res.message.lower()

def test_image_quality_overexposed():
    validator = ImageQualityValidator()
    img = np.full((200, 200, 3), 250, dtype=np.uint8) # mean brightness = 250 (> 240)
    res = validator.validate(img)
    
    assert res.valid is False
    assert "IMAGE_TOO_BRIGHT" in res.issues
    assert "glare" in res.message.lower() or "overexposed" in res.message.lower()

def test_image_quality_low_resolution():
    validator = ImageQualityValidator(min_width=120, min_height=120)
    img = create_synthetic_image(80, 80, brightness=128, sharp=True)
    res = validator.validate(img)
    
    assert res.valid is False
    assert "IMAGE_TOO_SMALL" in res.issues
    assert "closer" in res.message.lower()

def test_image_quality_corrupt_bytes():
    validator = ImageQualityValidator()
    decoded = validator.decode_image(b"invalid garbage bytes")
    assert decoded is None
    res = validator.validate(decoded)
    assert res.valid is False
    assert "INVALID_IMAGE" in res.issues

# ---------------------------------------------------------
# 2. Image Preprocessor Tests
# ---------------------------------------------------------

def test_image_preprocessor_output_tensor():
    preprocessor = ImagePreprocessor(target_size=(224, 224))
    img = create_synthetic_image(400, 300, brightness=128, sharp=True)
    tensor = preprocessor.preprocess(img)
    
    # NCHW format: (1, 3, 224, 224)
    assert tensor.shape == (1, 3, 224, 224)
    assert tensor.dtype == np.float32
    assert isinstance(tensor, np.ndarray)


# ---------------------------------------------------------
# 3. Vision Model Manager & Confidence Gating Tests
# ---------------------------------------------------------

def test_vision_manager_demo_accepted():
    manager = VisionModelManager(demo_mode=True, confidence_threshold=0.70)
    assert manager.is_model_ready() is True
    
    img = create_synthetic_image(224, 224, brightness=128, sharp=True)
    validator = ImageQualityValidator()
    quality_res = validator.validate(img)
    
    res = manager.analyze_image(img, quality_res, raw_confidence_override=0.88)
    assert res["status"] == "accepted"
    assert res["confidence"] == 0.88
    assert res["is_demo"] is True
    assert "Tomato Early Blight" in res["prediction"]

def test_vision_manager_confidence_gating_fail():
    manager = VisionModelManager(demo_mode=True, confidence_threshold=0.70)
    img = create_synthetic_image(224, 224, brightness=128, sharp=True)
    validator = ImageQualityValidator()
    quality_res = validator.validate(img)
    
    # Override with confidence 0.52 (< 0.70 threshold)
    res = manager.analyze_image(img, quality_res, raw_confidence_override=0.52)
    assert res["status"] == "low_confidence"
    assert res["prediction"] == "Unknown / Low Confidence"
    assert res["confidence"] == 0.52
    assert "uncertain" in res["message"].lower()

def test_vision_manager_real_mode_zero_hallucination():
    """
    In DEMO_MODE=False, if no physical ONNX model file exists on disk,
    the manager MUST NOT fabricate predictions and MUST report AI_NOT_READY / ai_unavailable.
    """
    manager = VisionModelManager(
        demo_mode=False,
        confidence_threshold=0.70,
        model_path="ai/models/non_existent_model_file.onnx"
    )
    assert manager.is_model_ready() is False
    
    status = manager.get_status()
    assert status.ready is False
    assert status.model_available is False
    assert "not found" in (status.reason_if_unavailable or "").lower()
    
    img = create_synthetic_image(224, 224, brightness=128, sharp=True)
    validator = ImageQualityValidator()
    quality_res = validator.validate(img)
    
    res = manager.analyze_image(img, quality_res)
    assert res["status"] == "ai_unavailable"
    assert res["prediction"] == "AI Unavailable"
    assert res["confidence"] == 0.0

# ---------------------------------------------------------
# 4. Vision API Route Tests
# ---------------------------------------------------------

def test_api_vision_status():
    response = client.get("/api/vision/status")
    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "accelerator" in data
    assert "confidence_threshold" in data
    assert data["confidence_threshold"] == settings.AI_CONFIDENCE_THRESHOLD

def test_api_vision_analyze_valid_upload():
    # Setup test farm and field in database
    db = SessionLocal()
    farm = Farm(name="Vision Test Farm", location_name="Pune, Maharashtra")
    db.add(farm)
    db.commit()
    db.refresh(farm)
    field = Field(name="Tomato Patch North", farm_id=farm.id, area=1.5, soil_type="Loamy")
    db.add(field)
    db.commit()
    db.refresh(field)
    field_id = field.id
    db.close()

    img = create_synthetic_image(300, 300, brightness=130, sharp=True)
    img_bytes = encode_image_bytes(img)
    
    response = client.post(
        "/api/vision/analyze",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")},
        data={"field_id": str(field_id), "confidence_override": "0.91"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["confidence"] == 0.91
    assert data["field_id"] == field_id
    assert data["scan_id"] is not None
    assert data["image_quality"]["valid"] is True
    assert data["image_path"] is not None

def test_api_vision_analyze_blurry_rejected():
    img = create_synthetic_image(300, 300, brightness=130, sharp=False)
    img_bytes = encode_image_bytes(img)
    
    response = client.post(
        "/api/vision/analyze",
        files={"file": ("blurry_leaf.jpg", img_bytes, "image/jpeg")},
        data={"confidence_override": "0.95"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "invalid_image"
    assert data["image_quality"]["valid"] is False
    assert "IMAGE_TOO_BLURRY" in data["image_quality"]["issues"]
    assert "blurry" in data["message"].lower()

def test_api_vision_analyze_camera_capture():
    response = client.post(
        "/api/vision/analyze",
        data={"use_camera": "true", "confidence_override": "0.85"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["confidence"] == 0.85
    assert data["image_quality"]["valid"] is True
