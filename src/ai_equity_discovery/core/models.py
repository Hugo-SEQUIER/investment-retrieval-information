from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Literal


SourceType = Literal["x", "reddit"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class DiscoveryAnnotation:
    post_id: str
    actionable: bool
    ai_relevance: float
    spam_likelihood: float
    entity_hints: list[str]
    reason: str
    english_summary: str
    provider: str
    model: str


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
    annotation: DiscoveryAnnotation | None = None


@dataclass(slots=True)
class MentionCandidate:
    candidate_id: str
    raw_post_id: str
    tickers: list[str]
    company_hints: list[str]
    themes: list[str]
    confidence: float


@dataclass(slots=True)
class FilteredPost:
    post_id: str
    keep: bool
    reason_code: str
    confidence: float
    dedup_key: str
    post: RawPost


ClaimType = Literal["fact", "opinion", "rumor", "hypothesis"]


@dataclass(slots=True)
class AnalysisItem:
    item_id: str
    post_id: str
    tickers: list[str]
    themes: list[str]
    claim_summary: str
    claim_type: ClaimType
    web_research_notes: str | None
    follow_up_questions: list[str] = field(default_factory=list)


@dataclass(slots=True)
class DailyReport:
    run_id: str
    report_date_utc: date
    analysis_items: list[AnalysisItem]
    themes: list[str]
    markdown: str
