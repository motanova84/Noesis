"""Service entrypoint helpers for supervised Noesis deployments."""
from __future__ import annotations

from .daemon import NoesisDaemon
from .ecosystem import EcosystemRuntime


def run(interval: float = 60.0, cycles: int | None = None, state_dir: str = ".noesis") -> None:
    runtime = EcosystemRuntime()
    daemon = NoesisDaemon(runtime, state_dir=state_dir, interval=interval)
    daemon.install_signal_handlers()
    daemon.start(cycles=cycles)


if __name__ == "__main__":
    run()
