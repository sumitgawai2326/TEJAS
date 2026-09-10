# Hardware Integration Architecture — KrishiDrishti Edge

> **Tagline:** "See. Sense. Predict. Act."  
> **Topology:** Edge-Native Heterogeneous Computing & Sensor Fusion

---

## 1. Physical Hardware Interconnect Block Diagram

```
                             ┌──────────────────────────────────┐
                             │       Raspberry Pi 5 (SBC)       │
                             │                                  │
                             │  - Linux 64-bit OS               │
                             │  - FastAPI REST Backend          │
                             │  - React / Vite UI Kiosk         │
                             │  - Local SQLite Database         │
                             └────────┬───────┬───────┬─────────┘
                                      │       │       │
             ┌────────────────────────┘       │       └────────────────────────┐
             │ (16-pin PCIe Gen 3)            │ (USB 3.0 Host)                 │ (CSI / USB)
             ▼                                ▼                                ▼
  ┌──────────────────────┐        ┌───────────────────────┐        ┌──────────────────────┐
  │ Raspberry Pi AI HAT+ │        │ USB-to-RS485 Adapter  │        │ Camera Subsystem     │
  │   (Hailo-8 NPU)      │        │  (FTDI / CH340 Chip)  │        │ (V4L2 / CSI Module)  │
  │                      │        └───────────┬───────────┘        └──────────┬───────────┘
  │ - Low-latency NPU    │                    │ (RS485 Differential A/B)      │
  │ - 26 TOPS Compute    │                    ▼                               ▼
  │ - Local INT8 Models  │        ┌───────────────────────┐        ┌──────────────────────┐
  └──────────┬───────────┘        │   6-Parameter Soil    │        │ Leaf Optical Image   │
             │                    │     Sensor Probe      │        │  (224x224 RGB Tensor)│
             │                    │                       │        └──────────┬───────────┘
             │                    │ - Nitrogen (N)        │                   │
             │                    │ - Phosphorus (P)      │                   │
             │                    │ - Potassium (K)       │                   │
             │                    │ - Soil pH             │                   │
             │                    │ - Soil Moisture       │                   │
             │                    │ - Soil Temperature    │                   │
             │                    └───────────┬───────────┘                   │
             │                                │                               │
             ▼                                ▼                               ▼
       [ NPU Vision ]                 [ Soil Telemetry ]             [ Image Quality ]
             └────────────────────────────────┼───────────────────────────────┘
                                              │
                                              ▼
                             ┌──────────────────────────────────┐
                             │  Multi-Modal Fusion Engine       │
                             │                                  │
                             │  - Agronomic Heuristic Evaluator │
                             │  - Temporal Trend Delta Engine   │
                             │  - Multi-Factor Risk Assessment  │
                             │  - Actionable Farmer Advisories  │
                             └────────────────┬─────────────────┘
                                              │
                                              ▼
                             ┌──────────────────────────────────┐
                             │  Local SQLite Persistence        │
                             │   (data/krishidrishti.db)        │
                             └──────────────────────────────────┘
```

---

## 2. Subsystem Interfaces & Protocols

| Subsystem | Physical Bus | Protocol / Transport | HAL Driver | Fallback Behavior |
|---|---|---|---|---|
| **AI Accelerator** | PCIe Gen 3 $\times 1$ | HailoRT PCIe Driver (`/dev/hailo0`) | `AcceleratorDetector` | High-performance CPU Fallback |
| **Soil Sensor** | USB $\to$ Differential RS485 | Modbus-RTU Master/Slave | `ModbusSoilSensor` | Truthful `SENSOR_DISCONNECTED` / `UNCONFIGURED` |
| **Camera** | MIPI CSI-2 / USB UVC | V4L2 / libcamera (`/dev/video0`) | `CameraHAL` | File Upload & Viewfinder Fallback |
| **Local Storage** | MicroSD / NVMe PCIe | SQLite WAL Engine | `SQLAlchemy` ORM | Read-only error containment |
| **Touch Display** | DSI / Micro-HDMI | Wayland / X11 Chromium Kiosk | Modern React SPA | Keyboard / Mouse navigation |
