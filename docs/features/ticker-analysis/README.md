# Ticker and Theme Analysis - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/extraction/service.py` (legacy base)
- **Dependencies**: mid-tier LLM route + Hermes web research
- **Patterns**: compact analysis records, claim typing, follow-up questions

## Purpose
Convert filtered posts into concise ticker/theme analysis items suitable for a
daily investment research digest.

## Contract
- Input: kept posts from filtering stage.
- Output: analysis items with fields:
  - `item_id`
  - `post_id`
  - `tickers`
  - `themes`
  - `claim_summary`
  - `claim_type` (`fact` | `opinion` | `rumor` | `hypothesis`)
  - `web_research_notes` (optional)
  - `follow_up_questions`

## Subagent Boundary
- Analyzer agent can call Hermes web research when needed.
- Keep analysis compact; do not produce long-form due diligence.
- No ranking, resolution, or enrichment in this stage.

## Failure Handling
- If web research is unavailable, emit analysis item with caveat.
- Keep per-item errors isolated; one failure must not block the whole stage.

## TODOs / Tech Debt
- [ ] Define strict JSON schema for analyzer output.
- [ ] Add contradiction flags when claims conflict across sources.

---
*Last update: 2026-04-13 - Initial Hermes foundation analysis doc.*
