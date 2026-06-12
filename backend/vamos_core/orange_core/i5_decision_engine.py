"""I-5 Condition & Decision Engine — 4-Gate 종합 → DecisionSchema(20필드, locked=true).

정본: D2.0-02 I-5 상세(L2874~)·§8.1 5-Gate + PART2 V0-STEP-4 #3 + PHASE3-DEC-001(순서)
+ PHASE4-DEC-010(A22 수용처 = Decision.gates["reasoning_trace"] + confidence V0 스텁).
V0 게이트: Policy→Approval→Cost→Evidence(plan 노드) + SelfCheck(verify 노드 — SKIP 예약 후
PASS 갱신). 게이트 결과 4종 전부 Decision에 기록. S3 후 결론(conclusion) 불변 —
reasoning_trace의 SelfCheck 갱신은 감사 기록 추가이며 결론 변경 아님 (DEC-010).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from vamos_core.infra.config_loader import get_config
from vamos_core.infra.logger import log_event
from vamos_core.orange_core.i8_policy_engine import PolicyEngine
from vamos_core.orange_core.i9_cost_manager import CostManager
from vamos_core.orange_core.i19_approval_manager import ApprovalManager
from vamos_core.schemas.contracts import DecisionSchema, EvidencePack, IntentFrame


class GateTraceEntry(BaseModel):
    """A22 reasoning_trace 엔트리 — PHASE3-DEC-009 스키마 (Decision.gates 내 수용, DEC-010)."""

    model_config = ConfigDict(extra="forbid")

    gate: Literal["PolicyGate", "ApprovalGate", "CostGate", "EvidenceGate", "SelfCheckGate"]
    result: Literal["PASS", "FAIL", "DOWNSHIFT", "DENY", "SKIP"]
    detail: dict[str, Any] = {}


def score_to_level(score: float) -> str:
    """confidence_level은 항상 score에서 단일 함수로 파생 (DEC-010 — 임계값 config LOCK 유래)."""
    cfg = get_config().confidence
    if score >= cfg.confidence_high_threshold:
        return "HIGH"
    if score >= cfg.confidence_medium_threshold:
        return "MEDIUM"
    if score >= cfg.confidence_refuse_threshold:
        return "LOW"
    return "REFUSE"


class DecisionEngine:
    """evaluate_gates → select_route → lock_decision (D2.0-02 I-5 최소 인터페이스)."""

    def __init__(
        self,
        policy: PolicyEngine | None = None,
        cost: CostManager | None = None,
        approval: ApprovalManager | None = None,
    ) -> None:
        self._policy = policy or PolicyEngine()
        self._cost = cost or CostManager()
        self._approval = approval or ApprovalManager()

    @staticmethod
    def _evidence_gate(evidence_pack: EvidencePack) -> bool:
        """EvidenceGate — V0 스텁: 항상 sufficient (PART2 L1023). V1: QoD/coverage 실평가."""
        return True

    async def decide(
        self,
        intent_frame: IntentFrame,
        evidence_pack: EvidencePack,
        trace_id: str,
        cost_usage_override: float | None = None,
    ) -> DecisionSchema:
        """4-Gate 평가 종합 → Decision(locked=true) 생성."""
        intent_frame = IntentFrame.model_validate(intent_frame.model_dump())  # 경계 검증
        evidence_pack = EvidencePack.model_validate(evidence_pack.model_dump())
        trace: list[GateTraceEntry] = []

        # ① PolicyGate (DEC-001 — 최우선)
        policy_check = await self._policy.check(intent_frame, trace_id)
        policy_result = {"deny": "DENY", "restrict": "DOWNSHIFT", "allow": "PASS"}[
            policy_check.decision
        ]
        trace.append(GateTraceEntry(gate="PolicyGate", result=policy_result,
                                    detail={"check_id": policy_check.check_id,
                                            "reasons": policy_check.reasons}))

        # ② ApprovalGate — P2 hold (V0: 즉시 미승인, I-19)
        priority = str(intent_frame.domain_hint.get("priority", "P0"))
        risk: Literal["P0", "P1", "P2"] = priority if priority in ("P0", "P1", "P2") else "P0"
        approval_needed = risk == "P2" or bool(
            intent_frame.risk_flags.get("approval_maybe_required")
        )
        approval = await self._approval.request_approval(
            risk_level=risk, description=intent_frame.user_goal[:200], trace_id=trace_id
        )
        hold = approval_needed and approval.status != "approved"
        trace.append(GateTraceEntry(
            gate="ApprovalGate",
            result="PASS" if approval.status == "approved" else "FAIL",
            detail={"approval_id": approval.approval_id, "risk_level": risk, "hold": hold},
        ))
        if hold:
            log_event("oc.i5.approval.required", producer="I-5",
                      payload={"risk_level": risk, "hold": True}, trace_id=trace_id,
                      severity="warn",
                      links={"failure_code": ["OC_I5_APPROVAL_REQUIRED"],
                             "fallback_id": ["FB_REQUIRE_APPROVAL"]})

        # ③ CostGate — 게이트 80/100 LOCK + 경보 70/85/95 통지 (I-9, DEC-002/-005)
        cost_gate = await self._cost.evaluate_gate(trace_id, cost_usage_override)
        trace.append(GateTraceEntry(
            gate="CostGate",
            result={"normal": "PASS", "downshift": "DOWNSHIFT", "stop": "DENY"}[cost_gate],
            detail={"cost_gate": cost_gate},
        ))
        if cost_gate == "downshift":
            log_event("oc.i5.cost.downshifted", producer="I-5",
                      payload={"to_model": get_config().cost.downshift_model},
                      trace_id=trace_id, severity="warn")

        # ④ EvidenceGate — V0 스텁: 항상 sufficient (PART2 L1023).
        # insufficient → 강제 REFUSE 배선(DEC-010)은 단위 테스트가 게이트 치환으로 검증.
        evidence_sufficient = self._evidence_gate(evidence_pack)
        trace.append(GateTraceEntry(
            gate="EvidenceGate", result="PASS" if evidence_sufficient else "FAIL",
            detail={"v0_stub": True, "sufficient": evidence_sufficient,
                    "items": len(evidence_pack.items)},
        ))
        # ⑤ SelfCheckGate — verify 노드 슬롯 예약 (DEC-001: SKIP = V0 미구현 슬롯 → PASS 갱신)
        trace.append(GateTraceEntry(gate="SelfCheckGate", result="SKIP",
                                    detail={"slot": "verify_node"}))

        log_event("oc.i5.gates.evaluated", producer="I-5",
                  payload={"results": [t.result for t in trace]}, trace_id=trace_id)

        # 종합 → Decision 필드 (PolicyGate 우선순위: block > require_approval > allow.
        # mask는 V1 마스킹 활성 시 — V0 restrict는 cost_gate가 표현)
        if policy_check.decision == "deny":
            policy_gate = "block"
        elif approval_needed:
            policy_gate = "require_approval"
        else:
            policy_gate = "allow"

        if policy_gate == "block" or cost_gate == "stop":
            conclusion = "REJECT"
        elif hold or not evidence_sufficient:  # insufficient → HOLD/ESCALATE (D2.0-02 I-5 §6)
            conclusion = "HOLD"
        else:
            conclusion = "ACCEPT"

        # confidence V0 산출 스텁 (PHASE4-DEC-010 결정 2 — 우선순위 표)
        if not evidence_sufficient:
            score = 0.0  # DEC-010 강제 REFUSE (V0 스텁은 도달 불가 — 단위 테스트로 강제 검증)
        elif policy_gate == "block" or cost_gate == "stop" or hold:
            score = 0.0
        elif intent_frame.domain_hint.get("intent") == "unknown" or intent_frame.ambiguity.get(
            "is_ambiguous"
        ):
            score = 0.50
        else:
            score = 0.90

        routing = {
            "selected_blue_node_id": "direct_llm_v0",  # V0: BLUE NODE 없음 (P4-2)
            "execution_mode": get_config().core.default_execution_mode,
        }
        log_event("oc.i5.route.selected", producer="I-5", payload=routing, trace_id=trace_id)

        decision = DecisionSchema.model_validate(  # 경계 검증 의무 — 20필드 FREEZE
            {
                "decision_id": f"dec_{uuid.uuid4().hex[:12]}",
                "trace_id": trace_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "intent_frame_ref": intent_frame.intent_id,
                "evidence_pack_ref": evidence_pack.evidence_pack_id,
                "policy_gate": policy_gate,
                "approval_required": approval_needed,
                "approval_status": approval.status,
                "cost_gate": cost_gate,
                "routing": routing,
                "memory_plan": {"save_candidate": False, "target_layer": "L0",
                                "requires_user_approval": False},
                "output_spec": {
                    "format_constraints": intent_frame.constraints.get("format_constraints")
                },
                "conclusion": conclusion,
                "locked": True,  # 단일결정 원칙 — S3 후 결론 불변 (DEC-004)
                "gates": {  # A22 V0 수용처 (PHASE4-DEC-010 결정 1)
                    "reasoning_trace": [t.model_dump() for t in trace],
                    "policy_gate": policy_gate,
                    "approval_status": approval.status,
                    "cost_gate": cost_gate,
                    "evidence_gate": "sufficient",
                },
                "confidence_score": score,
                "confidence_level": score_to_level(score),
            }
        )
        log_event("oc.i5.decision.locked", producer="I-5",
                  payload={"decision_id": decision.decision_id,
                           "conclusion": conclusion,
                           "confidence_level": decision.confidence_level},
                  trace_id=trace_id)
        return decision
