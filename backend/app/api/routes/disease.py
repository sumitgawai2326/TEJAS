"""
TEJAS Real Agricultural Disease Inference API Routes.

Exposes high-speed offline inference for tomato leaf disease classification.
"""

import os
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from app.schemas.disease import DiseasePredictResponse
from app.ai.inference.disease_engine import disease_engine
from app.core.logging import log_event

router = APIRouter(tags=["Disease Classification"])

SAMPLE_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "bacterial_spot",
        "label": "Bacterial Spot",
        "class_name": "Tomato_Bacterial_Spot",
        "filename": "sample_bacterial_spot.jpg",
        "url": "/api/v1/disease/samples/bacterial_spot/image"
    },
    {
        "id": "early_blight",
        "label": "Early Blight",
        "class_name": "Tomato_Early_Blight",
        "filename": "sample_early_blight.jpg",
        "url": "/api/v1/disease/samples/early_blight/image"
    },
    {
        "id": "healthy",
        "label": "Healthy",
        "class_name": "Tomato_Healthy",
        "filename": "sample_healthy.jpg",
        "url": "/api/v1/disease/samples/healthy/image"
    },
    {
        "id": "late_blight",
        "label": "Late Blight",
        "class_name": "Tomato_Late_Blight",
        "filename": "sample_late_blight.jpg",
        "url": "/api/v1/disease/samples/late_blight/image"
    },
    {
        "id": "yellow_leaf_curl",
        "label": "Yellow Leaf Curl Virus",
        "class_name": "Tomato_Yellow_Leaf_Curl_Virus",
        "filename": "sample_yellow_leaf_curl.jpg",
        "url": "/api/v1/disease/samples/yellow_leaf_curl/image"
    },
    {
        "id": "leaf_mold",
        "label": "Leaf Mold",
        "class_name": "Tomato_Leaf_Mold",
        "filename": "sample_leaf_mold.jpg",
        "url": "/api/v1/disease/samples/leaf_mold/image"
    },
    {
        "id": "mosaic_virus",
        "label": "Mosaic Virus",
        "class_name": "Tomato_Mosaic_Virus",
        "filename": "sample_mosaic_virus.jpg",
        "url": "/api/v1/disease/samples/mosaic_virus/image"
    },
    {
        "id": "septoria_leaf_spot",
        "label": "Septoria Leaf Spot",
        "class_name": "Tomato_Septoria_Leaf_Spot",
        "filename": "sample_septoria_leaf_spot.jpg",
        "url": "/api/v1/disease/samples/septoria_leaf_spot/image"
    },
    {
        "id": "target_spot",
        "label": "Target Spot",
        "class_name": "Tomato_Target_Spot",
        "filename": "sample_target_spot.jpg",
        "url": "/api/v1/disease/samples/target_spot/image"
    },
    {
        "id": "two_spotted_spider_mite",
        "label": "Two-Spotted Spider Mite",
        "class_name": "Tomato_Two-Spotted_Spider_Mite",
        "filename": "sample_two_spotted_spider_mite.jpg",
        "url": "/api/v1/disease/samples/two_spotted_spider_mite/image"
    }
]


@router.get(
    "/samples",
    response_model=List[Dict[str, Any]],
    summary="List curated sample tomato leaf images for presentation/demo testing"
)
async def list_sample_images() -> List[Dict[str, Any]]:
    """Returns metadata for curated verified test sample images."""
    return SAMPLE_CATALOG


@router.get(
    "/samples/{sample_id}/image",
    summary="Retrieve raw sample image file"
)
async def get_sample_image(sample_id: str):
    """Serves the JPEG image for a given sample ID."""
    sample = next((s for s in SAMPLE_CATALOG if s["id"] == sample_id), None)
    if not sample:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample '{sample_id}' not found."
        )

    # Check potential path locations
    possible_paths = [
        os.path.join("data", "sample_images", sample["filename"]),
        os.path.join("..", "data", "sample_images", sample["filename"]),
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "sample_images", sample["filename"])
    ]
    
    file_path = None
    for p in possible_paths:
        abs_p = os.path.abspath(p)
        if os.path.isfile(abs_p):
            file_path = abs_p
            break

    if not file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample image file '{sample['filename']}' not found on server storage."
        )

    return FileResponse(file_path, media_type="image/jpeg", filename=sample["filename"])


@router.post(
    "/predict",
    response_model=DiseasePredictResponse,
    summary="Classify tomato leaf disease with YOLO11n ONNX engine"
)
async def predict_disease(
    file: UploadFile = File(..., description="Multipart image file (JPEG, PNG, WEBP)")
) -> DiseasePredictResponse:
    """
    Ingests an uploaded leaf image, resizes to 224x224 RGB, runs YOLO11n ONNX inference,
    and returns top-1 and top-3 ranked pathology predictions.
    """
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided in request."
        )

    image_bytes = await file.read()
    if not image_bytes or len(image_bytes) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image file is empty (0 bytes)."
        )

    if not disease_engine.is_ready():
        log_event("API", "ERROR", "Disease inference engine is not ready.")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="TEJAS disease inference engine is not loaded or model file is unavailable."
        )

    try:
        result = disease_engine.predict(image_bytes)
        return DiseasePredictResponse(**result)
    except ValueError as ve:
        log_event("API", "WARNING", f"Image validation error: {ve}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    except Exception as e:
        log_event("API", "ERROR", f"Prediction execution failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal error during disease inference."
        )

