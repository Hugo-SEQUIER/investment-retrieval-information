---
name: memory-write-skill
description: Save a learning, decision, or reusable pattern in vault memory.
---

# Memory write: $ARGUMENTS

Write memory note in `$CLAUDE_VAULT` (fallback default path).

## Arguments

`/memory-write <learning|decision|knowledge> <title>`

## Target paths

- `learning` -> `global/learnings/YYYY-MM-DD-<slug>.md`
- `decision` -> `global/decisions/YYYY-MM-DD-<slug>.md`
- `knowledge` -> `global/knowledge/patterns/YYYY-MM-DD-<slug>.md`

## Rules

- One focused note per file.
- Use short structured sections (Context, Decision/Takeaway, Consequences/Gotchas).
- Use `[[wikilinks]]` for related notes when relevant.
- Confirm saved path and title after write.
