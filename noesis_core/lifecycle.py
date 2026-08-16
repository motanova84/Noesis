"""Continuous ecosystem lifecycle: heartbeat, observation, change detection and events."""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import hashlib, json, time
from typing import Callable

from .events import make_event

@dataclass(frozen=True)
class Observation:
    observed_at: str
    status: str
    fingerprint: str
    state: dict

class EcosystemPulse:
    """A small, transport-neutral pulse loop for the public runtime.

    It never mutates source repositories. Each cycle observes configured services,
    hashes the normalized state, and emits lifecycle events when state changes.
    """
    def __init__(self, runtime, interval_seconds: float = 60.0):
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self.runtime = runtime
        self.interval_seconds = interval_seconds
        self.previous: Observation | None = None
        self.running = False

    @staticmethod
    def _fingerprint(state: dict) -> str:
        raw = json.dumps(state, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def observe(self) -> tuple[Observation, list]:
        status = self.runtime.status()
        health = self.runtime.health()
        state = {"status": status, "health": health}
        fingerprint = self._fingerprint(state)
        now = datetime.now(timezone.utc).isoformat()
        current = Observation(now, health["status"], fingerprint, state)
        events = [make_event("ecosystem.heartbeat", "noesis", {
            "status": current.status,
            "fingerprint": current.fingerprint,
            "observed_at": current.observed_at,
        })]
        if self.previous is not None and self.previous.fingerprint != current.fingerprint:
            events.append(make_event("ecosystem.changed", "noesis", {
                "previous_fingerprint": self.previous.fingerprint,
                "fingerprint": current.fingerprint,
                "previous_status": self.previous.status,
                "status": current.status,
            }))
        for event in events:
            self.runtime.ledger.append(event.event_type, event.to_dict(), timestamp=current.observed_at)
        self.previous = current
        return current, events

    def run(self, cycles: int | None = None, sleep: Callable[[float], None] = time.sleep):
        """Run until cycles are exhausted or stop() is called."""
        self.running = True
        count = 0
        try:
            while self.running and (cycles is None or count < cycles):
                yield self.observe()
                count += 1
                if self.running and (cycles is None or count < cycles):
                    sleep(self.interval_seconds)
        finally:
            self.running = False

    def stop(self) -> None:
        self.running = False
