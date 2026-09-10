"""
Pydantic Schemas for Offline Edge AI Vision Pipeline, Model Registry, and Evaluation.
"""
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
    confidence_tier: str = Field(default="MEDIUM", description="HIGH, MEDIUM, or LOW confidence tier")
    model_name: str
    model_version: str
    model_hash: Optional[str] = None
    inference_time_ms: float
    inference_device: str = Field(..., description="HAILO or CPU")
    is_demo: bool = Field(..., description="True if inference was produced by demo/placeholder model")
    is_validated: bool = Field(default=False, description="True only if model has undergone formal evaluation")
    scan_id: Optional[int] = Field(None, description="SQLite Scan record ID if persisted")
    field_id: Optional[int] = Field(None, description="Associated Field ID")
    image_path: Optional[str] = Field(None, description="Local stored capture path")
    image_quality: ImageQualityResult
    crop: str = "General"
    severity: str = "Unknown"
    message: str = Field(..., description="Farmer-facing advisory status message")
    farmer_guidance: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class ModelMetadataSchema(BaseModel):
    model_id: str
    model_name: str
    model_version: str
    model_hash: Optional[str] = None
    model_path: Optional[str] = None
    status: str
    task_type: str = "crop_pathology_classification"
    framework: str
    format: str
    target_accelerator: str
    input_shape: List[int]
    classes: List[str] = Field(default_factory=list)
    training_dataset: Optional[str] = None
    validation_status: str = "NOT YET VALIDATED"
    is_demo_model: bool = False
    details: Optional[str] = None

class ModelRegistryResponse(BaseModel):
    total_models: int
    active_model_id: str
    active_model: Optional[ModelMetadataSchema] = None
    models: List[ModelMetadataSchema]
    demo_mode: bool
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class VisionStatusResponse(BaseModel):
    ready: bool
    model_available: bool
    model_name: str
    model_version: str
    model_hash: Optional[str] = None
    model_status: str = Field(default="MODEL_READY", description="MODEL_READY, AI_NOT_READY, DEMO_MODEL, MODEL_MISSING")
    accelerator: str
    inference_mode: str
    cpu_fallback_available: bool
    confidence_threshold: float
    high_confidence_threshold: float = 0.85
    demo_mode: bool
    validation_status: str = "NOT YET VALIDATED"
    reason_if_unavailable: Optional[str] = None
    supported_classes: List[str] = Field(default_factory=list)
    profiling_summary: Optional[Dict[str, Any]] = None
