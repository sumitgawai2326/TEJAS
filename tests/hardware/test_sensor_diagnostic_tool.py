"""
Automated Unit Tests for Sensor Diagnostic CLI Tool & Battery Monitor Zero-Hallucination Policy.
"""
import pytest
from unittest.mock import patch
from app.tools.sensor_diagnostic import run_diagnostic
from app.hardware.battery.battery_monitor import BatteryMonitor

def test_sensor_diagnostic_unconfigured_safe_exit():
    """Verify CLI diagnostic exits cleanly with code 0 on unconfigured yaml template."""
    exit_code = run_diagnostic(config_path="hardware/sensor_protocol/soil_sensor.yaml")
    assert exit_code == 0

def test_sensor_diagnostic_missing_config():
    """Verify CLI diagnostic reports error code 1 when config file does not exist."""
    exit_code = run_diagnostic(config_path="nonexistent/path/sensor.yaml")
    assert exit_code == 1

def test_battery_monitor_zero_hallucination_real_mode():
    """Verify that when battery hardware is absent in real mode, battery is reported as UNAVAILABLE (never fake %)."""
    bm = BatteryMonitor(demo_mode=False)
    with patch("psutil.sensors_battery", return_value=None):
        status = bm.get_status(demo_mode=False)
        assert status["percent"] is None
        assert status["status"] == "UNAVAILABLE"
        assert status["is_mock"] is False

def test_battery_monitor_demo_mode_simulation():
    """Verify that in demo mode, battery provides labeled simulated telemetry."""
    bm = BatteryMonitor(demo_mode=True)
    with patch("psutil.sensors_battery", return_value=None):
        status = bm.get_status(demo_mode=True)
        assert status["percent"] == 88.5
        assert status["is_mock"] is True
        assert status["status"] == "DISCHARGING"
