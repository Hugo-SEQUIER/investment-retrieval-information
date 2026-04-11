from __future__ import annotations

from fastapi import APIRouter

from ai_equity_discovery.api.config_service import (
    read_sources_config,
    write_sources_config,
)
from ai_equity_discovery.api.schemas import SourcesConfigPayload


router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/sources", response_model=SourcesConfigPayload)
def get_sources() -> SourcesConfigPayload:
    return read_sources_config()


@router.put("/sources", response_model=SourcesConfigPayload)
def put_sources(payload: SourcesConfigPayload) -> SourcesConfigPayload:
    write_sources_config(payload)
    return read_sources_config()
