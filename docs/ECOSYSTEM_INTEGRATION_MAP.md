# NOESIS — QCAL Ecosystem Integration Map

## Purpose

This document is the integration contract for the Noesis operational layer. It inventories existing repositories and protocols without replacing, deleting, or rewriting their native implementations.

**Preservation rule:** Noesis is an orchestrator/observer. Existing repositories remain authoritative for their own code, tests, formalizations, ledgers, experimental artifacts and documentation. Integration adds adapters and provenance; it does not erase source material.

## Reference configuration

- `F0_REFERENCE = 141.7001 Hz`
- `PI_CODE_HARMONIC = 888 Hz`
- `PSI_THRESHOLD = 0.999999`
- MCP transport: JSON-RPC 2.0, stdio and HTTP bridges where already implemented
- Noesis signature lineage: `∴𓂀Ω∞³`

## Existing operational layers discovered

| Layer | Repository | Existing assets to reuse | Integration role |
|---|---|---|---|
| Bus | `QCAL-BUS` | `qcal_mesh_sync.py`, `registry/NODE_CATALOG.json`, `ledger/emissions_log.csv`, dashboard :8505, MCP tools | primary mesh state/catalog/emissions adapter |
| Noesis orchestration | `noesis88` | `mcp_servers/orchestrator.py`, Repository Reader, Intelligent Writer, Memory Expansion, `api/mcp_api.py`, MCP stdio servers | central multi-repository control plane |
| Frequency/evidence | `141hz` | spectral analyses, validation docs, MCP network validator, QCAL/πCODE tooling, hardware and API artifacts | evidence/provenance source and validation runners |
| Formalization | `qcal-formalization` | Lean 4 modules, lakefile, formalization reports | formal verification source |
| Riemann | `Riemann-adelic` | Lean/Fredholm/adelic artifacts and MCP node | mathematical node adapter |
| P vs NP | `P-NP` | Boolean CFT and related formal/computational artifacts | mathematical node adapter |
| Navier-Stokes | `3D-Navier-Stokes` | symbolic/numerical/Lean artifacts | mathematical node adapter |
| Ramsey | `Ramsey` | SAT/Z3/Lean verification artifacts | combinatorial node adapter |
| BSD | `adelic-bsd` | adelic/spectral artifacts | mathematical node adapter |
| Quantum network | `quantum-internet-qcal` | QOSC-RC, QCAL-Lighthouse, BB84, entanglement, MCP bridge, API, hardware demonstrator, economy bridge | quantum/network adapter |
| Clock | `RelojCuantico-141Hz-QCAL` | experimental protocols, generators, Lean validation, tests, hardware and Compton-clock artifacts | experimental/hardware provenance adapter |
| Noesis88 | `noesis88` | 141.7001/888 MCP servers, sovereign signatures, memory, repository reader/writer | semantic/agent layer |
| Field | `field-qcal` | experiential mathematics, Zeta art, governance and integration | application/experience layer |
| Economy | `economia-qcal-nodo-semilla` | πCODE/PoCPSI/QHPT-related material | economic protocol adapter |
| Vault | `QCAL-Sovereign-Vault` | sovereign storage/signature artifacts | provenance/security adapter |
| Geometry | `empaquetamiento-esferas-qcal`, `empaquetamiento-esferas-qcal3` | geometric assets where present | geometry adapter |
| Backup | `ecosistema-qcal-backup` | preserved ecosystem snapshot | immutable recovery/reference source |

## Protocols to preserve and expose through Noesis

### 1. QCAL-BUS MCP

Native documented tools:

- `get_mesh_state`
- `get_node_catalog`
- `get_emissions_log`

HTTP bridge: `/api/mcp` on the existing dashboard service. Stdio mode is supported by `qcal_mesh_sync.py --mcp-server`.

### 2. Noesis88 control API

Native API surface discovered in `noesis88/api/mcp_api.py`:

- `GET /mcp/central`
- `GET /mcp/servers`
- `GET /mcp/repos`
- `POST /mcp/central`
- `POST /mcp/reader`
- `POST /mcp/writer`
- `POST /mcp/memory`

This is the richest existing orchestration surface and should be reused rather than duplicated inside Noesis.

### 3. Noesis88 stdio MCP

Existing tools include:

- `amda_resonance`
- `amda_creative_flow`
- `amda_emotional_analysis`
- `noesis_coherence`
- `noesis_phase_diff`
- `noesis_frequency`
- `noesis_calibrate`

### 4. QCAL frequency validation

`141hz/core/validate_mcp_network.py` already defines a network validator around 141.7001 Hz and 888 Hz, including frequency synchronization, coherence/entropy, observer synchronization, noetic-chain closure and server status.

Noesis should call or wrap this validator and preserve its raw report rather than reimplementing its logic.

### 5. Formal verification

`qcal-formalization` is the Lean 4 formalization source. Noesis should record:

- repository/ref
- Lean file/module
- theorem/lemma identifier
- build/test result
- `sorry`/axiom status when explicitly reported
- timestamp
- artifact hash

Noesis must not translate a repository claim such as “theorem proved” into an independent scientific certification without the corresponding build/test evidence.

## Evidence model

Every imported result should become a `verification.record` event with:

```json
{
  "repository": "motanova84/141hz",
  "ref": "main",
  "artifact": "path/to/artifact",
  "method": "test | simulation | experiment | Lean | analysis | documentation",
  "result": {},
  "status": "observed | reproduced | verified | claimed | failed | stale",
  "timestamp": "...",
  "source_sha": "..."
}
```

The raw artifact is never overwritten by the integration layer.

## Important consistency findings

1. `QCAL-BUS/registry/NODE_CATALOG.json` currently declares `version=2.0.0`, `f0_reference_hz=141.7001` and `total_nodes=34`, while older MCP documentation describes 33 nodes. Noesis must read the live catalog and report the discrepancy instead of hard-coding 33.
2. `RelojCuantico-141Hz-QCAL` contains references to both `141.70001 Hz` and `141.7001 Hz`. These are not interchangeable. Noesis must preserve the source value and classify cross-repository frequency mismatches as an audit finding.
3. `QCAL-BUS` documents read/monitor MCP tools; Noesis must not pretend that an `events/publish` endpoint exists unless the live bus exposes it.
4. Several repositories contain strong scientific/formal claims. The integration layer records them with provenance and execution status; it does not silently upgrade documentation into independent validation.

## Target operational graph

```text
                          NOESIS
                 control + provenance layer
                           │
          ┌────────────────┼────────────────┐
          │                │                │
       MCP/API          EVENT BUS         MEMORY
          │                │                │
          └────────────────┼────────────────┘
                           │
                       QCAL-BUS
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   NODE CATALOG        MESH STATE          LEDGER
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
       ┌───────────────┬───┴────┬───────────────┐
       │               │        │               │
    141hz         Formalization  Math         Quantum
       │               │        │               │
   evidence          Lean      Riemann       QOSC/QKD
       │               │        │               │
       └───────────────┴────────┴───────────────┘
                           │
                    VERIFICATION LEDGER
```

## Implementation order

1. Import the live QCAL-BUS catalog and preserve its exact state.
2. Add a Noesis ecosystem registry and provenance records.
3. Add adapters for QCAL-BUS and Noesis88 API/stdio.
4. Wrap existing 141hz validation runners and formalization build/test outputs.
5. Add health/state aggregation without duplicating node logic.
6. Emit deterministic `verification.record`, `node.status`, `bus.sync` and `resonance.measurement` events.
7. Persist an append-only integration ledger with source hashes.
8. Expose the entire graph through the Noesis CLI.
9. Add CI that checks integration contracts but never deletes or mutates source artifacts.

This map is additive by design.
