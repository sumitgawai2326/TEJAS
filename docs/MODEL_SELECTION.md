# KrishiDrishti Edge — AI Model Selection & Edge Architecture Trade-Offs (Phase H)

## 1. Objective
Select an optimal, lightweight computer vision architecture for whole-image Tomato leaf pathology classification deployable on a Raspberry Pi 5 with CPU execution provider or Hailo-8 AI acceleration.

---

## 2. Model Architecture Comparison

| Model Architecture | Parameter Count | Float32 Model Size | CPU Latency (est.) | Hailo-8 Target | Edge Memory Footprint | Primary Suitability |
|---|---|---|---|---|---|---|
| **YOLOv8n-cls / YOLO11n-cls (Nano)** | **~1.5M - 2.0M** | **~5.5 - 7.5 MB** | **~35 - 55 ms** | **~4 - 8 ms** | **Low (< 150 MB)** | **Primary Baseline (Recommended)** |
| **YOLOv8s-cls / YOLO11s-cls (Small)** | ~5.0M - 6.5M | ~20 - 25 MB | ~85 - 140 ms | ~12 - 18 ms | Medium (~300 MB) | Secondary (Fallback if Nano lacks capacity) |
| **MobileNetV3-Small** | ~2.5M | ~9.5 MB | ~45 - 65 ms | N/A | Low (< 180 MB) | Strong alternative |
| **ResNet-50** | ~25.6M | ~98 MB | ~350 - 600 ms | ~25 ms | High (> 800 MB) | Not edge recommended |

---

## 3. Decision & Rationale
1. **Primary Model Choice**: **YOLO Nano Classification (`yolo11n-cls` or `yolov8n-cls`)**
   - **Compactness**: With $\sim 1.5\text{M}$ parameters and $< 8\text{MB}$ ONNX file size, it fits easily in cache and local edge memory.
   - **CPU Fallback Responsiveness**: Under 60 ms inference latency on ARM Cortex-A76 (Raspberry Pi 5) ensures fluid touch UI interaction even when physical accelerator HAT is detached.
   - **ONNX Compatibility**: Seamless official export mechanism via Ultralytics without custom unsupported operators.
2. **Progression Strategy**: Start with Nano. Benchmark against the held-out test split. Only scale up to Small if Nano validation metrics demonstrate severe capacity limitations on multi-disease discrimination.
