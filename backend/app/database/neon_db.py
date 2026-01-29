"""
Neon PostgreSQL Database Connection Module

Provides connection pooling for efficient database access. Uses psycopg2's 
ThreadedConnectionPool to manage connections across requests.

Usage:
    from backend.app.database import neon_db
    
    # Initialize pool on app startup
    neon_db.init_pool()
    
    # Get connection from pool
    conn = neon_db.get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM documents")
    finally:
        neon_db.release_connection(conn)
    
    # Or use context manager
    with neon_db.get_connection_context() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM documents")
    
    # Close pool on app shutdown
    neon_db.close_pool()
"""
import os
import logging
from contextlib import contextmanager
from typing import Optional

import psycopg2
from psycopg2 import pool
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Module-level connection pool
_connection_pool: Optional[pool.ThreadedConnectionPool] = None

# Pool configuration
MIN_CONNECTIONS = 2
MAX_CONNECTIONS = 10


def init_pool() -> bool:
    """
    Initialize the connection pool and create required tables.
    
    Should be called once during application startup.
    
    Returns:
        True if pool was initialized successfully, False otherwise.
    
    Raises:
        RuntimeError: If pool is already initialized.
    """
    global _connection_pool
    
    if _connection_pool is not None:
        logger.warning("Connection pool already initialized")
        return True
    
    database_url = os.getenv("NEON_DATABASE_URL")
    if not database_url:
        logger.error("NEON_DATABASE_URL environment variable not set")
        return False
    
    try:
        _connection_pool = pool.ThreadedConnectionPool(
            minconn=MIN_CONNECTIONS,
            maxconn=MAX_CONNECTIONS,
            dsn=database_url
        )
        logger.info(f"Neon connection pool initialized (min={MIN_CONNECTIONS}, max={MAX_CONNECTIONS})")
        
        # Initialize schema
        _initialize_schema()
        
        return True
    except psycopg2.Error as e:
        logger.error(f"Failed to initialize Neon connection pool: {e}")
        _connection_pool = None
        return False


def _initialize_schema() -> None:
    """
    Create required database tables if they don't exist.
    
    Called automatically during pool initialization.
    """
    conn = get_connection()
    if conn is None:
        return
    
    try:
        with conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id UUID PRIMARY KEY,
                    content TEXT NOT NULL,
                    embedding VECTOR(1536),
                    metadata JSONB DEFAULT '{}',
                    content_hash VARCHAR(64),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create index for deduplication
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_documents_content_hash 
                ON documents(content_hash);
            """)
            
            conn.commit()
            logger.info("Database schema initialized successfully")
    except psycopg2.Error as e:
        conn.rollback()
        logger.error(f"Failed to initialize schema: {e}")
    finally:
        release_connection(conn)


def get_connection() -> Optional[psycopg2.extensions.connection]:
    """
    Get a connection from the pool.
    
    Returns:
        A database connection, or None if pool is not initialized.
    
    Note:
        Caller is responsible for releasing the connection via release_connection().
    """
    if _connection_pool is None:
        logger.error("Connection pool not initialized. Call init_pool() first.")
        return None
    
    try:
        conn = _connection_pool.getconn()
        return conn
    except psycopg2.Error as e:
        logger.error(f"Failed to get connection from pool: {e}")
        return None


def release_connection(conn: psycopg2.extensions.connection) -> None:
    """
    Return a connection to the pool.
    
    Args:
        conn: The connection to release.
    """
    if _connection_pool is None:
        logger.warning("Connection pool not initialized, cannot release connection")
        return
    
    if conn is not None:
        try:
            _connection_pool.putconn(conn)
        except psycopg2.Error as e:
            logger.error(f"Failed to release connection: {e}")


@contextmanager
def get_connection_context():
    """
    Context manager for database connections.
    
    Automatically releases the connection when the context exits.
    
    Yields:
        A database connection.
    
    Example:
        with get_connection_context() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM documents")
    """
    conn = get_connection()
    try:
        yield conn
    finally:
        if conn is not None:
            release_connection(conn)


def close_pool() -> None:
    """
    Close all connections in the pool.
    
    Should be called during application shutdown.
    """
    global _connection_pool
    
    if _connection_pool is not None:
        try:
            _connection_pool.closeall()
            logger.info("Neon connection pool closed")
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")
        finally:
            _connection_pool = None


def get_pool_status() -> dict:
    """
    Get the current status of the connection pool.
    
    Returns:
        Dictionary with pool status information.
    """
    if _connection_pool is None:
        return {"status": "not_initialized", "connections": 0}
    
    return {
        "status": "active",
        "min_connections": MIN_CONNECTIONS,
        "max_connections": MAX_CONNECTIONS,
    }


# Backwards compatibility - keep old function but log deprecation warning
def connect_to_neon():
    """
    DEPRECATED: Use get_connection() instead.
    
    Legacy function for backwards compatibility.
    Initializes pool if needed and returns a connection.
    """
    logger.warning("connect_to_neon() is deprecated. Use get_connection() instead.")
    
    if _connection_pool is None:
        init_pool()
    
    return get_connection()


if __name__ == '__main__':
    # Test the connection pool
    logging.basicConfig(level=logging.INFO)
    
    if init_pool():
        print("Pool initialized successfully")
        
        # Test getting a connection
        with get_connection_context() as conn:
            if conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT COUNT(*) FROM documents")
                    count = cur.fetchone()[0]
                    print(f"Documents in database: {count}")
        
        print(f"Pool status: {get_pool_status()}")
        close_pool()
    else:
        print("Failed to initialize pool")
