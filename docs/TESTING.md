# KrishiDrishti Edge — Automated Testing & Verification Guide

> **Test Suite Coverage & Instructions**

---

## 1. Test Architecture Overview

The KrishiDrishti Edge test suite enforces strict hardware isolation and zero hallucination policies across all layers:

1. **Hardware HAL Tests**:
   - `tests/backend/test_camera.py`: Tests mock camera, camera HAL disconnected state, mode switching.
   - `tests/backend/test_soil_sensor.py`: Tests mock sensor, unconfigured register map, disconnected sensor returning nulls, mode switching.
2. **AI Inference & Accelerator Tests**:
   - `tests/backend/test_ai_inference.py`: Tests accelerator detector CPU fallback, auto mode, confidence gating pass/fail.
3. **Database & Field History Tests**:
   - `tests/backend/test_database.py`: Tests SQLite models, foreign key cascades, null telemetry storage, risk assessments, chronologic timeline queries.
   - `tests/backend/test_fields_api.py`: Tests REST endpoints for fields, soil readings, scans, and timelines.
4. **Vision Pipeline & Preprocessing Tests**:
   - `tests/backend/test_vision_pipeline.py`: Tests image quality validator (sharp, blurry, dark, bright, small, corrupt), tensor preprocessor, vision manager, real mode zero hallucination (missing model file rejection), multipart image upload, and camera capture.
5. **Crop + Soil Intelligence Fusion & Advisory Tests**:
   - `tests/backend/test_fusion_engine.py`: Tests complete multi-modal fusion input, missing/partial soil telemetry, missing/gated vision signals, temporal trend deltas, repeat pathology detection, UNKNOWN risk state handling, unconfigured rule honesty, prioritized advisory generation, SQLite persistence, and REST endpoints (/analyze, /risk/latest, /risk/history, /advisories).
6. **System Diagnostics Tests**:
   - `tests/backend/test_health.py`: Tests `/health`, dynamic device status, battery, RAM, CPU temp telemetry.
   - `tests/backend/test_subsystems_api.py`: Tests `/api/camera/status`, `/api/soil/status`, `/api/ai/status`.

---

## 2. Running Backend Tests

```bash
# Run the entire backend test suite (66/66 tests)
python -m pytest tests/backend -v

# Run only Phase 5 Fusion tests
python -m pytest tests/backend/test_fusion_engine.py -v
```

---

## 3. Running Frontend Production Build & Tests

```bash
# Verify TypeScript compilation and Vite production build
npm.cmd --prefix frontend run build
```

