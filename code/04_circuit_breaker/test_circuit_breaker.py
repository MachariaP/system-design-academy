import time
import pytest
from circuit_breaker import CircuitBreaker, CircuitBreakerOpenError


class TestCircuitBreaker:
    def test_closed_passes(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)
        result = cb.call(lambda: "ok")
        assert result == "ok"

    def test_trips_after_n_failures(self):
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)
        for _ in range(3):
            with pytest.raises(ValueError):
                cb.call(ValueError)
        assert cb.state == cb.OPEN

    def test_rejects_during_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=5.0)
        with pytest.raises(ValueError):
            cb.call(ValueError)
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(lambda: "should not run")

    def test_allows_probe_after_timeout(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.2)
        with pytest.raises(ValueError):
            cb.call(ValueError)
        time.sleep(0.25)
        result = cb.call(lambda: "probe")
        assert result == "probe"
        assert cb.state == cb.CLOSED

    def test_half_open_failure_goes_back_to_open(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.2)
        with pytest.raises(ValueError):
            cb.call(ValueError)
        time.sleep(0.25)
        with pytest.raises(RuntimeError):
            cb.call(lambda: (_ for _ in ()).throw(RuntimeError))
        assert cb.state == cb.OPEN

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=10.0)
        with pytest.raises(ValueError):
            cb.call(ValueError)
        with pytest.raises(ValueError):
            cb.call(ValueError)
        assert cb.state == cb.OPEN
        cb.reset()
        assert cb.state == cb.CLOSED
        assert cb.call(lambda: "ok") == "ok"
