"""E-6 Z3 Solver — V1 CORE 외부 도구 (6-3 등록 인터페이스).

정본: D2.0-01 §5.8 (E-6 CORE, V1:ON, owner D4, builder/panel). 6-3 = ToolRegistryEntry 등록 +
인터페이스. 실 SMT solver(z3-solver 설치·실행) = 6-4 — C-2 Math Verifier 기호 검증과 연계
(EVX-6 Z3 Solver Routing 별개). 에러 폴백 = FB_RETURN_RAW(registries 정본).
"""

from __future__ import annotations

from vamos_core.tools._base import BaseExternalTool


class Z3Solver(BaseExternalTool):
    """E-6 — Z3 SMT solver (실 solver 설치·실행 = 6-4, C-2 연계)."""

    tool_id = "e6_z3_solver"
    module_id = "E-6"
    category = "solver.smt"
    risk_class = "low"
    cost_class = "v1"
    required_gates = ("policy", "cost")
    outputs = ("signal", "log")
    notes = "Z3 SMT solver (D2.0-01 §5.8 E-6). 실 solver = 6-4 (C-2 연계)"
    external = True
    error_fallback_id = "FB_RETURN_RAW"
