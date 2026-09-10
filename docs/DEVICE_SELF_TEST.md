# Device Self-Test Specification — KrishiDrishti Edge

> **Service Endpoint:** `GET /api/device/self-test`  
> **Service Layer:** `app.services.self_test.DeviceSelfTestService`

---

## 1. Overview & Architecture

The Device Self-Test subsystem performs a non-intrusive diagnostic sweep across the entire edge hardware and software stack upon initial boot or on-demand from the touchscreen diagnostics console.

---

## 2. Subsystems Evaluated

1. **Local SQLite Database (Critical)**:
   - Executes `SELECT 1` query through SQLAlchemy `SessionLocal`.
   - Validates file read/write permissions at `data/krishidrishti.db`.
   - Measures database roundtrip latency (typically $< 5\text{ms}$).
2. **Edge Local Storage (Critical)**:
   - Inspects volume partition hosting `data/`.
   - Checks free disk space against safety threshold ($> 500\text{MB}$).
   - Emits `WARNING` if free disk space is constrained.
3. **Camera Subsystem (Non-Critical Peripheral)**:
   - Probes V4L2 device index 0 (`CameraHAL.is_available()`).
   - If `DEMO_MODE=true`: reports `PASSED (Mock Viewfinder)`.
   - If `DEMO_MODE=false`: reports `PASSED` (if physical camera responds) or `WARNING` (if absent, enabling upload fallback).
4. **6-Parameter Soil Sensor Interface (Non-Critical Peripheral)**:
   - Probes RS485 serial link and YAML register map status.
   - If `DEMO_MODE=true`: reports `PASSED (Demo Simulation)`.
   - If `DEMO_MODE=false`: reports `PASSED` (if probe responds) or `WARNING (SENSOR DISCONNECTED / UNCONFIGURED)`.
5. **AI Inference Engine (Critical/Degraded)**:
   - Evaluates `AcceleratorDetector` status for Raspberry Pi AI HAT+ (`/dev/hailo0`) or CPU fallback.
   - Verifies neural network preprocessor tensor pipeline.
6. **Host Platform & Runtime (Critical)**:
   - Identifies board model (e.g. Raspberry Pi 5 vs Development Workstation), OS kernel, architecture, and Python runtime.

---

## 3. Overall Device States

- **`DEVICE READY`**: All 6 subsystems passed with zero warnings or errors.
- **`DEVICE READY WITH WARNINGS`**: Core system and database are healthy, but non-critical optional peripherals (e.g. RS485 soil probe or hardware camera) are disconnected or unconfigured. The system permits operation with file uploads and manual inputs.
- **`DEVICE INITIALIZATION FAILED`**: A critical dependency (such as the local SQLite database or disk storage) failed to initialize.
