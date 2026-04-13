from __future__ import annotations

import argparse
import logging
from pathlib import Path

from ai_equity_discovery.analysis.service import AnalysisService
from ai_equity_discovery.core.config import AppConfig
from ai_equity_discovery.core.database import SQLiteStore
from ai_equity_discovery.core.env import load_env
from ai_equity_discovery.core.loaders import load_source_config
from ai_equity_discovery.extraction.service import ExtractionService
from ai_equity_discovery.filtering.service import FilteringService
from ai_equity_discovery.ingestion.deep_agent import OpenRouterDiscoveryAnnotator
from ai_equity_discovery.ingestion.providers import RedditAdapter, ScweetAdapter
from ai_equity_discovery.ingestion.service import IngestionService
from ai_equity_discovery.memory.obsidian import ObsidianMemorySync
from ai_equity_discovery.pipeline.daily import DailyPipeline
from ai_equity_discovery.reporting.markdown import MarkdownReporter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run AI Equity Discovery daily pipeline"
    )
    parser.add_argument(
        "--sources",
        default="config/sources.example.json",
        help="Path to sources JSON config",
    )
    parser.add_argument(
        "--db", default="data/discovery.sqlite", help="SQLite database path"
    )
    parser.add_argument(
        "--output", default="reports/daily.md", help="Output markdown path"
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional externally provided run id",
    )
    return parser.parse_args()


def main() -> int:
    load_env()
    args = parse_args()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    app_config = AppConfig.from_env()
    logger = logging.getLogger(__name__)
    logger.info(
        "Model routing | filter=%s | analysis=%s | reporting=%s",
        app_config.discovery_agent.model_discovery or app_config.discovery_agent.model,
        app_config.discovery_agent.model_analysis or app_config.discovery_agent.model,
        app_config.discovery_agent.model_reporting or app_config.discovery_agent.model,
    )

    source_cfg = load_source_config(args.sources)

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ingestion_service = IngestionService(
        adapters=[
            ScweetAdapter(accounts=source_cfg.x_accounts),
            RedditAdapter(subreddits=source_cfg.reddit_subreddits),
        ],
        annotator=OpenRouterDiscoveryAnnotator(
            app_config.discovery_agent,
            model=app_config.discovery_agent.model_discovery,
        ),
    )

    pipeline = DailyPipeline(
        config=AppConfig(
            x_accounts=source_cfg.x_accounts,
            reddit_subreddits=source_cfg.reddit_subreddits,
            bootstrap_lookback_days=app_config.bootstrap_lookback_days,
            daily_lookback_days=app_config.daily_lookback_days,
            discovery_agent=app_config.discovery_agent,
            memory=app_config.memory,
        ),
        store=SQLiteStore(db_path),
        ingestion=ingestion_service,
        filtering=FilteringService(),
        analysis=AnalysisService(extraction=ExtractionService()),
        reporter=MarkdownReporter(),
        memory=ObsidianMemorySync(app_config.memory),
    )

    report = pipeline.run(run_id=args.run_id)
    output_path.write_text(report.markdown, encoding="utf-8")

    print(f"Run completed: {report.run_id}")
    print(f"Analysis items: {len(report.analysis_items)}")
    print(f"Report: {output_path}")

    if ingestion_service.last_health:
        print("Ingestion source health:")
        for item in ingestion_service.last_health:
            status = "ok" if item.success else "error"
            detail = f"posts={item.post_count}, {item.elapsed_ms}ms"
            if item.error:
                detail = f"{detail}, error={item.error}"
            print(f"- {item.source_name}: {status} ({detail})")

    if ingestion_service.last_errors:
        print("Ingestion warnings:")
        for error in ingestion_service.last_errors:
            print(f"- {error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
