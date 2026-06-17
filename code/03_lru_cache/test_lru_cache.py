import pytest
from lru_cache import LRUCache


class TestLRUCache:
    def test_get_missing(self):
        cache = LRUCache[int, str](2)
        assert cache.get(1) is None

    def test_put_and_get(self):
        cache = LRUCache[str, int](3)
        cache.put("a", 1)
        assert cache.get("a") == 1

    def test_eviction_order(self):
        cache = LRUCache[str, str](2)
        cache.put("a", "1")
        cache.put("b", "2")
        cache.put("c", "3")
        assert cache.get("a") is None
        assert cache.get("b") == "2"
        assert cache.get("c") == "3"

    def test_update_moves_to_front(self):
        cache = LRUCache[str, str](2)
        cache.put("a", "1")
        cache.put("b", "2")
        cache.get("a")
        cache.put("c", "3")
        assert cache.get("b") is None
        assert cache.get("a") == "1"
        assert cache.get("c") == "3"

    def test_update_value(self):
        cache = LRUCache[str, str](2)
        cache.put("a", "1")
        cache.put("a", "2")
        assert cache.get("a") == "2"

    def test_capacity_one(self):
        cache = LRUCache[str, str](1)
        cache.put("a", "1")
        cache.put("b", "2")
        assert cache.get("a") is None
        assert cache.get("b") == "2"
