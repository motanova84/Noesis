import json
from noesis_core.ecosystem import EcosystemRuntime
from noesis_core.events import make_event
from noesis_core.provenance import VerificationRecord
from noesis_core.resonance import coherence
from noesis_cli.__main__ import main

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

def test_provenance_is_hashed():
    record = VerificationRecord("example/repo", "README.md", "documentation", "claimed", {"x": 1})
    assert len(record.digest) == 64

def test_health_is_explicit_when_services_are_absent():
    result = EcosystemRuntime().health()
    assert result["status"] in {"healthy", "degraded"}
    assert "qcal_bus" in result["checks"]

def test_cli_nodes():
    assert main(["nodes"]) == 0
