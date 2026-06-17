from __future__ import annotations
import time
from enum import Enum
from typing import Callable, Optional


class Role(Enum):
    FOLLOWER = 0
    CANDIDATE = 1
    LEADER = 2


class RaftNode:
    """Simplified Raft node with leader election and heartbeat (AppendEntries)."""

    def __init__(self, node_id: str, peers: list[str],
                 election_timeout: float,
                 now_fn: Optional[Callable[[], float]] = None) -> None:
        self.id = node_id
        self.peers = peers
        self.election_timeout = election_timeout
        self._now = now_fn or time.monotonic

        self.role: Role = Role.FOLLOWER
        self.term: int = 0
        self.voted_for: Optional[str] = None
        self.leader_id: Optional[str] = None
        self.last_heartbeat: float = self._now()

        self._votes_received: set[str] = set()

    def tick(self) -> Optional[str]:
        """Called periodically. Returns 'elect' if election starts."""
        if self.role == Role.LEADER:
            return None
        if self._now() - self.last_heartbeat >= self.election_timeout:
            self.start_election()
            return "elect"
        return None

    def start_election(self) -> None:
        """Transition to CANDIDATE, increment term, request votes."""
        self.role = Role.CANDIDATE
        self.term += 1
        self.voted_for = self.id
        self._votes_received = {self.id}
        self.last_heartbeat = self._now()
        self.receive_vote(self.id)

    def request_vote(self, candidate_id: str, candidate_term: int) -> bool:
        """Handle a RequestVote RPC. Returns True if vote granted."""
        if candidate_term < self.term:
            return False
        if candidate_term > self.term:
            self.term = candidate_term
            self.role = Role.FOLLOWER
            self.voted_for = None
        if self.voted_for is None or self.voted_for == candidate_id:
            self.voted_for = candidate_id
            self.last_heartbeat = self._now()
            return True
        return False

    def receive_vote(self, voter_id: str) -> bool:
        """Register a vote for this candidate. Returns True if won election."""
        if self.role != Role.CANDIDATE:
            return False
        self._votes_received.add(voter_id)
        majority = (len(self.peers) + 1) // 2 + 1
        if len(self._votes_received) >= majority:
            self.role = Role.LEADER
            self.leader_id = self.id
            for peer in self.peers:
                self.send_heartbeat(peer)
            return True
        return False

    def send_heartbeat(self, peer_id: str | None = None) -> None:
        """Send AppendEntries (heartbeat) to all or a specific peer."""
        if self.role != Role.LEADER:
            return
        targets = [peer_id] if peer_id else self.peers
        for _ in targets:
            pass

    def receive_append_entries(self, leader_id: str, leader_term: int) -> bool:
        """Handle an AppendEntries RPC from a leader. Returns True if accepted."""
        if leader_term < self.term:
            return False
        if leader_term > self.term:
            self.term = leader_term
            self.role = Role.FOLLOWER
            self.voted_for = None
        self.leader_id = leader_id
        self.last_heartbeat = self._now()
        return True
