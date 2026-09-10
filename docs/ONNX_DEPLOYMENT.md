# KrishiDrishti Edge — ONNX & Edge Hardware Deployment Guide

**Target Hardware**: Raspberry Pi 5 (8GB) + Raspberry Pi AI HAT+ (Hailo-8 / Hailo-8L)  
**Edge Fallback**: ARM64 / x86_64 CPU via ONNX Runtime  
**Model Format**: Open Neural Network Exchange (`.onnx` v1.14+)  
**Status**: Real Hardware Architecture Verified (Physical Latency: Pending Physical Benchmarks)

---

## 1. Edge Deployment Architecture

```
+-------------------------------------------------------------------+
|                        KrishiDrishti Vision HAL                   |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                      Model Registry & Validator                   |
|  - Checksum (SHA-256) Verification                                |
|  - Input Shape & DataType Inspection                              |
|  - Dynamic Resolution Mapping (H x W x C)                         |
+-------------------------------------------------------------------+
                                  |
          +-----------------------+-----------------------+
          |                                               |
          v                                               v
+-------------------------------+               +-------------------+
|     Hailo-8/8L AI HAT+        |               |   CPU Execution   |
|   (PCIe Gen 3 M.2 HAT)        |               | (ONNX Runtime /   |
|                               |               |  OpenVINO / C++)  |
| - Format: HEF (Hailo Exec)    |               | - Format: .onnx   |
| - Target: 13/26 TOPS          |               | - Target: 4 Cores |
| - Status: HARDWARE PENDING    |               | - Status: ACTIVE  |
+-------------------------------+               +-------------------+
```

---

## 2. Model Pipeline & Export Sequence

1. **PyTorch Weight Export**:
   - Model weights checkpointed in `ml/runs/tomato_cls/weights/best.pt` or `data/models/weights.pt`.
   - Exported to ONNX using `ml/export_onnx.py`.
   - Dynamic or static batch size ($1 \times 3 \times H \times W$), opset version 14+.

2. **Graph Validation (`ml/validate_onnx.py`)**:
   - Verify ONNX graph integrity with `onnx.checker.check_model()`.
   - Inspect input tensor dimensions and normalize pre-processing transforms.
   - Run sample inference with `onnxruntime.InferenceSession`.
   - Compare PyTorch vs ONNX numerical parity ($L_\infty \text{ error} < 10^{-4}$).

3. **Integrity & Security (`ml/model_hash.py`)**:
   - Compute SHA-256 checksum for model provenance.
   - Record in model metadata / registry manifest.

---

## 3. Hailo-8 Compilation Workflow (Deployment on Pi AI HAT+)

When the physical Raspberry Pi AI HAT+ is connected:

1. **Parse ONNX**:
   ```bash
   hailo parser onnx data/models/crop_disease_v1.onnx --hw-arch hailo8
   ```
2. **Quantize with Calibration Dataset**:
   ```bash
   hailo optimize crop_disease_v1.har --calib-set-path ml/data/calib/
   ```
3. **Compile to HEF (Hailo Executable Format)**:
   ```bash
   hailo compiler crop_disease_v1_quantized.har --hw-arch hailo8 -o data/models/crop_disease_v1.hef
   ```
4. **Physical Latency Validation**:
   - Measure monotonic execution time per frame on physical PCIe interface.
   - Record power draw under load.
   - *Note: As per Zero Hardware Hallucination policy, latency and FPS metrics are reported as PENDING PHYSICAL BENCHMARK until tested on hardware.*

---

## 4. Fallback Execution on Edge CPU

If no NPU is detected or PCIe HAT initialization fails:
1. `HailoAccelerator` automatically falls back to `CPUInferenceBackend`.
2. ONNX Runtime uses OpenMP / multithreaded CPU kernels (`IntraOpNumThreads=4`).
3. Seamless zero-downtime diagnostic continuity is maintained for the farmer.
