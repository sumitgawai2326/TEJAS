"""
TEJAS Real Agricultural Disease Inference API Routes.

Exposes high-speed offline inference for tomato leaf disease classification.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.schemas.disease import DiseasePredictResponse
from app.ai.inference.disease_engine import disease_engine
from app.core.logging import log_event

router = APIRouter(tags=["Disease Classification"])


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
