# Modules — Learning Path

This directory contains the 14 core curriculum modules of the System Design Academy.

## Recommended Reading Order

The modules build on each other. Start with Module 01 and progress sequentially:

| Order | Module | Prerequisites |
|------:|--------|--------------|
| 1 | [01 — Traffic Routing & Network Foundations](01-traffic-routing.md) | None |
| 2 | [02 — Database Architectures & Scaling](02-database-scaling.md) | Module 01 |
| 3 | [03 — Caching Strategies & Memory Management](03-caching-memory.md) | Module 02 |
| 4 | [04 — Distributed Systems & Communication](04-distributed-comm.md) | Module 02 |
| 5 | [05 — Async Processing & Message Queues](05-async-messaging.md) | Modules 03, 04 |
| 6 | [06 — Service Discovery & Service Mesh](06-service-mesh.md) | Module 04 |
| 7 | [07 — Observability & Telemetry](07-observability.md) | Modules 04, 05 |
| 8 | [08 — Authentication & Authorization](08-security-auth.md) | Module 04 |
| 9 | [09 — Microservices Patterns](09-microservices-patterns.md) | Modules 04, 05 |
| 10 | [10 — File, Object & Block Storage](10-storage-systems.md) | Module 02 |
| 11 | [11 — Stream Processing & Analytics](11-stream-processing.md) | Module 05 |
| 12 | [12 — Distributed Transactions & Consensus](12-distributed-consensus.md) | Modules 04, 05 |
| 13 | [13 — Capacity Planning & Estimation](13-capacity-planning.md) | Module 02 |
| 14 | [14 — System Design Interview Framework](14-interview-framework.md) | All modules |

## How to Use

Each module has two companion guides in `Docs/`:
- **Beginner guide** (`Docs/XX-module-name.md`) — plain language with analogies and glossaries
- **Advanced guide** (`Docs/XX-module-name-advanced.md`) — FAANG Principal Engineer deep-dive

**Flow:** Beginner Guide → Module → Advanced Guide → Quiz → Practice

## Companion Resources

| Resource | Location | Purpose |
|----------|----------|---------|
| Beginner Docs | `Docs/` | Plain-language introductions |
| Advanced Docs | `Docs/` | FAANG-level deep-dives |
| Question Banks | `quiz/` | Self-assessment (20+ questions per module) |
| Practice Materials | `practice/` | Mock interview simulator |
| System Blueprints | `blueprints/` | 10 full design walkthroughs |
| Code Examples | `code/` | Runnable Python implementations |
