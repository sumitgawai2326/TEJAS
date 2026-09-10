# KrishiDrishti Edge — SIH Demo Mode & Jury Demonstration Runbook

## Overview
KrishiDrishti Edge provides an explicit, transparent dual-mode runtime architecture for Smart India Hackathon (SIH) demonstrations.

---

## 1. Dual Mode Architecture

### Mode A: Demo Mode (`DEMO_MODE=true`)
- **Purpose**: Demonstrates full UI flows, 7-step guided field check wizard, synthetic leaf image inference, and simulated 6-parameter soil telemetry without requiring live field soil probes or physical camera connection.
- **Visual Disclosures**:
  - UI Header displays pulsing amber badge: `DEMO MODE ACTIVE`.
  - All telemetry cards, scans, and advisories display `(Demo / Simulated)` tags.
  - Model status displays `DEMO_MODEL`.

### Mode B: Real Hardware Mode (`DEMO_MODE=false`)
- **Purpose**: Field deployment with physical USB/CSI cameras and RS485 Modbus-RTU NPK/pH/moisture/temperature soil probes.
- **Zero Hardware Hallucination**:
  - If RS485 probe is disconnected or register map is unconfigured, all soil parameters remain `NULL` (`--`).
  - If ONNX weights are not installed on disk, AI status reports `AI_NOT_READY` and no fake pathology diagnosis is generated.
  - UI Header displays green badge: `REAL HARDWARE MODE`.

---

## 2. Jury Demonstration Script (5-Minute Walkthrough)
1. **Startup & Diagnostics**: Show Diagnostics Tab confirming local host CPU/RAM/Battery metrics, detected serial interfaces, and self-test execution.
2. **7-Step Guided Wizard**:
   - Step 1: Select/Create Field Plot.
   - Step 2: Capture/Upload Crop Leaf Photograph.
   - Step 3: Automated Image Quality Inspection (sharpness & exposure validation).
   - Step 4: AI Pathology Diagnosis with Multi-Tier Confidence Gating.
   - Step 5: 6-Parameter Soil Telemetry Ingestion.
   - Step 6: Multi-Modal Fusion Engine Synthesizing Crop + Soil Risk.
   - Step 7: Prioritized, Multilingual Actionable Farmer Advisories.
3. **Field History Timeline**: View chronological timeline in local offline SQLite.
