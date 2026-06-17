import time
from typing import Callable, Any


class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open."""


class CircuitBreaker:
    """State-machine circuit breaker: CLOSED -> OPEN -> HALF_OPEN."""

    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

    def __init__(self, failure_threshold: int, recovery_timeout: float) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time: float = 0.0

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Invoke func if circuit is closed or half-open; raise otherwise."""
        if self.state == self.OPEN:
            if time.monotonic() - self.last_failure_time >= self.recovery_timeout:
                self.state = self.HALF_OPEN
            else:
                raise CircuitBreakerOpenError("Circuit breaker is OPEN")

        try:
            result = func(*args, **kwargs)
        except Exception:
            self.failure_count += 1
            self.last_failure_time = time.monotonic()
            if self.failure_count >= self.failure_threshold:
                self.state = self.OPEN
            raise

        if self.state == self.HALF_OPEN:
            self.state = self.CLOSED
            self.failure_count = 0

        return result

    def reset(self) -> None:
        """Manually reset the circuit breaker to closed state."""
        self.state = self.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0
