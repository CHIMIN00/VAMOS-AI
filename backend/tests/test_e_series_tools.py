"""E-Series (E-1~E-6) 외부 도구 검증 — ToolRegistryEntry 등록 + I-10 합성 + invoke stub.

6-3 범위: 등록 메타(계약 25 재사용) + 인터페이스. 실 외부 API/실행 = 6-4. 이벤트
ui.tool.call.*(registries 정본). 잠긴 TOOL_REGISTRY_SEED 무변경(라우터 entries 합성).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.schemas.contracts import ToolRegistryEntry
from vamos_core.schemas.registries import TOOL_REGISTRY_SEED, is_valid_fallback_id
from vamos_core.tools import E_SERIES_TOOLS, build_tool_router_with_e_series


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def test_six_tools_e1_to_e6():
    """E-1~E-6 전수 6개 — 모듈 ID 매핑."""
    ids = [t.module_id for t in E_SERIES_TOOLS]
    assert ids == ["E-1", "E-2", "E-3", "E-4", "E-5", "E-6"]


def test_entries_validate_as_contract():
    """각 도구 entry() = ToolRegistryEntry(계약 25 재사용) 검증 통과 + tool_id 고유."""
    entries = [t.entry() for t in E_SERIES_TOOLS]
    assert all(isinstance(e, ToolRegistryEntry) for e in entries)
    tool_ids = {e.tool_id for e in entries}
    assert len(tool_ids) == 6


def test_e4_high_risk_approval_gate():
    """E-4 Code Executor = risk high + approval 게이트 필수."""
    e4 = next(t for t in E_SERIES_TOOLS if t.module_id == "E-4").entry()
    assert e4.risk_class == "high"
    assert "approval" in e4.required_gates


def test_error_fallbacks_registered():
    """도구별 에러 폴백 = registries 정본 FB_*."""
    for t in E_SERIES_TOOLS:
        assert is_valid_fallback_id(t.error_fallback_id)


def test_i10_router_composition_unchanged_seed():
    """I-10 라우터 합성 = seed(2) + E-Series(6) = 8, 잠긴 TOOL_REGISTRY_SEED 무변경."""
    assert len(TOOL_REGISTRY_SEED) == 2  # 잠긴 분모 불변
    router = build_tool_router_with_e_series()
    tools = router.list_tools()
    assert len(tools) == 8
    assert router.get_tool("e6_z3_solver") is not None
    assert router.get_tool("llm_openai_text") is not None  # seed 보존


def test_invoke_stub_deferred_and_logs():
    """invoke = 6-4 위임 stub + ui.tool.call.{started,finished} 발행(registries 정본)."""
    tid = new_trace_id()
    tool = E_SERIES_TOOLS[0]
    result = tool.invoke({"q": "x"}, trace_id=tid)
    assert result["status"] == "deferred_to_6_4"
    assert result["output"] is None
    import vamos_core.infra.logger as lg
    content = lg._log_file(datetime.now(UTC).isoformat()).read_text(encoding="utf-8")
    events = [json.loads(line)["event_type"] for line in content.splitlines() if line.strip()]
    assert "ui.tool.call.started" in events
    assert "ui.tool.call.finished" in events


def test_categories_distinct():
    """6 도구 카테고리 분포 (§5.8 — 외부 기능 묶음)."""
    cats = {t.category for t in E_SERIES_TOOLS}
    assert len(cats) == 6
