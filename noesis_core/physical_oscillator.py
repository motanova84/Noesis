"""Physical oscillator observation boundary for Noesis.

Separates the QCAL nominal frequency from an actually measured signal.
No measurement is synthesized when hardware is unavailable.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Protocol

F0_QCAL_HZ = 141.7001

class SampleSource(Protocol):
    def read_samples(self, duration_s: float, sample_rate_hz: float) -> Iterable[float]: ...

@dataclass(frozen=True)
class FrequencyMeasurement:
    nominal_hz: float
    measured_hz: float
    error_hz: float
    relative_error: float
    sample_rate_hz: float
    duration_s: float
    sample_count: int
    status: str

def zero_crossing_frequency(samples: Iterable[float], sample_rate_hz: float) -> float:
    values = list(samples)
    if len(values) < 3 or sample_rate_hz <= 0:
        raise ValueError("insufficient samples or invalid sample rate")
    crossings = []
    previous = values[0]
    for index, current in enumerate(values[1:], 1):
        if previous <= 0 < current:
            fraction = (-previous) / (current - previous) if current != previous else 0.0
            crossings.append((index - 1) + fraction)
        previous = current
    if len(crossings) < 2:
        raise ValueError("fewer than two positive-going zero crossings")
    periods = [b - a for a, b in zip(crossings, crossings[1:])]
    return sample_rate_hz / (sum(periods) / len(periods))

def measure_frequency(source: SampleSource, duration_s: float, sample_rate_hz: float, nominal_hz: float = F0_QCAL_HZ) -> FrequencyMeasurement:
    samples = list(source.read_samples(duration_s, sample_rate_hz))
    measured = zero_crossing_frequency(samples, sample_rate_hz)
    error = measured - nominal_hz
    return FrequencyMeasurement(nominal_hz, measured, error, error / nominal_hz, sample_rate_hz, duration_s, len(samples), "measured")
