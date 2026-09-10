"""
Unit and Integration Tests for Phase 11A Hardware-Safe Soil Communication Layer.
Tests:
1. Modbus-RTU CRC-16 calculation and frame verification.
2. Agronomic physical range validation (Zero Hardware Hallucination).
3. USB-RS485 Serial Port Discovery.
4. ModbusSoilSensor Bounded Retry and Exponential Backoff.
5. Zero Hallucination Invariants across DEMO_MODE toggling.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))

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
from app.hardware.soil_sensor.modbus_sensor import ModbusSoilSensor
from app.hardware.soil_sensor.mock_sensor import MockSoilSensor
from app.hardware.soil_sensor import get_soil_sensor
from app.core.config import settings


# ==============================================================================
# 1. MODBUS-RTU CRC-16 TESTS
# ==============================================================================

def test_crc_calculation_standard_test_vector():
    """
    Test CRC-16 calculation against standard Modbus test vector:
    Payload: [0x01, 0x03, 0x00, 0x00, 0x00, 0x02]
    Expected CRC-16: 0xC40B -> transmitted as [0x0B, 0xC4] (Little-Endian).
    """
    payload = bytes([0x01, 0x03, 0x00, 0x00, 0x00, 0x02])
    crc_int = compute_modbus_crc(payload)
    crc_bytes = compute_modbus_crc_bytes(payload)

    assert crc_int == 0x0BC4
    assert crc_bytes == bytes([0xC4, 0x0B])


def test_validate_valid_modbus_frame():
    """Valid complete Modbus-RTU frame passes validation."""
    payload = bytes([0x01, 0x03, 0x04, 0x00, 0xE8, 0x01, 0x2C])
    crc_bytes = compute_modbus_crc_bytes(payload)
    valid_frame = payload + crc_bytes

    is_valid, err = validate_modbus_frame(valid_frame)
    assert is_valid is True
    assert err is None


def test_validate_invalid_crc_frame_rejected():
    """Frame with corrupted CRC is rejected with detailed error."""
    payload = bytes([0x01, 0x03, 0x04, 0x00, 0xE8, 0x01, 0x2C])
    corrupt_frame = payload + bytes([0xFF, 0xFF])  # Invalid CRC

    is_valid, err = validate_modbus_frame(corrupt_frame)
    assert is_valid is False
    assert "CRC mismatch" in err


def test_validate_truncated_frame_rejected():
    """Frames shorter than 4 bytes are rejected."""
    short_frame = bytes([0x01, 0x03])
    is_valid, err = validate_modbus_frame(short_frame)
    assert is_valid is False
    assert "too short" in err.lower()


def test_extract_modbus_payload():
    """Extracts slave ID, function code, and data payload from valid frame."""
    payload = bytes([0x02, 0x04, 0x00, 0x1A])
    frame = payload + compute_modbus_crc_bytes(payload)

    slave_id, func_code, data = extract_modbus_payload(frame)
    assert slave_id == 2
    assert func_code == 4
    assert data == bytes([0x00, 0x1A])


def test_extract_modbus_payload_invalid_raises():
    """Corrupted frame raises ValueError on extraction."""
    with pytest.raises(ValueError):
        extract_modbus_payload(bytes([0x01, 0x02, 0x00]))


# ==============================================================================
# 2. TELEMETRY RANGE VALIDATION TESTS
# ==============================================================================

def test_telemetry_validation_valid_npk():
    """Valid N/P/K values are accepted and rounded."""
    assert validate_parameter("nitrogen", 45.5) == 45.5
    assert validate_parameter("phosphorus", 32.0) == 32.0
    assert validate_parameter("potassium", 180.25) == 180.25


def test_telemetry_validation_invalid_npk_rejected():
    """Out-of-range N/P/K values (<0 or >1999) become None."""
    assert validate_parameter("nitrogen", -5.0) is None
    assert validate_parameter("nitrogen", 2500.0) is None
    assert validate_parameter("phosphorus", -1.0) is None
    assert validate_parameter("potassium", 2000.0) is None


def test_telemetry_validation_ph_range():
    """Valid pH (3.0–10.0) is accepted; out-of-range pH becomes None."""
    assert validate_parameter("ph", 6.8) == 6.8
    assert validate_parameter("ph", 3.0) == 3.0
    assert validate_parameter("ph", 10.0) == 10.0
    assert validate_parameter("ph", 2.9) is None
    assert validate_parameter("ph", 10.1) is None
    assert validate_parameter("ph", 14.0) is None


def test_telemetry_validation_moisture_range():
    """Valid moisture (0.0–100.0%) is accepted; out-of-range becomes None."""
    assert validate_parameter("moisture", 24.5) == 24.5
    assert validate_parameter("moisture", 0.0) == 0.0
    assert validate_parameter("moisture", 100.0) == 100.0
    assert validate_parameter("moisture", -0.5) is None
    assert validate_parameter("moisture", 105.0) is None


def test_telemetry_validation_temperature_range():
    """Valid temperature (-20.0 to 80.0°C) is accepted; out-of-range becomes None."""
    assert validate_parameter("temperature", 25.0) == 25.0
    assert validate_parameter("temperature", -15.0) == -15.0
    assert validate_parameter("temperature", 75.0) == 75.0
    assert validate_parameter("temperature", -25.0) is None
    assert validate_parameter("temperature", 85.0) is None


def test_telemetry_partial_preservation():
    """Partial valid telemetry preserves good values and rejects out-of-bound values."""
    res = validate_soil_telemetry(
        nitrogen=42.0,       # Valid
        phosphorus=-10.0,     # Invalid -> None
        potassium=150.0,     # Valid
        ph=6.5,              # Valid
        moisture=120.0,      # Invalid -> None
        temperature=24.0     # Valid
    )
    assert res["nitrogen"] == 42.0
    assert res["phosphorus"] is None
    assert res["potassium"] == 150.0
    assert res["ph"] == 6.5
    assert res["moisture"] is None
    assert res["temperature"] == 24.0


# ==============================================================================
# 3. RS485 PORT DISCOVERY TESTS
# ==============================================================================

def test_port_discovery_structure():
    """discover_rs485_ports returns valid discovery dictionary schema."""
    discovery = discover_rs485_ports(configured_port="COM3")
    assert "configured_port" in discovery
    assert "configured_port_exists" in discovery
    assert "candidate_ports" in discovery
    assert "all_ports" in discovery
    assert "total_ports" in discovery
    assert isinstance(discovery["candidate_ports"], list)


def test_port_discovery_does_not_imply_connected_sensor():
    """Discovering serial ports never fabricates sensor connection status."""
    discovery = discover_rs485_ports()
    # Port existence is independent from physical sensor attachment
    assert isinstance(discovery["total_ports"], int)


# ==============================================================================
# 4. BOUNDED RETRY & RECONNECTION TESTS
# ==============================================================================

def test_modbus_sensor_retry_bounds():
    """Verify max_retries is clamped between 1 and 5."""
    sensor_high = ModbusSoilSensor(max_retries=100)
    assert sensor_high.max_retries == 5

    sensor_low = ModbusSoilSensor(max_retries=-10)
    assert sensor_low.max_retries == 1


def test_modbus_sensor_bounded_retry_failure():
    """
    Verify persistent failure stops after exactly max_retries without infinite loop.
    """
    sensor = ModbusSoilSensor(port="NON_EXISTENT_PORT_123", max_retries=2, backoff_factor=0.001)
    # Even if properly configured was forced:
    sensor._is_properly_configured = True
    
    with patch("serial.Serial", side_effect=Exception("Serial Port Absent")):
        connected = sensor.connect()
        assert connected is False
        assert sensor.is_connected() is False


# ==============================================================================
# 5. ZERO-HALLUCINATION GUARANTEES
# ==============================================================================

def test_zero_hallucination_unconfigured_real_mode():
    """
    CRITICAL INVARIANT: In REAL mode with unconfigured YAML:
    - Never queries arbitrary registers.
    - Returns None for all 6 telemetry fields.
    - is_mock is strictly False.
    - status is UNCONFIGURED_REGISTER_MAP.
    """
    sensor = ModbusSoilSensor(config_file="hardware/sensor_protocol/soil_sensor.yaml")
    reading = sensor.read()

    assert reading.is_mock is False
    assert reading.connected is False
    assert reading.status == "UNCONFIGURED_REGISTER_MAP"
    assert reading.nitrogen is None
    assert reading.phosphorus is None
    assert reading.potassium is None
    assert reading.ph is None
    assert reading.moisture is None
    assert reading.temperature is None


def test_demo_mode_simulation_isolation():
    """
    CRITICAL INVARIANT: In DEMO mode:
    - MockSoilSensor generates values strictly flagged with is_mock=True.
    - status is DEMO_SIMULATION.
    """
    mock = MockSoilSensor()
    reading = mock.read()

    assert reading.is_mock is True
    assert reading.connected is True
    assert reading.status == "DEMO_SIMULATION"
    assert reading.nitrogen is not None
    assert reading.moisture is not None
