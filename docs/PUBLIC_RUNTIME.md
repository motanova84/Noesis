# NOESIS Public Runtime

Noesis is the public operational layer of the QCAL ecosystem. Private engines such as `noesis88` and `logosnoesis` remain private; Noesis exposes stable, auditable contracts around them.

## Principles

- Additive integration: existing repositories and artifacts are never deleted or silently replaced.
- Native authority: each repository remains authoritative for its own implementation and evidence.
- Provenance first: claims are represented with source, method, status and digest.
- Transport neutrality: the Noesis event protocol is independent of QCAL-BUS.
- Reference configuration: `f0 = 141.7001 Hz` and `PI-CODE harmonic = 888 Hz` are system references; scientific conclusions remain tied to their source artifacts and verification state.

## Runtime

```bash
pip install -e .
noesis ecosystem discover
noesis ecosystem status
noesis ecosystem verify
noesis nodes
noesis resonance 141.7001
noesis bus state
noesis bus catalog
noesis-api
```

The API defaults to `127.0.0.1:8788` and provides `/status`, `/ecosystem`, `/nodes`, and `/verify`.

## Adapters

- QCAL-BUS: MCP JSON-RPC read surfaces (`get_mesh_state`, `get_node_catalog`, `get_emissions_log`).
- Noesis88: native HTTP control surfaces (`/central`, `/servers`, `/repos`).
- 141hz: optional local validator adapter.
- Lean: optional local `lake build` adapter.

Adapters fail explicitly when their native service or checkout is unavailable; Noesis never simulates an external verification.
