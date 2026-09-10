# KrishiDrishti Edge — Dataset Statistical & Distribution Report

## 1. Dataset Overview
- **Dataset Name**: PlantVillage Tomato Classification Subset
- **Task Type**: Multi-Class Single-Label Image Classification
- **Total Samples across All Partitions**: 18146
- **Number of Target Pathology Classes**: 10
- **Split Ratio**: 70% Train / 15% Validation / 15% Held-Out Test

---

## 2. Partition & Class Distribution Matrix

| Class Index | Target Pathology Class | Train (70%) | Val (15%) | Test (15%) | Total Samples | Imbalance Ratio |
|:-----------:|:-----------------------|:-----------:|:---------:|:----------:|:-------------:|:---------------:|
| `0` | Tomato_Bacterial_Spot | 1488 | 319 | 320 | 2127 | 11.7% |
| `1` | Tomato_Early_Blight | 700 | 150 | 150 | 1000 | 5.5% |
| `2` | Tomato_Healthy | 1109 | 237 | 239 | 1585 | 8.7% |
| `3` | Tomato_Late_Blight | 1330 | 285 | 286 | 1901 | 10.5% |
| `4` | Tomato_Leaf_Mold | 666 | 142 | 144 | 952 | 5.2% |
| `5` | Tomato_Mosaic_Virus | 261 | 55 | 57 | 373 | 2.1% |
| `6` | Tomato_Septoria_Leaf_Spot | 1239 | 265 | 267 | 1771 | 9.8% |
| `7` | Tomato_Target_Spot | 982 | 210 | 212 | 1404 | 7.7% |
| `8` | Tomato_Two-Spotted_Spider_Mite | 1173 | 251 | 252 | 1676 | 9.2% |
| `9` | Tomato_Yellow_Leaf_Curl_Virus | 3749 | 803 | 805 | 5357 | 29.5% |

---

## 3. Data Integrity & Pre-Processing Safeguards
1. **Zero Data Leakage**: Partitions were created with deterministic random seed (`seed=42`) after deduplication.
2. **Held-Out Test Boundary**: The `test/` partition (2732 samples) is strictly reserved for post-training benchmark evaluation and is never exposed during gradient optimization.
3. **Format Standard**: All images validated for RGB channel integrity, standardized to JPEG format.
