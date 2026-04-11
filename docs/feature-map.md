# Feature Map

## Purpose
- Routing map from feature to code, docs, tests, and operational checks.

| Feature | Product Scope | Backend | Frontend | Docs | Tests |
|---|---|---|---|---|---|
| Social discovery | Ingest curated X and Reddit sources daily | `src/ai_equity_discovery/ingestion/` | `frontend/components/source-config-form.tsx` | `docs/features/social-discovery/README.md` | `tests/test_pipeline.py` |
| Mention extraction | Parse tickers, company names, themes from posts | `src/ai_equity_discovery/extraction/` | `N/A` | `docs/features/mention-extraction/README.md` | `tests/test_pipeline.py` |
| Company resolution | Map mentions to correct public companies | `src/ai_equity_discovery/resolution/` | `N/A` | `docs/features/company-resolution/README.md` | `tests/test_pipeline.py` |
| Company enrichment | Fetch company profile and normalize USD metrics | `src/ai_equity_discovery/enrichment/` | `N/A` | `docs/features/company-enrichment/README.md` | `tests/test_pipeline.py` |
| Ranking and scoring | Score candidates by relevance and confidence | `src/ai_equity_discovery/ranking/` | `N/A` | `docs/features/ranking-scoring/README.md` | `tests/test_pipeline.py` |
| Daily digest reporting | Generate markdown and Telegram-ready summaries | `src/ai_equity_discovery/reporting/` | `frontend/components/markdown-panel.tsx` | `docs/features/digest-reporting/README.md` | `tests/test_pipeline.py` |
| Frontend terminal monitor | Observe runs, stage workflow, source health, and markdown outputs | `src/ai_equity_discovery/api/` | `frontend/app/page.tsx` | `docs/features/frontend-terminal-monitor/README.md` | `tests/test_pipeline.py` |

## Entry Points
- New contributors: Social discovery -> `docs/features/social-discovery/README.md`
- Critical flows: Daily pipeline -> `docs/architecture/_index.md`

## Maintenance
- Last reviewed: 2026-04-12
- Update trigger: feature added or changed
