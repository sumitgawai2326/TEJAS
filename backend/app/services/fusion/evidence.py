"""
Evidence Synthesizer & Soil Data Quality Assessor for KrishiDrishti Edge.
Transforms raw sensor readings, AI vision signals, and metadata into explainable evidence items.
"""
from typing import List, Optional, Tuple
from app.services.fusion.schemas import (
    SoilSignal,
    VisionSignal,
    CropContext,
    HistorySummary,
    SoilDataQuality,
    EvidenceItem
)

class EvidenceSynthesizer:
    """Synthesizes structured, transparent evidence items across all edge sub-modalities."""

    @staticmethod
    def assess_soil_quality(soil: Optional[SoilSignal]) -> SoilDataQuality:
        if not soil:
            return SoilDataQuality(
                status="UNAVAILABLE",
                available_parameters=[],
                missing_parameters=["nitrogen", "phosphorus", "potassium", "ph", "moisture", "temperature"],
                is_mock=False
            )

        all_params = ["nitrogen", "phosphorus", "potassium", "ph", "moisture", "temperature"]
        available: List[str] = []
        missing: List[str] = []

        for p in all_params:
            if getattr(soil, p) is not None:
                available.append(p)
            else:
                missing.append(p)

        if len(available) == 6:
            status = "MOCK" if soil.is_mock else "COMPLETE"
        elif len(available) > 0:
            status = "PARTIAL"
        else:
            status = "UNAVAILABLE"

        return SoilDataQuality(
            status=status,
            available_parameters=available,
            missing_parameters=missing,
            is_mock=soil.is_mock
        )

    @staticmethod
    def extract_vision_evidence(vision: Optional[VisionSignal], is_demo: bool = False) -> List[EvidenceItem]:
        evidence: List[EvidenceItem] = []
        if not vision or vision.status == "unavailable":
            evidence.append(EvidenceItem(
                factor_id="VISION_DATA_UNAVAILABLE",
                category="DATA_QUALITY",
                title="No Crop Scan Available",
                description="Crop leaf image has not been captured or provided for this session.",
                severity="INFO",
                confidence=1.0,
                source="DATA_QUALITY_CHECK",
                is_demo=is_demo
            ))
            return evidence

        if vision.status == "accepted":
            is_healthy = "healthy" in vision.prediction.lower()
            evidence.append(EvidenceItem(
                factor_id="VISION_PATHOLOGY_SIGNAL",
                category="VISION",
                title=f"AI Vision: {vision.prediction}",
                description=f"Model detected '{vision.prediction}' with {int(vision.confidence * 100)}% confidence.",
                severity="INFO" if is_healthy else ("HIGH" if "blight" in vision.prediction.lower() or "rust" in vision.prediction.lower() else "MEDIUM"),
                confidence=vision.confidence,
                source="AI_OBSERVATION",
                is_demo=vision.is_demo or is_demo,
                details={
                    "model_name": vision.model_name,
                    "model_version": vision.model_version,
                    "scan_id": vision.scan_id
                }
            ))
        elif vision.status == "low_confidence":
            evidence.append(EvidenceItem(
                factor_id="VISION_CONFIDENCE_GATED",
                category="DATA_QUALITY",
                title="Low Confidence Vision Inference",
                description="Crop image analysis produced low confidence (< threshold) — diagnosis is gated to prevent false alarms.",
                severity="INFO",
                confidence=vision.confidence,
                source="DATA_QUALITY_CHECK",
                is_demo=vision.is_demo or is_demo
            ))
        elif vision.status == "invalid_image":
            evidence.append(EvidenceItem(
                factor_id="VISION_IMAGE_INVALID",
                category="DATA_QUALITY",
                title="Image Quality Below Diagnostic Threshold",
                description="Image was rejected due to blur, extreme lighting, or low resolution before running inference.",
                severity="INFO",
                confidence=1.0,
                source="DATA_QUALITY_CHECK",
                is_demo=vision.is_demo or is_demo
            ))
        elif vision.status == "ai_unavailable":
            evidence.append(EvidenceItem(
                factor_id="VISION_AI_UNAVAILABLE",
                category="DATA_QUALITY",
                title="AI Vision Engine Not Ready",
                description="AI model weights are not loaded or accelerator is unavailable on edge host.",
                severity="INFO",
                confidence=1.0,
                source="DATA_QUALITY_CHECK",
                is_demo=is_demo
            ))

        return evidence

    @staticmethod
    def extract_crop_evidence(crop_context: Optional[CropContext], is_demo: bool = False) -> List[EvidenceItem]:
        evidence: List[EvidenceItem] = []
        if crop_context and crop_context.crop_name != "General":
            evidence.append(EvidenceItem(
                factor_id="CROP_CONTEXT_REGISTERED",
                category="CROP",
                title=f"Active Crop: {crop_context.crop_name}",
                description=f"Field registered with {crop_context.crop_name} (Stage: {crop_context.growth_stage}).",
                severity="INFO",
                confidence=1.0,
                source="CONFIGURED_RULE",
                is_demo=is_demo
            ))
        return evidence
