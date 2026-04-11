from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Literal


SourceType = Literal["x", "reddit"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class RawPost:
    post_id: str
    source: str
    source_type: SourceType
    author: str
    url: str
    text: str
    published_at_utc: datetime
    ingested_at_utc: datetime
    engagement: dict[str, int] = field(default_factory=dict)


@dataclass(slots=True)
class MentionCandidate:
    candidate_id: str
    raw_post_id: str
    tickers: list[str]
    company_hints: list[str]
    themes: list[str]
    confidence: float


@dataclass(slots=True)
class ResolvedCompany:
    resolution_id: str
    candidate_id: str
    canonical_id: str
    company_name: str | None
    ticker: str | None
    exchange: str | None
    country: str | None
    sector: str | None
    industry: str | None
    confidence: float
    unresolved: bool
    reason_code: str


@dataclass(slots=True)
class EnrichedCompany:
    enrichment_id: str
    resolution_id: str
    canonical_id: str
    company_name: str | None
    ticker: str | None
    exchange: str | None
    country: str | None
    sector: str | None
    industry: str | None
    business_description: str | None
    market_cap_usd: float | None
    revenue_usd: float | None
    source_urls: list[str]
    fx_rate: float | None
    fx_date: date | None
    caveats: list[str] = field(default_factory=list)


@dataclass(slots=True)
class RankedIdea:
    canonical_id: str
    company_name: str
    ticker: str
    exchange: str
    country: str
    sector: str | None
    industry: str | None
    business_description: str | None
    market_cap_usd: float | None
    revenue_usd: float | None
    score: float
    mention_count: int
    cross_source_count: int
    ai_relevance_score: float
    resolution_confidence: float
    trend_reason: str
    caveats: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DailyReport:
    run_id: str
    report_date_utc: date
    top_ideas: list[RankedIdea]
    themes: list[str]
    markdown: str
