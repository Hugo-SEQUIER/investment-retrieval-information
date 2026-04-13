from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from uuid import uuid4

from ai_equity_discovery.core.config import AppConfig
from ai_equity_discovery.core.database import SQLiteStore
from ai_equity_discovery.core.models import DailyReport
from ai_equity_discovery.analysis.service import AnalysisService
from ai_equity_discovery.filtering.service import FilteringService
from ai_equity_discovery.ingestion.service import IngestionService
from ai_equity_discovery.memory.obsidian import ObsidianMemorySync
from ai_equity_discovery.reporting.markdown import MarkdownReporter


class DailyPipeline:
    def __init__(
        self,
        config: AppConfig,
        store: SQLiteStore,
        ingestion: IngestionService,
        filtering: FilteringService,
        analysis: AnalysisService,
        reporter: MarkdownReporter,
        memory: ObsidianMemorySync,
    ) -> None:
        self._config = config
        self._store = store
        self._ingestion = ingestion
        self._filtering = filtering
        self._analysis = analysis
        self._reporter = reporter
        self._memory = memory

    def run(
        self, report_date_utc: date | None = None, run_id: str | None = None
    ) -> DailyReport:
        logger = logging.getLogger(__name__)
        report_date_utc = report_date_utc or date.today()
        run_id = run_id or f"run-{report_date_utc.isoformat()}-{uuid4().hex[:8]}"
        logger.info("Run started | run_id=%s | report_date=%s", run_id, report_date_utc)
        self._store.create_run(run_id)
        self._store.mark_run_started(run_id)
        current_stage: str | None = None

        try:
            current_stage = "fetch"
            self._store.mark_stage_started(run_id, "fetch")
            lookback_days = self._config.daily_lookback_days
            if not self._store.has_previous_runs(current_run_id=run_id):
                lookback_days = self._config.bootstrap_lookback_days

            since_utc = datetime.now(timezone.utc) - timedelta(days=lookback_days)
            logger.info(
                "Stage fetch started | lookback_days=%s | since_utc=%s",
                lookback_days,
                since_utc.isoformat(),
            )
            posts = self._ingestion.collect(since_utc=since_utc)
            self._store.save_source_health(run_id, self._ingestion.last_health)
            self._store.save_stage_records(
                run_id, "fetch", [(post.post_id, post) for post in posts]
            )
            self._store.mark_stage_finished(
                run_id,
                "fetch",
                status="success",
                record_count=len(posts),
            )
            logger.info("Stage fetch finished | posts=%s", len(posts))

            current_stage = "filter"
            self._store.mark_stage_started(run_id, "filter")
            logger.info("Stage filter started")
            filtered = self._filtering.filter(posts)
            self._store.save_stage_records(
                run_id,
                "filter",
                [(item.post_id, item) for item in filtered],
            )
            self._store.mark_stage_finished(
                run_id,
                "filter",
                status="success",
                record_count=len(filtered),
            )
            logger.info("Stage filter finished | decisions=%s", len(filtered))

            current_stage = "analyze"
            self._store.mark_stage_started(run_id, "analyze")
            logger.info("Stage analyze started")
            analysis_items = self._analysis.analyze(filtered)
            themes = self._analysis.themes(analysis_items)
            self._store.save_stage_records(
                run_id,
                "analyze",
                [(item.item_id, item) for item in analysis_items],
            )
            self._store.mark_stage_finished(
                run_id,
                "analyze",
                status="success",
                record_count=len(analysis_items),
            )
            logger.info(
                "Stage analyze finished | analysis_items=%s", len(analysis_items)
            )

            current_stage = "report"
            self._store.mark_stage_started(run_id, "report")
            logger.info("Stage report started")
            markdown = self._reporter.build(
                report_date_utc=report_date_utc,
                analysis_items=analysis_items,
                themes=themes,
            )
            self._store.save_report(
                run_id=run_id,
                report_date_utc=report_date_utc.isoformat(),
                markdown=markdown,
            )
            self._store.mark_stage_finished(
                run_id,
                "report",
                status="success",
                record_count=1,
            )
            logger.info("Stage report finished")

            current_stage = "memory"
            self._store.mark_stage_started(run_id, "memory")
            logger.info("Stage memory started")
            memory_result = self._memory.sync(
                report_date_utc=report_date_utc,
                analysis_items=analysis_items,
                markdown=markdown,
            )
            self._store.save_stage_records(
                run_id,
                "memory",
                [
                    (f"memory:{idx}", {"path": path})
                    for idx, path in enumerate(memory_result.written_files)
                ],
            )
            self._store.mark_stage_finished(
                run_id,
                "memory",
                status="success",
                record_count=len(memory_result.written_files),
            )
            if memory_result.warning:
                logger.warning("Stage memory warning | %s", memory_result.warning)
            logger.info(
                "Stage memory finished | files=%s", len(memory_result.written_files)
            )

            self._store.mark_run_finished(run_id, status="success")
            logger.info("Run finished successfully | run_id=%s", run_id)
            return DailyReport(
                run_id=run_id,
                report_date_utc=report_date_utc,
                analysis_items=analysis_items,
                themes=themes,
                markdown=markdown,
            )
        except Exception as exc:
            logger.exception("Run failed | run_id=%s | stage=%s", run_id, current_stage)
            if current_stage is not None:
                self._store.mark_stage_finished(
                    run_id,
                    current_stage,
                    status="failed",
                    record_count=0,
                    error=str(exc),
                )
            self._store.mark_run_finished(run_id, status="failed", error=str(exc))
            raise
