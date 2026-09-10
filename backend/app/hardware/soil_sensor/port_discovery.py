"""
Safe USB-to-RS485 Serial Interface Discovery for TEJAS.

Discovers system COM and ttyUSB/ttyACM serial ports without asserting
fabricated hardware attachments.
"""

import os
from typing import Dict, Any, List, Optional
from app.hardware.detection import SystemDetector
from app.core.logging import log_event


def discover_rs485_ports(configured_port: Optional[str] = None) -> Dict[str, Any]:
    """
    Safely inspects attached serial interfaces and evaluates candidate RS485 adapters.
    
    Zero Hardware Hallucination:
    - Discovery only enumerates available physical serial devices.
    - Never asserts that a port has an attached active sensor.
    - Actual communication must still depend on verified sensor protocol configuration.
    """
    all_interfaces = SystemDetector.list_serial_interfaces()
    
    available_devices = [p["device"] for p in all_interfaces]
    configured_exists = bool(configured_port and configured_port in available_devices)
    
    candidates = [
        p for p in all_interfaces 
        if p.get("is_usb_rs485_candidate") or (os.name != "nt" and ("ttyUSB" in p["device"] or "ttyACM" in p["device"]))
    ]
    
    if not candidates:
        # Fall back to any available serial interface as potential candidate
        candidates = all_interfaces

    log_event(
        "SOIL",
        "INFO",
        f"Serial discovery found {len(all_interfaces)} port(s). Configured '{configured_port}' present: {configured_exists}"
    )

    return {
        "configured_port": configured_port,
        "configured_port_exists": configured_exists,
        "candidate_ports": candidates,
        "all_ports": all_interfaces,
        "total_ports": len(all_interfaces)
    }
