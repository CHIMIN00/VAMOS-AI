# C-3 Code Verifier — I/O Schema Specification

> **Status**: APPROVED
> **버전**: v1.1
> **Last-reviewed**: 2026-04-06
> **Owner**: 1-1_Verifier-Reasoning-Engines

---

## 1. 개요

본 문서는 C-3 Code Verifier의 I/O Schema를 L3 수준으로 정의한다. 코드의 기능 정확성·보안 취약점·복잡도를 Docker sandbox 내에서 검증하고, confidence 기반 판정을 반환한다.

> LOCK (D2.0-01 §5.11): C-3 Code Verifier: CORE, V1:ON, change_lock=false

---

## 2. ABC 계약 매핑 (LOCK-VR-11)

> LOCK (상세명세 C-1 §3): ABC 패턴: Ask→Bridge→Confirm, 엔진 간 표준 인터페이스. 메서드 시그니처 변경 불가.

C-3은 `BaseVerifier` ABC(P0-4 `base_verifier_abc.md`)를 구현한다.

| ABC 메서드 | I/O 매핑 | 단계 |
|-----------|---------|------|
| `verify(request: VerifyRequest) → VerifyResult` | `CodeVerifyRequest → CodeVerifyResult` | Ask→Bridge→Confirm 전체 |
| `get_confidence_threshold() → float` | 반환값: `0.8` (LOCK-VR-05) | Confirm 판정 기준 |
| `should_escalate(result: VerifyResult) → bool` | `result.confidence < 0.8` → True | Confirm 에스컬레이션 판단 |

---

## 3. Input Schema

### 3.1 CodeVerifyRequest

`VerifyRequest`(common_types.md §2.1)를 C-3 전용 필드로 확장한다.

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class CodeVerifyRequest(BaseModel):
    """C-3 Code Verifier 검증 요청.

    Base: VerifyRequest (common_types.md §2.1)
    """

    # --- Base 필드 (VerifyRequest 상속) ---
    code: str = Field(
        ...,
        min_length=1,
        max_length=100000,
        description="검증 대상 코드"
    )
    timeout_ms: int = Field(
        ...,
        gt=0,
        description="타임아웃 밀리초 (R-01-3 필수)"
    )
    request_id: str = Field(
        ...,
        min_length=1,
        description="요청 추적 ID (UUID 권장)"
    )

    # --- C-3 전용 필드 ---
    language: str = Field(
        ...,
        min_length=1,
        description="프로그래밍 언어 (python, typescript, rust, go 등)"
    )
    intent: str = Field(
        ...,
        min_length=1,
        description="코드의 의도/목적 설명 (의도-코드 일치 검증에 사용)"
    )
    test_cases: Optional[list["TestCase"]] = Field(
        default=None,
        description="테스트 케이스 (제공 시 sandbox에서 실행)"
    )
    security_scan: bool = Field(
        default=True,
        description="보안 스캔 포함 여부 (OWASP Top 10 + CWE)"
    )
```

| 필드 | 타입 | 필수 | 제약조건 | 기본값 | 근거 |
|------|------|------|---------|--------|------|
| `code` | `str` | Yes | `1 ≤ len ≤ 100000` | — | 상세명세 C-3 §1 |
| `language` | `str` | Yes | `min_length=1` | — | 상세명세 C-3 §1 |
| `intent` | `str` | Yes | `min_length=1` | — | 상세명세 C-3 §4 |
| `test_cases` | `Optional[list[TestCase]]` | No | — | `None` | 상세명세 C-3 §3 |
| `security_scan` | `bool` | No | — | `True` | 상세명세 C-3 §2 |
| `timeout_ms` | `int` | Yes | `> 0` | — | R-01-3 |
| `request_id` | `str` | Yes | `min_length=1` | — | common_types.md §2.1 |

---

## 4. Output Schema

### 4.1 CodeVerifyResult

`VerifyResult`(common_types.md §2.2)를 C-3 전용 필드로 확장한다.

> LOCK (상세명세 C-1 §4): Confidence 판정 >=0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL

```python
class CodeVerifyResult(BaseModel):
    """C-3 Code Verifier 검증 결과.

    Base: VerifyResult (common_types.md §2.2)
    R-01-4: confidence 필수 반환.
    """

    # --- Base 필드 (VerifyResult 상속) ---
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="검증 신뢰도 (R-01-4). LOCK-VR-05: ≥0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL"
    )
    is_valid: bool = Field(
        ...,
        description="종합 검증 통과 여부"
    )
    details: dict = Field(
        default_factory=dict,
        description="상세 검증 결과"
    )
    timestamp: str = Field(
        ...,
        description="결과 생성 시각 (ISO 8601)"
    )
    engine_id: str = Field(
        default="C-3",
        pattern=r"^C-3$",
        description="C-3 Code Verifier"
    )

    # --- C-3 전용 필드 ---
    is_correct: bool = Field(
        ...,
        description="기능적 정확성"
    )
    is_secure: bool = Field(
        ...,
        description="보안 취약점 없음 여부"
    )
    syntax_errors: list["SyntaxError"] = Field(
        default_factory=list,
        description="문법 오류 목록"
    )
    logic_errors: list["LogicError"] = Field(
        default_factory=list,
        description="논리 오류 목록"
    )
    security_issues: list["SecurityIssue"] = Field(
        default_factory=list,
        description="보안 취약점 목록 (OWASP Top 10 + CWE)"
    )
    test_results: list["TestResult"] = Field(
        default_factory=list,
        description="테스트 실행 결과"
    )
    complexity_metrics: Optional["ComplexityMetrics"] = Field(
        default=None,
        description="코드 복잡도 메트릭"
    )
```

---

## 5. 엔진 전용 타입 정의 (그룹 F)

> P0-6 `common_types.md` §8에서 본 spec.md로 정식 정의 위임.

### 5.1 TestCase

```python
class TestCase(BaseModel):
    """테스트 케이스 정의."""

    name: str = Field(..., description="테스트 이름")
    input_data: str = Field(..., description="테스트 입력 (문자열 표현)")
    expected_output: str = Field(..., description="기대 출력")
    timeout_ms: int = Field(default=5000, gt=0, le=30000, description="개별 테스트 타임아웃 (최대 30s, LOCK-VR-15)")
```

### 5.2 TestResult

```python
class TestResult(BaseModel):
    """테스트 실행 결과."""

    test_name: str = Field(..., description="테스트 이름")
    passed: bool = Field(..., description="통과 여부")
    actual_output: Optional[str] = Field(default=None, description="실제 출력")
    error_message: Optional[str] = Field(default=None, description="오류 메시지 (실패 시)")
    execution_time_ms: int = Field(..., ge=0, description="실행 소요 시간(ms)")
```

### 5.3 SyntaxError

```python
class SyntaxError(BaseModel):
    """문법 오류 정보."""

    line: int = Field(..., ge=1, description="오류 발생 줄 번호")
    column: int = Field(..., ge=1, description="오류 발생 열 번호")
    message: str = Field(..., description="오류 메시지")
    severity: Literal["error", "warning"] = Field(..., description="심각도")
```

### 5.4 LogicError

```python
class LogicError(BaseModel):
    """논리 오류 정보."""

    line: int = Field(..., ge=1, description="오류 발생 줄 번호")
    error_type: str = Field(..., description="오류 유형 (dead_code, infinite_loop, null_dereference 등)")
    description: str = Field(..., description="오류 설명")
    severity: Literal["critical", "major", "minor"] = Field(..., description="심각도")
```

### 5.5 SecurityIssue

```python
class SecurityIssue(BaseModel):
    """보안 취약점 정보."""

    line: int = Field(..., ge=1, description="취약점 발생 줄 번호")
    issue_type: str = Field(..., description="취약점 유형 (sql_injection, xss, command_injection 등)")
    owasp_category: Optional[str] = Field(default=None, description="OWASP Top 10 분류")
    cwe_id: Optional[str] = Field(default=None, description="CWE ID (예: CWE-89)")
    severity: Literal["critical", "high", "medium", "low"] = Field(..., description="심각도")
    description: str = Field(..., description="취약점 설명")
    recommendation: str = Field(..., description="수정 권장사항")
```

### 5.6 ComplexityMetrics

```python
class ComplexityMetrics(BaseModel):
    """코드 복잡도 메트릭."""

    cyclomatic_complexity: int = Field(..., ge=1, description="순환 복잡도")
    cognitive_complexity: int = Field(..., ge=0, description="인지 복잡도")
    lines_of_code: int = Field(..., ge=1, description="코드 줄 수")
    maintainability_index: Optional[float] = Field(default=None, ge=0.0, le=100.0, description="유지보수성 지수 (0~100)")
```

---

## 6. Docker Sandbox 정책 (LOCK-VR-15, CONF-VRE-006)

> LOCK (D2.0-02 §1.3-A): Docker sandbox, timeout 30s, CPU/RAM 상한은 설정 파일로 관리 (구체값은 운영 시 결정)

**CONF-VRE-006 준수**: CPU/RAM 리소스 제한을 하드코딩하지 않는다. 설정 파일에서 관리하며, 구체값은 운영 시 결정한다.

| 항목 | 정책 | 근거 |
|------|------|------|
| 실행 환경 | Docker sandbox 컨테이너 | LOCK-VR-15 |
| 실행 시간 제한 | 기본 30초 (I-8 Cost Gate 연동) | LOCK-VR-15 |
| CPU/RAM 상한 | **설정 파일로 관리** (구체값 운영 시 결정) | LOCK-VR-15, CONF-VRE-006 |
| 네트워크 | 기본 차단 (허용 목록만 열림) | D2.0-02 §1.3-A |
| 파일시스템 | 임시 볼륨만 마운트, 호스트 경로 직접 접근 금지 | D2.0-02 §1.3-A |
| 실패 코드 | `SANDBOX_TIMEOUT`, `SANDBOX_OOM`, `SANDBOX_POLICY_DENIED` | D2.0-02 §1.3-A |

---

## 7. Error Schema

> **R-01-7**: error_code + message + recoverable 필수.

| error_code | 설명 | recoverable |
|-----------|------|-------------|
| `VRE_TIMEOUT` | 타임아웃 초과 | True |
| `VRE_INVALID_INPUT` | 코드/언어 누락 또는 형식 오류 | False |
| `VRE_ENGINE_FAILURE` | 코드 검증 엔진 내부 오류 | True |
| `VRE_CONFIDENCE_RANGE` | confidence 범위 위반 | False |
| `VRE_ESCALATION_FAILED` | I-20 경유 에스컬레이션 실패 | True |
| `SANDBOX_TIMEOUT` | Docker sandbox 실행 시간 초과 (30s) | True |
| `SANDBOX_OOM` | Docker sandbox 메모리 초과 | True |
| `SANDBOX_POLICY_DENIED` | Docker sandbox 정책 위반 | False |

---

## 8. Fallback Chain (R-01-2, R-01-8)

> 참조: `failover_policy.md`(P0-8) §5.3

### Layer 2 — 엔진 에스컬레이션

| 단계 | 대상 | 조건 |
|------|------|------|
| Primary | C-3 Code Verifier | `verify()` 실행 |
| Secondary | D-1 Think Engine | `should_escalate()=True` → **I-20 경유** (R-01-8) |
| Tertiary | HITL | D-1도 실패 시 → **I-20 경유** |

> **C-3 I-20 경유 판단** (P0-4 §5.2): D2.0-01 §5.11 Notes열에 C-3은 "04, 07"만 기재되어 I-20 미명시이나, R-01-8 거버넌스 규칙이 우선. C-3도 I-20 경유.

### Layer 1 — LLM 브레인 Failover (LOCK-VR-07)

| 단계 | Brain | 비고 |
|------|-------|------|
| Primary | GPT-4o | 코드 검증 수행 |
| Secondary | Claude Sonnet | 연속 3회 실패 시 전환 |
| Tertiary | 로컬 Ollama | Docker sandbox는 LLM과 독립 동작 |

---

## 9. LOCK 값 참조 요약

> LOCK (상세명세 C-1 §3): ABC 패턴: Ask→Bridge→Confirm, 엔진 간 표준 인터페이스. 메서드 시그니처 변경 불가.

> LOCK (상세명세 C-1 §4): Confidence 판정 >=0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL

> LOCK (D2.0-02 §2.3-B): 단일응답 ≤2s, 복합응답 ≤10s, Self-check ≤1s

> LOCK (D2.0-01 §5.11): C-3: CORE, V1:ON, change_lock=false

> LOCK (D2.0-02 §1.3-A): Docker sandbox, timeout 30s, CPU/RAM 상한은 설정 파일로 관리 (구체값은 운영 시 결정)

---

## 10. 예시 JSON

### 10.1 Request 예시

```json
{
  "code": "def add(a, b):\n    return a + b",
  "language": "python",
  "intent": "두 수를 더하는 함수",
  "test_cases": [
    {"name": "basic_add", "input_data": "add(1, 2)", "expected_output": "3", "timeout_ms": 5000}
  ],
  "security_scan": true,
  "timeout_ms": 5000,
  "request_id": "req-c3-20260329-001"
}
```

### 10.2 Response 예시

```json
{
  "confidence": 0.92,
  "is_valid": true,
  "is_correct": true,
  "is_secure": true,
  "syntax_errors": [],
  "logic_errors": [],
  "security_issues": [],
  "test_results": [
    {
      "test_name": "basic_add",
      "passed": true,
      "actual_output": "3",
      "error_message": null,
      "execution_time_ms": 12
    }
  ],
  "complexity_metrics": {
    "cyclomatic_complexity": 1,
    "cognitive_complexity": 0,
    "lines_of_code": 2,
    "maintainability_index": 95.0
  },
  "details": {},
  "timestamp": "2026-03-29T14:40:00Z",
  "engine_id": "C-3"
}
```

---

## 11. Algorithm — 4-Phase 코드 검증 파이프라인 (L3)

> **Status**: APPROVED
> **이슈**: C3-3 (Phase 1 해결) — Algorithm Pseudocode L2→L3
> **게이트 기여**: G1-1 (spec.md Algorithm 섹션 Status=APPROVED)

### 11.0 개요 및 ABC 패턴 매핑 (LOCK-VR-11)

4-Phase 알고리즘은 ABC 패턴(Ask→Bridge→Confirm)의 **Bridge** 단계에 해당한다.

| ABC 단계 | 4-Phase 매핑 | 역할 |
|----------|-------------|------|
| **Ask** | `verify()` 진입 — 입력 검증·전처리 | `CodeVerifyRequest` 유효성 검사 (code, language, intent 필수 필드) |
| **Bridge** | **Phase 1(Parse) → Phase 2(Static Analysis) → Phase 3(Dynamic Execution) → Phase 4(Aggregate)** | 코드 검증 알고리즘 실행, confidence 산출 |
| **Confirm** | `verify()` 후속 — 결과 구성·에스컬레이션 판단 | `CodeVerifyResult` 반환, `should_escalate()` → `get_confidence_threshold()` 비교 |

```
verify(request: CodeVerifyRequest) → CodeVerifyResult
│
├── [Ask]  입력 검증·전처리
│
├── [Bridge]  4-Phase 알고리즘
│   ├── Phase 1: Parse             — 코드 파싱, AST 생성, 구문 유효성 검사
│   ├── Phase 2: Static Analysis   — 정적분석 도구 호출, 결과 정규화
│   ├── Phase 3: Dynamic Execution — Docker Sandbox 내 코드 실행·테스트
│   └── Phase 4: Aggregate         — 정적+동적 결과 종합, confidence 산출
│
└── [Confirm]  CodeVerifyResult 구성 → should_escalate() → 반환
```

### 11.1 Phase 1 — Parse (코드 파싱·구문 검증)

**입력**: `CodeVerifyRequest` (code, language, intent)
**출력**: `ParseResult { ast: ASTNode, language_detected: str, syntax_errors: list[SyntaxError] }`
**예외**: `VRE_INVALID_INPUT` — code가 빈 문자열이거나 지원하지 않는 언어일 경우

```python
SUPPORTED_LANGUAGES = {"python", "typescript", "javascript", "rust", "go", "java"}

def phase_parse(request: CodeVerifyRequest) -> ParseResult:
    """Phase 1: 코드를 파싱하여 AST를 생성하고 구문 유효성을 검사한다.

    Args:
        request: 검증 요청 (code + language + intent)

    Returns:
        ParseResult: AST, 감지된 언어, 구문 오류 목록

    Raises:
        VamosError(VRE_INVALID_INPUT): 코드 파싱 불가 시
    """
    syntax_errors: list[SyntaxError] = []

    # 1-1. 언어 감지 및 검증
    #      사용자 지정 language와 실제 코드 내용 기반 감지 결과를 교차 확인
    detected_lang = detect_language(request.code)
    if request.language not in SUPPORTED_LANGUAGES:
        raise VamosError(
            error_code="VRE_INVALID_INPUT",
            message=f"Unsupported language: '{request.language}'",
            recoverable=False
        )
    if detected_lang != request.language:
        # 불일치 시 사용자 지정 언어를 우선하되 경고 기록
        log_warning(f"Language mismatch: declared={request.language}, detected={detected_lang}")

    # 1-2. 언어별 파서로 AST 생성
    #      Python: ast.parse(), JS/TS: tree-sitter, Rust: syn, Go: go/parser, Java: javalang
    parser = get_parser(request.language)
    try:
        ast = parser.parse(request.code)
    except ParseError as e:
        raise VamosError(
            error_code="VRE_INVALID_INPUT",
            message=f"Code parse failed at line {e.line}: {e.message}",
            recoverable=False
        )

    # 1-3. 구문 유효성 검사 — AST 워킹으로 경고 수준 이슈 수집
    syntax_errors = collect_syntax_issues(ast, request.language)

    # 1-4. 치명적 구문 오류(severity="error") 존재 시 조기 실패
    critical_errors = [e for e in syntax_errors if e.severity == "error"]
    if critical_errors:
        raise VamosError(
            error_code="VRE_INVALID_INPUT",
            message=f"Critical syntax errors found: {len(critical_errors)} error(s)",
            recoverable=False
        )

    return ParseResult(
        ast=ast,
        language_detected=request.language,
        syntax_errors=syntax_errors
    )
```

**시간복잡도**: **O(L)** — L = 코드 줄 수(토큰 수). 언어별 파서는 선형 시간 파싱. 일반적 입력(L≤5000) 기준 ~10ms.

### 11.2 Phase 2 — Static Analysis (정적분석 도구 호출)

**입력**: `ParseResult`
**출력**: `StaticAnalysisResult { logic_errors: list[LogicError], security_issues: list[SecurityIssue], complexity_metrics: ComplexityMetrics }`
**예외**: `VRE_ENGINE_FAILURE` — 정적분석 도구 내부 오류 시 (recoverable=True)

> **security_rules.md 연동 포인트 (P1-4)**: Phase 2의 보안 스캔은 `security_rules.md`(P1-4에서 정의)의 규칙 집합을 로드하여 적용한다. 본 의사코드에서는 인터페이스(`load_security_rules()`)만 명시하며, 규칙 상세(OWASP Top 10 + CWE 매핑)는 P1-4에서 별도 정의한다.

```python
def phase_static_analysis(
    parse_result: ParseResult,
    security_scan: bool
) -> StaticAnalysisResult:
    """Phase 2: 정적분석 도구를 호출하여 논리 오류·보안 취약점·복잡도를 분석한다.

    Args:
        parse_result: Phase 1 산출물 (AST + 언어 정보)
        security_scan: 보안 스캔 포함 여부 (CodeVerifyRequest.security_scan)

    Returns:
        StaticAnalysisResult: 논리 오류, 보안 취약점, 복잡도 메트릭

    Raises:
        VamosError(VRE_ENGINE_FAILURE): 정적분석 도구 오류 시
    """
    lang = parse_result.language_detected
    ast = parse_result.ast
    logic_errors: list[LogicError] = []
    security_issues: list[SecurityIssue] = []

    # 2-1. Linter 호출 — 언어별 린터 인터페이스
    #      Python: pylint/ruff, JS/TS: eslint, Rust: clippy, Go: staticcheck, Java: spotbugs
    linter = get_linter(lang)
    try:
        lint_results = linter.analyze(ast)
    except ToolError as e:
        raise VamosError(
            error_code="VRE_ENGINE_FAILURE",
            message=f"Linter ({lang}) failed: {e}",
            recoverable=True
        )

    # 2-2. Lint 결과 정규화 → LogicError 변환
    for finding in lint_results:
        logic_errors.append(LogicError(
            line=finding.line,
            error_type=normalize_error_type(finding.rule_id),  # dead_code, infinite_loop 등
            description=finding.message,
            severity=map_severity(finding.level)  # critical|major|minor
        ))

    # 2-3. Type Checker 호출 (지원 언어만)
    #      Python: mypy/pyright, TS: tsc --noEmit, Rust: 컴파일러 내장, Go: go vet
    type_checker = get_type_checker(lang)
    if type_checker is not None:
        try:
            type_results = type_checker.check(ast)
        except ToolError as e:
            raise VamosError(
                error_code="VRE_ENGINE_FAILURE",
                message=f"Type checker ({lang}) failed: {e}",
                recoverable=True
            )
        for finding in type_results:
            logic_errors.append(LogicError(
                line=finding.line,
                error_type="type_error",
                description=finding.message,
                severity="major"
            ))

    # 2-4. 보안 스캔 (security_scan=True 시)
    #      security_rules.md(P1-4) 규칙 로드 → AST 기반 패턴 매칭
    if security_scan:
        rules = load_security_rules(lang)  # P1-4 security_rules.md 연동 포인트
        for rule in rules:
            matches = rule.match(ast)
            for m in matches:
                security_issues.append(SecurityIssue(
                    line=m.line,
                    issue_type=rule.issue_type,
                    owasp_category=rule.owasp_category,
                    cwe_id=rule.cwe_id,
                    severity=rule.severity,
                    description=m.description,
                    recommendation=rule.recommendation
                ))

    # 2-5. 복잡도 메트릭 산출
    complexity_metrics = compute_complexity(ast)
    # cyclomatic_complexity: McCabe 복잡도 (분기 수 기반)
    # cognitive_complexity: Sonar 인지 복잡도
    # lines_of_code: 유효 코드 줄 수 (빈 줄·주석 제외)
    # maintainability_index: MI = 171 - 5.2·ln(HV) - 0.23·CC - 16.2·ln(LOC)

    return StaticAnalysisResult(
        logic_errors=logic_errors,
        security_issues=security_issues,
        complexity_metrics=complexity_metrics
    )
```

**시간복잡도**: **O(L·R)** — L = 코드 줄 수, R = 보안 규칙 수. Linter/Type checker는 AST 워킹 O(L), 보안 패턴 매칭은 규칙당 O(L). 일반적 입력(L≤5000, R≤100) 기준 ~100ms.

### 11.3 Phase 3 — Dynamic Execution (Docker Sandbox 실행)

**입력**: `CodeVerifyRequest` (code, language, test_cases), `ParseResult`, `remaining_ms` (verify() ��여 시간)
**출력**: `DynamicResult { test_results: list[TestResult], sandbox_status: str }`
**예외**: `SANDBOX_TIMEOUT`, `SANDBOX_OOM`, `SANDBOX_POLICY_DENIED`

> LOCK (D2.0-02 §1.3-A): Docker sandbox, timeout 30s

> **CONF-VRE-006 준수**: CPU/RAM 리소스 제한을 하드코딩하지 않는다. 설정 파일에서 관리하며, 구체값은 운영 시 결정한다.

```python
def phase_dynamic_execution(
    request: CodeVerifyRequest,
    parse_result: ParseResult,
    remaining_ms: int = 30000
) -> DynamicResult:
    """Phase 3: Docker Sandbox 내에서 코드를 실행하고 테스트 결과를 수집한다.

    LOCK-VR-15: Docker sandbox, timeout 30s.
    CONF-VRE-006: CPU/RAM 상한은 설정 파일로 관리.

    Args:
        request: 검증 요청 (code, language, test_cases)
        parse_result: Phase 1 산출물 (AST, 언어 정보)
        remaining_ms: verify() 레벨 잔여 시간(ms). sandbox timeout과 min 적용

    Returns:
        DynamicResult: 테스트 실행 결과 + sandbox 상태

    Raises:
        VamosError(SANDBOX_TIMEOUT): 실행 시간 30s 초과
        VamosError(SANDBOX_OOM): 메모리 초과
        VamosError(SANDBOX_POLICY_DENIED): 보안 정책 위반
    """
    test_results: list[TestResult] = []
    lang = parse_result.language_detected

    # 3-0. 테스트 케이스 미제공 시 — 기본 실행 검증만 수행
    if request.test_cases is None or len(request.test_cases) == 0:
        return DynamicResult(
            test_results=[],
            sandbox_status="SKIPPED_NO_TESTS"
        )

    # ─── 3-1. 설정 파일에서 리소스 제한 로드 (CONF-VRE-006) ───
    sandbox_config = load_sandbox_config()
    # sandbox_config 예시:
    #   timeout_s: 30          ← LOCK-VR-15 기본값
    #   cpu_limit: <설정 파일>  ← 구체값 운영 시 결정
    #   memory_limit: <설정 파일> ← 구체값 운영 시 결정
    #   network: "none"        ← 기본 차단
    #   filesystem: "tmpfs"    ← 임시 볼륨만

    # ─── 3-2. Docker 컨테이너 생성 ───
    #      실효 timeout = min(sandbox 설정값, verify() 잔여 시간)
    effective_timeout_s = min(sandbox_config.timeout_s, remaining_ms / 1000)
    container = create_sandbox_container(
        image=get_language_image(lang),  # 언어별 런타임 이미지
        timeout_s=effective_timeout_s,            # min(LOCK-VR-15: 30s, remaining)
        cpu_limit=sandbox_config.cpu_limit,        # 설정 파일 관리 (CONF-VRE-006)
        memory_limit=sandbox_config.memory_limit,  # 설정 파일 관리 (CONF-VRE-006)
        network_mode="none",                       # 네트워크 기본 차단
        filesystem="tmpfs"                         # 임시 볼륨만 마운트
    )

    try:
        # ─── 3-3. 코드 주입 ───
        #      호스트 경로 직접 접근 금지 — 문자열 전달 방식
        container.inject_code(request.code, filename=f"main.{get_extension(lang)}")

        # ─── 3-4. 테스트 케이스별 실행 ───
        for tc in request.test_cases:
            tc_start = now_ms()

            try:
                # 개별 테스트 타임아웃: min(tc 설정값, 실효 sandbox timeout)
                exec_result = container.execute(
                    command=build_test_command(lang, tc),
                    timeout_ms=min(tc.timeout_ms, int(effective_timeout_s * 1000))
                )

                actual_output = exec_result.stdout.strip()
                passed = (actual_output == tc.expected_output)
                tc_elapsed = now_ms() - tc_start

                test_results.append(TestResult(
                    test_name=tc.name,
                    passed=passed,
                    actual_output=actual_output,
                    error_message=exec_result.stderr if not passed else None,
                    execution_time_ms=tc_elapsed
                ))

            except SandboxTimeoutError:
                test_results.append(TestResult(
                    test_name=tc.name,
                    passed=False,
                    actual_output=None,
                    error_message="Test execution timed out",
                    execution_time_ms=min(tc.timeout_ms, int(effective_timeout_s * 1000))
                ))

            except SandboxOOMError:
                raise VamosError(
                    error_code="SANDBOX_OOM",
                    message=f"Out of memory during test '{tc.name}'",
                    recoverable=True
                )

            except SandboxPolicyError as e:
                raise VamosError(
                    error_code="SANDBOX_POLICY_DENIED",
                    message=f"Sandbox policy violation: {e}",
                    recoverable=False
                )

        sandbox_status = "COMPLETED"

    except VamosError:
        raise  # SANDBOX_OOM, SANDBOX_POLICY_DENIED 재전파

    finally:
        # ─── 3-5. 컨테이너 정리 (항상 실행) ───
        container.destroy()

    # ─── 3-6. 전체 실행 시간 검증 (실효 timeout 적용) ───
    total_execution_ms = sum(tr.execution_time_ms for tr in test_results)
    if total_execution_ms > effective_timeout_s * 1000:
        raise VamosError(
            error_code="SANDBOX_TIMEOUT",
            message=f"Total sandbox execution exceeded {effective_timeout_s}s "
                    f"(elapsed: {total_execution_ms}ms)",
            recoverable=True
        )

    return DynamicResult(
        test_results=test_results,
        sandbox_status=sandbox_status
    )
```

**Sandbox 실행 플로우 요약**:

```
[Phase 3 진입]
    │
    ├── test_cases 미제공? ──Yes──→ SKIPPED_NO_TESTS 반환
    │
    ├── 설정 파일 로드 (CONF-VRE-006)
    │
    ├── Docker 컨테이너 생성
    │   ├── 언어별 런타임 이미지
    │   ├── timeout: min(30s, remaining_ms) — LOCK-VR-15 + verify() 잔여 시간
    │   ├── CPU/RAM: 설정 파일 참조 (CONF-VRE-006)
    │   ├── 네트워크: 차단
    │   └── 파일시스템: tmpfs
    │
    ├── 코드 주입 (문자열 전달, 호스트 경로 접근 금지)
    │
    ├── 테스트 케이스별 실행·결과 수집
    │   ├── 성공 → TestResult(passed=True/False)
    │   ├── 타임아웃 → TestResult(passed=False, error)
    │   ├── OOM → SANDBOX_OOM 예외
    │   └── 정책위반 → SANDBOX_POLICY_DENIED 예외
    │
    ├── 컨테이너 정리 (finally — 항상 실행)
    │
    └── 전체 시간 검증 (30s 이내)
```

**시간복잡도**: **O(T·E)** — T = 테스트 케이스 수, E = 개별 테스트 실행 시간. 실행 시간은 코드 특성에 의존하나, LOCK-VR-15에 의해 **전체 30s 이내 완료가 강제**된다. 개별 테스트 타임아웃(`tc.timeout_ms`, 최대 30s)으로 무한 실행을 방지한다.

**Timeout 완료 보장 전략** (5중 방어):
1. **verify() 레벨**: `remaining_ms` 전달 — sandbox timeout을 verify() 잔여 시간으로 제한
2. **컨테이너 레벨**: `create_sandbox_container(timeout_s=effective_timeout_s)` — OS 레벨 cgroup timeout 강제 (`min(LOCK-VR-15: 30s, remaining_ms)`)
3. **테스트 레벨**: `min(tc.timeout_ms, effective_timeout_s * 1000)` — 개별 테스트가 실효 타임아웃을 초과하지 못함
4. **후위 검증**: 전체 실행 시간 합산 후 실효 timeout 초과 시 `SANDBOX_TIMEOUT` 발생
5. **finally 보장**: 타임아웃/OOM 발생 시에도 `container.destroy()` 실행으로 자원 누수 방지

### 11.4 Phase 4 — Aggregate (결과 종합·Confidence 산출)

**입력**: `StaticAnalysisResult`, `DynamicResult`, `CodeVerifyRequest`
**출력**: `AggregateResult { confidence: float, judgment: Literal["PASS","REVIEW","FAIL"], is_valid: bool, is_correct: bool, is_secure: bool }`
**예외**: `VRE_CONFIDENCE_RANGE` — 산출된 confidence가 0.0~1.0 범위 외일 경우

> LOCK (상세명세 C-1 §4): Confidence 판정 >=0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL
> 참조: `confidence_thresholds.md`(P0-7) §2 — 판정 정책 정본

```python
def phase_aggregate(
    static_result: StaticAnalysisResult,
    dynamic_result: DynamicResult,
    request: CodeVerifyRequest
) -> AggregateResult:
    """Phase 4: 정적+동적 결과를 종합하여 confidence를 산출하고 판정한다.

    LOCK-VR-05 판정 기준:
      - confidence >= 0.8 → PASS (자동 승인)
      - 0.5 <= confidence < 0.8 → REVIEW (I-19 ApprovalManager 전달)
      - confidence < 0.5 → FAIL (자동 거부 + 근거 첨부)

    Args:
        static_result: Phase 2 산출물 (논리 오류, 보안 취약점, 복잡도)
        dynamic_result: Phase 3 산출물 (테스트 결과)
        request: 원본 요청 (intent 비교용)

    Returns:
        AggregateResult: confidence, judgment, is_valid, is_correct, is_secure

    Raises:
        VamosError(VRE_CONFIDENCE_RANGE): confidence 범위 위반 시
    """
    # 4-1. 기본 confidence 시작값
    confidence = 1.0

    # ── 4-2. 정적분석 결과 감점 ──

    # 4-2a. 논리 오류 감점
    for err in static_result.logic_errors:
        penalty = {"critical": 0.3, "major": 0.1, "minor": 0.02}[err.severity]
        confidence -= penalty

    # 4-2b. 보안 취약점 감점 (보안 위반 시 강한 감산)
    for issue in static_result.security_issues:
        penalty = {"critical": 0.4, "high": 0.25, "medium": 0.1, "low": 0.03}[issue.severity]
        confidence -= penalty

    # 4-2c. 복잡도 감점 (유지보수성 지수 기반)
    if static_result.complexity_metrics.maintainability_index is not None:
        mi = static_result.complexity_metrics.maintainability_index
        if mi < 20:
            confidence -= 0.15  # 매우 낮은 유지보수성
        elif mi < 40:
            confidence -= 0.05  # 낮은 유지보수성

    # ── 4-3. 의도-코드 일치 검증 (intent 활용) ──
    #      request.intent와 코드 구조(정적분석 결과)를 비교하여
    #      의도와 실제 구현 사이의 의미적 불일치 여부를 평가
    intent_match_score = evaluate_intent_alignment(
        intent=request.intent,
        logic_errors=static_result.logic_errors,
        complexity=static_result.complexity_metrics
    )
    # intent_match_score: 0.0~1.0 (1.0 = 완전 일치)
    # 불일치 시 감점: (1 - score) × 0.15
    confidence -= (1.0 - intent_match_score) * 0.15

    # ── 4-4. 동적 실행 결과 반영 ──

    if dynamic_result.sandbox_status == "SKIPPED_NO_TESTS":
        # 테스트 미제공 — 보수적 감점 (동적 검증 불가)
        confidence -= 0.1
        is_correct = True  # 동적 검증 미수행으로 확인된 결함 없음 → 잠정 True
    else:
        # 테스트 통과율 기반 감점
        total_tests = len(dynamic_result.test_results)
        passed_tests = sum(1 for tr in dynamic_result.test_results if tr.passed)
        pass_rate = passed_tests / total_tests if total_tests > 0 else 0.0

        # 통과율에 따른 감점: (1 - pass_rate) × 0.5
        confidence -= (1.0 - pass_rate) * 0.5
        is_correct = (pass_rate == 1.0)

    # ── 4-5. 보안 판정 ──
    is_secure = not any(
        issue.severity in ("critical", "high")
        for issue in static_result.security_issues
    )

    # ── 4-6. NaN 처리 (confidence_thresholds.md §5.2) ──
    if isnan(confidence):
        log_warning("Confidence is NaN — defaulting to FAIL")
        confidence = 0.0

    # ── 4-7. 범위 검증 및 클램핑 ──
    if not (0.0 <= confidence <= 1.0):
        raise VamosError(
            error_code="VRE_CONFIDENCE_RANGE",
            message=f"Confidence {confidence} out of range [0.0, 1.0]",
            recoverable=False
        )

    confidence = max(0.0, min(1.0, confidence))

    # ── 4-8. LOCK-VR-05 판정 (confidence_thresholds.md §2.1) ──
    if confidence >= 0.8:
        judgment = "PASS"
    elif confidence >= 0.5:
        judgment = "REVIEW"
    else:
        judgment = "FAIL"

    # ── 4-9. is_valid 종합 판정 ──
    #      PASS + 기능 정확성 확인 + critical/high 보안 이슈 없음
    is_valid = (judgment == "PASS") and is_correct and is_secure

    return AggregateResult(
        confidence=confidence,
        judgment=judgment,
        is_valid=is_valid,
        is_correct=is_correct,
        is_secure=is_secure
    )
```

**시간복잡도**: **O(LE + SI + TR)** — LE = 논리 오류 수, SI = 보안 이슈 수, TR = 테스트 결과 수. 단순 산술 연산으로 상수 시간에 근접. < 1ms.

### 11.5 전체 파이프라인 통합 (`verify()` 내부)

```python
async def verify(self, request: CodeVerifyRequest) -> CodeVerifyResult:
    """BaseVerifier.verify() 구현 — Ask→Bridge→Confirm.

    LOCK-VR-11: ABC 패턴 매핑
    LOCK-VR-12: 복합응답 ≤10s (C-3은 sandbox 포함 복합 검증)
    LOCK-VR-15: Docker sandbox timeout 30s
    """
    start_time = now_ms()

    # ── Ask ──────────────────────────────────────────
    validate_request(request)  # 필수 필드 검증 (code, language, intent)

    # ── Bridge (4-Phase) ─────────────────────────────

    # Phase 1: Parse — 코드 파싱, AST 생성
    parse_result = phase_parse(request)

    # Phase 2: Static Analysis — 정적분석 도구 호출
    static_result = phase_static_analysis(parse_result, request.security_scan)

    # 타임아웃 중간 체크 (Phase 3 진입 전 — sandbox는 비용이 크므로)
    elapsed = now_ms() - start_time
    if elapsed > request.timeout_ms:
        raise VamosError(
            error_code="VRE_TIMEOUT",
            message=f"Timeout before sandbox execution (elapsed: {elapsed}ms)",
            recoverable=True
        )

    # Phase 3: Dynamic Execution — Docker Sandbox
    #   remaining_ms를 전달하여 sandbox timeout과 verify timeout 중 작은 값 적용
    remaining_ms = request.timeout_ms - (now_ms() - start_time)
    dynamic_result = phase_dynamic_execution(request, parse_result, remaining_ms)

    # Phase 4: Aggregate — 결과 종합, confidence 산출
    agg_result = phase_aggregate(static_result, dynamic_result, request)

    # 최종 타임아웃 체크
    elapsed = now_ms() - start_time
    if elapsed > request.timeout_ms:
        raise VamosError(
            error_code="VRE_TIMEOUT",
            message=f"Code verification exceeded timeout of {request.timeout_ms}ms "
                    f"(elapsed: {elapsed}ms)",
            recoverable=True
        )

    # ── Confirm ──────────────────────────────────────
    result = CodeVerifyResult(
        confidence=agg_result.confidence,
        is_valid=agg_result.is_valid,
        is_correct=agg_result.is_correct,
        is_secure=agg_result.is_secure,
        syntax_errors=parse_result.syntax_errors,
        logic_errors=static_result.logic_errors,
        security_issues=static_result.security_issues,
        test_results=dynamic_result.test_results,
        complexity_metrics=static_result.complexity_metrics,
        details={
            "phases_completed": ["parse", "static_analysis", "dynamic_execution", "aggregate"],
            "sandbox_status": dynamic_result.sandbox_status,
            "judgment": agg_result.judgment
        },
        timestamp=iso8601_now(),
        engine_id="C-3"
    )

    # Confirm: 에스컬레이션 판단 (LOCK-VR-05, R-01-8)
    if await self.should_escalate(result):
        # I-20 Failure/Fallback Manager 경유 → D-1 재검증
        # R-01-8: 직접 호출 금지, 반드시 I-20 경유
        try:
            await escalate_via_i20(result, request)
        except EscalationError as e:
            raise VamosError(
                error_code="VRE_ESCALATION_FAILED",
                message=f"I-20 escalation failed: {e}",
                recoverable=True
            )

    return result
```

### 11.6 시간복잡도 요약 및 LOCK-VR-12 SLA 분석

| Phase | 최악 | 평균 | 일반 입력 실측 예상 | LOCK-VR-12 준수 |
|-------|------|------|-------------------|----------------|
| Phase 1 (Parse) | O(L) | O(L) | ~10ms | ✓ |
| Phase 2 (Static Analysis) | O(L·R) | O(L·R) | ~100ms | ✓ |
| Phase 3 (Dynamic Execution) | O(T·E) | O(T·E) | ≤30s (LOCK-VR-15 상한) | ✓ (별도 sandbox 시간) |
| Phase 4 (Aggregate) | O(LE+SI+TR) | O(LE+SI+TR) | <1ms | ✓ |
| **Phase 1+2+4 합계** | — | — | **~111ms** | ✓ |
| **Phase 3 (Sandbox)** | — | — | **≤30s** | LOCK-VR-15 강제 |

> **L**: 코드 줄 수, **R**: 보안 규칙 수, **T**: 테스트 수, **E**: 개별 테스트 실행 시간, **LE**: 논리 오류 수, **SI**: 보안 이슈 수, **TR**: 테스트 결과 수

**LOCK-VR-12 SLA 매핑**:
- C-3 Code Verifier는 Docker sandbox 실행을 포함하는 **복합 검증**이다.
- LOCK-VR-12(D2.0-02 §2.3-B): 복합응답 ≤10s (파이프라인 전체 S0→S5 기준).
- `base_verifier_abc.md` §7.2: C-3 복합 검증 `timeout_ms` 기본값 ≤5,000ms (파이프라인 10초 예산의 50% 이내).
- Phase 1+2+4는 ~111ms로 파이프라인 오버헤드에 충분한 여유 확보.
- Phase 3(Sandbox)는 LOCK-VR-15에 의해 30s 상한이 별도 적용되며, 일반 테스트(테스트 5개 이내)는 수초 내 완료.
- Phase 3의 실효 timeout = `min(LOCK-VR-15: 30s, verify() 잔여 시간)` — verify() 레벨 timeout_ms가 sandbox 상한보다 작으면 sandbox도 그 이내에 종료.
- **timeout 완료 보장**: verify() 레벨 잔여 시간 전달 + 컨테이너 cgroup timeout + 개별 테스트 timeout + 후위 합산 검증 + finally 정리의 5중 방어.

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| v1.0 | 2026-03-29 | 초기 작성 — P0-9 실행, I/O Schema L3 정의, CONF-VRE-006 준수 | P0-9 |
| v1.1 | 2026-04-06 | P1-3 실행 — Algorithm §11 추가, 4-Phase 코드 검증 파이프라인 의사코드 L3 완성 (C3-3 해결) | P1-3 |
