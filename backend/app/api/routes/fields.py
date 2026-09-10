"""
Phase 3 & Phase 5 Field, Soil History, Scans, Intelligence Fusion, and Advisory Endpoints.
"""
from typing import List, Optional, Dict, Any
import datetime
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories import (
    FarmRepository,
    FieldRepository,
    ScanRepository,
    SoilReadingRepository,
    FieldHistoryRepository,
    DeviceEventRepository,
    CropRepository,
    RiskAssessmentRepository,
    AdvisoryRepository
)
from app.schemas.fields import (
    FieldCreate,
    FieldResponse,
    ScanCreate,
    ScanResponse,
    SoilReadingCreate,
    SoilReadingResponse,
    FieldHistoryResponse,
    RiskAssessmentResponse,
    AdvisoryResponse,
    FieldAnalysisResponse
)
from app.hardware.soil_sensor import get_soil_sensor
from app.services.crop_detection.vision_service import vision_service
from app.services.fusion import (
    fusion_engine,
    FusionInput,
    VisionSignal,
    SoilSignal,
    CropContext,
    HistorySummary
)
from app.services.fusion.trends import TemporalTrendEngine
from app.services.advisory import advisory_engine
from app.core.config import settings
from app.core.logging import log_event

router = APIRouter(prefix="/fields", tags=["Fields & Historical Records"])


@router.get("", response_model=List[FieldResponse])
async def list_fields(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    """List all registered agricultural fields/plots."""
    field_repo = FieldRepository(db)
    return field_repo.list_all(skip=skip, limit=limit)

@router.post("", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
async def create_field(payload: FieldCreate, db: Session = Depends(get_db)):
    """Create a new field or plot attached to active farm."""
    farm_repo = FarmRepository(db)
    farm_id = payload.farm_id
    if not farm_id:
        farm = farm_repo.get_first_or_create(default_name="Primary Farm Plot", location_name="Local Edge Farm")
        farm_id = farm.id
    else:
        farm = farm_repo.get_by_id(farm_id)
        if not farm:
            raise HTTPException(status_code=404, detail=f"Farm with ID {farm_id} not found")

    field_repo = FieldRepository(db)
    field = field_repo.create(
        farm_id=farm_id,
        name=payload.name,
        area=payload.area,
        area_unit=payload.area_unit,
        soil_type=payload.soil_type
    )
    log_event("DATABASE", "INFO", f"Created Field '{field.name}' (ID: {field.id})")
    return field

@router.get("/{field_id}", response_model=FieldResponse)
async def get_field(field_id: int, db: Session = Depends(get_db)):
    """Retrieve field details by ID."""
    field_repo = FieldRepository(db)
    field = field_repo.get_by_id(field_id)
    if not field:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    return field

@router.get("/{field_id}/history", response_model=FieldHistoryResponse)
async def get_field_history(field_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """
    Retrieve chronological field history timeline combining scans,
    soil telemetry, risk assessments, and advisories.
    """
    history_repo = FieldHistoryRepository(db)
    timeline_data = history_repo.get_field_timeline(field_id=field_id, limit=limit)
    if "error" in timeline_data:
        raise HTTPException(status_code=404, detail=timeline_data["error"])
    return timeline_data

@router.get("/{field_id}/soil", response_model=List[SoilReadingResponse])
async def list_field_soil_readings(field_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """List historical 6-parameter soil readings for a field."""
    field_repo = FieldRepository(db)
    if not field_repo.get_by_id(field_id):
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    soil_repo = SoilReadingRepository(db)
    return soil_repo.list_by_field(field_id=field_id, limit=limit)

@router.get("/{field_id}/scans", response_model=List[ScanResponse])
async def list_field_scans(field_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """List historical crop leaf vision scans for a field."""
    field_repo = FieldRepository(db)
    if not field_repo.get_by_id(field_id):
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    scan_repo = ScanRepository(db)
    return scan_repo.list_by_field(field_id=field_id, limit=limit)

@router.post("/{field_id}/soil", response_model=SoilReadingResponse, status_code=status.HTTP_201_CREATED)
async def record_soil_reading(field_id: int, payload: Optional[SoilReadingCreate] = None, db: Session = Depends(get_db)):
    """
    Record a new soil reading.
    Zero Hardware Hallucination:
    - If DEMO_MODE=true: reads from MockSoilSensor (is_mock=True).
    - If DEMO_MODE=false: reads from ModbusSoilSensor. If disconnected, measurements remain NULL and a DeviceEvent is recorded.
    """
    field_repo = FieldRepository(db)
    field = field_repo.get_by_id(field_id)
    if not field:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")

    soil_repo = SoilReadingRepository(db)
    event_repo = DeviceEventRepository(db)

    # If payload is provided with explicit values
    if payload and (payload.nitrogen is not None or payload.moisture is not None or payload.sensor_status is not None):
        reading = soil_repo.create(
            field_id=field_id,
            sensor_status=payload.sensor_status or ("DEMO_SIMULATION" if settings.DEMO_MODE else "CONNECTED"),
            nitrogen=payload.nitrogen,
            phosphorus=payload.phosphorus,
            potassium=payload.potassium,
            ph=payload.ph,
            moisture=payload.moisture,
            temperature=payload.temperature,
            is_mock=payload.is_mock if payload.is_mock is not None else settings.DEMO_MODE
        )
        return reading

    # Live hardware probe query
    sensor = get_soil_sensor()
    telemetry = sensor.read()

    if not telemetry.connected and not settings.DEMO_MODE:
        # Record hardware disconnect event
        event_repo.create(
            subsystem="SOIL",
            event_type="SENSOR_DISCONNECTED",
            message=telemetry.error_message or "RS485 Soil sensor disconnected",
            severity="WARNING",
            details=f"Field {field_id} requested reading while sensor was unconfigured or disconnected."
        )

    reading = soil_repo.create(
        field_id=field_id,
        sensor_status=telemetry.status,
        nitrogen=telemetry.nitrogen,
        phosphorus=telemetry.phosphorus,
        potassium=telemetry.potassium,
        ph=telemetry.ph,
        moisture=telemetry.moisture,
        temperature=telemetry.temperature,
        is_mock=telemetry.is_mock,
        raw_payload_reference=telemetry.raw_response_hex
    )
    log_event("DATABASE", "INFO", f"Saved SoilReading ID {reading.id} for Field {field_id} (Status: {reading.sensor_status}, is_mock={reading.is_mock})")
    return reading

@router.post("/{field_id}/scans", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def record_scan(field_id: int, payload: ScanCreate, db: Session = Depends(get_db)):
    """Record a crop vision AI scan result into field history."""
    field_repo = FieldRepository(db)
    field = field_repo.get_by_id(field_id)
    if not field:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")

    scan_repo = ScanRepository(db)
    scan = scan_repo.create(
        field_id=field_id,
        prediction=payload.prediction,
        confidence=payload.confidence,
        model_name=payload.model_name,
        model_version=payload.model_version,
        image_path=payload.image_path,
        image_quality=payload.image_quality,
        inference_device=payload.inference_device,
        status=payload.status
    )
    log_event("DATABASE", "INFO", f"Saved Scan ID {scan.id} for Field {field_id} (Prediction: {scan.prediction}, Confidence: {scan.confidence:.2f})")
    return scan

@router.post("/{field_id}/analyze", response_model=FieldAnalysisResponse, summary="Execute multi-modal intelligence fusion")
async def analyze_field(
    field_id: int,
    file: Optional[UploadFile] = File(None),
    use_camera: bool = Form(False),
    trigger_soil_read: bool = Form(True),
    scan_id: Optional[int] = Form(None),
    soil_reading_id: Optional[int] = Form(None),
    confidence_override: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    """
    End-to-end multi-modal fusion intelligence execution:
    1. Loads field and registered crop context.
    2. Ingests or loads crop vision signal.
    3. Reads live or loads recent 6-param RS485 soil telemetry.
    4. Gathers historical observations and evaluates temporal trends.
    5. Fuses multi-modal evidence and evaluates transparent agronomic rules.
    6. Calculates explainable risk assessment and generates prioritized farmer advisories.
    7. Persists RiskAssessment and Advisory records into SQLite.
    """
    field_repo = FieldRepository(db)
    field = field_repo.get_by_id(field_id)
    if not field:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")

    crop_repo = CropRepository(db)
    crops = crop_repo.list_by_field(field_id)
    if crops:
        active_crop = crops[0]
        crop_context = CropContext(
            crop_name=active_crop.crop_name,
            variety=active_crop.variety,
            growth_stage=active_crop.growth_stage,
            sowing_date=active_crop.sowing_date
        )
    else:
        crop_context = CropContext(crop_name=field.soil_type or "General")

    # 1. Obtain Vision Signal
    vision_signal = VisionSignal(status="unavailable")
    scan_repo = ScanRepository(db)
    if file and file.filename:
        img_bytes = await file.read()
        res = vision_service.process_image(
            image_bytes=img_bytes,
            field_id=field_id,
            db=db,
            use_camera=False,
            raw_confidence_override=confidence_override
        )
        vision_signal = VisionSignal(
            status=res.status,
            prediction=res.prediction,
            confidence=res.confidence,
            model_name=res.model_name,
            model_version=res.model_version,
            image_quality=res.image_quality.score,
            is_demo=res.is_demo,
            scan_id=res.scan_id
        )
    elif use_camera:
        res = vision_service.process_image(
            field_id=field_id,
            db=db,
            use_camera=True,
            raw_confidence_override=confidence_override
        )
        vision_signal = VisionSignal(
            status=res.status,
            prediction=res.prediction,
            confidence=res.confidence,
            model_name=res.model_name,
            model_version=res.model_version,
            image_quality=res.image_quality.score,
            is_demo=res.is_demo,
            scan_id=res.scan_id
        )
    elif scan_id:
        existing_scan = scan_repo.get_by_id(scan_id)
        if existing_scan:
            vision_signal = VisionSignal(
                status="accepted" if existing_scan.status == "CONFIDENT" else "low_confidence",
                prediction=existing_scan.prediction,
                confidence=existing_scan.confidence,
                model_name=existing_scan.model_name,
                model_version=existing_scan.model_version,
                image_quality=existing_scan.image_quality,
                is_demo=settings.DEMO_MODE,
                scan_id=existing_scan.id
            )
    else:
        recent_scans = scan_repo.list_by_field(field_id, limit=1)
        if recent_scans:
            latest_s = recent_scans[0]
            vision_signal = VisionSignal(
                status="accepted" if latest_s.status == "CONFIDENT" else "low_confidence",
                prediction=latest_s.prediction,
                confidence=latest_s.confidence,
                model_name=latest_s.model_name,
                model_version=latest_s.model_version,
                image_quality=latest_s.image_quality,
                is_demo=settings.DEMO_MODE,
                scan_id=latest_s.id
            )

    # 2. Obtain Soil Signal
    soil_repo = SoilReadingRepository(db)
    soil_signal = SoilSignal(status="DISCONNECTED", availability="UNAVAILABLE")
    active_soil_id = None

    if trigger_soil_read:
        # Trigger live probe read
        sensor = get_soil_sensor()
        telemetry = sensor.read()
        reading = soil_repo.create(
            field_id=field_id,
            sensor_status=telemetry.status,
            nitrogen=telemetry.nitrogen,
            phosphorus=telemetry.phosphorus,
            potassium=telemetry.potassium,
            ph=telemetry.ph,
            moisture=telemetry.moisture,
            temperature=telemetry.temperature,
            is_mock=telemetry.is_mock,
            raw_payload_reference=telemetry.raw_response_hex
        )
        active_soil_id = reading.id
        soil_signal = SoilSignal(
            nitrogen=reading.nitrogen,
            phosphorus=reading.phosphorus,
            potassium=reading.potassium,
            ph=reading.ph,
            moisture=reading.moisture,
            temperature=reading.temperature,
            timestamp=reading.timestamp,
            sensor_status=reading.sensor_status,
            is_mock=reading.is_mock,
            availability="COMPLETE" if (reading.nitrogen is not None and reading.moisture is not None) else ("PARTIAL" if reading.moisture is not None else "UNAVAILABLE")
        )
    elif soil_reading_id:
        existing_reading = soil_repo.get_by_id(soil_reading_id)
        if existing_reading:
            active_soil_id = existing_reading.id
            soil_signal = SoilSignal(
                nitrogen=existing_reading.nitrogen,
                phosphorus=existing_reading.phosphorus,
                potassium=existing_reading.potassium,
                ph=existing_reading.ph,
                moisture=existing_reading.moisture,
                temperature=existing_reading.temperature,
                timestamp=existing_reading.timestamp,
                sensor_status=existing_reading.sensor_status,
                is_mock=existing_reading.is_mock,
                availability="COMPLETE" if (existing_reading.nitrogen is not None and existing_reading.moisture is not None) else "PARTIAL"
            )
    else:
        recent_soil = soil_repo.list_by_field(field_id, limit=1)
        if recent_soil:
            latest_sr = recent_soil[0]
            active_soil_id = latest_sr.id
            soil_signal = SoilSignal(
                nitrogen=latest_sr.nitrogen,
                phosphorus=latest_sr.phosphorus,
                potassium=latest_sr.potassium,
                ph=latest_sr.ph,
                moisture=latest_sr.moisture,
                temperature=latest_sr.temperature,
                timestamp=latest_sr.timestamp,
                sensor_status=latest_sr.sensor_status,
                is_mock=latest_sr.is_mock,
                availability="COMPLETE" if (latest_sr.nitrogen is not None and latest_sr.moisture is not None) else "PARTIAL"
            )

    # 3. Gather History & Temporal Trends
    hist_scans = scan_repo.list_by_field(field_id, limit=10)
    hist_soil = soil_repo.list_by_field(field_id, limit=10)
    history_summary = TemporalTrendEngine.analyze_history(
        recent_scans=hist_scans,
        recent_soil=hist_soil,
        current_vision=vision_signal,
        current_soil=soil_signal,
        is_demo=settings.DEMO_MODE
    )

    # 4. Execute Multi-Modal Fusion Engine
    fusion_input = FusionInput(
        field_id=field_id,
        crop_context=crop_context,
        vision=vision_signal,
        soil=soil_signal,
        history=history_summary
    )
    fusion_result = fusion_engine.fuse(fusion_input)

    # 5. Execute Actionable Advisory Engine
    advisory_result = advisory_engine.generate(
        field_id=field_id,
        risk=fusion_result.risk,
        evidence=fusion_result.evidence,
        data_quality=fusion_result.data_quality,
        vision=vision_signal,
        is_demo=fusion_result.is_demo
    )

    # 6. Persist RiskAssessment into SQLite
    risk_repo = RiskAssessmentRepository(db)
    saved_risk = risk_repo.create(
        field_id=field_id,
        field_health_score=round(1.0 - fusion_result.risk.score, 2) if fusion_result.risk.score is not None else None,
        disease_risk=fusion_result.risk.disease_risk,
        pest_risk=fusion_result.risk.pest_risk,
        soil_stress=fusion_result.risk.soil_stress,
        water_stress=fusion_result.risk.water_stress,
        scan_id=vision_signal.scan_id,
        soil_reading_id=active_soil_id,
        status=fusion_result.risk.risk_level
    )

    # 7. Persist Advisories into SQLite
    adv_repo = AdvisoryRepository(db)
    for adv in advisory_result.advisories:
        adv_repo.create(
            field_id=field_id,
            title=adv.title,
            message=adv.message,
            language="en",
            severity=adv.priority,
            category=adv.category,
            risk_assessment_id=saved_risk.id
        )

    log_event("DATABASE", "INFO", f"Saved RiskAssessment #{saved_risk.id} and {len(advisory_result.advisories)} Advisories for Field {field_id}")

    return FieldAnalysisResponse(
        field=FieldResponse.model_validate(field),
        vision=vision_signal.model_dump(),
        soil=soil_signal.model_dump(),
        history=history_summary.model_dump(),
        risk=fusion_result.risk.model_dump(),
        evidence=[e.model_dump() for e in fusion_result.evidence],
        advisories=[a.model_dump() for a in advisory_result.advisories],
        data_quality=fusion_result.data_quality.model_dump(),
        is_demo=fusion_result.is_demo,
        generated_at=datetime.datetime.now(datetime.timezone.utc).isoformat()
    )


@router.get("/{field_id}/risk/latest", response_model=RiskAssessmentResponse, summary="Get latest risk assessment for field")
async def get_latest_risk(field_id: int, db: Session = Depends(get_db)):
    """Retrieve most recent risk assessment record for a field."""
    field_repo = FieldRepository(db)
    if not field_repo.get_by_id(field_id):
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    risk_repo = RiskAssessmentRepository(db)
    latest = risk_repo.get_latest_by_field(field_id)
    if not latest:
        raise HTTPException(status_code=404, detail=f"No risk assessment found for field {field_id}")
    return latest

@router.get("/{field_id}/risk/history", response_model=List[RiskAssessmentResponse], summary="Get chronological risk history")
async def get_risk_history(field_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve chronological risk assessment records for a field."""
    field_repo = FieldRepository(db)
    if not field_repo.get_by_id(field_id):
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    risk_repo = RiskAssessmentRepository(db)
    return risk_repo.list_by_field(field_id, limit=limit)

@router.get("/{field_id}/advisories", response_model=List[AdvisoryResponse], summary="Get field advisories")
async def list_field_advisories(field_id: int, language: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db)):
    """Retrieve historical agronomic advisories for a field."""
    field_repo = FieldRepository(db)
    if not field_repo.get_by_id(field_id):
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    adv_repo = AdvisoryRepository(db)
    return adv_repo.list_by_field(field_id, language=language, limit=limit)

