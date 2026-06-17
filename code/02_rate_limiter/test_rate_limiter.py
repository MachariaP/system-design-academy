import time
import pytest
from rate_limiter import TokenBucket, SlidingWindowLog


class TestTokenBucket:
    def test_burst_absorption(self):
        bucket = TokenBucket(capacity=10, refill_rate=10, refill_interval=1.0)
        allowed = sum(bucket.allow_request() for _ in range(10))
        assert allowed == 10
        assert not bucket.allow_request()

    def test_refill_over_time(self):
        bucket = TokenBucket(capacity=5, refill_rate=5, refill_interval=1.0)
        for _ in range(5):
            bucket.allow_request()
        time.sleep(1.05)
        assert bucket.allow_request()

    def test_steady_state(self):
        bucket = TokenBucket(capacity=1, refill_rate=1, refill_interval=0.1)
        allowed = 0
        for _ in range(20):
            if bucket.allow_request():
                allowed += 1
            time.sleep(0.05)
        assert allowed >= 8


class TestSlidingWindowLog:
    def test_within_limit(self):
        sw = SlidingWindowLog(window_size_ms=1000, max_requests=5)
        for _ in range(5):
            assert sw.allow_request()

    def test_exceeds_limit(self):
        sw = SlidingWindowLog(window_size_ms=1000, max_requests=3)
        for _ in range(3):
            sw.allow_request()
        assert not sw.allow_request()

    def test_window_boundary(self):
        sw = SlidingWindowLog(window_size_ms=200, max_requests=2)
        assert sw.allow_request()
        assert sw.allow_request()
        assert not sw.allow_request()
        time.sleep(0.25)
        assert sw.allow_request()
