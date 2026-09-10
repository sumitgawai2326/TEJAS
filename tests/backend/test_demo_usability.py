"""
Tests for Phase 13B Demo Usability:
Curated sample images catalog, raw image retrieval, real YOLO11n prediction,
and DEMO_MODE integration.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_list_sample_images():
    """Verify GET /api/v1/disease/samples returns the full 10 curated sample items."""
    response = client.get("/api/v1/disease/samples")
    assert response.status_code == 200
    samples = response.json()
    assert isinstance(samples, list)
    assert len(samples) == 10
    
    sample_ids = [s["id"] for s in samples]
    assert "bacterial_spot" in sample_ids
    assert "early_blight" in sample_ids
    assert "healthy" in sample_ids
    assert "late_blight" in sample_ids
    assert "yellow_leaf_curl" in sample_ids

    for sample in samples:
        assert "id" in sample
        assert "label" in sample
        assert "class_name" in sample
        assert "filename" in sample
        assert "url" in sample


def test_get_sample_image_endpoint():
    """Verify GET /api/v1/disease/samples/{sample_id}/image returns raw JPEG bytes."""
    response = client.get("/api/v1/disease/samples/bacterial_spot/image")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert len(response.content) > 1000  # valid image size


def test_get_nonexistent_sample_image_returns_404():
    """Verify invalid sample ID returns 404."""
    response = client.get("/api/v1/disease/samples/non_existent_disease_xyz/image")
    assert response.status_code == 404


def test_sample_image_real_inference_execution():
    """Verify that fetching a sample image and sending to predict yields real YOLO11n output."""
    img_resp = client.get("/api/v1/disease/samples/early_blight/image")
    assert img_resp.status_code == 200
    
    files = {"file": ("sample_early_blight.jpg", img_resp.content, "image/jpeg")}
    predict_resp = client.post("/api/v1/disease/predict", files=files)
    
    assert predict_resp.status_code == 200
    data = predict_resp.json()
    assert data["success"] is True
    assert data["model"] == "tejas_tomato_yolo11n"
    assert data["prediction"]["class_name"] == "Tomato_Early_Blight"
    assert data["prediction"]["confidence"] >= 0.85
    assert len(data["top_predictions"]) >= 3


def test_sample_image_guided_wizard_flow():
    """Verify that a sample image passes through /api/vision/analyze into SQLite scan record."""
    img_resp = client.get("/api/v1/disease/samples/healthy/image")
    assert img_resp.status_code == 200

    files = {"file": ("sample_healthy.jpg", img_resp.content, "image/jpeg")}
    data_form = {"field_id": "1"}
    analyze_resp = client.post("/api/vision/analyze", data=data_form, files=files)

    assert analyze_resp.status_code == 200
    res = analyze_resp.json()
    assert res["status"] in ["accepted", "valid_diagnosis", "healthy_detected"]
    assert res["prediction"] in ["Tomato Healthy", "Tomato_Healthy"]
    assert res["confidence"] >= 0.85
    assert res["image_quality"]["valid"] is True
