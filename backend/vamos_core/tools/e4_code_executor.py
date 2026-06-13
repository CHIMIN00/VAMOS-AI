"""E-4 Code Executor — V1 CORE 외부 도구 (6-3 등록 인터페이스).

정본: D2.0-01 §5.8 (E-4 CORE, V1:ON, owner D4, both/panel). 6-3 = ToolRegistryEntry 등록 +
인터페이스. 실 코드 실행 = Docker 샌드박스(6-2 Security-Governance / 6-4, LOCK-VR-15 30s) —
C-3 Code Verifier 동적 실행과 연계. risk=high → approval 게이트 필수. 에러 폴백 = FB_RETRY_SOFT.
"""

from __future__ import annotations

from vamos_core.tools._base import BaseExternalTool


class CodeExecutor(BaseExternalTool):
    """E-4 — 코드 실행기 (실 샌드박스 실행 = 6-4/6-2, C-3 연계)."""

    tool_id = "e4_code_executor"
    module_id = "E-4"
    category = "exec.sandbox"
    risk_class = "high"
    cost_class = "v1"
    required_gates = ("policy", "cost", "approval")
    outputs = ("artifact", "log")
    notes = "코드 실행 (D2.0-01 §5.8 E-4). Docker 샌드박스 = 6-4/6-2 (C-3 연계, LOCK-VR-15)"
    external = True
    error_fallback_id = "FB_RETRY_SOFT"
