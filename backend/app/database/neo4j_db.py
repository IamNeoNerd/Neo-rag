"""
Neo4j Database Connection Module

Provides a singleton driver pattern for Neo4j connections. The Neo4j Python driver
already handles connection pooling internally, so we just need to manage the driver
lifecycle properly.

Usage:
    from backend.app.database import neo4j_db
    
    # Initialize driver on app startup
    neo4j_db.init_driver()
    
    # Get the driver for operations
    driver = neo4j_db.get_driver()
    with driver.session() as session:
        result = session.run("MATCH (n) RETURN n LIMIT 10")
    
    # Close driver on app shutdown
    neo4j_db.close_driver()
"""
import os
import logging
from typing import Optional

from neo4j import GraphDatabase, Driver
from neo4j.exceptions import ServiceUnavailable, AuthError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Module-level driver instance (singleton)
_driver: Optional[Driver] = None

# Connection pool settings (built into Neo4j driver)
MAX_CONNECTION_POOL_SIZE = 50
CONNECTION_ACQUISITION_TIMEOUT = 60  # seconds


def init_driver() -> bool:
    """
    Initialize the Neo4j driver and verify connectivity.
    
    Should be called once during application startup.
    
    Returns:
        True if driver was initialized successfully, False otherwise.
    """
    global _driver
    
    if _driver is not None:
        logger.warning("Neo4j driver already initialized")
        return True
    
    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME")
    password = os.getenv("NEO4J_PASSWORD")
    
    if not all([uri, username, password]):
        logger.error("Missing Neo4j credentials. Check NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")
        return False
    
    try:
        _driver = GraphDatabase.driver(
            uri,
            auth=(username, password),
            max_connection_pool_size=MAX_CONNECTION_POOL_SIZE,
            connection_acquisition_timeout=CONNECTION_ACQUISITION_TIMEOUT
        )
        
        # Verify connectivity
        _driver.verify_connectivity()
        
        logger.info(f"Neo4j driver initialized (pool_size={MAX_CONNECTION_POOL_SIZE})")
        return True
        
    except AuthError as e:
        logger.error(f"Neo4j authentication failed: {e}")
        _driver = None
        return False
    except ServiceUnavailable as e:
        logger.error(f"Neo4j service unavailable: {e}")
        _driver = None
        return False
    except Exception as e:
        logger.error(f"Failed to initialize Neo4j driver: {e}")
        _driver = None
        return False


def get_driver() -> Optional[Driver]:
    """
    Get the Neo4j driver instance.
    
    Returns:
        The Neo4j driver, or None if not initialized.
    
    Note:
        The driver manages its own connection pool internally.
        Use driver.session() to get a session for operations.
    """
    if _driver is None:
        logger.error("Neo4j driver not initialized. Call init_driver() first.")
        return None
    
    return _driver


def get_session():
    """
    Get a new Neo4j session.
    
    Returns:
        A Neo4j session, or None if driver is not initialized.
    
    Note:
        Caller is responsible for closing the session.
        Prefer using 'with driver.session() as session:' pattern.
    """
    driver = get_driver()
    if driver is None:
        return None
    
    return driver.session()


def close_driver() -> None:
    """
    Close the Neo4j driver and release all connections.
    
    Should be called during application shutdown.
    """
    global _driver
    
    if _driver is not None:
        try:
            _driver.close()
            logger.info("Neo4j driver closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j driver: {e}")
        finally:
            _driver = None


def get_driver_status() -> dict:
    """
    Get the current status of the Neo4j driver.
    
    Returns:
        Dictionary with driver status information.
    """
    if _driver is None:
        return {"status": "not_initialized"}
    
    try:
        # Verify connectivity is still valid
        _driver.verify_connectivity()
        return {
            "status": "connected",
            "max_pool_size": MAX_CONNECTION_POOL_SIZE,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }


def execute_query(cypher: str, parameters: dict = None) -> list:
    """
    Execute a Cypher query and return results.
    
    A convenience function for simple queries.
    
    Args:
        cypher: The Cypher query to execute.
        parameters: Optional query parameters.
    
    Returns:
        List of records from the query result.
    
    Raises:
        RuntimeError: If driver is not initialized.
    """
    driver = get_driver()
    if driver is None:
        raise RuntimeError("Neo4j driver not initialized")
    
    with driver.session() as session:
        result = session.run(cypher, parameters or {})
        return [record.data() for record in result]


# Backwards compatibility - keep old function but log deprecation warning
def connect_to_neo4j():
    """
    DEPRECATED: Use get_driver() instead.
    
    Legacy function for backwards compatibility.
    Initializes driver if needed and returns it.
    """
    logger.warning("connect_to_neo4j() is deprecated. Use get_driver() instead.")
    
    if _driver is None:
        init_driver()
    
    return get_driver()


if __name__ == '__main__':
    # Test the driver
    logging.basicConfig(level=logging.INFO)
    
    if init_driver():
        print("Driver initialized successfully")
        
        # Test a simple query
        try:
            results = execute_query("MATCH (n) RETURN count(n) as count")
            print(f"Nodes in database: {results[0]['count'] if results else 'N/A'}")
        except Exception as e:
            print(f"Query failed: {e}")
        
        print(f"Driver status: {get_driver_status()}")
        close_driver()
    else:
        print("Failed to initialize driver")
