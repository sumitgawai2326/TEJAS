"""
Model Validation & Integrity Verification Subsystem for KrishiDrishti Edge.
Performs pre-flight checks on neural network binaries:
- File existence & signature
- Tensor input/output shape consistency (dynamic input dimensions)
- Class mapping length vs output logit dimensions
- Non-destructive dummy tensor smoke inference
"""
import os
from typing import Dict, Any, List, Optional
import numpy as np
from pydantic import BaseModel, Field
from app.core.logging import log_event

class ValidationReport(BaseModel):
    model_path: str
    status: str = Field(..., description="MODEL_VALID, MODEL_INVALID, MODEL_NOT_FOUND, MODEL_INCOMPATIBLE")
    is_valid: bool
    input_shape: List[int] = Field(default_factory=list)
    output_shape: List[int] = Field(default_factory=list)
    smoke_test_passed: bool = False
    error_message: Optional[str] = None
    details: Optional[str] = None

class ModelValidator:
    """Validates structural and computational integrity of production neural network models."""

    @staticmethod
    def validate_onnx_model(
        model_path: str,
        expected_classes_count: Optional[int] = None,
        custom_input_shape: Optional[List[int]] = None
    ) -> ValidationReport:
        """
        Validates an ONNX model file.
        Dynamically extracts input dimensions from model graph metadata.
        """
        if not os.path.exists(model_path):
            return ValidationReport(
                model_path=model_path,
                status="MODEL_NOT_FOUND",
                is_valid=False,
                error_message=f"Model file does not exist at: {model_path}"
            )

        try:
            import onnxruntime as ort
        except ImportError:
            return ValidationReport(
                model_path=model_path,
                status="MODEL_INCOMPATIBLE",
                is_valid=False,
                error_message="onnxruntime library not installed in Python environment."
            )

        try:
            sess = ort.InferenceSession(model_path, providers=['CPUExecutionProvider'])
            inputs = sess.get_inputs()
            outputs = sess.get_outputs()

            if not inputs:
                return ValidationReport(
                    model_path=model_path,
                    status="MODEL_INVALID",
                    is_valid=False,
                    error_message="ONNX model contains no input tensors."
                )

            # Read input tensor dimensions dynamically
            raw_input_shape = inputs[0].shape
            resolved_shape = []
            for dim in raw_input_shape:
                if isinstance(dim, int) and dim > 0:
                    resolved_shape.append(dim)
                else:
                    resolved_shape.append(1) # Batch size default

            # If model requires 4D [N, C, H, W] but has dynamic dimensions, use resolved
            if len(resolved_shape) != 4 and custom_input_shape:
                resolved_shape = custom_input_shape

            raw_output_shape = outputs[0].shape if outputs else []
            resolved_output_shape = [s if isinstance(s, int) and s > 0 else 1 for s in raw_output_shape]

            # Validate Class mapping count against output dimension if specified
            if expected_classes_count is not None and len(resolved_output_shape) >= 2:
                output_classes = resolved_output_shape[-1]
                if output_classes != expected_classes_count:
                    return ValidationReport(
                        model_path=model_path,
                        status="MODEL_INVALID",
                        is_valid=False,
                        input_shape=resolved_shape,
                        output_shape=resolved_output_shape,
                        error_message=f"Output logit dimension ({output_classes}) does not match expected class count ({expected_classes_count})."
                    )

            # Execute non-destructive smoke inference test on dummy tensor
            dummy_input = np.zeros(resolved_shape, dtype=np.float32)
            input_name = inputs[0].name
            smoke_out = sess.run(None, {input_name: dummy_input})

            if not smoke_out or len(smoke_out) == 0:
                return ValidationReport(
                    model_path=model_path,
                    status="MODEL_INVALID",
                    is_valid=False,
                    input_shape=resolved_shape,
                    output_shape=resolved_output_shape,
                    smoke_test_passed=False,
                    error_message="Smoke inference returned empty output."
                )

            log_event("AI", "INFO", f"Model validation PASSED for {model_path} (Input: {resolved_shape}, Output: {resolved_output_shape})")

            return ValidationReport(
                model_path=model_path,
                status="MODEL_VALID",
                is_valid=True,
                input_shape=resolved_shape,
                output_shape=resolved_output_shape,
                smoke_test_passed=True,
                details=f"ONNX Model structurally valid. Input: {resolved_shape}, Output: {resolved_output_shape}."
            )

        except Exception as e:
            log_event("AI", "ERROR", f"Model validation exception for {model_path}: {e}")
            return ValidationReport(
                model_path=model_path,
                status="MODEL_INVALID",
                is_valid=False,
                error_message=str(e)
            )
