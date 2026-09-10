"""
Abstract Base Hardware Interface for 6-Parameter Soil Sensor.
Parameters: Nitrogen (N), Phosphorus (P), Potassium (K), pH, Moisture, Temperature.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.schemas.soil import SoilTelemetry

class BaseSoilSensor(ABC):
    """Abstract Base Class for 6-Parameter Soil Sensor Hardware Drivers."""

    @abstractmethod
    def connect(self) -> bool:
        """Establish connection with physical RS485 interface or initialize mock engine."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close physical serial port and release resources."""
        pass

    @abstractmethod
    def is_connected(self) -> bool:
        """Check live connection state."""
        pass

    @abstractmethod
    def read(self) -> SoilTelemetry:
        """
        Read 6 soil parameters (N, P, K, pH, Moisture, Temp).
        Zero Hardware Hallucination: strictly return None if disconnected or unconfigured.
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Execute quick hardware link diagnostics without taking full reading."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return diagnostic status of the sensor interface."""
        pass
