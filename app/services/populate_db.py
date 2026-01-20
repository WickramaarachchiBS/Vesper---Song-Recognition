"""
Offline database population script.
Processes audio files from dataset/ and stores fingerprints in database.
"""

import os
import logging
from pathlib import Path
from typing import List

from app.fingerprinting.audio_utils import load_audio, get_audio_duration
from app.fingerprinting.hashing import fingerprint_audio
from app.models.song import Song
from app.models.fingerprint import Fingerprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_audio_file(file_path: str, title: str = None, artist: str = None) -> int:
    """
    Process a single audio file and store its fingerprints.
    
    Args:
        file_path: Path to audio file
        title: Song title (defaults to parsed from filename)
        artist: Artist name (defaults to parsed from filename or "Unknown")
    
    Returns:
        song_id: ID of the created song
    """
    # Extract metadata from filename if not provided
    if title is None or artist is None:
        filename = Path(file_path).stem
        
        # Try to parse "Artist - Title" format
        if ' - ' in filename:
            parts = filename.split(' - ', 1)  # Split only on first occurrence
            parsed_artist = parts[0].strip()
            parsed_title = parts[1].strip()
            
            if artist is None:
                artist = parsed_artist
            if title is None:
                title = parsed_title
        else:
            # No separator found, use filename as title
            if title is None:
                title = filename
            if artist is None:
                artist = "Unknown"
    
    logger.info(f"Processing: {title} by {artist}")
    
    # Check if song already exists
    if Song.exists(title, artist):
        logger.warning(f"Song already exists: {title} by {artist}")
        return None
    
    # Load audio
    audio_data, sample_rate = load_audio(file_path)
    
    # Get duration
    duration = get_audio_duration(file_path)
    
    # Create song record
    song_id = Song.create(title, artist, file_path, duration)
    
    # Generate fingerprints
    fingerprints = fingerprint_audio(audio_data, sample_rate)
    
    # Prepare batch insert data
    fingerprint_records = [
        (hash_val, song_id, time_offset)
        for hash_val, time_offset in fingerprints
    ]
    
    # Insert fingerprints in batches
    batch_size = 1000
    for i in range(0, len(fingerprint_records), batch_size):
        batch = fingerprint_records[i:i + batch_size]
        Fingerprint.insert_batch(batch)
    
    logger.info(f"Stored {len(fingerprints)} fingerprints for song ID {song_id}")
    
    return song_id


def populate_database(dataset_dir: str = "dataset"):
    """
    Populate database with all audio files from dataset directory.
    
    Args:
        dataset_dir: Directory containing audio files
    """
    dataset_path = Path(dataset_dir)
    
    if not dataset_path.exists():
        logger.error(f"Dataset directory not found: {dataset_dir}")
        return
    
    # Supported audio formats
    audio_extensions = ['.wav', '.mp3', '.flac', '.ogg', '.m4a']
    
    # Find all audio files
    audio_files = []
    for ext in audio_extensions:
        audio_files.extend(dataset_path.glob(f"*{ext}"))
    
    if not audio_files:
        logger.warning(f"No audio files found in {dataset_dir}")
        return
    
    logger.info(f"Found {len(audio_files)} audio files")
    
    # Process each file
    processed = 0
    skipped = 0
    
    for audio_file in audio_files:
        try:
            result = process_audio_file(str(audio_file))
            if result:
                processed += 1
            else:
                skipped += 1
        except Exception as e:
            logger.error(f"Error processing {audio_file}: {e}")
            skipped += 1
    
    logger.info(f"Database population complete: {processed} processed, {skipped} skipped")
    
    # Print statistics
    total_songs = len(Song.get_all())
    total_fingerprints = Fingerprint.get_total_count()
    logger.info(f"Total songs in database: {total_songs}")
    logger.info(f"Total fingerprints in database: {total_fingerprints}")


if __name__ == "__main__":
    # Initialize database schema
    from app.database import db
    db.execute_schema("sql/schema.sql")
    
    # Populate database
    populate_database()
