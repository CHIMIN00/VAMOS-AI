"""I-10 Tool Registry/Router (툴 레지스트리/라우터) — 라우팅 활성화 (i5 인라인 대체).

정본: D2.0-01 §5.6 (I-10 CORE, V1:ON) + D2.0-02 §7.63~7.68 (구 I-10 UI·오케스트레이션 +
I-11 외부도구 어댑터 → N:1 정본 I-10, §4.0). 계약: ToolRegistryEntry(D2.1-D4 §4.1) +
TOOL_REGISTRY_SEED(registries 정본, 2 seed).

책임: ① 도구 레지스트리(가용 도구 등록/조회/카테고리 필터) ② 라우터(IntentFrame → routing
{selected_blue_node_id, execution_mode}). 6-3 범위: 레지스트리 + 라우팅 인터페이스(결정론).
실제 도구 실행·BLUE NODE·MCP 브릿지 = 4-2/6-4 (본 모듈은 direct_llm_v0 + config 기본 모드
보존, V0 무회귀). 도구 미발견 시 OC_I5_ROUTE_NOT_FOUND / FB_ROUTE_SAFE_NODE(registries 정본).

이벤트: ui.node.selected(registries 정본 — 구 oc.i10.ui.state.emitted 는 [LEGACY] 미등록).
i5 의 oc.i5.route.selected(Decision route 기록)는 i5 유지 — 본 모듈은 노드 선택만 통지.
"""

from __future__ import annotations

from typing import Any

from vamos_core.infra.config_loader import get_config
from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import IntentFrame, ToolRegistryEntry
from vamos_core.schemas.registries import TOOL_REGISTRY_SEED

#: V0/6-3 직접 LLM 노드 (BLUE NODE 미활성 — P4-2/6-4 연결 전)
DIRECT_LLM_NODE = "direct_llm_v0"


class ToolRegistryRouter:
    """도구 레지스트리 + 라우터 — D2.0-02 §7.64/§7.67 최소 인터페이스 (결정론)."""

    def __init__(self, entries: tuple[dict[str, Any], ...] | None = None) -> None:
        seed = entries if entries is not None else TOOL_REGISTRY_SEED
        # 경계 검증 의무 — 시드를 ToolRegistryEntry 계약으로 검증 후 보관
        self._tools: dict[str, ToolRegistryEntry] = {
            e["tool_id"]: ToolRegistryEntry.model_validate(e) for e in seed
        }

    def list_tools(self) -> list[ToolRegistryEntry]:
        return list(self._tools.values())

    def get_tool(self, tool_id: str) -> ToolRegistryEntry | None:
        return self._tools.get(tool_id)

    def tools_for_category(self, category: str) -> list[ToolRegistryEntry]:
        return [t for t in self._tools.values() if t.category == category]

    def route(self, intent_frame: IntentFrame, trace_id: str | None = None) -> dict[str, Any]:
        """IntentFrame → routing{selected_blue_node_id, execution_mode}.

        6-3: BLUE NODE 미활성 → direct_llm_v0 + config 기본 실행모드(V0 무회귀). 실제 노드/도구
        라우팅(능력 매칭·MCP)은 6-4. routing 계약 형태(selected_blue_node_id/execution_mode) 보존.
        """
        routing: dict[str, Any] = {
            "selected_blue_node_id": DIRECT_LLM_NODE,
            "execution_mode": get_config().core.default_execution_mode,
        }
        if trace_id is not None:
            log_event("ui.node.selected", producer="I-10",
                      payload={"selected_blue_node_id": routing["selected_blue_node_id"],
                               "execution_mode": routing["execution_mode"],
                               "intent_ref": intent_frame.intent_id,
                               "tools_available": len(self._tools)},
                      trace_id=trace_id)
        return routing
