"""1-1 Verifier/Reasoning 공통 기반 — ABC + 신뢰도 판정 (00_common 정본).

정본: docs/sot 2/1-1_Verifier-Reasoning-Engines/00_common (BaseVerifier/BaseReasoningEngine
ABC, Ask→Bridge→Confirm) + VERIFIER_REASONING_ENGINES_상세명세 (LOCK-VR-05 신뢰도 임계).

신뢰도 임계(LOCK-VR-05): confidence ≥ 0.8 → PASS / 0.5~0.8 → REVIEW / < 0.8 → escalate.
config 에 verifier 섹션 부재 → 모듈 상수(SOT cite, I-15 QoD 임계 선례 동형). 결과는 모듈 내부
dataclass(계약 25 무변경). should_escalate() = 결정론 노출(실 I-20 라우팅은 호출측 — R-01-8).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal

#: LOCK-VR-05 신뢰도 임계 — 본 패키지 단일 출처 (config verifier 섹션 부재 시 모듈 상수)
CONFIDENCE_PASS = 0.8
#: LOCK-VR-05 — REVIEW 하한 (이 미만 = FAIL)
CONFIDENCE_REVIEW = 0.5

Judgment = Literal["PASS", "REVIEW", "FAIL"]


def clamp01(value: float) -> float:
    """confidence 를 [0.0, 1.0] 로 보정 (계약 범위 강제)."""
    return min(1.0, max(0.0, value))


def judge(confidence: float) -> Judgment:
    """LOCK-VR-05 — confidence → PASS/REVIEW/FAIL (가변 아님, 고정 임계)."""
    if confidence >= CONFIDENCE_PASS:
        return "PASS"
    if confidence >= CONFIDENCE_REVIEW:
        return "REVIEW"
    return "FAIL"


@dataclass
class VerifyResult:
    """검증 결과 공통 봉투 — 모듈별 세부는 details (계약 25 무변경, 내부 타입)."""

    engine_id: str
    confidence: float
    is_valid: bool
    judgment: Judgment
    reasons: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ReasonResult:
    """추론 결과 공통 봉투 (D-1/D-2) — reasoning_trace 필수(R-01-5)."""

    engine_id: str
    answer: str
    confidence: float
    strategy_used: str
    reasoning_trace: list[dict[str, Any]] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    deferred_to_6_4: bool = False


class BaseVerifier(ABC):
    """C-Series 검증 엔진 ABC — verify() 결정론, should_escalate() 노출."""

    engine_id: str = "C-?"

    @abstractmethod
    def verify(self, request: Any) -> VerifyResult:
        """검증 수행 → VerifyResult (6-3 결정론, 6-4 위임은 details 마킹).

        request = 모듈별 *VerifyRequest dataclass (Any = LSP 호환, 구상 타입 override 허용).
        """

    def confidence_threshold(self) -> float:
        return CONFIDENCE_PASS

    def should_escalate(self, result: VerifyResult) -> bool:
        """LOCK-VR-05 — confidence < 0.8 → I-20 경유 D-1 에스컬레이션(R-01-8, 호출측)."""
        return result.confidence < self.confidence_threshold()


class BaseReasoningEngine(ABC):
    """D-Series 추론 엔진 ABC — reason() 결정론 골격, 실 LLM = 6-4."""

    engine_id: str = "D-?"

    @abstractmethod
    def reason(self, request: Any) -> ReasonResult:
        """추론 수행 → ReasonResult (6-3 전략선택·골격, 실 생성 6-4).

        request = 모듈별 *Request dataclass (Any = LSP 호환, 구상 타입 override 허용).
        """

    def should_escalate(self, result: ReasonResult) -> bool:
        """confidence < 0.5 → I-20 경유 Fallback Chain (R-01-8, 호출측)."""
        return result.confidence < CONFIDENCE_REVIEW
