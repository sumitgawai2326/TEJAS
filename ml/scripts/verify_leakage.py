"""
KrishiDrishti Edge — Cross-Partition Data Leakage Auditor
Validates that zero image hashes (cryptographic SHA-256 and perceptual dHash) cross the boundaries between Train, Val, and Test splits.
"""
import os
import sys
import hashlib
from collections import defaultdict
from PIL import Image
import numpy as np

PROCESSED_DIR = os.path.join("ml", "data", "processed", "tomato_cls")

def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_dhash(image_path: str, hash_size: int = 8) -> str:
    try:
        with Image.open(image_path) as img:
            img = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
            pixels = np.array(img, dtype=np.float32)
            diff = pixels[:, 1:] > pixels[:, :-1]
            return "".join(["1" if b else "0" for b in diff.flatten()])
    except Exception:
        return ""

def audit_leakage(base_dir: str = PROCESSED_DIR):
    print("=" * 70)
    print("KrishiDrishti Edge — Cross-Partition Data Leakage Audit")
    print(f"Directory: {base_dir}")
    print("=" * 70)

    splits = ["train", "val", "test"]
    partition_hashes = {}
    partition_dhashes = {}

    for s in splits:
        s_dir = os.path.join(base_dir, s)
        sha_set = set()
        dh_map = defaultdict(list)
        count = 0

        for root, _, files in os.walk(s_dir):
            for f in files:
                if f.lower().endswith(('.jpg', '.jpeg', '.png')):
                    fpath = os.path.join(root, f)
                    h = compute_sha256(fpath)
                    sha_set.add(h)
                    dh = compute_dhash(fpath)
                    if dh:
                        dh_map[dh].append(fpath)
                    count += 1

        partition_hashes[s] = sha_set
        partition_dhashes[s] = dh_map
        print(f"Partition '{s:<5}': {count:>5} images indexed ({len(sha_set)} unique SHA-256).")

    # 1. Cryptographic Exact Overlap
    train_val_overlap = partition_hashes["train"].intersection(partition_hashes["val"])
    train_test_overlap = partition_hashes["train"].intersection(partition_hashes["test"])
    val_test_overlap = partition_hashes["val"].intersection(partition_hashes["test"])

    print("\n[1] Exact Cryptographic SHA-256 Leakage Results:")
    print(f"  - Train <-> Val Overlap  : {len(train_val_overlap)} hashes")
    print(f"  - Train <-> Test Overlap : {len(train_test_overlap)} hashes")
    print(f"  - Val <-> Test Overlap   : {len(val_test_overlap)} hashes")

    # 2. Perceptual Similarity Overlap
    train_dh_keys = set(partition_dhashes["train"].keys())
    val_dh_keys = set(partition_dhashes["val"].keys())
    test_dh_keys = set(partition_dhashes["test"].keys())

    train_val_dh_overlap = train_dh_keys.intersection(val_dh_keys)
    train_test_dh_overlap = train_dh_keys.intersection(test_dh_keys)
    val_test_dh_overlap = val_dh_keys.intersection(test_dh_keys)

    print("\n[2] Perceptual Visual Similarity (dHash) Results:")
    print(f"  - Train <-> Val Overlap  : {len(train_val_dh_overlap)} dHash keys")
    print(f"  - Train <-> Test Overlap : {len(train_test_dh_overlap)} dHash keys")
    print(f"  - Val <-> Test Overlap   : {len(val_test_dh_overlap)} dHash keys")

    is_clean = (len(train_val_overlap) == 0 and len(train_test_overlap) == 0 and len(val_test_overlap) == 0)
    if is_clean:
        print("\n[+] VERIFIED: ZERO EXACT CRYPTOGRAPHIC LEAKAGE DETECTED.")
    else:
        print("\n[!] CRITICAL: Exact data leakage detected across partitions!")

    return {
        "train_val_exact": len(train_val_overlap),
        "train_test_exact": len(train_test_overlap),
        "val_test_exact": len(val_test_overlap),
        "train_val_perceptual": len(train_val_dh_overlap),
        "train_test_perceptual": len(train_test_dh_overlap),
        "val_test_perceptual": len(val_test_dh_overlap),
        "is_leakage_free": is_clean
    }

if __name__ == "__main__":
    audit_leakage()
