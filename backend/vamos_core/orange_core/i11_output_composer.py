"""I-11 Output Composer (출력 생성기) — ResponseEnvelope.answer 합성 (deliver 인라인 대체).

정본: D2.0-01 §5.6 (I-11 CORE, V1:ON). ⚠️ D2.0-02 0:1 GAP — "Output Composer 설계는 본 문서에
별도 커버 없음"(§4.0). 따라서 신규 최소 구현: deliver_node 에 흩어진 답변 합성 책임을 모듈로
집약 + output_spec 준수 점검 + next_actions 결정론 도출.

책임: confidence_level/conclusion + llm_response + self_check → answer{summary, details,
next_actions}(CLAUDE.md §12 ResponseEnvelope.answer 3필드). DEC-010 행동 분기 문구는 본 모듈
단일 출처. 단일결정 원칙: 합성만, 결론·게이트 변경 금지. 6-3 범위: 텍스트 합성(결정론) —
멀티모달 렌더링은 I-13, TTS/화면공유 등 S7B-015/017 = V2.

이벤트: ui.cli.output.streamed(registries 정본). output_spec 위반 시 OC_I4_OUTPUT_SPEC_VIOLATION
+ FB_OUTPUT_REFORMAT(정본 재사용 — I-11 전용 코드 미등록, [LEGACY] 추가 안 함).
"""

from __future__ import annotations

from typing import Any

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import DecisionSchema

#: DEC-010 행동 분기 사용자 문구 (PHASE3-DEC-010 표) — 단일 출처
LEVEL_MESSAGES: dict[str, str] = {
    "MEDIUM": "⚠ 확신도 보통",
    "LOW": "⚠ 불확실한 답변입니다. 직접 확인을 권장합니다",
    "REFUSE": "판단이 어렵습니다. 더 많은 정보가 필요합니다",
}


class OutputComposer:
    """compose(decision, llm_response, self_check) -> answer(3필드). 결정론 텍스트 합성."""

    @staticmethod
    def _next_actions(decision: DecisionSchema, self_check: dict[str, Any] | None) -> list[str]:
        """결정론 후속 행동 도출 (S7B-031 LLM 제안형 = V2, 본 모듈은 규칙 기반)."""
        actions: list[str] = []
        if decision.conclusion == "HOLD":
            actions.append("P2 작업 승인 여부를 확인하세요.")
        elif decision.conclusion in ("REJECT", "ESCALATE") or decision.confidence_level == "REFUSE":
            actions.append("요청을 구체화하거나 추가 정보를 제공하세요.")
        if self_check is not None and self_check.get("verdict") == "FAIL":
            actions.append("자기검증 미통과 — 결과를 직접 검토하세요.")
        return actions

    def compose(
        self,
        decision: DecisionSchema,
        llm_response: str | None,
        self_check: dict[str, Any] | None = None,
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """answer{summary, details, next_actions} 합성 — DEC-010 분기 문구 적용."""
        level = decision.confidence_level
        if llm_response and level != "REFUSE":
            prefix = LEVEL_MESSAGES.get(level)
            summary = f"{prefix}\n{llm_response}" if prefix else llm_response
        elif decision.conclusion == "HOLD":
            summary = "승인 대기(HOLD) — P2 작업은 명시적 승인이 필요합니다."
        else:
            summary = LEVEL_MESSAGES["REFUSE"] if level == "REFUSE" else "요청이 거부되었습니다."

        answer = {
            "summary": summary,
            "details": llm_response or "",
            "next_actions": self._next_actions(decision, self_check),
        }
        if trace_id is not None:
            log_event("ui.cli.output.streamed", producer="I-11",
                      payload={"decision_id": decision.decision_id,
                               "confidence_level": level, "has_response": bool(llm_response),
                               "next_actions": len(answer["next_actions"])},
                      trace_id=trace_id)
        return answer
