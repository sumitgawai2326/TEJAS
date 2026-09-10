import os

base_schemas = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app\schemas"

# 1. schemas/common.py
common_code = """\"\"\"
Common Schemas & Standard Error Definitions.
\"\"\"
from typing import Optional
import datetime
from pydantic import BaseModel, Field
from app.core.errors import ErrorCode

class ErrorResponse(BaseModel):
    code: ErrorCode = Field(..., description="Standardized error code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[str] = Field(None, description="Detailed diagnostic or troubleshooting advice")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
"""

with open(os.path.join(base_schemas, "common.py"), "w", encoding="utf-8") as f:
    f.write(common_code)

# 2. schemas/soil.py
soil_code = """\"\"\"
Pydantic Schemas for 6-Parameter Soil Sensor Telemetry & Diagnostics.
\"\"\"
from typing import Optional, Dict, Any
import datetime
from pydantic import BaseModel, Field

class SoilTelemetry(BaseModel):
    # ZERO HARDWARE HALLUCINATION: float | None (strictly None when unavailable)
    nitrogen: Optional[float] = Field(None, description="Available Soil Nitrogen (N) in mg/kg")
    phosphorus: Optional[float] = Field(None, description="Available Soil Phosphorus (P) in mg/kg")
    potassium: Optional[float] = Field(None, description="Available Soil Potassium (K) in mg/kg")
    ph: Optional[float] = Field(None, description="Soil pH level (0-14)")
    moisture: Optional[float] = Field(None, description="Volumetric Soil Moisture in %")
    temperature: Optional[float] = Field(None, description="Soil Temperature in °C")

    connected: bool = Field(..., description="True if sensor is physically connected and responding")
    status: str = Field(..., description="CONNECTED, SENSOR DISCONNECTED, UNCONFIGURED_REGISTER_MAP, DEMO_SIMULATION, ERROR")
    error_message: Optional[str] = Field(None, description="Diagnostic error details if disconnected or failing")
    is_mock: bool = Field(False, description="Strict marker distinguishing real hardware data from demo/simulated data")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
    raw_response_hex: Optional[str] = Field(None, description="Raw Modbus hex payload for debugging")

class SensorStatus(BaseModel):
    driver: str = Field(..., description="ModbusSoilSensor or MockSoilSensor")
    mode: str = Field(..., description="REAL_HARDWARE or DEMO_SIMULATION")
    connected: bool
    status: str = Field(..., description="CONNECTED, SENSOR DISCONNECTED, UNCONFIGURED_REGISTER_MAP, DEMO_SIMULATION")
    is_mock: bool
    port: Optional[str] = None
    baudrate: Optional[int] = None
    details: Optional[str] = None
    last_health_check: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
"""

with open(os.path.join(base_schemas, "soil.py"), "w", encoding="utf-8") as f:
    f.write(soil_code)

# 3. schemas/camera.py
camera_code = """\"\"\"
Pydantic Schemas for Camera Telemetry & Hardware Status.
\"\"\"
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
"""

with open(os.path.join(base_schemas, "camera.py"), "w", encoding="utf-8") as f:
    f.write(camera_code)

# 4. schemas/ai.py
ai_code = """\"\"\"
Pydantic Schemas for AI Engine Status & Confidence-Gated Predictions.
\"\"\"
from typing import Optional, List, Dict, Any
import datetime
from pydantic import BaseModel, Field

class AIStatus(BaseModel):
    ready: bool = Field(..., description="True if model is loaded and ready for inference")
    status: str = Field(..., description="READY, AI_NOT_READY, ACCELERATED, CPU_FALLBACK, DEMO_PLACEHOLDER")
    accelerator_type: str = Field(..., description="HAILO-8 or CPU")
    inference_mode: str = Field(..., description="HAILO ACCELERATED or CPU FALLBACK")
    model_name: str
    model_version: str
    is_demo_model: bool = Field(True, description="Marker for prototype demo placeholder model")
    confidence_threshold: float
    supported_classes: List[str]
    details: Optional[str] = None
    last_check: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())

class PredictionResult(BaseModel):
    prediction: str = Field(..., description="Diagnosis label (or 'Unknown / Low Confidence')")
    confidence: float = Field(..., description="Model confidence score (0.0 to 1.0)")
    model_name: str
    model_version: str
    inference_time_ms: float = Field(..., description="Measured inference time in milliseconds")
    inference_device: str = Field(..., description="HAILO or CPU")
    status: str = Field(..., description="CONFIDENT or LOW_CONFIDENCE")
    is_low_confidence: bool = Field(..., description="True if confidence is below configured threshold")
    crop: str = "General"
    severity: str = "Unknown"
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
"""

with open(os.path.join(base_schemas, "ai.py"), "w", encoding="utf-8") as f:
    f.write(ai_code)

# 5. schemas/health.py
health_code = """\"\"\"
Pydantic Schemas for System & Hardware Health Diagnostics.
\"\"\"
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
import datetime

class SubsystemStatus(BaseModel):
    status: str = Field(..., description="READY, CONNECTED, SENSOR DISCONNECTED, CAMERA_UNAVAILABLE, UNCONFIGURED_REGISTER_MAP, ERROR, SIMULATED")
    details: Optional[str] = None
    last_check: str
    is_mock: bool = False

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

class HealthResponse(BaseModel):
    status: str
    project: str
    version: str
    demo_mode: bool
    ai_mode: str
    timestamp: str = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat())
"""

with open(os.path.join(base_schemas, "health.py"), "w", encoding="utf-8") as f:
    f.write(health_code)

# 6. schemas/__init__.py
init_code = """from app.schemas.common import ErrorResponse
from app.schemas.health import DeviceStatus, DeviceCapabilities, SubsystemStatus, HealthResponse
from app.schemas.soil import SoilTelemetry, SensorStatus
from app.schemas.camera import CameraStatus
from app.schemas.ai import AIStatus, PredictionResult

__all__ = [
    "ErrorResponse",
    "DeviceStatus",
    "DeviceCapabilities",
    "SubsystemStatus",
    "HealthResponse",
    "SoilTelemetry",
    "SensorStatus",
    "CameraStatus",
    "AIStatus",
    "PredictionResult"
]
"""

with open(os.path.join(base_schemas, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(init_code)

print("Pydantic Schemas updated successfully.")
