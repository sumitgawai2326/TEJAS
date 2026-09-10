# KrishiDrishti Edge — UI/UX Design System

> **Tagline:** "See. Sense. Predict. Act."  
> **Philosophy:** Touch-Optimized, High-Contrast Outdoor Readability, Offline-First, Zero-Friction Farmer Journey.

---

## 1. Design Principles

1. **Rugged Field Readability**:
   - Dark Slate palette (`#020617`, `#0f172a`, `#1e293b`) minimizing battery drain on OLED field displays and eliminating glare under sunlight.
   - High-contrast typography with emerald (`#10b981`), cyan (`#06b6d4`), amber (`#f59e0b`), and rose (`#f43f5e`) accent signifiers.

2. **Touch-First Ergonomics**:
   - Minimum tap target size: 48px height for all primary buttons and controls.
   - Large tactile wizard progression buttons for gloved or field operation.

3. **Zero Hardware Hallucination Transparency**:
   - Distinct badges distinguishing `DEMO SIMULATION` mode from `REAL HARDWARE` mode.
   - Distinct labels for unattached hardware (`DISCONNECTED`, `CAMERA_UNAVAILABLE`, `UNCONFIGURED_REGISTER_MAP`) rather than displaying default synthetic zeros or fake values.

4. **Multi-Modal Synchronicity**:
   - Dedicated views for individual sensor probes (Camera, 6-Parameter RS485 Soil) alongside the unified multi-modal fusion dashboard.

---

## 2. Information Architecture & Navigation

The interface provides 10 purpose-built screens accessible via the primary navigation sidebar/drawer:

| Tab | Key | Description |
|---|---|---|
| **Overview** | `home` | System dashboard, live hardware diagnostic telemetry, quick field check trigger. |
| **Field Check Wizard** | `wizard` | 7-step guided workflow: Field $\to$ Leaf Photo $\to$ Quality Gate $\to$ Edge AI $\to$ Soil $\to$ Fusion $\to$ Advisory. |
| **Field Management** | `fields` | Visual plot cards, soil classification, acreage, crop assignment, creation modal. |
| **Leaf Scanner** | `scanner` | Standalone camera viewfinder, image upload, blur/exposure validation, pathology classifier. |
| **6-Param Soil Sensor** | `soil` | Real-time telemetry for $N$, $P$, $K$, $\text{pH}$, Moisture, and Temperature. |
| **Field Risk Analysis** | `risk` | Multi-modal risk index, explainability evidence feed, data completeness ratio. |
| **Farmer Advisories** | `advisory` | Priority-ranked agronomic recommendations and corrective actions. |
| **Field Timeline** | `history` | Chronological event stream of scans, soil readings, and advisories with category filters. |
| **Hardware Diagnostics** | `diagnostics` | Real-time health matrix for Camera, RS485 Soil Sensor, AI Accelerator, and SQLite. |
| **System Settings** | `settings` | Operating mode toggles, offline database statistics, driver configurations. |

---

## 3. Real-Time Telemetry Bar

The top header bar delivers persistent, glanceable hardware diagnostics at all times:
- **Offline Edge AI Status**: Verifies local-only execution with zero internet connectivity.
- **Hardware Mode Badge**: Dynamic toggle status (`REAL HARDWARE` vs. `DEMO SIMULATION`).
- **Battery Status & Level**: Real battery percentage, charging state, or mock state indicator.
- **CPU & RAM Utilization**: Dynamic core telemetry and thermals.
- **One-Touch Language Switcher**: Instant switching between English, हिन्दी (Hindi), and मराठी (Marathi).
