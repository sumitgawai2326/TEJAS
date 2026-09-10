# KrishiDrishti Edge — Actionable Agronomic Advisory Engine

> **Farmer-Centric Guidance & Multilingual Advisory Rules**

---

## 1. Design Principles

1. **Safety First (Zero Chemical / Toxic Fabrication)**:
   - The engine **never** invents arbitrary chemical formulations, pesticide quantities, or fertilizer doses without an explicit, scientifically validated agronomic rule.
   - For severe/unsupported conditions, guidance safely directs farmers to consult local agricultural universities or Krishi Vigyan Kendra (KVK) extension officers.
2. **Clear Separation of Observation vs. Action**:
   - Every advisory item clearly states what was observed (e.g. *"Leaf symptoms indicate presence of Early Blight"*), the reason, and the recommended farmer action.
3. **Multilingual Architecture**:
   - Advisories are tagged with standard localization keys (`ADVISORY_PATHOLOGY_CRITICAL`, `ADVISORY_SOIL_UNAVAILABLE`, `RISK_INSUFFICIENT_DATA`) for seamless translation into English, Hindi, and Marathi.

---

## 2. Advisory Priority Levels

- **URGENT**: High-impact, rapid-spread crop pathologies (e.g. Late Blight). Requires immediate physical isolation.
- **HIGH**: Treatable fungal diseases, significant soil moisture deficits.
- **MEDIUM**: Sub-optimal soil moisture/pH, unclear camera captures requiring retakes.
- **LOW**: Canopy maintenance, routine weeding.
- **INFO**: General monitoring, baseline data recording, partial sensor diagnostics.

---

## 3. Sample Generated Advisories

### Example 1: Critical Pathology Alert
- **Title**: Pathology Alert: Tomato Late Blight
- **Priority**: `URGENT`
- **Observation**: High-severity crop disease 'Tomato Late Blight' identified on leaf sample.
- **Recommended Action**: Isolate affected foliage, inspect surrounding plants for water-soaked lesions, avoid overhead irrigation, and consult local Krishi Vigyan Kendra (KVK) or extension officer.
- **Source**: `AI_OBSERVATION`

### Example 2: Soil Sensor Hardware Disconnect
- **Title**: Soil Probe Disconnected
- **Priority**: `MEDIUM`
- **Observation**: No live soil parameters received from RS485 Modbus link.
- **Recommended Action**: Ensure the USB-RS485 adapter is inserted and probe metal prongs are firmly embedded in moist soil.
- **Source**: `DATA_QUALITY_CHECK`
