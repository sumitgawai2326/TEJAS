# KrishiDrishti Edge — AI Model Training & Reproducibility Protocol

**Task**: Tomato Leaf Pathology Classification (10 Classes)  
**Model Architecture**: YOLOv8n-cls / YOLO11n-cls (Ultralytics Nano Backbone)  
**Target Precision**: Float32 (Exported to ONNX Opset 17 / FP16 Quantization Ready)  
**Config Path**: `ml/configs/tomato_yolo_cls.yaml`

---

## 1. Hyperparameter & Training Configuration

The training configuration is codified in `ml/configs/tomato_yolo_cls.yaml`:

```yaml
model:
  architecture: "yolo11n-cls.pt"  # Lightweight classification backbone (~1.5M params)
  pretrained: true
  num_classes: 10
  input_resolution: [224, 224]     # Dynamic resolution supported by ONNX export

training:
  epochs: 30
  batch_size: 16
  optimizer: "AdamW"
  lr0: 0.001
  lrf: 0.01
  weight_decay: 0.0005
  seed: 42
  workers: 4
  patience: 10
  save_period: 5

augmentation:
  hsv_h: 0.015    # Hue jitter
  hsv_s: 0.4      # Saturation jitter
  hsv_v: 0.4      # Brightness jitter
  degrees: 15.0   # Rotation range (+/- 15 deg)
  translate: 0.1  # Translation
  scale: 0.2      # Scale variation
  fliplr: 0.5     # Horizontal flip
  mosaic: 0.0     # Disabled for pure classification
```

---

## 2. Reproducibility & Partitioning Workflow

1. **Dataset Download & Verification**:
   - `python ml/scripts/download_dataset.py` creates the canonical class structure.
   - `python ml/scripts/check_duplicates.py` scans MD5 hashes to prevent identical image contamination across splits.
2. **Deterministic Partitioning**:
   - `python ml/scripts/create_split.py` splits images into `70% train`, `15% val`, and `15% test` partitions with a fixed pseudo-random seed (`seed=42`).
3. **Execution**:
   ```bash
   python ml/train.py --config ml/configs/tomato_yolo_cls.yaml
   ```
4. **Artifact Checkpointing**:
   - Best checkpoint saved to `ml/runs/tomato_cls/weights/best.pt`.
   - Training loss, validation loss, top-1 accuracy, and top-5 accuracy logged to `ml/runs/tomato_cls/results.csv`.

---

## 3. ONNX Conversion & Optimization

After training completes, the PyTorch weights are converted to ONNX:

```bash
python ml/export_onnx.py --weights ml/runs/tomato_cls/weights/best.pt --output data/models/crop_disease_v1.onnx
```

Validation and checksum:
```bash
python ml/validate_onnx.py --model data/models/crop_disease_v1.onnx
python ml/model_hash.py data/models/crop_disease_v1.onnx
```
