from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from ai_equity_discovery.api.schemas import SourcesConfigPayload


def sources_config_path() -> Path:
    configured = os.getenv("AI_EQUITY_SOURCES_CONFIG", "config/sources.example.json")
    return Path(configured)


def read_sources_config() -> SourcesConfigPayload:
    path = sources_config_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return SourcesConfigPayload(
        x_accounts=list(payload.get("x_accounts", [])),
        reddit_subreddits=list(payload.get("reddit_subreddits", [])),
    )


def write_sources_config(data: SourcesConfigPayload) -> None:
    path = sources_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp = tempfile.mkstemp(prefix="sources-", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "x_accounts": data.x_accounts,
                    "reddit_subreddits": data.reddit_subreddits,
                },
                handle,
                indent=2,
            )
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)
