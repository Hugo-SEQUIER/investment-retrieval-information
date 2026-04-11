from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from ai_equity_discovery.core.models import EnrichedCompany, ResolvedCompany


@dataclass(slots=True)
class EnrichmentFacts:
    business_description: str | None
    market_cap: float | None
    market_cap_currency: str | None
    revenue: float | None
    revenue_currency: str | None
    source_urls: list[str]


class EnrichmentProvider(Protocol):
    def get_facts(self, canonical_id: str) -> EnrichmentFacts | None: ...


class InMemoryEnrichmentProvider:
    def __init__(self, facts_by_id: dict[str, EnrichmentFacts]) -> None:
        self._facts_by_id = facts_by_id

    def get_facts(self, canonical_id: str) -> EnrichmentFacts | None:
        return self._facts_by_id.get(canonical_id)


class LayeredEnrichmentProvider:
    def __init__(
        self, primary: EnrichmentProvider, fallback: EnrichmentProvider
    ) -> None:
        self._primary = primary
        self._fallback = fallback

    def get_facts(self, canonical_id: str) -> EnrichmentFacts | None:
        primary = self._primary.get_facts(canonical_id)
        if primary is not None:
            return primary
        return self._fallback.get_facts(canonical_id)


class CurrencyNormalizer:
    def __init__(self, fx_rates_to_usd: dict[str, float], fx_date: date) -> None:
        self._fx = {
            currency.upper(): rate for currency, rate in fx_rates_to_usd.items()
        }
        self._fx.setdefault("USD", 1.0)
        self.fx_date = fx_date

    def to_usd(
        self, value: float | None, currency: str | None
    ) -> tuple[float | None, float | None, str | None]:
        if value is None:
            return None, None, "MISSING_VALUE"
        if not currency:
            return None, None, "MISSING_CURRENCY"
        rate = self._fx.get(currency.upper())
        if rate is None:
            return None, None, f"UNKNOWN_CURRENCY:{currency.upper()}"
        return value * rate, rate, None


class EnrichmentService:
    def __init__(
        self, provider: EnrichmentProvider, normalizer: CurrencyNormalizer
    ) -> None:
        self._provider = provider
        self._normalizer = normalizer

    def enrich(self, resolved: list[ResolvedCompany]) -> list[EnrichedCompany]:
        enriched: list[EnrichedCompany] = []
        for item in resolved:
            if item.unresolved:
                continue

            facts = self._provider.get_facts(item.canonical_id)
            caveats: list[str] = []
            source_urls: list[str] = []
            business_description: str | None = None
            market_cap_usd: float | None = None
            revenue_usd: float | None = None
            fx_rate: float | None = None

            if facts is None:
                caveats.append("NO_ENRICHMENT_FACTS")
            else:
                business_description = facts.business_description
                source_urls = facts.source_urls

                market_cap_usd, fx_rate_market_cap, market_cap_issue = (
                    self._normalizer.to_usd(
                        facts.market_cap,
                        facts.market_cap_currency,
                    )
                )
                if market_cap_issue:
                    caveats.append(f"MARKET_CAP_{market_cap_issue}")

                revenue_usd, fx_rate_revenue, revenue_issue = self._normalizer.to_usd(
                    facts.revenue,
                    facts.revenue_currency,
                )
                if revenue_issue:
                    caveats.append(f"REVENUE_{revenue_issue}")

                fx_rate = fx_rate_market_cap or fx_rate_revenue

            enriched.append(
                EnrichedCompany(
                    enrichment_id=f"{item.resolution_id}:ENRICHED",
                    resolution_id=item.resolution_id,
                    canonical_id=item.canonical_id,
                    company_name=item.company_name,
                    ticker=item.ticker,
                    exchange=item.exchange,
                    country=item.country,
                    sector=item.sector,
                    industry=item.industry,
                    business_description=business_description,
                    market_cap_usd=market_cap_usd,
                    revenue_usd=revenue_usd,
                    source_urls=source_urls,
                    fx_rate=fx_rate,
                    fx_date=self._normalizer.fx_date,
                    caveats=caveats,
                )
            )

        return enriched
