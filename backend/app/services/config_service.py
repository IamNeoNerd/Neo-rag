"""
Configuration Service

Centralized configuration management that:
1. Loads defaults from .env
2. Can be overridden by frontend-provided config
3. Persists user config to a local JSON file
4. Provides typed access to all config values
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from functools import lru_cache

logger = logging.getLogger(__name__)

# Config file path (in project root)
CONFIG_FILE = Path(__file__).parent.parent.parent.parent / "config.json"


class LLMConfig(BaseModel):
    """LLM provider configuration."""
    provider: str = "openai"
    api_key: str = ""
    model: str = "gpt-4-turbo"
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


class EmbeddingConfig(BaseModel):
    """Embedding provider configuration."""
    provider: str = "openai"
    api_key: str = ""
    model: str = "text-embedding-3-small"
    base_url: Optional[str] = None


class NeonConfig(BaseModel):
    """Neon PostgreSQL configuration."""
    connection_string: str = ""


class Neo4jConfig(BaseModel):
    """Neo4j configuration."""
    uri: str = ""
    username: str = "neo4j"
    password: str = ""


class AppConfig(BaseModel):
    """Complete application configuration."""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    neon: NeonConfig = Field(default_factory=NeonConfig)
    neo4j: Neo4jConfig = Field(default_factory=Neo4jConfig)
    is_configured: bool = False


class ConfigService:
    """
    Singleton service for managing application configuration.
    
    Priority order:
    1. Request-level overrides (API keys in headers)
    2. Saved config (config.json)
    3. Environment variables (.env)
    """
    
    _instance: Optional["ConfigService"] = None
    _config: Optional[AppConfig] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._config is None:
            self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from file or environment."""
        # Try loading from config file first
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    self._config = AppConfig(**data)
                    logger.info("Loaded configuration from config.json")
                    return
            except Exception as e:
                logger.warning(f"Failed to load config.json: {e}")
        
        # Fall back to environment variables
        self._config = AppConfig(
            llm=LLMConfig(
                provider=os.getenv("LLM_PROVIDER", "openai"),
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=os.getenv("LLM_MODEL", "gpt-4-turbo"),
            ),
            embedding=EmbeddingConfig(
                provider=os.getenv("EMBEDDING_PROVIDER", "openai"),
                api_key=os.getenv("OPENAI_API_KEY", ""),
                model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            ),
            neon=NeonConfig(
                connection_string=os.getenv("NEON_DATABASE_URL", ""),
            ),
            neo4j=Neo4jConfig(
                uri=os.getenv("NEO4J_URI", ""),
                username=os.getenv("NEO4J_USERNAME", "neo4j"),
                password=os.getenv("NEO4J_PASSWORD", ""),
            ),
            is_configured=bool(os.getenv("NEON_DATABASE_URL")),
        )
        logger.info("Loaded configuration from environment variables")
    
    def save_config(self, config: AppConfig) -> None:
        """Persist configuration to file."""
        self._config = config
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config.model_dump(), f, indent=2)
            logger.info("Configuration saved to config.json")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise
    
    def get_config(self) -> AppConfig:
        """Get current configuration."""
        if self._config is None:
            self._load_config()
        return self._config
    
    def get_masked_config(self) -> Dict[str, Any]:
        """Get config with API keys masked (for frontend display)."""
        config = self.get_config()
        
        def mask_key(key: str) -> str:
            if not key or len(key) < 8:
                return "••••••••"
            return f"{key[:4]}...{key[-4:]}"
        
        return {
            "llm": {
                "provider": config.llm.provider,
                "api_key": mask_key(config.llm.api_key),
                "model": config.llm.model,
                "has_key": bool(config.llm.api_key),
            },
            "embedding": {
                "provider": config.embedding.provider,
                "api_key": mask_key(config.embedding.api_key),
                "model": config.embedding.model,
                "has_key": bool(config.embedding.api_key),
            },
            "neon": {
                "connection_string": mask_key(config.neon.connection_string),
                "is_configured": bool(config.neon.connection_string),
            },
            "neo4j": {
                "uri": config.neo4j.uri,
                "username": config.neo4j.username,
                "is_configured": bool(config.neo4j.uri and config.neo4j.password),
            },
            "is_configured": config.is_configured,
        }
    
    def update_config(self, updates: Dict[str, Any]) -> AppConfig:
        """Update configuration with partial data."""
        current = self.get_config().model_dump()
        
        # Deep merge updates
        for key, value in updates.items():
            if key in current and isinstance(value, dict):
                current[key].update(value)
            else:
                current[key] = value
        
        new_config = AppConfig(**current)
        self.save_config(new_config)
        return new_config
    
    # Convenience accessors
    def get_llm_api_key(self, override: Optional[str] = None) -> str:
        """Get LLM API key, with optional request-level override."""
        return override or self.get_config().llm.api_key
    
    def get_embedding_api_key(self, override: Optional[str] = None) -> str:
        """Get embedding API key, with optional request-level override."""
        return override or self.get_config().embedding.api_key
    
    def get_neon_url(self) -> str:
        """Get Neon connection string."""
        return self.get_config().neon.connection_string or os.getenv("NEON_DATABASE_URL", "")
    
    def get_neo4j_config(self) -> Dict[str, str]:
        """Get Neo4j connection details."""
        config = self.get_config()
        return {
            "uri": config.neo4j.uri or os.getenv("NEO4J_URI", ""),
            "username": config.neo4j.username or os.getenv("NEO4J_USERNAME", "neo4j"),
            "password": config.neo4j.password or os.getenv("NEO4J_PASSWORD", ""),
        }


# Singleton instance
config_service = ConfigService()


def get_config_service() -> ConfigService:
    """Get the config service instance (for dependency injection)."""
    return config_service
