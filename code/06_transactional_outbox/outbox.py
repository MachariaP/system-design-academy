import time
import threading
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class OutboxMessage:
    id: str
    payload: str
    status: str = "PENDING"
    created_at: float = field(default_factory=time.monotonic)


class TransactionalOutbox:
    """In-memory transactional outbox with polling publisher."""

    def __init__(self) -> None:
        self._messages: dict[str, OutboxMessage] = {}
        self._lock = threading.Lock()

    def publish(self, message_id: str, payload: str) -> None:
        """Publish a new message in PENDING state."""
        with self._lock:
            msg = OutboxMessage(id=message_id, payload=payload)
            self._messages[message_id] = msg

    def poll_batch(self, batch_size: int = 10) -> list[OutboxMessage]:
        """Return up to batch_size PENDING messages ordered by creation time."""
        with self._lock:
            pending = sorted(
                [m for m in self._messages.values() if m.status == "PENDING"],
                key=lambda m: m.created_at,
            )
            return pending[:batch_size]

    def mark_processed(self, message_id: str) -> None:
        """Transition a message to PROCESSED state."""
        with self._lock:
            msg = self._messages.get(message_id)
            if msg is not None:
                msg.status = "PROCESSED"

    def get_message(self, message_id: str) -> Optional[OutboxMessage]:
        """Return a message by ID."""
        return self._messages.get(message_id)
