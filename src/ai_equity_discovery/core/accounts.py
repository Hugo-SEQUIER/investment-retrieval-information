from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


ACCOUNTS_CONFIG_ENV = "WATCHED_ACCOUNTS_PATH"
DEFAULT_ACCOUNTS_CONFIG = "config/watched_accounts.json"


@dataclass(slots=True)
class WatchedAccounts:
    x_accounts: list[str] = field(default_factory=list)
    reddit_subreddits: list[str] = field(default_factory=list)
    added_at: str = ""  # ISO timestamp of last modification

    def normalize(self) -> "WatchedAccounts":
        """Strip @ prefixes and whitespace from X accounts."""
        self.x_accounts = [
            a.lstrip("@").strip() for a in self.x_accounts if a.strip()
        ]
        self.reddit_subreddits = [
            s.strip() for s in self.reddit_subreddits if s.strip()
        ]
        return self


def _resolve_accounts_path() -> Path:
    path_str = os.getenv(ACCOUNTS_CONFIG_ENV, "").strip()
    if path_str:
        return Path(path_str)
    return Path(HERMES_PROJECT_ROOT()) / DEFAULT_ACCOUNTS_CONFIG


def HERMES_PROJECT_ROOT() -> Path:
    """Resolve project root — walk up from this file's directory."""
    return Path(__file__).resolve().parents[3]


def load_watched_accounts() -> WatchedAccounts:
    path = _resolve_accounts_path()
    if not path.exists():
        return WatchedAccounts()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    accounts = WatchedAccounts(
        x_accounts=list(data.get("x_accounts", [])),
        reddit_subreddits=list(data.get("reddit_subreddits", [])),
        added_at=data.get("added_at", ""),
    )
    return accounts.normalize()


def save_watched_accounts(accounts: WatchedAccounts) -> None:
    path = _resolve_accounts_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    accounts.added_at = datetime.now(timezone.utc).isoformat()
    payload = {
        "x_accounts": sorted(set(accounts.x_accounts)),
        "reddit_subreddits": sorted(set(accounts.reddit_subreddits)),
        "added_at": accounts.added_at,
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def add_x_account(username: str) -> WatchedAccounts:
    username = username.lstrip("@").strip()
    if not username:
        raise ValueError("Account username cannot be empty")
    accounts = load_watched_accounts()
    if username not in accounts.x_accounts:
        accounts.x_accounts.append(username)
        save_watched_accounts(accounts)
    return accounts


def remove_x_account(username: str) -> WatchedAccounts:
    username = username.lstrip("@").strip()
    accounts = load_watched_accounts()
    if username in accounts.x_accounts:
        accounts.x_accounts.remove(username)
        save_watched_accounts(accounts)
    return accounts


def add_subreddit(subreddit: str) -> WatchedAccounts:
    subreddit = subreddit.strip()
    if not subreddit:
        raise ValueError("Subreddit name cannot be empty")
    accounts = load_watched_accounts()
    if subreddit not in accounts.reddit_subreddits:
        accounts.reddit_subreddits.append(subreddit)
        save_watched_accounts(accounts)
    return accounts


def remove_subreddit(subreddit: str) -> WatchedAccounts:
    subreddit = subreddit.strip()
    accounts = load_watched_accounts()
    if subreddit in accounts.reddit_subreddits:
        accounts.reddit_subreddits.remove(subreddit)
        save_watched_accounts(accounts)
    return accounts
