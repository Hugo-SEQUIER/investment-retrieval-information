---
name: investment-research
description: Primary skill for interacting with the AI Equity Discovery pipeline — run research, manage watched accounts, query signals.
category: research
---

# Investment Research Skill

Load this skill before running any pipeline command or querying the database.

## Project Context

- **Path:** `/root/investment-retrieval-information`
- **Vault:** `~/Documents/Obsidian Vault`
- **Database:** SQLite at `data/discovery.sqlite`
- **Report:** `reports/daily.md` (latest pipeline output)

## Pipeline Commands

All commands run from project root with `.venv` activated:

```bash
cd /root/investment-retrieval-information
source .venv/bin/activate
```

### Run full pipeline
```bash
python -m ai_equity_discovery run-research
```
Lookback is 1 day by default.

### Query signals
```bash
python -m ai_equity_discovery query ticker <SYMBOL>
python -m ai_equity_discovery query theme <keyword>
python -m ai_equity_discovery query report      # show latest report
python -m ai_equity_discovery query runs         # show recent runs
```

### Manage watched accounts
```bash
python -m ai_equity_discovery accounts list
python -m ai_equity_discovery accounts add <username>        # Twitter
python -m ai_equity_discovery accounts remove <username>
python -m ai_equity_discovery accounts add-subreddit <name>
python -m ai_equity_discovery accounts remove-subreddit <name>
```

## Tracked Themes

The pipeline flags signals around these themes:
- hyperscaler-capex
- optical-interconnect
- memory-upcycle
- advanced-packaging
- datacenter-energy
- gpu-demand

## Known Small-Cap Gems (sub-$1B) in Same Sector

These appear in pipeline reports and are worth watching:
- AAOI (Applied Optoelectronics) — optical networking for hyperscalers
- SIVE — laser supplier for MRVL/JBL
- IQE — epiwafer supplier
- SPIR — space/weather AI
- AXTI, SOI — InP/SOI wafer monopolies
- HPS — optical components
- GSIT — SRAM for networking (~$250-300M, true small-cap)
- CEVA — DSP IP licensing (~$900M-1B)

## Pipeline Architecture

```
fetch (X + Reddit) -> filter -> analyze -> report -> memory (Obsidian vault)
```

## Notes

- The `discovery-agent` stage may skip if the model isn't ready — annotations won't run but pipeline completes.
- Reddit typically returns 0 posts; X returns the signal bulk.
- Token auth: uses `TWITTER_AUTH_TOKEN` from `.env` (token pool fallback supported).
- The `investment-research` skill file itself was missing on first load — if it errors, recreate from this content.
