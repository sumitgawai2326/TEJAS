# TEJAS

> **Technology Enabled Judicious Agriculture And soil sensor**  
> *Portable Offline Edge AI Agriculture System for Smart India Hackathon (SIH)*

---

## 🌾 Overview

**TEJAS** is a rugged, edge-native, portable agricultural intelligence instrument designed to provide localized field intelligence directly to farmers without cloud dependency.

It integrates:
1. **Edge AI Vision Subsystem**: Local crop leaf pathology and pest diagnosis with image quality gating (blur, brightness, contrast) and multi-tier confidence gating on lightweight ONNX neural models.
2. **Real 6-Parameter Soil Intelligence**: Direct RS485 MODBUS-RTU probe interface measuring Nitrogen (N), Phosphorus (P), Potassium (K), pH, Moisture, and Temperature.
3. **Offline SQLite Database & Temporal History**: On-device normalized relational schema recording farms, fields, crops, leaf scans, 6-parameter soil readings, risk assessments, advisories, and hardware diagnostic events.
4. **Crop + Soil Fusion & Advisory Engine**: Multi-modal rule engine combining vision predictions with soil chemistry and historical trends to generate timely agronomic advisories.
5. **Farmer Advisory & Multilingual UI**: Actionable decision support in English, Hindi (हिंदी), and Marathi (मराठी) on a high-contrast 7-inch touchscreen shell.
6. **Zero Hardware & AI Hallucination Policies**: Strict separation between real hardware data and isolated demo/simulation data, with cryptographic model hashing and truthful metrics.

---

## 🛡️ Critical Engineering Policies: Zero Hallucination

- **Zero Hardware Hallucination**: If sensors, camera, or accelerators are disconnected or unconfigured, the system strictly outputs `"SENSOR DISCONNECTED"`, `"CAMERA DISCONNECTED"`, or `"CPU FALLBACK"`. In the database, unmeasured parameters strictly remain `NULL`. Sensor baud rates and MODBUS registers are never invented.
- **Zero AI Hallucination**: Model performance metrics, latencies, and agricultural accuracy are never fabricated. Unvalidated field performance is explicitly labeled `PENDING FIELD VALIDATION`, and unmeasured hardware latency is marked `PENDING PHYSICAL BENCHMARK`.
- **Dedicated Demo Mode (`DEMO_MODE=true`)**: For hackathon presentations and development when physical hardware is not plugged in, simulated data is stored with `is_mock: true`, and the UI renders a prominent `DEMO / SIMULATION MODE` banner.
- **Declarative Unconfigured Register Map**: `hardware/sensor_protocol/soil_sensor.yaml` maintains `null` address placeholders until the exact sensor datasheet is supplied.

---

## 📁 Repository Structure

```
krishidrishti-edge/
├── ai/
│   ├── inference/           # ONNXModelBackend, DemoModelBackend, AcceleratorDetector
│   └── preprocessing/       # ImageQualityValidator, dynamic resolution preprocessors
├── backend/
│   ├── app/
│   │   ├── ai/              # Model registry, validator, evaluator, profiler
│   │   ├── api/routes/      # Health, subsystems, vision, fusion, and field history endpoints
│   │   ├── core/            # Config, logging, and error handling
│   │   ├── db/              # SQLite engine, models, and CRUD repositories
│   │   ├── hardware/        # HAL (soil_sensor, camera, battery, detection)
│   │   ├── schemas/         # Pydantic validation models
│   │   └── services/        # Vision pipeline, fusion engine, self-test
│   └── requirements.txt
├── ml/
│   ├── configs/             # tomato_yolo_cls.yaml
│   ├── scripts/             # download, prepare, deduplicate, split, report, profile
│   ├── data/                # raw/, interim/, processed/ (gitignored)
│   ├── train.py             # Reproducible training pipeline
│   ├── evaluate.py          # Held-out test set evaluation & report generator
│   ├── export_onnx.py       # ONNX export utility
│   ├── validate_onnx.py     # Graph structure & numerical validator
│   └── model_hash.py        # SHA-256 model checksum fingerprinting
├── frontend/
│   ├── src/
│   │   ├── components/      # Touchscreen widgets & hardware status bar
│   │   ├── i18n/locales/    # en.json, hi.json, mr.json
│   │   ├── services/        # Axios API client
│   │   └── App.tsx          # 7-inch touch shell
│   └── package.json
├── hardware/
│   └── sensor_protocol/     # Declarative soil_sensor.yaml register template
├── tests/
│   ├── ai/                  # 11 tests: ML pipeline, class map, manifest, ONNX, evaluation
│   ├── backend/             # 70 tests: HAL, Vision, AI gating, DB, APIs, Fusion Engine
│   └── hardware/            # 18 tests: Hardware detection, self-test, diagnostic CLI
├── docs/                    # Complete technical and ML documentation
├── data/
│   ├── models/              # crop_disease_v1.onnx
│   ├── class_map.yaml       # 10 Tomato pathology classes
│   └── dataset_manifest.yaml# Academic dataset provenance & licensing
├── .env.example
└── README.md
```

---

## ⚡ Quickstart

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Backend
```bash
cd backend
python -m pip install -r requirements.txt
python -m app.main
```

### 3. ML Pipeline & Verification
```bash
# Ingest & inspect dataset
python ml/scripts/download_dataset.py
python ml/scripts/inspect_dataset.py
python ml/scripts/check_duplicates.py

# Clean, split, and generate dataset report
python ml/scripts/prepare_dataset.py
python ml/scripts/create_split.py
python ml/scripts/dataset_report.py

# Validate & profile ONNX model
python ml/validate_onnx.py data/models/crop_disease_v1.onnx
python ml/model_hash.py data/models/crop_disease_v1.onnx
python ml/evaluate.py data/models/crop_disease_v1.onnx
python ml/scripts/profile_model.py
```

### 4. Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🧪 Testing Verification

```bash
# Run full automated test suite (99 tests across AI, Backend, and Hardware)
python -m pytest tests/ -v

# Run frontend production build (0 TypeScript errors)
npm --prefix frontend run build
```

---

## 📚 Technical Documentation Index

- `docs/AI_SCOPE.md`: AI vision task definition, 10 Tomato pathology classes, and confidence tiers.
- `docs/DATASET_RESEARCH.md`: Dataset audit (PlantVillage CC BY 4.0 vs PlantDoc wild benchmark).
- `docs/DATA_SPLIT_POLICY.md`: 70/15/15 deterministic partitioning and data leakage prevention.
- `docs/DATASET_REPORT.md`: Statistical distribution report across partitions.
- `docs/MODEL_SELECTION.md`: Lightweight edge classification architecture tradeoffs.
- `docs/MODEL_TRAINING.md`: Training hyperparameters, recipe, and reproducibility protocol.
- `docs/ONNX_DEPLOYMENT.md`: ONNX export, Raspberry Pi CPU fallback, and Hailo-8 AI HAT+ compilation.
- `docs/AI_PERFORMANCE.md`: Measured monotonic host CPU latency breakdown and FPS.
- `docs/MODEL_EVALUATION.md`: Truthful evaluation metrics on held-out test split.
- `docs/REAL_WORLD_VALIDATION_PLAN.md`: 4-phase field validation methodology for real canopy/sunlight.
- `docs/AI_LIMITATIONS.md`: Domain shift, multi-pathology co-infections, and optical failure modes.
- `docs/AI_DEPLOYMENT_STATUS.md`: Complete subsystem verification matrix.
- `docs/AI_COMPLETION_REPORT.md`: Comprehensive engineering completion summary.
