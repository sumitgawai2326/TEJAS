"""
Disease Prediction Schemas for TEJAS.
"""
from typing import List
from pydantic import BaseModel, Field

class ClassPrediction(BaseModel):
    class_name: str = Field(..., description="Predicted plant pathology class name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")

class ImageDimension(BaseModel):
    width: int = Field(..., ge=1, description="Original image width in pixels")
    height: int = Field(..., ge=1, description="Original image height in pixels")

class DiseasePredictResponse(BaseModel):
    success: bool = Field(default=True, description="Inference execution status")
    model: str = Field(default="tejas_tomato_yolo11n", description="Model identifier used")
    prediction: ClassPrediction = Field(..., description="Top-1 predicted pathology")
    top_predictions: List[ClassPrediction] = Field(..., description="Top-3 ranked predictions")
    image: ImageDimension = Field(..., description="Input image dimensions")
