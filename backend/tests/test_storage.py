"""I-3 L0 Session Memory + JSONL 로깅 검증 (V0-STEP-5 Stage Gate #1~#7)."""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import log_event, new_trace_id
from vamos_core.schemas.contracts import LogEventSchema, MemoryRecord
from vamos_core.storage.memory_store import MemoryStore


def _record(record_id: str = "mem_001") -> MemoryRecord:
    return MemoryRecord(
        record_id=record_id,
        project_id="proj_test",
        scope="L0",
        memory_type="B-4",
        content_summary="테스트 콘텐츠",
        created_at=datetime.now(UTC).isoformat(),
        policy_decision="allow",
        tags=["test"],
    )


@pytest.fixture
async def store(tmp_path):
    s = MemoryStore(str(tmp_path / "vamos.db"))
    await s.init()
    yield s
    await s.close()


async def test_table_and_indexes_created(store):
    """Stage Gate STEP-5 #1: memory_records 테이블 + 인덱스 3종."""
    cur = await store.db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='memory_records'"
    )
    assert await cur.fetchone() is not None
    cur = await store.db.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
    )
    names = {r[0] for r in await cur.fetchall()}
    assert names == {"idx_session", "idx_scope", "idx_expires"}


async def test_crud_cycle(store):
    """Stage Gate STEP-5 #2: create → read_by_id → update → delete."""
    rid = await store.create(_record(), session_id="sess_A")
    row = await store.read_by_id(rid)
    assert row is not None
    assert row["content"] == "테스트 콘텐츠"
    assert row["scope"] == "L0"
    assert json.loads(row["metadata"])["project_id"] == "proj_test"
    assert await store.update(rid, content="갱신본")
    assert (await store.read_by_id(rid))["content"] == "갱신본"
    assert await store.delete(rid)
    assert await store.read_by_id(rid) is None


async def test_read_by_session(store):
    """Stage Gate STEP-5 #3: 해당 세션 레코드만 반환."""
    await store.create(_record("mem_a1"), session_id="sess_A")
    await store.create(_record("mem_a2"), session_id="sess_A")
    await store.create(_record("mem_b1"), session_id="sess_B")
    rows = await store.read_by_session("sess_A")
    assert {r["id"] for r in rows} == {"mem_a1", "mem_a2"}


async def test_l0_ttl_min_rule(store):
    """Stage Gate STEP-5 #4 (M-30): expires_at = min(session_close, created+30d)."""
    rec = _record("mem_ttl")
    rid = await store.create(rec, session_id="sess_T")
    row = await store.read_by_id(rid)
    created = datetime.fromisoformat(rec.created_at)
    assert datetime.fromisoformat(row["expires_at"]) == created + timedelta(days=30)
    # 세션 종료가 30일 상한보다 이르면 close 시각으로 단축 + 만료분 정리
    close_at = (created + timedelta(hours=1)).isoformat()
    purged = await store.close_session("sess_T", close_time=close_at)
    assert purged == 0  # close 시각 미래 → 아직 만료 아님
    assert (await store.read_by_id(rid))["expires_at"] == close_at


async def test_session_close_purges_expired(store):
    rec = _record("mem_exp")
    await store.create(rec, session_id="sess_E")
    past = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    purged = await store.close_session("sess_E", close_time=past)
    assert purged == 1
    assert await store.read_by_session("sess_E") == []


async def test_update_rejects_unknown_column(store):
    rid = await store.create(_record("mem_guard"), session_id="sess_G")
    with pytest.raises(ValueError, match="갱신 불가"):
        await store.update(rid, expires_at="2099-01-01")  # TTL 우회 금지


# ── JSONL 로깅 (Stage Gate STEP-5 #5~#7) ──────────────────────────────────


@pytest.fixture
def log_env(tmp_path, monkeypatch):
    """config 유래 로그 디렉토리를 tmp로 격리."""
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield tmp_path / "logs"
    reset_config_cache()


def test_log_event_jsonl_7_fields(log_env):
    """#5 JSONL 생성 + #7 정본 7필드 (D2.1-D2 §4.2)."""
    tid = new_trace_id()
    ev = log_event(
        "oc.i1.parse.started", producer="I-1", payload={"input_meta": {"text_len": 5}},
        trace_id=tid,
    )
    assert isinstance(ev, LogEventSchema)
    files = list(log_env.glob("vamos_*.jsonl"))
    assert len(files) == 1
    rec = json.loads(files[0].read_text(encoding="utf-8").strip().splitlines()[-1])
    assert set(rec) >= {"event_type", "producer", "when", "payload", "severity", "links"}
    assert rec["links"]["trace_id"] == tid


def test_log_event_trace_id_consistency(log_env):
    """#6 동일 요청 trace_id 일관성 (UUID v4)."""
    tid = new_trace_id()
    log_event("oc.i1.parse.started", producer="I-1", payload={}, trace_id=tid)
    log_event("oc.i1.intent.parsed", producer="I-1", payload={}, trace_id=tid)
    f = next(iter(log_env.glob("vamos_*.jsonl")))
    lines = [json.loads(line) for line in f.read_text(encoding="utf-8").strip().splitlines()]
    assert [r["links"]["trace_id"] for r in lines[-2:]] == [tid, tid]


def test_log_event_rejects_unregistered_type(log_env):
    """event_type 레지스트리 검증 의무 (4-4 연동)."""
    with pytest.raises(ValueError, match="미등록 event_type"):
        log_event("oc.fake.event", producer="X", payload={}, trace_id=new_trace_id())


def test_log_event_requires_trace_id(log_env):
    with pytest.raises(ValueError, match="trace_id"):
        log_event("oc.i1.parse.started", producer="I-1", payload={}, trace_id="")
    with pytest.raises(ValueError):
        log_event("oc.i1.parse.started", producer="I-1", payload={}, trace_id="not-a-uuid")
