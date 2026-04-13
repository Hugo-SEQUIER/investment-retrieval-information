# Daily Pipeline - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/pipeline/daily.py`, `src/ai_equity_discovery/cli.py`
- **Dependencies**: core stage modules under `src/ai_equity_discovery/*`
- **Patterns**: strict stage ordering, stage-status instrumentation, auditable stage records

## Purpose
Coordinate end-to-end daily execution from fetch to memory while persisting
stage outputs and status.

## Target Stage Order
1. fetch
2. filter
3. analyze
4. report
5. memory

## Migration Note
- Runtime code is still on the legacy stage model and will be migrated to this
  target order.

## Fetch Lookback Window
- Pipeline computes `since_utc` automatically for fetch collection.
- First run: bootstrap window (default `BOOTSTRAP_LOOKBACK_DAYS=7`).
- Subsequent runs: daily window (default `DAILY_LOOKBACK_DAYS=1`).

## Observability
- Run-level status: queued/running/success/failed
- Stage-level status with start/end timestamps
- Source health written after fetch stage

## TODOs / Tech Debt
- [ ] Add retry policy per stage.
- [ ] Add stage-level timeout controls.
- [ ] Add run-log export for CLI operations.

---
*Last update: 2026-04-13 - Target stage model updated to fetch/filter/analyze/report/memory.*
