from __future__ import annotations

from datetime import date, datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import sys
import sqlite3

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.core.config import AppConfig
from ai_equity_discovery.core.database import SQLiteStore
from ai_equity_discovery.core.models import RawPost, utc_now
from ai_equity_discovery.enrichment.service import (
    CurrencyNormalizer,
    EnrichmentFacts,
    EnrichmentService,
    InMemoryEnrichmentProvider,
)
from ai_equity_discovery.extraction.service import ExtractionService
from ai_equity_discovery.ingestion.providers import InMemorySourceAdapter
from ai_equity_discovery.ingestion.service import IngestionService
from ai_equity_discovery.pipeline.daily import DailyPipeline
from ai_equity_discovery.ranking.service import RankingService
from ai_equity_discovery.reporting.markdown import MarkdownReporter
from ai_equity_discovery.resolution.registry import CompanyRegistry, RegistryEntry
from ai_equity_discovery.resolution.service import ResolutionService


class DailyPipelineTest(unittest.TestCase):
    def test_pipeline_builds_markdown_report_with_usd_values(self) -> None:
        with TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "discovery.sqlite"
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

            registry = CompanyRegistry(
                {
                    "NVDA": RegistryEntry(
                        company_name="NVIDIA Corporation",
                        ticker="NVDA",
                        exchange="NASDAQ",
                        country="US",
                        sector="Technology",
                        industry="Semiconductors",
                    ),
                    "ANET": RegistryEntry(
                        company_name="Arista Networks, Inc.",
                        ticker="ANET",
                        exchange="NYSE",
                        country="US",
                        sector="Technology",
                        industry="Networking",
                    ),
                }
            )

            enrichment_provider = InMemoryEnrichmentProvider(
                {
                    "NASDAQ:NVDA": EnrichmentFacts(
                        business_description="Designs GPUs and AI computing platforms.",
                        market_cap=2_100_000_000_000,
                        market_cap_currency="USD",
                        revenue=130_000_000_000,
                        revenue_currency="USD",
                        source_urls=["https://investor.nvidia.com"],
                    ),
                    "NYSE:ANET": EnrichmentFacts(
                        business_description="Provides high-performance networking for data centers.",
                        market_cap=95_000_000_000,
                        market_cap_currency="USD",
                        revenue=6_000_000_000,
                        revenue_currency="USD",
                        source_urls=["https://investors.arista.com"],
                    ),
                }
            )

            pipeline = DailyPipeline(
                config=AppConfig(top_n=5),
                store=store,
                ingestion=ingestion,
                extraction=ExtractionService(),
                resolution=ResolutionService(registry),
                enrichment=EnrichmentService(
                    provider=enrichment_provider,
                    normalizer=CurrencyNormalizer(
                        fx_rates_to_usd={"USD": 1.0}, fx_date=date(2026, 4, 11)
                    ),
                ),
                ranking=RankingService(),
                reporter=MarkdownReporter(),
            )

            report = pipeline.run(report_date_utc=date(2026, 4, 11))

            self.assertEqual(report.report_date_utc.isoformat(), "2026-04-11")
            self.assertGreaterEqual(len(report.top_ideas), 2)
            self.assertIn("NVIDIA Corporation (NVDA)", report.markdown)
            self.assertIn("Arista Networks, Inc. (ANET)", report.markdown)
            self.assertIn("Market cap: $2.1T", report.markdown)
            self.assertIn("Revenue: $130.0B", report.markdown)

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

            self.assertEqual(len(stage_rows), 6)
            self.assertTrue(all(row[1] == "success" for row in stage_rows))


if __name__ == "__main__":
    unittest.main()
