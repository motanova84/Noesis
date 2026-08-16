import json

from noesis_core.bus import QCALBusClient
from noesis_core.events import make_event


def test_event_is_versioned_and_deterministic():
    event = make_event(
        "resonance.measurement",
        "test",
        {"frequency_hz": 141.7001, "coherence": 1.0},
        event_id="evt-1",
        timestamp="2026-01-01T00:00:00+00:00",
    )
    event.validate()
    assert event.version == "1.0"
    assert event.digest
    assert json.loads(event.to_json())["event_type"] == "resonance.measurement"


def test_bus_payload_uses_qcal_mcp_shape(monkeypatch):
    client = QCALBusClient("http://example.invalid")
    captured = {}

    def fake_call(method, params=None, request_id="noesis-1"):
        captured.update(method=method, params=params, request_id=request_id)
        return {"ok": True}

    monkeypatch.setattr(client, "call", fake_call)
    event = make_event("bus.sync", "test", {"reference_hz": 141.7001}, event_id="evt-2", timestamp="2026-01-01T00:00:00+00:00")
    result = client.publish_event(event)
    assert result == {"ok": True}
    assert captured["method"] == "events/publish"
    assert captured["params"]["event"]["protocol"] == "noesis-event"
    assert captured["params"]["digest"] == event.digest
