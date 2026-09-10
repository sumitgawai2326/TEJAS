"""
Crop Vision Pathology Service for TEJAS.
Unified single-source pipeline:
Camera HAL / Upload -> Image Quality Validator -> YOLO11n ONNX disease_engine -> SQLite Persistence.
"""
import os
import uuid
import time
import datetime
import cv2
import numpy as np
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from app.schemas.vision import VisionAnalysisResponse, ImageQualityResult
from app.ai.preprocessing.quality import ImageQualityValidator
from app.ai.inference.disease_engine import disease_engine
from app.hardware.camera import get_camera
from app.db.repositories import ScanRepository, FieldRepository
from app.core.config import settings
from app.core.logging import log_event

MODEL_HASH_SHA256 = "c988ac480a2595eb4ed96c1aaeffb7bae33ccf5418639c8aea9ad7d70128944e"


class VisionPipelineService:
    """Unified crop leaf vision service powered by TEJAS YOLO11n ONNX model."""

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
        3. Preprocess & execute YOLO11n ONNX inference via disease_engine
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
                    confidence_tier="LOW",
                    model_name="tejas_tomato_yolo11n",
                    model_version="1.0.0",
                    model_hash=MODEL_HASH_SHA256,
                    inference_time_ms=0.0,
                    inference_device="CPU",
                    is_demo=False,
                    is_validated=False,
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
            # Encode frame to bytes for disease_engine
            _, buf = cv2.imencode(".jpg", img_bgr)
            image_bytes = buf.tobytes()
        else:
            if not image_bytes:
                return VisionAnalysisResponse(
                    status="invalid_image",
                    prediction="No Image Provided",
                    confidence=0.0,
                    confidence_tier="LOW",
                    model_name="tejas_tomato_yolo11n",
                    model_version="1.0.0",
                    model_hash=MODEL_HASH_SHA256,
                    inference_time_ms=0.0,
                    inference_device="CPU",
                    is_demo=False,
                    is_validated=False,
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
                confidence_tier="LOW",
                model_name="tejas_tomato_yolo11n",
                model_version="1.0.0",
                model_hash=MODEL_HASH_SHA256,
                inference_time_ms=0.0,
                inference_device="CPU",
                is_demo=False,
                is_validated=False,
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

        # Step 4: AI Model Inference via unified disease_engine
        if not disease_engine.is_ready():
            log_event("AI", "ERROR", "TEJAS YOLO11n disease_engine is not ready or model missing.")
            return VisionAnalysisResponse(
                status="ai_unavailable",
                prediction="AI Unavailable",
                confidence=0.0,
                confidence_tier="LOW",
                model_name="tejas_tomato_yolo11n",
                model_version="1.0.0",
                model_hash=MODEL_HASH_SHA256,
                inference_time_ms=0.0,
                inference_device="CPU",
                is_demo=False,
                is_validated=False,
                field_id=field_id,
                image_path=relative_image_path,
                image_quality=quality_res,
                message="AI model weights are not loaded. Ensure tejas_tomato_yolo11n.onnx is present."
            )

        start_inf = time.perf_counter()
        try:
            pred_res = disease_engine.predict(image_bytes)
            inf_time_ms = round((time.perf_counter() - start_inf) * 1000, 2)
        except Exception as e:
            log_event("AI", "ERROR", f"Inference execution failed in disease_engine: {e}")
            return VisionAnalysisResponse(
                status="inference_error",
                prediction="Inference Error",
                confidence=0.0,
                confidence_tier="LOW",
                model_name="tejas_tomato_yolo11n",
                model_version="1.0.0",
                model_hash=MODEL_HASH_SHA256,
                inference_time_ms=0.0,
                inference_device="CPU",
                is_demo=False,
                is_validated=False,
                field_id=field_id,
                image_path=relative_image_path,
                image_quality=quality_res,
                message=f"Inference error: {e}"
            )

        raw_pred_name = pred_res["prediction"]["class_name"]
        raw_conf = pred_res["prediction"]["confidence"]
        top_predictions = pred_res.get("top_predictions", [])

        if raw_confidence_override is not None:
            raw_conf = raw_confidence_override

        pred_class = raw_pred_name.replace("_", " ")

        # Multi-Tier Confidence Evaluation
        threshold = settings.AI_CONFIDENCE_THRESHOLD
        if raw_conf >= 0.85:
            conf_tier = "HIGH"
            status = "accepted"
            farmer_msg = f"High confidence diagnosis: {pred_class}."
            farmer_guide = "Condition identified with high model confidence. Review recommended agronomic practices."
        elif raw_conf >= threshold:
            conf_tier = "MEDIUM"
            status = "accepted"
            farmer_msg = f"Moderate confidence diagnosis: {pred_class}."
            farmer_guide = "Model confidence is moderate. Visually inspect crop and monitor closely."
        else:
            conf_tier = "LOW"
            status = "low_confidence"
            pred_class = "Unknown / Low Confidence"
            farmer_msg = "AI model confidence is below diagnostic threshold (uncertain)."
            farmer_guide = "Unable to confidently identify the condition. Prediction uncertain. Capture another clear photo with better lighting and focus on the leaf."

        # Severity categorization
        pred_lower = raw_pred_name.lower()
        if "healthy" in pred_lower:
            severity = "Low"
        elif "late_blight" in pred_lower or "mosaic" in pred_lower:
            severity = "Critical"
        else:
            severity = "Medium"

        # Step 5: Persist Scan Record in SQLite if DB session & field_id provided
        scan_id = None
        if db and field_id:
            field_repo = FieldRepository(db)
            if field_repo.get_by_id(field_id):
                scan_repo = ScanRepository(db)
                scan_rec = scan_repo.create(
                    field_id=field_id,
                    prediction=pred_class,
                    confidence=round(raw_conf, 4),
                    model_name="tejas_tomato_yolo11n",
                    model_version="1.0.0",
                    image_path=relative_image_path,
                    image_quality=quality_res.score,
                    inference_device="CPU",
                    status="CONFIDENT" if status == "accepted" else "LOW_CONFIDENCE"
                )
                scan_id = scan_rec.id
                log_event("DATABASE", "INFO", f"Saved Scan record ID {scan_id} for Field {field_id} ({pred_class})")

        return VisionAnalysisResponse(
            status=status,
            prediction=pred_class,
            confidence=round(raw_conf, 4),
            confidence_tier=conf_tier,
            model_name="tejas_tomato_yolo11n",
            model_version="1.0.0",
            model_hash=MODEL_HASH_SHA256,
            inference_time_ms=inf_time_ms,
            inference_device="CPU",
            is_demo=False,
            is_validated=True,
            scan_id=scan_id,
            field_id=field_id,
            image_path=relative_image_path,
            image_quality=quality_res,
            crop="Tomato",
            severity=severity,
            message=farmer_msg,
            farmer_guidance=farmer_guide,
            top_predictions=top_predictions
        )


vision_service = VisionPipelineService()
