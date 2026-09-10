"""
SQLAlchemy ORM Models for KrishiDrishti Edge Offline Field Intelligence.
Entities: Farm, Field, Crop, Scan, SoilReading, RiskAssessment, Advisory, DeviceEvent.
"""
import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Index
)
from sqlalchemy.orm import relationship
from app.db.database import Base

def utcnow_str() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

class Farm(Base):
    __tablename__ = "farms"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    location_name = Column(String(150), nullable=True)
    created_at = Column(String(40), default=utcnow_str, nullable=False)
    updated_at = Column(String(40), default=utcnow_str, onupdate=utcnow_str, nullable=False)

    # Relationships
    fields = relationship("Field", back_populates="farm", cascade="all, delete-orphan")

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    farm_id = Column(Integer, ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    area = Column(Float, nullable=True)
    area_unit = Column(String(20), default="Acre", nullable=False)
    soil_type = Column(String(50), nullable=True)
    created_at = Column(String(40), default=utcnow_str, nullable=False)
    updated_at = Column(String(40), default=utcnow_str, onupdate=utcnow_str, nullable=False)

    # Relationships
    farm = relationship("Farm", back_populates="fields")
    crops = relationship("Crop", back_populates="field", cascade="all, delete-orphan")
    scans = relationship("Scan", back_populates="field", cascade="all, delete-orphan")
    soil_readings = relationship("SoilReading", back_populates="field", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="field", cascade="all, delete-orphan")
    advisories = relationship("Advisory", back_populates="field", cascade="all, delete-orphan")

class Crop(Base):
    __tablename__ = "crops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    crop_name = Column(String(100), nullable=False)
    variety = Column(String(100), nullable=True)
    sowing_date = Column(String(40), nullable=True)
    growth_stage = Column(String(50), default="Vegetative", nullable=False)
    created_at = Column(String(40), default=utcnow_str, nullable=False)
    updated_at = Column(String(40), default=utcnow_str, onupdate=utcnow_str, nullable=False)

    # Relationship
    field = relationship("Field", back_populates="crops")

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(String(40), default=utcnow_str, nullable=False, index=True)
    image_path = Column(String(255), nullable=True)
    image_quality = Column(Float, nullable=True)
    prediction = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    model_name = Column(String(100), nullable=False)
    model_version = Column(String(50), nullable=False)
    inference_device = Column(String(30), default="CPU", nullable=False)
    status = Column(String(40), default="CONFIDENT", nullable=False)

    # Relationships
    field = relationship("Field", back_populates="scans")
    risk_assessments = relationship("RiskAssessment", back_populates="scan")

class SoilReading(Base):
    __tablename__ = "soil_readings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp = Column(String(40), default=utcnow_str, nullable=False, index=True)

    # ZERO HARDWARE HALLUCINATION: All 6 parameters strictly Nullable
    nitrogen = Column(Float, nullable=True)
    phosphorus = Column(Float, nullable=True)
    potassium = Column(Float, nullable=True)
    ph = Column(Float, nullable=True)
    moisture = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)

    sensor_status = Column(String(50), nullable=False)
    is_mock = Column(Boolean, default=False, nullable=False, index=True)
    raw_payload_reference = Column(String(255), nullable=True)

    # Relationships
    field = relationship("Field", back_populates="soil_readings")
    risk_assessments = relationship("RiskAssessment", back_populates="soil_reading")

class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="SET NULL"), nullable=True)
    soil_reading_id = Column(Integer, ForeignKey("soil_readings.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(String(40), default=utcnow_str, nullable=False, index=True)

    field_health_score = Column(Float, nullable=True)
    disease_risk = Column(String(30), nullable=True)
    pest_risk = Column(String(30), nullable=True)
    soil_stress = Column(String(30), nullable=True)
    water_stress = Column(String(30), nullable=True)
    status = Column(String(40), default="CALCULATED", nullable=False)

    # Relationships
    field = relationship("Field", back_populates="risk_assessments")
    scan = relationship("Scan", back_populates="risk_assessments")
    soil_reading = relationship("SoilReading", back_populates="risk_assessments")
    advisories = relationship("Advisory", back_populates="risk_assessment")

class Advisory(Base):
    __tablename__ = "advisories"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    field_id = Column(Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False, index=True)
    risk_assessment_id = Column(Integer, ForeignKey("risk_assessments.id", ondelete="SET NULL"), nullable=True)
    timestamp = Column(String(40), default=utcnow_str, nullable=False, index=True)

    language = Column(String(10), default="en", nullable=False)
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(String(30), default="Info", nullable=False)
    category = Column(String(50), default="General", nullable=False)

    # Relationships
    field = relationship("Field", back_populates="advisories")
    risk_assessment = relationship("RiskAssessment", back_populates="advisories")

class DeviceEvent(Base):
    __tablename__ = "device_events"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timestamp = Column(String(40), default=utcnow_str, nullable=False, index=True)
    subsystem = Column(String(30), nullable=False, index=True)  # SOIL, CAMERA, AI, SYSTEM, DEVICE
    event_type = Column(String(50), nullable=False)             # SENSOR_DISCONNECTED, CAMERA_UNAVAILABLE, etc.
    severity = Column(String(20), default="INFO", nullable=False) # INFO, WARNING, ERROR
    message = Column(String(255), nullable=False)
    details = Column(Text, nullable=True)

# Optional composite indexes for chronological history queries
Index("idx_soil_field_time", SoilReading.field_id, SoilReading.timestamp.desc())
Index("idx_scan_field_time", Scan.field_id, Scan.timestamp.desc())
Index("idx_risk_field_time", RiskAssessment.field_id, RiskAssessment.timestamp.desc())
Index("idx_advisory_field_time", Advisory.field_id, Advisory.timestamp.desc())
