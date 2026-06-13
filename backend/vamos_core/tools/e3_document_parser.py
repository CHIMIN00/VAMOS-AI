"""E-3 Document Parser — V1 CORE 외부 도구 (6-3 등록 인터페이스).

정본: D2.0-01 §5.8 (E-3 CORE, V1:ON, owner D4, both/panel). 6-3 = ToolRegistryEntry 등록 +
인터페이스. 실 문서 파싱(docling/Unstructured) = 6-4. 파일 변환 = ui.tool.file.converted,
에러 폴백 = FB_REQ_REUPLOAD(registries 정본).
"""

from __future__ import annotations

from vamos_core.tools._base import BaseExternalTool


class DocumentParser(BaseExternalTool):
    """E-3 — 문서 파서 (실 파싱 라이브러리 = 6-4)."""

    tool_id = "e3_document_parser"
    module_id = "E-3"
    category = "doc.parse"
    risk_class = "low"
    cost_class = "v1"
    required_gates = ("policy", "cost")
    outputs = ("artifact", "log")
    notes = "문서 파싱 (D2.0-01 §5.8 E-3). 실 파싱 = 6-4 / ui.tool.file.converted"
    external = True
    error_fallback_id = "FB_REQ_REUPLOAD"
