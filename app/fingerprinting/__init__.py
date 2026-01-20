"""
Fingerprinting package for audio fingerprint generation.
"""

from app.fingerprinting.audio_utils import load_audio, normalize_audio, get_audio_duration
from app.fingerprinting.spectrogram import generate_spectrogram, spectrogram_to_db
from app.fingerprinting.peak_detection import detect_peaks, sort_peaks_by_time
from app.fingerprinting.hashing import generate_fingerprints, fingerprint_audio

__all__ = [
    'load_audio',
    'normalize_audio',
    'get_audio_duration',
    'generate_spectrogram',
    'spectrogram_to_db',
    'detect_peaks',
    'sort_peaks_by_time',
    'generate_fingerprints',
    'fingerprint_audio',
]
