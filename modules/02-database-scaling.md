# Module 2: Database Architectures & Scaling

Databases are where system design becomes real.

Stateless services can be cloned. Queues can buffer. Caches can absorb reads. But storage has memory, ordering, ownership, durability, and correctness. Scaling a database means deciding where data lives, how replicas agree, what happens during network partitions, and which invariants cannot be broken.

This module is a definitive reference for distributed storage trade-offs, combining relational scaling, sharding, consistent hashing, Dynamo-style availability, GFS-style separation of control/data planes, and modern hot-partition lessons.

---

## Learning Goals

| Skill | What You Should Be Able To Explain |
|---|---|
| **SQL vs. NoSQL choice** | How consistency, joins, access patterns, and write volume drive storage choice |
| **Replication lag** | Why read replicas can return stale data after a successful write |
| **Sharding** | How shard keys shape query locality, hotspots, and operational complexity |
| **Consistent hashing** | Why virtual nodes reduce rebalancing and smooth ownership |
| **Dynamo-style AP storage** | Sloppy quorum, hinted handoff, vector clocks, and semantic reconciliation |
| **GFS architecture** | Why metadata control and bulk data flow are separated |
| **Hot partition handling** | How poor partition keys and skewed access patterns break otherwise scalable systems |
| **SQL tuning** | How indexing, data types, partitioning, and denormalization affect performance |

---

## 1. Master Decision Tree: Should I Use SQL Or NoSQL?

```mermaid
flowchart TD
    Start["Start: What does the data need?"]
    Txn["Do you need multi-row ACID transactions<br/>or strict invariants?"]
    Joins["Do you need rich joins and ad hoc queries?"]
    WriteScale["Is write volume too high for one primary<br/>or one vertical SQL cluster?"]
    Access["Are access patterns known and key-based?"]
    Global["Do you need global low-latency writes?"]
    NewSQLFit["Can you pay coordination latency<br/>for distributed SQL semantics?"]
    SQL["Traditional SQL<br/>Postgres/MySQL"]
    SQLScale["SQL + replicas + partitioning<br/>then shard/federate carefully"]
    NoSQL["NoSQL / Dynamo-style KV or wide-column"]
    NewSQL["NewSQL<br/>Spanner/CockroachDB-style"]
    Search["Specialized index/search store"]

    Start --> Txn
    Txn -->|"Yes"| Joins
    Txn -->|"No"| Access
    Joins -->|"Yes"| WriteScale
    Joins -->|"No, mostly key-value"| Access
    WriteScale -->|"No"| SQL
    WriteScale -->|"Yes"| NewSQLFit
    NewSQLFit -->|"Yes"| NewSQL
    NewSQLFit -->|"No"| SQLScale
    Access -->|"Yes, predictable key access"| Global
    Access -->|"No, search/ranking/text"| Search
    Global -->|"Yes, availability over immediate consistency"| NoSQL
    Global -->|"No"| SQLScale
```

> 🧠 **Staff-engineer note**  
> The correct database is usually not "SQL vs NoSQL." It is "which invariants must be enforced synchronously, and which views can be rebuilt asynchronously?"

---

## 2. Distributed Storage Reality: CAP And PACELC

In a distributed database, replicas communicate over a network that can drop, delay, duplicate, or reorder packets. During a **network partition**, one replica may be unable to verify whether another replica has accepted a newer write.

| Choice During Partition | Behavior | Trade-Off |
|---|---|---|
| **Consistency over availability** | Refuse or wait until the system can prove the latest value | Correct but may time out |
| **Availability over consistency** | Answer using local state | Responsive but may be stale |

**PACELC** extends the lesson:

- If there is a **Partition**, choose **Availability or Consistency**.
- **Else**, during normal operation, choose **Latency or Consistency**.

---

## 3. Storage Architecture Performance Matrix

| Architecture | Throughput | Write Latency | Data Consistency | Complexity |
|---|---|---|---|---|
| **RDBMS Master-Slave** | High reads via replicas; writes limited by primary | Low to moderate on primary | Strong on primary; replicas can lag | Moderate: failover, read routing |
| **RDBMS Master-Master** | Higher write availability when partitioned by ownership | Higher due to conflict handling or coordination | Hard, concurrent writes may conflict | High: conflict resolution, split-brain risk |
| **Federation** | Good when domains scale independently | Local to one functional database | Strong within domain, weaker across domains | High: cross-domain workflows |
| **Sharding** | High if shard key distributes load | Low for single-shard writes, high for cross-shard writes | Strong within shard, hard across shards | Very high: routing, rebalancing, hotspots |
| **NoSQL / Dynamo-style** | Very high horizontal throughput | Low when accepting local/quorum writes | Eventual or tunable consistency | High: reconciliation and data modeling |
| **NewSQL** | High horizontal scale for SQL workloads | Higher than local SQL due to consensus/clock coordination | Strong distributed transactions | High: operational and latency complexity |

**NewSQL difference:** systems such as Spanner and CockroachDB aim to preserve SQL and ACID semantics across distributed nodes, usually by using consensus and carefully managed replication. They reduce application-level sharding pain, but coordination latency is still real.

---

## 4. Replication Lag And Read-After-Write Bugs

Master-slave replication scales reads by copying primary writes to read replicas. The cost is **replication lag**.

```mermaid
sequenceDiagram
    participant U as User
    participant API as Application
    participant P as Primary DB
    participant R as Read Replica

    U->>API: Update display_name = "Amina"
    API->>P: COMMIT write at LSN=500
    P-->>API: Success
    API-->>U: 200 OK
    Note over P,R: Replica has only replayed to LSN=470
    U->>API: Refresh profile immediately
    API->>R: SELECT profile
    R-->>API: Old display_name
    API-->>U: Stale read
    P-->>R: Replication catches up to LSN=500
```

### Mitigations

| Technique | How It Works |
|---|---|
| **Read own writes from primary** | For a short window after writes, route that user's reads to primary |
| **Version token / LSN token** | Client carries last committed version; router chooses only caught-up replicas |
| **Replica lag tracking** | Remove lagging replicas from read pool |
| **Session consistency** | Keep user reads on a replica known to have observed the write |
| **Synchronous replication** | Wait for replicas before acking, trading latency for consistency |

---

## 5. Data Modeling For Sharding

Sharding is not just splitting rows. It is choosing the ownership model for your data.

### Common Shard Keys

| Shard Key | Good For | Risk |
|---|---|---|
| **user_id** | User-owned profiles, posts, settings, timelines | Celebrity or enterprise users can become hot |
| **tenant_id** | B2B SaaS isolation and billing ownership | Large tenants can dominate one shard |
| **geo_region** | Compliance, latency, regional data boundaries | Poor distribution for global products |
| **object_id hash** | Even distribution for independent objects | Cross-object queries become expensive |
| **time bucket** | Logs, events, metrics, retention windows | Current bucket can become hot |
| **composite key** | `tenant_id + hash(entity_id)` balances locality and spread | Query routing is more complex |

### How To Choose A Shard Key

A good shard key should:

- Have high cardinality.
- Distribute writes evenly.
- Match common query filters.
- Avoid cross-shard joins for the hottest paths.
- Avoid concentrating all traffic for one customer, celebrity, or region.
- Support rebalancing without rewriting the application.

### Bad Choice Example: `country` For A Global Social Network

`country` seems intuitive, but it is usually poor:

- A few countries dominate traffic.
- Users travel and use VPNs.
- Social graph edges cross countries.
- One viral event can heat one country partition.
- The key has low cardinality, so it cannot scale horizontally enough.

> ⚠️ **Failure mode**  
> A shard key can evenly distribute rows but still fail to distribute traffic. Always model request rate per key, not only storage per key.

---

## 6. Sharding Hotspot: Celebrity Key

```mermaid
flowchart LR
    Requests["Millions of requests<br/>profile:celebrity-123"]
    Router["Shard Router<br/>hash(user_id)"]

    subgraph Shards["Database Shards"]
        S1["Shard 1<br/>10% CPU"]
        S2["Shard 2<br/>12% CPU"]
        S3["Shard 3<br/>99% CPU<br/>celebrity-123 lives here"]
        S4["Shard 4<br/>8% CPU"]
    end

    Requests --> Router
    Router --> S3
    Router -. ordinary users .-> S1
    Router -. ordinary users .-> S2
    Router -. ordinary users .-> S4

    style S3 fill:#fee2e2,stroke:#dc2626
    style S1 fill:#ecfdf5,stroke:#059669
    style S2 fill:#ecfdf5,stroke:#059669
    style S4 fill:#ecfdf5,stroke:#059669
```

### Hotspot Mitigations

| Technique | Use When |
|---|---|
| **Read replicas for hot shard** | Hot key is read-heavy |
| **Cache hot object** | Same object read repeatedly |
| **Split logical key** | Comments, counters, likes can be bucketed |
| **Dedicated shard / tenant isolation** | One tenant or celebrity dominates |
| **Adaptive partitioning** | Storage engine can split hot ranges/items |
| **Rate limits and backpressure** | Protect system while rebalancing |

---

## 7. Consistent Hashing And Virtual Nodes

Consistent hashing maps both keys and nodes onto a fixed ring. A key belongs to the first node encountered while walking clockwise.

### Ring With Virtual Nodes And Key Movement

```mermaid
flowchart TB
    Ring["Hash Ring<br/>0 ... 2^128 - 1"]

    subgraph Before["Before: 3 Physical Nodes With Virtual Nodes"]
        A1["• A#1 token 08"]
        B1["• B#1 token 22"]
        C1["• C#1 token 39"]
        A2["• A#2 token 57"]
        C2["• C#2 token 74"]
        B2["• B#2 token 91"]
    end

    subgraph Keys["Keys"]
        K1["key user:42 token 18<br/>owned by B#1"]
        K2["key order:9 token 63<br/>owned by C#2"]
        K3["key cart:7 token 96<br/>wraps to A#1"]
    end

    subgraph Join["Node D Joins"]
        D1["• D#1 token 16"]
        D2["• D#2 token 67"]
    end

    Ring --> A1 --> B1 --> C1 --> A2 --> C2 --> B2 --> Ring
    K1 -->|"clockwise before join"| B1
    K2 -->|"clockwise before join"| C2
    K3 -->|"wrap"| A1
    D1 -->|"takes range (08,16]"| K1
    D2 -->|"takes range (57,67]"| K2

    style D1 fill:#fef3c7,stroke:#d97706
    style D2 fill:#fef3c7,stroke:#d97706
```

When node `D` joins, only keys in the ranges it now owns move. The rest of the cluster remains stable.

### Why Virtual Nodes Matter

| Without Virtual Nodes | With Virtual Nodes |
|---|---|
| One physical node owns one large random range | Each node owns many small ranges |
| Load can be uneven | Distribution smooths statistically |
| Adding a node affects one neighbor heavily | Movement spreads across many neighbors |
| Heterogeneous hardware is hard | Stronger nodes can get more virtual nodes |

---

## 8. Production Code: Consistent Hash Ring With Ownership Watch

```python
"""
Consistent Hash Ring with Virtual Nodes
======================================

Runtime: Python 3.10+
Dependencies: standard library only

Features:
- Stable hashing with hashlib.sha256
- Virtual nodes for smoother distribution
- O(log n) lookup using bisect
- Distribution statistics
- Text histogram
- Ownership watch to report which sampled keys move after topology changes
"""

from __future__ import annotations

import bisect
import hashlib
import logging
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Sequence


LOGGER = logging.getLogger(__name__)
MAX_TOKEN = 2**256


def stable_hash(value: str) -> int:
    digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
    return int(digest, 16)


@dataclass(frozen=True)
class RingEntry:
    token: int
    node: str
    vnode_id: int


class ConsistentHashRing:
    def __init__(self, nodes: Optional[Iterable[str]] = None, replicas: int = 128) -> None:
        if replicas <= 0:
            raise ValueError("replicas must be positive")

        self.replicas = replicas
        self._tokens: List[int] = []
        self._ring: Dict[int, RingEntry] = {}
        self._nodes: set[str] = set()

        for node in nodes or []:
            self.add_node(node)

    def add_node(self, node: str) -> None:
        self._validate_node(node)
        if node in self._nodes:
            return

        self._nodes.add(node)
        for vnode_id in range(self.replicas):
            token = self._unique_token(f"{node}#{vnode_id}")
            self._ring[token] = RingEntry(token=token, node=node, vnode_id=vnode_id)
            bisect.insort(self._tokens, token)

    def remove_node(self, node: str) -> None:
        if node not in self._nodes:
            return

        self._nodes.remove(node)
        doomed = [token for token, entry in self._ring.items() if entry.node == node]

        for token in doomed:
            del self._ring[token]
            index = bisect.bisect_left(self._tokens, token)
            if index < len(self._tokens) and self._tokens[index] == token:
                self._tokens.pop(index)

    def get_node(self, key: str) -> str:
        if not self._tokens:
            raise RuntimeError("cannot route key on an empty ring")

        token = stable_hash(key)
        index = bisect.bisect_left(self._tokens, token)
        if index == len(self._tokens):
            index = 0

        return self._ring[self._tokens[index]].node

    def get_replicas(self, key: str, count: int) -> List[str]:
        if count <= 0:
            raise ValueError("count must be positive")
        if count > len(self._nodes):
            raise ValueError("replica count cannot exceed physical node count")

        token = stable_hash(key)
        index = bisect.bisect_left(self._tokens, token)
        replicas: List[str] = []
        seen: set[str] = set()

        while len(replicas) < count:
            if index == len(self._tokens):
                index = 0

            node = self._ring[self._tokens[index]].node
            if node not in seen:
                replicas.append(node)
                seen.add(node)

            index += 1

        return replicas

    def distribution(self, sample_keys: Sequence[str]) -> Counter[str]:
        return Counter(self.get_node(key) for key in sample_keys)

    def distribution_percentages(self, sample_keys: Sequence[str]) -> Dict[str, float]:
        counts = self.distribution(sample_keys)
        total = sum(counts.values()) or 1
        return {node: (count / total) * 100 for node, count in sorted(counts.items())}

    def text_histogram(self, sample_keys: Sequence[str], width: int = 40) -> str:
        percentages = self.distribution_percentages(sample_keys)
        lines: List[str] = []

        for node, pct in percentages.items():
            bar = "#" * max(1, round((pct / 100) * width))
            lines.append(f"{node:>12} | {bar:<{width}} | {pct:6.2f}%")

        return "\n".join(lines)

    def watch_ownership_changes(
        self,
        sample_keys: Sequence[str],
        operation_name: str,
    ) -> Callable[[], Dict[str, tuple[str, str]]]:
        before = {key: self.get_node(key) for key in sample_keys}

        def finish() -> Dict[str, tuple[str, str]]:
            after = {key: self.get_node(key) for key in sample_keys}
            moved = {
                key: (before[key], after[key])
                for key in sample_keys
                if before[key] != after[key]
            }
            LOGGER.info(
                "ring operation=%s moved_keys=%s total_keys=%s",
                operation_name,
                len(moved),
                len(sample_keys),
            )
            return moved

        return finish

    def nodes(self) -> List[str]:
        return sorted(self._nodes)

    def _unique_token(self, seed: str) -> int:
        token = stable_hash(seed)
        collision = 0
        while token in self._ring:
            collision += 1
            token = stable_hash(f"{seed}:collision:{collision}")
        return token

    @staticmethod
    def _validate_node(node: str) -> None:
        if not node or not node.strip():
            raise ValueError("node must be a non-empty string")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    keys = [f"user:{i}" for i in range(10_000)]
    ring = ConsistentHashRing(["db-a", "db-b", "db-c"], replicas=128)

    print("Before adding db-d")
    print(ring.text_histogram(keys))

    finish_watch = ring.watch_ownership_changes(keys, "add db-d")
    ring.add_node("db-d")
    moved = finish_watch()

    print("\nAfter adding db-d")
    print(ring.text_histogram(keys))
    print(f"\nMoved sampled keys: {len(moved)} / {len(keys)}")
```

> 🧠 **Staff-engineer note**  
> Consistent hashing balances key ownership, not request rate. A single hot key can still overwhelm one node.

---

## 9. Dynamo-Style AP Systems

Dynamo-style systems optimize for write availability during failures. They use replication, sloppy quorums, hinted handoff, and conflict reconciliation.

### Sloppy Quorum + Hinted Handoff Write Path

```mermaid
sequenceDiagram
    participant C as Client
    participant Coord as Coordinator
    participant A as Node A<br/>ideal owner
    participant B as Node B<br/>ideal owner
    participant Cn as Node C<br/>ideal owner
    participant D as Node D<br/>temporary healthy node

    C->>Coord: PUT cart:123 = add book
    Coord->>A: write replica
    A--xCoord: unreachable
    Coord->>B: write replica
    Coord->>Cn: write replica
    Coord->>D: write with hint: belongs to A
    B-->>Coord: ack
    Cn-->>Coord: ack
    Coord-->>C: success after W=2 acks
    Note over D,A: Later, A recovers
    D->>A: hand off hinted write
    A-->>D: ack
    D->>D: delete temporary hinted copy
```

| Mechanism | Purpose |
|---|---|
| **Sloppy quorum** | Write to reachable healthy nodes, not only ideal owners |
| **Hinted handoff** | Temporary node later forwards missed writes to intended owner |
| **Eventual consistency** | Replicas converge after communication resumes |
| **Vector clocks** | Detect whether versions are causal descendants or conflicts |

---

## 10. Vector Clocks: Concrete Cart Conflict

Two clients update the same cart during a partition.

### Before Partition

| Version | Cart Items | Vector Clock |
|---|---|---|
| `V0` | `[]` | `{A: 1}` |

### During Partition

Client 1 writes through node `B`:

| Version | Cart Items | Vector Clock |
|---|---|---|
| `V1` | `["book"]` | `{A: 1, B: 1}` |

Client 2 writes through node `C`:

| Version | Cart Items | Vector Clock |
|---|---|---|
| `V2` | `["pen"]` | `{A: 1, C: 1}` |

Neither clock dominates the other. `V1` and `V2` are concurrent siblings.

### Reconciliation

| Step | Version | Cart Items | Vector Clock |
|---|---|---|---|
| Read after heal | `V1` | `["book"]` | `{A: 1, B: 1}` |
| Read after heal | `V2` | `["pen"]` | `{A: 1, C: 1}` |
| Application merge | `V3` | `["book", "pen"]` | `{A: 1, B: 1, C: 1, R: 1}` |

### Application Merge Snippet

```python
from typing import Dict, Iterable, List, Set


VectorClock = Dict[str, int]


def dominates(left: VectorClock, right: VectorClock) -> bool:
    """Return True when left causally includes right."""
    all_nodes = set(left) | set(right)
    return all(left.get(node, 0) >= right.get(node, 0) for node in all_nodes)


def merge_cart_siblings(siblings: Iterable[dict], resolver_node: str) -> dict:
    """Merge concurrent shopping-cart siblings using semantic reconciliation."""
    merged_items: Set[str] = set()
    merged_clock: VectorClock = {}

    for sibling in siblings:
        merged_items.update(sibling["items"])
        for node, counter in sibling["vector_clock"].items():
            merged_clock[node] = max(merged_clock.get(node, 0), counter)

    # Increment the resolver node to create a new descendant version.
    merged_clock[resolver_node] = merged_clock.get(resolver_node, 0) + 1

    return {
        "items": sorted(merged_items),
        "vector_clock": merged_clock,
    }


siblings = [
    {"items": ["book"], "vector_clock": {"A": 1, "B": 1}},
    {"items": ["pen"], "vector_clock": {"A": 1, "C": 1}},
]

print(merge_cart_siblings(siblings, resolver_node="R"))
```

> ⚠️ **Failure mode**  
> Last-write-wins would silently drop either `book` or `pen`. That is unacceptable for carts, balances, permissions, and collaborative editing.

---

## 11. GFS: Control Plane vs. Data Plane

GFS separates metadata control from bulk data movement.

| Plane | Component | Responsibility |
|---|---|---|
| **Control plane** | Master | Namespace, file-to-chunk mapping, leases, placement |
| **Data plane** | Chunkservers | Store large chunks and stream bytes |
| **Client** | GFS client | Asks master for metadata, then reads/writes chunkservers directly |

The master does not carry file data. It coordinates. The chunkservers move bytes.

Design lesson: keep high-volume data flow away from centralized metadata controllers.

---

## 12. SQL Tuning Matrix

| Technique | Why It Works | Trade-Off |
|---|---|---|
| **B-tree indexes** | Efficient equality, range, join, and ordering lookups | Slower writes and more storage |
| **Composite indexes** | Match multi-column access patterns | Column order matters |
| **Covering indexes** | Serve query from index only | Storage and write amplification |
| **Correct data types** | Smaller rows improve cache density | Bad choices require migrations |
| **Table partitioning** | Prunes scans and simplifies retention | Planner and operational complexity |
| **Denormalization** | Avoids expensive joins | Slower writes and consistency repair |

### Denormalization Trade-Off

Denormalization duplicates data to optimize read paths. It is useful when reads dominate writes, but every update now has multiple copies to maintain.

| Benefit | Cost |
|---|---|
| Faster reads | Slower writes |
| Fewer joins | Duplicate data |
| Better cache locality | Repair jobs may be needed |
| Simpler read queries | Update logic gets harder |

---

## 13. Real-World Case Studies

### Instagram-Style Sharding And ID Generation

Early Instagram architecture discussions popularized a practical pattern: generate IDs that include a timestamp, a shard identifier, and a per-shard sequence. This lets IDs remain roughly time-sortable while encoding where the object belongs.

| ID Segment | Purpose |
|---|---|
| Timestamp bits | Sort by creation time without another lookup |
| Shard ID bits | Route object to owning shard |
| Sequence bits | Generate many IDs per shard per time unit |

Design lesson: IDs can be routing metadata, not just identifiers.

### DynamoDB Adaptive Capacity And Hot Partitions

AWS DynamoDB documentation describes adaptive capacity as a mechanism that helps tables continue serving uneven access patterns without throttling, as long as traffic stays within table-level and partition-level limits. AWS also documents per-partition limits, so hot partition design still matters.

| Lesson | Meaning |
|---|---|
| Adaptive capacity helps | The database can react to uneven traffic |
| It is not magic | A single hot key or poor partition key can still limit scale |
| Model access patterns | Partition keys must spread request volume, not only storage |
| Watch partition heat | Monitor throttling, consumed capacity, and hot keys |

> 🧠 **Staff-engineer note**  
> Managed databases can reduce operational burden, but they do not remove data-modeling responsibility.

---

## 14. Mock Challenges

> **Challenge 1: Celebrity Hotspot On A Sharded Social Network**  
> A celebrity profile lives on one shard. Traffic spikes to millions of reads and comments. Explain why the whole cluster has capacity but the request still fails.

> **Challenge 2: Read-After-Write Bug From Replication Lag**  
> A user updates their shipping address and immediately refreshes checkout, but the old address appears from a read replica. Design a targeted fix.

> **Challenge 3: Dynamo Conflict During Partition**  
> Two replicas accept different cart updates during a network partition. Explain sloppy quorum, hinted handoff, vector clocks, and semantic reconciliation.

<details><summary>Click for Staff-Engineer Level Answers</summary>

## Challenge 1

The shard key routed the celebrity's data to one partition. Total cluster capacity is irrelevant because all traffic for the hot key hits the same owner. Fix with caching, read replicas, hot-key splitting, counter buckets, dedicated shards for extreme accounts, and per-shard circuit breakers.

## Challenge 2

The primary committed the write, but the replica had not replayed the log yet. Return a version token or LSN after the write. Route read-your-writes requests only to replicas caught up to that token, or temporarily to the primary for that user/session.

## Challenge 3

Sloppy quorum accepts writes on reachable nodes. Hinted handoff later forwards missed writes to intended owners. Vector clocks detect concurrent siblings. The application merges the cart semantically, writes back a merged version, and avoids last-write-wins data loss.

</details>

---

## References

- [Amazon DynamoDB: Burst and adaptive capacity](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/burst-adaptive-capacity.html)
- [Amazon DynamoDB warm throughput and partition limits](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/warm-throughput-scenarios.html)
- [AWS: DynamoDB adaptive capacity handles imbalanced workloads](https://aws.amazon.com/about-aws/whats-new/2019/11/amazon-dynamodb-adaptive-capacity-now-handles-imbalanced-workloads-better-by-isolating-frequently-accessed-items-automatically/)
- [Instagram sharding and ID generation reference](https://media.postgresql.org/sfpug/instagram_sfpug.pdf)
