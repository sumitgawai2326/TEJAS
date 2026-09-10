"""
Dedicated Hardware Subsystems Status Endpoints: Camera, Soil Sensor, and AI Accelerator.
"""
import os
import sys
import datetime
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.camera import CameraStatus
from app.schemas.soil import SensorStatus
from app.schemas.ai import AIStatus
from app.hardware.camera import get_camera
from app.hardware.soil_sensor import get_soil_sensor
from app.ai.inference.base import get_vision_model

router = APIRouter(tags=["Hardware Subsystems Status"])

@router.get("/camera/status", response_model=CameraStatus)
async def get_camera_status():
    """Returns live camera hardware diagnostics."""
    cam = get_camera()
    status_dict = cam.get_status()
    return CameraStatus(
        driver=status_dict["driver"],
        mode=status_dict["mode"],
        available=status_dict["available"],
        status=status_dict["status"],
        is_mock=status_dict["is_mock"],
        camera_device_index=status_dict["camera_device_index"],
        resolution=status_dict.get("resolution"),
        fps=status_dict.get("fps"),
        details=status_dict.get("details"),
        last_check=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

@router.get("/soil/status", response_model=SensorStatus)
async def get_soil_status():
    """Returns live RS485 Modbus soil sensor status."""
    sensor = get_soil_sensor()
    status_dict = sensor.get_status()
    return SensorStatus(
        driver=status_dict["driver"],
        mode=status_dict["mode"],
        connected=status_dict["connected"],
        status=status_dict["status"],
        is_mock=status_dict["is_mock"],
        port=status_dict.get("port"),
        baudrate=status_dict.get("baudrate"),
        details=status_dict.get("details"),
        last_health_check=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

@router.get("/ai/status", response_model=AIStatus)
async def get_ai_status():
    """Returns live AI accelerator and model status."""
    vision_model = get_vision_model(
        confidence_threshold=settings.AI_CONFIDENCE_THRESHOLD,
        ai_mode=settings.AI_MODE
    )
    return vision_model.get_status()
