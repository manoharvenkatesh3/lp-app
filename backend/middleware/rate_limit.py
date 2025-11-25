"""Rate limiting middleware for API endpoints."""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import HTTPException, Request, status

# In-memory storage for rate limiting (use Redis in production)
_rate_limit_storage: Dict[str, Tuple[int, float]] = defaultdict(lambda: (0, 0.0))


class RateLimiter:
    """Simple rate limiter using sliding window."""
    
    def __init__(self, requests: int = 100, window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            requests: Maximum number of requests allowed
            window: Time window in seconds
        """
        self.requests = requests
        self.window = window
    
    def check_rate_limit(self, key: str) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            key: Unique identifier for rate limiting (e.g., API key, IP address)
        
        Returns:
            True if within limit, False otherwise
        """
        current_time = time.time()
        count, window_start = _rate_limit_storage[key]
        
        # Reset if window has passed
        if current_time - window_start > self.window:
            _rate_limit_storage[key] = (1, current_time)
            return True
        
        # Increment count if within window
        if count < self.requests:
            _rate_limit_storage[key] = (count + 1, window_start)
            return True
        
        return False
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests in current window."""
        current_time = time.time()
        count, window_start = _rate_limit_storage.get(key, (0, current_time))
        
        if current_time - window_start > self.window:
            return self.requests
        
        return max(0, self.requests - count)
    
    def get_reset_time(self, key: str) -> float:
        """Get time when rate limit resets."""
        current_time = time.time()
        _, window_start = _rate_limit_storage.get(key, (0, current_time))
        return window_start + self.window


async def rate_limit_dependency(
    request: Request, limiter: RateLimiter = RateLimiter()
) -> None:
    """
    FastAPI dependency for rate limiting.
    
    Uses API key from header or IP address as identifier.
    """
    # Try to get API key from header
    api_key = request.headers.get("X-API-Key")
    if api_key:
        key = f"api_key:{api_key}"
    else:
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        key = f"ip:{client_ip}"
    
    if not limiter.check_rate_limit(key):
        reset_time = limiter.get_reset_time(key)
        retry_after = int(reset_time - time.time())
        
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
            headers={
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(limiter.requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset_time)),
            },
        )


class ATSRateLimiter(RateLimiter):
    """Rate limiter specifically for ATS API endpoints."""
    
    def __init__(self):
        # More generous limits for ATS integrations
        super().__init__(requests=1000, window=3600)  # 1000 requests per hour


ats_rate_limiter = ATSRateLimiter()


async def ats_rate_limit_dependency(request: Request) -> None:
    """Rate limiting for ATS endpoints."""
    await rate_limit_dependency(request, ats_rate_limiter)
