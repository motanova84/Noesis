"""Portable ecosystem snapshots with deterministic provenance."""
from __future__ import annotations
from datetime import datetime, timezone
import json

class Snapshot:
    def __init__(self, runtime): self.runtime = runtime

    def capture(self) -> dict:
        return {
            "schema": "noesis-snapshot/1.0",
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "reference": self.runtime.reference,
            "discovery": self.runtime.discover(),
            "health": self.runtime.health(),
            "ledger": [e.to_dict() for e in self.runtime.ledger.events],
        }

    def json(self) -> str:
        return json.dumps(self.capture(), indent=2, sort_keys=True)
