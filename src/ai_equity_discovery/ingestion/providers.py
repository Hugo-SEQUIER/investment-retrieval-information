from __future__ import annotations

from datetime import datetime, timezone
from os import getenv
from typing import Any

from ai_equity_discovery.core.models import RawPost, utc_now
from ai_equity_discovery.ingestion.base import SourceAdapter


class InMemorySourceAdapter(SourceAdapter):
    def __init__(self, source_name: str, posts: list[RawPost]) -> None:
        self.source_name = source_name
        self._posts = posts

    def fetch_posts(self, since_utc: datetime | None = None) -> list[RawPost]:
        if since_utc is None:
            return list(self._posts)
        return [post for post in self._posts if post.published_at_utc >= since_utc]


class ScweetAdapter(SourceAdapter):
    source_name = "x"

    def __init__(self, accounts: list[str], limit_per_account: int = 20) -> None:
        self._accounts = [
            account.lstrip("@").strip() for account in accounts if account.strip()
        ]
        self._limit_per_account = limit_per_account

    def _parse_datetime(self, value: Any) -> datetime | None:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

        text = str(value).strip()
        if not text:
            return None

        if text.endswith("Z"):
            text = text[:-1] + "+00:00"

        try:
            parsed = datetime.fromisoformat(text)
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def _as_records(self, payload: Any) -> list[dict[str, Any]]:
        if payload is None:
            return []

        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]

        if isinstance(payload, dict):
            if "tweets" in payload and isinstance(payload["tweets"], list):
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

    def fetch_posts(self, since_utc: datetime | None = None) -> list[RawPost]:
        if not self._accounts:
            return []

        auth_token = getenv("TWITTER_AUTH_TOKEN") or getenv("SCWEET_AUTH_TOKEN")
        if not auth_token:
            raise RuntimeError(
                "Missing X auth token. Set TWITTER_AUTH_TOKEN (or SCWEET_AUTH_TOKEN) in .env"
            )

        try:
            from Scweet import Scweet as ScweetClient
        except ImportError as exc:
            raise RuntimeError("Scweet is not installed") from exc

        db_path = getenv("SCWEET_DB_PATH", "scweet_state.db")
        client = ScweetClient(auth_token=auth_token, db_path=db_path)

        posts: list[RawPost] = []
        for account in self._accounts:
            payload = client.get_profile_tweets(
                [account], limit=self._limit_per_account
            )
            for record in self._as_records(payload):
                tweet_id = (
                    record.get("tweet_id") or record.get("id") or record.get("rest_id")
                )
                if not tweet_id:
                    continue

                published_at = self._parse_datetime(
                    record.get("created_at")
                    or record.get("createdAt")
                    or record.get("date")
                    or record.get("timestamp")
                )
                if published_at is None:
                    continue
                if since_utc is not None and published_at < since_utc:
                    continue

                username = (
                    record.get("username")
                    or record.get("screen_name")
                    or record.get("user")
                    or account
                )
                text = (
                    record.get("full_text")
                    or record.get("text")
                    or record.get("rawContent")
                    or ""
                )

                url = record.get("url") or record.get("permalink")
                if not url:
                    url = f"https://x.com/{username}/status/{tweet_id}"

                posts.append(
                    RawPost(
                        post_id=f"x:{tweet_id}",
                        source=f"x:{account}",
                        source_type="x",
                        author=str(username),
                        url=str(url),
                        text=str(text),
                        published_at_utc=published_at,
                        ingested_at_utc=utc_now(),
                        engagement={
                            "likes": int(record.get("likes", 0) or 0),
                            "retweets": int(record.get("retweets", 0) or 0),
                            "replies": int(record.get("replies", 0) or 0),
                        },
                    )
                )

        return posts


class TwscrapeAdapter(ScweetAdapter):
    """Backward-compatibility alias; now uses Scweet backend."""


class RedditAdapter(SourceAdapter):
    source_name = "reddit"

    def __init__(self, subreddits: list[str], limit_per_subreddit: int = 25) -> None:
        self._subreddits = [name.strip() for name in subreddits if name.strip()]
        self._limit_per_subreddit = limit_per_subreddit

    def fetch_posts(self, since_utc: datetime | None = None) -> list[RawPost]:
        if not self._subreddits:
            return []

        try:
            import praw
        except ImportError as exc:
            raise RuntimeError("praw is not installed") from exc

        client_id = getenv("REDDIT_CLIENT_ID")
        client_secret = getenv("REDDIT_CLIENT_SECRET")
        user_agent = getenv("REDDIT_USER_AGENT", "ai-equity-discovery/0.1")

        if not client_id or not client_secret:
            raise RuntimeError(
                "Missing Reddit credentials: REDDIT_CLIENT_ID/REDDIT_CLIENT_SECRET"
            )

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        posts: list[RawPost] = []
        for subreddit_name in self._subreddits:
            subreddit = reddit.subreddit(subreddit_name)
            for submission in subreddit.hot(limit=self._limit_per_subreddit):
                created_utc = datetime.fromtimestamp(
                    float(submission.created_utc), tz=timezone.utc
                )
                if since_utc is not None and created_utc < since_utc:
                    continue

                post_id = str(submission.id)
                title = str(getattr(submission, "title", "") or "")
                selftext = str(getattr(submission, "selftext", "") or "")
                text = f"{title}\n{selftext}".strip()

                posts.append(
                    RawPost(
                        post_id=f"reddit:{post_id}",
                        source=f"reddit:r/{subreddit_name}",
                        source_type="reddit",
                        author=str(
                            getattr(submission, "author", "unknown") or "unknown"
                        ),
                        url=f"https://reddit.com{submission.permalink}",
                        text=text,
                        published_at_utc=created_utc,
                        ingested_at_utc=utc_now(),
                        engagement={
                            "upvotes": int(getattr(submission, "score", 0) or 0),
                            "comments": int(
                                getattr(submission, "num_comments", 0) or 0
                            ),
                        },
                    )
                )

        return posts
