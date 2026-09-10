# TEJAS — Offline Model Evaluation & Benchmark Results (VAL)

## 1. Summary of VAL Split Evaluation
- **Evaluated Model**: `ml\runs\train\tejas_tomato_yolo11n_cls\weights\best.pt`
- **Evaluation Status**: **VALIDATED ON VAL DATA**
- **Total Samples**: 2717
- **Top-1 Accuracy**: **99.78%**
- **Top-5 Accuracy**: **100.00%**
- **Macro F1-Score**: **0.9975**
- **Macro Precision**: **0.9971**
- **Macro Recall**: **0.9978**
- **Evaluation Date**: 2026-09-10 16:07:55 UTC

---

## 2. Per-Class Performance Breakdown

| Class Name | Samples | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **Tomato_Bacterial_Spot** | 319 | 1.0000 | 0.9937 | 0.9968 |
| **Tomato_Early_Blight** | 150 | 0.9933 | 0.9933 | 0.9933 |
| **Tomato_Healthy** | 237 | 1.0000 | 1.0000 | 1.0000 |
| **Tomato_Late_Blight** | 285 | 1.0000 | 0.9965 | 0.9982 |
| **Tomato_Leaf_Mold** | 142 | 1.0000 | 1.0000 | 1.0000 |
| **Tomato_Mosaic_Virus** | 55 | 1.0000 | 1.0000 | 1.0000 |
| **Tomato_Septoria_Leaf_Spot** | 265 | 0.9962 | 1.0000 | 0.9981 |
| **Tomato_Target_Spot** | 210 | 0.9859 | 1.0000 | 0.9929 |
| **Tomato_Two-Spotted_Spider_Mite** | 251 | 0.9960 | 0.9960 | 0.9960 |
| **Tomato_Yellow_Leaf_Curl_Virus** | 803 | 1.0000 | 0.9988 | 0.9994 |

---

## 3. Real-World Invariant
> [!NOTE]
> Evaluation results reflect performance on the curated laboratory-style PlantVillage dataset. Real field performance across dynamic shadows, dust, and non-foliar backgrounds requires field-based testing.
