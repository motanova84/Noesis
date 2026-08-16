"""Persistent temporal memory for Noesis.

This module implements the software form of the ecosystem's temporal ledger:
append-only observations, deterministic fingerprints, restoration points and
explicit audit status. It does not claim physical phase invariance or perform
external-chain anchoring unless a concrete adapter is configured.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path


@dataclass(frozen=True)
class RestorationPoint:
    sequence: int
    observed_at: str
    fingerprint: str
    status: str
    reason: str
    ledger_hash: str | None = None


class TemporalMemory:
    def __init__(self, path: Path | str = ".noesis/temporal_memory.jsonl"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._points: list[RestorationPoint] = []
        self._load()

    @staticmethod
    def fingerprint(state: dict) -> str:
        material = json.dumps(state, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(material.encode("utf-8")).hexdigest()

    def _load(self) -> None:
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                self._points.append(RestorationPoint(**json.loads(line)))

    @property
    def points(self) -> tuple[RestorationPoint, ...]:
        return tuple(self._points)

    @property
    def latest(self) -> RestorationPoint | None:
        return self._points[-1] if self._points else None

    def record(self, state: dict, status: str, reason: str = "observation", ledger_hash: str | None = None) -> RestorationPoint:
        point = RestorationPoint(
            sequence=len(self._points) + 1,
            observed_at=datetime.now(timezone.utc).isoformat(),
            fingerprint=self.fingerprint(state),
            status=status,
            reason=reason,
            ledger_hash=ledger_hash,
        )
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(point), sort_keys=True) + "\n")
        self._points.append(point)
        return point

    def restore_target(self) -> RestorationPoint | None:
        """Return the newest recorded restoration point without mutating state."""
        return self.latest

    def verify(self) -> bool:
        if not self.path.exists():
            return True
        lines = [line for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if len(lines) != len(self._points):
            return False
        return all(p.sequence == i for i, p in enumerate(self._points, 1))
