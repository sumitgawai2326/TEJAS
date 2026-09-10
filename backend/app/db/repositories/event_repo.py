"""
Repository for System & Hardware Device Events (Watchdog / Diagnostic log).
"""
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
