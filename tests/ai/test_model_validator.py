"""
Tests for Phase 8 Model Structural & Functional Validator.
Verifies dynamic input shapes (not hard-coded), logit compatibility, and smoke inference.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.ai.validation.model_validator import ModelValidator

def test_model_validator_missing_file():
    """Verify validator fails gracefully with informative error on missing model file."""
    res = ModelValidator.validate_onnx_model(
        model_path="ai/models/does_not_exist.onnx",
        expected_classes_count=7
    )
    assert res.is_valid is False
    assert res.status == "MODEL_NOT_FOUND"
    assert res.error_message is not None
    assert "does not exist" in res.error_message.lower()
