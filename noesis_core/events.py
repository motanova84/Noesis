"""Versioned, deterministic Noesis event protocol.

Events are transport-neutral. QCAL-BUS is one adapter, not the schema owner.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib
import json
from typing import Any

PROTOCOL_NAME = "noesis-event"
PROTOCOL_VERSION = "1.0"
EVENT_TYPES = {
    "system.boot",
    "resonance.measurement",
    "node.heartbeat",
    "node.status",
    "bus.sync",
    "verification.record",
}


@dataclass(frozen=True)
class NoesisEvent:
    event_id: str
    event_type: str
    source: str
    timestamp: str
    payload: dict[str, Any]
    protocol: str = PROTOCOL_NAME
    version: str = PROTOCOL_VERSION

    def validate(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id cannot be empty")
        if self.event_type not in EVENT_TYPES:
            raise ValueError(f"unsupported event_type: {self.event_type}")
        if not self.source.strip():
            raise ValueError("source cannot be empty")
        if self.protocol != PROTOCOL_NAME or self.version != PROTOCOL_VERSION:
            raise ValueError("unsupported event protocol/version")
        if not isinstance(self.payload, dict):
            raise ValueError("payload must be an object")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


def make_event(event_type: str, source: str, payload: dict[str, Any], event_id: str | None = None,
               timestamp: str | None = None) -> NoesisEvent:
    ts = timestamp or datetime.now(timezone.utc).isoformat()
    material = f"{event_type}|{source}|{ts}|{json.dumps(payload, sort_keys=True, separators=(',', ':'))}"
    eid = event_id or hashlib.sha256(material.encode("utf-8")).hexdigest()[:24]
    return NoesisEvent(eid, event_type, source, ts, payload)
