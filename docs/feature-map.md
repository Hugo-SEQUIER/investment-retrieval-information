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
| API run control | Start runs, expose run/stage/source/report APIs, and manage source inputs | `src/ai_equity_discovery/api/` | `N/A` | `docs/features/api-run-control/README.md` | `tests/test_pipeline.py` |
| Daily pipeline | Orchestrate stage execution with run/stage lifecycle persistence | `src/ai_equity_discovery/pipeline/` | `N/A` | `docs/features/daily-pipeline/README.md` | `tests/test_pipeline.py` |
| Persistence run state | Store runs, stage status, source health, and reports in SQLite | `src/ai_equity_discovery/core/database.py` | `N/A` | `docs/features/persistence-run-state/README.md` | `tests/test_pipeline.py` |
| Frontend terminal monitor | Observe runs, stage workflow, source health, markdown, and source config edits | `src/ai_equity_discovery/api/` | `frontend/app/page.tsx` | `docs/features/frontend-terminal-monitor/README.md` | `frontend/app/page.tsx` |

## Entry Points
- New contributors: Social discovery -> `docs/features/social-discovery/README.md`
- Critical flows: Daily pipeline -> `docs/architecture/_index.md`

## Maintenance
- Last reviewed: 2026-04-12
- Update trigger: feature added or changed
