# Social Discovery - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/ingestion/providers.py`, `src/ai_equity_discovery/core/accounts.py`, `src/ai_equity_discovery/cli.py`
- **Dependencies**: `Scweet`, `praw` or `asyncpraw`
- **Patterns**: dynamic source registry, idempotent daily collection, raw post normalization

## Architecture
Collect posts from curated X accounts and selected Reddit communities. Normalize each item into a shared raw schema with source metadata, timestamp, author, and engagement fields.

## Account Management

Accounts are stored in `config/watched_accounts.json` and managed via CLI (no manual editing required):

```bash
# List all watched accounts
python -m ai_equity_discovery accounts list

# Add/remove Twitter accounts
python -m ai_equity_discovery accounts add <username>
python -m ai_equity_discovery accounts remove <username>

# Add/remove subreddits
python -m ai_equity_discovery accounts add-subreddit <name>
python -m ai_equity_discovery accounts remove-subreddit <name>
```

At pipeline runtime, accounts are loaded from `config/watched_accounts.json` (replacing the older static `config/sources.json`).

## Key Components
| Component | Purpose |
|-----------|---------|
| Twitter subagent | Pulls recent posts from curated X accounts |
| Reddit subagent | Pulls recent posts/comments from selected subreddits |
| Account registry (`core/accounts.py`) | JSON-backed CRUD for watched accounts |
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

## Token Pool (Fallback on Rate Limiting)

The `ScweetAdapter` supports multiple X auth tokens with automatic fallback:

```bash
# Comma-separated list — adapter rotates through tokens on rate-limit errors
TWITTER_AUTH_TOKENS=token1,token2,token3
```

When a token hits X's daily rate limit, the adapter automatically rotates to the next token and retries. If all tokens are exhausted, the pipeline raises a clear error telling you to wait for the daily reset.

**Token format:** X auth_token cookie values from your browser session.

## TODOs / Tech Debt
- [ ] Finalize curated source list and refresh cadence.
- [ ] Add robust retry and backoff policy.

---
*Last update: 2026-04-14 - Added token pool fallback for X ingestion.*
