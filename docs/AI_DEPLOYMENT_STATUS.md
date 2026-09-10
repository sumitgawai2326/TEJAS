# KrishiDrishti Edge — AI Subsystem Deployment & Verification Status

**Timestamp**: 2026-09-10  
**Target Hardware**: Raspberry Pi 5 (8GB) + Raspberry Pi AI HAT+ (Hailo-8 / 8L)  
**Edge Host**: Offline Edge Unit (Local SQLite + ONNX Runtime / Hailo HAL)  
**Compliance**: Strict Zero Hardware Hallucination & Zero AI Hallucination Invariants

---

## 1. Subsystem Verification Matrix

| Subsystem / Layer | Component / Feature | Current Implementation Status | Validation Truth State |
| :--- | :--- | :--- | :--- |
| **Model Scope** | Tomato 10-class leaf pathology classification | Implemented & Documented | `VALIDATED IN SOFTWARE` |
| **Dataset Provenance** | PlantVillage Tomato subset (CC BY 4.0) | Manifest & License verified | `VERIFIED ACADEMIC SOURCE` |
| **Data Partitioning** | 70% Train / 15% Val / 15% Test ($seed=42$) | Pipeline script & duplicate checker | `DETERMINISTIC & REPRODUCIBLE` |
| **Model Graph** | Lightweight Edge YOLO Classifier (`.onnx`) | Export & structural validation pipeline | `GRAPH VALIDATED (ONNX Opset 17)` |
| **Model Provenance** | SHA-256 graph checksum logging | Cryptographic hash generator | `CRYPTOGRAPHICALLY VERIFIED` |
| **Inference HAL** | `ONNXVisionModel` + `CPUInferenceBackend` | Active in `ai/inference/backends.py` | `ACTIVE & TESTED (CPU Fallback)` |
| **Model Registry** | `ModelRegistry` & dynamic tensor shape discovery | Integrated with backend and SQLite DB | `ACTIVE & INTEGRATED` |
| **Quality Gating** | Blur (Laplacian), Exposure, Glare checks | `ImageQualityValidator` | `ACTIVE & TESTED` |
| **Confidence Gating**| Tiers: HIGH ($\ge 0.85$), MED ($\ge 0.70$), LOW ($< 0.70$)| Backend prediction workflow | `ACTIVE & CONFIGURABLE` |
| **Physical Pi 5 Latency** | Monotonic execution time on BCM2712 CPU | Pipeline ready; awaits physical board | `PENDING PHYSICAL BENCHMARK` |
| **Hailo-8 NPU Inference**| HEF execution on PCIe AI HAT+ | HEF abstraction in place | `PENDING PHYSICAL BENCHMARK` |
| **Field Agronomic Accuracy**| In-situ accuracy under natural canopy & sunlight| Field validation protocol defined | `PENDING FIELD VALIDATION` |
| **Soil Modbus Map** | RS485 Modbus register mapping | `hardware/sensor_protocol/soil_sensor.yaml` | `UNCONFIGURED (SAFEGUARD ACTIVE)` |

---

## 2. Invariant Compliance Audit

### 2.1 Zero Hardware Hallucination
- No synthetic sensor baud rates or fake MODBUS registers have been populated.
- `hardware/sensor_protocol/soil_sensor.yaml` contains explicit `null` register addresses pending real physical sensor datasheet acquisition.
- Hailo-8 and Raspberry Pi 5 FPS/latency numbers are explicitly marked as `PENDING PHYSICAL BENCHMARK` rather than claiming fictitious numbers.

### 2.2 Zero AI Hallucination
- No fake field accuracy (e.g. "99.8% accurate in all conditions") is claimed.
- Model performance metrics distinguish strictly between verified test-split software evaluation and unvalidated in-the-wild agricultural accuracy.
- Any unmeasured metric is explicitly rendered as `"NOT YET VALIDATED"` in accordance with system directives.

---

## 3. Operational Fallback Architecture

```
[Camera Image]
      │
      ▼
[Image Quality Filter] ──(Fails Quality)──► [Quality Rejection Response]
      │
      ▼ (Passes Quality)
[Model Registry / ONNX Runtime]
      │
      ├─► Hailo-8 NPU (If PCIe HAT Present)
      └─► Multi-Core CPU Fallback (If NPU Unavailable)
      │
      ▼
[Confidence Gating]
      ├─► HIGH (>= 0.85)  ──► Confident Advisory + Fusion
      ├─► MED  (>= 0.70)  ──► Tentative Diagnosis + Physical Inspection Warning
      └─► LOW  (< 0.70)   ──► Uncertain Diagnosis + KVK Consultation Prompt
```
