---
session: 04
sections: [4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8, 4.9, 5.1, 5.2, 5.3, 5.4, 5.5, 5.6]
status: complete
---

# §4. 5-Gate 검증 시스템

> **비유**: 공항에서 비행기를 타려면 "여권 확인 → 보안 검색 → 탑승권 확인 → 수하물 검사 → 최종 탑승 게이트"를 모두 통과해야 합니다. 하나라도 실패하면 비행기를 탈 수 없습니다. VAMOS도 마찬가지로, AI의 모든 응답이 **5개의 검증 관문(Gate)**을 통과해야만 사용자에게 전달됩니다.

이 장에서는 VAMOS가 AI의 응답을 **안전하고 신뢰할 수 있도록** 만드는 5단계 검증 시스템을 설명합니다.

---

## §4.1 Gate 시스템 개요 — 공항 보안 검색대 5단계

### 비유

공항의 보안 검색대를 떠올려 보세요:

```
[여권 확인]     →  [보안 검색]    →  [탑승권 확인]  →  [수하물 검사]  →  [최종 게이트]
 PolicyGate         CostGate        ApprovalGate      EvidenceGate     SelfCheckGate
 "이 사람이         "비용이          "허가를            "근거가          "품질이
  규칙에             예산 안에        받았는가?"         충분한가?"       충분한가?"
  맞는가?"           있는가?"
```

### 정의

**5-Gate 시스템**이란, VAMOS의 Condition & Decision Engine(조건 판단 및 의사결정 엔진, I-5 모듈)이 최종 판단을 내리기 전에 반드시 거쳐야 하는 **5개의 검증 관문**입니다. 이 구조는 **LOCK(변경 불가)**이며, 어떤 버전에서도 게이트를 건너뛰거나 순서를 바꿀 수 없습니다. [근거: D2.0-07 §5.2.1 LOCK]

### 5-Gate 파이프라인 (처리 순서)

```
PolicyGate → CostGate → ApprovalGate → EvidenceGate → SelfCheckGate → 응답 전달
```

| 순서 | Gate 이름 | 역할 | 비유 |
|------|----------|------|------|
| 1 | **PolicyGate** (정책 검증) | 규칙·정책 위반 여부 확인 | 여권/비자 확인 |
| 2 | **CostGate** (비용 검증) | 예산 한도 초과 여부 확인 | 보안 검색대 |
| 3 | **ApprovalGate** (승인 검증) | 사용자 승인 필요 여부 확인 | 탑승권 확인 |
| 4 | **EvidenceGate** (근거 검증) | 답변 근거의 충분성 확인 | 수하물 검사 |
| 5 | **SelfCheckGate** (자체 품질 검증) | 출력 품질·정확성 최종 확인 | 최종 탑승 게이트 |

[근거: D2.0-07 §5.2.1, D2.0-02 §2.3, §7.46]

### 핵심 원칙: Fail-Safe = "닫힘(Closed)" 원칙

> 게이트 검증에 오류가 발생하면, **"일단 허용"이 아니라 "일단 차단"**합니다. 이것을 **Fail-Safe(안전 실패)** 원칙이라 합니다. [근거: D2.0-07 §15.7.1]

### 핵심 요약 (3줄)
1. VAMOS의 모든 응답은 5개 Gate(PolicyGate → CostGate → ApprovalGate → EvidenceGate → SelfCheckGate)를 통과해야 합니다.
2. 이 순서와 구조는 **LOCK(변경 불가)**이며, 어떤 Gate도 건너뛸 수 없습니다.
3. 검증 오류 시 "일단 차단"하는 Fail-Safe 원칙을 따릅니다.

---

## §4.2 Gate 1: PolicyGate (정책 검증)

### 비유

공항에서 **여권과 비자**를 확인하는 단계입니다. 여권이 만료되었거나 비자가 없으면 어떤 이유로든 입국할 수 없습니다. PolicyGate는 "이 요청이 VAMOS의 규칙에 맞는가?"를 확인합니다.

### 역할

사용자의 요청이 VAMOS의 **절대 금지 사항(Non-goal)**과 **정책 규칙(RULE 1.3)**에 위배되지 않는지 검증합니다. 4-Layer Guardrails(4중 방어 체계)를 통해 입력·처리·출력 단계에서 각각 검사합니다. [근거: D2.0-07 §1, §1.1, §6.4]

### 4-Layer LLM Guardrails (4중 방어 체계)

> **주의**: 이 4-Layer LLM Guardrails(§9.1)는 **10계층 보안 아키텍처(§6.8)**와 별개의 체계입니다. 4-Layer는 LLM 입출력 필터링, 10계층은 시스템 전체 보안 아키텍처를 다룹니다. [근거: MASTER_SPEC §6.8, §9.1, v13 DELTA-009~010]

| Layer | 도구 | 검사 대상 | 역할 |
|-------|------|----------|------|
| Layer 1 | NeMo Guardrails | **입력** | 정책 기반 프롬프트 필터링, 주제 제한 |
| Layer 2 | Guardrails AI | **처리 중** | 출력 품질/안전성 검증 (타입 체크, 범위 제한) |
| Layer 3 | LlamaGuard | **출력** | 최종 유해성/정책 위반 분류 |
| Layer 4 | Post-Delivery Audit | **출력 이후** | 전달 후 비동기 감사 및 패턴 분석 (V2+) |

[근거: D2.0-07 §1.1 ADD-013~015]

### 판정값 (decision)

| 판정 | 의미 | 다음 행동 |
|------|------|----------|
| **deny** (차단) | 즉시 중단 — 정책 위반 확실 | 요청 거절 + 사유 안내. `OC_I5_POLICY_BLOCK` 코드 발생 |
| **restrict** (제한) | 일부 제한 필요 — 축소 실행 가능 | 안전한 범위 내 제한 실행 또는 승인 요청 |
| **allow** (허용) | 정책 통과 — 다음 Gate로 진행 | CostGate로 이동 |

[근거: D2.1-D7 §4.1 PolicyCheckSchema, D2.0-07 §6.4]

### 트리거 조건 (이런 경우 검사됨)

- 모든 요청에 대해 **항상** 실행 (예외 없음)
- IntentFrame(의도 프레임)의 `risk_flags.safety_sensitive = true` 인 경우 강화 검사
- 절대 금지 항목(Non-goal) 7가지에 해당하는 경우 즉시 deny [근거: D2.0-07 §1]

### 절대 금지 사항 (Non-goal) — 7가지 (**LOCK — 변경 불가**)

| 번호 | 금지 항목 | 설명 |
|------|----------|------|
| 2.1 | 실거래·주문·API 연동 | 실제 돈이 오가는 거래 금지 |
| 2.2 | 불법 행위·해킹·권한 상승 | 법 위반 행위 금지 |
| 2.3 | 의료·법률 단정적 판단 | "~해야 합니다"식 대리 결정 금지 |
| 2.4 | 민감 개인정보 장기 저장 | 주민번호 등 민감 정보 보관 금지 |
| 2.5 | 저작권·약관 위반 | 저작권 침해 콘텐츠 생성 금지 |
| 2.6 | P2 도메인 자동 생성 | 고위험 영역 자동 처리 금지 |
| 2.7 | 위험 기능 자동 실행 | 위험한 명령 자동 수행 금지 |

[근거: D2.0-07 §1]

### 민감 유형 탐지 (detected_sensitive_types)

| 코드 | 의미 |
|------|------|
| PII | 개인식별정보 (주민번호, 전화번호 등) |
| AUTH | 인증 정보 (비밀번호, API 키 등) |
| MEDICAL | 의료 정보 |
| LEGAL | 법률 정보 |

[근거: D2.1-D7 §4.1 PolicyCheckSchema]

### 실패 시 행동

- **deny**: 즉시 차단 → `FB_DENY_WITH_REASON` 폴백(대체 행동) 실행 → 사용자에게 사유 안내
- **restrict**: 축소 실행 → `FB_RESTRICT_GENERAL_INFO` 폴백 실행 → 일반적 정보만 제공
- Guardrails 시스템 장애 시: **차단(deny)** 기본 적용 (Fail-Safe 원칙)

[근거: D2.0-07 §15.7.1, D2.1-D2 §8]

### 핵심 요약 (3줄)
1. PolicyGate는 모든 요청을 4-Layer Guardrails(NeMo → Guardrails AI → LlamaGuard → Post-Delivery Audit)로 검사합니다.
2. 판정은 deny(차단) / restrict(제한) / allow(허용) 3가지이며, 절대 금지 7항목은 **LOCK**입니다.
3. 시스템 오류 시에도 "일단 차단"하는 Fail-Safe 원칙을 따릅니다.

---

## §4.3 Gate 2: CostGate (비용 검증)

### 비유

여행 전에 "내 예산이 얼마 남았지?" 확인하는 것과 같습니다. 예산의 80%를 쓰면 경고가 나오고, 100%를 쓰면 더 이상 쓸 수 없습니다. VAMOS도 AI 사용 비용을 실시간으로 감시합니다.

### 역할

AI 모델 호출에 드는 비용이 사전에 설정한 **일일 한도** 및 **월간 한도** 내에 있는지 확인합니다. 한도에 근접하면 저비용 모델로 자동 전환(다운시프트)하고, 초과하면 차단합니다. [근거: D2.0-07 §4.1, §4.2]

### 비용 한도 (**LOCK — 변경 불가**)

| 버전 | 일일 한도 | 월간 한도 | 모델 전략 |
|------|----------|----------|----------|
| **V1** (기본) | 1,300원 (~$1) | **40,000원** (~$30) | Mini 모델 90% 이상 사용 |
| **V2** (확장) | 3,100원 (~$2.3) | 93,000원 (~$70) | Mini 60-70% / Main 30-40% |
| **V3** (프로) | 8,900원 (~$6.7) | 266,000원 (~$200) | Main 중심, Flagship 활용 |

[근거: D2.0-07 §4.1 LOCK, D2.1-D7 §4.3 CostBudgetSchema]

### 판정값 (cost_gate)

| 판정 | 의미 | 다음 행동 |
|------|------|----------|
| **normal** (정상) | 예산 여유 있음 | 다음 Gate로 진행 |
| **downshift** (다운시프트) | 예산 80% 이상 소진 — 저비용 모델로 전환 | Mini 모델 강제 + Main/Flagship은 승인 필요 |
| **split** (분할) | 작업을 나눠서 비용 분산 | 단계별 실행으로 전환 |
| **stop** (중단) | 예산 100% 소진 — 실행 불가 | 즉시 차단 + 사용자 알림 |

[근거: D2.0-02 §3.2 정본, D2.0-02 §7.56]

### 다운시프트 임계값 (**LOCK — 변경 불가**)

```
예산 사용률 0% ────────── 80% ──────── 100%
               정상 구간     경고 구간     차단
               (normal)    (downshift)  (stop/deny)
                           ⚠ Mini 강제   🚫 자동 차단
```

| 임계값 | 동작 | 설명 |
|--------|------|------|
| **80%** (**LOCK**) | 경고 + Mini 강제 (force_mini) | Main/Flagship 사용은 Approval(승인) 필요 |
| **100%** (**LOCK**) | 자동 차단 (deny) | 승인 없이 즉시 차단 |

[근거: D2.0-07 §4.2 LOCK, D2.1-D7 §4.4 DownshiftSchema]

### 트리거 조건

- **일일 한도(daily_limit)**와 **월간 한도(monthly_limit)** 둘 다 상시 감시
- **먼저 도달하는 쪽**에서 트리거 발생 [근거: D2.0-07 §4.2]
- IntentFrame의 `risk_flags.cost_sensitive = true` 인 경우 I-8 Cost Manager가 강화 모니터링

### UI 알림 단계 (게이트 아님, 표시 전용)

| 사용률 | 알림 유형 |
|--------|----------|
| 50% | 정보성 안내 (참고용) |
| 80% | 경고 — Mini 전환 안내 |
| 95% | 긴급 안내 (빨간색, Mini 전용 전환 공지) |
| 100% | 차단 안내 + 예산 증액 옵션 제시 |

[근거: D2.0-07 §15.6.2]

### 실패 시 행동

- **80% 도달**: `FB_COST_DOWNSHIFT` 폴백 → Mini 모델로 자동 전환
- **100% 도달**: 즉시 차단 → 사용자에게 두 가지 선택지 제시:
  - (A) 예산 증액 요청 → OWNER 승인 필요 (RULE 1.3 §9.2)
  - (B) 현재 모드 유지 → 차단 상태 유지 또는 Mini 전용 우회
- 예산 자동 상향은 **절대 불가** — 반드시 사용자 승인 필요 [근거: D2.0-07 §4.3]

### 핵심 요약 (3줄)
1. CostGate는 일일/월간 비용 한도를 실시간 감시하며, V1/V2/V3 한도는 **LOCK**입니다.
2. 80% 도달 시 Mini 모델 강제 전환, 100% 도달 시 자동 차단 — 이 임계값도 **LOCK**입니다.
3. 예산 증액은 사용자(OWNER) 승인 없이 절대 자동 실행되지 않습니다.

---

## §4.4 Gate 3: ApprovalGate (승인 검증)

### 비유

병원에서 큰 수술 전에 **"수술 동의서"**에 서명해야 하는 것과 같습니다. 위험하거나 비용이 큰 작업은 AI가 혼자 결정하지 않고, 반드시 사용자의 **명시적 허가**를 받습니다.

### 역할

위험하거나 비용이 큰 작업에 대해 **사용자(Human)의 명시적 승인**을 요구합니다. 2단계 승인(계획 승인 → 실행 승인)을 지원하며, 역할(RBAC)에 따라 승인 권한이 다릅니다. [근거: D2.0-07 §3.1, §3.3, §6.2]

### 2단계 승인 구조

```
[계획 승인 (Plan Approval)]  →  [실행 승인 (Execute Approval)]
 "이 계획대로 해도 될까요?"       "지금 실행해도 될까요?"
```

| 단계 | 이름 | 설명 | 예시 |
|------|------|------|------|
| 1단계 | **Plan Approval** (계획 승인) | "이런 방식으로 할 예정입니다" 확인 | 코드 수정 계획 보여주기 |
| 2단계 | **Execute Approval** (실행 승인) | "지금 실행합니다" 최종 확인 | 실제 파일 수정 직전 |

[근거: D2.0-07 §3.1, D2.1-D7 §4.2 ApprovalSchema approval_stage: plan | execute]

### 승인 필요 작업 목록

| 작업 유형 | 기본 처리 | 승인 단계 |
|----------|----------|----------|
| 분석/진단/제안 (읽기) | allow (허용) | 없음 |
| 변경 적용 (쓰기) | restrict (제한) | 계획 승인 필요 |
| 자동 적용/자동 배포 | deny (기본 금지) | 실행 승인 필요 (예외적 허용 시) |
| 읽기 전용 도구 | allow (허용) | 없음 (비용 한도 내) |
| 쓰기/수정 도구 | restrict (제한) | 계획 승인 필요 (파괴적 = 실행 승인 추가) |
| 고위험 실행 | deny (기본 금지) | 실행 승인 필요 |

[근거: D2.0-07 §3.3]

### 판정값 (approval_status)

| 판정 | 의미 |
|------|------|
| **approved** (승인됨) | 사용자가 허가 → 다음 Gate로 진행 |
| **denied** (거부됨) | 사용자가 거부 → 요청 취소 |

[근거: D2.1-D7 §4.2 ApprovalSchema, D2.0-02 §3.2 — pending 제거 확정]

### 승인 범위 (scope)

| 범위 | 설명 |
|------|------|
| **domain** | 도메인 확장 (P1/P2 영역 진입) |
| **cost** | 비용 한도 변경 |
| **policy** | BASE RULE에 영향을 주는 정책 변경 |
| **external_action** | 외부 API/서버 명령 실행 |
| **storage** | 데이터 저장 (사전 확인 필수) |

[근거: D2.1-D7 §4.2, D2.0-07 §6.2]

### RBAC 역할별 승인 권한 (**LOCK — 변경 불가**)

| 역할 | 설명 | 계획 승인 | 실행 승인 | P2 승인 |
|------|------|----------|----------|---------|
| **OWNER** (소유자) | 시스템 소유자 — 모든 권한 | ✅ | ✅ | ✅ |
| **ADMIN** (관리자) | 위임 관리자 (V2+) | ✅ | ✅ (고위험 제외) | ❌ |
| **OPERATOR** (운영자) | 일반 작업자 | ✅ | ❌ (OWNER/ADMIN이 승인) | ❌ |
| **VIEWER** (열람자) | 읽기 전용 감사자 | ❌ | ❌ | ❌ |

[근거: D2.0-07 §3.6 LOCK MOD-023, D2.1-D7 §4.6 RBACRoleSchema]

### 자율 수준 (Autonomy Level) (**LOCK — 변경 불가**)

| 수준 | 이름 | 자동 실행 | 알림 필수 | 승인 필수 |
|------|------|----------|----------|----------|
| **L0** | 수동 (FULL_MANUAL) | ❌ | ✅ | ✅ (매 행동마다) |
| **L1** | 제안 (SUPERVISED) — **기본값** | ❌ | ✅ | ✅ (허용 목록 외) |
| **L2** | 반자동 (SEMI_AUTO) | ✅ (읽기/분석) | ✅ | ❌ (쓰기만 승인) |
| **L3** | 완전자동 (FULL_AUTO) | ✅ | ❌ | ❌ (정책 위반만 차단) |

- **기본값**: L1 (SUPERVISED) — 사용자가 제안을 보고 승인
- **수준 변경**: OWNER의 명시적 승인 필요
- **L3 예외**: P2 도메인, Non-goal, 비용 한도 초과는 L3에서도 **자동 실행 불가**

[근거: D2.0-07 §3.2.1 LOCK, D2.1-D7 §4.7 AutonomyLevelSchema]

### 트리거 조건

- PolicyGate에서 `restrict` 판정 + 승인 필요 표시
- IntentFrame의 `risk_flags.approval_maybe_required = true`
- 비용 80% 이상에서 Main/Flagship 모델 사용 요청
- P2 도메인(고위험) 작업 요청

### 실패 시 행동

- 승인 거부: 작업 취소 + 사유 기록
- **승인 대기 시간 초과**: 자동 거부(deny) 처리
  - 표준 승인: **10분** 무응답 시 자동 거부
  - 고위험 HITL (P2/안전 필터): **5분** 무응답 시 자동 거부
- 폴백: `FB_REQUIRE_APPROVAL` → 승인 요청 재시도

[근거: D2.0-07 §4.3.2]

### 핵심 요약 (3줄)
1. ApprovalGate는 위험하거나 비용이 큰 작업에 대해 2단계(계획 → 실행) 사용자 승인을 요구합니다.
2. 4가지 역할(OWNER/ADMIN/OPERATOR/VIEWER)에 따라 승인 권한이 다르며, 이 구조는 **LOCK**입니다.
3. 기본 자율 수준은 L1(제안 모드)이며, L3에서도 P2/Non-goal/비용 초과는 자동 실행 불가입니다.

---

## §4.5 Gate 4: EvidenceGate (근거 검증)

### 비유

법원에서 판사가 판결을 내리기 전에 **"증거가 충분한가?"**를 확인하는 것과 같습니다. 증거가 부족하면 판결을 보류하거나 추가 조사를 지시합니다. EvidenceGate는 AI의 답변에 **충분한 근거가 있는지** 확인합니다.

### 역할

I-2 Evidence Collector(근거 수집기)가 수집한 EvidencePack(근거 묶음)의 **커버리지(충족률)**와 **QoD(Quality of Data, 근거 품질 점수)**가 임계값 이상인지 검증합니다. 미달 시 재검색을 시도하거나 결론을 제한합니다. [근거: D2.0-02 §7.12~7.16, §7.46]

### 판정값

| 판정 | 의미 | 다음 행동 |
|------|------|----------|
| **PASS** (통과) | 근거 충분 — 확정 가능 | 다음 Gate(SelfCheckGate)로 진행 |
| **FAIL** (미달) | 근거 부족 — 단정 불가 | 재검색 루프 시도 또는 HOLD/ESCALATE |

[근거: D2.0-02 §7.46]

### QoD (Quality of Data) 점수

QoD는 **0.0~1.0 사이의 숫자**로, 수집한 근거의 품질을 나타냅니다. I-15 Evidence & QoD Manager가 계산합니다.

| 점수 범위 | 의미 | 행동 |
|----------|------|------|
| 0.8~1.0 | 높은 품질 — 신뢰 가능 | PASS |
| 0.6~0.8 | 보통 — 조건부 사용 | 주의 표시 후 PASS |
| 0.0~0.6 | 낮은 품질 — 단정 금지 | FAIL → 재검색 또는 HOLD |

[근거: D2.0-02 §7.16]

### 트리거 조건

- EvidencePack의 `coverage.sufficient = false`인 경우
- 개별 근거 항목의 `qod_score`가 임계값 미만인 경우
- 근거 항목이 0개인 경우 (정보 없음)

### 실패 시 행동

- **1차 시도**: `FB_RAG_RETRY_EXPAND` 폴백 → 검색 범위를 넓혀 재검색 (최대 N회)
- **재검색 후에도 미달**: Decision 결론 제한
  - **HOLD**: "추가 정보가 필요합니다" — 사용자에게 질문
  - **ESCALATE**: "이 질문은 전문가 확인이 필요합니다" — 상위 단계로 이관
- **핵심 규칙**: QoD 미달 시 **"~입니다"라고 단정하는 것은 금지** [근거: D2.0-02 §7.16 정책]

[근거: D2.0-02 §7.46, D2.1-D2 §8]

### 핵심 요약 (3줄)
1. EvidenceGate는 AI 답변의 근거(EvidencePack)가 충분한지 QoD 점수로 검증합니다.
2. 근거 부족 시 재검색을 시도하고, 그래도 미달이면 HOLD(보류) 또는 ESCALATE(이관)합니다.
3. QoD가 낮으면 "단정 금지" — 확실하지 않은 내용을 확정적으로 말하지 않습니다.

---

## §4.6 Gate 5: SelfCheckGate (자체 품질 검증)

### 비유

음식점에서 요리가 나가기 전에 **주방장이 마지막으로 맛을 보는 것**과 같습니다. 맛이 기준 미달이면 다시 만들고, 그래도 안 되면 "오늘은 이 메뉴를 제공할 수 없습니다"라고 안내합니다.

### 역할

AI가 생성한 최종 응답의 **사실 정확성, 정책 준수, 근거 충분성, 안전 필터 통과 여부**를 스스로 검증합니다. 도메인(P0/P1/P2)별로 다른 통과 기준을 적용합니다. [근거: D2.0-07 §5.2.1 LOCK]

### 도메인별 최소 점수 (**LOCK — 변경 불가**)

| 도메인 | 최소 점수 | 실패 시 행동 |
|--------|----------|-------------|
| **P0** (일반) | ≥ **70점** | 1회 재생성 → 그래도 실패: 경고 표시 후 전달 |
| **P1** (확장) | ≥ **75점** | 1회 재생성 → 그래도 실패: 사용자 확인 요청 |
| **P2** (고위험) | ≥ **80점** | 1회 재생성 → 그래도 실패: 자동 거부 + OWNER 알림 |

[근거: D2.0-07 §5.2.1 LOCK]

### 평가 항목

| 항목 | 설명 |
|------|------|
| 사실 일관성 (Factual Consistency) | 답변 내용이 서로 모순되지 않는가? |
| 정책 준수 (Policy Compliance) | Non-goal 등 정책 규칙을 위반하지 않는가? |
| 근거 충분성 (Evidence Sufficiency) | 주장에 대한 근거가 제시되었는가? |
| 안전 필터 통과 (Safety Filter Pass) | 유해하거나 부적절한 내용이 없는가? |

### 환각(Hallucination) 검증 기준

| 모순 비율 | 판정 | 행동 |
|----------|------|------|
| 0~5% | 정상 | 통과 |
| 5~15% | 주의 | 경고 로그 기록 |
| 15~30% | 환각 의심 | 사용자 경고 + 검증 요청 |
| 30% 이상 | 심각한 환각 | 차단 + 재생성 + `HALLUCINATION_DETECTED` 코드 |

[근거: D2.0-07 §15.9.4]

### 트리거 조건

- 모든 응답에 대해 **항상** 실행 (출력 생성 완료 후, 전달 직전)
- 상태 머신의 S5(OUTPUT_READY) → S6(SELF_CHECKED) 전이 시점

### 실패 시 행동

- **Soft Loop(소프트 루프)**: 자동으로 **1회만** 재생성 시도
- **2회 연속 실패**: 게이트 결과 우선 → 도메인별 처리
  - P0: 경고 표시 후 전달
  - P1: 사용자 확인 요청 후 전달
  - P2: 자동 거부(deny) + OWNER 알림
- **P2 특례**: Soft Loop를 강행하지 않고 **Policy/Cost/Approval Gate 결론을 우선** 적용

[근거: D2.0-02 §7.53-1~4, D2.0-07 §5.2.1]

### 설정 위치

```toml
# config.toml
[self_check]
p0_threshold = 70    # P0 일반 도메인
p1_threshold = 75    # P1 확장 도메인
p2_threshold = 80    # P2 고위험 도메인
```

- 임계값 **하향** 조정: OWNER 승인(Approval) 필요 [근거: D2.0-07 §5.2.1]

### 핵심 요약 (3줄)
1. SelfCheckGate는 AI 응답의 사실 정확성·정책 준수·근거·안전성을 최종 점검합니다.
2. P0 ≥ 70, P1 ≥ 75, P2 ≥ 80 최소 점수는 **LOCK**이며, 하향 시 OWNER 승인 필요합니다.
3. 실패 시 1회 재생성 후에도 미달이면 도메인별 차등 처리(경고/확인/거부)합니다.

---

## §4.7 Gate 우선순위: Policy > Cost > Approval > Evidence > SelfCheck

### 비유

소방서에서 화재 신고가 들어오면 **"인명 구조 > 화재 진압 > 재산 보호"** 순으로 우선순위를 정합니다. VAMOS도 Gate 간 결과가 충돌할 때 **정해진 우선순위**로 최종 결정을 내립니다.

### 우선순위 체계 (**LOCK — 변경 불가**)

```
가장 높음                                           가장 낮음
   ┃                                                 ┃
   ▼                                                 ▼
[1. RULE 1.3 BASE]  ──────────────────────────────────
   모든 정책의 기반. 다른 정책보다 항상 우선.

[2. Non-goal 절대 금지 (§1)]  ────────────────────────
   예외 없음. 어떤 승인이 있어도 무시 불가.

[3. Safety 정책 (PolicyGate)]  ───────────────────────
   안전 > 기능. Guardrails 4중 방어.

[4. Cost 정책 (CostGate)]  ──────────────────────────
   비용 > 편의. 예산 초과 불가.

[5. Approval 정책 (ApprovalGate)]  ──────────────────
   미승인 요청 차단.

[6. Evidence + SelfCheck]  ──────────────────────────
   근거·품질 검증. 위 규칙 범위 내에서만 작동.
```

[근거: D2.0-07 §15.14.2 LOCK]

### 충돌 시 해결 규칙

| 충돌 상황 | 우선 적용 | 결과 |
|----------|----------|------|
| PolicyGate=deny, CostGate=normal | PolicyGate | **REJECT** — 정책이 비용보다 우선 |
| PolicyGate=allow, CostGate=stop | CostGate | **REJECT** — 예산 초과로 실행 불가 |
| CostGate=normal, ApprovalGate=denied | ApprovalGate | **REJECT** — 승인 거부됨 |
| 모든 Gate=통과, SelfCheck=FAIL | SelfCheck | 재시도 후 도메인별 처리 |
| PolicyGate=restrict, ApprovalGate=approved | PolicyGate | **제한 실행** — 정책 범위 내에서만 |

**핵심 규칙**: `policy_gate가 항상 우선 (deny > restrict > allow)` [근거: D2.0-02 §3.3]

### 핵심 요약 (3줄)
1. Gate 우선순위는 Policy > Cost > Approval > Evidence > SelfCheck이며, **LOCK**입니다.
2. 상위 Gate가 차단하면 하위 Gate가 통과해도 의미가 없습니다.
3. 정책(Policy)이 가장 높고, 사용자 선호(Preference)는 모든 규칙 범위 내에서만 반영됩니다.

---

## §4.8 Gate 결과 조합 행동 분기표

Gate 5개의 결과 조합에 따라 VAMOS가 어떤 행동을 취하는지 정리한 표입니다.

### 주요 조합별 행동 분기

| PolicyGate | CostGate | ApprovalGate | EvidenceGate | SelfCheckGate | 최종 행동 | Decision 결론 |
|-----------|----------|-------------|-------------|--------------|----------|---------------|
| allow | normal | approved/불필요 | PASS | PASS | ✅ 정상 응답 전달 | **ACCEPT** |
| allow | normal | approved/불필요 | PASS | FAIL | 🔄 1회 재생성 시도 | ACCEPT (재시도 후) |
| allow | normal | approved/불필요 | FAIL | — | ⏸ 재검색 또는 보류 | **HOLD** |
| allow | downshift | — | PASS | PASS | ⚠ Mini 모델로 축소 응답 | ACCEPT (축소) |
| allow | stop | — | — | — | 🚫 비용 초과 차단 | **REJECT** |
| restrict | normal | 승인 대기 | — | — | ⏸ 사용자 승인 요청 | **HOLD** |
| restrict | normal | denied | — | — | 🚫 승인 거부됨 | **REJECT** |
| deny | — | — | — | — | 🚫 즉시 차단 | **REJECT** |
| allow | normal | approved | FAIL | — | ⬆ 전문가 이관 | **ESCALATE** |

[근거: D2.0-02 §3.2~3.3, D2.0-07 §5.2.1, §4.2, §3.3]

### 시스템 장애 시 행동 (Graceful Degradation)

| 장애 상황 | 기본 행동 | 폴백 | 로그 코드 |
|----------|----------|------|----------|
| NeMo Guardrails 장애 | 차단 (deny) | 정규표현식(Regex) 기본 필터 | `safety.filter.nemo_down` |
| Guardrails AI 장애 | 차단 (deny) | Layer 1/3만으로 운영 (축소) | `safety.filter.gai_down` |
| LlamaGuard 장애 | 차단 (deny) | 건너뛸 수 없음 → deny | `safety.filter.llamaguard_down` |
| PolicyCheck Gate 오류 | 전체 차단 | 수동 승인으로 전환 | `gate.policy.error` |
| CostBudget 조회 실패 | 차단 | 마지막 알려진 상태 사용 (5분 캐시) | `gate.cost.error` |

[근거: D2.0-07 §15.7.1]

### 핵심 요약 (3줄)
1. 5개 Gate가 모두 통과해야 ACCEPT(수락), 하나라도 차단이면 REJECT(거절) 또는 HOLD(보류)입니다.
2. 근거 부족 시 HOLD/ESCALATE, 승인 거부 시 REJECT, 정책 위반 시 즉시 REJECT입니다.
3. 시스템 장애 시에도 Fail-Safe 원칙에 따라 "일단 차단" 후 가능한 범위로 축소 운영합니다.

---

## §4.9 HITL 타이밍 & Gate Threshold Ledger — GAP-9

### HITL이란?

**HITL (Human-in-the-Loop, 사람 개입)**이란, AI가 혼자 결정하지 않고 **"잠깐, 이건 사람이 확인해야 해"**라고 판단하여 사용자에게 결정권을 넘기는 것입니다.

### SF-L01 HITL 트리거 목록

아래 상황에서 VAMOS는 자동으로 사용자에게 승인을 요청합니다:

| 트리거 조건 | 임계값 | 대기 시간 | 거부 시 폴백 |
|------------|--------|----------|-------------|
| **P2 도메인 작업 실행** | P2 활성 + 요청별 | **5분** | 작업 취소 + P2 비활성화 |
| **비용 80% 이상 호출** | cost_gate = downshift 진입 | **10분** | force_mini 다운시프트 적용 |
| **안전 필터 경계 판단** | Guardrails 점수 0.4~0.6 구간 | **5분** | deny + 사유 로깅 |
| **불확실한 결정** | Confidence < **50%** (MASTER_SPEC §5/§7.9 정본) | **5분** | HOLD + 사용자 확인 요청 |
| **L2→L3 자율 수준 상향** | AutonomyLevel 변경 요청 | **10분** | L2 유지 |
| **Non-goal 근접 요청** | PolicyCheck restrict 판정 | **5분** | deny + OWNER 알림 |

[근거: D2.0-07 §15.11 SF-L01]

### Gate Threshold Ledger (게이트 임계값 원장)

모든 Gate의 주요 임계값을 한곳에 정리한 원장입니다.

| Gate | 임계값 | 값 | 상태 | 변경 규칙 |
|------|--------|-----|------|----------|
| PolicyGate | 안전 필터 TPR 최소치 | ≥ 95% | **LOCK** | 하향 불가 |
| PolicyGate | Red Team 방어 최소치 | ≥ 90% | **LOCK** | 하향 불가 |
| CostGate | 경고 임계값 | 80% | **LOCK** | 변경 불가 |
| CostGate | 차단 임계값 | 100% | **LOCK** | 변경 불가 |
| SelfCheckGate | P0 최소 점수 | 70점 | **LOCK** | OWNER 승인 시만 하향 |
| SelfCheckGate | P1 최소 점수 | 75점 | **LOCK** | OWNER 승인 시만 하향 |
| SelfCheckGate | P2 최소 점수 | 80점 | **LOCK** | OWNER 승인 시만 하향 |
| EvidenceGate | QoD 충분 기준 | 0.6~0.8 | 설정 가능 | config.toml에서 조정 |

[근거: D2.0-07 §4.2, §5.2.1, §15.6.2, §15.11]

### Gate 임계값 변경 규칙 (분기별 감사)

| 규칙 | 설명 |
|------|------|
| **LOCK 임계값** | 비용 80%/100%, SelfCheck P0/P1/P2 점수 — 변경 시 OWNER 승인 + 감사 기록 필수 |
| **분기별 감사** | 매 분기 Gate 임계값의 적절성을 SDAR(자기 진단 감사 보고서)에서 검토 |
| **하향 금지 항목** | 안전 필터 TPR(≥95%), Red Team 방어(≥90%) — 절대 하향 불가 |
| **변경 이력** | 모든 임계값 변경은 `audit_trace_id`로 추적, 변경 사유 기록 필수 |

### PolicyCheck Self-Check (정책 자기 검증)

PolicyGate 자체가 올바르게 작동하는지를 검증하는 메커니즘입니다:

| 검증 항목 | 설명 |
|----------|------|
| **정책 규칙 정합성** | 적용된 정책 규칙이 현재 RULE 1.3과 일치하는지 확인 |
| **판정 일관성** | 동일 유형 요청에 대해 일관된 판정을 내리는지 검증 |
| **오탐/미탐 비율** | 잘못 차단(오탐)하거나 놓친(미탐) 비율을 모니터링 |
| **Guardrails 상태 확인** | 4-Layer Guardrails 각 레이어의 정상 작동 여부 점검 |
| **감사 연결** | 모든 PolicyCheck 결과가 `check_id`로 추적 가능한지 확인 |

[근거: D2.1-D7 §4.1 PolicyCheckSchema, D2.0-07 §5.2.1]

### 핵심 요약 (3줄)
1. HITL은 P2 작업, 비용 80%+, 안전 경계 판단 등 5가지 상황에서 자동 트리거됩니다.
2. Gate 임계값은 대부분 **LOCK**이며, 변경 시 OWNER 승인 + 분기별 감사가 필요합니다.
3. PolicyGate 자체도 자기 검증(Self-Check)을 통해 올바른 작동 여부를 확인합니다.

---

---

# §5. Decision 객체

> **비유**: 법원에서 재판이 끝나면 **"판결문"**이 나옵니다. 이 판결문에는 사건 요약, 증거 목록, 법적 근거, 최종 판결, 그리고 판사의 서명이 담겨 있습니다. 서명 이후에는 판결을 바꿀 수 없습니다. VAMOS의 **Decision 객체**도 이와 같은 역할을 합니다.

이 장에서는 VAMOS가 사용자의 요청에 대해 내린 **최종 판단 기록**인 Decision 객체의 구조를 설명합니다.

---

## §5.1 Decision이란? (비유: 재판 판결문)

### 비유

```
┌──────────────────────────────────────┐
│           📄 재판 판결문              │
│                                      │
│  사건번호: 2026가단12345             │  ← decision_id (결정 ID)
│  사건추적: TRC-001                   │  ← trace_id (추적 ID)
│                                      │
│  [사건 요약]                         │  ← IntentFrame (의도 프레임)
│   피고인의 의도, 배경, 제약 조건     │
│                                      │
│  [증거 목록]                         │  ← EvidencePack (근거 묶음)
│   증거 1, 증거 2, 증거 3...         │
│                                      │
│  [관문 통과 기록]                    │  ← Gates (5-Gate 결과)
│   정책✅ 비용✅ 승인✅ 근거✅ 품질✅  │
│                                      │
│  [최종 판결]                         │  ← conclusion (결론)
│   유죄 / 무죄 / 보류 / 상급심 이관  │     ACCEPT/REJECT/HOLD/ESCALATE
│                                      │
│  [판사 서명] 🔒                     │  ← locked = true (잠금)
│   서명 이후 판결 변경 불가           │     서명 후 결론 수정 불가
└──────────────────────────────────────┘
```

### 정의

**Decision 객체**란, VAMOS의 Condition & Decision Engine(I-5 모듈)이 사용자의 요청을 처리한 결과로 생성하는 **단일 판단 기록**입니다. 의도 분석, 근거 수집, 5-Gate 검증 결과를 모두 포함하며, 한 번 잠기면(locked=true) **결론을 바꿀 수 없습니다**(단일결정 원칙). [근거: D2.0-02 §3.2, D2.1-D2 §4.1 DecisionSchema]

### Decision 객체의 구성 요소

| 구성 요소 | 역할 | 비유 |
|----------|------|------|
| **IntentFrame** (의도 프레임) | 사용자의 의도·목표·제약 조건 기록 | 사건 요약서 |
| **EvidencePack** (근거 묶음) | 수집한 근거·출처·품질 점수 기록 | 증거 목록 |
| **Gates 결과** | 5개 Gate 통과 여부 기록 | 법적 절차 준수 확인 |
| **conclusion** (결론) | 최종 판단: ACCEPT/REJECT/HOLD/ESCALATE | 판결 주문 |
| **locked** (잠금) | 결론 확정 후 변경 불가 표시 | 판사 서명 |

[근거: D2.0-02 §3.2, D2.1-D2 §4.1]

### 핵심 요약 (3줄)
1. Decision 객체는 AI의 최종 판단을 기록하는 "판결문"과 같습니다.
2. IntentFrame(의도) + EvidencePack(근거) + Gates(검증) + conclusion(결론)으로 구성됩니다.
3. locked=true 이후에는 결론을 바꿀 수 없는 **단일결정 원칙**을 따릅니다.

---

## §5.2 IntentFrame — 필드 10개 상세

### 비유

병원에 가면 간호사가 **"어디가 아프세요? 언제부터요? 알레르기가 있으세요?"** 등을 물어봐서 **"접수 카드"**를 만듭니다. IntentFrame은 사용자의 요청을 이런 접수 카드처럼 **구조화된 형태**로 정리한 것입니다.

### 정의

**IntentFrame(의도 프레임)**은 I-1 Intent Detector(의도 감지기)가 사용자의 자연어 입력을 분석하여 생성하는 **구조화된 의도 기록**입니다. 10개의 핵심 필드로 구성됩니다. [근거: D2.0-02 §7.2~7.3]

### 10개 필드 상세

| # | 필드명 | 타입 | 설명 | 예시 |
|---|--------|------|------|------|
| 1 | **intent_id** | string | 의도 프레임 고유 식별자 | `if_01HZX9R1ABCDE` |
| 2 | **trace_id** | string | 전체 추적 ID (감사 연결용) | `trc_01HZX9R1ABCDE` |
| 3 | **user_goal** | string | 사용자가 원하는 것 (목표) | "Python으로 정렬 알고리즘 설명해줘" |
| 4 | **domain_hint** | P0\|P1\|P2 + 목록 | 위험 수준 분류 + 후보 도메인 | `P0, ["programming", "education"]` |
| 5 | **constraints** | object | 출력 제약 조건 | 형식: 마크다운, 반드시 포함: 코드 예시 |
| 6 | **task_type** | enum | 작업 유형 분류 | `explain` (설명), `code` (코딩), `plan` (계획) 등 |
| 7 | **risk_flags** | object | 위험 플래그 3가지 | 안전 민감, 승인 필요 여부, 비용 민감 |
| 8 | **ambiguity** | object | 모호성 정보 | 모호한지, 빠진 정보, 확인 질문 |
| 9 | **required_artifacts** | enum | 필요한 산출물 유형 | `doc`, `code`, `diagram` 등 |
| 10 | **emotion** | Optional | 감정 컨텍스트 (V1+ 확장) | 감지된 감정, 강도, 문화적 맥락 |

[근거: D2.0-02 §7.2~7.6]

### 주요 필드 세부 구조

#### constraints (제약 조건)
```
constraints: {
  format_constraints: "마크다운",          ← 출력 형식
  must_include: ["코드 예시", "설명"],    ← 반드시 포함할 항목
  must_not_include: ["외부 링크"]          ← 포함하면 안 되는 항목
}
```

#### risk_flags (위험 플래그)
```
risk_flags: {
  safety_sensitive: false,          ← 안전 관련 민감한 내용인가? (true면 PolicyGate 강화)
  approval_maybe_required: false,   ← 승인이 필요할 수 있는가? (true면 ApprovalGate 평가)
  cost_sensitive: true              ← 비용이 많이 드는 작업인가? (true면 CostGate 강화 모니터링)
}
```

#### ambiguity (모호성)
```
ambiguity: {
  is_ambiguous: true,                       ← 사용자의 요청이 모호한가?
  missing_slots: ["프로그래밍 언어", "난이도"],  ← 빠진 정보 (최대 3개)
  clarification_questions: [                 ← 확인 질문 (최대 3개)
    "어떤 프로그래밍 언어를 원하시나요?",
    "초급/중급/고급 중 어느 수준인가요?"
  ]
}
```

#### task_type 목록
| 값 | 의미 |
|-----|------|
| `explain` | 설명 |
| `plan` | 계획 수립 |
| `code` | 코드 작성 |
| `research` | 조사/리서치 |
| `summarize` | 요약 |
| `design` | 설계 |
| `debug` | 디버깅 |
| `other` | 기타 (분류 불가) |

[근거: D2.0-02 §7.2~7.6, D2.1-D2 §5.1 S13-A-009]

### 버전별 IntentFrame 확장

| 버전 | 추가 필드 | 설명 |
|------|----------|------|
| **V0** | 기본 10개 필드 | intent_id ~ required_artifacts |
| **V1** | emotion (감정), complexity (복잡도) | 감정 인식 + 적응형 사고 수준 추가 |
| **V2** | visual_context (시각 맥락), voice_emotion | 멀티모달 입력 지원 |
| **V3** | 문화적 맥락, 멀티모달 통합 | 문화 적응 + 종합 맥락 |

[근거: D2.0-02 §7.2-A, S7B-001, S7B-002]

### 핵심 요약 (3줄)
1. IntentFrame은 사용자의 의도를 10개 필드(ID, 목표, 도메인, 제약, 유형, 위험, 모호성, 산출물, 감정 등)로 구조화합니다.
2. 모호한 요청은 `ambiguity` 필드에서 빠진 정보와 확인 질문을 자동 생성합니다.
3. V0에서 V3까지 점진적으로 감정, 시각, 문화적 맥락 필드가 확장됩니다.

---

## §5.3 EvidencePack — 필드 6개 상세

### 비유

변호사가 재판에서 **"증거 파일"**을 제출하는 것과 같습니다. 각 증거마다 "어디서 가져왔는지(출처)", "얼마나 믿을 만한지(신뢰도)", "언제 확인했는지(시점)"가 기록되어 있습니다.

### 정의

**EvidencePack(근거 묶음)**은 I-2 Evidence Collector(근거 수집기, RAG 기반)가 사용자의 질문에 답하기 위해 수집한 **근거 자료의 모음**입니다. 6개의 핵심 필드로 구성됩니다. [근거: D2.0-02 §7.12~7.13]

### 6개 필드 상세

| # | 필드명 | 타입 | 설명 | 예시 |
|---|--------|------|------|------|
| 1 | **evidence_pack_id** | string | 근거 묶음 고유 식별자 | `evp_01HZX9R1ABCDE` |
| 2 | **trace_id** | string | 전체 추적 ID (감사 연결용) | `trc_01HZX9R1ABCDE` |
| 3 | **items[]** | array | 개별 근거 항목 배열 | 아래 세부 구조 참조 |
| 4 | **coverage** | object | 근거 충족률 정보 | `sufficient: true, gaps: []` |
| 5 | **citations_ready** | boolean | 인용 생성 준비 완료 여부 | `true` |
| 6 | **qod** (종합) | float | 전체 근거 품질 종합 점수 (0.0~1.0) | `0.85` |

[근거: D2.0-02 §7.12~7.16]

### items[] 개별 근거 항목의 구조

각 `items[]` 항목에는 다음 정보가 포함됩니다:

| 하위 필드 | 타입 | 설명 |
|----------|------|------|
| **source_type** | enum | 출처 유형: `memory`(기억) \| `doc`(문서) \| `web`(웹) \| `code`(코드) \| `log`(로그) |
| **source_ref** | string | 출처 참조 (URL, 문서 ID 등) |
| **excerpt_or_summary** | string | 핵심 내용 발췌 또는 요약 |
| **qod_score** | float | 해당 근거의 품질 점수 (0.0~1.0, I-19가 계산) |
| **timestamp** | datetime | 근거 수집 시점 (ISO 8601) |

[근거: D2.0-02 §7.12~7.16]

### coverage (충족률) 구조

```
coverage: {
  sufficient: true,          ← 근거가 충분한가? (EvidenceGate 판정 기준)
  gaps: ["최신 버전 정보"]    ← 부족한 영역 목록 (비어있으면 충분)
}
```

- `sufficient = true` → EvidenceGate **PASS**
- `sufficient = false` → EvidenceGate **FAIL** → 재검색 또는 HOLD

### 버전별 EvidencePack 확장

| 버전 | 추가 기능 | 설명 |
|------|----------|------|
| **V0** | 기본 6개 필드 | 기본 근거 수집 및 품질 평가 |
| **V1** | 인용 표기 ([1][2][3]) | 인라인 출처 표기 지원 |
| **V2** | 멀티소스 + 웹 검색 그라운딩 | 여러 출처 통합 + 실시간 웹 검색 |
| **V3** | 멀티모달 근거 + 신뢰도 점수 | 이미지/음성 근거 + 출처 신뢰도 |

[근거: D2.0-02 §7.12-A, S7B-006, S7B-013]

### 핵심 요약 (3줄)
1. EvidencePack은 6개 필드(ID, 추적ID, 근거 항목 배열, 충족률, 인용 준비, QoD 점수)로 구성됩니다.
2. 각 근거 항목에는 출처 유형, 참조, 내용 요약, 품질 점수, 수집 시점이 기록됩니다.
3. `coverage.sufficient = false`이면 EvidenceGate가 FAIL하여 재검색 또는 보류됩니다.

---

## §5.4 Decision Lock 원칙 — locked=true 후 변경 불가

### 비유

공증사무소에서 문서에 **도장을 찍으면** 더 이상 그 문서를 수정할 수 없습니다. 수정이 필요하면 새 문서를 만들어야 합니다. Decision의 `locked=true`도 같은 의미입니다.

### 정의

**Decision Lock(결정 잠금)**이란, Condition & Decision Engine(I-5)이 최종 결론을 내린 후 `locked=true`로 설정하여 **이후 어떤 단계에서도 결론을 변경할 수 없게 하는 원칙**입니다. 이것을 **"한 시점·한 컨텍스트·한 결론"** 원칙이라 합니다. [근거: D2.0-02 §3.1, §3.2]

### Lock 이후 허용/금지 사항

| 구분 | 가능 여부 | 예시 |
|------|----------|------|
| ✅ 실행 결과 추가 | 가능 | 실행 메타데이터, 결과 데이터 누적 |
| ✅ 검증 결과 추가 | 가능 | SelfCheck 점수, 감사 기록 추가 |
| ✅ 축소(Downshift) | 가능 | 비용 절감을 위한 모델 다운그레이드 |
| ❌ **결론 변경** | **불가** (**LOCK**) | ACCEPT → REJECT로 변경 불가 |
| ❌ **Gate 재평가** | **불가** | 이미 통과한 Gate를 다시 판정 불가 |
| ❌ **결정 업그레이드** | **불가** | HOLD → ACCEPT로 격상 불가 |

[근거: D2.0-02 §2.2, §3.1, §3.2]

### 상태 머신에서의 Lock 시점

```
S0 → S1 → S2 → [S3_DECISION_LOCKED] → S4 → S5 → S6 → S7 → S8
                       ↑
                  이 시점에서 locked=true
                  이후 결론 변경 불가 (LOCK)
```

- **S3 (DECISION_LOCKED)** 이후: 결론(conclusion) 고정
- 이후 단계(S4~S8): 실행·출력·검증·저장·전달만 수행
- 축소(downshift)만 허용: `FB_COST_DOWNSHIFT`, `FB_OUTPUT_MINIMAL` 등

[근거: D2.0-02 §2.2]

### DecisionSchema의 locked 필드

```json
{
  "name": "locked",
  "type": "boolean",
  "required": true,
  "description": "결정 잠금 여부(단일결정 원칙)"
}
```

- `locked = true`: 결론 확정, 이후 변경 불가 (**LOCK**)
- `locked = false`: 아직 결정 중 (Gate 평가 진행 중)

[근거: D2.1-D2 §4.1 DecisionSchema]

### 핵심 요약 (3줄)
1. `locked=true`가 되면 결론(ACCEPT/REJECT/HOLD/ESCALATE)은 **절대 변경 불가**입니다 (**LOCK**).
2. Lock 이후에는 결과 추가와 축소(downshift)만 허용되며, 업그레이드나 재평가는 금지됩니다.
3. 상태 머신의 S3(DECISION_LOCKED)에서 잠기며, "한 시점·한 컨텍스트·한 결론" 원칙을 따릅니다.

---

## §5.5 Decision 결론 4가지: ACCEPT / REJECT / HOLD / ESCALATE

### 비유

| 결론 | 비유 |
|------|------|
| **ACCEPT** | 재판에서 **"승소"** — 요청이 모든 검증을 통과하여 정상 실행 |
| **REJECT** | 재판에서 **"기각"** — 규칙 위반 또는 예산 초과로 거절 |
| **HOLD** | 재판에서 **"속행 (다음 기일)"** — 추가 정보나 승인 필요 |
| **ESCALATE** | 재판에서 **"상급심 이관"** — AI가 판단할 수 없어 전문가에게 넘김 |

### 각 결론 상세

### ACCEPT (수락)

| 항목 | 내용 |
|------|------|
| **의미** | 요청을 정상적으로 처리하여 응답 전달 |
| **발생 조건** | 5개 Gate 모두 통과 + SelfCheck PASS |
| **다음 행동** | 실행(S4) → 출력(S5) → 검증(S6) → 저장(S7) → 완료(S8) |
| **이벤트** | `oc.i5.decision.locked` (conclusion=ACCEPT) |

### REJECT (거절)

| 항목 | 내용 |
|------|------|
| **의미** | 요청을 거절하고 사유를 안내 |
| **발생 조건** | PolicyGate=deny, CostGate=stop, ApprovalGate=denied 중 하나 이상 |
| **다음 행동** | 사유 안내 + 폴백 실행 (FB_DENY_WITH_REASON 등) |
| **이벤트** | `oc.deny.blocked` + 해당 failure_code |

### HOLD (보류)

| 항목 | 내용 |
|------|------|
| **의미** | 추가 정보나 사용자 승인을 기다림 |
| **발생 조건** | EvidenceGate=FAIL (근거 부족), ApprovalGate=승인 대기 중, 모호성 해소 필요 |
| **다음 행동** | 사용자에게 질문 또는 승인 요청 전송 |
| **이벤트** | `oc.i5.approval.required` 또는 재검색 루프 시작 |

### ESCALATE (이관)

| 항목 | 내용 |
|------|------|
| **의미** | AI가 판단할 수 없는 영역 — 상위 권한자/전문가에게 이관 |
| **발생 조건** | 근거 재검색 실패 + P2 도메인, Non-goal 근접 판단 불가, 정책 경계 사례 |
| **다음 행동** | OWNER에게 알림 + 작업 일시 중단 |
| **이벤트** | 관련 failure_code + OWNER 알림 이벤트 |

[근거: D2.0-02 §3.2 정본, D2.1-D2 §4.1 DecisionSchema conclusion 필드]

### 결론 결정 흐름도

```
5-Gate 평가 완료
      │
      ├─ 모든 Gate 통과 + 충분한 근거 ──────→ ACCEPT ✅
      │
      ├─ PolicyGate=deny 또는 CostGate=stop ──→ REJECT ❌
      │   또는 ApprovalGate=denied
      │
      ├─ 근거 부족 또는 승인 대기 ───────────→ HOLD ⏸
      │
      └─ AI 판단 불가 + 고위험 ──────────────→ ESCALATE ⬆
```

### 버전별 결론 처리 차이

| 버전 | ACCEPT | REJECT | HOLD | ESCALATE |
|------|--------|--------|------|----------|
| **V0** | 기본 실행 | 사유 안내 | 재질문 | 기본 이관 |
| **V1** | + 인용 첨부 | + 폴백 전략 | + 재검색 루프 | + OWNER 알림 |
| **V2** | + 사고 과정 표시 | + 대안 제시 | + 웹 검색 보완 | + 위험도 분류 |
| **V3** | + 출처 신뢰도 | + 감사 추적 강화 | + 멀티모달 보완 | + 자동 전문가 매칭 |

[근거: D2.0-02 §3.2, §6.3]

### 핵심 요약 (3줄)
1. Decision의 결론은 ACCEPT(수락), REJECT(거절), HOLD(보류), ESCALATE(이관) 4가지뿐입니다.
2. 5-Gate 결과와 근거 충족률에 따라 결론이 결정되며, Policy deny는 항상 REJECT입니다.
3. HOLD는 추가 정보를 기다리고, ESCALATE는 AI가 판단할 수 없을 때 전문가에게 넘깁니다.

---

## §5.6 ResponseEnvelope — 5필드

### 비유

편지를 보낼 때 **봉투**에 편지지, 첨부 서류, 영수증, 참조 번호, 배송 기록을 함께 넣습니다. **ResponseEnvelope(응답 봉투)**는 VAMOS가 사용자에게 전달하는 최종 응답을 담은 "봉투"입니다.

### 정의

**ResponseEnvelope(응답 봉투)**는 VAMOS가 사용자에게 전달하는 **최종 출력의 최상위 구조**입니다. 상태 머신의 S8(DONE)에서 생성되며, 5개의 핵심 필드로 구성됩니다. [근거: D2.0-02 §5.1.1]

### 5개 필드 상세

| # | 필드명 | 역할 | 비유 |
|---|--------|------|------|
| 1 | **ANSWER** | 실제 답변 내용 | 편지지 (본문) |
| 2 | **EVIDENCE** | 근거 정보 요약 | 첨부 서류 (증거) |
| 3 | **SELF_CHECK** | 자체 검증 결과 | 품질 검사 도장 |
| 4 | **DECISION_REF** | Decision 참조 + Gate 결과 | 참조 번호 |
| 5 | **AUDIT** | 감사 추적 기록 | 배송 추적 기록 |

[근거: D2.0-02 §5.1.1]

### 각 필드 세부 구조

#### 1. ANSWER (답변)
```
ANSWER: {
  summary: "Python의 버블 정렬은...",     ← 짧은 결론/요약
  details: "상세 설명...",                ← 필요 시 상세 내용
  next_actions: ["퀵 정렬도 알아보기"]    ← 다음 행동 제안
}
```

#### 2. EVIDENCE (근거)
```
EVIDENCE: {
  coverage: 0.92,            ← 근거 충족률 (0~1)
  items: [...],              ← 개별 근거 항목 (EvidenceItem[])
  qod: 0.85                  ← QoD 종합 점수 (0~1)
}
```

#### 3. SELF_CHECK (자체 검증)
```
SELF_CHECK: {
  score: 0.88,               ← 검증 점수 (0~1)
  verdict: "PASS",           ← 판정: PASS | WARN | FAIL
  reasons: [],               ← 실패 사유 (있을 경우)
  retry_allowed: true        ← 재시도 가능 여부
}
```

#### 4. DECISION_REF (결정 참조)
```
DECISION_REF: {
  decision_id: "dec_01HZX9R1ABCDE",   ← 연결된 Decision ID
  gates: {                              ← Gate 평가 결과 요약
    policy: "PASS",                     ← PolicyGate 결과
    cost: "PASS",                       ← CostGate 결과
    evidence: "PASS"                    ← EvidenceGate 결과
  }
}
```

#### 5. AUDIT (감사)
```
AUDIT: {
  event_ids: ["evt_001", "evt_002"],       ← 발생한 LogEvent ID 목록
  failure_codes: [],                        ← 발생한 FailureCode 목록
  fallback_ids: []                          ← 적용된 Fallback 전략 ID 목록
}
```

[근거: D2.0-02 §5.1.1~5.1.3]

### UI에서 사용자에게 보이는 최소 필드

| 표시 항목 | 출처 필드 |
|----------|----------|
| 답변 요약 | `ANSWER.summary` |
| 근거 충족률 | `EVIDENCE.coverage` + `EVIDENCE.qod` |
| 검증 결과 | `SELF_CHECK.verdict` + `SELF_CHECK.score` |
| Gate 통과 여부 | `DECISION_REF.gates` |
| 이벤트 요약 | `AUDIT.event_ids` (요약) + `AUDIT.failure_codes` (요약) |

[근거: D2.0-02 §5.1.3]

### 핵심 요약 (3줄)
1. ResponseEnvelope는 ANSWER(답변) + EVIDENCE(근거) + SELF_CHECK(검증) + DECISION_REF(결정 참조) + AUDIT(감사)의 5개 필드로 구성됩니다.
2. 사용자에게는 답변 요약, 근거 충족률, 검증 결과 등 핵심 정보만 간략히 표시됩니다.
3. 모든 응답에는 Gate 통과 기록과 감사 추적 ID가 포함되어 투명성을 보장합니다.

---

## 검증 체크리스트

- [x] 5 Gate 모두 설명 — §4.2~§4.6에서 PolicyGate, CostGate, ApprovalGate, EvidenceGate, SelfCheckGate 상세 기술
- [x] Gate 우선순위 명시 — §4.7에서 Policy > Cost > Approval > Evidence > SelfCheck 순서 LOCK 명시
- [x] HITL 트리거 목록 — §4.9 SF-L01에서 5가지 트리거 조건, 대기 시간, 폴백 상세 기술
- [x] IntentFrame 10필드 — §5.2에서 intent_id ~ emotion 10개 필드 상세 기술
- [x] EvidencePack 6필드 — §5.3에서 evidence_pack_id ~ qod 6개 필드 상세 기술
- [x] Decision Lock LOCK 표시 — §5.4에서 locked=true 후 변경 불가 원칙 LOCK 표시
- [x] 4가지 결론 설명 — §5.5에서 ACCEPT/REJECT/HOLD/ESCALATE 각각의 발생 조건과 행동 상세 기술
- [x] 근거 SOT 참조 표기 — 모든 섹션에 [근거: D2.0-XX §X.X] 형태로 SOT 참조 표기 완료
