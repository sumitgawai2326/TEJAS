"""
Tests for Soil Sensor Hardware Abstraction Layer & Zero Hardware Hallucination.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.hardware.soil_sensor.mock_sensor import MockSoilSensor
from app.hardware.soil_sensor.modbus_sensor import ModbusSoilSensor
from app.hardware.soil_sensor import get_soil_sensor
from app.core.config import settings

def test_mock_soil_sensor_in_demo_mode():
    """Verify MockSoilSensor produces isolated simulated data with is_mock=True."""
    mock = MockSoilSensor()
    assert mock.is_connected() is True
    status = mock.get_status()
    assert status["is_mock"] is True
    assert status["mode"] == "DEMO_SIMULATION"
    
    reading = mock.read()
    assert reading.is_mock is True
    assert reading.connected is True
    assert reading.status == "DEMO_SIMULATION"
    assert reading.nitrogen is not None
    assert reading.phosphorus is not None
    assert reading.potassium is not None
    assert reading.ph is not None
    assert reading.moisture is not None
    assert reading.temperature is not None

def test_mock_soil_sensor_disconnect():
    """Verify MockSoilSensor handles manual disconnection."""
    mock = MockSoilSensor()
    mock.disconnect()
    assert mock.is_connected() is False
    reading = mock.read()
    assert reading.connected is False
    assert reading.nitrogen is None
    assert reading.status == "SENSOR DISCONNECTED"

def test_modbus_sensor_unconfigured_map():
    """
    CRITICAL: Verify unconfigured YAML register map returns UNCONFIGURED_REGISTER_MAP
    and NEVER invents sensor values.
    """
    modbus = ModbusSoilSensor(
        port="COM3",
        config_file="hardware/sensor_protocol/soil_sensor.yaml"
    )
    assert modbus.is_connected() is False
    status = modbus.get_status()
    assert status["status"] == "UNCONFIGURED_REGISTER_MAP"
    assert status["is_mock"] is False
    
    reading = modbus.read()
    assert reading.connected is False
    assert reading.status == "UNCONFIGURED_REGISTER_MAP"
    assert reading.is_mock is False
    # All 6 values MUST be None
    assert reading.nitrogen is None
    assert reading.phosphorus is None
    assert reading.potassium is None
    assert reading.ph is None
    assert reading.moisture is None
    assert reading.temperature is None

def test_modbus_sensor_absent_port_zero_hallucination():
    """
    CRITICAL: Verify disconnected hardware port returns SENSOR DISCONNECTED
    and all 6 values remain strictly None.
    """
    modbus = ModbusSoilSensor(
        port="COM999_NON_EXISTENT",
        config_file="hardware/sensor_protocol/soil_sensor.yaml"
    )
    reading = modbus.read()
    assert reading.connected is False
    assert reading.is_mock is False
    assert reading.nitrogen is None
    assert reading.phosphorus is None
    assert reading.potassium is None
    assert reading.ph is None
    assert reading.moisture is None
    assert reading.temperature is None
    assert reading.error_message is not None

def test_soil_sensor_factory_mode_switching():
    """Verify get_soil_sensor() respects settings.DEMO_MODE."""
    orig = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = True
        sensor_demo = get_soil_sensor()
        assert isinstance(sensor_demo, MockSoilSensor)
        
        settings.DEMO_MODE = False
        sensor_real = get_soil_sensor()
        assert isinstance(sensor_real, ModbusSoilSensor)
    finally:
        settings.DEMO_MODE = orig
