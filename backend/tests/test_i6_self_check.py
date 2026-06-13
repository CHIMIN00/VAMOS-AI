"""I-6 Self-check Engine 검증 — verify 노드 활성화 (D2.0-02 §7.51~7.53 LOCK).

위험도 가변 임계값(P0≥70/P1≥75/P2≥80) · 4-검증(출력/근거-결론/안전/자기모순) · FAIL 수렴
fallback(02 §6.3 정본) · 단일결정 불변(conclusion 무변경) · 이벤트 registries 정본.
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i2_context_builder import ContextBuilder
from vamos_core.orange_core.i5_decision_engine import DecisionEngine
from vamos_core.orange_core.i6_self_check import SelfCheckEngine, risk_thresholds
from vamos_core.orange_core.pipeline import run_pipeline
from vamos_core.schemas.contracts import DecisionSchema, IntentFrame


class _FakeMsg:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeLLM:
    """Ollama 모킹 — intent 파싱 프롬프트엔 JSON, 그 외엔 답변 텍스트 (test_pipeline 동형)."""

    async def ainvoke(self, prompt: str) -> _FakeMsg:
        if "JSON 하나만 출력" in prompt:
            return _FakeMsg(json.dumps({
                "user_goal": prompt.rsplit("사용자 입력:", 1)[-1].strip(),
                "task_type": "explain", "domain_priority": "P0",
                "safety_sensitive": False, "approval_maybe_required": False,
                "cost_sensitive": False, "is_ambiguous": False,
                "missing_slots": [], "clarification_questions": [], "required_artifacts": [],
            }, ensure_ascii=False))
        return _FakeMsg("모킹 답변입니다.")


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def _intent(goal: str = "파이썬 코드 설명", priority: str = "P0") -> IntentFrame:
    return IntentFrame.model_validate(
        {
            "intent_id": f"int_{uuid.uuid4().hex[:8]}",
            "trace_id": new_trace_id(),
            "timestamp": datetime.now(UTC).isoformat(),
            "user_goal": goal,
            "task_type": "explain",
            "domain_hint": {"priority": priority, "candidates": []},
            "constraints": {"format_constraints": None, "must_include": [], "must_not_include": []},
            "risk_flags": {"safety_sensitive": False,
                           "approval_maybe_required": priority == "P2", "cost_sensitive": False},
            "ambiguity": {"is_ambiguous": False, "missing_slots": [],
                          "clarification_questions": []},
            "required_artifacts": [],
        }
    )


async def _decide(intent: IntentFrame) -> DecisionSchema:
    pack = await ContextBuilder().build_evidence(intent, intent.trace_id)
    return await DecisionEngine().decide(intent, pack, intent.trace_id)


def test_thresholds_from_config_lock():
    """§7.53-1 LOCK — 가변 임계값은 config [self_check] 단일 출처 (70/75/80)."""
    assert risk_thresholds() == {"P0": 70, "P1": 75, "P2": 80}


async def test_pass_normal_accept():
    """정상 ACCEPT + 산출 존재 → verdict PASS, score 1.0, retry 불필요."""
    d = await _decide(_intent())
    report = SelfCheckEngine().run_self_check(
        d, llm_response="답변 본문", failure_codes=[], trace_id=d.trace_id)
    assert report["verdict"] == "PASS"
    assert report["score"] == 1.0
    assert report["reasons"] == []
    assert report["retry_allowed"] is False
    assert report["_fallback_id"] is None


async def test_empty_output_for_accept_degrades():
    """ACCEPT인데 산출 공백 → 감점(출력 정합 위반)."""
    d = await _decide(_intent())
    report = SelfCheckEngine().run_self_check(
        d, llm_response="", failure_codes=[], trace_id=d.trace_id)
    assert "output_empty_for_accept" in report["reasons"]
    assert report["score"] < 1.0


async def test_safety_violation_fail_deny_fallback():
    """감사에 POLICY_DENY → FAIL + FB_DENY_WITH_REASON 수렴 (02 §6.3 정본)."""
    d = await _decide(_intent())
    report = SelfCheckEngine().run_self_check(
        d, llm_response="x", failure_codes=["POLICY_DENY"], trace_id=d.trace_id)
    assert report["verdict"] == "FAIL"
    assert report["retry_allowed"] is True  # 1차 FAIL soft loop 표기
    assert report["_fallback_id"] == "FB_DENY_WITH_REASON"
    assert "safety_violation_in_audit" in report["reasons"]


async def test_p2_threshold_higher():
    """P2(approval_required) → 임계값 80(보수 상향)."""
    d = await _decide(_intent(priority="P2"))
    report = SelfCheckEngine().run_self_check(
        d, llm_response="x", failure_codes=[], trace_id=d.trace_id)
    assert report["_threshold"] == 80
    assert report["_risk"] == "P2"


async def test_conclusion_immutable():
    """단일결정 원칙 — I-6은 self_check 보고서만 생성, Decision.conclusion 변경 금지."""
    d = await _decide(_intent())
    before = d.conclusion
    SelfCheckEngine().run_self_check(d, llm_response="x", failure_codes=[], trace_id=d.trace_id)
    assert d.conclusion == before


async def test_pipeline_self_check_activated():
    """E2E 배선 — verify 노드 I-6 활성화: self_check 실판정 + SelfCheckGate SKIP 탈피."""
    final = await run_pipeline("파이썬 데코레이터를 설명해줘", llm=_FakeLLM())
    env = final["response_envelope"]
    assert env is not None
    sc = env.self_check
    assert set(sc) == {"score", "verdict", "reasons", "retry_allowed"}  # 5필드 계약(내부힌트 제외)
    assert sc["verdict"] in ("PASS", "WARN", "FAIL")
    # SelfCheckGate reasoning_trace 가 SKIP에서 실판정으로 갱신됨
    trace = final["decision"].gates["reasoning_trace"]
    self_gate = next(t for t in trace if t["gate"] == "SelfCheckGate")
    assert self_gate["result"] in ("PASS", "FAIL")
    assert self_gate["result"] != "SKIP"
