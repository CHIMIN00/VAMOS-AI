# C-2 Math Verifier — Specification

> **Status**: APPROVED
> **버전**: v1.1
> **Last-reviewed**: 2026-04-06
> **Owner**: 1-1_Verifier-Reasoning-Engines

---

## 1. 개요

본 문서는 C-2 Math Verifier의 I/O Schema를 L3 수준으로 정의한다. 수식·계산의 정확성을 SymPy(기호 연산) 및 NumPy/SciPy(수치 연산)로 교차 검증하고, 단계별 계산 과정과 confidence 기반 판정을 반환한다.

> LOCK (D2.0-01 §5.11): C-2 Math Verifier: CORE, V1:ON, change_lock=false

---

## 2. ABC 계약 매핑 (LOCK-VR-11)

> LOCK (상세명세 C-1 §3): ABC 패턴: Ask→Bridge→Confirm, 엔진 간 표준 인터페이스. 메서드 시그니처 변경 불가.

C-2는 `BaseVerifier` ABC(P0-4 `base_verifier_abc.md`)를 구현한다.

| ABC 메서드 | I/O 매핑 | 단계 |
|-----------|---------|------|
| `verify(request: VerifyRequest) → VerifyResult` | `MathVerifyRequest → MathVerifyResult` | Ask→Bridge→Confirm 전체 |
| `get_confidence_threshold() → float` | 반환값: `0.8` (LOCK-VR-05) | Confirm 판정 기준 |
| `should_escalate(result: VerifyResult) → bool` | `result.confidence < 0.8` → True | Confirm 에스컬레이션 판단 |

---

## 3. Input Schema

### 3.1 MathVerifyRequest

`VerifyRequest`(common_types.md §2.1)를 C-2 전용 필드로 확장한다.

```python
from pydantic import BaseModel, Field
from typing import Optional

class MathVerifyRequest(BaseModel):
    """C-2 Math Verifier 검증 요청.

    Base: VerifyRequest (common_types.md §2.1)
    """

    # --- Base 필드 (VerifyRequest 상속) ---
    expression: str = Field(
        ...,
        min_length=1,
        max_length=50000,
        description="검증 대상 수식/계산식 (LaTeX 또는 ASCII math)"
    )
    context: str = Field(
        default="",
        description="수학적 맥락 (통계, 재무, 물리 등)"
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

    # --- C-2 전용 필드 ---
    expected_result: Optional[str] = Field(
        default=None,
        description="예상 결과값. 제공 시 계산 결과와 비교"
    )
    precision: int = Field(
        default=6,
        ge=2,
        le=15,
        description="소수점 정밀도 (기본 6, 최소 2, 최대 15). ge=2: precision<2이면 rtol≥1(≥100% 허용오차)로 수치 매칭 무력화"
    )
```

| 필드 | 타입 | 필수 | 제약조건 | 기본값 | 근거 |
|------|------|------|---------|--------|------|
| `expression` | `str` | Yes | `1 ≤ len ≤ 50000` | — | 상세명세 C-2 §1 |
| `context` | `str` | No | — | `""` | 상세명세 C-2 §1 |
| `timeout_ms` | `int` | Yes | `> 0` | — | R-01-3 |
| `request_id` | `str` | Yes | `min_length=1` | — | common_types.md §2.1 |
| `expected_result` | `Optional[str]` | No | — | `None` | 상세명세 C-2 §1 |
| `precision` | `int` | No | `0 ≤ v ≤ 15` | `6` | 상세명세 C-2 §2 |

---

## 4. Output Schema

### 4.1 MathVerifyResult

`VerifyResult`(common_types.md §2.2)를 C-2 전용 필드로 확장한다.

> LOCK (상세명세 C-1 §4): Confidence 판정 >=0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL

> 참조: `confidence_thresholds.md`(P0-7) — 판정 정책 정본

```python
class MathVerifyResult(BaseModel):
    """C-2 Math Verifier 검증 결과.

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
        description="수학적 정확성 통과 여부"
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
        default="C-2",
        pattern=r"^C-2$",
        description="C-2 Math Verifier"
    )

    # --- C-2 전용 필드 ---
    is_correct: bool = Field(
        ...,
        description="계산 결과의 정확성"
    )
    computed_result: str = Field(
        ...,
        description="엔진이 계산한 결과값"
    )
    error_type: Optional[str] = Field(
        default=None,
        description="오류 유형 (unit_error, dimension_mismatch, overflow, precision_loss 등)"
    )
    step_by_step: list["ComputeStep"] = Field(
        default_factory=list,
        description="단계별 계산 과정"
    )
    symbolic_verification: Optional[str] = Field(
        default=None,
        description="SymPy 기호 검증 결과 (예: 'simplify(lhs-rhs)==0')"
    )
```

| 필드 | 타입 | 필수 | 제약조건 | 기본값 | 근거 |
|------|------|------|---------|--------|------|
| `confidence` | `float` | Yes | `0.0 ≤ v ≤ 1.0` | — | R-01-4, LOCK-VR-05 |
| `is_valid` | `bool` | Yes | — | — | common_types.md §2.2 |
| `is_correct` | `bool` | Yes | — | — | 상세명세 C-2 §1 |
| `computed_result` | `str` | Yes | — | — | 상세명세 C-2 §1 |
| `error_type` | `Optional[str]` | No | — | `None` | 상세명세 C-2 §1 |
| `step_by_step` | `list[ComputeStep]` | No | — | `[]` | 상세명세 C-2 §1 |
| `symbolic_verification` | `Optional[str]` | No | — | `None` | 상세명세 C-2 §2 |

---

## 5. 엔진 전용 타입 정의 (그룹 F)

> P0-6 `common_types.md` §8에서 본 spec.md로 정식 정의 위임.

### 5.1 ComputeStep

```python
class ComputeStep(BaseModel):
    """단계별 계산 과정.

    C-2 MathVerifyResult.step_by_step에서 사용.
    common_types.md §8 그룹 F: 본 spec.md에서 정식 정의.
    """

    step_number: int = Field(
        ...,
        ge=1,
        description="계산 단계 번호 (1부터 시작)"
    )
    operation: str = Field(
        ...,
        description="수행한 연산 (예: 'simplify', 'differentiate', 'integrate', 'substitute')"
    )
    input_expression: str = Field(
        ...,
        description="이 단계의 입력 수식"
    )
    output_expression: str = Field(
        ...,
        description="이 단계의 출력 수식/결과"
    )
    method: Literal["symbolic", "numeric", "hybrid"] = Field(
        ...,
        description="계산 방법: symbolic(SymPy), numeric(NumPy/SciPy), hybrid(교차 검증)"
    )
    is_verified: bool = Field(
        default=True,
        description="이 단계의 결과가 교차 검증되었는지 여부"
    )
```

| 필드 | 타입 | 필수 | 제약조건 |
|------|------|------|---------|
| `step_number` | `int` | Yes | `≥ 1` |
| `operation` | `str` | Yes | — |
| `input_expression` | `str` | Yes | — |
| `output_expression` | `str` | Yes | — |
| `method` | `Literal[...]` | Yes | enum 3종 |
| `is_verified` | `bool` | No | — |

### 5.2 파이프라인 중간 타입 (Algorithm §10 내부용)

> §10 Algorithm 파이프라인의 Phase 간 데이터 전달에 사용되는 내부 타입이다. 외부 I/O 계약(§3, §4)이 아닌 엔진 내부 구현 타입.

```python
class ParseResult(BaseModel):
    """Phase 1 → Phase 2 전달 타입."""
    sympy_expr: Any          # SymPy Expr 객체
    expected_expr: Optional[Any]  # expected_result 파싱 결과
    input_format: Literal["latex", "mathml", "ascii"]
    parse_warnings: list[str] = Field(default_factory=list)

class DimensionCheckResult(BaseModel):
    """Phase 2 차원 검증 결과. Phase 4에서도 참조."""
    is_consistent: bool      # 차원 일관성 여부
    mismatch_detail: Optional[str] = None  # 불일치 시 상세 (예: "lhs=[L·T⁻¹], rhs=[L·T⁻²]")

class NormalizeResult(BaseModel):
    """Phase 2 → Phase 3 전달 타입."""
    normalized_expr: Any     # 정규화된 SymPy Expr
    expected_normalized: Optional[Any]
    variables: dict[str, Any]  # 치환된 변수 매핑
    dimension_check: DimensionCheckResult

class EvaluateResult(BaseModel):
    """Phase 3 → Phase 4 전달 타입."""
    symbolic_match: Optional[bool]   # 심볼릭 등가 여부 (None=미수행)
    numeric_match: Optional[bool]    # 수치 일치 여부 (None=미수행)
    computed_value: str              # 계산 결과 문자열
    symbolic_proof: Optional[str]    # 심볼릭 증명 (예: "simplify(...)== 0")
    numeric_error: Optional[float]   # 절대 오차
    method_used: Literal["symbolic", "numeric", "hybrid"]

class AggregateResult(BaseModel):
    """Phase 4 산출물. verify()에서 MathVerifyResult 구성에 사용."""
    confidence: float        # 0.0~1.0
    judgment: Literal["PASS", "REVIEW", "FAIL"]
    is_correct: bool
    is_valid: bool
```

---

## 6. Error Schema

> **R-01-7**: error_code + message + recoverable 필수.

| error_code | 설명 | recoverable |
|-----------|------|-------------|
| `VRE_TIMEOUT` | 타임아웃 초과 | True |
| `VRE_INVALID_INPUT` | 수식 파싱 실패 또는 형식 오류 | False |
| `VRE_ENGINE_FAILURE` | 수학 검증 엔진 내부 오류 | True |
| `VRE_CONFIDENCE_RANGE` | confidence 범위 위반 (0.0~1.0 외) | False |
| `VRE_ESCALATION_FAILED` | I-20 경유 D-1 에스컬레이션 실패 | True |

---

## 7. Fallback Chain (R-01-2, R-01-8)

> **R-01-2**: fallback chain 최소 2단계 필수.
> **R-01-8**: I-20 경유 필수, 직접 호출 금지.
> 참조: `failover_policy.md`(P0-8) §5.2

### Layer 2 — 엔진 에스컬레이션

| 단계 | 대상 | 조건 |
|------|------|------|
| Primary | C-2 Math Verifier | `verify()` 실행 |
| Secondary | D-1 Think Engine | `should_escalate()=True` → **I-20 경유** |
| Tertiary | HITL | D-1도 실패 시 → **I-20 경유** |

### Layer 1 — LLM 브레인 Failover (LOCK-VR-07)

| 단계 | Brain | 비고 |
|------|-------|------|
| Primary | GPT-4o | 수학 검증 수행 |
| Secondary | Claude Sonnet | 연속 3회 실패 시 전환 |
| Tertiary | 로컬 Ollama | confidence 저하 가능 — should_escalate() 트리거 증가 |

---

## 8. LOCK 값 참조 요약

> LOCK (상세명세 C-1 §3): ABC 패턴: Ask→Bridge→Confirm, 엔진 간 표준 인터페이스. 메서드 시그니처 변경 불가.

> LOCK (상세명세 C-1 §4): Confidence 판정 >=0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL

> LOCK (D2.0-02 §2.3-B): 단일응답 ≤2s, 복합응답 ≤10s, Self-check ≤1s

> LOCK (D2.0-01 §5.11): C-2: CORE, V1:ON, change_lock=false

---

## 9. 예시 JSON

### 9.1 Request 예시

```json
{
  "expression": "\\int_0^1 x^2 dx",
  "expected_result": "1/3",
  "context": "기본 적분",
  "precision": 6,
  "timeout_ms": 1000,
  "request_id": "req-c2-20260329-001"
}
```

### 9.2 Response 예시

```json
{
  "confidence": 1.0,
  "is_valid": true,
  "is_correct": true,
  "computed_result": "0.333333",
  "error_type": null,
  "step_by_step": [
    {
      "step_number": 1,
      "operation": "integrate",
      "input_expression": "x^2",
      "output_expression": "x^3/3",
      "method": "symbolic",
      "is_verified": true
    },
    {
      "step_number": 2,
      "operation": "evaluate_definite",
      "input_expression": "[x^3/3]_0^1",
      "output_expression": "1/3",
      "method": "symbolic",
      "is_verified": true
    }
  ],
  "symbolic_verification": "simplify(integrate(x**2, (x, 0, 1)) - Rational(1, 3)) == 0",
  "details": {},
  "timestamp": "2026-03-29T14:35:00Z",
  "engine_id": "C-2"
}
```

---

## 10. Algorithm — 4-Phase 수학 검증 파이프라인 (L3)

> **Status**: APPROVED
> **이슈**: C2-3 (Phase 1 해결) — Algorithm Pseudocode L2→L3
> **게이트 기여**: G1-1 (spec.md Algorithm 섹션 Status=APPROVED)

### 10.0 개요 및 ABC 패턴 매핑 (LOCK-VR-11)

4-Phase 파이프라인은 ABC 패턴(Ask→Bridge→Confirm)의 **Bridge** 단계에 해당한다.

| ABC 단계 | 수행 내용 | C-2 매핑 |
|----------|----------|----------|
| **Ask** | `verify()` 진입 — 입력 검증·전처리 | `MathVerifyRequest` 유효성 검사 |
| **Bridge** | **Phase 1(Parse) → Phase 2(Normalize) → Phase 3(Evaluate) → Phase 4(Aggregate)** | 수학 검증 알고리즘 실행, confidence 산출 |
| **Confirm** | `verify()` 후속 — 결과 구성·에스컬레이션 판단 | `MathVerifyResult` 반환, `should_escalate()` → `get_confidence_threshold()` 비교 |

```
[Ask]   MathVerifyRequest 유효성 검사 (expression 비어있지 않음, precision 범위)
│
├── [Bridge]  4-Phase 파이프라인
│   ├── Phase 1: Parse      — 수식 파싱, SymPy 표현식 변환
│   ├── Phase 2: Normalize  — 변수 치환, 단위 변환, 차원 일관성 검사
│   ├── Phase 3: Evaluate   — SymPy 기호 연산 + NumPy 수치 연산 이중 검증
│   └── Phase 4: Aggregate  — confidence 산출·LOCK-VR-05 판정
│
└── [Confirm]  MathVerifyResult 구성 → should_escalate() → 반환
```

### 10.1 수치 정밀도 정책: float vs Decimal 선택 기준

| 조건 | 선택 | 근거 |
|------|------|------|
| `precision ≤ 6` (기본값) | **float** (IEEE 754 double) | 유효숫자 ~15자리, 일반 수학 검증에 충분. NumPy 연산 호환. |
| `precision > 6` 이고 금융·통계 맥락 (`context`에 "financial", "currency", "accounting" 포함) | **Decimal** (Python `decimal.Decimal`, prec=`precision+4`) | 부동소수점 반올림 오차 방지. 정확한 십진 연산 필요. |
| 심볼릭 연산 (SymPy) | **Rational/Exact** | SymPy `Rational`, `pi`, `E` 등 정확한 기호 표현 사용. 수치 비교 시에만 `evalf(precision)` 호출. |

> **prec=precision+4 근거**: 중간 연산 과정에서의 정밀도 손실을 보상하기 위한 추가 여유 자릿수.

### 10.2 Phase 1 — Parse (수식 파싱)

**입력**: `MathVerifyRequest` (expression, context, expected_result?)
**출력**: `ParseResult { sympy_expr: Expr, expected_expr: Optional[Expr], input_format: str, parse_warnings: list[str] }`
**예외**: `VRE_INVALID_INPUT` — expression이 파싱 불가능한 형식일 때

```python
from sympy import sympify, latex, Symbol
from sympy.parsing.latex import parse_latex
import re

def phase_parse(request: MathVerifyRequest) -> ParseResult:
    """Phase 1: 입력 수식을 SymPy 표현식으로 변환한다.

    지원 형식: LaTeX, MathML, ASCII math (SymPy 구문).
    LaTeX 입력은 parse_latex()로, MathML은 mathml_to_sympy()로,
    ASCII/plain text는 sympify()로 처리한다.

    Args:
        request: MathVerifyRequest

    Returns:
        ParseResult: SymPy 표현식 + 메타데이터

    Raises:
        VRE_INVALID_INPUT: 파싱 실패 시
    """
    parse_warnings: list[str] = []

    # 1-1. 입력 형식 감지
    input_format = detect_format(request.expression)
    #   detect_format 규칙:
    #     - '<math' 또는 '<mrow' 등 MathML 태그 포함 → "mathml"
    #     - '\\' + LaTeX 명령어(int, frac, sum, sqrt 등) 포함 → "latex"
    #     - 그 외 → "ascii"

    # 1-2. SymPy 표현식 변환
    try:
        if input_format == "mathml":
            from sympy.parsing.mathml import parse_mathml
            sympy_expr = parse_mathml(request.expression)
        elif input_format == "latex":
            sympy_expr = parse_latex(request.expression)
        else:
            # sympify: 문자열 → SymPy 표현식
            # locals=None: 사용자 정의 심볼 자동 생성
            # evaluate=False: 입력 구조 보존 (Phase 2에서 정규화)
            sympy_expr = sympify(
                request.expression,
                locals=None,
                evaluate=False
            )
    except (SympifyError, LaTeXParsingError, ValueError) as e:
        raise VamosError(
            error_code="VRE_INVALID_INPUT",
            message=f"수식 파싱 실패: {str(e)}",
            recoverable=False
        )

    # 1-3. expected_result 파싱 (제공된 경우)
    expected_expr = None
    if request.expected_result is not None:
        try:
            expected_expr = sympify(
                request.expected_result,
                evaluate=True  # 기대값은 즉시 평가
            )
        except SympifyError:
            parse_warnings.append(
                f"expected_result 파싱 실패: '{request.expected_result}' — 수치 비교만 수행"
            )

    # 1-4. 기본 유효성 검사
    if sympy_expr is None or sympy_expr == sympify("nan"):
        raise VamosError(
            error_code="VRE_INVALID_INPUT",
            message="파싱 결과가 None 또는 NaN",
            recoverable=False
        )

    return ParseResult(
        sympy_expr=sympy_expr,
        expected_expr=expected_expr,
        input_format=input_format,
        parse_warnings=parse_warnings
    )
```

**시간복잡도**: **O(T)** — T = expression 토큰 수. `parse_latex`와 `sympify`는 입력 길이에 선형. LOCK-VR-12(≤2s) 내 처리 가능: 일반 수식(T≤1000) 기준 ~10ms.

### 10.3 Phase 2 — Normalize (수식 정규화 및 차원 검증)

**입력**: `ParseResult`, `MathVerifyRequest.context`
**출력**: `NormalizeResult { normalized_expr: Expr, expected_normalized: Optional[Expr], variables: dict[str,Symbol], dimension_check: DimensionCheckResult }`
**예외**: 없음 (차원 불일치는 `DimensionCheckResult.is_consistent=False`로 기록, 프로세스 중단 아님)

```python
from sympy import simplify, nsimplify, symbols, Rational
from sympy.physics.units import convert_to, meter, second, kilogram

def phase_normalize(
    parse_result: ParseResult,
    context: str
) -> NormalizeResult:
    """Phase 2: 수식을 정규화하고 차원 일관성을 검사한다.

    단계:
      2-1. 변수 치환: 관례적 약어를 표준 심볼로 통일
      2-2. 단위 변환: 혼합 단위를 SI 기본 단위로 통일
      2-3. 차원 일관성 검사 (dimensional analysis)
      2-4. 수식 정규화: evaluate=True로 자동 간소화

    Args:
        parse_result: Phase 1 산출물
        context: 수학적 맥락 문자열

    Returns:
        NormalizeResult: 정규화된 표현식 + 차원 검사 결과
    """
    expr = parse_result.sympy_expr
    variables: dict[str, Symbol] = {}

    # 2-1. 변수 치환 — 맥락 기반 표준 심볼 매핑
    #   예: 물리 맥락에서 v→velocity, a→acceleration
    #   예: 통계 맥락에서 mu→mean, sigma→std_dev
    variable_map = build_variable_map(context)
    #   build_variable_map: context 키워드로 도메인 판별 후
    #   해당 도메인의 관례적 변수 매핑 딕셔너리 반환
    for old_sym, new_sym in variable_map.items():
        expr = expr.subs(old_sym, new_sym)
        variables[str(new_sym)] = new_sym

    # 2-2. 단위 변환 — 물리량 맥락에서만 활성화
    has_units = detect_units(expr)
    #   detect_units: expr의 AST를 순회하여 sympy.physics.units 모듈의
    #   단위 심볼(meter, second, kilogram 등)이 포함되어 있는지 검사.
    #   반환: bool (True면 물리 단위 포함)
    if has_units:
        # 모든 단위를 SI 기본 단위(m, s, kg, K, A, mol, cd)로 변환
        expr = convert_to_si(expr)
        #   convert_to_si: sympy.physics.units.convert_to 래퍼
        #   예: km → 1000*m, min → 60*s

    # 2-3. 차원 일관성 검사 (Dimensional Analysis)
    dimension_check = check_dimensions(expr)
    #   check_dimensions 로직:
    #     (a) 덧셈/뺄셈 양변의 차원이 동일한지 검사
    #     (b) 등식(Eq)이면 좌변·우변 차원 비교
    #     (c) 불일치 시 DimensionCheckResult(is_consistent=False,
    #         mismatch_detail="lhs: [L·T⁻¹], rhs: [L·T⁻²]") 반환
    #     (d) 단위 미포함 순수 수식이면 DimensionCheckResult(is_consistent=True,
    #         mismatch_detail=None) 반환 (차원 검사 N/A)

    # 2-4. 수식 정규화 — 간소화 및 표준형 변환
    normalized_expr = simplify(expr)

    # expected_result도 동일 정규화 적용
    expected_normalized = None
    if parse_result.expected_expr is not None:
        expected_normalized = simplify(
            parse_result.expected_expr.subs(
                {old: new for old, new in variable_map.items()}
            )
        )

    return NormalizeResult(
        normalized_expr=normalized_expr,
        expected_normalized=expected_normalized,
        variables=variables,
        dimension_check=dimension_check
    )
```

#### 10.3.1 차원 검증 로직 상세

```python
from sympy.physics.units.dimensions import Dimension
from sympy import Add, Eq

def check_dimensions(expr) -> DimensionCheckResult:
    """차원 일관성 검사.

    규칙:
      1. Add(덧셈/뺄셈) 노드의 모든 피연산자는 동일 차원이어야 한다.
      2. Eq(등식) 노드의 좌변·우변은 동일 차원이어야 한다.
      3. 단위 미포함 순수 수학 수식은 무차원(dimensionless)으로 일관적.

    Returns:
        DimensionCheckResult:
            is_consistent: bool — 차원 일치 여부
            mismatch_detail: Optional[str] — 불일치 상세
    """
    mismatches: list[str] = []

    # Add 노드 순회
    for node in expr.atoms(Add):
        dims = [get_dimension(arg) for arg in node.args]
        if len(set(dims)) > 1:
            mismatches.append(
                f"덧셈/뺄셈 차원 불일치: {dims}"
            )

    # Eq 노드 검사
    if isinstance(expr, Eq):
        lhs_dim = get_dimension(expr.lhs)
        rhs_dim = get_dimension(expr.rhs)
        if lhs_dim != rhs_dim:
            mismatches.append(
                f"등식 차원 불일치: lhs={lhs_dim}, rhs={rhs_dim}"
            )

    return DimensionCheckResult(
        is_consistent=(len(mismatches) == 0),
        mismatch_detail="; ".join(mismatches) if mismatches else None
    )
```

**시간복잡도**: **O(S·V + U)** — S = 수식 노드 수(AST 크기), V = 변수 수(치환 순회), U = 단위 변환 대상 수. `simplify()`는 최악 O(S²)이나 일반 수식(S≤200)에서 ~50ms. LOCK-VR-12(≤2s) 내 처리 가능.

### 10.4 Phase 3 — Evaluate (이중 검증: 심볼릭 + 수치)

**입력**: `NormalizeResult`, `MathVerifyRequest` (precision, expected_result)
**출력**: `EvaluateResult { symbolic_match: Optional[bool], numeric_match: Optional[bool], computed_value: str, symbolic_proof: Optional[str], numeric_error: Optional[float], method_used: str }`
**예외**: `VRE_ENGINE_FAILURE` — SymPy/NumPy 내부 오류 시 (recoverable=True)

```python
from sympy import simplify, Eq, N, oo, zoo, nan as sympy_nan
from sympy import Abs as sym_abs
import numpy as np
from decimal import Decimal, getcontext

def phase_evaluate(
    norm_result: NormalizeResult,
    request: MathVerifyRequest
) -> EvaluateResult:
    """Phase 3: SymPy 기호 연산과 NumPy 수치 연산으로 이중 검증한다.

    전략:
      (A) 심볼릭 검증: simplify(expr - expected) == 0 여부
      (B) 수치 검증: 부동소수점/Decimal 수치 비교, 오차 허용 적용
      (C) 교차 검증: (A)와 (B) 결과가 불일치하면 method="hybrid"로 기록

    Args:
        norm_result: Phase 2 산출물
        request: 원본 요청 (precision, expected_result 참조)

    Returns:
        EvaluateResult: 심볼릭/수치 검증 결과

    Raises:
        VRE_ENGINE_FAILURE: 연산 실패 시
    """
    expr = norm_result.normalized_expr
    expected = norm_result.expected_normalized
    precision = request.precision

    symbolic_match: Optional[bool] = None
    numeric_match: Optional[bool] = None
    symbolic_proof: Optional[str] = None
    numeric_error: Optional[float] = None
    computed_value: str = ""
    method_used: str = "symbolic"  # 기본값

    # ── (A) 심볼릭 검증 ──────────────────────────────
    #   expected_result가 제공된 경우 simplify(expr - expected) == 0 검사.
    #   free symbol이 있어도 심볼릭 등가성 검증은 유효 (예: x+x vs 2x).
    if expected is not None:
        try:
            diff = simplify(expr - expected)
            symbolic_match = (diff == 0)
            symbolic_proof = f"simplify({expr} - {expected}) == {diff}"

            if not symbolic_match:
                # 추가 시도: trigsimp, expand 등 대안 간소화
                from sympy import trigsimp, expand
                diff_alt = trigsimp(expand(expr - expected))
                if diff_alt == 0:
                    symbolic_match = True
                    symbolic_proof = f"trigsimp(expand({expr} - {expected})) == 0"
        except Exception as e:
            symbolic_proof = f"심볼릭 검증 실패: {str(e)}"
            # symbolic_match는 None 유지 — 수치 검증으로 fallback

    # ── (B) 수치 검증 ────────────────────────────────
    #   free symbol 존재 여부에 따라 수치 검증 전략 분기
    has_free_symbols = len(expr.free_symbols) > 0

    try:
        if has_free_symbols and expected is not None:
            # free symbol 포함 수식: 랜덤 대입 교차 검증 (NumPy 활용)
            # 예: expr=x**2+x, expected=x*(x+1) → 여러 x값에서 수치 비교
            free_syms = sorted(expr.free_symbols, key=str)
            rng = np.random.default_rng(seed=42)  # 재현성 보장
            test_points = rng.uniform(-10.0, 10.0, size=(20, len(free_syms)))

            from sympy import lambdify
            f_expr = lambdify(free_syms, expr, modules=["numpy"])
            f_expected = lambdify(free_syms, expected, modules=["numpy"])

            mismatches = 0
            max_error = 0.0
            for point in test_points:
                try:
                    val_expr = float(f_expr(*point))
                    val_expected = float(f_expected(*point))
                    err = abs(val_expr - val_expected)
                    max_error = max(max_error, err)
                    atol = 10 ** (-precision)
                    rtol = 10 ** (-(precision - 1))
                    if err > atol + rtol * abs(val_expected):
                        mismatches += 1
                except (ValueError, ZeroDivisionError, OverflowError):
                    continue  # 정의역 밖의 점은 무시

            numeric_match = (mismatches == 0)
            numeric_error = max_error
            computed_value = str(expr)  # free symbol 포함이므로 수식 자체 반환

        elif not has_free_symbols:
            # free symbol 없음: 직접 수치 평가
            computed_sympy = N(expr, precision + 4)  # 추가 정밀도 여유

            # 발산·미정의 검사
            if computed_sympy in (oo, -oo, zoo, sympy_nan):
                raise VamosError(
                    error_code="VRE_ENGINE_FAILURE",
                    message=f"수식 평가 결과 비정상: {computed_sympy}",
                    recoverable=True
                )

            # float vs Decimal 선택 (§10.1 정책)
            use_decimal = (
                precision > 6
                and any(kw in request.context.lower()
                        for kw in ["financial", "currency", "accounting",
                                   "재무", "금융"])
            )

            if use_decimal:
                getcontext().prec = precision + 4
                computed_decimal = Decimal(str(computed_sympy))
                computed_value = str(computed_decimal.quantize(
                    Decimal(10) ** -precision
                ))
            else:
                computed_value = str(float(computed_sympy))

            # expected_result와 수치 비교
            if expected is not None:
                expected_num = float(N(expected, precision + 4))
                computed_num = float(computed_sympy)

                # ── 오차 허용 공식 ────────────────────
                #   PASS 조건: |computed - expected| ≤ atol + rtol × |expected|
                #
                #   atol (absolute tolerance) = 10^(-precision)
                #     → precision=6이면 atol=1e-6
                #   rtol (relative tolerance) = 10^(-precision+1)
                #     → precision=6이면 rtol=1e-5
                #
                #   근거: IEEE 754 double은 ~15유효숫자,
                #   precision≤15 제약에서 요청된 정밀도의 1자리 여유를 rtol로 허용
                atol = 10 ** (-precision)
                rtol = 10 ** (-(precision - 1))

                abs_error = abs(computed_num - expected_num)
                threshold = atol + rtol * abs(expected_num)
                numeric_match = (abs_error <= threshold)
                numeric_error = abs_error

                # NumPy 교차 검증: np.isclose로 독립 확인
                numpy_agree = np.isclose(
                    computed_num, expected_num, atol=atol, rtol=rtol
                )
                if numpy_agree != numeric_match:
                    # 수동 계산과 NumPy 판정 불일치 시 보수적 판단
                    numeric_match = False

        else:
            # free symbol 있고 expected 없음: 수식 자체를 문자열로 반환
            computed_value = str(expr)

        method_used = "symbolic" if symbolic_match is True else "numeric"

    except VamosError:
        raise
    except Exception as e:
        raise VamosError(
            error_code="VRE_ENGINE_FAILURE",
            message=f"수치 연산 실패: {str(e)}",
            recoverable=True
        )

    # ── (C) 교차 검증 ────────────────────────────────
    if (symbolic_match is not None and numeric_match is not None
            and symbolic_match != numeric_match):
        method_used = "hybrid"
        # 불일치 기록: symbolic과 numeric 결과가 다름
        # → Phase 4에서 confidence 감산 요인으로 반영

    return EvaluateResult(
        symbolic_match=symbolic_match,
        numeric_match=numeric_match,
        computed_value=computed_value,
        symbolic_proof=symbolic_proof,
        numeric_error=numeric_error,
        method_used=method_used
    )
```

#### 10.4.1 오차 허용 공식 (Tolerance)

| 파라미터 | 공식 | precision=6 예시 | 의미 |
|----------|------|-----------------|------|
| **atol** (absolute tolerance) | `10^(-precision)` | `1e-6` | 절대 오차 허용 한계 |
| **rtol** (relative tolerance) | `10^(-(precision-1))` | `1e-5` | 상대 오차 허용 비율 |
| **판정 기준** | `|computed - expected| ≤ atol + rtol × |expected|` | — | atol과 rtol의 혼합 허용 |

> **설계 근거**: NumPy `np.isclose(a, b, atol, rtol)` 판정 공식과 동일 구조. 절대 오차만 사용하면 큰 수에서 과도하게 엄격하고, 상대 오차만 사용하면 0 근방에서 불안정하므로 혼합 방식 채택.

> **precision별 tolerance 예시**:
>
> | precision | atol | rtol | |expected|=1000일 때 threshold |
> |-----------|------|------|-----------------------------|
> | 3 | 1e-3 | 1e-2 | 10.001 |
> | 6 | 1e-6 | 1e-5 | 0.010001 |
> | 10 | 1e-10 | 1e-9 | 1.0001e-6 |
> | 15 | 1e-15 | 1e-14 | 1.0001e-11 |

**시간복잡도**:
- **free symbol 없음**: **O(S²)** 최악 (SymPy `simplify` 지배적), **O(S·log S)** 평균 — S = AST 노드 수. 수치 연산(`N()`)은 O(S). NumPy `np.isclose` 교차 검증은 O(1). 일반 수식(S≤200) 기준 ~200ms.
- **free symbol 있음**: **O(K·S)** — K = 테스트 포인트 수(20), S = `lambdify` 변환 후 수치 평가 비용. NumPy 벡터 연산 활용으로 ~50ms.
- LOCK-VR-12(≤2s) 내 처리 가능. **주의**: 심볼릭 적분/미분이 포함된 복잡 수식(S>500)은 `simplify()`가 수 초 소요 가능 — §10.6 중간 타임아웃 체크로 방어.

### 10.5 Phase 4 — Aggregate (Confidence 산출 및 판정)

**입력**: `EvaluateResult`, `NormalizeResult.dimension_check`
**출력**: `AggregateResult { confidence: float, judgment: Literal["PASS","REVIEW","FAIL"], is_correct: bool, is_valid: bool }`
**예외**: `VRE_CONFIDENCE_RANGE` — 산출된 confidence가 0.0~1.0 범위 외일 경우

```python
def phase_aggregate(
    eval_result: EvaluateResult,
    dimension_check: DimensionCheckResult
) -> AggregateResult:
    """Phase 4: confidence를 산출하고 LOCK-VR-05 기준으로 판정한다.

    Confidence 산출 규칙:
      4-1. 기본 confidence = 1.0
      4-2. 심볼릭 일치: +0.0 (감산 없음, 최고 신뢰)
           심볼릭 불일치: -0.4
           심볼릭 미수행(None): -0.1 (수치만으로 검증, 약간의 불확실성)
      4-3. 수치 일치: +0.0
           수치 불일치: -0.5
           수치 미수행(None, expected 미제공): -0.05
      4-4. 교차 검증 불일치(method=hybrid): -0.15
      4-5. 차원 불일치: -0.3
      4-6. 오차 크기 비례 감산 (수치 일치 시에도 오차가 클수록 감산)
      4-7. NaN 방어: math.isnan(confidence) → 0.0 (FAIL, 안전 기본값)
      4-8. 범위 클램핑: max(0.0, min(1.0, confidence))

    LOCK-VR-05 판정 기준:
      confidence >= 0.8 → PASS (자동 승인)
      0.5 <= confidence < 0.8 → REVIEW (I-19 ApprovalManager)
      confidence < 0.5 → FAIL (자동 거부 + 근거 첨부)

    Args:
        eval_result: Phase 3 산출물
        dimension_check: Phase 2 차원 검사 결과

    Returns:
        AggregateResult: confidence, judgment, is_correct, is_valid

    Raises:
        VRE_CONFIDENCE_RANGE: confidence가 클램핑 후에도 범위 외 (방어 코드)
    """
    confidence = 1.0

    # 4-2. 심볼릭 검증 반영
    if eval_result.symbolic_match is True:
        pass  # 감산 없음
    elif eval_result.symbolic_match is False:
        confidence -= 0.4
    else:  # None — 심볼릭 검증 미수행
        confidence -= 0.1

    # 4-3. 수치 검증 반영
    if eval_result.numeric_match is True:
        pass  # 감산 없음
    elif eval_result.numeric_match is False:
        confidence -= 0.5
    else:  # None — 수치 검증 미수행 (expected 미제공)
        confidence -= 0.05

    # 4-4. 교차 검증 불일치 감산
    if eval_result.method_used == "hybrid":
        confidence -= 0.15

    # 4-5. 차원 불일치 감산
    if not dimension_check.is_consistent:
        confidence -= 0.3

    # 4-6. 오차 크기 비례 감산
    #   수치 일치(tolerance 내)라도 오차가 tolerance의 50% 이상이면
    #   경미한 감산 적용 — 정확도 그라데이션 반영
    if (eval_result.numeric_match is True
            and eval_result.numeric_error is not None
            and eval_result.numeric_error > 0):
        # 오차 비율: numeric_error / threshold (threshold는 Phase 3에서 사용한 값)
        # 여기서는 보수적으로 numeric_error 자체를 신호로 사용
        error_penalty = min(0.05, eval_result.numeric_error * 0.01)
        confidence -= error_penalty

    # 4-7. NaN 방어 (confidence_thresholds.md §5.2: NaN → FAIL 처리)
    import math
    if math.isnan(confidence):
        confidence = 0.0  # NaN → 0.0 (FAIL 방향, 안전 기본값)

    # 4-8. 범위 검증 (클램핑 전 — 실제 범위 위반 탐지)
    if not (0.0 <= confidence <= 1.0):
        raise VamosError(
            error_code="VRE_CONFIDENCE_RANGE",
            message=f"confidence 범위 위반: {confidence}",
            recoverable=False
        )

    # 방어 코드: 부동소수점 경계 오차 보정용 최종 클램핑
    confidence = max(0.0, min(1.0, confidence))

    # LOCK-VR-05 판정
    if confidence >= 0.8:
        judgment = "PASS"
    elif confidence >= 0.5:
        judgment = "REVIEW"
    else:
        judgment = "FAIL"

    # is_correct: 심볼릭 또는 수치 중 하나라도 일치하면 True
    is_correct = (
        eval_result.symbolic_match is True
        or eval_result.numeric_match is True
    )

    # is_valid: 차원 일관성 + 계산 가능성
    is_valid = dimension_check.is_consistent and (confidence >= 0.5)

    return AggregateResult(
        confidence=confidence,
        judgment=judgment,
        is_correct=is_correct,
        is_valid=is_valid
    )
```

**시간복잡도**: **O(1)** — 단순 산술·조건 분기. LOCK-VR-12 내 처리: < 1ms.

### 10.5.1 타임아웃 시 수치 전용 Fallback

§10.6에서 중간 타임아웃 체크 시 호출되는 간소화 모드. `simplify()` 호출을 생략하고 수치 검증만 수행한다.

```python
def phase_evaluate_numeric_only(
    norm_result: NormalizeResult,
    request: MathVerifyRequest
) -> EvaluateResult:
    """Phase 3 간소화 모드: 심볼릭 검증 생략, 수치 검증만 수행.

    타임아웃 예산 부족 시 호출된다. simplify()를 호출하지 않으므로
    O(S) 시간 내에 완료된다.

    Args:
        norm_result: Phase 2 산출물
        request: 원본 요청

    Returns:
        EvaluateResult: symbolic_match=None, 수치 결과만 포함
    """
    expr = norm_result.normalized_expr
    expected = norm_result.expected_normalized
    precision = request.precision

    numeric_match: Optional[bool] = None
    numeric_error: Optional[float] = None
    computed_value: str = ""

    has_free_symbols = len(expr.free_symbols) > 0

    if not has_free_symbols:
        computed_sympy = N(expr, precision + 4)
        computed_value = str(float(computed_sympy))

        if expected is not None:
            expected_num = float(N(expected, precision + 4))
            computed_num = float(computed_sympy)
            atol = 10 ** (-precision)
            rtol = 10 ** (-(precision - 1))
            abs_error = abs(computed_num - expected_num)
            numeric_match = (abs_error <= atol + rtol * abs(expected_num))
            numeric_error = abs_error
    else:
        computed_value = str(expr)

    return EvaluateResult(
        symbolic_match=None,  # 심볼릭 검증 생략
        numeric_match=numeric_match,
        computed_value=computed_value,
        symbolic_proof=None,
        numeric_error=numeric_error,
        method_used="numeric"
    )
```

### 10.6 전체 파이프라인 통합 (`verify()` 내부)

```python
async def verify(self, request: MathVerifyRequest) -> MathVerifyResult:
    """BaseVerifier.verify() 구현 — Ask→Bridge→Confirm.

    LOCK-VR-11: ABC 패턴 매핑
    LOCK-VR-12: 단일응답 ≤2s (C-2 단독 호출 시 timeout_ms ≤ 1,000ms 권장)
    """
    start_time = now_ms()

    # ── Ask ───────────────────────────────────────────
    validate_request(request)  # Pydantic 모델 유효성 (§3.1 제약조건)

    # ── Bridge (4-Phase) ─────────────────────────────
    step_by_step: list[ComputeStep] = []
    step_num = 0

    # Phase 1: Parse
    parse_result = phase_parse(request)
    step_num += 1
    step_by_step.append(ComputeStep(
        step_number=step_num,
        operation="parse",
        input_expression=request.expression,
        output_expression=str(parse_result.sympy_expr),
        method="symbolic",
        is_verified=True
    ))

    # Phase 2: Normalize
    norm_result = phase_normalize(parse_result, request.context)
    step_num += 1
    step_by_step.append(ComputeStep(
        step_number=step_num,
        operation="normalize",
        input_expression=str(parse_result.sympy_expr),
        output_expression=str(norm_result.normalized_expr),
        method="symbolic",
        is_verified=norm_result.dimension_check.is_consistent
    ))

    # 중간 타임아웃 체크 (Phase 3 진입 전 — simplify가 비용 큼)
    elapsed = now_ms() - start_time
    if elapsed > request.timeout_ms * 0.7:  # 예산 70% 소진 시 조기 경고
        # Phase 3을 간소화 모드로 전환: simplify 생략, 수치만 수행
        eval_result = phase_evaluate_numeric_only(norm_result, request)
    else:
        # Phase 3: Evaluate (전체 이중 검증)
        eval_result = phase_evaluate(norm_result, request)

    step_num += 1
    step_by_step.append(ComputeStep(
        step_number=step_num,
        operation="evaluate",
        input_expression=str(norm_result.normalized_expr),
        output_expression=eval_result.computed_value,
        method=eval_result.method_used,
        is_verified=(
            eval_result.symbolic_match is True
            or eval_result.numeric_match is True
        )
    ))

    # Phase 4: Aggregate
    agg_result = phase_aggregate(eval_result, norm_result.dimension_check)
    step_num += 1
    step_by_step.append(ComputeStep(
        step_number=step_num,
        operation="aggregate",
        input_expression=eval_result.computed_value,
        output_expression=f"confidence={agg_result.confidence:.4f}, judgment={agg_result.judgment}",
        method="symbolic",
        is_verified=True
    ))

    # 최종 타임아웃 체크
    elapsed = now_ms() - start_time
    if elapsed > request.timeout_ms:
        raise VamosError(
            error_code="VRE_TIMEOUT",
            message=f"수학 검증 타임아웃: {elapsed}ms > {request.timeout_ms}ms",
            recoverable=True
        )

    # ── Confirm ──────────────────────────────────────
    result = MathVerifyResult(
        confidence=agg_result.confidence,
        is_valid=agg_result.is_valid,
        is_correct=agg_result.is_correct,
        computed_result=eval_result.computed_value,
        error_type=(
            "dimension_mismatch" if not norm_result.dimension_check.is_consistent
            else "precision_loss" if eval_result.method_used == "hybrid"
            else None
        ),
        step_by_step=step_by_step,
        symbolic_verification=eval_result.symbolic_proof,
        details={
            "phases_completed": ["parse", "normalize", "evaluate", "aggregate"],
            "input_format": parse_result.input_format,
            "parse_warnings": parse_result.parse_warnings,
            "dimension_consistent": norm_result.dimension_check.is_consistent,
            "tolerance": {
                "atol": 10 ** (-request.precision),
                "rtol": 10 ** (-(request.precision - 1))
            }
        },
        timestamp=iso8601_now(),
        engine_id="C-2"
    )

    # should_escalate() — ABC Confirm 단계
    if await self.should_escalate(result):
        # I-20 경유 에스컬레이션 (R-01-8: 직접 호출 금지)
        try:
            escalation_result = await escalate_via_i20(
                engine_id="C-2",
                original_result=result,
                request=request
            )
            # D-1 Think Engine 재검증 성공 시 결과 갱신
            if escalation_result is not None:
                result = escalation_result
        except EscalationError as e:
            raise VamosError(
                error_code="VRE_ESCALATION_FAILED",
                message=f"I-20 경유 에스컬레이션 실패: {str(e)}",
                recoverable=True
            )
        result.details["escalated"] = True
        result.details["escalation_reason"] = (
            f"confidence {result.confidence:.4f} < threshold "
            f"{self.get_confidence_threshold()}"
        )

    return result
```

### 10.7 LOCK-VR-12 SLA 준수 분석

> LOCK (D2.0-02 §2.3-B): 단일응답 ≤2s, 복합응답 ≤10s, Self-check ≤1s

C-2 Math Verifier의 `verify()` 호출은 파이프라인 예산 내에서 소화되어야 한다 (base_verifier_abc.md §7.2: 단순 검증 ≤1,000ms).

| Phase | 최악 | 평균 | 일반 입력 실측 예상 | LOCK-VR-12 준수 |
|-------|------|------|-------------------|----------------|
| Phase 1 (Parse) | O(T) | O(T) | ~10ms | ✓ |
| Phase 2 (Normalize) | O(S²) | O(S·V) | ~50ms | ✓ |
| Phase 3 (Evaluate) | O(S²) / O(K·S) | O(S·log S) | ~200ms (no free sym) / ~50ms (free sym) | ✓ |
| Phase 4 (Aggregate) | O(1) | O(1) | < 1ms | ✓ |
| **합계** | — | — | **~261ms** | ✓ (예산 1,000ms 대비 26%) |

> **Worst-case 주의사항**: Phase 3의 `simplify()`는 복잡한 심볼릭 수식(삼각함수 합성, 다변수 적분 등)에서 수 초 소요 가능. 이를 방지하기 위해 §10.6에서 `timeout_ms * 0.7` 중간 체크를 수행하고, 초과 시 수치 전용 모드(`phase_evaluate_numeric_only`)로 전환한다.

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| v1.1 | 2026-04-06 | P1-2 실행 — Algorithm 섹션(§10) L3 완성: 4-Phase 의사코드, 오차 허용 공식, 차원 검증 로직, SymPy/NumPy 이중 검증, float/Decimal 선택 기준 | P1-2 |
| v1.0 | 2026-03-29 | 초기 작성 — P0-9 실행, I/O Schema L3 정의 | P0-9 |
