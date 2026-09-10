"""
Image Preprocessing Pipeline for Edge AI Vision Models.
Standardizes resolution, color channels, and tensor shapes for local neural networks.
"""
from typing import Any, Tuple, Optional
import numpy as np
import cv2

class ImagePreprocessor:
    """Prepares decoded crop images for neural network inference."""

    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size

    def preprocess(self, img_bgr: np.ndarray, normalize: bool = True) -> np.ndarray:
        """
        Transforms BGR image to RGB, resizes to target_size, normalizes pixel values,
        and adds batch dimension: (1, 3, H, W).
        """
        if img_bgr is None:
            raise ValueError("Cannot preprocess None image")

        # 1. Convert BGR to RGB
        if len(img_bgr.shape) == 3 and img_bgr.shape[2] == 3:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_GRAY2RGB)

        # 2. Resize with bilinear interpolation
        resized = cv2.resize(img_rgb, self.target_size, interpolation=cv2.INTER_LINEAR)

        # 3. Normalize pixels
        if normalize:
            float_img = resized.astype(np.float32) / 255.0
            # Standard ImageNet Mean and Std
            mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
            std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
            normalized = (float_img - mean) / std
        else:
            normalized = resized.astype(np.float32)

        # 4. Transpose from (H, W, C) to (C, H, W)
        chw = np.transpose(normalized, (2, 0, 1))

        # 5. Add Batch Dimension -> (1, C, H, W)
        batch_tensor = np.expand_dims(chw, axis=0)
        return batch_tensor
