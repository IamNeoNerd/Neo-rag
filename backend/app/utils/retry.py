"""
Retry utilities for Neo-rag API.

Provides exponential backoff retry logic for external API calls,
particularly for LLM providers that may have rate limits or transient failures.
"""
import time
import random
import logging
import functools
from typing import TypeVar, Callable, Optional, Tuple, Type, Any

from ..exceptions import (
    LLMRateLimitError,
    LLMTimeoutError,
    LLMApiKeyError,
    NeoRagException,
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


def exponential_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    retryable_exceptions: Tuple[Type[Exception], ...] = (Exception,),
    non_retryable_exceptions: Tuple[Type[Exception], ...] = (LLMApiKeyError,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Decorator that implements exponential backoff retry logic.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        exponential_base: Base for exponential calculation
        jitter: Add random jitter to prevent thundering herd
        retryable_exceptions: Tuple of exceptions that trigger retry
        non_retryable_exceptions: Exceptions that should never be retried
    
    Returns:
        Decorated function with retry logic
    
    Example:
        @exponential_backoff(max_retries=3, base_delay=1.0)
        def call_openai_api():
            # API call that might fail
            pass
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except non_retryable_exceptions as e:
                    # These exceptions should not be retried
                    logger.error(f"{func.__name__} failed with non-retryable error: {e}")
                    raise
                    
                except retryable_exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"{func.__name__} failed after {max_retries + 1} attempts: {e}"
                        )
                        raise
                    
                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    # Add jitter (up to 25% of delay)
                    if jitter:
                        delay = delay * (0.75 + random.random() * 0.5)
                    
                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
            
            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__} failed unexpectedly")
        
        return wrapper
    return decorator


def retry_llm_call(
    max_retries: int = 3,
    base_delay: float = 1.0,
    provider: str = "unknown"
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Specialized retry decorator for LLM API calls.
    
    Handles common LLM provider errors like rate limits and timeouts.
    
    Args:
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        provider: LLM provider name for logging
    
    Returns:
        Decorated function with LLM-specific retry logic
    """
    # Import here to avoid circular dependencies
    import openai
    
    # Define retryable exceptions for LLM calls
    retryable = (
        openai.RateLimitError,
        openai.APIConnectionError,
        openai.APITimeoutError,
        openai.InternalServerError,
        ConnectionError,
        TimeoutError,
    )
    
    # Non-retryable (auth errors, bad requests)
    non_retryable = (
        openai.AuthenticationError,
        openai.BadRequestError,
        LLMApiKeyError,
    )
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: Optional[Exception] = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except non_retryable as e:
                    logger.error(f"[{provider}] Non-retryable error in {func.__name__}: {e}")
                    if isinstance(e, openai.AuthenticationError):
                        raise LLMApiKeyError(provider) from e
                    raise
                    
                except retryable as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"[{provider}] {func.__name__} failed after {max_retries + 1} attempts"
                        )
                        if isinstance(e, openai.RateLimitError):
                            raise LLMRateLimitError(provider) from e
                        if isinstance(e, (openai.APITimeoutError, TimeoutError)):
                            raise LLMTimeoutError(provider) from e
                        raise
                    
                    # Calculate delay
                    delay = base_delay * (2 ** attempt)
                    delay = delay * (0.75 + random.random() * 0.5)  # Add jitter
                    
                    logger.warning(
                        f"[{provider}] {func.__name__} attempt {attempt + 1} failed. "
                        f"Retrying in {delay:.2f}s..."
                    )
                    
                    time.sleep(delay)
            
            if last_exception:
                raise last_exception
            raise RuntimeError(f"{func.__name__} failed unexpectedly")
        
        return wrapper
    return decorator


class RetryContext:
    """
    Context manager for retry logic with manual control.
    
    Use when you need more control over the retry behavior than
    decorators provide.
    
    Example:
        with RetryContext(max_retries=3) as retry:
            while retry.should_continue():
                try:
                    result = api_call()
                    break
                except Exception as e:
                    retry.record_failure(e)
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        operation_name: str = "operation"
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.operation_name = operation_name
        self.attempt = 0
        self.last_exception: Optional[Exception] = None
    
    def __enter__(self) -> 'RetryContext':
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False  # Don't suppress exceptions
    
    def should_continue(self) -> bool:
        """Check if retry should continue."""
        return self.attempt <= self.max_retries
    
    def record_failure(self, exception: Exception) -> None:
        """Record a failure and wait before next retry."""
        self.last_exception = exception
        
        if self.attempt >= self.max_retries:
            logger.error(
                f"{self.operation_name} failed after {self.max_retries + 1} attempts"
            )
            raise exception
        
        delay = min(
            self.base_delay * (2 ** self.attempt),
            self.max_delay
        )
        delay = delay * (0.75 + random.random() * 0.5)
        
        logger.warning(
            f"{self.operation_name} attempt {self.attempt + 1} failed: {exception}. "
            f"Retrying in {delay:.2f}s..."
        )
        
        time.sleep(delay)
        self.attempt += 1
