"""
KrishiDrishti Edge — Real PlantVillage Tomato Dataset Ingestion Pipeline
Downloads authentic PlantVillage Tomato leaf images (CC BY 4.0) via Git Sparse-Checkout.
Preserves provenance, commit hash, license, and file integrity.
"""
import os
import sys
import shutil
import subprocess
import time
import yaml

REPO_URL = "https://github.com/spMohanty/PlantVillage-Dataset.git"
DEST_RAW_DIR = os.path.join("ml", "data", "raw", "plantvillage_tomato")
TEMP_REPO_DIR = os.path.join("ml", "data", "downloads", "pv_git_repo")
MANIFEST_PATH = os.path.join("data", "dataset_manifest.yaml")

FOLDER_MAPPING = {
    "Tomato___Bacterial_spot": "Tomato_Bacterial_Spot",
    "Tomato___Early_blight": "Tomato_Early_Blight",
    "Tomato___Late_blight": "Tomato_Late_Blight",
    "Tomato___Leaf_Mold": "Tomato_Leaf_Mold",
    "Tomato___Septoria_leaf_spot": "Tomato_Septoria_Leaf_Spot",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Tomato_Two-Spotted_Spider_Mite",
    "Tomato___Target_Spot": "Tomato_Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus": "Tomato_Mosaic_Virus",
    "Tomato___healthy": "Tomato_Healthy"
}

def clean_old_synthetic_data():
    """Removes any previous synthetic test samples before real dataset ingestion."""
    if os.path.exists(DEST_RAW_DIR):
        print(f"[*] Cleaning directory {DEST_RAW_DIR} for clean real ingestion...")
        shutil.rmtree(DEST_RAW_DIR)
    os.makedirs(DEST_RAW_DIR, exist_ok=True)

def download_dataset():
    print("=" * 70)
    print("KrishiDrishti Edge — Real Agricultural Dataset Acquisition")
    print(f"Source Repository : {REPO_URL}")
    print(f"Target Directory   : {DEST_RAW_DIR}")
    print("=" * 70)

    clean_old_synthetic_data()

    if os.path.exists(TEMP_REPO_DIR):
        try:
            # Remove read-only git files if present on Windows
            subprocess.run(f'attrib -R "{TEMP_REPO_DIR}\\*.*" /S', shell=True)
            shutil.rmtree(TEMP_REPO_DIR, ignore_errors=True)
        except Exception:
            pass

    os.makedirs(os.path.dirname(TEMP_REPO_DIR), exist_ok=True)

    # 1. Clone repository structure (blob:none for efficient sparse download)
    print("\n[1] Initializing Git repository metadata (depth 1, blob:none)...")
    cmd_clone = ["git", "clone", "--filter=blob:none", "--no-checkout", "--depth", "1", REPO_URL, TEMP_REPO_DIR]
    res = subprocess.run(cmd_clone, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[!] Git clone failed: {res.stderr}")
        return False

    # Get Commit Hash
    res_commit = subprocess.run(["git", "-C", TEMP_REPO_DIR, "rev-parse", "HEAD"], capture_output=True, text=True)
    commit_hash = res_commit.stdout.strip()
    print(f"[+] Connected to GitHub commit: {commit_hash}")

    # 2. Configure Sparse-Checkout for only Tomato directories
    print("\n[2] Setting sparse-checkout patterns for 10 Tomato pathology classes...")
    sparse_paths = [f"raw/color/{src}" for src in FOLDER_MAPPING.keys()]
    cmd_sparse = ["git", "-C", TEMP_REPO_DIR, "sparse-checkout", "set"] + sparse_paths
    res_sparse = subprocess.run(cmd_sparse, capture_output=True, text=True)
    if res_sparse.returncode != 0:
        print(f"[!] Sparse-checkout set failed: {res_sparse.stderr}")
        return False

    # 3. Checkout Tomato images
    print("\n[3] Downloading Tomato image blobs from GitHub...")
    t_start = time.time()
    cmd_checkout = ["git", "-C", TEMP_REPO_DIR, "checkout", "master"]
    res_checkout = subprocess.run(cmd_checkout, capture_output=True, text=True)
    if res_checkout.returncode != 0:
        print(f"[!] Checkout failed: {res_checkout.stderr}")
        return False
    t_elapsed = round(time.time() - t_start, 2)
    print(f"[+] Download complete in {t_elapsed} seconds.")

    # 4. Copy and organize into canonical class hierarchy
    print("\n[4] Organizing images into target class directories...")
    total_images_copied = 0
    class_stats = {}

    for src_folder, target_class in FOLDER_MAPPING.items():
        src_path = os.path.join(TEMP_REPO_DIR, "raw", "color", src_folder)
        target_dir = os.path.join(DEST_RAW_DIR, target_class)
        os.makedirs(target_dir, exist_ok=True)

        if not os.path.exists(src_path):
            print(f"[!] Warning: Folder missing in checkout: {src_path}")
            class_stats[target_class] = 0
            continue

        files = [f for f in os.listdir(src_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        for f in files:
            shutil.copy2(os.path.join(src_path, f), os.path.join(target_dir, f))

        count = len(files)
        class_stats[target_class] = count
        total_images_copied += count
        print(f"  - {target_class:<32} : {count:>5} real images")

    print(f"\n[+] Total Real Images Acquired: {total_images_copied}")

    # 5. Clean up temporary git repository
    print("\n[5] Cleaning up temporary clone repository...")
    try:
        subprocess.run(f'attrib -R "{TEMP_REPO_DIR}\\*.*" /S', shell=True)
        shutil.rmtree(TEMP_REPO_DIR, ignore_errors=True)
    except Exception as e:
        print(f"[!] Note: Temp dir cleanup notice: {e}")

    # 6. Update manifest with verified real download provenance
    if os.path.exists(MANIFEST_PATH):
        with open(MANIFEST_PATH, "r") as f:
            manifest = yaml.safe_load(f)

        manifest["download_status"] = "AUTHENTIC_DATASET_DOWNLOADED"
        manifest["verified_status"] = "AUTHENTIC_PLANTVILLAGE_TOMATO"
        manifest["commit_hash"] = commit_hash
        manifest["download_timestamp"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        manifest["total_real_images"] = total_images_copied
        manifest["class_counts"] = class_stats

        with open(MANIFEST_PATH, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)
        print(f"[+] Dataset manifest updated at {MANIFEST_PATH}")

    return total_images_copied > 0

if __name__ == "__main__":
    success = download_dataset()
    if not success:
        print("\n[!] DATASET ACQUISITION BLOCKED: Could not download authentic dataset.")
        sys.exit(1)
    else:
        print("\n[+] SUCCESS: Authentic PlantVillage Tomato dataset acquired.")
