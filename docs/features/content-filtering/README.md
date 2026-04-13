# Content Filtering - Overview

## Quick Reference
- **Key files**: planned
- **Dependencies**: cheap LLM route + deterministic dedup rules
- **Patterns**: keep/drop gate, explicit reasons, low-cost triage

## Purpose
Reduce social noise before analysis by dropping low-signal, duplicate, and
off-topic content.

## Contract
- Input: normalized fetched posts.
- Output: one decision per post with fields:
  - `post_id`
  - `keep` (bool)
  - `reason_code`
  - `confidence`
  - `dedup_key`

## Subagent Boundary
- Filter agent uses a cheap model.
- No web research in this stage.
- No ranking in this stage.

## Failure Handling
- If model fails, fallback to deterministic baseline filters.
- If all items are dropped, reporting still runs with an explicit empty summary.

## TODOs / Tech Debt
- [ ] Define production reason-code dictionary.
- [ ] Add regression fixtures for false positive/false negative drift.

---
*Last update: 2026-04-13 - Initial Hermes foundation filtering doc.*
