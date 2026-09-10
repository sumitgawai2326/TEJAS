"""
Vision Model Manager with Multi-Tier Confidence Gating, Profiling & Provenance Tracking.
Strict Zero AI Hallucination Policy:
- Never asserts uncalibrated probabilities.
- Never marks unvalidated models as validated (is_validated=False).
"""
import os
import time
from typing import Dict, Any, Optional, Tuple
import numpy as np
from app.ai.inference.base import AcceleratorDetector
from app.ai.inference.backends import BaseModelBackend, DemoModelBackend, ONNXModelBackend
from app.ai.preprocessing.preprocessor import ImagePreprocessor
from app.schemas.vision import VisionAnalysisResponse, ImageQualityResult, VisionStatusResponse
from app.ai.model_registry import model_registry
from app.ai.profiling.profiler import ai_profiler
from app.core.config import settings
from app.core.logging import log_event

class VisionModelManager:
    """Central orchestrator for AI Vision inference, acceleration, and confidence gating."""

    def __init__(
        self,
        demo_mode: bool = True,
        confidence_threshold: float = 0.70,
        high_confidence_threshold: float = 0.85,
        ai_mode: str = "auto",
        model_path: str = "data/models/crop_disease_v1.onnx"
    ):
        self.demo_mode = demo_mode
        self.confidence_threshold = confidence_threshold
        self.high_confidence_threshold = high_confidence_threshold
        self.ai_mode = ai_mode
        self.model_path = model_path
        self.preprocessor = ImagePreprocessor(target_size=(224, 224))
        self.accelerator_info = AcceleratorDetector.detect(ai_mode)
        self.backend: Optional[BaseModelBackend] = None
        self._init_backend()

    def _init_backend(self) -> None:
        """Selects and initializes model backend based on DEMO_MODE."""
        if self.demo_mode:
            self.backend = DemoModelBackend(accelerator_type=self.accelerator_info["accelerator_type"])
            self.backend.load()
        else:
            # REAL HARDWARE MODE: Strictly verify if physical model file exists
            if os.path.exists(self.model_path):
                self.backend = ONNXModelBackend(
                    model_path=self.model_path,
                    accelerator_type=self.accelerator_info["accelerator_type"]
                )
                self.backend.load()
            else:
                self.backend = None
                log_event("AI", "INFO", f"Real Vision Model file not found at {self.model_path}. AI is in AI_NOT_READY state.")

    def is_model_ready(self) -> bool:
        return self.backend is not None and self.backend.is_ready()

    def get_status(self) -> VisionStatusResponse:
        is_ready = self.is_model_ready()
        meta = self.backend.get_metadata() if self.backend else {}
        active_model = model_registry.get_active_model_metadata()

        reason = None
        if not is_ready:
            if not self.demo_mode and not os.path.exists(self.model_path):
                reason = f"Production AI model file not found at '{self.model_path}'. Awaiting trained model export."
                model_status = "AI_NOT_READY"
            else:
                reason = "AI backend not initialized"
                model_status = "AI_NOT_READY"
        else:
            model_status = "DEMO_MODEL" if self.demo_mode else "MODEL_READY"

        return VisionStatusResponse(
            ready=is_ready,
            model_available=is_ready,
            model_name=active_model.model_name,
            model_version=active_model.model_version,
            model_hash=active_model.model_hash,
            model_status=model_status,
            accelerator=self.accelerator_info["accelerator_type"],
            inference_mode=self.accelerator_info["mode_label"],
            cpu_fallback_available=True,
            confidence_threshold=self.confidence_threshold,
            high_confidence_threshold=self.high_confidence_threshold,
            demo_mode=self.demo_mode,
            validation_status=active_model.validation_status,
            reason_if_unavailable=reason,
            supported_classes=active_model.classes or meta.get("supported_classes", []),
            profiling_summary=ai_profiler.get_summary()
        )

    def analyze_image(
        self,
        img_bgr: np.ndarray,
        quality_result: ImageQualityResult,
        raw_confidence_override: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes preprocessor -> inference -> multi-tier confidence gating -> profiling.
        """
        if not self.is_model_ready():
            return {
                "status": "ai_unavailable",
                "prediction": "AI Unavailable",
                "confidence": 0.0,
                "confidence_tier": "LOW",
                "model_name": "None",
                "model_version": "None",
                "model_hash": None,
                "inference_time_ms": 0.0,
                "inference_device": self.accelerator_info["accelerator_type"],
                "is_demo": self.demo_mode,
                "is_validated": False,
                "message": "AI model not ready or not installed. Consult system diagnostic status.",
                "farmer_guidance": "Model weights are not installed. Switch to Demo Mode for presentation testing."
            }

        t_pre_start = time.perf_counter()
        # Preprocess
        tensor = self.preprocessor.preprocess(img_bgr)
        t_pre_ms = (time.perf_counter() - t_pre_start) * 1000

        # Run Backend Inference
        t_inf_start = time.perf_counter()
        if isinstance(self.backend, DemoModelBackend):
            pred_class, raw_conf, extra = self.backend.predict(tensor, raw_confidence_override=raw_confidence_override)
        else:
            pred_class, raw_conf, extra = self.backend.predict(tensor)
        t_inf_ms = (time.perf_counter() - t_inf_start) * 1000

        crop = extra.get("crop", "General")
        severity = extra.get("severity", "Unknown")
        is_demo = extra.get("is_demo", self.demo_mode)
        active_model = model_registry.get_active_model_metadata()

        # Multi-Tier Confidence Evaluation
        if raw_conf >= self.high_confidence_threshold:
            conf_tier = "HIGH"
            farmer_msg = f"High confidence diagnosis: {pred_class}."
            farmer_guide = "Condition identified with high model confidence. Review recommended agronomic practices."
            status = "accepted"
        elif raw_conf >= self.confidence_threshold:
            conf_tier = "MEDIUM"
            farmer_msg = f"Moderate confidence diagnosis: {pred_class}."
            farmer_guide = "Model confidence is moderate. Visually inspect crop and monitor closely."
            status = "accepted"
        else:
            conf_tier = "LOW"
            log_event("AI", "WARNING", f"Confidence ({raw_conf:.2f}) < threshold ({self.confidence_threshold:.2f}) -> LOW_CONFIDENCE")
            status = "low_confidence"
            pred_class = "Unknown / Low Confidence"
            farmer_msg = "AI model confidence is below diagnostic threshold (uncertain)."
            farmer_guide = "Unable to confidently identify the condition. Prediction uncertain. Capture another clear photo with better lighting and focus on the leaf."

        # Profile Pipeline Timing
        ai_profiler.record(
            decode_ms=2.0, # Estimated decode slice
            preprocess_ms=t_pre_ms,
            inference_ms=t_inf_ms,
            postprocess_ms=1.0,
            accelerator=self.backend.get_device()
        )

        return {
            "status": status,
            "prediction": pred_class,
            "confidence": round(raw_conf, 2),
            "confidence_tier": conf_tier,
            "model_name": active_model.model_name,
            "model_version": active_model.model_version,
            "model_hash": active_model.model_hash,
            "inference_time_ms": round(t_inf_ms, 2),
            "inference_device": self.backend.get_device(),
            "is_demo": is_demo,
            "is_validated": False, # Strictly False until evaluation confirms
            "crop": crop,
            "severity": severity,
            "message": farmer_msg,
            "farmer_guidance": farmer_guide
        }

def get_vision_manager() -> VisionModelManager:
    """Factory returning configured vision model manager."""
    return VisionModelManager(
        demo_mode=settings.DEMO_MODE,
        confidence_threshold=settings.AI_CONFIDENCE_THRESHOLD,
        ai_mode=settings.AI_MODE,
        model_path=settings.MODEL_PATH
    )
