# Noesis ↔ QCAL Evidence Registry

Noesis does not duplicate scientific artifacts. It records their provenance and exposes them as auditable references through the event protocol.

## Primary ecosystem sources

| Source | Artifact | What it contains | Noesis treatment |
|---|---|---|---|
| `motanova84/141hz` | `DERIVACION_COMPLETA_F0.md` | GW150914 spectral analysis and several theoretical/phenomenological derivations of `f₀ = 141.7001 Hz` | **claimed evidence / requires independent audit** |
| `motanova84/141hz` | `PSI_ZETA_SPECTRUM_VERIFICATION.md` | executable spectral framework, tests and explicit calibration caveat | **reproducible artifact; calibration caveat retained** |
| `motanova84/141hz` | `EVIDENCE_CONSOLIDATION_15SIGMA.md` | consolidated significance claims across GW, TDE, numerical, atomic and geophysical sources | **repository claim; significance not independently certified by Noesis** |
| `motanova84/QCAL-BUS` | `qcal_mesh_sync.py` | QCAL-EPR mesh monitor and MCP JSON-RPC bridge | **operational integration target** |
| `motanova84/QCAL-BUS` | `registry/NODE_CATALOG.json` | ecosystem node catalog and MCP endpoints | **source of topology metadata** |

## Important distinction

A repository can contain a reproducible computation, a formal proof, an experimental analysis, or a claim about one of these. Noesis records the provenance without silently upgrading a claim into an independently established scientific fact.

The `verification.record` event exists precisely for this purpose: it can carry the source repository, commit/ref, artifact path, method, result, and audit status.

## Current QCAL-BUS contract

The documented QCAL-BUS bridge exposes MCP JSON-RPC tools for:

- `get_mesh_state`
- `get_node_catalog`
- `get_emissions_log`

Noesis integrates these read/monitor capabilities through `noesis_core.bus.QCALBusClient`.

Event publication is intentionally separated as an optional `events/publish` capability. Noesis will report an explicit transport error if the running QCAL-BUS instance does not expose that method; it will never masquerade a read operation as event publication.
