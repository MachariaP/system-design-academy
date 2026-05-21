# Module 5: Asynchronous Processing & Message Queues

Synchronous systems fail in chains.

If a user request directly calls a slow payment processor, a report generator, an image transformer, an email provider, and a database, the user is now waiting on every dependency. Worse, every dependency outage becomes a user-facing outage.

Asynchronous messaging changes the shape of the system. The application records intent, places work into a broker, and lets independent worker pools process that work at their own pace. This is how high-scale systems absorb bursts, isolate failures, and keep core product flows alive under pressure.

---

## Learning Goals

By the end of this module, you should be able to:

| Skill | What You Should Be Able To Explain |
|---|---|
| **Queue lifecycle** | How clients, applications, brokers, and workers interact |
| **Point-to-point queues** | Why one task should usually be processed by one worker |
| **Pub/Sub** | Why one event may need to reach many independent subscribers |
| **Delivery guarantees** | Why at-least-once delivery requires idempotent consumers |
| **Backpressure** | How queues protect memory, databases, and downstream services |
| **DLQs** | How failed jobs are isolated for later repair |
| **Retry strategy** | Why exponential backoff and jitter prevent retry storms |
| **Service boundaries** | How async messaging helps services scale independently |

---

## 1. Why Asynchronous Processing Exists

A web request should not do every expensive task inline.

Good async candidates include:

- Image resizing and video transcoding.
- Report generation.
- Email and SMS delivery.
- Search indexing.
- Fraud checks.
- Payment capture workflows.
- Inventory reservation.
- Webhook delivery.
- Analytics and audit pipelines.

The user-facing system should record the request, return quickly, and let workers complete the slow work in the background.

---

## 2. Message Queue Lifecycle

Consider a user generating a large financial report.

### End-To-End Runtime Flow

| Step | Component | Action |
|---:|---|---|
| 1 | **Client** | Sends `POST /reports` |
| 2 | **Application** | Validates request and creates a `report_id` |
| 3 | **Application** | Publishes a job message to the broker |
| 4 | **Broker** | Durably stores the message |
| 5 | **Application** | Returns `202 Accepted` with report status URL |
| 6 | **Worker** | Pulls or receives the message |
| 7 | **Worker** | Generates the report |
| 8 | **Worker** | Writes result to object storage or database |
| 9 | **Worker** | Acknowledges the message |
| 10 | **Client** | Polls, subscribes, or receives notification when complete |

### Why This Helps

| Problem In Synchronous Flow | Async Improvement |
|---|---|
| User waits for heavy work | User gets quick acknowledgement |
| Web servers do CPU-heavy jobs | Worker pool handles computation |
| Traffic spike overloads downstream service | Broker buffers work |
| One dependency slows the whole request | Work can retry independently |
| Scaling web means scaling workers too | Each layer scales separately |

---

## 3. Message Queues: Point-To-Point

A **message queue** delivers each task to one consumer.

This is the right model when work should be performed exactly once from a business perspective, even if technical delivery is at-least-once.

Examples:

- Process one payment.
- Generate one report.
- Resize one uploaded image.
- Send one password reset email.
- Reserve inventory for one order.

### Queue Semantics

| Concept | Meaning |
|---|---|
| **Producer** | Publishes work into the queue |
| **Broker** | Stores messages and dispatches them |
| **Consumer/Worker** | Processes messages |
| **Acknowledgment** | Worker confirms successful processing |
| **Negative acknowledgment** | Worker rejects or requeues failed work |
| **Visibility / in-flight state** | Message is temporarily hidden while a worker processes it |
| **Durability** | Broker persists messages so they survive restart |

### Delivery Guarantees

Most real queues provide **at-least-once delivery**.

That means a message can be delivered more than once if:

- A worker crashes after doing work but before acking.
- The broker loses the worker connection.
- The ack times out.
- A retry policy deliberately republishes the job.

Therefore, consumers must be **idempotent**.

Idempotent processing means running the same message twice does not duplicate business effects. Use idempotency keys, unique constraints, processed-message tables, or state-machine transitions.

---

## 4. Pub/Sub: Broadcasting

**Publish/Subscribe** delivers one event to many independent subscribers.

This is the right model when multiple systems need to react to the same fact.

Example: `OrderPlaced`

| Subscriber | Reaction |
|---|---|
| Payment service | Capture payment |
| Inventory service | Reserve stock |
| Email service | Send confirmation |
| Analytics service | Record conversion |
| Fraud service | Score order |
| Search/indexing service | Update projections |

The event is broadcast. Each subscriber owns its own processing.

### Pub/Sub Semantics

| Concept | Meaning |
|---|---|
| **Topic / exchange** | Named event stream |
| **Publisher** | Emits events |
| **Subscriber group** | Logical consumer of events |
| **Fanout** | One event reaches many subscribers |
| **Offset / cursor** | Subscriber's position in a log-style system |
| **Replay** | Ability to reprocess historical events |

---

## 5. Queue vs. Pub/Sub Comparison

| Dimension | Message Queue: Point-to-Point | Pub/Sub: Broadcasting |
|---|---|---|
| **Primary purpose** | Distribute tasks among workers | Notify multiple systems of events |
| **Consumer model** | One message handled by one worker in a group | One event delivered to many subscriber groups |
| **Throughput** | High; scales with worker count and partitions/queues | Very high in log systems; scales by topic partitions and consumer groups |
| **Delivery guarantee** | Usually at-least-once; exactly-once requires idempotency and broker support | Usually at-least-once; Kafka can provide exactly-once processing under strict constraints |
| **Durability** | Durable queues persist messages until acked or expired | Durable logs retain events by time or size policy |
| **Ordering** | Usually best within one queue or partition | Usually guaranteed only within a partition |
| **Replay** | Limited or awkward in traditional queues | Natural in log-based systems like Kafka |
| **Best use cases** | Background jobs, task queues, work distribution | Event-driven architecture, audit streams, projections, analytics |
| **Common tools** | RabbitMQ, SQS, Celery, Redis queues | Kafka, Pulsar, SNS/SQS fanout, RabbitMQ exchanges |

### Exactly-Once Reality Check

"Exactly once" is rarely a simple broker feature.

End-to-end exactly-once behavior requires:

- Idempotent producers.
- Transactional writes or deduplication.
- Consumer offset commits tied to output commits.
- Stable message IDs.
- Careful handling of retries and crashes.

In most business systems, design for **at-least-once delivery plus idempotent consumers**.

---

## 6. Producer-Consumer Architecture

Kafka-style brokers scale through partitions. A topic is split into partitions, and each partition is consumed by at most one worker inside a consumer group at a time.

That gives load balancing while preserving ordering within each partition.

```mermaid
flowchart LR
    Client["Client<br/>Checkout Request"]
    API["Checkout API<br/>validates request"]
    DB["Orders DB<br/>order status=pending"]

    subgraph Broker["Message Broker: Kafka Topic orders"]
        P0["Partition 0<br/>order_id hash range A"]
        P1["Partition 1<br/>order_id hash range B"]
        P2["Partition 2<br/>order_id hash range C"]
    end

    subgraph Group["Consumer Group: payment-workers"]
        W1["Worker 1<br/>assigned P0"]
        W2["Worker 2<br/>assigned P1"]
        W3["Worker 3<br/>assigned P2"]
    end

    Payment["Payment Provider"]
    Inventory["Inventory Service"]
    DLQ["Dead Letter Topic/Queue<br/>failed orders"]
    Retry["Retry Topic/Queue<br/>delayed backoff"]

    Client -->|"POST /checkout"| API
    API -->|"create order row"| DB
    API -->|"produce OrderSubmitted event<br/>key=order_id"| Broker
    API -->|"202 Accepted<br/>order pending"| Client

    Broker --> P0
    Broker --> P1
    Broker --> P2

    P0 -->|"ordered stream"| W1
    P1 -->|"ordered stream"| W2
    P2 -->|"ordered stream"| W3

    W1 --> Payment
    W2 --> Payment
    W3 --> Payment

    W1 --> Inventory
    W2 --> Inventory
    W3 --> Inventory

    W1 -->|"success: commit offset / ack"| P0
    W2 -->|"temporary failure"| Retry
    Retry -->|"after delay"| Broker
    W3 -->|"permanent failure or retries exhausted"| DLQ

    W1 -->|"mark paid/failed"| DB
    W2 -->|"mark paid/failed"| DB
    W3 -->|"mark paid/failed"| DB
```

### Partitioning Rules

| Rule | Why It Matters |
|---|---|
| Use stable keys such as `order_id` | Related events go to the same partition |
| Do not use a hot key for all messages | One partition becomes overloaded |
| More partitions allow more consumers | But increase broker and operational overhead |
| Ordering is per partition | Global ordering does not scale well |

---

## 7. Backpressure

**Backpressure** is how a system says: "I cannot safely accept more work right now."

Queues are buffers, not magic. If producers publish faster than consumers process, the backlog grows.

### What Happens When Workers Fall Behind

| Symptom | Meaning |
|---|---|
| Queue depth grows | Producers are outpacing consumers |
| Message age increases | Users wait longer for completion |
| Broker memory rises | Broker may page to disk or throttle |
| Worker CPU is saturated | Need more workers or less work per job |
| Downstream latency rises | Workers are blocked on another dependency |
| Retries increase | Failures are amplifying load |

### Backpressure Controls

| Control | Effect |
|---|---|
| **Queue length limits** | Prevent unbounded memory growth |
| **Producer rate limits** | Slow new work before broker collapse |
| **HTTP 429/503 responses** | Tell clients to retry later |
| **Worker concurrency caps** | Avoid overwhelming databases or APIs |
| **Prefetch limits** | Prevent one worker from hoarding too many messages |
| **Circuit breakers** | Stop calling unhealthy downstreams |
| **Autoscaling** | Add workers when backlog and downstream health allow |

Backpressure should protect the whole system, not just the broker.

---

## 8. Service Boundaries And Discovery

Async messaging works best when service boundaries are clear.

### Web Layer vs. Worker Layer

| Layer | Responsibility |
|---|---|
| **Web/API layer** | Authentication, validation, fast response, job publication |
| **Broker layer** | Durable buffering, routing, delivery tracking |
| **Worker layer** | Slow computation, retries, downstream integration |
| **Storage layer** | Durable state, job status, results |

This lets each layer scale independently. If image processing gets expensive, scale workers. If HTTP traffic spikes, scale web servers. If broker lag grows, add partitions, queues, or consumers.

### Service Discovery

In cloud systems, IP addresses change constantly. Service discovery systems such as Consul, ZooKeeper, and etcd maintain a live registry.

| Mechanism | Purpose |
|---|---|
| **Registration** | Service instances announce host, port, and metadata |
| **Health checks** | Unhealthy instances are removed from routing |
| **Key-value config** | Shared dynamic configuration |
| **Watch APIs** | Clients update when membership changes |
| **Leader election / locks** | Coordinate singleton workers or schedulers |

For messaging systems, service discovery helps clients locate brokers, schema registries, and dependent services.

---

## 9. Tooling Trade-Offs

| Tool | Strengths | Trade-Offs |
|---|---|---|
| **Redis Pub/Sub** | Very low latency, simple broadcasting | Weak durability; subscribers can miss messages |
| **Redis Streams** | Persistent stream with consumer groups | Operational limits compared with Kafka-scale logs |
| **RabbitMQ** | Strong task queue semantics, routing, acknowledgments, DLQs | Cluster operations and AMQP concepts add complexity |
| **Kafka** | High-throughput durable log, replay, partitions, consumer groups | More operational complexity; not ideal for tiny per-message task semantics |
| **Amazon SQS** | Managed queue, durable, simple scaling | At-least-once delivery, possible duplicates, higher latency than local brokers |
| **Celery** | Python task queue with scheduling and worker management | Tied to Python ecosystem; broker/backend choices matter |

### Simple Delivery vs. Durable Task Delivery

| Dimension | Simple Pub/Sub | Durable Task Queue |
|---|---|---|
| **Message persistence** | Often none or limited | Persistent until acked or expired |
| **Acknowledgments** | Often absent | Core feature |
| **Message loss risk** | Higher | Lower when configured correctly |
| **Latency** | Very low | Slightly higher due to durability |
| **Replay** | Usually no | Sometimes, depending on broker |
| **Best fit** | Live notifications, ephemeral updates | Payments, jobs, reports, emails |

---

## 10. Production Code Template: RabbitMQ Task Queue

This template uses `pika` to implement durable task publication and acknowledged consumption.

Install:

```bash
pip install pika
```

### `producer.py`

```python
"""
RabbitMQ Task Producer
======================

Publishes durable JSON jobs to a task queue.

Environment:
  RABBITMQ_URL=amqp://guest:guest@localhost:5672/%2F
"""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Dict

import pika


QUEUE_NAME = "report.tasks"
EXCHANGE_NAME = "report.exchange"
ROUTING_KEY = "report.generate"


def connect() -> pika.BlockingConnection:
    params = pika.URLParameters(
        os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
    )
    params.heartbeat = 30
    params.blocked_connection_timeout = 60
    return pika.BlockingConnection(params)


def publish_task(payload: Dict[str, Any]) -> None:
    message_id = payload.setdefault("job_id", str(uuid.uuid4()))
    payload.setdefault("created_at_epoch", int(time.time()))

    body = json.dumps(payload, separators=(",", ":")).encode("utf-8")

    with connect() as connection:
        channel = connection.channel()

        channel.exchange_declare(
            exchange=EXCHANGE_NAME,
            exchange_type="direct",
            durable=True,
        )
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(
            queue=QUEUE_NAME,
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
        )

        # Publisher confirms let the producer know the broker accepted the message.
        channel.confirm_delivery()

        channel.basic_publish(
            exchange=EXCHANGE_NAME,
            routing_key=ROUTING_KEY,
            body=body,
            properties=pika.BasicProperties(
                content_type="application/json",
                delivery_mode=pika.DeliveryMode.Persistent,
                message_id=message_id,
                timestamp=int(time.time()),
                headers={"schema": "report.generate.v1"},
            ),
            mandatory=True,
        )

    print(f"published job_id={message_id}")


if __name__ == "__main__":
    publish_task(
        {
            "user_id": "user-123",
            "report_type": "monthly_statement",
            "parameters": {"month": "2026-05"},
        }
    )
```

### `worker.py`

```python
"""
RabbitMQ Task Worker
====================

Consumes durable JSON jobs and acknowledges only after successful processing.
Failed jobs are rejected without requeue so RabbitMQ can route them to a DLQ
when dead-lettering is configured.
"""

from __future__ import annotations

import json
import logging
import os
import random
import time
from typing import Any, Dict

import pika


LOGGER = logging.getLogger("report-worker")

QUEUE_NAME = "report.tasks"
EXCHANGE_NAME = "report.exchange"
ROUTING_KEY = "report.generate"
DLX_NAME = "report.dlx"
DLQ_NAME = "report.tasks.dlq"


class PermanentJobError(Exception):
    pass


class TemporaryJobError(Exception):
    pass


def connect() -> pika.BlockingConnection:
    params = pika.URLParameters(
        os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
    )
    params.heartbeat = 30
    params.blocked_connection_timeout = 60
    return pika.BlockingConnection(params)


def declare_topology(channel: pika.channel.Channel) -> None:
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type="direct", durable=True)
    channel.exchange_declare(exchange=DLX_NAME, exchange_type="direct", durable=True)

    channel.queue_declare(
        queue=QUEUE_NAME,
        durable=True,
        arguments={
            "x-dead-letter-exchange": DLX_NAME,
            "x-dead-letter-routing-key": "report.failed",
        },
    )
    channel.queue_bind(queue=QUEUE_NAME, exchange=EXCHANGE_NAME, routing_key=ROUTING_KEY)

    channel.queue_declare(queue=DLQ_NAME, durable=True)
    channel.queue_bind(queue=DLQ_NAME, exchange=DLX_NAME, routing_key="report.failed")


def generate_report(task: Dict[str, Any]) -> None:
    if "job_id" not in task or "user_id" not in task:
        raise PermanentJobError("missing required job_id or user_id")

    # Replace with real report generation. This is deliberately idempotent:
    # output should be written using job_id as a unique key.
    LOGGER.info("generating report job_id=%s user_id=%s", task["job_id"], task["user_id"])
    time.sleep(random.uniform(0.2, 1.0))


def on_message(channel, method, properties, body: bytes) -> None:
    try:
        task = json.loads(body.decode("utf-8"))
        generate_report(task)
    except json.JSONDecodeError:
        LOGGER.exception("invalid JSON; sending to DLQ")
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    except PermanentJobError:
        LOGGER.exception("permanent job failure; sending to DLQ")
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    except TemporaryJobError:
        LOGGER.exception("temporary job failure; requeueing")
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
    except Exception:
        LOGGER.exception("unknown failure; sending to DLQ to avoid poison loop")
        channel.basic_reject(delivery_tag=method.delivery_tag, requeue=False)
    else:
        channel.basic_ack(delivery_tag=method.delivery_tag)


def main() -> None:
    logging.basicConfig(level=logging.INFO)

    connection = connect()
    channel = connection.channel()
    declare_topology(channel)

    # Fair dispatch: do not send a worker more than one unacked job at a time.
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)

    LOGGER.info("worker waiting for tasks")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        LOGGER.info("shutdown requested")
        channel.stop_consuming()
    finally:
        connection.close()


if __name__ == "__main__":
    main()
```

### Why Acknowledgments Prevent Data Loss

| Event | Broker Behavior |
|---|---|
| Worker succeeds and acks | Message is removed |
| Worker crashes before ack | Message is redelivered |
| Worker rejects without requeue | Message goes to DLQ if configured |
| Worker nacks with requeue | Message becomes available again |

Acknowledgments do not prevent duplicate processing. They prevent silent loss.

---

## 11. Dead Letter Queues

A **Dead Letter Queue (DLQ)** stores messages that cannot be processed successfully.

Messages should go to a DLQ when:

- Payload is invalid.
- Required referenced data does not exist.
- Retries are exhausted.
- Consumer code repeatedly fails.
- Message violates schema.
- Downstream rejects it permanently.

### DLQ Design Rules

| Rule | Why |
|---|---|
| Include failure reason | Makes repair possible |
| Preserve original payload | Allows replay after fix |
| Track retry count | Prevents infinite poison-message loops |
| Alert on DLQ growth | DLQ is a production signal, not a trash bin |
| Build replay tooling | Operators need safe repair paths |
| Separate temporary and permanent failures | Avoid retrying messages that can never succeed |

---

## 12. Exponential Backoff And Retry Wrapper

Retries should be bounded, delayed, and jittered.

```python
"""
Retry wrapper with exponential backoff and jitter.

Use this around transient downstream calls inside workers. Keep job-level retry
state in the message headers or payload so retries remain visible and bounded.
"""

from __future__ import annotations

import functools
import random
import time
from typing import Callable, Iterable, Type, TypeVar


T = TypeVar("T")


def retry_with_backoff(
    *,
    retry_on: Iterable[Type[BaseException]],
    max_attempts: int = 5,
    base_delay_seconds: float = 0.25,
    max_delay_seconds: float = 10.0,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    retryable = tuple(retry_on)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            attempt = 1
            while True:
                try:
                    return func(*args, **kwargs)
                except retryable:
                    if attempt >= max_attempts:
                        raise

                    exponential_delay = min(
                        max_delay_seconds,
                        base_delay_seconds * (2 ** (attempt - 1)),
                    )
                    sleep_for = random.uniform(0, exponential_delay)
                    time.sleep(sleep_for)
                    attempt += 1

        return wrapper

    return decorator


class PaymentTimeout(Exception):
    pass


@retry_with_backoff(retry_on=[PaymentTimeout], max_attempts=4)
def call_payment_provider(order_id: str) -> None:
    # Replace with real API call.
    raise PaymentTimeout(f"payment provider timed out for order_id={order_id}")
```

### Retry Placement

| Retry Location | Use When | Risk |
|---|---|---|
| **Inside worker** | Fast transient dependency errors | Worker slot stays occupied |
| **Broker delayed retry queue** | Longer backoff windows | More topology complexity |
| **Scheduler-based replay** | Large failures or manual repair | Slower recovery |
| **No retry, DLQ immediately** | Permanent validation errors | Requires repair workflow |

---

## 13. Black Friday Design Scenario

Imagine an e-commerce order engine at midnight on Black Friday.

Traffic increases by 10,000 percent. Users can browse, add items to cart, and attempt checkout. The payment provider slows down.

### Architecture Walkthrough

| Stage | Design Choice | Protection |
|---|---|---|
| 1 | Web/API servers stay stateless | Scale horizontally for connection volume |
| 2 | Checkout validates and creates pending order | User intent is durably recorded |
| 3 | Order event is published to broker | Payment work is decoupled from request |
| 4 | User receives `202 Accepted` or pending status | User is not blocked on bank latency |
| 5 | Payment workers consume queue | Worker pool scales independently |
| 6 | Broker tracks backlog | Operators see queue depth and message age |
| 7 | Payment provider slows | Workers stall but web layer remains alive |
| 8 | Backpressure activates | New checkouts are slowed or rejected before collapse |
| 9 | Retries use backoff and jitter | Recovering provider is not hammered |
| 10 | Failed poison jobs go to DLQ | Bad messages do not block the queue |

### Core Lesson

The queue is not just a buffer. It is a **failure boundary**.

It lets browsing, carts, checkout intake, payment processing, email, analytics, and inventory scale and fail independently.

---

## 14. Interview Checklist

When designing an async system, ask:

| Question | Why It Matters |
|---|---|
| What is the business meaning of one message? | Defines idempotency and retry safety |
| Is this task queue or pub/sub? | Determines consumer model |
| What is the delivery guarantee? | Shapes duplicate handling |
| Where is the durable state written first? | Prevents lost intent |
| How are consumers made idempotent? | Required for at-least-once delivery |
| What happens when workers are slower than producers? | Backpressure plan |
| What goes to the DLQ? | Poison message isolation |
| How are retries delayed and bounded? | Prevents retry storms |
| What metrics page an operator? | Queue depth, message age, retry rate, DLQ growth |
| How is ordering scoped? | Usually per key or partition, not global |

---

## Mock Questions

<details>
<summary>How do message queues protect an overloaded backend?</summary>

Queues decouple the rate of incoming requests from the rate of backend processing. The application can accept work quickly, persist a message, and let workers process the backlog at a controlled rate.

When the backend slows down, queue depth and message age rise. Backpressure should then limit producers, reduce intake, or return `429`/`503` before broker memory and downstream databases collapse.

The queue protects the backend only if it is bounded, durable, monitored, and paired with idempotent consumers.

</details>

<details>
<summary>Why does at-least-once delivery require idempotent consumers?</summary>

At-least-once delivery means the broker will redeliver a message if it cannot prove processing completed. A worker might finish the business operation and then crash before acknowledging the message.

The broker will deliver the same message again. Without idempotency, the system might charge a card twice, send duplicate emails, or reserve inventory twice.

Use idempotency keys, unique database constraints, processed-message records, and state transitions so duplicate deliveries do not create duplicate business effects.

</details>

<details>
<summary>When should a message go to a Dead Letter Queue?</summary>

A message should go to a DLQ when it cannot be processed safely by normal retries.

Examples include invalid JSON, schema violations, missing required fields, permanently rejected downstream operations, or retry exhaustion.

The DLQ should preserve the original payload and failure reason. It should trigger alerts and support safe replay after the underlying bug or data issue is fixed.

</details>

<details>
<summary>What are the trade-offs of queues versus pub/sub?</summary>

Queues are best for distributing work where one task should be handled by one worker. They are natural for background jobs, report generation, image processing, and payment tasks.

Pub/sub is best when one event should notify many systems. It is natural for event-driven architecture, analytics, projections, and audit pipelines.

Queues simplify task ownership. Pub/sub improves decoupling and fanout, but subscribers must each manage their own replay, idempotency, and failure behavior.

</details>
