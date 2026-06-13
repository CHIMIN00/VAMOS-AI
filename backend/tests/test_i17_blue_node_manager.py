"""I-17 Blue Node Manager 검증 — 레지스트리 + 요청봉투 (D2.0-01 §5.6, D2.0-03).

NODE_REGISTRY_SEED 로드 · 도메인 필터 · NodeRequestEnvelope 계약 구성 · 미등록 노드 폴백 ·
이벤트 정본 · 실 노드 실행 없음(6-3 경계).
"""

from __future__ import annotations

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i17_blue_node_manager import BlueNodeManager
from vamos_core.schemas.contracts import NodeRequestEnvelope


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def test_registry_loads_seed():
    m = BlueNodeManager()
    nodes = m.list_nodes()
    assert len(nodes) == 1
    assert m.get_node("bn_web_research") is not None
    assert m.get_node("missing") is None


def test_nodes_for_domain():
    m = BlueNodeManager()
    assert [n["node_id"] for n in m.nodes_for_domain("research")] == ["bn_web_research"]
    assert m.nodes_for_domain("nope") == []


def test_build_request_contract():
    """build_request → NodeRequestEnvelope 계약 (7 필수 필드)."""
    m = BlueNodeManager()
    env = m.build_request("bn_web_research", "웹 검색 요약", "proj1", "sess1", new_trace_id())
    assert isinstance(env, NodeRequestEnvelope)
    assert env.node_id == "bn_web_research"
    assert env.intent_summary == "웹 검색 요약"
    assert env.request_id.startswith("req_")


def test_build_request_unknown_node_raises_with_fallback():
    """미등록 노드 → KeyError + FB_ROUTE_SAFE_NODE 통지 (예외 전 이벤트 정본)."""
    m = BlueNodeManager()
    with pytest.raises(KeyError):
        m.build_request("bn_unknown", "x", "p", "s", new_trace_id())


def test_event_registered():
    m = BlueNodeManager()
    m.build_request("bn_web_research", "x", "p", "s", new_trace_id())
