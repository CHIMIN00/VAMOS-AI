"""I-13 Multimodal Output Renderer 검증 (D2.0-01 §5.6, D2.0-02 0:1 GAP 신규 최소).

artifact_type 별 결정론 렌더 · 비텍스트(diagram/image) 6-4 위임 stub · surface 검증 · 이벤트 정본.
"""

from __future__ import annotations

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i13_output_renderer import OutputRenderer


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def test_render_md_passthrough():
    r = OutputRenderer().render({"artifact_type": "md", "content": "# 제목\n본문"})
    assert r["format"] == "md"
    assert r["body"] == "# 제목\n본문"
    assert r["rendered"] is True


def test_render_json_pretty_fenced():
    r = OutputRenderer().render({"artifact_type": "json", "content": '{"a":1}'})
    assert r["body"].startswith("```json")
    assert '"a": 1' in r["body"]


def test_render_code_wraps_fence():
    r = OutputRenderer().render({"artifact_type": "code", "content": "print(1)"})
    assert r["body"].startswith("```")
    assert "print(1)" in r["body"]


def test_render_code_keeps_existing_fence():
    r = OutputRenderer().render({"artifact_type": "code", "content": "```py\nx=1\n```"})
    assert r["body"] == "```py\nx=1\n```"


def test_render_diagram_deferred_stub():
    """비텍스트 — 결정론 렌더 불가, 6-4 위임 stub."""
    r = OutputRenderer().render({"artifact_type": "diagram", "content": "graph TD"})
    assert r["rendered"] is False
    assert "6-4" in r["body"]


def test_surface_validation_defaults_cli():
    r = OutputRenderer().render({"artifact_type": "md", "content": "x"}, surface="invalid")
    assert r["surface"] == "cli"


def test_surface_hologram_kept():
    r = OutputRenderer().render({"artifact_type": "md", "content": "x"}, surface="hologram")
    assert r["surface"] == "hologram"


def test_event_registered():
    OutputRenderer().render({"artifact_type": "md", "content": "x"}, trace_id=new_trace_id())
