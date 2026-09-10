# Hardware Safety & Operational Principles — KrishiDrishti Edge

> **Zero Hardware Hallucination & Operator Safety Directive**

---

## 1. Power Supply & Battery Safety

1. **Commercial Battery / Power Bank Requirement**:
   - **DO NOT** construct DIY, unshielded 18650/LiPo battery packs for hackathon or field demonstrations without certified Battery Management Systems (BMS).
   - Use a certified commercial USB-C Power Delivery (PD) power bank capable of `5V @ 5.0A (25W)` minimum (e.g. Official Raspberry Pi 27W USB-C PSU or Anker/Baseus 65W PD Battery Bank).
2. **Voltage Regulation**:
   - Raspberry Pi 5 requires a regulated 5.1V power rail. Undervoltage conditions throttle the CPU and corrupt SQLite write cycles on SD/NVMe media.
3. **Power Down Protocol**:
   - Always initiate a safe OS shutdown (`sudo poweroff` or via UI settings) before disconnecting the power supply to prevent SQLite WAL database corruption.

---

## 2. RS485 & Soil Sensor Electrical Safety

1. **Galvanic Isolation & Differential Bus**:
   - Industrial soil sensors typically operate at `9V - 24V DC`. **DO NOT** connect the sensor's power supply directly to Raspberry Pi 3.3V or 5V GPIO pins.
   - Power the soil sensor externally using an isolated 12V/24V step-up booster or dedicated 12V DC battery rail.
   - Connect only the differential signal lines (`RS485 A+` and `RS485 B-`) to the isolated USB-RS485 transceiver.
2. **Polarity & Grounding**:
   - Reversing `A` and `B` differential lines will prevent communication without damaging modern protected transceivers, but will cause `SENSOR_DISCONNECTED` errors.
   - Always connect common reference ground (`GND`) between the RS485 converter and sensor if long cable runs (> 10m) are deployed.

---

## 3. Field Environmental Protection (Ingress Protection)

1. **Field Probe Handling**:
   - Only the stainless steel probe pins of the 6-parameter soil sensor should be inserted into the soil.
   - The probe handle, resin epoxy potting joint, cable strain relief, and electronics must be kept clean and dry.
   - Do not force the probe into hard, dry, or rocky terrain—use a soil auger or pre-hole tool to prevent bending the sensor prongs.
2. **Enclosure Guidelines**:
   - Mount the Raspberry Pi 5, AI HAT+, touchscreen, and RS485 adapter inside an IP65-rated weather-resistant polycarbonate or 3D-printed enclosure with rubber gaskets and silicone port plugs.
   - Provide adequate active cooling (Raspberry Pi Active Cooler) to maintain CPU temperatures below $75^\circ\text{C}$ in ambient outdoor sunlight.
