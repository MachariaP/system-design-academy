import math
import pytest
from bloom_filter import BloomFilter


class TestBloomFilter:
    def test_no_false_negatives(self):
        bf = BloomFilter(capacity=1000, error_rate=0.01)
        items = [f"item{i}" for i in range(500)]
        for item in items:
            bf.add(item)
        for item in items:
            assert bf.check(item)

    def test_false_positives_within_bounds(self):
        bf = BloomFilter(capacity=1000, error_rate=0.05)
        for i in range(800):
            bf.add(f"key{i}")
        fp = 0
        trials = 2000
        for i in range(trials):
            if bf.check(f"nope{i}"):
                fp += 1
        measured = fp / trials
        theoretical = bf.estimate_fpp()
        assert measured <= theoretical * 2 + 0.05

    def test_estimate_fpp(self):
        bf = BloomFilter(capacity=100, error_rate=0.1)
        bf.add("a")
        est = bf.estimate_fpp()
        assert 0 < est < 0.5

    def test_empty_filter(self):
        bf = BloomFilter(capacity=100, error_rate=0.01)
        assert not bf.check("anything")

    def test_invalid_params(self):
        with pytest.raises(ValueError):
            BloomFilter(capacity=0, error_rate=0.01)
        with pytest.raises(ValueError):
            BloomFilter(capacity=100, error_rate=0)
        with pytest.raises(ValueError):
            BloomFilter(capacity=100, error_rate=1)
