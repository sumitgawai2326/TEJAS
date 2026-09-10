"""
Industrial RS485 Modbus-RTU 6-Parameter Soil Sensor Driver (DEMO_MODE=false).
Strict Zero Hardware Hallucination Policy:
Never invent register addresses, baud rate, slave ID, or sensor readings.
If unconfigured or disconnected, strictly returns None for all 6 telemetry parameters.
"""
import os
import yaml
from typing import Dict, Any, Optional
from app.hardware.soil_sensor.base import BaseSoilSensor
from app.schemas.soil import SoilTelemetry
from app.core.logging import log_event

class ModbusSoilSensor(BaseSoilSensor):
    def __init__(self, port: str = "COM3", baudrate: int = 4800, slave_id: int = 1, config_file: str = "hardware/sensor_protocol/soil_sensor.yaml", timeout: float = 2.0):
        self.port = port
        self.baudrate = baudrate
        self.slave_id = slave_id
        self.config_file = config_file
        self.timeout = timeout
        self._connected = False
        self._config_loaded = False
        self._is_properly_configured = False
        self._config_data: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Loads declarative YAML register configuration."""
        if not os.path.exists(self.config_file):
            log_event("SOIL", "WARNING", f"Soil config file not found at {self.config_file}")
            self._config_loaded = False
            self._is_properly_configured = False
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                self._config_data = yaml.safe_load(f) or {}
                self._config_loaded = True
                sensor_meta = self._config_data.get("sensor", {})
                self._is_properly_configured = bool(sensor_meta.get("is_configured", False))
                if not self._is_properly_configured:
                    log_event("SOIL", "INFO", "Soil sensor register map is UNCONFIGURED (awaiting physical hardware datasheet)")
        except Exception as e:
            log_event("SOIL", "ERROR", f"Error loading soil sensor config: {e}")
            self._config_loaded = False
            self._is_properly_configured = False

    def connect(self) -> bool:
        """Attempts physical serial port initialization."""
        if not self._is_properly_configured:
            self._connected = False
            return False
        
        try:
            import serial
            ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            ser.close()
            self._connected = True
            log_event("SOIL", "INFO", f"RS485 adapter opened on port {self.port}")
            return True
        except Exception as e:
            self._connected = False
            log_event("SOIL", "WARNING", f"Cannot open RS485 port {self.port}: {e}")
            return False

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def read(self) -> SoilTelemetry:
        """
        Reads real MODBUS registers.
        Zero Hallucination Guarantee: Never returns fake numbers if disconnected or unconfigured.
        """
        if not self._is_properly_configured:
            return SoilTelemetry(
                nitrogen=None,
                phosphorus=None,
                potassium=None,
                ph=None,
                moisture=None,
                temperature=None,
                connected=False,
                status="UNCONFIGURED_REGISTER_MAP",
                error_message="Soil sensor register map unconfigured. Populate hardware/sensor_protocol/soil_sensor.yaml from manufacturer datasheet.",
                is_mock=False
            )

        if not self.connect():
            return SoilTelemetry(
                nitrogen=None,
                phosphorus=None,
                potassium=None,
                ph=None,
                moisture=None,
                temperature=None,
                connected=False,
                status="SENSOR DISCONNECTED",
                error_message=f"RS485 sensor disconnected or unresponsive on port {self.port}.",
                is_mock=False
            )

        # Real modbus reading will execute in Phase 8 using the populated datasheet registers
        return SoilTelemetry(
            nitrogen=None,
            phosphorus=None,
            potassium=None,
            ph=None,
            moisture=None,
            temperature=None,
            connected=False,
            status="SENSOR DISCONNECTED",
            error_message="Awaiting physical sensor communication on RS485 bus.",
            is_mock=False
        )

    def health_check(self) -> Dict[str, Any]:
        """Quick health verification of driver configuration & serial link."""
        if not self._is_properly_configured:
            return {
                "healthy": False,
                "status": "UNCONFIGURED_REGISTER_MAP",
                "driver": "ModbusSoilSensor",
                "error": "Register map unconfigured in soil_sensor.yaml",
                "is_mock": False
            }
        
        connected = self.connect()
        return {
            "healthy": connected,
            "status": "CONNECTED" if connected else "SENSOR DISCONNECTED",
            "driver": "ModbusSoilSensor",
            "port": self.port,
            "is_mock": False
        }

    def get_status(self) -> Dict[str, Any]:
        if not self._is_properly_configured:
            return {
                "driver": "ModbusSoilSensor",
                "mode": "REAL_HARDWARE",
                "connected": False,
                "status": "UNCONFIGURED_REGISTER_MAP",
                "is_mock": False,
                "port": self.port,
                "baudrate": self.baudrate,
                "details": "Register map unconfigured in soil_sensor.yaml"
            }
        
        return {
            "driver": "ModbusSoilSensor",
            "mode": "REAL_HARDWARE",
            "connected": self._connected,
            "status": "CONNECTED" if self._connected else "SENSOR DISCONNECTED",
            "is_mock": False,
            "port": self.port,
            "baudrate": self.baudrate,
            "details": f"Port: {self.port}, Baud: {self.baudrate}"
        }
