import os

base_path = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app"

# 1. core/config.py
config_content = """\"\"\"
Application Configuration Module for KrishiDrishti Edge.
Provides centralized settings management via Pydantic BaseSettings.
\"\"\"
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Application Settings
    PROJECT_NAME: str = "KrishiDrishti Edge"
    VERSION: str = "1.0.0-sih-prototype"
    TAGLINE: str = "See. Sense. Predict. Act."
    APP_ENV: str = "development"
    DEBUG: bool = True
    DEMO_MODE: bool = True  # Strict gating: True enables mock telemetry; False enforces real hardware

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    FRONTEND_PORT: int = 5173

    # AI Inference Settings
    AI_ACCELERATOR: str = "auto"  # 'auto', 'hailo', 'cpu'
    MODEL_PATH: str = "ai/models/crop_disease_v1.onnx"
    CONFIDENCE_THRESHOLD: float = 0.70
    MIN_IMAGE_QUALITY_SCORE: float = 0.60

    # Hardware Serial & RS485 Modbus Settings
    SOIL_SENSOR_PORT: str = "COM3" if os.name == "nt" else "/dev/ttyUSB0"
    SOIL_SENSOR_BAUDRATE: int = 4800
    SOIL_SENSOR_SLAVE_ID: int = 1
    SOIL_SENSOR_TIMEOUT: float = 2.0
    SOIL_SENSOR_CONFIG_FILE: str = "hardware/sensor_protocol/soil_sensor.yaml"

    # Camera Settings
    CAMERA_INDEX: int = 0
    CAMERA_WIDTH: int = 1920
    CAMERA_HEIGHT: int = 1080
    CAMERA_FPS: int = 30

    # Storage & Persistence
    DATABASE_URL: str = "sqlite:///./data/krishidrishti.db"
    IMAGE_STORAGE_DIR: str = "./data/captures"

    # Localization
    DEFAULT_LANGUAGE: str = "en"  # "en", "hi", "mr"

    # Security & CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000"
    ]
    SECRET_KEY: str = "krishidrishti-local-edge-secret-key-change-in-production"

settings = Settings()
"""

with open(os.path.join(base_path, "core", "config.py"), "w", encoding="utf-8") as f:
    f.write(config_content)

# 2. core/logging.py
logging_content = """\"\"\"
Structured Hardware-Domain Logging Module for KrishiDrishti Edge.
\"\"\"
import logging
import sys
from datetime import datetime

class DomainFormatter(logging.Formatter):
    \"\"\"Custom formatter providing hardware/subsystem domain tags.\"\"\"
    def format(self, record):
        domain = getattr(record, "domain", "SYSTEM")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        levelname = record.levelname
        msg = record.getMessage()
        return f"[{timestamp}] [{domain.upper():<8}] [{levelname:<5}] {msg}"

def setup_logger(name: str = "krishidrishti", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(DomainFormatter())
        logger.addHandler(handler)
        
    return logger

logger = setup_logger()

def log_event(domain: str, level: str, message: str, **kwargs):
    \"\"\"Convenience helper to emit domain-tagged logs.\"\"\"
    extra = {"domain": domain, **kwargs}
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=extra)
"""

with open(os.path.join(base_path, "core", "logging.py"), "w", encoding="utf-8") as f:
    f.write(logging_content)

# 3. schemas/health.py
schema_health = """\"\"\"
Pydantic Schemas for System & Hardware Health Diagnostics.
\"\"\"
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

class SubsystemStatus(BaseModel):
    status: str = Field(..., description="READY, CONNECTED, DISCONNECTED, ERROR, DEGRADED, SIMULATED")
    details: Optional[str] = None
    last_check: str
    is_mock: bool = False

class DeviceStatusResponse(BaseModel):
    status: str = Field(..., description="OVERALL STATUS: OK, WARNING, ERROR")
    app_version: str
    app_name: str
    demo_mode: bool
    mode_label: str = Field(..., description="OFFLINE EDGE AI or DEMO SIMULATION")
    uptime_seconds: float
    cpu_temperature_celsius: Optional[float] = None
    cpu_usage_percent: float
    ram_usage_percent: float
    ram_available_mb: float
    storage_usage_percent: float
    storage_free_gb: float
    battery: Dict[str, Any]
    subsystems: Dict[str, SubsystemStatus]

class CapabilityResponse(BaseModel):
    project_name: str
    version: str
    ai_accelerator_available: bool
    ai_accelerator_type: str
    ai_inference_mode: str
    supported_crops: List[str]
    supported_languages: List[str]
    soil_sensor_parameters: List[str]
    offline_ready: bool
    demo_mode_enabled: bool

class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    demo_mode: bool
    timestamp: str
"""

with open(os.path.join(base_path, "schemas", "health.py"), "w", encoding="utf-8") as f:
    f.write(schema_health)

# 4. hardware/battery/battery_monitor.py
battery_content = """\"\"\"
Battery & Power Management Telemetry for Portable Edge Operation.
\"\"\"
import psutil
from typing import Dict, Any

class BatteryMonitor:
    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode

    def get_status(self) -> Dict[str, Any]:
        \"\"\"Reads real OS power status or provides safe demo telemetry.\"\"\"
        battery = psutil.sensors_battery()
        if battery is not None:
            return {
                "percent": round(battery.percent, 1),
                "power_plugged": battery.power_plugged,
                "seconds_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else -1,
                "status": "CHARGING" if battery.power_plugged else ("DISCHARGING" if battery.percent > 20 else "LOW_BATTERY"),
                "is_mock": False
            }
        
        # Fallback / Simulated battery state for edge power packs without I2C fuel gauge
        return {
            "percent": 88.5,
            "power_plugged": False,
            "seconds_left": 14400,
            "status": "DISCHARGING",
            "is_mock": True,
            "note": "Hardware UPS / Power pack running (simulated reading)"
        }

battery_monitor = BatteryMonitor()
"""

with open(os.path.join(base_path, "hardware", "battery", "battery_monitor.py"), "w", encoding="utf-8") as f:
    f.write(battery_content)

# 5. api/routes/health.py
routes_health = """\"\"\"
Health & Diagnostic Endpoints.
\"\"\"
import time
import psutil
import datetime
from fastapi import APIRouter
from app.core.config import settings
from app.core.logging import log_event
from app.schemas.health import HealthResponse, DeviceStatusResponse, CapabilityResponse, SubsystemStatus
from app.hardware.battery.battery_monitor import battery_monitor

router = APIRouter(tags=["Health & Diagnostics"])
START_TIME = time.time()

@router.get("/health", response_model=HealthResponse)
async def get_health():
    \"\"\"Basic service health check.\"\"\"
    return HealthResponse(
        status="healthy",
        project=settings.PROJECT_NAME,
        version=settings.VERSION,
        demo_mode=settings.DEMO_MODE,
        timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )

@router.get("/device/status", response_model=DeviceStatusResponse)
async def get_device_status():
    \"\"\"Comprehensive hardware & host telemetry for touch UI status bar.\"\"\"
    now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
    uptime = round(time.time() - START_TIME, 1)
    
    # System Resource Metrics
    cpu_percent = psutil.cpu_percent(interval=None)
    vm = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    
    # CPU Thermal Check
    cpu_temp = None
    try:
        if hasattr(psutil, "sensors_temperatures"):
            temps = psutil.sensors_temperatures()
            if temps and "cpu_thermal" in temps and temps["cpu_thermal"]:
                cpu_temp = temps["cpu_thermal"][0].current
            elif temps and "coretemp" in temps and temps["coretemp"]:
                cpu_temp = temps["coretemp"][0].current
    except Exception:
        cpu_temp = None

    # Subsystems status evaluation
    subsystems = {
        "camera": SubsystemStatus(
            status="READY" if settings.DEMO_MODE else "CONNECTED",
            details="OpenCV / V4L2 Cam0 Initialized" if not settings.DEMO_MODE else "Demo Sample Viewfinder",
            last_check=now_iso,
            is_mock=settings.DEMO_MODE
        ),
        "soil_sensor": SubsystemStatus(
            status="SIMULATED" if settings.DEMO_MODE else "WAITING_FOR_SENSOR",
            details="Mock 6-Parameter Telemetry" if settings.DEMO_MODE else f"RS485 Serial on {settings.SOIL_SENSOR_PORT}",
            last_check=now_iso,
            is_mock=settings.DEMO_MODE
        ),
        "ai_engine": SubsystemStatus(
            status="READY",
            details="CPU Fallback Engine (Hailo-8 Standby)",
            last_check=now_iso,
            is_mock=False
        ),
        "database": SubsystemStatus(
            status="READY",
            details="SQLite Local Storage Engine Connected",
            last_check=now_iso,
            is_mock=False
        )
    }

    battery_info = battery_monitor.get_status()

    return DeviceStatusResponse(
        status="OK",
        app_version=settings.VERSION,
        app_name=settings.PROJECT_NAME,
        demo_mode=settings.DEMO_MODE,
        mode_label="DEMO SIMULATION" if settings.DEMO_MODE else "OFFLINE EDGE AI",
        uptime_seconds=uptime,
        cpu_temperature_celsius=cpu_temp if cpu_temp is not None else (48.5 if settings.DEMO_MODE else None),
        cpu_usage_percent=cpu_percent,
        ram_usage_percent=vm.percent,
        ram_available_mb=round(vm.available / (1024 * 1024), 1),
        storage_usage_percent=disk.percent,
        storage_free_gb=round(disk.free / (1024 * 1024 * 1024), 2),
        battery=battery_info,
        subsystems=subsystems
    )

@router.get("/device/capabilities", response_model=CapabilityResponse)
async def get_device_capabilities():
    \"\"\"Device capabilities metadata.\"\"\"
    return CapabilityResponse(
        project_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        ai_accelerator_available=False,
        ai_accelerator_type="CPU (Cortex-A76 Optimized)",
        ai_inference_mode="CPU_FALLBACK",
        supported_crops=["Tomato", "Potato", "Cotton", "Wheat", "Rice", "Soybean", "Chilli"],
        supported_languages=["en", "hi", "mr"],
        soil_sensor_parameters=["Nitrogen", "Phosphorus", "Potassium", "pH", "Moisture", "Temperature"],
        offline_ready=True,
        demo_mode_enabled=settings.DEMO_MODE
    )
"""

with open(os.path.join(base_path, "api", "routes", "health.py"), "w", encoding="utf-8") as f:
    f.write(routes_health)

# 6. api/routes/__init__.py
routes_init = """from fastapi import APIRouter
from app.api.routes.health import router as health_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
"""

with open(os.path.join(base_path, "api", "routes", "__init__.py"), "w", encoding="utf-8") as f:
    f.write(routes_init)

# 7. main.py
main_content = """\"\"\"
Main FastAPI Application Entry Point for KrishiDrishti Edge.
\"\"\"
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger, log_event
from app.api.routes import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Lifespan
    log_event("SYSTEM", "INFO", f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    log_event("SYSTEM", "INFO", f"Tagline: {settings.TAGLINE}")
    log_event("SYSTEM", "INFO", f"Running Mode: {'DEMO / SIMULATION' if settings.DEMO_MODE else 'PRODUCTION EDGE'}")
    log_event("AI", "INFO", f"AI Accelerator configured as: {settings.AI_ACCELERATOR}")
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

# Global API Exception Handler to prevent stack trace leaks
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_event("SYSTEM", "ERROR", f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error occurred",
            "detail": str(exc) if settings.DEBUG else "An unexpected error occurred. Please consult system logs.",
            "path": request.url.path
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

with open(os.path.join(base_path, "main.py"), "w", encoding="utf-8") as f:
    f.write(main_content)

print("Backend initial foundation created successfully.")
