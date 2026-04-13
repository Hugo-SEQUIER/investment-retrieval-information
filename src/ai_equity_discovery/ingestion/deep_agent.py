from __future__ import annotations

import json
from http.client import IncompleteRead
import logging
from dataclasses import dataclass
from typing import Any
from urllib import request
from urllib.error import URLError

from ai_equity_discovery.core.config import DiscoveryAgentConfig
from ai_equity_discovery.core.models import DiscoveryAnnotation, RawPost


def _clamp_score(value: object) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 0.0
    if numeric < 0:
        return 0.0
    if numeric > 1:
        return 1.0
    return numeric


@dataclass(slots=True)
class AnnotationStats:
    attempted_posts: int = 0
    annotated_posts: int = 0
    parse_failures: int = 0
    request_failures: int = 0


class OpenRouterDiscoveryAnnotator:
    def __init__(self, config: DiscoveryAgentConfig, model: str | None = None) -> None:
        self._config = config
        self._model = (model or config.model_discovery or config.model).strip()
        self.last_stats = AnnotationStats()

    @property
    def is_ready(self) -> bool:
        return bool(self._config.enabled and self._config.api_key and self._model)

    def annotate(self, posts: list[RawPost]) -> dict[str, DiscoveryAnnotation]:
        logger = logging.getLogger(__name__)
        self.last_stats = AnnotationStats(attempted_posts=len(posts))
        if not posts or not self.is_ready:
            logger.info(
                "Discovery agent skipped | ready=%s | model=%s | posts=%s",
                self.is_ready,
                self._model,
                len(posts),
            )
            return {}

        annotations: dict[str, DiscoveryAnnotation] = {}
        batch_size = max(1, self._config.batch_size)
        for start in range(0, len(posts), batch_size):
            chunk = posts[start : start + batch_size]
            logger.info(
                "Discovery agent batch | model=%s | start=%s | size=%s | total=%s",
                self._model,
                start,
                len(chunk),
                len(posts),
            )
            payload = self._call_with_retries(chunk)
            if payload is None:
                self.last_stats.request_failures += 1
                logger.warning(
                    "Discovery agent request failed for batch at index %s", start
                )
                continue

            parsed = self._parse_annotations(payload)
            if not parsed:
                self.last_stats.parse_failures += 1
                logger.warning(
                    "Discovery agent parse failed for batch at index %s", start
                )
                continue

            annotations.update(parsed)

        self.last_stats.annotated_posts = len(annotations)
        logger.info(
            "Discovery agent done | attempted=%s | annotated=%s | request_failures=%s | parse_failures=%s",
            self.last_stats.attempted_posts,
            self.last_stats.annotated_posts,
            self.last_stats.request_failures,
            self.last_stats.parse_failures,
        )
        return annotations

    def _call_with_retries(self, posts: list[RawPost]) -> dict[str, Any] | None:
        attempts = max(1, self._config.max_retries + 1)
        for _ in range(attempts):
            response = self._call_openrouter(posts)
            if response is not None:
                return response
        return None

    def _call_openrouter(self, posts: list[RawPost]) -> dict[str, Any] | None:
        system_prompt = (
            "You are a market discovery annotation agent. Understand all languages, "
            "but always answer only in English. Do not invent facts. "
            "Return strict JSON only."
        )
        user_payload = {
            "task": "Annotate social posts for discovery shadow mode. Do not filter items.",
            "schema": {
                "annotations": [
                    {
                        "post_id": "string",
                        "actionable": "boolean",
                        "ai_relevance": "number 0-1",
                        "spam_likelihood": "number 0-1",
                        "entity_hints": ["string"],
                        "reason": "short english reason",
                        "english_summary": "single sentence in english",
                    }
                ]
            },
            "posts": [
                {
                    "post_id": post.post_id,
                    "source": post.source,
                    "source_type": post.source_type,
                    "author": post.author,
                    "text": post.text,
                    "url": post.url,
                }
                for post in posts
            ],
            "output_language": self._config.output_language,
        }

        body = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": json.dumps(user_payload, ensure_ascii=True),
                },
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0,
        }

        endpoint = f"{self._config.base_url}/chat/completions"
        data = json.dumps(body).encode("utf-8")
        req = request.Request(
            endpoint,
            data=data,
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self._config.timeout_seconds) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw)
        except IncompleteRead:
            return None
        except (URLError, TimeoutError, ValueError, OSError):
            return None

    def _parse_annotations(
        self, response: dict[str, Any]
    ) -> dict[str, DiscoveryAnnotation]:
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices:
            return {}
        message = choices[0].get("message")
        if not isinstance(message, dict):
            return {}
        content = message.get("content")

        if isinstance(content, str):
            content_text = content
        elif isinstance(content, list):
            text_parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    text_parts.append(item["text"])
            content_text = "\n".join(text_parts)
        else:
            return {}

        try:
            payload = json.loads(content_text)
        except ValueError:
            return {}
        annotations = payload.get("annotations")
        if not isinstance(annotations, list):
            return {}

        parsed: dict[str, DiscoveryAnnotation] = {}
        for item in annotations:
            if not isinstance(item, dict):
                continue
            post_id = item.get("post_id")
            if not isinstance(post_id, str) or not post_id:
                continue

            entity_hints_raw = item.get("entity_hints", [])
            if isinstance(entity_hints_raw, list):
                entity_hints = [
                    str(value).strip()
                    for value in entity_hints_raw
                    if str(value).strip()
                ]
            else:
                entity_hints = []

            parsed[post_id] = DiscoveryAnnotation(
                post_id=post_id,
                actionable=bool(item.get("actionable", False)),
                ai_relevance=_clamp_score(item.get("ai_relevance")),
                spam_likelihood=_clamp_score(item.get("spam_likelihood")),
                entity_hints=entity_hints,
                reason=str(item.get("reason", "")).strip(),
                english_summary=str(item.get("english_summary", "")).strip(),
                provider=self._config.provider,
                model=self._model,
            )
        return parsed
