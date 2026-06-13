"""I-4 Multimodal Interpreter (멀티모달 해석) — 출력 구조화 활성화.

정본: D2.0-01 §5.6 (I-4 CORE, V1:ON) + D2.0-02 §7.31~7.40 (구 I-4 문서·코드·데이터 구조화,
A* 번호일치·해석차이 §4.0). 계약: StructuredOutput(D2.0-02 I-4 상세 4필드, contracts.py 정본).

책임(§7.31): Action 결과(raw_output)를 사용자가 읽고/재사용/저장 가능한 구조화 산출물로 변환.
structure_output(raw, output_spec, citations) → StructuredOutput{artifact_type, content,
compliance_report{output_spec_ok, citations_ok, missing_parts}, artifact_meta}. 상태(§7.35):
I4_S0_RAW→I4_S1_STRUCTURING→I4_S2_READY/I4_S3_SPEC_VIOLATION.

6-3/6-4 경계: 멀티모달 입력(이미지/음성) 실해석 = 6-4 (interpret_input 은 텍스트 passthrough +
비텍스트 결정론 stub). 출력 텍스트·코드·json 구조화 = 6-3(결정론). 이벤트: oc.i4.output.structured
/ 위반 OC_I4_OUTPUT_SPEC_VIOLATION / 폴백 FB_OUTPUT_REFORMAT·FB_OUTPUT_MINIMAL (registries 정본).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from vamos_core.infra.logger import log_event
from vamos_core.schemas.contracts import StructuredOutput

#: §7.35 내부 상태 (참조용 — Decision 9-State 와 별개, 모듈 로컬)
I4_STATES = ("I4_S0_RAW", "I4_S1_STRUCTURING", "I4_S2_READY", "I4_S3_SPEC_VIOLATION")

_TEXT_MODALITIES = {"doc", "code", "diagram", "sheet", "etc"}
_NONTEXT_MODALITIES = {"image", "audio", "video", "pdf"}


class MultimodalInterpreter:
    """structure_output / interpret_input — D2.0-02 §7.33 출력 구조화 (결정론)."""

    @staticmethod
    def interpret_input(
        input_text: str, required_artifacts: list[str] | None = None
    ) -> dict[str, Any]:
        """입력 모달리티 판별 — 텍스트 passthrough, 비텍스트는 stub(실해석=6-4)."""
        arts = required_artifacts or []
        nontext = sorted(set(arts) & _NONTEXT_MODALITIES)
        return {
            "modality": "multimodal" if nontext else "text",
            "text": input_text,
            "nontext_artifacts": nontext,
            "stub": bool(nontext),  # 비텍스트 해석은 6-4 (결정론 stub)
        }

    @staticmethod
    def _detect_artifact_type(content: str, output_spec: dict[str, Any]) -> str:
        """artifact_type 결정론 탐지 — output_spec 우선, 이후 내용 추론."""
        fmt = (output_spec or {}).get("format_constraints")
        if isinstance(fmt, str) and fmt in ("md", "json", "code", "diagram"):
            return fmt
        stripped = content.strip()
        if stripped.startswith(("{", "[")):
            try:
                json.loads(stripped)
                return "json"
            except ValueError:
                pass
        if "```" in content:
            return "code"
        return "md"

    def structure_output(
        self,
        raw_output: str,
        output_spec: dict[str, Any] | None = None,
        citations_ready: bool = False,
        trace_id: str | None = None,
    ) -> StructuredOutput:
        """raw_output → StructuredOutput (계약 검증) + compliance 점검."""
        spec = output_spec or {}
        content = raw_output or ""
        artifact_type = self._detect_artifact_type(content, spec)

        must_include = spec.get("must_include") or []
        missing_parts = [m for m in must_include if isinstance(m, str) and m not in content]
        fmt = spec.get("format_constraints")
        # output_spec 위반: 강제 포맷이 code인데 코드블럭 부재, 또는 필수 항목 누락
        output_spec_ok = not missing_parts
        if fmt == "code" and "```" not in content and content.strip():
            output_spec_ok = False

        structured = StructuredOutput.model_validate({  # 경계 검증 의무 — 4필드
            "artifact_type": artifact_type,
            "content": content,
            "compliance_report": {
                "output_spec_ok": output_spec_ok,
                "citations_ok": citations_ready,
                "missing_parts": missing_parts,
                "safety_mask": False,  # V0 마스킹 비활성 (07 정책 훅 = 실LLM/6-4)
            },
            "artifact_meta": {
                "size": len(content),
                "hash": hashlib.sha256(content.encode("utf-8")).hexdigest()[:16],
                "parts": 1,
            },
        })
        if trace_id is not None:
            state = "I4_S2_READY" if output_spec_ok else "I4_S3_SPEC_VIOLATION"
            log_event("oc.i4.output.structured", producer="I-4",
                      payload={"artifact_type": artifact_type, "state": state,
                               "output_spec_ok": output_spec_ok, "size": len(content)},
                      trace_id=trace_id,
                      severity="warn" if not output_spec_ok else "info",
                      links=None if output_spec_ok else {
                          "failure_code": ["OC_I4_OUTPUT_SPEC_VIOLATION"],
                          "fallback_id": ["FB_OUTPUT_REFORMAT"]})
        return structured
