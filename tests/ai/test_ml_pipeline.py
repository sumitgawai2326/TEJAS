"""
Tests for KrishiDrishti Edge ML Pipeline components.
Validates dataset manifest, class map, split policies, hashing, duplicate detection, ONNX graph validation, and evaluation reporting.
"""

import os
import json
import tempfile
import yaml
import pytest
import numpy as np
import cv2
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
CLASS_MAP_PATH = DATA_DIR / "class_map.yaml"
DATASET_MANIFEST_PATH = DATA_DIR / "dataset_manifest.yaml"
MODEL_PATH = DATA_DIR / "models" / "crop_disease_v1.onnx"
EVAL_REPORT_PATH = PROJECT_ROOT / "reports" / "model_evaluation.json"
PROFILE_REPORT_PATH = PROJECT_ROOT / "reports" / "model_profile.json"


class TestClassMap:
    """Validates data/class_map.yaml against agricultural and engineering standards."""

    def test_class_map_exists(self):
        assert CLASS_MAP_PATH.exists(), f"Class map not found at {CLASS_MAP_PATH}"

    def test_class_map_schema(self):
        with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert data.get("crop") == "tomato"
        assert data.get("total_classes") == 10
        assert data.get("task_type") == "single_label_classification"
        assert "classes" in data

        classes = data["classes"]
        assert len(classes) == 10

        expected_keys = {"id", "name", "pathogen", "type", "severity_category"}
        valid_types = {"bacterial", "fungal", "oomycete", "pest_infestation", "viral", "healthy"}
        valid_severities = {"NORMAL", "LOW", "MEDIUM", "HIGH", "CRITICAL"}

        for idx, item in classes.items():
            assert isinstance(idx, int)
            assert 0 <= idx <= 9
            for k in expected_keys:
                assert k in item, f"Missing key '{k}' in class {idx}"
            assert item["type"] in valid_types, f"Invalid type '{item['type']}' in class {idx}"
            assert item["severity_category"] in valid_severities, f"Invalid severity in class {idx}"

    def test_healthy_class_present(self):
        with open(CLASS_MAP_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        healthy_found = False
        for _, item in data["classes"].items():
            if item["id"] == "tomato_healthy":
                healthy_found = True
                assert item["severity_category"] == "NORMAL"
                assert item["type"] == "healthy"
        assert healthy_found, "tomato_healthy class must be present"


class TestDatasetManifest:
    """Validates data/dataset_manifest.yaml for provenance, licensing, and citation."""

    def test_dataset_manifest_exists(self):
        assert DATASET_MANIFEST_PATH.exists(), f"Manifest not found at {DATASET_MANIFEST_PATH}"

    def test_dataset_manifest_content(self):
        with open(DATASET_MANIFEST_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        assert "dataset_name" in data
        assert "source" in data
        assert "license" in data
        assert "citation" in data
        assert "download_status" in data
        assert "verified_status" in data
        assert data.get("selected_for_training") is True
        assert len(data.get("secondary_datasets", [])) > 0


class TestModelHashing:
    """Validates SHA-256 model hashing utility."""

    def test_compute_sha256(self):
        from ml.model_hash import compute_sha256

        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".bin") as tmp:
            tmp.write("krishidrishti-edge-test-content")
            tmp_path = tmp.name

        try:
            h = compute_sha256(tmp_path)
            assert isinstance(h, str)
            assert len(h) == 64
            # Consistent hash check
            assert h == compute_sha256(tmp_path)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


class TestDuplicateDetection:
    """Validates exact duplicate file detection using MD5/SHA-256."""

    def test_find_duplicates_in_dir(self):
        from ml.scripts.check_duplicates import find_duplicates

        with tempfile.TemporaryDirectory() as tmpdir:
            f1 = Path(tmpdir) / "img1.jpg"
            f2 = Path(tmpdir) / "img2.jpg"
            f3 = Path(tmpdir) / "img3.jpg"

            f1.write_bytes(b"content-a")
            f2.write_bytes(b"content-a")  # duplicate of f1
            f3.write_bytes(b"content-b")  # unique

            res = find_duplicates(tmpdir, check_perceptual=False)
            assert len(res["exact_duplicates"]) == 1
            hash_val, files = list(res["exact_duplicates"].items())[0]
            assert len(files) == 2
            assert str(f1) in files
            assert str(f2) in files


class TestONNXModelExecution:
    """Validates ONNX model file and inference engine execution."""

    def test_onnx_model_file_exists(self):
        assert MODEL_PATH.exists(), f"Model file missing at {MODEL_PATH}"

    def test_onnx_opencv_dnn_inference(self):
        net = cv2.dnn.readNetFromONNX(str(MODEL_PATH))
        dummy_blob = np.random.randn(1, 3, 224, 224).astype(np.float32)
        net.setInput(dummy_blob)
        out = net.forward()
        assert out.shape == (1, 10), f"Expected shape (1, 10), got {out.shape}"
        assert not np.isnan(out).any(), "Output contains NaN values"


class TestEvaluationReports:
    """Validates that evaluation and profiling reports comply with Zero AI/Hardware Hallucination."""

    def test_evaluation_report_schema(self):
        assert EVAL_REPORT_PATH.exists(), f"Missing evaluation report at {EVAL_REPORT_PATH}"
        with open(EVAL_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "model_path" in data
        assert "status" in data
        assert "total_test_samples" in data
        assert "accuracy" in data
        assert "macro_f1" in data
        assert "per_class_metrics" in data

    def test_profiler_report_schema(self):
        assert PROFILE_REPORT_PATH.exists(), f"Missing profiler report at {PROFILE_REPORT_PATH}"
        with open(PROFILE_REPORT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        assert "hardware_status" in data
        assert data["hardware_status"]["raspberry_pi_5_cpu"] == "PENDING PHYSICAL BENCHMARK"
        assert data["hardware_status"]["raspberry_pi_ai_hat_hailo8"] == "PENDING PHYSICAL BENCHMARK"
        assert "latency_breakdown_ms" in data
        assert data["latency_breakdown_ms"]["total_e2e_latency_ms"] > 0
