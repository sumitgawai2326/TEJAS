# KrishiDrishti Edge — Troubleshooting & Diagnostic Guide

> **Common Issues & Edge System Remediation**

---

## 1. AI Vision Pipeline Issues

### Issue: `status: "invalid_image"` (Image Rejected Before Inference)
- **Cause**: Image failed pre-inference quality checks.
- **Diagnostics**:
  - `IMAGE_TOO_BLURRY` ($\text{Laplacian Variance} < 18.0$): The leaf is out of focus or camera moved during capture.
  - `IMAGE_TOO_DARK` ($\text{Mean Brightness} < 20.0$): Insufficient ambient light.
  - `IMAGE_TOO_BRIGHT` ($\text{Mean Brightness} > 240.0$): Excessive sunlight glare on leaf surface.
  - `IMAGE_TOO_SMALL`: Image resolution under $120 \times 120$.
- **Remediation**: Re-frame the leaf under diffuse natural light, steady the camera, and move 15–20 cm from the diseased area.

### Issue: `status: "low_confidence"` (Unknown / Low Confidence)
- **Cause**: Model prediction probability was lower than `AI_CONFIDENCE_THRESHOLD` (default 70%).
- **Remediation**: The system intentionally prevents false diagnoses. Capture a cleaner angle showing both lesion edges and healthy leaf context.

### Issue: `status: "ai_unavailable"` / `ready: false`
- **Cause**: The system is running in `DEMO_MODE=false` (Real Hardware Mode) and no trained ONNX model weights were found at `MODEL_PATH`.
- **Remediation**: Place the trained `.onnx` or `.hef` model into `ai/models/` and configure `MODEL_PATH` in `.env`.

---

## 2. Hardware Subsystems Issues

### Issue: Soil Sensor Returns All `null` Values
- **Cause**: In `DEMO_MODE=false`, the RS485 Modbus sensor is disconnected or register map is unconfigured.
- **Rule**: This is expected behavior under the **Zero Hardware Hallucination** policy. Real disconnected hardware must never produce fabricated numbers.
- **Remediation**: Connect USB-RS485 adapter to `/dev/ttyUSB0` and configure `hardware/sensor_protocol/soil_sensor.yaml`.

### Issue: Camera Unavailable (`status: "CAMERA_UNAVAILABLE"`)
- **Cause**: V4L2 device `/dev/video0` or libcamera index not accessible.
- **Remediation**: Check ribbon cable / USB connection and verify permissions (`sudo usermod -a -G video $USER`).
