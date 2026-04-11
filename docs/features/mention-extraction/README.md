# Mention Extraction - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/extraction/service.py`, `src/ai_equity_discovery/core/models.py`
- **Dependencies**: `re`, `langchain`
- **Patterns**: deterministic parsing first, LLM-assisted fallback, confidence scoring

## Architecture
Process normalized social posts to identify tickers, company names, and AI-related themes. Attach extraction confidence and keep source offsets when available.

## Key Components
| Component | Purpose |
|-----------|---------|
| Ticker parser | Detects exchange-style ticker mentions and variants |
| Company parser | Detects company names and aliases |
| Theme classifier | Tags AI value-chain themes (GPU, optics, power, etc.) |

## Conventions
- Prefer deterministic extraction before model-based extraction.
- Record extraction confidence per entity.
- Keep raw mention text alongside normalized fields.

## Gotchas
- Cashtags and common words can collide (for example: AI, ARM).
- Social shorthand causes false positives without context windows.

## TODOs / Tech Debt
- [ ] Build ticker disambiguation rules for ambiguous symbols.
- [ ] Add benchmark set for precision/recall tracking.

---
*Last update: 2026-04-12 - Added concrete extraction module paths.*
