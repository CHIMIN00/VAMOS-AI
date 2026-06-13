"""E-Series 외부 도구 공통 기반 — ToolRegistryEntry 등록 + invoke() stub.

정본: D2.0-01 §5.8 (E-Series) + ToolRegistryEntry(D2.1-D4 §4.1, 계약 25 재사용).
6-3 = 등록 메타 + 인터페이스 + 6-4 위임 stub(코드/외부호출 미실행). 이벤트: ui.tool.call.
{started,finished}(registries 정본). 에러 폴백 = FB_*(registries 정본, 도구별 선언).
"""

from __future__ import annotations

from typing import Any, Literal

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import ToolRegistryEntry

RiskClass = Literal["low", "med", "high"]
CostClass = Literal["v0", "v1", "v2", "v3"]
Gate = Literal["policy", "cost", "approval", "evidence", "self_check"]
Output = Literal["signal", "artifact", "memory", "log"]


class BaseExternalTool:
    """E-Series 도구 ABC — entry() 등록 + invoke() 6-4 위임 stub (실행 미수행)."""

    tool_id: str = "e?"
    module_id: str = "E-?"
    category: str = "tool.generic"
    risk_class: RiskClass = "low"
    cost_class: CostClass = "v1"
    required_gates: tuple[Gate, ...] = ("policy", "cost")
    outputs: tuple[Output, ...] = ("log",)
    notes: str = ""
    #: 외부 API/실행 필요 여부 (True = 실 호출 6-4)
    external: bool = True
    #: 에러 경로 폴백 (registries 정본 FB_*)
    error_fallback_id: str = "FB_RETRY_SOFT"

    def entry(self) -> ToolRegistryEntry:
        """ToolRegistryEntry(D2.1-D4 §4.1) — 경계 검증 의무(.model_validate)."""
        return ToolRegistryEntry.model_validate({
            "tool_id": self.tool_id,
            "category": self.category,
            "adapter_id": self.tool_id,
            "risk_class": self.risk_class,
            "cost_class": self.cost_class,
            "required_gates": list(self.required_gates),
            "outputs": list(self.outputs),
            "notes": self.notes,
        })

    def invoke(self, payload: dict[str, Any], trace_id: str | None = None) -> dict[str, Any]:
        """6-3 stub — 실 외부 호출/실행 = 6-4. 등록·계약·이벤트 형태만 보존(미실행)."""
        if trace_id is not None:
            log_event("ui.tool.call.started", producer=self.module_id,
                      payload={"tool_id": self.tool_id, "external": self.external},
                      trace_id=trace_id)
            log_event("ui.tool.call.finished", producer=self.module_id,
                      payload={"tool_id": self.tool_id, "status": "deferred_to_6_4"},
                      trace_id=trace_id)
        return {
            "tool_id": self.tool_id,
            "status": "deferred_to_6_4",
            "output": None,
            "external": self.external,
        }
