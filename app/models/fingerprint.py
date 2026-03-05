"""
Fingerprint database operations.
"""

from typing import List, Tuple, Dict
import logging

from psycopg2.extras import execute_values
from app.database import db

logger = logging.getLogger(__name__)


class Fingerprint:
    """Fingerprint model for database operations."""
    
    @staticmethod
    def insert_batch(fingerprints: List[Tuple[str, int, float]]):
        """
        Batch insert fingerprints for efficient database population.
        
        Args:
            fingerprints: List of (hash, song_id, time_offset) tuples
        """
        if not fingerprints:
            return
        
        with db.get_cursor() as cursor:
            # Use execute_values for fast bulk insert (single query with multiple rows)
            execute_values(
                cursor,
                """
                INSERT INTO fingerprints (hash, song_id, time_offset)
                VALUES %s
                """,
                fingerprints,
                page_size=5000
            )
            logger.info(f"Inserted {len(fingerprints)} fingerprints")
    
    @staticmethod
    def find_matches(hashes: List[str]) -> List[Dict]:
        """
        Find all fingerprints matching the given hashes.
        
        This is the core query for song recognition.
        
        Args:
            hashes: List of hash strings to search for
        
        Returns:
            List of dictionaries with keys: hash, song_id, time_offset
        """
        if not hashes:
            return []
        
        with db.get_cursor() as cursor:
            # Use IN clause for efficient batch lookup
            # Convert list to tuple for psycopg2
            cursor.execute(
                """
                SELECT hash, song_id, time_offset
                FROM fingerprints
                WHERE hash = ANY(%s)
                """,
                (hashes,)
            )
            matches = cursor.fetchall()
            logger.info(f"Found {len(matches)} fingerprint matches for {len(hashes)} hashes")
            return matches
    
    @staticmethod
    def get_count_by_song(song_id: int) -> int:
        """
        Get number of fingerprints for a song.
        
        Args:
            song_id: Song ID
        
        Returns:
            Count of fingerprints
        """
        with db.get_cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) as count FROM fingerprints WHERE song_id = %s",
                (song_id,)
            )
            result = cursor.fetchone()
            return result['count']
    
    @staticmethod
    def delete_by_song(song_id: int):
        """
        Delete all fingerprints for a song.
        
        Args:
            song_id: Song ID
        """
        with db.get_cursor() as cursor:
            cursor.execute(
                "DELETE FROM fingerprints WHERE song_id = %s",
                (song_id,)
            )
            logger.info(f"Deleted fingerprints for song ID: {song_id}")
    
    @staticmethod
    def get_total_count() -> int:
        """
        Get total number of fingerprints in database.
        
        Returns:
            Total fingerprint count
        """
        with db.get_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM fingerprints")
            result = cursor.fetchone()
            return result['count']
