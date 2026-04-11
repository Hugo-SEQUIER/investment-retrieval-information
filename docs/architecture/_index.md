# Architecture Index

## Purpose
- Routing map for architecture-level references.

## Components
| Component | Boundary | Primary Doc | Notes |
|---|---|---|---|
| Ingestion layer | External sources -> normalized raw posts | `docs/features/social-discovery/README.md` | Uses twscrape and PRAW |
| Extraction layer | Raw posts -> entities and themes | `docs/features/mention-extraction/README.md` | Tickers, company names, AI themes |
| Resolution layer | Mentions -> canonical public companies | `docs/features/company-resolution/README.md` | Dedup and confidence scoring |
| Enrichment layer | Companies -> factual profile in USD | `docs/features/company-enrichment/README.md` | Uses web research sources |
| Ranking layer | Enriched candidates -> ranked shortlist | `docs/features/ranking-scoring/README.md` | Multi-signal scoring |
| Reporting layer | Ranked shortlist -> daily digest | `docs/features/digest-reporting/README.md` | Markdown and Telegram-ready output |

## Cross-Cutting
- Decisions: `docs/decision-index.md`
- Feature mapping: `docs/feature-map.md`

## Maintenance
- Last reviewed: 2026-04-11
- Update trigger: architecture boundary changes
