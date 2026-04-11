from __future__ import annotations

import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.enrichment.service import (
    EnrichmentFacts,
    LayeredEnrichmentProvider,
)


class StaticProvider:
    def __init__(self, payload: dict[str, EnrichmentFacts]) -> None:
        self._payload = payload

    def get_facts(self, canonical_id: str) -> EnrichmentFacts | None:
        return self._payload.get(canonical_id)


class EnrichmentLayeredTest(unittest.TestCase):
    def test_layered_provider_uses_fallback_when_primary_missing(self) -> None:
        primary = StaticProvider(payload={})
        fallback = StaticProvider(
            payload={
                "NASDAQ:NVDA": EnrichmentFacts(
                    business_description="Designs GPUs",
                    market_cap=None,
                    market_cap_currency=None,
                    revenue=None,
                    revenue_currency=None,
                    source_urls=["https://investor.nvidia.com"],
                )
            }
        )

        layered = LayeredEnrichmentProvider(primary=primary, fallback=fallback)
        facts = layered.get_facts("NASDAQ:NVDA")

        self.assertIsNotNone(facts)
        assert facts is not None
        self.assertEqual(facts.business_description, "Designs GPUs")


if __name__ == "__main__":
    unittest.main()
