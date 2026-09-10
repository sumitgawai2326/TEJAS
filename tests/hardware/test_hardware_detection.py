"""
Automated Unit Tests for Hardware Detection & System Telemetry Layer.
Tests cross-platform safe detection on Raspberry Pi and Development PCs.
"""
import os
import pytest
from unittest.mock import patch, mock_open
from app.hardware.detection import SystemDetector

def test_platform_info_workstation_fallback():
    """Verify safe fallback when not running on Raspberry Pi."""
    with patch("os.path.exists", return_value=False):
        info = SystemDetector.get_platform_info()
        assert "board_model" in info
        assert isinstance(info["is_raspberry_pi"], bool)
        assert "architecture" in info
        assert "python_version" in info
        assert "os_name" in info

def test_platform_info_raspberry_pi_detection():
    """Verify Raspberry Pi 5 detection via /proc/device-tree/model."""
    mock_model = "Raspberry Pi 5 Model B Rev 1.0\x00"
    with patch("os.path.exists", side_effect=lambda path: path == "/proc/device-tree/model"):
        with patch("builtins.open", mock_open(read_data=mock_model)):
            info = SystemDetector.get_platform_info()
            assert info["is_raspberry_pi"] is True
            assert info["rpi_version"] == "Raspberry Pi 5"
            assert "Raspberry Pi 5" in info["board_model"]

def test_list_serial_interfaces():
    """Verify serial interface discovery does not crash and returns list."""
    ports = SystemDetector.list_serial_interfaces()
    assert isinstance(ports, list)
    for p in ports:
        assert "device" in p
        assert "description" in p
        assert "hardware_id" in p
        assert "is_usb_rs485_candidate" in p

def test_get_storage_metrics():
    """Verify local storage capacity & free space calculation."""
    storage = SystemDetector.get_storage_metrics(".")
    assert "total_gb" in storage
    assert "free_gb" in storage
    assert "percent_used" in storage
    assert "is_low_space" in storage
    assert storage["total_gb"] > 0
    assert storage["free_gb"] >= 0

def test_get_cpu_temperature():
    """Verify CPU temperature query executes safely without throwing exceptions."""
    temp = SystemDetector.get_cpu_temperature()
    if temp is not None:
        assert isinstance(temp, float)
        assert -20.0 < temp < 150.0
