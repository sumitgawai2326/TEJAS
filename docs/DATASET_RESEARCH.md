# KrishiDrishti Edge — Agricultural Dataset Research & Licensing Audit (Phase C)

## 1. Overview & Research Methodology
To train and validate an edge classification model for Tomato disease identification, candidate datasets were evaluated against strict criteria:
- Verified academic/institutional provenance
- Permissive licensing for research & edge distribution
- Tomato pathology coverage
- Real-world vs controlled laboratory image characteristics

---

## 2. Dataset Comparative Audit

### Dataset 1: PlantVillage (Hughes & Salathé, 2015)
- **Source URL**: `https://github.com/spMohanty/PlantVillage-Dataset` / `https://zenodo.org/record/1483986`
- **Institution**: Penn State University & EPFL
- **Citation**: Hughes, D., & Salathé, M. (2015). *An open access repository of images on plant health to enable the development of mobile disease diagnostics*. arXiv preprint arXiv:1511.08060.
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0) / Public Domain Dedication (CC0)
- **Tomato Coverage**:
  - `Tomato___Bacterial_spot` (2,127 images)
  - `Tomato___Early_blight` (1,000 images)
  - `Tomato___Late_blight` (1,909 images)
  - `Tomato___Leaf_Mold` (952 images)
  - `Tomato___Septoria_leaf_spot` (1,771 images)
  - `Tomato___Spider_mites Two-spotted_spider_mite` (1,676 images)
  - `Tomato___Target_Spot` (1,404 images)
  - `Tomato___Tomato_Yellow_Leaf_Curl_Virus` (5,357 images)
  - `Tomato___Tomato_mosaic_virus` (373 images)
  - `Tomato___healthy` (1,591 images)
  - **Total Tomato Samples**: ~18,160 images
- **Strengths**: Clean ground-truth pathological validation, large sample volume, clear taxonomic definitions.
- **Known Limitations**: Images were captured in laboratory conditions with plucked leaves on uniform gray/black paper backgrounds. High potential for laboratory background bias if deployed in unconstrained field environments without data augmentation or wild validation.
- **Suitability**: **High for baseline representation learning and initial edge ONNX model export.**

---

### Dataset 2: PlantDoc (Singh et al., 2019)
- **Source URL**: `https://github.com/pratikkayal/PlantDoc-Dataset`
- **Institution**: IIT Gandhinagar & TCS Research
- **Citation**: Singh, D., Jain, N., Jain, P., Kayal, P., Kumawat, S., & Batra, N. (2020). *PlantDoc: a dataset for visual plant disease detection in the wild*. In Proceedings of the 7th ACM IKDD CoDS and 25th COMAD (pp. 249-253).
- **License**: Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Tomato Coverage**: In-the-wild field photographs of Tomato Early Blight, Late Blight, Leaf Mold, Septoria, Two-spotted Spider Mite, Yellow Leaf Curl, and Healthy leaves.
- **Total Samples**: ~2,569 total images across 13 plant species (sub-sample for Tomato).
- **Strengths**: Authentic field conditions, complex canopy backgrounds, variable ambient sunlight.
- **Known Limitations**: Significantly lower image count per class, multi-leaf clutter, web-scraped noise requiring rigorous duplicate and quality filtering.
- **Suitability**: **High for field validation planning and robustness testing.**

---

## 3. Dataset Selection for Initial Model Pipeline
- **Selected Primary Training Source**: Verified **PlantVillage Tomato Subset (CC BY 4.0)** for foundational feature representation.
- **Field Robustness Plan**: **PlantDoc In-The-Wild Protocol** adopted for real-world field validation roadmap.
- **Repository Policy**: Raw full dataset binaries are excluded from Git repository tracking (`.gitignore`); only deterministic preparation scripts and metadata manifests are versioned.
