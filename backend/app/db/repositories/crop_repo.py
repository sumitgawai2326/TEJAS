"""
Repository for Crop Entities.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Crop

class CropRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, field_id: int, crop_name: str, variety: Optional[str] = None, sowing_date: Optional[str] = None, growth_stage: str = "Vegetative") -> Crop:
        crop = Crop(field_id=field_id, crop_name=crop_name, variety=variety, sowing_date=sowing_date, growth_stage=growth_stage)
        self.db.add(crop)
        self.db.commit()
        self.db.refresh(crop)
        return crop

    def get_by_id(self, crop_id: int) -> Optional[Crop]:
        return self.db.query(Crop).filter(Crop.id == crop_id).first()

    def list_by_field(self, field_id: int) -> List[Crop]:
        return self.db.query(Crop).filter(Crop.field_id == field_id).all()

    def delete(self, crop_id: int) -> bool:
        crop = self.get_by_id(crop_id)
        if crop:
            self.db.delete(crop)
            self.db.commit()
            return True
        return False
