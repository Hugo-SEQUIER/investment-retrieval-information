# AI Equity Discovery (Project Overrides)

Project-only constraints; rely on global and `.opencode` router rules for shared behavior.

## Scope Guardrails

- Discovery and research only. Never implement trade execution.
- Treat X/Reddit as discovery signals, not factual truth.
- Verify company facts from reputable public sources.
- Normalize market cap and revenue to USD in user-facing output.

## Pipeline Boundaries

- Strict stage separation: fetch -> filter -> analyze -> report -> memory.
- Prefer explicit schemas and auditable scoring in v1.

## Interactive Commands

All commands run from project root (`/root/investment-retrieval-information`).

| Action | Command |
|--------|---------|
| List watched accounts | `python -m ai_equity_discovery accounts list` |
| Follow Twitter account | `python -m ai_equity_discovery accounts add <username>` |
| Unfollow Twitter account | `python -m ai_equity_discovery accounts remove <username>` |
| Add subreddit | `python -m ai_equity_discovery accounts add-subreddit <name>` |
| Remove subreddit | `python -m ai_equity_discovery accounts remove-subreddit <name>` |
| Run full pipeline | `python -m ai_equity_discovery run-research` |
| Query by ticker | `python -m ai_equity_discovery query ticker <SYMBOL>` |
| Query by theme | `python -m ai_equity_discovery query theme <keyword>` |
| Show latest report | `python -m ai_equity_discovery query report` |
| Show recent runs | `python -m ai_equity_discovery query runs` |

## Skill

- **investment-research** — primary skill for all pipeline interactions.
  Located at `.opencode/skills/investment-research/SKILL.md`.
  Load with `skill_view(name='investment-research')` before running any pipeline command.

## Docs Routing

- Start from `README.md` and `docs/feature-map.md`.
- Update matching `docs/features/*` docs whenever feature behavior changes.

## Vault Architecture

Obsidian vault: `~/Documents/Obsidian Vault`
- `Agents/memory/` — agent persistent notes (untouched by pipeline)
- `Projects/ai-equity-discovery-agent/research/` — pipeline research output

## Maintenance
- Last updated: 2026-04-14 — Added interactive commands and investment-research skill.