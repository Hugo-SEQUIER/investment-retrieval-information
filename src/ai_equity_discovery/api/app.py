from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ai_equity_discovery.api.routes.config import router as config_router
from ai_equity_discovery.api.routes.runs import router as runs_router
from ai_equity_discovery.core.database import SQLiteStore


def database_path() -> Path:
    return Path(os.getenv("AI_EQUITY_DB_PATH", "data/discovery.sqlite"))


def create_app() -> FastAPI:
    app = FastAPI(title="AI Equity Discovery API", version="0.1.0")
    app.state.store = SQLiteStore(database_path())

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(runs_router)
    app.include_router(config_router)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()


def main() -> None:
    import uvicorn

    uvicorn.run(
        "ai_equity_discovery.api.app:app", host="0.0.0.0", port=8000, reload=False
    )
