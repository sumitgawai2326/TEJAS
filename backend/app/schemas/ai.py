"""
Pydantic Schemas for AI Engine Status & Confidence-Gated Predictions.
"""
from typing import Optional, List, Dict, Any
import datetime
from pydantic import BaseModel, Field

class AIStatus(BaseModel):
    ready: bool = Field(..., description="True if model is loaded and ready for inference")
    status: str = Field(..., description="READY, AI_NOT_READY, ACCELERATED, CPU_FALLBACK, DEMO_PLACEHOLDER")
    accelerator_type: str = Field(..., description="HAILO-8 or CPU")
    inference_mode: str = Field(..., description="HAILO ACCELERATED or CPU FALLBACK")
    model_name: str
    model_version: str
    is_demo_model: bool = Field(True, description="Marker for prototype demo placeholder model")
    confidence_threshold: float
    supported_classes: List[str]
    details: Optional[str] = None
    last_check: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class PredictionResult(BaseModel):
    prediction: str = Field(..., description="Diagnosis label (or 'Unknown / Low Confidence')")
    confidence: float = Field(..., description="Model confidence score (0.0 to 1.0)")
    model_name: str
    model_version: str
    inference_time_ms: float = Field(..., description="Measured inference time in milliseconds")
    inference_device: str = Field(..., description="HAILO or CPU")
    status: str = Field(..., description="CONFIDENT or LOW_CONFIDENCE")
    is_low_confidence: bool = Field(..., description="True if confidence is below configured threshold")
    crop: str = "General"
    severity: str = "Unknown"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
