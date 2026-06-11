# VAMOS AI 통합 상세 명세서 (Master Specification)

> **버전**: v1.0.0 | **생성일**: 2026-02-22
> **소스**: D2.0-01~08, D2.1-D1~D8/A1/Q1, BASE-1.3, PLAN-3.0, PHASE_B1~B7
> **목적**: 구현 착수 전 VAMOS AI의 모든 흐름·구조·기능·규칙을 빠짐없이 정리한 단일 참조 문서

---

## 목차

1. [VAMOS 정체성 & 철학](#1-vamos-정체성--철학)
2. [전체 아키텍처](#2-전체-아키텍처)
3. [문서 우선순위 & 버전 규칙](#3-문서-우선순위--버전-규칙)
4. [ORANGE CORE (판단/제어 엔진)](#4-orange-core-판단제어-엔진)
5. [BLUE NODES (도메인 실행 모듈)](#5-blue-nodes-도메인-실행-모듈)
6. [INFRA CORE (인프라 계층)](#6-infra-core-인프라-계층)
7. [AGENT WORKFLOW (워크플로우 파이프라인)](#7-agent-workflow-워크플로우-파이프라인)
8. [STORAGE & MEMORY (저장/메모리)](#8-storage--memory-저장메모리)
9. [SAFETY, COST & APPROVAL (안전/비용/승인)](#9-safety-cost--approval-안전비용승인)
10. [UI/UX (사용자 인터페이스)](#10-uiux-사용자-인터페이스)
11. [자기진화 (Self-Evolution)](#11-자기진화-self-evolution)
12. [스키마 & 레지스트리 (전체)](#12-스키마--레지스트리-전체)
13. [API 계약 (88 엔드포인트)](#13-api-계약-88-엔드포인트)
14. [프로젝트 구조 (Monorepo)](#14-프로젝트-구조-monorepo)
15. [기술 스택 (Tech Combo)](#15-기술-스택-tech-combo)
16. [버전 로드맵 (V0→V3)](#16-버전-로드맵-v0v3)
17. [전체 LOCK 결정사항](#17-전체-lock-결정사항)

---

## 0. 산출물 전체 인덱스 (39개 파일)

> **구현단계 추적성 보장**: 이 테이블은 모든 산출물 파일의 역할, 분류, 구현 버전별 참조 시점을 정의한다.
> 구현 착수 전 이 인덱스를 기준으로 필요 파일을 확인하라.

| # | 파일명 | 분류 | 역할 요약 | 줄 수 | V0 | V1 | V2 | V3 | 비고 |
|---|--------|------|----------|-------|----|----|----|----|------|
| 1 | BASE-1.3_VAMOS_RULE_1.3_BASE.md | RULE | 절대 상위 규칙 (Identity/Safety/Policy/비용상한/Non-goal) | 633 | 필수 | 필수 | 필수 | 필수 | 위반 시 무효 |
| 2 | PLAN-2.0_VAMOS_PLAN_2.0_.md | PLAN | (SUPERSEDED) 이전 로드맵/비용/버전 정본 | 4350 | - | - | - | - | PLAN-3.0으로 전면 대체, 히스토리 참조만 |
| 3 | PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | PLAN | 로드맵/비용/버전 정본 (SOT) | 6948 | 필수 | 필수 | 필수 | 필수 | 모든 비용상한/버전정의/모듈목록 정본 |
| 4 | D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md | DESIGN | 통합 개요/연결 허브/레지스트리/다이어그램 | 1718 | 필수 | 필수 | 필수 | 필수 | LOCK 우선, 모듈 카탈로그 §5.6~5.13 |
| 5 | D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md | DESIGN | ORANGE CORE 판단/제어 엔진 (I-1~I-21 상세설계) | 4230 | 필수 | 필수 | 필수 | 필수 | LOCK 우선, I-Series 핵심 |
| 6 | D2.0-03_03. VAMOS_DESIGN_2.0_BLUE_NODES.md | DESIGN | BLUE NODES 도메인 실행 모듈 (P0/P1/P2) | 1935 | 필수 | 필수 | 필수 | 필수 | LOCK 우선, MCP/Tool 계층 |
| 7 | D2.0-04_04. VAMOS_DESIGN_2.0_INFRA_CORE.md | DESIGN | 인프라 계층 (Brain Adapter/HAL/Tool실행) | 1588 | 필수 | 필수 | 필수 | 필수 | LOCK 우선, 모델라우팅/배포 |
| 8 | D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md | DESIGN | Agent/Workflow 파이프라인 (5단계+상태전이) | 1971 | 필수 | 필수 | 필수 | 필수 | LOCK 우선, Fallback/Retry |
| 9 | D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md | DESIGN | 저장/메모리 계층 (L0~L3/RAG/마스킹) | 2414 | 필수 | 필수 | 필수 | 필수 | LOCK 우선, 메모리 정책 |
| 10 | D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md | DESIGN | 안전/비용/승인 정책 (Guardrails/RBAC) | 2605 | 필수 | 필수 | 필수 | 필수 | LOCK 우선, 비용상한/승인게이트 |
| 11 | D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md | DESIGN | UI/UX 설계 (Builder/Hologram/3패널) | 2480 | 필수 | 필수 | 필수 | 필수 | LOCK 우선, 멀티모달 UI |
| 12 | D2.1-A1_A1_TECH_STACK.md | SCHEMA | 기술 스택 정본 (V1/V2/V3 Combo) | 401 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스 |
| 13 | D2.1-D1_D1_SCHEMA_GLOSSARY.md | SCHEMA | 스키마 용어집/공통 타입 정의 | 352 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스 |
| 14 | D2.1-D2_D2_SCHEMA_ORANGE_CORE.md | SCHEMA | ORANGE CORE JSON Schema (Decision/LogEvent) | 424 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스, I-Series 핵심 |
| 15 | D2.1-D3_D3_SCHEMA_BLUE_NODES.md | SCHEMA | BLUE NODES JSON Schema (Node/MCP/CloudLib) | 756 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스 |
| 16 | D2.1-D4_D4_SCHEMA_INFRA_CORE.md | SCHEMA | INFRA CORE JSON Schema (Brain/Tool/HAL) | 515 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스 |
| 17 | D2.1-D5_D5_SCHEMA_AGENT_WORKFLOW.md | SCHEMA | AGENT WORKFLOW JSON Schema (Pipeline/State) | 635 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스 |
| 18 | D2.1-D6_D6_SCHEMA_STORAGE_MEMORY.md | SCHEMA | STORAGE/MEMORY JSON Schema (Memory/RAG) | 393 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스 |
| 19 | D2.1-D7_D7_SCHEMA_SAFETY_COST_APPROVAL.md | SCHEMA | SAFETY/COST/APPROVAL JSON Schema | 593 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스 |
| 20 | D2.1-D8_D8_SCHEMA_UI_UX.md | SCHEMA | UI/UX JSON Schema (Event/Theme/Layout) | 181 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스 |
| 21 | D2.1-Q1_Q1_AUDIT_REPORT.md | SCHEMA | 감사 보고서 (문서간 정합성 검증) | 1172 | 필수 | 필수 | 필수 | 필수 | 코드 생성 소스, 정합성 체크 |
| 22 | PHASE_B1_API_CONTRACT.md | PHASE | API 계약 (Tauri IPC/Python-Rust/MCP 88개) | 2218 | 필수 | 필수 | 참고 | 참고 | 구현 직접 가이드 |
| 23 | PHASE_B2_PROJECT_STRUCTURE.md | PHASE | 프로젝트 구조 (Monorepo 디렉토리 레이아웃) | 886 | 필수 | 필수 | 참고 | 참고 | 구현 직접 가이드 |
| 24 | PHASE_B3_DEPENDENCIES.md | PHASE | 의존성 관리 (패키지/버전 정책) | 356 | 필수 | 필수 | 참고 | 참고 | 구현 직접 가이드 |
| 25 | PHASE_B4_CONFIG_SPEC.md | PHASE | 설정 명세 (환경변수/Config 구조) | 1170 | 필수 | 필수 | 참고 | 참고 | 구현 직접 가이드 |
| 26 | PHASE_B5_TEST_STRATEGY.md | PHASE | 테스트 전략 (단위/통합/E2E) | 945 | 필수 | 필수 | 참고 | 참고 | 구현 직접 가이드 |
| 27 | PHASE_B6_CICD_PIPELINE.md | PHASE | CI/CD 파이프라인 설계 | 1735 | 필수 | 필수 | 참고 | 참고 | 구현 직접 가이드 |
| 28 | PHASE_B7_MIGRATION_STRATEGY.md | PHASE | 마이그레이션 전략 (V1->V2->V3) | 2308 | 필수 | 필수 | 참고 | 참고 | 구현 직접 가이드 |
| 29 | VAMOS_MASTER_SPECIFICATION.md | SPEC | 통합 요약 (본 문서) | 1841 | 필수 | 필수 | 필수 | 필수 | 전체 흐름/구조/규칙 단일 참조 |
| 30 | VAMOS_STEP7_A-E_상세명세서.md | STEP7 | STEP7 A~E 카테고리 상세명세 | 1000 | 참고 | 참고 | 필수 | 필수 | 놓치지 말 것, AI기술보강 |
| 31 | VAMOS_STEP7_F-I_상세명세서.md | STEP7 | STEP7 F~I 카테고리 상세명세 | 2867 | 참고 | 참고 | 필수 | 필수 | 놓치지 말 것, AI기술보강 |
| 32 | VAMOS_STEP7_J-M_상세명세서.md | STEP7 | STEP7 J~M 카테고리 상세명세 | 1822 | 참고 | 참고 | 필수 | 필수 | 놓치지 말 것, AI기술보강 |
| 33 | VAMOS_STEP7_N-P_보강_상세명세서.md | STEP7 | STEP7 N~P + 보강 상세명세 | 1807 | 참고 | 참고 | 필수 | 필수 | 놓치지 말 것, AI기술보강 |
| 34 | VAMOS_STEP7_보강_통합명세서.md | STEP7 | TITLE_ONLY 448건 상세 확장 | 1523 | - | 참고 | 필수 | 필수 | TITLE_ONLY 항목 보강 |
| 35 | VAMOS_AI_INVESTING_SPEC.md | SPEC | AI 투자 도메인 통합 명세 | 1415 | - | - | 필수 | 필수 | P1 투자 도메인 |
| 36 | VAMOS_CLOUD_LIBRARY_SPEC.md | SPEC | Cloud Library System 통합 상세 명세 | 1439 | - | - | 필수 | 필수 | E-15/S-5 클라우드 라이브러리 |
| 37 | VAMOS_AGENT_TEAMS_SPEC.md | SPEC | Agent Teams 통합 설계 명세 (에이전트 팀 위임) | 2192 | - | - | 필수 | 필수 | 멀티에이전트 아키텍처 |
| 38 | VAMOS_SDAR_DESIGN_SPECIFICATION.md | SPEC | I-25 SDAR 자가진단·자동복구 설계 명세 | 1647 | - | - | 참고 | 필수 | Self-Diagnosis & Auto-Repair |
| 39 | VAMOS_BEGINNER_GUIDE.md | GUIDE | 초보자 온보딩/사용자 가이드 | 1853 | - | 참고 | 참고 | 참고 | 비개발자 대상 안내 문서 |

> **분류 범례**: RULE=절대규칙, PLAN=로드맵/계획, DESIGN=아키텍처/모듈설계(01~08), SCHEMA=JSON Schema/타입(D1~D8/A1/Q1), PHASE=구현직접가이드(B1~B7), SPEC=통합명세, STEP7=AI기술보강 상세, GUIDE=사용자안내
> **참조 수준**: 필수=반드시 읽고 준수, 참고=필요시 참조, -=해당 버전에서 불필요

---

# 1. VAMOS 정체성 & 철학

## 1.1 I AM 정의
VAMOS는 사용자의 지능적 결정을 돕는 **개인 맞춤형 AI 보조 지능**이며, **궁극적으로 AGI 수준의 구조를 지향**한다.

## 1.2 핵심 철학 (6대 원칙)
1. **사용자 중심/개인 맞춤형** 원칙
2. **정확성/근거 기반 출력** (환각 최소화, RAG + Self-check)
3. **최신성 확보** (RAG, 외부 API, 개인 문서)
4. **장기 맥락 유지** & 프로젝트별 독립성 보장
5. **다중 의도/대화 메타인지**
6. **구조적/모듈화 지능**

## 1.3 14대 목표

### A. 지능/정확도/대화 이해 (5개)
| # | 목표 |
|---|------|
| 1 | 정확도/신뢰성 개선 (환각 최소화, RAG + Self-check) |
| 2 | 최신성/지식 갱신 (RAG, API, 개인 문서) |
| 3 | 장기 맥락/기억 (Long-term Memory) |
| 4 | 고급 대화 분석 & 다중 의도 처리 |
| 5 | 대화 메타인지 / 자기-대화 분석 |

### B. 구조/아키텍처/모듈 (4개)
| # | 목표 |
|---|------|
| 6 | 테마 기반 모듈 구조 (행동 모듈화) |
| 7 | 도메인/부도메인 확장성 + 자동 생성 |
| 8 | LLM + 다른 뇌 + LLM 구조 |
| 9 | 멀티-테마/멀티-도메인 복합 작업 처리 |

### C. 코딩/리서치/생산성/부수입 (3개)
| # | 목표 |
|---|------|
| 10 | 코딩 능력 극대화 |
| 11 | 리서치/문서/데이터 분석 자동화 |
| 12 | 생산성/부수입 지원 |

### D. 자기진화/안전/비용 (2개)
| # | 목표 |
|---|------|
| 13 | Self-Evolving AI (자기진단 + 자기개선) |
| 14 | 안전/비용/운영 효율 최적화 |

## 1.4 Non-goal 전체 목록 (7개, 절대 금지)

| # | Non-goal | 위반 시 대응 |
|---|----------|-------------|
| 2.1 | 실거래/주문/계좌/API 연동 | 즉시 거부. 분석 보조만 가능 |
| 2.2 | 불법 행위/해킹/권한 상승 | 즉시 차단. 법적 책임 고지 |
| 2.3 | 의료/법률 단정적 판단 또는 대리 결정 | 단정 금지. "전문가 상담 필요" + 참고정보만 |
| 2.4 | 민감 개인정보 장기 저장 | 저장 거부. 세션 내 임시 사용 후 즉시 파기 |
| 2.5 | 저작권/약관 위반 | 거부. 합법적 접근 방법 안내 |
| 2.6 | P2 도메인 자동 생성 금지 | 활성화 전 반드시 명시적 승인 요청 |
| 2.7 | 위험 기능 자동 실행 금지 | HITL 승인 없이 실행 불가 |

## 1.5 성공 기준 (우선순위)
1. 정확성/근거 > 2. 이해도/품질 > 3. 안전/규제 > 4. 속도/효율 > 5. 비용

---

# 2. 전체 아키텍처

## 2.1 처리 흐름 (AGI 구조)
```
Front Mini LLM (의도/보안/도메인 판별)
  → ORANGE CORE (정책/룰/비용/라우팅/안전)
    → BLUE NODE (도메인 전용 실행 스택)
      → OTHER BRAINS (검색/RAG/DB/API/코드실행/분석엔진)
        → Main/Hologram LLM (최종 출력/시각화/보고서)
```

## 2.2 4계층 역할 분담

| 계층 | 역할 | 정본 |
|------|------|------|
| **Front Mini LLM** | 요청 해석, 도메인/의도 판별, 안전 필터링, TASK 구조화 | 02 |
| **ORANGE CORE** | 정책/룰/비용 관리, Self-check/Self-evo 판단, 메모리 규칙/저장 계층 제어, 도메인/모델 라우팅, 실행 승인/위험 관리 | 02 |
| **BLUE NODE** | 트레이딩/코딩/리서치/생산성 등 목적별 소형 AGI 스택. 도메인 템플릿/메모리/정책 포함. CORE 지시에 따라 실행 | 03 |
| **OTHER BRAINS** | 벡터/RAG, DB, 크롤러, 외부 API, 코드 실행기, 분석 엔진 | 04 |

## 2.3 내부(I)/외부(E)/자기진화(S) 기능 분류

> **CORE 모듈 범위 (26개)**: I/E/S/A 시리즈에서 status="CORE"인 모듈 — I(17)+E(6)+S(1)+A(2)=26.
> P0 도메인(16개, §5.2 BLUE NODES)과는 다른 분류 축임. CORE=시스템 기능 상태 분류, P0=도메인 우선순위 분류.

### I-Series (I-1~I-25) 내부 기능

> **확장 시리즈 참조**: I/E/S/A 외에 B-Series(Memory/Skill/Self-evo), C-Series(Verifier/Reasoning), D-Series(Brain/Planner/RAG), EVX-Series(검증체인) 총 25개 추가 모듈이 CLAUDE.md §6에 정의. 전체 합산 81개(I25+E16+S8+A7+B6+C7+D6+EVX6).

| ID | 명칭 | status | change_lock | V1 | V2 | V3 |
|---|---|---|---|---|---|---|
| I-1 | Intent Detector (대화 이해/추론) | CORE | false | ON | ON | ON |
| I-2 | Context Builder (RAG/지식 검색) | CORE | false | ON | ON | ON |
| I-3 | Memory System (4계층(L0~L3)) | CORE | false | ON | ON | ON |
| I-4 | Multimodal Interpreter | CORE | false | ON | ON | ON |
| I-5 | Condition & Decision Engine | CORE | **true** | ON | ON | ON |
| I-6 | Self-check Engine | CORE | false | ON | ON | ON |
| I-7 | Project/Session Manager | COND | false | OFF | COND | ON |
| I-8 | Policy Engine | CORE | **true** | ON | ON | ON |
| I-9 | Cost Manager | CORE | **true** | ON | ON | ON |
| I-10 | Tool Registry/Router | CORE | false | ON | ON | ON |
| I-11 | Output Composer | CORE | false | ON | ON | ON |
| I-12 | Workflow Builder | COND | false | OFF | COND | ON |
| I-13 | Multimodal Output Renderer | CORE | false | ON | ON | ON |
| I-14 | Summarizer & Memory Distiller | CORE | false | ON | ON | ON |
| I-15 | Evidence & QoD Manager | CORE | false | ON | ON | ON |
| I-16 | Knowledge Search Engine | CORE | false | ON | ON | ON |
| I-17 | Blue Node Manager | CORE | false | ON | ON | ON |
| I-18 | Self-evo Engine | EXP | false | OFF | OFF | ON |
| I-19 | Approval Manager | CORE | **true** | ON | ON | ON |
| I-20 | Failure/Fallback Manager | CORE | false | ON | ON | ON |
| I-21 | Source Evolution | EXP | false | OFF | OFF | ON |
| I-22 | Task/Project Manager | COND | false | OFF | COND | ON |
| I-23 | Doc/Code Structuring | COND | false | OFF | COND | ON |
| I-24 | Knowledge Graph Engine | EXP | false | OFF | OFF | ON |
| I-25 | SDAR Engine (자가진단/수리) | COND | false | OFF | COND | ON |

### E-Series (E-1~E-16) 외부 기능

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| E-1 | Coding & System Design Helper | CORE | ON | ON | ON |
| E-2 | Web Search | CORE | ON | ON | ON |
| E-3 | Document Parser | CORE | ON | ON | ON |
| E-4 | Code Executor | CORE | ON | ON | ON |
| E-5 | Image Analyzer | CORE | ON | ON | ON |
| E-6 | Z3 Solver | CORE | ON | ON | ON |
| E-7 | Speech-to-Text | EXP | OFF | OFF | ON |
| E-8 | Text-to-Speech | EXP | OFF | OFF | ON |
| E-9 | Video Analyzer | EXP | OFF | OFF | ON |
| E-10 | External API Gateway | EXP | OFF | OFF | ON |
| E-11 | Browser Automation | EXP | OFF | OFF | ON |
| E-12 | DB Connector | EXP | OFF | OFF | ON |
| E-13 | Calendar/Task Sync | RE-ADD | OFF | COND | ON |
| E-14 | Email Handler | RE-ADD | OFF | COND | ON |
| E-15 | File System Access | RE-ADD | OFF | COND | ON |
| E-16 | Cloud Storage Sync | RE-ADD | OFF | COND | ON |

### S-Series (S-1~S-8) 자기진화

| ID | 명칭 | status | V1 | V2 | V3 | I-모듈 연결 |
|---|---|---|---|---|---|---|
| S-1 | Self-check Engine | CORE | ON | ON | ON | I-6, I-15 |
| S-2 | Benchmark QA Suite | EXP | OFF | OFF | ON | I-24 |
| S-3 | Template Evolution | EXP | OFF | OFF | ON | I-12, I-18 |
| S-4 | Error Pattern Miner | EXP | OFF | OFF | ON | I-20, I-18 |
| S-5 | Router Evolution | EXP | OFF | OFF | ON | I-10, I-18 |
| S-6 | Search Evolution | EXP | OFF | OFF | ON | I-16, I-18 |
| S-7 | User-Coop Designer | EXP | OFF | OFF | ON | I-19, I-18 |
| S-8 | Self-evo Governance | COND | OFF | OFF | ON | I-19, I-8, I-9, I-24 |

### A-Series (A-1~A-7) 아키텍처 확장

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| A-1 | MultiBrain Adapter | CORE | ON | ON | ON |
| A-2 | Preset Modularization | CORE | ON | ON | ON |
| A-3 | Meta AI | EXP | OFF | OFF | ON |
| A-4 | Debate Mode | COND | OFF | COND | ON |
| A-5 | Lazy Generation | EXP | OFF | OFF | ON |
| A-6 | Federated Module Network | EXP | OFF | OFF | ON |
| A-7 | Remote Executor | EXP | OFF | OFF | ON |

## 2.4 파이프라인 명칭 매핑표 (정본)

| 02 ORANGE CORE | 05 WORKFLOW | 08 UI/UX | 상태 코드 |
|---|---|---|---|
| Perception | Intake | RECEIVED→INTENT | S0_RECEIVED → S1_INTENT_PARSED |
| Reasoning | Plan | EVIDENCE→DECISION | S2_EVIDENCE_READY → S3_DECISION_LOCKED |
| Action | Execute | EXEC | S4_EXECUTING → S5_OUTPUT_READY |
| Memory | Store/Commit | MEMORY | S7_MEMORY_COMMITTED |
| Reflection | Verify | SELF-CHECK→DONE | S6_SELF_CHECKED → S8_DONE |

---

# 3. 문서 우선순위 & 버전 규칙

## 3.1 문서 우선순위 (LOCK)
```
RULE 1.3 (절대규칙) > PLAN 3.0 (상위원칙) > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK
```
충돌 시: 상위 번호가 하위를 override.

## 3.2 네이밍 규칙 (LOCK)

| 유형 | 형식 | 예시 |
|------|------|------|
| event_type | lower.dot.case | `oc.i1.intent.parsed` |
| failure_code | UPPER_SNAKE | `OC_I1_PARSE_FAIL` |
| fallback_id | FB_UPPER_SNAKE | `FB_ASK_CLARIFICATION` |
| trace_id | UUID v4 | `550e8400-e29b-41d4-a716-...` |
| decision_id | `dec_{uuid}` | `dec_550e8400...` |
| node_id | `{domain}_{name}` | `dev_coder_v1` |
| 상태(State) | `S#_DESCRIPTION` | `S0_RECEIVED` |
| 모듈 ID | `S-#` (하이픈) | `S-1` (Self-check Engine) |

## 3.3 변경관리 규칙 (LOCK)
1. **삭제 금지**: 모든 변경은 `[DEPRECATE] + (대체 경로)` 로만 처리
2. **없는 내용 창작 금지**: 신규 정책 임의 생성 불가
3. **Major 변경**: 07 Approval Gate 승인 필수
4. **표기 규칙 변경**: 충돌 해결 규칙 + 마이그레이션 표에 기록

---

# 4. ORANGE CORE (판단/제어 엔진)

## 4.1 5-Phase 파이프라인 (I-1 ~ I-5)

### I-1. Intent Understanding (대화 이해/추론) — 완전 확정

**목적**: 사용자 입력을 의도/도메인/제약/출력 형식으로 구조화

**입력**:
- `user_input.text` (required)
- `user_input.attachments_meta` (optional)
- `session_context` (optional; L0 요약)
- `project_context_hint` (optional)

**출력**: IntentFrame

**상태 전이**: `I1_S0_RAW → I1_S1_PARSING → (I1_S2_AMBIGUOUS | I1_S3_READY) → I1_S4_EMITTED`

**정책 Hooks**:
- `PC_SAFETY_CLASSIFY`: safety_sensitive / approval_maybe_required flag 계산
- `PC_P2_DOMAIN_HINT`: P2 후보 감지 시 I-5 라우팅에서 재확인 트리거

**이벤트**: `oc.i1.parse.started`, `oc.i1.intent.parsed`, `oc.i1.intent.ambiguous`, `oc.i1.parse.failed`

**실패/폴백**: `OC_I1_PARSE_FAIL` → `FB_INTENT_HEURISTIC_PARSE` / `OC_I1_AMBIGUOUS_UNRESOLVED` → `FB_ASK_CLARIFICATION` (질문 1~3개)

**인터페이스**: `parse_intent(user_input, session_context, project_hint) → IntentFrame`

### I-2. RAG & Evidence Retrieval (RAG/지식 검색) — 완전 확정

**목적**: 내부/외부 소스에서 근거(Evidence) 수집/정리하여 단정/환각 방지

**입력**: IntentFrame, allowed_sources_policy (07), time_constraints, project_assets_hint

**출력**: EvidencePack

**상태 전이**: `I2_S0_READY → I2_S1_QUERY_BUILT → I2_S2_FETCHING → (I2_S3_PACK_READY | I2_S4_INSUFFICIENT | I2_S5_BLOCKED)`

**정책 Hooks**: `PC_SOURCE_ALLOWED`, `PC_QOD_THRESHOLD`, `PC_RECENCY_REQUIRED`

**실패/폴백**:
- `OC_I2_RAG_NO_SOURCE` → `FB_RAG_RETRY_EXPAND` (검색 확장, 최대 2~3회)
- `OC_I2_EVIDENCE_QOD_LOW` → `FB_RAG_SWITCH_SOURCE`
- `OC_I2_SOURCE_POLICY_BLOCK` → `FB_RAG_SWITCH_SOURCE`
- `OC_I2_TIMEOUT` → `FB_RAG_RETRY_EXPAND`

**인터페이스**: `build_queries(intent_frame) → query_bundle` / `retrieve_evidence(query_bundle, policy_ctx) → EvidencePack`

### I-3. Memory Orchestration (메모리 4계층(L0~L3)) — 완전 확정

**목적**: 무엇을/언제/어디에(L0/L1/L2)/승인 필요 여부 결정, 저장 실행 트리거

**출력**: `MemoryCommitRequest { commit_id, trace_id, target_layer, payload_ref, requires_user_approval, commit_mode(full|summary|meta_only), deny_reason }`

**상태 전이**: `I3_S0_PLAN_CREATED → (I3_S1_WAIT_APPROVAL | I3_S2_COMMITTING | I3_S4_DENY) → I3_S3_DONE`

**실패/폴백**: `OC_I3_MEMORY_POLICY_DENY` → `FB_MEMORY_META_ONLY` / `OC_I3_APPROVAL_REQUIRED` → `FB_REQUIRE_APPROVAL`

### I-4. Output Structuring (구조화/분석 엔진) — 완전 확정

**목적**: 실행 결과를 사용자 요구 포맷에 맞춘 구조화 산출물로 변환

**출력**: `StructuredOutput { artifact_type, content, compliance_report { output_spec_ok, citations_ok, safety_mask_applied, missing_parts[] }, artifact_meta }`

**상태 전이**: `I4_S0_RAW → I4_S1_STRUCTURING → (I4_S2_READY | I4_S3_SPEC_VIOLATION | I4_S4_MASKED)`

**실패/폴백**: `OC_I4_OUTPUT_SPEC_VIOLATION` → `FB_OUTPUT_REFORMAT` / `OC_I4_MASK_FAIL` → `FB_OUTPUT_MINIMAL`

### I-5. Routing & Decision Kernel — 완전 확정

**목적**: IntentFrame + EvidencePack + Policy/Approval/Cost 조건 종합하여 Decision 생성 + `locked=true` 고정

**상태 전이**: `I5_S0_READY → I5_S1_GATES_EVAL → I5_S2_ROUTE_SELECTED → (I5_S3_DECISION_LOCKED | I5_S4_WAIT_APPROVAL | I5_S5_DENY)`

**게이트 우선순위 (확정)**:
1. **Policy Gate (최우선)**: block > require_approval > mask > allow
2. **Cost Gate**: 예산 초과 위험이면 downshift/split/stop
3. **Evidence Gate**: insufficient/QoD 미달이면 HOLD/ESCALATE + 재검색 루프

**인터페이스**: `evaluate_gates()` → `select_route()` → `lock_decision()` → Decision

## 4.2 IntentFrame 스키마

```python
class IntentFrame:
    intent_id: str
    trace_id: str
    timestamp: str  # ISO8601
    user_goal: str
    task_type: Literal["explain","plan","code","research","summarize","design","debug",...]
    domain_hint: str  # P0|P1|P2 + 후보 리스트
    constraints:
        format_constraints: str
        must_include: List[str]
        must_not_include: List[str]
    risk_flags:
        safety_sensitive: bool
        approval_maybe_required: bool
        cost_sensitive: bool
    ambiguity:
        is_ambiguous: bool
        missing_slots: List[str]  # 0..N
        clarification_questions: List[str]  # 0..3
    required_artifacts: List[str]  # doc|pdf|ppt|sheet|code|diagram
    # 확장 필드
    query: str                    # 원본 질문
    domain: Literal["trading","coding","research","general"]
    intent_type: Literal["analysis","action","query","chat"]
    complexity: Literal["simple","moderate","complex"]
    risk_level: Literal["P0","P1","P2"]
    required_tools: List[str]
    confidence: float             # 0~1 (< 0.5 시 HITL)
    sub_intents: List[str]
```

## 4.3 EvidencePack 스키마

```python
class EvidencePack:
    evidence_pack_id: str
    trace_id: str
    timestamp: str  # ISO8601
    items: List[EvidenceItem]
        # source_type: memory|doc|web|code|log|tool
        # source_ref: str
        # excerpt_or_summary: str
        # qod_score: float (0~1)
        # captured_at / recency_hint: str
    coverage:
        sufficient: bool
        gaps: List[str]
    citations_ready: bool
```

## 4.4 Decision 스키마 (16필드, FREEZE)

```python
class Decision:
    decision_id: str              # 고유
    trace_id: str
    timestamp: str                # ISO8601
    intent_frame_ref: str         # I-1 결과 참조
    evidence_pack_ref: str        # I-2 결과 참조
    policy_gate: Literal["deny","restrict","allow"]
    approval_required: bool
    approval_status: Literal["approved","denied"]  # D7 정본 2값 (PL-09 FIX). pending은 approval_required=True 상태로 표현
    cost_gate: Literal["normal","downshift","split","stop"]
    routing:
        selected_blue_node_id: str
        execution_mode: Literal["mini","main","tool"]
    memory_plan:
        save_candidate: bool
        target_layer: Literal["L0","L1","L2","L3"]
        requires_user_approval: bool
    output_spec:
        format_constraints: str
    conclusion: Literal["ACCEPT","REJECT","HOLD","ESCALATE"]
    locked: bool = True           # 단일결정 원칙
    # 확장 필드
    optional_signals: List[dict]  # signal_id, source, name, value, confidence
    verify: dict                  # chain_used, refs
    gates: dict                   # result (policy/approval/cost/evidence)
    s_module_hints: dict          # source_s_module, hint_type, suggestion
```

## 4.5 상태 머신 (S0~S8)

```
S0_RECEIVED → S1_INTENT_PARSED (I-1)
  → S2_EVIDENCE_READY (I-2)
    → S3_DECISION_LOCKED (I-5)
      → S4_EXECUTING (BLUE NODE)
        → S5_OUTPUT_READY (I-4)
          → S6_SELF_CHECKED (I-6)
            → S7_MEMORY_COMMITTED (I-3)
              → S8_DONE
```

**상태별 타임아웃**: S1=5초, S2=30초, S3=120초, S4=10초, S5=15초

**핵심 규칙**: S3(Decision Locked) 이후 결론 변경 불가 (단일결정 원칙)

## 4.6 Gate 시스템 상세

| Gate | 위치 | 결과 | 실패 시 |
|------|------|------|--------|
| **PolicyGate** | S1~S3, S6 재검증 | block/require_approval/mask/allow | deny + 감사로그 |
| **CostGate** | S2~S3, S4 모니터링 | normal/downshift/split/stop | FB_COST_DOWNSHIFT |
| **ApprovalGate** | S1~S3 | approved/denied (D7 정본 2값) | FB_REQUIRE_APPROVAL |
| **EvidenceGate** | S2 | sufficient/insufficient | HOLD/ESCALATE + 재검색 |
| **SelfCheckGate** | S5→S6 | PASS/WARN/FAIL | Soft loop 1회 → 승인/deny |

**Self-check 임계값 (LOCK)**:
- P0: self_check_score ≥ 70 → PASS
- P1: self_check_score ≥ 75 → PASS
- P2: self_check_score ≥ 80 → PASS

## 4.7 ResponseEnvelope (최상위 출력 규격, LOCK)

```python
class ResponseEnvelope:
    answer:
        summary: str
        details: str
        next_actions: List[str]
    evidence:
        coverage: float  # 0~1
        items: List[EvidenceItem]
        qod: float  # 0~1
    self_check:
        score: float  # 0~1
        verdict: Literal["PASS","WARN","FAIL"]
        reasons: List[str]
        retry_allowed: bool
    decision_ref:
        decision_id: str
        gates: dict  # policy/cost/evidence
    audit:
        event_ids: List[str]
        failure_codes: List[str]
        fallback_ids: List[str]
```

## 4.8 성능 벤치마크 목표 (P1 확정)

| 지표 | 목표 | 측정 위치 |
|------|------|----------|
| 단순 응답 (mini) | ≤ 2초 | S0 → S5 |
| 복합 응답 (main + 툴 1회) | ≤ 10초 | S0 → S5 |
| Self-check 소요 | ≤ 1초 | S5 → S6 |
| 처리량 | 동시 5요청 | 큐 레이어 |
| 토큰 카운팅 (tiktoken) | ≤ 50ms / 1만 토큰 | S2 게이트 |

---

# 5. BLUE NODES (도메인 실행 모듈)

## 5.1 정의 & 제약 (LOCK)
- BLUE NODE는 **도메인 실행 모듈** (RULE 1.3 4.2)
- ORANGE CORE 규칙을 **상속**, **독립 실행 불가**
- Non-goal/안전/비용/승인 구조는 **변경 불가**

## 5.2 P0/P1/P2 도메인 분류

### P0 — 기본 활성 (핵심)
- Dev/System, Research, Productivity
- P0라도 외부 서비스/API는 약관 체크리스트 필수

### P1 — 승인 후 활성 (확장)
- Content, Data & Quant
- 승인 채널: A(CORE 제안형) + B(사용자 요청형) 둘 다 허용 (LOCK)
- 자동화는 "후보 프로필 생성"까지만 허용

### P2 — 세션별 승인 + 자동 OFF (위험)
- Trading Strategy 등 (실거래 금지)
- **세션 종료 시 즉시 OFF** (LOCK: Option A)
- 활성화 조건: 사용자 명시적 승인 요청, 해당 세션에서만 활성

## 5.3 NodeCapabilityProfile

```python
node_id: str
required_tools: List[str]  # tool_id
optional_tools: List[str]
risk_class: Literal["low","med","high"]
cost_class: Literal["v0","v1","v2","v3"]
gates_required: List[str]  # ["policy","cost","approval","evidence","self_check"]
```

## 5.4 NodeRequest/ResponseEnvelope

**필수**: `request_id`, `project_id`, `session_id`, `node_id`, `intent_summary`, `constraints`, `trace_id`

**선택**: `policy_snapshot_id`, `budget_snapshot_id`, `evidence_refs`, `decision_id`, `ui_hints`

**최소 필드**: `trace_id`, `node_id`, `domain`, `inputs.summary`, `outputs.result`, `status`

## 5.5 MCP Bridge Layer (DEC-017 LOCK)

### 기본 설정
- **전송 계층**: Streamable HTTP (DEC-017 확정)
- **보안**: 모든 MCP 연결은 TLS 필수, 인증 토큰은 07 Gate 경유
- **타임아웃**: 도구 호출 **30초**, 스트리밍 **120초**
- **재시도**: 일시적 실패(5xx/네트워크) 최대 **2회**, 그 외 fallback/deny

### config.toml MCP 설정
```toml
[mcp]
transport = "streamable_http"
timeout_tool_s = 30
timeout_stream_s = 120
max_retries = 2
tls_required = true
auth_injection = "07_gate"
```

### MCP 패턴 카탈로그

| 패턴 | 설명 |
|------|------|
| 단순 도구 호출 | NODE → ToolRegistry → @mcp.tool → Decision.optional_signals |
| 스트리밍 응답 | 긴 실행 → Streamable HTTP 청크 수신 → Decision ref |
| 멀티 도구 체인 | 순차 의존 → verify.chain_used에 순서 기록 |
| 조건부 폴백 | 1차 실패 → 동일 risk_class 대체 adapter 전환 |

### MCP 서버 카탈로그

| 서버 ID | 기능 | 배포 | risk | V |
|---|---|---|---|---|
| mcp.search.tavily | 웹 검색 | cloud | med | V1 |
| mcp.search.serpapi | 검색엔진 API | cloud | med | V1 |
| mcp.code.e2b | 코드 샌드박스 | cloud | high | V1 |
| mcp.code.pyodide | 브라우저 Python | local | low | V1 |
| mcp.doc.unstructured | 문서 파싱 | cloud | low | V1 |
| mcp.doc.pymupdf | PDF 파싱 | local | low | V1 |
| mcp.vision.clip | 이미지 분석 | local | low | V2 |
| mcp.speech.whisper | STT | cloud | low | V2 |
| mcp.browser.playwright | 브라우저 제어 | local | high | V1 |
| mcp.db.postgres | DB 연동 | local | high | V1 |
| mcp.realtime.websocket | 실시간 WebSocket | hybrid | med | V2 |

### MCP 보안 위협 방어 (LOCK)
- 입력 검증: ToolRegistry 스키마 통과 필수
- 프롬프트 인젝션 방어: 응답 내 지시문 패턴 필터링
- 자격증명 격리: NODE 내부 하드코딩 금지, 07 Gate 런타임 주입
- 최소 권한: risk_class/cost_class에 따라 범위 최소화
- 감사 로그: 모든 외부 도구 호출 LogEvent 기록

### MCP SDK 통합
- 동시 세션 상한: `max_concurrent_mcp: 10`
- 세션 풀 TTL: 300초
- 미사용 세션: 60초 idle 시 자동 종료

## 5.6 TemplateSet (LOCK): 3종
1. **TS_CORE**: 일반 대화/요약/정리
2. **TS_WEB_RESEARCH**: 웹 리서치/근거 수집/인용
3. **TS_CODE**: 코딩/디버깅/리팩토링

## 5.7 노드 상한 (LOCK)
- `active_node_cap`: 세션당 활성 NODE 상한
- `candidate_node_cap`: 세션당 후보 NODE 상한
- 상한 도달 시: 신규 후보 생성 금지 → 기존 NODE 재사용

---

# 6. INFRA CORE (인프라 계층)

## 6.1 Brain Adapter Layer

### ConnectorResponse 스키마 (LOCK)
```python
class ConnectorResponse(BaseModel):
    output_text: str
    evidence_summary: Optional[str]
    cost_used_estimate: float
    warnings: List[str]
    tool_calls: Optional[List[Any]]
    trace_id: str
    qod_hint: Optional[float]  # 0~1
    class Config:
        extra = "forbid"
```

### OTHER BRAINS 매핑표 (LOCK)

| category | 예시 | 기본 게이트 |
|---|---|---|
| llm.text | main/cheap LLM | policy, cost |
| llm.vision | 이미지/비전 모델 | policy, cost |
| browser.render | Playwright/Selenium | policy, cost, approval(고위험) |
| api.http | REST/GraphQL | policy, cost |
| code.exec | 샌드박스 코드 실행 | policy, cost |
| data.vector | VectorDB | cost |
| storage.obj | object storage | policy(PII), cost |
| logging | jsonl/sqlite/postgres | cost |

## 6.2 ToolRegistry 스키마 (MOD-006)

```python
class ToolRegistryEntry(BaseModel):
    tool_id: str
    category: Literal["browser.render","api.http","code.exec",
                       "llm.text","llm.vision","data.vector",
                       "storage.obj","logging"]
    adapter_id: str
    risk_class: Literal["low","med","high"]
    cost_class: Literal["v0","v1","v2","v3"]
    required_gates: List[Literal["policy","cost","approval","evidence","self_check"]]
    outputs: List[Literal["signal","artifact","memory","log"]]
    enabled: bool = True
    notes: str = ""
```

## 6.3 동적 모델 라우팅

1. **입력 분류**: 복잡도(low/mid/high), 도메인, 토큰 예상량
2. **후보 선택**: HAL 카탈로그에서 활성 엔진 필터
3. **비용/품질 최적화**: cost_class × quality_score 가중 비교
4. **게이트 통과**: 07 PolicyCheck + CostBudget 확인
5. **폴백**: 선택 엔진 실패 시 차순위 전환 (최대 2회)

**Fallback Chain**: `gpt-4o → claude-sonnet → local-ollama → error_response` (최대 3단계)

**Multi-Brain Failover**: 연속 3회 타임아웃 시 전환 (LOCK)

## 6.4 Prompt Cache Manager

- **Anthropic**: ephemeral cache_control 블록 마킹 (90% 할인)
- **OpenAI**: 1024+ 토큰 prefix 자동 캐싱 (50% 할인)
- **응답 캐시 계층**: L0(인메모리, 10분) → L1(Redis, 1시간) → miss 시 실제 호출
- **Semantic Cache TTL**: 실시간 5분, 분석 24시간, 지식 7일

## 6.5 Rate Limit

| 항목 | 수치 |
|------|------|
| Token Rate Limit (V1) | 일일 100K 토큰 |
| API Call Rate | 분당 60회 |
| Burst Protection | 10초 내 10회 초과 시 1분 쿨다운 |
| 외부 API 호출 | 10회/분 |
| 고비용 모델 호출 | 3회/분 |
| 병렬 실행 상한 | **3** (LOCK) |
| 429 응답 시 | 지수 백오프 (1초/2초/4초, max 3회) |

## 6.6 Backup/Recovery

- **자동 백업**: 일 1회 02:00, 로컬 `~/.vamos/backup/`
- **대상**: SQLite DB + Chroma 컬렉션 + KG JSON + config
- **보존**: 7일분 + 4주분 + 3월분
- **복원**: `vamos restore --date 2026-02-20`

### 장애 복구 시나리오

| 시나리오 | 복구 절차 | 목표 RTO |
|---------|----------|---------|
| DB 커넥션 끊김 | docker compose restart → 커넥션 풀 재시작 | 5분 |
| LLM API 429 | 자동 큐잉 + 지수 백오프 (max 3회) | 2분 |
| 디스크 용량 부족 | 오래된 JSONL 압축/삭제 → 알림 | 10분 |
| Core 프로세스 크래시 | docker compose up -d → 로그 확인 | 3분 |
| Qdrant 데이터 손상 | 최근 스냅샷 복원 → 재인덱싱 | 30분 |

## 6.7 배포 전략

| 버전 | 배포 | Storage | Logging |
|------|------|---------|---------|
| V1 | 로컬 Windows/WSL | SQLite+JSONL, Chroma | JSONL+SQLite |
| V2 | Docker Compose | Postgres, Qdrant | Postgres+JSONL 압축 |
| V3 | K8s | 매니지드 Postgres, Qdrant Cloud | Loki/ELK |

## 6.8 10계층 보안 아키텍처 (4-Layer LLM Guardrails §9.1과 별개)

| # | 계층 | 역할 |
|---|------|------|
| 10 | UI/UX | 사용자 인터페이스 |
| 9 | Workflow Orchestrator | Agent 워크플로우 |
| 8 | Decision Engine | 판단/게이트/승인 |
| 7 | Memory/Storage | 메모리 + 벡터 저장 |
| 6 | RAG Pipeline | 검색 증강 생성 |
| 5 | Brain Routing | 모델 선택/라우팅 |
| 4 | Brain Adapter | LLM 추상화 |
| 3 | Tool Execution | 외부 도구 실행 |
| 2 | Infra Runtime | Docker/DB/로그 |
| 1 | Config/Security | 설정 + 보안 정책 |

호출 방향: 상위 → 하위 (역방향 금지, 이벤트 기반 통지만)

## 6.9 설정 우선순위 (LOCK)
```
환경변수 (ENV) > 설정파일 (config.toml/.env) > 코드 기본값 (default)
```

## 6.10 로깅 표준 (JSON Structured, LOCK)
- 필수: `timestamp`(ISO8601 UTC), `level`(DEBUG~FATAL), `module`, `event`(snake_case), `trace_id`, `payload`
- 평문 로그 직접 출력 금지
- 민감 정보 payload 포함 금지

---

# 7. AGENT WORKFLOW (워크플로우 파이프라인)

## 7.1 표준 5단계 Pipeline (LOCK)

| # | 단계 | 내용 | Gate |
|---|------|------|------|
| 1 | **Intake** | 요청/제약 수집 + G0 입력 검증 | G0 |
| 2 | **Plan** | 분해/라우팅 + G1 정책 + G2 비용 + TEE Think | G1, G2 |
| 3 | **Execute** | 도구/노드 실행 + TEE Execute | (07 선행) |
| 4 | **Verify** | G3 품질 + Self-check + EVX 체인 + TEE Evaluate | G3 |
| 5 | **Deliver** | 출력/로그/저장 + G4 최종 승인 + 3단 출력 | G4 |

## 7.2 LangGraph StateGraph 통합 (LOCK)

```
Intake → Plan → [Gate Check] → Execute → Verify → Deliver
                  |(deny)              ^(retry)
                Abort  ←-------- Soft Loop
```

### 외부 Workflow Engine 어댑터 규칙 (FREEZE)
1. **Gate 선행**: Execute 전 07 Gate 결과 확정 필수
2. **Checkpoint/Replay/Fork**: VAMOS trace_id 단위로만 허용
3. **멀티 에이전트 제약**: 자유 상호 호출/무한 대화 금지

## 7.3 EVX-1~EVX-6 검증 체인 (LOCK)

| EVX | 목적 | 배치 위치 | 차단 조건 |
|-----|------|----------|---------|
| EVX-1 | Code-as-Policy | Plan/Verify | Policy deny / P2 미승인 |
| EVX-2 | Adversarial Verifier | Verify | 비용 차단 / 미승인 |
| EVX-3 | Uncertainty Signal | Plan/Verify | 비용 차단 시 확장 금지 |
| EVX-4 | Thought Buffer | Execute/Verify | Policy deny / 민감정보 저장 금지 |
| EVX-5 | Generate-Verify-Learn | Verify/Reflection | 자동 적용 금지 (승인 전까지 신호만) |
| EVX-6 | Z3 Routing/Constraint Gate | Plan/Verify | Policy deny / Solver 미승인 |

**공통 차단**: PolicyCheck=deny → 모든 EVX 즉시 중단 / 비용 초과 → EVX 확장 불가

## 7.4 Circuit Breaker (LOCK)

| 상태 | 설명 |
|------|------|
| CLOSED | 정상 (호출 허용) |
| OPEN | 연속 **3회** 실패 → 자동 차단 |
| HALF-OPEN | **60초** 후 1건 시도 → 성공 시 CLOSED |

P2 이상: OPEN 시 자동 복구 없이 승인 후 HALF-OPEN만

## 7.5 Gate-Pipeline Mapping (LOCK)

| 단계 | Gate | 역할 | 실패 시 |
|------|------|------|--------|
| Intake | G0 | 입력 검증 | 즉시 거부 |
| Plan | G1 | 정책 검사 | deny |
| Plan | G2 | 비용 검사 | deny/downshift |
| Verify | G3 | 품질 검사 | Soft loop/deny |
| Deliver | G4 | 최종 승인 | hold/deny |

## 7.6 3단 출력 (LOCK)

| # | 필드 | 설명 |
|---|------|------|
| 1 | `user_response` | 최종 결과 (사용자에게 전달) |
| 2 | `evidence_summary` | 근거/요약 (출처, QoD) |
| 3 | `log_report` | 로그 (trace_id, 승인 이벤트) |

## 7.7 TEE 루프 (Think-Execute-Evaluate, LOCK)

1. **Think**: 상태/컨텍스트 분석 → 다음 액션 결정 (Gate 선행, 비용 예측)
2. **Execute**: 결정된 액션 실행 (Allowlist 자동승인 or 확인)
3. **Evaluate**: 결과 평가 (Self-check, 미달 시 Soft loop)

**TEE 최대 반복**: P0=3회, P1=5회, P2=10회 (승인 시 확장)

## 7.8 Soft/Hard Loop 규칙 (LOCK)

- **Soft loop**: 동일 단계 내 1회 보정 후 재시도 (자동 1회만)
- **Hard loop**: 한 단계 이전으로 되감아 재실행 (**자동 금지**, 승인 후만)
- **위험/정책 위반**: 루프/재시도 없이 **즉시 deny**

## 7.9 HITL (Human-In-The-Loop)

**개입 시점**:
- P2 승인: 위험 작업 전
- 불확실성: QoD < 0.5 → 인간 판단 위임
- 모호 의도: 복수 해석 → 명확화
- 비용 초과 예상: 한도 80%+ → 사전 확인
- 결과 검증: 고위험 결과물 인간 최종 검토

**타임아웃**: 기본 30분, P2는 무제한

## 7.10 Agent Marketplace

- Agent 프로필: `{agent_id, name, skills, success_rate, cost_per_use}`
- Workflow 템플릿: `{template_id, name, steps, required_tools, estimated_cost}`
- 설치/활성화: 07 Gate 승인 후만

## 7.11 도구 승인 Allowlist (DEC-003, LOCK)

- **Allowlist 자동승인**: 읽기 전용/조회/로그 등 안전 도구
- **명시적 확인 필요**: 외부 API/파일 쓰기/코드 실행/P2 이상
- 미등록 도구: 기본값 "확인 필요"

## 7.12 대화 턴 상한 (LOCK)
- P0=5턴, P1=10턴, P2=20턴

## 7.13 4레이어 Guardrails 호출 시점

| 레이어 | 호출 단계 |
|--------|---------|
| L1 NeMo Guardrails | Intake (입력 필터링) |
| L2 Guardrails AI | Plan (정책 검사) |
| L3 LlamaGuard | Execute (출력 안전성) |
| L4 Post-delivery Audit | Deliver 이후 (사후 감사) |

## 7.14 워크플로우 패턴 카탈로그 (12건)

| # | 패턴 | 구조 | 용도 |
|---|------|------|------|
| 1 | Sequential | A→B→C | 단순 분석 |
| 2 | Parallel Fan-out | A→[B1,B2,B3]→C | 멀티소스 수집 |
| 3 | Map-Reduce | 분할→병렬→통합 | 대량 데이터 |
| 4 | Router | 조건별 분기 | 시나리오별 처리 |
| 5 | Retry-with-Backoff | 실패→대기→재시도 | 외부 API |
| 6 | Saga | 분산 트랜잭션→보상 | 멀티 시스템 |
| 7 | Pipeline | 단계별 변환 | 데이터 정제 |
| 8 | Observer | 이벤트 감지→반응 | 모니터링 |
| 9 | Mediator | 중앙 조율 | 멀티에이전트 |
| 10 | Chain of Responsibility | 핸들러 체인 | 승인 단계 |
| 11 | State Machine | 상태 전이 | 복잡 워크플로우 |
| 12 | Event Sourcing | 이벤트 로그 기반 | 감사/재현 |

---

# 8. STORAGE & MEMORY (저장/메모리)

## 8.1 4계층 메모리

| 계층 | 범위 | TTL | B-Series | V1 | V2 | V3 |
|------|------|-----|----------|----|----|-----|
| **L0** Session | 단일 세션 | 세션 종료 (최대 7일) | B-4 Working | 활성화 | 동일 | 동일 |
| **L1** Project | project_id 단위 | 90일 (연장 가능) | B-1 Episodic | 선택적 | 기본 활성화 | 활성화 |
| **L2** Long-term | 전역 (검색 기반) | 무기한 (QoD 재평가) | B-3 Semantic | 비활성화 | 제한적 (승인필수) | 활성화 |
| **L3** Procedural | 전역/프로젝트 | 무기한 (deprecated 전환) | B-2 Procedural | 비활성화 | 제한적 | 활성화 (D7 Gate) |

## 8.2 4종 기억 유형 (B-Series)

| 유형 | 설명 | 대표 저장 계층 |
|------|------|-------------|
| **B-4 Working** | 세션 컨텍스트/작업 중 메모리, 휘발성 | L0 |
| **B-1 Episodic** | 사건/대화/상황 기록 | L1 |
| **B-3 Semantic** | 정리된 사실/지식 | L2 |
| **B-2 Procedural** | 절차/플레이북/루틴/템플릿 | L3 |

### B-2 Procedural Memory 상세
- **형태**: playbook, workflow, template, routine
- **최소 필드**: procedure_id, version(semver), target_scope, trigger_conditions, steps[], required_tools, safety_notes, activation_state(draft/approved/active/deprecated), provenance
- **파이프라인**: Candidate(draft) → PolicyCheck(D7) → Approval → 저장(write) → 활성(active)
- **폐기/롤백**: 위험/오류/비용 폭주 시 즉시 비활성화, audit log 필수

## 8.3 Vector DB 전략

| 버전 | 저장소 | Vector DB |
|------|--------|-----------|
| V1 | SQLite + JSONL | **Chroma** (로컬 임베디드) |
| V2 | Postgres 중심 | **Qdrant** (서버 우선) / Chroma 폴백 |
| V3 | 매니지드 Postgres | **Qdrant Cloud** |

### VectorStore 어댑터 인터페이스 (LOCK)
```python
upsert(records: VectorRecord[]) → void
search(query_vector: float[], top_k: int, filters: dict) → VectorRecord[]
delete(ids: str[]) → void
get_by_id(id: str) → VectorRecord | None
```
설정 변경만으로 교체 가능, 비즈니스 로직 수정 금지

## 8.4 Embedding 모델 (DEC-005 UPDATED)

| 환경 | 모델 | 차원 | 비용 |
|------|------|------|------|
| V1 로컬 (기본) | **BGE-M3** | 1024 (Matryoshka 256) | 무료 |
| V1 클라우드 (옵션) | **text-embedding-3-small** | 1536 | 과금 |
| V2+ | 벤치마크 기준 최적 | 1536~3072 | - |

## 8.5 GraphRAG (DEC-004 LOCK)

| 단계 | 버전 | 구성 | 정확도 |
|------|------|------|--------|
| Basic | V1 | Vector 단독 + 단순 프롬프트 (NetworkX+JSON) | 64%+ |
| Hybrid+Rerank | V2 | BM25+Vector 앙상블 + Cross-encoder (Neo4j) | 83%+ |
| Self-RAG+Graph | V3 | Self-RAG 자체 검증 + GraphRAG 다중 홉 | 90%+ |

## 8.6 Semantic Cache (MOD-017)

- **캐시 히트 임계값**: cosine_similarity ≥ **0.95**
- **캐시 저장소**: V1=인메모리(LRU), V2+=Redis
- **무효화 정책**:
  - TTL: 기본 **24시간** (변동 잦은 프로젝트 6시간)
  - 소스 변경: 인덱싱 문서 갱신/삭제 시 즉시 무효화
  - QoD 변동: QoD ≤ 0.4 시 무효화
  - 수동 flush: 프로젝트/전역 단위

## 8.7 RAG 6단계 파이프라인 (LOCK)

| # | 단계 | 설명 |
|---|------|------|
| 1 | 수집 (Collect) | 파일, URL, DB에서 문서 수집 |
| 2 | 쪼개기 (Chunk) | 청크 크기 300~500 토큰, 오버랩 50~100 |
| 3 | 벡터화 (Embed) | BGE-M3/text-embedding-3-small |
| 4 | 저장 (Store) | VectorStore 어댑터 |
| 5 | 검색 (Retrieve) | BM25+Vector 앙상블 + Rerank |
| 6 | 생성 (Generate) | 검색 결과 → LLM 컨텍스트 주입 → 응답 |

**운영 한계**: 문서 15개/프로젝트, 청크 30개/문서
**재시도**: max 3회 (BM25 단독 → 캐시 → 모델 단독 + 경고)

## 8.8 QoD (Quality of Data) 점수 체계 (DEC-010 LOCK)

**스케일**: 0.0~1.0

**가중치 공식 (DEC-014)**:
```
qod_score = relevance × 0.30 + accuracy × 0.25 + freshness × 0.25 + completeness × 0.20
```

**출처별 QoD 가중치**:
| 출처 | 가중치 |
|------|--------|
| 공식 문서 (API Doc, RFC) | 0.85 |
| 내부 KB / 팀 문서 | 0.70 |
| 커뮤니티 (StackOverflow) | 0.50 |
| 미분류 / 출처 불명 | 0.30 |

**임계값**: QoD < 0.4 → L2 벡터 삽입 금지, QoD < 0.7 → 출력 보류

## 8.9 저장 정책 (LOCK)

| 정책 | 동작 |
|------|------|
| **Allow (PASS)** | 요약/결과만 저장. L3은 자동 활성 금지 |
| **Restrict (NEEDS_APPROVAL)** | 마스킹 후 저장 허용 + TTL. 마스킹 불완전 시 deny |
| **Deny (BLOCK)** | 모든 저장소 장기 저장 불가. 벡터 삽입 절대 금지 |

**마스킹/PII**: `***` 마스킹 또는 hash. V1=정규식/패턴, V2+=NER 모델+문맥 분류기

---

# 9. SAFETY, COST & APPROVAL (안전/비용/승인)

## 9.1 4-Layer LLM Guardrails (10계층 보안 아키텍처 §6.8과 별개)

| 레이어 | 엔진 | 위치 | 역할 |
|--------|------|------|------|
| L1 입력 방어 | **NeMo Guardrails** | Intake | 프롬프트 필터링/토픽 제한 |
| L2 처리 방어 | **Guardrails AI** | Plan/Execute | 출력 품질/안전성 검증 |
| L3 출력 방어 | **LlamaGuard** | Execute/Deliver | 유해성/정책 위반 분류 |
| L4 사후 감사 | 비동기 감사 엔진 | Deliver 이후 | NLI 환각 검증, 편향 탐지 |

**Fail-safe**: 안전 시스템 장애 시 "닫힘(closed)" 기본값 → 확인 불가 시 차단

### 장애 시 복구

| 장애 | 기본 대응 | Fallback |
|------|----------|---------|
| NeMo 장애 | deny | 정규식 기본 필터 |
| Guardrails AI 장애 | deny | L1/L3만 운영 |
| LlamaGuard 장애 | deny | 출력 검증 생략 불가 → deny |
| PolicyCheck 장애 | 전체 차단 | 수동 Approval |
| CostBudget 조회 실패 | 차단 | 마지막 상태 사용 (5분 캐시) |

## 9.2 RBAC (역할 기반 접근 제어, LOCK)

| 역할 | 설명 | 최대 자율 | P2 | 비용 한도 |
|------|------|---------|----|---------|
| **OWNER** | 시스템 소유자 | L3 | O | ₩266,000/월 |
| **ADMIN** | 위임 관리자 | L2 | O | ₩93,000/월 |
| **OPERATOR** | 일반 운영자 | L1 | X | ₩40,000/월 |
| **VIEWER** | 읽기 전용 | L0 | X | 0 |

## 9.3 Autonomy Level (자율 수준, LOCK)

| 수준 | 명칭 | 설명 | 기본값 |
|------|------|------|--------|
| L0 | FULL_MANUAL | 모든 행동에 확인 | - |
| L1 | SUPERVISED | Allowlist 내만 자동 | **기본값** |
| L2 | SEMI_AUTO | 읽기/생성 자동, 쓰기 승인 | - |
| L3 | FULL_AUTO | 비용/Non-goal/P2 외 자동 | - |

**L3에서도 절대 불가**: Non-goal, RBAC 자기 권한 상승, CostBudget 자체 변경, 안전 필터 우회

## 9.4 PolicyCheck

- **결과**: deny / restrict / allow
- **호출 위치**: (a) 외부 API 직전 (b) P2 활성화 직전 (c) 저장/인덱싱 직전 (d) 비용 체크
- **검사 항목**: Non-goal 위반, 약관/체크리스트, P2 세션 재확인, 민감정보, 비용 상한

## 9.5 Approval 2단계

| 단계 | 설명 | 권한 |
|------|------|------|
| 1단계 계획 승인 | "무엇을 할지" 설명 + 승인 | OPERATOR+ |
| 2단계 실행 승인 | "지금 실행할지" 최종 확인 (위험 작업) | ADMIN/OWNER |

**승인 타임아웃**: 10분 미응답 → 자동 거부

### S-Module/E-Module 승인 규칙 (LOCK)

| 구분 | 유형 | 기본 처리 | 승인 단계 |
|------|------|----------|----------|
| S-Module | 분석/진단/제안(읽기) | allow | 없음 |
| S-Module | 변경 적용(패치) | restrict | 계획 승인 |
| S-Module | 자동 배포 | deny(기본) | 실행 승인 |
| E-Module | 읽기 전용 | allow | 없음 |
| E-Module | 쓰기/변경 | restrict | 계획 승인 |
| E-Module | 고위험 실행 | deny(기본) | 실행 승인 |

## 9.6 CostBudget (비용 상한, LOCK)

| 버전 | 일일 상한 | **월 상한** | 모델 전략 |
|------|----------|------------|----------|
| V1 | 1,300원 ($1) | **40,000원 ($30)** | Mini 90%+ |
| V2 | 3,100원 ($2.3) | **93,000원 ($70)** | Mini 60-70% / Main 30-40% |
| V3 | 8,900원 ($6.7) | **266,000원 ($200)** | Main 중심, 플래그십 적극 |

## 9.7 Downshift (LOCK)

| 임계값 | 동작 |
|--------|------|
| **80% 도달** | Mini 우선 강제. Main/Flagship은 승인 시만 |
| **100% 도달** | 상한 초과 모델 호출 승인 없이 **자동 차단** |

**예산 알림 단계**: 50%(정보) → 80%(경고, 노란색) → 95%(긴급, Mini-only) → 100%(차단, 빨간색)

## 9.8 투자(AINV) 특화 규칙
- VaR > 포트폴리오 5% → 자동 경고, 초과 주문 P2 승인 필수
- 매매 추천 포함 응답에 100% 면책 삽입
- 금융 특화 Red-teaming 공격 패턴 DB 100+건
- 재무 수치 할루시네이션 자동 탐지

## 9.9 7개 불변 구역 (LOCK)
1. `safety_rules` 2. `cost_ceiling` 3. `approval_flow` 4. `non_goals` 5. `audit_format` 6. `data_retention` 7. `user_consent`

---

# 10. UI/UX (사용자 인터페이스)

## 10.1 프레임워크 (LOCK)
- **V1**: Tauri 2.0 (Rust 백엔드 + React 프론트엔드, ~30MB)
- **V2**: + PWA (Next.js + Tailwind CSS + shadcn/ui)
- **i18n**: 기본 `ko-KR`, 보조 `en-US`

## 10.2 Hologram View (3-Panel)

### Left Panel (Timeline, ~250px)
- 세션 리스트/날짜별, 활성 BLUE NODE (P0/P1/P2 배지)
- Runtime Pipeline 타임라인: RECEIVED→INTENT→EVIDENCE→DECISION_LOCK→EXEC→OUTPUT→SELF-CHECK→MEMORY→DONE
- Self-check 요약, Cost 상태, RAG/Evidence 상태

### Center Panel (Stream Canvas)
- User bubble(우측) / AI bubble(좌측, Markdown)
- Thinking/Status block, Artifact Embed, Input(텍스트+파일+음성+캡처)

### Right Panel (Glass HUD, ~300px)
- Verification Badge: ≥0.8 VERIFIED(Green), 0.5~0.8 PARTIAL(Yellow), <0.5 UNVERIFIED(Gray)
- Uncertainty Alert, Cost 게이지, Approval 슬라이드

## 10.3 Builder View (3-Panel)

### Left Panel (Navigation, ~300px)
- 프로젝트/세션 트리, Registry(EventTypes/FailureCodes/Fallbacks/NodeRegistry)

### Center Panel (Main Canvas)
- ORANGE CORE: 중앙 육각형 (active 시 pulsing)
- BLUE NODE: 주변 원형 (상태별 색상)
- Module Manager Tab

### Right Panel (Control, ~400px)
- 탭: Logs | Approval | Cost | Memory
- Approve/Deny/Edit&Retry, Budget Gauge, Live Token Counter

## 10.4 UI 상태 머신

| 상태 | 설명 | 사용자 액션 |
|------|------|-----------|
| UIS1_IDLE | 입력 대기 | 입력 가능 |
| UIS2_PROCESSING | Core 처리 중 | 취소 가능 |
| UIS3_LOCKED | Decision Lock | 취소 가능, 수정 불가 |
| UIS4_RUNNING | 실행 단계 | 실행 취소 |
| UIS5_AWAIT_APPROVAL | 승인 대기 | 승인/거절 |
| UIS6_PRESENTING | 결과 표시 | 재생성, 저장, 피드백 |

**업데이트 주기**: 이벤트 기반 (폴링 금지), 지연 최대 500ms

## 10.5 에러 메시지 매핑

### 입력 단계 (Front Mini)
| Code | 메시지 |
|------|--------|
| FM_ERR_FMT | 지원하지 않는 파일 형식입니다 |
| FM_ERR_SIZE | 파일 크기가 제한 초과 (최대 25MB) |
| FM_ERR_PII | 민감 정보 포함. 마스킹 후 진행할까요? |
| FM_ERR_ZERO | 파일 내용이 비어 있거나 읽을 수 없습니다 |

### 판단 단계 (ORANGE CORE)
| Code | 메시지 |
|------|--------|
| OC_ERR_NONGOAL | VAMOS 안전 정책상 수행 불가 |
| OC_ERR_P2_LOCK | '{도메인}' 활성화 승인 필요 |
| OC_ERR_COST | 절약 모드 전환 |
| OC_ERR_NO_ROUTE | 적절한 도구를 찾지 못했습니다 |

### 실행 단계 (Tool)
| Code | 메시지 |
|------|--------|
| TL_ERR_TIMEOUT | 작업 시간 초과. 잠시 후 재시도 |
| TL_ERR_403 | 직접 접근 차단. 검색 엔진 우회 탐색 |
| TL_ERR_PARSE | 파싱 실패. 원본 텍스트로 결과 표시 |
| MC_ERR_LOW_QOD | 결과 품질 기준 미달. 보완 수행 중 |
| MC_ERR_CONFLICT | 출처 간 정보 충돌 |

## 10.6 컬러 팔레트
- **ORANGE CORE**: `#F97316`
- **BLUE NODE**: `#00F6FF`
- **Approval 대기**: `#F59E0B` / 승인: `#10B981` / 거절: `#EF4444`
- **Evidence**: `#00DDB3`
- **Background**: `#1E1E1E` (Dark IDE)
- **비용 80%**: `#FBBF24` (노란색) / **100%**: `#EF4444` (빨간색)

## 10.7 접근성
- WCAG 2.1 AA 준수
- 키보드 전용 네비게이션, 고대비 모드, 스크린 리더 호환 (V3)
- 폰트 크기 조절, 애니메이션 감소 모드 (`prefers-reduced-motion`)

---

# 11. 자기진화 (Self-Evolution)

## 11.1 핵심 원칙 (LOCK)
- Self-evo는 "**제안**"까지만 생성, **자동 적용 절대 금지** (RULE 1.3 section 8)
- 불변 영역: RULE/정체성/비용상한은 수정 불가

## 11.2 S-Module → I-Module 경유 동작 (LOCK)
1. I-모듈 로그/근거/템플릿/스냅샷/품질지표를 입력으로 받음
2. S-1(Self-check)가 "문제 신호" 생성
3. S-3~S-7이 "후보" 생성 → S-8(거버넌스) 전달
4. S-8이 위험/비용/정책 1차 확인 → "승인된 항목만" 반영
5. S-2가 "개선 전/후 성능 비교" 회귀 테스트

## 11.3 Self-evo 가능 범위 (6개 허용 도메인)
1. 프롬프트 최적화 (철학 키워드 유지)
2. 도구 조합
3. 메모리 관리
4. 출력 포맷
5. 워크플로우 순서
6. 모델 선택

## 11.4 Self-evo 절대 불가 영역 (7개 불변 구역)
1. 정체성/가치/철학
2. Non-goal
3. 법/규제/윤리
4. 비용 상한 금액
5. 승인 구조
6. P0 도메인
7. P2 도메인 생성/활성화

## 11.5 Self-evo 롤백 메커니즘
1. 자동 스냅샷: 적용 직전 전체 상태 저장
2. 이상 감지: QoD < 0.70 지속 3회, 안전 위반 1회, 사용자 롤백 명령
3. 부분 롤백: 최소 변경 단위(diff) 순차 역산
4. 전체 롤백: 부분 실패 시 스냅샷 전체 복구
5. 재적용 잠금: 동일 제안 롤백 후 **14일간 재적용 금지**

---

# 12. 스키마 & 레지스트리 (전체)

## 12.1 Registry 소유권

| Registry | Owner Doc | 네이밍 |
|----------|-----------|--------|
| EventTypeRegistry | D2 | lower.dot |
| FailureCodeRegistry | D2 | UPPER_SNAKE |
| FallbackRegistry | D2 | FB_UPPER_SNAKE |
| ToolRegistry | D4 | tool_id |
| NodeRegistry | D3 | domain_name |
| VerifyChainRegistry | D5 | EVX-ID |

## 12.2 EventTypeRegistry (53개)

```
oc.request.received
oc.i1.parse.started, oc.i1.intent.parsed, oc.i1.intent.ambiguous, oc.i1.parse.failed
oc.i2.query.built, oc.i2.fetch.started, oc.i2.evidence.ready, oc.i2.evidence.insufficient, oc.i2.fetch.blocked, oc.i2.fetch.failed
oc.i3.plan.created, oc.i3.commit.requested, oc.i3.commit.approval_required, oc.i3.commit.completed, oc.i3.commit.denied, oc.i3.commit.failed
oc.i4.structuring.started, oc.i4.output.structured, oc.i4.spec.violated, oc.i4.mask.applied, oc.i4.structuring.failed
oc.i5.gates.evaluated, oc.i5.route.selected, oc.i5.decision.locked, oc.i5.approval.required, oc.i5.cost.downshifted, oc.i5.policy.blocked, oc.i5.decision.failed
oc.loop.retry.reasoning, oc.loop.retry.action, oc.deny.blocked, oc.done
oc.p2.activated, oc.p2.deactivated
oc.i6.selfcheck.started/passed/failed, oc.i7~i21 각 모듈 이벤트
wf.stage.enter, wf.stage.exit, wf.approval.requested
ui.builder.*, ui.hologram.* (24개 시나리오)
mem.reference.updated, mem.kb.derived
```

## 12.3 FailureCodeRegistry (20개)

```
OC_I1_PARSE_FAIL, OC_I1_AMBIGUOUS_UNRESOLVED
OC_I2_RAG_NO_SOURCE, OC_I2_EVIDENCE_QOD_LOW, OC_I2_SOURCE_POLICY_BLOCK, OC_I2_TIMEOUT
OC_I3_MEMORY_POLICY_DENY, OC_I3_APPROVAL_REQUIRED, OC_I3_COMMIT_FAIL
OC_I4_OUTPUT_SPEC_VIOLATION, OC_I4_CITATION_MISSING, OC_I4_MASK_FAIL
OC_I5_POLICY_BLOCK, OC_I5_APPROVAL_REQUIRED, OC_I5_COST_OVER_BUDGET, OC_I5_EVIDENCE_INSUFFICIENT, OC_I5_ROUTE_NOT_FOUND
POLICY_DENY, GT_ERR_COST_LIMIT, TOOL_TIMEOUT
```

## 12.4 FallbackRegistry (13개) & 매핑

| fallback_id | 목표 | 주요 트리거 |
|------------|------|-----------|
| FB_ASK_CLARIFICATION | 정확도 | 의도 모호 |
| FB_INTENT_HEURISTIC_PARSE | 진행성 | 파싱 실패 |
| FB_RAG_RETRY_EXPAND | 정확도 | 근거 부족 (최대 2~3회) |
| FB_RAG_SWITCH_SOURCE | 안전/정확도 | 소스 차단/QoD 낮음 |
| FB_COST_DOWNSHIFT | 비용 | 예산 초과 |
| FB_REQUIRE_APPROVAL | 안전 | 승인 필요 |
| FB_POLICY_MASK | 안전 | 민감정보 탐지 |
| FB_OUTPUT_REFORMAT | 정확도 | 출력 스펙 위반 |
| FB_OUTPUT_MINIMAL | 속도/안전 | 연쇄 오류 |
| FB_MEMORY_META_ONLY | 안전 | 메모리 정책 거부 |
| FB_ROUTE_SAFE_NODE | 안전/비용 | 라우트 미발견 |
| FB_DENY_WITH_REASON | 안전 | 정책 차단 |
| FB_RESTRICT_GENERAL_INFO | 안전 | 법률/의료 차단 |

## 12.5 Failure → Fallback 매핑 (20쌍)

| failure_code | fallback_id |
|---|---|
| OC_I1_PARSE_FAIL | FB_INTENT_HEURISTIC_PARSE |
| OC_I1_AMBIGUOUS_UNRESOLVED | FB_ASK_CLARIFICATION |
| OC_I2_RAG_NO_SOURCE | FB_RAG_RETRY_EXPAND |
| OC_I2_EVIDENCE_QOD_LOW | FB_RAG_RETRY_EXPAND |
| OC_I2_SOURCE_POLICY_BLOCK | FB_RAG_SWITCH_SOURCE |
| OC_I2_TIMEOUT | FB_RAG_SWITCH_SOURCE |
| OC_I3_MEMORY_POLICY_DENY | FB_MEMORY_META_ONLY |
| OC_I3_APPROVAL_REQUIRED | FB_REQUIRE_APPROVAL |
| OC_I3_COMMIT_FAIL | FB_DENY_WITH_REASON |
| OC_I4_OUTPUT_SPEC_VIOLATION | FB_OUTPUT_REFORMAT |
| OC_I4_CITATION_MISSING | FB_POLICY_MASK |
| OC_I4_MASK_FAIL | FB_POLICY_MASK |
| OC_I5_POLICY_BLOCK | FB_DENY_WITH_REASON |
| OC_I5_APPROVAL_REQUIRED | FB_REQUIRE_APPROVAL |
| OC_I5_COST_OVER_BUDGET | FB_COST_DOWNSHIFT |
| OC_I5_EVIDENCE_INSUFFICIENT | FB_RAG_RETRY_EXPAND |
| OC_I5_ROUTE_NOT_FOUND | FB_ROUTE_SAFE_NODE |
| POLICY_DENY | FB_DENY_WITH_REASON |
| GT_ERR_COST_LIMIT | FB_COST_DOWNSHIFT |
| TOOL_TIMEOUT | FB_RAG_RETRY_EXPAND |

## 12.6 LogEventSchema (7필드)

```python
event_type: str      # D2 EventTypeRegistry SOT
producer: str        # I-모듈/컴포넌트
when: str            # 발생 조건
payload: dict        # trace_id, decision_id 등
severity: Literal["info","warn","error","critical"]
sinks: List[str]     # file, db, audit
links: dict          # failure_code, fallback_id, policy_check
```

---

# 13. API 계약 (88 엔드포인트)

## 13.1 Tauri IPC Commands (72개)

**명명 규칙**: `vamos:{category}:{action}`

| 카테고리 | 건수 | 예시 |
|---------|------|------|
| Core (decision/workflow/session) | 15 | `vamos:decision:create/get/list/lock/event` |
| Agent (node/pipeline/marketplace) | 15 | `vamos:node:dispatch/response/profile/list/register` |
| Storage (memory/vector/cache/graphrag/qod) | 18 | `vamos:memory:save/get/search/delete/list` |
| Safety (policy/cost/approval/guardrails/rbac/autonomy) | 19 | `vamos:policy:check/result/block_event` |
| UI (log/config/theme/notification) | 5 | `vamos:ui:log_stream/config_get/config_set` |

## 13.2 Python-Rust JSON-RPC (13개)

| Method | 스키마 소스 |
|--------|-----------|
| langgraph.workflow.run | D5 WorkflowOutputEnvelope |
| langgraph.stage.execute | D5 WorkflowStage |
| langgraph.decision.create | D2 Decision |
| langgraph.node.dispatch | D3 NodeEnvelope |
| langgraph.verify.run_chain | D5 VerifyChainEntry |
| embedding.encode | D6 KBEmbeddingRecord |
| embedding.store | D6 VectorStoreAdapter |
| llm.generate | D4 BrainAdapterResponse |
| llm.record_invoke | D4 InfraInvokeResult |
| llm.rate_limit.get | D4 RateLimitConfig |
| mcp.bridge.init | D3 MCPBridgeLayer |
| mcp.bridge.health | D3 MCPBridgeLayer |
| mcp.tools.discover | D3 ToolCallRegistry |

## 13.3 MCP Tool Protocol (3개)
- `tools/call` (Streamable HTTP)
- `mcp.tool_registry.get` / `mcp.tool_registry.list` (내부)

## 13.4 응답 규격

**성공**: `{ success: true, data: T, trace_id: string }`
**에러**: `{ success: false, error: { code: string, message: string, trace_id: string } }`

## 13.5 RBAC 권한 매트릭스

| 카테고리 | 최소 역할 | 비고 |
|---------|----------|------|
| Core 읽기 | VIEWER | - |
| Core 실행 | OPERATOR | - |
| Node 등록 | ADMIN | - |
| Storage 삭제 | ADMIN | - |
| Safety 변경 | ADMIN | - |
| Autonomy L3 | OWNER | - |

---

# 14. 프로젝트 구조 (Monorepo, LOCK)

```
vamos/
├── .github/workflows/       # CI/CD
├── src/                     # React 프론트엔드
│   ├── components/          # common, layout, canvas, artifacts, notifications,
│   │                        # autonomy, decision, memory, cost, log
│   ├── pages/               # Dashboard, Chat, Workflow, Memory, Settings, Log
│   ├── hooks/               # useTauriIPC, useDecision, useWorkflow, useCost...
│   ├── stores/              # appStore, decisionStore, workflowStore...
│   ├── types/               # decision, logEvent, blueNode, workflow...
│   └── utils/               # formatters, validators, constants
├── src-tauri/               # Rust Tauri 백엔드
│   └── src/
│       ├── commands/        # decision, workflow, memory, cost, settings, log
│       ├── bridge/          # python_manager, ipc_protocol
│       ├── state/           # app_state
│       └── models/          # decision, log_event, envelope
├── backend/                 # Python AI/ML
│   └── vamos_core/
│       ├── orange_core/     # decision_kernel, front_mini, i1~i5
│       ├── blue_nodes/      # base_node, dev/, research/, content/, quant/, trading/
│       ├── infra/           # brain/, tools/, prompt/, rate_limit/, backup/
│       ├── agent/           # graph/, pipeline/, circuit_breaker, hitl
│       ├── storage/         # memory/, vector/, graph/, cache/, db/, logging/, kb/
│       ├── safety/          # policy/, approval/, cost/, guardrails/, rbac/, autonomy/
│       ├── schemas/         # contracts.py (32개 Pydantic v2), enums.py
│       └── mcp/             # bridge, server, client, tool_discovery
├── shared/types/            # JSON Schema (Golden Source)
├── config/                  # default.toml, llm/, embedding/, storage/, safety/, mcp/
└── tests/                   # unit, integration, e2e
```

**타입 동기화**: Python `contracts.py`가 정본(SOT) → TypeScript/Rust 타입 생성

---

# 15. 기술 스택 (Tech Combo)

| 항목 | V1 (로컬/개인) | V2 (서버) | V3 (운영형) |
|------|---------------|-----------|------------|
| **LLM** | Ollama + GPT-4o mini | GPT-4o mini + Sonnet | vLLM + 외부 조합 |
| **Embedding** | BGE-M3 (로컬, 무료) | text-embedding-3-small + BGE-M3 | text-embedding-3-large + BGE-M3 |
| **Vector** | Chroma 로컬 | Qdrant 서버 | Qdrant Cloud |
| **Graph** | JSON (NetworkX) | Neo4j Community | Neo4j Aura |
| **Storage** | SQLite + JSONL | Postgres | 매니지드 Postgres |
| **Logging** | JSONL + SQLite | Postgres + JSONL | Loki/ELK |
| **Deploy** | Windows/WSL | Docker Compose | K8s |
| **UI** | Tauri 2.0 + React | + PWA | + 모바일 네이티브 |
| **Guardrails** | NeMo + Guardrails AI (2층) | + LlamaGuard (3층) | + 사후 감사 (4층) |
| **Framework** | **LangGraph** (LOCK) | 동일 | 동일 |
| **MCP 전송** | Streamable HTTP (LOCK) | 동일 | 동일 |

---

# 16. 버전 로드맵 (V0→V3)

## V0 — 최소 구현 ("돌아가는 코어") — cf. PLAN-3.0 §3.1: "Foundation Stage, 전체 골격 준비 단계"
- ORANGE CORE I-1~I-5 최소 기능
- Gate: deny + downshift + hold 최소
- Logging: LogEvent 최소 (jsonl 1개)
- Storage: L0만 (session)
- Infra: 단일 모델 또는 2단계 downshift
- UI: CLI 또는 최소 대시보드

## V1 — 초기 제품화 ("운영 가능한 설계") — cf. PLAN-3.0 §1: ORANGE CORE 안정화, RAG·메모리·라우팅 기반 구축
- Storage: L1(project) + QoD 반영
- Evidence: 다중 소스 + 재검색 폴백
- Blue Nodes: 2~3개 핵심 노드
- Infra: Multi-Brain Adapter (2~3 brain)
- Safety: 승인 워크플로우 표준화
- UI: Builder/Hologram 골격
- 비용 상한: 월 ₩40,000

## V2 — 확장/팀용 서버 — cf. PLAN-3.0 §1: BLUE NODE 확장, 도메인별 전문화, 멀티모달 기반 강화
- Postgres, Qdrant, Docker Compose
- Extended Thinking, 대화 Fork
- P1 확장 도메인 활성화
- 4-Layer Guardrails 전체 (L1~L4)
- 비용 상한: 월 ₩93,000

## V3 — 엔터프라이즈/고도화 — cf. PLAN-3.0 §1: Self-evo 고도화, 외부 연동 확장, 고급 분석 엔진
- K8s, 관측 스택, GPU Brain
- Self-evo (S-Module) 본격 활성
- P0/P1/P2 전체 운용
- 고급 메모리, GraphRAG
- 실시간 카메라/화면 분석
- 비용 상한: 월 ₩266,000

### V-버전 전환 체크리스트

**V1→V2**: QoD ≥ 0.85 (30일), RAG 정확도 ≥ 60%, 메모리 승격/강등 오류율 < 1%, P0 테스트 100%, 비용 초과 없이 30일, 사용자 승인

**V2→V3**: QoD ≥ 0.90 (60일), 2단 LLM 최적화 완료, P1 고급 테스트 통과, Self-evo 체계 검증, V3 비용 재검토 + 승인, Loki+Grafana 배포

---

# 17. 전체 LOCK 결정사항

## 17.1 아키텍처 LOCK

| 항목 | LOCK 내용 |
|------|----------|
| 문서 우선순위 | RULE > PLAN > DESIGN LOCK > DESIGN 본문 > 스키마 |
| 변경관리 | 삭제 금지, 창작 금지, Major는 07 Approval |
| E-*/EVX-* | E-*=외부기능, EVX-*=Verify 확장, E 변형 금지 |
| S-#/S#_ | S-#=모듈 ID(하이픈), S#_=상태(언더스코어) |
| A-6/A-7 | A-6=Federated, A-7=Remote Executor |
| Monorepo | 저장소 구조 확정 |
| LangGraph | Agent Workflow 프레임워크 (import 아닌 패턴 참조) |
| LangChain import | 금지 (DEC-002), 패턴만 참조 |

## 17.2 핵심 엔진 LOCK

| 항목 | LOCK 내용 |
|------|----------|
| Decision Lock | 한 시점/한 컨텍스트/한 결론 → locked=true |
| Gate 우회 불가 | Policy→Approval→Cost→Evidence 필수 |
| Self-check 임계값 | P0:70, P1:75, P2:80 |
| Self-check 루프 | 자동 Soft 1회만, 이후 승인 필요 |
| L2 저장 정책 | 기본 "승인 필요" |
| 외부 프레임워크 | 실행 오케스트레이션만, Gate 우회 금지 |
| 코드 실행 격리 | Docker 샌드박스 필수 (네트워크 차단, 30초) |
| MCP 전송 | Streamable HTTP (DEC-017) |
| 동시성 | 큐+세마포어 (MAX_CONCURRENT_BLUE_NODES=3, TOOLS=5) |
| Multi-Brain Failover | GPT-4o→Claude→Ollama (3회 타임아웃 시 전환) |

## 17.3 비용/안전 LOCK

| 항목 | LOCK 내용 |
|------|----------|
| V1 비용 상한 | ₩40,000/월 ($30) |
| V2 비용 상한 | ₩93,000/월 ($70) |
| V3 비용 상한 | ₩266,000/월 ($200) |
| Downshift | 80% warn/force_mini, 100% block |
| RBAC | OWNER/ADMIN/OPERATOR/VIEWER |
| Autonomy 기본 | L1 (SUPERVISED) |
| Guardrails | 4-Layer (L1 NeMo + L2 Guardrails AI + L3 LlamaGuard + L4 사후감사) |
| P2 자동 OFF | 세션 종료 시 즉시 OFF |
| Non-goal | 7개 절대 금지 항목 |
| 7개 불변 구역 | safety/cost/approval/non_goals/audit/retention/consent |

## 17.4 데이터/인프라 LOCK

| 항목 | LOCK 내용 |
|------|----------|
| QoD 스케일 | 0.0~1.0 (DEC-010) |
| QoD 가중치 | relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20 (DEC-014) |
| Semantic Cache | cosine ≥ 0.95 |
| Embedding | V1=BGE-M3(로컬)/text-embedding-3-small(클라우드) (DEC-005) |
| Vector | V1=Chroma, V2+=Qdrant 우선 |
| GraphRAG | 하이브리드 RAG (DEC-004) |
| RAG Pipeline | 6단계 (Collect→Chunk→Embed→Store→Retrieve→Generate) |
| 병렬 실행 상한 | 3 |
| 설정 우선순위 | ENV > config.toml > default |
| 로깅 | JSON Structured, 평문 금지 |

## 17.5 Self-evo LOCK

| 항목 | LOCK 내용 |
|------|----------|
| Self-evo 원칙 | 제안만 가능, 자동 적용 절대 금지 |
| 허용 도메인 | 6개 (프롬프트/도구/메모리/출력/워크플로우/모델) |
| 불변 구역 | 7개 (정체성/Non-goal/법규/비용/승인/P0/P2생성) |
| 롤백 잠금 | 동일 제안 롤백 후 14일 재적용 금지 |

## 17.6 UI/UX LOCK

| 항목 | LOCK 내용 |
|------|----------|
| 프레임워크 | Tauri 2.0 + React |
| 2-View | Builder + Hologram |
| 3-Panel | Left + Center + Right |
| P2 재확인 | 모달 (DEC-011) |
| 비용 경고 색상 | 80%=#FBBF24, 100%=#EF4444 (DEC-015) |
| Decision Lock UI | 결론 변경 금지, 포맷만 갱신 |
| 이벤트 네이밍 | `ui.{layer}.{subject}.{action}` |

---

# 18. AI INVESTING (AINV) 통합 명세

> **상세**: `VAMOS_AI_INVESTING_SPEC.md` 참조 (1,368줄, 24개 섹션)

## 18.1 시스템 정의
- **목적**: 분석 전용 AI 투자 보조 시스템 (실거래 절대 금지, Non-goal)
- **핵심 지표**: Win Rate ≥ 51%, Sharpe Ratio ≥ 1.0, Decay Rate < 30%
- **5-Agent 구조**: Perplexity(데이터 발견) → Gemini(분석/PM) → ChatGPT(로직/코드) → Claude(감사/검증) → Copilot(구현)

## 18.2 7-Layer 데이터 아키텍처
```
L1 Collection (83개 소스) → L2 Processing (DQ 검증) → L3 Storage (TimescaleDB/Chroma)
→ L4 Strategy Engine (96 전략) → L5 Execution (Paper Only) → L6 Monitoring (Grafana)
→ L7 VAMOS Core Integration (Gate/Approval)
```

## 18.3 83개 데이터 소스 (Tier 분류)

| Tier | 건수 | 주요 소스 |
|------|------|----------|
| **P0 Critical** | 16 | FRED, ECOS, KRX, CME, VIX, SEC EDGAR, DART, Glassnode, DeFiLlama |
| **P1 High** | 9 | Federal Register, arXiv(q-fin), PR Newswire, EIA, Token Terminal |
| **S0/S1 Scraper** | 17+ | Goldman Insights, TradingView, SwaggyStocks, OpenInsider |
| **KB Knowledge** | 41+ | Bloomberg, Reuters, CoinDesk, Reddit, Kaggle, 학습 플랫폼 |

## 18.4 96개 투자 전략 카탈로그

| 카테고리 | 건수 | 대표 전략 |
|---------|------|----------|
| Technical Analysis | 25 | MACD Crossover, RSI+BB, Ichimoku, Supertrend |
| Chart Patterns | 15 | Head&Shoulders, Cup&Handle, Harmonic |
| Quantitative | 12 | Mean Reversion, Pairs Trading, PCA |
| Factor Investing | 8 | Value, Momentum, Quality, Multi-Factor |
| Options | 10 | Iron Condor, Covered Call, MAX_PAIN |
| Event-Driven | 6 | Earnings Momentum, Merger Arb, FOMC |
| ML/AI-Based | 8 | XGBoost, LSTM, FinBERT, RL(PPO/DQN) |
| Crypto-Specific | 6 | Grid Trading, DCA, Funding Arb |
| Portfolio/Risk | 6 | Kelly Criterion, Risk Parity, ATR Sizing |

## 18.5 데이터 스키마 (LOCK)

### VAMOS_OHLCV_PLUS
```json
{ "entity_id": "SPY", "timestamp_utc": "ISO8601", "data_type": "candle|tick|economic|onchain",
  "values": { "open": "485.20", "high": "487.50", "low": "484.10", "close": "486.80",
              "volume": "52341000", "vwap": "485.90" },
  "metadata": { "source": "yfinance", "confidence": 0.95, "frequency": "1d" } }
```

### VAMOS_EVENT
```json
{ "event_id": "evt_abc", "event_type": "filing|news|sentiment|corporate_action",
  "sentiment_score": 0.65, "impact_level": 3, "entities": ["AAPL","MSFT"] }
```

## 18.6 51% Gate (백테스팅 검증, LOCK)

| 지표 | 임계값 | 실패 시 |
|------|--------|--------|
| Win Rate | ≥ 0.51 (51%) | GATE_WINRATE_FAIL |
| Sharpe Ratio (Test) | ≥ 1.0 | GATE_SHARPE_FAIL |
| Decay Rate | < 0.30 (30%) | OVERFITTING_DECAY_FAIL |
| Test Trade Count | ≥ 30 | INSUFFICIENT_SAMPLE |

**공식**:
- `Sharpe = (Mean Return - Rf) / Std × √(252)` (일봉 기준)
- `Decay = max(0, (Sharpe_Train - Sharpe_Test) / |Sharpe_Train|)`
- `Kelly f* = (b×p - q) / b` (Half-Kelly = f*/2, 최대 25%)

## 18.7 법적 준수 (A-Mode, LOCK)

| 규칙 | 국가 | 설명 | 위반 시 |
|------|------|------|--------|
| **Wash Sale Rule** | USA | 손실 매도 후 30일 내 재매수 금지 | 주문 차단 |
| **PDT Rule** | USA | $25K 미만 계좌: 5일 내 데이트레이드 3회 제한 | 주문 차단 |
| **Uptick Rule** | KOR | 공매도는 직전 종가 이상에서만 | 주문 차단 |

## 18.8 AINV 전용 기술 스택 (14, LOCK)

| 컴포넌트 | 용도 |
|---------|------|
| Python ≥3.12 | 메인 언어 |
| TimescaleDB | 시계열 데이터 |
| Kafka ≥3.6 | 실시간 스트리밍 |
| Airflow ≥2.8 | DAG 스케줄링 (06:00~06:35 일일 파이프라인) |
| Grafana ≥10.0 | 모니터링 (8+ 패널) |
| ChromaDB ≥0.4 | 벡터 임베딩 |
| MinIO/S3 | 오브젝트 스토리지 |
| FinBERT | 금융 감성 분석 |
| SHAP/LIME | 모델 설명 가능성 |
| Stable-Baselines3 | 강화학습 (PPO/DQN) |

## 18.9 AINV 안전 규칙 (기존 9.8 확장)
- VaR > 포트폴리오 5% → 자동 경고 + P2 승인 필수
- 매매 추천 응답 → 100% 면책 삽입
- 금융 환각 자동 탐지 (PE/PBR 검증)
- 레드팀 공격 패턴 DB 100+건
- 감정적 투자 방지: FOMO/패닉 감지 → 15분 쿨다운

---

# 19. SDAR (Self-Diagnosis & Auto-Repair) 설계

> **상세**: `VAMOS_SDAR_DESIGN_SPECIFICATION.md` 참조 (1,643줄, 10개 섹션 + 3개 부록)

## 19.1 목적
알집(ALZip)의 오류 자동 복구처럼, VAMOS가 오류를 **스스로 진단하고 단계적 자율수준에 따라 복구/수정**하는 시스템.

## 19.2 모듈 등록
- **모듈 ID**: I-25 (SDAR Engine)
- **상태**: COND (V1: OFF, V2: COND, V3: ON)
- **연결 모듈**: S-1, S-4, I-6, I-16, I-20, S-8, I-19, I-8

## 19.3 5-Layer 파이프라인

```
[L1 DETECTION] → [L2 DIAGNOSIS] → [L3 PRESCRIPTION] → [L4 REPAIR] → [L5 VERIFICATION]
 실시간 감지       근본 원인 분석     처방 생성           수리 실행       검증/롤백
```

| Layer | 역할 | 주요 기능 |
|-------|------|----------|
| **L1 Detection** | 이상 감지 | 헬스체크(30초), 오류패턴 감지, 이상행동 탐지 |
| **L2 Diagnosis** | 원인 분석 | 로그 상관분석, 의존성 그래프, 패턴 매칭 |
| **L3 Prescription** | 처방 생성 | 수정 후보 1~5개 생성, 위험도 평가, 복구 계획 |
| **L4 Repair** | 수리 실행 | **단계적 자율수준(AR-Level)**에 따른 자동/수동 실행 |
| **L5 Verification** | 검증 | 수리 후 검증, 5분 관찰, 롤백 트리거 |

## 19.4 단계적 자율수준 (AR-Level, 핵심)

| Level | 명칭 | 자동 수리 범위 | 승인 | 예시 |
|-------|------|-------------|------|------|
| **AR-L0** | MANUAL | 없음 | 모두 사람 | - |
| **AR-L1** | NOTIFY_ONLY | 진단+제안만 | 사람 결정 | "설정 오류 발견, 이렇게 수정 제안" |
| **AR-L2** | AUTO_SAFE | 저위험만 자동 | 저위험 자동 | 서비스 재시작, 캐시 정리, API 재시도, 모델 전환 |
| **AR-L3** | AUTO_MODERATE | 중위험까지 자동 | 알림+자동(가역만) | 프롬프트 패치, 설정 변경, 인덱스 재구성 |
| **AR-L4** | AUTO_AGGRESSIVE | 고위험까지 자동 | 알림+자동(스냅샷) | 코드 핫픽스, 스키마 마이그레이션 |

**기본값**: AR-L2 (VAMOS L1 SUPERVISED 철학과 일치)

**RBAC 매핑**: OWNER→AR-L4, ADMIN→AR-L3, OPERATOR→AR-L2

## 19.5 오류 분류 & AR-Level 매핑

| 카테고리 | 예시 | 자동 수리 가능 수준 |
|---------|------|-------------------|
| **A. 인프라** | DB 연결, API 429, 디스크 부족 | AR-L2 (대부분 자동) |
| **B. 모델/AI** | 환각, 품질 저하, 라우팅 실패 | AR-L3 (중위험) |
| **C. 로직** | 워크플로우 멈춤, Gate 오설정 | AR-L3~L4 |
| **D. 코드** | 버그, 회귀, 의존성 깨짐 | AR-L4 (고위험) |
| **E. 보안** | 인젝션, 무단접근, 데이터 유출 | **NEVER_AUTO** (즉시 차단+사람) |

## 19.6 수리 액션 카탈로그

**LOW (AR-L2)**: restart_service, clear_cache, retry_with_backoff, switch_model_fallback, adjust_rate_limit

**MEDIUM (AR-L3)**: patch_prompt_template, update_config, rotate_api_key, rollback_to_snapshot, compress_logs

**HIGH (AR-L4)**: patch_code_hotfix, migrate_schema, reinstall_dependency, rebuild_vector_index

**NEVER_AUTO** (10개): [7개 불변구역] modify_safety_rules, change_cost_ceiling, alter_approval_flow, modify_non_goals, change_audit_format, alter_data_retention, modify_user_consent / [3개 운영금지] escalate_own_privilege, disable_guardrails, bypass_gate

## 19.7 안전 제약 (LOCK)
- RULE 1.3 7개 불변구역 + 3개 운영금지(총 10개): NEVER_AUTO (`frozenset` 강제)
- 시간당 동일 이슈 최대 3회 자동 수리
- MEDIUM/HIGH 수리 전 **필수 스냅샷**
- **모든 수리에 사람 알림** 필수
- Emergency Kill Switch: 모든 역할에서 즉시 비활성화 가능

## 19.8 버전 로드맵

| 버전 | AR-Level | 가용 액션 |
|------|---------|----------|
| V1 | AR-L2 | LOW 5개 (재시작, 캐시, 재시도, 모델전환, Rate조정) |
| V2 | AR-L3 | + MEDIUM 5개 (프롬프트패치, 설정변경, 키회전, 롤백, 로그압축) |
| V3 | AR-L4 | + HIGH 4개 (코드핫픽스, 스키마 마이그레이션, 의존성, 인덱스) |

## 19.9 상태 머신
```
SDAR_S0_MONITORING → SDAR_S1_DETECTED → SDAR_S2_DIAGNOSED → SDAR_S3_PRESCRIBED
→ SDAR_S4_REPAIRING → SDAR_S5_VERIFIED → SDAR_S6_DONE
```

---

# 20. Agent Teams (에이전트 팀) 통합 명세

> **상세**: `VAMOS_AGENT_TEAMS_SPEC.md` 참조 (2,188줄, 11개 섹션)

## 20.1 시스템 정의
- **목적**: VAMOS의 복합 작업을 Lead Agent + Sub-Agents 위임 구조로 병렬/순차 처리
- **기반**: LangGraph (LOCK) 워크플로우 + MCP 프로토콜
- **Claude Agent Teams 아키텍처 참조**: S7-A-001

## 20.2 Agent 계층 구조

```
ORANGE CORE (Decision Engine)
    ↓ DelegationPlan 생성
Lead Agent (Supervisor)
    ├── Research Agent ── E-2(Web Search), E-3(Doc Parser)
    ├── Coding Agent ──── E-1(Coding Helper), E-4(Code Executor)
    ├── Quant Agent ───── AINV 전략 엔진, 백테스팅
    ├── Content Agent ─── E-3, I-11(Output Composer)
    ├── Trading Agent ─── AINV 연동, 51% Gate
    └── SDAR Agent ────── I-25(SDAR Engine)
```

## 20.3 위임(Delegation) 시스템
- **위임 결정 알고리즘**: 5단계 스코어링 (domain_match × skill_match × availability × cost_fit × history_score)
- **Task Decomposition**: 4전략 (Sequential, Parallel, Map-Reduce, Pipeline)
- **위임 체인**: 최대 3단계 깊이 (Lead → Sub → Sub-sub)
- **제약**: 최대 병렬 에이전트 V1=3, V2=5, V3=10

## 20.4 협업 패턴 (5가지, LOCK)

| 패턴 | 설명 | 용도 |
|------|------|------|
| **Sequential** | A → B → C 순차 실행 | 의존성 있는 작업 |
| **Parallel** | A \| B \| C 병렬 실행 후 합산 | 독립 작업 동시 처리 |
| **Debate** | Agent 간 토론 → 합의 (A-4 연동) | 복잡한 판단/분석 |
| **Supervisor** | Lead가 Sub 결과를 검증/재지시 | 품질 보증 |
| **Handoff** | Agent 간 컨텍스트 인계 | 도메인 전환 |

## 20.5 기존 시스템 통합

| 통합 대상 | 연동 방식 |
|----------|----------|
| **5 Gates** | 에이전트 생성/실행 전 PolicyGate + CostGate 통과 필수 |
| **9-State Machine** | S4_EXECUTING에서 Agent Teams 활성화 |
| **RBAC** | OWNER→전체, ADMIN→Debate+Parallel, OPERATOR→Sequential만 |
| **비용 관리** | 에이전트별 비용 추적, 팀 전체 예산 = 작업 예산의 80% |
| **Delegation Attack 방어** | Agent 간 통신 HMAC 검증, 권한 상속 불가 |

## 20.6 Pydantic v2 스키마 (핵심)
- `AgentTeamConfig`: 팀 구성 (max_agents, collaboration_pattern, budget)
- `AgentTask`: 하위 작업 정의 (task_type, assigned_agent, dependencies)
- `DelegationPlan`: 위임 계획 (decomposition_strategy, assignments[])
- `AgentResult`: 에이전트 결과 (status, output, cost_used, duration)
- `TeamResult`: 팀 최종 결과 (merged_output, total_cost, agent_reports[])

## 20.7 API 엔드포인트
- **Tauri IPC**: 10개 (`vamos:agent:create_team`, `vamos:agent:delegate`, `vamos:agent:cancel` 등)
- **JSON-RPC**: 12개 (`agent.create_team`, `agent.get_status`, `agent.debate.start` 등)

## 20.8 버전 로드맵

| 버전 | 에이전트 수 | 패턴 | 주요 기능 |
|------|-----------|------|----------|
| **V1** | 2~3 | Sequential, Supervisor | 기본 위임, Lead+Sub |
| **V2** | 5~10 | + Parallel, Debate | 병렬 실행, 토론 모드, Handoff |
| **V3** | 10~50+ | + 동적 생성/해체 | 자율 팀 구성, Mesh, Federation |

## 20.9 LOCK 결정사항
- LangGraph 기반 워크플로우 (LOCK)
- 최대 위임 깊이 3단계 (LOCK)
- Agent 간 통신 HMAC 검증 필수 (LOCK)
- NEVER_AUTO 영역은 Agent도 접근 불가 (LOCK)

---

# 21. STEP7 AI기술보강 3,101건 통합 현황

> **상세**: `VAMOS_STEP7_보강_통합명세서.md` (1,519줄) + 카테고리별 상세명세서 참조

## 21.1 통합 현황 요약

| 구분 | STEP6 | STEP7 | 합계 |
|------|-------|-------|------|
| 총 항목 | 1,556건 | 1,545건 | **3,101건** |
| 적용 완료 | 1,556건 (100%) | 1,545건 (100%) | **3,101건** |

## 21.2 STEP7 16개 카테고리 상세 반영 문서

| 카테고리 | 건수 | 반영 문서 | 상세 수준 |
|---------|------|----------|----------|
| **A** 경쟁분석/혁신 | 316 | STEP7_A-E_상세명세서 | 구현방식+기술스택+연동 |
| **B** 대화프로세스 | 35 | STEP7_A-E_상세명세서 | 구현방식+기술스택+연동 |
| **C** UI/UX | 104 | STEP7_A-E_상세명세서 | 구현방식+기술스택+연동 |
| **D** 메모리/저장소 | 82 | STEP7_A-E_상세명세서 | 구현방식+기술스택+연동 |
| **E** 보안/안전 | 92 | STEP7_A-E_상세명세서 | 구현방식+기술스택+연동 |
| **F** 인프라/배포 | 96 | STEP7_F-I_상세명세서 | 구현방식+기술스택+연동 |
| **G** 벤치마크 | 88 | STEP7_F-I_상세명세서 | 구현방식+기술스택+연동 |
| **H** 비즈니스 | 78 | STEP7_F-I_상세명세서 | 구현방식+기술스택+연동 |
| **I** AI Investing | 106 | STEP7_F-I + AI_INVESTING_SPEC | 구현방식+기술스택+연동 |
| **J** 멀티모달 | 98 | STEP7_J-M_상세명세서 | 구현방식+기술스택+연동 |
| **K** 에이전트 | 86 | STEP7_J-M + AGENT_TEAMS_SPEC | 구현방식+기술스택+연동 |
| **L** 개발자도구 | 82 | STEP7_J-M_상세명세서 | 구현방식+기술스택+연동 |
| **M** PKM/지식관리 | 78 | STEP7_J-M_상세명세서 | 구현방식+기술스택+연동 |
| **N** 워크플로우 | 44 | STEP7_N-P_보강_상세명세서 | 구현방식+기술스택+연동 |
| **O** 교육/학습 | 36 | STEP7_N-P_보강_상세명세서 | 구현방식+기술스택+연동 |
| **P** 건강/웰니스 | 42 | STEP7_N-P_보강_상세명세서 | 구현방식+기술스택+연동 |
| **보강** 추가항목 | 82 | STEP7_N-P_보강 + 통합명세서 | 구현방식+기술스택+연동 |

## 21.3 우선순위별 분포

| 우선순위 | V1 | V2 | V3 | 합계 |
|---------|-----|-----|-----|------|
| CRITICAL | ~120 | ~80 | ~38 | ~238 |
| HIGH | ~350 | ~250 | ~86 | ~686 |
| MEDIUM | ~180 | ~220 | ~88 | ~488 |
| LOW | ~20 | ~60 | ~36 | ~116 |

## 21.4 산출물 문서 체계

```
output/updated/
├── VAMOS_MASTER_SPECIFICATION.md      ← 단일 참조점 (이 문서)
├── VAMOS_BEGINNER_GUIDE.md            ← 초보자 가이드
├── VAMOS_AI_INVESTING_SPEC.md         ← AINV 상세 (1,368줄)
├── VAMOS_SDAR_DESIGN_SPECIFICATION.md ← SDAR 상세 (1,643줄)
├── VAMOS_AGENT_TEAMS_SPEC.md          ← Agent Teams 상세 (2,188줄)
├── VAMOS_CLOUD_LIBRARY_SPEC.md        ← Cloud Library 상세
├── VAMOS_STEP7_보강_통합명세서.md       ← STEP7 교차통합 (1,519줄)
├── VAMOS_STEP7_A-E_상세명세서.md       ← A~E 629건 상세
├── VAMOS_STEP7_F-I_상세명세서.md       ← F~I 368건 상세
├── VAMOS_STEP7_J-M_상세명세서.md       ← J~M 344건 상세
├── VAMOS_STEP7_N-P_보강_상세명세서.md   ← N~P+보강 204건 상세
└── (28개 기존 D2.0/D2.1/BASE/PLAN/PHASE 문서)
```

---

> **끝** — 본 문서는 VAMOS AI의 28개 소스 문서 + AI INVESTING 전체 명세 + SDAR 자가진단/자동복구 설계 + Agent Teams 통합 명세 + STEP7 3,101건 AI기술보강 전체에서 추출한 모든 내용을 빠짐없이 통합한 것입니다. 구현 시 본 문서를 단일 참조점(Single Source of Truth)으로 사용하십시오.

---

<\!-- END OF DOCUMENT -->
