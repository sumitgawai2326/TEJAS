# 6-Parameter Soil Sensor Setup & Protocol Guide — KrishiDrishti Edge

> **Module:** 6-Parameter Soil Intelligence Module  
> **Parameters:** Nitrogen ($N$), Phosphorus ($P$), Potassium ($K$), Soil $\text{pH}$, Volumetric Moisture ($\%$) and Temperature ($^\circ\text{C}$).  
> **Bus Standard:** RS485 Half-Duplex Differential Bus  
> **Protocol:** Modbus-RTU

---

## 1. Hardware Connection Topology

```
[ Industrial 6-Parameter Soil Probe ]
   ├── Brown Wire   : Power Supply + (9V - 24V DC External Source)
   ├── Black Wire   : Power Supply - / Ground (GND)
   ├── Yellow Wire  : RS485 A+ (Non-inverting differential signal)
   └── Blue Wire    : RS485 B- (Inverting differential signal)
            │
            ▼
[ USB-to-RS485 Transceiver (FTDI / CH340) ]
   ├── Terminal A+  <-- Connected to Yellow Wire (RS485 A+)
   ├── Terminal B-  <-- Connected to Blue Wire (RS485 B-)
   └── Terminal GND <-- Connected to Common Ground
            │
            ▼ (USB 3.0 Port)
[ Raspberry Pi 5 / Host Computer ]
```

> [!CAUTION]
> **Power Isolation Warning**:
> Never supply 9V-24V DC power to the Raspberry Pi's GPIO pins. The sensor must be powered from a dedicated 12V DC rail, with only the differential RS485 lines connected to the USB-RS485 converter.

---

## 2. Register Configuration Walkthrough

1. When the physical sensor is received with its manufacturer datasheet, open `hardware/sensor_protocol/soil_sensor.yaml`.
2. Update the `sensor` section:
   - `baudrate`: Enter the datasheet default (e.g. 4800 or 9600).
   - `slave_id`: Enter the Modbus slave address (typically 1).
   - `is_configured`: Set to `true`.
3. Fill in the register addresses, scaling factors, and datatypes under `parameters`.
4. Validate the configuration using the CLI diagnostic tool:
   ```bash
   python -m app.tools.sensor_diagnostic
   ```
