"""C-2 Math Verifier (수식 검증기) — V1 CORE 6-3 결정론 인터페이스.

정본: D2.0-01 §5.11 (C-2 CORE, V1:ON, owner D4, ties 02(I-20)/07) +
docs/sot 2/1-1_Verifier-Reasoning-Engines/02_math-verifier 상세명세 (Parse→Normalize→
Evaluate(symbolic+numeric)→Aggregate, tolerance atol=10^-precision).

6-3 범위(결정론): stdlib ast 기반 **안전 산술 평가**(+,-,*,/,**,단항) + 등식 좌우 수치 비교
(허용오차) — eval() 미사용, 화이트리스트 노드만. 6-4 위임: SymPy 기호대수, LaTeX/MathML
파싱, 차원분석, Z3 solver(E-6 연계). 결과는 모듈 내부 dataclass(계약 25 무변경).
"""

from __future__ import annotations

import ast
import operator
from collections.abc import Callable
from dataclasses import dataclass

from vamos_core.reasoning._common import BaseVerifier, VerifyResult, clamp01, judge

#: 화이트리스트 이항 연산 (안전 — eval 금지, ast 노드 한정)
_BIN_OPS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY_OPS: dict[type[ast.unaryop], Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


class MathEvalError(ValueError):
    """안전 평가 불가(미지원 노드/심볼) — 6-4 SymPy 위임 신호."""


def _safe_eval(node: ast.AST) -> float:
    """ast 노드 안전 평가 — 화이트리스트 외 노드는 MathEvalError(6-4 위임)."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        return _BIN_OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))
    raise MathEvalError(f"미지원 노드(6-4 위임): {type(node).__name__}")


@dataclass
class MathVerifyRequest:
    """C-2 입력 — 02_math-verifier §2 (6-3 결정론 필드 서브셋)."""

    expression: str
    expected_result: str | None = None
    precision: int = 6
    request_id: str = ""


def _parse_eval(expr: str) -> float:
    """수식 문자열 → 안전 평가 (파싱/평가 실패 시 MathEvalError)."""
    try:
        tree = ast.parse(expr.strip(), mode="eval")
    except SyntaxError as exc:
        raise MathEvalError(f"파싱 실패: {exc}") from exc
    try:
        return _safe_eval(tree)
    except MathEvalError:
        raise
    except (ZeroDivisionError, OverflowError, ValueError) as exc:
        # 0-나눗셈/오버플로 등 산술 예외 → 6-4 위임 신호(크래시 방지, _deferred 경로)
        raise MathEvalError(f"산술 오류(6-4 위임): {exc}") from exc


class MathVerifier(BaseVerifier):
    """verify(MathVerifyRequest) → VerifyResult — 안전 산술 평가 + 허용오차 비교 (결정론)."""

    engine_id = "C-2"

    def verify(self, request: MathVerifyRequest) -> VerifyResult:
        reasons: list[str] = []
        atol = 10.0 ** (-request.precision)

        # 등식("lhs = rhs" / "lhs == rhs") 분해
        expr = request.expression
        normalized = expr.replace("==", "=")
        if "=" in normalized:
            lhs_s, _, rhs_s = normalized.partition("=")
            try:
                lhs, rhs = _parse_eval(lhs_s), _parse_eval(rhs_s)
            except MathEvalError as exc:
                return self._deferred(request, str(exc))
            diff = abs(lhs - rhs)
            is_correct = diff <= atol
            confidence = 1.0 if is_correct else clamp01(1.0 - min(1.0, diff))
            if not is_correct:
                reasons.append(f"equation mismatch diff={diff:.3e} > atol={atol:.1e}")
            computed = repr(lhs)
        else:
            try:
                value = _parse_eval(expr)
            except MathEvalError as exc:
                return self._deferred(request, str(exc))
            computed = repr(value)
            if request.expected_result is not None:
                try:
                    expected = _parse_eval(request.expected_result)
                except MathEvalError as exc:
                    return self._deferred(request, str(exc))
                diff = abs(value - expected)
                is_correct = diff <= atol
                confidence = 1.0 if is_correct else clamp01(1.0 - min(1.0, diff))
                if not is_correct:
                    reasons.append(f"result mismatch diff={diff:.3e} > atol={atol:.1e}")
            else:
                is_correct = True  # 평가만 성공 = 형식 유효(기대값 없음)
                confidence = 0.8
                reasons.append("no_expected_result")

        verdict = judge(confidence)
        return VerifyResult(
            engine_id=self.engine_id,
            confidence=confidence,
            is_valid=is_correct and verdict != "FAIL",
            judgment=verdict,
            reasons=reasons,
            details={
                "computed_result": computed,
                "method": "numeric",
                "tolerance_atol": atol,
                "request_id": request.request_id,
                "defer_to_6_4": ["sympy_symbolic", "latex_parse", "z3_solver_E-6"],
            },
        )

    def _deferred(self, request: MathVerifyRequest, why: str) -> VerifyResult:
        """안전 평가 불가 → 6-4(SymPy/Z3) 위임. 6-3 결정론 판정 보류(REVIEW)."""
        return VerifyResult(
            engine_id=self.engine_id,
            confidence=0.5,
            is_valid=False,
            judgment="REVIEW",
            reasons=[f"deferred_to_6_4: {why}"],
            details={
                "computed_result": None,
                "method": "deferred",
                "request_id": request.request_id,
                "defer_to_6_4": ["sympy_symbolic", "latex_parse", "z3_solver_E-6"],
            },
        )
