"""Backward-compatible re-export of AI base inference components from app.ai."""
from app.ai.inference.base import (
    AcceleratorDetector,
    BaseVisionModel,
    DemoVisionModel,
    get_vision_model,
)

__all__ = ["AcceleratorDetector", "BaseVisionModel", "DemoVisionModel", "get_vision_model"]
