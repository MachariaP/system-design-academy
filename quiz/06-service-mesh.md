# Module 6 — Service Discovery & Service Mesh — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** Service Discovery Definition
**Type:** Multiple Choice

What is the primary function of service discovery?

A) Encrypting communication between services
B) Dynamically locating network addresses of service instances
C) Balancing database read queries
D) Monitoring service CPU usage

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Service discovery enables services to find each other's network locations (IP:port) without hardcoded addresses. It maintains a registry of healthy instances and provides lookup mechanisms via DNS (e.g., SRV records) or API queries.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 2 🟢
**Topic:** Service Mesh Overview
**Type:** Multiple Choice

What is a sidecar proxy in a service mesh?

A) A separate container/process that runs alongside the main application container
B) A database proxy that caches queries
C) A load balancer external to the service
D) A monitoring agent on the host machine

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** A sidecar proxy (e.g., Envoy) runs as a separate container or process alongside each service instance. It intercepts all network traffic in/out of the service, handling service discovery, retries, timeouts, observability, and security without modifying application code.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 3 🟢
**Topic:** Client-Side vs Server-Side Discovery
**Type:** Open-Ended

Compare client-side and server-side service discovery. Give one advantage of each.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
- **Client-side:** The client queries a registry (e.g., Consul, Eureka) and selects an instance directly. Advantage: no middle hop, lower latency.
- **Server-side:** A load balancer/router (e.g., AWS ALB, Kubernetes Service) receives requests and forwards to healthy instances. Advantage: clients don't need discovery logic and can use simple DNS.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 4 🟢
**Topic:** Envoy Proxy
**Type:** Multiple Choice

Which company originally developed Envoy Proxy?

A) Google
B) Lyft
C) Netflix
D) HashiCorp

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Envoy was originally built at Lyft in 2016 and later donated to the CNCF. It's a high-performance L3/L4/L7 proxy designed for service mesh architectures and is the default sidecar in Istio.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 5 🟢
**Topic:** mTLS
**Type:** Multiple Choice

What does mTLS (mutual TLS) provide in a service mesh context?

A) Encryption of service-to-service traffic with mutual certificate authentication
B) Load balancing between services
C) Rate limiting of API calls
D) Distributed tracing

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** mTLS encrypts traffic between services and requires both sides to present certificates, verifying both the client and server identity. This provides authentication + encryption, preventing man-in-the-middle attacks and unauthorized service access.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 6 🟢
**Topic:** Kubernetes Service
**Type:** Open-Ended

What is a Kubernetes Service and how does it relate to service discovery?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A Kubernetes Service is an abstraction that defines a logical set of Pods and a policy to access them. It provides a stable DNS name (e.g., `my-service.namespace.svc.cluster.local`) and load-balances across the Pods. Kube-DNS or CoreDNS provides service discovery by resolving service names to ClusterIPs.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 7 🟢
**Topic:** Istio Architecture
**Type:** Multiple Choice

What are the two main planes in Istio's architecture?

A) Data plane and control plane
B) North plane and south plane
C) Management plane and worker plane
D) East plane and west plane

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** The data plane consists of Envoy sidecar proxies that handle service-to-service communication. The control plane (istiod) manages and configures the proxies, handling service discovery, certificate management, and policy distribution.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 8 🟢
**Topic:** Circuit Breaking in Service Mesh
**Type:** Open-Ended

How does a service mesh implement circuit breaking without application code changes?

<details>
<summary>Answer & Explanation</summary>

**Answer:** The sidecar proxy (Envoy) monitors upstream service failures. When error rate exceeds a threshold, the proxy opens the circuit, returning errors immediately without forwarding requests. The control plane distributes circuit breaker configuration (max connections, pending requests, retries, etc.) to all proxies. The application is unaware of the circuit breaking — it's handled entirely in the sidecar.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 9 🟡
**Topic:** Istio VirtualService and DestinationRule
**Type:** Open-Ended

What is the difference between an Istio VirtualService and a DestinationRule? Give a concrete example.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
- **VirtualService:** Defines routing rules — how traffic reaches a destination. Can route based on headers, URI, weight, etc. to different subsets.
- **DestinationRule:** Defines policies for how to handle traffic once it reaches a destination — including circuit breakers, load balancing algorithms, connection pool settings, and mTLS configuration.

**Example:** VirtualService routes 90% traffic to `reviews:v1` and 10% to `reviews:v2` based on header `version: test`. DestinationRule defines that `reviews:v1` uses round-robin load balancing and a circuit breaker (max 100 connections).

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 10 🟡
**Topic:** mTLS Performance Overhead
**Type:** Calculation

A service mesh encrypts all inter-service traffic with mTLS. Each request is 2 KB. The cluster handles 100,000 requests/sec. Calculate the CPU overhead if TLS handshake happens per connection (no reuse) and if connections are reused (100 requests per connection). Assume a TLS handshake costs 2ms of CPU time on a single core.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Without connection reuse:**
- Handshakes per second: 100,000
- CPU time: 100,000 × 0.002s = 200 seconds of CPU per second.
- Requires 200 dedicated cores just for TLS — prohibitive.

**With connection reuse (100 req/conn):**
- New connections per second: 100,000 / 100 = 1,000
- CPU time: 1,000 × 0.002s = 2 seconds of CPU per second.
- Requires 2 cores — negligible.

**Conclusion:** Connection reuse is critical. HTTP/2 multiplexing (used in Istio) reduces handshake overhead to near-zero. With Keep-Alive, the overhead of mTLS is ~1-3% additional CPU.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 11 🟡
**Topic:** Service Mesh vs API Gateway
**Type:** Open-Ended

Compare a service mesh (e.g., Istio) with an API gateway (e.g., Kong). When would you use both?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Service mesh:** Handles east-west traffic (service-to-service). Focuses on reliability (retries, circuit breaking), security (mTLS), and observability (traces, metrics). Operates at the sidecar level, transparent to applications.

**API Gateway:** Handles north-south traffic (external → service). Focuses on API management (authentication, rate limiting, routing, request/response transformation). Operates at the edge.

**Use both:** The API gateway handles external traffic; the service mesh handles internal traffic. The gateway can also be part of the mesh (e.g., Istio Ingress Gateway).

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 12 🟡
**Topic:** Consul Service Discovery
**Type:** Multiple Choice

Which protocol does HashiCorp Consul use for service-to-service communication?

A) gRPC
B) HTTP and DNS
C) WebSocket
D) AMQP

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Consul provides service discovery via DNS (SRV records) and HTTP API. Services register themselves via the Consul agent, and clients discover them by querying `service-name.service.consul` or via the `/v1/catalog/service/:name` endpoint.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 13 🟡
**Topic:** Traffic Mirroring
**Type:** Open-Ended

What is traffic mirroring (shadowing) in a service mesh? How would you use it to test a new version of a recommendation engine in production?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Traffic mirroring duplicates live traffic and sends a copy to a shadow destination while the original goes to the primary destination. The shadow response is discarded.

**Use case:** In a VirtualService, mirror 100% of requests from the stable recommendation engine (v1) to the new canary (v2). The response from v2 is ignored by the client but logged/traced. Compare latency, error rates, and recommendation quality between v1 and v2 without impacting users.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 14 🟡
**Topic:** Service Mesh Observability
**Type:** Multiple Choice

Which of the following is NOT automatically provided by a service mesh's sidecar proxy?

A) HTTP request metrics (latency, status codes)
B) Application-level business logic traces
C) Distributed tracing headers propagation
D) Access logs

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** The sidecar proxies automatically generate TCP/HTTP metrics, propagate trace headers, and log all requests. However, application-level business logic traces (e.g., what a specific code path does within the application) require manual instrumentation with OpenTelemetry SDKs. The proxy captures network-level data only.

**Reference:** Docs/06-service-mesh.md
</details>

---

## Question 15 🔴
**Topic:** Service Mesh Scaling at 10,000 Services
**Type:** Whiteboard

Design a service mesh control plane (like Istio) for 10,000 services across 50 Kubernetes clusters. Each service has 10-100 instances. The control plane must push configuration updates (e.g., new routing rules) to all proxies within 30 seconds. Discuss the bottleneck and how you'd solve it.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Scale estimation:**
- Total proxy instances: 10,000 services × 50 instances avg = 500,000 Envoy proxies.
- Each proxy connects to the control plane via xDS protocol.
- Configuration push: serializing and sending full config to 500K proxies is expensive.

**Solutions:**
1. **Hierarchical control plane:** Use a global control plane to manage per-cluster control planes. Each cluster has its own Istiod instance.
2. **Delta xDS (Incremental):** Instead of sending full config on every change, send only the changed resources (Istio 1.8+ supports delta xDS).
3. **Shard by namespace/service:** Each control plane instance handles a subset of proxies (e.g., 10K per istiod).
4. **Config caching / EDS (Endpoint Discovery Service):** Separate endpoint updates (frequent) from route/cluster updates (infrequent). Endpoints use a dedicated EDS stream.
5. **Async eventual consistency:** For non-critical updates, tolerate 30s-60s propagation. Use a message queue to batch config pushes.

**Reference:** Docs/06-service-mesh.md, Docs/06-service-mesh-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Custom Network Policy with Envoy
**Type:** Whiteboard

Design an Envoy filter that blocks all traffic to endpoints tagged with `environment: staging` from services tagged with `environment: production`. The service mesh manages 5,000 services. How do you implement this without modifying application code?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Solution:** Use Envoy's RBAC (Role-Based Access Control) HTTP filter with custom metadata matching.

1. **Metadata propagation:** Istio injects service metadata (labels/environment) into Envoy's dynamic metadata. The production service's proxy knows its own environment.
2. **Envoy RBAC filter:** Configure an RBAC filter on the inbound listener (for staging services) that denies requests where the downstream peer's metadata `environment=production`.
3. **Configuration:** Use Istio's AuthorizationPolicy with custom conditions:
   ```yaml
   spec:
     action: DENY
     rules:
     - from:
       - source:
           principals: ["cluster.local/ns/prod/sa/*"]
   ```
   Or use a Wasm filter for complex logic.

4. **Scale:** For 5K services, use namespace-level or label-level policies rather than per-service policies. Use a sidecar-scoped `exportTo` to limit visibility.

**Reference:** Docs/06-service-mesh-advanced.md
</details>

---

## Question 17 🔴
**Topic:** gRPC Load Balancing in Service Mesh
**Type:** Debug

A service mesh routes gRPC traffic between two services. After enabling the mesh, P99 latency for gRPC calls increases from 5ms to 200ms. Investigation shows most connections are to a single backend instance. What is happening and how do you fix it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Problem:** gRPC uses HTTP/2 long-lived connections. The service mesh's L4 (TCP) load balancing creates one connection from the client proxy to one server proxy. Since gRPC doesn't reconnect frequently, all requests on that connection go to the same backend — effectively no load balancing.

**Fix:**
1. **Envoy's HTTP/2 connection pooling:** Configure the sidecar to break the long-lived gRPC connection into separate streams and rebalance them across backends. Enable `USE_DOWNSTREAM_PROTOCOL` or configure Envoy with HTTP/2 and connection rebalancing.
2. **Enable Envoy's "rebalance" feature:** `connectionBalanceConfig` with `exactBalance` during connection reuse.
3. **Use L7 (HTTP) gRPC load balancing:** Envoy's original_dst cluster or strict DNS with healthy-panic thresholds.
4. **Keep alive / connection draining:** Configure Envoy to drain old connections and re-establish to newly discovered backends.

**Reference:** Docs/06-service-mesh-advanced.md
</details>

---

## Question 18 🔴
**Topic:** Mesh Expansion for VMs
**Type:** Whiteboard

Design an Istio mesh expansion strategy that includes 200 virtual machines (non-Kubernetes) alongside a Kubernetes cluster. Services on VMs must be able to call and be called by Kubernetes services with mTLS. How do you handle the DNS resolution, certificate provisioning, and network connectivity?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

1. **DNS resolution:** Use Istio's DNS interception or configure VMs to use CoreDNS that forwards `.global` zone queries to the Kubernetes DNS.
2. **Certificate provisioning:** Use Istio's workload certificate provisioning (SPIFFE). On VMs, run Istio agent (istio-agent) that communicates with istiod to acquire mTLS certificates. The agent handles rotation automatically.
3. **Network connectivity:** Use a VPN or direct peering between VPCs. Install Envoy as a sidecar on each VM. If Envoy cannot run as a sidecar, use a per-VM gateway (istio-egressgateway for VM → K8s, and a VM-facing ingress gateway for K8s → VM).
4. **Service registration:** Register VM workloads in Istio's ServiceEntry. Use WorkloadEntry to specify IP addresses. Kubernetes services discover VMs via the ServiceEntry.
5. **Security:** Apply AuthorizationPolicy to both K8s and VM workloads uniformly.

**Reference:** Docs/06-service-mesh-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Canary Deployments with Service Mesh
**Type:** Whiteboard

Using Istio, design a canary deployment strategy for a payment service that:
1. Routes 1% of traffic to v2
2. Escalates to 10% if error rate < 0.1% for 5 minutes
3. Automatically rolls back if error rate exceeds 1%
4. Includes a "sticky" canary for internal testers (header `X-Canary: tester`)

<details>
<summary>Answer & Explanation</summary>

**Answer:** 

**Istio configuration:**
```yaml
# VirtualService — Weighted routing + header-based routing
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: payments
spec:
  hosts:
  - payments
  http:
  - match:
    - headers:
        X-Canary:
          exact: tester
    route:
    - destination:
        host: payments
        subset: v2
      weight: 100
  - route:
    - destination:
        host: payments
        subset: v1
      weight: 99
    - destination:
        host: payments
        subset: v2
      weight: 1
```

**Automated escalation/rollback (Flagger + Prometheus):**
Flagger automates the canary process:
1. Creates the VirtualService with 1% weight.
2. Monitors Prometheus metrics (error rate, latency P99, request rate).
3. After each interval (5 min), increases v2 weight if metrics pass thresholds.
4. Rollback: if error rate > 1%, set v2 to 0%, alert.

**Sticky canary:** The header-based match ensures `X-Canary: tester` always goes to v2 regardless of weight.

**Reference:** Docs/06-service-mesh-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Sidecar Proxy Resource Overhead
**Type:** Calculation**

A cluster runs 500 services, each with 10 instances = 5,000 pods. Each Envoy sidecar uses 50 MB RAM + 0.5 vCPU idle. Under load, each uses 200 MB RAM + 1 vCPU. Peak traffic occurs for 4 hours daily. Calculate:
1. Total resource overhead per day (vCPU-hours and GB-hours)
2. Annual cost if 1 vCPU = $24/month, 1 GB RAM = $8/month (reserved pricing)
3. How would you reduce overhead for non-mesh services?

<details>
<summary>Answer & Explanation</summary>

**Answer:**

1. **Daily resource overhead:**
   - Idle (20 hours): 5,000 × 0.5 vCPU × 20h = 50,000 vCPU-hours. RAM: 5,000 × 50 MB × 20h = 5,000 GB-hours.
   - Peak (4 hours): 5,000 × 1.0 vCPU × 4h = 20,000 vCPU-hours. RAM: 5,000 × 200 MB × 4h = 4,000 GB-hours.
   - Total: 70,000 vCPU-hours/day, 9,000 GB-hours/day.

2. **Annual cost:**
   - vCPU: 70,000 vCPU-h/day × 365 / 730 (hours/month) × $24 = ~$672,000/year.
   - RAM: 9,000 GB-h/day × 365 / 730 × $8 = ~$36,000/year.
   - Total: ~$708,000/year.

3. **Reduction strategies:**
   - Use a per-node proxy (e.g., Cilium or Istio ambient mesh) instead of per-pod sidecar.
   - Only inject sidecars for services that need mesh features.
   - Right-size sidecar resource requests (many teams over-allocate).
   - Use eBPF-based solutions (Cilium) for lower overhead.

**Reference:** Docs/06-service-mesh-advanced.md
</details>
