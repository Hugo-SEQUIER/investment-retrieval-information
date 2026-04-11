---
name: vault-search-skill
description: Search vault notes for relevant context before proposing decisions.
---

# Vault search: $ARGUMENTS

Search vault at `$CLAUDE_VAULT` or `C:\Users\Hugo\Documents\dev\ClaudeCodeVault`.

## Priority

1. `projects/<project>/architecture`, `docs`, `context`, `changelog`
2. `global/knowledge`, `global/decisions`, `global/learnings`
3. `projects/*` only if needed

## Rules

- Infer project from working directory.
- Read matched notes, do not rely only on filenames.
- Return max 5 relevant results per section.
- Never edit vault files.

## Output

- Query
- Project inferred
- Results by section with one-line relevance
- Missing sections / no matches
