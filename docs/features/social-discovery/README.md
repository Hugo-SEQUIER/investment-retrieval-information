# Social Discovery - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/ingestion/providers.py`, `src/ai_equity_discovery/ingestion/service.py`, `src/ai_equity_discovery/cli.py`
- **Dependencies**: `Scweet`, `praw` or `asyncpraw`
- **Patterns**: curated source ingestion, idempotent daily collection, raw post normalization

## Architecture
Collect posts from curated X accounts and selected Reddit communities. Normalize each item into a shared raw schema with source metadata, timestamp, author, and engagement fields.

## Key Components
| Component | Purpose |
|-----------|---------|
| Twitter subagent | Pulls recent posts from curated X accounts |
| Reddit subagent | Pulls recent posts/comments from selected subreddits |
| Normalizer | Converts source-specific payloads into a common raw format |
| Deep Agent annotator (shadow mode) | Adds multilingual-understanding annotations in English without filtering out posts |

## Boundaries
- Discovery subagents (Twitter, Reddit) only collect and normalize social signals.
- Web research belongs to analysis, not fetch.
- Fetch does not rank or validate claims.

## Conventions
- Preserve original post text and source link for traceability.
- Store ingestion timestamps in UTC.
- Keep source allowlists explicit and versioned.
- Persist per-source ingestion health per run (success, post count, latency, error).
- First run uses a bootstrap lookback window (default: 7 days), then daily runs use 1-day lookback.

## Gotchas
- API/rate limits vary by source and account state.
- Duplicate items can appear across polling windows.
- Scweet can return `daily_limit` lease warnings; in that case X may report `posts=0` for the run.
- Rotating Scweet DB files helps local state hygiene but does not reset provider-side daily quotas.

## TODOs / Tech Debt
- [ ] Finalize curated source list and refresh cadence.
- [ ] Add robust retry and backoff policy.

---
*Last update: 2026-04-13 - Updated boundaries for fetch/filter/analyze pipeline.*
