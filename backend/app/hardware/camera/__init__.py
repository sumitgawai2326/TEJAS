"""
Camera Factory Selector.
"""
from app.hardware.camera.base import BaseCamera
from app.hardware.camera.mock_camera import MockCamera
from app.hardware.camera.camera_hal import CameraHAL
from app.core.config import settings

def get_camera() -> BaseCamera:
    if settings.DEMO_MODE:
        return MockCamera()
    return CameraHAL(
        camera_device=settings.CAMERA_DEVICE,
        width=settings.CAMERA_WIDTH,
        height=settings.CAMERA_HEIGHT,
        fps=settings.CAMERA_FPS
    )
