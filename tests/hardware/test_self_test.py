"""
Automated Unit Tests for Hardware Self-Test Subsystem & REST API.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.self_test import DeviceSelfTestService

@pytest.fixture
def client():
    return TestClient(app)

def test_device_self_test_service_execution():
    """Verify self-test evaluates all 6 subsystems and returns valid overall status."""
    res = DeviceSelfTestService.run_self_test()
    assert res.overall_status in ["DEVICE READY", "DEVICE READY WITH WARNINGS", "DEVICE INITIALIZATION FAILED"]
    assert res.passed_count + res.warning_count + res.failed_count == len(res.items)
    assert len(res.items) >= 6

    subsystems = [i.subsystem for i in res.items]
    assert "Local SQLite Database" in subsystems
    assert "Edge Local Storage" in subsystems
    assert "Camera Subsystem" in subsystems
    assert "6-Parameter Soil Sensor" in subsystems
    assert "AI Inference Engine" in subsystems
    assert "Host Platform & Runtime" in subsystems

def test_api_device_self_test_endpoint(client):
    """Verify GET /api/device/self-test endpoint returns 200 OK and valid schema."""
    response = client.get("/api/device/self-test")
    assert response.status_code == 200
    data = response.json()
    assert "overall_status" in data
    assert "passed_count" in data
    assert "items" in data
    assert isinstance(data["items"], list)

def test_api_device_status_platform_fields(client):
    """Verify GET /api/device/status returns platform info and serial ports."""
    response = client.get("/api/device/status")
    assert response.status_code == 200
    data = response.json()
    assert "platform" in data
    assert "board_model" in data["platform"]
    assert "serial_ports" in data
    assert isinstance(data["serial_ports"], list)
