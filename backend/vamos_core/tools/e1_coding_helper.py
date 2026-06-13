"""E-1 Coding & System Design Helper — V1 CORE 외부 도구 (6-3 등록 인터페이스).

정본: D2.0-01 §5.8 (E-1 CORE, V1:ON, owner D4, both/panel — 범용 개발/설계 지원,
EVX-1 Code-as-Policy 와 구분). 6-3 = ToolRegistryEntry 등록 + 인터페이스. 실 LLM 코딩 = 6-4.
"""

from __future__ import annotations

from vamos_core.tools._base import BaseExternalTool


class CodingHelper(BaseExternalTool):
    """E-1 — 개발/설계 지원 도구 (실 LLM 생성 = 6-4)."""

    tool_id = "e1_coding_helper"
    module_id = "E-1"
    category = "dev.coding"
    risk_class = "low"
    cost_class = "v1"
    required_gates = ("policy", "cost")
    outputs = ("artifact", "log")
    notes = "범용 개발/설계 지원 (D2.0-01 §5.8 E-1, EVX-1 구분). 실 LLM = 6-4"
    external = True
    error_fallback_id = "FB_RETRY_SOFT"
