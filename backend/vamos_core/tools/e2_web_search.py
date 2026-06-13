"""E-2 Web Search — V1 CORE 외부 도구 (6-3 등록 인터페이스).

정본: D2.0-01 §5.8 (E-2 CORE, V1:ON, owner D4, both/panel). 6-3 = ToolRegistryEntry 등록 +
인터페이스. 실 웹 검색 API(외부) = 6-4. 에러 폴백 = FB_USE_WEB_SEARCH(registries 정본).
"""

from __future__ import annotations

from vamos_core.tools._base import BaseExternalTool


class WebSearch(BaseExternalTool):
    """E-2 — 웹 검색 도구 (실 외부 검색 API = 6-4)."""

    tool_id = "e2_web_search"
    module_id = "E-2"
    category = "api.search"
    risk_class = "med"
    cost_class = "v1"
    required_gates = ("policy", "cost")
    outputs = ("signal", "log")
    notes = "웹 검색 (D2.0-01 §5.8 E-2). 실 외부 API = 6-4"
    external = True
    error_fallback_id = "FB_USE_WEB_SEARCH"
