import json
from noesis_core.ecosystem import EcosystemRuntime
from noesis_core.events import make_event
from noesis_core.resonance import coherence

def test_runtime_discovers_registered_ecosystem():
    rt=EcosystemRuntime(); data=rt.discover()
    assert data["reference"]["f0_hz"] == 141.7001
    assert len(data["nodes"]) >= 1

def test_resonance_reference_is_unity():
    assert coherence(141.7001, 141.7001) == 1.0

def test_event_is_deterministically_serializable():
    e=make_event("bus.sync","test",{"nodes":34},timestamp="2026-01-01T00:00:00+00:00")
    assert json.loads(e.to_json())["protocol"] == "noesis-event"
    assert len(e.digest) == 64
