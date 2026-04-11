from __future__ import annotations

import re


_MONEY_PATTERN = re.compile(
    r"(?P<prefix>USD|US\$|\$|EUR|€|GBP|£|JPY|¥)?\s*"
    r"(?P<number>\d+(?:[\.,]\d+)?)\s*"
    r"(?P<suffix>T|B|M|K|trillion|billion|million|thousand)?",
    flags=re.IGNORECASE,
)


def _normalize_currency(prefix: str | None) -> str | None:
    if not prefix:
        return None
    normalized = prefix.upper()
    if normalized in {"$", "US$", "USD"}:
        return "USD"
    if normalized in {"€", "EUR"}:
        return "EUR"
    if normalized in {"£", "GBP"}:
        return "GBP"
    if normalized in {"¥", "JPY"}:
        return "JPY"
    return None


def _suffix_multiplier(suffix: str | None) -> float:
    if not suffix:
        return 1.0
    normalized = suffix.lower()
    if normalized in {"t", "trillion"}:
        return 1_000_000_000_000.0
    if normalized in {"b", "billion"}:
        return 1_000_000_000.0
    if normalized in {"m", "million"}:
        return 1_000_000.0
    if normalized in {"k", "thousand"}:
        return 1_000.0
    return 1.0


def parse_money_token(token: str) -> tuple[float, str | None] | None:
    match = _MONEY_PATTERN.search(token)
    if match is None:
        return None

    number_text = match.group("number").replace(",", "")
    value = float(number_text) * _suffix_multiplier(match.group("suffix"))
    currency = _normalize_currency(match.group("prefix"))
    return value, currency


def _extract_labeled_money(
    text: str, label_regex: re.Pattern[str]
) -> tuple[float, str | None] | None:
    lowered = text.lower()
    for label_match in label_regex.finditer(lowered):
        start = label_match.start()
        end = min(len(text), start + 180)
        window = text[start:end]
        money = parse_money_token(window)
        if money is not None:
            return money
    return None


_MARKET_CAP_LABEL = re.compile(r"market\s*cap(?:italization)?", flags=re.IGNORECASE)
_REVENUE_LABEL = re.compile(
    r"(?:annual\s+)?revenue|total\s+revenue|ttm\s+revenue", flags=re.IGNORECASE
)


def extract_market_cap(text: str) -> tuple[float | None, str | None]:
    found = _extract_labeled_money(text, _MARKET_CAP_LABEL)
    if found is None:
        return None, None
    value, currency = found
    return value, currency or "USD"


def extract_revenue(text: str) -> tuple[float | None, str | None]:
    found = _extract_labeled_money(text, _REVENUE_LABEL)
    if found is None:
        return None, None
    value, currency = found
    return value, currency or "USD"


def summarize_business_description(text: str, max_chars: int) -> str | None:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return None
    if len(compact) <= max_chars:
        return compact

    sentence = compact[:max_chars]
    period_pos = sentence.rfind(".")
    if period_pos > 80:
        return sentence[: period_pos + 1]
    return sentence
