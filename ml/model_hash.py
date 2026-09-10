"""
KrishiDrishti Edge — SHA-256 Model Integrity & Fingerprint Utility
Computes cryptographic hash of exported PyTorch and ONNX models for forensic auditability and model registry pinning.
"""
import os
import sys
import hashlib
import json

def calculate_sha256(file_path: str) -> str:
    """Calculates SHA-256 checksum of a model file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Model file not found: {file_path}")

    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

compute_sha256 = calculate_sha256

def inspect_model_fingerprint(model_path: str):
    print("=" * 70)
    print("KrishiDrishti Edge — AI Model Cryptographic Integrity Audit")
    print("=" * 70)

    if not os.path.exists(model_path):
        print(f"[!] Model file does not exist at: {model_path}")
        return None

    file_size_bytes = os.path.getsize(model_path)
    file_size_mb = round(file_size_bytes / (1024 * 1024), 2)
    sha256_hash = calculate_sha256(model_path)

    print(f"Model Path : {model_path}")
    print(f"File Size  : {file_size_mb} MB ({file_size_bytes:,} bytes)")
    print(f"SHA-256    : {sha256_hash}")
    print("=" * 70)

    return {
        "model_path": model_path,
        "file_size_bytes": file_size_bytes,
        "file_size_mb": file_size_mb,
        "sha256": sha256_hash
    }

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/models/crop_disease_v1.onnx"
    inspect_model_fingerprint(target)
