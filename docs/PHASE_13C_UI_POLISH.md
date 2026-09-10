# TEJAS — Phase 13C: UI / Presentation Polish

**Project Name**: TEJAS  
**Full Form**: Technology Enabled Judicious Agriculture And soil sensor  
**Date**: September 2026  
**Status**: COMPLETE  
**Primary Color Theme**: Dark Forest Green Navigation (`#0a1f14` / `#0f2d21`), Light Cream/Off-White Viewport (`#f6f8f6`), Crisp White Content Cards (`#ffffff`), Emerald Green Accents (`#059669` / `#10b981`)

---

## 1. Overview & Objective

Phase 13C focused strictly on frontend UI/UX elevation and presentation polish for the **TEJAS** edge platform to ensure optimal legibility, professional visual balance, and intuitive navigation during Smart India Hackathon (SIH) jury evaluations on laptops, touchscreens, and overhead projectors.

All underlying AI models, OpenCV DNN ONNX pipelines, zero-hallucination protocols, and database structures remain strictly preserved without alteration.

---

## 2. Visual Architecture & Design System

### 2.1 Theme Hierarchy & Color Palette
- **Top Embedded Hardware Header (`bg-[#0a1f14]` / `border-[#18452e]`)**:
  - High-contrast `TEJAS` brand badge with emerald glow.
  - Distinct `DEMO / SIMULATION MODE` (Amber) vs `REAL HARDWARE MODE` (Emerald) pill tags.
  - Hardware host telemetry (CPU %, RAM %, Temperature, Battery %).
  - One-touch language selector (`EN`, `हिंदी`, `मराठी`) with active emerald fill.
- **Left Navigation Sidebar (`bg-[#0f2d21]` / `border-[#1a4733]`)**:
  - Dark forest green container providing strong grounding on screen.
  - Active tab elevation with emerald highlight and soft drop-shadow.
  - Direct quick-access to Guided Field Check Wizard, Standalone Scanner, 6-Param Soil Module, Multi-Modal Risk, Advisories, Timeline, and Hardware Diagnostics.
- **Main Viewport Workspace (`bg-[#f6f8f6]` / `text-slate-800`)**:
  - Soft cream/off-white background tailored for projector legibility and high contrast in ambient room lighting.
  - Clean typographic hierarchy with dark slate headers (`#0f172a`), muted secondary captions (`#64748b`), and crisp borders (`#e2e8f0`).
- **Content Cards (`bg-white` / `rounded-2xl` / `shadow-sm` / `border-slate-200`)**:
  - Structured modular cards for diagnostic metrics, disease predictions, telemetry gauges, and agronomic advisories.

---

## 3. Screen-by-Screen Enhancements

### 3.1 Home Dashboard (`home`)
- **Primary Hero Banner**: Elevated gradient action container prominently displaying `"START GUIDED FIELD CHECK"` with descriptive edge workflow summary.
- **Live Hardware Diagnostic Matrix**: 4 distinct status cards for Camera Subsystem, 6-Parameter Soil Sensor, Edge AI Accelerator, and Offline SQLite DB.
- **Quick Shortcuts**: One-click jump cards to Fields, 6-Param Soil Probe, and Field Timeline.

### 3.2 Guided Field Check Wizard (`wizard` — 7 Steps)
- **Step Progress Bar**: Top-level 7-step tracker with numbered pill badges, checkmarks, and active step highlighting.
- **Step 1 (Target Field)**: Interactive plot selector grid with active checkmark indicators and modal for registering new plots.
- **Step 2 (Leaf Capture)**: Quick-select bar containing 10 curated test leaves (`Bacterial Spot`, `Early Blight`, `Healthy`, `Late Blight`, `Yellow Leaf Curl`, etc.), live viewfinder preview, camera capture button, and file upload fallback.
- **Step 3 (Image Quality)**: Automated focus blur assessment, exposure luminance check, and resolution validation with pass/warning banners.
- **Step 4 (AI Disease Diagnosis)**: Top-1 predicted pathology class banner, confidence progress bar, Top-3 ranked probability distributions, inference device & latency metadata, and Responsible AI disclaimer.
- **Step 5 (6-Param Soil Telemetry)**: 6 modular metric cards ($N, P, K, \text{pH}, \text{Moisture}, \text{Temp}$) with clear units, live/simulated tags, and re-read trigger.
- **Step 6 (Multi-Modal Fusion)**: Overall field risk level badge (`CRITICAL`, `HIGH`, `MODERATE`, `LOW`), composite explanation, disease risk vs soil stress scores, and data completeness metric.
- **Step 7 (Actionable Advisories)**: Prioritized agronomic recommendations (`URGENT`, `HIGH`, `NORMAL`) with distinct observation notes and actionable guidance boxes.

### 3.3 Standalone Crop Scanner (`scanner`)
- Dedicated rapid-testing screen with target plot selector, one-touch sample leaf buttons, live input dimension display, OpenCV DNN inference engine stats, and Top-3 prediction bars.

### 3.4 6-Parameter Soil Intelligence Module (`soil`)
- 6 large parameter telemetry cards ($mg/kg$, $pH$, $\%$, $^\circ C$) with explicit `Live RS485` or `Simulated (DEMO_MODE)` indicators.

### 3.5 Multi-Modal Risk & Explainable Evidence (`risk`)
- Multi-signal risk synthesis with visual breakdown of Vision pathology, Soil nutrient levels, and historical plot records.

### 3.6 Personalized Agronomic Advisories (`advisory`)
- Non-toxic, practical agronomic advice categorized by urgency with clean green action callout containers.

### 3.7 Historical Timeline (`history`)
- Chronological event logs with category filter pills (`ALL`, `SCAN`, `SOIL`, `RISK`, `ADVISORY`), color-coded icons, timestamps, and confidence scores.

### 3.8 System Diagnostics & Settings (`diagnostics` & `settings`)
- Host platform info (OS, Kernel, CPU Temp, Storage, PMIC), detected RS485 serial ports, one-click hardware self-test suite, and active AI model registry verifying SHA-256 integrity.

---

## 4. Verification & Validation Summary

1. **Frontend Production Build**:
   - `tsc && vite build` &rarr; 0 TypeScript or bundling errors. Output: `dist/assets/index-GywFBXyO.js` (295 kB).
2. **Backend Automated Tests**:
   - `pytest tests/ -v` &rarr; **130 passed in 9.64s** (0 failures).
3. **Model Integrity**:
   - File: `data/models/tejas_tomato_yolo11n.onnx`
   - Checksum: `C988AC480A2595EB4ED96C1AAEFFB7BAE33CCF5418639C8AEA9AD7D70128944E` (100% verified & intact).
