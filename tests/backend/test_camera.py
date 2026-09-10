"""
Tests for Camera Hardware Abstraction Layer.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.hardware.camera.mock_camera import MockCamera
from app.hardware.camera.camera_hal import CameraHAL
from app.hardware.camera import get_camera
from app.core.config import settings

def test_mock_camera_demo_mode():
    """Verify MockCamera functions for demo viewfinder."""
    cam = MockCamera()
    assert cam.is_available() is True
    status = cam.get_status()
    assert status["is_mock"] is True
    assert status["mode"] == "DEMO_SIMULATION"
    assert status["available"] is True
    
    success, frame, meta = cam.capture()
    assert success is True
    assert meta["is_mock"] is True
    assert meta["source"] == "DEMO_SAMPLE_VIEWFINDER"

def test_camera_hal_unavailable_state():
    """
    Verify CameraHAL handles invalid camera device indices gracefully
    without claiming false availability.
    """
    cam = CameraHAL(camera_device=99)
    status = cam.get_status()
    assert status["is_mock"] is False
    assert status["mode"] == "REAL_HARDWARE"
    if not status["available"]:
        assert status["status"] == "CAMERA_UNAVAILABLE"
        success, frame, meta = cam.capture()
        assert success is False
        assert frame is None
        assert meta["source"] == "CAMERA_UNAVAILABLE"

def test_camera_factory_mode_switching():
    """Verify get_camera() respects settings.DEMO_MODE."""
    orig = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = True
        cam_demo = get_camera()
        assert isinstance(cam_demo, MockCamera)

        settings.DEMO_MODE = False
        cam_real = get_camera()
        assert isinstance(cam_real, CameraHAL)
    finally:
        settings.DEMO_MODE = orig
