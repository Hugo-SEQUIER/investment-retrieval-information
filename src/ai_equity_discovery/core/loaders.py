from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SourceConfig:
    x_accounts: list[str]
    reddit_subreddits: list[str]


def _read_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_source_config(path: str | Path) -> SourceConfig:
    payload = _read_json(path)
    return SourceConfig(
        x_accounts=list(payload.get("x_accounts", [])),
        reddit_subreddits=list(payload.get("reddit_subreddits", [])),
    )
