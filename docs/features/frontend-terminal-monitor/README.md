# Frontend Terminal Monitor - Overview

## Quick Reference
- **Key files**: `frontend/app/page.tsx`, `frontend/components/*`, `frontend/lib/api.ts`, `frontend/lib/types.ts`
- **Dependencies**: Next.js, TypeScript, Tailwind CSS, shadcn/ui, FastAPI
- **Patterns**: polling-driven run monitor, markdown-first output, guarded source config edits

## Purpose
Provide an operator-style terminal dashboard to observe pipeline runs, inspect stage workflow and source health, view generated markdown, and manage discovery inputs.

## Related Backend Feature
- Run/API behavior is documented in `docs/features/api-run-control/README.md`.

## Boundaries
- UI never executes trades or broker actions.
- Source edits apply to future runs only.
- Markdown remains canonical report output.

## Panels
| Panel | Purpose |
|---|---|
| Run control | Start run and inspect recent run IDs |
| Workflow timeline | Show per-stage status and record counts |
| Source health | Show per-source status, latency, and errors |
| Markdown report | Render canonical report text |
| Source config | Edit X accounts and subreddit lists |

## TODOs / Tech Debt
- [ ] Add pagination + filters for run history.
- [ ] Replace polling with SSE when API events are ready.
- [ ] Add auth for config-edit and run-trigger actions.

---
*Last update: 2026-04-12 - Scoped monitor doc to frontend UI and linked API feature doc.*
