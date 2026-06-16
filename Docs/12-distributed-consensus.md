# Distributed Transactions & Consensus – A Beginner's Guide

> This guide explains how multiple servers agree on a single truth even when some are failing, the network is broken, or messages are delayed.
> Every technical term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand these foundations, the original advanced module will feel like a natural next step.

---

## Table of Contents

1. [The Consensus Problem: Getting Multiple Machines to Agree](#1-the-consensus-problem-getting-multiple-machines-to-agree)
2. [Two-Phase Commit (2PC): All or Nothing](#2-two-phase-commit-2pc-all-or-nothing)
3. [Three-Phase Commit (3PC): Avoiding the Block](#3-three-phase-commit-3pc-avoiding-the-block)
4. [Raft: Electing a Leader](#4-raft-electing-a-leader)
5. [How Raft Replicates Data](#5-how-raft-replicates-data)
6. [Dynamo: Leaderless Consensus](#6-dynamo-leaderless-consensus)
7. [Vector Clocks: Detecting Conflicts](#7-vector-clocks-detecting-conflicts)
8. [Common Disasters and How to Avoid Them](#8-common-disasters-and-how-to-avoid-them)
9. [Putting It All Together — Keeping a Database Consistent Across Three Servers](#9-putting-it-all-together--keeping-a-database-consistent-across-three-servers)
10. [Glossary of Technical Terms](#10-glossary-of-technical-terms)
11. [Key Takeaways](#11-key-takeaways)

---

## 1. The Consensus Problem: Getting Multiple Machines to Agree

Imagine three friends (servers) keeping a shared diary. They all have copies, and they must agree on what is written. But:

- The phone line between them sometimes drops (network partition).
- One friend might fall asleep (server crash).
- A message might arrive after a long delay (latency).

The **consensus problem** is: *how do multiple machines agree on a single, coherent state despite network partitions, crashes, and delays?*

There are two families of solutions:
- **Leader-based consensus** (Raft): Elect one leader. The leader decides. Everyone follows the leader.
- **Leaderless consensus** (Dynamo): No leader. Every node can accept writes. Conflicts are resolved later.

---

## 2. Two-Phase Commit (2PC): All or Nothing

**Two-Phase Commit** is the classic protocol for ensuring that a transaction either succeeds on all servers or fails on all servers. It has two phases.

**Analogy:** A wedding ceremony. The officiant (coordinator) asks the audience: "Does anyone object?" (Phase 1 — Prepare). If nobody objects, the officiant says "I now pronounce you..." (Phase 2 — Commit). If anyone objects, the wedding is called off (Abort).

### Phase 1: Prepare
- The **Coordinator** sends a "prepare" message to all participants.
- Each participant prepares to commit (locks resources) and replies: "Yes" (ready) or "No" (abort).

### Phase 2: Commit or Abort
- If all participants replied "Yes", the coordinator sends "Commit". Everyone commits.
- If any participant replied "No" or timed out, the coordinator sends "Abort". Everyone aborts.

### The Blocking Problem

The fatal flaw: if a participant has voted "Yes" and the coordinator crashes before sending the final decision, that participant is **blocked**. It cannot unilaterally commit (others might have aborted) or abort (others might have committed). It holds its locks and waits for the coordinator to recover.

**Analogy:** The officiant asks "Does anyone object?" Nobody objects. But before the officiant can say "I now pronounce you," they faint. The guests freeze — they have already stated they have no objection, but they do not know whether the wedding is on or off.

In production, this means database rows remain locked, queue messages remain pending, and file handles remain open — waiting for a coordinator that may not come back.

---

## 3. Three-Phase Commit (3PC): Avoiding the Block

**Three-Phase Commit** adds an extra phase (Pre-Commit) to prevent blocking.

| Phase | 2PC | 3PC |
|-------|-----|-----|
| 1 | Prepare → vote | Prepare → vote |
| 2 | Commit / Abort | **Pre-Commit** (coordinator tells everyone: "a majority agreed") |
| 3 | — | Commit / Abort |

The extra phase gives participants enough information to decide unilaterally if the coordinator fails:

- If a participant received "Pre-Commit" and then the coordinator crashes, it knows a majority voted Yes. It can safely commit on a timeout.
- If a participant voted Yes but never received "Pre-Commit", it knows the coordinator failed early. It can safely abort.

**Reality check:** 3PC is rarely used in production. It is complex to implement correctly and can still fail under network partitions. Most systems prefer 2PC with a highly available coordinator (using Raft for the coordinator) or skip distributed transactions entirely in favor of Sagas.

---

## 4. Raft: Electing a Leader

**Raft** is a consensus algorithm designed to be understandable. It solves the agreement problem by having a **strong leader** that makes all decisions.

**Analogy:** Raft is like a parliamentary democracy. The leader (prime minister) is elected. Once elected, all decisions flow through the leader. If the leader becomes unreachable, a new election is held.

### The Three Roles

| Role | Description | Analogy |
|------|-------------|---------|
| **Leader** | The single authoritative node that accepts writes and replicates them | Prime Minister — makes all decisions |
| **Follower** | Passive nodes that replicate the leader's data | Cabinet members — approve the PM's proposals |
| **Candidate** | A follower that starts an election when it detects the leader is gone | Someone who calls for a new election |

### How Leader Election Works

1. All servers start as **followers**.
2. If a follower does not hear from the leader within a timeout (randomized, 150-300ms), it becomes a **candidate** and starts an election.
3. The candidate asks other servers for votes.
4. If it receives votes from a **majority** (`floor(N/2) + 1`), it becomes the **leader**.
5. The leader sends periodic heartbeats to maintain authority.
6. If the leader fails, followers detect the missing heartbeats and start a new election.

**Critical detail:** Election timeouts are **randomized** (each server picks a random timeout between 150-300ms). This prevents multiple candidates from starting elections simultaneously and splitting the vote forever.

---

## 5. How Raft Replicates Data

Once a leader is elected, all writes go through the leader:

1. **Client sends a write** (e.g., "set x = 5") to the leader.
2. The leader appends this command to its **log** (a file of pending operations).
3. The leader sends the log entry to all followers via `AppendEntries` RPC.
4. Each follower writes the entry to its own log and acknowledges.
5. When a **majority** of followers have acknowledged, the leader **commits** the entry (makes it visible to clients).
6. The leader tells the followers to commit.

**Why majority?** A majority (`N/2 + 1`) is the minimum number of nodes needed to guarantee that even if the current leader fails, any future leader will have seen the committed data. This is because majority sets always overlap — if you have 3 nodes, any 2 nodes always contain at least 1 node in common with any other 2 nodes.

---

## 6. Dynamo: Leaderless Consensus

Amazon's Dynamo (and its open-source descendants like Cassandra, Riak) takes a completely different approach: **there is no leader**. Any node can accept writes at any time.

**Analogy:** A whiteboard in a shared office where anyone can write. If two people write conflicting information at the same time, a third person later compares the two versions and merges them.

### Key Concepts

| Concept | What it means |
|---------|---------------|
| **N (Replication factor)** | How many nodes store each piece of data. N=3 means 3 copies. |
| **W (Write consistency)** | How many nodes must acknowledge a write before it is considered successful. W=2 means 2 out of 3 must confirm. |
| **R (Read consistency)** | How many nodes must respond to a read before returning the result. R=2 means query 2 of 3 nodes. |

For a system with N=3, W=2, R=2:
- A write succeeds when 2 of 3 nodes acknowledge. Even if 1 node is down, the write succeeds.
- A read queries 2 of 3 nodes. If they return different versions, the conflict is detected and resolved.

This gives **high availability**: the system can lose 1 node and still accept writes and reads.

---

## 7. Vector Clocks: Detecting Conflicts

When multiple nodes can accept writes without coordinating, conflicts are inevitable. How do you detect them?

A **vector clock** is like a version counter attached to each piece of data. It tracks which node has made how many updates.

### Example: Shopping Cart

1. **Initial state:** Cart is empty. Vector clock: `{A:1}` (Server A initialized it).
2. **Adding "book":** Server B handles the update. Clock: `{A:1, B:1}`.
3. **Adding "pen" (concurrently):** Server C handles another update from the same initial state. Clock: `{A:1, C:1}`.
4. **Comparing:** Is `{A:1, B:1}` ≥ `{A:1, C:1}`? No — B has a higher count (1 vs 0), but C has a higher count (1 vs 0). Neither clock completely dominates. These are **siblings** — a conflict.
5. **Resolution:** The application merges the carts: `["book", "pen"]`. New clock: `{A:1, B:1, C:1}`.

**Why not just use "last write wins"?** Because that would silently discard one update. If two users simultaneously add items to the same shopping cart, last-write-wins would lose one item. Vector clocks allow the system to detect the conflict and let the application merge intelligently.

---

## 8. Common Disasters and How to Avoid Them

### Split-Brain in Elasticsearch

A 6-node Elasticsearch cluster is configured with `minimum_master_nodes: 3`. A network partition splits the cluster into two groups of 3. Each group elects its own master. Two masters means both groups accept writes independently. When the network heals, reconciling the divergent data is impossible — data is lost.

**Mitigation:** Set `minimum_master_nodes` to a strict majority (`N/2 + 1`). For a 6-node cluster, that is 4 (not 3). This prevents any single group from electing a master. Also, use a **quorum-based approach** with a third node or witness.

### The etcd Election Storm

etcd (Kubernetes' consensus store) had an incident where Quality of Service (QoS) throttling slowed heartbeat messages. Heartbeats arrived late, triggering unnecessary elections. Each election caused more load, making the heartbeats slower, triggering more elections. 47 leader elections in 5 minutes. Kubernetes stopped working.

**Mitigation:** Ensure the election timeout is much larger than the heartbeat interval. The rule: `broadcastTime ≪ electionTimeout ≪ MeanTimeBetweenFailures (MTBF)`.

### 2-Node Raft Cluster

A Raft cluster with 2 nodes has no fault tolerance. If 1 node fails, the remaining 1 node cannot form a majority. The system stops.

**Mitigation:** Always run an odd number of nodes (3, 5, 7). A 3-node cluster tolerates 1 failure. A 5-node cluster tolerates 2.

### The `alg: none` of Consensus

In some JWT libraries, the server accepted "no algorithm" as valid (see the Security module). Similarly, in consensus, accepting writes without proper quorum is the equivalent — data is silently lost.

**Mitigation:** Always enforce strict quorum checks. Never accept writes that have not been acknowledged by a majority.

---

## 9. Putting It All Together — Keeping a Database Consistent Across Three Servers

Let's trace a write to a replicated database using Raft:

1. **Client sends a write** to the Raft cluster's known leader (Node 1).
2. The leader appends the write to its log and sends it to Node 2 and Node 3.
3. Node 2 receives the entry and acknowledges. Node 3 is slow (maybe under load).
4. The leader has received 2 of 3 acknowledgments — a majority. It commits the entry and responds to the client: "Write successful."
5. The leader tells both followers to commit. Node 2 commits. Node 3 eventually receives the entry, acknowledges, and commits.
6. **Now the leader (Node 1) fails.**
7. Node 2 detects the missing heartbeats (after a random timeout of ~200ms). It becomes a candidate.
8. Node 2 asks Node 3 for a vote. Node 3 votes for Node 2.
9. Node 2 wins with 2 of 2 votes (a majority of the remaining 2 nodes). It becomes the new leader.
10. Node 2's log contains the committed entry. The client's write is safe.
11. When Node 1 recovers, it rejoins as a follower. Node 2 catches it up on any entries it missed.

The write was never lost. The cluster survived a leader failure. The client experienced only a brief delay during the election.

---

## 10. Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **2PC (Two-Phase Commit)** | A protocol for atomic transactions across multiple nodes. Can block during coordinator failure. |
| **3PC (Three-Phase Commit)** | An extension of 2PC that adds a pre-commit phase to avoid blocking. Rarely used in practice. |
| **BFT (Byzantine Fault Tolerance)** | Consensus that tolerates nodes that intentionally lie or act maliciously. |
| **Candidate** | A Raft node that is holding an election. |
| **CFT (Crash Fault Tolerance)** | Consensus that tolerates nodes crashing but not malicious behavior. |
| **Commit** | Making a log entry visible to clients (permanent). |
| **Consensus** | The process of multiple servers agreeing on a single value or sequence of operations. |
| **Coordinator** | The node managing a 2PC or 3PC transaction. |
| **Election** | The process of selecting a new Raft leader. |
| **Follower** | A passive Raft node that replicates the leader's log. |
| **Heartbeat** | Periodic messages from the leader to followers to maintain authority. |
| **Leader** | The single authoritative node in Raft that accepts writes and replicates data. |
| **Log** | An ordered sequence of commands that the leader replicates to followers. |
| **Majority / Quorum** | More than half of the nodes: `floor(N/2) + 1`. |
| **Network Partition** | A condition where some nodes cannot communicate with others. |
| **Quorum** | The minimum number of nodes needed to agree for a decision to be valid. |
| **Raft** | A leader-based consensus algorithm designed for understandability. |
| **Read-Repair** | In Dynamo, correcting stale replicas during a read operation. |
| **Split-Brain** | Two partitions each electing a leader and accepting writes, causing divergence. |
| **Term** | A logical time unit in Raft — each election starts a new term. |
| **Vector Clock** | A data structure that tracks version history across nodes to detect conflicts. |

---

## 11. Key Takeaways

1. **Consensus = getting unreliable machines to agree.** There is no way around it in distributed systems.
2. **2PC is simple but blocking.** The coordinator crash during prepare locks resources across all participants.
3. **3PC avoids blocking** but is complex and rarely used. Most systems use 2PC with a replicated coordinator or skip distributed transactions entirely.
4. **Raft provides understandable consensus** with a strong leader, randomized elections, and majority-based commits.
5. **Raft elections must be randomized** to prevent vote-splitting. The timeout range (150-300ms) is essential.
6. **A Raft cluster needs an odd number of nodes** (3, 5, 7). 2 nodes provide zero fault tolerance.
7. **Dynamo-style consensus** trades strict consistency for availability. Any node can accept writes.
8. **Vector clocks detect conflicts** without losing data. Last-write-wins should never be used for critical data.
9. **Split-brain is prevented by quorum math**, not chance. A majority ensures at most one leader.
10. **Election storms happen when heartbeats are delayed.** Ensure heartbeat interval ≪ election timeout.
11. **Choose CFT or BFT based on trust.** CFT for internal systems (crash only), BFT for adversarial environments (blockchain, financial settlement).

---

> This guide explains the "why" behind distributed consensus protocols.
> Once you're comfortable with these concepts, the original module (with its Raft quorum simulator code, voting worked examples, and Elasticsearch split-brain case study) will serve as your in-depth reference.
> Remember: in a distributed system, agreeing on the truth is the hardest problem — and the most important one to get right.
