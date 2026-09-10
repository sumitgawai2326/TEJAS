"""
Pydantic Request & Response Schemas for Database Entities & Field History.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

# Field Schemas
class FieldCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Field or plot identifier name")
    farm_id: Optional[int] = Field(None, description="Farm ID. Defaults to first active farm if omitted")
    area: Optional[float] = Field(None, ge=0.0, description="Field surface area")
    area_unit: str = Field("Acre", description="Acre, Hectare, Guntha, or Bigha")
    soil_type: Optional[str] = Field(None, description="Black Cotton, Loamy, Red, Clay, Sandy")

class FieldResponse(BaseModel):
    id: int
    farm_id: int
    name: str
    area: Optional[float]
    area_unit: str
    soil_type: Optional[str]
    created_at: str
    updated_at: str

    model_config = {"from_attributes": True}

# Crop Schemas
class CropCreate(BaseModel):
    crop_name: str = Field(..., description="Crop type: Tomato, Potato, Cotton, Wheat, Rice, etc.")
    variety: Optional[str] = None
    sowing_date: Optional[str] = None
    growth_stage: str = Field("Vegetative", description="Seedling, Vegetative, Flowering, Fruiting, Harvesting")

class CropResponse(BaseModel):
    id: int
    field_id: int
    crop_name: str
    variety: Optional[str]
    sowing_date: Optional[str]
    growth_stage: str
    created_at: str

    model_config = {"from_attributes": True}

# Scan Schemas
class ScanCreate(BaseModel):
    prediction: str = Field(..., description="Pathology prediction label")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    model_name: str = Field("KrishiDrishti-DemoVision-V1")
    model_version: str = Field("0.1.0-demo-placeholder")
    image_path: Optional[str] = None
    image_quality: Optional[float] = None
    inference_device: str = "CPU"
    status: str = "CONFIDENT"

class ScanResponse(BaseModel):
    id: int
    field_id: int
    timestamp: str
    image_path: Optional[str]
    image_quality: Optional[float]
    prediction: str
    confidence: float
    model_name: str
    model_version: str
    inference_device: str
    status: str

    model_config = {"from_attributes": True}

# Soil Reading Schemas
class SoilReadingCreate(BaseModel):
    # Nullable values (Zero Hallucination)
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    moisture: Optional[float] = None
    temperature: Optional[float] = None
    sensor_status: Optional[str] = None
    is_mock: Optional[bool] = None

class SoilReadingResponse(BaseModel):
    id: int
    field_id: int
    timestamp: str
    nitrogen: Optional[float]
    phosphorus: Optional[float]
    potassium: Optional[float]
    ph: Optional[float]
    moisture: Optional[float]
    temperature: Optional[float]
    sensor_status: str
    is_mock: bool
    raw_payload_reference: Optional[str]

    model_config = {"from_attributes": True}

# Field History Timeline Schema
class FieldHistoryResponse(BaseModel):
    field_id: int
    field_name: str
    area: Optional[float]
    area_unit: str
    soil_type: Optional[str]
    total_timeline_entries: int
    timeline: List[Dict[str, Any]]
    scans_count: int
    soil_readings_count: int
    risk_assessments_count: int
    advisories_count: int

# Risk Assessment Response Schema
class RiskAssessmentResponse(BaseModel):
    id: int
    field_id: int
    scan_id: Optional[int] = None
    soil_reading_id: Optional[int] = None
    timestamp: str
    field_health_score: Optional[float] = None
    disease_risk: Optional[str] = None
    pest_risk: Optional[str] = None
    soil_stress: Optional[str] = None
    water_stress: Optional[str] = None
    status: str = "CALCULATED"

    model_config = {"from_attributes": True}

# Advisory Response Schema
class AdvisoryResponse(BaseModel):
    id: int
    field_id: int
    risk_assessment_id: Optional[int] = None
    timestamp: str
    language: str = "en"
    title: str
    message: str
    severity: str = "Info"
    category: str = "General"

    model_config = {"from_attributes": True}

# Combined Field Fusion Analysis Response Schema
class FieldAnalysisResponse(BaseModel):
    field: FieldResponse
    vision: Optional[Dict[str, Any]] = None
    soil: Optional[Dict[str, Any]] = None
    history: Optional[Dict[str, Any]] = None
    risk: Dict[str, Any]
    evidence: List[Dict[str, Any]] = []
    advisories: List[Dict[str, Any]] = []
    data_quality: Dict[str, Any]
    is_demo: bool = False
    generated_at: str


