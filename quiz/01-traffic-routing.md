# Module 1 — Traffic Routing & Network Foundations — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** DNS Resolution
**Type:** Multiple Choice

What happens first when a user types `https://www.example.com` into a browser?

A) The browser sends an HTTP request to the server's IP address
B) The browser queries a DNS resolver to resolve the domain to an IP address
C) The browser establishes a TCP connection to `www.example.com`
D) The browser checks its cache for a previous response

<details>
<summary>Answer & Explanation</summary>

**Answer:** B (with D happening first if a cached record exists).

**Explanation:** DNS resolution is the first network step. The browser checks its local cache, then the OS cache, then queries a recursive DNS resolver. Only after obtaining the IP address does it establish a TCP connection and send HTTP requests.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 2 🟢
**Topic:** Load Balancer Algorithms
**Type:** Multiple Choice

Which load-balancing algorithm sends each request to the server with the fewest active connections?

A) Round Robin
B) Least Connections
C) IP Hash
D) Weighted Round Robin

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Least Connections routes traffic to the server currently handling the fewest active connections. Round Robin cycles through a list regardless of load. IP Hash uses the client IP for consistent routing. Weighted Round Robin assigns proportional traffic based on server capacity.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 3 🟢
**Topic:** HTTP vs HTTPS
**Type:** Open-Ended

Explain the difference between HTTP and HTTPS. What does TLS provide that HTTP alone lacks?

<details>
<summary>Answer & Explanation</summary>

**Answer:** HTTP transmits data in plaintext. HTTPS adds TLS encryption on top of HTTP, providing confidentiality (encryption), integrity (tamper detection via MAC), and authentication (server certificate verification via a CA).

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 4 🟢
**Topic:** TCP Three-Way Handshake
**Type:** Multiple Choice

What are the three steps of the TCP three-way handshake?

A) SYN → SYN-ACK → ACK
B) SYN → ACK → SYN-ACK
C) ACK → SYN → SYN-ACK
D) SYN → SYN → ACK

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** The client sends a SYN (synchronize) packet. The server responds with SYN-ACK. The client sends ACK. This establishes a reliable connection before data transfer begins.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 5 🟢
**Topic:** Anycast Routing
**Type:** Open-Ended

What is Anycast and how does it improve latency and availability for global services?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Anycast routes traffic to the nearest (topologically closest) server among a group sharing the same IP address. BGP announces the same IP prefix from multiple locations. Packets flow to the closest announced prefix. This reduces latency and provides automatic failover: if one location goes down, BGP withdraws its route and traffic shifts to the next closest.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 6 🟢
**Topic:** Reverse Proxy
**Type:** Multiple Choice

Which of the following is NOT a typical function of a reverse proxy?

A) Load balancing
B) SSL termination
C) Client IP address masking
D) Serving as an authoritative DNS server

<details>
<summary>Answer & Explanation</summary>

**Answer:** D

**Explanation:** A reverse proxy handles load balancing, SSL termination, caching, and hides backend server details. DNS server functionality is unrelated.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 7 🟢
**Topic:** Connection Pooling
**Type:** Open-Ended

Why do backend services use connection pooling when talking to a database?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Opening a TCP connection has overhead (handshake, TLS negotiation). Connection pooling reuses a set of pre-established connections, reducing latency and server resource usage (CPU, memory per socket). It also limits the number of concurrent connections to the database to avoid overwhelming it.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 8 🟢
**Topic:** CDN
**Type:** Multiple Choice

What is the primary purpose of a Content Delivery Network (CDN)?

A) Encrypting traffic between client and server
B) Caching static and dynamic content at edge locations close to users
C) Balancing database read replicas
D) Monitoring server health

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** A CDN caches content (HTML, CSS, JS, images, video) at geographically distributed edge servers. This reduces latency, offloads origin servers, and improves availability. It can also accelerate dynamic content via optimized routing.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 9 🟡
**Topic:** BGP Routing
**Type:** Open-Ended

Explain how BGP works at a high level and why it is considered the "glue" of the internet. What happens when a BGP router receives conflicting route advertisements for the same IP prefix?

<details>
<summary>Answer & Explanation</summary>

**Answer:** BGP (Border Gateway Protocol) exchanges routing and reachability information between autonomous systems (AS). Each AS advertises IP prefixes to neighbors. Path selection uses the shortest AS-path, lowest MED, and local preference.

When conflicting advertisements arrive, BGP applies tie-breaking rules: highest local preference, shortest AS-path, lowest origin type, lowest MED, eBGP over iBGP, lowest IGP metric, and finally the router ID.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 10 🟡
**Topic:** Load Balancer Stickiness
**Type:** Open-Ended

What is session stickiness (persistent sessions) in a load balancer? When is it necessary and what are its downsides?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Stickiness routes all requests from a client to the same backend server, typically via a cookie or client IP hash. Necessary when session state is stored in-memory on the server (e.g., a购物 cart without an external session store). Downsides: reduces load-balancing effectiveness, causes uneven load distribution, and creates availability coupling — a server failure loses all its sticky sessions.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 11 🟡
**Topic:** TLS Handshake
**Type:** Multiple Choice

During a TLS 1.3 handshake, how many round trips are needed before encrypted data can be sent?

A) 0 (0-RTT)
B) 1 (1-RTT)
C) 2 (2-RTT)
D) 3 (3-RTT)

<details>
<summary>Answer & Explanation</summary>

**Answer:** B — 1 round trip for a full handshake. TLS 1.3 also supports 0-RTT for resumed sessions.

**Explanation:** TLS 1.3 reduced the handshake from 2 round trips (TLS 1.2) to 1. The client sends a ClientHello with key-share. The server responds with ServerHello, finished, and encrypted data all in one flight.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 12 🟡
**Topic:** Health Checks
**Type:** Open-Ended

Describe the difference between passive and active health checks in a load balancer. When would you prefer one over the other?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Active health checks proactively probe backend endpoints at a fixed interval (e.g., GET /health). Passive health checks monitor real traffic — if a server returns 5xx for N consecutive requests, it is marked unhealthy.

Prefer active for critical services where early detection is needed; prefer passive for high-throughput systems where probes add overhead or where health endpoints may not be representative.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 13 🟡
**Topic:** OSI Model Layer 4 vs Layer 7
**Type:** Multiple Choice

Which statement about Layer 4 vs Layer 7 load balancing is correct?

A) Layer 4 load balancers can inspect HTTP headers
B) Layer 7 load balancers operate on individual TCP connections without reading payloads
C) Layer 7 load balancers can route based on URL path, headers, and cookies
D) Layer 4 load balancers require TLS termination to function

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** Layer 7 (Application Layer) load balancers can inspect HTTP/HTTPS payloads and route based on URL, headers, cookies, or request body. Layer 4 (Transport Layer) operates at the TCP/UDP level, forwarding connections based on IP and port without inspecting payloads.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 14 🟡
**Topic:** QUIC / HTTP/3
**Type:** Open-Ended

What problem does QUIC solve compared to TCP+TLS? Why is HTTP/3 built on QUIC?

<details>
<summary>Answer & Explanation</summary>

**Answer:** QUIC replaces TCP+TLS with a single transport-layer protocol built on UDP. It eliminates head-of-line blocking (TCP HOL blocking where a lost packet blocks all subsequent streams), reduces connection establishment to 0-RTT for resumed sessions, handles connection migration natively (client IP changes don't break connections), and encrypts more of the transport metadata. HTTP/3 maps HTTP semantics onto QUIC streams.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 15 🟡
**Topic:** Consistent Hashing in Load Balancers
**Type:** Open-Ended

How does consistent hashing work in a load balancer context and why is it useful for caching layers?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Consistent hashing maps both servers and request keys onto a hash ring. Each key is assigned to the next server clockwise on the ring. When servers are added or removed, only N/m keys are remapped (where N = total keys, m = total servers). This minimizes cache invalidation compared to simple modulo hashing, which would remap almost all keys.

**Reference:** Docs/01-traffic-routing.md
</details>

---

## Question 16 🔴
**Topic:** TCP Congestion Control Debug
**Type:** Debug

A team observes that their service's throughput plateaus at ~200 Mbps even though the network link supports 10 Gbps and CPU/memory are idle. They notice the connection RTT is 200 ms and the TCP window size stays small. What is likely happening? How would you fix it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** The TCP window size is likely too small, limiting the Bandwidth-Delay Product (BDP). BDP = 10 Gbps × 0.2 s = ~250 MB. If the TCP receive window is 64 KB (default on some OS configurations), throughput is capped at 64 KB / 0.2 s = 3.2 Mbps.

**Fix:** Enable TCP window scaling (RFC 1323) and increase the socket buffer sizes (`tcp_rmem`, `tcp_wmem` on Linux). Use auto-tuning. Consider switching to a protocol like QUIC or using multiple parallel connections.

**Reference:** Docs/01-traffic-routing.md, Docs/01-traffic-routing-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Global Traffic Manager Design
**Type:** Whiteboard

Design a global traffic management system for a video streaming platform that spans 5 AWS regions. Traffic must be routed to the nearest healthy region. If a region fails, traffic must shift with < 30 second propagation delay. How would you implement health probing, DNS-based routing, and failover?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Use a GTM (Global Traffic Manager) combining:
1. **DNS-based routing:** Route53 or equivalent with latency-based or geo-proximity routing, low TTL (60s) for fast propagation.
2. **Health probing:** Active health checks from each region's load balancer plus cross-region synthetic probes (measure real end-to-end streaming). 3. **BGP anycast** for the ingest endpoints. 4. **Failover:** Health status → configuration updates → DNS record changes. Use a health-score aggregator with hysteresis (N of M probes, 3 strikes) to avoid flapping. 5. **Pre-warming:** On failover, direct traffic gradually via weighted records to avoid thundering herd on the recovery region.

**Reference:** Docs/01-traffic-routing-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Anycast vs DNS Load Balancing
**Type:** Whiteboard

Compare Anycast and DNS-based global load balancing. For a real-time multiplayer game requiring sub-50ms pings globally, which would you choose and why? Provide a rough design with traffic flow.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Anycast is preferred for ultra-low-latency real-time traffic because BGP converges faster than DNS TTL propagation and doesn't depend on client DNS caching behavior. Design: Deploy game server clusters in 6-8 global locations, announce the same IP prefix via BGP from each. Use BGP communities and AS-path prepending for traffic engineering. For connection-oriented games, use Anycast for the connection-establishment phase, then redirect to a regional unicast IP for the session to avoid routing asymmetry during the session.

**Reference:** Docs/01-traffic-routing-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Multi-Region Active-Active Architecture
**Type:** Whiteboard

Design an active-active multi-region API architecture with a global load balancer. Discuss:
1. How do you handle read-after-write consistency?
2. How do you prevent thundering herd during failover?
3. What DNS strategy achieves < 10 second failover?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **Read-after-write consistency:** Route writes to a primary region with async replication. Use read-your-writes consistency by reading from primary for a short window, or use hybrid-clock-based timestamps with CRDTs.
2. **Thundering herd prevention:** Gradual traffic shift via DNS weight stepping (10% → 25% → 50% → 100% over 2 minutes). Use a global circuit breaker — if error rate > 5% in the recovery region, pause and rebalance. 3. **DNS strategy:** Use a custom DNS authoritative server with extremely low TTL (1 second) and pre-computed failover records. Pair with Anycast for the DNS resolver itself to minimize lookup time. Use a health-checker that updates Route53 or equivalent within 3 heartbeats.

**Reference:** Docs/01-traffic-routing-advanced.md
</details>

---

## Question 20 🔴
**Topic:** BGP Hijack & Mitigation
**Type:** Open-Ended

Describe a BGP hijack attack. How would you detect it in real time and mitigate it for a large SaaS provider with a /22 prefix announced from 8 data centers?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A BGP hijack occurs when an AS falsely advertises an IP prefix it doesn't own, causing traffic to be routed to the attacker.

**Detection:** Deploy BGP monitoring (RIPE RIS, BGPMon, or internal looking glass) with prefix-origin analysis (ROA/ RPKI). Monitor for new AS paths, path length drops, or prefix more-specific advertisements.

**Mitigation:** Filter outbound BGP announcements; deploy RPKI with ROAs signed by the prefix owner; configure prefix-max and AS-path filters on upstream routers; use BGP Flowspec to drop malicious traffic; have a response runbook that contacts upstream ISPs to filter the hijacking prefix.

**Reference:** Docs/01-traffic-routing-advanced.md
</details>
