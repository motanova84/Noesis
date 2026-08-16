"""QCAL-BUS integration adapter.

The adapter targets the QCAL-BUS MCP JSON-RPC bridge and keeps transport details
outside the Noesis core. Default endpoint follows the ecosystem catalog.
"""

from __future__ import annotations

import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .events import NoesisEvent

DEFAULT_QCAL_BUS_URL = "http://localhost:5000/api/mcp"


class QCALBusError(RuntimeError):
    pass


class QCALBusClient:
    def __init__(self, endpoint: str = DEFAULT_QCAL_BUS_URL, timeout: float = 10.0) -> None:
        self.endpoint = endpoint
        self.timeout = timeout

    def call(self, method: str, params: dict | None = None, request_id: str = "noesis-1") -> dict:
        body = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params or {},
        }
        request = Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise QCALBusError(f"QCAL-BUS request failed: {exc}") from exc
        if isinstance(result, dict) and "error" in result:
            raise QCALBusError(str(result["error"]))
        return result

    def mesh_state(self) -> dict:
        return self.call("tools/call", {"name": "get_mesh_state", "arguments": {}})

    def node_catalog(self) -> dict:
        return self.call("tools/call", {"name": "get_node_catalog", "arguments": {}})

    def emissions(self, tail: int = 50) -> dict:
        return self.call("tools/call", {"name": "get_emissions_log", "arguments": {"tail": tail}})

    def publish_event(self, event: NoesisEvent) -> dict:
        """Publish a Noesis event through the bus when the bus exposes event ingestion.

        QCAL-BUS currently exposes read/monitor MCP tools in its documented bridge.
        Therefore this method uses the optional `events/publish` method and fails
        explicitly if that capability is not installed, rather than pretending that
        a read-only endpoint accepted the event.
        """
        event.validate()
        return self.call("events/publish", {"event": event.to_dict(), "digest": event.digest})
