# Microservices Patterns (Saga, Outbox, CQRS, Event Sourcing) – A Beginner's Guide

> This guide explains the four essential patterns that maintain data integrity when a single business process spans multiple microservices and databases.
> Every technical term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand these foundations, the original advanced module will feel like a natural next step.

---

## Table of Contents

1. [The Problem: A Transaction Across Services](#1-the-problem-a-transaction-across-services)
2. [Why Not Just Use a Database Transaction?](#2-why-not-just-use-a-database-transaction)
3. [The Saga Pattern: Step-by-Step with a Safety Net](#3-the-saga-pattern-step-by-step-with-a-safety-net)
4. [Choreography vs Orchestration](#4-choreography-vs-orchestration)
5. [The Transactional Outbox: Never Lose a Message](#5-the-transactional-outbox-never-lose-a-message)
6. [CQRS: Separate Reading from Writing](#6-cqrs-separate-reading-from-writing)
7. [Event Sourcing: The Immutable Ledger](#7-event-sourcing-the-immutable-ledger)
8. [Common Disasters and How to Avoid Them](#8-common-disasters-and-how-to-avoid-them)
9. [Putting It All Together — An Order Flows Through a System](#9-putting-it-all-together--an-order-flows-through-a-system)
10. [Glossary of Technical Terms](#10-glossary-of-technical-terms)
11. [Key Takeaways](#11-key-takeaways)

---

## 1. The Problem: A Transaction Across Services

Imagine an e-commerce system with separate services for **Orders**, **Payments**, **Inventory**, and **Shipping**. When a user places an order, the system must:

1. Create the order record.
2. Charge the credit card.
3. Reserve inventory.
4. Schedule shipment.

In a monolith, this would be a single database transaction: all four steps succeed or all four fail together. But in a microservice architecture, each service has its own database. There is no "global transaction" that spans all four databases.

This is the fundamental challenge: **how do you keep data consistent across multiple services without a shared database?**

---

## 2. Why Not Just Use a Database Transaction?

Traditional **Two-Phase Commit (2PC)** is a protocol that tries to coordinate transactions across databases. But it has a fatal flaw for microservices:

**Analogy:** 2PC is like a coordinated wedding toast. The best man asks everyone to raise their glasses ("prepare"), waits for every single guest to confirm they are ready ("vote"), and only then says "cheers" ("commit"). If one guest is stuck in traffic, everyone stands there with raised glasses, unable to drink.

In database terms, those "raised glasses" are **row-level locks**. If the coordinator crashes, every participant is stuck holding locks, unable to proceed or release them. In a microservice environment, this can bring down the entire system.

This is why microservice systems have moved to **eventual consistency** — accepting that data will be briefly inconsistent but will eventually become correct.

---

## 3. The Saga Pattern: Step-by-Step with a Safety Net

A **Saga** is a sequence of local transactions. Each step updates its own service's database and then triggers the next step. Unlike 2PC, each step **commits immediately** — no locks are held across services.

The key innovation: **compensating transactions**. If step 3 fails, the system runs "undo" operations for steps 1 and 2.

**Analogy:** Imagine you book a hotel, then rent a car, then reserve a restaurant table. If the restaurant is full, you don't want to be stuck with a hotel and car but no dinner. So you undo: cancel the car rental, cancel the hotel. Each cancellation is a compensating transaction (and may have its own fees or rules).

```text
Forward: Book Hotel → Rent Car → Reserve Restaurant
                                     ↓ (FAIL)
Compensate:            ← Cancel Car ← Cancel Hotel
```

**Important:** A compensating transaction is not always a perfect inverse. If step 1 was "send confirmation email," the compensation might be "send a follow-up email saying the previous email was in error" — you cannot "un-send" an email. The compensation must leave the system in a **semantically consistent** state, not necessarily the exact previous state.

---

## 4. Choreography vs Orchestration

There are two ways to coordinate a Saga:

### Choreography (No Central Coordinator)

Each service listens for events and decides what to do next. The work flows like a bucket brigade: each person passes the bucket to the next.

```
Order Service: "OrderCreated!"
    → Payment Service: "PaymentApproved!"
        → Inventory Service: "InventoryReserved!"
            → Shipping Service: "ShipmentScheduled!"
```

**Analogy:** A bucket brigade — each person passes the bucket to the next. Nobody is directing the flow; everyone knows their role.

**Pros:** Highly decoupled, simple for linear workflows (2-4 services).
**Cons:** Workflow logic is spread across every service's event handlers. Hard to track what went wrong in a complex flow.

### Orchestration (Central Coordinator)

A single **Saga Orchestrator** tells each service what to do. The orchestrator manages the full workflow, tracks progress, and triggers compensations on failure.

**Analogy:** A film director. The director tells the actor ("action!"), the cinematographer ("roll camera!"), and the sound engineer ("record!"). If something goes wrong, the director calls "cut!" and tells everyone to reset.

**Pros:** Easy to audit, debug, and manage complex workflows. The logic is in one place.
**Cons:** The orchestrator is stateful and must track the current step. It can become a bottleneck.

| Factor | Choreography | Orchestration |
|--------|-------------|---------------|
| Complexity | Low for simple flows | Moderate (orchestrator is a service) |
| Decoupling | Maximum | Services know about the orchestrator |
| Debugging | Hard (logic spread everywhere) | Easy (one place to look) |
| Best for | 2-4 services, simple linear flows | 5+ services, complex branching, strict auditing |

---

## 5. The Transactional Outbox: Never Lose a Message

A common problem in microservices is the **dual-write**: you update the database and send a message (to notify other services) in the same operation. What if the database update succeeds but the message sending fails? Or vice versa?

**Analogy:** You try to mail a letter and also update your diary. If you update your diary but the letter gets lost in the mail, you have a problem — you think you sent it, but nobody received it.

The **Transactional Outbox** pattern solves this:

1. Instead of sending the message directly, you write both the business data and the message (called an "outbox record") in the **same database transaction**.
2. A separate process (the **message relay**) reads the outbox table and sends the messages to the message broker.
3. Once a message is successfully sent, the relay marks it as sent or deletes it.

**The trick:** The outbox write and the business data write are in the same transaction, so they succeed or fail together. The message relay can be implemented by polling the database or by using **CDC (Change Data Capture)** — reading the database's write-ahead log (WAL) to see what changed, and sending those changes as messages.

---

## 6. CQRS: Separate Reading from Writing

**CQRS** stands for **Command Query Responsibility Segregation**. It means using different models for reading data and writing data.

**Analogy:** A library has two different counters:
- The **check-in counter** (write model): you return books, the librarian updates the database.
- The **search counter** (read model): you look up where a book is, using a separately maintained search index.

These are connected — when a book is checked in, the system updates both the records database and the search index — but they serve different purposes and can be optimized independently.

**Why CQRS matters in microservices:**

- **Reads and writes have different shapes.** A write might store one row, while a read might join data from five different services. With CQRS, you can create a **read model** that is pre-joined, denormalized, and optimized for the specific query.
- **Independent scaling.** You can have 10 read replicas and 1 write master.
- **Different storage.** You might write to PostgreSQL and read from Elasticsearch.

**The cost:** Eventual consistency. When you write data, the read model is updated asynchronously. There is a brief period where a read returns stale data. This is acceptable for many use cases (catalog search) but not for others (displaying the payment status after a purchase).

---

## 7. Event Sourcing: The Immutable Ledger

**Event Sourcing** means storing the state of a system as a sequence of events, rather than as the current state.

**Analogy:** A bank account. Instead of storing "current balance: $500," the bank stores every transaction: "Deposited $1000, Withdrew $200, Withdrew $300." The current balance ($500) is calculated by replaying all events.

**Why this is powerful:**

- **Full audit trail.** You know exactly what happened, in what order, and who did it. No data is ever deleted or overwritten.
- **Time travel.** You can reconstruct the state at any point in time (great for debugging).
- **Event-driven ecosystem.** The events can drive other services (the Saga pattern loves Event Sourcing).

**The cost:**

- **Complexity.** You now have two ways to access data: by replaying events (authoritative) and by reading snapshots (fast).
- **Storage.** You never delete anything. Over time, the event store grows unboundedly.
- **Schema evolution.** Old events have old schemas. Your code must handle all schema versions.

**Snapshots:** To avoid replaying millions of events every time, you periodically save a **snapshot** of the current state. To reconstruct state, you load the latest snapshot and replay only the events after it.

---

## 8. Common Disasters and How to Avoid Them

### Dual-Write Failure

You update the database and try to send a Kafka message. The database update succeeds, but Kafka is down. The message is lost forever — another service never finds out about the change.

**Fix:** Always use the Transactional Outbox pattern. The message is saved in the same database transaction as the business data.

### The Double Charge

A payment service receives a charge request. It charges the credit card successfully, but crashes before updating the order status. When it restarts, it retries the charge — the customer is charged twice.

**Fix:** Idempotency keys. The client sends a unique key with each request. The server checks if it has already processed this key. If yes, it returns the previous result without charging again.

### Saga Compensation Failure

A Saga is rolling back because payment failed. The "cancel shipment" step also fails (the shipping service is down). The system is now in an inconsistent state — hotel is cancelled but shipping is not.

**Fix:** The orchestrator must retry compensations with exponential backoff. If a compensation permanently fails, it must be escalated to a human operator (a "compensation dead letter queue").

### CQRS Stale Read

A user updates their profile and immediately sees the old data because the read model has not been updated yet.

**Fix:** For critical "read-your-writes" scenarios, read from the write model (the primary database) for a short window after the write. Use the read model only for other queries.

---

## 9. Putting It All Together — An Order Flows Through a System

Let's trace an order through a system that uses all four patterns:

1. **User places an order.** The Order Service writes the order and an outbox event ("OrderCreated") in the same database transaction (Transactional Outbox).

2. **Message relay picks up the event.** Debezium (CDC) reads the database WAL and publishes "OrderCreated" to Kafka.

3. **The Saga Orchestrator receives the event** and begins orchestrating the order fulfillment saga:
   - Tells Payment Service: "Charge $99.99" (the Payment Service uses idempotency keys).
   - Payment Service responds: "Approved" (or "Declined" → orchestrator starts compensations).

4. **Orchestrator tells Inventory Service:** "Reserve items." Inventory responds: "Reserved."

5. **Orchestrator tells Shipping Service:** "Schedule delivery." Shipping responds: "Scheduled."

6. **Orchestrator marks the saga as complete.** It writes to the read model (CQRS) so the search and display systems see the updated order status.

7. **The read model eventually catches up.** If a user checks the order status immediately, they might see "processing" (Eventual Consistency). A few seconds later, it shows "confirmed" (convergence).

8. **If any step fails at any point,** the orchestrator runs compensating transactions: cancel the charge, release inventory, cancel the shipment.

The system never holds locks across services. Each step commits independently. If something fails, compensations undo the damage. And every event is durably recorded for auditing.

---

## 10. Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **2PC (Two-Phase Commit)** | A protocol for atomic transactions across multiple databases. Blocking — rarely used in microservices. |
| **CDC (Change Data Capture)** | Reading a database's transaction log to detect and publish changes as events. |
| **Choreography** | A Saga style where each service decides independently based on events, with no central coordinator. |
| **Compensating Transaction** | An operation that undoes the business effect of a previous step in a Saga. |
| **CQRS (Command Query Responsibility Segregation)** | Separating the models used for reading data and writing data. |
| **Dual-Write** | The problem of updating two systems (DB + message broker) atomically without a distributed transaction. |
| **Event Sourcing** | Storing state as a sequence of immutable events rather than as the current state. |
| **Eventual Consistency** | A model where data may be briefly inconsistent but will converge over time. |
| **Idempotency** | The property that an operation can be repeated safely without changing the result. |
| **Idempotency Key** | A unique identifier that lets a server detect and skip duplicate operations. |
| **Message Relay** | A process that reads outbox records and publishes them to a message broker. |
| **Orchestration** | A Saga style with a central coordinator that manages the workflow. |
| **Outbox** | A database table where messages are written atomically with business data for reliable delivery. |
| **Read Model** | A denormalized, optimized view of data for querying (in CQRS). |
| **Saga** | A sequence of local transactions with compensating transactions for rollback. |
| **Snapshot** | A saved copy of state at a point in time, used to avoid replaying all events. |
| **Transactional Outbox** | The pattern of writing business data + outgoing messages in one DB transaction. |
| **WAL (Write-Ahead Log)** | The append-only log in a database that records every change before applying it. Used by CDC tools. |

---

## 11. Key Takeaways

1. **Distributed transactions (2PC) do not scale.** Locks held across services during a crash can bring down the system.
2. **Sagas break a large transaction into small, independent steps** with compensating transactions for rollback.
3. **Compensating transactions are not database rollbacks** — they are business operations that undo the effect (e.g., "send cancellation email" vs. "un-send email").
4. **Choreography is simpler for linear workflows** (2-4 services). Orchestration is better for complex flows with auditing needs.
5. **The Transactional Outbox solves the dual-write problem** — write business data and message in one DB transaction.
6. **CDC (Debezium) is more reliable than polling** for reading the outbox — it does not put extra load on the database.
7. **CQRS lets you optimize reads and writes independently** — different models, different storage, different scaling.
8. **Event Sourcing provides full auditability** — every change is recorded as an immutable event. State is derived by replay.
9. **Snapshots prevent unbounded replay** — combine the latest snapshot with events after it.
10. **Idempotency is the foundation of safe retries.** Always use idempotency keys for payment-like operations.
11. **Eventual consistency is a trade-off:** better scalability and availability, but you must handle stale reads gracefully.
12. **The four patterns work together:** Saga for orchestration, Outbox for reliable messaging, CQRS for read/write separation, Event Sourcing for the audit trail.

---

> This guide explains the "why" behind the four essential microservices data patterns.
> Once you're comfortable with these concepts, the original module (with its Saga orchestrator code, Debezium CDC setup, and production failure postmortems) will serve as your in-depth reference.
> Remember: strong consistency is a luxury of the monolith. In distributed systems, you design for eventual consistency and handle the edge cases explicitly.
