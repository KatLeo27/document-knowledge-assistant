"""In-memory sliding-window rate limiter for FastAPI endpoints.

Designed for serverless and single-instance deployments without external
infrastructure dependencies like Redis.
"""

from __future__ import annotations

import time
from collections import defaultdict
from threading import Lock

from fastapi import HTTPException, Request, status


class SlidingWindowRateLimiter:
    """Thread-safe in-memory sliding window rate limiter."""

    def __init__(
        self,
        max_requests: int,
        window_seconds: int,
        name: str = "Action",
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.name = name
        self.lock = Lock()
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._last_cleanup = time.time()

    def _get_client_identifier(self, request: Request) -> str:
        """Extract client IP address, respecting reverse proxies."""
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        if request.client and request.client.host:
            return request.client.host
        return "127.0.0.1"

    def _cleanup_stale(self, now: float) -> None:
        """Remove expired timestamps to prevent memory growth."""
        cutoff = now - self.window_seconds
        stale_keys = []
        for key, timestamps in self._requests.items():
            valid = [ts for ts in timestamps if ts > cutoff]
            if valid:
                self._requests[key] = valid
            else:
                stale_keys.append(key)
        for key in stale_keys:
            del self._requests[key]
        self._last_cleanup = now

    def __call__(self, request: Request) -> None:
        """FastAPI dependency that enforces rate limiting per client IP."""
        now = time.time()
        client_id = self._get_client_identifier(request)

        with self.lock:
            if now - self._last_cleanup > 300:
                self._cleanup_stale(now)

            cutoff = now - self.window_seconds
            timestamps = self._requests[client_id]
            active_timestamps = [ts for ts in timestamps if ts > cutoff]

            if len(active_timestamps) >= self.max_requests:
                oldest_active = active_timestamps[0]
                if self.window_seconds >= 60:
                    window_desc = f"{self.window_seconds // 60} minute(s)"
                else:
                    window_desc = f"{self.window_seconds} second(s)"

                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"{self.name} rate limit exceeded. You are allowed at most "
                        f"{self.max_requests} requests per {window_desc}. "
                        f"Please wait {retry_after} seconds before retrying."
                    ),
                    headers={"Retry-After": str(retry_after)},
                )

            active_timestamps.append(now)
            self._requests[client_id] = active_timestamps


# Target limits: 10 queries/minute, 3 uploads/hour
query_rate_limiter = SlidingWindowRateLimiter(
    max_requests=10,
    window_seconds=60,
    name="Query",
)

upload_rate_limiter = SlidingWindowRateLimiter(
    max_requests=3,
    window_seconds=3600,
    name="Document upload",
)
