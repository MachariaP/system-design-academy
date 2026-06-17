> **You've used this when...** You added a product to your cart on Amazon, refreshed the page, and it was still there. You posted a comment on Instagram and it appeared instantly. Behind these moments, a database stored that data, made sure it survived even if a server crashed, and served it back to you when you asked.

Now imagine you are the engineer designing that database layer. At first, a single database on one machine works fine. But as your users grow, reads slow down, writes pile up, and the machine runs out of disk. You need to split data across multiple machines, make copies for reading, and pick databases that handle different types of workloads.

This module explains how databases scale — from a single server to thousands — and what trade-offs you make at each step.

# Database Architectures & Scaling – A Beginner’s Guide

> This guide explains how databases store, replicate, and scale data in distributed systems.
> We use simple analogies and plain language.
> Every technical term is defined the first time it appears, and a full Glossary is at the end.
> After reading this, the original advanced module will feel much easier.

---

> **Before you start:** You should understand [Module 1: Traffic Routing & Network Foundations](#). If you haven’t read that yet, start there — this module builds on routing and load balancing concepts.

---

## Table of Contents

1. [The Core Question: SQL or NoSQL?](#1-the-core-question-sql-or-nosql)
2. [The CAP Theorem – When the Network Breaks](#2-the-cap-theorem--when-the-network-breaks)
3. [Scaling Reads: Replication and the Lag Problem](#3-scaling-reads-replication-and-the-lag-problem)
4. [Splitting Data Across Many Machines – Sharding](#4-splitting-data-across-many-machines--sharding)
5. [Shard Keys: The Good, the Bad, and the Hot](#5-shard-keys-the-good-the-bad-and-the-hot)
6. [Consistent Hashing – Distributing Data Smoothly](#6-consistent-hashing--distributing-data-smoothly)
7. [When Availability Wins: Dynamo‑Style Systems](#7-when-availability-wins-dynamostyle-systems)
8. [Vector Clocks – Detecting Conflicting Updates](#8-vector-clocks--detecting-conflicting-updates)
9. [A Famous Design: GFS – Separating Control from Data Flow](#9-a-famous-design-gfs--separating-control-from-data-flow)
10. [SQL Performance Tuning – Quick Tips](#10-sql-performance-tuning--quick-tips)
11. [Common Pitfalls and How to Avoid Them](#11-common-pitfalls-and-how-to-avoid-them)
12. [Glossary of Technical Terms](#12-glossary-of-technical-terms)
13. [Key Takeaways](#13-key-takeaways)

---

> **⏱ TL;DR — If you only learn 3 things from this module:**
> 1. **SQL vs NoSQL is not a religious war.** Use SQL when you need complex joins and strong consistency; use NoSQL when you need to scale writes across many machines.
> 2. **Replication helps reads, sharding helps writes.** Both introduce complexity: replication lag and hot keys can bring your system down if ignored.
> 3. **Consistent hashing makes adding/removing nodes cheap**, but it doesn’t fix hot keys. Always monitor for hotspots.

---

## 1. The Core Question: SQL or NoSQL?

When you start building an application, one of the first choices is **where to store the data**.

- **SQL databases** (like PostgreSQL, MySQL) are like a well‑organized filing cabinet with strict rules. They enforce **schemas** (a fixed structure for data), support powerful **joins** (combining data from multiple tables), and guarantee **ACID transactions** (Atomicity, Consistency, Isolation, Durability – meaning your data always follows the rules, even if the power fails).
- **NoSQL databases** (like DynamoDB, MongoDB, Cassandra) are more like a flexible warehouse. They often sacrifice strict rules in favour of **horizontal scalability** (spreading data across many cheap machines), **high write throughput**, and the ability to work even when parts of the network are broken.

### How to decide (in plain language)

Ask yourself these questions:

| Approach | Use when... | Don’t use when... |
|----------|-------------|-------------------|
| **SQL (PostgreSQL, MySQL)** | You need multi-row transactions (ACID); your main queries involve complex joins; data structure is known and stable | Write volume is extremely high and you need to scale writes horizontally; your data is unstructured or varies per record; you need to serve a billion users with a single master |
| **NoSQL (DynamoDB, MongoDB, Cassandra)** | Your workload is mostly key-value lookups; write volume is extremely high and consistency can be slightly relaxed; you need to scale horizontally across many cheap machines | You need complex joins on the hot path; you require strong consistency for every read; your application relies heavily on multi-row transactions |
| **Specialized (Elasticsearch, Graph DB)** | You need full-text search or graph traversal (friends-of-friends, recommendation chains) | Your primary workload is simple CRUD; you can achieve the same with SQL indexes and joins |

**The real question is not “SQL vs NoSQL”, but:**  
*“Which invariants must be enforced immediately (synchronously), and which can be built up gradually (asynchronously)?”*

---

## 2. The CAP Theorem – When the Network Breaks

In a distributed database, data is spread over many servers that talk over a network. Networks are **not perfect**: messages can be delayed, lost, or blocked. This leads to the famous **CAP theorem**:

- **Consistency (C)** – Every read sees the latest write. All copies agree.
- **Availability (A)** – Every request gets a response (even if it’s not the latest data).
- **Partition Tolerance (P)** – The system continues to operate even when the network is cut (a **network partition**).

You cannot have all three perfectly at the same time when a partition happens. You must choose:

- **CP (Consistency + Partition Tolerance):** During a partition, the system may refuse some requests to avoid returning wrong data. Example: a banking system that says “sorry, try again later” rather than show an incorrect balance.
- **AP (Availability + Partition Tolerance):** During a partition, the system always answers, even if the data might be slightly stale. Example: a social media feed that shows an older version until the network heals.

A more detailed version is **PACELC**: if there is a **P**artition, trade **A**vailability vs **C**onsistency; **E**lse (no partition), trade **L**atency vs **C**onsistency.

Think of it like two friends keeping a shared notebook over a bad phone line. They either wait until they can agree on every word (consistency) or they each keep writing and sort out differences later (availability).

---

## 3. Scaling Reads: Replication and the Lag Problem

When a database gets too many read requests, you can create **read replicas** – extra copies of the data that only serve reads. Writes still go to the **primary** (or master), and the changes are sent to the replicas.

**The problem:** Replication takes time. There is always a small delay between a write on the primary and the moment it appears on a replica. This is called **replication lag**.

### Example (Read‑after‑write bug)

1. User updates their display name to “Amina”.
2. The primary commits the change and says “Success”.
3. Immediately the user refreshes the page, and the read request goes to a replica that hasn’t received the update yet.
4. The replica returns the old name. The user sees the old name – confusing!

### How to fix it

| Approach | Use when... | Don’t use when... |
|----------|-------------|-------------------|
| **Read your own writes from primary** | Users must see their own changes immediately after writing; your read/write ratio is moderate | Your write volume is very high (you would overload the primary); read-after-write consistency is acceptable to be eventually consistent |
| **Version tokens** | You need fine-grained control over read freshness; your replicas have varying lag levels | The complexity of managing tokens outweighs the benefit; you have a simple workload |
| **Lag tracking** | You have many replicas and want to automatically route around slow ones | You only have one or two replicas; lag is uniform across replicas |
| **Synchronous replication** | You cannot tolerate any inconsistency between primary and replicas; your network latency between nodes is low | Your writes must be very fast (synchronous waits add latency); your replicas are geographically far apart |

---

## 4. Splitting Data Across Many Machines – Sharding

```mermaid
flowchart LR
    Client["App / Client"]
    LB["Load Balancer / Proxy"]
    subgraph Replicas["Read Replicas (Scale Reads)"]
        R1[(Replica 1)]
        R2[(Replica 2)]
        R3[(Replica 3)]
    end
    subgraph Shards["Shards (Scale Writes & Storage)"]
        S1[(Shard A<br/>Users A-M)]
        S2[(Shard B<br/>Users N-Z)]
    end
    Client -->|Write| Primary[(Primary DB)]
    Primary -->|Async replication| R1
    Primary -->|Async replication| R2
    Primary -->|Async replication| R3
    Client -->|Read-only queries| LB
    LB --> R1 & R2 & R3
    Client -->|Sharded writes| LB2[Shard Router]
    LB2 -->|hash(user_id) % 2| S1
    LB2 --> S2
```

When a single database server cannot hold all the data or handle all the traffic, you split the data into pieces called **shards**. Each shard is an independent database that holds a subset of the data.

**Sharding is like splitting a phonebook:**

- You could split by last name: A‑M in one book, N‑Z in another.
- The rule you use to decide which record goes to which shard is called the **shard key**.

But sharding is not just about storing rows. It’s about **ownership** of data and **query patterns**. If most queries need data from many shards, performance can become terrible.

---

## 5. Shard Keys: The Good, the Bad, and the Hot

A **shard key** determines which shard a record lives on. Choosing the right one is critical.

### Good shard key properties

- **High cardinality** – many possible values, so data spreads evenly.
- **Matches common query filters** – so you can read from a single shard.
- **Avoids “hotspots”** – no single value gets disproportionately more traffic.
- **Supports rebalancing** – you can add shards without rewriting everything.

### Examples

| Shard Key | Good for | Risk |
|-----------|----------|------|
| `user_id` | User‑owned data | A celebrity user can create a hotspot. |
| `tenant_id` | Multi‑tenant SaaS | One large enterprise can dominate a shard. |
| `geo_region` | Compliance, local data | Some regions may be tiny, others huge. |
| **Hash of `object_id`** | Even distribution | Cross‑object queries become hard. |
| **Composite key** `tenant_id + hash(entity_id)` | Balance locality and spread | Routing logic is more complex. |

### The celebrity hotspot trap

Even if rows are evenly distributed, **request rate** may not be. Imagine a social network sharded by `user_id`. A famous celebrity’s profile lives on one shard. When they post something, millions of read requests hammer that single shard, while other shards are idle. The system fails even though total capacity is sufficient.

**Mitigations:** heavy caching, read replicas for that shard, splitting the hot key into sub‑keys, dedicated shards for extreme accounts, and rate limiting.

---

## 6. Consistent Hashing – Distributing Data Smoothly

When you add or remove a shard, you want to move as little data as possible. **Consistent hashing** solves this.

Imagine a circle (a ring) with numbers from 0 to a huge maximum. Both the shard names and the data keys are hashed to points on this ring. A key belongs to the first shard encountered while walking clockwise.

- When you add a new shard, it appears at a point on the ring and takes over only the keys that fall into its small arc. All other keys stay where they were.
- Without consistent hashing, adding a shard might require remapping almost every key.

**Virtual nodes:** Each physical shard gets many small points on the ring (e.g., 128 “virtual nodes”). This ensures load is evenly spread, even if the physical machines have different capacities (stronger machines get more virtual nodes).

> 🧠 **Note:** Consistent hashing balances *key ownership*, not *request rate*. A single hot key still hits one shard.

---

## 7. When Availability Wins: Dynamo‑Style Systems

Amazon’s Dynamo paper described a database designed to **always accept writes**, even during network failures. It’s an **AP** system (availability + partition tolerance) with **eventual consistency**: replicas may temporarily disagree, but they will converge over time.

### Key mechanisms

- **Sloppy quorum:** A write is accepted as soon as a minimum number of healthy nodes (not necessarily the “ideal” owners) acknowledge it. This keeps the system writable even when some nodes are down.
- **Hinted handoff:** If a write was temporarily stored on a node that isn’t the real owner, that node later forwards the data to the correct owner when it recovers.
- **Vector clocks:** A way to track version history so you can later detect and merge conflicting updates (see next section).
- **Read repair:** When a read detects stale data, it updates the lagging replica.

Think of it like a team of note‑takers in different rooms during a fire alarm. They all keep taking notes (availability). When the alarm stops, they compare notes and combine them (eventual consistency).

---

## 8. Vector Clocks – Detecting Conflicting Updates

When two users change the same shopping cart at the same time on different replicas, the system needs to know that these two versions are **concurrent** (neither is just an update of the other) and must be merged.

A **vector clock** is a little map attached to each version. It counts how many updates each node has seen.

### Example: Shopping cart conflict

1. **Initial state:** `{items: []}` with clock `{A:1}`
2. User 1 on replica B adds “book” → clock becomes `{A:1, B:1}`
3. User 2 on replica C adds “pen” → clock becomes `{A:1, C:1}`
4. Neither clock is “bigger” than the other (B’s count isn’t ≥ C’s everywhere), so the system knows they are **siblings** – a conflict.
5. The application merges them: `{items: ["book", "pen"]}` and writes back a new clock `{A:1, B:1, C:1, R:1}`.

This is far safer than **last‑write‑wins**, which would silently drop one of the items (imagine that for a bank balance!). Reconciliation rules are **application‑specific**: merging cart items by union is safe, but merging calendar times may need human review.

---

## 9. A Famous Design: GFS – Separating Control from Data Flow

Google File System (GFS) introduced a classic pattern: separate the **control plane** (metadata about where data lives) from the **data plane** (the actual bytes).

- **Master server** – keeps track of file names, which chunks belong to which files, and where each chunk is stored. It is like a librarian who knows where every book is, but does not carry the books.
- **Chunkservers** – store the actual file chunks and stream data directly to clients.
- A client asks the master for the chunk locations, then reads/writes directly to the chunkservers.

This design keeps the master lightweight (it handles only metadata, not file transfers) and allows the data plane to scale horizontally.

---

## 10. SQL Performance Tuning – Quick Tips

Even if you stick with SQL, there are many knobs to make it faster.

- **Indexes** are like a book’s index: they let the database find rows without scanning everything. A **covering index** contains all the columns needed for a query, so the database never even has to look at the main table.
- **Proper data types** – using `integer` instead of `string` for IDs saves space and speeds up comparisons.
- **Table partitioning** – splitting one huge table into smaller physical pieces (by date, for example) can make queries and data removal faster.
- **Denormalization** – sometimes you copy a piece of data into another table to avoid a slow join. The cost is that you must keep both copies in sync.
- **Always use `EXPLAIN ANALYZE`** to see what the database is actually doing, instead of guessing.

**Common mistake:** adding too many indexes. Every index speeds up reads but slows down writes, because it must be updated on every insert/update.

---

> **✏️ Check Your Understanding**
> 1. Your social media app has 10 million users. Each user has a profile, posts, and friends. You need to show the “friends feed” (posts from friends, sorted by time). Would you choose SQL or NoSQL for this? Why?
> 2. A user updates their profile picture. When they refresh the page, they still see the old picture. What happened and how would you fix it?
> 3. Your database is split into 10 shards by `user_id`. One user has 50 million followers and their posts get 100x more reads than anyone else’s. What problem do you face and what can you do about it?
> <details>
> <summary>Answers</summary>
> 1. **SQL** — the “friends feed” query typically involves joining a friends list table with a posts table, which SQL handles elegantly. NoSQL can work but requires denormalization and application-level joins.
> 2. **Read-after-write inconsistency** — the write went to the primary but the read went to a lagging replica. Fix: read from primary for a short time after a write, or use version tokens.
> 3. **Celebrity hotspot** — one shard gets 100x the traffic of others. Mitigate with heavy caching, read replicas for that shard, splitting the hot key, or a dedicated shard for extreme accounts.
> </details>

---

## 11. Common Pitfalls and How to Avoid Them

### Hot partition / celebrity key

**Symptom:** One shard’s CPU and IOPS are maxed out while other shards sit idle. Users on that shard experience slow responses or timeouts.
**Root Cause:** The shard key distributes rows evenly but not request rate. A single popular entity (celebrity, trending topic) generates disproportionate traffic to its shard.
**Real Incident:** Twitter’s “Fail Whale” era — early Twitter sharded by user ID. When a celebrity tweeted, the shard hosting that user would collapse under the read storm, taking down that user’s entire shard.
**Fix:** Cache aggressively, add read replicas for that shard, split the hot key into sub-keys (e.g., `celebrity_id_1`, `celebrity_id_2`), or move extreme accounts to dedicated shards.
**How to Detect Early:** Monitor per-shard QPS, latency, and error rates. Set alerts if one shard’s QPS exceeds 2x the median across all shards.

### Read-after-write inconsistency

**Symptom:** A user updates their data and sees the old value on the next page load. Other users may also see inconsistent states.
**Root Cause:** Writes go to the primary, but the read is served by a replica that hasn’t received the latest update yet (replication lag).
**Real Incident:** Many early social networks experienced this when they first introduced read replicas. Users would post a comment, refresh, and not see it — causing confusion and re-posts.
**Fix:** Route a user’s reads to the primary for a short window after they write, or use version tokens so reads only go to replicas that have caught up.
**How to Detect Early:** Monitor replication lag in seconds. Alert if lag exceeds 1 second for user-facing workloads.

### Cross-shard joins

**Symptom:** Queries that worked fine on a single database become extremely slow or timeout after sharding. Memory usage on the application server spikes.
**Root Cause:** A query needs data from multiple shards, forcing the application to scatter requests to all shards and combine results in memory.
**Real Incident:** A major e-commerce platform found that their “order history with product details” query became 50x slower after sharding orders by `user_id`, because product details lived on different shards.
**Fix:** Denormalize (store product details alongside the order), use async materialized views, or redesign the query to avoid cross-shard operations on the hot path.
**How to Detect Early:** Monitor query latency percentile (p99) before and after sharding. If response time jumps disproportionately, cross-shard queries are likely the cause.

### Split-brain in master-master

**Symptom:** Two database nodes both accept writes. After the network heals, data is inconsistent — some records have conflicting values that cannot be auto-merged.
**Root Cause:** During a network partition, both nodes promoted themselves to primary and accepted writes. No fencing mechanism prevented the split.
**Real Incident:** GitHub’s October 2018 MySQL failover — a network timeout caused both MySQL nodes to believe they were primary, leading to a split-brain scenario and data inconsistencies.
**Fix:** Use a witness/quorum to confirm the old primary is truly down before promoting a standby. Implement fencing (STONITH: Shoot The Other Node In The Head). Avoid multi-master unless absolutely necessary.
**How to Detect Early:** Monitor replication status on all nodes. Alert if two nodes report themselves as “primary” or “master.”

### Last-write-wins data loss

**Symptom:** Two users update the same record simultaneously. One update silently overwrites the other. Critical data (cart items, document edits) disappears.
**Root Cause:** The database uses a “last write wins” conflict resolution strategy, which keeps only the most recent write and discards concurrent updates without merging.
**Real Incident:** Amazon experienced this with early versions of their shopping cart — two devices adding items to the same cart could lose one device’s additions. This led to the development of vector clocks in Dynamo.
**Fix:** Use versioning (vector clocks, CRDTs) and application-level merge logic. For carts, merge item lists; for bank balances, use transactional updates.
**How to Detect Early:** Monitor conflict-resolution metrics. If you use last-write-wins, audit periodically for unexpected data loss by comparing a sample of overwritten records.

### Over-indexing

**Symptom:** Writes become progressively slower as data grows. Disk usage is higher than expected.
**Root Cause:** Too many indexes were created to speed up reads. Every INSERT or UPDATE must update every index, adding write amplification.
**Real Incident:** A SaaS startup added indexes for every column to “prepare for all possible queries.” Write latency went from 2ms to 200ms as the table grew. Removing unused indexes restored performance.
**Fix:** Index only the queries that actually run in production. Use `EXPLAIN ANALYZE` to verify index usage. Monitor write performance and index size.
**How to Detect Early:** Track index size vs. table size ratio. Monitor write latency trend. Use slow query logs to find unindexed queries rather than pre-emptively adding indexes.


> **🧪 Conceptual Exercises**
> 1. **Design the database layer for a global messaging app.** Users send billions of messages per day. Messages must be delivered with low latency, and users must be able to search their message history. What database types would you use? How would you shard? How would you handle a user with millions of followers who sends a broadcast message?
> 2. **Your e-commerce site’s inventory system uses a single SQL database.** During Black Friday, writes to the database become slow and some fail entirely. You need to scale. Would you add read replicas or shard the database? What are the trade-offs?
> <details>
> <summary>Hints</summary>
> - For the messaging app, consider separate services for message delivery vs. message search — they have very different access patterns.
> - For the inventory system, think about whether the bottleneck is reads or writes. If it’s writes, read replicas won’t help.
> - For the broadcast message, recall the celebrity hotspot problem and the mitigations.
> </details>

---

## 12. Glossary of Technical Terms

| Term | Definition | Section |
|------|------------|---------|
| **ACID** | Atomicity, Consistency, Isolation, Durability – the properties that guarantee reliable database transactions. | 1 |
| **Joins** | SQL operation that combines rows from two or more tables based on a related column. | 1 |
| **NoSQL** | “Not only SQL” – a category of databases that may sacrifice SQL‑like joins and transactions for scalability. | 1 |
| **CAP theorem** | In a distributed system, you can only have two of Consistency, Availability, Partition tolerance during a network fault. | 2 |
| **Eventual consistency** | A model where replicas may briefly disagree, but will converge to the same state if no new updates occur. | 2 |
| **Network partition** | A situation where some nodes in a distributed system cannot communicate with others. | 2 |
| **Partition tolerance** | The ability to keep operating even when the network is broken into isolated groups. | 2 |
| **Master‑slave replication** | One primary (master) handles writes; replicas (slaves) copy the data and serve reads. | 3 |
| **Read replica** | A copy of the database used only for reading, to spread the read load. | 3 |
| **Replication lag** | The delay between a write on the primary and its appearance on a replica. | 3 |
| **Horizontal scaling** | Adding more machines rather than upgrading a single machine (vertical scaling). | 4 |
| **Shard** | A horizontal partition of a database – each shard holds a subset of data. | 4 |
| **Shard key** | The column or hashed value used to decide which shard a record belongs to. | 5 |
| **Consistent Hashing** | A technique to distribute data across nodes so that adding/removing nodes moves minimal data. | 6 |
| **Virtual node** | In consistent hashing, many small points assigned to one physical node to improve load distribution. | 6 |
| **Dynamo‑style** | A class of highly available, eventually consistent databases inspired by Amazon’s Dynamo. | 7 |
| **Hinted handoff** | In Dynamo, a temporary node stores a write intended for a down node and forwards it later. | 7 |
| **Sloppy quorum** | Accepting writes from a set of nodes that may not be the ideal owners, to maintain availability. | 7 |
| **Vector clock** | A data structure that tracks the update history of a piece of data across different nodes, allowing conflict detection. | 8 |
| **GFS** | Google File System – a distributed file system that separates metadata management from bulk data transfer. | 9 |
| **Denormalization** | Duplicating data in multiple places to speed up reads at the cost of write overhead and possible inconsistency. | 10 |
| **Index** | A data structure (like a book index) that speeds up data retrieval. | 10 |


---

## 13. Key Takeaways

1. **The database choice is about trade‑offs.** There is no “best” database – only the right one for your access patterns, consistency needs, and scale.
2. **Replication helps reads but introduces lag.** Always design for the possibility that a user might read stale data right after writing.
3. **Sharding gives scale, but the shard key is everything.** A bad key creates hotspots and operational pain.
4. **Consistent hashing makes adding/removing nodes cheap.** But it does not fix hot keys.
5. **Dynamo‑style systems prioritise availability.** They use sloppy quorums, hinted handoff, and vector clocks to handle failures gracefully.
6. **Conflicts are inevitable in distributed systems.** Use vector clocks and application‑specific merging – never rely on last‑write‑wins for critical data.
7. **Separate control from data flow** (the GFS lesson) – let metadata be small and centralized, and bulk data flow directly.
8. **Tune SQL wisely:** indexes, proper data types, partitioning, and denormalization all have costs.
9. **Always monitor the real traffic patterns**, not just storage distribution. A shard that looks balanced by row count may still be a hotspot.

---

> This guide translates a dense, production‑oriented module into plain English.
> Once you're comfortable with these concepts, the [advanced material](02-database-scaling-advanced.md) will become a powerful reference — covering CAP at the packet level, the raw mechanics of replication lag, B-Tree internals, and the full celebrity hot-spot mitigation playbook.
> Remember: every complex storage system is built from a handful of simple, repeatable patterns.
