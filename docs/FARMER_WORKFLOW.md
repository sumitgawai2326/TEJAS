# KrishiDrishti Edge — Farmer Workflow Documentation

> **Tagline:** "See. Sense. Predict. Act."  
> **Target Audience:** Smallholder & Commercial Farmers, Field Agronomists, Krishi Vigyan Kendra (KVK) Extension Officers.  
> **Operating Constraint:** 100% Offline, Touch-Optimized, Multilingual (English, Hindi, Marathi).

---

## 1. Guided Field Check Architecture (7 Steps)

KrishiDrishti Edge guides the operator through a sequential, fool-proof 7-step process that eliminates guesswork and prevents data corruption:

```
[ Step 1: Field Selection ]
           ↓
[ Step 2: Crop Leaf Capture / Camera ]
           ↓
[ Step 3: Edge Image Quality Check ]
   ├── If Rejected: Instant guidance (Blur / Dark / Overexposed) -> Retake
   └── If Passed: Proceed -> Preprocessing
           ↓
[ Step 4: Edge AI Inference & Confidence Gating ]
   ├── Confidence >= 0.70: High-confidence pathology diagnosis
   └── Confidence < 0.70: Gated as uncertain / low confidence
           ↓
[ Step 5: 6-Parameter Soil Sensor Reading ]
   ├── N, P, K, pH, Moisture, Soil Temperature
   └── Real Mode: Truthful Modbus RS485 read (NULL if disconnected)
           ↓
[ Step 6: Multi-Modal Fusion & Explainable Risk ]
   ├── Combines AI Vision + Soil Health + Historical Trends
   └── Outputs Explainable Risk Level: LOW / MODERATE / HIGH / CRITICAL / UNKNOWN
           ↓
[ Step 7: Actionable Farmer Advisories & Offline DB Persistence ]
   ├── Generates priority-ordered non-toxic agronomic recommendations
   └── Automatically commits atomic records to local SQLite database
```

---

## 2. Detailed Step Breakdown

### Step 1: Field Selection
- The farmer selects their targeted plot or field from a visual card grid.
- Displays field metadata: Soil classification (e.g., Black Cotton, Red Soil, Alluvial), acreage, and active crop.
- Farmers can create new field plots directly with a one-touch modal.

### Step 2: Crop Leaf Capture
- Touch-first trigger to capture high-resolution imagery using the onboard hardware camera (USB/MIPI-CSI) or upload a photo.
- Displays live preview thumbnail with status indicators.

### Step 3: Edge Image Quality Check
- Evaluates raw image metrics before AI ingestion:
  1. **Blur / Sharpness**: Laplacian variance score (> 100.0 required).
  2. **Exposure / Brightness**: Mean luminance check (40 <= L <= 220 required).
  3. **Resolution**: Minimum pixel dimensions (224 x 224).
- Prevents garbage-in/garbage-out AI hallucinations. Blurry or dark photos are stopped immediately with clear visual feedback and a "Retake Photo" button.

### Step 4: Offline Edge AI Inference & Confidence Gating
- Processes the normalized 224 x 224 x 3 tensor through the local model backend (Hailo-8 / ONNX / CPU).
- Runs confidence gating (0.70 default threshold):
  - If confidence < 0.70, the UI shows an explicit warning: *"AI result is uncertain (< 70% threshold). Proceeding with caution."*

### Step 5: 6-Parameter Soil Sensor Telemetry
- Reads exact 6 soil parameters over RS485 Modbus-RTU:
  - Nitrogen ($N$) in $\text{mg/kg}$
  - Phosphorus ($P$) in $\text{mg/kg}$
  - Potassium ($K$) in $\text{mg/kg}$
  - Soil $\text{pH}$
  - Volumetric Soil Moisture ($\%$)
  - Soil Temperature ($^\circ\text{C}$)
- **Zero Hardware Hallucination**: If the probe is unattached or Modbus registers are unconfigured in real mode, the UI displays clear disconnected state with `NULL`/`--` values without inventing synthetic readings.

### Step 6: Multi-Modal Crop + Soil Fusion
- Synthesizes optical pathology with chemical/physical soil stressors and historical field trajectories.
- Displays the synthesized Field Risk Level with clear badges:
  - **LOW**: Green
  - **MODERATE**: Yellow/Amber
  - **HIGH**: Orange/Rose
  - **CRITICAL**: Red
  - **UNKNOWN**: Slate (Missing critical sensor data)
- Lists explainable evidence cards detailing *why* the risk was computed.

### Step 7: Actionable Farmer Advisories & Persistence
- Presents clear, prioritized agronomic actions (URGENT, HIGH, MEDIUM, LOW).
- Focuses on immediate, actionable steps (e.g. bio-fungicides, irrigation scheduling, balanced nutrient correction, organic soil amendments).
- Persists all scans, readings, risk assessments, and advisories to the local offline SQLite database (`data/krishidrishti.db`) for chronological timeline review.

---

## 3. Multilingual Support

The UI natively supports instant runtime language switching with zero network overhead:
1. **English (en)**
2. **Hindi (hi — हिन्दी)**
3. **Marathi (mr — मराठी)**

All labels, technical descriptions, diagnostic cards, and button texts are stored in structured JSON dictionaries (`frontend/src/i18n/locales/`).
