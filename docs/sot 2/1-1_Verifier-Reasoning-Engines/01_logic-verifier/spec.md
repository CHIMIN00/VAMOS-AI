# C-1 Logic Verifier — Specification

> **Status**: APPROVED
> **버전**: v1.1
> **Last-reviewed**: 2026-04-06
> **Owner**: 1-1_Verifier-Reasoning-Engines

---

## 1. 개요

본 문서는 C-1 Logic Verifier의 I/O Schema 및 4-Phase 알고리즘을 L3 수준으로 정의한다. 주장(claim)과 근거(context) 간 논리적 일관성을 검증하고, 모순·오류를 탐지하여 confidence 기반 판정을 반환한다.

> LOCK (D2.0-01 §5.11): C-1 Logic Verifier: CORE, V1:ON, change_lock=false

---

## 2. ABC 계약 매핑 (LOCK-VR-11)

> LOCK (상세명세 C-1 §3): ABC 패턴: Ask→Bridge→Confirm, 엔진 간 표준 인터페이스. 메서드 시그니처 변경 불가.

C-1은 `BaseVerifier` ABC(P0-4 `base_verifier_abc.md`)를 구현한다.

| ABC 메서드 | I/O 매핑 | 단계 |
|-----------|---------|------|
| `verify(request: VerifyRequest) → VerifyResult` | `LogicVerifyRequest → LogicVerifyResult` | Ask→Bridge→Confirm 전체 |
| `get_confidence_threshold() → float` | 반환값: `0.8` (LOCK-VR-05) | Confirm 판정 기준 |
| `should_escalate(result: VerifyResult) → bool` | `result.confidence < 0.8` → True | Confirm 에스컬레이션 판단 |

### Ask→Bridge→Confirm 흐름

```
[호출자] ──verify(LogicVerifyRequest)──→ [C-1 LogicVerifier]
                                              │
                                        ┌─────┴─────┐
                                        │    Ask    │  LogicVerifyRequest 검증·전처리
                                        └─────┬─────┘
                                              │
                                        ┌─────┴─────┐
                                        │  Bridge   │  4-Phase 논리 검증 알고리즘
                                        │           │  confidence 값 산출
                                        └─────┬─────┘
                                              │
                                        ┌─────┴─────┐
                                        │  Confirm  │  LogicVerifyResult 구성
                                        │           │  should_escalate() 판단
                                        └─────┬─────┘
                                              │
                              ┌───────────────┴───────────────┐
                              │                               │
                    confidence ≥ 0.8                  confidence < 0.8
                              │                               │
                     LogicVerifyResult 반환          I-20 경유 → D-1 재검증
```

---

## 3. Input Schema

### 3.1 LogicVerifyRequest

`VerifyRequest`(common_types.md §2.1)를 C-1 전용 필드로 확장한다.

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal

class LogicVerifyRequest(BaseModel):
    """C-1 Logic Verifier 검증 요청.

    Base: VerifyRequest (common_types.md §2.1)
    """

    # --- Base 필드 (VerifyRequest 상속) ---
    claim: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="검증 대상 주장"
    )
    context: list[str] = Field(
        ...,
        min_length=1,
        description="근거 문장 목록 (최소 1개)"
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

    # --- C-1 전용 필드 ---
    reasoning_chain: Optional[list["ReasoningStep"]] = Field(
        default=None,
        description="검증할 추론 체인 (선택). 제공 시 체인의 논리적 타당성도 검증"
    )
    verification_depth: Literal["shallow", "standard", "deep"] = Field(
        default="standard",
        description="검증 깊이. shallow: Phase 1-2만, standard: Phase 1-3, deep: Phase 1-4 전체"
    )
```

| 필드 | 타입 | 필수 | 제약조건 | 기본값 | 근거 |
|------|------|------|---------|--------|------|
| `claim` | `str` | Yes | `1 ≤ len ≤ 10000` | — | 상세명세 C-1 §1 |
| `context` | `list[str]` | Yes | `min_length=1` | — | 상세명세 C-1 §1 |
| `timeout_ms` | `int` | Yes | `> 0` | — | R-01-3 |
| `request_id` | `str` | Yes | `min_length=1` | — | common_types.md §2.1 |
| `reasoning_chain` | `Optional[list[ReasoningStep]]` | No | — | `None` | 상세명세 C-1 §1 |
| `verification_depth` | `Literal["shallow","standard","deep"]` | No | enum | `"standard"` | 상세명세 C-1 §1 |

---

## 4. Output Schema

### 4.1 LogicVerifyResult

`VerifyResult`(common_types.md §2.2)를 C-1 전용 필드로 확장한다.

> LOCK (상세명세 C-1 §4): Confidence 판정 >=0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL

> 참조: `confidence_thresholds.md`(P0-7) — 판정 정책 정본

```python
class LogicVerifyResult(BaseModel):
    """C-1 Logic Verifier 검증 결과.

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
        description="논리적 일관성 통과 여부"
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
        default="C-1",
        pattern=r"^C-1$",
        description="C-1 Logic Verifier"
    )

    # --- C-1 전용 필드 ---
    contradictions: list["Contradiction"] = Field(
        default_factory=list,
        description="발견된 모순 목록"
    )
    fallacy_types: list[str] = Field(
        default_factory=list,
        description="감지된 논리적 오류 유형 (Ad hominem, Straw man 등 24종)"
    )
    evidence_mapping: dict[str, str] = Field(
        default_factory=dict,
        description="주장→근거 매핑 (key: 주장 요소, value: 대응 근거)"
    )
```

| 필드 | 타입 | 필수 | 제약조건 | 기본값 | 근거 |
|------|------|------|---------|--------|------|
| `confidence` | `float` | Yes | `0.0 ≤ v ≤ 1.0` | — | R-01-4, LOCK-VR-05 |
| `is_valid` | `bool` | Yes | — | — | 상세명세 C-1 §1 |
| `details` | `dict` | No | — | `{}` | common_types.md §2.2 |
| `timestamp` | `str` | Yes | ISO 8601 | — | common_types.md §2.2 |
| `engine_id` | `str` | Yes | `^C-1$` | `"C-1"` | common_types.md §2.2 |
| `contradictions` | `list[Contradiction]` | No | — | `[]` | 상세명세 C-1 §1 |
| `fallacy_types` | `list[str]` | No | — | `[]` | 상세명세 C-1 §1 |
| `evidence_mapping` | `dict[str, str]` | No | — | `{}` | 상세명세 C-1 §1 |

### 4.2 Confidence 판정 기준 (LOCK-VR-05)

> 참조: `confidence_thresholds.md`(P0-7) §2 — 정본

| 범위 | 판정 | 후속 처리 |
|------|------|----------|
| `confidence >= 0.8` | **PASS** | 자동 승인 |
| `0.5 <= confidence < 0.8` | **REVIEW** | I-19 ApprovalManager로 전달 |
| `confidence < 0.5` | **FAIL** | 자동 거부 + 근거 첨부 |

---

## 5. 엔진 전용 타입 정의 (그룹 F)

> P0-6 `common_types.md` §8에서 본 spec.md로 정식 정의 위임.

### 5.1 Contradiction

```python
class Contradiction(BaseModel):
    """논리적 모순 정보.

    C-1 LogicVerifyResult.contradictions에서 사용.
    common_types.md §8 그룹 F: 본 spec.md에서 정식 정의.
    """

    premise_a: str = Field(
        ...,
        description="모순의 첫 번째 전제/주장"
    )
    premise_b: str = Field(
        ...,
        description="모순의 두 번째 전제/주장 (premise_a와 충돌)"
    )
    contradiction_type: Literal["negation", "scope_conflict", "temporal_conflict"] = Field(
        ...,
        description="모순 유형: negation(부정), scope_conflict(범위 충돌), temporal_conflict(시간 모순)"
    )
    severity: Literal["critical", "major", "minor"] = Field(
        ...,
        description="심각도: critical(결론 무효화), major(신뢰도 저하), minor(경미)"
    )
    explanation: str = Field(
        ...,
        description="모순에 대한 설명"
    )
```

| 필드 | 타입 | 필수 | 제약조건 |
|------|------|------|---------|
| `premise_a` | `str` | Yes | — |
| `premise_b` | `str` | Yes | — |
| `contradiction_type` | `Literal[...]` | Yes | enum 3종 |
| `severity` | `Literal[...]` | Yes | enum 3종 |
| `explanation` | `str` | Yes | — |

---

## 6. Error Schema

> **R-01-7**: error_code + message + recoverable 필수.

`VamosError`(common_types.md §3.4)를 C-1 전용 에러 코드로 확장한다.

| error_code | 설명 | recoverable |
|-----------|------|-------------|
| `VRE_TIMEOUT` | 타임아웃 초과 | True |
| `VRE_INVALID_INPUT` | claim 또는 context 누락/형식 오류 | False |
| `VRE_ENGINE_FAILURE` | 논리 검증 엔진 내부 오류 | True |
| `VRE_CONFIDENCE_RANGE` | confidence 범위 위반 (0.0~1.0 외) | False |
| `VRE_ESCALATION_FAILED` | I-20 경유 D-1 에스컬레이션 실패 | True |

```json
{
  "error_code": "VRE_TIMEOUT",
  "message": "Logic verification exceeded timeout of 1000ms",
  "recoverable": true
}
```

---

## 7. Fallback Chain (R-01-2, R-01-8)

> **R-01-2**: 모든 엔진은 fallback chain 최소 2단계 필수.
> **R-01-8**: 에스컬레이션은 반드시 I-20 Failure/Fallback Manager 경유. 직접 호출 금지.
> 참조: `failover_policy.md`(P0-8) §5.1 — C-1 Failover 시나리오 정본

### Layer 2 — 엔진 에스컬레이션

| 단계 | 대상 | 조건 |
|------|------|------|
| Primary | C-1 Logic Verifier | `verify()` 실행 |
| Secondary | D-1 Think Engine | `should_escalate()=True` (confidence < 0.8) → **I-20 경유** |
| Tertiary | HITL (사용자 판단) | D-1 재검증도 실패 시 → **I-20 경유** |

```
C-1 verify() → confidence < 0.8
    │
    ▼
I-20 Failure/Fallback Manager (경유 필수, R-01-8)
    │
    ▼
D-1 Think Engine 재검증
    │
    ├── 성공 → 결과 반환
    └── 실패 → I-20 경유 → HITL
```

### Layer 1 — LLM 브레인 Failover (LOCK-VR-07)

> 참조: `failover_policy.md`(P0-8) §5.1

| 단계 | Brain | 비고 |
|------|-------|------|
| Primary | GPT-4o | 논리 검증 수행 |
| Secondary | Claude Sonnet | 연속 3회 타임아웃/5xx 시 전환 |
| Tertiary | 로컬 Ollama | Claude도 실패 시 전환 |

---

## 8. 타임아웃 정책

> LOCK (D2.0-02 §2.3-B): 단일응답 ≤2s, 복합응답 ≤10s, Self-check ≤1s

| 시나리오 | `timeout_ms` 기본값 | 근거 |
|----------|-------------------|------|
| 단순 논리 검증 (shallow/standard) | ≤ 1,000ms | 파이프라인 2초 예산의 50% (P0-4 §7.2) |
| 심층 논리 검증 (deep) | ≤ 5,000ms | 파이프라인 10초 예산의 50% (P0-4 §7.2) |

---

## 9. LOCK 값 참조 요약

> LOCK (상세명세 C-1 §3): ABC 패턴: Ask→Bridge→Confirm, 엔진 간 표준 인터페이스. 메서드 시그니처 변경 불가.

> LOCK (상세명세 C-1 §4): Confidence 판정 >=0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL

> LOCK (D2.0-02 §2.3-B): 단일응답 ≤2s, 복합응답 ≤10s, Self-check ≤1s

> LOCK (D2.0-01 §5.11): C-1: CORE, V1:ON, change_lock=false

---

## 10. 예시 JSON

### 10.1 Request 예시

```json
{
  "claim": "모든 포유류는 알을 낳지 않는다",
  "context": [
    "포유류는 새끼를 낳아 젖을 먹여 키우는 동물이다",
    "오리너구리는 포유류이면서 알을 낳는다"
  ],
  "reasoning_chain": null,
  "verification_depth": "standard",
  "timeout_ms": 1000,
  "request_id": "req-c1-20260329-001"
}
```

### 10.2 Response 예시

```json
{
  "confidence": 0.55,
  "is_valid": false,
  "details": {
    "phases_completed": ["parse", "normalize", "evaluate", "aggregate"]
  },
  "timestamp": "2026-03-29T14:30:00Z",
  "engine_id": "C-1",
  "contradictions": [
    {
      "premise_a": "모든 포유류는 알을 낳지 않는다",
      "premise_b": "오리너구리는 포유류이면서 알을 낳는다",
      "contradiction_type": "negation",
      "severity": "critical",
      "explanation": "전칭 부정('모든 포유류는 알을 낳지 않는다')이 반례('오리너구리')에 의해 반증됨"
    }
  ],
  "fallacy_types": ["hasty_generalization"],
  "evidence_mapping": {
    "모든 포유류는 알을 낳지 않는다": "오리너구리는 포유류이면서 알을 낳는다"
  }
}
```

---

## 11. Algorithm — 4-Phase 논리 검증 (L3)

> **Status**: APPROVED
> **이슈**: C1-3 (Phase 1 해결) — Algorithm Pseudocode L2→L3
> **게이트 기여**: G1-1 (spec.md Algorithm 섹션 Status=APPROVED)

### 11.0 개요 및 ABC 패턴 매핑 (LOCK-VR-11)

4-Phase 알고리즘은 ABC 패턴(Ask→Bridge→Confirm)의 **Bridge** 단계에 해당한다.

| ABC 단계 | 4-Phase 매핑 | 역할 |
|----------|-------------|------|
| **Ask** | `verify()` 진입 — 입력 검증·전처리 | `LogicVerifyRequest` 유효성 검사 |
| **Bridge** | **Phase 1(Parse) → Phase 2(Normalize) → Phase 3(Evaluate) → Phase 4(Aggregate)** | 논리 검증 알고리즘 실행, confidence 산출 |
| **Confirm** | `verify()` 후속 — 결과 구성·에스컬레이션 판단 | `LogicVerifyResult` 반환, `should_escalate()` → `get_confidence_threshold()` 비교 |

**`verification_depth`에 따른 Phase 수행 범위** (§3.1 정의):

| verification_depth | 수행 Phase | 비고 |
|-------------------|-----------|------|
| `shallow` | Phase 1(Parse) + Phase 2(Normalize) + Phase 4(Aggregate) | Phase 3(Evaluate) 생략, 보수적 confidence 상한 적용 |
| `standard` | Phase 1 + Phase 2 + Phase 3(Evaluate) + Phase 4 | 기본값 |
| `deep` | Phase 1 + Phase 2 + Phase 3 + Phase 4 | Phase 4에서 fallacy 감점 가중 |

> **Phase 4(Aggregate)는 모든 depth에서 항상 수행된다.** Phase 4는 confidence 산출·판정 단계이므로 검증 깊이와 무관하게 최종 결과 생성에 필수적이다.

```
verify(request: LogicVerifyRequest) → LogicVerifyResult
│
├── [Ask]  입력 검증·전처리
│
├── [Bridge]  4-Phase 알고리즘
│   ├── Phase 1: Parse      — 논리 명제 추출
│   ├── Phase 2: Normalize  — 표준형 변환·중복 제거
│   ├── Phase 3: Evaluate   — 일관성 평가·모순 탐지
│   └── Phase 4: Aggregate  — confidence 산출·판정
│
└── [Confirm]  LogicVerifyResult 구성 → should_escalate() → 반환
```

### 11.1 Phase 1 — Parse (논리 명제 추출)

**입력**: `LogicVerifyRequest` (claim, context, reasoning_chain?)
**출력**: `ParseResult { propositions: list[Proposition], parse_errors: list[str] }`
**예외**: `VRE_INVALID_INPUT` — claim 또는 context가 빈 문자열이거나 파싱 불가 시

```python
def phase_parse(request: LogicVerifyRequest) -> ParseResult:
    """Phase 1: 입력 텍스트에서 논리 명제를 추출한다.

    Args:
        request: 검증 요청 (claim + context + optional reasoning_chain)

    Returns:
        ParseResult: 추출된 명제 목록 + 파싱 에러 목록

    Raises:
        VamosError(VRE_INVALID_INPUT): claim/context 파싱 불가 시
    """
    propositions: list[Proposition] = []
    parse_errors: list[str] = []

    # 1-1. claim에서 주 명제 추출 (source="claim" 태깅)
    claim_props = extract_propositions(request.claim, source="claim")
    if not claim_props:
        raise VamosError(
            error_code="VRE_INVALID_INPUT",
            message=f"Failed to parse claim: '{request.claim[:100]}'",
            recoverable=False
        )
    propositions.extend(claim_props)

    # 1-2. context 각 문장에서 근거 명제 추출 (source="context" 태깅)
    for idx, ctx_sentence in enumerate(request.context):
        ctx_props = extract_propositions(ctx_sentence, source="context")
        if not ctx_props:
            parse_errors.append(f"context[{idx}] parse failed: '{ctx_sentence[:100]}'")
            continue
        propositions.extend(ctx_props)

    # 1-3. reasoning_chain이 있으면 각 step에서 명제 추출 (source="reasoning_chain" 태깅)
    if request.reasoning_chain is not None:
        for step in request.reasoning_chain:
            step_props = extract_propositions(step.content, source="reasoning_chain")
            if step_props:
                propositions.extend(step_props)

    # 1-4. 최소 2개 명제 필요 (claim 1개 + context 1개 이상)
    if len(propositions) < 2:
        raise VamosError(
            error_code="VRE_INVALID_INPUT",
            message="Insufficient propositions extracted (min 2 required)",
            recoverable=False
        )

    return ParseResult(propositions=propositions, parse_errors=parse_errors)
```

**시간복잡도**: **O(N·L)** — N = context 문장 수, L = 문장 평균 길이(토큰 수). `extract_propositions`은 문장당 O(L) 선형 파싱. LOCK-VR-12(≤2s) 내 처리 가능: 일반적 입력(N≤100, L≤500) 기준 수십 ms 이내.

### 11.2 Phase 2 — Normalize (표준형 변환)

**입력**: `ParseResult`
**출력**: `NormalizeResult { normalized: list[NormalizedProp], dedup_count: int }`
**예외**: 없음 (Phase 1에서 유효성 보장)

```python
def phase_normalize(parse_result: ParseResult) -> NormalizeResult:
    """Phase 2: 명제를 표준형으로 변환하고 중복을 제거한다.

    Args:
        parse_result: Phase 1 산출물 (추출된 명제 목록)

    Returns:
        NormalizeResult: 정규화된 명제 목록 + 제거된 중복 수
    """
    normalized: list[NormalizedProp] = []
    seen_hashes: set[str] = set()
    dedup_count: int = 0

    for prop in parse_result.propositions:
        # 2-1. 논리식 표준형 변환 (CNF — Conjunctive Normal Form)
        #      CNF를 기본 표준형으로 채택 (DNF 대비 SAT solver 호환성 우수)
        #      부정 정규화(NNF) → 분배 법칙 적용 → CNF
        cnf_form = to_negation_normal_form(prop.expression)
        cnf_form = distribute_or_over_and(cnf_form)

        # 2-2. 변수명 정규화 (동의어·대용어 통합)
        cnf_form = canonicalize_variables(cnf_form)

        # 2-3. 중복 제거 (구조적 해싱)
        prop_hash = structural_hash(cnf_form)
        if prop_hash in seen_hashes:
            dedup_count += 1
            continue
        seen_hashes.add(prop_hash)

        normalized.append(NormalizedProp(
            original=prop,
            cnf=cnf_form,
            source=prop.source  # "claim" | "context" | "reasoning_chain"
        ))

    return NormalizeResult(normalized=normalized, dedup_count=dedup_count)
```

**시간복잡도**: **O(P·2^V)** 최악, **O(P·V^2)** 평균 — P = 명제 수, V = 명제 내 변수 수. CNF 변환은 최악 지수적이나 실무적 논리식(V≤20)에서는 다항 시간. LOCK-VR-12(≤2s) 내 처리 가능: 일반적 입력(P≤50, V≤10) 기준 수십 ms.

### 11.3 Phase 3 — Evaluate (논리적 일관성 평가)

**입력**: `NormalizeResult`
**출력**: `EvaluateResult { contradictions: list[Contradiction], fallacy_types: list[str], evidence_mapping: dict[str,str], consistency_score: float }`
**예외**: `VRE_ENGINE_FAILURE` — SAT solver 내부 오류 시 (recoverable=True)

```python
def phase_evaluate(norm_result: NormalizeResult) -> EvaluateResult:
    """Phase 3: 논리적 일관성을 평가하고 모순·오류를 탐지한다.

    Args:
        norm_result: Phase 2 산출물 (정규화된 명제 목록)

    Returns:
        EvaluateResult: 모순 목록, 오류 유형, 근거 매핑, 일관성 점수

    Raises:
        VamosError(VRE_ENGINE_FAILURE): SAT solver 내부 오류 시
    """
    contradictions: list[Contradiction] = []
    fallacy_types: list[str] = []
    evidence_mapping: dict[str, str] = {}

    claim_props = [p for p in norm_result.normalized if p.source == "claim"]
    context_props = [p for p in norm_result.normalized if p.source != "claim"]

    # 3-1. SAT solver를 통한 모순 탐지
    #      claim ∧ context 전체를 결합하여 satisfiability 검사
    combined_cnf = conjoin([p.cnf for p in norm_result.normalized])
    try:
        sat_result = sat_solve(combined_cnf)
    except SolverError as e:
        raise VamosError(
            error_code="VRE_ENGINE_FAILURE",
            message=f"SAT solver failed: {e}",
            recoverable=True
        )

    if not sat_result.is_satisfiable:
        # 3-2. UNSAT — 최소 모순 부분집합(MUS) 추출
        mus_sets = extract_minimal_unsatisfiable_subsets(combined_cnf)
        for mus in mus_sets:
            pair = identify_contradiction_pair(mus, norm_result.normalized)
            contradictions.append(Contradiction(
                premise_a=pair.prop_a.original.text,
                premise_b=pair.prop_b.original.text,
                contradiction_type=classify_contradiction(pair),  # negation|scope_conflict|temporal_conflict
                severity=assess_severity(pair, claim_props),      # critical|major|minor
                explanation=generate_explanation(pair)
            ))

    # 3-3. 추론 규칙 기반 오류 탐지 (24종 fallacy 체크)
    for claim_p in claim_props:
        for ctx_p in context_props:
            detected = detect_fallacies(claim_p, ctx_p)
            fallacy_types.extend(detected)

    fallacy_types = list(set(fallacy_types))  # 중복 제거

    # 3-4. 주장→근거 매핑 구축
    for claim_p in claim_props:
        best_match = find_best_supporting_evidence(claim_p, context_props)
        if best_match is not None:
            evidence_mapping[claim_p.original.text] = best_match.original.text

    # 3-5. 일관성 점수 산출 (0.0~1.0)
    #      기본 점수 1.0에서 모순·오류에 따라 감점
    consistency_score = 1.0
    for c in contradictions:
        penalty = {"critical": 0.4, "major": 0.2, "minor": 0.05}[c.severity]
        consistency_score -= penalty
    consistency_score -= len(fallacy_types) * 0.05
    consistency_score = max(0.0, consistency_score)

    return EvaluateResult(
        contradictions=contradictions,
        fallacy_types=fallacy_types,
        evidence_mapping=evidence_mapping,
        consistency_score=consistency_score
    )
```

**시간복잡도**: **O(2^V)** 최악 (SAT solver NP-complete), **O(P^2·V)** 평균 — SAT 문제는 이론적 최악 지수적이나, 실무적 CNF(변수 ≤20, 절 ≤100)에서 DPLL/CDCL solver는 다항 시간 수렴. 오류 탐지 O(P_claim·P_context). LOCK-VR-12(≤2s) 내 처리 가능: 일반적 입력 기준 수백 ms.

### 11.4 Phase 4 — Aggregate (Confidence 산출 및 판정)

**입력**: `EvaluateResult`, `LogicVerifyRequest.verification_depth`
**출력**: `AggregateResult { confidence: float, judgment: Literal["PASS","REVIEW","FAIL"], is_valid: bool }`
**예외**: `VRE_CONFIDENCE_RANGE` — 산출된 confidence가 0.0~1.0 범위 외일 경우

> LOCK (상세명세 C-1 §4): Confidence 판정 >=0.8 PASS, 0.5~0.8 REVIEW, <0.5 FAIL
> 참조: `confidence_thresholds.md`(P0-7) §2 — 판정 정책 정본

```python
def phase_aggregate(
    eval_result: EvaluateResult,
    verification_depth: Literal["shallow", "standard", "deep"]
) -> AggregateResult:
    """Phase 4: confidence를 산출하고 LOCK-VR-05 기준으로 판정한다.

    LOCK-VR-05 판정 기준:
      - confidence >= 0.8 → PASS (자동 승인)
      - 0.5 <= confidence < 0.8 → REVIEW (I-19 ApprovalManager 전달)
      - confidence < 0.5 → FAIL (자동 거부 + 근거 첨부)

    Args:
        eval_result: Phase 3 산출물
        verification_depth: 검증 깊이 (shallow|standard|deep)

    Returns:
        AggregateResult: confidence, judgment, is_valid

    Raises:
        VamosError(VRE_CONFIDENCE_RANGE): confidence 범위 위반 시
    """
    # 4-1. 기본 confidence = consistency_score
    confidence = eval_result.consistency_score

    # 4-2. 검증 깊이에 따른 보정
    #      shallow: Phase 1-2만 수행 → Phase 3 결과 미반영, 보수적 감점
    #      standard: Phase 1-3 → 기본값
    #      deep: Phase 1-4 전체 → fallacy 가중치 상향
    if verification_depth == "shallow":
        # Phase 3 미수행 시 보수적 하한 적용
        confidence = min(confidence, 0.7)
    elif verification_depth == "deep":
        # 심층 검증: fallacy 감점 가중
        fallacy_penalty = len(eval_result.fallacy_types) * 0.08
        confidence -= fallacy_penalty
        confidence = max(0.0, confidence)

    # 4-3. NaN 처리 (confidence_thresholds.md §5.2)
    if isnan(confidence):
        log_warning(f"Confidence is NaN — defaulting to FAIL")
        confidence = 0.0  # 안전 방향(FAIL) 기본 적용

    # 4-4. 범위 검증 (0.0 ~ 1.0)
    if not (0.0 <= confidence <= 1.0):
        raise VamosError(
            error_code="VRE_CONFIDENCE_RANGE",
            message=f"Confidence {confidence} out of range [0.0, 1.0]",
            recoverable=False
        )

    # 4-5. LOCK-VR-05 판정 (confidence_thresholds.md §2.1)
    if confidence >= 0.8:
        judgment = "PASS"
    elif confidence >= 0.5:
        judgment = "REVIEW"
    else:
        judgment = "FAIL"

    # 4-6. is_valid 판정: PASS이고 critical 모순 없음
    is_valid = (judgment == "PASS") and not any(
        c.severity == "critical" for c in eval_result.contradictions
    )

    return AggregateResult(
        confidence=confidence,
        judgment=judgment,
        is_valid=is_valid
    )
```

**시간복잡도**: **O(C + F)** — C = 모순 수, F = fallacy 유형 수. 단순 산술 연산으로 상수 시간에 근접. LOCK-VR-12(≤2s) 내 처리: < 1ms.

### 11.5 전체 파이프라인 통합 (`verify()` 내부)

```python
async def verify(self, request: LogicVerifyRequest) -> LogicVerifyResult:
    """BaseVerifier.verify() 구현 — Ask→Bridge→Confirm.

    LOCK-VR-11: ABC 패턴 매핑
    LOCK-VR-12: 단일응답 ≤2s
    """
    start_time = now_ms()

    # ── Ask ──────────────────────────────────────────
    validate_request(request)  # 필수 필드 검증, 타입 체크

    # ── Bridge (4-Phase) ─────────────────────────────
    # Phase 1: Parse
    parse_result = phase_parse(request)

    # Phase 2: Normalize
    norm_result = phase_normalize(parse_result)

    # Phase 3: Evaluate (shallow이면 skip → 기본 EvaluateResult 사용)
    if request.verification_depth == "shallow":
        eval_result = EvaluateResult(
            contradictions=[], fallacy_types=[],
            evidence_mapping={}, consistency_score=1.0
        )
    else:
        eval_result = phase_evaluate(norm_result)

    # Phase 4: Aggregate
    agg_result = phase_aggregate(eval_result, request.verification_depth)

    # 타임아웃 체크 (후위 검사)
    # NOTE: 프로덕션 구현 시 Phase 간 중간 타임아웃 체크 권장 (특히 Phase 3 진입 전)
    elapsed = now_ms() - start_time
    if elapsed > request.timeout_ms:
        raise VamosError(
            error_code="VRE_TIMEOUT",
            message=f"Logic verification exceeded timeout of {request.timeout_ms}ms (elapsed: {elapsed}ms)",
            recoverable=True
        )

    # ── Confirm ──────────────────────────────────────
    result = LogicVerifyResult(
        confidence=agg_result.confidence,
        is_valid=agg_result.is_valid,
        details={
            # shallow: Phase 3 생략, standard/deep: 전체 수행
            "judgment": agg_result.judgment,  # PASS/REVIEW/FAIL (LOCK-VR-05; verdict 대체)
            "phases_completed": (
                ["parse", "normalize", "aggregate"]
                if request.verification_depth == "shallow"
                else ["parse", "normalize", "evaluate", "aggregate"]
            ),
            "parse_errors": parse_result.parse_errors,
            "dedup_count": norm_result.dedup_count,
            "consistency_score": eval_result.consistency_score
        },
        timestamp=iso8601_now(),
        engine_id="C-1",
        contradictions=eval_result.contradictions,
        fallacy_types=eval_result.fallacy_types,
        evidence_mapping=eval_result.evidence_mapping
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

### 11.6 시간복잡도 요약

| Phase | 최악 | 평균 | 일반 입력 실측 예상 | LOCK-VR-12 준수 |
|-------|------|------|-------------------|----------------|
| Phase 1 (Parse) | O(N·L) | O(N·L) | ~10ms | ✓ |
| Phase 2 (Normalize) | O(P·2^V) | O(P·V²) | ~20ms | ✓ |
| Phase 3 (Evaluate) | O(2^V) | O(P²·V) | ~200ms | ✓ |
| Phase 4 (Aggregate) | O(C+F) | O(C+F) | <1ms | ✓ |
| **합계** | — | — | **~230ms** | ✓ (≤2s 예산의 ~12%) |

> **N**: context 문장 수, **L**: 평균 토큰 수, **P**: 명제 수, **V**: 변수 수, **C**: 모순 수, **F**: fallacy 수
> 일반 입력 기준: N≤100, L≤500, P≤50, V≤10. LOCK-VR-12(단일응답 ≤2s) 충분 준수.

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| v1.0 | 2026-03-29 | 초기 작성 — P0-9 실행, I/O Schema L3 정의 | P0-9 |
| v1.1 | 2026-04-06 | P1-1 실행 — Algorithm §11 추가, 4-Phase 의사코드 L3 완성 (C1-3 해결) | P1-1 |
