# Feature Map

## Purpose
- Routing map from feature to code, docs, tests, and operational checks.

| Feature | Product Scope | Backend | Frontend | Docs | Tests |
|---|---|---|---|---|---|
| Social fetch | Ingest curated X and Reddit sources daily | `src/ai_equity_discovery/ingestion/` | `N/A` | `docs/features/social-discovery/README.md` | `tests/test_pipeline.py` |
| **Account management** | Dynamic watchlist for X accounts and subreddits | `src/ai_equity_discovery/core/accounts.py` | `N/A` | `docs/features/social-discovery/README.md` | `tests/test_pipeline.py` |
| Content filtering | Drop low-signal/duplicate content before analysis | `src/ai_equity_discovery/filtering/` | `N/A` | `docs/features/content-filtering/README.md` | `tests/test_pipeline.py` |
| Ticker and theme analysis | Analyze filtered posts into concise ticker/theme claims | `src/ai_equity_discovery/extraction/` | `N/A` | `docs/features/ticker-analysis/README.md` | `tests/test_pipeline.py` |
| Daily digest reporting | Generate concise markdown summaries for review | `src/ai_equity_discovery/reporting/` | `N/A` | `docs/features/digest-reporting/README.md` | `tests/test_pipeline.py` |
| Obsidian memory sync | Write/update investment research notes with overwrite policy | `src/ai_equity_discovery/memory/` | `N/A` | `docs/features/obsidian-memory/README.md` | `tests/test_pipeline.py` |
| Daily pipeline | Orchestrate stage execution with run/stage lifecycle persistence | `src/ai_equity_discovery/pipeline/` | `N/A` | `docs/features/daily-pipeline/README.md` | `tests/test_pipeline.py` |
| Persistence run state | Store runs, stage status, source health, and reports in SQLite | `src/ai_equity_discovery/core/database.py` | `N/A` | `docs/features/persistence-run-state/README.md` | `tests/test_pipeline.py` |

## Entry Points
- New contributors: Social fetch -> `docs/features/social-discovery/README.md`
- Critical flows: Daily pipeline -> `docs/architecture/_index.md`

## Maintenance
- Last reviewed: 2026-04-14
- Update trigger: feature added or changed
