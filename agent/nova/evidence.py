"""Nova evidence capture and storage helpers.

This module is intentionally opt-in. The default recorder is disabled and does
not write profile state. Shadow mode can record compact evidence references
beside the existing Hermes runtime without changing tool behavior.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol

from agent.nova.kernel import (
    EvidenceBundle,
    EvidenceRef,
    EvidenceRefKind,
    KernelMode,
    LedgerEntryKind,
    ToolLedgerBatchPlan,
    stable_hash,
    stable_json_dumps,
    tool_args_hash,
)
from agent.nova.ledger import (
    AppendOnlyLedger,
    DisabledLedger,
    SQLiteAppendOnlyLedger,
    default_ledger_path,
)
from hermes_state import apply_wal_with_fallback


EVIDENCE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS nova_evidence_bundles (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL,
    metadata TEXT NOT NULL DEFAULT '{}',
    created_at REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS nova_evidence_refs (
    bundle_id TEXT NOT NULL REFERENCES nova_evidence_bundles(id),
    ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
    kind TEXT NOT NULL,
    ref TEXT NOT NULL,
    digest TEXT,
    metadata TEXT NOT NULL DEFAULT '{}',
    PRIMARY KEY (bundle_id, ordinal)
);

CREATE INDEX IF NOT EXISTS idx_nova_evidence_bundle_run
    ON nova_evidence_bundles(run_id);
CREATE INDEX IF NOT EXISTS idx_nova_evidence_refs_kind_ref
    ON nova_evidence_refs(kind, ref);
"""


class MissingEvidenceError(ValueError):
    """Raised when a trusted transition lacks required evidence refs."""


class EvidenceStore(Protocol):
    """Minimal storage boundary for compact evidence bundles."""

    def put_bundle(self, bundle: EvidenceBundle) -> EvidenceBundle | None:
        """Persist one evidence bundle."""

    def get_bundle(self, bundle_id: str) -> EvidenceBundle | None:
        """Return one evidence bundle by ID."""

    def iter_bundles(self, run_id: str, *, limit: int | None = None) -> list[EvidenceBundle]:
        """Return bundles for a run ordered by creation time."""


@dataclass(frozen=True)
class ToolCallEvidence:
    """Compact record of a model-requested tool call."""

    tool_call_id: str
    tool_name: str
    args: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "tool_call_id", str(self.tool_call_id))
        object.__setattr__(self, "tool_name", str(self.tool_name))
        if not isinstance(self.args, Mapping):
            object.__setattr__(self, "args", {})
        else:
            object.__setattr__(self, "args", dict(self.args))


@dataclass(frozen=True)
class ToolResultEvidence:
    """Compact record of a completed or blocked tool result."""

    tool_call_id: str
    tool_name: str
    args: Mapping[str, Any] = field(default_factory=dict)
    result: Any = ""
    duration_seconds: float | None = None
    is_error: bool = False
    blocked: bool = False
    message_index: int | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "tool_call_id", str(self.tool_call_id))
        object.__setattr__(self, "tool_name", str(self.tool_name))
        if not isinstance(self.args, Mapping):
            object.__setattr__(self, "args", {})
        else:
            object.__setattr__(self, "args", dict(self.args))
        if self.duration_seconds is not None:
            object.__setattr__(self, "duration_seconds", float(self.duration_seconds))
        if self.message_index is not None:
            object.__setattr__(self, "message_index", int(self.message_index))


class DisabledEvidenceStore:
    """No-op store for disabled Nova mode."""

    def put_bundle(self, bundle: EvidenceBundle) -> EvidenceBundle:
        return bundle

    def get_bundle(self, bundle_id: str) -> EvidenceBundle | None:
        return None

    def iter_bundles(self, run_id: str, *, limit: int | None = None) -> list[EvidenceBundle]:
        return []

    def close(self) -> None:
        return None


class SQLiteEvidenceStore:
    """SQLite-backed compact evidence storage.

    The table stores evidence pointers, digests, and bounded metadata only.
    Raw tool output and message bodies are never stored here.
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
        self._conn.executescript(EVIDENCE_SCHEMA_SQL)

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                except Exception:
                    pass
                self._conn.close()
                self._conn = None

    def put_bundle(self, bundle: EvidenceBundle) -> EvidenceBundle:
        if not isinstance(bundle, EvidenceBundle):
            raise TypeError(f"bundle must be EvidenceBundle, got {type(bundle).__name__}")

        def _put(conn: sqlite3.Connection) -> EvidenceBundle:
            conn.execute(
                """
                INSERT INTO nova_evidence_bundles(id, run_id, metadata, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    bundle.id,
                    bundle.run_id,
                    stable_json_dumps(bundle.metadata),
                    bundle.created_at,
                ),
            )
            for ordinal, ref in enumerate(bundle.refs):
                conn.execute(
                    """
                    INSERT INTO nova_evidence_refs(
                        bundle_id, ordinal, kind, ref, digest, metadata
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bundle.id,
                        ordinal,
                        ref.kind.value,
                        ref.ref,
                        ref.digest,
                        stable_json_dumps(ref.metadata),
                    ),
                )
            return bundle

        return self._execute_write(_put)

    def get_bundle(self, bundle_id: str) -> EvidenceBundle | None:
        row = self._conn.execute(
            "SELECT * FROM nova_evidence_bundles WHERE id = ?",
            (str(bundle_id),),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_bundle(row)

    def iter_bundles(self, run_id: str, *, limit: int | None = None) -> list[EvidenceBundle]:
        sql = (
            "SELECT * FROM nova_evidence_bundles "
            "WHERE run_id = ? ORDER BY created_at ASC, id ASC"
        )
        params: list[object] = [str(run_id)]
        if limit is not None:
            sql += " LIMIT ?"
            params.append(int(limit))
        return [self._row_to_bundle(row) for row in self._conn.execute(sql, params).fetchall()]

    def _row_to_bundle(self, row: sqlite3.Row) -> EvidenceBundle:
        ref_rows = self._conn.execute(
            "SELECT * FROM nova_evidence_refs WHERE bundle_id = ? ORDER BY ordinal ASC",
            (row["id"],),
        ).fetchall()
        grouped: dict[EvidenceRefKind, list[EvidenceRef]] = {kind: [] for kind in EvidenceRefKind}
        for ref_row in ref_rows:
            kind = EvidenceRefKind(ref_row["kind"])
            grouped.setdefault(kind, []).append(
                EvidenceRef(
                    kind=kind,
                    ref=ref_row["ref"],
                    digest=ref_row["digest"],
                    metadata=json.loads(ref_row["metadata"] or "{}"),
                )
            )
        return EvidenceBundle(
            id=row["id"],
            run_id=row["run_id"],
            message_refs=tuple(grouped.get(EvidenceRefKind.MESSAGE, ())),
            file_refs=tuple(grouped.get(EvidenceRefKind.FILE, ())),
            command_refs=tuple(grouped.get(EvidenceRefKind.COMMAND, ())),
            tool_result_refs=tuple(grouped.get(EvidenceRefKind.TOOL_RESULT, ())),
            check_refs=tuple(grouped.get(EvidenceRefKind.CHECK, ())),
            retrieval_refs=tuple(grouped.get(EvidenceRefKind.RETRIEVAL, ())),
            approval_refs=tuple(grouped.get(EvidenceRefKind.APPROVAL, ())),
            metadata=json.loads(row["metadata"] or "{}"),
            created_at=row["created_at"],
        )

    def _execute_write(self, fn):
        if self._conn is None:
            raise sqlite3.ProgrammingError("evidence store connection is closed")
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


class NovaRecorder:
    """Opt-in recorder that ties compact evidence to ledger entries."""

    def __init__(
        self,
        *,
        mode: KernelMode | str = KernelMode.DISABLED,
        ledger: AppendOnlyLedger | None = None,
        evidence_store: EvidenceStore | None = None,
    ):
        self.mode = KernelMode(mode)
        self.enabled = self.mode is KernelMode.SHADOW
        self.ledger = ledger if ledger is not None else DisabledLedger()
        self.evidence_store = evidence_store if evidence_store is not None else DisabledEvidenceStore()
        self._finished_runs: set[str] = set()

    @classmethod
    def disabled(cls) -> "NovaRecorder":
        return cls(mode=KernelMode.DISABLED)

    @classmethod
    def shadow(cls, db_path: Path | str | None = None) -> "NovaRecorder":
        return cls(
            mode=KernelMode.SHADOW,
            ledger=SQLiteAppendOnlyLedger(db_path),
            evidence_store=SQLiteEvidenceStore(db_path),
        )

    def close(self) -> None:
        for resource in (self.evidence_store, self.ledger):
            close = getattr(resource, "close", None)
            if callable(close):
                try:
                    close()
                except Exception:
                    pass

    def record_run_start(
        self,
        *,
        run_id: str,
        session_id: str | None = None,
        user_message: Any = "",
        message_index: int | None = None,
        task_id: str | None = None,
    ) -> EvidenceBundle | None:
        if not self.enabled:
            return None
        ref = build_message_evidence_ref(
            session_id=session_id,
            role="user",
            message_index=message_index,
            content=user_message,
        )
        bundle = EvidenceBundle(
            run_id=str(run_id),
            message_refs=(ref,),
            metadata={
                "capture": "run_start",
                "session_id": session_id or "",
                "task_id": task_id or "",
            },
        )
        self.evidence_store.put_bundle(bundle)
        self.ledger.append_event(
            str(run_id),
            LedgerEntryKind.RUN_STARTED,
            actor="agent",
            subject_ref=f"session:{session_id}" if session_id else None,
            evidence_bundle_id=bundle.id,
            metadata={
                "session_id": session_id or "",
                "task_id": task_id or "",
                "message_index": message_index,
            },
        )
        return bundle

    def record_run_end(
        self,
        *,
        run_id: str,
        session_id: str | None = None,
        final_response: Any = "",
        completed: bool = False,
        interrupted: bool = False,
        exit_reason: str = "",
        api_calls: int | None = None,
        message_index: int | None = None,
    ) -> EvidenceBundle | None:
        if not self.enabled:
            return None
        run_id = str(run_id)
        if run_id in self._finished_runs:
            return None
        self._finished_runs.add(run_id)
        message_refs: tuple[EvidenceRef, ...] = ()
        if final_response:
            message_refs = (
                build_message_evidence_ref(
                    session_id=session_id,
                    role="assistant",
                    message_index=message_index,
                    content=final_response,
                ),
            )
        bundle = EvidenceBundle(
            run_id=run_id,
            message_refs=message_refs,
            metadata={
                "capture": "run_end",
                "session_id": session_id or "",
                "completed": bool(completed),
                "interrupted": bool(interrupted),
                "exit_reason": exit_reason,
                "api_calls": api_calls,
            },
        )
        self.evidence_store.put_bundle(bundle)
        end_entry = self.ledger.append_event(
            run_id,
            LedgerEntryKind.RUN_ENDED,
            actor="agent",
            subject_ref=f"session:{session_id}" if session_id else None,
            evidence_bundle_id=bundle.id,
            metadata={
                "completed": bool(completed),
                "interrupted": bool(interrupted),
                "exit_reason": exit_reason,
                "api_calls": api_calls,
            },
        )
        self.ledger.append_event(
            run_id,
            LedgerEntryKind.OUTCOME,
            actor="agent",
            subject_ref=f"session:{session_id}" if session_id else None,
            parent_seq=end_entry.seq if end_entry is not None else None,
            evidence_bundle_id=bundle.id,
            payload_ref=f"outcome:{run_id}",
            metadata={
                "completed": bool(completed),
                "interrupted": bool(interrupted),
                "response_digest": compact_content_digest(final_response) if final_response else None,
            },
        )
        return bundle

    def record_tool_call_batch(
        self,
        *,
        run_id: str,
        session_id: str | None = None,
        api_call_count: int | None = None,
        calls: Iterable[ToolCallEvidence],
    ) -> ToolLedgerBatchPlan | None:
        calls = tuple(calls)
        if not self.enabled or not calls:
            return None
        reserved = self.ledger.reserve_sequence(str(run_id), count=len(calls) * 2)
        plan = ToolLedgerBatchPlan.from_tool_call_ids(
            str(run_id),
            [call.tool_call_id for call in calls],
            first_seq=reserved.start,
        )
        for call in calls:
            slot = plan.slot_for(call.tool_call_id)
            self.ledger.append_event(
                str(run_id),
                LedgerEntryKind.TOOL_CALL,
                seq=slot.call_seq,
                actor="assistant",
                subject_ref=call.tool_call_id,
                args_hash=tool_args_hash(call.args),
                batch_id=slot.batch_id,
                batch_index=slot.batch_index,
                metadata={
                    "session_id": session_id or "",
                    "api_call_count": api_call_count,
                    "tool_name": call.tool_name,
                    "args_keys": sorted(str(key) for key in call.args.keys()),
                },
            )
        return plan

    def record_tool_result(
        self,
        *,
        run_id: str,
        session_id: str | None = None,
        plan: ToolLedgerBatchPlan | None,
        result: ToolResultEvidence,
    ) -> EvidenceBundle | None:
        if not self.enabled or plan is None:
            return None
        slot = plan.slot_for(result.tool_call_id)
        ref = build_tool_result_evidence_ref(
            session_id=session_id,
            tool_call_id=result.tool_call_id,
            tool_name=result.tool_name,
            result=result.result,
            message_index=result.message_index,
        )
        bundle = EvidenceBundle(
            run_id=str(run_id),
            tool_result_refs=(ref,),
            metadata={
                "capture": "tool_result",
                "session_id": session_id or "",
                "tool_name": result.tool_name,
                "tool_call_id": result.tool_call_id,
                "blocked": bool(result.blocked),
                "is_error": bool(result.is_error),
                "duration_seconds": result.duration_seconds,
                "message_index": result.message_index,
            },
        )
        self.evidence_store.put_bundle(bundle)
        self.ledger.append_event(
            str(run_id),
            LedgerEntryKind.TOOL_RESULT,
            seq=slot.result_seq,
            actor="tool",
            subject_ref=result.tool_call_id,
            args_hash=tool_args_hash(result.args),
            evidence_bundle_id=bundle.id,
            parent_seq=slot.call_seq,
            batch_id=slot.batch_id,
            batch_index=slot.batch_index,
            metadata={
                "session_id": session_id or "",
                "tool_name": result.tool_name,
                "blocked": bool(result.blocked),
                "is_error": bool(result.is_error),
                "duration_seconds": result.duration_seconds,
                "message_index": result.message_index,
            },
        )
        return bundle


def build_message_evidence_ref(
    *,
    session_id: str | None,
    role: str,
    content: Any,
    message_index: int | None = None,
    message_id: int | str | None = None,
) -> EvidenceRef:
    return EvidenceRef(
        EvidenceRefKind.MESSAGE,
        _message_ref(session_id=session_id, message_id=message_id, message_index=message_index),
        digest=compact_content_digest(content),
        metadata={
            "role": role,
            "session_id": session_id or "",
            "message_id": message_id,
            "message_index": message_index,
            "content_shape": _content_shape(content),
            "content_size": _content_size(content),
        },
    )


def build_tool_result_evidence_ref(
    *,
    session_id: str | None,
    tool_call_id: str,
    tool_name: str,
    result: Any,
    message_index: int | None = None,
) -> EvidenceRef:
    return EvidenceRef(
        EvidenceRefKind.TOOL_RESULT,
        f"session:{session_id or 'unknown'}:tool_result:{tool_call_id}",
        digest=compact_content_digest(result),
        metadata={
            "session_id": session_id or "",
            "tool_call_id": str(tool_call_id),
            "tool_name": str(tool_name),
            "message_index": message_index,
            "content_shape": _content_shape(result),
            "content_size": _content_size(result),
        },
    )


def require_evidence_refs(
    bundle: EvidenceBundle | None,
    required_kinds: Iterable[EvidenceRefKind | str],
) -> EvidenceBundle:
    """Fail closed unless the bundle contains all required evidence kinds."""

    required = tuple(EvidenceRefKind(kind) for kind in required_kinds)
    if bundle is None:
        raise MissingEvidenceError("missing evidence bundle")
    if not required:
        if not bundle.refs:
            raise MissingEvidenceError(f"evidence bundle {bundle.id} has no refs")
        return bundle
    present = {ref.kind for ref in bundle.refs}
    missing = [kind.value for kind in required if kind not in present]
    if missing:
        raise MissingEvidenceError(
            f"evidence bundle {bundle.id} missing required refs: {', '.join(missing)}"
        )
    return bundle


def compact_content_digest(content: Any) -> str:
    """Hash redacted normalized content without storing the raw payload."""

    normalized = _normalize_content_for_digest(content)
    try:
        from agent.redact import redact_sensitive_text
        if isinstance(normalized, str):
            normalized = redact_sensitive_text(normalized, force=True)
        else:
            normalized = _redact_jsonable(normalized, redact_sensitive_text)
    except Exception:
        pass
    return stable_hash(normalized)


def _message_ref(
    *,
    session_id: str | None,
    message_id: int | str | None = None,
    message_index: int | None = None,
) -> str:
    base = f"session:{session_id or 'unknown'}"
    if message_id is not None:
        return f"{base}:message:{message_id}"
    if message_index is not None:
        return f"{base}:message_index:{message_index}"
    return f"{base}:message:unknown"


def _normalize_content_for_digest(content: Any) -> Any:
    if isinstance(content, bytes):
        return {"type": "bytes", "size": len(content)}
    if isinstance(content, str):
        return content
    if isinstance(content, Mapping):
        content_type = str(content.get("type", "")).lower()
        if content_type in {"image", "image_url", "input_image"}:
            return {"type": content_type or "image", "omitted": True}
        return {str(k): _normalize_content_for_digest(v) for k, v in content.items()}
    if isinstance(content, (list, tuple)):
        return [_normalize_content_for_digest(item) for item in content]
    return content


def _redact_jsonable(value: Any, redact_fn) -> Any:
    if isinstance(value, str):
        return redact_fn(value, force=True)
    if isinstance(value, Mapping):
        return {str(k): _redact_jsonable(v, redact_fn) for k, v in value.items()}
    if isinstance(value, list):
        return [_redact_jsonable(item, redact_fn) for item in value]
    return value


def _content_shape(content: Any) -> str:
    if isinstance(content, str):
        return "text"
    if isinstance(content, bytes):
        return "bytes"
    if isinstance(content, list):
        return "list"
    if isinstance(content, Mapping):
        content_type = content.get("type")
        return f"mapping:{content_type}" if content_type else "mapping"
    return type(content).__name__


def _content_size(content: Any) -> int:
    if content is None:
        return 0
    if isinstance(content, str):
        return len(content)
    if isinstance(content, bytes):
        return len(content)
    try:
        return len(stable_json_dumps(content))
    except Exception:
        return len(str(content))
