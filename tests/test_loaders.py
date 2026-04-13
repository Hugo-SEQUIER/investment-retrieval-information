from __future__ import annotations

import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.core.loaders import (
    load_source_config,
)


class LoadersTest(unittest.TestCase):
    def test_loaders_parse_source_config(self) -> None:
        with TemporaryDirectory() as tmp:
            base = Path(tmp)

            sources = base / "sources.json"
            sources.write_text(
                json.dumps(
                    {"x_accounts": ["jukan05"], "reddit_subreddits": ["stocks"]}
                ),
                encoding="utf-8",
            )

            source_cfg = load_source_config(sources)

            self.assertEqual(source_cfg.x_accounts, ["jukan05"])
            self.assertEqual(source_cfg.reddit_subreddits, ["stocks"])


if __name__ == "__main__":
    unittest.main()
