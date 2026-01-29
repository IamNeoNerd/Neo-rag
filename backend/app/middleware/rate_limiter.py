"""
Rate limiting middleware for Neo-rag API.

Implements a sliding window rate limiter to prevent abuse and ensure
fair resource allocation across clients.
"""
import time
import logging
from typing import Dict, Tuple, Optional
from collections import defaultdict
from threading import Lock
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Thread-safe sliding window rate limiter.
    
    Tracks request counts per client IP using a sliding window algorithm
    for more accurate rate limiting than fixed windows.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_limit: int = 10
    ):
        """
        Initialize the rate limiter.
        
        Args:
            requests_per_minute: Maximum requests allowed per minute per client
            requests_per_hour: Maximum requests allowed per hour per client
            burst_limit: Maximum concurrent requests in a short burst
        """
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.burst_limit = burst_limit
        
        # Track requests: {client_ip: [(timestamp, count), ...]}
        self._minute_windows: Dict[str, list] = defaultdict(list)
        self._hour_windows: Dict[str, list] = defaultdict(list)
        self._burst_tracker: Dict[str, Tuple[float, int]] = {}
        self._lock = Lock()
        
    def _clean_old_entries(self, entries: list, window_seconds: int) -> list:
        """Remove entries older than the window."""
        cutoff = time.time() - window_seconds
        return [e for e in entries if e[0] > cutoff]
    
    def _count_requests(self, entries: list) -> int:
        """Count total requests in entries."""
        return sum(count for _, count in entries)
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if a request from this client is allowed.
        
        Args:
            client_ip: The client's IP address
            
        Returns:
            Tuple of (is_allowed, error_message, retry_after_seconds)
        """
        with self._lock:
            now = time.time()
            
            # Clean old entries
            self._minute_windows[client_ip] = self._clean_old_entries(
                self._minute_windows[client_ip], 60
            )
            self._hour_windows[client_ip] = self._clean_old_entries(
                self._hour_windows[client_ip], 3600
            )
            
            # Check minute limit
            minute_count = self._count_requests(self._minute_windows[client_ip])
            if minute_count >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded (minute) for {client_ip}")
                return False, "Too many requests per minute", 60
            
            # Check hour limit
            hour_count = self._count_requests(self._hour_windows[client_ip])
            if hour_count >= self.requests_per_hour:
                logger.warning(f"Rate limit exceeded (hour) for {client_ip}")
                return False, "Too many requests per hour", 3600
            
            # Check burst limit (10 requests in 1 second)
            if client_ip in self._burst_tracker:
                burst_time, burst_count = self._burst_tracker[client_ip]
                if now - burst_time < 1.0:
                    if burst_count >= self.burst_limit:
                        logger.warning(f"Burst limit exceeded for {client_ip}")
                        return False, "Too many requests in burst", 1
                    self._burst_tracker[client_ip] = (burst_time, burst_count + 1)
                else:
                    self._burst_tracker[client_ip] = (now, 1)
            else:
                self._burst_tracker[client_ip] = (now, 1)
            
            # Record the request
            self._minute_windows[client_ip].append((now, 1))
            self._hour_windows[client_ip].append((now, 1))
            
            return True, None, None
    
    def get_client_stats(self, client_ip: str) -> Dict:
        """Get rate limit stats for a client."""
        with self._lock:
            now = time.time()
            
            minute_entries = self._clean_old_entries(
                self._minute_windows.get(client_ip, []), 60
            )
            hour_entries = self._clean_old_entries(
                self._hour_windows.get(client_ip, []), 3600
            )
            
            return {
                "requests_this_minute": self._count_requests(minute_entries),
                "requests_this_hour": self._count_requests(hour_entries),
                "limit_per_minute": self.requests_per_minute,
                "limit_per_hour": self.requests_per_hour
            }


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=60,
    requests_per_hour=1000,
    burst_limit=10
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting requests.
    
    Applies rate limits based on client IP address.
    Excludes health check and docs endpoints from rate limiting.
    """
    
    # Paths excluded from rate limiting
    EXCLUDED_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc"}
    
    async def dispatch(self, request: Request, call_next):
        """Process the request and apply rate limiting."""
        path = request.url.path
        
        # Skip rate limiting for excluded paths
        if path in self.EXCLUDED_PATHS:
            return await call_next(request)
        
        # Get client IP (handle proxy headers)
        client_ip = self._get_client_ip(request)
        
        # Check rate limit
        is_allowed, error_msg, retry_after = rate_limiter.is_allowed(client_ip)
        
        if not is_allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "detail": error_msg,
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        stats = rate_limiter.get_client_stats(client_ip)
        response.headers["X-RateLimit-Limit"] = str(stats["limit_per_minute"])
        response.headers["X-RateLimit-Remaining"] = str(
            max(0, stats["limit_per_minute"] - stats["requests_this_minute"])
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP, handling reverse proxies."""
        # Check for forwarded headers (reverse proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            # Take the first IP in the chain (original client)
            return forwarded.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
