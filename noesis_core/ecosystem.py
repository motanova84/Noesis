"""Ecosystem runtime: discovery, liveness, provenance and snapshots."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json
from .adapters import QCALBusAdapter, Noesis88Adapter
from .provenance import VerificationRecord
from .events import make_event
from .ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "config" / "ecosystem_registry.json"

@dataclass(frozen=True)
class EcosystemNode:
    id: str; repo: str; role: str; protocols: tuple[str, ...] = ()

class EcosystemRuntime:
    def __init__(self, registry: Path | str = REGISTRY):
        self.registry_path = Path(registry)
        self.config = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.ledger = Ledger()
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
        return Snapshot(self).capture()
