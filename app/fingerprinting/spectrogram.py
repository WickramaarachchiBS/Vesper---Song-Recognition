"""
Spectrogram generation using Short-Time Fourier Transform (STFT).
"""

import librosa
import numpy as np
from typing import Tuple
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def generate_spectrogram(audio_data: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate magnitude spectrogram using STFT.
    
    The spectrogram represents the frequency content of the audio over time.
    Each column represents a time frame, each row represents a frequency bin.
    
    Args:
        audio_data: 1D array of audio samples
    
    Returns:
        Tuple of (spectrogram, frequencies)
        - spectrogram: 2D array (freq_bins x time_frames) of magnitude values
        - frequencies: 1D array of frequency values for each bin
    """
    # Compute Short-Time Fourier Transform
    # n_fft: FFT window size (frequency resolution)
    # hop_length: number of samples between successive frames (time resolution)
    stft_matrix = librosa.stft(
        audio_data,
        n_fft=settings.WINDOW_SIZE,
        hop_length=settings.HOP_SIZE
    )
    
    # Convert complex STFT to magnitude spectrogram
    spectrogram = np.abs(stft_matrix)
    
    # Get frequency bins
    frequencies = librosa.fft_frequencies(
        sr=settings.SAMPLE_RATE,
        n_fft=settings.WINDOW_SIZE
    )
    
    logger.info(f"Generated spectrogram: shape={spectrogram.shape}")
    
    return spectrogram, frequencies


def spectrogram_to_db(spectrogram: np.ndarray) -> np.ndarray:
    """
    Convert magnitude spectrogram to decibel scale.
    
    Decibel scale is more perceptually relevant and helps with peak detection.
    
    Args:
        spectrogram: Magnitude spectrogram
    
    Returns:
        Spectrogram in decibel scale
    """
    # Convert to dB scale (logarithmic)
    # ref=np.max sets the maximum value as 0 dB reference
    db_spectrogram = librosa.amplitude_to_db(spectrogram, ref=np.max)
    
    return db_spectrogram


def get_time_frames(audio_length: int) -> np.ndarray:
    """
    Get time values for each frame in the spectrogram.
    
    Args:
        audio_length: Length of audio signal in samples
    
    Returns:
        1D array of time values (in seconds) for each frame
    """
    frames = librosa.frames_to_time(
        np.arange(audio_length // settings.HOP_SIZE + 1),
        sr=settings.SAMPLE_RATE,
        hop_length=settings.HOP_SIZE
    )
    
    return frames
