# Feature Map

## Purpose
- Routing map from feature to code, docs, tests, and operational checks.

| Feature | Product Scope | Backend | Frontend | Docs | Tests |
|---|---|---|---|---|---|
| Social discovery | Ingest curated X and Reddit sources daily | `src/ingestion/` | `N/A` | `docs/features/social-discovery/README.md` | `tests/ingestion/` |
| Mention extraction | Parse tickers, company names, themes from posts | `src/extraction/` | `N/A` | `docs/features/mention-extraction/README.md` | `tests/extraction/` |
| Company resolution | Map mentions to correct public companies | `src/resolution/` | `N/A` | `docs/features/company-resolution/README.md` | `tests/resolution/` |
| Company enrichment | Fetch company profile and normalize USD metrics | `src/enrichment/` | `N/A` | `docs/features/company-enrichment/README.md` | `tests/enrichment/` |
| Ranking and scoring | Score candidates by relevance and confidence | `src/ranking/` | `N/A` | `docs/features/ranking-scoring/README.md` | `tests/ranking/` |
| Daily digest reporting | Generate markdown and Telegram-ready summaries | `src/reporting/` | `N/A` | `docs/features/digest-reporting/README.md` | `tests/reporting/` |

## Entry Points
- New contributors: Social discovery -> `docs/features/social-discovery/README.md`
- Critical flows: Daily pipeline -> `docs/architecture/_index.md`

## Maintenance
- Last reviewed: 2026-04-11
- Update trigger: feature added or changed
