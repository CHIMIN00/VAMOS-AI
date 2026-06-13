"""A-1 MultiBrain Adapter 검증 — 5-step 결정론 라우팅 (6-9/01,03,04).

classify→filter→score→gate→select + Fallback Chain. 실 LLM invoke = 6-4. 응답 계약 =
BrainAdapterResponse(D2.1-D4, 계약 25 재사용). 이벤트 ui.node.selected(registries 정본).
"""

from __future__ import annotations

import pytest

from vamos_core.adapters.a1_multibrain_adapter import (
    BrainRequest,
    MultiBrainAdapter,
    classify_complexity,
    gate_check,
)
from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.schemas.contracts import BrainAdapterResponse


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def test_classify_complexity_tiers():
    """토큰 임계 → 복잡도 (03_llm-routing §4.2)."""
    assert classify_complexity(5) == "instant"
    assert classify_complexity(50) == "low"
    assert classify_complexity(300) == "medium"
    assert classify_complexity(1000) == "high"
    assert classify_complexity(5000) == "max"
    assert classify_complexity(600, tier="main") == "max"


def test_gate_check_cost_thresholds():
    """LOCK-69-7 — ≥100 deny / 80~100 downshift / <80 allow."""
    assert gate_check(50.0) == "allow"
    assert gate_check(85.0) == "downshift"
    assert gate_check(100.0) == "deny"


def test_route_high_complexity():
    """high 복잡도 → claude_sonnet 선두 후보."""
    d = MultiBrainAdapter().route(BrainRequest(task_type="reasoning", prompt="x",
                                               token_estimate=1000))
    assert d.complexity == "high"
    assert d.selected_model == "claude_sonnet"
    assert d.gate_result == "allow"


def test_domain_override():
    """domain=code → claude_sonnet 우선 (도메인 오버라이드)."""
    d = MultiBrainAdapter().route(BrainRequest(task_type="reasoning", prompt="x",
                                               domain="code", token_estimate=300))
    assert d.selected_model == "claude_sonnet"
    assert "domain_override" in d.reason


def test_cost_deny_safe_node():
    """비용 초과 → deny → 안전 노드(ollama_local)."""
    d = MultiBrainAdapter().route(BrainRequest(task_type="reasoning", prompt="x",
                                               token_estimate=5000, cost_budget_used_pct=100.0))
    assert d.gate_result == "deny"
    assert d.selected_model == "ollama_local"


def test_fallback_chain_present():
    """Fallback Chain (MAX_TRANSITIONS=2 + safe node)."""
    d = MultiBrainAdapter().route(BrainRequest(task_type="reasoning", prompt="x",
                                               token_estimate=1000))
    assert d.fallback_chain
    assert d.fallback_chain[-1] == "ollama_local"


def test_domain_override_selected_in_candidates():
    """오버라이드 모델은 후보집합에 편입되어야 함 (selected ∈ candidates, 적대검증 수리)."""
    a = MultiBrainAdapter()
    # medium 복잡도 + domain=code → claude_sonnet 는 medium 후보 아님 → 편입되어 선택
    d = a.route(BrainRequest(task_type="reasoning", prompt="x", domain="code",
                             token_estimate=300))
    assert d.selected_model == "claude_sonnet"
    # candidates_evaluated 가 편입을 반영 (medium 3 + override 1 = 4)
    assert d.candidates_evaluated == 4


def test_invoke_returns_contract_stub():
    """invoke → BrainAdapterResponse(계약 25) stub, 6-4 위임 경고."""
    resp = MultiBrainAdapter().invoke(BrainRequest(task_type="main_llm", prompt="x",
                                                    token_estimate=100, trace_id=new_trace_id()))
    assert isinstance(resp, BrainAdapterResponse)
    assert resp.output_text == ""
    assert any("deferred_to_6_4" in w for w in resp.warnings)
