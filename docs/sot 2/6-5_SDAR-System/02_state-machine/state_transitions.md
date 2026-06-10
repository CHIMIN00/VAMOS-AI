# State Transitions — 전이 매트릭스 14경로 상세

> **도메인**: 6-5_SDAR-System / 02_state-machine
> **Tier**: 6 (System-wide Components)
> **정본**: SDAR_SPEC **§7.1~§7.4** (7-State Machine 전이 정의)
> **Part2 출처**: §6.9 (L5422~L5438) — When/Where 정본
> **수정 정책**: Phase 변경 시 갱신 (종합계획서 §8.2)
> **LOCK 매핑**: L2 (7-State Machine 상태 전이 규칙), L7 (MAX_CONCURRENT_SDAR_INSTANCES=3), L14 (Kill Switch 트리거 조건), L15 (CATEGORY E 자동수리 절대 금지)
> **Phase**: P1-6
> **생성일**: 2026-04-13
> **ISS 해결**: ISS-3 (7-State 전이 예외 경로 매핑, 14경로 100% 커버)

---

## 교차 참조 블록

| 참조 대상 | 관계 |
|----------|------|
| **SDAR_SPEC §7.1~§7.4** | 7-State Machine 정의 정본 — 상태 정의(§7.1), 상태별 상세(§7.2), 전이 이벤트 매핑(§7.3), 동시 실행 제한(§7.4) |
| **SDAR_SPEC §9.2** | 운영 제한 — MAX_CONCURRENT_SDAR_INSTANCES=3 (L7) |
| **SDAR_SPEC §9.4** | Kill Switch — 트리거 조건, RBAC 전역 접근, SDAR_ROLLBACK_FAILED 시 자동 ON (L14) |
| **SDAR_SPEC §9.5** | CATEGORY E — 자동수리 절대 금지 5규칙 (L15) |
| **Part2 §6.9** | When/Where 정본 — Phase별 참조 범위, XREF-S6-05 상태명 매핑 |
| **종합계획서 부록 A.2** | 전이 조건 요약 10경로 (정상+실패 혼재) |
| **종합계획서 부록 A.3** | 예외 전이 4경로 (타임아웃, 5-Gate REJECT, Kill Switch) |
| **02_state-machine/_index.md** | P0 총괄 — 7-State 정의, 전이 매트릭스 개요 12경로+14경로, LOCK 참조 |
| **01_five-layer-pipeline/_index.md** | 5-Layer↔7-State 1:1 대응 (Layer 1=S1, Layer 2=S2, ..., Layer 5=S5) |
| **01_five-layer-pipeline/diagnosis.md** | DH-SDAR-T1=120초 Diagnosis 타임아웃 — 예외 전이 EX-02 조건 |
| **01_five-layer-pipeline/repair.md** | 수리 실행 상세 — S4 타임아웃(estimated_duration_s × 3), 롤백 절차 |
| **01_five-layer-pipeline/verification.md** | 검증 상세 — OBSERVATION_PERIOD=300초(L11), 롤백 트리거(L12) |
| **AUTHORITY_CHAIN.md §4** | LOCK L2, L7, L14, L15 레지스트리 |
| **CONFLICT_LOG.md** | XREF-01/02 등재 완료 — 본 파일 신규 CONFLICT 없음 |

---

## 1. 개요

본 문서는 SDAR 7-State Machine의 **전이 매트릭스를 14경로 100% 커버**로 정의한다. SDAR_SPEC §7.3의 12경로를 기반으로, 종합계획서 부록 A.2/A.3의 확장 경로를 통합하여 정상 9경로 + 예외 4경로 + Kill Switch 1경로 = 14경로로 전수 정의한다. (LOCK L2: IDLE → DETECTING → DIAGNOSING → PRESCRIBING → REPAIRING → VERIFYING → IDLE, 실패 시 ESCALATED)

### 1.1 핵심 요구사항

- 14경로 전수 정의: 정상 9 + 예외 4 + Kill Switch 1
- 각 전이별 트리거 이벤트, 가드 조건, 액션, 타임아웃 명세
- MAX_CONCURRENT_SDAR=3 (L7) 동시 실행 시 인스턴스 관리
- Kill Switch (L14) ANY→S0 즉시 전이 상세
- CATEGORY E (L15) S2→S6 즉시 전이 상세 (진단 중 CATEGORY E 식별 시)
- §4.3 R-65-4 (T-SDAR-05) 전이 완전성 검증 기준 충족

### 1.2 상태명 매핑 (SPEC 정식명 ↔ 편의 약칭)

| SPEC 정식 상태명 | 약칭 | 코드 | 5-Layer 대응 |
|-----------------|------|------|-------------|
| SDAR_S0_MONITORING | IDLE | S0 | — |
| SDAR_S1_DETECTED | DETECTING | S1 | Layer 1 |
| SDAR_S2_DIAGNOSED | DIAGNOSING | S2 | Layer 2 |
| SDAR_S3_PRESCRIBED | PRESCRIBING | S3 | Layer 3 |
| SDAR_S4_REPAIRING | REPAIRING | S4 | Layer 4 |
| SDAR_S5_VERIFIED | VERIFYING | S5 | Layer 5 |
| SDAR_S6_DONE | ESCALATED | S6 | — (종료) |

> **참고**: XREF-S6-05 — SPEC §7.1의 S6_DONE은 "전체 프로세스 완료"이며, ESCALATED는 S6_DONE의 하위 경로. 부록 A에서 편의상 7번째 상태로 별도 표기.

---

## 2. 전이 매트릭스 — 14경로 전수 테이블

### 2.1 정상 전이 9경로 (NORMAL)

| # | ID | From | To | 트리거 이벤트 | 가드 조건 | 액션 | 타임아웃 | SPEC 대응 |
|---|-----|------|----|-------------|----------|------|---------|----------|
| 1 | N-01 | S0 (IDLE) | S1 (DETECTING) | `oc.sdar.detection.signal_emitted` | severity >= "warn" | Detection Layer 활성화, SDAR 인스턴스 생성 | 없음 (이벤트 드리븐) | §7.3 #1 |
| 2 | N-02 | S1 (DETECTING) | S0 (IDLE) | `oc.sdar.detection.false_positive` | 오탐 판정 완료 | 오탐 로그 기록, FALSE_POSITIVE_COOLDOWN(300초) 적용 | — | §7.3 #3 |
| 3 | N-03 | S1 (DETECTING) | S2 (DIAGNOSING) | `oc.sdar.diagnosis.completed` | root_cause 특정 성공 | Diagnosis Layer 진입, SDARDiagnosis 인스턴스 생성 | S1 체류 30초 (§7.2) | §7.3 #2 |
| 4 | N-04 | S2 (DIAGNOSING) | S3 (PRESCRIBING) | `oc.sdar.prescription.plan_ready` | 수리 계획 수립 완료, CATEGORY != E | Prescription Layer 진입, SDARRepairPlan 생성 | S2 체류 60초 (§7.2) | §7.3 #4 |
| 5 | N-05 | S3 (PRESCRIBING) | S4 (REPAIRING) | `oc.sdar.repair.started` | AR-Level >= AR-L2 AND 수리 가능 AND 5-Gate 전체 PASS | Repair Layer 진입, 스냅샷 생성(L8, MEDIUM/HIGH risk) | S3 체류 30초 (§7.2) | §7.3 #6 |
| 6 | N-06 | S3 (PRESCRIBING) | S6 (DONE) | — (내부 전이) | AR-Level == AR-L0 또는 AR-L1 | 알림만 발송 후 완료 (L9 NOTIFICATION_MANDATORY), 수리 미실행 | — | §7.3 #7 |
| 7 | N-07 | S4 (REPAIRING) | S5 (VERIFYING) | `oc.sdar.repair.succeeded` / `.failed` | 수리 실행 완료 (성공/실패 무관) | Verification Layer 진입, OBSERVATION_PERIOD(300초, L11) 시작 | S4 체류 estimated_duration_s × 3 (§7.2) | §7.3 #9 |
| 8 | N-08 | S5 (VERIFYING) | S6 (DONE) | `oc.sdar.verification.passed` / `.warned` | 검증 통과 또는 경고(허용 범위) | 최종 결과 로그, 알림 발송(L9) | S5 체류 300초 (L11) | §7.3 #10 |
| 9 | N-09 | S6 (DONE) | S0 (IDLE) | `oc.sdar.verification.completed` | 프로세스 종료, 인간 개입 완료(에스컬레이션의 경우) | SDAR 인스턴스 정리, COOLDOWN(60초, L13) 시작 | S6 체류 10초 (§7.2) | §7.3 #12 |

### 2.2 예외 전이 4경로 (EXCEPTION)

| # | ID | From | To | 트리거 이벤트 | 가드 조건 | 액션 | 타임아웃 | SPEC/부록 대응 |
|---|-----|------|----|-------------|----------|------|---------|--------------|
| 10 | EX-01 | S1 (DETECTING) | S0 (IDLE) | 내부 타이머 만료 | Detection 타임아웃 30초 내 미완료 (§7.2 S1 timeout) | 현재 감지 작업 중단, 다음 주기로 이월, 로그 기록 | 30초 | 부록 A.3 #1, §7.3 #3 유사 |
| 11 | EX-02 | S2 (DIAGNOSING) | S6 (ESCALATED) | 내부 타이머 만료 | RCA 타임아웃 DH-SDAR-T1=120초 초과 | 인간 에스컬레이션 발행, EscalationPayload 전송, 진단 결과 부분 저장 | DH-SDAR-T1=120초 | 부록 A.3 #2, §7.3 #5 유사 |
| 12 | EX-03 | S3 (PRESCRIBING) | S6 (ESCALATED) | `oc.sdar.prescription.no_fix_available` 또는 5-Gate REJECT | (a) 수리 불가 판정 또는 (b) 5-Gate 중 하나라도 REJECT | 에스컬레이션 발행, 거부 사유 로그(Gate별), EscalationPayload 전송 | — | §7.3 #8 + 부록 A.3 #3 |
| 13 | EX-04 | S5 (VERIFYING) | S4 (REPAIRING) | `oc.sdar.verification.failed` | 검증 실패 → 롤백 필요 | 롤백 실행(L12 ROLLBACK_TIMEOUT=300초), 스냅샷 복원(L8), 재수리 시도 | — | §7.3 #11 |

> **EX-02 타임아웃 스코프 차이 주석**: SDAR_SPEC §7.2의 S2 상태 타임아웃=60초는 S2 상태 내 체류 시간 상한이며, DH-SDAR-T1=120초는 Diagnosis 프로세스 전체 허용 시간이다. 두 값은 스코프가 다르며 모순이 아닌 보완 관계에 있다. S2 체류 60초 시점에서 1차 경고를 발행하고, DH-SDAR-T1=120초에 최종 에스컬레이션이 트리거된다.

### 2.3 Kill Switch 전이 1경로 (KILL SWITCH)

| # | ID | From | To | 트리거 이벤트 | 가드 조건 | 액션 | 타임아웃 | SPEC/부록 대응 |
|---|-----|------|----|-------------|----------|------|---------|--------------|
| 14 | KS-01 | ANY (S0~S6) | S0 (IDLE) | `vamos:sdar:kill_switch` IPC 또는 UI 긴급 정지 버튼 | Kill Switch 활성화 (L14: 모든 RBAC 역할 접근 가능) 또는 SDAR_ROLLBACK_FAILED 자동 ON | 모든 진행 중 작업 즉시 중단, S4 진행 중이면 안전 롤백 시도(최대 ROLLBACK_TIMEOUT=300초), 모든 SDAR 인스턴스 S0 복귀, KillSwitchActivated 이벤트 발행 | 즉시 (응답 시간 < 1초) | 부록 A.3 #4, L14 |

### 2.4 14경로 합계 검증

| 유형 | 경로 수 | 경로 ID |
|------|--------|---------|
| 정상 (NORMAL) | 9 | N-01 ~ N-09 |
| 예외 (EXCEPTION) | 4 | EX-01 ~ EX-04 |
| Kill Switch | 1 | KS-01 |
| **합계** | **14** | — |

> **T-SDAR-05 완전성 확인**: 14경로 = 정상 9 + 예외 4 + Kill Switch 1. §4.3 R-65-4 전이 완전성 검증 기준 충족.

---

## 3. 각 전이 경로 상세

### 3.1 N-01: S0 → S1 (IDLE → DETECTING)

```
FUNCTION on_detection_signal(signal: SDARDetectionSignal):
    # 시간복잡도: O(1) — 단일 인스턴스 생성
    # ABC 패턴: BaseStateTransition(ABC).execute(from_state, to_state, context) → TransitionResult
    
    # 가드 조건 검사
    IF signal.severity < "warn":
        RETURN  # 무시, 상태 유지
    
    # 동시 실행 제한 검사 (L7)
    IF active_sdar_instances.count >= MAX_CONCURRENT_SDAR_INSTANCES:  # L7 = 3
        queue_signal(signal)
        RETURN  # 큐잉, 상태 유지
    
    # 동일 failure_code 중복 검사 (§7.4)
    IF active_sdar_instances.has(failure_code=signal.failure_code):
        LOG("duplicate SDAR for failure_code={}", signal.failure_code)
        RETURN  # 중복 방지
    
    # 전이 실행
    instance = SDARInstance.create(signal)
    instance.state = S1_DETECTING
    instance.start_timer(timeout=30)  # §7.2 S1 타임아웃
    EMIT "oc.sdar.detection.signal_emitted"
    NOTIFY(signal)  # L9 NOTIFICATION_MANDATORY
```

**실패 시 fallback**: 인스턴스 생성 실패 → 신호를 큐에 적재, 다음 Detection 주기에 재시도.

### 3.2 N-02: S1 → S0 (DETECTING → IDLE) — 오탐

```
FUNCTION on_false_positive(instance: SDARInstance, reason: str):
    # 시간복잡도: O(1)
    
    instance.cancel_timer()
    instance.state = S0_IDLE
    instance.result = "false_positive"
    
    EMIT "oc.sdar.detection.false_positive"
    LOG(level="INFO", code=null, reason=reason)
    
    # 오탐 쿨다운 적용
    cooldown_registry.add(
        source=instance.signal.source_module,
        duration=FALSE_POSITIVE_COOLDOWN  # 300초
    )
    
    instance.destroy()
```

**실패 시 fallback**: 인스턴스 정리 실패 → 강제 종료 후 로그 기록.

### 3.3 N-03: S1 → S2 (DETECTING → DIAGNOSING)

```
FUNCTION on_detection_confirmed(instance: SDARInstance, signal: SDARDetectionSignal):
    # 시간복잡도: O(1) — 상태 전이 + Diagnosis 인스턴스 생성
    
    instance.cancel_timer()  # S1 타이머 해제
    instance.state = S2_DIAGNOSING
    instance.start_timer(timeout=60)   # §7.2 S2 상태 타임아웃
    instance.start_timer(timeout=120)  # DH-SDAR-T1 프로세스 타임아웃 (별도)
    
    diagnosis = SDARDiagnosis.create(signal)
    EMIT "oc.sdar.diagnosis.started"  # → Layer 2 진입 (RCA/분류 완료는 N-04에서 oc.sdar.diagnosis.completed 발행)
```

**실패 시 fallback**: Diagnosis 인스턴스 생성 실패 → EX-01 경로로 S0 복귀, 다음 주기 재시도.

### 3.4 N-04: S2 → S3 (DIAGNOSING → PRESCRIBING)

```
FUNCTION on_diagnosis_completed(instance: SDARInstance, diagnosis: SDARDiagnosis):
    # 시간복잡도: O(1)
    
    # CATEGORY E 검사 (L15)
    IF diagnosis.error_category == "E":
        # CATEGORY E → 즉시 에스컬레이션 (L15 5규칙 적용)
        trigger_category_e_escalation(instance, diagnosis)
        RETURN  # N-04 중단, S2→S6 즉시 전이로 처리
    
    instance.cancel_timer()  # S2 타이머 해제
    instance.state = S3_PRESCRIBING
    instance.start_timer(timeout=30)  # §7.2 S3 타임아웃
    
    EMIT "oc.sdar.prescription.plan_ready"  # → Layer 3 진입
```

**실패 시 fallback**: Prescription 생성 실패 → EX-03 경로로 에스컬레이션.

### 3.5 N-05: S3 → S4 (PRESCRIBING → REPAIRING)

```
FUNCTION on_prescription_approved(instance: SDARInstance, plan: SDARRepairPlan):
    # 시간복잡도: O(g) where g = Gate 수 (현재 5)
    # ABC 패턴: BaseGate(ABC).check(context) → GateResult (L20)
    
    # 5-Gate 검증
    FOR each gate IN [PolicyGate, EvidenceGate, CostGate, ApprovalGate]:  # SelfCheckGate는 Layer 5(검증)에서만 적용 (gate_integration.md §3.1)
        result = gate.check(plan.context)
        IF result.status IN ["deny", "stop", "insufficient", "denied"]:
            trigger_escalation(instance, gate, result)  # EX-03
            RETURN
    
    # AR-Level 검사
    IF plan.ar_level < AR_L2:
        # AR-L0/L1 → N-06 (알림만)
        trigger_notify_only(instance, plan)
        RETURN
    
    # 동시 수리 검사 (L5)
    IF active_repairs.count >= MAX_CONCURRENT_REPAIRS:  # L5 = 1
        queue_repair(instance)
        RETURN
    
    # 스냅샷 생성 (L8 — MEDIUM/HIGH risk)
    IF plan.risk_level IN ["MEDIUM", "HIGH"]:
        snapshot = create_snapshot(instance)  # L8 SNAPSHOT_MANDATORY
    
    instance.cancel_timer()
    instance.state = S4_REPAIRING
    timeout = plan.estimated_duration_s * 3  # §7.2 S4 타임아웃
    instance.start_timer(timeout=timeout)
    
    EMIT "oc.sdar.repair.started"
    NOTIFY(plan)  # L9 NOTIFICATION_MANDATORY
```

**실패 시 fallback**: 스냅샷 생성 실패 → 수리 진행 불가, EX-03 에스컬레이션.

### 3.6 N-06: S3 → S6 (PRESCRIBING → DONE) — AR-L0/L1

```
FUNCTION on_notify_only(instance: SDARInstance, plan: SDARRepairPlan):
    # AR-L0 (모니터링만) 또는 AR-L1 (알림+제안)
    instance.cancel_timer()
    instance.state = S6_DONE
    instance.result = "notify_only"
    
    NOTIFY(plan)  # L9
    LOG(level="INFO", ar_level=plan.ar_level, action="notify_only")
    
    # S6 → S0 자동 전이 (10초 후)
    instance.start_timer(timeout=10)  # §7.2 S6 타임아웃
```

### 3.7 N-07: S4 → S5 (REPAIRING → VERIFYING)

```
FUNCTION on_repair_completed(instance: SDARInstance, result: SDARRepairResult):
    # 시간복잡도: O(1)
    
    instance.cancel_timer()  # S4 타이머 해제
    instance.state = S5_VERIFYING
    instance.start_timer(timeout=300)  # L11 OBSERVATION_PERIOD
    
    IF result.status == "succeeded":
        EMIT "oc.sdar.repair.succeeded"
    ELSE:
        EMIT "oc.sdar.repair.failed"
    
    # Verification Layer 진입
    verification = SDARVerification.create(instance, result)
```

### 3.8 N-08: S5 → S6 (VERIFYING → DONE) — 검증 통과

```
FUNCTION on_verification_passed(instance: SDARInstance, verification: SDARVerificationResult):
    # 시간복잡도: O(1)
    
    instance.cancel_timer()  # S5 타이머 해제
    instance.state = S6_DONE
    
    IF verification.status == "passed":
        EMIT "oc.sdar.verification.passed"
    ELIF verification.status == "warned":
        EMIT "oc.sdar.verification.warned"
    
    instance.result = verification.status
    NOTIFY(verification)  # L9
    instance.start_timer(timeout=10)  # §7.2 S6 타임아웃
```

### 3.9 N-09: S6 → S0 (DONE → IDLE)

```
FUNCTION on_process_completed(instance: SDARInstance):
    # 시간복잡도: O(1)
    
    instance.cancel_timer()
    instance.state = S0_IDLE
    
    EMIT "oc.sdar.verification.completed"
    
    # 쿨다운 적용 (L13)
    cooldown_registry.add(
        action=instance.last_repair_action,
        duration=COOLDOWN_BETWEEN_REPAIRS  # L13 = 60초
    )
    
    # 인스턴스 정리
    instance.destroy()
    
    # 큐에 대기 중인 신호가 있으면 다음 SDAR 시작
    IF signal_queue.has_pending():
        next_signal = signal_queue.dequeue()
        on_detection_signal(next_signal)  # N-01 재진입
```

### 3.10 EX-01: S1 → S0 (DETECTING → IDLE) — Detection 타임아웃

```
FUNCTION on_detection_timeout(instance: SDARInstance):
    # S1 체류 30초 초과
    # 시간복잡도: O(1)
    
    instance.state = S0_IDLE
    instance.result = "detection_timeout"
    
    LOG(level="WARN", code="DET-E006", message="Detection timeout, deferring to next cycle")
    
    # 다음 Detection 주기에 자동 이월
    deferred_signals.add(instance.original_signal)
    
    instance.destroy()
```

### 3.11 EX-02: S2 → S6 (DIAGNOSING → ESCALATED) — RCA 타임아웃

```
FUNCTION on_diagnosis_timeout(instance: SDARInstance):
    # DH-SDAR-T1 = 120초 초과 (프로세스 레벨)
    # 또는 S2 상태 타임아웃 60초 초과 (상태 레벨 — 1차 경고)
    # 시간복잡도: O(1)
    
    instance.state = S6_DONE
    instance.result = "diagnosis_timeout_escalated"
    
    # 부분 진단 결과 저장
    partial_diagnosis = instance.diagnosis.get_partial_result()
    
    # 에스컬레이션 발행
    escalation = EscalationPayload(
        type="DIAGNOSIS_TIMEOUT",
        sdar_id=instance.id,
        timeout_value=120,
        partial_diagnosis=partial_diagnosis,
        human_action_required="manual_root_cause_analysis",
        urgency="HIGH"
    )
    EMIT_ESCALATION(escalation)
    NOTIFY(escalation)  # L9
    
    instance.start_timer(timeout=10)  # S6 타임아웃
```

### 3.12 EX-03: S3 → S6 (PRESCRIBING → ESCALATED)

```
FUNCTION on_prescription_rejected(instance: SDARInstance, reason: str, gate: Optional[str]):
    # (a) no_fix_available 또는 (b) 5-Gate REJECT
    # 시간복잡도: O(1)
    
    instance.cancel_timer()
    instance.state = S6_ESCALATED
    instance.result = "prescription_rejected_escalated"
    
    IF reason == "no_fix_available":
        EMIT "oc.sdar.prescription.no_fix_available"
    
    escalation = EscalationPayload(
        type="PRESCRIPTION_REJECTED",
        sdar_id=instance.id,
        rejection_reason=reason,
        rejected_gate=gate,
        repair_plan=instance.repair_plan,
        human_action_required="manual_repair_or_override",
        urgency="MEDIUM"
    )
    EMIT_ESCALATION(escalation)
    NOTIFY(escalation)  # L9
    
    instance.start_timer(timeout=10)  # S6 타임아웃
```

### 3.13 EX-04: S5 → S4 (VERIFYING → REPAIRING) — 롤백

```
FUNCTION on_verification_failed(instance: SDARInstance, verification: SDARVerificationResult):
    # 검증 실패 → 롤백 + 재수리
    # 시간복잡도: O(r) where r = 롤백 대상 액션 수
    
    instance.cancel_timer()  # S5 타이머 해제
    
    EMIT "oc.sdar.verification.failed"
    
    # 롤백 실행 (L12 ROLLBACK_TIMEOUT = 300초)
    rollback_timer = start_timer(timeout=300)  # L12
    rollback_result = execute_rollback(
        snapshot=instance.snapshot,  # L8 스냅샷 복원
        actions=instance.repair_actions
    )
    
    IF rollback_result.status == "failed":
        # 롤백 실패 → Kill Switch 자동 활성화 (L14: SDAR_ROLLBACK_FAILED → 자동 ON)
        trigger_kill_switch(instance, reason="SDAR_ROLLBACK_FAILED")
        RETURN  # KS-01 경로로 전이
    
    # 재수리 시도 제한 확인 (L6: MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR = 3)
    IF instance.repair_attempt_count >= MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR:
        # 재시도 소진 → 에스컬레이션
        trigger_escalation(instance, reason="MAX_RETRIES_EXHAUSTED")
        RETURN  # S6으로 전이
    
    # S4 재진입
    instance.state = S4_REPAIRING
    instance.repair_attempt_count += 1
    instance.start_timer(timeout=instance.repair_plan.estimated_duration_s * 3)
    
    EMIT "oc.sdar.repair.started"
    NOTIFY(instance.repair_plan)  # L9
```

### 3.14 KS-01: ANY → S0 (Kill Switch)

```
FUNCTION on_kill_switch_activated(trigger: KillSwitchTrigger):
    # 시간복잡도: O(n) where n = 활성 SDAR 인스턴스 수 (최대 3, L7)
    # 응답 시간 요건: < 1초
    
    # Kill Switch 활성화 이벤트 발행
    EMIT KillSwitchActivated(
        trigger_source=trigger.source,  # "ipc" | "ui" | "auto_rollback_failed"
        trigger_user=trigger.user,
        trigger_rbac_role=trigger.rbac_role,
        timestamp=now()
    )
    
    # 모든 활성 인스턴스 즉시 중단
    FOR each instance IN active_sdar_instances:
        instance.cancel_all_timers()
        
        IF instance.state == S4_REPAIRING:
            # 수리 중이면 안전 롤백 시도
            rollback_result = safe_rollback(
                instance,
                timeout=ROLLBACK_TIMEOUT  # L12 = 300초
            )
            IF rollback_result.status == "failed":
                LOG(level="CRITICAL", code="KS-E001",
                    message="Kill Switch rollback failed, manual intervention required")
                EMIT_ESCALATION(EscalationPayload(
                    type="KILL_SWITCH_ROLLBACK_FAILED",
                    sdar_id=instance.id,
                    urgency="CRITICAL"
                ))
        
        instance.state = S0_IDLE
        instance.result = "kill_switch_terminated"
        instance.destroy()
    
    # 전역 상태 설정
    sdar_enabled = FALSE
    LOG(level="CRITICAL", code="KS-E000", message="Kill Switch activated — all SDAR stopped")
    NOTIFY_ALL(trigger)  # L9 — 모든 역할에 알림
```

---

## 4. CATEGORY E 즉시 전이 (L15)

CATEGORY E(보안 오류) 감지 시 정상 경로를 무시하고 즉시 에스컬레이션 전이가 발생한다.

### 4.1 전이 경로: S2 → S6 (DIAGNOSING → ESCALATED)

```
FUNCTION trigger_category_e_escalation(instance: SDARInstance, diagnosis: SDARDiagnosis):
    # L15 5규칙 적용
    # 시간복잡도: O(1)
    
    # 규칙 1: 자동수리 절대 금지
    instance.auto_repair_allowed = FALSE
    
    # 규칙 2: 즉시 차단 — S2 → S6 직접 전이 (S3~S5 스킵)
    instance.cancel_all_timers()
    instance.state = S6_ESCALATED
    instance.result = "category_e_escalated"
    
    # 규칙 3: 감사 로그 강제 (CRITICAL, 삭제 불가)
    LOG(level="CRITICAL", code="CAT-E-001",
        message="CATEGORY E detected — security violation",
        immutable=TRUE,  # 삭제 불가
        category=diagnosis.category,
        detail=diagnosis.root_cause)
    
    # 규칙 4: 인간 알림 필수 — 보안팀 즉시 통보
    escalation = EscalationPayload(
        type="CATEGORY_E_SECURITY_VIOLATION",
        sdar_id=instance.id,
        category="E",
        diagnosis=diagnosis,
        human_action_required="security_team_immediate_review",
        urgency="CRITICAL",
        auto_repair_blocked=TRUE,
        forensic_retention_days=30
    )
    EMIT_ESCALATION(escalation)
    NOTIFY_SECURITY_TEAM(escalation)
    
    # 규칙 5: 포렌식 데이터 30일 보존
    forensic_data = collect_forensic_data(instance, diagnosis)
    store_forensic(forensic_data, retention_days=30)
    
    instance.start_timer(timeout=10)  # S6 타임아웃 (인간 개입 대기)
```

### 4.2 CATEGORY E 판정 기준

| 조건 | 예시 | 판정 |
|------|------|------|
| 보안 규칙 위반 감지 | 인증 우회, 권한 상승 시도 | CATEGORY E |
| 감사 로그 변조 시도 | audit_format 불변구역 변경 | CATEGORY E (L19 NEVER_AUTO) |
| guardrails 비활성화 시도 | disable_guardrails | CATEGORY E (L19 NEVER_AUTO) |
| Gate 우회 시도 | bypass_gate | CATEGORY E (L19 NEVER_AUTO) |

---

## 5. MAX_CONCURRENT_SDAR 인스턴스 관리 (L7)

### 5.1 동시 실행 제한 구조

```
FUNCTION sdar_instance_manager():
    # L7: MAX_CONCURRENT_SDAR_INSTANCES = 3
    # L5: MAX_CONCURRENT_REPAIRS = 1 (S4 상태 직렬화)
    # §7.4: 동일 failure_code 병렬 SDAR = 1
    # 시간복잡도: O(n) where n = 큐 크기 (최대 제한 100)
    
    active_instances: List[SDARInstance]  # max_size = 3 (L7)
    repair_slot: Optional[SDARInstance]   # max_size = 1 (L5)
    signal_queue: PriorityQueue           # severity 기반 우선순위
    
    INVARIANT: len(active_instances) <= 3      # L7
    INVARIANT: len(repair_slot) <= 1           # L5
    INVARIANT: no duplicate failure_code       # §7.4
```

### 5.2 인스턴스 배정 알고리즘

```
FUNCTION allocate_instance(signal: SDARDetectionSignal) -> Optional[SDARInstance]:
    # 시간복잡도: O(n) where n = active_instances.count (최대 3)
    
    # 1. 동일 failure_code 중복 검사
    IF any(i.failure_code == signal.failure_code FOR i IN active_instances):
        RETURN None  # 중복 방지
    
    # 2. 슬롯 가용성 검사
    IF len(active_instances) >= MAX_CONCURRENT_SDAR_INSTANCES:
        # 큐잉
        signal_queue.enqueue(signal, priority=severity_to_int(signal.severity))
        RETURN None
    
    # 3. 인스턴스 생성
    instance = SDARInstance.create(signal)
    active_instances.add(instance)
    RETURN instance
```

### 5.3 인스턴스 해제 및 큐 소비

```
FUNCTION release_instance(instance: SDARInstance):
    # 시간복잡도: O(1) amortized
    
    active_instances.remove(instance)
    
    # 쿨다운 적용 (L13 = 60초)
    IF instance.last_repair_action:
        cooldown_registry.add(instance.last_repair_action, COOLDOWN_BETWEEN_REPAIRS)
    
    # 큐에서 다음 신호 소비
    IF signal_queue.has_pending():
        next_signal = signal_queue.dequeue()
        allocate_instance(next_signal)
```

---

## 6. 상태 전이 시퀀스 예시

### 6.1 정상 전이 시퀀스 (전체 파이프라인 성공)

```
시나리오: DB 커넥션 latency 3000ms 감지 → 진단 → 수리 → 검증 통과

시간     상태 전이              이벤트                           비고
─────────────────────────────────────────────────────────────────────────────
T+0s     S0 → S1 (N-01)       oc.sdar.detection.signal_emitted  severity=critical
T+2s     S1 → S2 (N-03)       oc.sdar.diagnosis.completed       root_cause=db_connection_pool_exhausted
T+15s    S2 → S3 (N-04)       oc.sdar.prescription.plan_ready   category=B, AR-L2
T+18s    S3 → S4 (N-05)       oc.sdar.repair.started            5-Gate PASS, snapshot 생성
T+25s    S4 → S5 (N-07)       oc.sdar.repair.succeeded          connection pool 재설정 완료
T+325s   S5 → S6 (N-08)       oc.sdar.verification.passed       300초 관찰 PASS
T+335s   S6 → S0 (N-09)       oc.sdar.verification.completed    COOLDOWN 60초 시작
```

### 6.2 에러 전이 시퀀스 (RCA 타임아웃 → 에스컬레이션)

```
시나리오: 알 수 없는 오류 패턴 감지 → 진단 실패 → 인간 에스컬레이션

시간     상태 전이              이벤트                           비고
─────────────────────────────────────────────────────────────────────────────
T+0s     S0 → S1 (N-01)       oc.sdar.detection.signal_emitted  severity=error, channel=error_pattern
T+3s     S1 → S2 (N-03)       oc.sdar.diagnosis.completed       RCA 시작
T+60s    — (1차 경고)         —                                  S2 상태 타임아웃 60초 도달, WARN 로그
T+120s   S2 → S6 (EX-02)     (타이머 만료)                       DH-SDAR-T1=120초 초과
         —                    EscalationPayload 전송              type=DIAGNOSIS_TIMEOUT, urgency=HIGH
T+130s   S6 → S0 (N-09)      oc.sdar.verification.completed     인간 개입 후 복귀
```

### 6.3 Kill Switch 시퀀스 (수리 중 긴급 정지)

```
시나리오: 수리 실행 중 운영자가 UI 긴급 정지 버튼 클릭

시간     상태 전이              이벤트                           비고
─────────────────────────────────────────────────────────────────────────────
T+0s     S0 → S1 (N-01)       oc.sdar.detection.signal_emitted  severity=critical
T+3s     S1 → S2 (N-03)       oc.sdar.diagnosis.completed       root_cause 특정
T+10s    S2 → S3 (N-04)       oc.sdar.prescription.plan_ready   AR-L3, MEDIUM risk
T+12s    S3 → S4 (N-05)       oc.sdar.repair.started            snapshot 생성 완료
T+20s    S4 → S0 (KS-01)     KillSwitchActivated               trigger=ui, user=operator
         —                    safe_rollback 시작                  snapshot 복원 시도
T+25s    —                    safe_rollback 완료                  수리 액션 롤백 성공
         —                    sdar_enabled=FALSE                  모든 SDAR 중단
         —                    NOTIFY_ALL                          전체 운영팀 알림 (L9)
```

---

## 7. 일관성 검증

### 7.1 SPEC §7.3 12경로 ↔ 14경로 매핑 검증

| SPEC §7.3 경로 # | 14경로 ID | 매핑 상태 |
|------------------|----------|----------|
| #1 (S0→S1) | N-01 | MAPPED |
| #2 (S1→S2) | N-03 | MAPPED |
| #3 (S1→S0) | N-02 | MAPPED |
| #4 (S2→S3) | N-04 | MAPPED |
| #5 (S2→S0) | EX-02 변형 (S2→S6, 부록 A 해석) | MAPPED (스코프 차이: SPEC은 S0 복귀, 부록 A는 S6 에스컬레이션) |
| #6 (S3→S4) | N-05 | MAPPED |
| #7 (S3→S6, AR-L0/L1) | N-06 | MAPPED |
| #8 (S3→S6, no_fix) | EX-03 | MAPPED |
| #9 (S4→S5) | N-07 | MAPPED |
| #10 (S5→S6) | N-08 | MAPPED |
| #11 (S5→S4) | EX-04 | MAPPED |
| #12 (S6→S0) | N-09 | MAPPED |
| — (부록 A.3 Detection timeout) | EX-01 | 추가 (부록 A.3 자체 정의) |
| — (부록 A.3 Kill Switch) | KS-01 | 추가 (L14 §9.4 참조) |

> **검증 결과**: SPEC §7.3 12경로 전수 매핑 + 부록 A.3 추가 2경로 = 14경로 100% 커버 확인.

### 7.2 상태별 진입/종료 경로 완전성

| 상태 | 진입 경로 | 종료 경로 | 완전성 |
|------|----------|----------|--------|
| S0 (IDLE) | N-02, N-09, EX-01, KS-01 | N-01 | 4 진입 / 1 종료 |
| S1 (DETECTING) | N-01 | N-02, N-03, EX-01 | 1 진입 / 3 종료 |
| S2 (DIAGNOSING) | N-03 | N-04, EX-02, §4 CATEGORY E(S2→S6) | 1 진입 / 3 종료 |
| S3 (PRESCRIBING) | N-04 | N-05, N-06, EX-03 | 1 진입 / 3 종료 |
| S4 (REPAIRING) | N-05, EX-04 | N-07 | 2 진입 / 1 종료 |
| S5 (VERIFYING) | N-07 | N-08, EX-04 | 1 진입 / 2 종료 |
| S6 (DONE/ESCALATED) | N-06, N-08, EX-02, EX-03 | N-09 | 4 진입 / 1 종료 |

> **데드락 없음**: 모든 상태에 1개 이상의 종료 경로 존재.
> **고립 상태 없음**: 모든 상태에 1개 이상의 진입 경로 존재.
> **KS-01은 모든 상태에서 S0으로 전이 가능** — 데드락 최종 안전망.

---

## 8. 에스컬레이션 페이로드 구조

### 8.1 EscalationPayload 스키마

```python
class EscalationPayload(BaseModel):
    """SDAR 에스컬레이션 페이로드 — 인간 개입 요청 시 발행"""
    
    # 식별
    escalation_id: str           # UUID v4
    sdar_id: str                 # 원본 SDAR 인스턴스 ID
    trace_id: str                # 추적 ID
    
    # 유형
    type: Literal[
        "DIAGNOSIS_TIMEOUT",                # EX-02
        "PRESCRIPTION_REJECTED",            # EX-03 (no_fix / 5-Gate REJECT)
        "CATEGORY_E_SECURITY_VIOLATION",    # L15
        "KILL_SWITCH_ROLLBACK_FAILED",      # KS-01 롤백 실패
        "MAX_RETRIES_EXHAUSTED"             # EX-04 재시도 소진
    ]
    
    # 컨텍스트
    from_state: str              # 에스컬레이션 발생 상태
    to_state: str = "S6"         # 항상 S6 (ESCALATED)
    
    # 상세
    rejection_reason: Optional[str] = None
    rejected_gate: Optional[str] = None
    partial_diagnosis: Optional[dict] = None
    repair_plan: Optional[dict] = None
    
    # 요청
    human_action_required: str   # 필요한 인간 작업 설명
    urgency: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    
    # 보안 (CATEGORY E 전용)
    auto_repair_blocked: bool = False
    forensic_retention_days: Optional[int] = None
    
    # 타임스탬프
    escalated_at: str            # ISO8601 UTC
```

---

## 9. 예외 처리 표

| 에러 코드 | 상태 전이 | 발생 조건 | 처리 방법 | 복구 가능 | 영향 범위 |
|----------|----------|----------|----------|----------|----------|
| ST-E001 | N-01 실패 | 인스턴스 생성 실패 (메모리 부족) | 신호 큐잉, 다음 주기 재시도 | 예 | 단일 SDAR |
| ST-E002 | N-03 실패 | Diagnosis 인스턴스 생성 실패 | EX-01 경로 (S0 복귀), 로그 기록 | 예 | 단일 SDAR |
| ST-E003 | N-05 실패 | 스냅샷 생성 실패 (L8) | EX-03 경로 (에스컬레이션) | 아니오 | 단일 SDAR |
| ST-E004 | EX-04 실패 | 롤백 실패 | KS-01 자동 Kill Switch 활성화 (L14) | 아니오 | 전체 SDAR |
| ST-E005 | KS-01 실패 | Kill Switch 롤백 실패 | CRITICAL 에스컬레이션, 인간 즉시 개입 | 아니오 | 전체 시스템 |
| ST-E006 | N-01 실패 | 동시 인스턴스 초과 (L7=3) | 큐잉, 슬롯 해제 시 자동 재시도 | 예 | 단일 신호 |
| ST-E007 | N-05 실패 | 동시 수리 초과 (L5=1) | 수리 큐잉, 수리 슬롯 해제 시 재시도 | 예 | 단일 SDAR |
| ST-E008 | EX-04 | 재시도 횟수 초과 (L6=3) | 에스컬레이션 (S6) | 아니오 | 단일 SDAR |
| ST-E009 | 전이 타이머 | 타이머 생성/관리 실패 | 즉시 타임아웃 처리 (안전 실패) | 예 | 단일 SDAR |
| ST-E010 | 이벤트 발행 | 이벤트 버스 장애 | 로컬 로그 + 재시도(최대 3회) | 예 | 단일 이벤트 |

---

## 10. Phase별 복구 전략

### 10.1 복구 흐름도

```
Phase 1 (현재) — 전이 매트릭스 복구
  ├── ST-E001~E003: 자동 재시도 / 큐잉 / 에스컬레이션
  ├── ST-E004: Kill Switch 자동 활성화 (L14)
  ├── ST-E006~E007: 큐잉 기반 자동 재시도
  └── 실패 시 → 에스컬레이션 (S6)

Phase 2 — 상태 머신 고급 복구
  ├── 전이 경로 통계 기반 이상 패턴 감지
  ├── 반복 에스컬레이션 경로 자동 분석
  └── 인스턴스 우선순위 동적 조정

Phase 3 — 전체 Pipeline 통합 복구
  ├── Layer 5 검증 결과 → 전이 매트릭스 가중치 피드백
  ├── 에스컬레이션 이력 기반 자동 경로 최적화
  └── 멀티 인스턴스 부하 분산 최적화

Phase 4 — 거버넌스 완성
  ├── 전이 경로별 성공률 KPI 자동 보고
  └── 상태 체류 시간 감사 로그
```

### 10.2 다운그레이드 시 confidence penalty 표

| 다운그레이드 상황 | 영향받는 전이 | confidence 감소 | 비고 |
|-----------------|-------------|----------------|------|
| 이벤트 버스 장애 (ST-E010) | 모든 전이 | -25% | 이벤트 발행 지연/누락 가능 |
| 타이머 관리 실패 (ST-E009) | 타임아웃 전이 (EX-01, EX-02) | -30% | 즉시 타임아웃 처리로 과잉 에스컬레이션 |
| 인스턴스 초과 큐잉 (ST-E006) | N-01 | -15% | 감지→처리 지연 |
| 스냅샷 실패 (ST-E003) | N-05, EX-04 | -40% | 롤백 불가 → 수리 진행 차단 |
| 롤백 실패 (ST-E004) | EX-04 | -100% | Kill Switch 자동 활성화 |

---

## 11. 로깅 포맷 (R-01-7 structured JSON)

### 11.1 상태 전이 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.state_transition",
    "timestamp": "2026-04-13T12:00:00Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "sdar_id": "sdar-instance-001",
    "transition_id": "N-01",
    "from_state": "S0_MONITORING",
    "to_state": "S1_DETECTED",
    "trigger_event": "oc.sdar.detection.signal_emitted",
    "guard_condition": "severity >= warn",
    "guard_result": true,
    "active_instances": 1,
    "max_instances": 3,
    "timeout_ms": 30000
  },
  "recovery": {
    "action": "none",
    "fallback": "queue_signal",
    "retry_count": 0
  }
}
```

> **참고**: `trace_id`는 `log_event.trace_id`에 1회만 기재. 루트 레벨 중복 제거 (R-01-7 structured JSON 단일 소스 원칙).

### 11.2 에스컬레이션 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.state_transition.escalation",
    "timestamp": "2026-04-13T12:02:00Z",
    "level": "WARN",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": "DH-T1-TIMEOUT",
    "message": "Diagnosis process timeout (DH-SDAR-T1=120s) exceeded for failure_code=DB_CONN_TIMEOUT",
    "recoverable": false
  },
  "context": {
    "sdar_id": "sdar-instance-001",
    "transition_id": "EX-02",
    "from_state": "S2_DIAGNOSED",
    "to_state": "S6_DONE",
    "escalation_type": "DIAGNOSIS_TIMEOUT",
    "timeout_value_s": 120,
    "dh_sdar_t1_exceeded": true,
    "partial_diagnosis": {
      "root_cause_candidates": ["db_pool_exhausted", "network_partition"],
      "confidence": 0.45,
      "elapsed_s": 120
    }
  },
  "recovery": {
    "action": "human_escalation",
    "escalation_payload_id": "esc-uuid-001",
    "urgency": "HIGH"
  }
}
```

### 11.3 Kill Switch 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.kill_switch.activated",
    "timestamp": "2026-04-13T12:05:00Z",
    "level": "CRITICAL",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": "KS-E000",
    "message": "Kill Switch activated — all SDAR stopped",
    "recoverable": false
  },
  "context": {
    "trigger_source": "ui",
    "trigger_user": "operator@vamos.io",
    "trigger_rbac_role": "OPERATOR",
    "affected_instances": [
      {
        "sdar_id": "sdar-001",
        "state_at_kill": "S4_REPAIRING",
        "rollback_status": "succeeded"
      }
    ],
    "total_instances_terminated": 1,
    "sdar_enabled_after": false
  },
  "recovery": {
    "action": "full_shutdown",
    "manual_restart_required": true,
    "rollback_results": [
      {"sdar_id": "sdar-001", "status": "succeeded", "elapsed_s": 5}
    ]
  }
}
```

---

## 12. 공통 자료 구조

### 12.1 SDARInstance

```python
class SDARInstance(BaseModel):
    """SDAR 상태 머신 인스턴스 — 단일 SDAR 파이프라인 실행 단위"""
    
    id: str                      # UUID v4
    trace_id: str                # 추적 ID
    state: SDARState             # 현재 상태 (S0~S6)
    failure_code: Optional[str]  # 원본 failure_code (중복 방지용)
    
    # 타이머 관리
    state_timer: Optional[Timer]    # 상태 체류 타임아웃
    process_timer: Optional[Timer]  # 프로세스 레벨 타임아웃 (DH-SDAR-T1)
    
    # 파이프라인 결과
    signal: SDARDetectionSignal      # Layer 1 결과
    diagnosis: Optional[SDARDiagnosis]    # Layer 2 결과
    repair_plan: Optional[SDARRepairPlan] # Layer 3 결과
    repair_result: Optional[SDARRepairResult]   # Layer 4 결과
    verification: Optional[SDARVerificationResult]  # Layer 5 결과
    
    # 수리 관리
    snapshot: Optional[Snapshot]     # L8 스냅샷
    repair_attempt_count: int = 0   # 재시도 횟수 (L6 제한: 3)
    auto_repair_allowed: bool = True  # L15 CATEGORY E 시 FALSE
    
    # 메타
    created_at: str              # ISO8601
    result: Optional[str]        # 최종 결과 ("success", "false_positive", "escalated", ...)
```

### 12.2 SDARState 열거형

```python
class SDARState(str, Enum):
    """SDAR 7-State 정의 (LOCK L2)"""
    S0_MONITORING = "S0_MONITORING"    # IDLE
    S1_DETECTED = "S1_DETECTED"        # DETECTING
    S2_DIAGNOSED = "S2_DIAGNOSED"      # DIAGNOSING
    S3_PRESCRIBED = "S3_PRESCRIBED"    # PRESCRIBING
    S4_REPAIRING = "S4_REPAIRING"      # REPAIRING
    S5_VERIFIED = "S5_VERIFIED"        # VERIFYING
    S6_DONE = "S6_DONE"                # DONE / ESCALATED
```

### 12.3 TransitionResult

```python
class TransitionResult(BaseModel):
    """상태 전이 결과"""
    transition_id: str           # N-01 ~ KS-01
    from_state: SDARState
    to_state: SDARState
    trigger_event: Optional[str]
    guard_satisfied: bool
    actions_executed: list[str]
    timestamp: str               # ISO8601
    duration_ms: int             # 전이 소요 시간
```

---

## 13. 세션 간 인터페이스 cross-check

### 13.1 P1-1 ~ P1-5 (01_five-layer-pipeline) 인터페이스

| P1 세션 | 산출물 | 본 문서 참조 위치 | 인터페이스 정합성 |
|---------|--------|-----------------|-----------------|
| P1-1 detection.md | SDARDetectionSignal 스키마 | §3.1 N-01 signal 파라미터 | CONSISTENT — signal_id, severity, channel 필드 일치 |
| P1-2 diagnosis.md | SDARDiagnosis 스키마, DH-SDAR-T1 | §3.4 N-04 diagnosis 파라미터, §3.11 EX-02 timeout | CONSISTENT — category 필드 CATEGORY E 판정, 120초 타임아웃 |
| P1-3 prescription.md | SDARRepairPlan 스키마, 5-Gate | §3.5 N-05 plan 파라미터, 5-Gate 검증 | CONSISTENT — ar_level, risk_level 필드, 5-Gate PASS/REJECT |
| P1-4 repair.md | SDARRepairResult 스키마 | §3.7 N-07 result 파라미터 | CONSISTENT — status(succeeded/failed) 필드 |
| P1-5 verification.md | SDARVerificationResult 스키마 | §3.8 N-08 verification 파라미터 | CONSISTENT — status(passed/warned/failed) 필드, OBSERVATION_PERIOD |

### 13.2 P1-7 (event_catalog.md) 예상 인터페이스

| 항목 | 본 문서 정의 | P1-7 예상 정의 | 비고 |
|------|------------|--------------|------|
| oc.sdar.detection.signal_emitted | N-01 트리거 | 이벤트 #1 페이로드 스키마 | 정합 필요 |
| oc.sdar.detection.false_positive | N-02 트리거 | 이벤트 #2 페이로드 스키마 | 정합 필요 |
| oc.sdar.verification.completed | N-09 트리거 | 이벤트 #13 페이로드 스키마 | 정합 필요 |
| CATEGORY_E 전용 이벤트 | §4 CATEGORY E 섹션 | 전용 이벤트 2건 | 정합 필요 |

---

## 14. 알고리즘 Big-O 요약 + LOCK + ABC

| 알고리즘 | Big-O | LOCK | ABC 패턴 |
|---------|-------|------|---------|
| `on_detection_signal` (N-01) | O(1) | L7, L9 | BaseStateTransition(ABC).execute() |
| `on_false_positive` (N-02) | O(1) | — | — |
| `on_detection_confirmed` (N-03) | O(1) | — | — |
| `on_diagnosis_completed` (N-04) | O(1) | L15 | — |
| `on_prescription_approved` (N-05) | O(g), g=5 Gates | L3, L5, L8, L9, L20 | BaseGate(ABC).check() |
| `on_repair_completed` (N-07) | O(1) | L11 | — |
| `on_verification_passed` (N-08) | O(1) | L9 | — |
| `on_process_completed` (N-09) | O(1) | L13 | — |
| `on_detection_timeout` (EX-01) | O(1) | — | — |
| `on_diagnosis_timeout` (EX-02) | O(1) | L9, DH-SDAR-T1 | — |
| `on_prescription_rejected` (EX-03) | O(1) | L9 | — |
| `on_verification_failed` (EX-04) | O(r), r=롤백 액션 수 | L6, L8, L12, L14 | — |
| `on_kill_switch_activated` (KS-01) | O(n), n=인스턴스 수(max 3) | L7, L9, L12, L14 | — |
| `allocate_instance` | O(n), n=인스턴스 수(max 3) | L7 | — |
| `trigger_category_e_escalation` | O(1) | L15 | — |

---

## 15. Phase 2 테스트 시나리오

| # | 시나리오 | 기대 결과 | 검증 방법 |
|---|---------|----------|----------|
| T-ST-01 | N-01: severity=critical 신호 수신 | S0→S1 전이, 인스턴스 생성, 타이머(30초) 시작 | 상태 확인 + 타이머 검증 |
| T-ST-02 | N-02: 오탐 판정 | S1→S0 전이, FALSE_POSITIVE_COOLDOWN(300초) 적용 | 쿨다운 레지스트리 검증 |
| T-ST-03 | N-05: 5-Gate 전체 PASS + AR-L3 | S3→S4 전이, 스냅샷 생성(L8), 수리 시작 | 스냅샷 존재 + 수리 로그 |
| T-ST-04 | EX-01: S1 30초 체류 초과 | S1→S0 전이, 다음 주기 이월 | deferred_signals 큐 확인 |
| T-ST-05 | EX-02: DH-SDAR-T1=120초 초과 | S2→S6 전이, EscalationPayload(type=DIAGNOSIS_TIMEOUT) 발행 | 에스컬레이션 수신 + 페이로드 구조 |
| T-ST-06 | EX-03: 5-Gate 중 CostGate REJECT | S3→S6 전이, rejected_gate=CostGate 포함 | 에스컬레이션 페이로드 검증 |
| T-ST-07 | EX-04: 검증 실패 → 롤백 → 재수리 | S5→S4 전이, 롤백 완료, 재시도 카운터 +1 | 롤백 로그 + repair_attempt_count 검증 |
| T-ST-08 | KS-01: 수리 중 Kill Switch (UI) | ALL→S0, safe_rollback 실행, sdar_enabled=FALSE | 모든 인스턴스 S0 + 알림 확인 |
| T-ST-09 | CATEGORY E: 보안 오류 감지 | S2→S6 즉시 전이 (진단 중 CATEGORY E 식별), 포렌식 30일 보존, 자동수리 차단 | L15 5규칙 전체 충족 확인 |
| T-ST-10 | L7 초과: 4번째 SDAR 시도 | 큐잉, 기존 인스턴스 종료 후 자동 할당 | 큐 적재 + 해제 후 할당 검증 |
| T-ST-11 | EX-04 + L6: 3회 재시도 소진 | S6 에스컬레이션 (MAX_RETRIES_EXHAUSTED) | 재시도 카운터 3/3 + 에스컬레이션 |
| T-ST-12 | KS-01 자동: SDAR_ROLLBACK_FAILED | Kill Switch 자동 ON, CRITICAL 에스컬레이션 | L14 자동 트리거 + 로그 검증 |
| T-ST-13 | 정상 전체 시퀀스: S0→S1→S2→S3→S4→S5→S6→S0 | 9경로 순차 통과, COOLDOWN(60초) 시작 | 전체 전이 로그 + 최종 S0 확인 |
| T-ST-14 | 동일 failure_code 중복 SDAR 시도 | 2번째 SDAR 인스턴스 생성 거부 | 중복 방지 로그 + 단일 인스턴스 확인 |

---

## 16. LOCK 참조 요약

| LOCK # | 항목 | 값 | 본 문서 적용 위치 |
|--------|------|-----|-----------------|
| **L2** | 7-State Machine 상태 전이 규칙 | IDLE → DETECTING → DIAGNOSING → PRESCRIBING → REPAIRING → VERIFYING → IDLE, 실패 시 ESCALATED | §1 개요 — 전체 전이 구조 |
| **L7** | MAX_CONCURRENT_SDAR_INSTANCES | 3 | §5 — 동시 실행 인스턴스 관리, N-01 가드 조건 |
| **L14** | Kill Switch 트리거 조건 | 모든 RBAC 역할 활성화 가능, SDAR_ROLLBACK_FAILED 시 자동 ON | §3.14 KS-01 — Kill Switch 전이 상세 |
| **L15** | CATEGORY E 자동수리 절대 금지 | 5규칙: 자동수리 금지, 즉시 차단, 감사 로그 강제, 인간 알림, 포렌식 30일 보존 | §4 — CATEGORY E 즉시 전이 |

### 관련 LOCK (본 문서에서 참조만)

| LOCK # | 항목 | 값 | 참조 목적 |
|--------|------|-----|----------|
| L1 | 5-Layer Pipeline 단계 정의 | Detection → ... → Verification | 5-Layer↔7-State 1:1 대응 |
| L3 | 5-Gate 통합 아키텍처 | PolicyGate → ... → SelfCheckGate | N-05 5-Gate 검증 |
| L5 | MAX_CONCURRENT_REPAIRS | 1 | N-05 수리 슬롯 직렬화 |
| L6 | MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR | 3 | EX-04 재시도 제한 |
| L8 | SNAPSHOT_MANDATORY | MEDIUM/HIGH risk 수리 전 스냅샷 | N-05 스냅샷 생성, EX-04 롤백 |
| L9 | NOTIFICATION_MANDATORY | 모든 수리 활동 알림 필수 | 전이 시 알림 발송 |
| L11 | OBSERVATION_PERIOD | 300초 (5분 관찰) | N-07→N-08 검증 기간 |
| L12 | ROLLBACK_TIMEOUT | 300초 | EX-04, KS-01 롤백 제한 |
| L13 | COOLDOWN_BETWEEN_REPAIRS | 60초 | N-09 쿨다운 |
| L20 | Gate 코드 공유 전략 (M-28) | BaseGate(ABC) → check(context) → GateResult | N-05 5-Gate ABC 패턴 |
| DH-SDAR-T1 | Diagnosis 단계 timeout | 120초 | EX-02 프로세스 타임아웃 |

---

## 17. ISS-3 해결 확인

| 검증 항목 | 상태 | 근거 |
|----------|------|------|
| 정상 전이 9경로 전수 포함 (G1-6a) | **완료** | §2.1 N-01 ~ N-09 |
| 예외 전이 4경로 전수 포함 (G1-6b) | **완료** | §2.2 EX-01 ~ EX-04 (타임아웃, 부분실패, CATEGORY_E) |
| Kill Switch 1경로 포함 (G1-6c) | **완료** | §2.3 KS-01 (ANY→S0) |
| 14경로 합계 확인 (G1-6d) | **완료** | §2.4 합계 표 — 정상 9 + 예외 4 + Kill Switch 1 = 14 |
| 각 전이별 트리거/가드/타임아웃 명세 (G1-6e) | **완료** | §3 전이 경로 상세 (14건 전수) |
| LOCK L2, L7, L14, L15 매핑 (G1-6f) | **완료** | §16 LOCK 참조 요약 |
| ISS-3 해결 (T-SDAR-05 전이 완전성) (G1-6g) | **완료** | §7 일관성 검증 — SPEC 12경로 100% 매핑 + 부록 A 확장 2경로 |

---
