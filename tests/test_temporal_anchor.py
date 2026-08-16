from noesis_core.temporal_memory import RestorationPoint
from noesis_core.temporal_anchor import TemporalAnchor, LocalAnchor


def test_local_anchor_is_durable(tmp_path):
    path = tmp_path / "anchors.jsonl"
    anchor = TemporalAnchor(LocalAnchor(path))
    point = RestorationPoint(1, "2026-08-15T00:00:00+00:00", "abc", "healthy", "heartbeat", "ledger")
    anchor_id = anchor.create(point)
    assert len(anchor_id) == 64
    assert path.exists()
    assert anchor_id in path.read_text()
