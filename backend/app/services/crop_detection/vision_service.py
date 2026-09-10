"""
Crop Vision Pathology Service.
Coordinates Camera HAL -> Image Quality Validator -> Preprocessor -> AI Inference Engine -> SQLite Persistence.
"""
import os
import uuid
import datetime
import cv2
import numpy as np
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.schemas.vision import VisionAnalysisResponse, ImageQualityResult
from app.ai.preprocessing.quality import ImageQualityValidator
from app.ai.inference.manager import get_vision_manager
from app.hardware.camera import get_camera
from app.db.repositories import ScanRepository, FieldRepository
from app.core.config import settings
from app.core.logging import log_event

class VisionPipelineService:
    def __init__(self):
        self.quality_validator = ImageQualityValidator(
            min_width=120,
            min_height=120,
            min_blur_score=18.0,
            min_brightness=20.0,
            max_brightness=240.0
        )
        self.captures_dir = settings.IMAGE_STORAGE_DIR
        os.makedirs(self.captures_dir, exist_ok=True)

    def process_image(
        self,
        image_bytes: Optional[bytes] = None,
        field_id: Optional[int] = None,
        db: Optional[Session] = None,
        use_camera: bool = False,
        raw_confidence_override: Optional[float] = None
    ) -> VisionAnalysisResponse:
        """
        Executes end-to-end crop pathology pipeline:
        1. Capture / Ingest image
        2. Validate quality (blur, exposure, resolution)
        3. Preprocess & execute local AI inference
        4. Apply confidence gating
        5. Save capture & persist scan in SQLite if field_id is present
        """
        # Step 1: Obtain Image
        img_bgr = None
        if use_camera:
            camera = get_camera()
            success, frame, meta = camera.capture()
            if not success or frame is None:
                log_event("CAMERA", "WARNING", f"Camera capture failed: {meta.get('error')}")
                return VisionAnalysisResponse(
                    status="invalid_image",
                    prediction="Camera Unavailable",
                    confidence=0.0,
                    model_name="None",
                    model_version="None",
                    inference_time_ms=0.0,
                    inference_device="CPU",
                    is_demo=settings.DEMO_MODE,
                    image_quality=ImageQualityResult(
                        valid=False,
                        score=0.0,
                        issues=["CAMERA_UNAVAILABLE"],
                        resolution="0x0",
                        blur_score=0.0,
                        brightness_score=0.0,
                        message="Failed to capture frame from camera device."
                    ),
                    message="Camera device is unavailable or unattached."
                )
            img_bgr = frame
        else:
            if not image_bytes:
                return VisionAnalysisResponse(
                    status="invalid_image",
                    prediction="No Image Provided",
                    confidence=0.0,
                    model_name="None",
                    model_version="None",
                    inference_time_ms=0.0,
                    inference_device="CPU",
                    is_demo=settings.DEMO_MODE,
                    image_quality=ImageQualityResult(
                        valid=False,
                        score=0.0,
                        issues=["EMPTY_IMAGE"],
                        resolution="0x0",
                        blur_score=0.0,
                        brightness_score=0.0,
                        message="Please capture or upload a valid crop leaf image."
                    ),
                    message="No image provided for analysis."
                )
            img_bgr = self.quality_validator.decode_image(image_bytes)

        # Step 2: Quality Validation
        quality_res = self.quality_validator.validate(img_bgr)
        if not quality_res.valid:
            log_event("AI", "WARNING", f"Image rejected due to quality issues: {quality_res.issues}")
            return VisionAnalysisResponse(
                status="invalid_image",
                prediction="Invalid Image Quality",
                confidence=0.0,
                model_name="None",
                model_version="None",
                inference_time_ms=0.0,
                inference_device="CPU",
                is_demo=settings.DEMO_MODE,
                field_id=field_id,
                image_quality=quality_res,
                message=quality_res.message
            )

        # Step 3: Local Storage Persistence for Image File
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"scan_{timestamp_str}_{uuid.uuid4().hex[:8]}.jpg"
        file_path = os.path.join(self.captures_dir, filename)
        try:
            cv2.imwrite(file_path, img_bgr)
            relative_image_path = f"data/captures/{filename}"
        except Exception as e:
            log_event("AI", "WARNING", f"Could not write image capture to disk: {e}")
            relative_image_path = None

        # Step 4: AI Model Inference & Confidence Gating
        vision_mgr = get_vision_manager()
        ai_res = vision_mgr.analyze_image(
            img_bgr=img_bgr,
            quality_result=quality_res,
            raw_confidence_override=raw_confidence_override
        )

        # Step 5: Persist Scan Record in SQLite if DB session & field_id provided
        scan_id = None
        if db and field_id:
            field_repo = FieldRepository(db)
            if field_repo.get_by_id(field_id):
                scan_repo = ScanRepository(db)
                scan_rec = scan_repo.create(
                    field_id=field_id,
                    prediction=ai_res["prediction"],
                    confidence=ai_res["confidence"],
                    model_name=ai_res["model_name"],
                    model_version=ai_res["model_version"],
                    image_path=relative_image_path,
                    image_quality=quality_res.score,
                    inference_device=ai_res["inference_device"],
                    status=ai_res["status"]
                )
                scan_id = scan_rec.id
                log_event("DATABASE", "INFO", f"Saved Scan record ID {scan_id} for Field {field_id}")

        return VisionAnalysisResponse(
            status=ai_res["status"],
            prediction=ai_res["prediction"],
            confidence=ai_res["confidence"],
            model_name=ai_res["model_name"],
            model_version=ai_res["model_version"],
            inference_time_ms=ai_res["inference_time_ms"],
            inference_device=ai_res["inference_device"],
            is_demo=ai_res["is_demo"],
            scan_id=scan_id,
            field_id=field_id,
            image_path=relative_image_path,
            image_quality=quality_res,
            crop=ai_res.get("crop", "General"),
            severity=ai_res.get("severity", "Unknown"),
            message=ai_res["message"]
        )

vision_service = VisionPipelineService()
