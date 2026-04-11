---
name: refactor
description: Improve code structure without behavior changes.
---

# Refactor: $ARGUMENTS

Refactor incrementally, preserving behavior.

## Workflow

1. Validate baseline (tests/checks if available).
2. Identify high-value refactors (duplication, naming, complexity, boundaries).
3. Apply small changes in sequence.
4. Re-run relevant checks.
5. Summarize what changed and why.

## Rules

- No feature additions.
- No behavior changes unless explicitly requested.
- If architecture/doc behavior changed, suggest `.claude/**/CLAUDE.md` updates.
