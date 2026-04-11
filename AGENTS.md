# AI Equity Discovery (Project Overrides)

Project-only constraints; rely on global and `.opencode` router rules for shared behavior.

## Scope Guardrails

- Discovery and research only. Never implement trade execution.
- Treat X/Reddit as discovery signals, not factual truth.
- Verify company facts from reputable public sources.
- Normalize market cap and revenue to USD in user-facing output.

## Pipeline Boundaries

- Keep strict stage separation: discovery -> extraction -> resolution -> enrichment -> ranking -> reporting.
- Prefer explicit schemas and auditable scoring in v1.

## Docs Routing

- Start from `README.md` and `docs/feature-map.md`.
- Update matching `docs/features/*` docs whenever feature behavior changes.
