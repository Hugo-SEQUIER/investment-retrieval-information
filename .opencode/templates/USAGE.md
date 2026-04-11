# Template Usage

These templates are generic routing indexes, not detailed documentation.

## What each template is for
- `templates/docs/_index.md`: top-level docs router.
- `templates/architecture/_index.md`: architecture router by component/boundary.
- `templates/docs/decision-index.md`: index of major decisions and ADR-like records.
- `templates/docs/feature-map.md`: feature-to-code/docs/tests routing table.

## When to use
- At project bootstrap.
- When docs become hard to navigate.
- After major architecture or feature changes.

## How to adapt in a project
1. Copy templates into your project under `.opencode/` (or docs root).
2. Replace placeholders (`[LIKE_THIS]`) with project values.
3. Keep entries short; link out to detailed docs.
4. Update only routing rows when structure changes.
