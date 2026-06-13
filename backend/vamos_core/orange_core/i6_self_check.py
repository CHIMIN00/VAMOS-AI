"""I-6 Self-check Engine (자기검증 엔진) — verify 노드 활성화 (V0 스텁 대체).

정본: D2.0-01 §5.6 (I-6 CORE, V1:ON) + D2.0-02 §7.51~7.53 (목적/인터페이스/임계값 LOCK)
+ §8.1 SelfCheckGate(5-Gate 5번째) + ResponseEnvelope.self_check 5필드(CLAUDE.md §12).

핵심(§7.53-1 LOCK): 가변 임계값(위험도 P0≥70 / P1≥75 / P2≥80, 0~100 내부 척도) — "관문은 고정,
임계값은 가변". FAIL 처리(§7.53-2 LOCK): 1차 FAIL → 자동 Soft loop 1회(retry_allowed) → 재평가,
2회 연속 FAIL → 게이트 결과 우선 수렴(fallback: FB_REQUIRE_APPROVAL/FB_OUTPUT_MINIMAL/
FB_DENY_WITH_REASON — 02 §6.3 정본만). Self-evo 제안은 V1 비활성(I-12/I-18/I-21 = V2/V3).

검증 4종(V1 결정론 — LLM 심판/메타모픽 = 6-4): 출력 정합 / 근거-결론 정합 / 안전(Non-goal·
POLICY_DENY) / 자기모순(confidence_level↔conclusion). 단일결정 원칙: S3 후 conclusion 불변 —
본 엔진은 self_check 보고서 생성만, Decision 결론 변경 금지(DEC-010).

배선: pipeline.verify_node 에서 호출, SelfCheckGate reasoning_trace(SKIP→PASS/FAIL) 갱신 +
self_check 보고서를 deliver_node 로 전달. 직선 5노드 토폴로지 무변경(soft loop = retry_allowed
플래그, 신규 엣지 없음). 이벤트: ui.main.selfcheck.{started,passed,failed}(registries 정본).
"""

from __future__ import annotations

from typing import Any, Literal, cast

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import DecisionSchema

#: §7.53-1 LOCK — 위험도 기반 가변 PASS 임계값 (0~100 내부 척도)
RISK_THRESHOLDS: dict[str, int] = {"P0": 70, "P1": 75, "P2": 80}

#: WARN 밴드 폭 — 임계값 미만 ~ (임계값-WARN_BAND)는 WARN(비차단), 그 아래 FAIL
WARN_BAND = 10

SelfVerdict = Literal["PASS", "WARN", "FAIL"]


class SelfCheckEngine:
    """run_self_check(decision, snapshot) -> self_check 보고서(5필드 계약).

    propose_self_evo 는 V1 비활성(자동 적용 금지·제안만, I-12/I-18/I-21 = V2/V3) — 미구현 슬롯.
    """

    @staticmethod
    def _risk_of(decision: DecisionSchema) -> str:
        """Decision routing/approval 에서 위험도 도출 — approval_required면 보수적으로 상향."""
        risk = "P0"
        gates = decision.gates or {}
        trace = gates.get("reasoning_trace", []) if isinstance(gates, dict) else []
        for entry in trace:
            if isinstance(entry, dict) and entry.get("gate") == "ApprovalGate":
                detail = entry.get("detail", {})
                cand = detail.get("risk_level")
                if cand in RISK_THRESHOLDS:
                    risk = cast(str, cand)
        if decision.approval_required and risk == "P0":
            risk = "P2"
        return risk

    def run_self_check(
        self,
        decision: DecisionSchema,
        *,
        llm_response: str | None,
        failure_codes: list[str],
        trace_id: str,
    ) -> dict[str, Any]:
        """결정론 4-검증 → score(0~1)/verdict/reasons/retry_allowed + 수렴 fallback_id.

        S3 후 호출(conclusion locked) — 본 메서드는 conclusion 을 변경하지 않는다(DEC-010).
        """
        log_event("ui.main.selfcheck.started", producer="I-6",
                  payload={"decision_id": decision.decision_id}, trace_id=trace_id)

        reasons: list[str] = []
        raw = 100  # 0~100 내부 척도, 검증 실패 시 감점

        # ① 출력 정합 — ACCEPT면 비어있지 않은 산출 필요
        if decision.conclusion == "ACCEPT" and not (llm_response and llm_response.strip()):
            raw -= 40
            reasons.append("output_empty_for_accept")

        # ② 근거-결론 정합 — ACCEPT인데 EvidenceGate insufficient면 감점
        gates = decision.gates or {}
        evidence_gate = gates.get("evidence_gate") if isinstance(gates, dict) else None
        if decision.conclusion == "ACCEPT" and evidence_gate == "insufficient":
            raw -= 30
            reasons.append("evidence_conclusion_mismatch")

        # ③ 안전 — POLICY_DENY/Non-goal 계열 실패코드 존재 시 즉시 FAIL 수준 감점
        unsafe = {"POLICY_DENY", "OC_ERR_NONGOAL", "PII_LONGTERM_DENIED"}
        if unsafe & set(failure_codes):
            raw -= 60
            reasons.append("safety_violation_in_audit")

        # ④ 자기모순 — confidence_level ↔ conclusion 정합 (HIGH인데 REJECT 등)
        if decision.confidence_level == "HIGH" and decision.conclusion in ("REJECT", "ESCALATE"):
            raw -= 20
            reasons.append("confidence_conclusion_contradiction")
        if decision.confidence_level == "REFUSE" and decision.conclusion == "ACCEPT":
            raw -= 20
            reasons.append("refuse_level_but_accept")

        raw = max(0, raw)
        risk = self._risk_of(decision)
        threshold = RISK_THRESHOLDS[risk]
        verdict: SelfVerdict = (
            "PASS" if raw >= threshold
            else "WARN" if raw >= threshold - WARN_BAND
            else "FAIL"
        )

        # §7.53-2 — 1차 FAIL은 Soft loop 1회 허용(retry_allowed). 토폴로지 LOCK이라 실제 재실행
        # 엣지는 추가하지 않음 — 플래그로 표기(전체 루프 배선은 6-3 범위 외, 직선 그래프 보존).
        retry_allowed = verdict == "FAIL"

        # 2회 연속 FAIL 수렴 fallback (게이트 결과 우선) — 02 §6.3 정본 fallback_id 만
        fallback_id: str | None = None
        if verdict == "FAIL":
            if "safety_violation_in_audit" in reasons:
                fallback_id = "FB_DENY_WITH_REASON"
            elif decision.approval_required or risk == "P2":
                fallback_id = "FB_REQUIRE_APPROVAL"
            else:
                fallback_id = "FB_OUTPUT_MINIMAL"

        report: dict[str, Any] = {
            "score": round(raw / 100.0, 4),  # 계약: 0~1
            "verdict": verdict,
            "reasons": reasons,
            "retry_allowed": retry_allowed,
        }

        event = "ui.main.selfcheck.passed" if verdict != "FAIL" else "ui.main.selfcheck.failed"
        log_event(event, producer="I-6",
                  payload={"decision_id": decision.decision_id, "verdict": verdict,
                           "score": report["score"], "risk": risk, "threshold": threshold,
                           "fallback_id": fallback_id},
                  trace_id=trace_id,
                  severity="warn" if verdict == "FAIL" else "info")
        return {**report, "_risk": risk, "_threshold": threshold, "_fallback_id": fallback_id}
