"""
Repository for Risk Assessment Records.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import RiskAssessment

class RiskAssessmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        field_id: int,
        field_health_score: Optional[float] = None,
        disease_risk: Optional[str] = None,
        pest_risk: Optional[str] = None,
        soil_stress: Optional[str] = None,
        water_stress: Optional[str] = None,
        scan_id: Optional[int] = None,
        soil_reading_id: Optional[int] = None,
        status: str = "CALCULATED"
    ) -> RiskAssessment:
        risk = RiskAssessment(
            field_id=field_id,
            scan_id=scan_id,
            soil_reading_id=soil_reading_id,
            field_health_score=field_health_score,
            disease_risk=disease_risk,
            pest_risk=pest_risk,
            soil_stress=soil_stress,
            water_stress=water_stress,
            status=status
        )
        self.db.add(risk)
        self.db.commit()
        self.db.refresh(risk)
        return risk

    def list_by_field(self, field_id: int, limit: int = 50) -> List[RiskAssessment]:
        return self.db.query(RiskAssessment).filter(RiskAssessment.field_id == field_id).order_by(RiskAssessment.timestamp.desc()).limit(limit).all()

    def get_latest_by_field(self, field_id: int) -> Optional[RiskAssessment]:
        return self.db.query(RiskAssessment).filter(RiskAssessment.field_id == field_id).order_by(RiskAssessment.timestamp.desc()).first()

