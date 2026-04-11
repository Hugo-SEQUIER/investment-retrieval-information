---
name: update-docs
description: Update feature docs in `.claude/**/CLAUDE.md` after code changes.
---

# Update docs: $ARGUMENTS

Update the relevant `.claude/**/CLAUDE.md` files for changed features.

## Workflow

1. Read existing feature doc(s).
2. Compare with recent code changes.
3. Update only what changed: files, architecture notes, conventions, gotchas.
4. Keep existing structure and add/update short "Last update" note.

## Rules

- Keep concise and factual.
- Prefer delta updates over full rewrites.
