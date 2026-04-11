# Company Resolution - Overview

## Quick Reference
- **Key files**: `src/resolution/entity_matcher.py`, `src/resolution/ticker_registry.py`, `src/resolution/resolve.py`
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
- Keep unresolved mentions for later review, do not silently drop.
- Log reason codes for low-confidence mappings.

## Gotchas
- Multiple companies can share near-identical names.
- ADR/local listings can create duplicate ticker confusion.

## TODOs / Tech Debt
- [ ] Define canonical ID format for resolved entities.
- [ ] Add unresolved queue reporting in daily digest appendix.

---
*Last update: 2026-04-11 - Initial feature documentation scaffold.*
