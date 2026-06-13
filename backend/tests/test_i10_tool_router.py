"""I-10 Tool Registry/Router 검증 — 레지스트리 + 라우팅 (D2.0-02 §7.63~7.68).

ToolRegistryEntry 계약 검증 · route 결정론(direct_llm_v0 + config 기본모드, V0 무회귀) ·
이벤트 registries 정본(ui.node.selected) · i5 라우팅 활성화 통합.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

import pytest

from vamos_core.infra.config_loader import get_config, reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i2_context_builder import ContextBuilder
from vamos_core.orange_core.i5_decision_engine import DecisionEngine
from vamos_core.orange_core.i10_tool_router import DIRECT_LLM_NODE, ToolRegistryRouter
from vamos_core.schemas.contracts import IntentFrame, ToolRegistryEntry


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def _intent() -> IntentFrame:
    return IntentFrame.model_validate({
        "intent_id": f"int_{uuid.uuid4().hex[:8]}", "trace_id": new_trace_id(),
        "timestamp": datetime.now(UTC).isoformat(), "user_goal": "설명", "task_type": "explain",
        "domain_hint": {"priority": "P0", "candidates": []},
        "constraints": {"format_constraints": None, "must_include": [], "must_not_include": []},
        "risk_flags": {"safety_sensitive": False, "approval_maybe_required": False,
                       "cost_sensitive": False},
        "ambiguity": {"is_ambiguous": False, "missing_slots": [], "clarification_questions": []},
        "required_artifacts": [],
    })


def test_registry_loads_seed_as_contract():
    """TOOL_REGISTRY_SEED → ToolRegistryEntry 계약 검증 후 보관 (2 seed)."""
    r = ToolRegistryRouter()
    tools = r.list_tools()
    assert len(tools) == 2
    assert all(isinstance(t, ToolRegistryEntry) for t in tools)
    assert r.get_tool("llm_openai_text") is not None
    assert r.get_tool("nonexistent") is None


def test_tools_for_category():
    r = ToolRegistryRouter()
    assert [t.tool_id for t in r.tools_for_category("llm.text")] == ["llm_openai_text"]
    assert r.tools_for_category("nope") == []


def test_route_deterministic_direct_llm():
    """6-3: BLUE NODE 미활성 → direct_llm_v0 + config 기본 실행모드 (V0 무회귀)."""
    r = ToolRegistryRouter()
    routing = r.route(_intent(), new_trace_id())
    assert routing["selected_blue_node_id"] == DIRECT_LLM_NODE
    assert routing["execution_mode"] == get_config().core.default_execution_mode
    assert set(routing) == {"selected_blue_node_id", "execution_mode"}


async def test_i5_routing_uses_i10():
    """i5 통합 — Decision.routing 이 I-10 산출(direct_llm_v0) 반영."""
    intent = _intent()
    pack = await ContextBuilder().build_evidence(intent, intent.trace_id)
    d = await DecisionEngine().decide(intent, pack, intent.trace_id)
    assert d.routing["selected_blue_node_id"] == DIRECT_LLM_NODE
    assert "execution_mode" in d.routing
