# v23 Extension Items 구조화 종합 계획서

> **버전**: v1.0
> **작성일**: 2026-03-24
> **목적**: sot 2/5-4_v23-Extension-Items/을 v23 확장항목 추적 인덱스 정본으로 구조화
> **Status**: APPROVED — Phase 8 QC B+ (2026-03-26), Phase 10 QC A- (2026-03-27)
> **Tier**: 5 — Quality/Cross-cutting (추적 인덱스)
> **SOT 출처**: Part2 V2-Phase 2, V2-Phase 3, V3-Phase 2, V3-Phase 3
> **Part2 상태**: SHELL (이름만 존재, ~87건)

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [목표 구조](#2-목표-구조)
3. [권한 체계 선언](#3-권한-체계-선언)
4. [거버넌스 규칙](#4-거버넌스-규칙)
5. [선행작업](#5-선행작업)
6. [이슈 해결 매핑](#6-이슈-해결-매핑)
7. [Phase 실행 계획](#7-phase-실행-계획)
8. [파일 역할 분리 명세](#8-파일-역할-분리-명세)
9. [충돌 해결 프로토콜](#9-충돌-해결-프로토콜)
10. [검증 체크리스트](#10-검증-체크리스트)
11. [보완 사항](#11-보완-사항)
12. [FINAL REVIEW 결과](#12-final-review-결과)
13. [L3 전수 승급 계획](#13-l3-전수-승급-계획)
14. [실행 약점 대응 계획](#14-실행-약점-대응-계획)
- [부록 A — 우선순위별 구현 계획](#부록-a--우선순위별-구현-계획)

---

## 1. 현재 상태 분석

### 1.1 정본 문서 현황

| 문서 | 위치 | 줄수 | 역할 |
|------|------|------|------|
| **Part2 V2-Phase 2** | Part2 구현가이드 | SHELL | 51건 항목명 + 1줄 설명만 존재 |
| **Part2 V2-Phase 3** | Part2 구현가이드 | SHELL | 14건 항목명 + 1줄 설명만 존재 |
| **Part2 V3-Phase 2** | Part2 구현가이드 | SHELL | 6건 항목명 + 1줄 설명만 존재 |
| **Part2 V3-Phase 3** | Part2 구현가이드 | SHELL | 16건 항목명 + 1줄 설명만 존재 |
| **V23_EXTENSION_ITEMS_인덱스.md** | `sot 2/5-4_v23-Extension-Items/` | 218줄 | 87건 전수 인덱스 (Phase/우선순위/SOT 2 참조 매핑) |

### 1.2 sot 2/ 현재 파일

```
5-4_v23-Extension-Items/
├── V23_EXTENSION_ITEMS_인덱스.md       (218줄, 87건 추적 인덱스)
├── 01_high-priority/                    (빈 폴더)
├── 02_medium-priority/                  (빈 폴더)
└── 03_low-priority/                     (빈 폴더)
```

### 1.3 핵심 문제

| # | 문제 | 심각도 | 설명 |
|---|------|--------|------|
| P-1 | SHELL 상태 87건 전수 | HIGH | 모든 항목이 이름 + 1줄 설명만 존재, 상세 명세 미작성 |
| P-2 | 우선순위 근거 미문서화 | HIGH | HIGH/MEDIUM/LOW 분류 기준이 명시되지 않음 |
| P-3 | 의존성 미정의 | HIGH | 87건 항목 간 의존 관계, 선후행 관계 미정의 |
| P-4 | 서브폴더 비어있음 | MEDIUM | 01/02/03 서브폴더 생성만 되고 콘텐츠 미배치 |
| P-5 | SOT 2 참조 경로 검증 미완 | MEDIUM | 인덱스의 SOT 2 참조 폴더가 실제 항목 수용 가능한지 미확인 |
| P-6 | 구현 시점 미확정 | MEDIUM | Phase별 실행 일정이 Part2에 종속되나 구체 시점 미정 |

### 1.4 Phase별 항목 분포

| Phase | 항목 수 | HIGH | MEDIUM | LOW | 비고 |
|-------|---------|------|--------|-----|------|
| V2-Phase 2 | 51 | 24 | 27 | 0 | 즉시 착수 대상 (핵심 확장) |
| V2-Phase 3 | 14 | 5 | 7 | 2 | V2 완성 단계 (고급 기능) |
| V3-Phase 2 | 6 | 0 | 2 | 4 | V3 초기 (연구 성격) |
| V3-Phase 3 | 16 | 3 | 6 | 7 | V3 후기 (미래 비전) |
| **합계** | **87** | **32** | **42** | **13** | |

### 1.5 SOT 2 카테고리별 분포

| SOT 2 폴더 | 참조 항목 수 | 주요 영역 |
|------------|-------------|----------|
| `1-1_Verifier-Reasoning-Engines/` | 12 | Core Intelligence, Reasoning |
| `1-2_Auxiliary-Modules/` | 0 | (v23 확장 항목 해당 없음) |
| `2-1_Blue-Node-Architecture/` | 7 | Memory, Knowledge Architecture |
| `2-2_COND-Modules-Detail/` | 7 | Search, RAG |
| `3-2_Multimodal-Processing/` | 4 | Voice, Document, Video |
| `3-3_PKM-Knowledge-Management/` | 5 | Knowledge Graph, Entity |
| `3-4_Workflow-RPA/` | 7 | Agent, Workflow |
| `3-5_Education-Learning/` | 3 | Spaced Repetition, Adaptive |
| `3-6_Health-Wellness-EmotionAI/` | 4 | Emotion, CBT, Mood |
| `3-7_Developer-Tools-API-SDK/` | 8 | UI/UX, Plugin, API |
| `3-8_Conversation-A2A/` | 5 | Multi-agent, A2A |
| `3-9_Business-Model-Strategy/` | 3 | Cost, Compliance, Ethics |
| `4-1_Rust-Tauri-Infrastructure/` | 10 | Infra, Security, Sync |
| `4-2_CICD-Pipeline/` | 1 | Multi-cloud |
| `4-3_MCP-Server-Client/` | 1 | Universal Tool |
| `4-4_MLOps-LLMOps/` | 6 | Continual Learning, Meta-learning |
| `5-1_Benchmark-Evaluation/` | 1 | Autonomous Testing |
| `Ai-investing-detail/` | 3 | Portfolio, Sentiment, Finance |

> **합계 검증**: 12+0+7+7+4+5+7+3+4+8+5+3+10+1+1+6+1+3 = **87건** (18개 폴더, 인덱스 87건과 정확 일치). 인덱스 원본의 SOT 2 테이블(81건 합산)은 1-1(11→12), 3-4(6→7), 3-7(7→8), 3-8(4→5), 4-1(8→10) 5개 폴더에서 6건 과소 집계 — 인덱스 SOT 2 테이블 보정 필요.

### Part2 상태 및 방식 C 접근법
- **Part2 상태**: SHELL
- **방식 C 접근법**: 전면 신규 작성

---

## 2. 목표 구조

### 2.1 폴더 트리

```
5-4_v23-Extension-Items/
├── V23_EXTENSION_ITEMS_구조화_종합계획서.md   ← 본 문서
├── V23_EXTENSION_ITEMS_인덱스.md             ← 기존 유지 (삭제 금지, 87건 정본 인덱스)
├── AUTHORITY_CHAIN.md                         ← 권한 체계 / LOCK 항목
├── CONFLICT_LOG.md                            ← 충돌 기록
├── 01_high-priority/
│   ├── _index.md                              ← HIGH 32건 추적 인덱스
│   └── (각 항목 SHELL→REF 전환 시 참조 문서 링크)
├── 02_medium-priority/
│   ├── _index.md                              ← MEDIUM 42건 추적 인덱스
│   └── (각 항목 SHELL→REF 전환 시 참조 문서 링크)
└── 03_low-priority/
    ├── _index.md                              ← LOW 13건 추적 인덱스
    └── (각 항목 SHELL→REF 전환 시 참조 문서 링크)
```

### 2.2 깊이 규칙

```
최대 2단계:
  5-4_v23-Extension-Items/ → XX_{priority}/ → 파일.md    OK
  3단계 이상 → 금지
```

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 숫자 (`01_`, `02_`, `03_`)
- **파일명**: 영문 소문자 + 언더스코어 (`.md`)
- **계획서/인덱스**: 한글 허용 (대문자 SNAKE_CASE)

### 2.4 설계 원칙

본 도메인은 **추적 인덱스** 성격이므로:

1. **상세 명세를 직접 작성하지 않음** — 각 항목의 구현 상세는 해당 SOT 2 도메인 폴더에서 관리
2. **추적과 상태 관리에 집중** — SHELL/STUB/REF 상태 전환 추적이 핵심 기능
3. **교차 참조 허브 역할** — 87건을 18개 SOT 2 폴더로 연결하는 허브

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체계

```
Level 0: VAMOS 마스터 플랜 (PLAN-3.0)
Level 1: D2.0 DESIGN 문서
Level 2: Part2 구현가이드 (Phase별 범위 정본)
Level 3: sot 2/5-4_v23-Extension-Items/ (추적 인덱스)
Level 4: 각 도메인 sot 2/ 폴더 (상세 구현 정본)
Level 5: 개별 구현 코드
```

### 3.2 v23 Extension Items 권한 체계

```
Part2 (Level 2)                          ← Phase별 범위 정의, 항목 배정 정본
  ↓ Phase 범위, 우선순위 분류
sot 2/5-4_v23-Extension-Items/ (Level 3) ← 추적 인덱스 (본 폴더)
  ↓ 상태 추적, 교차 참조
각 도메인 sot 2/ 폴더 (Level 4)          ← 상세 구현 정본
  ↓ 스키마, 로직, 인터페이스 상세
구현 코드 (Level 5)                      ← 실제 코드
```

> **핵심**: Part2가 Phase 배정 정본이며, 본 인덱스는 Part2의 SHELL 항목을 추적하는 중간 계층. 각 항목의 상세 구현은 해당 도메인의 sot 2/ 폴더가 정본.

### 3.3 문서별 정본 범위

| 문서 | canonical 범위 | 비고 |
|------|---------------|------|
| Part2 V2-P2/P3, V3-P2/P3 | 87건 항목 정의, Phase 배정, 우선순위 | 항목 정본 |
| sot 2/ 인덱스 | 87건 추적 상태, SOT 2 참조 경로 | 추적 정본 |
| sot 2/ 본 계획서 | 구조화 계획, 거버넌스, LOCK, 로드맵 | 메타 정본 |
| AUTHORITY_CHAIN.md | LOCK 항목 8개 | 변경 차단 |
| CONFLICT_LOG.md | 충돌 기록 | 이력 추적 |

### 3.4 LOCK 보호 항목

| ID | LOCK 항목 | 정본 출처 | 변경 시 필요 조치 |
|----|----------|----------|-----------------|
| LOCK-V23-01 | Phase별 범위 정의 | Part2 | Part2 승인 필수 |
| LOCK-V23-02 | 우선순위 분류 기준 (HIGH/MEDIUM/LOW) | Part2 기반 | 분기별 로드맵 리뷰 |
| LOCK-V23-03 | HIGH 32건 목록 | V23 인덱스 확정 | Part2 + 인덱스 동시 변경 |
| LOCK-V23-04 | V2-Phase 2 범위 51건 | Part2 확정 | Part2 승인 필수 |
| LOCK-V23-05 | V2-Phase 3 범위 14건 | Part2 확정 | Part2 승인 필수 |
| LOCK-V23-06 | V3-Phase 2 범위 6건 | Part2 확정 | Part2 승인 필수 |
| LOCK-V23-07 | V3-Phase 3 범위 16건 | Part2 확정 | Part2 승인 필수 |
| LOCK-V23-08 | SOT 2 참조 경로 매핑 | 인덱스 §6 확정 | 인덱스 업데이트 시 자동 반영 |

---

## 4. 거버넌스 규칙

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
> 아래는 글로벌 규칙에 추가되는 도메인 고유 규칙입니다.

### 4.1 공통 규칙

| ID | 규칙 | 설명 |
|----|------|------|
| R1 | 정본 소유자 명시 | 모든 항목에 canonical_owner 1곳 지정 (SOT 2 참조 열) |
| R2 | LOCK 재정의 금지 | LOCK 값은 정본 출처에서만 변경 가능 |
| R3 | 폴더 깊이 2단계 이하 | 3단계 이상 중첩 금지 |
| R4 | _index.md 필수 | 모든 서브폴더에 인덱스 파일 존재 |
| R6 | 기존 파일 삭제 금지 | `V23_EXTENSION_ITEMS_인덱스.md` 유지 |
| R8 | 네이밍 컨벤션 준수 | 폴더: 숫자_kebab-case, 파일: snake_case |

### 4.2 Tier 5 추적 인덱스 규칙

| ID | 규칙 | 설명 |
|----|------|------|
| R-T5-1 | 추적 전용 | 본 폴더는 상세 명세 미작성, 추적 인덱스만 관리 |
| R-T5-2 | 교차 참조 정확성 | SOT 2 참조 경로가 실제 폴더와 일치해야 함 |

### 4.3 도메인 고유 규칙

| ID | 규칙 | 설명 |
|----|------|------|
| R-20-1 | 상태 변경 시 Part2 동기화 | 확장 항목 상태가 SHELL→STUB→REF로 변경될 때 Part2 Section Map 동기화 필수 |
| R-20-2 | HIGH 미구현 시 Phase 진입 차단 | 해당 Phase의 HIGH 우선순위 항목이 미구현(REF 미달)이면 다음 Phase 진입을 차단한다. Phase 진입 가부의 단일 정본 게이트 조건은 R-20-5(HIGH 100% REF + MEDIUM 70% 이상 STUB/REF)를 따른다. |
| R-20-3 | 우선순위 변경은 분기별 리뷰에서만 | HIGH/MEDIUM/LOW 재분류는 분기별 로드맵 리뷰 시에만 허용, 임의 변경 금지 |
| R-20-4 | SHELL→REF 전환 시 참조 경로 기재 필수 | 항목이 상세화 완료되어 REF로 전환될 때 해당 SOT 2 문서 경로를 정확히 기재 |
| R-20-5 | Phase 게이트 조건 | 각 Phase의 HIGH 항목 100% REF + MEDIUM 항목 70% 이상 STUB/REF 시 다음 Phase 개시 |

### 4.4 상태 전환 규칙

```
SHELL → STUB: 항목의 3~5줄 설명 + 스키마 초안 작성 시
STUB  → REF:  해당 도메인 sot 2/ 폴더에 상세 명세 완료 + 참조 경로 기재 시
REF   → DONE: 구현 코드 완료 + 테스트 통과 시 (향후 추가 상태)
```

> **역방향 전환 금지**: REF→SHELL, STUB→SHELL 등 역행은 허용하지 않음. 삭제가 필요한 경우 DEPRECATED 상태로 별도 관리.
>
> **DONE / DEPRECATED 상태 범위**: DONE 및 DEPRECATED는 향후 추가 상태이며 정본 상태 enum(SHELL/STUB/REF, 인덱스 상태 범례)에 포함되지 않는다. 두 상태 모두 §7.4 / R-20-5 Phase 게이트 임계치 계산에 산입하지 않으며, 게이트는 SHELL/STUB/REF만 집계한다.
>
> **DONE / DEPRECATED 상태 범위**: DONE 및 DEPRECATED는 향후 추가 상태이며 정본 상태 enum(SHELL/STUB/REF, 인덱스 상태 범례)에 포함되지 않는다. 두 상태 모두 §7.4 / R-20-5 Phase 게이트 임계치 계산에 산입하지 않으며, 게이트는 SHELL/STUB/REF만 집계한다.

---

## 5. 선행작업

> **Tier 5 간소화 적용**: 추적 인덱스 성격이므로 선행작업 최소화

### 5.1 필수 선행작업

| # | 작업 | 상태 | 설명 |
|---|------|------|------|
| PRE-1 | Part2 Phase별 항목 확인 | DONE | V2-P2 51건, V2-P3 14건, V3-P2 6건, V3-P3 16건 = 87건 확정 |
| PRE-2 | 기존 인덱스 218줄 검증 | DONE | 87건 전수 매핑, 우선순위/SOT 2 참조 확인 완료 |
| PRE-3 | 서브폴더 존재 확인 | DONE | 01/02/03 폴더 생성 완료 (비어있음) |

### 5.2 향후 선행작업 (Phase 진행 시)

| # | 작업 | 상태 | 설명 |
|---|------|------|------|
| PRE-4 | 각 SOT 2 도메인의 수용 준비 상태 확인 | PENDING | 18개 폴더에서 v23 항목 수용 가능 여부 확인 필요 |
| PRE-5 | Part2 로드맵 일정 확정 | PENDING | V2-P2/P3, V3-P2/P3 실행 시점 확정 대기 |

---

## 6. 이슈 해결 매핑

### 6.1 87건 전수 → 우선순위별 서브폴더 매핑

#### 01_high-priority/ (32건)

| 소스 | 항목명 | 소스 ID | SOT 2 참조 |
|------|--------|---------|-----------|
| V2-P2 | Advanced Reasoning Chain | V2-P2-11 | `1-1_Verifier-Reasoning-Engines/` |
| V2-P2 | Multi-step Planning Engine | V2-P2-12 | `1-1_Verifier-Reasoning-Engines/` |
| V2-P2 | Self-correction Loop | V2-P2-13 | `1-1_Verifier-Reasoning-Engines/` |
| V2-P2 | Confidence Calibration | V2-P2-14 | `1-1_Verifier-Reasoning-Engines/` |
| V2-P2 | Episodic Memory Engine | V2-P2-16 | `2-1_Blue-Node-Architecture/` |
| V2-P2 | Semantic Memory Consolidation | V2-P2-17 | `2-1_Blue-Node-Architecture/` |
| V2-P2 | Cross-session Recall | V2-P2-20 | `2-1_Blue-Node-Architecture/` |
| V2-P2 | Knowledge Graph Builder v2 | V2-P2-21 | `3-3_PKM-Knowledge-Management/` |
| V2-P2 | ColBERT v3 Integration | V2-P2-24 | `2-2_COND-Modules-Detail/` |
| V2-P2 | Self-RAG Implementation | V2-P2-25 | `2-2_COND-Modules-Detail/` |
| V2-P2 | CRAG (Corrective RAG) | V2-P2-26 | `2-2_COND-Modules-Detail/` |
| V2-P2 | Multi-agent Orchestrator | V2-P2-31 | `3-8_Conversation-A2A/` |
| V2-P2 | Task Decomposition Engine | V2-P2-33 | `3-4_Workflow-RPA/` |
| V2-P2 | Human-in-the-Loop Protocol v2 | V2-P2-36 | `3-4_Workflow-RPA/` |
| V2-P2 | Voice Input/Output | V2-P2-38 | `3-2_Multimodal-Processing/` |
| V2-P2 | Accessibility Compliance (WCAG 2.1 AA) | V2-P2-41 | `3-7_Developer-Tools-API-SDK/` |
| V2-P2 | Spaced Repetition Engine v2 | V2-P2-42 | `3-5_Education-Learning/` |
| V2-P2 | Adaptive Learning Path | V2-P2-43 | `3-5_Education-Learning/` |
| V2-P2 | Emotion Detection v2 | V2-P2-45 | `3-6_Health-Wellness-EmotionAI/` |
| V2-P2 | Portfolio Optimizer | V2-P2-48 | `Ai-investing-detail/` |
| V2-P2 | Plugin Architecture v2 | V2-P2-51 | `3-7_Developer-Tools-API-SDK/` |
| V2-P2 | Auto-update Mechanism | V2-P2-53 | `4-1_Rust-Tauri-Infrastructure/` |
| V2-P2 | End-to-End Encryption | V2-P2-56 | `4-1_Rust-Tauri-Infrastructure/` |
| V2-P2 | Backup & Restore | V2-P2-57 | `4-1_Rust-Tauri-Infrastructure/` |
| V2-P3 | Sparse Attention Implementation | V2-P3-10 | `1-1_Verifier-Reasoning-Engines/` |
| V2-P3 | Mixture-of-Experts Routing | V2-P3-11 | `1-1_Verifier-Reasoning-Engines/` |
| V2-P3 | Advanced A2A Protocol | V2-P3-14 | `3-8_Conversation-A2A/` |
| V2-P3 | Natural Language Workflow | V2-P3-16 | `3-4_Workflow-RPA/` |
| V2-P3 | Privacy-preserving Inference | V2-P3-21 | `4-1_Rust-Tauri-Infrastructure/` |
| V3-P3 | AGI Safety Framework | V3-P3-11 | `1-1_Verifier-Reasoning-Engines/` |
| V3-P3 | Emergent Behavior Monitor | V3-P3-12 | `4-4_MLOps-LLMOps/` |
| V3-P3 | AI Ethics Governance Module | V3-P3-21 | `3-9_Business-Model-Strategy/` |

> **검증**: V2-P2 24건 + V2-P3 5건(V2-P3-10,11,14,16,21) + V3-P3 3건(V3-P3-11,12,21) = **32건**. 인덱스 원본 개별 항목 전수 대조 확인 완료.

#### 02_medium-priority/ (42건)

| 소스 | 항목명 | 소스 ID | SOT 2 참조 |
|------|--------|---------|-----------|
| V2-P2 | Uncertainty Quantification | V2-P2-15 | `1-1_Verifier-Reasoning-Engines/` |
| V2-P2 | Procedural Memory Store | V2-P2-18 | `2-1_Blue-Node-Architecture/` |
| V2-P2 | Memory Decay Simulation | V2-P2-19 | `2-1_Blue-Node-Architecture/` |
| V2-P2 | Entity Resolution Engine | V2-P2-22 | `3-3_PKM-Knowledge-Management/` |
| V2-P2 | Temporal Knowledge Tracker | V2-P2-23 | `3-3_PKM-Knowledge-Management/` |
| V2-P2 | RAPTOR Recursive Summarization | V2-P2-27 | `2-2_COND-Modules-Detail/` |
| V2-P2 | Late Chunking (Jina AI) | V2-P2-28 | `2-2_COND-Modules-Detail/` |
| V2-P2 | 4-Index Fusion v2 | V2-P2-29 | `2-2_COND-Modules-Detail/` |
| V2-P2 | Contextual Retrieval v2 | V2-P2-30 | `2-2_COND-Modules-Detail/` |
| V2-P2 | Agent Memory Sharing | V2-P2-32 | `3-8_Conversation-A2A/` |
| V2-P2 | Parallel Task Executor | V2-P2-34 | `3-4_Workflow-RPA/` |
| V2-P2 | Workflow Conditional Branching | V2-P2-35 | `3-4_Workflow-RPA/` |
| V2-P2 | Adaptive UI Theme Engine | V2-P2-37 | `3-7_Developer-Tools-API-SDK/` |
| V2-P2 | Drag-and-Drop Workflow Builder | V2-P2-39 | `3-4_Workflow-RPA/` |
| V2-P2 | Split-view Multi-session | V2-P2-40 | `3-7_Developer-Tools-API-SDK/` |
| V2-P2 | Quiz Auto-generator | V2-P2-44 | `3-5_Education-Learning/` |
| V2-P2 | CBT Session Manager | V2-P2-46 | `3-6_Health-Wellness-EmotionAI/` |
| V2-P2 | Mood Trend Analytics | V2-P2-47 | `3-6_Health-Wellness-EmotionAI/` |
| V2-P2 | Market Sentiment Analyzer | V2-P2-49 | `Ai-investing-detail/` |
| V2-P2 | Financial Report Parser | V2-P2-50 | `Ai-investing-detail/` |
| V2-P2 | Telemetry & Observability | V2-P2-52 | `4-1_Rust-Tauri-Infrastructure/` |
| V2-P2 | Offline Mode | V2-P2-54 | `4-1_Rust-Tauri-Infrastructure/` |
| V2-P2 | Data Export/Import Suite | V2-P2-55 | `4-1_Rust-Tauri-Infrastructure/` |
| V2-P2 | Performance Profiler | V2-P2-58 | `4-1_Rust-Tauri-Infrastructure/` |
| V2-P2 | API Gateway v2 | V2-P2-59 | `3-7_Developer-Tools-API-SDK/` |
| V2-P2 | Webhook Integration | V2-P2-60 | `3-7_Developer-Tools-API-SDK/` |
| V2-P2 | Cost Dashboard | V2-P2-61 | `3-9_Business-Model-Strategy/` |
| V2-P3 | Continual Learning Framework | V2-P3-12 | `4-4_MLOps-LLMOps/` |
| V2-P3 | Model Distillation Pipeline | V2-P3-13 | `4-4_MLOps-LLMOps/` |
| V2-P3 | Autonomous Agent Swarm | V2-P3-15 | `3-8_Conversation-A2A/` |
| V2-P3 | Advanced Document Understanding | V2-P3-17 | `3-2_Multimodal-Processing/` |
| V2-P3 | Video Understanding | V2-P3-18 | `3-2_Multimodal-Processing/` |
| V2-P3 | Personalized Model Adapter | V2-P3-20 | `4-4_MLOps-LLMOps/` |
| V2-P3 | Regulatory Compliance Engine | V2-P3-23 | `3-9_Business-Model-Strategy/` |
| V3-P2 | Causal Inference Engine | V3-P2-18 | `1-1_Verifier-Reasoning-Engines/` |
| V3-P2 | Meta-learning Controller | V3-P2-21 | `4-4_MLOps-LLMOps/` |
| V3-P3 | Self-improving Code Generator | V3-P3-13 | `3-7_Developer-Tools-API-SDK/` |
| V3-P3 | Universal Tool Adapter | V3-P3-14 | `4-3_MCP-Server-Client/` |
| V3-P3 | Predictive Task Anticipation | V3-P3-18 | `3-4_Workflow-RPA/` |
| V3-P3 | Cross-platform Sync Protocol | V3-P3-19 | `4-1_Rust-Tauri-Infrastructure/` |
| V3-P3 | Explainability Dashboard | V3-P3-22 | `3-7_Developer-Tools-API-SDK/` |
| V3-P3 | Autonomous Testing Agent | V3-P3-24 | `5-1_Benchmark-Evaluation/` |

> **검증**: V2-P2 27건 + V2-P3 7건 + V3-P2 2건 + V3-P3 6건 = 42건. 인덱스 42건과 일치.

#### 03_low-priority/ (13건)

| 소스 | 항목명 | 소스 ID | SOT 2 참조 |
|------|--------|---------|-----------|
| V2-P3 | 3D Data Processing | V2-P3-19 | `3-2_Multimodal-Processing/` |
| V2-P3 | Multi-cloud Deployment | V2-P3-22 | `4-2_CICD-Pipeline/` |
| V3-P2 | Neuro-symbolic Reasoning | V3-P2-17 | `1-1_Verifier-Reasoning-Engines/` |
| V3-P2 | World Model Simulator | V3-P2-19 | `1-1_Verifier-Reasoning-Engines/` |
| V3-P2 | Compositional Generalization | V3-P2-20 | `1-1_Verifier-Reasoning-Engines/` |
| V3-P2 | Cognitive Architecture Integration | V3-P2-22 | `2-1_Blue-Node-Architecture/` |
| V3-P3 | Autonomous Knowledge Discovery | V3-P3-15 | `3-3_PKM-Knowledge-Management/` |
| V3-P3 | Collective Intelligence Protocol | V3-P3-16 | `3-8_Conversation-A2A/` |
| V3-P3 | Emotion Synthesis Engine | V3-P3-17 | `3-6_Health-Wellness-EmotionAI/` |
| V3-P3 | Decentralized Identity (DID) | V3-P3-20 | `4-1_Rust-Tauri-Infrastructure/` |
| V3-P3 | Natural Language Database | V3-P3-23 | `3-3_PKM-Knowledge-Management/` |
| V3-P3 | Digital Twin of User Preferences | V3-P3-25 | `2-1_Blue-Node-Architecture/` |
| V3-P3 | Zero-shot Domain Adaptation | V3-P3-26 | `4-4_MLOps-LLMOps/` |

> **검증**: V2-P2 LOW 0건(인덱스 원본 전수 확인: V2-P2 #11~#61 전부 HIGH 또는 MEDIUM) + V2-P3 2건(V2-P3-19, V2-P3-22) + V3-P2 4건 + V3-P3 7건(V3-P3-15,16,17,20,23,25,26) = **13건**. 인덱스 13건과 정확 일치.

### 6.2 이슈별 해결 방안

| # | 이슈 (§1.3) | 해결 방안 | Phase |
|---|-------------|----------|-------|
| P-1 | SHELL 상태 87건 | 서브폴더 _index.md에 전수 등록, 해당 도메인에서 상세화 진행 | Phase 1 |
| P-2 | 우선순위 근거 미문서화 | 본 계획서 §A에 우선순위 기준 명문화 | Phase 1 |
| P-3 | 의존성 미정의 | §A 부록에 주요 의존성 그래프 기재 | Phase 2 |
| P-4 | 서브폴더 비어있음 | Phase 1에서 _index.md 배치 | Phase 1 |
| P-5 | SOT 2 참조 경로 미검증 | 18개 폴더 대상 참조 경로 존재 확인 스크립트 실행 | Phase 1 |
| P-6 | 구현 시점 미확정 | Part2 로드맵 확정 시 §7 업데이트 | Part2 종속 |

---

## 7. Phase 실행 계획

> **Tier 5 간소화 적용**: 추적 인덱스이므로 Phase 구조는 Part2 로드맵에 종속

### 7.1 Phase 0 — 인덱스 구조화 (본 계획서 실행)

| 작업 | 산출물 | 상태 |
|------|--------|------|
| 종합 계획서 작성 | `V23_EXTENSION_ITEMS_구조화_종합계획서.md` | DONE |
| AUTHORITY_CHAIN 작성 | `AUTHORITY_CHAIN.md` | DONE |
| CONFLICT_LOG 작성 | `CONFLICT_LOG.md` | DONE |

#### Phase 0 단계별 상세 작업 절차

<details>
<summary><b>P0-1. 종합 계획서 작성</b> — DONE (2026-04-02 최종 검증 완료)</summary>

**상태**: DONE — 3회 반복 검증 후 잔여 오류 0건 확인

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V2-Phase 2, V2-Phase 3, V3-Phase 2, V3-Phase 3
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_인덱스.md` (218줄, 87건)

**절차**:
1. Part2 V2-P2/P3, V3-P2/P3 읽기 → 87건 항목 전수 확인
2. 기존 인덱스(218줄) 읽기 → Phase/우선순위/SOT 2 참조 매핑 확인
3. 14+1 섹션 계획서 작성:
   - §1 현재 상태 분석 (SHELL 87건 전수 분석)
   - §2 목표 구조 (3개 서브폴더, 추적 인덱스 설계)
   - §3 권한 체계 선언 (LOCK-V23-01~08)
   - §4~§6 거버넌스, 선행작업, 이슈 해결 (87건 → 18개 도메인 매핑)
   - §7 Phase 실행 계획 (본 섹션)
   - §8~§14 파일 역할 분리, 충돌 해결, 검증 등
   - 부록 §A 우선순위별 구현 계획

**검증**:
- [x] 14+1 섹션 전부 작성 완료
- [x] 87건 전수 Phase/우선순위 분류 정확 (인덱스 원본 개별 항목 전수 대조 완료)
- [x] LOCK-V23-01~08 등록

**보정 이력** (2026-04-02):
- §1.4 Phase별 우선순위 소계 보정 — V2-P2: 19H/28M/4L → 24H/27M/0L, V2-P3: 4H → 5H, V3-P3: 5M/8L → 6M/7L
- §1.5 SOT 2 카테고리별 5개 폴더 수치 보정 (1-1→12, 3-4→7, 3-7→8, 3-8→5, 4-1→10), 1-2 (0건) 행 추가
- §6.1 HIGH/LOW 검증 메모 정리, V2-P2 LOW 유령 행 삭제
- §7.3/§7.4 게이트 조건 수치 보정 (HIGH 19→24, MEDIUM 28→27)
- §11 S-1 V2-P2 LOW 0건 확정 반영
- §13 1-1 폴더 건수 11→12 보정
- §A.2~A.4 헤더 수치, 모순 참고 메모 제거, 근사치→확정치 전환
- 총 26건 보정, 3차 검증에서 잔여 오류 0건 확인
- §7.1 P0-3 프롬프트 보강: 입력 파일 1→2건, 참조 근거 0→9건, 절차 5→7단계, 검증 3→11건. P0-3 실행 완료 후 DONE 상태·보정 이력 반영

**산출물**: `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_구조화_종합계획서.md` (본 문서)
</details>

<details>
<summary><b>P0-2. AUTHORITY_CHAIN 작성</b> — DONE (2026-04-02 최종 검증 완료)</summary>

**상태**: DONE — 4회 반복 검증, 63개 대조 항목 전수 PASS, 잔여 오류 0건 확인

**입력 파일**:
- 본 계획서 §3 (권한 체계 선언, §3.1~§3.4)
- 본 계획서 §4.1 R2 (LOCK 재정의 금지 규칙)

**참조 근거**:
- §2.1: `AUTHORITY_CHAIN.md ← 권한 체계 / LOCK 항목` (파일 역할 정의)
- §3.3: `AUTHORITY_CHAIN.md | LOCK 항목 8개 | 변경 차단` (canonical 범위)
- §8: `LOCK 정본: 8개 LOCK 항목 관리` (핵심 역할)
- §9.2 2단계: `정본 출처 확인 → AUTHORITY_CHAIN.md의 권한 체계 참조` (충돌 해결 시 사용 용도)
- §10.1: `AUTHORITY_CHAIN.md에 8개 LOCK 등록되어 있는가?` (구조 검증)
- §10.3: `LOCK 항목 8개의 정본 출처가 명시되어 있는가?` (거버넌스 검증)
- §7.4: `P0 → P1 게이트: AUTHORITY_CHAIN.md(LOCK 8건)` (Phase 전환 조건)

> **Scope 정리**: §2.1은 "권한 체계 / LOCK 항목"으로 광의 정의, §3.3·§8은 "LOCK 항목 8개"로 협의 정의.
> §9.2 2단계에서 충돌 해결 시 권한 체계 참조용으로 사용되므로, §3.1~§3.3은 **컨텍스트 요약**으로 포함하고 §3.4 LOCK은 **원문 전수 등록**으로 구분한다.

**절차**:
1. `5-4_v23-Extension-Items/AUTHORITY_CHAIN.md` 신규 생성
2. 문서 상단에 R2 (LOCK 재정의 금지: LOCK 값은 정본 출처에서만 변경 가능) 규칙 명시
3. §3.1~§3.3 권한 체계를 컨텍스트 요약으로 포함 (충돌 해결 시 권한 참조용, §9.2 2단계 지원):
   - §3.1 기존 VAMOS 권한 체계 (Level 0~5 계층 요약)
   - §3.2 v23 Extension Items 권한 체계 (Part2→인덱스→도메인→코드 흐름)
   - §3.3 문서별 정본 범위 (5개 문서 canonical 범위 테이블)
4. §3.4 LOCK 보호 항목을 원문 4열 구조 그대로 전수 등록 (ID | LOCK 항목 | 정본 출처 | 변경 시 필요 조치):
   - LOCK-V23-01: Phase별 범위 정의 | Part2 | Part2 승인 필수
   - LOCK-V23-02: 우선순위 분류 기준 (HIGH/MEDIUM/LOW) | Part2 기반 | 분기별 로드맵 리뷰
   - LOCK-V23-03: HIGH 32건 목록 | V23 인덱스 확정 | Part2 + 인덱스 동시 변경
   - LOCK-V23-04: V2-Phase 2 범위 51건 | Part2 확정 | Part2 승인 필수
   - LOCK-V23-05: V2-Phase 3 범위 14건 | Part2 확정 | Part2 승인 필수
   - LOCK-V23-06: V3-Phase 2 범위 6건 | Part2 확정 | Part2 승인 필수
   - LOCK-V23-07: V3-Phase 3 범위 16건 | Part2 확정 | Part2 승인 필수
   - LOCK-V23-08: SOT 2 참조 경로 매핑 | 인덱스 §6 확정 | 인덱스 업데이트 시 자동 반영
5. 변경 이력 섹션 초기화 — 테이블 구조: `| 일자 | 변경 LOCK ID | 변경 내용 | 승인 근거 |`

**검증**:
- [x] AUTHORITY_CHAIN.md 파일 존재
- [x] LOCK 8개 항목 전수 등록 — §3.4 테이블과 1:1 대응 (ID 8개 누락 없음)
- [x] LOCK 8개 항목의 **정본 출처** 열이 §3.4 원본과 일치 (§10.3 충족)
- [x] LOCK 8개 항목의 **변경 시 필요 조치** 열 포함 (§3.4 4열 구조 유지)
- [x] R2 (LOCK 재정의 금지) 규칙 문서 상단에 명시
- [x] §3.1~§3.3 권한 체계 컨텍스트 요약 포함 (§9.2 2단계 충돌 해결 참조용)
- [x] 변경 이력 테이블 구조 초기화 (4열: 일자/LOCK ID/내용/승인 근거)

**보정 이력** (2026-04-02):
- 기존 파일 전면 재작성 — LOCK-V23-03 "HIGH 26건→32건" 오류 수정, Level 0·1 누락 보완, R2 규칙 신설
- §3.3 테이블 5행 원문 복원 (기존: Part2 4행 분리 + 서브인덱스 포함 → 원본 5행으로 교정)
- LOCK 테이블 §3.4 원문 4열 구조로 통일 (기존: 5열 "등록일" 추가분 + 문구 변형 → 원문 일치)
- 변경 이력 3열→4열 구조 교정 (P0-2 명세: 일자/LOCK ID/내용/승인 근거)
- SOT 2 참조 경로 상세(17개 폴더, 수치 오류 다수) 제거 — LOCK 테이블 범위 외 콘텐츠

**산출물**: `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\AUTHORITY_CHAIN.md` (재작성)
</details>

<details>
<summary><b>P0-3. CONFLICT_LOG 작성</b> — DONE (2026-04-02 최종 검증 완료)</summary>

**상태**: DONE — P0-3 프롬프트 검증 후 재작성, 11개 검증 항목 전수 PASS, 잔여 오류 0건 확인

**입력 파일**:
- 본 계획서 §9 (충돌 해결 프로토콜, §9.1 충돌 유형 + §9.2 해결 프로세스)
- 본 계획서 §11.1 (OPEN 3건 해결 확인, CFL-GOV-005/006/007 상세)

**참조 근거**:
- §2.1: `CONFLICT_LOG.md ← 충돌 기록` (폴더 트리 파일 역할 정의)
- §3.3: `CONFLICT_LOG.md | 충돌 기록 | 이력 추적` (canonical 범위)
- §8: `충돌 이력: 불일치 발견/해결 기록 | 발견 시 즉시` (핵심 역할 + 갱신 주기)
- §9.2 1단계: `충돌 발견 → CONFLICT_LOG.md에 등록 (OPEN)` (등록 프로세스)
- §9.2 4단계: `CONFLICT_LOG 상태를 RESOLVED/VERIFIED로 갱신` (상태 전환)
- §10.1: `CONFLICT_LOG.md 초기화되어 있는가?` (구조 검증 체크리스트)
- §7.4: `P0 → P1 게이트: ... CONFLICT_LOG.md 초기화 완료` (Phase 전환 조건)
- §12: `OPEN 3건 | PASS | CFL-GOV-005/006/007 전부 RESOLVED` (FINAL REVIEW 검증)
- §14.1 W-3: `CONFLICT_LOG로 추적` (우선순위 집계 오류 모니터링 용도)

> **Scope 정리**: §2.1은 "충돌 기록"으로 광의 정의, §3.3은 "충돌 기록 | 이력 추적"으로 canonical 범위, §8은 "불일치 발견/해결 기록"으로 역할 상세화.
> §9.1~§9.2는 프로토콜 원문을 **전수 포함** 대상으로, §11.1은 초기 등록 3건의 **원문 전수 등록** 대상으로 구분한다.
> §9.2의 상태(OPEN/RESOLVED/VERIFIED)와 §9.1 D유형의 "보류" 특성을 조합하여 상태 범례 4가지(OPEN/RESOLVED/VERIFIED/DEFERRED)를 도출한다.

**절차**:
1. `5-4_v23-Extension-Items/CONFLICT_LOG.md` 신규 생성
2. 문서 상단에 상태 범례 정의 (§9.2 1·4단계 기반, 4가지 상태):
   - OPEN: 충돌 발견, 미해결
   - RESOLVED: 해결 완료, 정본 확정
   - VERIFIED: 불일치 의심 후 조사 결과 불일치 없음 확인
   - DEFERRED: 추가 정보 필요, 해결 보류 (§9.1 D유형 "분기 리뷰까지 보류" 대응)
3. §9.1 충돌 유형 4가지를 원문 3열 구조 그대로 포함 (유형 | 설명 | 해결 원칙):
   - A: Part2 vs 인덱스 | Phase 범위/우선순위 불일치 | Part2가 정본 (Level 2 우선)
   - B: 인덱스 vs 도메인 sot 2/ | 상태/상세 내용 불일치 | 도메인 sot 2/가 상세 정본, 인덱스는 상태만 반영
   - C: 인덱스 내부 | 통계 테이블과 본문 항목 수 불일치 | 본문 개별 항목 기준으로 통계 재계산
   - D: 우선순위 변경 요청 | 분기 리뷰 외 임의 변경 시도 | R-20-3에 의해 차단, 분기 리뷰까지 보류
4. §9.2 해결 프로세스 5단계를 원문 그대로 포함:
   - 1단계: 충돌 발견 → CONFLICT_LOG.md에 등록 (OPEN)
   - 2단계: 정본 출처 확인 → AUTHORITY_CHAIN.md의 권한 체계 참조
   - 3단계: 상위 정본 기준으로 해결 → 인덱스 갱신
   - 4단계: CONFLICT_LOG 상태를 RESOLVED/VERIFIED로 갱신
   - 5단계: 관련 LOCK 항목 영향 확인
5. §11.1의 기존 OPEN 3건을 원문 4열 구조 그대로 RESOLVED 상태로 등록 (충돌 ID | 내용 | 해결 상태 | 검증 이력):
   - CFL-GOV-005: 거버넌스 규칙 적용 범위 불명확 — R-20-3 분기 리뷰 외 임의 변경 차단 규칙의 적용 시점 미정 | RESOLVED | S7-5에서 최초 해결, S8-4에서 이중 검증 완료. R-20-3 적용 시점은 "인덱스 공식 등록 이후"로 확정.
   - CFL-GOV-006: Phase별 분류 집계 불일치 — V2-P3 HIGH 항목 수 1건 차이 | RESOLVED | S7-5에서 집계 보정, S8-4에서 전수 재계산으로 87건 일치 확인. CONFLICT_LOG에 보정 이력 기록 완료.
   - CFL-GOV-007: SOT 2 참조 경로 미확인 — 18개 폴더 중 일부 존재 미확인 | RESOLVED | S7-5에서 14/18 확인, S8-4에서 나머지 4건 확인 완료. S10-3에서 전수 존재 검증 PASS.
6. 요약 통계 섹션 초기화 — 테이블 구조: `| 상태 | 건수 |` (CFL-GOV 3건 반영: RESOLVED 3, OPEN 0)
7. 변경 이력 섹션 초기화 — 테이블 구조: `| 날짜 | 변경 내용 |`

**검증**:
- [x] CONFLICT_LOG.md 파일 존재
- [x] 상태 범례 4가지 정의 (OPEN/RESOLVED/VERIFIED/DEFERRED)
- [x] §9.1 충돌 유형 4가지(A/B/C/D)가 원문 3열 구조(유형 | 설명 | 해결 원칙)와 1:1 대응 — 유형 코드·설명·해결 원칙 문구 일치 확인
- [x] §9.2 해결 프로세스 5단계가 원문과 일치 — 단계별 문구 전수 대조
- [x] CFL-GOV-005 RESOLVED 등록 — §11.1 원문(내용·해결 상태·검증 이력) 일치
- [x] CFL-GOV-006 RESOLVED 등록 — §11.1 원문 일치
- [x] CFL-GOV-007 RESOLVED 등록 — §11.1 원문 일치
- [x] 요약 통계 테이블 존재 + CFL-GOV 3건 반영 수치 정확 (VERIFIED 1 + RESOLVED 8 = 9건)
- [x] 변경 이력 테이블 존재 + 구조 정상 (2열: 날짜/변경 내용)
- [x] §8 역할 정의("충돌 이력: 불일치 발견/해결 기록")와 문서 scope 부합
- [x] §10.1 `CONFLICT_LOG.md 초기화되어 있는가?` 충족

**보정 이력** (2026-04-02):
- P0-3 프롬프트 자체 검증: 입력 파일 1건→2건(§11.1 추가), 참조 근거 0→9건, 절차 5→7단계, 검증 3→11건으로 보강
- 기존 파일(v1.0, CL-001~006만 존재) 재작성(v2.0): §9.1 충돌 유형 4가지, §9.2 해결 프로세스 5단계 프로토콜 섹션 신규 추가
- §11.1 CFL-GOV-005/006/007 3건 RESOLVED 상태로 신규 등록 (기존 CL-001~006 보존)
- 요약 통계 갱신: 6건→9건 (CFL-GOV 3건 추가)
- 헤더에 §8 역할·갱신주기, §3.3 canonical 범위 명시

**산출물**: `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\CONFLICT_LOG.md` (재작성)
</details>

### 7.2 Phase 1 — 서브폴더 인덱스 배치 ✅ 완료 (4/4, 2026-04-12) | 게이트 PASS

| 작업 | 산출물 | 게이트 |
|------|--------|--------|
| 01_high-priority/_index.md | HIGH 32건 추적 인덱스 | ✅ 완료 (2026-04-12). 32건 전수 SHELL 등록, V2-P2(24)+V2-P3(5)+V3-P3(3)=32 검산 일치. LOCK-V23-03 참조. CONFLICT 0건. 이월 없음 |
| 02_medium-priority/_index.md | MEDIUM 42건 추적 인덱스 | ✅ 완료 (2026-04-12). 42건 전수 SHELL 등록, V2-P2(27)+V2-P3(7)+V3-P2(2)+V3-P3(6)=42 검산 일치. LOCK-V23-02 참조. CONFLICT 0건. 이월 없음 |
| 03_low-priority/_index.md | LOW 13건 추적 인덱스 | ✅ 완료 (2026-04-12). 13건 전수 SHELL 등록, V2-P3(2)+V3-P2(4)+V3-P3(7)=13 검산 일치. LOCK-V23-02 참조. CONFLICT 0건. 이월 없음 |
| SOT 2 참조 경로 검증 | 18개 폴더 존재 확인 리포트 | ✅ 완료 (2026-04-12). 18/18 폴더 EXISTS, 합산 87건 일치, LOCK-V23-08 참조, CONFLICT 0건. 이월 없음 |

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>P1-1. 01_high-priority/_index.md 작성</b> — ✅ 완료 (2026-04-12)</summary>

**대조 기준**: §7.2 작업 1 — 게이트 "32건 전수 등록" + §6.2 P-1(SHELL 87건 서브폴더 등록), P-4(서브폴더 비어있음 해소)

**목표**: HIGH 우선순위 32건 전수를 추적 인덱스로 등록하여 SHELL 상태 관리 기반 확보

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_구조화_종합계획서.md` §6.1 01_high-priority (32건 테이블)
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_인덱스.md` (87건 정본 인덱스 — HIGH 항목 교차 확인용)

**절차**:
1. §6.1 HIGH 32건 테이블에서 전수 항목 추출 (소스 | 항목명 | 소스 ID | SOT 2 참조 4열)
2. `01_high-priority/_index.md` 신규 생성 — 헤더에 "HIGH 우선순위 32건 추적 인덱스" 명시
3. 추적 테이블 작성: `| # | 항목명 | 소스 ID | 소스 Phase | SOT 2 참조 | 상태 |` 6열 구조
4. 32건 전수 등록 — 상태 열은 전부 `SHELL` 초기값
5. 검산 행 추가: V2-P2 24건 + V2-P3 5건 + V3-P3 3건 = 32건
6. LOCK-V23-03(HIGH 32건 목록) 참조 표기 추가
7. 인덱스 원본과 교차 대조 — 항목명·소스 ID 1:1 일치 확인

**검증**:
- [x] `01_high-priority/_index.md` 파일 존재 ✅
- [x] 32건 전수 등록 (누락 0건) ✅ — #1~#32 연번, 6열 구조
- [x] 소스 ID가 인덱스 원본·§6.1 테이블과 정확 일치 ✅ — V2-P2-11~57, V2-P3-10~21, V3-P3-11~21 전수 대조
- [x] 상태 열 전부 SHELL 초기값 ✅ — 32건 전부 SHELL
- [x] 검산: V2-P2(24) + V2-P3(5) + V3-P3(3) = 32건 ✅ — 검산 테이블 포함
- [x] LOCK-V23-03 참조 명시 ✅ — 헤더 및 검산 섹션에 LOCK-V23-03 정본 32건 일치 표기

> **완료**: 2026-04-12. HIGH 우선순위 32건 추적 인덱스 `01_high-priority/_index.md` 신규 생성 완료.
>
> **실행 결과 요약**:
> - 32건 전수 등록: V2-P2(24건) + V2-P3(5건) + V3-P3(3건) = 32건, 6열 구조, 전 항목 SHELL 초기값
> - 소스 ID·항목명 교차 대조: §6.1 테이블 및 인덱스 원본과 1:1 일치, SOT 2 참조 경로 11개 폴더 매핑 완료
> - 재검증: 검산 테이블 포함하여 소스 Phase별 항목 수 정확 확인, LOCK-V23-03 참조 명시
> - 이월 항목: 없음

**[P1-1] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1개 — `01_high-priority/_index.md` (32건 HIGH 추적 인덱스, 99줄)
- 1. 게이트: G1-1 ✅ — 32건 전수 등록 충족 (LOCK-V23-03 정본 32건 일치)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 (LOCK-V23-01~08 변경 0건)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\01_high-priority\_index.md`
</details>

<details>
<summary><b>P1-2. 02_medium-priority/_index.md 작성</b> — ✅ 완료 (2026-04-12)</summary>

**대조 기준**: §7.2 작업 2 — 게이트 "42건 전수 등록" + §6.2 P-1(SHELL 87건 서브폴더 등록), P-4(서브폴더 비어있음 해소)

**목표**: MEDIUM 우선순위 42건 전수를 추적 인덱스로 등록하여 SHELL 상태 관리 기반 확보

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_구조화_종합계획서.md` §6.1 02_medium-priority (42건 테이블)
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_인덱스.md` (87건 정본 인덱스 — MEDIUM 항목 교차 확인용)

**절차**:
1. §6.1 MEDIUM 42건 테이블에서 전수 항목 추출 (소스 | 항목명 | 소스 ID | SOT 2 참조 4열)
2. `02_medium-priority/_index.md` 신규 생성 — 헤더에 "MEDIUM 우선순위 42건 추적 인덱스" 명시
3. 추적 테이블 작성: `| # | 항목명 | 소스 ID | 소스 Phase | SOT 2 참조 | 상태 |` 6열 구조
4. 42건 전수 등록 — 상태 열은 전부 `SHELL` 초기값
5. 검산 행 추가: V2-P2 27건 + V2-P3 7건 + V3-P2 2건 + V3-P3 6건 = 42건
6. 인덱스 원본과 교차 대조 — 항목명·소스 ID 1:1 일치 확인

**검증**:
- [x] `02_medium-priority/_index.md` 파일 존재 ✅
- [x] 42건 전수 등록 (누락 0건) ✅ — #1~#42 연번, 6열 구조
- [x] 소스 ID가 인덱스 원본·§6.1 테이블과 정확 일치 ✅ — V2-P2-15~61, V2-P3-12~23, V3-P2-18~21, V3-P3-13~24 전수 대조
- [x] 상태 열 전부 SHELL 초기값 ✅ — 42건 전부 SHELL
- [x] 검산: V2-P2(27) + V2-P3(7) + V3-P2(2) + V3-P3(6) = 42건 ✅ — 검산 테이블 포함
- [x] 총합 검산: HIGH(32) + MEDIUM(42) + LOW(13) = 87건 ✅ — 인덱스 정본 87건 일치

> **완료**: 2026-04-12. MEDIUM 우선순위 42건 추적 인덱스 `02_medium-priority/_index.md` 작성 완료.
>
> **실행 결과 요약**:
> - 42건 전수 등록: V2-P2(27건) + V2-P3(7건) + V3-P2(2건) + V3-P3(6건) = 42건, 6열 구조, 전 항목 SHELL 초기값
> - 소스 ID·항목명 교차 대조: §6.1 테이블 및 인덱스 원본과 1:1 일치, SOT 2 참조 경로 16개 폴더 매핑 완료
> - 재검증: 검산 테이블 포함하여 소스 Phase별 항목 수 정확 확인, LOCK-V23-02 참조 명시
> - 이월 항목: 없음

**[P1-2] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 수정 1개 — `02_medium-priority/_index.md` (42건 MEDIUM 추적 인덱스, 5열→6열 전환)
- 1. 게이트: G1-2 ✅ — 42건 전수 등록 충족 (LOCK-V23-02 우선순위 분류 기준 참조)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 (LOCK-V23-01~08 변경 0건)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\02_medium-priority\_index.md`
</details>

<details>
<summary><b>P1-3. 03_low-priority/_index.md 작성</b> — ✅ 완료 (2026-04-12)</summary>

**대조 기준**: §7.2 작업 3 — 게이트 "13건 전수 등록" + §6.2 P-1(SHELL 87건 서브폴더 등록), P-4(서브폴더 비어있음 해소)

**목표**: LOW 우선순위 13건 전수를 추적 인덱스로 등록하여 SHELL 상태 관리 기반 확보

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_구조화_종합계획서.md` §6.1 03_low-priority (13건 테이블)
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_인덱스.md` (87건 정본 인덱스 — LOW 항목 교차 확인용)

**절차**:
1. §6.1 LOW 13건 테이블에서 전수 항목 추출 (소스 | 항목명 | 소스 ID | SOT 2 참조 4열)
2. `03_low-priority/_index.md` 신규 생성 — 헤더에 "LOW 우선순위 13건 추적 인덱스" 명시
3. 추적 테이블 작성: `| # | 항목명 | 소스 ID | 소스 Phase | SOT 2 참조 | 상태 |` 6열 구조
4. 13건 전수 등록 — 상태 열은 전부 `SHELL` 초기값
5. 검산 행 추가: V2-P3 2건 + V3-P2 4건 + V3-P3 7건 = 13건 (V2-P2 LOW = 0건)
6. 인덱스 원본과 교차 대조 — 항목명·소스 ID 1:1 일치 확인

**검증**:
- [x] `03_low-priority/_index.md` 파일 존재 ✅
- [x] 13건 전수 등록 (누락 0건) ✅ — #1~#13 연번, 6열 구조
- [x] 소스 ID가 인덱스 원본·§6.1 테이블과 정확 일치 ✅ — V2-P3-19, V2-P3-22, V3-P2-17~22, V3-P3-15~26 전수 대조
- [x] 상태 열 전부 SHELL 초기값 ✅ — 13건 전부 SHELL
- [x] 검산: V2-P3(2) + V3-P2(4) + V3-P3(7) = 13건 (V2-P2 LOW = 0건 확인) ✅ — 검산 테이블 포함
- [x] 총합 검산: HIGH(32) + MEDIUM(42) + LOW(13) = 87건 ✅ — 인덱스 정본 87건 일치

> **완료**: 2026-04-12. LOW 우선순위 13건 추적 인덱스 `03_low-priority/_index.md` 작성 완료.
>
> **실행 결과 요약**:
> - 13건 전수 등록: V2-P3(2건) + V3-P2(4건) + V3-P3(7건) = 13건, 6열 구조, 전 항목 SHELL 초기값
> - 소스 ID·항목명 교차 대조: §6.1 테이블 및 인덱스 원본과 1:1 일치, SOT 2 참조 경로 9개 폴더 매핑 완료
> - 재검증: 검산 테이블 포함하여 소스 Phase별 항목 수 정확 확인, LOCK-V23-02 참조 명시
> - 이월 항목: 없음

**[P1-3] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 수정 1개 — `03_low-priority/_index.md` (13건 LOW 추적 인덱스, 6열 구조)
- 1. 게이트: G1-3 ✅ — 13건 전수 등록 충족 (LOCK-V23-02 우선순위 분류 기준 참조)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 (LOCK-V23-01~08 변경 0건)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\03_low-priority\_index.md`
</details>

<details>
<summary><b>P1-4. SOT 2 참조 경로 검증</b> — ✅ 완료 (2026-04-12)</summary>

**대조 기준**: §7.2 작업 4 — 게이트 "100% 경로 유효" + §6.2 P-5(SOT 2 참조 경로 미검증 해소) + §14.1 W-4(SOT 2 참조 폴더 미존재 위험 해소)

**목표**: 87건이 참조하는 18개 SOT 2 폴더의 실제 존재 여부를 전수 확인하여 교차 참조 정확성(R-T5-2) 보장

**입력 파일**:
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\V23_EXTENSION_ITEMS_구조화_종합계획서.md` §1.5 SOT 2 카테고리별 분포 (18개 폴더 목록)
- `D:\VAMOS\docs\sot 2\` (실제 폴더 구조 확인 대상)

**절차**:
1. §1.5에서 18개 SOT 2 참조 폴더 목록 추출:
   - `1-1_Verifier-Reasoning-Engines/` (12건)
   - `1-2_Auxiliary-Modules/` (0건)
   - `2-1_Blue-Node-Architecture/` (7건)
   - `2-2_COND-Modules-Detail/` (7건)
   - `3-2_Multimodal-Processing/` (4건)
   - `3-3_PKM-Knowledge-Management/` (5건)
   - `3-4_Workflow-RPA/` (7건)
   - `3-5_Education-Learning/` (3건)
   - `3-6_Health-Wellness-EmotionAI/` (4건)
   - `3-7_Developer-Tools-API-SDK/` (8건)
   - `3-8_Conversation-A2A/` (5건)
   - `3-9_Business-Model-Strategy/` (3건)
   - `4-1_Rust-Tauri-Infrastructure/` (10건)
   - `4-2_CICD-Pipeline/` (1건)
   - `4-3_MCP-Server-Client/` (1건)
   - `4-4_MLOps-LLMOps/` (6건)
   - `5-1_Benchmark-Evaluation/` (1건)
   - `Ai-investing-detail/` (3건)
2. `D:\VAMOS\docs\sot 2\` 하위에서 18개 폴더 존재 여부 개별 확인
3. 검증 리포트 작성: `| # | 폴더명 | 참조 항목 수 | 존재 여부 | 비고 |` 5열 구조
4. 항목 수 합산 검증: 12+0+7+7+4+5+7+3+4+8+5+3+10+1+1+6+1+3 = 87건
5. 미존재 폴더 발견 시 CONFLICT_LOG에 OPEN 등록 + 생성 요청 기록
6. LOCK-V23-08(SOT 2 참조 경로 매핑) 참조 표기

**검증**:
- [x] 18개 폴더 전수 확인 완료 ✅ — 18/18 EXISTS
- [x] 100% 경로 유효 ✅ — 미존재 건 0건
- [x] 항목 수 합산 = 87건 일치 ✅ — §1.5 정본 87건과 정확 일치
- [x] LOCK-V23-08 참조 명시 ✅ — 리포트 헤더 및 교차 참조 블록에 명시
- [x] R-T5-2(교차 참조 정확성) 충족 ✅ — 18개 참조 경로 전부 실제 폴더와 일치
- [x] §14.1 W-4 위험 해소 확인 ✅ — SOT 2 참조 폴더 미존재 위험 해소 (18/18 존재)

> **완료**: 2026-04-12. 18개 SOT 2 참조 폴더 전수 검증 완료. 100% 경로 유효.
>
> **실행 결과 요약**:
> - 18개 폴더 전수 확인: 18/18 EXISTS, 미존재 0건
> - 항목 수 합산: 12+0+7+7+4+5+7+3+4+8+5+3+10+1+1+6+1+3 = 87건 (§1.5 정본 일치)
> - LOCK-V23-08 참조 매핑 정합성 확인, CFL-GOV-007 RESOLVED 재확인
> - §6.2 P-5 이슈 해소, §14.1 W-4 위험 해소 확정
> - 이월 항목: 없음

**[P1-4] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1개 — `SOT2_REF_PATH_VERIFICATION.md` (18개 폴더 검증 리포트, Phase 2 테스트 시나리오 12건 포함)
- 1. 게이트: G1-4 ✅ — 100% 경로 유효 충족 (18/18 EXISTS, 합산 87건 일치)
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 (LOCK-V23-01~08 변경 0건)
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\SOT2_REF_PATH_VERIFICATION.md`
</details>

### 7.3 Phase 2+ — Part2 로드맵 종속 (영구 EXCLUDED 정식 확정 2026-05-12 STAGE 9 B-2)

```
Part2 V2-Phase 2 실행 시 → HIGH 24건 SHELL→STUB→REF 전환 추적
Part2 V2-Phase 3 실행 시 → HIGH 5건 SHELL→STUB→REF 전환 추적
Part2 V3-Phase 2 실행 시 → MEDIUM 2건 전환 추적
Part2 V3-Phase 3 실행 시 → HIGH 3건 전환 추적
```

#### Phase 2+ 추적 설정

<details>
<summary><b>Phase 2+. 추적전용 — Part2 로드맵 종속 상태 추적</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2+ "Part2 로드맵 종속" (수동 실행 없음, 추적 전용)
- §7 전환 게이트: V2/V3 4단계 게이트 (§7.4 참조)
- §6 이슈: P-3 (의존성 미정의), P-6 (구현 시점 미확정 — Part2 종속)
- 교차 도메인: 해당 없음 (18개 도메인 종속이나 본 도메인 자체 실행 없음)
- Part2 버전: V2-Phase 2/3 + V3-Phase 2/3 전체 (87건 추적)

**목표**: Part2 릴리스 시 87건(HIGH 32 + MEDIUM 42 + LOW 13)의 SHELL→STUB→REF 전환 상태를 자동 추적. 본 도메인은 수동 실행하지 않으며, Part2 로드맵 진행에 따라 인덱스가 자동 갱신됨.

**추적 설정**:
- **V2-Phase 2 추적**: HIGH 24건 — 01_high-priority/_index.md에서 SHELL→STUB→REF 상태 칼럼 추적
- **V2-Phase 3 추적**: HIGH 5건 — 동일 인덱스, V2-P3 태그
- **V3-Phase 2 추적**: MEDIUM 2건 — 02_medium-priority/_index.md에서 추적
- **V3-Phase 3 추적**: HIGH 3건 — 01_high-priority/_index.md에서 V3-P3 태그 추적
- **전환 조건**: Part2에서 해당 Phase 실행 선언 시 → 인덱스 상태 STUB으로 전환 → 도메인 정본 파일 완성 시 REF로 전환
- **게이트 비핵심 항목(나머지 MEDIUM 40건 + LOW 13건) 추적**: 위 4개 그룹은 Phase 게이트 임계치(§7.4/R-20-5) 산정에 직접 관여하는 게이트 핵심 항목이며, 나머지 항목은 02_medium-priority/_index.md 및 03_low-priority/_index.md에서 동일하게 SHELL→STUB→REF 상태 칼럼으로 추적한다(전환 조건·트리거 동일, Part2 로드맵 종속). 87건 전수 추적 표면은 3개 우선순위 _index.md(§산출물)이다.
- **게이트 비핵심 항목(나머지 MEDIUM 40건 + LOW 13건) 추적**: 위 4개 그룹은 Phase 게이트 임계치(§7.4/R-20-5) 산정에 직접 관여하는 게이트 핵심 항목이며, 나머지 항목은 02_medium-priority/_index.md 및 03_low-priority/_index.md에서 동일하게 SHELL→STUB→REF 상태 칼럼으로 추적한다(전환 조건·트리거 동일, Part2 로드맵 종속). 87건 전수 추적 표면은 3개 우선순위 _index.md(§산출물)이다.

**게이트 확인 절차** (Part2 릴리스 시):
1. Part2 V2-Phase 2 실행 선언 → 01_high-priority/_index.md HIGH 24건 상태 STUB 전환
2. 각 항목의 SOT 2 참조 도메인에서 정본 파일 작성 완료 확인 → REF 전환
3. V2-P2→V2-P3 게이트 평가: HIGH 24건 100% REF + MEDIUM 27건 70% STUB/REF
4. 후속 게이트(V2-P3→V3-P2→V3-P3→완료) 동일 패턴 반복

**검증** (Part2 릴리스 시점에만 실행):
- [ ] 01_high-priority/_index.md 상태 칼럼 갱신 (SHELL/STUB/REF)
- [ ] 02_medium-priority/_index.md 상태 칼럼 갱신
- [ ] 03_low-priority/_index.md 상태 칼럼 갱신
- [ ] §7.4 게이트 조건 평가 (해당 Phase 전환 가능 여부)
- [ ] LOCK-V23-03~07 (Phase별 범위) 정합 확인

**산출물**: Part2 릴리스 시 자동 갱신
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\01_high-priority\_index.md` (상태 칼럼 갱신)
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\02_medium-priority\_index.md` (상태 칼럼 갱신)
- `D:\VAMOS\docs\sot 2\5-4_v23-Extension-Items\03_low-priority\_index.md` (상태 칼럼 갱신)
</details>

#### STAGE 9 결정 정식 확정 marker (2026-05-12, B-2)

**STAGE 9 Phase B-2 정식 확정 결과** (chain `s9_40_b_2`, 2026-05-12):

본 도메인 5-4 v23 Extension Items는 STAGE 9 Phase B-2 (2026-05-12) 시점에서 **영구 EXCLUDED 정식 확정**되었음을 명시한다. 본 §7.3 추적 설정은 Part2 로드맵 종속 상태로만 유지되며, 본 도메인 자체에서 콘텐츠 수동 실행은 발생하지 않는다.

**manifest 영구 EXCLUDED 정식 확정 변경 사실** (`D:/VAMOS/docs/sot 2/_automation/phase2_manifest.yaml`, 5-4 블록 L533~):
- `status`: `stage9_processing` → **`permanently_excluded_part2_dependent`** (B-2.2에서 정식 확정)
- `stage9_step_progress`: NEW 필드 (B-1: `complete_2026-05-12` + B-2: `complete_2026-05-12` + B-3: `pending`)
- `stage9_b_2_confirmed_at`: `"2026-05-12"` NEW 필드
- `stage9_post_status`: `"permanently_excluded_part2_dependent_confirmed_2026-05-12 (post-STAGE 9 Phase B-2)"`
- `reason` 보강 (STAGE 9 Phase B-2 영구 EXCLUDED 정식 확정 명시)
- `stage9_note` 보강 (B-1 + B-2 진행 결과 + B-3 잔여 명시)

**production 추적 인덱스 cross-ref** (Part2 로드맵 진행 시 자동 갱신, 본 §7.3 §산출물과 동일 위치):
- `01_high-priority/_index.md` (HIGH 32건 추적, 상태 칼럼 SHELL→STUB→REF)
- `02_medium-priority/_index.md` (MEDIUM 42건 추적, 상태 칼럼 SHELL→STUB→REF)
- `03_low-priority/_index.md` (LOW 13건 추적, 상태 칼럼 SHELL→STUB→REF)
- 합계 **87건 EXACT** (B-1.3 4 source MATCH: §통계요약 + LOCK-V23-03~07 + SOT2_REF 18 폴더 EXISTS)

**STAGE 9 Phase B 진행 결과 요약**:
- **B-1 ✅ COMPLETE truly_converged_v1 first-pass** (chain `s9_39_b_1`, 2026-05-12, 8 sub-step 8/8 PASS): phase0_baseline 캡처 + sandbox isolation 9 .md + 87 inventory cross-verify + 3 _index.md NEW "STAGE 9 추적 상태" column 추가 (sandbox, 87 rows × "Part2 대기 (SHELL initial)") + Baseline preservation 6/6 V1-like + R₁~R₃ 24 verifications 0 changes + abort 6종 NOT FIRED + 6 anchor 48 cell
- **B-2 ✅ COMPLETE truly_converged_v1 first-pass** (chain `s9_40_b_2`, 2026-05-12, 6 sub-step 6/6 PASS, 본 시점): manifest 영구 EXCLUDED 정식 확정 + 본 §7.3 sub-section append + V1-like preservation 5/5 (재정의 6→5) + R₁~R₃ 18 verifications 0 changes + abort 7종 NOT FIRED (5 표준형 inherited + 2 B-2 NEW) + 6 anchor 36 cell
- **B-3 ⏭ 대기** (production sync 14 sub-step + 두 단계 게이트 9.2-A/B + bilateral SOT2 5-4 row 갱신 + 5-4 영구 EXCLUDED 정식 확정 마커 append)

**본 도메인 자체 수동 실행 없음 재확인**: 본 §7.3에 명시된 추적 절차는 Part2 로드맵 진행 시점에 외부 트리거로 자동 실행되며, 본 5-4 v23 Extension Items 도메인은 자체 콘텐츠 작업을 수행하지 않는다. STAGE 9 Phase B-2 결정 이후 본 도메인 상태는 변경되지 않으며, 인덱스 상태 칼럼만 Part2 진행에 따라 SHELL→STUB→REF로 점진 전환됨.

### 7.4 Phase 게이트 조건

| Phase 전환 | 게이트 조건 |
|-----------|-----------|
| P0 → P1 | 계획서 14+1 섹션 완성 + AUTHORITY_CHAIN.md(LOCK 8건) + CONFLICT_LOG.md 초기화 완료 |
| V2-P2 → V2-P3 | V2-P2 HIGH 24건 100% REF + MEDIUM 27건 70% 이상 STUB/REF |
| V2-P3 → V3-P2 | V2-P3 HIGH 전수 REF + MEDIUM 70% 이상 STUB/REF |
| V3-P2 → V3-P3 | V3-P2 MEDIUM 2건 STUB 이상 + LOW 4건 상태 무관 |
| V3-P3 완료 | V3-P3 HIGH 3건 100% REF + MEDIUM 70% 이상 STUB/REF |

---

## 8. 파일 역할 분리 명세

| 파일 | 역할 | 갱신 주기 |
|------|------|----------|
| `V23_EXTENSION_ITEMS_구조화_종합계획서.md` | 메타 정본: 구조, 거버넌스, 로드맵 | 분기별 |
| `V23_EXTENSION_ITEMS_인덱스.md` | 추적 정본: 87건 전수 상태 추적 | 상태 변경 시 즉시 |
| `AUTHORITY_CHAIN.md` | LOCK 정본: 8개 LOCK 항목 관리 | LOCK 변경 시 |
| `CONFLICT_LOG.md` | 충돌 이력: 불일치 발견/해결 기록 | 발견 시 즉시 |
| `01_high-priority/_index.md` | HIGH 32건 상세 추적 | 상태 변경 시 즉시 |
| `02_medium-priority/_index.md` | MEDIUM 42건 상세 추적 | 상태 변경 시 즉시 |
| `03_low-priority/_index.md` | LOW 13건 상세 추적 | 상태 변경 시 즉시 |

---

## 9. 충돌 해결 프로토콜

### 9.1 충돌 유형

| 유형 | 설명 | 해결 원칙 |
|------|------|----------|
| A: Part2 vs 인덱스 | Phase 범위/우선순위 불일치 | Part2가 정본 (Level 2 우선) |
| B: 인덱스 vs 도메인 sot 2/ | 상태/상세 내용 불일치 | 도메인 sot 2/가 상세 정본, 인덱스는 상태만 반영 |
| C: 인덱스 내부 | 통계 테이블과 본문 항목 수 불일치 | 본문 개별 항목 기준으로 통계 재계산 |
| D: 우선순위 변경 요청 | 분기 리뷰 외 임의 변경 시도 | R-20-3에 의해 차단, 분기 리뷰까지 보류 |

### 9.2 해결 프로세스

```
1. 충돌 발견 → CONFLICT_LOG.md에 등록 (OPEN)
2. 정본 출처 확인 → AUTHORITY_CHAIN.md의 권한 체계 참조
3. 상위 정본 기준으로 해결 → 인덱스 갱신
4. CONFLICT_LOG 상태를 RESOLVED/VERIFIED로 갱신
5. 관련 LOCK 항목 영향 확인
```

---

## 10. 검증 체크리스트

### 10.1 구조 검증

- [ ] 87건 전수가 인덱스에 등록되어 있는가?
- [ ] Phase별 합계: V2-P2(51) + V2-P3(14) + V3-P2(6) + V3-P3(16) = 87인가?
- [ ] 우선순위별 합계: HIGH + MEDIUM + LOW = 87인가?
- [ ] 서브폴더 3개 (01/02/03) 존재하는가?
- [ ] AUTHORITY_CHAIN.md에 8개 LOCK 등록되어 있는가?
- [ ] CONFLICT_LOG.md 초기화되어 있는가?

### 10.2 참조 무결성 검증

- [ ] 18개 SOT 2 참조 폴더가 모두 존재하는가?
- [ ] 각 항목의 SOT 2 참조 경로가 인덱스와 계획서에서 일치하는가?
- [ ] Part2 Phase별 범위와 인덱스가 정확히 대응하는가?

### 10.3 거버넌스 검증

- [ ] R-20-1 ~ R-20-5 규칙이 모두 문서화되어 있는가?
- [ ] LOCK 항목 8개의 정본 출처가 명시되어 있는가?
- [ ] Phase 게이트 조건이 정의되어 있는가?

---

## 11. 보완 사항

> **Tier 5 간소화 적용**: 추적 인덱스이므로 보완 사항 최소

| # | 보완 항목 | 우선순위 | 시기 | 상태 |
|---|----------|---------|------|------|
| S-1 | V2-P2 LOW 건수 확인 — 인덱스 전수 대조 결과 0건 확정 | HIGH | Phase 1 | DONE |
| S-2 | 의존성 그래프 작성 (87건 간 선후행) | MEDIUM | Phase 2 | OPEN |
| S-3 | 자동화 스크립트: 상태 변경 시 인덱스 자동 갱신 | LOW | Phase 3+ | OPEN |

### 11.1 OPEN 3건 해결 확인 (CFL-GOV-005/006/007)

> S10-3 QC 과정에서 기존 OPEN 3건의 해결 상태를 명시적으로 문서화한다.

| 충돌 ID | 내용 | 해결 상태 | 검증 이력 |
|---------|------|----------|----------|
| **CFL-GOV-005** | 거버넌스 규칙 적용 범위 불명확 — R-20-3 분기 리뷰 외 임의 변경 차단 규칙의 적용 시점 미정 | **RESOLVED** | S7-5에서 최초 해결, S8-4에서 이중 검증 완료. R-20-3 적용 시점은 "인덱스 공식 등록 이후"로 확정. |
| **CFL-GOV-006** | Phase별 분류 집계 불일치 — V2-P3 HIGH 항목 수 1건 차이 | **RESOLVED** | S7-5에서 집계 보정, S8-4에서 전수 재계산으로 87건 일치 확인. CONFLICT_LOG에 보정 이력 기록 완료. |
| **CFL-GOV-007** | SOT 2 참조 경로 미확인 — 18개 폴더 중 일부 존재 미확인 | **RESOLVED** | S7-5에서 14/18 확인, S8-4에서 나머지 4건 확인 완료. S10-3에서 전수 존재 검증 PASS. |

---

## 12. FINAL REVIEW 결과

> **상태**: APPROVED — Phase 8 QC B+ → Phase 10 QC A- (2026-03-27)

| 항목 | 결과 | 비고 |
|------|------|------|
| **87건 전수 등록** | PASS | 인덱스 218줄에 87건 전수 존재 확인 |
| **Phase별 분류 정확성** | PASS | V2-P2: 51건, V2-P3: 14건, V3-P2: 6건, V3-P3: 16건 = 87건 전수 일치 |
| **SOT 2 참조 경로** | PASS | 18개 폴더 존재 확인 완료 — S10-3에서 전수 검증 (PARTIAL → PASS 승격) |
| **LOCK 항목 완전성** | PASS | 8건 registered, Part2 출처 전수 대조 완료 |
| **거버넌스 규칙** | PASS | R-20-1 ~ R-20-5 정의 완료, 규칙 간 충돌 없음 확인 |
| **OPEN 3건** | PASS | CFL-GOV-005/006/007 전부 RESOLVED — S7-5/S8-4 이중 검증 완료 (§11 참조) |
| **Gate 판정** | **APPROVED** | Phase 8 QC B+ → Phase 10 QC A- (2026-03-27). 모든 OPEN 항목 해결, 전수 검증 완료. |

---

## 13. L3 전수 승급 계획

> **해당 없음** — 본 도메인은 미래 확장 항목의 추적 인덱스이므로 L3 승급 대상이 아님.

각 항목의 L3 승급은 해당 항목이 배정된 SOT 2 도메인 폴더에서 개별 관리:
- `1-1_Verifier-Reasoning-Engines/` → 12건의 L3 승급은 해당 도메인 계획서에서 관리
- `2-1_Blue-Node-Architecture/` → 7건의 L3 승급은 해당 도메인 계획서에서 관리
- (이하 18개 폴더 동일)

---

## 14. 실행 약점 대응 계획

> **Tier 5 간소화 적용**

### 14.1 식별된 약점

| # | 약점 | 위험도 | 대응 |
|---|------|--------|------|
| W-1 | SHELL 상태 장기 방치 | HIGH | Phase 게이트(R-20-5)로 강제 전환 유도. 분기별 리뷰에서 미진행 항목 식별 |
| W-2 | Part2 로드맵 지연 | HIGH | 인덱스는 Part2 종속이므로, Part2 미확정 시 본 인덱스도 정체. 독립적 STUB 전환이라도 진행 |
| W-3 | 우선순위 집계 오류 | MEDIUM | §6 전수 매핑과 인덱스 통계 테이블 간 교차 검증 필수. CONFLICT_LOG로 추적 |
| W-4 | SOT 2 참조 폴더 미존재 | MEDIUM | Phase 1에서 18개 폴더 존재 확인. 미존재 시 생성 요청 |
| W-5 | 교차 도메인 조율 부재 | MEDIUM | 87건이 18개 도메인에 분산되므로, 분기별 전체 현황 보고서 작성 |

### 14.2 모니터링 지표

| 지표 | 목표 | 측정 주기 |
|------|------|----------|
| SHELL→STUB 전환율 | Phase별 목표 일정 대비 80% 이상 | 월간 |
| STUB→REF 전환율 | Phase별 목표 일정 대비 70% 이상 | 월간 |
| HIGH 항목 정체 기간 | 3개월 이내 STUB 전환 | 분기별 |
| 인덱스-Part2 동기화 | 100% 일치 | 상태 변경 시 즉시 |

---

## 부록 §A — 우선순위별 구현 계획

### A.1 우선순위 분류 기준

| 등급 | 기준 | 설명 |
|------|------|------|
| **HIGH** | 핵심 기능 / 사용자 영향 대 / 다른 항목 의존성 상위 | V1 기능의 자연스러운 진화, 핵심 UX 개선, 보안/안정성 필수 |
| **MEDIUM** | 품질 향상 / 사용자 편의 / 중간 의존성 | 기능 확장, 고급 사용자 대상, 운영 효율화 |
| **LOW** | 연구 성격 / 장기 비전 / 의존성 최소 | 실험적 기능, 미래 기술 탐색, 선택적 구현 |

### A.2 HIGH 우선순위 구현 계획 (32건)

> CONFLICT_LOG CL-003/CL-004/CL-006 보정 반영: HIGH 32건 확정.

#### V2-Phase 2 HIGH (24건)

| # | 항목명 | 소스 ID | 예상 공수 | 의존성 | SOT 2 참조 폴더 |
|---|--------|---------|----------|--------|----------------|
| 1 | Advanced Reasoning Chain | V2-P2-11 | L | V1 Reasoning 완료 | `1-1_Verifier-Reasoning-Engines/` |
| 2 | Multi-step Planning Engine | V2-P2-12 | L | V2-P2-11 | `1-1_Verifier-Reasoning-Engines/` |
| 3 | Self-correction Loop | V2-P2-13 | M | V2-P2-11 | `1-1_Verifier-Reasoning-Engines/` |
| 4 | Confidence Calibration | V2-P2-14 | M | V2-P2-11 | `1-1_Verifier-Reasoning-Engines/` |
| 5 | Episodic Memory Engine | V2-P2-16 | L | Blue Node V1 | `2-1_Blue-Node-Architecture/` |
| 6 | Semantic Memory Consolidation | V2-P2-17 | L | V2-P2-16 | `2-1_Blue-Node-Architecture/` |
| 7 | Cross-session Recall | V2-P2-20 | M | V2-P2-16, V2-P2-17 | `2-1_Blue-Node-Architecture/` |
| 8 | Knowledge Graph Builder v2 | V2-P2-21 | L | PKM V1 | `3-3_PKM-Knowledge-Management/` |
| 9 | ColBERT v3 Integration | V2-P2-24 | M | COND V1 | `2-2_COND-Modules-Detail/` |
| 10 | Self-RAG Implementation | V2-P2-25 | L | V2-P2-24 | `2-2_COND-Modules-Detail/` |
| 11 | CRAG (Corrective RAG) | V2-P2-26 | M | V2-P2-25 | `2-2_COND-Modules-Detail/` |
| 12 | Multi-agent Orchestrator | V2-P2-31 | L | A2A V1 | `3-8_Conversation-A2A/` |
| 13 | Task Decomposition Engine | V2-P2-33 | M | Workflow V1 | `3-4_Workflow-RPA/` |
| 14 | Human-in-the-Loop Protocol v2 | V2-P2-36 | M | V2-P2-33 | `3-4_Workflow-RPA/` |
| 15 | Voice Input/Output | V2-P2-38 | L | Multimodal V1 | `3-2_Multimodal-Processing/` |
| 16 | Accessibility Compliance (WCAG 2.1 AA) | V2-P2-41 | M | UI Framework | `3-7_Developer-Tools-API-SDK/` |
| 17 | Spaced Repetition Engine v2 | V2-P2-42 | M | Education V1 | `3-5_Education-Learning/` |
| 18 | Adaptive Learning Path | V2-P2-43 | M | V2-P2-42 | `3-5_Education-Learning/` |
| 19 | Emotion Detection v2 | V2-P2-45 | M | Health V1 | `3-6_Health-Wellness-EmotionAI/` |
| 20 | Portfolio Optimizer | V2-P2-48 | L | Investing V1 | `Ai-investing-detail/` |
| 21 | Plugin Architecture v2 | V2-P2-51 | L | DevTools V1 | `3-7_Developer-Tools-API-SDK/` |
| 22 | Auto-update Mechanism | V2-P2-53 | M | Tauri V1 | `4-1_Rust-Tauri-Infrastructure/` |
| 23 | End-to-End Encryption | V2-P2-56 | L | Tauri V1 | `4-1_Rust-Tauri-Infrastructure/` |
| 24 | Backup & Restore | V2-P2-57 | M | V2-P2-56 | `4-1_Rust-Tauri-Infrastructure/` |

> **검증**: 인덱스 원본 전수 대조 결과 V2-P2 HIGH = 24건 확정. 위 24건 전수 인덱스 HIGH 표기와 일치.

#### V2-Phase 3 HIGH (5건)

| # | 항목명 | 소스 ID | 예상 공수 | 의존성 | SOT 2 참조 폴더 |
|---|--------|---------|----------|--------|----------------|
| 1 | Sparse Attention Implementation | V2-P3-10 | L | V2-P2 Reasoning 완료 | `1-1_Verifier-Reasoning-Engines/` |
| 2 | Mixture-of-Experts Routing | V2-P3-11 | L | V2-P3-10 | `1-1_Verifier-Reasoning-Engines/` |
| 3 | Advanced A2A Protocol | V2-P3-14 | L | V2-P2-31 Multi-agent | `3-8_Conversation-A2A/` |
| 4 | Natural Language Workflow | V2-P3-16 | M | V2-P2-33 Task Decomp | `3-4_Workflow-RPA/` |
| 5 | Privacy-preserving Inference | V2-P3-21 | L | V2-P2-56 E2E Encryption | `4-1_Rust-Tauri-Infrastructure/` |

> **검증**: V2-P3 HIGH = {10,11,14,16,21} = 5건. 인덱스 원본과 정확 일치.

#### V3-Phase 3 HIGH (3건)

| # | 항목명 | 소스 ID | 예상 공수 | 의존성 | SOT 2 참조 폴더 |
|---|--------|---------|----------|--------|----------------|
| 1 | AGI Safety Framework | V3-P3-11 | L | V2 전체 완료 | `1-1_Verifier-Reasoning-Engines/` |
| 2 | Emergent Behavior Monitor | V3-P3-12 | L | V3-P3-11 | `4-4_MLOps-LLMOps/` |
| 3 | AI Ethics Governance Module | V3-P3-21 | M | V3-P3-11 | `3-9_Business-Model-Strategy/` |

### A.3 MEDIUM 우선순위 구현 계획 (42건)

> 42건 전수 목록은 §6.1의 02_medium-priority/ 테이블 참조. 아래는 Phase별 요약.

| Phase | 건수 | 주요 영역 | 예상 공수 분포 |
|-------|------|----------|---------------|
| V2-Phase 2 | 27건 | RAG(4), Agent(3), UI(3), Domain(5), Infra(6), Memory(2), PKM(2), etc. | S:8, M:14, L:5 |
| V2-Phase 3 | 7건 | ML/AI(3), Multimodal(2), Agent(1), Business(1) | S:1, M:4, L:2 |
| V3-Phase 2 | 2건 | Reasoning(1), MLOps(1) | M:1, L:1 |
| V3-Phase 3 | 6건 | DevTools(2), Workflow(1), Infra(1), Eval(1), MCP(1) | S:1, M:3, L:2 |

### A.4 LOW 우선순위 구현 계획 (13건)

> 13건 전수 목록은 §6.1의 03_low-priority/ 테이블 참조. 아래는 Phase별 요약.

| Phase | 건수 | 성격 | 비고 |
|-------|------|------|------|
| V2-Phase 2 | 0건 | 인덱스 전수 대조 결과 V2-P2에 LOW 항목 없음 | 확인 완료 |
| V2-Phase 3 | 2건 | 3D Data Processing(V2-P3-19), Multi-cloud Deployment(V2-P3-22) | 실험적/선택적 |
| V3-Phase 2 | 4건 | Neuro-symbolic, World Model, Compositional, Cognitive | 순수 연구 |
| V3-Phase 3 | 7건 | Knowledge Discovery, Collective Intelligence, Emotion Synthesis, DID, NL Database, Digital Twin, Zero-shot | 미래 비전 |

### A.5 공수 범례

| 등급 | 정의 | 예상 기간 |
|------|------|----------|
| S (Small) | 기존 구현 확장, 설정 변경 수준 | 1~2주 |
| M (Medium) | 신규 모듈, 중간 복잡도 | 3~6주 |
| L (Large) | 핵심 아키텍처 변경, 높은 복잡도 | 2~3개월 |

### A.6 핵심 의존성 그래프 (HIGH 항목)

```
V1 Core 완료
├── V2-P2 Reasoning (11~14) ──→ V2-P3 Sparse/MoE (10,11)
├── V2-P2 Memory (16,17,20) ──→ (도메인 내부 순차)
├── V2-P2 RAG (24,25,26) ──→ (도메인 내부 순차)
├── V2-P2 Agent (31,33,36) ──→ V2-P3 A2A (14), NL Workflow (16)
├── V2-P2 Infra (53,56,57) ──→ V2-P3 Privacy (21)
└── V2 전체 완료 ──→ V3-P3 AGI Safety (11) ──→ Emergent (12), Ethics (21)
```

---

> **문서 끝** | 총 87건 추적 | Tier 5 간소화 적용 | Phase 1 완료 (2026-04-12) | 다음 단계: Phase 2+ Part2 로드맵 종속 추적
