"""I-11 Output Composer 검증 — answer 합성 (D2.0-01 §5.6, D2.0-02 0:1 GAP 신규 최소).

DEC-010 분기 문구 단일 출처 · next_actions 결정론 · self_check FAIL 반영 · conclusion 무변경.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i2_context_builder import ContextBuilder
from vamos_core.orange_core.i5_decision_engine import DecisionEngine
from vamos_core.orange_core.i11_output_composer import LEVEL_MESSAGES, OutputComposer
from vamos_core.schemas.contracts import DecisionSchema, IntentFrame


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def _intent(goal: str = "설명해줘", priority: str = "P0") -> IntentFrame:
    return IntentFrame.model_validate({
        "intent_id": f"int_{uuid.uuid4().hex[:8]}", "trace_id": new_trace_id(),
        "timestamp": datetime.now(UTC).isoformat(), "user_goal": goal, "task_type": "explain",
        "domain_hint": {"priority": priority, "candidates": []},
        "constraints": {"format_constraints": None, "must_include": [], "must_not_include": []},
        "risk_flags": {"safety_sensitive": False, "approval_maybe_required": priority == "P2",
                       "cost_sensitive": False},
        "ambiguity": {"is_ambiguous": False, "missing_slots": [], "clarification_questions": []},
        "required_artifacts": [],
    })


async def _decide(intent: IntentFrame) -> DecisionSchema:
    pack = await ContextBuilder().build_evidence(intent, intent.trace_id)
    return await DecisionEngine().decide(intent, pack, intent.trace_id)


async def test_compose_accept_high_no_prefix():
    """ACCEPT/HIGH + 응답 → summary=응답(접두 없음), details, next_actions 빈."""
    d = await _decide(_intent())
    a = OutputComposer().compose(d, "데코레이터는 함수를 감싸는 함수입니다.")
    assert a["summary"] == "데코레이터는 함수를 감싸는 함수입니다."
    assert a["details"] == "데코레이터는 함수를 감싸는 함수입니다."
    assert a["next_actions"] == []
    assert set(a) == {"summary", "details", "next_actions"}


async def test_compose_hold_p2_next_action():
    """P2 HOLD → 승인 대기 문구 + next_actions 승인 안내."""
    d = await _decide(_intent(priority="P2"))
    a = OutputComposer().compose(d, None)
    assert "승인 대기(HOLD)" in a["summary"]
    assert any("승인" in x for x in a["next_actions"])


async def test_compose_refuse_message_and_action():
    """non-goal REJECT/REFUSE → REFUSE 문구 + 구체화 안내."""
    d = await _decide(_intent(goal="내 계좌에서 A주식 100주 매수해줘"))
    a = OutputComposer().compose(d, None)
    assert a["summary"] == LEVEL_MESSAGES["REFUSE"]
    assert any("추가 정보" in x for x in a["next_actions"])


async def test_compose_self_check_fail_adds_action():
    """self_check FAIL → '자기검증 미통과' 후속 안내 추가."""
    d = await _decide(_intent())
    a = OutputComposer().compose(d, "답변", {"verdict": "FAIL", "score": 0.4})
    assert any("자기검증" in x for x in a["next_actions"])


async def test_compose_conclusion_immutable():
    """합성만 — Decision.conclusion 변경 금지."""
    d = await _decide(_intent())
    before = d.conclusion
    OutputComposer().compose(d, "답변", trace_id=d.trace_id)
    assert d.conclusion == before
