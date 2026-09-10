# KrishiDrishti Edge — AI Model Scope, Assumptions & Limitations

**Version**: 1.0.0  
**Target Crop**: Tomato (*Solanum lycopersicum*)  
**Architecture**: Lightweight Edge Vision Classifier (YOLO / MobileNet ONNX)  
**Status**: Real Model Pipeline (Zero AI Hallucination Policy)

---

## 1. Executive Summary

KrishiDrishti Edge provides localized, real-time, offline computer vision inference for 10 tomato leaf health classes directly on edge devices (Raspberry Pi 5 + Hailo-8 AI HAT / CPU). While this provides low-latency diagnostics in disconnected rural environments, agricultural edge vision has fundamental biological, environmental, and algorithmic boundaries.

This document explicitly defines the operational boundaries, failure modes, assumptions, and limitations of the vision subsystem.

---

## 2. Fundamental Agricultural Limitations

### 2.1 Lab vs. Field Domain Shift
- **Lab Data Bias**: Baseline training models trained on uniform datasets (such as PlantVillage) feature detached leaves photographed against solid gray/black/white backgrounds under diffuse artificial lighting.
- **Field Realities**: Real field imagery captured by farmers or edge cameras exhibits dynamic direct sunlight, heavy shadows, variable focus, soil/mulch background clutter, wet leaves with water droplets, and leaf flutter due to wind.
- **Mitigation**: Edge confidence gating rejects out-of-distribution frames (confidence $< 0.70$), image quality checks enforce sharpness/lighting filters prior to inference, and PlantDoc wild-benchmarking is integrated into the validation roadmap.

### 2.2 Single-Label vs. Multi-Pathology Co-Infections
- **Single-Label Constraint**: The current model uses categorical single-label classification with a softmax output layer ($\sum p_i = 1$).
- **Biological Reality**: Plants in the field frequently suffer from simultaneous co-infections (e.g., *Alternaria solani* Early Blight alongside *Septoria lycopersici* Leaf Spot, or viral infection accompanied by secondary fungal colonization).
- **Behavior**: The model will only predict the visually dominant pattern. It cannot output multi-label lesion co-occurrence in v1.

### 2.3 Early-Stage & Latent Infections
- **Macroscopic Symptom Dependency**: Computer vision relies on visible morphological changes (chlorosis, necrosis, halo lesions, mosaic mottling, curling).
- **Latent Incubation**: Pathogens during early incubation periods (prior to macroscopic symptom expression) cannot be detected by RGB vision.
- **Mitigation**: Multi-modal fusion with soil moisture, temperature, and electrical conductivity provides environmental disease risk indexes even when visual symptoms are early or absent.

### 2.4 Nutritional Deficiency vs. Disease Mimicry
- **Visual Overlap**: Nutrient deficiencies frequently mimic fungal or viral symptoms:
  - Potassium deficiency mimics marginal necrosis similar to bacterial speck/spot.
  - Nitrogen deficiency produces general chlorosis similar to early yellow leaf curl or mold.
  - Magnesium deficiency produces interveinal chlorosis resembling viral mottles.
- **Mitigation**: The KrishiDrishti Fusion Engine cross-references visual predictions against soil electrical conductivity and NPK parameters to eliminate false visual alerts.

---

## 3. Optical & Environmental Limitations

| Factor | Failure Mode | System Safeguard |
| :--- | :--- | :--- |
| **Severe Motion Blur** | Soft focus masks fine texture (e.g. *Septoria* black pycnidia) | Laplacian variance check ($> 100.0$) in `ImageQualityValidator` |
| **Underexposure / Darkness** | Low SNR, loss of chromatic contrast | Mean luminance check ($> 40.0$) |
| **Direct Solar Glare** | Saturated white pixels, washed-out color | Saturated pixel percentage ceiling ($< 15\%$) |
| **Off-Target Subjects** | Sticks, weed foliage, hands, soil | Low maximum softmax confidence triggering `"UNRECOGNIZED_PATTERN"` fallback |

---

## 4. Operational & Agronomic Advisory Safeguards

1. **Advisory is Decision Support, Not Autonomous Treatment**: Model outputs must never trigger automatic irreversible chemical sprayers without human verification.
2. **Confidence-Gated Communication**:
   - **HIGH ($\ge 0.85$)**: Specific targeted chemical/organic recommendations presented to farmer.
   - **MEDIUM ($0.70 - 0.84$)**: Tentative diagnosis displayed with explicit instruction to inspect further and monitor.
   - **LOW ($< 0.70$)**: Flagged as `"UNCERTAIN"`; advises capturing clearer images or consulting a local Krishi Vigyan Kendra (KVK) agronomist.
3. **Multilingual Clarity**: Warnings are displayed in plain language (English, Hindi, Marathi) emphasizing physical leaf inspection.
