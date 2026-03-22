# VAMOS v10 Pipeline — Feature Coverage 완전 검증 계획서

> **버전**: v10.1.0-PLAN (v10.0.0 대비 33개 약점 보완 완료)
> **작성일**: 2026-03-08
> **대상 문서**: `VAMOS_구현가이드_PART2_구현단계.md` v21.0.0 (3,807줄+)
> **목적**: SRC 43개 파일의 모든 구현 기능 항목이 PART2 구현 Phase에 빠짐없이 매핑되었는지 검증
> **전제**: v6(구조) → v7(SOT교차) → v8(4-Dim통합) → v9(구현준비) 완료. 정합성/실현성은 확인됨. **완전성(completeness)만 미검증**
> **핵심 원칙**: V8/V9 산출물은 "참고"일 뿐 "신뢰"하지 않는다 → 반드시 1:1 재검증

---

# 목차

1. [v6-v9 vs v10 포지션](#1-v6-v9-vs-v10-포지션)
2. [파일 및 기본 규칙](#2-파일-및-기본-규칙)
3. [검증 흐름 총괄](#3-검증-흐름-총괄)
4. [약점 전수 분석 및 방어 규칙](#4-약점-전수-분석-및-방어-규칙)
5. [Phase 0-A: 기능 항목 단위 정의 + 추출 템플릿](#5-phase-0-a)
6. [Phase 0-B: CLAUDE.md 기능 인덱스 추출 (Layer 1)](#6-phase-0-b)
7. [Phase 0-C: 43개 SRC 전수 기능 추출 (Layer 2)](#7-phase-0-c)
8. [Phase 0-D: CLAUDE.md ↔ SRC 교차 검증 (Delta)](#8-phase-0-d)
9. [Phase 0-E: V8/V9 산출물 1:1 재검증](#9-phase-0-e)
10. [Phase 0-F: 최종 Feature Registry 확정 (Ground Truth)](#10-phase-0-f)
11. [Phase 1: Feature → PART2 매핑 검증](#11-phase-1)
12. [Phase 1.5: 적대적 재검증](#12-phase-1-5)
13. [Phase 2: 누락 항목 반영 + 재검증](#13-phase-2)
14. [완료 판정 (CHECKPOINT)](#14-checkpoint)
15. [대화별 실행 가이드](#15-대화별-실행-가이드)
16. [입출력 파일 인덱스](#16-입출력-파일-인덱스)

---

# 1. v6-v9 vs v10 포지션

```
v6 (완료)     구조 무결성        — 테이블/heading/ID/산술/LOCK 추출
v7 (완료)     SOT 교차 검증      — 41 SRC ↔ PART 값 일치 (189항목)
v8 (완료)     4-Dim 통합 검증    — 구조 + 내용정합 + 구현실현 + 프롬프트 (~791항목)
v9 (완료)     구현 준비 완전성    — 의존성/경로/구현가능/산출물/수량/외부의존 (877 checks)
─────────────────────────────────────────────────────────────
v10 (본 계획)  Feature Coverage   — SRC 43개 기능 항목 → PART2 Phase 1:1 매핑 완전성

v6-v9 공통 맹점:
  "PART2에 있는 내용이 맞는지" = 정합성(correctness) ← 4번 검증 완료
  "PART2에 있어야 할 내용이 있는지" = 완전성(completeness) ← 0번 검증 = v10 대상
```

---

# 2. 파일 및 기본 규칙

## 2.1 주 검증 대상

| 구분 | 파일명 | 버전 | 경로 |
|------|--------|------|------|
| **PART2** | `VAMOS_구현가이드_PART2_구현단계.md` | v21.0.0 | `D:\VAMOS\docs\guides\` |

## 2.2 원본 파일 (SRC 43개, CLAUDE.md 포함)

> **원본 경로**: `C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\00. 통합\02. TECH\00. FINAL SUMMARY\STEP6_pipeline\output\updated\`
> **V10 사용 경로 (고정)**: `D:\VAMOS\docs\sot\` (v9 Phase -1G에서 복사 완료, 원본과 동일 확인 완료)
> **⚠ 모든 에이전트는 반드시 `D:\VAMOS\docs\sot\` 경로만 사용한다. OneDrive 경로 직접 참조 금지.**

### 그룹 A: 설계 (20개)

| # | 약칭 | 파일명 | 줄 수 |
|---|------|--------|-------|
| 1 | BASE-1.3 | `BASE-1.3_VAMOS_RULE_1.3_BASE.md` | 634 |
| 2 | PLAN-3.0 | `PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md` | 7,046 |
| 3 | D2.0-01 | `D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md` | 1,857 |
| 4 | D2.0-02 | `D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` | 4,474 |
| 5 | D2.0-03 | `D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md` | 1,943 |
| 6 | D2.0-04 | `D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md` | 1,591 |
| 7 | D2.0-05 | `D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` | 1,982 |
| 8 | D2.0-06 | `D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` | 2,428 |
| 9 | D2.0-07 | `D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` | 2,655 |
| 10 | D2.0-08 | `D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | 2,696 |
| 11 | D2.1-A1 | `D2.1-A1_A1_TECH_STACK.md` | 401 |
| 12 | D2.1-D1 | `D2.1-D1_D1_SCHEMA_GLOSSARY.md` | 363 |
| 13 | D2.1-D2 | `D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` | 547 |
| 14 | D2.1-D3 | `D2.1-D3_D3_SCHEMA_BLUE_NODES.md` | 759 |
| 15 | D2.1-D4 | `D2.1-D4_D4_SCHEMA_INFRA_CORE.md` | 518 |
| 16 | D2.1-D5 | `D2.1-D5_D5_SCHEMA_AGENT_WORKFLOW.md` | 665 |
| 17 | D2.1-D6 | `D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md` | 394 |
| 18 | D2.1-D7 | `D2.1-D7_D7_SCHEMA_SAFETY_COST_APPROVAL.md` | 594 |
| 19 | D2.1-D8 | `D2.1-D8_D8_SCHEMA_UI_UX.md` | 201 |
| 20 | D2.1-Q1 | `D2.1-Q1_Q1_AUDIT_REPORT.md` | 1,172 |

### 그룹 B: 구현가이드 (7개)

| # | 약칭 | 파일명 | 줄 수 |
|---|------|--------|-------|
| 21 | PHASE_B1 | `PHASE_B1_API_CONTRACT.md` | 2,218 |
| 22 | PHASE_B2 | `PHASE_B2_PROJECT_STRUCTURE.md` | 886 |
| 23 | PHASE_B3 | `PHASE_B3_DEPENDENCIES.md` | 367 |
| 24 | PHASE_B4 | `PHASE_B4_CONFIG_SPEC.md` | 1,242 |
| 25 | PHASE_B5 | `PHASE_B5_TEST_STRATEGY.md` | 945 |
| 26 | PHASE_B6 | `PHASE_B6_CICD_PIPELINE.md` | 1,757 |
| 27 | PHASE_B7 | `PHASE_B7_MIGRATION_STRATEGY.md` | 2,336 |

### 그룹 C: 전문 SPEC (5개)

| # | 약칭 | 파일명 | 줄 수 |
|---|------|--------|-------|
| 28 | MASTER_SPEC | `VAMOS_MASTER_SPECIFICATION.md` | 1,893 |
| 29 | AI_INVESTING | `VAMOS_AI_INVESTING_SPEC.md` | 1,379 |
| 30 | CLOUD_LIBRARY | `VAMOS_CLOUD_LIBRARY_SPEC.md` | 1,439 |
| 31 | AGENT_TEAMS | `VAMOS_AGENT_TEAMS_SPEC.md` | 2,204 |
| 32 | SDAR_SPEC | `VAMOS_SDAR_DESIGN_SPECIFICATION.md` | 1,647 |

### 그룹 D: STEP7 상세 (5개)

| # | 약칭 | 파일명 | 줄 수 |
|---|------|--------|-------|
| 33 | STEP7_A-E | `VAMOS_STEP7_A-E_상세명세서.md` | 1,000 |
| 34 | STEP7_F-I | `VAMOS_STEP7_F-I_상세명세서.md` | 2,876 |
| 35 | STEP7_J-M | `VAMOS_STEP7_J-M_상세명세서.md` | 1,824 |
| 36 | STEP7_N-P | `VAMOS_STEP7_N-P_보강_상세명세서.md` | 1,809 |
| 37 | STEP7_보강 | `VAMOS_STEP7_보강_통합명세서.md` | 1,523 |

### 그룹 E: 기타 (1개)

| # | 약칭 | 파일명 | 줄 수 |
|---|------|--------|-------|
| 38 | BEGINNER | `VAMOS_BEGINNER_GUIDE.md` | 1,844 |

### 그룹 F: CLAUDE.md (1개)

| # | 약칭 | 파일명 | 줄 수 |
|---|------|--------|-------|
| 39 | CLAUDE.md | `CLAUDE.md` | 697 |

### 그룹 G: 가이드/리뷰 (4개)

| # | 약칭 | 파일명 | 줄 수 |
|---|------|--------|-------|
| 40 | READINESS_GUIDE | `VAMOS_IMPLEMENTATION_READINESS_GUIDE.md` | 1,256 |
| 41 | READINESS_REVIEW | `VAMOS_IMPLEMENTATION_READINESS_REVIEW.md` | 765 |
| 42 | V0_READINESS | `VAMOS_V0_READINESS_FINAL_REVIEW.md` | 743 |
| 43 | PLAN-2.0 | `PLAN-2.0_VAMOS_PLAN_2.0_.md` | 4,350 (SUPERSEDED) |

> **검증**: 20+7+5+5+1+1+4 = **43개** (v9 SOT 매핑과 일치 확인)
> **제외**: `메이커 에반.md` — 사용자 작업 파일, SRC 아님

## 2.3 V8/V9 기존 산출물 (Phase 0-E 재검증 대상)

| 산출물 | 경로 |
|--------|------|
| V8 Phase 0 결과 (14개 JSON) | `D:\VAMOS\04. 구현단계\v8_results\phase0\0-A.json` ~ `IMP-F.json` |
| V8 Phase 1 Agent 결과 (12개) | `D:\VAMOS\04. 구현단계\v8_results\phase1\대화01_agent01.md` ~ `대화12_agent12_d202.md` |
| V8 Phase 2 Checkpoint | `D:\VAMOS\04. 구현단계\v8_results\phase2\대화17_phase2c_checkpoint.md` |
| V9 SOT 매핑 | `D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_sot_mapping.json` |
| V9 GT-1 파일 경로 | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt1_file_path_registry.json` |
| V9 GT-2 산출물 체인 | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt2_artifact_chain.json` |
| V9 GT-3 수량 인덱스 | `D:\VAMOS\04. 구현단계\v9_results\phase0\gt3_quantity_index.json` |
| V9 Phase 1 최종 보고 | `D:\VAMOS\04. 구현단계\v9_results\phase1\phase1_final_report.md` |
| V9 Phase 2 최종 보고 | `D:\VAMOS\04. 구현단계\v9_results\phase2\v9_phase2_final_report.md` |

## 2.4 V10 산출물 경로

```
D:\VAMOS\04. 구현단계\v10_results\
├── phase0-a\
│   └── v10_feature_definition.md          ← 기능 항목 단위 정의 + 추출 템플릿
├── phase0-b\
│   └── v10_layer1_claude_features.json    ← CLAUDE.md 기능 인덱스
├── phase0-c\
│   ├── v10_src_C01a_plan.json             ← SRC 에이전트 C-1a 추출 (PLAN-3.0)
│   ├── v10_src_C01b_base_master_ready.json← SRC 에이전트 C-1b 추출 (BASE+MASTER+READINESS)
│   ├── v10_src_C02_overview_orange.json   ← SRC 에이전트 C-2 추출 결과
│   ├── v10_src_C03_blue_infra_wf.json     ← SRC 에이전트 C-3 추출 결과
│   ├── v10_src_C04_storage_safety.json    ← SRC 에이전트 C-4 추출 결과
│   ├── v10_src_C05_uiux.json              ← SRC 에이전트 C-5 추출 결과
│   ├── v10_src_C06_schema.json            ← SRC 에이전트 C-6 추출 결과
│   ├── v10_src_C07_phase_b.json           ← SRC 에이전트 C-7 추출 결과
│   ├── v10_src_C08_spec.json              ← SRC 에이전트 C-8 추출 결과
│   ├── v10_src_C09a_step7_ai.json         ← SRC 에이전트 C-9a 추출 (STEP7 A~I)
│   ├── v10_src_C09b_step7_jp.json         ← SRC 에이전트 C-9b 추출 (STEP7 J~P+보강)
│   ├── v10_src_C10_beginner_claude.json   ← SRC 에이전트 C-10 추출 결과
│   └── v10_src_coverage_report.md         ← 에이전트별 읽기 완료율 보고
├── phase0-d\
│   ├── v10_layer1_layer2_delta.json       ← CLAUDE.md ↔ SRC 차이
│   └── v10_merged_features.json           ← 병합 + 중복제거된 기능 목록
├── phase0-e\
│   ├── v10_v8_revalidation.json           ← V8 산출물 재검증 결과
│   ├── v10_v9_revalidation.json           ← V9 산출물 재검증 결과
│   └── v10_revalidation_report.md         ← 재검증 종합 보고
├── phase0-f\
│   └── v10_feature_registry_final.json    ← 최종 Feature Registry (Ground Truth)
├── phase1\
│   ├── v10_mapping_M01_v0.json            ← V0 기능→PART2 매핑 결과
│   ├── v10_mapping_M02_v1.json            ← V1 기능→PART2 매핑 결과
│   ├── v10_mapping_M03_v2.json            ← V2 기능→PART2 매핑 결과
│   ├── v10_mapping_M04_v3.json            ← V3 기능→PART2 매핑 결과
│   ├── v10_mapping_M05a_sys_front.json    ← §6.1~§6.7 매핑 결과
│   ├── v10_mapping_M05b_sys_back.json     ← §6.8~§6.13 + §7 매핑 결과
│   └── v10_phase1_report.md               ← Phase 1 종합 보고
├── phase15\
│   └── v10_adversarial_report.md          ← 적대적 재검증 결과
├── phase2\
│   ├── v10_missing_items_list.md          ← 확정 누락 항목 목록
│   ├── v10_part2_patch_plan.md            ← PART2 반영 계획
│   └── v10_phase2_final_report.md         ← 최종 보고
└── v10_checkpoint.md                      ← 완료 판정
```

## 2.5 정본 우선순위 (LOCK)

```
RULE 1.3 > PLAN 3.0 > MASTER_SPEC > DESIGN 2.0 LOCK > 전문 SPEC(LOCK)
> DESIGN 본문 > 전문 SPEC(본문) > Schema > TECH_STACK
```

## 2.6 절대 규칙

```
1.  파일을 수정하지 않는다. 검증 결과만 보고한다. (Phase 2 제외)
2.  V8/V9 "PASS" 판정을 무조건 신뢰하지 않는다. 1:1 재검증 필수.
3.  자동 스크립트 추출에 의존하지 않는다. 에이전트가 직접 읽고 추출한다.
4.  기능 항목의 "단위"를 먼저 확립한 뒤 추출한다. (Phase 0-A)
5.  추출 누락(FN)을 최소화하기 위해 Layer 1 ↔ Layer 2 교차 검증을 반드시 수행한다.
6.  모든 보고에 SRC 파일명 + 행번호 + PART2 행번호(+섹션ID)를 반드시 기재한다.
7.  STEP7 TITLE_ONLY 항목은 extractable=false로 태깅하되, 건수는 카운트한다.
8.  사용자 확인 없이 Phase 전환하지 않는다.
9.  SRC 경로는 반드시 D:\VAMOS\docs\sot\ 만 사용한다. OneDrive 직접 참조 금지.
10. 각 Phase 시작 시 선행 산출물 파일 존재 여부를 확인한다. 없으면 진행 중단.
11. 산출물 저장 후 파일 존재 확인(Read 1줄)을 수행한다.
12. Feature Registry 총 건수 예상 범위: 300~800건. 범위 이탈 시 원인 분석 + 사용자 확인.
13. 에이전트 실패 시: (1)실패 지점 기록 (2)미완료 부분만 재실행 (3)재시도 최대 2회
    (4)2회 실패 시 파일 분할 후 재실행.
14. Phase 전환 승인 프로토콜:
    → 에이전트가 "Phase X 완료 보고" 출력 (통계 + 이슈 요약)
    → 사용자가 "승인" 또는 "보류(사유)" 응답
    → 부분 승인 허용: "Phase 0-C까지 승인, 0-D 보류" 가능
```

---

# 3. 검증 흐름 총괄

```
Phase 0-A ─── 기능 항목 단위 정의 + 추출 템플릿 확립
    │
Phase 0-B ─── CLAUDE.md 기능 인덱스 추출 (Layer 1)
    │           ~384개 기능 항목 기준선
    │
Phase 0-C ─── 43개 SRC 전수 기능 추출 (Layer 2)
    │           12개 에이전트 (C-1a~C-10), 각 파일 전문 읽기
    │
Phase 0-D ─── CLAUDE.md ↔ SRC 교차 검증
    │           Delta 식별 + 중복 병합 + 사용자 판정
    │
Phase 0-E ─── V8/V9 산출물 1:1 재검증
    │           IMP-B~F + SOT매핑 + GT 결과의 실제 커버 범위 확인
    │
Phase 0-F ─── 최종 Feature Registry 확정
    │           v10_feature_registry_final.json = Phase 1 유일한 입력
    │
    ▼ ─── 사용자 승인 ───
    │
Phase 1 ──── Feature → PART2 매핑 검증
    │           6개 에이전트 (M-1~M-4, M-5a, M-5b), 버전별 + 교차
    │
Phase 1.5 ── 적대적 재검증
    │           MATCHED/MISSING 판정 정확성 감사
    │
Phase 2 ──── 누락 항목 PART2 반영 + 재검증
    │
CHECKPOINT ── 완료 판정
```

**총 대화 수**: ~30개

| 대화 | Phase | 에이전트 | 내용 | SRC 줄 수 |
|------|-------|---------|------|-----------|
| 0 | 0-A | — | 기능 항목 단위 정의 + 추출 템플릿 확립 | — |
| 1 | 0-B | Layer 1 | CLAUDE.md → 기능 인덱스 + 용어 매핑 테이블 | 697 |
| 2 | 0-C | C-1a | PLAN-3.0 단독 전수 추출 | 7,046 |
| 3 | 0-C | C-1b | BASE-1.3 + MASTER_SPEC + READINESS×3 | 5,291 |
| 4 | 0-C | C-2 | D2.0-01 + D2.0-02 | 6,331 |
| 5 | 0-C | C-3 | D2.0-03 + D2.0-04 + D2.0-05 | 5,516 |
| 6 | 0-C | C-4 | D2.0-06 + D2.0-07 | 5,083 |
| 7 | 0-C | C-5 | D2.0-08 + D2.1-D8 (UI 핵심) | 2,897 |
| 8 | 0-C | C-6 | D2.1-A1 + D2.1-D1~D7 + D2.1-Q1 (스키마 9개) | 5,414 |
| 9 | 0-C | C-7 | PHASE_B1~B7 (⚠ 과부하 시 분할) | 9,751 |
| 10 | 0-C | C-8 | AI_INVESTING + CLOUD_LIBRARY + AGENT_TEAMS + SDAR | 6,669 |
| 11 | 0-C | C-9a | STEP7_A-E + STEP7_F-I | 3,876 |
| 12 | 0-C | C-9b | STEP7_J-M + STEP7_N-P + STEP7_보강 | 5,156 |
| 13 | 0-C | C-10 | BEGINNER + CLAUDE.md(독립확인) + PLAN-2.0(스캔) | 6,891 |
| 14 | 0-D | Delta-1 | JSON 정규화 + Layer 1↔Layer 2 Delta 분석 | — |
| 15 | 0-D | Delta-2 | 버전 확인 + 중복 병합 | — |
| 16 | 0-D | Delta-3 | 판단필요 정리 + V_UNKNOWN 확정 + 사용자 판정 | — |
| 17 | 0-E | V8 재검증 | V8 IMP-B~F + Agent 7 결과 1:1 재검증 | — |
| 18 | 0-E | V9 재검증 | V9 SOT매핑 + GT-1~3 + Phase 1 결과 재검증 | — |
| 19 | 0-F | Registry | Feature Registry 최종 확정 + 사용자 승인 | — |
| 20 | 1 | M-1 | V0 기능 → PART2 §2 매핑 | — |
| 21 | 1 | M-2 | V1 기능 → PART2 §3 매핑 | — |
| 22 | 1 | M-3 | V2 기능 → PART2 §4 매핑 | — |
| 23 | 1 | M-4 | V3 기능 → PART2 §5 매핑 | — |
| 24 | 1 | M-5a | §6.1~§6.7 매핑 | — |
| 25 | 1 | M-5b | §6.8~§6.13 + §7 + V_UNKNOWN + 통합 보고 | — |
| 26 | 1.5 | 적대적 | MATCHED/MISSING FP/FN 감사 (층화 샘플링 30~60건) | — |
| 27 | 2 | 목록 확정 | 누락 항목 목록 + Ripple Map + 반영 계획 | — | ✅ 완료 |
| 28 | 2 | PART2 수정 | 수정 반영 + 행번호 매핑 테이블 | — | ✅ 완료 |
| 29 | 2 | Step 1/2 분류 | 1,068건 정밀 분류 (67건 제외 → 1,001건 잔여) | — | ✅ 완료 |
| 30 | 2 | 1,001건 전수 검증 | Step 2 잔여 1,001건 PART2 커버리지 자동 검증 → 미커버 발견 시 재분류+수정 | — | ▶ **여기서부터** |
| 31 | 2 | 재검증 | 구조 검증 + MATCHED 영향 확인 + 대화 30 결과 반영 | — | 미시작 |
| 32 | CP | 판정 | 9개 완료 조건 판정 | — | 미시작 |

---

# 4. 약점 전수 분석 및 방어 규칙

## 4.1 추출 단계 약점 (Phase 0-A~C)

| # | 약점 | 위험도 | Phase | 방어 규칙 | 잔여 위험 |
|---|------|--------|-------|----------|----------|
| W-01 | 에이전트마다 추출 기준 불일치 | HIGH | 0-A | 표준 템플릿 + "기능 항목" 단위 정의를 Phase 0-A에서 먼저 확립. 모든 에이전트에 동일 템플릿 강제 | LOW |
| W-02 | "기능"과 "설명"의 경계 모호 | HIGH | 0-C | "PART2 Phase에 배정 가능한 최소 독립 구현 단위"만 추출. 원칙/철학/용어 정의는 제외. 판단 애매한 경우 "판단필요" 태그 → Phase 0-D에서 사용자 판정 | LOW |
| W-03 | SRC 파일을 끝까지 못 읽음 (컨텍스트 초과) | HIGH | 0-C | 각 에이전트가 읽기 완료율 보고 필수. **90% 미만** 읽은 파일 → 파일 분할 재실행. 미읽은 줄 범위 명시. 마지막 읽은 줄 내용 1줄 인용 필수 (거짓 보고 방지) | LOW (분할로 해소) |
| W-04 | 기능 누락 (FN) | HIGH | 0-C,D | Phase 0-D에서 Layer 1(CLAUDE.md) ↔ Layer 2(SRC) 교차 검증. Layer 1에 있는데 Layer 2에 없으면 → 해당 SRC 파일 재확인 | LOW |
| W-05 | 기능 과다 추출 (FP) | MED | 0-C,D | Phase 0-D에서 "설명 vs 기능" 필터링. 사용자 판정 | LOW |
| W-06 | STEP7 TITLE_ONLY (~675건) | MED | 0-C | extractable=false 태깅. 건수만 카운트. V2 CRITICAL ~190건은 별도 목록으로 관리 | MED (본질적 한계) |
| W-07 | 여러 SRC에 같은 기능이 다른 표현으로 존재 | MED | 0-D | feature_name + version_scope + category 복합 매칭으로 중복 탐지 → 병합 | LOW |
| W-08 | 버전 스코프 오판 (V2 기능을 V1으로 태깅) | MED | 0-C,D | 명시적 태그 없으면 "추론" 플래그 표시. Phase 0-D에서 PLAN-3.0 로드맵과 교차 확인 | LOW |

## 4.2 재검증 단계 약점 (Phase 0-E)

| # | 약점 | 위험도 | Phase | 방어 규칙 | 잔여 위험 |
|---|------|--------|-------|----------|----------|
| W-09 | V8/V9 "PASS" 판정의 실제 범위를 오해 | HIGH | 0-E | 각 산출물이 정확히 뭘 검증했는지 명시하고, 검증하지 않은 관점을 나열. "값 일치 PASS"와 "Phase 배정 확인"은 다른 검증임을 구분 | LOW |
| W-10 | PART2 버전 불일치 (V8=v18, V9=v20.4→v21) | MED | 0-E | 버전 간 변경사항(changelog) 식별. v18→v21 사이 추가/삭제된 항목 목록 작성 | LOW |
| W-11 | V8/V9 산출물 자체에 오류 존재 가능 | MED | 0-E | V8/V9 결과를 "참고"로만 사용. Phase 0-C의 독립 추출 결과가 primary source | LOW |

## 4.3 매핑 단계 약점 (Phase 1)

| # | 약점 | 위험도 | Phase | 방어 규칙 | 잔여 위험 |
|---|------|--------|-------|----------|----------|
| W-12 | 기능이 PART2에서 다른 이름으로 존재 → 매핑 실패 | HIGH | 1 | feature_name 외에 모듈ID, 파일경로, 기술명 복합 검색. "찾지 못함" 즉시 보고 (추측 금지) | LOW |
| W-13 | §6 시스템별 상세에 존재하지만 §2-§5 Phase에는 없는 항목 | MED | 1 | M-5a/M-5b 에이전트가 §6-§7 전수 커버. §6에만 있고 Phase에 없으면 "배정 누락" 보고 | LOW |
| W-14 | PART2의 "요약 표현"을 "부재"로 오판 | MED | 1 | v8 RULE-5 계승: 요약 테이블 vs 전체 열거는 구조적 차이이지 누락이 아님 | LOW |
| W-15 | 기능이 여러 Phase에 분산 구현 → 단일 매핑 불가 | MED | 1 | 하나의 기능이 여러 Phase에 걸치면 "분산구현" 태그 + 모든 Phase 행번호 기재 | LOW |

## 4.4 전체 프로세스 약점

| # | 약점 | 위험도 | Phase | 방어 규칙 | 잔여 위험 |
|---|------|--------|-------|----------|----------|
| W-16 | CLAUDE.md 갱신일(2026-02-24)과 SRC/PART2 최종 갱신일 차이 | MED | 0-B,D | CLAUDE.md 이후 변경된 SRC 파일 식별 (v9 이후 SRC 변경 없으면 무시 가능) | LOW |
| W-17 | Feature Registry 자체의 완전성 보장 불가 | MED | 0-F | Layer 1 + Layer 2 + V8/V9 재검증의 3중 교차로 최대한 보완. 잔여 위험은 Phase 1.5 적대적 재검증에서 샘플 검사 | LOW |

## 4.5 추가 약점 — v10.1.0 보강분 (W-18~W-33)

### 추출/매핑 정확도

| # | 약점 | 위험도 | Phase | 방어 규칙 | 잔여 위험 |
|---|------|--------|-------|----------|----------|
| W-18 | version_scope "추론" 정확도 미보장 | HIGH | 0-C,D | confidence="추론" 항목을 Phase 0-D에서 별도 목록 추출 → PLAN-3.0 로드맵 + PART2 §2~§5 구조와 교차 대조하여 버전 확정. 확정 불가 항목은 **V_UNKNOWN** 태깅 → Phase 1에서 전 Phase 검색 | LOW |
| W-19 | "판단필요" 항목 대량 발생 시 사용자 병목 | MED | 0-D | 판단필요 항목에 "추천(기능/제외)" + "확신도(높음/중간/낮음)" 추가. **확신도 "높음"은 자동 반영**, "중간/낮음"만 사용자 판정 | LOW |
| W-20 | PLAN-2.0 SUPERSEDED 항목의 Registry 반영 기준 불명확 | MED | 0-C,F | SUPERSEDED 전용 기능 → part2_mapping_status = **NOT_APPLICABLE** 자동 태깅. Registry에는 포함하되 Phase 1 매핑 대상에서 제외 | LOW |
| W-21 | SRC↔PART2 용어 불일치로 매핑 실패 | HIGH | 0-B,1 | Phase 0-B에서 CLAUDE.md의 용어 매핑 테이블(SRC 용어 ↔ PART2 용어) 추출 → Phase 1 에이전트에 참조 제공 | LOW |
| W-22 | TITLE_ONLY + V2 CRITICAL 항목의 PART2 검증 불가 | MED | 0-C,1 | TITLE_ONLY이더라도 V2 CRITICAL 항목은 **제목 기반 PART2 키워드 매칭 시도**. 매칭 불가 시 "TITLE_ONLY_UNVERIFIABLE" 태그 → Phase 2 보고에 포함 | MED (본질적 한계) |

### 에이전트 운영

| # | 약점 | 위험도 | Phase | 방어 규칙 | 잔여 위험 |
|---|------|--------|-------|----------|----------|
| W-23 | 에이전트 "완료" 거짓 보고 (파일 미완독) | HIGH | 0-C | RULE-C1 강화: 읽기 완료율 보고에 **마지막 읽은 줄 내용 1줄 인용** 필수. 파일 끝부분과 대조 가능 | LOW |
| W-24 | 에이전트 간 JSON 키 이름 불일치 | MED | 0-C,D | Phase 0-D 프롬프트에 **JSON 키 정규화 STEP** 추가 (snake_case 통일, 오타 수정). 공통 템플릿 키와 불일치 시 경고 | LOW |
| W-25 | 에이전트 과부하 (C-1: 12,337줄, C-9: 9,032줄) | HIGH | 0-C | C-1 → C-1a(PLAN-3.0 단독) + C-1b(나머지 5개). C-9 → C-9a(A-E+F-I) + C-9b(J-M+N-P+보강). 대화 수 반영 | LOW |
| W-26 | Phase 0-D 대화 2회로 교차검증 부족 | MED | 0-D | Phase 0-D를 **3회**(Delta분석 + 병합 + 사용자판정)으로 확장 | LOW |
| W-27 | M-5 에이전트 §6-§7 전수 컨텍스트 초과 | MED | 1 | M-5를 **M-5a(§6.1~§6.7)** + **M-5b(§6.8~§6.13 + §7 + 통합보고)**로 분할 | LOW |

### 매핑/검증 프로세스

| # | 약점 | 위험도 | Phase | 방어 규칙 | 잔여 위험 |
|---|------|--------|-------|----------|----------|
| W-28 | 교차 버전 기능(V1,V2,V3) 중복 매핑 불일치 | MED | 1 | 다중 버전 기능의 **주 매핑 에이전트 규칙**: version_scope 첫 번째 버전 = 주 에이전트, 나머지 = 교차확인만 | LOW |
| W-29 | 적대적 재검증 20% 샘플링 비현실적 (대량 시) | MED | 1.5 | 샘플링 상한 설정: **최소 30건, 최대 60건** + **카테고리별 층화 샘플링** (FT-MOD, FT-UI 등에서 균등 추출) | LOW |
| W-30 | Phase 0-E GAP_FOUND 항목의 Registry 추가 방식 불명확 | MED | 0-E,F | 2가지 구분: (a) Registry에 없는 기능 → 새 feature_id 부여 (GAP-001~) (b) 기능은 있지만 Phase 배정 미확인 → 기존 feature의 part2_mapping_status = PRE_GAP | LOW |
| W-31 | 중복 탐지 시 feature_name만 의존 → 다른 표현 동일 기능 누락 | MED | 0-D | 중복 탐지 기준에 **모듈ID + 기술 키워드** 매칭 추가 (feature_name 의존도 낮추기) | LOW |
| W-32 | PART2 행번호 Phase 2 수정 후 변동 | MED | 2 | Phase 2 수정 전후 **행번호 매핑 테이블** 생성. Phase 1.5 참조 시 행번호+섹션ID 복합 참조 | LOW |
| W-33 | Phase 2 "v8 Phase 0 스크립트 재실행" 방법 미정의 | MED | 2 | v8 스크립트 재실행 대신 **"PART2 구조 검증 프롬프트"** 별도 정의: heading 계층 + 테이블 산술 + LOCK 유지 확인 | LOW |

---

# 5. Phase 0-A: 기능 항목 단위 정의 + 추출 템플릿

> **대화 0** | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase0-a\v10_feature_definition.md`

## 5.0 AI 프롬프트

```
당신은 VAMOS v10 Feature Coverage 검증의 Phase 0-A 에이전트입니다.

## 임무
v10 검증의 기초가 되는 "기능 항목(Feature Item)"의 정의, 추출 템플릿,
에이전트 공통 규칙을 확립합니다. 이 산출물이 이후 모든 Phase의 기준이 됩니다.

## 사전 확인
1. SRC 안정 경로 존재 확인: D:\VAMOS\docs\sot\ (43개 .md 파일)
2. PART2 존재 확인: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
3. v10_results 디렉토리 생성: D:\VAMOS\04. 구현단계\v10_results\phase0-a\

## 작업
1. 아래 §5.1 "기능 항목 정의"를 정리하여 v10_feature_definition.md에 기재
2. §5.2 "추출 템플릿" JSON 형식 확정
3. §5.3 "에이전트 실행 규칙" RULE-C1~C9 기재
4. 11개 카테고리(FT-MOD ~ FT-DOMAIN) 정의 + 판단 예시 각 2건 이상
5. "기능 vs 설명" 경계 판단 가이드라인 + 예시 5건

## 출력
v10_feature_definition.md (Phase 0-B~C의 모든 에이전트가 참조할 기준 문서)
```

## 5.1 기능 항목(Feature Item) 정의

```
하나의 Feature Item = PART2의 구현 Phase(V0 STEP 1~6, V1 Phase 1~6,
V2 Phase 1~3, V3 Phase 1~3)에 배정될 수 있는 최소 독립 구현 단위.

포함 대상:
  FT-MOD   모듈 구현         (I-1 Intent Detector 구현, E-7 STT 통합)
  FT-INFRA 인프라 구성       (Chroma→Qdrant 마이그레이션, K8s Helm)
  FT-UI    UI 화면/컴포넌트  (Builder View, 3-Panel, PWA 오프라인)
  FT-FUNC  기능 구현         (5-Phase 파이프라인, RBAC 4역할)
  FT-CFG   설정/정책         (config.v1.toml 13섹션, LOCK 값 적용)
  FT-TEST  테스트/검증       (E2E Playwright, Python 80% 커버리지)
  FT-MIG   마이그레이션      (SQLite→PostgreSQL, NetworkX→Neo4j)
  FT-API   API 엔드포인트    (Tauri IPC 72개, JSON-RPC 13개)
  FT-SCHEMA 스키마 구현      (25개 Pydantic 모델 코드 생성)
  FT-SEC   보안 구현         (Guardrails 4-Layer, PII 마스킹)
  FT-DOMAIN 도메인 기능      (AI Investing 51% Gate, SDAR 5-Layer)

제외 대상:
  - 설계 원칙, 철학, 방향성 서술 (예: "사용자 중심 설계를 지향")
  - LOCK 값 자체 (값 정합성은 V8에서 검증 완료)
  - 문서 간 용어 정의/약어 설명
  - STEP7 TITLE_ONLY 항목 → extractable=false 태깅만
  - PLAN-2.0 (SUPERSEDED) 내용
```

## 5.2 추출 템플릿 (모든 에이전트 공통)

```json
{
  "feature_id": "SRC약칭-NNN",
  "source_file": "D2.0-08",
  "source_line": 345,
  "source_section": "§7.3 모바일 UI",
  "feature_name": "React Native 네이티브 앱 (iOS/Android)",
  "version_scope": "V3",
  "category": "FT-UI",
  "implementation_type": "신규구현",
  "dependencies": ["IDEA-M05", "S7C-054"],
  "extractable": true,
  "confidence": "명시적|추론",
  "notes": "D2.0-08 §7.3에 V3 RESERVED로 명시"
}
```

**필드 설명**:

| 필드 | 필수 | 설명 |
|------|------|------|
| feature_id | Y | `SRC약칭-순번` (예: `D208-015`) |
| source_file | Y | SRC 파일 약칭 |
| source_line | Y | 기능이 정의된 행번호 (범위일 경우 시작-끝) |
| source_section | Y | SRC 파일 내 섹션 (§ 표기) |
| feature_name | Y | 기능 이름 (구현 관점에서 명확하게) |
| version_scope | Y | V0/V1/V2/V3 (복수 가능: "V1,V2,V3") |
| category | Y | FT-MOD/FT-INFRA/FT-UI/FT-FUNC/FT-CFG/FT-TEST/FT-MIG/FT-API/FT-SCHEMA/FT-SEC/FT-DOMAIN |
| implementation_type | Y | 신규구현/마이그레이션/설정/인프라/테스트/보강 |
| dependencies | N | 의존하는 다른 기능 ID 또는 모듈 ID |
| extractable | Y | true/false (TITLE_ONLY 등은 false) |
| confidence | Y | "명시적" (SRC에 직접 기재) / "추론" (문맥에서 도출) |
| notes | N | 보충 설명 |

## 5.3 에이전트 실행 규칙 (Phase 0-C 전 에이전트 공통)

```
RULE-C1: 할당된 SRC 파일을 전문(全文) 읽는다. 일부만 읽으면 반드시 보고.
         (읽은 줄 수 / 전체 줄 수, 미읽은 영역 명시)
         ★ 90% 미만 읽은 파일 → 파일 분할 재실행 필수.
         ★ 마지막으로 읽은 줄의 내용 1줄을 그대로 인용 (거짓 완료 보고 방지).
RULE-C2: 위 추출 템플릿에 따라 모든 구현 기능 항목을 추출한다.
RULE-C3: 각 기능에 version_scope를 반드시 태깅한다.
         - 명시적 태그가 있으면 confidence="명시적"
         - 문맥에서 추론하면 confidence="추론" + 근거 기재
         - 확정 불가능하면 version_scope="V_UNKNOWN" + 근거 기재
RULE-C4: STEP7 항목 중 TITLE_ONLY는 extractable=false로 태깅한다.
         - TITLE_ONLY 판정 기준: 제목만 있고 상세 설명/스펙이 없는 항목
         - V2 CRITICAL + TITLE_ONLY → 제목 기반 PART2 키워드 매칭 시도.
           매칭 불가 시 "TITLE_ONLY_UNVERIFIABLE" 태그
RULE-C5: 기능인지 설명인지 판단이 애매하면 일단 추출하고 notes에 "판단필요" 표시.
         + 추천(기능/제외) + 확신도(높음/중간/낮음) 함께 기재.
RULE-C6: 추출 완료 후 통계 보고 필수:
         - 총 추출 건수 (extractable=true / false 구분)
         - 카테고리별 분포
         - confidence="추론" 건수
         - version_scope="V_UNKNOWN" 건수
         - "판단필요" 건수 (확신도별)
         - 읽기 완료율
RULE-C7: 하나의 SRC 파일 내에서 같은 기능이 여러 곳에 언급되면 첫 출현만 추출.
         (단, 버전별로 다른 내용이면 별도 항목으로)
RULE-C8: SRC 경로는 반드시 D:\VAMOS\docs\sot\ 만 사용한다.
RULE-C9: 산출물 JSON 저장 후 파일 존재 확인(Read 1줄) 수행.
```

---

# 6. Phase 0-B: CLAUDE.md 기능 인덱스 추출 (Layer 1)

> **대화 1** | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase0-b\v10_layer1_claude_features.json`

## 입력

```
파일: CLAUDE.md
경로: D:\VAMOS\docs\sot\CLAUDE.md
줄 수: 697줄
```

## AI 프롬프트

```
당신은 VAMOS v10 Feature Coverage 검증의 Phase 0-B 에이전트입니다.

## 임무
CLAUDE.md 전문을 읽고, "Phase 0-A 기능 항목 정의"에 따라 모든 구현 기능 항목을 추출하세요.

## 입력 파일
- CLAUDE.md (697줄, 전문 읽기)
- v10_feature_definition.md (Phase 0-A 산출물 — 기능 정의 + 템플릿)

## 추출 대상 섹션별 가이드

| 섹션 | 추출 초점 |
|------|----------|
| §1 프로젝트 개요 | V0→V1→V2→V3 전환에 필요한 구현 항목 |
| §5 4계층 아키텍처 | 5-Phase, 5-Gate, 상태머신 구현 |
| §6 모듈 81개 | 모듈별 구현 (버전별 ON/OFF 기준) |
| §7 LOCK 결정사항 | LOCK이 요구하는 구현 (값 자체가 아닌 "이것을 구현해야 한다"는 항목) |
| §9 미해소 이슈 45건 | 이슈 해결에 필요한 구현 |
| §10 GO/NO-GO 62건 | 체크리스트가 요구하는 구현 |
| §11 기술 스택 | 버전별 기술 전환 구현 (예: Chroma→Qdrant) |
| §12 핵심 스키마 | 스키마 코드 생성 구현 |
| §13 API 계약 | API 엔드포인트 구현 (88개) |
| §14 프로젝트 구조 | 디렉토리/파일 스캐폴딩 |
| §15 메모리/저장 | L0~L3 구현 |
| §17 특화 시스템 | AI Investing + SDAR + Agent Teams 구현 |
| §19 V1 구현 순서 | 주차별 구현 대상 |
| §20 Config LOCK 값 | Config 파일 구현 |

## 출력 형식
Phase 0-A에서 정의한 JSON 템플릿 배열.
마지막에:
1. 통계 요약:
   - 총 추출 건수 (extractable=true / false)
   - 카테고리별 분포
   - 버전별 분포 (V0/V1/V2/V3)
2. **용어 매핑 테이블** (Phase 1 에이전트 참조용):
   - CLAUDE.md/SRC에서 사용하는 용어 ↔ PART2에서 사용하는 용어 대응표
   - 예: "IntentDetector" ↔ "의도 분석기", "EvidencePack" ↔ "증거 패킷"
   - 모듈 ID(I-1~I-25, E-1~E-16)의 PART2 내 표기 확인

## 절대 규칙
- CLAUDE.md를 전문 읽는다. 스킵 금지.
- "판단필요" 항목은 notes에 추천(기능/제외) + 확신도(높음/중간/낮음) 기재.
- LOCK 값 자체가 아닌 "구현 행위"를 추출.
  예: "비용 상한 ₩40,000" → 값이므로 제외.
  예: "비용 엔진 ₩40,000/월 하드코딩" → 구현 행위이므로 FT-FUNC로 추출.
- SRC 경로: D:\VAMOS\docs\sot\CLAUDE.md
```

---

# 7. Phase 0-C: 43개 SRC 전수 기능 추출 (Layer 2)

> **대화 2~13** (12회) | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase0-c\v10_src_C01a~C10.json`

## 에이전트 배정 매트릭스

> **에이전트 총 줄 수 상한: ~7,000줄/대화 (안전), ~5,000줄/대화 (권장)**

| 에이전트 | 대화 | SRC 파일 | 파일 수 | 합산 줄 수 | 추출 초점 |
|---------|------|---------|---------|-----------|----------|
| **C-1a** | 2 | PLAN-3.0 | 1 | 7,046 | V0→V1→V2→V3 로드맵 기능, 전환 조건, 기능 배치 |
| **C-1b** | 3 | BASE-1.3, MASTER_SPEC, READINESS_GUIDE, READINESS_REVIEW, V0_READINESS | 5 | 5,291 | 규칙 기반 구현, 이슈 해결, GO/NO-GO 요구 구현 |
| **C-2** | 4 | D2.0-01 (Overview), D2.0-02 (ORANGE CORE) | 2 | 6,331 | 모듈 정의, I-1~I-25 구현, 파이프라인, Gate, IntentFrame, EvidencePack |
| **C-3** | 5 | D2.0-03 (BLUE NODES), D2.0-04 (INFRA), D2.0-05 (Workflow) | 3 | 5,516 | E-모듈, MCP, 통신 프로토콜, LangGraph, Circuit Breaker |
| **C-4** | 6 | D2.0-06 (Storage/Memory), D2.0-07 (Safety/Cost) | 2 | 5,083 | L0~L3, RAG 6단계, Guardrails 4-Layer, RBAC, 비용 Gate |
| **C-5** | 7 | D2.0-08 (UI/UX), D2.1-D8 (UI Schema) | 2 | 2,897 | **UI 전수 — 모바일/PWA/위젯/크로스디바이스/AR 포함** |
| **C-6** | 8 | D2.1-A1, D2.1-D1~D7, D2.1-Q1 | 9 | 5,414 | 스키마 구현, 타입 동기화, 기술스택 |
| **C-7** | 9 | PHASE_B1~B7 | 7 | 9,751 | API 계약, 프로젝트 구조, 의존성, Config, 테스트, CI/CD, 마이그레이션. ⚠ 줄 수 과다 — 컨텍스트 초과 시 C-7a(B1~B3, 3,471줄) / C-7b(B4~B7, 6,280줄)로 분할. 분할 시 대화 1회 추가 |
| **C-8** | 10 | AI_INVESTING, CLOUD_LIBRARY, AGENT_TEAMS, SDAR_SPEC | 4 | 6,669 | 도메인별 기능 전수 |
| **C-9a** | 11 | STEP7_A-E, STEP7_F-I | 2 | 3,876 | STEP7 A~I 구현 기능 추출. TITLE_ONLY 태깅 필수 |
| **C-9b** | 12 | STEP7_J-M, STEP7_N-P, STEP7_보강 | 3 | 5,156 | STEP7 J~P+보강 구현 기능 추출. V2 CRITICAL TITLE_ONLY 제목 매칭 시도 |
| **C-10** | 13 | BEGINNER, CLAUDE.md(교차확인), PLAN-2.0(SUPERSEDED 확인) | 3 | 6,891 | 온보딩 기능 + PLAN-2.0 SUPERSEDED 확인. ⚠ PLAN-2.0은 스캔만 (신규 추출 없음) |

## 에이전트별 AI 프롬프트 (공통 구조)

각 에이전트(C-1a~C-10)에 아래 프롬프트 구조를 적용합니다:

```
당신은 VAMOS v10 Feature Coverage 검증의 Phase 0-C 에이전트 C-{N}입니다.

## 임무
할당된 SRC 파일을 전문 읽고, v10_feature_definition.md의 정의에 따라
모든 구현 기능 항목을 추출하세요.

## 입력 파일
{에이전트별 SRC 파일 목록 — 경로: D:\VAMOS\docs\sot\}

## 참조 파일
- v10_feature_definition.md (D:\VAMOS\04. 구현단계\v10_results\phase0-a\)
- ⚠ v10_layer1_claude_features.json은 참조하지 않는다 (독립성 확보).
  Layer 1과의 비교는 Phase 0-D에서만 수행한다.

## 추출 규칙
RULE-C1~C7 (§5.3 참조) 전수 적용.

## 특별 주의사항
{에이전트별 특별 지시}

## 출력
1. 기능 항목 JSON 배열
2. 통계 요약 (총 건수, 카테고리별, 버전별, 추론 건수, 판단필요 건수)
3. 읽기 완료 보고 (파일별: 읽은 줄 / 전체 줄, 미읽은 영역)
```

### 에이전트별 특별 지시

**C-1a** (PLAN-3.0 단독 — 7,046줄):
```
- V0→V1→V2→V3 전환 시 필요한 구현 항목을 version_scope별로 추출
- 각 Phase(V0 STEP1~6, V1 Phase1~6, V2 Phase1~3, V3 Phase1~3)에 배정된 기능 식별
- 로드맵 전환 조건(entry/exit criteria)에서 구현 행위 추출
- 기능 중복 주의: DESIGN 2.0과 겹치는 내용은 PLAN-3.0 고유 정보만 추출
```

**C-1b** (BASE, MASTER, READINESS 3개):
```
- BASE-1.3에서 구현 규칙이 요구하는 기능 항목 추출
- MASTER_SPEC에서 시스템 전체 구현 항목 추출
- READINESS_GUIDE의 45개 이슈에서 구현 행위가 필요한 항목만 추출
- GO/NO-GO 62건 중 구현 행위를 요구하는 항목 추출 (확인/검증만 하는 항목은 제외)
- V0_READINESS에서 V0 진입 전 필수 구현 항목 추출
- READINESS_REVIEW에서 준비성 결함 → 구현 필요 항목 추출
```

**C-2** (D2.0-01, D2.0-02):
```
- I-1~I-25 각 모듈의 구현 기능 추출 (ON/OFF 매트릭스 기반 버전별)
- 5-Phase 파이프라인 구현 항목
- 5-Gate 각각의 구현 항목
- 9-State Machine 구현
- IntentFrame, EvidencePack, Decision 구현
- V0 stub vs V1 full 구현 구분
```

**C-3** (D2.0-03, D2.0-04, D2.0-05):
```
- E-1~E-16 외부 모듈 구현 (버전별 ON/OFF)
- MCP 7개 컴포넌트 구현
- JSON-RPC 통신 구현
- LangGraph StateGraph 구현
- Circuit Breaker 구현
- IPC 아키텍처 구현
```

**C-4** (D2.0-06, D2.0-07):
```
- L0~L3 메모리 계층 각각의 구현
- RAG 6단계 파이프라인 구현
- Semantic Cache 구현
- Guardrails 4-Layer 구현 (버전별)
- RBAC 4역할 구현
- 비용 Gate 구현 (80%/100%)
- NEVER_AUTO 10항목 구현
```

**C-5** (D2.0-08, D2.1-D8) — **핵심 에이전트**:
```
- ★ 모바일 네이티브 앱 (React Native/Flutter) 관련 항목 전수 추출
- ★ PWA 오프라인 지원 관련 항목 전수 추출
- ★ 크로스 디바이스 동기화 관련 항목 전수 추출
- ★ AR (ARKit/ARCore) 관련 항목 전수 추출
- ★ 위젯/CLI 인터페이스 관련 항목 전수 추출
- V2/V3 UI 진화 항목 누락 없이 추출
- Builder/Hologram View, 3-Panel, ~44 컴포넌트, 8 Hook, 7 Store
- RESERVED 슬롯, IDEA 항목도 추출 (extractable 여부 판단)
- S7C, S7D, J-시리즈 항목 ID가 있으면 전수 추출
```

**C-6** (D2.1-A1, D2.1-D1~D7, D2.1-Q1):
```
- 25개 Pydantic 모델 코드 생성 구현
- Pydantic→Zod→serde 타입 동기화 구현
- 기술 스택 버전별 전환 구현 (A1에서)
- 스키마 v3.0.0 통일 승격 구현
```

**C-7** (PHASE_B1~B7):
```
- API 88개 엔드포인트 구현 (B1)
- 모노레포 디렉토리 생성 (B2)
- 의존성 설치 (B3)
- Config 13섹션 구현 (B4)
- 테스트 전략 구현 (B5)
- CI/CD 14개 워크플로우 구현 (B6)
- 마이그레이션 전략 구현 (B7)
```

**C-8** (AI_INVESTING, CLOUD_LIBRARY, AGENT_TEAMS, SDAR):
```
- AI Investing: 51% Gate, 5-Agent, 83 데이터소스, Paper Trading
- Cloud Library: 10-Layer, RT-BNP, DCL, G0-G4
- Agent Teams: LOCK-AT 17항목, 5 협업패턴, 위임 깊이 3
- SDAR: 5-Layer, AR-L0~L4, Kill Switch, CATEGORY E, NEVER_AUTO
```

**C-9a** (STEP7_A-E + STEP7_F-I — 3,876줄):
```
- STEP7 카테고리 A~I 항목을 전수 스캔
- 각 항목의 상태 분류:
  (a) 상세 스펙 있음 → extractable=true, 기능 항목 추출
  (b) TITLE_ONLY → extractable=false, 건수만 카운트
  (c) V2 CRITICAL → 별도 목록으로 표시 (우선순위 HIGH)
- 카테고리(A~I)별 추출 건수 보고
```

**C-9b** (STEP7_J-M + STEP7_N-P + STEP7_보강 — 5,156줄):
```
- STEP7 카테고리 J~P + 보강 항목을 전수 스캔
- 상태 분류 기준 C-9a와 동일
- V2 CRITICAL + TITLE_ONLY 항목은 제목 기반 PART2 키워드 매칭 시도
  → 매칭 불가 시 "TITLE_ONLY_UNVERIFIABLE" 태그
- 카테고리(J~P+보강)별 추출 건수 보고
- C-9a 결과와의 합산 통계 산출
```

**C-10** (BEGINNER, CLAUDE.md, PLAN-2.0 — 6,891줄):
```
- BEGINNER_GUIDE에서 온보딩 구현 항목 추출
- CLAUDE.md를 독립적으로 읽어 SRC 관점 기능 추출 (Phase 0-B와 비교는 Phase 0-D에서)
- PLAN-2.0: SUPERSEDED 확인. 새로운 기능 추출 없음. 단, PLAN-3.0에 없고
  PLAN-2.0에만 있는 기능이 있다면 "SUPERSEDED 기능" 태그로 보고
  → SUPERSEDED 기능은 part2_mapping_status = NOT_APPLICABLE 자동 태깅
- ⚠ PLAN-2.0(4,350줄)은 전문 읽기 필수가 아님. 목차+주요 섹션 스캔으로 충분.
```

### 읽기 완료 보고 형식 (각 에이전트 산출물 말미에 포함)

```markdown
## 읽기 완료 보고

| 파일 | 전체 줄 | 읽은 줄 | 완료율 | 미읽은 영역 | 마지막 줄 인용 |
|------|---------|---------|--------|------------|--------------|
| D2.0-08 | 2,696 | 2,696 | 100% | — | "..." (실제 마지막 줄) |
| D2.1-D8 | 201 | 201 | 100% | — | "..." (실제 마지막 줄) |

추출 건수: N건 (extractable=true: M건, false: K건)
```

### v10_src_coverage_report.md 취합 규칙

```
작성 주체: Phase 0-D 대화 14(Delta-1)에서 에이전트가 12개 JSON 파일의
           읽기 완료 보고를 취합하여 v10_src_coverage_report.md를 생성한다.
취합 내용:
- 12개 에이전트 × 43개 파일의 읽기 완료율 매트릭스
- 90% 미만 파일 목록 (있으면 Phase 0-C 보충 실행 필요 → 진행 중단)
- 전체 평균 완료율
```

---

# 8. Phase 0-D: CLAUDE.md ↔ SRC 교차 검증 (Delta)

> **대화 14~16** (3회) | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase0-d\`

## 선행 확인
```
Phase 0-D 시작 전 필수 확인:
□ v10_layer1_claude_features.json 존재 확인 (Phase 0-B)
□ v10_src_C01a ~ C10.json 12개 파일 전수 존재 확인 (Phase 0-C)
□ v10_src_coverage_report.md에서 읽기 완료율 90% 미만 파일 = 0개 확인
```

## 입력

```
- v10_layer1_claude_features.json  (Phase 0-B 결과)
- v10_src_C01a~C10.json            (Phase 0-C 결과 12개)
- v10_src_coverage_report.md       (Phase 0-C 읽기 완료율)
```

## AI 프롬프트

```
당신은 VAMOS v10 Phase 0-D 교차 검증 에이전트입니다.

## 임무
Layer 1(CLAUDE.md)과 Layer 2(SRC 43개)의 기능 추출 결과를 교차 비교하여:
1. 누락 후보 식별
2. 중복 병합
3. 판단 필요 항목 정리
4. 최종 병합 목록 생성

## 입력 파일
- v10_layer1_claude_features.json (D:\VAMOS\04. 구현단계\v10_results\phase0-b\)
- v10_src_C01a~C10.json 12개 (D:\VAMOS\04. 구현단계\v10_results\phase0-c\)

## 대화 분할 (3회)
- **대화 14**: STEP 0(JSON 정규화) + STEP 1~2 (Delta 분석)
- **대화 15**: STEP 3 + STEP 5(V_UNKNOWN 확정) + STEP 6(중복 병합)
- **대화 16**: STEP 4(판단필요 정리) → 사용자 판정 대기

## 검증 작업

### STEP 0: JSON 키 정규화 (W-24 방어)
- 12개 에이전트 JSON 파일의 키 이름 통일 확인 (snake_case)
- 공통 템플릿 키와 불일치 시 자동 수정 + 경고 보고
- 필수 필드 누락 항목 보고

### STEP 1: Layer 1에만 있고 Layer 2에 없는 항목
- CLAUDE.md에서 추출했지만 43개 SRC 어디에서도 추출되지 않은 기능
- → "SRC 추출 누락 후보" 목록 생성
- → 해당 SRC 파일을 특정하여 재확인 요청 여부 판단
- → CLAUDE.md 요약 과정에서 생긴 "축약 기능"이면 제외

### STEP 2: Layer 2에만 있고 Layer 1에 없는 항목
- SRC에서 추출했지만 CLAUDE.md에 없는 기능
- → 정상 (SRC가 더 상세하므로)
- → 단, LOCK 관련 항목이면 "CLAUDE.md 미기재" 플래그

### STEP 3: 양쪽에 있지만 version_scope가 다른 항목
- → PLAN-3.0 로드맵 기준으로 정답 버전 확정
- → 오류 쪽의 version_scope 수정

### STEP 4: "판단필요" 태그 항목 정리 (→ 대화 16에서 사용자 판정)
- Phase 0-C에서 "판단필요"로 태깅된 항목 전수 목록
- → 각각에 대해 "기능/제외" 추천 + 근거 + 확신도(높음/중간/낮음)
- → **확신도 "높음" 항목은 자동 반영** (사용자 판정 불필요)
- → **확신도 "중간/낮음" 항목만 사용자 최종 판정 대기**

### STEP 5: V_UNKNOWN 버전 확정 (W-18 방어)
- version_scope="V_UNKNOWN" 항목 전수 목록
- → PLAN-3.0 로드맵 + PART2 §2~§5 구조와 대조하여 버전 확정
- → 확정 불가 시 V_UNKNOWN 유지 → Phase 1에서 전 Phase(§2~§7) 검색

### STEP 6: 중복 병합
- feature_name + version_scope + category + **모듈ID + 기술키워드** 복합 매칭 (W-31 방어)
- 동일 기능이 여러 SRC에서 추출된 경우 → 가장 상세한 버전을 주(primary)로, 나머지는 cross_ref로 연결
- 병합 결과: v10_merged_features.json

## 출력
1. v10_layer1_layer2_delta.json: STEP 1~3 결과
2. v10_merged_features.json: STEP 6 결과 (중복 제거된 전체 기능 목록)
3. 사용자 판정 필요 목록 (STEP 4)
4. V_UNKNOWN 확정/잔여 목록 (STEP 5)
4. 통계: 총 기능 수, Layer 1 only, Layer 2 only, 양쪽 일치, 중복 병합 수
```

---

# 9. Phase 0-E: V8/V9 산출물 1:1 재검증

> **대화 17~18** | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase0-e\`

## 선행 확인
```
Phase 0-E 시작 전 필수 확인:
□ v10_merged_features.json 존재 확인 (Phase 0-D)
□ 사용자 Phase 0-D 판정 완료 확인
□ V8 산출물 경로 존재: D:\VAMOS\04. 구현단계\v8_results\phase0\IMP-*.json
□ V9 산출물 경로 존재: D:\VAMOS\04. 구현단계\v9_results\
```

## 입력

```
- v10_merged_features.json (Phase 0-D 결과)
- V8/V9 산출물 (§2.3 경로 참조)
```

## AI 프롬프트 (대화 17: V8 재검증)

```
당신은 VAMOS v10 Phase 0-E V8 재검증 에이전트입니다.

## 임무
V8의 주요 산출물이 "완료"라고 판정한 영역을, Phase 0-D의 독립 추출 결과와
1:1 대조하여 실제 커버 범위를 확인합니다.

## V8/V9 산출물은 "참고"입니다. 신뢰하지 않습니다.

## 재검증 대상

### 1. IMP-E 모듈 활성 매트릭스
- 파일: D:\VAMOS\04. 구현단계\v8_results\phase0\IMP-E.json
- V8 판정: "V0=5, V1=32, V2=42, V3=81 행합/열합 PASS"
- V10 질문:
  Q1: 81개 모듈 각각이 v10_merged_features.json에서 기능 항목으로 추출되었는가?
  Q2: V3 전용 39개 모듈(81-42)은 PART2 V3-Phase 1/2/3 중 어디에 배정되어야 하는가?
  Q3: IMP-E는 "모듈 수 매칭"이지 "Phase 배정 확인"은 아닌데 — Phase 배정이 실제로 되어 있는가?
  → Q3의 답이 "미확인"이면 GAP_FOUND

### 2. IMP-C API 엔드포인트
- 파일: D:\VAMOS\04. 구현단계\v8_results\phase0\IMP-C.json
- V8 판정: "88개 매칭 완료"
- V10 질문:
  Q1: 88개 API가 v10_merged_features에서 FT-API 카테고리로 추출되었는가?
  Q2: 각 API의 PART2 Phase 배정이 되어 있는가?

### 3. IMP-B 스키마 필드 수
- 파일: D:\VAMOS\04. 구현단계\v8_results\phase0\IMP-B.json
- V10 질문: 25개 스키마의 "코드 생성" 구현이 PART2 Phase에 배정되어 있는가?

### 4. IMP-D Config 키
- 파일: D:\VAMOS\04. 구현단계\v8_results\phase0\IMP-D.json
- V10 질문: Config 13섹션의 "구현" 작업이 PART2 Phase에 배정되어 있는가?

### 5. V8 Agent 7 (UI/UX) 결과
- 파일: D:\VAMOS\04. 구현단계\v8_results\phase1\대화07_agent07.md
- V10 질문:
  Q1: Agent 7이 D2.0-08을 읽었을 때 "모바일/PWA/위젯/AR" 기능을 발견했는가?
  Q2: 발견했다면 PART2 매핑을 확인했는가?
  Q3: Phase 0-C C-5의 추출 결과와 비교하여 차이가 있는가?

## 출력
각 산출물별: 재검증_결과(CONFIRMED / GAP_FOUND), 발견된_갭_목록
→ v10_v8_revalidation.json
```

## AI 프롬프트 (대화 18: V9 재검증)

```
당신은 VAMOS v10 Phase 0-E V9 재검증 에이전트입니다.

## 임무
V9의 산출물을 v10_merged_features.json과 1:1 대조합니다.

## 재검증 대상

### 1. V9 SOT 매핑 (v9_sot_mapping.json)
- 파일: D:\VAMOS\04. 구현단계\v9_results\phase-1\v9_sot_mapping.json
- V10 질문:
  Q1: 43개 파일 전수 매핑이 맞는가? (Phase 0-C에서 읽은 파일과 1:1 대조)
  Q2: part2_references 수(488건)와 v10의 기능 항목 수 간 상관 확인
  Q3: references가 0건인 SRC 파일이 있는가? → 있으면 PART2에 해당 파일 내용이 미반영

### 2. V9 GT-1 파일 경로 레지스트리
- 파일: D:\VAMOS\04. 구현단계\v9_results\phase0\gt1_file_path_registry.json
- V10 질문: V9가 검증한 "파일 경로 정합성"과 v10의 "기능 항목 존재 여부"는 다른 관점. 확인만.

### 3. V9 Phase 1 최종 보고
- 파일: D:\VAMOS\04. 구현단계\v9_results\phase1\phase1_final_report.md
- V10 질문: 877 checks에서 "Feature Coverage" 관련 체크가 있었는가? → 없었으면 GAP_FOUND

### 4. PART2 버전 확인
- V8 대상: v18.0.0
- V9 대상: v20.4.0 → v21.0.0
- V10 대상: v21.0.0
- V10 질문: v18→v21 사이 changelog에서 추가/삭제된 구현 항목 식별

## 출력
→ v10_v9_revalidation.json + v10_revalidation_report.md
```

---

# 10. Phase 0-F: 최종 Feature Registry 확정

> **대화 19** | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json`

## 입력

```
- v10_merged_features.json (Phase 0-D)
- v10_v8_revalidation.json (Phase 0-E)
- v10_v9_revalidation.json (Phase 0-E)
- 사용자 판정 결과 (Phase 0-D STEP 4)
```

## AI 프롬프트

```
당신은 VAMOS v10 Phase 0-F Feature Registry 확정 에이전트입니다.

## 임무
Phase 0-B~E의 모든 결과를 통합하여 최종 Feature Registry를 확정합니다.
이 Registry가 Phase 1의 유일한 입력이 됩니다.

## 작업

### STEP 1: 통합
- v10_merged_features.json의 모든 기능 항목
- + Phase 0-E에서 발견된 GAP_FOUND 항목 추가:
  - **(a) Registry에 아예 없는 기능** → 새 feature_id 부여 (GAP-001~)
  - **(b) 기능은 있지만 Phase 배정 미확인** → 기존 feature의 part2_mapping_status = PRE_GAP
- + 사용자 판정 결과 반영 ("제외" 판정된 항목 삭제)
- + SUPERSEDED 기능 → NOT_APPLICABLE 자동 태깅

### STEP 2: 매핑 초기 상태 부여
각 기능 항목에 part2_mapping_status 추가:
- UNKNOWN: 아직 PART2 매핑 확인 안 됨 (Phase 1에서 확인)
- PRE_MATCHED: V8/V9에서 커버 확인 + Phase 0-E에서 재확인 완료
- PRE_GAP: V8/V9에서 커버했다고 했지만 Phase 0-E에서 갭 발견
- NOT_APPLICABLE: PLAN-2.0 SUPERSEDED 등 PART2 반영 불필요

### STEP 3: 통계 산출
- 총 기능 항목 수
- extractable=true / false 구분
- 버전별 분포: V0 / V1 / V2 / V3
- 카테고리별 분포: FT-MOD / FT-UI / ...
- 매핑 초기 상태: UNKNOWN / PRE_MATCHED / PRE_GAP / NOT_APPLICABLE
- confidence="추론" 비율

### STEP 4: 사용자 승인
- 통계 요약을 사용자에게 제시
- Feature Registry 승인 요청
- 승인 후 Phase 1 진행

## 출력
v10_feature_registry_final.json
```

**Feature Registry 스키마**:
```json
{
  "_meta": {
    "version": "v10.1.0",
    "generated": "2026-03-XX",
    "total_features": 0,
    "extractable_true": 0,
    "extractable_false": 0,
    "by_version": {"V0": 0, "V1": 0, "V2": 0, "V3": 0},
    "by_category": {"FT-MOD": 0, "FT-UI": 0},
    "by_mapping_status": {"UNKNOWN": 0, "PRE_MATCHED": 0, "PRE_GAP": 0}
  },
  "features": [
    {
      "feature_id": "D208-015",
      "source_file": "D2.0-08",
      "source_line": 345,
      "source_section": "§7.3",
      "feature_name": "React Native 네이티브 앱",
      "version_scope": "V3",
      "category": "FT-UI",
      "implementation_type": "신규구현",
      "extractable": true,
      "confidence": "명시적",
      "part2_mapping_status": "UNKNOWN",
      "part2_phase": null,
      "part2_line": null,
      "cross_refs": ["CLAUDE-081", "STEP7-J009"],
      "notes": ""
    }
  ]
}
```

---

# 11. Phase 1: Feature → PART2 매핑 검증

> **대화 20~25** | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase1\`

## 선행 확인
```
□ v10_feature_registry_final.json 존재 확인
□ 사용자 Phase 0-F 승인 완료 확인
□ PART2 파일 존재 확인: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md
□ Phase 0-B 용어 매핑 테이블 참조 준비
```

## 입력

```
- v10_feature_registry_final.json (Phase 0-F)
- PART2: D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md (v21.0.0)
- v10_layer1_claude_features.json 내 용어 매핑 테이블 (Phase 0-B)
```

## 교차 버전 기능 규칙 (W-28 방어)

```
다중 버전 기능 (예: version_scope="V1,V2,V3")의 주 매핑 에이전트:
→ version_scope의 첫 번째 버전이 주 매핑 에이전트
→ 나머지 에이전트는 "교차확인만" (주 매핑 결과 참조)
예: "V1,V2,V3" → M-2가 주 매핑, M-3/M-4는 교차확인
→ V_UNKNOWN 항목은 M-5b가 전 Phase(§2~§7) 검색
```

## 에이전트 배정

| 에이전트 | 대화 | 검증 범위 | Feature Registry 필터 |
|---------|------|----------|---------------------|
| **M-1** | 20 | V0 기능 → PART2 §2 (V0 STEP 1~6) | version_scope contains "V0" |
| **M-2** | 21 | V1 기능 → PART2 §3 (V1 Phase 1~6) | version_scope contains "V1" |
| **M-3** | 22 | V2 기능 → PART2 §4 (V2 Phase 1~3) | version_scope contains "V2" |
| **M-4** | 23 | V3 기능 → PART2 §5 (V3 Phase 1~3) | version_scope contains "V3" |
| **M-5a** | 24 | §6.1~§6.7 시스템별 상세 | 전체 (§6 전반부 커버) |
| **M-5b** | 25 | §6.8~§6.13 + §7 GO/NO-GO + V_UNKNOWN + 통합 보고 | 전체 (§6 후반부 + §7 + 통합) |

## 에이전트 공통 AI 프롬프트

```
당신은 VAMOS v10 Phase 1 매핑 검증 에이전트 M-{N}입니다.

## 임무
Feature Registry에서 {버전} 기능 항목을 PART2 {섹션}에 1:1 매핑합니다.

## 입력
- v10_feature_registry_final.json (D:\VAMOS\04. 구현단계\v10_results\phase0-f\)
  → version_scope에 "{버전}"이 포함된 항목만 필터
- PART2 (D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md)
  → {해당 섹션} 전문 읽기

## 매핑 규칙

### 판정 기준
- MATCHED: PART2에 해당 기능의 구현 항목이 명시적으로 존재
  → part2_phase, part2_line 기재
- PARTIAL: PART2에 관련 내용이 있으나 구현 항목으로 배정되지 않음 (§6에만 존재 등)
  → 어디에 있는지 기재 + "Phase 미배정" 표시
- MISSING: PART2 어디에서도 찾을 수 없음
  → 심각도 판정 (BLOCKER / HIGH / MEDIUM / LOW)
- SPREAD: 여러 Phase에 분산 구현
  → 모든 Phase와 행번호 기재
- NOT_APPLICABLE: PART2 반영 불필요 (SUPERSEDED, 설계 원칙 등)

### 심각도 기준
- BLOCKER: V{버전} 구현에 필수인데 PART2에 완전히 없음
- HIGH: 중요 기능이 Phase에 미배정 (§6에만 있고 §2-5에 없음)
- MEDIUM: 세부 기능 누락 (상위 기능은 있으나 하위 항목 부재)
- LOW: 부가 기능 누락 (핵심 경로에 영향 없음)

### 검색 방법
1. feature_name으로 PART2 내 키워드 검색
2. 모듈 ID (I-1, E-7 등)로 검색
3. 기술명 (React Native, Qdrant 등)으로 검색
4. source_section의 SRC 참조명 (D2.0-08 §7.3 등)으로 검색
5. 위 4가지 모두 실패하면 MISSING 판정 (추측 금지)

### 절대 규칙
- "상식적으로 포함되어 있을 것" = 금지. 명시적 증거만.
- PART2 **행번호 + 섹션ID** 반드시 기재 (행번호 변동 대비).
- PRE_MATCHED 항목도 재확인 필수 (V8/V9를 신뢰하지 않음).
- 용어 매핑 테이블(Phase 0-B 산출물)을 참조하여 SRC↔PART2 용어 불일치 해소.

## 출력
1. 매핑 결과 JSON: 각 feature_id별 판정 + PART2 행번호
2. 통계: MATCHED / PARTIAL / MISSING / SPREAD / NOT_APPLICABLE 건수
3. MISSING 항목 심각도별 분류 목록
```

### M-5a 에이전트 특별 지시 (§6.1~§6.7)

```
M-5a는 §6 전반부(§6.1~§6.7)를 전수 커버합니다.

## 추가 입력 (M-1~M-4 완료 후)
- v10_mapping_M01_v0.json ~ M04_v3.json (MISSING 항목 목록 참조)

임무:
1. §6.1~§6.7에 있지만 §2-§5 Phase에는 없는 기능 항목 식별
   → PARTIAL 판정 + "§6 only, Phase 미배정"
2. M-1~M-4의 MISSING 항목이 혹시 §6.1~§6.7에 있는지 재확인
3. V_UNKNOWN 항목 중 §6.1~§6.7에서 발견되는 항목 버전 확정 시도
```

### M-5b 에이전트 특별 지시 (§6.8~§6.13 + §7 + 통합)

```
M-5b는 §6 후반부(§6.8~§6.13)와 §7 GO/NO-GO를 전수 커버하고
Phase 1 전체 통합 보고서를 작성합니다.

## 추가 입력
- v10_mapping_M01~M04.json (MISSING 항목 목록 참조)
- v10_mapping_M05a_sys_front.json (M-5a 결과)

임무:
1. §6.8~§6.13에 있지만 §2-§5 Phase에는 없는 기능 항목 식별
2. §7 GO/NO-GO 62건이 Feature Registry의 어떤 항목에 대응하는지 매핑
3. M-1~M-4의 MISSING 항목이 혹시 §6.8~§6.13에 있는지 재확인
4. §6.13 작업량 요약 매트릭스의 수치와 Feature Registry 건수 비교
5. V_UNKNOWN 잔여 항목 최종 검색
6. M-1~M-4 + M-5a + M-5b 결과 통합 → 전체 통합 보고서 (v10_phase1_report.md)
```

---

# 12. Phase 1.5: 적대적 재검증

> **대화 26** | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase15\v10_adversarial_report.md`

## AI 프롬프트

```
당신은 VAMOS v10 Phase 1.5 적대적 재검증 에이전트입니다.

## 임무
Phase 1의 M-1~M-4, M-5a, M-5b 판정 결과에 대해 오판(FP/FN)이 없는지 감사합니다.

## 입력
- v10_mapping_M01~M04.json + M05a + M05b (D:\VAMOS\04. 구현단계\v10_results\phase1\)
- PART2 (D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md)
- v10_feature_registry_final.json (D:\VAMOS\04. 구현단계\v10_results\phase0-f\)

## 감사 방법

### A: MATCHED → 실제 MISSING? (False Positive 검사)
- MATCHED 판정 중 **카테고리별 층화 샘플링** (FT-MOD, FT-UI 등에서 균등 추출)
- 샘플 수: **최소 30건, 최대 60건** (MATCHED 총 수 대비 적정 비율)
- 해당 PART2 행번호+섹션ID를 직접 읽어 실제로 구현 항목이 있는지 확인
- "값이 언급된 것"과 "구현 항목으로 배정된 것"을 구분

### B: MISSING → 실제 MATCHED? (False Negative 검사)
- MISSING 판정 전수 재확인
- 각 MISSING 항목에 대해 PART2 전문 검색 재시도
  (다른 표현, 약칭, 상위 항목 포함 여부)
- 재검색 후에도 못 찾으면 REAL_MISSING 확정

### C: PARTIAL 항목 재분류
- PARTIAL 판정 전수 재확인
- §6에만 있고 Phase에 없는 항목 → MISSING(HIGH)인지 의도적인지 판단

## 출력
- FALSE_POSITIVE 목록 (MATCHED → MISSING으로 변경)
- FALSE_NEGATIVE 목록 (MISSING → MATCHED로 변경)
- REAL_MISSING 확정 목록 (심각도별)
- 최종 통계
```

---

# 13. Phase 2: 누락 항목 반영 + 재검증

> **대화 27~29** | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\phase2\`

## 대화 27: 누락 항목 목록 확정 + 반영 계획

```
## 입력
- v10_adversarial_report.md (Phase 1.5)
- REAL_MISSING 확정 목록

## 작업
1. REAL_MISSING 항목을 심각도별 정렬
2. 각 항목이 PART2 어느 Phase에 배정되어야 하는지 제안
3. Ripple Map 작성 (아래 형식)
4. 사용자 확인 후 Phase 2 수정 진행 결정

## Ripple Map 형식 (W-33 방어)
{
  "ripple_map": [
    {
      "added_item": "feature_id",
      "target_section": "§5.2 V3 Phase 2",
      "target_line": 2850,
      "affected_sections": [
        {"section": "§6.8 UI/UX", "impact_type": "수량 갱신", "detail": "컴포넌트 수 +3"},
        {"section": "§6.13 작업량 매트릭스", "impact_type": "행 추가", "detail": "V3-P2 행합 변경"},
        {"section": "§7 GO/NO-GO", "impact_type": "체크항목 추가", "detail": "#63 추가 가능"}
      ]
    }
  ]
}

## 산출물
- v10_missing_items_list.md
- v10_part2_patch_plan.md (Ripple Map 포함)
```

## 대화 28: PART2 수정

```
## 입력
- v10_part2_patch_plan.md
- PART2 v21.0.0

## 작업
- 승인된 누락 항목을 PART2에 반영
- Ripple Map에 따른 연쇄 수정
- 버전업 (v21.0.0 → v22.0.0)
- Changelog 추가
- 수정 전후 행번호 매핑 테이블 생성 (W-32 방어)
```

## 대화 29: Step 1/2 분류 결과 (2026-03-10 완료)

> **실행 시점**: 대화 28 PART2 v22.0.0 수정 이후
> **목적**: 잔여 1,058건(1,068 - 10 RESOLVED)의 정밀 분류로 실질 PART2 반영 대상 확정
> **방법**: 5차 재검토 (SOT 대조, STEP7 작업가이드 대조, 아키텍처 근거 확보)

### Step 1 결과: 확정 분류 (67건 제외)

| # | 분류 | 건수 | 설명 | 산출물 |
|---|------|------|------|--------|
| 3-1 | NOT_APPLICABLE | 0 | 4차 재검토에서 전수 Step 2 이동 | `step1/3-1_NOT_APPLICABLE.md` |
| 3-2 | SUB_FEATURE_OF_EXISTING | 45 | PART2 상위 모듈에 종속 (아키텍처 근거 확보, HIGH 27+MEDIUM 18) | `step1/3-2_SUB_FEATURE_OF_EXISTING.md` |
| 3-3 | SKIP_CONFIRMED | 10 | PART2에서 100% 커버 확인 (2차 재검토 완료) | `step1/3-3_SKIP_CONFIRMED.md` |
| 3-4 | RESOLVED | 10 | 대화 28 PART2 v22.0.0 반영 완료 (BLOCKER 3+HIGH 7) | `step1/3-4_RESOLVED.md` |
| 3-5 | SECTION6_DETAILED | 1 | §6 상세 구현 가이드 존재 확인 (CLIB-023) | `step1/3-5_SECTION6_DETAILED.md` |
| 3-6 | DUPLICATE | 1 | 의미적 중복 (D207-108 ↔ AINV-056) | `step1/3-6_DUPLICATE.md` |
| | **합계** | **67** | | |

### Step 2 잔여: 1,001건

| 구분 | 건수 |
|------|------|
| 원본 REAL_MISSING | 1,068 |
| Step 1 제외 | -67 |
| **Step 2 잔여** | **1,001** |

### 1,001건 PART2 적용 판정

> **핵심 결론**: Step 1/2 분류 결과, PART2에 대한 **추가 수정은 불필요**.
> 대화 28의 10건 RESOLVED가 유일한 PART2 변경이며, 잔여 1,001건은 아래 사유로 PART2 변경 없음.

| 대상 | 건수 | 처리 방침 | PART2 영향 | 근거 |
|------|------|----------|------------|------|
| STEP7 TITLE_ONLY | ~140 | NOT_APPLICABLE 확정 | 변경 없음 | 제목만 존재, 구현 스펙 없음 |
| STEP7 실질 항목 | ~480 | MISSING_CONFIRMED (§6 참조 유지) | 변경 없음 | §6 상세 구현 가이드에 이미 존재 |
| HIGH PRIMARY 비-STEP7 잔여 | ~98 | COVERED_BY_UPPER_MODULE | 변경 없음 | §6 상위 모듈에서 커버 |
| SUB_FEATURE 제외 후 잔여 | ~45→0 | Step 1에서 제외 완료 | — | 상위 모듈 종속 |
| MEDIUM/LOW/CROSSCHECK | ~283 | SKIP 또는 PARTIAL 유지 | 변경 없음 | 다른 버전/모듈에서 커버 |

### PART2 v22.0.0 최종 수정 내역 요약

대화 28에서 적용된 10건이 PART2 유일한 변경:

| Patch | 적용 항목 | PART2 위치 |
|-------|----------|-----------|
| PATCH-B01 | D202-130, D205-067 (PARL Agent Swarm) | §5.2 행 15-16 + §6.7 PARL 상세 |
| PATCH-B02 | D205-076 (Agent Specialization) | §5.3 행 9 + §6.7 Specialization 상세 |
| PATCH-H02 | P30-009, P30-029, P30-058, P30-061, CLAUDE-108 | §3 I-5/I-8/I-9 하위 체크리스트 |
| PATCH-H05 | DA1-016, DA1-019 (AI Investing 고급) | §5.3 행 10 |

산출물 경로: `D:\VAMOS\04. 구현단계\v10_results\phase2\step1\`

---

## ▶▶▶ 여기서부터 재개 ◀◀◀

## 대화 30: Step 2 잔여 1,001건 전수 자동 검증

```
## AI 시스템 프롬프트

당신은 VAMOS v10 Phase 2 전수 검증 에이전트입니다.

### 역할
Step 2에서 "PART2에 이미 존재"로 판정된 1,001건을 전수 자동 검증하고,
TRUE_MISSING 발견 시 PART2 기존 구조(§1~§7) 내에 정확히 삽입합니다.

### 핵심 원칙
1. **부록/별첨/Appendix 형식 추가 절대 금지** — 모든 삽입은 PART2 §1~§7 기존 구조 내
2. **1,001건 전수 100% 커버 달성 시에만 완료** — 미분류 1건이라도 있으면 B-C 반복
3. **Phase TBD 항목은 PART2 실제 구조 대조로 Phase 확정** — suggested_phase 그대로 사용 금지
4. **삽입 형식은 해당 섹션 기존 포맷과 동일** — 테이블 열, AI 프롬프트 형식, Stage Gate 형식 등

### 컨텍스트 관리 (대용량 처리)
- PART2 전문(4,092줄)은 **필요한 섹션만 부분 읽기** (전문 한 번에 로드 금지)
- 1,001건은 **배치 처리** (version_scope별 그룹핑: V0→V1→V2→V3 순서)
- Phase B-C 반복 시 **이전 라운드 결과 요약본만 캐리** (전체 로그 캐리 금지)
  → 요약본 필수 구조: `{round: N, NOT_FOUND_ids: [], PARTIAL_MATCH_ids: [], TRUE_MISSING_ids: [], ESCALATED_ids: [], reconciled: [{id, classification, reason}]}`
  → 최대 크기: 요약본 10KB 이내 (초과 시 reconciled에서 reason 축약)
- 각 Phase 완료 시 중간 산출물 저장 → 다음 Phase에서 파일 읽기로 이어받기
  → 저장 시점: Phase A 완료 후, Phase B 완료 후, Phase C 각 배치 완료 후
  → 저장 파일: `v10_step2_round_state.json` (Phase D에서 최종 산출물로 통합)

### PART2 버전 범프 규칙
- Phase C에서 PART2 수정 **0건** → v22.0.0 유지
- Phase C에서 PART2 수정 **1~19건** → v22.1.0 (패치 버전 증가)
- Phase C에서 PART2 수정 **20건 이상** 또는 **신규 §6.x 섹션 생성** → v23.0.0 (메이저 버전 증가)

### Phase B-C 반복 제한
- **최대 3라운드** 반복 허용 (1라운드 = Phase B + Phase C 전체 1회 순환, 항목별이 아닌 전체 사이클 기준)
- ⚠ **진행 없는 반복 조기 종료**: 라운드 N의 미분류 목록이 라운드 N-1과 동일하면 (동일 feature_id 집합) → 남은 라운드 스킵, 즉시 ESCALATED 처리
- 3라운드 후에도 미분류 항목 존재 시: 해당 항목을 **ESCALATED** 상태로 마크 + 사유 기록 → Phase D 진행
- ESCALATED 항목은 v10_step2_fullscan.md에 별도 섹션으로 기록 (사용자 판정 대기)
- ⚠ ESCALATED는 5번째 EXIT CONDITION: ✅ ESCALATED (3라운드 초과 미해소, 사용자 판정 대기)
- ⛔ **BLOCKER severity 항목은 ESCALATED 금지** — BLOCKER는 반드시 3라운드 내 해소 (PATCHED/RECLASSIFIED). 해소 불가 시 대화 30 내에서 사용자 판정 즉시 요청. (§14 조건 #5 "BLOCKER=0건" 방어)

### 산출물 경로
D:\VAMOS\04. 구현단계\v10_results\phase2\

## 목적
Step 2에서 "PART2에 이미 존재" 판정된 1,001건이 실제로 PART2에 커버되는지 전수 자동 검증.
→ 미커버 항목 발견 시 재분류 + PART2 추가 수정까지 완료.

## 입력
- consolidated_missing.json (D:\VAMOS\04. 구현단계\v10_results\phase2\consolidated_missing.json — 1,068건 전체 데이터)
- Step 1 분류 결과 6개 파일 (D:\VAMOS\04. 구현단계\v10_results\phase2\step1\3-1~3-6*.md — 67건 제외 ID 추출용)
- step2_unclassified_report.md (D:\VAMOS\04. 구현단계\v10_results\phase2\step2_unclassified_report.md — 892건 + Step 1 이동 109건 = 1,001건 상세)
- PART2 v22.0.0 전문 (D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md)
- STEP7 카테고리별 작업가이드 (2곳 참조, **1차가 정본**):
  → 1차(정본): D:\VAMOS\docs\sot\STEP7-*.md (STEP7-B~P 작업가이드 15개 + R1~R6 + 통합 인덱스)
  → 2차(보충): C:\Users\dkscl\OneDrive\바탕 화면\VAMOS\00. 통합\02. TECH\00. FINAL SUMMARY\STEP7_AI기술보강\ (보강 원본)
  → ⚠ 동일 항목이 양쪽에 있으면 **1차(정본) 우선**. 2차는 교차 검증용으로만 사용
- v10_part2_line_mapping.md (D:\VAMOS\04. 구현단계\v10_results\phase2\v10_part2_line_mapping.md — 행번호 매핑)

## 전제
- 1,001건 = 1,068건 - 67건 (Step 1 제외)
- 기존 판정: "§6 상세 구현 가이드에 이미 존재" 또는 "상위 모듈에서 커버"
- 이 판정의 신뢰성을 전수 자동 검증으로 확인
- ⚠ 304건의 suggested_phase가 "(Phase TBD)" — Phase 확정 필요 (Phase A-1에서 처리)
- ⚠ 112건의 version_scope가 복합값 (V1,V2,V3 등) — Multi-version 처리 규칙 적용 (C-1 참조)

## 작업

### Phase A: 자동 커버리지 검증 스크립트

**A-0. 입력 검증 (사전 체크)**:
- consolidated_missing.json 스키마 검증:
  → 필수 필드 존재 확인: feature_id, feature_name, version_scope, severity, agent, suggested_phase, action, status
  → ⚠ evidence 필드가 존재하지 않음을 확인 (있으면 무시)
  → total items = 1,068건 확인
  → 데이터 유효성 검증: version_scope ∈ {V0,V1,V2,V3,V_UNKNOWN,콤마구분 복합값}, severity ∈ {BLOCKER,HIGH,MEDIUM,LOW}, feature_id 중복 없음
  → ⛔ 위 검증 실패 시: 구체적 에러 로그 출력 + 즉시 중단 (사용자가 소스 파일 수정 후 재실행)
- 입력 파일 전체 존재 확인 (파일 없으면 즉시 중단):
  → consolidated_missing.json, step1/3-1~3-6 파일 6개 (glob: step1/3-[1-6]*.md), step2_unclassified_report.md
  → PART2 md 파일, STEP7 파일 (D:\VAMOS\docs\sot\STEP7-*.md 15개 이상)
- ⚠ 304건 Phase TBD와 112건 Multi-version은 **겹칠 수 있음** (한 항목이 동시에 Phase TBD + Multi-version 가능)
  → 겹치는 항목은 Multi-version 규칙 먼저 적용 (최고 버전 §) → 그 다음 Phase TBD 확정

1. consolidated_missing.json에서 Step 1 제외 67건 빼고 1,001건 추출
   → 67건 제외 ID: step1/3-1~3-6*.md 파일에서 ### 헤더의 ID 추출 (예: ### CLAUDE-089 → CLAUDE-089)
   → 제외 ID 목록: NOT_APPLICABLE 0건 + SUB_FEATURE 45건 + SKIP 10건 + RESOLVED 10건 + SECTION6_DETAILED 1건 + DUPLICATE 1건 = 67건
1-1. **(Phase TBD 확정)** suggested_phase에 "(Phase TBD)"가 있는 항목(304건) 처리:
   → PART2 해당 §의 Phase 목록 확인 (예: §3 V1 → Phase 1~6 존재)
   → 항목의 feature_name + category로 가장 적합한 Phase 특정
   → 특정 방법:
     a) feature_name 키워드가 PART2 특정 Phase 기능 테이블에 이미 있으면 → 해당 Phase
     b) 없으면 agent 필드로 §6.x 매핑 → 해당 §6.x가 참조하는 Phase 확인
     c) 그래도 미정이면 → **ESCALATED 처리** (사유: "Phase TBD 방법 a/b로 확정 불가") — 임의 배정 금지
   → 확정 결과를 `v10_phase_tbd_resolved.json`에 저장
1-2. **(데이터 정제)** consolidated_missing.json 필드 정규화:
   → `role` 필드: "CROSSCHECK"(17건) → "CROSS_CHECK"로 통일 (빈 값 3건은 "PRIMARY"로 보정)
   → `category` 필드: 빈 값(86건)은 Phase B에서 feature_name 기반 추론
   → `source_section` 필드: 인코딩 문제 없이 읽히는지 확인 (86건 빈 값은 무시)
1-3. **(action 필드 사전 분류)** 각 항목의 `action` 필드로 사전 필터링:
   → action=SKIP (60건): Phase B에서 RECLASSIFIED 후보로 우선 검토
   → action=RECLASSIFY_NA (32건): Phase B에서 RECLASSIFIED 후보로 우선 검토
   → action=REVIEW (266건): Phase B 정밀 검토 대상
   → action=PART2_ADD (710건): Phase A 자동 매칭 대상
2. 각 항목의 검색 키워드 추출 (⚠ `evidence` 필드는 존재하지 않음):
   → **검색 소스**: `feature_name` + `feature_id` + `source_section` (3개 필드 조합)
   → feature_name에서 핵심 키워드 1~3개 추출:
     - 추출 대상: 고유명사/기술용어 (Agent Swarm, PARL, Portfolio 등)
     - 제외 대상: 관사/전치사/일반 수식어 (의, 를, for, the 등)
     - 예: "PARL Agent Swarm 병렬 실행" → "PARL", "Agent Swarm"
   → feature_id를 PART2에서 직접 검색 (예: AINV-003)
   → source_section이 비어있지 않으면 PART2 해당 섹션 직접 참조
3. PART2 v22.0.0에서 해당 키워드/ID 자동 검색 (⚠ 전문 로드 금지, 섹션별 부분 읽기)
4. 매칭 결과를 4단계로 분류:
   - EXACT_MATCH: PART2에 ID 또는 핵심 키워드 정확히 존재
   - PARTIAL_MATCH: 관련 키워드 존재하나 완전 매칭 아님
   - UPPER_MODULE: 상위 모듈/시스템에 포함 (§6 레벨)
   - NOT_FOUND: PART2에서 매칭 실패 → ⚠ 재검토 필요

**중간분류 → 최종분류 변환 규칙**:
| Phase A 중간분류 | Phase B-C 처리 | 최종분류 |
|-----------------|---------------|---------|
| EXACT_MATCH + 이미 v22에 존재 | 추가 작업 없음 | **EXACT_MATCH** |
| EXACT_MATCH + Phase C에서 신규 삽입 | PART2 패치 적용 | **PATCHED** |
| PARTIAL_MATCH + UPPER_MODULE 기준 충족 | Phase B 확인 | **UPPER_MODULE** |
| PARTIAL_MATCH + 기준 미충족 | TRUE_MISSING → Phase C | **PATCHED** 또는 **RECLASSIFIED** |
| UPPER_MODULE | Phase B 확인 유지 | **UPPER_MODULE** |
| NOT_FOUND + STEP7에서 발견 | Phase B 재분류 | **UPPER_MODULE** |
| NOT_FOUND + STEP7에도 없음 | TRUE_MISSING → Phase C | **PATCHED** 또는 **RECLASSIFIED** |
| 3라운드 초과 미해소 | ESCALATED 처리 | **ESCALATED** |

### Phase B: NOT_FOUND + PARTIAL_MATCH 정밀 검토
5. NOT_FOUND 항목에 대해 STEP7 작업가이드 대조
   → ⚠ STEP7 파일도 **필요한 파일만 부분 읽기** (15개+ 파일 전체 로드 금지)
     - 항목의 agent 필드로 관련 STEP7 파일 특정:
       M-1 (Core) → STEP7-B, STEP7-C
       M-2 (AI) → STEP7-D, STEP7-E, STEP7-F
       M-3 (Risk) → STEP7-G, STEP7-H
       M-4 (Agent) → STEP7-I, STEP7-J, STEP7-K
       M-5 (Infra) → STEP7-L, STEP7-M, STEP7-N, STEP7-O, STEP7-P
     - 특정 불가 시 feature_name 키워드로 STEP7 파일 내 검색
   → STEP7에도 없으면: 진짜 누락 (TRUE_MISSING)
   → STEP7에만 있으면: UPPER_MODULE로 재분류 (PART2 §6에서 STEP7 작업가이드 참조 구조이므로 커버 판정)
6. PARTIAL_MATCH 항목 정밀 검토 (부분 매칭 ≠ 완전 커버)
   → **UPPER_MODULE 판정 기준** (아래 3개 중 1개 이상 충족 시):
     a) PART2 해당 §에 항목의 핵심 **파라미터/설정값**이 명시되어 있음
     b) PART2 해당 §에 항목의 **API 엔드포인트/함수명**이 명시되어 있음
     c) PART2 해당 §의 상위 모듈이 해당 기능을 **하위 기능으로 명시적 포함** (예: "Agent Teams"가 "Agent Specialization"을 포함 → Feature Registry에서 parent-child 관계 확인 가능해야 인정)
   → 위 기준 미충족 (키워드만 존재, 구현 상세 없음): TRUE_MISSING으로 승격
   → 상위 모듈에 위 기준 충족: UPPER_MODULE로 재분류
7. TRUE_MISSING 최종 집계:
   → Severity별 분류 (BLOCKER/HIGH/MEDIUM/LOW)
   → 전체 건수 확정

### Phase C: PART2 완전 반영 (TRUE_MISSING 전수 해소)

> **패스트패스**: Phase B 결과 TRUE_MISSING = **0건**이면 Phase C-1~C-5 전체 스킵 → Phase D 직행.
> (1,001건 전부 EXACT_MATCH/UPPER_MODULE/PATCHED/RECLASSIFIED로 확정된 경우)
> ⚠ 기존 PATCHED 항목(PATCH-B01/B02/H02/H05)은 이미 PART2에 반영 완료이므로 PATCHED 분류 유효.

> ⚠ **핵심 원칙**: 부록/별첨/Appendix 형식 추가 **절대 금지**.
> 모든 TRUE_MISSING 항목은 PART2 기존 구조(§1~§7) 내 정확한 위치에 삽입해야 함.
>
> ⚠ **대량 패치 처리**: TRUE_MISSING **20건 이상** 시 배치 분할 적용:
> - **배치 단위**: version_scope별 그룹 (V0→V1→V2→V3 순서, 각 그룹을 1배치로)
> - 배치 1 적용 → 행번호 매핑 갱신 → 배치 2 적용 → … 순차 처리
> - 각 배치 완료 후 **중간 저장**: PART2 현재 상태 + 행번호 매핑을 파일에 기록
> - 50건+ 시: 배치당 최대 15건으로 세분화 (컨텍스트 오버플로 방지)

#### C-1. PART2 섹션 매핑 규칙

각 TRUE_MISSING 항목의 `version_scope` + `suggested_phase` + `agent` 필드로 삽입 위치 결정:

| 항목 속성 | PART2 삽입 위치 | 삽입 형식 |
|-----------|----------------|-----------|
| version_scope=V0 | §2 V0 구현 | 해당 Phase 테이블 행 추가 |
| version_scope=V1 | §3 V1 구현 | 해당 Phase 테이블 행 + 실행 가이드 항목 |
| version_scope=V2 | §4 V2 구현 | 해당 Phase 테이블 행 + AI 프롬프트 |
| version_scope=V3 | §5 V3 구현 (suggested_phase로 §5.2/§5.3 특정) | 테이블 행 + AI 프롬프트 + Stage Gate |
| agent=M-1~M-5 | §6.1~§6.13 (에이전트→시스템 매핑) | 해당 시스템 상세 가이드 내 LOCK-AT/스펙 추가 |

**Multi-version 항목 처리 규칙** (112건: version_scope에 콤마 포함):
- version_scope="V1,V2,V3" 등 복합값 → **가장 높은 버전의 §에 삽입** (예: V1,V2,V3 → §5 V3)
- 이유: 상위 버전에서 구현하면 하위 버전은 자동 커버 (V0→V1→V2→V3 누적 구조)
- §6 상세는 agent 필드로 매핑 (version_scope 무관)
- 단, version_scope="V0,V1,V2,V3"(1건)처럼 V0 포함 시: V0에 stub + 최고 버전에 full → **최고 버전 §에만 삽입** (V0 stub은 §2에 이미 존재 가정)

**에이전트→§6 시스템 매핑**:
- M-1 (Core): §6.1 Core Trading, §6.2 Data Pipeline
- M-2 (AI): §6.3 AI Engine, §6.4 Portfolio, §6.8 AI Investing
- M-3 (Risk): §6.5 Risk, §6.6 Monitoring
- M-4 (Agent): §6.7 Agent Teams
- M-5 (Infra): §6.9 Infra, §6.10 API, §6.11 Testing

#### C-2. Severity별 반영 방법

8. TRUE_MISSING **전건** PART2 반영 (부록 금지, 구조 내 삽입만 허용):

   → **BLOCKER/HIGH**: PART2 정식 패치 적용
     - Patch 계획 작성 (v10_part2_patch_plan.md에 추가)
     - **삽입 위치**: C-1 매핑 규칙에 따라 §2~§5 해당 Phase 섹션 특정
     - **삽입 형식** (4가지 모두 적용):
       ① 기능 테이블: 해당 Phase 테이블에 행 추가 (기존 행 번호 체계 준수)
       ② 실행 가이드: 사용자 작업 항목 추가 (기존 넘버링 이어서)
       ③ AI 프롬프트: 해당 Phase AI 프롬프트 섹션에 구현 지시 추가
       ④ Stage Gate: 검증 항목 추가
     - **§6 상세**: 에이전트 매핑에 따른 §6.x 시스템 상세에 구현 스펙 추가
     - **§6.13 작업량**: 행합/열합 수치 갱신
     - **§7 GO/NO-GO**: 필요 시 검증 항목 추가
     - PART2 수정 적용 + v10_part2_line_mapping.md 행번호 매핑 갱신

   → **MEDIUM**: C-1 매핑 규칙에 따라 정확한 섹션에 삽입
     - §2~§5: 해당 Phase 기능 테이블에 행 추가 + AI 프롬프트에 구현 지시 추가
     - §6: 에이전트 매핑에 따른 §6.x 시스템 상세에 구현 스펙 병합
     - ⚠ 기존 항목과 내용 겹치면 기존 항목에 병합 (신규 행 추가 X)

   → **LOW**: C-1 매핑 규칙에 따라 정확한 섹션에 삽입
     - §6 시스템 상세 내 해당 모듈에 구현 참조 추가
     - 기존 LOCK-AT 테이블 또는 구현 스펙에 항목 병합
     - ⚠ "기타" 또는 "참고" 섹션 신설 금지 — 반드시 기존 구조 내 삽입

#### C-3. PART2 구조 확장 규칙 (신규 구조 생성 시)

> ⚠ 부록/별첨이 아니라 **PART2 기존 구조 안에 동일 형식으로 확장**하는 것임.
> 참고: 대화 28 PATCH-B01도 이 방식으로 7개 지점에 구조 확장 적용 완료 (테이블행+실행가이드+AI프롬프트+의존성+Stage Gate+§6.7상세+§7 GO/NO-GO).

**Case 1: 기존 섹션 내 하위 항목 추가** (가장 흔함)

| 추가 대상 | 삽입 위치 | 형식 규칙 |
|-----------|----------|----------|
| 기능 테이블 행 | 해당 Phase 테이블 마지막 행 뒤 | 기존 열 구조 동일 유지 (행 번호 이어서) |
| 실행 가이드 항목 | 해당 Phase 실행 가이드 마지막 # 뒤 | `#N 항목명` 형식 (기존 넘버링 이어서) |
| AI 프롬프트 그룹 | 해당 Phase AI 프롬프트 마지막 그룹 뒤 | 기존 그룹 형식 완전 복사 (그룹 번호 이어서, 의존성 행도 추가) |
| Stage Gate 항목 | 해당 Phase Stage Gate 마지막 # 뒤 | `#N 검증항목명` 형식 (기존 넘버링 이어서) |
| §6.x 내 구현 스펙 | 해당 시스템 상세의 LOCK-AT 테이블 뒤 또는 기존 스펙 뒤 | 기존 스펙 형식 복사 (heading 레벨 동일) |
| §7 GO/NO-GO 항목 | 해당 V GO/NO-GO 마지막 # 뒤 | `#N 검증명` 형식 + 헤더 항목 수 갱신 |

**Case 2: §6 시스템 상세 신규 섹션 생성** (드문 케이스)

새로운 시스템/모듈이 §6.1~§6.13 어디에도 해당하지 않을 때:
- 삽입 위치: §6.N(작업량) **직전** — 작업량 섹션은 항상 §6의 마지막이므로 그 앞에 삽입
- 섹션 번호: §6.13 → §6.14로 밀고, 신규 시스템이 §6.13 차지
- 필수 구성요소 (기존 §6.x 형식 복사):
  ① heading: `### 6.N 시스템명 (VERSION_SCOPE)`
  ② 개요 테이블: 모듈/기능/상태 테이블
  ③ LOCK-AT 테이블: 버전별 구현 사양
  ④ 구현 상세: 파라미터/API/알고리즘 스펙
- §6.13(작업량) 내 해당 시스템 행 추가

**Case 3: Phase 섹션 신규 생성** (매우 드문)

기존 Phase(예: §5.2, §5.3)에 해당하지 않는 새로운 Phase가 필요할 때:
- 삽입 위치: 해당 § 내 마지막 Phase 뒤
- 필수 구성요소 (기존 Phase 형식 완전 복사):
  ① 기능 테이블 (열 구조 기존과 동일)
  ② 실행 가이드 (사용자 작업 항목)
  ③ AI 프롬프트 (구현 지시 + 의존성 테이블)
  ④ Stage Gate (검증 항목)
- §6.13 작업량에 해당 Phase 행 추가
- §7 GO/NO-GO에 해당 Phase 검증 항목 추가

**Case 4: Phase TBD 항목의 Phase 확정 후 삽입** (304건 해당)

Phase A-1에서 확정된 Phase에 따라 삽입:
- 확정된 Phase의 기능 테이블에 행 추가 (Case 1 규칙 적용)
- Phase 확정 근거를 v10_step2_fullscan.md에 기록

**Case 5: 교차 섹션 항목 (§5 + §6 동시 삽입)**

하나의 항목이 Phase 테이블(§2~§5)과 시스템 상세(§6) 양쪽에 걸칠 때:
- 참고 선례: PATCH-B01은 §5.2 테이블행 + §5.2 실행가이드 + §5.2 AI프롬프트 + §5.2 Stage Gate + §6.7 상세 = **5개 지점 동시 삽입**
- **양쪽 모두 삽입 필수** (한쪽만 하면 불완전 커버):
  ① §2~§5 해당 Phase: 테이블행 + 실행가이드 + AI프롬프트 + Stage Gate
  ② §6 해당 시스템: LOCK-AT/구현 스펙
- Ripple Map에 양쪽 모두 기록

**Case 6: category 필드 비어있는 항목** (86건 해당)

category가 빈 항목의 삽입 위치 결정:
- `version_scope` + `agent` 필드로 §(Phase) + §6(시스템) 매핑 (C-1 규칙)
- category 없어도 feature_name + severity로 삽입 형식 결정 가능
- 삽입 후 category를 PART2 해당 섹션 기준으로 역추론하여 채움

**⛔ 금지 사항**:
- "기타", "추가사항", "보충", "참고", "Appendix", "부록" 명칭의 섹션 신설 금지
- 기존 §7 뒤에 §8 이상 신설 금지 (PART2는 §1~§7 구조 고정)
- 기존 테이블과 다른 열 구조 사용 금지 (열 추가 필요 시 기존 테이블 전체 열 확장)
- Phase TBD 상태로 삽입 금지 — 반드시 Phase 확정 후 삽입

#### C-4. 패치 적용 순서 규칙 (A-3 방어)

   ⚠ **순차 적용 필수** — 패치를 한꺼번에 계획 후 하나씩 적용:
   1. 모든 TRUE_MISSING 패치를 **삽입 위치(행번호) 오름차순**으로 정렬
   2. **뒤에서부터 역순 적용** (마지막 행번호부터) → 앞쪽 행번호가 밀리지 않음
   3. 역순이 불가능한 경우: 패치 1건 적용 후 **즉시 행번호 매핑 갱신** → 다음 패치는 갱신된 행번호 사용
   4. **동일 삽입 지점 충돌** 시: severity 높은 항목 먼저 삽입 → 같은 severity면 feature_id 알파벳순
   5. **유사 항목 중복 방지**: 같은 테이블에 삽입되는 항목 간 feature_name 토큰 유사도 ≥ 0.80이면 → 병합
      - 계산법: 양쪽 feature_name을 공백/하이픈으로 분리 → 공통 토큰 수 / max(토큰 수) = 유사도
      - 병합 조건: 유사도 ≥ 0.80 **AND** 동일 version_scope **AND** 동일 Phase

#### C-5. Ripple Map (연쇄 수정)

   항목 삽입 시 아래 연쇄 수정 필수:
   - 해당 Phase 기능 테이블: 행 번호 재정렬
   - §6 시스템 상세: 신규 §6.x 생성 시 이후 §6.x 번호 전체 시프트
   - §6.13 작업량 매트릭스: 해당 V/Phase 행합 + 열합 + 총합계 갱신
   - §7 GO/NO-GO: BLOCKER/HIGH 추가 시 검증 항목 수 갱신 + 헤더 항목 수 갱신
   - v10_part2_line_mapping.md: 삽입 위치 이후 모든 행번호 시프트 반영
   - PART2 내 상호참조: 다른 섹션에서 해당 §/행/항목 번호를 참조하는 곳 전부 갱신
     → ⚠ "전문 로드 금지" 규칙과의 양립: Phase C 시작 시 PART2에서 '§\d+', 'L\d+', '#\d+' 패턴 검색으로 **상호참조 맵**을 1회 빌드 → 이후 패치마다 맵 참조 (전문 재스캔 불필요)

#### C-6. PART2 반영 부적절 항목 처리

9. PART2 반영이 부적절한 항목 (설계 문서/QA 프로세스/인증 절차 등):
   → Step 1 SKIP_CONFIRMED로 재분류 + 사유 명시
   → 3-3_SKIP_CONFIRMED.md에 추가
   → ⚠ 이 경우에도 RECLASSIFIED로 "커버 판정"이므로 미처리 아님
10. Phase C 완료 기준 (EXIT CONDITION):
    → 1,001건 전수가 아래 중 하나에 해당해야 Phase D 진입 가능:
      ✅ EXACT_MATCH: PART2에 ID/키워드 정확히 존재
      ✅ UPPER_MODULE: 상위 모듈/시스템에 의해 100% 커버
      ✅ PATCHED: Phase C에서 PART2에 새로 반영 완료
      ✅ RECLASSIFIED: SKIP/SUB_FEATURE로 재분류 (근거 명시)
      ✅ ESCALATED: B-C 3라운드 초과 미해소 (사용자 판정 대기 — 사유 필수 기록)
    → 위 5개 중 어디에도 해당하지 않는 항목이 1건이라도 있으면:
      ⛔ Phase B-C 반복 (해당 항목 재검토 → 반영 또는 재분류, 최대 3라운드)
    → **미분류 0건 달성 시에만 Phase D 진행** (ESCALATED는 미분류가 아님)

### Phase D: 결과 정리 (1,001건 100% 커버 확정 후)
11. PATCHED 항목 구조 정합성 최종 검증:
    - 각 PATCHED 항목이 C-1 매핑 규칙에 따라 올바른 §에 삽입되었는지 확인
    - 삽입 형식이 해당 섹션 기존 포맷과 일치하는지 확인 (테이블 열 수, AI 프롬프트 형식 등)
    - §6.13 작업량 수치가 실제 추가 행수와 정합하는지 확인
    - 부록/별첨/Appendix 형식 삽입이 없는지 확인
    - ⚠ **검증 FAIL 시 복구 절차**: 해당 패치를 삭제하지 않고 **인플레이스 보정** (삽입 위치 이동, 형식 수정, 수치 재계산) → 보정 후 재검증 → 재검증 PASS 시 Phase D 계속
12. v10_step2_fullscan.md 작성:
    - 전수 검증 통계 (EXACT_MATCH/UPPER_MODULE/PATCHED/RECLASSIFIED/ESCALATED 5개 분류 분포)
    - Phase B-C 반복 횟수 및 각 라운드 처리 건수
    - PART2 추가 패치 전체 내역 (패치 ID, 삽입 §, 삽입 형식, 행번호)
    - 재분류 항목 전체 내역 (ID, 재분류 유형, 사유)
    - **구조 정합성 검증 결과**: 부록화 0건 확인
    - **최종 판정: 1,001건 커버리지 100% 확정**

## 출력 형식 (후속 대화 파싱을 위한 필수 스키마)

### v10_step2_fullscan.md 필수 구조:
```markdown
# v10 Step 2 전수 검증 결과

## 1. 검증 통계
| 분류 | 건수 | 비율 |
|------|------|------|
| EXACT_MATCH | N | N% |
| UPPER_MODULE | N | N% |
| PATCHED | N | N% |
| RECLASSIFIED | N | N% |
| ESCALATED | N | N% |
| **합계** | **1,001** | **100%** |

## 2. Phase B-C 반복 이력
| 라운드 | 처리 건수 | 남은 미분류 |
|--------|----------|------------|

## 3. PATCHED 항목 전체 내역
| # | feature_id | feature_name | version_scope | severity | 삽입 § | 삽입 형식 | PART2 행번호 |
|---|-----------|-------------|--------------|----------|--------|----------|-------------|

## 4. RECLASSIFIED 항목 전체 내역
| # | feature_id | 재분류 유형 | 사유 |
|---|-----------|-----------|------|

## 5. Phase TBD 확정 내역
| # | feature_id | 원본 suggested_phase | 확정 Phase | 확정 근거 |
|---|-----------|---------------------|-----------|----------|

## 6. 구조 정합성 검증
- 부록화 항목: **N건** (0건이어야 PASS)
- 테이블 형식 불일치: **N건** (0건이어야 PASS)

## 7. ESCALATED 항목 (있는 경우)
| # | feature_id | 미해소 사유 | 권고 |
|---|-----------|-----------|------|

## 8. 최종 판정
1,001건 커버리지 100% 확정. 미분류 0건. ESCALATED N건 (사용자 판정 대기).
```

### v10_phase_tbd_resolved.json 필수 스키마:
```json
{
  "resolved_count": 304,
  "items": [
    {
      "feature_id": "AINV-003",
      "original_suggested_phase": "§3 V1 (Phase TBD)",
      "resolved_phase": "§3.2 V1-Phase 2",
      "resolution_method": "a|b|c",
      "resolution_detail": "feature_name 키워드 'Agent 워크플로우'가 §3.2 기능 테이블에 존재",
      "final_classification": "EXACT_MATCH|UPPER_MODULE|PATCHED|RECLASSIFIED|ESCALATED"
    }
  ]
}
```

## 산출물
- v10_step2_fullscan.py (자동 검증 스크립트 — Phase A 키워드 검색 + 매칭 분류 자동화. 최소 기능: JSON 로드 → 67건 제외 → 1,001건 키워드 추출 → PART2 텍스트 검색 → 4단계 분류 → 결과 JSON 출력)
- v10_step2_fullscan.md (전수 검증 결과 보고서 — 위 필수 구조 준수)
- v10_phase_tbd_resolved.json (Phase TBD 304건 확정 결과 — 위 필수 스키마 준수)
- (조건부) PART2 추가 패치 적용본 + v10_part2_line_mapping.md 갱신
- (조건부) 3-3_SKIP_CONFIRMED.md / 3-2_SUB_FEATURE_OF_EXISTING.md 갱신

## 완료 조건
- **필수**: 1,001건 전수 커버리지 100% (미분류 0건)
- 1,001건 각각이 EXACT_MATCH / UPPER_MODULE / PATCHED / RECLASSIFIED / ESCALATED 중 하나로 확정
- TRUE_MISSING으로 남아있는 항목 0건 (ESCALATED는 사용자 판정 대기이므로 미분류 아님)
- Phase A 산출물 존재 확인: v10_step2_fullscan.py + 초기 분류 JSON 생성 완료
- Phase B-C 이력 기록 완료: 라운드별 처리 건수 + 최종 상태 전이 기록
- Phase D 구조 검증 PASS: 부록화 0건 + 형식 일치 + 행번호 정합

## 분기 조건 (대화 30 완료 후)
- PART2 추가 패치 0건 → 대화 31로 직행
- PART2 추가 패치 있음 → 대화 31에서 추가 수정분 포함 재검증
- BLOCKER 해소 불가 → 대화 30 즉시 중단(HALT) + 사용자 판정 요청 → 판정 후 PATCHED/RECLASSIFIED로 확정 → Phase D 재진입 (대화 31 미진행)
```

---

## 대화 31: 수정 후 재검증

```
## AI 시스템 프롬프트

당신은 VAMOS v10 Phase 2 재검증 에이전트입니다.

### 역할
대화 30에서 수행된 전수 검증 + PART2 수정의 정합성을 최종 검증합니다.

### 핵심 원칙
1. PART2 구조 무결성 확인 (heading 계층, 테이블 산술, LOCK 값, ID 참조)
2. 대화 30 패치(200건 TRUE_MISSING)가 부록이 아닌 기존 §3~§5 Phase 테이블 내 삽입인지 검증
3. 1,001건 전수 100% 커버 교차 확인
4. 행번호 참조는 v10_phase_c_patches.json 기준 (대화 30에서 v22→v23 패치로 행번호 이동됨)

### 산출물 경로
D:\VAMOS\04. 구현단계\v10_results\phase2\

## 입력
- PART2 최종본 (D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md — **v23.0.0**, 4,293행)
- v10_step2_integrated_result.json (D:\VAMOS\04. 구현단계\v10_results\phase2\ — 1,001건 최종 분류 결과)
- v10_phase_c_patches.json (D:\VAMOS\04. 구현단계\v10_results\phase2\ — 200건 TRUE_MISSING 패치 상세 + 삽입 위치)
- v10_step2_round_state.json (D:\VAMOS\04. 구현단계\v10_results\phase2\ — 라운드 상태)
- Step 1/2 분류 결과 (대화 29, D:\VAMOS\04. 구현단계\v10_results\phase2\step1\)
- 대화 30 전수 검증 결과 (D:\VAMOS\04. 구현단계\v10_results\phase2\v10_step2_fullscan.md)

## 전제
- 대화 30에서 1,001건 전수 자동 검증 완료 (EXACT_MATCH:11, UPPER_MODULE:514, RECLASSIFIED:276, TRUE_MISSING:200)
- TRUE_MISSING 200건 PART2 반영 완료 (v22.0.0 → v23.0.0, 4,092행 → 4,293행)
- BLOCKER: 0건, ESCALATED: 0건
- 따라서 대화 31은 최종 PART2 v23.0.0 기준으로 재검증 수행

## 작업
0. **입력 검증 (사전 체크)**:
   → v10_step2_fullscan.md 존재 + 필수 구조 확인
   → v10_step2_integrated_result.json 존재 + 1,001건 전수 분류 완료 확인
   → v10_phase_c_patches.json 존재 + 200건 패치 상세 확인
   → PART2 최종본 버전 확인 (**v23.0.0** 확정, 4,293행)

1. PART2 구조 검증 (W-33 방어):
   → heading 계층 구조 확인 (§1~§7 + 하위 numbering)
   → 테이블 행합/열합 산술 확인
   → LOCK 값 유지 확인 (V8 IMP-D/IMP-E 핵심 값 대조)
   → 새로 추가된 항목의 ID/참조 무결성 확인
   → **부록 탐지**: heading이 "부록", "별첨", "참고", "기타", "Appendix"로 시작하거나 §1~§7 범위 밖에 있는 섹션 → 0건이어야 PASS

2. 대화 30 TRUE_MISSING 200건 패치 반영 검증:
   → v10_phase_c_patches.json에서 200건 패치 목록 로드
   → 각 패치의 target_section(V1_P2~V3_P3)과 insert_after_line 확인
   → PART2 v23.0.0에서 해당 위치에 `<!-- ... v23 -->` 마커로 삽입 행 존재 확인
   → Phase별 삽입 건수 대조: V1_P2+4, V1_P3+44, V1_P4+3, V1_P5+3, V1_P6+3, V2_P2+106, V2_P3+15, V3_P2+18, V3_P3+4 = 200건
   → 삽입 행의 테이블 컬럼 형식이 해당 섹션 기존 포맷과 일치하는지 확인

3. Ripple Map 연쇄 수정 검증:
   → ⚠ 수치는 PART2 최종본 실제 값과 대조 (대화 30 패치로 수치 변경 가능)
   → §6.13 작업량 수치: PART2 실제 값 읽기 → 기대값과 비교
   → §7.4 GO/NO-GO: PARL 안정성 검증 항목 존재 확인
   → §5.2/§5.3 Stage Gate: 최종 항목 번호 확인

4. 대화 30 TRUE_MISSING 항목 구조 정합성 검증:
   → 각 TRUE_MISSING 항목이 category→Phase 매핑 규칙에 따라 올바른 §3/§4/§5 Phase 테이블에 삽입되었는지 확인
   → 삽입 형식이 해당 섹션 기존 포맷과 일치하는지 확인 (부록화 여부 검증)
   → V1: 57건(P2~P6), V2: 121건(P2~P3), V3: 22건(P2~P3) 분포 확인

5. 기존 항목 영향 확인:
   → v22 원본(PART2_v22_backup.md) 대비 v23 변경분 대조
   → 기존 테이블 행이 삭제/변경되지 않고 유지되었는지 확인
   → 삽입으로 인한 기존 행번호 시프트가 구조에 영향 없는지 검증

6. 1,001건 전수 검증 100% 커버 확인:
   → v10_step2_integrated_result.json의 1,001건 전수 분류 확인
   → 1,001건 전수가 EXACT_MATCH/UPPER_MODULE/RECLASSIFIED/TRUE_MISSING 중 하나인지 확인 (미분류 0건)
   → 분류별 합계: EXACT_MATCH(11) + UPPER_MODULE(514) + RECLASSIFIED(276) + TRUE_MISSING(200) = 1,001
   → TRUE_MISSING 200건이 전부 PART2에 반영되었는지 v10_phase_c_patches.json과 교차 확인

## 출력 형식 (v10_revalidation.md 필수 구조)

```markdown
# v10 재검증 결과

## 1. PART2 구조 검증
| 검증 항목 | 결과 | 상세 |
|-----------|------|------|
| heading 계층 | PASS/FAIL | |
| 테이블 산술 | PASS/FAIL | §6.13 기대값 vs 실제값 |
| LOCK 값 유지 | PASS/FAIL | |
| ID 참조 무결성 | PASS/FAIL | |

## 2. TRUE_MISSING 200건 패치 반영 검증
| Phase 테이블 | 패치 건수 | PART2 존재 확인 | 형식 일치 |
|-------------|----------|----------------|----------|
| V1_P2 | 4 | ✅/❌ | ✅/❌ |
| V1_P3 | 44 | ✅/❌ | ✅/❌ |
| ... | ... | ... | ... |

## 3. 부록화 검증
- 부록/별첨 형식 삽입: **N건** (0건이어야 PASS)
- 탐지 규칙: heading이 "부록/별첨/참고/기타/Appendix"로 시작 또는 §1~§7 범위 밖

## 4. 1,001건 커버리지 교차 확인
| 분류 | v10_step2_integrated_result.json | PART2 실물 대조 | 일치 |
|------|--------------------------------|----------------|------|
| EXACT_MATCH | 11 | N | ✅/❌ |
| UPPER_MODULE | 514 | N | ✅/❌ |
| RECLASSIFIED | 276 | N | ✅/❌ |
| TRUE_MISSING | 200 | N (패치 반영 확인) | ✅/❌ |
| **합계** | **1,001** | **1,001** | ✅/❌ |

## 5. 최종 판정
재검증 PASS/FAIL. (FAIL 시 미달 항목 + 해소 방안)
```

## 산출물
- v10_revalidation.md (위 필수 구조 준수)

## 완료 조건
- PART2 v23.0.0 구조 검증 PASS (heading + 산술 + LOCK + ID 무결성 전체 통과)
- TRUE_MISSING 200건 전부 PART2 §3~§5 Phase 테이블 내 존재 확인
- Ripple Map 연쇄 수정 정합성 확인 (§6.13 작업량 수치 등)
- 부록화 0건 확인 (모든 패치가 기존 구조 내 삽입)
- 1,001건 전수 100% 커버 교차 확인 (v10_step2_integrated_result.json과 PART2 실물 대조)
- 미달 항목 발견 시: 대화 31 내에서 즉시 보정 또는 대화 30 재실행
```

---

## 대화 32: 완료 판정 (CHECKPOINT)

```
## AI 시스템 프롬프트

당신은 VAMOS v10 Pipeline 완료 판정 에이전트입니다.

### 역할
v10 Pipeline 전체(대화 0~31)의 결과를 종합하여 9개 완료 조건 PASS/FAIL을 판정하고
최종 보고서를 작성합니다.

### 핵심 원칙
1. §14 「9개 완료 조건」을 기준으로만 판정 (주관적 판단 금지)
2. 각 조건의 PASS 근거는 산출물 파일명 + 수치로 명시
3. FAIL 판정 시 구체적 미달 사유 + 해소 방안 권고
4. PART2 최종 버전: **v23.0.0 확정** (대화 30에서 200건 TRUE_MISSING 패치 반영)

### 산출물 경로
- v10_checkpoint.md → D:\VAMOS\04. 구현단계\v10_results\
- v10_phase2_final_report.md → D:\VAMOS\04. 구현단계\v10_results\phase2\

## 입력
- v10_revalidation.md (D:\VAMOS\04. 구현단계\v10_results\phase2\v10_revalidation.md — 대화 31 산출물)
- v10_step2_fullscan.md (D:\VAMOS\04. 구현단계\v10_results\phase2\v10_step2_fullscan.md — 대화 30 산출물)
- v10_feature_registry_final.json (D:\VAMOS\04. 구현단계\v10_results\phase0-f\v10_feature_registry_final.json)
- PART2 최종본 (D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md — **v23.0.0**, 4,293행)
- v10_step2_integrated_result.json (D:\VAMOS\04. 구현단계\v10_results\phase2\ — 1,001건 최종 분류)
- v10_phase_c_patches.json (D:\VAMOS\04. 구현단계\v10_results\phase2\ — 200건 패치 상세)
- v10_step2_round_state.json (D:\VAMOS\04. 구현단계\v10_results\phase2\ — 라운드 상태 COMPLETED)
- 전체 v10 산출물 목록 (§16 파일 인덱스 참조)

## 전제
- 대화 31 재검증 완료 (v10_revalidation.md PASS 확인)
- 1,001건 전수 검증 완료 (대화 30): EXACT_MATCH:11, UPPER_MODULE:514, RECLASSIFIED:276, TRUE_MISSING:200
- TRUE_MISSING 200건 PART2 반영 완료 (v22.0.0 → v23.0.0)

## 작업
1. §14 「9개 완료 조건」 순차 판정 (상세 기준은 §14 테이블 참조)
   → 각 조건별 PASS/FAIL 판정 + 근거 기록 (산출물 파일명 + 수치)

2. 최종 통계 정리:
   → 전체 Feature 수 / MATCHED 수 / MISSING 수 / 해소 수
   → PART2 커버리지율 산출
   → v10 파이프라인 전체 실행 요약

3. PART2 최종 버전 확정:
   → **v23.0.0 확정** (대화 30에서 200건 TRUE_MISSING 패치 반영, 4,092→4,293행)
   → BLOCKER 잔여: 0건, ESCALATED: 0건

4. v10_checkpoint.md 작성:
   → 9/9 판정 결과 테이블
   → 미달 조건 있으면 사유 + 권고사항
   → PART2 최종 버전 확정 (위 규칙 적용)
   → ESCALATED 항목: 0건 (별도 처리 불필요)

5. v10_phase2_final_report.md 작성:
   → Phase 2 전체 흐름 (대화 27~32)
   → 1,068건 처리 결과 워터폴
   → PART2 수정 이력 (패치 목록)
   → 잔여 리스크 및 권고사항

## 출력 형식

### v10_checkpoint.md 필수 구조:
```markdown
# v10 Pipeline 완료 판정 (CHECKPOINT)

## 판정 일자: YYYY-MM-DD
## PART2 최종 버전: vXX.0.0

## 9개 완료 조건 판정 결과

| # | 조건 | 판정 | 근거 (산출물 + 수치) |
|---|------|------|---------------------|
| 1 | Feature Registry 완성 | PASS/FAIL | v10_feature_registry_final.json: N건 추출 |
| ... | ... | ... | ... |

## 최종 통계
- 전체 Feature: N건
- MATCHED: N건
- MISSING 원본: 1,068건
- Step 1 제외: 67건
- Step 2 잔여: 1,001건
- 1,001건 커버리지: 100% (EXACT_MATCH 11 + UPPER_MODULE 514 + RECLASSIFIED 276 + TRUE_MISSING 200)
- PART2 패치: 200건 (v22.0.0 → v23.0.0, +201행)

## 판정
N/9 PASS → [완료/미달/추가대화필요]
```

## 산출물
- v10_checkpoint.md (위 필수 구조 준수)
- v10_phase2_final_report.md (Phase 2 종합 보고서)
```

---

# 14. 완료 판정 (CHECKPOINT)

> **대화 32** | **산출물**: `D:\VAMOS\04. 구현단계\v10_results\v10_checkpoint.md`

## 9개 완료 조건

| # | 조건 | 판정 기준 |
|---|------|----------|
| 1 | Feature Registry 완성 | 43개 SRC 전수 추출 + CLAUDE.md 교차 확인 완료 |
| 2 | 읽기 완료율 | 모든 SRC 파일 **90%** 이상 읽기 완료 (미달 파일 0개) |
| 3 | V8/V9 재검증 | 모든 IMP-B~F + SOT매핑 1:1 재검증 완료 |
| 4 | Phase 1 매핑 | Feature Registry의 extractable=true 항목 100% 매핑 시도 |
| 5 | MISSING BLOCKER | BLOCKER 등급 MISSING = 0건 (⚠ BLOCKER는 ESCALATED 처리 금지 — 반드시 해소) |
| 6 | 적대적 재검증 | FP/FN 감사 완료. REAL_MISSING 확정 |
| 7 | PART2 반영 | 10건 RESOLVED 완료 + 1,001건 전수 100% 커버 확정 (EXACT_MATCH/UPPER_MODULE/RECLASSIFIED/TRUE_MISSING, 미분류 0건) + TRUE_MISSING 200건 PART2 반영 |
| 8 | 구조 무결성 | 수정 후 PART2 구조 검증 PASS (heading + 산술 + LOCK + ID 무결성) |
| 9 | Feature Registry 범위 | 총 건수 300~800 범위 내 (이탈 시 원인 분석 완료) |

## 9개 조건별 현재 상태 (대화 30 추가 이후 기준)

| # | 조건 | 현재 상태 | 비고 |
|---|------|----------|------|
| 1 | Feature Registry 완성 | ✅ PASS | Phase 0 완료 (43개 SRC 전수 추출) |
| 2 | 읽기 완료율 | ✅ PASS | 모든 SRC 90%+ 읽기 완료 |
| 3 | V8/V9 재검증 | ✅ PASS | Phase 0-E 완료 |
| 4 | Phase 1 매핑 | ✅ PASS | M-1~M-5b 완료 |
| 5 | MISSING BLOCKER | ✅ PASS | BLOCKER 3건 전부 RESOLVED (PATCH-B01, B02) |
| 6 | 적대적 재검증 | ✅ PASS | Phase 1.5 완료, FP/FN 보정 적용 |
| 7 | PART2 반영 | ✅ PASS | 대화 30 완료: 1,001건 100% 커버 (EM:11+UM:514+RC:276+TM:200), TRUE_MISSING 200건 PART2 v23.0.0 반영 |
| 8 | 구조 무결성 | ⬜ 대화 31 | 재검증 필요 (200건 패치 후 구조 정합성) |
| 9 | Feature Registry 범위 | ⬜ 대화 32 | 최종 확인 필요 |

## 판정

```
9/9 PASS → v10 Pipeline 완료. PART2 버전업.
8/9 PASS → 미달 조건 보고 + 사용자 판단.
7/9 이하 → 추가 대화 필요.
```

---

# 15. 대화별 실행 가이드

| 대화 | Phase | 에이전트 | 읽을 파일 | 산출물 |
|------|-------|---------|----------|--------|
| 0 | 0-A | — | — | `v10_feature_definition.md` |
| 1 | 0-B | Layer 1 | CLAUDE.md (697줄) | `v10_layer1_claude_features.json` (용어 매핑 포함) |
| 2 | 0-C | C-1a | PLAN-3.0 (7,046줄) | `v10_src_C01a_plan.json` |
| 3 | 0-C | C-1b | BASE+MASTER+READINESS×3 (5,291줄) | `v10_src_C01b_base_master_ready.json` |
| 4 | 0-C | C-2 | D2.0-01 (1,857줄) + D2.0-02 (4,474줄) | `v10_src_C02_overview_orange.json` |
| 5 | 0-C | C-3 | D2.0-03 + D2.0-04 + D2.0-05 (5,516줄) | `v10_src_C03_blue_infra_wf.json` |
| 6 | 0-C | C-4 | D2.0-06 + D2.0-07 (5,083줄) | `v10_src_C04_storage_safety.json` |
| 7 | 0-C | C-5 | D2.0-08 (2,696줄) + D2.1-D8 (201줄) | `v10_src_C05_uiux.json` |
| 8 | 0-C | C-6 | D2.1-A1 + D2.1-D1~D7 + D2.1-Q1 (5,414줄) | `v10_src_C06_schema.json` |
| 9 | 0-C | C-7 | PHASE_B1~B7 (9,751줄 ⚠) | `v10_src_C07_phase_b.json` |
| 10 | 0-C | C-8 | AI_INVESTING~SDAR (6,669줄) | `v10_src_C08_spec.json` |
| 11 | 0-C | C-9a | STEP7_A-E + F-I (3,876줄) | `v10_src_C09a_step7_ai.json` |
| 12 | 0-C | C-9b | STEP7_J-M + N-P + 보강 (5,156줄) | `v10_src_C09b_step7_jp.json` |
| 13 | 0-C | C-10 | BEGINNER+CLAUDE.md+PLAN-2.0 (6,891줄) | `v10_src_C10_beginner_claude.json` |
| 14 | 0-D | Delta-1 | Layer 1 + Layer 2 결과 12개 | `v10_layer1_layer2_delta.json` |
| 15 | 0-D | Delta-2 | Delta + 에이전트 결과 | `v10_merged_features.json` |
| 16 | 0-D | Delta-3 | 판단필요 + V_UNKNOWN 목록 | 사용자 판정 결과 반영 |
| 17 | 0-E | V8 재검증 | V8 IMP-B~F + Agent 7 결과 | `v10_v8_revalidation.json` |
| 18 | 0-E | V9 재검증 | V9 SOT매핑 + GT + Phase 1 보고 | `v10_v9_revalidation.json` + `v10_revalidation_report.md` |
| 19 | 0-F | Registry | 0-D + 0-E 통합 | `v10_feature_registry_final.json` |
| 20 | 1 | M-1 | Registry(V0) + PART2 §2 + 용어매핑 | `v10_mapping_M01_v0.json` |
| 21 | 1 | M-2 | Registry(V1) + PART2 §3 + 용어매핑 | `v10_mapping_M02_v1.json` |
| 22 | 1 | M-3 | Registry(V2) + PART2 §4 + 용어매핑 | `v10_mapping_M03_v2.json` |
| 23 | 1 | M-4 | Registry(V3) + PART2 §5 + 용어매핑 | `v10_mapping_M04_v3.json` |
| 24 | 1 | M-5a | Registry(전체) + PART2 §6.1~§6.7 | `v10_mapping_M05a_sys_front.json` |
| 25 | 1 | M-5b | Registry(전체) + PART2 §6.8~§7 | `v10_mapping_M05b_sys_back.json` + `v10_phase1_report.md` |
| 26 | 1.5 | 적대적 | M-1~M-5b 결과 + PART2 | `v10_adversarial_report.md` |
| 27 | 2 | 목록 확정 | 적대적 결과 | `v10_missing_items_list.md` + `v10_part2_patch_plan.md` | ✅ |
| 28 | 2 | PART2 수정 | patch plan + PART2 | PART2 v22.0.0 + 행번호 매핑 테이블 | ✅ |
| 29 | 2 | Step 1/2 분류 | 1,068건 MISSING | `step1/3-1~3-6*.md` (67건 제외, 1,001건 잔여) | ✅ |
| 30 | 2 | 전수 검증 에이전트 | consolidated_missing.json + PART2 v22.0.0 + STEP7 + v10_part2_line_mapping.md | `v10_step2_fullscan.py` + `v10_step2_fullscan.md` + `v10_phase_tbd_resolved.json` (+ 조건부: PART2 패치본 + 행번호 매핑 갱신) | ▶ |
| 31 | 2 | 재검증 에이전트 | PART2 v22+ + v10_part2_line_mapping.md + v10_step2_fullscan.md + v10_phase_tbd_resolved.json + step1/ | `v10_revalidation.md` | ⬜ |
| 32 | CP | 판정 에이전트 | 전체 결과 | `v10_checkpoint.md` + `v10_phase2_final_report.md` | ⬜ |

---

# 16. 입출력 파일 인덱스

## 전체 산출물 목록

| # | 파일명 | Phase | 경로 |
|---|--------|-------|------|
| 1 | `v10_feature_definition.md` | 0-A | `D:\VAMOS\04. 구현단계\v10_results\phase0-a\` |
| 2 | `v10_layer1_claude_features.json` | 0-B | `D:\VAMOS\04. 구현단계\v10_results\phase0-b\` |
| 3 | `v10_src_C01a_plan.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 4 | `v10_src_C01b_base_master_ready.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 5 | `v10_src_C02_overview_orange.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 6 | `v10_src_C03_blue_infra_wf.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 7 | `v10_src_C04_storage_safety.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 8 | `v10_src_C05_uiux.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 9 | `v10_src_C06_schema.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 10 | `v10_src_C07_phase_b.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 11 | `v10_src_C08_spec.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 12 | `v10_src_C09a_step7_ai.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 13 | `v10_src_C09b_step7_jp.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 14 | `v10_src_C10_beginner_claude.json` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 15 | `v10_src_coverage_report.md` | 0-C | `D:\VAMOS\04. 구현단계\v10_results\phase0-c\` |
| 16 | `v10_layer1_layer2_delta.json` | 0-D | `D:\VAMOS\04. 구현단계\v10_results\phase0-d\` |
| 17 | `v10_merged_features.json` | 0-D | `D:\VAMOS\04. 구현단계\v10_results\phase0-d\` |
| 18 | `v10_v8_revalidation.json` | 0-E | `D:\VAMOS\04. 구현단계\v10_results\phase0-e\` |
| 19 | `v10_v9_revalidation.json` | 0-E | `D:\VAMOS\04. 구현단계\v10_results\phase0-e\` |
| 20 | `v10_revalidation_report.md` | 0-E | `D:\VAMOS\04. 구현단계\v10_results\phase0-e\` |
| 21 | `v10_feature_registry_final.json` | 0-F | `D:\VAMOS\04. 구현단계\v10_results\phase0-f\` |
| 22 | `v10_mapping_M01_v0.json` | 1 | `D:\VAMOS\04. 구현단계\v10_results\phase1\` |
| 23 | `v10_mapping_M02_v1.json` | 1 | `D:\VAMOS\04. 구현단계\v10_results\phase1\` |
| 24 | `v10_mapping_M03_v2.json` | 1 | `D:\VAMOS\04. 구현단계\v10_results\phase1\` |
| 25 | `v10_mapping_M04_v3.json` | 1 | `D:\VAMOS\04. 구현단계\v10_results\phase1\` |
| 26 | `v10_mapping_M05a_sys_front.json` | 1 | `D:\VAMOS\04. 구현단계\v10_results\phase1\` |
| 27 | `v10_mapping_M05b_sys_back.json` | 1 | `D:\VAMOS\04. 구현단계\v10_results\phase1\` |
| 28 | `v10_phase1_report.md` | 1 | `D:\VAMOS\04. 구현단계\v10_results\phase1\` |
| 29 | `v10_adversarial_report.md` | 1.5 | `D:\VAMOS\04. 구현단계\v10_results\phase15\` |
| 30 | `v10_missing_items_list.md` | 2 | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| 31 | `v10_part2_patch_plan.md` | 2 | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| 32 | `v10_phase2_final_report.md` | 2 (32) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| 33 | `step1/3-1_NOT_APPLICABLE.md` | 2 (29) | `D:\VAMOS\04. 구현단계\v10_results\phase2\step1\` |
| 34 | `step1/3-2_SUB_FEATURE_OF_EXISTING.md` | 2 (29) | `D:\VAMOS\04. 구현단계\v10_results\phase2\step1\` |
| 35 | `step1/3-3_SKIP_CONFIRMED.md` | 2 (29) | `D:\VAMOS\04. 구현단계\v10_results\phase2\step1\` |
| 36 | `step1/3-4_RESOLVED.md` | 2 (29) | `D:\VAMOS\04. 구현단계\v10_results\phase2\step1\` |
| 37 | `step1/3-5_SECTION6_DETAILED.md` | 2 (29) | `D:\VAMOS\04. 구현단계\v10_results\phase2\step1\` |
| 38 | `step1/3-6_DUPLICATE.md` | 2 (29) | `D:\VAMOS\04. 구현단계\v10_results\phase2\step1\` |
| 39 | `v10_step2_fullscan.py` | 2 (30) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| 40 | `v10_step2_fullscan.md` | 2 (30) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| 41 | `v10_phase_tbd_resolved.json` | 2 (30) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| 42 | `v10_revalidation.md` | 2 (31) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| 43 | `v10_checkpoint.md` | CP | `D:\VAMOS\04. 구현단계\v10_results\` |

### 입력/참조 파일 (산출물 외)

| # | 파일명 | 용도 | 경로 |
|---|--------|------|------|
| R1 | `consolidated_missing.json` | 대화 30 입력 (1,068건) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| R2 | `step2_unclassified_report.md` | 대화 30 입력 (1,001건 상세) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| R3 | `v10_part2_line_mapping.md` | 대화 28/30/31 참조 (행번호 매핑) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| R4 | `v10_part2_patch_plan.md` | 대화 28/30 참조 (패치 계획) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |
| R5 | `reclassify_result.json` | 대화 29 참조 (재분류 결과) | `D:\VAMOS\04. 구현단계\v10_results\phase2\` |

> **총 산출물**: 43개 파일 + 입력/참조 5개 (대화 30에서 PART2 추가 패치 시 산출물 수 증가 가능)

## 참조 파일 요약

| 용도 | 경로 | 비고 |
|------|------|------|
| **SRC (V10 사용 경로)** | `D:\VAMOS\docs\sot\` | **모든 에이전트는 이 경로만 사용** |
| SRC 원본 | `C:\Users\dkscl\OneDrive\...\output\updated\` | 참조 금지 (OneDrive 동기화 리스크) |
| PART2 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` | v22.0.0 (대화 30 이후 버전 범프 가능) |
| V8 결과 | `D:\VAMOS\04. 구현단계\v8_results\` | Phase 0-E 재검증 대상 |
| V9 결과 | `D:\VAMOS\04. 구현단계\v9_results\` | Phase 0-E 재검증 대상 |
| V10 결과 | `D:\VAMOS\04. 구현단계\v10_results\` | 본 파이프라인 산출물 |
