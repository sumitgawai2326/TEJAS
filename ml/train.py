"""
TEJAS — AI Model Training Pipeline
Trains a lightweight YOLO classification model on the processed PlantVillage Tomato dataset.
Saves checkpoints, best PyTorch weights, training metadata, and class mappings.
"""
import os
import sys
import yaml
import json
import time
import argparse
from pathlib import Path

def train_tomato_classifier(
    config_path: str = os.path.join("ml", "configs", "tomato_yolo_cls.yaml"),
    epochs_override: int = None,
    run_name_override: str = None
):
    print("=" * 70)
    print("TEJAS — Tomato Disease Model Training Pipeline")
    print(f"Config: {config_path}")
    print("=" * 70)

    if not os.path.exists(config_path):
        print(f"[!] Config file not found: {config_path}")
        return None

    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)

    data_dir = cfg.get("data", "ml/data/processed/tomato_cls")
    if not os.path.exists(data_dir) or not os.path.exists(os.path.join(data_dir, "train")):
        print(f"[!] Processed dataset not found at {data_dir}. Run data preparation and split scripts first.")
        return None

    # Detect Ultralytics
    try:
        from ultralytics import YOLO
    except ImportError:
        print("[!] Ultralytics is not installed in the active environment.")
        return None

    model_name = cfg.get("model", "yolo11n-cls.pt")
    print(f"\n[+] Initializing YOLO Model: {model_name}")
    try:
        model = YOLO(model_name)
    except Exception as e:
        print(f"[!] Could not load {model_name}: {e}. Attempting fallback to yolov8n-cls.pt...")
        model = YOLO("yolov8n-cls.pt")

    epochs = epochs_override if epochs_override is not None else cfg.get("epochs", 30)
    run_name = run_name_override if run_name_override is not None else cfg.get("name", "tejas_tomato_yolo11n_cls")
    project_dir = cfg.get("project", "ml/runs/train")

    print(f"\n[+] Starting Training Run: {run_name} ({epochs} epochs)...")
    t_start = time.time()
    t_start_iso = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    results = model.train(
        data=data_dir,
        epochs=epochs,
        imgsz=cfg.get("imgsz", 224),
        batch=cfg.get("batch", 16),
        workers=cfg.get("workers", 2),
        optimizer=cfg.get("optimizer", "AdamW"),
        lr0=cfg.get("lr0", 0.001),
        lrf=cfg.get("lrf", 0.01),
        weight_decay=cfg.get("weight_decay", 0.0005),
        patience=cfg.get("patience", 10),
        seed=cfg.get("seed", 42),
        deterministic=True,
        project=project_dir,
        name=run_name,
        exist_ok=True,
        device=cfg.get("device", "cpu")
    )
    t_elapsed = round(time.time() - t_start, 2)
    t_end_iso = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    print(f"\n[+] Training completed in {t_elapsed} seconds ({t_elapsed/60:.2f} mins).")

    # Save training summary metadata
    save_dir = str(results.save_dir) if hasattr(results, "save_dir") else os.path.join(project_dir, run_name)
    best_weights = os.path.join(save_dir, "weights", "best.pt")
    last_weights = os.path.join(save_dir, "weights", "last.pt")

    # If saved under runs/classify/, also mirror/copy key weights to ml/runs/train/run_name for convenience
    target_project_run = os.path.join("ml", "runs", "train", run_name)
    os.makedirs(os.path.join(target_project_run, "weights"), exist_ok=True)
    import shutil
    if os.path.exists(best_weights):
        shutil.copy2(best_weights, os.path.join(target_project_run, "weights", "best.pt"))
    if os.path.exists(last_weights):
        shutil.copy2(last_weights, os.path.join(target_project_run, "weights", "last.pt"))

    out_meta = {
        "project": "TEJAS",
        "task": "tomato_disease_classification",
        "model_architecture": model_name,
        "run_name": run_name,
        "dataset_path": data_dir,
        "save_dir": save_dir,
        "training_start_time": t_start_iso,
        "training_end_time": t_end_iso,
        "training_duration_seconds": t_elapsed,
        "epochs_requested": epochs,
        "imgsz": cfg.get("imgsz", 224),
        "batch_size": cfg.get("batch", 16),
        "optimizer": cfg.get("optimizer", "AdamW"),
        "best_weights_path": best_weights if os.path.exists(best_weights) else None,
        "last_weights_path": last_weights if os.path.exists(last_weights) else None,
        "best_fitness": float(results.fitness) if hasattr(results, "fitness") and results.fitness is not None else None
    }

    for target_dir in [save_dir, target_project_run]:
        os.makedirs(target_dir, exist_ok=True)
        meta_path = os.path.join(target_dir, "training_metadata.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(out_meta, f, indent=2)

    print(f"[+] Training metadata saved to: {os.path.join(target_project_run, 'training_metadata.json')}")
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TEJAS Tomato Disease YOLO Training")
    parser.add_argument("--config", type=str, default=os.path.join("ml", "configs", "tomato_yolo_cls.yaml"))
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--name", type=str, default=None)
    parser.add_argument("--smoke-test", action="store_true", help="Run a 1-epoch smoke test")
    args = parser.parse_args()

    epochs = 1 if args.smoke_test else args.epochs
    run_name = "tejas_smoke_run" if args.smoke_test else args.name
    train_tomato_classifier(config_path=args.config, epochs_override=epochs, run_name_override=run_name)
