from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from ai_equity_discovery.core.config import AppConfig
from ai_equity_discovery.core.database import SQLiteStore
from ai_equity_discovery.core.loaders import (
    load_company_registry,
    load_enrichment_facts,
    load_enrichment_source_urls,
    load_fx_rates,
    load_source_config,
)
from ai_equity_discovery.enrichment.service import (
    CurrencyNormalizer,
    EnrichmentService,
    InMemoryEnrichmentProvider,
    LayeredEnrichmentProvider,
)
from ai_equity_discovery.enrichment.web_provider import WebResearchEnrichmentProvider
from ai_equity_discovery.extraction.service import ExtractionService
from ai_equity_discovery.ingestion.providers import RedditAdapter, TwscrapeAdapter
from ai_equity_discovery.ingestion.service import IngestionService
from ai_equity_discovery.pipeline.daily import DailyPipeline
from ai_equity_discovery.ranking.service import RankingService
from ai_equity_discovery.reporting.markdown import MarkdownReporter
from ai_equity_discovery.resolution.registry import CompanyRegistry
from ai_equity_discovery.resolution.service import ResolutionService


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
        "--companies",
        default="config/companies.example.json",
        help="Path to company registry JSON",
    )
    parser.add_argument(
        "--facts",
        default="config/enrichment.example.json",
        help="Path to enrichment facts JSON",
    )
    parser.add_argument(
        "--db", default="data/discovery.sqlite", help="SQLite database path"
    )
    parser.add_argument(
        "--output", default="reports/daily.md", help="Output markdown path"
    )
    parser.add_argument(
        "--top-n", type=int, default=10, help="Top ideas to keep in report"
    )
    parser.add_argument(
        "--fx",
        default="config/fx.example.json",
        help="Path to FX rates JSON",
    )
    parser.add_argument(
        "--enrichment-mode",
        choices=["fixture", "layered-web"],
        default="fixture",
        help="Enrichment provider mode",
    )
    parser.add_argument(
        "--run-id",
        default=None,
        help="Optional externally provided run id",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    source_cfg = load_source_config(args.sources)
    registry = CompanyRegistry(load_company_registry(args.companies))
    facts = load_enrichment_facts(args.facts)
    source_urls_by_id = load_enrichment_source_urls(args.facts)
    fx_rates = load_fx_rates(args.fx)

    db_path = Path(args.db)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ingestion_service = IngestionService(
        adapters=[
            TwscrapeAdapter(accounts=source_cfg.x_accounts),
            RedditAdapter(subreddits=source_cfg.reddit_subreddits),
        ]
    )

    enrichment_provider = InMemoryEnrichmentProvider(facts_by_id=facts)
    if args.enrichment_mode == "layered-web":
        enrichment_provider = LayeredEnrichmentProvider(
            primary=enrichment_provider,
            fallback=WebResearchEnrichmentProvider(source_urls_by_id=source_urls_by_id),
        )

    pipeline = DailyPipeline(
        config=AppConfig(
            x_accounts=source_cfg.x_accounts,
            reddit_subreddits=source_cfg.reddit_subreddits,
            top_n=args.top_n,
        ),
        store=SQLiteStore(db_path),
        ingestion=ingestion_service,
        extraction=ExtractionService(),
        resolution=ResolutionService(registry),
        enrichment=EnrichmentService(
            provider=enrichment_provider,
            normalizer=CurrencyNormalizer(
                fx_rates_to_usd=fx_rates, fx_date=date.today()
            ),
        ),
        ranking=RankingService(),
        reporter=MarkdownReporter(),
    )

    report = pipeline.run(run_id=args.run_id)
    output_path.write_text(report.markdown, encoding="utf-8")

    print(f"Run completed: {report.run_id}")
    print(f"Top ideas: {len(report.top_ideas)}")
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
