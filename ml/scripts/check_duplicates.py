"""
KrishiDrishti Edge — Dataset Duplicate & Perceptual Near-Duplicate Checker
Computes cryptographic hashes (SHA-256) and perceptual difference hashes (dHash) to detect exact copies and visual near-duplicates.
"""
import os
import sys
import hashlib
from collections import defaultdict
from PIL import Image
import numpy as np

def compute_file_hash(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def compute_dhash(image_path: str, hash_size: int = 8) -> str:
    """Computes difference hash (dHash) for visual perceptual similarity."""
    try:
        with Image.open(image_path) as img:
            # Resize to (hash_size + 1, hash_size) grayscale
            img = img.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.BILINEAR)
            pixels = np.array(img, dtype=np.float32)
            # Compare adjacent pixels
            diff = pixels[:, 1:] > pixels[:, :-1]
            return "".join(["1" if b else "0" for b in diff.flatten()])
    except Exception:
        return ""

def check_duplicates(dataset_dir: str, check_perceptual: bool = True):
    print("=" * 70)
    print(f"KrishiDrishti Edge — Cryptographic & Perceptual Duplicate Audit")
    print(f"Target Directory: {dataset_dir}")
    print("=" * 70)

    if not os.path.exists(dataset_dir):
        print(f"[!] Directory not found: {dataset_dir}")
        return {}

    sha_map = defaultdict(list)
    dhash_map = defaultdict(list)
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    total_scanned = 0

    for root, _, files in os.walk(dataset_dir):
        for f in sorted(files):
            if os.path.splitext(f)[1].lower() in valid_exts:
                fpath = os.path.join(root, f)
                try:
                    h = compute_file_hash(fpath)
                    sha_map[h].append(fpath)
                    total_scanned += 1

                    if check_perceptual:
                        dh = compute_dhash(fpath)
                        if dh:
                            dhash_map[dh].append(fpath)
                except Exception as e:
                    print(f"[!] Error hashing {fpath}: {e}")

    exact_duplicates = {h: paths for h, paths in sha_map.items() if len(paths) > 1}
    exact_dup_file_count = sum(len(paths) - 1 for paths in exact_duplicates.values())

    near_duplicates = {dh: paths for dh, paths in dhash_map.items() if len(paths) > 1}
    near_dup_file_count = sum(len(paths) - 1 for paths in near_duplicates.values())

    print(f"\n[+] Total Images Scanned       : {total_scanned}")
    print(f"[+] Unique SHA-256 Hashes      : {len(sha_map)}")
    print(f"[+] Exact Duplicate Groups     : {len(exact_duplicates)} ({exact_dup_file_count} redundant files)")
    if check_perceptual:
        print(f"[+] Perceptual Similarity Groups: {len(near_duplicates)} ({near_dup_file_count} potential near-duplicate frames)")

    if exact_duplicates:
        print("\n[!] Exact Duplicate Groups Sample (first 5):")
        for idx, (h, paths) in enumerate(list(exact_duplicates.items())[:5]):
            print(f"  Group {idx+1} ({len(paths)} copies):")
            for p in paths:
                print(f"    - {p}")

    return {
        "total_scanned": total_scanned,
        "exact_duplicates": exact_duplicates,
        "exact_dup_file_count": exact_dup_file_count,
        "near_duplicates": near_duplicates,
        "near_dup_file_count": near_dup_file_count
    }

find_duplicates = check_duplicates

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join("ml", "data", "raw", "plantvillage_tomato")
    check_duplicates(target)
