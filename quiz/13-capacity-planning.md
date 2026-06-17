# Module 13 — Capacity Planning & Estimation — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** Latency Constants
**Type:** Multiple Choice

Approximately how long does it take to read 1 MB sequentially from memory (RAM)?

A) 10 ns
B) 250 μs
C) 10 ms
D) 100 ms

<details>
<summary>Answer & Explanation</summary>

**Answer:** B — approximately 250 μs (microseconds).

**Explanation:** Typical latency numbers: L1 cache reference: ~1 ns, L2 cache: ~7 ns, RAM random access: ~100 ns, RAM sequential read 1 MB: ~250 μs, SSD random read: ~150 μs, SSD sequential read 1 MB: ~1 ms, Disk seek: ~10 ms, Network round trip (intra-DC): ~500 μs.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 2 🟢
**Topic:** DAU to QPS Conversion
**Type:** Calculation

A social media platform has 100 million DAU (Daily Active Users). Each user makes an average of 5 requests per day. What is the average QPS (queries per second)? What is the peak QPS if you assume a peak factor of 5× the average?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Total daily requests = 100M × 5 = 500M. Average QPS = 500M / 86,400 ≈ **5,787 QPS**. Peak QPS = 5,787 × 5 = **~28,935 QPS**.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 3 🟢
**Topic:** Power of Two Rules
**Type:** Multiple Choice

According to the "power of two" rules for capacity planning, what does "2 is 1, 3 is 2, 4 is 3, 5 is 4" refer to?

A) Database indexing depth
B) The number of replicas needed for each level of fault tolerance in a quorum-based system
C) The relationship between CPU cores and optimal thread pool size
D) The relationship between cache size and hit rate

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** In quorum-based systems, with N replicas, you need a majority of ⌊N/2⌋ + 1 for writes. With 2 replicas, you need both (quorum = 2, tolerate 0). With 3, you need 2 (tolerate 1). With 4, you need 3 (tolerate 1). With 5, you need 3 (tolerate 2). So "2 is 1, 3 is 2, 4 is 3, 5 is 4" refers to the write quorum size for N replicas.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 4 🟢
**Topic:** Storage Estimation
**Type:** Calculation

A messaging app stores each message as 1 KB of data with metadata (sender, receiver, timestamp) adding 200 bytes. If there are 50 million DAU and each user sends 20 messages per day, how much storage is needed per day? How much for 5 years?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Daily messages = 50M × 20 = 1 billion messages. Each message = 1 KB + 200 B = 1.2 KB. Daily storage = 1B × 1.2 KB = 1.2 TB. Per year = 1.2 TB × 365 = 438 TB. For 5 years = 438 TB × 5 = **2.19 PB**. In practice, add replication (3×) and indexing overhead (~30%) → ~8.5 PB total.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 5 🟢
**Topic:** Bandwidth Estimation
**Type:** Open-Ended

A video streaming service delivers 10 Mbps per stream to 1 million concurrent viewers. What is the total egress bandwidth? Express in Gbps and estimate the monthly data transfer in PB.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Total bandwidth = 10 Mbps × 1M = 10,000,000 Mbps = **10,000 Gbps** (10 Tbps). Monthly transfer = 10,000 Gbps × 86,400 s/day × 30 days = 25,920,000,000 Gb. Convert to bytes: 25,920,000,000 / 8 = 3,240,000,000 GB ÷ 1,000,000 = **3,240 PB/month**. This is why CDNs are essential — they absorb the egress at edge locations and reduce origin bandwidth.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 6 🟢
**Topic:** Peak Factor
**Type:** Multiple Choice

What is the typical peak-to-average traffic ratio for consumer internet applications?

A) 1.1× to 1.5×
B) 2× to 20×
C) 50× to 100×
D) 1000× to 5000×

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Most consumer internet applications experience a peak-to-average ratio between 2× and 20×. Social media (global): ~2-5×, e-commerce flash sales: ~10-20×, video streaming: ~2-3× (evening prime time), messaging: ~3-5×. Enterprise/SaaS apps tend to have lower ratios (1.5-3×) since usage is constrained to business hours.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 7 🟢
**Topic:** Cache vs Database Latency
**Type:** Multiple Choice

A web page loads 50 resources (HTML, CSS, JS, images). If uncached, each requires a 200ms round trip to the server. If cached at the CDN, each requires a 20ms round trip. How much faster is the cached page load?

A) 2× faster
B) 10× faster
C) The difference is negligible
D) 50× faster

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Uncached: 50 × 200ms = 10 seconds (sequential) or parallel limited by browser's 6 concurrent connections per domain: ceil(50/6) × 200ms ≈ 1.8s. Cached: 20ms × ceil(50/6) ≈ 180ms. The improvement is roughly **10×** faster, ignoring the significant bandwidth savings at the origin.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 8 🟢
**Topic:** Latency vs Throughput
**Type:** Open-Ended

What is the difference between latency and throughput in capacity planning? Give an example where improving one hurts the other.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Latency is the time to complete a single operation (e.g., 50ms per request). Throughput is the number of operations completed per unit time (e.g., 10,000 requests/second). They are related but not directly proportional.

**Example where improving one hurts the other:** Batching. To increase throughput, you batch 100 requests into one network call — throughput increases (less overhead per request), but the first request in the batch now waits until 100 accumulate, increasing latency for that first request (batching delay). This is the latency-vs-throughput trade-off.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 9 🟡
**Topic:** QPS to CPU Cores Estimation
**Type:** Calculation

A service handles 50,000 QPS. Each request requires 15ms of CPU processing time. Assuming the service is CPU-bound and has zero queue wait at 60% utilization, how many CPU cores are needed? How many for 90% utilization?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Total CPU seconds per second = 50,000 × 0.015 = 750 CPU-seconds/second. So at 100% utilization, we need 750 cores. At 60% utilization: 750 / 0.6 = **1,250 cores**. At 90% utilization: 750 / 0.9 = **834 cores**. The lower utilization (more cores) provides better latency at the cost of more hardware. The higher utilization (fewer cores) saves cost but risks latency spikes from queueing.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 10 🟡
**Topic:** Bandwidth-Delay Product
**Type:** Open-Ended

What is the Bandwidth-Delay Product (BDP) and why does it matter for capacity planning of global services?

<details>
<summary>Answer & Explanation</summary>

**Answer:** BDP = Bandwidth × Round-trip Time. It represents the amount of data that can be "in flight" (unacknowledged) in a TCP connection. For a 10 Gbps link with 200ms RTT, BDP = 10 × 10^9 × 0.2 = 2 × 10^9 bits = ~250 MB. The TCP congestion window must be at least this large to fully utilize the link. If the window is smaller (e.g., 64 KB), throughput is capped at 64 KB / 0.2 = 3.2 Mbps regardless of link speed. For capacity planning, BDP determines the required socket buffer sizes and the number of concurrent connections needed to saturate a link.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 11 🟡
**Topic:** Database Connection Pool Sizing
**Type:** Calculation

A web service uses a PostgreSQL database. Each request takes 5ms of CPU work and 20ms waiting for a database query. The service handles 10,000 QPS. What is the minimum connection pool size? If a 50ms query latency spike occurs, what happens?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Little's Law: Concurrent requests in-flight = Throughput × Latency. For the database: each request occupies a connection for 20ms. Concurrent connections needed = 10,000 × 0.020 = **200 connections**.

**During latency spike (50ms):** Concurrent connections = 10,000 × 0.050 = 500 needed. If the pool is capped at 200, requests queue up waiting for a connection. The queue grows as: queue_depth = throughput × (spike_latency - normal_latency) / connections. With 200 connections and 50ms latency, each connection handles 20 req/s (1/0.050) = 4,000 req/s total → 6,000 req/s queue → queue grows at 6,000/second. P95 latency spikes significantly until the spike subsides.

**Recommendation:** Set connection pool to ~250-300 (safety margin), use connection pooling middleware (PgBouncer), and set a query timeout to prevent queue buildup from runaway queries.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 12 🟡
**Topic:** Storage IOPS Estimation
**Type:** Open-Ended

A database requires 50,000 random read IOPS (4 KB each) and 20,000 random write IOPS. How many 7,500 IOPS SSDs are needed? How does RAID 10 affect the write IOPS calculation?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Read IOPS needed: 50,000. Write IOPS needed: 20,000. Each SSD: 7,500 IOPS (mix). Assume R:W ratio is 5:2 (as given). Each SSD can handle ~7500 IOPS regardless of read/write mix (SSDs have similar read/write latency). Minimum SSDs = max(50,000 / 7,500, 20,000 / 7,500) = max(6.7, 2.7) = **7 SSDs** for a single server.

**RAID 10 effect:** RAID 10 mirrors writes (each write goes to 2 disks). Available write IOPS = (number_of_disks / 2) × IOPS_per_disk. With 8 disks in RAID 10: write IOPS = 4 × 7,500 = 30,000. Read IOPS = 8 × 7,500 = 60,000. This comfortably handles the workload. **Recommend 8 SSDs in RAID 10.**

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 13 🟡
**Topic:** Cache Hit Rate Impact
**Type:** Open-Ended

A CDN serves 100 TB/day of content at 95% cache hit rate. Origin bandwidth is 5 TB/day. If the hit rate drops to 90%, what is the increase in origin bandwidth? How does this affect cost if origin bandwidth costs $0.08/GB and CDN bandwidth costs $0.02/GB?

<details>
<summary>Answer & Explanation</summary>

**Answer:** At 95% hit rate: origin = 5% of total = 100 × 0.05 = 5 TB. At 90% hit rate: origin = 10% of total = 100 × 0.10 = 10 TB. **Origin bandwidth doubles** (increase of 5 TB/day = ~150 TB/month).

**Cost impact:** Origin bandwidth increase = 150 TB/month × $0.08/GB × 1000 = **$12,000/month more.** CDN bandwidth decreases by the same amount (5 TB/day less from CDN) = 150 TB/month × $0.02/GB = **$3,000/month savings.** Net cost increase = $12,000 - $3,000 = **$9,000/month.**

This shows why cache hit rate is such a critical metric — a 5% drop costs $9K/month.

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 14 🟡
**Topic:** Service-Level Capacity Calculation
**Type:** Calculation

A microservice has 10 instances, each with 4 CPU cores. Each request uses 50ms of CPU time. At 80% CPU utilization target, what is the maximum QPS the service can handle? If traffic grows 30% MoM for 3 months, how many additional instances are needed?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Total CPU cores = 10 × 4 = 40 cores. At 80% utilization: 40 × 0.80 = 32 effective cores. Total CPU-seconds per second = 32 CPU-seconds. Each request = 50ms = 0.05 CPU-seconds. Max QPS = 32 / 0.05 = **640 QPS**.

**Growth:** 30% MoM for 3 months = 1.3^3 = 2.197× growth. Future QPS = 640 × 2.197 = ~1,406 QPS. Future effective cores needed = 1,406 × 0.05 = 70.3 CPU-seconds. At 80% utilization: raw cores = 70.3 / 0.8 = 87.9 → **88 cores**. Current: 40 cores. Additional cores needed = 88 - 40 = 48 cores. With 4 cores per instance: **12 additional instances** (22 total).

**Reference:** Docs/13-capacity-planning.md
</details>

---

## Question 15 🔴
**Topic:** End-to-End Latency Budget Calculation
**Type:** Calculation

Design a system where a user clicks "Post Comment" and the comment appears on 1M followers' feeds within 5 seconds (p99). The path is: Client → Load Balancer (5ms) → API Server (50ms) → Write to Database (20ms) → Kafka (10ms) → Fanout Service (200ms to process 1M followers) → Push Notification Service (500ms). What's the total latency? Which component is the bottleneck and how would you optimize it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Total latency (serial):** 5 + 50 + 20 + 10 + 200 + 500 = **785ms**. This is well under 5 seconds. However, this is the simple case.

**Real bottleneck:** The Fanout Service processing 1M followers sequentially. 200ms per 1M followers might be too optimistic — writing 1M feed entries takes 1M × small_write_time. If each write takes 5ms, total = 1M × 0.005 = 5,000 seconds (unacceptable).

**Optimization:** 
- **Pre-compute fanout for high-profile users:** Maintain a pre-built feed for celebrity accounts. Followers read from it (pull model).
- **Hybrid fanout:** Fanout to currently online followers via push (use presence service → push to ~10%).
- **Batch writes:** Batch feed writes in groups of 100 → 10,000 batches × 5ms = 50 seconds. Still too slow. Use async batch updates with eventual consistency.
- **Actual recommendation:** Use a pull-based model for the feed (each follower queries their feed on app open). Cache the top N posts per user. The push notification serves as the "new content available" signal, not the feed itself.

**Revised budget:** Push notification fires immediately. Feed loads from cache when user opens app. Latency target: notification within 2 seconds (p99), feed load within 500ms (p99).

**Reference:** Docs/13-capacity-planning-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Global Database Capacity Planning
**Type:** Whiteboard

A global e-commerce platform has 500M products, 5 billion listings, and 1 billion users. The product catalog receives 200,000 reads/second and 2,000 writes/second. The transaction system processes 10,000 orders/second with 5-10 line items each. Design the database capacity plan across read replicas, sharding, and caching. Calculate the number of shards, replica lag impact, and cache memory needed.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Product catalog:**
- 500M products × 10 KB = 5 TB (hot data: 10% = 500 GB). Shard by `product_id` across 64 shards → ~78 GB per shard.
- Read replicas: 200K reads/s. Each DB can handle ~5K reads/s. Need 200K / 5K = 40 replicas. But use caching: 90% cache hit rate → 20K reads/s to DB → 4 replicas.
- Cache (Redis): 500 GB hot data, but store only active products (last 30 days) = ~50 GB. Use Redis Cluster with 10 GB per node → 5 nodes.

**Order system:**
- 10,000 orders/s. Each order + line items = ~2 KB. Write throughput = 10,000 ops/s. 
- Shard by `user_id` or `order_id`. With 100 shards → 100 writes/s per shard (well within single-node DB capacity).
- Replica lag: async replicas for read-your-orders. Target replica lag < 100ms. Use semi-sync replication or read from primary for recent orders.

**Total DB nodes:** 64 catalog shards × 1 primary + 4 replicas = 320 catalog nodes. 100 order shards × 1 primary + 2 replicas = 300 order nodes. Total: ~620 DB nodes. Use larger instances to reduce shards: 64 shards × 8xlarge = 64 primary nodes total.

**Reference:** Docs/13-capacity-planning-advanced.md
</details>

---

## Question 17 🔴
**Topic:** DAU Growth Capacity Planning
**Type:** Calculation

A startup currently has 500K DAU. Each user generates 50 write requests and 200 read requests daily. Average write response time is 50ms, average read response time is 10ms. User growth is 15% month-over-month. Plan capacity for 18 months. How many application servers (each handling 500 QPS) and database nodes (each handling 2,000 QPS at 60% target utilization) are needed at month 18?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Month 18 DAU:** 500K × (1.15)^18 = 500K × 11.97 = **~5.99M DAU**.

**Daily requests:** Writes = 5.99M × 50 = 299.5M/day. Reads = 5.99M × 200 = 1,198M/day. Total requests = 299.5M + 1,198M = 1,497.5M/day.

**QPS:** Average writes = 299.5M / 86,400 = **3,466 writes/s**. Average reads = 1,198M / 86,400 = **13,866 reads/s**. Total average QPS = **17,332 QPS**.

**Peak QPS (5× factor):** 86,660 QPS.

**Application servers (500 QPS each):** At peak: 86,660 / 500 = **174 servers** (allow 20% headroom → 209 servers).

**Database nodes:** Each DB handles 2,000 QPS at 60% target utilization = 1,200 effective QPS. Peak reads = 13,866 × 5 = 69,330 reads/s. Peak writes = 3,466 × 5 = 17,330 writes/s.

Read nodes = 69,330 / 1,200 = **58 nodes**. Write nodes = 17,330 / 1,200 = **15 nodes**. Total DB nodes = **73 nodes** (plus replicas for HA).

**Cost projection at month 18:** 209 app servers + 73 DB nodes + networking + cache + storage ≈ $200K-$400K/month. Significantly more if RDS-managed.

**Reference:** Docs/13-capacity-planning-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Kafka Capacity Planning
**Type:** Whiteboard

Design a Kafka cluster for an event-tracking pipeline: 500 million events/day, each event is 2 KB. Events must be retained for 14 days with 3× replication. The cluster uses the lowest cost per GB while meeting a write throughput target where the 99th percentile producer latency is under 500ms. Calculate storage, broker count, partition count, and choose between HDD and SSD.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Ingress:** 500M × 2 KB = 1 TB/day. With 3× replication: 3 TB/day stored. 14-day retention: 3 × 14 = **42 TB**.

**Throughput:** 500M / 86,400 = ~5,787 events/s × 2 KB = ~11.6 MB/s ingress. Replicated: ~34.7 MB/s.

**Broker count:** With 4 TB HDD per broker (cheapest) → 42 / 4 = ~11 brokers. With 2 TB SSD → 21 brokers. HDD is cheaper per GB.

**Partition count:** 500M events/day / 86,400 = 5,787 events/s. Each partition should handle well under the 10 MB/s recommendation. With 50 partitions → 5,787/50 = ~116 events/s per partition × 2 KB = ~232 KB/s (trivial). Use more partitions for parallelism: **50-100 partitions**.

**HDD vs SSD decision:** HDDs have higher sequential throughput (150-200 MB/s) but suffer on seek latency if many partitions contend. With only 11.6 MB/s ingress and HDDs handling ~100 MB/s each, HDD is sufficient IF each broker has few partition leaders. Spread partition leaders evenly. SSD is preferred if consumer groups are numerous (each consumer reads from multiple partitions, creating random reads). **Recommendation:** Use HDD for pure write-heavy tracking, SSD if the cluster also serves heavy consumer read workloads.

**Broker count (HDD):** 11 brokers with 4 TB HDD each. Partition: 100 partitions, replication factor 3. Each broker = 100 × 3 / 11 ≈ 27 replicas per broker (well within limits).

**Reference:** Docs/13-capacity-planning-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Network Capacity Planning
**Type:** Calculation

A data center has 2,000 servers, each with a 25 Gbps NIC. The network uses a leaf-spine topology with 40 leaf switches (each with 48×25G downlinks, 8×100G uplinks) and 8 spine switches (each with 40×100G ports). Calculate:
1. Total oversubscription ratio from server to leaf
2. Total oversubscription ratio from leaf to spine
3. Is this suitable for a latency-sensitive financial trading application?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **Server to leaf:** 40 leaves × 48 servers per leaf = 1,920 servers (close to 2,000). Downlink capacity per leaf = 48 × 25 Gbps = 1,200 Gbps. Uplink capacity per leaf = 8 × 100 Gbps = 800 Gbps. Oversubscription = 1,200 / 800 = **1.5:1**.

2. **Leaf to spine:** 40 leaves × 8 uplinks = 320 × 100 Gbps uplinks total. 8 spines × 40 ports = 320 × 100 Gbps spine capacity. Oversubscription from leaf to spine = 800 Gbps per leaf / (8 × 100) = **1:1** (no oversubscription at the spine layer — each leaf has exactly enough uplink bandwidth).

3. **Suitability for financial trading:** 1.5:1 oversubscription at the server-to-leaf layer means during peak contention, servers may experience 67% of their 25 Gbps throughput. For latency-sensitive trading, this is generally acceptable — leaf-spine provides predictable, low-latency paths (any server to any server in 2 hops). However, for HFT (high-frequency trading), you'd want 1:1 oversubscription at every layer (no contention) and potentially faster switching (using 100G NICs and switches with sub-microsecond latency).

**Reference:** Docs/13-capacity-planning-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Resource Estimation for Video Platform
**Type:** Whiteboard

Estimate the infrastructure cost for a YouTube-like platform with 500M MAU, 1 billion video views per day, average video length 10 minutes, average bitrate 5 Mbps. Include storage (videos uploaded at 500 hours/minute), CDN bandwidth, transcoding compute, and database. Provide a monthly cost estimate.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Video views:** 1B views/day. Average view: 10 min × 60 s × 5 Mbps / 8 = 375 MB per view. Total daily bandwidth: 1B × 375 MB = 375 PB/day ≈ 4.3 TB/s peak (assuming 2× peak factor). CDN cost: $0.01/GB delivered (bulk rate) → 375 PB/day × 1,000 GB/PB × $0.01 = $3.75B/day? No — that's $3.75B daily, clearly too high.

**Correction:** Not every view is a full 10 min. Average watch time may be 4 min. Average bitrate after transcoding to multiple resolutions: weighted average ~2 Mbps. Data per view: 4 min × 60 × 2 Mbps / 8 = 60 MB. Daily: 1B × 60 MB = 60 PB/day. CDN cost: 60,000 TB × $0.03/GB (blended) = **$1.8M/day = $54M/month**.

**Storage:** 500 hours uploaded/min × 60 × 24 × 30 = 21.6M hours/month. At 10 Mbps upload bitrate × 1 hour = 4.5 GB per raw hour. With transcoding (3 versions at avg 3 Mbps): ~5.4 GB per hour processed. Monthly storage: 21.6M × 5.4 GB = 116.6 PB/month. At $0.02/GB/month = **$2.3M/month** storage cost.

**Transcoding:** 500 hours/min = 30,000 hours/hour of video to transcode. With 2× real-time GPU transcoding, need 30,000 GPU-hours/hour = 30,000 GPUs. At $0.50/GPU-hour ≈ **$15M/month** (spot pricing can reduce to $4-5M).

**Database:** 500M users, metadata per video, analytics. Use sharded MySQL/Spanner. Estimate: **$1-2M/month**.

**Total monthly:** CDN ($54M) + Storage ($2.3M) + Transcode ($5M) + DB ($1.5M) + Servers/ networking ($3M) ≈ **$66M/month**.

**Reference:** Docs/13-capacity-planning-advanced.md
</details>
