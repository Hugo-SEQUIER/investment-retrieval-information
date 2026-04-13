from __future__ import annotations

from datetime import datetime, timezone
from http.client import IncompleteRead
import os
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.ingestion.providers import (
    ScweetAdapter,
    resolve_scweet_db_path,
)
from ai_equity_discovery.core.config import DiscoveryAgentConfig
from ai_equity_discovery.ingestion.deep_agent import OpenRouterDiscoveryAnnotator


class ScweetAdapterDateParseTest(unittest.TestCase):
    def test_parse_twitter_style_created_at(self) -> None:
        adapter = ScweetAdapter(accounts=["jukan05"])
        parsed = adapter._parse_datetime("Mon Apr 13 12:34:56 +0000 2026")
        self.assertIsNotNone(parsed)
        assert parsed is not None
        self.assertEqual(parsed.tzinfo, timezone.utc)
        self.assertEqual(parsed.year, 2026)
        self.assertEqual(parsed.month, 4)
        self.assertEqual(parsed.day, 13)


class ScweetDbPathRotationTest(unittest.TestCase):
    def test_resolve_scweet_db_path_uses_daily_rotation_and_cleanup(self) -> None:
        original_env = os.environ.copy()
        with TemporaryDirectory() as tmp:
            try:
                os.environ["SCWEET_DB_ROTATE_DAILY"] = "true"
                os.environ["SCWEET_DB_DIR"] = tmp
                os.environ["SCWEET_DB_RETENTION_DAYS"] = "7"

                old_file = Path(tmp) / "scweet_2026-04-01.db"
                old_file.write_text("x", encoding="utf-8")

                now = datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc)
                db_path = resolve_scweet_db_path(now_utc=now)

                self.assertTrue(db_path.endswith("scweet_2026-04-13.db"))
                self.assertFalse(old_file.exists())
            finally:
                os.environ.clear()
                os.environ.update(original_env)

    def test_resolve_scweet_db_path_falls_back_to_static_path(self) -> None:
        original_env = os.environ.copy()
        try:
            os.environ.pop("SCWEET_DB_ROTATE_DAILY", None)
            os.environ["SCWEET_DB_PATH"] = "custom_scweet.db"
            db_path = resolve_scweet_db_path()
            self.assertEqual(db_path, "custom_scweet.db")
        finally:
            os.environ.clear()
            os.environ.update(original_env)


class OpenRouterAnnotatorTransportTest(unittest.TestCase):
    def test_incomplete_read_returns_none_and_does_not_raise(self) -> None:
        annotator = OpenRouterDiscoveryAnnotator(
            DiscoveryAgentConfig(
                enabled=True,
                api_key="key",
                model="qwen/qwen3.6-plus",
            )
        )

        with patch(
            "ai_equity_discovery.ingestion.deep_agent.request.urlopen",
            side_effect=IncompleteRead(b"partial", 100),
        ):
            result = annotator._call_openrouter([])

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
