---
name: fix
description: Diagnose and fix a bug with root-cause-first workflow.
---

# Fix: $ARGUMENTS

Investigate and fix the issue with minimal targeted changes.

## Workflow

1. Reproduce or characterize failure.
2. Find root cause (not only symptom).
3. Propose fix plan (files + verification).
4. Implement focused fix.
5. Validate with relevant tests/checks.
6. Report cause, fix, and regression risk.

## Rules

- Check relevant `.claude/**/CLAUDE.md` for known gotchas.
- Prefer smallest safe patch.
