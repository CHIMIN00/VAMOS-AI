"""I-19 Approval Manager (V0 스켈레톤) — P0/P1 auto-approve · P2 hold · 타임아웃 600s.

정본: PART2 V0-STEP-4 #7 + B4 §3.8b(timeout_s=600 LOCK) + D2.1-D7 §4.2 ApprovalSchema(12필드).
ApprovalSchema.status는 정본 2값(approved|denied — DN-014): V0 비대화형이라 P2 hold는
"즉시 미승인(denied) + Decision(conclusion=HOLD, approval_required=true)"로 표현 —
600s 미응답 시 자동 거부 정본(B4 §3.8b)의 V0 즉시 평가. 본격 워크플로우는 V1.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal

from vamos_core.infra.config_loader import get_config
from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import ApprovalSchema


class ApprovalManager:
    """request_approval(risk_level) -> ApprovalSchema (V0: P0/P1 auto, P2 hold)."""

    async def request_approval(
        self,
        risk_level: Literal["P0", "P1", "P2"],
        description: str,
        trace_id: str,
    ) -> ApprovalSchema:
        cfg = get_config().approval
        timeout = cfg.p2_timeout_s if risk_level == "P2" else cfg.timeout_s
        expires_at = (datetime.now(UTC) + timedelta(seconds=timeout)).isoformat()
        auto_approve = risk_level in ("P0", "P1")
        approval = ApprovalSchema.model_validate(  # 경계 검증 의무
            {
                "approval_id": f"apr_{uuid.uuid4().hex[:12]}",
                "approval_stage": "plan",
                "requester": "orange_core.i5",
                "scope": "domain",
                "description": description,
                "expires_at": expires_at,
                "status": "approved" if auto_approve else "denied",
                "decided_by": "auto_approve_v0" if auto_approve else "v0_hold_timeout_default",
                "risk_level": risk_level,
                "audit_trace_id": trace_id,
            }
        )
        log_event(
            "wf.approval.requested",
            producer="I-19",
            payload={
                "approval_id": approval.approval_id,
                "risk_level": risk_level,
                "status": approval.status,
                "auto_approve": auto_approve,
                "hold": not auto_approve,  # P2 → hold (V0)
                "timeout_s": timeout,
            },
            trace_id=trace_id,
            severity="warn" if not auto_approve else "info",
        )
        return approval
