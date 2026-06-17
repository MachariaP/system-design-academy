from __future__ import annotations
from collections import defaultdict
from typing import Any, Optional


class Channel:
    """Unbuffered FIFO channel between two nodes."""

    def __init__(self) -> None:
        self._messages: list = []

    def send(self, msg: Any) -> None:
        self._messages.append(msg)

    def recv_all(self) -> list:
        msgs = list(self._messages)
        self._messages.clear()
        return msgs

    def peek_all(self) -> list:
        return list(self._messages)

    def is_empty(self) -> bool:
        return len(self._messages) == 0


class Snapshot:
    """Consistent global snapshot recorded via Chandy-Lamport markers."""

    def __init__(self, local_states: dict[str, Any],
                 channel_states: dict[tuple[str, str], list]) -> None:
        self.local_states = local_states
        self.channel_states = channel_states


class Node:
    """A process in the Chandy-Lamport snapshot algorithm."""

    def __init__(self, node_id: str, initial_state: Any) -> None:
        self.id = node_id
        self.state = initial_state
        self.out_channels: dict[str, Channel] = {}

    def connect(self, peer_id: str, channel: Channel) -> None:
        self.out_channels[peer_id] = channel

    @staticmethod
    def run_chandy_lamport(nodes: list[Node],
                           channels: dict[tuple[str, str], Channel]) -> Optional[Snapshot]:
        """Run the Chandy-Lamport algorithm to get a consistent snapshot."""
        if not nodes:
            return None
        initiator = nodes[0]

        local_snapshots: dict[str, Any] = {}
        channel_markers: dict[str, bool] = defaultdict(bool)
        channel_states: dict[tuple[str, str], list] = {}
        recorded_channels: set[tuple[str, str]] = set()

        queue = [initiator]

        while queue:
            node = queue.pop(0)
            if node.id in local_snapshots:
                continue

            local_snapshots[node.id] = node.state

            for peer_id, chan in node.out_channels.items():
                edge = (node.id, peer_id)
                if not channel_markers.get(str(edge)):
                    channel_markers[str(edge)] = True
                    msgs = chan.peek_all()
                    if msgs:
                        channel_states[edge] = msgs
                    recorded_channels.add(edge)
                    marker_msg = ("MARKER", node.id)
                    chan.send(marker_msg)

        for node in nodes:
            if node.id not in local_snapshots:
                local_snapshots[node.id] = node.state

        return Snapshot(local_states=local_snapshots,
                        channel_states=channel_states)
