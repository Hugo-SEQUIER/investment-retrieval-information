# Company Enrichment - Overview

## Quick Reference
- **Key files**: `src/enrichment/research.py`, `src/enrichment/financials.py`, `src/enrichment/usd_normalization.py`
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

## Conventions
- Prefer official IR/company sources first.
- Store source URL for every factual field.
- Mark stale or unverifiable financial values clearly.

## Gotchas
- Financial units differ across sources (millions vs billions).
- Mixed reporting currencies can break comparisons without normalization.

## TODOs / Tech Debt
- [ ] Define source reliability tiers.
- [ ] Add FX conversion date and method to enrichment output.

---
*Last update: 2026-04-11 - Initial feature documentation scaffold.*
