"""E-5 Image Analyzer — V1 CORE 외부 도구 (6-3 등록 인터페이스).

정본: D2.0-01 §5.8 (E-5 CORE, V1:ON, owner D4, both/panel). 6-3 = ToolRegistryEntry 등록 +
인터페이스. 실 이미지 분석(비전 LLM/CLIP, 외부) = 6-4 — D-2 Multimodal Engine 연계.
에러 폴백 = FB_RETURN_RAW(registries 정본).
"""

from __future__ import annotations

from vamos_core.tools._base import BaseExternalTool


class ImageAnalyzer(BaseExternalTool):
    """E-5 — 이미지 분석기 (실 비전 모델/API = 6-4, D-2 연계)."""

    tool_id = "e5_image_analyzer"
    module_id = "E-5"
    category = "llm.vision"
    risk_class = "med"
    cost_class = "v2"
    required_gates = ("policy", "cost")
    outputs = ("signal", "log")
    notes = "이미지 분석 (D2.0-01 §5.8 E-5). 실 비전 = 6-4 (D-2 연계)"
    external = True
    error_fallback_id = "FB_RETURN_RAW"
