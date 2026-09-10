"""
Hardware Capability & Platform Detection Layer for KrishiDrishti Edge.
Detects physical Raspberry Pi hardware, OS platform, CPU thermals, and available serial/RS485 interfaces safely.
Zero Hardware Hallucination: Never claims Raspberry Pi on non-Pi platforms.
"""
import os
import sys
import platform
import psutil
from typing import Dict, Any, List, Optional
from app.core.logging import log_event

class SystemDetector:
    """Discovers host hardware, architecture, and attached interfaces."""

    @staticmethod
    def get_platform_info() -> Dict[str, Any]:
        """
        Detects whether running on physical Raspberry Pi or a development workstation.
        Reads /proc/device-tree/model on Linux / Raspberry Pi OS.
        """
        board_model = "Unknown Host"
        is_raspberry_pi = False
        rpi_version = None

        # Check Linux Device Tree (Standard Raspberry Pi identifier)
        device_tree_model_path = "/proc/device-tree/model"
        if os.path.exists(device_tree_model_path):
            try:
                with open(device_tree_model_path, "r", encoding="utf-8", errors="ignore") as f:
                    model_str = f.read().strip().replace("\x00", "")
                    if model_str:
                        board_model = model_str
                        if "Raspberry Pi" in model_str:
                            is_raspberry_pi = True
                            if "5" in model_str:
                                rpi_version = "Raspberry Pi 5"
                            elif "4" in model_str:
                                rpi_version = "Raspberry Pi 4"
                            else:
                                rpi_version = "Raspberry Pi (Legacy)"
            except Exception as e:
                log_event("HARDWARE", "WARNING", f"Could not read device tree model: {e}")

        if not is_raspberry_pi:
            system_name = platform.system()
            machine_arch = platform.machine()
            board_model = f"Development Host ({system_name} {machine_arch})"

        return {
            "board_model": board_model,
            "is_raspberry_pi": is_raspberry_pi,
            "rpi_version": rpi_version,
            "os_name": platform.system(),
            "os_release": platform.release(),
            "os_version": platform.version(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "hostname": platform.node()
        }

    @staticmethod
    def list_serial_interfaces() -> List[Dict[str, Any]]:
        """
        Discovers serial ports and USB-RS485 adapters.
        Uses pyserial's list_ports utility.
        """
        interfaces = []
        try:
            import serial.tools.list_ports as list_ports
            ports = list_ports.comports()
            for p in ports:
                is_usb_serial = bool("USB" in (p.description or "").upper() or "USB" in (p.hwid or "").upper() or "TTYUSB" in (p.device or "").upper() or "TTYACM" in (p.device or "").upper())
                interfaces.append({
                    "device": p.device,
                    "description": p.description or "Unknown Serial Port",
                    "hardware_id": p.hwid or "Unknown",
                    "is_usb_rs485_candidate": is_usb_serial
                })
        except Exception as e:
            log_event("HARDWARE", "WARNING", f"Error scanning serial ports: {e}")

        return interfaces

    @staticmethod
    def get_cpu_temperature() -> Optional[float]:
        """
        Reads CPU thermal sensor.
        Supports Raspberry Pi /sys/class/thermal and psutil thermal sensors.
        """
        # 1. Raspberry Pi direct sysfs thermal zone
        rpi_thermal_path = "/sys/class/thermal/thermal_zone0/temp"
        if os.path.exists(rpi_thermal_path):
            try:
                with open(rpi_thermal_path, "r") as f:
                    temp_raw = f.read().strip()
                    if temp_raw:
                        return round(float(temp_raw) / 1000.0, 1)
            except Exception:
                pass

        # 2. psutil sensors_temperatures fallback (Linux)
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                if temps:
                    for key in ["cpu_thermal", "coretemp", "k10temp", "cpu-thermal", "soc_thermal"]:
                        if key in temps and temps[key]:
                            return round(temps[key][0].current, 1)
        except Exception:
            pass

        return None

    @staticmethod
    def get_storage_metrics(path: str = ".") -> Dict[str, Any]:
        """Reads local disk storage metrics."""
        try:
            abs_path = os.path.abspath(path)
            disk = psutil.disk_usage(abs_path)
            return {
                "total_gb": round(disk.total / (1024 ** 3), 2),
                "used_gb": round(disk.used / (1024 ** 3), 2),
                "free_gb": round(disk.free / (1024 ** 3), 2),
                "percent_used": disk.percent,
                "is_low_space": (disk.free / (1024 ** 2)) < 500  # less than 500 MB
            }
        except Exception as e:
            return {
                "total_gb": 0.0,
                "used_gb": 0.0,
                "free_gb": 0.0,
                "percent_used": 0.0,
                "is_low_space": False,
                "error": str(e)
            }
