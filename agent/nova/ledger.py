"""Append-only Nova run ledger storage boundaries."""

from __future__ import annotations

import json
import sqlite3
import threading
from pathlib import Path
from typing import Protocol

from agent.nova.kernel import LedgerEntryKind, RunLedgerEntry, stable_json_dumps
from hermes_constants import get_hermes_home
from hermes_state import apply_wal_with_fallback


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS nova_ledger_entries (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    seq INTEGER NOT NULL CHECK (seq > 0),
    kind TEXT NOT NULL,
    actor TEXT NOT NULL,
    subject_ref TEXT,
    args_hash TEXT,
    evidence_bundle_id TEXT,
    policy_decision_id TEXT,
    payload_ref TEXT,
    parent_seq INTEGER,
    batch_id TEXT,
    batch_index INTEGER,
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at REAL NOT NULL,
    UNIQUE (run_id, seq)
);

CREATE TABLE IF NOT EXISTS nova_run_sequences (
    run_id TEXT PRIMARY KEY,
    next_seq INTEGER NOT NULL CHECK (next_seq > 0)
);

CREATE INDEX IF NOT EXISTS idx_nova_ledger_run_seq
    ON nova_ledger_entries(run_id, seq);
CREATE INDEX IF NOT EXISTS idx_nova_ledger_kind
    ON nova_ledger_entries(kind);
CREATE INDEX IF NOT EXISTS idx_nova_ledger_subject
    ON nova_ledger_entries(subject_ref);
"""


class AppendOnlyLedger(Protocol):
    """Minimal ledger interface used by disabled and shadow implementations."""

    def reserve_sequence(self, run_id: str, count: int = 1) -> range:
        """Reserve deterministic per-run sequence numbers."""

    def append(self, entry: RunLedgerEntry) -> RunLedgerEntry | None:
        """Append one immutable entry."""

    def append_event(
        self,
        run_id: str,
        kind: LedgerEntryKind | str,
        *,
        seq: int | None = None,
        actor: str = "kernel",
        subject_ref: str | None = None,
        args_hash: str | None = None,
        evidence_bundle_id: str | None = None,
        policy_decision_id: str | None = None,
        payload_ref: str | None = None,
        parent_seq: int | None = None,
        batch_id: str | None = None,
        batch_index: int | None = None,
        metadata: dict | None = None,
    ) -> RunLedgerEntry | None:
        """Build and append a ledger entry."""

    def get_entry(self, entry_id: str) -> RunLedgerEntry | None:
        """Return one entry by ID."""

    def iter_entries(
        self,
        run_id: str,
        *,
        kind: LedgerEntryKind | str | None = None,
        after_seq: int | None = None,
        limit: int | None = None,
    ) -> list[RunLedgerEntry]:
        """Return replay/debug entries ordered by sequence."""


def default_ledger_path() -> Path:
    """Return the profile-scoped default Nova ledger DB path."""

    return get_hermes_home() / "nova" / "kernel.db"


class DisabledLedger:
    """No-op implementation for disabled Nova mode."""

    def __init__(self) -> None:
        self._next_by_run: dict[str, int] = {}

    def reserve_sequence(self, run_id: str, count: int = 1) -> range:
        _validate_count(count)
        start = self._next_by_run.get(run_id, 1)
        self._next_by_run[run_id] = start + count
        return range(start, start + count)

    def append(self, entry: RunLedgerEntry) -> RunLedgerEntry | None:
        return entry

    def append_event(
        self,
        run_id: str,
        kind: LedgerEntryKind | str,
        *,
        seq: int | None = None,
        actor: str = "kernel",
        subject_ref: str | None = None,
        args_hash: str | None = None,
        evidence_bundle_id: str | None = None,
        policy_decision_id: str | None = None,
        payload_ref: str | None = None,
        parent_seq: int | None = None,
        batch_id: str | None = None,
        batch_index: int | None = None,
        metadata: dict | None = None,
    ) -> RunLedgerEntry:
        if seq is None:
            seq = self.reserve_sequence(run_id, 1).start
        return RunLedgerEntry(
            run_id=run_id,
            seq=seq,
            kind=LedgerEntryKind(kind),
            actor=actor,
            subject_ref=subject_ref,
            args_hash=args_hash,
            evidence_bundle_id=evidence_bundle_id,
            policy_decision_id=policy_decision_id,
            payload_ref=payload_ref,
            parent_seq=parent_seq,
            batch_id=batch_id,
            batch_index=batch_index,
            metadata=metadata or {},
        )

    def get_entry(self, entry_id: str) -> RunLedgerEntry | None:
        return None

    def iter_entries(
        self,
        run_id: str,
        *,
        kind: LedgerEntryKind | str | None = None,
        after_seq: int | None = None,
        limit: int | None = None,
    ) -> list[RunLedgerEntry]:
        return []


class SQLiteAppendOnlyLedger:
    """SQLite-backed append-only run ledger.

    The schema is deliberately separate from ``SessionDB`` for Phase 1. That
    keeps the storage boundary opt-in and allows disabled mode to avoid touching
    the existing Hermes runtime or session database.
    """

    def __init__(self, db_path: Path | str | None = None):
        self.db_path = Path(db_path) if db_path is not None else default_ledger_path()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            timeout=1.0,
            isolation_level=None,
        )
        self._conn.row_factory = sqlite3.Row
        apply_wal_with_fallback(self._conn, db_label="nova kernel.db")
        self._conn.executescript(SCHEMA_SQL)

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                except Exception:
                    pass
                self._conn.close()
                self._conn = None

    def reserve_sequence(self, run_id: str, count: int = 1) -> range:
        _validate_count(count)
        run_id = str(run_id)

        def _reserve(conn: sqlite3.Connection) -> range:
            conn.execute(
                "INSERT OR IGNORE INTO nova_run_sequences(run_id, next_seq) VALUES (?, 1)",
                (run_id,),
            )
            row = conn.execute(
                "SELECT next_seq FROM nova_run_sequences WHERE run_id = ?",
                (run_id,),
            ).fetchone()
            start = int(row["next_seq"])
            conn.execute(
                "UPDATE nova_run_sequences SET next_seq = ? WHERE run_id = ?",
                (start + count, run_id),
            )
            return range(start, start + count)

        return self._execute_write(_reserve)

    def append(self, entry: RunLedgerEntry) -> RunLedgerEntry:
        if not isinstance(entry, RunLedgerEntry):
            raise TypeError(f"entry must be RunLedgerEntry, got {type(entry).__name__}")

        def _append(conn: sqlite3.Connection) -> RunLedgerEntry:
            conn.execute(
                """
                INSERT INTO nova_ledger_entries(
                    id, run_id, seq, kind, actor, subject_ref, args_hash,
                    evidence_bundle_id, policy_decision_id, payload_ref,
                    parent_seq, batch_id, batch_index, metadata, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry.id,
                    entry.run_id,
                    entry.seq,
                    entry.kind.value,
                    entry.actor,
                    entry.subject_ref,
                    entry.args_hash,
                    entry.evidence_bundle_id,
                    entry.policy_decision_id,
                    entry.payload_ref,
                    entry.parent_seq,
                    entry.batch_id,
                    entry.batch_index,
                    stable_json_dumps(entry.metadata),
                    entry.created_at,
                ),
            )
            conn.execute(
                """
                INSERT INTO nova_run_sequences(run_id, next_seq)
                VALUES (?, ?)
                ON CONFLICT(run_id) DO UPDATE SET
                    next_seq = max(nova_run_sequences.next_seq, excluded.next_seq)
                """,
                (entry.run_id, entry.seq + 1),
            )
            return entry

        return self._execute_write(_append)

    def append_event(
        self,
        run_id: str,
        kind: LedgerEntryKind | str,
        *,
        seq: int | None = None,
        actor: str = "kernel",
        subject_ref: str | None = None,
        args_hash: str | None = None,
        evidence_bundle_id: str | None = None,
        policy_decision_id: str | None = None,
        payload_ref: str | None = None,
        parent_seq: int | None = None,
        batch_id: str | None = None,
        batch_index: int | None = None,
        metadata: dict | None = None,
    ) -> RunLedgerEntry:
        if seq is None:
            seq = self.reserve_sequence(run_id, 1).start
        return self.append(
            RunLedgerEntry(
                run_id=run_id,
                seq=seq,
                kind=LedgerEntryKind(kind),
                actor=actor,
                subject_ref=subject_ref,
                args_hash=args_hash,
                evidence_bundle_id=evidence_bundle_id,
                policy_decision_id=policy_decision_id,
                payload_ref=payload_ref,
                parent_seq=parent_seq,
                batch_id=batch_id,
                batch_index=batch_index,
                metadata=metadata or {},
            )
        )

    def get_entry(self, entry_id: str) -> RunLedgerEntry | None:
        row = self._conn.execute(
            "SELECT * FROM nova_ledger_entries WHERE id = ?",
            (str(entry_id),),
        ).fetchone()
        return _row_to_entry(row) if row is not None else None

    def iter_entries(
        self,
        run_id: str,
        *,
        kind: LedgerEntryKind | str | None = None,
        after_seq: int | None = None,
        limit: int | None = None,
    ) -> list[RunLedgerEntry]:
        clauses = ["run_id = ?"]
        params: list[object] = [str(run_id)]
        if kind is not None:
            clauses.append("kind = ?")
            params.append(LedgerEntryKind(kind).value)
        if after_seq is not None:
            clauses.append("seq > ?")
            params.append(int(after_seq))
        sql = (
            "SELECT * FROM nova_ledger_entries "
            f"WHERE {' AND '.join(clauses)} "
            "ORDER BY seq ASC"
        )
        if limit is not None:
            sql += " LIMIT ?"
            params.append(int(limit))
        return [_row_to_entry(row) for row in self._conn.execute(sql, params).fetchall()]

    def _execute_write(self, fn):
        if self._conn is None:
            raise sqlite3.ProgrammingError("ledger connection is closed")
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                result = fn(self._conn)
                self._conn.commit()
                return result
            except BaseException:
                try:
                    self._conn.rollback()
                except Exception:
                    pass
                raise


def _row_to_entry(row: sqlite3.Row) -> RunLedgerEntry:
    metadata = json.loads(row["metadata"] or "{}")
    return RunLedgerEntry(
        id=row["id"],
        run_id=row["run_id"],
        seq=row["seq"],
        kind=LedgerEntryKind(row["kind"]),
        actor=row["actor"],
        subject_ref=row["subject_ref"],
        args_hash=row["args_hash"],
        evidence_bundle_id=row["evidence_bundle_id"],
        policy_decision_id=row["policy_decision_id"],
        payload_ref=row["payload_ref"],
        parent_seq=row["parent_seq"],
        batch_id=row["batch_id"],
        batch_index=row["batch_index"],
        metadata=metadata,
        created_at=row["created_at"],
    )


def _validate_count(count: int) -> None:
    if int(count) < 1:
        raise ValueError("count must be positive")
