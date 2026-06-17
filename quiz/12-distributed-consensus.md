# Module 12 — Distributed Consensus & Coordination — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** 2PC Coordinator Failure
**Type:** Multiple Choice

In Two-Phase Commit (2PC), what happens if the coordinator crashes after all participants have voted "yes" (Prepare phase) but before sending the Commit decision?

A) Participants automatically commit after a timeout
B) Participants automatically abort after a timeout
C) Participants remain in a blocked state, waiting for the coordinator to recover
D) Participants elect a new coordinator and continue

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Participants that voted "yes" are in a prepared (ready) state — holding locks, resources, and their transaction branch. They cannot independently decide to commit or abort because they don't know if the coordinator received all "yes" votes. They remain blocked until the coordinator recovers and reads its transaction log to determine the decision. This blocking property is the primary limitation of 2PC.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 2 🟢
**Topic:** Raft Leader Election
**Type:** Multiple Choice

In Raft, what triggers a new leader election?

A) A follower receives a client request
B) A follower's election timeout expires without receiving a heartbeat from the current leader
C) The leader voluntarily steps down every 10 minutes
D) A majority of nodes request an election

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Followers expect periodic heartbeats (AppendEntries RPCs with no entries) from the leader. If a follower's election timeout (randomized between 150-300ms typically) expires without receiving a heartbeat, it assumes the leader is dead, increments its term, becomes a candidate, and starts a new election by requesting votes from other nodes.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 3 🟢
**Topic:** Raft Terms
**Type:** Open-Ended

What is a "term" in Raft and why is it important?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A term is a monotonically increasing integer representing a period of time with a single leader. Each election begins a new term. If the election succeeds, the term has a single leader. If it fails (split vote), the term ends without a leader and a new term starts with a new election. Terms act as a logical clock that prevents stale leaders from making decisions — if a server receives a request with a stale term, it rejects it.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 4 🟢
**Topic:** Quorum
**Type:** Multiple Choice

What is a quorum in distributed consensus?

A) The minimum number of members that must agree to make a decision
B) The total number of nodes in a cluster
C) The maximum number of nodes that can fail
D) The leader's voting power

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** A quorum is the minimum number of nodes that must participate in a decision (vote) for it to be valid. In Raft, a majority quorum (⌊n/2⌋ + 1) is required for leader election and log entry commitment. For a 5-node cluster, the quorum is 3. This ensures that at most one leader can be elected per term (the quorum intersection property).

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 5 🟢
**Topic:** Vector Clock
**Type:** Open-Ended

What is a vector clock and what problem does it solve in distributed systems?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A vector clock is a data structure used to determine causal ordering of events in a distributed system without a centralized clock. Each node maintains a vector of counters (one per node). When an event occurs, the node increments its own counter. When messages are exchanged, vector clocks are merged. Vector clocks detect concurrent updates (conflicts) — if two updates are causally unrelated, they are concurrent. Vector clocks are used in Dynamo-style databases for conflict detection during read-repair.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 6 🟢
**Topic:** Gossip Protocol
**Type:** Multiple Choice

What is a gossip protocol primarily used for in distributed systems?

A) Encrypting data between nodes
B) Disseminating information (e.g., membership lists, failure detection) in a decentralized manner
C) Resolving transaction conflicts
D) Electing a leader

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Gossip protocols periodically exchange information with a random subset of peers (like epidemic spreading). Each node shares its knowledge, which propagates exponentially. Use cases: membership management (SWIM), failure detection, metadata propagation (e.g., Cassandra's ring state), and configuration dissemination. Gossip is decentralized, fault-tolerant, and eventually consistent.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 7 🟢
**Topic:** CFT vs BFT
**Type:** Open-Ended

What is the difference between Crash Fault Tolerance (CFT) and Byzantine Fault Tolerance (BFT)?

<details>
<summary>Answer & Explanation</summary>

**Answer:** CFT handles nodes that crash or fail silently — they stop responding but don't act maliciously. Raft, Paxos, and ZooKeeper's Zab are CFT protocols. BFT handles nodes that may behave arbitrarily or maliciously (Byzantine faults) — sending conflicting or corrupted messages. BFT protocols (e.g., PBFT, HotStuff) require at least 3f + 1 nodes to tolerate f faulty nodes, while CFT requires 2f + 1. BFT is used in blockchain consensus and safety-critical systems.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 8 🟢
**Topic:** Raft Log Replication
**Type:** Multiple Choice

In Raft, when does a log entry become "committed"?

A) When the leader writes it to its own log
B) When a majority of servers have replicated the entry to their logs
C) When all servers have applied the entry to their state machines
D) When the client acknowledges receipt

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** A log entry is committed when the leader has replicated it to a majority of the cluster (the quorum). Once committed, the entry is durable and will eventually be applied to all servers' state machines. The leader applies the entry to its own state machine and responds to the client only after committing.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 9 🟡
**Topic:** Raft Election Timeout Tuning
**Type:** Open-Ended

Why does Raft randomize election timeouts? What happens if all followers have the same timeout?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Randomization prevents election storms (split votes). If all followers have the same timeout, they would all become candidates simultaneously when the leader fails. Each would vote for itself and no one would get a majority (they all split the vote). After their election timeouts expire, they'd try again with the same result — the cluster would never elect a leader. Randomizing timeouts (e.g., 150-300ms) ensures that one follower's timeout expires slightly before the others, giving it time to request votes and win the election before the others time out.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 10 🟡
**Topic:** Raft Log Matching
**Type:** Multiple Choice

What happens in Raft if a follower's log is inconsistent with the leader's log (e.g., the follower has extra entries or missing entries)?

A) The follower is removed from the cluster
B) The leader forces the follower to adopt its log, overwriting conflicting entries
C) The follower's log takes precedence
D) A manual merge is required

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Raft's log matching is leader-driven: if the leader finds that a follower's log diverges (detected via PrevLogIndex/PrevLogTerm mismatch in AppendEntries), it finds the latest common entry and deletes any conflicting entries on the follower. The leader then sends all subsequent entries to bring the follower's log in line. This ensures all servers eventually have identical logs.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 11 🟡
**Topic:** 3PC (Three-Phase Commit)
**Type:** Open-Ended

How does 3PC improve upon 2PC? What limitation remains?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 3PC adds a third phase — **Pre-commit** — between Prepare and Commit. After all participants vote "yes," the coordinator sends a "pre-commit" message. Participants acknowledge. Only then does the coordinator send "commit." The pre-commit phase gives participants knowledge that all other participants voted "yes," so if the coordinator crashes after pre-commit, participants can independently commit without blocking.

**Remaining limitation:** 3PC still cannot tolerate network partitions. If a partition occurs, some participants may receive pre-commit while others don't, leading to inconsistency. 3PC is also more complex and slower (more message rounds). For practical systems, Raft/Paxos are preferred.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 12 🟡
**Topic:** Dynamo Read-Repair
**Type:** Open-Ended

What is read-repair in Dynamo-style databases? How does it provide eventual consistency?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Read-repair is a mechanism that detects and fixes stale replicas during read operations. When a client reads with consistency level QUORUM, the coordinator fetches data from all replicas, compares vector clocks to detect conflicts, resolves (using last-write-wins or application-level conflict resolution), and returns the freshest data. If some replicas returned stale data, the coordinator asynchronously writes the freshest version back to those replicas. Over time, read-repair heals inconsistencies without requiring a separate anti-entropy process.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 13 🟡
**Topic:** Election Storm
**Type:** Open-Ended

What is an election storm in Raft and under what conditions are they likely to occur?

<details>
<summary>Answer & Explanation</summary>

**Answer:** An election storm occurs when multiple servers become candidates at nearly the same time, each starting an election. If the vote is split (no candidate gets a majority), all candidates time out and start new elections. This can repeat indefinitely, preventing the cluster from electing a leader.

**Conditions:** Election storms are likely when: (1) election timeouts are too short relative to heartbeat interval, (2) timeouts are not sufficiently randomized, (3) network latency spikes cause multiple followers to miss the same heartbeat, (4) the cluster is large (more candidates competing), or (5) during cluster overload (CPU-bound nodes take longer to process heartbeats).

**Mitigation:** Randomize election timeouts, use pre-vote (a candidate checks if it's likely to win before starting a real election), and increase election timeout range.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 14 🟡
**Topic:** Dynamo Quorum Calculation
**Type:** Calculation

In a Dynamo-style database with N=5 (replication factor), W=3 (write quorum), R=3 (read quorum), what level of consistency is provided? If a network partition splits the cluster into 3 nodes and 2 nodes, can writes succeed on the 3-node side? Can reads on the 3-node side see the latest write?

<details>
<summary>Answer & Explanation</summary>

**Answer:** With W + R > N (3 + 3 = 6 > 5), this provides **strong consistency** for read-after-write. At least one replica in the read quorum overlaps with the write quorum, so the read will see the latest write.

**During partition (3+2 split):** The 3-node side has W=3 available (a quorum) → writes succeed. R=3 is also available on the 3-node side → reads succeed and see the latest write because W + R > N guarantees read-quorum/write-quorum intersection. The 2-node side cannot form W=3 or R=3 → both reads and writes fail. This means the majority partition continues operating, and the minority partition is unavailable — providing **availability** on the majority side and **consistency** across the whole system.

**Reference:** Docs/12-distributed-consensus.md
</details>

---

## Question 15 🔴
**Topic:** Raft Cluster Partition (Split-Brain) Analysis
**Type:** Whiteboard

A Raft cluster with 5 nodes is in a network partition: nodes A, B in one partition (P1) and nodes C, D, E in the other (P2). The leader (A) is in P1. Describe what happens in each partition. Can either side elect a new leader? Can either side commit new log entries? What happens when the partition heals?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**P1 (A, B — 2 nodes):** Node A is leader, continues sending heartbeats to B but cannot reach C, D, E. Follower B receives heartbeats from A, so no election is triggered. However, A cannot commit new log entries because it needs a majority (3/5) — it can only replicate to B (2/5), not a quorum. New writes hang (append but not committed) until quorum is restored.

**P2 (C, D, E — 3 nodes):** C, D, E stop receiving heartbearts from A. Their election timeouts expire. They start an election. With 3 nodes, they can form a majority (3/3). A new leader is elected (e.g., C). C can commit new log entries because it can replicate to D and E (3/5 = majority). This partition writes, commits, and serves clients normally.

**Result:** P2 elects a leader and commits writes. P1 cannot commit (old leader A is isolated and can't get majority). This is NOT split-brain — only one side (P2) can make progress.

**When partition heals:** Node A (old leader in P1) discovers its term is stale. It steps down and becomes a follower. The leader from P2 (C) is authoritative. Its log has entries committed during the partition that are missing on A and B. C replicates these entries to A and B. Any entries on A that were not committed are discarded (they weren't committed, so no data loss).

**Reference:** Docs/12-distributed-consensus-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Dynamo Vector Clock Conflict Resolution
**Type:** Debug

In a Dynamo-style database, two concurrent writes to the same key happen: Write 1 on node X (clock: [X:1]), Write 2 on node Y (clock: [Y:1]). These writes are replicated and a read on node Z returns both values with clock [X:1, Y:1]. The application uses last-write-wins (LWW) based on wall clock timestamps. A third write arrives with clock [X:1, Y:1, Z:1]. Explain what happened. How could this cause data loss? How would you recommend the application handle it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**What happened:** Writes 1 and 2 were concurrent (no causal relationship — X and Y operated independently). The read returned both as siblings with clock [X:1, Y:1]. LWW resolved by picking the write with the later wall-clock timestamp, silently discarding the other sibling. Write 3 (on Z) occurred after the read, so its clock [X:1, Y:1, Z:1] notes it causally depends on both preceding writes. But if LWW discarded a sibling, that sibling's data is **permanently lost**.

**Data loss scenario:** Write 1 set user.email = "alice@example.com". Write 2 (concurrent) set user.email = "bob@example.com". LWW picks the later one and the other email is lost forever. If a user had updated their email and this was the "lost" sibling, the change is silently rolled back.

**Recommendation:**
- Use **application-level conflict resolution** instead of LWW. Return all siblings to the application and let it merge (e.g., if updating a shopping cart, merge items from both versions).
- If LWW is necessary, ensure the application's data model supports CRDTs (Conflict-free Replicated Data Types) that automatically merge, such as last-writer-wins registers per sub-field, or use DynamoDB's "conditional writes."
- For Dynamo-style systems: never treat a sibling as discardable without application-level inspection.

**Reference:** Docs/12-distributed-consensus-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Raft Membership Change (Joint Consensus)
**Type:** Whiteboard

You need to change a Raft cluster from 3 servers to 5 servers without downtime. Explain why a naive approach (just add 2 servers) can cause split-brain. Describe how Raft's joint consensus handles this in two phases.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Naive approach failure:** If you add 2 servers directly (C_{new} = {A, B, C, D, E}), three servers {A, B, C} might both use the old config (thinking quorum is 2/3) while the new servers use the new config. A could be the leader of the old cluster {A, B, C} while D is elected leader of the new cluster {A, B, C, D, E} using the new quorum of 3 — splitting the system.

**Raft's Joint Consensus (two-phase):**
1. **Phase 1 (Joint):** The leader proposes the **joint configuration** C_{old} ∪ C_{new} = {A, B, C, D, E}. This requires a majority of BOTH C_{old} (2/3) AND C_{new} (3/5). Any decision needs 2/2 overlap = quorum intersection. During this phase, none of the servers are allowed to make decisions alone — both configs must agree.
2. **Phase 2 (New):** Once the joint config is committed, the leader proposes C_{new} = {A, B, C, D, E} alone. From this point, quorum is 3/5 normally. The old servers {A, B, C} no longer have standalone quorum.

**Key insight:** During joint consensus, cluster decisions require approval from both the old and new majorities. This prevents split brain because no single config can decide without the other.

**Reference:** Docs/12-distributed-consensus-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Gossip Protocol Convergence Analysis
**Type:** Whiteboard

Design a gossip-based membership protocol for a 500-node cluster that detects node failures within 10 seconds (p99) with <5% false positives. Describe the gossip rounds, failure detection mechanism, and how you prevent false positives during temporary network hiccups.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Protocol (based on SWIM — Scalable Weakly-consistent Infection-style Membership):**

1. **Gossip round:** Each node every 100ms selects a random peer and sends a ping. The peer responds with its membership list (including incarnation numbers).
2. **Indirect probing:** If the direct ping fails (timeout 200ms), the requesting node asks K random nodes (e.g., K=3) to ping the suspect node on its behalf. This handles the case where a specific network path is broken, not the node itself.
3. **Failure detection:** If direct ping and all K indirect probes fail, the node is marked "suspected" (not dead) with a suspicion timeout of 5 seconds. The suspicion is gossiped. If no confirmation of liveness arrives within suspicion timeout, the node is declared "dead."
4. **False positive prevention:** 
   - The **suspicion phase** prevents flapping — a momentary hiccup causes suspicion, not immediate death.
   - The suspected node has a chance to respond with an updated incarnation number to prove it's alive.
   - Heartbeats: if the suspected node is alive, it hears its own suspicion via gossip, increments its incarnation number, and gossips the new incarnation — clearing the suspicion.

**Convergence:** With 500 nodes and 100ms rounds prospecting 1 peer + 3 indirect probes, infection spreads exponentially. The false-suspicion-to-death time is ~5s, meeting the 10s detection p99. False positive rate: <1% with suspicion phase.

**Reference:** Docs/12-distributed-consensus-advanced.md
</details>

---

## Question 19 🔴
**Topic:** ZooKeeper vs Raft vs Paxos
**Type:** Open-Ended

Compare ZooKeeper's Zab, Raft, and Paxos. How do they differ in leader election, log replication, and exactly-once semantics? Under what scenario would you choose one over the others?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
| Aspect | Zab (ZooKeeper) | Raft | Paxos (Multi-Paxos) |
|---|---|---|---|
| **Leader election** | Uses a distinguished leader; election uses a "fast leader election" with epochs | Randomized election timeouts with terms; explicit RequestVote RPC | Leader lease via "preparing" phase; less explicit |
| **Log replication** | Leader proposes; followers acknowledge; commit at quorum ACK | Leader sends AppendEntries; committed when replicated to majority | Leader proposes number; acceptors promise/accept; commit at quorum |
| **Exactly-once** | Global ZooKeeper session — using zxid (ZooKeeper transaction ID) | At-least-once from client perspective unless idempotent client retry | At-least-once; relies on proposer idempotency |
| **Implementation complexity** | Moderate | Lowest (designed for teachability) | Highest (notoriously subtle) |

**When to choose:**
- **Zab/ZooKeeper:** When you need a coordination service (locks, configuration, group membership) in addition to consensus. ZooKeeper provides a hierarchical namespace, watches, and ephemeral nodes that aren't built into Raft.
- **Raft:** When you need a simple, well-understood consensus protocol to build a consistent key-value store or replicated state machine. Most popular for new projects (etcd, Consul, TiKV).
- **Paxos:** Legacy systems or very specific needs where the flexibility of leaderless (fast) Paxos is required. Generally, Raft has replaced Paxos for practical systems.

**Reference:** Docs/12-distributed-consensus-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Raft Performance — Throughput and Latency
**Type:** Calculation

A Raft cluster has 5 nodes spread across 3 AWS regions (us-east-1, us-west-2, eu-west-1) with a round-trip time of 60ms between US regions and 140ms between US and Europe. Each log entry is 1 KB. Calculate:
1. The minimum commit latency for a write
2. Maximum theoretical throughput
3. How does adding more nodes affect latency and throughput?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **Minimum commit latency:** The leader must replicate to a majority (3/5). The best case is the leader in us-east-1 → it needs 1 ACK from another US region (60ms RTT) + 1 ACK from either Europe (140ms) or the other US region (60ms). The pipeline: client → leader (0), leader sends to replicas (parallel). Commit after receiving majority ACKs = max of the two fastest ACKs = max(60ms, 60ms) = **~60ms** (if both secondaries are in the US). Worst case (leader in Europe, needs 2 US ACKs) = max(140ms, 140ms) = ~140ms.

2. **Maximum throughput with pipelining:** Raft pipelines AppendEntries requests — the leader doesn't wait for each commit to send the next. With TCP windows and batch size, throughput ≈ entry_size / (RTT / batch_count). If the leader batches 100 entries per AppendEntries, throughput ≈ 100 × 1 KB / (0.060 / 1) = ~100 KB / 0.06s = **~1.7 MB/s** (at 60ms). With larger batches (1000 entries at 1 KB each): ~17 MB/s. In practice, with modern pipelining and a single region, Raft clusters handle 10,000-50,000 ops/s.

3. **Adding more nodes:**
   - **Latency:** Increases latency because more replicas must ACK. A 7-node cluster needs 4/7 instead of 3/5 — the 4th could be the slowest one. Latency = max of the fastest N nodes where N = quorum size.
   - **Throughput:** Decreases slightly because more logs must be replicated. However, **read throughput can increase** because reads can be served from followers (with some latency).
   - **Failure tolerance:** Increases (3-node tolerates 1 failure, 5-node tolerates 2, 7-node tolerates 3).
   - **Recommendation:** 5 nodes is the sweet spot for most systems — good fault tolerance with reasonable latency.

**Reference:** Docs/12-distributed-consensus-advanced.md
</details>
