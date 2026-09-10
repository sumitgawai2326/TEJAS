"""
TEJAS Real Agricultural Disease Inference Engine.

Loads the trained YOLO11n ONNX model (data/models/tejas_tomato_yolo11n.onnx)
and executes real-time tomato pathology classification with top-1 and top-3 ranking.
"""

import os
import io
import time
import numpy as np
import cv2
from PIL import Image
from typing import Dict, Any, List, Optional, Tuple
from app.core.logging import log_event

CLASS_MAP = {
    0: "Tomato_Bacterial_Spot",
    1: "Tomato_Early_Blight",
    2: "Tomato_Healthy",
    3: "Tomato_Late_Blight",
    4: "Tomato_Leaf_Mold",
    5: "Tomato_Mosaic_Virus",
    6: "Tomato_Septoria_Leaf_Spot",
    7: "Tomato_Target_Spot",
    8: "Tomato_Two-Spotted_Spider_Mite",
    9: "Tomato_Yellow_Leaf_Curl_Virus"
}


class DiseaseInferenceEngine:
    """Production Inference Engine for TEJAS YOLO11n Tomato Disease Classification."""

    _instance: Optional["DiseaseInferenceEngine"] = None

    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            possible_paths = [
                os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../data/models/tejas_tomato_yolo11n.onnx")),
                os.path.abspath("data/models/tejas_tomato_yolo11n.onnx"),
                os.path.abspath("../data/models/tejas_tomato_yolo11n.onnx")
            ]
            self.model_path = next((p for p in possible_paths if os.path.exists(p)), possible_paths[0])
        else:
            self.model_path = os.path.abspath(model_path)

        self.model_name = "tejas_tomato_yolo11n"
        self.class_map = CLASS_MAP
        self.input_size = (224, 224)
        self.session = None
        self.cv2_net = None
        self._is_loaded = False
        self._load_model()

    @classmethod
    def get_instance(cls, model_path: Optional[str] = None) -> "DiseaseInferenceEngine":
        """Singleton accessor for inference engine."""
        if cls._instance is None:
            cls._instance = cls(model_path)
        return cls._instance

    def _load_model(self) -> bool:
        """Loads ONNX model weights via OpenCV DNN or ONNX Runtime."""
        if not os.path.exists(self.model_path):
            log_event("AI_DISEASE", "WARNING", f"ONNX model file not found at: {self.model_path}")
            self._is_loaded = False
            return False

        # Attempt OpenCV DNN
        try:
            self.cv2_net = cv2.dnn.readNetFromONNX(self.model_path)
            self._is_loaded = True
            log_event("AI_DISEASE", "INFO", f"Loaded TEJAS YOLO11n model via OpenCV DNN from {self.model_path}")
            return True
        except Exception as e_cv:
            log_event("AI_DISEASE", "WARNING", f"OpenCV DNN load failed: {e_cv}, attempting ONNXRuntime...")

        # Attempt ONNX Runtime
        try:
            import onnxruntime as ort
            providers = ['CPUExecutionProvider']
            self.session = ort.InferenceSession(self.model_path, providers=providers)
            self._is_loaded = True
            log_event("AI_DISEASE", "INFO", f"Loaded TEJAS YOLO11n model via ONNXRuntime from {self.model_path}")
            return True
        except Exception as e_ort:
            log_event("AI_DISEASE", "ERROR", f"Failed to load ONNX model via any backend: {e_ort}")
            self._is_loaded = False
            return False

    def is_ready(self) -> bool:
        """Returns whether the model is loaded and ready for inference."""
        return self._is_loaded and (self.cv2_net is not None or self.session is not None)

    def preprocess_image(self, image_bytes: bytes) -> Tuple[np.ndarray, int, int]:
        """
        Decodes image bytes, validates dimensions, resizes to (224, 224),
        normalizes [0.0, 1.0], and formats to (1, 3, 224, 224) float32 RGB tensor.
        """
        if not image_bytes or len(image_bytes) == 0:
            raise ValueError("Empty image byte payload received.")

        try:
            pil_img = Image.open(io.BytesIO(image_bytes))
            orig_width, orig_height = pil_img.size
            # Convert any mode (RGBA, CMYK, Grayscale, etc.) to RGB
            pil_img_rgb = pil_img.convert("RGB")
        except Exception as e:
            raise ValueError(f"Invalid or corrupted image format: {e}")

        # Resize to model input dimension (224, 224)
        resized_img = pil_img_rgb.resize(self.input_size, Image.Resampling.BILINEAR)
        img_array = np.array(resized_img, dtype=np.float32) / 255.0  # Normalized [0.0, 1.0]

        # Shape: (H, W, C) -> (C, H, W) -> (1, C, H, W)
        tensor = np.transpose(img_array, (2, 0, 1))
        tensor = np.expand_dims(tensor, axis=0)

        return tensor, orig_width, orig_height

    def predict(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Runs full inference pipeline: decode -> preprocess -> forward pass -> probabilities -> Top-1 & Top-3 ranking.
        """
        if not self.is_ready():
            # Attempt reload once
            if not self._load_model():
                raise RuntimeError("TEJAS disease classification model is not available or loaded.")

        start_time = time.perf_counter()

        tensor, orig_w, orig_h = self.preprocess_image(image_bytes)

        # Forward pass
        if self.cv2_net is not None:
            self.cv2_net.setInput(tensor)
            outputs = self.cv2_net.forward()
            raw_out = outputs[0] if len(outputs.shape) > 1 else outputs
        elif self.session is not None:
            input_name = self.session.get_inputs()[0].name
            outputs = self.session.run(None, {input_name: tensor})
            raw_out = outputs[0][0]
        else:
            raise RuntimeError("No active inference runtime session found.")

        # Flatten output array
        raw_out = np.squeeze(raw_out).astype(np.float64)

        # Check if output is already probabilities (sum close to 1.0 and all >= 0)
        sum_out = np.sum(raw_out)
        if np.isclose(sum_out, 1.0, atol=1e-2) and np.all(raw_out >= -1e-5):
            probs = raw_out / sum_out  # re-normalize slightly for exact sum = 1.0
        else:
            # Apply stable Softmax to raw logits
            exp_logits = np.exp(raw_out - np.max(raw_out))
            probs = exp_logits / np.sum(exp_logits)

        # Sort class predictions by confidence descending
        sorted_indices = np.argsort(probs)[::-1]

        top_predictions = []
        for idx in sorted_indices[:3]:
            class_idx = int(idx)
            class_name = self.class_map.get(class_idx, f"Class_{class_idx}")
            confidence = float(probs[class_idx])
            top_predictions.append({
                "class_name": class_name,
                "confidence": round(confidence, 4)
            })

        top1 = top_predictions[0]
        inference_latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        log_event(
            "AI_DISEASE",
            "INFO",
            f"Prediction: {top1['class_name']} ({top1['confidence']:.4f}) in {inference_latency_ms}ms"
        )

        return {
            "success": True,
            "model": self.model_name,
            "prediction": top1,
            "top_predictions": top_predictions,
            "image": {
                "width": orig_w,
                "height": orig_h
            }
        }


# Global singleton instance provider
disease_engine = DiseaseInferenceEngine.get_instance()
