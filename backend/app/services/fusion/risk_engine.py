"""
Transparent, Explainable Risk Assessment Engine for KrishiDrishti Edge.
Enforces:
- UNKNOWN risk level whenever data is insufficient or AI confidence is low.
- Zero assertion of ungrounded causal heuristics.
- Explicit prototype heuristic labeling.
"""
import os
import yaml
from typing import List, Optional, Dict, Any
from app.services.fusion.schemas import (
    FusionInput,
    SoilDataQuality,
    EvidenceItem,
    RiskAssessmentResult
)
from app.core.logging import log_event

class RiskEngine:
    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "knowledge", "risk_config.yaml")
        self.config = self._load_config(config_path)

    def _load_config(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            return {
                "risk_scoring": {"min_data_completeness_for_confident_risk": 0.35},
                "thresholds": {"critical_score": 0.75, "high_score": 0.55, "moderate_score": 0.30}
            }
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def assess_risk(
        self,
        fusion_input: FusionInput,
        evidence: List[EvidenceItem],
        data_quality: SoilDataQuality,
        is_demo: bool = False
    ) -> RiskAssessmentResult:
        """
        Synthesizes multi-modal evidence into an explainable risk assessment.
        Returns UNKNOWN if insufficient inputs exist.
        """
        # 1. Calculate Data Completeness Score (0.0 to 1.0)
        vision = fusion_input.vision
        soil = fusion_input.soil
        history = fusion_input.history

        has_vision = vision is not None and vision.status == "accepted"
        soil_param_ratio = len(data_quality.available_parameters) / 6.0
        has_history = history is not None and history.has_sufficient_history

        data_completeness = round(
            (0.45 if has_vision else 0.0) +
            (0.35 * soil_param_ratio) +
            (0.20 if has_history else 0.0),
            2
        )

        min_completeness = self.config.get("risk_scoring", {}).get("min_data_completeness_for_confident_risk", 0.35)

        # 2. Check for Insufficient Data condition
        if data_completeness < min_completeness and not has_vision:
            return RiskAssessmentResult(
                risk_level="UNKNOWN",
                score=None,
                confidence=0.0,
                factors=evidence,
                explanation="Not enough reliable data for a risk assessment. Please capture a crop scan or take a soil reading.",
                data_completeness=data_completeness,
                is_demo=is_demo,
                disease_risk="UNKNOWN",
                pest_risk="UNKNOWN",
                soil_stress="UNKNOWN",
                water_stress="UNKNOWN",
                is_prototype_heuristic=True
            )

        # 3. Evaluate Modality Drivers
        disease_risk = "LOW"
        pest_risk = "LOW"
        soil_stress = "LOW"
        water_stress = "LOW"
        risk_score = 0.10

        explanations: List[str] = []

        # Vision Driver
        if has_vision:
            pred = vision.prediction.lower()
            if "blight" in pred or "rust" in pred or "blast" in pred:
                if "late blight" in pred or "blast" in pred:
                    disease_risk = "CRITICAL"
                    risk_score += 0.65
                    explanations.append(f"Severe pathology '{vision.prediction}' detected by AI vision ({int(vision.confidence*100)}% confidence).")
                else:
                    disease_risk = "HIGH"
                    risk_score += 0.45
                    explanations.append(f"Crop disease '{vision.prediction}' identified by AI vision ({int(vision.confidence*100)}% confidence).")
            elif "healthy" in pred:
                disease_risk = "LOW"
                explanations.append(f"Leaf observed healthy with {int(vision.confidence*100)}% confidence.")
            else:
                disease_risk = "MODERATE"
                risk_score += 0.25
                explanations.append(f"Unclassified leaf symptom detected: '{vision.prediction}'.")
        elif vision and vision.status == "low_confidence":
            disease_risk = "UNKNOWN"
            explanations.append("Crop scan confidence was low; disease risk is gated as uncertain.")

        # Soil Evidence Drivers
        for ev in evidence:
            if ev.category == "SOIL" and ev.severity in ["MEDIUM", "HIGH", "CRITICAL"]:
                if "MOISTURE" in ev.factor_id:
                    water_stress = "MODERATE"
                    risk_score += 0.15
                    explanations.append(ev.description)
                elif "PH" in ev.factor_id:
                    soil_stress = "MODERATE"
                    risk_score += 0.10
                    explanations.append(ev.description)

        # History Drivers
        if history and history.repeated_diagnosis:
            risk_score += 0.15
            explanations.append(f"Pathology persistent across {history.scans_count} recorded scans.")

        # Clamp Score
        risk_score = min(max(round(risk_score, 2), 0.0), 1.0)

        # Determine Final Level
        thresholds = self.config.get("thresholds", {})
        crit_thresh = thresholds.get("critical_score", 0.75)
        high_thresh = thresholds.get("high_score", 0.55)
        mod_thresh = thresholds.get("moderate_score", 0.30)

        if disease_risk == "CRITICAL" or risk_score >= crit_thresh:
            overall_level = "CRITICAL"
        elif disease_risk == "HIGH" or risk_score >= high_thresh:
            overall_level = "HIGH"
        elif risk_score >= mod_thresh:
            overall_level = "MODERATE"
        else:
            overall_level = "LOW"

        final_explanation = " ".join(explanations) if explanations else "Field operating within baseline parameters."

        return RiskAssessmentResult(
            risk_level=overall_level,
            score=risk_score,
            confidence=round(data_completeness * 0.9, 2),
            factors=evidence,
            explanation=final_explanation,
            data_completeness=data_completeness,
            is_demo=is_demo,
            disease_risk=disease_risk,
            pest_risk=pest_risk,
            soil_stress=soil_stress,
            water_stress=water_stress,
            is_prototype_heuristic=True
        )
