# KrishiDrishti Edge — Data Splitting & Leakage Prevention Policy (Phase F)

## 1. Principles of Data Partitioning
To prevent data contamination and ensure scientifically sound evaluation:
1. **Deterministic Random Partitioning**: A fixed pseudorandom seed (`RANDOM_SEED=42`) is enforced across all splitting scripts (`ml/scripts/create_split.py`).
2. **Fixed 70 / 15 / 15 Partition Ratio**:
   - **Training (70%)**: Parameter learning via backpropagation.
   - **Validation (15%)**: Model checkpoint selection, learning rate decay, and early stopping.
   - **Held-Out Test (15%)**: Final benchmark evaluation ONLY. Never seen during training or tuning.
3. **Data Deduplication**: Duplicate hash verification (`ml/scripts/check_duplicates.py`) is conducted prior to splitting to prevent identical images from appearing across both training and test partitions.
4. **Isolated Test Set Storage**: Test images are stored in `ml/data/processed/tomato_cls/test/` and are inaccessible to the training loop.
