# Module 5 — Async Processing & Message Queues — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** Message Queue Fundamentals
**Type:** Multiple Choice

What is the primary role of a message queue in a distributed system?

A) Storing database queries for later execution
B) Decoupling producers and consumers so they operate independently
C) Replacing HTTP for all service-to-service communication
D) Caching frequently accessed data

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Message queues decouple producers (publishers) from consumers (subscribers). Producers send messages without waiting for consumers. Consumers process at their own pace. This improves resilience, allows independent scaling, and handles traffic bursts by buffering.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 2 🟢
**Topic:** At-Least-Once vs At-Most-Once
**Type:** Multiple Choice

Which delivery guarantee could result in duplicate message processing if the consumer crashes after processing but before acknowledging?

A) At-most-once
B) At-least-once
C) Exactly-once
D) Best-effort

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** At-least-once delivery guarantees the message is delivered at least once, but may be delivered multiple times. If a consumer processes a message but crashes before sending the ACK, the broker redelivers the message to another consumer. The consumer must handle duplicates (idempotency).

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 3 🟢
**Topic:** Kafka Topic & Partition
**Type:** Open-Ended

What is a Kafka topic? How does partitioning within a topic enable parallelism?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A topic is a logical channel to which producers write and from which consumers read. Topics are divided into partitions (ordered, immutable sequences of records). Partitions enable parallelism: different consumers in a consumer group can read different partitions simultaneously. A partition's ordering guarantee applies within the partition, not across partitions.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 4 🟢
**Topic:** Consumer Group
**Type:** Multiple Choice

In Kafka, if a consumer group has 5 consumers and the topic has 3 partitions, what happens?

A) Each consumer gets approximately 0.6 partitions
B) 3 consumers are active (one per partition), 2 remain idle
C) Each consumer reads all 3 partitions
D) The group fails because consumers exceed partitions

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Each partition is assigned to exactly one consumer in a group. With 3 partitions and 5 consumers, 3 consumers are active (each gets one partition) and 2 are idle. To maximize parallelism, the number of consumers should equal the number of partitions.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 5 🟢
**Topic:** RabbitMQ Exchange Types
**Type:** Multiple Choice

Which RabbitMQ exchange type routes messages based on routing key pattern matching (e.g., `orders.*`)?

A) Direct exchange
B) Fanout exchange
C) Topic exchange
D) Headers exchange

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Topic exchanges route messages to queues whose binding key matches the routing key using wildcards (`*` matches one word, `#` matches zero or more words). Direct uses exact match. Fanout broadcasts to all bound queues. Headers uses header attributes instead of routing keys.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 6 🟢
**Topic:** Dead Letter Queue
**Type:** Open-Ended

What is a dead letter queue (DLQ) and why is it important in a messaging system?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A DLQ is a queue where messages are sent when they cannot be processed successfully (e.g., after exhausting retries). It prevents poison messages from blocking the main queue and allows debugging/ reprocessing failed messages later. Without a DLQ, a single bad message can cause infinite retries or be silently discarded.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 7 🟢
**Topic:** Push vs Pull
**Type:** Multiple Choice

Which messaging model does Apache Kafka use?

A) Push — broker pushes messages to consumers
B) Pull — consumers poll the broker for messages
C) Hybrid — push for high priority, pull for low priority
D) Pub-sub — broker broadcasts to all subscribers

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Kafka uses a pull model: consumers request batches of messages from the broker. This allows consumers to control their consumption rate, avoids overwhelming slow consumers, and enables batching for efficiency. RabbitMQ uses a push model (or optional basic.get for pull).

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 8 🟢
**Topic:** Message Ordering
**Type:** Open-Ended

How does Kafka guarantee message ordering within a partition but not across partitions? How would you design a system where all messages for a specific user must be in order?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Kafka appends messages to a partition in write order, and consumers read a partition sequentially. To guarantee ordering for a specific user, use the user_id as the message key. Kafka hashes the key to deterministically assign it to a partition, ensuring all messages for that user go to the same partition and are processed in order.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 9 🟡
**Topic:** Exactly-Once Semantics
**Type:** Open-Ended

Describe how to achieve exactly-once processing in Kafka. What are the trade-offs of enabling exactly-once semantics?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Kafka achieves exactly-once via:
1. **Idempotent producer:** The producer tags each message with a producer ID and sequence number. The broker deduplicates in case of retries.
2. **Transactional producer:** Multiple messages can be committed atomically across partitions.
3. **Consumer transactional offset commit:** The consumer commits its offset within the same transaction as its output.

**Trade-offs:** Increased latency (transaction coordinator overhead), reduced throughput (up to 20-30% depending on configuration), and complexity. Often, idempotent consumer design (at-least-once + dedup) is preferred for performance.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 10 🟡
**Topic:** Back-pressure in Messaging
**Type:** Open-Ended

What is back-pressure? How do different messaging systems handle it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Back-pressure occurs when producers send messages faster than consumers can process them. If unhandled, brokers run out of memory/disk, or consumers crash.

**Handling:**
- **Kafka:** Consumers control their own pace via polling. The broker stores messages on disk (configurable retention). If consumers fall behind, Kafka uses disk (bounded by retention policy/disk space).
- **RabbitMQ:** Uses flow control — if a broker detects memory pressure, it stops accepting messages from producers. Consumers can also use QoS (prefetch count) to limit unacked messages.
- **Reactive streams:** Use back-pressure signals (request N) to flow control from consumer to producer.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 11 🟡
**Topic:** Kafka Partition Rebalancing
**Type:** Debug

A Kafka consumer group experiences "stop-the-world" rebalancing every 5 minutes, causing processing pauses of 30-60 seconds. What causes frequent rebalancing and how do you fix it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Frequent rebalancing is typically caused by consumers timing out (session.timeout.ms too low, heartbeats not sent in time due to GC pauses or slow processing). 

**Fixes:**
1. Increase `session.timeout.ms` and `max.poll.interval.ms`.
2. Increase `heartbeat.interval.ms` for more frequent heartbeats.
3. Use static group membership (Kafka 2.3+) with `group.instance.id` so members are expected and rejoin faster.
4. Use cooperative rebalancing (`partition.assignment.strategy=CooperativeStickyAssignor`) for incremental rebalancing.
5. Fix consumer processing time / GC pauses.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 12 🟡
**Topic:** Message Deduplication
**Type:** Open-Ended

Design a message deduplication system for a payment processing pipeline that receives webhook events. Messages may be delivered multiple times due to retries. How do you prevent double charging?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

1. **Idempotency key:** Each event includes an idempotency key (e.g., `event_id` or `payment_intent_id`). The processor checks a deduplication store (Redis or DB) for this key before processing.
2. **Dedup store design:** `SETNX idempotency_key TTL 24h`. If the key already exists with status "processing" or "completed", skip.
3. **Atomicity:** Use a transaction: insert dedup record + charge customer in the same DB transaction (or use a Redis lock + compensating action).
4. **Handling late duplicates:** Store the result (success/failure) so even delayed duplicates don't cause issues.
5. **Garbage collection:** TTL-based cleanup of old idempotency keys.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 13 🟡
**Topic:** Kafka Log Compaction
**Type:** Multiple Choice

What is Kafka log compaction useful for?

A) Reducing the number of partitions for better performance
B) Keeping only the latest value for each key, useful for restoring state
C) Encrypting message data at rest
D) Increasing message retention time

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Log compaction retains only the most recent value for each message key, removing older duplicates. This is useful for state restoration (e.g., a user profile topic where only the latest state matters), database changelog topics, and keyed state stores. The compacted topic can be used to rebuild a consumer's state by replaying from the beginning.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 14 🟡
**Topic:** Priority Queues
**Type:** Open-Ended

How would you implement a priority queue in a message system where high-priority orders should be processed before lower-priority ones? Compare using RabbitMQ vs Kafka.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
- **RabbitMQ:** Use multiple queues (priority_high, priority_medium, priority_low). Consumers use per-queue prefetch and process from high first. Or use RabbitMQ's built-in priority queue support (x-max-priority).
- **Kafka:** Kafka doesn't natively support priority ordering within a partition. Approaches: (1) Separate topics per priority level, consumers poll high-priority topics first. (2) Use a priority field and route messages to different partitions, with consumers prioritizing certain partitions. (3) Use an external priority queue (Redis Sorted Set) as a staging layer.

**Reference:** Docs/05-async-messaging.md
</details>

---

## Question 15 🔴
**Topic:** Exactly-Once End-to-End Pipeline
**Type:** Whiteboard

Design an end-to-end exactly-once pipeline: Postgres CDC → Kafka → Flink → S3. Money is involved, so duplicates are unacceptable at the S3 output. The pipeline must survive broker failures, task manager crashes, and network partitions.

<details>
<summary>Answer & Explanation</summary>

**Answer:**

1. **Postgres CDC (Debezium):** Uses WAL-based streaming. Messages include LSN (log sequence number) for offset tracking. Debezium commits its offset in Kafka's `connect-offsets` topic.
2. **Kafka:** Idempotent producer + transactional producer. Set `acks=all`, `enable.idempotence=true`. Use a single partition per source table (or key by PK) to preserve order.
3. **Flink:** Enable checkpointing with exactly-once semantics. Use Kafka's transactional API for source offset commit. Use `EXACTLY_ONCE` mode for the Kafka producer (or file sink).
4. **S3 sink:** Use Flink's StreamingFileSink with exactly-once mode — it uses a two-phase commit: writes to temp files, then commits on checkpoint. Or use a manifest-based approach: write Parquet files to a staging directory, then atomically move them with a manifest.
5. **Recovery scenario:** If Flink crashes, it restarts from the last checkpoint. Kafka offsets are restored, and in-flight transactions are rolled back. S3 staging files are cleaned up.

**Reference:** Docs/05-async-messaging.md, Docs/05-async-messaging-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Kafka Consumer Lag Diagnosis & Resolution
**Type:** Calculation

A Kafka topic has 16 partitions, 16 consumers, each ingesting 50 MB/s. Consumer lag grows at 2 GB/minute. Each consumer runs on a c5.2xlarge (8 vCPU, 16 GB RAM). Processing involves deserializing Avro, enriching via Redis lookup, and writing to Elasticsearch. Identify the bottleneck and calculate the resources needed to close the gap.

<details>
<summary>Answer & Explanation</summary>

**Answer:**

**Calculation:**
- Lag growth: 2 GB/min = 34 MB/s lagging per consumer (2GB/60/16).
- Current throughput: 50 MB/s consumed, but only processing 50 - 34 = 16 MB/s successfully.
- Bottleneck likely in Redis lookup (network I/O) or Elasticsearch indexing (bulk write throughput).

**Diagnosis:**
1. Measure CPU: if < 70%, bottleneck is I/O (network or disk).
2. Measure Redis latency P99: if > 10ms per lookup, Redis is the bottleneck.
3. Measure ES bulk indexing throughput.

**Scaling:**
- If Redis is bottleneck: increase number of Redis read replicas, use local cache for hot keys.
- If ES is bottleneck: add ES nodes, increase shards, batch writes (flush every 10s or 1000 docs).
- If CPU: increase partitions + consumers to 32. Each consumer handles ~25 MB/s. Resources needed: 32 c5.xlarge (cheaper) or 16 c5.4xlarge.
- If network: move processing to same AZ as Redis/ES to reduce latency.

**Reference:** Docs/05-async-messaging-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Outbox Pattern with Transactional Outbox
**Type:** Whiteboard

Design a transactional outbox pattern for an order service that writes to both PostgreSQL and Kafka. A single row insertion in the `orders` table must reliably produce a Kafka message. The system handles 10,000 orders/sec. Address failure scenarios where:
1. DB write succeeds, Kafka send fails
2. Kafka send succeeds, DB commit fails
3. The outbox is processed twice

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Design:**
1. **Transactional outbox table:** `order_outbox(order_id, payload, status, created_at)` in the same PostgreSQL database.
2. **Write:** In a single DB transaction: INSERT INTO orders(...) + INSERT INTO order_outbox(...).
3. **Relay (CDC or periodic poll):** Use Debezium to stream outbox inserts → Kafka (CDC approach). Or use a scheduled job that polls for `status = 'PENDING'`, sends to Kafka, and marks as `SENT`.

**Failure handling:**
1. DB succeeds, Kafka fails → outbox row remains PENDING. The relay retries until Kafka acknowledges. No data loss.
2. Kafka send succeeds, DB commit fails → the DB transaction rolls back, so the outbox row never exists. The consumer receives a message for an order that doesn't exist → must handle with idempotency check (look up order_id before processing).
3. Double processing → idempotency key in the outbox. The relay checks for duplicate sends. The consumer uses order_id as idempotency key.

**Reference:** Docs/05-async-messaging-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Kafka Cluster Sizing
**Type:** Calculation

You need to design a Kafka cluster handling 500 TB/day of incoming data. Replication factor = 3. Each message is 1 KB average. Retention = 7 days. Compression ratio = 3:1. Calculate:
1. Total raw data per day including replication
2. Total storage needed (raw vs compressed)
3. Required number of brokers if each broker has 8 × 20 TB disks
4. Estimated partition count and throughput per broker

<details>
<summary>Answer & Explanation</summary>

**Answer:**

1. **Raw data per day:** 500 TB × 3 (replication) = 1500 TB/day.
2. **Compressed data per day:** 1500 / 3 = 500 TB/day.
   **Total storage (7 days):** 500 TB × 7 = 3500 TB raw, ~1167 TB compressed.
3. **Broker count:** Each broker: 8 × 20 TB = 160 TB raw, ~53 TB usable (with RAID 10, 50% = 80 TB). But with replication, each broker stores a replica. Total usable = 3500 TB raw / 80 TB per broker ≈ 44 brokers. With overhead (10% OS, logs): ~50 brokers.
4. **Partitions:** 500 TB/day ÷ 1 KB per msg ≈ 500B messages/day. At 10 MB/s per partition write (typical), a broker handles ~50-100 partitions. Total partitions ≈ 44 brokers × 80 partitions ≈ 3500 partitions. Each broker handles ~1.1 TB/day (compressed) = ~12 MB/s sustained.

**Reference:** Docs/05-async-messaging-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Multi-Region Kafka
**Type:** Whiteboard

Design a multi-region Kafka deployment (active-active) across 3 AWS regions. Producers write locally. Consumers should be able to read any region's data within < 5 seconds of publication. How do you handle cross-region replication, conflict resolution, and disaster recovery?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Design:**
1. **Per-region Kafka clusters** — each region has its own cluster with RF=3 within the region.
2. **MirrorMaker 2** — runs in each region, consumes from remote clusters and produces to the local one. Configure topic replication with `replication.policy` for topic name mangling (or use the same name for active-active).
3. **DR / failover:** Confluent Cluster Linking for real-time replication with offset translation. Or use MirrorMaker 2 with bidirectional sync and `sync.topic.configs.enabled=true`.

**Conflict resolution:** In active-active, use a deterministic rule per topic: either (a) partition key hashed to region (no conflict), (b) last-writer-wins with timestamp, or (c) CRDT-based merge.

**Latency:** Cross-region replication adds RTT (e.g., us-east-1 ↔ us-west-2 ~65ms). For < 5s replication, this is fine. Use `replication.factor` and tune `min.sync.replicas` for durability.

**Disaster recovery:** On full region failure, promote a region to primary, redirect all producers globally via DNS. Consumers in remaining regions already have the data (within 5s lag).

**Reference:** Docs/05-async-messaging-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Queue-Based Load Leveling
**Type:** Debug

A photo-processing service receives unpredictable spikes (10x normal load). Using an SQS queue, workers process images (average 500ms each). During spikes, the queue depth grows to 500K messages. Processing latency increases from 2s to 15 minutes. Customers are unhappy. The team adds more workers (autoscaling), but the latency only drops to 8 minutes. What's wrong?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Likely issues:**
1. **Workers are hitting a downstream bottleneck** (e.g., S3 upload limit, database write throughput, API rate limit). Adding workers just increases contention.
2. **Cold start latency** — new workers take time to warm up (download ML model, connect to DB).
3. **Visibility timeout / redrive** — if processing takes 500ms but the visibility timeout is 30s, a large backlog of messages might be invisible and then reappear, causing duplicate processing.

**Fixes:**
1. Identify and scale the downstream bottleneck. If it's S3, add prefixes. If it's a DB, add read replicas or batch writes.
2. Pre-warm workers (keep a baseline pool running).
3. Implement fast-fail and dead-letter after retry limit.
4. Use priority queuing: process short-running images first, batch long-running ones.
5. Implement back-pressure: reject new uploads early with a clear error rather than delaying all processing.

**Reference:** Docs/05-async-messaging-advanced.md
</details>
