"""
TEJAS — Ultralytics PyTorch to ONNX Model Exporter & Validator
Exports trained YOLO classification weights to edge-deployable ONNX format.
Performs ONNX Runtime numerical verification against PyTorch inference on real test images.
Calculates SHA-256 cryptographic hashes.
"""
import os
import sys
import shutil
import time
import hashlib
import json
import argparse
from typing import Dict, Any, List
import numpy as np
from PIL import Image

def calculate_sha256(filepath: str) -> str:
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(65536), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def export_and_verify(
    weights_path: str = "ml/runs/train/tejas_tomato_yolo11n_cls/weights/best.pt",
    output_onnx_path: str = "data/models/tejas_tomato_yolo11n.onnx",
    test_sample_dir: str = "ml/data/processed/tomato_cls/test",
    imgsz: int = 224,
    dynamic: bool = False,
    report_path: str = "reports/onnx_export_verification.json"
) -> Dict[str, Any]:
    print("=" * 70)
    print("TEJAS — ONNX Model Export & Verification Pipeline")
    print(f"Source Weights: {weights_path}")
    print(f"Target ONNX   : {output_onnx_path}")
    print("=" * 70)

    if not os.path.exists(weights_path):
        print(f"[!] Source PyTorch weights not found at: {weights_path}")
        return {"status": "FAIL", "error": f"Weights not found: {weights_path}"}

    try:
        from ultralytics import YOLO
    except ImportError:
        print("[!] Ultralytics library not available.")
        return {"status": "FAIL", "error": "Ultralytics not installed"}

    # Compute PyTorch weights SHA-256
    pt_sha256 = calculate_sha256(weights_path)
    print(f"[+] PyTorch Weights SHA-256: {pt_sha256}")

    print("\n[+] Loading PyTorch model for ONNX export...")
    model = YOLO(weights_path)

    print(f"[+] Exporting to ONNX (imgsz={imgsz}, dynamic={dynamic}, opset=17)...")
    t_start = time.time()
    exported_path = model.export(
        format="onnx",
        imgsz=imgsz,
        dynamic=dynamic,
        opset=17,
        simplify=False
    )
    t_elapsed = round(time.time() - t_start, 2)
    print(f"[+] ONNX export completed in {t_elapsed}s -> {exported_path}")

    # Copy to target destination (DO NOT overwrite crop_disease_v1.onnx)
    os.makedirs(os.path.dirname(output_onnx_path), exist_ok=True)
    if os.path.exists(exported_path):
        shutil.copy2(exported_path, output_onnx_path)
        print(f"[+] Exported model deployed to target path: {output_onnx_path}")

    onnx_sha256 = calculate_sha256(output_onnx_path)
    print(f"[+] Exported ONNX SHA-256: {onnx_sha256}")

    # Verify numerical consistency with ONNX Runtime
    print("\n[+] Verifying ONNX model numerical consistency with ONNX Runtime...")
    import onnxruntime as ort
    session = ort.InferenceSession(output_onnx_path, providers=["CPUExecutionProvider"])
    input_name = session.get_inputs()[0].name
    input_shape = session.get_inputs()[0].shape

    # Test inference on real sample images
    verification_results = []
    classes = sorted([d for d in os.listdir(test_sample_dir) if os.path.isdir(os.path.join(test_sample_dir, d))])
    
    max_abs_diff = 0.0
    matched_predictions = 0
    total_tested = 0

    for c in classes:
        c_dir = os.path.join(test_sample_dir, c)
        imgs = [f for f in os.listdir(c_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if not imgs:
            continue
        # Test 1 sample per class
        test_img_path = os.path.join(c_dir, imgs[0])
        total_tested += 1

        # PyTorch prediction
        pt_res = model.predict(test_img_path, imgsz=imgsz, verbose=False, device="cpu")
        pt_probs = pt_res[0].probs.data.cpu().numpy()
        pt_pred = int(np.argmax(pt_probs))

        # ONNX Runtime prediction (Ultralytics classify graph directly outputs softmax probabilities)
        img = Image.open(test_img_path).convert("RGB").resize((imgsz, imgsz))
        arr = np.array(img, dtype=np.float32) / 255.0
        tensor = np.transpose(arr, (2, 0, 1))[np.newaxis, ...]
        onnx_outs = session.run(None, {input_name: tensor})[0]
        onnx_probs = onnx_outs[0]
        onnx_pred = int(np.argmax(onnx_probs))

        diff = float(np.max(np.abs(pt_probs - onnx_probs)))
        if diff > max_abs_diff:
            max_abs_diff = diff

        is_match = (pt_pred == onnx_pred)
        if is_match:
            matched_predictions += 1

        verification_results.append({
            "class": c,
            "image": os.path.basename(test_img_path),
            "pytorch_prediction": classes[pt_pred] if pt_pred < len(classes) else "Unknown",
            "onnx_prediction": classes[onnx_pred] if onnx_pred < len(classes) else "Unknown",
            "prediction_match": is_match,
            "max_probability_diff": round(diff, 6)
        })

    report = {
        "project": "TEJAS",
        "task": "onnx_export_and_verification",
        "source_pytorch_weights": weights_path,
        "pytorch_weights_sha256": pt_sha256,
        "exported_onnx_path": output_onnx_path,
        "exported_onnx_sha256": onnx_sha256,
        "export_duration_seconds": t_elapsed,
        "input_name": input_name,
        "input_shape": list(input_shape),
        "onnxruntime_samples_tested": total_tested,
        "prediction_match_rate": round(float(matched_predictions / total_tested), 4) if total_tested > 0 else 0.0,
        "max_absolute_diff": round(max_abs_diff, 6),
        "numerical_status": "PASS" if (max_abs_diff < 1e-3 and matched_predictions == total_tested) else "CHECK",
        "samples": verification_results,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[+] ONNX Verification Status : {report['numerical_status']}")
    print(f"[+] Prediction Match Rate    : {matched_predictions}/{total_tested} ({report['prediction_match_rate']*100:.1f}%)")
    print(f"[+] Max Numerical Diff       : {max_abs_diff:.6f}")
    print(f"[+] Verification report saved: {report_path}")

    return report

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TEJAS ONNX Export & Verification")
    parser.add_argument("--weights", type=str, default="ml/runs/train/tejas_tomato_yolo11n_cls/weights/best.pt")
    parser.add_argument("--output", type=str, default="data/models/tejas_tomato_yolo11n.onnx")
    parser.add_argument("--test-dir", type=str, default="ml/data/processed/tomato_cls/test")
    parser.add_argument("--imgsz", type=int, default=224)
    parser.add_argument("--report", type=str, default="reports/onnx_export_verification.json")
    args = parser.parse_args()

    export_and_verify(
        weights_path=args.weights,
        output_onnx_path=args.output,
        test_sample_dir=args.test_dir,
        imgsz=args.imgsz,
        report_path=args.report
    )
