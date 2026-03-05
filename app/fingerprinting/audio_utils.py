"""
Audio loading and preprocessing utilities.
"""

import librosa
import numpy as np
from scipy.signal import butter, sosfilt
from typing import Tuple
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def load_audio(file_path: str, offset: float = 0.0, duration: float = None) -> Tuple[np.ndarray, int]:
    """
    Load audio file and convert to mono at target sample rate.
    
    Args:
        file_path: Path to audio file (WAV, MP3, etc.)
        offset: Start reading after this time (in seconds)
        duration: Only load up to this duration (in seconds)
    
    Returns:
        Tuple of (audio_data, sample_rate)
        - audio_data: 1D numpy array of audio samples
        - sample_rate: Sample rate (should match settings.SAMPLE_RATE)
    """
    try:
        # Load audio file with librosa
        # sr=settings.SAMPLE_RATE resamples to target rate
        # mono=True converts to mono
        audio_data, sample_rate = librosa.load(
            file_path,
            sr=settings.SAMPLE_RATE,
            mono=True,
            offset=offset,
            duration=duration
        )
        
        logger.info(f"Loaded audio: {file_path}, duration: {len(audio_data)/sample_rate:.2f}s")
        return audio_data, sample_rate
    
    except Exception as e:
        logger.error(f"Error loading audio file {file_path}: {e}")
        raise


def normalize_audio(audio_data: np.ndarray) -> np.ndarray:
    """
    Normalize audio to [-1, 1] range.
    
    Args:
        audio_data: Input audio samples
    
    Returns:
        Normalized audio samples
    """
    max_val = np.max(np.abs(audio_data))
    if max_val > 0:
        return audio_data / max_val
    return audio_data


def bandpass_filter(audio_data: np.ndarray, low_freq: float = 200.0, high_freq: float = 6000.0) -> np.ndarray:
    """
    Apply a bandpass filter to focus on the most musically relevant frequency range.
    Removes rumble below low_freq and hiss above high_freq.
    
    Args:
        audio_data: Input audio samples
        low_freq: Low cutoff frequency in Hz
        high_freq: High cutoff frequency in Hz
    
    Returns:
        Filtered audio samples
    """
    nyquist = settings.SAMPLE_RATE / 2
    low = low_freq / nyquist
    high = high_freq / nyquist
    sos = butter(4, [low, high], btype='band', output='sos')
    return sosfilt(sos, audio_data).astype(np.float32)


def preprocess_audio(audio_data: np.ndarray) -> np.ndarray:
    """
    Full preprocessing pipeline: normalize and bandpass filter.
    
    Args:
        audio_data: Raw audio samples
    
    Returns:
        Preprocessed audio samples
    """
    audio_data = normalize_audio(audio_data)
    audio_data = bandpass_filter(audio_data)
    return audio_data


def get_audio_duration(file_path: str) -> float:
    """
    Get duration of audio file in seconds.
    
    Args:
        file_path: Path to audio file
    
    Returns:
        Duration in seconds
    """
    try:
        duration = librosa.get_duration(path=file_path)
        return duration
    except Exception as e:
        logger.error(f"Error getting duration for {file_path}: {e}")
        raise
