# v13 Phase 0-F: SOT 수정 기록

> **버전**: v13
> **작성일**: 2026-03-18
> **총 수정**: 20건 (CRITICAL 4 + WARNING 16)
> **검증**: 20/20 PASS (100%)

## 수정 목록

| # | 파일 | 행 | before | after | 근거 |
|---|------|-----|--------|-------|------|
| 1 | CLAUDE.md | L92 | `## 6. 모듈 시스템 (81개)` | `## 6. 모듈 시스템 (81개: I25+E16+S8+A7+B6+C7+D6+EVX6)` | INC-001, FIX-001R — 범위 명시로 혼란 해소 |
| 2 | D2.0-03 BLUE_NODES | L766 | `Confidence < 70%` | `Confidence < 50% (MASTER_SPEC §5/§7.9 정본)` | INC-004, FIX-004 — MASTER_SPEC 0.5 기준 통일 |
| 3 | STEP7-K 작업가이드 | L848 | `Confidence < 70%` | `Confidence < 50% (MASTER_SPEC §5/§7.9 정본)` | INC-004 ripple — FIX-004 동일 |
| 4 | STEP7 J-M 상세명세서 | L881 | `Confidence<70%` | `Confidence<50%` | INC-004 ripple — FIX-004 동일 |
| 5 | MASTER_SPEC | L1726 | `NEVER_AUTO: modify_safety_rules, change_cost_ceiling, alter_approval_flow, modify_non_goals, disable_guardrails, bypass_gate` (6개) | `NEVER_AUTO (10개): [7개 불변구역] modify_safety_rules, change_cost_ceiling, alter_approval_flow, modify_non_goals, change_audit_format, alter_data_retention, modify_user_consent / [3개 운영금지] escalate_own_privilege, disable_guardrails, bypass_gate` | INC-006, FIX-006 — SDAR/CLAUDE.md 10개 합의 기준 |
| 6 | MASTER_SPEC | L1729 | `RULE 1.3 7개 불변구역: NEVER_AUTO (frozenset 강제)` | `RULE 1.3 7개 불변구역 + 3개 운영금지(총 10개): NEVER_AUTO (frozenset 강제)` | INC-006 ripple — 카운트 정합성 |
| 7 | PART2 구현단계 | L3199 | `HIGH(94개) → MEDIUM(9개) → LOW(3개)` | `HIGH(94개) → MEDIUM(8개) → LOW(4개)` | INC-007, FIX-007R — 상세 목록 재카운트 결과 |
| 8 | PART2 구현단계 | L3290 | `HIGH(94개) → MEDIUM(9개) → LOW(3개)` | `HIGH(94개) → MEDIUM(8개) → LOW(4개)` | INC-007, FIX-007R — 중복 위치 동일 수정 |
| 9 | MASTER_SPEC | L729 | `## 6.8 10계층 아키텍처` | `## 6.8 10계층 보안 아키텍처 (4-Layer LLM Guardrails §9.1과 별개)` | INC-009, FIX-009 — 용어 구분 명확화 |
| 10 | MASTER_SPEC | L1008 | `## 9.1 4-Layer Guardrails` | `## 9.1 4-Layer LLM Guardrails (10계층 보안 아키텍처 §6.8과 별개)` | INC-009 ripple — 양방향 교차 참조 |
| 11 | D2.0-06 STORAGE | L177 | `top_k 기본값: **10** (config.toml ...)` | `top_k 기본값: **10** (config.toml ..., API 레이어 B1은 top_k=5 기본)` | INC-011, FIX-011 — 교차 참조 주석 |
| 12 | B2 PROJECT_STRUCTURE | L334 | `I-1: Intent Parser — 의도 해석` | `I-1: Intent Detector — 의도 해석 (대화 이해/추론)` | INC-014, FIX-014 — MASTER_SPEC 정본 명칭 |
| 13 | B2 PROJECT_STRUCTURE | L353 | `I-5: Gate Evaluator — 게이트 평가/라우팅` | `I-5: Condition & Decision Engine — 게이트 평가/라우팅` | INC-015, FIX-015 — MASTER_SPEC 정본 명칭 |
| 14 | D2.0-01 OVERVIEW | L1011 | `I-1 Intent Parser\nIntentFrame 생성` | `I-1 Intent Detector\nIntentFrame 생성` | INC-014 ripple — Mermaid 다이어그램 |
| 15 | B5 TEST_STRATEGY | L127 | `Decision Kernel, Intent Parser` | `Decision Kernel, Intent Detector` | INC-014 ripple — 테스트 섹션 제목 |
| 16 | AGENT_TEAMS_SPEC | L505 | `I-1 Intent Parser` | `I-1 Intent Detector` | INC-014 ripple — 팀 구성 흐름도 |
| 17 | PLAN-3.0 | L806 | `ERROR = **#FF4D4D**` | `ERROR = **#EF4444**` | INC-013, FIX-013 — Tailwind red-500 표준 통일 |
| 18 | PLAN-3.0 | L808 | `COST = **#FACC15**` | `COST = **#FBBF24**` | INC-012, FIX-012 — Tailwind amber-400 표준 통일 |

## 적대적 검증으로 철회된 수정 (3건)

| 원래 FIX | INC | 철회 사유 |
|----------|-----|----------|
| FIX-002 (ADD_MAPPING) | INC-002 | FP — Series/Priority/Layer는 직교 분류 체계 |
| FIX-003 (ADD_CLARIFICATION) | INC-003 | FP — QoD 0.7 출력보류는 양쪽 일치, 0.4는 별개 기능 |
| FIX-005 (ADD_CLARIFICATION) | INC-005 | 문서가 이미 갭 인정, 인덱스 수 변경은 추적성 상실 |

## 보류 → 완료 (2건, 대화 7에서 처리)

| # | 파일 | 행 | before | after | 근거 |
|---|------|-----|--------|-------|------|
| 19 | MASTER_SPEC | L167 | (CORE 범위 명시 없음) | `> CORE 모듈 범위 (26개): I(17)+E(6)+S(1)+A(2)=26. P0 16개와 구분` | INC-008, FIX-008 — CORE vs P0 범위 혼동 방지 |
| 20 | MASTER_SPEC | L170,L194-198 | `I-Series (I-1~I-24)`, I-21/22/23/25 누락 | `I-Series (I-1~I-25)`, I-21~I-25 전수 추가 (COND 5개: I-7,I-12,I-22,I-23,I-25) | INC-010, FIX-010 — CLAUDE.md와 COND 모듈 수 일치 |

## 수정 대상 파일 요약

| 파일 | 수정 수 |
|------|---------|
| VAMOS_MASTER_SPECIFICATION.md | 4건 (L729, L1008, L1726, L1729) |
| PHASE_B2_PROJECT_STRUCTURE.md | 2건 (L334, L353) |
| PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | 2건 (L806, L808) |
| VAMOS_구현가이드_PART2_구현단계.md | 2건 (L3199, L3290) |
| D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md | 1건 (L766) |
| STEP7-K_에이전트프로토콜_상호운용성_작업가이드.md | 1건 (L848) |
| VAMOS_STEP7_J-M_상세명세서.md | 1건 (L881) |
| CLAUDE.md | 1건 (L92) |
| D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | 1건 (L177) |
| D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md | 1건 (L1011) |
| PHASE_B5_TEST_STRATEGY.md | 1건 (L127) |
| VAMOS_AGENT_TEAMS_SPEC.md | 1건 (L505) |

## 백업 파일 위치

`D:\VAMOS\04. 구현단계\v13_results\phase0\fixes\*_backup_v13.md` (11개 파일)
