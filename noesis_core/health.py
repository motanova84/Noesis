"""Liveness aggregation for the public runtime."""
from __future__ import annotations
from datetime import datetime, timezone

class HealthMonitor:
    def __init__(self, runtime): self.runtime = runtime

    def check(self) -> dict:
        checks = {}
        for name, fn in (("qcal_bus", self.runtime.bus().state), ("noesis88", self.runtime.noesis88().central)):
            snap = fn()
            checks[name] = {"ok": snap.ok, "error": snap.error, "observed_at": datetime.now(timezone.utc).isoformat()}
        ok = all(x["ok"] for x in checks.values())
        return {"status": "healthy" if ok else "degraded", "checks": checks}
