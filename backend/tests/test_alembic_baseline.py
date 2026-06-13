"""Alembic V0 baseline 검증 (PHASE5-DEC-001 item 16 / A23 — II-1 적대검증 대상).

3개 오라클:
  1. drift-guard: alembic upgrade가 만드는 스키마 == memory_store.init()가 만드는 스키마
     (PRAGMA table_info + index 대조 — 마이그레이션 frozen SQL이 V0 정본과 어긋나면 FAIL).
  2. V0 read-compat: 기존 V0 데이터가 있는 db에 upgrade해도 데이터 무손실(IF NOT EXISTS no-op).
  3. stamp: 기존 V0 db를 stamp하면 버전만 기록되고 테이블 재생성/데이터 손실 없음.
"""

from __future__ import annotations

import sqlite3
from datetime import UTC, datetime
from pathlib import Path

import pytest
from alembic.config import Config

from alembic import command
from vamos_core.schemas.contracts import MemoryRecord
from vamos_core.storage.memory_store import MemoryStore

_BACKEND = Path(__file__).resolve().parent.parent


def _alembic_cfg(db_path: Path, monkeypatch: pytest.MonkeyPatch) -> Config:
    monkeypatch.setenv("VAMOS_DB_PATH", str(db_path))
    cfg = Config(str(_BACKEND / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND / "alembic"))
    return cfg


def _schema_fingerprint(db_path: Path) -> dict[str, object]:
    """PRAGMA 기반 의미적 스키마 지문 (raw SQL 텍스트 변동에 무관)."""
    con = sqlite3.connect(str(db_path))
    try:
        cols = [
            (r[1], r[2], r[3], r[4], r[5])  # name, type, notnull, dflt_value, pk
            for r in con.execute("PRAGMA table_info(memory_records)").fetchall()
        ]
        idx = sorted(
            r[1] for r in con.execute("PRAGMA index_list(memory_records)").fetchall()
        )
        idx_cols = {
            name: [c[2] for c in con.execute(f"PRAGMA index_info({name})").fetchall()]
            for name in idx
        }
        return {"columns": cols, "indexes": idx, "index_columns": idx_cols}
    finally:
        con.close()


def _record(record_id: str = "mem_alembic_001") -> MemoryRecord:
    return MemoryRecord(
        record_id=record_id,
        project_id="proj_alembic",
        scope="L0",
        memory_type="B-4",
        content_summary="alembic 호환 테스트 레코드",
        created_at=datetime.now(UTC).isoformat(),
        policy_decision="allow",
        tags=["alembic"],
    )


async def test_baseline_schema_matches_memory_store(tmp_path, monkeypatch):
    """drift-guard: alembic baseline 스키마 == memory_store V0 스키마 (지문 동일)."""
    ms_db = tmp_path / "ms.db"
    store = MemoryStore(str(ms_db))
    await store.init()
    await store.close()
    ms_fp = _schema_fingerprint(ms_db)

    al_db = tmp_path / "al.db"
    command.upgrade(_alembic_cfg(al_db, monkeypatch), "head")
    al_fp = _schema_fingerprint(al_db)

    assert al_fp == ms_fp, (
        "Alembic baseline 스키마가 memory_store V0 정본과 drift "
        f"(alembic={al_fp} vs memory_store={ms_fp})"
    )


async def test_v0_data_preserved_on_upgrade(tmp_path, monkeypatch):
    """V0 read-compat: 기존 V0 데이터 db에 upgrade → 데이터 무손실(IF NOT EXISTS no-op)."""
    db = tmp_path / "vamos.db"
    store = MemoryStore(str(db))
    await store.init()
    rec_id = await store.create(_record(), session_id="sess_v0")
    await store.close()

    # 기존 V0 db에 alembic upgrade — 테이블 존재하므로 no-op이어야 함
    command.upgrade(_alembic_cfg(db, monkeypatch), "head")

    store2 = MemoryStore(str(db))
    await store2.init()
    row = await store2.read_by_id(rec_id)
    await store2.close()
    assert row is not None, "upgrade 후 V0 레코드 소실 — 데이터 손실(A23 위반)"
    assert row["content"] == "alembic 호환 테스트 레코드"
    assert row["session_id"] == "sess_v0"


async def test_stamp_existing_v0_records_version_without_recreate(tmp_path, monkeypatch):
    """기존 V0 db stamp → alembic_version 기록 + 데이터 무손실 + 테이블 재생성 없음."""
    db = tmp_path / "vamos.db"
    store = MemoryStore(str(db))
    await store.init()
    rec_id = await store.create(_record("mem_stamp_001"), session_id="sess_stamp")
    await store.close()

    command.stamp(_alembic_cfg(db, monkeypatch), "0001_v0_baseline")

    con = sqlite3.connect(str(db))
    try:
        ver = con.execute("SELECT version_num FROM alembic_version").fetchone()
        assert ver is not None and ver[0] == "0001_v0_baseline"
        cnt = con.execute(
            "SELECT COUNT(*) FROM memory_records WHERE id=?", (rec_id,)
        ).fetchone()[0]
        assert cnt == 1, "stamp 후 V0 데이터 소실"
    finally:
        con.close()
