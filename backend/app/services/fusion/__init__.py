"""
Fusion Engine Module exports.
"""
from app.services.fusion.fusion_engine import FusionEngine, fusion_engine
from app.services.fusion.schemas import (
    FusionInput,
    FusionResult,
    RiskFactor,
    EvidenceItem,
    SoilDataQuality,
    CropContext,
    VisionSignal,
    SoilSignal,
    HistorySummary,
    RiskAssessmentResult
)

__all__ = [
    "FusionEngine",
    "fusion_engine",
    "FusionInput",
    "FusionResult",
    "RiskFactor",
    "EvidenceItem",
    "SoilDataQuality",
    "CropContext",
    "VisionSignal",
    "SoilSignal",
    "HistorySummary",
    "RiskAssessmentResult"
]
