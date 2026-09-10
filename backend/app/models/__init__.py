"""Models package alias pointing to app.db.models."""
from app.db.models import (
    Base,
    Farm,
    Field,
    Crop,
    Scan,
    SoilReading,
    RiskAssessment,
    Advisory,
    DeviceEvent
)

__all__ = [
    "Base",
    "Farm",
    "Field",
    "Crop",
    "Scan",
    "SoilReading",
    "RiskAssessment",
    "Advisory",
    "DeviceEvent"
]
