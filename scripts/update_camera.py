import os

base_camera = r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend\app\hardware\camera"

# 1. base.py
base_code = """\"\"\"
Abstract Base Hardware Interface for Camera Subsystem.
\"\"\"
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple

class BaseCamera(ABC):
    \"\"\"Abstract Base Class for Camera Hardware Drivers.\"\"\"

    @abstractmethod
    def initialize(self) -> bool:
        \"\"\"Initialize hardware capture device or prepare mock image engine.\"\"\"
        pass

    @abstractmethod
    def capture(self) -> Tuple[bool, Optional[Any], Dict[str, Any]]:
        \"\"\"
        Capture single frame.
        Returns: (success: bool, frame: Optional[np.ndarray], metadata: Dict[str, Any]).
        Zero Hardware Hallucination: never fabricate frames if camera is unavailable.
        \"\"\"
        pass

    @abstractmethod
    def release(self) -> None:
        \"\"\"Release camera device handle and hardware resources.\"\"\"
        pass

    @abstractmethod
    def is_available(self) -> bool:
        \"\"\"Check if camera device is physically available and functional.\"\"\"
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        \"\"\"Return comprehensive hardware telemetry for camera.\"\"\"
        pass
"""

with open(os.path.join(base_camera, "base.py"), "w", encoding="utf-8") as f:
    f.write(base_code)

# 2. mock_camera.py
mock_code = """\"\"\"
Mock Camera Driver for Safe UI & Presentation Testing (DEMO_MODE=true).
\"\"\"
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
        
        return True, None, {
            "source": "DEMO_SAMPLE_VIEWFINDER",
            "is_mock": True,
            "resolution": "1920x1080",
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
"""

with open(os.path.join(base_camera, "mock_camera.py"), "w", encoding="utf-8") as f:
    f.write(mock_code)

# 3. camera_hal.py
hal_code = """\"\"\"
Physical V4L2 / CSI / UVC Camera Hardware Abstraction Layer (DEMO_MODE=false).
Strict Zero Hardware Hallucination Policy:
If camera is physically disconnected or unavailable, is_available returns False
and capture returns (False, None, error="CAMERA_UNAVAILABLE").
\"\"\"
import datetime
from typing import Dict, Any, Optional, Tuple
from app.hardware.camera.base import BaseCamera
from app.core.logging import log_event

class CameraHAL(BaseCamera):
    def __init__(self, camera_device: int = 0, width: int = 1920, height: int = 1080, fps: int = 30):
        self.camera_device = camera_device
        self.width = width
        self.height = height
        self.fps = fps
        self._cap = None
        self._is_initialized = False

    def initialize(self) -> bool:
        try:
            import cv2
            self._cap = cv2.VideoCapture(self.camera_device)
            if self._cap and self._cap.isOpened():
                self._cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self._cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                self._cap.set(cv2.CAP_PROP_FPS, self.fps)
                self._is_initialized = True
                log_event("CAMERA", "INFO", f"Camera index {self.camera_device} initialized successfully")
                return True
            else:
                self._is_initialized = False
                log_event("CAMERA", "WARNING", f"Camera index {self.camera_device} failed to open (CAMERA_UNAVAILABLE)")
                return False
        except Exception as e:
            self._is_initialized = False
            log_event("CAMERA", "ERROR", f"Exception initializing camera index {self.camera_device}: {e}")
            return False

    def capture(self) -> Tuple[bool, Optional[Any], Dict[str, Any]]:
        \"\"\"Capture real frame without fabricating data if camera is absent.\"\"\"
        if not self._is_initialized and not self.initialize():
            return False, None, {
                "source": "CAMERA_UNAVAILABLE",
                "is_mock": False,
                "error": f"Physical camera index {self.camera_device} unavailable",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }

        try:
            ret, frame = self._cap.read()
            if not ret or frame is None:
                return False, None, {
                    "source": "CAPTURE_FAILED",
                    "is_mock": False,
                    "error": "Failed to read frame from video device",
                    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
                }
            return True, frame, {
                "source": f"V4L2_DEVICE_{self.camera_device}",
                "is_mock": False,
                "shape": frame.shape,
                "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }
        except Exception as e:
            return False, None, {
                "source": "CAPTURE_EXCEPTION",
                "is_mock": False,
                "error": str(e),
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }

    def release(self) -> None:
        if self._cap:
            try:
                self._cap.release()
            except Exception:
                pass
        self._cap = None
        self._is_initialized = False
        log_event("CAMERA", "INFO", f"Camera index {self.camera_device} released")

    def is_available(self) -> bool:
        \"\"\"Non-intrusive probe check for camera hardware.\"\"\"
        if self._is_initialized and self._cap and self._cap.isOpened():
            return True
        return self.initialize()

    def get_status(self) -> Dict[str, Any]:
        available = self.is_available()
        return {
            "driver": "CameraHAL",
            "mode": "REAL_HARDWARE",
            "available": available,
            "status": "READY" if available else "CAMERA_UNAVAILABLE",
            "is_mock": False,
            "camera_device_index": self.camera_device,
            "resolution": f"{self.width}x{self.height}",
            "fps": self.fps,
            "details": f"Physical video device index {self.camera_device} ({'Active' if available else 'Unavailable'})"
        }
"""

with open(os.path.join(base_camera, "camera_hal.py"), "w", encoding="utf-8") as f:
    f.write(hal_code)

# 4. __init__.py
cam_init = """\"\"\"
Camera Factory Selector.
\"\"\"
from app.hardware.camera.base import BaseCamera
from app.hardware.camera.mock_camera import MockCamera
from app.hardware.camera.camera_hal import CameraHAL
from app.core.config import settings

def get_camera() -> BaseCamera:
    if settings.DEMO_MODE:
        return MockCamera()
    return CameraHAL(
        camera_device=settings.CAMERA_DEVICE,
        width=settings.CAMERA_WIDTH,
        height=settings.CAMERA_HEIGHT,
        fps=settings.CAMERA_FPS
    )
"""

with open(os.path.join(base_camera, "__init__.py"), "w", encoding="utf-8") as f:
    f.write(cam_init)

print("Camera HAL abstraction layer updated.")
