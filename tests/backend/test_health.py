"""
Tests for System Health, Device Status, and Device Capabilities APIs.
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

def test_health_endpoint():
    """Verify /api/health responds with 200 OK and valid metadata."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["project"] == "TEJAS"
    assert "version" in data
    assert "ai_mode" in data
    assert "demo_mode" in data

def test_device_status_dynamic_reporting():
    """Verify /api/device/status returns dynamic subsystem statuses."""
    response = client.get("/api/device/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["OK", "WARNING", "ERROR"]
    assert "cpu_usage_percent" in data
    assert "ram_usage_percent" in data
    assert "storage_usage_percent" in data
    assert "battery" in data
    assert "subsystems" in data
    assert "camera" in data["subsystems"]
    assert "soil_sensor" in data["subsystems"]
    assert "ai_engine" in data["subsystems"]
    assert "database" in data["subsystems"]

def test_device_capabilities_structure():
    """Verify /api/device/capabilities returns 6 parameters and correct languages."""
    response = client.get("/api/device/capabilities")
    assert response.status_code == 200
    data = response.json()
    assert data["offline_capable"] is True
    assert set(data["supported_languages"]) == {"en", "hi", "mr"}
    assert len(data["soil_sensor_parameters"]) == 6
    expected_params = ["Nitrogen", "Phosphorus", "Potassium", "pH", "Moisture", "Temperature"]
    for p in expected_params:
        assert p in data["soil_sensor_parameters"]
