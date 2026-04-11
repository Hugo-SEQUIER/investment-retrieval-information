from __future__ import annotations

from datetime import date

from ai_equity_discovery.core.models import RankedIdea


def _format_usd(value: float | None) -> str:
    if value is None:
        return "N/A"
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.1f}T"
    if abs_value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.1f}B"
    if abs_value >= 1_000_000:
        return f"${value / 1_000_000:.1f}M"
    return f"${value:,.0f}"


class MarkdownReporter:
    def build(
        self, report_date_utc: date, top_ideas: list[RankedIdea], themes: list[str]
    ) -> str:
        lines: list[str] = []
        lines.append(f"AI EQUITY DISCOVERY - {report_date_utc.isoformat()}")
        lines.append("")
        lines.append("Top names:")

        for idx, idea in enumerate(top_ideas, start=1):
            lines.append(f"{idx}. {idea.company_name} ({idea.ticker})")
            if idea.business_description:
                lines.append(f"   - {idea.business_description}")
            lines.append(f"   - Market cap: {_format_usd(idea.market_cap_usd)}")
            lines.append(f"   - Revenue: {_format_usd(idea.revenue_usd)}")
            lines.append(f"   - {idea.trend_reason}")
            if idea.caveats:
                lines.append(f"   - Caveats: {', '.join(idea.caveats)}")

        if themes:
            lines.append("")
            lines.append("Themes:")
            for theme in themes[:5]:
                lines.append(f"- {theme}")

        return "\n".join(lines)
