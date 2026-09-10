# KrishiDrishti Edge — AI Model Scope & Task Definition (Phase B)

## 1. Scope Summary
- **Target Crop**: **Tomato** (*Solanum lycopersicum*)
- **AI Task**: **Whole-Image Multi-Class Pathology Classification**
- **Deployment Target**: Raspberry Pi 5 + Raspberry Pi AI HAT+ (Hailo-8) / CPU Execution Provider Fallback
- **Portable Model Format**: **ONNX (Open Neural Network Exchange)**

---

## 2. Task Specification: Whole-Image Classification (v1)

> [!IMPORTANT]
> **This is NOT object detection in v1.**
> The model does not produce bounding box coordinates.
> The model directly answers the fundamental agronomic question:
> **"What tomato leaf health or disease class does this image belong to?"**

### Input Definition
- **Data Modality**: 2D RGB Photographic Image of a single or cluster of Tomato leaves.
- **Acquisition Source**: Attached USB/CSI camera HAL or direct upload via farmer touch UI.
- **Dynamic Resolution**: Scaled and padded dynamically according to target model graph metadata (standard baseline: $224 \times 224 \times 3$).

### Output Definition
- **Primary Output**: Top-1 predicted pathology class label (e.g., `Tomato Early Blight`).
- **Confidence Metric**: Softmax probability score $\in [0.0, 1.0]$.
- **Top-$k$ Distribution**: Ranked probability vector over all registered target classes for explainability.

---

## 3. Multi-Tier Confidence Architecture

The system enforces three operational confidence tiers mapped to explicit farmer actionability:

| Confidence Tier | Prototype Threshold | System Interpretation | Farmer Guidance |
|---|---|---|---|
| **`HIGH`** | $\text{Confidence} \ge 0.85$ | Strong visual feature match with validated training patterns | Condition identified with high confidence. Review recommended cultural and agronomic practices. |
| **`MEDIUM`** | $0.70 \le \text{Confidence} < 0.85$ | Moderate feature match; symptom overlaps possible | Moderate model confidence. Visually inspect crop canopy, verify moisture levels, and monitor progression. |
| **`LOW`** | $\text{Confidence} < 0.70$ | Gated below diagnostic safety threshold | Diagnosis gated to prevent false alarms. Capture another focused photograph with better lighting. |

*Note: Thresholds (0.85 and 0.70) are configurable prototype boundaries and are not asserted as definitive Bayesian probability limits.*
