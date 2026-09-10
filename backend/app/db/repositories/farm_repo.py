"""
Repository for Farm Entities.
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import Farm

class FarmRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, name: str, location_name: Optional[str] = None) -> Farm:
        farm = Farm(name=name, location_name=location_name)
        self.db.add(farm)
        self.db.commit()
        self.db.refresh(farm)
        return farm

    def get_by_id(self, farm_id: int) -> Optional[Farm]:
        return self.db.query(Farm).filter(Farm.id == farm_id).first()

    def get_first_or_create(self, default_name: str = "Default Farm", location_name: str = "Local Plot") -> Farm:
        farm = self.db.query(Farm).first()
        if not farm:
            farm = self.create(name=default_name, location_name=location_name)
        return farm

    def list_all(self, skip: int = 0, limit: int = 100) -> List[Farm]:
        return self.db.query(Farm).offset(skip).limit(limit).all()

    def delete(self, farm_id: int) -> bool:
        farm = self.get_by_id(farm_id)
        if farm:
            self.db.delete(farm)
            self.db.commit()
            return True
        return False
