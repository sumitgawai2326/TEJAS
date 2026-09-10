"""
Abstract Base Hardware Interface for Camera Subsystem.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple

class BaseCamera(ABC):
    """Abstract Base Class for Camera Hardware Drivers."""

    @abstractmethod
    def initialize(self) -> bool:
        """Initialize hardware capture device or prepare mock image engine."""
        pass

    @abstractmethod
    def capture(self) -> Tuple[bool, Optional[Any], Dict[str, Any]]:
        """
        Capture single frame.
        Returns: (success: bool, frame: Optional[np.ndarray], metadata: Dict[str, Any]).
        Zero Hardware Hallucination: never fabricate frames if camera is unavailable.
        """
        pass

    @abstractmethod
    def release(self) -> None:
        """Release camera device handle and hardware resources."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if camera device is physically available and functional."""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return comprehensive hardware telemetry for camera."""
        pass
