from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ai_equity_discovery.core.serialization import to_jsonable


class SQLiteStore:
    def __init__(self, path: str | Path) -> None:
        self._path = str(path)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        conn = self._connect()
        try:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    created_at_utc TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'queued',
                    started_at_utc TEXT,
                    finished_at_utc TEXT,
                    error TEXT
                );

                CREATE TABLE IF NOT EXISTS stage_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    stage_name TEXT NOT NULL,
                    record_key TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    created_at_utc TEXT NOT NULL,
                    UNIQUE(run_id, stage_name, record_key)
                );

                CREATE TABLE IF NOT EXISTS reports (
                    run_id TEXT PRIMARY KEY,
                    report_date_utc TEXT NOT NULL,
                    markdown TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS source_health (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    source_name TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    post_count INTEGER NOT NULL,
                    elapsed_ms INTEGER NOT NULL,
                    error TEXT,
                    created_at_utc TEXT NOT NULL,
                    UNIQUE(run_id, source_name)
                );

                CREATE TABLE IF NOT EXISTS stage_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT NOT NULL,
                    stage_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at_utc TEXT,
                    finished_at_utc TEXT,
                    error TEXT,
                    record_count INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(run_id, stage_name)
                );
                """
            )
            self._ensure_runs_columns(conn)
            conn.commit()
        finally:
            conn.close()

    def _ensure_runs_columns(self, conn: sqlite3.Connection) -> None:
        existing = {
            row[1] for row in conn.execute("PRAGMA table_info(runs)").fetchall()
        }
        if "status" not in existing:
            conn.execute(
                "ALTER TABLE runs ADD COLUMN status TEXT NOT NULL DEFAULT 'queued'"
            )
        if "started_at_utc" not in existing:
            conn.execute("ALTER TABLE runs ADD COLUMN started_at_utc TEXT")
        if "finished_at_utc" not in existing:
            conn.execute("ALTER TABLE runs ADD COLUMN finished_at_utc TEXT")
        if "error" not in existing:
            conn.execute("ALTER TABLE runs ADD COLUMN error TEXT")

    def create_run(self, run_id: str, status: str = "queued") -> None:
        created_at_utc = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO runs(run_id, created_at_utc, status)
                VALUES (?, ?, ?)
                """,
                (run_id, created_at_utc, status),
            )
            conn.commit()
        finally:
            conn.close()

    def mark_run_started(self, run_id: str) -> None:
        started_at_utc = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE runs
                SET status = 'running',
                    started_at_utc = COALESCE(started_at_utc, ?),
                    error = NULL
                WHERE run_id = ?
                """,
                (started_at_utc, run_id),
            )
            conn.commit()
        finally:
            conn.close()

    def mark_run_finished(
        self, run_id: str, status: str, error: str | None = None
    ) -> None:
        finished_at_utc = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.execute(
                """
                UPDATE runs
                SET status = ?,
                    finished_at_utc = ?,
                    error = ?
                WHERE run_id = ?
                """,
                (status, finished_at_utc, error, run_id),
            )
            conn.commit()
        finally:
            conn.close()

    def mark_stage_started(self, run_id: str, stage_name: str) -> None:
        started_at_utc = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO stage_status(
                    run_id,
                    stage_name,
                    status,
                    started_at_utc,
                    finished_at_utc,
                    error,
                    record_count
                ) VALUES (
                    ?,
                    ?,
                    'running',
                    COALESCE((SELECT started_at_utc FROM stage_status WHERE run_id = ? AND stage_name = ?), ?),
                    NULL,
                    NULL,
                    0
                )
                """,
                (run_id, stage_name, run_id, stage_name, started_at_utc),
            )
            conn.commit()
        finally:
            conn.close()

    def mark_stage_finished(
        self,
        run_id: str,
        stage_name: str,
        status: str,
        record_count: int = 0,
        error: str | None = None,
    ) -> None:
        finished_at_utc = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.execute(
                """
                INSERT OR REPLACE INTO stage_status(
                    run_id,
                    stage_name,
                    status,
                    started_at_utc,
                    finished_at_utc,
                    error,
                    record_count
                ) VALUES (
                    ?,
                    ?,
                    ?,
                    COALESCE((SELECT started_at_utc FROM stage_status WHERE run_id = ? AND stage_name = ?), ?),
                    ?,
                    ?,
                    ?
                )
                """,
                (
                    run_id,
                    stage_name,
                    status,
                    run_id,
                    stage_name,
                    finished_at_utc,
                    finished_at_utc,
                    error,
                    record_count,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def save_stage_records(
        self, run_id: str, stage_name: str, records: list[tuple[str, Any]]
    ) -> None:
        created_at_utc = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.executemany(
                """
                INSERT OR REPLACE INTO stage_records(run_id, stage_name, record_key, payload_json, created_at_utc)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        stage_name,
                        record_key,
                        json.dumps(to_jsonable(payload), sort_keys=True),
                        created_at_utc,
                    )
                    for record_key, payload in records
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def save_report(self, run_id: str, report_date_utc: str, markdown: str) -> None:
        conn = self._connect()
        try:
            conn.execute(
                "INSERT OR REPLACE INTO reports(run_id, report_date_utc, markdown) VALUES (?, ?, ?)",
                (run_id, report_date_utc, markdown),
            )
            conn.commit()
        finally:
            conn.close()

    def save_source_health(self, run_id: str, health_records: list[Any]) -> None:
        created_at_utc = datetime.now(timezone.utc).isoformat()
        conn = self._connect()
        try:
            conn.executemany(
                """
                INSERT OR REPLACE INTO source_health(
                    run_id,
                    source_name,
                    success,
                    post_count,
                    elapsed_ms,
                    error,
                    created_at_utc
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        run_id,
                        str(getattr(record, "source_name")),
                        1 if bool(getattr(record, "success")) else 0,
                        int(getattr(record, "post_count", 0)),
                        int(getattr(record, "elapsed_ms", 0)),
                        getattr(record, "error", None),
                        created_at_utc,
                    )
                    for record in health_records
                ],
            )
            conn.commit()
        finally:
            conn.close()

    def has_active_run(self) -> bool:
        conn = self._connect()
        try:
            row = conn.execute(
                "SELECT 1 FROM runs WHERE status IN ('queued', 'running') LIMIT 1"
            ).fetchone()
            return row is not None
        finally:
            conn.close()

    def list_runs(self, limit: int = 20) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT run_id, created_at_utc, status, started_at_utc, finished_at_utc, error
                FROM runs
                ORDER BY created_at_utc DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                """
                SELECT run_id, created_at_utc, status, started_at_utc, finished_at_utc, error
                FROM runs
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def get_stage_status(self, run_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT run_id, stage_name, status, started_at_utc, finished_at_utc, error, record_count
                FROM stage_status
                WHERE run_id = ?
                ORDER BY id ASC
                """,
                (run_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_source_health(self, run_id: str) -> list[dict[str, Any]]:
        conn = self._connect()
        try:
            rows = conn.execute(
                """
                SELECT source_name, success, post_count, elapsed_ms, error, created_at_utc
                FROM source_health
                WHERE run_id = ?
                ORDER BY source_name ASC
                """,
                (run_id,),
            ).fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_report(self, run_id: str) -> dict[str, Any] | None:
        conn = self._connect()
        try:
            row = conn.execute(
                """
                SELECT run_id, report_date_utc, markdown
                FROM reports
                WHERE run_id = ?
                """,
                (run_id,),
            ).fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
