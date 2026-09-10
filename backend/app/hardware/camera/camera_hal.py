"""
Physical V4L2 / CSI / UVC Camera Hardware Abstraction Layer (DEMO_MODE=false).
Strict Zero Hardware Hallucination Policy:
If camera is physically disconnected or unavailable, is_available returns False
and capture returns (False, None, error="CAMERA_UNAVAILABLE").
"""
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
        """Capture real frame without fabricating data if camera is absent."""
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
        """Non-intrusive probe check for camera hardware."""
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
