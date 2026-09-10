"""
AI Vision Latency Profiler & Monotonic Pipeline Timing for KrishiDrishti Edge.
Tracks rolling latency statistics across image decode, preprocessing, inference, and postprocessing.
Strict Zero AI Hallucination Policy: Only records real measured intervals from time.perf_counter().
"""
import time
from typing import Dict, Any, List
from collections import deque
from pydantic import BaseModel, Field

class LatencyBreakdown(BaseModel):
    image_decode_ms: float = 0.0
    preprocessing_ms: float = 0.0
    inference_ms: float = 0.0
    postprocessing_ms: float = 0.0
    total_ms: float = 0.0
    accelerator: str = "CPU"
    timestamp: float = Field(default_factory=time.time)

class AIPipelineProfiler:
    """Collects and aggregates real runtime performance measurements."""

    def __init__(self, max_history: int = 50):
        self.history: deque = deque(maxlen=max_history)

    def record(
        self,
        decode_ms: float,
        preprocess_ms: float,
        inference_ms: float,
        postprocess_ms: float,
        accelerator: str
    ) -> LatencyBreakdown:
        total = round(decode_ms + preprocess_ms + inference_ms + postprocess_ms, 2)
        breakdown = LatencyBreakdown(
            image_decode_ms=round(decode_ms, 2),
            preprocessing_ms=round(preprocess_ms, 2),
            inference_ms=round(inference_ms, 2),
            postprocessing_ms=round(postprocess_ms, 2),
            total_ms=total,
            accelerator=accelerator
        )
        self.history.append(breakdown)
        return breakdown

    def get_summary(self) -> Dict[str, Any]:
        """Calculates rolling average latencies."""
        if not self.history:
            return {
                "total_inferences_measured": 0,
                "avg_inference_ms": None,
                "avg_total_ms": None,
                "status": "NO_MEASUREMENTS_RECORDED"
            }

        inferences = [x.inference_ms for x in self.history]
        totals = [x.total_ms for x in self.history]

        return {
            "total_inferences_measured": len(self.history),
            "avg_inference_ms": round(sum(inferences) / len(inferences), 2),
            "min_inference_ms": round(min(inferences), 2),
            "max_inference_ms": round(max(inferences), 2),
            "avg_total_ms": round(sum(totals) / len(totals), 2),
            "last_latency": self.history[-1].model_dump()
        }

ai_profiler = AIPipelineProfiler()
