"""C-2 Math Verifier 검증 — 안전 산술 평가 + 허용오차 (1-1/02_math-verifier).

6-3 범위: stdlib ast 안전 평가(eval 금지), 등식 좌우 비교. SymPy/LaTeX/Z3 = 6-4.
"""

from __future__ import annotations

from vamos_core.reasoning.c2_math_verifier import (
    MathEvalError,
    MathVerifier,
    MathVerifyRequest,
    _parse_eval,
)


def test_correct_equation_passes():
    """2 + 2 = 4 → is_correct, PASS."""
    v = MathVerifier()
    r = v.verify(MathVerifyRequest(expression="2 + 2 = 4"))
    assert r.judgment == "PASS"
    assert r.is_valid is True


def test_wrong_equation_fails():
    """2 + 2 = 5 → mismatch, FAIL/REVIEW (신뢰도 하락)."""
    v = MathVerifier()
    r = v.verify(MathVerifyRequest(expression="2 + 2 = 5"))
    assert r.is_valid is False
    assert any("mismatch" in reason for reason in r.reasons)


def test_expression_with_expected():
    """expr + expected_result 비교."""
    v = MathVerifier()
    r = v.verify(MathVerifyRequest(expression="3 * 4", expected_result="12"))
    assert r.judgment == "PASS"
    assert r.details["computed_result"] == repr(12.0)


def test_no_eval_used():
    """안전 평가 — 심볼 포함 시 MathEvalError (eval 미사용 입증)."""
    try:
        _parse_eval("x + 1")
    except MathEvalError:
        pass
    else:
        raise AssertionError("심볼 식은 MathEvalError 여야 함 (eval 금지)")


def test_symbolic_deferred_to_6_4():
    """평가 불가(심볼) → REVIEW 6-4 위임."""
    v = MathVerifier()
    r = v.verify(MathVerifyRequest(expression="x ** 2 + 1"))
    assert r.judgment == "REVIEW"
    assert any("deferred_to_6_4" in reason for reason in r.reasons)
    assert "z3_solver_E-6" in r.details["defer_to_6_4"]


def test_power_operator():
    """** 거듭제곱 안전 평가."""
    v = MathVerifier()
    r = v.verify(MathVerifyRequest(expression="2 ** 10 = 1024"))
    assert r.is_valid is True


def test_division_by_zero_no_crash():
    """0-나눗셈 → 크래시 없이 REVIEW(6-4 위임). (적대검증 round-1 수리)"""
    v = MathVerifier()
    r = v.verify(MathVerifyRequest(expression="1 / 0 = 5"))
    assert r.judgment == "REVIEW"
    assert r.is_valid is False


def test_modulo_by_zero_no_crash():
    """0-나머지 → 크래시 없이 REVIEW."""
    v = MathVerifier()
    r = v.verify(MathVerifyRequest(expression="5 % 0 = 1"))
    assert r.judgment == "REVIEW"


def test_overflow_no_crash():
    """오버플로(10.0**10000) → 크래시 없이 REVIEW(6-4 위임)."""
    v = MathVerifier()
    r = v.verify(MathVerifyRequest(expression="10.0 ** 10000 = 0"))
    assert r.judgment == "REVIEW"
    assert any("deferred_to_6_4" in reason for reason in r.reasons)
