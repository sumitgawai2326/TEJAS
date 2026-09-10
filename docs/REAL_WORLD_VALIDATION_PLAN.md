# KrishiDrishti Edge — Real-World & In-The-Wild Field Validation Plan (Phase K)

## 1. Domain Challenge: Laboratory vs Real-World Field Gap
Baseline academic datasets such as PlantVillage were captured under controlled conditions (plucked single leaflets placed on uniform gray or black sheets under constant diffused artificial lighting).

In contrast, an in-the-wild agricultural deployment encounters:
1. **Dynamic Solar Illumination**: Direct intense sunlight, deep canopy shadows, sunrise/sunset golden hour color temperatures.
2. **Complex Natural Backgrounds**: Multi-leaf foliage overlaps, soil, weed vegetation, plastic mulching, drip irrigation lines, human hands holding leaves.
3. **Motion Blur & Wind**: Camera shake during handheld smartphone or edge camera capture in outdoor breezes.
4. **Co-Infections & Non-Pathological Stress**: Combined nutritional deficiency symptoms (e.g. Nitrogen yellowing alongside Early Blight lesions), insect chew holes, dust accumulation.

---

## 2. Field-Validation Dataset Architecture
A dedicated, secondary evaluation split (**"KrishiDrishti-Wild-Tomato-v1"**) is specified to bridge this gap:

### Required Field Capture Inclusions
- **Image Acquisition Protocol**:
  - Distance: $15\text{ cm} - 30\text{ cm}$ from focal leaf.
  - Device diversity: Low-cost USB webcams, Raspberry Pi Camera Module 3 (Sony IMX708 autofocus), standard farmer Android smartphones ($8\text{MP} - 50\text{MP}$).
- **Lighting Strata**:
  - Full direct midday sun ($> 50,000\text{ lux}$)
  - Partial cloud cover & overcast conditions
  - Morning / evening low-angle sun
  - Greenhouse diffused lighting
- **Pathology & Stage Representation**:
  - Early-stage micro-lesions ( $< 2\text{ mm}$ spots)
  - Severe defoliation & sporulation stages
  - Healthy crop leaves at vegetative, flowering, and fruiting growth stages
  - Partially occluded and overlapping leaves

---

## 3. Official Truthful Status
```
================================================================================
REAL-WORLD FIELD VALIDATION STATUS: FIELD VALIDATION PENDING
================================================================================
```
No research-grade field generalization accuracy is claimed until physical data collection and testing across the above strata are completed and recorded.
