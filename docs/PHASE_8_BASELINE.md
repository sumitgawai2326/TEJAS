# Phase 8 Baseline Inspection Report — KrishiDrishti Edge

> **Inspection Date:** 2026-09-09  
> **Project:** KrishiDrishti Edge ("See. Sense. Predict. Act.")  
> **Baseline State:** Phases 0 through 7 Complete & Verified.

---

## 1. Existing System Architecture Baseline

### A. AI Vision & Inference Pipeline
- **Accelerator Detection (`ai/inference/base.py`)**: `AcceleratorDetector` checks for `/dev/hailo0` (Raspberry Pi AI HAT+) and `hailo_platform`, falling back dynamically to `CPU FALLBACK`.
- **Model Backend Implementations (`ai/inference/backends.py`)**:
  - `DemoModelBackend`: Explicit placeholder backend for UI and presentation testing with synthetic pathology outputs.
  - `ONNXModelBackend`: Physical file-based ONNX runtime backend loaded if `MODEL_PATH` exists on disk.
- **Vision Model Manager (`ai/inference/manager.py`)**: Central orchestrator applying confidence gating ($0.70$ threshold). If no real model file is present in production mode, returns `status: "ai_unavailable"` / `AI_NOT_READY`.
- **Image Quality Validation (`ai/preprocessing/quality.py`)**: Pre-inference 3-point check (Laplacian blur variance $> 20.0$, exposure luminance $25.0 \le L \le 235.0$, resolution $\ge 120 \times 120$).
- **Tensor Preprocessor (`ai/preprocessing/preprocessor.py`)**: Normalizes input to $224 \times 224 \times 3$ ImageNet mean/std tensor.

### B. Hardware Abstraction Layer (HAL)
- **Soil Sensor HAL (`backend/app/hardware/soil_sensor/`)**:
  - `ModbusSoilSensor`: RS485 Modbus-RTU driver reading 6 parameters ($N, P, K, \text{pH}$, Moisture, Temperature) using declarative `hardware/sensor_protocol/soil_sensor.yaml`.
  - Zero Hardware Hallucination: Retains unconfigured `null` registers in `soil_sensor.yaml`. In real mode without hardware, strictly reports `SENSOR_UNCONFIGURED` / `SENSOR_DISCONNECTED` with `NULL` measurements.
  - `MockSoilSensor`: Isolated simulated telemetry active only when `DEMO_MODE=true`.
- **Camera HAL (`backend/app/hardware/camera/`)**:
  - `CameraHAL`: Physical V4L2 device index 0 wrapper (`/dev/video0`). Returns `CAMERA_UNAVAILABLE` when absent.
  - `MockCamera`: Synthetic test pattern active only when `DEMO_MODE=true`.
- **Battery Monitor (`backend/app/hardware/battery/battery_monitor.py`)**:
  - Reads `psutil.sensors_battery()`. In real mode when absent, returns `status: "UNAVAILABLE"` with `percent: None` (no fabricated battery values).

### C. Multi-Modal Fusion, Risk & Advisory Architecture
- **Fusion Engine (`backend/app/services/fusion/`)**:
  - Synthesizes Vision Pathology + 6-Parameter Soil Telemetry + Field Context + Historical Trends.
  - Generates structured `EvidenceItem` records with explicit `is_demo` tags.
- **Risk Engine (`backend/app/services/fusion/risk_engine.py`)**:
  - Evaluates Data Completeness ratio ($0.0$ to $1.0$). If completeness $< 0.35$ and vision is low confidence, outputs `risk_level: "UNKNOWN"`.
  - Prototype heuristic risk scoring flagged with `is_prototype_heuristic: true`.
- **Advisory Engine (`backend/app/services/advisory/`)**:
  - Generates priority-ordered non-toxic agronomic guidance (`URGENT`, `HIGH`, `MEDIUM`, `LOW`, `INFO`). Zero chemical pesticide doses are invented.

### D. Offline Database & Storage
- **Relational Schema (`backend/app/db/models.py`)**:
  - Normalized SQLite tables: `farms`, `fields`, `crops`, `scans`, `soil_readings`, `risk_assessments`, `advisories`, `device_events`.
  - Enforces `PRAGMA foreign_keys=ON` and `is_mock` separation.

### E. Verification & Test Baseline
- **Automated Backend & Hardware Tests**: `78 / 78 PASSED (100% green in 9.51s)`.
  - 66 backend unit/integration tests (`tests/backend/`).
  - 12 hardware detection, self-test, and diagnostic CLI tests (`tests/hardware/`).
- **Frontend Production Build**: `npm --prefix frontend run build` compiles with **0 TypeScript Errors** into `dist/`.

---

## 2. Phase 8 Evolution Scope
Phase 8 evolves the vision subsystem toward a real, reproducible, and verifiable agricultural model lifecycle without compromising honesty:
1. Pluggable agricultural dataset manifest architecture (`data/datasets/`, `docs/DATASET_GUIDE.md`).
2. Robust model registry and discovery (`backend/app/ai/model_registry.py`, `GET /api/vision/models`).
3. Model validation & input/output shape verification (`backend/app/ai/validation/`).
4. Agricultural prediction schema with metadata provenance (`prediction_id`, `model_hash`, `is_validated`, `latency_ms`).
5. Multi-tier confidence & uncertainty farmer guidance.
6. Offline model evaluation pipeline on labeled test splits (`backend/app/ai/evaluation/`).
7. Complete multi-modal evidence provenance tracking in Fusion, Risk, and Advisories (`REAL_VISION`, `DEMO_VISION`, `REAL_SOIL`, `MOCK_SOIL`, `RULE`, `COMBINED`).
8. Dedicated SIH demonstration mode and technical claims verification (`docs/SIH_DEMO_MODE.md`, `docs/SIH_TECHNICAL_CLAIMS.md`).
