"""I-17 Blue Node Manager (블루 노드 매니저) — 노드 레지스트리 + CORE→NODE 요청 구성.

정본: D2.0-01 §5.6 (I-17 CORE, V1:ON). 설계는 D2.0-03 BLUE_NODES 참조(§4.0). 계약:
NodeRequestEnvelope/NodeResponseEnvelope/NodeCapabilityProfile(D2.1-D3) + NODE_REGISTRY_SEED.

책임: ① 블루 노드 레지스트리(등록/조회/도메인 필터) ② build_request → NodeRequestEnvelope
(CORE→NODE 봉투). 6-3/6-4 경계: 실제 노드 디스패치·실행·MCP 브릿지 = 4-2/6-4 (V0 파이프라인은
direct_llm_v0 사용, BLUE NODE 미실행). 본 모듈은 레지스트리 + 요청봉투 구성 인터페이스(결정론).
이벤트: ui.node.context.loaded (registries 정본). 미등록 노드 → OC_I5_ROUTE_NOT_FOUND/
FB_ROUTE_SAFE_NODE (registries 정본).
"""

from __future__ import annotations

import uuid
from typing import Any

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import NodeRequestEnvelope
from vamos_core.schemas.registries import NODE_REGISTRY_SEED


class BlueNodeManager:
    """블루 노드 레지스트리 + 요청 구성 — D2.0-03 정본 (6-3=인터페이스, 실행=6-4)."""

    def __init__(self, entries: tuple[dict[str, Any], ...] | None = None) -> None:
        seed = entries if entries is not None else NODE_REGISTRY_SEED
        self._nodes: dict[str, dict[str, Any]] = {e["node_id"]: dict(e) for e in seed}

    def list_nodes(self) -> list[dict[str, Any]]:
        return list(self._nodes.values())

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        return self._nodes.get(node_id)

    def nodes_for_domain(self, domain: str) -> list[dict[str, Any]]:
        return [n for n in self._nodes.values() if n.get("domain") == domain]

    def build_request(
        self,
        node_id: str,
        intent_summary: str,
        project_id: str,
        session_id: str,
        trace_id: str,
        constraints: dict[str, Any] | None = None,
    ) -> NodeRequestEnvelope:
        """CORE→NODE 요청 봉투 구성 (계약 검증). 미등록 node_id → 안전 노드 폴백 통지."""
        if node_id not in self._nodes:
            log_event("ui.node.context.loaded", producer="I-17",
                      payload={"node_id": node_id, "found": False}, trace_id=trace_id,
                      severity="warn",
                      links={"failure_code": ["OC_I5_ROUTE_NOT_FOUND"],
                             "fallback_id": ["FB_ROUTE_SAFE_NODE"]})
            raise KeyError(f"미등록 blue node: {node_id!r} (NODE_REGISTRY)")
        envelope = NodeRequestEnvelope.model_validate({  # 경계 검증 의무
            "request_id": f"req_{uuid.uuid4().hex[:12]}",
            "project_id": project_id,
            "session_id": session_id,
            "node_id": node_id,
            "intent_summary": intent_summary,
            "constraints": constraints or {},
            "trace_id": trace_id,
        })
        log_event("ui.node.context.loaded", producer="I-17",
                  payload={"node_id": node_id, "found": True,
                           "request_id": envelope.request_id,
                           "domain": self._nodes[node_id].get("domain")},
                  trace_id=trace_id)
        return envelope
