"""
Chunking Service

Provides multiple text chunking strategies for document ingestion:
1. Fixed-size chunking (RecursiveCharacterTextSplitter)
2. Semantic chunking (embedding-based breakpoints)
3. Markdown-aware chunking
4. Code-aware chunking

Each strategy is optimized for different content types.
"""
import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict, Any

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    Language,
    RecursiveCharacterTextSplitter as CodeSplitter,
)
from langchain_core.documents import Document
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ChunkingStrategy(str, Enum):
    """Available chunking strategies."""
    RECURSIVE = "recursive"      # Default: recursive character splitting
    SEMANTIC = "semantic"        # Embedding-based semantic boundaries
    MARKDOWN = "markdown"        # Markdown structure-aware
    CODE = "code"               # Programming language-aware


class ChunkingConfig(BaseModel):
    """Configuration for chunking behavior."""
    strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE
    chunk_size: int = 1000
    chunk_overlap: int = 200
    language: Optional[str] = None  # For code splitting: python, javascript, etc.
    min_chunk_size: int = 100       # Minimum chunk size for semantic chunking
    

class ChunkResult(BaseModel):
    """Result of chunking operation."""
    chunks: List[str]
    strategy_used: str
    chunk_count: int
    avg_chunk_size: float


class BaseChunker(ABC):
    """Abstract base class for chunking strategies."""
    
    @abstractmethod
    def chunk(self, text: str, config: ChunkingConfig) -> List[str]:
        """Split text into chunks using the specific strategy."""
        pass


class RecursiveChunker(BaseChunker):
    """
    Recursive character text splitting.
    
    Splits on natural boundaries (paragraphs, sentences, words) recursively
    until chunks are under the size limit.
    """
    
    def chunk(self, text: str, config: ChunkingConfig) -> List[str]:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        return splitter.split_text(text)


class MarkdownChunker(BaseChunker):
    """
    Markdown-aware chunking.
    
    Respects markdown structure (headers, code blocks, lists) when splitting.
    """
    
    def chunk(self, text: str, config: ChunkingConfig) -> List[str]:
        splitter = MarkdownTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )
        return splitter.split_text(text)


class CodeChunker(BaseChunker):
    """
    Programming language-aware chunking.
    
    Respects code structure (functions, classes, blocks) when splitting.
    """
    
    LANGUAGE_MAP = {
        "python": Language.PYTHON,
        "javascript": Language.JS,
        "typescript": Language.TS,
        "java": Language.JAVA,
        "go": Language.GO,
        "rust": Language.RUST,
        "cpp": Language.CPP,
        "c": Language.C,
    }
    
    def chunk(self, text: str, config: ChunkingConfig) -> List[str]:
        lang = config.language or "python"
        lang_enum = self.LANGUAGE_MAP.get(lang.lower(), Language.PYTHON)
        
        splitter = RecursiveCharacterTextSplitter.from_language(
            language=lang_enum,
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
        )
        return splitter.split_text(text)


class SemanticChunker(BaseChunker):
    """
    Embedding-based semantic chunking.
    
    Uses embeddings to find natural semantic boundaries in text.
    Chunks are created where the semantic similarity between sentences drops.
    
    This is more expensive (requires embedding calls) but produces
    more coherent chunks.
    """
    
    def __init__(self, embedding_service=None):
        """
        Initialize semantic chunker.
        
        Args:
            embedding_service: Service to generate embeddings. 
                               If None, falls back to recursive chunking.
        """
        self.embedding_service = embedding_service
    
    def chunk(self, text: str, config: ChunkingConfig) -> List[str]:
        if not self.embedding_service:
            logger.warning("No embedding service available, falling back to recursive chunking")
            return RecursiveChunker().chunk(text, config)
        
        # Split into sentences first
        sentences = self._split_into_sentences(text)
        if len(sentences) <= 1:
            return [text] if text.strip() else []
        
        # Generate embeddings for each sentence
        try:
            embeddings = self.embedding_service.generate_embeddings(sentences)
        except Exception as e:
            logger.warning(f"Embedding generation failed: {e}, falling back to recursive")
            return RecursiveChunker().chunk(text, config)
        
        # Find semantic breakpoints
        breakpoints = self._find_semantic_breakpoints(
            sentences, 
            embeddings, 
            config.chunk_size,
            config.min_chunk_size
        )
        
        # Group sentences into chunks based on breakpoints
        chunks = []
        current_chunk = []
        current_size = 0
        
        for i, sentence in enumerate(sentences):
            current_chunk.append(sentence)
            current_size += len(sentence)
            
            if i in breakpoints or current_size >= config.chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        import re
        # Simple sentence splitting on ., !, ?
        sentences = re.split(r'(?<=[.!?])\s+', text.strip())
        return [s.strip() for s in sentences if s.strip()]
    
    def _find_semantic_breakpoints(
        self, 
        sentences: List[str], 
        embeddings: List[List[float]], 
        max_chunk_size: int,
        min_chunk_size: int
    ) -> set:
        """
        Find indices where semantic similarity drops significantly.
        
        These are natural breakpoints for chunking.
        """
        if len(embeddings) < 2:
            return set()
        
        import numpy as np
        
        breakpoints = set()
        similarities = []
        
        # Calculate cosine similarity between consecutive sentences
        for i in range(len(embeddings) - 1):
            sim = self._cosine_similarity(embeddings[i], embeddings[i + 1])
            similarities.append(sim)
        
        if not similarities:
            return set()
        
        # Find breakpoints where similarity drops below threshold
        avg_sim = np.mean(similarities)
        std_sim = np.std(similarities)
        threshold = avg_sim - std_sim  # One standard deviation below mean
        
        current_size = 0
        for i, sim in enumerate(similarities):
            current_size += len(sentences[i])
            
            # Add breakpoint if similarity drops and we have enough content
            if sim < threshold and current_size >= min_chunk_size:
                breakpoints.add(i)
                current_size = 0
        
        return breakpoints
    
    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        import numpy as np
        v1, v2 = np.array(v1), np.array(v2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))


class ChunkingService:
    """
    Main chunking service that orchestrates different strategies.
    
    Usage:
        service = ChunkingService()
        result = service.chunk_text(text, ChunkingConfig(strategy="semantic"))
    """
    
    def __init__(self, embedding_service=None):
        self.chunkers = {
            ChunkingStrategy.RECURSIVE: RecursiveChunker(),
            ChunkingStrategy.MARKDOWN: MarkdownChunker(),
            ChunkingStrategy.CODE: CodeChunker(),
            ChunkingStrategy.SEMANTIC: SemanticChunker(embedding_service),
        }
    
    def chunk_text(
        self, 
        text: str, 
        config: Optional[ChunkingConfig] = None
    ) -> ChunkResult:
        """
        Chunk text using the specified strategy.
        
        Args:
            text: The text to chunk.
            config: Configuration for chunking behavior.
        
        Returns:
            ChunkResult with chunks and metadata.
        """
        if config is None:
            config = ChunkingConfig()
        
        if not text or not text.strip():
            return ChunkResult(
                chunks=[],
                strategy_used=config.strategy.value,
                chunk_count=0,
                avg_chunk_size=0.0
            )
        
        chunker = self.chunkers.get(config.strategy, self.chunkers[ChunkingStrategy.RECURSIVE])
        
        try:
            chunks = chunker.chunk(text, config)
        except Exception as e:
            logger.error(f"Chunking failed with {config.strategy}: {e}, falling back to recursive")
            chunks = self.chunkers[ChunkingStrategy.RECURSIVE].chunk(text, config)
        
        # Filter empty chunks
        chunks = [c for c in chunks if c.strip()]
        
        avg_size = sum(len(c) for c in chunks) / len(chunks) if chunks else 0.0
        
        logger.info(
            f"Chunked text into {len(chunks)} chunks using {config.strategy.value} "
            f"(avg size: {avg_size:.0f} chars)"
        )
        
        return ChunkResult(
            chunks=chunks,
            strategy_used=config.strategy.value,
            chunk_count=len(chunks),
            avg_chunk_size=avg_size
        )
    
    def detect_content_type(self, text: str) -> ChunkingStrategy:
        """
        Auto-detect the best chunking strategy based on content.
        
        Args:
            text: The text to analyze.
        
        Returns:
            Recommended ChunkingStrategy.
        """
        # Check for markdown
        if any(marker in text for marker in ["# ", "## ", "```", "- [ ]", "* "]):
            return ChunkingStrategy.MARKDOWN
        
        # Check for code patterns
        code_indicators = ["def ", "class ", "function ", "import ", "const ", "let ", "var "]
        code_count = sum(1 for ind in code_indicators if ind in text)
        if code_count >= 2:
            return ChunkingStrategy.CODE
        
        # Default to recursive
        return ChunkingStrategy.RECURSIVE
