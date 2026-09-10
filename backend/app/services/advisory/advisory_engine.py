"""
Actionable Agronomic Advisory Engine for KrishiDrishti Edge.
Transforms Risk Assessments and Multi-Modal Evidence into Prioritized Farmer Advisories.
"""
from typing import List, Optional
from app.services.advisory.schemas import AdvisoryResult, FarmerAdvisoryItem
from app.services.advisory.rules import AdvisoryRules
from app.services.fusion.schemas import (
    RiskAssessmentResult,
    EvidenceItem,
    SoilDataQuality,
    VisionSignal
)

class AdvisoryEngine:
    """Orchestrates generation, prioritization, and formatting of farmer advisories."""

    @staticmethod
    def generate(
        field_id: int,
        risk: RiskAssessmentResult,
        evidence: List[EvidenceItem],
        data_quality: SoilDataQuality,
        vision: Optional[VisionSignal] = None,
        is_demo: bool = False
    ) -> AdvisoryResult:
        items = AdvisoryRules.generate_advisories(
            field_id=field_id,
            risk=risk,
            evidence=evidence,
            data_quality=data_quality,
            vision=vision,
            is_demo=is_demo
        )

        # Priority ordering: URGENT > HIGH > MEDIUM > LOW > INFO
        priority_weights = {"URGENT": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2, "INFO": 1}
        items.sort(key=lambda x: priority_weights.get(x.priority, 0), reverse=True)

        primary = items[0] if items else None

        return AdvisoryResult(
            field_id=field_id,
            advisories=items,
            total_advisories=len(items),
            primary_advisory=primary,
            is_demo=is_demo
        )

advisory_engine = AdvisoryEngine()
