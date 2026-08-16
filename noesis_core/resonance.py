"""Reference frequency and deterministic resonance metrics."""

from dataclasses import dataclass
from math import exp

F0_REFERENCE = 141.7001


@dataclass(frozen=True)
class ResonanceState:
    frequency_hz: float
    coherence: float
    reference_hz: float = F0_REFERENCE


def coherence(frequency_hz: float, reference_hz: float = F0_REFERENCE, sigma_hz: float = 0.0) -> float:
    """Return bounded coherence from frequency deviation and measurement spread.

    A perfect match with zero spread yields 1.0.  The metric is deterministic,
    bounded to [0, 1], and does not claim physical validation of the reference.
    """
    if frequency_hz <= 0 or reference_hz <= 0:
        raise ValueError("frequencies must be positive")
    if sigma_hz < 0:
        raise ValueError("sigma_hz must be non-negative")
    relative_error = abs(frequency_hz - reference_hz) / reference_hz
    spread = sigma_hz / reference_hz
    return max(0.0, min(1.0, exp(-(relative_error + spread) ** 2)))


def measure(frequency_hz: float, sigma_hz: float = 0.0) -> ResonanceState:
    return ResonanceState(
        frequency_hz=frequency_hz,
        coherence=coherence(frequency_hz, sigma_hz=sigma_hz),
    )
