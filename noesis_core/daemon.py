"""Persistent heartbeat daemon for the public Noesis runtime."""
from __future__ import annotations

import json
import signal
import time
from pathlib import Path

from .events import make_event
from .lifecycle import EcosystemPulse


class NoesisDaemon:
    def __init__(self, runtime, state_dir: Path | str = ".noesis", interval: float = 60.0):
        self.runtime = runtime
        self.state_dir = Path(state_dir)
        self.interval = max(0.1, float(interval))
        self.running = False
        self.pulse = EcosystemPulse(runtime)

    @property
    def state_file(self) -> Path:
        return self.state_dir / "last_pulse.json"

    def start(self, cycles: int | None = None) -> list[dict]:
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.running = True
        results = []
        remaining = cycles
        while self.running and (remaining is None or remaining > 0):
            result = self.pulse.tick()
            event = make_event("system.pulse", "noesis.daemon", result)
            self.runtime.ledger.append(event.event_type, event.to_dict())
            self.state_file.write_text(
                json.dumps(result, ensure_ascii=False, indent=2, default=str) + "\n",
                encoding="utf-8",
            )
            results.append(result)
            if remaining is not None:
                remaining -= 1
                if remaining <= 0:
                    break
            time.sleep(self.interval)
        self.running = False
        return results

    def stop(self, *_signals) -> None:
        self.running = False

    def install_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def last_pulse(self) -> dict | None:
        if not self.state_file.exists():
            return None
        return json.loads(self.state_file.read_text(encoding="utf-8"))
