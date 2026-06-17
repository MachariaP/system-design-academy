# Capacity Planning & Estimation – A Beginner's Guide

**You've used this when...**

You are planning a road trip. You estimate the total distance (requests), fuel efficiency (bandwidth), how much luggage fits in the trunk (storage), and where you will stop for gas (cache). If you guess wrong on fuel, you run out of gas in the desert — the engineering equivalent of a midnight pager alert that the database is full.

You start a new job and the team is building a feature for 100 million users. Your tech lead asks: "How many servers do we need?" You cannot say "I don't know" — and you cannot just throw money at the problem either. Capacity planning is how you produce a reasoned estimate that lets the team order hardware, provision cloud resources, and set launch timelines with confidence.

You join a startup that is growing 5x per year. The founder says "just add more servers when we need them." But by the time you notice the database is full, provisioning takes 2 weeks. Your users experience errors. Capacity planning is what lets you predict growth and stay ahead of it — so the system never runs out of room.

> This guide explains how to estimate the resources your system will need — servers, storage, bandwidth, and memory — using simple back-of-the-envelope math.
> Every technical term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand these foundations, the original advanced module will feel like a natural next step.
>
> **Before you start:** You should understand [Module 1: Traffic Routing](/Docs/01-traffic-routing.md) and [Module 3: Caching & Memory](/Docs/03-caching-memory.md). If you haven't read those yet, start there.

---

## Table of Contents

1. [Why Capacity Planning Matters](#1-why-capacity-planning-matters)
2. [Latency Numbers Every Programmer Should Know](#2-latency-numbers-every-programmer-should-know)
3. [The Power of Two Rules](#3-the-power-of-two-rules)
4. [The Basic Formulas: QPS, Storage, Bandwidth](#4-the-basic-formulas-qps-storage-bandwidth)
5. [Peaks and Bursts: Why Averages Lie](#5-peaks-and-bursts-why-averages-lie)
6. [The Estimation Framework Step-by-Step](#6-the-estimation-framework-step-by-step)
7. [Worked Example: A Photo-Sharing App (100M DAU)](#7-worked-example-a-photo-sharing-app-100m-dau)
8. [Common Mistakes and How to Avoid Them](#8-common-mistakes-and-how-to-avoid-them)
9. [Putting It All Together — Presenting Your Estimates](#9-putting-it-all-together--presenting-your-estimates)
10. [Glossary of Technical Terms](#10-glossary-of-technical-terms)
11. [Key Takeaways](#11-key-takeaways)

---

> **💡 Quick Reference – Capacity Planning Shortcuts**
> | Item | Rule of Thumb |
> |------|--------------|
> | Traffic | **100K requests/day ≈ 1 QPS** |
> | Peak | **Design for 2–5× average** (launch day: 10×) |
> | L1 cache | 0.5 ns |
> | RAM | 100 ns |
> | SSD | 16 µs |
> | Cross-DC | 150 ms |
>
> **⏱ TL;DR — If you only learn 3 things from this module:**
> 1. **Capacity planning is about bounding uncertainty, not being exact** — produce ranges, state your assumptions, and use padding factors of 2-3× for unknowns.
> 2. **Always design for peak load, not average** — peak-to-average ratios of 2-5× are normal, and a launch day can hit 10×. If you provision for the average, you will fail under the first spike.
> 3. **Memorize the traffic shortcut: 100K requests/day ≈ 1 QPS** — and know the latency numbers (L1: 0.5 ns, RAM: 100 ns, SSD: 16 µs, Cross-DC: 150 ms) so you can estimate storage, bandwidth, and bottlenecks in minutes.

---

## 1. Why Capacity Planning Matters

**Capacity planning** is the process of estimating how much infrastructure your system needs before you build it. It answers questions like:

- How many servers do I need?
- How much storage will I need in 5 years?
- What network bandwidth is required?
- Will a single database be enough, or do I need sharding?

**Analogy:** Planning a cross-country road trip. You estimate the distance (requests), fuel efficiency (bandwidth), how much luggage fits in the trunk (storage), and where you will make pit stops (cache). If you guess wrong, you run out of gas in the desert — the engineering equivalent of a midnight pager alert that the database is full.

Capacity planning is not about being exact — it is about **bounding uncertainty**. You produce a range, not a single number, and you explain your assumptions.

---

## 2. Latency Numbers Every Programmer Should Know

These are the approximate times for common operations. Memorize them — they are the common language for making data-access trade-off decisions without running a benchmark.

| Operation | Latency | Human Scale |
|-----------|---------|-------------|
| L1 cache reference | 0.5 ns | 1 second |
| L2 cache reference | 7 ns | 14 seconds |
| Main memory (RAM) reference | 100 ns | 3.3 minutes |
| SSD random read | 16 µs (16,000 ns) | 8.9 hours |
| Same data-center round trip | 0.5 ms (500,000 ns) | 11.6 days |
| Cross-continental round trip (CA→NL) | 150 ms (150,000,000 ns) | 9.5 years |

**What this means in practice:**

- Reading from L1 cache is 300,000x faster than a cross-continental network call.
- If an engineer proposes "let's fetch this from the US database on every European request," that 150 ms per request adds up fast.
- If a feature requires 10 sequential database queries (each 10 ms), that is 100 ms — visible to the user.

---

## 3. The Power of Two Rules

Computers use binary (powers of 2), not decimal. These shortcuts let you estimate quickly in your head:

| Prefix | Power of 2 | Approx Value | Good for |
|--------|-----------|--------------|----------|
| Kilo (KB) | 2^10 | 1,024 | Small files |
| Mega (MB) | 2^20 | ~1 million | Images, documents |
| Giga (GB) | 2^30 | ~1 billion | Memory, SSD capacity |
| Tera (TB) | 2^40 | ~1 trillion | Database size |
| Peta (PB) | 2^50 | ~1 quadrillion | Data lakes |

**Key shortcut:** 2^30 ≈ 1 billion. If you see "1 billion bytes," round to 1 GB. The error (7.4%) is well within the margin of error for capacity planning.

### Traffic Shortcuts

| Daily Volume | Approx QPS |
|-------------|-----------|
| 1 million requests/day | ~12 QPS |
| 100 million requests/day | ~1,200 QPS |
| 1 billion requests/day | ~12,000 QPS |

**Memorize this:** 100,000 requests/day ≈ 1 QPS. From there, scale linearly.

Formula: `QPS = Daily Volume / 86,400` (seconds in a day).

---

## 4. The Basic Formulas: QPS, Storage, Bandwidth

### Queries Per Second (QPS)

```
QPS = (DAU × Actions per User per Day) / 86,400
```

Example: 100M DAU, each user sends 10 requests per day.
`QPS = (100,000,000 × 10) / 86,400 ≈ 11,574 QPS`

### Storage (5-Year)

```
Storage = Daily Data × 365 × 5 × Replication × Padding
```

Example: 100M new records per day, each 500 bytes, 2x replication, 1.3x padding.
`Daily: 100M × 500 = 50 GB/day`
`5-year: 50 GB × 365 × 5 × 2 × 1.3 = ~237 TB`

### Network Bandwidth

```
Bandwidth (Gbps) = QPS × Avg Response Size × 8 / 1,000,000,000
```

The `× 8` converts bytes to bits. Network is measured in bits per second.

---

## 5. Peaks and Bursts: Why Averages Lie

Your system must handle **peak load**, not the average. The peak is always higher than the average.

| Scenario | Peak Multiplier |
|----------|----------------|
| Typical daily pattern | 2× average |
| Flash sale / launch day | 5× average |
| Viral event (rare) | 10× average |

### Choosing Your Peak Multiplier

| System Type | Suggested Multiplier | Rationale |
|-------------|---------------------|-----------|
| Internal enterprise tool | 1.5-2× | Predictable usage patterns, business hours only |
| Consumer app (stable) | 2-3× | Daily cycles, weekends higher than weekdays |
| E-commerce / ticketing | 5-10× | Flash sales, holiday spikes, ticket drops |
| Social media / viral content | 10-20× | A single share can double traffic in minutes |
| Startup (pre-launch) | 5-10× | Unknown demand — be conservative until you have data |

**Why this matters:** If your average QPS is 10,000, but you provision for 10,000, the system will fail during the first traffic spike. If a launch goes viral and QPS hits 50,000, you have a complete outage.

**Always design for peak.** The peak-to-average ratio is the most commonly underestimated factor in capacity planning.

---

## 6. The Estimation Framework Step-by-Step

Here is the workflow for estimating any system's capacity:

1. **Clarify scope.** What is the DAU? What actions does each user perform? What is the data model (size per entity)?

2. **Calculate QPS.** Writes and reads separately.

3. **Calculate storage.** How much data per day? Multiply by 365 × years × replication × padding.

4. **Calculate bandwidth.** QPS × response size. Convert to Gbps.

5. **Calculate cache size.** Typically 20% of daily reads (the "hot" data that should be cached).

6. **Identify bottlenecks.** Based on the numbers, will a single database suffice? Do you need sharding? A CDN? A message queue?

7. **Add padding.** Multiply everything by 2-3x for unknowns and growth.

---

## 7. Worked Example: A Photo-Sharing App (100M DAU)

Let's estimate the capacity for a photo-sharing app with 100 million daily active users.

### Assumptions

- DAU: 100 million
- Each user views 20 photos per day, uploads 2 photos per day
- Average photo size: 500 KB (compressed)
- Metadata per photo: 500 bytes
- Read:Write ratio: 10:1 (20 reads for every 2 writes)
- Retention: 5 years
- Replication factor: 3x for database, 2x for object storage
- Padding: 2x for unknowns

### QPS

- **Write QPS:** (100M × 2) / 86,400 ≈ 2,315 writes/sec
- **Read QPS:** (100M × 20) / 86,400 ≈ 23,150 reads/sec
- **Peak QPS (2× multi):** ~46,000 reads/sec, ~4,600 writes/sec

### Storage (5 years)

- **Photo storage:** 100M × 2 photos × 500 KB × 365 × 5 × 2 (replication) × 2 (padding)
  = 100M × 2 × 500 KB × 365 × 5 × 2 × 2
  ≈ 2M photos/day × 500 KB × 3,650
  ≈ 365 PB → with 2x padding ≈ 730 PB

- **Metadata storage:** 100M × 2 × 500 bytes × 365 × 5 × 3 (replication) × 2 (padding)
  ≈ 100M × 2 × 500 × 365 × 5 × 3 × 2
  ≈ 1 PB

### Bandwidth

- **Upload bandwidth:** 2,315 writes/sec × 500 KB × 8 (bytes to bits)
  ≈ 9.3 Gbps peak

- **Download bandwidth:** 23,150 reads/sec × 500 KB × 8
  ≈ 92.6 Gbps peak

### Cache Sizing (20% of daily reads)

- Daily reads: 100M × 20 = 2 billion reads
- 20% = 400 million hot reads
- 400M photos × 500 KB = 200 GB of hot data → allocate ~300 GB cache

### Conclusion

- A single database server cannot handle 2,315 writes/sec or 730 PB of storage. **Sharding is required.**
- The read load (23K QPS) can be handled by a Redis/Memcached cluster with ~300 GB.
- Photos should go to object storage (like S3) with a CDN in front.
- Upload bandwidth of 9.3 Gbps and download of 92.6 Gbps are significant but manageable with a CDN.

---

> **✏️ Check Your Understanding**
> 1. Your chat app has 50 million DAU. Each user sends 5 messages and reads 20 messages per day. Average message size is 1 KB (with metadata). Calculate the write QPS, read QPS, and 3-year storage (no replication, 1.5× padding).
> 2. You estimate average QPS of 5,000 for an e-commerce site and provision for exactly 5,000. On Black Friday, traffic spikes to 8× average. What happens, and what should you have done differently?
> 3. Your photo-sharing app stores both photos (500 KB average) and short videos (5 MB average). Users upload 2 photos and 0.5 videos per day. Why is it dangerous to use a single "average object size" of 1.5 MB for your storage estimate?
> <details>
> <summary>Answers</summary>
> 1. **Write QPS:** (50M × 5) / 86,400 ≈ 2,894 writes/sec. **Read QPS:** (50M × 20) / 86,400 ≈ 11,574 reads/sec. **Storage:** 50M × 5 msgs × 1 KB × 365 × 3 × 1.5 ≈ 411 TB.
> 2. **The system crashes.** At 8× (40,000 QPS), the servers, database, and network are all overwhelmed. You should have provisioned for at least 5× average (25,000 QPS) as a baseline, with auto-scaling to handle spikes beyond that.
> 3. **Averaging hides the real cost.** Photos contribute 2 × 500 KB = 1 MB/day/user. Videos contribute 0.5 × 5 MB = 2.5 MB/day/user. Despite being only 20% of uploads, videos consume 71% of storage. If you model them separately, you get an accurate picture; if you average them, you underestimate by a factor of ~2.4×.
> </details>

---

## 8. Common Mistakes and How to Avoid Them

### Confusing Bytes and Bits
**Symptom:** Your bandwidth estimate says 1 Gbps is needed. In reality, you need 8 Gbps. The network is saturated on day one.
**Root Cause:** Bandwidth is measured in bits per second (Gbps). Storage is measured in bytes (GB, TB). Forgetting the ×8 conversion leads to an 8× underestimation of bandwidth requirements.
**Real Incident:** Multiple startups have under-provisioned network capacity because they treated storage estimates (bytes) as bandwidth estimates (bits). One well-known messaging app had to scramble to upgrade its inter-datacenter links after launch because the ×8 conversion was overlooked in capacity planning.
**Fix:** Always apply the ×8 conversion when moving from storage to bandwidth. Remember: 1 Gbps = 125 MB/s.
**How to Detect Early:** Cross-check your bandwidth number: if it looks too low relative to your storage numbers, you probably forgot the ×8. Run a simple sanity check: `Gbps ≈ (GB_per_sec × 8)`.

### Forgetting the Peak Multiplier
**Symptom:** You provision for average QPS of 10,000. On launch day, traffic is 5× higher. The system crashes under load. Users see 503 errors.
**Root Cause:** You designed for average load, not peak. The peak-to-average ratio is the most commonly underestimated factor in capacity planning.
**Real Incident:** A major UK grocery delivery service saw its site crash on the first day of lockdown when traffic spiked to 5× normal. They had provisioned for average load and had no auto-scaling configured.
**Fix:** Always multiply by the peak factor (2-5×) when provisioning. Use auto-scaling to handle unexpected spikes beyond that.
**How to Detect Early:** Compare your provisioned capacity against historical traffic peaks. If the margin is less than 2×, you are at risk. Monitor CPU and connection utilization — sustained high utilization during non-peak hours is a warning sign.

### Linear Extrapolation
**Symptom:** You projected 100 TB of storage over 5 years. By year 3, you are at 300 TB. You have to migrate databases in an emergency.
**Root Cause:** You assumed linear growth, but your user base is growing 3× per year. By year 3, your estimates are off by a factor of 27.
**Real Incident:** Several social media platforms (including Twitter in its early years) experienced database capacity crises because growth was exponential while provisioning assumed linear trends. Emergency sharding migrations are among the highest-risk operations in production.
**Fix:** Model growth as a range ("worst case, best case"). Use compound growth: `year_n = starting_value × (1 + growth_rate)^n`. Revisit estimates quarterly.
**How to Detect Early:** Track month-over-month growth in DAU, storage, and QPS. If growth rate is accelerating, your linear model is already wrong. Set up trend-line alerts that flag when actual usage exceeds the projected curve by 20%.

### Overlooking Metadata Overhead
**Symptom:** You estimate 500 bytes per chat message. Your database is 3× larger than expected after 6 months.
**Root Cause:** Each message also has a database index, an ID, a timestamp, a sender field, and a delivery status flag. The actual storage is 3-5× the raw message size.
**Real Incident:** Discord engineers discovered that message metadata (author ID, channel ID, timestamp, flags, edit history) accounted for over 70% of their messages table storage, far exceeding the raw text content.
**Fix:** Apply a metadata overhead factor (typically 1.5-3× for databases, 3-5× for small objects). For any entity, estimate not just the payload but also the primary key, foreign keys, indexes, and padding.
**How to Detect Early:** Run `SELECT pg_size_pretty(pg_total_relation_size('table_name'))` or equivalent for your database. Compare actual storage to your estimated payload-only size. If the ratio exceeds 3×, your overhead factor needs adjustment.

### Averaging Object Size
**Symptom:** You estimate 500 KB average file size and 100 TB total storage. You hit 300 TB within a year.
**Root Cause:** 70% of the storage is consumed by videos (10 MB each), but you averaged them with photos (500 KB). The average hides the real cost.
**Real Incident:** Pinterest discovered that while Pins are mostly images, the growing number of video Pins was consuming storage at a rate 20× higher per Pin than images. Their original capacity model had to be completely rebuilt to separate the two object types.
**Fix:** Model different object types separately. Use weighted averages, not simple averages. For each type, calculate: `count × size × retention`.
**How to Detect Early:** Instrument storage usage by object type. If one type (e.g., videos) consumes a disproportionate share, model it separately. Monitor the ratio of storage consumed by each object type quarterly.

### Optimistic Padding
**Symptom:** You used a padding factor of 1.3× "because we will optimize later." The system runs out of capacity in 8 months instead of 24. You are doing an emergency migration at midnight.
**Root Cause:** You underestimated unknowns — growth, data explosion, new features, regulatory requirements. Optimistic padding is the most common cause of capacity emergencies.
**Real Incident:** A major cloud storage provider (Dropbox) experienced a storage capacity crisis in its early years because the engineering team used minimal padding in their estimates. The gap between projected and actual storage usage forced an expensive infrastructure acceleration program.
**Fix:** Use 2-3× padding for production estimates. You can tighten the numbers as you collect real data after 6-12 months of production experience.
**How to Detect Early:** Track the "time-to-capacity" metric: based on current growth, how many months until you hit your provisioned limit? If it is less than 3 months, you need to act immediately. Set an alert when this drops below 6 months.

---

## 9. Putting It All Together — Presenting Your Estimates

In a system design interview (or a real architecture review), you present your estimates like this:

> **Scope:** 100M DAU, 10:1 read/write ratio.
>
> **Assumptions:** 500 bytes per metadata record, 500 KB per photo, 2 uploads/day/user, 5-year retention.
>
> **QPS:** ~2,300 writes/sec, ~23,000 reads/sec. Peak (2×): ~4,600 / ~46,000.
>
> **Storage:** ~730 PB for photos (object storage), ~1 PB for metadata (sharded database).
>
> **Bandwidth:** ~9 Gbps upload, ~93 Gbps download peak. CDN needed.
>
> **Bottlenecks:** Single DB cannot handle 730 PB. Need sharding or NewSQL. Cache needed for reads (20% working set ~300 GB). CDN mandatory for photo delivery.
>
> **Padding:** All numbers include 2× padding. These are estimates — we will refine after launch with actual usage data.

Presenting a structured estimate shows you have thought about the system holistically. It is better to state your assumptions and be slightly wrong than to have no numbers at all.

---

> **🧪 Conceptual Exercises**
> 1. **Video Streaming Service:** Design a capacity plan for a Netflix-like service with 200 million subscribers. Each subscriber watches 1.5 hours of content per day. Average bitrate is 5 Mbps. Videos are encoded in 3 resolutions (480p, 720p, 1080p). Calculate: total daily bandwidth (in PBs delivered), peak bandwidth (assume 70% of viewing happens during 6 PM—midnight), and CDN edge storage if you cache the top 10% of the catalog (100K titles at 2 GB each on average). Where is the biggest bottleneck?
> 2. **IoT Sensor Pipeline:** A smart-building company deploys 10 million sensors, each sending a 1 KB reading every 5 minutes. You need to store raw data for 30 days, 1-minute rollups for 1 year, and 1-hour rollups for 5 years. Estimate the total storage (assume downsampling reduces 1-minute data by 60× to get hourly, and hourly is kept indefinitely). What is the write QPS at the ingress? Will a single database server handle it?
> <details>
> <summary>Hints</summary>
> 1. Break the problem into three parts: ingestion (encoding/writing), delivery (CDN egress), and storage. The biggest bottleneck is usually CDN egress bandwidth during peak hours. Remember that 5 Mbps × 1.5 hours × 200M users gives you total data delivered per day. But 70% in 6 hours means peak bandwidth is much higher than average. Consider the 90/10 rule for cache sizing.
> 2. Start with ingress: 10M sensors × 1 reading per 5 min = 2M writes/min ≈ 33K writes/sec. That alone likely exceeds a single database's write capacity. Consider a time-series database, partitioning by sensor ID range, and a message queue to buffer spikes. For storage, model each tier (raw, 1-min, 1-hour) separately with its retention period and downsampling factor.
> </details>

---

## 10. Glossary of Technical Terms

| Term | Section | Definition |
|------|---------|------------|
| **Capacity Planning** | 1 | Estimating future infrastructure needs based on expected usage. |
| **Cache** | 1 | A temporary, fast storage layer that holds frequently accessed data. |
| **Bandwidth** | 1 | The maximum rate of data transfer, typically measured in bits per second (bps). |
| **Latency** | 2 | The time delay between a request and its response. |
| **Byte vs Bit** | 4 | 1 byte = 8 bits. Storage is in bytes, network bandwidth is in bits. |
| **QPS (Queries Per Second)** | 4 | The number of requests handled per second. Also called RPS or TPS. |
| **DAU (Daily Active Users)** | 4 | The number of unique users who interact with the system in a day. |
| **Padding Factor** | 4 | A multiplier applied to estimates to account for unknowns, growth, and safety margins (typically 2-3×). |
| **Peak Multiplier** | 5 | The ratio of peak traffic to average traffic (typically 2-10×). |
| **Working Set** | 7 | The subset of data that is frequently accessed (typically ~20% of total data). |
| **Sharding** | 7 | Splitting a database across multiple servers to handle more data or traffic. |
| **Downsampling** | — | Reducing data resolution over time (e.g., raw 1-second → 1-minute → 1-hour rollups). |
| **TSDB (Time-Series Database)** | — | A database optimized for storing and querying timestamped metrics data. |

---

## 11. Key Takeaways

1. **Capacity planning is not about being exact.** It is about bounding uncertainty with reasoned assumptions.
2. **Memorize the latency table.** L1 (0.5 ns) → RAM (100 ns) → SSD (16 µs) → Cross-DC (150 ms).
3. **Memorize the traffic shortcut:** 100K requests/day ≈ 1 QPS. Scales linearly.
4. **Always design for peak load, not average.** 2× for typical peaks, 5× for launches.
5. **Storage grows deceptively fast.** Multiple multiplicative factors (users × actions × data size × retention × replication × padding).
6. **Model growth as a range.** Linear extrapolation hides exponential growth.
7. **Differentiate bytes and bits.** Storage = bytes, bandwidth = bits. The ×8 conversion matters.
8. **Cache the working set (20% of reads).** It saves enormous database load.
9. **Do not average different object types.** 10 MB videos and 500 byte messages have very different storage footprints.
10. **Use padding factors of 2-3×** for production estimates. Be optimistic only when you have real data.
11. **Revisit estimates before major launches.** A product launch can increase traffic by 10x or more.
12. **Structured estimates show engineering judgment.** Even rough numbers demonstrate systematic thinking.

---

> Once you're comfortable with these concepts, dive deeper in the [advanced companion module](13-capacity-planning-advanced.md), where we cover the full latency table with human time scaling, multi-tier cache sizing at exabyte scale, compound growth modeling, and three worked mock exercises (URL shortener, video streaming, social network profiles) with step-by-step math.
> Remember: you do not need perfect numbers — you need enough to make informed design decisions.
