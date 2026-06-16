# Observability: Monitoring, Logging & Tracing – A Beginner's Guide

> This guide explains the three pillars of observability — Metrics, Logs, and Traces — and how they work together to help you understand what your system is doing, why it is failing, and where to look.
> Every technical term is defined the first time it appears, and a full Glossary is at the end.
> Once you understand these foundations, the original advanced module will feel like a natural next step.

---

## Table of Contents

1. [Why Observability Matters](#1-why-observability-matters)
2. [The Three Pillars: Metrics, Logs, Traces](#2-the-three-pillars-metrics-logs-traces)
3. [Metrics – The What](#3-metrics--the-what)
4. [Logs – The Why](#4-logs--the-why)
5. [Traces – The Where](#5-traces--the-where)
6. [SLI, SLO, and Error Budgets](#6-sli-slo-and-error-budgets)
7. [Alerts: Push vs Pull](#7-alerts-push-vs-pull)
8. [Common Disasters and How to Avoid Them](#8-common-disasters-and-how-to-avoid-them)
9. [Putting It All Together — Debugging a Slow Request](#9-putting-it-all-together--debugging-a-slow-request)
10. [Glossary of Technical Terms](#10-glossary-of-technical-terms)
11. [Key Takeaways](#11-key-takeaways)

---

## 1. Why Observability Matters

When your application is a single process running on one machine, you can debug it by looking at the console, attaching a debugger, or checking a single log file. But in a distributed system with hundreds of microservices, a request may pass through 10 different services, each running on a different machine in a different data center. You cannot attach a debugger to all of them at once.

**Observability** is the practice of designing your system to answer questions about its internal state *from the outside*, without deploying new code. If your system is observable, you can ask "what happened?" after a failure without ever connecting to a running server.

---

## 2. The Three Pillars: Metrics, Logs, Traces

Relying on only one type of telemetry is like diagnosing a car with only a speedometer:

- The **speedometer** tells you the car is moving (Metrics), but not why the engine is sputtering.
- The **check-engine light** tells you something is wrong (Logs), but not which cylinder misfired first.
- The **timing of the misfire** pinpoints the exact problem (Traces).

You need all three to form a complete picture.

| Pillar | Answers | Analogy |
|--------|---------|---------|
| **Metrics** | What is happening? | Speedometer, fuel gauge, odometer |
| **Logs** | Why is it happening? | Check-engine light, mechanic's notes |
| **Traces** | Where is it happening? | Which cylinder misfired, in what order |

---

## 3. Metrics – The What

**Metrics** are numbers measured over time. They are cheap to store and fast to query. There are three basic types:

| Type | Behavior | Example | Analogy |
|------|----------|---------|---------|
| **Counter** | Only goes up (monotonic) | Total HTTP requests | An odometer — you read the difference between now and 5 minutes ago |
| **Gauge** | Goes up and down | Current memory usage | A fuel gauge — you care about the value right now |
| **Histogram** | Statistical distribution | Request latency (p50, p99) | A speed camera that records every car's speed — you ask "what speed did 99% of cars stay under?" |

**Why metrics are valuable:** They are extremely efficient. A single metric with a few labels takes a few bytes. You can store millions of data points across thousands of machines in a dedicated **Time-Series Database (TSDB)** like Prometheus.

**Why metrics are insufficient:** They tell you something is wrong (e.g., error rate spiked) but not *why*. For that, you need logs and traces.

---

## 4. Logs – The Why

**Logs** are records of discrete events. A good log entry is **structured** (machine-readable) — it is a JSON object with key-value pairs, not a sentence:

```json
{"timestamp": "2026-05-21T14:30:00Z", "level": "ERROR", "service": "payments", "message": "payment declined", "error_code": "insufficient_funds", "amount": 49.99}
```

Structured logs can be indexed and queried: "How many `insufficient_funds` errors happened in the last hour?" — a question that is slow and expensive with unstructured text.

**The cost of logs:** Logs are **10-100x more expensive** to store than metrics. Every string takes disk space and CPU to index. In production, teams aggressively reduce log volume by:
- Sampling debug logs (store 1 in 100 debug messages)
- Using higher log levels in production (WARN and above only)
- Expiring low-value logs after days, not years

**Best practice:** Always include a **correlation ID** (like a `trace_id`) in every log entry. This lets you connect a log to a specific request's trace.

---

## 5. Traces – The Where

**Traces** track a single request as it moves through multiple services. A trace is a tree of **spans**, where each span represents one unit of work (e.g., "validate token" in the auth service, "query database" in the order service).

**How tracing works:**

1. The first service (e.g., API gateway) generates a unique **Trace ID** and creates a **Span** for the incoming request.
2. When the gateway calls the next service, it passes the Trace ID in an HTTP header (`traceparent`).
3. The next service creates a child span, records its work, and passes the Trace ID further downstream.
4. A collector gathers all spans from all services and assembles them into a single trace.

**Why traces are critical:** In a distributed system, a single user request might touch 10-15 services. Without traces, you have 15 sets of metrics and 15 log files. With traces, you can see exactly which service caused the slowdown.

**The cost of traces:** Storing every span for every request is expensive. Most systems use **sampling**:
- **Head-based sampling:** Decide at the start of a request whether to trace it (e.g., trace 1% of requests). Simple but may miss rare errors.
- **Tail-based sampling:** Trace everything temporarily, then decide which traces to keep based on what happened (e.g., keep all traces with errors). More complex but captures more signal.

---

## 6. SLI, SLO, and Error Budgets

These three concepts form the contract between your team and your users about reliability.

| Term | Meaning | Example |
|------|---------|---------|
| **SLI (Service Level Indicator)** | A metric that measures a specific aspect of reliability | "The percentage of requests that complete in under 200ms" |
| **SLO (Service Level Objective)** | The target value for the SLI | "99.9% of requests complete in under 200ms, measured over 30 days" |
| **Error Budget** | The allowed amount of unreliability | "100% - 99.9% = 0.1% of requests can be slow or fail. If we have 10M requests per month, that is 10,000 allowed errors." |

**How error budgets drive decisions:** If your error budget is not exhausted, you can deploy new features. If the budget is running low, you must stop deploying and focus on reliability. This turns reliability into a data-driven decision, not an emotional argument between "ship fast" and "don't break things."

**Burn rate alerting:** Instead of alerting when you have exceeded your SLO (too late!), you alert when you are **burning through your error budget too fast**. For example, if your error budget for a month is 10,000 errors and you have 5,000 errors in 1 hour, something is very wrong — alert immediately.

---

## 7. Alerts: Push vs Pull

There are two main ways to collect telemetry:

| Architecture | How it works | Best for |
|-------------|--------------|----------|
| **Pull (Prometheus)** | The monitoring server polls each service's `/metrics` endpoint at regular intervals. | Persistent services running on known servers. |
| **Push (StatsD, OpenTelemetry Collector)** | Each service sends metrics to a central collector, which buffers and forwards them. | Ephemeral workloads (Lambda, short-lived batch jobs) that will not be around when the poller asks. |

**The danger of push:** If the collector crashes or the network is congested, metrics can be lost. The service thinks it sent data, but nobody received it.

**The danger of pull:** If a service is overloaded, serving the `/metrics` page might make it more overloaded. Also, short-lived jobs may finish before the next poll.

---

## 8. Common Disasters and How to Avoid Them

### Cardinality Explosion

You decide to add a `user_id` label to your metrics to track per-user performance. If you have 1 million active users, your metric now has 1 million unique label combinations. The TSDB's memory usage goes from megabytes to gigabytes in minutes, causing an Out-Of-Memory (OOM) crash.

**Mitigation:** Never use unbounded values (user IDs, session IDs, email addresses) as metric labels. Use high-cardinality data in traces, not metrics.

### Head-Based Sampling Misses Rare Errors

You trace 1% of all requests. A rare bug causes a 0.01% error rate. You have a 1 in 10,000 chance of capturing that error in your traces. You will almost never see it.

**Mitigation:** Use tail-based sampling (keep all traces with errors) or increase the sampling rate for error spans.

### The 15-Minute Blind Spot

Your push-based metrics collector (StatsD) sends data in batches every 15 minutes. During a Black Friday sale, the payment service starts failing. The ops team does not notice for 15 minutes because the metrics are from before the failure.

**Mitigation:** Use real-time streaming (sub-minute granularity) for critical metrics. Batch for cost savings on non-critical ones.

---

## 9. Putting It All Together — Debugging a Slow Request

A user reports that the "Place Order" button takes 10 seconds. Here is how observability helps:

1. **Metrics (p99 latency)** — You open your dashboard and see that the order service p99 latency jumped from 200ms to 8 seconds. Something is clearly wrong.

2. **Traces** — You search for recent traces with high latency. You see one trace showing:
   - API Gateway → 50ms (normal)
   - Order Service → 200ms (normal)
   - Payment Service → 7.5 seconds (problem found!)

3. **Logs** — You open the payment service logs for that trace ID. You see: `"level": "WARN", "message": "connection timeout on attempt 3/3"`. The payment service is timing out trying to reach the external payment provider.

4. **Action:** The payment provider's API is down. You activate the fallback (queue payments for later) and page the provider's support team.

Without all three pillars, you would have known *something* was slow (metrics), but not *where* (traces) or *why* (logs).

---

## 10. Glossary of Technical Terms

| Term | Definition |
|------|------------|
| **Burn Rate** | The rate at which you consume your error budget. High burn rate = immediate action required. |
| **Cardinality** | The number of unique values a label or field can have. High cardinality = expensive. |
| **Correlation ID** | A unique identifier attached to a request that flows through all services and log entries. |
| **Counter** | A metric that only increases (e.g., total requests). |
| **Error Budget** | The acceptable amount of unreliability: 100% minus your SLO target. |
| **Gauge** | A metric that goes up and down (e.g., current memory). |
| **Head-Based Sampling** | Deciding at the start of a request whether to trace it. |
| **Histogram** | A metric that records a distribution of values (e.g., latency percentiles). |
| **Logs** | Discrete records of events, ideally in structured (JSON) format. |
| **Metrics** | Numerical measurements aggregated over time. |
| **Observability** | The ability to understand a system's internal state from its external outputs. |
| **OpenTelemetry** | An open standard for generating, collecting, and exporting telemetry data. |
| **p50 / p95 / p99** | The latency value below which 50%/95%/99% of requests fall. p99 is the most important for user experience. |
| **Prometheus** | A popular pull-based metrics and alerting system. |
| **Sampling** | Recording only a subset of traces to reduce cost. |
| **SLI (Service Level Indicator)** | A specific metric that measures reliability (e.g., latency, error rate). |
| **SLO (Service Level Objective)** | The target value for an SLI (e.g., 99.9% of requests succeed). |
| **Span** | A single unit of work within a trace (e.g., a database query). |
| **Structured Logging** | Logging in a machine-readable format (JSON) rather than free text. |
| **Tail-Based Sampling** | Deciding which traces to keep after seeing the full result (keeps errors). |
| **Three Pillars** | Metrics, Logs, and Traces — the three types of telemetry data. |
| **Trace** | The complete path of a single request through a distributed system. |
| **Trace ID** | A unique identifier shared by all spans in a single request. |
| **TSDB (Time-Series Database)** | A database optimized for storing and querying metrics with timestamps. |

---

## 11. Key Takeaways

1. **Metrics tell you what, logs tell you why, traces tell you where.** You need all three.
2. **Structured logs** (JSON with key-value pairs) are far more useful than unstructured text.
3. **Always include a correlation ID (trace ID)** in every log entry to connect logs to traces.
4. **SLIs → SLOs → Error Budgets** form a decision framework for reliability: is it safe to deploy?
5. **Watch the burn rate**, not just the absolute error count. A sudden high burn rate is an emergency.
6. **High cardinality kills TSDBs.** Never use user IDs, email addresses, or session IDs as metric labels.
7. **Tail-based sampling** catches rare errors that head-based sampling would miss.
8. **Push for ephemeral workloads, pull for persistent services.**
9. **Correlation IDs are the glue** that tie the three pillars together.
10. **Design for observability from the start.** Adding it after a crisis is expensive and slow.

---

> This guide explains the "why" behind observability patterns.
> Once you're comfortable with these concepts, the original module (with its OpenTelemetry details, PromQL burn rate alerts, and structured logging code) will serve as your in-depth reference.
> Remember: you cannot fix what you cannot see — invest in observability before you need it.
