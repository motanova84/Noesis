from noesis_core.lifecycle import EcosystemPulse

class FakeRuntime:
    def __init__(self):
        self.i = 0
        self.ledger = type("Ledger", (), {"append": lambda *args, **kwargs: None})()
    def status(self):
        return {"counter": self.i}
    def health(self):
        return {"status": "healthy"}

def test_pulse_emits_heartbeat_and_detects_change():
    rt = FakeRuntime()
    pulse = EcosystemPulse(rt, interval_seconds=1)
    first, events1 = pulse.observe()
    assert first.status == "healthy"
    assert [e.event_type for e in events1] == ["ecosystem.heartbeat"]
    rt.i = 1
    second, events2 = pulse.observe()
    assert second.fingerprint != first.fingerprint
    assert [e.event_type for e in events2] == ["ecosystem.heartbeat", "ecosystem.changed"]

def test_pulse_run_is_bounded():
    rt = FakeRuntime()
    pulse = EcosystemPulse(rt, interval_seconds=1)
    cycles = list(pulse.run(cycles=2, sleep=lambda _: None))
    assert len(cycles) == 2
    assert pulse.running is False
