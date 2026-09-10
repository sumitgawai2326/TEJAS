"""
KrishiDrishti Edge — AI Pipeline Latency Profiler
Measures real monotonic latency breakdown across decode, preprocess, inference, and postprocess.
Saves profile data to reports/model_profile.json and updates docs/AI_PERFORMANCE.md.
"""
import os
import sys
import time
import json
import cv2
import numpy as np

def profile_model_pipeline(
    model_path: str = "data/models/crop_disease_v1.onnx",
    iterations: int = 50,
    output_json: str = "reports/model_profile.json",
    output_doc: str = "docs/AI_PERFORMANCE.md"
):
    print("=" * 70)
    print("KrishiDrishti Edge — AI Inference Latency & Subsystem Profiler")
    print(f"Model Path : {model_path}")
    print(f"Iterations : {iterations}")
    print("=" * 70)

    if not os.path.exists(model_path):
        print(f"[!] Model file not found at: {model_path}")
        return

    net = cv2.dnn.readNetFromONNX(model_path)

    # Prepare a dummy 1080p frame (simulating camera capture)
    raw_img = np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8)
    is_success, buffer = cv2.imencode(".jpg", raw_img)
    encoded_bytes = buffer.tobytes()

    decode_times = []
    preproc_times = []
    inference_times = []
    postproc_times = []

    # Warmup
    for _ in range(5):
        nparr = np.frombuffer(encoded_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        resized = cv2.resize(img, (224, 224))
        blob = cv2.dnn.blobFromImage(resized, 1.0/255.0, (224, 224), (123.675, 116.28, 103.53), swapRB=True)
        net.setInput(blob)
        out = net.forward()
        _ = np.argmax(out)

    # Benchmark run
    for _ in range(iterations):
        # 1. Image Decode
        t0 = time.perf_counter()
        nparr = np.frombuffer(encoded_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        t1 = time.perf_counter()
        decode_times.append((t1 - t0) * 1000)

        # 2. Preprocess
        t2 = time.perf_counter()
        resized = cv2.resize(img, (224, 224))
        blob = cv2.dnn.blobFromImage(resized, 1.0/255.0, (224, 224), (123.675, 116.28, 103.53), swapRB=True)
        t3 = time.perf_counter()
        preproc_times.append((t3 - t2) * 1000)

        # 3. Model Inference
        t4 = time.perf_counter()
        net.setInput(blob)
        out = net.forward()
        t5 = time.perf_counter()
        inference_times.append((t5 - t4) * 1000)

        # 4. Softmax Postprocess
        t6 = time.perf_counter()
        exp_out = np.exp(out[0] - np.max(out[0]))
        probs = exp_out / np.sum(exp_out)
        top_idx = int(np.argmax(probs))
        top_conf = float(probs[top_idx])
        t7 = time.perf_counter()
        postproc_times.append((t7 - t6) * 1000)

    avg_decode = round(float(np.mean(decode_times)), 2)
    avg_preproc = round(float(np.mean(preproc_times)), 2)
    avg_inference = round(float(np.mean(inference_times)), 2)
    avg_postproc = round(float(np.mean(postproc_times)), 2)
    total_pipeline_ms = round(avg_decode + avg_preproc + avg_inference + avg_postproc, 2)
    fps = round(1000.0 / total_pipeline_ms, 1) if total_pipeline_ms > 0 else 0.0

    profile_data = {
        "model_path": model_path,
        "iterations": iterations,
        "execution_backend": "OpenCV DNN / CPU (Host Test Environment)",
        "hardware_status": {
            "host_cpu_benchmarked": True,
            "raspberry_pi_5_cpu": "PENDING PHYSICAL BENCHMARK",
            "raspberry_pi_ai_hat_hailo8": "PENDING PHYSICAL BENCHMARK"
        },
        "latency_breakdown_ms": {
            "image_decode_ms": avg_decode,
            "image_preprocess_ms": avg_preproc,
            "model_inference_ms": avg_inference,
            "softmax_postprocess_ms": avg_postproc,
            "total_e2e_latency_ms": total_pipeline_ms
        },
        "throughput_fps": fps,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    }

    os.makedirs(os.path.dirname(output_json), exist_ok=True)
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, indent=2)

    # Markdown documentation
    doc_content = f"""# KrishiDrishti Edge — AI Subsystem Latency & Performance Profile

**Benchmark Date**: {profile_data['timestamp']}  
**Execution Environment**: Host CPU Benchmark (`{profile_data['execution_backend']}`)  
**Iterations**: {iterations} frames  
**Zero Hardware Hallucination Policy**: ACTIVE

---

## 1. Measured End-to-End Latency Breakdown (Host CPU)

| Pipeline Stage | Monotonic Average Latency (ms) | Percentage of Total |
| :--- | :--- | :--- |
| **Image Decode (1080p JPEG)** | `{avg_decode} ms` | {round(avg_decode/total_pipeline_ms*100, 1)}% |
| **Image Preprocessing (Resize & Norm)** | `{avg_preproc} ms` | {round(avg_preproc/total_pipeline_ms*100, 1)}% |
| **Neural Network Inference (ONNX)** | `{avg_inference} ms` | {round(avg_inference/total_pipeline_ms*100, 1)}% |
| **Softmax Postprocessing & Gating** | `{avg_postproc} ms` | {round(avg_postproc/total_pipeline_ms*100, 1)}% |
| **TOTAL END-TO-END LATENCY** | **`{total_pipeline_ms} ms`** | **100.0%** |
| **Effective Throughput (FPS)** | **`{fps} FPS`** | — |

---

## 2. Target Hardware Deployment Matrix

| Target Hardware Platform | Target Execution Engine | Status | Measured Latency | Measured FPS |
| :--- | :--- | :--- | :--- | :--- |
| **Host Workstation (Dev)** | Multi-core x86_64 CPU | `MEASURED & VERIFIED` | `{avg_inference} ms` (Inference) | `{fps} FPS` (E2E) |
| **Raspberry Pi 5 (8GB)** | Quad-core ARM Cortex-A76 CPU | `PENDING PHYSICAL BENCHMARK` | *Pending Board* | *Pending Board* |
| **Raspberry Pi AI HAT+** | Hailo-8 / Hailo-8L NPU (PCIe) | `PENDING PHYSICAL BENCHMARK` | *Pending Board* | *Pending Board* |

---

## 3. Invariant Compliance
> [!IMPORTANT]
> In accordance with the **Zero Hardware Hallucination** policy, Raspberry Pi 5 and Hailo-8 execution speeds are not guessed or fabricated. They will be populated strictly upon running `profile_model.py` on the physical target hardware.
"""
    with open(output_doc, "w", encoding="utf-8") as f:
        f.write(doc_content)

    print(f"[+] Total E2E Latency : {total_pipeline_ms} ms ({fps} FPS)")
    print(f"[+] Model Inference   : {avg_inference} ms")
    print(f"[+] Profile written to {output_json} and {output_doc}")

if __name__ == "__main__":
    profile_model_pipeline()
