# TEJAS — Phase 9C: Real Tomato Disease Model Training Report

**Project**: TEJAS  
**Tagline**: *"See. Sense. Predict. Act."*  
**Run Name**: `tejas_tomato_yolo11n_cls`  
**Date**: September 10, 2026  
**Document Status**: **AUTHENTICATED ML TRAINING COMPLETE**  

---

## 1. Environment & Hardware Specifications

- **Python Runtime**: `Python 3.11.9` (64-bit AMD64)
- **Virtual Environment**: `.venv-ml`
- **PyTorch Version**: `2.5.1+cpu`
- **Torchvision Version**: `0.20.1+cpu`
- **Ultralytics Version**: `8.4.146`
- **ONNX Version**: `1.22.0`
- **ONNX Runtime Version**: `1.19.2`
- **Hardware Profile**: Intel Core i5-10210U @ 1.60GHz (4 physical cores, 8 logical cores, 7.78 GB RAM)
- **Acceleration**: CPU Mode (`CUDA: False`)

---

## 2. Authenticated Dataset Summary

- **Source Dataset**: Authenticated PlantVillage Tomato leaf pathology dataset (CC BY 4.0)
- **Storage Location**: `ml/data/processed/tomato_cls/`
- **Total Clean Usable Images**: 18,146 images (0 corruptions, 0 cross-partition duplicates)
- **Total Classes**: 10 pathology classes

### Split Distribution

| Split Partition | Image Count | Percentage | Partition Purpose |
| :--- | :--- | :--- | :--- |
| **Train** | 12,697 | 69.97% | Model parameter gradient updates |
| **Validation** | 2,717 | 14.97% | Hyperparameter tuning & model selection |
| **Held-Out Test** | 2,732 | 15.06% | Unseen evaluation baseline |
| **Total** | **18,146** | **100.0%** | Dedicated single-leaf tomato dataset |

---

## 3. Model Architecture & Hyperparameters

- **Architecture**: `YOLO11n-cls` (Ultralytics pretrained backbone fine-tuned for 10 classes)
- **Parameters**: 1,538,834 parameters (0.4 GFLOPs fused inference)
- **Input Resolution**: `224 x 224 x 3` RGB
- **Epochs Requested**: 30
- **Epochs Completed**: 30
- **Batch Size**: 16
- **Optimizer**: AdamW (`lr0 = 0.001`, `lrf = 0.01`, `weight_decay = 0.0005`)
- **Patience**: 10
- **Seed**: 42 (Deterministic execution)
- **Device**: CPU (`workers = 2`)

---

## 4. Training Execution & Timing

- **Exact Training Command**:
  ```powershell
  .\.venv-ml\Scripts\python.exe ml\train.py --epochs 30 --name tejas_tomato_yolo11n_cls
  ```
- **Training Start Time**: `2026-09-10 10:02:31 UTC`
- **Training End Time**: `2026-09-10 16:04:31 UTC`
- **Total Measured Elapsed Time**: **21719.43 seconds (361.99 minutes / 6.03 hours)**
- **Best Epoch**: Epoch 29 (Validation Loss: 0.00958, Fitness: 0.998896)

---

## 5. Validation Split Evaluation Results

- **Validation Top-1 Accuracy**: **99.78% (0.9978)**
- **Validation Top-5 Accuracy**: **100.00% (1.0)**
- **Validation Macro Precision**: **0.9971**
- **Validation Macro Recall**: **0.9978**
- **Validation Macro F1-Score**: **0.9975**

---

## 6. Held-Out Test Split Evaluation Results

- **Held-Out Test Top-1 Accuracy**: **99.63% (0.9963)**
- **Held-Out Test Top-5 Accuracy**: **100.00% (1.0)**
- **Held-Out Test Macro Precision**: **0.9945**
- **Held-Out Test Macro Recall**: **0.9954**
- **Held-Out Test Macro F1-Score**: **0.9949**

### Per-Class Test Performance Breakdown

| Class Name | Test Samples | Precision | Recall | F1-Score |
| :--- | :--- | :--- | :--- | :--- |
| **Tomato_Bacterial_Spot** | 320 | 1.0000 | 1.0000 | **1.0000** |
| **Tomato_Early_Blight** | 150 | 1.0000 | 0.9800 | **0.9899** |
| **Tomato_Healthy** | 239 | 1.0000 | 0.9958 | **0.9979** |
| **Tomato_Late_Blight** | 286 | 0.9896 | 1.0000 | **0.9948** |
| **Tomato_Leaf_Mold** | 144 | 0.9931 | 1.0000 | **0.9965** |
| **Tomato_Mosaic_Virus** | 57 | 0.9828 | 1.0000 | **0.9913** |
| **Tomato_Septoria_Leaf_Spot** | 267 | 0.9963 | 0.9963 | **0.9963** |
| **Tomato_Target_Spot** | 212 | 0.9953 | 0.9906 | **0.9929** |
| **Tomato_Two-Spotted_Spider_Mite** | 252 | 0.9881 | 0.9921 | **0.9901** |
| **Tomato_Yellow_Leaf_Curl_Virus** | 805 | 1.0000 | 0.9988 | **0.9994** |

---

## 7. ONNX Export & ONNX Runtime Verification

- **Exported ONNX Model**: `data\models\tejas_tomato_yolo11n.onnx`
- **Input Dimension**: `1 x 3 x 224 x 224`
- **Output Dimension**: `1 x 10`
- **ONNX Verification Status**: **PASS**
- **Prediction Consistency with PyTorch**: **100.0% match** across test images
- **Max Absolute Probability Difference**: **0.000115** (well below 0.001 threshold)

---

## 8. Cryptographic Model SHA-256 Hashes

| Artifact Path | Description | SHA-256 Checksum |
| :--- | :--- | :--- |
| `C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\runs\classify\ml\runs\train\tejas_tomato_yolo11n_cls\weights\best.pt` | Trained PyTorch Weights | `89ef6b0aa7cd285f533c0b022c718b5d6f91cebfa33f0c133c377f688cff976a` |
| `data\models\tejas_tomato_yolo11n.onnx` | Edge-Deployable ONNX Model | `c988ac480a2595eb4ed96c1aaeffb7bae33ccf5418639c8aea9ad7d70128944e` |
| `data/models/crop_disease_v1.onnx` | Preserved Synthetic Smoke Test Model | `5035e5d1796d113ae87fcba98007db1352fecbf45db611e9f45ba8ec63297379` |

---

## 9. Real-World Limitations & Responsible AI Disclaimer

> [!IMPORTANT]
> - **Laboratory Dataset Boundary**: PlantVillage images are captured in controlled, uniform background environments with isolated leaves.
> - **Field Domain Shift**: Field conditions introduce dynamic shadows, camera shake, dust on leaves, multi-pathology co-occurrence, and soil background clutter.
> - **Operational Classification**: This model is designated as a **PlantVillage-trained tomato disease classification prototype** until physical field testing in agricultural conditions is conducted.
> - **Multi-Modal Risk Mitigation**: TEJAS cross-references visual predictions with soil parameter telemetry (EC, pH, Moisture, NPK) before issuing actionable farmer advisories.
