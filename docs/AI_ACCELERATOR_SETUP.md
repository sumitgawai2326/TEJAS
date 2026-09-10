# Raspberry Pi AI HAT+ (Hailo-8) Setup Guide — KrishiDrishti Edge

> **Target Hardware:** Raspberry Pi AI HAT+ with Hailo-8 / Hailo-8L NPU  
> **Interface:** PCIe Gen 3 $\times 1$ via 16-pin FPC

---

## 1. Hardware Overview

The Raspberry Pi AI HAT+ incorporates the Hailo-8 Neural Processing Unit, delivering up to **26 TOPS** (Tera-Operations Per Second) of INT8/FP16 AI inference performance at ultra-low power consumption ($< 2.5\text{W}$).

---

## 2. PCIe Driver & HailoRT Runtime Setup

### Step 1: Enable PCIe Gen 3 Mode
In `/boot/firmware/config.txt`:
```ini
dtparam=pciex1
dtparam=pciex1_gen=3
```

### Step 2: Install Hailo Software Suite
```bash
sudo apt update
sudo apt install -y hailo-all
```

### Step 3: Verify Driver & Device Node
```bash
# Verify kernel device node
ls -l /dev/hailo0

# Query Hailo firmware identity
hailortcli fw-control identify
```

---

## 3. Execution Engine Switching (Zero False Reporting)

The `AcceleratorDetector` component automatically identifies the active runtime engine without manual intervention:

```
[ AI Engine Initialization ]
             ↓
[ Detect /dev/hailo0 or hailo_platform ]
   ├── Detected: Mode = HAILO ACCELERATED (PCIe NPU active)
   └── Not Detected: Mode = CPU FALLBACK (Optimized ONNX / NumPy compute)
```
