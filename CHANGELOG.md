# Changelog

All notable changes to the **System Design Academy** curriculum are documented in this file.

This project follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) and uses versioned entries to make curriculum updates, blueprint additions, and documentation improvements easy to track.

---

## v1.3.0 - 2026-06-17

### Added

- Added advanced companion guides for all 14 modules in `Docs/` — each written from the perspective of a FAANG Principal Engineer with deep-dive sections, paper references (GFS, Dynamo, Raft, Facebook Memcached), real-world failure modes, and teacher's corner with grading rubrics:
  - `01-traffic-routing-advanced.md` — L4/L7 packet journey, edge architecture, CDN trade-offs
  - `02-database-scaling-advanced.md` — CAP theorem, SQL scaling, GFS control/data plane separation
  - `03-caching-memory-advanced.md` — Facebook Memcached blueprint, eviction mathematics, Bloom filters
  - `04-distributed-comm-advanced.md` — TCP vs UDP, RPC vs REST, circuit breakers, vector clocks
  - `05-async-messaging-advanced.md` — back pressure, service discovery, Black Friday case study
  - `06-service-mesh-advanced.md` — client-side vs server-side discovery, sidecar interception, control plane failure modes
  - `07-observability-advanced.md` — W3C trace context, error budget math, cardinality explosion
  - `08-security-auth-advanced.md` — JWT/JWKS, OAuth2 PKCE flow, mTLS, replay attack mitigation
  - `09-microservices-patterns-advanced.md` — Saga choreography/orchestration, transactional outbox with CDC, CQRS/event sourcing
  - `10-storage-systems-advanced.md` — block/file/object comparison, erasure coding math, bit rot detection
  - `11-stream-processing-advanced.md` — log-centric architecture, watermark semantics, Lambda vs Kappa
  - `12-distributed-consensus-advanced.md` — 2PC/3PC, Raft leader election, Dynamo vector clocks, election storms
  - `13-capacity-planning-advanced.md` — latency constants, QPS/storage/bandwidth framework, 100M DAU photo app sizing
  - `14-interview-framework-advanced.md` — 4-phase whiteboard roadmap, 10-point FAANG rubric, defensive whiteboarding

### Changed

- Updated all 14 beginner guides' closing notes to link to their respective advanced companions.

---

## v1.1.0 - 2026-06-16

### Added

- Added Module 06: Service Discovery & Service Mesh.
- Added Module 07: Observability: Monitoring, Logging, Tracing.
- Added Module 08: Authentication & Authorization.
- Added Module 09: Microservices Patterns (Saga, Outbox, CQRS, Event Sourcing).
- Added Module 10: File, Object & Block Storage.
- Added Module 11: Stream Processing & Real-Time Analytics.
- Added Module 12: Distributed Transactions & Consensus.
- Added Module 13: Back-of-the-Envelope Estimation & Capacity Planning.
- Added Module 14: System Design Interview Framework.
- Added beginner-friendly companion guides for all 14 modules in `Docs/`.
- Added 4th blueprint: Live Comments System (WebSocket fanout).
- Updated `README.md` curriculum table to cover all 14 modules and 4 blueprints.

---

## v1.0.0 - 2026-05-21

### Added

- Added the core curriculum structure with the `modules/` folder.
- Added Module 01: Traffic Routing & Network Foundations.
- Added Module 02: Database Architectures & Scaling.
- Added Module 03: Caching Strategies & Memory Management.
- Added Module 04: Distributed Systems & Communication.
- Added Module 05: Asynchronous Processing & Message Queues.
- Added beginner-friendly guides for modules 01-05 in `Docs/`.
- Added `blueprints/system-designs.md` with URL Shortener, Web Crawler, and Twitter Timeline Engine designs.
- Added initial `README.md` documentation for the repository.
- Added `CONTRIBUTING.md` with contribution guidelines.
- Added `LICENSE` for open-source distribution.

### Changed

- Established the initial documentation tone and structure for the project.

### Fixed

- No fixes in the initial release.
