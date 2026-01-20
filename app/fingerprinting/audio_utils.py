"""
Audio loading and preprocessing utilities.
"""

import librosa
import numpy as np
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
