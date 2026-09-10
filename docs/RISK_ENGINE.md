# KrishiDrishti Edge — Explainable Multi-Modal Risk Engine

> **Risk Assessment & Evidence Scoring Specification**

---

## 1. Overview

The **Risk Engine** (`backend/app/services/fusion/risk_engine.py`) synthesizes multi-modal observations into an explainable crop and field health assessment.

---

## 2. Risk Levels & Definitions

| Risk Level | Trigger Condition | Primary Meaning | Farmer Impact |
|:-----------|:------------------|:----------------|:--------------|
| **CRITICAL** | Severe pathology (e.g. Late Blight, Rice Blast) or multiple concurrent severe stresses. | Imminent crop loss potential if unmanaged. | Immediate field quarantine and expert intervention required. |
| **HIGH** | Active disease detected (e.g. Early Blight, Rust) with high confidence ($P \ge 0.70$). | Noticeable symptom spread. | Targeted pruning, canopy airflow, daily monitoring. |
| **MODERATE** | Mild stress, sub-optimal soil moisture, or persistent unclassified leaf symptoms. | Potential developing stress. | Adjust irrigation/drainage, re-evaluate within 48h. |
| **LOW** | Healthy leaf tissue confirmed with high confidence; normal soil telemetry. | Field operating in optimal baseline conditions. | Routine maintenance and weekly soil sampling. |
| **UNKNOWN** | Insufficient data (missing vision scan, missing soil telemetry, or low AI confidence). | Not enough reliable data to determine risk. | Establish baseline observation; no false assumptions made. |

---

## 3. Data Completeness Calculation

Data completeness represents the fraction of reliable edge intelligence available:
$$\text{Completeness} = 0.45 \times \mathbb{I}(\text{Vision Valid}) + 0.35 \times \left(\frac{N_{\text{available parameters}}}{6}\right) + 0.20 \times \mathbb{I}(\text{History Sufficient})$$

- If $\text{Completeness} < 0.35$ and no confident vision detection exists:
  $$\text{Risk Level} \leftarrow \text{UNKNOWN}, \quad \text{Score} \leftarrow \text{null}$$

---

## 4. Prototype Heuristic Disclaimer

> [!NOTE]
> Scoring weights in `backend/app/services/fusion/knowledge/risk_config.yaml` are configuration-driven prototype heuristics designed for hackathon demonstration. They are explicitly tagged in all API responses as `is_prototype_heuristic: true` and must not be presented as certified agronomic science without institutional validation.
