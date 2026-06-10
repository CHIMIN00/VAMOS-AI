# Layer 5: VERIFICATION — 수리 후 검증 상세

> **도메인**: 6-5_SDAR-System / 01_five-layer-pipeline
> **Tier**: 6 (System-wide Components)
> **정본**: SDAR_SPEC **§2.6** (Layer 5 VERIFICATION), **§9.2** (운영 제한 — OBSERVATION_PERIOD, ROLLBACK_TIMEOUT, COOLDOWN_BETWEEN_REPAIRS)
> **Part2 출처**: §6.9 (L5412~L5419) — When/Where 정본
> **수정 정책**: Phase 변경 시 갱신 (종합계획서 §8.2)
> **LOCK 매핑**: L1 (5-Layer Pipeline 단계 정의), L8 (SNAPSHOT_MANDATORY), L9 (NOTIFICATION_MANDATORY), L11 (OBSERVATION_PERIOD), L12 (ROLLBACK_TIMEOUT), L13 (COOLDOWN_BETWEEN_REPAIRS)
> **Phase**: P1-5
> **생성일**: 2026-04-13
> **ISS 해결**: ISS-1 Layer 5

---

## 교차 참조 블록

| 참조 대상 | 관계 |
|----------|------|
| **SDAR_SPEC §2.6** | Layer 5 VERIFICATION 정의 정본 — 3단계 검증 프로세스, SDARVerificationResult 스키마, 이벤트 |
| **SDAR_SPEC §7.2** | S5_VERIFIED 상태 타임아웃 300초 (관찰 기간, L11과 동일) |
| **SDAR_SPEC §7.3** | 상태 전이: S4→S5 (수리 완료), S5→S6 (검증 통과/경고), S5→S4 (검증 실패→롤백) |
| **SDAR_SPEC §8.3** | SDARRepairResult 스키마 — Layer 5 입력 (repair_result_ref 참조) |
| **SDAR_SPEC §8.4** | 스키마 간 관계: SDARRepairResult → SDARVerificationResult (repair_result_ref) |
| **SDAR_SPEC §9.2** | 운영 제한: OBSERVATION_PERIOD=300초(L11), ROLLBACK_TIMEOUT=300초(L12), COOLDOWN_BETWEEN_REPAIRS=60초(L13), SNAPSHOT_MANDATORY(L8) |
| **SDAR_SPEC §9.4** | Kill Switch — 검증 중에도 ANY→S0 즉시 전이 가능 (LOCK L14) |
| **SDAR_SPEC §9.5** | CATEGORY E 특별 규칙 — 자동수리 절대 금지 (LOCK L15, 검증 도달 전 차단) |
| **SDAR_SPEC §6.1** | 5-Gate 통합 — SelfCheckGate: 수리 후 품질 확인 (Layer 5 적용) |
| **Part2 §6.9** | When/Where 정본 — Phase별 참조 범위, 구현 위치 |
| **D2.0-02 §7 I-25** | I-25 SDAR Engine 모듈 정의 |
| **01_five-layer-pipeline/_index.md** | P0 총괄 — Layer 5 개요 |
| **01_five-layer-pipeline/repair.md** | Layer 4 산출물 — SDARRepairResult 스키마 (Layer 5 입력) |
| **02_state-machine/_index.md** | Layer 5 = VERIFYING 상태(S5)와 동기화 |
| **04_self-diagnosis/gate_integration.md** | SelfCheckGate — 수리 후 품질 검증 (Phase 2 상세) |
| **AUTHORITY_CHAIN.md §4** | LOCK L1, L8, L9, L11, L12, L13 레지스트리 |
| **CONFLICT_LOG.md** | 신규 CONFLICT 발견 시 등재 |

---

## 1. 개요

Layer 5 VERIFICATION은 SDAR 5-Layer Pipeline의 마지막 단계로서, Layer 4 REPAIR이 출력한 `SDARRepairResult`를 입력으로 받아 **수리 결과 검증, 회귀 검사, 롤백 판정**을 수행하고, 최종 `SDARVerificationResult`를 출력한다. (LOCK L1: Detection → Diagnosis → Prescription → Repair → **Verification**)

이 계층은 SDAR의 안전성을 최종 보장하는 관문(Gate)으로, 수리가 실제로 문제를 해결했는지, 새로운 문제를 야기하지 않았는지를 확인한다. (SDAR_SPEC §2.6)

### 1.1 핵심 요구사항

- 3단계 검증 프로세스: Post-Repair Validation → Regression Check → Rollback Trigger (SDAR_SPEC §2.6)
- OBSERVATION_PERIOD=300초 (LOCK L11) — 수리 후 최소 5분 관찰 기간
- ROLLBACK_TIMEOUT=300초 (LOCK L12) — 롤백 실행 최대 300초, 초과 시 인간 에스컬레이션
- COOLDOWN_BETWEEN_REPAIRS=60초 (LOCK L13) — 검증 완료 후 동일 액션 반복 간 최소 대기
- SNAPSHOT_MANDATORY (LOCK L8) — 롤백 시 스냅샷 복원 절차 (MEDIUM/HIGH risk)
- NOTIFICATION_MANDATORY (LOCK L9) — 모든 검증 활동 알림 필수
- `SDARVerificationResult` 출력 스키마를 통한 표준화된 검증 결과 전달 (SDAR_SPEC §2.6)
- S5_VERIFIED 상태 타임아웃 300초 (SDAR_SPEC §7.2) — 관찰 기간과 동일
- SelfCheckGate 적용: 수리 후 Self-check 재실행하여 품질 확인 (SDAR_SPEC §6.1)

---

## 2. 3단계 검증 프로세스 상세 (SDAR_SPEC §2.6)

### 2.1 검증 흐름 다이어그램

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Layer 5: VERIFICATION 검증 흐름                    │
│                                                                     │
│  SDARRepairResult 수신 (Layer 4 출력)                                │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────┐                                        │
│  │ Step 5-1: Post-Repair   │                                        │
│  │ Validation (수리 후 검증) │                                        │
│  │                         │                                        │
│  │ • post_conditions 검증   │                                        │
│  │ • Health Check 재실행    │                                        │
│  │ • 원래 오류 재현 확인     │                                        │
│  └──────────┬──────────────┘                                        │
│             │                                                       │
│        ┌────┴────┐                                                  │
│        │ PASS?   │                                                  │
│        └────┬────┘                                                  │
│        YES  │  NO → Step 5-3 즉시 (롤백 판정)                        │
│             ▼                                                       │
│  ┌─────────────────────────┐                                        │
│  │ Step 5-2: Regression    │                                        │
│  │ Check (회귀 검사)        │                                        │
│  │                         │                                        │
│  │ • 영향 범위 모듈 상태    │  ← OBSERVATION_PERIOD=300초 (L11)      │
│  │ • 성능 지표 비교         │                                        │
│  │ • 새로운 오류 모니터링   │                                        │
│  └──────────┬──────────────┘                                        │
│             │                                                       │
│        ┌────┴────┐                                                  │
│        │ PASS?   │                                                  │
│        └────┬────┘                                                  │
│   PASS  │  WARN │  FAIL                                             │
│         │       │    │                                              │
│         ▼       ▼    ▼                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────┐                 │
│  │ verdict  │ │ verdict  │ │ Step 5-3: Rollback   │                 │
│  │ = PASS   │ │ = WARN   │ │ Trigger (롤백 판정)   │                 │
│  └────┬─────┘ └────┬─────┘ │                      │                 │
│       │            │       │ • MEDIUM/HIGH: 스냅샷 │ ← L8, L12      │
│       │            │       │ • LOW: 역동작 실행    │                 │
│       │            │       └──────────┬───────────┘                 │
│       │            │                  │                              │
│       ▼            ▼                  ▼                              │
│  SDARVerificationResult 생성 + oc.sdar.verification.completed        │
│       │                                                             │
│       ▼                                                             │
│  COOLDOWN=60초 (L13) 대기 후 S6_DONE 전이                            │
└─────────────────────────────────────────────────────────────────────┘
```

### 2.2 Step 5-1: Post-Repair Validation (수리 후 검증)

**목적**: 수리 계획에서 정의한 사후 조건(post_conditions)이 실제로 충족되었는지 확인한다.

**입력**: `SDARRepairResult` (Layer 4 출력)

**절차**:

1. **사후 조건 전수 검증**: `SDARRepairPlan.post_conditions`에 정의된 모든 조건을 순차 평가
   - 각 조건별 passed/failed 판정 + 상세 사유 기록
   - 전체 조건 중 하나라도 FAIL → Step 5-3 (Rollback Trigger)으로 즉시 전이
2. **Health Check 재실행**: 수리 대상 모듈의 Health Check 재실행
   - Self-check score 측정 (수리 전 baseline과 비교)
   - 모듈 상태가 `healthy` 또는 `degraded`(경고) 이상인지 확인
3. **원래 오류 재현 확인**: 수리 대상이었던 원래 오류가 더 이상 재현되지 않는지 확인
   - `SDARDiagnosis.error_code` 기준으로 오류 발생 여부 모니터링
   - 재현 시 → FAIL 판정

**알고리즘**:

```
FUNCTION post_repair_validate(
    repair_result: SDARRepairResult,
    repair_plan: SDARRepairPlan
) -> PostRepairValidationResult:
    # 시간복잡도: O(C) where C = len(post_conditions)
    # ABC 패턴: BaseValidator(ABC).validate(result, plan) → PostRepairValidationResult
    # LOCK 참조: L9 (NOTIFICATION_MANDATORY)

    results = []
    FOR EACH condition IN repair_plan.post_conditions:
        result = evaluate_condition(condition, repair_result)
        results.append({
            "condition": condition,
            "passed": result.passed,
            "detail": result.detail
        })
        IF NOT result.passed:
            EMIT oc.sdar.verification.failed
            RETURN PostRepairValidationResult(
                passed=False,
                condition_results=results,
                reason="post_condition_failed"
            )

    health = run_health_check(repair_result.target_modules)
    IF health.score < baseline_score:
        RETURN PostRepairValidationResult(
            passed=False,
            condition_results=results,
            reason="health_check_degraded"
        )

    original_error = check_error_recurrence(
        repair_result.diagnosis_ref,
        timeout_s=30
    )
    IF original_error.recurred:
        RETURN PostRepairValidationResult(
            passed=False,
            condition_results=results,
            reason="original_error_recurred"
        )

    RETURN PostRepairValidationResult(
        passed=True,
        condition_results=results,
        reason="all_conditions_met"
    )
```

### 2.3 Step 5-2: Regression Check (회귀 검사)

**목적**: 수리가 다른 모듈에 부정적 영향을 미치지 않았는지 5분간 관찰한다.

**OBSERVATION_PERIOD=300초 (LOCK L11)**: 수리 후 최소 5분간 모니터링 메트릭을 수집하여 회귀 여부를 판정한다.

**절차**:

1. **영향 범위 모듈 상태 확인**: `SDARDiagnosis.impact.scope`에 정의된 모든 모듈의 상태 확인
   - 각 모듈별 Health Check 실행
   - 기존에 healthy 상태였던 모듈이 degraded/unhealthy로 변경되었는지 확인
2. **성능 지표 비교** (수리 전 vs 수리 후, 5분 관찰):
   - **응답 시간 변화**: 평균 응답 시간이 수리 전 baseline 대비 20% 이상 증가 → WARN
   - **Self-check score 변화**: 수리 전 score보다 하락 → FAIL (SDAR_SPEC §2.6 Step 5-3 롤백 조건)
   - **QoD score 변화**: QoD score 하락 → WARN (관찰 지속)
   - **에러율 변화**: 에러율이 수리 전 baseline 대비 상승 → WARN/FAIL (심각도에 따라)
3. **새로운 오류 발생 확인** (5분 관찰 기간 내):
   - `error`/`critical` 심각도 이벤트 발생 여부 모니터링
   - 새로운 오류 발생 시 → FAIL 판정 (SDAR_SPEC §2.6 Step 5-3 롤백 조건)

**알고리즘**:

```
FUNCTION regression_check(
    repair_result: SDARRepairResult,
    diagnosis: SDARDiagnosis,
    observation_period_s: int = 300  # LOCK L11
) -> RegressionCheckResult:
    # 시간복잡도: O(M * T) where M = modules in blast_radius, T = observation ticks
    # ABC 패턴: BaseRegressionChecker(ABC).check(result, diagnosis) → RegressionCheckResult
    # LOCK 참조: L11 (OBSERVATION_PERIOD=300초)

    metrics_before = capture_current_metrics(diagnosis.impact.scope)
    start_time = now()

    WHILE elapsed(start_time) < observation_period_s:
        # 10초 주기로 메트릭 수집
        current_metrics = capture_current_metrics(diagnosis.impact.scope)

        # 새로운 error/critical 이벤트 확인
        new_errors = check_new_errors(
            since=repair_result.completed_at,
            severity_filter=["error", "critical"]
        )
        IF new_errors.count > 0:
            RETURN RegressionCheckResult(
                passed=False,
                metrics_before=metrics_before,
                metrics_after=current_metrics,
                new_errors=new_errors,
                verdict="FAIL",
                reason="new_critical_errors_during_observation"
            )

        # Self-check score 하락 확인
        IF current_metrics.self_check_score < metrics_before.self_check_score:
            RETURN RegressionCheckResult(
                passed=False,
                metrics_before=metrics_before,
                metrics_after=current_metrics,
                new_errors=[],
                verdict="FAIL",
                reason="self_check_score_degraded"
            )

        SLEEP(10)  # 10초 주기 폴링

    # 관찰 기간 완료 후 최종 메트릭 비교
    final_metrics = capture_current_metrics(diagnosis.impact.scope)

    IF metrics_before.avg_response_time == 0:
        response_time_change = 0.0  # baseline 0 — 회귀 측정 불가, 변화 0 처리 (div-by-zero 방지)
    ELSE:
        response_time_change = (
            (final_metrics.avg_response_time - metrics_before.avg_response_time)
            / metrics_before.avg_response_time
        )
    IF response_time_change > 0.2:  # 20% 이상 증가
        verdict = "WARN"
    ELIF final_metrics.error_rate > metrics_before.error_rate:
        verdict = "WARN"
    ELSE:
        verdict = "PASS"

    RETURN RegressionCheckResult(
        passed=(verdict != "FAIL"),
        metrics_before=metrics_before,
        metrics_after=final_metrics,
        new_errors=[],
        verdict=verdict,
        reason="observation_completed"
    )
```

### 2.4 Step 5-3: Rollback Trigger (롤백 판정)

**목적**: 검증 실패 시 수리 전 상태로 자동 복원한다.

**ROLLBACK_TIMEOUT=300초 (LOCK L12)**: 롤백 실행 최대 300초, 초과 시 인간 에스컬레이션.

**롤백 트리거 조건** (하나라도 해당되면 자동 롤백 — SDAR_SPEC §2.6):

| # | 조건 | 감지 단계 | 즉시성 |
|---|------|----------|--------|
| RT-1 | `post_conditions` 미충족 | Step 5-1 | 즉시 |
| RT-2 | 수리 후 새로운 `error`/`critical` 심각도 이벤트 발생 | Step 5-2 | 즉시 |
| RT-3 | Self-check score가 수리 전보다 하락 | Step 5-2 | 즉시 |
| RT-4 | 사용자가 수동 롤백 명령 발행 | 관찰 기간 중 언제든 | 즉시 |

**롤백 실행 전략** (SDAR_SPEC §2.6 + LOCK L8):

| Risk Level | 롤백 전략 | 스냅샷 | 타임아웃 |
|-----------|----------|--------|---------|
| **MEDIUM/HIGH** | `snapshot_restore` — 스냅샷에서 복원 | 필수 (LOCK L8) | 300초 (LOCK L12) |
| **LOW** | `reverse_actions` — 역동작 실행 (e.g., 재시작한 서비스 원상복구) | 선택 | 300초 (LOCK L12) |

**알고리즘**:

```
FUNCTION execute_rollback(
    repair_result: SDARRepairResult,
    rollback_plan: SDARRollbackPlan,
    rollback_timeout_s: int = 300  # LOCK L12
) -> RollbackResult:
    # 시간복잡도: O(S) where S = snapshot restore steps or reverse steps
    # ABC 패턴: BaseRollbackExecutor(ABC).execute(result, plan) → RollbackResult
    # LOCK 참조: L8 (SNAPSHOT_MANDATORY), L12 (ROLLBACK_TIMEOUT=300초), L14 (Kill Switch)

    EMIT oc.sdar.verification.failed

    start_time = now()

    IF rollback_plan.strategy == "snapshot_restore":
        # MEDIUM/HIGH risk: 스냅샷 복원 (LOCK L8)
        IF repair_result.snapshot_id IS NULL:
            # 스냅샷 누락 — 긴급 에스컬레이션
            EMIT SDAR_ROLLBACK_FAILED
            RETURN RollbackResult(
                success=False,
                strategy="snapshot_restore",
                reason="snapshot_missing",
                escalation_required=True
            )

        restore_result = restore_snapshot(
            snapshot_id=repair_result.snapshot_id,
            timeout_s=rollback_timeout_s
        )

        IF elapsed(start_time) > rollback_timeout_s:
            # 롤백 타임아웃 — 인간 에스컬레이션 (LOCK L12)
            EMIT SDAR_ROLLBACK_FAILED
            # Kill Switch 자동 ON (LOCK L14: SDAR_ROLLBACK_FAILED 시 자동 ON)
            RETURN RollbackResult(
                success=False,
                strategy="snapshot_restore",
                reason="rollback_timeout_exceeded",
                escalation_required=True,
                kill_switch_triggered=True
            )

    ELIF rollback_plan.strategy == "reverse_actions":
        # LOW risk: 역동작 실행
        FOR EACH step IN REVERSE(rollback_plan.reverse_steps):
            step_result = execute_reverse_step(step, timeout_s=rollback_timeout_s - elapsed(start_time))
            IF NOT step_result.success:
                EMIT SDAR_ROLLBACK_FAILED
                RETURN RollbackResult(
                    success=False,
                    strategy="reverse_actions",
                    reason=f"reverse_step_{step.step_order}_failed",
                    escalation_required=True
                )

    ELIF rollback_plan.strategy == "manual":
        # 수동 롤백 — 에스컬레이션
        RETURN RollbackResult(
            success=False,
            strategy="manual",
            reason="manual_rollback_required",
            escalation_required=True
        )

    EMIT oc.sdar.verification.rollback_executed
    RETURN RollbackResult(
        success=True,
        strategy=rollback_plan.strategy,
        reason="rollback_completed",
        duration_ms=elapsed_ms(start_time)
    )
```

---

## 3. SDARVerificationResult 출력 스키마 (SDAR_SPEC §2.6)

### 3.1 스키마 정의 (Pydantic v2)

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Literal
from datetime import datetime


class PostConditionResult(BaseModel):
    """사후 조건 개별 검증 결과"""
    condition: str = Field(..., description="검증 조건 문자열")
    passed: bool = Field(..., description="조건 충족 여부")
    detail: str = Field(default="", description="상세 사유")


class RegressionCheckDetail(BaseModel):
    """회귀 검사 상세 결과"""
    passed: bool = Field(..., description="회귀 검사 통과 여부")
    metrics_before: dict = Field(
        ..., description="수리 전 메트릭 {avg_response_time, self_check_score, qod_score, error_rate}"
    )
    metrics_after: dict = Field(
        ..., description="수리 후 메트릭 (동일 구조)"
    )
    new_errors: List[dict] = Field(
        default_factory=list,
        description="관찰 기간 내 발견된 새 오류 [{error_code, severity, timestamp, module}]"
    )
    observation_duration_s: int = Field(
        default=300, description="실제 관찰 소요 시간 (초)"
    )


class RollbackDetail(BaseModel):
    """롤백 실행 상세 결과"""
    strategy: Literal["snapshot_restore", "reverse_actions", "manual"] = Field(
        ..., description="롤백 전략"
    )
    snapshot_id: Optional[str] = Field(None, description="복원된 스냅샷 ID")
    success: bool = Field(..., description="롤백 성공 여부")
    duration_ms: int = Field(..., description="롤백 소요 시간 (ms)")
    reason: str = Field(..., description="롤백 결과 사유")
    escalation_required: bool = Field(
        default=False, description="인간 에스컬레이션 필요 여부"
    )
    kill_switch_triggered: bool = Field(
        default=False, description="Kill Switch 자동 ON 여부 (LOCK L14)"
    )


class SDARVerificationResult(BaseModel):
    """Layer 5 수리 검증 결과 스키마 (SDAR_SPEC §2.6)"""
    verification_id: str = Field(..., description="검증 결과 고유 ID (UUID v4)")
    repair_result_ref: str = Field(
        ..., description="SDARRepairResult.result_id 참조"
    )
    trace_id: str = Field(..., description="연관 trace_id")
    verified_at: str = Field(..., description="검증 완료 시각 (ISO8601 UTC)")

    # Step 5-1: Post-Repair Validation 결과
    post_condition_results: List[PostConditionResult] = Field(
        ..., description="사후 조건 개별 검증 결과 목록"
    )

    # Step 5-2: Regression Check 결과
    regression_check: RegressionCheckDetail = Field(
        ..., description="회귀 검사 상세 결과"
    )

    # 최종 판정
    verdict: Literal["PASS", "WARN", "FAIL"] = Field(
        ..., description="최종 검증 판정 — PASS(통과)/WARN(경고, 관찰 지속)/FAIL(실패, 롤백)"
    )

    # 롤백
    rollback_triggered: bool = Field(
        default=False, description="롤백 실행 여부"
    )
    rollback_result: Optional[RollbackDetail] = Field(
        None, description="롤백 실행 시 상세 결과"
    )

    # 관찰 기간
    observation_period_s: int = Field(
        default=300, description="관찰 기간 (초) — LOCK L11"
    )

    # 후속 조치 권고
    recommendations: List[str] = Field(
        default_factory=list, description="후속 조치 권고 목록"
    )

    # 알림 (LOCK L9)
    notification_sent: bool = Field(
        default=False, description="알림 발송 여부"
    )
    notification_channel: Optional[str] = Field(
        None, description="알림 채널 (ui/log/both)"
    )

    # S-8 거버넌스 보고용
    governance_summary: dict = Field(
        default_factory=dict,
        description="거버넌스 보고 요약 {verification_verdict, rollback_executed, observation_period_s, new_errors_count}"
    )

    model_config = ConfigDict(extra="forbid")
```

### 3.2 스키마 필드 상세

| 필드 | 타입 | 필수 | 설명 | 정본 |
|------|------|------|------|------|
| `verification_id` | `str` | Y | UUID v4 | SDAR_SPEC §2.6 |
| `repair_result_ref` | `str` | Y | `SDARRepairResult.result_id` 참조 | SDAR_SPEC §8.4 |
| `trace_id` | `str` | Y | 전체 SDAR 프로세스 추적 ID | SDAR_SPEC §2.6 |
| `verified_at` | `str` | Y | ISO8601 UTC 검증 완료 시각 | SDAR_SPEC §2.6 |
| `post_condition_results` | `List[PostConditionResult]` | Y | 사후 조건 검증 목록 | SDAR_SPEC §2.6 Step 5-1 |
| `regression_check` | `RegressionCheckDetail` | Y | 회귀 검사 상세 | SDAR_SPEC §2.6 Step 5-2 |
| `verdict` | `PASS/WARN/FAIL` | Y | 최종 판정 | SDAR_SPEC §2.6 |
| `rollback_triggered` | `bool` | Y | 롤백 실행 여부 | SDAR_SPEC §2.6 Step 5-3 |
| `rollback_result` | `RollbackDetail?` | N | 롤백 실행 시 결과 | SDAR_SPEC §2.6 |
| `observation_period_s` | `int` | Y | 관찰 기간 (초) | LOCK L11=300 |
| `recommendations` | `List[str]` | N | 후속 조치 권고 | SDAR_SPEC §2.6 |
| `notification_sent` | `bool` | N (default=False) | 알림 발송 여부 | LOCK L9 (NOTIFICATION_MANDATORY) |
| `notification_channel` | `str?` | N | 알림 채널 (ui/log/both) | LOCK L9 |
| `governance_summary` | `dict` | N (default={}) | 거버넌스 보고 요약 {verification_verdict, rollback_executed, observation_period_s, new_errors_count} | LOCK L18 (Self-evo 보고) |

### 3.3 스키마 간 관계 (SDAR_SPEC §8.4)

```
SDARDetectionSignal (Layer 1)
    │  signal_ref
    ▼
SDARDiagnosis (Layer 2)
    │  diagnosis_ref
    ▼
SDARRepairPlan (Layer 3)
    │  plan_ref
    ▼
SDARRepairResult (Layer 4)
    │  repair_result_ref
    ▼
SDARVerificationResult (Layer 5)  ← 본 파일
    │  보고
    ▼
S-8 Self-evo Governance (6-6 도메인)
```

---

## 4. 이벤트 (SDAR_SPEC §2.6 Layer 5)

### 4.1 이벤트 카탈로그

| # | 이벤트명 | 발생 시점 | 상태 전이 | 페이로드 |
|---|---------|----------|----------|---------|
| VE-1 | `oc.sdar.verification.started` | 검증 시작 (Step 5-1 진입) | S4→S5 | `{verification_id, repair_result_ref, trace_id, started_at}` |
| VE-2 | `oc.sdar.verification.passed` | 검증 통과 (PASS 판정) | S5→S6 | `{verification_id, verdict: "PASS", metrics_summary}` |
| VE-3 | `oc.sdar.verification.warned` | 경고 (WARN 판정, 부분적 문제) | S5→S6 | `{verification_id, verdict: "WARN", warnings, recommendations}` |
| VE-4 | `oc.sdar.verification.failed` | 검증 실패 (FAIL 판정) | S5→S4 (롤백) | `{verification_id, verdict: "FAIL", failure_reason, rollback_triggered}` |
| VE-5 | `oc.sdar.verification.rollback_executed` | 롤백 실행 완료 | - | `{verification_id, rollback_strategy, rollback_success, duration_ms}` |
| VE-6 | `oc.sdar.verification.completed` | 검증 프로세스 종료 | S6→S0 | `{verification_id, verdict, total_duration_ms, cooldown_s}` |

### 4.2 이벤트 발행 순서

```
정상 경로 (PASS):
  VE-1 (started) → [300초 관찰] → VE-2 (passed) → VE-6 (completed)

경고 경로 (WARN):
  VE-1 (started) → [300초 관찰] → VE-3 (warned) → VE-6 (completed)

실패+롤백 경로 (FAIL):
  VE-1 (started) → VE-4 (failed) → VE-5 (rollback_executed) → VE-6 (completed)

실패+롤백실패 경로 (ESCALATION):
  VE-1 (started) → VE-4 (failed) → SDAR_ROLLBACK_FAILED → Kill Switch ON (L14)
```

### 4.3 로깅 중첩 JSON

```json
{
  "event_type": "oc.sdar.verification.completed",
  "timestamp": "2026-04-13T10:35:00Z",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "verification_id": "ver_550e8400-e29b-41d4-a716-446655440010",
  "payload": {
    "repair_result_ref": "rep_550e8400-e29b-41d4-a716-446655440008",
    "verdict": "PASS",
    "post_condition_results": [
      {
        "condition": "error_rate < 0.01",
        "passed": true,
        "detail": "Current error rate: 0.002"
      },
      {
        "condition": "response_time_p99 < 500ms",
        "passed": true,
        "detail": "Current p99: 320ms"
      }
    ],
    "regression_check": {
      "passed": true,
      "metrics_before": {
        "avg_response_time": 450,
        "self_check_score": 0.82,
        "qod_score": 0.90,
        "error_rate": 0.05
      },
      "metrics_after": {
        "avg_response_time": 320,
        "self_check_score": 0.95,
        "qod_score": 0.93,
        "error_rate": 0.002
      },
      "new_errors": [],
      "observation_duration_s": 300
    },
    "rollback_triggered": false,
    "observation_period_s": 300,
    "recommendations": [],
    "notification": {
      "sent": true,
      "channel": "both"
    },
    "governance_summary": {
      "verification_verdict": "PASS",
      "rollback_executed": false,
      "observation_period_s": 300,
      "new_errors_count": 0
    }
  }
}
```

---

## 5. 에러 코드 카탈로그 (DH-2 등재)

### 5.1 Layer 5 에러 코드 목록

| 에러 코드 | 심각도 | 설명 | 트리거 조건 | 폴백 | 상태 전이 |
|----------|--------|------|-----------|------|----------|
| **VER-E001** | ERROR | 사후 조건 미충족 | Step 5-1: post_conditions 중 1개 이상 FAIL | 롤백 실행 | S5→S4 |
| **VER-E002** | ERROR | Health Check 하락 | Step 5-1: 수리 대상 모듈 Health Check score 하락 | 롤백 실행 | S5→S4 |
| **VER-E003** | ERROR | 원래 오류 재현 | Step 5-1: 수리 대상 오류가 재발생 | 롤백 실행 | S5→S4 |
| **VER-E004** | ERROR | 새로운 critical 오류 발생 | Step 5-2: 관찰 기간 내 error/critical 이벤트 감지 | 롤백 실행 | S5→S4 |
| **VER-E005** | ERROR | Self-check score 하락 | Step 5-2: Self-check score가 수리 전보다 하락 | 롤백 실행 | S5→S4 |
| **VER-E006** | WARN | 응답 시간 증가 | Step 5-2: 평균 응답 시간 수리 전 대비 20% 이상 증가 | WARN 판정, 관찰 지속 | S5→S6 (WARN) |
| **VER-E007** | WARN | QoD score 하락 | Step 5-2: QoD score 수리 전 대비 하락 | WARN 판정, 관찰 지속 | S5→S6 (WARN) |
| **VER-E008** | WARN | 에러율 소폭 증가 | Step 5-2: 에러율 증가 (error/critical 미만) | WARN 판정, 관찰 지속 | S5→S6 (WARN) |
| **VER-E009** | CRITICAL | 롤백 실패 — 스냅샷 누락 | Step 5-3: snapshot_id IS NULL (MEDIUM/HIGH risk) | 인간 에스컬레이션 | Kill Switch ON |
| **VER-E010** | CRITICAL | 롤백 타임아웃 | Step 5-3: 롤백 300초 초과 (LOCK L12) | 인간 에스컬레이션 + Kill Switch ON (LOCK L14) | Kill Switch ON |
| **VER-E011** | CRITICAL | 역동작 롤백 실패 | Step 5-3: reverse_actions 실행 중 단계 실패 | 인간 에스컬레이션 | Kill Switch ON |
| **VER-E012** | ERROR | 관찰 기간 타임아웃 | Step 5-2: S5 상태 타임아웃 300초 초과 (SDAR_SPEC §7.2) | 에스컬레이션 | S5→S6 (에스컬레이션) |

### 5.2 에러 코드 → 폴백 매핑

| 에러 코드 | FailureCode | FallbackAction |
|----------|------------|----------------|
| VER-E001~E005 | `SDAR_VERIFICATION_FAILED` | `FB_SDAR_SNAPSHOT_ROLLBACK` |
| VER-E006~E008 | (WARN — 폴백 불필요) | 관찰 지속 + 알림 |
| VER-E009~E011 | `SDAR_ROLLBACK_FAILED` | `FB_SDAR_MANUAL_ESCALATION` + Kill Switch ON |
| VER-E012 | `SDAR_VERIFICATION_TIMEOUT` | `FB_SDAR_MANUAL_ESCALATION` |

---

## 6. 에스컬레이션 페이로드

### 6.1 EscalationPayload 스키마

```python
class VerificationEscalationPayload(BaseModel):
    """Layer 5 검증 실패 에스컬레이션 페이로드"""
    escalation_id: str = Field(..., description="에스컬레이션 ID (UUID v4)")
    verification_id: str = Field(..., description="검증 ID")
    repair_result_ref: str = Field(..., description="수리 결과 참조")
    trace_id: str = Field(..., description="trace_id")
    escalated_at: str = Field(..., description="에스컬레이션 시각 (ISO8601 UTC)")

    # 에스컬레이션 사유
    error_code: str = Field(..., description="에러 코드 (VER-E001~E012)")
    severity: Literal["ERROR", "CRITICAL"] = Field(..., description="심각도")
    reason: str = Field(..., description="에스컬레이션 사유 상세")

    # 컨텍스트
    verdict: Literal["FAIL"] = Field(default="FAIL")
    rollback_attempted: bool = Field(..., description="롤백 시도 여부")
    rollback_success: Optional[bool] = Field(None, description="롤백 성공 여부")
    kill_switch_triggered: bool = Field(default=False, description="Kill Switch ON 여부")

    # 수리 컨텍스트
    original_error_category: str = Field(..., description="원래 오류 카테고리 (A~E)")
    original_error_code: str = Field(..., description="원래 오류 코드")
    ar_level_used: str = Field(..., description="수리에 사용된 AR-Level")

    # 권고
    recommended_actions: List[str] = Field(
        ..., description="권장 조치 목록"
    )

    model_config = ConfigDict(extra="forbid")
```

### 6.2 에스컬레이션 흐름

```
검증 FAIL → 롤백 시도
    │
    ├── 롤백 성공 → SDARVerificationResult(verdict=FAIL, rollback_triggered=True)
    │               → S5→S4→S5→S6 (재시도 1회 허용, 이후 에스컬레이션)
    │
    └── 롤백 실패 → VerificationEscalationPayload 생성
                  → SDAR_ROLLBACK_FAILED 이벤트 발행
                  → Kill Switch 자동 ON (LOCK L14)
                  → 인간 즉시 통보 (LOCK L9)
                  → S5→ESCALATED (S6_DONE 경유)
```

---

## 7. 복구 전략 + Penalty

### 7.1 Phase별 복구 흐름도

```
V1-Phase 0 (SDAR OFF, AR-L2):
  검증 FAIL → 수동 롤백 → 인간 확인 후 재시도
  Penalty: 최소 (수동 모드, 영향 범위 제한)

V2-Phase 1 (SDAR ON, AR-L3):
  검증 FAIL → 자동 롤백(스냅샷) → COOLDOWN 60초 → 재시도 1회 허용
  검증 FAIL 2회 연속 → 에스컬레이션
  Penalty: MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR(L6=3) 카운트 +1

V3-Phase 2 (SDAR ON 확장, AR-L4):
  검증 FAIL → 자동 롤백(스냅샷) → COOLDOWN 60초 → 재시도 1회 허용
  검증 FAIL 2회 연속 → 에스컬레이션 + SDAR_VERIFICATION_FAILED 이력 기록
  롤백 FAIL → Kill Switch ON (L14) + 인간 에스컬레이션
  Penalty: MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR(L6=3) 카운트 +1, 수리 성공률 메트릭 하락
```

### 7.2 Penalty 매트릭스

| 검증 결과 | 수리 성공률 영향 | L6 카운트 | 후속 제약 |
|----------|----------------|----------|----------|
| PASS | +1 성공 | +1 (총 1회) | 없음 (COOLDOWN 60초 후 다음 수리 가능) |
| WARN | +1 성공 (경고 첨부) | +1 | 후속 관찰 권고 (recommendations) |
| FAIL → 롤백 성공 | +1 실패 | +1 | 재시도 1회 허용, 이후 에스컬레이션 |
| FAIL → 롤백 실패 | +1 실패 (CRITICAL) | +1 | Kill Switch ON, 전체 SDAR 중단 |

---

## 8. 알고리즘 Big-O, LOCK, ABC 요약

### 8.1 알고리즘 복잡도

| 함수 | 시간복잡도 | 공간복잡도 | 비고 |
|------|----------|----------|------|
| `post_repair_validate` | O(C) | O(C) | C = post_conditions 수 (일반적으로 2~10) |
| `regression_check` | O(M * T) | O(M) | M = blast_radius modules, T = observation ticks (300초/10초=30) |
| `execute_rollback` | O(S) | O(1) | S = snapshot restore 단계 또는 reverse_steps 수 |
| `run_verification` (전체) | O(C + M*T + S) | O(M + C) | 전체 검증 프로세스 |

### 8.2 LOCK 참조 매핑

| LOCK # | 항목 | 값 | 적용 위치 |
|--------|------|-----|----------|
| **L1** | 5-Layer Pipeline 단계 정의 | Detection → ... → **Verification** | 파이프라인 최종 단계 |
| **L8** | SNAPSHOT_MANDATORY | MEDIUM/HIGH risk 수리 전 스냅샷 필수 | Step 5-3: 롤백 시 스냅샷 복원 |
| **L9** | NOTIFICATION_MANDATORY | 모든 수리 활동 알림 필수 | 전체: 검증 시작/완료/실패 알림 |
| **L11** | OBSERVATION_PERIOD | **300초** (5분 관찰) | Step 5-2: Regression Check 관찰 기간 |
| **L12** | ROLLBACK_TIMEOUT | **300초** (초과 시 인간 에스컬레이션) | Step 5-3: 롤백 실행 제한 시간 |
| **L13** | COOLDOWN_BETWEEN_REPAIRS | **60초** (동일 액션 반복 간 최소 대기) | 검증 완료 후 쿨다운 적용 |

### 8.3 ABC 패턴 (추상 기반 클래스)

```python
from abc import ABC, abstractmethod

class BaseVerifier(ABC):
    """Layer 5 검증 추상 기반 클래스"""

    @abstractmethod
    def validate_post_conditions(
        self, repair_result: SDARRepairResult, repair_plan: SDARRepairPlan
    ) -> PostRepairValidationResult:
        """Step 5-1: 사후 조건 검증"""
        ...

    @abstractmethod
    def check_regression(
        self, repair_result: SDARRepairResult, diagnosis: SDARDiagnosis,
        observation_period_s: int = 300
    ) -> RegressionCheckResult:
        """Step 5-2: 회귀 검사 (LOCK L11)"""
        ...

    @abstractmethod
    def execute_rollback(
        self, repair_result: SDARRepairResult, rollback_plan: SDARRollbackPlan,
        rollback_timeout_s: int = 300
    ) -> RollbackResult:
        """Step 5-3: 롤백 실행 (LOCK L12)"""
        ...

    def run_verification(
        self, repair_result: SDARRepairResult, repair_plan: SDARRepairPlan,
        diagnosis: SDARDiagnosis
    ) -> SDARVerificationResult:
        """전체 검증 오케스트레이터"""
        # 1. Post-Repair Validation
        validation = self.validate_post_conditions(repair_result, repair_plan)
        if not validation.passed:
            rollback = self.execute_rollback(
                repair_result, repair_plan.rollback_plan
            )
            return self._build_result(
                repair_result, validation, None, "FAIL", rollback
            )

        # 2. Regression Check (300초 관찰)
        regression = self.check_regression(
            repair_result, diagnosis, observation_period_s=300
        )

        if regression.verdict == "FAIL":
            rollback = self.execute_rollback(
                repair_result, repair_plan.rollback_plan
            )
            return self._build_result(
                repair_result, validation, regression, "FAIL", rollback
            )

        # 3. PASS or WARN
        verdict = regression.verdict  # "PASS" or "WARN"
        return self._build_result(
            repair_result, validation, regression, verdict, None
        )
```

---

## 9. 공통 자료 구조 선정의

### 9.1 Layer 5 사용 공통 자료 구조

| 자료 구조 | 용도 | 선정 근거 |
|----------|------|----------|
| `SDARVerificationResult` (Pydantic v2) | 검증 결과 출력 | SDAR_SPEC §2.6 정본 스키마, 5-Layer 출력 체인 최종 |
| `SDARRepairResult` (Layer 4 출력) | 검증 입력 | SDAR_SPEC §8.3 — repair_result_ref로 참조 |
| `SDARRepairPlan` (Layer 3 출력) | post_conditions, rollback_plan 참조 | SDAR_SPEC §8.2 — 사후 조건 + 롤백 계획 |
| `SDARDiagnosis` (Layer 2 출력) | impact.scope(영향 범위) 참조 | SDAR_SPEC §8.1 — blast_radius 모듈 목록 |
| `PostConditionResult` | 사후 조건 개별 결과 | DH-2 (Layer별 에러 코드 카탈로그의 하위 구조) |
| `RegressionCheckDetail` | 회귀 검사 상세 | DH-3 (SDAR 모니터링 메트릭 포함) |
| `RollbackDetail` | 롤백 실행 상세 | SDAR_SPEC §2.6 Step 5-3 |
| `VerificationEscalationPayload` | 에스컬레이션 데이터 | Layer 5 전용 에스컬레이션 (VER-E009~E011) |

### 9.2 DH-3 모니터링 메트릭 (Layer 5 관련)

| 메트릭 | 수집 주기 | 판정 기준 | 용도 |
|--------|----------|----------|------|
| `avg_response_time` | 10초 | 수리 전 대비 20% 이상 증가 → WARN | Regression Check |
| `self_check_score` | 10초 | 수리 전 대비 하락 → FAIL | Regression Check (롤백 트리거) |
| `qod_score` | 10초 | 수리 전 대비 하락 → WARN | Regression Check |
| `error_rate` | 10초 | error/critical 발생 → FAIL, 소폭 증가 → WARN | Regression Check |
| `verification_success_rate` | 수리 완료 시 | 성공/실패 비율 | DH-3 해결율 메트릭 |
| `avg_verification_duration_ms` | 수리 완료 시 | 평균 검증 소요 시간 | DH-3 평균 수리 시간 |
| `escalation_rate` | 수리 완료 시 | 에스컬레이션 비율 | DH-3 에스컬레이션 비율 |

---

## 10. 세션 간 인터페이스 Cross-check

### 10.1 입력 인터페이스 (Layer 4 → Layer 5)

| 인터페이스 | 출처 세션 | 스키마 | 검증 |
|-----------|----------|--------|------|
| `SDARRepairResult` | P1-4 (repair.md) | SDAR_SPEC §8.3 — result_id, trace_id, plan_ref, diagnosis_ref, overall_status, step_results, snapshot_id, rollback_triggered, governance_summary | **교차 확인 완료** — repair.md §4 스키마 정의와 일치 |
| `SDARRepairPlan` | P1-3 (prescription.md) | SDAR_SPEC §8.2 — post_conditions, rollback_plan | **교차 확인 완료** — 사후 조건 + 롤백 계획 참조 |
| `SDARDiagnosis` | P1-2 (diagnosis.md) | SDAR_SPEC §8.1 — impact.scope (blast_radius) | **교차 확인 완료** — 영향 범위 참조 |

### 10.2 출력 인터페이스 (Layer 5 → 후속)

| 인터페이스 | 소비자 | 스키마 | 용도 |
|-----------|--------|--------|------|
| `SDARVerificationResult` | S-8 Self-evo Governance (6-6 도메인) | 본 파일 §3.1 | 수리 결과 피드백 → Self-evo 학습 |
| `oc.sdar.verification.*` 이벤트 | 02_state-machine (상태 전이) | 본 파일 §4.1 | S5→S6 (PASS/WARN), S5→S4 (FAIL) |
| `VerificationEscalationPayload` | 인간 운영자 | 본 파일 §6.1 | 롤백 실패 시 긴급 에스컬레이션 |
| `SDAR_VERIFICATION_FAILED` | 6-12 Event-Logging (FallbackRegistry) | 본 파일 §5.2 | FB_SDAR_SNAPSHOT_ROLLBACK 매핑 |
| `SDAR_ROLLBACK_FAILED` | 6-12 Event-Logging + Kill Switch | 본 파일 §5.2 | FB_SDAR_MANUAL_ESCALATION + Kill Switch ON |

### 10.3 상태 전이 동기화 (02_state-machine 연동)

| Layer 5 이벤트 | 상태 전이 | 정본 | P1-6 state_transitions.md 참조 |
|---------------|----------|------|------|
| `oc.sdar.verification.started` | S4→S5 | SDAR_SPEC §7.3 | 예정 |
| `oc.sdar.verification.passed` | S5→S6 | SDAR_SPEC §7.3 | 예정 |
| `oc.sdar.verification.warned` | S5→S6 | SDAR_SPEC §7.3 | 예정 |
| `oc.sdar.verification.failed` | S5→S4 (롤백) | SDAR_SPEC §7.3 | 예정 |
| `oc.sdar.verification.completed` | S6→S0 | SDAR_SPEC §7.3 | 예정 |

---

## 11. 예외 처리 표

| # | 예외 상황 | 감지 방법 | 처리 | 에러 코드 | 상태 전이 |
|---|----------|----------|------|----------|----------|
| EX-1 | SDARRepairResult 수신 불가 | 입력 검증 | 에스컬레이션 (Layer 4 실패로 간주) | VER-E012 | S4→S5 전이 불가 → S4 유지 |
| EX-2 | post_conditions 전부 미충족 | Step 5-1 | 즉시 롤백 | VER-E001 | S5→S4 |
| EX-3 | Health Check 모듈 접근 불가 | Step 5-1 | WARN 판정 + 관찰 지속 | VER-E002 | S5 유지 |
| EX-4 | 관찰 기간 중 Kill Switch 발동 | 모든 단계 | 즉시 중단, S0 복귀 | (Kill Switch) | S5→S0 (L14) |
| EX-5 | 관찰 기간 중 시스템 재시작 | Step 5-2 | 관찰 중단, WARN 판정 | VER-E012 | S5→S6 (WARN) |
| EX-6 | 스냅샷 corruption | Step 5-3 | 수동 에스컬레이션 | VER-E009 | Kill Switch ON |
| EX-7 | 롤백 중 추가 오류 발생 | Step 5-3 | Kill Switch ON | VER-E011 | Kill Switch ON |
| EX-8 | COOLDOWN 위반 시도 | 검증 완료 후 | 실행 거부 + 대기 | (L13 차단) | S0 유지 (대기) |
| EX-9 | S5 상태 타임아웃 (300초) | SDAR_SPEC §7.2 | 에스컬레이션 | VER-E012 | S5→S6 |
| EX-10 | 동시 검증 인스턴스 충돌 | L7(MAX_CONCURRENT_SDAR=3) | 큐 대기 | (L7 차단) | S4 유지 (대기) |

---

## 12. Phase 2 테스트 케이스

### 12.1 검증 정상 경로 테스트

| # | 테스트 ID | 시나리오 | 입력 | 기대 결과 | LOCK 참조 |
|---|----------|---------|------|----------|----------|
| 1 | T-VER-001 | 검증 PASS — 전체 정상 | SDARRepairResult(overall_status=success), 모든 post_conditions 충족 | verdict=PASS, rollback_triggered=False | L11=300초 |
| 2 | T-VER-002 | 검증 WARN — 응답 시간 소폭 증가 | 수리 후 avg_response_time 25% 증가 | verdict=WARN, VER-E006 기록, recommendations 포함 | L11 |
| 3 | T-VER-003 | 검증 WARN — QoD score 소폭 하락 | 수리 후 qod_score 0.90 → 0.88 | verdict=WARN, VER-E007 기록 | L11 |

### 12.2 검증 실패 + 롤백 테스트

| # | 테스트 ID | 시나리오 | 입력 | 기대 결과 | LOCK 참조 |
|---|----------|---------|------|----------|----------|
| 4 | T-VER-004 | post_conditions 미충족 → 롤백 | post_conditions[0].passed=False | verdict=FAIL, rollback_triggered=True, VER-E001 | L8, L12 |
| 5 | T-VER-005 | Self-check score 하락 → 롤백 | self_check_score 하락 (관찰 60초 시점) | verdict=FAIL, 즉시 롤백, VER-E005 | L8, L11, L12 |
| 6 | T-VER-006 | 새로운 critical 오류 → 롤백 | 관찰 기간 내 CRITICAL 이벤트 발생 | verdict=FAIL, 즉시 롤백, VER-E004 | L11, L12 |
| 7 | T-VER-007 | LOW risk 역동작 롤백 성공 | risk_level=LOW, reverse_actions 전략 | rollback_result.strategy=reverse_actions, success=True | L12 |

### 12.3 롤백 실패 + 에스컬레이션 테스트

| # | 테스트 ID | 시나리오 | 입력 | 기대 결과 | LOCK 참조 |
|---|----------|---------|------|----------|----------|
| 8 | T-VER-008 | 스냅샷 누락 → 롤백 불가 | snapshot_id=None, risk_level=HIGH | VER-E009, Kill Switch ON, VerificationEscalationPayload 생성 | L8, L14 |
| 9 | T-VER-009 | 롤백 타임아웃 → Kill Switch | 롤백 300초 초과 | VER-E010, Kill Switch ON, 인간 에스컬레이션 | L12, L14 |
| 10 | T-VER-010 | 역동작 롤백 실패 | reverse_step 실행 중 오류 | VER-E011, Kill Switch ON | L14 |

### 12.4 운영 제한 테스트

| # | 테스트 ID | 시나리오 | 입력 | 기대 결과 | LOCK 참조 |
|---|----------|---------|------|----------|----------|
| 11 | T-VER-011 | COOLDOWN 60초 적용 확인 | 검증 완료 직후 동일 수리 재실행 시도 | 60초 대기 후 실행 허용 | L13 |
| 12 | T-VER-012 | Kill Switch 발동 중 검증 | 관찰 기간 중 Kill Switch ON | 즉시 중단, S5→S0, 검증 결과 미완료 | L14 |
| 13 | T-VER-013 | OBSERVATION_PERIOD 정확성 | 관찰 시작 후 정확히 300초 경과 | observation_duration_s=300 (±5초 허용) | L11 |

---

## 13. SelfCheckGate 연동 (SDAR_SPEC §6.1)

**SelfCheckGate**는 5-Gate 아키텍처의 5번째 Gate로, Layer 5에서 수리 후 품질을 최종 확인한다. (LOCK L3)

| Gate | 역할 | Layer 5 적용 |
|------|------|-------------|
| **SelfCheckGate** | 수리 후 Self-check 재실행하여 품질 확인 | Step 5-2 Regression Check에서 self_check_score 비교 |

> **Phase 2 상세**: SelfCheckGate의 구현 로직은 `04_self-diagnosis/gate_integration.md`에서 상세 정의 예정. Layer 5에서는 SelfCheckGate를 호출하여 결과를 받는 인터페이스만 정의.

---

## 14. LOCK 변경 및 CONFLICT 보고

### 14.1 LOCK 변경

본 세션(P1-5)에서 LOCK 값 변경은 없음. L1, L8, L9, L11, L12, L13 모두 참조만 수행.

### 14.2 CONFLICT 보고

본 세션(P1-5)에서 신규 CONFLICT 발견 없음.

- SDAR_SPEC §2.6 원문과 교차 검증 완료 — 3단계 검증 프로세스, SDARVerificationResult 스키마 일치
- SDAR_SPEC §7.2 S5_VERIFIED 타임아웃 300초 = LOCK L11(OBSERVATION_PERIOD=300초) 일치
- SDAR_SPEC §7.3 상태 전이(S4→S5, S5→S6, S5→S4) 일치
- SDAR_SPEC §9.2 운영 제한(L11, L12, L13) 일치

---

## 15. ISS-1 Layer 5 해결 확인

| 이슈 | 해결 항목 | 상태 |
|------|----------|------|
| ISS-1 Layer 5 | 3단계 검증 프로세스 상세 (Step 5-1, 5-2, 5-3) | **해결** |
| ISS-1 Layer 5 | SDARVerificationResult 출력 스키마 완전 정의 | **해결** |
| ISS-1 Layer 5 | OBSERVATION_PERIOD, ROLLBACK_TIMEOUT, COOLDOWN 명세 | **해결** |
| ISS-1 Layer 5 | 에러 코드 카탈로그 (VER-E001~E012) | **해결** |
| ISS-1 Layer 5 | 이벤트 카탈로그 (6건) | **해결** |
| ISS-1 Layer 5 | 롤백 절차 + 스냅샷 복원 (L8) | **해결** |

> **ISS-1 전체 상태**: Layer 1(P1-1), Layer 2(P1-2), Layer 3(P1-3), Layer 4(P1-4), Layer 5(P1-5, 본 파일) — **5/5 Layer 전체 해결 완료**
