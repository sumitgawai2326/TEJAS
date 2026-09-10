"""
KrishiDrishti Edge — Dataset Inspector
Scans raw and interim dataset directories, validates image readability, dimensions, and file extensions.
"""
import os
import sys
from PIL import Image
import yaml

def inspect_dir(data_dir: str):
    print("=" * 70)
    print(f"KrishiDrishti Edge — Inspecting Dataset at: {data_dir}")
    print("=" * 70)

    if not os.path.exists(data_dir):
        print(f"[!] Directory {data_dir} does not exist.")
        return {}

    stats = {}
    valid_exts = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for class_name in sorted(os.listdir(data_dir)):
        class_path = os.path.join(data_dir, class_name)
        if not os.path.isdir(class_path):
            continue

        images = [f for f in os.listdir(class_path) if os.path.splitext(f)[1].lower() in valid_exts]
        corrupt = 0
        dims = set()

        for img_name in images:
            img_path = os.path.join(class_path, img_name)
            try:
                with Image.open(img_path) as img:
                    img.verify()
                with Image.open(img_path) as img:
                    dims.add(img.size)
            except Exception:
                corrupt += 1

        stats[class_name] = {
            "total_images": len(images),
            "valid_images": len(images) - corrupt,
            "corrupt_images": corrupt,
            "resolutions": list(dims)[:3]
        }
        print(f"Class: {class_name:<35} | Total: {len(images):<5} | Valid: {len(images)-corrupt:<5} | Corrupt: {corrupt}")

    return stats

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join("ml", "data", "raw", "plantvillage_tomato")
    inspect_dir(target)
