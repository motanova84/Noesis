"""Read-only adapter for the documented QCAL-BUS MCP surface."""
from __future__ import annotations
from dataclasses import dataclass
import json, os, urllib.request

@dataclass(frozen=True)
class BusSnapshot:
    ok: bool
    data: dict
    error: str | None = None

class QCALBusAdapter:
    def __init__(self, url: str | None = None, timeout: float = 5.0):
        self.url = url or os.getenv("QCAL_BUS_MCP_URL", "http://localhost:5000/api/mcp")
        self.timeout = timeout

    def _call(self, method: str, params: dict | None = None) -> BusSnapshot:
        payload = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params or {}}).encode()
        req = urllib.request.Request(self.url, payload, {"Content-Type":"application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                data = json.loads(response.read().decode())
            if "error" in data:
                return BusSnapshot(False, data, str(data["error"]))
            return BusSnapshot(True, data.get("result", data))
        except Exception as exc:
            return BusSnapshot(False, {}, f"{type(exc).__name__}: {exc}")

    def state(self) -> BusSnapshot: return self._call("get_mesh_state")
    def catalog(self) -> BusSnapshot: return self._call("get_node_catalog")
    def emissions(self, limit: int = 10) -> BusSnapshot: return self._call("get_emissions_log", {"limit": limit})
