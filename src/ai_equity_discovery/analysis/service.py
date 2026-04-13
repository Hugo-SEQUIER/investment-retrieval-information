from __future__ import annotations

from collections import Counter
from typing import Protocol

from ai_equity_discovery.core.models import (
    AnalysisItem,
    ClaimType,
    FilteredPost,
    RawPost,
)
from ai_equity_discovery.extraction.service import ExtractionService


class WebResearcher(Protocol):
    def research(self, query: str) -> str | None: ...


class AnalysisService:
    def __init__(
        self,
        extraction: ExtractionService | None = None,
        web_researcher: WebResearcher | None = None,
    ) -> None:
        self._extraction = extraction or ExtractionService()
        self._web_researcher = web_researcher

    def analyze(self, filtered: list[FilteredPost]) -> list[AnalysisItem]:
        kept = [item for item in filtered if item.keep]
        analyses: list[AnalysisItem] = []

        for item in kept:
            post = item.post
            candidate = self._extract_for_post(post)
            tickers = candidate.tickers if candidate is not None else []
            themes = candidate.themes if candidate is not None else []

            claim_summary = self._claim_summary(post)
            claim_type = self._claim_type(post.text)
            follow_up_questions = self._follow_up_questions(tickers, themes)
            web_notes = self._web_notes(post, tickers, themes)

            analyses.append(
                AnalysisItem(
                    item_id=f"analysis:{post.post_id}",
                    post_id=post.post_id,
                    tickers=tickers,
                    themes=themes,
                    claim_summary=claim_summary,
                    claim_type=claim_type,
                    web_research_notes=web_notes,
                    follow_up_questions=follow_up_questions,
                )
            )

        return analyses

    def themes(self, items: list[AnalysisItem], limit: int = 5) -> list[str]:
        counts: Counter[str] = Counter()
        for item in items:
            counts.update(item.themes)
        return [theme for theme, _ in counts.most_common(limit)]

    def _extract_for_post(self, post: RawPost):
        extracted = self._extraction.extract([post])
        if not extracted:
            return None
        return extracted[0]

    def _claim_summary(self, post: RawPost) -> str:
        annotation = post.annotation
        if annotation is not None and annotation.english_summary.strip():
            return annotation.english_summary.strip()

        text = " ".join(post.text.strip().split())
        if len(text) <= 200:
            return text
        return text[:197].rstrip() + "..."

    def _claim_type(self, text: str) -> ClaimType:
        lowered = text.lower()
        if any(token in lowered for token in ("rumor", "unconfirmed", "leak")):
            return "rumor"
        if any(
            token in lowered
            for token in ("i think", "imo", "looks like", "bullish", "bearish")
        ):
            return "opinion"
        if any(token in lowered for token in ("could", "might", "maybe", "expect")):
            return "hypothesis"
        return "fact"

    def _follow_up_questions(self, tickers: list[str], themes: list[str]) -> list[str]:
        questions: list[str] = []
        for ticker in tickers[:2]:
            questions.append(f"Validate latest primary-source update for {ticker}.")
        for theme in themes[:1]:
            questions.append(f"What changed this week for theme '{theme}'?")
        if not questions:
            questions.append("Does this post contain a concrete, verifiable catalyst?")
        return questions

    def _web_notes(
        self, post: RawPost, tickers: list[str], themes: list[str]
    ) -> str | None:
        if self._web_researcher is None:
            return None
        query_parts = [" ".join(tickers[:2]), " ".join(themes[:2]), post.text[:80]]
        query = " ".join(part for part in query_parts if part).strip()
        if not query:
            return None
        try:
            return self._web_researcher.research(query)
        except Exception:
            return None
