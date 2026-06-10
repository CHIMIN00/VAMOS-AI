# Layer 4: REPAIR — 수리 실행 상세

> **도메인**: 6-5_SDAR-System / 01_five-layer-pipeline
> **Tier**: 6 (System-wide Components)
> **정본**: SDAR_SPEC **§2.5** (Layer 4 REPAIR), **§8.3** (SDARRepairResult 스키마), **§5** (Repair Action Catalog), **§6.1** (5-Gate 통합 — ApprovalGate), **§9.2** (자동수리 제한 규칙)
> **Part2 출처**: §6.9 (L5412~L5419) — When/Where 정본
> **수정 정책**: Phase 변경 시 갱신 (종합계획서 §8.2)
> **LOCK 매핑**: L1 (5-Layer Pipeline 단계 정의), L5 (MAX_CONCURRENT_REPAIRS), L8 (SNAPSHOT_MANDATORY), L9 (NOTIFICATION_MANDATORY)
> **Phase**: P1-4
> **생성일**: 2026-04-13
> **ISS 해결**: ISS-1 Layer 4

---

## 교차 참조 블록

| 참조 대상 | 관계 |
|----------|------|
| **SDAR_SPEC §2.5** | Layer 4 REPAIR 정의 정본 — AR-Level별 실행 흐름, 공통 6단계, 이벤트 |
| **SDAR_SPEC §8.3** | SDARRepairResult 스키마 정본 — Pydantic v2 정의 (SDARRepairStepResult, SDARRepairResult) |
| **SDAR_SPEC §5** | Repair Action Catalog 정본 — RA_001~RA_014 (LOW/MEDIUM/HIGH), RA_NEVER_01~RA_NEVER_10 |
| **SDAR_SPEC §5.3** | 수리 액션 실행 규칙 — cooldown, 스냅샷 의무, NEVER_AUTO 차단, side effect 공개, 타임아웃 |
| **SDAR_SPEC §6.1** | 5-Gate 통합 정본 — Layer 4 적용 Gate: PolicyGate(재확인) + ApprovalGate |
| **SDAR_SPEC §9.2** | 자동수리 제한 규칙 — L5, L6, L8, L9, L10, L13 |
| **SDAR_SPEC §9.3** | Self-evo 원칙 — 자동 적용 절대 금지 (LOCK L18) |
| **SDAR_SPEC §9.4** | Kill Switch — 모든 상태에서 즉시 정지 (LOCK L14) |
| **SDAR_SPEC §9.5** | CATEGORY E 특별 규칙 — 자동수리 절대 금지 (LOCK L15) |
| **SDAR_SPEC §9.6** | P2 도메인 수리 제한 — AR-Level 무관 인간 승인 필수 (LOCK L16) |
| **Part2 §6.9** | When/Where 정본 — Phase별 참조 범위, 구현 위치 |
| **D2.0-02 §7 I-25** | I-25 SDAR Engine 모듈 정의 |
| **01_five-layer-pipeline/_index.md** | P0 총괄 — Layer 4 개요 |
| **01_five-layer-pipeline/prescription.md** | Layer 3 산출물 — SDARRepairPlan 스키마 (Layer 4 입력) |
| **02_state-machine/_index.md** | Layer 4 = REPAIRING 상태(S4)와 동기화 |
| **04_self-diagnosis/gate_integration.md** | Layer 3→4 전환 시 5-Gate 통과 필수 (LOCK L3) — Phase 2 상세 |
| **AUTHORITY_CHAIN.md §4** | LOCK L1, L5, L8, L9 레지스트리 |

---

## 1. 개요

Layer 4 REPAIR은 SDAR 5-Layer Pipeline의 네 번째 단계로서, Layer 3 PRESCRIPTION이 출력한 `SDARRepairPlan`을 입력으로 받아 **단계적 자율수준(Graduated Autonomy)**에 따라 수리 액션을 실행하고, 실행 결과를 `SDARRepairResult`로 출력한다. (LOCK L1: Detection → Diagnosis → Prescription → Repair → Verification)

이 계층이 SDAR의 핵심이며, AR-Level에 따른 실행 흐름이 달라진다. (SDAR_SPEC §2.5)

### 1.1 핵심 요구사항

- AR-Level별 실행: L0(STOP/log) → L1(NOTIFY/suggest) → L2(AUTO/LOW) → L3(snap+notify+execute/MEDIUM) → L4(snap+[approval]+execute/HIGH) (SDAR_SPEC §2.5)
- 공통 6단계 실행 흐름: Pre-flight Check → Snapshot → Execute → Monitor → Result Capture → Notification
- MAX_CONCURRENT_REPAIRS=1 (LOCK L5) — 동시 수리 실행 최대 1건
- SNAPSHOT_MANDATORY (LOCK L8) — MEDIUM/HIGH risk 수리 전 스냅샷 필수
- NOTIFICATION_MANDATORY (LOCK L9) — 모든 수리 활동 알림 필수
- APPROVAL_TIMEOUT=600초 (LOCK L10) — 승인 대기 최대 10분, 초과 시 자동 거부
- COOLDOWN_BETWEEN_REPAIRS=60초 (LOCK L13) — 동일 액션 반복 간 최소 대기
- P2 도메인 수리 인간 승인 필수 (LOCK L16) — AR-Level 무관
- CATEGORY E 자동수리 절대 금지 (LOCK L15) — 검증 포인트
- Self-evo 자동 적용 절대 금지 (LOCK L18) — 수리 결과는 "제안"으로 간주
- `SDARRepairResult` 출력 스키마를 통한 표준화된 수리 결과 전달 (SDAR_SPEC §8.3)
- L6 상한(MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR=3) 도달 시 실행 거부 + 에스컬레이션

---

## 2. AR-Level별 실행 절차 상세 (SDAR_SPEC §2.5)

### 2.1 실행 흐름 다이어그램

```
┌──────────────────────────────────────────────────────────────────┐
│                    Layer 4: REPAIR 실행 흐름                      │
│                                                                  │
│  SDARRepairPlan 수신 (Layer 3 출력)                               │
│       │                                                          │
│       ▼                                                          │
│  ┌──────────────────────┐                                        │
│  │ CATEGORY E 사전 차단  │ ← LOCK L15                            │
│  │ (§2.7 검증 포인트)     │                                       │
│  └──────────┬───────────┘                                        │
│             │ PASS                                               │
│             ▼                                                    │
│  ┌──────────────────────┐                                        │
│  │ Self-evo 자동적용     │ ← LOCK L18                            │
│  │ 검증 포인트            │                                       │
│  └──────────┬───────────┘                                        │
│             │ PASS                                               │
│             ▼                                                    │
│  ┌──────────────────────┐                                        │
│  │ L6 반복 제한 확인      │ ← MAX_AUTO_REPAIRS_PER_ISSUE=3/h     │
│  └──────────┬───────────┘                                        │
│             │ PASS                                               │
│             ▼                                                    │
│  ┌──────────────────────┐                                        │
│  │ Concurrency Lock 취득 │ ← L5 MAX_CONCURRENT_REPAIRS=1         │
│  └──────────┬───────────┘                                        │
│             │ ACQUIRED                                           │
│             ▼                                                    │
│  ┌──────────────────────┐                                        │
│  │ AR-Level 분기          │                                       │
│  └────────┬─────────────┘                                        │
│     ┌─────┼──────┬───────────┬───────────┐                       │
│     ▼     ▼      ▼           ▼           ▼                       │
│  AR-L0  AR-L1  AR-L2      AR-L3      AR-L4                      │
│  STOP   NOTIFY  AUTO       AUTO       AUTO                       │
│  (log)  (suggest)(execute)  (snap+     (snap+                    │
│                              notify+    [approval]+              │
│                              execute)   notify+                  │
│                                         execute)                 │
│                                                                  │
│  ※ AR-L2: 즉시 실행 (LOW risk only)                              │
│  ※ AR-L3: 스냅샷 → 실행 → 알림 (MEDIUM, reversible)              │
│  ※ AR-L4: 스냅샷 → [선택적 승인] → 실행 → 알림 (HIGH)            │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 AR-L0 (MANUAL) — 로그만 기록

```
FUNCTION execute_ar_l0(
    plan: SDARRepairPlan
) -> SDARRepairResult:
    # 시간복잡도: O(1)
    # ABC 패턴: BaseRepairExecutor(ABC).execute(plan) → SDARRepairResult
    # LOCK 참조: L9 (NOTIFICATION_MANDATORY)

    LOG info("AR-L0 MANUAL — repair not executed, log only",
             plan_id=plan.plan_id,
             trace_id=plan.trace_id)

    EMIT oc.sdar.repair.started(
        plan_id=plan.plan_id,
        ar_level="AR-L0",
        mode="log_only"
    )

    # 알림 발송 (LOCK L9 — AR-Level 무관)
    notify_all_channels(
        type="sdar_repair_log_only",
        plan_id=plan.plan_id,
        diagnosis_ref=plan.diagnosis_ref,
        message="AR-L0: Repair plan logged but not executed"
    )

    result = SDARRepairResult(
        result_id=generate_uuid_v4(),
        trace_id=plan.trace_id,
        plan_ref=plan.plan_id,
        diagnosis_ref=plan.diagnosis_ref,
        ar_level_used="AR-L0",
        started_at=now_iso8601(),
        completed_at=now_iso8601(),
        total_duration_ms=0,
        overall_status="success",  # 로그만 기록 = 성공
        step_results=[],
        notification_sent=True,
        notification_channel="log",
        follow_up_required=True,
        follow_up_actions=["human_review_required"],
        governance_summary={
            "diagnosis_ref": plan.diagnosis_ref,
            "error_category": lookup_diagnosis(plan.diagnosis_ref).error_category,
            "repair_action": "log_only",
            "success": True,
            "cost_impact": 0
        }
    )

    RETURN result
```

### 2.3 AR-L1 (NOTIFY_ONLY) — 진단 + 제안 전달

```
FUNCTION execute_ar_l1(
    plan: SDARRepairPlan
) -> SDARRepairResult:
    # 시간복잡도: O(1)
    # ABC 패턴: BaseRepairExecutor(ABC).execute(plan) → SDARRepairResult
    # LOCK 참조: L9 (NOTIFICATION_MANDATORY)

    EMIT oc.sdar.repair.started(
        plan_id=plan.plan_id,
        ar_level="AR-L1",
        mode="notify_suggest"
    )

    # 사용자에게 수리 제안 전달 (UI + 로그)
    suggestion = build_repair_suggestion(plan)
    notify_all_channels(
        type="sdar_repair_suggestion",
        plan_id=plan.plan_id,
        diagnosis_ref=plan.diagnosis_ref,
        suggestion=suggestion,
        selected_candidate=plan.candidates[plan.selected_candidate_idx],
        message="AR-L1: Repair suggestion ready — human decision required"
    )

    result = SDARRepairResult(
        result_id=generate_uuid_v4(),
        trace_id=plan.trace_id,
        plan_ref=plan.plan_id,
        diagnosis_ref=plan.diagnosis_ref,
        ar_level_used="AR-L1",
        started_at=now_iso8601(),
        completed_at=now_iso8601(),
        total_duration_ms=0,
        overall_status="success",  # 제안 전달 = 성공
        step_results=[],
        notification_sent=True,
        notification_channel="both",
        follow_up_required=True,
        follow_up_actions=["await_human_decision", "manual_execution_if_approved"],
        governance_summary={
            "diagnosis_ref": plan.diagnosis_ref,
            "error_category": lookup_diagnosis(plan.diagnosis_ref).error_category,
            "repair_action": "notify_suggest",
            "success": True,
            "cost_impact": 0
        }
    )

    RETURN result
```

### 2.4 AR-L2 (AUTO_SAFE) — LOW risk 즉시 자동 실행

```
FUNCTION execute_ar_l2(
    plan: SDARRepairPlan
) -> SDARRepairResult:
    # 시간복잡도: O(S) where S = 수리 단계(step) 수
    # ABC 패턴: BaseRepairExecutor(ABC).execute(plan) → SDARRepairResult
    # LOCK 참조: L5 (MAX_CONCURRENT_REPAIRS=1), L9 (NOTIFICATION_MANDATORY),
    #            L13 (COOLDOWN=60초)

    selected = plan.candidates[plan.selected_candidate_idx]

    # 1. risk_level 확인 — AR-L2는 LOW만 허용
    IF selected.risk_level != "LOW":
        RAISE RepairExecutionError(REP_E001,
            message=f"AR-L2 only allows LOW risk, got {selected.risk_level}")

    EMIT oc.sdar.repair.started(
        plan_id=plan.plan_id,
        ar_level="AR-L2",
        mode="auto_safe",
        risk_level="LOW"
    )

    # 2. 공통 6단계 실행 (§3 참조)
    result = execute_common_6_steps(
        plan=plan,
        selected=selected,
        ar_level="AR-L2",
        requires_snapshot=False,  # LOW risk — 스냅샷 불필요
        requires_approval=False
    )

    RETURN result
```

### 2.5 AR-L3 (AUTO_MODERATE) — MEDIUM risk까지 자동 실행

```
FUNCTION execute_ar_l3(
    plan: SDARRepairPlan
) -> SDARRepairResult:
    # 시간복잡도: O(S + SNAP) where S = 수리 단계 수, SNAP = 스냅샷 비용
    # ABC 패턴: BaseRepairExecutor(ABC).execute(plan) → SDARRepairResult
    # LOCK 참조: L5, L8 (SNAPSHOT_MANDATORY), L9, L13

    selected = plan.candidates[plan.selected_candidate_idx]

    # 1. risk_level 확인 — AR-L3는 MEDIUM까지 허용
    IF selected.risk_level NOT IN ["LOW", "MEDIUM"]:
        RAISE RepairExecutionError(REP_E001,
            message=f"AR-L3 allows up to MEDIUM risk, got {selected.risk_level}")

    # 2. reversibility 확인 — MEDIUM은 reversible only
    IF selected.risk_level == "MEDIUM" AND selected.reversibility == "irreversible":
        RAISE RepairExecutionError(REP_E010,
            message="AR-L3 MEDIUM risk requires reversible action")

    EMIT oc.sdar.repair.started(
        plan_id=plan.plan_id,
        ar_level="AR-L3",
        mode="auto_moderate",
        risk_level=selected.risk_level
    )

    # 3. 공통 6단계 실행 — 스냅샷 필수 (MEDIUM일 때, LOCK L8)
    result = execute_common_6_steps(
        plan=plan,
        selected=selected,
        ar_level="AR-L3",
        requires_snapshot=(selected.risk_level == "MEDIUM"),  # L8
        requires_approval=False
    )

    RETURN result
```

### 2.6 AR-L4 (AUTO_AGGRESSIVE) — HIGH risk까지 자동 실행

```
FUNCTION execute_ar_l4(
    plan: SDARRepairPlan
) -> SDARRepairResult:
    # 시간복잡도: O(S + SNAP + APPROVAL) where APPROVAL = 승인 대기 (최대 600초)
    # ABC 패턴: BaseRepairExecutor(ABC).execute(plan) → SDARRepairResult
    # LOCK 참조: L5, L8, L9, L10 (APPROVAL_TIMEOUT=600초), L13, L16

    selected = plan.candidates[plan.selected_candidate_idx]

    # 1. risk_level 확인 — AR-L4는 HIGH까지 허용
    IF selected.risk_level NOT IN ["LOW", "MEDIUM", "HIGH"]:
        RAISE RepairExecutionError(REP_E001,
            message=f"AR-L4 allows up to HIGH risk, got {selected.risk_level}")

    EMIT oc.sdar.repair.started(
        plan_id=plan.plan_id,
        ar_level="AR-L4",
        mode="auto_aggressive",
        risk_level=selected.risk_level
    )

    # 2. 승인 필요 여부 확인
    needs_approval = (
        plan.requires_approval
        OR selected.risk_level == "HIGH"
        OR is_p2_domain_repair(plan)  # LOCK L16 — P2 도메인 AR-Level 무관 승인 필수
    )

    # 3. 공통 6단계 실행 — 스냅샷 필수 (MEDIUM/HIGH, LOCK L8), 승인 포함
    result = execute_common_6_steps(
        plan=plan,
        selected=selected,
        ar_level="AR-L4",
        requires_snapshot=(selected.risk_level IN ["MEDIUM", "HIGH"]),  # L8
        requires_approval=needs_approval
    )

    RETURN result
```

### 2.7 검증 포인트: CATEGORY E 자동수리 금지 (LOCK L15)

Layer 4 진입 전 CATEGORY E 여부를 반드시 검증한다. Layer 3에서 이미 차단하지만, Layer 4에서도 방어적으로 재확인한다.

```
FUNCTION verify_category_e_block(
    plan: SDARRepairPlan,
    diagnosis: SDARDiagnosis
) -> None:
    # LOCK 참조: L15 (CATEGORY E 자동수리 절대 금지)
    IF diagnosis.error_category == "E":
        LOG critical("CATEGORY E detected at Layer 4 — repair execution blocked",
                     plan_id=plan.plan_id,
                     error_code=diagnosis.error_code,
                     lock_ref="L15")
        EMIT oc.sdar.repair.failed(
            plan_id=plan.plan_id,
            reason="CATEGORY_E_BLOCK_L15",
            error_code="REP-E009"
        )
        RAISE RepairBlockedError(REP_E009)
```

### 2.8 검증 포인트: Self-evo 자동 적용 금지 (LOCK L18)

SDAR 수리 결과는 "제안"으로 간주되며, S-Module에 자동 적용하려는 시도는 차단한다.

```
FUNCTION verify_self_evo_block(
    plan: SDARRepairPlan
) -> None:
    # LOCK 참조: L18 (Self-evo 원칙: 자동 적용 절대 금지)
    # 수리 결과가 S-Module 적용을 포함하는 경우 차단
    FOR step IN plan.candidates[plan.selected_candidate_idx].steps:
        IF step.action_name IN ["apply_to_s_module", "auto_evolve", "auto_learn"]:
            LOG critical("Self-evo auto-apply detected at Layer 4 — blocked",
                         plan_id=plan.plan_id,
                         action_name=step.action_name,
                         lock_ref="L18")
            RAISE RepairBlockedError(REP_E011)
```

---

## 3. 공통 6단계 실행 흐름 (SDAR_SPEC §2.5)

모든 AR-Level(L2~L4)에서 수리 액션 실행 시 공통으로 적용되는 6단계 흐름:

### 3.1 실행 흐름 다이어그램

```
┌───────────────────────────────────────────────────────────────┐
│                  공통 6단계 REPAIR 실행 흐름                    │
│                                                               │
│  Step 1: Pre-flight Check                                     │
│     ├── 전제 조건 확인 (plan.pre_conditions)                    │
│     ├── 시스템 상태 재검증                                      │
│     ├── L5 동시 수리 Lock 확인                                  │
│     ├── L13 Cooldown 확인                                      │
│     └── Kill Switch 상태 확인 (LOCK L14)                       │
│            │                                                   │
│            ▼ PASS                                              │
│  Step 2: Snapshot (MEDIUM/HIGH — LOCK L8)                     │
│     ├── 수리 대상 시스템 상태 스냅샷 저장                         │
│     ├── snapshot_id 생성 + 결과에 기록                           │
│     └── 스냅샷 실패 시 수리 중단 (REP-E003)                     │
│            │                                                   │
│            ▼ CREATED                                           │
│  [ApprovalGate — AR-L4 + HIGH/P2 시] (LOCK L10, L16)          │
│     ├── I-19 Approval Manager 승인 요청                        │
│     ├── 최대 600초 대기                                         │
│     ├── approved → 실행 진행                                    │
│     ├── denied → 수리 취소 (REP-E005)                          │
│     └── timeout → 자동 거부 (REP-E006)                         │
│            │                                                   │
│            ▼ APPROVED / NOT_NEEDED                              │
│  Step 3: Execute                                               │
│     ├── 수리 단계 순차 실행                                      │
│     ├── 각 단계: timeout = expected_duration_s * 3              │
│     ├── 각 단계 on_failure: abort/skip/rollback                 │
│     └── side_effects 기록                                       │
│            │                                                   │
│            ▼ EXECUTING                                          │
│  Step 4: Monitor                                               │
│     ├── 실행 중 실시간 모니터링                                   │
│     ├── 타임아웃 감지 → 강제 중단 + 롤백                          │
│     ├── 이상 감지 → 조기 종료                                    │
│     └── Kill Switch 감시 (활성화 시 즉시 중단)                    │
│            │                                                   │
│            ▼ COMPLETED / FAILED                                 │
│  Step 5: Result Capture                                        │
│     ├── 각 step_result 수집                                     │
│     ├── overall_status 결정 (success/partial/failed/rollback)   │
│     └── governance_summary 구성                                 │
│            │                                                   │
│            ▼                                                    │
│  Step 6: Notification (LOCK L9)                                │
│     ├── AR-Level에 따른 알림 발송                                │
│     ├── side_effects 포함 (SDAR_SPEC §5.3 규칙 4)              │
│     └── 채널: ui/log/both                                      │
└───────────────────────────────────────────────────────────────┘
```

### 3.2 공통 실행 알고리즘

```
FUNCTION execute_common_6_steps(
    plan: SDARRepairPlan,
    selected: SDARRepairCandidate,
    ar_level: str,
    requires_snapshot: bool,
    requires_approval: bool
) -> SDARRepairResult:
    # 시간복잡도: O(S * T_max) where S = 단계 수, T_max = 최대 단계 타임아웃
    # ABC 패턴: BaseRepairExecutor(ABC).execute_pipeline(plan, selected) → SDARRepairResult
    # LOCK 참조: L5, L8, L9, L10, L13, L14

    started_at = now_iso8601()
    overall_status = "unknown"  # TRY 진입 전 초기화 — preflight 예외(RepairConcurrencyError/RepairMaxAttemptsError/RepairPreConditionError/RepairCooldownError) 전파 시 FINALLY 안전 보장
    step_results = []
    snapshot_id = None
    approval_id = None
    approval_status = None
    rollback_triggered = False
    rollback_result = None

    TRY:
        # ═══════════════════════════════════════════════
        # Step 1: Pre-flight Check
        # ═══════════════════════════════════════════════
        preflight_check(plan, selected)  # §3.3 상세

        # ═══════════════════════════════════════════════
        # Step 2: Snapshot (LOCK L8)
        # ═══════════════════════════════════════════════
        IF requires_snapshot:
            snapshot_id = create_snapshot(plan, selected)  # §3.4 상세
            EMIT oc.sdar.repair.snapshot_created(
                plan_id=plan.plan_id,
                snapshot_id=snapshot_id
            )

        # ═══════════════════════════════════════════════
        # ApprovalGate (Layer 4 적용 — SDAR_SPEC §6.1)
        # ═══════════════════════════════════════════════
        IF requires_approval:
            approval_result = request_approval(plan, selected)  # §3.5 상세
            approval_id = approval_result.approval_id
            approval_status = approval_result.status

            IF approval_status == "denied":
                RAISE RepairApprovalDeniedError(REP_E005)
            IF approval_status == "timeout":
                RAISE RepairApprovalTimeoutError(REP_E006)

        # ═══════════════════════════════════════════════
        # Step 3: Execute
        # ═══════════════════════════════════════════════
        FOR step IN selected.steps:
            step_timeout = step.expected_duration_s * 3  # SDAR_SPEC §5.3 규칙 5
            step_result = execute_single_step(step, step_timeout)  # §3.6 상세

            step_results.append(step_result)

            EMIT oc.sdar.repair.step_completed(
                plan_id=plan.plan_id,
                step_order=step.step_order,
                status=step_result.status
            )

            # Step 4: Monitor (각 단계 실행 중 내장)
            IF step_result.status == "failed":
                IF step.on_failure == "abort":
                    BREAK
                ELIF step.on_failure == "rollback":
                    rollback_triggered = True
                    rollback_result = execute_rollback(
                        plan, snapshot_id, selected)  # §3.7 상세
                    BREAK
                ELIF step.on_failure == "skip":
                    CONTINUE

            # Kill Switch 감시 (LOCK L14)
            IF is_kill_switch_active():
                LOG critical("Kill Switch activated during repair — aborting",
                             plan_id=plan.plan_id)
                rollback_triggered = True
                rollback_result = execute_rollback(
                    plan, snapshot_id, selected)
                RAISE RepairKillSwitchError(REP_E008)

        # ═══════════════════════════════════════════════
        # Step 5: Result Capture
        # ═══════════════════════════════════════════════
        overall_status = determine_overall_status(step_results, rollback_triggered)

        IF overall_status == "success":
            EMIT oc.sdar.repair.succeeded(plan_id=plan.plan_id)
        ELSE:
            EMIT oc.sdar.repair.failed(
                plan_id=plan.plan_id,
                overall_status=overall_status
            )

    EXCEPT RepairApprovalDeniedError:
        overall_status = "failed"
        EMIT oc.sdar.repair.failed(plan_id=plan.plan_id, reason="approval_denied")

    EXCEPT RepairApprovalTimeoutError:
        overall_status = "failed"
        EMIT oc.sdar.repair.failed(plan_id=plan.plan_id, reason="approval_timeout")

    EXCEPT RepairKillSwitchError:
        overall_status = "failed"
        # Kill Switch 이벤트는 03_emergency-kill-switch에서 별도 발행

    EXCEPT RepairExecutionError AS e:
        overall_status = "failed"
        EMIT oc.sdar.repair.failed(plan_id=plan.plan_id, reason=str(e))
        # 스냅샷이 있으면 롤백 시도
        IF snapshot_id AND NOT rollback_triggered:
            rollback_triggered = True
            rollback_result = execute_rollback(plan, snapshot_id, selected)

    FINALLY:
        completed_at = now_iso8601()

        # 수리 Lock 해제 (LOCK L5 — preflight_check에서 취득한 Lock 반환)
        release_repair_lock()

        # ═══════════════════════════════════════════════
        # Step 6: Notification (LOCK L9)
        # ═══════════════════════════════════════════════
        notification_channel = determine_notification_channel(ar_level)
        notify_all_channels(
            type="sdar_repair_result",
            plan_id=plan.plan_id,
            overall_status=overall_status,
            ar_level=ar_level,
            side_effects=selected.side_effects,  # SDAR_SPEC §5.3 규칙 4
            rollback_triggered=rollback_triggered,
            channel=notification_channel
        )

    result = SDARRepairResult(
        result_id=generate_uuid_v4(),
        trace_id=plan.trace_id,
        plan_ref=plan.plan_id,
        diagnosis_ref=plan.diagnosis_ref,
        ar_level_used=ar_level,
        started_at=started_at,
        completed_at=completed_at,
        total_duration_ms=calculate_duration_ms(started_at, completed_at),
        overall_status=overall_status,
        step_results=step_results,
        snapshot_id=snapshot_id,
        approval_id=approval_id,
        approval_status=approval_status,
        rollback_triggered=rollback_triggered,
        rollback_result=rollback_result,
        notification_sent=True,
        notification_channel=notification_channel,
        follow_up_required=(overall_status != "success"),
        follow_up_actions=build_follow_up_actions(overall_status, rollback_triggered),
        governance_summary=build_governance_summary(
            plan, selected, overall_status, step_results)
    )

    RETURN result
```

### 3.3 Step 1: Pre-flight Check 상세

```
FUNCTION preflight_check(
    plan: SDARRepairPlan,
    selected: SDARRepairCandidate
) -> None:
    # 시간복잡도: O(P) where P = pre_conditions 수
    # LOCK 참조: L5, L13, L14, L15, L18

    # 1. Kill Switch 확인 (LOCK L14)
    IF is_kill_switch_active():
        RAISE RepairKillSwitchError(REP_E008)

    # 2. 동시 수리 Lock (LOCK L5 — MAX_CONCURRENT_REPAIRS=1)
    IF NOT acquire_repair_lock(timeout=30):
        RAISE RepairConcurrencyError(REP_E002)

    # 3. Cooldown 확인 (LOCK L13 — 60초)
    last_repair = get_last_repair_for_action(
        selected.steps[0].action_id)
    IF last_repair AND (now() - last_repair.completed_at) < 60:
        remaining = 60 - (now() - last_repair.completed_at)
        RAISE RepairCooldownError(REP_E007,
            message=f"Cooldown active — {remaining}s remaining (L13)")

    # 4. L6 반복 횟수 확인 (MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR=3)
    hourly_count = get_hourly_repair_count(plan.diagnosis_ref)
    IF hourly_count >= 3:
        RAISE RepairMaxAttemptsError(REP_E004)

    # 5. 전제 조건 확인
    FOR condition IN plan.pre_conditions:
        IF NOT evaluate_condition(condition):
            RAISE RepairPreConditionError(REP_E001,
                message=f"Pre-condition failed: {condition}")

    # 6. 시스템 상태 재검증
    current_health = check_system_health()
    IF current_health.status == "critical":
        RAISE RepairPreConditionError(REP_E001,
            message="System health critical — repair deferred")
```

### 3.4 Step 2: Snapshot 생성/복원 절차 (LOCK L8)

```
FUNCTION create_snapshot(
    plan: SDARRepairPlan,
    selected: SDARRepairCandidate
) -> str:
    # 시간복잡도: O(D) where D = 스냅샷 대상 데이터 크기
    # LOCK 참조: L8 (SNAPSHOT_MANDATORY — MEDIUM/HIGH)

    # 1. 스냅샷 대상 식별
    target_modules = extract_target_modules(plan, selected)

    # 2. 스냅샷 생성 (기존 6.6 Backup/Recovery 연동)
    snapshot = backup_recovery_service.create_snapshot(
        targets=target_modules,
        metadata={
            "plan_id": plan.plan_id,
            "trace_id": plan.trace_id,
            "reason": "sdar_repair_preflight",
            "ar_level": plan.required_ar_level,
            "risk_level": selected.risk_level
        }
    )

    IF NOT snapshot.success:
        LOG error("Snapshot creation failed — repair cannot proceed (L8)",
                  plan_id=plan.plan_id,
                  error=snapshot.error)
        RAISE SnapshotCreationError(REP_E003)

    LOG info("Snapshot created successfully",
             plan_id=plan.plan_id,
             snapshot_id=snapshot.snapshot_id)

    RETURN snapshot.snapshot_id


FUNCTION restore_snapshot(
    snapshot_id: str,
    plan_id: str
) -> dict:
    # LOCK 참조: L8, L12 (ROLLBACK_TIMEOUT=300초)

    restore_result = backup_recovery_service.restore_snapshot(
        snapshot_id=snapshot_id,
        timeout=300  # L12 ROLLBACK_TIMEOUT
    )

    IF NOT restore_result.success:
        LOG critical("Snapshot restore failed — human escalation required",
                     plan_id=plan_id,
                     snapshot_id=snapshot_id,
                     error=restore_result.error)
        # SDAR_ROLLBACK_FAILED → Kill Switch 자동 활성화 (LOCK L14)
        EMIT oc.sdar.kill_switch.activated(
            reason="SDAR_ROLLBACK_FAILED",
            triggered_by="sdar.layer4.repair"
        )
        RAISE RollbackFailedError(REP_E012)

    RETURN {
        "snapshot_id": snapshot_id,
        "restored_at": now_iso8601(),
        "duration_ms": restore_result.duration_ms
    }
```

### 3.5 ApprovalGate: 승인 요청 절차 (LOCK L10, L16)

```
FUNCTION request_approval(
    plan: SDARRepairPlan,
    selected: SDARRepairCandidate
) -> ApprovalResult:
    # 시간복잡도: O(1) + 대기 최대 600초
    # ABC 패턴: BaseGate(ABC).check(context) → GateResult (LOCK L20)
    # LOCK 참조: L10 (APPROVAL_TIMEOUT=600초), L16 (P2 도메인 인간 승인 필수)

    EMIT oc.sdar.repair.approval_requested(
        plan_id=plan.plan_id,
        required_ar_level=plan.required_ar_level,
        risk_level=selected.risk_level,
        approval_reason=plan.approval_reason,
        is_p2_domain=is_p2_domain_repair(plan)
    )

    # I-19 Approval Manager에 승인 요청
    approval_request = i19_approval_manager.request(
        type="sdar_repair_approval",
        plan_id=plan.plan_id,
        trace_id=plan.trace_id,
        repair_summary={
            "selected_action": selected.steps[0].action_name,
            "risk_level": selected.risk_level,
            "ar_level": plan.required_ar_level,
            "estimated_duration_s": selected.estimated_total_duration_s,
            "side_effects": selected.side_effects,
            "requires_snapshot": plan.requires_snapshot,
            "rollback_strategy": plan.rollback_plan.strategy
        },
        timeout=600,  # L10 APPROVAL_TIMEOUT
        p2_domain=is_p2_domain_repair(plan)  # L16
    )

    # 대기 (최대 600초)
    approval_result = approval_request.await_result(timeout=600)

    IF approval_result.status == "timeout":
        LOG warn("Approval timeout — auto-denied (L10)",
                 plan_id=plan.plan_id,
                 waited_seconds=600)

    RETURN approval_result
```

### 3.6 Step 3: 개별 단계 실행

```
FUNCTION execute_single_step(
    step: SDARRepairStep,
    timeout: int
) -> SDARRepairStepResult:
    # 시간복잡도: O(T) where T = 단계 실행 시간
    # SDAR_SPEC §5.3 규칙 5: timeout = expected_duration_s * 3

    started_at = now_iso8601()

    TRY:
        # 액션 실행기 조회
        executor = repair_action_registry.get_executor(step.action_id)

        IF executor IS None:
            RAISE RepairExecutionError(REP_E001,
                message=f"No executor for action {step.action_id}")

        # 실행
        output = executor.execute(
            action_name=step.action_name,
            parameters=step.parameters,
            timeout=timeout
        )

        RETURN SDARRepairStepResult(
            step_order=step.step_order,
            action_id=step.action_id,
            action_name=step.action_name,
            status="success",
            started_at=started_at,
            completed_at=now_iso8601(),
            duration_ms=calculate_duration_ms(started_at, now_iso8601()),
            output=output
        )

    EXCEPT TimeoutError:
        RETURN SDARRepairStepResult(
            step_order=step.step_order,
            action_id=step.action_id,
            action_name=step.action_name,
            status="timeout",
            started_at=started_at,
            completed_at=now_iso8601(),
            duration_ms=timeout * 1000,
            error=f"Step timed out after {timeout}s (estimated * 3)"
        )

    EXCEPT Exception AS e:
        RETURN SDARRepairStepResult(
            step_order=step.step_order,
            action_id=step.action_id,
            action_name=step.action_name,
            status="failed",
            started_at=started_at,
            completed_at=now_iso8601(),
            duration_ms=calculate_duration_ms(started_at, now_iso8601()),
            error=str(e)
        )
```

### 3.7 롤백 실행

```
FUNCTION execute_rollback(
    plan: SDARRepairPlan,
    snapshot_id: Optional[str],
    selected: SDARRepairCandidate
) -> dict:
    # LOCK 참조: L8 (SNAPSHOT_MANDATORY), L12 (ROLLBACK_TIMEOUT=300초)

    EMIT oc.sdar.repair.rollback_triggered(
        plan_id=plan.plan_id,
        snapshot_id=snapshot_id,
        strategy=plan.rollback_plan.strategy
    )

    rollback_strategy = plan.rollback_plan.strategy

    IF rollback_strategy == "snapshot_restore" AND snapshot_id:
        # 스냅샷 복원 (LOCK L8)
        RETURN restore_snapshot(snapshot_id, plan.plan_id)

    ELIF rollback_strategy == "reverse_actions":
        # 역순 수리 단계 실행
        reverse_results = []
        FOR step IN plan.rollback_plan.reverse_steps:
            step_timeout = step.expected_duration_s * 3
            result = execute_single_step(step, step_timeout)
            reverse_results.append(result)
            IF result.status == "failed":
                LOG critical("Reverse action failed — manual intervention needed",
                             plan_id=plan.plan_id,
                             step=step.action_name)
                BREAK

        RETURN {
            "strategy": "reverse_actions",
            "steps_executed": len(reverse_results),
            "all_success": all(r.status == "success" FOR r IN reverse_results)
        }

    ELIF rollback_strategy == "manual":
        # 수동 롤백 — 인간 에스컬레이션
        LOG warn("Manual rollback required — escalating to human",
                 plan_id=plan.plan_id)
        RETURN {
            "strategy": "manual",
            "escalation_required": True
        }

    ELSE:
        LOG error("Unknown rollback strategy",
                  strategy=rollback_strategy)
        RETURN {"strategy": "unknown", "error": "unrecognized rollback strategy"}
```

---

## 4. MAX_CONCURRENT_REPAIRS=1 동시 실행 제한 구현 (LOCK L5)

```
FUNCTION acquire_repair_lock(timeout: int = 30) -> bool:
    # LOCK 참조: L5 (MAX_CONCURRENT_REPAIRS=1)
    # 구현: 분산 Lock (Redis SETNX 또는 동등 메커니즘)

    lock_key = "sdar:repair:execution_lock"
    lock_ttl = 1800  # 최대 30분 (안전 상한)

    acquired = distributed_lock.acquire(
        key=lock_key,
        ttl=lock_ttl,
        timeout=timeout
    )

    IF NOT acquired:
        LOG warn("Repair lock acquisition failed — another repair in progress (L5)",
                 timeout=timeout)

    RETURN acquired


FUNCTION release_repair_lock() -> None:
    lock_key = "sdar:repair:execution_lock"
    distributed_lock.release(key=lock_key)
```

### 4.1 직렬화 보장 (SDAR_SPEC §7.4)

- SDAR_S4_REPAIRING 상태에서는 최대 1개 수리만 실행 가능 (LOCK L5)
- MAX_CONCURRENT_SDAR_INSTANCES=3 (LOCK L7)은 SDAR 인스턴스(Detection~Verification) 수준
- Layer 4 REPAIR만 직렬화 (동시 1건), 다른 Layer는 인스턴스별 독립 실행

---

## 5. `SDARRepairResult` 출력 스키마 (SDAR_SPEC §8.3)

### 5.1 스키마 정의 (Pydantic v2)

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Literal


class SDARRepairStepResult(BaseModel):
    """개별 수리 단계 실행 결과"""
    step_order: int = Field(..., description="실행 순서")
    action_id: str = Field(..., description="Repair Action Catalog ID (e.g., RA_003)")
    action_name: str = Field(..., description="액션 명칭 (e.g., retry_with_backoff)")
    status: Literal["success", "failed", "skipped", "timeout"] = Field(
        ..., description="실행 결과"
    )
    started_at: str = Field(..., description="시작 시각 (ISO8601 UTC)")
    completed_at: str = Field(..., description="완료 시각 (ISO8601 UTC)")
    duration_ms: int = Field(..., description="실행 소요 시간 (ms)")
    output: dict = Field(default_factory=dict, description="액션 실행 결과 데이터")
    error: Optional[str] = Field(None, description="오류 메시지 (실패 시)")


class SDARRepairResult(BaseModel):
    """Layer 4 수리 실행 결과 스키마 (SDAR_SPEC §8.3)"""
    result_id: str = Field(..., description="수리 결과 고유 ID (UUID v4)")
    trace_id: str = Field(..., description="연관 trace_id")
    plan_ref: str = Field(..., description="SDARRepairPlan.plan_id 참조")
    diagnosis_ref: str = Field(..., description="SDARDiagnosis.diagnosis_id 참조")

    # 실행 정보
    ar_level_used: str = Field(..., description="실행에 사용된 AR-Level")
    started_at: str = Field(..., description="수리 시작 시각 (ISO8601 UTC)")
    completed_at: str = Field(..., description="수리 완료 시각 (ISO8601 UTC)")
    total_duration_ms: int = Field(..., description="전체 수리 소요 시간 (ms)")

    # 결과
    overall_status: Literal["success", "partial_success", "failed", "rollback_executed"] = Field(
        ..., description="전체 수리 결과"
    )
    step_results: List[SDARRepairStepResult] = Field(
        ..., description="개별 단계 결과"
    )

    # 스냅샷
    snapshot_id: Optional[str] = Field(
        None, description="수리 전 생성된 스냅샷 ID"
    )

    # 승인
    approval_id: Optional[str] = Field(
        None, description="I-19 승인 ID (승인이 필요했던 경우)"
    )
    approval_status: Optional[Literal["approved", "denied", "timeout"]] = Field(
        None, description="승인 결과"
    )

    # 롤백
    rollback_triggered: bool = Field(default=False, description="롤백 실행 여부")
    rollback_result: Optional[dict] = Field(
        None, description="롤백 실행 결과"
    )

    # 알림
    notification_sent: bool = Field(default=False, description="알림 발송 여부")
    notification_channel: Optional[str] = Field(
        None, description="알림 채널 (ui/log/both)"
    )

    # 후속 조치
    follow_up_required: bool = Field(default=False, description="추가 후속 조치 필요 여부")
    follow_up_actions: List[str] = Field(
        default_factory=list, description="권장 후속 조치"
    )

    # S-8 거버넌스 보고용
    governance_summary: dict = Field(
        default_factory=dict,
        description="거버넌스 보고 요약 {error_category, error_code, repair_action, success, cost_impact}"
    )

    model_config = ConfigDict(extra="forbid")
```

### 5.2 필드 상세

| 필드 | 타입 | 필수/선택 | 설명 |
|------|------|----------|------|
| `result_id` | `str` (UUID v4) | **필수** | 수리 결과 고유 식별자 |
| `trace_id` | `str` (UUID v4) | **필수** | 연관 trace_id — 전체 파이프라인 추적용 |
| `plan_ref` | `str` | **필수** | Layer 3 SDARRepairPlan.plan_id 참조 |
| `diagnosis_ref` | `str` | **필수** | Layer 2 SDARDiagnosis.diagnosis_id 참조 |
| `ar_level_used` | `str` | **필수** | 실행에 사용된 AR-Level (AR-L0~AR-L4) |
| `started_at` | `str` (ISO8601 UTC) | **필수** | 수리 시작 시각 |
| `completed_at` | `str` (ISO8601 UTC) | **필수** | 수리 완료 시각 |
| `total_duration_ms` | `int` | **필수** | 전체 수리 소요 시간 (밀리초) |
| `overall_status` | `Literal[...]` | **필수** | 전체 수리 결과: success, partial_success, failed, rollback_executed |
| `step_results` | `List[SDARRepairStepResult]` | **필수** | 개별 단계 결과 목록 |
| `snapshot_id` | `Optional[str]` | 선택 | 수리 전 생성된 스냅샷 ID (MEDIUM/HIGH 시) |
| `approval_id` | `Optional[str]` | 선택 | I-19 승인 ID (승인 필요 시) |
| `approval_status` | `Optional[Literal[...]]` | 선택 | 승인 결과: approved, denied, timeout |
| `rollback_triggered` | `bool` | 선택 (기본 False) | 롤백 실행 여부 |
| `rollback_result` | `Optional[dict]` | 선택 | 롤백 실행 결과 상세 |
| `notification_sent` | `bool` | 선택 (기본 False) | 알림 발송 여부 (LOCK L9) |
| `notification_channel` | `Optional[str]` | 선택 | 알림 채널: ui, log, both |
| `follow_up_required` | `bool` | 선택 (기본 False) | 추가 후속 조치 필요 여부 |
| `follow_up_actions` | `List[str]` | 선택 (기본 []) | 권장 후속 조치 목록 |
| `governance_summary` | `dict` | 선택 (기본 {}) | S-8 거버넌스 보고 요약 |

### 5.3 예시 (AR-L2 — LOW risk 자동 수리 성공)

```json
{
    "result_id": "res_550e8400-e29b-41d4-a716-446655440010",
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "plan_ref": "plan_550e8400-e29b-41d4-a716-446655440003",
    "diagnosis_ref": "diag_550e8400-e29b-41d4-a716-446655440001",
    "ar_level_used": "AR-L2",
    "started_at": "2026-02-23T10:30:10Z",
    "completed_at": "2026-02-23T10:30:25Z",
    "total_duration_ms": 15000,
    "overall_status": "success",
    "step_results": [
        {
            "step_order": 1,
            "action_id": "RA_003",
            "action_name": "retry_with_backoff",
            "status": "success",
            "started_at": "2026-02-23T10:30:10Z",
            "completed_at": "2026-02-23T10:30:18Z",
            "duration_ms": 8000,
            "output": {"retries": 2, "final_status_code": 200},
            "error": null
        },
        {
            "step_order": 2,
            "action_id": "RA_004",
            "action_name": "switch_model_fallback",
            "status": "skipped",
            "started_at": "2026-02-23T10:30:18Z",
            "completed_at": "2026-02-23T10:30:18Z",
            "duration_ms": 0,
            "output": {"reason": "primary action succeeded, fallback unnecessary"},
            "error": null
        }
    ],
    "snapshot_id": null,
    "approval_id": null,
    "approval_status": null,
    "rollback_triggered": false,
    "rollback_result": null,
    "notification_sent": true,
    "notification_channel": "log",
    "follow_up_required": false,
    "follow_up_actions": [],
    "governance_summary": {
        "error_category": "A",
        "error_code": "SDAR_A04_API_429",
        "repair_action": "retry_with_backoff",
        "success": true,
        "cost_impact": 0
    }
}
```

---

## 6. 공통 자료 구조 정의 (세션 간 인터페이스)

### 6.1 Layer 3 → Layer 4 인터페이스

Layer 4는 Layer 3의 `SDARRepairPlan`을 입력으로 받는다. (prescription.md §5, §6.2 참조)

```python
# 입력: SDARRepairPlan (Layer 3 출력, SDAR_SPEC §8.2)
# - plan_id: str (UUID v4)
# - trace_id: str (UUID v4)
# - diagnosis_ref: str (SDARDiagnosis.diagnosis_id 참조)
# - created_at: str (ISO8601 UTC)
# - candidates: List[SDARRepairCandidate] (1~5개)
# - selected_candidate_idx: int (기본 0)
# - required_ar_level: Literal["AR-L2", "AR-L3", "AR-L4", "NEVER_AUTO"]
# - current_ar_level: str
# - can_auto_execute: bool
# - gate_results: dict
# - pre_conditions: List[str]
# - post_conditions: List[str]
# - rollback_plan: SDARRollbackPlan
# - requires_snapshot: bool
# - requires_approval: bool
# - approval_reason: Optional[str]
```

### 6.2 Layer 4 → Layer 5 인터페이스

Layer 4는 `SDARRepairResult`를 출력하며, Layer 5 VERIFICATION의 입력이 된다.

```python
# 출력: SDARRepairResult (SDAR_SPEC §8.3 — 위 §5 상세)
# - result_id: str (UUID v4)
# - trace_id: str (UUID v4)
# - plan_ref: str (SDARRepairPlan.plan_id 참조)
# - diagnosis_ref: str (SDARDiagnosis.diagnosis_id 참조)
# - ar_level_used: str
# - started_at: str (ISO8601 UTC)
# - completed_at: str (ISO8601 UTC)
# - total_duration_ms: int
# - overall_status: Literal["success", "partial_success", "failed", "rollback_executed"]
# - step_results: List[SDARRepairStepResult]
# - snapshot_id: Optional[str]
# - approval_id: Optional[str]
# - approval_status: Optional[Literal["approved", "denied", "timeout"]]
# - rollback_triggered: bool
# - rollback_result: Optional[dict]
# - notification_sent: bool
# - notification_channel: Optional[str]
# - follow_up_required: bool
# - follow_up_actions: List[str]
# - governance_summary: dict
```

### 6.3 Layer 4 내부 중간 자료 구조

```python
class ApprovalResult(BaseModel):
    """I-19 승인 결과 (내부 중간 구조)"""
    approval_id: str
    status: Literal["approved", "denied", "timeout"]
    decided_by: Optional[str]  # 승인자 ID
    decided_at: Optional[str]  # ISO8601 UTC
    reason: Optional[str]


class SnapshotResult(BaseModel):
    """스냅샷 생성/복원 결과 (내부 중간 구조)"""
    snapshot_id: str
    success: bool
    created_at: str  # ISO8601 UTC
    size_bytes: int
    targets: List[str]  # 스냅샷 대상 모듈
    error: Optional[str]
    duration_ms: int


class RepairLockInfo(BaseModel):
    """수리 실행 Lock 정보 (L5 동시 실행 제한)"""
    lock_key: str
    acquired: bool
    acquired_at: Optional[str]  # ISO8601 UTC
    ttl: int  # 초
    holder_plan_id: Optional[str]
```

---

## 7. 이벤트 카탈로그 (SDAR_SPEC §2.5)

| 이벤트 타입 | 설명 | 발행 시점 | 포함 데이터 |
|------------|------|----------|-----------|
| `oc.sdar.repair.started` | 수리 실행 시작 | Layer 4 진입 시 | plan_id, ar_level, mode, risk_level |
| `oc.sdar.repair.snapshot_created` | 스냅샷 생성 완료 | Step 2 완료 시 (MEDIUM/HIGH) | plan_id, snapshot_id |
| `oc.sdar.repair.approval_requested` | 승인 요청 발송 | ApprovalGate 진입 시 (AR-L4/HIGH/P2) | plan_id, required_ar_level, risk_level, approval_reason, is_p2_domain |
| `oc.sdar.repair.step_completed` | 개별 단계 완료 | Step 3 각 단계 완료 시 | plan_id, step_order, status |
| `oc.sdar.repair.succeeded` | 수리 성공 | 전체 수리 성공 시 | plan_id |
| `oc.sdar.repair.failed` | 수리 실패 | 수리 실패 시 | plan_id, overall_status, reason |
| `oc.sdar.repair.rollback_triggered` | 롤백 시작 | 롤백 실행 시 | plan_id, snapshot_id, strategy |

---

## 8. 에러 코드 카탈로그 (DH-2: Layer 4)

| 에러 코드 | 심각도 | 설명 | 복구 가능 | 처리 |
|----------|--------|------|----------|------|
| `REP-E001` | ERROR | 실행 전제조건 미충족 — pre_condition 실패 또는 risk level 불일치 | YES | 수리 중단 + 인간 에스컬레이션 |
| `REP-E002` | WARN | 동시 수리 제한 — 다른 수리 진행 중 (L5) | YES | 대기 후 재시도 (최대 30초), 실패 시 에스컬레이션 |
| `REP-E003` | ERROR | 스냅샷 생성 실패 — Backup/Recovery 서비스 오류 (L8) | YES | 수리 중단 (MEDIUM/HIGH risk 스냅샷 필수), 에스컬레이션 |
| `REP-E004` | WARN | 시간당 최대 수리 횟수 초과 — L6 상한 도달 | YES | 수리 거부 + 에스컬레이션 (1시간 대기 후 자동 해제) |
| `REP-E005` | ERROR | 승인 거부 — I-19 Approval denied | YES | 수리 취소 + 사유 기록 |
| `REP-E006` | ERROR | 승인 타임아웃 — 600초(L10) 초과 자동 거부 | YES | 수리 취소 + 에스컬레이션 |
| `REP-E007` | WARN | Cooldown 위반 — 동일 액션 60초(L13) 이내 재실행 시도 | YES | 대기 후 재시도, 잔여 cooldown 시간 안내 |
| `REP-E008` | CRITICAL | Kill Switch 활성화로 수리 중단 (L14) | NO | 즉시 중단 + 가능 시 롤백 + S0 전이 |
| `REP-E009` | CRITICAL | CATEGORY E 차단 — Layer 4 방어적 재확인 (L15) | NO | 즉시 에스컬레이션, 수리 실행 거부 |
| `REP-E010` | ERROR | reversibility 부적합 — AR-L3에서 irreversible 액션 시도 | YES | 수리 중단 + AR-Level 상향 필요 안내 |
| `REP-E011` | CRITICAL | Self-evo 자동 적용 시도 차단 (L18) | NO | 즉시 에스컬레이션, 수리 실행 거부 |
| `REP-E012` | CRITICAL | 롤백 실패 — 스냅샷 복원 실패 (L14 Kill Switch 자동 활성화) | NO | Kill Switch 자동 ON + 인간 긴급 에스컬레이션 |

### 8.1 예외 처리 정책 표

| error_code | recoverable | 처리 | 재시도 횟수 | 에스컬레이션 조건 |
|-----------|-------------|------|-----------|-----------------|
| REP-E001 | YES | 수리 중단 | 0 | 즉시 (전제 조건 실패) |
| REP-E002 | YES | 대기 후 재시도 | 1 | Lock 취득 실패 |
| REP-E003 | YES | 수리 중단 | 1 | 스냅샷 2회 연속 실패 |
| REP-E004 | YES | 1시간 대기 | 0 | L6 상한 도달 시 인간 통보 |
| REP-E005 | YES | 수리 취소 | 0 | 즉시 (승인 거부) |
| REP-E006 | YES | 수리 취소 | 0 | 즉시 (승인 타임아웃) |
| REP-E007 | YES | cooldown 대기 | 1 | N/A (자동 해제) |
| REP-E008 | NO | 즉시 중단 | 0 | Kill Switch 해제 대기 |
| REP-E009 | NO | 즉시 에스컬레이션 | 0 | 즉시 (CATEGORY E) |
| REP-E010 | YES | AR-Level 상향 요청 | 0 | 인간 판단 필요 |
| REP-E011 | NO | 즉시 에스컬레이션 | 0 | 즉시 (Self-evo 차단) |
| REP-E012 | NO | Kill Switch ON + 긴급 에스컬레이션 | 0 | 즉시 (롤백 실패) |

---

## 9. 에스컬레이션 페이로드 구조 (I-20 경유, R-01-8)

### 9.1 수리 실패 에스컬레이션

수리 실행이 실패하여 인간 개입이 필요할 때:

```json
{
  "escalation": {
    "type": "sdar_repair_failed",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer4.repair",
    "timestamp": "2026-04-13T12:05:00Z",
    "severity": "error"
  },
  "error": {
    "code": "REP-E001",
    "message": "Repair execution failed — pre-condition not met",
    "plan_ref": "plan_uuid-v4",
    "diagnosis_ref": "diag_uuid-v4",
    "ar_level_used": "AR-L2",
    "overall_status": "failed"
  },
  "context": {
    "selected_action": "retry_with_backoff",
    "risk_level": "LOW",
    "step_results": [
      {"step_order": 1, "action_id": "RA_003", "status": "failed", "error": "Connection refused"}
    ],
    "snapshot_id": null,
    "rollback_triggered": false,
    "lock_refs": ["L5", "L9"]
  },
  "recovery": {
    "attempted": ["pre_flight_check", "execute_step_1"],
    "all_failed": true,
    "recommended": "human_investigation",
    "estimated_impact": "Automatic repair failed — manual intervention required"
  },
  "trace_id": "uuid-v4"
}
```

### 9.2 승인 타임아웃 에스컬레이션

AR-L4 수리의 승인 요청이 600초 초과하여 자동 거부되었을 때:

```json
{
  "escalation": {
    "type": "sdar_repair_approval_timeout",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer4.repair",
    "timestamp": "2026-04-13T12:15:00Z",
    "severity": "warn"
  },
  "error": {
    "code": "REP-E006",
    "message": "Approval timeout — auto-denied after 600s (L10)",
    "plan_ref": "plan_uuid-v4",
    "diagnosis_ref": "diag_uuid-v4",
    "ar_level_used": "AR-L4"
  },
  "context": {
    "selected_action": "patch_code_hotfix",
    "risk_level": "HIGH",
    "approval_timeout_s": 600,
    "is_p2_domain": false,
    "snapshot_created": true,
    "snapshot_id": "snap_uuid-v4",
    "lock_refs": ["L10", "L16"]
  },
  "recovery": {
    "attempted": ["approval_request_sent", "waited_600s"],
    "all_failed": true,
    "recommended": "human_review_and_manual_approval",
    "estimated_impact": "HIGH risk repair pending — requires manual approval or alternative approach"
  },
  "trace_id": "uuid-v4"
}
```

### 9.3 롤백 실패 에스컬레이션 (CRITICAL — Kill Switch 연동)

스냅샷 복원 실패로 Kill Switch가 자동 활성화되었을 때:

```json
{
  "escalation": {
    "type": "sdar_repair_rollback_failed",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer4.repair",
    "timestamp": "2026-04-13T12:10:00Z",
    "severity": "critical"
  },
  "error": {
    "code": "REP-E012",
    "message": "Rollback failed — snapshot restore error, Kill Switch auto-activated (L14)",
    "plan_ref": "plan_uuid-v4",
    "diagnosis_ref": "diag_uuid-v4",
    "ar_level_used": "AR-L3"
  },
  "context": {
    "selected_action": "rollback_to_snapshot",
    "risk_level": "MEDIUM",
    "snapshot_id": "snap_uuid-v4",
    "rollback_strategy": "snapshot_restore",
    "rollback_timeout_s": 300,
    "kill_switch_activated": true,
    "kill_switch_reason": "SDAR_ROLLBACK_FAILED",
    "lock_refs": ["L8", "L12", "L14"]
  },
  "recovery": {
    "attempted": ["snapshot_restore", "kill_switch_activation"],
    "all_failed": true,
    "recommended": "immediate_human_intervention",
    "estimated_impact": "System state potentially inconsistent — SDAR halted, manual recovery required",
    "urgency": "CRITICAL"
  },
  "trace_id": "uuid-v4"
}
```

### 9.4 CATEGORY E 차단 에스컬레이션 (방어적 재확인)

Layer 4에서 CATEGORY E를 방어적으로 재확인하여 차단했을 때:

```json
{
  "escalation": {
    "type": "sdar_repair_category_e_block",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer4.repair",
    "timestamp": "2026-04-13T12:00:45Z",
    "severity": "critical"
  },
  "error": {
    "code": "REP-E009",
    "message": "CATEGORY E detected at Layer 4 — repair execution blocked (LOCK L15)",
    "plan_ref": "plan_uuid-v4",
    "diagnosis_ref": "diag_uuid-v4",
    "error_category": "E"
  },
  "context": {
    "category_e_rules": [
      "auto_repair_forbidden",
      "immediate_block",
      "audit_log_critical_immutable",
      "human_notification",
      "forensic_30day_retention"
    ],
    "repair_executed": false,
    "lock_ref": "L15",
    "layer4_defensive_check": true,
    "note": "Layer 3 should have blocked — this is a defensive re-check"
  },
  "recovery": {
    "attempted": ["category_e_block_executed"],
    "all_failed": false,
    "recommended": "human_security_review",
    "estimated_impact": "Security incident — repair execution refused, manual investigation required",
    "forensic_retention_days": 30
  },
  "trace_id": "uuid-v4"
}
```

---

## 10. Phase별 복구 전략

### 10.1 복구 흐름도

```
Phase 1 (현재) — Repair 자체 복구
  ├── REP-E001: 전제 조건 실패 → 수리 중단 + 에스컬레이션
  ├── REP-E002: 동시 수리 제한 → 30초 대기 후 재시도
  ├── REP-E003: 스냅샷 실패 → 수리 중단 + 에스컬레이션
  ├── REP-E004: L6 상한 → 수리 거부 + 1시간 대기
  ├── REP-E005: 승인 거부 → 수리 취소
  ├── REP-E006: 승인 타임아웃 → 자동 거부 + 에스컬레이션
  ├── REP-E007: Cooldown → 대기 후 재시도
  ├── REP-E008: Kill Switch → 즉시 중단 + 롤백
  ├── REP-E009: CATEGORY E → 즉시 차단 (L15)
  ├── REP-E010: reversibility 부적합 → AR-Level 상향 안내
  ├── REP-E011: Self-evo 차단 → 즉시 에스컬레이션 (L18)
  ├── REP-E012: 롤백 실패 → Kill Switch ON + 긴급 에스컬레이션
  └── 실패 시 → I-20 에스컬레이션

Phase 2 — Repair + Verification 연계 복구
  ├── Layer 5 검증 실패 → 자동 롤백 재시도
  ├── 스냅샷 관리 고도화 (증분 스냅샷, 병렬 복원)
  ├── 승인 워크플로 개선 (대리 승인, 자동 승인 조건 확장)
  └── 수리 실행 모니터링 메트릭 고도화

Phase 3 — 전체 Pipeline 통합 복구
  ├── 수리 이력 기반 자동 AR-Level 조정 제안
  ├── 수리 성공률 기반 Repair Action Catalog 최적화
  ├── 롤백 성공률 추적 + 롤백 전략 자동 선택
  └── 연속 실패 패턴 분석 → 선제적 에스컬레이션

Phase 4 — 거버넌스 완성
  ├── 수리 실행 KPI 자동 보고 (해결율, MTTR, 롤백율)
  ├── AR-Level별 성공/실패 통계 → AR-Level 정책 개선 피드백
  ├── 비용 영향 추적 → CostBudget 최적화 리포트
  └── S-8 거버넌스 통합 감사
```

### 10.2 다운그레이드 시 penalty 표

| 다운그레이드 상황 | 영향받는 단계 | penalty | 비고 |
|-----------------|-------------|---------|------|
| 스냅샷 생성 실패 (REP-E003) | Step 2 Snapshot | 수리 완전 중단 (MEDIUM/HIGH) | L8 필수 — 스냅샷 없이 수리 불가 |
| 승인 거부 (REP-E005) | ApprovalGate | 수리 취소, 대안 검색 없음 | 인간 결정 존중 |
| 승인 타임아웃 (REP-E006) | ApprovalGate | 자동 거부 + 에스컬레이션 | 10분 미응답 = 거부 |
| 단일 단계 실패 (on_failure=skip) | Step 3 Execute | 해당 단계 건너뛰기, 이후 단계 계속 | partial_success 가능 |
| 단일 단계 실패 (on_failure=abort) | Step 3 Execute | 전체 수리 중단 | overall_status=failed |
| 단일 단계 실패 (on_failure=rollback) | Step 3 Execute | 전체 수리 중단 + 롤백 | overall_status=rollback_executed |
| 동시 수리 Lock 실패 (REP-E002) | Step 1 Pre-flight | 30초 대기 후 재시도 1회 | L5 직렬화 |
| Cooldown 위반 (REP-E007) | Step 1 Pre-flight | 잔여 시간 대기 | L13 최대 60초 |
| Kill Switch 활성화 (REP-E008) | 모든 단계 | 즉시 중단 + 롤백 | SDAR 전체 정지 |
| 롤백 실패 (REP-E012) | 롤백 | Kill Switch 자동 ON | 최악 시나리오 — 긴급 인간 개입 |

---

## 11. 로깅 포맷 (R-01-7 structured JSON)

### 11.1 수리 시작 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.repair.started",
    "timestamp": "2026-04-13T12:05:00Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "plan_id": "plan_uuid-v4",
    "diagnosis_ref": "diag_uuid-v4",
    "ar_level": "AR-L2",
    "mode": "auto_safe",
    "risk_level": "LOW",
    "selected_action": "retry_with_backoff",
    "estimated_duration_s": 12,
    "requires_snapshot": false,
    "requires_approval": false,
    "current_concurrent_repairs": 0,
    "lock_refs": ["L5", "L9"]
  },
  "recovery": {
    "action": "repair_in_progress",
    "phase": "pre_flight_check"
  },
  "trace_id": "uuid-v4"
}
```

### 11.2 스냅샷 생성 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.repair.snapshot_created",
    "timestamp": "2026-04-13T12:05:02Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "plan_id": "plan_uuid-v4",
    "snapshot_id": "snap_uuid-v4",
    "targets": ["module_A", "module_B"],
    "size_bytes": 1048576,
    "duration_ms": 1500,
    "risk_level": "MEDIUM",
    "lock_ref": "L8"
  },
  "recovery": {
    "action": "proceed_to_approval_or_execute",
    "phase": "snapshot_complete"
  },
  "trace_id": "uuid-v4"
}
```

### 11.3 승인 요청 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.repair.approval_requested",
    "timestamp": "2026-04-13T12:05:03Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "plan_id": "plan_uuid-v4",
    "ar_level": "AR-L4",
    "risk_level": "HIGH",
    "approval_reason": "HIGH risk repair requires human approval",
    "is_p2_domain": false,
    "timeout_s": 600,
    "lock_refs": ["L10", "L16"]
  },
  "recovery": {
    "action": "awaiting_approval",
    "phase": "approval_gate",
    "timeout_at": "2026-04-13T12:15:03Z"
  },
  "trace_id": "uuid-v4"
}
```

### 11.4 에러 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.repair.error",
    "timestamp": "2026-04-13T12:05:15Z",
    "level": "ERROR",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": "REP-E003",
    "message": "Snapshot creation failed — repair cannot proceed (L8)",
    "recoverable": true,
    "snapshot_targets": ["module_A"],
    "backup_service_error": "Storage quota exceeded"
  },
  "context": {
    "plan_id": "plan_uuid-v4",
    "ar_level": "AR-L3",
    "risk_level": "MEDIUM",
    "step_reached": "snapshot",
    "repair_aborted": true,
    "lock_ref": "L8"
  },
  "recovery": {
    "action": "escalate_to_human",
    "escalation_type": "sdar_repair_failed",
    "escalation_id": "esc_uuid-v4"
  },
  "trace_id": "uuid-v4"
}
```

### 11.5 롤백 실행 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.repair.rollback_triggered",
    "timestamp": "2026-04-13T12:05:20Z",
    "level": "WARN",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": "Rollback triggered due to step failure",
    "recoverable": true
  },
  "context": {
    "plan_id": "plan_uuid-v4",
    "snapshot_id": "snap_uuid-v4",
    "rollback_strategy": "snapshot_restore",
    "failed_step": {
      "step_order": 2,
      "action_id": "RA_007",
      "status": "failed",
      "on_failure": "rollback"
    },
    "lock_refs": ["L8", "L12"]
  },
  "recovery": {
    "action": "restoring_snapshot",
    "phase": "rollback",
    "rollback_timeout_s": 300
  },
  "trace_id": "uuid-v4"
}
```

### 11.6 CATEGORY E 보안 감사 로그 구조 (LOCK L15 — 삭제 불가)

```json
{
  "log_event": {
    "event_type": "oc.sdar.repair.security_block",
    "timestamp": "2026-04-13T12:00:45Z",
    "level": "CRITICAL",
    "trace_id": "uuid-v4",
    "audit": {
      "immutable": true,
      "retention_days": 30,
      "lock_ref": "L15"
    }
  },
  "error": {
    "code": "REP-E009",
    "message": "CATEGORY E detected at Layer 4 — repair execution blocked (LOCK L15)",
    "recoverable": false,
    "error_category": "E"
  },
  "context": {
    "plan_id": "plan_uuid-v4",
    "diagnosis_ref": "diag_uuid-v4",
    "category_e_rules_applied": [
      "auto_repair_forbidden",
      "immediate_block",
      "audit_log_critical_immutable",
      "human_notification",
      "forensic_30day_retention"
    ],
    "repair_executed": false,
    "layer4_defensive_check": true
  },
  "recovery": {
    "action": "human_security_review_required",
    "escalation_id": "esc_uuid-v4",
    "auto_recovery_blocked": true,
    "reason": "LOCK L15 — CATEGORY E auto-repair absolutely forbidden"
  },
  "trace_id": "uuid-v4"
}
```

---

## 12. LOCK 참조 요약

| LOCK # | 항목 | 값 | 본 문서 적용 위치 |
|--------|------|-----|-----------------|
| **L1** | 5-Layer Pipeline 단계 정의 | Detection → Diagnosis → Prescription → Repair → Verification | §1 개요 — Layer 4 위치 |
| **L5** | MAX_CONCURRENT_REPAIRS | 1 (동시 수리 실행 최대 1건) | §4 동시 실행 제한 구현, §3.3 Pre-flight Check |
| **L8** | SNAPSHOT_MANDATORY | MEDIUM/HIGH risk 수리 전 스냅샷 필수 | §3.4 Snapshot 생성/복원, §2.5 AR-L3, §2.6 AR-L4 |
| **L9** | NOTIFICATION_MANDATORY | 모든 수리 활동 알림 필수 (AR-Level 무관) | §3.2 Step 6 Notification, §2.2~§2.6 전 AR-Level |

### 관련 LOCK (본 문서에서 참조만)

| LOCK # | 항목 | 값 | 참조 목적 |
|--------|------|-----|----------|
| L2 | 7-State Machine | REPAIRING 상태 관련 | Layer 4 = S4_REPAIRING 상태 동기 |
| L3 | 5-Gate 통합 아키텍처 | ApprovalGate Layer 4 적용 | §3.5 ApprovalGate 승인 요청 |
| L6 | MAX_AUTO_REPAIRS_PER_ISSUE_PER_HOUR | 3 | §3.3 Pre-flight Check L6 반복 제한 |
| L7 | MAX_CONCURRENT_SDAR_INSTANCES | 3 | §4.1 직렬화 보장 (L5와 스코프 차이 설명) |
| L10 | APPROVAL_TIMEOUT | 600초 (10분, 초과 시 자동 거부) | §3.5 승인 요청 절차 |
| L12 | ROLLBACK_TIMEOUT | 300초 (초과 시 인간 에스컬레이션) | §3.4 스냅샷 복원 타임아웃 |
| L13 | COOLDOWN_BETWEEN_REPAIRS | 60초 (동일 액션 반복 간 최소 대기) | §3.3 Pre-flight Check Cooldown 확인 |
| L14 | Kill Switch 트리거 조건 | 모든 RBAC 역할 활성화, ROLLBACK_FAILED 자동 ON | §3.3 Pre-flight, §3.4 롤백 실패 시 |
| L15 | CATEGORY E 자동수리 절대 금지 | 5규칙 적용 | §2.7 방어적 재확인 |
| L16 | P2 도메인 수리 인간 승인 필수 | AR-Level 무관 인간 승인 | §2.6 AR-L4 P2 도메인 검사 |
| L18 | Self-evo 원칙: 자동 적용 절대 금지 | 수리 결과 = "제안" | §2.8 Self-evo 차단 검증 |
| L19 | NEVER_AUTO 10항목 | 7개 불변구역 + 3개 운영금지 | Layer 3에서 사전 차단, Layer 4 입력 시 이미 필터링 |
| L20 | Gate 코드 공유 전략 (M-28) | BaseGate(ABC) → check(context) → GateResult | §3.5 ApprovalGate BaseGate 준수 |

---

## 13. Phase 2 테스트 시나리오

| # | 시나리오 | 기대 결과 | 검증 방법 |
|---|---------|----------|----------|
| T-REP-01 | AR-L0 수리 — 로그만 기록 | SDARRepairResult(ar_level_used="AR-L0", overall_status="success", step_results=[], follow_up_required=True) | 이벤트 + 알림 발생 확인, 실제 수리 미실행 확인 |
| T-REP-02 | AR-L1 수리 — 제안 전달 | SDARRepairResult(ar_level_used="AR-L1", notification_channel="both", follow_up_actions=["await_human_decision"]) | 사용자 제안 전달 + 이벤트 확인 |
| T-REP-03 | AR-L2 정상 수리 — LOW risk | SDARRepairResult(overall_status="success", snapshot_id=None, approval_id=None) | 6단계 순차 실행 + 이벤트 시퀀스 확인 |
| T-REP-04 | AR-L3 정상 수리 — MEDIUM risk + 스냅샷 | SDARRepairResult(snapshot_id=non-null, overall_status="success") + oc.sdar.repair.snapshot_created 이벤트 | 스냅샷 생성 + 수리 실행 + 알림 확인 (L8) |
| T-REP-05 | AR-L4 정상 수리 — HIGH risk + 승인 + 스냅샷 | SDARRepairResult(approval_status="approved", snapshot_id=non-null) | 스냅샷 → 승인 → 실행 → 알림 전체 흐름 확인 |
| T-REP-06 | 승인 거부 (REP-E005) | SDARRepairResult(overall_status="failed", approval_status="denied") | 수리 미실행 + 에스컬레이션 확인 |
| T-REP-07 | 승인 타임아웃 600초 (REP-E006) | SDARRepairResult(overall_status="failed", approval_status="timeout") | 600초 대기 후 자동 거부 확인 (L10) |
| T-REP-08 | 동시 수리 Lock 실패 (REP-E002) | 30초 대기 후 재시도, 실패 시 에스컬레이션 | L5 Lock 경합 시나리오 확인 |
| T-REP-09 | 스냅샷 생성 실패 (REP-E003) | 수리 중단 + 에스컬레이션 | MEDIUM/HIGH risk 스냅샷 실패 시 수리 불가 확인 (L8) |
| T-REP-10 | 롤백 실행 — 단계 실패 + snapshot_restore | SDARRepairResult(rollback_triggered=True, overall_status="rollback_executed") | 스냅샷 복원 + Kill Switch 미활성화 확인 |
| T-REP-11 | 롤백 실패 — Kill Switch 자동 활성화 (REP-E012) | Kill Switch ON + oc.sdar.kill_switch.activated 이벤트 | 롤백 실패 → Kill Switch 자동 ON + 긴급 에스컬레이션 확인 (L14) |
| T-REP-12 | CATEGORY E 방어적 차단 (REP-E009) | 수리 미실행 + CRITICAL 감사 로그 | Layer 4 방어 검증 + L15 5규칙 적용 확인 |
| T-REP-13 | Kill Switch 활성화 중 수리 진행 (REP-E008) | 즉시 중단 + 가능 시 롤백 + S0 전이 | Kill Switch 감시 + 중단 확인 (L14) |
| T-REP-14 | Cooldown 위반 60초 (REP-E007) | 잔여 시간 안내 + 대기 후 재시도 | L13 Cooldown 적용 확인 |
| T-REP-15 | L6 상한 도달 — 시간당 3회 초과 (REP-E004) | 수리 거부 + 에스컬레이션 | L6 카운팅 + 1시간 대기 확인 |

---

## 14. ISS-1 Layer 4 해결 확인

| 검증 항목 | 상태 | 근거 |
|----------|------|------|
| AR-L0~L4 전체 레벨별 실행 절차 포함 | **완료** | §2.2 AR-L0, §2.3 AR-L1, §2.4 AR-L2, §2.5 AR-L3, §2.6 AR-L4 |
| 공통 6단계 실행 흐름 포함 | **완료** | §3 전체 — Pre-flight Check → Snapshot → Execute → Monitor → Result Capture → Notification |
| `SDARRepairResult` 출력 스키마 완전 정의 | **완료** | §5 전체 필드 + SDARRepairStepResult 서브 모델 (SDAR_SPEC §8.3 대조 완료) |
| 스냅샷 필수 (L8) 명세 포함 | **완료** | §3.4 Snapshot 생성/복원 절차 상세 |
| 동시 실행 제한 (L5) 명세 포함 | **완료** | §4 MAX_CONCURRENT_REPAIRS=1 구현 상세 |
| 에러 코드 카탈로그 포함 | **완료** | §8 REP-E001~REP-E012 |
| LOCK L1, L5, L8, L9 매핑 명시 | **완료** | §12 LOCK 참조 요약 + 관련 LOCK 14건 |
| CATEGORY E 검증 포인트 (L15) | **완료** | §2.7 방어적 재확인 |
| Self-evo 자동적용 금지 검증 (L18) | **완료** | §2.8 Self-evo 차단 검증 |
| P2 도메인 인간 승인 (L16) + APPROVAL_TIMEOUT (L10) | **완료** | §3.5 ApprovalGate 절차 |
| ISS-1 Layer 4 | **해결** | 본 문서 전체 — Layer 4 L3 상세 정의 완성 |

---

*끝*
