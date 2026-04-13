from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from ai_equity_discovery.core.models import AnalysisItem


@dataclass(slots=True)
class MemorySyncResult:
    written_files: list[str]
    warning: str | None = None


@dataclass(slots=True)
class ObsidianMemoryConfig:
    enabled: bool = False
    vault_path: str = ""
    root_subdir: str = "projects/ai-equity-discovery-agent/research"


class ObsidianMemorySync:
    def __init__(self, config: ObsidianMemoryConfig) -> None:
        self._config = config

    def sync(
        self,
        report_date_utc: date,
        analysis_items: list[AnalysisItem],
        markdown: str,
    ) -> MemorySyncResult:
        if not self._config.enabled:
            return MemorySyncResult(written_files=[], warning="MEMORY_DISABLED")

        vault_path = Path(self._config.vault_path).expanduser()
        if not self._config.vault_path or not vault_path.exists():
            return MemorySyncResult(written_files=[], warning="VAULT_PATH_UNAVAILABLE")

        root = vault_path / self._config.root_subdir
        files: list[str] = []

        daily_logs = root / "Daily Logs"
        daily_logs.mkdir(parents=True, exist_ok=True)
        daily_file = daily_logs / f"{report_date_utc.isoformat()}.md"
        daily_file.write_text(
            self._build_daily_log(report_date_utc, markdown),
            encoding="utf-8",
        )
        files.append(str(daily_file))

        companies_dir = root / "Companies"
        companies_dir.mkdir(parents=True, exist_ok=True)
        for ticker in sorted(
            {ticker for item in analysis_items for ticker in item.tickers}
        ):
            note_file = companies_dir / f"{ticker}.md"
            note_file.write_text(
                self._build_company_note(ticker, analysis_items),
                encoding="utf-8",
            )
            files.append(str(note_file))

        return MemorySyncResult(written_files=files)

    def _build_daily_log(self, report_date_utc: date, markdown: str) -> str:
        return "\n".join(
            [
                f"# Daily Log - {report_date_utc.isoformat()}",
                "",
                "## Auto-Generated",
                markdown,
                "",
                "## Hermes Notes",
                "",
                "## Human Notes",
                "",
            ]
        )

    def _build_company_note(
        self, ticker: str, analysis_items: list[AnalysisItem]
    ) -> str:
        related = [item for item in analysis_items if ticker in item.tickers]
        lines = [f"# {ticker}", "", "## Auto-Generated", ""]
        for item in related[:8]:
            lines.append(f"- {item.claim_summary}")
            if item.follow_up_questions:
                lines.append(f"  - Follow-up: {item.follow_up_questions[0]}")
        lines.extend(["", "## Hermes Notes", "", "## Human Notes", ""])
        return "\n".join(lines)
