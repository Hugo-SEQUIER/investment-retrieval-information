from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.core.loaders import (
    load_company_registry,
    load_enrichment_facts,
    load_source_config,
)


class LoadersTest(unittest.TestCase):
    def test_loaders_parse_json_configs(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)

            sources = base / "sources.json"
            sources.write_text(
                json.dumps(
                    {"x_accounts": ["jukan05"], "reddit_subreddits": ["stocks"]}
                ),
                encoding="utf-8",
            )

            companies = base / "companies.json"
            companies.write_text(
                json.dumps(
                    {
                        "companies": [
                            {
                                "company_name": "NVIDIA Corporation",
                                "ticker": "NVDA",
                                "exchange": "NASDAQ",
                                "country": "US",
                                "sector": "Technology",
                                "industry": "Semiconductors",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            facts = base / "facts.json"
            facts.write_text(
                json.dumps(
                    {
                        "facts": [
                            {
                                "canonical_id": "NASDAQ:NVDA",
                                "business_description": "GPU company",
                                "market_cap": 1,
                                "market_cap_currency": "USD",
                                "revenue": 1,
                                "revenue_currency": "USD",
                                "source_urls": ["https://example.com"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            source_cfg = load_source_config(sources)
            registry = load_company_registry(companies)
            enrichment = load_enrichment_facts(facts)

            self.assertEqual(source_cfg.x_accounts, ["jukan05"])
            self.assertEqual(source_cfg.reddit_subreddits, ["stocks"])
            self.assertIn("NVDA", registry)
            self.assertIn("NASDAQ:NVDA", enrichment)


if __name__ == "__main__":
    unittest.main()
