"""
Pydantic Schemas for Actionable Agronomic Advisory Engine.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class FarmerAdvisoryItem(BaseModel):
    advisory_id: str
    priority: str = Field(..., description="INFO, LOW, MEDIUM, HIGH, URGENT")
    title: str
    message: str
    recommended_action: str
    reason: str
    source: str = Field(..., description="MODEL, SOIL, HISTORY, RULE, COMBINED, CONFIGURED_RULE, AI_OBSERVATION, SOIL_OBSERVATION, HISTORICAL_OBSERVATION, GENERAL_PRECAUTION, DATA_QUALITY_CHECK")
    provenance: str = Field("REAL", description="REAL, DEMO, MOCK, RULE, UNKNOWN")
    confidence: float = Field(..., ge=0.0, le=1.0)
    localization_key: str = Field("ADVISORY_GENERAL", description="Standard localization tag for multilingual UI")
    is_demo: bool = False
    category: str = "General"

class AdvisoryResult(BaseModel):
    field_id: int
    advisories: List[FarmerAdvisoryItem] = Field(default_factory=list)
    total_advisories: int = 0
    primary_advisory: Optional[FarmerAdvisoryItem] = None
    is_demo: bool = False
