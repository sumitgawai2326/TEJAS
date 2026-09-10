"""
Pydantic Schemas for 6-Parameter Soil Sensor Telemetry & Diagnostics.
"""
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
