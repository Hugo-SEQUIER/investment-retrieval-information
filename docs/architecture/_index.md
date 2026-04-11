# Architecture Index

## Purpose
- Routing map for architecture-level references.

## Components
| Component | Boundary | Primary Doc | Notes |
|---|---|---|---|
| Ingestion layer | External sources -> normalized raw posts | `docs/features/social-discovery/README.md` | Uses Scweet and PRAW |
| Extraction layer | Raw posts -> entities and themes | `docs/features/mention-extraction/README.md` | Tickers, company names, AI themes |
| Resolution layer | Mentions -> canonical public companies | `docs/features/company-resolution/README.md` | Dedup and confidence scoring |
| Enrichment layer | Companies -> factual profile in USD | `docs/features/company-enrichment/README.md` | Uses web research sources |
| Ranking layer | Enriched candidates -> ranked shortlist | `docs/features/ranking-scoring/README.md` | Multi-signal scoring |
| Reporting layer | Ranked shortlist -> daily digest | `docs/features/digest-reporting/README.md` | Markdown and Telegram-ready output |
| Daily pipeline orchestrator | Coordinates stage execution and lifecycle updates | `docs/features/daily-pipeline/README.md` | Strict stage order + status instrumentation |
| Persistence layer | Stores run state, stage status, source health, and reports | `docs/features/persistence-run-state/README.md` | SQLite-backed observability and payload storage |
| Run control API layer | Exposes run/config/report endpoints | `docs/features/api-run-control/README.md` | FastAPI + subprocess launcher model |
| Operator monitor UI layer | Terminal-style run monitoring and source configuration | `docs/features/frontend-terminal-monitor/README.md` | Next.js + shadcn + Tailwind frontend |

## Cross-Cutting
- Decisions: `docs/decision-index.md`
- Feature mapping: `docs/feature-map.md`

## Maintenance
- Last reviewed: 2026-04-12
- Update trigger: architecture boundary changes
