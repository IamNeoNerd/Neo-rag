"""
Custom exceptions for Neo-rag API.

Provides structured error handling with error codes and detailed messages
for better debugging and client-side error handling.
"""
from typing import Optional, Dict, Any


class NeoRagException(Exception):
    """Base exception for all Neo-rag errors."""
    
    error_code: str = "NEORAG_ERROR"
    status_code: int = 500
    
    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        self.message = message
        self.details = details or {}
        self.cause = cause
        super().__init__(message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API response."""
        result = {
            "error_code": self.error_code,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


# ==============================================================================
# Database Exceptions
# ==============================================================================

class DatabaseException(NeoRagException):
    """Base exception for database errors."""
    error_code = "DATABASE_ERROR"


class NeonConnectionError(DatabaseException):
    """Failed to connect to Neon PostgreSQL database."""
    error_code = "NEON_CONNECTION_ERROR"
    status_code = 503


class Neo4jConnectionError(DatabaseException):
    """Failed to connect to Neo4j database."""
    error_code = "NEO4J_CONNECTION_ERROR"
    status_code = 503


class PoolExhaustedError(DatabaseException):
    """Database connection pool is exhausted."""
    error_code = "POOL_EXHAUSTED"
    status_code = 503
    
    def __init__(self, pool_type: str = "unknown"):
        super().__init__(
            f"Connection pool exhausted for {pool_type}. Please try again later.",
            details={"pool_type": pool_type}
        )


class QueryExecutionError(DatabaseException):
    """Error executing database query."""
    error_code = "QUERY_EXECUTION_ERROR"
    status_code = 500


# ==============================================================================
# LLM Exceptions
# ==============================================================================

class LLMException(NeoRagException):
    """Base exception for LLM-related errors."""
    error_code = "LLM_ERROR"


class LLMApiKeyError(LLMException):
    """Invalid or missing LLM API key."""
    error_code = "LLM_API_KEY_ERROR"
    status_code = 401
    
    def __init__(self, provider: str = "unknown"):
        super().__init__(
            f"Invalid or missing API key for {provider}",
            details={"provider": provider}
        )


class LLMRateLimitError(LLMException):
    """LLM provider rate limit exceeded."""
    error_code = "LLM_RATE_LIMIT"
    status_code = 429
    
    def __init__(self, provider: str = "unknown", retry_after: Optional[int] = None):
        super().__init__(
            f"Rate limit exceeded for {provider}. Please wait and retry.",
            details={"provider": provider, "retry_after": retry_after}
        )


class LLMTimeoutError(LLMException):
    """LLM request timed out."""
    error_code = "LLM_TIMEOUT"
    status_code = 504
    
    def __init__(self, provider: str = "unknown", timeout_seconds: int = 30):
        super().__init__(
            f"Request to {provider} timed out after {timeout_seconds}s",
            details={"provider": provider, "timeout_seconds": timeout_seconds}
        )


class EmbeddingGenerationError(LLMException):
    """Failed to generate embeddings."""
    error_code = "EMBEDDING_GENERATION_ERROR"
    status_code = 500


class GraphExtractionError(LLMException):
    """Failed to extract knowledge graph from text."""
    error_code = "GRAPH_EXTRACTION_ERROR"
    status_code = 500


# ==============================================================================
# Ingestion Exceptions
# ==============================================================================

class IngestionException(NeoRagException):
    """Base exception for ingestion errors."""
    error_code = "INGESTION_ERROR"


class DuplicateDocumentError(IngestionException):
    """Document already exists in the database."""
    error_code = "DUPLICATE_DOCUMENT"
    status_code = 409
    
    def __init__(self, content_hash: str):
        super().__init__(
            "Document with identical content already exists",
            details={"content_hash": content_hash}
        )


class ChunkingError(IngestionException):
    """Error during text chunking."""
    error_code = "CHUNKING_ERROR"
    status_code = 500


# ==============================================================================
# Retrieval Exceptions
# ==============================================================================

class RetrievalException(NeoRagException):
    """Base exception for retrieval errors."""
    error_code = "RETRIEVAL_ERROR"


class VectorSearchError(RetrievalException):
    """Error during vector similarity search."""
    error_code = "VECTOR_SEARCH_ERROR"
    status_code = 500


class GraphSearchError(RetrievalException):
    """Error during graph search."""
    error_code = "GRAPH_SEARCH_ERROR"
    status_code = 500


class RoutingError(RetrievalException):
    """Error in query routing decision."""
    error_code = "ROUTING_ERROR"
    status_code = 500


# ==============================================================================
# Validation Exceptions
# ==============================================================================

class ValidationException(NeoRagException):
    """Base exception for validation errors."""
    error_code = "VALIDATION_ERROR"
    status_code = 400


class InvalidInputError(ValidationException):
    """Invalid input data provided."""
    error_code = "INVALID_INPUT"
    
    def __init__(self, field: str, reason: str):
        super().__init__(
            f"Invalid value for field '{field}': {reason}",
            details={"field": field, "reason": reason}
        )


class ContentTooLargeError(ValidationException):
    """Content exceeds maximum allowed size."""
    error_code = "CONTENT_TOO_LARGE"
    status_code = 413
    
    def __init__(self, max_size: int, actual_size: int):
        super().__init__(
            f"Content size {actual_size} exceeds maximum allowed {max_size}",
            details={"max_size": max_size, "actual_size": actual_size}
        )
