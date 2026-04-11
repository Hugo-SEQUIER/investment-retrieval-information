# AI Equity Discovery Agent

Daily research pipeline for **AI-related public equities**.

It discovers candidates from **X/Twitter** and **Reddit**, resolves companies, enriches facts from reputable sources, normalizes financials to **USD**, ranks ideas, and outputs a markdown digest.

## Scope and Guardrails

- Discovery and research only (no trading or execution).
- Social media is discovery input, not factual truth.
- Company facts are verified from reputable public sources.
- User-facing market cap and revenue are always normalized to USD.
- Pipeline stages stay strictly separated:
  `discovery -> extraction -> resolution -> enrichment -> ranking -> reporting`.

## Current Status

- v1 pipeline and storage are implemented in Python.
- v1.1 includes FastAPI run-monitoring endpoints and a Next.js terminal-style frontend.
- Markdown is the canonical report output.

## Quick Start (Pipeline)

1) Install Python dependencies:

```bash
python -m pip install -e .
python -m pip install ".[api]"
```

2) (Optional) install ingestion dependencies for live X/Reddit collection:

```bash
python -m pip install ".[ingestion]"
```

3) Configure credentials when using live ingestion:

- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USER_AGENT` (optional)

4) Run daily pipeline:

```bash
$env:PYTHONPATH="src"; python -m ai_equity_discovery --db data/discovery.sqlite --output reports/daily.md
```

The command writes:
- stage artifacts in SQLite
- source health per run
- markdown report output file

## Start API (v1.1)

```bash
$env:PYTHONPATH="src"; python -m uvicorn ai_equity_discovery.api.app:app --host 0.0.0.0 --port 8000
```

## Start Frontend (v1.1)

```bash
cd frontend
npm install
npm run dev
```

Environment variable for frontend:

- `NEXT_PUBLIC_API_BASE_URL` (default: `http://localhost:8000`)

## API Endpoints (v1.1)

- `POST /api/runs` - start run (single active-run policy)
- `GET /api/runs` - list recent runs
- `GET /api/runs/{run_id}` - run summary
- `GET /api/runs/{run_id}/stages` - stage status timeline
- `GET /api/runs/{run_id}/source-health` - per-source health
- `GET /api/runs/{run_id}/report` - markdown report
- `GET /api/config/sources` - read source config
- `PUT /api/config/sources` - update source config (applies to future runs)

## Project Structure

```text
src/ai_equity_discovery/
  core/            # config, models, serialization, sqlite storage
  ingestion/       # X/Reddit adapters + parallel discovery collection
  extraction/      # ticker/theme extraction
  resolution/      # exchange:ticker company resolution
  enrichment/      # facts providers, reliability policy, USD normalization
  ranking/         # deterministic scoring and ranking
  reporting/       # markdown report rendering
  pipeline/        # daily orchestration with stage instrumentation
  api/             # FastAPI routes, schemas, run launcher, config service
  cli.py           # pipeline entrypoint

frontend/
  app/page.tsx     # terminal-style monitor UI
  components/      # workflow/source health/markdown/config panels
  lib/api.ts       # backend client

docs/
  feature-map.md
  architecture/_index.md
  features/*
```

## LangChain Agents: What Are We Using?

Short answer: **no runtime LangChain agent graph is wired yet** in the current codebase.

Today, orchestration is deterministic Python stage services (pipeline-first). The LangChain/LangGraph direction is still architectural intent for deeper agent-style orchestration later.

Planned mapping when we introduce LangGraph:

- Discovery subagents: X and Reddit collectors
- Resolution/enrichment nodes: tool-driven factual verification
- Ranking/reporting nodes: deterministic scoring + digest synthesis

## Example Output

```text
AI EQUITY DISCOVERY - 2026-04-11

Top names:
1. NVIDIA Corporation (NVDA)
   - Designs GPUs and AI computing platforms.
   - Market cap: $2.1T
   - Revenue: $130.0B
```
