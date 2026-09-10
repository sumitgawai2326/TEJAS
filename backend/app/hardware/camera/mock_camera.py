"""
Mock Camera Driver for Safe UI & Presentation Testing (DEMO_MODE=true).
"""
import datetime
from typing import Dict, Any, Optional, Tuple
from app.hardware.camera.base import BaseCamera

class MockCamera(BaseCamera):
    def __init__(self):
        self._is_open = True

    def initialize(self) -> bool:
        self._is_open = True
        return True

    def capture(self) -> Tuple[bool, Optional[Any], Dict[str, Any]]:
        if not self._is_open:
            return False, None, {
                "source": "MOCK_CAMERA_RELEASED",
                "is_mock": True,
                "error": "Mock camera is closed"
            }
        
        # Generate high quality synthetic leaf frame (640x480) for offline demo testing
        import numpy as np
        import cv2
        frame = np.full((480, 640, 3), (34, 139, 34), dtype=np.uint8) # Forest green
        # Draw high-contrast leaf vein patterns to provide good sharpness/blur score
        for i in range(40, 440, 30):
            cv2.line(frame, (320, 40), (i, 440), (50, 205, 50), 2)
            cv2.circle(frame, (i, 240), 12, (20, 100, 20), -1)
        
        return True, frame, {
            "source": "DEMO_SAMPLE_VIEWFINDER",
            "is_mock": True,
            "resolution": "640x480",
            "fps": 30,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }


    def release(self) -> None:
        self._is_open = False

    def is_available(self) -> bool:
        return self._is_open

    def get_status(self) -> Dict[str, Any]:
        return {
            "driver": "MockCamera",
            "mode": "DEMO_SIMULATION",
            "available": self._is_open,
            "status": "SIMULATED" if self._is_open else "CAMERA_UNAVAILABLE",
            "is_mock": True,
            "camera_device_index": 0,
            "resolution": "1920x1080",
            "fps": 30,
            "details": "Demo sample image viewfinder active"
        }
