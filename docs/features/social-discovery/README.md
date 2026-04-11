# Social Discovery - Overview

## Quick Reference
- **Key files**: `src/ingestion/x_sources.py`, `src/ingestion/reddit_sources.py`, `src/ingestion/collect.py`
- **Dependencies**: `twscrape`, `praw` or `asyncpraw`
- **Patterns**: curated source ingestion, idempotent daily collection, raw post normalization

## Architecture
Collect posts from curated X accounts and selected Reddit communities. Normalize each item into a shared raw schema with source metadata, timestamp, author, and engagement fields.

## Key Components
| Component | Purpose |
|-----------|---------|
| X collector | Pulls recent posts from curated X accounts |
| Reddit collector | Pulls recent posts/comments from selected subreddits |
| Normalizer | Converts source-specific payloads into a common raw format |

## Conventions
- Preserve original post text and source link for traceability.
- Store ingestion timestamps in UTC.
- Keep source allowlists explicit and versioned.

## Gotchas
- API/rate limits vary by source and account state.
- Duplicate items can appear across polling windows.

## TODOs / Tech Debt
- [ ] Finalize curated source list and refresh cadence.
- [ ] Add robust retry and backoff policy.

---
*Last update: 2026-04-11 - Initial feature documentation scaffold.*
