from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.core.models import RawPost, utc_now
from ai_equity_discovery.extraction.service import ExtractionService


class ExtractionServiceTest(unittest.TestCase):
    def test_extract_tickers_does_not_promote_normal_words(self) -> None:
        service = ExtractionService()
        post = RawPost(
            post_id="p1",
            source="x:test",
            source_type="x",
            author="test",
            url="https://x.com/test/status/1",
            text="Bank of Korea today discussed inflation and growth outlook.",
            published_at_utc=datetime(2026, 4, 13, 0, 0, 0, tzinfo=timezone.utc),
            ingested_at_utc=utc_now(),
            engagement={},
        )

        candidates = service.extract([post])
        self.assertEqual(candidates, [])

    def test_extract_tickers_keeps_cashtags_and_uppercase_symbols(self) -> None:
        service = ExtractionService()
        post = RawPost(
            post_id="p2",
            source="x:test",
            source_type="x",
            author="test",
            url="https://x.com/test/status/2",
            text="$nvda and ANET remain strong in AI infra",
            published_at_utc=datetime(2026, 4, 13, 0, 0, 0, tzinfo=timezone.utc),
            ingested_at_utc=utc_now(),
            engagement={},
        )

        candidates = service.extract([post])
        self.assertEqual(len(candidates), 1)
        self.assertIn("NVDA", candidates[0].tickers)
        self.assertIn("ANET", candidates[0].tickers)


if __name__ == "__main__":
    unittest.main()
