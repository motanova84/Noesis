"""Ecosystem runtime: discover configured nodes, query native adapters, and emit provenance."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import json, os, subprocess
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
    def nodes(self) -> list[EcosystemNode]:
        return [EcosystemNode(x["id"], x["repo"], x.get("role", "unknown"), tuple(x.get("protocols", []))) for x in self.config["repositories"]]
    def discover(self) -> dict:
        return {"schema": self.config["schema"], "reference": self.reference, "nodes": [n.__dict__ for n in self.nodes()]}
    def bus(self): return QCALBusAdapter()
    def noesis88(self): return Noesis88Adapter()
    def status(self) -> dict:
        result = {"reference": self.reference, "configured_nodes": len(self.nodes()), "services": {}}
        b = self.bus(); result["services"]["qcal_bus"] = {"state": b.state().__dict__, "catalog": b.catalog().__dict__}
        n = self.noesis88(); result["services"]["noesis88"] = {"central": n.central().__dict__, "servers": n.servers().__dict__}
        self.ledger.append("bus.sync", {"configured_nodes": result["configured_nodes"]})
        return result
    def verify(self) -> list[dict]:
        records=[]
        for node in self.nodes():
            status = "observed"
            result = {"registered": True, "role": node.role, "protocols": list(node.protocols)}
            records.append(VerificationRecord(node.repo, "registry", "ecosystem_registry", status, result).to_dict())
        self.ledger.append("verification.record", {"count": len(records)})
        return records
    def resonance_event(self, frequency_hz: float, coherence_value: float | None = None):
        from .resonance import coherence
        c = coherence_value if coherence_value is not None else coherence(frequency_hz, self.reference["f0_hz"])
        event = make_event("resonance.measurement", "noesis", {"frequency_hz": frequency_hz, "coherence": c, "reference_hz": self.reference["f0_hz"]})
        self.ledger.append(event.event_type, event.to_dict())
        return event
