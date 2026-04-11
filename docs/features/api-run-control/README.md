# API Run Control - Overview

## Quick Reference
- **Key files**: `src/ai_equity_discovery/api/app.py`, `src/ai_equity_discovery/api/routes/runs.py`, `src/ai_equity_discovery/api/routes/config.py`, `src/ai_equity_discovery/api/runner.py`
- **Dependencies**: `fastapi`, `uvicorn`
- **Patterns**: subprocess run launch, single active-run policy, polling-first monitor endpoints

## Purpose
Expose run-control and observability APIs for the v1.1 frontend terminal monitor.

## Boundaries
- API can start runs and read run metadata.
- API does not execute trades or portfolio actions.
- Source config changes apply to future runs only.

## Endpoints
- `POST /api/runs`
- `GET /api/runs`
- `GET /api/runs/{run_id}`
- `GET /api/runs/{run_id}/stages`
- `GET /api/runs/{run_id}/source-health`
- `GET /api/runs/{run_id}/report`
- `GET /api/config/sources`
- `PUT /api/config/sources`

## TODOs / Tech Debt
- [ ] Add authentication and authorization.
- [ ] Add rate limiting for run-trigger endpoint.
- [ ] Add SSE endpoint for live stage updates.

---
*Last update: 2026-04-12 - Initial API run-control feature doc.*
