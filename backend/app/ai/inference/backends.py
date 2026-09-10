"""
Model Backend Implementations: Demo Backend, ONNX Runtime / OpenCV DNN Backend, Hailo Hardware Backend.
"""
from abc import ABC, abstractmethod
from typing import Tuple, Dict, Any, Optional, List
import time
import os
import yaml
import numpy as np
import cv2
from app.core.logging import log_event

CLASS_NAMES = [
    "Tomato Bacterial Spot",
    "Tomato Early Blight",
    "Tomato Late Blight",
    "Tomato Leaf Mold",
    "Tomato Septoria Leaf Spot",
    "Tomato Two-Spotted Spider Mite",
    "Tomato Target Spot",
    "Tomato Yellow Leaf Curl Virus",
    "Tomato Mosaic Virus",
    "Tomato Healthy"
]

class BaseModelBackend(ABC):
    """Abstract base class for neural network inference execution backends."""

    @abstractmethod
    def load(self, model_path: Optional[str] = None) -> bool:
        """Load model weights and initialize inference session."""
        pass

    @abstractmethod
    def predict(self, input_tensor: np.ndarray) -> Tuple[str, float, Dict[str, Any]]:
        """
        Run inference on preprocessed tensor.
        Returns: (predicted_class: str, confidence: float, extra_meta: Dict[str, Any]).
        """
        pass

    @abstractmethod
    def is_ready(self) -> bool:
        pass

    @abstractmethod
    def get_device(self) -> str:
        """Return execution device identifier: 'HAILO-8' or 'CPU'."""
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        pass

class DemoModelBackend(BaseModelBackend):
    """
    Explicitly Marked Demo Backend for Hackathon Presentation & UI Testing.
    Zero claim of production agricultural accuracy.
    """
    def __init__(self, accelerator_type: str = "CPU"):
        self.accelerator_type = accelerator_type
        self.model_name = "KrishiDrishti-DemoVision-V1"
        self.model_version = "0.1.0-demo-placeholder"
        self._is_loaded = True
        self.supported_classes = CLASS_NAMES

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
    """
    Local ONNX / OpenCV DNN Inference Backend for CPU / Accelerated execution.
    Only active if a physical .onnx model file exists at the configured path.
    """
    def __init__(self, model_path: str, accelerator_type: str = "CPU"):
        self.model_path = model_path
        self.accelerator_type = accelerator_type
        self.session = None
        self.cv2_net = None
        self._is_loaded = False
        self.model_name = "crop_disease_v1"
        self.model_version = "1.0.0"
        self.supported_classes = CLASS_NAMES

    def load(self, model_path: Optional[str] = None) -> bool:
        path = model_path or self.model_path
        if not path or not os.path.exists(path):
            self._is_loaded = False
            log_event("AI", "WARNING", f"ONNX model file not found at: {path}")
            return False

        # Try OpenCV DNN first for robust zero-dependency edge execution
        try:
            self.cv2_net = cv2.dnn.readNetFromONNX(path)
            self._is_loaded = True
            log_event("AI", "INFO", f"Loaded ONNX Model via OpenCV DNN from {path}")
            return True
        except Exception as e_cv2:
            log_event("AI", "WARNING", f"OpenCV DNN load failed ({e_cv2}), trying onnxruntime...")

        try:
            import onnxruntime as ort
            providers = ['CPUExecutionProvider']
            self.session = ort.InferenceSession(path, providers=providers)
            self._is_loaded = True
            log_event("AI", "INFO", f"Loaded ONNX Model via ONNXRuntime from {path}")
            return True
        except Exception as e_ort:
            self._is_loaded = False
            log_event("AI", "ERROR", f"Failed to load ONNX model via all backends: {e_ort}")
            return False

    def predict(self, input_tensor: np.ndarray) -> Tuple[str, float, Dict[str, Any]]:
        if not self._is_loaded:
            raise RuntimeError("ONNX Model not loaded")

        start_t = time.perf_counter()

        # Input shape ensure (1, 3, H, W)
        if len(input_tensor.shape) == 3:
            input_tensor = np.expand_dims(input_tensor, axis=0)

        if self.cv2_net is not None:
            self.cv2_net.setInput(input_tensor)
            outputs = self.cv2_net.forward()
            logits = outputs[0]
        elif self.session is not None:
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: input_tensor})
            logits = outputs[0][0]
        else:
            raise RuntimeError("No active inference runtime session")

        latency = round((time.perf_counter() - start_t) * 1000, 2)

        # Softmax
        exp_logits = np.exp(logits - np.max(logits))
        probs = exp_logits / np.sum(exp_logits)
        top_idx = int(np.argmax(probs))
        top_conf = float(probs[top_idx])

        pred_class = self.supported_classes[top_idx] if top_idx < len(self.supported_classes) else f"Class_{top_idx}"

        return pred_class, top_conf, {
            "crop": "Tomato",
            "predicted_class_index": top_idx,
            "inference_time_ms": latency,
            "is_demo": False
        }

    def is_ready(self) -> bool:
        return self._is_loaded and (self.cv2_net is not None or self.session is not None)

    def get_device(self) -> str:
        return self.accelerator_type

    def get_metadata(self) -> Dict[str, Any]:
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "backend": "OpenCV-DNN-ONNX" if self.cv2_net is not None else "ONNXRuntime",
            "is_demo": False,
            "model_path": self.model_path,
            "is_trained_production_model": False,
            "device": self.accelerator_type,
            "supported_classes": self.supported_classes
        }
