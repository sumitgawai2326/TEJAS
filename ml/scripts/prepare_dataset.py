"""
KrishiDrishti Edge — Real Dataset Preparation & Cleaning Pipeline
Standardizes image formats, RGB channels, eliminates duplicate hashes, and saves clean files into ml/data/interim/.
"""
import os
import sys
import shutil
import hashlib
from PIL import Image

RAW_DIR = os.path.join("ml", "data", "raw", "plantvillage_tomato")
INTERIM_DIR = os.path.join("ml", "data", "interim", "tomato_cleaned")

def compute_sha256(filepath: str) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def prepare_dataset(src_dir: str = RAW_DIR, dest_dir: str = INTERIM_DIR):
    print("=" * 70)
    print("KrishiDrishti Edge — Real Data Cleaning & Deduplication Pipeline")
    print(f"Source : {src_dir}")
    print(f"Dest   : {dest_dir}")
    print("=" * 70)

    if not os.path.exists(src_dir):
        print(f"[!] Source directory {src_dir} does not exist.")
        return

    # Clean previous interim data
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)
    os.makedirs(dest_dir, exist_ok=True)

    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    seen_hashes = set()

    total_processed = 0
    total_valid = 0
    total_rejected = 0
    total_duplicates_skipped = 0
    class_counts = {}

    for class_name in sorted(os.listdir(src_dir)):
        src_class_path = os.path.join(src_dir, class_name)
        if not os.path.isdir(src_class_path):
            continue

        dest_class_path = os.path.join(dest_dir, class_name)
        os.makedirs(dest_class_path, exist_ok=True)
        class_valid = 0

        for img_name in sorted(os.listdir(src_class_path)):
            if os.path.splitext(img_name)[1].lower() not in valid_exts:
                continue

            total_processed += 1
            src_img_path = os.path.join(src_class_path, img_name)

            # Check hash duplicate
            try:
                f_hash = compute_sha256(src_img_path)
                if f_hash in seen_hashes:
                    total_duplicates_skipped += 1
                    continue
                seen_hashes.add(f_hash)
            except Exception:
                total_rejected += 1
                continue

            # Standardize filename and format
            base_name, _ = os.path.splitext(img_name)
            dest_img_path = os.path.join(dest_class_path, f"{base_name}.jpg")

            try:
                with Image.open(src_img_path) as img:
                    img_rgb = img.convert("RGB")
                    # Minimum dimension check
                    if img_rgb.width < 64 or img_rgb.height < 64:
                        total_rejected += 1
                        continue
                    img_rgb.save(dest_img_path, format="JPEG", quality=95)
                    total_valid += 1
                    class_valid += 1
            except Exception as e:
                total_rejected += 1

        class_counts[class_name] = class_valid
        print(f"Class '{class_name:<32}': {class_valid:>5} clean images.")

    print(f"\nSummary:")
    print(f"  - Total Scanned         : {total_processed}")
    print(f"  - Valid Standardized    : {total_valid}")
    print(f"  - Duplicates Skipped    : {total_duplicates_skipped}")
    print(f"  - Rejected / Corrupt    : {total_rejected}")

    return class_counts

if __name__ == "__main__":
    prepare_dataset()
