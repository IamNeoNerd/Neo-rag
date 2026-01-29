"""
Configuration API Router

Endpoints for managing application configuration from the frontend.
"""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..services.config_service import config_service, AppConfig, LLMConfig, EmbeddingConfig, NeonConfig, Neo4jConfig

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/config", tags=["configuration"])


# Request/Response Models

class ConfigUpdateRequest(BaseModel):
    """Request to update configuration."""
    llm: Optional[dict] = None
    embedding: Optional[dict] = None
    neon: Optional[dict] = None
    neo4j: Optional[dict] = None


class ConnectionTestRequest(BaseModel):
    """Request to test a specific connection."""
    type: str = Field(..., pattern="^(neon|neo4j|llm|embedding)$")
    config: dict


class ConnectionTestResponse(BaseModel):
    """Response from connection test."""
    success: bool
    message: str
    details: Optional[dict] = None


class ValidateKeyRequest(BaseModel):
    """Request to validate an API key."""
    provider: str
    api_key: str
    type: str = Field(default="llm", pattern="^(llm|embedding)$")


# Endpoints

@router.get("")
async def get_config():
    """
    Get current configuration (with masked API keys).
    
    Returns config suitable for display in frontend settings.
    """
    return config_service.get_masked_config()


@router.put("")
async def update_config(request: ConfigUpdateRequest):
    """
    Update configuration.
    
    Accepts partial updates - only specified fields will be changed.
    """
    try:
        updates = request.model_dump(exclude_none=True)
        
        # Mark as configured if we have the essentials
        if updates:
            current = config_service.get_config()
            updates["is_configured"] = True
        
        new_config = config_service.update_config(updates)
        logger.info("Configuration updated successfully")
        return {"success": True, "config": config_service.get_masked_config()}
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=ConnectionTestResponse)
async def test_connection(request: ConnectionTestRequest):
    """
    Test a specific connection.
    
    Validates that the provided configuration can connect successfully.
    """
    try:
        if request.type == "neon":
            return await _test_neon(request.config)
        elif request.type == "neo4j":
            return await _test_neo4j(request.config)
        elif request.type == "llm":
            return await _test_llm(request.config)
        elif request.type == "embedding":
            return await _test_embedding(request.config)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown type: {request.type}")
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return ConnectionTestResponse(
            success=False,
            message=str(e)
        )


@router.post("/validate-key")
async def validate_api_key(request: ValidateKeyRequest):
    """
    Validate an API key without storing it.
    
    Quick check that the key format is valid and works.
    """
    try:
        if request.type == "llm":
            result = await _test_llm({
                "provider": request.provider,
                "api_key": request.api_key
            })
        else:
            result = await _test_embedding({
                "provider": request.provider,
                "api_key": request.api_key
            })
        return {"valid": result.success, "message": result.message}
    except Exception as e:
        return {"valid": False, "message": str(e)}


# Connection Test Implementations

async def _test_neon(config: dict) -> ConnectionTestResponse:
    """Test Neon PostgreSQL connection."""
    import psycopg2
    
    connection_string = config.get("connection_string", "")
    if not connection_string:
        return ConnectionTestResponse(
            success=False,
            message="Connection string is required"
        )
    
    try:
        conn = psycopg2.connect(connection_string, connect_timeout=10)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return ConnectionTestResponse(
            success=True,
            message="Connected successfully",
            details={"version": version.split(",")[0]}
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}"
        )


async def _test_neo4j(config: dict) -> ConnectionTestResponse:
    """Test Neo4j connection."""
    from neo4j import GraphDatabase
    
    uri = config.get("uri", "")
    username = config.get("username", "neo4j")
    password = config.get("password", "")
    
    if not uri or not password:
        return ConnectionTestResponse(
            success=False,
            message="URI and password are required"
        )
    
    try:
        driver = GraphDatabase.driver(uri, auth=(username, password))
        driver.verify_connectivity()
        info = driver.get_server_info()
        driver.close()
        
        return ConnectionTestResponse(
            success=True,
            message="Connected successfully",
            details={"version": info.agent}
        )
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Connection failed: {str(e)}"
        )


async def _test_llm(config: dict) -> ConnectionTestResponse:
    """Test LLM API connection."""
    provider = config.get("provider", "openai")
    api_key = config.get("api_key", "")
    
    if not api_key:
        return ConnectionTestResponse(
            success=False,
            message="API key is required"
        )
    
    try:
        if provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            models = client.models.list()
            return ConnectionTestResponse(
                success=True,
                message="OpenAI API key valid",
                details={"models_available": len(list(models))}
            )
        
        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            # Simple validation - send a minimal request
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=5,
                messages=[{"role": "user", "content": "Hi"}]
            )
            return ConnectionTestResponse(
                success=True,
                message="Anthropic API key valid"
            )
        
        elif provider == "google":
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            models = genai.list_models()
            return ConnectionTestResponse(
                success=True,
                message="Google API key valid"
            )
        
        elif provider == "groq":
            from groq import Groq
            client = Groq(api_key=api_key)
            models = client.models.list()
            return ConnectionTestResponse(
                success=True,
                message="Groq API key valid"
            )
        
        elif provider in ["ollama", "local"]:
            # Local providers don't need API key validation
            return ConnectionTestResponse(
                success=True,
                message="Local provider configured"
            )
        
        else:
            return ConnectionTestResponse(
                success=False,
                message=f"Unknown provider: {provider}"
            )
    
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"API key validation failed: {str(e)}"
        )


async def _test_embedding(config: dict) -> ConnectionTestResponse:
    """Test embedding API connection."""
    provider = config.get("provider", "openai")
    api_key = config.get("api_key", "")
    
    if not api_key and provider not in ["ollama", "local"]:
        return ConnectionTestResponse(
            success=False,
            message="API key is required"
        )
    
    try:
        if provider == "openai":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            # Test with a small embedding request
            response = client.embeddings.create(
                model=config.get("model", "text-embedding-3-small"),
                input="test"
            )
            return ConnectionTestResponse(
                success=True,
                message="OpenAI embedding API valid",
                details={"dimensions": len(response.data[0].embedding)}
            )
        
        elif provider == "cohere":
            import cohere
            client = cohere.Client(api_key)
            response = client.embed(texts=["test"], model="embed-english-v3.0")
            return ConnectionTestResponse(
                success=True,
                message="Cohere API key valid"
            )
        
        elif provider == "voyage":
            import voyageai
            client = voyageai.Client(api_key=api_key)
            return ConnectionTestResponse(
                success=True,
                message="Voyage AI configured"
            )
        
        elif provider in ["ollama", "local"]:
            return ConnectionTestResponse(
                success=True,
                message="Local embedding provider configured"
            )
        
        else:
            return ConnectionTestResponse(
                success=False,
                message=f"Unknown provider: {provider}"
            )
    
    except Exception as e:
        return ConnectionTestResponse(
            success=False,
            message=f"Embedding API validation failed: {str(e)}"
        )
