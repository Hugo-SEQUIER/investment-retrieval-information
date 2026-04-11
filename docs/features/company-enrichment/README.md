# Company Enrichment - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/enrichment/service.py`, `src/ai_equity_discovery/enrichment/policy.py`, `src/ai_equity_discovery/enrichment/web_provider.py`, `src/ai_equity_discovery/enrichment/parsing.py`, `src/ai_equity_discovery/core/loaders.py`
- **Dependencies**: `httpx`, `beautifulsoup4`, `trafilatura`
- **Patterns**: source prioritization, citation-first outputs, currency normalization

## Architecture
For each resolved company, fetch factual profile fields from reputable sources and normalize key financial metrics to USD. Attach source citations and caveats to every enriched record.

## Key Components
| Component | Purpose |
|-----------|---------|
| Source fetcher | Retrieves and parses relevant public pages |
| Fact extractor | Extracts company description and financial fields |
| USD normalizer | Converts market cap and revenue to USD |
| Financial parser | Pulls labeled market cap and revenue values from extracted text |

## Conventions
- Prefer official IR/company sources first.
- Store source URL for every factual field.
- Mark stale or unverifiable financial values clearly.
- Apply reliability tiers in this order: official -> exchange -> reference -> news.

## Gotchas
- Financial units differ across sources (millions vs billions).
- Mixed reporting currencies can break comparisons without normalization.

## TODOs / Tech Debt
- [ ] Expand domain allowlist and move it to config.
- [ ] Replace static FX file with periodic provider-based refresh.

---
*Last update: 2026-04-12 - Added labeled financial parsing, FX config loading, and layered web enrichment mode.*
