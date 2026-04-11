---
name: session-start
description: Load vault context at session start.
---

# Session start

Load minimal context from `$CLAUDE_VAULT` before work.

## Steps

1. Load global prefs: `global/preferences/{code-style,stack,workflow}.md` when present.
2. Infer active project from cwd.
3. Read `projects/<project>/{_project.md,kanban.md,versions.md}` when present.
4. Optionally read latest scratch note and open proposed ADRs.
5. Return concise status: version, in-progress tasks, open decisions, suggested next action.

## Rules

- Read-only; never edit on session start.
- Skip missing files without error.
- Keep output short and actionable.
