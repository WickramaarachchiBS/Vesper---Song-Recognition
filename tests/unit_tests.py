"""Simple unit tests for core fingerprinting utilities.

These are not pytest tests; they print pass/fail so they can be run
with plain `python` and produce terminal output for evidence.
"""
import sys
import os
import numpy as np

# Ensure project root is on sys.path when running from tests/ directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.fingerprinting.audio_utils import normalize_audio, preprocess_audio
from app.fingerprinting.hashing import generate_fingerprints


def test_normalize_audio():
    a = np.array([0.0, 0.5, -0.25, 1.0], dtype=float)
    normalized = normalize_audio(a)
    assert np.max(np.abs(normalized)) == 1.0
    print("unit:test_normalize_audio ✓")


def test_generate_fingerprints_simple():
    # simple peak list: (freq_idx, time_idx)
    peaks = [(10, 0), (20, 2), (30, 4)]
    fps = generate_fingerprints(peaks)
    assert isinstance(fps, list)
    print(f"unit:test_generate_fingerprints_simple ✓ (generated {len(fps)} hashes)")


def run():
    print("== Unit Tests ==")
    try:
        test_normalize_audio()
    except AssertionError as e:
        print("unit:test_normalize_audio ✗", e)

    try:
        test_generate_fingerprints_simple()
    except AssertionError as e:
        print("unit:test_generate_fingerprints_simple ✗", e)


if __name__ == '__main__':
    run()
