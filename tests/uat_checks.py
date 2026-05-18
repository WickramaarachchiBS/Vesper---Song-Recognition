"""User Acceptance Test (UAT) checklist runner.

Prints manual steps that a tester can follow and performs a couple of lightweight checks.
"""
import sys
import os
try:
    from fastapi.testclient import TestClient
except Exception:
    TestClient = None

# Ensure project root is importable when running from tests/ directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app


def print_checklist():
    print("== UAT Checklist ==")
    items = [
        "1. Populate the database with sample songs (see docs/).",
        "2. Start the API: `uvicorn app.main:app --reload`",
        "3. POST an audio file to /api/identify to verify recognition.",
        "4. Use /api/identify-peaks to test lightweight client uploads.",
        "5. Verify logs show DB queries and recognition timings."
    ]
    for it in items:
        print(it)


def smoke_api_check():
    print("== UAT: smoke API check ==")
    if TestClient is None:
        print("uat:health -> skipped (httpx/fastapi testclient not installed)")
        return
    client = TestClient(app)
    r = client.get("/api/health")
    print(f"uat:health -> status {r.status_code}, body={r.json()}")


def run():
    print_checklist()
    try:
        smoke_api_check()
    except Exception as e:
        print("uat:smoke_api_check failed:", e)


if __name__ == '__main__':
    run()
