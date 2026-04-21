from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from ai_equity_discovery.analysis.service import AnalysisService
from ai_equity_discovery.core.accounts import (
    add_subreddit,
    add_x_account,
    load_watched_accounts,
    remove_subreddit,
    remove_x_account,
)
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

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
REPORTS_DIR = PROJECT_ROOT / "reports"
DEFAULT_DB = DATA_DIR / "discovery.sqlite"
DEFAULT_OUTPUT = REPORTS_DIR / "daily.md"


def _setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def _ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────────────────
# accounts subcommand
# ─────────────────────────────────────────────────────────────────────────────

def cmd_accounts(args: argparse.Namespace) -> int:
    accounts = load_watched_accounts()
    if args.account_action == "list":
        print(f"X accounts ({len(accounts.x_accounts)}):")
        for a in accounts.x_accounts:
            print(f"  @{a}")
        print(f"\nReddit subreddits ({len(accounts.reddit_subreddits)}):")
        for s in accounts.reddit_subreddits:
            print(f"  r/{s}")
        return 0

    elif args.account_action == "add":
        try:
            accounts = add_x_account(args.username)
            print(f"Added @{args.username.lstrip('@')} to watch list.")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    elif args.account_action == "remove":
        try:
            accounts = remove_x_account(args.username)
            print(f"Removed @{args.username.lstrip('@')} from watch list.")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    elif args.account_action == "add-subreddit":
        try:
            add_subreddit(args.subreddit)
            print(f"Added r/{args.subreddit} to watch list.")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    elif args.account_action == "remove-subreddit":
        try:
            remove_subreddit(args.subreddit)
            print(f"Removed r/{args.subreddit} from watch list.")
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        return 0

    return 0


# ─────────────────────────────────────────────────────────────────────────────
# query subcommand
# ─────────────────────────────────────────────────────────────────────────────

def cmd_query(args: argparse.Namespace) -> int:
    _setup_logging()
    load_env()
    db_path = Path(args.db or DEFAULT_DB)
    if not db_path.exists():
        print(f"No database found at {db_path}. Run 'run-research' first.", file=sys.stderr)
        return 1

    store = SQLiteStore(db_path)

    if args.query_action == "ticker":
        ticker = args.ticker.upper().strip()
        items = store.query_analysis_items(ticker=ticker, limit=args.limit)
        if not items:
            print(f"No analysis found for {ticker}.")
            return 0
        print(f"Analysis items for ${ticker} (last {len(items)} results):\n")
        for item in items:
            tickers = item.get("tickers", [])
            themes = item.get("themes", [])
            print(f"  Claim: {item.get('claim_summary', 'N/A')}")
            print(f"  Type: {item.get('claim_type', 'N/A')}")
            if tickers:
                print(f"  Tickers: {', '.join(tickers)}")
            if themes:
                print(f"  Themes: {', '.join(themes)}")
            questions = item.get("follow_up_questions", [])
            if questions:
                print(f"  Follow-up: {questions[0]}")
            print()
        return 0

    elif args.query_action == "theme":
        theme = args.theme.strip()
        items = store.query_analysis_items(theme=theme, limit=args.limit)
        if not items:
            print(f"No analysis found for theme '{theme}'.")
            return 0
        print(f"Analysis items for theme '{theme}' (last {len(items)} results):\n")
        for item in items:
            print(f"  Claim: {item.get('claim_summary', 'N/A')}")
            print(f"  Tickers: {', '.join(item.get('tickers', []))}")
            print()
        return 0

    elif args.query_action == "report":
        report = store.get_latest_report()
        if not report:
            print("No report found.")
            return 0
        print(f"# Latest Report ({report['report_date_utc']})\n")
        print(report["markdown"])
        return 0

    elif args.query_action == "runs":
        runs = store.list_runs(limit=args.limit)
        if not runs:
            print("No runs found.")
            return 0
        print(f"Recent runs:\n")
        for run in runs:
            status = run.get("status", "?")
            created = run.get("created_at_utc", "?")
            finished = run.get("finished_at_utc", "")
            run_id = run.get("run_id", "?")
            error = run.get("error", "")
            error_str = f" | ERROR: {error}" if error else ""
            print(f"  {run_id} | {status} | created={created} | finished={finished}{error_str}")
        return 0

    return 0


# ─────────────────────────────────────────────────────────────────────────────
# run-research (pipeline) subcommand
# ─────────────────────────────────────────────────────────────────────────────

def cmd_run(args: argparse.Namespace) -> int:
    _setup_logging()
    load_env()
    _ensure_dirs()
    args.db = args.db or DEFAULT_DB
    args.output = args.output or DEFAULT_OUTPUT

    app_config = AppConfig.from_env()
    logger = logging.getLogger(__name__)

    # Always read accounts from the dynamic registry
    watched = load_watched_accounts()

    logger.info(
        "Model routing | filter=%s | analysis=%s | reporting=%s",
        app_config.discovery_agent.model_discovery or app_config.discovery_agent.model,
        app_config.discovery_agent.model_analysis or app_config.discovery_agent.model,
        app_config.discovery_agent.model_reporting or app_config.discovery_agent.model,
    )

    # Build source config from watched accounts
    source_cfg = type("SourceConfig", (), {
        "x_accounts": watched.x_accounts,
        "reddit_subreddits": watched.reddit_subreddits,
    })()

    db_path = Path(args.db)
    output_path = Path(args.output)

    ingestion_service = IngestionService(
        adapters=[
            ScweetAdapter(accounts=source_cfg.x_accounts),
            RedditAdapter(subreddits=source_cfg.reddit_subreddits),
        ],
        annotator=OpenRouterDiscoveryAnnotator(
            app_config.discovery_agent,
            model=app_config.discovery_agent.model_resolution,
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


# ─────────────────────────────────────────────────────────────────────────────
# Argument parser
# ─────────────────────────────────────────────────────────────────────────────

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="ai-equity-discovery",
        description="AI Equity Discovery — investment research pipeline",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # accounts subcommand
    acct_parser = subparsers.add_parser(
        "accounts",
        help="Manage watched X accounts and subreddits",
    )
    acct_subparsers = acct_parser.add_subparsers(
        dest="account_action", required=True
    )

    list_parser = acct_subparsers.add_parser("list", help="List all watched accounts")
    list_parser.set_defaults(account_action="list")

    add_parser = acct_subparsers.add_parser(
        "add", help="Add a Twitter account to watch"
    )
    add_parser.add_argument("username", help="Twitter username (with or without @)")
    add_parser.set_defaults(account_action="add")

    rem_parser = acct_subparsers.add_parser(
        "remove", help="Remove a Twitter account from watch list"
    )
    rem_parser.add_argument("username", help="Twitter username")
    rem_parser.set_defaults(account_action="remove")

    add_sub_parser = acct_subparsers.add_parser(
        "add-subreddit", help="Add a subreddit to watch"
    )
    add_sub_parser.add_argument("subreddit", help="Subreddit name (with or without r/)")
    add_sub_parser.set_defaults(account_action="add-subreddit")

    rem_sub_parser = acct_subparsers.add_parser(
        "remove-subreddit", help="Remove a subreddit from watch list"
    )
    rem_sub_parser.add_argument("subreddit", help="Subreddit name")
    rem_sub_parser.set_defaults(account_action="remove-subreddit")

    # query subcommand
    query_parser = subparsers.add_parser(
        "query",
        help="Query existing research data",
    )
    query_parser.add_argument(
        "--db", default=None, help=f"SQLite database path (default: {DEFAULT_DB})"
    )
    query_subparsers = query_parser.add_subparsers(
        dest="query_action", required=True
    )

    query_ticker = query_subparsers.add_parser(
        "ticker", help="Query analysis by ticker"
    )
    query_ticker.add_argument("ticker", help="Ticker symbol (e.g. NVDA)")
    query_ticker.add_argument(
        "--limit", type=int, default=20, help="Max results (default: 20)"
    )
    query_ticker.set_defaults(query_action="ticker")

    query_theme = query_subparsers.add_parser(
        "theme", help="Query analysis by theme keyword"
    )
    query_theme.add_argument("theme", help="Theme keyword")
    query_theme.add_argument(
        "--limit", type=int, default=20, help="Max results (default: 20)"
    )
    query_theme.set_defaults(query_action="theme")

    query_report = query_subparsers.add_parser(
        "report", help="Show latest research report"
    )
    query_report.set_defaults(query_action="report")

    query_runs = query_subparsers.add_parser(
        "runs", help="Show recent pipeline runs"
    )
    query_runs.add_argument(
        "--limit", type=int, default=10, help="Max runs to show (default: 10)"
    )
    query_runs.set_defaults(query_action="runs")

    # run-research subcommand (pipeline runner)
    run_parser = subparsers.add_parser(
        "run-research",
        help="Run the full research pipeline (fetch → filter → analyze → report → memory)",
    )
    run_parser.add_argument(
        "--db", default=None, help=f"SQLite database path (default: {DEFAULT_DB})"
    )
    run_parser.add_argument(
        "--output", default=None, help=f"Output markdown path (default: {DEFAULT_OUTPUT})"
    )
    run_parser.add_argument(
        "--run-id", default=None, help="Optional externally provided run id",
    )
    run_parser.set_defaults(command="run")

    return parser.parse_args(argv)


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    cmd = args.command

    if cmd == "accounts":
        return cmd_accounts(args)
    elif cmd == "query":
        return cmd_query(args)
    elif cmd == "run":
        return cmd_run(args)

    parser = parse_args(["-h"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
