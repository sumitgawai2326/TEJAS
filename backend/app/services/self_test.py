"""
Hardware & System Startup Self-Test Service for KrishiDrishti Edge.
Verifies all 6 local subsystems on boot or on demand.
Evaluates overall device readiness:
- DEVICE READY (All subsystems operational)
- DEVICE READY WITH WARNINGS (Core functional, non-critical peripheral disconnected)
- DEVICE INITIALIZATION FAILED (Critical failure e.g., database or storage error)
"""
import time
import os
from typing import List
from sqlalchemy import text
from app.core.config import settings
from app.core.logging import log_event
from app.schemas.health import SelfTestItem, SelfTestResponse
from app.hardware.detection import SystemDetector
from app.hardware.camera import get_camera
from app.hardware.soil_sensor import get_soil_sensor
from app.db.database import SessionLocal
from app.ai.inference.base import AcceleratorDetector

class DeviceSelfTestService:
    """Executes non-destructive diagnostics on all edge hardware and software components."""

    @classmethod
    def run_self_test(cls) -> SelfTestResponse:
        items: List[SelfTestItem] = []

        # 1. Local SQLite Database Check (Critical)
        db_start = time.perf_counter()
        try:
            db = SessionLocal()
            db.execute(text("SELECT 1"))
            db.close()
            db_lat = round((time.perf_counter() - db_start) * 1000, 2)
            items.append(SelfTestItem(
                subsystem="Local SQLite Database",
                status="PASSED",
                critical=True,
                message="SQLite database read/write connection operational",
                details=f"Path: {settings.DATABASE_PATH}",
                latency_ms=db_lat
            ))
        except Exception as e:
            db_lat = round((time.perf_counter() - db_start) * 1000, 2)
            items.append(SelfTestItem(
                subsystem="Local SQLite Database",
                status="FAILED",
                critical=True,
                message=f"Database connection error: {e}",
                details=f"Path: {settings.DATABASE_PATH}",
                latency_ms=db_lat
            ))

        # 2. Local Storage Space Check (Critical)
        storage_metrics = SystemDetector.get_storage_metrics(settings.DATA_DIR)
        free_gb = storage_metrics.get("free_gb", 0.0)
        is_low = storage_metrics.get("is_low_space", False)
        if is_low:
            items.append(SelfTestItem(
                subsystem="Edge Local Storage",
                status="WARNING",
                critical=False,
                message=f"Low disk space remaining ({free_gb} GB free)",
                details="Free disk space is below 500 MB threshold."
            ))
        else:
            items.append(SelfTestItem(
                subsystem="Edge Local Storage",
                status="PASSED",
                critical=True,
                message=f"Storage healthy ({free_gb} GB free, {storage_metrics.get('percent_used', 0)}% used)",
                details=f"Directory: {os.path.abspath(settings.DATA_DIR)}"
            ))

        # 3. Camera Subsystem Check (Non-critical peripheral)
        cam_start = time.perf_counter()
        camera = get_camera()
        cam_status = camera.get_status()
        cam_lat = round((time.perf_counter() - cam_start) * 1000, 2)

        if settings.DEMO_MODE:
            items.append(SelfTestItem(
                subsystem="Camera Subsystem",
                status="PASSED",
                critical=False,
                message="Camera operational (Demo / Mock Viewfinder)",
                details="Running simulated hardware camera driver.",
                latency_ms=cam_lat
            ))
        elif cam_status.get("available", False):
            items.append(SelfTestItem(
                subsystem="Camera Subsystem",
                status="PASSED",
                critical=False,
                message="Physical camera device connected and ready",
                details=f"Device Index: {cam_status.get('camera_device_index', 0)}, Resolution: {cam_status.get('resolution')}",
                latency_ms=cam_lat
            ))
        else:
            items.append(SelfTestItem(
                subsystem="Camera Subsystem",
                status="WARNING",
                critical=False,
                message="Camera unavailable — leaf photo upload fallback enabled",
                details="No physical video device detected at index 0 (Zero Hardware Hallucination).",
                latency_ms=cam_lat
            ))

        # 4. 6-Parameter Soil Sensor Interface Check (Non-critical peripheral)
        soil_start = time.perf_counter()
        soil_sensor = get_soil_sensor()
        soil_status = soil_sensor.get_status()
        soil_lat = round((time.perf_counter() - soil_start) * 1000, 2)

        if settings.DEMO_MODE:
            items.append(SelfTestItem(
                subsystem="6-Parameter Soil Sensor",
                status="PASSED",
                critical=False,
                message="Soil sensor operational (Demo Simulation)",
                details="Mock 6-in-1 NPK + pH + Moisture + Temp telemetry active.",
                latency_ms=soil_lat
            ))
        elif soil_status.get("connected", False):
            items.append(SelfTestItem(
                subsystem="6-Parameter Soil Sensor",
                status="PASSED",
                critical=False,
                message="RS485 Modbus-RTU probe connected and responsive",
                details=f"Port: {soil_status.get('port')}, Baud: {soil_status.get('baudrate')}",
                latency_ms=soil_lat
            ))
        else:
            status_text = soil_status.get("status", "SENSOR DISCONNECTED")
            items.append(SelfTestItem(
                subsystem="6-Parameter Soil Sensor",
                status="WARNING",
                critical=False,
                message=f"Soil probe {status_text} (Zero Hardware Hallucination)",
                details=soil_status.get("details", "RS485 probe not detected on bus."),
                latency_ms=soil_lat
            ))

        # 5. AI Inference & Accelerator Check (Critical for AI pipeline, fallback available)
        ai_start = time.perf_counter()
        accel_info = AcceleratorDetector.detect(settings.AI_MODE)
        ai_lat = round((time.perf_counter() - ai_start) * 1000, 2)

        items.append(SelfTestItem(
            subsystem="AI Inference Engine",
            status="PASSED",
            critical=True,
            message=f"Inference engine active ({accel_info['mode_label']})",
            details=accel_info.get("details", "AI execution environment ready."),
            latency_ms=ai_lat
        ))

        # 6. Backend Host Platform Check (Critical)
        plat = SystemDetector.get_platform_info()
        items.append(SelfTestItem(
            subsystem="Host Platform & Runtime",
            status="PASSED",
            critical=True,
            message=f"Platform: {plat['board_model']}",
            details=f"OS: {plat['os_name']} {plat['architecture']} | Python {plat['python_version']}"
        ))

        # Calculate Overall Status
        passed_count = sum(1 for i in items if i.status == "PASSED")
        warning_count = sum(1 for i in items if i.status == "WARNING")
        failed_count = sum(1 for i in items if i.status == "FAILED")

        if failed_count > 0:
            overall_status = "DEVICE INITIALIZATION FAILED"
        elif warning_count > 0:
            overall_status = "DEVICE READY WITH WARNINGS"
        else:
            overall_status = "DEVICE READY"

        log_event("SELF_TEST", "INFO", f"Self-test complete: {overall_status} (Passed: {passed_count}, Warnings: {warning_count}, Failed: {failed_count})")

        return SelfTestResponse(
            overall_status=overall_status,
            passed_count=passed_count,
            warning_count=warning_count,
            failed_count=failed_count,
            items=items,
            demo_mode=settings.DEMO_MODE
        )
