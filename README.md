# System Design Academy

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen)](#)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)
[![Language: Python](https://img.shields.io/badge/language-Python-3776AB)](#)

> **An interactive engineering manual for senior-level system design preparation, built around real architecture trade-offs, production code templates, and FAANG-style whiteboard execution.**

System Design Academy is a professional, open-source curriculum for engineers who want to move beyond memorized diagrams and learn how large systems actually behave under load, failure, replication lag, cache pressure, and global traffic.

---

## Curriculum Overview

| # | Module | What You Will Learn |
|---:|---|---|
| 01 | [Traffic Routing & Network Foundations](modules/01-traffic-routing.md) | DNS routing, CDNs, L4 vs L7 load balancing, reverse proxies, failover, and edge security |
| 02 | [Database Architectures & Scaling](modules/02-database-scaling.md) | CAP, replication, sharding, consistent hashing, Dynamo-style availability, GFS storage lessons, and SQL tuning |
| 03 | [Caching Strategies & Memory Management](modules/03-caching-memory.md) | Cache-aside, write-through, write-behind, LRU internals, Facebook Memcached patterns, leases, and cache crisis handling |
| 04 | [Distributed Systems & Communication](modules/04-distributed-comm.md) | TCP/UDP, REST vs gRPC vs WebSockets, consensus, Raft leader election, circuit breakers, retries, and jitter |
| 05 | [Asynchronous Processing & Message Queues](modules/05-async-messaging.md) | Message queues, pub/sub, Kafka partitions, RabbitMQ task queues, acknowledgments, backpressure, retries, and DLQs |
| 06 | [Real-World System Design Blueprints](blueprints/system-designs.md) | Interview-ready designs for a URL shortener, web crawler, and Twitter/X timeline engine |

---

## Why This Repo?

Most system design resources stop at boxes and arrows. This repository is built to go deeper.

- **Mermaid-rendered architecture diagrams** for concrete request paths, cache flows, consensus, fanout, and queue processing.
- **Production-ready code snippets** in Python and TypeScript for reverse proxies, consistent hashing, LRU caches, gRPC services, RabbitMQ workers, and retry patterns.
- **FAANG-style interview preparation** with explicit requirements, back-of-the-envelope math, bottleneck analysis, and senior-level trade-off framing.
- **Paper-inspired engineering lessons** from systems like Dynamo, GFS, and Facebook Memcached, translated into practical design patterns.

---

## Getting Started

Clone the repository:

```bash
git clone https://github.com/MachariaP/system-design-academy.git
cd system-design-academy
```

Read the modules in order:

```text
modules/01-traffic-routing.md
modules/02-database-scaling.md
modules/03-caching-memory.md
modules/04-distributed-comm.md
modules/05-async-messaging.md
blueprints/system-designs.md
```

Recommended study loop:

1. Read one module end-to-end.
2. Re-draw the Mermaid diagrams from memory.
3. Explain each trade-off out loud as if in an interview.
4. Run or adapt the code templates locally.
5. Apply the concepts to one new system design prompt.

---

## How To Contribute

Contributions are welcome, especially from engineers who want to add practical, interview-grade system design blueprints.

Good contributions include:

- New system design case studies.
- Improved architecture diagrams.
- More production-grade code templates.
- Better capacity estimates and bottleneck analysis.
- Corrections, clarifications, and source-backed improvements.

Suggested workflow:

```bash
git checkout -b feature/new-blueprint
# edit or add markdown files
git add .
git commit -m "Add system design blueprint for notification service"
git push origin feature/new-blueprint
```

Then open a pull request with:

- The design problem being solved.
- Key trade-offs covered.
- Any assumptions used for calculations.
- Screenshots or previews of Mermaid diagrams if helpful.

---

## Who This Is For

- Backend engineers preparing for senior system design interviews.
- Distributed systems learners who want practical architecture mechanics.
- Developer advocates and educators building teaching material.
- Engineering teams looking for clean internal study references.
- Open-source contributors who enjoy turning complex systems into clear guides.

---

## License

This project is released under the [MIT License](LICENSE).

If this helps you prepare, teach, or design better systems, consider starring the repository and sharing it with another engineer.
