# Camera Subsystem & V4L2 Guide — KrishiDrishti Edge

> **Supported Interfaces:** Raspberry Pi Camera Module 3 (MIPI CSI-2) & Standard USB Video Class (UVC) Cameras

---

## 1. Hardware Interfaces on Raspberry Pi 5

Raspberry Pi 5 features two 4-lane MIPI CSI/DSI transceiver ports (`CAM/DISP0` and `CAM/DISP1`).

### Supported Camera Types:
1. **Raspberry Pi Camera Module 3 (Sony IMX708)**: High-resolution CSI sensor with autofocus support.
2. **USB UVC Webcams**: Standard plug-and-play USB cameras supporting V4L2 video formats.

---

## 2. Configuration & Verification

### Enabling Camera in Linux Kernel (`/boot/firmware/config.txt`)
```ini
# Auto-detect official Raspberry Pi cameras
camera_auto_detect=1
```

### Command-Line Diagnostics
```bash
# Verify camera hardware detection
rpicam-hello --list-cameras

# Verify V4L2 device nodes
v4l2-ctl --list-devices
```

---

## 3. Camera HAL Fallback Hierarchy

```
[ Physical Camera Device Check (index 0) ]
       ├── Device Present: Initialize V4L2 / OpenCV VideoCapture -> Real Frame
       └── Device Absent:
             ├── Real Hardware Mode (DEMO_MODE=false) -> Return CAMERA_UNAVAILABLE (Upload fallback active)
             └── Demo Mode (DEMO_MODE=true) -> Return Mock Camera Leaf Frame
```
