# Ranking and Scoring - Overview

## Quick Reference
- **Key files**: `src/ranking/signals.py`, `src/ranking/score.py`, `src/ranking/rank.py`
- **Dependencies**: `langchain`, `sqlite3`
- **Patterns**: weighted signal scoring, thresholding, explainable ranking notes

## Architecture
Aggregate discovery and enrichment signals into a final score per company. Rank candidates by signal quality, AI relevance, novelty, and confidence while preserving short score explanations.

## Key Components
| Component | Purpose |
|-----------|---------|
| Signal builder | Computes mention, novelty, and relevance features |
| Scoring engine | Applies weighted scoring policy |
| Ranker | Produces sorted shortlist with rationale snippets |

## Conventions
- Keep scoring deterministic for reproducibility.
- Record score breakdown fields for auditability.
- Separate source-quality signal from pure mention volume.

## Gotchas
- Viral noise can dominate without source-quality weighting.
- Sparse data can inflate novelty unless smoothed.

## TODOs / Tech Debt
- [ ] Define v1 scoring weights and guardrails.
- [ ] Add daily stability checks for rank drift.

---
*Last update: 2026-04-11 - Initial feature documentation scaffold.*
