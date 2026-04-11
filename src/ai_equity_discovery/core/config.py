from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class AppConfig:
    x_accounts: list[str] = field(default_factory=list)
    reddit_subreddits: list[str] = field(default_factory=list)
    top_n: int = 10
    base_currency: str = "USD"
