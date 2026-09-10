"""
Mock Soil Sensor Driver for Safe Demo & Presentation Testing (DEMO_MODE=true).
Outputs are explicitly flagged with is_mock=True.
"""
import random
from typing import Dict, Any
from app.hardware.soil_sensor.base import BaseSoilSensor
from app.schemas.soil import SoilTelemetry

class MockSoilSensor(BaseSoilSensor):
    def __init__(self):
        self._connected = True

    def connect(self) -> bool:
        self._connected = True
        return True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def read(self) -> SoilTelemetry:
        """Produces realistic simulated agricultural soil metrics for demo presentations."""
        if not self._connected:
            return SoilTelemetry(
                nitrogen=None,
                phosphorus=None,
                potassium=None,
                ph=None,
                moisture=None,
                temperature=None,
                connected=False,
                status="SENSOR DISCONNECTED",
                error_message="Mock sensor manually disconnected",
                is_mock=True
            )

        return SoilTelemetry(
            nitrogen=round(random.uniform(42.0, 58.0), 1),
            phosphorus=round(random.uniform(28.0, 36.0), 1),
            potassium=round(random.uniform(55.0, 72.0), 1),
            ph=round(random.uniform(6.2, 6.8), 2),
            moisture=round(random.uniform(22.0, 26.5), 1),
            temperature=round(random.uniform(24.0, 27.5), 1),
            connected=True,
            status="DEMO_SIMULATION",
            error_message=None,
            is_mock=True
        )

    def health_check(self) -> Dict[str, Any]:
        return {
            "healthy": self._connected,
            "status": "SIMULATED" if self._connected else "DISCONNECTED",
            "driver": "MockSoilSensor",
            "is_mock": True
        }

    def get_status(self) -> Dict[str, Any]:
        return {
            "driver": "MockSoilSensor",
            "mode": "DEMO_SIMULATION",
            "connected": self._connected,
            "status": "DEMO_SIMULATION" if self._connected else "SENSOR DISCONNECTED",
            "is_mock": True,
            "port": "MOCK_PORT",
            "baudrate": 4800,
            "details": "Simulated 6-parameter telemetry for SIH demo testing"
        }
