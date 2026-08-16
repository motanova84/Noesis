# Noesis

Núcleo operativo de Noēsis: estado determinista, resonancia de referencia, nodos, eventos, ledger y puente con QCAL-BUS.

## Referencia de sistema

- Frecuencia de referencia: `f₀ = 141.7001 Hz`
- Coherencia: métrica determinista y auditable en `noesis_core.resonance`
- Protocolo de eventos: `noesis-event/1.0`
- Integración: QCAL-BUS mediante MCP JSON-RPC

> La frecuencia es una referencia del sistema. Los resultados científicos se conservan como artefactos con procedencia y estado de auditoría; Noesis no convierte automáticamente una afirmación documental en una validación independiente.

## CLI

Tras instalar el paquete:

```bash
pip install -e .

noesis status
noesis resonance 141.7001
noesis nodes
noesis ledger verify
noesis event resonance.measurement --payload '{"frequency_hz":141.7001,"coherence":1.0}'
```

## QCAL-BUS

El adaptador `noesis_core.bus.QCALBusClient` consume el puente MCP documentado por QCAL-BUS:

```bash
noesis bus state
noesis bus catalog
noesis bus emissions --tail 10
```

Endpoint configurable con `QCAL_BUS_ENDPOINT`; por defecto:

```text
http://localhost:5000/api/mcp
```

El cliente también define `publish_event()` para una capacidad opcional `events/publish`. Si el servidor no la expone, falla explícitamente en lugar de simular una publicación.

## Evidencia QCAL

El registro de procedencia está en [`docs/QCAL_EVIDENCE_REGISTRY.md`](docs/QCAL_EVIDENCE_REGISTRY.md).

Entre los artefactos del ecosistema consultados se encuentran:

- `motanova84/141hz/DERIVACION_COMPLETA_F0.md`
- `motanova84/141hz/PSI_ZETA_SPECTRUM_VERIFICATION.md`
- `motanova84/141hz/EVIDENCE_CONSOLIDATION_15SIGMA.md`
- `motanova84/QCAL-BUS/qcal_mesh_sync.py`

Esto permite que Noesis sea el punto de orquestación sin perder la distinción entre **código reproducible, análisis, formalización y afirmaciones científicas**.
