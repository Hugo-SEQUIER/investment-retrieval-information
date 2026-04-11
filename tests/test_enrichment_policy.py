from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.enrichment.policy import sort_urls_by_reliability, source_tier


class EnrichmentPolicyTest(unittest.TestCase):
    def test_source_tier_prefers_official_domains(self) -> None:
        self.assertEqual(source_tier("https://investor.nvidia.com"), 1)
        self.assertEqual(
            source_tier("https://nasdaq.com/market-activity/stocks/nvda"), 2
        )

    def test_sort_urls_orders_by_tier(self) -> None:
        urls = [
            "https://reuters.com/article/test",
            "https://investor.nvidia.com",
            "https://nasdaq.com/market-activity/stocks/nvda",
        ]
        sorted_urls = sort_urls_by_reliability(urls)
        self.assertEqual(sorted_urls[0], "https://investor.nvidia.com")


if __name__ == "__main__":
    unittest.main()
