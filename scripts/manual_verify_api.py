import json
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge\backend")
sys.path.insert(0, r"C:\Users\Admin\.gemini\antigravity\scratch\krishidrishti-edge")

from app.main import app
from app.core.config import settings

client = TestClient(app)

print("=== MANUAL API VERIFICATION: DEMO_MODE=True ===")
settings.DEMO_MODE = True

for path in ["/api/health", "/api/device/status", "/api/device/capabilities", "/api/camera/status", "/api/soil/status", "/api/ai/status"]:
    res = client.get(path)
    print(f"[{res.status_code}] {path}")
    print(json.dumps(res.json(), indent=2)[:200] + "...\n")

print("=== MANUAL API VERIFICATION: DEMO_MODE=False (REAL HARDWARE MODE) ===")
settings.DEMO_MODE = False

for path in ["/api/health", "/api/device/status", "/api/device/capabilities", "/api/camera/status", "/api/soil/status", "/api/ai/status"]:
    res = client.get(path)
    print(f"[{res.status_code}] {path}")
    print(json.dumps(res.json(), indent=2)[:200] + "...\n")
