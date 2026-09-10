# KrishiDrishti Edge — SIH Technical Claims & Engineering Disclosures

## Statement of Engineering Honesty
KrishiDrishti Edge adheres to absolute technical transparency. We explicitly distinguish between **implemented, verified engineering features** and **future field calibration milestones**.

---

## 1. Verified & Proven System Capabilities
| Subsystem | Implemented Capability | Status |
|---|---|---|
| **Edge Hardware HAL** | Cross-platform hardware detection (Raspberry Pi 5 / x86 Workstation), CPU temp, battery PMIC monitoring, serial/RS485 auto-discovery | **VERIFIED** |
| **RS485 Modbus Driver** | Configurable template driver (`soil_sensor.yaml`), CRC-16 checksums, strictly nullable fallback upon disconnection | **VERIFIED** |
| **Offline SQLite DB** | Full relational schema (Farms, Fields, Crops, Scans, SoilReadings, Risks, Advisories, Events) with WAL mode and PRAGMA FKs | **VERIFIED** |
| **Image Quality Hal** | Laplacian variance sharpness testing, luminance histograms, minimum resolution checks | **VERIFIED** |
| **AI Inference HAL** | Hailo-8 / CPU execution provider fallback abstraction, dynamic shape support, multi-tier confidence gating | **VERIFIED** |
| **Model Registry** | SHA-256 binary hash auditability, dynamic tensor dimension resolution, status tracking | **VERIFIED** |
| **Pipeline Profiler** | Monotonic timing (`time.perf_counter()`) across decode, preprocess, inference, and postprocess stages | **VERIFIED** |
| **Multi-Modal Fusion** | Rule-based explainable risk synthesis combining vision, soil, and temporal trend delta analysis | **VERIFIED** |
| **Offline UI** | Touch-first responsive React + TypeScript + Tailwind UI with English, Hindi, and Marathi translations | **VERIFIED** |

---

## 2. Explicit Engineering Invariants & Boundaries
- **Soil Sensor Registers**: The registers in `hardware/sensor_protocol/soil_sensor.yaml` remain unconfigured (`null`) pending acquisition of the specific sensor datasheet. No arbitrary register map is hallucinated.
- **AI Model Accuracy Claims**: Without a finalized, verified on-disk agricultural model and test split, model validation status is explicitly reported as `"NOT YET VALIDATED"`.
- **Confidence Thresholds**: Thresholds (0.85 and 0.70) are configurable prototype thresholds, not claims of definitive Bayesian probability bounds.
