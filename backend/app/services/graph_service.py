"""
Graph Service

Provides functionality for querying the Neo4j knowledge graph using
natural language queries converted to Cypher via LangChain.
"""
import logging
from typing import List, Dict, Any, Optional

from langchain_community.chains.graph_qa.cypher import GraphCypherQAChain
from langchain_openai import ChatOpenAI
from langchain_community.graphs import Neo4jGraph

from ..database import neo4j_db

logger = logging.getLogger(__name__)

# Cached graph instance for reuse
_graph_instance: Optional[Neo4jGraph] = None


def get_neo4j_graph() -> Optional[Neo4jGraph]:
    """
    Get or create a Neo4jGraph instance for LangChain operations.
    
    Uses the managed driver from neo4j_db module and caches the graph
    instance for reuse.
    
    Returns:
        Neo4jGraph instance, or None if driver is not available.
    """
    global _graph_instance
    
    if _graph_instance is not None:
        return _graph_instance
    
    driver = neo4j_db.get_driver()
    if driver is None:
        logger.error("Neo4j driver not available. Call neo4j_db.init_driver() first.")
        return None
    
    try:
        _graph_instance = Neo4jGraph(driver=driver)
        return _graph_instance
    except Exception as e:
        logger.error(f"Failed to create Neo4jGraph: {e}")
        return None


def query_graph(query: str, model: str = "gpt-4-turbo") -> List[Dict[str, Any]]:
    """
    Convert a natural language query to Cypher and execute it.
    
    Uses LangChain's GraphCypherQAChain to translate natural language
    to Cypher queries and execute them against the Neo4j database.
    
    Args:
        query: Natural language query about relationships or entities.
        model: OpenAI model to use for Cypher generation.
    
    Returns:
        List of results from the graph query, or empty list on failure.
    
    Example:
        >>> results = query_graph("What entities are related to AI?")
        >>> for item in results:
        ...     print(item)
    """
    graph = get_neo4j_graph()
    if graph is None:
        logger.warning("Cannot query graph: Neo4j not available")
        return []
    
    try:
        chain = GraphCypherQAChain.from_llm(
            ChatOpenAI(model=model, temperature=0), 
            graph=graph, 
            verbose=True,
            return_intermediate_steps=True
        )
        
        result = chain.invoke({"query": query})
        
        # Log the generated Cypher for debugging
        intermediate_steps = result.get("intermediate_steps", [])
        if intermediate_steps:
            logger.debug(f"Generated Cypher: {intermediate_steps}")
        
        query_result = result.get("result", [])
        
        # Ensure we return a list
        if isinstance(query_result, list):
            return query_result
        elif isinstance(query_result, str):
            return [{"content": query_result}]
        else:
            return [{"content": str(query_result)}]
            
    except Exception as e:
        logger.error(f"Graph query failed: {e}")
        return []


def execute_cypher(cypher: str, parameters: dict = None) -> List[Dict[str, Any]]:
    """
    Execute a raw Cypher query directly.
    
    Use this for custom queries that don't need LLM translation.
    
    Args:
        cypher: The Cypher query to execute.
        parameters: Optional query parameters (for safe parameterized queries).
    
    Returns:
        List of records from the query result.
    
    Warning:
        Use parameterized queries to prevent Cypher injection.
        Never interpolate user input directly into the cypher string.
    """
    try:
        return neo4j_db.execute_query(cypher, parameters)
    except Exception as e:
        logger.error(f"Cypher execution failed: {e}")
        return []


def get_graph_schema() -> Optional[str]:
    """
    Get the current schema of the Neo4j graph.
    
    Returns:
        String representation of the graph schema, or None on failure.
    """
    graph = get_neo4j_graph()
    if graph is None:
        return None
    
    try:
        return graph.schema
    except Exception as e:
        logger.error(f"Failed to get graph schema: {e}")
        return None


def reset_graph_cache() -> None:
    """
    Reset the cached graph instance.
    
    Call this if you need to refresh the graph connection,
    for example after schema changes.
    """
    global _graph_instance
    _graph_instance = None
    logger.info("Graph cache reset")
