import math
from noesis_core.physical_oscillator import zero_crossing_frequency


def test_zero_crossing_recovers_signal_frequency():
    sample_rate = 10000.0
    frequency = 141.7001
    samples = [math.sin(2 * math.pi * frequency * i / sample_rate) for i in range(int(sample_rate * 2))]
    measured = zero_crossing_frequency(samples, sample_rate)
    assert abs(measured - frequency) < 0.02
