# KrishiDrishti Edge — AI Model Architecture & Export Specification

> **SIH 2026 Prototype Specification**  
> **Rule**: Zero Hardware Hallucination. AI models operate entirely offline on the edge device (Raspberry Pi 5 / Hailo-8 AI HAT+ / CPU fallback).

---

## 1. Overview

KrishiDrishti Edge is engineered for offline edge deployment. In order to ensure safety, auditability, and clear engineering boundaries, the AI engine is structured into two distinct execution modes:

1. **Simulation / Demo Mode (`DEMO_MODE=true`)**:
   - Uses `DemoModelBackend` (`ai/inference/backends.py`) and `DemoVisionModel` (`ai/inference/base.py`).
   - Clearly stamped in all API payloads with `"is_demo": true` and `"model_version": "0.1.0-demo-placeholder"`.
   - Allows judges and testers to demonstrate the UI, confidence gating, pre-processing, and database persistence on laptops or Raspberry Pis before the custom model training cycle finishes.

2. **Real Hardware Mode (`DEMO_MODE=false`)**:
   - Strictly enforces the presence of the physical ONNX/Hailo model file at `MODEL_PATH` (`ai/models/crop_disease_v1.onnx` or `ai/models/crop_disease_v1.hef`).
   - If the trained model file is absent, the engine reports `ready: false`, `model_available: false`, and `status: "ai_unavailable"`.
   - **Zero Hallucination Guarantee**: The system will **never** fabricate fake predictions or assert real model accuracy when running without trained weights.

---

## 2. Model Input & Output Specification

### Input Tensor
- **Shape**: Dynamic resolution read directly from model graph metadata via ONNX Runtime bindings (`[1, 3, H, W]`). Baseline default: `[1, 3, 224, 224]` (Batch Size: 1, Channels: 3 RGB, Height: 224, Width: 224).
- **Data Type**: `float32`
- **Normalization**: Standard ImageNet Z-Score Normalization
  $$\text{Normalized} = \frac{\frac{X}{255.0} - \mu}{\sigma}$$
  - $\mu = [0.485, 0.456, 0.406]$
  - $\sigma = [0.229, 0.224, 0.225]$

### Output Vector
- **Shape**: `[1, N_CLASSES]` (Softmax probability distribution)
- **Data Type**: `float32` in range $[0.0, 1.0]$

---

## 3. Supported Pathology Classes

| Class Index | Disease / Pathology Label | Target Crop | Typical Severity |
|:-----------:|:-------------------------|:------------|:-----------------|
| `0` | Tomato Early Blight (*Alternaria solani*) | Tomato | Medium |
| `1` | Tomato Late Blight (*Phytophthora infestans*) | Tomato | Critical |
| `2` | Potato Late Blight (*Phytophthora infestans*) | Potato | Critical |
| `3` | Cotton Bacterial Blight (*Xanthomonas*) | Cotton | High |
| `4` | Rice Blast (*Magnaporthe oryzae*) | Rice | Critical |
| `5` | Wheat Rust (*Puccinia*) | Wheat | High |
| `6` | Healthy Leaf | Multi-crop | Normal |
| `7` | Unknown / Low Confidence | Any | Gated |

---

## 4. Multi-Tier Confidence Protocol

To protect farmers from misdiagnosis:
- **Configurable Thresholds**: `HIGH_CONFIDENCE_THRESHOLD=0.85` (High), `AI_CONFIDENCE_THRESHOLD=0.70` (Medium).
  *(Note: Thresholds are configurable prototype boundaries, not assertions of definitive Bayesian probability bounds).*
- **Tiers**:
  - `HIGH (>= 0.85)`: Status `accepted`, confidence tier `HIGH`, affirmative farmer advice.
  - `MEDIUM (>= 0.70)`: Status `accepted`, confidence tier `MEDIUM`, visual inspection recommendation.
  - `LOW (< 0.70)`: Status `low_confidence`, diagnosis `"Unknown / Low Confidence"`, advisory: *"Unable to confidently identify the condition. Prediction uncertain. Capture another clear photo with better lighting and focus."*

---

## 5. Acceleration Targets

1. **Raspberry Pi AI HAT+ (Hailo-8 / HailoRT)**:
   - PCIe M.2 connection on Raspberry Pi 5.
   - Target Latency: 15–35 ms per inference.
2. **ARM / x86 CPU Fallback**:
   - Optimized ONNX Runtime with OpenMP.
   - Target Latency: 60–120 ms per inference.
