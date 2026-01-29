"""
Graph Embedding Service

Adds embedding capabilities to Neo4j graph nodes for semantic similarity search.
Enables hybrid graph+vector traversal by storing embeddings as node properties.
"""
import logging
from typing import List, Dict, Any, Optional
import numpy as np

from ..database import neo4j_db
from . import embedding_service

logger = logging.getLogger(__name__)


def generate_node_embedding(node_id: str, node_label: str, context: str = "") -> List[float]:
    """
    Generate an embedding for a graph node.
    
    Args:
        node_id: The node's ID (usually a meaningful name).
        node_label: The node's label (Entity, Concept, etc.).
        context: Optional additional context.
    
    Returns:
        Embedding vector as a list of floats.
    """
    text_to_embed = f"{node_label}: {node_id}"
    if context:
        text_to_embed += f" - {context}"
    
    embedding_model = embedding_service.get_openai_embeddings()
    return embedding_model.embed_query(text_to_embed)


def store_node_with_embedding(
    node_id: str, 
    node_label: str, 
    embedding: List[float],
    properties: Optional[Dict[str, Any]] = None
) -> bool:
    """Store a node in Neo4j with its embedding vector."""
    driver = neo4j_db.get_driver()
    if driver is None:
        return False
    
    properties = properties or {}
    
    try:
        with driver.session() as session:
            cypher = f"""
                MERGE (n:{node_label} {{id: $id}})
                SET n.embedding = $embedding, n.label = $label, n += $properties
            """
            session.run(cypher, id=node_id, embedding=embedding, label=node_label, properties=properties)
        return True
    except Exception as e:
        logger.error(f"Failed to store node {node_id}: {e}")
        return False


def find_similar_nodes(
    query_embedding: List[float],
    top_k: int = 5,
    min_similarity: float = 0.7
) -> List[Dict[str, Any]]:
    """
    Find nodes similar to query embedding using cosine similarity.
    
    Note: Uses manual calculation for compatibility. For production scale,
    consider Neo4j's vector index (5.11+).
    """
    driver = neo4j_db.get_driver()
    if driver is None:
        return []
    
    try:
        with driver.session() as session:
            result = session.run(
                "MATCH (n) WHERE n.embedding IS NOT NULL RETURN n.id as id, n.label as label, n.embedding as embedding"
            )
            
            query_vec = np.array(query_embedding)
            query_norm = np.linalg.norm(query_vec)
            
            scored_nodes = []
            for record in result:
                node_vec = np.array(record["embedding"])
                node_norm = np.linalg.norm(node_vec)
                
                if node_norm == 0 or query_norm == 0:
                    continue
                
                similarity = float(np.dot(query_vec, node_vec) / (query_norm * node_norm))
                
                if similarity >= min_similarity:
                    scored_nodes.append({
                        "id": record["id"],
                        "label": record["label"],
                        "similarity": round(similarity, 3)
                    })
            
            scored_nodes.sort(key=lambda x: x["similarity"], reverse=True)
            return scored_nodes[:top_k]
            
    except Exception as e:
        logger.error(f"Similarity search failed: {e}")
        return []


def hybrid_graph_search(query: str, top_k: int = 5, hop_depth: int = 1) -> Dict[str, Any]:
    """
    Hybrid search: find similar nodes by embedding, then traverse relationships.
    
    Args:
        query: Natural language query.
        top_k: Number of similar nodes to find.
        hop_depth: Relationship hops to traverse.
    
    Returns:
        Dict with similar nodes and connected context.
    """
    try:
        embedding_model = embedding_service.get_openai_embeddings()
        query_embedding = embedding_model.embed_query(query)
    except Exception as e:
        logger.error(f"Failed to embed query: {e}")
        return {"nodes": [], "context": ""}
    
    similar_nodes = find_similar_nodes(query_embedding, top_k=top_k)
    
    if not similar_nodes:
        return {"nodes": [], "context": ""}
    
    driver = neo4j_db.get_driver()
    if driver is None:
        return {"nodes": similar_nodes, "context": ""}
    
    try:
        with driver.session() as session:
            node_ids = [n["id"] for n in similar_nodes]
            
            cypher = f"""
                MATCH (n)-[r*1..{hop_depth}]-(connected)
                WHERE n.id IN $node_ids
                RETURN DISTINCT n.id as source, type(r[0]) as rel_type, connected.id as target
                LIMIT 50
            """
            
            result = session.run(cypher, node_ids=node_ids)
            connections = [{"source": r["source"], "rel": r["rel_type"], "target": r["target"]} for r in result]
            
            # Build context
            context_parts = [f"{n['label']}: {n['id']} (sim: {n['similarity']})" for n in similar_nodes]
            for c in connections:
                context_parts.append(f"  {c['source']} --{c['rel']}--> {c['target']}")
            
            return {"nodes": similar_nodes, "connections": connections, "context": "\n".join(context_parts)}
            
    except Exception as e:
        logger.error(f"Graph traversal failed: {e}")
        return {"nodes": similar_nodes, "context": ""}


def get_embedding_stats() -> Dict[str, Any]:
    """Get statistics about node embeddings in the graph."""
    driver = neo4j_db.get_driver()
    if driver is None:
        return {"status": "disconnected"}
    
    try:
        with driver.session() as session:
            result = session.run("""
                MATCH (n)
                RETURN count(n) as total, 
                       sum(CASE WHEN n.embedding IS NOT NULL THEN 1 ELSE 0 END) as with_embeddings
            """)
            record = result.single()
            total = record["total"]
            with_emb = record["with_embeddings"]
            return {
                "total_nodes": total,
                "nodes_with_embeddings": with_emb,
                "coverage": round(with_emb / total, 2) if total > 0 else 0
            }
    except Exception as e:
        return {"status": "error", "error": str(e)}
