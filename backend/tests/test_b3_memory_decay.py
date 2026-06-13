"""B-3 Memory Decay 검증 — 지수 감쇠 결정론 (6-4/01_memory-hierarchy/B3_memory_decay.md §3).

`decay_score = 0.5^(days/30)`, review=0.3, demote=0.1. 자동삭제 금지(LOCK-MR-005). 이벤트
mem.reference.updated(registries 정본 — 설계 memory.decay.* 미등록 재사용).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.storage.b3_memory_decay import (
    DECAY_THRESHOLD_DEMOTE,
    MemoryDecay,
    classify,
    compute_decay_score,
)


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def test_decay_score_half_life():
    """30일 후 ≈0.50, 60일 ≈0.25, 90일 ≈0.125 (B3 §3.2 verbatim)."""
    now = datetime(2026, 1, 1, tzinfo=UTC)
    assert compute_decay_score(now, now) == 1.0
    assert compute_decay_score(now - timedelta(days=30), now) == 0.5
    assert compute_decay_score(now - timedelta(days=60), now) == 0.25
    assert abs(compute_decay_score(now - timedelta(days=90), now) - 0.125) < 0.001


def test_future_access_clamped():
    """미래 접근 시각 → 1.0 보정."""
    now = datetime(2026, 1, 1, tzinfo=UTC)
    assert compute_decay_score(now + timedelta(days=5), now) == 1.0


def test_classify_thresholds():
    """≥0.3 ACTIVE / 0.1~0.3 REVIEW / <0.1 DEMOTE_CANDIDATE."""
    assert classify(0.9) == "ACTIVE"
    assert classify(0.3) == "ACTIVE"
    assert classify(0.2) == "REVIEW"
    assert classify(0.05) == "DEMOTE_CANDIDATE"


def test_classify_exact_boundaries():
    """경계 정확값 — 0.3=ACTIVE(≥), 0.1=REVIEW(≥), 0.0999=DEMOTE (적대검증 수리)."""
    assert classify(0.30) == "ACTIVE"
    assert classify(0.29) == "REVIEW"
    assert classify(0.10) == "REVIEW"
    assert classify(0.0999) == "DEMOTE_CANDIDATE"


def test_naive_timestamp_no_crash():
    """naive 타임스탬프(SQLite CURRENT_TIMESTAMP) → 크래시 없이 평가 (적대검증 수리)."""
    now = datetime(2026, 6, 1, tzinfo=UTC)
    rec = {"id": "x", "created_at": "2026-01-01 00:00:00"}  # naive(오프셋 없음)
    ev = MemoryDecay().evaluate_record(rec, now)
    assert 0.0 <= ev.decay_score <= 1.0
    assert ev.record_id == "x"


def test_evaluate_record_recommends_action():
    """오래된 레코드 → DEMOTE_CANDIDATE + demote_candidate 권고 (삭제 아님)."""
    now = datetime(2026, 6, 1, tzinfo=UTC)
    rec = {"id": "m1", "created_at": (now - timedelta(days=120)).isoformat()}
    ev = MemoryDecay().evaluate_record(rec, now)
    assert ev.status == "DEMOTE_CANDIDATE"
    assert ev.recommended_action == "demote_candidate"
    assert ev.decay_score < DECAY_THRESHOLD_DEMOTE


def test_batch_skips_pinned():
    """pinned 레코드 = Decay 제외 (S7D-041 예외)."""
    now = datetime(2026, 6, 1, tzinfo=UTC)
    old = (now - timedelta(days=200)).isoformat()
    recs = [{"id": "a", "created_at": old, "pinned": True},
            {"id": "b", "created_at": old, "pinned": False}]
    evs = MemoryDecay().evaluate_batch(recs, now)
    assert [e.record_id for e in evs] == ["b"]


def test_stale_logs_registered_event():
    """저감쇠 stale → mem.reference.updated + MC_ERR_STALE/FB_SHOW_STALE links (registries 정본)."""
    now = datetime(2026, 6, 1, tzinfo=UTC)
    tid = new_trace_id()
    rec = {"id": "m9", "created_at": (now - timedelta(days=150)).isoformat()}
    ev = MemoryDecay().evaluate_record(rec, now, trace_id=tid)
    assert ev.status == "DEMOTE_CANDIDATE"
    # 발행된 로그에 정본 이벤트/링크 기록 확인
    import vamos_core.infra.logger as lg
    log_file = lg._log_file(datetime.now(UTC).isoformat())
    content = log_file.read_text(encoding="utf-8")
    lines = [json.loads(line) for line in content.splitlines() if "mem.reference.updated" in line]
    assert lines
    assert lines[-1]["links"]["failure_code"] == ["MC_ERR_STALE"]
