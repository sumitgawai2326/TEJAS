"""Backward-compatible re-export of VisionModelManager from app.ai."""
from app.ai.inference.manager import VisionModelManager, get_vision_manager

__all__ = ["VisionModelManager", "get_vision_manager"]
