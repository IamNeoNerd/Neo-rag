import requests
import json

BASE = "http://127.0.0.1:8000"

print("=== Testing /health ===")
try:
    r = requests.get(f"{BASE}/health", timeout=5)
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

print("\n=== Testing /api/v1/config ===")
try:
    r = requests.get(f"{BASE}/api/v1/config", timeout=5)
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")

print("\n=== Testing /api/v1/config/test (neon) ===")
try:
    r = requests.post(f"{BASE}/api/v1/config/test", json={
        "type": "neon",
        "config": {"connection_string": "test"}
    }, timeout=10)
    print(f"Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
except Exception as e:
    print(f"Error: {e}")
