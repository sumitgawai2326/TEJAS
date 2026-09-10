"""
Tests for Phase 2 Subsystems API Routes: /camera/status, /soil/status, /ai/status.
"""
import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app
from app.core.config import settings

client = TestClient(app)

def test_api_camera_status():
    """Verify GET /api/camera/status returns camera diagnostics."""
    response = client.get("/api/camera/status")
    assert response.status_code == 200
    data = response.json()
    assert "driver" in data
    assert "available" in data
    assert "status" in data
    assert "mode" in data

def test_api_soil_status():
    """Verify GET /api/soil/status returns soil sensor link status."""
    response = client.get("/api/soil/status")
    assert response.status_code == 200
    data = response.json()
    assert "driver" in data
    assert "connected" in data
    assert "status" in data
    assert "is_mock" in data

def test_api_ai_status():
    """Verify GET /api/ai/status returns AI model and accelerator status."""
    response = client.get("/api/ai/status")
    assert response.status_code == 200
    data = response.json()
    assert data["ready"] is True
    assert "accelerator_type" in data
    assert "inference_mode" in data
    assert "confidence_threshold" in data
    assert "supported_classes" in data
    assert len(data["supported_classes"]) > 0

def test_real_mode_subsystem_statuses():
    """Verify in DEMO_MODE=false, subsystems report real hardware status."""
    orig = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = False
        res_soil = client.get("/api/soil/status")
        assert res_soil.status_code == 200
        soil_data = res_soil.json()
        assert soil_data["is_mock"] is False
        assert soil_data["status"] in ["UNCONFIGURED_REGISTER_MAP", "SENSOR DISCONNECTED"]

        res_cam = client.get("/api/camera/status")
        assert res_cam.status_code == 200
        cam_data = res_cam.json()
        assert cam_data["is_mock"] is False
    finally:
        settings.DEMO_MODE = orig
