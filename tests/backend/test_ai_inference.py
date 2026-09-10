"""
Tests for AI Inference Engine, Hardware Acceleration Detection & Confidence Gating.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from ai.inference.base import AcceleratorDetector, DemoVisionModel, get_vision_model

def test_accelerator_detector_cpu_fallback():
    """Verify runtime detector accurately identifies CPU fallback."""
    res = AcceleratorDetector.detect("cpu")
    assert res["accelerator_type"] == "CPU"
    assert res["mode_label"] == "CPU FALLBACK"
    assert res["is_accelerated"] is False

def test_accelerator_detector_auto_mode():
    """Verify auto mode selects valid runtime device."""
    res = AcceleratorDetector.detect("auto")
    assert res["accelerator_type"] in ["HAILO-8", "CPU"]
    assert res["mode_label"] in ["HAILO ACCELERATED", "CPU FALLBACK"]

def test_ai_model_confidence_gating_pass():
    """Verify prediction passes when confidence >= threshold."""
    model = DemoVisionModel(confidence_threshold=0.70)
    assert model.is_ready() is True
    
    res = model.predict(image_input=None, raw_confidence_override=0.85)
    assert res.confidence == 0.85
    assert res.status == "CONFIDENT"
    assert res.is_low_confidence is False
    assert res.prediction == "Tomato Early Blight"
    assert res.inference_time_ms > 0

def test_ai_model_confidence_gating_fail():
    """
    CRITICAL: Verify when confidence < threshold, model drops prediction
    to 'Unknown / Low Confidence' with status 'LOW_CONFIDENCE'.
    """
    model = DemoVisionModel(confidence_threshold=0.75)
    res = model.predict(image_input=None, raw_confidence_override=0.62)
    assert res.confidence == 0.62
    assert res.status == "LOW_CONFIDENCE"
    assert res.is_low_confidence is True
    assert res.prediction == "Unknown / Low Confidence"
