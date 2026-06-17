# Module 4 — Distributed Systems & Communication — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** Synchronous vs Asynchronous Communication
**Type:** Multiple Choice

Which statement about synchronous communication between microservices is correct?

A) The caller never waits for a response
B) The caller blocks until it receives a response or timeout
C) It always uses message queues
D) It cannot use HTTP

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Synchronous communication (e.g., HTTP/REST, gRPC) blocks the caller until a response is received. Asynchronous communication uses message queues or event streams where the caller sends a message and continues processing without waiting.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 2 🟢
**Topic:** gRPC vs REST
**Type:** Multiple Choice

Which protocol does gRPC use under the hood for data serialization?

A) JSON
B) XML
C) Protocol Buffers (protobuf)
D) YAML

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** gRPC uses Protocol Buffers for serialization — a binary format that is smaller and faster than JSON. The contract is defined in `.proto` files, from which client and server code is generated.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 3 🟢
**Topic:** Idempotency
**Type:** Open-Ended

What does idempotency mean in the context of distributed APIs? Give an example of an idempotent and a non-idempotent operation.

<details>
<summary>Answer & Explanation</summary>

**Answer:** An operation is idempotent if executing it multiple times produces the same result as executing it once. Example: `PUT /user/123/status` with value "active" is idempotent (status stays "active"). `POST /order` (create) is non-idempotent — repeated calls create multiple orders. Idempotency is critical for safe retries in distributed systems.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 4 🟢
**Topic:** Circuit Breaker
**Type:** Multiple Choice

What are the three states of a circuit breaker pattern?

A) Open, Closed, Half-Open
B) Running, Stopped, Paused
C) Connected, Disconnected, Reconnecting
D) On, Off, Standby

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** Closed = normal operation, requests pass through. Open = failure threshold exceeded, requests fail fast without calling downstream. Half-Open = after a timeout, a few probe requests are allowed to test if the downstream has recovered. Success → Closed; Failure → Open.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 5 🟢
**Topic:** Retry with Exponential Backoff
**Type:** Open-Ended

Why add jitter to exponential backoff? What problem does it solve?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Without jitter, multiple clients with the same retry interval retry simultaneously, causing a thundering herd. Jitter adds randomness (e.g., random(0, base * 2^n)) so retries spread out. This prevents synchronized retry storms from overwhelming the downstream service.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 6 🟢
**Topic:** Timeout
**Type:** Multiple Choice

What is the recommended timeout strategy for a distributed system to avoid cascading failures?

A) No timeout — wait indefinitely for a response
B) Very short timeout (100ms) on all calls
C) Client-side timeout with circuit breaker, shorter than the downstream's timeout
D) Server-side timeout only

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Always set client-side timeouts shorter than downstream timeouts (e.g., client 2s, server 5s). This prevents one slow service from consuming all resources and cascading failures. Combine with circuit breaker for automatic degradation.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 7 🟢
**Topic:** Network Partitions
**Type:** Open-Ended

What is a network partition? How does the CAP theorem relate to it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A network partition is a split in the network where nodes in different partitions cannot communicate. Since partitions are inevitable in distributed systems, CAP theorem becomes a choice between Consistency and Availability during a partition (P is always required). You must handle partition detection, quorum adjustments, and split-brain scenarios.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 8 🟢
**Topic:** Load Shedding
**Type:** Multiple Choice

What is the purpose of load shedding in a distributed system?

A) Adding more servers to handle traffic
B) Dropping low-priority or excess requests to protect system stability
C) Distributing load evenly across servers
D) Caching frequently accessed data

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Load shedding intentionally drops requests (typically with a 503 response) when the system is overloaded, rather than degrading all responses. It's implemented with a priority queue: drop the lowest-priority work first to keep the system stable for critical requests.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 9 🟡
**Topic:** gRPC Streaming vs Unary
**Type:** Open-Ended

Compare gRPC unary RPC vs server-side streaming vs bidirectional streaming. When would you choose each?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
- **Unary:** Client sends one request, server responds with one response. Best for request-response patterns (e.g., GET user profile).
- **Server-side streaming:** Client sends one request, server streams multiple responses. Best for large data sets (e.g., downloading a log file, real-time feed).
- **Bidirectional streaming:** Both sides send independent streams concurrently. Best for real-time interactions (e.g., chat, collaboration, real-time dashboards).

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 10 🟡
**Topic:** Graceful Degradation
**Type:** Open-Ended

What is graceful degradation in a distributed system? Give three concrete strategies for degrading a movie recommendation service when the recommendation engine is down.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Graceful degradation means the system continues to provide reduced but functional service when some components fail.

**Strategies for recommendations:**
1. Serve cached/popular recommendations from a CDN or Redis.
2. Fall back to a simpler algorithm (e.g., trending movies instead of personalized).
3. Show a curated editorial list (human-curated or genre-based).
4. Return an empty section instead of failing the entire page load.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 11 🟡
**Topic:** Deadlines vs Timeouts
**Type:** Multiple Choice

In distributed systems, what is the difference between a deadline and a timeout?

A) They are the same thing
B) A deadline is the absolute time by which an operation must complete; a timeout is a duration limit
C) A timeout applies to the client; a deadline applies to the server
D) Deadlines are only used in gRPC

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** A deadline is an absolute point in time (e.g., "must finish by 12:00:00.000 UTC"). A timeout is a relative duration (e.g., "max 5 seconds"). gRPC uses deadlines. Timeouts are context-dependent and should be propagated across service calls to avoid work being done after the caller has given up.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 12 🟡
**Topic:** Bulkhead Pattern
**Type:** Open-Ended

Describe the bulkhead pattern. How does it prevent cascading failures in a service that calls three downstream APIs?

<details>
<summary>Answer & Explanation</summary>

**Answer:** The bulkhead pattern isolates resources (thread pools, connections) for different downstream services. If one downstream becomes slow, it can only exhaust its dedicated thread pool, leaving thread pools for other downstreams unaffected.

**Example:** An API gateway calling payments, inventory, and shipping services. Allocate 5 threads each, with a shared reserve of 5. If payments latency spikes, at most 5+2 threads are blocked; inventory and shipping still have their full allocation.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 13 🟡
**Topic:** Service Discovery Basics
**Type:** Multiple Choice

What is the primary purpose of service discovery in a distributed system?

A) Encrypting service-to-service communication
B) Allowing services to find each other's network locations dynamically
C) Monitoring service health
D) Load balancing traffic between services

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Service discovery solves the problem of finding network addresses (IP:port) of service instances that can change dynamically due to auto-scaling, failures, or deployments. It maintains a registry of healthy instances and provides lookup mechanisms.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 14 🟡
**Topic:** Distributed Tracing Basics
**Type:** Open-Ended

What is distributed tracing and how does a trace ID help debug a slow request that spans 5 microservices?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Distributed tracing tracks a single request as it propagates through multiple services. A trace ID is generated at the entry point and propagated via HTTP headers (e.g., `X-Request-Id`, `traceparent`). Each service records "spans" with start/end timestamps, linked by the trace ID and parent span ID. When debugging a slow request, you can see which service consumed the most time, whether network latency is a factor, and whether there are concurrent calls causing contention.

**Reference:** Docs/04-distributed-comm.md
</details>

---

## Question 15 🔴
**Topic:** Tail Latency at Scale
**Type:** Whiteboard

A service experiences high P99.9 latency (2s) while P50 is 50ms. The latency is caused by a few slow query responses from a sharded database. Design a strategy to reduce P99.9 without adding hardware. Consider hedged requests, request coalescing, and speculative execution.

<details>
<summary>Answer & Explanation</summary>

**Answer:**

1. **Hedged requests:** Send the same query to 2 replicas in parallel. Wait for the first response, cancel the other. For a sharded DB, the slowest shard determines tail latency. Hedging against 2 replicas dramatically improves tail: from P99 alone to P99^2 (e.g., 100ms tail becomes 10ms if uncorrelated).
2. **Speculative execution (tied requests):** If a query takes > P95, automatically send a duplicate to another replica. Use a small delay (e.g., 5ms) before issuing the speculative request to avoid doubling load on most requests.
3. **Request coalescing:** Collapse concurrent requests for the same key into a single DB query, broadcasting the result to all waiters.
4. **Back-pressure and load shedding:** Reject requests early when latency crosses a threshold.

**Reference:** Docs/04-distributed-comm.md, Docs/04-distributed-comm-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Distributed Transaction Across Microservices
**Type:** Whiteboard

Design a reliable money transfer between two accounts that live in different microservices (Account A in Service X, Account B in Service Y). You cannot use a distributed transaction coordinator. Ensure exactly-once semantics, detect failures, and handle idempotency.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Saga pattern (choreography):**
1. Service X begins: create a "Transfer" event in an outbox table. Emit `TransferStarted(transferId, from=X, to=Y, amount)`.
2. Service X debits Account A. Emit `Debited(transferId)`.
3. Service Y receives event, credits Account B. Emit `Credited(transferId)`.
4. If step 2 or 3 fails, emit `TransferFailed(transferId, reason)`. Service X runs a compensating transaction (re-credit).

**Idempotency:** Each event has a unique transferId. Services track processed IDs in a dedup table.

**Exactly-once:** Outbox pattern + CDC ensures at-least-once delivery. Dedup table provides at-most-once processing. Combine → exactly-once.

**Failure scenario:** Service Y crashes after crediting but before emitting the event. The orchestrator (or a compensating job) scans for stuck transfers and replays the completion event.

**Reference:** Docs/04-distributed-comm-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Network Latency Calculation
**Type:** Calculation

Two data centers are 3000 km apart. Light in fiber travels at ~200,000 km/s. A 1 KB request + 10 KB response cross this link. Calculate:
1. The minimum theoretical RTT
2. The actual P99 RTT if the link has 5 hops each with 2ms processing latency and 0.1% packet loss (TCP retransmission overhead)
3. How much does gRPC streaming save vs REST for 100 sequential requests?

<details>
<summary>Answer & Explanation</summary>

**Answer:**

1. **Minimum RTT:** 2 × (3000 km / 200,000 km/s) = 2 × 0.015s = 30ms.

2. **Actual RTT:** Propagation = 30ms. Serialization: 1 KB at 10 Gbps = 0.0008ms (negligible). 5 hops × 2ms = 10ms. Total ~40ms. With 0.1% packet loss, TCP must retransmit ~0.1% of packets, adding ~RTO (often 200ms+) for each retransmission, effectively adding ~0.2ms average. P99 may hit 60-80ms due to queuing and reordering.

3. **REST vs gRPC streaming:** REST requires 100 separate HTTP request/response pairs → 100 × 40ms = 4000ms + 100 TCP handshakes (if no keep-alive). gRPC streaming uses one TCP connection with multiplexed streams → ~1 RTT for setup + 100 stream messages in one connection ≈ 45ms total. Savings: ~4000x for connection setup, ~100x for round trips.

**Reference:** Docs/04-distributed-comm-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Byzantine Fault Tolerance
**Type:** Open-Ended

What is the Byzantine Generals Problem? How does PBFT (Practical Byzantine Fault Tolerance) solve it? How many nodes are needed to tolerate f byzantine faults, and why?

<details>
<summary>Answer & Explanation</summary>

**Answer:** The Byzantine Generals Problem describes a scenario where distributed nodes must agree on a plan despite some nodes being malicious (lying, sending conflicting messages).

**PBFT** solves it with a 3-phase protocol (pre-prepare, prepare, commit) and requires 3f + 1 nodes to tolerate f byzantine failures. The system can proceed correctly as long as 2f + 1 nodes are honest. The +1 accounts for the fact that honest nodes may receive conflicting information and need a supermajority (2/3) to achieve consensus despite f malicious nodes.

**Why 3f+1:** With N nodes and f faulty ones, an honest node needs to hear from N - f nodes to guarantee correctness. In the worst case, f of those responses could be from faulty nodes. The majority of N - f messages (i.e., (N - f + 1)/2) must be honest → (N - f + 1)/2 > f → N > 3f.

**Reference:** Docs/04-distributed-comm-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Request Funnel / Coalescing
**Type:** Whiteboard

Design a "request coalescing" cache layer that deduplicates concurrent requests for the same resource. If 100 concurrent requests ask for the same user profile, only one DB call should be made. Handle transient failures, timeouts, and partial results.

<details>
<summary>Answer & Explanation</summary>

**Answer:**

**Design:**
1. **CoalescingMap:** An in-memory map keyed by resource identifier (e.g., "user:123"). Value is a shared future/promise.
2. On request: check L1 cache → miss → check coalescing map for an in-flight request.
   - If in-flight: await the existing future.
   - If not: insert a new future in the map, make the DB call, resolve the future, remove from map.
3. **Timeout:** If the DB call exceeds a threshold, fail the future with a timeout error. All waiters receive the error.
4. **Failure handling:** If the DB call fails, all coalesced requests fail together (fast-fail). Optionally, on failure, allow one retry via a new future.
5. **Back-pressure:** Limit the number of outstanding coalesced requests globally (e.g., max 1000).

**Edge cases:** Handle future cleanup after timeout; handle cancellation (if one caller cancels, the DB call still proceeds for others).

**Reference:** Docs/04-distributed-comm-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Resilience Testing
**Type:** Debug

A team's microservice A calls service B with a 5-second timeout and no circuit breaker. During a partial B outage, A's threads all block on B. A stops responding, causing its upstream services to also timeout, cascading to a full system outage. What architectural and code-level changes prevent this from happening again?

<details>
<summary>Answer & Explanation</summary>

**Answer:**

**Architectural:**
1. Add circuit breaker (e.g., Resilience4j) with failure threshold (e.g., 50% in 10s window) → open state → fail fast.
2. Add bulkhead: dedicated thread pool for B calls (e.g., max 10 threads).
3. Set shorter timeouts: A's timeout for B = 500ms (B's internal timeout = 2s).
4. Graceful degradation: when B is down, serve cached data or an empty response.

**Code-level:**
1. Use async non-blocking IO (e.g., reactive stack) to avoid blocking threads.
2. Add timeouts: `HttpClient.withTimeout(Duration.ofMillis(500))`.
3. Add retry with exponential backoff and jitter for transient failures.
4. Health check / startup probe: don't send traffic to A unless B is healthy.

**Testing:**
1. Chaos engineering: regularly inject B failures in staging.
2. Load test with partial failures to validate resilience.

**Reference:** Docs/04-distributed-comm-advanced.md
</details>
