"""Ecosystem runtime: discovery, liveness, provenance and temporal memory."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
from .adapters import QCALBusAdapter, Noesis88Adapter
from .provenance import VerificationRecord
from .events import make_event
from .persistent_ledger import PersistentLedger
from .temporal_memory import TemporalMemory

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "ecosystem_registry.json"
STATE_DIR = ROOT / ".noesis"

@dataclass(frozen=True)
class EcosystemNode:
    id: str; repo: str; role: str; protocols: tuple[str, ...] = ()

class EcosystemRuntime:
    def __init__(self, registry: Path | str = REGISTRY, state_dir: Path | str = STATE_DIR):
        self.registry_path = Path(registry)
        self.config = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.state_dir = Path(state_dir)
        self.ledger = PersistentLedger(self.state_dir / "ledger.jsonl")
        self.temporal_memory = TemporalMemory(self.state_dir / "temporal_memory.jsonl")
    @property
    def reference(self): return self.config["reference"]
    def nodes(self):
        return [EcosystemNode(x["id"], x["repo"], x.get("role", "unknown"), tuple(x.get("protocols", []))) for x in self.config["repositories"]]
    def discover(self):
        return {"schema": self.config["schema"], "reference": self.reference, "nodes": [n.__dict__ for n in self.nodes()]}
    def bus(self): return QCALBusAdapter()
    def noesis88(self): return Noesis88Adapter()
    def health(self):
        from .health import HealthMonitor
        return HealthMonitor(self).check()
    def status(self):
        result = {"reference": self.reference, "configured_nodes": len(self.nodes()), "services": {}}
        b = self.bus(); bs, bc = b.state(), b.catalog()
        result["services"]["qcal_bus"] = {"state": bs.__dict__, "catalog": bc.__dict__}
        n = self.noesis88(); nc, ns = n.central(), n.servers()
        result["services"]["noesis88"] = {"central": nc.__dict__, "servers": ns.__dict__}
        self.ledger.append("bus.sync", {"configured_nodes": result["configured_nodes"], "qcal_bus_ok": bs.ok, "noesis88_ok": nc.ok})
        return result
    def verify(self):
        records=[]
        for node in self.nodes():
            records.append(VerificationRecord(node.repo, "registry", "ecosystem_registry", "observed", {"registered": True, "role": node.role, "protocols": list(node.protocols)}).to_dict())
        self.ledger.append("verification.record", {"count": len(records)})
        return records
    def resonance_event(self, frequency_hz: float, coherence_value: float | None = None):
        from .resonance import coherence
        c = coherence_value if coherence_value is not None else coherence(frequency_hz, self.reference["f0_hz"])
        event = make_event("resonance.measurement", "noesis", {"frequency_hz": frequency_hz, "coherence": c, "reference_hz": self.reference["f0_hz"]})
        self.ledger.append(event.event_type, event.to_dict())
        return event
    def snapshot(self):
        from .snapshot import Snapshot
        snapshot = Snapshot(self).capture()
        point = self.temporal_memory.record(snapshot, "captured", "ecosystem.snapshot", self.ledger.events[-1].hash if self.ledger.events else None)
        snapshot["temporal_memory"] = {"sequence": point.sequence, "fingerprint": point.fingerprint, "restoration_point": True}
        return snapshot
    def temporal_status(self):
        latest = self.temporal_memory.latest
        return {"records": len(self.temporal_memory.points), "latest": None if latest is None else latest.__dict__, "integrity": self.temporal_memory.verify(), "ledger_integrity": self.ledger.verify()}
