"""
Vision API Routes for KrishiDrishti Edge.
Provides offline crop pathology detection, image quality analysis, model registry, and accelerator status.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.vision import VisionAnalysisResponse, VisionStatusResponse, ModelRegistryResponse, ModelMetadataSchema
from app.services.crop_detection.vision_service import vision_service
from app.ai.model_registry import model_registry
from app.core.config import settings
from app.ai.inference.manager import get_vision_manager

router = APIRouter(prefix="/vision", tags=["Vision Pipeline"])

@router.post("/analyze", response_model=VisionAnalysisResponse, summary="Analyze crop leaf image for pathology")
async def analyze_crop(
    file: Optional[UploadFile] = File(None),
    field_id: Optional[int] = Form(None),
    use_camera: bool = Form(False),
    confidence_override: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Ingests an image (via multipart upload or camera HAL capture), executes image quality validation,
    runs offline AI inference with confidence gating, and optionally records the scan into SQLite.
    """
    image_bytes = None
    if file and file.filename:
        image_bytes = await file.read()

    result = vision_service.process_image(
        image_bytes=image_bytes,
        field_id=field_id,
        db=db,
        use_camera=use_camera,
        raw_confidence_override=confidence_override
    )
    return result

@router.post("/detect", response_model=VisionAnalysisResponse, summary="Alias for /analyze")
async def detect_crop_alias(
    file: Optional[UploadFile] = File(None),
    field_id: Optional[int] = Form(None),
    use_camera: bool = Form(False),
    confidence_override: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """Alias for /api/vision/analyze"""
    return await analyze_crop(
        file=file,
        field_id=field_id,
        use_camera=use_camera,
        confidence_override=confidence_override,
        db=db
    )

@router.get("/status", response_model=VisionStatusResponse, summary="Get AI accelerator and model status")
def get_vision_status():
    """
    Returns AI vision runtime status, accelerator details (CPU vs Hailo-8), model readiness,
    and confidence threshold settings.
    """
    manager = get_vision_manager()
    return manager.get_status()

@router.get("/models", response_model=ModelRegistryResponse, summary="List all registered AI models")
def list_registered_models():
    """
    Returns inventory of all registered models (Demo, Real, Missing) with hashes and metadata.
    """
    models = model_registry.get_registered_models()
    active = model_registry.get_active_model_metadata()
    return ModelRegistryResponse(
        total_models=len(models),
        active_model_id=active.model_id,
        active_model=ModelMetadataSchema(**active.model_dump()),
        models=[ModelMetadataSchema(**m.model_dump()) for m in models],
        demo_mode=settings.DEMO_MODE
    )
