"""Provenance records: preserve source claims without silently upgrading them."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
import hashlib, json

STATUSES = {"claimed", "observed", "reproduced", "tested", "formally_verified", "experimentally_supported", "failed", "stale"}

@dataclass(frozen=True)
class VerificationRecord:
    repository: str
    artifact: str
    method: str
    status: str
    result: dict[str, Any]
    ref: str = "main"
    source_sha: str | None = None
    timestamp: str = ""

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError(f"unsupported status: {self.status}")
        if not self.timestamp:
            object.__setattr__(self, "timestamp", datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict[str, Any]: return asdict(self)
    @property
    def digest(self) -> str:
        raw = json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()
