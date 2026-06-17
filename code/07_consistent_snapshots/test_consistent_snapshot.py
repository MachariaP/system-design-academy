import pytest
from consistent_snapshot import Node, Channel, Snapshot


class TestConsistentSnapshot:
    def test_single_node_snapshot(self):
        node = Node("A", {"balance": 100})
        channels: dict = {}
        result = Node.run_chandy_lamport([node], channels)
        assert result is not None
        assert result.local_states == {"A": {"balance": 100}}

    def test_three_node_cluster(self):
        a = Node("A", {"count": 1})
        b = Node("B", {"count": 2})
        c = Node("C", {"count": 3})
        ch_ab = Channel()
        ch_bc = Channel()
        ch_ca = Channel()
        a.connect("B", ch_ab)
        b.connect("C", ch_bc)
        c.connect("A", ch_ca)
        nodes = [a, b, c]
        channels = {("A", "B"): ch_ab, ("B", "C"): ch_bc, ("C", "A"): ch_ca}
        result = Node.run_chandy_lamport(nodes, channels)
        assert result.local_states["A"] == {"count": 1}
        assert result.local_states["B"] == {"count": 2}
        assert result.local_states["C"] == {"count": 3}

    def test_captures_in_flight_messages(self):
        a = Node("A", {"x": 10})
        b = Node("B", {"x": 20})
        ch_ab = Channel()
        ch_ab.send("MSG1")
        ch_ab.send("MSG2")
        a.connect("B", ch_ab)
        nodes = [a, b]
        channels = {("A", "B"): ch_ab}
        result = Node.run_chandy_lamport(nodes, channels)
        assert ("A", "B") in result.channel_states

    def test_all_local_states_recorded(self):
        nodes = [
            Node("X", 100),
            Node("Y", 200),
            Node("Z", 300),
        ]
        channels: dict = {}
        result = Node.run_chandy_lamport(nodes, channels)
        assert set(result.local_states.keys()) == {"X", "Y", "Z"}
