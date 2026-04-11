from __future__ import annotations

from pydantic import BaseModel, Field


class SourcesConfigPayload(BaseModel):
    x_accounts: list[str] = Field(default_factory=list)
    reddit_subreddits: list[str] = Field(default_factory=list)


class RunCreateResponse(BaseModel):
    run_id: str
    status: str


class RunSummary(BaseModel):
    run_id: str
    created_at_utc: str
    status: str
    started_at_utc: str | None = None
    finished_at_utc: str | None = None
    error: str | None = None


class StageStatus(BaseModel):
    run_id: str
    stage_name: str
    status: str
    started_at_utc: str | None = None
    finished_at_utc: str | None = None
    error: str | None = None
    record_count: int


class SourceHealthItem(BaseModel):
    source_name: str
    success: int
    post_count: int
    elapsed_ms: int
    error: str | None = None
    created_at_utc: str


class ReportPayload(BaseModel):
    run_id: str
    report_date_utc: str
    markdown: str
