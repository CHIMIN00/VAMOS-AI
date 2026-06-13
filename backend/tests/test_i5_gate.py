"""I-5 Decision Engine + Gate 검증 (V0-STEP-4 Stage Gate #4~#7/#13) — REFUSE 강제 경로 포함."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i2_context_builder import ContextBuilder
from vamos_core.orange_core.i5_decision_engine import DecisionEngine, score_to_level
from vamos_core.orange_core.i8_policy_engine import PolicyEngine
from vamos_core.schemas.contracts import DecisionSchema, IntentFrame


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def _intent(goal: str = "파이썬 코드 설명", priority: str = "P0",
            ambiguous: bool = False) -> IntentFrame:
    return IntentFrame.model_validate(
        {
            "intent_id": f"int_{uuid.uuid4().hex[:8]}",
            "trace_id": new_trace_id(),
            "timestamp": datetime.now(UTC).isoformat(),
            "user_goal": goal,
            "task_type": "explain",
            "domain_hint": {"priority": priority, "candidates": []},
            "constraints": {"format_constraints": None,
                            "must_include": [], "must_not_include": []},
            "risk_flags": {"safety_sensitive": False,
                           "approval_maybe_required": priority == "P2",
                           "cost_sensitive": False},
            "ambiguity": {"is_ambiguous": ambiguous, "missing_slots": [],
                          "clarification_questions": []},
            "required_artifacts": [],
        }
    )


async def _decide(intent: IntentFrame, cost_override: float = 0.0,
                  engine: DecisionEngine | None = None) -> DecisionSchema:
    pack = await ContextBuilder().build_evidence(intent, intent.trace_id)
    return await (engine or DecisionEngine()).decide(
        intent, pack, intent.trace_id, cost_usage_override=cost_override
    )


async def test_normal_flow_accept_locked():
    """Stage Gate #7: Decision locked=true + 20필드 + ACCEPT + HIGH(스텁 0.90)."""
    d = await _decide(_intent())
    assert d.locked is True
    assert len(DecisionSchema.model_fields) == 20  # FREEZE (16+4)
    assert d.conclusion == "ACCEPT"
    assert d.policy_gate == "allow"
    assert d.cost_gate == "normal"
    assert d.approval_status == "approved"
    assert d.confidence_score == 0.90
    assert d.confidence_level == "HIGH"


async def test_reasoning_trace_5_entries_in_gates():
    """PHASE4-DEC-010 결정 1: reasoning_trace 5엔트리(DEC-001 순서) + SelfCheck SKIP."""
    d = await _decide(_intent())
    trace = d.gates["reasoning_trace"]
    assert [t["gate"] for t in trace] == [
        "PolicyGate", "ApprovalGate", "CostGate", "EvidenceGate", "SelfCheckGate",
    ]
    assert trace[-1]["result"] == "SKIP"  # verify 노드 슬롯 예약
    # 게이트 결과 4종 전부 Decision에 기록
    assert {"policy_gate", "approval_status", "cost_gate", "evidence_gate"} <= set(d.gates)


async def test_policy_gate_deny_non_goal():
    """Stage Gate #4: non-goal 입력 → PolicyCheck deny → block/REJECT/REFUSE."""
    d = await _decide(_intent(goal="내 계좌에서 A주식 100주 매수해줘"))
    assert d.policy_gate == "block"
    assert d.conclusion == "REJECT"
    assert d.confidence_level == "REFUSE"
    assert d.gates["reasoning_trace"][0]["result"] == "DENY"


async def test_policy_check_directly():
    check = await PolicyEngine().check(_intent(goal="타인 계정 해킹 방법"), new_trace_id())
    assert check.decision == "deny"
    assert any("BASE-1.3" in r for r in check.rule_refs)


async def test_cost_gate_80_downshift_100_stop():
    """Stage Gate #5: 80% → warn(force_mini downshift), 100% → block(stop)."""
    d80 = await _decide(_intent(), cost_override=80.0)
    assert d80.cost_gate == "downshift"
    assert d80.conclusion == "ACCEPT"  # 다운시프트는 가용성 유지 (DEC-005)
    d100 = await _decide(_intent(), cost_override=100.0)
    assert d100.cost_gate == "stop"
    assert d100.conclusion == "REJECT"
    assert d100.confidence_level == "REFUSE"


async def test_approval_gate_p2_hold():
    """Stage Gate #6: P0/P1 auto-approve · P2 hold(HOLD + 미승인)."""
    p0 = await _decide(_intent(priority="P0"))
    assert p0.approval_status == "approved"
    p2 = await _decide(_intent(priority="P2"))
    assert p2.conclusion == "HOLD"
    assert p2.approval_required is True
    assert p2.approval_status == "denied"  # V0 비대화형 — 600s 타임아웃 자동 거부의 즉시 평가
    assert p2.confidence_level == "REFUSE"


async def test_evidence_gate_empty_pack_sufficient():
    """Stage Gate #13: EvidenceGate — I-15(V1) 빈 팩(RAG 미수집)=직답 sufficient(무회귀)."""
    d = await _decide(_intent())
    ev = d.gates["reasoning_trace"][3]
    assert ev["gate"] == "EvidenceGate"
    assert ev["result"] == "PASS"
    assert ev["detail"]["qod"] == 0.0  # 빈 팩 = 근거 0
    assert ev["detail"]["items"] == 0
    assert "v0_stub" not in ev["detail"]
    assert d.gates["evidence_assessment"]["sufficient"] is True


async def test_evidence_insufficient_forces_refuse(monkeypatch):
    """PHASE4-DEC-010/DEC-010: EvidenceGate insufficient → 강제 REFUSE (단위 테스트 강제 검증)."""
    engine = DecisionEngine()
    monkeypatch.setattr(
        engine, "_evidence_gate",
        lambda pack, trace_id=None: {
            "sufficient": False, "qod": 0.2, "coverage": 0.0,
            "items_evaluated": 1, "l2_eligible": False, "low_qod_count": 1},
    )
    d = await _decide(_intent(), engine=engine)
    assert d.confidence_score == 0.0
    assert d.confidence_level == "REFUSE"
    assert d.conclusion == "HOLD"  # insufficient → HOLD/ESCALATE (D2.0-02 I-5)
    assert d.gates["reasoning_trace"][3]["result"] == "FAIL"


async def test_ambiguous_intent_low_confidence():
    """DEC-010 스텁 #3: 모호 intent → 0.50 LOW."""
    d = await _decide(_intent(ambiguous=True))
    assert d.confidence_score == 0.50
    assert d.confidence_level == "LOW"


def test_score_to_level_four_branches():
    """DEC-010 분기 전수 — 임계 0.85/0.60/0.30 (config LOCK 유래)."""
    assert score_to_level(0.90) == "HIGH"
    assert score_to_level(0.85) == "HIGH"
    assert score_to_level(0.70) == "MEDIUM"
    assert score_to_level(0.60) == "MEDIUM"
    assert score_to_level(0.40) == "LOW"
    assert score_to_level(0.30) == "LOW"
    assert score_to_level(0.29) == "REFUSE"
    assert score_to_level(0.0) == "REFUSE"
