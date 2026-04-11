from __future__ import annotations

import re

from ai_equity_discovery.core.models import MentionCandidate, RawPost


TICKER_PATTERN = re.compile(r"\$?[A-Z]{1,5}\b")
STOP_TICKERS = {
    "A",
    "AI",
    "ALL",
    "AND",
    "ARE",
    "FOR",
    "I",
    "IT",
    "THE",
    "TO",
}

THEME_KEYWORDS: dict[str, set[str]] = {
    "hyperscaler-capex": {"capex", "hyperscaler", "cloud"},
    "gpu-demand": {"gpu", "accelerator", "cuda"},
    "optical-interconnect": {"optical", "photonics", "interconnect"},
    "datacenter-energy": {"power", "cooling", "energy", "datacenter"},
    "advanced-packaging": {"packaging", "chiplet", "substrate"},
    "memory-upcycle": {"hbm", "dram", "memory"},
}


class ExtractionService:
    def extract(self, posts: list[RawPost]) -> list[MentionCandidate]:
        candidates: list[MentionCandidate] = []
        for post in posts:
            tickers = self._extract_tickers(post.text)
            themes = self._extract_themes(post.text)
            if not tickers and not themes:
                continue
            confidence = 0.8 if tickers else 0.5
            candidates.append(
                MentionCandidate(
                    candidate_id=post.post_id,
                    raw_post_id=post.post_id,
                    tickers=tickers,
                    company_hints=[],
                    themes=themes,
                    confidence=confidence,
                )
            )
        return candidates

    def _extract_tickers(self, text: str) -> list[str]:
        tickers: list[str] = []
        for match in TICKER_PATTERN.findall(text.upper()):
            ticker = match.lstrip("$")
            if ticker in STOP_TICKERS:
                continue
            if ticker not in tickers:
                tickers.append(ticker)
        return tickers

    def _extract_themes(self, text: str) -> list[str]:
        lowered = text.lower()
        themes: list[str] = []
        for theme, keywords in THEME_KEYWORDS.items():
            if any(keyword in lowered for keyword in keywords):
                themes.append(theme)
        return themes
