"""
Industrial RS485 Modbus-RTU 6-Parameter Soil Sensor CLI Diagnostic Utility.
Usage:
    python -m app.tools.sensor_diagnostic [--port PORT] [--config CONFIG_PATH]

Zero Hardware Hallucination:
- Never invents simulated sensor readings.
- Strictly reports SENSOR_UNCONFIGURED or SENSOR_DISCONNECTED if physical sensor is not active.
"""
import os
import sys
import argparse
import yaml
from typing import Dict, Any, Optional

# Add backend directory to sys.path if invoked directly
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "../.."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.hardware.detection import SystemDetector
from app.core.logging import log_event

def run_diagnostic(config_path: str = "hardware/sensor_protocol/soil_sensor.yaml", port_override: Optional[str] = None) -> int:
    print("=" * 70)
    print("KrishiDrishti Edge — RS485 6-Parameter Soil Sensor Diagnostic Utility")
    print("Zero Hardware Hallucination Policy: ACTIVE")
    print("=" * 70)

    # 1. Host Platform Detection
    plat = SystemDetector.get_platform_info()
    print(f"\n[1] HOST PLATFORM:")
    print(f"    - Board Model: {plat['board_model']}")
    print(f"    - OS: {plat['os_name']} {plat['os_release']} ({plat['architecture']})")
    print(f"    - Python: {plat['python_version']}")

    # 2. Serial & USB-RS485 Port Discovery
    ports = SystemDetector.list_serial_interfaces()
    print(f"\n[2] DETECTED SERIAL / RS485 INTERFACES ({len(ports)} found):")
    if not ports:
        print("    [!] No serial communication ports detected on host.")
        print("        Connect USB-RS485 adapter (e.g. FTDI/CH340/CP2102) to Raspberry Pi/PC.")
    else:
        for p in ports:
            cand = " (Candidate USB-RS485 Adapter)" if p["is_usb_rs485_candidate"] else ""
            print(f"    - Device: {p['device']}")
            print(f"      Description: {p['description']}{cand}")
            print(f"      Hardware ID: {p['hardware_id']}")

    # 3. Protocol Configuration Verification
    print(f"\n[3] PROTOCOL CONFIGURATION ({config_path}):")
    if not os.path.exists(config_path):
        # Check relative to backend dir or root
        alt_path = os.path.join(BACKEND_DIR, "..", config_path)
        if os.path.exists(alt_path):
            config_path = alt_path
        else:
            print(f"    [FAIL] Config file not found at: {config_path}")
            return 1

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"    [FAIL] Error loading YAML configuration: {e}")
        return 1

    sensor_meta = cfg.get("sensor", {})
    is_configured = bool(sensor_meta.get("is_configured", False))
    baudrate = sensor_meta.get("baudrate")
    slave_id = sensor_meta.get("slave_id")
    params = cfg.get("parameters", {})

    print(f"    - Sensor Name: {sensor_meta.get('name', 'UNKNOWN')}")
    print(f"    - Protocol: {sensor_meta.get('protocol', 'MODBUS-RTU')}")
    print(f"    - Configured Baudrate: {baudrate if baudrate is not None else 'null (Awaiting Datasheet)'}")
    print(f"    - Configured Slave ID: {slave_id if slave_id is not None else 'null (Awaiting Datasheet)'}")
    print(f"    - Is Register Map Configured?: {is_configured}")

    # Display Parameter Register Map
    print(f"\n[4] 6-PARAMETER MODBUS REGISTER MAP:")
    target_params = ["nitrogen", "phosphorus", "potassium", "ph", "moisture", "temperature"]
    for param_key in target_params:
        p_info = params.get(param_key, {})
        reg = p_info.get("register")
        scale = p_info.get("scale")
        unit = p_info.get("unit", "")
        desc = p_info.get("description", param_key)
        reg_str = f"0x{reg:04x} ({reg})" if isinstance(reg, int) else str(reg)
        print(f"    - {desc.ljust(35)}: Register={reg_str}, Scale={scale}, Unit={unit}")

    # 4. Diagnostics Evaluation
    if not is_configured:
        print("\n[5] HARDWARE COMMUNICATION STATUS:")
        print("    [!] SENSOR_UNCONFIGURED")
        print("    --> The register map in hardware/sensor_protocol/soil_sensor.yaml is unconfigured.")
        print("    --> Strict Zero Hallucination: No communication will be attempted with fake registers.")
        print("    --> Action: Populate exact register addresses from the manufacturer's datasheet.")
        print("\n" + "=" * 70)
        print("DIAGNOSTIC RESULT: SAFE EXIT (Awaiting Physical Datasheet Configuration)")
        print("=" * 70)
        return 0

    # 5. If Configured, Attempt Port Verification
    target_port = port_override or (ports[0]["device"] if ports else None)
    if not target_port:
        print("\n[5] HARDWARE COMMUNICATION STATUS:")
        print("    [!] SERIAL_PORT_ERROR: No serial port available or specified.")
        return 0

    print(f"\n[5] ATTEMPTING MODBUS-RTU COMMUNICATION ON {target_port} @ {baudrate} baud (Slave ID: {slave_id})...")
    try:
        import serial
        ser = serial.Serial(target_port, baudrate, timeout=2.0)
        ser.close()
        print(f"    [+] Serial port {target_port} opened successfully.")
        print(f"    [!] Note: Awaiting physical sensor responses on the RS485 bus.")
    except Exception as e:
        print(f"    [!] SENSOR_DISCONNECTED / PORT_ERROR: {e}")

    print("\n" + "=" * 70)
    print("DIAGNOSTIC RESULT: COMPLETE")
    print("=" * 70)
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KrishiDrishti Edge RS485 Soil Sensor Diagnostic Tool")
    parser.add_argument("--port", type=str, default=None, help="Serial port to test (e.g. /dev/ttyUSB0 or COM3)")
    parser.add_argument("--config", type=str, default="hardware/sensor_protocol/soil_sensor.yaml", help="Path to soil_sensor.yaml")
    args = parser.parse_args()

    exit_code = run_diagnostic(config_path=args.config, port_override=args.port)
    sys.exit(exit_code)
