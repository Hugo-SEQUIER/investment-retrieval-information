# Company Resolution - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/resolution/registry.py`, `src/ai_equity_discovery/resolution/service.py`
- **Dependencies**: `sqlite3`, `httpx`
- **Patterns**: canonical entity mapping, alias matching, confidence thresholds

## Architecture
Resolve extracted mentions into canonical public companies using ticker registries, alias maps, and context clues. Produce one resolved entity per candidate mention cluster with confidence notes.

## Key Components
| Component | Purpose |
|-----------|---------|
| Ticker registry | Maintains ticker-to-company/exchange mapping |
| Alias matcher | Maps company aliases to canonical entities |
| Resolver | Combines mention evidence into final company resolution |

## Conventions
- Include exchange and country in canonical entity keys.
- Canonical ID format is `exchange:ticker`.
- Keep unresolved mentions for later review, do not silently drop.
- Log reason codes for low-confidence mappings.

## Gotchas
- Multiple companies can share near-identical names.
- ADR/local listings can create duplicate ticker confusion.

## TODOs / Tech Debt
- [ ] Add unresolved queue reporting in daily digest appendix.

---
*Last update: 2026-04-12 - Canonical ID format locked to exchange:ticker (DEC-004).*
