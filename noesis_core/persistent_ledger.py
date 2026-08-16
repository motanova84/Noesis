"""Durable append-only ledger backed by JSONL."""
from __future__ import annotations

import json
from pathlib import Path

from .ledger import Ledger, LedgerEvent


class PersistentLedger(Ledger):
    def __init__(self, path: Path | str = ".noesis/ledger.jsonl"):
        super().__init__()
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            data = json.loads(line)
            self._events.append(LedgerEvent(**data))
        if not self.verify():
            raise ValueError(f"Invalid ledger chain: {self.path}")

    def append(self, event_type: str, payload: dict, timestamp: str | None = None) -> LedgerEvent:
        event = super().append(event_type, payload, timestamp)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(event.__dict__, sort_keys=True) + "\n")
        return event
