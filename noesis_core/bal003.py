"""BAL003 adapter contract.

BAL003 is treated as a physical observation source only when a concrete
hardware backend is supplied. The default backend is intentionally unavailable
rather than synthetic, so Noesis cannot mistake a simulation for measurement.
"""
from __future__ import annotations
from typing import Iterable
from .physical_oscillator import SampleSource

class BAL003Unavailable(RuntimeError):
    pass

class BAL003(SampleSource):
    def __init__(self, backend=None):
        self.backend = backend

    def connect(self) -> None:
        if self.backend is None:
            raise BAL003Unavailable("BAL003 hardware backend is not configured")
        self.backend.connect()

    def read_samples(self, duration_s: float, sample_rate_hz: float) -> Iterable[float]:
        if self.backend is None:
            raise BAL003Unavailable("BAL003 hardware backend is not configured")
        return self.backend.read_samples(duration_s, sample_rate_hz)

    def health(self) -> dict:
        if self.backend is None:
            return {"status": "unavailable", "source": "BAL003"}
        return {"status": "available", "source": "BAL003"}
