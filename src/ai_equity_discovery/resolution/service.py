from __future__ import annotations

from ai_equity_discovery.core.models import MentionCandidate, ResolvedCompany
from ai_equity_discovery.resolution.registry import CompanyRegistry


class ResolutionService:
    def __init__(self, registry: CompanyRegistry) -> None:
        self._registry = registry

    def resolve(self, candidates: list[MentionCandidate]) -> list[ResolvedCompany]:
        results: list[ResolvedCompany] = []
        for candidate in candidates:
            if not candidate.tickers:
                results.append(
                    ResolvedCompany(
                        resolution_id=f"{candidate.candidate_id}:UNRESOLVED",
                        candidate_id=candidate.candidate_id,
                        canonical_id="UNRESOLVED",
                        company_name=None,
                        ticker=None,
                        exchange=None,
                        country=None,
                        sector=None,
                        industry=None,
                        confidence=0.0,
                        unresolved=True,
                        reason_code="NO_TICKER",
                    )
                )
                continue

            for ticker in candidate.tickers:
                entry = self._registry.resolve_ticker(ticker)
                if entry is None:
                    results.append(
                        ResolvedCompany(
                            resolution_id=f"{candidate.candidate_id}:{ticker}",
                            candidate_id=candidate.candidate_id,
                            canonical_id="UNRESOLVED",
                            company_name=None,
                            ticker=ticker,
                            exchange=None,
                            country=None,
                            sector=None,
                            industry=None,
                            confidence=0.2,
                            unresolved=True,
                            reason_code="TICKER_NOT_IN_REGISTRY",
                        )
                    )
                    continue

                results.append(
                    ResolvedCompany(
                        resolution_id=f"{candidate.candidate_id}:{entry.canonical_id}",
                        candidate_id=candidate.candidate_id,
                        canonical_id=entry.canonical_id,
                        company_name=entry.company_name,
                        ticker=entry.ticker,
                        exchange=entry.exchange,
                        country=entry.country,
                        sector=entry.sector,
                        industry=entry.industry,
                        confidence=0.9,
                        unresolved=False,
                        reason_code="EXACT_TICKER_MATCH",
                    )
                )
        return results
