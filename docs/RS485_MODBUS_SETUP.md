# RS485 Modbus-RTU Technical Specification — KrishiDrishti Edge

> **Protocol Standards & Zero Hallucination Reference**

---

## 1. Modbus-RTU Frame Structure

Modbus-RTU transmits binary frames over differential serial lines with a 16-bit Cyclic Redundancy Check (CRC-16):

```
┌───────────┬───────────────┬───────────────────┬───────────────────┬───────────────┐
│ Slave ID  │ Function Code │ Start Address     │ Number of Points  │ CRC-16 (L/H)  │
│  (1 Byte) │   (1 Byte)    │ (2 Bytes: MSB/LSB)│ (2 Bytes: MSB/LSB)│ (2 Bytes)     │
└───────────┴───────────────┴───────────────────┴───────────────────┴───────────────┘
```

### Supported Function Codes
- **Function Code `0x03`**: Read Holding Registers
- **Function Code `0x04`**: Read Input Registers

---

## 2. Parameter Scaling & Transformation Pipeline

The data decoding architecture processes raw bytes into agronomic engineering units through a deterministic, transparent pipeline:

$$\text{Reading} = (\text{Raw Register Value} \times \text{Scale Factor}) + \text{Calibration Offset}$$

```
[ Raw Modbus Frame: 2 Bytes (MSB + LSB) ]
                 ↓
[ 16-bit Integer Decoding: uint16 / int16 ]
                 ↓
[ Scaling Factor Application (e.g. 0.1 for 1 decimal place) ]
                 ↓
[ Agronomic Engineering Units (mg/kg, pH, %, °C) ]
                 ↓
[ Zero-Hallucination Range Validation ]
                 ↓
[ Committed to SQLite SoilReading Entity ]
```

---

## 3. Communication Error Codes

| Error Code | Root Cause | Operator Action |
|---|---|---|
| `SENSOR_UNCONFIGURED` | `is_configured: false` in `soil_sensor.yaml` | Populate register addresses from sensor datasheet. |
| `SENSOR_DISCONNECTED` | Serial port cannot be opened or device node absent | Check USB-RS485 adapter connection and permissions (`dialout` group). |
| `HARDWARE_TIMEOUT` | No response within 2.0s from slave device | Verify sensor 12V power supply and $A+/B-$ wiring polarity. |
| `INVALID_RESPONSE` | CRC-16 checksum error or truncated frame | Check for electrical noise on RS485 bus or baud rate mismatch. |
| `PERMISSION_ERROR` | Insufficient Linux user privileges on `/dev/ttyUSB0` | Run `sudo usermod -aG dialout $USER` and relogin. |
