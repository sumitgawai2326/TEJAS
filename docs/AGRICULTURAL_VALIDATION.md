# KrishiDrishti Edge — Agricultural Domain Validation & Pathological Scope

## Overview
KrishiDrishti Edge provides localized agronomic decision support. To ensure responsible AI deployment in agricultural settings, the scope, capabilities, and boundaries of the AI vision model are explicitly documented.

---

## 1. Supported Agricultural Pathology Classes (Target Scope)
The edge vision subsystem is designed around major staple and cash crops common in Indian agriculture:
1. **Tomato Early Blight** (*Alternaria solani*)
2. **Tomato Late Blight** (*Phytophthora infestans*)
3. **Potato Late Blight** (*Phytophthora infestans*)
4. **Cotton Bacterial Blight** (*Xanthomonas citri*)
5. **Rice Blast** (*Magnaporthe oryzae*)
6. **Wheat Rust** (*Puccinia striiformis / graminis*)
7. **Healthy Crop Canopy** (Normal leaf tissue)

---

## 2. Multi-Modal Agricultural Safeguards
Vision signals are not interpreted in isolation. The system enforces multi-modal cross-verification:
- **Soil Context Gating**: Fungal and water-stress symptoms are evaluated alongside volumetric soil moisture and soil pH.
- **Image Quality Pre-Filtering**: Blurry, overexposed, or corrupt leaf images are rejected before entering inference.
- **Multi-Tier Confidence Protocol**:
  - `HIGH (>= 0.85)`: Strong visual alignment with trained pathology patterns.
  - `MEDIUM (>= 0.70)`: Moderate visual alignment; system flags visual inspection advice.
  - `LOW (< 0.70)`: Diagnosis gated; farmer instructed to capture fresh focused photo.

---

## 3. Responsible Agronomic Guidance
- Advisories never recommend dangerous or unverified chemical concoctions.
- Advisories focus on cultural practices, canopy aeration, irrigation adjustments, and recommendation to consult local Krishi Vigyan Kendra (KVK) extension officers.
