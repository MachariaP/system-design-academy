import pytest
from consistent_hash import ConsistentHashRing


class TestConsistentHashRing:
    def test_add_and_get_node(self):
        ring = ConsistentHashRing(vnodes=100)
        ring.add_node("A")
        ring.add_node("B")
        ring.add_node("C")
        keys = [f"key{i}" for i in range(100)]
        nodes = [ring.get_node(k) for k in keys]
        assert all(n in ("A", "B", "C") for n in nodes)
        assert len(set(nodes)) == 3

    def test_remove_node(self):
        ring = ConsistentHashRing(vnodes=100)
        ring.add_node("A")
        ring.add_node("B")
        ring.add_node("C")
        ring.add_node("D")
        keys = [f"key{i}" for i in range(1000)]
        before = [ring.get_node(k) for k in keys]
        ring.remove_node("D")
        after = [ring.get_node(k) for k in keys]
        redirected = sum(1 for b, a in zip(before, after) if b != a)
        assert redirected == 0 or abs(redirected / len(keys) - 0.25) < 0.15

    def test_skew_after_removal(self):
        ring = ConsistentHashRing(vnodes=200)
        for n in ["A", "B", "C", "D", "E"]:
            ring.add_node(n)
        keys = [f"key{i}" for i in range(1000)]
        before = {n: 0 for n in ["A", "B", "C", "D", "E"]}
        for k in keys:
            before[ring.get_node(k)] += 1
        ring.remove_node("E")
        after = {n: 0 for n in ["A", "B", "C", "D"]}
        for k in keys:
            after[ring.get_node(k)] += 1
        total = sum(after.values())
        for count in after.values():
            assert abs(count / total - 0.25) <= 0.10

    def test_empty_ring(self):
        ring = ConsistentHashRing()
        assert ring.get_node("any") is None

    def test_duplicate_add(self):
        ring = ConsistentHashRing(vnodes=10)
        ring.add_node("A")
        ring.add_node("A")
        assert ring.get_node("x") == "A"
