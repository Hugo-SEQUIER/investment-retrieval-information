from __future__ import annotations

import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def new_run_id() -> str:
    now = datetime.now(timezone.utc).date().isoformat()
    return f"run-{now}-{uuid4().hex[:8]}"


def launch_pipeline_subprocess(run_id: str, db_path: Path) -> None:
    logs_dir = Path("data") / "run-logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    log_file = logs_dir / f"{run_id}.log"

    command = [
        sys.executable,
        "-m",
        "ai_equity_discovery",
        "--run-id",
        run_id,
        "--db",
        str(db_path),
    ]

    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    src_path = str(Path("src").resolve())
    if pythonpath:
        env["PYTHONPATH"] = f"{src_path}{os.pathsep}{pythonpath}"
    else:
        env["PYTHONPATH"] = src_path

    handle = log_file.open("a", encoding="utf-8")
    try:
        subprocess.Popen(
            command,
            stdout=handle,
            stderr=handle,
            cwd=str(Path.cwd()),
            env=env,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
    finally:
        handle.close()
