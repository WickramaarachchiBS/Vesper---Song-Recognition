"""
Database connection management using psycopg2.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Generator
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """PostgreSQL database connection manager."""
    
    def __init__(self):
        self.connection_params = {
            'host': settings.DB_HOST,
            'port': settings.DB_PORT,
            'database': settings.DB_NAME,
            'user': settings.DB_USER,
            'password': settings.DB_PASSWORD,
            'sslmode': settings.DB_SSLMODE
        }
    
    @contextmanager
    def get_connection(self) -> Generator:
        """
        Context manager for database connections.
        Automatically handles connection cleanup.
        
        Yields:
            psycopg2.connection: Database connection
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.connection_params)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, cursor_factory=RealDictCursor) -> Generator:
        """
        Context manager for database cursors.
        
        Args:
            cursor_factory: Cursor factory class (default: RealDictCursor)
        
        Yields:
            psycopg2.cursor: Database cursor
        """
        with self.get_connection() as conn:
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def execute_schema(self, schema_file: str):
        """
        Execute SQL schema file to initialize database.
        
        Args:
            schema_file: Path to SQL schema file
        """
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        with self.get_cursor() as cursor:
            cursor.execute(schema_sql)
        
        logger.info("Database schema initialized successfully")


# Global database instance
db = Database()
