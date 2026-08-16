"""Append-only, hash-chained event ledger for Noesis."""

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json


@dataclass(frozen=True)
class LedgerEvent:
    event_type: str
    payload: dict
    timestamp: str
    previous_hash: str
    hash: str


class Ledger:
    def __init__(self) -> None:
        self._events: list[LedgerEvent] = []

    @property
    def events(self) -> tuple[LedgerEvent, ...]:
        return tuple(self._events)

    def append(self, event_type: str, payload: dict, timestamp: str | None = None) -> LedgerEvent:
        ts = timestamp or datetime.now(timezone.utc).isoformat()
        previous = self._events[-1].hash if self._events else "0" * 64
        material = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": ts,
            "previous_hash": previous,
        }
        digest = hashlib.sha256(
            json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        event = LedgerEvent(**material, hash=digest)
        self._events.append(event)
        return event

    def verify(self) -> bool:
        previous = "0" * 64
        for event in self._events:
            if event.previous_hash != previous:
                return False
            material = {
                "event_type": event.event_type,
                "payload": event.payload,
                "timestamp": event.timestamp,
                "previous_hash": event.previous_hash,
            }
            digest = hashlib.sha256(
                json.dumps(material, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()
            if digest != event.hash:
                return False
            previous = event.hash
        return True

    def to_jsonl(self) -> str:
        return "".join(json.dumps(asdict(event), sort_keys=True) + "\n" for event in self._events)
