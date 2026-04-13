from __future__ import annotations

from datetime import datetime, timezone
import sys
from pathlib import Path
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.core.models import DiscoveryAnnotation, RawPost, utc_now
from ai_equity_discovery.ingestion.base import SourceAdapter
from ai_equity_discovery.ingestion.providers import InMemorySourceAdapter
from ai_equity_discovery.ingestion.service import IngestionService


class FailingAdapter(SourceAdapter):
    source_name = "failing"

    def fetch_posts(self, since_utc: datetime | None = None) -> list[RawPost]:
        raise RuntimeError("boom")


class SlowAdapter(SourceAdapter):
    def __init__(self, source_name: str, post: RawPost, delay_seconds: float) -> None:
        self.source_name = source_name
        self._post = post
        self._delay_seconds = delay_seconds

    def fetch_posts(self, since_utc: datetime | None = None) -> list[RawPost]:
        time.sleep(self._delay_seconds)
        return [self._post]


class IngestionServiceTest(unittest.TestCase):
    def test_collect_applies_discovery_annotations_in_shadow_mode(self) -> None:
        post = RawPost(
            post_id="x:42",
            source="x:test",
            source_type="x",
            author="test",
            url="https://x.com/test/status/42",
            text="Nuevo contrato de IA para $NVDA",
            published_at_utc=datetime(2026, 4, 12, 0, 0, 0, tzinfo=timezone.utc),
            ingested_at_utc=utc_now(),
            engagement={"likes": 10},
        )

        class StubAnnotator:
            def annotate(self, posts: list[RawPost]) -> dict[str, DiscoveryAnnotation]:
                return {
                    posts[0].post_id: DiscoveryAnnotation(
                        post_id=posts[0].post_id,
                        actionable=True,
                        ai_relevance=0.92,
                        spam_likelihood=0.03,
                        entity_hints=["NVDA", "NVIDIA"],
                        reason="AI contract mention and ticker signal.",
                        english_summary="The post highlights an AI-related NVIDIA contract.",
                        provider="openrouter",
                        model="qwen/qwen3.6-plus",
                    )
                }

        service = IngestionService(
            adapters=[InMemorySourceAdapter("x", [post])],
            annotator=StubAnnotator(),
        )

        posts = service.collect()
        self.assertEqual(len(posts), 1)
        self.assertIsNotNone(posts[0].annotation)
        assert posts[0].annotation is not None
        self.assertEqual(posts[0].annotation.english_summary.split()[0], "The")

    def test_collect_keeps_working_if_one_adapter_fails(self) -> None:
        post = RawPost(
            post_id="x:1",
            source="x:test",
            source_type="x",
            author="test",
            url="https://x.com/test/status/1",
            text="$NVDA",
            published_at_utc=datetime(2026, 4, 12, 0, 0, 0, tzinfo=timezone.utc),
            ingested_at_utc=utc_now(),
            engagement={"likes": 1},
        )

        service = IngestionService(
            adapters=[
                FailingAdapter(),
                InMemorySourceAdapter("x", [post]),
            ]
        )

        posts = service.collect()
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0].post_id, "x:1")
        self.assertEqual(len(service.last_errors), 1)
        self.assertIn("failing", service.last_errors[0])
        self.assertEqual(len(service.last_health), 2)
        failing = [
            item for item in service.last_health if item.source_name == "failing"
        ][0]
        self.assertFalse(failing.success)

    def test_collect_runs_sources_in_parallel(self) -> None:
        post_a = RawPost(
            post_id="x:2",
            source="x:a",
            source_type="x",
            author="a",
            url="https://x.com/a/status/2",
            text="$NVDA",
            published_at_utc=datetime(2026, 4, 12, 0, 0, 0, tzinfo=timezone.utc),
            ingested_at_utc=utc_now(),
            engagement={"likes": 1},
        )
        post_b = RawPost(
            post_id="reddit:3",
            source="reddit:r/stocks",
            source_type="reddit",
            author="b",
            url="https://reddit.com/r/stocks/3",
            text="ANET",
            published_at_utc=datetime(2026, 4, 12, 0, 1, 0, tzinfo=timezone.utc),
            ingested_at_utc=utc_now(),
            engagement={"upvotes": 1},
        )

        service = IngestionService(
            adapters=[
                SlowAdapter("x", post_a, 0.2),
                SlowAdapter("reddit", post_b, 0.2),
            ]
        )

        started = time.perf_counter()
        posts = service.collect()
        elapsed = time.perf_counter() - started

        self.assertEqual(len(posts), 2)
        self.assertLess(elapsed, 0.35)
        self.assertTrue(all(item.success for item in service.last_health))


if __name__ == "__main__":
    unittest.main()
