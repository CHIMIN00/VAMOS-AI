"""S-1 Self-check Surface 검증 — I-6 + I-15 항상-ON wrap (D2.0-01 §5.7).

S-1 은 재구현 없이 I-6(self_check)·I-15(evidence) 위임. run_self_check 반환 형태는 I-6 동형
(파이프라인 verify 노드 동작 불변 — V0 무회귀). minimal_check 는 둘을 결합한 표면.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i2_context_builder import ContextBuilder
from vamos_core.orange_core.i5_decision_engine import DecisionEngine
from vamos_core.orange_core.i6_self_check import SelfCheckEngine
from vamos_core.orange_core.s1_self_check_surface import SelfCheckSurface
from vamos_core.schemas.contracts import DecisionSchema, IntentFrame


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def _intent() -> IntentFrame:
    return IntentFrame.model_validate({
        "intent_id": f"int_{uuid.uuid4().hex[:8]}",
        "trace_id": new_trace_id(),
        "timestamp": datetime.now(UTC).isoformat(),
        "user_goal": "파이썬 설명", "task_type": "explain",
        "domain_hint": {"priority": "P0", "candidates": []},
        "constraints": {"format_constraints": None, "must_include": [], "must_not_include": []},
        "risk_flags": {"safety_sensitive": False, "approval_maybe_required": False,
                       "cost_sensitive": False},
        "ambiguity": {"is_ambiguous": False, "missing_slots": [], "clarification_questions": []},
        "required_artifacts": [],
    })


async def _decide(intent: IntentFrame) -> DecisionSchema:
    pack = await ContextBuilder().build_evidence(intent, intent.trace_id)
    return await DecisionEngine().decide(intent, pack, intent.trace_id)


async def test_surface_self_check_matches_i6():
    """S-1.run_self_check == I-6.run_self_check (재구현 없음 — wrap 동형)."""
    intent = _intent()
    d = await _decide(intent)
    surface = SelfCheckSurface().run_self_check(
        d, llm_response="답변", failure_codes=[], trace_id=d.trace_id)
    direct = SelfCheckEngine().run_self_check(
        d, llm_response="답변", failure_codes=[], trace_id=d.trace_id)
    assert surface["verdict"] == direct["verdict"]
    assert surface["score"] == direct["score"]
    assert set(surface) == set(direct)


async def test_minimal_check_combines_i6_i15():
    """minimal_check → self_check + evidence 결합(항상-ON 표면)."""
    intent = _intent()
    d = await _decide(intent)
    pack = await ContextBuilder().build_evidence(intent, intent.trace_id)
    out = SelfCheckSurface().minimal_check(
        d, llm_response="답변", evidence_pack=pack, failure_codes=[], trace_id=d.trace_id)
    assert "self_check" in out and "evidence" in out
    assert out["self_check"]["verdict"] in ("PASS", "FAIL")
    assert "sufficient" in out["evidence"]


async def test_minimal_check_no_evidence_pack():
    """evidence_pack 없음 → 직답 경로 보존(sufficient True, V0 무회귀)."""
    intent = _intent()
    d = await _decide(intent)
    out = SelfCheckSurface().minimal_check(
        d, llm_response="답변", evidence_pack=None, failure_codes=[], trace_id=d.trace_id)
    assert out["evidence"]["sufficient"] is True
    assert out["evidence"]["items_evaluated"] == 0


async def test_none_path_keyset_matches_i15():
    """None-path evidence 키셋 = I-15 evaluate() 빈-팩 출력 동형 (적대검증 수리)."""
    from vamos_core.orange_core.i15_evidence_qod import EvidenceQoDManager
    from vamos_core.schemas.contracts import EvidencePack
    intent = _intent()
    d = await _decide(intent)
    out = SelfCheckSurface().minimal_check(
        d, llm_response="답변", evidence_pack=None, failure_codes=[], trace_id=d.trace_id)
    empty_pack = EvidencePack.model_validate({
        "evidence_pack_id": "ep_x", "trace_id": d.trace_id,
        "timestamp": datetime.now(UTC).isoformat(), "items": [],
        "coverage": {"sufficient": True, "gaps": []}, "citations_ready": False})
    i15_keys = set(EvidenceQoDManager().evaluate(empty_pack))
    assert set(out["evidence"]) == i15_keys


async def test_minimal_check_fail_path_fallback():
    """FAIL 경로 — POLICY_DENY → self_check FAIL + fallback (I-6 위임 정합)."""
    intent = _intent()
    d = await _decide(intent)
    out = SelfCheckSurface().minimal_check(
        d, llm_response="x", evidence_pack=None, failure_codes=["POLICY_DENY"], trace_id=d.trace_id)
    assert out["self_check"]["verdict"] == "FAIL"
    assert out["self_check"]["retry_allowed"] is True
