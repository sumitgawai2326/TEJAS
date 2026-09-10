"""
Generic Modbus-RTU Frame Decoder and Telemetry Validator for TEJAS.

Provides:
1. Deterministic Modbus CRC-16 calculation and frame verification.
2. Safe frame parsing with payload extraction.
3. Agronomic telemetry range validation (Zero Hardware Hallucination).

Independent of specific physical sensor models.
"""

from typing import Tuple, Optional, Dict, Any, Union
from app.core.logging import log_event


# Agronomic Physical Range Boundaries for 6-Parameter Soil Probes
TELEMETRY_RANGES: Dict[str, Tuple[float, float, str]] = {
    "nitrogen": (0.0, 1999.0, "mg/kg"),
    "phosphorus": (0.0, 1999.0, "mg/kg"),
    "potassium": (0.0, 1999.0, "mg/kg"),
    "ph": (3.0, 10.0, "pH"),
    "moisture": (0.0, 100.0, "%"),
    "temperature": (-20.0, 80.0, "°C"),
}


def compute_modbus_crc(data: bytes) -> int:
    """
    Computes standard Modbus-RTU 16-bit Cyclic Redundancy Check (CRC-16).
    Polynomial: 0xA001 (reversed representation of standard 0x8005).
    Initial value: 0xFFFF.
    """
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def compute_modbus_crc_bytes(data: bytes) -> bytes:
    """
    Returns the 2-byte CRC for a Modbus frame in Little-Endian byte order
    (Low byte followed by High byte).
    """
    crc = compute_modbus_crc(data)
    low_byte = crc & 0xFF
    high_byte = (crc >> 8) & 0xFF
    return bytes([low_byte, high_byte])


def validate_modbus_frame(frame: bytes) -> Tuple[bool, Optional[str]]:
    """
    Validates a received Modbus-RTU binary frame:
    1. Checks minimum frame length (at least 4 bytes: Slave ID, Func Code, Data/Byte Count, CRC-L, CRC-H).
    2. Computes CRC-16 on payload portion (all bytes except last 2).
    3. Compares computed CRC with received trailing 2 bytes.

    Returns:
        (True, None) if frame is valid and uncorrupted.
        (False, error_reason) if frame is too short or CRC does not match.
    """
    if not isinstance(frame, (bytes, bytearray)):
        return False, "Frame must be bytes or bytearray"

    if len(frame) < 4:
        return False, f"Frame too short ({len(frame)} bytes, minimum 4 bytes required for Modbus-RTU)"

    payload = frame[:-2]
    received_crc = frame[-2:]

    computed_crc_bytes = compute_modbus_crc_bytes(payload)

    if received_crc != computed_crc_bytes:
        computed_int = compute_modbus_crc(payload)
        rec_int = received_crc[0] | (received_crc[1] << 8)
        return False, f"CRC mismatch: expected 0x{computed_int:04X}, received 0x{rec_int:04X}"

    return True, None


def extract_modbus_payload(frame: bytes) -> Tuple[int, int, bytes]:
    """
    Validates frame and extracts (slave_id, function_code, data_bytes).

    Raises:
        ValueError: if frame fails length or CRC verification.
    """
    is_valid, err = validate_modbus_frame(frame)
    if not is_valid:
        raise ValueError(f"Invalid Modbus-RTU frame: {err}")

    slave_id = frame[0]
    func_code = frame[1]
    data_bytes = frame[2:-2]

    return slave_id, func_code, data_bytes


def validate_parameter(name: str, value: Optional[Union[int, float]]) -> Optional[float]:
    """
    Validates a single agricultural parameter against its physical range.
    Rejects out-of-range/impossible numbers to None (Zero Hardware Hallucination).
    Never replaces invalid numbers with fake defaults.
    """
    if value is None:
        return None

    try:
        val_float = float(value)
    except (TypeError, ValueError):
        log_event("SOIL", "WARNING", f"Parameter '{name}' invalid non-numeric value: {value} -> Rejected to None")
        return None

    range_spec = TELEMETRY_RANGES.get(name.lower())
    if not range_spec:
        # Unknown parameter without strict bounds; return rounded value
        return round(val_float, 2)

    min_val, max_val, unit = range_spec
    if val_float < min_val or val_float > max_val:
        log_event(
            "SOIL",
            "WARNING",
            f"Physical range violation for '{name}': {val_float} {unit} outside [{min_val}, {max_val}] -> Rejected to None"
        )
        return None

    return round(val_float, 2)


def validate_soil_telemetry(
    nitrogen: Optional[float] = None,
    phosphorus: Optional[float] = None,
    potassium: Optional[float] = None,
    ph: Optional[float] = None,
    moisture: Optional[float] = None,
    temperature: Optional[float] = None
) -> Dict[str, Optional[float]]:
    """
    Validates all 6 telemetry parameters independently.
    Valid parameters are preserved; invalid parameters are converted to None.
    """
    return {
        "nitrogen": validate_parameter("nitrogen", nitrogen),
        "phosphorus": validate_parameter("phosphorus", phosphorus),
        "potassium": validate_parameter("potassium", potassium),
        "ph": validate_parameter("ph", ph),
        "moisture": validate_parameter("moisture", moisture),
        "temperature": validate_parameter("temperature", temperature)
    }
