"""Command-line interface for the public Noesis runtime."""
from __future__ import annotations
import argparse, json
from noesis_core.ecosystem import EcosystemRuntime
from noesis_core.resonance import coherence
from noesis_core.ledger import Ledger

def main(argv=None):
    p=argparse.ArgumentParser(prog="noesis", description="Public operational runtime of the Noesis/QCAL ecosystem")
    s=p.add_subparsers(dest="command", required=True)
    s.add_parser("discover")
    s.add_parser("status")
    r=s.add_parser("resonance"); r.add_argument("frequency", type=float); r.add_argument("--sigma", type=float, default=0.0)
    n=s.add_parser("nodes"); n.add_argument("--role")
    e=s.add_parser("ecosystem"); es=e.add_subparsers(dest="action", required=True)
    for name in ("discover","status","verify","graph"): es.add_parser(name)
    b=s.add_parser("bus"); bs=b.add_subparsers(dest="action", required=True)
    for name in ("state","catalog","emissions"): x=bs.add_parser(name); x.add_argument("--tail", type=int, default=10)
    l=s.add_parser("ledger"); ls=l.add_subparsers(dest="action", required=True); ls.add_parser("verify")
    args=p.parse_args(argv); rt=EcosystemRuntime()
    if args.command in {"discover","status"}: out=rt.discover() if args.command=="discover" else rt.status()
    elif args.command=="resonance": out={"frequency_hz":args.frequency,"reference_hz":rt.reference["f0_hz"],"coherence":coherence(args.frequency,rt.reference["f0_hz"],args.sigma)}
    elif args.command=="nodes":
        out=[n.__dict__ for n in rt.nodes() if not args.role or n.role==args.role]
    elif args.command=="ecosystem":
        out={"discover":rt.discover,"status":rt.status,"verify":rt.verify,"graph":rt.discover}[args.action]()
    elif args.command=="bus":
        result=getattr(rt.bus(), args.action)(); out=result.data if result.ok else {"ok":False,"error":result.error,"source":result.source}
    elif args.command=="ledger": out={"valid":rt.ledger.verify()}
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str)); return 0

if __name__ == "__main__": raise SystemExit(main())
