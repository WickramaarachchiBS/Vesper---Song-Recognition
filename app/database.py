"""
Database connection management using psycopg2.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
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
        # Initialize a simple connection pool to avoid creating a new
        # TCP connection for every request. Fall back to direct
        # connections if pool creation fails.
        self.pool = None
        try:
            minconn = getattr(settings, 'DB_POOL_MIN', 1)
            maxconn = getattr(settings, 'DB_POOL_MAX', 10)
            self.pool = SimpleConnectionPool(minconn, maxconn, **self.connection_params)
            logger.info(f"Initialized DB connection pool (min={minconn}, max={maxconn})")
        except Exception as e:
            logger.warning(f"Could not initialize DB pool, falling back to direct connections: {e}")
    
    @contextmanager
    def get_connection(self) -> Generator:
        """
        Context manager for database connections.
        Automatically handles connection cleanup.
        
        Yields:
            psycopg2.connection: Database connection
        """
        conn = None
        # If a pool is available, get a connection from it
        if self.pool:
            conn = self.pool.getconn()
            try:
                yield conn
                conn.commit()
            except Exception as e:
                if conn:
                    conn.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                if conn:
                    try:
                        self.pool.putconn(conn)
                    except Exception:
                        conn.close()
        else:
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
