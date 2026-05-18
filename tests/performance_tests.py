"""Simple performance microbenchmarks for fingerprint generation.

Generates synthetic audio and measures time to fingerprint.
"""
import sys
import os
import time
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.fingerprinting.hashing import fingerprint_audio


def run_benchmark(duration_seconds=2.0, iterations=3):
    print("== Performance Tests ==")
    sr = 44100
    samples = int(duration_seconds * sr)

    # Synthetic audio: sine wave + noise
    t = np.linspace(0, duration_seconds, samples, endpoint=False)
    audio = 0.5 * np.sin(2 * np.pi * 440 * t) + 0.02 * np.random.randn(samples)

    times = []
    for i in range(iterations):
        t0 = time.monotonic()
        fps = fingerprint_audio(audio, sr)
        t1 = time.monotonic()
        elapsed = (t1 - t0)
        times.append(elapsed)
        print(f"perf:iteration {i+1} -> {elapsed:.3f}s, fingerprints={len(fps)}")

    if times:
        avg = sum(times) / len(times)
        print(f"perf:average {avg:.3f}s over {len(times)} runs")


if __name__ == '__main__':
    run_benchmark()
