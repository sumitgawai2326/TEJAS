"""
Central Crop + Soil Intelligence Fusion Engine for KrishiDrishti Edge.
Coordinates Data Quality -> Agronomic Rules -> Temporal Trends -> Evidence Synthesis -> Risk Assessment.
"""
from typing import List, Optional
from app.services.fusion.schemas import (
    FusionInput,
    FusionResult,
    EvidenceItem
)
from app.services.fusion.evidence import EvidenceSynthesizer
from app.services.fusion.rules import AgronomicRulesEngine
from app.services.fusion.trends import TemporalTrendEngine
from app.services.fusion.risk_engine import RiskEngine
from app.core.config import settings
from app.core.logging import log_event

class FusionEngine:
    def __init__(self):
        self.rules_engine = AgronomicRulesEngine()
        self.evidence_synthesizer = EvidenceSynthesizer()
        self.trend_engine = TemporalTrendEngine()
        self.risk_engine = RiskEngine()

    def fuse(self, fusion_input: FusionInput) -> FusionResult:
        """
        Executes multi-modal intelligence fusion on provided edge telemetry.
        """
        is_demo = (
            (fusion_input.vision and fusion_input.vision.is_demo) or
            (fusion_input.soil and fusion_input.soil.is_mock) or
            settings.DEMO_MODE
        )

        missing_data: List[str] = []
        if not fusion_input.vision or fusion_input.vision.status in ["unavailable", "ai_unavailable"]:
            missing_data.append("CROP_VISION_SCAN")
        if not fusion_input.soil or fusion_input.soil.availability == "UNAVAILABLE":
            missing_data.append("SOIL_TELEMETRY")
        if not fusion_input.history or not fusion_input.history.has_sufficient_history:
            missing_data.append("FIELD_HISTORY")

        # 1. Soil Quality Assessment
        soil_quality = self.evidence_synthesizer.assess_soil_quality(fusion_input.soil)

        # 2. Gather Evidence across Modalities
        evidence: List[EvidenceItem] = []

        # Vision Evidence
        evidence.extend(self.evidence_synthesizer.extract_vision_evidence(fusion_input.vision, is_demo=is_demo))

        # Crop Context Evidence
        evidence.extend(self.evidence_synthesizer.extract_crop_evidence(fusion_input.crop_context, is_demo=is_demo))

        # Agronomic Rule Evaluation
        evidence.extend(self.rules_engine.evaluate(fusion_input.soil, fusion_input.crop_context, is_demo=is_demo))

        # Historical Trend Evidence
        if fusion_input.history:
            evidence.extend(self.trend_engine.extract_trend_evidence(fusion_input.history, is_demo=is_demo))

        # 3. Assess Multimodal Risk
        risk_result = self.risk_engine.assess_risk(
            fusion_input=fusion_input,
            evidence=evidence,
            data_quality=soil_quality,
            is_demo=is_demo
        )

        # 4. Determine Modality Provenance
        if fusion_input.vision and fusion_input.vision.status not in ["unavailable", "ai_unavailable"]:
            vision_provenance = "DEMO_VISION" if fusion_input.vision.is_demo else "REAL_VISION"
        else:
            vision_provenance = "NONE"

        if fusion_input.soil and fusion_input.soil.availability != "UNAVAILABLE":
            soil_provenance = "MOCK_SOIL" if fusion_input.soil.is_mock else "REAL_SOIL"
        else:
            soil_provenance = "NONE"

        if fusion_input.history and fusion_input.history.has_sufficient_history:
            history_provenance = "SUFFICIENT_HISTORY"
        elif fusion_input.history:
            history_provenance = "INSUFFICIENT_HISTORY"
        else:
            history_provenance = "NONE"

        risk_result.vision_provenance = vision_provenance
        risk_result.soil_provenance = soil_provenance
        risk_result.history_provenance = history_provenance

        # 5. Determine Overall Status
        if risk_result.risk_level == "UNKNOWN":
            overall_status = "INSUFFICIENT_DATA"
        elif missing_data:
            overall_status = "PARTIAL_DATA"
        else:
            overall_status = "SUCCESS"

        log_event("AI", "INFO", f"Fusion completed for Field {fusion_input.field_id}: status={overall_status}, risk={risk_result.risk_level}")

        return FusionResult(
            field_id=fusion_input.field_id,
            overall_status=overall_status,
            risk=risk_result,
            evidence=evidence,
            data_quality=soil_quality,
            missing_data=missing_data,
            is_demo=is_demo,
            vision_provenance=vision_provenance,
            soil_provenance=soil_provenance,
            history_provenance=history_provenance
        )

fusion_engine = FusionEngine()
