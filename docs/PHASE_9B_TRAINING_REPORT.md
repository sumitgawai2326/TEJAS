# KrishiDrishti Edge — Phase 9B Real Model Training Report

**Project**: KrishiDrishti Edge  
**Phase**: Phase 9B — Real YOLO Tomato Disease Model Training  
**Target Crop**: Tomato (*Solanum lycopersicum*)  
**Architecture**: YOLO11n-cls / YOLOv8n-cls (Ultralytics Classification Backbone)  
**Execution Date**: 2026-09-10  
**Policy Compliance**: Strict Zero AI Hallucination & Zero Hardware Hallucination  

---

## 1. Executive Summary & Training Status

```
PHASE 9B STATUS:
TRAINING BLOCKED

REAL TRAINING NOT COMPLETED
```

The authentic PlantVillage Tomato dataset (18,146 usable images across 10 classes in 70/15/15 split) is fully prepared and validated on disk. However, model training execution via PyTorch/Ultralytics is currently **BLOCKED** on the host machine due to a low-level binary runtime incompatibility between CPython 3.14.2 on Windows and the PyTorch `c10.dll` dynamic link library.

In strict accordance with the **Zero AI Hallucination Policy**, no fake checkpoints, synthetic training curves, or fabricated validation metrics have been created. The previous synthetic model (`data/models/crop_disease_v1.onnx`) remains labeled as a pipeline smoke-test artifact and is NOT claimed as a trained agricultural model.

---

## 2. Environment & Hardware Diagnostics

- **Host Operating System**: Windows 11 (AMD64, 10.0.26200)
- **Host CPU**: Intel64 Family 6 Model 142 (8 Logical Cores)
- **Host RAM**: 7.78 GB Total (0.92 GB Free)
- **Python Runtime**: `3.14.2` (`MSC v.1944 64 bit (AMD64)`)
- **PyTorch Wheel Installed**: `torch 2.14.0 (cp314-cp314-win_amd64)`
- **Ultralytics Wheel Installed**: `ultralytics 8.4.146`
- **CUDA Acceleration**: `UNAVAILABLE / BLOCKED`
- **Root Cause of Execution Block**:
  ```
  OSError: [WinError 1114] A dynamic link library (DLL) initialization routine failed.
  Error loading "...\site-packages\torch\lib\c10.dll" or one of its dependencies.
  ```
  CPython 3.14 introduces core internal C API changes. The Windows PyTorch 2.14 C10 runtime fails during `DllMain` entry in this Python version.

---

## 3. Dataset Verification State (ml/data/processed/tomato_cls/)

The real dataset is ready for training whenever the execution runtime is enabled:

| Partition | Real Image Count | Verification Status | Exact Duplicate Cross-Overlap |
| :--- | :---: | :---: | :---: |
| **Train (70%)** | `12,697` | Authenticated PlantVillage | 0 hashes |
| **Val (15%)** | `2,717` | Authenticated PlantVillage | 0 hashes |
| **Test (15%)** | `2,732` | Authenticated PlantVillage (Held-out) | 0 hashes |
| **Total** | **18,146** | **10 / 10 Target Classes** | **0 Hashes** |

### Verified 10-Class Distribution:
1. `Tomato_Bacterial_Spot`: 2,127 images (Train: 1,488, Val: 319, Test: 320)
2. `Tomato_Early_Blight`: 1,000 images (Train: 700, Val: 150, Test: 150)
3. `Tomato_Healthy`: 1,585 images (Train: 1,109, Val: 237, Test: 239)
4. `Tomato_Late_Blight`: 1,901 images (Train: 1,330, Val: 285, Test: 286)
5. `Tomato_Leaf_Mold`: 952 images (Train: 666, Val: 142, Test: 144)
6. `Tomato_Mosaic_Virus`: 373 images (Train: 261, Val: 55, Test: 57)
7. `Tomato_Septoria_Leaf_Spot`: 1,771 images (Train: 1,239, Val: 265, Test: 267)
8. `Tomato_Target_Spot`: 1,404 images (Train: 982, Val: 210, Test: 212)
9. `Tomato_Two-Spotted_Spider_Mite`: 1,676 images (Train: 1,173, Val: 251, Test: 252)
10. `Tomato_Yellow_Leaf_Curl_Virus`: 5,357 images (Train: 3,749, Val: 803, Test: 805)

---

## 4. Training Recipe & Configuration Prepared

The training script [`ml/train.py`](file:///C:/Users/Admin/.gemini/antigravity/scratch/krishidrishti-edge/ml/train.py) and configuration [`ml/configs/tomato_yolo_cls.yaml`](file:///C:/Users/Admin/.gemini/antigravity/scratch/krishidrishti-edge/ml/configs/tomato_yolo_cls.yaml) are configured:

```yaml
model:
  architecture: "yolo11n-cls.pt"
  num_classes: 10
  input_resolution: [224, 224]

training:
  data: "ml/data/processed/tomato_cls"
  epochs: 30
  batch_size: 16
  imgsz: 224
  optimizer: "AdamW"
  lr0: 0.001
  lrf: 0.01
  weight_decay: 0.0005
  seed: 42
  workers: 2
  patience: 10
  project: "ml/runs/train"
  name: "tomato_cls_yolo"

augmentation:
  hsv_h: 0.015
  hsv_s: 0.4
  hsv_v: 0.4
  degrees: 15.0
  translate: 0.1
  scale: 0.2
  fliplr: 0.5
  mosaic: 0.0
```

---

## 5. Checkpoint & Artifact Truth Matrix

- **Real Checkpoint (`ml/runs/train/tomato_cls_yolo/weights/best.pt`)**: `NOT CREATED` (Training blocked by Python 3.14 PyTorch DLL error).
- **Candidate Real Model (`data/models/tomato_yolo_cls_v1.pt`)**: `NOT CREATED`.
- **Synthetic Smoke-Test Artifact (`data/models/crop_disease_v1.onnx`)**: `PRESERVED AS PIPELINE TEST ONLY`.
- **Validation Metrics**: `NOT MEASURED (NO REAL TRAINING EXECUTED)`.
- **Test Metrics**: `HELD-OUT PARTITION UNTOUCHED`.

---

## 6. Resolution Roadmap for Real Training

To execute real training:
1. Use Python 3.11 or Python 3.12 (the standard supported CPython versions for PyTorch/CUDA and Ultralytics on Windows/Linux).
2. Run `python ml/train.py --config ml/configs/tomato_yolo_cls.yaml` on the authenticated `ml/data/processed/tomato_cls/` dataset.
3. Checkpoint the authentic `best.pt` weights and proceed to Phase 9C test evaluation and ONNX export.
