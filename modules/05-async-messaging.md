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

### Visual Lifecycle: `OrderPlaced`

This sequence shows the operational life of a message, including visibility timeout, acknowledgments, failure routing, and replay.

```mermaid
sequenceDiagram
    autonumber
    participant Client
    participant API as Order API
    participant Broker as Broker / Queue
    participant Worker as Payment Worker
    participant DLQ as Dead Letter Queue
    participant Ops as Operator / Replay Tool

    Client->>API: POST /orders
    API->>API: validate request<br/>create order_id
    API->>Broker: publish OrderPlaced<br/>message_id=uuid
    Broker-->>API: publisher confirm
    API-->>Client: 202 Accepted<br/>order_status=pending

    Broker->>Worker: deliver message<br/>visibility timeout starts
    Worker->>Worker: process payment
    alt success before visibility timeout
        Worker->>Broker: ack
        Broker->>Broker: remove message
    else transient failure
        Worker->>Broker: nack requeue=true
        Broker->>Broker: make message visible again
        Broker->>Worker: redeliver message<br/>delivery_count += 1
    else worker crashes or timeout expires
        Broker->>Broker: visibility timeout expires
        Broker->>Worker: redeliver message
    else retries exhausted or permanent failure
        Worker->>Broker: reject / nack requeue=false
        Broker->>DLQ: route to DLQ<br/>preserve payload + headers
        DLQ-->>Ops: alert: DLQ size > 0
        Ops->>DLQ: inspect and repair payload/code
        Ops->>Broker: replay fixed OrderPlaced
        Broker->>Worker: deliver replayed message
    end
```

The key rule is simple: a message should be removed only after the business effect is safely committed. If the worker cannot prove that, the broker should redeliver or isolate the message.

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

### Decision Matrix

| Requirement | Prefer Queue | Prefer Pub/Sub / Stream |
|---|---|---|
| **One task processed once** | Use a queue such as SQS, RabbitMQ, or Celery so one worker claims one task | Avoid plain broadcast unless each subscriber has its own dedupe and task ownership |
| **Multiple independent reactions** | Use separate queues only if each reaction is a separate task pipeline | Use SNS fanout, RabbitMQ exchanges, Kafka, or Pulsar so payment, inventory, email, and analytics all receive the same event |
| **Replayability** | Traditional queues are awkward after ack; replay usually means re-enqueueing from storage or DLQ | Log systems such as Kafka make replay natural by resetting offsets or starting a new consumer group |
| **Ordering guarantee** | Usually per queue, FIFO queue, or shard; strict ordering limits parallelism | Usually per partition or message group; global ordering is expensive |
| **Latency** | SQS is managed but often higher latency; RabbitMQ is low-latency for task dispatch | SNS is fast fanout; Kafka is high-throughput and durable but adds batching and commit behavior |

### Tool Examples

| Pair | Queue Shape | Pub/Sub Shape |
|---|---|---|
| **SQS vs. SNS** | SQS gives each message to one consumer in a queue; use it for jobs | SNS broadcasts one event to many subscriptions; often SNS fans out into many SQS queues |
| **RabbitMQ vs. Kafka** | RabbitMQ is excellent for routed work queues, acknowledgments, TTLs, and DLQs | Kafka is a durable ordered log with partitions, offsets, replay, and consumer groups |

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

### Kafka Transactions: What "Exactly Once" Really Means

Kafka's exactly-once semantics are strongest when the application consumes from Kafka, writes output back to Kafka, and commits consumed offsets in the same transaction.

Conceptual flow:

```python
# Pseudocode: Kafka consume-process-produce transaction.

producer.init_transactions()

while True:
    records = consumer.poll(timeout_ms=1000)
    if not records:
        continue

    producer.begin_transaction()
    try:
        for record in records:
            output = transform(record.value)
            producer.send(
                "order-projections",
                key=record.key,
                value=output,
            )

        producer.send_offsets_to_transaction(
            offsets=consumer.current_offsets(),
            consumer_group_id="order-projector-v1",
        )
        producer.commit_transaction()
    except Exception:
        producer.abort_transaction()
        raise
```

Consumers that set `isolation.level=read_committed` will not read aborted transactional output. This prevents a downstream Kafka consumer from seeing output records when the input offsets were not committed.

Important limits:

- Kafka transactions do not automatically make external databases, payment gateways, email providers, or REST APIs exactly-once.
- Transactions add coordination cost and require correct producer IDs, fencing, offset handling, and consumer isolation settings.
- They are most natural for Kafka-to-Kafka pipelines, stream processing, projections, and event enrichment.

### Practical Default: Idempotent Producer + Idempotent Consumer

A more common production design is:

| Layer | Practical Control |
|---|---|
| **Producer** | Use stable `message_id`, idempotency key, publisher confirms, and retry with dedupe |
| **Broker** | Expect at-least-once delivery and possible redelivery |
| **Consumer** | Store processed message IDs inside the same transaction as the business update |
| **External side effects** | Pass idempotency keys to providers when supported |

### Idempotent Consumer With A Unique Constraint

Use a unique constraint on `(message_id, consumer_id)` so duplicate deliveries become harmless.

```sql
CREATE TABLE processed_messages (
    message_id VARCHAR(128) NOT NULL,
    consumer_id VARCHAR(128) NOT NULL,
    processed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (message_id, consumer_id)
);
```

```python
from __future__ import annotations

import psycopg


CONSUMER_ID = "payment-worker-v1"


def handle_order_placed(conn: psycopg.Connection, message: dict) -> None:
    message_id = message["message_id"]
    order_id = message["order_id"]

    with conn.transaction():
        inserted = conn.execute(
            """
            INSERT INTO processed_messages (message_id, consumer_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING
            RETURNING message_id
            """,
            (message_id, CONSUMER_ID),
        ).fetchone()

        if inserted is None:
            return

        conn.execute(
            """
            UPDATE orders
            SET payment_status = 'captured'
            WHERE order_id = %s
              AND payment_status = 'pending'
            """,
            (order_id,),
        )
```

The dedupe insert and the business update happen in one transaction. If the worker crashes before commit, the broker can redeliver. If the worker commits but crashes before ack, the duplicate delivery is skipped.

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

### Propagation Diagram

```mermaid
flowchart LR
    Client["Clients"]
    API["API Layer<br/>accepts orders"]
    Producer["Producer<br/>publishes jobs"]
    Broker["Broker<br/>queue depth rising"]
    Consumer["Consumers<br/>payment workers"]
    DB["Downstream DB<br/>latency rising"]
    Scale["Autoscaler<br/>add workers if DB healthy"]
    Throttle["Broker / Gateway<br/>producer throttling"]
    Reject["API returns 429<br/>Retry-After header"]

    Client -->|"checkout requests"| API
    API --> Producer
    Producer -->|"publish OrderPlaced"| Broker
    Broker -->|"deliver jobs"| Consumer
    Consumer -->|"writes / reads"| DB

    DB -.->|"p99 latency spikes"| Consumer
    Consumer -.->|"ack rate falls"| Broker
    Broker -.->|"queue depth + message age rise"| Scale
    Broker -.->|"memory / depth threshold crossed"| Throttle
    Throttle -.->|"publish rate limited"| Producer
    Producer -.->|"cannot enqueue safely"| API
    API -.->|"shed load"| Reject
    Reject -.->|"client retries later"| Client
```

Backpressure is healthiest when it propagates before the broker is full. The API should know when the queue is no longer a safe place to put new work.

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

### Backpressure Escalation Policy

| Trigger | Action | User-Facing Result |
|---|---|---|
| DB p99 latency above threshold | Reduce worker concurrency | Existing backlog drains slowly, database recovers |
| Queue depth rising but DB healthy | Scale workers horizontally | Users see delayed completion, not failed intake |
| Queue depth and message age both rising | Throttle producers | API accepts fewer new jobs |
| Broker memory or disk alarm | Stop non-critical producers | Optional workflows pause |
| Queue is beyond safe limit | Return `429 Too Many Requests` or `503 Service Unavailable` | Clients retry with `Retry-After` |

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
    params.connection_attempts = 5
    params.retry_delay = 2
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


def publish_with_retry(payload: Dict[str, Any], *, max_attempts: int = 5) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            publish_task(payload)
            return
        except pika.exceptions.AMQPError:
            if attempt == max_attempts:
                raise
            time.sleep(min(10, 2 ** attempt))


if __name__ == "__main__":
    publish_with_retry(
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
    params.connection_attempts = 5
    params.retry_delay = 2
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

    while True:
        connection = None
        try:
            connection = connect()
            channel = connection.channel()
            declare_topology(channel)

            # Fair dispatch: do not send a worker more than one unacked job at a time.
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=on_message)

            LOGGER.info("worker waiting for tasks")
            channel.start_consuming()
        except KeyboardInterrupt:
            LOGGER.info("shutdown requested")
            if connection and connection.is_open:
                connection.close()
            break
        except pika.exceptions.AMQPError:
            LOGGER.exception("RabbitMQ connection failed; reconnecting soon")
            time.sleep(5)
        finally:
            if connection and connection.is_open:
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

### Publisher Confirms, Heartbeats, And Recovery

| Mechanism | Why It Matters |
|---|---|
| **Publisher confirms** | The producer waits for broker acceptance before treating the publish as successful. If confirm fails, retry with the same `message_id` so consumers can dedupe. |
| **Heartbeat** | The broker and client detect dead TCP connections instead of waiting forever. |
| **Connection retry** | Producers and workers survive broker restarts, rolling deploys, and short network interruptions. |
| **`blocked_connection_timeout`** | Prevents a producer from hanging forever when RabbitMQ blocks publishers due to memory or disk alarms. |

### Per-Queue Dead Letter Exchange

RabbitMQ dead-lettering is configured on the source queue, not on the consumer. The worker declares:

```python
arguments={
    "x-dead-letter-exchange": "report.dlx",
    "x-dead-letter-routing-key": "report.failed",
}
```

Any message rejected with `requeue=False`, expired by TTL, or dropped due to queue limits can then be routed to the DLX and into the DLQ.

### Docker Compose: RabbitMQ + Producer + Worker

```yaml
version: "3.9"

services:
  rabbitmq:
    image: rabbitmq:3.13-management
    ports:
      - "5672:5672"
      - "15672:15672"
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  worker:
    image: python:3.12-slim
    working_dir: /app
    volumes:
      - .:/app
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/%2F
    command: >
      sh -c "pip install pika &&
             python worker.py"
    depends_on:
      rabbitmq:
        condition: service_healthy

  producer:
    image: python:3.12-slim
    working_dir: /app
    volumes:
      - .:/app
    environment:
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/%2F
    command: >
      sh -c "pip install pika &&
             python producer.py"
    depends_on:
      rabbitmq:
        condition: service_healthy
```

Run the stack from a directory containing `producer.py`, `worker.py`, and `docker-compose.yml`:

```bash
docker compose up --build
```

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

### DLQ Workflow State Machine

```mermaid
stateDiagram-v2
    [*] --> InQueue
    InQueue --> Processing: worker receives message\nalert if message_age p99 high
    Processing --> [*]: success ack\nalert if ack_rate drops
    Processing --> RetryQueue: temporary failure\nalert if retry_rate spikes
    Processing --> DLQ: permanent failure\nalert immediately
    RetryQueue --> Processing: delay elapsed\nredelivery_count += 1
    RetryQueue --> DLQ: retries exhausted\nalert if exhausted_count > threshold
    DLQ --> ManualRepair: operator triage\nalert if DLQ age > SLA
    ManualRepair --> Replay: payload fixed or code deployed
    Replay --> Processing: re-enqueue with same message_id\nor new replay_id
```

### Alert Triggers

| Stage | Alert Trigger | Likely Meaning |
|---|---|---|
| **InQueue** | Queue depth or p99 message age exceeds SLA | Consumers are slow or producers are too fast |
| **Processing** | Ack rate falls while delivery rate stays high | Workers are stuck, crashing, or blocked downstream |
| **RetryQueue** | Retry rate jumps | Dependency instability or a bad deploy |
| **DLQ** | DLQ size greater than zero for critical workflows | Poison message, schema mismatch, or permanent downstream rejection |
| **Manual repair** | Oldest DLQ message exceeds repair SLA | Operational backlog needs escalation |
| **Replay** | Replayed messages fail again | Fix is incomplete or replay is unsafe |

### Replay Rules

| Rule | Reason |
|---|---|
| Replay into the normal queue only after the bug or data issue is fixed | Otherwise the DLQ loops forever |
| Preserve original `message_id` when consumers use dedupe | Prevents duplicate business effects |
| Add `replay_id` and `replayed_by` metadata | Gives operators an audit trail |
| Replay in batches with rate limits | Avoids overwhelming recovered dependencies |
| Watch DLQ and normal queue metrics during replay | Confirms that repair is working |

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

### Case Study: Checkout Surge

At 00:00:00, the sale opens. The checkout API normally handles 2,000 orders per minute with 10 payment workers. Each worker processes about 20 payment jobs per second when the payment provider is healthy.

At 00:00:30:

- Queue depth jumps from 0 to 10,000,000 messages.
- The oldest message age climbs from 0 seconds to 4 minutes.
- Payment provider p99 latency rises from 250 ms to 8 seconds.
- Worker ack rate falls while redelivery count climbs.
- A new payment webhook schema breaks 3 percent of jobs, sending them to the DLQ.

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

### Operational Response

| Time | Signal | Action |
|---|---|---|
| 00:00:10 | Queue depth crosses 1M | Autoscaler starts adding payment workers |
| 00:00:45 | Workers scale from 10 to 150 | Throughput rises, but provider latency remains high |
| 00:01:30 | DB p99 remains healthy, provider p99 improves | Autoscaler continues to 500 workers |
| 00:03:00 | DLQ grows to 300,000 messages | On-call disables the broken webhook subscriber and pages payments team |
| 00:08:00 | Queue depth stops rising | API removes emergency `429` for paid users, keeps rate limits for anonymous traffic |
| 00:20:00 | Bug fixed and deployed | Operators replay DLQ in 10,000-message batches |

### Why The System Survived

| Design Choice | Effect During The Incident |
|---|---|
| Orders were written before publishing | Customer intent was not lost even when payment lagged |
| Broker was durable and monitored | The team could see backlog size, age, and failure pattern |
| Workers were stateless | Scaling from 10 to 500 was operationally simple |
| Worker concurrency was capped per instance | The database did not collapse while the worker fleet grew |
| DLQ separated poison messages | Broken webhook payloads did not block valid payment jobs |
| Replay tooling existed before the sale | The team repaired and replayed bad messages without ad hoc scripts |

### Core Lesson

The queue is not just a buffer. It is a **failure boundary**.

It lets browsing, carts, checkout intake, payment processing, email, analytics, and inventory scale and fail independently.

---

## 14. Monitoring Checklist

Every async system needs metrics that show backlog, freshness, throughput, failure, and replay safety.

| Metric | What It Tells You | Alert Example |
|---|---|---|
| **Queue depth** | How many messages are waiting | Depth above normal baseline for 5 minutes |
| **Message age p99** | User-visible delay for queued work | p99 age greater than workflow SLA |
| **Redelivery count** | Duplicate deliveries and crash/timeout behavior | Redelivery rate suddenly doubles |
| **DLQ size** | Poison or exhausted messages | DLQ size > 0 for payments, orders, or security workflows |
| **Consumer lag** | How far a stream consumer is behind the head of the log | Lag grows while producers are steady |
| **Ack rate** | Successful processing throughput | Ack rate drops below expected capacity |
| **Nack rate** | Explicit processing failures | Nack rate spikes after deploy |
| **Retry queue depth** | Delayed transient failures | Retry depth grows faster than it drains |
| **Oldest DLQ message age** | Repair SLA health | Oldest DLQ message older than 30 minutes |
| **Worker concurrency** | Active processing pressure | Concurrency pinned at max while ack rate is low |
| **Downstream p99 latency** | Whether workers are blocked on dependencies | DB or provider p99 above backpressure threshold |
| **Producer publish failures** | Broker availability or throttling | Confirm failures or blocked publishes exceed threshold |

Dashboards should show queue depth and message age together. A deep queue with young messages may be a manageable burst; a moderate queue with old messages means users are waiting too long.

---

## 15. Interview Checklist

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

<details>
<summary>Design a system that runs millions of cron jobs per day, each may take from 1 second to 1 hour, with at-most-once or at-least-once guarantees.</summary>

Start with requirements:

- Millions of scheduled executions per day.
- Jobs vary from 1 second to 1 hour.
- Tenants may need isolation and rate limits.
- Some jobs are at-most-once, where skipping is better than duplicate execution.
- Some jobs are at-least-once, where retry is required and handlers must be idempotent.

High-level design:

```mermaid
flowchart LR
    API["Schedule API"]
    Store["Schedule Store<br/>job_id, cron, next_run_at"]
    Shards["Scheduler Shards<br/>claim due jobs"]
    Queue["Execution Queue"]
    Workers["Worker Fleet"]
    Lease["Lease Store<br/>run_id, expires_at"]
    Results["Run History<br/>status, duration, error"]
    DLQ["DLQ / Repair Queue"]

    API --> Store
    Shards -->|"scan by next_run_at"| Store
    Shards -->|"enqueue run_id"| Queue
    Queue --> Workers
    Workers --> Lease
    Workers --> Results
    Workers --> DLQ
    Workers -->|"compute next_run_at"| Store
```

Key components:

| Component | Responsibility |
|---|---|
| **Schedule store** | Durable source of truth for cron expression, timezone, owner, enabled flag, and next run time |
| **Scheduler shards** | Claim due schedules by shard key and enqueue execution messages |
| **Execution queue** | Buffer runnable jobs and absorb bursts at minute boundaries |
| **Lease store** | Prevent two workers from executing the same run concurrently |
| **Worker fleet** | Executes jobs with per-tenant concurrency and runtime limits |
| **Run history** | Stores status, timestamps, attempts, error, and output pointer |
| **DLQ** | Isolates invalid jobs, exhausted retries, and poison payloads |

Guarantee choices:

| Guarantee | Implementation | Trade-Off |
|---|---|---|
| **At-most-once** | Mark run as `started` before execution; do not retry after worker crash | May skip jobs during crashes |
| **At-least-once** | Enqueue run with lease; retry when lease expires or worker nacks | May run duplicates, so job handler needs idempotency |

Important details:

- Use `job_id` plus scheduled fire time to create a stable `run_id`.
- Partition schedules by `hash(job_id)` so scheduler shards do not fight over the whole table.
- Claim due schedules with a transactional compare-and-set on `next_run_at` or a lease.
- Use priority queues or separate queues for short, long, and tenant-isolated work.
- Do not let one-hour jobs occupy all workers; use separate pools or runtime classes.
- Track p99 scheduling delay: `actual_start_time - scheduled_time`.
- Put exhausted or invalid executions into a DLQ with enough context to repair and replay.
- For at-least-once jobs, require idempotency keys or a processed-run table in the target system.

The core interview answer is that the scheduler decides *when* work should run, but the queue and worker system decides *how fast* work can safely run.

</details>
