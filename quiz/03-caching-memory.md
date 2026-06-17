# Module 3 — Caching Strategies & Memory Management — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** Cache Hit vs Miss
**Type:** Multiple Choice

What is a cache hit ratio?

A) The percentage of write operations that succeed
B) The percentage of read requests served from the cache without hitting the origin
C) The percentage of data evicted from the cache
D) The ratio of cache size to database size

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Cache hit ratio = (cache hits / total requests) × 100. A high hit ratio (>90%) indicates the cache is effective at reducing load on the origin. Low hit ratio suggests the cache size is too small, TTL is too short, or the workload is not cache-friendly.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 2 🟢
**Topic:** Cache-Aside Pattern
**Type:** Open-Ended

Describe the cache-aside (lazy loading) pattern. When is data loaded into the cache?

<details>
<summary>Answer & Explanation</summary>

**Answer:** In cache-aside (lazy loading), the application checks the cache first. On a miss, it fetches data from the database, stores it in the cache with a TTL, and returns it to the caller. Data is loaded into the cache on first read after it has been evicted or expired. On writes, the application updates the database and invalidates the cache entry.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 3 🟢
**Topic:** Redis Data Structures
**Type:** Multiple Choice

Which Redis data structure would you use to implement a real-time leaderboard?

A) Strings
B) Lists
C) Sorted Sets
D) Hashes

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Sorted Sets store members with scores and maintain order by score. They support efficient range queries (`ZRANGE`), rank lookup (`ZRANK`), and score updates (`ZINCRBY`) — all O(log n). Perfect for leaderboards.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 4 🟢
**Topic:** Cache Invalidation
**Type:** Open-Ended

What is cache invalidation and why is it difficult in distributed systems?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Cache invalidation removes or updates stale cached data when the source data changes. It's difficult because: (1) multiple application instances may have locally cached copies, (2) network partitions can cause missed invalidation messages, (3) timing windows exist between write and invalidation, (4) cascading invalidations can cause thundering herds when many cache entries expire simultaneously.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 5 🟢
**Topic:** TTL
**Type:** Multiple Choice

What does TTL (Time-To-Live) accomplish in a caching system?

A) It limits the total number of cache entries
B) It automatically removes stale data after a specified duration
C) It encrypts cache entries
D) It distributes cache entries across servers

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** TTL ensures data is evicted after a configured lifetime, preventing stale data from being served indefinitely. It acts as a safety net for data consistency. Too short TTL reduces hit ratio; too long TTL risks serving stale data.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 6 🟢
**Topic:** Write-Through Cache
**Type:** Multiple Choice

In a write-through cache, when is data written to the database?

A) Only when the cache entry is evicted
B) On every cache miss
C) Simultaneously with the cache write, on every write request
D) Asynchronously, batched every 5 seconds

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Write-through writes data to both cache and database synchronously on every write. This ensures cache-data consistency but increases write latency. It's useful when data must be immediately consistent in both cache and database.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 7 🟢
**Topic:** Eviction Policy
**Type:** Multiple Choice

Which eviction policy removes the least recently accessed items first?

A) FIFO
B) LFU
C) LRU
D) TTL

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** LRU (Least Recently Used) evicts items that haven't been accessed for the longest time. It's effective for workloads with temporal locality. LFU (Least Frequently Used) tracks access frequency. FIFO evicts in insertion order regardless of access patterns.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 8 🟢
**Topic:** CDN Caching
**Type:** Open-Ended

How does a CDN cache work? What determines whether a CDN edge server serves a cached copy or fetches from the origin?

<details>
<summary>Answer & Explanation</summary>

**Answer:** The CDN caches responses at edge servers based on Cache-Control headers from the origin (`max-age`, `s-maxage`, `private`/`public`). It serves cached content if it hasn't expired. When content expires or isn't cached, the edge sends a request to the origin (possibly with `If-None-Match` or `If-Modified-Since` for conditional revalidation). Origin can return 304 Not Modified or a fresh 200.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 9 🟡
**Topic:** Thundering Herd Problem
**Type:** Debug

A popular product page has a Redis cache entry with TTL of 60 seconds. When the TTL expires, 500 concurrent requests all hit the database simultaneously, causing a spike. What is this called and how do you prevent it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** This is the **thundering herd** problem.

**Solutions:**
1. **Mutex / lock on cache miss:** Only one request does the recomputation; others wait (or get stale data).
2. **Early re-computation (probabilistic early expiration):** Recompute before TTL expires if the request volume is near expiration time.
3. **Stale-while-revalidate:** Serve stale data while asynchronously refreshing in the background.
4. **Jitter:** Add random variance to TTLs so entries don't expire simultaneously.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 10 🟡
**Topic:** Cache Penetration
**Type:** Open-Ended

What is cache penetration? How do you prevent a flood of requests for non-existent keys (e.g., negative user IDs) from hitting the database?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Cache penetration occurs when requests for non-existent data bypass the cache (cache miss → DB miss → no cache entry created). Each request hits the database.

**Prevention:**
1. **Cache the null/empty result** with a short TTL (e.g., 60 seconds) so repeated requests don't hit the DB.
2. **Bloom filter:** Check a bloom filter before querying. If the key is definitely not in the DB, reject it immediately. No false negatives, tunable false positive rate.
3. **Rate limiting** on suspicious patterns.
4. **Request validation** at the API gateway.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 11 🟡
**Topic:** Redis Sentinel vs Cluster
**Type:** Open-Ended

Compare Redis Sentinel and Redis Cluster. When would you choose one over the other?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
- **Redis Sentinel:** Provides high availability (automatic failover) for a single Redis instance. Client connects via sentinel to discover the current master. Supports read replicas. Capacity is limited to one master's memory.
- **Redis Cluster:** Distributes data across multiple nodes (sharding) with automatic failover per shard. Supports horizontal scaling (up to ~1000 nodes). Has built-in hash slots (16384) for key distribution. Supports multi-key operations only within the same hash slot.

**Choose Sentinel** when data fits on one node and you just need HA. **Choose Cluster** when data exceeds one node's memory or you need write throughput scaling.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 12 🟡
**Topic:** Distributed Caching with Consistent Hashing
**Type:** Calculation

You have 5 cache nodes using modulo routing: `hash(key) % 5`. You need to add a 6th node. What percentage of keys are remapped? How does consistent hashing improve this?

<details>
<summary>Answer & Explanation</summary>

**Answer:** With modulo routing, adding a 6th node to 5 remaps ~(N-1)/N = 5/6 ≈ 83% of keys. With consistent hashing using v nodes (e.g., 150 per server), only ~1/m = 1/6 ≈ 17% of keys are remapped. The exact percentage varies slightly with the hash ring distribution.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 13 🟡
**Topic:** Cache Stampede
**Type:** Open-Ended

What is a cache stampede? Describe two algorithmic approaches to prevent it without requiring external locking.

<details>
<summary>Answer & Explanation</summary>

**Answer:** A cache stampede is a sudden spike of recomputation traffic when a cache entry expires and many concurrent requests detect the expiration simultaneously.

**Algorithmic approaches:**
1. **X fetch-ahead:** If TTL = T, probabilistically recompute at T - ε where ε = β × log(random()) / requests_per_second. Only a few requests early-expire.
2. **Lease (memcached-style):** On cache miss, the cache returns a "lease token." The winning request gets exclusive permission to recompute; others are told to retry or get stale data.

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 14 🟡
**Topic:** Write-Behind Cache
**Type:** Open-Ended

What is a write-behind (write-back) cache? What are the risks and how do you mitigate data loss?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Write-back cache acknowledges writes immediately and asynchronously flushes them to the database in batches. Risks: data loss if the cache node fails before flushing, data duplication if writes are flushed more than once.

**Mitigations:**
1. Persistent backing store for the cache (e.g., Redis AOF + periodic snapshots).
2. Replication of the cache itself.
3. Idempotent writes in the database so duplicates are harmless.
4. Write-ahead log on the application side before sending to cache.
5. Bounded flush window (e.g., flush every 1 second or every 100 writes).

**Reference:** Docs/03-caching-memory.md
</details>

---

## Question 15 🔴
**Topic:** Multi-Layer Cache Design
**Type:** Whiteboard

Design a multi-layer caching architecture for a news feed that has:
- 100M daily active users
- P99 read latency must be < 50ms
- Feed is personalized and changes frequently
- Viral posts can cause 100x traffic spikes

Show the layers, data flow, and how you handle cache consistency.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Layers:**
1. **L1: Client-side cache** (browser localStorage/ServiceWorker) — cache the user's last loaded feed for instant rendering.
2. **L2: CDN edge cache** — cache anonymized pre-rendered feed fragments. Use surrogate keys for granular invalidation.
3. **L3: Redis Cluster (in-memory)** — store serialized feed objects (per user, TTL 5 min). Use read-replicas per AZ. 
4. **L4: Local in-process cache** (caffeine/caffine) — store the top 100 most-read feeds globally.

**Consistency:** On new post creation, publish an invalidation event → send surrogate-key purge to CDN → async delete from Redis → local cache entries expire via TTL. Use a version vector to detect stale in-process cache.

**Traffic spike handling:** Pre-compute the feed for viral content and store it in a dedicated hot-key Redis shard with additional replicas. Use circuit breakers.

**Reference:** Docs/03-caching-memory.md, Docs/03-caching-memory-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Global Cache with Strong Consistency
**Type:** Whiteboard

Design a globally distributed cache that provides strong consistency for a stock trading platform. Writes can occur in any region. Reads must return the latest committed write with P99 < 10ms. How do you handle the conflict between consistency and latency?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **Leader-per-key:** Each stock symbol has a designated leader region. Route all writes for that symbol to the leader.
2. **Read lease:** Cache nodes hold read leases with bounded staleness (e.g., 50ms). On write, the leader sends an invalidation with a timestamp. Cache nodes must invalidate before serving reads.
3. **Hybrid logical clocks (HLC):** Every write is tagged with a timestamp. On read, the client provides its last known timestamp. The cache must serve data ≥ that timestamp, waiting if necessary.
4. **CockroachDB-style (Raft):** The cache is backed by a strongly consistent KV store. Reads go through a leaseholder for linearizability. Cross-region latency adds ~50ms, so locate leaseholders close to the region's primary trading volume.

**Reference:** Docs/03-caching-memory-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Hot Key Resolution
**Type:** Calculation

A Redis cluster has 12 shards. One key (a celebrity's profile) receives 800,000 QPS, while the max throughput per shard is 100,000 QPS. The cluster's total capacity is 1.2M QPS. Yet the hot shard is at 800% capacity while others are at 10%. Design a solution and estimate the resources needed.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Solutions:**
1. **Local cache (application-side):** Add an in-memory cache (e.g., Caffeine) in each application instance with TTL of 1-5 seconds. With 200 application instances, each handles ~4,000 QPS for this key, easily cached locally.
2. **Replicate the hot key:** Store the same hot key on every Redis shard. The application picks a random shard to read. Writes must update all copies.
3. **Read replicas:** Add dedicated Redis read replicas for hot keys.

**Calculation:** 800,000 QPS / 100,000 QPS per shard = 8 shards needed for this key alone. Using approach #2, replicate the key to 8+ shards. Total storage impact: the key's size × 8 — negligible for a profile.

**Reference:** Docs/03-caching-memory-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Cache Coherence Protocol Design
**Type:** Whiteboard

Design a write-invalidate cache coherence protocol for a distributed system with 50 application nodes and a shared Redis cluster. Guarantee that after a write, no node serves stale data for more than 100ms. Handle network partitions gracefully.

<details>
<summary>Answer & Explanation</summary>

**Answer:**

**Protocol:**
1. **Write path:** Application node writes to DB → publishes invalidation event (key + version) to a Redis Pub/Sub channel.
2. **Subscribe:** All nodes subscribe to invalidation events. On receiving an event, they evict the local cache entry.
3. **Read path:** Check local cache (TTL = 60s). On key hit, also check a version counter in Redis (using a background goroutine with 50ms tick). If local version < Redis version, evict and reload.
4. **Partition handling:** Nodes that miss Pub/Sub events will detect staleness within 50ms via version polling.

**Guarantee:** Worst-case staleness = 50ms (poll interval) + 20ms (network) + 30ms (reload) = 100ms.

**Reference:** Docs/03-caching-memory-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Scale Cache from 0 to 1B Requests
**Type:** Whiteboard

Walk through how you would evolve the caching layer of a photo-sharing app from a single Redis instance to handling 1B daily requests. Cover architecture at 3 stages: prototype, growth, and hyper-scale. What breaks at each stage?

<details>
<summary>Answer & Explanation</summary>

**Answer:**

**Stage 1 — Prototype (< 1M req/day):** Single Redis instance with cache-aside. No replication. All keys in one node. *Breaks:* Memory limit hit, single point of failure.

**Stage 2 — Growth (1M — 50M req/day):** Redis Sentinel for HA + read replicas. Add Memcached for session data (separate from content cache). Use local in-process cache for hot keys. *Breaks:* Read replica lag inconsistent, sentinel failover can cause write unavailability, memory grows but single master bottleneck.

**Stage 3 — Hyper-scale (> 50M req/day):** Redis Cluster with 32+ shards, consistent hashing, replication factor 2. Add CDN for static content. Multi-layer caching (L1 browser, L2 CDN, L3 Redis, L4 local). Implement hot-key detection and automatic replication. Use write-behind for non-critical data. *Breaks:* Cross-shard multi-key operations, resharding complexity, network bandwidth between shards, cross-region consistency.

**Reference:** Docs/03-caching-memory-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Cache Consistency for Shopping Cart
**Type:** Debug

A shopping cart service uses Redis with a TTL of 30 minutes. Users report that items sometimes disappear from their cart. Investigation reveals the issue correlates with Redis memory pressure. The eviction policy is `allkeys-lru`. What is happening and how do you fix it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Problem:** `allkeys-lru` evicts any key when memory is full, including active shopping carts. A cart TTL of 30 minutes doesn't protect against eviction — LRU sees carts as "least recently used" if the user hasn't interacted for a few minutes. Memory pressure causes carts to be evicted silently.

**Fixes:**
1. Change to `volatile-lru` — evict only keys with TTLs. Carts still can be evicted but at least keys without TTL (e.g., session locks) are protected.
2. Increase Redis `maxmemory` limit.
3. Add more Redis shards to distribute the memory load.
4. Implement a two-tier approach: a small `allkeys-lru` cache (fast, cheap) + a persistent Redis with `noeviction` for active carts.
5. Use a write-through cache pattern: persist the cart to DB on every change, use Redis as a hot cache with `volatile-lru`.

**Reference:** Docs/03-caching-memory-advanced.md
</details>
