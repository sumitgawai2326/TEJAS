"""
Pydantic Schemas for Camera Telemetry & Hardware Status.
"""
from typing import Optional, Dict, Any
import datetime
from pydantic import BaseModel, Field

class CameraStatus(BaseModel):
    driver: str = Field(..., description="CameraHAL or MockCamera")
    mode: str = Field(..., description="REAL_HARDWARE or DEMO_SIMULATION")
    available: bool = Field(..., description="True if video stream / capture device is opened and ready")
    status: str = Field(..., description="READY, CONNECTED, CAMERA_UNAVAILABLE, CAMERA DISCONNECTED, SIMULATED")
    is_mock: bool
    camera_device_index: int
    resolution: Optional[str] = None
    fps: Optional[int] = None
    details: Optional[str] = None
    last_check: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
