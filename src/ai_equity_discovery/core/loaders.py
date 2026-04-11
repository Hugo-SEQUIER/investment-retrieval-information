from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from ai_equity_discovery.enrichment.service import EnrichmentFacts
from ai_equity_discovery.resolution.registry import RegistryEntry


@dataclass(slots=True)
class SourceConfig:
    x_accounts: list[str]
    reddit_subreddits: list[str]


def _read_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_source_config(path: str | Path) -> SourceConfig:
    payload = _read_json(path)
    return SourceConfig(
        x_accounts=list(payload.get("x_accounts", [])),
        reddit_subreddits=list(payload.get("reddit_subreddits", [])),
    )


def load_company_registry(path: str | Path) -> dict[str, RegistryEntry]:
    payload = _read_json(path)
    entries: dict[str, RegistryEntry] = {}
    for item in payload.get("companies", []):
        ticker = str(item["ticker"]).upper()
        entries[ticker] = RegistryEntry(
            company_name=str(item["company_name"]),
            ticker=ticker,
            exchange=str(item["exchange"]).upper(),
            country=str(item.get("country", "US")),
            sector=str(item.get("sector", "Unknown")),
            industry=str(item.get("industry", "Unknown")),
        )
    return entries


def load_enrichment_facts(path: str | Path) -> dict[str, EnrichmentFacts]:
    payload = _read_json(path)
    entries: dict[str, EnrichmentFacts] = {}
    for item in payload.get("facts", []):
        canonical_id = str(item["canonical_id"])
        entries[canonical_id] = EnrichmentFacts(
            business_description=item.get("business_description"),
            market_cap=item.get("market_cap"),
            market_cap_currency=item.get("market_cap_currency"),
            revenue=item.get("revenue"),
            revenue_currency=item.get("revenue_currency"),
            source_urls=list(item.get("source_urls", [])),
        )
    return entries


def load_enrichment_source_urls(path: str | Path) -> dict[str, list[str]]:
    payload = _read_json(path)
    result: dict[str, list[str]] = {}
    for item in payload.get("facts", []):
        canonical_id = str(item["canonical_id"])
        result[canonical_id] = list(item.get("source_urls", []))
    return result


def load_fx_rates(path: str | Path) -> dict[str, float]:
    payload = _read_json(path)
    fx_to_usd = payload.get("fx_to_usd", {})
    result: dict[str, float] = {"USD": 1.0}
    for currency, rate in fx_to_usd.items():
        result[str(currency).upper()] = float(rate)
    return result
