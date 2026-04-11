---
name: review
description: Review code or diffs for correctness, risk, and maintainability.
---

# Review: $ARGUMENTS

Review target files or recent changes.

## Focus

- Correctness and edge cases
- Security and auth/data exposure
- Performance hotspots
- Maintainability and complexity

## Output

For each issue:
`[SEVERITY] category - file:line - problem - suggested fix`

Severity scale: `critical`, `warning`, `suggestion`.

End with totals and top-priority fixes.
