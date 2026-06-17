# Module 14 — System Design Interview Framework — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** 4-Phase Whiteboard Roadmap
**Type:** Multiple Choice

What are the four phases of a system design interview according to the standard framework?

A) Code, Test, Deploy, Monitor
B) Requirements Clarification, High-Level Design, Deep Dive, Summary/Trade-offs
C) Requirements, Architecture, Implementation, Testing
D) Brainstorm, Sketch, Prototype, Launch

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** The standard system design interview framework: 1. **Requirements clarification** — scope the problem (functional + non-functional), estimate scale. 2. **High-level design** — sketch core components, data flow, API design. 3. **Deep dive** — focus on the most interesting or contentious component (database sharding, consistency model, caching strategy). 4. **Summary and trade-offs** — discuss bottlenecks, alternatives, and what you'd do with more time.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 2 🟢
**Topic:** Requirements Bounding
**Type:** Multiple Choice

When the interviewer says "design a URL shortener," which question is most important to ask first?

A) What programming language should I use?
B) What are the scale requirements? (Number of URLs created per day, redirects per second, data retention)
C) Should I use a monorepo?
D) What is the company's stock ticker?

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Before any design, you must understand the scale. A URL shortener for 100 URLs/day is different from one for 100M URLs/day. Clarifying scale determines: storage requirements (database choice), throughput (caching needs), availability targets, and cost constraints. Always bound the problem first.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 3 🟢
**Topic:** Trade-off Articulation
**Type:** Open-Ended

In a system design interview, why is it important to explicitly discuss trade-offs rather than just presenting a solution?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Discussing trade-offs demonstrates deeper understanding. Every engineering decision involves trade-offs (consistency vs availability, cost vs latency, simplicity vs flexibility). Articulating them shows you understand the problem holistically, can defend your choices, and can adapt the design to different constraints. It also prevents the interviewer from thinking you chose a technology by rote rather than by analysis.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 4 🟢
**Topic:** Defensive Whiteboarding
**Type:** Multiple Choice

What does "defensive whiteboarding" mean in a system design interview?

A) Protecting your whiteboard from being erased by the interviewer
B) Anticipating and preemptively addressing failure modes, bottlenecks, and edge cases in your design
C) Using physical barriers to block the interviewer's view
D) Drawing diagrams in a specific security-cleared format

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Defensive whiteboarding means proactively identifying weak points in your design before the interviewer points them out. Examples: "This single database is a SPOF — let me add a replica and failover." "This cache could have a cold-start problem — let me pre-warm it." "The write path is synchronous — this could cause backup under load, let me add a queue." It shows systems thinking and experience.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 5 🟢
**Topic:** Rubric Scoring
**Type:** Open-Ended

What are the typical scoring dimensions for a system design interview at FAANG companies?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Typical dimensions (weight varies by company): 1. **Requirements gathering** — did you scope the problem correctly? 2. **High-level design** — is the architecture coherent and well-communicated? 3. **Deep dive** — depth of knowledge on the chosen focus area. 4. **Trade-offs** — awareness of alternatives and their implications. 5. **Communication** — clarity, pacing, collaboration (did you treat the interviewer as a teammate?). 6. **Breadth** — knowledge across storage, networking, databases, caching, etc. 7. **Scale** — did you address the scale constraints appropriately?

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 6 🟢
**Topic:** Anti-Patterns
**Type:** Multiple Choice

Which of the following is a common anti-pattern in system design interviews?

A) Asking clarifying questions about scale
B) Jumping straight to a solution without understanding requirements
C) Discussing trade-offs aloud
D) Using a whiteboard to sketch the architecture

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Jumping to a solution without understanding requirements is the #1 anti-pattern. It leads to designs that don't match the problem's scale or constraints. Interviewers deduct points for not scoping the problem. Other anti-patterns: over-engineering (adding Kafka to a 100 QPS system), being rigid about technology choices, and not acknowledging trade-offs.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 7 🟢
**Topic:** Follow-Up Handling
**Type:** Open-Ended

An interviewer asks: "How would you handle a 100× traffic spike?" What is the correct approach to answering this?

<details>
<summary>Answer & Explanation</summary>

**Answer:** First, clarify the nature of the spike (expected vs unexpected, duration, is it read-heavy or write-heavy?). Then discuss:
1. **Auto-scaling** — add more application servers (horizontal scaling).
2. **Caching** — absorb read spikes with Redis/CDN.
3. **Rate limiting / load shedding** — queue or drop non-critical requests.
4. **Database** — read replicas absorb read spikes, connection pooling limits impact.
5. **Graceful degradation** — disable non-critical features.
6. **Pre-warming** — for expected spikes (e.g., Black Friday), scale up ahead of time.
Do not panic — walk through the layers methodically.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 8 🟢
**Topic:** Synthesis of All Modules
**Type:** Open-Ended

Name at least three modules from the System Design Academy curriculum that are relevant when designing a chat application and explain briefly why each matters.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 1. **Traffic Routing (Module 1)** — WebSocket connection management, load balancing persistent connections, DNS for global presence. 2. **Database Scaling (Module 2)** — Sharding messages by user_id, read replicas for message history. 3. **Async Messaging (Module 5)** — Kafka/RabbitMQ for message delivery between sender, receiver, and push notification services. 4. **Caching (Module 3)** — Redis for presence status, recent messages, and session state. 5. **Consensus (Module 12)** — Ensuring reliable message ordering and delivery guarantees.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 9 🟡
**Topic:** Requirements Clarification Framework
**Type:** Open-Ended

List at least 5 clarifying questions you should ask when asked to "design Twitter." Group them into functional, non-functional, and scale categories.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Functional:** 1. Can users post text-only or also images/video? 2. Is the timeline algorithmic or chronological? 3. Can users retweet, like, and reply? 4. Is there a direct messaging feature? 5. Is there a "trending topics" feature?

**Non-functional:** 6. What is the latency target for loading the timeline? 7. Is the system expected to be always available or can it tolerate brief downtime? 8. What consistency level is needed (e.g., should a tweet appear immediately on all followers' timelines?)?

**Scale:** 9. How many MAU? How many tweets per day? 10. What is the read-to-write ratio? 11. How many followers does the average user have? What about the top 1% of users?

These questions bound the problem and guide architectural choices (e.g., fanout on write vs fanout on read).

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 10 🟡
**Topic:** Deep Dive Selection
**Type:** Open-Ended

During a system design interview for a "design YouTube" question, you've presented the high-level design. The interviewer asks: "Let's dive deeper into the video upload pipeline." What specific sub-topics should you cover in this deep dive?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 1. **Upload flow:** Client uploads to a temporary storage (presigned URL), triggers a transcoding job. 2. **Transcoding pipeline:** Chunk video, encode to multiple resolutions (360p, 720p, 1080p, 4K), codec selection (H.264, VP9, AV1), segmenting for DASH/HLS streaming. 3. **Storage:** Object store for raw and transcoded videos, metadata in a relational DB. 4. **Processing orchestration:** Message queue or workflow engine (e.g., Temporal) to track transcoding status, trigger notifications. 5. **Thumbnail generation:** Extract frames at intervals, select representative thumbnail. 6. **Content moderation:** Scan video for copyright, violence, adult content. 7. **Error handling:** What if transcoding fails? Partial uploads? Notify user, allow retry.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 11 🟡
**Topic:** Trade-off Analysis Structure
**Type:** Multiple Choice

When discussing trade-offs in a design review, which structure is most effective?

A) "Technology X is better than Y because I know it well"
B) "Choosing X gives us benefit A but costs B; choosing Y gives us benefit C but costs D. Given our constraint of E, I recommend X"
C) "Let's use both X and Y"
D) "We'll figure out the trade-offs in implementation"

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** An effective trade-off analysis clearly states the options, the pros and cons of each, and ties the recommendation back to the requirements/constraints. Example: "Using PostgreSQL gives us strong consistency and transactional support but requires manual sharding at scale. Using Cassandra gives us linear scalability but only eventual consistency. Since our system needs strong consistency for payments, I choose PostgreSQL with application-level sharding."

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 12 🟡
**Topic:** Interview Anti-Pattern Recognition
**Type:** Debug

A candidate is asked to "design a rate limiter." They immediately draw a Redis cluster and start explaining Redis data structures. What anti-patterns are they committing?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 1. **Jumping to solution without requirements** — did they ask: How many requests? Which algorithm? Distributed or single-node? Per-user or per-IP? 2. **Over-engineering** — not all rate limiters need a distributed Redis cluster. A single-node token-bucket in application memory is fine for many cases. 3. **Lack of defense** — they didn't discuss availability, latency impact, or failure modes of Redis. 4. **No trade-off discussion** — they didn't compare token bucket vs sliding window vs leaky bucket approaches, or consider the cost of Redis.

**Better approach:** Ask clarifying questions first. Present multiple options (local in-memory vs distributed Redis). Discuss trade-offs (Redis adds latency and complexity, local is simpler but less accurate across nodes). Recommend based on requirements.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 13 🟡
**Topic:** Time Management in Interviews
**Type:** Open-Ended

You have 40 minutes to design a system. How do you allocate time across the four phases? What do you do if you spend too long on requirements and only have 10 minutes left for the deep dive?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Suggested time allocation: 5 min — Requirements and estimation. 15 min — High-level design (boxes and arrows, data flow, API). 15 min — Deep dive (most interesting or contentious component). 5 min — Summary and trade-offs.

**If you're behind:** Don't panic. Prioritize: (1) Quickly solidify the high-level design — it's the most heavily weighted. (2) Choose ONE component for a focused deep dive — depth over breadth. (3) Skip the detailed estimation in requirements (just estimate order of magnitude). (4) If only 10 min left, combine deep dive and summary: "The most critical component is X because Y. Let me walk through it quickly. The main trade-off is A vs B. Given our constraints, I recommend A."

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 14 🟡
**Topic:** Non-Functional Requirement Trade-offs
**Type:** Open-Ended

Compare the trade-offs between prioritizing strong consistency vs high availability in a system design. Give an example where each is the right choice.

<details>
<summary>Answer & Explanation</summary>

**Answer:** **Strong consistency (CP from CAP):** All nodes see the same data at the same time. Trade-off: lower availability during partitions (the minority partition is unavailable). Example: Banking transactions — if the system can't guarantee that a withdrawal isn't counted twice, it should refuse the request (unavailable) rather than risk inconsistency.

**High availability (AP from CAP):** The system remains available even during partitions, at the cost of potential stale reads or conflicts. Example: Social media feed — if a user's tweet can't reach all followers immediately during a partition, it's acceptable. Better to show a slightly stale feed than show an error.

**Reference:** Docs/14-interview-framework.md
</details>

---

## Question 15 🔴
**Topic:** Multi-Module Synthesis — Design a Ride-Sharing App
**Type:** Whiteboard

Design Uber's backend. Walk through the full 4-phase approach, specifically addressing:
1. How does the system match riders with nearby drivers in real time?
2. How does the pricing engine calculate surge pricing?
3. How does the system handle consistency between driver location updates and ride assignment?
4. What modules from the Academy curriculum apply?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Phase 1 — Requirements:** 10M daily rides, 5M drivers. p95 ETA accuracy < 5s. Read-heavy (location polling every 3s). Real-time matching SLA < 2s.

**Phase 2 — High-Level Design:**
- **Location service:** Drivers report GPS via WebSocket → ingested into a high-write-throughput store (Redis/GEO or Apache Kafka + stream processor).
- **Matching service:** When a rider requests a ride, query the GEO index for nearby drivers, score candidates (distance, rating, surge multiplier), dispatch via push notification.
- **Pricing engine:** Compute surge based on supply/demand ratio in a geohash region. Use historical data + real-time demand.
- **Trip service:** Once matched, manage trip lifecycle (start, track, end, payment).

**Phase 3 — Deep dive (Matching):**
- **GEO index:** Use bounded geohash queries in Redis (GEORADIUS) — O(log N). For higher scale, partition geohash tiles across shards.
- **Surge pricing:** Stream demand events (ride requests) and supply events (driver online status) into a windowed aggregation (e.g., Flink). Compute utilization per geohash cell every 30s. If demand/supply > threshold, apply multiplier.
- **Consistency:** Driver locations are eventually consistent (they stream every 3s). Accept stale reads (< 3s) for matching. Use idempotent dispatch (driver can accept/reject; if no response in 10s, dispatch to next candidate).

**Phase 4 — Trade-offs:** Geo-index in Redis is fast but not persistent (need backup). Surge pricing could be gamed by drivers clustering. Write-heavy location updates need careful Kafka partitioning.

**Academy modules:** Async Messaging (Module 5) for ride dispatch, Database Scaling (Module 2) for trip data, Caching (Module 3) for GEO, Traffic Routing (Module 1) for WebSocket management, Consensus (Module 12) for payment consistency.

**Reference:** Docs/14-interview-framework-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Whiteboard Presentation Scoring
**Type:** Whiteboard

Simulate a system design interview: You are asked to design a payment system that processes $1B in transactions daily, operates globally, requires 99.999% availability, and must never lose or duplicate a transaction. Walk through the full 4-phase framework with a focus on idempotency, reconciliation, and failure handling.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Phase 1 — Requirements:** 1M transactions/day (average $1,000). 5x peak during holidays. 99.999% availability (< 5 min downtime/year). No data loss. Idempotent retry. Support 10+ currencies and 5+ payment providers.

**Phase 2 — High-Level Design:**
- **API Gateway:** Accepts payment requests with idempotency key (UUID). Validates, rate limits.
- **Payment Service:** Core orchestration. Creates transaction record (PENDING), routes to the appropriate payment provider adapter.
- **Provider Adapters:** Normalize provider-specific APIs. Handle retries and webhooks.
- **Ledger Service:** Double-entry accounting (debit user wallet, credit merchant wallet). Append-only.
- **Reconciliation Service:** Batch comparison of internal ledger vs provider settlement reports.

**Phase 3 — Deep dive (Idempotency and Failure Handling):**
- **Idempotency:** Every payment request carries an idempotency key. Payment Service checks idempotency store (DynamoDB/Cassandra) for duplicates. If key exists, return the existing result. If not, proceed with idempotency guarantee.
- **Multi-step failure:** If the provider responds but the response is lost (network failure), the client retries with the same idempotency key. Payment Service checks the provider's transaction status via a GET API (provider-side idempotency).
- **Exactly-once:** Use Transactional Outbox pattern — write payment event + state transition atomically. Outbox publisher pushes to Kafka for downstream (notifications, analytics).
- **Saga:** If a payment succeeds but the ledger update fails, a compensating transaction reverses the payment.

**Phase 4 — Trade-offs:** Centralized ID store is a SPOF — use multi-region replication. Idempotency keys have a TTL (pick 24h for payments). Reconciliation is eventually consistent — accept a 24h lag.

**Reference:** Docs/14-interview-framework-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Handling Hostile Follow-Up Questions
**Type:** Open-Ended

An interviewer aggressively questions your database choice: "Why would you use PostgreSQL for this? Everyone knows NoSQL is better for scale. You clearly don't understand modern systems." How do you respond professionally and demonstrate depth?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Stay calm and don't get defensive. Acknowledge the point while defending your reasoning:

"I understand that NoSQL systems like Cassandra or DynamoDB are popular for horizontal scaling. Let me explain my reasoning given our requirements:

1. **Consistency requirements:** This system needs strong consistency for the transaction ledger. PostgreSQL's ACID properties guarantee this, while Cassandra only offers eventual consistency.
2. **Data model:** Our data is highly relational (users ↔ accounts ↔ transactions ↔ merchants). A relational model with joins and foreign keys is more natural and less complex than joining data in application code.
3. **Scale:** We estimated 10K writes/s and 50K reads/s. With appropriate sharding (e.g., Citus extension) and read replicas, PostgreSQL handles this comfortably. We can always migrate specific high-throughput partitions to NoSQL if needed.

**Trade-off acknowledged:** PostgreSQL is harder to shard than Cassandra. If we grew 10× beyond our estimate, we would need application-level sharding or migrate to CockroachDB/Spanner. For our current scale, the development simplicity and consistency guarantees of PostgreSQL outweigh the scaling flexibility of NoSQL."

This response shows depth, acknowledges trade-offs, and demonstrates you thought about the problem rather than blindly choosing a technology.

**Reference:** Docs/14-interview-framework-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Design Critique and Improvement
**Type:** Debug

A junior engineer presents this design for a real-time analytics dashboard: "Collect events via REST API → write directly to PostgreSQL → dashboard queries PostgreSQL every 10 seconds." Identify at least 4 problems and redesign the pipeline.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Problems:** 
1. **Write bottleneck:** Every event is an individual REST API call + PostgreSQL INSERT. Under 100K events/s, PostgreSQL becomes the bottleneck (WAL writes, index updates per row).
2. **Query performance:** Dashboard queries on the same DB that handles writes will contend for resources. Aggregation queries (COUNT, SUM, GROUP BY) on raw event data are slow.
3. **Data structure:** Raw events are not pre-aggregated. Querying "users in last hour" requires scanning millions of rows.
4. **No buffering:** If the DB goes down, events are lost (no message queue).
5. **Polling:** Dashboard polls every 10s instead of pushing updates, wasting resources.

**Redesigned pipeline:**
1. **Ingest:** Events → REST API → **Kafka** (buffering, durability, replay).
2. **Stream process:** Kafka Streams / Flink reads from Kafka, aggregates in **tumbling windows** (e.g., count per minute, p50/p99 latency per route).
3. **Write aggregates:** Pre-aggregated results written to **ClickHouse or TimescaleDB** (columnar, optimized for time-series queries).
4. **Dashboard:** Reads from ClickHouse via HTTP API. Alternatively, push updates via **WebSocket** from the stream processor for real-time display.
5. **Dead letter:** Failed events go to a dead-letter queue for debugging.

**Benefits:** Kafka decouples producers from consumers. Stream processor handles aggregation at scale. Columnar store enables sub-second queries on billions of events.

**Reference:** Docs/14-interview-framework-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Full Whiteboard Simulation
**Type:** Whiteboard

Design a global file storage and sharing platform (like Google Drive) from scratch. Walk through all 4 phases. Cover: chunking and sync protocol, conflict resolution for concurrent edits, offline support, and sharing/permissions. Use the curriculum's 14 modules to justify your choices.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Phase 1 — Requirements:** 1B users, 10 PB storage, 10M concurrent sync operations. Sync latency < 30s. Support files up to 5 TB.

**Phase 2 — High-Level Design:** 
- **Client sync service:** Watches local file changes, chunks files (4 MB default), computes SHA-256 hash per chunk, uploads changed chunks.
- **Metadata service:** Stores file tree, permissions, version history in a sharded relational DB (Spanner/CockroachDB).
- **Chunk store:** Object store (S3/GCS) for raw chunk data. Keyed by content hash (content-addressed) → deduplication.
- **Delta sync:** Only upload changed chunks (not entire file) using chunk hash comparison.
- **Notification service:** When a file changes, notify authorized users via WebSocket/push.

**Phase 3 — Deep dive (Conflict Resolution):**
- Use **OT (Operational Transformation) or CRDTs** for concurrent document edits. Google Docs uses OT; modern approaches use CRDTs (Automerge/Yjs).
- For binary files: last-writer-wins with version history (keep both conflicting versions, mark second as "conflict copy").
- Use **vector clocks** (Module 12) to detect concurrent edits. The metadata server tracks per-file version vectors.
- Offline support: sync queue on the client. When online, replay queued changes in order.

**Phase 4 — Trade-offs:** Content-addressed dedup saves storage but requires a hash store. Conflict resolution for binary files can create duplicates. Offline sync can cause merge conflicts — accept UX complexity.

**Module references:** Traffic Routing (Module 1 — global load balancing), Storage (Module 10 — object store for chunks), Database Scaling (Module 2 — sharding metadata), Consensus (Module 12 — CRDTs for conflict resolution), Caching (Module 3 — cache file listings), Security/Auth (Module 8 — OAuth for sharing), Stream Processing (Module 11 — notification pipeline).

**Reference:** Docs/14-interview-framework-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Meta-Cognition — Self-Evaluation
**Type:** Open-Ended

After a system design interview, you realize you forgot to discuss caching. How could this have been avoided? What would you do differently next time? How does this relate to the 14-module synthesis approach?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Why it happened:** The candidate focused too heavily on the core data flow (especially writes) and skipped the read path optimizations. In a 14-module approach, caching (Module 3) is a fundamental layer that should always be on your mental checklist.

**What to do differently:**
1. **Use a mental template:** Before any design, run through a quick checklist: traffic routing, database, caching, async messaging, storage, security, observability. This ensures no major component is missed.
2. **Read-path walk:** Always dedicate 1-2 minutes to explicitly tracing the read path and asking "how can this be faster?" — cache is the first answer.
3. **Multi-layer caching:** Mention CDN (static assets), application cache (Redis for hot data), database query cache, and in-memory cache. Specify TTL, eviction policy, and cache invalidation strategy.

**14-module synthesis:** The 14-module curriculum is designed as a comprehensive mental framework for system design. Before presenting a design, mentally map it across:
- Layer 1 (Entry): Traffic Routing, Security
- Layer 2 (Data): Database, Storage, Caching, Async Messaging
- Layer 3 (Infrastructure): Service Mesh, Observability, Consensus
- Layer 4 (Process): Microservices Patterns, Stream Processing, Capacity Planning

If you forget one module (e.g., caching), rethink how that module's concepts apply to your design. Over time, this becomes automatic and ensures comprehensive coverage.

**Reference:** Docs/14-interview-framework-advanced.md
</details>
