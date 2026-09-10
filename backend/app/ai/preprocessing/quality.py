"""
Image Quality Assessment Engine for Crop Leaf Pathology Scanning.
Detects blur, underexposure, overexposure, and inadequate resolution before inference.
"""
from typing import List, Tuple, Optional, Any, Dict
import numpy as np
import cv2
from PIL import Image
import io
from app.schemas.vision import ImageQualityResult
from app.core.logging import log_event

class ImageQualityValidator:
    """Validates crop leaf image suitability for AI pathology classification."""

    def __init__(
        self,
        min_width: int = 120,
        min_height: int = 120,
        min_blur_score: float = 20.0,
        min_brightness: float = 25.0,
        max_brightness: float = 235.0
    ):
        self.min_width = min_width
        self.min_height = min_height
        self.min_blur_score = min_blur_score
        self.min_brightness = min_brightness
        self.max_brightness = max_brightness

    def decode_image(self, image_data: Any) -> Optional[np.ndarray]:
        """Safely decodes raw bytes or converts PIL image into OpenCV BGR numpy array."""
        if image_data is None:
            return None

        if isinstance(image_data, np.ndarray):
            return image_data

        if isinstance(image_data, (bytes, bytearray)):
            try:
                nparr = np.frombuffer(image_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                return img
            except Exception as e:
                log_event("AI", "WARNING", f"Failed to decode image bytes: {e}")
                return None

        if hasattr(image_data, "read"):
            try:
                data = image_data.read()
                nparr = np.frombuffer(data, np.uint8)
                return cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            except Exception:
                return None

        return None

    def validate(self, image_input: Any) -> ImageQualityResult:
        """Evaluates image against sharpness, exposure, and resolution thresholds."""
        img = self.decode_image(image_input)
        if img is None:
            return ImageQualityResult(
                valid=False,
                score=0.0,
                issues=["INVALID_IMAGE"],
                resolution="0x0",
                blur_score=0.0,
                brightness_score=0.0,
                message="Unable to decode image. Please provide a valid JPEG or PNG file."
            )

        h, w = img.shape[:2]
        resolution_str = f"{w}x{h}"
        issues: List[str] = []

        # 1. Resolution Check
        if w < self.min_width or h < self.min_height:
            issues.append("IMAGE_TOO_SMALL")

        # Convert to Grayscale for Blur & Exposure Metrics
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img

        # 2. Sharpness / Blur Estimate (Laplacian Variance)
        blur_val = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        if blur_val < self.min_blur_score:
            issues.append("IMAGE_TOO_BLURRY")

        # 3. Luminance / Brightness Exposure Check
        brightness_val = float(np.mean(gray))
        if brightness_val < self.min_brightness:
            issues.append("IMAGE_TOO_DARK")
        elif brightness_val > self.max_brightness:
            issues.append("IMAGE_TOO_BRIGHT")

        # Compute Normalized Quality Score (0.0 to 1.0)
        # Blur component score
        blur_norm = min(blur_val / 100.0, 1.0)
        # Brightness component score (ideal is centered around 128)
        brightness_norm = 1.0 - abs(brightness_val - 128.0) / 128.0
        brightness_norm = max(0.0, min(brightness_norm, 1.0))
        # Resolution penalty
        res_norm = 1.0 if (w >= 224 and h >= 224) else (0.5 if (w >= self.min_width and h >= self.min_height) else 0.0)

        quality_score = round(float(0.45 * blur_norm + 0.35 * brightness_norm + 0.20 * res_norm), 2)
        is_valid = len(issues) == 0

        # Construct Farmer-friendly explanation
        if is_valid:
            farmer_msg = "Image quality is optimal for crop diagnosis."
        else:
            issue_msgs = []
            if "IMAGE_TOO_SMALL" in issues:
                issue_msgs.append("Image resolution is too low. Move closer to the crop leaf.")
            if "IMAGE_TOO_BLURRY" in issues:
                issue_msgs.append("Image is blurry. Hold the camera steady and focus on the leaf.")
            if "IMAGE_TOO_DARK" in issues:
                issue_msgs.append("Image is too dark. Increase lighting or avoid heavy shadows.")
            if "IMAGE_TOO_BRIGHT" in issues:
                issue_msgs.append("Image is overexposed. Reduce harsh sunlight glare on the leaf.")
            farmer_msg = " ".join(issue_msgs)

        log_event("AI", "INFO", f"Image Quality Evaluated: valid={is_valid}, score={quality_score}, issues={issues}")

        return ImageQualityResult(
            valid=is_valid,
            score=quality_score,
            issues=issues,
            resolution=resolution_str,
            blur_score=round(blur_val, 1),
            brightness_score=round(brightness_val, 1),
            message=farmer_msg
        )
