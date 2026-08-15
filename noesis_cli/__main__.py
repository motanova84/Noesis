from __future__ import annotations

import argparse
import json
import os
import sys

from noesis_core import Ledger, Node, NodeRegistry, coherence
from noesis_core.bus import QCALBusClient, QCALBusError
from noesis_core.events import make_event
from noesis_core.resonance import F0_REFERENCE


def _json(value: object) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="noesis", description="Noesis operational CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    status = sub.add_parser("status", help="show local Noesis status")
    status.add_argument("--frequency", type=float, default=F0_REFERENCE)
    status.add_argument("--sigma", type=float, default=0.0)

    resonance = sub.add_parser("resonance", help="measure coherence against f0")
    resonance.add_argument("frequency", type=float, nargs="?", default=F0_REFERENCE)
    resonance.add_argument("--sigma", type=float, default=0.0)

    nodes = sub.add_parser("nodes", help="inspect the local node registry")
    nodes.add_argument("--online", action="store_true", help="show only online nodes")

    ledger = sub.add_parser("ledger", help="inspect or verify the local ledger")
    ledger.add_argument("action", choices=("verify", "count"), default="verify", nargs="?")

    event = sub.add_parser("event", help="create a protocol event")
    event.add_argument("event_type", choices=("system.boot", "resonance.measurement", "node.heartbeat", "node.status", "bus.sync", "verification.record"))
    event.add_argument("--source", default="noesis-cli")
    event.add_argument("--payload", default="{}", help="JSON object")

    bus = sub.add_parser("bus", help="query QCAL-BUS through its MCP bridge")
    bus.add_argument("action", choices=("state", "catalog", "emissions"))
    bus.add_argument("--endpoint", default=os.getenv("QCAL_BUS_ENDPOINT", "http://localhost:5000/api/mcp"))
    bus.add_argument("--tail", type=int, default=50)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "resonance":
        _json({"frequency_hz": args.frequency, "reference_hz": F0_REFERENCE, "coherence": coherence(args.frequency, sigma_hz=args.sigma)})
        return 0

    if args.command == "status":
        _json({"service": "noesis", "reference_frequency_hz": F0_REFERENCE, "measurement": {"frequency_hz": args.frequency, "coherence": coherence(args.frequency, sigma_hz=args.sigma)}})
        return 0

    if args.command == "nodes":
        registry = NodeRegistry()
        for node_id in ("N1", "N2", "N3", "N4", "N5", "N6", "N7"):
            registry.register(Node(node_id, role="ecosystem"))
        result = [node.__dict__ for node in registry.snapshot() if not args.online or node.online]
        _json({"count": len(result), "nodes": result})
        return 0

    if args.command == "ledger":
        ledger = Ledger()
        _json({"valid": ledger.verify(), "count": len(ledger.events)})
        return 0

    if args.command == "event":
        try:
            payload = json.loads(args.payload)
        except json.JSONDecodeError as exc:
            print(f"invalid payload JSON: {exc}", file=sys.stderr)
            return 2
        if not isinstance(payload, dict):
            print("payload must be a JSON object", file=sys.stderr)
            return 2
        _json(make_event(args.event_type, args.source, payload).to_dict())
        return 0

    if args.command == "bus":
        client = QCALBusClient(args.endpoint)
        try:
            if args.action == "state":
                result = client.mesh_state()
            elif args.action == "catalog":
                result = client.node_catalog()
            else:
                result = client.emissions(args.tail)
        except QCALBusError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        _json(result)
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
