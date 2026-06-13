"""S-1 Self-check Engine (자기검증 surface) — V1 CORE 항상-ON 최소검증 표면.

정본: D2.0-01 §5.7 (S-1 CORE, V1:ON, owner D2, i_module_link **I-6, I-15**,
"일반 태스크에서도 최소 검증 수행(항상 ON)").

S-1 은 신규 엔진이 아니라 기구현 I-6(Self-check Engine) + I-15(Evidence & QoD Manager)를
묶는 **항상-ON 최소검증 surface**다(중복 구현 금지 — wrap). run_self_check 는 I-6 보고서를
그대로 위임(반환 형태 I-6 동형), assess_evidence 는 I-15 평가를 위임, minimal_check 는 둘을
결합한 표면(일반 태스크 최소검증 호출용 — §5.7 "항상 ON"). 파이프라인 verify 노드는 I-6 을
직접 사용(P6-1b 정본·토폴로지 LOCK 보존) — S-1 은 비-파이프라인 호출의 통합 표면(C/D/E/A/B
시리즈와 동형: 6-3 = 모듈 구조+인터페이스+결정론, 배선은 토폴로지 무변경 범위 내 선택).
"""

from __future__ import annotations

from typing import Any

from vamos_core.orange_core.i6_self_check import SelfCheckEngine
from vamos_core.orange_core.i15_evidence_qod import EvidenceQoDManager
from vamos_core.schemas.contracts import DecisionSchema, EvidencePack


class SelfCheckSurface:
    """S-1 — I-6 + I-15 묶는 항상-ON 최소검증 표면 (wrap, 재구현 없음)."""

    def __init__(self) -> None:
        self._self_check = SelfCheckEngine()
        self._evidence = EvidenceQoDManager()

    def run_self_check(
        self,
        decision: DecisionSchema,
        *,
        llm_response: str | None,
        failure_codes: list[str],
        trace_id: str,
    ) -> dict[str, Any]:
        """I-6 결정론 4-검증 위임 — 반환 형태 불변(파이프라인 verify 노드 동작 보존)."""
        return self._self_check.run_self_check(
            decision,
            llm_response=llm_response,
            failure_codes=failure_codes,
            trace_id=trace_id,
        )

    def assess_evidence(
        self, evidence_pack: EvidencePack, trace_id: str | None = None
    ) -> dict[str, Any]:
        """I-15 QoD 평가 위임 — EvidenceGate sufficient/coverage/qod."""
        return self._evidence.evaluate(evidence_pack, trace_id)

    def minimal_check(
        self,
        decision: DecisionSchema,
        *,
        llm_response: str | None,
        evidence_pack: EvidencePack | None,
        failure_codes: list[str],
        trace_id: str,
    ) -> dict[str, Any]:
        """항상-ON 최소검증 표면 — I-6 self_check + I-15 evidence 결합(비-파이프라인 호출용)."""
        self_check = self.run_self_check(
            decision, llm_response=llm_response, failure_codes=failure_codes, trace_id=trace_id)
        evidence = (
            self.assess_evidence(evidence_pack, trace_id)
            if evidence_pack is not None
            # 빈 팩 경로 = I-15 evaluate() 빈-팩 출력과 동일 키셋(직답 경로 보존, 형태 정합)
            else {"qod": 0.0, "coverage": 0.0, "sufficient": True, "l2_eligible": False,
                  "items_evaluated": 0, "low_qod_count": 0}
        )
        return {"self_check": self_check, "evidence": evidence}
