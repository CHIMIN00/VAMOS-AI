# v13 Phase 0-A: SOT 68개 파일 핵심 값 전수 추출

> **버전**: v13.2.0 (2계층 검증 시스템 반영)
> **대화**: 대화 1~3 (3개 대화에 분산)
> **목표**: SOT 68개 파일(89,363줄)에서 크로스 매칭 대상 핵심 값 전수 추출
> **성격**: v13 Phase 0의 기반 데이터 생성. Phase 0-B 크로스 매칭의 입력.
> **선행 조건**: 없음 (v13 첫 번째 작업)
> **검증**: 각 EA 산출물은 /quality-gate (GOLD/SILVER) 통과 필수

---

## Pre-check Protocol

**매 대화 시작 시 반드시 수행:**

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v13_plan.md (§5 Phase 0 부분)
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v13\prompts\phase0_A_extraction_prompt.md
③ v13_results 디렉토리 존재 확인: D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\
④ 이전 대화 산출물 확인:
   - 대화 1: 없음 (첫 대화)
   - 대화 2: 대화 1 산출물 (EA-1~EA-5) 존재 확인
   - 대화 3: 대화 1~2 산출물 (EA-1~EA-10) 존재 확인
⑤ 확인 완료 후 작업 시작
```

---

## 핵심 원칙: 환각/오류 방지 규칙 (R1~R6)

> **이 규칙은 모든 EA 에이전트에 반드시 적용됩니다.**

```
R1: 모든 수치 비교 시 에이전트는 반드시 SOT 원문 라인번호를 인용한다
R2: JSON 출력에 source_file + source_line 필수 포함
R3: 파일 89,363줄은 68개 파일 × 파일별 개별 처리 → 크로스 참조만 별도
R4: 적대적 에이전트는 CRITICAL 판정 시 반드시 2개 이상의 SOT 근거를 제시
R5: 동일 항목이 3개 이상 SOT에서 서로 다른 값이면 SOURCE_CONFLICT로 에스컬레이션
R6: 세션 종료 시 미완료 항목 목록을 JSON으로 저장 → 다음 세션에서 자동 로드
```

**추가 방지 규칙:**
- **부분 읽기 금지**: SOT 파일은 반드시 전체 읽기. limit 사용 시 나머지 반드시 후속 읽기
- **환각 금지**: 파일에 없는 값을 생성하지 않는다. 반드시 원문 텍스트를 인용
- **추론 금지**: 값이 명시되지 않으면 `"value": null, "note": "명시되지 않음"` 으로 기록
- **라인번호 직접 확인**: source_line은 파일 읽기 시 실제 확인한 행 번호만 기재

---

## 스킬 에이전트 실행 규칙

> **필수**: 본 Phase의 작업 단위는 반드시 **Agent tool(스킬 에이전트)**을 사용하여 병렬 실행합니다.

1. **병렬 실행**: 독립적인 EA 에이전트는 Agent tool로 동시 투입 (대화당 최대 5개)
2. **동일 템플릿**: 모든 에이전트는 본 프롬프트에 정의된 추출 템플릿을 준수
3. **결과 저장**: 각 에이전트 결과는 개별 JSON 파일로 디스크 저장
4. **전체 읽기 강제**: 각 파일을 Read tool로 읽을 때 전체를 읽는다. 2000줄 초과 파일은 offset으로 나눠서 전체 읽기

---

## 2계층 품질 게이트 (v13.2.0 신규 — 각 EA 산출물 필수)

> **각 EA JSON 저장 후 반드시 아래 검증 파이프라인을 수행합니다.**
> Hook이 자동으로 Layer A를 실행하며, CRITICAL이 있으면 저장이 차단됩니다.

### Layer A: 결정론적 검증 (자동 — Hook이 실행)

EA JSON을 Write tool로 저장하면 PreToolUse Hook이 자동으로 아래를 실행합니다:

```bash
python deterministic_validator.py <EA_JSON_PATH>
```

**DV-1~DV-7 검증 (프로그램 — AI 판단 0%)**:
- DV-1: JSON 스키마 필수 필드 존재 (metadata 7개 + item 8개)
- DV-2: metadata.categories 합계 = total_items_extracted = items 길이
- DV-3: source_line이 0 초과 & 파일 줄 수 이하
- DV-4: source_text 키워드가 SOT 파일 해당 줄 ±3줄에 존재
- DV-5: item_id 연속성 (건너뛴 번호)
- DV-6: value_type vs value 실제 타입 일치
- DV-7: COUNT key ↔ LIST key 길이 교차 검증

**CRITICAL ≥ 1 → 저장 차단. 해당 항목 수정 후 재저장.**

### Layer B: AI 의미적 검증 (수동 — /quality-gate 실행)

Layer A 통과 후 `/quality-gate <EA_JSON_PATH>` 실행:

- SV-1: 의미적 정확성 (key/context가 맥락에 맞는지)
- SV-2: 추출 완전성 (SOT에 있는데 JSON에 없는 항목)
- SV-3: 표준 키 적절성
- AD-1~AD-3: 적대적 감사 (환각/변조/약점 탐지)

**판정: GOLD/SILVER → Phase 0-B 진행 가능 / REJECT → 수정 후 재추출**

### 검증 결과 저장 위치

```
v13_results/phase0/extraction/
├── v13_EA01_claude_md.json              ← EA 산출물
├── validation/
│   ├── v13_EA01_claude_md_dv_result.json    ← Layer A 결과 (자동)
│   └── v13_EA01_claude_md_sv_result.json    ← Layer B 결과
├── audit/
│   └── v13_EA01_claude_md_audit.json        ← 적대적 감사 결과
└── sot_check/
    └── v13_EA01_claude_md_sot_check.json    ← SOT 대조 결과
```

---

## 추출 대상: 8개 카테고리 (C1~C8)

> 각 EA 에이전트는 담당 파일에서 아래 8개 카테고리에 해당하는 값을 **빠짐없이** 추출합니다.

| # | 카테고리 | 추출 대상 | 예시 |
|---|----------|----------|------|
| C1 | **수치/파라미터** | 숫자로 표현된 모든 값 (개수, 비율, 금액, 시간, 크기) | "모듈 81개", "타임아웃 15분", "비용 ₩500" |
| C2 | **카운트/목록** | 항목 수를 명시한 요약 + 해당 상세 목록 | "7개 불변구역: [목록]", "COND 10개: [목록]" |
| C3 | **분류/계층** | 모듈/기능/항목의 분류 체계 | "3-tier: CORE/COND/EXP", "4-tier: +RE-ADD" |
| C4 | **명칭/용어** | 모듈명, 시스템명, 기능명 | "Decision Engine", "Condition & Decision Engine" |
| C5 | **범위/스코프** | 특정 개념이 포함하는 범위 | "불변구역 = safety_rules + cost_ceiling + ..." |
| C6 | **버전 범위** | V0/V1/V2/V3 활성화 정보 | "L4: V2+", "E-009: V1~V3" |
| C7 | **수식/임계값** | 계산식, 임계값, LOCK/FREEZE 값 | "LOCK=32", "cost_ceiling=₩50,000/일" |
| C8 | **참조** | 다른 SOT 파일/섹션을 참조하는 내용 | "§6.3 참조", "PHASE_B4 참조" |

---

## 추출 JSON 템플릿

```json
{
  "item_id": "EA-{agent_num}_{seq:3자리}",
  "category": "C1|C2|C3|C4|C5|C6|C7|C8",
  "source_file": "파일명 (확장자 포함)",
  "source_line": 123,
  "source_text": "원문 텍스트 (100자 이내, 원문 그대로 복사)",
  "key": "항목의 식별 키 (예: 'CORE_MODULE_COUNT', 'TIMEOUT_DEFAULT')",
  "value": "추출된 값 (숫자, 문자열, 배열 등 원본 형태 그대로)",
  "value_type": "number|string|list|boolean",
  "context": "해당 값이 어떤 맥락에서 사용되는지 1줄 설명"
}
```

**필수 제약:**
- `source_text`: 반드시 파일 원문을 그대로 복사. 요약/의역 금지
- `source_line`: 반드시 Read tool에서 확인한 실제 행 번호
- `value`: 파일에 명시된 값만. 추론/계산하여 생성한 값 금지
- `key`: 동일 개념은 모든 에이전트가 동일한 key를 사용 (아래 표준 키 목록 참조)

---

## 표준 키 목록 (key 통일용)

> 동일 개념이 여러 SOT에서 등장할 때 크로스 매칭이 가능하도록 key를 통일합니다.
> 아래 목록에 없는 항목은 `{카테고리}_{대상}_{속성}` 형식으로 자유 생성 가능.

### 수치/카운트 관련
| 표준 key | 의미 |
|----------|------|
| `TOTAL_MODULE_COUNT` | 전체 모듈 수 |
| `CORE_MODULE_COUNT` | CORE 모듈 수 |
| `COND_MODULE_COUNT` | COND 모듈 수 |
| `EXP_MODULE_COUNT` | EXP 모듈 수 |
| `READD_MODULE_COUNT` | RE-ADD 모듈 수 |
| `IMMUTABLE_ZONE_COUNT` | 불변구역 수 |
| `NEVER_AUTO_COUNT` | NEVER_AUTO 항목 수 |
| `COND_PRIORITY_CRITICAL` | COND CRITICAL 수 |
| `COND_PRIORITY_HIGH` | COND HIGH 수 |
| `COND_PRIORITY_MEDIUM` | COND MEDIUM 수 |
| `COND_PRIORITY_LOW` | COND LOW 수 |
| `STAGE_GATE_COUNT` | Stage Gate 수 |
| `AI_PROMPT_COUNT` | AI 프롬프트 수 |
| `API_ENDPOINT_COUNT` | API 엔드포인트 수 |

### 목록 관련
| 표준 key | 의미 |
|----------|------|
| `IMMUTABLE_ZONE_LIST` | 불변구역 목록 |
| `NEVER_AUTO_LIST` | NEVER_AUTO 목록 |
| `CORE_MODULE_LIST` | CORE 모듈 목록 |
| `COND_MODULE_LIST` | COND 모듈 목록 |
| `EXP_MODULE_LIST` | EXP 모듈 목록 |
| `READD_MODULE_LIST` | RE-ADD 모듈 목록 |
| `GUARDRAILS_LAYER_LIST` | Guardrails 계층 목록 |
| `V0_STEP_LIST` | V0 STEP 목록 |
| `V1_PHASE_LIST` | V1 Phase 목록 |

### 분류 체계 관련
| 표준 key | 의미 |
|----------|------|
| `MODULE_TIER_SYSTEM` | 모듈 분류 체계 (3-tier/4-tier) |
| `MODULE_TIER_COUNT` | 분류 tier 수 |
| `GUARDRAILS_LAYER_COUNT` | Guardrails 계층 수 |

### 수식/임계값 관련
| 표준 key | 의미 |
|----------|------|
| `COST_CEILING_DAILY` | 일일 비용 상한 |
| `COST_CEILING_MONTHLY` | 월간 비용 상한 |
| `TIMEOUT_DEFAULT` | 기본 타임아웃 |
| `LOCK_{대상}` | LOCK 값 (예: LOCK_CORE_COUNT) |

### 버전 범위 관련
| 표준 key | 의미 |
|----------|------|
| `VERSION_SCOPE_{모듈ID}` | 특정 모듈의 활성화 버전 |

---

## 대화별 작업 상세

### ═══ 대화 1: EA-1 ~ EA-5 (핵심 SOT) ═══

#### EA-1: CLAUDE.md

**대상 파일 (1개, 697줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | CLAUDE.md | `D:\VAMOS\docs\sot\CLAUDE.md` | 697 |

**추출 초점**:
- §7.3 불변구역 목록 + 수 (C2, C5: `IMMUTABLE_ZONE_COUNT`, `IMMUTABLE_ZONE_LIST`)
- §17 SDAR NEVER_AUTO 목록 + 수 (C2, C5: `NEVER_AUTO_COUNT`, `NEVER_AUTO_LIST`)
- 모듈 분류 체계 (C3: `MODULE_TIER_SYSTEM`, `MODULE_TIER_COUNT`)
- 모듈 목록 (C2: `CORE_MODULE_LIST`, `COND_MODULE_LIST`, `EXP_MODULE_LIST`, `READD_MODULE_LIST`)
- 모듈 수 (C1: `CORE_MODULE_COUNT`, `COND_MODULE_COUNT`, `EXP_MODULE_COUNT`, `READD_MODULE_COUNT`, `TOTAL_MODULE_COUNT`)
- 모든 LOCK/FREEZE 값 (C7)
- 모든 수치 (C1)
- 다른 SOT 참조 (C8)

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA01_claude_md.json`

---

#### EA-2: BASE-1.3 + PLAN-3.0

**대상 파일 (2개, 7,680줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | BASE-1.3 | `D:\VAMOS\docs\sot\BASE-1.3_VAMOS_RULE_1.3_BASE.md` | 634 |
| 2 | PLAN-3.0 | `D:\VAMOS\docs\sot\PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md` | 7,046 |

**추출 초점**:
- BASE-1.3: 규칙 목록, 정본 우선순위, LOCK 값, 비용 관련 수치
- PLAN-3.0: 버전별 로드맵 (V0~V3), 모듈 수/목록, 비용 파라미터, 타임라인, Stage Gate
- 양 파일의 모든 수치(C1), 카운트(C2), 분류(C3), 명칭(C4), 범위(C5), 버전(C6), 임계값(C7), 참조(C8)

**⚠️ PLAN-3.0은 7,046줄**: Read tool로 최소 4회 분할 읽기 필요 (offset: 0→2000→4000→6000)

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA02_base_plan.json`

---

#### EA-3: MASTER_SPECIFICATION

**대상 파일 (1개, 1,893줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | MASTER_SPEC | `D:\VAMOS\docs\sot\VAMOS_MASTER_SPECIFICATION.md` | 1,893 |

**추출 초점**:
- 통합 참조값 전수: 모듈 수/목록, 분류 체계, API 수, 프롬프트 수
- 모든 수치(C1), 카운트(C2), 분류(C3), 명칭(C4), 범위(C5), 버전(C6), 임계값(C7), 참조(C8)

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA03_master_spec.json`

---

#### EA-4: D2.0-01 (OVERVIEW) + D2.0-02 (ORANGE_CORE)

**대상 파일 (2개, 6,331줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | D2.0-01 | `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` | 1,857 |
| 2 | D2.0-02 | `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | 4,474 |

**추출 초점**:
- D2.0-01: Overview LOCK 값, 전체 아키텍처 수치, 모듈 분류/목록
- D2.0-02: ORANGE CORE 상세 — 모듈명, 파라미터, 임계값, API 수, 스키마

**⚠️ D2.0-02는 4,474줄**: Read tool로 최소 3회 분할 읽기 필요

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA04_d20_01_02.json`

---

#### EA-5: D2.0-03 (BLUE_NODES) + D2.0-04 (INFRA_CORE)

**대상 파일 (2개, 3,534줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | D2.0-03 | `D:\VAMOS\docs\sot\D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md` | 1,943 |
| 2 | D2.0-04 | `D:\VAMOS\docs\sot\D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md` | 1,591 |

**추출 초점**:
- D2.0-03: BLUE NODES 모듈 목록/수, 기능별 파라미터, 활성화 버전
- D2.0-04: INFRA CORE 구성요소, 배포 파라미터, CI/CD 수치

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA05_d20_03_04.json`

---

### ═══ 대화 2: EA-6 ~ EA-10 (Design + PHASE_B + 전문 SPEC) ═══

#### EA-6: D2.0-05 (AGENT_WORKFLOW) + D2.0-06 (STORAGE_MEMORY)

**대상 파일 (2개, 4,410줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | D2.0-05 | `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` | 1,982 |
| 2 | D2.0-06 | `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` | 2,428 |

**추출 초점**:
- D2.0-05: 에이전트 팀 구성, 워크플로우 단계, 상태머신 수치
- D2.0-06: 저장소 계층, 메모리 파라미터, RAG 설정값

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA06_d20_05_06.json`

---

#### EA-7: D2.0-07 (SAFETY_COST) + D2.0-08 (UI_UX)

**대상 파일 (2개, 5,351줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | D2.0-07 | `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` | 2,655 |
| 2 | D2.0-08 | `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | 2,696 |

**추출 초점**:
- D2.0-07: 안전 계층(Guardrails), 비용 상한, 승인 흐름, LOCK 값
- D2.0-08: UI 컴포넌트 수, 화면 구성, 반응형 임계값

**⚠️ 양 파일 모두 2,600줄 이상**: Read tool 분할 읽기 필요

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA07_d20_07_08.json`

---

#### EA-8: D2.1 부속서 전체 (A1 + D1~D8 + Q1, 10개)

**대상 파일 (10개, 5,614줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | D2.1-A1 | `D:\VAMOS\docs\sot\D2.1-A1_A1_TECH_STACK.md` | 401 |
| 2 | D2.1-D1 | `D:\VAMOS\docs\sot\D2.1-D1_D1_SCHEMA_GLOSSARY.md` | 363 |
| 3 | D2.1-D2 | `D:\VAMOS\docs\sot\D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` | 547 |
| 4 | D2.1-D3 | `D:\VAMOS\docs\sot\D2.1-D3_D3_SCHEMA_BLUE_NODES.md` | 759 |
| 5 | D2.1-D4 | `D:\VAMOS\docs\sot\D2.1-D4_D4_SCHEMA_INFRA_CORE.md` | 518 |
| 6 | D2.1-D5 | `D:\VAMOS\docs\sot\D2.1-D5_D5_SCHEMA_AGENT_WORKFLOW.md` | 665 |
| 7 | D2.1-D6 | `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` | 394 |
| 8 | D2.1-D7 | `D:\VAMOS\docs\sot\D2.1-D7_D7_SCHEMA_SAFETY_COST_APPROVAL.md` | 594 |
| 9 | D2.1-D8 | `D:\VAMOS\docs\sot\D2.1-D8_D8_SCHEMA_UI_UX.md` | 201 |
| 10 | D2.1-Q1 | `D:\VAMOS\docs\sot\D2.1-Q1_Q1_AUDIT_REPORT.md` | 1,172 |

**추출 초점**:
- A1: 기술 스택 버전, 패키지 목록
- D1~D8: 스키마별 필드 수, 필수값, 타입, 제약조건
- Q1: 감사 항목 수, 결과 수치

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA08_d21_schemas.json`

---

#### EA-9: PHASE_B1~B3 (API 계약 + 프로젝트 구조 + 의존성)

**대상 파일 (3개, 3,471줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | PHASE_B1 | `D:\VAMOS\docs\sot\PHASE_B1_API_CONTRACT.md` | 2,218 |
| 2 | PHASE_B2 | `D:\VAMOS\docs\sot\PHASE_B2_PROJECT_STRUCTURE.md` | 886 |
| 3 | PHASE_B3 | `D:\VAMOS\docs\sot\PHASE_B3_DEPENDENCIES.md` | 367 |

**추출 초점**:
- B1: API 엔드포인트 수/목록, 요청/응답 스키마, HTTP 메서드
- B2: 디렉토리 구조, 파일 수, 경로 규칙
- B3: 의존성 패키지 목록, 버전 제약

**⚠️ B1은 2,218줄**: Read tool 분할 읽기 필요

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA09_phase_b1_b3.json`

---

#### EA-10: PHASE_B4~B7 (Config + 테스트 + CI/CD + 마이그레이션)

**대상 파일 (4개, 6,280줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | PHASE_B4 | `D:\VAMOS\docs\sot\PHASE_B4_CONFIG_SPEC.md` | 1,242 |
| 2 | PHASE_B5 | `D:\VAMOS\docs\sot\PHASE_B5_TEST_STRATEGY.md` | 945 |
| 3 | PHASE_B6 | `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` | 1,757 |
| 4 | PHASE_B7 | `D:\VAMOS\docs\sot\PHASE_B7_MIGRATION_STRATEGY.md` | 2,336 |

**추출 초점**:
- B4: Config 키 목록, 기본값, 타입, LOCK 여부
- B5: 테스트 유형/수, 커버리지 목표, 실행 환경
- B6: 파이프라인 단계, 타임아웃, 트리거 조건
- B7: 마이그레이션 단계, 순서, 롤백 조건

**⚠️ B7은 2,336줄**: Read tool 분할 읽기 필요

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA10_phase_b4_b7.json`

---

### ═══ 대화 3: EA-11 ~ EA-15 (전문 SPEC + STEP7 + 기타) ═══

#### EA-11: 전문 SPEC 4개 (AGENT_TEAMS + AI_INVESTING + CLOUD_LIBRARY + SDAR)

**대상 파일 (4개, 6,669줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | AGENT_TEAMS | `D:\VAMOS\docs\sot\VAMOS_AGENT_TEAMS_SPEC.md` | 2,204 |
| 2 | AI_INVESTING | `D:\VAMOS\docs\sot\VAMOS_AI_INVESTING_SPEC.md` | 1,379 |
| 3 | CLOUD_LIBRARY | `D:\VAMOS\docs\sot\VAMOS_CLOUD_LIBRARY_SPEC.md` | 1,439 |
| 4 | SDAR | `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | 1,647 |

**추출 초점**:
- AGENT_TEAMS: 에이전트 수/목록, 팀 구성, 역할 정의
- AI_INVESTING: 투자 전략 파라미터, 모델 수치
- CLOUD_LIBRARY: 라이브러리 구성요소, 인터페이스 수
- SDAR: NEVER_AUTO 목록, 보안 규칙, 승인 흐름

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA11_spec_4.json`

---

#### EA-12: STEP7 상세명세서 5개

**대상 파일 (5개, 9,032줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | STEP7_A-E | `D:\VAMOS\docs\sot\VAMOS_STEP7_A-E_상세명세서.md` | 1,000 |
| 2 | STEP7_F-I | `D:\VAMOS\docs\sot\VAMOS_STEP7_F-I_상세명세서.md` | 2,876 |
| 3 | STEP7_J-M | `D:\VAMOS\docs\sot\VAMOS_STEP7_J-M_상세명세서.md` | 1,824 |
| 4 | STEP7_N-P | `D:\VAMOS\docs\sot\VAMOS_STEP7_N-P_보강_상세명세서.md` | 1,809 |
| 5 | STEP7_보강통합 | `D:\VAMOS\docs\sot\VAMOS_STEP7_보강_통합명세서.md` | 1,523 |

**추출 초점**:
- 각 STEP의 산출물 목록/수, 구현 항목 수, 모듈별 할당, 우선순위 수치

**⚠️ STEP7_F-I는 2,876줄**: Read tool 분할 읽기 필요

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA12_step7_spec.json`

---

#### EA-13: STEP7 작업가이드 16개 (총론 + B~P)

**대상 파일 (16개, 14,891줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | 총론 | `D:\VAMOS\docs\sot\STEP7_작업가이드.md` | 940 |
| 2 | A 보강 | `D:\VAMOS\docs\sot\STEP7_A-I_보강_추가항목_통합.md` | 666 |
| 3 | B | `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` | 1,188 |
| 4 | C | `D:\VAMOS\docs\sot\STEP7-C_UI_UX_전수비교_작업가이드.md` | 235 |
| 5 | D | `D:\VAMOS\docs\sot\STEP7-D_메모리_저장소_아키텍처_작업가이드.md` | 294 |
| 6 | E | `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` | 1,210 |
| 7 | F | `D:\VAMOS\docs\sot\STEP7-F_인프라_배포_MLOps_작업가이드.md` | 1,450 |
| 8 | G | `D:\VAMOS\docs\sot\STEP7-G_벤치마크_평가_품질보증_작업가이드.md` | 891 |
| 9 | H | `D:\VAMOS\docs\sot\STEP7-H_비즈니스모델_시장전략_작업가이드.md` | 1,053 |
| 10 | I | `D:\VAMOS\docs\sot\STEP7-I_AI_Investing_보강_작업가이드.md` | 1,349 |
| 11 | J | `D:\VAMOS\docs\sot\STEP7-J_멀티모달_생성처리_작업가이드.md` | 1,698 |
| 12 | K | `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` | 1,416 |
| 13 | L | `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` | 1,026 |
| 14 | M | `D:\VAMOS\docs\sot\STEP7-M_PKM_지식관리_작업가이드.md` | 883 |
| 15 | N | `D:\VAMOS\docs\sot\STEP7-N_워크플로우자동화_RPA_작업가이드.md` | 667 |
| 16 | O | `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` | 543 |

**추출 초점**:
- 각 작업가이드의 구현 항목 수, 모듈 매핑, 우선순위, 참조 관계

**⚠️ 16개 파일, 총 14,891줄**: 파일별 순차 읽기. 각 파일에서 C1~C8 추출

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA13_step7_guides.json`

---

#### EA-14: STEP7 나머지 (P 작업가이드 + R1~R6 + 마스터인덱스 + 최종검증)

**대상 파일 (9개, 3,747줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | P | `D:\VAMOS\docs\sot\STEP7-P_건강_웰니스_감성AI_작업가이드.md` | 668 |
| 2 | R1 | `D:\VAMOS\docs\sot\STEP7_R1_V1_CRITICAL.md` | 892 |
| 3 | R2 | `D:\VAMOS\docs\sot\STEP7_R2_V1_HIGH.md` | 662 |
| 4 | R3 | `D:\VAMOS\docs\sot\STEP7_R3_V1_MEDIUM_LOW.md` | 178 |
| 5 | R4 | `D:\VAMOS\docs\sot\STEP7_R4_V2_CRITICAL_HIGH.md` | 170 |
| 6 | R5 | `D:\VAMOS\docs\sot\STEP7_R5_V2_MEDIUM_LOW.md` | 140 |
| 7 | R6 | `D:\VAMOS\docs\sot\STEP7_R6_V3_ALL.md` | 154 |
| 8 | 마스터인덱스 | `D:\VAMOS\docs\sot\STEP7_STEP6통합_마스터인덱스.md` | 828 |
| 9 | 최종검증 | `D:\VAMOS\docs\sot\STEP7_PHASE7_최종검증보고서.md` | 242 |

**추출 초점**:
- R1~R6: 우선순위별 항목 수, 모듈 매핑, 버전 범위
- 마스터인덱스: 전체 항목 수, 분류별 카운트
- 최종검증: 검증 결과 수치

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA14_step7_rest.json`

---

#### EA-15: 기타 참조 (BEGINNER + PLAN-2.0 + READINESS 3개)

**대상 파일 (5개, 8,958줄)**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|-------|
| 1 | BEGINNER | `D:\VAMOS\docs\sot\VAMOS_BEGINNER_GUIDE.md` | 1,844 |
| 2 | PLAN-2.0 | `D:\VAMOS\docs\sot\PLAN-2.0_VAMOS_PLAN_2.0_.md` | 4,350 |
| 3 | READINESS_GUIDE | `D:\VAMOS\docs\sot\VAMOS_IMPLEMENTATION_READINESS_GUIDE.md` | 1,256 |
| 4 | READINESS_REVIEW | `D:\VAMOS\docs\sot\VAMOS_IMPLEMENTATION_READINESS_REVIEW.md` | 765 |
| 5 | V0_READINESS | `D:\VAMOS\docs\sot\VAMOS_V0_READINESS_FINAL_REVIEW.md` | 743 |

**추출 초점**:
- BEGINNER: 세션 수, 단계별 항목 수, 참조 관계
- PLAN-2.0: 이전 버전 수치 (PLAN-3.0과 비교용), 모듈 분류, 비용 파라미터
- READINESS 3개: 준비도 체크리스트 항목 수, 판정 기준

**⚠️ PLAN-2.0은 4,350줄**: Read tool 분할 읽기 필요

**산출물**: `D:\VAMOS\04. 구현단계\v13_results\phase0\extraction\v13_EA15_etc.json`

---

## 산출물 JSON 구조 (각 EA 공통)

```json
{
  "metadata": {
    "agent": "EA-{N}",
    "version": "v13",
    "created": "2026-03-XX",
    "source_files": ["파일명1", "파일명2"],
    "source_file_hashes": {
      "파일명1": "SHA-256 해시값 (64자 hex)",
      "파일명2": "SHA-256 해시값 (64자 hex)"
    },
    "total_lines_read": 0,
    "total_items_extracted": 0,
    "categories": {
      "C1": 0, "C2": 0, "C3": 0, "C4": 0,
      "C5": 0, "C6": 0, "C7": 0, "C8": 0
    }
  },
  "items": [
    {
      "item_id": "EA-01_001",
      "category": "C2",
      "source_file": "CLAUDE.md",
      "source_line": 45,
      "source_text": "7개 불변 구역: safety_rules, cost_ceiling, ...",
      "key": "IMMUTABLE_ZONE_COUNT",
      "value": 7,
      "value_type": "number",
      "context": "§7.3에서 정의된 불변 구역 수"
    }
  ]
}
```

> **[v13.2.0 신규] source_file_hashes**: 각 SOT 파일의 SHA-256 해시값을 기록합니다.
> Phase 0-F에서 SOT를 수정하면 해시가 변경되어 DV-9에서 EA 무효화를 탐지합니다.
> 해시 계산법: `python -c "import hashlib; print(hashlib.sha256(open('파일','r',encoding='utf-8').read().encode('utf-8')).hexdigest())"`
```

---

## 산출물 전수 목록

| # | 에이전트 | 파일 수 | 줄 수 | 산출물 경로 | 대화 |
|---|----------|---------|-------|------------|------|
| 1 | EA-1 | 1 | 697 | `v13_results/phase0/extraction/v13_EA01_claude_md.json` | 1 |
| 2 | EA-2 | 2 | 7,680 | `v13_results/phase0/extraction/v13_EA02_base_plan.json` | 1 |
| 3 | EA-3 | 1 | 1,893 | `v13_results/phase0/extraction/v13_EA03_master_spec.json` | 1 |
| 4 | EA-4 | 2 | 6,331 | `v13_results/phase0/extraction/v13_EA04_d20_01_02.json` | 1 |
| 5 | EA-5 | 2 | 3,534 | `v13_results/phase0/extraction/v13_EA05_d20_03_04.json` | 1 |
| 6 | EA-6 | 2 | 4,410 | `v13_results/phase0/extraction/v13_EA06_d20_05_06.json` | 2 |
| 7 | EA-7 | 2 | 5,351 | `v13_results/phase0/extraction/v13_EA07_d20_07_08.json` | 2 |
| 8 | EA-8 | 10 | 5,614 | `v13_results/phase0/extraction/v13_EA08_d21_schemas.json` | 2 |
| 9 | EA-9 | 3 | 3,471 | `v13_results/phase0/extraction/v13_EA09_phase_b1_b3.json` | 2 |
| 10 | EA-10 | 4 | 6,280 | `v13_results/phase0/extraction/v13_EA10_phase_b4_b7.json` | 2 |
| 11 | EA-11 | 4 | 6,669 | `v13_results/phase0/extraction/v13_EA11_spec_4.json` | 3 |
| 12 | EA-12 | 5 | 9,032 | `v13_results/phase0/extraction/v13_EA12_step7_spec.json` | 3 |
| 13 | EA-13 | 16 | 14,891 | `v13_results/phase0/extraction/v13_EA13_step7_guides.json` | 3 |
| 14 | EA-14 | 9 | 3,747 | `v13_results/phase0/extraction/v13_EA14_step7_rest.json` | 3 |
| 15 | EA-15 | 5 | 8,958 | `v13_results/phase0/extraction/v13_EA15_etc.json` | 3 |
| **합계** | **15** | **68** | **89,558** | | **3대화** |

> ⚠️ 줄 수 합계 89,558 vs 실제 89,363: 반올림 차이. 실행 시 실제 파일 줄 수 사용.

---

## 완료 시 수행 (대화 3 마지막)

```
1. EA-1 ~ EA-15 산출물 15개 파일 전수 존재 확인
2. 각 파일의 /quality-gate 판정 확인:
   - 15개 전수 GOLD 또는 SILVER 필수
   - REJECT 잔여 시 해당 EA 수정 후 재추출
3. 각 파일의 metadata.total_items_extracted 합산 → 총 추출 항목 수 기록
4. 카테고리별 합산 통계:
   - C1(수치): N건, C2(카운트): N건, C3(분류): N건, C4(명칭): N건
   - C5(범위): N건, C6(버전): N건, C7(임계값): N건, C8(참조): N건
5. 기존 3건 불일치 관련 항목 존재 확인:
   - 불일치 A: IMMUTABLE_ZONE_COUNT + NEVER_AUTO_COUNT → EA-1에서 추출 확인
   - 불일치 B: COND_PRIORITY_MEDIUM + COND_PRIORITY_LOW → 관련 EA에서 추출 확인
   - 불일치 C: MODULE_TIER_SYSTEM → EA-1, EA-3 등에서 추출 확인
6. DV 검증 결과 통계: 15개 EA × DV-1~DV-7 = 105건 검증 결과 요약
7. 미완료 항목이 있으면 JSON으로 저장: v13_results/phase0/extraction/v13_EA_incomplete.json
```

---

## 컨텍스트 윈도우 안전장치 (약점 E 대응 — v13.2.0 신규)

> 대용량 파일 처리 시 컨텍스트 윈도우 한계로 인한 누락/품질 저하를 방지합니다.

### 강제 분할 읽기 규칙

| 파일 줄 수 | 분할 횟수 | offset 패턴 |
|-----------|----------|------------|
| ≤ 2,000 | 1회 (전체) | 전체 읽기 |
| 2,001~4,000 | 2회 | 0→2000 |
| 4,001~6,000 | 3회 | 0→2000→4000 |
| 6,001~8,000 | 4회 | 0→2000→4000→6000 |
| > 8,000 | 5회+ | 2000줄 단위 |

### 후반부 누락 방지 체크리스트

```
□ 파일 마지막 100줄을 별도로 1회 더 읽었는가?
□ 파일 후반부(70% 이후)에서 추출한 항목이 전체의 30% 이상인가?
  → 미만이면 후반부 재읽기 필요 (컨텍스트 한계로 누락 의심)
□ 분할 읽기 경계(2000, 4000줄 부근)에서 잘린 항목이 없는가?
  → 경계 ±50줄 구간을 중복 읽기하여 확인
```

### EA 에이전트 입력 과부하 방지

- 각 EA 에이전트는 담당 파일 **만** 읽습니다 (다른 EA의 파일 읽기 금지)
- 단일 에이전트가 처리하는 총 줄 수가 15,000줄을 초과하면 경고
  → EA-13(16개 파일, 14,891줄)은 정상이지만 주의 필요
- 추출 도중 컨텍스트가 부족해지면 **즉시 중간 저장** 후 다음 에이전트로 분할

### source_file_hashes 생성 규칙

각 SOT 파일을 Read tool로 읽은 직후 해시를 계산하여 metadata에 포함합니다:

```bash
python -c "import hashlib; f=open('D:/VAMOS/docs/sot/파일명','r',encoding='utf-8'); print(hashlib.sha256(f.read().encode('utf-8')).hexdigest())"
```

---

## AI 오류 방지 규칙 요약 (이 Phase에서 준수)

1. **환각 금지**: 파일에 없는 값 생성 금지. 반드시 source_text로 원문 인용
2. **부분 읽기 금지**: 모든 SOT 파일 전체 읽기. 2000줄 초과 시 분할 읽기
3. **라인 번호 직접 확인**: source_line은 Read tool에서 확인한 행 번호만
4. **추론 금지**: 명시되지 않은 값은 `null` + `"note": "명시되지 않음"`
5. **표준 키 사용**: 동일 개념은 반드시 표준 키 목록의 key 사용 (DV-8이 검증)
6. **value 원본 유지**: 숫자는 숫자, 문자열은 문자열, 목록은 배열로 원본 형태 유지
7. **대화 간 상태**: 이전 대화 산출물은 JSON 파일로 전달. 컨텍스트 의존 금지
8. **[신규] source_file_hashes 필수**: 각 SOT 파일의 SHA-256 해시를 metadata에 포함 (DV-9가 검증)
9. **[신규] 후반부 검증**: 파일 후반부(70% 이후) 추출 비율이 30% 미만이면 재읽기 (DV-10이 검증)
10. **[신규] 분할 경계 중복 읽기**: 2000줄 분할 경계 ±50줄 구간은 반드시 중복 읽기

---

## 🔍 사용자 확인 체크리스트 (Phase 0-A 완료 시 Claude가 생성)

> **이 섹션은 Claude가 Phase 0-A 완료 시 자동으로 채워서 사용자에게 제출합니다.**
> 사용자는 아래 형식의 체크리스트를 받고, 지시된 파일의 지시된 행을 직접 열어 확인합니다.

### Claude 작성 규칙

Phase 0-A 각 대화 완료 시 (대화 1, 2, 3 종료 시) 아래 형식으로 **사용자 확인 체크리스트**를 출력하세요:

```
═══════════════════════════════════════════════════
🔍 사용자 확인 체크리스트 (Phase 0-A 대화 {N} 완료)
═══════════════════════════════════════════════════

■ 확인 항목 1: 환각 여부 스팟 체크 (3건)
  [확인1-1] 파일: D:\VAMOS\docs\sot\{파일명}
            행: {source_line}
            찾을 텍스트: "{source_text 앞 30자}"
            → 해당 행에 위 텍스트가 있으면 ✅, 없으면 ❌

  [확인1-2] 파일: D:\VAMOS\docs\sot\{파일명}
            행: {source_line}
            찾을 텍스트: "{source_text 앞 30자}"
            → 해당 행에 위 텍스트가 있으면 ✅, 없으면 ❌

  [확인1-3] 파일: D:\VAMOS\docs\sot\{파일명}
            행: {source_line}
            찾을 텍스트: "{source_text 앞 30자}"
            → 해당 행에 위 텍스트가 있으면 ✅, 없으면 ❌

■ 확인 항목 2: 기존 불일치 3건 관련 항목 존재 확인
  [확인2-1] EA JSON에서 key="IMMUTABLE_ZONE_COUNT" 검색
            → value가 숫자이면 ✅ (값: ___)
  [확인2-2] EA JSON에서 key="COND_PRIORITY_MEDIUM" 검색
            → value가 숫자이면 ✅ (값: ___)
  [확인2-3] EA JSON에서 key="MODULE_TIER_SYSTEM" 검색
            → value가 있으면 ✅ (값: ___)

■ 확인 항목 3: 후반부 커버리지 (대용량 파일만)
  [확인3-1] {대용량 파일명} ({줄수}줄)
            → DV-10 결과: PASS / WARNING / CRITICAL
            → 후반부 추출 비율: ___%
            → 20% 미만이면 ❌ → "뒷부분 다시 읽어줘" 요청

■ 확인 항목 4: quality-gate 판정
  [확인4-1] EA-{N}: {판정} (GOLD/SILVER/BRONZE/REJECT)
  [확인4-2] EA-{N}: {판정}
  ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ 가 하나라도 있으면 Claude에게 해당 항목 수정을 요청하세요.
모두 ✅ 이면 다음 대화(또는 Phase 0-B)로 진행합니다.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 확인 항목 선택 기준

- **확인1 (환각 스팟체크)**: 각 EA에서 무작위 1건씩, 총 3건 선택. **파일 후반부 항목 1건 이상 포함 필수**.
- **확인2 (기존 불일치)**: 해당 대화에서 추출한 EA 중 관련 항목이 있는 경우만.
- **확인3 (후반부 커버리지)**: 2,000줄 초과 파일만. DV-10 결과를 그대로 인용.
- **확인4 (quality-gate)**: 해당 대화에서 완료한 EA 전수.
