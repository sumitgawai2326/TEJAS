"""
Comprehensive Unit & Integration Tests for Phase 5: Crop + Soil Intelligence Fusion Engine.
Validates:
1. Complete Fusion & Multi-Modal Evidence Synthesis
2. Data Quality (Complete, Partial, Unavailable, Mock)
3. Zero Hardware & Agronomic Hallucination (Strict Nullability, Disabled Rules)
4. Temporal Trend Engine (Deltas, Repeat Pathology, Insufficient History)
5. Risk Engine (Explainable Factors, Gating, UNKNOWN State)
6. Advisory Engine (Farmer-friendly Guidance, Zero Chemical Doses, Localization Keys)
7. SQLite Persistence & Field History Timeline Integration
8. REST API Endpoints (/analyze, /risk/latest, /risk/history, /advisories)
"""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings
from app.db.database import SessionLocal, init_db
from app.db.models import Farm, Field, Scan, SoilReading, RiskAssessment, Advisory
from app.db.repositories import (
    FarmRepository,
    FieldRepository,
    ScanRepository,
    SoilReadingRepository,
    RiskAssessmentRepository,
    AdvisoryRepository,
    FieldHistoryRepository
)
from app.services.fusion import (
    FusionEngine,
    FusionInput,
    VisionSignal,
    SoilSignal,
    CropContext,
    HistorySummary
)
from app.services.fusion.evidence import EvidenceSynthesizer
from app.services.fusion.rules import AgronomicRulesEngine
from app.services.fusion.trends import TemporalTrendEngine
from app.services.fusion.risk_engine import RiskEngine
from app.services.advisory import AdvisoryEngine, AdvisoryRules

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

def create_test_field(name: str = "Test Field Alpha") -> int:
    db = SessionLocal()
    farm_repo = FarmRepository(db)
    farm = farm_repo.get_first_or_create(default_name="Fusion Test Farm", location_name="Pune")
    field_repo = FieldRepository(db)
    field = field_repo.create(farm_id=farm.id, name=name, area=2.0, soil_type="Black Cotton")
    db.close()
    return field.id

# ---------------------------------------------------------
# 1. Fusion Engine & Data Quality Tests
# ---------------------------------------------------------

def test_complete_fusion_input():
    engine = FusionEngine()
    fusion_input = FusionInput(
        field_id=1,
        crop_context=CropContext(crop_name="Tomato", growth_stage="Fruiting"),
        vision=VisionSignal(status="accepted", prediction="Tomato Early Blight", confidence=0.92, is_demo=False),
        soil=SoilSignal(nitrogen=45.0, phosphorus=20.0, potassium=160.0, ph=6.8, moisture=25.0, temperature=26.0, availability="COMPLETE", is_mock=False),
        history=HistorySummary(scans_count=2, soil_readings_count=2, has_sufficient_history=True)
    )
    result = engine.fuse(fusion_input)
    assert result.overall_status in ["SUCCESS", "PARTIAL_DATA"]
    assert result.risk.risk_level in ["HIGH", "MODERATE", "CRITICAL"]
    assert result.data_quality.status == "COMPLETE"
    assert len(result.evidence) > 0
    assert any(e.category == "VISION" for e in result.evidence)
    assert any(e.category == "SOIL" for e in result.evidence)

def test_missing_soil_data():
    engine = FusionEngine()
    fusion_input = FusionInput(
        field_id=1,
        crop_context=CropContext(crop_name="Tomato"),
        vision=VisionSignal(status="accepted", prediction="Healthy Leaf", confidence=0.95),
        soil=SoilSignal(availability="UNAVAILABLE", sensor_status="DISCONNECTED", is_mock=False)
    )
    result = engine.fuse(fusion_input)
    assert result.data_quality.status == "UNAVAILABLE"
    assert "SOIL_TELEMETRY" in result.missing_data
    assert any(e.factor_id == "VISION_PATHOLOGY_SIGNAL" for e in result.evidence)
    assert result.risk.risk_level == "LOW"

def test_partial_soil_data():
    synthesizer = EvidenceSynthesizer()
    soil = SoilSignal(moisture=22.5, nitrogen=30.0, availability="PARTIAL", is_mock=False)
    quality = synthesizer.assess_soil_quality(soil)
    
    assert quality.status == "PARTIAL"
    assert "moisture" in quality.available_parameters
    assert "nitrogen" in quality.available_parameters
    assert "ph" in quality.missing_parameters
    assert "potassium" in quality.missing_parameters

def test_missing_vision_result():
    engine = FusionEngine()
    fusion_input = FusionInput(
        field_id=1,
        soil=SoilSignal(moisture=24.0, availability="PARTIAL"),
        vision=VisionSignal(status="unavailable")
    )
    result = engine.fuse(fusion_input)
    assert "CROP_VISION_SCAN" in result.missing_data
    assert any(e.factor_id == "VISION_DATA_UNAVAILABLE" for e in result.evidence)

def test_low_confidence_vision_gating():
    engine = FusionEngine()
    fusion_input = FusionInput(
        field_id=1,
        vision=VisionSignal(status="low_confidence", prediction="Unknown / Low Confidence", confidence=0.52),
        soil=SoilSignal(availability="UNAVAILABLE")
    )
    result = engine.fuse(fusion_input)
    assert result.risk.disease_risk == "UNKNOWN"
    assert any(e.factor_id == "VISION_CONFIDENCE_GATED" for e in result.evidence)

def test_unknown_risk_state():
    engine = FusionEngine()
    # No vision, no soil, no history -> MUST return UNKNOWN
    fusion_input = FusionInput(
        field_id=1,
        vision=VisionSignal(status="unavailable"),
        soil=SoilSignal(availability="UNAVAILABLE"),
        history=HistorySummary(has_sufficient_history=False)
    )
    result = engine.fuse(fusion_input)
    assert result.risk.risk_level == "UNKNOWN"
    assert result.risk.score is None
    assert result.overall_status == "INSUFFICIENT_DATA"
    assert "Not enough reliable data" in result.risk.explanation

# ---------------------------------------------------------
# 2. Agronomic Rules & Zero Hallucination Tests
# ---------------------------------------------------------

def test_disabled_rule_behavior():
    rules_engine = AgronomicRulesEngine()
    soil = SoilSignal(moisture=10.0, ph=5.5)
    evidence = rules_engine.evaluate(soil, CropContext(crop_name="Tomato"))
    
    # Since rules default to disabled/unconfigured, it should honestly report observation rather than fake violation
    assert any("UNCONFIGURED" in e.factor_id or e.source == "SOIL_OBSERVATION" for e in evidence)

def test_no_fabricated_soil_values_or_predictions():
    """Verify that None values are never coerced to zero or invented numbers."""
    rules_engine = AgronomicRulesEngine()
    soil = SoilSignal(nitrogen=None, phosphorus=None, moisture=None)
    evidence = rules_engine.evaluate(soil, CropContext(crop_name="Tomato"))
    
    assert len(evidence) == 0

# ---------------------------------------------------------
# 3. Temporal Trend Engine Tests
# ---------------------------------------------------------

def test_insufficient_history():
    history = TemporalTrendEngine.analyze_history(recent_scans=[], recent_soil=[])
    assert history.has_sufficient_history is False
    assert any("INSUFFICIENT_HISTORY" in n for n in history.notes)

def test_historical_soil_delta():
    s1 = SoilReading(field_id=1, moisture=28.0, temperature=24.0, sensor_status="CONNECTED", is_mock=False)
    s2 = SoilReading(field_id=1, moisture=22.0, temperature=27.0, sensor_status="CONNECTED", is_mock=False)
    
    history = TemporalTrendEngine.analyze_history(recent_scans=[], recent_soil=[s1, s2])
    assert history.soil_moisture_delta == 6.0
    assert history.soil_temp_delta == -3.0
    assert history.has_sufficient_history is True

def test_historical_scan_comparison():
    s1 = Scan(field_id=1, prediction="Tomato Early Blight", confidence=0.88, model_name="Demo", model_version="1.0")
    current_vision = VisionSignal(status="accepted", prediction="Tomato Early Blight", confidence=0.91)
    
    history = TemporalTrendEngine.analyze_history(recent_scans=[s1], recent_soil=[], current_vision=current_vision)
    assert history.repeated_diagnosis == "Tomato Early Blight"
    
    evidence = TemporalTrendEngine.extract_trend_evidence(history)
    assert any(e.factor_id == "HISTORY_PERSISTENT_DIAGNOSIS" for e in evidence)

# ---------------------------------------------------------
# 4. Actionable Advisory Engine Tests
# ---------------------------------------------------------

def test_advisory_generation_urgent():
    risk = RiskEngine().assess_risk(
        fusion_input=FusionInput(
            field_id=1,
            vision=VisionSignal(status="accepted", prediction="Tomato Late Blight", confidence=0.95),
            soil=SoilSignal(availability="UNAVAILABLE")
        ),
        evidence=[],
        data_quality=EvidenceSynthesizer.assess_soil_quality(None)
    )
    advisory_res = AdvisoryEngine.generate(
        field_id=1,
        risk=risk,
        evidence=[],
        data_quality=EvidenceSynthesizer.assess_soil_quality(None),
        vision=VisionSignal(status="accepted", prediction="Tomato Late Blight", confidence=0.95)
    )
    assert advisory_res.total_advisories >= 1
    assert advisory_res.primary_advisory is not None
    assert advisory_res.primary_advisory.priority == "URGENT"
    assert "KVK" in advisory_res.primary_advisory.recommended_action or "extension" in advisory_res.primary_advisory.recommended_action
    assert advisory_res.primary_advisory.localization_key == "ADVISORY_PATHOLOGY_CRITICAL"

def test_advisory_with_insufficient_data():
    synthesizer = EvidenceSynthesizer()
    quality = synthesizer.assess_soil_quality(None)
    risk = RiskEngine().assess_risk(
        fusion_input=FusionInput(field_id=1),
        evidence=[],
        data_quality=quality
    )
    advisory_res = AdvisoryEngine.generate(field_id=1, risk=risk, evidence=[], data_quality=quality)
    assert advisory_res.primary_advisory is not None
    assert advisory_res.primary_advisory.localization_key == "RISK_INSUFFICIENT_DATA"
    assert "baseline" in advisory_res.primary_advisory.recommended_action.lower()

# ---------------------------------------------------------
# 5. Database Persistence & Timeline Integration Tests
# ---------------------------------------------------------

def test_risk_and_advisory_persistence():
    field_id = create_test_field("Persistence Field")
    db = SessionLocal()
    
    risk_repo = RiskAssessmentRepository(db)
    saved_risk = risk_repo.create(
        field_id=field_id,
        field_health_score=0.75,
        disease_risk="HIGH",
        pest_risk="LOW",
        soil_stress="LOW",
        water_stress="MODERATE",
        status="HIGH"
    )
    assert saved_risk.id is not None
    
    latest_risk = risk_repo.get_latest_by_field(field_id)
    assert latest_risk is not None
    assert latest_risk.id == saved_risk.id
    
    adv_repo = AdvisoryRepository(db)
    saved_adv = adv_repo.create(
        field_id=field_id,
        title="Prune infected foliage",
        message="Early blight lesions observed.",
        severity="HIGH",
        category="Plant Protection",
        risk_assessment_id=saved_risk.id
    )
    assert saved_adv.id is not None
    
    # Check field timeline includes both
    hist_repo = FieldHistoryRepository(db)
    timeline = hist_repo.get_field_timeline(field_id)
    assert timeline["risk_assessments_count"] >= 1
    assert timeline["advisories_count"] >= 1
    assert any(t["type"] == "RISK_ASSESSMENT" for t in timeline["timeline"])
    assert any(t["type"] == "ADVISORY" for t in timeline["timeline"])
    db.close()

# ---------------------------------------------------------
# 6. REST API Endpoint Tests
# ---------------------------------------------------------

def test_api_field_analyze_endpoint():
    field_id = create_test_field("API Analyze Plot")
    response = client.post(f"/api/fields/{field_id}/analyze")
    assert response.status_code == 200
    data = response.json()
    
    assert "field" in data
    assert data["field"]["id"] == field_id
    assert "risk" in data
    assert "advisories" in data
    assert "data_quality" in data
    assert len(data["advisories"]) >= 1

def test_api_risk_latest_and_history_endpoints():
    field_id = create_test_field("Risk API Plot")
    # Trigger analysis to create records
    client.post(f"/api/fields/{field_id}/analyze")
    
    latest_res = client.get(f"/api/fields/{field_id}/risk/latest")
    assert latest_res.status_code == 200
    assert latest_res.json()["field_id"] == field_id
    
    hist_res = client.get(f"/api/fields/{field_id}/risk/history")
    assert hist_res.status_code == 200
    assert len(hist_res.json()) >= 1

def test_api_list_advisories_endpoint():
    field_id = create_test_field("Advisories API Plot")
    client.post(f"/api/fields/{field_id}/analyze")
    
    adv_res = client.get(f"/api/fields/{field_id}/advisories")
    assert adv_res.status_code == 200
    advisories = adv_res.json()
    assert len(advisories) >= 1
    assert "title" in advisories[0]
    assert "message" in advisories[0]

def test_demo_mode_tagging():
    orig = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = True
        field_id = create_test_field("Demo Tagging Plot")
        response = client.post(f"/api/fields/{field_id}/analyze")
        assert response.status_code == 200
        data = response.json()
        assert data["is_demo"] is True
    finally:
        settings.DEMO_MODE = orig

def test_real_mode_no_mock_contamination():
    orig = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = False
        field_id = create_test_field("Real Hardware Plot")
        response = client.post(f"/api/fields/{field_id}/analyze")
        assert response.status_code == 200
        data = response.json()
        assert data["is_demo"] is False
        assert data["data_quality"]["is_mock"] is False
    finally:
        settings.DEMO_MODE = orig
