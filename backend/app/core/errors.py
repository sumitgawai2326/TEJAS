"""
Standardized Error Definitions & Exceptions for KrishiDrishti Edge.
"""
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
