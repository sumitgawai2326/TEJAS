"""
KrishiDrishti Edge — ML Training Environment Hardware & Dependency Diagnostic
Zero AI Hallucination: Truthfully reports hardware and software capabilities without fabricating CUDA or accelerator support.
"""
import sys
import os
import platform
import shutil
import psutil

def check_env():
    print("=" * 70)
    print("KrishiDrishti Edge — ML Training Environment Diagnostic")
    print("Zero Hardware / AI Hallucination Policy: ACTIVE")
    print("=" * 70)

    # 1. System Platform
    print("\n[1] HOST SYSTEM & CPU:")
    print(f"  - OS / Platform    : {platform.system()} {platform.release()} ({platform.machine()})")
    print(f"  - Processor / CPU  : {platform.processor() or 'Standard Architecture'}")
    print(f"  - Logical Cores    : {os.cpu_count()}")
    ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    ram_avail_gb = round(psutil.virtual_memory().available / (1024 ** 3), 2)
    print(f"  - Physical RAM     : {ram_gb} GB Total ({ram_avail_gb} GB Available)")

    # Storage
    total_disk, used_disk, free_disk = shutil.disk_usage(".")
    print(f"  - Disk Storage     : {round(free_disk / (1024**3), 2)} GB Free / {round(total_disk / (1024**3), 2)} GB Total")

    # 2. Python Environment
    print("\n[2] PYTHON RUNTIME:")
    print(f"  - Python Version   : {sys.version.split()[0]} ({sys.executable})")

    # 3. PyTorch & Acceleration
    print("\n[3] PYTORCH & COMPUTE BACKEND:")
    try:
        import torch
        print(f"  - PyTorch Version  : {torch.__version__}")
        cuda_avail = torch.cuda.is_available()
        print(f"  - CUDA Available   : {cuda_avail}")
        if cuda_avail:
            print(f"  - CUDA Device Name : {torch.cuda.get_device_name(0)}")
            print(f"  - CUDA Device Count: {torch.cuda.device_count()}")
        else:
            print("  - Hardware Compute : CPU Execution Provider (No physical NVIDIA GPU detected)")
    except ImportError:
        print("  - PyTorch          : NOT INSTALLED")

    # 4. Ultralytics & Vision Libraries
    print("\n[4] ML & COMPUTER VISION LIBRARIES:")
    for pkg in ["torchvision", "ultralytics", "onnx", "onnxruntime", "cv2", "PIL", "sklearn", "matplotlib", "pandas", "yaml"]:
        try:
            if pkg == "cv2":
                import cv2
                print(f"  - opencv-python    : {cv2.__version__}")
            elif pkg == "PIL":
                import PIL
                print(f"  - Pillow           : {PIL.__version__}")
            elif pkg == "sklearn":
                import sklearn
                print(f"  - scikit-learn     : {sklearn.__version__}")
            elif pkg == "yaml":
                import yaml
                print(f"  - PyYAML           : {yaml.__version__}")
            else:
                mod = __import__(pkg)
                ver = getattr(mod, "__version__", "Available")
                print(f"  - {pkg:<16} : {ver}")
        except ImportError:
            print(f"  - {pkg:<16} : NOT INSTALLED")

    print("\n" + "=" * 70)
    print("DIAGNOSTIC STATUS: COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    check_env()
