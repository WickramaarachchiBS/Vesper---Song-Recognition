"""
Peak detection for identifying prominent frequency points in spectrogram.
"""

import numpy as np
from scipy.ndimage import maximum_filter
from typing import List, Tuple
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def detect_peaks(spectrogram: np.ndarray) -> List[Tuple[int, int]]:
    """
    Detect local maxima (peaks) in the spectrogram.
    
    Peaks represent prominent frequency-time points that are used as
    anchor and target points for fingerprint generation.
    
    Algorithm:
    1. Apply maximum filter to find local maxima
    2. Compare original with filtered version
    3. Apply amplitude threshold to filter weak peaks
    
    Args:
        spectrogram: 2D magnitude spectrogram (freq_bins x time_frames)
    
    Returns:
        List of (frequency_idx, time_idx) tuples representing peak locations
    """
    # Apply maximum filter to find local maxima
    # This creates a new array where each point is the maximum in its neighborhood
    neighborhood_size = settings.PEAK_NEIGHBORHOOD_SIZE
    local_max = maximum_filter(spectrogram, size=neighborhood_size)
    
    # A peak is where the original value equals the local maximum
    # (i.e., it's the highest point in its neighborhood)
    peaks = (spectrogram == local_max)
    
    # Apply amplitude threshold to filter out weak peaks
    # This reduces noise and focuses on prominent features
    threshold_mask = (spectrogram > settings.MIN_AMPLITUDE)
    peaks = peaks & threshold_mask
    
    # Get coordinates of peaks
    peak_coords = np.argwhere(peaks)
    
    # Convert to list of (freq_idx, time_idx) tuples
    peak_list = [(int(freq), int(time)) for freq, time in peak_coords]
    
    logger.info(f"Detected {len(peak_list)} peaks")
    
    return peak_list


def filter_peaks_by_frequency(
    peaks: List[Tuple[int, int]], 
    min_freq_idx: int = 0, 
    max_freq_idx: int = None
) -> List[Tuple[int, int]]:
    """
    Filter peaks to only include those within a frequency range.
    
    This can be useful to focus on specific frequency bands
    (e.g., excluding very low or very high frequencies).
    
    Args:
        peaks: List of (freq_idx, time_idx) tuples
        min_freq_idx: Minimum frequency index (inclusive)
        max_freq_idx: Maximum frequency index (exclusive), None for no limit
    
    Returns:
        Filtered list of peaks
    """
    if max_freq_idx is None:
        max_freq_idx = float('inf')
    
    filtered = [
        (freq, time) for freq, time in peaks
        if min_freq_idx <= freq < max_freq_idx
    ]
    
    logger.info(f"Filtered peaks: {len(peaks)} -> {len(filtered)}")
    
    return filtered


def sort_peaks_by_time(peaks: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """
    Sort peaks by time index (useful for fingerprint generation).
    
    Args:
        peaks: List of (freq_idx, time_idx) tuples
    
    Returns:
        Sorted list of peaks
    """
    return sorted(peaks, key=lambda x: x[1])
