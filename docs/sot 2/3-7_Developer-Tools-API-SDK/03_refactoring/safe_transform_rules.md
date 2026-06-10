# 안전한 변환 규칙

> **L-ID**: L-003
> **V 배정**: V1 (LLM 기반) / V2 (AST 기반)
> **Phase**: Phase 1 P1-3 (V1 범위 — 시맨틱 보존 + 테스트 회귀 방지 + 롤백)
> **수준**: L2+ (D1~D8 전수, §13 P0 항목)
> **의존 LOCK**: LOCK-DT-06 (코드 실행 타임아웃 30초), LOCK-DT-10 (테스트 커버리지 >= 80%)

---

## 교차 참조 블록

| 정본 문서 | 참조 내용 |
|----------|----------|
| STEP7-L L-003 | 안전한 리팩토링: 스냅샷, 영향 범위 분석, 테스트 자동 실행, Diff 리뷰 |
| 종합계획서 §13 | L3 기준 D1~D8, P0 항목 전수 |
| 종합계획서 §3.4 | LOCK-DT-06 (30초), LOCK-DT-10 (커버리지 >= 80%) |
| 종합계획서 §11.3 FR-8 | 리팩토링 패턴 안전성 검증 — 전제조건/후조건, 타입 호환성, 롤백 |
| L-003 pattern_catalog.md | 패턴별 변환 요청 (TransformRequest) |
| L-003 ast_pipeline.md | AST 분석 결과 (ASTContext) |
| L-001 dev_node_architecture.md | 코딩 엔진 파이프라인 |

---

## 안전한 변환 3원칙

| 원칙 | 설명 | 근거 |
|------|------|------|
| **시맨틱 보존** | 리팩토링 전후 프로그램 동작이 동일해야 함 | L-003 안전한 리팩토링 |
| **테스트 회귀 방지** | 기존 테스트가 모두 통과해야 함 (커버리지 >= 80%) | LOCK-DT-10 |
| **롤백 가능** | 모든 변경은 즉시 롤백 가능해야 함 | L-003 변경 전 스냅샷 |

---

## D1. Input Schema

```python
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

class ValidationLevel(Enum):
    STRICT = "strict"       # 모든 검증 통과 필수
    NORMAL = "normal"       # 주요 검증만 (기본)
    LENIENT = "lenient"     # 경고만 발생 (강제 적용 가능)

@dataclass
class RefactoringChange:
    """개별 변경 항목 (pattern_catalog.md에서 전달)"""
    file_path: str
    line_start: int
    line_end: int
    original_code: str
    refactored_code: str
    description: str
    confidence: float                           # 0.0 ~ 1.0

@dataclass
class TransformValidationRequest:
    """안전한 변환 검증 요청"""
    changes: list[RefactoringChange]            # 적용할 변경 목록
    snapshot_id: str                            # 롤백용 스냅샷 ID
    source_hash: str                            # 원본 파일 해시 (무결성 검증)
    test_suite_path: Optional[str] = None       # 테스트 스위트 경로
    validation_level: ValidationLevel = ValidationLevel.NORMAL
    coverage_threshold: float = 0.80            # LOCK-DT-10: >= 0.80 (fraction, 80%)
    timeout_ms: int = 30000                     # LOCK-DT-06: 30초
    trace_id: Optional[str] = None
    project_root: Optional[str] = None          # 프로젝트 루트 (의존성 추적용)
```

---

## D2. Output Schema

```python
@dataclass
class SemanticCheck:
    """시맨틱 보존 검증 결과"""
    passed: bool
    checks_performed: list[str]                 # 수행한 검증 목록
    violations: list[str] = field(default_factory=list)  # 위반 사항
    confidence: float = 0.0                     # 검증 신뢰도

@dataclass
class TestRegressionCheck:
    """테스트 회귀 검증 결과"""
    passed: bool
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    coverage_before: float = 0.0
    coverage_after: float = 0.0
    coverage_threshold_met: bool = True         # LOCK-DT-10
    failed_test_names: list[str] = field(default_factory=list)

@dataclass
class TransformValidationResult:
    """안전한 변환 검증 결과"""
    status: str                                 # "approved", "rejected", "warning"
    semantic_check: SemanticCheck
    test_check: TestRegressionCheck
    rollback_available: bool = True
    snapshot_id: Optional[str] = None
    diff_preview: Optional[str] = None
    approval_required: bool = False             # 사람 승인 필요 여부
    latency_ms: float = 0.0
    trace_id: Optional[str] = None

@dataclass
class EscalationPayload:
    """안전한 변환 에스컬레이션 페이로드"""
    trigger: str                                # 에스컬레이션 사유
    request: TransformValidationRequest
    validation_result: Optional[TransformValidationResult] = None
    error_code: str = ""
    recommended_action: str = ""
    escalation_level: str = "L2"                # L1=자동재시도, L2=사람검토, L3=긴급
```

---

## D3. Algorithm

```
시간복잡도: O(N + T)
  - N: 변경 영향 라인 수 (시맨틱 검증)
  - T: 테스트 실행 시간 (회귀 검증)
공간복잡도: O(N) — 스냅샷 + diff
```

### 시맨틱 보존 검증 절차

```python
async def validate_transform(
    request: TransformValidationRequest
) -> TransformValidationResult:
    """
    안전한 변환 검증 파이프라인.
    ABC 패턴: Auditor → Barrier → Certifier
      - Auditor: 변경 사항 감사 (시맨틱, 타입, 의존성)
      - Barrier: 테스트 회귀 검증 (LOCK-DT-10)
      - Certifier: 최종 승인/거부 판정
    """
    # 0. 무결성 검증 — 원본 해시 확인
    if not verify_source_hash(request.source_hash):
        return rejected("E_INTEGRITY", "소스 파일이 변경됨")
    
    # 1. Auditor: 시맨틱 보존 검증
    semantic = await check_semantic_preservation(request.changes)
    
    # 2. Auditor: 타입 호환성 검증
    type_ok = check_type_compatibility(request.changes)
    if not type_ok:
        semantic.violations.append("타입 호환성 위반")
        semantic.passed = False
    
    # 3. Auditor: 의존성 영향 분석
    dep_ok = check_dependency_impact(request.changes, request.project_root)
    if not dep_ok:
        semantic.violations.append("의존성 파괴")
        semantic.passed = False
    
    # 4. Barrier: 테스트 회귀 검증 (LOCK-DT-10)
    test_check = await run_test_regression(
        request.test_suite_path,
        coverage_threshold=request.coverage_threshold,
        timeout_ms=request.timeout_ms
    )
    
    # 5. Certifier: 최종 판정
    if not semantic.passed:
        return TransformValidationResult(
            status="rejected",
            semantic_check=semantic,
            test_check=test_check,
            snapshot_id=request.snapshot_id,
            trace_id=request.trace_id
        )
    
    if not test_check.passed or not test_check.coverage_threshold_met:
        return TransformValidationResult(
            status="rejected",
            semantic_check=semantic,
            test_check=test_check,
            snapshot_id=request.snapshot_id,
            approval_required=True,
            trace_id=request.trace_id
        )
    
    return TransformValidationResult(
        status="approved",
        semantic_check=semantic,
        test_check=test_check,
        snapshot_id=request.snapshot_id,
        diff_preview=generate_diff(request.changes),
        trace_id=request.trace_id
    )
```

### 시맨틱 보존 검증 상세

```python
async def check_semantic_preservation(
    changes: list[RefactoringChange]
) -> SemanticCheck:
    """
    시맨틱 보존 검증: 리팩토링 전후 동작 동일성 확인.
    
    검증 항목:
    1. 반환값 보존 — 함수 반환 타입/값 불변
    2. 부작용 보존 — I/O, 전역 상태 변경 순서 불변
    3. 예외 전파 보존 — 예외 타입/발생 조건 불변
    4. 참조 무결성 — 모든 참조가 올바른 대상을 가리킴
    5. 실행 순서 보존 — 문장 실행 순서 불변
    """
    checks = [
        "return_value_preservation",
        "side_effect_preservation",
        "exception_propagation",
        "reference_integrity",
        "execution_order"
    ]
    violations = []
    
    for change in changes:
        # LLM 기반 시맨틱 비교
        result = await llm_compare_semantics(
            change.original_code, change.refactored_code
        )
        if not result.equivalent:
            violations.append(
                f"{change.file_path}:{change.line_start} — {result.reason}"
            )
    
    return SemanticCheck(
        passed=len(violations) == 0,
        checks_performed=checks,
        violations=violations,
        confidence=compute_confidence(changes)
    )
```

### 패턴별 전제조건/후조건

| 패턴 | 전제조건 (Pre-condition) | 후조건 (Post-condition) |
|------|------------------------|----------------------|
| Extract Variable | 표현식이 순수(부작용 없음) | 변수 선언 + 참조 교체 완료 |
| Extract Function | 선택 블록이 단일 진입/단일 출구 | 함수 호출로 대체 + 파라미터/반환값 정확 |
| Inline | 참조 횟수 = 1 또는 순수 함수 | 모든 참조가 정의로 대체됨 |
| Move | 대상 모듈이 존재 | import 문 갱신 + 참조 무결성 |
| Rename | 새 이름이 스코프 내 충돌 없음 | 모든 참조가 새 이름으로 변경 |
| Remove Dead Code | 참조 횟수 = 0 | 코드 제거 + 기존 동작 불변 |
| Deduplicate | 클론 코드 블록 >= 2개 | 공통 함수 1개 + 호출 대체 |

---

### 롤백 전략

```python
class RollbackManager:
    """
    롤백 관리자 — 모든 리팩토링 변경은 롤백 가능해야 함.
    
    복구 흐름:
    1. 리팩토링 전 스냅샷 저장 (git stash)
    2. 변경 적용
    3. 검증 실패 시 즉시 롤백
    4. 검증 성공 시 스냅샷 유지 (수동 롤백 가능)
    """
    
    def save_snapshot(self, file_path: str) -> str:
        """변경 전 스냅샷 저장. 반환: snapshot_id"""
        snapshot_id = f"snap-{timestamp()}-{random_hex(6)}"
        git_stash_create(file_path, snapshot_id)
        return snapshot_id
    
    def rollback(self, snapshot_id: str) -> bool:
        """스냅샷으로 롤백. 반환: 성공 여부"""
        return git_stash_apply(snapshot_id)
    
    def discard_snapshot(self, snapshot_id: str) -> bool:
        """검증 성공 후 일정 기간(24시간) 후 스냅샷 삭제"""
        schedule_cleanup(snapshot_id, delay_hours=24)
        return True
```

### 복구 흐름도

```
리팩토링 변환 요청
  │
  ├─ 1. 스냅샷 저장 (RollbackManager.save_snapshot)
  │
  ├─ 2. 변경 적용 (dry_run이면 미적용)
  │
  ├─ 3. 시맨틱 보존 검증
  │   ├─ 통과 → 4번으로
  │   └─ 실패 → 즉시 롤백 → EscalationPayload(L2) → 종료
  │
  ├─ 4. 테스트 회귀 검증 (LOCK-DT-10: 커버리지 >= 80%)
  │   ├─ 통과 + 커버리지 충족 → 5번으로
  │   ├─ 테스트 실패 → 즉시 롤백 → EscalationPayload(L2) → 종료
  │   └─ 커버리지 미달 → 경고 + 사람 승인 요청
  │
  ├─ 5. 최종 승인
  │   ├─ approved → diff 반환 + 스냅샷 유지 (24시간 후 삭제)
  │   └─ rejected → 롤백 → 사유 기록
  │
  └─ 종료
```

---

## D4. Error Handling

| 에러 코드 | recoverable | 처리 | 에스컬레이션 |
|-----------|-------------|------|-------------|
| E_INTEGRITY | No | 원본 파일 해시 불일치 → 변환 거부 | L2 사람 검토 |
| E_SEMANTIC_BREAK | No | 시맨틱 보존 실패 → 즉시 롤백 | L2 사람 검토 |
| E_TEST_FAIL | No | 테스트 실패 → 즉시 롤백 | L2 사람 검토 |
| E_COVERAGE_LOW | Yes | 커버리지 < 80% (LOCK-DT-10) → 경고 + 승인 요청 | L1 자동 |
| E_TIMEOUT | Yes | 검증 타임아웃 (LOCK-DT-06: 30초) → 부분 검증 결과 | L1 자동재시도 |
| E_ROLLBACK_FAIL | No | 롤백 실패 → 긴급 에스컬레이션 | L3 긴급 |
| E_TYPE_MISMATCH | No | 타입 호환성 위반 → 변환 거부 | L2 사람 검토 |
| E_DEP_BREAK | No | 의존성 파괴 → 변환 거부 | L2 사람 검토 |

### 예외 처리 정책 표

| 정책 | 설명 | 근거 |
|------|------|------|
| 무결성 우선 | 원본 해시 불일치 시 어떤 변환도 거부 | 동시 편집 안전성 |
| 시맨틱 절대 | 시맨틱 파괴 시 무조건 롤백 (override 불가) | 안전한 리팩토링 원칙 |
| 커버리지 임계 | 80% 미만이면 경고 (STRICT 모드에서는 거부) | LOCK-DT-10 |
| 타임아웃 강제 | 30초 초과 시 검증 중단 | LOCK-DT-06 |
| 롤백 실패 긴급 | 롤백 자체가 실패하면 L3 에스컬레이션 | 데이터 무결성 최우선 |

---

## D5. Dependencies

| 의존성 | 버전 | 용도 |
|--------|------|------|
| pytest | >= 7.0 | 테스트 실행 |
| coverage | >= 7.0 | 커버리지 측정 (LOCK-DT-10) |
| git (libgit2) | >= 2.0 | 스냅샷/롤백 |
| LLM API | - | 시맨틱 비교 |
| difflib | stdlib | diff 생성 |
| hashlib | stdlib | 원본 해시 검증 |

### 의존성 그래프

```
safe_transform_rules.md
  ├── pattern_catalog.md (변환 요청 수신 — TransformRequest)
  ├── ast_pipeline.md (분석 결과 참조 — ASTContext)
  ├── L-001 dev_node_architecture.md (파이프라인 통합)
  ├── L-004 test_pipeline.md (테스트 실행 연동 — Phase 2)
  └── L-005 code_review_ai.md (변환 후 리뷰 — Phase 2)
```

---

## D6. Performance

| 메트릭 | 목표 | 비고 |
|--------|------|------|
| 시맨틱 검증 (LLM) | < 5초 | LLM API 호출 1회 |
| 타입 호환성 검증 | < 1초 | AST 기반 로컬 |
| 의존성 분석 | < 2초 | 프로젝트 인덱스 활용 |
| 테스트 실행 | < 20초 | LOCK-DT-06 잔여 시간 내 |
| 전체 검증 파이프라인 | < 30초 | LOCK-DT-06 절대 상한 |
| 스냅샷 생성 | < 1초 | git stash |
| 롤백 실행 | < 1초 | git stash apply |

### Big-O 요약

| 연산 | 시간 복잡도 | 공간 복잡도 |
|------|-----------|-----------|
| 해시 검증 | O(N) | O(1) |
| 시맨틱 검증 | O(C) | O(C) |
| 타입 검증 | O(C * S) | O(S) |
| 의존성 분석 | O(F) | O(F) |
| 테스트 실행 | O(T) | O(1) |
| diff 생성 | O(N) | O(N) |

> N = 파일 크기, C = 변경 수, S = 심볼 수, F = 프로젝트 파일 수, T = 테스트 수

---

## D7. Test Spec -- Phase 2 테스트 시나리오

| # | 시나리오 | 입력 | 기대 결과 |
|---|---------|------|----------|
| T1 | 시맨틱 보존 성공 | 순수 함수 추출 변경 | status="approved" |
| T2 | 시맨틱 파괴 감지 | 부작용 있는 코드 인라인 | status="rejected", semantic violation |
| T3 | 테스트 회귀 감지 | 리팩토링 후 1개 테스트 실패 | status="rejected", failed_tests=1 |
| T4 | 커버리지 미달 | 리팩토링 후 커버리지 75% | E_COVERAGE_LOW, approval_required=True |
| T5 | 커버리지 충족 | 리팩토링 후 커버리지 85% | coverage_threshold_met=True |
| T6 | 원본 해시 불일치 | 동시 편집 후 검증 | E_INTEGRITY, 즉시 거부 |
| T7 | 롤백 성공 | 시맨틱 파괴 후 롤백 | 원본 복원 확인 |
| T8 | 타임아웃 | 대규모 테스트 + timeout_ms=100 | E_TIMEOUT, 부분 결과 |
| T9 | 타입 호환성 위반 | int → str 변환 | E_TYPE_MISMATCH |
| T10 | 의존성 파괴 | 다른 모듈 참조 함수 삭제 | E_DEP_BREAK |
| T11 | STRICT 모드 커버리지 | 커버리지 79% + STRICT | status="rejected" |
| T12 | LENIENT 모드 시맨틱 | 경미한 시맨틱 차이 + LENIENT | status="warning" |

---

## D8. Security

- 테스트 실행 시 LOCK-DT-06 (30초) 타임아웃 강제 적용 — 무한 루프 테스트 방지
- 스냅샷은 .git 내부에만 저장 — 외부 유출 방지
- 롤백 이력은 감사 로그에 기록 (누가, 언제, 어떤 변경을 롤백했는지)
- 시맨틱 검증에 LLM을 사용하는 경우, 소스코드 프라이버시 모드에서는 로컬 모델만 허용
- 테스트 실행 환경 격리: 리팩토링 검증용 테스트는 샌드박스 환경에서 실행

---

## 로깅 포맷 (R-01-7)

```json
{
  "trace_id": "dt-transform-20260410-qrs456",
  "timestamp": "2026-04-10T10:10:00.000Z",
  "service": "safe_transform_rules",
  "level": "INFO",
  "event": "transform_validation_complete",
  "error": { "code": null, "message": null, "stack_trace": null },
  "context": {
    "changes_count": 2,
    "validation_level": "normal",
    "semantic_passed": true,
    "test_passed": true,
    "coverage_before": 85.2,
    "coverage_after": 84.8,
    "coverage_threshold": 80.0,
    "rollback_available": true,
    "snapshot_id": "snap-20260410-001"
  },
  "recovery": {
    "fallback_used": false,
    "retry_count": 0,
    "rollback_applied": false,
    "escalation": null,
    "confidence_penalty": 0.0
  }
}
```

---

## 세션간 인터페이스 Cross-Check

```python
# 입력 인터페이스: pattern_catalog.md → safe_transform_rules.md
# TransformRequest (pattern_catalog.md 정의) → TransformValidationRequest 매핑
# TransformRequest.changes → TransformValidationRequest.changes
# TransformRequest.snapshot_id → TransformValidationRequest.snapshot_id
# TransformRequest.source_hash → TransformValidationRequest.source_hash

# 출력 인터페이스: safe_transform_rules.md → pattern_catalog.md
# TransformValidationResult.status → RefactoringResult 판정 기준
# TransformValidationResult.snapshot_id → RefactoringResult.rollback_snapshot_id
```
