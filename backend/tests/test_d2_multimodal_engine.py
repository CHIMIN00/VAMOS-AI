"""D-2 Multimodal Engine 검증 — 모달 검증 + fusion 전략 + 텍스트 패스스루.

6-3 범위: 모달 유형 검증, 규칙기반 fusion, 텍스트 결정론 패스스루. CLIP/Whisper/OCR = 6-4.
"""

from __future__ import annotations

from vamos_core.reasoning.d2_multimodal_engine import (
    ModalityInput,
    MultimodalEngine,
    MultimodalRequest,
    select_fusion,
)


def test_text_only_passthrough():
    """텍스트 전용 → 패스스루 answer, 6-4 위임 아님."""
    e = MultimodalEngine()
    r = e.reason(MultimodalRequest(modalities=[ModalityInput(type="text", data="hello")]))
    assert r.answer == "hello"
    assert r.deferred_to_6_4 is False
    assert r.details["confidence_per_modality"]["text"] == 1.0


def test_image_modality_deferred():
    """이미지 포함 → 6-4 위임(실 처리), answer 공백."""
    e = MultimodalEngine()
    r = e.reason(MultimodalRequest(modalities=[
        ModalityInput(type="text", data="describe"),
        ModalityInput(type="image", data="<bytes>"),
    ]))
    assert r.deferred_to_6_4 is True
    assert r.answer == ""
    assert r.details["confidence_per_modality"]["image"] == 0.0
    assert "clip_whisper_ocr_ffmpeg" in r.details["defer_to_6_4"]


def test_fusion_strategy_selection():
    """단일/동종 → early, 이종 → hybrid."""
    assert select_fusion([ModalityInput(type="text")]) == "early"
    assert select_fusion([ModalityInput(type="text"),
                          ModalityInput(type="image")]) == "hybrid"


def test_unsupported_modality_listed():
    """미지원 모달 → unsupported_modalities, 신뢰도 0."""
    e = MultimodalEngine()
    r = e.reason(MultimodalRequest(modalities=[ModalityInput(type="hologram", data="x")]))
    assert "hologram" in r.details["unsupported_modalities"]
    assert r.details["confidence_per_modality"]["hologram"] == 0.0


def test_empty_modalities():
    """빈 모달 → confidence 0, error."""
    e = MultimodalEngine()
    r = e.reason(MultimodalRequest(modalities=[]))
    assert r.confidence == 0.0
    assert r.details["error"] == "no_modalities"


def test_duplicate_modality_order_independent():
    """동종 모달 중복 → confidence 순서 무관(타입 붕괴 없음, 적대검증 수리)."""
    e = MultimodalEngine()
    fwd = e.reason(MultimodalRequest(modalities=[
        ModalityInput(type="text", data="a"), ModalityInput(type="text", data="")]))
    rev = e.reason(MultimodalRequest(modalities=[
        ModalityInput(type="text", data=""), ModalityInput(type="text", data="a")]))
    assert fwd.confidence == rev.confidence == 0.5  # 입력 단위 평균 (1.0+0.0)/2
    assert fwd.details["confidence_per_modality"]["text"] == 0.5


def test_ties_i4_i13():
    """I-4(입력)↔D-2↔I-13(출력) 연계 명시."""
    e = MultimodalEngine()
    r = e.reason(MultimodalRequest(modalities=[ModalityInput(type="text", data="x")]))
    assert r.details["ties"] == {"input": "I-4", "output": "I-13"}
