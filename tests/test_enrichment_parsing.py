from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.enrichment.parsing import (
    extract_market_cap,
    extract_revenue,
    parse_money_token,
)


class EnrichmentParsingTest(unittest.TestCase):
    def test_parse_money_token_with_suffix(self) -> None:
        value = parse_money_token("$2.1T")
        self.assertIsNotNone(value)
        assert value is not None
        self.assertEqual(round(value[0]), 2_100_000_000_000)
        self.assertEqual(value[1], "USD")

    def test_extract_market_cap_and_revenue(self) -> None:
        text = "Company profile. Market cap $95.0B. Annual revenue USD 6.0B."
        market_cap, market_ccy = extract_market_cap(text)
        revenue, revenue_ccy = extract_revenue(text)

        self.assertEqual(market_ccy, "USD")
        self.assertEqual(revenue_ccy, "USD")
        self.assertEqual(round(market_cap or 0), 95_000_000_000)
        self.assertEqual(round(revenue or 0), 6_000_000_000)


if __name__ == "__main__":
    unittest.main()
