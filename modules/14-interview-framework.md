# Module 14: System Design Interview Framework

The system design interview is not a test of how many components you can name — it is a test of how methodically you decompose complexity and defend your decisions through mathematical and structural trade-offs.

---

## Table of Contents

- [1. The 4-Phase Whiteboard Roadmap](#1-the-4-phase-whiteboard-roadmap)
- [2. The Seniority Signal](#2-the-seniority-signal)
- [3. The Defensive Whiteboarding Art](#3-the-defensive-whiteboarding-art)
- [4. Execution Flow](#4-execution-flow)
- [5. The Bar Raiser Checklist](#5-the-bar-raiser-checklist)

---

## 1. The 4-Phase Whiteboard Roadmap

A standard 45-minute interview is an open-ended conversation that **you** are expected to lead.

### 🕒 Phase 1: Scope & Requirements (5–10 min)

Do not start drawing until you have extracted the **functional** and **non-functional** constraints.

| Action | Signal to Sender |
|---|---|
| Ask who the users are and what the primary inputs/outputs are | You establish scope instead of guessing |
| Clarify DAU, read/write ratio, data size per entity | You are thinking about capacity from minute one |
| Compute back-of-the-envelope: QPS, storage (5-year), bandwidth | You prove the system must be distributed |
| Confirm consistency vs. availability trade-off up front | You anchor the conversation on CAP before drawing a box |

### 📐 Phase 2: High-Level Design (10–15 min)

Sketch the request path from **Client** to **Data Store**. Keep it box-and-arrow — no deep dives yet.

```
[Client] → [DNS / CDN] → [L7 Reverse Proxy] → [App Servers (stateless)] → [Primary DB]
                                                       ↕
                                                 [Cache Layer (Redis / Memcached)]
```

- Map the **Edge Infrastructure** (DNS, CDN, reverse proxy).
- Show the **Application Tier** as stateless (horizontal scaling).
- Place the **Storage Layer** without yet choosing SQL vs. NoSQL.
- Label arrows with protocols (HTTP/gRPC) and data formats (JSON/Protobuf).

### 🧩 Phase 3: Deep-Dive Component Engineering (15–20 min)

Steer the conversation into specific modules based on the system's bottlenecks.

- **Data schemas** — define the core entities and their relationships.
- **Database justification** — SQL (ACID, joins) vs. NoSQL (BASE, high-speed ingestion).
- **Cache strategy** — cache-aside, write-through, or write-behind. Address invalidation and thundering herd.
- **Sharding logic** — pick a shard key; explain how consistent hashing prevents reshuffle storms.
- **Async boundaries** — insert message queues for heavy operations (fan-out, report generation, image processing).

### ⚖️ Phase 4: Bottleneck & Scaling (5 min)

Defensively stress-test your own design.

- How do you scale horizontally? Where is the first bottleneck?
- How does Master-Slave replication lag affect reads?
- What happens when a cache node fails? A DB primary?
- What is the single point of failure in your current diagram?

---

## 2. The Seniority Signal

A Bar Raiser distinguishes **Junior** from **Staff+** engineers by watching for these specific behaviors:

| Aspect | Junior Behavior | Staff+ Behavior |
|---|---|---|
| **Requirement elicitation** | Waits for the interviewer to state each requirement | Asks pointed questions about DAU, latency SLOs, and write/read ratios before drawing |
| **Diagramming** | Draws one box and immediately dives into implementation details | Draws the full end-to-end path (client → edge → app → cache → DB → workers) before refining |
| **Handling ambiguity** | Freezes or asks "what do you want me to do?" | States assumptions out loud (e.g., "I'll assume 5 nines for reads, 3 nines for writes") and proceeds |
| **Trade-off discussion** | Calls components "perfect" or "simple" | States explicitly that "everything is a trade-off" — e.g., "Increasing availability in this Dynamo-style system means accepting eventual consistency" |
| **Proactivity** | Needs prompting for every next step | Drives the roadmap independently: "I've finished the high-level layout; let me now deep-dive into the cache layer" |
| **Operational empathy** | Ignores failure modes until asked | Discusses observability, security (mTLS/JWT), and SLOs as primary concerns, not afterthoughts |

---

## 3. The Defensive Whiteboarding Art

When an interviewer drops a mid-session constraint, you must think aloud using distributed systems fundamentals.

### Example: "The network between our app and cache has 5% packet loss."

**Step 1 — Apply CAP:** 5% packet loss is a **Network Partition** (P). I must decide: do we sacrifice **Availability** (refuse requests until the network stabilizes) or **Consistency** (serve potentially stale cache data)?

**Step 2 — Decorate for fault tolerance:**
- **Retries with exponential backoff** — prevent thundering herds from crushing the backend on retry.
- **Back pressure** — return HTTP 503 if the connection pool to the cache saturates.
- **Circuit breaker** — trip the cache circuit after N consecutive failures; serve stale data from a local replica or fall back to the database.

**Step 3 — Durability under partition:**
- If this is a write-heavy system (like Dynamo), use **Sloppy Quorums** and **Hinted Handoff** — writes are accepted by a healthy node outside the primary partition until the network heals.

---

## 4. Execution Flow

```mermaid
graph TD
    START(["🕒 Phase 1:<br/>Scope & Requirements"]) --> HLD["📐 Phase 2:<br/>High-Level Design"]
    HLD --> DEEP["🧩 Phase 3:<br/>Deep-Dive Components"]
    DEEP --> SCALE["⚖️ Phase 4:<br/>Bottleneck & Scaling"]

    SCALE -->|"Interviewer satisfied"| WRAP["Wrap-up"]
    SCALE -->|"Interviewer adds<br/>new constraint"| DEEP

    HLD -->|"Interviewer asks<br/>'why that DB?'"| DEEP
    START -->|"Missing storage calc"| HLD

    WRAP --> CHECKLIST["Run 10-point<br/>self-assessment"]

    style START fill:#e8f4ff,stroke:#2563eb
    style HLD fill:#fef3c7,stroke:#d97706
    style DEEP fill:#ecfdf5,stroke:#059669
    style SCALE fill:#fee2e2,stroke:#dc2626
    style WRAP fill:#f3e8ff,stroke:#9333ea
```

*The system design interview execution flow. The candidate moves through four phases sequentially, but feedback loops (decision diamonds) may send them back to earlier phases. The 10-point checklist runs at wrap-up.*

---

## 5. The Bar Raiser Checklist

Use this 10-point checklist to self-assess any design before concluding. Each item should be answerable with a clear **yes** or **no**.

> - [ ] **1. Requirements bounded** — Calculated storage (5-year), QPS, and bandwidth before choosing a database.
> - [ ] **2. CAP alignment** — Explicitly stated whether the system is **CP** (sacrifice availability) or **AP** (sacrifice consistency) under a network partition.
> - [ ] **3. Edge integrity** — DNS, CDN, L4/L7 load balancers correctly positioned with TLS termination at the edge.
> - [ ] **4. Stateless scaling** — Application tier is stateless, enabling independent horizontal scaling via a load balancer.
> - [ ] **5. Database justification** — Justified SQL (ACID, normalized) vs. NoSQL (BASE, denormalized) based on data structure and access patterns.
> - [ ] **6. Sharding logic** — Chose a shard key and described consistent hashing or range-based partitioning to prevent hot-spots.
> - [ ] **7. Cache strategy** — Addressed cache invalidation (TTL, write-through vs. cache-aside) and the thundering herd problem.
> - [ ] **8. Async decoupling** — Expensive or fan-out workloads moved to a message queue (Kafka / SQS / RabbitMQ).
> - [ ] **9. Security & auth** — Included JWT/OAuth2 for the public edge and mTLS for internal service-to-service communication.
> - [ ] **10. Graceful degradation** — Defined a fallback or "gutter" pool behavior when a core component (cache, DB, queue) becomes unavailable.
