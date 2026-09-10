from app.schemas.common import ErrorResponse
from app.schemas.health import DeviceStatus, DeviceCapabilities, SubsystemStatus, HealthResponse
from app.schemas.soil import SoilTelemetry, SensorStatus
from app.schemas.camera import CameraStatus
from app.schemas.ai import AIStatus, PredictionResult
from app.schemas.fields import (
    FieldCreate,
    FieldResponse,
    CropCreate,
    CropResponse,
    ScanCreate,
    ScanResponse,
    SoilReadingCreate,
    SoilReadingResponse,
    FieldHistoryResponse
)
from app.schemas.vision import (
    ImageQualityResult,
    VisionAnalysisResponse,
    VisionStatusResponse
)

__all__ = [
    "ErrorResponse",
    "DeviceStatus",
    "DeviceCapabilities",
    "SubsystemStatus",
    "HealthResponse",
    "SoilTelemetry",
    "SensorStatus",
    "CameraStatus",
    "AIStatus",
    "PredictionResult",
    "FieldCreate",
    "FieldResponse",
    "CropCreate",
    "CropResponse",
    "ScanCreate",
    "ScanResponse",
    "SoilReadingCreate",
    "SoilReadingResponse",
    "FieldHistoryResponse",
    "ImageQualityResult",
    "VisionAnalysisResponse",
    "VisionStatusResponse"
]
