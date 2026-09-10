import os

base_repo = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app\db\repositories"

# 1. farm_repo.py
farm_code = """\"\"\"
Repository for Farm Entities.
\"\"\"
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
"""

with open(os.path.join(base_repo, "farm_repo.py"), "w", encoding="utf-8") as f:
    f.write(farm_code)

# 2. field_repo.py
field_code = """\"\"\"
Repository for Field Entities.
\"\"\"
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
"""

with open(os.path.join(base_repo, "field_repo.py"), "w", encoding="utf-8") as f:
    f.write(field_code)

# 3. crop_repo.py
crop_code = """\"\"\"
Repository for Crop Entities.
\"\"\"
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
"""

with open(os.path.join(base_repo, "crop_repo.py"), "w", encoding="utf-8") as f:
    f.write(crop_code)

# 4. scan_repo.py
scan_code = """\"\"\"
Repository for Crop Scan & AI Pathology Records.
\"\"\"
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
"""

with open(os.path.join(base_repo, "scan_repo.py"), "w", encoding="utf-8") as f:
    f.write(scan_code)

# 5. soil_repo.py
soil_code = """\"\"\"
Repository for Soil Intelligence Telemetry.
Zero Hardware Hallucination: Strict storage of nullable values.
\"\"\"
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
"""

with open(os.path.join(base_repo, "soil_repo.py"), "w", encoding="utf-8") as f:
    f.write(soil_code)

# 6. risk_repo.py
risk_code = """\"\"\"
Repository for Risk Assessment Records.
\"\"\"
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
"""

with open(os.path.join(base_repo, "risk_repo.py"), "w", encoding="utf-8") as f:
    f.write(risk_code)

# 7. advisory_repo.py
advisory_code = """\"\"\"
Repository for Agronomic Advisory Records.
\"\"\"
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
"""

with open(os.path.join(base_repo, "advisory_repo.py"), "w", encoding="utf-8") as f:
    f.write(advisory_code)

# 8. event_repo.py
event_code = """\"\"\"
Repository for System & Hardware Device Events (Watchdog / Diagnostic log).
\"\"\"
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db.models import DeviceEvent

class DeviceEventRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        subsystem: str,
        event_type: str,
        message: str,
        severity: str = "INFO",
        details: Optional[str] = None
    ) -> DeviceEvent:
        event = DeviceEvent(
            subsystem=subsystem,
            event_type=event_type,
            message=message,
            severity=severity,
            details=details
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def list_events(self, subsystem: Optional[str] = None, limit: int = 100) -> List[DeviceEvent]:
        q = self.db.query(DeviceEvent)
        if subsystem:
            q = q.filter(DeviceEvent.subsystem == subsystem)
        return q.order_by(DeviceEvent.timestamp.desc()).limit(limit).all()
"""

with open(os.path.join(base_repo, "event_repo.py"), "w", encoding="utf-8") as f:
    f.write(event_code)

# 9. history_repo.py
history_code = """\"\"\"
Aggregated Field History Repository for Timeline Generation.
Combines chronologically sorted Scans, Soil Readings, Risk Assessments, and Advisories.
\"\"\"
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.db.models import Field, Scan, SoilReading, RiskAssessment, Advisory

class FieldHistoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_field_timeline(self, field_id: int, limit: int = 50) -> Dict[str, Any]:
        field = self.db.query(Field).filter(Field.id == field_id).first()
        if not field:
            return {"error": "Field not found", "field_id": field_id}

        scans = self.db.query(Scan).filter(Scan.field_id == field_id).order_by(Scan.timestamp.desc()).limit(limit).all()
        soil_readings = self.db.query(SoilReading).filter(SoilReading.field_id == field_id).order_by(SoilReading.timestamp.desc()).limit(limit).all()
        risk_assessments = self.db.query(RiskAssessment).filter(RiskAssessment.field_id == field_id).order_by(RiskAssessment.timestamp.desc()).limit(limit).all()
        advisories = self.db.query(Advisory).filter(Advisory.field_id == field_id).order_by(Advisory.timestamp.desc()).limit(limit).all()

        timeline_entries = []

        for s in scans:
            timeline_entries.append({
                "type": "SCAN",
                "timestamp": s.timestamp,
                "id": s.id,
                "prediction": s.prediction,
                "confidence": s.confidence,
                "status": s.status,
                "image_path": s.image_path
            })

        for r in soil_readings:
            timeline_entries.append({
                "type": "SOIL_READING",
                "timestamp": r.timestamp,
                "id": r.id,
                "nitrogen": r.nitrogen,
                "phosphorus": r.phosphorus,
                "potassium": r.potassium,
                "ph": r.ph,
                "moisture": r.moisture,
                "temperature": r.temperature,
                "sensor_status": r.sensor_status,
                "is_mock": r.is_mock
            })

        for rk in risk_assessments:
            timeline_entries.append({
                "type": "RISK_ASSESSMENT",
                "timestamp": rk.timestamp,
                "id": rk.id,
                "field_health_score": rk.field_health_score,
                "disease_risk": rk.disease_risk,
                "pest_risk": rk.pest_risk,
                "soil_stress": rk.soil_stress,
                "water_stress": rk.water_stress
            })

        for a in advisories:
            timeline_entries.append({
                "type": "ADVISORY",
                "timestamp": a.timestamp,
                "id": a.id,
                "title": a.title,
                "message": a.message,
                "severity": a.severity,
                "category": a.category,
                "language": a.language
            })

        # Sort combined timeline chronologically descending
        timeline_entries.sort(key=lambda x: x["timestamp"], reverse=True)

        return {
            "field_id": field.id,
            "field_name": field.name,
            "area": field.area,
            "area_unit": field.area_unit,
            "soil_type": field.soil_type,
            "total_timeline_entries": len(timeline_entries),
            "timeline": timeline_entries[:limit],
            "scans_count": len(scans),
            "soil_readings_count": len(soil_readings),
            "risk_assessments_count": len(risk_assessments),
            "advisories_count": len(advisories)
        }
"""

with open(os.path.join(base_repo, "history_repo.py"), "w", encoding="utf-8") as f:
    f.write(history_code)

# 10. __init__.py
init_code = """from app.db.repositories.farm_repo import FarmRepository
from app.db.repositories.field_repo import FieldRepository
from app.db.repositories.crop_repo import CropRepository
from app.db.repositories.scan_repo import ScanRepository
from app.db.repositories.soil_repo import SoilReadingRepository
from app.db.repositories.risk_repo import RiskAssessmentRepository
from app.db.repositories.advisory_repo import AdvisoryRepository
from app.db.repositories.event_repo import DeviceEventRepository
from app.db.repositories.history_repo import FieldHistoryRepository

__all__ = [
    "FarmRepository",
    "FieldRepository",
    "CropRepository",
    "ScanRepository",
    "SoilReadingRepository",
    "RiskAssessmentRepository",
    "AdvisoryRepository",
    "DeviceEventRepository",
    "FieldHistoryRepository"
]
"""

with open(os.path.join(base_repo, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(init_code)

print("Repositories created successfully.")
