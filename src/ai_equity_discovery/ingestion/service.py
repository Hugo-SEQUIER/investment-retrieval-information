from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from time import perf_counter

from ai_equity_discovery.core.models import RawPost
from ai_equity_discovery.ingestion.base import SourceAdapter


@dataclass(slots=True)
class SourceHealth:
    source_name: str
    success: bool
    post_count: int
    elapsed_ms: int
    error: str | None = None


class IngestionService:
    def __init__(self, adapters: list[SourceAdapter]) -> None:
        self._adapters = adapters
        self.last_errors: list[str] = []
        self.last_health: list[SourceHealth] = []

    def _collect_from_adapter(
        self,
        adapter: SourceAdapter,
        since_utc: datetime | None,
    ) -> tuple[SourceHealth, list[RawPost]]:
        started = perf_counter()
        try:
            posts = adapter.fetch_posts(since_utc=since_utc)
            elapsed_ms = int((perf_counter() - started) * 1000)
            return (
                SourceHealth(
                    source_name=adapter.source_name,
                    success=True,
                    post_count=len(posts),
                    elapsed_ms=elapsed_ms,
                    error=None,
                ),
                posts,
            )
        except Exception as exc:
            elapsed_ms = int((perf_counter() - started) * 1000)
            return (
                SourceHealth(
                    source_name=adapter.source_name,
                    success=False,
                    post_count=0,
                    elapsed_ms=elapsed_ms,
                    error=str(exc),
                ),
                [],
            )

    def collect(self, since_utc: datetime | None = None) -> list[RawPost]:
        merged: dict[str, RawPost] = {}
        self.last_errors = []
        self.last_health = []

        if not self._adapters:
            return []

        max_workers = max(1, min(8, len(self._adapters)))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_adapter = {
                executor.submit(self._collect_from_adapter, adapter, since_utc): adapter
                for adapter in self._adapters
            }

            for future in as_completed(future_to_adapter):
                health, posts = future.result()
                self.last_health.append(health)
                if not health.success:
                    self.last_errors.append(f"{health.source_name}: {health.error}")
                    continue

                for post in posts:
                    merged[post.post_id] = post

        self.last_health.sort(key=lambda item: item.source_name)
        return sorted(
            merged.values(), key=lambda post: (post.published_at_utc, post.post_id)
        )
