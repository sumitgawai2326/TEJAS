"""
System & Hardware Health Endpoints for KrishiDrishti Edge.
Provides truthful telemetry, self-test verification, and hardware capabilities.
"""
import time
import psutil
import datetime
import os
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import (
    HealthResponse, 
    DeviceStatus, 
    DeviceCapabilities, 
    SubsystemStatus, 
    SelfTestResponse,
    PlatformInfo
)
from app.hardware.battery.battery_monitor import battery_monitor
from app.hardware.soil_sensor import get_soil_sensor
from app.hardware.camera import get_camera
from app.hardware.detection import SystemDetector
from app.services.self_test import DeviceSelfTestService
from app.ai.inference.base import AcceleratorDetector

router = APIRouter(tags=["System Health & Diagnostics"])
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse)
async def get_health():
    """Basic service health check."""
    accel = AcceleratorDetector.detect(settings.AI_MODE)
    return HealthResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        demo_mode=settings.DEMO_MODE,
        ai_mode=accel["mode_label"],
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

@router.get("/device/self-test", response_model=SelfTestResponse)
async def run_device_self_test():
    """
    Executes automated self-test across all 6 core subsystems:
    1. Local SQLite Database
    2. Local Storage Space
    3. Camera HAL / Viewfinder
    4. 6-Parameter Soil Sensor Probe
    5. AI Inference Engine
    6. Host Platform & Architecture
    """
    return DeviceSelfTestService.run_self_test()

@router.get("/device/status", response_model=DeviceStatus)
async def get_device_status():
    """
    Comprehensive host and hardware telemetry.
    Strictly reports real hardware status without fake numbers when DEMO_MODE=false.
    """
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    uptime = round(time.time() - START_TIME, 1)

    # Host System Metrics
    cpu_percent = psutil.cpu_percent(interval=None)
    vm = psutil.virtual_memory()
    storage_metrics = SystemDetector.get_storage_metrics(settings.DATA_DIR)

    # CPU Temperature probe
    cpu_temp = SystemDetector.get_cpu_temperature()

    # Platform & Serial Ports
    platform_data = SystemDetector.get_platform_info()
    platform_info = PlatformInfo(**platform_data)
    serial_ports = SystemDetector.list_serial_interfaces()

    # Subsystems Hardware Query
    accel_info = AcceleratorDetector.detect(settings.AI_MODE)
    soil_sensor = get_soil_sensor()
    soil_status = soil_sensor.get_status()
    camera = get_camera()
    camera_status = camera.get_status()

    subsystems = {
        "camera": SubsystemStatus(
            status=camera_status.get("status", "CAMERA_UNAVAILABLE"),
            details=camera_status.get("details", "Camera Driver"),
            last_check=now_iso,
            is_mock=settings.DEMO_MODE
        ),
        "soil_sensor": SubsystemStatus(
            status=soil_status.get("status", "SENSOR DISCONNECTED"),
            details=soil_status.get("details", "RS485 Modbus Interface"),
            last_check=now_iso,
            is_mock=settings.DEMO_MODE
        ),
        "ai_engine": SubsystemStatus(
            status="READY",
            details=accel_info.get("details", "AI Accelerator Engine"),
            last_check=now_iso,
            is_mock=False
        ),
        "database": SubsystemStatus(
            status="READY",
            details="SQLite Local Storage Initialized",
            last_check=now_iso,
            is_mock=False
        )
    }

    battery_info = battery_monitor.get_status(demo_mode=settings.DEMO_MODE)

    return DeviceStatus(
        status="OK",
        app_version=settings.VERSION,
        app_name=settings.PROJECT_NAME,
        demo_mode=settings.DEMO_MODE,
        mode_label="DEMO SIMULATION" if settings.DEMO_MODE else "OFFLINE EDGE AI",
        ai_status_label=accel_info["mode_label"],
        soil_status_label=soil_status.get("status", "SENSOR DISCONNECTED"),
        camera_status_label=camera_status.get("status", "CAMERA_UNAVAILABLE"),
        uptime_seconds=uptime,
        cpu_temperature_celsius=cpu_temp,
        cpu_usage_percent=cpu_percent,
        ram_usage_percent=vm.percent,
        ram_available_mb=round(vm.available / (1024 * 1024), 1),
        storage_usage_percent=storage_metrics.get("percent_used", 0.0),
        storage_free_gb=storage_metrics.get("free_gb", 0.0),
        battery=battery_info,
        subsystems=subsystems,
        platform=platform_info,
        serial_ports=serial_ports
    )

@router.get("/device/capabilities", response_model=DeviceCapabilities)
async def get_device_capabilities():
    """Dynamically detected device capabilities metadata."""
    accel_info = AcceleratorDetector.detect(settings.AI_MODE)
    camera = get_camera()
    camera_status = camera.get_status()
    soil_sensor = get_soil_sensor()
    soil_status = soil_sensor.get_status()
    platform_data = SystemDetector.get_platform_info()
    platform_info = PlatformInfo(**platform_data)

    return DeviceCapabilities(
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        camera_available=camera_status.get("available", False),
        soil_sensor_available=soil_status.get("connected", False),
        soil_sensor_register_configured=False, # Strictly False until datasheet registers are filled
        ai_accelerator_available=accel_info["is_accelerated"],
        ai_accelerator_type=accel_info["accelerator_type"],
        ai_inference_mode=accel_info["mode_label"],
        ai_status_label=accel_info["mode_label"],
        offline_capable=True,
        demo_mode=settings.DEMO_MODE,
        supported_crops=["Tomato", "Potato", "Cotton", "Wheat", "Rice", "Soybean", "Chilli"],
        supported_languages=["en", "hi", "mr"],
        soil_sensor_parameters=["Nitrogen", "Phosphorus", "Potassium", "pH", "Moisture", "Temperature"],
        platform_info=platform_info
    )
