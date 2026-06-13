"""C-3 Code Verifier 검증 — stdlib ast 구문 + 정적 보안 (1-1/03_code-verifier).

6-3 범위: Python ast.parse 구문 + AST 보안 패턴(코드 미실행). Docker 샌드박스(E-4) = 6-4.
"""

from __future__ import annotations

from vamos_core.reasoning.c3_code_verifier import CodeVerifier, CodeVerifyRequest


def test_valid_python_passes():
    """정상 Python → PASS, secure."""
    v = CodeVerifier()
    r = v.verify(CodeVerifyRequest(code="def add(a, b):\n    return a + b\n"))
    assert r.judgment == "PASS"
    assert r.details["is_secure"] is True
    assert r.details["syntax_errors"] == []


def test_syntax_error_fails():
    """구문 오류 → FAIL, confidence 0."""
    v = CodeVerifier()
    r = v.verify(CodeVerifyRequest(code="def broken(:\n"))
    assert r.judgment == "FAIL"
    assert r.confidence == 0.0
    assert r.details["syntax_errors"]


def test_eval_security_issue():
    """eval 호출 → security issue high, not secure."""
    v = CodeVerifier()
    r = v.verify(CodeVerifyRequest(code="x = eval(user_input)\n"))
    issues = r.details["security_issues"]
    assert any(i["issue_type"] == "code_injection" for i in issues)
    assert r.details["is_secure"] is False


def test_shell_true_security_issue():
    """subprocess(..., shell=True) → command_injection 탐지."""
    v = CodeVerifier()
    r = v.verify(CodeVerifyRequest(
        code="import subprocess\nsubprocess.run(cmd, shell=True)\n"))
    issues = r.details["security_issues"]
    assert any(i["symbol"] == "shell=True" for i in issues)


def test_non_python_deferred():
    """비-Python → REVIEW 6-4 위임(tree-sitter)."""
    v = CodeVerifier()
    r = v.verify(CodeVerifyRequest(code="fn main() {}", language="rust"))
    assert r.judgment == "REVIEW"
    assert "tree_sitter_parse" in r.details["defer_to_6_4"]


def test_complexity_counted():
    """분기 노드 순환복잡도 추정."""
    v = CodeVerifier()
    code = "def f(x):\n    if x:\n        for i in range(x):\n            pass\n    return x\n"
    r = v.verify(CodeVerifyRequest(code=code))
    assert r.details["cyclomatic_complexity"] >= 3
