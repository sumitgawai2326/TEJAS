"""
Battery & Power Management Telemetry for Portable Edge Operation.
Strict Zero Hardware Hallucination Policy:
Never fabricates battery percentage in Real Hardware Mode (DEMO_MODE=false).
"""
import psutil
from typing import Dict, Any, Optional

class BatteryMonitor:
    def __init__(self, demo_mode: bool = True):
        self.demo_mode = demo_mode

    def get_status(self, demo_mode: Optional[bool] = None) -> Dict[str, Any]:
        """
        Reads real OS power status or provides safe demo telemetry.
        If demo_mode is False and no physical battery/PMIC is detected, returns UNAVAILABLE.
        """
        is_demo = self.demo_mode if demo_mode is None else demo_mode
        battery = psutil.sensors_battery()
        
        if battery is not None:
            return {
                "percent": round(battery.percent, 1),
                "power_plugged": battery.power_plugged,
                "seconds_left": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else -1,
                "status": "CHARGING" if battery.power_plugged else ("DISCHARGING" if battery.percent > 20 else "LOW_BATTERY"),
                "is_mock": False,
                "note": "Hardware battery sensor active"
            }
        
        if is_demo:
            # Simulated battery telemetry in Demo Mode
            return {
                "percent": 88.5,
                "power_plugged": False,
                "seconds_left": 14400,
                "status": "DISCHARGING",
                "is_mock": True,
                "note": "Hardware UPS / Power pack running (Demo Simulation)"
            }
        
        # Real Hardware Mode without I2C PMIC fuel gauge / smart battery
        return {
            "percent": None,
            "power_plugged": None,
            "seconds_left": -1,
            "status": "UNAVAILABLE",
            "is_mock": False,
            "note": "Battery telemetry unavailable (no PMIC/I2C fuel gauge detected)"
        }

battery_monitor = BatteryMonitor()
