import time
from collections import deque
from typing import Deque


class TokenBucket:
    """Token bucket rate limiter."""

    def __init__(self, capacity: int, refill_rate: float, refill_interval: float) -> None:
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.refill_interval = refill_interval
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        added = (elapsed / self.refill_interval) * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + added)
        self.last_refill = now

    def allow_request(self) -> bool:
        """Check if a request is allowed, consuming one token if so."""
        self._refill()
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return True
        return False


class SlidingWindowLog:
    """Sliding window log rate limiter using a deque of timestamps."""

    def __init__(self, window_size_ms: float, max_requests: int) -> None:
        self.window_size_ms = window_size_ms
        self.max_requests = max_requests
        self.log: Deque[float] = deque()

    def allow_request(self) -> bool:
        """Check if a request is allowed within the sliding window."""
        now = time.monotonic()
        cutoff = now - (self.window_size_ms / 1000.0)
        while self.log and self.log[0] < cutoff:
            self.log.popleft()
        if len(self.log) < self.max_requests:
            self.log.append(now)
            return True
        return False
