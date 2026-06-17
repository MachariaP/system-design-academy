import hashlib
import bisect
from typing import Optional


class ConsistentHashRing:
    """Consistent hash ring with virtual nodes for even distribution."""

    def __init__(self, vnodes: int = 200) -> None:
        self.vnodes = vnodes
        self.ring: list[tuple[int, str]] = []
        self.nodes: set[str] = set()

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node_id: str) -> None:
        """Add a node to the ring with virtual nodes."""
        if node_id in self.nodes:
            return
        self.nodes.add(node_id)
        for i in range(self.vnodes):
            vkey = f"{node_id}#{i}"
            h = self._hash(vkey)
            bisect.insort(self.ring, (h, node_id))
        self._dedupe()

    def remove_node(self, node_id: str) -> None:
        """Remove a node and all its virtual nodes from the ring."""
        if node_id not in self.nodes:
            return
        self.nodes.discard(node_id)
        self.ring = [(h, n) for h, n in self.ring if n != node_id]

    def _dedupe(self) -> None:
        """Remove duplicates keeping last occurrence."""
        seen: set[int] = set()
        unique: list[tuple[int, str]] = []
        for h, n in reversed(self.ring):
            if h not in seen:
                seen.add(h)
                unique.append((h, n))
        unique.reverse()
        self.ring = unique

    def get_node(self, key: str) -> Optional[str]:
        """Return the node responsible for the given key."""
        if not self.ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self.ring, (h, ""))
        if idx == len(self.ring):
            idx = 0
        return self.ring[idx][1]
