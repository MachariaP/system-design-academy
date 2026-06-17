# Module 11 — Stream Processing & Event-Driven Architectures — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** Log-Centric Architecture
**Type:** Multiple Choice

What does "log-centric architecture" mean in distributed systems?

A) All services write their operations to a central log file
B) A centralized append-only log (e.g., Kafka) serves as the primary communication backbone between services
C) Services only communicate via syslog
D) The system keeps a changelog of all database queries

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** In a log-centric architecture, an append-only commit log (like Kafka) acts as the central nervous system of the system. Services produce events to the log and consume events from it. This decouples producers from consumers, provides durability, and enables replayability. Jay Kreps' "The Log" article popularized this concept.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 2 🟢
**Topic:** Kafka Topic
**Type:** Multiple Choice

What is a Kafka topic?

A) A single message in Kafka
B) A named category or feed to which records are published
C) A consumer group identifier
D) A Kafka cluster node

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** A topic is a logical channel to which producers write records and from which consumers read. Topics are partitioned for parallelism. Each partition is an ordered, immutable sequence of records. The topic name identifies the stream of data (e.g., "order-events", "page-visits").

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 3 🟢
**Topic:** Kafka Partitioning
**Type:** Open-Ended

Why are Kafka topics divided into partitions? How does partitioning affect parallelism?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Partitions enable horizontal scaling: each partition can be hosted on a different broker. Producers write to a specific partition (typically key-based hashing). Each partition is consumed by exactly one consumer in a consumer group (but a consumer can handle multiple partitions). More partitions = more parallelism (more consumers can process concurrently). However, ordering is guaranteed only within a partition, not across partitions.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 4 🟢
**Topic:** Consumer Group
**Type:** Multiple Choice

In a Kafka consumer group, what happens when a consumer joins or leaves?

A) The entire group stops processing
B) Kafka triggers a rebalance, redistributing partitions among the remaining/ new consumers
C) Partitions are permanently assigned to the first consumer
D) The consumer group is recreated from scratch

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** When a consumer joins or leaves a group, Kafka initiates a rebalance. Partition assignments are recomputed and redistributed among the group's consumers. This ensures load balancing (partitions are distributed) and fault tolerance (if a consumer dies, its partitions are reassigned). During rebalance, consumers briefly pause processing (stop-the-world) until the new assignment is complete.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 5 🟢
**Topic:** Event Time vs Processing Time
**Type:** Open-Ended

What is the difference between event time and processing time in stream processing?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Event time is when the event actually occurred (timestamp embedded in the event payload by the producer). Processing time is when the event is processed by the stream processor. These can differ significantly due to network delays, buffering, or system outages. For accurate windowing and analytics, event time is preferred, but it requires handling late-arriving data (events that arrive long after their event time).

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 6 🟢
**Topic:** Kafka Offset
**Type:** Multiple Choice

What is a Kafka offset?

A) The size of a message in bytes
B) The unique position identifier of a record within a partition
C) The timestamp when a message was produced
D) The number of partitions in a topic

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Each record in a Kafka partition has an offset — an integer that uniquely identifies its position. Offsets are sequential and immutable. Consumers track their current offset (the next record to read) and can commit it to mark progress. This enables replay: a consumer can reset its offset to an earlier position to reprocess messages.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 7 🟢
**Topic:** Watermark
**Type:** Open-Ended

What is a watermark in stream processing (e.g., in Flink or Kafka Streams)?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A watermark is a timestamp that declares "no events with event time earlier than this will arrive." It advances as the stream processor sees newer event timestamps. Watermarks handle event-time processing by defining when to trigger computations (e.g., closing a window). An event with event time before the watermark is considered "late" and is either dropped or sent to a side output. Watermark progress is based on observed data, not real-time clock.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 8 🟢
**Topic:** Tumbling vs Sliding Windows
**Type:** Multiple Choice

What is the difference between a tumbling window and a sliding window?

A) Tumbling windows are fixed-size, non-overlapping; sliding windows are fixed-size and may overlap
B) Sliding windows are fixed-size, non-overlapping; tumbling windows may overlap
C) Tumbling windows are based on event time; sliding windows are based on processing time
D) There is no difference — they are synonyms

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** Tumbling windows are fixed-size, non-overlapping (e.g., every 5 minutes — [0:00-0:05), [0:05-0:10)). Sliding windows are also fixed-size but overlap (e.g., 10-minute window sliding every 5 minutes — [0:00-0:10), [0:05-0:15)). Tumbling windows are simpler for per-period aggregations. Sliding windows provide smoother aggregations at the cost of more computations.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 9 🟡
**Topic:** Kafka At-Least-Once vs Exactly-Once
**Type:** Multiple Choice

Which of the following is required for Kafka exactly-once semantics in a producer?

A) `acks=0`
B) `enable.idempotence=true` and `acks=all`
C) `compression.type=gzip`
D) `batch.size=0`

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** For exactly-once semantics, the producer must set `enable.idempotence=true` (prevents duplicate records due to retries) and `acks=all` (ensures all in-sync replicas acknowledge). The broker uses a producer ID and sequence number per partition to deduplicate. For end-to-end exactly-once, consumers must also be configured with `isolation.level=read_committed` and use a transactional producer for the output.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 10 🟡
**Topic:** Lambda vs Kappa Architecture
**Type:** Open-Ended

Compare Lambda Architecture and Kappa Architecture for stream processing. What are the trade-offs of each?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Lambda Architecture:** Has two parallel pipelines — a speed layer (real-time stream processing for low latency) and a batch layer (batch processing for accuracy and completeness). Results are merged in a serving layer. Pro: handles both real-time and historical data. Con: maintaining two code bases for the same logic (stream + batch) leads to inconsistency, operational complexity, and debugging difficulty.

**Kappa Architecture:** A single streaming pipeline for all data. Historical data is replayed through the stream processor from the beginning (using Kafka's log replay). Pro: single code base, simpler operations, no reconciliation needed. Con: requires the stream processor to handle high throughput for historical replays, and some operations (large joins, complex aggregations) may be harder to express as streams.

**When Lambda:** Legacy systems, or when real-time and batch require fundamentally different technologies. **When Kappa:** Greenfield projects, when the stream processor (e.g., Flink, Kafka Streams) can handle both real-time and historical throughput.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 11 🟡
**Topic:** Session Windows
**Type:** Open-Ended

What is a session window and what type of workloads is it suited for? How is a session gap configured?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A session window groups events that occur close together (within a defined "session gap") and closes when no events arrive within that gap. Unlike tumbling/sliding windows, session windows are **data-driven** — their size and boundaries depend on the event pattern, not a fixed time interval.

**Use cases:** User activity sessions (web clicks, mobile app interactions), where a "session" ends after inactivity (e.g., 30 minutes). The gap is the max allowed inactivity period — if a user sends events, then stops for 30 minutes, the window closes. If a new event arrives after 30 minutes, a new session begins.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 12 🟡
**Topic:** Watermark Strategies
**Type:** Open-Ended

In Apache Flink, how does a BoundedOutOfOrderness watermark work? What is the trade-off between low latency and completeness when setting the max-out-of-orderness parameter?

<details>
<summary>Answer & Explanation</summary>

**Answer:** `BoundedOutOfOrderness` watermark strategy assumes events arrive within a fixed maximum delay (e.g., 5 seconds) of their event time. The watermark = max_observed_event_time - max_out_of_orderness. As the processor observes an event with timestamp T, the watermark advances to T - 5s. Any event with event_time < watermark is "late."

**Trade-off:** A smaller max-out-of-orderness (e.g., 1s) means the watermark advances quickly → windows close sooner → results available faster (low latency). But events delayed beyond 1s are dropped as late, reducing completeness. A larger value (e.g., 1 hour) ensures almost all events are captured (high completeness), but windows stay open for an hour → results are delayed by an hour. Choose based on business requirements: fraud detection needs low latency (smaller gap), accurate billing needs completeness (larger gap with allowed lateness).

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 13 🟡
**Topic:** Kafka Producer Acknowledgement
**Type:** Calculation

A Kafka producer sends 10,000 messages/second with `acks=all` and `min.insync.replicas=2`. The cluster has 3 brokers with replication factor 3. What is the throughput impact if one broker fails and the remaining two must handle all write traffic? What happens if another broker fails?

<details>
<summary>Answer & Explanation</summary>

**Answer:** With `acks=all` and `min.insync.replicas=2`, the producer requires acknowledgments from at least 2 in-sync replicas. With 3 brokers, initially all 3 ISRs are available — throughput is distributed.

**One broker fails:** The remaining 2 brokers have 2 ISRs for each partition (if the leader was on the failed broker, a new leader is elected on one of the remaining brokers). `min.insync.replicas=2` is still satisfied. Throughput may drop because partition leaderships are redistributed (each remaining broker handles more leader partitions) and network load is concentrated. Expected throughput: ~60-70% of original.

**Second broker fails:** Only 1 broker remains. `min.insync.replicas=2` cannot be satisfied → the producer gets a `NotEnoughReplicas` exception and stops accepting writes. The cluster becomes unavailable for writes until at least one more broker comes back. This demonstrates the importance of setting `min.insync.replicas` carefully: 2 is safe for 3 brokers but provides no tolerance for double failure. For higher tolerance, increase replication factor or tolerate `min.insync.replicas=1` with the risk of data loss.

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 14 🟡
**Topic:** Late Data Handling
**Type:** Debug

A Flink job computes hourly revenue using event-time tumbling windows. The output is consistently low by ~5% compared to the database's daily reconciliation report. Late-arriving events are allowed with a 10-minute watermark delay. What is the most likely cause and how would you fix it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** **Most likely cause:** Events arriving more than 10 minutes after their event time are being dropped as late. Payment events from mobile devices in low-connectivity areas can be delayed by hours when the device comes back online. The 10-minute watermark allowed lateness is too short.

**Fix:** 
1. Increase the allowed lateness (e.g., to 2 hours) and route late events to a side output instead of dropping them.
2. Create a separate hourly reconciliation job that processes the side output (late events) and produces correction records.
3. Alternatively, use a **daily batch job** that reads from the same Kafka topics (replaying from the beginning) to produce the authoritative daily revenue number. Mark the stream output as "preliminary" and the batch output as "final."

**Reference:** Docs/11-stream-processing.md
</details>

---

## Question 15 🔴
**Topic:** Kafka Partition Rebalance Optimization
**Type:** Whiteboard

A Kafka cluster has a topic with 100 partitions consumed by 10 consumers in one group. When a consumer crashes, rebalancing takes 30 seconds during which all consumers pause processing. The system requires p99 latency under 100ms. Design a solution to reduce rebalance downtime to under 1 second.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Solutions (in increasing order of effectiveness):**

1. **Static group membership** (Kafka 3.1+): Assign consumer instances to group members with unique `group.instance.id`. On rebalance, only the partitions of the failed consumer are reassigned — other consumers keep their assignments and continue processing. This avoids stop-the-world.

2. **Cooperative rebalancing** (`partition.assignment.strategy=CooperativeStickyAssignor`): Instead of revoking all partitions and reassigning (eager rebalancing), cooperative rebalancing revokes a subset of partitions, triggers a rebalance for that subset, then continues. Multiple rounds may be needed but each round is fast.

3. **Reduce partition count per consumer:** With 100 partitions / 10 consumers = 10 partitions per consumer. Each partition revocation takes time (flushing state, committing offsets). Reduce to fewer partitions per consumer (e.g., 200 partitions → 20 per consumer, but fewer consumers).

4. **Run extra standby consumers:** Deploy 12 consumers instead of 10. With rack-aware assignment, the extra consumers act as hot spares. On failure, reassignment is faster because partitions can move to already-running consumers.

5. **Use Kafka Streams with state storage:** Kafka Streams uses cooperative rebalancing by default and stores state in RocksDB, minimizing the cost of moving stateful partitions.

**Recommended approach:** Static group membership (if using Kafka 3.1+) + CooperativeStickyAssignor. This reduces rebalance downtime from stop-the-world to ~100ms per partition reassignment.

**Reference:** Docs/11-stream-processing-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Exactly-Once End-to-End Pipeline
**Type:** Whiteboard

Design an end-to-end exactly-once processing pipeline: Kafka → Flink → S3. A record must be processed exactly once even if Flink crashes mid-processing or Kafka has leader failures. Describe the exact mechanisms at each layer.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Layer 1 — Kafka Source (exactly-once read):**
- Flink uses Kafka transactions to track progress: Flink's Kafka consumer reads messages using `isolation.level=read_committed`.
- Flink periodically checkpoints its state + current Kafka offsets to a durable store (e.g., HDFS, S3), coordinated by Flink's checkpoint coordinator.
- On crash recovery, Flink restores from the last completed checkpoint and resets Kafka offsets to the checkpointed positions — messages between the checkpoint and crash may be re-read, but the sink deduplicates them.

**Layer 2 — Flink Processing (exactly-once state):**
- Flink uses checkpointed state backends (RocksDB or in-memory with file system backup).
- Checkpoints are aligned: all inputs are barriered before processing continues.
- Idempotent operations: if the same record is processed twice (due to offset reset), the state update is idempotent (e.g., adding to a count: processing the same event twice produces the same result if the count increments by the value).

**Layer 3 — Flink Sink to S3 (exactly-once write):**
- Flink uses the `StreamingFileSink` with the **exactly-once** mode. It writes to temporary files (in-progress), then on checkpoint completion, atomically commits (renames/moves) files to final location.
- S3's PUT Object is idempotent for the same object key — uploading the same data twice with the same key produces the same result.
- The sink uses a transaction ID tied to the checkpoint number. On recovery, incomplete files are rolled back (deleted), and already-committed files are visible.

**Result:** End-to-end exactly-once: the same record is never lost and never processed more than once in the final S3 output.

**Reference:** Docs/11-stream-processing-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Stream Processing Anti-Patterns
**Type:** Debug

A team implements a real-time fraud detection system using Kafka Streams. They use a 1-hour sliding window with 1-minute advances to count transactions per user. The system outputs a "fraud score" for each window. Production shows that the score oscillates wildly — high, then low, then high — even though the actual transaction rate is steady. What is happening and how do you fix it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** **Problem:** The sliding window is advancing every minute, but each window is independent. When a high-transaction period rolls out of the window (the 61-minute-old data is dropped) and the window is recalculated, the count drops suddenly. One minute later, it jumps again when new data enters. This creates oscillation because the window calculation uses a **tumbling** approach (recalculating from scratch each advance) rather than an incremental approach.

**Fix:**
1. Use **incremental aggregation** — when a new event arrives, add to the window count; when an event ages out, subtract from the count. This produces a smooth count that doesn't oscillate.
2. If using Kafka Streams, use stateful aggregation with `SlidingWindows` (introduced in Kafka Streams 3.0) that supports incremental sliding windows natively.
3. Alternatively, increase the window advance so it's less frequent relative to the window size, or use a dampening/smoothing function (e.g., exponential moving average instead of a raw count).

**Reference:** Docs/11-stream-processing-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Global Event Ordering Design
**Type:** Whiteboard

Design a system that streams events from 5 data centers to a single Kafka cluster in us-east-1. Events from the same user (keyed by user_id) must be processed in timestamp order. Latency from any DC should be under 500ms. The system produces 1M events/second. How do you handle cross-DC clock skew and partition assignment?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Challenge:** Events from the same user can arrive from different DCs in non-chronological order due to network latency and clock skew.

**Design:**
1. **Partitioning:** Hash by `user_id` to ensure all events for a user land on the same partition, preserving per-user order.
2. **Producer in each DC:** Each DC has a local Kafka producer that sends events to the central cluster. Use `acks=1` for low latency (no wait for all replicas cross-region).
3. **Clock skew mitigation:**
   - **Option A (recommended):** Use hybrid logical clocks (HLC). Each event carries a hybrid timestamp that combines wall clock + logical counter. Brokers use this for ordering within a partition, not the Kafka record timestamp.
   - **Option B:** Use a timestamp-based partition router with a "wait buffer." Each DC's events are buffered for 200ms before publishing to Kafka, allowing for out-of-order arrival of earlier-timestamped events from other DCs.
4. **Consumer-side reordering:** Use a buffer in the stream processor (e.g., Flink) that holds events per user_id for a short window (e.g., 5 seconds), sorts by the HLC timestamp, then processes. This ensures chronological ordering despite network arrival order.
5. **Monitoring:** Track the difference between event time and Kafka append time per DC. Alert if skew exceeds thresholds.

**Reference:** Docs/11-stream-processing-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Kafka Cluster Capacity Planning
**Type:** Calculation

You need to design a Kafka cluster for 500,000 messages/second, average message size 2 KB, with 3× replication and 7-day retention. Each broker has 10 TB of usable storage. Calculate:
1. Total storage required
2. Minimum number of brokers
3. Sustained ingress throughput per broker (write)
4. Recommended partition count if you want 50 MB/s per partition throughput

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **Total storage:** 500,000 msg/s × 2 KB = 1 GB/s ingress. With 3× replication: 3 GB/s write. Per day: 3 GB/s × 86,400 s = 259.2 TB/day. For 7 days: 259.2 × 7 = **~1,814 TB**.
2. **Minimum brokers:** 1,814 TB / 10 TB per broker = ~182 brokers. But also consider throughput. Each broker can handle ~200-300 MB/s write throughput (with fast SSDs and 25 GbE). 1,814 TB / 182 = 10 TB (storage bound). Let's check throughput: 3 GB/s total write / 182 = ~16.5 MB/s per broker. Storage is the bottleneck. **Minimum: ~182 brokers.** (In practice, fewer brokers with larger disks, e.g., 91 brokers with 20 TB each.)
3. **Sustained ingress per broker:** 500,000 × 2 KB = 1 GB/s total ingress / 182 = ~5.5 MB/s per broker (after replication: 3× = ~16.5 MB/s).
4. **Partition count:** Target 50 MB/s per partition throughput max. 1 GB/s total / 50 MB/s = ~20 partitions. But for parallelism and consumer scaling, use a larger number: recommended **100-200 partitions** (each partition will handle 5-10 MB/s, well within limits). Ensure no single broker holds too many leader partitions.

**Reference:** Docs/11-stream-processing-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Kappa Architecture with Historical Replay
**Type:** Open-Ended

A team adopting Kappa Architecture wants to deploy a new streaming job that processes the last 30 days of Kafka data (200 TB) before going live with real-time processing. The Kafka cluster retains only 7 days of data in hot storage. How do you replay the full 30 days? What are the performance implications for the running real-time pipeline?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Approach:**
1. **Archival storage:** Kafka data is archived to S3 (or HDFS) daily in Parquet/Avro format with the same partitioning as the original topic.
2. **Replay mechanism:** The streaming framework (e.g., Flink, Kafka Streams) supports reading from batch sources. Configure a **bounded source** that reads the 200 TB from S3 (30 days of Parquet files) as a batch, then seamlessly transitions to unbounded Kafka consumption.
3. **Parallel replay:** Partition the S3 data by the same keys used in Kafka (e.g., by transaction ID range or day/ hour) and replay in parallel. Use Flink's `Source.ENUMERATE` or Kafka Streams' `KafkaStreams.restore()` from a state store backup.

**Performance implications for real-time pipeline:**
- **No impact if isolated:** Run the replay on a separate Flink cluster/application ID. The real-time pipeline continues independently.
- **If same cluster:** The replay consumes significant CPU and memory resources. Use resource quotas (YARN/Kubernetes resource pools) to limit the replay job to available capacity. Or throttle the replay to use idle resources only (e.g., run overnight, use lower parallelism).
- **State size warning:** Processing 30 days at once will build a large state (RocksDB). Ensure the state can fit in the available disk (possibly 30× the real-time state size). Use incremental checkpointing and plan for a longer recovery time.

**Reference:** Docs/11-stream-processing-advanced.md
</details>
