# System Design Interview Framework – A Beginner's Guide

**You've used this when...**

You are in a system design interview. The interviewer says: "Design Twitter." Your mind goes blank. You have 45 minutes to produce a design that shows you can think like an engineer. Where do you start? This framework gives you a structured roadmap — scope the problem, draw the high-level design, dive deep on one component, and proactively find the bottlenecks.

You are a senior engineer at a tech company. You are asked to review a proposal for a new service. The author has drawn a beautiful diagram with 12 microservices, but there are no numbers — no QPS, no storage estimates, no failure analysis. You realize they skipped the same steps that interviewees skip when they are nervous. The interview framework is not just for interviews — it is how experienced engineers approach any ambiguous design problem.

You are mentoring a junior engineer. They ask: "How do I get better at system design?" The answer is not "read more" — it is practice with a repeatable process. The 4-phase structure gives them a checklist they can follow every time, turning an overwhelming open-ended question into a manageable sequence of steps.

> This guide explains how to approach system design interviews — the 4-phase structure, what senior engineers look for, and how to practice.
> Every term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand this framework, the [advanced module](14-interview-framework-advanced.md) (with mock interview walkthroughs, the 10-point evaluation rubric, and a full question bank) will feel like a natural next step.
>
> **Before you start:** This module references concepts from all other modules (01-13). It is designed as a capstone — come back to it after you have completed the others.

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

> **⏱ TL;DR — If you only learn 3 things from this module:**
> 1. **The interview tests how you think, not what you know** — trade-offs, reasoning, and failure analysis matter more than the final diagram. State your assumptions out loud.
> 2. **Follow the 4-phase structure religiously** — Scope (5-10 min) → HLD (10-15 min) → Deep-Dive (15-20 min) → Bottlenecks (5 min). Do not skip Phase 1 (scope) or jump straight to drawing.
> 3. **Start simple and add complexity only when the numbers justify it** — a monolith with a cache works for most systems. Prove the need for distribution with QPS and storage math before adding microservices, queues, or sharding.

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

```text
┌─────────────────────────────────────────────────────────┐
│             System Design Interview Flow                 │
├──────────────┬──────────┬───────────────────────────────┤
│ Phase        │ Time     │ Focus                         │
├──────────────┼──────────┼───────────────────────────────┤
│ 1. Scope     │ 5–10 min │ Requirements, constraints,     │
│              │          │ capacity estimation            │
├──────────────┼──────────┼───────────────────────────────┤
│ 2. High-     │ 10–15    │ Box-and-arrows diagram:        │
│    Level     │ min      │ clients, LB, services, DB      │
├──────────────┼──────────┼───────────────────────────────┤
│ 3. Deep Dive │ 15–20    │ Pick hardest component:        │
│              │ min      │ data model, API, trade-offs    │
├──────────────┼──────────┼───────────────────────────────┤
│ 4. Bottle-   │ 5 min    │ Stress-test: what fails first? │
│    necks     │          │ Mitigation plan                │
└──────────────┴──────────┴───────────────────────────────┘
```

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

### Choosing Your Presentation Strategy

| Problem Type | Emphasize in HLD | Emphasize in Deep-Dive | Pitfall to avoid |
|-------------|------------------|----------------------|-------------------|
| **Data-intensive** (URL shortener, KV store, news feed) | Storage model, sharding strategy, caching layers | Schema design, read/write paths, replication | Over-engineering the API while ignoring the storage bottleneck |
| **Real-time** (chat, ride-sharing, collaborative editor) | WebSocket connections, presence service, message ordering | Protocol choice (WebSocket vs SSE vs polling), conflict resolution | Ignoring offline delivery and reconnection logic |
| **Media-heavy** (video streaming, photo sharing, CDN) | CDN strategy, geo-distribution, adaptive bitrate | Chunking, caching tiers, origin protection | Forgetting the bandwidth calculation and CDN egress costs |
| **Infrastructure** (rate limiter, distributed counter, crawler) | Stateless vs stateful design, consistency model | Data structure choice, shard key, leader election | Jumping to a complex consensus algorithm when a simple approach works |
| **classic CRUD** (e-commerce, ticket booking, payment) | Database choice (SQL vs NoSQL), transaction boundaries | Indexing strategy, isolation levels, inventory consistency | Starting with microservices before proving the need for distribution |

---

> **✏️ Check Your Understanding**
> 1. In a system design interview, you are asked to design a URL shortener. After 2 minutes of clarifying questions, you start drawing a box-and-arrow diagram with 5 microservices, a message queue, a Redis cluster, and a sharded database. The interviewer asks: "Why do you need all of this?" What did you do wrong?
> 2. Your interviewer asks: "What if the database goes down?" You respond: "We will use a read replica." They push: "What if the read replica is in a different region and has replication lag?" What concept are they testing, and how should you respond?
> 3. A candidate spends 25 minutes explaining the exact schema for the `users` table, including index types and query plans. The interviewer asks: "Can you show me the high-level architecture first?" Which phase did the candidate skip, and why does it matter?
> <details>
> <summary>Answers</summary>
> 1. **You skipped Phase 1 (Scope).** You assumed a complex distributed system was needed without calculating capacity. A URL shortener with 38 write QPS (as shown in the module) does not need 5 microservices. You should have calculated QPS and storage first to justify distribution.
> 2. **They are testing your understanding of failure modes and consistency trade-offs.** Respond: "Read replicas help with read scaling but introduce eventual consistency. If the application needs read-your-writes consistency, we would route reads for the same user to the primary. We would also implement a circuit breaker to fail gracefully if replication lag exceeds a threshold."
> 3. **They skipped Phase 2 (High-Level Design).** The interviewer cannot see how the schema fits into the overall system. Without the HLD, they do not know if the database connects to a cache, a queue, or directly to clients. Always show the architecture first, then dive deep on one component.
> </details>

---

## 8. Common Anti-Patterns (What Not to Do)

### Jumping to Microservices
**Symptom:** You propose 20 microservices for a URL shortener with 38 write QPS. The diagram is beautiful but impossible to justify.
**Root Cause:** You skipped Phase 1 (Scope) and never calculated QPS or storage. Without numbers, you have no basis to decide when distribution is needed.
**Real Incident:** Multiple real startups (including the early version of a well-known task management app) burned months building a microservice architecture for systems that could have run on a single database server. They spent more time on service orchestration than on product features.
**Fix:** Always start with a monolith. Add microservices only when you can point to a specific bottleneck (e.g., "the monolith's database cannot handle 50K write QPS") that justifies the complexity.
**How to Detect Early:** Before proposing a microservice, ask yourself: "Can I prove with numbers that a single server cannot handle this load?" If the answer is no, keep it simple.

### No Capacity Math
**Symptom:** You draw boxes (load balancer, app servers, database, cache) but never calculate QPS, storage, or bandwidth. The diagram is just boxes floating in space.
**Root Cause:** You are treating system design as a diagramming exercise. The interviewer cannot evaluate whether your design fits the scale without numbers.
**Real Incident:** Interviewers at FAANG companies consistently report that the #1 reason candidates fail system design interviews is not a lack of architectural knowledge — it is the absence of any quantitative reasoning.
**Fix:** Before drawing anything, calculate: DAU × actions/user / 86,400 = QPS. Storage = daily data × retention × replication × padding. These numbers ground your design in reality.
**How to Detect Early:** If you have drawn three boxes and have not written a single number, you have fallen into this trap. Pause, calculate, then draw.

### One Correct Answer Mindset
**Symptom:** You keep asking the interviewer: "Is this the right approach?" You freeze when they say "it depends."
**Root Cause:** You believe system design has one correct answer, like a coding problem. It does not. The interview evaluates trade-off reasoning, not correctness.
**Real Incident:** A candidate at a top tech company spent 10 minutes trying to get the interviewer to confirm that Cassandra was "the right choice" instead of discussing the trade-offs between Cassandra and PostgreSQL. The interviewer could not evaluate their depth because they would not commit to a position.
**Fix:** State your choice and its trade-offs explicitly: "I would choose PostgreSQL over Cassandra here because our write volume is moderate, we need strong consistency, and the relational model fits our data. The cost is that we will need to shard earlier than with Cassandra."
**How to Detect Early:** If your internal monologue is "I hope this is right" instead of "Here is why I chose this and what I am trading off," you have the wrong mindset.

### Ignoring Failure
**Symptom:** Your design works perfectly — until the interviewer asks "what if the cache goes down?" You have no answer.
**Root Cause:** You designed for the happy path only. Experienced engineers always have a plan for when components fail.
**Real Incident:** In a real production incident at GitHub, a Redis cache cluster failure caused the database to receive 40× normal load within seconds. The database fell over, taking the entire site down. The architecture had no circuit breaker or fallback plan for cache failure.
**Fix:** For every component in your diagram, ask: "What if this fails?" Have a mitigation plan for each (circuit breaker, fallback, failover, degradation).
**How to Detect Early:** Look at your diagram and point to each box. If you cannot describe what happens when that box goes down, you have ignored failure.

### Not Stating Assumptions
**Symptom:** You have numbers in your head but never say them out loud. The interviewer cannot follow your reasoning.
**Root Cause:** You assume the interviewer knows what you are thinking. In an interview, unspoken assumptions do not exist.
**Real Incident:** A candidate at Meta calculated 10K QPS in their head but never said it. The interviewer assumed they had not done the math. The feedback was "no capacity analysis performed." The candidate was shocked — they had done it, but silently.
**Fix:** Narrate everything: "Let me assume 100M DAU. That gives us roughly 11.5K QPS for reads. I am using the formula DAU × actions / 86,400. If that assumption is wrong, the rest scales proportionally."
**How to Detect Early:** Pause and check: have you said a number out loud in the last 2 minutes? If not, start narrating.

### Going Too Deep Too Early
**Symptom:** You spend 20 minutes on the database schema for the `users` table, describing indexes, query plans, and migration strategies — before showing the high-level architecture.
**Root Cause:** You jumped to your area of comfort (details) instead of following the structured 4-phase process.
**Real Incident:** A candidate at Google spent the first 25 minutes designing the perfect database schema for a chat app. The interviewer had to interrupt and ask: "Can you show me how the webSocket connections work?" The candidate had not considered WebSockets at all.
**Fix:** Follow the phases in order: Phase 2 (HLD) first, then Phase 3 (Deep-Dive). The HLD should take no more than 10-15 minutes and show the full picture. Only then dive deep.
**How to Detect Early:** If you find yourself describing column types or query patterns before you have drawn a box-and-arrow diagram, you are going too deep too early.

### Silent Drawing
**Symptom:** You draw a complex diagram for 5 minutes without saying a word. The interviewer watches in silence. When you finish, they have no idea what you were thinking.
**Root Cause:** You are focused on getting the diagram "right" instead of communicating your reasoning. In an interview, the diagram is a communication tool, not the output.
**Real Incident:** A candidate at Amazon drew an excellent architecture diagram but never explained their choices. The interviewer could not evaluate their thinking process. The feedback was: "Good diagram, but we could not assess their decision-making ability."
**Fix:** Narrate as you draw: "I am putting a load balancer here because we have multiple app servers. I will add Redis for caching because the read/write ratio is 10:1..." Every box should have a spoken explanation.
**How to Detect Early:** If you have drawn two boxes without speaking, stop and describe what you just drew and why.

### Over-engineering
**Symptom:** You add Kafka, 12 microservices, a service mesh, and multi-region replication — for a URL shortener with 38 write QPS.
**Root Cause:** You are trying to impress the interviewer with your knowledge of advanced tools instead of solving the problem at its actual scale.
**Real Incident:** A real startup built its entire infrastructure on Kubernetes, Kafka, and 15 microservices for a product that had 200 users. The CTO later admitted the complexity slowed development by 10× with zero benefit.
**Fix:** Start with the simplest possible design: a monolith, one database, a cache if needed. Add complexity only when you (or the interviewer) identify a specific bottleneck that requires it.
**How to Detect Early:** Count the number of distinct systems in your diagram. If it exceeds 5-6 for a simple CRUD problem, you are likely over-engineering. Ask yourself for each component: "Can I remove this and still meet the requirements?"

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

> **🧪 Conceptual Exercises**
> 1. **The Silent Interviewer:** You are in a system design interview for a senior role. The interviewer has said almost nothing for 30 minutes. You have drawn a diagram, explained your reasoning, and identified bottlenecks. The only feedback has been nods. What strategies can you use to draw out more signal from the interviewer and demonstrate senior-level communication?
> 2. **Mid-Interview Curveball:** 25 minutes into designing a real-time chat system, the interviewer says: "We just acquired a company that has 50 million existing users. They use a completely different data model. How do you handle the migration without downtime?" Walk through your response using the 4-phase framework.
> <details>
> <summary>Hints</summary>
> 1. A silent interviewer may be testing your ability to lead the conversation. Propose concrete trade-offs and ask for direction: "I see two approaches — using Cassandra for write scalability or PostgreSQL with sharding for consistency. Which would you like me to explore?" This gives the interviewer something to respond to. You can also summarize your progress: "Let me recap what I have covered so far and what I plan to dive into next — does that align with what you are looking for?"
> 2. This is a scope-change scenario. Do not panic. Re-enter Phase 1 (Scope): clarify the acquisition's implications. "Let me re-scope. We now have 50M additional users with their own data model. The key questions are: (a) do we need real-time interoperability between the two systems, and (b) is there a deadline for full migration?" Then update your HLD to include a dual-write or ETL bridge phase, then deep-dive on the migration strategy (backfill, validation, cut-over).
> </details>

---

## 10. Glossary of Key Terms

| Term | Section | Definition |
|------|---------|------------|
| **DAU (Daily Active Users)** | 3 | The number of unique users per day. |
| **Back-of-the-Envelope** | 3 | A rough calculation using approximate numbers to estimate scale. |
| **QPS (Queries Per Second)** | 3 | The number of requests per second the system handles. |
| **CAP Theorem** | 3 | A system can only provide two of Consistency, Availability, and Partition Tolerance during a network fault. |
| **Replication** | 3 | Copying data to multiple servers for durability or read scaling. |
| **CDN (Content Delivery Network)** | 4 | A geographically distributed network of servers that cache content close to users. |
| **Reverse Proxy** | 4 | A server that accepts client requests and forwards them to backend servers. |
| **API Gateway** | 4 | A reverse proxy that manages API routing, authentication, and rate limiting. |
| **Cache** | 4 | A temporary, fast storage layer that holds frequently accessed data. |
| **Load Balancer** | 4 | Distributes incoming requests across multiple servers. |
| **HLD (High-Level Design)** | 4 | The overall architecture diagram showing components and connections. |
| **Shard** | 5 | A horizontal partition of a database — each shard holds a subset of data. |
| **Failover** | 6 | Automatically switching to a backup system when the primary fails. |
| **Horizontal Scaling** | 6 | Adding more machines to handle increased load. |
| **Circuit Breaker** | 6 | A pattern that stops requests to a failing service to prevent cascading failures. |
| **SPOF (Single Point of Failure)** | 6 | A component whose failure brings down the entire system. |
| **Idempotency** | — | The property that an operation can be applied multiple times without changing the result. |
| **Vertical Scaling** | — | Upgrading a single machine with more CPU, RAM, or storage. |

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
> Once you are comfortable with this framework, the [advanced module](14-interview-framework-advanced.md) (with its full mock interview walkthrough, seniority dialogue examples, 10-point evaluation rubric, and complete interview script) will give you everything you need to prepare confidently.
> Remember: the goal is not to design a perfect system. It is to demonstrate clear, methodical engineering judgment under time pressure.
