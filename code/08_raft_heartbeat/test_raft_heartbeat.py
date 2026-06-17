from __future__ import annotations
from raft_heartbeat import RaftNode, Role


def make_node(node_id: str, peer_ids: list[str] | None = None) -> RaftNode:
    now = [0.0]
    peers = peer_ids or []
    return RaftNode(node_id, peers, election_timeout=5.0, now_fn=lambda: now[0]), now


def test_single_node_becomes_leader() -> None:
    node, now = make_node("n1")
    assert node.role == Role.FOLLOWER
    now[0] += 6.0
    result = node.tick()
    assert result == "elect"
    assert node.role == Role.LEADER
    assert node.term == 1


def test_follower_does_not_elect_within_timeout() -> None:
    node, now = make_node("n1")
    now[0] += 4.0
    result = node.tick()
    assert result is None
    assert node.role == Role.FOLLOWER


def test_three_node_cluster_elects_leader() -> None:
    n1, t1 = make_node("n1", ["n2", "n3"])
    n2, t2 = make_node("n2", ["n1", "n3"])
    n3, t3 = make_node("n3", ["n1", "n2"])

    t1[0] += 6.0
    n1.tick()
    assert n1.role == Role.CANDIDATE

    assert n2.request_vote("n1", n1.term)
    assert n3.request_vote("n1", n1.term)

    assert n1.receive_vote("n2")
    assert n1.role == Role.LEADER
    assert n1.leader_id == "n1"


def test_leader_heartbeats_prevent_election() -> None:
    n1, t1 = make_node("n1", ["n2"])
    n2, t2 = make_node("n2", ["n1"])

    t1[0] += 6.0
    n1.tick()
    assert n1.role == Role.CANDIDATE
    n2.request_vote("n1", n1.term)
    n1.receive_vote("n2")
    assert n1.role == Role.LEADER

    n1.send_heartbeat("n2")
    n2.receive_append_entries("n1", n1.term)

    t2[0] += 4.0
    result = n2.tick()
    assert result is None
    assert n2.role == Role.FOLLOWER
    assert n2.leader_id == "n1"


def test_higher_term_overrides_current() -> None:
    n1, t1 = make_node("n1", ["n2"])
    n2, t2 = make_node("n2", ["n1"])

    n1.term = 5
    n1.role = Role.LEADER

    n1.receive_append_entries("n2", 6)
    assert n1.term == 6
    assert n1.role == Role.FOLLOWER


def test_deny_vote_for_lower_term() -> None:
    n1, _ = make_node("n1")
    n1.term = 10
    granted = n1.request_vote("n2", 5)
    assert not granted


def test_leader_sends_heartbeat_to_all_peers() -> None:
    n1, t1 = make_node("n1", ["n2", "n3"])
    n2, t2 = make_node("n2", ["n1", "n3"])
    n3, t3 = make_node("n3", ["n1", "n2"])

    t1[0] += 6.0
    n1.tick()
    n2.request_vote("n1", n1.term)
    n1.receive_vote("n2")
    n3.request_vote("n1", n1.term)
    n1.receive_vote("n3")

    assert n1.role == Role.LEADER
    n2.receive_append_entries("n1", n1.term)
    assert n2.leader_id == "n1"
    assert n2.role == Role.FOLLOWER


def test_vote_once_per_term() -> None:
    n1, t1 = make_node("n1", ["n2", "n3"])
    t1[0] += 6.0
    n1.tick()
    assert n1.request_vote("n2", 2)
    assert not n1.request_vote("n3", 2)
