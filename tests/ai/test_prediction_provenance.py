"""
Tests for Phase 8 Prediction Provenance, Multi-Tier Confidence, and Evidence Tracking.
"""
import pytest
import os
import sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.services.fusion.fusion_engine import fusion_engine
from app.services.fusion.schemas import (
    FusionInput,
    VisionSignal,
    SoilSignal,
    CropContext,
    HistorySummary
)
from app.services.advisory.advisory_engine import advisory_engine
from ai.inference.manager import VisionModelManager
from ai.preprocessing.quality import ImageQualityValidator

def test_multi_tier_confidence_evaluation():
    """Verify HIGH, MEDIUM, and LOW confidence tiers."""
    manager = VisionModelManager(demo_mode=True, confidence_threshold=0.70)
    # High confidence >= 0.85
    img = np.full((224, 224, 3), 128, dtype=np.uint8)
    validator = ImageQualityValidator()
    q_res = validator.validate(img)

    res_high = manager.analyze_image(img, q_res, raw_confidence_override=0.92)
    assert res_high["confidence_tier"] == "HIGH"
    assert res_high["status"] == "accepted"

    # Medium confidence >= 0.70 and < 0.85
    res_med = manager.analyze_image(img, q_res, raw_confidence_override=0.75)
    assert res_med["confidence_tier"] == "MEDIUM"
    assert res_med["status"] == "accepted"

    # Low confidence < 0.70
    res_low = manager.analyze_image(img, q_res, raw_confidence_override=0.45)
    assert res_low["confidence_tier"] == "LOW"
    assert res_low["status"] == "low_confidence"

def test_fusion_and_advisory_provenance():
    """Verify modality provenance is accurately computed and attached."""
    f_input = FusionInput(
        field_id=1,
        crop_context=CropContext(crop_name="Tomato", growth_stage="Flowering"),
        vision=VisionSignal(
            status="accepted",
            prediction="Tomato Early Blight",
            confidence=0.89,
            model_name="DemoVision",
            model_version="0.1.0",
            is_demo=True
        ),
        soil=SoilSignal(
            nitrogen=45.0,
            phosphorus=20.0,
            potassium=150.0,
            ph=6.5,
            moisture=22.0,
            temperature=25.0,
            sensor_status="CONNECTED",
            is_mock=True,
            availability="COMPLETE"
        ),
        history=HistorySummary(has_sufficient_history=True, scans_count=5)
    )

    fusion_res = fusion_engine.fuse(f_input)
    assert fusion_res.vision_provenance == "DEMO_VISION"
    assert fusion_res.soil_provenance == "MOCK_SOIL"
    assert fusion_res.history_provenance == "SUFFICIENT_HISTORY"

    adv_res = advisory_engine.generate(
        field_id=1,
        risk=fusion_res.risk,
        evidence=fusion_res.evidence,
        data_quality=fusion_res.data_quality,
        vision=f_input.vision,
        is_demo=fusion_res.is_demo
    )
    assert len(adv_res.advisories) > 0
    for adv in adv_res.advisories:
        assert adv.source in [
            "MODEL", "SOIL", "HISTORY", "RULE", "COMBINED",
            "AI_OBSERVATION", "SOIL_OBSERVATION", "HISTORICAL_OBSERVATION",
            "CONFIGURED_RULE", "GENERAL_PRECAUTION", "DATA_QUALITY_CHECK"
        ]
