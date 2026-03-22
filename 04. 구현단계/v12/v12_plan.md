# v12 — VAMOS AI PART2 구현단계 최종 검증 및 완성 계획

> **작성일**: 2026-03-13
> **목표**: SOT 68개 파일(89,363줄) 기준 PART2 구현단계 완전성 검증 + 누락 해소 → 최종본
> **성격**: v12는 v시리즈의 **마지막** 검증 프롬프트. 이후 V0-STEP-1 즉시 착수.
> **방식**: B안 (PART2 전체 독립 점검 + v7/v10 교차확인)

---

## 1. 목표 및 성공 기준

### 1.1 목표

```
입력:  SOT 68개 파일 (89,363줄) — VAMOS AI 전체 설계 원본
대상:  PART2 v25.2.0 (5,858줄) — 구현 가이드
결과:  PART2에 있어야 하는데 없는 것 = 0건
       PART2에 있는데 틀린 것 = 0건
       → PART2 최종본 (V0-STEP-1 즉시 착수 가능)
```

### 1.2 성공 기준 (CHECKPOINT)

| # | 조건 | 판정 기준 |
|---|------|---------|
| 1 | v12 Feature Registry 완성 | SOT 68개 전수 추출, 읽기 완료율 90%+ |
| 2 | SOT→PART2 매핑 100% | extractable=true 전건 매핑 시도 |
| 3 | MISSING BLOCKER 0건 | BLOCKER 심각도 잔여 0건 |
| 4 | 적대적 재검증 PASS | 오판율 ≤ 10% |
| 5 | v10 교차 대사 완료 | v12 vs v10 차이 전건 분석 |
| 6 | v7 역방향 교차 확인 | 추가 누락 0건 확인 |
| 7 | §6 참조 57건 전수 해소 | 구체적 §6.X 매핑 또는 §6 내용 추가 |
| 8 | v11 미해결 패턴 5건 해소 | Pattern A/B, V1 고립, V3 과적재, V2-P2 저커버리지 |
| 9 | PART2 반영 완료 | 전수 패치 + 구조 무결성 PASS |
| 10 | 18개 AI 프롬프트 재검증 | P1~P10 전항목 PASS |
| 11 | 수치/참조 정합성 | 재구축 인덱스 기준 PASS |
| 12 | 원본 보호 | SHA256 백업 + 역패치 가능 |

---

## 2. 입력 파일 전수 목록

### 2.1 SOT 68개 파일 (D:\VAMOS\docs\sot\)

#### 그룹 A: 규칙/계획/마스터 (3개, 9,573줄)
| # | 파일명 | 줄 수 |
|---|--------|------|
| 1 | BASE-1.3_VAMOS_RULE_1.3_BASE.md | 634 |
| 2 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | 7,046 |
| 3 | VAMOS_MASTER_SPECIFICATION.md | 1,893 |

#### 그룹 B: DESIGN 2.0 본문 (8개, 19,626줄)
| # | 파일명 | 줄 수 |
|---|--------|------|
| 4 | D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md | 1,857 |
| 5 | D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md | 4,474 |
| 6 | D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md | 1,943 |
| 7 | D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md | 1,591 |
| 8 | D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md | 1,982 |
| 9 | D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | 2,428 |
| 10 | D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md | 2,655 |
| 11 | D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md | 2,696 |

#### 그룹 C: DESIGN 2.1 스키마 (10개, 5,614줄)
| # | 파일명 | 줄 수 |
|---|--------|------|
| 12 | D2.1-A1_A1_TECH_STACK.md | 401 |
| 13 | D2.1-D1_D1_SCHEMA_GLOSSARY.md | 363 |
| 14 | D2.1-D2_D2_SCHEMA_ORANGE_CORE.md | 547 |
| 15 | D2.1-D3_D3_SCHEMA_BLUE_NODES.md | 759 |
| 16 | D2.1-D4_D4_SCHEMA_INFRA_CORE.md | 518 |
| 17 | D2.1-D5_D5_SCHEMA_AGENT_WORKFLOW.md | 665 |
| 18 | D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md | 394 |
| 19 | D2.1-D7_D7_SCHEMA_SAFETY_COST_APPROVAL.md | 594 |
| 20 | D2.1-D8_D8_SCHEMA_UI_UX.md | 201 |
| 21 | D2.1-Q1_Q1_AUDIT_REPORT.md | 1,172 |

#### 그룹 D: PHASE_B 구현 가이드 (7개, 9,751줄)
| # | 파일명 | 줄 수 |
|---|--------|------|
| 22 | PHASE_B1_API_CONTRACT.md | 2,218 |
| 23 | PHASE_B2_PROJECT_STRUCTURE.md | 886 |
| 24 | PHASE_B3_DEPENDENCIES.md | 367 |
| 25 | PHASE_B4_CONFIG_SPEC.md | 1,242 |
| 26 | PHASE_B5_TEST_STRATEGY.md | 945 |
| 27 | PHASE_B6_CICD_PIPELINE.md | 1,757 |
| 28 | PHASE_B7_MIGRATION_STRATEGY.md | 2,336 |

#### 그룹 E: 전문 SPEC (4개, 6,669줄)
| # | 파일명 | 줄 수 |
|---|--------|------|
| 29 | VAMOS_AGENT_TEAMS_SPEC.md | 2,204 |
| 30 | VAMOS_AI_INVESTING_SPEC.md | 1,379 |
| 31 | VAMOS_CLOUD_LIBRARY_SPEC.md | 1,439 |
| 32 | VAMOS_SDAR_DESIGN_SPECIFICATION.md | 1,647 |

#### 그룹 F: STEP7 상세명세서 (5개, 9,032줄)
| # | 파일명 | 줄 수 |
|---|--------|------|
| 33 | VAMOS_STEP7_A-E_상세명세서.md | 1,000 |
| 34 | VAMOS_STEP7_F-I_상세명세서.md | 2,876 |
| 35 | VAMOS_STEP7_J-M_상세명세서.md | 1,824 |
| 36 | VAMOS_STEP7_N-P_보강_상세명세서.md | 1,809 |
| 37 | VAMOS_STEP7_보강_통합명세서.md | 1,523 |

#### 그룹 G: STEP7 작업가이드 (16개, 15,237줄) ⭐ v10 미분석
| # | 파일명 | 줄 수 | v10 분석 |
|---|--------|------|---------|
| 38 | STEP7_A-I_보강_추가항목_통합.md (= STEP7-A 작업가이드) | 666 | ❌ 미분석 |
| 39 | STEP7-B_대화프로세스_작업가이드.md | 1,188 | ❌ 미분석 |
| 40 | STEP7-C_UI_UX_전수비교_작업가이드.md | 235 | ❌ 미분석 |
| 41 | STEP7-D_메모리_저장소_아키텍처_작업가이드.md | 294 | ❌ 미분석 |
| 42 | STEP7-E_보안_안전_거버넌스_작업가이드.md | 1,210 | ❌ 미분석 |
| 43 | STEP7-F_인프라_배포_MLOps_작업가이드.md | 1,450 | ❌ 미분석 |
| 44 | STEP7-G_벤치마크_평가_품질보증_작업가이드.md | 891 | ❌ 미분석 |
| 45 | STEP7-H_비즈니스모델_시장전략_작업가이드.md | 1,053 | ❌ 미분석 |
| 46 | STEP7-I_AI_Investing_보강_작업가이드.md | 1,349 | ❌ 미분석 |
| 47 | STEP7-J_멀티모달_생성처리_작업가이드.md | 1,698 | ❌ 미분석 |
| 48 | STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md | 1,416 | ❌ 미분석 |
| 49 | STEP7-L_개발자도구_API_SDK_작업가이드.md | 1,026 | ❌ 미분석 |
| 50 | STEP7-M_PKM_지식관리_작업가이드.md | 883 | ❌ 미분석 |
| 51 | STEP7-N_워크플로우자동화_RPA_작업가이드.md | 667 | ❌ 미분석 |
| 52 | STEP7-O_교육_학습_자기개발_작업가이드.md | 543 | ❌ 미분석 |
| 53 | STEP7-P_건강_웰니스_감성AI_작업가이드.md | 668 | ❌ 미분석 |

#### 그룹 H: STEP7 우선순위/인덱스/검증 (9개, 4,206줄) ⭐ v10 미분석
| # | 파일명 | 줄 수 | v10 분석 |
|---|--------|------|---------|
| 54 | STEP7_작업가이드.md (총론) | 940 | ❌ 미분석 |
| 55 | STEP7_STEP6통합_마스터인덱스.md | 828 | ❌ 미분석 |
| 56 | STEP7_PHASE7_최종검증보고서.md | 242 | ❌ 미분석 |
| 57 | STEP7_R1_V1_CRITICAL.md | 892 | ❌ 미분석 |
| 58 | STEP7_R2_V1_HIGH.md | 662 | ❌ 미분석 |
| 59 | STEP7_R3_V1_MEDIUM_LOW.md | 178 | ❌ 미분석 |
| 60 | STEP7_R4_V2_CRITICAL_HIGH.md | 170 | ❌ 미분석 |
| 61 | STEP7_R5_V2_MEDIUM_LOW.md | 140 | ❌ 미분석 |
| 62 | STEP7_R6_V3_ALL.md | 154 | ❌ 미분석 |

#### 그룹 I: Readiness/온보딩/기타 (6개, 9,655줄)
| # | 파일명 | 줄 수 |
|---|--------|------|
| 63 | CLAUDE.md | 697 |
| 64 | PLAN-2.0_VAMOS_PLAN_2.0_.md | 4,350 |
| 65 | VAMOS_BEGINNER_GUIDE.md | 1,844 |
| 66 | VAMOS_IMPLEMENTATION_READINESS_GUIDE.md | 1,256 |
| 67 | VAMOS_IMPLEMENTATION_READINESS_REVIEW.md | 765 |
| 68 | VAMOS_V0_READINESS_FINAL_REVIEW.md | 743 |

**통계**: 68개 파일, 89,363줄. v10 미분석 25개 파일(19,443줄).

### 2.2 PART2 대상 파일

```
D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
버전: v25.2.0 | 줄 수: 5,858
```

### 2.3 v10/v11 기존 산출물 (교차확인용)

| 파일 | 경로 |
|------|------|
| v10 Feature Registry | D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json |
| v10 Consolidated Missing | D:\VAMOS\04. 구현단계\v10_results\phase2\consolidated_missing.json |
| v10 Integrated Result | D:\VAMOS\04. 구현단계\v10_results\phase2\v10_step2_integrated_result.json |
| v10 Phase 2 Final Report | D:\VAMOS\04. 구현단계\v10_results\phase2\v10_phase2_final_report.md |
| v10 Checkpoint | D:\VAMOS\04. 구현단계\v10_results\v10_checkpoint.md |
| v11 Checkpoint | D:\VAMOS\04. 구현단계\v11_results\v11_checkpoint.md |
| v11 Phase Status | D:\VAMOS\04. 구현단계\v11_results\v11_phase_status.json |
| v11 Adversarial Report | D:\VAMOS\04. 구현단계\v11_results\phase15\v11_adversarial_report.md |
| v11 Section Map | D:\VAMOS\04. 구현단계\v11_results\phase0\v11_section_map.json |
| v11 Reference Map | D:\VAMOS\04. 구현단계\v11_results\phase0\v11_reference_map.json |
| v11 Numeric Registry | D:\VAMOS\04. 구현단계\v11_results\phase0\v11_numeric_registry.json |
| v11 Prompt Inventory | D:\VAMOS\04. 구현단계\v11_results\phase0\v11_prompt_inventory.json |
| v11 Terminology Dict | D:\VAMOS\04. 구현단계\v11_results\phase0\v11_terminology_dict.json |
| v11 Codeblock Inventory | D:\VAMOS\04. 구현단계\v11_results\phase0\v11_codeblock_inventory.json |
| v11 v6v10 Reuse Index | D:\VAMOS\04. 구현단계\v11_results\phase0\v11_v6v10_reuse_index.json |

### 2.4 v6~v11 검증 프롬프트 (스킬 에이전트 패턴 참조용)

| 파일 | 경로 |
|------|------|
| v6 | C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_검증_프롬프트_v6.md |
| v7 | C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_검증_프롬프트_v7.md |
| v8 | C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\04. 구현단계\VAMOS_검증_프롬프트_v8.md |
| v9 | D:\VAMOS\04. 구현단계\v9_pipeline_plan.md |
| v10 | D:\VAMOS\04. 구현단계\v10_pipeline_plan.md |
| v11 | D:\VAMOS\04. 구현단계\v11_pipeline_framework_skill.md |

---

## 3. 스킬 에이전트 감사 및 재사용 계획

### 3.1 v6~v11 스킬 에이전트 알려진 오류

| 출처 | 오류 유형 | 상세 | v12 대응 |
|------|---------|------|---------|
| v7~v8 | 라인 번호 기반 참조 | v25.2.0에서 +1,463줄 시프트 → 모든 라인 참조 무효 | Phase 0에서 인덱스 재구축 |
| v10 | SRC 43개만 분석 | 25개 SOT 파일 미분석 (19,443줄) | Phase 0에서 SOT 68개 전수 추출 |
| v10 | Feature Registry v21~v23 기준 | v25.2.0에서 +1,565줄 추가 후 미반영 | Phase 0에서 v12 Registry 독립 구축 |
| v11 | Pattern A: 연쇄 미갱신 | v10 대량 추가 후 프롬프트/체크리스트 미갱신 가능 | Phase -1A에서 확인 |
| v11 | Pattern B: FIX-09 Gate 명칭 미전파 | L3875, L3876, L3927, L3928 | Phase -1A에서 확인 |
| v11 | V1 구조 고립 | 균일성 5/7 항목 ✗ | Phase 2-C에서 해소 |
| v11 | V3 과적재 | 자기완결성 2.5/5 | Phase 2-C에서 해소 |
| v11 | V2-P2 저커버리지 | 116건 중 프롬프트 10건 | Phase 2-C에서 해소 |
| v11 | 적대적 검증 FP율 19.7% | 44/223건 FP | v12 적대적에서 FP 기준 강화 |

### 3.2 재사용할 스킬 에이전트 패턴

| 패턴 | 출처 | v12 적용 위치 | 오류 확인 |
|------|------|-------------|---------|
| 정본 우선순위 | v6 §4-A | 전 Phase | ✅ 변경 없음 |
| 심각도 분류 (H/M/L) | v6 §4-C | Phase 2-E | ✅ 변경 없음 |
| 도메인별 SOT 역방향 MISSING 탐지 | v7 Agent 1~10 | Phase 1 교차확인 | ⚠️ 라인 참조 무효 → 재구축 필요 |
| 4-Dimension 검증 (구조/내용/구현/프롬프트) | v8 | Phase 4 | ✅ 프레임워크 유효 |
| 프롬프트 검증 P1~P10 | v8 Agent 11 | Phase 4-B | ✅ 변경 없음 |
| GT 기반 검증 | v9 GT-1~GT-5 | Phase 0 인덱스 | ⚠️ v25.2.0 기준 재구축 필요 |
| Feature 추출 템플릿 | v10 Phase 0-A | Phase 0 C-에이전트 | ✅ 변경 없음 |
| 12개 SRC 추출 에이전트 | v10 Phase 0-C | Phase 0 C-1a~C-10 | ✅ + C-11~C-13 신규 추가 |
| 6개 매핑 에이전트 | v10 Phase 1 M-1~M-5b | Phase 1 M-1~M-6 | ✅ + M-6 신규 추가 |
| 4-Phase 분류 | v10 Phase 2 | Phase 2 | ✅ 변경 없음 |
| 적대적 재검증 | v10/v11 Phase 1.5 | Phase 1.5 | ✅ FP 기준 강화 |
| 7개 Phase 0 인덱스 | v11 0-A~0-G | Phase 0 인덱스 | ⚠️ v25.2.0 기준 재구축 필요 |
| 원본 보호 프로토콜 BP-1~15 | v11 | Phase 3 | ✅ 변경 없음 |

### 3.3 정본 우선순위 (v6 계승, 전 Phase 적용)

```
RULE 1.3 > PLAN 3.0 > MASTER_SPEC > DESIGN 2.0 LOCK > 전문 SPEC(LOCK)
> DESIGN 본문 > 전문 SPEC(본문) > Schema > TECH_STACK
```

---

## 4. 세션 관리 및 오류 방지

### 4.1 대화창 분리 기준

| 대화 | Phase | 이유 |
|------|-------|------|
| **대화 1** | Phase -1 전체 | 기초 검증 — 컨텍스트 작음 |
| **대화 2** | Phase 0: C-1a~C-3 (기존 43개 중 전반) | SRC 읽기 대량 — 컨텍스트 관리 |
| **대화 3** | Phase 0: C-4~C-10 (기존 43개 중 후반) | SRC 읽기 대량 |
| **대화 4** | Phase 0: C-11~C-13 (신규 25개) | 신규 SOT 전수 추출 |
| **대화 5** | Phase 0: 0-D~0-F (Delta + Registry) + 인덱스 구축 | 병합 + 인덱스 |
| **대화 6** | Phase 1: M-1~M-3 (V0/V1/V2) | 매핑 전반 |
| **대화 7** | Phase 1: M-4~M-6 (V3/§6/프롬프트) | 매핑 후반 |
| **대화 8** | Phase 1.5: 적대적 재검증 | 독립 검증 |
| **대화 9** | Phase 2: 교차 대사 + 확정 + 계획 | 통합 분석 |
| **대화 10** | Phase 3: PART2 업데이트 실행 | 수정 작업 |
| **대화 11** | Phase 4: 최종 검증 + CHECKPOINT | 최종 판정 |

### 4.2 매 대화 시작 프로토콜

```
[Pre-check] 매 새 대화 시작 시 반드시 수행:
① 본 계획 파일 읽기: D:\VAMOS\04. 구현단계\v12\v12_plan.md
② 해당 Phase 프롬프트 읽기: D:\VAMOS\04. 구현단계\v12\prompts\phase{N}_prompt.md
③ 이전 Phase 산출물 확인: D:\VAMOS\04. 구현단계\v12\v12_results\phase{N-1}\
④ 이전 Phase PASS/FAIL 확인
⑤ FAIL이면 해당 Phase 재실행 (새 대화에서)
```

### 4.3 AI 오류 방지 체크리스트

| # | 오류 유형 | 방지 방법 |
|---|---------|---------|
| 1 | **환각 (Hallucination)** | 모든 판정에 evidence_source + evidence_line + evidence_text 3개 필드 필수 |
| 2 | **라인 번호 시프트** | v10/v11 라인 참조 사용 금지. Phase 0에서 재구축한 v12 인덱스만 사용 |
| 3 | **컨텍스트 오버플로우** | 대화별 SOT 파일 수 제한 (~25개/대화, 대화 3 기준 C-4~C-10 = 최대 분량). 대화 분리 기준 §4.1 준수 |
| 4 | **부분 읽기** | 파일 읽기 시 반드시 전체 읽기. `limit` 파라미터 사용 시 나머지도 후속 읽기 |
| 5 | **이전 대화 참조 불가** | 모든 중간 산출물을 JSON/MD 파일로 저장. 다음 대화에서 파일로 로드 |
| 6 | **FP/FN 누적** | Phase 1.5 적대적 재검증 + Phase 4 최종 재검증 이중 방어 |
| 7 | **수정 시 연쇄 파괴** | v11 BP-1~15 원본 보호 프로토콜 적용. 건별 diff 저장 |
| 8 | **에이전트 간 불일치** | 교차검증 7회 (매 Phase 완료 시) |
| 9 | **대화 간 상태 유실** | v12_phase_status.json으로 진행 상태 추적 |
| 10 | **SRC 변경 미감지** | Phase -1C에서 SOT 68개 파일 수정일 전수 확인 |

### 4.4 진행 상태 추적 파일

```json
// D:\VAMOS\04. 구현단계\v12\v12_results\v12_phase_status.json
{
  "current_phase": "phase-1",
  "phases": {
    "phase-1": { "status": "pending", "conversation": null, "pass": null, "started_at": null, "completed_at": null },
    "phase0": { "status": "pending", "conversation": null, "pass": null, "started_at": null, "completed_at": null },
    "phase1": { "status": "pending", "conversation": null, "pass": null, "started_at": null, "completed_at": null },
    "phase15": { "status": "pending", "conversation": null, "pass": null, "started_at": null, "completed_at": null },
    "phase2": { "status": "pending", "conversation": null, "pass": null, "started_at": null, "completed_at": null },
    "phase3": { "status": "pending", "conversation": null, "pass": null, "started_at": null, "completed_at": null },
    "phase4": { "status": "pending", "conversation": null, "pass": null, "started_at": null, "completed_at": null }
  },
  "part2_version_start": "v25.2.0",
  "part2_version_target": "v26.0.0",
  "part2_lines_start": 5858,
  "sot_files_count": 68,
  "sot_total_lines": 89363,
  "last_updated": null
}
```

---

## 5. Phase별 상세 계획

### Phase -1: 기초 검증 (스킬 에이전트 오류 점검)

**대화**: 대화 1
**목표**: v6~v11 스킬 에이전트 재사용 전 오류 점검 + 기반 환경 확인
**프롬프트**: `D:\VAMOS\04. 구현단계\v12\prompts\phase-1_prompt.md`

| 작업 | 내용 | 입력 | 산출물 |
|------|------|------|--------|
| **-1A** | v11 미해결 패턴 5건 현재 상태 확인 (Pattern A/B, V1 고립, V3 과적재, V2-P2) | PART2 v25.2.0 + v11_adversarial_report.md | `v12_results/phase-1/v12_pattern_check.md` |
| **-1B** | v25.1.0/v25.2.0 편집 vs v11 Fix 충돌 점검 | PART2 v25.2.0 + v11 phase2 결과 | `v12_results/phase-1/v12_v25_conflict.md` |
| **-1C** | SOT 68개 파일 수정일 확인 (v10 실행 3/8~3/11 이후 변경 여부) | SOT 68개 파일 메타데이터 | `v12_results/phase-1/v12_sot_currency.md` |
| **-1D** | v10 Feature Registry(3,940건) 샘플 30건 유효성 검증 | v10_feature_registry_final.json + SOT | `v12_results/phase-1/v12_registry_validity.md` |
| **-1E** | 스킬 에이전트 재사용 패턴 확정 + 오류 목록 정리 | v6~v11 프롬프트 6개 파일 | `v12_results/phase-1/v12_agent_pattern_audit.md` |
| **교차검증 ①** | Phase -1 전체 PASS/FAIL | 위 5개 산출물 | `v12_results/phase-1/v12_phase-1_verdict.md` |

---

### Phase 0: SOT 68개 전수 Feature 추출 + 인덱스 구축

**대화**: 대화 2~5
**목표**: SOT 68개 파일에서 Feature 전수 추출 → v12 Feature Registry 구축 + PART2 인덱스 재구축
**프롬프트**: `D:\VAMOS\04. 구현단계\v12\prompts\phase0_prompt.md`

#### Feature 추출 에이전트 (15개)

| 에이전트 | 대화 | 대상 파일 (SOT 경로) | 줄 수 | 산출물 |
|---------|------|-------------------|------|--------|
| **C-1a** | 2 | PLAN-3.0 (#2) | 7,046 | `phase0/v12_src_C01a.json` |
| **C-1b** | 2 | BASE-1.3(#1) + MASTER_SPEC(#3) + READINESS 3개(#66,67,68) | 5,291 | `phase0/v12_src_C01b.json` |
| **C-2** | 2 | D2.0-01(#4) + D2.0-02(#5) | 6,331 | `phase0/v12_src_C02.json` |
| **C-3** | 2 | D2.0-03(#6) + D2.0-04(#7) + D2.0-05(#8) | 5,516 | `phase0/v12_src_C03.json` |
| **C-4** | 3 | D2.0-06(#9) + D2.0-07(#10) | 5,083 | `phase0/v12_src_C04.json` |
| **C-5** | 3 | D2.0-08(#11) + D2.1-D8(#20) | 2,897 | `phase0/v12_src_C05.json` |
| **C-6** | 3 | D2.1-A1(#12) + D2.1-D1~D7(#13~19) + D2.1-Q1(#21) | 5,413 | `phase0/v12_src_C06.json` |
| **C-7** | 3 | PHASE_B1~B7 (#22~28) | 9,751 | `phase0/v12_src_C07.json` |
| **C-8** | 3 | AGENT_TEAMS(#29) + AI_INVESTING(#30) + CLOUD_LIBRARY(#31) + SDAR(#32) | 6,669 | `phase0/v12_src_C08.json` |
| **C-9a** | 3 | STEP7_A-E(#33) + STEP7_F-I(#34) 상세명세서 | 3,876 | `phase0/v12_src_C09a.json` |
| **C-9b** | 3 | STEP7_J-M(#35) + STEP7_N-P(#36) + 보강통합(#37) | 5,156 | `phase0/v12_src_C09b.json` |
| **C-10** | 3 | BEGINNER(#65) + CLAUDE.md(#63) + PLAN-2.0(#64) | 6,891 | `phase0/v12_src_C10.json` |
| **C-11** ⭐ | 4 | STEP7-A보강(#38) + STEP7-B~I 작업가이드(#39~46) | 8,336 | `phase0/v12_src_C11.json` |
| **C-12** ⭐ | 4 | STEP7-J~P 작업가이드 (#47~53) | 6,901 | `phase0/v12_src_C12.json` |
| **C-13** ⭐ | 4 | STEP7_작업가이드총론(#54) + 마스터인덱스(#55) + 최종검증(#56) + R1~R6(#57~62) | 4,206 | `phase0/v12_src_C13.json` |

#### Delta + Registry 확정 (대화 5)

| 작업 | 내용 | 산출물 |
|------|------|--------|
| **0-D** | Layer 1(CLAUDE.md) ↔ Layer 2(68개) Delta 분석 + 중복 제거 + 병합 | `phase0/v12_merged_features.json` |
| **0-E** | v10 Feature Registry(3,940건) 교차 확인 — 신규 추출 vs 기존 비교 | `phase0/v12_v10_delta.json` |
| **0-F** | **v12 Feature Registry Final 확정** | `phase0/v12_feature_registry_final.json` |

#### PART2 인덱스 구축 (대화 5, 병렬)

| 인덱스 | 내용 | 산출물 |
|--------|------|--------|
| **0-I-A** | PART2 v25.2.0 섹션 구조 | `phase0/v12_section_map.json` |
| **0-I-B** | 내부 참조 매핑 (§N, STEP, Phase, L번호) | `phase0/v12_reference_map.json` |
| **0-I-C** | 수치 전수 (LOCK/FREEZE/수량/비용/퍼센트) | `phase0/v12_numeric_registry.json` |
| **0-I-D** | 18개 AI 프롬프트 인벤토리 | `phase0/v12_prompt_inventory.json` |
| **0-I-E** | §6 참조 57건 → §6.X 예비 매핑 | `phase0/v12_s6_mapping.json` |

| **교차검증 ②** | Feature Registry 완전성 + 인덱스 정합성 | `phase0/v12_phase0_verdict.md` |

---

### Phase 1: SOT Feature → PART2 전수 매핑

**대화**: 대화 6~7
**목표**: v12 Feature Registry의 모든 항목을 PART2 v25.2.0에 매핑 → MATCHED/MISSING 판정
**프롬프트**: `D:\VAMOS\04. 구현단계\v12\prompts\phase1_prompt.md`

| 에이전트 | 대화 | 범위 | 입력 | 산출물 |
|---------|------|------|------|--------|
| **M-1** | 6 | PART2 §2 (V0 STEP 1~6) | Registry(V0) + PART2 | `phase1/v12_mapping_M01_v0.json` |
| **M-2** | 6 | PART2 §3 (V1 Phase 1~6) | Registry(V1) + PART2 | `phase1/v12_mapping_M02_v1.json` |
| **M-3** | 6 | PART2 §4 (V2 Phase 1~3) | Registry(V2) + PART2 | `phase1/v12_mapping_M03_v2.json` |
| **M-4** | 7 | PART2 §5 (V3 Phase 1~3) | Registry(V3) + PART2 | `phase1/v12_mapping_M04_v3.json` |
| **M-5a** | 7 | PART2 §6.1~§6.7 | Registry(전체) + PART2 | `phase1/v12_mapping_M05a.json` |
| **M-5b** | 7 | PART2 §6.8~§6.13 + §7 | Registry(전체) + PART2 | `phase1/v12_mapping_M05b.json` |
| **M-6** | 7 | PART2 §1 + §7(변경이력) + 18개 AI 프롬프트 내부 참조 | Registry + 인덱스 | `phase1/v12_mapping_M06.json` |

**판정 기준** (v10 계승):
- **MATCHED**: PART2에 명시적 존재 → 행번호 + 섹션ID
- **PARTIAL**: 관련 내용 있으나 배정 안 됨 → "§6 only" 플래그
- **MISSING**: PART2 어디에도 없음 → 심각도 판정
- **SPREAD**: 여러 Phase에 분산 → 모든 위치 기재
- **NOT_APPLICABLE**: PART2 반영 불필요 → 사유 명시

| **교차검증 ③** | 에이전트 간 중복/충돌 대사 + 통계 검증 | `phase1/v12_phase1_report.md` |

---

### Phase 1.5: 적대적 재검증

**대화**: 대화 8
**목표**: Phase 1 MATCHED/MISSING 판정의 FP/FN 감사
**프롬프트**: `D:\VAMOS\04. 구현단계\v12\prompts\phase15_prompt.md`

| 작업 | 내용 | 산출물 |
|------|------|--------|
| 층화 샘플링 | MATCHED 30건 + MISSING 30건 + PARTIAL 15건 Spot-check (총 75건) | — |
| FP 감사 | MISSING 판정 중 실제 MATCHED | FP 목록 |
| FN 감사 | MATCHED 판정 중 실제 MISSING | FN 목록 |
| REAL_MISSING 확정 | FP/FN 보정 적용 | `phase15/v12_adversarial_report.md` |

**정확도 기준**: 오판율 ≤ 10%. 초과 시 Phase 1 재실행.

| **교차검증 ④** | Spot-check 결과 → REAL_MISSING 확정 | 포함 |

---

### Phase 2: v10 교차 대사 + 최종 누락 확정 + 업데이트 계획

**대화**: 대화 9
**목표**: v12 독립 결과 + v10/v7 기존 결과 교차 대사 → 최종 수정 목록 확정
**프롬프트**: `D:\VAMOS\04. 구현단계\v12\prompts\phase2_prompt.md`

| 작업 | 내용 | 산출물 |
|------|------|--------|
| **2-A** | v12 MISSING vs v10 consolidated_missing(1,068건) 교차 대사 | `phase2/v12_v10_crosscheck.md` |
| **2-B** | v7 역방향 MISSING 교차 확인 | `phase2/v12_v7_crosscheck.md` |
| **2-C** | v11 미해결 패턴 5건 해소 방안 | `phase2/v12_pattern_resolution.md` |
| **2-D** | §6 참조 57건 최종 매핑 확정 (§6.X 존재 vs 부재) | `phase2/v12_s6_final_mapping.md` |
| **2-E** | 심각도 분류 (BLOCKER/HIGH/MEDIUM/LOW) | `phase2/v12_final_missing_list.md` |
| **2-F** | Patch Plan 수립 (수정 순서, 영향 분석) | `phase2/v12_update_plan.md` |

| **교차검증 ⑤** | 최종 목록 + 계획 정합성 | `phase2/v12_phase2_verdict.md` |

---

### Phase 3: PART2 업데이트 실행

**대화**: 대화 10
**목표**: 확정된 수정 사항을 PART2에 반영 (원본 보호 하에)
**프롬프트**: `D:\VAMOS\04. 구현단계\v12\prompts\phase3_prompt.md`

| 작업 | 내용 | 산출물 |
|------|------|--------|
| **3-0** | 원본 백업 + SHA256 지문 (v11 BP-1~3) | `phase3/backup/v25_backup.md` + `phase3/backup/v25_integrity.json` |
| **3-A** | MISSING 항목 PART2 반영 (Phase별 테이블 삽입) | PART2 수정 + `phase3/diffs/` |
| **3-B** | §6 참조 57건 해소 (구체적 §6.X 변환 또는 §6 내용 추가) | PART2 수정 + `phase3/diffs/` |
| **3-C** | v11 미해결 패턴 5건 해소 (A, B, V1 고립, V3 과적재, V2-P2 저커버리지) | PART2 수정 + `phase3/diffs/` |
| **3-D** | v12 impl_skill_agent §5.2 동기화 + impl_status.json 갱신 | v12 문서 수정 |
| **3-E** | V0-STEP-6 R1~R11 참조 + §6.12.6 번호 중복 등 소폭 수정 | PART2 수정 |
| **3-F** | 버전 업데이트 (v25.2.0 → v26.0.0) + changelog 추가 | PART2 수정 |
| **Ripple Map** | 수정 건별 영향 추적 | `phase3/v12_ripple_map.json` |

| **교차검증 ⑥** | 건별 diff 검증 + 구조 무결성 | `phase3/v12_phase3_verdict.md` |

---

### Phase 4: 최종 검증 + CHECKPOINT

**대화**: 대화 11
**목표**: PART2 최종본(v26.0.0) 전수 재검증 → CHECKPOINT 판정
**프롬프트**: `D:\VAMOS\04. 구현단계\v12\prompts\phase4_prompt.md`

| 작업 | 내용 | 산출물 |
|------|------|--------|
| **4-A** | 인덱스 전수 재구축 (v26.0.0 기준) | `phase4/v12_final_section_map.json` 등 |
| **4-B** | 18개 AI 프롬프트 재검증 (v8 P1~P10) | `phase4/v12_prompt_validation.md` |
| **4-C** | 수치/참조/용어 정합성 재검증 | `phase4/v12_consistency_check.md` |
| **4-D** | 18개 Stage Gate 전수 확인 | `phase4/v12_stagegate_check.md` |
| **4-E** | SOT 68개 → PART2 최종 커버리지 판정 | `phase4/v12_coverage_final.md` |
| **4-F** | 적대적 재검증 (수정 후) | `phase4/v12_final_adversarial.md` |
| **4-G** | **CHECKPOINT** (§1.2 성공 기준 12개 전수 판정) | `v12_results/v12_checkpoint.md` + `phase4/v12_final_validation.md` |

| **교차검증 ⑦** | 전수 최종 PASS/FAIL | 포함 |

---

## 6. 산출물 디렉토리 구조

```
D:\VAMOS\04. 구현단계\v12\
├── v12_plan.md                          ← 본 문서
├── v12_impl_skill_agent.md              ← 기존 구현 스킬 에이전트 (Phase 3-D에서 갱신)
├── prompts/                             ← Phase별 AI 프롬프트 (별도 파일)
│   ├── phase-1_prompt.md
│   ├── phase0_prompt.md
│   ├── phase1_prompt.md
│   ├── phase15_prompt.md
│   ├── phase2_prompt.md
│   ├── phase3_prompt.md
│   └── phase4_prompt.md
└── v12_results/
    ├── v12_phase_status.json            ← 진행 상태 추적
    ├── phase-1/                         ← 기초 검증 결과
    │   ├── v12_pattern_check.md
    │   ├── v12_v25_conflict.md
    │   ├── v12_sot_currency.md
    │   ├── v12_registry_validity.md
    │   ├── v12_agent_pattern_audit.md
    │   └── v12_phase-1_verdict.md
    ├── phase0/                          ← Feature 추출 + 인덱스
    │   ├── v12_src_C01a.json ~ v12_src_C13.json (15개)
    │   ├── v12_merged_features.json
    │   ├── v12_v10_delta.json
    │   ├── v12_feature_registry_final.json  ← 핵심
    │   ├── v12_section_map.json
    │   ├── v12_reference_map.json
    │   ├── v12_numeric_registry.json
    │   ├── v12_prompt_inventory.json
    │   ├── v12_s6_mapping.json
    │   └── v12_phase0_verdict.md
    ├── phase1/                          ← SOT→PART2 매핑
    │   ├── v12_mapping_M01_v0.json ~ v12_mapping_M06.json (7개)
    │   └── v12_phase1_report.md
    ├── phase15/                         ← 적대적 재검증
    │   └── v12_adversarial_report.md
    ├── phase2/                          ← 최종 누락 확정
    │   ├── v12_v10_crosscheck.md
    │   ├── v12_v7_crosscheck.md
    │   ├── v12_pattern_resolution.md
    │   ├── v12_s6_final_mapping.md
    │   ├── v12_final_missing_list.md    ← 핵심
    │   ├── v12_update_plan.md
    │   └── v12_phase2_verdict.md
    ├── phase3/                          ← 업데이트 실행
    │   ├── backup/
    │   │   ├── VAMOS_구현가이드_PART2_구현단계_v25.2.0_backup.md
    │   │   ├── v25_backup.md
    │   │   └── v25_integrity.json
    │   ├── diffs/                       ← 건별 diff
    │   ├── v12_ripple_map.json
    │   └── v12_phase3_verdict.md
    ├── phase4/                          ← 최종 검증
    │   ├── v12_final_section_map.json
    │   ├── v12_prompt_validation.md
    │   ├── v12_consistency_check.md
    │   ├── v12_stagegate_check.md
    │   ├── v12_coverage_final.md
    │   ├── v12_final_adversarial.md
    │   └── v12_final_validation.md      ← 4-G (CHECKPOINT 판정) 산출물
    └── v12_checkpoint.md                ← 최종 완료 판정
```

---

## 7. 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| v1 | 2026-03-13 | 초기 작성 — SOT 68개 기반 B안 최종 계획 |
