"""I-20 Failure/Fallback Manager (V0 stub) — FailureCode→Fallback 매핑 + 로그만.

정본: PART2 V0-STEP-4 #8 — FailureReport 수신 → FailureCodeRegistry 매핑 →
FallbackRegistry 대응 전략 조회 → 로그 기록 + 기본 에러 메시지 반환 (V0 실행 없음).
매핑은 D2.0-02 I-모듈 상세 절의 failure↔fallback links 기반 V0 서브셋 —
전수 매핑 정본화는 V1 (미등재 코드는 FB_DENY_WITH_REASON 안전 기본값).
"""

from __future__ import annotations

from typing import Any

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import FailureReport
from vamos_core.schemas.registries import is_valid_failure_code, is_valid_fallback_id

#: D2.0-02 I-1/I-2/I-5 상세 절 fallback 목록 기반 V0 매핑
FAILURE_TO_FALLBACK: dict[str, str] = {
    "OC_I1_PARSE_FAIL": "FB_INTENT_HEURISTIC_PARSE",
    "OC_I1_AMBIGUOUS_UNRESOLVED": "FB_ASK_CLARIFICATION",
    "OC_I2_RAG_NO_SOURCE": "FB_RAG_RETRY_EXPAND",
    "OC_I2_EVIDENCE_QOD_LOW": "FB_RAG_SWITCH_SOURCE",
    "OC_I2_SOURCE_POLICY_BLOCK": "FB_RAG_SWITCH_SOURCE",
    "OC_I2_TIMEOUT": "FB_RAG_RETRY_EXPAND",
    "OC_I5_POLICY_BLOCK": "FB_DENY_WITH_REASON",
    "OC_I5_APPROVAL_REQUIRED": "FB_REQUIRE_APPROVAL",
    "OC_I5_COST_OVER_BUDGET": "FB_COST_DOWNSHIFT",
    "OC_I5_EVIDENCE_INSUFFICIENT": "FB_RAG_RETRY_EXPAND",
    "OC_I5_ROUTE_NOT_FOUND": "FB_ROUTE_SAFE_NODE",
    "OC_ERR_NONGOAL": "FB_DENY_WITH_REASON",
    "POLICY_DENY": "FB_DENY_WITH_REASON",
    "GT_ERR_COST_LIMIT": "FB_COST_DOWNSHIFT",
}

_DEFAULT_FALLBACK = "FB_DENY_WITH_REASON"
_DEFAULT_MESSAGE = "요청을 처리하지 못했습니다. 입력을 확인하거나 다시 시도해 주세요."


class FailureManager:
    """handle_failure(report, failure_code) -> 매핑 결과 + 기본 에러 메시지 (V0: 로그만)."""

    async def handle_failure(
        self,
        report: FailureReport,
        failure_code: str,
        trace_id: str,
    ) -> dict[str, Any]:
        report = FailureReport.model_validate(report.model_dump())  # 경계 검증 의무
        if not is_valid_failure_code(failure_code):
            raise ValueError(f"미등록 failure_code: {failure_code!r} (registries — 4-4 연동)")
        fallback_id = FAILURE_TO_FALLBACK.get(failure_code, _DEFAULT_FALLBACK)
        if not is_valid_fallback_id(fallback_id):  # 매핑표 자체 무결성 (registries 검증)
            raise ValueError(f"미등록 fallback_id: {fallback_id!r}")
        log_event(
            "oc.deny.blocked",
            producer="I-20",
            payload={
                "failure_cause": report.failure_cause,
                "evidence_gap": report.evidence_gap,
                "improvement_hint": report.improvement_hint,
                "v0_action": "log_only",
            },
            trace_id=trace_id,
            severity="error",
            links={"failure_code": [failure_code], "fallback_id": [fallback_id]},
        )
        return {
            "failure_code": failure_code,
            "fallback_id": fallback_id,
            "message": _DEFAULT_MESSAGE,
        }
