"""
Fingerprint hash generation using Shazam-style combinatorial hashing.
"""

import hashlib
from typing import List, Tuple, Dict
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def generate_fingerprints(peaks: List[Tuple[int, int]]) -> List[Tuple[str, float]]:
    """
    Generate fingerprint hashes from peaks using combinatorial hashing.
    
    Shazam Algorithm:
    1. For each peak (anchor point):
       - Look ahead to find target peaks within a time window
       - Create hash from (anchor_freq, target_freq, delta_time)
       - Store hash with anchor's time offset
    
    This creates a robust fingerprint that's resistant to:
    - Time shifts (uses relative time delta)
    - Noise (uses prominent peaks only)
    - Speed changes (to some degree)
    
    Args:
        peaks: List of (freq_idx, time_idx) tuples, should be sorted by time
    
    Returns:
        List of (hash_string, time_offset) tuples
        - hash_string: SHA1 hash of the fingerprint
        - time_offset: Time offset of the anchor peak (in frames)
    """
    fingerprints = []
    
    # Sort peaks by time to ensure proper ordering
    peaks = sorted(peaks, key=lambda x: x[1])
    
    # For each peak, use it as an anchor
    for i, (anchor_freq, anchor_time) in enumerate(peaks):
        # Look ahead for target peaks
        target_count = 0
        
        for j in range(i + 1, len(peaks)):
            target_freq, target_time = peaks[j]
            
            # Calculate time difference
            delta_time = target_time - anchor_time
            
            # Check if target is within valid time window
            if delta_time < settings.MIN_TIME_DELTA:
                continue
            
            if delta_time > settings.MAX_TIME_DELTA:
                break  # No more valid targets for this anchor
            
            # Create fingerprint tuple: (anchor_freq, target_freq, delta_time)
            fingerprint_data = f"{anchor_freq}|{target_freq}|{delta_time}"
            
            # Generate SHA1 hash
            hash_object = hashlib.sha1(fingerprint_data.encode())
            hash_string = hash_object.hexdigest()
            
            # Store hash with anchor time offset
            # Convert frame index to seconds
            time_offset = anchor_time * settings.HOP_SIZE / settings.SAMPLE_RATE
            
            fingerprints.append((hash_string, time_offset))
            
            target_count += 1
            
            # Limit number of targets per anchor (fan-out value)
            if target_count >= settings.FAN_VALUE:
                break
    
    logger.info(f"Generated {len(fingerprints)} fingerprints from {len(peaks)} peaks")
    
    return fingerprints


def group_fingerprints_by_hash(
    fingerprints: List[Tuple[str, float]]
) -> Dict[str, List[float]]:
    """
    Group fingerprints by hash for efficient storage.
    
    Args:
        fingerprints: List of (hash, time_offset) tuples
    
    Returns:
        Dictionary mapping hash -> list of time offsets
    """
    grouped = {}
    
    for hash_val, time_offset in fingerprints:
        if hash_val not in grouped:
            grouped[hash_val] = []
        grouped[hash_val].append(time_offset)
    
    return grouped


def fingerprint_audio(audio_data, sample_rate: int = None) -> List[Tuple[str, float]]:
    """
    Complete fingerprinting pipeline: audio -> fingerprints.
    
    This is a convenience function that combines all steps:
    1. Generate spectrogram
    2. Detect peaks
    3. Generate fingerprint hashes
    
    Args:
        audio_data: Audio samples
        sample_rate: Sample rate (unused, kept for compatibility)
    
    Returns:
        List of (hash, time_offset) tuples
    """
    from app.fingerprinting.spectrogram import generate_spectrogram, spectrogram_to_db
    from app.fingerprinting.peak_detection import detect_peaks, sort_peaks_by_time, filter_peaks_by_frequency
    from app.fingerprinting.audio_utils import preprocess_audio
    
    # Preprocess audio (normalize + bandpass filter)
    audio_data = preprocess_audio(audio_data)
    
    # Generate spectrogram
    spectrogram, frequencies = generate_spectrogram(audio_data)
    
    # Convert to dB scale for better peak detection
    spectrogram = spectrogram_to_db(spectrogram)
    
    # Detect peaks
    peaks = detect_peaks(spectrogram)
    
    # Filter out very low and very high frequencies (focus on 300 Hz - 5000 Hz)
    # Convert Hz to frequency bin indices
    freq_resolution = settings.SAMPLE_RATE / settings.WINDOW_SIZE
    min_freq_idx = int(300 / freq_resolution)
    max_freq_idx = int(5000 / freq_resolution)
    peaks = filter_peaks_by_frequency(peaks, min_freq_idx=min_freq_idx, max_freq_idx=max_freq_idx)
    
    # Sort peaks by time
    peaks = sort_peaks_by_time(peaks)
    
    # Generate fingerprints
    fingerprints = generate_fingerprints(peaks)
    
    return fingerprints
