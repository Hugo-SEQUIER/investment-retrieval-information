# Persistence Run State - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/core/database.py`
- **Dependencies**: `sqlite3`
- **Patterns**: append/update run metadata, stage-status lifecycle, JSON stage payload storage

## Purpose
Persist run lifecycle and stage observability data used by the pipeline and CLI.

## Core Tables
- `runs`
- `stage_records`
- `stage_status`
- `source_health`
- `reports`

## Hermes Foundation Note
- Target pipeline adds a `memory` stage that writes to Obsidian.
- SQLite remains the run observability store for pipeline status.

## Conventions
- UTC timestamps for all persisted lifecycle fields.
- `runs.status` is the canonical run state.
- `stage_status` is used for workflow timeline visualization.

## TODOs / Tech Debt
- [ ] Add migration/version table for schema evolution.
- [ ] Add indexed queries for larger run history.
- [ ] Add archive/retention policy.

---
*Last update: 2026-04-12 - Initial persistence run-state feature doc.*
