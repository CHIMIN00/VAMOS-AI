# VAMOS v10 Phase 2: PART2 수정 계획 (Patch Plan)

> **파이프라인**: v10 Phase 2 — 대화 27
> **생성일**: 2026-03-09
> **대상**: `VAMOS_구현가이드_PART2_구현단계.md` v21.0.0 → v22.0.0
> **Ripple Map**: W-33 약점 방어

---


> **FN Reconciliation Note**: Phase 1.5 자동 탐지 FN=51, POSSIBLE_FN=42이나,
> 본 Patch Plan은 확정(confirmed) 수치 FN=38, POSSIBLE_FN=37을 사용.
> 차이(13건, 5건)는 cross-version(다른 에이전트) MISSING으로 잔존하며 보수적 처리됨.
> 상세: `consolidated_missing.json` → `_meta.fn_reconciliation` 참조.

## 1. 수정 범위 요약

| 우선순위 | 대상 | 건수 | PART2 수정 유형 |
|---------|------|------|----------------|
| **P1** | BLOCKER | 3 | §5 테이블 행 추가 + 실행 가이드 추가 |
| **P2** | HIGH PRIMARY (비-STEP7) | ~143 | §3/§4/§5 테이블 행 추가 |
| **P3** | MEDIUM PRIMARY | ~116 | 선별 후 §3/§4/§5 추가 |
| **P4** | FP→MISSING 전환 | 3 | 매핑 상태 보정 |
| **P5** | STEP7 통합 처리 | ~620 | §6 참조 또는 NOT_APPLICABLE |
| **P6** | 수량/메트릭 갱신 | - | §6.13 작업량, §7 GO/NO-GO |

---

## 2. BLOCKER Ripple Map (3건) — 즉시 실행

### PATCH-B01: Agent Swarm (PARL) 병렬 실행

```json
{
  "patch_id": "PATCH-B01",
  "feature_ids": ["D202-130", "D205-067"],
  "feature_names": [
    "Agent Swarm (PARL) 병렬 실행 구현",
    "PARL Agent Swarm Execute 단계"
  ],
  "severity": "BLOCKER",
  "sot_references": [
    "D2.0-02 §11.15.2 — Agent Swarm (PARL) 패턴 정의",
    "D2.0-05 §12.17.1 — PARL Agent Swarm Execute 단계",
    "D2.0-05 §12.5.1 — TEE 루프 Execute에 PARL 옵션",
    "D2.0-04 §INFRA — PARL 에이전트 풀 자동 확장/축소",
    "D2.0-07 §PARL — PARL 보상 패턴"
  ],
  "target_section": "§5.2 V3-Phase 2 (L2422~L2439)",
  "target_line": 2439,
  "action": "테이블 행 15~16 추가",
  "content_to_add": [
    "| 15 | Agent Teams | **PARL Agent Swarm** | TEE Execute에 PARL 패턴 통합, 최대 100 병렬 서브에이전트, RL 기반 병렬화 학습 (VAMOS_AGENT_TEAMS_SPEC §9, D2.0-05 §12.17.1) |",
    "| 16 | Agent Teams | **PARL 인프라** | 에이전트 풀 자동 확장/축소, 보상 스케줄(초기=병렬화, 후기=품질80%+효율20%), Decision Aggregator (D2.0-04, D2.0-07) |"
  ],
  "ripple_effects": [
    {
      "section": "§5.2 실행 가이드 (L2454~L2464)",
      "impact_type": "항목 추가",
      "detail": "사용자 작업 #9: PARL RL 학습 파이프라인 환경 준비, 보상 함수 초기 가중치 설정"
    },
    {
      "section": "§5.2 AI 프롬프트 (L2468~)",
      "impact_type": "그룹 추가",
      "detail": "그룹 15: PARL Agent Swarm → backend/vamos_core/agent_teams/parl/ 신규 디렉토리"
    },
    {
      "section": "§6.7 Agent Teams 상세 (L3103~L3164)",
      "impact_type": "V3 섹션 추가",
      "detail": "### V3 추가: PARL Agent Swarm 상세 (PARL 패턴 정의, 보상 스케줄, Decision Aggregator, 100 병렬 상한)"
    },
    {
      "section": "§6.13 작업량 (L3717)",
      "impact_type": "수량 갱신",
      "detail": "V3 기타 행: ~17 → ~22 (+5 SP), 합계 ~454 → ~459"
    },
    {
      "section": "§7.4 V3 GO/NO-GO (L3814~L3831)",
      "impact_type": "항목 추가 검토",
      "detail": "PARL 병렬 실행 안정성 검증 항목 추가 가능 (#12)"
    },
    {
      "section": "§5.2 단계 완료 검증 (L2662~L2681)",
      "impact_type": "Stage Gate 추가",
      "detail": "PARL Agent Swarm 병렬 실행 테스트 PASS 조건 추가"
    }
  ]
}
```

### PATCH-B02: Agent Specialization Protocol

```json
{
  "patch_id": "PATCH-B02",
  "feature_ids": ["D205-076"],
  "feature_names": [
    "Agent Specialization Protocol (자동 fork/특화/retire)"
  ],
  "severity": "BLOCKER",
  "sot_references": [
    "D2.0-05 §12.19 — Agent Specialization Protocol",
    "PLAN-3.0 P6-AGT-04 — 자기 복제",
    "D2.0-05 §12.17.3 — PARL 수준 자동 스케일링"
  ],
  "target_section": "§5.3 V3-Phase 3 (L2682~L2693)",
  "target_line": 2693,
  "action": "테이블 행 9 추가",
  "content_to_add": [
    "| 9 | **Agent Specialization** | 에이전트 자동 fork/특화/retire 프로토콜 (P6-AGT-04, D2.0-05 §12.19) |"
  ],
  "ripple_effects": [
    {
      "section": "§5.3 실행 가이드 (L2706~L2716)",
      "impact_type": "항목 추가",
      "detail": "사용자 작업 #9: Agent Specialization 정책 정의 (fork 조건, 특화 기준, retire 트리거)"
    },
    {
      "section": "§5.3 AI 프롬프트 (L2718~)",
      "impact_type": "섹션 추가",
      "detail": "## 9. Agent Specialization → backend/vamos_core/agent_teams/specialization/"
    },
    {
      "section": "§6.7 Agent Teams 상세 (L3103~L3164)",
      "impact_type": "V3 섹션 추가",
      "detail": "### V3 추가: Agent Specialization Protocol (fork/특화/retire 규칙, PARL 연동)"
    },
    {
      "section": "§6.13 작업량 (L3717)",
      "impact_type": "수량 갱신",
      "detail": "V3 기타 행: ~22 → ~25 (+3 SP)"
    },
    {
      "section": "§5.3 단계 완료 검증 (L2818~L2836)",
      "impact_type": "Stage Gate 추가",
      "detail": "Agent Specialization Protocol fork/retire 사이클 테스트 PASS 조건 추가"
    }
  ]
}
```

---

## 3. HIGH PRIMARY Ripple Map (비-STEP7, ~143건)

### 3.1 §3 V1 추가 대상 — 주요 그룹

#### PATCH-H01: EVX 검증 모듈 Phase 배정

```json
{
  "patch_id": "PATCH-H01",
  "feature_ids": ["CLAUDE-089", "CLAUDE-090", "CLAUDE-091", "CLAUDE-092", "CLAUDE-093"],
  "feature_names": [
    "EVX-1 Code-as-Policy 검증",
    "EVX-2 Adversarial 검증",
    "EVX-3 Log-prob Confidence 검증",
    "EVX-4 Thought Buffer 검증",
    "EVX-5 Gen-Verify-Learn 검증"
  ],
  "severity": "HIGH",
  "analysis": "EVX-1~6은 이미 §5.2 V3-Phase 2 행 13에 배정됨. V1 MISSING은 version_scope V1,V2,V3에 의한 M-2 CROSSCHECK. 실제 구현은 V3에서만 수행. MISSING 판정은 정상.",
  "action": "NO_CHANGE — §5.2에 이미 존재. M-2 MISSING은 버전 범위에 의한 정상 분류",
  "ripple_effects": []
}
```

#### PATCH-H02: 비용 관련 구현 항목 Phase 배정

```json
{
  "patch_id": "PATCH-H02",
  "feature_ids": ["P30-009", "P30-029", "P30-058", "P30-061", "CLAUDE-108"],
  "feature_names": [
    "DomainScore 종합 점수화 공식 구현",
    "비용 기반 뇌 선택 정책 구현",
    "비용 3단계 경보 체계 (70%/85%/95%)",
    "고비용 모델 사용 제약 구현",
    "대화 턴 상한 구현 (P0=5, P1=10, P2=20)"
  ],
  "severity": "HIGH",
  "analysis": "이들은 PART2 §3 V1-Phase 1 ORANGE CORE 완성 또는 §6.5 보안/§6.7 Agent Teams에서 LOCK으로 정의됨. Phase 구현 테이블에 명시적 행은 없으나 I-5 Decision Engine, I-8 Policy Engine, I-9 Cost Manager의 하위 구현으로 커버됨.",
  "target_section": "§3 V1-Phase 1 (L1393~L1474)",
  "action": "REVIEW — 상위 모듈(I-5, I-8, I-9) 실행 가이드에 하위 항목으로 명시 권고",
  "ripple_effects": [
    {
      "section": "§3 V1-Phase 1 실행 가이드",
      "impact_type": "상세화",
      "detail": "I-5/I-8/I-9 구현 시 하위 항목(DomainScore, 비용 경보, 턴 상한) 구현 체크리스트 추가"
    }
  ]
}
```

#### PATCH-H03: Phase 1.5 FP→MISSING 전환 3건

```json
{
  "patch_id": "PATCH-H03",
  "feature_ids": ["S7AE-035", "AINV-003", "AINV-066"],
  "feature_names": [
    "Citation 시스템",
    "5-Agent 워크플로우 오케스트레이션",
    "Docker Compose 전체 스택 설정"
  ],
  "severity": "HIGH/MEDIUM",
  "analysis": [
    "S7AE-035: Citation 시스템은 V2 기능. §4 V2-Phase 2에 E-series 또는 별도 항목으로 추가 검토.",
    "AINV-003: 5-Agent 오케스트레이션은 §6.8 AI Investing에 기재되어 있으나 §3 V1-Phase 6에 명시적 행 없음. 기존 '5-Agent Pipeline' 행(L1703)이 커버하나 키워드 불일치.",
    "AINV-066: Docker Compose는 §4 V2-Phase 1 인프라 마이그레이션(L1866)에서 docker-compose.v2.yml로 커버됨. V0 단계 설정은 별도 불필요."
  ],
  "action": "S7AE-035 → §4 추가 검토, AINV-003 → NO_CHANGE (기존 커버), AINV-066 → NO_CHANGE (V2에서 커버)",
  "ripple_effects": []
}
```

### 3.2 §4 V2 추가 대상

#### PATCH-H04: V2 UI/기능 추가

```json
{
  "patch_id": "PATCH-H04",
  "feature_ids": ["CLAUDE-203"],
  "feature_names": ["V2 UI: PWA (Next.js) 추가"],
  "severity": "MEDIUM",
  "analysis": "§4 V2-Phase 2 또는 V2-Phase 3에 PWA 구현 항목 추가 검토. 현재 §4에 UI 관련 명시적 항목이 없음.",
  "target_section": "§4 V2-Phase 2 또는 V2-Phase 3",
  "action": "REVIEW — V2 UI 진화는 기존 §4 범위를 넘을 수 있음. 사용자 판단 필요.",
  "ripple_effects": [
    {
      "section": "§6.1 UI/UX 상세",
      "impact_type": "PWA 관련 항목 확인",
      "detail": "§6.1에 PWA 관련 항목이 있는지 확인 후 Phase 배정"
    }
  ]
}
```

### 3.3 §5 V3 추가 대상

#### PATCH-H05: V3 AI Investing 고급

```json
{
  "patch_id": "PATCH-H05",
  "feature_ids": ["DA1-016", "DA1-019"],
  "feature_names": [
    "섹터/피어 그룹 비교 분석 모듈 (PER/PBR/EV-EBITDA)",
    "옵션/파생상품 분석 (그릭스/Black-Scholes/변동성 서피스)"
  ],
  "severity": "HIGH",
  "analysis": "§5.3 V3-Phase 3에 AI Investing 고급 분석 항목 추가. 현재 §6.8 AI Investing 상세에 5-Agent Pipeline과 51% Gate만 기재.",
  "target_section": "§5.3 V3-Phase 3 (L2682~L2693)",
  "action": "REVIEW — AI Investing V3 고급 기능은 §6.8에 상세가 있을 수 있으므로 Phase 배정만 필요",
  "ripple_effects": [
    {
      "section": "§6.8 AI Investing 상세 (L3167~)",
      "impact_type": "항목 확인",
      "detail": "섹터 분석/파생상품 모듈이 §6.8에 있는지 확인"
    }
  ]
}
```

---

## 4. STEP7 추정 항목 처리 방안 (620건)

### 4.1 분류 기준

| 분류 | 기준 | 추정 건수 | 처리 |
|------|------|----------|------|
| **TITLE_ONLY_NA** | 제목만 존재, 스펙 없음 | ~140 | NOT_APPLICABLE 재분류 |
| **COVERED_BY_UPPER** | 상위 모듈에서 이미 커버 | ~200 | NO_CHANGE (기존 매핑 유지) |
| **NEEDS_DETAIL** | 상세 스펙 있으나 Phase 미배정 | ~180 | §6 참조로 처리 |
| **REAL_GAP** | 실제 PART2 보강 필요 | ~100 | P2 선별 추가 |

### 4.2 시스템설계/데이터설계 시리즈 (S7AE-448~537, 16건)

M-4에서 HIGH로 보고된 V3 STEP7 항목. "C-097~C-104 시스템설계", "D-075~D-082 데이터설계" 형태로 **TITLE_ONLY**에 해당.

**권고**: NOT_APPLICABLE 재분류. 실제 시스템/데이터 설계는 각 모듈 SRC(D2.0-02~D2.1-D7)에서 정의되며, PART2 §2~§5에 개별 행으로 추가할 성격이 아님.

---

## 5. 수정 순서 (대화 28 실행 계획)

```
Step 1: BLOCKER 3건 수정 (PATCH-B01, PATCH-B02)
  → §5.2 테이블 행 추가 (15~16행)
  → §5.3 테이블 행 추가 (9행)
  → §5.2/§5.3 실행 가이드 + AI 프롬프트 추가
  → §6.7 V3 Agent Teams 상세 추가
  → §6.13 수량 갱신 (V3 기타: ~17 → ~25)
  → §5.2/§5.3 Stage Gate 추가
  → §7.4 GO/NO-GO 검토

Step 2: HIGH PRIMARY 비-STEP7 항목 (PATCH-H02~H05) — 사용자 승인 후
  → §3 V1-Phase 1 실행 가이드 상세화
  → §4 V2 PWA 검토
  → §5 V3 AI Investing 검토

Step 3: STEP7 항목 재분류 — 사용자 승인 후
  → TITLE_ONLY 140건 NOT_APPLICABLE 처리
  → COVERED_BY_UPPER 200건 확인
  → REAL_GAP 100건 선별 추가

Step 4: 메타데이터 갱신
  → PART2 버전 v21.0.0 → v22.0.0
  → 변경 이력 추가
  → 행번호 매핑 테이블 생성
```

---

## 6. Ripple Map 종합 (JSON)

```json
{
  "ripple_map": [
    {
      "patch_id": "PATCH-B01",
      "added_items": ["D202-130", "D205-067"],
      "target_section": "§5.2 V3-Phase 2",
      "target_line": 2439,
      "affected_sections": [
        {"section": "§5.2 실행 가이드 (L2454)", "impact_type": "항목 추가", "detail": "사용자 작업 #9: PARL 환경 준비"},
        {"section": "§5.2 AI 프롬프트 (L2468)", "impact_type": "그룹 추가", "detail": "그룹 15: PARL Agent Swarm"},
        {"section": "§6.7 Agent Teams (L3103)", "impact_type": "V3 섹션 신규", "detail": "PARL Agent Swarm 상세 추가"},
        {"section": "§6.13 작업량 (L3717)", "impact_type": "수량 갱신", "detail": "V3 기타 ~17→~22 (+5 SP)"},
        {"section": "§7.4 V3 GO/NO-GO (L3814)", "impact_type": "항목 추가 검토", "detail": "PARL 안정성 검증 (#12)"},
        {"section": "§5.2 Stage Gate (L2662)", "impact_type": "항목 추가", "detail": "PARL 병렬 실행 테스트 PASS"}
      ]
    },
    {
      "patch_id": "PATCH-B02",
      "added_items": ["D205-076"],
      "target_section": "§5.3 V3-Phase 3",
      "target_line": 2693,
      "affected_sections": [
        {"section": "§5.3 실행 가이드 (L2706)", "impact_type": "항목 추가", "detail": "사용자 작업 #9: Specialization 정책 정의"},
        {"section": "§5.3 AI 프롬프트 (L2718)", "impact_type": "섹션 추가", "detail": "## 9. Agent Specialization"},
        {"section": "§6.7 Agent Teams (L3103)", "impact_type": "V3 섹션 신규", "detail": "Specialization Protocol 상세 추가"},
        {"section": "§6.13 작업량 (L3717)", "impact_type": "수량 갱신", "detail": "V3 기타 ~22→~25 (+3 SP)"},
        {"section": "§5.3 Stage Gate (L2818)", "impact_type": "항목 추가", "detail": "Specialization fork/retire 테스트 PASS"}
      ]
    },
    {
      "patch_id": "PATCH-H02",
      "added_items": ["P30-009", "P30-029", "P30-058", "P30-061", "CLAUDE-108"],
      "target_section": "§3 V1-Phase 1",
      "target_line": 1456,
      "affected_sections": [
        {"section": "§3 V1-Phase 1 실행 가이드", "impact_type": "상세화", "detail": "I-5/I-8/I-9 하위 구현 체크리스트 추가"}
      ]
    }
  ]
}
```

---

## 7. 사용자 확인 요청

Phase 2 수정을 진행하기 전 아래 사항의 확인이 필요합니다:

### 확인 1: BLOCKER 수정 승인

| # | Patch | 내용 | 승인? |
|---|-------|------|-------|
| 1 | PATCH-B01 | §5.2에 PARL Agent Swarm 2행 추가 + 6개 연쇄 수정 | |
| 2 | PATCH-B02 | §5.3에 Agent Specialization 1행 추가 + 5개 연쇄 수정 | |

### 확인 2: STEP7 처리 방침

| 옵션 | 설명 |
|------|------|
| A | STEP7 620건 전수 NOT_APPLICABLE 처리 (PART2는 현행 유지) |
| B | TITLE_ONLY 140건만 NOT_APPLICABLE, 나머지 480건은 §6 참조로 PARTIAL 유지 |
| C | REAL_GAP ~100건 선별 추가 + 나머지 NOT_APPLICABLE/PARTIAL |

### 확인 3: HIGH/MEDIUM PRIMARY 처리

| 옵션 | 설명 |
|------|------|
| A | 비-STEP7 HIGH PRIMARY ~143건 전수 PART2 추가 |
| B | BLOCKER 3건만 추가, 나머지는 §6 참조로 충분 판단 |
| C | 선별 추가 (사용자가 추가 대상 지정) |

---

**대화 27 완료. 사용자 확인 후 대화 28에서 PART2 수정 실행.**

---

## 8. 결정사항 (대화 28 기록)

> **기록일**: 2026-03-09

### PATCH-H04: V2 UI PWA (CLAUDE-203)
- **Status**: NO_CHANGE
- **Reason**: V2 데스크톱 중심, PWA는 V3 모바일 확장에서 처리

### PATCH-H05: V3 AI Investing 고급 (DA1-016, DA1-019)
- **Status**: ADD
- **Reason**: §6.8 상세 존재 확인 → §5 Phase 배정 추가
- **Action**: §5.3 V3-Phase 3 테이블에 AI Investing 고급 분석 행 추가 (섹터/피어 비교, 파생상품 분석)

### STEP7 620건 처리 방침
- **Decision**: 옵션 B — TITLE_ONLY만 NA, 실질 구현 항목 MISSING 유지
- **Detail**: TITLE_ONLY ~140건 → NOT_APPLICABLE 재분류, 나머지 ~480건 → §6 참조로 PARTIAL 유지

### S7AE-035: Citation 시스템
- **Status**: NO_CHANGE
- **Reason**: V2 §4에서 별도 검토 (PATCH-H03에서 이미 '§4 추가 검토'로 기록)

---

## 9. 대화 28.5 — Step 1/2 분류 결과 반영 (2026-03-10)

> **기록일**: 2026-03-10
> **목적**: Step 1 5차 재검토 결과를 Patch Plan에 반영

### 9.1 Step 1에서 추가 제외된 항목 (57건, RESOLVED 10건 제외)

| 분류 | 건수 | Patch Plan 영향 |
|------|------|----------------|
| SUB_FEATURE_OF_EXISTING | 45 | P2(HIGH PRIMARY) 대상에서 27건 제외, P3(MEDIUM PRIMARY) 대상에서 18건 제외 |
| SKIP_CONFIRMED | 10 | P2/P3/P6 대상에서 제외 |
| SECTION6_DETAILED | 1 | P2 대상에서 제외 (CLIB-023) |
| DUPLICATE | 1 | P2 대상에서 제외 (D207-108) |

### 9.2 수정 범위 갱신 (1,068건 → 1,001건 기준)

| 우선순위 | 대상 | 원래 건수 | 갱신 건수 | PART2 수정 |
|---------|------|----------|----------|-----------|
| **P1** | BLOCKER | 3 | 0 (**전부 RESOLVED**) | 완료 |
| **P2** | HIGH PRIMARY (비-STEP7) | ~143 | ~98 | 불필요 (COVERED_BY_UPPER_MODULE) |
| **P3** | MEDIUM PRIMARY | ~116 | ~98 | 불필요 (SKIP/PARTIAL) |
| **P4** | FP→MISSING 전환 | 3 | 0 (**SKIP 또는 NO_CHANGE 확정**) | 완료 |
| **P5** | STEP7 통합 처리 | ~620 | ~620 | 불필요 (§6 참조 유지) |
| **P6** | 수량/메트릭 갱신 | - | - | 완료 (§6.13, §7.4) |

### 9.3 PART2 추가 수정 필요 여부

**결론: 추가 수정 불필요**

- BLOCKER 3건: 전부 RESOLVED (PATCH-B01, B02)
- HIGH PRIMARY 비-STEP7 잔여 ~98건: COVERED_BY_UPPER_MODULE — §6 상위 모듈에서 커버
- SUB_FEATURE 45건: 상위 모듈에 종속 확인 (5차 재검토, 아키텍처 근거 확보)
- STEP7 620건: 옵션 B 결정 유지 (TITLE_ONLY NA + 실질 항목 §6 참조)
- MEDIUM/LOW: SKIP 또는 PARTIAL 유지

### 9.4 Patch Plan 최종 상태

| Patch | 상태 | 비고 |
|-------|------|------|
| PATCH-B01 | APPLIED | §5.2 행 15-16, §6.7 PARL 상세 |
| PATCH-B02 | APPLIED | §5.3 행 9, §6.7 Specialization 상세 |
| PATCH-H02 | APPLIED | §3 I-5/I-8/I-9 체크리스트 |
| PATCH-H05 | APPLIED | §5.3 행 10 AI Investing 고급 |
| PATCH-H01 | NO_CHANGE | EVX §5.2 이미 존재 |
| PATCH-H03 | NO_CHANGE | 기존 PART2에서 커버 |
| PATCH-H04 | NO_CHANGE | V3 모바일 확장에서 처리 |
| P2-P6 잔여 | 추가 수정 불필요 | Step 1/2 분류 결과 확정 |

**→ 대화 29 (재검증)으로 진행 가능**
