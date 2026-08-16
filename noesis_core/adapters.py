"""Transport-neutral adapters for the ecosystem's native HTTP/MCP surfaces."""
from __future__ import annotations
from dataclasses import dataclass
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import json, os

@dataclass
class AdapterResult:
    ok: bool
    data: object = None
    error: str | None = None
    source: str = ""

class JSONRPCClient:
    def __init__(self, endpoint: str, timeout: float = 5.0): self.endpoint, self.timeout = endpoint, timeout
    def call(self, method: str, params: dict | None = None) -> AdapterResult:
        body = json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params or {}}).encode()
        req = Request(self.endpoint, data=body, headers={"Content-Type":"application/json"}, method="POST")
        try:
            with urlopen(req, timeout=self.timeout) as r: payload = json.loads(r.read().decode())
            if "error" in payload: return AdapterResult(False, error=str(payload["error"]), source=self.endpoint)
            return AdapterResult(True, payload.get("result", payload), source=self.endpoint)
        except (URLError, HTTPError, TimeoutError, ValueError) as exc:
            return AdapterResult(False, error=str(exc), source=self.endpoint)

class QCALBusAdapter(JSONRPCClient):
    def __init__(self, endpoint: str | None = None, timeout: float = 5.0):
        super().__init__(endpoint or os.getenv("QCAL_BUS_ENDPOINT", "http://localhost:5000/api/mcp"), timeout)
    def state(self): return self.call("get_mesh_state")
    def catalog(self): return self.call("get_node_catalog")
    def emissions(self): return self.call("get_emissions_log")
    def publish(self, event: dict): return self.call("events/publish", {"event": event})

class Noesis88Adapter:
    def __init__(self, base_url: str | None = None, timeout: float = 5.0):
        self.base = (base_url or os.getenv("NOESIS88_API", "http://localhost:8700/mcp")).rstrip("/")
        self.timeout = timeout
    def get(self, path: str) -> AdapterResult:
        try:
            with urlopen(Request(self.base + path), timeout=self.timeout) as r: return AdapterResult(True, json.loads(r.read().decode()), source=self.base+path)
        except (URLError, HTTPError, TimeoutError, ValueError) as exc: return AdapterResult(False, error=str(exc), source=self.base+path)
    def central(self): return self.get("/central")
    def servers(self): return self.get("/servers")
    def repos(self): return self.get("/repos")
