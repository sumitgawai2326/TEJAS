"""
Temporal Trend Engine for KrishiDrishti Edge Field Intelligence.
Performs fact-based historical comparisons without ungrounded causal claims.
"""
from typing import List, Optional, Dict, Any
from app.services.fusion.schemas import HistorySummary, EvidenceItem, SoilSignal, VisionSignal
from app.db.models import Scan, SoilReading

class TemporalTrendEngine:
    """Analyzes historical observations to identify genuine numeric deltas and repeated signals."""

    @staticmethod
    def analyze_history(
        recent_scans: List[Scan],
        recent_soil: List[SoilReading],
        current_vision: Optional[VisionSignal] = None,
        current_soil: Optional[SoilSignal] = None,
        is_demo: bool = False
    ) -> HistorySummary:
        scans_cnt = len(recent_scans)
        soil_cnt = len(recent_soil)
        notes: List[str] = []
        repeated_diag: Optional[str] = None
        moisture_delta: Optional[float] = None
        temp_delta: Optional[float] = None

        has_sufficient = (scans_cnt >= 2) or (soil_cnt >= 2)

        # 1. Vision Pathology Repeat Detection
        if current_vision and current_vision.status == "accepted" and scans_cnt >= 1:
            prev_scan = recent_scans[0]
            if prev_scan.prediction == current_vision.prediction and current_vision.prediction not in ["Healthy Leaf", "Unknown / Low Confidence"]:
                repeated_diag = current_vision.prediction
                notes.append(f"Repeated observation: '{current_vision.prediction}' detected in consecutive field scans.")

        # 2. Soil Moisture & Temperature Numeric Deltas
        if soil_cnt >= 2:
            latest_s = recent_soil[0]
            prev_s = recent_soil[1]

            if latest_s.moisture is not None and prev_s.moisture is not None:
                moisture_delta = round(latest_s.moisture - prev_s.moisture, 2)
                notes.append(f"Soil moisture delta: {moisture_delta:+0.1f}% (Previous: {prev_s.moisture}%, Latest: {latest_s.moisture}%).")

            if latest_s.temperature is not None and prev_s.temperature is not None:
                temp_delta = round(latest_s.temperature - prev_s.temperature, 2)
                notes.append(f"Soil temperature delta: {temp_delta:+0.1f}°C (Previous: {prev_s.temperature}°C, Latest: {latest_s.temperature}°C).")
        elif soil_cnt == 1:
            notes.append("Single historical soil reading available; baseline recorded.")
        else:
            notes.append("INSUFFICIENT_HISTORY: No prior soil measurements recorded.")

        if scans_cnt == 0:
            notes.append("INSUFFICIENT_HISTORY: No prior crop scans recorded.")

        return HistorySummary(
            scans_count=scans_cnt,
            soil_readings_count=soil_cnt,
            repeated_diagnosis=repeated_diag,
            soil_moisture_delta=moisture_delta,
            soil_temp_delta=temp_delta,
            has_sufficient_history=has_sufficient,
            notes=notes
        )

    @staticmethod
    def extract_trend_evidence(history: HistorySummary, is_demo: bool = False) -> List[EvidenceItem]:
        """Extracts structured EvidenceItems from historical trend summaries."""
        evidence: List[EvidenceItem] = []

        if history.repeated_diagnosis:
            evidence.append(EvidenceItem(
                factor_id="HISTORY_PERSISTENT_DIAGNOSIS",
                category="HISTORY",
                title="Persistent Pathology Signal",
                description=f"Crop pathology '{history.repeated_diagnosis}' detected across multiple observation sessions.",
                severity="HIGH",
                confidence=0.85,
                source="HISTORICAL_OBSERVATION",
                is_demo=is_demo
            ))

        if history.soil_moisture_delta is not None:
            evidence.append(EvidenceItem(
                factor_id="HISTORY_SOIL_MOISTURE_DELTA",
                category="HISTORY",
                title="Measured Soil Moisture Change",
                description=f"Soil moisture changed by {history.soil_moisture_delta:+0.1f}% between recent records.",
                severity="INFO",
                confidence=1.0,
                source="HISTORICAL_OBSERVATION",
                is_demo=is_demo,
                details={"delta": history.soil_moisture_delta}
            ))

        if not history.has_sufficient_history:
            evidence.append(EvidenceItem(
                factor_id="HISTORY_INSUFFICIENT_DATA",
                category="DATA_QUALITY",
                title="Limited Field History",
                description="Field has limited historical observations; baseline timeline is being established.",
                severity="INFO",
                confidence=1.0,
                source="DATA_QUALITY_CHECK",
                is_demo=is_demo
            ))

        return evidence
