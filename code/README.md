# System Design — Code Examples

Runnable Python implementations of core system design patterns.

| Module | Pattern | File | Test |
|---|---|---|---|
| 01 | Consistent Hashing | `01_consistent_hashing/consistent_hash.py` | `test_consistent_hash.py` |
| 02 | Rate Limiter (Token Bucket + Sliding Window) | `02_rate_limiter/rate_limiter.py` | `test_rate_limiter.py` |
| 03 | LRU Cache (O(1) doubly-linked list) | `03_lru_cache/lru_cache.py` | `test_lru_cache.py` |
| 04 | Circuit Breaker (state machine) | `04_circuit_breaker/circuit_breaker.py` | `test_circuit_breaker.py` |
| 05 | Bloom Filter (mmh3, FPP math) | `05_bloom_filter/bloom_filter.py` | `test_bloom_filter.py` |
| 06 | Transactional Outbox (polling) | `06_transactional_outbox/outbox.py` | `test_outbox.py` |
| 07 | Consistent Snapshot (Chandy-Lamport) | `07_consistent_snapshots/consistent_snapshot.py` | `test_consistent_snapshot.py` |
| 08 | Raft Heartbeat (Leader Election) | `08_raft_heartbeat/raft_heartbeat.py` | `test_raft_heartbeat.py` |

## Usage

```bash
pip install -r requirements.txt
python -m pytest code/
```
