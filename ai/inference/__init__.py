"""Backward-compatible re-export of AI inference module."""
from app.ai.inference import (
    BaseVisionModel,
    AcceleratorDetector,
    DemoVisionModel,
    get_vision_model,
    BaseModelBackend,
    DemoModelBackend,
    ONNXModelBackend,
    VisionModelManager,
    get_vision_manager,
)

__all__ = [
    "BaseVisionModel",
    "AcceleratorDetector",
    "DemoVisionModel",
    "get_vision_model",
    "BaseModelBackend",
    "DemoModelBackend",
    "ONNXModelBackend",
    "VisionModelManager",
    "get_vision_manager",
]
