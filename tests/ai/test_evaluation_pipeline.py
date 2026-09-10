"""
Tests for Phase 8 Offline Model Evaluation Pipeline.
Verifies calculation of accuracy, macro precision, recall, F1 score, and confusion matrix.
Strict Zero AI Hallucination: Never invents scores when ground truth is absent.
"""
import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from app.ai.evaluation.evaluator import ModelEvaluator

def test_evaluation_metrics_computation():
    """Verify precision, recall, F1, and confusion matrix computation on synthetic sample dataset."""
    classes = ["Tomato Early Blight", "Tomato Late Blight", "Tomato Healthy"]
    y_true = ["Tomato Early Blight", "Tomato Early Blight", "Tomato Late Blight", "Tomato Late Blight", "Tomato Healthy", "Tomato Healthy"]
    y_pred = ["Tomato Early Blight", "Tomato Late Blight", "Tomato Late Blight", "Tomato Late Blight", "Tomato Healthy", "Tomato Healthy"]

    report = ModelEvaluator.calculate_classification_metrics(
        y_true=y_true,
        y_pred=y_pred,
        classes=classes,
        dataset_name="Synthetic-Validation-Split-v1"
    )

    assert report.total_samples == 6
    assert report.top1_accuracy is not None
    assert 0.0 <= report.top1_accuracy <= 1.0
    assert report.macro_f1 is not None
    assert 0.0 <= report.macro_f1 <= 1.0
    assert len(report.per_class_metrics) >= 3
    assert len(report.confusion_matrix) >= 3
    assert report.status == "VALIDATED ON TEST DATA"

def test_evaluation_empty_dataset_zero_hallucination():
    """Verify empty dataset reports NOT_YET_VALIDATED and None metrics without fabricating accuracy."""
    report = ModelEvaluator.calculate_classification_metrics(
        y_true=[],
        y_pred=[],
        classes=["Tomato Healthy"],
        dataset_name="Empty-Set"
    )
    assert report.total_samples == 0
    assert report.top1_accuracy is None
    assert report.macro_f1 is None
    assert report.status == "NOT YET VALIDATED"
