from __future__ import annotations

import asyncio
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


class TwscrapeAdapter(SourceAdapter):
    source_name = "x"

    def __init__(self, accounts: list[str], limit_per_account: int = 20) -> None:
        self._accounts = [
            account.lstrip("@").strip() for account in accounts if account.strip()
        ]
        self._limit_per_account = limit_per_account

    def _run_async(self, coro: Any) -> Any:
        try:
            return asyncio.run(coro)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()

    def fetch_posts(self, since_utc: datetime | None = None) -> list[RawPost]:
        if not self._accounts:
            return []

        try:
            from twscrape import API
        except ImportError as exc:
            raise RuntimeError("twscrape is not installed") from exc

        async def _collect() -> list[RawPost]:
            api = API()
            posts: list[RawPost] = []
            for account in self._accounts:
                async for tweet in api.user_tweets(
                    account, limit=self._limit_per_account
                ):
                    tweet_dt = getattr(tweet, "date", None)
                    if tweet_dt is None:
                        continue
                    if since_utc is not None and tweet_dt < since_utc:
                        continue

                    tweet_id = str(getattr(tweet, "id", ""))
                    if not tweet_id:
                        continue

                    tweet_user = getattr(tweet, "user", None)
                    username = (
                        getattr(tweet_user, "username", None)
                        or getattr(tweet_user, "displayname", None)
                        or account
                    )

                    posts.append(
                        RawPost(
                            post_id=f"x:{tweet_id}",
                            source=f"x:{account}",
                            source_type="x",
                            author=str(username),
                            url=f"https://x.com/{account}/status/{tweet_id}",
                            text=str(getattr(tweet, "rawContent", "") or ""),
                            published_at_utc=tweet_dt,
                            ingested_at_utc=utc_now(),
                            engagement={
                                "likes": int(getattr(tweet, "likeCount", 0) or 0),
                                "retweets": int(getattr(tweet, "retweetCount", 0) or 0),
                                "replies": int(getattr(tweet, "replyCount", 0) or 0),
                            },
                        )
                    )
            return posts

        return self._run_async(_collect())


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
