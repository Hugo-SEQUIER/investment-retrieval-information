from __future__ import annotations

from urllib.parse import urlparse


TIER_1_OFFICIAL = {
    "investor.nvidia.com",
    "investors.arista.com",
}

TIER_2_EXCHANGE = {
    "nasdaq.com",
    "nyse.com",
}

TIER_3_REFERENCE = {
    "companiesmarketcap.com",
    "macrotrends.net",
    "marketscreener.com",
}

TIER_4_NEWS = {
    "reuters.com",
    "bloomberg.com",
    "wsj.com",
}


def domain_for_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.lower().replace("www.", "")


def source_tier(url: str) -> int:
    domain = domain_for_url(url)
    if domain in TIER_1_OFFICIAL:
        return 1
    if domain in TIER_2_EXCHANGE:
        return 2
    if domain in TIER_3_REFERENCE:
        return 3
    if domain in TIER_4_NEWS:
        return 4
    return 5


def sort_urls_by_reliability(urls: list[str]) -> list[str]:
    unique = list(dict.fromkeys(urls))
    return sorted(unique, key=lambda item: (source_tier(item), item))
