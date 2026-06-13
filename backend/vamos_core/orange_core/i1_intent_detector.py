"""I-1 Intent Detector — 사용자 입력 → IntentFrame (V0 최소 구현).

정본: D2.0-02 I-1 상세(L2620~) + PART2 V0-STEP-4 #1.
상태: I1_S0_RAW → I1_S1_PARSING → I1_S3_READY → I1_S4_EMITTED
  (S2=AMBIGUOUS는 V1+ 전용 — skip 정상, D2.0-02 §7.5)
파싱 실패 시 FailureReport 생성 + fallback intent="unknown"
  (FB_INTENT_HEURISTIC_PARSE — 최소 IntentFrame으로 다운시프트).
"""

from __future__ import annotations

import json
import uuid
from datetime import UTC, datetime
from typing import Any, Protocol, cast

from vamos_core.infra.config_loader import get_config
from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import FailureReport, IntentFrame

_TASK_TYPES = ("explain", "plan", "code", "research", "summarize", "design", "debug", "etc")

_PARSE_PROMPT = """다음 사용자 입력을 분석하여 JSON 하나만 출력하세요 (설명 금지).
필드: user_goal(문자열), task_type({task_types} 중 1),
domain_priority(P0|P1|P2), safety_sensitive(bool), approval_maybe_required(bool),
cost_sensitive(bool), is_ambiguous(bool), missing_slots(문자열 배열),
clarification_questions(문자열 배열, 최대 3),
required_artifacts(문자열 배열 — doc|pdf|ppt|sheet|code|diagram|etc)

사용자 입력: {user_input}"""


class ChatModel(Protocol):
    """LLM 최소 인터페이스 (테스트 주입용 — 실구현 ChatOllama)."""

    async def ainvoke(self, prompt: str) -> Any: ...  # returns .content


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


class IntentDetector:
    """parse_intent(user_input, ...) -> IntentFrame (D2.0-02 I-1 Interface)."""

    def __init__(self, llm: ChatModel | None = None) -> None:
        self._llm = llm

    def _get_llm(self) -> ChatModel:
        if self._llm is None:
            # Ollama 호출은 langchain-community ChatOllama (PART2 규칙) · 모델은 config 유래
            from langchain_community.chat_models import ChatOllama

            mini = get_config().llm.mini_model.removeprefix("ollama/")
            self._llm = cast(ChatModel,
                             ChatOllama(model=mini, temperature=get_config().llm.temperature))
        return self._llm

    async def parse_intent(
        self,
        user_input: str,
        trace_id: str,
        session_context: str | None = None,
        project_hint: str | None = None,
    ) -> tuple[IntentFrame, FailureReport | None]:
        """I-1 최소 인터페이스 — 실패 시 (fallback IntentFrame, FailureReport) 반환."""
        # I1_S0_RAW → I1_S1_PARSING
        log_event(
            "oc.i1.parse.started",
            producer="I-1",
            payload={
                "state": "I1_S0_RAW->I1_S1_PARSING",
                "input_meta": {"text_len": len(user_input)},
                "project_hint": project_hint,
            },
            trace_id=trace_id,
        )
        try:
            raw = await self._get_llm().ainvoke(
                _PARSE_PROMPT.format(task_types="|".join(_TASK_TYPES), user_input=user_input)
            )
            frame = self._build_frame(user_input, trace_id, self._extract_json(raw.content))
        except Exception as exc:  # noqa: BLE001 — 파싱 실패는 전부 fallback 경로 (PART2 #1)
            log_event(
                "oc.i1.parse.failed",
                producer="I-1",
                payload={"error_class": type(exc).__name__, "error_message": str(exc)[:200]},
                trace_id=trace_id,
                severity="error",
                links={"failure_code": ["OC_I1_PARSE_FAIL"],
                       "fallback_id": ["FB_INTENT_HEURISTIC_PARSE"]},
            )
            report = FailureReport(
                failure_cause=f"OC_I1_PARSE_FAIL: {type(exc).__name__}",
                evidence_gap="intent 파싱 불능 — LLM 응답 비정형 또는 호출 실패",
                risk_detected={},
                improvement_hint="FB_INTENT_HEURISTIC_PARSE 약식 파싱 적용",
            )
            return self._fallback_frame(user_input, trace_id), report
        # I1_S1_PARSING → I1_S3_READY
        log_event(
            "oc.i1.intent.parsed",
            producer="I-1",
            payload={
                "state": "I1_S1_PARSING->I1_S3_READY",
                "intent_id": frame.intent_id,
                "task_type": frame.task_type,
                "domain_hint": frame.domain_hint,
                "risk_flags": frame.risk_flags,
            },
            trace_id=trace_id,
        )
        # I1_S3_READY → I1_S4_EMITTED
        log_event(
            "oc.i1.intent.parsed",
            producer="I-1",
            payload={"state": "I1_S3_READY->I1_S4_EMITTED", "intent_id": frame.intent_id},
            trace_id=trace_id,
        )
        return frame, None

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:
        start, end = text.find("{"), text.rfind("}")
        if start < 0 or end <= start:
            raise ValueError("LLM 응답에 JSON 객체 없음")
        return cast("dict[str, Any]", json.loads(text[start : end + 1]))

    @staticmethod
    def _build_frame(user_input: str, trace_id: str, d: dict[str, Any]) -> IntentFrame:
        task_type = d.get("task_type") if d.get("task_type") in _TASK_TYPES else "etc"
        priority = d.get("domain_priority")
        if priority not in ("P0", "P1", "P2"):
            priority = "P0"
        return IntentFrame.model_validate(  # 경계 검증 의무 (DEC-004 전이 규칙 3)
            {
                "intent_id": f"int_{uuid.uuid4().hex[:12]}",
                "trace_id": trace_id,
                "timestamp": _now_iso(),
                "user_goal": str(d.get("user_goal") or user_input),
                "task_type": task_type,
                "domain_hint": {"priority": priority, "candidates": []},
                "constraints": {
                    "format_constraints": d.get("format_constraints"),
                    "must_include": [],
                    "must_not_include": [],
                },
                "risk_flags": {
                    "safety_sensitive": bool(d.get("safety_sensitive", False)),
                    "approval_maybe_required": bool(d.get("approval_maybe_required", False))
                    or priority == "P2",
                    "cost_sensitive": bool(d.get("cost_sensitive", False)),
                },
                "ambiguity": {
                    "is_ambiguous": bool(d.get("is_ambiguous", False)),
                    "missing_slots": list(d.get("missing_slots") or []),
                    "clarification_questions": list(d.get("clarification_questions") or [])[:3],
                },
                "required_artifacts": list(d.get("required_artifacts") or []),
            }
        )

    @staticmethod
    def _fallback_frame(user_input: str, trace_id: str) -> IntentFrame:
        """FB_INTENT_HEURISTIC_PARSE — 최소 IntentFrame. intent="unknown"은 domain_hint에 표기
        (task_type Literal에 unknown 부재 — contracts 정본 enum 보존)."""
        return IntentFrame.model_validate(
            {
                "intent_id": f"int_{uuid.uuid4().hex[:12]}",
                "trace_id": trace_id,
                "timestamp": _now_iso(),
                "user_goal": user_input,
                "task_type": "etc",
                "domain_hint": {"priority": "P0", "candidates": [], "intent": "unknown"},
                "constraints": {"format_constraints": None,
                                "must_include": [], "must_not_include": []},
                "risk_flags": {"safety_sensitive": False,
                               "approval_maybe_required": False, "cost_sensitive": False},
                "ambiguity": {"is_ambiguous": True, "missing_slots": ["intent"],
                              "clarification_questions": []},
                "required_artifacts": [],
            }
        )
