# Service Discovery & Service Mesh — The Principal Engineer's Deep Dive

*As a Principal Infrastructure Engineer at Netflix, I've operated one of the world's largest service mesh deployments across thousands of microservices. This module dissects every layer of service discovery and mesh architecture — from control plane internals to the iptables interception mechanism — so you can design, diagnose, and optimize mesh infrastructure that serves billions of requests daily.*

> **Prerequisites:** This module assumes you have read the beginner-friendly [Module 6 guide](06-service-mesh.md) and understand the basic concepts (service registry, sidecar proxy, control plane vs data plane, mTLS). You should also understand [Module 1: Traffic Routing](../Docs/01-traffic-routing.md) (DNS, load balancers, L4/L7) and [Module 4: Distributed Communication](../Docs/04-distributed-comm.md) (RPC, CAP theorem).

---

## Table of Contents

1. [Client-Side vs Server-Side Discovery — Connection Lifecycle](#1-client-side-vs-server-side-discovery--connection-lifecycle)
2. [Service Mesh Architecture — Control Plane and Data Plane](#2-service-mesh-architecture--control-plane-and-data-plane)
3. [Dynamic Routing & Mesh Balancing](#3-dynamic-routing--mesh-balancing)
4. [Real-World Failure Modes](#4-real-world-failure-modes)
5. [Teacher's Corner](#5-teachers-corner)
6. [Glossary of Key Terms](#6-glossary-of-key-terms)
7. [Key Takeaways](#7-key-takeaways)

---

## 1. Client-Side vs Server-Side Discovery — Connection Lifecycle

```mermaid
flowchart LR
    subgraph ClientSide["Client-Side Discovery"]
        SvcA["Service A<br/>(Client)"]
        Reg["Service Registry<br/>(Consul / etcd)"]
        SvcB1["Service B<br/>Instance 1<br/>10.0.0.1:8080"]
        SvcB2["Service B<br/>Instance 2<br/>10.0.0.2:8080"]

        SvcA -->|1. Lookup service B| Reg
        Reg -->|2. Return IP list| SvcA
        SvcA -->|3. Direct call (round-robin)| SvcB1
        SvcA -->|3. Direct call| SvcB2
    end

    subgraph ServerSide["Server-Side Discovery (via LB)"]
        LB["Load Balancer<br/>(AWS ALB / K8s Service)"]
        SvcC1["Service C<br/>Instance 1"]
        SvcC2["Service C<br/>Instance 2"]

        SvcA2["Service A"] -->|1. Call LB| LB
        LB -->|2. Forward to healthy node| SvcC1
        LB -->|2. Forward| SvcC2
    end
```

### Client-Side Discovery: The Connection Lifecycle

```
┌─────────────┐  1. Lookup   ┌─────────────┐
│  Service A  │─────────────▶│  Registry   │
│  (Client)   │              │  (Consul/   │
│             │◀─────────────│   etcd)     │
└──────┬──────┘  2. Returns  └─────────────┘
       │          IP:PORT list
       │  3. Select instance
       │     (Round-robin /
       │      Least connections)
       │
       │  4. Direct HTTP/gRPC
       ▼
┌─────────────┐
│  Service B  │
│  Instance 3 │
└─────────────┘
```

**Step-by-step:**
1. **Lookup:** Service A queries the registry with the logical service name (`payment-service`). The registry returns a list of healthy instances with their IP:PORT, metadata (version, region, weight), and health status.
2. **Selection:** Service A's embedded client library selects one instance using a load-balancing strategy.
3. **Direct call:** Service A opens a TCP connection directly to Service B's IP:PORT. One network hop — the fastest possible path.
4. **Health feedback:** If the call fails, the client library notifies the registry ("mark instance 3 as unhealthy") and may retry on a different instance.

**Why this matters at scale:** At Netflix, every service instance embeds Eureka client libraries. When a new service deploys with 500 instances, each client picks up the change within 30 seconds (Eureka's heartbeat interval). The approach scales to tens of thousands of instances because the registry is not in the request path — it only answers lookup queries. **The key insight: the registry is a directory, not a router.** It does not touch a single data packet.

**The fatal flaw:** Every service must embed the right library. Polyglot environments (Go services, Python services, Node.js services) need separate library implementations. If one library has a bug (e.g., does not handle stale entries correctly), that service silently routes traffic to dead instances.

### Server-Side Discovery: The Connection Lifecycle

```
┌─────────────┐  1. Request   ┌─────────────┐  2. Lookup   ┌─────────────┐
│  Service A  │─────────────▶│  Load       │─────────────▶│  Registry   │
│  (Client)   │              │  Balancer   │              │             │
│             │              │  (ALB/Nginx)│◀─────────────│             │
└─────────────┘              └──────┬──────┘  3. Returns  └─────────────┘
                                    │           IP:PORT
                                    │  4. Forward
                                    ▼
                           ┌─────────────┐
                           │  Service B  │
                           │  Instance 2 │
                           └─────────────┘
```

**Step-by-step:**
1. **Client sends to fixed address:** Service A sends a request to a stable DNS name or load balancer IP. The client does not need to know about the registry — it just calls `payment-service.internal.example.com`.
2. **Load balancer resolves:** The load balancer (or Kubernetes kube-proxy) queries the registry or watches endpoints internally.
3. **Forward:** The load balancer picks a healthy instance and forwards the request. Two network hops: client → LB → instance.

**The smart hotel lobby analogy:**

Imagine a hotel where guests never leave their room. They call the front desk (the load balancer) and say "Connect me to the maintenance department." The front desk looks up which maintenance staff are available (registry lookup), picks one, and connects the call. The guest never knows the phone number of the specific maintenance person, nor do they know that the maintenance team changed shifts at 3 PM.

### Dynamic Health-Checking: Preventing Zombie Routing

**Zombie routing** is what happens when the registry thinks an instance is healthy but the instance is actually brain-dead — alive but incapable of serving traffic (e.g., stuck on a deadlock, out of database connections, corrupted heap).

The fix is **layered health checking**:

| Check Level | Mechanism | Failure Detection | Response |
|-------------|-----------|-------------------|----------|
| **L1: Process** (Kubernetes liveness probe) | OS-level - does PID exist? | Immediate | Kill and restart container |
| **L2: Readiness** (Kubernetes readiness probe) | Application `/healthz` — is the service ready for traffic? | 1-2 seconds | Remove from service endpoints |
| **L3: Deep health** (custom) | Service checks dependencies — is DB reachable? Is connection pool healthy? | 5-10 seconds | Mark as unhealthy, stop routing |
| **L4: Passive** (client-side failure counting) | Client observes connections failing | After N failures in M seconds | Client marks instance as unhealthy locally |

Netflix's Eureka uses TTL-based health: the service sends a heartbeat every 30 seconds. If 3 heartbeats are missed (90 seconds), Eureka evicts the instance. The 90-second window means up to 90 seconds of zombie routing — unacceptable for critical services. Solution: combine TTL with active health checking (the registry probes the instance's health endpoint every 5 seconds).

---

## 2. Service Mesh Architecture — Control Plane and Data Plane

### The Two-Planar Architecture

A service mesh is not a monolith. It is two physically and logically separate systems that communicate through a well-defined API:

```
┌─────────────────────────────────────────────────────────────┐
│                    Control Plane (Istiod)                    │
│                                                             │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐           │
│  │  Pilot     │  │  Citadel   │  │  Galley    │           │
│  │ (Routing   │  │ (mTLS cert │  │ (Config    │           │
│  │  rules,    │  │  manage-   │  │  validation│           │
│  │  discovery)│  │  ment)     │  │  + ingest) │           │
│  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘           │
│        │               │               │                    │
│        └───────────────┼───────────────┘                    │
│                        │ xDS (Discovery API)                │
└────────────────────────┼────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│  Envoy Sidecar │ │  Envoy Sidecar │ │  Envoy Sidecar │
│  (Service A)   │ │  (Service B)   │ │  (Service C)   │
│                │ │                │ │                │
│  Data Plane    │ │  Data Plane    │ │  Data Plane    │
└────────┬───────┘ └────────┬───────┘ └────────┬───────┘
         │                  │                  │
         └──────────────────┼──────────────────┘
                            │
                    All data traffic flows
                    through sidecars only
```

**Control Plane — Istiod (Istio 1.5+):**
- **Pilot:** Implements the xDS (Discovery Service) APIs: LDS (Listener), RDS (Route), CDS (Cluster), EDS (Endpoint). Pilot watches Kubernetes services and endpoints, translates them into Envoy configuration, and pushes changes to sidecars via gRPC streams.
- **Citadel:** Manages certificates. Issues SPIFFE-compliant X.509 certificates to each workload. Automatically rotates certificates before expiry. Acts as the Certificate Authority for mTLS.
- **Galley:** Validates configuration. Ingest pilot's config from Kubernetes CRDs, CLI, or API. Rejects invalid config before it reaches Pilot.

**Data Plane — Envoy Sidecars:**
- Each Envoy runs as a sidecar container in every pod.
- Envoy listens on two ports: one for inbound traffic (redirected from the app container), one for outbound traffic.
- Envoy does not process control plane traffic — only data plane traffic.
- Envoy caches the last known configuration from the control plane and continues operating if the control plane becomes unreachable.

### Transparent Interception via iptables

This is the most misunderstood part of service mesh. How does the application's traffic get redirected through the sidecar without changing a single line of application code?

```
┌─────────────────────────────────────────────────┐
│  Pod: Service A                                  │
│                                                  │
│  ┌──────────────┐   App process opens            │
│  │ Application  │───socket to 10.0.0.5:8080      │
│  │ (Python/Go/  │   (thinks it's talking         │
│  │  Java/etc.)  │    directly to Service B)      │
│  └──────┬───────┘                                │
│         │                                         │
│         │  iptables OUTPUT chain                  │
│         │  Rule: REDIRECT traffic to              │
│         │  Envoy's outbound port (15001)          │
│         ▼                                         │
│  ┌──────────────┐   Envoy intercepts,            │
│  │ Envoy Sidecar│───applies routing rules,        │
│  │ (Port 15001) │   mTLS handshake, load          │
│  │              │   balances to target            │
│  └──────┬───────┘                                │
│         │                                         │
│         │  Outbound packet to real destination    │
│         ▼                                         │
└──────────────────────────────────────────────────┘
         │
         ▼
  ┌─────────────────────────────────────────────────┐
  │  Pod: Service B                                  │
  │                                                  │
  │         │  iptables INPUT chain                  │
  │         │  Rule: REDIRECT inbound to             │
  │         │  Envoy's inbound port (15006)          │
  │         ▼                                         │
  │  ┌──────────────┐   Envoy verifies mTLS,        │
  │  │ Envoy Sidecar│───applies auth policies,       │
  │  │ (Port 15006) │   forwards to app on 127.0.0.1│
  │  └──────┬───────┘                                │
  │         │                                         │
  │         ▼                                         │
  │  ┌──────────────┐                                 │
  │  │ Application  │   Receives request —            │
  │  │ (Java/Go/    │   never knew the mesh existed   │
  │  │  etc.)       │                                 │
  │  └──────────────┘                                 │
  └──────────────────────────────────────────────────┘
```

**The iptables rules in detail (Istio init container):**
- `OUTPUT` chain: Redirect TCP traffic that is not localhost (127.0.0.1) and not the sidecar itself to Envoy's port 15001.
- `INPUT` chain: Redirect inbound TCP traffic on port 8080 (the app's port) to Envoy's inbound port 15006.
- All traffic is redirected, including traffic from the app to itself (avoided by excluding localhost).

**The app code is genuinely unaware.** The application opens a socket to `service-b:8080`. The operating system transparently redirects through Envoy. The application receives the response as if it connected directly. This is the fundamental breakthrough of sidecar-based meshes: **zero code changes for observability, security, and traffic management.**

---

## 3. Dynamic Routing & Mesh Balancing

### Traffic Splitting for Canary/Blue-Green Deployments

Once all traffic flows through Envoy, the mesh can apply routing rules that would be impossible to implement at the application layer:

```yaml
# Istio VirtualService for canary deployment
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payment-service-routing
spec:
  hosts:
  - payment-service
  http:
  - match:
    - headers:
        x-canary:
          exact: "test-user"
    route:
    - destination:
        host: payment-service
        subset: v2
  - route:
    - destination:
        host: payment-service
        subset: v1
      weight: 90
    - destination:
        host: payment-service
        subset: v2
      weight: 10
```

**What this enables:**
- **Header-based routing:** Route requests with `x-canary: test-user` to v2 regardless of weight. Internal testers see the new version while 90% of users stay on v1.
- **Gradual weight shift:** 10% → 25% → 50% → 100% with automatic rollback if error rate spikes.
- **No DNS changes, no load balancer reconfiguration, no code changes.**

### Circuit Breaking at the Infrastructure Layer

Circuit breakers are typically implemented at the application layer (Hystrix, Resilience4j). In a mesh, they operate at the transport layer, providing protection even when the application has no circuit breaker library:

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: payment-service-circuit-breaker
spec:
  host: payment-service
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http1MaxPendingRequests: 10
        maxRequestsPerConnection: 10
    outlierDetection:
      consecutive5xxErrors: 5
      interval: 30s
      baseEjectionTime: 60s
      maxEjectionPercent: 50
```

**This configuration means:**
- Max 100 concurrent TCP connections to any single instance.
- Max 10 pending HTTP requests queued. Excess = 503 immediately.
- If an instance returns 5 consecutive 5xx errors, eject it from the pool for 60 seconds.
- Never eject more than 50% of instances (prevents cascade that empties the pool).

### L7 Load Balancing

Envoy supports advanced L7 load balancing strategies beyond simple round-robin:
- **Least request:** Picks the instance with the fewest active requests — best for variable-duration workloads.
- **Ring hash:** Consistent hash on a header (e.g., `x-user-id`) — ensures the same user hits the same instance. Useful for session affinity without cookies.
- **Random:** Useful for load testing or when all options are equally good.
- **Maglev:** Consistent hash with minimal disruption on backend changes — used by Google for their internal load balancing.

---

## 4. Real-World Failure Modes

### Control Plane Partition

**Scenario:** The Istiod control plane loses connectivity to a subset of sidecars due to a network partition.

**What happens:**
- Existing sidecars continue operating with the **last known configuration** they received from the control plane.
- Routing rules remain in effect. mTLS certificates continue to work (until they expire).
- **However:** New services cannot be discovered. Canary weight changes are not applied. Certificate rotation fails.
- The system operates in a "frozen" state — functional but unchangeable.

**This is by design.** The data plane does not depend on the control plane for runtime decisions. Envoy caches all configuration. This is the difference between a mesh (resilient, cached) and a centralized load balancer (single point of failure).

**Mitigation:**
- Run the control plane with 3+ replicas across availability zones.
- Use PodDisruptionBudgets to prevent all replicas from going down simultaneously.
- Configure sidecar certificate TTL long enough to survive extended control plane outages (e.g., 24 hours), but short enough to limit damage from a compromised CA (e.g., 24 hours).
- Monitor control plane xDS push latency and error rate. If pushes fail for more than 60 seconds, page.

### Performance Tax of Sidecar Hops

**The problem:** Every request traverses two Envoy proxies (outbound from caller, inbound to callee). Each proxy adds:
- Connection acceptance (TCP stack)
- TLS handshake (certificate verification, key exchange — CPU intensive)
- Route lookup (header matching, weight selection)
- Metrics emission (request count, latency histogram, status code)
- Access logging (string formatting, file I/O)

**Measured overhead (from Lyft's Envoy production data, 2021):**
| Operation | Latency Added (p50) | Latency Added (p99) |
|-----------|---------------------|---------------------|
| TCP proxy (no TLS) | 0.05ms | 0.2ms |
| HTTP/1.1 proxy + TLS | 0.5ms | 2ms |
| HTTP/2 proxy + mTLS + access logging | 1ms | 5ms |
| Lua filter + header manipulation | 2ms | 10ms |

**For a chain of 5 services: 5 × 2 × 1ms = 10ms at p50, up to 50ms at p99.** This is the "sidecar tax."

**When it hurts:**
- High-frequency, low-payload calls (health checks, cache lookups) — the tax dominates the total request time.
- Deep call chains (A → B → C → D → E) — tax accumulates linearly.

**When it is worth it:**
- The tax buys automatic mTLS, routing agility, circuit breaking, and observability. At Netflix scale, the operational cost of implementing these features in every service library far exceeds the proxy tax.
- **Optimization:** Use direct connections (`DISABLE_ENVOY_ON_PORT` annotation) for latency-critical, low-risk paths. Lyft measures that 95% of their mesh traffic uses Envoy, and the remaining 5% (health check, internal cache) bypasses it.

### The Zombie Instance Problem in Server-Side Discovery

When a load balancer (AWS ALB, kube-proxy) caches endpoint data, it can route to a terminated instance until the cache expires. The fix is:
1. **Pre-stop hooks:** When Kubernetes terminates a pod, the pre-stop hook delays termination for a configurable "drain period" — usually 30-60 seconds — during which the load balancer detects the instance is unhealthy.
2. **Connection draining (AWS ALB):** Deregistration delay = 300 seconds ensures in-flight requests complete before the instance is removed.
3. **Readiness gates:** The pod does not become "ready" until Envoy confirms it has received initial configuration from the control plane.

---

## 5. Teacher's Corner

### Advanced Question 1: Scalability Limit of Centralized Discovery

*"You deploy a microservice with 50,000 instances in a single region. Each instance heartbeats to the registry every 10 seconds. Design the registry architecture. What is the bottleneck? How does a mesh improve or worsen this?"*

**Grading Rubric (Principal level):**

| Score | Criteria |
|-------|----------|
| **Outstanding (10)** | Identifies that 50K instances × 10s heartbeat = 5,000 heartbeats/second. This is within ZooKeeper/etcd write capacity (10K+ writes/sec), but the watch fan-out is the bottleneck — every registry change triggers updates to all 50K clients, generating 50K × N changes/second of watch traffic. Proposes hierarchical partitioning: split the registry by service type or shard key, with a global aggregator for cross-service lookups. Explains that a mesh makes this worse (each Envoy watches endpoints via xDS, same fan-out problem) unless you use an intermediate load balancer (server-side discovery) that absorbs the watch fan-out and presents a single endpoint to clients. References Google's SRE book on "watch-based vs poll-based" registry design. |
| **Good (7-9)** | Identifies heartbeat volume as a concern. Mentions hierarchical registries or sharding. Does not address watch fan-out or mesh implications. |
| **Needs Work (<7)** | Suggests a single ZooKeeper cluster with no scaling concern. Does not calculate heartbeats/second. |

### Advanced Question 2: Sidecar vs Centralized LB Trade-Off

*"Your CTO proposes replacing the service mesh with a centralized L7 load balancer cluster for all inter-service communication. 'Fewer moving parts, lower latency, simpler ops.' Defend or oppose this decision with specific metrics and trade-offs."*

**Grading Rubric (Staff/Principal level):**

| Score | Criteria |
|-------|----------|
| **Outstanding (10)** | Opposes with precise reasoning: (1) Centralized LB becomes a single point of failure AND a throughput bottleneck — all 50K inter-service calls pass through it, requiring a 100Gbps+ cluster with N+2 redundancy. (2) LB adds two network hops (client → LB → server) — same as mesh's two proxy hops, but centralized (cannot be colocated) adds cross-AZ latency. (3) Centralized LB cannot do per-instance health checking — it routes to a service VIP, not individual instances. (4) Security: mTLS termination at a centralized point creates a TLS bottleneck — sidecars distribute the crypto work. (5) Ops: upgrading the centralized LB requires traffic draining and rollout — mesh sidecars are upgraded per-pod during rolling deployments, zero additional ops. References Google's B4 paper and the rationale for per-host Envoy. |
| **Good (7-9)** | Mentions SPOF and throughput concerns. Prefers mesh but cannot quantify the comparison. |
| **Needs Work (<7)** | Defends centralized LB without addressing SPOF or throughput calculations. |

### Advanced Question 3: CAP During Canary Rollout

*"During a canary rollout, the control plane pushes a 'send 10% to v2' routing rule to all sidecars. Two sidecars do not receive the update due to a network partition. A third sidecar receives it partially (the RDS update but not the CDS update for v2 cluster). What happens to traffic? How does this relate to CAP theorem?"*

**Grading Rubric (Principal level):**

| Score | Criteria |
|-------|----------|
| **Outstanding (10)** | Identifies this as a Consistency vs Availability trade-off in a system with P (network partition). The two sidecars that missed the update continue routing 100% to v1 (safe, consistent with old state). The sidecar with RDS but not CDS has an inconsistent state: it knows to route 10% to v2 but does not know where v2 endpoints are — these requests fail. This is a CP failure mode. Proposes the fix: Envoy validates configuration consistency before applying — if RDS references a cluster not in CDS, reject the RDS update. At Istio level: use a version-ordered configuration push where CDS updates are pushed before RDS, and a version check ensures any sidecar receiving RDS v2 has also received CDS v2. This is essentially a distributed agreement problem solved with configuration versioning, not consensus. References Istio's "update ordering" design doc and Envoy's "warm-up" mechanism for new clusters. |
| **Good (7-9)** | Identifies the partial update problem. Mentions that requests to v2 would fail. Does not relate to CAP or propose a configuration validation fix. |
| **Needs Work (<7)** | Proposes "just restart the sidecar" or assumes the control plane is synchronous. |

---

## 6. Glossary of Key Terms

| Term | Section | Definition |
|------|---------|------------|
| **Zombie Routing** | 1 | Routing traffic to an instance that is alive but incapable of serving traffic, because the registry has stale health information |
| **Eureka** | 1 | Netflix's service registry — client-side discovery with TTL-based heartbeats and 30s propagation delay |
| **xDS API** | 2 | Envoy's Discovery Service API family: LDS (Listener), RDS (Route), CDS (Cluster), EDS (Endpoint) — the protocol between control plane and data plane |
| **SPIFFE** | 2 | Secure Production Identity Framework for Everyone — standard identity format for workloads in a mesh: `spiffe://cluster.local/ns/default/sa/payment-sa` |
| **Transparent Interception** | 2 | Using iptables rules to redirect application traffic through a sidecar proxy without the application's knowledge |
| **Init Container** | 2 | Container that runs before the main container in a Kubernetes pod — Istio uses an init container to set up iptables rules |
| **Maglev** | 3 | Google's consistent hashing algorithm for load balancing — minimizes disruption when backend membership changes |
| **Sidecar Tax** | 4 | The latency overhead added by each sidecar proxy hop in a service mesh |
| **Connection Draining** | 4 | Allowing in-flight requests to complete before terminating a connection, preventing data loss during scaling events |
| **Partition Tolerance** | 5 | CAP property — the system continues operating despite arbitrary message loss or delay between nodes |

---

## 7. Key Takeaways

1. **Client-side discovery gives lowest latency (1 hop) but requires library per language.** Server-side discovery simplifies clients (2 hops) but adds a load balancer SPOF.

2. **Health checking must be multi-layered.** Process health + readiness probe + deep dependency check + passive failure counting prevents zombie routing.

3. **The mesh's two-planar architecture is fundamental.** The data plane (Envoy) operates independently of the control plane (Istiod). Cached config means existing traffic continues if the control plane goes down.

4. **Transparent interception via iptables is the core innovation.** Zero code changes for mTLS, routing, circuit breaking, and observability.

5. **The sidecar tax is real but usually worth it.** Measure it in your environment. Bypass the mesh for latency-critical, low-risk paths.

6. **Traffic splitting in the mesh is more powerful than DNS weighting.** Header-based routing + gradual weight shift + automatic rollback = confident canary deployments.

7. **Circuit breaking at the mesh layer protects even services without circuit breaker libraries.** Connection pooling + outlier detection + ejection limits work for any language.

8. **Configuration consistency during partial control plane partition is a solvable CP problem.** Version-ordered pushes and cross-check rejection prevent inconsistent routing state.

9. **The centralized LB vs mesh debate is a throughput vs architecture trade-off.** Mesh distributes the work and eliminates SPOF, at the cost of per-instance CPU overhead.

10. **Pre-stop hooks, connection draining, and readiness gates are mandatory.** Without them, scaling events and deployments silently drop requests.

---

> This deep-dive gives you the mental model to design service mesh infrastructure that Netflix and Google rely on. You can now argue the trade-offs between discovery patterns, diagnose control plane failures by reading xDS traffic, and design a canary rollout strategy that survives network partitions.
