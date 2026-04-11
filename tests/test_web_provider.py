from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.enrichment.web_provider import WebResearchEnrichmentProvider


class DummyWebProvider(WebResearchEnrichmentProvider):
    def __init__(
        self, source_urls_by_id: dict[str, list[str]], pages: dict[str, str]
    ) -> None:
        super().__init__(source_urls_by_id=source_urls_by_id)
        self._pages = pages

    def _extract_page_text(self, url: str) -> str | None:
        return self._pages.get(url)


class WebProviderTest(unittest.TestCase):
    def test_web_provider_extracts_labeled_financials(self) -> None:
        urls = {
            "NASDAQ:NVDA": [
                "https://reuters.com/article/nvda",
                "https://investor.nvidia.com",
            ]
        }
        pages = {
            "https://investor.nvidia.com": "NVIDIA designs GPUs. Market cap $2.1T. Annual revenue USD 130.0B.",
            "https://reuters.com/article/nvda": "News coverage.",
        }

        provider = DummyWebProvider(source_urls_by_id=urls, pages=pages)
        facts = provider.get_facts("NASDAQ:NVDA")

        self.assertIsNotNone(facts)
        assert facts is not None
        self.assertEqual(round(facts.market_cap or 0), 2_100_000_000_000)
        self.assertEqual(round(facts.revenue or 0), 130_000_000_000)
        self.assertEqual(facts.market_cap_currency, "USD")
        self.assertEqual(facts.revenue_currency, "USD")
        self.assertTrue(facts.source_urls)


if __name__ == "__main__":
    unittest.main()
