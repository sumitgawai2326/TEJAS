"""
Pydantic Schemas for Crop + Soil Intelligence Fusion Engine.
Enforces strict nullability, explainable evidence tracking, and truthful data completeness.
"""
from typing import Optional, List, Dict, Any
import datetime
from pydantic import BaseModel, Field

class SoilDataQuality(BaseModel):
    status: str = Field(..., description="COMPLETE, PARTIAL, UNAVAILABLE, STALE, MOCK")
    available_parameters: List[str] = Field(default_factory=list)
    missing_parameters: List[str] = Field(default_factory=list)
    age_seconds: Optional[float] = None
    is_mock: bool = False

class EvidenceItem(BaseModel):
    factor_id: str
    category: str = Field(..., description="VISION, SOIL, HISTORY, CROP, DATA_QUALITY")
    title: str
    description: str
    severity: str = Field("INFO", description="INFO, LOW, MEDIUM, HIGH, CRITICAL, UNKNOWN")
    confidence: float = Field(..., ge=0.0, le=1.0)
    source: str = Field(..., description="CONFIGURED_RULE, AI_OBSERVATION, SOIL_OBSERVATION, HISTORICAL_OBSERVATION, GENERAL_PRECAUTION, DATA_QUALITY_CHECK, MODEL, SOIL, HISTORY, RULE, COMBINED")
    provenance: str = Field("REAL", description="REAL, DEMO, MOCK, RULE, UNKNOWN")
    is_demo: bool = False
    details: Optional[Dict[str, Any]] = None

# RiskFactor is an alias/standard representation for transparent risk drivers
RiskFactor = EvidenceItem

class CropContext(BaseModel):
    crop_name: str = "General"
    variety: Optional[str] = None
    growth_stage: str = "Vegetative"
    sowing_date: Optional[str] = None

class VisionSignal(BaseModel):
    status: str = "unavailable"  # accepted, low_confidence, invalid_image, ai_unavailable, unavailable
    prediction: str = "None"
    confidence: float = 0.0
    model_name: str = "None"
    model_version: str = "None"
    image_quality: Optional[float] = None
    is_demo: bool = False
    scan_id: Optional[int] = None

class SoilSignal(BaseModel):
    # Strictly nullable for Zero Hardware Hallucination
    nitrogen: Optional[float] = None
    phosphorus: Optional[float] = None
    potassium: Optional[float] = None
    ph: Optional[float] = None
    moisture: Optional[float] = None
    temperature: Optional[float] = None
    timestamp: Optional[str] = None
    sensor_status: str = "DISCONNECTED"
    is_mock: bool = False
    availability: str = "UNAVAILABLE"  # COMPLETE, PARTIAL, UNAVAILABLE, MOCK

class HistorySummary(BaseModel):
    scans_count: int = 0
    soil_readings_count: int = 0
    risk_assessments_count: int = 0
    advisories_count: int = 0
    repeated_diagnosis: Optional[str] = None
    soil_moisture_delta: Optional[float] = None
    soil_temp_delta: Optional[float] = None
    has_sufficient_history: bool = False
    notes: List[str] = Field(default_factory=list)

class FusionInput(BaseModel):
    field_id: int
    crop_context: Optional[CropContext] = None
    vision: Optional[VisionSignal] = None
    soil: Optional[SoilSignal] = None
    history: Optional[HistorySummary] = None

class RiskAssessmentResult(BaseModel):
    risk_level: str = Field(..., description="LOW, MODERATE, HIGH, CRITICAL, UNKNOWN")
    score: Optional[float] = Field(None, description="Heuristic score between 0.0 and 1.0, or None if UNKNOWN")
    confidence: float = Field(..., ge=0.0, le=1.0)
    factors: List[EvidenceItem] = Field(default_factory=list)
    explanation: str
    data_completeness: float = Field(..., ge=0.0, le=1.0)
    is_demo: bool = False
    disease_risk: str = "UNKNOWN"
    pest_risk: str = "UNKNOWN"
    soil_stress: str = "UNKNOWN"
    water_stress: str = "UNKNOWN"
    is_prototype_heuristic: bool = True
    vision_provenance: str = "NONE"
    soil_provenance: str = "NONE"
    history_provenance: str = "NONE"

class FusionResult(BaseModel):
    field_id: int
    overall_status: str = Field(..., description="SUCCESS, PARTIAL_DATA, INSUFFICIENT_DATA")
    risk: RiskAssessmentResult
    evidence: List[EvidenceItem] = Field(default_factory=list)
    data_quality: SoilDataQuality
    missing_data: List[str] = Field(default_factory=list)
    is_demo: bool = False
    vision_provenance: str = "NONE"  # REAL_VISION, DEMO_VISION, NONE
    soil_provenance: str = "NONE"    # REAL_SOIL, MOCK_SOIL, NONE
    history_provenance: str = "NONE" # SUFFICIENT_HISTORY, INSUFFICIENT_HISTORY, NONE
    generated_at: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
