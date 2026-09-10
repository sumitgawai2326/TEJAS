"""
Backend Unit and Integration Tests for TEJAS Tomato Disease Inference Pipeline.
Tests POST /api/v1/disease/predict and POST /api/disease/predict.
"""

import io
import os
import glob
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from app.main import app

client = TestClient(app)

# Helper to find a real test image from the dataset
def get_sample_image_bytes() -> bytes:
    dataset_samples = glob.glob("ml/data/processed/tomato_cls/test/*/*.*")
    if not dataset_samples:
        dataset_samples = glob.glob("../ml/data/processed/tomato_cls/test/*/*.*")
    
    if dataset_samples:
        with open(dataset_samples[0], "rb") as f:
            return f.read()

    # Fallback: create a valid synthetic RGB test image if dataset is not found in test path
    img = Image.new("RGB", (256, 256), color=(34, 139, 34))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_disease_predict_valid_image():
    """Test inference with a valid image payload."""
    img_bytes = get_sample_image_bytes()
    response = client.post(
        "/api/v1/disease/predict",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["model"] == "tejas_tomato_yolo11n"
    assert "prediction" in data
    assert "class_name" in data["prediction"]
    assert "confidence" in data["prediction"]
    assert 0.0 <= data["prediction"]["confidence"] <= 1.0
    assert "top_predictions" in data
    assert len(data["top_predictions"]) == 3
    assert data["top_predictions"][0]["class_name"] == data["prediction"]["class_name"]
    assert data["top_predictions"][0]["confidence"] == data["prediction"]["confidence"]
    # Check descending confidence ordering
    confidences = [p["confidence"] for p in data["top_predictions"]]
    assert confidences == sorted(confidences, reverse=True)
    assert "image" in data
    assert data["image"]["width"] > 0
    assert data["image"]["height"] > 0


def test_disease_predict_alias_endpoint():
    """Test alias endpoint /api/disease/predict."""
    img_bytes = get_sample_image_bytes()
    response = client.post(
        "/api/disease/predict",
        files={"file": ("leaf.jpg", img_bytes, "image/jpeg")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["model"] == "tejas_tomato_yolo11n"


def test_disease_predict_empty_file():
    """Test error handling when an empty file (0 bytes) is uploaded."""
    response = client.post(
        "/api/v1/disease/predict",
        files={"file": ("empty.jpg", b"", "image/jpeg")}
    )
    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "empty" in detail.lower() or "no image" in detail.lower()


def test_disease_predict_corrupt_file():
    """Test error handling when corrupt/non-image bytes are uploaded."""
    corrupt_bytes = b"This is not a valid image format by any stretch of imagination!"
    response = client.post(
        "/api/v1/disease/predict",
        files={"file": ("corrupt.jpg", corrupt_bytes, "image/jpeg")}
    )
    assert response.status_code == 400
    detail = response.json().get("detail", "")
    assert "invalid" in detail.lower() or "corrupted" in detail.lower() or "format" in detail.lower()
