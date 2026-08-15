from datetime import datetime, timezone

from noesis_core import Ledger, Node, NodeRegistry, coherence


def test_reference_frequency_is_perfectly_coherent():
    assert coherence(141.7001) == 1.0


def test_node_registry_heartbeat():
    registry = NodeRegistry()
    registry.register(Node("N1"))
    registry.heartbeat("N1", datetime(2026, 1, 1, tzinfo=timezone.utc))
    assert registry.online_count() == 1
    assert registry.get("N1").online is True


def test_ledger_is_hash_chained_and_verifiable():
    ledger = Ledger()
    ledger.append("boot", {"node": "N1"}, timestamp="2026-01-01T00:00:00+00:00")
    ledger.append("heartbeat", {"node": "N1"}, timestamp="2026-01-01T00:01:00+00:00")
    assert ledger.verify() is True
