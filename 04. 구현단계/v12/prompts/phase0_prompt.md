# Phase 0: SOT 68개 전수 Feature 추출 + 인덱스 구축

> **대화**: 대화 2~5 (4개 대화에 분산)
> **목표**: SOT 68개 파일(89,363줄)에서 Feature 전수 추출 → v12 Feature Registry 구축 + PART2 v25.2.0 인덱스 재구축
> **성격**: v12 파이프라인 핵심 기반. Phase 1 매핑의 입력 데이터 생성.
> **선행 조건**: Phase -1 PASS

---

## Pre-check Protocol

**매 대화(대화 2/3/4/5) 시작 시 반드시 수행:**

```
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v12\v12_plan.md
② 본 프롬프트 읽기: D:\VAMOS\04. 구현단계\v12\prompts\phase0_prompt.md
③ 진행 상태 확인: D:\VAMOS\04. 구현단계\v12\v12_results\v12_phase_status.json
④ Phase -1 PASS 확인 (FAIL이면 Phase 0 진행 불가)
   - Phase -1 산출물 전수 로드:
     D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_agent_pattern_audit.md
     D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_phase-1_verdict.md
     D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_pattern_check.md
     D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_v25_conflict.md
     D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_sot_currency.md
     D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_registry_validity.md
⑤ 이전 대화 산출물 확인:
   - 대화 2: Phase -1 verdict 읽기
   - 대화 3: 대화 2 산출물 (C-1a~C-3) 존재 확인
   - 대화 4: 대화 2~3 산출물 (C-1a~C-10) 존재 확인
   - 대화 5: 대화 2~4 산출물 (C-1a~C-13) 전수 존재 확인
⑥ 확인 완료 후 작업 시작
```

---

## 스킬 에이전트 실행 규칙

> **필수**: 본 Phase의 작업 단위는 반드시 **Agent tool(스킬 에이전트)**을 사용하여 병렬 실행합니다.

1. **병렬 실행**: 독립적인 작업 단위(C-에이전트)는 Agent tool로 동시 투입
2. **동일 템플릿**: 모든 에이전트는 본 프롬프트에 정의된 출력 템플릿을 준수
3. **결과 통합**: 개별 에이전트 결과를 취합하여 교차검증 수행
4. **재현성**: 동일 입력 → 동일 출력 보장을 위해 에이전트별 명확한 범위 지정

**Agent tool 호출 예시**:
```
각 C-에이전트를 Agent tool의 prompt 파라미터로 투입:
- description: "C-1a: PLAN-3.0 Feature 추출"
- prompt: "D:\VAMOS\docs\sot\PLAN-3.0_... 파일을 읽고 아래 템플릿에 따라 Feature를 추출하세요. [템플릿 내용]"
- 독립적인 C-에이전트는 동시에 여러 개 투입 가능
```

---

## 입력 파일

### PART2 대상
| 파일 | 경로 |
|------|------|
| PART2 구현단계 v25.2.0 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` |

### SOT 68개 파일
```
경로: D:\VAMOS\docs\sot\
전수 목록: v12_plan.md §2.1 참조 (그룹 A~I, 68개 파일, 89,363줄)
```

### v10 기존 산출물 (교차확인용, 대화 5에서 사용)
| 파일 | 경로 |
|------|------|
| v10 Feature Registry | `D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json` |

### Phase -1 산출물 (참조용)
| 파일 | 경로 |
|------|------|
| 에이전트 감사 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_agent_pattern_audit.md` |
| Phase -1 판정 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_phase-1_verdict.md` |
| SOT 최신성 검증 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_sot_currency.md` |
| Registry 유효성 검증 | `D:\VAMOS\04. 구현단계\v12\v12_results\phase-1\v12_registry_validity.md` |

---

## 스킬 에이전트 패턴

### 사용할 패턴

| 패턴 | 출처 | 적용 |
|------|------|------|
| Feature 추출 템플릿 | v10 Phase 0-A | C-에이전트 전체 |
| 12개 SRC 추출 에이전트 구조 | v10 Phase 0-C | C-1a~C-10 (기존 구조 계승) |
| 정본 우선순위 | v6 §4-A | Feature 충돌 시 우선순위 판정 |
| 7개 Phase 0 인덱스 | v11 0-A~0-G | 인덱스 구축 (0-I-A~0-I-E) |

### 오류 주의사항

| 오류 | 대응 |
|------|------|
| v10은 SRC 43개만 분석 | C-11~C-13은 **완전 신규** 추출. v10에 해당 Feature 없음 |
| v10 Feature Registry는 v21~v23 기준 | v12는 v25.2.0 기준 독립 구축. v10 결과는 대화 5에서 교차확인만 |
| v11 인덱스는 v24.0.0 기준 | v12는 v25.2.0 기준 재구축. v11 인덱스 참조 금지 |
| 라인 번호 시프트 | v10/v11의 라인 참조 사용 금지. v25.2.0에서 직접 검색 |

---

## 대화별 작업 상세

### ═══ 대화 2: C-1a ~ C-3 (기존 SOT 전반) ═══

#### C-1a: PLAN-3.0

**대상 파일**: `D:\VAMOS\docs\sot\PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md` (7,046줄)

**작업**:
1. 파일 전체 읽기 (부분 읽기 금지 — 여러 번 나눠서라도 전체 읽을 것)
2. 구현 가능한 Feature 추출 (함수/모듈/API/로직/데이터구조/UI 등)
3. Feature별 version_scope 판정 (V0/V1/V2/V3/multi)
4. Feature별 extractable 판정 (true: 구현 대상, false: 개념/원칙)

**추출 템플릿** (v10 Phase 0-A 계승):
```json
{
  "feature_id": "v12_C01a_NNN",
  "source_file": "PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md",
  "source_group": "A",
  "source_line": 123,
  "source_text": "원본 텍스트 (50자 이내 요약)",
  "feature_name": "Feature 이름",
  "feature_description": "상세 설명",
  "version_scope": "V1",
  "extractable": true,
  "category": "orange_core|blue_nodes|storage|safety|agent|infra|mcp|schemas|ui|benchmark|business",
  "priority": "CRITICAL|HIGH|MEDIUM|LOW"
}
```

> **⚠️ 필드 값 제약 (MANDATORY)** — 아래 정의된 값만 사용. 다른 값 사용 시 해당 JSON은 무효 처리됩니다.

**① priority (4개만 허용)**:

| 허용 값 | 의미 |
|---------|------|
| CRITICAL | 필수 핵심 기능 |
| HIGH | 중요 기능 |
| MEDIUM | 보통 기능 |
| LOW | 낮은 우선순위 |

> ❌ **금지**: `P0`, `P1`, `P2`, `P3`, `높음`, `낮음` 등 비표준 값 사용 절대 금지

**② category (11개만 허용)**:

| 허용 값 | 의미 |
|---------|------|
| orange_core | 오렌지 코어 모듈 |
| blue_nodes | 블루 노드 모듈 |
| storage | 저장소/메모리 |
| safety | 보안/안전/거버넌스 |
| agent | 에이전트 워크플로우 |
| infra | 인프라/배포/MLOps |
| mcp | MCP 프로토콜 |
| schemas | 스키마/데이터 구조 |
| ui | UI/UX |
| benchmark | 벤치마크/평가/품질 |
| business | 비즈니스모델/시장전략 |

> ❌ **금지**: `architecture`, `config`, `registry`, `module`, `logic`, `agent_framework` 등 비표준 값 사용 절대 금지

**③ source_group (파일별 그룹 문자 A~I — v12_plan.md §2.1 기준)**:

| 그룹 | 파일 범위 |
|------|---------|
| A | BASE-1.3, PLAN-3.0, MASTER_SPEC |
| B | D2.0-01 ~ D2.0-08 (Design 2.0 본문 8개) |
| C | D2.1-A1, D2.1-D1~D8, D2.1-Q1 (Design 2.1 부속서 10개) |
| D | PHASE_B1 ~ PHASE_B7 (구현준비 7개) |
| E | AGENT_TEAMS, AI_INVESTING, CLOUD_LIBRARY, SDAR (전문 SPEC 4개) |
| F | STEP7 상세명세서 5개 (A-E, F-I, J-M, N-P, 보강통합) |
| G | STEP7 작업가이드 16개 (총론 + B~P 작업가이드) |
| H | STEP7 R1~R6, 마스터인덱스, 최종검증보고서, A-I보강 (9개) |
| I | CLAUDE.md, PLAN-2.0, BEGINNER, READINESS 3개 (기타참조 6개) |

> ❌ **금지**: 항목 ID(`K-021` 등), 에이전트명(`C-1b` 등) 사용 금지. 반드시 **파일이 속한 그룹의 문자(A~I)**만 기재.
> ⚠️ **주의**: 동일 에이전트가 여러 그룹 파일을 처리할 수 있음. source_group은 **에이전트 단위가 아니라 파일 단위**로 결정.

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C01a.json`

---

#### C-1b: BASE-1.3 + MASTER_SPEC + READINESS 3개

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | BASE-1.3 | `D:\VAMOS\docs\sot\BASE-1.3_VAMOS_RULE_1.3_BASE.md` | 634 |
| 2 | MASTER_SPEC | `D:\VAMOS\docs\sot\VAMOS_MASTER_SPECIFICATION.md` | 1,893 |
| 3 | READINESS_GUIDE | `D:\VAMOS\docs\sot\VAMOS_IMPLEMENTATION_READINESS_GUIDE.md` | 1,256 |
| 4 | READINESS_REVIEW | `D:\VAMOS\docs\sot\VAMOS_IMPLEMENTATION_READINESS_REVIEW.md` | 765 |
| 5 | V0_READINESS | `D:\VAMOS\docs\sot\VAMOS_V0_READINESS_FINAL_REVIEW.md` | 743 |

**작업**: 5개 파일 전체 읽기 → Feature 추출 (C-1a와 동일 템플릿)
**source_group 지정**: BASE-1.3=`A`, MASTER_SPEC=`A`, READINESS_GUIDE=`I`, READINESS_REVIEW=`I`, V0_READINESS=`I`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C01b.json`

---

#### C-2: D2.0-01 (OVERVIEW) + D2.0-02 (ORANGE_CORE)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | D2.0-01 OVERVIEW | `D:\VAMOS\docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` | 1,857 |
| 2 | D2.0-02 ORANGE_CORE | `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | 4,474 |

**작업**: 2개 파일 전체 읽기 → Feature 추출
**source_group 지정**: 전체 `B`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C02.json`

---

#### C-3: D2.0-03 (BLUE_NODES) + D2.0-04 (INFRA_CORE) + D2.0-05 (AGENT_WORKFLOW)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | D2.0-03 BLUE_NODES | `D:\VAMOS\docs\sot\D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md` | 1,943 |
| 2 | D2.0-04 INFRA_CORE | `D:\VAMOS\docs\sot\D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md` | 1,591 |
| 3 | D2.0-05 AGENT_WORKFLOW | `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` | 1,982 |

**작업**: 3개 파일 전체 읽기 → Feature 추출
**source_group 지정**: 전체 `B`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C03.json`

---

### ═══ 대화 3: C-4 ~ C-10 (기존 SOT 후반) ═══

#### C-4: D2.0-06 (STORAGE_MEMORY) + D2.0-07 (SAFETY_COST_APPROVAL)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | D2.0-06 STORAGE_MEMORY | `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` | 2,428 |
| 2 | D2.0-07 SAFETY_COST_APPROVAL | `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` | 2,655 |

**source_group 지정**: 전체 `B`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C04.json`

---

#### C-5: D2.0-08 (UI_UX) + D2.1-D8 (SCHEMA_UI_UX)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | D2.0-08 UI_UX | `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | 2,696 |
| 2 | D2.1-D8 SCHEMA_UI_UX | `D:\VAMOS\docs\sot\D2.1-D8_D8_SCHEMA_UI_UX.md` | 201 |

**source_group 지정**: D2.0-08=`B`, D2.1-D8=`C`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C05.json`

---

#### C-6: D2.1 스키마 전체 (A1 + D1~D7 + Q1)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | D2.1-A1 TECH_STACK | `D:\VAMOS\docs\sot\D2.1-A1_A1_TECH_STACK.md` | 401 |
| 2 | D2.1-D1 SCHEMA_GLOSSARY | `D:\VAMOS\docs\sot\D2.1-D1_D1_SCHEMA_GLOSSARY.md` | 363 |
| 3 | D2.1-D2 SCHEMA_ORANGE_CORE | `D:\VAMOS\docs\sot\D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` | 547 |
| 4 | D2.1-D3 SCHEMA_BLUE_NODES | `D:\VAMOS\docs\sot\D2.1-D3_D3_SCHEMA_BLUE_NODES.md` | 759 |
| 5 | D2.1-D4 SCHEMA_INFRA_CORE | `D:\VAMOS\docs\sot\D2.1-D4_D4_SCHEMA_INFRA_CORE.md` | 518 |
| 6 | D2.1-D5 SCHEMA_AGENT_WORKFLOW | `D:\VAMOS\docs\sot\D2.1-D5_D5_SCHEMA_AGENT_WORKFLOW.md` | 665 |
| 7 | D2.1-D6 SCHEMA_STORAGE_MEMORY | `D:\VAMOS\docs\sot\D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` | 394 |
| 8 | D2.1-D7 SCHEMA_SAFETY_COST_APPROVAL | `D:\VAMOS\docs\sot\D2.1-D7_D7_SCHEMA_SAFETY_COST_APPROVAL.md` | 594 |
| 9 | D2.1-Q1 AUDIT_REPORT | `D:\VAMOS\docs\sot\D2.1-Q1_Q1_AUDIT_REPORT.md` | 1,172 |

**주의**: D2.1-D8은 C-5에서 처리됨 (UI_UX와 동시 분석)
**source_group 지정**: 전체 `C`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C06.json`

---

#### C-7: PHASE_B 구현 가이드 (B1~B7)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | PHASE_B1 API_CONTRACT | `D:\VAMOS\docs\sot\PHASE_B1_API_CONTRACT.md` | 2,218 |
| 2 | PHASE_B2 PROJECT_STRUCTURE | `D:\VAMOS\docs\sot\PHASE_B2_PROJECT_STRUCTURE.md` | 886 |
| 3 | PHASE_B3 DEPENDENCIES | `D:\VAMOS\docs\sot\PHASE_B3_DEPENDENCIES.md` | 367 |
| 4 | PHASE_B4 CONFIG_SPEC | `D:\VAMOS\docs\sot\PHASE_B4_CONFIG_SPEC.md` | 1,242 |
| 5 | PHASE_B5 TEST_STRATEGY | `D:\VAMOS\docs\sot\PHASE_B5_TEST_STRATEGY.md` | 945 |
| 6 | PHASE_B6 CICD_PIPELINE | `D:\VAMOS\docs\sot\PHASE_B6_CICD_PIPELINE.md` | 1,757 |
| 7 | PHASE_B7 MIGRATION_STRATEGY | `D:\VAMOS\docs\sot\PHASE_B7_MIGRATION_STRATEGY.md` | 2,336 |

**source_group 지정**: 전체 `D`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C07.json`

---

#### C-8: 전문 SPEC (AGENT_TEAMS + AI_INVESTING + CLOUD_LIBRARY + SDAR)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | AGENT_TEAMS_SPEC | `D:\VAMOS\docs\sot\VAMOS_AGENT_TEAMS_SPEC.md` | 2,204 |
| 2 | AI_INVESTING_SPEC | `D:\VAMOS\docs\sot\VAMOS_AI_INVESTING_SPEC.md` | 1,379 |
| 3 | CLOUD_LIBRARY_SPEC | `D:\VAMOS\docs\sot\VAMOS_CLOUD_LIBRARY_SPEC.md` | 1,439 |
| 4 | SDAR_DESIGN_SPEC | `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md` | 1,647 |

**source_group 지정**: 전체 `E`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C08.json`

---

#### C-9a: STEP7 상세명세서 전반 (A-E + F-I)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | STEP7_A-E 상세명세서 | `D:\VAMOS\docs\sot\VAMOS_STEP7_A-E_상세명세서.md` | 1,000 |
| 2 | STEP7_F-I 상세명세서 | `D:\VAMOS\docs\sot\VAMOS_STEP7_F-I_상세명세서.md` | 2,876 |

**source_group 지정**: 전체 `F`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C09a.json`

---

#### C-9b: STEP7 상세명세서 후반 (J-M + N-P + 보강통합)

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | STEP7_J-M 상세명세서 | `D:\VAMOS\docs\sot\VAMOS_STEP7_J-M_상세명세서.md` | 1,824 |
| 2 | STEP7_N-P 보강 상세명세서 | `D:\VAMOS\docs\sot\VAMOS_STEP7_N-P_보강_상세명세서.md` | 1,809 |
| 3 | STEP7 보강 통합명세서 | `D:\VAMOS\docs\sot\VAMOS_STEP7_보강_통합명세서.md` | 1,523 |

**source_group 지정**: 전체 `F`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C09b.json`

---

#### C-10: BEGINNER + CLAUDE.md + PLAN-2.0

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | BEGINNER_GUIDE | `D:\VAMOS\docs\sot\VAMOS_BEGINNER_GUIDE.md` | 1,844 |
| 2 | CLAUDE.md | `D:\VAMOS\docs\sot\CLAUDE.md` | 697 |
| 3 | PLAN-2.0 | `D:\VAMOS\docs\sot\PLAN-2.0_VAMOS_PLAN_2.0_.md` | 4,350 |

**source_group 지정**: 전체 `I`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C10.json`

---

### ═══ 대화 4: C-11 ~ C-13 (신규 25개 — v10 미분석) ═══

⭐ **핵심**: 이 3개 에이전트는 v10에서 전혀 분석하지 않은 25개 파일을 처리함. 완전 신규 Feature가 다수 발견될 것으로 예상.

#### C-11: STEP7-A 보강 + STEP7-B~I 작업가이드 (9개 파일) ⭐

**대상 파일**:
| # | 파일 | 경로 | 줄 수 | 비고 |
|---|------|------|------|------|
| 1 | STEP7_A-I 보강 (= STEP7-A 작업가이드) | `D:\VAMOS\docs\sot\STEP7_A-I_보강_추가항목_통합.md` | 666 | ⭐ STEP7-A 작업가이드로 분류 |
| 2 | STEP7-B 대화프로세스 작업가이드 | `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` | 1,188 | |
| 3 | STEP7-C UI_UX 전수비교 작업가이드 | `D:\VAMOS\docs\sot\STEP7-C_UI_UX_전수비교_작업가이드.md` | 235 | |
| 4 | STEP7-D 메모리_저장소 아키텍처 작업가이드 | `D:\VAMOS\docs\sot\STEP7-D_메모리_저장소_아키텍처_작업가이드.md` | 294 | |
| 5 | STEP7-E 보안_안전_거버넌스 작업가이드 | `D:\VAMOS\docs\sot\STEP7-E_보안_안전_거버넌스_작업가이드.md` | 1,210 | |
| 6 | STEP7-F 인프라_배포_MLOps 작업가이드 | `D:\VAMOS\docs\sot\STEP7-F_인프라_배포_MLOps_작업가이드.md` | 1,450 | |
| 7 | STEP7-G 벤치마크_평가_품질보증 작업가이드 | `D:\VAMOS\docs\sot\STEP7-G_벤치마크_평가_품질보증_작업가이드.md` | 891 | |
| 8 | STEP7-H 비즈니스모델_시장전략 작업가이드 | `D:\VAMOS\docs\sot\STEP7-H_비즈니스모델_시장전략_작업가이드.md` | 1,053 | |
| 9 | STEP7-I AI_Investing 보강 작업가이드 | `D:\VAMOS\docs\sot\STEP7-I_AI_Investing_보강_작업가이드.md` | 1,349 | |

**총 줄 수**: 8,336줄
**source_group 지정**: STEP7_A-I_보강=`H`, STEP7-B~I 작업가이드(8개)=`G`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C11.json`

---

#### C-12: STEP7-J~P 작업가이드 (7개 파일) ⭐

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | STEP7-J 멀티모달_생성처리 작업가이드 | `D:\VAMOS\docs\sot\STEP7-J_멀티모달_생성처리_작업가이드.md` | 1,698 |
| 2 | STEP7-K 에이전트프로토콜_상호운용성 작업가이드 | `D:\VAMOS\docs\sot\STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md` | 1,416 |
| 3 | STEP7-L 개발자도구_API_SDK 작업가이드 | `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` | 1,026 |
| 4 | STEP7-M PKM_지식관리 작업가이드 | `D:\VAMOS\docs\sot\STEP7-M_PKM_지식관리_작업가이드.md` | 883 |
| 5 | STEP7-N 워크플로우자동화_RPA 작업가이드 | `D:\VAMOS\docs\sot\STEP7-N_워크플로우자동화_RPA_작업가이드.md` | 667 |
| 6 | STEP7-O 교육_학습_자기개발 작업가이드 | `D:\VAMOS\docs\sot\STEP7-O_교육_학습_자기개발_작업가이드.md` | 543 |
| 7 | STEP7-P 건강_웰니스_감성AI 작업가이드 | `D:\VAMOS\docs\sot\STEP7-P_건강_웰니스_감성AI_작업가이드.md` | 668 |

**총 줄 수**: 6,901줄
**source_group 지정**: 전체 `G`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C12.json`

---

#### C-13: STEP7 총론 + 마스터인덱스 + 최종검증 + R1~R6 (9개 파일) ⭐

**대상 파일**:
| # | 파일 | 경로 | 줄 수 |
|---|------|------|------|
| 1 | STEP7 작업가이드 총론 | `D:\VAMOS\docs\sot\STEP7_작업가이드.md` | 940 |
| 2 | STEP6통합 마스터인덱스 | `D:\VAMOS\docs\sot\STEP7_STEP6통합_마스터인덱스.md` | 828 |
| 3 | PHASE7 최종검증보고서 | `D:\VAMOS\docs\sot\STEP7_PHASE7_최종검증보고서.md` | 242 |
| 4 | R1 V1 CRITICAL | `D:\VAMOS\docs\sot\STEP7_R1_V1_CRITICAL.md` | 892 |
| 5 | R2 V1 HIGH | `D:\VAMOS\docs\sot\STEP7_R2_V1_HIGH.md` | 662 |
| 6 | R3 V1 MEDIUM_LOW | `D:\VAMOS\docs\sot\STEP7_R3_V1_MEDIUM_LOW.md` | 178 |
| 7 | R4 V2 CRITICAL_HIGH | `D:\VAMOS\docs\sot\STEP7_R4_V2_CRITICAL_HIGH.md` | 170 |
| 8 | R5 V2 MEDIUM_LOW | `D:\VAMOS\docs\sot\STEP7_R5_V2_MEDIUM_LOW.md` | 140 |
| 9 | R6 V3 ALL | `D:\VAMOS\docs\sot\STEP7_R6_V3_ALL.md` | 154 |

**총 줄 수**: 4,206줄 (그룹 H 전체 = R1~R6 우선순위 목록 포함)
**source_group 지정**: STEP7_작업가이드(총론)=`G`, 나머지 8개(마스터인덱스/최종검증/R1~R6)=`H`

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_src_C13.json`

---

### ═══ 대화 5: Delta + Registry + 인덱스 구축 ═══

#### 0-D: Delta 분석 + 중복 제거 + 병합

**입력**: C-1a ~ C-13 전체 산출물 (15개 JSON)
**작업**:
1. 15개 JSON 로드
2. **⚠️ 필드 값 정규화 (병합 전 필수)**:
   - `priority` 정규화: `P0`→`CRITICAL`, `P1`→`HIGH`, `P2`→`MEDIUM`, `P3`→`LOW`, 기타 비표준→가장 가까운 표준값
   - `category` 정규화: `architecture`→`orange_core`, `config`→`infra`, `registry`→`schemas`, `module`→해당 모듈 판정, `logic`→해당 모듈 판정, `agent_framework`→`agent`, 기타 비표준→컨텍스트 기반 11개 중 매핑
   - `source_group` 정규화: 항목 ID(`K-021` 등)→파일이 속한 그룹 문자(A~I), 에이전트명→파일별 그룹 문자
   - 정규화 불가 시 `_normalization_flag: true` + `_original_value` 필드 추가하여 수동 검토 대상 마킹
3. Layer 1 (CLAUDE.md 기반 Features) ↔ Layer 2 (68개 파일 추출 Features) Delta 분석
4. 중복 Feature 식별 및 제거 (동일 Feature가 여러 SOT 파일에서 추출된 경우)
5. 병합 결과 생성
6. **정규화 통계 출력**: 정규화된 건수를 필드별로 집계 (priority: N건, category: N건, source_group: N건)

**중복 판정 기준**:
- 동일 feature_name + 동일 version_scope → 중복
- 중복 시 정본 우선순위에 따라 상위 source 유지

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_merged_features.json`

---

#### 0-E: v10 Feature Registry 교차 확인

**입력**:
- v12 병합 Features (`v12_merged_features.json`)
- v10 Feature Registry (`v10_feature_registry_final.json`, 3,940건)

**작업**:
1. v12 Features vs v10 Features 교차 비교
2. v12에만 있는 Feature (신규) 식별
3. v10에만 있는 Feature (v12에서 누락되었거나, SOT 변경으로 삭제됨) 식별
4. 양쪽에 있으나 내용이 다른 Feature 식별

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_v10_delta.json`

---

#### 0-F: v12 Feature Registry Final 확정

**입력**: v12 병합 Features + v10 Delta 분석 결과
**작업**:
1. 최종 Feature Registry 확정
2. 통계 계산: 총 건수, version별, category별, extractable별
3. 비교 통계: v10(3,940건) 대비 증감

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_feature_registry_final.json`

**최종 JSON 스키마**:
```json
{
  "metadata": {
    "version": "v12",
    "created": "2026-03-XX",
    "sot_files": 68,
    "sot_lines": 89363,
    "total_features": "N",
    "extractable_true": "N",
    "extractable_false": "N"
  },
  "statistics": {
    "by_version": { "V0": 0, "V1": 0, "V2": 0, "V3": 0, "multi": 0 },
    "by_category": { ... },
    "vs_v10": { "v10_total": 3940, "v12_total": 0, "new": 0, "removed": 0, "changed": 0 }
  },
  "features": [ ... ]
}
```

---

#### 0-I-A: PART2 v25.2.0 섹션 구조 인덱스

**입력**: PART2 v25.2.0 전체
**작업**: 모든 heading (#, ##, ###, ####) 추출 → 섹션 ID + 행 번호 + 제목 매핑

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_section_map.json`

---

#### 0-I-B: 내부 참조 매핑

**입력**: PART2 v25.2.0 전체
**작업**: "§N" + "STEP-N" + "Phase N" + "L번호" + "표 N" 등 모든 내부 참조 → 대상 행 매핑

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_reference_map.json`

---

#### 0-I-C: 수치 전수 등록

**입력**: PART2 v25.2.0 전체
**작업**: LOCK/FREEZE 값 + 수량 + 비용(₩) + 퍼센트(%) + 시간(ms/s/분) 전수 추출

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_numeric_registry.json`

---

#### 0-I-D: 18개 AI 프롬프트 인벤토리

**입력**: PART2 v25.2.0 전체
**작업**: 18개 AI 프롬프트 (V0:6 + V1:6 + V2:3 + V3:3) 위치 + 내용 요약 + 커버하는 작업 목록

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_prompt_inventory.json`

---

#### 0-I-E: §6 참조 57건 → §6.X 예비 매핑

**입력**: PART2 v25.2.0 전체
**작업**:
1. "§6 참조" 또는 "§6" 만 언급하는 곳 57건 전수 추출
2. 각각의 맥락 분석 → 가장 적합한 §6.X (§6.1~§6.13) 매핑 시도
3. 매핑 불가 시 "NO_MATCH" 플래그 + 사유

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_s6_mapping.json`

---

#### 교차검증 ②: Feature Registry 완전성 + 인덱스 정합성

**작업**:
1. Feature Registry 통계 교차검증 (합계 = version별 합 = category별 합)
2. 인덱스 간 참조 무결성 (reference_map의 §N이 section_map에 존재하는지)
3. 프롬프트 인벤토리의 18개가 PART2에서 실제 확인 가능한지
4. §6 매핑의 타당성 (NO_MATCH 건수 확인)

**산출물**: `D:\VAMOS\04. 구현단계\v12\v12_results\phase0\v12_phase0_verdict.md`

---

## 산출물 전수 목록

| # | 파일 | 경로 | 대화 |
|---|------|------|------|
| 1 | C-1a Feature | `v12_results/phase0/v12_src_C01a.json` | 2 |
| 2 | C-1b Feature | `v12_results/phase0/v12_src_C01b.json` | 2 |
| 3 | C-2 Feature | `v12_results/phase0/v12_src_C02.json` | 2 |
| 4 | C-3 Feature | `v12_results/phase0/v12_src_C03.json` | 2 |
| 5 | C-4 Feature | `v12_results/phase0/v12_src_C04.json` | 3 |
| 6 | C-5 Feature | `v12_results/phase0/v12_src_C05.json` | 3 |
| 7 | C-6 Feature | `v12_results/phase0/v12_src_C06.json` | 3 |
| 8 | C-7 Feature | `v12_results/phase0/v12_src_C07.json` | 3 |
| 9 | C-8 Feature | `v12_results/phase0/v12_src_C08.json` | 3 |
| 10 | C-9a Feature | `v12_results/phase0/v12_src_C09a.json` | 3 |
| 11 | C-9b Feature | `v12_results/phase0/v12_src_C09b.json` | 3 |
| 12 | C-10 Feature | `v12_results/phase0/v12_src_C10.json` | 3 |
| 13 | C-11 Feature ⭐ | `v12_results/phase0/v12_src_C11.json` | 4 |
| 14 | C-12 Feature ⭐ | `v12_results/phase0/v12_src_C12.json` | 4 |
| 15 | C-13 Feature ⭐ | `v12_results/phase0/v12_src_C13.json` | 4 |
| 16 | 병합 Features | `v12_results/phase0/v12_merged_features.json` | 5 |
| 17 | v10 Delta | `v12_results/phase0/v12_v10_delta.json` | 5 |
| 18 | Feature Registry Final | `v12_results/phase0/v12_feature_registry_final.json` | 5 |
| 19 | Section Map | `v12_results/phase0/v12_section_map.json` | 5 |
| 20 | Reference Map | `v12_results/phase0/v12_reference_map.json` | 5 |
| 21 | Numeric Registry | `v12_results/phase0/v12_numeric_registry.json` | 5 |
| 22 | Prompt Inventory | `v12_results/phase0/v12_prompt_inventory.json` | 5 |
| 23 | §6 Mapping | `v12_results/phase0/v12_s6_mapping.json` | 5 |
| 24 | Phase 0 Verdict | `v12_results/phase0/v12_phase0_verdict.md` | 5 |

---

## AI 오류 방지 규칙 (이 Phase에서 준수)

1. **환각 금지**: Feature 추출 시 반드시 원본 텍스트 인용 (source_text 필드). 원본에 없는 Feature 생성 금지
2. **부분 읽기 금지**: SOT 파일 전체 읽기. limit 사용 시 나머지 반드시 후속 읽기
3. **라인 번호 직접 확인**: source_line은 파일 읽기 시 직접 확인한 행 번호만 기재
4. **중복 추출 허용**: 같은 Feature가 여러 SOT에서 발견 가능 → 0-D에서 중복 제거
5. **extractable 판정 엄격**: "~해야 한다", "~로 구성된다" 등 원칙/개념은 extractable=false
6. **version_scope 판정**: SOT 원본에 명시적 버전 언급이 없으면, 해당 모듈의 Phase 배치 기반 추론 + "추론" 플래그
7. **대화 간 상태**: 대화 2~4는 C-에이전트 추출만. 대화 5에서 병합 + 인덱스. 대화 간 산출물은 JSON 파일로 전달.
8. **v10 결과 참조 시점**: C-1a~C-13 추출 시에는 v10 결과 참조 금지 (독립 추출). v10은 0-E에서만 교차확인.
9. **필드 값 enum 준수 (MANDATORY)**: `priority`, `category`, `source_group` 필드는 반드시 본 프롬프트 §추출 템플릿 하단의 "필드 값 제약" 테이블에 정의된 값만 사용. C-에이전트가 비표준 값을 생성하면 해당 JSON 전체가 무효 처리됨. 특히:
   - priority: `CRITICAL|HIGH|MEDIUM|LOW` (4개만). `P0/P1/P2` 등 코드형 축약 금지
   - category: 11개 표준 값만. `architecture/config/registry/module/logic/agent_framework` 등 임의 생성 금지
   - source_group: 파일별 그룹 문자 `A~I`만. 항목 ID/에이전트명 사용 금지

---

## 완료 시 수행 (대화 5 마지막)

1. 위 24개 산출물 파일 전수 존재 확인
2. `v12_phase_status.json` 업데이트:
   ```json
   {
     "phase0": {
       "status": "completed",
       "conversation": "대화 2~5",
       "pass": true/false,
       "started_at": "2026-03-XX",
       "completed_at": "2026-03-XX"
     }
   }
   ```
3. Feature Registry Final 통계 요약 출력
4. FAIL이면 사유 기재 + 해당 대화 재실행 또는 전체 Phase 0 재실행
