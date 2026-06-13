"""I-13 Multimodal Output Renderer (멀티모달 출력 렌더러) — StructuredOutput → 표시 산출.

정본: D2.0-01 §5.6 (I-13 CORE, V1:ON). ⚠️ D2.0-02 0:1 GAP (설계 부재 — 신규, §4.0). I-4
Multimodal Interpreter(구조화) ↔ I-13(렌더) 짝. 6-3/6-4 경계: 실제 멀티모달 렌더(다이어그램
이미지화·TTS·차트) = 6-4. 본 모듈은 결정론 텍스트/마크다운/코드/JSON 렌더만 — 비텍스트는 stub.

render(structured_output, surface) → {format, body, surface, rendered}. surface=cli|builder|
hologram. 이벤트: ui.main.artifact.created (registries 정본).
"""

from __future__ import annotations

import json
from typing import Any

from vamos_core.infra.logger import log_event

SURFACES = ("cli", "builder", "hologram")
#: 비텍스트 — 결정론 렌더 불가, 실 렌더는 6-4
_DEFERRED_TYPES = {"diagram", "image", "video", "audio"}


class OutputRenderer:
    """render — StructuredOutput(I-4) → surface 표시 body (결정론, 멀티모달=6-4 stub)."""

    def render(
        self, structured_output: dict[str, Any], surface: str = "cli",
        trace_id: str | None = None,
    ) -> dict[str, Any]:
        """artifact_type 별 결정론 렌더. diagram/image 등 비텍스트는 6-4 위임 stub."""
        if surface not in SURFACES:
            surface = "cli"
        atype = str(structured_output.get("artifact_type", "md"))
        content = str(structured_output.get("content", ""))

        if atype in _DEFERRED_TYPES:
            body = f"[{atype}: 결정론 렌더 불가 — 멀티모달 렌더 6-4 위임]"
            rendered = False
        elif atype == "json":
            try:
                body = "```json\n" + json.dumps(
                    json.loads(content), ensure_ascii=False, indent=2) + "\n```"
            except ValueError:
                body = content
            rendered = True
        elif atype == "code":
            body = content if "```" in content else f"```\n{content}\n```"
            rendered = True
        else:  # md / etc — 텍스트 passthrough
            body = content
            rendered = True

        result = {"format": atype, "body": body, "surface": surface, "rendered": rendered}
        if trace_id is not None:
            log_event("ui.main.artifact.created", producer="I-13",
                      payload={"format": atype, "surface": surface, "rendered": rendered,
                               "body_len": len(body)},
                      trace_id=trace_id)
        return result
