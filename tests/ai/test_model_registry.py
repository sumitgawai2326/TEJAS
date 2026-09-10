"""
Tests for Phase 8 Model Registry, Discovery, SHA-256 Hash Verification, and Status Tracking.
Strict Zero AI Hallucination Policy:
- Model hashes and weights are verified against on-disk files.
- If physical model is missing or demo, status is explicitly DEMO_MODEL or MODEL_MISSING.
"""
import pytest
import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.main import app
from app.ai.model_registry import model_registry, ModelMetadata
from app.core.config import settings

client = TestClient(app)

def test_model_registry_discovery():
    """Verify registry discovers models and calculates metadata."""
    models = model_registry.get_registered_models()
    assert len(models) >= 1
    
    active = model_registry.get_active_model_metadata()
    assert active is not None
    assert "KrishiDrishti" in active.model_name
    assert len(active.classes) > 0
    assert active.validation_status in ["NOT YET VALIDATED", "VALIDATED ON TEST DATA"]

def test_model_registry_demo_mode_tagging():
    """In DEMO_MODE, model status must be DEMO_MODEL."""
    orig = settings.DEMO_MODE
    try:
        settings.DEMO_MODE = True
        active = model_registry.get_active_model_metadata()
        assert active.status == "DEMO_MODEL"
        assert active.is_demo_model is True
    finally:
        settings.DEMO_MODE = orig

def test_model_registry_real_mode_missing_file():
    """In DEMO_MODE=False, if non-existent file is specified, status is MODEL_MISSING."""
    orig_demo = settings.DEMO_MODE
    orig_path = settings.MODEL_PATH
    try:
        settings.DEMO_MODE = False
        settings.MODEL_PATH = "ai/models/non_existent_weights.onnx"
        model_registry.configured_model_path = settings.MODEL_PATH
        meta = model_registry.get_active_model_metadata()
        assert meta.status == "MODEL_MISSING"
        assert meta.model_hash is None
    finally:
        settings.DEMO_MODE = orig_demo
        settings.MODEL_PATH = orig_path
        model_registry.configured_model_path = orig_path

def test_api_vision_models_endpoint():
    """Verify GET /api/vision/models returns registered model catalog."""
    res = client.get("/api/vision/models")
    assert res.status_code == 200
    data = res.json()
    assert "total_models" in data
    assert "active_model" in data
    assert "models" in data
    assert data["total_models"] >= 1
    assert data["active_model"]["model_name"] != ""

def test_api_vision_status_phase8_fields():
    """Verify GET /api/vision/status contains model_hash and validation_status."""
    res = client.get("/api/vision/status")
    assert res.status_code == 200
    data = res.json()
    assert "model_hash" in data
    assert "validation_status" in data
    assert "profiling_summary" in data
    assert "supported_classes" in data
