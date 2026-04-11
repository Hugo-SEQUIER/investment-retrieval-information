# Daily Pipeline - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/pipeline/daily.py`, `src/ai_equity_discovery/cli.py`
- **Dependencies**: core stage modules under `src/ai_equity_discovery/*`
- **Patterns**: strict stage ordering, stage-status instrumentation, auditable stage records

## Purpose
Coordinate end-to-end daily execution from discovery to reporting while persisting stage outputs and status.

## Stage Order
1. discovery
2. extraction
3. resolution
4. enrichment
5. ranking
6. reporting

## Observability
- Run-level status: queued/running/success/failed
- Stage-level status with start/end timestamps
- Source health written after discovery stage

## TODOs / Tech Debt
- [ ] Add retry policy per stage.
- [ ] Add stage-level timeout controls.
- [ ] Add event streaming surface for frontend live updates.

---
*Last update: 2026-04-12 - Initial daily pipeline feature doc.*
