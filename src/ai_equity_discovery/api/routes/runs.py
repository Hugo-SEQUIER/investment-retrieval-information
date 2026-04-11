from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException, Request

from ai_equity_discovery.api.runner import launch_pipeline_subprocess, new_run_id
from ai_equity_discovery.api.schemas import (
    ReportPayload,
    RunCreateResponse,
    RunSummary,
    SourceHealthItem,
    StageStatus,
)


router = APIRouter(prefix="/api", tags=["runs"])


def _db_path() -> Path:
    return Path(os.getenv("AI_EQUITY_DB_PATH", "data/discovery.sqlite"))


@router.post("/runs", response_model=RunCreateResponse)
def start_run(request: Request) -> RunCreateResponse:
    store = request.app.state.store
    if store.has_active_run():
        raise HTTPException(status_code=409, detail="A run is already active")

    run_id = new_run_id()
    store.create_run(run_id, status="queued")
    launch_pipeline_subprocess(run_id=run_id, db_path=_db_path())
    return RunCreateResponse(run_id=run_id, status="queued")


@router.get("/runs", response_model=list[RunSummary])
def list_runs(request: Request) -> list[RunSummary]:
    store = request.app.state.store
    return [RunSummary(**item) for item in store.list_runs(limit=50)]


@router.get("/runs/{run_id}", response_model=RunSummary)
def get_run(run_id: str, request: Request) -> RunSummary:
    store = request.app.state.store
    row = store.get_run(run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return RunSummary(**row)


@router.get("/runs/{run_id}/stages", response_model=list[StageStatus])
def get_stages(run_id: str, request: Request) -> list[StageStatus]:
    store = request.app.state.store
    return [StageStatus(**item) for item in store.get_stage_status(run_id)]


@router.get("/runs/{run_id}/source-health", response_model=list[SourceHealthItem])
def get_source_health(run_id: str, request: Request) -> list[SourceHealthItem]:
    store = request.app.state.store
    return [SourceHealthItem(**item) for item in store.get_source_health(run_id)]


@router.get("/runs/{run_id}/report", response_model=ReportPayload)
def get_report(run_id: str, request: Request) -> ReportPayload:
    store = request.app.state.store
    row = store.get_report(run_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportPayload(**row)
