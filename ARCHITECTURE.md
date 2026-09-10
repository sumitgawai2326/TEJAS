# KrishiDrishti Edge - Architecture & Database Specification

## 1. Zero-Hallucination Architectural Principles

1. **Deterministic Hardware Reality**: The system strictly refuses to manufacture fake values for Nitrogen, Phosphorus, Potassium, pH, Moisture, or Temperature in production mode (`DEMO_MODE=false`). If hardware is disconnected or unconfigured, all telemetry fields remain `NULL` in the database.
2. **Unconfigured Register Map Policy**: Until the specific 6-parameter sensor model is purchased and its datasheet verified, `hardware/sensor_protocol/soil_sensor.yaml` maintains `null` addresses and `is_configured: false`.
3. **Runtime AI Accelerator Detection**: The AI subsystem dynamically detects physical Hailo-8 PCIe hardware (`/dev/hailo0` or HailoRT) and selects `HAILO ACCELERATED` or `CPU FALLBACK`.
4. **Isolated Demo Simulation Mode**: `DEMO_MODE=true` isolates mock drivers (`MockSoilSensor`, `MockCamera`, `DemoVisionModel`) and marks all generated records with `is_mock: true`.

---

## 2. Relational Database Schema (SQLite)

```
+--------------------+        +--------------------+        +--------------------+
|       farms        |        |       fields       |        |       crops        |
|--------------------|        |--------------------|        |--------------------|
| id (PK)            |<-------| id (PK)            |<-------| id (PK)            |
| name               |   1:N  | farm_id (FK)       |   1:N  | field_id (FK)      |
| location_name      |        | name               |        | crop_name          |
| created_at         |        | area, area_unit    |        | variety            |
| updated_at         |        | soil_type          |        | sowing_date        |
+--------------------+        +---------+----------+        | growth_stage       |
                                        |                   +--------------------+
         +------------------------------+------------------------------+
         |                              |                              |
         v 1:N                          v 1:N                          v 1:N
+--------------------+        +--------------------+        +--------------------+
|       scans        |        |   soil_readings    |        | risk_assessments   |
|--------------------|        |--------------------|        |--------------------|
| id (PK)            |        | id (PK)            |        | id (PK)            |
| field_id (FK)      |        | field_id (FK)      |        | field_id (FK)      |
| timestamp          |        | timestamp          |        | scan_id (FK)       |
| image_path         |        | nitrogen (NULLABLE)|        | soil_reading_id(FK)|
| image_quality      |        | phosphorus(NULLABLE|        | field_health_score |
| prediction         |        | potassium (NULLABLE|        | disease_risk       |
| confidence         |        | ph (NULLABLE)      |        | pest_risk          |
| model_name         |        | moisture (NULLABLE)|        | soil_stress        |
| model_version      |        | temp (NULLABLE)    |        | water_stress       |
| inference_device   |        | sensor_status      |        +---------+----------+
| status             |        | is_mock (BOOL)     |                  |
+--------------------+        +--------------------+                  v 1:N
                                                            +--------------------+
                                                            |     advisories     |
+--------------------+                                      |--------------------|
|   device_events    |                                      | id (PK)            |
|--------------------|                                      | field_id (FK)      |
| id (PK)            |                                      | risk_assessment_id |
| timestamp          |                                      | language           |
| subsystem          |                                      | title, message     |
| event_type         |                                      | severity, category |
| severity, message  |                                      +--------------------+
+--------------------+
```

---

## 3. Implemented API Endpoints (Phase 0 - 3)

### System & Diagnostics
- `GET /api/health`
- `GET /api/device/status`
- `GET /api/device/capabilities`
- `GET /api/camera/status`
- `GET /api/soil/status`
- `GET /api/ai/status`

### Fields & Historical Intelligence
- `GET /api/fields`
- `POST /api/fields`
- `GET /api/fields/{field_id}`
- `GET /api/fields/{field_id}/history` (Aggregated chronological timeline)
- `GET /api/fields/{field_id}/soil`
- `GET /api/fields/{field_id}/scans`
- `POST /api/fields/{field_id}/soil`
- `POST /api/fields/{field_id}/scans`
