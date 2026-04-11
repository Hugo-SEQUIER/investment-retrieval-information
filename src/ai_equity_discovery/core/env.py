from __future__ import annotations

from pathlib import Path


_LOADED = False


def load_env() -> None:
    global _LOADED
    if _LOADED:
        return

    try:
        from dotenv import load_dotenv
    except ImportError:
        _LOADED = True
        return

    repo_root = Path(__file__).resolve().parents[3]
    load_dotenv(repo_root / ".env")
    _LOADED = True
