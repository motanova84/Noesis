#!/usr/bin/env python3
"""Deterministic validator for the QCAL Ω evidence ledger."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "qcal_omega_ledger.json"
ALLOWED_LEVELS = {"M", "C", "E"}
ALLOWED_STATUSES = {"OPEN", "FORMALIZED", "VERIFIED", "PREDICTED", "FALSIFIED"}


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "qcal-omega-audit/1.0":
        errors.append("invalid schema")
    ref = data.get("reference", {})
    if ref.get("f0_hz") != 141.7001:
        errors.append("f0_hz must equal 141.7001")
    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        return errors + ["claims must be a non-empty list"]

    ids = [c.get("id") for c in claims]
    if len(ids) != len(set(ids)):
        errors.append("claim ids must be unique")
    known = set(ids)
    for claim in claims:
        cid = claim.get("id", "<missing>")
        if claim.get("level") not in ALLOWED_LEVELS:
            errors.append(f"{cid}: invalid evidence level")
        if claim.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{cid}: invalid status")
        for dep in claim.get("depends_on", []):
            if dep not in known:
                errors.append(f"{cid}: unknown dependency {dep}")
    return errors


def main() -> int:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"QCAL Ω ledger valid: {len(data['claims'])} claims")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
