"""
Repository for Soil Intelligence Telemetry.
Zero Hardware Hallucination: Strict storage of nullable values.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import SoilReading

class SoilReadingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        field_id: int,
        sensor_status: str,
        nitrogen: Optional[float] = None,
        phosphorus: Optional[float] = None,
        potassium: Optional[float] = None,
        ph: Optional[float] = None,
        moisture: Optional[float] = None,
        temperature: Optional[float] = None,
        is_mock: bool = False,
        raw_payload_reference: Optional[str] = None
    ) -> SoilReading:
        reading = SoilReading(
            field_id=field_id,
            sensor_status=sensor_status,
            nitrogen=nitrogen,
            phosphorus=phosphorus,
            potassium=potassium,
            ph=ph,
            moisture=moisture,
            temperature=temperature,
            is_mock=is_mock,
            raw_payload_reference=raw_payload_reference
        )
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_by_id(self, reading_id: int) -> Optional[SoilReading]:
        return self.db.query(SoilReading).filter(SoilReading.id == reading_id).first()

    def list_by_field(self, field_id: int, limit: int = 50) -> List[SoilReading]:
        return self.db.query(SoilReading).filter(SoilReading.field_id == field_id).order_by(SoilReading.timestamp.desc()).limit(limit).all()

    def get_latest_by_field(self, field_id: int) -> Optional[SoilReading]:
        return self.db.query(SoilReading).filter(SoilReading.field_id == field_id).order_by(SoilReading.timestamp.desc()).first()
