"""
Unit tests for Offline SQLite Database Models, Repositories, and Zero Hallucination Storage.
"""
import pytest
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.db.database import Base
from app.db.models import Farm, Field, Crop, Scan, SoilReading, RiskAssessment, Advisory, DeviceEvent
from app.db.repositories import (
    FarmRepository,
    FieldRepository,
    CropRepository,
    ScanRepository,
    SoilReadingRepository,
    RiskAssessmentRepository,
    AdvisoryRepository,
    DeviceEventRepository,
    FieldHistoryRepository
)

# Use in-memory SQLite for high-speed isolated unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def test_db():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_farm_and_field_creation(test_db):
    """Verify Farm and Field hierarchy can be created and queried."""
    farm_repo = FarmRepository(test_db)
    farm = farm_repo.create(name="Maharashtra Model Farm", location_name="Pune District")
    assert farm.id is not None
    assert farm.name == "Maharashtra Model Farm"

    field_repo = FieldRepository(test_db)
    field = field_repo.create(farm_id=farm.id, name="Tomato Plot 1", area=2.5, area_unit="Acre", soil_type="Black Cotton")
    assert field.id is not None
    assert field.farm_id == farm.id
    assert field.soil_type == "Black Cotton"

def test_crop_creation(test_db):
    """Verify Crop records attach to a Field."""
    farm = FarmRepository(test_db).create(name="Farm A")
    field = FieldRepository(test_db).create(farm_id=farm.id, name="Field 1")
    
    crop_repo = CropRepository(test_db)
    crop = crop_repo.create(
        field_id=field.id,
        crop_name="Tomato",
        variety="Abhinav",
        growth_stage="Flowering"
    )
    assert crop.id is not None
    assert crop.crop_name == "Tomato"
    assert crop.growth_stage == "Flowering"

def test_scan_storage(test_db):
    """Verify Vision Scan records are persisted without binary image bloat."""
    farm = FarmRepository(test_db).create(name="Farm A")
    field = FieldRepository(test_db).create(farm_id=farm.id, name="Field 1")

    scan_repo = ScanRepository(test_db)
    scan = scan_repo.create(
        field_id=field.id,
        prediction="Tomato Early Blight",
        confidence=0.91,
        model_name="KrishiDrishti-DemoVision-V1",
        model_version="0.1.0",
        image_path="/data/captures/scan_001.jpg",
        image_quality=0.88,
        inference_device="CPU",
        status="CONFIDENT"
    )
    assert scan.id is not None
    assert scan.prediction == "Tomato Early Blight"
    assert scan.image_path == "/data/captures/scan_001.jpg"

def test_soil_reading_null_values_zero_hallucination(test_db):
    """
    CRITICAL: Verify disconnected soil reading stores NULL measurements
    and NEVER stores fabricated numbers.
    """
    farm = FarmRepository(test_db).create(name="Farm A")
    field = FieldRepository(test_db).create(farm_id=farm.id, name="Field 1")

    soil_repo = SoilReadingRepository(test_db)
    reading = soil_repo.create(
        field_id=field.id,
        sensor_status="SENSOR DISCONNECTED",
        nitrogen=None,
        phosphorus=None,
        potassium=None,
        ph=None,
        moisture=None,
        temperature=None,
        is_mock=False
    )
    assert reading.id is not None
    assert reading.sensor_status == "SENSOR DISCONNECTED"
    assert reading.is_mock is False
    assert reading.nitrogen is None
    assert reading.phosphorus is None
    assert reading.potassium is None
    assert reading.ph is None
    assert reading.moisture is None
    assert reading.temperature is None

def test_mock_soil_reading_storage(test_db):
    """Verify demo mode soil telemetry stores simulated values with is_mock=True."""
    farm = FarmRepository(test_db).create(name="Farm A")
    field = FieldRepository(test_db).create(farm_id=farm.id, name="Field 1")

    soil_repo = SoilReadingRepository(test_db)
    reading = soil_repo.create(
        field_id=field.id,
        sensor_status="DEMO_SIMULATION",
        nitrogen=48.0,
        phosphorus=32.0,
        potassium=65.0,
        ph=6.5,
        moisture=24.0,
        temperature=26.0,
        is_mock=True
    )
    assert reading.id is not None
    assert reading.is_mock is True
    assert reading.nitrogen == 48.0

def test_risk_and_advisory_storage(test_db):
    """Verify RiskAssessment and Advisory records are stored with relationships."""
    farm = FarmRepository(test_db).create(name="Farm A")
    field = FieldRepository(test_db).create(farm_id=farm.id, name="Field 1")

    risk_repo = RiskAssessmentRepository(test_db)
    risk = risk_repo.create(
        field_id=field.id,
        field_health_score=78.5,
        disease_risk="Medium",
        water_stress="Low"
    )
    assert risk.id is not None
    assert risk.field_health_score == 78.5

    adv_repo = AdvisoryRepository(test_db)
    adv = adv_repo.create(
        field_id=field.id,
        risk_assessment_id=risk.id,
        title="Check early blight symptoms",
        message="Mild early blight detected. Maintain standard monitoring.",
        language="en",
        severity="Warning"
    )
    assert adv.id is not None
    assert adv.risk_assessment_id == risk.id

def test_device_event_storage(test_db):
    """Verify DeviceEvent records hardware diagnostic logs."""
    event_repo = DeviceEventRepository(test_db)
    event = event_repo.create(
        subsystem="SOIL",
        event_type="SENSOR_DISCONNECTED",
        message="RS485 communication timeout on COM3",
        severity="WARNING",
        details="Probe unpowered or unplugged"
    )
    assert event.id is not None
    assert event.subsystem == "SOIL"
    assert event.event_type == "SENSOR_DISCONNECTED"

def test_field_history_timeline(test_db):
    """Verify FieldHistoryRepository aggregates chronological timeline."""
    farm = FarmRepository(test_db).create(name="Farm A")
    field = FieldRepository(test_db).create(farm_id=farm.id, name="Plot North")

    ScanRepository(test_db).create(
        field_id=field.id,
        prediction="Tomato Early Blight",
        confidence=0.89,
        model_name="DemoVision",
        model_version="0.1.0"
    )
    SoilReadingRepository(test_db).create(
        field_id=field.id,
        sensor_status="DEMO_SIMULATION",
        nitrogen=50.0,
        moisture=25.0,
        is_mock=True
    )
    AdvisoryRepository(test_db).create(
        field_id=field.id,
        title="Irrigation recommendation",
        message="Moisture level optimal.",
        language="en"
    )

    history_repo = FieldHistoryRepository(test_db)
    timeline = history_repo.get_field_timeline(field.id)
    assert timeline["field_id"] == field.id
    assert timeline["total_timeline_entries"] == 3
    assert timeline["scans_count"] == 1
    assert timeline["soil_readings_count"] == 1
    assert timeline["advisories_count"] == 1
