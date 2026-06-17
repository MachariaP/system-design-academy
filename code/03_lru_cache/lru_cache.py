from typing import Generic, Optional, TypeVar

K = TypeVar("K")
V = TypeVar("V")


class _Node(Generic[K, V]):
    __slots__ = ("key", "value", "prev", "next")

    def __init__(self, key: K, value: V) -> None:
        self.key = key
        self.value = value
        self.prev: Optional["_Node[K, V]"] = None
        self.next: Optional["_Node[K, V]"] = None


class LRUCache(Generic[K, V]):
    """O(1) LRU cache using a doubly-linked list and hash map."""

    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self._cache: dict[K, _Node[K, V]] = {}
        self._head = _Node[K, V](None, None)  # type: ignore[arg-type]
        self._tail = _Node[K, V](None, None)  # type: ignore[arg-type]
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node: _Node[K, V]) -> None:
        node.prev.next = node.next  # type: ignore[union-attr]
        node.next.prev = node.prev  # type: ignore[union-attr]

    def _add_to_front(self, node: _Node[K, V]) -> None:
        node.next = self._head.next
        node.prev = self._head
        self._head.next.prev = node  # type: ignore[union-attr]
        self._head.next = node

    def get(self, key: K) -> Optional[V]:
        """Return the value for key, or None if missing."""
        node = self._cache.get(key)
        if node is None:
            return None
        self._remove(node)
        self._add_to_front(node)
        return node.value

    def put(self, key: K, value: V) -> None:
        """Insert or update a key-value pair."""
        node = self._cache.get(key)
        if node is not None:
            node.value = value
            self._remove(node)
            self._add_to_front(node)
            return
        if len(self._cache) == self.capacity:
            lru = self._tail.prev
            self._cache.pop(lru.key)  # type: ignore[union-attr]
            self._remove(lru)
        new_node = _Node(key, value)
        self._cache[key] = new_node
        self._add_to_front(new_node)
