"""V0 baseline — memory_records (L0 Session Memory) 초기 스키마 동결.

Revision ID: 0001_v0_baseline
Revises:
Create Date: 2026-06-13

PHASE5-DEC-001 item 16 / A23 V0→V1 마이그레이션:
  본 revision은 V0 스키마를 baseline(rev 0)으로 *동결*한다. SQL은 V0 시점
  `vamos_core/storage/memory_store.py`(_CREATE_TABLE·_CREATE_INDEXES, PART2 L1260~1275 정본)
  와 **byte 동일**하게 frozen — 마이그레이션 불변성(historical record) 원칙상 복사하되,
  drift는 tests/test_alembic_baseline.py가 두 경로(memory_store.init vs alembic upgrade)의
  sqlite_master를 대조해 차단한다.

V0 호환(무손실):
  - upgrade()는 CREATE TABLE/INDEX IF NOT EXISTS → 기존 V0 vamos.db에 실행해도 no-op
    (데이터·스키마 보존). 신규 db에는 V0 동일 스키마 생성.
  - 기존 V0 db 등록 권장: `alembic stamp 0001_v0_baseline` (테이블 재생성 없이 버전만 기록).
  - downgrade()는 DROP — *파괴적*(V0 데이터 손실). 운영 db에 절대 자동 실행 금지(II-1).
"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_v0_baseline"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# V0 정본 SQL (memory_store.py 동결 복사 — V0 시점, 변경 금지).
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
_INDEX_NAMES = ("idx_session", "idx_scope", "idx_expires")


def upgrade() -> None:
    op.execute(_CREATE_TABLE)
    for stmt in _CREATE_INDEXES:
        op.execute(stmt)


def downgrade() -> None:
    # ⚠️ 파괴적 — V0 L0 메모리 데이터 전체 손실. 운영 db 금지(II-1 적대검증 대상).
    for idx in _INDEX_NAMES:
        op.execute(f"DROP INDEX IF EXISTS {idx};")
    op.execute("DROP TABLE IF EXISTS memory_records;")
