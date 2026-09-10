# TEJAS — Offline Model Evaluation & Benchmark Results (TEST)

## 1. Summary of TEST Split Evaluation
- **Evaluated Model**: `ml\runs\train\tejas_tomato_yolo11n_cls\weights\best.pt`
- **Evaluation Status**: **VALIDATED ON TEST DATA**
- **Total Samples**: 2732
- **Top-1 Accuracy**: **99.63%**
- **Top-5 Accuracy**: **100.00%**
- **Macro F1-Score**: **0.9949**
- **Macro Precision**: **0.9945**
- **Macro Recall**: **0.9954**
- **Evaluation Date**: 2026-09-10 16:09:04 UTC

---

## 2. Per-Class Performance Breakdown

| Class Name | Samples | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **Tomato_Bacterial_Spot** | 320 | 1.0000 | 1.0000 | 1.0000 |
| **Tomato_Early_Blight** | 150 | 1.0000 | 0.9800 | 0.9899 |
| **Tomato_Healthy** | 239 | 1.0000 | 0.9958 | 0.9979 |
| **Tomato_Late_Blight** | 286 | 0.9896 | 1.0000 | 0.9948 |
| **Tomato_Leaf_Mold** | 144 | 0.9931 | 1.0000 | 0.9965 |
| **Tomato_Mosaic_Virus** | 57 | 0.9828 | 1.0000 | 0.9913 |
| **Tomato_Septoria_Leaf_Spot** | 267 | 0.9963 | 0.9963 | 0.9963 |
| **Tomato_Target_Spot** | 212 | 0.9953 | 0.9906 | 0.9929 |
| **Tomato_Two-Spotted_Spider_Mite** | 252 | 0.9881 | 0.9921 | 0.9901 |
| **Tomato_Yellow_Leaf_Curl_Virus** | 805 | 1.0000 | 0.9988 | 0.9994 |

---

## 3. Real-World Invariant
> [!NOTE]
> Evaluation results reflect performance on the curated laboratory-style PlantVillage dataset. Real field performance across dynamic shadows, dust, and non-foliar backgrounds requires field-based testing.
