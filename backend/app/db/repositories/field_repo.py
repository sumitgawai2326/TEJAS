"""
Repository for Field Entities.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Field

class FieldRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, farm_id: int, name: str, area: Optional[float] = None, area_unit: str = "Acre", soil_type: Optional[str] = None) -> Field:
        field = Field(farm_id=farm_id, name=name, area=area, area_unit=area_unit, soil_type=soil_type)
        self.db.add(field)
        self.db.commit()
        self.db.refresh(field)
        return field

    def get_by_id(self, field_id: int) -> Optional[Field]:
        return self.db.query(Field).filter(Field.id == field_id).first()

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Field]:
        return self.db.query(Field).offset(skip).limit(limit).all()

    def list_by_farm(self, farm_id: int) -> List[Field]:
        return self.db.query(Field).filter(Field.farm_id == farm_id).all()

    def delete(self, field_id: int) -> bool:
        field = self.get_by_id(field_id)
        if field:
            self.db.delete(field)
            self.db.commit()
            return True
        return False
