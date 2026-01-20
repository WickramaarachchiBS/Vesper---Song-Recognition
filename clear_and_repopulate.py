"""
Clear existing songs and fingerprints, then repopulate with correct artist/title parsing.
"""

import logging
from app.database import db
from app.services.populate_db import populate_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_database():
    """Clear all songs and fingerprints from database."""
    logger.info("Clearing database...")
    
    with db.get_cursor() as cursor:
        # Delete all fingerprints (will cascade if foreign key is set)
        cursor.execute("DELETE FROM fingerprints")
        fingerprints_deleted = cursor.rowcount
        
        # Delete all songs
        cursor.execute("DELETE FROM songs")
        songs_deleted = cursor.rowcount
        
        logger.info(f"Deleted {songs_deleted} songs and {fingerprints_deleted} fingerprints")


if __name__ == "__main__":
    print("=" * 60)
    print("CLEAR AND REPOPULATE DATABASE")
    print("=" * 60)
    print("\nThis will:")
    print("1. Delete all existing songs and fingerprints")
    print("2. Re-process all audio files in dataset/")
    print("3. Parse artist and title from filenames (Artist - Title format)")
    print("\n" + "=" * 60)
    
    response = input("\nAre you sure you want to continue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        # Clear database
        clear_database()
        
        # Repopulate with new parsing logic
        print("\nRepopulating database with correct artist/title parsing...")
        populate_database()
        
        print("\n" + "=" * 60)
        print("COMPLETE!")
        print("=" * 60)
    else:
        print("\nOperation cancelled.")
