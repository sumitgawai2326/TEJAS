import os

base_backend = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app"

# 1. core/config.py
config_code = """\"\"\"
Application Configuration Module for KrishiDrishti Edge.
Centralized settings management via Pydantic BaseSettings.
\"\"\"
from typing import List, Optional
from pydantic import Field, AliasChoices
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
    HOST: str = Field(default="0.0.0.0", validation_alias=AliasChoices("HOST", "API_HOST"))
    PORT: int = Field(default=8000, validation_alias=AliasChoices("PORT", "API_PORT"))
    FRONTEND_PORT: int = 5173

    # AI Inference & Gating Settings
    AI_MODE: str = Field(default="auto", validation_alias=AliasChoices("AI_MODE", "AI_ACCELERATOR"))  # 'auto', 'hailo', 'cpu'
    MODEL_PATH: str = "ai/models/crop_disease_v1.onnx"
    AI_CONFIDENCE_THRESHOLD: float = Field(default=0.70, validation_alias=AliasChoices("AI_CONFIDENCE_THRESHOLD", "CONFIDENCE_THRESHOLD"))
    MIN_IMAGE_QUALITY_SCORE: float = 0.60

    # Hardware Camera Settings
    CAMERA_DEVICE: int = Field(default=0, validation_alias=AliasChoices("CAMERA_DEVICE", "CAMERA_INDEX"))
    CAMERA_WIDTH: int = 1920
    CAMERA_HEIGHT: int = 1080
    CAMERA_FPS: int = 30

    # Hardware Serial & RS485 Modbus Settings
    SOIL_SENSOR_PORT: str = "COM3" if os.name == "nt" else "/dev/ttyUSB0"
    SOIL_SENSOR_BAUDRATE: int = 4800
    SOIL_SENSOR_SLAVE_ID: int = 1
    SOIL_SENSOR_TIMEOUT: float = 2.0
    SOIL_SENSOR_CONFIG: str = Field(default="hardware/sensor_protocol/soil_sensor.yaml", validation_alias=AliasChoices("SOIL_SENSOR_CONFIG", "SOIL_SENSOR_CONFIG_FILE"))

    # Logging
    LOG_LEVEL: str = "INFO"

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

with open(os.path.join(base_backend, "core", "config.py"), "w", encoding="utf-8") as f:
    f.write(config_code)

# 2. core/errors.py
errors_code = """\"\"\"
Standardized Error Definitions & Exceptions for KrishiDrishti Edge.
\"\"\"
from enum import Enum
from typing import Optional, Dict, Any
import datetime
from pydantic import BaseModel, Field

class ErrorCode(str, Enum):
    CAMERA_UNAVAILABLE = "CAMERA_UNAVAILABLE"
    SENSOR_DISCONNECTED = "SENSOR_DISCONNECTED"
    SENSOR_UNCONFIGURED = "SENSOR_UNCONFIGURED"
    AI_NOT_READY = "AI_NOT_READY"
    AI_MODEL_NOT_FOUND = "AI_MODEL_NOT_FOUND"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    INVALID_IMAGE = "INVALID_IMAGE"
    HARDWARE_TIMEOUT = "HARDWARE_TIMEOUT"
    DATABASE_ERROR = "DATABASE_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"

class ErrorResponse(BaseModel):
    code: ErrorCode = Field(..., description="Standardized error code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[str] = Field(None, description="Detailed diagnostic or troubleshooting advice")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class KrishiException(Exception):
    def __init__(self, code: ErrorCode, message: str, details: Optional[str] = None, status_code: int = 400):
        self.code = code
        self.message = message
        self.details = details
        self.status_code = status_code
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "code": self.code.value,
            "message": self.message,
            "details": self.details,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

class CameraUnavailableException(KrishiException):
    def __init__(self, message: str = "Camera hardware unavailable or disconnected", details: Optional[str] = None):
        super().__init__(ErrorCode.CAMERA_UNAVAILABLE, message, details, status_code=503)

class SensorDisconnectedException(KrishiException):
    def __init__(self, message: str = "Soil sensor probe disconnected or unresponsive", details: Optional[str] = None):
        super().__init__(ErrorCode.SENSOR_DISCONNECTED, message, details, status_code=503)

class SensorUnconfiguredException(KrishiException):
    def __init__(self, message: str = "Soil sensor register map is unconfigured in soil_sensor.yaml", details: Optional[str] = None):
        super().__init__(ErrorCode.SENSOR_UNCONFIGURED, message, details, status_code=422)

class LowConfidenceException(KrishiException):
    def __init__(self, message: str = "AI inference confidence below threshold", details: Optional[str] = None):
        super().__init__(ErrorCode.LOW_CONFIDENCE, message, details, status_code=422)
"""

with open(os.path.join(base_backend, "core", "errors.py"), "w", encoding="utf-8") as f:
    f.write(errors_code)

# 3. core/logging.py
logging_code = """\"\"\"
Structured Hardware-Domain Logging Module for KrishiDrishti Edge.
Includes credential sanitization and hardware subsystem domain tags.
\"\"\"
import logging
import sys
import re
from datetime import datetime

# Regex pattern to redact sensitive keys from log output
SENSITIVE_PATTERN = re.compile(r"(password|secret|token|api[_-]?key|auth)=([^\s,]+)", re.IGNORECASE)

class DomainFormatter(logging.Formatter):
    \"\"\"Custom formatter providing hardware/subsystem domain tags.\"\"\"
    def format(self, record):
        domain = getattr(record, "domain", "SYSTEM")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        levelname = record.levelname
        msg = record.getMessage()
        # Redact sensitive parameters
        sanitized_msg = SENSITIVE_PATTERN.sub(r"\\1=********", msg)
        return f"[{timestamp}] [{domain.upper():<8}] [{levelname:<5}] {sanitized_msg}"

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
    \"\"\"
    Convenience helper to emit domain-tagged logs.
    Subsystems: [AI], [CAMERA], [SOIL], [API], [DATABASE], [DEVICE], [SYSTEM]
    \"\"\"
    extra = {"domain": domain, **kwargs}
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, extra=extra)
"""

with open(os.path.join(base_backend, "core", "logging.py"), "w", encoding="utf-8") as f:
    f.write(logging_code)

print("Core modules (config, errors, logging) updated successfully.")
