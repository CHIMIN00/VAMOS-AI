"""C-1 Logic Verifier (논리 검증기) — V1 CORE 6-3 결정론 인터페이스.

정본: D2.0-01 §5.11 (C-1 CORE, V1:ON, owner D4, ties 02(I-20)/07) +
docs/sot 2/1-1_Verifier-Reasoning-Engines/01_logic-verifier 상세명세 (4-Phase
Parse→Normalize→Evaluate→Aggregate, LOCK-VR-05 신뢰도 임계).

6-3 범위(결정론): 명제 정규화 + 명시적 부정 모순 탐지(claim ↔ context) + 단순 오류유형
규칙 + 신뢰도 집계/판정. 6-4 위임: 의미론적 SAT/CNF solver, LLM 기반 함의 분석. 결과는
모듈 내부 dataclass(계약 25 무변경). escalate(confidence<0.8) = I-20 경유 D-1(R-01-8, 호출측).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from vamos_core.reasoning._common import (
    BaseVerifier,
    VerifyResult,
    clamp01,
    judge,
)

#: 영문 부정 토큰 — **전체 토큰 일치**(부분문자열 금지: 'no'≠'now'/'note')
_NEG_EN = frozenset({"not", "no", "never", "false", "incorrect", "cannot", "none", "nor"})
#: 한글 부정 형태소 — 교착어 특성상 부분문자열 매칭(전체 단어 분리 불가)
_NEG_KO = ("아니", "없", "않", "거짓", "틀")
#: 영문 불용어 — 내용어 비교에서 제외(공유 stopword로 인한 허위 모순 방지)
_STOPWORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
    "of", "to", "and", "or", "in", "on", "at", "it", "its", "that", "this",
    "with", "for", "as", "by", "i", "we", "will", "do", "does", "did",
})
#: 단순 오류유형 키워드 규칙 (전수 24종은 6-4 — 본 6-3은 결정론 부분집합)
_FALLACY_PATTERNS: dict[str, tuple[str, ...]] = {
    "hasty_generalization": ("everyone", "always", "never", "모두", "항상", "절대"),
    "false_dilemma": ("either", "only two", "둘 중", "양자택일"),
}
_TOKEN_RE = re.compile(r"[A-Za-z가-힣]+")


@dataclass
class LogicVerifyRequest:
    """C-1 입력 — 01_logic-verifier §2 (6-3 결정론 필드 서브셋)."""

    claim: str
    context: list[str] = field(default_factory=list)
    request_id: str = ""


def _content_tokens(text: str) -> set[str]:
    """내용어 토큰 집합 — 영문 부정/불용어(전체일치) + 한글 부정형태소(부분일치) 제외."""
    out: set[str] = set()
    for raw in _TOKEN_RE.findall(text):
        t = raw.lower()
        if t in _NEG_EN or t in _STOPWORDS:
            continue
        if any(neg in t for neg in _NEG_KO):
            continue
        out.add(t)
    return out


def _polarity(text: str) -> bool:
    """부정 극성 여부 — 영문 부정어 전체일치 또는 한글 부정형태소 부분일치."""
    toks = {t.lower() for t in _TOKEN_RE.findall(text)}
    if toks & _NEG_EN:
        return True
    return any(neg in text for neg in _NEG_KO)


class LogicVerifier(BaseVerifier):
    """verify(LogicVerifyRequest) → VerifyResult — 결정론 모순/오류 탐지 (Ask→Bridge→Confirm)."""

    engine_id = "C-1"

    def verify(self, request: LogicVerifyRequest) -> VerifyResult:
        reasons: list[str] = []
        contradictions: list[dict[str, str]] = []
        claim_tokens = _content_tokens(request.claim)
        claim_polarity = _polarity(request.claim)

        # Evaluate — 명시적 부정 모순: 동일 내용어 공유 + 극성 반전 (결정론)
        for ctx in request.context:
            shared = claim_tokens & _content_tokens(ctx)
            if shared and _polarity(ctx) != claim_polarity:
                contradictions.append({
                    "premise_a": request.claim,
                    "premise_b": ctx,
                    "contradiction_type": "negation",
                    "severity": "major",
                })

        # 단순 오류유형 규칙 (결정론 부분집합 — 전수 24종 = 6-4)
        fallacy_types: list[str] = []
        low_claim = request.claim.lower()
        for name, kws in _FALLACY_PATTERNS.items():
            if any(kw in low_claim for kw in kws):
                fallacy_types.append(name)

        # Aggregate — 결정론 신뢰도 (모순/오류 감점)
        confidence = 1.0
        if contradictions:
            confidence -= 0.4 * len(contradictions)
            reasons.append(f"{len(contradictions)} negation contradiction(s)")
        if fallacy_types:
            confidence -= 0.15 * len(fallacy_types)
            reasons.append(f"fallacy: {','.join(fallacy_types)}")
        if not request.context:
            reasons.append("no_context_provided")
        confidence = clamp01(confidence)

        verdict = judge(confidence)
        return VerifyResult(
            engine_id=self.engine_id,
            confidence=confidence,
            is_valid=not contradictions and verdict == "PASS",
            judgment=verdict,
            reasons=reasons,
            details={
                "contradictions": contradictions,
                "fallacy_types": fallacy_types,
                "request_id": request.request_id,
                "defer_to_6_4": ["semantic_sat_solver", "llm_entailment"],
            },
        )
