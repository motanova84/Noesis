"""CLI for the public Noesis ecosystem runtime."""
from __future__ import annotations
import argparse, json
from noesis_core.ecosystem import EcosystemRuntime
from noesis_core.resonance import coherence

def main(argv=None):
    p=argparse.ArgumentParser(prog="noesis", description="Public operational runtime of the Noesis/QCAL ecosystem")
    s=p.add_subparsers(dest="command", required=True)
    for name in ("discover","status","health","snapshot"): s.add_parser(name)
    r=s.add_parser("resonance"); r.add_argument("frequency", type=float); r.add_argument("--sigma", type=float, default=0.0)
    n=s.add_parser("nodes"); n.add_argument("--role")
    e=s.add_parser("ecosystem"); es=e.add_subparsers(dest="action", required=True)
    for name in ("discover","status","verify","graph","health","snapshot"): es.add_parser(name)
    b=s.add_parser("bus"); bs=b.add_subparsers(dest="action", required=True)
    for name in ("state","catalog","emissions"): x=bs.add_parser(name); x.add_argument("--tail", type=int, default=10)
    l=s.add_parser("ledger"); ls=l.add_subparsers(dest="action", required=True); ls.add_parser("verify")
    args=p.parse_args(argv); rt=EcosystemRuntime()
    if args.command=="discover": out=rt.discover()
    elif args.command=="status": out=rt.status()
    elif args.command=="health": out=rt.health()
    elif args.command=="snapshot": out=rt.snapshot()
    elif args.command=="resonance": out={"frequency_hz":args.frequency,"reference_hz":rt.reference["f0_hz"],"coherence":coherence(args.frequency,rt.reference["f0_hz"],args.sigma)}
    elif args.command=="nodes": out=[n.__dict__ for n in rt.nodes() if not args.role or n.role==args.role]
    elif args.command=="ecosystem": out={"discover":rt.discover,"status":rt.status,"verify":rt.verify,"graph":rt.discover,"health":rt.health,"snapshot":rt.snapshot}[args.action]()
    elif args.command=="bus":
        result=getattr(rt.bus(), args.action)(args.tail) if args.action=="emissions" else getattr(rt.bus(), args.action)()
        out=result.data if result.ok else {"ok":False,"error":result.error}
    else: out={"valid":rt.ledger.verify()}
    print(json.dumps(out, ensure_ascii=False, indent=2, default=str)); return 0

if __name__ == "__main__": raise SystemExit(main())
