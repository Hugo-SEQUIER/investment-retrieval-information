---
name: changelog-entry-skill
description: Create a structured changelog note for meaningful code changes.
---

# Changelog entry: $ARGUMENTS

Write changelog note in `$CLAUDE_VAULT` (fallback default path).

## Arguments

`/changelog-entry <version> <slug>`

## Workflow

1. Infer project from working directory.
2. Ensure `projects/<project>/changelog/<version>/` exists.
3. Compute next file as `NNN-<slug>.md`.
4. Infer summary from diff, commits, and touched files.
5. Draft entry with: metadata, what changed, why, how, tests, decisions, related.
6. Show concise preview and request confirmation before write.

## Rules

- Infer type/scope unless ambiguous.
- Keep "What changed" short (2-3 sentences).
- Add `[[versions.md#<version>]]` link.
- If first entry for version, suggest updating `versions.md`.
