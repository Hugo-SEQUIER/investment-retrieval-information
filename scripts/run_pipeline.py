#!/usr/bin/env python3
"""
Convenience wrapper to run the AI Equity Discovery pipeline.

Usage:
    python scripts/run_pipeline.py [--db data/discovery.sqlite] [--output reports/daily.md]

Environment: reads from .env at project root.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure project src/ is on sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

if __name__ == "__main__":
    from ai_equity_discovery.cli import main
    raise SystemExit(main())
