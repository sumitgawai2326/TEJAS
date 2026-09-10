import os

base_api = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app\api\routes"
base_app = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app"

# 1. api/routes/fields.py
fields_route_code = """\"\"\"
Phase 3 Field, Soil History, Scans, and Timeline API Endpoints.
\"\"\"
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.repositories import (
    FarmRepository,
    FieldRepository,
    ScanRepository,
    SoilReadingRepository,
    FieldHistoryRepository,
    DeviceEventRepository
)
from app.schemas.fields import (
    FieldCreate,
    FieldResponse,
    ScanCreate,
    ScanResponse,
    SoilReadingCreate,
    SoilReadingResponse,
    FieldHistoryResponse
)
from app.hardware.soil_sensor import get_soil_sensor
from app.core.config import settings
from app.core.logging import log_event

router = APIRouter(prefix="/fields", tags=["Fields & Historical Records"])

@router.get("", response_model=List[FieldResponse])
async def list_fields(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    \"\"\"List all registered agricultural fields/plots.\"\"\"
    field_repo = FieldRepository(db)
    return field_repo.list_all(skip=skip, limit=limit)

@router.post("", response_model=FieldResponse, status_code=status.HTTP_201_CREATED)
async def create_field(payload: FieldCreate, db: Session = Depends(get_db)):
    \"\"\"Create a new field or plot attached to active farm.\"\"\"
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
    \"\"\"Retrieve field details by ID.\"\"\"
    field_repo = FieldRepository(db)
    field = field_repo.get_by_id(field_id)
    if not field:
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    return field

@router.get("/{field_id}/history", response_model=FieldHistoryResponse)
async def get_field_history(field_id: int, limit: int = 50, db: Session = Depends(get_db)):
    \"\"\"
    Retrieve chronological field history timeline combining scans,
    soil telemetry, risk assessments, and advisories.
    \"\"\"
    history_repo = FieldHistoryRepository(db)
    timeline_data = history_repo.get_field_timeline(field_id=field_id, limit=limit)
    if "error" in timeline_data:
        raise HTTPException(status_code=404, detail=timeline_data["error"])
    return timeline_data

@router.get("/{field_id}/soil", response_model=List[SoilReadingResponse])
async def list_field_soil_readings(field_id: int, limit: int = 50, db: Session = Depends(get_db)):
    \"\"\"List historical 6-parameter soil readings for a field.\"\"\"
    field_repo = FieldRepository(db)
    if not field_repo.get_by_id(field_id):
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    soil_repo = SoilReadingRepository(db)
    return soil_repo.list_by_field(field_id=field_id, limit=limit)

@router.get("/{field_id}/scans", response_model=List[ScanResponse])
async def list_field_scans(field_id: int, limit: int = 50, db: Session = Depends(get_db)):
    \"\"\"List historical crop leaf vision scans for a field.\"\"\"
    field_repo = FieldRepository(db)
    if not field_repo.get_by_id(field_id):
        raise HTTPException(status_code=404, detail=f"Field {field_id} not found")
    scan_repo = ScanRepository(db)
    return scan_repo.list_by_field(field_id=field_id, limit=limit)

@router.post("/{field_id}/soil", response_model=SoilReadingResponse, status_code=status.HTTP_201_CREATED)
async def record_soil_reading(field_id: int, payload: Optional[SoilReadingCreate] = None, db: Session = Depends(get_db)):
    \"\"\"
    Record a new soil reading.
    Zero Hardware Hallucination:
    - If DEMO_MODE=true: reads from MockSoilSensor (is_mock=True).
    - If DEMO_MODE=false: reads from ModbusSoilSensor. If disconnected, measurements remain NULL and a DeviceEvent is recorded.
    \"\"\"
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
    \"\"\"Record a crop vision AI scan result into field history.\"\"\"
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
"""

with open(os.path.join(base_api, "fields.py"), "w", encoding="utf-8") as f:
    f.write(fields_route_code)

# 2. Update api/routes/__init__.py
routes_init = """\"\"\"
Central API Router for KrishiDrishti Edge.
\"\"\"
from fastapi import APIRouter
from app.api.routes.health import router as health_router
from app.api.routes.subsystems import router as subsystems_router
from app.api.routes.fields import router as fields_router

api_router = APIRouter(prefix="/api")
api_router.include_router(health_router)
api_router.include_router(subsystems_router)
api_router.include_router(fields_router)
"""

with open(os.path.join(base_api, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(routes_init)

# 3. Update main.py to call init_db() on startup
main_code = """\"\"\"
Main FastAPI Application Entry Point for KrishiDrishti Edge.
\"\"\"
from contextlib import asynccontextmanager
import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger, log_event
from app.core.errors import KrishiException, ErrorCode
from app.api.routes import api_router
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup Lifespan: Initialize offline SQLite database safely
    log_event("SYSTEM", "INFO", f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    log_event("SYSTEM", "INFO", f"Tagline: {settings.TAGLINE}")
    log_event("DEVICE", "INFO", f"Mode: {'DEMO SIMULATION' if settings.DEMO_MODE else 'REAL HARDWARE MODE'}")
    log_event("AI", "INFO", f"AI Mode: {settings.AI_MODE} (Confidence Threshold: {settings.AI_CONFIDENCE_THRESHOLD:.2f})")
    
    # Initialize SQLite Database & Tables
    init_db()
    
    yield
    # Shutdown Lifespan
    log_event("SYSTEM", "INFO", "Shutting down KrishiDrishti Edge gracefully...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Portable Offline AI-Powered Farming Assistant for Smart India Hackathon (SIH)",
    lifespan=lifespan
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# KrishiException Handler
@app.exception_handler(KrishiException)
async def krishi_exception_handler(request: Request, exc: KrishiException):
    log_event("API", "WARNING", f"KrishiException on {request.url.path}: [{exc.code}] {exc.message}")
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )

# Global API Exception Handler (Zero Stack Trace Leaks)
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_event("SYSTEM", "ERROR", f"Unhandled exception on {request.url.path}: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "code": ErrorCode.INTERNAL_ERROR.value,
            "message": "Internal server error occurred",
            "details": str(exc) if settings.DEBUG else "An unexpected error occurred. Consult system logs.",
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }
    )

# Include API Router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
"""

with open(os.path.join(base_app, "main.py"), "w", encoding="utf-8") as f:
    f.write(main_code)

print("Fields API routes and database lifespan integration completed.")
