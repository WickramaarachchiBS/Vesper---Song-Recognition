"""
Song database operations.
"""

from typing import Optional, List, Dict
import logging

from app.database import db

logger = logging.getLogger(__name__)


class Song:
    """Song model for database operations."""
    
    @staticmethod
    def create(title: str, artist: str, file_path: str, duration_seconds: float = None) -> int:
        """
        Insert a new song into the database.
        
        Args:
            title: Song title
            artist: Artist name
            file_path: Path to audio file
            duration_seconds: Duration in seconds
        
        Returns:
            song_id: ID of the inserted song
        """
        with db.get_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO songs (title, artist, file_path, duration_seconds)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (title, artist, file_path, duration_seconds)
            )
            song_id = cursor.fetchone()['id']
            logger.info(f"Created song: {title} by {artist} (ID: {song_id})")
            return song_id
    
    @staticmethod
    def get_by_id(song_id: int) -> Optional[Dict]:
        """
        Get song by ID.
        
        Args:
            song_id: Song ID
        
        Returns:
            Dictionary with song data or None if not found
        """
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM songs WHERE id = %s",
                (song_id,)
            )
            return cursor.fetchone()
    
    @staticmethod
    def get_all() -> List[Dict]:
        """
        Get all songs from database.
        
        Returns:
            List of song dictionaries
        """
        with db.get_cursor() as cursor:
            cursor.execute("SELECT * FROM songs ORDER BY id")
            return cursor.fetchall()
    
    @staticmethod
    def delete(song_id: int):
        """
        Delete a song (and its fingerprints via CASCADE).
        
        Args:
            song_id: Song ID to delete
        """
        with db.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM songs WHERE id = %s",
                (song_id,)
            )
            logger.info(f"Deleted song ID: {song_id}")
    
    @staticmethod
    def exists(title: str, artist: str) -> bool:
        """
        Check if a song already exists.
        
        Args:
            title: Song title
            artist: Artist name
        
        Returns:
            True if song exists, False otherwise
        """
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM songs WHERE title = %s AND artist = %s",
                (title, artist)
            )
            result = cursor.fetchone()
            return result['count'] > 0
