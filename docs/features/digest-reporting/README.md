# Digest Reporting - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/reporting/markdown.py`, `src/ai_equity_discovery/pipeline/daily.py`, `src/ai_equity_discovery/cli.py`
- **Dependencies**: `jinja2` (optional), `python-telegram-bot` (optional)
- **Patterns**: concise ranked output, citation-ready notes, stable section ordering

## Architecture
Turn ranked enriched candidates into a daily markdown report and optional Telegram digest. Ensure each top name includes business context, USD metrics, AI relevance, and trend rationale.

## Key Components
| Component | Purpose |
|-----------|---------|
| Report builder | Composes canonical report payload |
| Markdown renderer | Produces daily markdown artifact |
| Telegram formatter | Produces concise digest-safe output |

## Conventions
- Keep top names section concise and comparable day to day.
- Include confidence/caveat notes for weakly resolved names.
- Preserve generated report date in UTC.

## Gotchas
- Message length limits require compact Telegram formatting.
- Missing enrichment fields should degrade gracefully, not fail report generation.

## TODOs / Tech Debt
- [ ] Finalize output schema for terminal + markdown + Telegram.
- [ ] Add snapshot tests for report formatting stability.

---
*Last update: 2026-04-12 - Added concrete reporting and pipeline module paths.*
