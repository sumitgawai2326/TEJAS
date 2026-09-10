"""
Repository for Crop Scan & AI Pathology Records.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Scan

class ScanRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        field_id: int,
        prediction: str,
        confidence: float,
        model_name: str,
        model_version: str,
        image_path: Optional[str] = None,
        image_quality: Optional[float] = None,
        inference_device: str = "CPU",
        status: str = "CONFIDENT"
    ) -> Scan:
        scan = Scan(
            field_id=field_id,
            prediction=prediction,
            confidence=confidence,
            model_name=model_name,
            model_version=model_version,
            image_path=image_path,
            image_quality=image_quality,
            inference_device=inference_device,
            status=status
        )
        self.db.add(scan)
        self.db.commit()
        self.db.refresh(scan)
        return scan

    def get_by_id(self, scan_id: int) -> Optional[Scan]:
        return self.db.query(Scan).filter(Scan.id == scan_id).first()

    def list_by_field(self, field_id: int, limit: int = 50) -> List[Scan]:
        return self.db.query(Scan).filter(Scan.field_id == field_id).order_by(Scan.timestamp.desc()).limit(limit).all()
