---
name: plan-review-skill
description: Build a docs-first implementation plan, stress-test it, then wait for approval.
---

# Plan review: $ARGUMENTS

Create a plan first. Do not implement code yet.

## Workflow

1. Delegate repository discovery to `repo-explorer`:
   - locate relevant `_index`, `decision-index`, `feature-map`, and `.claude/**/CLAUDE.md`
   - return only the most relevant paths and key lines
2. Delegate documentation triage to `doc-router`:
   - identify canonical docs to follow
   - list missing or conflicting information
3. Use `/vault-search <query>` only if doc gaps remain.
4. Read source code only as targeted fallback for unresolved gaps.
5. Draft plan: goal, files, steps, edge cases, risks.
6. Delegate plan critique:
   - prefer `plan-critic` for normal review
   - use `agent: plan` when high-stakes planning quality is required
7. Return final revised plan and wait for approval.

## Output

- Documentation Read
- Vault Context (if used)
- Draft Plan
- Review Findings
- Final Plan
- Open Questions

## Routing Rules

- Keep main context minimal by using subtasks for discovery and critique.
- Do not run broad code exploration in the main thread.
