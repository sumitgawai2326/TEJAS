"""Hardware Abstraction Layer (HAL)."""
from app.hardware.detection import SystemDetector
from app.hardware.camera import get_camera
from app.hardware.soil_sensor import get_soil_sensor

__all__ = ["SystemDetector", "get_camera", "get_soil_sensor"]
