"""
Rate Limiting Service
"""

import time
import redis
from typing import Optional, Dict, Any
from src.config.settings import settings
from src.config.constants import (
    RATE_LIMIT_PER_MIN,
    RATE_LIMIT_BURST,
    RATE_LIMIT_WINDOW_S,
    MAX_CONCURRENT_JOBS_PER_IP,
)


class RateLimiter:
    """
    Sliding window rate limiter using Redis
    """

    def __init__(
        self,
        redis_url: Optional[str] = None,
        redis_client: Optional[redis.Redis] = None,
        requests_per_minute: Optional[int] = None,
        burst: Optional[int] = None,
        window_seconds: Optional[int] = None,
        raise_on_limit: Optional[bool] = None,
    ):
        """
        Initialize rate limiter

        Args:
            redis_url: Redis connection URL (defaults to settings.REDIS_URL)
        """
        self.redis_url = redis_url or settings.redis_url
        
        # In Mock Mode, we bypass Redis if it's not available
        self.mock_mode = getattr(settings, "mock_mode", False)
        
        if self.mock_mode and not redis_client:
            # Try to connect, if fails, use dummy client or just disable
            try:
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True,
                    socket_connect_timeout=1
                )
                self.redis_client.ping()
                self.redis_available = True
            except (redis.ConnectionError, redis.TimeoutError):
                self.redis_client = None
                self.redis_available = False
        else:
            self.redis_client = redis_client or redis.from_url(
                self.redis_url,
                decode_responses=True,
            )
            self.redis_available = True

        self.requests_per_minute = requests_per_minute or RATE_LIMIT_PER_MIN
        self.burst = burst or RATE_LIMIT_BURST
        self.window_seconds = window_seconds or RATE_LIMIT_WINDOW_S
        self.use_simple_counter = (
            self.redis_available
            and (
                requests_per_minute is not None
                or burst is not None
                or window_seconds is not None
            )
        )
        if raise_on_limit is None:
            self.raise_on_limit = self.use_simple_counter
        else:
            self.raise_on_limit = raise_on_limit

        # Allowlist for bypassing rate limits (e.g., testing IPs)
        self.rate_limit_allowlist: set = set()

    def check_rate_limit(
        self,
        ip: str,
        limit: int = RATE_LIMIT_PER_MIN,
        window: int = RATE_LIMIT_WINDOW_S,
        raise_on_limit: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Check if request is within rate limit
        """
        # If Redis is unavailable in Mock Mode, bypass checks
        if not self.redis_available and self.mock_mode:
            return {
                "allowed": True,
                "remaining": limit,
                "reset_at": int(time.time()) + window,
            }

        if raise_on_limit is None:
            raise_on_limit = self.raise_on_limit

        if self.use_simple_counter:
            limit = limit or self.requests_per_minute
            window = window or self.window_seconds
            key = f"ratelimit:{ip}"
            current = self.redis_client.incr(key)
            if current == 1:
                self.redis_client.expire(key, window)
            if current > limit:
                if raise_on_limit:
                    raise RateLimitError(f"Rate limit exceeded for {ip}")
                return {
                    "allowed": False,
                    "remaining": 0,
                    "reset_at": int(time.time()) + window,
                }
            remaining = max(limit - current, 0)
            return {
                "allowed": True,
                "remaining": remaining,
                "reset_at": int(time.time()) + window,
            }

        # Check allowlist
        if ip in self.rate_limit_allowlist:
            return {
                "allowed": True,
                "remaining": limit,
                "reset_at": int(time.time()) + window,
            }

        key = f"ratelimit:{ip}"
        now = time.time()
        window_start = now - window

        # Remove timestamps outside current window
        self.redis_client.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        current_count = self.redis_client.zcard(key)

        if current_count < limit:
            # Add current request
            self.redis_client.zadd(key, {str(now): now})
            self.redis_client.expire(key, window)
            remaining = limit - (current_count + 1)
            reset_at = int(now) + window
            return {
                "allowed": True,
                "remaining": remaining,
                "reset_at": reset_at,
            }
        else:
            # Rate limit exceeded
            oldest_request = self.redis_client.zrange(key, 0, 0, withscores=True)
            reset_at = int(oldest_request[0][1]) + window if oldest_request else int(now) + window
            return {
                "allowed": False,
                "remaining": 0,
                "reset_at": reset_at,
            }

    def check_concurrent_jobs(
        self,
        ip: str,
        max_concurrent: Optional[int] = None,
        raise_on_limit: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Check if IP is within concurrent job limit

        Args:
            ip: Client IP address

        Returns:
            Dict with {
                "allowed": bool,
                "current": int,
                "max": int
            }
        """
        # If Redis is unavailable in Mock Mode, bypass checks
        if not self.redis_available and self.mock_mode:
            return {
                "allowed": True,
                "current": 0,
                "max": max_concurrent or MAX_CONCURRENT_JOBS_PER_IP,
            }

        key = f"concurrent:{ip}"
        current = self.redis_client.get(key)

        if current is None:
            current = 0
        else:
            current = int(current)

        if max_concurrent is None:
            max_concurrent = MAX_CONCURRENT_JOBS_PER_IP
        if raise_on_limit is None:
            raise_on_limit = self.raise_on_limit

        if current < max_concurrent:
            return {
                "allowed": True,
                "current": current,
                "max": max_concurrent,
            }

        if raise_on_limit:
            raise RateLimitError(
                f"Concurrent job limit exceeded for {ip} (max {max_concurrent})"
            )

        return {
            "allowed": False,
            "current": current,
            "max": max_concurrent,
        }

    def increment_concurrent_jobs(self, ip: str) -> int:
        """
        Increment concurrent job count for IP

        Args:
            ip: Client IP address

        Returns:
            New concurrent job count
        """
        if not self.redis_available and self.mock_mode:
            return 1

        key = f"concurrent:{ip}"
        return self.redis_client.incr(key)

    def decrement_concurrent_jobs(self, ip: str) -> int:
        """
        Decrement concurrent job count for IP

        Args:
            ip: Client IP address

        Returns:
            New concurrent job count
        """
        if not self.redis_available and self.mock_mode:
            return 0

        key = f"concurrent:{ip}"
        new_value = self.redis_client.decr(key)

        # Clean up if count reaches zero
        if new_value <= 0:
            self.redis_client.delete(key)
            return 0

        return new_value

    def add_to_allowlist(self, ip: str) -> None:
        """
        Add IP to rate limit allowlist

        Args:
            ip: Client IP address
        """
        self.rate_limit_allowlist.add(ip)

    def remove_from_allowlist(self, ip: str) -> None:
        """
        Remove IP from rate limit allowlist

        Args:
            ip: Client IP address
        """
        self.rate_limit_allowlist.discard(ip)

    def increment_request_count(self, ip: str) -> int:
        """Increment request count in a simple counter mode."""
        if not self.redis_available and self.mock_mode:
            return 1

        key = f"ratelimit:{ip}"
        count = self.redis_client.incr(key)
        self.redis_client.expire(key, self.window_seconds)
        return count

    def get_request_count(self, ip: str) -> int:
        """Get current request count."""
        if not self.redis_available and self.mock_mode:
            return 0

        key = f"ratelimit:{ip}"
        value = self.redis_client.get(key)
        return int(value) if value is not None else 0

    def increment_job_count(self, ip: str) -> int:
        """Increment concurrent job count."""
        if not self.redis_available and self.mock_mode:
            return 1

        key = f"concurrent:{ip}"
        return self.redis_client.incr(key)

    def decrement_job_count(self, ip: str) -> int:
        """Decrement concurrent job count."""
        if not self.redis_available and self.mock_mode:
            return 0

        key = f"concurrent:{ip}"
        return self.redis_client.decr(key)

    def get_job_count(self, ip: str) -> int:
        """Get current concurrent job count."""
        if not self.redis_available and self.mock_mode:
            return 0

        key = f"concurrent:{ip}"
        value = self.redis_client.get(key)
        return int(value) if value is not None else 0

    def reset_rate_limit(self, ip: str) -> None:
        """Reset rate limit counters for an IP."""
        if not self.redis_available and self.mock_mode:
            return

        self.redis_client.delete(f"ratelimit:{ip}")


class RateLimitError(Exception):
    """Rate limiting error."""

    pass
