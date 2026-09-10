"""
Soil Sensor Factory Selector and Hardware Subsystem Exports.
"""
from app.hardware.soil_sensor.base import BaseSoilSensor
from app.hardware.soil_sensor.mock_sensor import MockSoilSensor
from app.hardware.soil_sensor.modbus_sensor import ModbusSoilSensor
from app.hardware.soil_sensor.modbus_decoder import (
    compute_modbus_crc,
    compute_modbus_crc_bytes,
    validate_modbus_frame,
    extract_modbus_payload,
    validate_parameter,
    validate_soil_telemetry,
    TELEMETRY_RANGES
)
from app.hardware.soil_sensor.port_discovery import discover_rs485_ports
from app.core.config import settings

def get_soil_sensor() -> BaseSoilSensor:
    if settings.DEMO_MODE:
        return MockSoilSensor()
    return ModbusSoilSensor(
        port=settings.SOIL_SENSOR_PORT,
        baudrate=settings.SOIL_SENSOR_BAUDRATE,
        slave_id=settings.SOIL_SENSOR_SLAVE_ID,
        config_file=settings.SOIL_SENSOR_CONFIG,
        timeout=settings.SOIL_SENSOR_TIMEOUT
    )

__all__ = [
    "BaseSoilSensor",
    "MockSoilSensor",
    "ModbusSoilSensor",
    "get_soil_sensor",
    "compute_modbus_crc",
    "compute_modbus_crc_bytes",
    "validate_modbus_frame",
    "extract_modbus_payload",
    "validate_parameter",
    "validate_soil_telemetry",
    "TELEMETRY_RANGES",
    "discover_rs485_ports"
]
