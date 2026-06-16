# File, Object & Block Storage – A Beginner's Guide

> This guide explains the three fundamental ways computers store data — block, file, and object storage — and when to use each one.
> Every technical term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand these foundations, the original advanced module will feel like a natural next step.

---

## Table of Contents

1. [The Three Storage Paradigms](#1-the-three-storage-paradigms)
2. [Block Storage: The Numbered Lockers](#2-block-storage-the-numbered-lockers)
3. [File Storage: The Library with a Librarian](#3-file-storage-the-library-with-a-librarian)
4. [Object Storage: The Barcode Warehouse](#4-object-storage-the-barcode-warehouse)
5. [Which One Should You Pick?](#5-which-one-should-you-pick)
6. [Consistent Hashing: Distributing Data Evenly](#6-consistent-hashing-distributing-data-evenly)
7. [Erasure Coding: Save Space, Survive Failures](#7-erasure-coding-save-space-survive-failures)
8. [Bit Rot: Data Decays Over Time](#8-bit-rot-data-decays-over-time)
9. [Common Disasters and How to Avoid Them](#9-common-disasters-and-how-to-avoid-them)
10. [Putting It All Together — A Photo App's Storage Strategy](#10-putting-it-all-together--a-photo-apps-storage-strategy)
11. [Glossary of Technical Terms](#11-glossary-of-technical-terms)
12. [Key Takeaways](#12-key-takeaways)

---

## 1. The Three Storage Paradigms

Imagine you need to organize a large collection of items. You have three options:

| Type | Analogy | Best for |
|------|---------|----------|
| **Block storage** | Numbered lockers — fast access, but you need to know the exact locker number | Databases, high-performance applications |
| **File storage** | Library with a catalog and a librarian — hierarchical folders, shared access | Shared files, home directories, media editing |
| **Object storage** | Warehouse with barcodes — flat, massive scale, accessible via HTTP | Backups, data lakes, static web assets |

Each type has a different trade-off between speed, scalability, and cost. The right choice depends on what you are storing and how you access it.

---

## 2. Block Storage: The Numbered Lockers

Block storage is the closest to how physical hard drives work. The storage is divided into **blocks** (chunks of raw bytes, typically 512 bytes to 4 KB). Each block has an address, and the operating system reads and writes blocks by their address.

**Analogy:** A wall of numbered lockers. You open locker #42, put stuff in, close it. Fast, simple, and you can access any locker directly. But you must know the exact locker number — there is no "search by content."

**Real-world examples:** AWS EBS (Elastic Block Store), iSCSI drives, local SSDs.

**Pros:**
- Extremely fast for random reads and writes.
- Low latency (microseconds to milliseconds).

**Cons:**
- Cannot be easily shared between multiple servers (one server at a time).
- Limited size (a single volume can only be so large).

**Used by:** Databases like PostgreSQL and MySQL. They need fast, low-latency access to specific blocks.

---

## 3. File Storage: The Library with a Librarian

File storage adds a **metadata server** that keeps track of a directory tree — folders, filenames, permissions, and which blocks belong to which file.

**Analogy:** A library with a Dewey Decimal System and a librarian. You say, "I need the book in `/science/physics/quantum.txt`". The librarian looks up the catalog, finds which shelf the book is on, and retrieves it. You never need to know the exact shelf number.

**Real-world examples:** NFS (Network File System), SMB/CIFS (Windows file sharing), AWS EFS (Elastic File System).

**Pros:**
- Hierarchical, human-friendly organization.
- Can be mounted and accessed by many servers simultaneously.
- Familiar interface (files and folders).

**Cons:**
- The metadata server can become a bottleneck at massive scale.
- Slower than block storage because every operation goes through the file system layer.

**Used by:** Shared home directories, media editing teams, analytics datasets.

---

## 4. Object Storage: The Barcode Warehouse

Object storage strips away the folder hierarchy entirely. There are no directories — just a flat pool of **objects**. Each object has a unique key (like a barcode), the data (the bytes), and metadata (tags and attributes). You access objects via HTTP (REST API).

**Analogy:** A warehouse where every item gets a unique barcode. To find something, you do not browse shelves — you scan the barcode, and the system uses a lookup map (consistent hashing) to figure out which aisle contains it.

**Real-world examples:** AWS S3, Azure Blob Storage, Google Cloud Storage.

**Pros:**
- Exabyte-scale — limited only by total cluster capacity.
- Accessible via HTTP from anywhere.
- Cheaper than block or file storage for bulk data.

**Cons:**
- Cannot modify a single byte — you must rewrite the entire object.
- Higher latency than block storage (tens to hundreds of milliseconds).

**Used by:** Backups, data lakes, static websites, user-uploaded content (photos, videos).

---

## 5. Which One Should You Pick?

Here is a simple decision tree:

1. **Is sub-millisecond latency critical?** → **Block Storage** (databases, trading systems)
2. **Do you need shared access with folders?** → **File Storage** (team files, home directories)
3. **Is massive scale or geo-distribution needed?** → **Object Storage** (data lakes, backups, media)
4. **On a budget and accessing sequentially?** → **Object Storage** (archives, logs)

**Real-world example:** A photo-sharing app uses **all three**:
- PostgreSQL runs on **block storage** (needs fast, random reads/writes).
- The team shares analytics CSVs over **file storage** (shared access).
- User-uploaded photos go to **object storage** (massive scale, accessed via URL).

---

## 6. Consistent Hashing: Distributing Data Evenly

When you have many storage servers, you need to decide which server stores which data. The simplest approach would be: `server = hash(key) % N`. But if you add a server (N becomes N+1), almost every key maps to a new server — you would have to move almost all your data.

**Consistent hashing** solves this. Imagine a ring (circle) with many points. Both servers and data keys are placed on this ring. A key belongs to the first server you encounter going clockwise.

- When you **add a server**, it appears on the ring and takes over only the keys in its small arc. Most keys stay where they were.
- When you **remove a server**, only its keys need to be redistributed.

**Virtual nodes:** Each physical server gets many small points on the ring (e.g., 128 virtual nodes). This ensures even load distribution, especially when servers have different capacities (stronger servers get more virtual nodes).

---

## 7. Erasure Coding: Save Space, Survive Failures

To protect against disk failures, you could store 3 copies of every piece of data (3x replication). That uses 3x the storage space. **Erasure coding** achieves the same protection with far less overhead.

**How it works:** Split the data into `k` chunks. Then compute `m` additional parity chunks using math. You can lose up to `m` chunks and still reconstruct the original data from the remaining `k` chunks.

**Analogy:** "In case I lose this page, here are 4 clues to reconstruct it" — you only need some of the clues, not all of them.

**Example:** 4+2 erasure coding (k=4, m=2):
- Split a file into 4 data chunks.
- Compute 2 parity chunks (total 6 chunks, stored on 6 different servers).
- You can lose any 2 servers and still recover the file.
- Overhead: only 50% (6/4 = 1.5x), compared to 200% for 3x replication.

| Method | Overhead | Can Lose |
|--------|----------|----------|
| 3x replication | 200% | 2 copies |
| 4+2 erasure coding | 50% | 2 chunks |
| 8+3 erasure coding | 37.5% | 3 chunks |

**Trade-off:** Erasure coding uses more CPU (to compute parity) and is slower for recovery than simple replication. Use replication for hot (frequently accessed) data, erasure coding for cold (archival) data.

---

## 8. Bit Rot: Data Decays Over Time

**Bit rot** (also called data degradation) is the gradual corruption of data on storage media. Bits can flip spontaneously due to cosmic rays, manufacturing defects, or simple wear over time. While the probability is low (about 1 in 10^15 bits read for enterprise drives), at petabyte scale, it becomes a daily occurrence.

Storage systems protect against bit rot by:
- **Checksums:** Every chunk of data has a checksum stored separately. When the data is read, the system recomputes the checksum and compares it. If they do not match, the data is corrupted.
- **Background scrubbing:** The system periodically reads all data, checks the checksums, and repairs any corruption using the redundant copies or erasure coding parity.
- **Self-healing:** When corruption is detected, the corrupted chunk is replaced with a fresh copy reconstructed from the remaining data.

AWS S3, for example, does this automatically. If you store a file and retrieve it years later, S3 will detect and repair any bit rot during the background scrub, returning your data intact.

---

## 9. Common Disasters and How to Avoid Them

### Choosing the Wrong Storage Type

Using file storage for a database will be slow (the metadata server becomes a bottleneck). Using object storage for a database will be impossible (no random byte-level writes).

**Mitigation:** Match the storage type to the access pattern: block for low-latency random I/O, file for shared hierarchical access, object for massive-scale sequential access.

### Hot-Spotting in Object Storage

A single popular object (or prefix) gets so much traffic that its storage nodes are overwhelmed. For example, Docker Hub experienced this when a popular container image was pulled millions of times per day, overloading the nodes storing that specific image.

**Mitigation:** Spread hot objects across more nodes (increase replication), use caching (CDN), add rate limiting, or split the hot key into sub-keys.

### Metadata Server Overload

In a file storage system, the metadata server knows where every file is. If you create 10 billion small files, the metadata server needs enough RAM to hold all those entries. This can easily exceed the server's capacity.

**Mitigation:** Object storage avoids this by using a flat namespace and consistent hashing — there is no central metadata server.

### Recovery Bandwidth Saturation

When a disk fails, the system must rebuild the data on replacement disks. If the failed disk held 600 GB of data and the network can transfer 100 MB/s, the rebuild takes 100 minutes. During that time, the system is more vulnerable to additional failures.

**Mitigation:** Spread data across many disks (smaller recovery per failure), prioritize recovering the most critical data first, and ensure sufficient spare network capacity.

---

## 10. Putting It All Together — A Photo App's Storage Strategy

Let's design the storage for a photo-sharing app with 100 million users:

1. **PostgreSQL database** (user accounts, metadata, comments) → **Block Storage** (AWS EBS). Needs fast, low-latency random I/O for updates and joins.

2. **Uploaded photos** → **Object Storage** (AWS S3). Each photo is 2-10 MB, written once, read many times, accessed via HTTP URLs. Needs to scale to billions of objects. Enables erasure coding (8+3) for cost-effective durability.

3. **CDN caching** (CloudFront) for the most popular photos → Sits in front of S3 to serve popular images from edge locations, reducing load on S3 and latency for users.

4. **Shared analytics files** for the data science team → **File Storage** (AWS EFS). Multiple data scientists mount the same file system to share CSV exports and Jupyter notebooks.

5. **Cold storage for old photos** → Photos older than 1 year move to **S3 Glacier** (deep archive object storage). Cheaper but takes minutes to retrieve.

6. **Bit rot protection** → S3 automatically checksums every object, scrubs for corruption, and repairs using erasure coding parity.

A single application, using all three storage types, each chosen for its specific job.

---

## 11. Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **Bit Rot** | Gradual data corruption over time due to media degradation or cosmic rays. |
| **Block Storage** | Raw storage divided into fixed-size blocks, addressed by block number. |
| **Checksum** | A small computed value attached to data to detect corruption. |
| **Consistent Hashing** | A distribution technique where adding/removing servers moves only a fraction of the data. |
| **Erasure Coding** | A method of splitting data into chunks with parity, allowing recovery from partial loss. |
| **File Storage** | Hierarchical storage with directories, filenames, and a metadata server. |
| **Hot Data** | Frequently accessed data that should be stored on fast, expensive media. |
| **Metadata** | Data about data — filenames, sizes, permissions, locations. |
| **Object Storage** | Flat, key-value storage with HTTP access, designed for massive scale. |
| **Parity** | Redundant data computed from the original data, used for recovery. |
| **Replication** | Keeping multiple copies of data on separate servers for durability. |
| **Scrubbing** | Periodically reading all data to detect and repair bit rot. |
| **Virtual Node (vnode)** | In consistent hashing, many small ring positions assigned to one physical node for even load distribution. |

---

## 12. Key Takeaways

1. **Block, file, and object storage optimize different axes:** block = speed, file = hierarchy, object = scale.
2. **Choose storage based on access pattern:** random I/O → block, shared hierarchical → file, massive sequential → object.
3. **Most real-world systems use all three** for different workloads.
4. **Consistent hashing enables horizontal scaling** of storage — adding nodes moves only a fraction of the data.
5. **Virtual nodes ensure even distribution** even when servers have different capacities.
6. **Erasure coding saves 60-80% storage cost** compared to 3x replication, at the cost of more CPU.
7. **Use replication for hot data, erasure coding for cold data.**
8. **Bit rot is inevitable at scale.** Always use checksums and background scrubbing.
9. **The metadata server is the bottleneck in file storage.** Object storage avoids this by using a flat namespace.
10. **Recovery bandwidth is a first-class operational concern.** A failed disk means hours of reduced redundancy.
11. **Hybrid strategies win:** replicate frequently accessed data, erasure-code archives.

---

> This guide explains the "why" behind the three storage paradigms.
> Once you're comfortable with these concepts, the original module (with its erasure coding simulator code, consistent hashing worked examples, and S3 internals) will serve as your in-depth reference.
> Remember: storage is not a commodity — the wrong choice can cost an order of magnitude more in performance or money.
