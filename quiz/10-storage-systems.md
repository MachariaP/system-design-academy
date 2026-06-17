# Module 10 — Storage Systems & Distributed File Systems — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** Block vs File vs Object Storage
**Type:** Multiple Choice

Which storage type is most appropriate for storing static assets (images, videos) served via HTTPS at global scale?

A) Block storage (EBS, iSCSI)
B) File storage (NFS, SMB)
C) Object storage (S3, GCS)
D) Local SSD

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Object storage (S3, GCS, Azure Blob) is designed for unstructured data at massive scale. Objects are accessible via HTTP, have rich metadata, support versioning, and are replicated across data centers. Block storage is for OS volumes and databases. File storage is for shared file systems (legacy apps, home directories).

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 2 🟢
**Topic:** GFS Architecture
**Type:** Open-Ended

What are the three main components of a Google File System (GFS) cluster?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 1. **GFS Master** — manages metadata (file names, chunk locations, access control), coordinates chunk leases, and handles garbage collection. 2. **Chunkservers** — store 64 MB chunks on local disks, serve read/write requests. 3. **Clients** — interact with the master for metadata and with chunkservers for data. The master is a single point of failure mitigated by shadow masters and logging.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 3 🟢
**Topic:** Replication in Storage
**Type:** Multiple Choice

What is the primary purpose of data replication in distributed storage?

A) Reducing storage costs
B) Improving write performance
C) Providing fault tolerance and data durability
D) Enabling SQL queries

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Replication stores multiple copies of data across different nodes or data centers. If one copy is lost (disk failure, node crash, data center outage), the data is still available from another replica. Replication also improves read throughput but the primary goal is durability and availability.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 4 🟢
**Topic:** Erasure Coding vs Replication
**Type:** Multiple Choice

Which statement about erasure coding is correct?

A) Erasure coding stores 3 exact copies of data
B) Erasure coding breaks data into fragments and generates parity fragments for reconstruction
C) Erasure coding is always faster than replication for reads
D) Erasure coding requires exactly 2× storage overhead

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Erasure coding splits data into k data fragments and generates m parity fragments. Any k fragments can reconstruct the original data. This provides better storage efficiency than replication. For example, 4+2 EC uses 1.5× storage overhead and tolerates 2 failures, while 3× replication uses 3× for the same tolerance.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 5 🟢
**Topic:** Hot/Warm/Cold Storage Tiers
**Type:** Open-Ended

Describe the difference between hot, warm, and cold storage tiers.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Hot tier: high-performance (SSD/NVMe), low latency (<1ms), expensive per GB, used for frequently accessed data. Warm tier: HDD or lower-cost SSD, moderate latency (10-50ms), used for less frequently accessed data with moderate retrieval needs. Cold tier: archival media (magnetic tape, Blu-ray, Glacier), very low cost, retrieval time in minutes to hours, used for long-term backup and compliance data.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 6 🟢
**Topic:** CRUSH Algorithm
**Type:** Multiple Choice

What problem does the CRUSH (Controlled Replication Under Scalable Hashing) algorithm solve?

A) Encrypting data at rest
B) Determining where to place data replicas in a distributed storage cluster without a central metadata server
C) Compressing data before storage
D) Balancing network load across switches

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** CRUSH (used in Ceph) deterministically maps data objects to storage nodes using a pseudo-random hash function and a cluster map (hierarchical description of the physical topology — hosts, racks, rows, datacenters). It eliminates the need for a central metadata server for placement decisions. The hash depends on the object ID and cluster map, so any client can compute exactly which OSDs should store a given object.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 7 🟢
**Topic:** Bit Rot Detection
**Type:** Multiple Choice

What is "bit rot" (data degradation) and how is it commonly detected?

A) Data corruption caused by slow disk rotation speeds
B) Gradual corruption of stored data due to physical media degradation, detected via checksums
C) A virus that slowly corrupts files
D) Data loss caused by accidental deletion

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Bit rot refers to the gradual, undetected corruption of data on storage media (caused by cosmic rays, magnetic decay, NAND flash charge leakage). Detection: systems store checksums alongside data and periodically verify them by re-reading and recomputing. ZFS and Btrfs are filesystems with built-in checksumming. Object stores like S3 provide checksums (MD5 ETag) and automatically detect bit rot.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 8 🟢
**Topic:** Concurrent Append
**Type:** Open-Ended

What is a "concurrent append" operation in a distributed storage system and why is it challenging?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Concurrent append allows multiple clients to append data to the same file/stream simultaneously without coordinating with each other. It's challenging because: (1) multiple writers trying to write to the same location creates race conditions, (2) the system must ensure each append appears exactly once and atomically (no partial writes), (3) ordering of appends from different clients is non-deterministic. GFS addressed this with a lease-based primary replicas approach where the primary serializes concurrent appends.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 9 🟡
**Topic:** GFS Read/Write Flow
**Type:** Open-Ended

Describe the read and write data flow in GFS. Why does the client send data to the nearest replica for writes?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Read:** Client asks the master for chunk locations → master returns primary and secondary chunk locations → client reads from the nearest replica (to minimize network hops).

**Write:** Client asks the master for the primary chunk server → master grants a lease to one primary → client sends data to all replicas (the data is pushed along a chain to maximize network utilization) → once all replicas acknowledge, the client sends a write request to the primary → primary assigns a serial number and applies the write → primary forwards to secondaries → secondaries apply and acknowledge → primary responds to the client.

Data is pushed to the nearest replica first, then propagated in a chain, to pipeline the data transfer and avoid the client being a bottleneck for multiple copies.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 10 🟡
**Topic:** Erasure Coding Overhead Calculation
**Type:** Calculation

A storage system uses 6+3 erasure coding (6 data fragments, 3 parity fragments). If a 12 MB file is stored:
1. What is the total storage consumed?
2. How many fragment failures can be tolerated?
3. What is the storage overhead compared to the original file?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. Each fragment = 12 MB / 6 = 2 MB. Total fragments = 6 + 3 = 9. Total storage = 9 × 2 MB = 18 MB.
2. Up to 3 failures tolerated (any 3 of 9 fragments can be lost and the file is still reconstructable from the remaining 6).
3. Overhead = 18 MB / 12 MB = 1.5× (50% overhead). Compare to 3× replication = 300% overhead for the same 3-failure tolerance.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 11 🟡
**Topic:** CRUSH Map Hierarchy
**Type:** Open-Ended

How does CRUSH use the cluster hierarchy (buckets: host, rack, row, datacenter) to improve fault tolerance?

<details>
<summary>Answer & Explanation</summary>

**Answer:** CRUSH's hierarchical bucket types represent the physical topology. When placing replicas, CRUSH takes the hierarchy into account: it tries to place each replica in a different failure domain. For example, with 3 replicas, CRUSH can place one on each of 3 different racks (failure domain = rack). This ensures that if an entire rack loses power, only one replica of each piece of data is affected — the other two are on other racks. Without hierarchy awareness, replicas might all end up in the same rack.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 12 🟡
**Topic:** GFS Master Failure
**Type:** Debug

A GFS cluster's master process crashes. Operations stop. After restart, the master must recover its metadata. Where does GFS persist metadata and what happens to the chunk location information?

<details>
<summary>Answer & Explanation</summary>

**Answer:** GFS persists metadata (file names, directory structure, access control lists) in an **operation log** on the master's local disk AND on replicated shadow masters. The chunk location information is **NOT persisted** — the master collects it at startup by polling all chunkservers for their current chunk inventory. This design avoids the complexity of keeping chunk location data consistent because chunkservers are the authoritative source of their own chunk lists. Startup time depends on the number of chunkservers and chunks.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 13 🟡
**Topic:** Object Storage vs POSIX File System
**Type:** Open-Ended

Why is object storage (S3) considered "eventually consistent" by default for overwrites and deletes? When did it achieve strong consistency?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Object storage is eventually consistent for overwrites and deletes because of the underlying replication architecture. When an object is overwritten or deleted, the change must propagate to all replicas. A read that hits a replica that hasn't received the update yet will see the old version or still see the deleted object. List operations (listing bucket contents) also exhibit eventual consistency. 

AWS S3 announced **strong read-after-write consistency** for all GET, PUT, LIST operations in December 2020, achieved by changes to the internal metadata management. However, many on-premises object stores (Ceph RGW, MinIO) may still have eventual consistency configurations.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 14 🟡
**Topic:** Storage Tier Auto-Migration
**Type:** Multiple Choice

What mechanism automatically moves data between hot, warm, and cold storage tiers based on access patterns?

A) RAID striping
B) Lifecycle policies
C) LVM snapshots
D) Inode allocation

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Lifecycle policies (e.g., S3 Lifecycle, Azure Blob Storage lifecycle management) automatically transition objects between tiers based on age or last-access time. For example: move to infrequent access after 30 days, move to Glacier after 90 days, delete after 365 days. Some systems also use access-frequency tracking for automatic tiering.

**Reference:** Docs/10-storage-systems.md
</details>

---

## Question 15 🔴
**Topic:** Distributed File System Design — Facebook Haystack
**Type:** Whiteboard

Design a photo storage system for 1 trillion photos with an average size of 350 KB. Reads are 100× more frequent than writes. The system must serve reads in under 100ms for 99th percentile. Discuss how you'd approach metadata overhead (millions of files on a traditional filesystem), and why a custom approach is needed.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Problem:** 1 trillion × 350 KB = ~350 PB. A traditional filesystem with separate inodes for each file would consume significant memory for metadata and struggle with directory enumeration.

**Haystack-style approach:**
1. **Append-only "needle" store:** Aggregate millions of photos into large files (e.g., 100 GB files called "volumes"). Each photo is a "needle" — a fixed-size header + photo data + footer — appended sequentially to the volume.
2. **In-memory index:** Each volume has an in-memory mapping of photo ID → (offset, size, flags). This is loaded at startup from a compact index file. For 1 trillion photos, with ~30 bytes of index per photo, the index is ~30 TB — partitioned across machines.
3. **Write flow:** Store writes append a needle to the current volume. The volume's index is updated in memory and periodically flushed.
4. **Read flow:** Client sends photo ID → application server → lookup machine finds (volume, offset, size) → storage machine reads from the volume at the given offset — a single seek + read.
5. **Caching:** Cache the most popular 1% of photos in memory (hot cache), use CDN for the rest.

This design avoids filesystem metadata overhead for billions of small files and enables O(1) reads.

**Reference:** Docs/10-storage-systems-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Concurrent Append Race Condition
**Type:** Debug

GFS supports concurrent appends to the same file from multiple clients. A team observes that some records appended to the same file are duplicated. The company's analytics pipeline reads these files and counts the records, producing inflated numbers. What causes duplication in GFS appends and how would you fix the downstream analytics?

<details>
<summary>Answer & Explanation</summary>

**Answer:** **Cause:** In GFS, concurrent appends from multiple clients are serialized by the primary replica. However, if a replica (primary or secondary) crashes between applying the write and acknowledging it, the client retries. The retried append succeeds on the new primary or after recovery. The data is written twice — once by the original attempt (now at some offset) and once by the retry. Additionally, GFS may insert padding or leave undefined regions if record boundaries don't align with 64 MB chunk boundaries, leading to duplicates or partial records.

**Fix for downstream analytics:**
1. Add a unique ID (UUID or monotonically incrementing sequence number) to each record before appending. The analytics pipeline deduplicates by ignoring records with the same ID.
2. Use record-level checksums and skip records that are duplicates (same content within a time window).
3. Alternatively, switch to a deterministic append approach: use a single writer for a given file, or use a system with exactly-once append semantics (e.g., Kafka with idempotent producer).

**Reference:** Docs/10-storage-systems-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Erasure Coding vs Replication — Cost-Latency Trade-off
**Type:** Calculation

A storage cluster stores 10 PB of data. Compare the total raw storage cost, reconstruction time, and read latency for 3× replication vs 10+4 erasure coding with 1 TB disks:
1. Total disks needed (assuming 10 PB usable, 1 TB per disk)
2. How many concurrent disk failures can survive?
3. Why might 3× replication be preferred over EC for latency-sensitive workloads?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **3× replication:** 10 PB × 3 = 30 PB raw storage = 30,000 × 1 TB disks. **10+4 EC:** 10 PB × (14/10) = 14 PB raw = 14,000 × 1 TB disks. EC saves 16,000 disks.

2. **3× replication:** Survives 2 concurrent failures per replication group (if the 3rd fails, data is lost). **10+4 EC:** Survives any 4 concurrent failures across the entire EC stripe.

3. **Why replication for latency-sensitive workloads:**
   - **Reads:** Replication serves reads from the nearest replica (low latency). EC reads require reading k fragments and reconstructing — which means k network transfers plus CPU for reconstruction. For a 10+4 scheme, reading a 10 MB object requires reading all 10 MB (k fragments) from potentially 10 different nodes, while replication reads from one node.
   - **Write latency:** Replication writes to 3 replicas in parallel. EC writes to 14 nodes (10 data + 4 parity), requiring more coordination.
   - **CPU overhead:** EC reconstruction is CPU-intensive. A cluster doing many reads of cold data (requiring reconstruction) can become CPU-bound.

**Reference:** Docs/10-storage-systems-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Ceph CRUSH Data Placement Optimization
**Type:** Whiteboard

Design a CRUSH map hierarchy for a Ceph cluster with 300 OSDs across 30 servers (10 OSDs each), 3 racks (10 servers each), 2 data centers. The system must survive a full data center failure while ensuring cross-DC traffic for writes is minimized. Define failure domains and describe how CRUSH bucket weights are configured.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**CRUSH Hierarchy (from top to bottom):**
```
root=global
  datacenter=dc1
    rack=dc1-rack1
      host=dc1-rack1-host1   (weight = 10.0 — 10 × 1 TB OSDs)
      host=dc1-rack1-host2
      ... (10 hosts)
    rack=dc1-rack2
      ...
    rack=dc1-rack3
      ...
  datacenter=dc2
    rack=dc2-rack1
      host=dc2-rack1-host1
      ... (15 hosts in dc2)
    rack=dc2-rack2
      ...
```

**Pool configuration (3 replicas, survival of DC failure):**
Set `crush-failure-domain = datacenter`. With 2 DCs, 3 replicas can't all be in different DCs, so set `crush-failure-domain = rack` and use a **CRUSH rule** that tries to place 2 replicas in dc1 and 1 in dc2 (or 1-1-1 across three DCs if a third DC exists).

**Weight configuration:**
Each OSD has weight = its capacity in TB. Each host sums its OSD weights. Each rack sums its host weights. Each DC sums its rack weights. Data placement is proportional to weights.

**Cross-DC traffic minimization:**
For replicated pools, accept that at least one replica will be cross-DC. For EC pools, configure the CRUSH rule to use `min_size` per failure domain to reduce cross-DC data flow. Use a **locality group** — the primary copy is always local, only replicas cross DC.

**Reference:** Docs/10-storage-systems-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Bit Rot Detection and Repair Pipeline
**Type:** Whiteboard

Design a background scrubber for a distributed storage system that detects and repairs bit rot across 100,000 disks. The system must verify every byte at least once every 30 days without impacting production I/O more than 10%. How do you prioritize which data to scrub, handle checksum verification, and trigger repair?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Architecture:**
1. **Checksum storage:** Each 4 KB data block has a 32-byte checksum (SHA-256) stored alongside (in metadata or a separate checksum file). Larger objects have a Merkle tree of block checksums.
2. **Scrub scheduling:** Divide the total disk capacity by 30 days → scrub rate = (total_data / 30 days) per day. Use an I/O scheduler that limits scrub reads to 10% of available bandwidth (e.g., if disks can do 200 MB/s, limit scrub to 20 MB/s per disk).
3. **Priority ordering:**
   - **Priority 1:** Recently written data (scrub within 24h) — catch early failures.
   - **Priority 2:** Data read frequently — opportunistic scrub (piggyback on production reads to verify checksum).
   - **Priority 3:** Data not read in last 30 days — deep scrub.
4. **Detection:** Scrubber reads a block, recomputes its checksum, compares to stored checksum. If mismatch → mark as suspect. If replication factor > 1, read another replica — if good, overwrite the bad replica (self-heal). If all replicas are bad, restore from backup.
5. **Repair:** For replicated data, overwrite the bad replica with a good copy. For EC data, reconstruct the bad fragment using k other fragments.

**Performance isolation:** Use cgroups/io-throttle to limit scrub I/O. Run scrubs during low-traffic windows (overnight) for full scans, opportunistic during peak.

**Reference:** Docs/10-storage-systems-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Comparing GFS, HDFS, and Ceph
**Type:** Open-Ended

Compare GFS, HDFS, and Ceph in terms of metadata management, data placement, and consistency guarantees. Under what scenario would each be the best choice?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
| Feature | GFS | HDFS | Ceph |
|---|---|---|---|
| **Metadata** | Single master (w/ shadow) | Single NameNode (w/ standby) | Distributed (CRUSH-based, no single metadata server for data placement, but has MONs + MDS for filesystem metadata) |
| **Data placement** | Master assigns chunks to chunkservers. Forward | NameNode manages block locations. Forward. | CRUSH hash computes location. No central mapping |
| **Consistency** | Relaxed (concurrent append may duplicate) | Write-once-read-many, single writer | Strong for RADOS, POSIX via MDS |
| **Atomic append** | Yes (at-least-once, may duplicate) | No (no concurrent writers) | Yes via RADOS (atomic) |

**Best choice scenarios:**
- **GFS:** Large sequential reads/writes (MapReduce, batch processing). Relaxed consistency useful for append-heavy pipelines.
- **HDFS:** Batch analytics (Hadoop/Spark ecosystem). Simpler model (write-once) fits ETL pipelines well. Mature ecosystem.
- **Ceph:** General-purpose storage needing POSIX, block, and object interfaces from the same cluster. Best for cloud-native (Rook on Kubernetes). CRUSH eliminates metadata SPOF.

**Reference:** Docs/10-storage-systems-advanced.md
</details>
