"""Typed Nova claim records and append-only transition storage.

Claims model typed state at the Nova kernel boundary. This module does not
replace Hermes memory and performs no writes unless an explicit store method is
called.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Iterable, Mapping, Protocol

from agent.nova.evidence import MissingEvidenceError
from agent.nova.kernel import (
    ClaimStatus,
    EvidenceRef,
    EvidenceRefKind,
    GateDecision,
    GateResult,
    stable_json_dumps,
)
from agent.nova.ledger import default_ledger_path
from hermes_state import apply_wal_with_fallback


CLAIMS_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS nova_claim_transitions (
    transition_seq INTEGER PRIMARY KEY AUTOINCREMENT,
    id TEXT NOT NULL UNIQUE,
    claim_id TEXT NOT NULL,
    transition_kind TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    scope TEXT NOT NULL,
    statement TEXT NOT NULL,
    source TEXT NOT NULL,
    status TEXT NOT NULL,
    trust_state TEXT NOT NULL,
    evidence_bundle_id TEXT,
    evidence_refs TEXT NOT NULL DEFAULT '[]',
    gate_decision_id TEXT,
    invalidation_refs TEXT NOT NULL DEFAULT '[]',
    previous_status TEXT,
    previous_trust_state TEXT,
    actor TEXT NOT NULL,
    reason TEXT NOT NULL DEFAULT '',
    claim_metadata TEXT NOT NULL DEFAULT '{}',
    metadata TEXT NOT NULL DEFAULT '{}',
    claim_created_at REAL NOT NULL,
    claim_updated_at REAL NOT NULL,
    created_at REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_nova_claim_transitions_claim
    ON nova_claim_transitions(claim_id, transition_seq);
CREATE INDEX IF NOT EXISTS idx_nova_claim_transitions_scope_type
    ON nova_claim_transitions(scope, claim_type);
CREATE INDEX IF NOT EXISTS idx_nova_claim_transitions_status
    ON nova_claim_transitions(status, trust_state);
"""


class ClaimTrustState(StrEnum):
    """Trust posture for typed claims."""

    UNTRUSTED = "untrusted"
    STAGED = "staged"
    TRUSTED = "trusted"
    DEMOTED = "demoted"
    INVALIDATED = "invalidated"


class ClaimTransitionKind(StrEnum):
    """Append-only claim transition families."""

    PROPOSED = "proposed"
    STAGED = "staged"
    TRUSTED = "trusted"
    REJECTED = "rejected"
    DEMOTED = "demoted"
    INVALIDATED = "invalidated"


class ClaimTrustError(ValueError):
    """Raised when a claim trust transition fails closed."""


class ClaimStore(Protocol):
    """Minimal storage boundary for typed claims."""

    def create_claim(
        self,
        claim: "ClaimRecord",
        *,
        actor: str = "kernel",
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> "ClaimTransition":
        """Persist an initial claim proposal transition."""

    def append_transition(self, transition: "ClaimTransition") -> "ClaimTransition | None":
        """Append one immutable claim transition."""

    def transition_claim(
        self,
        claim_id: str,
        status: ClaimStatus | str,
        *,
        trust_state: ClaimTrustState | str | None = None,
        gate_decision: GateDecision | None = None,
        required_evidence_kinds: Iterable[EvidenceRefKind | str] = (),
        evidence_refs: Iterable[EvidenceRef] | None = None,
        evidence_bundle_id: str | None = None,
        invalidation_refs: Iterable[str] | None = None,
        actor: str = "kernel",
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> "ClaimTransition":
        """Load the latest claim, build a validated transition, and append it."""

    def get_claim(self, claim_id: str) -> "ClaimRecord | None":
        """Return the latest claim state."""

    def iter_claims(
        self,
        *,
        scope: str | None = None,
        claim_type: str | None = None,
        status: ClaimStatus | str | None = None,
        trust_state: ClaimTrustState | str | None = None,
        limit: int | None = None,
    ) -> list["ClaimRecord"]:
        """Return latest claim states matching optional filters."""

    def iter_transitions(
        self,
        *,
        claim_id: str | None = None,
        scope: str | None = None,
        claim_type: str | None = None,
        limit: int | None = None,
    ) -> list["ClaimTransition"]:
        """Return transition history for audit/debug."""


@dataclass(frozen=True)
class ClaimRecord:
    """Typed state claim with compact evidence pointers."""

    claim_type: str
    scope: str
    statement: str
    source: str
    id: str = field(default_factory=lambda: _new_id("claim"))
    status: ClaimStatus = ClaimStatus.PROPOSED
    trust_state: ClaimTrustState = ClaimTrustState.UNTRUSTED
    evidence_refs: tuple[EvidenceRef, ...] = ()
    evidence_bundle_id: str | None = None
    gate_decision_id: str | None = None
    invalidation_refs: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        object.__setattr__(self, "id", str(self.id))
        object.__setattr__(self, "claim_type", _required_text("claim_type", self.claim_type))
        object.__setattr__(self, "scope", _required_text("scope", self.scope))
        object.__setattr__(self, "statement", _required_text("statement", self.statement))
        object.__setattr__(self, "source", _required_text("source", self.source))
        object.__setattr__(self, "status", ClaimStatus(self.status))
        object.__setattr__(self, "trust_state", ClaimTrustState(self.trust_state))
        object.__setattr__(self, "evidence_refs", _tuple_of_refs(self.evidence_refs))
        object.__setattr__(self, "invalidation_refs", _tuple_of_str(self.invalidation_refs))
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))
        object.__setattr__(self, "created_at", float(self.created_at))
        object.__setattr__(self, "updated_at", float(self.updated_at))
        _validate_status_trust_pair(self.status, self.trust_state)
        if self.is_trusted:
            if not self.gate_decision_id:
                raise ClaimTrustError("trusted claims require a gate decision")
            if not self.evidence_refs:
                raise MissingEvidenceError("trusted claims require evidence refs")
        if self.status is ClaimStatus.INVALIDATED and not self.invalidation_refs:
            raise ValueError("invalidated claims require invalidation refs")

    @property
    def is_trusted(self) -> bool:
        return self.status is ClaimStatus.ACTIVE and self.trust_state is ClaimTrustState.TRUSTED


@dataclass(frozen=True)
class ClaimTransition:
    """Single append-only claim transition snapshot."""

    claim: ClaimRecord
    transition_kind: ClaimTransitionKind
    previous_status: ClaimStatus | None = None
    previous_trust_state: ClaimTrustState | None = None
    actor: str = "kernel"
    reason: str = ""
    metadata: Mapping[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: _new_id("clt"))
    created_at: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        if not isinstance(self.claim, ClaimRecord):
            raise TypeError(f"claim must be ClaimRecord, got {type(self.claim).__name__}")
        object.__setattr__(self, "transition_kind", ClaimTransitionKind(self.transition_kind))
        if self.previous_status is not None:
            object.__setattr__(self, "previous_status", ClaimStatus(self.previous_status))
        if self.previous_trust_state is not None:
            object.__setattr__(
                self,
                "previous_trust_state",
                ClaimTrustState(self.previous_trust_state),
            )
        object.__setattr__(self, "actor", str(self.actor))
        object.__setattr__(self, "reason", str(self.reason))
        object.__setattr__(self, "metadata", _dict_copy(self.metadata))
        object.__setattr__(self, "id", str(self.id))
        object.__setattr__(self, "created_at", float(self.created_at))


class DisabledClaimStore:
    """No-op claim store for disabled Nova mode."""

    def create_claim(
        self,
        claim: ClaimRecord,
        *,
        actor: str = "kernel",
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> ClaimTransition:
        return initial_claim_transition(
            claim,
            actor=actor,
            reason=reason,
            metadata=metadata,
        )

    def append_transition(self, transition: ClaimTransition) -> ClaimTransition:
        return transition

    def transition_claim(
        self,
        claim_id: str,
        status: ClaimStatus | str,
        *,
        trust_state: ClaimTrustState | str | None = None,
        gate_decision: GateDecision | None = None,
        required_evidence_kinds: Iterable[EvidenceRefKind | str] = (),
        evidence_refs: Iterable[EvidenceRef] | None = None,
        evidence_bundle_id: str | None = None,
        invalidation_refs: Iterable[str] | None = None,
        actor: str = "kernel",
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> ClaimTransition:
        raise KeyError(str(claim_id))

    def get_claim(self, claim_id: str) -> ClaimRecord | None:
        return None

    def iter_claims(
        self,
        *,
        scope: str | None = None,
        claim_type: str | None = None,
        status: ClaimStatus | str | None = None,
        trust_state: ClaimTrustState | str | None = None,
        limit: int | None = None,
    ) -> list[ClaimRecord]:
        return []

    def iter_transitions(
        self,
        *,
        claim_id: str | None = None,
        scope: str | None = None,
        claim_type: str | None = None,
        limit: int | None = None,
    ) -> list[ClaimTransition]:
        return []

    def close(self) -> None:
        return None


class SQLiteClaimStore:
    """SQLite-backed append-only typed claim transition store."""

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
        self._conn.executescript(CLAIMS_SCHEMA_SQL)

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.execute("PRAGMA wal_checkpoint(PASSIVE)")
                except Exception:
                    pass
                self._conn.close()
                self._conn = None

    def create_claim(
        self,
        claim: ClaimRecord,
        *,
        actor: str = "kernel",
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> ClaimTransition:
        if self.get_claim(claim.id) is not None:
            raise sqlite3.IntegrityError(f"claim already exists: {claim.id}")
        transition = initial_claim_transition(
            claim,
            actor=actor,
            reason=reason,
            metadata=metadata,
        )
        return self.append_transition(transition)

    def append_transition(self, transition: ClaimTransition) -> ClaimTransition:
        if not isinstance(transition, ClaimTransition):
            raise TypeError(
                f"transition must be ClaimTransition, got {type(transition).__name__}"
            )

        def _append(conn: sqlite3.Connection) -> ClaimTransition:
            latest = _latest_transition_row(conn, transition.claim.id)
            if latest is None:
                if (
                    transition.previous_status is not None
                    or transition.previous_trust_state is not None
                ):
                    raise ValueError("initial claim transition cannot have previous state")
            else:
                latest_status = ClaimStatus(latest["status"])
                latest_trust_state = ClaimTrustState(latest["trust_state"])
                if transition.previous_status != latest_status:
                    raise ValueError("claim transition previous_status is stale")
                if transition.previous_trust_state != latest_trust_state:
                    raise ValueError("claim transition previous_trust_state is stale")

            conn.execute(
                """
                INSERT INTO nova_claim_transitions(
                    id, claim_id, transition_kind, claim_type, scope, statement,
                    source, status, trust_state, evidence_bundle_id, evidence_refs,
                    gate_decision_id, invalidation_refs, previous_status,
                    previous_trust_state, actor, reason, claim_metadata, metadata,
                    claim_created_at, claim_updated_at, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                _transition_params(transition),
            )
            return transition

        return self._execute_write(_append)

    def transition_claim(
        self,
        claim_id: str,
        status: ClaimStatus | str,
        *,
        trust_state: ClaimTrustState | str | None = None,
        gate_decision: GateDecision | None = None,
        required_evidence_kinds: Iterable[EvidenceRefKind | str] = (),
        evidence_refs: Iterable[EvidenceRef] | None = None,
        evidence_bundle_id: str | None = None,
        invalidation_refs: Iterable[str] | None = None,
        actor: str = "kernel",
        reason: str = "",
        metadata: Mapping[str, Any] | None = None,
    ) -> ClaimTransition:
        claim = self.get_claim(claim_id)
        if claim is None:
            raise KeyError(str(claim_id))
        transition = build_claim_transition(
            claim,
            status,
            trust_state=trust_state,
            gate_decision=gate_decision,
            required_evidence_kinds=required_evidence_kinds,
            evidence_refs=evidence_refs,
            evidence_bundle_id=evidence_bundle_id,
            invalidation_refs=invalidation_refs,
            actor=actor,
            reason=reason,
            metadata=metadata,
        )
        return self.append_transition(transition)

    def get_claim(self, claim_id: str) -> ClaimRecord | None:
        row = _latest_transition_row(self._conn, str(claim_id))
        if row is None:
            return None
        return _row_to_claim(row)

    def iter_claims(
        self,
        *,
        scope: str | None = None,
        claim_type: str | None = None,
        status: ClaimStatus | str | None = None,
        trust_state: ClaimTrustState | str | None = None,
        limit: int | None = None,
    ) -> list[ClaimRecord]:
        clauses: list[str] = []
        params: list[object] = []
        if scope is not None:
            clauses.append("t.scope = ?")
            params.append(str(scope))
        if claim_type is not None:
            clauses.append("t.claim_type = ?")
            params.append(str(claim_type))
        if status is not None:
            clauses.append("t.status = ?")
            params.append(ClaimStatus(status).value)
        if trust_state is not None:
            clauses.append("t.trust_state = ?")
            params.append(ClaimTrustState(trust_state).value)
        sql = _latest_claims_sql(clauses)
        if limit is not None:
            sql += " LIMIT ?"
            params.append(int(limit))
        rows = self._conn.execute(sql, params).fetchall()
        return [_row_to_claim(row) for row in rows]

    def iter_transitions(
        self,
        *,
        claim_id: str | None = None,
        scope: str | None = None,
        claim_type: str | None = None,
        limit: int | None = None,
    ) -> list[ClaimTransition]:
        clauses: list[str] = []
        params: list[object] = []
        if claim_id is not None:
            clauses.append("claim_id = ?")
            params.append(str(claim_id))
        if scope is not None:
            clauses.append("scope = ?")
            params.append(str(scope))
        if claim_type is not None:
            clauses.append("claim_type = ?")
            params.append(str(claim_type))
        sql = "SELECT * FROM nova_claim_transitions"
        if clauses:
            sql += f" WHERE {' AND '.join(clauses)}"
        sql += " ORDER BY transition_seq ASC"
        if limit is not None:
            sql += " LIMIT ?"
            params.append(int(limit))
        rows = self._conn.execute(sql, params).fetchall()
        return [_row_to_transition(row) for row in rows]

    def _execute_write(self, fn):
        if self._conn is None:
            raise sqlite3.ProgrammingError("claim store connection is closed")
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


def propose_claim(
    *,
    claim_type: str,
    scope: str,
    statement: str,
    source: str,
    evidence_refs: Iterable[EvidenceRef] | None = None,
    evidence_bundle_id: str | None = None,
    metadata: Mapping[str, Any] | None = None,
    claim_id: str | None = None,
) -> ClaimRecord:
    """Build an untrusted claim proposal without writing storage."""

    return ClaimRecord(
        id=claim_id or _new_id("claim"),
        claim_type=claim_type,
        scope=scope,
        statement=statement,
        source=source,
        status=ClaimStatus.PROPOSED,
        trust_state=ClaimTrustState.UNTRUSTED,
        evidence_refs=_tuple_of_refs(evidence_refs),
        evidence_bundle_id=evidence_bundle_id,
        metadata=metadata or {},
    )


def initial_claim_transition(
    claim: ClaimRecord,
    *,
    actor: str = "kernel",
    reason: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> ClaimTransition:
    return ClaimTransition(
        claim=claim,
        transition_kind=_transition_kind_for_status(claim.status),
        previous_status=None,
        previous_trust_state=None,
        actor=actor,
        reason=reason,
        metadata=metadata or {},
    )


def build_claim_transition(
    claim: ClaimRecord,
    status: ClaimStatus | str,
    *,
    trust_state: ClaimTrustState | str | None = None,
    gate_decision: GateDecision | None = None,
    required_evidence_kinds: Iterable[EvidenceRefKind | str] = (),
    evidence_refs: Iterable[EvidenceRef] | None = None,
    evidence_bundle_id: str | None = None,
    invalidation_refs: Iterable[str] | None = None,
    actor: str = "kernel",
    reason: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> ClaimTransition:
    """Build a validated transition without writing storage."""

    if not isinstance(claim, ClaimRecord):
        raise TypeError(f"claim must be ClaimRecord, got {type(claim).__name__}")
    new_status = ClaimStatus(status)
    new_trust_state = (
        ClaimTrustState(trust_state)
        if trust_state is not None
        else _trust_state_for_status(new_status)
    )
    resolved_evidence_refs = (
        _tuple_of_refs(evidence_refs) if evidence_refs is not None else claim.evidence_refs
    )
    resolved_gate_decision_id = claim.gate_decision_id
    if gate_decision is not None:
        resolved_gate_decision_id = str(gate_decision.id)
    if new_status is ClaimStatus.ACTIVE or new_trust_state is ClaimTrustState.TRUSTED:
        _validate_gate_decision(gate_decision, claim)
        require_claim_evidence_refs(resolved_evidence_refs, required_evidence_kinds)
    resolved_invalidation_refs = (
        _tuple_of_str(invalidation_refs)
        if invalidation_refs is not None
        else claim.invalidation_refs
    )
    if new_status is ClaimStatus.INVALIDATED and not resolved_invalidation_refs:
        raise ValueError("invalidated claims require invalidation refs")
    updated_claim = ClaimRecord(
        id=claim.id,
        claim_type=claim.claim_type,
        scope=claim.scope,
        statement=claim.statement,
        source=claim.source,
        status=new_status,
        trust_state=new_trust_state,
        evidence_refs=resolved_evidence_refs,
        evidence_bundle_id=evidence_bundle_id
        if evidence_bundle_id is not None
        else claim.evidence_bundle_id,
        gate_decision_id=resolved_gate_decision_id,
        invalidation_refs=resolved_invalidation_refs,
        metadata=claim.metadata,
        created_at=claim.created_at,
        updated_at=time.time(),
    )
    return ClaimTransition(
        claim=updated_claim,
        transition_kind=_transition_kind_for_status(new_status),
        previous_status=claim.status,
        previous_trust_state=claim.trust_state,
        actor=actor,
        reason=reason,
        metadata=metadata or {},
    )


def trust_claim(
    claim: ClaimRecord,
    *,
    gate_decision: GateDecision,
    required_evidence_kinds: Iterable[EvidenceRefKind | str] = (),
    evidence_refs: Iterable[EvidenceRef] | None = None,
    evidence_bundle_id: str | None = None,
    actor: str = "kernel",
    reason: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> ClaimTransition:
    """Build a trusted transition, failing closed without gate and evidence."""

    return build_claim_transition(
        claim,
        ClaimStatus.ACTIVE,
        trust_state=ClaimTrustState.TRUSTED,
        gate_decision=gate_decision,
        required_evidence_kinds=required_evidence_kinds,
        evidence_refs=evidence_refs,
        evidence_bundle_id=evidence_bundle_id,
        actor=actor,
        reason=reason,
        metadata=metadata,
    )


def invalidate_claim(
    claim: ClaimRecord,
    *,
    invalidation_refs: Iterable[str],
    actor: str = "kernel",
    reason: str = "",
    metadata: Mapping[str, Any] | None = None,
) -> ClaimTransition:
    """Build an invalidation transition with explicit invalidation refs."""

    return build_claim_transition(
        claim,
        ClaimStatus.INVALIDATED,
        trust_state=ClaimTrustState.INVALIDATED,
        invalidation_refs=invalidation_refs,
        actor=actor,
        reason=reason,
        metadata=metadata,
    )


def require_claim_evidence_refs(
    refs: Iterable[EvidenceRef],
    required_kinds: Iterable[EvidenceRefKind | str],
) -> tuple[EvidenceRef, ...]:
    """Fail closed unless claim evidence has all required ref families."""

    evidence_refs = _tuple_of_refs(refs)
    required = tuple(EvidenceRefKind(kind) for kind in required_kinds)
    if not evidence_refs:
        raise MissingEvidenceError("missing claim evidence refs")
    if not required:
        return evidence_refs
    present = {ref.kind for ref in evidence_refs}
    missing = [kind.value for kind in required if kind not in present]
    if missing:
        raise MissingEvidenceError(f"claim missing required evidence refs: {', '.join(missing)}")
    return evidence_refs


def _transition_params(transition: ClaimTransition) -> tuple[object, ...]:
    claim = transition.claim
    return (
        transition.id,
        claim.id,
        transition.transition_kind.value,
        claim.claim_type,
        claim.scope,
        claim.statement,
        claim.source,
        claim.status.value,
        claim.trust_state.value,
        claim.evidence_bundle_id,
        stable_json_dumps([_evidence_ref_to_dict(ref) for ref in claim.evidence_refs]),
        claim.gate_decision_id,
        stable_json_dumps(list(claim.invalidation_refs)),
        transition.previous_status.value if transition.previous_status is not None else None,
        transition.previous_trust_state.value
        if transition.previous_trust_state is not None
        else None,
        transition.actor,
        transition.reason,
        stable_json_dumps(claim.metadata),
        stable_json_dumps(transition.metadata),
        claim.created_at,
        claim.updated_at,
        transition.created_at,
    )


def _latest_transition_row(conn: sqlite3.Connection, claim_id: str) -> sqlite3.Row | None:
    return conn.execute(
        """
        SELECT * FROM nova_claim_transitions
        WHERE claim_id = ?
        ORDER BY transition_seq DESC
        LIMIT 1
        """,
        (str(claim_id),),
    ).fetchone()


def _latest_claims_sql(clauses: list[str]) -> str:
    sql = """
        SELECT t.* FROM nova_claim_transitions t
        JOIN (
            SELECT claim_id, max(transition_seq) AS transition_seq
            FROM nova_claim_transitions
            GROUP BY claim_id
        ) latest
        ON latest.claim_id = t.claim_id
        AND latest.transition_seq = t.transition_seq
    """
    if clauses:
        sql += f" WHERE {' AND '.join(clauses)}"
    sql += " ORDER BY t.transition_seq ASC"
    return sql


def _row_to_transition(row: sqlite3.Row) -> ClaimTransition:
    previous_status = row["previous_status"]
    previous_trust_state = row["previous_trust_state"]
    return ClaimTransition(
        id=row["id"],
        claim=_row_to_claim(row),
        transition_kind=ClaimTransitionKind(row["transition_kind"]),
        previous_status=ClaimStatus(previous_status) if previous_status is not None else None,
        previous_trust_state=ClaimTrustState(previous_trust_state)
        if previous_trust_state is not None
        else None,
        actor=row["actor"],
        reason=row["reason"],
        metadata=json.loads(row["metadata"] or "{}"),
        created_at=row["created_at"],
    )


def _row_to_claim(row: sqlite3.Row) -> ClaimRecord:
    return ClaimRecord(
        id=row["claim_id"],
        claim_type=row["claim_type"],
        scope=row["scope"],
        statement=row["statement"],
        source=row["source"],
        status=ClaimStatus(row["status"]),
        trust_state=ClaimTrustState(row["trust_state"]),
        evidence_refs=tuple(
            _evidence_ref_from_dict(value) for value in json.loads(row["evidence_refs"] or "[]")
        ),
        evidence_bundle_id=row["evidence_bundle_id"],
        gate_decision_id=row["gate_decision_id"],
        invalidation_refs=tuple(json.loads(row["invalidation_refs"] or "[]")),
        metadata=json.loads(row["claim_metadata"] or "{}"),
        created_at=row["claim_created_at"],
        updated_at=row["claim_updated_at"],
    )


def _evidence_ref_to_dict(ref: EvidenceRef) -> dict[str, Any]:
    return {
        "kind": ref.kind.value,
        "ref": ref.ref,
        "digest": ref.digest,
        "metadata": dict(ref.metadata),
    }


def _evidence_ref_from_dict(value: Mapping[str, Any]) -> EvidenceRef:
    return EvidenceRef(
        EvidenceRefKind(value["kind"]),
        str(value["ref"]),
        digest=value.get("digest"),
        metadata=value.get("metadata") or {},
    )


def _validate_gate_decision(gate_decision: GateDecision | None, claim: ClaimRecord) -> None:
    if gate_decision is None:
        raise ClaimTrustError("trusted claim transitions require a gate decision")
    if gate_decision.result is not GateResult.PASS:
        raise ClaimTrustError(
            f"trusted claim transitions require a passing gate decision, got {gate_decision.result}"
        )
    if str(gate_decision.proposal_id) != claim.id:
        raise ClaimTrustError("gate decision must target the claim being trusted")


def _transition_kind_for_status(status: ClaimStatus) -> ClaimTransitionKind:
    if status is ClaimStatus.PROPOSED:
        return ClaimTransitionKind.PROPOSED
    if status is ClaimStatus.STAGED:
        return ClaimTransitionKind.STAGED
    if status is ClaimStatus.ACTIVE:
        return ClaimTransitionKind.TRUSTED
    if status is ClaimStatus.REJECTED:
        return ClaimTransitionKind.REJECTED
    if status is ClaimStatus.DEMOTED:
        return ClaimTransitionKind.DEMOTED
    if status is ClaimStatus.INVALIDATED:
        return ClaimTransitionKind.INVALIDATED
    raise ValueError(f"unsupported claim status: {status}")


def _trust_state_for_status(status: ClaimStatus) -> ClaimTrustState:
    if status is ClaimStatus.STAGED:
        return ClaimTrustState.STAGED
    if status is ClaimStatus.ACTIVE:
        return ClaimTrustState.TRUSTED
    if status is ClaimStatus.DEMOTED:
        return ClaimTrustState.DEMOTED
    if status is ClaimStatus.INVALIDATED:
        return ClaimTrustState.INVALIDATED
    return ClaimTrustState.UNTRUSTED


def _validate_status_trust_pair(status: ClaimStatus, trust_state: ClaimTrustState) -> None:
    allowed = {
        ClaimStatus.PROPOSED: {ClaimTrustState.UNTRUSTED},
        ClaimStatus.REJECTED: {ClaimTrustState.UNTRUSTED, ClaimTrustState.DEMOTED},
        ClaimStatus.STAGED: {ClaimTrustState.STAGED},
        ClaimStatus.ACTIVE: {ClaimTrustState.TRUSTED},
        ClaimStatus.DEMOTED: {ClaimTrustState.DEMOTED},
        ClaimStatus.INVALIDATED: {ClaimTrustState.INVALIDATED},
    }
    if trust_state not in allowed[status]:
        raise ValueError(
            f"claim status {status.value} is incompatible with trust state {trust_state.value}"
        )


def _tuple_of_refs(values: Iterable[EvidenceRef] | None) -> tuple[EvidenceRef, ...]:
    if values is None:
        return ()
    refs = tuple(values)
    for ref in refs:
        if not isinstance(ref, EvidenceRef):
            raise TypeError(f"evidence refs must be EvidenceRef, got {type(ref).__name__}")
    return refs


def _tuple_of_str(values: Iterable[str] | None) -> tuple[str, ...]:
    if values is None:
        return ()
    return tuple(str(value) for value in values)


def _dict_copy(value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError(f"metadata must be a mapping, got {type(value).__name__}")
    return dict(value)


def _required_text(field_name: str, value: Any) -> str:
    text = str(value)
    if not text:
        raise ValueError(f"{field_name} is required")
    return text


def _new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"
