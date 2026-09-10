# KrishiDrishti Edge — AI Model Validation & Pre-Flight Integrity Architecture

## Overview
Before deploying or activating any computer vision neural network on the edge runtime, KrishiDrishti Edge executes a rigorous, multi-stage automated validation process.

```
Model File on Disk (.onnx)
         ↓
1. Binary Signature & Hash Verification (SHA-256)
         ↓
2. Dynamic Tensor Shape Resolution (Non-hardcoded)
         ↓
3. Logit-Class Dimensional Alignment
         ↓
4. Non-Destructive Smoke Inference (Zero-Tensor)
         ↓
Model Validation Report (VALIDATED vs INVALID vs NOT_YET_VALIDATED)
```

---

## 1. Dynamic Input Shape Resolution
KrishiDrishti Edge does **not** hardcode input tensor shapes as `(1, 3, 224, 224)` universally across all models. 
- Input dimensions are inspected directly from model graph metadata via ONNX runtime bindings.
- If a model utilizes dynamic batching `[-1, 3, H, W]` or resolution dimensions, the preprocessor dynamically adapts to the model's graph specification while retaining `224x224` as the default baseline where compatible.

---

## 2. Integrity Check Criteria
A model binary is verified against the following checks:
1. **File Existence & Readability**: Checks binary existence and permissions.
2. **SHA-256 Checksum Calculation**: Calculates and logs an immutable SHA-256 hash for forensic auditability and model version pinning.
3. **Graph Inspection**: Confirms valid input and output node definitions.
4. **Logit-to-Class Count Alignment**: Confirms that output tensor dimensions match the length of the registered target class mapping.
5. **Dummy Tensor Smoke Inference**: Runs single zero-tensor inference through the CPU execution provider to confirm stability without runtime segfaults or unhandled exceptions.

---

## 3. Validation Status States
- `MODEL_VALID`: All structural and smoke inference checks passed.
- `MODEL_INVALID`: Graph is malformed, logit count mismatches class list, or smoke inference crashed.
- `MODEL_NOT_FOUND`: Production weights file does not exist at configured path.
- `NOT YET VALIDATED`: Model structure is valid, but full experimental validation against labeled ground-truth splits has not been conducted.
