# TEJAS — Phase 11A: Hardware-Safe Soil Communication Layer

**Project**: TEJAS  
**Tagline**: *"See. Sense. Predict. Act."*  
**Date**: September 10, 2026  
**Status**: **PHASE 11A COMPLETE — HARDWARE-SAFE SOIL LAYER INTEGRATED**

---

## 1. Executive Summary

Phase 11A implements the hardware-safe foundation for the TEJAS RS485 Modbus-RTU 6-parameter soil intelligence subsystem. It establishes generic Modbus-RTU CRC-16 computation and validation, parameter-level physical range validation, safe USB-RS485 port auto-discovery, and bounded exponential backoff reconnection logic.

> [!IMPORTANT]
> **Real Modbus register decoding remains disabled until the exact physical sensor datasheet is verified.**

---

## 2. Modbus-RTU Frame CRC-16 Architecture

The generic Modbus-RTU decoder (`backend/app/hardware/soil_sensor/modbus_decoder.py`) computes standard 16-bit Cyclic Redundancy Checks:
- **Polynomial**: `0xA001` (reversed representation of `0x8005`)
- **Initial Value**: `0xFFFF`
- **Transmission Format**: Little-Endian (Low-order byte followed by High-order byte)

### Frame Validation Invariants
1. **Minimum Length Verification**: Rejects any frame shorter than 4 bytes ($1\text{ byte slave ID} + 1\text{ byte func code} + \text{payload} + 2\text{ bytes CRC}$).
2. **CRC Verification**: Computes CRC on `frame[:-2]` and strictly matches against `frame[-2:]`. Corrupted frames are rejected immediately with diagnostic error messages.
3. **Payload Extraction**: `extract_modbus_payload(frame)` safely unpacks `(slave_id, func_code, data_bytes)`.

---

## 3. Telemetry Physical Range Validation

To enforce the **Zero Hardware Hallucination Policy**, telemetry validation ensures that noise, bus contention, or uncalibrated responses cannot insert impossible numbers into SQLite:

| Telemetry Parameter | Physical Range Boundary | Unit | Action on Violation |
| :--- | :---: | :---: | :--- |
| **Nitrogen ($N$)** | `[0.0, 1999.0]` | $\text{mg/kg}$ | Logged as warning $\to$ set to `None` |
| **Phosphorus ($P$)** | `[0.0, 1999.0]` | $\text{mg/kg}$ | Logged as warning $\to$ set to `None` |
| **Potassium ($K$)** | `[0.0, 1999.0]` | $\text{mg/kg}$ | Logged as warning $\to$ set to `None` |
| **Soil pH** | `[3.0, 10.0]` | $\text{pH}$ | Logged as warning $\to$ set to `None` |
| **Soil Moisture** | `[0.0, 100.0]` | $\%$ | Logged as warning $\to$ set to `None` |
| **Soil Temperature** | `[-20.0, 80.0]` | $^\circ\text{C}$ | Logged as warning $\to$ set to `None` |

### Validation Invariants
- **No Fallback Defaults**: Invalid values are never replaced with $0.0$ or arbitrary numbers.
- **Partial Telemetry Preservation**: If one parameter is corrupted (e.g. $\text{pH} = 14.5$), valid parameters in the same packet (e.g. $\text{Moisture} = 24.5\%$) are preserved while the invalid parameter is clamped to `None`.

---

## 4. USB-RS485 Serial Port Auto-Discovery

The port discovery helper (`backend/app/hardware/soil_sensor/port_discovery.py`) scans host hardware:
- **Windows**: Enumerate `COM*` ports.
- **Linux / Raspberry Pi**: Enumerate `/dev/ttyUSB*` and `/dev/ttyACM*` adapters.
- **Safe Prioritization**: If the configured port exists, it is prioritized.
- **Zero-Hallucination Invariant**: Port existence *never* implies sensor attachment or responsiveness. Actual connectivity is confirmed only through valid Modbus responses.

---

## 5. Bounded Retry & Reconnection Flow

The driver (`backend/app/hardware/soil_sensor/modbus_sensor.py`) incorporates safe retry:
- **Retry Bound**: Clamped between $1$ and $5$ attempts (default $3$).
- **Exponential Backoff**: Initial delay $0.1\text{s}$, doubling each attempt ($0.1\text{s} \to 0.2\text{s} \to 0.4\text{s}$).
- **Non-blocking Abort**: If all retries fail, cleanly returns `SoilTelemetry` with `status="SENSOR DISCONNECTED"`, `connected=False`, and all 6 parameters as `None`.
- **No Infinite Loops**: Guaranteed bounded execution time.

---

## 6. Strict Zero-Hallucination Guarantees

| Mode | `soil_sensor.yaml` State | Behavior | Telemetry Output |
| :--- | :--- | :--- | :--- |
| `DEMO_MODE=true` | Any | Isolated `MockSoilSensor` | $N, P, K, \text{pH}$, Moist, Temp simulated; `is_mock=True` |
| `DEMO_MODE=false` | `is_configured: false` | Real driver safe unconfigured exit | All 6 values strictly `None`; `is_mock=False` |
| `DEMO_MODE=false` | Disconnected port | Bounded retry $\to$ safe disconnect | All 6 values strictly `None`; `is_mock=False` |

---

## 7. Blocked Physical Sensor Items (Awaiting Hardware Datasheet)

The following items remain strictly unconfigured until the physical 6-in-1 sensor hardware and datasheet are received:
1. Exact Modbus Slave ID address.
2. Baud rate ($4800, 9600, 19200$, etc.).
3. Modbus Function Code (`0x03` Holding Registers vs `0x04` Input Registers).
4. Register start addresses for Nitrogen, Phosphorus, Potassium, pH, Moisture, and Temperature.
5. Register data types (`uint16` / `int16`) and byte endianness.
6. Parameter scale factors (e.g. $0.1$ for $1$ decimal place).
