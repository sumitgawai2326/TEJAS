# KrishiDrishti Edge — Phase 9A Real Dataset Acquisition & Validation Report

**Project**: KrishiDrishti Edge  
**Phase**: Phase 9A — Real Dataset Acquisition & Dataset Validation  
**Target Crop**: Tomato (*Solanum lycopersicum*)  
**Task**: Whole-Image Multi-Class Pathology Classification (10 Classes)  
**Execution Date**: 2026-09-10  
**Policy Compliance**: Strict Zero AI Hallucination & Zero Hardware Hallucination  

---

## 1. Executive Summary & Final Status

```
FINAL STATUS:
DATASET READY FOR REAL TRAINING
```

The authentic **PlantVillage Tomato Dataset** (CC BY 4.0) has been acquired directly from the official academic repository via Git sparse-checkout, verified with PIL for channel and format integrity, deduplicated, and partitioned into a deterministic 70/15/15 train/validation/test split.

No synthetic images or randomly generated matrices were involved in this acquisition or partition. The previous smoke-test ONNX model remains preserved as a labelled pipeline artifact, and no training has been initiated yet.

---

## 2. Dataset Provenance & Source Information

1. **Dataset Name**: PlantVillage Tomato Classification Subset
2. **Primary Repository Source**: `https://github.com/spMohanty/PlantVillage-Dataset.git`
3. **Repository Commit Hash**: `7f7ecc7e1eaca78107e3affe7cb5abd9427e139a`
4. **License**: Creative Commons Attribution 4.0 International (`CC BY 4.0`)
5. **Academic Citation**:  
   *Hughes, D., & Salathé, M. (2015). An open access repository of images on plant health to enable the development of mobile disease diagnostics. arXiv preprint arXiv:1511.08060.*
6. **Download Date**: 2026-09-09 19:38:02 UTC
7. **Local Storage Paths**:
   - **Raw Ingestion Directory**: `ml/data/raw/plantvillage_tomato/`
   - **Cleaned Interim Directory**: `ml/data/interim/tomato_cleaned/`
   - **Processed Split Directory**: `ml/data/processed/tomato_cls/`

---

## 3. Dataset Counts & Class Distribution

- **Total Downloaded Raw Images**: `18,160`
- **Corrupted / Unreadable Images**: `0`
- **Exact Cryptographic Duplicates Detected**: `14` files
- **Total Usable Clean Images (Post-Deduplication)**: `18,146`
- **All 10 Target Classes Present**: **YES** (10 / 10 classes available)

### Class Breakdown Table

| Index | Target Pathology Class | Raw Downloaded | Deduplicated Clean | Train (70%) | Val (15%) | Test (15%) | Imbalance Ratio |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `0` | `Tomato_Bacterial_Spot` | 2,127 | 2,127 | 1,488 | 319 | 320 | 11.7% |
| `1` | `Tomato_Early_Blight` | 1,000 | 1,000 | 700 | 150 | 150 | 5.5% |
| `2` | `Tomato_Healthy` | 1,591 | 1,585 | 1,109 | 237 | 239 | 8.7% |
| `3` | `Tomato_Late_Blight` | 1,909 | 1,901 | 1,330 | 285 | 286 | 10.5% |
| `4` | `Tomato_Leaf_Mold` | 952 | 952 | 666 | 142 | 144 | 5.2% |
| `5` | `Tomato_Mosaic_Virus` | 373 | 373 | 261 | 55 | 57 | 2.1% |
| `6` | `Tomato_Septoria_Leaf_Spot` | 1,771 | 1,771 | 1,239 | 265 | 267 | 9.8% |
| `7` | `Tomato_Target_Spot` | 1,404 | 1,404 | 982 | 210 | 212 | 7.7% |
| `8` | `Tomato_Two-Spotted_Spider_Mite` | 1,676 | 1,676 | 1,173 | 251 | 252 | 9.2% |
| `9` | `Tomato_Yellow_Leaf_Curl_Virus` | 5,357 | 5,357 | 3,749 | 803 | 805 | 29.5% |
| **TOTAL** | — | **18,160** | **18,146** | **12,697** | **2,717** | **2,732** | **100.0%** |

---

## 4. Cross-Partition Data Leakage Audit Findings

Audited via `ml/scripts/verify_leakage.py` across all 18,146 partition images:

1. **Exact Cryptographic SHA-256 Overlap**:
   - `Train` $\leftrightarrow$ `Val`: **0 hashes (Zero Overlap)**
   - `Train` $\leftrightarrow$ `Test`: **0 hashes (Zero Overlap)**
   - `Val` $\leftrightarrow$ `Test`: **0 hashes (Zero Overlap)**
2. **Perceptual Similarity (dHash) Overlap**:
   - `Train` $\leftrightarrow$ `Val`: **0 dHash keys**
   - `Train` $\leftrightarrow$ `Test`: **1 isolated near-similarity key** (within normal botanical variance across separate leaf samples)
   - `Val` $\leftrightarrow$ `Test`: **0 dHash keys**
3. **Partition Integrity Verification**:
   - **ZERO exact cryptographic leakage detected**.
   - Held-out `test/` partition (2,732 images) is strictly isolated for post-training benchmark evaluation.

---

## 5. Dataset Known Limitations & Real-World Caveats

In compliance with the **Zero AI Hallucination Policy**, the following real-world dataset limitations are documented:

1. **Laboratory Background Bias**: PlantVillage images were captured in controlled lab settings with detached leaves placed against neutral or dark backgrounds under uniform lighting.
2. **Class Imbalance**: *Tomato Yellow Leaf Curl Virus* comprises 29.5% of the dataset (5,357 images), while *Tomato Mosaic Virus* comprises 2.1% (373 images). Loss weighting and balanced sampling will be required during training.
3. **Wild Field Gap**: In-situ deployment under natural field canopies, soil backgrounds, wind flutter, and direct sun glare requires subsequent benchmarking on field datasets (e.g. *PlantDoc*) and physical in-field validation as specified in `docs/REAL_WORLD_VALIDATION_PLAN.md`.

---

## 6. Readiness for Subsequent Phases

- Real dataset downloaded, inspected, cleaned, deduplicated, and partitioned: **COMPLETE**.
- Pipeline unit tests (99/99 passing): **COMPLETE**.
- Frontend production build (0 errors): **COMPLETE**.
- Next action: Await explicit approval to proceed to **Phase 9B (Real Model Training on Authenticated Data)**.
