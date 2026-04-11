from __future__ import annotations

from datetime import datetime
from typing import Protocol

from ai_equity_discovery.core.models import RawPost


class SourceAdapter(Protocol):
    source_name: str

    def fetch_posts(self, since_utc: datetime | None = None) -> list[RawPost]: ...
