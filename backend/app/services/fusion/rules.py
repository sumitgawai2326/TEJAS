"""
Configurable Agronomic Rules Engine for KrishiDrishti Edge.
Enforces Zero Agronomic Hallucination:
- Unconfigured / disabled rules are explicitly reported as UNCONFIGURED.
- Missing (None) sensor parameters are never evaluated against fake defaults.
- Only configured, enabled reference ranges produce rule-based evidence.
"""
import os
import yaml
from typing import Dict, Any, Optional, List
from app.services.fusion.schemas import EvidenceItem, SoilSignal, CropContext
from app.core.logging import log_event

class AgronomicRulesEngine:
    def __init__(self, config_path: Optional[str] = None):
        if not config_path:
            config_path = os.path.join(os.path.dirname(__file__), "knowledge", "agronomic_rules.yaml")
        self.config_path = config_path
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_path):
            log_event("AI", "WARNING", f"Agronomic rules file not found at {self.config_path}. Operating in unconfigured mode.")
            return {"crops": {}}
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {"crops": {}}
        except Exception as e:
            log_event("AI", "ERROR", f"Failed to load agronomic rules: {e}")
            return {"crops": {}}

    def evaluate(
        self,
        soil: Optional[SoilSignal],
        crop_context: Optional[CropContext],
        is_demo: bool = False
    ) -> List[EvidenceItem]:
        """
        Evaluates soil parameters against configured crop rules.
        If a rule is disabled or unconfigured, reports UNCONFIGURED status without inventing thresholds.
        """
        evidence: List[EvidenceItem] = []
        if not soil:
            return evidence

        crop_name = (crop_context.crop_name if crop_context else "general").lower()
        crops_cfg = self.rules.get("crops", {})
        crop_rules = crops_cfg.get(crop_name) or crops_cfg.get("general", {})
        param_rules = crop_rules.get("parameters", {})

        # Evaluate each soil parameter if present
        # Moisture
        if soil.moisture is not None:
            moist_rule = param_rules.get("soil_moisture", {})
            if moist_rule.get("enabled", False):
                min_v = moist_rule.get("min")
                max_v = moist_rule.get("max")
                if min_v is not None and soil.moisture < min_v:
                    evidence.append(EvidenceItem(
                        factor_id="SOIL_MOISTURE_LOW",
                        category="SOIL",
                        title="Soil Moisture Below Configured Reference",
                        description=f"Measured soil moisture ({soil.moisture}%) is below configured minimum ({min_v}%).",
                        severity="MEDIUM",
                        confidence=0.85,
                        source="CONFIGURED_RULE",
                        is_demo=is_demo,
                        details={"parameter": "moisture", "measured": soil.moisture, "min": min_v}
                    ))
                elif max_v is not None and soil.moisture > max_v:
                    evidence.append(EvidenceItem(
                        factor_id="SOIL_MOISTURE_HIGH",
                        category="SOIL",
                        title="Soil Moisture Above Configured Reference",
                        description=f"Measured soil moisture ({soil.moisture}%) is above configured maximum ({max_v}%).",
                        severity="MEDIUM",
                        confidence=0.85,
                        source="CONFIGURED_RULE",
                        is_demo=is_demo,
                        details={"parameter": "moisture", "measured": soil.moisture, "max": max_v}
                    ))
            else:
                # Document unconfigured state honestly
                evidence.append(EvidenceItem(
                    factor_id="SOIL_MOISTURE_MEASURED_UNCONFIGURED_RULE",
                    category="SOIL",
                    title="Soil Moisture Measured",
                    description=f"Soil moisture is {soil.moisture}%. Agronomic reference range is not configured for {crop_name}.",
                    severity="INFO",
                    confidence=1.0,
                    source="SOIL_OBSERVATION",
                    is_demo=is_demo,
                    details={"measured": soil.moisture, "rule_status": "DISABLED_OR_UNCONFIGURED"}
                ))

        # pH
        if soil.ph is not None:
            ph_rule = param_rules.get("soil_ph", {})
            if ph_rule.get("enabled", False):
                min_ph = ph_rule.get("min")
                max_ph = ph_rule.get("max")
                if min_ph is not None and soil.ph < min_ph:
                    evidence.append(EvidenceItem(
                        factor_id="SOIL_PH_ACIDIC",
                        category="SOIL",
                        title="Soil pH Below Configured Reference",
                        description=f"Measured pH ({soil.ph}) is below configured threshold ({min_ph}).",
                        severity="MEDIUM",
                        confidence=0.85,
                        source="CONFIGURED_RULE",
                        is_demo=is_demo
                    ))
            else:
                evidence.append(EvidenceItem(
                    factor_id="SOIL_PH_MEASURED_UNCONFIGURED_RULE",
                    category="SOIL",
                    title="Soil pH Measured",
                    description=f"Soil pH is {soil.ph}. Agronomic reference range is not configured for {crop_name}.",
                    severity="INFO",
                    confidence=1.0,
                    source="SOIL_OBSERVATION",
                    is_demo=is_demo
                ))

        # Nitrogen (N)
        if soil.nitrogen is not None:
            evidence.append(EvidenceItem(
                factor_id="SOIL_NITROGEN_MEASURED",
                category="SOIL",
                title="Soil Nitrogen (N) Measured",
                description=f"Available Nitrogen is {soil.nitrogen} mg/kg.",
                severity="INFO",
                confidence=1.0,
                source="SOIL_OBSERVATION",
                is_demo=is_demo
            ))

        return evidence
