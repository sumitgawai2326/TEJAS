"""Backward-compatible re-export of AI backend inference components from app.ai."""
from app.ai.inference.backends import (
    BaseModelBackend,
    DemoModelBackend,
    ONNXModelBackend,
    CLASS_NAMES,
)

__all__ = ["BaseModelBackend", "DemoModelBackend", "ONNXModelBackend", "CLASS_NAMES"]
