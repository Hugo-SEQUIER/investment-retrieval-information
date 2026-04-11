# Project AGENTS

Project-specific execution rules only.
Global routing and cost policy live in global `AGENTS.md`.

## First Read Policy

- Read project docs/indexes before source code:
  - `[DOCS_INDEX_PATH]`
  - `[ARCH_INDEX_PATH]`
  - `[FEATURE_MAP_PATH]`
  - `[DECISION_INDEX_PATH]`
- If docs are insufficient, do targeted code reads.

## Architecture Guardrails

- Boundaries:
  - `[BOUNDARY_1]`
  - `[BOUNDARY_2]`
- Non-negotiables:
  - `[RULE_1]`
  - `[RULE_2]`

## Implementation Conventions

- Backend: `[CONVENTIONS]`
- Frontend: `[CONVENTIONS]`
- Naming: `[NAMING_RULES]`

## Validation Commands

- Fast checks: `[COMMANDS]`
- Full checks: `[COMMANDS]`
- Build/release checks: `[COMMANDS]`

## Done Criteria

- Change respects architecture boundaries.
- Relevant checks pass (or failures are explained).
- Related docs are updated when behavior/structure changed.

## Optional Vault Workflow

- Session start: `/session-start`
- Search before major decisions: `/vault-search <query>`
- After meaningful changes: `/kanban-update ...`, `/changelog-entry ...`
- Save reusable insights: `/memory-write ...`
