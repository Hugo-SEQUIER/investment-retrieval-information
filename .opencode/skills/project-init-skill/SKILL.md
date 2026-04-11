---
name: project-init-skill
description: Create minimal vault scaffold for a new project.
---

# Project init: $ARGUMENTS

Create project scaffold in `$CLAUDE_VAULT` (fallback default path).

## Arguments

`/project-init <project-name>`

## Create

- `projects/<project>/_project.md`
- `projects/<project>/kanban.md`
- `projects/<project>/versions.md`
- `projects/<project>/changelog/v0.0.0/001-project-init.md`
- `projects/<project>/{architecture,docs,context,scratch}/...` minimal folders

## Rules

- Use kebab-case project folder name.
- Pre-fill files with concise starter templates.
- If target exists, do not overwrite without confirmation.

## Output

- Created paths
- Initial version
- Suggested next commands (`/session-start`, `/kanban-update`)
