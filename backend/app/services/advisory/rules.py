"""
Actionable Farmer Advisory Rules Engine.
Generates safe, non-toxic, explainable guidance without fabricating chemical treatments or arbitrary doses.
"""
from typing import List, Optional
from app.services.advisory.schemas import FarmerAdvisoryItem
from app.services.fusion.schemas import (
    RiskAssessmentResult,
    EvidenceItem,
    SoilDataQuality,
    VisionSignal
)

class AdvisoryRules:
    """Generates farmer-friendly, actionable recommendations mapped to localization keys."""

    @staticmethod
    def generate_advisories(
        field_id: int,
        risk: RiskAssessmentResult,
        evidence: List[EvidenceItem],
        data_quality: SoilDataQuality,
        vision: Optional[VisionSignal],
        is_demo: bool = False
    ) -> List[FarmerAdvisoryItem]:
        advisories: List[FarmerAdvisoryItem] = []

        # 1. Insufficient Data / Hardware Disconnect Advisories
        if risk.risk_level == "UNKNOWN":
            advisories.append(FarmerAdvisoryItem(
                advisory_id="ADV_INSUFFICIENT_DATA",
                priority="INFO",
                title="Baseline Observation Required",
                message="Current observations are insufficient to generate a confident risk assessment.",
                recommended_action="Take a focused crop leaf photograph and connect the RS485 soil probe to establish baseline field intelligence.",
                reason="Multi-modal data completeness is below diagnostic threshold.",
                source="DATA_QUALITY_CHECK",
                confidence=1.0,
                localization_key="RISK_INSUFFICIENT_DATA",
                is_demo=is_demo,
                category="Data Quality"
            ))
            return advisories

        # 2. Vision Pathology Advisories
        if vision and vision.status == "accepted":
            pred_low = vision.prediction.lower()
            if "late blight" in pred_low or "blast" in pred_low:
                advisories.append(FarmerAdvisoryItem(
                    advisory_id="ADV_PATHOLOGY_CRITICAL",
                    priority="URGENT",
                    title=f"Pathology Alert: {vision.prediction}",
                    message=f"High-severity crop disease '{vision.prediction}' identified on leaf sample.",
                    recommended_action="Isolate affected foliage, inspect surrounding plants for water-soaked lesions, avoid overhead irrigation, and consult local Krishi Vigyan Kendra (KVK) or extension officer.",
                    reason=f"AI vision detected {vision.prediction} with {int(vision.confidence*100)}% confidence.",
                    source="AI_OBSERVATION",
                    confidence=vision.confidence,
                    localization_key="ADVISORY_PATHOLOGY_CRITICAL",
                    is_demo=is_demo,
                    category="Plant Protection"
                ))
            elif "early blight" in pred_low or "rust" in pred_low or "blight" in pred_low:
                advisories.append(FarmerAdvisoryItem(
                    advisory_id="ADV_PATHOLOGY_HIGH",
                    priority="HIGH",
                    title=f"Disease Management: {vision.prediction}",
                    message=f"Leaf symptoms indicate presence of {vision.prediction}.",
                    recommended_action="Prune lower infected leaves showing concentric rings, improve row spacing for better aeration, and monitor daily progression.",
                    reason=f"AI vision identified symptoms with {int(vision.confidence*100)}% confidence.",
                    source="AI_OBSERVATION",
                    confidence=vision.confidence,
                    localization_key="ADVISORY_PATHOLOGY_HIGH",
                    is_demo=is_demo,
                    category="Plant Protection"
                ))
            elif "healthy" in pred_low:
                advisories.append(FarmerAdvisoryItem(
                    advisory_id="ADV_HEALTHY_CANOPY",
                    priority="LOW",
                    title="Crop Canopy Healthy",
                    message="Leaf tissue shows normal coloration without visible fungal or bacterial lesions.",
                    recommended_action="Maintain routine field monitoring and standard weeding schedule.",
                    reason="AI vision confirmed healthy leaf tissue.",
                    source="AI_OBSERVATION",
                    confidence=vision.confidence,
                    localization_key="ADVISORY_HEALTHY_MAINTENANCE",
                    is_demo=is_demo,
                    category="General Maintenance"
                ))
        elif vision and vision.status == "low_confidence":
            advisories.append(FarmerAdvisoryItem(
                advisory_id="ADV_IMAGE_UNCERTAIN",
                priority="MEDIUM",
                title="Unclear Leaf Image",
                message="AI vision analysis confidence is below threshold for confident diagnosis.",
                recommended_action="Hold the camera 15-20 cm away from the leaf in diffuse daylight and capture a fresh image.",
                reason="Prediction confidence was gated to prevent false diagnoses.",
                source="DATA_QUALITY_CHECK",
                confidence=vision.confidence,
                localization_key="ADVISORY_IMAGE_LOW_QUALITY",
                is_demo=is_demo,
                category="Diagnostics"
            ))

        # 3. Soil Telemetry Quality Advisories
        if data_quality.status == "UNAVAILABLE":
            advisories.append(FarmerAdvisoryItem(
                advisory_id="ADV_SOIL_UNAVAILABLE",
                priority="MEDIUM",
                title="Soil Probe Disconnected",
                message="No live soil parameters received from RS485 Modbus link.",
                recommended_action="Ensure the USB-RS485 adapter is inserted and probe metal prongs are firmly embedded in moist soil.",
                reason="Zero soil parameters available in hardware read.",
                source="DATA_QUALITY_CHECK",
                confidence=1.0,
                localization_key="ADVISORY_SOIL_UNAVAILABLE",
                is_demo=is_demo,
                category="Sensor Diagnostics"
            ))
        elif data_quality.status == "PARTIAL":
            advisories.append(FarmerAdvisoryItem(
                advisory_id="ADV_SOIL_PARTIAL",
                priority="INFO",
                title="Partial Soil Sensor Telemetry",
                message=f"Active parameters: {', '.join(data_quality.available_parameters)}. Missing: {', '.join(data_quality.missing_parameters)}.",
                recommended_action="Inspect sensor configuration map or wire terminals for unmeasured channels.",
                reason="Incomplete register mapping.",
                source="DATA_QUALITY_CHECK",
                confidence=1.0,
                localization_key="ADVISORY_SOIL_PARTIAL",
                is_demo=is_demo,
                category="Sensor Diagnostics"
            ))

        # 4. Configured Rule Advisories
        for ev in evidence:
            if ev.factor_id == "SOIL_MOISTURE_LOW":
                advisories.append(FarmerAdvisoryItem(
                    advisory_id="ADV_SOIL_DRY",
                    priority="HIGH",
                    title="Soil Moisture Stress (Low)",
                    message=ev.description,
                    recommended_action="Plan irrigation cycle to restore root zone moisture.",
                    reason="Soil moisture fell below configured reference minimum.",
                    source="CONFIGURED_RULE",
                    confidence=ev.confidence,
                    localization_key="ADVISORY_SOIL_MOISTURE_LOW",
                    is_demo=is_demo,
                    category="Irrigation"
                ))
            elif ev.factor_id == "SOIL_MOISTURE_HIGH":
                advisories.append(FarmerAdvisoryItem(
                    advisory_id="ADV_SOIL_WET",
                    priority="MEDIUM",
                    title="Excess Soil Moisture",
                    message=ev.description,
                    recommended_action="Pause irrigation and ensure drainage furrows are clear to prevent root asphyxiation.",
                    reason="Soil moisture exceeded configured reference maximum.",
                    source="CONFIGURED_RULE",
                    confidence=ev.confidence,
                    localization_key="ADVISORY_SOIL_MOISTURE_HIGH",
                    is_demo=is_demo,
                    category="Irrigation"
                ))

        # If no specific advisory generated, add general precaution
        if not advisories:
            advisories.append(FarmerAdvisoryItem(
                advisory_id="ADV_ROUTINE_MONITORING",
                priority="INFO",
                title="Routine Field Monitoring",
                message="Field is currently operating within normal operational parameters.",
                recommended_action="Continue regular crop inspection and record weekly soil sensor readings.",
                reason="No active risk factors identified.",
                source="GENERAL_PRECAUTION",
                confidence=1.0,
                localization_key="ADVISORY_GENERAL",
                is_demo=is_demo,
                category="General"
            ))

        return advisories
