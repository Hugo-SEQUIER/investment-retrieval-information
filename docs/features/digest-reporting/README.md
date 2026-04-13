# Digest Reporting - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/reporting/markdown.py`, `src/ai_equity_discovery/pipeline/daily.py`, `src/ai_equity_discovery/cli.py`
- **Dependencies**: `jinja2` (optional), `python-telegram-bot` (optional)
- **Patterns**: concise non-ranked output, citation-ready notes, stable section ordering

## Architecture
Turn analyzed items into a concise daily markdown report and optional Telegram
digest. Focus on high-signal claims, ticker/theme summaries, and concrete
follow-up questions.

## Key Components
| Component | Purpose |
|-----------|---------|
| Report builder | Composes canonical report payload |
| Markdown renderer | Produces daily markdown artifact |
| Telegram formatter | Produces concise digest-safe output |

## Conventions
- Keep report sections concise and comparable day to day.
- Keep each analyzed item short: claim, source context, and follow-up.
- Preserve generated report date in UTC.
- Avoid ranking language (no top-N ordering in the canonical report).

## Gotchas
- Message length limits require compact Telegram formatting.
- Over-analysis can make reports noisy; enforce compact section caps.

## TODOs / Tech Debt
- [ ] Finalize output schema for terminal + markdown + Telegram.
- [ ] Add snapshot tests for report formatting stability.

---
*Last update: 2026-04-13 - Reporting reframed around analyzed items (no ranking).*
