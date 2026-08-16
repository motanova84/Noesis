"""Read-only adapter for the private noesis88 HTTP control plane."""
from __future__ import annotations
from dataclasses import dataclass
import json, os, urllib.request

@dataclass(frozen=True)
class ServiceSnapshot:
    ok: bool
    data: dict
    error: str | None = None

class Noesis88Adapter:
    def __init__(self, base_url: str | None = None, timeout: float = 5.0):
        self.base_url = (base_url or os.getenv("NOESIS88_API_URL", "http://localhost:8700/mcp")).rstrip("/")
        self.timeout = timeout

    def _get(self, path: str) -> ServiceSnapshot:
        try:
            with urllib.request.urlopen(f"{self.base_url}/{path.lstrip('/')}", timeout=self.timeout) as response:
                return ServiceSnapshot(True, json.loads(response.read().decode()))
        except Exception as exc:
            return ServiceSnapshot(False, {}, f"{type(exc).__name__}: {exc}")

    def central(self) -> ServiceSnapshot: return self._get("central")
    def servers(self) -> ServiceSnapshot: return self._get("servers")
    def repositories(self) -> ServiceSnapshot: return self._get("repos")
