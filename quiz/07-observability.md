# Module 7 — Observability, Monitoring & Telemetry — Question Bank

Questions span three tiers: 🟢 Beginner, 🟡 Intermediate, 🔴 Advanced (FAANG-level).

---

## Question 1 🟢
**Topic:** RED vs USE Method
**Type:** Multiple Choice

Which of the following best describes the RED method for monitoring?

A) Requests, Errors, Duration — focused on service-level metrics
B) Utilization, Saturation, Errors — focused on resource-level metrics
C) Rate, Errors, Duration — focused on infrastructure metrics
D) Requests, Events, Data — focused on business metrics

<details>
<summary>Answer & Explanation</summary>

**Answer:** A

**Explanation:** The RED method (Requests, Errors, Duration) is designed for monitoring services and microservices. USE (Utilization, Saturation, Errors) is for infrastructure resources like CPU, memory, and disk. RED answers "is my service working?" while USE answers "is my resource saturated?"

**Reference:** Docs/07-observability.md
</details>

---

## Question 2 🟢
**Topic:** Structured vs Unstructured Logging
**Type:** Multiple Choice

What is a key advantage of structured logging over unstructured logging?

A) Structured logs are always smaller in file size
B) Structured logs use key-value pairs, enabling automated parsing and querying
C) Structured logs eliminate the need for log aggregation systems
D) Structured logs require no schema definition

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Structured logging outputs machine-parseable key-value pairs (e.g., JSON), which allows log aggregators like Elasticsearch or Loki to index and query individual fields. Unstructured plaintext logs require regex parsing and are harder to search, filter, and alert on at scale.

**Reference:** Docs/07-observability.md
</details>

---

## Question 3 🟢
**Topic:** Prometheus Basics
**Type:** Multiple Choice

How does Prometheus primarily collect metrics from targets?

A) Targets push metrics to a central agent
B) Prometheus pulls (scrapes) metrics from HTTP endpoints exposed by targets
C) Targets write metrics directly to a shared database
D) Prometheus reads metrics from log files

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Prometheus uses a pull model: it scrapes metrics from HTTP endpoints (typically `/metrics`) exposed by applications and exporters. This is in contrast to push-based systems like Graphite where agents push data to a central collector.

**Reference:** Docs/07-observability.md
</details>

---

## Question 4 🟢
**Topic:** Tracing Span
**Type:** Open-Ended

What is a "span" in distributed tracing and what information does it typically carry?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A span represents a single unit of work in a distributed system — e.g., a database query, an HTTP request to a downstream service, or a function execution. It carries: span ID, trace ID, parent span ID, operation name, start/end timestamps, tags/attributes (e.g., HTTP method, status code), and optional logs of events within the span.

**Reference:** Docs/07-observability.md
</details>

---

## Question 5 🟢
**Topic:** SLI vs SLO vs Error Budget
**Type:** Multiple Choice

What is the relationship between SLI, SLO, and Error Budget?

A) SLI is the target, SLO is the measurement, Error Budget is the difference
B) SLI is the measurement, SLO is the target, Error Budget is the tolerated deviation
C) Error Budget determines the SLI, which sets the SLO
D) SLI and SLO are synonyms; Error Budget is unrelated

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** SLI (Service Level Indicator) is the actual measured value (e.g., 99.95% availability). SLO (Service Level Objective) is the target (e.g., 99.9% availability). Error Budget = 100% - SLO (e.g., 0.1% tolerated downtime over a window). As long as the SLI stays above the SLO, the error budget is not consumed.

**Reference:** Docs/07-observability.md
</details>

---

## Question 6 🟢
**Topic:** Log Levels
**Type:** Multiple Choice

Which log level should be used for events that require immediate attention but don't cause service shutdown?

A) DEBUG
B) INFO
C) WARN
D) ERROR

<details>
<summary>Answer & Explanation</summary>

**Answer:** C

**Explanation:** WARN indicates a potential issue that should be investigated but doesn't cause immediate service degradation (e.g., high latency, retry attempts). ERROR indicates a failure that affects functionality. INFO is for normal operations. DEBUG is for detailed diagnostic information.

**Reference:** Docs/07-observability.md
</details>

---

## Question 7 🟢
**Topic:** Metrics vs Logs vs Traces
**Type:** Open-Ended

In the "three pillars of observability," what is the primary purpose of each: metrics, logs, and traces?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Metrics are numeric aggregations over time (latency p99, error rate, CPU) — best for alerting and dashboards. Logs are discrete event records with timestamps — best for deep debugging of specific events. Traces follow a request across services as it propagates through the system — best for understanding request flow and pinpointing latency bottlenecks.

**Reference:** Docs/07-observability.md
</details>

---

## Question 8 🟢
**Topic:** Health Check Endpoints
**Type:** Multiple Choice

What should a basic `/health` endpoint for a web service check?

A) Only that the process is running
B) That the process is running and critical dependencies (database, cache) are reachable
C) That the DNS resolution for all external services works
D) That the server's disk space is below 80%

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** A readiness health check should verify that the service process is alive AND that its critical dependencies (database connection pool, cache connection, upstream gRPC channels) are responsive. This prevents the load balancer from routing traffic to an instance that is alive but cannot serve requests.

**Reference:** Docs/07-observability.md
</details>

---

## Question 9 🟡
**Topic:** W3C Trace Context
**Type:** Open-Ended

What is the W3C Trace Context standard and what are the two main headers it defines?

<details>
<summary>Answer & Explanation</summary>

**Answer:** W3C Trace Context standardizes how tracing information is propagated across services via HTTP headers. The two headers are:

1. **`traceparent`** — contains the trace ID (16 bytes, globally unique), span ID (8 bytes, current span), and trace flags (sampling decision, etc.). Format: `00-{trace-id}-{span-id}-{flags}`.
2. **`tracestate`** — carries vendor-specific trace context data beyond the base standard, allowing multiple tracing systems to interoperate.

This enables consistent distributed tracing across services using different tracing libraries.

**Reference:** Docs/07-observability.md
</details>

---

## Question 10 🟡
**Topic:** Prometheus vs Graphite
**Type:** Open-Ended

Compare Prometheus and Graphite. What are the key architectural differences and in what scenarios would you choose one over the other?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Prometheus uses a pull model (scrapes targets), stores dimensional data (labels enable multi-dimensional queries), has built-in alerting (Alertmanager), and is designed for high-cardinality short-lived time series in dynamic environments (Kubernetes). Graphite uses a push model (clients send data via Carbon), stores hierarchical dot-delimited metrics (no labels), and is simpler to deploy but harder to scale with high cardinality. Choose Prometheus for cloud-native, containerized environments with dynamic service discovery. Choose Graphite for legacy infrastructure or when you need a lighter-weight push-based system.

**Reference:** Docs/07-observability.md
</details>

---

## Question 11 🟡
**Topic:** Cardinality Explosion
**Type:** Multiple Choice

What is "cardinality explosion" in the context of Prometheus metrics?

A) When too many metrics are defined, causing the Prometheus server to run out of memory
B) When a metric label has a large or unbounded set of values (e.g., user_id, request_id), causing an exponential growth in time series
C) When the scrape interval is too short, causing network saturation
D) When alerting rules exceed the configured limit

<details>
<summary>Answer & Explanation</summary>

**Answer:** B

**Explanation:** Cardinality explosion occurs when a metric label takes on a large number of unique values (e.g., tagging every HTTP request with `user_id` or `session_id`). Since each unique label combination creates a new time series, this can rapidly exhaust memory and storage. Prometheus recommends keeping label cardinality below 100,000 per metric.

**Reference:** Docs/07-observability.md
</details>

---

## Question 12 🟡
**Topic:** Sampling Strategies
**Type:** Open-Ended

Compare head-based vs tail-based sampling in distributed tracing. When would you use each?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Head-based sampling decides at the root of a trace whether to sample (e.g., sample 1% of all requests). It is simple and low-overhead but can miss rare error traces. Tail-based sampling buffers traces and decides at completion based on criteria (e.g., sample all traces with errors, or slow traces above a latency threshold). It captures more relevant traces but requires more memory and processing. Use head-based for high-throughput systems with limited infrastructure. Use tail-based when error/ latency investigation is the primary goal and you can afford the buffer overhead.

**Reference:** Docs/07-observability-advanced.md
</details>

---

## Question 13 🟡
**Topic:** Error Budget Math
**Type:** Calculation

A service has a 99.9% monthly SLO. How many minutes of downtime are allowed in a 30-day month? If the service has already experienced 20 minutes of downtime after 15 days, what's the remaining error budget and what action should the team take?

<details>
<summary>Answer & Explanation</summary>

**Answer:** Total minutes in 30 days = 30 × 24 × 60 = 43,200 minutes. Allowed downtime = 43,200 × (1 - 0.999) = 43.2 minutes. Error budget consumed = 20 minutes. Remaining error budget = 43.2 - 20 = 23.2 minutes.

Action: The team is on pace to exhaust the budget before month end (at 40 minutes if the trend holds). They should consider freezing risky deploys, throttling non-critical features, or investing in reliability improvements before the budget runs out.

**Reference:** Docs/07-observability.md
</details>

---

## Question 14 🟡
**Topic:** Log Aggregation Architecture
**Type:** Open-Ended

Describe the typical log pipeline from application to storage. What role does a log shipper play vs a log aggregator vs a log store?

<details>
<summary>Answer & Explanation</summary>

**Answer:** A log shipper (e.g., Filebeat, Fluent Bit) runs on each node, tails log files or listens on a socket, and forwards logs to a central aggregator. The log aggregator (e.g., Fluentd, Logstash) receives logs from many shippers, parses, filters, transforms, and enriches them, then writes to a log store. The log store (e.g., Elasticsearch, Loki, CloudWatch Logs) indexes and stores logs for querying and visualization (e.g., Kibana, Grafana). This three-stage pipeline decouples log production from consumption and enables centralized search and alerting.

**Reference:** Docs/07-observability.md
</details>

---

## Question 15 🔴
**Topic:** Multi-Service Tracing Debug
**Type:** Debug

A team deploys a microservice call chain: A → B → C. Service A consistently shows p99 latency of 500ms, but B and C each report p99 latency of 50ms. The total should be ~100ms, not 500ms. No errors are logged. What is the most likely cause and how would you confirm it?

<details>
<summary>Answer & Explanation</summary>

**Answer:** The discrepancy suggests **clock skew** between service A's host and B/C's hosts. A records the start time on its clock, but B and C record durations on their clocks. If A's clock is 400ms ahead of B/C's, A's perceived end-to-end latency will be inflated by that skew even though actual processing is fast.

**Confirmation:** Compare `CLOCK_MONOTONIC` offsets (or NTP offset) across hosts. In distributed tracing, use schemes like Google's "jump in span timestamps" detection — if a child span's start timestamp is before the parent's start, clock skew is present. Mitigate by using a trace-aware clock correction algorithm or by reporting durations (delta) instead of absolute timestamps.

**Reference:** Docs/07-observability-advanced.md
</details>

---

## Question 16 🔴
**Topic:** Prometheus Auto-Scaling Pipeline Design
**Type:** Whiteboard

Design a metrics pipeline that auto-scales a Kubernetes deployment based on custom application metrics (queue depth beyond 1000, p99 latency beyond 200ms). Include scrape configuration, recording rules, and HPA integration. How do you prevent flapping during traffic spikes?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **Instrumentation:** The application exposes `/metrics` with a gauge `queue_depth` and a histogram `request_duration_seconds`. 
2. **Scrape:** Prometheus scrapes via the Kubernetes service monitor with a 15s interval. 
3. **Recording rules:** Create a recording rule `:queue_depth:avg5m` averaging over 5 minutes and `:latency_p99:5m` computing histogram_quantile(0.99, rate(...)[5m]).
4. **HPA:** Use the `custom-metrics-stackdriver-adapter` or `Prometheus Adapter`. Set target: queue depth 1000, p99 latency 200ms.
5. **Flapping prevention:** Add a cooldown period (HPA `--horizontal-pod-autoscaler-downscale-stabilization` default 5 min). Use averaging windows (5m) rather than instant values. Set a minimum replica count (e.g., 2) and scale-up more aggressively than scale-down.

**Reference:** Docs/07-observability-advanced.md
</details>

---

## Question 17 🔴
**Topic:** Distributed Tracing at Scale
**Type:** Whiteboard

Design a distributed tracing system for a platform processing 500,000 requests/second across 200 microservices. The system must sample intelligently to stay under 10 TB/day storage. Discuss sampling strategy, trace context propagation, and storage backend. How do you ensure a trace that revealed a production incident is not lost?

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
1. **Trace context propagation:** W3C Trace Context headers propagated via Envoy sidecars. Each proxy generates child span IDs transparently.
2. **Sampling:** Use **tail-based sampling** with a 10-second buffer window. Sample 100% of error traces (HTTP 5xx, exceptions), 100% of traces exceeding a latency threshold (e.g., > 1s), and 1% of healthy traces. This captures the signal (incidents, slow requests) while dropping the volume of OK traces.
3. **Storage:** Use a columnar store (e.g., Elasticsearch with rollover indices, or Apache Cassandra) with time-based partitioning. Set a span retention of 7 days for full traces, 30 days for aggregated metrics (RED metrics per service). Total: ~5-8 TB/day with tail sampling.
4. **Incident preservation:** Tag the trace with a unique incident ID when an alert fires. Pin the trace index to prevent rollover deletion. Export a copy to long-term cold storage (S3/GCS).

**Reference:** Docs/07-observability-advanced.md
</details>

---

## Question 18 🔴
**Topic:** SLO Violation Root Cause
**Type:** Debug

A service has a 99.95% monthly SLO for request latency under 300ms (p99). Monitoring shows the p99 latency is 280ms, yet the SLO is in violation (99.80%). All other RED metrics look healthy. What is the most likely explanation? How do you calculate the real compliance?

<details>
<summary>Answer & Explanation</summary>

**Answer:** The SLO is likely defined as the proportion of requests that complete under 300ms (a **latency threshold**), not the p99 latency. These are different metrics: you can have p99 = 280ms but still have 0.20% of requests exceeding 300ms (the p99.8 tail). The p99 value being under 300ms guarantees only that 99% of requests are under that threshold. To meet 99.95%, you need the p99.95 latency to be under 300ms — a much stricter requirement.

**Real compliance calculation:** Count all requests with duration > 300ms over the month window. Compliance = (total_requests - slow_requests) / total_requests × 100. If this is below 99.95%, the SLO is violated even if p99 looks fine. Fix requires reducing the tail latency by optimizing GC pauses, connection pool exhaustion, or hot partitions.

**Reference:** Docs/07-observability-advanced.md
</details>

---

## Question 19 🔴
**Topic:** Centralized Logging Cost Optimization
**Type:** Whiteboard

Your logging pipeline ingests 50 TB/day of structured JSON logs. The monthly bill from your log vendor is $200,000. Design a tiered log strategy to reduce costs by 60% while ensuring that debugging data is available within 1 hour for all production incidents.

<details>
<summary>Answer & Explanation</summary>

**Answer:** 
**Tier 1 (Hot — $):** 10% of traffic (5 TB/day) retained in Elasticsearch for 7 days. Includes all ERROR, WARN, and a 1% sample of INFO/DEBUG logs. Budget: ~$40,000/mo.

**Tier 2 (Warm — $$):** 90% of logs (45 TB/day) sent to object storage (S3/GCS) as compressed Parquet files partitioned by hour and service. Retention: 30 days. Queryable via Presto/Athena on-demand. Budget: ~$25,000/mo.

**Tier 3 (Cold — $):** All logs archived to S3 Glacier Deep Archive after 30 days. Retention: 1 year. Retrieval within 12 hours. Budget: ~$15,000/mo.

**Total:** ~$80,000/mo (60% savings). Additionally, reduce log verbosity in production — drop DEBUG logs, sample INFO at 10%, and aggregate high-volume access logs as metrics instead of individual log lines.

**Reference:** Docs/07-observability-advanced.md
</details>

---

## Question 20 🔴
**Topic:** Prometheus High Availability Design
**Type:** Open-Ended

Design a highly available Prometheus monitoring stack for a multi-cluster Kubernetes environment spanning 3 regions. How do you handle data durability, query durability across regions, and long-term storage? Discuss Thanos or VictoriaMetrics architecture trade-offs.

<details>
<summary>Answer & Explanation</summary>

**Answer:** Deploy Prometheus instances per cluster (per-region, per-availability-zone) in each of 3 regions, each scraping only its local targets.

**Thanos approach:** Thanos Sidecar runs alongside each Prometheus, uploading TSDB blocks to object storage (S3/GCS). Thanos Query acts as a global query frontend, querying both local Prometheus (for recent data) and the object store (for historical data). Thanos Compactor deduplicates and down-samples blocks. Ruler handles alerting and recording rules globally. Pro: native PromQL, strong community. Con: complexity of many components.

**VictoriaMetrics approach:** Deploy `vmagent` for scraping (replaces Prometheus), `vmstorage` for storage (single binary, more efficient than Prometheus TSDB), `vmselect` for global queries, and `vminsert` as a write gateway. Pro: simpler, 10x more efficient storage, better performance at high cardinality. Con: different query language nuances, smaller ecosystem.

**Durability:** Object storage as long-term back-end (retention 1+ year). Cross-region replication of the bucket. Back up recent data (last 7 days) daily from Prometheus local storage.

**Reference:** Docs/07-observability-advanced.md
</details>
