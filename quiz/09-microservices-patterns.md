# Module 9 — Microservices Patterns & Transactional Integrity — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** Saga Pattern
**Type:** Multiple Choice

What is the purpose of the Saga pattern in microservices?

A) To enable synchronous communication between services
B) To manage distributed transactions across multiple services with compensating actions on failure
C) To replace the need for a database
D) To implement service discovery

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** A Saga is a sequence of local transactions where each step publishes an event or triggers the next step. If a step fails, the Saga executes compensating transactions to undo previous steps. This maintains data consistency without requiring distributed ACID transactions (2PC).

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 2 🟢
**Topic:** Choreography vs Orchestration
**Type:** Multiple Choice

In the choreography-based Saga, how do services coordinate?

A) A central coordinator tells each service what to do
B) Each service listens for events and decides locally what to do next
C) Services communicate via direct REST calls in a chain
D) A database trigger manages the workflow

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** In choreography, each service produces events after completing its local transaction, and other services consume events they are interested in. There is no central coordinator. In orchestration, an orchestrator service explicitly tells each participant what to do and tracks the overall state.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 3 🟢
**Topic:** Transactional Outbox
**Type:** Open-Ended

What is the Transactional Outbox pattern and what problem does it solve?

<details>
<summary>Answer & Explanation</summary>

**Answer:** The Transactional Outbox pattern solves the dual-write problem: when a service must write to a database AND send a message/event atomically. Instead of writing to DB and then sending a Kafka message (which can fail after the DB write), the service writes both the business data and an outbox record in the same database transaction. A separate process (outbox publisher) reads the outbox table and publishes the events, ensuring exactly-once or at-least-once delivery.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 4 🟢
**Topic:** CQRS
**Type:** Multiple Choice

What does CQRS stand for and what is its core idea?

A) Command Query Responsibility Segregation — separate models for reading and writing data
B) Complete Query Response System — a caching layer for queries
C) Concurrent Query and Replication System — a database replication strategy
D) Centralized Query Routing Service — a query load balancer

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** CQRS separates the read model (queries) from the write model (commands). The write model handles validation and persistence; the read model is optimized for query performance and may be in a completely different store (e.g., write to PostgreSQL, read from Elasticsearch). This allows independent scaling and optimization of read and write workloads.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 5 🟢
**Topic:** Database per Service
**Type:** Open-Ended

What does "database per service" mean in a microservices architecture and what is its primary benefit?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Each microservice owns its private database — no other service can access it directly. Services communicate only via APIs or events. The primary benefit is **loose coupling**: a service can change its schema, choose the best database technology for its needs (relational, document, graph), and scale independently without affecting other services.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 6 🟢
**Topic:** Event Sourcing
**Type:** Multiple Choice

In event sourcing, what is stored as the source of truth?

A) The current state of each entity
B) An append-only log of every state-changing event
C) A diff between the previous and current state
D) Only the latest snapshot of each entity

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Event sourcing stores the full sequence of events that have changed an entity's state, not just the current state. The current state is derived by replaying all events (or applying a snapshot + subsequent events). This provides a complete audit trail and enables temporal queries ("what was the state at time T?").

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 7 🟢
**Topic:** CDC (Change Data Capture)
**Type:** Multiple Choice

What does Change Data Capture (CDC) do?

A) Captures changes made to a database and streams them as events
B) Periodically takes full database snapshots
C) Replicates the entire database schema
D) Monitors database CPU utilization

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** CDC captures insert, update, and delete operations from a database's transaction log (binlog, WAL) and streams them as change events. Tools like Debezium connect to these logs and publish events to Kafka. This enables real-time data synchronization, cache invalidation, and event-driven architectures without modifying the application code.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 8 🟢
**Topic:** 2PC (Two-Phase Commit)
**Type:** Open-Ended

What are the two phases of the Two-Phase Commit (2PC) protocol?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Phase 1 — **Prepare:** The coordinator sends a prepare request to all participants. Each participant writes the transaction to a durable log and replies "yes" (ready) or "no" (abort). Phase 2 — **Commit/Abort:** If all participants replied "yes", the coordinator sends a commit message. If any replied "no", it sends an abort. Each participant then commits or rolls back.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 9 🟡
**Topic:** Saga Orchestration
**Type:** Open-Ended

Design a Saga for an e-commerce order flow: Reserve Inventory → Process Payment → Ship Order. Describe the steps and compensating transactions. Would you use choreography or orchestration and why?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Steps:** 1. Order Service creates order (PENDING status). 2. Inventory Service reserves items. 3. Payment Service charges the card. 4. Shipping Service creates shipment.

**Compensations:** If payment fails → Inventory Service releases reservation. If shipping fails → Payment Service refunds the charge, Inventory Service releases reservation.

**Choice: Orchestration.** An Order Orchestrator service manages the flow. For an e-commerce system, orchestration is preferred because: (a) the flow is complex with branching (e.g., digital vs physical goods), (b) you need a single source of truth for order state, (c) compensating actions are easier to track and retry.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 10 🟡
**Topic:** Debezium CDC
**Type:** Multiple Choice

When using Debezium for CDC, why does it typically use Kafka Connect?

A) Kafka Connect provides a distributed, fault-tolerant runtime for running Debezium connectors
B) Kafka Connect transforms CDC data into GraphQL
C) Kafka Connect replaces the source database
D) Kafka Connect is the only way to read database transaction logs

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** Debezium connectors run on Kafka Connect, which provides a distributed, scalable framework for running source/sink connectors. Kafka Connect handles configuration management, offset tracking (which log position was last read), rebalancing when workers join/leave, and exactly-once semantics for streaming data into Kafka topics.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 11 🟡
**Topic:** CQRS + Event Sourcing
**Type:** Open-Ended

How does CQRS complement event sourcing? What is a "projection" and how does it populate the read model?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Event sourcing stores events as the source of truth. CQRS separates the read model from the write model. A **projection** subscribes to the event stream, processes events in order, and builds a denormalized read model optimized for queries. For example, the write model stores "UserRegistered", "ItemAddedToCart", "OrderPlaced" events. A projection builds a "UserOrderSummary" read model that aggregates this data for fast dashboard queries. This combines the auditability of event sourcing with the query performance of CQRS.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 12 🟡
**Topic:** Event Sourcing Snapshots
**Type:** Open-Ended

Why are snapshots needed in event sourcing? How does the snapshot frequency affect performance?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Without snapshots, rebuilding the current state of an entity requires replaying all events since the beginning — which becomes increasingly expensive as the event log grows. A snapshot captures the state at a point in time. To rebuild state, you load the latest snapshot and replay only events after the snapshot. Trade-off: more frequent snapshots reduce replay time but increase write overhead and storage. Common strategies: snapshot every N events (e.g., 100), or snapshot when the event count since last snapshot exceeds a threshold.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 13 🟡
**Topic:** Transactional Outbox Implementation
**Type:** Debug

A team implements the Transactional Outbox pattern but observes duplicate message delivery during a database failover. The outbox publisher reads records that were not yet marked as published. Why does this happen and how do you ensure idempotent processing?

<details>
<summary>Answer & Explanation</summary>

**Answer:** During failover, the outbox publisher may read the same records twice if the database connection is interrupted after reading but before marking the record as "published". The new publisher instance (or the restarted one) scans the outbox table and finds the same records again.

**Fix:** Make the consumer idempotent — each message carries a unique deduplication ID (can be the outbox record ID or a UUID). The consumer stores processed message IDs in a deduplication table and skips any message it has already processed. Alternatively, use Kafka's exactly-once semantics with the outbox publisher writing to Kafka with `idempotence=true` and `acks=all`.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 14 🟡
**Topic:** 2PC Failure Scenarios
**Type:** Open-Ended

What happens in 2PC if the coordinator crashes after sending the prepare request but before receiving all responses? How is this resolved?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Participants that have replied "yes" are now in a **prepared (ready)** state — holding locks and resources, waiting for the coordinator's decision. They cannot decide independently whether to commit or abort (they are blocked). **Resolution:** The coordinator writes its state to a durable transaction log before each step. On recovery, the coordinator reads the log to determine the state of the transaction (preparing vs prepared vs committing) and resumes from where it left off. If the coordinator is permanently down, a human operator or a dedicated recovery process must query participants and manually resolve. This blocking property is the main reason 2PC is avoided in distributed systems.

**Reference:** Docs/09-microservices-patterns.md
</details>

---

## Question 15 🔴
**Topic:** Distributed Transaction Failure Analysis
**Type:** Debug

A financial system uses a choreography-based Saga for a money transfer: Service A (Debit) emits "DebitCompleted", Service B (Credit) listens and credits the account. A bug causes Service A to emit "DebitCompleted" without actually debiting the account. The credit succeeds. The money is created out of thin air. How would you design a system to detect and prevent such inconsistencies?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Prevention:** Use the Transactional Outbox pattern — the debit operation and the "DebitCompleted" event must be written atomically in the same database transaction. If the debit fails, the event is never written.

**Detection (even with outbox):** Implement a **Saga Log Auditor** — a background process that reads all saga events and validates each flow:
1. For each saga instance, verify that a "DebitSucceeded" event is preceded by a valid debit transaction record.
2. Run reconciliation: sum of all "DebitSucceeded" amounts should equal sum of all "CreditCompleted" amounts within a time window (allowing for in-flight).
3. If a "DebitSucceeded" exists without a corresponding debit entry, trigger an alert and execute a compensating transaction (reverse the credit).

**Additional:** Add a "saga_id" to all events and transactions. The auditor traces the complete flow and flags any missing or inconsistent steps.

**Reference:** Docs/09-microservices-patterns-advanced.md
</details>

---

## Question 16 🔴
**Topic:** CQRS + Event Sourcing at Scale
**Type:** Whiteboard

Design a CQRS + Event Sourcing system for a trading platform processing 100,000 orders/second. The read model must support real-time queries (current positions within 500ms) and historical analytics (P&L over time). Address event store scaling, projection performance, and read model consistency.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Event Store:** Use Apache Kafka as the event store (Kafka is an append-only log, naturally ordered). Partition by `account_id` to maintain ordering per account. Retention: 7 days hot on Kafka, archived to S3/Parquet for longer queries.

**Write Model:** Services write commands to Kafka as events. Each service maintains a small local state using a compacted topic (latest value per key) for fast lookups.

**Projections:** Use Kafka Streams or Apache Flink for stateful stream processing. Each projection (current positions, P&L, risk metrics) runs as a separate Kafka Streams application with its own state store (RocksDB). Scale projections by partitioning — one task per Kafka partition.

**Read Model:** Write projection results to a low-latency store like Redis (current positions) or Elasticsearch (searchable historical data). For historical P&L, use pre-aggregated time-series in ClickHouse or TimescaleDB.

**Consistency:** Projections are **eventually consistent** with the event store. For read-your-writes, the API can pass the last event offset — the read model checks if it has processed up to that offset, or the API reads from the write model if needed.

**Reference:** Docs/09-microservices-patterns-advanced.md
</details>

---

## Question 17 🔴
**Topic:** CDC Pipeline Disaster Recovery
**Type:** Whiteboard

A team runs Debezium CDC streaming 50 database tables to Kafka. A misconfiguration causes the Debezium connector to lose its offset tracking. Re-snapshotting all 50 tables would take 12 hours and the Kafka topic retention is only 24 hours. Design a recovery strategy that minimizes data loss and downtime.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Immediate recovery:**
1. Stop the Debezium connector immediately to prevent further data loss.
2. Determine the last known offset from Kafka consumer group offsets (if any consumers processed the CDC events) or from the downstream sink's state.
3. Create a **selective re-snapshot** — use Debezium's "ad hoc snapshot" feature to re-snapshot only tables where offset recovery is impossible. For other tables, advance the offset manually using database metadata (e.g., the current MySQL binlog position from `SHOW MASTER STATUS`).

**Fallback:**
4. Start a new connector with a fresh Kafka topic (e.g., `dbserver2.public.table`). This avoids the 24-hour retention limit — you get a complete snapshot in the new topic.
5. Backfill the downstream sinks: compare the old topic's remaining data (last 24h) with the new snapshot and deduplicate.

**Long-term prevention:**
- Store Debezium connector offsets in a dedicated Kafka topic with infinite retention, not the default `__consumer_offsets`.
- Monitor offset lag and set up alerts for stale offsets.
- Back up offset storage to S3 periodically.

**Reference:** Docs/09-microservices-patterns-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Orchestrated Saga Failure Modes
**Type:** Debug

An orchestrated Saga for a hotel booking system has 5 steps: Reserve Room → Charge Card → Book Flight → Send Confirmation → Update Loyalty Points. The Charge Card step is idempotent. The Book Flight step is NOT idempotent (calling it twice books two seats). The orchestrator crashes after executing Book Flight but before marking it as completed in its state store. Upon recovery, the orchestrator re-executes Book Flight, booking a duplicate seat. Design the fix.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Problem:** The orchestrator crashes between executing Book Flight (call to flight API succeeded) and persisting the state (marking step as completed). On recovery, it re-executes the last command because the state still shows it as pending.

**Fix options:**
1. **Idempotency key (recommended):** The orchestrator generates a unique idempotency key per saga step (e.g., `saga_id + step_name`) and passes it to each service. The Flight Service checks if it has already processed this key: if yes, return the existing result instead of booking again. This is the most robust solution.
2. **Atomic execution + state persistence:** Execute the flight booking call AND persist the state change in a single transaction using the Transactional Outbox/Inbox pattern. The orchestrator writes "Book Flight command" + state change to its outbox atomically. A publisher dispatches the command reliably.
3. **Compensation on recovery:** After recovery, the orchestrator checks the actual state by querying the flight service (does this reservation exist?) before deciding to re-execute. This requires the flight service to expose a query endpoint.

**Reference:** Docs/09-microservices-patterns-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Database-per-Service Query Challenge
**Type:** Whiteboard

A microservices system uses database-per-service. The Product Service (PostgreSQL), Inventory Service (PostgreSQL), and Pricing Service (DynamoDB) each own their data. A new requirement demands a "Product Detail" page showing product info, stock level, and price. How do you implement this query without coupling the services or running distributed joins? Compare an API composition approach vs a CQRS approach.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**API Composition:** The Product Detail API (a BFF or API gateway) calls Product Service → returns product data, then calls Inventory Service → returns stock, then calls Pricing Service → returns price. The API gateway merges the results. Pro: simple, always reads fresh data. Con: N+1 calls add latency (3 sequential calls = at least 3× RTT), one failure degrades the whole response, and load on each service increases with page views.

**CQRS with joint projection:** A subscription/reconciliation process listens to events from all three services (ProductUpdated, InventoryChanged, PriceChanged) and builds a denormalized "ProductDetail" read model in a fast store (e.g., Elasticsearch, Redis, or a dedicated PostgreSQL read replica). The Product Detail API serves from this read model with a single query. Pro: O(1) query, high performance, services stay decoupled. Con: eventual consistency (brief staleness), additional infrastructure and maintenance.

**Recommendation:** Use CQRS for high-traffic pages where latency matters. Use API composition for low-traffic administrative pages where freshness is critical.

**Reference:** Docs/09-microservices-patterns-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Distributed Saga Idempotency Design
**Type:** Calculation

A Saga has 5 steps, each with a 1% independent failure probability. The compensating transaction for each step also has a 1% failure probability. What is the probability that the overall Saga fails to complete? What architectural changes reduce this to under 0.1%?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
A Saga succeeds if all 5 steps succeed, OR if any step fails and all preceding compensations succeed. Calculate the probability of the happy path: 0.99^5 = 95.1%. For failures, we need to consider each step where failure occurs and all compensations for preceding steps succeed.

**Probability of ultimate failure** = probability of a step failing AND its compensation also failing.

For simplification, consider the worst-case scenario: failure at step 5 requires compensating steps 1-4. If any compensation fails, the saga is stuck.

The chance of the Saga not ultimately completing is approximately:
- No failure: 0.99^5 = 0.951
- Single failure at step k (all previous compensations succeed): roughly sum across k of (0.99^(k-1) × 0.01 × 0.99^(k-1)) — the compensation failure for the same step.

A more precise model using failure of compensations: The probability of not reaching a consistent end state ≈ 1 - [0.99^5 + Σ(failure modes)]. With 1% compensation failure and up to 4 compensations potentially needed, the failure probability is approximately **1 - 2%**.

**Architectural changes to get under 0.1%:**
1. **Make all steps idempotent** — compensations become no-ops if the step was never executed, eliminating compensation failures.
2. **Increase retries with exponential backoff** — retry up to 5 times reduces per-step failure from 1% to 10^-10.
3. **Add a saga coordinator with durable state and a dead-letter queue** — human operator can manually resolve stuck sagas.
4. **Use at-least-once delivery with idempotent consumers** — retries handle transient failures.

With idempotent steps + 5 retries, effective failure probability per step drops to 10^-10, making overall saga failure effectively 0%.

**Reference:** Docs/09-microservices-patterns-advanced.md
</details>
