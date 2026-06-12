"""I-2 Context Builder — IntentFrame → EvidencePack (V0 스텁).

정본: D2.0-02 I-2 상세(L2689~) + PART2 V0-STEP-4 #2.
V0: 빈 EvidencePack 반환(items=[]) — V1 RAG 파이프라인 연결용 인터페이스만 정의.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import EvidencePack, IntentFrame


class ContextBuilder:
    """V0 스텁 — V1에서 build_queries/retrieve_evidence가 RAG로 대체."""

    async def build_queries(self, intent_frame: IntentFrame) -> dict[str, Any]:
        """I-2 최소 인터페이스 1 (D2.0-02) — V1 RAG 쿼리 번들. V0는 빈 번들."""
        return {"queries": [], "intent_ref": intent_frame.intent_id}

    async def retrieve_evidence(
        self, query_bundle: dict[str, Any], trace_id: str
    ) -> EvidencePack:
        """I-2 최소 인터페이스 2 — V0: 빈 EvidencePack (EvidenceGate 스텁은 항상 sufficient)."""
        pack = EvidencePack.model_validate(  # 경계 검증 의무
            {
                "evidence_pack_id": f"evp_{uuid.uuid4().hex[:12]}",
                "trace_id": trace_id,
                "timestamp": datetime.now(UTC).isoformat(),
                "items": [],  # V0 빈 팩 — RAG·임베딩 0 (PART2 L1017)
                "coverage": {"sufficient": True, "gaps": []},  # V0 스텁 정합 (PART2 L1023)
                "citations_ready": False,
            }
        )
        log_event(
            "oc.i2.evidence.ready",
            producer="I-2",
            payload={"evidence_pack_id": pack.evidence_pack_id, "items": 0, "v0_stub": True},
            trace_id=trace_id,
        )
        return pack

    async def build_evidence(self, intent_frame: IntentFrame, trace_id: str) -> EvidencePack:
        """편의 결합 — IntentFrame → (쿼리) → EvidencePack."""
        bundle = await self.build_queries(intent_frame)
        return await self.retrieve_evidence(bundle, trace_id)
