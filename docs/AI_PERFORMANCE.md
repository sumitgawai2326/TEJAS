# KrishiDrishti Edge — AI Subsystem Latency & Performance Profile

**Benchmark Date**: 2026-09-09 19:20:40 UTC  
**Execution Environment**: Host CPU Benchmark (`OpenCV DNN / CPU (Host Test Environment)`)  
**Iterations**: 50 frames  
**Zero Hardware Hallucination Policy**: ACTIVE

---

## 1. Measured End-to-End Latency Breakdown (Host CPU)

| Pipeline Stage | Monotonic Average Latency (ms) | Percentage of Total |
| :--- | :--- | :--- |
| **Image Decode (1080p JPEG)** | `62.4 ms` | 93.4% |
| **Image Preprocessing (Resize & Norm)** | `2.04 ms` | 3.1% |
| **Neural Network Inference (ONNX)** | `2.08 ms` | 3.1% |
| **Softmax Postprocessing & Gating** | `0.29 ms` | 0.4% |
| **TOTAL END-TO-END LATENCY** | **`66.81 ms`** | **100.0%** |
| **Effective Throughput (FPS)** | **`15.0 FPS`** | — |

---

## 2. Target Hardware Deployment Matrix

| Target Hardware Platform | Target Execution Engine | Status | Measured Latency | Measured FPS |
| :--- | :--- | :--- | :--- | :--- |
| **Host Workstation (Dev)** | Multi-core x86_64 CPU | `MEASURED & VERIFIED` | `2.08 ms` (Inference) | `15.0 FPS` (E2E) |
| **Raspberry Pi 5 (8GB)** | Quad-core ARM Cortex-A76 CPU | `PENDING PHYSICAL BENCHMARK` | *Pending Board* | *Pending Board* |
| **Raspberry Pi AI HAT+** | Hailo-8 / Hailo-8L NPU (PCIe) | `PENDING PHYSICAL BENCHMARK` | *Pending Board* | *Pending Board* |

---

## 3. Invariant Compliance
> [!IMPORTANT]
> In accordance with the **Zero Hardware Hallucination** policy, Raspberry Pi 5 and Hailo-8 execution speeds are not guessed or fabricated. They will be populated strictly upon running `profile_model.py` on the physical target hardware.
