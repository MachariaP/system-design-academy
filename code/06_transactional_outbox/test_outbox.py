import pytest
from outbox import TransactionalOutbox


class TestTransactionalOutbox:
    def test_publish_and_poll(self):
        outbox = TransactionalOutbox()
        outbox.publish("1", "hello")
        batch = outbox.poll_batch()
        assert len(batch) == 1
        assert batch[0].id == "1"
        assert batch[0].status == "PENDING"

    def test_poll_returns_none_when_all_processed(self):
        outbox = TransactionalOutbox()
        outbox.publish("1", "data")
        outbox.mark_processed("1")
        assert outbox.poll_batch() == []

    def test_mark_processed(self):
        outbox = TransactionalOutbox()
        outbox.publish("1", "data")
        outbox.mark_processed("1")
        msg = outbox.get_message("1")
        assert msg is not None
        assert msg.status == "PROCESSED"

    def test_batch_size(self):
        outbox = TransactionalOutbox()
        for i in range(20):
            outbox.publish(str(i), f"payload{i}")
        assert len(outbox.poll_batch(batch_size=5)) == 5
        assert len(outbox.poll_batch(batch_size=10)) == 10

    def test_order_by_creation(self):
        outbox = TransactionalOutbox()
        outbox.publish("a", "first")
        outbox.publish("b", "second")
        batch = outbox.poll_batch(2)
        assert [m.id for m in batch] == ["a", "b"]
