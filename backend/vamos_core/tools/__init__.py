"""VAMOS E-Series 외부 도구 (도구/커넥터/입출력/자동화) — V1 CORE 6-3 인터페이스 계층.

정본: D2.0-01 §5.8 (E-Series — E-1~E-6 CORE, V1:ON, owner D4, "외부 기능 묶음").

본 패키지(E-1~E-6) = 6-3 범위 = ToolRegistryEntry(D2.1-D4 §4.1, 계약 25 재사용) 등록 +
도구 인터페이스 + invoke() stub. 실 외부 API/실행 = 6-4: E-2 Web Search·E-5 Image Analyzer
= 외부 API, E-4 Code Executor = Docker 샌드박스(6-2 연계), E-6 Z3 Solver = 실 solver(C-2 연계).
I-10 Tool Registry/Router 에 등록(build_tool_router_with_e_series — 잠긴 TOOL_REGISTRY_SEED
무변경, 라우터 entries 인자로 합성). 이벤트: ui.tool.call.*/error.*(registries 정본).
"""

from __future__ import annotations

from typing import Any

from vamos_core.orange_core.i10_tool_router import ToolRegistryRouter
from vamos_core.schemas.contracts import ToolRegistryEntry
from vamos_core.schemas.registries import TOOL_REGISTRY_SEED
from vamos_core.tools.e1_coding_helper import CodingHelper
from vamos_core.tools.e2_web_search import WebSearch
from vamos_core.tools.e3_document_parser import DocumentParser
from vamos_core.tools.e4_code_executor import CodeExecutor
from vamos_core.tools.e5_image_analyzer import ImageAnalyzer
from vamos_core.tools.e6_z3_solver import Z3Solver

#: E-Series CORE 6 — D2.0-01 §5.8 (E-1~E-6 전부 V1:ON)
E_SERIES_TOOLS = (
    CodingHelper(), WebSearch(), DocumentParser(),
    CodeExecutor(), ImageAnalyzer(), Z3Solver(),
)


def e_series_entries() -> list[dict[str, Any]]:
    """E-Series 6 도구의 ToolRegistryEntry dict 목록 (I-10 등록용)."""
    return [tool.entry().model_dump(exclude_none=True) for tool in E_SERIES_TOOLS]


def build_tool_router_with_e_series() -> ToolRegistryRouter:
    """I-10 라우터에 seed + E-Series 6 합성 등록 (잠긴 TOOL_REGISTRY_SEED 무변경)."""
    entries = tuple(TOOL_REGISTRY_SEED) + tuple(e_series_entries())
    return ToolRegistryRouter(entries=entries)


__all__ = [
    "CodeExecutor", "CodingHelper", "DocumentParser", "E_SERIES_TOOLS",
    "ImageAnalyzer", "ToolRegistryEntry", "WebSearch", "Z3Solver",
    "build_tool_router_with_e_series", "e_series_entries",
]
