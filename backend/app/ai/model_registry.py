"""
AI Model Registry & Lifecycle Manager for KrishiDrishti Edge.
Discovers local neural network weights, computes SHA-256 hashes, inspects metadata,
and tracks model validation status.
Strict Zero AI Hallucination Policy: Unvalidated models remain 'NOT YET VALIDATED'.
"""
import os
import hashlib
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.core.config import settings
from app.core.logging import log_event

class ModelMetadata(BaseModel):
    model_id: str
    model_name: str
    model_version: str
    model_hash: Optional[str] = None
    model_path: Optional[str] = None
    status: str = Field(..., description="REAL_MODEL, DEMO_MODEL, MODEL_MISSING, MODEL_INVALID, MODEL_INCOMPATIBLE")
    task_type: str = "crop_pathology_classification"
    framework: str = "ONNXRuntime"
    format: str = ".onnx"
    target_accelerator: str = "Hailo-8 / CPU Fallback"
    input_shape: List[int] = Field(default_factory=lambda: [1, 3, 224, 224])
    classes: List[str] = Field(default_factory=list)
    training_dataset: Optional[str] = None
    validation_status: str = Field(default="NOT YET VALIDATED", description="NOT YET VALIDATED or VALIDATED ON TEST DATA")
    is_demo_model: bool = False
    details: Optional[str] = None

class ModelRegistry:
    """Central registry tracking all available and configured AI models."""

    def __init__(self, models_dir: str = "data/models", configured_model_path: Optional[str] = None):
        self.models_dir = models_dir
        self.configured_model_path = configured_model_path or settings.MODEL_PATH

    @staticmethod
    def calculate_file_hash(file_path: str) -> Optional[str]:
        """Computes SHA-256 checksum of model binary file for auditability."""
        if not os.path.exists(file_path):
            return None
        sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            log_event("AI", "WARNING", f"Could not compute hash for {file_path}: {e}")
            return None

    def get_registered_models(self) -> List[ModelMetadata]:
        """Scans filesystem and returns metadata for all candidate models."""
        models: List[ModelMetadata] = []

        # 1. Register Built-in Demo Placeholder Model
        demo_meta = ModelMetadata(
            model_id="krishidrishti-demo-v1",
            model_name="KrishiDrishti-DemoVision-V1",
            model_version="0.1.0-demo-placeholder",
            model_hash="demo-placeholder-hash-00000000",
            model_path=None,
            status="DEMO_MODEL",
            task_type="crop_pathology_classification",
            framework="DemoEngine",
            format="in-memory",
            target_accelerator="CPU / Hailo Simulator",
            input_shape=[1, 3, 224, 224],
            classes=[
                "Tomato Early Blight",
                "Tomato Late Blight",
                "Potato Late Blight",
                "Cotton Bacterial Blight",
                "Rice Blast",
                "Wheat Rust",
                "Healthy Crop Leaf"
            ],
            training_dataset="None (Demo Synthetic)",
            validation_status="NOT YET VALIDATED",
            is_demo_model=True,
            details="Standard prototype demo model active when DEMO_MODE=true."
        )
        models.append(demo_meta)

        # 2. Check Configured Production Model Path
        conf_path = self.configured_model_path
        if conf_path and os.path.exists(conf_path):
            file_hash = self.calculate_file_hash(conf_path)
            # Inspect dimensions if ONNX
            input_shape = [1, 3, 224, 224]
            classes = []
            try:
                import onnxruntime as ort
                sess = ort.InferenceSession(conf_path, providers=['CPUExecutionProvider'])
                input_meta = sess.get_inputs()[0]
                if input_meta.shape:
                    input_shape = [s if isinstance(s, int) and s > 0 else 1 for s in input_meta.shape]
            except Exception:
                pass

            real_meta = ModelMetadata(
                model_id="configured-production-model",
                model_name=os.path.basename(conf_path),
                model_version="1.0.0",
                model_hash=file_hash,
                model_path=conf_path,
                status="REAL_MODEL",
                task_type="crop_pathology_classification",
                framework="ONNXRuntime",
                format=os.path.splitext(conf_path)[1],
                target_accelerator="Hailo-8 / CPU Fallback",
                input_shape=input_shape,
                classes=classes,
                training_dataset="Configured Production Weights",
                validation_status="NOT YET VALIDATED",
                is_demo_model=False,
                details=f"Production model binary detected at {conf_path}."
            )
            models.append(real_meta)
        elif conf_path:
            # Model file missing
            missing_meta = ModelMetadata(
                model_id="configured-production-model",
                model_name=os.path.basename(conf_path),
                model_version="1.0.0",
                model_hash=None,
                model_path=conf_path,
                status="MODEL_MISSING",
                task_type="crop_pathology_classification",
                framework="ONNXRuntime",
                format=os.path.splitext(conf_path)[1],
                target_accelerator="Hailo-8 / CPU Fallback",
                input_shape=[1, 3, 224, 224],
                classes=[],
                training_dataset=None,
                validation_status="NOT YET VALIDATED",
                is_demo_model=False,
                details=f"Production weights file not found at '{conf_path}'. AI status remains AI_NOT_READY in real hardware mode."
            )
            models.append(missing_meta)

        return models

    def get_active_model_metadata(self) -> ModelMetadata:
        """Returns metadata of currently active inference backend."""
        models = self.get_registered_models()
        if settings.DEMO_MODE:
            return models[0] # Demo model
        
        # Real Mode: find real model or missing
        for m in models:
            if not m.is_demo_model and m.status == "REAL_MODEL":
                return m
            
        for m in models:
            if not m.is_demo_model:
                return m
            
        return models[0]

model_registry = ModelRegistry()
