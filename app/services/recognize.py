"""
Song recognition service using time-offset alignment.
"""

import logging
from typing import Optional, Dict, List, Tuple
from collections import defaultdict

from app.fingerprinting.hashing import fingerprint_audio, fingerprints_from_peak_points
from app.models.fingerprint import Fingerprint
from app.models.song import Song
from app.config import settings
import time

logger = logging.getLogger(__name__)


def _recognize_from_fingerprints(query_fingerprints: List[Tuple[str, float]]) -> Optional[Dict]:
    """
    Match precomputed query fingerprints against the database.

    Args:
        query_fingerprints: List of (hash, time_offset_seconds) tuples.

    Returns:
        Recognition result dictionary or None if no match.
    """
    if not query_fingerprints:
        logger.warning("No query fingerprints provided")
        return None

    logger.info(f"Generated {len(query_fingerprints)} query fingerprints")

    # Extract hashes
    query_hashes = [hash_val for hash_val, _ in query_fingerprints]

    # Find matching fingerprints in database
    t_db_start = time.monotonic()
    db_matches = Fingerprint.find_matches(query_hashes)
    t_db_end = time.monotonic()
    logger.info(f"DB fingerprint query took {(t_db_end - t_db_start)*1000:.1f}ms")

    if not db_matches:
        logger.info("No matching fingerprints found in database")
        return None

    logger.info(f"Found {len(db_matches)} database matches")

    # Create lookup for query fingerprint offsets
    # Use list to handle duplicate hashes (same hash can appear at multiple times)
    query_offset_map = defaultdict(list)
    for hash_val, offset in query_fingerprints:
        query_offset_map[hash_val].append(offset)

    # Group matches by song and calculate offset differences
    # Structure: song_id -> list of offset_diffs
    song_offset_diffs = defaultdict(list)
    # Also collect song metadata returned from the DB join
    song_meta = {}

    for match in db_matches:
        hash_val = match['hash']
        song_id = match['song_id']
        db_offset = match['time_offset']
        # store metadata if present
        if 'title' in match and match.get('title'):
            song_meta[song_id] = {
                'title': match.get('title'),
                'artist': match.get('artist')
            }

        # Check all query offsets for this hash (handles duplicate hashes)
        for query_offset in query_offset_map.get(hash_val, []):
            # Calculate offset difference
            offset_diff = db_offset - query_offset
            song_offset_diffs[song_id].append(offset_diff)

    # For each song, find the most common offset difference
    song_scores = []
    t_match_start = time.monotonic()

    for song_id, offset_diffs in song_offset_diffs.items():
        # Create histogram of offset differences
        # Bin to nearest 0.5 second for robustness against timing jitter
        offset_histogram = defaultdict(int)

        for offset_diff in offset_diffs:
            # Bin to 0.5-second intervals
            binned_offset = round(offset_diff * 2) / 2
            offset_histogram[binned_offset] += 1

        # Find the peak (most common offset)
        max_count = max(offset_histogram.values())

        # Only consider songs with sufficient matches
        if max_count >= settings.MIN_MATCH_COUNT:
            song_scores.append({
                'song_id': song_id,
                'match_count': max_count,
                'total_matches': len(offset_diffs)
            })

    t_match_end = time.monotonic()
    logger.info(f"Offset matching took {(t_match_end - t_match_start)*1000:.1f}ms")

    if not song_scores:
        logger.info("No songs met minimum match threshold")
        return None

    # Sort by match count (descending)
    song_scores.sort(key=lambda x: x['match_count'], reverse=True)

    # Get best match
    best_match = song_scores[0]
    song_id = best_match['song_id']

    # Get song metadata (from DB join results if available)
    song = song_meta.get(song_id) or Song.get_by_id(song_id)

    if not song:
        logger.error(f"Song ID {song_id} not found in database")
        return None

    # Calculate confidence score
    # Primary: ratio of aligned matches to query fingerprints
    raw_confidence = (best_match['match_count'] / len(query_fingerprints)) * 100

    # Boost confidence if there's a clear gap between best and second-best match
    if len(song_scores) >= 2:
        second_best = song_scores[1]['match_count']
        if second_best > 0:
            separation = best_match['match_count'] / second_best
            # Scale: separation of 2x+ gives full confidence, 1x gives half
            confidence = raw_confidence * min(separation / 2, 1.0)
        else:
            confidence = raw_confidence
    else:
        confidence = raw_confidence

    # Apply confidence threshold to reduce false positives
    match_ratio = best_match['match_count'] / len(query_fingerprints)
    second_best = song_scores[1]['match_count'] if len(song_scores) >= 2 else 0
    separation = (best_match['match_count'] / second_best) if second_best > 0 else float('inf')
    
    if len(query_fingerprints) < settings.MIN_QUERY_FINGERPRINTS:
        logger.info(f"Recognition rejected: insufficient fingerprints (got {len(query_fingerprints)}, need {settings.MIN_QUERY_FINGERPRINTS})")
        return None
    
    if match_ratio < settings.CONFIDENCE_THRESHOLD:
        logger.info(f"Recognition rejected: low match ratio {match_ratio:.2f} < {settings.CONFIDENCE_THRESHOLD}")
        return None
    
    if separation < settings.MIN_SEPARATION_RATIO:
        logger.info(f"Recognition rejected: ambiguous (separation={separation:.2f} < {settings.MIN_SEPARATION_RATIO})")
        return None

    result = {
        'song_id': song_id,
        'title': song['title'],
        'artist': song['artist'],
        'match_count': best_match['match_count'],
        'confidence': round(confidence, 2),
        'total_fingerprints': len(query_fingerprints)
    }

    logger.info(f"Recognition result: {result['title']} by {result['artist']} "
                f"(confidence: {result['confidence']}%)")

    return result


def recognize_song_from_fingerprints(
    query_fingerprints: List[Tuple[str, float]]
) -> Optional[Dict]:
    """
    Recognize a song using precomputed fingerprints.

    Args:
        query_fingerprints: List of (hash, time_offset_seconds) tuples.

    Returns:
        Recognition result dictionary or None if no match.
    """
    logger.info("Starting song recognition from fingerprints...")
    return _recognize_from_fingerprints(query_fingerprints)


def recognize_song_from_peaks(peaks: List[Tuple[int, int]]) -> Optional[Dict]:
    """
    Recognize a song from peak points provided by a client.

    Args:
        peaks: List of (freq_idx, time_idx) tuples.

    Returns:
        Recognition result dictionary or None if no match.
    """
    logger.info("Starting song recognition from peak points...")
    query_fingerprints = fingerprints_from_peak_points(peaks)

    if not query_fingerprints:
        logger.warning("No fingerprints generated from peak points")
        return None

    return _recognize_from_fingerprints(query_fingerprints)


def recognize_song(audio_data, sample_rate: int = None) -> Optional[Dict]:
    """
    Recognize a song from audio data using fingerprint matching.
    
    Algorithm:
    1. Generate fingerprints from query audio
    2. Find matching fingerprints in database
    3. Group matches by song
    4. For each song, perform time-offset alignment
    5. Return song with highest match count and confidence
    
    Time-offset alignment:
    - For each match: calculate offset_diff = db_offset - query_offset
    - Matches from the same song should have similar offset_diff
    - Count matches with same offset_diff (histogram)
    - The peak in the histogram indicates the best alignment
    
    Args:
        audio_data: Query audio samples
        sample_rate: Sample rate (unused, kept for compatibility)
    
    Returns:
        Dictionary with recognition results:
        {
            'song_id': int,
            'title': str,
            'artist': str,
            'match_count': int,
            'confidence': float,
            'total_fingerprints': int
        }
        Returns None if no match found
    """
    logger.info("Starting song recognition...")
    
    # Generate fingerprints from query audio
    query_fingerprints = fingerprint_audio(audio_data, sample_rate)
    
    if not query_fingerprints:
        logger.warning("No fingerprints generated from query audio")
        return None

    return _recognize_from_fingerprints(query_fingerprints)
