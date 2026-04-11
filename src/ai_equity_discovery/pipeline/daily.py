from __future__ import annotations

from datetime import date
from uuid import uuid4

from ai_equity_discovery.core.config import AppConfig
from ai_equity_discovery.core.database import SQLiteStore
from ai_equity_discovery.core.models import DailyReport
from ai_equity_discovery.enrichment.service import EnrichmentService
from ai_equity_discovery.extraction.service import ExtractionService
from ai_equity_discovery.ingestion.service import IngestionService
from ai_equity_discovery.ranking.service import RankingService
from ai_equity_discovery.reporting.markdown import MarkdownReporter
from ai_equity_discovery.resolution.service import ResolutionService


class DailyPipeline:
    def __init__(
        self,
        config: AppConfig,
        store: SQLiteStore,
        ingestion: IngestionService,
        extraction: ExtractionService,
        resolution: ResolutionService,
        enrichment: EnrichmentService,
        ranking: RankingService,
        reporter: MarkdownReporter,
    ) -> None:
        self._config = config
        self._store = store
        self._ingestion = ingestion
        self._extraction = extraction
        self._resolution = resolution
        self._enrichment = enrichment
        self._ranking = ranking
        self._reporter = reporter

    def run(
        self, report_date_utc: date | None = None, run_id: str | None = None
    ) -> DailyReport:
        report_date_utc = report_date_utc or date.today()
        run_id = run_id or f"run-{report_date_utc.isoformat()}-{uuid4().hex[:8]}"
        self._store.create_run(run_id)
        self._store.mark_run_started(run_id)
        current_stage: str | None = None

        try:
            current_stage = "discovery"
            self._store.mark_stage_started(run_id, "discovery")
            posts = self._ingestion.collect()
            self._store.save_source_health(run_id, self._ingestion.last_health)
            self._store.save_stage_records(
                run_id, "discovery", [(post.post_id, post) for post in posts]
            )
            self._store.mark_stage_finished(
                run_id,
                "discovery",
                status="success",
                record_count=len(posts),
            )

            current_stage = "extraction"
            self._store.mark_stage_started(run_id, "extraction")
            candidates = self._extraction.extract(posts)
            self._store.save_stage_records(
                run_id,
                "extraction",
                [(candidate.candidate_id, candidate) for candidate in candidates],
            )
            self._store.mark_stage_finished(
                run_id,
                "extraction",
                status="success",
                record_count=len(candidates),
            )

            current_stage = "resolution"
            self._store.mark_stage_started(run_id, "resolution")
            resolved = self._resolution.resolve(candidates)
            self._store.save_stage_records(
                run_id,
                "resolution",
                [(item.resolution_id, item) for item in resolved],
            )
            self._store.mark_stage_finished(
                run_id,
                "resolution",
                status="success",
                record_count=len(resolved),
            )

            current_stage = "enrichment"
            self._store.mark_stage_started(run_id, "enrichment")
            enriched = self._enrichment.enrich(resolved)
            self._store.save_stage_records(
                run_id,
                "enrichment",
                [(item.enrichment_id, item) for item in enriched],
            )
            self._store.mark_stage_finished(
                run_id,
                "enrichment",
                status="success",
                record_count=len(enriched),
            )

            current_stage = "ranking"
            self._store.mark_stage_started(run_id, "ranking")
            ranked, themes = self._ranking.rank(posts, candidates, resolved, enriched)
            top_ideas = ranked[: self._config.top_n]
            self._store.save_stage_records(
                run_id,
                "ranking",
                [(item.canonical_id, item) for item in top_ideas],
            )
            self._store.mark_stage_finished(
                run_id,
                "ranking",
                status="success",
                record_count=len(top_ideas),
            )

            current_stage = "reporting"
            self._store.mark_stage_started(run_id, "reporting")
            markdown = self._reporter.build(
                report_date_utc=report_date_utc, top_ideas=top_ideas, themes=themes
            )
            self._store.save_report(
                run_id=run_id,
                report_date_utc=report_date_utc.isoformat(),
                markdown=markdown,
            )
            self._store.mark_stage_finished(
                run_id,
                "reporting",
                status="success",
                record_count=1,
            )

            self._store.mark_run_finished(run_id, status="success")
            return DailyReport(
                run_id=run_id,
                report_date_utc=report_date_utc,
                top_ideas=top_ideas,
                themes=themes,
                markdown=markdown,
            )
        except Exception as exc:
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
