# KrishiDrishti Edge — Agronomic Knowledge Base & Policy

> **Knowledge Structure & Zero Agronomic Hallucination Protocol**

---

## 1. Zero Hallucination Protocol

Agricultural advice directly impacts farmers' livelihoods, crop yields, and soil health. In accordance with strict engineering safety policies:
- **No Invented Scientific Citations**: No fake papers, fabricated university research, or ungrounded statistics are cited.
- **No Hardcoded Soil Thresholds in Python**: Reference ranges must reside in external configuration (`backend/app/services/fusion/knowledge/agronomic_rules.yaml`).
- **Unconfigured Rules Remain Disabled**: All parameters default to `enabled: false` with reason `"Reference threshold not configured."` until verified by localized agro-climatic datasheets.

---

## 2. Agronomic Configuration Schema

```yaml
crops:
  tomato:
    growth_stages:
      - seedling
      - vegetative
      - flowering
      - fruiting
      - harvesting
    parameters:
      soil_moisture:
        enabled: false
        unit: "%"
        min: null
        max: null
        source: "UNCONFIGURED_TEMPLATE"
        reason: "Reference threshold not configured for local agro-climatic zone."
```

---

## 3. Safe Extension Protocol for Localized Deployment

When deploying KrishiDrishti Edge to a specific state or agro-climatic zone (e.g. Maharashtra Black Cotton Soil Zone):
1. Obtain official state agricultural university guidelines (e.g. MPKV Rahuri / ICAR).
2. Populate `min` and `max` values in `agronomic_rules.yaml`.
3. Set `enabled: true` and specify the exact institutional citation in `source`.
4. Run automated test suite to ensure parameter evaluations trigger accurately without regressing safety invariants.
