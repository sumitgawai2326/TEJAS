"""
Aggregated Field History Repository for Timeline Generation.
Combines chronologically sorted Scans, Soil Readings, Risk Assessments, and Advisories.
"""
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
