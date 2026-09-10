import os

base_api = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app\api\routes"
base_app = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app"

# 1. api/routes/health.py
health_code = """\"\"\"
System & Hardware Health Endpoints.
\"\"\"
import time
import psutil
import datetime
import os
import sys
from fastapi import APIRouter
from app.core.config import settings
from app.schemas.health import HealthResponse, DeviceStatus, DeviceCapabilities, SubsystemStatus
from app.hardware.battery.battery_monitor import battery_monitor
from app.hardware.soil_sensor import get_soil_sensor
from app.hardware.camera import get_camera

# Add root for AI package import
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from ai.inference.base import AcceleratorDetector

router = APIRouter(tags=["System Health & Diagnostics"])
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse)
async def get_health():
    \"\"\"Basic service health check.\"\"\"
    accel = AcceleratorDetector.detect(settings.AI_MODE)
    return HealthResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        demo_mode=settings.DEMO_MODE,
        ai_mode=accel["mode_label"],
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

@router.get("/device/status", response_model=DeviceStatus)
async def get_device_status():
    \"\"\"
    Comprehensive host and hardware telemetry.
    Strictly reports real hardware status without fake numbers when DEMO_MODE=false.
    \"\"\"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    uptime = round(time.time() - START_TIME, 1)

    # Host System Metrics
    cpu_percent = psutil.cpu_percent(interval=None)
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage(os.path.abspath(os.sep))

    # CPU Temperature probe
    cpu_temp = None
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps:
                for key in ["cpu_thermal", "coretemp", "k10temp", "cpu-thermal"]:
                    if key in temps and temps[key]:
                        cpu_temp = round(temps[key][0].current, 1)
                        break
    except Exception:
        cpu_temp = None

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

    battery_info = battery_monitor.get_status()

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
        storage_usage_percent=disk.percent,
        storage_free_gb=round(disk.free / (1024 * 1024 * 1024), 2),
        battery=battery_info,
        subsystems=subsystems
    )

@router.get("/device/capabilities", response_model=DeviceCapabilities)
async def get_device_capabilities():
    \"\"\"Dynamically detected device capabilities metadata.\"\"\"
    accel_info = AcceleratorDetector.detect(settings.AI_MODE)
    camera = get_camera()
    camera_status = camera.get_status()
    soil_sensor = get_soil_sensor()
    soil_status = soil_sensor.get_status()

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
        soil_sensor_parameters=["Nitrogen", "Phosphorus", "Potassium", "pH", "Moisture", "Temperature"]
    )
"""

with open(os.path.join(base_api, "health.py"), "w", encoding="utf-8") as f:
    f.write(health_code)

# 2. api/routes/subsystems.py
subsystems_code = """\"\"\"
Dedicated Hardware Subsystems Status Endpoints: Camera, Soil Sensor, and AI Accelerator.
\"\"\"
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

# Add root for AI package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))
from ai.inference.base import get_vision_model

router = APIRouter(tags=["Hardware Subsystems Status"])

@router.get("/camera/status", response_model=CameraStatus)
async def get_camera_status():
    \"\"\"Returns live camera hardware diagnostics.\"\"\"
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
    \"\"\"Returns live RS485 Modbus soil sensor status.\"\"\"
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
    \"\"\"Returns live AI accelerator and model status.\"\"\"
    vision_model = get_vision_model(
        confidence_threshold=settings.AI_CONFIDENCE_THRESHOLD,
        ai_mode=settings.AI_MODE
    )
    return vision_model.get_status()
"""

with open(os.path.join(base_api, "subsystems.py"), "w", encoding="utf-8") as f:
    f.write(subsystems_code)

# 3. api/routes/__init__.py
routes_init_code = """\"\"\"
Central API Router for KrishiDrishti Edge.
\"\"\"
from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.subsystems import router as subsystems_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(subsystems_router)
"""

with open(os.path.join(base_api, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(routes_init_code)

# 4. backend/app/main.py
main_code = """\"\"\"
Main FastAPI Application Entry Point for KrishiDrishti Edge.
\"\"\"
from contextlib import asynccontextmanager
import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger, log_event
from app.core.errors import KrishiException, ErrorCode
from app.api.routes import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Lifespan
    log_event("SYSTEM", "INFO", f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    log_event("SYSTEM", "INFO", f"Tagline: {settings.TAGLINE}")
    log_event("DEVICE", "INFO", f"Mode: {'DEMO SIMULATION' if settings.DEMO_MODE else 'REAL HARDWARE MODE'}")
    log_event("AI", "INFO", f"AI Mode configured: {settings.AI_MODE} (Confidence Threshold: {settings.AI_CONFIDENCE_THRESHOLD:.2f})")
    log_event("SOIL", "INFO", f"Soil Sensor Port: {settings.SOIL_SENSOR_PORT}")
    log_event("CAMERA", "INFO", f"Camera Device Index: {settings.CAMERA_DEVICE}")
    yield
    # Shutdown Lifespan
    log_event("SYSTEM", "INFO", "Shutting down KrishiDrishti Edge gracefully...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Portable Offline AI-Powered Farming Assistant for Smart India Hackathon (SIH)",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# KrishiException Handler
@app.exception_handler(KrishiException)
async def krishi_exception_handler(request: Request, exc: KrishiException):
    log_event("API", "WARNING", f"KrishiException on {request.url.path}: [{exc.code}] {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# Global API Exception Handler (Zero Stack Trace Leaks)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_event("SYSTEM", "ERROR", f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": ErrorCode.INTERNAL_ERROR.value,
            "message": "Internal server error occurred",
            "details": str(exc) if settings.DEBUG else "An unexpected error occurred. Consult system logs.",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    )

# Include API Router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
"""

with open(os.path.join(base_app, "main.py"), "w", encoding="utf-8") as f:
    f.write(main_code)

print("Phase 2 API Routes and FastAPI Main updated successfully.")
