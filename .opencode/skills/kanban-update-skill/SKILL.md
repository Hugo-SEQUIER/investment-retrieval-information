---
name: kanban-update-skill
description: Add or move project tasks in vault kanban.
---

# Kanban update: $ARGUMENTS

Update `projects/<project>/kanban.md` in `$CLAUDE_VAULT` (fallback default vault path).

## Arguments

`/kanban-update <add|start|review|done|remove> <task>`

## Rules

- Infer project from current directory; ask only if ambiguous.
- Preserve all unrelated content/frontmatter.
- Fuzzy match task text when moving existing items.
- For `add`, infer a tag: `#feature|#fix|#refactor|#docs|#testing|#research|#chore`.
- For `done`, mark checkbox complete and add completion date.

## Output

- Action applied
- Task moved/created/removed
- Final section location
