# System Design Interview Framework – A Beginner's Guide

> This guide explains how to approach system design interviews — the 4-phase structure, what senior engineers look for, and how to practice.
> Every term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand this framework, the original advanced module (with mock interview walkthroughs and a full question bank) will feel like a natural next step.

---

## Table of Contents

1. [What the Interview Is Really Testing](#1-what-the-interview-is-really-testing)
2. [The 4-Phase Structure (Overview)](#2-the-4-phase-structure-overview)
3. [Phase 1: Scope and Requirements (5-10 min)](#3-phase-1-scope-and-requirements-5-10-min)
4. [Phase 2: High-Level Design (10-15 min)](#4-phase-2-high-level-design-10-15-min)
5. [Phase 3: Deep-Dive (15-20 min)](#5-phase-3-deep-dive-15-20-min)
6. [Phase 4: Bottlenecks and Scaling (5 min)](#6-phase-4-bottlenecks-and-scaling-5-min)
7. [Seniority Signals: What Different Levels Sound Like](#7-seniority-signals-what-different-levels-sound-like)
8. [Common Anti-Patterns (What Not to Do)](#8-common-anti-patterns-what-not-to-do)
9. [How to Practice](#9-how-to-practice)
10. [Glossary of Key Terms](#10-glossary-of-key-terms)
11. [Key Takeaways](#11-key-takeaways)

---

## 1. What the Interview Is Really Testing

The system design interview is **not** a test of how many components you can name. It is a test of how methodically you:

- **Decompose complexity** — turn an ambiguous problem into a structured design.
- **Make trade-offs** — defend why you chose SQL over NoSQL, cache-aside over write-through, etc.
- **Think about failure** — what breaks first, and how does your design survive it?
- **Communicate clearly** — lead the conversation, ask clarifying questions, explain your reasoning.

**Analogy:** It is like a martial arts grading. You are not being judged on whether you can name every technique. You are judged on how you handle pressure, react to unexpected constraints, and whether your fundamentals are solid enough to build a coherent system from scratch in 45 minutes.

---

## 2. The 4-Phase Structure (Overview)

A standard 45-minute interview follows this structure:

| Phase | Duration | Goal | Output |
|-------|----------|------|--------|
| **1. Scope & Requirements** | 5-10 min | Define the problem, constraints, and capacity numbers | A clear problem statement + initial calculation |
| **2. High-Level Design** | 10-15 min | Draw the big picture — components and how they connect | A box-and-arrow diagram |
| **3. Deep-Dive** | 15-20 min | Go deep into the most interesting/important component | Detailed design of data model, API, and trade-offs |
| **4. Bottlenecks & Scaling** | 5 min | Stress-test your design — what fails first? | Mitigation plan for the weakest link |

---

## 3. Phase 1: Scope and Requirements (5-10 min)

**Do not start drawing** until you have clarified the problem. This is the most common mistake juniors make.

### What to ask

| Question | Why it matters |
|----------|---------------|
| "What are the core features?" | Do we need to design the full product or just the core API? |
| "How many users? (DAU)" | Determines whether we need distribution at all |
| "Read/write ratio?" | Determines caching strategy, DB choice |
| "Data size per entity?" | Determines storage needs, sharding |
| "Consistency or availability priority?" | Sets the CAP trade-off |

### What to calculate (out loud)

Once you have the numbers, do **back-of-the-envelope math**:

- **QPS:** `DAU × actions/user / 86,400`
- **Storage:** `daily data × 365 × years × replication × padding`
- **Peak multiplier:** 2-5× the average

**Example:** "100M DAU, each user reads 10 tweets and writes 1 tweet per day."
`Read QPS: 100M × 10 / 86,400 ≈ 11,574`
`Write QPS: 100M × 1 / 86,400 ≈ 1,157`
`5-year storage at 140 bytes per tweet: ~15 TB`

**Why this matters:** The numbers prove that you need a distributed system. A single server cannot handle 11,574 QPS and 15 TB of storage. This anchors the rest of the design.

---

## 4. Phase 2: High-Level Design (10-15 min)

Draw the "box and arrow" diagram. Keep it high-level.

### Typical components

```
[Client] → [CDN] → [Reverse Proxy / API Gateway] → [App Servers (stateless)] → [Database]
                                                         ↓
                                                    [Cache (Redis/Memcached)]
                                                         ↓
                                                    [Queue + Workers (async)]
```

### Rules of thumb

| Component | When to include |
|-----------|----------------|
| **CDN** | Serving static assets or media to a global audience |
| **Load balancer / Reverse proxy** | Multiple app servers, need TLS termination or routing |
| **Cache** | Read-heavy workload (10:1+ read/write ratio) |
| **Queue** | Async operations (email, image processing, notifications) |
| **Database** | Always needed. Pick SQL or NoSQL based on requirements |

**Label your arrows** with protocols (HTTP, gRPC, WebSocket) and data formats (JSON, Protobuf).

---

## 5. Phase 3: Deep-Dive (15-20 min)

The interviewer will guide you to a specific component. This is where you go deep.

### What to cover in a deep-dive

| Topic | What to discuss |
|-------|-----------------|
| **Data model** | Entities, relationships, key schema design |
| **API design** | Key endpoints, request/response format |
| **Database choice** | Why SQL vs NoSQL, indexing strategy |
| **Cache strategy** | Cache-aside? Write-through? Write-behind? TTL? |
| **Sharding** | Shard key choice, consistent hashing, rebalancing |
| **Async boundaries** | Where to put a queue and why |
| **Consistency model** | Strong vs eventual, trade-offs |

### Example deep-dive: Database for a messaging app

- **Schema:** `messages (id, sender_id, receiver_id, content, timestamp, status)`
- **Indexes:** `(sender_id, timestamp)` for inbox queries, `(receiver_id, timestamp)` for outbox
- **Choice:** NoSQL (Cassandra) for write scalability, or SQL with sharding
- **Shard key:** `hash(sender_id)` for even distribution
- **Cache:** Recent conversations in Redis (write-through, TTL 5 minutes)

---

## 6. Phase 4: Bottlenecks and Scaling (5 min)

Defensively stress-test your own design. The interviewer will often prompt you, but you should **proactively** point out the weak spots.

### Questions to ask yourself

| Bottleneck | How to mitigate |
|------------|-----------------|
| "What if traffic doubles?" | Horizontal scaling for app servers, read replicas for DB |
| "What if a database node fails?" | Replication, failover, read replicas |
| "What if the cache fails?" | Circuit breaker falls through to DB, but DB gets hammered |
| "What if a popular key becomes a hotspot?" | Replicate hot key, CDN, local cache |
| "What if replication lag causes stale reads?" | Read-your-writes from primary, version tokens |
| "What is the single point of failure?" | Eliminate it or make it highly available |

### The golden phrase

> *"The first bottleneck in my design would be X. To mitigate it, I would Y. If that is not enough, I would Z."*

This shows you are thinking ahead and have a plan.

---

## 7. Seniority Signals: What Different Levels Sound Like

| Level | Behavior | Example quote |
|-------|----------|---------------|
| **Junior** | Jumps to drawing without clarifying requirements. Names components without trade-offs. | "I'll use Redis for caching and MongoDB for the database." |
| **Mid** | Asks clarifying questions, does capacity math, explains trade-offs. | "For 100M DAU with 10:1 read/write, I would use a cache-aside pattern with Redis and a sharded PostgreSQL database." |
| **Senior** | Leads the conversation, structures ambiguity, points out failure modes unprompted. | "Let me first scope the problem. I will assume 100M DAU and calculate from there. If that assumption is wrong, the rest adjusts proportionally." |
| **Staff** | Connects technical decisions to business outcomes, navigates organizational constraints, delegates sub-problems. | "The read path is straightforward with a CDN, but the write path has a fundamental tension between durability and latency that I want to address up front." |

**The key difference:** Senior engineers do not wait for the interviewer to give them numbers — they **assume and state their assumptions out loud**, then adjust if the interviewer corrects them.

---

## 8. Common Anti-Patterns (What Not to Do)

| Anti-Pattern | Why it fails |
|-------------|-------------|
| **Jumping to microservices** | Starting with 20 microservices for a 38 QPS system. You must prove the need for distribution with numbers first. |
| **No capacity math** | Drawing boxes without ever calculating QPS or storage. The interviewer cannot tell if you understand scale. |
| **One correct answer mindset** | There is no single correct design. The evaluation is about trade-offs, not "the right answer." |
| **Ignoring failure** | Designing a perfect system that works when nothing breaks. The interviewer wants to know what happens when things break. |
| **Not stating assumptions** | Keeping numbers in your head. The interviewer cannot evaluate what they cannot see. |
| **Going too deep too early** | Spending 20 minutes on the database schema before showing the high-level architecture. |
| **Silent drawing** | Drawing without explaining. The interviewer needs to hear your reasoning. |
| **Over-engineering** | Adding Kafka, 12 microservices, and a service mesh for a URL shortener with 38 write QPS. |

---

## 9. How to Practice

### The Study Loop

1. Pick one problem from the question bank (URL Shortener, Chat System, News Feed, etc.).
2. Set a 45-minute timer.
3. Go through the 4 phases on paper or a whiteboard.
4. After the timer, review: Did you clarify requirements first? Did you calculate capacity? Did you discuss trade-offs? Did you identify failure modes?
5. Re-draw the architecture from memory the next day.
6. Explain the design out loud to yourself or a peer.

### What to Focus On

- **Capacity math:** Practice until you can calculate QPS, storage, and bandwidth for any problem in 2 minutes.
- **Trade-off language:** Every decision must have a "why." Not "I use Redis" but "I use Redis because the read/write ratio is 10:1, and cache-aside minimizes write overhead."
- **Failure modes:** For every component, ask "what breaks first?"
- **Mock interviews:** Practice with a peer. The conversational format is different from studying alone.

### 10 Classic Problems

| Problem | Key topics to practice |
|---------|-----------------------|
| URL Shortener | Key generation, redirects (301 vs 302), storage estimation |
| Chat System | WebSockets, message ordering, presence, offline delivery |
| News Feed | Fan-out on write vs read, caching, ranking |
| Video Streaming | CDN, adaptive bitrate, chunking, geo-distribution |
| Ride-Sharing | Real-time matching, geospatial indexing, surge pricing |
| Distributed KV Store | Consistent hashing, replication, quorum |
| Rate Limiter | Token bucket, sliding window, distributed counters |
| Search Autocomplete | Trie, prefix matching, frequency-based ranking |
| Collaborative Editor | CRDTs, OT, WebSocket, conflict resolution |
| Web Crawler | BFS, deduplication (Bloom filter), politeness, queue |

---

## 10. Glossary of Key Terms

| Term | Definition |
|------|------------|
| **API Gateway** | A reverse proxy that manages API routing, authentication, and rate limiting. |
| **Back-of-the-Envelope** | A rough calculation using approximate numbers to estimate scale. |
| **CAP Theorem** | A system can only provide two of Consistency, Availability, and Partition Tolerance during a network fault. |
| **CDN (Content Delivery Network)** | A geographically distributed network of servers that cache content close to users. |
| **Circuit Breaker** | A pattern that stops requests to a failing service to prevent cascading failures. |
| **DAU (Daily Active Users)** | The number of unique users per day. |
| **Failover** | Automatically switching to a backup system when the primary fails. |
| **HLD (High-Level Design)** | The overall architecture diagram showing components and connections. |
| **Horizontal Scaling** | Adding more machines to handle increased load. |
| **Idempotency** | The property that an operation can be applied multiple times without changing the result. |
| **Load Balancer** | Distributes incoming requests across multiple servers. |
| **QPS (Queries Per Second)** | The number of requests per second the system handles. |
| **Replication** | Copying data to multiple servers for durability or read scaling. |
| **Reverse Proxy** | A server that accepts client requests and forwards them to backend servers. |
| **Shard** | A horizontal partition of a database — each shard holds a subset of data. |
| **SPOF (Single Point of Failure)** | A component whose failure brings down the entire system. |
| **Vertical Scaling** | Upgrading a single machine with more CPU, RAM, or storage. |

---

## 11. Key Takeaways

1. **The interview tests how you think, not what you know.** Trade-offs and reasoning matter more than the final diagram.
2. **The 4-phase structure gives you a roadmap.** Scope → HLD → Deep-Dive → Bottlenecks. Follow it.
3. **Phase 1 (Scope) is the most important.** Clarify requirements and calculate capacity before drawing.
4. **Phase 2 (HLD) should be broad, not deep.** Box-and-arrow with labels. Save details for Phase 3.
5. **Phase 3 (Deep-Dive) is where you show depth.** Pick one component and go into detail: schema, API, trade-offs.
6. **Phase 4 (Bottlenecks) is your chance to show experience.** Proactively identify what breaks and how you fix it.
7. **State your assumptions out loud.** The interviewer cannot evaluate what they cannot hear.
8. **Always talk about trade-offs.** "I chose X because of Y, at the cost of Z."
9. **Failure modes are first-class components.** Every box in your diagram should have a "what if this fails?" answer.
10. **Practice capacity math until it is automatic.** It is the most repeatable skill to improve.
11. **Start simple and add complexity only when the numbers justify it.** A monolith with a cache works for most systems.
12. **Summarize at the end.** "To recap: my design uses a CDN for static content, a sharded SQL database for storage, Redis for caching writes, and a message queue for async processing."

---

> This guide explains the structure and strategy behind system design interviews.
> Once you are comfortable with this framework, the original module (with its full mock interview walkthrough, seniority dialogue examples, and 10-problem question bank) will give you everything you need to prepare confidently.
> Remember: the goal is not to design a perfect system. It is to demonstrate clear, methodical engineering judgment under time pressure.
