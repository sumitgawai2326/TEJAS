# KrishiDrishti Edge — AI Current State Audit (Phase A Baseline)

## 1. Executive Summary
This document records the exact baseline architectural state of the **KrishiDrishti Edge** vision and AI subsystem prior to implementing the dedicated Tomato ML pipeline.

- **Baseline Test Suite**: **88 / 88 tests PASSED (100% Green)** across backend, hardware, and AI validation suites.
- **Frontend Production Build**: **0 TypeScript errors** (Bundle: 281.39 kB JS, 23.32 kB CSS).
- **Core Policy Enforced**: Strict **Zero AI Hallucination** & **Zero Hardware Hallucination**.

---

## 2. Comprehensive Subsystem Audit

### 1. What Already Exists
- **Hardware Abstraction Layer (HAL)**: Auto-detection for host platforms (Raspberry Pi 5 / x86 workstation), dynamic RS485 serial interface listing, and camera HAL supporting OpenCV/V4L2 device capture with synthetic image fallback.
- **Image Quality Validation Subsystem** (`ai/preprocessing/quality.py`): Rejects blurry images (Laplacian variance $< 18.0$), underexposed ($< 20$), overexposed ($> 240$), or sub-resolution ($< 120 \times 120$) captures with actionable farmer instructions.
- **Image Preprocessing** (`ai/preprocessing/preprocessor.py`): BGR to RGB conversion, dynamic target dimension resolution, ImageNet normalization, and NCHW tensor batch expansion.
- **AI Inference Abstraction** (`ai/inference/`):
  - `VisionModelManager` coordinating execution, dynamic input shapes, and multi-tier confidence gating.
  - `BaseVisionModel`, `DemoVisionModel`, `ONNXVisionModel`.
  - `AcceleratorDetector` supporting Hailo-8 / CPU execution provider fallback.
- **Model Registry & Integrity Subsystem** (`backend/app/ai/model_registry.py`): Dynamic discovery of local models, SHA-256 binary hash computation, and status tracking (`REAL_MODEL`, `DEMO_MODEL`, `MODEL_MISSING`, `MODEL_INVALID`).
- **Model Validation Subsystem** (`backend/app/ai/validation/model_validator.py`): Pre-flight structural and smoke inference validation.
- **Offline Benchmark & Evaluator** (`backend/app/ai/evaluation/evaluator.py`): Top-1 accuracy, Precision, Recall, Macro F1, and Confusion Matrix calculation without synthetic score fabrication.
- **Monotonic Pipeline Profiler** (`backend/app/ai/profiling/profiler.py`): Monotonic timing (`time.perf_counter()`) across decode, preprocess, inference, and postprocess.
- **Crop + Soil Intelligence Fusion & Advisory Engines** (`backend/app/services/fusion/` & `advisory/`): Explainable risk synthesis and evidence tracking with explicit modality provenance (`vision_provenance`, `soil_provenance`, `history_provenance`).
- **Offline SQLite Relational Database** (`backend/app/db/`): Persistent relational schema for farms, fields, crops, scans, soil readings, risk assessments, advisories, and device events.

### 2. What Works
- 7-step guided field check wizard and standalone scanner in the frontend.
- Confidence gating separating High ($\ge 0.85$), Medium ($\ge 0.70$), and Low ($< 0.70$) tiers.
- Provenance tags propagating through vision, soil, fusion, and advisories.
- Safe exit on unconfigured hardware and absent model files without crashing.

### 3. What is Placeholder / Demo-Only
- In `DEMO_MODE=true`, `DemoModelBackend` simulates leaf predictions (`is_demo: true`, `model_version: "0.1.0-demo-placeholder"`).
- In `DEMO_MODE=false`, production weights (`ai/models/crop_disease_v1.onnx`) are currently absent on disk, resulting in the truthful status `AI_NOT_READY` and `NOT YET VALIDATED`.
- Physical training pipeline and custom tomato model export to ONNX are not yet implemented.

### 4. What is Missing
- A structured machine learning dataset management and preparation pipeline in `ml/data/` and `ml/scripts/`.
- Documented dataset research, licensing audit, and class mapping specifically for Tomato pathology.
- Deterministic data splitting with data leakage prevention.
- PyTorch / Ultralytics lightweight YOLO classification training pipeline (`ml/train.py`).
- Automated model export and validation script (`ml/export_onnx.py`, `ml/validate_onnx.py`).
- Benchmarked evaluation report on a held-out test partition (`reports/model_evaluation.json`).

### 5. What Must NOT Be Changed
- Do NOT rewrite or break existing FastAPI REST endpoints (`/api/vision/status`, `/api/vision/analyze`, `/api/vision/models`, `/api/fields/*`, `/api/device/*`).
- Do NOT alter the Zero Hardware Hallucination policy or unconfigured registers in `hardware/sensor_protocol/soil_sensor.yaml`.
- Do NOT fabricate model accuracy or physical Hailo/RPi benchmarks.
- Do NOT alter working Phase 0–8 database schemas, models, or test suites.

### 6. What This Implementation Will Add
- Complete ML development workspace (`ml/`) with reproducible dataset ingestion, cleaning, splitting, training, evaluation, and ONNX export.
- Verified Tomato disease class map (`data/class_map.yaml`) and dataset manifest (`data/dataset_manifest.yaml`).
- Trained & validated lightweight YOLO classification model exported to ONNX format.
- Seamless backend integration where the real ONNX model is discovered and loaded by `ONNXVisionModel` and `ModelRegistry`.
- Comprehensive documentation suite and test suites covering dataset integrity, model export, ONNX inference, confidence gating, and advisory safety.
