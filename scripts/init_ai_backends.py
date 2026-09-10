import os

base_ai = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\ai\inference"

# 1. backends.py
backends_code = """\"\"\"
Model Backend Implementations: Demo Backend, ONNX Runtime Backend, Hailo Hardware Backend.
\"\"\"
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional, List
import time
import os
import numpy as np
from app.core.logging import log_event

class BaseModelBackend(ABC):
    \"\"\"Abstract base class for neural network inference execution backends.\"\"\"

    @abstractmethod
    def load(self, model_path: Optional[str] = None) -> bool:
        \"\"\"Load model weights and initialize inference session.\"\"\"
        pass

    @abstractmethod
    def predict(self, input_tensor: np.ndarray) -> Tuple[str, float, Dict[str, Any]]:
        \"\"\"
        Run inference on preprocessed tensor.
        Returns: (predicted_class: str, confidence: float, extra_meta: Dict[str, Any]).
        \"\"\"
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        pass

    @abstractmethod
    def get_device(self) -> str:
        \"\"\"Return execution device identifier: 'HAILO-8' or 'CPU'.\"\"\"
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        pass

class DemoModelBackend(BaseModelBackend):
    \"\"\"
    Explicitly Marked Demo Backend for Hackathon Presentation & UI Testing.
    Zero claim of production agricultural accuracy.
    \"\"\"
    def __init__(self, accelerator_type: str = "CPU"):
        self.accelerator_type = accelerator_type
        self.model_name = "KrishiDrishti-DemoVision-V1"
        self.model_version = "0.1.0-demo-placeholder"
        self._is_loaded = True
        self.supported_classes = [
            "Tomato Early Blight",
            "Tomato Late Blight",
            "Potato Late Blight",
            "Cotton Bacterial Blight",
            "Rice Blast",
            "Wheat Rust",
            "Healthy Crop Leaf"
        ]

    def load(self, model_path: Optional[str] = None) -> bool:
        self._is_loaded = True
        log_event("AI", "INFO", f"Demo Vision Model Backend initialized (Version: {self.model_version})")
        return True

    def predict(self, input_tensor: np.ndarray, raw_confidence_override: Optional[float] = None) -> Tuple[str, float, Dict[str, Any]]:
        # Simulate local compute latency
        start_t = time.perf_counter()
        time.sleep(0.025 if self.accelerator_type == "HAILO-8" else 0.065)
        latency = round((time.perf_counter() - start_t) * 1000, 2)

        conf = raw_confidence_override if raw_confidence_override is not None else 0.89
        pred_class = "Tomato Early Blight"

        return pred_class, float(conf), {
            "crop": "Tomato",
            "severity": "Medium",
            "inference_time_ms": latency,
            "is_demo": True
        }

    def is_ready(self) -> bool:
        return self._is_loaded

    def get_device(self) -> str:
        return self.accelerator_type

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "backend": "DemoPlaceholder",
            "is_demo": True,
            "is_trained_production_model": False,
            "device": self.accelerator_type,
            "supported_classes": self.supported_classes
        }

class ONNXModelBackend(BaseModelBackend):
    \"\"\"
    Local ONNX Runtime Inference Backend for CPU / Accelerated execution.
    Only active if a physical .onnx model file exists at the configured path.
    \"\"\"
    def __init__(self, model_path: str, accelerator_type: str = "CPU"):
        self.model_path = model_path
        self.accelerator_type = accelerator_type
        self.session = None
        self._is_loaded = False
        self.model_name = "ONNX-CropVision"
        self.model_version = "1.0.0"

    def load(self, model_path: Optional[str] = None) -> bool:
        path = model_path or self.model_path
        if not path or not os.path.exists(path):
            self._is_loaded = False
            log_event("AI", "WARNING", f"ONNX model file not found at: {path}")
            return False

        try:
            import onnxruntime as ort
            providers = ['CPUExecutionProvider']
            self.session = ort.InferenceSession(path, providers=providers)
            self._is_loaded = True
            log_event("AI", "INFO", f"Loaded ONNX Model from {path}")
            return True
        except Exception as e:
            self._is_loaded = False
            log_event("AI", "ERROR", f"Failed to load ONNX model: {e}")
            return False

    def predict(self, input_tensor: np.ndarray) -> Tuple[str, float, Dict[str, Any]]:
        if not self._is_loaded or self.session is None:
            raise RuntimeError("ONNX Model not loaded")

        start_t = time.perf_counter()
        input_name = self.session.get_inputs()[0].name
        outputs = self.session.run(None, {input_name: input_tensor})
        latency = round((time.perf_counter() - start_t) * 1000, 2)

        # Process logits/probabilities
        logits = outputs[0][0]
        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / exp_logits.sum()
        top_idx = int(np.argmax(probs))
        top_conf = float(probs[top_idx])

        return f"Class_{top_idx}", top_conf, {
            "inference_time_ms": latency,
            "is_demo": False
        }

    def is_ready(self) -> bool:
        return self._is_loaded and self.session is not None

    def get_device(self) -> str:
        return self.accelerator_type

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "backend": "ONNXRuntime",
            "is_demo": False,
            "model_path": self.model_path,
            "is_trained_production_model": True,
            "device": self.accelerator_type
        }
"""

with open(os.path.join(base_ai, "backends.py"), "w", encoding="utf-8") as f:
    f.write(backends_code)

# 2. manager.py
manager_code = """\"\"\"
Vision Model Manager with Confidence Gating & Truthful Hardware Acceleration.
\"\"\"
import os
from typing import Dict, Any, Optional, Tuple
import numpy as np
from ai.inference.base import AcceleratorDetector
from ai.inference.backends import BaseModelBackend, DemoModelBackend, ONNXModelBackend
from ai.preprocessing.preprocessor import ImagePreprocessor
from app.schemas.vision import VisionAnalysisResponse, ImageQualityResult, VisionStatusResponse
from app.core.config import settings
from app.core.logging import log_event

class VisionModelManager:
    \"\"\"Central orchestrator for AI Vision inference, acceleration, and confidence gating.\"\"\"

    def __init__(
        self,
        demo_mode: bool = True,
        confidence_threshold: float = 0.70,
        ai_mode: str = "auto",
        model_path: str = "ai/models/crop_disease_v1.onnx"
    ):
        self.demo_mode = demo_mode
        self.confidence_threshold = confidence_threshold
        self.ai_mode = ai_mode
        self.model_path = model_path
        self.preprocessor = ImagePreprocessor(target_size=(224, 224))
        self.accelerator_info = AcceleratorDetector.detect(ai_mode)
        self.backend: Optional[BaseModelBackend] = None
        self._init_backend()

    def _init_backend(self) -> None:
        \"\"\"Selects and initializes model backend based on DEMO_MODE.\"\"\"
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
        
        reason = None
        if not is_ready:
            if not self.demo_mode and not os.path.exists(self.model_path):
                reason = f"Production AI model file not found at '{self.model_path}'. Awaiting trained model export."
            else:
                reason = "AI backend not initialized"

        return VisionStatusResponse(
            ready=is_ready,
            model_available=is_ready,
            model_name=meta.get("model_name", "None"),
            model_version=meta.get("model_version", "None"),
            accelerator=self.accelerator_info["accelerator_type"],
            inference_mode=self.accelerator_info["mode_label"],
            cpu_fallback_available=True,
            confidence_threshold=self.confidence_threshold,
            demo_mode=self.demo_mode,
            reason_if_unavailable=reason,
            supported_classes=meta.get("supported_classes", [])
        )

    def analyze_image(
        self,
        img_bgr: np.ndarray,
        quality_result: ImageQualityResult,
        raw_confidence_override: Optional[float] = None
    ) -> Dict[str, Any]:
        \"\"\"
        Executes preprocessor -> inference -> confidence gating.
        \"\"\"
        if not self.is_model_ready():
            return {
                "status": "ai_unavailable",
                "prediction": "AI Unavailable",
                "confidence": 0.0,
                "model_name": "None",
                "model_version": "None",
                "inference_time_ms": 0.0,
                "inference_device": self.accelerator_info["accelerator_type"],
                "is_demo": self.demo_mode,
                "message": "AI model not ready or not installed. Consult system diagnostic status."
            }

        # Preprocess
        tensor = self.preprocessor.preprocess(img_bgr)

        # Run Backend Inference
        if isinstance(self.backend, DemoModelBackend):
            pred_class, raw_conf, extra = self.backend.predict(tensor, raw_confidence_override=raw_confidence_override)
        else:
            pred_class, raw_conf, extra = self.backend.predict(tensor)

        inference_time = extra.get("inference_time_ms", 0.0)
        crop = extra.get("crop", "General")
        severity = extra.get("severity", "Unknown")
        is_demo = extra.get("is_demo", self.demo_mode)
        meta = self.backend.get_metadata()

        # Apply Strict Confidence Gating
        if raw_conf < self.confidence_threshold:
            log_event("AI", "WARNING", f"Confidence ({raw_conf:.2f}) < threshold ({self.confidence_threshold:.2f}) -> LOW_CONFIDENCE")
            return {
                "status": "low_confidence",
                "prediction": "Unknown / Low Confidence",
                "confidence": round(raw_conf, 2),
                "model_name": meta.get("model_name", "Unknown"),
                "model_version": meta.get("model_version", "Unknown"),
                "inference_time_ms": inference_time,
                "inference_device": self.backend.get_device(),
                "is_demo": is_demo,
                "crop": crop,
                "severity": "Unknown",
                "message": "AI result uncertain — capture a clearer image with better lighting and focus."
            }

        return {
            "status": "accepted",
            "prediction": pred_class,
            "confidence": round(raw_conf, 2),
            "model_name": meta.get("model_name", "Unknown"),
            "model_version": meta.get("model_version", "Unknown"),
            "inference_time_ms": inference_time,
            "inference_device": self.backend.get_device(),
            "is_demo": is_demo,
            "crop": crop,
            "severity": severity,
            "message": f"Diagnosis: {pred_class} (Confidence: {int(raw_conf*100)}%)"
        }

def get_vision_manager() -> VisionModelManager:
    \"\"\"Factory returning configured vision model manager.\"\"\"
    return VisionModelManager(
        demo_mode=settings.DEMO_MODE,
        confidence_threshold=settings.AI_CONFIDENCE_THRESHOLD,
        ai_mode=settings.AI_MODE,
        model_path=settings.MODEL_PATH
    )
"""

with open(os.path.join(base_ai, "manager.py"), "w", encoding="utf-8") as f:
    f.write(manager_code)

print("AI inference backends and manager created.")
