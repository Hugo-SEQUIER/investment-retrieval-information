# Obsidian Memory Sync - Overview

## Quick Reference
- **Key files**: planned
- **Dependencies**: vault filesystem access
- **Patterns**: deterministic paths, overwrite policy, section ownership

## Purpose
Persist Hermes research memory into Obsidian after each run using predictable
note layouts.

## Vault Scope
- `Companies/`
- `Themes/`
- `Daily Logs/`
- `Open Questions/`
- `Sources/`

## Write Policy
- Managed sections are overwritten on each sync.
- Human sections are preserved.
- Required ownership markers:
  - `## Auto-Generated`
  - `## Hermes Notes`
  - `## Human Notes`

## Identity and Idempotency
- Company note key: ticker-first identifier.
- Daily log key: UTC date.
- Re-running the same report date overwrites managed sections only.

## Failure Handling
- If vault write fails, run status remains success with memory-stage warning.
- Writes should be atomic per file to avoid partial updates.

## TODOs / Tech Debt
- [ ] Finalize note frontmatter schema.
- [ ] Add dry-run mode for memory sync validation.

---
*Last update: 2026-04-13 - Initial Hermes foundation Obsidian memory doc.*
