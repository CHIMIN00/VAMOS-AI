"""C-3 Code Verifier (코드 검증기) — V1 CORE 6-3 결정론 인터페이스.

정본: D2.0-01 §5.11 (C-3 CORE, V1:ON, owner D4, ties 04/07) +
docs/sot 2/1-1_Verifier-Reasoning-Engines/03_code-verifier 상세명세 (Parse→Static→
Dynamic(sandbox)→Aggregate, LOCK-VR-15 샌드박스 30s).

6-3 범위(결정론): Python = stdlib ast.parse **구문 검증** + AST 패턴 기반 정적 보안 스캔
(eval/exec/os.system/shell=True 등) + 단순 순환복잡도 추정. 6-4 위임: Docker 샌드박스 실행
(E-4 Code Executor), 비-Python tree-sitter 파싱, 전수 OWASP, LLM 의도정합. 결과는 모듈 내부
dataclass(계약 25 무변경). 샌드박스 실행 = 6-4 — 본 6-3은 정적 분석만(코드 미실행).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass

from vamos_core.reasoning._common import BaseVerifier, VerifyResult, clamp01, judge

#: 6-3 정적 보안 규칙 (AST 패턴 — 전수 OWASP/CWE = 6-4). 위험 호출 이름.
_DANGEROUS_CALLS: dict[str, str] = {
    "eval": "code_injection",
    "exec": "code_injection",
    "compile": "code_injection",
    "__import__": "dynamic_import",
}
#: os/subprocess 위험 속성 호출 (os.system / subprocess.* )
_DANGEROUS_ATTR: dict[str, str] = {
    "system": "command_injection",
    "popen": "command_injection",
}
#: 분기 노드 (순환복잡도 추정 — McCabe 근사)
_BRANCH_NODES = (ast.If, ast.For, ast.While, ast.Try, ast.With,
                ast.BoolOp, ast.comprehension)


@dataclass
class CodeVerifyRequest:
    """C-3 입력 — 03_code-verifier §2 (6-3 결정론 필드 서브셋)."""

    code: str
    language: str = "python"
    intent: str = ""
    security_scan: bool = True
    request_id: str = ""


class _SecurityVisitor(ast.NodeVisitor):
    """AST 보안 패턴 방문자 — 위험 호출 수집 (결정론, 코드 미실행)."""

    def __init__(self) -> None:
        self.issues: list[dict[str, object]] = []
        self.complexity = 1  # McCabe 기저 1

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802 — ast 규약
        if isinstance(node.func, ast.Name) and node.func.id in _DANGEROUS_CALLS:
            self.issues.append({"line": node.lineno, "issue_type": _DANGEROUS_CALLS[node.func.id],
                                "severity": "high", "symbol": node.func.id})
        if isinstance(node.func, ast.Attribute) and node.func.attr in _DANGEROUS_ATTR:
            self.issues.append({"line": node.lineno, "issue_type": _DANGEROUS_ATTR[node.func.attr],
                                "severity": "high", "symbol": node.func.attr})
        # subprocess(..., shell=True)
        for kw in node.keywords:
            if kw.arg == "shell" and isinstance(kw.value, ast.Constant) and kw.value.value is True:
                self.issues.append({"line": node.lineno, "issue_type": "command_injection",
                                    "severity": "high", "symbol": "shell=True"})
        self.generic_visit(node)

    def generic_visit(self, node: ast.AST) -> None:
        if isinstance(node, _BRANCH_NODES):
            self.complexity += 1
        super().generic_visit(node)


class CodeVerifier(BaseVerifier):
    """verify(CodeVerifyRequest) → VerifyResult — 구문+정적 보안 (실행 = 6-4/E-4)."""

    engine_id = "C-3"

    def verify(self, request: CodeVerifyRequest) -> VerifyResult:
        if request.language != "python":
            # 비-Python 파싱(tree-sitter) = 6-4 위임 — 6-3 결정론 판정 보류
            return VerifyResult(
                engine_id=self.engine_id, confidence=0.5, is_valid=False, judgment="REVIEW",
                reasons=[f"non_python_deferred_to_6_4: {request.language}"],
                details={"defer_to_6_4": ["tree_sitter_parse", "docker_sandbox_E-4"],
                         "request_id": request.request_id},
            )

        reasons: list[str] = []
        syntax_errors: list[dict[str, object]] = []
        try:
            tree = ast.parse(request.code)
        except SyntaxError as exc:
            syntax_errors.append({"line": exc.lineno or 0, "message": str(exc.msg),
                                  "severity": "error"})
            return VerifyResult(
                engine_id=self.engine_id, confidence=0.0, is_valid=False, judgment="FAIL",
                reasons=["syntax_error"],
                details={"syntax_errors": syntax_errors, "request_id": request.request_id,
                         "defer_to_6_4": ["docker_sandbox_E-4", "llm_intent_alignment"]},
            )

        visitor = _SecurityVisitor()
        security_issues: list[dict[str, object]] = []
        if request.security_scan:
            visitor.visit(tree)
            security_issues = visitor.issues

        # Aggregate — 결정론 신뢰도 (보안 high -0.4, 복잡도 높으면 감점)
        confidence = 1.0
        high = sum(1 for i in security_issues if i.get("severity") == "high")
        if high:
            confidence -= 0.4 * high
            reasons.append(f"{high} high-severity security issue(s)")
        if visitor.complexity > 10:
            confidence -= 0.15
            reasons.append(f"high_cyclomatic_complexity={visitor.complexity}")
        confidence = clamp01(confidence)
        is_secure = high == 0
        verdict = judge(confidence)
        return VerifyResult(
            engine_id=self.engine_id,
            confidence=confidence,
            is_valid=not syntax_errors and is_secure and verdict != "FAIL",
            judgment=verdict,
            reasons=reasons,
            details={
                "syntax_errors": syntax_errors,
                "security_issues": security_issues,
                "is_secure": is_secure,
                "cyclomatic_complexity": visitor.complexity,
                "request_id": request.request_id,
                "defer_to_6_4": ["docker_sandbox_E-4", "tree_sitter_non_python",
                                 "llm_intent_alignment"],
            },
        )
