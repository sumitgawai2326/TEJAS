"""
KrishiDrishti Edge — Deterministic Leakage-Safe Data Splitting
Creates 70% Train, 15% Validation, 15% Test partitions in standard Ultralytics Classification format:
ml/data/processed/tomato_cls/
  train/
    <class>/
  val/
    <class>/
  test/
    <class>/
"""
import os
import sys
import random
import shutil

INTERIM_DIR = os.path.join("ml", "data", "interim", "tomato_cleaned")
PROCESSED_DIR = os.path.join("ml", "data", "processed", "tomato_cls")
RANDOM_SEED = 42

def create_deterministic_splits(
    src_dir: str = INTERIM_DIR,
    out_dir: str = PROCESSED_DIR,
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = RANDOM_SEED
):
    print("=" * 70)
    print("KrishiDrishti Edge — Data Splitting Pipeline (70 / 15 / 15)")
    print(f"Random Seed : {seed}")
    print(f"Source      : {src_dir}")
    print(f"Output      : {out_dir}")
    print("=" * 70)

    if not os.path.exists(src_dir):
        print(f"[!] Interim directory not found: {src_dir}")
        return {}

    # Clean previous processed files
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    random.seed(seed)
    splits = ["train", "val", "test"]
    for s in splits:
        os.makedirs(os.path.join(out_dir, s), exist_ok=True)

    split_counts = {s: {} for s in splits}
    total_split_sums = {s: 0 for s in splits}

    for class_name in sorted(os.listdir(src_dir)):
        class_path = os.path.join(src_dir, class_name)
        if not os.path.isdir(class_path):
            continue

        images = sorted([f for f in os.listdir(class_path) if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
        random.shuffle(images)

        n_total = len(images)
        n_train = int(n_total * train_ratio)
        n_val = int(n_total * val_ratio)
        # Remainder goes to test to ensure exact preservation of sample count
        n_test = n_total - n_train - n_val

        train_imgs = images[:n_train]
        val_imgs = images[n_train:n_train + n_val]
        test_imgs = images[n_train + n_val:]

        for s_name, img_list in [("train", train_imgs), ("val", val_imgs), ("test", test_imgs)]:
            dest_dir = os.path.join(out_dir, s_name, class_name)
            os.makedirs(dest_dir, exist_ok=True)
            for img_file in img_list:
                shutil.copy2(
                    os.path.join(class_path, img_file),
                    os.path.join(dest_dir, img_file)
                )
            split_counts[s_name][class_name] = len(img_list)
            total_split_sums[s_name] += len(img_list)

        print(f"Class '{class_name:<30}': Total={n_total:<5} | Train={n_train:<5} | Val={n_val:<5} | Test={n_test:<5}")

    print("\n[+] Partition Summary:")
    print(f"  - Train Partition (70%) : {total_split_sums['train']} images")
    print(f"  - Val Partition   (15%) : {total_split_sums['val']} images")
    print(f"  - Test Partition  (15%) : {total_split_sums['test']} images")
    print(f"  - Grand Total           : {sum(total_split_sums.values())} images")

    return split_counts

if __name__ == "__main__":
    create_deterministic_splits()
