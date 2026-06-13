"""C-1 Logic Verifier 검증 — 결정론 모순/오류 탐지 (1-1/01_logic-verifier, LOCK-VR-05).

6-3 범위: 명시적 부정 모순 + 단순 오류유형 규칙 + 신뢰도 판정. 의미론 SAT/LLM = 6-4.
"""

from __future__ import annotations

from vamos_core.reasoning._common import CONFIDENCE_PASS
from vamos_core.reasoning.c1_logic_verifier import LogicVerifier, LogicVerifyRequest


def test_supported_claim_passes():
    """지지 컨텍스트 + 모순 없음 → PASS, is_valid."""
    v = LogicVerifier()
    r = v.verify(LogicVerifyRequest(claim="The system is secure",
                                    context=["The system is secure by design"]))
    assert r.judgment == "PASS"
    assert r.is_valid is True
    assert r.details["contradictions"] == []
    assert r.confidence >= CONFIDENCE_PASS


def test_negation_contradiction_detected():
    """동일 내용어 + 극성 반전 → 모순 탐지, 신뢰도 감점."""
    v = LogicVerifier()
    r = v.verify(LogicVerifyRequest(claim="The system is secure",
                                    context=["The system is not secure"]))
    assert len(r.details["contradictions"]) == 1
    assert r.details["contradictions"][0]["contradiction_type"] == "negation"
    assert r.is_valid is False
    assert r.confidence < CONFIDENCE_PASS


def test_fallacy_detected():
    """과잉일반화 키워드 → fallacy_types 등재, 감점."""
    v = LogicVerifier()
    r = v.verify(LogicVerifyRequest(claim="Everyone always agrees", context=["sample"]))
    assert "hasty_generalization" in r.details["fallacy_types"]
    assert r.confidence < 1.0


def test_should_escalate_on_low_confidence():
    """confidence < 0.8 → should_escalate True (R-01-8, I-20 경유)."""
    v = LogicVerifier()
    r = v.verify(LogicVerifyRequest(claim="X is true", context=["X is false"]))
    assert v.should_escalate(r) is True


def test_defer_marker_present():
    """6-4 위임 항목 명시 (의미론 SAT/LLM)."""
    v = LogicVerifier()
    r = v.verify(LogicVerifyRequest(claim="The cat is here", context=["A dog is around"]))
    assert "semantic_sat_solver" in r.details["defer_to_6_4"]


def test_no_substring_negation_false_flip():
    """'now' 의 'no' 부분문자열로 인한 허위 극성 반전 없음 (적대검증 수리)."""
    v = LogicVerifier()
    # 'secure now' vs 'secure soon' — 둘 다 긍정, 'now' 가 부정으로 오판되면 안 됨
    r = v.verify(LogicVerifyRequest(claim="ship it now", context=["ship it soon"]))
    assert r.details["contradictions"] == []


def test_no_stopword_false_contradiction():
    """불용어만 공유하는 무관한 문장 → 허위 모순 없음 (적대검증 수리)."""
    v = LogicVerifier()
    r = v.verify(LogicVerifyRequest(claim="The cat is black",
                                    context=["The dog is not white"]))
    assert r.details["contradictions"] == []
    assert r.judgment == "PASS"
