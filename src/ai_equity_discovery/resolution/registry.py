from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RegistryEntry:
    company_name: str
    ticker: str
    exchange: str
    country: str
    sector: str
    industry: str

    @property
    def canonical_id(self) -> str:
        return f"{self.exchange}:{self.ticker}"


class CompanyRegistry:
    def __init__(self, by_ticker: dict[str, RegistryEntry]) -> None:
        self._by_ticker = {ticker.upper(): entry for ticker, entry in by_ticker.items()}

    def resolve_ticker(self, ticker: str) -> RegistryEntry | None:
        return self._by_ticker.get(ticker.upper())
