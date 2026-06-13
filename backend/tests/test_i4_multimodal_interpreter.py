"""I-4 Multimodal Interpreter 검증 — 출력 구조화 (D2.0-02 §7.31~7.40).

artifact_type 결정론 탐지 · compliance(T1 output_spec 강제/T2 missing_parts 노출) ·
interpret_input 모달리티(텍스트 passthrough/비텍스트 stub=6-4) · 이벤트 registries 정본.
"""

from __future__ import annotations

import pytest

from vamos_core.infra.config_loader import reset_config_cache
from vamos_core.infra.logger import new_trace_id
from vamos_core.orange_core.i4_multimodal_interpreter import MultimodalInterpreter
from vamos_core.schemas.contracts import StructuredOutput


@pytest.fixture(autouse=True)
def _env(tmp_path, monkeypatch):
    monkeypatch.setenv("VAMOS_DATA_DIR", str(tmp_path).replace("\\", "/"))
    reset_config_cache()
    yield
    reset_config_cache()


def test_structure_returns_contract():
    s = MultimodalInterpreter().structure_output("안녕하세요 설명입니다.")
    assert isinstance(s, StructuredOutput)
    assert s.artifact_type == "md"
    assert s.compliance_report["output_spec_ok"] is True
    assert s.artifact_meta["size"] == len("안녕하세요 설명입니다.")
    assert len(s.artifact_meta["hash"]) == 16


def test_detect_json():
    s = MultimodalInterpreter().structure_output('{"a": 1, "b": [2, 3]}')
    assert s.artifact_type == "json"


def test_detect_code_fence():
    s = MultimodalInterpreter().structure_output("```python\nprint(1)\n```")
    assert s.artifact_type == "code"


def test_t1_output_spec_code_enforced():
    """T1: output_spec format=code 강제인데 코드블럭 부재 → output_spec_ok False (위반 노출)."""
    s = MultimodalInterpreter().structure_output(
        "그냥 텍스트 답변", output_spec={"format_constraints": "code"})
    assert s.artifact_type == "code"  # spec 강제
    assert s.compliance_report["output_spec_ok"] is False


def test_t2_missing_parts_exposed():
    """T2: must_include 누락 항목이 compliance_report.missing_parts 로 노출."""
    s = MultimodalInterpreter().structure_output(
        "결론만 있는 답변", output_spec={"must_include": ["근거", "예시"]})
    assert s.compliance_report["missing_parts"] == ["근거", "예시"]
    assert s.compliance_report["output_spec_ok"] is False


def test_citations_ok_reflected():
    s = MultimodalInterpreter().structure_output("x", citations_ready=True)
    assert s.compliance_report["citations_ok"] is True


def test_interpret_input_text_vs_multimodal():
    m = MultimodalInterpreter()
    assert m.interpret_input("질문", [])["modality"] == "text"
    mm = m.interpret_input("이미지 분석", ["image", "doc"])
    assert mm["modality"] == "multimodal"
    assert mm["nontext_artifacts"] == ["image"]
    assert mm["stub"] is True  # 비텍스트 실해석 = 6-4


def test_event_emits_registered():
    """oc.i4.output.structured 정본 이벤트 — log_event 레지스트리 검증 통과(예외 없음)."""
    MultimodalInterpreter().structure_output("ok", trace_id=new_trace_id())
