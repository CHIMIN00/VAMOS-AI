"""I-15 Evidence & QoD Manager 검증 — EvidenceGate 활성화 (D2.0-02 §7.90~7.92).

임계 LOCK(QoD<0.4 L2 금지 / <0.7 HOLD) · 빈 팩=직답 sufficient(무회귀) · score_qod/filter_by_qod
· 이벤트 registries 정본(ui.main.qod.updated) · conclusion 무관(게이트 입력만).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i15_evidence_qod import (
    QOD_HOLD,
    QOD_L2_BAN,
    EvidenceQoDManager,
)
from vamos_core.schemas.contracts import EvidencePack


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def _pack(qods: list[float]) -> EvidencePack:
    return EvidencePack.model_validate({
        "evidence_pack_id": f"evp_{uuid.uuid4().hex[:8]}",
        "trace_id": new_trace_id(),
        "timestamp": datetime.now(UTC).isoformat(),
        "items": [{"source_type": "doc", "source_ref": f"s{i}", "excerpt_or_summary": "x",
                   "qod_score": q, "captured_at": "2026-06-14"} for i, q in enumerate(qods)],
        "coverage": {"sufficient": True, "gaps": []},
        "citations_ready": bool(qods),
    })


def test_thresholds_lock():
    """정본 LOCK — QoD<0.4 L2 금지 / <0.7 HOLD."""
    assert QOD_L2_BAN == 0.4
    assert QOD_HOLD == 0.7


def test_score_qod_clamps_and_defaults():
    m = EvidenceQoDManager()
    assert m.score_qod({"qod_score": 0.9}) == 0.9
    assert m.score_qod({"qod_score": 1.5}) == 1.0  # clamp
    assert m.score_qod({"qod_score": -0.2}) == 0.0
    assert m.score_qod({}) == 0.5  # 누락 = 중립 기본


def test_filter_by_qod_removes_below_ban():
    m = EvidenceQoDManager()
    items = _pack([0.9, 0.3, 0.45, 0.1]).items
    kept = m.filter_by_qod(items)  # 기본 임계 0.4
    assert [it["qod_score"] for it in kept] == [0.9, 0.45]


def test_evaluate_empty_pack_sufficient_no_regression():
    """빈 팩(RAG 미수집/6-3) → sufficient=True 직답, qod/coverage=0 (V0 무회귀)."""
    a = EvidenceQoDManager().evaluate(_pack([]), new_trace_id())
    assert a["sufficient"] is True
    assert a["qod"] == 0.0
    assert a["coverage"] == 0.0
    assert a["items_evaluated"] == 0
    assert a["l2_eligible"] is False


def test_evaluate_high_qod_sufficient():
    """집계 QoD ≥ 0.7 → sufficient + L2 적격."""
    a = EvidenceQoDManager().evaluate(_pack([0.8, 0.9, 0.7]), new_trace_id())
    assert a["qod"] == 0.8
    assert a["sufficient"] is True
    assert a["l2_eligible"] is True
    assert a["coverage"] == 1.0  # 전부 ≥0.4


def test_evaluate_low_qod_insufficient_hold():
    """집계 QoD < 0.7 → insufficient(HOLD), 하지만 ≥0.4면 L2 적격 유지."""
    a = EvidenceQoDManager().evaluate(_pack([0.5, 0.6, 0.4]), new_trace_id())
    assert a["qod"] == 0.5
    assert a["sufficient"] is False  # < 0.7 HOLD
    assert a["l2_eligible"] is True  # 0.5 ≥ 0.4
    assert a["low_qod_count"] == 0


def test_evaluate_below_ban_not_l2_eligible():
    """집계 QoD < 0.4 → L2 삽입 금지 + insufficient."""
    a = EvidenceQoDManager().evaluate(_pack([0.2, 0.3, 0.1]), new_trace_id())
    assert a["sufficient"] is False
    assert a["l2_eligible"] is False  # < 0.4 → L2 금지
    assert a["low_qod_count"] == 3
