"""
Integration tests for Phase 3 Field, Soil, Scan, and History API Endpoints.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app
from app.core.config import settings
from app.db.database import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def test_create_and_list_fields():
    """Verify POST /api/fields and GET /api/fields."""
    payload = {
        "name": "Wheat Sector 4",
        "area": 5.0,
        "area_unit": "Acre",
        "soil_type": "Loamy"
    }
    response = client.post("/api/fields", json=payload)
    assert response.status_code == 201
    field_data = response.json()
    assert field_data["name"] == "Wheat Sector 4"
    field_id = field_data["id"]

    list_res = client.get("/api/fields")
    assert list_res.status_code == 200
    fields = list_res.json()
    assert any(f["id"] == field_id for f in fields)

def test_get_field_by_id():
    """Verify GET /api/fields/{id} with valid and invalid IDs."""
    create_res = client.post("/api/fields", json={"name": "Chilli Plot"})
    field_id = create_res.json()["id"]

    res = client.get(f"/api/fields/{field_id}")
    assert res.status_code == 200
    assert res.json()["name"] == "Chilli Plot"

    # Invalid ID check
    res_404 = client.get("/api/fields/99999")
    assert res_404.status_code == 404

def test_record_and_list_scans():
    """Verify POST /api/fields/{id}/scans and GET /api/fields/{id}/scans."""
    create_res = client.post("/api/fields", json={"name": "Potato Field"})
    field_id = create_res.json()["id"]

    scan_payload = {
        "prediction": "Potato Late Blight",
        "confidence": 0.94,
        "model_name": "DemoVision",
        "model_version": "0.1.0",
        "status": "CONFIDENT"
    }
    scan_res = client.post(f"/api/fields/{field_id}/scans", json=scan_payload)
    assert scan_res.status_code == 201
    assert scan_res.json()["prediction"] == "Potato Late Blight"

    list_res = client.get(f"/api/fields/{field_id}/scans")
    assert list_res.status_code == 200
    scans = list_res.json()
    assert len(scans) >= 1
    assert scans[0]["prediction"] == "Potato Late Blight"

def test_record_soil_reading_demo_mode():
    """Verify POST /api/fields/{id}/soil in DEMO_MODE=True saves mock telemetry."""
    orig = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = True
        create_res = client.post("/api/fields", json={"name": "Cotton Block"})
        field_id = create_res.json()["id"]

        soil_res = client.post(f"/api/fields/{field_id}/soil")
        assert soil_res.status_code == 201
        data = soil_res.json()
        assert data["is_mock"] is True
        assert data["sensor_status"] == "DEMO_SIMULATION"
        assert data["nitrogen"] is not None
    finally:
        settings.DEMO_MODE = orig

def test_record_soil_reading_real_mode_zero_hallucination():
    """
    CRITICAL: Verify POST /api/fields/{id}/soil in DEMO_MODE=False
    with disconnected sensor NEVER stores fake numbers.
    """
    orig = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = False
        create_res = client.post("/api/fields", json={"name": "Organic Soil Bed"})
        field_id = create_res.json()["id"]

        soil_res = client.post(f"/api/fields/{field_id}/soil")
        assert soil_res.status_code == 201
        data = soil_res.json()
        assert data["is_mock"] is False
        assert data["sensor_status"] in ["UNCONFIGURED_REGISTER_MAP", "SENSOR DISCONNECTED"]
        assert data["nitrogen"] is None
        assert data["phosphorus"] is None
        assert data["potassium"] is None
        assert data["ph"] is None
        assert data["moisture"] is None
        assert data["temperature"] is None
    finally:
        settings.DEMO_MODE = orig

def test_get_field_history_timeline():
    """Verify GET /api/fields/{id}/history returns combined timeline."""
    create_res = client.post("/api/fields", json={"name": "Timeline Field"})
    field_id = create_res.json()["id"]

    # Add a scan and soil reading
    client.post(f"/api/fields/{field_id}/scans", json={
        "prediction": "Healthy Leaf",
        "confidence": 0.98,
        "model_name": "DemoVision",
        "model_version": "0.1.0"
    })
    client.post(f"/api/fields/{field_id}/soil")

    hist_res = client.get(f"/api/fields/{field_id}/history")
    assert hist_res.status_code == 200
    data = hist_res.json()
    assert data["field_id"] == field_id
    assert data["total_timeline_entries"] >= 2
    assert "timeline" in data
    assert any(entry["type"] == "SCAN" for entry in data["timeline"])
    assert any(entry["type"] == "SOIL_READING" for entry in data["timeline"])
