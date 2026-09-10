"""
TEJAS — Real Agricultural Model Evaluator (PyTorch & ONNX)
Evaluates PyTorch / ONNX models on Validation or Held-Out Test partitions.
Calculates Top-1 Accuracy, Top-5 Accuracy, Precision, Recall, Macro-F1, and Confusion Matrix.
Zero AI Hallucination: Reports actual numerical measurements only.
"""
import os
import sys
import json
import time
import argparse
from typing import Dict, Any, List, Optional
import numpy as np
from PIL import Image

def evaluate_model(
    model_path: str = "ml/runs/train/tejas_tomato_yolo11n_cls/weights/best.pt",
    split_dir: str = os.path.join("ml", "data", "processed", "tomato_cls", "val"),
    split_name: str = "val",
    output_report_path: str = os.path.join("reports", "model_evaluation_val.json"),
    doc_report_path: Optional[str] = None
) -> Dict[str, Any]:
    print("=" * 70)
    print(f"TEJAS — Offline Model Evaluation on {split_name.upper()} Split")
    print(f"Model Path : {model_path}")
    print(f"Data Split : {split_dir}")
    print("=" * 70)

    if not os.path.exists(split_dir) or not os.path.exists(model_path):
        print(f"[!] Warning: Missing split directory ({split_dir}) or model file ({model_path}).")
        report = {
            "model_path": model_path,
            "status": "NOT YET VALIDATED",
            "validation_status": "NOT YET VALIDATED",
            "total_samples": 0,
            "top1_accuracy": None,
            "top5_accuracy": None,
            "macro_f1": None,
            "macro_precision": None,
            "macro_recall": None,
            "per_class_metrics": {},
            "confusion_matrix": {},
            "notes": "Data split or trained weights missing on disk. Zero AI Hallucination policy enforced."
        }
        os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
        with open(output_report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        return report

    # Load classes
    classes = sorted([d for d in os.listdir(split_dir) if os.path.isdir(os.path.join(split_dir, d))])
    if not classes:
        print("[!] No class folders in data split.")
        return {}

    y_true = []
    y_pred = []
    top5_correct = 0
    t_start = time.time()

    is_onnx = model_path.endswith(".onnx")
    if is_onnx:
        import onnxruntime as ort
        session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        input_name = session.get_inputs()[0].name
        input_shape = session.get_inputs()[0].shape
        img_h = input_shape[2] if len(input_shape) >= 3 and isinstance(input_shape[2], int) else 224
        img_w = input_shape[3] if len(input_shape) >= 4 and isinstance(input_shape[3], int) else 224
    else:
        from ultralytics import YOLO
        model = YOLO(model_path)
        img_h, img_w = 224, 224

    for c_idx, c_name in enumerate(classes):
        c_dir = os.path.join(split_dir, c_name)
        img_files = sorted([f for f in os.listdir(c_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        for f in img_files:
            fpath = os.path.join(c_dir, f)
            y_true.append(c_name)

            if is_onnx:
                img = Image.open(fpath).convert("RGB").resize((img_w, img_h))
                arr = np.array(img, dtype=np.float32) / 255.0
                tensor = np.transpose(arr, (2, 0, 1))[np.newaxis, ...]
                outputs = session.run(None, {input_name: tensor})[0]
                logits = outputs[0]
            else:
                results = model.predict(fpath, imgsz=224, verbose=False, device="cpu")
                probs = results[0].probs
                logits = probs.data.cpu().numpy()

            pred_idx = int(np.argmax(logits))
            pred_class = classes[pred_idx] if pred_idx < len(classes) else "Unknown"
            y_pred.append(pred_class)

            top5_indices = np.argsort(logits)[-5:]
            top5_classes = [classes[i] for i in top5_indices if i < len(classes)]
            if c_name in top5_classes:
                top5_correct += 1

    t_elapsed = round(time.time() - t_start, 2)
    total_samples = len(y_true)
    if total_samples == 0:
        return {}

    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    top1_accuracy = round(float(correct / total_samples), 4)
    top5_accuracy = round(float(top5_correct / total_samples), 4)

    # Confusion matrix
    cm = {c: {c2: 0 for c2 in classes} for c in classes}
    for yt, yp in zip(y_true, y_pred):
        if yt in cm and yp in cm[yt]:
            cm[yt][yp] += 1

    per_class = {}
    precisions, recalls, f1s = [], [], []

    for c in classes:
        tp = cm[c][c]
        fp = sum(cm[other][c] for other in classes if other != c)
        fn = sum(cm[c][other] for other in classes if other != c)
        samples = sum(cm[c].values())

        prec = round(float(tp / (tp + fp)), 4) if (tp + fp) > 0 else 0.0
        rec = round(float(tp / (tp + fn)), 4) if (tp + fn) > 0 else 0.0
        f1 = round(float(2 * prec * rec / (prec + rec)), 4) if (prec + rec) > 0 else 0.0

        if samples > 0:
            precisions.append(prec)
            recalls.append(rec)
            f1s.append(f1)

        per_class[c] = {
            "samples": samples,
            "precision": prec,
            "recall": rec,
            "f1_score": f1
        }

    macro_p = round(float(sum(precisions) / len(precisions)), 4) if precisions else 0.0
    macro_r = round(float(sum(recalls) / len(recalls)), 4) if recalls else 0.0
    macro_f1 = round(float(sum(f1s) / len(f1s)), 4) if f1s else 0.0

    report = {
        "project": "TEJAS",
        "evaluation_split": split_name.upper(),
        "model_path": model_path,
        "status": f"VALIDATED ON {split_name.upper()} DATA",
        "total_samples": total_samples,
        "top1_accuracy": top1_accuracy,
        "top5_accuracy": top5_accuracy,
        "macro_f1": macro_f1,
        "macro_precision": macro_p,
        "macro_recall": macro_r,
        "per_class_metrics": per_class,
        "confusion_matrix": cm,
        "evaluation_duration_seconds": t_elapsed,
        "evaluation_date": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] {split_name.upper()} Top-1 Accuracy: {top1_accuracy * 100:.2f}%")
    print(f"[+] {split_name.upper()} Top-5 Accuracy: {top5_accuracy * 100:.2f}%")
    print(f"[+] {split_name.upper()} Macro F1-Score: {macro_f1:.4f}")
    print(f"[+] Report written to {output_report_path}")

    if doc_report_path:
        os.makedirs(os.path.dirname(doc_report_path), exist_ok=True)
        doc_content = f"""# TEJAS — Offline Model Evaluation & Benchmark Results ({split_name.upper()})

## 1. Summary of {split_name.upper()} Split Evaluation
- **Evaluated Model**: `{model_path}`
- **Evaluation Status**: **VALIDATED ON {split_name.upper()} DATA**
- **Total Samples**: {total_samples}
- **Top-1 Accuracy**: **{top1_accuracy * 100:.2f}%**
- **Top-5 Accuracy**: **{top5_accuracy * 100:.2f}%**
- **Macro F1-Score**: **{macro_f1:.4f}**
- **Macro Precision**: **{macro_p:.4f}**
- **Macro Recall**: **{macro_r:.4f}**
- **Evaluation Date**: {report['evaluation_date']}

---

## 2. Per-Class Performance Breakdown

| Class Name | Samples | Precision | Recall | F1-Score |
|---|---|---|---|---|
"""
        for c, m in per_class.items():
            doc_content += f"| **{c}** | {m['samples']} | {m['precision']:.4f} | {m['recall']:.4f} | {m['f1_score']:.4f} |\n"

        doc_content += """
---

## 3. Real-World Invariant
> [!NOTE]
> Evaluation results reflect performance on the curated laboratory-style PlantVillage dataset. Real field performance across dynamic shadows, dust, and non-foliar backgrounds requires field-based testing.
"""
        with open(doc_report_path, "w", encoding="utf-8") as f:
            f.write(doc_content)

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TEJAS Model Evaluator")
    parser.add_argument("--model", type=str, default="ml/runs/train/tejas_tomato_yolo11n_cls/weights/best.pt")
    parser.add_argument("--data", type=str, default="ml/data/processed/tomato_cls/val")
    parser.add_argument("--split", type=str, default="val")
    parser.add_argument("--output", type=str, default="reports/model_evaluation_val.json")
    parser.add_argument("--doc", type=str, default=None)
    args = parser.parse_args()

    evaluate_model(
        model_path=args.model,
        split_dir=args.data,
        split_name=args.split,
        output_report_path=args.output,
        doc_report_path=args.doc
    )
