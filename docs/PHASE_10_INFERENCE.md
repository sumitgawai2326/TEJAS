# TEJAS — Phase 10: Real Disease-Image Inference Pipeline

**Project**: TEJAS  
**Tagline**: *"See. Sense. Predict. Act."*  
**Date**: September 10, 2026  
**Document Status**: **PHASE 10 COMPLETE — INFERENCE PIPELINE INTEGRATED**

---

## 1. Executive Summary

Phase 10 connects the verified YOLO11n tomato disease classification model (`data/models/tejas_tomato_yolo11n.onnx`) to the TEJAS FastAPI backend and frontend UI. It delivers high-speed, local offline inference on tomato leaf images with zero internet connectivity requirements, returning top-1 and top-3 ranked pathology predictions along with model provenance and image metadata.

---

## 2. API Endpoints

### Primary Endpoint
`POST /api/v1/disease/predict`

### Alias Endpoint
`POST /api/disease/predict`

- **Content-Type**: `multipart/form-data`
- **Payload**: Form field `file` containing image binary (`image/jpeg`, `image/png`, `image/webp`).
- **Response Format**: `application/json` (Status `200 OK`)

### Request Example (`curl`)

```bash
curl -X POST "http://localhost:8000/api/v1/disease/predict" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@sample_leaf.jpg;type=image/jpeg"
```

### JSON Response Schema

```json
{
  "success": true,
  "model": "tejas_tomato_yolo11n",
  "prediction": {
    "class_name": "Tomato_Bacterial_Spot",
    "confidence": 1.0
  },
  "top_predictions": [
    {
      "class_name": "Tomato_Bacterial_Spot",
      "confidence": 1.0
    },
    {
      "class_name": "Tomato_Target_Spot",
      "confidence": 0.0
    },
    {
      "class_name": "Tomato_Yellow_Leaf_Curl_Virus",
      "confidence": 0.0
    }
  ],
  "image": {
    "width": 256,
    "height": 256
  }
}
```

---

## 3. Preprocessing & Inference Architecture

```
User Leaf Upload (JPEG / PNG / WEBP)
                 ↓
      PIL Image.open() / RGB Decode
                 ↓
     Image Resizing (224 × 224 pixels)
                 ↓
 Normalization [0.0, 1.0] (float32 / 255.0)
                 ↓
 Tensor Formatting: (1, 3, 224, 224) [B, C, H, W]
                 ↓
 OpenCV DNN / ONNX Runtime Inference Session
                 ↓
  Output Evaluation & Probabilities (10 classes)
                 ↓
 Top-1 and Top-3 Descending Confidence Ranking
                 ↓
 Structured JSON API Response
```

---

## 4. Class Taxonomy (10 Tomato Pathology Classes)

| Index | Class Name | Category / Pathogen |
| :---: | :--- | :--- |
| `0` | `Tomato_Bacterial_Spot` | Bacterial (*Xanthomonas perforans*) |
| `1` | `Tomato_Early_Blight` | Fungal (*Alternaria solani*) |
| `2` | `Tomato_Healthy` | Healthy Leaf Tissue |
| `3` | `Tomato_Late_Blight` | Oomycete (*Phytophthora infestans*) |
| `4` | `Tomato_Leaf_Mold` | Fungal (*Passalora fulva*) |
| `5` | `Tomato_Mosaic_Virus` | Viral (*Tobamovirus / ToMV*) |
| `6` | `Tomato_Septoria_Leaf_Spot` | Fungal (*Septoria lycopersici*) |
| `7` | `Tomato_Target_Spot` | Fungal (*Corynespora cassiicola*) |
| `8` | `Tomato_Two-Spotted_Spider_Mite` | Pest Infestation (*Tetranychus urticae*) |
| `9` | `Tomato_Yellow_Leaf_Curl_Virus` | Viral (*Begomovirus / TYLCV*) |

---

## 5. Model Verification & Integrity

| Property | Value |
| :--- | :--- |
| **Model File** | `data/models/tejas_tomato_yolo11n.onnx` |
| **Architecture** | YOLO11n Classification (`yolo11n-cls`) |
| **Input Shape** | `(1, 3, 224, 224)` float32 |
| **Output Shape** | `(1, 10)` float32 |
| **SHA-256 Checksum** | `c988ac480a2595eb4ed96c1aaeffb7bae33ccf5418639c8aea9ad7d70128944e` |
| **Inference Engine** | OpenCV DNN (`cv2.dnn.readNetFromONNX`) with ONNX Runtime fallback |
| **Measured CPU Latency** | ~17 - 50 ms per frame |

---

## 6. Frontend Integration

The TEJAS Scanner Tab (`frontend/src/App.tsx`) incorporates:
1. Direct file upload & edge capture preview.
2. Direct invocation of `POST /api/v1/disease/predict` via `predictDisease(formData)` in `frontend/src/services/api.ts`.
3. High-contrast Top-1 Diagnosis display.
4. Top-3 Ranked Predictions with visual confidence percentage bars.
5. Image dimensions and model metadata indicators.
6. Responsible AI field validation disclaimers.

---

## 7. Responsible AI & Operational Limitations

> [!IMPORTANT]
> - **Test-Set Accuracy**: **99.63% top-1 accuracy on the held-out PlantVillage test set.**
> - **Prototype Scope**: **Prototype model trained on laboratory-style PlantVillage images; field validation is still required.**
> - **Domain Shift Protection**: In real-world field conditions, ambient lighting variations, leaf dust, camera motion blur, and co-occurring stresses can alter visual patterns. TEJAS cross-references visual classification with 6-in-1 Modbus soil telemetry before generating high-impact agronomic advisories.
