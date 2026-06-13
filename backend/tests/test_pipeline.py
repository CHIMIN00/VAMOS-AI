"""pipeline E2E 검증 (V0-STEP-4 Stage Gate #8/#9 + deny 조기 종료 + A21 L3)."""

from __future__ import annotations

import json

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.orange_core.pipeline import run_pipeline
from vamos_core.safety.never_auto import NEVER_AUTO, detect_never_auto, is_never_auto
from vamos_core.schemas.contracts import ResponseEnvelope


class _FakeMsg:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeLLM:
    """intent 파싱 프롬프트엔 JSON, 그 외엔 답변 텍스트 반환 (Ollama 모킹)."""

    def __init__(self, priority: str = "P0", answer: str = "모킹 답변입니다.") -> None:
        self._priority = priority
        self._answer = answer

    async def ainvoke(self, prompt: str) -> _FakeMsg:
        if "JSON 하나만 출력" in prompt:
            return _FakeMsg(json.dumps({
                "user_goal": prompt.rsplit("사용자 입력:", 1)[-1].strip(),
                "task_type": "explain",
                "domain_priority": self._priority,
                "safety_sensitive": False,
                "approval_maybe_required": self._priority == "P2",
                "cost_sensitive": False,
                "is_ambiguous": False,
                "missing_slots": [],
                "clarification_questions": [],
                "required_artifacts": [],
            }, ensure_ascii=False))
        return _FakeMsg(self._answer)


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield tmp_path
    reset_config_cache()


async def test_e2e_full_flow(_env):
    """Stage Gate #8/#9: intake→plan→execute→verify→deliver → ResponseEnvelope 5필드."""
    state = await run_pipeline("파이썬 데코레이터를 설명해줘", llm=_FakeLLM())
    env = state["response_envelope"]
    assert isinstance(env, ResponseEnvelope)
    assert len(ResponseEnvelope.model_fields) == 5  # CLAUDE.md §12 LOCK
    assert state["pipeline_state"] == "S8_DONE"
    assert state["decision"].locked is True
    assert state["decision"].confidence_level == "HIGH"
    assert state["llm_response"] == "모킹 답변입니다."
    assert env.answer["summary"] == "모킹 답변입니다."  # HIGH — 경고 prefix 없음
    assert env.decision_ref["decision_id"] == state["decision"].decision_id


async def test_e2e_state_transitions_logged(_env):
    """S0_RECEIVED~S8_DONE 전이 기록 (D2.0-02 §2.2)."""
    state = await run_pipeline("hello", llm=_FakeLLM())
    log_file = next(iter((_env / "logs").glob("vamos_*.jsonl")))
    lines = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]
    tid = state["trace_id"]
    stages = [r["payload"]["pipeline_state"] for r in lines
              if r["event_type"] == "wf.stage.enter" and r["links"]["trace_id"] == tid]
    assert stages == ["S0_RECEIVED", "S2_EVIDENCE_READY", "S4_EXECUTING",
                      "S6_SELF_CHECKED", "S7_MEMORY_COMMITTED"]
    assert state["pipeline_state"] == "S8_DONE"
    # 전 로그 trace_id 일관성
    assert all(r["links"]["trace_id"] == tid for r in lines if tid == r["links"]["trace_id"])


async def test_gate_deny_early_exit(_env):
    """Gate deny → LLM 미호출 조기 종료 + 거부 응답 (직선 토폴로지 보존)."""
    state = await run_pipeline("내 계좌에서 A주식 100주 매수해줘", llm=_FakeLLM())
    assert state["decision"].conclusion == "REJECT"
    assert state["decision"].policy_gate == "block"
    assert state["llm_response"] is None  # 조기 종료 — LLM 미호출
    assert state["decision"].confidence_level == "REFUSE"
    assert "판단이 어렵습니다" in state["response_envelope"].answer["summary"]


async def test_p2_hold_early_exit(_env):
    state = await run_pipeline("P2 작업 실행", llm=_FakeLLM(priority="P2"))
    assert state["decision"].conclusion == "HOLD"
    assert state["llm_response"] is None
    assert "승인 대기" in state["response_envelope"].answer["summary"]


async def test_never_auto_layer3_blocks(_env):
    """A21 Defense Layer 3 — NEVER_AUTO는 게이트 통과와 무관하게 실행 차단 (DEC-008)."""
    state = await run_pipeline("비용 상한 변경해줘", llm=_FakeLLM())
    assert state["llm_response"] is None  # L3 단독 차단
    assert "POLICY_DENY" in state["response_envelope"].audit["failure_codes"]
    assert "FB_DENY_WITH_REASON" in state["response_envelope"].audit["fallback_ids"]


def test_never_auto_frozenset_verbatim():
    """SDAR §5.1 L594~603 RA_NEVER_01~10 전사 — frozenset 10항목 (L3 완전체)."""
    assert isinstance(NEVER_AUTO, frozenset)
    assert NEVER_AUTO == frozenset({
        "modify_safety_rules", "change_cost_ceiling", "alter_approval_flow",
        "modify_non_goals", "change_audit_format", "alter_data_retention",
        "modify_user_consent", "escalate_own_privilege", "disable_guardrails",
        "bypass_gate",
    })
    assert is_never_auto("bypass_gate")
    assert not is_never_auto("rebuild_vector_index")  # RA_014 — 자동 허용군
    assert detect_never_auto("게이트 우회해서 실행해") == "bypass_gate"
    assert detect_never_auto("날씨 알려줘") is None


async def test_selfcheck_skip_to_pass_in_envelope(_env):
    """V1(P6-1b): verify 노드 I-6 활성화 — SelfCheck SKIP→실판정(PASS) envelope 반영."""
    state = await run_pipeline("설명해줘", llm=_FakeLLM())
    trace = state["response_envelope"].decision_ref["gates"]["reasoning_trace"]
    self_check = next(t for t in trace if t["gate"] == "SelfCheckGate")
    assert self_check["result"] == "PASS"
    assert self_check["detail"]["verdict"] == "PASS"  # I-6 실판정 (v0_stub 대체)
    assert "v0_stub" not in self_check["detail"]
    # 결론 불변 (S3 후 단일결정 원칙)
    assert state["decision"].conclusion == "ACCEPT"


async def test_cost_usage_recorded(_env):
    """I-9 연동 — 실행 후 cost_usage.jsonl 기록 (날짜/모델/토큰/추정비용)."""
    await run_pipeline("토큰 기록 테스트", llm=_FakeLLM())
    usage = (_env / "logs" / "cost_usage.jsonl").read_text(encoding="utf-8").strip()
    entry = json.loads(usage.splitlines()[-1])
    assert {"date", "model", "input_tokens", "output_tokens", "cost_krw"} <= set(entry)
    assert entry["cost_krw"] == 0.0  # V0 로컬 Ollama = ₩0 (D10)
