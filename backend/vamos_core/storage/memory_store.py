"""I-3 구현체 — L0 Session Memory (SQLite, V0-STEP-5 / PART2 L1248~1275).

memory_records SQL은 MemoryRecord(contracts.py 20필드)의 저장 서브셋 —
config/schema_registry.toml [sqlite.tables]에 동기 등재 (P4-1).
컬럼 매핑: id←record_id / content←content_summary / metadata←잔여 필드 JSON /
session_id는 L0 저장 계층 키(인자 — MemoryRecord 외).
TTL (M-30): expires_at = min(session_close_time, created_at + 30days) — CLAUDE.md §15 정본.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from typing import Any

import aiosqlite

from vamos_core.schemas.contracts import MemoryRecord

#: L0 최대 보존 30일 (CLAUDE.md §15 / PART2 M-30 — 정본 상수, config storage.memory_ttl_L0
#: 리터럴 "session_end"의 강제 만료 상한)
L0_MAX_RETENTION_DAYS = 30

#: PART2 L1260~1275 정본 SQL (인덱스는 재초기화 멱등성 위해 IF NOT EXISTS 부가 — 의미 동일)
_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS memory_records (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    scope TEXT DEFAULT 'L0',
    content TEXT NOT NULL,
    embedding BLOB,
    metadata TEXT,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    activation_state TEXT DEFAULT 'active'
);
"""
_CREATE_INDEXES = (
    "CREATE INDEX IF NOT EXISTS idx_session ON memory_records(session_id);",
    "CREATE INDEX IF NOT EXISTS idx_scope ON memory_records(scope);",
    "CREATE INDEX IF NOT EXISTS idx_expires ON memory_records(expires_at);",
)

#: metadata JSON으로 보존하는 MemoryRecord 잔여 필드 (SQL 컬럼 직매핑 외 전부)
_DIRECT_COLUMNS = {"record_id", "scope", "content_summary", "created_at", "activation_state"}


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _max_expiry(created_at: str) -> str:
    created = datetime.fromisoformat(created_at)
    return (created + timedelta(days=L0_MAX_RETENTION_DAYS)).isoformat()


class MemoryStore:
    """L0 Session Memory — aiosqlite CRUD 5종 + TTL 정리."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._db: aiosqlite.Connection | None = None

    async def init(self) -> None:
        """테이블 + 인덱스 3종 생성 (Stage Gate STEP-5 #1)."""
        self._db = await aiosqlite.connect(self._db_path)
        self._db.row_factory = aiosqlite.Row
        await self._db.execute(_CREATE_TABLE)
        for stmt in _CREATE_INDEXES:
            await self._db.execute(stmt)
        await self._db.commit()

    async def close(self) -> None:
        if self._db is not None:
            await self._db.close()
            self._db = None

    @property
    def db(self) -> aiosqlite.Connection:
        if self._db is None:
            raise RuntimeError("MemoryStore.init() 선행 필요")
        return self._db

    # ── CRUD 5종 (PART2 V0-STEP-5 #1) ──────────────────────────────────────

    async def create(self, record: MemoryRecord, session_id: str) -> str:
        """경계 검증(.model_validate 의무) 후 저장. expires_at = created+30d (생성 시점 상한)."""
        rec = MemoryRecord.model_validate(record.model_dump())
        meta = {k: v for k, v in rec.model_dump().items() if k not in _DIRECT_COLUMNS}
        await self.db.execute(
            "INSERT INTO memory_records "
            "(id, session_id, scope, content, embedding, metadata, created_at, updated_at,"
            " expires_at, activation_state) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (
                rec.record_id,
                session_id,
                rec.scope,
                rec.content_summary,
                None,  # V0 임베딩 0
                json.dumps(meta, ensure_ascii=False),
                rec.created_at,
                _now_iso(),
                _max_expiry(rec.created_at),
                rec.activation_state or "active",
            ),
        )
        await self.db.commit()
        return rec.record_id

    async def read_by_id(self, record_id: str) -> dict[str, Any] | None:
        cur = await self.db.execute("SELECT * FROM memory_records WHERE id = ?", (record_id,))
        row = await cur.fetchone()
        return dict(row) if row else None

    async def read_by_session(self, session_id: str) -> list[dict[str, Any]]:
        cur = await self.db.execute(
            "SELECT * FROM memory_records WHERE session_id = ?", (session_id,)
        )
        return [dict(r) for r in await cur.fetchall()]

    async def update(self, record_id: str, **fields: Any) -> bool:
        """content/metadata/activation_state 한정 갱신 + updated_at 자동."""
        allowed = {"content", "metadata", "activation_state"}
        bad = set(fields) - allowed
        if bad:
            raise ValueError(f"갱신 불가 컬럼: {sorted(bad)} (허용: {sorted(allowed)})")
        if not fields:
            return False
        sets = ", ".join(f"{k} = ?" for k in fields)
        cur = await self.db.execute(
            f"UPDATE memory_records SET {sets}, updated_at = ? WHERE id = ?",  # noqa: S608 — 컬럼명 allowlist 검증 완료
            (*fields.values(), _now_iso(), record_id),
        )
        await self.db.commit()
        return cur.rowcount > 0

    async def delete(self, record_id: str) -> bool:
        cur = await self.db.execute("DELETE FROM memory_records WHERE id = ?", (record_id,))
        await self.db.commit()
        return cur.rowcount > 0

    # ── TTL (M-30) ──────────────────────────────────────────────────────────

    async def close_session(self, session_id: str, close_time: str | None = None) -> int:
        """세션 종료 — expires_at = min(session_close_time, created_at + 30d) 적용 후 만료 정리."""
        close_iso = close_time or _now_iso()
        await self.db.execute(
            "UPDATE memory_records SET expires_at = MIN(expires_at, ?), updated_at = ? "
            "WHERE session_id = ?",
            (close_iso, _now_iso(), session_id),
        )
        await self.db.commit()
        return await self.purge_expired()

    async def purge_expired(self, now: str | None = None) -> int:
        """TTL 만료 레코드 삭제 (세션 종료 시 자동 정리)."""
        cur = await self.db.execute(
            "DELETE FROM memory_records WHERE expires_at IS NOT NULL AND expires_at <= ?",
            (now or _now_iso(),),
        )
        await self.db.commit()
        return cur.rowcount
