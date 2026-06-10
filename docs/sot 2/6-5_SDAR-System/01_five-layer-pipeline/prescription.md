# Layer 3: PRESCRIPTION — 처방 생성 상세

> **도메인**: 6-5_SDAR-System / 01_five-layer-pipeline
> **Tier**: 6 (System-wide Components)
> **정본**: SDAR_SPEC **§2.4** (Layer 3 PRESCRIPTION), **§8.2** (SDARRepairPlan 스키마), **§6.1** (5-Gate 통합), **§3.1** (AR-Level 정의), **§5** (Repair Action Catalog)
> **Part2 출처**: §6.9 (L5412~L5419) — When/Where 정본
> **수정 정책**: Phase 변경 시 갱신 (종합계획서 §8.2)
> **LOCK 매핑**: L1 (5-Layer Pipeline 단계 정의), L3 (5-Gate 통합 아키텍처), L4 (AR-Level 정의 L0~L4+NEVER), L17 (비용 상한 내 수리)
> **Phase**: P1-3
> **생성일**: 2026-04-13
> **ISS 해결**: ISS-1 Layer 3

---

## 교차 참조 블록

| 참조 대상 | 관계 |
|----------|------|
| **SDAR_SPEC §2.4** | Layer 3 PRESCRIPTION 정의 정본 — 3단계 처방, SDARRepairPlan 스키마, 이벤트 |
| **SDAR_SPEC §8.2** | SDARRepairPlan 스키마 정본 — Pydantic v2 정의 (SDARRepairStep, SDARRollbackPlan, SDARRepairCandidate, SDARRepairPlan) |
| **SDAR_SPEC §6.1** | 5-Gate 통합 정본 — Layer 3 적용 Gate: PolicyGate, CostGate, EvidenceGate |
| **SDAR_SPEC §3.1** | AR-Level 정의 정본 — L0~L4+NEVER, VAMOS Autonomy Level 매핑 |
| **SDAR_SPEC §5** | Repair Action Catalog 정본 — RA_001~RA_014, RA_NEVER_01~RA_NEVER_10 |
| **SDAR_SPEC §9.5** | CATEGORY E 특별 규칙 — 자동수리 절대 금지 (LOCK L15) |
| **SDAR_SPEC §9.7** | 비용 상한 내 수리 — CostBudget 상한 (LOCK L17) |
| **Part2 §6.9** | When/Where 정본 — Phase별 참조 범위, 구현 위치, Gate 코드 공유 전략 |
| **D2.0-02 §7 I-25** | I-25 SDAR Engine 모듈 정의 |
| **01_five-layer-pipeline/_index.md** | P0 총괄 — Layer 3 개요 |
| **01_five-layer-pipeline/diagnosis.md** | Layer 2 산출물 — SDARDiagnosis 스키마 (Layer 3 입력) |
| **02_state-machine/_index.md** | Layer 3 = PRESCRIBING 상태(S3)와 동기화 |
| **04_self-diagnosis/gate_integration.md** | Layer 3→4 전환 시 5-Gate 통과 필수 (LOCK L3) — Phase 2 상세 |
| **AUTHORITY_CHAIN.md §4** | LOCK L1, L3, L4, L17 레지스트리 |

---

## 1. 개요

Layer 3 PRESCRIPTION은 SDAR 5-Layer Pipeline의 세 번째 단계로서, Layer 2 DIAGNOSIS가 출력한 `SDARDiagnosis`를 입력으로 받아 **수리 후보(Fix Candidates)**를 생성하고, 각 후보의 **위험도(Risk Level)**를 평가하며, 최적의 **수리 계획(Repair Plan)**을 수립하여 `SDARRepairPlan`을 출력한다. (LOCK L1: Detection → Diagnosis → Prescription → Repair → Verification)

### 1.1 핵심 요구사항

- 3단계 처방 프로세스: Fix Candidate Generation → Risk Assessment → Repair Plan Generation (SDAR_SPEC §2.4)
- 수리 후보 1~5개 생성, 우선순위 결정 (성공률 → 위험도 → 복구 시간 → 비용 영향)
- 위험도 평가: LOW / MEDIUM / HIGH / CRITICAL (SDAR_SPEC §2.4 Step 3-2)
- AR-Level 매핑: L0~L4 + NEVER, 현재 AR-Level 대비 자동 실행 가능 여부 판정 (LOCK L4)
- 5-Gate 통과 필수: PolicyGate, CostGate, EvidenceGate (LOCK L3 아키텍처)
- `SDARRepairPlan` 출력 스키마를 통한 표준화된 수리 계획 전달 (SDAR_SPEC §8.2)
- 비용 상한 내 수리 검증 (LOCK L17: CostBudget 상한, 일일 10% 초과 시 인간 승인)
- NOTIFICATION_MANDATORY (LOCK L9) — 모든 처방 활동 알림 필수
- CATEGORY E (보안 오류) 진단 수신 시 자동수리 후보 생성 금지 (LOCK L15)
- L6 상한 도달 시 자동수리 억제, 인간 에스컬레이션 권장

---

## 2. 3단계 처방 프로세스 상세 (SDAR_SPEC §2.4)

### 2.1 Step 3-1: Fix Candidate Generation (수리 후보 생성)

#### 알고리즘

```
FUNCTION generate_fix_candidates(
    diagnosis: SDARDiagnosis
) -> List[SDARRepairCandidate]:
    # 시간복잡도: O(C * A) where C = 오류 카테고리 매핑 액션 수, A = 후보 평가 비용
    # ABC 패턴: BaseCandidateGenerator(ABC).generate(diagnosis) → List[SDARRepairCandidate]
    # LOCK 참조: L1 (Pipeline 순서 — Layer 2 SDARDiagnosis 입력 보장)
    #            L4 (AR-Level 정의 — 후보별 required_ar_level 결정)
    #            L15 (CATEGORY E 자동수리 절대 금지)

    # 0. CATEGORY E 사전 차단 (LOCK L15)
    IF diagnosis.error_category == "E":
        LOG critical("CATEGORY E detected — auto-repair NEVER allowed", 
                     error_code=diagnosis.error_code)
        EMIT oc.sdar.prescription.no_fix_available(
            diagnosis_ref=diagnosis.diagnosis_id,
            reason="CATEGORY_E_NEVER_AUTO",
            lock_ref="L15"
        )
        RAISE PrescriptionBlockedError(PRESC_E006)

    # 1. L6 상한 확인 (SDARDiagnosis.previous_occurrences 참조)
    IF diagnosis.previous_occurrences >= 3:  # L6 상한 도달
        LOG warn("L6 limit reached — suppressing auto-repair",
                 error_code=diagnosis.error_code,
                 previous_occurrences=diagnosis.previous_occurrences)
        # 에스컬레이션 권장 플래그 설정, 후보 생성은 계속 (수동 실행용)
        l6_suppressed = True
    ELSE:
        l6_suppressed = False

    candidates = []

    # 2. Repair Action Catalog 검색 (SDAR_SPEC §5)
    applicable_actions = repair_action_catalog.search(
        error_category=diagnosis.error_category,
        error_code=diagnosis.error_code,
        risk_level_max=determine_max_risk(diagnosis)
    )

    # 3. 과거 수리 이력 조회 (I-16 Knowledge Search Engine 연동)
    repair_history = i16_knowledge_engine.query_repair_history(
        error_code=diagnosis.error_code,
        similar_patterns=diagnosis.pattern_match_ref,
        window=7 * 86400  # 7일
    )

    # 4. 후보 생성 (최소 1개, 최대 5개)
    FOR each action IN applicable_actions:
        # NEVER_AUTO 필터링
        IF action.min_ar_level == "NEVER_AUTO":
            CONTINUE

        # 성공률 계산
        success_rate = calculate_success_rate(action, repair_history)

        # 후보 구성
        candidate = SDARRepairCandidate(
            candidate_id=generate_uuid_v4(),
            rank=999,  # 임시값, 정렬 후 §2.1 Step 7에서 1~5 재부여 (ge=1 제약 충족)
            success_probability=success_rate,
            risk_level=action.risk_level,
            reversibility=action.reversibility,
            steps=build_repair_steps(action, diagnosis),
            side_effects=action.side_effects,
            estimated_total_duration_s=action.estimated_duration_s
        )
        candidates.append(candidate)

    # 5. 후보 없음 처리
    IF len(candidates) == 0:
        EMIT oc.sdar.prescription.no_fix_available(
            diagnosis_ref=diagnosis.diagnosis_id,
            reason="no_applicable_actions"
        )
        RAISE PrescriptionNoFixError(PRESC_E001)

    # 6. 우선순위 결정 (4대 기준)
    candidates.sort(key=lambda c: (
        -c.success_probability,           # 1. 성공률 (높을수록 우선)
        RISK_ORDER[c.risk_level],         # 2. 위험도 (낮을수록 우선)
        c.estimated_total_duration_s,     # 3. 복구 시간 (빠를수록 우선)
        estimate_cost(c)                  # 4. 비용 영향 (적을수록 우선)
    ))

    # 7. 최대 5개 제한 + rank 부여
    candidates = candidates[:5]
    FOR i, c IN enumerate(candidates):
        c.rank = i + 1

    EMIT oc.sdar.prescription.candidates_generated(
        diagnosis_ref=diagnosis.diagnosis_id,
        candidate_count=len(candidates),
        l6_suppressed=l6_suppressed
    )

    RETURN candidates
```

#### 우선순위 결정 기준 (SDAR_SPEC §2.4)

| 순위 | 기준 | 정렬 방향 | 설명 |
|------|------|----------|------|
| 1 | 성공률 (`success_probability`) | DESC | 과거 동일 패턴 수리 성공률 (I-16 이력) |
| 2 | 위험도 (`risk_level`) | ASC | LOW < MEDIUM < HIGH < CRITICAL |
| 3 | 복구 시간 (`estimated_total_duration_s`) | ASC | 예상 수리 소요 시간 |
| 4 | 비용 영향 (`estimated_cost`) | ASC | 수리로 인한 추가 비용 (L17 참조) |

#### 성공률 계산 공식

```
FUNCTION calculate_success_rate(
    action: RepairAction,
    history: List[RepairHistoryEntry]
) -> float:
    # 시간복잡도: O(H) where H = 이력 수
    
    relevant = [h FOR h IN history IF h.action_id == action.action_id]
    
    IF len(relevant) == 0:
        # 이력 없음 — 기본값 사용
        base_rates = {
            "LOW": 0.85,
            "MEDIUM": 0.65,
            "HIGH": 0.45,
            "CRITICAL": 0.25
        }
        RETURN base_rates[action.risk_level]
    
    # 이력 기반 계산
    successes = len([h FOR h IN relevant IF h.status == "success"])
    rate = successes / len(relevant)
    
    # 최근 3건에 가중 (시간 감쇠)
    recent = sorted(relevant, key=lambda h: h.completed_at, reverse=True)[:3]
    recent_successes = len([h FOR h IN recent IF h.status == "success"])
    recent_rate = recent_successes / len(recent)
    
    # 가중 평균: 전체 40% + 최근 60%
    weighted = rate * 0.4 + recent_rate * 0.6
    
    RETURN min(max(weighted, 0.01), 0.99)  # 0.01~0.99 범위 제한
```

#### RISK_ORDER 상수

```python
RISK_ORDER = {
    "LOW": 0,
    "MEDIUM": 1,
    "HIGH": 2,
    "CRITICAL": 3
}
```

### 2.2 Step 3-2: Risk Assessment (위험도 평가)

#### 알고리즘

```
FUNCTION assess_risk(
    candidate: SDARRepairCandidate,
    diagnosis: SDARDiagnosis
) -> RiskAssessmentResult:
    # 시간복잡도: O(S) where S = 수리 단계(step) 수
    # ABC 패턴: BaseRiskAssessor(ABC).assess(candidate, diagnosis) → RiskAssessmentResult
    # LOCK 참조: L4 (AR-Level 정의), L8 (SNAPSHOT_MANDATORY), L17 (비용 상한)

    # 1. 위험도 평가 기준 (SDAR_SPEC §2.4 Step 3-2)
    risk_factors = {
        "risk_level": candidate.risk_level,
        "reversibility": candidate.reversibility,
        "side_effects": candidate.side_effects,
        "estimated_downtime": candidate.estimated_total_duration_s,
        "required_ar_level": determine_required_ar_level(candidate)
    }

    # 2. reversibility 평가
    IF candidate.reversibility == "irreversible":
        # irreversible 액션은 자동수리 대상에서 제외
        risk_factors["risk_level"] = "CRITICAL"
        risk_factors["auto_execute_blocked"] = True
        risk_factors["block_reason"] = "irreversible action — manual execution only"
    ELIF candidate.reversibility == "partially_reversible":
        # partially_reversible은 스냅샷 필수
        risk_factors["requires_snapshot"] = True

    # 3. 부작용 평가
    IF len(candidate.side_effects) > 0:
        FOR effect IN candidate.side_effects:
            IF is_data_affecting(effect):
                risk_factors["data_risk"] = True
            IF is_service_affecting(effect):
                risk_factors["service_risk"] = True

    # 4. 비용 영향 평가 (LOCK L17)
    cost_impact = estimate_cost_impact(candidate, diagnosis)
    IF cost_impact.exceeds_daily_budget_10_percent:
        risk_factors["requires_human_approval"] = True
        risk_factors["cost_warning"] = "daily budget 10% exceeded — L17 approval required"

    # 5. 종합 위험도 판정
    final_risk = max_risk(
        candidate.risk_level,
        reversibility_risk(candidate.reversibility),
        side_effect_risk(candidate.side_effects),
        cost_risk(cost_impact)
    )

    EMIT oc.sdar.prescription.risk_assessed(
        diagnosis_ref=diagnosis.diagnosis_id,
        candidate_id=candidate.candidate_id,
        risk_level=final_risk,
        required_ar_level=risk_factors["required_ar_level"]
    )

    RETURN RiskAssessmentResult(
        candidate_id=candidate.candidate_id,
        final_risk_level=final_risk,
        risk_factors=risk_factors,
        requires_snapshot=(final_risk IN ["MEDIUM", "HIGH", "CRITICAL"]),
        requires_approval=(
            final_risk IN ["HIGH", "CRITICAL"]
            OR risk_factors.get("requires_human_approval", False)
        )
    )
```

#### 위험도 판정 매트릭스

| risk_level 입력 | reversibility | side_effects | 최종 위험도 | 스냅샷 필수 | 승인 필수 |
|----------------|---------------|--------------|-----------|-----------|---------|
| LOW | fully_reversible | 없음 | **LOW** | NO | NO |
| LOW | fully_reversible | 있음 | **LOW** | NO | NO |
| LOW | partially_reversible | 없음 | **MEDIUM** | YES (L8) | NO |
| MEDIUM | fully_reversible | 없음 | **MEDIUM** | YES (L8) | NO |
| MEDIUM | fully_reversible | 있음 | **MEDIUM** | YES (L8) | NO |
| MEDIUM | partially_reversible | 있음 | **HIGH** | YES (L8) | YES |
| HIGH | fully_reversible | 무관 | **HIGH** | YES (L8) | YES |
| HIGH | partially_reversible | 무관 | **HIGH** | YES (L8) | YES |
| 임의 | irreversible | 무관 | **CRITICAL** | YES (L8) | YES (수동만) |

### 2.3 Step 3-3: Repair Plan Generation (수리 계획 수립)

#### 알고리즘

```
FUNCTION generate_repair_plan(
    diagnosis: SDARDiagnosis,
    candidates: List[SDARRepairCandidate],
    risk_results: List[RiskAssessmentResult]
) -> SDARRepairPlan:
    # 시간복잡도: O(N * G) where N = 후보 수, G = Gate 수 (5)
    # ABC 패턴: BaseRepairPlanGenerator(ABC).generate(diagnosis, candidates) → SDARRepairPlan
    # LOCK 참조: L3 (5-Gate 통합 아키텍처), L4 (AR-Level), L8 (SNAPSHOT_MANDATORY)
    #            L17 (비용 상한)

    # 1. 후보별 Gate 검증 (LOCK L3 — 5-Gate 통합)
    gate_validated_candidates = []
    FOR each candidate, risk IN zip(candidates, risk_results):
        gate_result = run_layer3_gates(candidate, diagnosis, risk)

        IF gate_result.all_passed:
            candidate.gate_results = gate_result.details
            gate_validated_candidates.append(candidate)
        ELSE:
            LOG info("Candidate rejected by Gate",
                     candidate_id=candidate.candidate_id,
                     rejected_by=gate_result.rejected_gates)
            # 거부된 후보도 기록 (감사 추적용)

    # 2. Gate 통과 후보 없음 처리
    IF len(gate_validated_candidates) == 0:
        EMIT oc.sdar.prescription.no_fix_available(
            diagnosis_ref=diagnosis.diagnosis_id,
            reason="all_candidates_gate_rejected"
        )
        RAISE PrescriptionGateRejectError(PRESC_E003)

    # 3. 최적 후보 선택 (rank 1 = Gate 통과 + 최고 우선순위)
    selected = gate_validated_candidates[0]
    selected_risk = find_risk_result(risk_results, selected.candidate_id)

    # 4. AR-Level 판정
    required_ar = determine_required_ar_level(selected)
    current_ar = get_current_ar_level()
    can_auto = can_auto_execute(required_ar, current_ar)

    # L6 억제 적용
    IF diagnosis.previous_occurrences >= 3:
        can_auto = False  # L6 상한 → 자동수리 억제

    # 5. 전제 조건 / 사후 조건 / 롤백 계획 구성
    pre_conditions = build_pre_conditions(selected, diagnosis)
    post_conditions = build_post_conditions(selected, diagnosis)
    rollback_plan = build_rollback_plan(selected, selected_risk)

    # 6. SDARRepairPlan 생성
    plan = SDARRepairPlan(
        plan_id=generate_uuid_v4(),
        trace_id=diagnosis.trace_id,
        diagnosis_ref=diagnosis.diagnosis_id,
        created_at=now_iso8601(),
        candidates=gate_validated_candidates,
        selected_candidate_idx=0,
        required_ar_level=required_ar,
        current_ar_level=current_ar,
        can_auto_execute=can_auto,
        gate_results={
            "policy": selected.gate_results.get("policy", "allow"),
            "cost": selected.gate_results.get("cost", "normal"),
            "evidence": selected.gate_results.get("evidence", "sufficient")
        },
        pre_conditions=pre_conditions,
        post_conditions=post_conditions,
        rollback_plan=rollback_plan,
        requires_snapshot=selected_risk.requires_snapshot,
        requires_approval=selected_risk.requires_approval,
        approval_reason=(
            build_approval_reason(selected, selected_risk)
            IF selected_risk.requires_approval ELSE None
        )
    )

    EMIT oc.sdar.prescription.plan_ready(
        diagnosis_ref=diagnosis.diagnosis_id,
        plan_id=plan.plan_id,
        required_ar_level=required_ar,
        can_auto_execute=can_auto,
        candidate_count=len(gate_validated_candidates)
    )

    RETURN plan
```

---

## 3. AR-Level 매핑 로직 (LOCK L4)

### 3.1 AR-Level 결정 규칙 (SDAR_SPEC §3.1)

| AR-Level | 명칭 | 자동수리 범위 | risk_level 상한 | 매핑 기준 |
|----------|------|-------------|----------------|----------|
| **AR-L0** | MANUAL | 수리 안 함 | N/A | 수리 후보 있으나 실행 불가, 로그만 기록 |
| **AR-L1** | NOTIFY_ONLY | 진단 + 제안까지 | N/A | 후보 제시, 인간이 직접 실행 결정 |
| **AR-L2** | AUTO_SAFE | LOW risk 자동 수리 | LOW | RA_001~RA_005 (retry, restart, cache clear, model switch, rate limit) |
| **AR-L3** | AUTO_MODERATE | MEDIUM risk까지 | MEDIUM | RA_006~RA_010 (prompt patch, config update, API key rotate, snapshot rollback, log compress) |
| **AR-L4** | AUTO_AGGRESSIVE | HIGH risk까지 | HIGH | RA_011~RA_014 (code hotfix, schema migration, dependency reinstall, vector index rebuild) — **전제: ISS-8 3중 검증(gate_integration.md §5: AR-L4 성공률 ≥95% / 스냅샷 복원 100% / Kill Switch <1초) ALL PASS 필요, 1개라도 미충족 시 ar_level_cap=AR-L2** |
| **NEVER** | NEVER_AUTO | 절대 금지 | N/A | RA_NEVER_01~RA_NEVER_10 (7개 불변구역 + 3개 운영금지) |

### 3.2 required_ar_level 결정 알고리즘

```
FUNCTION determine_required_ar_level(
    candidate: SDARRepairCandidate
) -> Literal["AR-L2", "AR-L3", "AR-L4", "NEVER_AUTO"]:
    # ABC 패턴: BaseARLevelMapper(ABC).map(candidate) → AR-Level
    # LOCK 참조: L4 (AR-Level 정의)
    
    # 1. NEVER_AUTO 체크 (LOCK L15 + L19)
    FOR step IN candidate.steps:
        IF step.action_id.startswith("RA_NEVER"):
            RETURN "NEVER_AUTO"
    
    # 2. risk_level 기반 매핑
    level_map = {
        "LOW": "AR-L2",
        "MEDIUM": "AR-L3",
        "HIGH": "AR-L4",
        "CRITICAL": "NEVER_AUTO"  # CRITICAL = 수동만
    }
    
    RETURN level_map[candidate.risk_level]
```

### 3.3 자동 실행 가능 여부 판정

```
FUNCTION can_auto_execute(
    required: str,
    current: str
) -> bool:
    # VAMOS Autonomy Level에 의한 AR-Level 상한 제한 (SDAR_SPEC §3.2)
    # L0(FULL_MANUAL) → AR-L0 상한
    # L1(SUPERVISED) → AR-L2 상한 (기본값)
    # L2(SEMI_AUTO) → AR-L3 상한
    # L3(FULL_AUTO) → AR-L4 상한
    
    IF required == "NEVER_AUTO":
        RETURN False
    
    ar_order = {"AR-L0": 0, "AR-L1": 1, "AR-L2": 2, "AR-L3": 3, "AR-L4": 4}
    
    RETURN ar_order[current] >= ar_order[required]
```

---

## 4. 5-Gate 통과 조건 상세 (LOCK L3)

Layer 3에서 적용되는 Gate는 3개: **PolicyGate**, **CostGate**, **EvidenceGate** (SDAR_SPEC §6.1).
ApprovalGate는 Layer 4, SelfCheckGate는 Layer 5에서 적용.

### 4.1 Gate 통과 흐름 (SDAR_SPEC §6.1)

```
Layer 3 (PRESCRIPTION)
    │
    ├──▶ PolicyGate: 수리 액션이 정책 위반하는가?
    │       ├── deny → 해당 수리 후보 제거
    │       ├── restrict → 승인 필요 플래그 설정
    │       └── allow → 통과
    │
    ├──▶ CostGate: 수리로 추가 비용 발생하는가?
    │       ├── stop → 수리 포기 (비용 초과, L17)
    │       ├── downshift → 저비용 대안 검색
    │       └── normal → 통과
    │
    └──▶ EvidenceGate: 진단 근거가 충분한가?
            ├── insufficient → 추가 진단 필요 (Layer 2 재진입)
            └── sufficient → 통과
```

### 4.2 Gate별 통과/거부 기준

#### 4.2.1 PolicyGate (I-8 Policy Engine 연동)

```
FUNCTION check_policy_gate(
    candidate: SDARRepairCandidate,
    diagnosis: SDARDiagnosis
) -> GateResult:
    # ABC 패턴: BaseGate(ABC).check(context) → GateResult (LOCK L20 — Gate 코드 공유)
    # LOCK 참조: L3 (5-Gate 아키텍처), L16 (P2 도메인 수리 인간 승인 필수)
    
    # Non-goal 위반 여부 확인
    FOR step IN candidate.steps:
        policy_check = i8_policy_engine.validate(
            action=step.action_name,
            target_module=diagnosis.root_causes[0].related_modules,
            context={"error_category": diagnosis.error_category}
        )
        
        IF policy_check.violates_non_goal:
            RETURN GateResult(status="deny", reason=policy_check.violation_detail)
        
        IF policy_check.requires_approval:
            RETURN GateResult(status="restrict", reason=policy_check.restriction_detail)
    
    # P2 관련 수리 시 재확인 (LOCK L16)
    IF is_p2_domain_repair(candidate, diagnosis):
        RETURN GateResult(status="restrict", reason="P2 domain — human approval mandatory (L16)")
    
    RETURN GateResult(status="allow")
```

#### 4.2.2 CostGate (LOCK L17)

```
FUNCTION check_cost_gate(
    candidate: SDARRepairCandidate,
    diagnosis: SDARDiagnosis
) -> GateResult:
    # ABC 패턴: BaseGate(ABC).check(context) → GateResult (LOCK L20)
    # LOCK 참조: L3, L17 (비용 상한 CostBudget)
    
    estimated_cost = estimate_repair_cost(candidate)
    current_budget = cost_budget_service.get_remaining()
    daily_usage = cost_budget_service.get_daily_usage()
    daily_budget = cost_budget_service.get_daily_budget()  # V1: 40,000원/월 / 30일
    
    # 비용 상한 초과 확인
    IF estimated_cost > current_budget.remaining:
        RETURN GateResult(status="stop", reason="CostBudget exceeded (L17)")
    
    # 일일 10% 초과 확인 (L17) — 완전 차단이 아닌 인간 승인 요구
    IF (daily_usage + estimated_cost) > daily_budget * 0.10:
        RETURN GateResult(
            status="downshift",
            reason="Daily budget 10% exceeded — human approval required (L17)",
            requires_approval=True
        )
    
    # 모델 전환 시 추가 비용 확인 (switch_model_fallback)
    IF "switch_model_fallback" IN [s.action_name FOR s IN candidate.steps]:
        model_cost = estimate_model_switch_cost(candidate)
        IF model_cost > current_budget.remaining * 0.05:  # 잔여 예산 5% 초과
            RETURN GateResult(status="downshift", reason="Model switch cost warning")
    
    RETURN GateResult(status="normal")
```

#### 4.2.3 EvidenceGate (SDAR 전용)

```
FUNCTION check_evidence_gate(
    candidate: SDARRepairCandidate,
    diagnosis: SDARDiagnosis
) -> GateResult:
    # ABC 패턴: BaseGate(ABC).check(context) → GateResult (LOCK L20)
    # LOCK 참조: L3 (EvidenceGate — SDAR 전용 Gate)
    
    # 진단 근거 충분성 확인
    primary_cause = diagnosis.root_causes[diagnosis.primary_root_cause_idx]
    
    # confidence 임계값 확인
    IF primary_cause.confidence < 0.5:
        RETURN GateResult(
            status="insufficient",
            reason=f"Primary root cause confidence too low: {primary_cause.confidence} < 0.5"
        )
    
    # evidence 개수 확인 (최소 1개 근거 필요)
    IF len(primary_cause.evidence_refs) == 0:
        RETURN GateResult(
            status="insufficient",
            reason="No evidence references for primary root cause"
        )
    
    # HIGH/CRITICAL risk 수리 시 추가 검증 — confidence 0.7 이상 요구
    IF candidate.risk_level IN ["HIGH", "CRITICAL"]:
        IF primary_cause.confidence < 0.7:
            RETURN GateResult(
                status="insufficient",
                reason=f"HIGH/CRITICAL risk requires confidence >= 0.7, got {primary_cause.confidence}"
            )
    
    RETURN GateResult(status="sufficient")
```

### 4.3 Gate 코드 공유 인터페이스 (LOCK L20)

Part2 §6.9 (L5442-5450) 정의에 따라, 5-Gate는 BaseGate(ABC) 추상 클래스를 공유한다.

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel, Field
from typing import Optional, Literal


class GateResult(BaseModel):
    """Gate 검증 결과"""
    status: str = Field(..., description="allow/deny/restrict/stop/downshift/normal/insufficient/sufficient")
    reason: Optional[str] = Field(None, description="판정 사유")
    requires_approval: bool = Field(default=False, description="추가 승인 필요 여부")


class BaseGate(ABC):
    """Gate 추상 베이스 클래스 (LOCK L20 — Part2 §6.9 M-28)"""
    
    @abstractmethod
    def check(self, context: dict) -> GateResult:
        """Gate 검증 수행"""
        ...
    
    @property
    @abstractmethod
    def gate_name(self) -> str:
        """Gate 이름 (e.g., 'PolicyGate')"""
        ...
    
    @property
    def is_sdar_specific(self) -> bool:
        """SDAR 전용 Gate 여부"""
        return False


# Layer 3 적용 Gate 구현 (개요)
# - PolicyGate(BaseGate): is_sdar_specific=False (Gate 1, 공유)
# - CostGate(BaseGate): is_sdar_specific=False (Gate 3, 공유)
# - EvidenceGate(BaseGate): is_sdar_specific=True (Gate 2, SDAR 전용)
# 상세 구현: Phase 2 — 04_self-diagnosis/gate_integration.md
```

---

## 5. `SDARRepairPlan` 출력 스키마 (SDAR_SPEC §8.2)

### 5.1 스키마 정의 (Pydantic v2)

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional, Literal


class SDARRepairStep(BaseModel):
    """개별 수리 단계"""
    step_order: int = Field(..., ge=1, description="실행 순서")
    action_id: str = Field(..., description="Repair Action Catalog ID (e.g., RA_003)")
    action_name: str = Field(..., description="액션 명칭 (e.g., retry_with_backoff)")
    parameters: dict = Field(default_factory=dict, description="액션별 실행 파라미터")
    expected_duration_s: int = Field(..., description="예상 소요 시간 (초)")
    timeout_s: int = Field(..., description="타임아웃 (초)")
    on_failure: Literal["abort", "skip", "rollback"] = Field(
        default="rollback", description="실패 시 행동"
    )


class SDARRollbackPlan(BaseModel):
    """롤백 계획"""
    strategy: Literal["snapshot_restore", "reverse_actions", "manual"] = Field(
        ..., description="롤백 전략"
    )
    snapshot_ref: Optional[str] = Field(None, description="복원 대상 스냅샷 ID")
    reverse_steps: List[SDARRepairStep] = Field(
        default_factory=list, description="역순 수리 단계 (reverse_actions 전략 시)"
    )
    estimated_rollback_duration_s: int = Field(
        ..., description="예상 롤백 소요 시간 (초)"
    )


class SDARRepairCandidate(BaseModel):
    """수리 후보"""
    candidate_id: str = Field(..., description="후보 ID")
    rank: int = Field(..., ge=1, description="우선순위 (1이 최우선)")
    success_probability: float = Field(
        ..., ge=0.0, le=1.0, description="예상 성공률"
    )
    risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ..., description="위험도"
    )
    reversibility: Literal["fully_reversible", "partially_reversible", "irreversible"] = Field(
        ..., description="되돌림 가능 여부"
    )
    steps: List[SDARRepairStep] = Field(..., min_length=1, description="수리 단계")
    side_effects: List[str] = Field(default_factory=list, description="예상 부작용")
    estimated_total_duration_s: int = Field(..., description="전체 예상 소요 시간 (초)")


class SDARRepairPlan(BaseModel):
    """Layer 3 수리 계획 스키마 (SDAR_SPEC §8.2)"""
    plan_id: str = Field(..., description="수리 계획 고유 ID (UUID v4)")
    trace_id: str = Field(..., description="연관 trace_id")
    diagnosis_ref: str = Field(..., description="SDARDiagnosis.diagnosis_id 참조")
    created_at: str = Field(..., description="계획 수립 시각 (ISO8601 UTC)")

    # 수리 후보
    candidates: List[SDARRepairCandidate] = Field(
        ..., min_length=1, max_length=5, description="수리 후보 목록 (최대 5개)"
    )
    selected_candidate_idx: int = Field(
        default=0, description="선택된 후보 인덱스"
    )

    # 자율 수준 판정
    required_ar_level: Literal["AR-L2", "AR-L3", "AR-L4", "NEVER_AUTO"] = Field(
        ..., description="실행에 필요한 최소 AR-Level"
    )
    current_ar_level: str = Field(..., description="현재 시스템 AR-Level 설정")
    can_auto_execute: bool = Field(..., description="현재 AR-Level로 자동 실행 가능 여부")

    # Gate 결과
    gate_results: dict = Field(
        default_factory=dict,
        description="Gate 검증 결과 {policy: allow/deny, cost: normal/stop, evidence: sufficient}"
    )

    # 전제 조건
    pre_conditions: List[str] = Field(default_factory=list, description="실행 전제 조건")
    post_conditions: List[str] = Field(default_factory=list, description="수리 성공 판정 기준")

    # 롤백 계획
    rollback_plan: SDARRollbackPlan = Field(..., description="롤백 계획")

    # 스냅샷 필요 여부
    requires_snapshot: bool = Field(..., description="수리 전 스냅샷 필요 여부")

    # 승인 필요 여부
    requires_approval: bool = Field(
        ..., description="I-19 Approval 필요 여부"
    )
    approval_reason: Optional[str] = Field(
        None, description="승인 필요 사유"
    )

    model_config = ConfigDict(extra="forbid")
```

### 5.2 필드 상세

| 필드 | 타입 | 필수/선택 | 설명 |
|------|------|----------|------|
| `plan_id` | `str` (UUID v4) | **필수** | 수리 계획 고유 식별자 |
| `trace_id` | `str` (UUID v4) | **필수** | 연관 trace_id — 전체 파이프라인 추적용 |
| `diagnosis_ref` | `str` | **필수** | Layer 2 SDARDiagnosis.diagnosis_id 참조 |
| `created_at` | `str` (ISO8601 UTC) | **필수** | 계획 수립 시각 |
| `candidates` | `List[SDARRepairCandidate]` (1~5) | **필수** | 수리 후보 목록 |
| `selected_candidate_idx` | `int` | 선택 (기본 0) | 선택된 후보 인덱스 |
| `required_ar_level` | `Literal[...]` | **필수** | 실행에 필요한 최소 AR-Level |
| `current_ar_level` | `str` | **필수** | 현재 시스템 AR-Level |
| `can_auto_execute` | `bool` | **필수** | 자동 실행 가능 여부 |
| `gate_results` | `dict` | 선택 (기본 {}) | Gate 검증 결과 |
| `pre_conditions` | `List[str]` | 선택 (기본 []) | 실행 전제 조건 |
| `post_conditions` | `List[str]` | 선택 (기본 []) | 수리 성공 판정 기준 |
| `rollback_plan` | `SDARRollbackPlan` | **필수** | 롤백 계획 |
| `requires_snapshot` | `bool` | **필수** | 스냅샷 필요 여부 (L8) |
| `requires_approval` | `bool` | **필수** | I-19 Approval 필요 여부 |
| `approval_reason` | `Optional[str]` | 선택 | 승인 필요 사유 |

### 5.3 예시 (CATEGORY A — API Rate Limit)

```json
{
    "plan_id": "plan_550e8400-e29b-41d4-a716-446655440003",
    "trace_id": "550e8400-e29b-41d4-a716-446655440000",
    "diagnosis_ref": "diag_550e8400-e29b-41d4-a716-446655440001",
    "created_at": "2026-02-23T10:30:05Z",
    "candidates": [
        {
            "candidate_id": "cand_001",
            "rank": 1,
            "success_probability": 0.92,
            "risk_level": "LOW",
            "reversibility": "fully_reversible",
            "steps": [
                {
                    "step_order": 1,
                    "action_id": "RA_003",
                    "action_name": "retry_with_backoff",
                    "parameters": {"base_delay_s": 1, "max_retries": 3, "backoff_factor": 2},
                    "expected_duration_s": 12,
                    "timeout_s": 36,
                    "on_failure": "skip"
                },
                {
                    "step_order": 2,
                    "action_id": "RA_004",
                    "action_name": "switch_model_fallback",
                    "parameters": {"fallback_order": ["claude-3-5-sonnet", "ollama-llama3"]},
                    "expected_duration_s": 10,
                    "timeout_s": 30,
                    "on_failure": "abort"
                }
            ],
            "side_effects": ["temporary_latency_increase"],
            "estimated_total_duration_s": 22
        }
    ],
    "selected_candidate_idx": 0,
    "required_ar_level": "AR-L2",
    "current_ar_level": "AR-L2",
    "can_auto_execute": true,
    "gate_results": {
        "policy": "allow",
        "cost": "normal",
        "evidence": "sufficient"
    },
    "pre_conditions": ["API endpoint reachable", "Fallback model available"],
    "post_conditions": ["API response status 200", "Response latency < 5s"],
    "rollback_plan": {
        "strategy": "reverse_actions",
        "snapshot_ref": null,
        "reverse_steps": [
            {
                "step_order": 1,
                "action_id": "RA_004",
                "action_name": "switch_model_fallback",
                "parameters": {"restore_original": true},
                "expected_duration_s": 5,
                "timeout_s": 15,
                "on_failure": "abort"
            }
        ],
        "estimated_rollback_duration_s": 5
    },
    "requires_snapshot": false,
    "requires_approval": false,
    "approval_reason": null
}
```

---

## 6. 공통 자료 구조 정의 (세션 간 인터페이스)

### 6.1 Layer 2 → Layer 3 인터페이스

Layer 3은 Layer 2의 `SDARDiagnosis`를 입력으로 받는다. (diagnosis.md §3.2, §4 참조)

```python
# 입력: SDARDiagnosis (Layer 2 출력, SDAR_SPEC §8.1)
# - diagnosis_id: str (UUID v4)
# - trace_id: str (UUID v4)
# - signal_ref: str (SDARDetectionSignal.signal_id 참조)
# - diagnosed_at: str (ISO8601 UTC)
# - error_category: Literal["A", "B", "C", "D", "E"]
# - error_code: str
# - severity: Literal["info", "warn", "error", "critical"]
# - root_causes: List[SDARRootCause]
# - primary_root_cause_idx: int
# - impact: SDARImpactAssessment
# - diagnosis_duration_ms: int
# - pattern_match_ref: Optional[str]
# - previous_occurrences: int  ← L6 카운팅 기준점 (diagnosis.md §6)
```

### 6.2 Layer 3 → Layer 4 인터페이스

Layer 3은 `SDARRepairPlan`을 출력하며, Layer 4 REPAIR의 입력이 된다.

```python
# 출력: SDARRepairPlan (SDAR_SPEC §8.2 — 위 §5 상세)
# - plan_id: str (UUID v4)
# - trace_id: str (UUID v4)
# - diagnosis_ref: str
# - created_at: str (ISO8601 UTC)
# - candidates: List[SDARRepairCandidate] (1~5개)
# - selected_candidate_idx: int
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

### 6.3 Layer 3 내부 중간 자료 구조

```python
class RiskAssessmentResult(BaseModel):
    """위험도 평가 결과 (내부 중간 구조)"""
    candidate_id: str
    final_risk_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    risk_factors: dict
    requires_snapshot: bool
    requires_approval: bool


class RepairHistoryEntry(BaseModel):
    """과거 수리 이력 항목 (I-16 조회 결과)"""
    action_id: str
    action_name: str
    error_code: str
    status: Literal["success", "failed", "rollback"]
    completed_at: str  # ISO8601 UTC
    duration_ms: int
```

---

## 7. 이벤트 카탈로그 (SDAR_SPEC §2.4)

| 이벤트 타입 | 설명 | 발행 시점 | 포함 데이터 |
|------------|------|----------|-----------|
| `oc.sdar.prescription.started` | 처방 생성 시작 | Layer 3 진입 시 | diagnosis_ref, trace_id, start_time |
| `oc.sdar.prescription.candidates_generated` | 후보 생성 완료 | Step 3-1 완료 시 | diagnosis_ref, candidate_count, l6_suppressed |
| `oc.sdar.prescription.risk_assessed` | 위험도 평가 완료 | Step 3-2 완료 시 (후보별) | diagnosis_ref, candidate_id, risk_level, required_ar_level |
| `oc.sdar.prescription.plan_ready` | 수리 계획 수립 완료 | Step 3-3 완료 시 | diagnosis_ref, plan_id, required_ar_level, can_auto_execute, candidate_count |
| `oc.sdar.prescription.no_fix_available` | 적용 가능한 수리 없음 | 후보 없음 / Gate 전원 거부 / CATEGORY E 시 | diagnosis_ref, reason, lock_ref(CATEGORY E 시) |

---

## 8. 에러 코드 카탈로그 (DH-2: Layer 3)

| 에러 코드 | 심각도 | 설명 | 복구 가능 | 처리 |
|----------|--------|------|----------|------|
| `PRESC-E001` | ERROR | 후보 생성 실패 — 적용 가능한 수리 액션 없음 | YES | `oc.sdar.prescription.no_fix_available` 발행 + 인간 에스컬레이션 |
| `PRESC-E002` | ERROR | 위험도 평가 실패 — 후보 평가 중 오류 | YES | 해당 후보 제거, 나머지 후보로 계속 |
| `PRESC-E003` | ERROR | Gate 전원 거부 — 모든 후보 Gate 검증 실패 | YES | `oc.sdar.prescription.no_fix_available` 발행 + 인간 에스컬레이션 |
| `PRESC-E004` | WARN | CostGate downshift — 비용 초과로 저비용 대안 검색 | YES | 저비용 후보 재검색, 없으면 PRESC-E003 |
| `PRESC-E005` | WARN | EvidenceGate insufficient — 진단 근거 불충분 | YES | Layer 2 재진입 요청, 타임아웃 시 에스컬레이션 |
| `PRESC-E006` | CRITICAL | CATEGORY E 자동수리 차단 — LOCK L15 | NO | 즉시 에스컬레이션, 수리 계획 생성 거부 |
| `PRESC-E007` | WARN | L6 상한 도달 — 자동수리 억제 | YES | can_auto_execute=False, 수동 실행 가능 후보는 유지 |
| `PRESC-E008` | ERROR | Repair Action Catalog 조회 실패 | YES | 캐시된 카탈로그 사용, 실패 시 PRESC-E001 |
| `PRESC-E009` | ERROR | I-16 Knowledge Engine 연결 실패 | YES | 이력 없이 기본 성공률 적용, confidence 감소 |
| `PRESC-E010` | WARN | 비용 상한 10% 초과 경고 (L17) | YES | 인간 승인 요청 플래그 설정 |
| `PRESC-E011` | ERROR | 롤백 계획 수립 실패 | YES | rollback_plan.strategy="manual"로 설정 + 수동 검토 플래그 |
| `PRESC-E012` | CRITICAL | Kill Switch 활성화로 Prescription 중단 | NO | 즉시 중단, SDAR_S0_MONITORING(IDLE) 전이 (LOCK L14) |

### 8.1 예외 처리 정책 표

| error_code | recoverable | 처리 | 재시도 횟수 | 에스컬레이션 조건 |
|-----------|-------------|------|-----------|-----------------|
| PRESC-E001 | YES | 인간 에스컬레이션 | 0 | 즉시 (후보 없음) |
| PRESC-E002 | YES | 해당 후보 제거 | 1 | 모든 후보 평가 실패 |
| PRESC-E003 | YES | 인간 에스컬레이션 | 0 | 즉시 (Gate 전원 거부) |
| PRESC-E004 | YES | 저비용 대안 검색 | 2 | 대안 없음 |
| PRESC-E005 | YES | Layer 2 재진입 요청 | 1 | 재진단 후에도 불충분 |
| PRESC-E006 | NO | 즉시 에스컬레이션 | 0 | 즉시 (CATEGORY E) |
| PRESC-E007 | YES | 수동 모드 전환 | N/A | N/A |
| PRESC-E008 | YES | 캐시 사용 | 2 | 캐시도 실패 |
| PRESC-E009 | YES | 기본 성공률 적용 | 2 | 2회 연속 실패 |
| PRESC-E010 | YES | 인간 승인 요청 | N/A | N/A |
| PRESC-E011 | YES | 수동 롤백 설정 | 1 | 1회 실패 |
| PRESC-E012 | NO | 즉시 중단 | 0 | Kill Switch 해제 대기 |

---

## 9. 에스컬레이션 페이로드 구조 (I-20 경유, R-01-8)

### 9.1 후보 없음 에스컬레이션

Layer 3에서 적용 가능한 수리 후보가 없을 때:

```json
{
  "escalation": {
    "type": "sdar_prescription_no_fix",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer3.prescription",
    "timestamp": "2026-04-13T12:01:00Z",
    "severity": "error"
  },
  "error": {
    "code": "PRESC-E001",
    "message": "No applicable repair actions found for error",
    "diagnosis_ref": "diag_uuid-v4",
    "error_category": "C",
    "error_code": "SDAR_C03_SCHEMA_MISMATCH"
  },
  "context": {
    "diagnosis_severity": "error",
    "source_module": "I-6",
    "catalog_searched": true,
    "catalog_actions_evaluated": 24,
    "filter_reasons": {
      "category_mismatch": 18,
      "never_auto": 10,
      "risk_exceeds_max": 2
    },
    "i16_history_available": true,
    "past_similar_repairs": 0
  },
  "recovery": {
    "attempted": ["catalog_search", "history_search"],
    "all_failed": true,
    "recommended": "human_investigation",
    "estimated_impact": "No automatic repair possible — manual intervention required"
  },
  "trace_id": "uuid-v4"
}
```

### 9.2 Gate 전원 거부 에스컬레이션

모든 후보가 Gate 검증에 실패할 때:

```json
{
  "escalation": {
    "type": "sdar_prescription_gate_reject",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer3.prescription",
    "timestamp": "2026-04-13T12:01:05Z",
    "severity": "error"
  },
  "error": {
    "code": "PRESC-E003",
    "message": "All repair candidates rejected by Gate validation",
    "diagnosis_ref": "diag_uuid-v4",
    "candidates_evaluated": 3,
    "candidates_rejected": 3
  },
  "context": {
    "gate_rejections": [
      {"candidate_id": "cand_001", "gate": "PolicyGate", "status": "deny", "reason": "Non-goal violation"},
      {"candidate_id": "cand_002", "gate": "CostGate", "status": "stop", "reason": "CostBudget exceeded (L17)"},
      {"candidate_id": "cand_003", "gate": "EvidenceGate", "status": "insufficient", "reason": "confidence < 0.5"}
    ],
    "lock_refs": ["L3", "L17"]
  },
  "recovery": {
    "attempted": ["gate_validation_3_candidates"],
    "all_failed": true,
    "recommended": "human_intervention_with_gate_override",
    "estimated_impact": "Repair blocked by safety gates — manual approval or alternative needed"
  },
  "trace_id": "uuid-v4"
}
```

### 9.3 CATEGORY E 차단 에스컬레이션

CATEGORY E 진단 수신 시 (LOCK L15):

```json
{
  "escalation": {
    "type": "sdar_prescription_category_e_block",
    "escalation_id": "uuid-v4",
    "source": "sdar.layer3.prescription",
    "timestamp": "2026-04-13T12:00:30Z",
    "severity": "critical"
  },
  "error": {
    "code": "PRESC-E006",
    "message": "CATEGORY E diagnosis received — auto-repair plan generation blocked (LOCK L15)",
    "diagnosis_ref": "diag_uuid-v4",
    "error_category": "E",
    "error_code": "SDAR_E02_UNAUTHORIZED_ACCESS"
  },
  "context": {
    "diagnosis_severity": "critical",
    "source_module": "I-10",
    "category_e_rules": [
      "auto_repair_forbidden",
      "immediate_block",
      "audit_log_critical_immutable",
      "human_notification",
      "forensic_30day_retention"
    ],
    "repair_plan_generated": false,
    "lock_ref": "L15"
  },
  "recovery": {
    "attempted": ["category_e_block_executed"],
    "all_failed": false,
    "recommended": "human_security_review",
    "estimated_impact": "Security incident — repair plan generation refused, manual investigation required",
    "forensic_retention_days": 30
  },
  "trace_id": "uuid-v4"
}
```

---

## 10. Phase별 복구 전략

### 10.1 복구 흐름도

```
Phase 1 (현재) — Prescription 자체 복구
  ├── PRESC-E001: 후보 없음 → 인간 에스컬레이션
  ├── PRESC-E002: 위험도 평가 실패 → 해당 후보 제거 + 잔여 후보로 계속
  ├── PRESC-E003: Gate 전원 거부 → 인간 에스컬레이션
  ├── PRESC-E004: CostGate downshift → 저비용 대안 검색
  ├── PRESC-E005: EvidenceGate insufficient → Layer 2 재진입
  ├── PRESC-E006: CATEGORY E → 즉시 에스컬레이션 (LOCK L15)
  ├── PRESC-E007: L6 상한 → 수동 모드 전환
  ├── PRESC-E009: I-16 실패 → 기본 성공률
  └── 실패 시 → I-20 에스컬레이션

Phase 2 — Prescription + Diagnosis 연계 복구
  ├── Layer 2 재진단 결과 반영 (EvidenceGate insufficient 재시도)
  ├── Repair Action Catalog 동적 확장 (신규 액션 추가)
  ├── Gate 임계값 자동 조정 (PolicyGate/CostGate/EvidenceGate)
  └── 비용 예측 모델 개선 (CostGate 정확도)

Phase 3 — 전체 Pipeline 통합 복구
  ├── Layer 4/5 결과 → 후보 성공률 역추적 검증
  ├── 후보 우선순위 알고리즘 자동 튜닝
  ├── Gate 통과/거부 패턴 분석 → Gate 최적화
  └── 수리 이력 기반 신규 후보 자동 생성

Phase 4 — 거버넌스 완성
  ├── 처방 정확도 KPI 자동 보고
  ├── Gate 거부율 통계 → 정책 개선 피드백
  └── 비용 최적화 리포트 → CostBudget 조정 제안
```

### 10.2 다운그레이드 시 confidence/성공률 penalty 표

| 다운그레이드 상황 | 영향받는 단계 | penalty | 비고 |
|-----------------|-------------|---------|------|
| I-16 연결 실패 (PRESC-E009) | Step 3-1 후보 생성 | 성공률 -20% (기본값 적용) | 과거 이력 없이 기본 성공률 |
| Repair Action Catalog 조회 실패 (PRESC-E008) | Step 3-1 후보 생성 | 후보 수 제한 (캐시 기반) | 최신 카탈로그 미반영 |
| 후보 1건 위험도 평가 실패 (PRESC-E002) | Step 3-2 위험도 평가 | 해당 후보 제거 | 잔여 후보로 계속 |
| EvidenceGate insufficient (PRESC-E005) | Step 3-3 계획 수립 | 전체 처방 지연 (Layer 2 재진입) | 재진단 결과에 의존 |
| CostGate downshift (PRESC-E004) | Step 3-3 계획 수립 | 고비용 후보 제거 | 저비용 대안 검색 |
| L6 상한 도달 (PRESC-E007) | 전체 | can_auto_execute=False | 수동 실행 전환 |
| 롤백 계획 수립 실패 (PRESC-E011) | Step 3-3 계획 수립 | strategy="manual" | 수동 롤백 플래그 |

---

## 11. 로깅 포맷 (R-01-7 structured JSON)

### 11.1 Prescription 진행 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.prescription.started",
    "timestamp": "2026-04-13T12:00:10Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "diagnosis_ref": "diag_uuid-v4",
    "error_category": "A",
    "error_code": "SDAR_A04_API_429",
    "severity": "warn",
    "previous_occurrences": 1,
    "l6_limit_reached": false,
    "current_ar_level": "AR-L2"
  },
  "recovery": {
    "action": "prescription_in_progress",
    "phase": "candidate_generation"
  },
  "trace_id": "uuid-v4"
}
```

### 11.2 후보 생성 완료 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.prescription.candidates_generated",
    "timestamp": "2026-04-13T12:00:11Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "diagnosis_ref": "diag_uuid-v4",
    "candidate_count": 3,
    "catalog_actions_evaluated": 24,
    "i16_history_entries": 5,
    "candidates": [
      {"candidate_id": "cand_001", "rank": 1, "action_id": "RA_003", "risk_level": "LOW", "success_probability": 0.92},
      {"candidate_id": "cand_002", "rank": 2, "action_id": "RA_004", "risk_level": "LOW", "success_probability": 0.85},
      {"candidate_id": "cand_003", "rank": 3, "action_id": "RA_005", "risk_level": "LOW", "success_probability": 0.78}
    ],
    "l6_suppressed": false
  },
  "recovery": {
    "action": "proceed_to_risk_assessment",
    "phase": "risk_assessment"
  },
  "trace_id": "uuid-v4"
}
```

### 11.3 Gate 검증 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.prescription.gate_validation",
    "timestamp": "2026-04-13T12:00:12Z",
    "level": "INFO",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": null,
    "message": null,
    "recoverable": null
  },
  "context": {
    "diagnosis_ref": "diag_uuid-v4",
    "candidate_id": "cand_001",
    "gates_applied": ["PolicyGate", "CostGate", "EvidenceGate"],
    "gate_results": {
      "PolicyGate": {"status": "allow", "reason": null},
      "CostGate": {"status": "normal", "reason": null, "estimated_cost": 0},
      "EvidenceGate": {"status": "sufficient", "reason": null, "confidence": 0.92}
    },
    "all_passed": true,
    "lock_refs": ["L3", "L17", "L20"]
  },
  "recovery": {
    "action": "proceed_to_plan_generation",
    "phase": "plan_generation"
  },
  "trace_id": "uuid-v4"
}
```

### 11.4 에러 로그 구조

```json
{
  "log_event": {
    "event_type": "oc.sdar.prescription.error",
    "timestamp": "2026-04-13T12:00:15Z",
    "level": "ERROR",
    "trace_id": "uuid-v4"
  },
  "error": {
    "code": "PRESC-E003",
    "message": "All repair candidates rejected by Gate validation",
    "recoverable": true,
    "candidates_evaluated": 3,
    "candidates_rejected": 3
  },
  "context": {
    "diagnosis_ref": "diag_uuid-v4",
    "gate_rejections": [
      {"candidate_id": "cand_001", "gate": "CostGate", "status": "stop"},
      {"candidate_id": "cand_002", "gate": "PolicyGate", "status": "deny"},
      {"candidate_id": "cand_003", "gate": "EvidenceGate", "status": "insufficient"}
    ]
  },
  "recovery": {
    "action": "escalate_to_human",
    "escalation_type": "sdar_prescription_gate_reject",
    "escalation_id": "esc_uuid-v4"
  },
  "trace_id": "uuid-v4"
}
```

### 11.5 CATEGORY E 보안 감사 로그 구조 (LOCK L15 — 삭제 불가)

```json
{
  "log_event": {
    "event_type": "oc.sdar.prescription.security_block",
    "timestamp": "2026-04-13T12:00:30Z",
    "level": "CRITICAL",
    "trace_id": "uuid-v4",
    "audit": {
      "immutable": true,
      "retention_days": 30,
      "lock_ref": "L15"
    }
  },
  "error": {
    "code": "PRESC-E006",
    "message": "CATEGORY E diagnosis — repair plan generation blocked (LOCK L15)",
    "recoverable": false,
    "error_category": "E",
    "error_code": "SDAR_E02_UNAUTHORIZED_ACCESS"
  },
  "context": {
    "diagnosis_ref": "diag_uuid-v4",
    "source_module": "I-10",
    "category_e_rules_applied": [
      "auto_repair_forbidden",
      "immediate_block",
      "audit_log_critical_immutable",
      "human_notification",
      "forensic_30day_retention"
    ],
    "repair_plan_generated": false
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
| **L1** | 5-Layer Pipeline 단계 정의 | Detection → Diagnosis → Prescription → Repair → Verification | §1 개요 — Layer 3 위치 |
| **L3** | 5-Gate 통합 아키텍처 | PolicyGate → EvidenceGate → CostGate → ApprovalGate → SelfCheckGate | §4 — Gate 통과 조건 상세 (Layer 3: PolicyGate, CostGate, EvidenceGate) |
| **L4** | AR-Level 정의 (L0~L4+NEVER) | L0(0개) → L1(2개) → L2(5개) → L3(5개) → L4(4개) + NEVER(10개) | §3 — AR-Level 매핑 로직 |
| **L17** | 비용 상한 내 수리 | CostBudget 상한(V1: 40,000원/월), 일일 10% 초과 시 인간 승인 | §4.2.2 CostGate |

### 관련 LOCK (본 문서에서 참조만)

| LOCK # | 항목 | 값 | 참조 목적 |
|--------|------|-----|----------|
| L2 | 7-State Machine | PRESCRIBING 상태 관련 | Layer 3 = S3_PRESCRIBED 상태 동기 |
| L8 | SNAPSHOT_MANDATORY | MEDIUM/HIGH risk 스냅샷 필수 | §2.2 위험도 평가 — 스냅샷 필요 여부 결정 |
| L9 | NOTIFICATION_MANDATORY | 모든 활동 알림 필수 | §1.1 알림 요구사항 |
| L14 | Kill Switch 트리거 조건 | 모든 RBAC 역할 활성화 | PRESC-E012 Kill Switch 중단 |
| L15 | CATEGORY E 자동수리 절대 금지 | 5규칙 적용 | §2.1 CATEGORY E 사전 차단, §9.3 에스컬레이션 |
| L16 | P2 도메인 수리 인간 승인 필수 | AR-Level 무관 인간 승인 | §4.2.1 PolicyGate P2 재확인 |
| L19 | NEVER_AUTO 10항목 | 7개 불변구역 + 3개 운영금지 | §3.2 NEVER_AUTO 체크 |
| L20 | Gate 코드 공유 전략 (M-28) | BaseGate(ABC) → check(context) → GateResult | §4.3 Gate 코드 공유 인터페이스 |

---

## 13. Phase 2 테스트 시나리오

| # | 시나리오 | 기대 결과 | 검증 방법 |
|---|---------|----------|----------|
| T-PRESC-01 | 후보 생성: CATEGORY A(Infra) — LOW risk | SDARRepairPlan(candidates[0].risk_level="LOW", required_ar_level="AR-L2") | 후보 목록 + AR-Level 매핑 검증 |
| T-PRESC-02 | 후보 생성: CATEGORY B(Model) — MEDIUM risk | SDARRepairPlan(candidates[0].risk_level="MEDIUM", requires_snapshot=True) | 스냅샷 필요 여부 + 위험도 검증 |
| T-PRESC-03 | 후보 생성: CATEGORY D(Code) — HIGH risk | SDARRepairPlan(required_ar_level="AR-L4", requires_approval=True) | AR-Level + 승인 필요 여부 검증 |
| T-PRESC-04 | CATEGORY E 차단 (LOCK L15) | PRESC-E006 발생, 수리 계획 생성 거부, 에스컬레이션 페이로드 발송 | 에스컬레이션 + 감사 로그 + L15 규칙 적용 확인 |
| T-PRESC-05 | PolicyGate deny — Non-goal 위반 후보 제거 | 해당 후보 gate_results.policy="deny", 제거 후 잔여 후보로 계속 | Gate 결과 + 후보 목록 확인 |
| T-PRESC-06 | CostGate stop — 비용 초과 (L17) | PRESC-E004 또는 PRESC-E003, 비용 초과 사유 기록 | Gate 결과 + 비용 검증 |
| T-PRESC-07 | EvidenceGate insufficient — confidence < 0.5 | PRESC-E005, Layer 2 재진입 요청 | Gate 결과 + 재진단 요청 확인 |
| T-PRESC-08 | L6 상한 도달 (previous_occurrences >= 3) | PRESC-E007, can_auto_execute=False | L6 억제 + 수동 모드 확인 |
| T-PRESC-09 | Gate 전원 거부 — 3개 후보 모두 실패 | PRESC-E003 발생, 에스컬레이션 페이로드 발송 | 에스컬레이션 + Gate 거부 상세 확인 |
| T-PRESC-10 | I-16 연결 실패 중 후보 생성 | PRESC-E009 로깅, 기본 성공률 적용, confidence 감소 | 부분 동작 + 성공률 기본값 검증 |
| T-PRESC-11 | Kill Switch 활성화 중 Prescription 진행 | PRESC-E012 발생, 즉시 중단, S0 전이 | 중단 확인 + 상태 전이 검증 |
| T-PRESC-12 | 전체 3단계 정상 흐름 (CATEGORY A, LOW risk, AR-L2) | SDARRepairPlan 정상 생성, 5개 이벤트 순차 발행, Gate 전원 통과 | 전체 이벤트 시퀀스 + 스키마 검증 |
| T-PRESC-13 | 다중 후보 우선순위 정렬 (5개 후보, 혼합 risk) | candidates 순서: 성공률 DESC → risk ASC → 시간 ASC → 비용 ASC | 정렬 결과 검증 |
| T-PRESC-14 | AR-Level 불충분 — required=AR-L4, current=AR-L2 | can_auto_execute=False, requires_approval=True | AR-Level 비교 + 자동 실행 불가 확인 |
| T-PRESC-15 | 롤백 계획 수립: snapshot_restore 전략 | rollback_plan.strategy="snapshot_restore", snapshot_ref 포함 | 롤백 계획 구조 검증 |

---

## 14. ISS-1 Layer 3 해결 확인

| 검증 항목 | 상태 | 근거 |
|----------|------|------|
| 3단계 처방 전체 상세 (Candidate Generation, Risk Assessment, Plan Generation) | **완료** | §2.1 Step 3-1, §2.2 Step 3-2, §2.3 Step 3-3 |
| `SDARRepairPlan` 출력 스키마 완전 정의 | **완료** | §5 전체 필드 + 서브 모델(SDARRepairStep, SDARRollbackPlan, SDARRepairCandidate) |
| AR-Level L0~L4+NEVER 매핑 로직 포함 | **완료** | §3 전체 — 결정 규칙, 자동 실행 판정, VAMOS Autonomy Level 매핑 |
| 5-Gate 통과 조건 상세 포함 | **완료** | §4 전체 — PolicyGate, CostGate, EvidenceGate 통과/거부 기준 + Gate 코드 공유(L20) |
| 에러 코드 카탈로그 포함 | **완료** | §8 PRESC-E001~PRESC-E012 |
| LOCK L1, L3, L4 매핑 명시 | **완료** | §12 LOCK 참조 요약 + 관련 LOCK(L8, L9, L14, L15, L16, L17, L19, L20) |
| ISS-1 Layer 3 | **해결** | 본 문서 전체 — Layer 3 L3 상세 정의 완성 |

---

*끝*
