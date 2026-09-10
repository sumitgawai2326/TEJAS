"""
Offline Model Evaluation & Benchmark Pipeline for KrishiDrishti Edge.
Evaluates classification models against labeled test splits.
Calculates Top-1 Accuracy, Precision, Recall, F1-Score, and Confusion Matrix.
Strict Zero AI Hallucination Policy: Returns 'NOT YET VALIDATED' if no test split is present.
"""
import os
import json
import time
from typing import Dict, Any, List, Optional
import numpy as np
from pydantic import BaseModel, Field
from app.core.logging import log_event

class ClassMetrics(BaseModel):
    class_name: str
    samples_count: int
    true_positives: int
    false_positives: int
    false_negatives: int
    precision: float
    recall: float
    f1_score: float

class EvaluationReport(BaseModel):
    model_name: str
    model_version: str
    model_hash: Optional[str] = None
    dataset_name: str
    evaluation_date: str
    status: str = Field(..., description="VALIDATED ON TEST DATA or NOT YET VALIDATED")
    total_samples: int
    top1_accuracy: Optional[float] = None
    macro_precision: Optional[float] = None
    macro_recall: Optional[float] = None
    macro_f1: Optional[float] = None
    per_class_metrics: List[ClassMetrics] = Field(default_factory=list)
    confusion_matrix: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    limitations: List[str] = Field(default_factory=list)

class ModelEvaluator:
    """Runs rigorous offline evaluation on candidate edge neural network models."""

    @staticmethod
    def calculate_classification_metrics(
        y_true: List[str],
        y_pred: List[str],
        classes: List[str],
        model_name: str = "CandidateModel",
        model_version: str = "1.0.0",
        model_hash: Optional[str] = None,
        dataset_name: str = "Verified-Agricultural-TestSplit"
    ) -> EvaluationReport:
        """Computes multi-class classification evaluation metrics from ground truth and predictions."""
        if not y_true or not y_pred or len(y_true) != len(y_pred):
            return EvaluationReport(
                model_name=model_name,
                model_version=model_version,
                model_hash=model_hash,
                dataset_name=dataset_name,
                evaluation_date=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                status="NOT YET VALIDATED",
                total_samples=0,
                limitations=["No test samples provided for evaluation."]
            )

        total_samples = len(y_true)
        unique_classes = sorted(list(set(classes + y_true + y_pred)))

        # Initialize confusion matrix
        cm: Dict[str, Dict[str, int]] = {c: {c2: 0 for c2 in unique_classes} for c in unique_classes}
        for yt, yp in zip(y_true, y_pred):
            if yt in cm and yp in cm[yt]:
                cm[yt][yp] += 1

        # Accuracy
        correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
        accuracy = round(float(correct / total_samples), 4)

        # Per-class metrics
        per_class: List[ClassMetrics] = []
        precisions: List[float] = []
        recalls: List[float] = []
        f1s: List[float] = []

        for c in unique_classes:
            tp = cm[c][c]
            fp = sum(cm[other][c] for other in unique_classes if other != c)
            fn = sum(cm[c][other] for other in unique_classes if other != c)
            samples = sum(cm[c].values())

            prec = round(float(tp / (tp + fp)), 4) if (tp + fp) > 0 else 0.0
            rec = round(float(tp / (tp + fn)), 4) if (tp + fn) > 0 else 0.0
            f1 = round(float(2 * prec * rec / (prec + rec)), 4) if (prec + rec) > 0 else 0.0

            if samples > 0:
                precisions.append(prec)
                recalls.append(rec)
                f1s.append(f1)

            per_class.append(ClassMetrics(
                class_name=c,
                samples_count=samples,
                true_positives=tp,
                false_positives=fp,
                false_negatives=fn,
                precision=prec,
                recall=rec,
                f1_score=f1
            ))

        macro_p = round(float(sum(precisions) / len(precisions)), 4) if precisions else 0.0
        macro_r = round(float(sum(recalls) / len(recalls)), 4) if recalls else 0.0
        macro_f = round(float(sum(f1s) / len(f1s)), 4) if f1s else 0.0

        report = EvaluationReport(
            model_name=model_name,
            model_version=model_version,
            model_hash=model_hash,
            dataset_name=dataset_name,
            evaluation_date=time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            status="VALIDATED ON TEST DATA",
            total_samples=total_samples,
            top1_accuracy=accuracy,
            macro_precision=macro_p,
            macro_recall=macro_r,
            macro_f1=macro_f,
            per_class_metrics=per_class,
            confusion_matrix=cm,
            limitations=[
                "Metrics reflect performance on the evaluated test split.",
                "Performance may vary under extreme sunlight variations or novel pathogen strains."
            ]
        )

        log_event("AI", "INFO", f"Evaluation completed for {model_name}: Accuracy={accuracy}, F1={macro_f}")
        return report
