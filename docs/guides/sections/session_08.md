---
session: 08
sections: [7.18, 7.19, 7.20, 7.21, 7.22, 7.23, 7.24, 7.25]
status: complete
---

# §7. I-Series Part 3: I-18 ~ I-25 — ORANGE CORE 고급·자율 진화 모듈 상세

> **비유**: Part 1(I-1~I-8)이 두뇌의 **핵심 사고 영역**, Part 2(I-9~I-17)가 **관리·운영 영역**이었다면, Part 3(I-18~I-25)는 두뇌의 **자기 성찰·면역·진화 영역**입니다. 사람에 비유하면, I-18~I-25는 "스스로 더 나아지려고 노력하고(I-18), 위험한 결정은 반드시 허락을 받고(I-19), 몸이 아프면 자동으로 회복하고(I-20), 정보 출처의 질을 꾸준히 관리하고(I-21), 복잡한 프로젝트를 쪼개서 추적하고(I-22), 문서와 코드를 깔끔하게 정리하고(I-23), 모든 지식을 그물처럼 연결하고(I-24), 스스로 고장을 찾아 고치는(I-25) **자기 관리 시스템**"입니다.

[근거: D2.0-02 §0.1, §4.0, CLAUDE.md §6]

---

## §7.18 I-18 자기 진화 힌트 엔진 (Self-evo Engine)

### 비유
운동선수의 **경기 분석 코치**와 같습니다. 지난 경기(과거 대화) 기록을 분석해서 "이런 전략이 잘 먹혔고, 이런 건 실패했다"는 **힌트(조언)**를 추출합니다. 단, 코치는 조언만 하고 실제 변경은 선수(사용자)의 승인이 있어야 적용됩니다.

### 목적
VAMOS가 과거 성공/실패 로그(I-9 기록)를 분석하여 "무엇이 잘 먹히는지" 패턴을 추출하고, 개선 힌트를 **제안만** 합니다. 절대로 자동 적용하지 않으며, 사용자 승인 후에만 반영됩니다. 이것이 VAMOS의 '자기 진화(Self-evolution)' 철학의 핵심입니다. [근거: D2.0-02 §7.87, CLAUDE.md §7.5]

### 구조도

```
과거 대화 로그 (I-9)
        ↓
┌──────────────────────────────────────┐
│       I-18 Self-evo Engine           │
│  ┌────────────────────────────────┐  │
│  │ 1. mine_patterns(logs)        │  │  → 성공/실패 패턴 추출
│  │ 2. rank_hints(hints)          │  │  → 우선순위 정렬
│  └────────────────────────────────┘  │
│                                      │
│  [변경 가능 영역 — 6가지]            │
│  ┌────────────────────────────────┐  │
│  │ ✅ 프롬프트 (Prompt)           │  │
│  │ ✅ 도구 조합 (Tool Mix)        │  │
│  │ ✅ 메모리 관리 (Memory Mgmt)   │  │
│  │ ✅ 출력 포맷 (Output Format)   │  │
│  │ ✅ 워크플로우 순서 (WF Order)  │  │
│  │ ✅ 모델 선택 (Model Selection) │  │
│  └────────────────────────────────┘  │
│                                      │
│  [변경 불가 영역 — 7가지] 🔒 LOCK   │
│  ┌────────────────────────────────┐  │
│  │ 🚫 정체성 (Identity)          │  │
│  │ 🚫 Non-goal (7대 금지)        │  │
│  │ 🚫 법규·윤리 (Legal/Ethics)    │  │
│  │ 🚫 비용 상한 (Cost Ceiling)    │  │
│  │ 🚫 승인 구조 (Approval Flow)   │  │
│  │ 🚫 P0 도메인                   │  │
│  │ 🚫 P2 생성 활성화              │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
        ↓
  hints[] (개선 힌트 목록) → 사용자 승인 필요
```

### ⚠️ LOCK — 7가지 불변 구역 + 3가지 운영 금지 = 총 10가지 (NEVER_AUTO)

> **이 10가지 영역은 Self-evo가 절대 변경할 수 없습니다. NEVER_AUTO (frozenset 강제) 규칙이 적용됩니다.** [근거: v13 DELTA-005~006]

**[7개 불변 구역]**

| # | 불변 영역 | SOT 키 | 설명 |
|---|----------|--------|------|
| 1 | **안전 규칙** | `modify_safety_rules` | RULE 1.3 안전 규칙 보호 |
| 2 | **비용 상한** | `change_cost_ceiling` | V1 ₩40K / V2 ₩93K / V3 ₩266K (ABSOLUTE LOCK) |
| 3 | **승인 흐름** | `alter_approval_flow` | 승인 절차/흐름 자체를 수정하는 것 |
| 4 | **Non-goal (7대 금지)** | `modify_non_goals` | 절대 하지 않을 것들 (자율 실행, 감정 조작 등) |
| 5 | **감사 형식** | `change_audit_format` | 감사 로그 형식 변경 금지 |
| 6 | **데이터 보존** | `alter_data_retention` | 데이터 보존 정책 변경 금지 |
| 7 | **사용자 동의** | `modify_user_consent` | 사용자 동의 구조 변경 금지 |

**[3개 운영 금지]**

| # | 운영 금지 영역 | SOT 키 | 설명 |
|---|-------------|--------|------|
| 8 | **자기 권한 상승** | `escalate_own_privilege` | RBAC 역할 변경 포함 — 보안 위반 방지 |
| 9 | **가드레일 비활성화** | `disable_guardrails` | 4-Layer 안전 필터 비활성화/우회 금지 |
| 10 | **게이트 우회** | `bypass_gate` | 5-Gate 안전 관문 무력화 금지 |

[근거: CLAUDE.md §7.5 Self-evo LOCK, MASTER_SPEC NEVER_AUTO 정본, v13 DELTA-005~006]

### 롤백 정책 🔒

| 정책 | 설명 |
|------|------|
| **스냅샷 필수** | 변경 적용 전 반드시 현재 상태 스냅샷 저장 |
| **이상 탐지** | 변경 적용 후 성능 지표가 악화되면 자동 감지 |
| **재적용 잠금** | 롤백된 동일 제안은 **14일간 재적용 금지** (LOCK) |

[근거: CLAUDE.md §7.5 롤백 잠금]

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `logs` | 필수 | I-9에서 수집한 성공/실패 로그 데이터 |
| `search_runs` | 선택 | 검색 실행 이력 (소스별 통계 포함) |

[근거: D2.0-02 §7.88]

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `hints[]` | 개선 힌트 목록 | `["프롬프트에 구체적 예시 추가 시 정확도 +12%"]` |
| `ranked_hints` | 우선순위 정렬된 힌트 | 효과 크기순으로 정렬 |

[근거: D2.0-02 §7.88]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `IDLE` | 분석 대기 중 |
| `MINING` | 패턴 추출 진행 중 |
| `HINTS_READY` | 힌트 생성 완료 — 승인 대기 |
| `APPLIED` | 사용자 승인 후 적용 완료 |
| `ROLLED_BACK` | 롤백 완료 (이상 탐지 또는 사용자 요청) |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i18.hint.generated` | 개선 힌트 생성 완료 시 발생 |

[근거: D2.0-02 §7.89]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I18_HINT_FAIL` | 힌트 추출 실패 | fallback → 기존 설정 유지 |

[근거: D2.0-02 §7.89]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_SELFEVO_SKIP` | 힌트 추출 실패 시 Self-evo 건너뛰기 — 기존 설정 유지, 다음 주기에 재시도 |

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| ApprovalGate (변경 적용 전) | 모든 Self-evo 변경은 반드시 사용자 승인 필요 (LOCK) |
| SelfCheckGate (적용 후) | 변경 적용 후 성능 지표 검증 |
| 롤백 잠금 | 롤백된 제안은 14일간 재적용 금지 |

[근거: CLAUDE.md §7.5]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-9 (Cost Manager) | 로그 데이터 제공 (분석 원본) |
| I-19 (Approval Manager) | 변경 적용 시 승인 게이트 |
| I-6 (Self-check Engine) | 적용 후 품질 검증 |
| I-25 (SDAR Engine) | S-8 Self-evo Governance 연동 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | OFF | **OFF** | **OFF** | **ON** |
| 모듈 상태 | EXP | EXP | EXP | EXP |

### 🔒 LOCK 여부

- **change_lock**: Self-evo 원칙 자체가 LOCK — "제안만 가능, 자동 적용 절대 금지"
- 10가지 NEVER_AUTO_TARGETS(7개 불변구역 + 3개 운영금지)은 **ABSOLUTE LOCK**
- 롤백 후 14일 재적용 금지 규칙도 LOCK

### 핵심 요약 (3줄)
1. **I-18 Self-evo Engine**은 과거 로그에서 개선 힌트를 추출하는 "경기 분석 코치"로, **제안만 하고 자동 적용은 절대 금지**입니다.
2. 변경 가능 영역은 6가지(프롬프트, 도구, 메모리, 출력, 워크플로우, 모델)이며, 변경 불가 영역은 7가지(정체성, Non-goal, 법규, 비용, 승인, P0, P2)입니다.
3. 롤백된 제안은 14일간 재적용이 금지되며, V3에서만 활성화되는 실험적(EXP) 모듈입니다.

---

## §7.19 I-19 승인 관리자 (Approval Manager) 🔒

### 비유
은행의 **결재 시스템**과 같습니다. 적은 금액(저위험 작업)은 자동 승인되지만, 큰 금액(고위험 작업)은 반드시 상급자(사용자)의 도장(승인)이 필요합니다. 10분 안에 도장을 안 찍으면 자동으로 거절됩니다.

### 목적
VAMOS의 모든 **위험하거나 중요한 결정**에 대해 사용자 승인을 관리합니다. 작업의 위험도를 P0(일반)/P1(확장)/P2(고위험) 3단계로 분류하고, 각 등급에 맞는 승인 절차를 적용합니다. **승인 구조 자체를 변경하는 것은 절대 불가능(LOCK, change_lock=true)**합니다. [근거: D2.0-07 §3, CLAUDE.md §7.5]

### ⚠️ ABSOLUTE LOCK — change_lock = true (변경 불가)

> **I-19 Approval Manager의 승인 구조·정책·스키마는 LOCK 상태입니다. 어떤 Self-evo 제안으로도 변경할 수 없으며, 정책 변경은 반드시 ApprovalGate를 통과해야 합니다.**

[근거: CLAUDE.md §6 I-19 CORE(LOCK), D2.0-07 §3.3]

### 구조도

```
위험한 작업 발생
        ↓
┌──────────────────────────────────────────┐
│       I-19 Approval Manager              │
│                                          │
│  [1단계: 위험도 분류]                     │
│  ┌────────────────────────────────────┐  │
│  │ P0 (일반)  → 자동 허용 (allow)     │  │
│  │ P1 (확장)  → 계획 승인 필요        │  │
│  │ P2 (고위험) → 계획+실행 승인 필요  │  │
│  └────────────────────────────────────┘  │
│                                          │
│  [2단계: 승인 대기]                       │
│  ┌────────────────────────────────────┐  │
│  │ 승인 요청 → UI 모달/패널 표시      │  │
│  │ 타임아웃: 10분 (P2: 5분)           │  │
│  │ 미응답 → 자동 거부 (deny)          │  │
│  └────────────────────────────────────┘  │
│                                          │
│  [NEVER_AUTO 규칙] 🔒                    │
│  ┌────────────────────────────────────┐  │
│  │ 🚫 safety_rules 자동 변경 금지     │  │
│  │ 🚫 cost_ceiling 자동 변경 금지     │  │
│  │ 🚫 approval_flow 자동 변경 금지    │  │
│  │ 🚫 non_goals 자동 변경 금지        │  │
│  │ 🚫 audit_format 자동 변경 금지     │  │
│  │ 🚫 data_retention 자동 변경 금지   │  │
│  │ 🚫 user_consent 자동 변경 금지     │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
        ↓
  approved / denied / expired
```

### P0/P1/P2 승인 매트릭스 🔒

| 도메인 | Self-check 임계값 | 기본 처리 | 승인 유형 | 타임아웃 |
|--------|-------------------|----------|----------|---------|
| **P0** (일반) | ≥70점 | allow (자동 허용) | 없음 | N/A |
| **P1** (확장) | ≥75점 | allow (계획 승인 시) | 계획 승인 | **10분** |
| **P2** (고위험) | ≥80점 | restrict/deny | 계획 승인 + 실행 승인 | **5분** (HITL) |

[근거: D2.0-07 §2.1, §3.3, §4.3.2]

### 타임아웃 규칙

| 규칙 | 설명 |
|------|------|
| 일반 승인 타임아웃 | **10분** 내 응답 없으면 → **자동 거부(deny)** 처리 |
| P2 HITL 타임아웃 | **5분** 내 미응답 시 → 자동 deny |
| 적용 대상 | P2 도메인 작업, 안전 필터 경계 판정(confidence 0.4~0.6) |

[근거: D2.0-07 §4.3.2]

### NEVER_AUTO 규칙 🔒 (총 10개)

> **다음 10가지 영역은 어떤 상황에서도 자동 실행/변경이 금지됩니다. (frozenset 강제)** [근거: v13 DELTA-005~006]

**[7개 불변 구역]**

| # | NEVER_AUTO 대상 | 설명 |
|---|----------------|------|
| 1 | `modify_safety_rules` | 안전 규칙 자동 변경 금지 |
| 2 | `change_cost_ceiling` | 비용 상한 자동 변경 금지 |
| 3 | `alter_approval_flow` | 승인 절차 자동 변경 금지 |
| 4 | `modify_non_goals` | 7대 금지 사항 자동 변경 금지 |
| 5 | `change_audit_format` | 감사 로그 형식 자동 변경 금지 |
| 6 | `alter_data_retention` | 데이터 보존 정책 자동 변경 금지 |
| 7 | `modify_user_consent` | 사용자 동의 정책 자동 변경 금지 |

**[3개 운영 금지]**

| # | NEVER_AUTO 대상 | 설명 |
|---|----------------|------|
| 8 | `escalate_own_privilege` | 자기 권한 상승 (RBAC 역할 변경 포함) 금지 |
| 9 | `disable_guardrails` | 가드레일(4-Layer 안전 필터) 비활성화 금지 |
| 10 | `bypass_gate` | 5-Gate 안전 관문 우회 금지 |

추가 금지 규칙:
- P2 도메인 자동 생성 금지 (매 요청마다 "P2 도메인 사용 확인" 프롬프트 필수)
- 위험 기능 자동 실행 금지 (ABSOLUTE)
- 자동 적용/무인 배포 금지 (기본값: deny)
- P2 세션 종료 시 자동 OFF

[근거: D2.0-07 §1, §3.2.1, §4, CLAUDE.md §7.5]

### 자율 운영 수준 (Autonomy Levels)

| 수준 | 명칭 | 설명 | 승인 요구 |
|------|------|------|-----------|
| **L0** | FULL_MANUAL | 모든 행동에 사용자 확인 필수 | 매 동작마다 승인 |
| **L1** | SUPERVISED (기본값) | Allowlist 내 자동, 나머지 승인 | Allowlist 외 계획 승인 |
| **L2** | SEMI_AUTO | 읽기/생성 자동, 쓰기/변경 승인 | 쓰기·변경 시 계획 승인 |
| **L3** | FULL_AUTO | 정책/비용/P2 제외 자동 실행 | 정책 위반·상한 초과 시만 차단 |

- **기본값**: L1 (SUPERVISED)
- **수준 변경**: OWNER의 명시적 승인 필수
- **L3 제약**: P2 도메인, Non-goal, 비용 상한 초과 행동은 자동 실행 불가 (RULE 1.3)

[근거: D2.0-07 §3.2.1]

### 역할별 승인 권한 (RBAC)

| 역할 | 계획 승인 | 실행 승인 | 고위험 승인 | 비용 상한 |
|------|----------|----------|------------|----------|
| **OWNER** | ✅ 가능 | ✅ 가능 | ✅ 가능 | ₩266K (L3, P2) |
| **ADMIN** | ✅ 가능 | ✅ 가능 | ❌ 불가 | ₩93K (L2, P2) |
| **OPERATOR** | ✅ 가능 | ❌ 불가 | ❌ 불가 | ₩40K (L1) |
| **VIEWER** | ❌ 불가 | ❌ 불가 | ❌ 불가 | ₩0 (L0) |
| **AGENT** | 요청만 가능 | Allowlist 내만 | ❌ 불가 | — |

[근거: D2.0-07 §3.6.1~3.6.2, CLAUDE.md §7.4]

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `action_type` | 필수 | 수행하려는 행동 유형 (읽기/쓰기/고위험 등) |
| `domain` | 필수 | P0/P1/P2 도메인 분류 |
| `role` | 필수 | 요청자의 역할 (OWNER/ADMIN/OPERATOR/VIEWER) |
| `cost_context` | 선택 | 비용 관련 컨텍스트 (상한 초과 여부) |

[근거: D2.0-07 §3]

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `decision` | 승인 결과 | `approved` / `denied` / `expired` |
| `approval_type` | 승인 유형 | `plan_approval` / `execution_approval` |
| `reason` | 사유 | `"P2 도메인 — 실행 승인 거부"` |

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `PENDING` | 승인 요청 발송, 사용자 응답 대기 중 |
| `APPROVED` | 승인 완료 — 작업 재개 |
| `REJECTED` | 거절 — 사유 기록 후 작업 중단 |
| `EXPIRED` | 타임아웃(10분/5분) — 자동 거부 처리 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.approval.requested` | 승인 요청 발송 시 |
| `oc.approval.approved` | 승인 완료 시 |
| `oc.approval.rejected` | 거절 시 |
| `oc.approval.expired` | 타임아웃 만료 시 |
| `oc.gate.approval.requested` | ApprovalGate에서 승인 요청 시 |
| `oc.gate.approval.resolved` | ApprovalGate 결과 확정 시 |

[근거: D2.0-02 §6.1, D2.0-07 §3]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I3_APPROVAL_REQUIRED` | 승인 필요 (메모리 저장 관련) | fallback → FB_REQUIRE_APPROVAL |
| `OC_I5_APPROVAL_REQUIRED` | 승인 필요 (Decision 관련) | fallback → FB_REQUIRE_APPROVAL |
| `OC_GATE_APPROVAL_TIMEOUT` | 승인 타임아웃 | deny → 안전 종료 |
| `OC_GATE_APPROVAL_DENIED` | 승인 거부 | deny → 사유 기록 |
| `RBAC_PERMISSION_DENIED` | 역할 권한 부족 | deny |

[근거: D2.0-02 §6.2, D2.0-07 §3]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_REQUIRE_APPROVAL` | 승인 요청 메시지 생성 → 승인 전까지 Decision HOLD → 승인/거절/타임아웃 시 해제 |
| `FB_APPROVAL_TIMEOUT` | 타임아웃 시 안전 종료 (deny + 사유 기록) |
| `FB_OUTPUT_MINIMAL` | 승인 거절 시 최소 안전 출력만 반환 |

[근거: D2.0-02 §6.3]

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| ApprovalGate (S2~S4) | 파이프라인 전 구간에서 승인 게이트 적용 |
| PolicyGate 연동 | PolicyGate에서 `require_approval` 판정 시 트리거 |
| CostGate 연동 | 일/월 상한 초과 감지 시 비용 승인 요청 |
| 타임아웃 enforce | 10분(일반)/5분(P2) 타임아웃 자동 적용 |

[근거: D2.0-07 §3, §4.3.2]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-5 (Condition & Decision Engine) | Decision HOLD/재개 제어 |
| I-8 (Policy Engine) | PolicyGate → require_approval 판정 시 트리거 |
| I-9 (Cost Manager) | 비용 상한 초과 시 비용 승인 요청 |
| I-10 (Tool Registry) | 도구 실행 시 권한별 승인 분기 |
| I-18 (Self-evo Engine) | Self-evo 변경 적용 시 승인 게이트 |
| I-25 (SDAR Engine) | 자동 수리 시 승인 필요 여부 판단 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE(LOCK) | CORE(LOCK) | CORE(LOCK) | CORE(LOCK) |

### 🔒 LOCK 여부

- **change_lock = true** (변경 불가) 🔒
- 승인 구조·정책·스키마 변경은 반드시 ApprovalGate 통과 필수
- Major 버전 변경(2.0.0 → 3.0.0)은 07의 Approval Gate 필수
- NEVER_AUTO 10가지 영역은 ABSOLUTE LOCK
- Constitution(헌법) 편집: OWNER만 가능

[근거: D2.0-07 §3.3, CLAUDE.md §6 I-19 CORE(LOCK)]

### 핵심 요약 (3줄)
1. **I-19 Approval Manager**는 VAMOS의 "결재 시스템"으로, P0(자동)/P1(계획 승인)/P2(계획+실행 승인) 3단계로 위험도를 관리합니다.
2. 타임아웃은 일반 10분, P2 고위험 5분이며, 미응답 시 **자동 거부(deny)**됩니다. NEVER_AUTO 10가지 영역은 절대 자동 변경 불가입니다.
3. **change_lock=true**로, 승인 구조 자체의 변경이 불가능한 VAMOS에서 가장 강력한 보호를 받는 모듈입니다.

---

## §7.20 I-20 장애 대응 관리자 (Failure/Fallback Manager)

### 비유
병원의 **응급실 트리아지(분류) 시스템**과 같습니다. 환자(오류)가 들어오면 증상(에러 코드)을 보고 어떤 치료(폴백 전략)를 할지 자동으로 결정합니다. 같은 문제가 계속 반복되면 해당 구역을 **차단(Circuit Breaker)**해서 더 큰 피해를 막습니다.

### 목적
VAMOS 시스템 내에서 발생하는 모든 **오류(FailureCode)**를 감지하고, 미리 정의된 **폴백 전략(Fallback)**으로 자동 복구를 시도합니다. **36개의 에러 코드를 23개의 폴백 전략에 매핑**하여 체계적으로 장애에 대응하며, 연속 실패 시 **Circuit Breaker**(회로 차단기)로 서비스를 보호합니다. [근거: D2.0-02 §6.2~6.3, §7.78~7.80]

### 구조도

```
오류 발생!
        ↓
┌──────────────────────────────────────────────┐
│      I-20 Failure/Fallback Manager           │
│                                              │
│  [1단계: 에러 분류]                           │
│  ┌──────────────────────────────────────┐    │
│  │ FailureCode 식별                     │    │
│  │ 예: OC_I1_PARSE_FAIL → "파싱 실패"   │    │
│  └──────────────┬───────────────────────┘    │
│                 ↓                             │
│  [2단계: 폴백 매핑]                           │
│  ┌──────────────────────────────────────┐    │
│  │ 36 FailureCode → 23 Fallback 매핑    │    │
│  │ 예: OC_I1_PARSE_FAIL                 │    │
│  │     → FB_INTENT_HEURISTIC_PARSE      │    │
│  └──────────────┬───────────────────────┘    │
│                 ↓                             │
│  [3단계: Circuit Breaker 감시]                │
│  ┌──────────────────────────────────────┐    │
│  │ CLOSED  → 정상 (호출 허용)           │    │
│  │ OPEN    → 차단 (연속 3회 실패)       │    │
│  │ HALF-OPEN → 복구 탐지 (60초 후 시도) │    │
│  └──────────────────────────────────────┘    │
└──────────────────────────────────────────────┘
        ↓
  복구 성공 또는 deny
```

### 36 FailureCode → 23 Fallback 매핑 (주요 항목)

| FailureCode | 출처 | 설명 | 폴백 |
|-------------|------|------|------|
| `OC_I1_PARSE_FAIL` | I-1 | 의도 파싱 실패 | `FB_INTENT_HEURISTIC_PARSE` |
| `OC_I1_AMBIGUOUS_UNRESOLVED` | I-1 | 모호성 미해소 | `FB_ASK_CLARIFICATION` |
| `OC_I2_RAG_NO_SOURCE` | I-2 | 근거 소스 부재 | `FB_RAG_RETRY_EXPAND` |
| `OC_I2_EVIDENCE_QOD_LOW` | I-2 | 근거 품질 미달 | `FB_RAG_RETRY_EXPAND` |
| `OC_I2_SOURCE_POLICY_BLOCK` | I-2 | 소스 정책 차단 | `FB_RAG_SWITCH_SOURCE` |
| `OC_I2_TIMEOUT` | I-2 | 검색 타임아웃 | `FB_RAG_SWITCH_SOURCE` |
| `OC_I3_MEMORY_POLICY_DENY` | I-3 | 메모리 저장 정책 위반 | `FB_MEMORY_META_ONLY` |
| `OC_I3_APPROVAL_REQUIRED` | I-3 | 승인 필수 | `FB_REQUIRE_APPROVAL` |
| `OC_I3_COMMIT_FAIL` | I-3 | 커밋 실패 | deny (폴백 없음) |
| `OC_I4_OUTPUT_SPEC_VIOLATION` | I-4 | 출력 규격 위반 | `FB_OUTPUT_REFORMAT` / `FB_OUTPUT_MINIMAL` |
| `OC_I4_CITATION_MISSING` | I-4 | 인용 누락 | `FB_POLICY_MASK` |
| `OC_I4_MASK_FAIL` | I-4 | 마스킹 실패 | `FB_POLICY_MASK` |
| `OC_I5_POLICY_BLOCK` | I-5 | 정책 차단 | `FB_RESTRICT_GENERAL_INFO` / `FB_DENY_WITH_REASON` |
| `OC_I5_APPROVAL_REQUIRED` | I-5 | 승인 필수 | `FB_REQUIRE_APPROVAL` |
| `OC_I5_COST_OVER_BUDGET` | I-5 | 비용 초과 | `FB_COST_DOWNSHIFT` |
| `OC_I5_EVIDENCE_INSUFFICIENT` | I-5 | 근거 부족 | `FB_OUTPUT_MINIMAL` |
| `OC_I5_ROUTE_NOT_FOUND` | I-5 | 라우팅 실패 | `FB_ROUTE_SAFE_NODE` |
| `OC_I20_SNAPSHOT_FAIL` | I-20 | 스냅샷 저장 실패 | deny (폴백 없음) |
| `OC_ERR_SCHEMA_INVALID` | 공통 | 스키마 검증 실패 | deny |
| `QUEUE_OVERFLOW` | 공통 | 큐 포화 | deny (요청 지연 반환) |
| `INPUT_VALIDATION_FAIL` | 공통 | 입력 검증 실패 | deny |
| `EXTERNAL_RESPONSE_INVALID` | 공통 | 외부 API 응답 불일치 | deny |
| `SENSITIVE_DATA_FLAG` | 공통 | 민감 데이터 감지 | restrict (감사 로그 기록) |

[근거: D2.0-02 §6.2]

### 23 Fallback 전략 (주요 항목)

| 폴백 ID | 목표 | 핵심 동작 | 하위 버전 |
|---------|------|----------|----------|
| `FB_INTENT_HEURISTIC_PARSE` | 최소 파싱 성공 | 핵심 슬롯만 추출, 불확실 = "unknown" | V1 |
| `FB_ASK_CLARIFICATION` | 모호성 해소 | 모호한 슬롯 1~3개 질문, Decision HOLD | V1 |
| `FB_RAG_RETRY_EXPAND` | 근거 부족 해결 | 검색 범위 확장(내부→외부), 미달 시 다운시프트 | V1 |
| `FB_RAG_SWITCH_SOURCE` | 소스 차단 회피 | 다른 소스 세트로 재시도, 타임아웃 시 짧은 응답 | V1 |
| `FB_MEMORY_META_ONLY` | 저장 정책 준수 | 원문 대신 메타(해시/요약/태그)만 저장 | V1 |
| `FB_REQUIRE_APPROVAL` | 승인 게이트 준수 | 승인 요청 → Decision HOLD → 승인/거절/타임아웃 | V1 |
| `FB_OUTPUT_REFORMAT` | 출력 규격 준수 | output_spec에 맞게 재정렬 | V1 |
| `FB_OUTPUT_MINIMAL` | 최소 안전 출력 | 핵심 결론만 반환, 상세 생략 | V0 |
| `FB_POLICY_MASK` | 마스킹 준수 | 민감 필드 재탐지 → 마스킹 후 재출력 | V1 |
| `FB_COST_DOWNSHIFT` | 비용 상한 준수 | 저비용 모드 전환, 출력 범위 축소 | V1 |
| `FB_ROUTE_SAFE_NODE` | 안전 라우팅 | 기본 안전 노드로 라우팅, 기능 제한 모드 | V1 |
| `FB_RESTRICT_GENERAL_INFO` | 대리결정 회피 | 단정적 결론 제거, 일반 정보만 안내, 전문가 상담 권유 | V1 |
| `FB_DENY_WITH_REASON` | 명시적 거절 | 거절 사유 설명 + 대안 1~2개 제시 | V0 |

[근거: D2.0-02 §6.3]

### Circuit Breaker (회로 차단기) 3상태 🔒

> **비유**: 가정용 **누전 차단기**와 같습니다. 전기(요청)가 정상이면 켜져 있고(CLOSED), 합선(연속 오류)이 발생하면 자동으로 내려가고(OPEN), 잠시 후 조심스럽게 다시 올려봅니다(HALF-OPEN).

| 상태 | 설명 | 동작 | 전환 조건 |
|------|------|------|-----------|
| **CLOSED** (닫힘) | 정상 동작 상태 | 호출 허용 | 기본 상태 |
| **OPEN** (열림) | 차단 상태 | 호출 즉시 deny | 연속 실패 **3회** 초과 시 진입 |
| **HALF-OPEN** (반열림) | 복구 탐지 상태 | 제한적 호출 허용 (테스트) | OPEN 유지 **60초** 경과 후 |

**Circuit Breaker 규칙:**
- 연속 실패 N회(기본: 3회) 초과 → OPEN 전환
- OPEN 60초 경과 후 → HALF-OPEN (복구 시도)
- HALF-OPEN에서 성공 → CLOSED 복귀
- **P2 예외**: P2 이상 작업은 60초 자동 HALF-OPEN 적용 안 됨 — **반드시 사용자 승인 후에만 HALF-OPEN 허용** 🔒
- 상태 변경은 반드시 LogEvent에 기록

[근거: D2.0-05 §4.4 ADD-072]

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `failure_code` | 필수 | 발생한 에러 코드 (예: `OC_I1_PARSE_FAIL`) |
| `trace_id` | 필수 | 추적 ID (어떤 요청에서 발생했는지) |
| `context` | 선택 | 오류 발생 시점의 컨텍스트 정보 |

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `fallback_id` | 적용된 폴백 전략 | `FB_ASK_CLARIFICATION` |
| `result` | 폴백 실행 결과 | `recovered` / `denied` / `escalated` |
| `circuit_state` | Circuit Breaker 상태 | `CLOSED` / `OPEN` / `HALF-OPEN` |

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `MONITORING` | 정상 감시 중 |
| `FALLBACK_EXECUTING` | 폴백 전략 실행 중 |
| `RECOVERED` | 폴백으로 복구 완료 |
| `CIRCUIT_OPEN` | Circuit Breaker 열림 — 해당 구간 차단 |
| `CIRCUIT_HALF_OPEN` | 복구 테스트 중 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i20.snapshot.saved` | 상태 스냅샷 저장 완료 |
| `oc.circuit.opened` | Circuit Breaker OPEN 전환 |
| `oc.circuit.half_opened` | Circuit Breaker HALF-OPEN 전환 |
| `oc.circuit.closed` | Circuit Breaker CLOSED 복귀 |

[근거: D2.0-02 §7.80, D2.0-05 §4.4]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I20_SNAPSHOT_FAIL` | 스냅샷 저장 실패 | deny |
| `OC_CIRCUIT_OPEN` | Circuit Breaker 열림 상태에서 호출 시도 | deny |

[근거: D2.0-02 §7.80]

### 폴백 전략 (Fallbacks)

위의 "23 Fallback 전략" 표 참조. I-20이 이 전체 폴백 레지스트리를 관리합니다.

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| 전 파이프라인 구간 | 모든 모듈의 FailureCode 발생 시 자동 트리거 |
| Circuit Breaker | 연속 실패 감시 — 3회 초과 시 OPEN 전환 |
| P2 승인 연동 | P2 작업의 Circuit Breaker HALF-OPEN 전환 시 승인 필요 |
| LogEvent 기록 | 모든 상태 변경 반드시 기록 |

[근거: D2.0-05 §4.4]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-1 ~ I-5 (핵심 모듈) | FailureCode 발생원 — 폴백 매핑 대상 |
| I-19 (Approval Manager) | FB_REQUIRE_APPROVAL 연동, P2 Circuit Breaker 승인 |
| I-9 (Cost Manager) | FB_COST_DOWNSHIFT 연동 |
| I-25 (SDAR Engine) | 고급 자동 수리와 연계 (V2+) |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | ON | **ON** | **ON** | **ON** |
| 모듈 상태 | CORE | CORE | CORE | CORE |

### 🔒 LOCK 여부

- **change_lock = false** (변경 가능)
- 단, Circuit Breaker의 P2 승인 규칙은 LOCK (사용자 승인 없이 HALF-OPEN 불가)
- Hard loop 규칙: 승인 없이는 외부 재실행 금지 (LOCK)

[근거: D2.0-07 §4.5]

### 핵심 요약 (3줄)
1. **I-20 Failure/Fallback Manager**는 VAMOS의 "응급실 트리아지"로, **36개 에러 코드를 23개 폴백 전략에 매핑**하여 체계적으로 장애에 대응합니다.
2. **Circuit Breaker**(회로 차단기)가 연속 3회 실패 시 OPEN(차단), 60초 후 HALF-OPEN(복구 시도), 성공 시 CLOSED(정상) 3상태로 서비스를 보호합니다.
3. P2 고위험 작업의 Circuit Breaker 복구는 반드시 사용자 승인이 필요하며, V1부터 모든 버전에서 활성화되는 핵심(CORE) 모듈입니다.

---

## §7.21 I-21 정보원 진화 엔진 (Source Evolution)

### 비유
도서관의 **장서 품질 관리사**와 같습니다. 어떤 책(정보 소스)이 자주 인용되고 정확한지, 어떤 책이 오래되어 신뢰할 수 없는지를 평가하고, 신뢰도가 낮은 책은 서가에서 빼는(비활성화) 역할을 합니다.

### 목적
VAMOS가 사용하는 **정보 소스(검색 엔진, 데이터베이스, API 등)**의 품질을 지속적으로 평가합니다. 각 소스의 성공/실패 통계를 분석하여 신뢰도 점수를 매기고, 신뢰도가 일정 수준 이하로 떨어지면 **자동으로 비활성화**합니다. 소스 변경 제안은 승인 후 반영됩니다. [근거: D2.0-02 §7.96~7.98]

### 구조도

```
검색 실행 이력 (search_runs)
        ↓
┌──────────────────────────────────────┐
│      I-21 Source Evolution           │
│  ┌────────────────────────────────┐  │
│  │ 1. evaluate_sources()         │  │  → 소스별 성과 분석
│  │ 2. propose_source_changes()   │  │  → 변경 제안 생성
│  └────────────────────────────────┘  │
│                                      │
│  [신뢰도 관리]                        │
│  ┌────────────────────────────────┐  │
│  │ 높음 (>0.8) → 우선 사용        │  │
│  │ 보통 (0.5~0.8) → 일반 사용     │  │
│  │ 낮음 (<0.5) → 자동 비활성화 ⚠️  │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
        ↓
  scorecard + proposals[] → 승인 필요
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `search_runs` | 필수 | 검색 실행 이력 (소스별 성공/실패 통계) |

[근거: D2.0-02 §7.97]

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `scorecard` | 소스 평가 카드 | `{source: "Google", score: 0.85, trend: "stable"}` |
| `proposals[]` | 소스 변경 제안 목록 | `["소스 X 비활성화 권고 (score: 0.3)"]` |

[근거: D2.0-02 §7.97]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `IDLE` | 평가 대기 중 |
| `EVALUATING` | 소스 평가 진행 중 |
| `PROPOSALS_READY` | 변경 제안 생성 완료 — 승인 대기 |
| `APPLIED` | 제안 승인 후 반영 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i21.source.proposed` | 소스 변경 제안 생성 시 발생 |

[근거: D2.0-02 §7.98]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I21_SOURCE_EVO_FAIL` | 소스 평가/진화 실패 | fallback → 기존 소스 설정 유지 |

[근거: D2.0-02 §7.98]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_SOURCE_EVO_SKIP` | 소스 평가 실패 시 기존 소스 설정 유지, 다음 주기에 재시도 |

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| ApprovalGate (변경 적용 전) | 소스 변경 제안은 반드시 사용자 승인 필요 |
| 자동 비활성화 | 신뢰도 임계값 이하 소스는 자동 비활성화 (로그 기록) |

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-2 (RAG/Search Engine) | 검색 소스 목록 관리 및 소스별 성과 데이터 수신 |
| I-18 (Self-evo Engine) | Self-evo 프레임워크 내에서 소스 진화 담당 |
| I-19 (Approval Manager) | 소스 변경 제안 승인 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | OFF | **OFF** | **OFF** | **ON** |
| 모듈 상태 | EXP | EXP | EXP | EXP |

### 🔒 LOCK 여부

- **change_lock = false** (변경 가능)
- 단, 소스 변경 적용은 Self-evo 원칙에 따라 반드시 승인 필요

### 핵심 요약 (3줄)
1. **I-21 Source Evolution**은 VAMOS의 "장서 품질 관리사"로, 검색 소스의 신뢰도를 지속적으로 평가하고 점수화합니다.
2. 신뢰도가 임계값 이하로 떨어지면 해당 소스를 자동 비활성화하고, 소스 변경 제안은 승인 후 반영됩니다.
3. V3에서만 활성화되는 실험적(EXP) 모듈로, I-2(RAG/검색)와 I-18(Self-evo)과 긴밀히 연동됩니다.

---

## §7.22 I-22 작업 관리자 (Task/Project Manager)

### 비유
회사의 **프로젝트 매니저(PM)**와 같습니다. 복잡한 프로젝트를 작은 작업(Task)들로 쪼개고, 각 작업 사이의 순서(의존성)를 파악하고, 진행 상황을 추적하며, 마감 기한과 우선순위를 관리합니다.

### 목적
복잡한 사용자 요청을 여러 작업(검색 → 요약 → 비교 → 정리 등)으로 **분해(Decompose)**하고, 작업 간 의존성을 파악하여 실행 가능한 **DAG(방향성 비순환 그래프, Directed Acyclic Graph — 순서가 있는 작업 흐름도)**를 생성합니다. 프로젝트 단위로 TODO 목록, 진행 상태, 마감/우선순위를 관리하며, I-12(스케줄러)와 함께 장기 작업을 조율합니다. [근거: D2.0-02 §7.99~7.101]

### 구조도

```
복잡한 요청 (intent_frame)
        ↓
┌──────────────────────────────────────────┐
│     I-22 Task/Project Manager            │
│  ┌────────────────────────────────────┐  │
│  │ 1. decompose_task()               │  │  → 작업 분해 + DAG 생성
│  │ 2. track_progress()               │  │  → 진행 상태 추적
│  │ 3. schedule_batch()               │  │  → 장기 작업 스케줄링
│  └────────────────────────────────────┘  │
│                                          │
│  [프로젝트 ↔ 세션 매핑]                   │
│  ┌────────────────────────────────────┐  │
│  │ Project A ──→ Session 1, 3, 7     │  │
│  │ Project B ──→ Session 2, 5        │  │
│  │ Project C ──→ Session 4, 6, 8, 9  │  │
│  └────────────────────────────────────┘  │
└──────────────────────────────────────────┘
        ↓
  task_dag + progress_status
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `intent_frame` | 필수 | I-1에서 생성한 의도 프레임 (작업 분해 판단용) |
| `project_context` | 필수 | 프로젝트 컨텍스트 (기존 TODO, 진행 상태) |
| `project_id` | 진행 추적 시 | 프로젝트 고유 ID |
| `task_id` | 진행 추적 시 | 특정 작업 ID |
| `constraints` | 스케줄링 시 | 제약 조건 (마감, 우선순위 등) |

[근거: D2.0-02 §7.100]

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `task_dag` | 작업 분해 결과 (DAG 구조) | 검색→요약→비교→정리 순서 |
| `progress_status` | 진행 상태 | `{total: 5, done: 3, in_progress: 1, pending: 1}` |
| `batch_plan` | 배치 실행 계획 | 야간 배치, 주간 리포트 스케줄 |

[근거: D2.0-02 §7.100]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `IDLE` | 대기 중 |
| `DECOMPOSING` | 작업 분해 진행 중 |
| `TRACKING` | 진행 상태 추적 중 |
| `SCHEDULING` | 배치 스케줄링 중 |
| `COMPLETED` | 프로젝트/작업 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i22.task.decomposed` | 작업 분해 완료 시 발생 |
| `oc.i22.project.updated` | 프로젝트 상태 업데이트 시 발생 |

[근거: D2.0-02 §7.101]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I22_DECOMPOSE_FAIL` | 작업 분해 실패 | fallback → 단일 작업으로 실행 |
| `OC_I22_DAG_CYCLE_DETECTED` | DAG에 순환 의존성 감지 | deny → 사용자에게 의존성 수정 요청 |

[근거: D2.0-02 §7.101]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_TASK_SINGLE_EXEC` | 작업 분해 실패 시 전체를 단일 작업으로 실행 |
| `FB_DAG_LINEARIZE` | DAG 순환 감지 시 선형 순서로 변환 시도 |

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| I-1 연동 | 작업 분해 판단 시 I-1 의도 분석 결과 참조 |
| I-12 연동 | 장기 작업(야간 배치, 주간 리포트) 스케줄링 조율 |
| I-3 연동 | project_memory에 프로젝트 상태 저장 |

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-1 (Intent Detector) | 작업 분해 판단 정보 제공 |
| I-3 (Memory Engine) | project_memory에 프로젝트 상태 저장 |
| I-6 (Self-check Engine) | 작업 완료 후 품질 검증 |
| I-7 (Session Manager) | 프로젝트 ↔ 세션 매핑 관리 |
| I-10 (Tool Registry) | 작업별 필요 도구 매칭 |
| I-12 (Workflow Builder) | 장기 작업 스케줄링 조율 |

[근거: D2.0-02 §7.101]

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | OFF | **OFF** | **COND** | **ON** |
| 모듈 상태 | COND | COND | COND | COND |

> **COND** = 조건부 활성화 (Conditional). 특정 조건(프로젝트 기능 활성화)을 만족해야 작동합니다.

### 🔒 LOCK 여부

- **change_lock = false** (변경 가능)

### 핵심 요약 (3줄)
1. **I-22 Task/Project Manager**는 VAMOS의 "프로젝트 매니저"로, 복잡한 요청을 DAG(작업 흐름도) 형태로 분해하여 체계적으로 실행합니다.
2. 프로젝트 ↔ 세션 매핑으로 장기 작업을 추적하며, I-12(스케줄러)와 연동하여 야간 배치, 주간 리포트 등을 조율합니다.
3. V2에서 조건부(COND) 활성화, V3에서 완전 활성화되는 모듈입니다.

---

## §7.23 I-23 문서/코드 구조화 엔진 (Doc/Code Structuring)

### 비유
서점의 **도서 정리 전문가**와 같습니다. 두꺼운 책(긴 문서, 코드, 로그)을 받으면 목차를 만들고, 섹션별로 나누고, 핵심 포인트를 뽑아내고, 깔끔한 요약본을 만들어 줍니다.

### 목적
긴 문서, 코드, 로그, 표 데이터를 **구조적으로 파싱(분석)·요약·분석**합니다. 논문/백서/문서에서 섹션별 요약과 핵심 포인트를 추출하고, 코드/로그에서 구조 분석과 이슈 위치를 요약합니다. I-2(RAG) 인덱싱용 L1 요약을 생성하고, I-13(템플릿)과 연동합니다. [근거: D2.0-02 §7.102~7.104]

> **참고**: 기존 I-4(출력 구조화) 역할에서 분리된 기능으로, PLAN 3.0에서 신규 추가되었습니다.

### 구조도

```
긴 문서 / 코드 / 로그
        ↓
┌──────────────────────────────────────┐
│     I-23 Doc/Code Structuring        │
│  ┌────────────────────────────────┐  │
│  │ 1. parse_document()           │  │  → 문서 파싱 + 섹션 분리
│  │ 2. extract_key_points()       │  │  → 핵심 포인트 추출
│  │ 3. generate_l1_summary()      │  │  → RAG용 L1 요약 생성
│  └────────────────────────────────┘  │
│                                      │
│  [지원 타입]                          │
│  ┌────────────────────────────────┐  │
│  │ 📄 논문/백서 → 섹션/요약/키포인트│  │
│  │ 💻 코드/로그 → 구조 분석/이슈   │  │
│  │ 📊 표 데이터 → 구조화된 데이터   │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
        ↓
  structured_sections + key_points + l1_summary
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `doc_ref` | 필수 | 문서/코드 참조 (파일 경로, URL 등) |
| `doc_type` | 필수 | 문서 유형 (논문, 코드, 로그, 표 등) |

[근거: D2.0-02 §7.103]

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `structured_sections` | 구조화된 섹션 목록 | `[{title: "서론", content: "...", page: 1}]` |
| `key_points[]` | 핵심 포인트 목록 | `["주요 발견 1", "주요 발견 2"]` |
| `l1_summary` | RAG 인덱싱용 L1 요약 | 한 단락 요약 텍스트 |

[근거: D2.0-02 §7.103]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `IDLE` | 대기 중 |
| `PARSING` | 문서 파싱 진행 중 |
| `EXTRACTING` | 핵심 포인트 추출 중 |
| `SUMMARIZING` | L1 요약 생성 중 |
| `DONE` | 처리 완료 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i23.doc.parsed` | 문서 파싱 완료 시 발생 |
| `oc.i23.structure.extracted` | 구조 추출 완료 시 발생 |

[근거: D2.0-02 §7.104]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I23_PARSE_FAIL` | 문서 파싱 실패 | fallback → 원문 그대로 전달 |
| `OC_I23_UNSUPPORTED_FORMAT` | 지원하지 않는 형식 | deny → 사용자에게 형식 변환 요청 |

[근거: D2.0-02 §7.104]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_DOC_RAW_PASS` | 파싱 실패 시 원문 그대로 다음 단계에 전달 |
| `FB_DOC_PARTIAL` | 부분 파싱 성공 시 파싱된 부분만 사용 |

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| I-2 연동 | RAG 인덱싱용 L1 요약 자동 생성 |
| I-13 연동 | 문서 템플릿과 연동하여 출력 구조화 |
| I-4 연동 | 구조화된 산출물 포맷팅 |

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-2 (RAG/Search Engine) | RAG 인덱싱용 L1 요약 생성 |
| I-4 (Multimodal Interpreter) | 구조화된 산출물 포맷팅 (역할 분리 원본) |
| I-13 (Template Engine) | 문서 템플릿과 연동 |

[근거: D2.0-02 §7.104]

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | OFF | **OFF** | **COND** | **ON** |
| 모듈 상태 | COND | COND | COND | COND |

### 🔒 LOCK 여부

- **change_lock = false** (변경 가능)

### 핵심 요약 (3줄)
1. **I-23 Doc/Code Structuring**은 VAMOS의 "도서 정리 전문가"로, 긴 문서/코드/로그를 구조적으로 파싱하고 핵심 포인트를 추출합니다.
2. I-2(RAG) 인덱싱용 L1 요약을 자동 생성하며, I-4(출력 구조화)에서 분리된 신규 모듈입니다.
3. V2에서 조건부(COND) 활성화, V3에서 완전 활성화됩니다.

---

## §7.24 I-24 지식 그래프 엔진 (Knowledge Graph Engine)

### 비유
도서관의 **상호 참조 색인 시스템**과 같습니다. 모든 책(문서, 결정, 산출물)을 그물처럼 연결하여 "이 문서는 저 결정과 관련있고, 저 결정은 이 산출물을 만들었다"는 **관계(Relationship)**를 추적합니다.

### 목적
VAMOS 내부의 개념, 문서, 결정, 산출물 간의 **관계를 그래프(Graph)로 유지**하여 탐색과 재사용을 돕습니다. Neo4j(그래프 데이터베이스) 또는 NetworkX(파이썬 그래프 라이브러리) 기반으로 동작하며, **GraphRAG**(그래프 기반 검색 증강 생성)와 연동하여 I-2(RAG/검색)의 검색 품질을 향상시킵니다. [근거: D2.0-02 §7.93~7.95]

> **참고**: D2.0-02에서는 I-20으로 번호가 배정되어 있으나, 정본(D2.0-01)에서는 I-24입니다. 설계 내용은 D2.0-02 I-20 (§7.93~7.95)에서 커버됩니다.

### 구조도

```
개념 / 문서 / 결정 / 산출물
        ↓
┌──────────────────────────────────────┐
│     I-24 Knowledge Graph Engine      │
│  ┌────────────────────────────────┐  │
│  │ 1. upsert_nodes_edges()       │  │  → 노드/엣지 추가·갱신
│  │ 2. query_graph()              │  │  → 그래프 쿼리 실행
│  └────────────────────────────────┘  │
│                                      │
│  [그래프 구조 예시]                    │
│  ┌────────────────────────────────┐  │
│  │  [문서A] ──관련──→ [결정B]     │  │
│  │     │                ↓         │  │
│  │   참조             생성         │  │
│  │     ↓                ↓         │  │
│  │  [문서C] ←──근거── [산출물D]   │  │
│  └────────────────────────────────┘  │
│                                      │
│  [기술 스택]                          │
│  Neo4j (그래프 DB) / NetworkX (경량)  │
│  + GraphRAG 연동                     │
└──────────────────────────────────────┘
        ↓
  query_results (관련 노드/엣지)
```

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `entities` | upsert 시 | 추가/갱신할 개념/문서/결정 (노드 데이터) |
| `relations` | upsert 시 | 관계 정의 (엣지 데이터) |
| `query` | 쿼리 시 | 그래프 탐색 쿼리 |

[근거: D2.0-02 §7.94]

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `ok` | upsert 성공 여부 | `true` / `false` |
| `results` | 쿼리 결과 (관련 노드/엣지) | `[{node: "결정B", relation: "생성", target: "산출물D"}]` |

[근거: D2.0-02 §7.94]

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `IDLE` | 대기 중 |
| `UPSERTING` | 노드/엣지 추가·갱신 중 |
| `QUERYING` | 그래프 쿼리 실행 중 |
| `SYNCING` | GraphRAG와 동기화 중 |

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `oc.i24.graph.updated` | 그래프 업데이트 완료 시 발생 |

[근거: D2.0-02 §7.95]

### 에러 코드 (FailureCodes)

| 에러 코드 | 설명 | 기본 조치 |
|----------|------|----------|
| `OC_I24_GRAPH_FAIL` | 그래프 작업 실패 | fallback → 그래프 없이 일반 검색으로 진행 |

[근거: D2.0-02 §7.95]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_GRAPH_FALLBACK_SEARCH` | 그래프 실패 시 일반 키워드/벡터 검색으로 대체 |

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| I-2 연동 | GraphRAG 검색 시 그래프 데이터 제공 |
| I-3 연동 | 메모리 저장 시 관계 그래프 자동 업데이트 |

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-2 (RAG/Search Engine) | GraphRAG 연동으로 검색 품질 향상 |
| I-3 (Memory Engine) | 메모리 저장 시 관계 그래프 업데이트 |
| I-23 (Doc/Code Structuring) | 구조화된 문서에서 관계 추출 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | OFF | **OFF** | **OFF** | **ON** |
| 모듈 상태 | EXP | EXP | EXP | EXP |

### 🔒 LOCK 여부

- **change_lock = false** (변경 가능)

### 핵심 요약 (3줄)
1. **I-24 Knowledge Graph Engine**은 VAMOS의 "상호 참조 색인"으로, 문서/결정/산출물 간 관계를 **그래프(Graph)** 형태로 관리합니다.
2. Neo4j/NetworkX 기반으로 동작하며, **GraphRAG**와 연동하여 I-2(RAG)의 검색 품질을 향상시킵니다.
3. V3에서만 활성화되는 실험적(EXP) 모듈로, D2.0-02에서는 I-20으로 번호가 배정되어 있습니다.

---

## §7.25 I-25 자가진단/자동수리 엔진 (SDAR Engine)

### 비유
인체의 **면역 시스템**과 같습니다. 몸(시스템)에 이상이 생기면 자동으로 감지하고, 원인을 분석하고, 치료법을 처방하고, 치료(수리)를 실행하고, 치료 효과를 검증합니다. 단, 큰 수술(고위험 수리)은 반드시 의사(사용자)의 동의가 필요합니다.

### 목적
VAMOS의 **자가진단 및 자동수리(Self-Diagnosis & Auto-Repair)** 엔진입니다. 시스템 오류를 실시간으로 감지하고, 근본 원인을 분석하며, 위험도에 따라 **단계적 자율(Graduated Autonomy)** 원칙으로 수리를 실행합니다. 5개 레이어 파이프라인으로 구성되며, **보안 오류는 절대 자동 수리 불가(NEVER_AUTO)**입니다. [근거: VAMOS_SDAR_DESIGN_SPECIFICATION §1~2]

### ⚠️ LOCK — 보안 오류 특별 규칙 (변경 불가)

> **보안 관련 오류(CATEGORY E)는 어떤 자율 수준에서도 자동 수리가 절대 금지됩니다. 반드시 사용자 승인 필요.**

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §4, §9 RULE 1.3]

### 5-Layer Pipeline (5단계 파이프라인)

```
이상 발생!
    ↓
┌─────────────────────────────────────────────────┐
│              I-25 SDAR Engine                    │
│                                                  │
│  Layer 1: DETECTION (감지) 🔍                    │
│  ┌──────────────────────────────────────────┐   │
│  │ ① Health Monitoring (건강 모니터링)       │   │
│  │ ② Error Pattern Detection (에러 패턴)     │   │
│  │ ③ Anomaly Detection (이상 탐지)           │   │
│  └──────────────────────────────────────────┘   │
│    ↓                                             │
│  Layer 2: DIAGNOSIS (진단) 🔬                    │
│  ┌──────────────────────────────────────────┐   │
│  │ ① Root Cause Analysis (근본 원인 분석)    │   │
│  │ ② Error Classification (5분류: A~E)       │   │
│  │ ③ Impact Assessment (영향도 평가)          │   │
│  └──────────────────────────────────────────┘   │
│    ↓                                             │
│  Layer 3: PRESCRIPTION (처방) 💊                 │
│  ┌──────────────────────────────────────────┐   │
│  │ ① Fix Candidate Generation (수리 후보)    │   │
│  │ ② Risk Assessment (위험 평가)              │   │
│  │ ③ Repair Plan Generation (수리 계획)       │   │
│  └──────────────────────────────────────────┘   │
│    ↓                                             │
│  Layer 4: REPAIR (수리) 🔧                       │
│  ┌──────────────────────────────────────────┐   │
│  │ Graduated Autonomy (단계적 자율 실행)      │   │
│  │ AR-L0 ~ AR-L4 수준별 실행                  │   │
│  └──────────────────────────────────────────┘   │
│    ↓                                             │
│  Layer 5: VERIFICATION (검증) ✅                 │
│  ┌──────────────────────────────────────────┐   │
│  │ ① Post-Repair Validation (수리 후 검증)   │   │
│  │ ② Regression Check (회귀 검사)             │   │
│  │ ③ Rollback Trigger (롤백 트리거)           │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
    ↓
  수리 완료 / 롤백 / 사용자 승인 요청
```

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §2]

### 단계적 자율 모델 (Graduated Autonomy: AR-L0 ~ AR-L4)

| 수준 | 명칭 | 설명 | 자동 수리 범위 |
|------|------|------|---------------|
| **AR-L0** | MANUAL | 로그만 기록 | 없음 (진단만) |
| **AR-L1** | NOTIFY_ONLY | 제안만 | 없음 (사용자에게 알림만) |
| **AR-L2** | AUTO_SAFE | LOW 위험 자동 수리 | RA_001~005 (5종) |
| **AR-L3** | AUTO_MODERATE | MEDIUM 위험 자동 수리 | RA_006~010 추가 (5종) |
| **AR-L4** | AUTO_AGGRESSIVE | HIGH 위험 자동 수리 | RA_011~014 추가 (4종) |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §3]

### 수리 액션 카탈로그 (Repair Action Catalog)

**LOW Risk (AR-L2에서 자동 실행 가능):**

| 액션 ID | 설명 | 위험도 |
|---------|------|--------|
| `RA_001` | 서비스 재시작 (restart_service) | LOW |
| `RA_002` | 캐시 초기화 (clear_cache) | LOW |
| `RA_003` | 지수 백오프 재시도 (retry_with_backoff) | LOW |
| `RA_004` | 모델 폴백 전환 (switch_model_fallback) | LOW |
| `RA_005` | 속도 제한 조정 (adjust_rate_limit) | LOW |

**MEDIUM Risk (AR-L3에서 자동 실행 가능):**

| 액션 ID | 설명 | 위험도 |
|---------|------|--------|
| `RA_006` | 프롬프트 템플릿 패치 (patch_prompt_template) | MEDIUM |
| `RA_007` | 설정 파라미터 수정 (update_config_parameter) | MEDIUM |
| `RA_008` | API 키 로테이션 (rotate_api_key) | MEDIUM |
| `RA_009` | 스냅샷 롤백 (rollback_to_snapshot) | MEDIUM |
| `RA_010` | 로그 압축 (compress_logs) | MEDIUM |

**HIGH Risk (AR-L4에서 자동 실행 가능):**

| 액션 ID | 설명 | 위험도 |
|---------|------|--------|
| `RA_011` | 코드 핫픽스 (patch_code_hotfix) | HIGH |
| `RA_012` | 스키마 마이그레이션 (migrate_schema) | HIGH |
| `RA_013` | 의존성 재설치 (reinstall_dependency) | HIGH |
| `RA_014` | 벡터 인덱스 재구축 (rebuild_vector_index) | HIGH |

**NEVER_AUTO (절대 자동 수리 금지):** 🔒

| 액션 ID | 설명 |
|---------|------|
| `RA_NEVER_01` ~ `RA_NEVER_10` | 보안 규칙 변경, 승인 구조 수정 등 10개 NEVER_AUTO 영역(7개 불변구역 + 3개 운영금지) 관련 수리 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §5]

### 오류 분류 체계 (5 Categories)

| 카테고리 | 명칭 | 오류 코드 범위 | 자동 수리 가능 |
|---------|------|---------------|---------------|
| **A** | Infrastructure (인프라) | SDAR_A01~A12 | ✅ (위험도별) |
| **B** | Model/AI (모델/AI) | SDAR_B01~B08 | ✅ (위험도별) |
| **C** | Logic (로직) | SDAR_C01~C06 | ✅ (위험도별) |
| **D** | Code (코드) | SDAR_D01~D06 | ✅ (위험도별) |
| **E** | Security (보안) 🔒 | SDAR_E01~E06 | ❌ **NEVER_AUTO** |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §4]

### Kill Switch (긴급 정지 스위치) 🔒

> **모든 권한 수준에서 활성화 가능한 긴급 정지 장치**입니다. 활성화 시 **모든 자동 수리가 즉시 중단**됩니다.

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9]

### 자동 수리 제한 규칙 🔒

| 규칙 | 값 | 설명 |
|------|-----|------|
| `MAX_AUTO_REPAIRS_PER_HOUR` | **3회** | 시간당 최대 자동 수리 횟수 |
| `MAX_CONCURRENT_REPAIRS` | **1회** | 동시 수리 최대 수 |
| `SNAPSHOT_MANDATORY` | **true** | 수리 전 스냅샷 필수 |
| `NOTIFICATION_MANDATORY` | **true** | 수리 시 알림 필수 |
| `APPROVAL_TIMEOUT` | **10분** | 승인 대기 타임아웃 |
| `OBSERVATION_PERIOD` | **300초** | 수리 후 관찰 기간 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9]

### 입력 (Input)

| 항목 | 필수 여부 | 설명 |
|------|----------|------|
| `detection_signal` | 감지 시 | 건강 모니터링, 에러 패턴, 이상 탐지 신호 |
| `system_state` | 필수 | 현재 시스템 상태 정보 |
| `autonomy_level` | 필수 | 현재 자율 수준 (AR-L0~L4) |

### 출력 (Output)

| 필드 | 설명 | 예시 |
|------|------|------|
| `diagnosis` | 진단 결과 (근본 원인, 분류, 영향도) | `{category: "A", code: "SDAR_A01", impact: "LOW"}` |
| `repair_plan` | 수리 계획 | `{action: "RA_001", risk: "LOW", auto: true}` |
| `repair_result` | 수리 결과 | `{status: "success", duration: "3s"}` |
| `verification_result` | 검증 결과 | `{passed: true, regression: false}` |

### 내부 상태 (States)

| 상태 | 설명 |
|------|------|
| `SDAR_S0_MONITORING` | 정상 모니터링 중 |
| `SDAR_S1_DETECTED` | 이상 감지됨 |
| `SDAR_S2_DIAGNOSED` | 진단 완료 |
| `SDAR_S3_PRESCRIBED` | 처방(수리 계획) 생성 완료 |
| `SDAR_S4_REPAIRING` | 수리 실행 중 |
| `SDAR_S5_VERIFIED` | 수리 후 검증 중 |
| `SDAR_S6_DONE` | 수리 완료 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §7]

### 관련 이벤트 (Events)

| 이벤트 | 설명 |
|--------|------|
| `sdar.detection.triggered` | 이상 감지 트리거 |
| `sdar.diagnosis.completed` | 진단 완료 |
| `sdar.repair.started` | 수리 시작 |
| `sdar.repair.completed` | 수리 완료 |
| `sdar.verification.passed` | 검증 통과 |
| `sdar.verification.failed` | 검증 실패 (롤백 트리거) |
| `sdar.killswitch.activated` | Kill Switch 활성화 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §6]

### 에러 코드 (FailureCodes)

| 에러 코드 범위 | 카테고리 | 설명 |
|---------------|---------|------|
| `SDAR_A01~A12` | Infrastructure | 인프라 관련 오류 (서버, 네트워크, 스토리지) |
| `SDAR_B01~B08` | Model/AI | AI 모델 관련 오류 (응답 불일치, 환각) |
| `SDAR_C01~C06` | Logic | 로직 오류 (파이프라인 실패, 상태 불일치) |
| `SDAR_D01~D06` | Code | 코드 오류 (예외, 타입 에러) |
| `SDAR_E01~E06` | Security 🔒 | 보안 오류 — **NEVER_AUTO** |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §4]

### 폴백 전략 (Fallbacks)

| 폴백 ID | 설명 |
|---------|------|
| `FB_SDAR_ROLLBACK` | 수리 실패/검증 실패 시 스냅샷으로 롤백 |
| `FB_SDAR_NOTIFY` | 자동 수리 불가 시 사용자에게 알림만 전송 |
| `FB_SDAR_ESCALATE` | 수리 실패 반복 시 상위 권한에 에스컬레이션 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §6]

### 5-Gate 통합

| Gate | SDAR 연동 방식 |
|------|---------------|
| PolicyGate | 수리 액션이 정책 위반인지 검사 |
| CostGate | 수리 비용이 상한 내인지 검사 |
| ApprovalGate | MEDIUM/HIGH 위험 수리 시 승인 요청 |
| EvidenceGate | 수리 근거(진단 결과) 품질 검증 |
| SelfCheckGate | 수리 후 시스템 정상 여부 검증 |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §6]

### Policy Hook 목록

| Hook | 설명 |
|------|------|
| 5-Gate 통합 | 모든 수리 액션은 5개 Gate를 통과 |
| S-8 Self-evo Governance | Self-evo 거버넌스에 수리 결과 보고 |
| Circuit Breaker 연동 | I-20 Circuit Breaker 상태와 동기화 |
| Kill Switch | 긴급 정지 — 모든 자동 수리 즉시 중단 |
| 스냅샷 필수 | 수리 전 반드시 상태 스냅샷 저장 (LOCK) |

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §6, §9]

### 관련 모듈 (Cross-reference)

| 관련 모듈 | 연결 방식 |
|----------|----------|
| I-5 (Condition & Decision Engine) | Decision 기반 수리 판단 |
| I-6 (Self-check Engine) | 수리 후 검증 |
| I-18 (Self-evo Engine) | S-8 Self-evo Governance 연동 |
| I-19 (Approval Manager) | MEDIUM/HIGH 수리 시 승인 요청 |
| I-20 (Failure/Fallback Manager) | Circuit Breaker 연동, FailureCode 공유 |

### 버전별 활성 여부

| 항목 | V0 | V1 | V2 | V3 |
|------|----|----|----|----|
| 활성 상태 | OFF | **OFF** | **COND** | **ON** |
| 모듈 상태 | COND | COND | COND | COND |
| 자율 수준 | — | — | AR-L2 (AUTO_SAFE) | AR-L4 (AUTO_AGGRESSIVE) |
| 수리 범위 | — | — | RA_001~005 (LOW 5종) | RA_001~014 (전체 14종) |

**버전별 로드맵:**
- **V1**: OFF (미활성)
- **V2**: AR-L2 (AUTO_SAFE) — LOW 위험 수리 5종(RA_001~005)만 자동
- **V3**: AR-L4 (AUTO_AGGRESSIVE) — HIGH 위험까지 14종 자동 + S-8 완전 연동

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §10]

### 🔒 LOCK 여부

- **change_lock**: SDAR 자체는 변경 가능하나, 다음 규칙은 **ABSOLUTE LOCK**:
  - 보안 오류(CATEGORY E)는 **NEVER_AUTO** — 자동 수리 절대 금지
  - 10개 NEVER_AUTO_TARGETS(7개 불변구역 + 3개 운영금지)은 수리 대상 제외
  - 스냅샷 필수(SNAPSHOT_MANDATORY = true) — 수리 전 스냅샷 없이 실행 불가
  - 알림 필수(NOTIFICATION_MANDATORY = true)
  - 시간당 자동 수리 최대 3회(MAX_AUTO_REPAIRS_PER_HOUR = 3)
  - 동시 수리 최대 1건(MAX_CONCURRENT_REPAIRS = 1)
  - Kill Switch는 모든 권한에서 활성화 가능

[근거: VAMOS_SDAR_DESIGN_SPECIFICATION §9]

### 핵심 요약 (3줄)
1. **I-25 SDAR Engine**은 VAMOS의 "면역 시스템"으로, 5-Layer Pipeline(감지→진단→처방→수리→검증)으로 자동 복구를 수행합니다.
2. 단계적 자율(AR-L0~L4) 원칙에 따라 LOW 위험은 자동, HIGH 위험은 승인 필요하며, **보안 오류(CATEGORY E)는 NEVER_AUTO(절대 자동 금지)**입니다.
3. V2에서 AR-L2(LOW 5종 자동), V3에서 AR-L4(전체 14종 자동)로 단계적 확장되며, Kill Switch로 언제든 긴급 정지할 수 있습니다.

---

# 📋 전체 검증 체크리스트

| # | 항목 | 상태 |
|---|------|------|
| 1 | 8개 모듈 모두 작성? (I-18~I-25) | ✅ |
| 2 | 각 모듈 13가지 항목 모두 포함? | ✅ |
| 3 | I-19의 LOCK 표시? (change_lock=true) | ✅ |
| 4 | I-25 SDAR 5-Layer 설명? | ✅ |
| 5 | 비유 설명 포함? (8개 모듈 모두) | ✅ |
| 6 | 근거 SOT 참조 표기? | ✅ |
| 7 | NEVER_AUTO 규칙 명시? (I-18, I-19, I-25) | ✅ |
| 8 | 버전별 활성 여부 표 포함? (V0/V1/V2/V3) | ✅ |
| 9 | Circuit Breaker 3상태 설명? (I-20) | ✅ |
| 10 | 36 FailureCode → 23 Fallback 매핑? (I-20) | ✅ |

---

# 📊 I-18 ~ I-25 버전별 활성 요약표

| 모듈 | 상태 | V0 | V1 | V2 | V3 | LOCK |
|------|------|----|----|----|----|------|
| I-18 Self-evo Engine | EXP | OFF | OFF | OFF | **ON** | Self-evo 원칙 LOCK |
| I-19 Approval Manager | CORE(LOCK) | ON | **ON** | **ON** | **ON** | **change_lock=true** 🔒 |
| I-20 Failure/Fallback Manager | CORE | ON | **ON** | **ON** | **ON** | P2 CB 승인 LOCK |
| I-21 Source Evolution | EXP | OFF | OFF | OFF | **ON** | — |
| I-22 Task/Project Manager | COND | OFF | OFF | **COND** | **ON** | — |
| I-23 Doc/Code Structuring | COND | OFF | OFF | **COND** | **ON** | — |
| I-24 Knowledge Graph Engine | EXP | OFF | OFF | OFF | **ON** | — |
| I-25 SDAR Engine | COND | OFF | OFF | **COND** | **ON** | 보안 NEVER_AUTO 🔒 |

[근거: CLAUDE.md §6]
