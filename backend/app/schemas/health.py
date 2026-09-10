"""
Pydantic Schemas for System & Hardware Health Diagnostics.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import datetime

class SubsystemStatus(BaseModel):
    status: str = Field(..., description="READY, CONNECTED, SENSOR DISCONNECTED, CAMERA_UNAVAILABLE, UNCONFIGURED_REGISTER_MAP, ERROR, SIMULATED")
    details: Optional[str] = None
    last_check: str
    is_mock: bool = False

class PlatformInfo(BaseModel):
    board_model: str
    is_raspberry_pi: bool
    rpi_version: Optional[str] = None
    os_name: str
    os_release: str
    os_version: str
    architecture: str
    python_version: str
    hostname: str

class DeviceStatus(BaseModel):
    status: str = Field(..., description="Overall Status: OK, WARNING, ERROR")
    app_version: str
    app_name: str
    demo_mode: bool
    mode_label: str = Field(..., description="OFFLINE EDGE AI or DEMO SIMULATION")
    ai_status_label: str = Field(..., description="HAILO ACCELERATED or CPU FALLBACK")
    soil_status_label: str = Field(..., description="CONNECTED, SENSOR DISCONNECTED, UNCONFIGURED_REGISTER_MAP, or DEMO SIMULATION")
    camera_status_label: str = Field(..., description="READY, CAMERA_UNAVAILABLE, or SIMULATED")
    uptime_seconds: float
    cpu_temperature_celsius: Optional[float] = None
    cpu_usage_percent: float
    ram_usage_percent: float
    ram_available_mb: float
    storage_usage_percent: float
    storage_free_gb: float
    battery: Dict[str, Any]
    subsystems: Dict[str, SubsystemStatus]
    platform: Optional[PlatformInfo] = None
    serial_ports: Optional[List[Dict[str, Any]]] = None

class DeviceCapabilities(BaseModel):
    project_name: str
    version: str
    camera_available: bool
    soil_sensor_available: bool
    soil_sensor_register_configured: bool
    ai_accelerator_available: bool
    ai_accelerator_type: str
    ai_inference_mode: str
    ai_status_label: str
    offline_capable: bool
    demo_mode: bool
    supported_crops: List[str]
    supported_languages: List[str]
    soil_sensor_parameters: List[str]
    platform_info: Optional[PlatformInfo] = None

class SelfTestItem(BaseModel):
    subsystem: str
    status: str = Field(..., description="PASSED, WARNING, FAILED")
    critical: bool = True
    message: str
    details: Optional[str] = None
    latency_ms: Optional[float] = None

class SelfTestResponse(BaseModel):
    overall_status: str = Field(..., description="DEVICE READY, DEVICE READY WITH WARNINGS, DEVICE INITIALIZATION FAILED")
    passed_count: int
    warning_count: int
    failed_count: int
    items: List[SelfTestItem]
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    demo_mode: bool

class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    demo_mode: bool
    ai_mode: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
