"""
Neo-rag API Main Application

FastAPI application providing endpoints for hybrid RAG (Retrieval-Augmented Generation)
combining vector search and knowledge graph capabilities.
"""
import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from .database import neon_db, neo4j_db
from .services import ingestion_service, retrieval_service, query_service
from .models.api_models import (
    IngestDataRequest,
    RetrievalRequest,
    RetrievalResponse,
    QueryRequest,
    QueryResponse,
    HealthResponse,
    ErrorResponse,
)
from .middleware.rate_limiter import RateLimitMiddleware, rate_limiter
from .exceptions import NeoRagException
from .routers import config_router
from .services.config_service import config_service

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle: startup and shutdown events.
    
    Initializes database connection pools on startup and closes them on shutdown.
    """
    # Startup
    logger.info("Starting Neo-rag API...")
    
    neon_initialized = neon_db.init_pool()
    neo4j_initialized = neo4j_db.init_driver()
    
    if not neon_initialized:
        logger.warning("Neon database pool failed to initialize")
    if not neo4j_initialized:
        logger.warning("Neo4j driver failed to initialize")
    
    logger.info("Neo-rag API started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Neo-rag API...")
    neon_db.close_pool()
    neo4j_db.close_driver()
    logger.info("Neo-rag API shutdown complete")


app = FastAPI(
    title="Neo-rag API",
    description="API for the Neo-rag hybrid RAG application combining vector and graph search.",
    version="0.3.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.add_middleware(RateLimitMiddleware)

# Include routers
app.include_router(config_router.router)


# ==============================================================================
# Request Tracking Middleware
# ==============================================================================

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add a unique request ID for tracing."""
    request_id = str(uuid.uuid4())[:8]
    request.state.request_id = request_id
    
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# ==============================================================================
# Exception Handlers
# ==============================================================================

@app.exception_handler(NeoRagException)
async def neorag_exception_handler(request: Request, exc: NeoRagException):
    """Handle custom Neo-rag exceptions with structured responses."""
    request_id = getattr(request.state, 'request_id', 'unknown')
    logger.error(f"[{request_id}] {exc.error_code}: {exc.message}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "request_id": request_id,
            **exc.details
        }
    )


# ==============================================================================
# Endpoints
# ==============================================================================

@app.get("/")
async def root():
    """
    Root endpoint with a welcome message.
    
    Returns:
        Welcome message with API version.
    """
    return {
        "message": "Welcome to the Neo-rag API!",
        "version": "0.3.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify all service connections.
    
    Returns:
        Status of databases, LLM, and embedding services.
    """
    neon_status = neon_db.get_pool_status()
    neo4j_status = neo4j_db.get_driver_status()
    
    # Get config for LLM/embedding status
    config = config_service.get_config()
    
    llm_status = {
        "status": "configured" if config.llm.api_key else "not_configured",
        "provider": config.llm.provider,
        "model": config.llm.model,
    }
    
    embedding_status = {
        "status": "configured" if config.embedding.api_key else "not_configured",
        "provider": config.embedding.provider,
        "model": config.embedding.model,
    }
    
    overall_healthy = (
        neon_status.get("status") == "active" and 
        neo4j_status.get("status") == "connected"
    )
    
    return {
        "healthy": overall_healthy,
        "neon_database": neon_status,
        "neo4j_database": neo4j_status,
        "llm": llm_status,
        "embedding": embedding_status,
        "is_configured": config.is_configured,
        "version": "0.4.0"
    }


@app.get("/rate-limit-status")
async def rate_limit_status(request: Request):
    """
    Get rate limit status for the current client.
    
    Returns:
        Current rate limit statistics for the requesting client.
    """
    client_ip = request.client.host if request.client else "unknown"
    return rate_limiter.get_client_stats(client_ip)


@app.post("/ingest")
async def ingest_data(request: IngestDataRequest):
    """
    Ingest text data into the system.
    
    Processes the text by:
    1. Chunking into manageable pieces (using configurable strategy)
    2. Generating embeddings for vector storage
    3. Extracting entities and relationships for graph storage
    
    Args:
        request: Contains text content, metadata, and chunking configuration.
    
    Returns:
        Ingestion results including chunk count and strategy used.
    
    Raises:
        HTTPException: If ingestion fails.
    """
    try:
        result = ingestion_service.ingest_text(
            text=request.text,
            metadata=request.metadata,
            chunking_strategy=request.chunking_strategy,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        return {
            "message": f"Successfully ingested {result['chunks_stored']} chunks.",
            "chunks_stored": result['chunks_stored'],
            "strategy_used": result['strategy_used'],
            "chunk_count": result.get('chunk_count', 0),
            "avg_chunk_size": result.get('avg_chunk_size', 0),
            "graph_nodes": result.get('graph_nodes', 0)
        }
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_data(request: RetrievalRequest):
    """
    Retrieve data from the system using agentic hybrid search.
    
    Uses an intelligent router to determine whether to use vector search,
    graph search, or code analysis based on the query.
    
    Args:
        request: Contains query string and optional top_k parameter.
    
    Returns:
        Retrieved context from vector and/or graph search with synthesized answer.
    
    Raises:
        HTTPException: If retrieval fails.
    """
    try:
        return retrieval_service.hybrid_retrieval(request.query, request.top_k)
    except Exception as e:
        logger.error(f"Retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Retrieval failed: {str(e)}")


@app.post("/api/v1/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Process a query using the hybrid query service with alpha weighting.
    
    The alpha parameter controls the balance between graph and vector context:
    - alpha=0.0: Vector context only (semantic search)
    - alpha=0.5: Equal weight (default)
    - alpha=1.0: Graph context only (relationship queries)
    
    Args:
        request: Contains query string and optional alpha parameter (0.0-1.0).
    
    Returns:
        Synthesized answer with both graph and vector contexts.
    
    Raises:
        HTTPException: If query processing fails.
    """
    try:
        query_service_instance = query_service.QueryService()
        return query_service_instance.query(request.query, request.alpha)
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")
