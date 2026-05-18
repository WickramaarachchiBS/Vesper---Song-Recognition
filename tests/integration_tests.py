"""Integration tests using FastAPI TestClient for API endpoints.

These tests call the `/api/health` and `/api/identify-peaks` endpoints
with synthetic data and print results.
"""
import sys
import os
import json
try:
    from fastapi.testclient import TestClient
except Exception:
    TestClient = None

# Ensure project root is importable when running from tests/ directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app


def test_health():
    if TestClient is None:
        print("integration:test_health -> skipped (httpx/fastapi testclient not installed)")
        return
    client = TestClient(app)
    r = client.get("/health")
    print(f"integration:test_health -> status {r.status_code}, body={r.json()}")


def test_identify_peaks():
    if TestClient is None:
        print("integration:test_identify_peaks -> skipped (httpx/fastapi testclient not installed)")
        return
    client = TestClient(app)

    # Synthetic peaks: small list that will generate fingerprints
    payload = {
        "schema_version": "1.0",
        "clip_duration_seconds": 5.0,
        "sample_rate_hz": 44100,
        "hop_size": 512,
        "window_size": 1024,
        "peaks": [
            {"freq_idx": 10, "time_idx": 0},
            {"freq_idx": 20, "time_idx": 2},
            {"freq_idx": 30, "time_idx": 4}
        ]
    }

    r = client.post("/api/identify-peaks", json=payload)
    try:
        body = r.json()
    except Exception:
        body = r.text

    print(f"integration:test_identify_peaks -> status {r.status_code}, body={body}")


def run():
    print("== Integration Tests ==")
    try:
        test_health()
    except Exception as e:
        print("integration:test_health ✗", e)

    try:
        test_identify_peaks()
    except Exception as e:
        print("integration:test_identify_peaks ✗", e)


if __name__ == '__main__':
    run()
