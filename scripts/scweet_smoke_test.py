from __future__ import annotations

import argparse
import os
from pathlib import Path


def load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return

    load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scweet smoke test (fetch 10 tweets)")
    parser.add_argument("--query", default="AI stocks", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Number of tweets")
    parser.add_argument("--db-path", default="scweet_state.db", help="Scweet DB path")
    return parser.parse_args()


def as_records(payload: object) -> list[dict]:
    if payload is None:
        return []
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        if isinstance(payload.get("tweets"), list):
            return [item for item in payload["tweets"] if isinstance(item, dict)]
        return [payload]

    to_dict = getattr(payload, "to_dict", None)
    if callable(to_dict):
        try:
            records = to_dict("records")
        except TypeError:
            records = to_dict()
        if isinstance(records, list):
            return [item for item in records if isinstance(item, dict)]
        if isinstance(records, dict):
            return [records]
    return []


def main() -> int:
    load_env()
    args = parse_args()

    auth_token = os.getenv("TWITTER_AUTH_TOKEN") or os.getenv("SCWEET_AUTH_TOKEN")
    if not auth_token:
        print("Missing TWITTER_AUTH_TOKEN (or SCWEET_AUTH_TOKEN) in .env")
        return 1

    try:
        from Scweet import Scweet
    except ImportError:
        print("Scweet is not installed. Run: python -m pip install '.[ingestion]'")
        return 1

    client = Scweet(auth_token=auth_token, db_path=args.db_path)
    payload = client.search(args.query, limit=args.limit, save=False)
    rows = as_records(payload)

    print(f"Requested: {args.limit}")
    print(f"Retrieved: {len(rows)}")

    for idx, row in enumerate(rows[: min(3, len(rows))], start=1):
        tweet_id = row.get("tweet_id") or row.get("id") or row.get("rest_id") or "?"
        username = row.get("username") or row.get("screen_name") or "?"
        text = (row.get("full_text") or row.get("text") or "").replace("\n", " ")
        print(f"{idx}. [{tweet_id}] @{username}: {text[:120]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
