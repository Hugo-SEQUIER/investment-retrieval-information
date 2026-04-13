from __future__ import annotations

from datetime import date

from ai_equity_discovery.core.models import AnalysisItem


class MarkdownReporter:
    def build(
        self,
        report_date_utc: date,
        analysis_items: list[AnalysisItem],
        themes: list[str],
    ) -> str:
        lines: list[str] = []
        lines.append(f"AI EQUITY DISCOVERY - {report_date_utc.isoformat()}")
        lines.append("")
        lines.append("Signals to review:")

        if not analysis_items:
            lines.append("No high-signal items passed filtering today.")
        for idx, item in enumerate(analysis_items[:12], start=1):
            ticker_label = ", ".join(item.tickers) if item.tickers else "NO_TICKER"
            lines.append(f"{idx}. {ticker_label}")
            lines.append(f"   - Claim type: {item.claim_type}")
            lines.append(f"   - {item.claim_summary}")
            if item.follow_up_questions:
                lines.append(f"   - Follow-up: {item.follow_up_questions[0]}")
            if item.web_research_notes:
                lines.append(f"   - Web note: {item.web_research_notes}")

        if themes:
            lines.append("")
            lines.append("Theme highlights:")
            for theme in themes[:5]:
                lines.append(f"- {theme}")

        return "\n".join(lines)
