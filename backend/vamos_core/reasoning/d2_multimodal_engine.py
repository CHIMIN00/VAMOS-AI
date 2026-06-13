"""D-2 Multimodal Engine (멀티모달 엔진) — V1 CORE 6-3 결정론 인터페이스.

정본: D2.0-01 §5.12 (D-2 CORE, V1:ON, owner D2, internal, ties 02) +
docs/sot 2/1-1_Verifier-Reasoning-Engines/05_multimodal-engine + 3-2_Multimodal-Processing
상세명세 (Early/Late/Hybrid fusion, confidence_per_modality R-01-6).

6-3 범위(결정론): 모달리티 유형 검증 + 규칙기반 fusion 전략 선택 + 텍스트 패스스루 +
모달별 신뢰도(텍스트=처리가능, 그 외=6-4 대기). 6-4 위임: CLIP/Whisper/OCR/FFmpeg 실 처리,
LLM 융합 추론, D-1 호출. I-4(입력 해석)↔D-2↔I-13(출력 렌더) 연계. 결과는 모듈 내부 dataclass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from vamos_core.reasoning._common import BaseReasoningEngine, ReasonResult, clamp01

Fusion = Literal["early", "late", "hybrid", "auto"]
#: 지원 입력 모달리티 (05_multimodal-engine §2 — 6-3 검증 대상)
SUPPORTED_MODALITIES = ("text", "image", "audio", "video", "document")
#: 6-3 결정론 처리 가능 모달 (텍스트만 — 그 외 실 처리 = 6-4)
_DETERMINISTIC_MODALITIES = ("text",)


@dataclass
class ModalityInput:
    """단일 모달 입력 — type/data/metadata (05_multimodal-engine §3.3)."""

    type: str
    data: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MultimodalRequest:
    """D-2 입력 — 05_multimodal-engine §2 (6-3 결정론 필드 서브셋)."""

    modalities: list[ModalityInput]
    task: str = ""
    fusion_strategy: Fusion = "auto"
    request_id: str = ""


def select_fusion(modalities: list[ModalityInput], hint: Fusion = "auto") -> Fusion:
    """규칙기반 fusion 전략 선택 (결정론) — 단일=early, 동종=early, 이종=hybrid."""
    if hint != "auto":
        return hint
    types = {m.type for m in modalities}
    if len(types) <= 1:
        return "early"   # 단일/동종 모달 = 조기 융합
    return "hybrid"      # 이종 모달 = 혼합 융합


class MultimodalEngine(BaseReasoningEngine):
    """reason(MultimodalRequest) → ReasonResult — 모달 검증·전략·텍스트 패스스루 (실 처리 6-4)."""

    engine_id = "D-2"

    def reason(self, request: MultimodalRequest) -> ReasonResult:
        if not request.modalities:
            return ReasonResult(
                engine_id=self.engine_id, answer="", confidence=0.0,
                strategy_used="none", reasoning_trace=[],
                details={"error": "no_modalities", "request_id": request.request_id},
                deferred_to_6_4=False,
            )

        unsupported = [m.type for m in request.modalities if m.type not in SUPPORTED_MODALITIES]
        strategy = select_fusion(request.modalities, request.fusion_strategy)

        # 모달별 입력 점수 (결정론): 텍스트(내용有)=1.0, 그 외/공백=0.0(6-4 대기).
        # 전체 입력 단위로 산출 — 동종 모달 중복도 보존(순서 무관, 결정론 보장).
        def _score(m: ModalityInput) -> float:
            if m.type not in SUPPORTED_MODALITIES:
                return 0.0
            if m.type in _DETERMINISTIC_MODALITIES:
                return 1.0 if m.data.strip() else 0.0
            return 0.0  # 실 처리 = 6-4

        per_input = [(m.type, _score(m)) for m in request.modalities]
        # confidence_per_modality = 타입별 평균(중복 붕괴 없이 집계, 순서 무관)
        conf_per_modality: dict[str, float] = {}
        for mtype in {t for t, _ in per_input}:
            vals = [s for t, s in per_input if t == mtype]
            conf_per_modality[mtype] = round(sum(vals) / len(vals), 4)

        # 텍스트 전용 입력 = 6-3 패스스루(결정론), 그 외 모달 포함 = 6-4 위임
        text_parts = [m.data for m in request.modalities
                     if m.type == "text" and m.data.strip()]
        non_text = [m.type for m in request.modalities if m.type != "text"]
        deferred = bool(non_text)
        answer = "\n".join(text_parts) if not deferred else ""

        # 전체 신뢰도 = 입력 단위 평균(타입 중복 보존 — 순서 의존성 제거)
        scores = [s for _, s in per_input]
        confidence = clamp01(sum(scores) / len(scores)) if scores else 0.0
        return ReasonResult(
            engine_id=self.engine_id,
            answer=answer,
            confidence=confidence,
            strategy_used=strategy,
            reasoning_trace=[
                {"step_number": 1, "description": "모달리티 검증", "deferred_to_6_4": False},
                {"step_number": 2, "description": f"{strategy} 융합 전략 선택",
                 "deferred_to_6_4": False},
                {"step_number": 3, "description": "융합 추론", "deferred_to_6_4": deferred},
            ],
            details={
                "confidence_per_modality": conf_per_modality,
                "unsupported_modalities": unsupported,
                "ties": {"input": "I-4", "output": "I-13"},
                "request_id": request.request_id,
                "defer_to_6_4": ["clip_whisper_ocr_ffmpeg", "llm_fusion", "d1_think_call"],
            },
            deferred_to_6_4=deferred,
        )
