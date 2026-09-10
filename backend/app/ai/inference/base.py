"""
AI Inference & Acceleration Abstraction Layer for KrishiDrishti Edge.
Provides BaseVisionModel, AcceleratorDetector, and DemoVisionModel with strict confidence gating.
"""
import os
import sys
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from app.schemas.ai import PredictionResult, AIStatus
from app.core.logging import log_event

class AcceleratorDetector:
    """Detects physical presence of Raspberry Pi AI HAT+ (Hailo-8 / HailoRT)."""

    @staticmethod
    def detect(configured_mode: str = "auto") -> Dict[str, Any]:
        """
        Determines execution engine without false reporting.
        Modes: 'auto', 'hailo', 'cpu'.
        """
        if configured_mode.lower() == "cpu":
            return {
                "accelerator_type": "CPU",
                "mode_label": "CPU FALLBACK",
                "is_accelerated": False,
                "device_node": None,
                "driver_available": False,
                "details": "Forced CPU fallback execution configured"
            }

        # Check for physical Hailo PCIe character device or library
        hailo_device_exists = os.path.exists("/dev/hailo0")
        hailort_installed = False
        try:
            import hailo_platform  # type: ignore
            hailort_installed = True
        except ImportError:
            hailort_installed = False

        if hailo_device_exists or (hailort_installed and configured_mode.lower() in ["hailo", "auto"]):
            return {
                "accelerator_type": "HAILO-8",
                "mode_label": "HAILO ACCELERATED",
                "is_accelerated": True,
                "device_node": "/dev/hailo0" if hailo_device_exists else "PCIe HailoRT",
                "driver_available": True,
                "details": "Raspberry Pi AI HAT+ (Hailo-8) Hardware Accelerator active"
            }

        return {
            "accelerator_type": "CPU",
            "mode_label": "CPU FALLBACK",
            "is_accelerated": False,
            "device_node": None,
            "driver_available": False,
            "details": "AI HAT+ not detected on PCIe bus. Running optimized CPU fallback."
        }

class BaseVisionModel(ABC):
    """Abstract Base Interface for Edge Vision AI Models."""

    def __init__(self, model_name: str, model_version: str, confidence_threshold: float = 0.70):
        self.model_name = model_name
        self.model_version = model_version
        self.confidence_threshold = confidence_threshold
        self._is_loaded = False

    @abstractmethod
    def load_model(self, model_path: Optional[str] = None) -> bool:
        """Load neural network weights into memory or accelerator."""
        pass

    @abstractmethod
    def predict(self, image_input: Any, raw_confidence_override: Optional[float] = None) -> PredictionResult:
        """
        Run inference on preprocessed crop/leaf image with confidence gating.
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Return model version, supported classes, and confidence threshold."""
        pass

    @abstractmethod
    def get_device(self) -> str:
        """Return active execution device (HAILO or CPU)."""
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        """Return True if model is loaded and ready for inference."""
        pass

class DemoVisionModel(BaseVisionModel):
    """
    Clearly marked Demo Model / Placeholder for SIH Prototype.
    Implements confidence gating without fabricating trained model claims.
    """

    def __init__(self, confidence_threshold: float = 0.70, ai_mode: str = "auto"):
        super().__init__(
            model_name="KrishiDrishti-DemoVision-V1",
            model_version="0.1.0-demo-placeholder",
            confidence_threshold=confidence_threshold
        )
        self.ai_mode = ai_mode
        self._device_info = AcceleratorDetector.detect(ai_mode)
        self._is_loaded = True
        self.supported_classes = [
            "Tomato Early Blight",
            "Tomato Late Blight",
            "Potato Late Blight",
            "Cotton Bacterial Blight",
            "Rice Blast",
            "Wheat Rust",
            "Healthy Leaf",
            "Unknown / Low Confidence"
        ]

    def load_model(self, model_path: Optional[str] = None) -> bool:
        self._is_loaded = True
        log_event("AI", "INFO", f"Demo Vision Model loaded (Version: {self.model_version})")
        return True

    def predict(self, image_input: Any, raw_confidence_override: Optional[float] = None) -> PredictionResult:
        """
        Runs inference and applies configurable confidence gating.
        If confidence < threshold, returns LOW_CONFIDENCE and 'Unknown / Low Confidence'.
        """
        start_t = time.perf_counter()
        
        # Simulate local compute latency
        time.sleep(0.035 if self._device_info["is_accelerated"] else 0.085)
        latency_ms = round((time.perf_counter() - start_t) * 1000, 2)

        # Use override if provided (for unit testing confidence gating) or demo default 0.88
        confidence = raw_confidence_override if raw_confidence_override is not None else 0.88

        # Apply strict Confidence Gating
        if confidence < self.confidence_threshold:
            log_event("AI", "WARNING", f"Prediction confidence ({confidence:.2f}) < threshold ({self.confidence_threshold:.2f}) -> LOW_CONFIDENCE")
            return PredictionResult(
                prediction="Unknown / Low Confidence",
                confidence=round(confidence, 2),
                model_name=self.model_name,
                model_version=self.model_version,
                inference_time_ms=latency_ms,
                inference_device=self.get_device(),
                status="LOW_CONFIDENCE",
                is_low_confidence=True,
                crop="General",
                severity="Unknown"
            )

        return PredictionResult(
            prediction="Tomato Early Blight",
            confidence=round(confidence, 2),
            model_name=self.model_name,
            model_version=self.model_version,
            inference_time_ms=latency_ms,
            inference_device=self.get_device(),
            status="CONFIDENT",
            is_low_confidence=False,
            crop="Tomato",
            severity="Medium"
        )

    def get_model_info(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "confidence_threshold": self.confidence_threshold,
            "status": "DEMO_PLACEHOLDER",
            "is_demo_model": True,
            "is_trained_production_model": False,
            "accelerator_type": self._device_info["accelerator_type"],
            "inference_mode": self._device_info["mode_label"],
            "supported_classes": self.supported_classes
        }

    def get_device(self) -> str:
        return self._device_info["accelerator_type"]

    def is_ready(self) -> bool:
        return self._is_loaded

    def get_status(self) -> AIStatus:
        info = self.get_model_info()
        return AIStatus(
            ready=self.is_ready(),
            status="READY",
            accelerator_type=info["accelerator_type"],
            inference_mode=info["inference_mode"],
            model_name=self.model_name,
            model_version=self.model_version,
            is_demo_model=True,
            confidence_threshold=self.confidence_threshold,
            supported_classes=self.supported_classes,
            details=self._device_info["details"]
        )

def get_vision_model(confidence_threshold: float = 0.70, ai_mode: str = "auto") -> BaseVisionModel:
    """Factory returning active Vision Model instance."""
    return DemoVisionModel(confidence_threshold=confidence_threshold, ai_mode=ai_mode)
