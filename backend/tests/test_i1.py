"""I-1 Intent Detector 검증 (V0-STEP-4 Stage Gate #1/#2/#11 일부)."""

from __future__ import annotations

import json

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i1_intent_detector import IntentDetector
from vamos_core.schemas.contracts import FailureReport, IntentFrame


class _FakeMsg:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeLLM:
    def __init__(self, content: str) -> None:
        self._content = content
        self.prompts: list[str] = []

    async def ainvoke(self, prompt: str) -> _FakeMsg:
        self.prompts.append(prompt)
        return _FakeMsg(self._content)


class _BrokenLLM:
    async def ainvoke(self, prompt: str) -> _FakeMsg:
        return _FakeMsg("JSON 아님 — 파싱 불가 응답")


_GOOD_JSON = json.dumps(
    {
        "user_goal": "파이썬 코드 설명",
        "task_type": "explain",
        "domain_priority": "P0",
        "safety_sensitive": False,
        "approval_maybe_required": False,
        "cost_sensitive": False,
        "is_ambiguous": False,
        "missing_slots": [],
        "clarification_questions": [],
        "required_artifacts": ["code"],
    },
    ensure_ascii=False,
)


@pytest.fixture(autouse=True)
def _log_isolation(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield tmp_path
    reset_config_cache()


async def test_intent_frame_10_fields(_log_isolation):
    """Stage Gate STEP-4 #1: 텍스트 입력 → IntentFrame 10필드."""
    frame, failure = await IntentDetector(llm=_FakeLLM(_GOOD_JSON)).parse_intent(
        "이 파이썬 코드를 설명해줘", trace_id=new_trace_id()
    )
    assert failure is None
    assert isinstance(frame, IntentFrame)
    assert len(IntentFrame.model_fields) == 10  # D2.0-02 I-1 상세 분모
    assert frame.task_type == "explain"
    assert frame.user_goal == "파이썬 코드 설명"
    assert frame.required_artifacts == ["code"]


async def test_i1_state_transitions_logged(_log_isolation):
    """Stage Gate STEP-4 #2: I1_S0_RAW → S1_PARSING → S3_READY → S4_EMITTED 로그."""
    tid = new_trace_id()
    await IntentDetector(llm=_FakeLLM(_GOOD_JSON)).parse_intent("hello", trace_id=tid)
    log_file = next(iter((_log_isolation / "logs").glob("vamos_*.jsonl")))
    lines = [json.loads(line) for line in log_file.read_text(encoding="utf-8").splitlines()]
    states = [r["payload"].get("state") for r in lines if r["links"]["trace_id"] == tid]
    assert states == [
        "I1_S0_RAW->I1_S1_PARSING",
        "I1_S1_PARSING->I1_S3_READY",
        "I1_S3_READY->I1_S4_EMITTED",
    ]


async def test_parse_failure_returns_fallback_and_report(_log_isolation):
    """파싱 실패 → FailureReport + fallback intent='unknown' (Stage Gate #11 연계)."""
    frame, failure = await IntentDetector(llm=_BrokenLLM()).parse_intent(
        "???", trace_id=new_trace_id()
    )
    assert isinstance(failure, FailureReport)
    assert "OC_I1_PARSE_FAIL" in failure.failure_cause
    assert frame.domain_hint.get("intent") == "unknown"
    assert frame.task_type == "etc"  # contracts Literal 보존 — unknown은 domain_hint 표기
    assert frame.ambiguity["is_ambiguous"] is True


async def test_invalid_task_type_coerced_to_etc(_log_isolation):
    bad = _GOOD_JSON.replace('"explain"', '"hacking"')
    frame, failure = await IntentDetector(llm=_FakeLLM(bad)).parse_intent(
        "x", trace_id=new_trace_id()
    )
    assert failure is None
    assert frame.task_type == "etc"


async def test_clarification_questions_capped_at_3(_log_isolation):
    """D2.0-02 I-1 T2: 질문 0..3 상한."""
    data = json.loads(_GOOD_JSON)
    data["clarification_questions"] = ["q1", "q2", "q3", "q4", "q5"]
    frame, _ = await IntentDetector(llm=_FakeLLM(json.dumps(data))).parse_intent(
        "x", trace_id=new_trace_id()
    )
    assert len(frame.ambiguity["clarification_questions"]) == 3
