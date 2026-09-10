# Agricultural Dataset Integration & Licensing Guide — KrishiDrishti Edge

> **Zero AI Hallucination & Dataset Integrity Directive**

---

## 1. Dataset Verification & Ingestion Criteria

Before any agricultural dataset is imported into `data/datasets/`, it must undergo a rigorous 4-point verification check:

1. **Source & Lineage Verification**:
   - The dataset must originate from a verified agricultural research institute, university, or peer-reviewed agronomic publication.
   - Public datasets on aggregation portals (e.g. Kaggle, GitHub repositories) are **NOT automatically approved** without primary source lineage verification.
2. **Permissive Licensing**:
   - The license terms (e.g., Creative Commons `CC-BY`, `CC0`, `MIT`, `Apache-2.0`) must be inspected and documented in the dataset manifest.
   - Datasets with non-commercial restrictions (`CC-BY-NC`) or unclear copyright claims must not be bundled without explicit authorization.
3. **Class Label & Taxonomy Integrity**:
   - Disease classes must align with standard phytopathological nomenclature (e.g. *Alternaria solani* for Early Blight, *Phytophthora infestans* for Late Blight).
   - "Healthy" control samples for every target crop must be included to avoid false positive bias.
4. **Field Environment Generalizability**:
   - Datasets collected in laboratory environments with detached leaves on plain paper backgrounds have severe domain shift when deployed in natural field conditions (varying sunlight, complex background soil/weeds, leaf shadows).
   - Preference is given to in-situ outdoor field capture datasets.

---

## 2. Directory Structure

```
data/
├── datasets/
│   ├── manifest_template.yaml   # Standard declarative manifest template
│   └── <dataset_name>/          # Ingested dataset folder
│       ├── manifest.yaml        # Populated manifest
│       ├── train/               # Training class folders
│       ├── val/                 # Validation class folders
│       └── test/                # Test split for offline evaluation
├── models/                      # Stored neural network weight files (.onnx / .hef)
└── evaluation/                  # Generated evaluation reports and confusion matrices
```
