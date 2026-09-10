import os

base_schemas = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app\schemas"

# 1. vision.py
vision_code = """\"\"\"
Pydantic Schemas for Offline Edge AI Vision Pipeline & Image Quality.
\"\"\"
from typing import Optional, List, Dict, Any
import datetime
from pydantic import BaseModel, Field

class ImageQualityResult(BaseModel):
    valid: bool = Field(..., description="True if image passes blur, exposure, and resolution checks")
    score: float = Field(..., ge=0.0, le=1.0, description="Normalized quality score between 0.0 and 1.0")
    issues: List[str] = Field(default_factory=list, description="Quality issues: IMAGE_TOO_BLURRY, IMAGE_TOO_DARK, etc.")
    resolution: str = Field(..., description="Image resolution formatted as WxH")
    blur_score: float = Field(..., description="Laplacian variance sharpness metric")
    brightness_score: float = Field(..., description="Mean pixel luminance metric (0-255)")
    message: str = Field(..., description="Farmer-friendly quality explanation")

class VisionAnalysisResponse(BaseModel):
    status: str = Field(..., description="accepted, low_confidence, invalid_image, ai_unavailable, inference_error")
    prediction: str = Field(..., description="Crop pathology label or 'Unknown / Low Confidence'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    model_name: str
    model_version: str
    inference_time_ms: float
    inference_device: str = Field(..., description="HAILO or CPU")
    is_demo: bool = Field(..., description="True if inference was produced by demo/placeholder model")
    scan_id: Optional[int] = Field(None, description="SQLite Scan record ID if persisted")
    field_id: Optional[int] = Field(None, description="Associated Field ID")
    image_path: Optional[str] = Field(None, description="Local stored capture path")
    image_quality: ImageQualityResult
    crop: str = "General"
    severity: str = "Unknown"
    message: str = Field(..., description="Farmer-facing advisory status message")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class VisionStatusResponse(BaseModel):
    ready: bool
    model_available: bool
    model_name: str
    model_version: str
    accelerator: str
    inference_mode: str
    cpu_fallback_available: bool
    confidence_threshold: float
    demo_mode: bool
    reason_if_unavailable: Optional[str] = None
    supported_classes: List[str] = Field(default_factory=list)
"""

with open(os.path.join(base_schemas, "vision.py"), "w", encoding="utf-8") as f:
    f.write(vision_code)

# 2. Update __init__.py
init_code = """from app.schemas.common import ErrorResponse
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
"""

with open(os.path.join(base_schemas, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(init_code)

print("Vision schemas updated.")
