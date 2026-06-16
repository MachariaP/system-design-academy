# Capacity Planning & Estimation – A Beginner's Guide

> This guide explains how to estimate the resources your system will need — servers, storage, bandwidth, and memory — using simple back-of-the-envelope math.
> Every technical term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand these foundations, the original advanced module will feel like a natural next step.

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

## 8. Common Mistakes and How to Avoid Them

### Confusing Bytes and Bits

Bandwidth is measured in bits per second (Gbps). Storage is measured in bytes (GB, TB). Forgetting the ×8 conversion will lead to an 8x underestimation of bandwidth requirements.

**Check:** 1 Gbps = 125 MB/s. If your bandwidth estimate seems too low, check if you forgot the ×8.

### Forgetting the Peak Multiplier

You calculate average QPS of 10,000 and provision for exactly 10,000. On launch day, traffic is 5× higher. The system crashes.

**Fix:** Always multiply by the peak factor (2-5x) when provisioning.

### Linear Extrapolation

You project storage needs by assuming linear growth. But your user base is growing 3× per year. By year 3, your estimates are off by a factor of 27.

**Fix:** Model growth as a range ("worst case, best case"). Use compound growth: `year_n = starting_value × (1 + growth_rate)^n`.

### Overlooking Metadata Overhead

A chat message is 500 bytes. But each message also has a database index, an ID, a timestamp, a sender field, and a delivery status flag. The actual storage is 3-5x the raw message size.

**Fix:** Apply a metadata overhead factor (typically 1.5-3x for databases, 3-5x for small objects).

### Averaging Object Size

Your photo-sharing app's average file size is 500 KB. But 70% of the storage is actually consumed by videos (10 MB each). Averaging hides the real cost.

**Fix:** Model different object types separately. Use weighted averages, not simple averages.

### Optimistic Padding

You use a padding factor of 1.3× "because we will optimize later." You never optimize.

**Fix:** Use 2-3× padding for production estimates. You can tighten the numbers as you collect real data.

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

## 10. Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **Bandwidth** | The maximum rate of data transfer, typically measured in bits per second (bps). |
| **Byte vs Bit** | 1 byte = 8 bits. Storage is in bytes, network bandwidth is in bits. |
| **Cache** | A temporary, fast storage layer that holds frequently accessed data. |
| **Capacity Planning** | Estimating future infrastructure needs based on expected usage. |
| **DAU (Daily Active Users)** | The number of unique users who interact with the system in a day. |
| **Downsampling** | Reducing data resolution over time (e.g., raw 1-second → 1-minute → 1-hour rollups). |
| **Latency** | The time delay between a request and its response. |
| **Padding Factor** | A multiplier applied to estimates to account for unknowns, growth, and safety margins (typically 2-3×). |
| **Peak Multiplier** | The ratio of peak traffic to average traffic (typically 2-10×). |
| **QPS (Queries Per Second)** | The number of requests handled per second. Also called RPS or TPS. |
| **Sharding** | Splitting a database across multiple servers to handle more data or traffic. |
| **TSDB (Time-Series Database)** | A database optimized for storing and querying timestamped metrics data. |
| **Working Set** | The subset of data that is frequently accessed (typically ~20% of total data). |

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

> This guide explains the "why" behind capacity planning and estimation.
> Once you are comfortable with these concepts, the original module (with its detailed worked exercises for chat systems, metrics pipelines, and the 4 AM storage meltdown case study) will serve as your in-depth reference.
> Remember: you do not need perfect numbers — you need enough to make informed design decisions.
