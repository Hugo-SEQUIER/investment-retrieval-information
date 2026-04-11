# Decision Index

## Purpose
- Fast lookup table for major technical or product decisions.

| Decision ID | Title | Status | Date | Owner | Record |
|---|---|---|---|---|---|
| DEC-001 | Social media is discovery only, not source of truth | accepted | 2026-04-11 | core team | `README.md` |
| DEC-002 | V1 persistence uses SQLite | accepted | 2026-04-11 | core team | `README.md` |
| DEC-003 | Orchestration uses LangChain + LangGraph agents | accepted | 2026-04-11 | core team | `README.md` |
| DEC-004 | Canonical company identity is `exchange:ticker` | accepted | 2026-04-12 | core team | `docs/features/company-resolution/README.md` |
| DEC-005 | Run discovery on both X and Reddit for global coverage | accepted | 2026-04-12 | core team | `docs/features/social-discovery/README.md` |
| DEC-006 | Markdown is the canonical report output in v1 | accepted | 2026-04-12 | core team | `docs/features/digest-reporting/README.md` |
| DEC-007 | Enrichment source precedence uses reliability tiers (official -> exchange -> reference -> news) | accepted | 2026-04-12 | core team | `src/ai_equity_discovery/enrichment/policy.py` |
| DEC-008 | Subagent boundaries: Twitter+Reddit are discovery only; Web is enrichment only | accepted | 2026-04-12 | core team | `docs/features/social-discovery/README.md` |
| DEC-009 | Frontend/API is v1.1 scope with Next.js + TypeScript + shadcn + Tailwind | accepted | 2026-04-12 | core team | `docs/features/frontend-terminal-monitor/README.md` |
| DEC-010 | v1.1 run triggering uses single active run policy and subprocess execution model | accepted | 2026-04-12 | core team | `docs/features/api-run-control/README.md` |
| DEC-011 | v1.1 live monitor uses polling-first updates before SSE/WebSocket | accepted | 2026-04-12 | core team | `docs/features/frontend-terminal-monitor/README.md` |

## Routing
- Proposed first: `docs/decision-index.md`
- Accepted first: `docs/decision-index.md`
- Superseded archive: `docs/decisions/archive/`

## Maintenance
- Last reviewed: 2026-04-12
- Update trigger: new or changed decision
