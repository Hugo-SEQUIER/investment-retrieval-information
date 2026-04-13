from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.analysis.service import AnalysisService
from ai_equity_discovery.core.config import AppConfig
from ai_equity_discovery.core.database import SQLiteStore
from ai_equity_discovery.core.models import RawPost, utc_now
from ai_equity_discovery.extraction.service import ExtractionService
from ai_equity_discovery.filtering.service import FilteringService
from ai_equity_discovery.ingestion.providers import InMemorySourceAdapter
from ai_equity_discovery.ingestion.service import IngestionService
from ai_equity_discovery.memory.obsidian import ObsidianMemoryConfig, ObsidianMemorySync
from ai_equity_discovery.pipeline.daily import DailyPipeline
from ai_equity_discovery.reporting.markdown import MarkdownReporter


class DailyPipelineTest(unittest.TestCase):
    def test_pipeline_uses_bootstrap_then_daily_lookback(self) -> None:
        with TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "discovery.sqlite"
            store = SQLiteStore(db_path)

            now = datetime.now(timezone.utc)
            old_post = RawPost(
                post_id="x-old",
                source="x:test",
                source_type="x",
                author="test",
                url="https://x.com/test/status/old",
                text="$NVDA old signal with AI demand commentary",
                published_at_utc=now - timedelta(days=6),
                ingested_at_utc=utc_now(),
                engagement={"likes": 1},
            )
            recent_post = RawPost(
                post_id="x-recent",
                source="x:test",
                source_type="x",
                author="test",
                url="https://x.com/test/status/recent",
                text="$NVDA recent signal with updated AI demand commentary",
                published_at_utc=now - timedelta(hours=12),
                ingested_at_utc=utc_now(),
                engagement={"likes": 2},
            )

            ingestion = IngestionService(
                adapters=[InMemorySourceAdapter("x", [old_post, recent_post])]
            )

            pipeline = DailyPipeline(
                config=AppConfig(
                    bootstrap_lookback_days=7,
                    daily_lookback_days=1,
                    memory=ObsidianMemoryConfig(enabled=False),
                ),
                store=store,
                ingestion=ingestion,
                filtering=FilteringService(),
                analysis=AnalysisService(extraction=ExtractionService()),
                reporter=MarkdownReporter(),
                memory=ObsidianMemorySync(ObsidianMemoryConfig(enabled=False)),
            )

            first = pipeline.run(report_date_utc=date.today())
            second = pipeline.run(report_date_utc=date.today())

            conn = sqlite3.connect(db_path)
            try:
                first_count = conn.execute(
                    "SELECT record_count FROM stage_status WHERE run_id = ? AND stage_name = 'fetch'",
                    (first.run_id,),
                ).fetchone()
                second_count = conn.execute(
                    "SELECT record_count FROM stage_status WHERE run_id = ? AND stage_name = 'fetch'",
                    (second.run_id,),
                ).fetchone()
            finally:
                conn.close()

            self.assertIsNotNone(first_count)
            self.assertIsNotNone(second_count)
            assert first_count is not None
            assert second_count is not None
            self.assertEqual(first_count[0], 2)
            self.assertEqual(second_count[0], 1)

    def test_pipeline_builds_markdown_report_and_writes_memory(self) -> None:
        with TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "discovery.sqlite"
            vault_path = Path(tmp) / "vault"
            vault_path.mkdir(parents=True, exist_ok=True)
            store = SQLiteStore(db_path)

            published = datetime(2026, 4, 11, 8, 0, 0, tzinfo=timezone.utc)

            x_posts = [
                RawPost(
                    post_id="x-1",
                    source="x:jukan05",
                    source_type="x",
                    author="jukan05",
                    url="https://x.com/jukan05/status/1",
                    text="$NVDA demand still strong, optical interconnect is critical for AI datacenter growth.",
                    published_at_utc=published,
                    ingested_at_utc=utc_now(),
                    engagement={"likes": 100},
                )
            ]

            reddit_posts = [
                RawPost(
                    post_id="r-1",
                    source="reddit:r/stocks",
                    source_type="reddit",
                    author="user123",
                    url="https://reddit.com/r/stocks/1",
                    text="ANET keeps coming up with hyperscaler capex and optical upgrades for AI clusters.",
                    published_at_utc=published,
                    ingested_at_utc=utc_now(),
                    engagement={"upvotes": 42},
                )
            ]

            ingestion = IngestionService(
                adapters=[
                    InMemorySourceAdapter("x", x_posts),
                    InMemorySourceAdapter("reddit", reddit_posts),
                ]
            )

            memory_config = ObsidianMemoryConfig(
                enabled=True,
                vault_path=str(vault_path),
                root_subdir="research",
            )

            pipeline = DailyPipeline(
                config=AppConfig(memory=memory_config),
                store=store,
                ingestion=ingestion,
                filtering=FilteringService(),
                analysis=AnalysisService(extraction=ExtractionService()),
                reporter=MarkdownReporter(),
                memory=ObsidianMemorySync(memory_config),
            )

            report = pipeline.run(report_date_utc=date(2026, 4, 11))

            self.assertEqual(report.report_date_utc.isoformat(), "2026-04-11")
            self.assertGreaterEqual(len(report.analysis_items), 2)
            self.assertIn("Signals to review:", report.markdown)
            self.assertIn("NVDA", report.markdown)
            self.assertIn("ANET", report.markdown)

            memory_log = vault_path / "research" / "Daily Logs" / "2026-04-11.md"
            self.assertTrue(memory_log.exists())

            conn = sqlite3.connect(db_path)
            try:
                rows = conn.execute(
                    "SELECT source_name, success, post_count FROM source_health WHERE run_id = ? ORDER BY source_name",
                    (report.run_id,),
                ).fetchall()

                run_row = conn.execute(
                    "SELECT status FROM runs WHERE run_id = ?",
                    (report.run_id,),
                ).fetchone()

                stage_rows = conn.execute(
                    "SELECT stage_name, status FROM stage_status WHERE run_id = ?",
                    (report.run_id,),
                ).fetchall()
            finally:
                conn.close()

            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0][0], "reddit")
            self.assertEqual(rows[1][0], "x")
            self.assertEqual(rows[0][1], 1)
            self.assertEqual(rows[1][1], 1)

            self.assertIsNotNone(run_row)
            assert run_row is not None
            self.assertEqual(run_row[0], "success")

            self.assertEqual(len(stage_rows), 5)
            self.assertTrue(all(row[1] == "success" for row in stage_rows))


if __name__ == "__main__":
    unittest.main()
