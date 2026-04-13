# AI Equity Discovery Agent

Daily research pipeline for **AI-related public equities**.

It fetches posts from **X/Twitter** and **Reddit**, filters low-signal noise,
analyzes tickers/themes with agent support, generates concise markdown reports,
and syncs research memory to Obsidian.

## Scope and Guardrails

- Discovery and research only (no trading or execution).
- Social media is discovery input, not factual truth.
- Pipeline stages stay strictly separated:
  `fetch -> filter -> analyze -> report -> memory`.

## Current Status

- Foundation direction is set to a minimal Hermes-friendly flow:
  `fetch -> filter -> analyze -> report -> memory`.
- Runtime pipeline now follows the same stage model.
- Markdown remains the canonical report output.

## How To Use This Project

### 1) Install dependencies

1) Install Python dependencies:

```bash
python -m pip install -e .
```

Install live-ingestion dependencies for X/Reddit:

```bash
python -m pip install ".[ingestion]"
```

### 2) Configure `.env`

Create a `.env` at repository root.

Required for live Reddit ingestion:

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT` (optional)

Optional for X ingestion:

- `TWITTER_AUTH_TOKEN` (or `SCWEET_AUTH_TOKEN`)
- `SCWEET_DB_ROTATE_DAILY` (optional, `true` to use daily DB files)
- `SCWEET_DB_DIR` (optional, default: `data/scweet` when rotation enabled)
- `SCWEET_DB_RETENTION_DAYS` (optional, default: `7`)
- `SCWEET_DB_PATH` (optional static path when rotation disabled)

Note: DB rotation resets local scraper state only; provider-side X limits may still apply.

Optional for agent-assisted filtering/analysis/reporting (OpenRouter):

- `OPENROUTER_API_KEY`
- `OPENROUTER_MODEL` (global default model)
- `OPENROUTER_MODEL_DISCOVERY` (cheap model for high-volume filtering)
- `OPENROUTER_MODEL_REPORTING` (reserved for report synthesis routing)
- `DISCOVERY_AGENT_ENABLED` (default: `true`; filtering/analyze assistant)
- `AGENT_OUTPUT_LANGUAGE` (default: `en`)
- `BOOTSTRAP_LOOKBACK_DAYS` (default: `7`; used on first run)
- `DAILY_LOOKBACK_DAYS` (default: `1`; used on subsequent runs)

Minimal example:

```env
OPENROUTER_API_KEY=...
OPENROUTER_MODEL=qwen/qwen3.6-plus
OPENROUTER_MODEL_DISCOVERY=qwen/qwen2.5-7b-instruct
DISCOVERY_AGENT_ENABLED=true
AGENT_OUTPUT_LANGUAGE=en
BOOTSTRAP_LOOKBACK_DAYS=7
DAILY_LOOKBACK_DAYS=1
REDDIT_CLIENT_ID=...
REDDIT_CLIENT_SECRET=...
```

### 3) Run the pipeline (CLI)

First run (bootstrap): collects up to last 7 days by default.
Daily runs after that: collect last 1 day by default.
Report lines focus on actionable signal summaries and concise ticker/theme
analysis.

Run command:

```bash
$env:PYTHONPATH="src"; python -m ai_equity_discovery --db data/discovery.sqlite --output reports/daily.md
```

CLI prints live stage progress logs. Target stage model is
`fetch/filter/analyze/report/memory`.

The command writes:
- stage artifacts in SQLite
- source health per run
- markdown report output file

## Project Structure

```text
src/ai_equity_discovery/
  core/            # config, models, serialization, sqlite storage
  ingestion/       # X/Reddit adapters + parallel fetch collection
  extraction/      # ticker/theme extraction helpers used by analysis
  filtering/       # low-signal and dedup filtering stage
  analysis/        # claim typing + ticker/theme analysis stage
  reporting/       # markdown report rendering
  memory/          # Obsidian sync for research memory
  pipeline/        # daily orchestration with stage instrumentation
  cli.py           # pipeline entrypoint

docs/
  feature-map.md
  architecture/_index.md
  features/*
```

## Agent Notes

- Current pipeline orchestration remains deterministic by stage.
- Hermes target model uses focused subagents:
  fetcher -> cheap filter -> analyzer (+ web research) -> reporter -> memory writer.
- Ranking, resolution, and enrichment are removed from target architecture.

## Example Output

```text
AI EQUITY DISCOVERY - 2026-04-11

Signals to review:
1. NVDA - repeated AI data-center capex mentions across X and Reddit.
   - Claim type: opinion + earnings expectation
   - Follow-up: verify new capex guidance from primary sources

Theme highlights:
- AI data-center power bottlenecks mentioned by multiple operators.
```
