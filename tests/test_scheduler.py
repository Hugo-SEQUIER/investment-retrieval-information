from __future__ import annotations

import sys
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.scheduler import run_pipeline


class SchedulerTest(unittest.TestCase):
    @patch("ai_equity_discovery.scheduler.subprocess.run")
    def test_run_pipeline_invokes_module_entrypoint(self, mock_run) -> None:
        mock_run.return_value.returncode = 0
        code = run_pipeline(["--top-n", "3"])
        self.assertEqual(code, 0)
        called = mock_run.call_args.args[0]
        self.assertEqual(called[1:3], ["-m", "ai_equity_discovery"])


if __name__ == "__main__":
    unittest.main()
