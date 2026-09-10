# Hardware Validation & Acceptance Test Manual — KrishiDrishti Edge

> **Zero Hardware Hallucination Directive:**  
> This protocol specifies 15 manual and automated tests to be performed upon physical assembly with real hardware components.

---

## Acceptance Test Protocol Matrix

| Test ID | Test Name | Verification Procedure | Expected Outcome |
|---|---|---|---|
| **TEST 01** | Raspberry Pi Boot & Service Startup | Power on Raspberry Pi 5 with commercial 27W USB-C PSU. Verify systemd startup: `systemctl status krishidrishti.service`. | Backend active on port 8000, UI renders on local kiosk. |
| **TEST 02** | Hardware Capability Auto-Detection | Access `GET /api/device/status`. Verify board model reports "Raspberry Pi 5" and Linux 64-bit OS. | Truthful host identification without hardcoding. |
| **TEST 03** | Startup Subsystem Self-Test | Trigger `GET /api/device/self-test` or tap "Run Hardware Self-Test" in Diagnostics tab. | Reports `DEVICE READY` (or `DEVICE READY WITH WARNINGS` if sensor unattached). |
| **TEST 04** | Physical Camera Initialization | Connect Raspberry Pi Camera Module / USB camera. Verify `GET /subsystems/camera`. | Status: `READY`, device index 0 detected with valid resolution. |
| **TEST 05** | Real Image Capture & Quality Gate | Trigger capture from leaf viewfinder. | Passes blur variance, exposure luminance, and $224 \times 224$ resolution checks. |
| **TEST 06** | Blurry / Dark Image Quality Rejection | Capture deliberately out-of-focus or covered camera frame. | Status `rejected_quality` with farmer advice: "Image is blurry" or "Improve lighting". |
| **TEST 07** | Raspberry Pi AI HAT+ Detection | Verify Hailo character device `/dev/hailo0` via `lspci -nn` and `/subsystems/ai`. | AI Mode reports `HAILO ACCELERATED` (or `CPU FALLBACK` if HAT unseated). |
| **TEST 08** | Quantized Edge AI Inference | Execute leaf pathology diagnosis on captured leaf image. | Inference time $< 50\text{ms}$ on Hailo-8, confidence score calculated with gating. |
| **TEST 09** | RS485 Adapter Hardware Enumeration | Plug USB-RS485 adapter into USB 3.0 port. Check `python -m app.tools.sensor_diagnostic`. | Serial port `/dev/ttyUSB0` discovered and tagged as candidate. |
| **TEST 10** | Unconfigured Register Map Safety | Query soil reading when `is_configured: false`. | Status: `UNCONFIGURED_REGISTER_MAP`, all 6 parameters strictly `null`. |
| **TEST 11** | Physical Soil Sensor Modbus Read | Populate valid datasheet registers in `soil_sensor.yaml`. Insert probe into soil sample. | Reads exact 6 parameters: $N, P, K, \text{pH}$, Moisture, Temperature. |
| **TEST 12** | Sensor Disconnection Detection | Unplug RS485 differential wire during active operation. | Status transitions to `SENSOR DISCONNECTED`; database records `null` values (no fake zeros). |
| **TEST 13** | Multi-Modal Fusion Execution | Run complete field check on selected field with real camera photo and soil read. | Generates synthesized Field Risk Level (`LOW`/`MODERATE`/`HIGH`/`CRITICAL`) with evidence breakdown. |
| **TEST 14** | Actionable Farmer Advisory & DB Commit | Verify generated advisories and check SQLite `data/krishidrishti.db`. | Priority-ranked advisories created and persisted into local relational tables. |
| **TEST 15** | 100% Offline Field Verification | Disconnect all Wi-Fi, Ethernet, and external networks. Run complete 7-step wizard. | Full workflow functions with zero cloud calls, zero network lag, and persistent history timeline. |
