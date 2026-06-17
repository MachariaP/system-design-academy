# Scoring Rubric — System Design Mock Interview

Total: **10 points** (2 pts per dimension). **≥ 7 = hire**. **8–9 = strong hire**. **10 = bar raiser**.

Aligned with the FAANG Master Evaluation Checklist from the curriculum.

---

## Dimension 1: Requirements (2 pts)

*Corresponds to: Requirements Bounding, Back-of-the-Envelope Estimation*

| Score | Definition |
|-------|-----------|
| **0** | Starts drawing immediately without clarifying. No functional/non-functional list. No traffic estimates. |
| **1** | Asks some clarifying questions but misses key constraints (latency SLO, write/read ratio, data retention). Estimates are incomplete or off by >10x. |
| **2** | Extracts full requirement set: functional (core + edge), non-functional (latency, consistency, durability), and scale (DAU → QPS → storage → bandwidth over 5 years). Notes whether the system fits on a single server before proposing distribution. |

**Checklist:**
- [ ] Asked clarifying questions before drawing
- [ ] Listed functional requirements
- [ ] Listed non-functional requirements (latency, consistency, availability)
- [ ] Calculated DAU → Read QPS / Write QPS
- [ ] Calculated storage (5-yr with padding)
- [ ] Calculated bandwidth (ingress/egress)
- [ ] Determined single-server vs distributed

---

## Dimension 2: Architecture (2 pts)

*Corresponds to: CAP Alignment, Edge Integrity, Stateless Scaling*

| Score | Definition |
|-------|-----------|
| **0** | No coherent diagram. Missing core components (LB, cache, DB). No CAP consideration. |
| **1** | Basic boxes-and-arrows but missing edge layer (CDN, DNS), no component justification, no CAP discussion. Web tier may be stateful. |
| **2** | Clean layered diagram: DNS → CDN → L4/L7 LB → stateless app tier → cache → DB → queue → workers. CAP decision stated explicitly (CP vs AP with justification). Edge security included (SSL termination, rate limiting). Stateless scaling explained. |

**Checklist:**
- [ ] DNS routing explained
- [ ] CDN strategy (push vs pull) chosen and justified
- [ ] L4 vs L7 LB justified
- [ ] Web/app tier is stateless
- [ ] CAP decision stated (CP or AP with justification)
- [ ] Message queue positioned for async work
- [ ] Edge security (SSL termination, rate limiting)

---

## Dimension 3: Deep Dive (2 pts)

*Corresponds to: DB Justification, Sharding Logic, Cache Strategy*

| Score | Definition |
|-------|-----------|
| **0** | No schema, no sharding, no caching — or all three are wrong for the access pattern. |
| **1** | Schema presented but incomplete. DB choice is asserted without justification. Sharding or caching mentioned but no detail on key selection, invalidation, or stampede prevention. |
| **2** | SQL schema with keys and indexes. DB type justified by access pattern (SQL for ACID, NoSQL type for specific access needs). Shard key chosen with consistent hashing + virtual nodes. Cache strategy specified (cache-aside, write-through, etc.) with invalidation plan and stampede mitigation (leases, jittered TTLs). |

**Checklist:**
- [ ] Schema with primary keys, indexes, data types
- [ ] DB choice justified by access pattern
- [ ] Shard key chosen with reasoning
- [ ] Consistent hashing + virtual nodes
- [ ] Hot-spot mitigation (celebrity problem)
- [ ] Cache strategy chosen
- [ ] Cache invalidation addressed
- [ ] Thundering herd prevented (leases / jittered TTLs)

---

## Dimension 4: Trade-offs (2 pts)

*Corresponds to: Async Decoupling, Graceful Degradation*

| Score | Definition |
|-------|-----------|
| **0** | No trade-offs discussed. Design presented as "perfect." No failure scenarios. |
| **1** | Mentions one or two trade-offs but doesn't articulate benefit/cost/mitigation. Failure scenarios acknowledged but not designed for. |
| **2** | Every architectural decision includes explicit trade-off articulation: "I choose A over B because X. Benefit: Y. Cost: Z. Mitigation: W." Stress-tests the design with 3+ "What If" scenarios (traffic spike, network partition, master failure, cache stampede, replication lag). Graceful degradation described: what breaks, what degrades, what survives. |

**Checklist:**
- [ ] Trade-off framework used for ≥2 decisions
- [ ] Benefit / Cost / Mitigation stated for each
- [ ] "What If" scenarios addressed
- [ ] Graceful degradation defined
- [ ] Async decoupling / back pressure discussed
- [ ] Retry + circuit breaker strategy

---

## Dimension 5: Communication (2 pts)

*Corresponds to: Security & Auth, Overall Senior Signal*

| Score | Definition |
|-------|-----------|
| **0** | Mumbles, jumps between topics, ignores interviewer's questions, defensive. |
| **1** | Coherent but reactive — waits for interviewer to drive. Misses security/auth discussion. Doesn't connect decisions to trade-offs naturally. |
| **2** | Drives the whiteboard independently. States "everything is a trade-off" unprompted. Discusses security (JWT/OAuth2, mTLS, PKCE) as primary architecture. Focuses on p99 latency, not averages. Mentions observability (SLIs/SLOs, tracing). Uses structured language: "Let me scope this first...", "The bottleneck here is...", "To stress-test this design...". |

**Checklist:**
- [ ] Drives the session, doesn't wait for prompts
- [ ] Structured communication (phases are clear)
- [ ] Security/auth discussed proactively
- [ ] Mentions p99, not just averages
- [ ] Mentions observability / monitoring
- [ ] Audience-aware (adjusts depth to interviewer signals)

---

## Quick Scorecard

| Candidate | Requirements (/2) | Architecture (/2) | Deep Dive (/2) | Trade-offs (/2) | Communication (/2) | **Total** | **Decision** |
|-----------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| | | | | | | **/10** | |

**Hire threshold: ≥ 7/10.** Below 7: identify the two weakest dimensions and target them in next practice session.
