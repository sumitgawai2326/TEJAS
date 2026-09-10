"""
Repository for Agronomic Advisory Records.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Advisory

class AdvisoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        field_id: int,
        title: str,
        message: str,
        language: str = "en",
        severity: str = "Info",
        category: str = "General",
        risk_assessment_id: Optional[int] = None
    ) -> Advisory:
        advisory = Advisory(
            field_id=field_id,
            title=title,
            message=message,
            language=language,
            severity=severity,
            category=category,
            risk_assessment_id=risk_assessment_id
        )
        self.db.add(advisory)
        self.db.commit()
        self.db.refresh(advisory)
        return advisory

    def list_by_field(self, field_id: int, language: Optional[str] = None, limit: int = 50) -> List[Advisory]:
        q = self.db.query(Advisory).filter(Advisory.field_id == field_id)
        if language:
            q = q.filter(Advisory.language == language)
        return q.order_by(Advisory.timestamp.desc()).limit(limit).all()
