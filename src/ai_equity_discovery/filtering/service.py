from __future__ import annotations

import hashlib
from dataclasses import dataclass

from ai_equity_discovery.core.models import FilteredPost, RawPost


@dataclass(slots=True)
class FilterConfig:
    min_text_length: int = 20
    min_relevance_score: float = 0.5
    max_spam_likelihood: float = 0.75


class FilteringService:
    def __init__(self, config: FilterConfig | None = None) -> None:
        self._config = config or FilterConfig()

    def filter(self, posts: list[RawPost]) -> list[FilteredPost]:
        seen_keys: set[str] = set()
        decisions: list[FilteredPost] = []

        for post in posts:
            dedup_key = self._dedup_key(post)
            if dedup_key in seen_keys:
                decisions.append(
                    FilteredPost(
                        post_id=post.post_id,
                        keep=False,
                        reason_code="DUPLICATE_CONTENT",
                        confidence=0.99,
                        dedup_key=dedup_key,
                        post=post,
                    )
                )
                continue
            seen_keys.add(dedup_key)

            keep, reason_code, confidence = self._decide(post)
            decisions.append(
                FilteredPost(
                    post_id=post.post_id,
                    keep=keep,
                    reason_code=reason_code,
                    confidence=confidence,
                    dedup_key=dedup_key,
                    post=post,
                )
            )

        return decisions

    def _decide(self, post: RawPost) -> tuple[bool, str, float]:
        text = (post.text or "").strip()
        if len(text) < self._config.min_text_length:
            return False, "TOO_SHORT", 0.95

        annotation = post.annotation
        if annotation is not None:
            if annotation.spam_likelihood >= self._config.max_spam_likelihood:
                return False, "HIGH_SPAM_LIKELIHOOD", 0.95
            if annotation.ai_relevance >= self._config.min_relevance_score:
                return True, "AGENT_RELEVANT", annotation.ai_relevance
            if annotation.actionable:
                return True, "AGENT_ACTIONABLE", 0.7

        lowered = text.lower()
        if "$" in text:
            return True, "HAS_CASHTAG", 0.7
        if any(token in lowered for token in ("ai", "gpu", "datacenter", "earnings")):
            return True, "KEYWORD_MATCH", 0.6

        return False, "LOW_SIGNAL", 0.6

    def _dedup_key(self, post: RawPost) -> str:
        normalized = " ".join((post.text or "").strip().lower().split())
        digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()
        return f"{post.source_type}:{digest}"
