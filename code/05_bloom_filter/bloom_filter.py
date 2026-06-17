import math
import mmh3
from bitarray import bitarray
from typing import Sequence


class BloomFilter:
    """Bloom filter with optimal m and k computed from capacity and error rate."""

    def __init__(self, capacity: int, error_rate: float) -> None:
        if capacity <= 0 or error_rate <= 0 or error_rate >= 1:
            raise ValueError("capacity > 0 and 0 < error_rate < 1 required")
        self.capacity = capacity
        self.error_rate = error_rate
        n = float(capacity)
        p = error_rate
        self.m = int(math.ceil(-(n * math.log(p)) / (math.log(2) ** 2)))
        self.k = int(math.ceil((self.m / n) * math.log(2)))
        self._bits = bitarray(self.m)
        self._bits.setall(False)
        self._inserted = 0

    @property
    def bits(self) -> bitarray:
        return self._bits

    def _hashes(self, item: str) -> Sequence[int]:
        return [mmh3.hash(item, seed=i) % self.m for i in range(self.k)]

    def add(self, item: str) -> None:
        """Insert an item into the bloom filter."""
        for h in self._hashes(item):
            self._bits[h] = 1
        self._inserted += 1

    def check(self, item: str) -> bool:
        """Return False if definitely not present, True if possibly present."""
        return all(self._bits[h] for h in self._hashes(item))

    def estimate_fpp(self) -> float:
        """Estimate the current false-positive probability."""
        p = (1.0 - math.exp(-self.k * self._inserted / self.m)) ** self.k
        return p
