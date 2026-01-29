"""
Enhanced Pydantic models with strict validation for Neo-rag API.

This module provides input validation with security-focused constraints
to prevent injection attacks and ensure data integrity.
"""
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List, Dict, Any
import re


# ==============================================================================
# Validation Helpers
# ==============================================================================

def sanitize_string(value: str, max_length: int = 10000) -> str:
    """Remove potentially dangerous characters and limit length."""
    if not value:
        return value
    # Strip null bytes and control characters (except newlines/tabs)
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', value)
    return cleaned[:max_length]


def validate_metadata_keys(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Validate metadata keys are alphanumeric with underscores."""
    if not metadata:
        return metadata
    valid_key_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    for key in metadata.keys():
        if not valid_key_pattern.match(key):
            raise ValueError(f"Invalid metadata key: '{key}'. Keys must be alphanumeric with underscores.")
    return metadata


# ==============================================================================
# Request Models
# ==============================================================================

class QueryRequest(BaseModel):
    """
    Request model for the /api/v1/query endpoint.
    
    Attributes:
        query: The search query (1-2000 characters)
        alpha: Weight for graph vs vector search (0.0 = all vector, 1.0 = all graph)
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Search query text"
    )
    alpha: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Graph weight (0=vector only, 1=graph only)"
    )
    
    @field_validator('query')
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        return sanitize_string(v, max_length=2000)


class SourceCitation(BaseModel):
    """Model for source citations with detailed provenance."""
    source_id: str = Field(..., description="Unique identifier for the source chunk or node")
    source_type: str = Field(..., description="Type: vector_chunk, graph_node, or hybrid")
    content_preview: str = Field(default="", max_length=200, description="Brief preview of the source content")
    similarity_score: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Similarity/relevance score")


class QueryResponse(BaseModel):
    """Response model for the /api/v1/query endpoint with transparency features."""
    answer: str
    graph_context: str
    vector_context: str
    sources: Optional[List[str]] = Field(default_factory=list)
    source_citations: Optional[List[SourceCitation]] = Field(
        default_factory=list,
        description="Detailed source citations with IDs and scores"
    )
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    routing_decision: Optional[str] = Field(
        default=None,
        description="Which retrieval method was used: vector, graph, hybrid, or hybrid_graph"
    )


class IngestDataRequest(BaseModel):
    """
    Request model for data ingestion.
    
    Attributes:
        text: Document text to ingest (1-100,000 characters)
        metadata: Optional metadata (keys must be alphanumeric)
        chunking_strategy: Chunking method to use (recursive, semantic, markdown, code)
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    text: str = Field(
        ...,
        min_length=1,
        max_length=100000,
        description="Document text to ingest"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Optional document metadata"
    )
    chunking_strategy: str = Field(
        default="auto",
        description="Chunking strategy: auto, recursive, semantic, markdown, code"
    )
    chunk_size: int = Field(default=1000, ge=100, le=4000, description="Target chunk size")
    chunk_overlap: int = Field(default=200, ge=0, le=500, description="Overlap between chunks")
    
    @field_validator('text')
    @classmethod
    def sanitize_text(cls, v: str) -> str:
        return sanitize_string(v, max_length=100000)
    
    @field_validator('metadata')
    @classmethod
    def validate_metadata(cls, v: Dict[str, Any]) -> Dict[str, Any]:
        return validate_metadata_keys(v)
    
    @field_validator('chunking_strategy')
    @classmethod
    def validate_chunking_strategy(cls, v: str) -> str:
        valid = {"auto", "recursive", "semantic", "markdown", "code"}
        if v.lower() not in valid:
            raise ValueError(f"Invalid chunking_strategy: {v}. Must be one of: {valid}")
        return v.lower()


class RetrievalRequest(BaseModel):
    """
    Request model for retrieval endpoint.
    
    Attributes:
        query: Search query text
        top_k: Number of results to return (1-50)
    """
    model_config = ConfigDict(str_strip_whitespace=True)
    
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="Search query"
    )
    top_k: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Number of results to return"
    )
    
    @field_validator('query')
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        return sanitize_string(v, max_length=2000)


# ==============================================================================
# Data Models
# ==============================================================================

class Document(BaseModel):
    """Represents a document stored in the vector database."""
    id: str = Field(..., min_length=1, max_length=100)
    content: str
    embedding: List[float] = Field(..., min_length=1)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GraphEntity(BaseModel):
    """Represents an entity in the knowledge graph."""
    id: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=100, pattern=r'^[A-Za-z][A-Za-z0-9_]*$')
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphRelationship(BaseModel):
    """Represents a relationship in the knowledge graph."""
    source_id: str = Field(..., min_length=1, max_length=100)
    target_id: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=100, pattern=r'^[A-Z][A-Z0-9_]*$')
    properties: Dict[str, Any] = Field(default_factory=dict)


class RetrievalResponse(BaseModel):
    """Response model for retrieval endpoint."""
    vector_results: List[Document] = Field(default_factory=list)
    graph_results: List[Dict[str, Any]] = Field(default_factory=list)
    synthesized_answer: str
    routing_decision: Optional[str] = None


# ==============================================================================
# Graph Extraction Models
# ==============================================================================

class Node(BaseModel):
    """Represents a node for graph extraction."""
    id: str = Field(..., min_length=1, max_length=100)
    label: str = Field(..., min_length=1, max_length=100)


class Relationship(BaseModel):
    """Represents a relationship for graph extraction."""
    source_node_id: str = Field(..., min_length=1, max_length=100)
    target_node_id: str = Field(..., min_length=1, max_length=100)
    type: str = Field(..., min_length=1, max_length=100)
    properties: Dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraph(BaseModel):
    """Represents an extracted knowledge graph."""
    nodes: List[Node] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)


# ==============================================================================
# Health & Status Models
# ==============================================================================

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    healthy: bool
    neon_database: Dict[str, Any]
    neo4j_database: Dict[str, Any]
    version: str = "0.2.0"


class ErrorResponse(BaseModel):
    """Standard error response model."""
    detail: str
    error_code: Optional[str] = None
    request_id: Optional[str] = None