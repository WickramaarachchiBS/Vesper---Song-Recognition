"""
Alternative version of populate_db.py that can fetch songs from cloud storage.
Modify the download_from_cloud() function to work with your cloud storage provider.
"""

import os
import logging
from pathlib import Path
import tempfile
from typing import List

from app.fingerprinting.audio_utils import load_audio, get_audio_duration
from app.fingerprinting.hashing import fingerprint_audio
from app.models.song import Song
from app.models.fingerprint import Fingerprint

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_from_cloud(cloud_url: str, local_path: str) -> bool:
    """
    Download audio file from cloud storage.
    
    MODIFY THIS FUNCTION for your cloud storage provider:
    - AWS S3: Use boto3
    - Google Cloud Storage: Use google-cloud-storage
    - Azure Blob Storage: Use azure-storage-blob
    - HTTP URL: Use requests
    
    Args:
        cloud_url: URL or path to cloud file
        local_path: Where to save the file locally
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Example for HTTP/HTTPS URLs:
        import requests
        response = requests.get(cloud_url, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded: {cloud_url}")
        return True
    
    except Exception as e:
        logger.error(f"Failed to download {cloud_url}: {e}")
        return False


def process_cloud_audio(cloud_url: str, title: str = None, artist: str = None) -> int:
    """
    Download audio from cloud, process it, and store fingerprints.
    
    Args:
        cloud_url: URL to cloud-stored audio file
        title: Song title
        artist: Artist name
    
    Returns:
        song_id or None if failed
    """
    # Create temporary file
    temp_dir = tempfile.gettempdir()
    filename = os.path.basename(cloud_url)
    temp_path = os.path.join(temp_dir, filename)
    
    try:
        # Download from cloud
        if not download_from_cloud(cloud_url, temp_path):
            return None
        
        # Extract metadata from filename if not provided
        if title is None:
            title = Path(filename).stem
        
        if artist is None:
            artist = "Unknown"
        
        logger.info(f"Processing: {title} by {artist}")
        
        # Check if song already exists
        if Song.exists(title, artist):
            logger.warning(f"Song already exists: {title} by {artist}")
            return None
        
        # Load audio
        audio_data, sample_rate = load_audio(temp_path)
        
        # Get duration
        duration = get_audio_duration(temp_path)
        
        # Create song record (store cloud URL as file_path)
        song_id = Song.create(title, artist, cloud_url, duration)
        
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
    
    except Exception as e:
        logger.error(f"Error processing {cloud_url}: {e}")
        return None
    
    finally:
        # Clean up temporary file
        if os.path.exists(temp_path):
            os.unlink(temp_path)


def populate_from_cloud_list(song_list: List[dict]):
    """
    Populate database from a list of cloud-stored songs.
    
    Args:
        song_list: List of dictionaries with keys: url, title, artist
        
    Example:
        song_list = [
            {
                "url": "https://storage.example.com/songs/song1.mp3",
                "title": "Song Title",
                "artist": "Artist Name"
            },
            ...
        ]
    """
    logger.info(f"Processing {len(song_list)} songs from cloud storage")
    
    processed = 0
    skipped = 0
    
    for song_info in song_list:
        try:
            result = process_cloud_audio(
                cloud_url=song_info['url'],
                title=song_info.get('title'),
                artist=song_info.get('artist')
            )
            
            if result:
                processed += 1
            else:
                skipped += 1
        
        except Exception as e:
            logger.error(f"Error processing {song_info.get('url', 'unknown')}: {e}")
            skipped += 1
    
    logger.info(f"Cloud population complete: {processed} processed, {skipped} skipped")
    
    # Print statistics
    total_songs = len(Song.get_all())
    total_fingerprints = Fingerprint.get_total_count()
    logger.info(f"Total songs in database: {total_songs}")
    logger.info(f"Total fingerprints in database: {total_fingerprints}")


if __name__ == "__main__":
    # Example usage with cloud URLs
    song_list = [
        {
            "url": "https://example.com/path/to/song1.mp3",
            "title": "Song 1",
            "artist": "Artist 1"
        },
        {
            "url": "https://example.com/path/to/song2.mp3",
            "title": "Song 2",
            "artist": "Artist 2"
        },
    ]
    
    # Initialize database schema
    from app.database import db
    db.execute_schema("sql/schema.sql")
    
    # Populate from cloud
    populate_from_cloud_list(song_list)
