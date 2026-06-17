# Module 2 — Database Architectures & Scaling — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** ACID Properties
**Type:** Multiple Choice

Which ACID property ensures that once a transaction is committed, it remains committed even after a system crash?

A) Atomicity
B) Consistency
C) Isolation
D) Durability

<details>
<summary>Answer & Explanation</summary>

**Answer:** D

**Explanation:** Durability guarantees that committed transactions survive permanent failures (crashes, power loss) through write-ahead logging or replication. Atomicity ensures all-or-nothing execution. Consistency ensures valid state transitions. Isolation ensures concurrent transactions don't interfere.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 2 🟢
**Topic:** Read Replicas
**Type:** Open-Ended

What is a read replica and when would you add one to your database architecture?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A read replica is a copy of the primary database that serves only read queries. It's added when read traffic exceeds the primary's capacity, when you need lower read latency for geographically distant users, or when running heavy analytics/ reporting queries that shouldn't impact the primary. Replication is typically asynchronous.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 3 🟢
**Topic:** Vertical vs Horizontal Scaling
**Type:** Multiple Choice

Which statement about vertical scaling is correct?

A) It distributes data across many machines
B) It requires application-level sharding logic
C) It adds more CPU/RAM/storage to a single machine
D) It provides infinite scalability

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Vertical scaling (scaling up) adds resources to an existing machine. It has hard limits (max CPU/memory of the hardware) and creates a single point of failure. Horizontal scaling (scaling out) adds machines but requires partitioning logic.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 4 🟢
**Topic:** Indexing
**Type:** Multiple Choice

What type of index is typically used by default in relational databases like PostgreSQL?

A) Hash index
B) B-Tree index
C) Bitmap index
D) GiST index

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** B-Tree indexes are the default in most relational databases. They support equality and range queries efficiently with O(log n) lookup, insertion, and deletion. Hash indexes only support equality. Bitmap indexes are for low-cardinality columns. GiST is for geospatial/full-text.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 5 🟢
**Topic:** Database Connection Pooling
**Type:** Open-Ended

Why is database connection pooling important for a web application? What happens if connections are not pooled?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Connection pooling reuses database connections instead of creating a new TCP connection for each request. Without pooling, each request incurs TCP handshake + TLS overhead, and the database may exhaust its max connections (e.g., PostgreSQL's default is 100). This leads to connection refused errors and degraded performance.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 6 🟢
**Topic:** Sharding Overview
**Type:** Multiple Choice

What is a shard key?

A) The encryption key for the database
B) A column or set of columns used to distribute data across database instances
C) A caching strategy for hot data
D) A type of database transaction

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** A shard key determines how data is partitioned across shards. It should be chosen to distribute data evenly and support the most common query patterns. A poorly chosen shard key leads to hotspots and uneven data distribution.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 7 🟢
**Topic:** CAP Theorem
**Type:** Open-Ended

What does the CAP theorem state? Give an example of a CP system and an AP system.

<details>
<summary>Answer & Explanation</summary>

**Answer:** CAP states a distributed data system can provide at most two of: Consistency (every read gets the latest write), Availability (every request gets a non-error response), and Partition Tolerance (system continues despite network failures). Since partitions are inevitable, this is effectively a choice between C and A during a partition. CP: traditional RDBMS with synchronous replication. AP: Cassandra, DynamoDB.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 8 🟢
**Topic:** Denormalization
**Type:** Multiple Choice

What is the primary trade-off of denormalization?

A) Simpler queries at the cost of data redundancy and update complexity
B) Reduced storage at the cost of complex joins
C) Faster writes at the cost of slower reads
D) Better consistency at the cost of availability

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** Denormalization adds redundant data to avoid joins, making reads faster. The costs: increased storage, more complex updates (must update multiple copies), and potential for data inconsistency.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 9 🟡
**Topic:** Database Migration Without Downtime
**Type:** Open-Ended

Describe a strategy for running a schema migration (e.g., adding a column with a default value) on a large PostgreSQL table without downtime.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Use the "expand-migrate-contract" pattern:
1. **Expand:** Add the column as nullable (no default). The application writes to both old and new but reads from old.
2. **Migrate:** Backfill the column in batches using batched UPDATE with small transaction sizes. Run data consistency checks.
3. **Contract:** Add NOT NULL constraint (if needed), remove the old code path, drop obsolete columns.

For large tables, use pgRoll or pt-online-schema-change which creates a shadow table and incrementally syncs via triggers.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 10 🟡
**Topic:** Sharding Strategy Design
**Type:** Open-Ended

Design a sharding strategy for a multi-tenant SaaS application with 50,000 tenants. Some tenants have 100x the data of others. How do you avoid hot shards?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Use a two-level approach:
1. **Logical shard mapping:** Create a lookup table mapping tenant_id → shard_id. This allows moving tenants between shards.
2. **Virtual shards (shard groups):** Create 512-1024 virtual shards and map them to fewer physical databases. Distribute large tenants across multiple virtual shards.
3. **Re-sharding mechanism:** Monitor shard sizes and move hot tenants gradually using weighted consistent hashing or a configurable mapping table. Automate detection (size + QPS per tenant) and rebalancing.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 11 🟡
**Topic:** N+1 Query Problem
**Type:** Debug

An API endpoint that lists 100 blog posts takes 5 seconds to respond. The code queries the posts table, then for each post queries the author table. What is this problem called and how do you fix it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** This is the N+1 query problem: 1 query for the list + N queries for each item (101 total).

**Fix:** Use eager loading — fetch all posts in one query (`SELECT * FROM posts WHERE ...`), then fetch all authors with a single query (`SELECT * FROM authors WHERE id IN (...)`) and join in application memory. Or use SQL JOINs. ORM-level solutions: `SelectIn` or `Include` (depending on ORM).

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 12 🟡
**Topic:** Index Selection
**Type:** Multiple Choice

A query `SELECT * FROM orders WHERE status = 'pending' AND created_at > '2024-01-01'` runs slowly on a 10M row table. The `status` column has 3 distinct values. The `created_at` column is highly selective. Which index is optimal?

A) Index on `status` only
B) Index on `created_at` only
C) Composite index on `(status, created_at)`
D) Composite index on `(created_at, status)`

<details>
<summary>Answer & Explanation</summary>

**Answer:** C — composite index on `(status, created_at)`

**Explanation:** The leading column should be the most selective one used in equality conditions. But since `status` has low selectivity, putting it first allows the database to quickly narrow down to the matching partition, then use the second column for range filtering. Option D would scan a large portion of the index.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 13 🟡
**Topic:** Database Replication Lag
**Type:** Open-Ended

How does replication lag occur in an async replication setup? What can a user experience when reading from a read replica during a lag spike?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Replication lag is the delay between a write on the primary and its appearance on replicas. Causes: replica CPU saturation, network latency, large write transactions, or replica row-lock contention. User impact: "read-after-write inconsistency" — a user writes data and immediately reads from a replica that hasn't caught up, seeing stale data.

**Mitigations:** Read-your-writes consistency (route reads to primary for a session window), synchronous replication for critical data, monitoring lag with alerts.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 14 🟡
**Topic:** Partitioning (RDBMS)
**Type:** Open-Ended

What is the difference between database partitioning (e.g., PostgreSQL partitioning) and sharding? When would you choose one over the other?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Partitioning splits a table within a single database server. Sharding distributes data across multiple database servers. Partitioning helps with query performance (partition pruning), data lifecycle management (drop old partitions), and vacuum/maintenance. Sharding helps with horizontal scaling beyond a single server's capacity. Choose partitioning when data fits on one server but needs better manageability. Choose sharding when data exceeds one server's capacity.

**Reference:** Docs/02-database-scaling.md
</details>

---

## Question 15 🔴
**Topic:** Distributed Join Across Shards
**Type:** Whiteboard

Design a system that supports a join query across two tables that live in different shards. Your system has 64 shards, and the join is frequent. Discuss trade-offs of at least three approaches.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Three approaches:
1. **Application-side join:** Query both shards, fetch all results, join in memory. Simple but requires transferring all matching rows, O(n) data transfer.
2. **Colocate by join key:** Shard both tables using the same key (e.g., user_id), so matching rows are on the same shard. Eliminates cross-shard joins entirely. Best for OLTP but inflexible.
3. **Distributed query engine:** Use Presto/Trino or Spark to push down predicates, fetch intermediate results from each shard, and perform the join in the engine. Flexible but adds infrastructure complexity and latency.
4. **Materialized view / read model:** Precompute the joined result and store it. Use change data capture to keep it updated. Best for read-heavy workloads.

**Reference:** Docs/02-database-scaling.md, Docs/02-database-scaling-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Strong Consistency at Scale
**Type:** Whiteboard

Design a system that provides strong consistency (linearizability) across a globally distributed database with 5 regions. How do you handle writes with low latency (P99 < 100ms for writes within a region)? Discuss at least two consensus protocols and their trade-offs.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Options:
1. **Spanner-style (TrueTime):** Use a global clock (TrueTime API) with commit-wait to order transactions. Writes go to a leader in the nearest region. Synchronous replication to a majority across regions. Latency is ~RTT to the nearest quorum members.
2. **CockroachDB-style (Hybrid Logical Clock + Raft):** Each range (default 64 MB) has a Raft group with replicas in 3 regions. Writes commit when a majority of replicas acknowledge. Cross-region latency adds ~50-200ms depending on distance.
3. **Leader lease approach:** Assign a single leader region for each partition. All writes for that partition go to the leader. Provide read leases for cache-coherent reads. Use epoch-based leases to detect leader failure.

**Key trade-off:** Strict consistency always adds cross-region latency. For low-latency writes, configure preferred-leader zone to be close to most writes.

**Reference:** Docs/02-database-scaling-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Hotspot Mitigation
**Type:** Calculation

A social media app uses user_id % 100 as its shard key. One celebrity user generates 40% of all writes. The shard hosting user_id % 100 = 42 reaches 95% CPU. You cannot re-shard immediately. Design an immediate mitigation + long-term fix. Calculate the load distribution.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Immediate mitigation:** 
- Temporarily route the celebrity user's writes to a dedicated single-node "shard" (a tier-1 cache with async flush to main DB, or a separate small shard cluster).
- Or rate-limit the celebrity's writes at the application level (accept but batch).

**Long-term fix:**
- Use consistent hashing with virtual nodes instead of modulo.
- Split the hot shard: migrate 50% of the data to a new shard. Point reads at both during migration using a lookup table.

**Calculation:** With modulo 100 and uniform distribution, each shard gets ~1% of traffic (ignoring the celebrity). The celebrity's share = 40%. Shard 42 receives: 1% (normal share) + 40% (celebrity) = 41% of all writes. After mitigation: if celebrity gets a dedicated shard, shard 42 drops to 0.6% and the dedicated shard handles 40%.

**Reference:** Docs/02-database-scaling-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Hybrid Transactional/Analytical Processing
**Type:** Whiteboard

Design a system that supports both high-throughput OLTP (10,000 writes/sec) and complex analytical queries (aggregations across billions of rows) on the same dataset with < 1 minute data freshness for analytics. Discuss the Lambda vs Kappa architecture trade-offs.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Use a Lambda architecture:
1. **OLTP layer (speed):** PostgreSQL or MySQL with primary serving writes. Use change data capture (Debezium) to stream changes.
2. **Streaming layer:** Kafka captures CDC events. Stream processor (Flink) computes real-time aggregations and writes to a real-time view (Redis or ClickHouse).
3. **Batch layer (analytics):** Data is also written to S3/Parquet nightly via Spark for complex ETL. Presto/Trino or Athena queries the combined batch + real-time view.

**Kappa variation:** Replace the batch layer with a second streaming pipeline that replays from the beginning of the Kafka topic. Easier operationally but higher latency for large reprocessing.

**Reference:** Docs/02-database-scaling-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Multi-Leader Replication Conflict
**Type:** Debug

A team deployed a multi-leader database setup across two data centers. They experience "last write wins" conflicts that lose user data (e.g., a user edits their profile in DC1, then the same field is overwritten by a stale write from DC2). How would you redesign the conflict resolution to prevent data loss?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **CRDTs (Conflict-free Replicated Data Types):** Use mergeable data structures like RGA (Replicated Growable Array) for text, or LWW-register with hybrid clocks.
2. **Application-level conflict resolution:** Instead of LWW, store version vectors per document. On conflict, return both versions to the application (or a specialized conflict resolution service) for semantic merge.
3. **Avoid multi-leader for user-mutable data:** Use a single leader per partition. Route all writes for user_id N to DC1, user_id N+1 to DC2, etc. Use a deterministic shard-to-leader mapping.
4. **Operational transformations** for collaborative editing (Google Docs-style).

**Reference:** Docs/02-database-scaling-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Optimistic vs Pessimistic Locking
**Type:** Open-Ended

In an e-commerce system with high contention on inventory stock counts, when would you choose optimistic locking over pessimistic locking? Show a specific scenario where pessimistic locking is necessary and why.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Optimistic locking** (version column, compare-and-set) works when contention is low — retries are cheap and most transactions succeed on first attempt. Better throughput for read-heavy workloads.

**Pessimistic locking** (`SELECT ... FOR UPDATE`) is necessary when:
1. Contention is high (many concurrent transactions on the same row).
2. Operations involve multiple related rows that must be changed atomically (e.g., deducting from inventory while inserting an order item).
3. A retry would be expensive (e.g., a multi-step checkout after 3rd-party payment authorization).

**Scenario requiring pessimistic:** Two users try to buy the last item in stock simultaneously. With optimistic locking, both read stock=1, both decrement to 0, one write succeeds, the other fails and retries — but now the item is gone, causing a confusing "sorry, item sold out" after the user went through checkout. With pessimistic locking, the second user's transaction waits and then correctly sees stock=0 immediately.

**Reference:** Docs/02-database-scaling-advanced.md
</details>
