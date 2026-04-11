from __future__ import annotations

from dataclasses import dataclass

from ai_equity_discovery.enrichment.parsing import (
    extract_market_cap,
    extract_revenue,
    summarize_business_description,
)
from ai_equity_discovery.enrichment.policy import sort_urls_by_reliability
from ai_equity_discovery.enrichment.service import EnrichmentFacts, EnrichmentProvider


@dataclass(slots=True)
class WebProviderConfig:
    timeout_seconds: float = 8.0
    max_description_chars: int = 260


class WebResearchEnrichmentProvider(EnrichmentProvider):
    def __init__(
        self,
        source_urls_by_id: dict[str, list[str]],
        config: WebProviderConfig | None = None,
    ) -> None:
        self._source_urls_by_id = source_urls_by_id
        self._config = config or WebProviderConfig()

    def get_facts(self, canonical_id: str) -> EnrichmentFacts | None:
        urls = self._source_urls_by_id.get(canonical_id, [])
        if not urls:
            return None

        sorted_urls = sort_urls_by_reliability(urls)
        description: str | None = None
        market_cap: float | None = None
        market_cap_currency: str | None = None
        revenue: float | None = None
        revenue_currency: str | None = None
        used_urls: list[str] = []

        for url in sorted_urls:
            text = self._extract_page_text(url)
            if not text:
                continue

            used_urls.append(url)
            if description is None:
                description = summarize_business_description(
                    text, self._config.max_description_chars
                )

            if market_cap is None:
                market_cap, market_cap_currency = extract_market_cap(text)

            if revenue is None:
                revenue, revenue_currency = extract_revenue(text)

        if description is None and market_cap is None and revenue is None:
            return None

        return EnrichmentFacts(
            business_description=description,
            market_cap=market_cap,
            market_cap_currency=market_cap_currency,
            revenue=revenue,
            revenue_currency=revenue_currency,
            source_urls=used_urls,
        )

    def _extract_page_text(self, url: str) -> str | None:
        try:
            import httpx
        except ImportError as exc:
            raise RuntimeError("httpx is not installed") from exc

        try:
            response = httpx.get(
                url, timeout=self._config.timeout_seconds, follow_redirects=True
            )
            response.raise_for_status()
            html = response.text
        except Exception:
            return None

        try:
            import trafilatura

            extracted = trafilatura.extract(html)
            if extracted:
                return extracted
        except Exception:
            pass

        try:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator=" ")
            return text
        except Exception:
            return None
