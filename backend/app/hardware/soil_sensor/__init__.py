"""
Soil Sensor Factory Selector.
"""
from app.hardware.soil_sensor.base import BaseSoilSensor
from app.hardware.soil_sensor.mock_sensor import MockSoilSensor
from app.hardware.soil_sensor.modbus_sensor import ModbusSoilSensor
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
