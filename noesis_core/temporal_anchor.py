"""External anchoring boundary for Noesis temporal memory.

Anchors are adapters, not claims: an anchor is only marked committed after a
concrete backend confirms it. This keeps local temporal memory usable offline
and prevents the runtime from presenting an unsubmitted external transaction
as immutable external evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True)
class AnchorRequest:
    sequence: int
    fingerprint: str
    ledger_hash: str | None
    created_at: str

    def canonical(self) -> str:
        return json.dumps({
            "sequence": self.sequence,
            "fingerprint": self.fingerprint,
            "ledger_hash": self.ledger_hash,
            "created_at": self.created_at,
        }, sort_keys=True, separators=(",", ":"))

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.canonical().encode("utf-8")).hexdigest()


class AnchorBackend(Protocol):
    def submit(self, request: AnchorRequest) -> str: ...


class LocalAnchor:
    """Durable local anchor used as the default backend."""
    def __init__(self, path: Path | str = ".noesis/anchors.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def submit(self, request: AnchorRequest) -> str:
        anchor_id = request.digest
        record = {
            "anchor_id": anchor_id,
            "backend": "local",
            "committed_at": datetime.now(timezone.utc).isoformat(),
            "request": json.loads(request.canonical()),
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
        return anchor_id


class TemporalAnchor:
    def __init__(self, backend: AnchorBackend | None = None):
        self.backend = backend or LocalAnchor()

    def create(self, point) -> str:
        request = AnchorRequest(
            sequence=point.sequence,
            fingerprint=point.fingerprint,
            ledger_hash=point.ledger_hash,
            created_at=point.observed_at,
        )
        return self.backend.submit(request)
