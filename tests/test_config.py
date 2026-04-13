from __future__ import annotations

import os
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.core.config import AppConfig


class AppConfigEnvTest(unittest.TestCase):
    def test_from_env_reads_openrouter_and_lookback_settings(self) -> None:
        original = os.environ.copy()
        try:
            os.environ["OPENROUTER_API_KEY"] = "key123"
            os.environ["OPENROUTER_MODEL"] = "qwen/qwen3.6-plus"
            os.environ["OPENROUTER_MODEL_DISCOVERY"] = "qwen/qwen2.5-7b-instruct"
            os.environ["OPENROUTER_MODEL_ANALYSIS"] = "qwen/qwen3.6-plus"
            os.environ["AGENT_OUTPUT_LANGUAGE"] = "en"
            os.environ["BOOTSTRAP_LOOKBACK_DAYS"] = "7"
            os.environ["DAILY_LOOKBACK_DAYS"] = "1"
            os.environ["DISCOVERY_AGENT_ENABLED"] = "true"
            os.environ["OBSIDIAN_MEMORY_ENABLED"] = "true"
            os.environ["CLAUDE_VAULT"] = "C:/vault"

            cfg = AppConfig.from_env()
            self.assertEqual(cfg.bootstrap_lookback_days, 7)
            self.assertEqual(cfg.daily_lookback_days, 1)
            self.assertEqual(cfg.discovery_agent.model, "qwen/qwen3.6-plus")
            self.assertEqual(
                cfg.discovery_agent.model_discovery,
                "qwen/qwen2.5-7b-instruct",
            )
            self.assertEqual(cfg.discovery_agent.model_analysis, "qwen/qwen3.6-plus")
            self.assertEqual(cfg.discovery_agent.output_language, "en")
            self.assertTrue(cfg.discovery_agent.enabled)
            self.assertTrue(cfg.memory.enabled)
            self.assertEqual(cfg.memory.vault_path, "C:/vault")
        finally:
            os.environ.clear()
            os.environ.update(original)


if __name__ == "__main__":
    unittest.main()
