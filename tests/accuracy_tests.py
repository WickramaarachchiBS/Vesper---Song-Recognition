"""Recognition accuracy smoke test.

Tries to run recognition on the first file in `dataset/` and prints the result.
If database or dataset is missing, this prints an explanatory message.
"""
import sys
import os
import traceback

# Ensure project root is on sys.path when running from tests/ directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.fingerprinting.audio_utils import load_audio
from app.services.recognize import recognize_song


def run():
    print("== Recognition Accuracy Smoke Test ==")
    dataset_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dataset')
    if not os.path.exists(dataset_dir):
        print(f"accuracy:skipped - dataset directory not found: {dataset_dir}")
        return

    audio_files = [f for f in os.listdir(dataset_dir) if f.lower().endswith(('.wav', '.mp3', '.flac'))]
    if not audio_files:
        print(f"accuracy:skipped - no audio files in {dataset_dir}")
        return

    test_file = os.path.join(dataset_dir, audio_files[0])
    print(f"accuracy:testing file {audio_files[0]}")

    try:
        audio, sr = load_audio(test_file, duration=10)
        result = recognize_song(audio, sr)
        print(f"accuracy:result -> {result}")
    except Exception:
        print("accuracy:failed to run recognition (likely DB not configured). Trace:")
        traceback.print_exc()


if __name__ == '__main__':
    run()
