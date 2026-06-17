# Mock Interview Simulator

Timer-based interview script for the interviewer. The candidate drives; the interviewer probes. Each section includes: what the interviewer says, candidate response templates, scoring cues, and anti-pattern alerts.

---

## Before Starting (2 min)

**Interviewer says:**
> "This will be a 45-minute system design interview. I'll give you a prompt. Please scope the requirements, propose an architecture, dive into specifics, and discuss trade-offs. I'll ask follow-ups along the way. Do you have any questions before we begin?"

**Interviewer prep:**
- Pick a prompt from `prompt-cards.md`
- Have the scoring rubric printed
- Start a timer (visible to candidate if virtual)

**Anti-pattern alert:** Candidate starts drawing before asking any questions. → Interrupt: "Before you draw, what would you like to clarify?"

---

## Phase 1: Prompt & Clarify (5 min)

**Interviewer says:**
> "Here's the problem: [read prompt]. Please start by clarifying requirements and constraints."

### What the interviewer evaluates
The candidate should ask 5 categories of questions before touching the whiteboard:

| Category | Sample Questions |
|----------|-----------------|
| Functional | "What are the primary user actions? What are edge cases?" |
| Non-functional | "What's the latency SLO? Availability target? Consistency requirement?" |
| Scale | "What's the DAU? Read-to-write ratio? Peak vs average traffic?" |
| Data | "What are the core entities? Any data retention policies?" |
| Constraints | "Any regulatory/compliance requirements? Budget or team constraints?" |

### Candidate Response Template

> "Let me start by clarifying the requirements. I have 5 areas I'd like to explore..."
>
> *Functional:* "The core use cases are X, Y, and Z. An edge case is..."
> *Non-functional:* "We need p99 latency under X, availability at Y nines, and Z consistency."
> *Scale:* "With N DAU, assuming M reads and W writes per user per day, that gives us..."
> *[Optional: "Actually, N DAU × M actions ÷ 86,400 = X QPS. Over 5 years, storage is..."]*

### Scoring cues (Requirements dimension)
- ✅ Asked clarifying questions before drawing
- ✅ Produced a numbered list of functional + non-functional requirements
- ✅ Wrote down DAU, QPS, storage, bandwidth
- ✅ Noted if the system fits on one server

### Anti-pattern alerts
- **Silent math:** Candidate estimates in their head without writing. → "Could you walk me through those numbers?"
- **Over-scoping:** Trying to design every feature. → "Focus on the top 3 use cases for now."
- **Under-scoping:** Missing non-functional requirements entirely.

---

## Phase 2: High-Level Design (10 min)

**Interviewer says:**
> "Great. Now sketch the high-level architecture. Show me the request path from client to storage."

### What the interviewer evaluates
The candidate should draw a layered diagram and explain each component's role.

### Candidate Response Template

> "Here's the architecture. The request flows through these layers..."
>
> *Edge:* "DNS routes to the nearest PoP. CDN serves cached content. L4/L7 LB terminates SSL and routes to app servers."
> *App tier:* "Stateless for horizontal scaling. Session state in Redis."
> *Cache:* "Redis cluster with cache-aside pattern for reads."
> *DB:* "Primary DB for writes, read replicas. Sharded across N nodes."
> *Async:* "Message queue decouples heavy operations. Workers pick up jobs."
>
> *CAP:* "Under partition, I choose AP because [reason]. Trade-off is..."
> *CDN:* "I choose pull CDN because [reason]."

### Deepening Questions (interviewer uses 2-3)

1. "You mentioned DNS — geolocation vs latency-based routing? Why?"
2. "Your web tier — how does it scale from 10 to 10,000 instances?"
3. "You drew a cache and a database — what if the cache node fails?"
4. "Why that specific message queue? What's your delivery guarantee?"
5. "Is your design single-region? How would you make it multi-region?"

### Scoring cues (Architecture dimension)
- ✅ Complete layered diagram
- ✅ Component roles explained
- ✅ CAP decision stated
- ✅ Stateless app tier
- ✅ Edge layer included (DNS/CDN/LB)

### Anti-pattern alerts
- **One-box syndrome:** Everything crammed into one box labeled "app server."
- **Missing arrows:** No direction of data flow.
- **Vague labels:** "Cache" without specifying type or strategy.
- **No CAP mention:** Interviewer should prompt: "What happens during a network partition?"

---

## Phase 3: Deep Dive (15 min)

**Interviewer says:**
> "Let's zoom in on [bottleneck component]. Walk me through the schema, data model, and how you'd scale that component."

### How the interviewer selects the deep dive

| System Type | Dive Into |
|-------------|-----------|
| Read-heavy | Caching strategy, DB replication, denormalization |
| Write-heavy | Message queue, batch processing, NoSQL choice |
| Low-latency | In-memory cache, CDN, specialized index |
| Real-time | WebSocket management, ordering, fan-out |

### Candidate Response Template

> "The bottleneck in this system is [component]. Let me dive deep."
>
> *Schema:* "Here's the SQL schema. Primary key is X. Index on Y for the query pattern Z."
> *DB Choice:* "I choose [SQL/NoSQL] because the access pattern is [pattern]."
> *Sharding:* "Shard key is X with consistent hashing. Virtual nodes handle heterogeneous servers."
> *Caching:* "Cache-aside with 10-min TTL. Leases prevent stampede. Gutter pool for failover."
> *Hot spot:* "For celebrities/hot keys, I add a dedicated cache layer and increase replication."

### Advanced Probing Drills

If the candidate is strong, push harder:

**Drill 1 — Consistency:** "You chose eventual consistency. Walk me through a specific scenario where two users see different data. How does your system resolve it?"

**Drill 2 — Shard rebalancing:** "You're adding 10 new nodes to your consistent hash ring. Walk me through the data migration. What could go wrong?"

**Drill 3 — Cache stampede:** "Your most popular cache key expires at peak traffic. 10K requests hit the DB simultaneously. Walk me through the timeline. How do your mitigations work step by step?"

**Drill 4 — Schema contest:** "I disagree with your schema design. I'd denormalize this into a single table. Convince me why your normalized approach is better."

### Scoring cues (Deep Dive dimension)
- ✅ Schema with keys, types, indexes
- ✅ DB choice justified by access pattern
- ✅ Shard key with reasoning
- ✅ Cache strategy with invalidation
- ✅ Hot-spot mitigation

### Anti-pattern alerts
- **No schema at all:** Candidate stays abstract. → "Can you write the actual SQL?"
- **Wrong DB type:** Using SQL for time-series or document store for financial transactions.
- **No shard key:** "I'll just use auto-increment." → "What happens when you exceed one node?"
- **Cache as magic:** "I'll cache everything." → "What's your cache-to-DB size ratio?"

---

## Phase 4: Trade-offs & Stress Test (10 min)

**Interviewer says:**
> "Let's stress-test this. Walk me through what happens under these scenarios..."

### The "What If" Scenarios

Interviewer picks 2-3:

| Scenario | What to Watch For |
|----------|-------------------|
| "Traffic spikes 10x" | Stateless scale-out, queue back pressure, read replica scaling |
| "Database master fails" | Failover time, unreplicated writes, 503 handling |
| "A celebrity uses your system" | Hot-key mitigation, fan-out on read for celebs |
| "Network partition between DCs" | CAP decision in action, sloppy quorums, hinted handoff |
| "Cache cluster loses 3 nodes" | Gutter pool, stampede prevention, graceful degradation |

### Candidate Response Template

> "Let me stress-test this systematically..."
>
> *Scenario 1 (traffic spike):* "Web tier auto-scales. Cache hit ratio drops but gutter pool absorbs. Queue fills → back pressure → 503s with exponential backoff. Read replicas take read load."
>
> *Trade-off articulation:* "I chose [X] over [Y] because [reason]. Benefit: [what we gain]. Cost: [what we sacrifice]. Mitigation: [how we handle the cost]."
>
> *Security:* "JWT at the edge with PKCE. mTLS between services. Short-lived tokens + refresh flow."

### Recap (last 5 min)

**Interviewer says:**
> "We have 5 minutes left. Give me a 60-second summary of your design and the top 3 risks you'd want to address before shipping."

### Candidate Response Template

> "Summary: [2-3 sentence description]."
>
> *Risk 1:* "Cache stampede under celebrity event — mitigated by leases and gutter pool."
> *Risk 2:* "Consistency during cross-region replication — mitigated by CRDTs."
> *Risk 3:* "Queue back pressure bound — mitigated by monitoring and auto-scaling workers."
>
> "I'd implement these in order: caching first, then replication strategy, then observability."

### Scoring cues (Trade-offs + Communication dimensions)
- ✅ Trade-off framework used (benefit/cost/mitigation)
- ✅ Multiple failure scenarios handled
- ✅ Graceful degradation described
- ✅ Security/auth discussed
- ✅ Recap was structured and concise

### Anti-pattern alerts
- **Silver bullet:** "We'll use Kubernetes and it'll be fine."
- **No trade-offs admitted:** All decisions presented as obviously correct.
- **Recap too long:** Fails to summarize in 60 seconds.
- **No risks stated:** Implies the design is perfect.

---

## Debrief (15 min, post-interview)

### Interviewer-led debrief structure

1. **Share scores** per rubric dimension (1-2 min)
2. **One strength** — what the candidate did best (2 min)
3. **One growth area** — lowest-scoring dimension (3 min)
4. **Re-do** — re-run the weak section with the same prompt (5 min)
5. **Action items** — 3 specific things to practice before next session (3 min)

### Self-debrief (solo practice)

1. Score yourself on each dimension. Be honest.
2. Where did you spend too much time? Where too little?
3. What question made you freeze? Write it down.
4. Re-do that section immediately — second attempt always reveals the gap.
