from __future__ import annotations

from datetime import date
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ai_equity_discovery.core.models import AnalysisItem
from ai_equity_discovery.reporting.markdown import MarkdownReporter


class MarkdownReporterTest(unittest.TestCase):
    def test_report_renders_analysis_items(self) -> None:
        reporter = MarkdownReporter()
        item = AnalysisItem(
            item_id="analysis:x:1",
            post_id="x:1",
            tickers=["NVDA"],
            themes=["gpu-demand"],
            claim_summary="NVIDIA demand remains strong for AI clusters.",
            claim_type="opinion",
            web_research_notes="Recent IR note confirms strong data-center demand.",
            follow_up_questions=["Validate latest primary-source update for NVDA."],
        )

        markdown = reporter.build(date(2026, 4, 13), [item], ["gpu-demand"])
        self.assertIn("Signals to review:", markdown)
        self.assertIn("1. NVDA", markdown)
        self.assertIn("Claim type: opinion", markdown)
        self.assertIn("Theme highlights:", markdown)


if __name__ == "__main__":
    unittest.main()
