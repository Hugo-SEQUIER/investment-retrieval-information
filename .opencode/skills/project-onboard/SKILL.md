---
name: project-onboard
description: Onboard an existing repo into the vault with a practical first snapshot.
---

# Project onboard: $ARGUMENTS

Import current repo context into `$CLAUDE_VAULT`.

## Workflow

1. Analyze repo (docs, stack, structure, git activity, TODO/FIXME markers).
2. Present onboarding summary and proposed vault files.
3. Wait for confirmation.
4. Create/update project files:
   - `_project.md`, `kanban.md`, `versions.md`
   - initial changelog entry
   - optional ADR stubs for major detected architecture choices
5. Return what was created and what needs manual review.

## Rules

- Never edit source code; vault files only.
- Keep generated content concise and clearly marked as auto-generated.
- If git or docs are missing, skip gracefully.
- Cap seeded kanban tasks to the most relevant items.
