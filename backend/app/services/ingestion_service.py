"""
Ingestion Service

Handles the complete ingestion pipeline:
1. Text chunking (with configurable strategies)
2. Embedding generation
3. Vector storage in Neon DB
4. Entity/relationship extraction
5. Graph storage in Neo4j
"""
import uuid
import hashlib
import logging
from typing import List, Dict, Any, Optional

from ..database import neon_db, neo4j_db
from . import embedding_service
from . import graph_extraction_service
from .chunking_service import (
    ChunkingService, 
    ChunkingConfig, 
    ChunkingStrategy,
    ChunkResult
)

logger = logging.getLogger(__name__)

# Chunking service instance
_chunking_service: Optional[ChunkingService] = None


def get_chunking_service() -> ChunkingService:
    """Get or create the chunking service instance."""
    global _chunking_service
    if _chunking_service is None:
        _chunking_service = ChunkingService()
    return _chunking_service


# Allowed labels for graph nodes (prevents Cypher injection)
ALLOWED_NODE_LABELS = {"Entity", "Concept", "Person", "Organization", "Location", "Event", "Document"}
ALLOWED_REL_TYPES = {"RELATES_TO", "MENTIONS", "CONTAINS", "PART_OF", "CREATED_BY", "LOCATED_IN"}


def chunk_text(
    text: str, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 200,
    strategy: str = "recursive"
) -> ChunkResult:
    """
    Splits the input text into manageable chunks.
    
    Args:
        text: The raw text to split.
        chunk_size: Maximum size of each chunk in characters.
        chunk_overlap: Overlap between consecutive chunks.
        strategy: Chunking strategy (recursive, semantic, markdown, code, auto).
    
    Returns:
        ChunkResult with chunks and metadata.
    """
    service = get_chunking_service()
    
    # Handle "auto" strategy
    if strategy == "auto":
        strategy = service.detect_content_type(text).value
    
    # Map string to enum
    strategy_enum = ChunkingStrategy(strategy)
    
    config = ChunkingConfig(
        strategy=strategy_enum,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    
    return service.chunk_text(text, config)


def _compute_content_hash(content: str) -> str:
    """
    Compute SHA-256 hash of content for deduplication.
    
    Args:
        content: The text content to hash.
    
    Returns:
        Hex digest of the content hash.
    """
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def _sanitize_label(label: str) -> str:
    """
    Sanitize and validate graph node label.
    
    Args:
        label: The proposed node label.
    
    Returns:
        A safe label from the allowed list.
    
    Note:
        Falls back to 'Entity' if label is not in allowed list.
    """
    if label in ALLOWED_NODE_LABELS:
        return label
    logger.warning(f"Unknown label '{label}', falling back to 'Entity'")
    return "Entity"


def _sanitize_rel_type(rel_type: str) -> str:
    """
    Sanitize and validate relationship type.
    
    Args:
        rel_type: The proposed relationship type.
    
    Returns:
        A safe relationship type from the allowed list.
    
    Note:
        Falls back to 'RELATES_TO' if type is not in allowed list.
    """
    # Normalize: uppercase and replace spaces with underscores
    normalized = rel_type.upper().replace(" ", "_").replace("-", "_")
    
    if normalized in ALLOWED_REL_TYPES:
        return normalized
    logger.warning(f"Unknown relationship type '{rel_type}', falling back to 'RELATES_TO'")
    return "RELATES_TO"


def _store_chunks_in_vector_db(chunks: List[str], embeddings: List[List[float]], 
                                metadata: Dict[str, Any]) -> int:
    """
    Store text chunks and embeddings in Neon vector database.
    
    Args:
        chunks: List of text chunks.
        embeddings: Corresponding embeddings for each chunk.
        metadata: Metadata to attach to each document.
    
    Returns:
        Number of chunks successfully stored.
    """
    with neon_db.get_connection_context() as conn:
        if conn is None:
            logger.error("Failed to get Neon DB connection. Aborting vector storage.")
            return 0
        
        stored_count = 0
        with conn.cursor() as cur:
            for i, chunk in enumerate(chunks):
                doc_id = str(uuid.uuid4())
                content_hash = _compute_content_hash(chunk)
                
                # Check for duplicate content
                cur.execute(
                    "SELECT id FROM documents WHERE content_hash = %s",
                    (content_hash,)
                )
                if cur.fetchone():
                    logger.debug(f"Skipping duplicate chunk (hash: {content_hash[:16]}...)")
                    continue
                
                cur.execute(
                    """
                    INSERT INTO documents (id, content, embedding, metadata, content_hash) 
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (doc_id, chunk, embeddings[i], metadata, content_hash)
                )
                stored_count += 1
        
        conn.commit()
        logger.info(f"Stored {stored_count} chunks in vector database (skipped {len(chunks) - stored_count} duplicates)")
        return stored_count


def _store_graph_data(graph_data: Dict[str, Any]) -> int:
    """
    Store extracted graph data (nodes and relationships) in Neo4j with embeddings.
    
    Args:
        graph_data: Dictionary containing 'nodes' and 'relationships' lists.
    
    Returns:
        Number of nodes stored.
    """
    driver = neo4j_db.get_driver()
    if driver is None:
        logger.error("Failed to get Neo4j driver. Aborting graph storage.")
        return 0
    
    nodes = graph_data.get("nodes", [])
    relationships = graph_data.get("relationships", [])
    
    # Generate embeddings for all nodes
    node_texts = []
    for node in nodes:
        node_label = node.get('label', 'Entity')
        node_id = node.get('id', '')
        node_texts.append(f"{node_label}: {node_id}")
    
    # Batch generate embeddings
    node_embeddings = []
    if node_texts:
        try:
            embedding_model = embedding_service.get_openai_embeddings()
            node_embeddings = embedding_model.embed_documents(node_texts)
            logger.info(f"Generated embeddings for {len(node_embeddings)} nodes")
        except Exception as e:
            logger.warning(f"Failed to generate node embeddings: {e}")
            node_embeddings = [None] * len(nodes)
    
    with driver.session() as session:
        # Store nodes with sanitized labels and embeddings
        for i, node in enumerate(nodes):
            safe_label = _sanitize_label(node.get('label', 'Entity'))
            node_id = node.get('id', str(uuid.uuid4()))
            embedding = node_embeddings[i] if i < len(node_embeddings) else None
            
            # Use parameterized query with pre-validated label
            if embedding:
                cypher = f"MERGE (n:{safe_label} {{id: $id}}) SET n.label = $label, n.embedding = $embedding"
                session.run(cypher, id=node_id, label=node.get('label', 'Entity'), embedding=embedding)
            else:
                cypher = f"MERGE (n:{safe_label} {{id: $id}}) SET n.label = $label"
                session.run(cypher, id=node_id, label=node.get('label', 'Entity'))
        
        # Store relationships with sanitized types
        for rel in relationships:
            safe_type = _sanitize_rel_type(rel.get('type', 'RELATES_TO'))
            source_id = rel.get('source_node_id')
            target_id = rel.get('target_node_id')
            
            if not source_id or not target_id:
                logger.warning(f"Skipping relationship with missing source/target: {rel}")
                continue
            
            # Use parameterized query with pre-validated type
            cypher = f"""
                MATCH (a {{id: $source_id}}), (b {{id: $target_id}})
                MERGE (a)-[r:{safe_type}]->(b)
            """
            session.run(cypher, source_id=source_id, target_id=target_id)
    
    logger.info(f"Stored {len(nodes)} nodes and {len(relationships)} relationships in graph database")
    return len(nodes)


def ingest_text(
    text: str, 
    metadata: Dict[str, Any] = None,
    chunking_strategy: str = "auto",
    chunk_size: int = 1000,
    chunk_overlap: int = 200
) -> Dict[str, Any]:
    """
    Ingests raw text, chunks it, generates embeddings, and stores it in both databases.
    
    The ingestion process:
    1. Splits text into overlapping chunks (using configurable strategy)
    2. Generates embeddings for each chunk
    3. Stores chunks + embeddings in Neon (with deduplication)
    4. Extracts entities and relationships using LLM
    5. Stores graph data in Neo4j
    
    Args:
        text: The raw text content to ingest.
        metadata: Optional metadata about the source document.
        chunking_strategy: Strategy to use (auto, recursive, semantic, markdown, code).
        chunk_size: Target size for each chunk.
        chunk_overlap: Overlap between consecutive chunks.
    
    Returns:
        Dict with ingestion results including chunk count and strategy used.
    
    Raises:
        ValueError: If text is empty or None.
    """
    if not text or not text.strip():
        raise ValueError("Cannot ingest empty text")
    
    metadata = metadata or {}
    
    # Step 1: Chunk the text using configurable strategy
    chunk_result = chunk_text(
        text, 
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap,
        strategy=chunking_strategy
    )
    chunks = chunk_result.chunks
    logger.info(
        f"Split text into {chunk_result.chunk_count} chunks "
        f"using {chunk_result.strategy_used} strategy "
        f"(avg size: {chunk_result.avg_chunk_size:.0f} chars)"
    )
    
    if not chunks:
        logger.warning("No chunks generated from text")
        return {
            "chunks_stored": 0,
            "strategy_used": chunk_result.strategy_used,
            "graph_nodes": 0
        }
    
    # Step 2: Generate embeddings
    try:
        embedding_model = embedding_service.get_openai_embeddings()
        embeddings = embedding_model.embed_documents(chunks)
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        raise
    
    # Step 3: Store in vector database
    stored_count = _store_chunks_in_vector_db(chunks, embeddings, metadata)
    
    # Step 4: Extract graph data
    try:
        graph_data = graph_extraction_service.extract_entities_and_relationships(text)
    except Exception as e:
        logger.warning(f"Graph extraction failed (non-fatal): {e}")
        graph_data = {"nodes": [], "relationships": []}
    
    # Step 5: Store in graph database
    graph_nodes = _store_graph_data(graph_data)
    
    logger.info(f"Ingestion complete: {stored_count} chunks stored, {graph_nodes} graph nodes")
    
    return {
        "chunks_stored": stored_count,
        "strategy_used": chunk_result.strategy_used,
        "chunk_count": chunk_result.chunk_count,
        "avg_chunk_size": chunk_result.avg_chunk_size,
        "graph_nodes": graph_nodes
    }

