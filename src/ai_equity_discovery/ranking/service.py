from __future__ import annotations

from dataclasses import dataclass

from ai_equity_discovery.core.models import (
    EnrichedCompany,
    MentionCandidate,
    RankedIdea,
    RawPost,
    ResolvedCompany,
)


@dataclass(slots=True)
class RankingWeights:
    mention_count: float = 0.4
    cross_source: float = 0.2
    ai_relevance: float = 0.2
    resolution_confidence: float = 0.2


class RankingService:
    def __init__(self, weights: RankingWeights | None = None) -> None:
        self._weights = weights or RankingWeights()

    def rank(
        self,
        posts: list[RawPost],
        candidates: list[MentionCandidate],
        resolved: list[ResolvedCompany],
        enriched: list[EnrichedCompany],
    ) -> tuple[list[RankedIdea], list[str]]:
        post_by_id = {post.post_id: post for post in posts}
        candidate_by_id = {
            candidate.candidate_id: candidate for candidate in candidates
        }
        enrichment_by_id = {item.canonical_id: item for item in enriched}

        grouped: dict[str, list[ResolvedCompany]] = {}
        for item in resolved:
            if item.unresolved:
                continue
            grouped.setdefault(item.canonical_id, []).append(item)

        themes: dict[str, int] = {}
        ranked: list[RankedIdea] = []

        for canonical_id, items in grouped.items():
            mention_count = len(items)
            source_types: set[str] = set()
            ai_matches = 0
            confidence_total = 0.0
            trend_themes: list[str] = []

            for resolved_item in items:
                candidate = candidate_by_id.get(resolved_item.candidate_id)
                if candidate is None:
                    continue
                post = post_by_id.get(candidate.raw_post_id)
                if post is not None:
                    source_types.add(post.source_type)
                ai_matches += len(candidate.themes)
                confidence_total += resolved_item.confidence
                for theme in candidate.themes:
                    themes[theme] = themes.get(theme, 0) + 1
                    if theme not in trend_themes:
                        trend_themes.append(theme)

            cross_source_count = len(source_types)
            mention_signal = min(1.0, mention_count / 5.0)
            cross_source_signal = min(1.0, cross_source_count / 2.0)
            ai_relevance_signal = 1.0 if ai_matches > 0 else 0.0
            resolution_confidence_signal = confidence_total / max(1, mention_count)

            score = (
                mention_signal * self._weights.mention_count
                + cross_source_signal * self._weights.cross_source
                + ai_relevance_signal * self._weights.ai_relevance
                + resolution_confidence_signal * self._weights.resolution_confidence
            )

            seed = items[0]
            enrich = enrichment_by_id.get(canonical_id)
            trend_reason = (
                f"Mentioned {mention_count} times across {cross_source_count} source(s); themes: "
                + ", ".join(trend_themes[:3])
                if trend_themes
                else f"Mentioned {mention_count} times across {cross_source_count} source(s)."
            )

            ranked.append(
                RankedIdea(
                    canonical_id=canonical_id,
                    company_name=seed.company_name or canonical_id,
                    ticker=seed.ticker or "N/A",
                    exchange=seed.exchange or "N/A",
                    country=seed.country or "N/A",
                    sector=seed.sector,
                    industry=seed.industry,
                    business_description=enrich.business_description
                    if enrich
                    else None,
                    market_cap_usd=enrich.market_cap_usd if enrich else None,
                    revenue_usd=enrich.revenue_usd if enrich else None,
                    score=round(score, 4),
                    mention_count=mention_count,
                    cross_source_count=cross_source_count,
                    ai_relevance_score=ai_relevance_signal,
                    resolution_confidence=round(resolution_confidence_signal, 4),
                    trend_reason=trend_reason,
                    caveats=enrich.caveats if enrich else ["NO_ENRICHMENT_FACTS"],
                )
            )

        ranked.sort(key=lambda item: item.score, reverse=True)
        sorted_themes = [
            key
            for key, _ in sorted(themes.items(), key=lambda pair: pair[1], reverse=True)
        ]
        return ranked, sorted_themes
