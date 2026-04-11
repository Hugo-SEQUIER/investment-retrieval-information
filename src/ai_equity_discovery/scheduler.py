from __future__ import annotations

import argparse
import subprocess
import sys
import time


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run AI Equity Discovery on a schedule"
    )
    parser.add_argument(
        "--interval-seconds", type=int, default=86400, help="Run interval in seconds"
    )
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument(
        "pipeline_args", nargs="*", help="Arguments passed to ai_equity_discovery CLI"
    )
    return parser.parse_args()


def run_pipeline(pipeline_args: list[str]) -> int:
    cmd = [sys.executable, "-m", "ai_equity_discovery", *pipeline_args]
    completed = subprocess.run(cmd, check=False)
    return int(completed.returncode)


def main() -> int:
    args = parse_args()
    while True:
        code = run_pipeline(args.pipeline_args)
        if args.once:
            return code
        if code != 0:
            print(f"Pipeline exited with code {code}; retrying at next interval")
        time.sleep(args.interval_seconds)


if __name__ == "__main__":
    raise SystemExit(main())
