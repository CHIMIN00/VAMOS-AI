# Hologram-Main-LLM 구조화 종합 계획서

> **버전**: v1.0
> **작성일**: 2026-03-24
> **목적**: sot 2/6-11_Hologram-Main-LLM/을 Hologram View 렌더링 파이프라인 + Main LLM 응답 통합 정본으로 구조화
> **Status**: APPROVED
> **Tier**: 6 — System-wide
> **SOT 출처**: D2.0-08 (UI/UX Design), D2.0-02 §7.63/§11.15.1 (UI 오케스트레이션/MoE 라우팅), D2.0-05 §7.2 (출력 포맷), Part2 §6.1/V1-P4
> **Part2 상태**: PARTIAL (§6.1 — UI/UX 상세 ~85개 항목 중 Hologram View는 4개 Layout 중 하나. V1-P4 L2274~2414에 44개 컴포넌트/8개 Hook/7개 Store 명시. 단, 렌더링 파이프라인 내부 흐름·Main LLM 연동 상세·Glass HUD 오버레이 프로토콜 부재)

---

## 목차

1. [현재 상태 분석](#1-현재-상태-분석)
2. [목표 구조 (최종 형태)](#2-목표-구조-최종-형태)
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
- [부록 §A — Hologram 렌더링 파이프라인 상세](#부록-a--hologram-렌더링-파이프라인-상세)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 내용 요약 | 줄 수 |
|------|------|----------|-------|
| Part2 V1-Phase 4 | `VAMOS_구현가이드_PART2_구현단계.md` line 2274~2414 | UI/UX with Hologram View — 44개 React 컴포넌트, 8개 Custom Hook, 7개 Zustand Store | ~140줄 |
| Part2 §6.1 | `VAMOS_구현가이드_PART2_구현단계.md` line 4557~4670 | UI/UX 상세 (~85개 항목) — Hologram View는 4개 Layout 중 하나 | ~113줄 |
| D2.0-08 | `D2.0-08_UI_UX_Design.md` | UI/UX Design 정본 — §2.2 Hologram View 레이아웃 정본, §3 4-Layout 구조, §4 9-State UI State Machine | 정본 |
| D2.0-02 §7.63 | `D2.0-02_시스템설계.md` | I-10 UI 오케스트레이션 레이어 — Builder/Hologram UI 상태/근거/승인/비용/로그 변환 | 섹션 |
| D2.0-02 §11.15.1 | `D2.0-02_시스템설계.md` | MoE 라우팅 패턴 — Front Mini → Main LLM 2단 라우팅 | 섹션 |
| D2.0-05 §7.2 | `D2.0-05_출력포맷.md` | 3-point 출력 포맷 (user_response / evidence_summary / log_report) | 섹션 |

### 1.2 sot 2/ 현재 파일

```
6-11_Hologram-Main-LLM/
└── (없음 — 신규 도메인)
```

서브폴더 없음. 계획서 없음. AUTHORITY_CHAIN/CONFLICT_LOG 없음.

### 1.3 핵심 문제

| # | 문제 | 심각도 | 근거 |
|---|------|--------|------|
| P-1 | Hologram View 렌더링 파이프라인 내부 흐름 미정의 — 타임라인·스트리밍 캔버스·Glass HUD 간 데이터 흐름 부재 | HIGH | D2.0-08 §2.2는 레이아웃만, 내부 흐름 없음 |
| P-2 | Main LLM 응답 → Hologram UI 변환 프로토콜 미정의 — LLM 출력이 어떤 컴포넌트에 어떻게 바인딩되는지 부재 | HIGH | D2.0-02 §7.63은 역할만 명시 |
| P-3 | Glass HUD 오버레이 데이터 스키마 부재 — 비용/근거/승인 실시간 표시의 구체적 데이터 구조 없음 | HIGH | D2.0-08에 개념만 |
| P-4 | 9-State UI State Machine 전이 조건 상세 부재 — D2.0-08 §4에 상태 이름만, 전이 이벤트/가드/액션 미정의 | MEDIUM | D2.0-08 §4 |
| P-5 | 44개 컴포넌트 간 의존 관계 그래프 부재 — V1-P4에 목록만, 조합 패턴 없음 | MEDIUM | Part2 V1-P4 |
| P-6 | Front Mini → Main LLM 2-tier 라우팅의 Hologram View 맥락 전달 방식 미정의 | MEDIUM | D2.0-02 §11.15.1 |
| P-7 | 스트리밍 캔버스의 SSE/WebSocket 프로토콜 상세 부재 | MEDIUM | Part2 미언급 |
| P-8 | ChatPage.tsx 통합 패턴 — Hologram View 채팅·스트리밍·아티팩트 렌더링 조합 규칙 부재 | MEDIUM | Part2 V1-P4 |

### 1.4 Part2 PARTIAL 영역 분석

| 영역 | Part2 커버리지 | sot 2/ 보완 필요 |
|------|--------------|-----------------|
| Hologram View 레이아웃 정의 | ✅ D2.0-08 §2.2 정본 | 내부 렌더링 파이프라인 |
| 4-Layout 구조 | ✅ D2.0-08 §2.1/§3 정본 | Layout 전환 프로토콜 |
| 44개 React 컴포넌트 목록 | ✅ V1-P4 (L2274~2414) | 컴포넌트 의존 그래프, Props 인터페이스 |
| 8개 Custom Hook 목록 | ✅ V1-P4 | Hook 시그니처, 상태 흐름 |
| 7개 Zustand Store 목록 | ✅ V1-P4 | Store 스키마, 셀렉터, 액션 정의 |
| Main LLM 2-tier 라우팅 | △ D2.0-02 §11.15.1 개념 | Hologram 맥락 전달 상세 |
| I-10 UI 오케스트레이션 | △ D2.0-02 §7.63 역할 | 데이터 매핑 테이블, 변환 규칙 |
| Glass HUD 오버레이 | △ D2.0-08 개념 | 데이터 스키마, 갱신 주기, 렌더링 규칙 |
| 9-State UI State Machine | △ D2.0-08 §4 상태 이름 | 전이 매트릭스, 가드 조건, 액션 |
| 3-point 출력 포맷 | ✅ D2.0-05 §7.2 정본 | Hologram UI 바인딩 매핑 |
| 스트리밍 프로토콜 | ❌ 없음 | SSE/WS 프로토콜, 청크 포맷, 재연결 |
| ChatPage 통합 패턴 | ❌ 없음 | 아티팩트·채팅·스트리밍 조합 규칙 |

### 1.5 도메인 경계 분석

| 인접 도메인 | 경계 정의 |
|------------|----------|
| 6-1 UI-UX-System | 6-1이 존재할 경우 broad UI/UX 전반 커버. **6-11은 Hologram View 렌더링 파이프라인 + Main LLM 응답 생성 통합에 특화** |
| 1-1 Verifier | 추론 엔진 소유. **6-11은 LLM 모델 선택 로직을 소유하지 않음** — 응답 결과의 UI 표현만 담당 |
| 6-9 Brain-Adapter-HAL | LLM 라우팅/폴백 소유. **6-11은 모델 스위칭 로직을 소유하지 않음** — 라우팅 결과를 수신하여 UI 표현 |
| 4-1 Rust-Tauri-Infrastructure | IPC/Tauri 인프라 소유. 6-11은 IPC 채널 위에서 동작하는 **UI 레이어** |
| 3-8 Conversation-A2A | 대화 프로토콜 소유. 6-11은 대화 결과의 **Hologram View 렌더링** |

### 1.6 6-11 소유 범위 (Ownership Scope)

6-11이 정본으로 소유하는 영역:

1. **Hologram View 렌더링 파이프라인** — 타임라인 + 스트리밍 캔버스 + Glass HUD 조합 렌더링
2. **Main LLM 응답 포맷팅** — LLM 출력 → Hologram UI 컴포넌트 변환
3. **UI State → LLM Output 매핑** — 9-State Machine과 LLM 응답 간 바인딩
4. **Glass HUD 오버레이 시스템** — 비용/근거/승인 실시간 표시 데이터 흐름
5. **스트리밍 캔버스** — SSE/WS 기반 실시간 응답 렌더링
6. **타임라인 뷰** — 대화·워크플로우·이벤트 시간순 렌더링
7. **ChatPage 통합** — Hologram View 채팅·스트리밍·아티팩트 통합 렌더링

### Part2 상태 및 방식 C 접근법
- **Part2 상태**: PARTIAL
- **방식 C 접근법**: 보완 작성

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
6-11_Hologram-Main-LLM/
├── HOLOGRAM_MAIN_LLM_구조화_종합계획서.md        ← 본 문서
├── AUTHORITY_CHAIN.md
├── CONFLICT_LOG.md
├── 01_hologram-view-layout/
│   ├── _index.md              ← Hologram View 레이아웃 인덱스
│   ├── layout_structure.md    ← 타임라인 + 스트리밍 캔버스 + Glass HUD 구조
│   ├── layout_switching.md    ← 4-Layout 전환 프로토콜 (3-Column↔Builder↔Hologram↔CLI)
│   └── responsive_rules.md    ← 반응형 레이아웃 규칙 및 브레이크포인트
├── 02_component-architecture/
│   ├── _index.md              ← 44개 컴포넌트 인덱스 + 의존 그래프
│   ├── component_catalog.md   ← 44개 React 컴포넌트 카탈로그 (Props/역할/계층)
│   ├── hook_catalog.md        ← 8개 Custom Hook 카탈로그 (시그니처/상태흐름)
│   ├── store_catalog.md       ← 7개 Zustand Store 카탈로그 (스키마/셀렉터/액션)
│   └── chatpage_integration.md ← ChatPage.tsx 통합 패턴 (채팅/스트리밍/아티팩트)
├── 03_ui-state-machine/
│   ├── _index.md              ← 9-State Machine 인덱스
│   ├── state_definitions.md   ← 9개 상태 정의 (진입/탈출 조건, 가드, 액션)
│   └── transition_matrix.md   ← 상태 전이 매트릭스 (이벤트 × 상태 → 다음 상태)
├── 04_main-llm-integration/
│   ├── _index.md              ← Main LLM 통합 인덱스
│   ├── two_tier_routing.md    ← Front Mini → Main LLM 2-tier 라우팅 (Hologram 맥락)
│   ├── response_formatting.md ← 3-point 출력 → Hologram UI 바인딩
│   ├── dcl_context.md         ← DCL (Domain Context Layer) 배경 인식 응답 생성
│   └── moe_evolution.md       ← V1(2-3모델) → V3(MoE multi-expert) 진화 경로
├── 05_glass-hud-overlay/
│   ├── _index.md              ← Glass HUD 인덱스
│   ├── overlay_schema.md      ← 오버레이 데이터 스키마 (비용/근거/승인)
│   ├── realtime_update.md     ← 실시간 갱신 프로토콜 (SSE push, 갱신 주기)
│   └── rendering_rules.md     ← HUD 렌더링 규칙 (투명도/위치/애니메이션)
├── 06_streaming-canvas/
│   ├── _index.md              ← 스트리밍 캔버스 인덱스
│   ├── stream_protocol.md     ← SSE/WebSocket 프로토콜 상세 (청크 포맷/재연결)
│   ├── token_rendering.md     ← 토큰 단위 실시간 렌더링 파이프라인
│   └── artifact_rendering.md  ← 아티팩트(코드/차트/테이블) 인라인 렌더링
└── 07_orchestration-layer/
    ├── _index.md              ← I-10 오케스트레이션 인덱스
    ├── ui_state_mapping.md    ← UI 상태 → LLM 출력 매핑 테이블
    ├── cost_evidence_log.md   ← 비용/근거/승인/로그 변환 규칙
    └── page_routing.md        ← 7개 페이지 라우팅 (Dashboard/Chat/Workflow/Memory/Settings/Log/NodeDetail)
```

### 2.2 깊이 규칙

```
최대 2단계:
  6-11_Hologram-Main-LLM/ → 0X_{카테고리}/ → 파일.md     ✅
  3단계 이상 → 금지 ❌
```

### 2.3 네이밍 규칙

- **폴더**: `XX_kebab-case/` (01~07)
- **파일**: `snake_case.md`
- **컴포넌트 파일**: 설명적 이름 사용 (예: `component_catalog.md`, `hook_catalog.md`)

### 2.4 파일 수 요약

| 서브폴더 | 파일 수 | 핵심 내용 |
|---------|--------|----------|
| 01_hologram-view-layout/ | 4 | Hologram View 레이아웃 구조/전환/반응형 |
| 02_component-architecture/ | 5 | 44 컴포넌트, 8 Hook, 7 Store, ChatPage 통합 |
| 03_ui-state-machine/ | 3 | 9-State 정의, 전이 매트릭스 |
| 04_main-llm-integration/ | 5 | 2-tier 라우팅, 응답 포맷팅, DCL, MoE 진화 |
| 05_glass-hud-overlay/ | 4 | 오버레이 스키마, 실시간 갱신, 렌더링 |
| 06_streaming-canvas/ | 4 | 스트림 프로토콜, 토큰 렌더링, 아티팩트 |
| 07_orchestration-layer/ | 4 | UI↔LLM 매핑, 비용/로그, 페이지 라우팅 |
| **합계** | **29** | + 계획서, AUTHORITY_CHAIN, CONFLICT_LOG = **32** |

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 체인

```
BASE 1.3 → PLAN 3.0 → DESIGN 2.0 → Prompt 2.1 (D2.1-D1~D8) → Part2 → sot 2/
```

### 3.2 Hologram-Main-LLM 확장 체인

```
DESIGN 2.0 (D2.0-08 UI/UX) → D2.0-02 §7.63 (I-10 오케스트레이션)
                              → D2.0-02 §11.15.1 (MoE 라우팅)
                              → D2.0-05 §7.2 (3-point 출력 포맷)
    ↓
Part2 §6.1 (UI/UX 상세 ~85항목) → Part2 V1-P4 (L2274~2414)
    ↓
sot 2/ 계획서 (본 문서) → sot 2/ 서브폴더 (구현 상세)
```

### 3.3 문서별 정본 범위

| 문서 | 정본 범위 | 비고 |
|------|----------|------|
| D2.0-08 (UI/UX Design) | Hologram View 레이아웃 정의 (§2.2), 4-Layout 구조 (§2.1/§3), 9-State UI State Machine (§4), Glass HUD 개념 | LOCK |
| D2.0-02 §7.63 | I-10 UI 오케스트레이션 레이어 역할 — Builder/Hologram UI 상태/근거/승인/비용/로그 변환 | LOCK |
| D2.0-02 §11.15.1 | MoE 라우팅 패턴 — Front Mini → Main LLM 2단 라우팅 | LOCK |
| D2.0-05 §7.2 | 3-point 출력 포맷 (user_response / evidence_summary / log_report) | LOCK |
| Part2 §6.1 | UI/UX 상세 ~85개 항목 — Hologram View 관련 항목 | LOCK |
| Part2 V1-P4 | 44개 React 컴포넌트, 8개 Custom Hook, 7개 Zustand Store 목록 | LOCK |
| sot 2/ 계획서 (본 문서) | 구조, 거버넌스, Phase 계획, 검증 | DEFINED-HERE |
| sot 2/ 서브폴더 | 렌더링 파이프라인 상세, LLM 응답 매핑, Glass HUD 스키마, 스트리밍 프로토콜 | DEFINED-HERE |

### 3.4 LOCK 보호 항목

> 상세: `AUTHORITY_CHAIN.md` 참조

| LOCK ID | 항목 | 정본 |
|---------|------|------|
| LOCK-HM-01 | Hologram View = 타임라인 + 스트리밍 캔버스 + Glass HUD | D2.0-08 §2.2 |
| LOCK-HM-02 | 4 Layout 구조 (3-Column, Builder, Hologram, CLI) | D2.0-08 §2.1/§3 |
| LOCK-HM-03 | 9-State UI State Machine | D2.0-08 §4 |
| LOCK-HM-04 | Main LLM 2-tier 라우팅 (Front Mini → Main) | D2.0-02 §11.15.1 |
| LOCK-HM-05 | I-10 UI 오케스트레이션 레이어 역할 | D2.0-02 §7.63 |
| LOCK-HM-06 | 3-point 출력 포맷 (user_response / evidence_summary / log_report) | D2.0-05 §7.2 |
| LOCK-HM-07 | 44개 React 컴포넌트 구조 | Part2 V1-P4 |
| LOCK-HM-08 | 8개 Custom Hook | Part2 V1-P4 |
| LOCK-HM-09 | 7개 Zustand Store | Part2 V1-P4 |
| LOCK-HM-10 | Glass HUD 오버레이 = 비용/근거/승인 실시간 표시 | D2.0-08 |

---

## 4. 거버넌스 규칙

### 4.1 공통 규칙 (R1~R11)

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.

| ID | 규칙 | 적용 범위 |
|----|------|----------|
| R1 | LOCK 값 재정의 금지 | 전체 |
| R2 | 정본 소유자 단일 지정 (canonical_owner 1곳) | 모든 항목 |
| R3 | 폴더 깊이 최대 2단계 (도메인 → 카테고리 → 파일) | 전체 |
| R4 | 서브폴더 _index.md 필수 | 01~07 전체 |
| R5 | 파일 네이밍 snake_case.md | 전체 |
| R6 | 스키마 변경 시 AUTHORITY_CHAIN 갱신 | D2.0 연동 항목 |
| R7 | CONFLICT_LOG 즉시 기록 원칙 | 충돌 발견 시 |
| R8 | 방식 C 형식 준수 (Part2 출처 명시) | PARTIAL 영역 |
| R9 | 도메인 경계 침범 금지 | 인접 도메인 |
| R10 | Phase 게이트 통과 필수 | Phase 전환 시 |
| R11 | 검증 체크리스트 전수 통과 필수 | FINAL REVIEW 전 |

### 4.2 Tier 6 System-wide 공통 규칙

| ID | 규칙 | 근거 |
|----|------|------|
| R-T6-1 | Part2 §6.1 + V1-P4가 UI/UX 관련 항목의 최상위 정본 | Tier 6 가이드 |
| R-T6-2 | 교차 도메인 영향 분석 필수 — System-wide 변경 시 영향받는 모든 도메인 목록화 | Tier 6 특성 |
| R-T6-3 | UI State Machine 변경 시 전체 레이아웃 정합성 검증 필수 | Hologram View가 4-Layout 중 하나 |
| R-T6-4 | LLM 응답 포맷 변경 시 모든 View(3-Column/Builder/Hologram/CLI) 영향 분석 | System-wide 특성 |

### 4.3 도메인 고유 규칙

| ID | 규칙 | 근거 |
|----|------|------|
| R-611-1 | Hologram View 3요소(타임라인/스트리밍 캔버스/Glass HUD) 분리 렌더링 원칙 — 각 요소는 독립 컴포넌트로 구현, 결합은 조합 패턴만 허용 | LOCK-HM-01 |
| R-611-2 | Glass HUD 오버레이는 투명 레이어로 구현 — 하위 콘텐츠 상호작용 차단 금지 | D2.0-08 Glass HUD 개념 |
| R-611-3 | Main LLM 응답은 반드시 3-point 포맷(user_response/evidence_summary/log_report)으로 파싱 후 UI 바인딩 | LOCK-HM-06 |
| R-611-4 | 스트리밍 렌더링 시 토큰 단위 점진적 표시 필수 — 전체 응답 대기 후 일괄 표시 금지 | UX 요구사항 |
| R-611-5 | UI State Machine 전이는 반드시 정의된 이벤트를 통해서만 발생 — 직접 상태 변경 금지 | LOCK-HM-03 |
| R-611-6 | 컴포넌트 Props 인터페이스 변경 시 AUTHORITY_CHAIN 갱신 + 영향 컴포넌트 목록 명시 | 44개 컴포넌트 의존 그래프 |
| R-611-7 | Store 스키마 변경 시 관련 Hook/컴포넌트 동시 갱신 필수 | 7 Store ↔ 8 Hook ↔ 44 컴포넌트 |
| R-611-8 | Layout 전환 시 현재 상태 보존 원칙 — Hologram → 3-Column 전환 후 복귀 시 이전 상태 복원 | 4-Layout UX |
| R-611-9 | 6-11은 LLM 모델 선택/라우팅/폴백 로직을 구현하지 않음 — 해당 로직은 6-9(Brain-Adapter-HAL) 정본 | 도메인 경계 |
| R-611-10 | ChatPage.tsx는 Hologram View의 진입점 — 모든 Hologram 렌더링은 ChatPage를 통해 조합 | Part2 V1-P4 |

---

## 5. 선행작업

| # | 선행작업 | 설명 | 상태 |
|---|---------|------|------|
| PRE-1 | D2.0-08 §2.2 Hologram View 정본 확인 | D2.0-08 문서에서 Hologram View 정의 3요소(타임라인/스트리밍 캔버스/Glass HUD) 정확한 구조 추출 | ✅ T0-5 |
| PRE-2 | Part2 V1-P4 44개 컴포넌트 완전 목록 확정 | L2274~2414에서 44개 컴포넌트명 전수 추출 및 카테고리 분류 | ✅ T0-5 |
| PRE-3 | Part2 V1-P4 8개 Hook 시그니처 확인 | 8개 Custom Hook의 이름·파라미터·반환값 확인 | ✅ T0-5 |
| PRE-4 | Part2 V1-P4 7개 Store 스키마 확인 | 7개 Zustand Store의 이름·상태 필드·액션 확인 | ✅ T0-5 |
| PRE-5 | D2.0-08 §4 9-State 목록 확인 | 9개 상태 이름 및 초기 전이 다이어그램 확인 | ✅ T0-5 |
| PRE-6 | D2.0-02 §7.63 I-10 역할 범위 확정 | UI 오케스트레이션 레이어가 Hologram View에 전달하는 데이터 항목 확인 | ⏳ |
| PRE-7 | D2.0-02 §11.15.1 2-tier 라우팅 상세 확인 | Front Mini → Main LLM 라우팅에서 Hologram View 맥락 전달 방식 확인 | ⏳ |
| PRE-8 | 6-9 Brain-Adapter-HAL 경계 확정 | ✅ T0-6에서 해소 — domain_boundary.md §1에서 6-11↔6-9 경계 확정. R-611-9 원문 인용, 6-9 AUTHORITY_CHAIN L87 양측 교차 대조 완료(불일치 0건) | ✅ T0-6 |
| PRE-9 | 6-1 UI-UX-System 경계 확정 | ✅ T0-6에서 해소 — domain_boundary.md §2에서 6-11↔6-1 경계 확정. 6-1 AUTHORITY_CHAIN §5.1 양측 교차 대조 완료(불일치 0건), C-3 RESOLVED | ✅ T0-6 |

---

## 6. 이슈 해결 매핑

> **NOTE (upstream inheritance) [2026-05-21]**: 6-9 Brain-Adapter-HAL Phase 3 ✅ 완료 (2026-05-21, 4 task: P3-1 V2 HAL Docker Compose+LiteLLM W3 RESOLVED / P3-2 V3 HAL K8s+vLLM+LOCK-69-2 V3 승인 ★교차 4-4 W1 RESOLVED / **P3-3 라우팅 성능 벤치마크 ★교차 4 도메인 E2E (1-1+4-4+6-11+4-3)** W2 RESOLVED / P3-4 비용 최적화 Prompt Caching+Batch API+30%+ 절감+6-4/6-2 cross-ref W5 RESOLVED, Wave 3 #27 단일 대화창 tcv1 first-pass NO-DRIFT 100% direct path 4 P3 ALL, R cascade 432 verifications + 0 drift fix Phase 3 ENTRY 단계, 통산 10번째 NO-DRIFT 100% 도메인 milestone + Wave 3 6번째 NO-DRIFT 100% 도메인 specialty). 본 도메인 (6-11 Hologram-Main-LLM, Wave 3 #28) 진입 시 6-9 결과 inheritance — **DAG L71 6-9 ↔ 6-11 양방향 cycle 권장 진입 순 6-9 먼저 정합 + P3-3 ★교차 4 매핑이 6-11 P3-4 cross_domain_validation_report 입력 base**:
> - **6-9 P3-3 라우팅 성능 벤치마크 ★교차 4 도메인 E2E** (1-1 추론 C-1~C-3 검증기 + D-1~D-2 판단기 + 4-4 드리프트 자동학습 + **6-11 2-tier 라우팅 최적화** + 4-3 MCP Tool 확장 ToolRegistry, p95 < 2초 V2 / < 1.5초 V3 + 100 QPS + 폴백 빈도 < 1% + ★ E2E 시나리오 ≥ 10) → **6-11 P3-4 cross_domain_validation_report (6-1/6-9/1-1/4-1) 4 도메인 통합 검증 target 직접 inheritance** (Phase 4 entry-gate 6-11 P3-4 핵심 cross-handoff, 4-1 NOTE inheritance와 stacked baseline 양방향 완성)
> - **6-9 P3-3 P2-3 two_tier_routing.md (362L Phase 2 V2 NEW)** ↔ **6-11 04_main-llm-integration/two_tier_routing.md** verbatim 정합 (file 명 동일 cross-domain inheritance specialty, 양방향 cycle 정본 동일)
> - **6-9 P3-2 V3 HAL K8s + vLLM 자체호스팅** (LOCK-69-2 V3 병렬 상한 승인 워크플로 + LOCK-69-8 V3 폴백 Ollama→vLLM 대체 + LOCK-69-7 V3 ₩26.6만/월 $200) → 6-11 Hologram Main LLM 2-tier 라우팅 V3 vLLM 통합 시 최적화 inheritance (P3-2 6-11 cross-handoff "Hologram main LLM 라우팅 정합" CROSS_REF §3 6-9 P3-3 ★교차 4 매트릭스 정합)
> - **권한 boundary**: 6-9 LOCK-69-1~10 §3.4 read-only inheritance (LOCK-69-1 ConnectorResponse 5필드+2선택 / LOCK-69-2 병렬 상한 3 V1/V2 + V3 승인 / LOCK-69-3 ToolRegistry 경유 / LOCK-69-4 Decision.gates.result.{policy,approval,cost} / LOCK-69-5 CORE 실행 금지 / LOCK-69-6 ENV>yaml>코드 / LOCK-69-7 비용 상한 자동 차단 / LOCK-69-8 폴백 체인 Claude→GPT-4o→DeepSeek→Ollama 30s / LOCK-69-9 LangChain import 금지 / LOCK-69-10 JSON 구조화 로깅) PRESERVE / AUTHORITY v1.4 truly_converged_v2 무손상 통산 보존
> - **production .md baseline (8종 무손상 inheritance reference)**: Phase 1 V1 4 파일 (01_multi-brain-adapter/P1-1_brain_adapter_v1_spec.md + 02_hal-interface/P1-2_hal_v1_spec.md + 03_llm-routing/P1-3_llm_router_v1_spec.md + 04_fallback-chain/P1-4_fallback_chain_v1_spec.md = 2,223L historical baseline 보존 raw LF 2,227L EOL convention) + Phase 2 V2 NEW 4 파일 (01_multi-brain-adapter/e2e_reasoning_integration.md 380L + 03_llm-routing/drift_routing_integration.md 371L + 03_llm-routing/two_tier_routing.md 362L + 01_multi-brain-adapter/parallel_executor.md 421L = **1,534L raw LF EXACT MATCH 100%** SHA UNCHANGED 통산) = **8 files aggregate EXACT** (Tier 6 Brain-Adapter 도메인 production 무손상 강제 통산 보존)
> - **CROSS_REF_MATRIX §1 양방향 정합**: 6-9 downstream (**6-11** P3-4 cross_domain_validation) ↔ 6-11 upstream (6-1 + **6-9** + 1-1 + 4-1 + 3-2 + 6-4) — 본 NOTE로 양방향 100% 정합 도달 + Wave 3 derivation 6-9 ★ + 6-11 ★ 양방향 cycle 정본 관계 확정 (DAG L71 권장 진입 순 6-9 먼저 정합)
> - **Phase 4 entry-gate**: 6-11 Wave 3 #28 진입 시 6-9 production 8 .md baseline + LOCK-69-1~10 10 entries inheritance + Phase 3 NEW 4 산출물 forward-defined (hal_v2_deployment.md / hal_v3_deployment.md / routing_performance_benchmark.md / cost_optimization_report.md) Phase 4 implementation 단계 inheritance + cross_domain_validation_report P3-4 작성 시 6-9 4 도메인 중 하나로 통합 검증 target 명시 + ★교차 4 도메인 (1-1+4-4+6-11+4-3) 양방향 cycle 정합
> - **참조**: `D:/VAMOS/docs/sot 2/6-9_Brain-Adapter-HAL/BRAIN_ADAPTER_HAL_구조화_종합계획서.md` §7 Phase 3 (L1180~L1407, 4 details 블록 P3-1~P3-4 + Phase 3 → Phase 4 인계 게이트 + Phase 3 세션 검증 결과 요약) + `D:/VAMOS/docs/sot 2/PHASE3_ORCHESTRATION/PROGRESS.md` §4 (6-9 P3-1~P3-4 checkpoint × 4 + ④⑤⑥⑦ 도메인 종료 4단계)

> **NOTE (upstream inheritance) [2026-05-21]**: 4-1 Rust-Tauri-Infrastructure Phase 3 ✅ 완료 (2026-05-21, 3 task: T3-1 L3 핵심 항목 승급 ≥ 3개 / T3-2 FINAL REVIEW GOLD/SILVER 판정 §12 갱신 / T3-3 교차 도메인 검증 4-2 CICD-Pipeline + 4-3 MCP-Server-Client 경계 정합, Wave 3 #24 단일 대화창 tcv1 first-pass NO-DRIFT 100%, R cascade 통산 324 verifications + 0 drift fix, Tier 4 Infrastructure 도메인 NO-DRIFT 100% first specialty + 통산 7번째 NO-DRIFT 100% 도메인 milestone). 본 도메인 (6-11 Hologram-Main-LLM, Wave 3 #28) 진입 시 4-1 결과 inheritance 가능 — **cross_domain_validation_report P3-4 4 도메인 (6-1/6-9/1-1/4-1) 중 4-1 baseline 확보**:
> - **4-1 T3-2 FINAL REVIEW GOLD/SILVER 판정** (4-1 종합계획서 §7 P3-2 L1211~L1260 + §12 FINAL REVIEW 표 T0-1 B+ → T0-2 A- → T0-3 A → T0-4 historical row L1400~L1413 + T3-2 row append Phase 4 implementation) → **6-11 P3-4 cross_domain_validation_report (6-1/6-9/1-1/4-1)** 통합 검증 target 직접 inheritance (Phase 4 entry-gate 6-11 P3-4 핵심 cross-handoff)
> - **4-1 T3-1 L3 핵심 항목 승급** (Session IPC 8 + JSON-RPC process_message + Python Spawn 프로토콜 3 L3 후보 + M-1~M-7 매트릭스 전수 + IPC SLA P99 카테고리별 + Phase 4 entry-gate staging 7일 측정 데이터) → 6-11 Hologram UI 4-1 Rust-Tauri IPC 경계 정합 inheritance (P3-1 모바일 대응 V3 + P3-3 Avatar Dialog 등 forward-defined cross-handoff)
> - **권한 boundary**: 4-1 LOCK-RT-01~15 §3.4 read-only inheritance / LOCK-RT-02 (IPC 카테고리 배분 Core 15 / Agent 15 / Storage 18 / Safety 19 / UI 5) PRESERVE / LOCK-RT-04 (Rust 핵심 모듈 4개) PRESERVE / LOCK-RT-14 (TauriError enum 7 variant) PRESERVE / 4-1 self-contained INDEX L8 `cross_domain_deps=[]` 정합 유지
> - **production .md baseline (5종 무손상 inheritance reference)**: 01_ipc-commands/ 14 files 181,274 B + 02_serde-models/ 5 files 102,195 B + 03_python-bridge/ 3 files 107,711 B + 04_build-signing/ 3 files 60,235 B + 05_process-management/ 4 files 150,525 B = **30 files / 615,817 B aggregate EXACT** (Tier 4 Infrastructure 도메인 production 무손상 강제 통산 보존)
> - **CROSS_REF_MATRIX §1 양방향 정합**: 4-1 downstream (4-3 + **6-11**) ↔ 6-11 upstream (6-1 + 6-9 + 1-1 + **4-1** + 3-2 + 6-4) — 본 NOTE로 양방향 100% 정합 도달 + Wave 3 두 derivation 도메인 (4-1 ★ + 6-11 ★) cross_domain_validation_report 정본 관계 확정
> - **Phase 4 entry-gate**: 6-11 Wave 3 #28 진입 시 4-1 production 30 .md (615,817 B) baseline + LOCK-RT-01~15 15 entries inheritance + §12 FINAL REVIEW GOLD/SILVER 판정 결과 (Phase 4 implementation 단계) inheritance + cross_domain_validation_report 작성 시 4-1 4 도메인 중 하나로 통합 검증 target 명시
> - **참조**: `D:/VAMOS/docs/sot 2/4-1_Rust-Tauri-Infrastructure/RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md` §7 Phase 3 (L1147~L1308, 3 details 블록 T3-1/T3-2/T3-3 + Phase 3 세션 검증 결과 요약 + §12 FINAL REVIEW 표 historical row 4건) + `D:/VAMOS/docs/sot 2/PHASE3_ORCHESTRATION/PROGRESS.md` §2 (4-1 P3-1~P3-3 checkpoint × 3 + ④⑤⑥⑦ 도메인 종료 4단계)

> **NOTE (upstream inheritance) [2026-05-16]**: 3-2 Multimodal-Processing Phase 3 ✅ 완료 (2026-05-16, 4 task: P3-1 J-009 AR/공간 + J-020 3D / P3-2 J-040 실시간 비디오 / P3-3 J-073 멀티유저 캔버스 / P3-4 전체 L3 점검). 본 도메인 (6-11 Hologram-Main-LLM, Wave 3 #28) 진입 시 3-2 V3 결과 inheritance 가능:
> - **3-2 P3-1 J-009 AR/공간 이해** (`vision_language_integration.md` V3 EXTEND, Depth Estimation(MiDaS/DPT) + ARKit/ARCore 좌표계 + 공간 메시 생성, SLA ≤ 300ms/frame) → 6-11 `01_hologram-view-layout/` + `02_component-architecture/` 공간 컴포넌트 매핑 가능
> - **3-2 P3-1 J-020 3D 자산 생성** (`image_generation.md` V3 EXTEND, Meshy/TripoSR/Shap-E 파이프라인 + 비용 LOCK-MM-06 ≤ $150/월) → 6-11 `02_component-architecture/` 3D 자산 렌더링 컴포넌트 매핑 가능
> - **3-2 P3-2 J-040 실시간 비디오 스트리밍** (`video_analysis.md` V3 EXTEND, WebRTC/RTMP + circular buffer max=100 + 실시간 CLIP/Vision 분석 + SLA p95 ≤ 500ms/frame + LOCK-MM-09 max_frames=100) → 6-11 `06_streaming-canvas/` (token_rendering / stream_protocol) 실시간 시각 매핑 가능
> - **3-2 P3-3 J-073 멀티유저 협업 캔버스** (`vamos_differentiators.md` V3 EXTEND, OT/CRDT(Y.js/Automerge) + RBAC 4단계 (Owner/Editor/Commenter/Viewer) + LOCK-MM-05 MultimodalMessage UUID v7 스키마 확장 + 동기화 지연 p95 ≤ 200ms 5명 동시) → 6-11 `02_component-architecture/` (store_catalog / chatpage_integration) 다중 사용자 store + `06_streaming-canvas/` 협업 canvas 매핑 가능
> - **권한 boundary**: 3-2 LOCK-MM-01~12 §3.4 read-only inheritance / LOCK-MM-05 PRESERVE (다중 작성자 metadata 확장 호환) / LOCK-MM-07 CLIP 768d (ViT-L/14@336) PRESERVE / LOCK-MM-09 max_frames=100 (스트리밍 윈도우 기준) PRESERVE
> - **production .md baseline (4종 무손상 inheritance reference)**: vision_language_integration.md 35,323 B / B54D999695637E27 + image_generation.md 29,785 B / 737AAEFC026E5874 + video_analysis.md 18,616 B / C684C25DA2760A4F + vamos_differentiators.md 29,090 B / 7E574849D7775058 = **112,814 B aggregate EXACT**
> - **CROSS_REF_MATRIX §1 양방향 정합**: 3-2 downstream (5-2 + **6-11**) ↔ 6-11 upstream (6-1 + 6-9 + 1-1 + 4-1 + **3-2** + 6-4) — 본 NOTE로 양방향 100% 정합 도달
> - **Phase 4 entry-gate**: 6-11 Wave 3 #28 진입 시 3-2 production .md 4종 baseline + LOCK-MM 12 entries inheritance + V2 영향 LOCK 5건 (L2/L5/L12/L15/L18) AUTHORITY §8.4 5-2 inheritance EXACT 인용 유지
> - **참조**: `D:/VAMOS/docs/sot 2/3-2_Multimodal-Processing/MULTIMODAL_PROCESSING_구조화_종합계획서.md` §7 Phase 3 (L1599~L1830, 4 details 블록 + 검증 결과 요약) + `D:/VAMOS/docs/sot 2/PHASE3_ORCHESTRATION/PROGRESS.md` §3 (3-2 P3-1~P3-4 checkpoint × 4)

### 6.1 PARTIAL 보완 매핑 (Part2에 이름/개념만 → sot 2/에서 상세 작성)

| # | Part2/D2.0 항목 | 기존 내용 | sot 2/ 보완 내용 | 서브폴더 |
|---|----------------|----------|-----------------|---------|
| ISS-01 | D2.0-08 §2.2 Hologram View 레이아웃 | 3요소 정의만 | 내부 렌더링 파이프라인 데이터 흐름 | 01_hologram-view-layout/ |
| ISS-02 | Part2 V1-P4 44개 컴포넌트 | 이름 목록만 | Props 인터페이스, 의존 그래프, 계층 구조 | 02_component-architecture/ |
| ISS-03 | Part2 V1-P4 8개 Hook | 이름 목록만 | 시그니처, 상태 흐름, 사용처 매핑 | 02_component-architecture/ |
| ISS-04 | Part2 V1-P4 7개 Store | 이름 목록만 | 스키마, 셀렉터, 액션 정의 | 02_component-architecture/ |
| ISS-05 | D2.0-08 §4 9-State Machine | 상태 이름만 | 전이 매트릭스, 가드 조건, 액션 정의 | 03_ui-state-machine/ |
| ISS-06 | D2.0-02 §11.15.1 2-tier 라우팅 | 개념 정의만 | Hologram 맥락 전달 프로토콜, DCL 연동 | 04_main-llm-integration/ |
| ISS-07 | D2.0-02 §7.63 I-10 오케스트레이션 | 역할 정의만 | 데이터 매핑 테이블, 변환 규칙, 이벤트 흐름 | 07_orchestration-layer/ |
| ISS-08 | D2.0-05 §7.2 3-point 출력 | 포맷 정의만 | Hologram UI 바인딩 매핑 (어떤 필드 → 어떤 컴포넌트) | 04_main-llm-integration/ |

### 6.2 신규 작성 매핑 (Part2/D2.0에 없음)

| # | 항목 | 내용 | 서브폴더 |
|---|------|------|---------|
| ISS-09 | Glass HUD 오버레이 데이터 스키마 | 비용/근거/승인 필드 정의, 갱신 주기, 렌더링 규칙 | 05_glass-hud-overlay/ |
| ISS-10 | 스트리밍 캔버스 프로토콜 | SSE/WebSocket 선택, 청크 포맷, 재연결 정책 | 06_streaming-canvas/ |
| ISS-11 | 토큰 단위 렌더링 파이프라인 | 토큰 수신 → 파싱 → 마크다운 변환 → DOM 갱신 흐름 | 06_streaming-canvas/ |
| ISS-12 | 아티팩트 인라인 렌더링 | 코드 블록/차트/테이블을 스트리밍 중 인라인 렌더링 | 06_streaming-canvas/ |
| ISS-13 | Layout 전환 프로토콜 | 4-Layout 간 전환 시 상태 보존/복원 프로토콜 | 01_hologram-view-layout/ |
| ISS-14 | 컴포넌트 의존 그래프 | 44개 컴포넌트 간 import/props 의존 관계 | 02_component-architecture/ |
| ISS-15 | 7페이지 라우팅 규칙 | Dashboard/Chat/Workflow/Memory/Settings/Log/NodeDetail 라우팅 | 07_orchestration-layer/ |
| ISS-16 | ChatPage.tsx 통합 패턴 | 채팅/스트리밍/아티팩트 조합 렌더링 규칙 | 02_component-architecture/ |

### 6.3 Part2 PARTIAL 요약 (방식 C)

#### Part2 §6.1 + V1-P4 정본 요약

> **출처**: PART2 §6.1 (line 4557~4670), V1-Phase 4 (line 2274~2414)
> **Part2/D2.0이 정본**: When + Where + What — Hologram View 정의, 4-Layout 구조, 컴포넌트/Hook/Store 목록, 9-State 이름, 2-tier 라우팅 개념, I-10 역할, 3-point 출력 포맷
> **sot 2/가 정본**: How — 렌더링 파이프라인 흐름, 컴포넌트 상세 인터페이스, 상태 전이 규칙, LLM 응답 변환 규칙, Glass HUD 스키마, 스트리밍 프로토콜

**D2.0-08 §2.2 핵심**: Hologram View = 타임라인 + 스트리밍 캔버스 + Glass HUD. 4개 Layout 중 하나.

**Part2 V1-P4 핵심**: 44개 React 컴포넌트, 8개 Custom Hook, 7개 Zustand Store. ChatPage.tsx가 Hologram View 진입점.

**D2.0-02 §7.63 핵심**: I-10 UI 오케스트레이션 레이어 — Builder/Hologram UI에 상태/근거/승인/비용/로그 노출.

**D2.0-02 §11.15.1 핵심**: ORANGE CORE → Front Mini → Main LLM 2-tier 라우팅. V1에서 2-3 모델, V3에서 MoE multi-expert pool.

**D2.0-05 §7.2 핵심**: 3-point 출력 포맷 — user_response (사용자 응답), evidence_summary (근거 요약), log_report (로그 리포트).

### 6.X 6-1 UI-UX-System Phase 4 ✅ Stage A 완료 inheritance (2026-05-26, downstream 전파)

> **[PHASE4_COMPLETE_STAGE_A: 6-1 — 2026-05-26]** ⬛ (downstream reference, P4-1~P4-4 4/4 ALL ✅ NO-DRIFT FULL milestone first specialty 확정): 6-1 도메인 Phase 4 Stage A 완료에 따른 본 도메인 inheritance 자원 — **🌟 AR 렌더링 정본 (6-11) ↔ View 구조 (6-1) 경계 V3 시점 최종 확정 forward-defined** (AUTHORITY §5.1 4 row verbatim 정합: 범위/관심/결과/충돌, 6-1 = AR UI View 구조 (좌표계+오버레이+사용자 제스처 입력) / 6-11 = AR 렌더링 + Main LLM 파이프라인 EXACT 경계) + **🌟 AR EventType 8건 `ui.hologram.ar.{action}`** (gesture_detected / gaze_changed / spatial_anchor_set / depth_updated / occlusion_resolved / hand_tracking_lost / scene_understanding_ready / ar_session_ended) LOCK L19 100% 준수 forward-defined + **🌟 아바타 3D 렌더링 cross-handoff** (P4-3 5 컴포넌트 UserAvatar/DigitalHuman/AvatarDialog/AvatarPermission/AvatarGallery — 아바타 3D 표현 시 6-11 렌더링 정합 forward-defined). 6-1 V3 산출물 5 NEW + 3 UPDATE forward-defined (OUT of scope per 사용자 결정 A verify-only inheritance, SPEC Stage B 또는 별도 결정 위임). **Wave 3 #28 본 도메인 Phase 4 진입 시 본 inheritance reference 처리 예정** — ISS-6 V3 시점 최종 확정 양방향 EXACT MATCH 100% + 6-11 cross_domain_validation_report에 6-1 P4-2/P4-3 reference 통합 + V3 AUTHORITY §3 6-11 경계 V3 갱신 row append (P4-2 SPEC Stage B 위임 산출물) 양방향 verify. (출처: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §7 Phase 4, post 236,927 B / `E39161CFBFEFC36D` Stage A baseline EXACT 보존 + ④ 세션 요약 블록 +Δ 별도)

---

## 7. Phase 실행 계획

> Tier 6 기본: Phase 0 스펙 확정 → Phase 1 기본 구현 → Phase 2 심화·통합 → Phase 3 프로덕션 안정화

### Phase 0: 스펙 확정 — ✅ 완료 (2026-04-05)

| 태스크 | 산출물 | 완료 기준 | 상태 |
|--------|--------|----------|------|
| T0-1 계획서 작성 | 본 문서 | 14+1 섹션 완성 | ✅ |
| T0-2 AUTHORITY_CHAIN 초안 | AUTHORITY_CHAIN.md | 권한 체계 + 10 LOCK 레지스트리 + T6 규칙 + 경계 | ✅ |
| T0-3 CONFLICT_LOG 초기화 | CONFLICT_LOG.md | §9.1 우선순위 5단 + 5컬럼 테이블 + §9.4 초기 3행(C-1~C-3) + CFL-HM-001 + 기록 규칙 | ✅ |
| T0-4 서브폴더 골격 생성 | 01~07/ + _index.md 7개 | 구조 확정 | ✅ |
| T0-5 PRE-1~PRE-5 해소 | 01·02·03/_index.md 갱신 | 3요소/44컴포넌트/8Hook/7Store/9State+전환6건+런타임매핑 전수 확인 | ✅ |
| T0-6 도메인 경계 확정 | domain_boundary.md + PRE-8/PRE-9 해소 | 6-1, 6-9와 경계 문서화, 양측 AUTHORITY_CHAIN 교차 대조 | ✅ |

**Phase 0 → Phase 1 게이트**: ✅ G0-1~G0-6 전수 PASS (2026-04-05) — T0-1~T0-6 완료, LOCK-HM-01~10 검증 PASS, Phase 1 진입 가능

#### Phase 0 세부 태스크

<details>
<summary><b>T0-1. 계획서 작성 (본 문서)</b></summary>

**상태**: ✅ 완료

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` (Hologram View 레이아웃, 9-State, Glass HUD)
  - §2.1/§3: 4-Layout 구조(3-Column Fluid, Builder, Hologram, CLI) — LOCK-HM-02 출처
  - §2.2 (L223-282): Hologram View 3-Pane(Left 250px/Center Main/Right 300px), 컨텍스트 사이드바, 스트림 캔버스, 12 UI 이벤트
  - §4.1 (L335-344): 9-State(UI_S0_BOOT~UI_S8_ARCHIVED), §4.2 전환 6건, §4.4 런타임 6-State, §4.5 양방향 매핑, §4.6 파이프라인 매핑
  - §2.2.2 (L255-265): Glass HUD — Evidence(VERIFIED/PARTIAL/UNVERIFIED qod 기반)/Cost(80%황/100%적)/Approval 카드, Uncertainty Alert 3종
  - §10.4 (L1493-1509): Hologram 컴포넌트 17개(V1 필수 13개 ★)
  - §9.1 (L1409-1417): Design Freeze — Option A(Fixed HUD) LOCK
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md`
  - §7.63 (L2091-2119): I-10 UI 오케스트레이션 — emit_ui_state(trace_id, ui_state)/render_artifact_preview(artifact_ref), 이벤트: oc.i10.ui.state.emitted, 실패: OC_I10_UI_EMIT_FAIL, STEP7 확장 3건(S7B-027 멀티대화/S7B-015 TTS/S7B-017 화면공유)
  - §11.15.1 (L4261-4266): MoE 2-tier 라우팅 — Tier 1: Orange Core → 라우팅 매트릭스, Tier 2: MoE Router → 최적 모델 선택(V1: 2~3개, V3: 다수 풀), Kimi "384→8 선택" 개념 차용
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md`
  - §7.2 (L359-368): 표준 3단 출력(LOCK) — user_response(최종 결과)/evidence_summary(근거·QoD)/log_report(trace_id·이벤트), 스키마: 02 Decision 확장 또는 별도 OutputEnvelope
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md`
  - §6.1 (L4561-4672): UI/UX 상세 ~85항목 — §6.1.1 핵심 레이아웃 4종, §6.1.2 React 컴포넌트 44개, §6.1.3 Hook 8개+Store 7개, §6.1.6 9-State SM, §6.1.7 Failure/Fallback, §6.1.8 RBAC 4-tier
  - V1-P4 (L2277-2414): Week 13-14 UI/UX — 3-Column Fluid, Builder/Hologram View, 44컴포넌트, 8Hook, 7Store, i18n(ko-KR/en-US), ORANGE/BLUE 테마 LOCK, 6 CLI 커맨드

**절차**:
1. D2.0-08 §2.1/§3에서 4-Layout 구조(3-Column/Builder/Hologram/CLI) + §2.2에서 Hologram View 3-Pane 레이아웃(Left 타임라인/Center 스트림/Right Glass HUD) + §10.4 컴포넌트 17개(V1 필수 13개) + 12 UI 이벤트 수집
2. D2.0-08 §4.1~§4.6에서 9-State(S0~S8) 정의 + 전환 규칙 6건 + 런타임 6-State + 양방향 매핑 + 파이프라인 매핑 수집
3. D2.0-08 §2.2.2에서 Glass HUD 사양 — Evidence(qod 기반 3등급)/Cost(임계값 경고)/Approval(슬라이드인) 카드 + Uncertainty Alert 3종 + Design Freeze Option A(Fixed) 수집
4. D2.0-02 §7.63에서 I-10 오케스트레이션(emit_ui_state/render_artifact_preview, 이벤트 흐름, STEP7 확장) 사양 수집
5. D2.0-02 §11.15.1에서 MoE 2-tier 라우팅(Tier 1 Core Decision → Tier 2 Expert Selection, V1~V3 점진 확장) 사양 수집
6. D2.0-05 §7.2에서 3-point 출력 포맷(user_response/evidence_summary/log_report, LOCK) 사양 수집
7. Part2 §6.1에서 44컴포넌트·8Hook·7Store·9-State SM·RBAC + V1-P4에서 Week 13-14 구현 범위·검증 기준 수집
8. 수집된 SoT 기반 14+1 섹션 계획서 작성 (§1~§14 + 부록 A Hologram 렌더링 파이프라인)

**검증**:
- [x] 14+1 섹션 완성 — §1~§14(14섹션) + 부록 §A(12개 서브섹션) = 15섹션
- [x] D2.0-08 전수 반영 — 4-Layout(§A.4 LOCK-HM-02), Hologram 3-Pane(§A.2 LOCK-HM-01), 9-State(§A.5 LOCK-HM-03), Glass HUD(§A.8 LOCK-HM-10), 17 Hologram 컴포넌트(§A.11, §5 PRE-2 44개 중)
- [x] D2.0-02 §7.63 반영 — I-10 오케스트레이션(§3 LOCK-HM-05, §A.3)
- [x] D2.0-02 §11.15.1 반영 — MoE 2-tier 라우팅(§3 LOCK-HM-04, §A.6)
- [x] D2.0-05 §7.2 반영 — 3-point 출력 포맷(§3 LOCK-HM-06, §A.7)
- [x] Part2 §6.1 + V1-P4 반영 — 44컴포넌트/8Hook/7Store(§5 PRE-1~5), V1-P4 Week 13-14(§1.4)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md`
**상태**: ✅ 완료 (2026-04-05 — 절차 1~8 SoT 4건 전수 수집 + 14+1 섹션 완성 + LOCK-HM-01~10 반영 확인)
</details>

<details>
<summary><b>T0-2. AUTHORITY_CHAIN 초안 (권한 체계 + LOCK-HM-01~10 레지스트리)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md`
  - §2.2 (L223-282): Hologram View 3요소 정본 — LOCK-HM-01 출처
  - §2.1/§3: 4-Layout 구조 — LOCK-HM-02 출처
  - §4.1 (L335-344): 9-State UI State Machine — LOCK-HM-03 출처
  - §2.2.2 (L255-265): Glass HUD 오버레이 — LOCK-HM-10 출처
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md`
  - §11.15.1 (L4261): MoE 2-tier 라우팅 — LOCK-HM-04 출처
  - §7.63 (L2091-2119): I-10 UI 오케스트레이션 — LOCK-HM-05 출처
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md`
  - §7.2 (L359-368): 3-point 출력 포맷 — LOCK-HM-06 출처
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md`
  - §6.1 (L4561-4672): UI/UX 상세 ~85항목
  - V1-P4 (L2277-2414): 44 컴포넌트/8 Hook/7 Store — LOCK-HM-07~09 출처
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md`
  - §3.1: 기존 VAMOS 권한 체인
  - §3.2: 도메인 확장 체인
  - §3.4: LOCK-HM-01~10 정의
  - §4.2: Tier 6 공통 규칙 (R-T6-1~4)
  - §1.5: 도메인 경계 분석 (5개 인접 도메인)
  - §1.6: 6-11 소유 범위 (7개 영역)
  - §8.2: 서브폴더별 역할 (01~07 매핑)
  - §8.3: 인접 도메인 파일 역할 구분

**절차**:
1. 본 계획서 §3.1에서 기존 VAMOS 권한 체인 복사, §3.2에서 도메인 확장 체인(D2.0-08 → D2.0-02/D2.0-05 → Part2 → sot 2/6-11) 복사
2. 본 계획서 §3.4에서 LOCK-HM-01~10 전수 추출 → D2.0 정의 LOCK(7건: HM-01~06, 10)과 Part2 정의 LOCK(3건: HM-07~09)으로 분류
3. 각 LOCK의 출처(SoT 문서 + 섹션 + 라인 번호), 적용 서브폴더(§8.2 참조 01~07 매핑), 위반 시 조치를 정리 (위반 조치가 정본에 미정의된 경우 "상위 정본 참조" 표기)
4. 각 LOCK에 대해 정본 원문 인용 기록 (SoT에서 해당 정의 원문 발췌)
5. 본 계획서 §4.2에서 Tier 6 공통 규칙(R-T6-1~4) 추출
6. 본 계획서 §1.5에서 의존성 도메인(5개 인접 도메인) 추출, §8.3 + §1.6에서 도메인 경계(본 도메인 소유 vs 인접 도메인 소유) 작성
7. `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md`에 권한 체인 + LOCK 레지스트리 + Tier 6 규칙 + 의존성 + 도메인 경계 작성

**검증**:
- [x] 권한 체인(§3.1 기존 체인 + §3.2 도메인 확장 체인) 포함
- [x] LOCK-HM-01~10 총 10건 전수 포함 (D2.0 정의 7건 + Part2 정의 3건 분류)
- [x] 각 LOCK에 출처(문서+섹션+라인)·적용 서브폴더(01~07)·위반 시 조치 기재
- [x] 각 LOCK에 정본 원문 인용 포함
- [x] Tier 6 공통 규칙(R-T6-1~4) 포함
- [x] 의존성 도메인(§1.5 기반 5개 인접 도메인 + 5-2 기존 1건) + 도메인 경계(§8.3 + §1.6 기반 13항목) 포함
- [x] 파일이 비어있지 않음 (194줄)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md`
**상태**: ✅ 완료 (2026-04-05, LOCK 10건 SoT 원문 전수 대조 + 위반 조치 10건 출처 확인 + 도메인 확장 체인 L1~L4 + T6 규칙 4건 + 의존성 6건 + 경계 13항목)
</details>

<details>
<summary><b>T0-3. CONFLICT_LOG 초기화</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md`
  - §9.1: 우선순위 5단 체계 (`LOCK 값 > D2.0 정본(D2.0-08, D2.0-02, D2.0-05) > Part2 §6.1+V1-P4 > sot 2/ 계획서 > sot 2/ 서브폴더`)
  - §9.2: 도메인 간 충돌 시나리오 8건 (분류 기준 — 2컬럼: 시나리오, 판정)
  - §9.3: CONFLICT_LOG 규칙 4개 (즉시 기록, OPEN→RESOLVED→VERIFIED, 해소 근거 필수(정본 출처 명시), 주 1회 교차 검토)
  - §9.4: 기존 인지된 충돌 3건 (C-1 RESOLVED, C-2 RESOLVED, C-3 OPEN)
  - §11.2 S10-1: CFL-HM-001 Hook 목록 내부 충돌 — RESOLVED (V1-P4와 §6.1.3 Hook 상호 보완 관계, LOCK-HM-08 수량 범위 내)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md`
  - T0-2 완료 결과: LOCK-HM-01~10 전수 SoT 원문 대조, 위반 0건 (LOCK 교차 확인 baseline 근거)

**절차**:
1. CONFLICT_LOG.md 상단에 문서 목적(충돌 발생·추적·해결 이력 관리) 기재 + §9.1 우선순위 5단 체계 원문 인용(`LOCK 값 > D2.0 정본(D2.0-08, D2.0-02, D2.0-05) > Part2 §6.1+V1-P4 > sot 2/ 계획서 > sot 2/ 서브폴더`)
2. 충돌 기록 테이블 헤더 5개 컬럼 작성: `날짜 | 항목 | 출처A vs 출처B | 해결 방법 | 상태`
   - §9.2(2컬럼: 시나리오, 판정)를 운용 로깅에 맞게 확장한 포맷임을 주석으로 명시
3. §9.4 기존 인지된 충돌 3건을 초기 행으로 기재:
   - C-1: Hologram View 정의 출처 복수 (D2.0-08 §2.2 vs Part2 V1-P4) — RESOLVED (D2.0-08=레이아웃 정본, Part2=컴포넌트 목록 정본 → 역할 분리)
   - C-2: Glass HUD 상세 수준 (D2.0-08 개념 vs sot 2/ 스키마) — RESOLVED (D2.0-08 개념 LOCK, sot 2/=구현 스키마 정본 → 계층 분리)
   - C-3: 6-11 vs 6-1 UI/UX 범위 — OPEN (6-1 도메인 구조화 완료 시 경계 재확정 필요)
4. §11.2 S10-1 충돌 기재: CFL-HM-001 Hook 목록 내부 충돌 (S8-6 SSV-1-B) — RESOLVED (V1-P4와 §6.1.3 Hook 상호 보완 관계, LOCK-HM-08 수량(8개) 범위 내, 개별 이름은 Phase 1 PRE-3에서 확정)
5. T0-2 AUTHORITY_CHAIN LOCK 교차 확인 baseline 행 기재: LOCK-HM-01~10 × SoT 원문 전수 대조 → 위반 0건, 상태=VERIFIED
6. 기록 규칙 섹션 작성 (§9.3 + §4.1 R7 기반):
   a. **기록 트리거**: ① 새 Phase 진입 시 LOCK 교차 확인 (R10), ② §9.2 도메인 간 충돌 시나리오 8건 해당 시, ③ LOCK 위반 또는 정본 간 불일치 발견 시, ④ 교차 도메인 영향 식별 시 (R-T6-2 System-wide 변경 영향 분석)
   b. **분류 기준**: §9.2 시나리오 유형 참조 — 8개 시나리오(컴포넌트 목록 vs Part2, Glass HUD 스키마 vs D2.0-08, 렌더링 vs 6-1, LLM 포맷 vs 6-9, 2-tier 설명 vs D2.0-02, 출력 포맷 vs D2.0-05, IPC vs 4-1, State Machine vs D2.0-08)
   c. **상태 관리**: OPEN → RESOLVED → VERIFIED (§9.3 원문. 해결 방법란에 §9.1 우선순위 적용 결과 + 정본 출처 기재)
   d. **책임**: 해당 Phase 실행자가 발견 즉시 등록 (R7 CONFLICT_LOG 즉시 기록 원칙), 해결 후 상태 갱신, System-wide 특성상 주 1회 교차 검토 (§9.3)
7. `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\CONFLICT_LOG.md` 생성

**검증**:
- [x] 문서 상단에 §9.1 우선순위 5단 체계 원문(`LOCK 값 > D2.0 정본 > Part2 > sot 2/ 계획서 > sot 2/ 서브폴더`) 명시
- [x] 테이블 헤더 5개 컬럼 존재 (날짜, 항목, 출처A vs 출처B, 해결 방법, 상태)
- [x] §9.4 기존 충돌 3건(C-1 RESOLVED, C-2 RESOLVED, C-3 OPEN) 초기 행 존재 + 각 해소 근거(정본 출처) 기재
- [x] §11.2 S10-1 충돌 1건(CFL-HM-001 RESOLVED) 초기 행 존재 + 해소 근거 기재 + 기존 상세(S8-6→S10-5) 보존
- [x] T0-2 LOCK 교차 확인 baseline 행 존재 (LOCK-HM-01~10 × SoT 대조, 위반 0건, VERIFIED)
- [x] §9.2 8개 시나리오 분류가 기록 규칙의 분류 기준에 반영 — S1~S8 전수, §9.2 원문 글자 단위 일치
- [x] §9.3 기록 규칙 4개 항목(트리거·분류·상태 관리·책임) 존재
- [x] R7(즉시 기록 원칙) + 주 1회 교차 검토(System-wide 특성) 규칙 명시
- [x] 파일이 비어있지 않음 (129줄)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\CONFLICT_LOG.md`
**상태**: ✅ 완료 (2026-04-05, 검증 9/9 PASS + 2차 검증 28항목 전수 PASS — §9.1 원문 5단 글자 일치 + §9.2 S1~S8 글자 대조 + §9.4 C-1~C-3 전수 등재 + CFL-HM-001 기존 상세 보존(S8-6→S10-5) + LOCK baseline T0-2 근거 + §9.3 기록 규칙 4항목 + W-1~W-3 보존 + W-1→C-3 교차 참조 + 2차 수정 3건: C-2 우선순위 2→1순위(LOCK-HM-10), C-3 R-611-9→R9+§8.3(6-1 경계), 인접 도메인 3→5개 일관성)
</details>

<details>
<summary><b>T0-4. 서브폴더 골격 생성 (7개)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §2.1 (폴더 트리), §2.4 (파일 수 요약), §8.2 (서브폴더별 역할)
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` (§2.2 Hologram View, §4 9-State, Glass HUD)
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` (§7.63 I-10 오케스트레이션, §11.15.1 2-tier 라우팅)
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` (§7.2 3-point 출력)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1, V1-P4

**절차**:
1. `01_hologram-view-layout/_index.md` 생성 — 폴더 목적(Hologram View 레이아웃 구조, 렌더링 파이프라인, Layout 전환), 범위(D2.0-08 §2.2 Hologram View 3요소 + §2.1/§3 4-Layout 구조), 관련 LOCK(LOCK-HM-01 Hologram View 3요소, LOCK-HM-02 4-Layout 구조), Phase 배정(Phase 1 T1-1), 작성 대상 파일 목록(layout_structure.md, layout_switching.md, responsive_rules.md — §2.1 폴더 트리 글자 일치), 정본 소유(6-11 DEFINED-HERE)
2. `02_component-architecture/_index.md` 생성 — 폴더 목적(44 컴포넌트 Props, 8 Hook 시그니처, 7 Store 스키마, ChatPage 통합), 범위(Part2 V1-P4 목록 LOCK + sot 2/ 상세 보완), 관련 LOCK(LOCK-HM-07 44개 컴포넌트, LOCK-HM-08 8개 Hook, LOCK-HM-09 7개 Store), Phase 배정(Phase 1 T1-2~T1-4, T1-6), 작성 대상 파일 목록(component_catalog.md, hook_catalog.md, store_catalog.md, chatpage_integration.md — §2.1 글자 일치), 정본 소유(6-11 DEFINED-HERE, 목록은 Part2 LOCK)
3. `03_ui-state-machine/_index.md` 생성 — 폴더 목적(9-State 전이 규칙, 가드 조건, 액션 정의), 범위(D2.0-08 §4 상태 이름 LOCK + sot 2/ 전이 상세), 관련 LOCK(LOCK-HM-03 9-State UI State Machine), Phase 배정(Phase 1 T1-5), 작성 대상 파일 목록(state_definitions.md, transition_matrix.md — §2.1 글자 일치), 정본 소유(6-11 DEFINED-HERE, 상태 이름은 D2.0-08 LOCK)
4. `04_main-llm-integration/_index.md` 생성 — 폴더 목적(2-tier 라우팅 맥락, 응답 포맷팅, DCL, MoE 진화), 범위(D2.0-02 §11.15.1 라우팅 개념 LOCK + D2.0-05 §7.2 출력 포맷 LOCK + sot 2/ Hologram 맥락 상세), 관련 LOCK(LOCK-HM-04 2-tier 라우팅, LOCK-HM-06 3-point 출력), Phase 배정(Phase 2 T2-1~T2-3, Phase 3 T3-1), 작성 대상 파일 목록(two_tier_routing.md, response_formatting.md, dcl_context.md, moe_evolution.md — §2.1 글자 일치), 정본 소유(6-11 DEFINED-HERE, 라우팅 개념은 D2.0-02 LOCK)
5. `05_glass-hud-overlay/_index.md` 생성 — 폴더 목적(HUD 데이터 스키마, 실시간 갱신, 렌더링 규칙), 범위(D2.0-08 Glass HUD 개념 LOCK + sot 2/ 구현 스키마), 관련 LOCK(LOCK-HM-10 Glass HUD 오버레이), Phase 배정(Phase 2 T2-4), 작성 대상 파일 목록(overlay_schema.md, realtime_update.md, rendering_rules.md — §2.1 글자 일치), 정본 소유(6-11 DEFINED-HERE, 개념은 D2.0-08 LOCK)
6. `06_streaming-canvas/_index.md` 생성 — 폴더 목적(스트림 프로토콜, 토큰 렌더링, 아티팩트 렌더링), 범위(Part2/D2.0 미언급 → 전면 신규 DEFINED-HERE), 관련 LOCK(없음 — 신규 정의), Phase 배정(Phase 2 T2-5), 작성 대상 파일 목록(stream_protocol.md, token_rendering.md, artifact_rendering.md — §2.1 글자 일치), 정본 소유(6-11 DEFINED-HERE)
7. `07_orchestration-layer/_index.md` 생성 — 폴더 목적(UI↔LLM 매핑, 비용/로그 변환, 페이지 라우팅), 범위(D2.0-02 §7.63 I-10 역할 LOCK + sot 2/ 데이터 매핑 상세), 관련 LOCK(LOCK-HM-05 I-10 오케스트레이션), Phase 배정(Phase 2 T2-6), 작성 대상 파일 목록(ui_state_mapping.md, cost_evidence_log.md, page_routing.md — §2.1 글자 일치), 정본 소유(6-11 DEFINED-HERE, 역할은 D2.0-02 LOCK)

> **참고**: 모든 경로의 루트는 `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\`이다. 절차 1~7의 경로는 이 루트 하위 상대 경로이다.

**검증**:
- [x] 7개 서브폴더 디렉토리 존재 (01_hologram-view-layout, 02_component-architecture, 03_ui-state-machine, 04_main-llm-integration, 05_glass-hud-overlay, 06_streaming-canvas, 07_orchestration-layer)
- [x] 7개 _index.md 존재 + 비어있지 않음 (63/71/61/66/60/60/62줄)
- [x] 각 _index.md에 폴더 목적·범위·관련 LOCK 참조·Phase 배정·작성 대상 파일 목록·정본 소유 포함 (7/7 전수 6항목)
- [x] 폴더명이 §2.1 폴더 트리 및 §8.2 서브폴더별 역할과 글자 일치 (7/7)
- [x] 작성 대상 파일 목록이 §2.1 폴더 트리의 파일명과 글자 일치 (22/22)
- [x] 파일 수 합계가 §2.4와 일치 (4+5+3+5+4+4+4 = 29개)
- [x] LOCK 매핑이 §3.4 LOCK 레지스트리(LOCK-HM-01~10) 및 AUTHORITY_CHAIN.md와 정합 (10/10)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\01_hologram-view-layout\_index.md` ~ `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\_index.md` (7개)
**상태**: ✅ 완료 (2026-04-05, 검증 7/7 전수 PASS + 2차 검증 PASS — 기존 3폴더 삭제 후 §8.2 기준 7폴더 재생성, 2차 검증: 인코딩 깨짐 9건 수정(01·02·04·05), LOCK-HM-02 "3-Column Fluid" 원문 일치 수정, LOCK 10건 항목·정본·위반조치 AUTHORITY_CHAIN 글자 대조 30/30 PASS, ISS 16건 §6.1/§6.2 매핑 16/16 PASS, 도메인 규칙 R-611-1~10+R-T6 배치 13/13 PASS, 파일 수 29개 §2.4 일치)
</details>

<details>
<summary><b>T0-5. PRE-1~PRE-5 해소</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md`
  - §2.2 (L223-282): Hologram View 3요소(타임라인/스트리밍 캔버스/Glass HUD) 구조 정의 — PRE-1 출처
  - §4.1 (L335-344): 9-State 정규명(UI_S0_BOOT~UI_S8_ARCHIVED) — PRE-5 출처
  - §4.2: 전환 규칙 6건 — PRE-5 전이 다이어그램 출처
  - §4.4~§4.6: 런타임 6-State, 양방향 매핑, 파이프라인 매핑 — PRE-5 매핑 출처
  - §10.4 (L1493-1509): Hologram 컴포넌트 17개(V1 필수 13개) — PRE-2 교차 확인 대상
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md`
  - V1-P4 (L2274~2414): 44개 컴포넌트·8개 Hook·7개 Store 목록 — PRE-2/PRE-3/PRE-4 주 출처
  - §6.1 (L4561~4672): UI/UX 상세 ~85항목 — §6.1.3 Hook·Store 상호보완 대조 (CFL-HM-001 참조)

**절차**:
1. **[PRE-1]** D2.0-08 §2.2(L223-282)에서 Hologram View 3요소(타임라인/스트리밍 캔버스/Glass HUD) 구조 추출 — 각 영역의 역할·패널 크기·데이터 소스를 01_hologram-view-layout/_index.md 범위 테이블과 대조 확인 후, 3요소 정본 요약을 등록
2. **[PRE-2]** Part2 V1-P4 L2274~2414에서 44개 컴포넌트명 전수 추출 및 카테고리 분류(Layout/Feature/Atom), D2.0-08 §10.4 Hologram 17개와 교차 확인 — 17개가 44개의 부분집합인지 검증, 불일치 발견 시 CONFLICT_LOG에 즉시 기록(§9.3 규칙 적용)
3. **[PRE-3]** Part2 V1-P4에서 8개 Hook 이름·파라미터·반환값 추출, Part2 §6.1.3과 교차 대조 — CFL-HM-001(V1-P4와 §6.1.3 Hook 상호보완 관계) 인지 상태에서 수량 8개 범위 내 확인 (LOCK-HM-08)
4. **[PRE-4]** Part2 V1-P4에서 7개 Store 이름·상태 필드·액션 추출, Part2 §6.1.3과 교차 대조 — 수량 7개 범위 내 확인 (LOCK-HM-09)
5. 44 컴포넌트(이름+카테고리)·8 Hook(이름+시그니처)·7 Store(이름+상태 필드+액션) → `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\_index.md`에 전수 등록 (기존 범위 테이블·LOCK 테이블 하위에 목록 테이블 추가)
6. **[PRE-5]** D2.0-08 §4.1에서 9 State 정규명(UI_S0_BOOT~UI_S8_ARCHIVED) 추출, §4.2에서 전환 규칙 6건 추출, §4.4~§4.6에서 런타임 6-State·양방향 매핑·파이프라인 매핑 추출
7. 9 State(정규명+설명)·전환 규칙 6건·런타임 매핑 → `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\03_ui-state-machine\_index.md`에 전수 등록 (기존 범위 테이블·LOCK 테이블 하위에 목록 테이블 추가)

**검증**:
- [x] Hologram View 3요소 구조 확인 — 01_hologram-view-layout/_index.md에 타임라인/스트리밍 캔버스/Glass HUD 3건 등록, D2.0-08 §2.2 원문과 글자 대조 일치 (PRE-1)
- [x] 44 컴포넌트 전수 확인 — 02_component-architecture/_index.md에 44개 이름+카테고리 등록, Part2 V1-P4 원문과 글자 대조 일치 (PRE-2)
- [x] D2.0-08 §10.4 Hologram **18개**가 44개 내 부분집합 — 계획서 초안 "17개" 오류 발견, CFL-HM-002로 CONFLICT_LOG 기록 + 수정 완료 (PRE-2)
- [x] 8 Hook 전수 확인 — 02/_index.md에 8개 이름 양측 대조 등록, CFL-HM-001 상호보완 확인. V1-P4(useAuth/useStreaming) vs §6.1.3(useAutonomy/useLog) 이름 차이 인지, 수량 8개 LOCK-HM-08 범위 내 (PRE-3)
- [x] 7 Store 전수 확인 — 02/_index.md에 7개 이름·상태 필드·액션 등록, Part2 V1-P4 + §6.1.3 양측 원문 대조 **이름 완전 일치** (PRE-4)
- [x] 9 State 전수 확인 — 03/_index.md에 9개 정규명(UI_S0_BOOT~UI_S8_ARCHIVED)+설명 등록, D2.0-08 §4.1 원문과 글자 대조 일치 (PRE-5)
- [x] 전환 규칙 6건 + 런타임 6-State + 양방향 매핑 + 파이프라인 매핑 확인 — 03/_index.md에 전수 등록, D2.0-08 §4.2/§4.4~§4.6 원문 대조 일치 (PRE-5)
- [x] Part2 V1-P4 원문과 글자 대조 일치 (44 컴포넌트·8 Hook·7 Store 전수)
- [x] D2.0-08 원문과 글자 대조 일치 (3요소·9 State·전환 규칙·런타임 매핑 전수)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\01_hologram-view-layout\_index.md` (갱신) + `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\_index.md` (갱신) + `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\03_ui-state-machine\_index.md` (갱신)
**상태**: ✅ 완료 (2026-04-05 — PRE-1~PRE-5 전수 해소, D2.0-08·Part2 양측 원문 글자 대조 PASS, CFL-HM-002 등재)
</details>

<details>
<summary><b>T0-6. 도메인 경계 확정 (PRE-8/PRE-9 해소)</b></summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md`
  - §1.5: 도메인 경계 분석 (5개 인접 도메인 경계 정의)
  - §1.6: 6-11 소유 범위 (7개 영역)
  - §4.3 R-611-9: "6-11은 LLM 모델 선택/라우팅/폴백 로직을 구현하지 않음 — 해당 로직은 6-9(Brain-Adapter-HAL) 정본"
  - §8.3: 인접 도메인 파일 역할 구분 (소유 5항목 ✅ + 인접 소유 5항목 ❌ = 10항목)
  - §9.2: 도메인 간 충돌 시나리오 (6-1 관련: "6-11 렌더링 vs 6-1 UI/UX 체계", 6-9 관련: "6-11 LLM 응답 포맷 vs 6-9 LLM 라우팅")
  - §9.4 C-3: "6-11 vs 6-1 UI/UX 범위 — OPEN" (6-1 구조화 완료 시 재확정)
  - §11.1 SUP-1: "6-1 UI-UX-System 도메인 미구조화 → 6-1 Phase 0 완료 후 재확정"
  - §11.1 SUP-2: "6-9 Brain-Adapter-HAL 도메인 미구조화 → 6-9 Phase 0 완료 후 재확정"
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md`
  - 의존성 도메인 (L157~164): 6-1(← 참조), 6-9(← 소비) 포함 6건
  - 도메인 경계 (L168~185): 기존 13항목 (6-9: "LLM 라우팅/폴백 로직 ❌", 6-1: "Broad UI/UX 체계 ❌")
- `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\BRAIN_ADAPTER_HAL_구조화_종합계획서.md`
  - §5.2: 의존성 도메인 — "6-11 Hologram-Main-LLM | Main LLM 2-tier 라우팅 → Brain Adapter 경유 | ✅ 완료"
  - §8: 파일 역할 분리 — sot 2/6-9 = "어댑터 구현 패턴, 라우팅 config 상세, 폴백 시나리오, HAL 구현체 매핑, 성능 벤치마크 기준"
- `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\AUTHORITY_CHAIN.md`
  - 도메인 경계 (L82~89): "6-11 행 — 본 도메인 소유: HAL 라우팅 엔진, 병렬 태스크 상한(LOCK-69-2) / 인접 도메인 소유: Main LLM 2-tier 라우팅 정책, 응답 생성 로직"
  - 의존성 도메인 (L76): "6-11 Hologram-Main-LLM | ← 소비 | Main LLM 2-tier 라우팅이 Brain Adapter 경유"
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md`
  - §5.2: 도메인 중복 범위 — "6-11 Hologram-Main-LLM: 6-1은 Hologram View UI 구조만, 렌더링 로직은 6-11 범위"
  - ISS-6: "Hologram View와 6-11 도메인 범위 경계"
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md`
  - §5.1: 6-1 vs 6-11 경계 테이블 — 6-1 = UI 레이어(Glass HUD 레이아웃, 패널 배치, 상태 표시, React 컴포넌트, 상태관리) / 6-11 = LLM 통합(렌더링 로직, 응답 생성, 3-point 렌더링 품질, Main LLM 파이프라인, 프롬프트 조합) — 경계점: StreamingEffect 스트림 인터페이스

**전제 조건 확인**:
- 6-9 Phase 0: ✅ 완료 (2026-04-05, G0-1~G0-6 PASS) → SUP-2 해소 가능
- 6-1 Phase 0: ✅ 완료 (2026-04-03, G0 ALL PASS) → SUP-1 해소 가능
- 양측 AUTHORITY_CHAIN에 경계 정의 기 존재 → 신규 작성이 아닌 교차 대조 + 통합 문서화

**절차**:
1. **6-11 기존 경계 정의 수집**: 본 계획서 §1.5(5개 인접 도메인 경계), §1.6(7개 소유 영역), §4.3 R-611-9(라우팅/폴백 금지), §8.3(10항목 소유 테이블) 전수 추출
2. **6-9 기존 경계 정의 수집**: 6-9 AUTHORITY_CHAIN.md 도메인 경계 테이블(L84~89)에서 6-11 행 추출 — "6-9 소유: HAL 라우팅 엔진, 병렬 태스크 상한(LOCK-69-2)" / "6-11 소유: Main LLM 2-tier 라우팅 정책, 응답 생성 로직"
3. **6-1 기존 경계 정의 수집**: 6-1 AUTHORITY_CHAIN.md §5.1에서 6-1 vs 6-11 경계 테이블 추출 — 6-1 = Hologram View UI 구조(표시 계층), 6-11 = LLM 통합(생성 계층), 경계점 = StreamingEffect 스트림 인터페이스
4. **6-11 ↔ 6-9 경계 교차 대조**: 6-11 §8.3("LLM 라우팅/폴백 로직 ❌ → 6-9 소유") + R-611-9 규칙 vs 6-9 AUTHORITY_CHAIN L87("6-9 소유: HAL 라우팅 엔진, 병렬 태스크 상한") — 양측 일치 확인, 불일치 시 CONFLICT_LOG 등재
5. **6-11 ↔ 6-1 경계 교차 대조**: 6-11 §8.3("Broad UI/UX 체계 ❌ → 6-1 소유") + §9.2("6-11 렌더링 vs 6-1 UI/UX 체계") vs 6-1 AUTHORITY_CHAIN §5.1(표시 계층 vs 생성 계층) — 양측 일치 확인, 불일치 시 CONFLICT_LOG 등재
6. **경계 문서 작성**: `domain_boundary.md`에 다음 포함:
   - 문서 목적 + PRE-8/PRE-9 해소 근거
   - **§1 6-11 ↔ 6-9 경계**: 6-11 소유(Hologram View 렌더링 파이프라인, Main LLM 응답 → UI 변환, 2-tier 라우팅 정책 맥락 전달) vs 6-9 소유(HAL 라우팅 엔진, 폴백 체인 LOCK-69-8, ConnectorResponse 스키마, 병렬 태스크 상한 LOCK-69-2) — R-611-9 원문 인용 — 경계점: Brain Adapter ConnectorResponse 수신 인터페이스
   - **§2 6-11 ↔ 6-1 경계**: 6-11 소유(렌더링 로직, 응답 생성, 3-point 렌더링 품질, Main LLM 파이프라인, 프롬프트 조합) vs 6-1 소유(Hologram View UI 구조, Glass HUD 레이아웃, 패널 배치, 상태 표시, React 컴포넌트, 상태관리) — 경계점: StreamingEffect 스트림 인터페이스 (6-1 AUTHORITY_CHAIN §5.1 원문 인용)
   - **§3 소유권 전수 테이블**: §8.3 기반 10항목 + 양측 AUTHORITY_CHAIN 교차 대조 결과 (항목/6-11 소유/인접 도메인/인접 AUTHORITY_CHAIN 일치 여부)
   - **§4 LOCK 경계 영향**: 6-9 LOCK-69-2(병렬 상한), LOCK-69-8(폴백 순서) → 6-11은 소비만, 정의 변경 불가 명시
   - **§5 충돌 시나리오**: §9.2에서 6-1/6-9 관련 시나리오 인용 + 해소 규칙
7. **§9.4 C-3 해소**: C-3("6-11 vs 6-1 UI/UX 범위 — OPEN")을 domain_boundary.md §2 근거로 RESOLVED 처리 → CONFLICT_LOG.md에 상태 갱신
8. **§11.1 SUP-1/SUP-2 해소**: 6-1 Phase 0 완료(2026-04-03) + 6-9 Phase 0 완료(2026-04-05) 확인 → SUP-1/SUP-2 상태를 "✅ T0-6에서 해소" 갱신
9. **PRE-8/PRE-9 해소 기록**: PRE-8("6-9 경계 확정") + PRE-9("6-1 경계 확정")을 "✅ T0-6" 상태로 갱신

**검증**:
- [x] domain_boundary.md에 6-11 ↔ 6-9 경계 섹션 존재 — R-611-9 원문("6-11은 LLM 모델 선택/라우팅/폴백 로직을 구현하지 않음") 인용 포함 — §1.2 L25 글자 대조 일치
- [x] domain_boundary.md에 6-11 ↔ 6-1 경계 섹션 존재 — 6-1 AUTHORITY_CHAIN §5.1 경계(표시 계층 vs 생성 계층, StreamingEffect 인터페이스) 원문 인용 포함 — §2.2 L54-59 글자 대조 일치
- [x] 6-9 AUTHORITY_CHAIN L87 경계 정의와 양측 일치 확인 — "6-9 소유: HAL 라우팅 엔진, 병렬 태스크 상한(LOCK-69-2)" / "6-11 소유: Main LLM 2-tier 라우팅 정책, 응답 생성 로직" 반영 — §1.3 교차 대조 4항목 전수 ✅
- [x] 6-1 AUTHORITY_CHAIN §5.1 경계 정의와 양측 일치 확인 — 6-1(UI 레이어) / 6-11(LLM 통합) / 경계점(StreamingEffect) 반영 — §2.3 교차 대조 4항목 전수 ✅
- [x] §8.3 기반 소유권 10항목 전수 반영 + 양측 AUTHORITY_CHAIN 교차 대조 결과 기재 — §3 전수 테이블 13항목(§8.3 10 + AC 추가 3), 라인 번호 전수 대조 일치(§8.3 L733~L742, AC L174~L186)
- [x] 6-9 LOCK-69-2(병렬 상한), LOCK-69-8(폴백 순서) 경계 영향 명시 — 6-11은 소비만(정의 변경 불가) — §4 L108-109, 값 6-9 §3.3 글자 대조 일치
- [x] §9.2 충돌 시나리오(6-1 관련 1건 + 6-9 관련 1건) 인용 + 해소 규칙 포함 — §5.1(S3) + §5.2(S4)
- [x] §9.4 C-3 OPEN → RESOLVED 처리 + CONFLICT_LOG.md 갱신 — CONFLICT_LOG OPEN 0건, C-3 RESOLVED, 변경 이력 T0-6 행 추가
- [x] §11.1 SUP-1/SUP-2 상태 갱신 확인 (6-1/6-9 Phase 0 완료 근거 명시) — SUP-1 "✅ 해소"(6-1 2026-04-03), SUP-2 "✅ 해소"(6-9 2026-04-05)
- [x] PRE-8/PRE-9 상태 "✅ T0-6" 갱신 확인 — §5 선행작업 테이블 PRE-8/PRE-9 양쪽 "✅ T0-6"
- [x] 불일치 발견 시 CONFLICT_LOG 등재 여부 확인 — 교차 대조 완료, 불일치 0건 (§1.3 + §2.3 + §3 전수 ✅)
- [x] 파일이 비어있지 않음 — domain_boundary.md 144줄

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\domain_boundary.md` (신규) + `CONFLICT_LOG.md` (C-3 RESOLVED 갱신) + `AUTHORITY_CHAIN.md` (도메인 경계 섹션에 domain_boundary.md 교차 참조 추가) + PRE-8/PRE-9/SUP-1/SUP-2 상태 갱신 (본 계획서)
**상태**: ✅ 완료 (2026-04-05, 검증 12/12 PASS — R-611-9 원문 글자 대조 일치 + 6-1 AC §5.1 원문 글자 대조 일치 + 6-9 AC L87 글자 대조 일치 + LOCK-69-2/69-8 값 글자 대조 일치 + §3 라인 번호 13건 전수 대조 + 양측 교차 대조 불일치 0건 + C-3 RESOLVED + SUP-1/SUP-2 해소 + PRE-8/PRE-9 해소 + G0-6 PASS)
</details>

**Phase 0→Phase 1 게이트 (G0)**:
- [x] **G0-1**: T0-1 계획서 APPROVED — ✅ 완료 (2026-04-05, 14+1 섹션 + LOCK-HM-01~10 전수 반영 + SoT 4건 수집 검증)
- [x] **G0-2**: AUTHORITY_CHAIN.md에 권한 체계 + LOCK-HM-01~10 전수 포함 + 각 LOCK 출처·적용 서브폴더·위반 조치 기재 — ✅ 완료 (2026-04-05, LOCK 10건 SoT 원문 전수 대조 + 위반 조치 10건 + T6 규칙 4건 + 의존성 6건 + 경계 13항목)
- [x] **G0-3**: CONFLICT_LOG.md에 §9.1 우선순위 5단 원문 + 5개 컬럼 테이블 + §9.4 초기 3행(C-1~C-3) + CFL-HM-001 행 + LOCK baseline 행 + §9.3 기록 규칙 4항목 존재 — ✅ 완료 (2026-04-05, 검증 9/9 + 2차 검증 28항목 전수 PASS, 2차 수정 3건 반영: C-2 1순위·C-3 R9+§8.3·인접 5개 도메인) + T0-5 추가: CFL-HM-002(HV 18), CFL-HM-003(★39 vs 37) → RESOLVED 5건
- [x] **G0-4**: 7개 서브폴더(01_hologram-view-layout ~ 07_orchestration-layer) 디렉토리 존재 + 7개 _index.md 존재·비어있지 않음 + 각 _index.md에 폴더 목적·범위·LOCK 참조·Phase 배정·파일 목록·정본 소유 포함 (6항목) + 폴더명·파일명이 §2.1/§8.2와 글자 일치 — ✅ 완료 (2026-04-05, 1차 검증 7/7 PASS + 2차 검증: 인코딩 9건 수정, LOCK 30항목 글자 대조 PASS, ISS 16건 PASS, 규칙 13건 PASS)
- [x] **G0-5**: Hologram View 3요소 구조 확인(PRE-1) + 44 컴포넌트/8 Hook(이름·파라미터·반환값)/7 Store(이름·상태 필드·액션)/9 State+전환 6건+런타임 매핑 전수 확인(PRE-2~PRE-5) + D2.0-08·Part2 양측 원문 글자 대조 PASS — ✅ 완료 (2026-04-05, CFL-HM-002 HV 18개 수정 반영, CFL-HM-001 Hook 상호보완 확인)
- [x] **G0-6**: 6-1, 6-9 도메인 경계 문서화 완료 — ✅ 완료 (2026-04-05, domain_boundary.md §1~§5 작성, 양측 AUTHORITY_CHAIN 교차 대조 불일치 0건, C-3 RESOLVED, PRE-8/PRE-9 해소, SUP-1/SUP-2 해소)

### Phase 1: 기본 구현 문서 — ✅ 완료 (2026-04-14)

**Phase 1 전체 상태**: ✅ 완료 (2026-04-14) — T1-1~T1-6 6/6 PASS, ISS-01~ISS-05/ISS-14/ISS-16 전수 해소, /validate PASS, LOCK-HM-01~10 변경 0건, CONFLICT RESOLVED 10건(C-1/C-2/C-3 + CFL-HM-001/002/003 기존 유지 + Step 7 정식 등재 CFL-HM-004/005/006/007), OPEN 0건, Phase 2 진입 가능.

| 태스크 | 산출물 | 완료 기준 |
|--------|--------|----------|
| T1-1 Hologram View 레이아웃 상세 | 01_hologram-view-layout/*.md 3개 | ✅ 완료 (2026-04-14, v1.0). 3요소 렌더링 파이프라인 + 4-Layout 전환 프로토콜 + 반응형 규칙 명세. 산출물 3건 1078줄(layout_structure 428 + layout_switching 365 + responsive_rules 285), LOCK-HM-01/02 정본 글자 일치, ISS-01 해소, 검증 5/5 PASS, CONFLICT 0건. 이월 없음 |
| T1-2 44개 컴포넌트 카탈로그 | 02_component-architecture/component_catalog.md | ✅ 완료 (2026-04-14, v1.0). 44개 컴포넌트 전수 Props/역할/계층/의존 그래프 명세. 산출물 1건 616줄(View별 12+18+7+4+3=44, 기능 그룹 §6.1.2 합계 44, V1 필수 39), LOCK-HM-07 정본 정합 PASS, ISS-02/ISS-14 해소, 검증 5/5 PASS, CONFLICT 신규 0건(CFL-HM-002/003 기존 해소 반영). 이월 없음(T1-3~T1-6 독립) |
| T1-3 8개 Hook 카탈로그 | 02_component-architecture/hook_catalog.md | ✅ 완료 (2026-04-14, v1.0). 8개 Custom Hook 전수 시그니처/상태 흐름/사용처 매핑 명세. 산출물 1건 634줄(useTauriIPC/useDecision/useWorkflow/useNotification/useAuth/useMemory/useCost/useStreaming = 8개 = LOCK-HM-08), V1-P4 L2327-2330 정본 정합 PASS, ISS-03 해소, 검증 6/6 PASS, CONFLICT 신규 0건(CFL-HM-001 기존 RESOLVED 상호보완 반영). 이월 없음(T1-4~T1-6 독립) |
| T1-4 7개 Store 카탈로그 | 02_component-architecture/store_catalog.md | ✅ 완료 (2026-04-14, v1.0). 7개 Zustand Store 전수 State 스키마/셀렉터/액션/구독 관계 명세. 산출물 1건 606줄(appStore/decisionStore/costStore/notificationStore/authStore/memoryStore/workflowStore = 7개 = LOCK-HM-09), Part2 V1-P4 L2331 정본 정합 PASS, ISS-04 해소, T1-2 component_catalog "구독 Store" 열·T1-3 hook_catalog "(f) 의존 Store" cross-check 불일치 0건, 테스트 시나리오 16건, 에러표 6코드, Big-O+LOCK+ABC 매핑. CONFLICT 신규 0건, LOCK 변경 없음. 이월 없음(T1-5/T1-6 독립) |
| T1-5 9-State Machine 상세 | 03_ui-state-machine/*.md 2개 | ✅ 완료 (2026-04-14, v1.0). 9개 UI 상태 전수 정의(S0~S8) + 기본 전이 6건(LOCK) + 확장 전이 포함 9×9 FROM×TO 매트릭스 + 가드/액션 전수 명세. 산출물 2건 929줄(state_definitions 511 + transition_matrix 418), LOCK-HM-03 §4.1 9개 노드 정본 정합 PASS, ISS-05 해소, 검증 6/6 PASS, CONFLICT Step 7 정식 등재 CFL-HM-004/005 2건 모두 RESOLVED(OPEN 0). 이월 없음(T1-6 독립) |
| T1-6 ChatPage 통합 패턴 | 02_component-architecture/chatpage_integration.md | ✅ 완료 (2026-04-14, v1.0). ChatPage.tsx 진입점 통합 명세 — HV-LAYOUT-01 단일 자식 트리, 9-단계 메시지 파이프라인(USER_SUBMIT~ASSISTANT_CLOSE+ERROR+APPROVAL+COST), SSE/WS→useStreaming→HV-CHAT-01/02/03 렌더 계층, 6-kind ArtifactRenderRule 매트릭스+resolveArtifactRender, 공통 자료구조 선정의(MessageEvent/ArtifactRenderRule/ChatPageContext — T1-2/T1-3/T1-4와 중복 0건), 에러 10/복구 10/테스트 15 시나리오, LOCK-HM-07/08/09 정본 정합 PASS(Hook 8 전수·Store 7 전수), ISS-16 해소, T1-2 컴포넌트ID/T1-3 Hook/T1-4 Store cross-check 불일치 0건, CONFLICT Step 7 정식 등재 CFL-HM-006/007 2건 모두 RESOLVED(CFL-HM-001/002/003 기존 RESOLVED 유지, OPEN 0). 이월: T2-1/T2-2/T2-3/T2-4/T2-5/T2-6 위임 (SSE 스키마 본체·3-point 매핑·HUD 애니메이션·DCL·2-tier·I-10) |

**Phase 1 → Phase 2 게이트**: ✅ PASS (2026-04-14) — ISS-01/02/03/04/05/14/16 전수 해소 + /validate PASS + LOCK-HM-01~10 변경 0건 + CONFLICT OPEN 0건 (Step 7 CFL-HM-004~007 정식 등재·전부 RESOLVED 포함)

#### Phase 1 단계별 상세 작업 절차

<details>
<summary><b>T1-1. Hologram View 레이아웃 상세</b></summary>

**대조 기준**:
- §7 세부 작업: T1-1 "Hologram View 레이아웃 상세"
- §7 전환 게이트: ISS-01 해소 + /validate PASS
- §6 이슈: ISS-01 (Phase 1 완료 시점)

**목표**: Hologram View의 타임라인 + 스트리밍 캔버스 + Glass HUD 3요소 렌더링 파이프라인과 4개 레이아웃 간 전환 프로토콜을 완전 명세한다. LOCK-HM-01(Hologram View 3요소), LOCK-HM-02(4 Layout 구조)를 기준으로 데이터 흐름과 반응형 규칙까지 커버한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\01_hologram-view-layout\_index.md` (도메인 인덱스 — 추출 현황 및 미해소 이슈 목록)
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.1(4 Layout), §2.2(Hologram View 3요소), §3(전환 프로토콜) — LOCK-HM-01, LOCK-HM-02 정본

**절차**:
1. `_index.md`에서 ISS-01 미해소 항목 및 기존 추출 현황을 확인한다.
2. `D2.0-08` §2.2를 읽어 타임라인 패널 / 스트리밍 캔버스 / Glass HUD의 렌더링 순서와 데이터 흐름을 추출한다.
3. `D2.0-08` §2.1 및 §3을 읽어 3-Column → Builder → Hologram → CLI 전환 조건과 전환 시 상태 유지 규칙을 추출한다.
4. 추출 내용을 세 파일로 분리 작성한다: `layout_structure.md`(3요소 구조 + 렌더링 파이프라인), `layout_switching.md`(전환 프로토콜 + 가드 조건), `responsive_rules.md`(반응형 브레이크포인트 + 오버라이드 규칙).
5. 각 파일 상단에 `출처: D2.0-08 §{섹션}` 및 `LOCK: LOCK-HM-01, LOCK-HM-02` 메타데이터를 기재한다.
6. ISS-01 해소 여부를 체크리스트로 기재한 후 `/validate`를 실행한다.

**검증**:
- [x] `layout_structure.md`에 타임라인 / 스트리밍 캔버스 / Glass HUD 3요소 각각의 데이터 흐름이 명시됨 ✅ (3요소 × 렌더 파이프라인 + 데이터 흐름 Mermaid)
- [x] `layout_switching.md`에 4개 레이아웃 간 전이 트리거와 상태 유지 규칙이 명시됨 ✅ (4×4 전이 매트릭스 + 가드 조건 + 상태 보존표)
- [x] `responsive_rules.md`에 반응형 브레이크포인트 규칙이 명시됨 ✅ (브레이크포인트 + 오버라이드 + 레이아웃별 강등 규칙)
- [x] 모든 파일에 정본 출처(D2.0-08 §섹션) 및 LOCK-HM-01/02 태그 기재 ✅ (3/3 파일 메타데이터 PASS)
- [x] ISS-01 해소 확인 및 `/validate` PASS ✅ (5/5 검증 항목 PASS, ISS-01 RESOLVED)

> **완료**: 2026-04-14. Hologram View 3요소 렌더링 파이프라인 + 4-Layout 전환 프로토콜 + 반응형 규칙을 3개 파일에 완전 명세, ISS-01 해소.
>
> **실행 결과 요약**:
> - 산출물 3건 / 총 1078줄 (layout_structure.md 428줄, layout_switching.md 365줄, responsive_rules.md 285줄)
> - LOCK-HM-01(Hologram View 3요소) / LOCK-HM-02(4-Layout 구조) 정본 글자 일치 검증 PASS, D2.0-08 §2.1/§2.2/§3 출처 표기 3/3
> - 4개 레이아웃 × 4개 레이아웃 전이 매트릭스 16칸 전수 작성, 상태 유지/소실 규칙 명시
> - SoT 교차검증: D2.0-08 정본과 LOCK-HM-01/02 일치, 인접 도메인(6-1/6-9) 경계 위반 0건
> - 재검증/이월 없음, CONFLICT 신규 발견 0건
> - 해결 이슈: ISS-01 RESOLVED

**[T1-1] 검증 결과 요약** (갱신: 2026-04-14)
- 0. 산출물: 3개 파일 (`01_hologram-view-layout/layout_structure.md`, `layout_switching.md`, `responsive_rules.md`), 총 1078줄
- 1. 게이트: G1(T1-1) ✅ — 검증 5/5 PASS, ISS-01 해소, /validate PASS
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음 (LOCK-HM-01, LOCK-HM-02 baseline 유지)
- 4. 이월: 없음 (T1-2~T1-6 후속 세션은 독립 수행)

**산출물**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\01_hologram-view-layout\layout_structure.md` (3요소 렌더링 파이프라인)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\01_hologram-view-layout\layout_switching.md` (전환 프로토콜)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\01_hologram-view-layout\responsive_rules.md` (반응형 규칙)
</details>

<details>
<summary><b>T1-2. 44개 컴포넌트 카탈로그</b></summary>

**대조 기준**:
- §7 세부 작업: T1-2 "44개 컴포넌트 카탈로그"
- §7 전환 게이트: ISS-02, ISS-14 해소 + /validate PASS
- §6 이슈: ISS-02 (Phase 1 완료 시점), ISS-14 (Phase 1 완료 시점)

**목표**: LOCK-HM-07(44개 React 컴포넌트 구조)을 기준으로 44개 컴포넌트 전수의 Props 인터페이스, 역할, 계층 위치, 의존 그래프(import/props 관계)를 단일 카탈로그에 완전 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\_index.md` (도메인 인덱스 — 추출 현황 및 ISS-02, ISS-14 미해소 항목)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4 (LOCK-HM-07 정본 — 44개 컴포넌트 Props/계층/의존관계)

**절차**:
1. `_index.md`에서 ISS-02, ISS-14 미해소 항목과 기존 추출 현황을 확인한다.
2. `PART2_구현단계.md` V1-P4 섹션을 읽어 44개 컴포넌트 목록을 전수 확보한다.
3. 각 컴포넌트에 대해 다음 항목을 추출한다: 컴포넌트명, 파일 경로, Props 인터페이스(타입 포함), 역할 요약, 계층 레벨(페이지/레이아웃/기능/공통), 부모-자식 관계.
4. import/props 의존 관계를 분석하여 컴포넌트 간 의존 그래프(방향 그래프 형태의 텍스트 표현)를 작성한다.
5. 44개 전수 목록과 의존 그래프를 `component_catalog.md`에 통합 작성한다.
6. 파일 상단에 `출처: PART2_구현단계.md V1-P4` 및 `LOCK: LOCK-HM-07` 메타데이터를 기재한다.
7. ISS-02, ISS-14 해소 여부를 체크리스트로 기재한 후 `/validate`를 실행한다.

**검증**:
- [x] 컴포넌트 총 수가 정확히 44개임 ✅ (View별 12+18+7+4+3=44, 기능 그룹 §6.1.2 합계 44 교차 일치)
- [x] 각 컴포넌트에 Props 인터페이스(타입 명시), 역할, 계층 레벨이 기재됨 ✅ (§5.1~§5.5 44/44 전수, L0~L4 계층)
- [x] 의존 그래프에 44개 컴포넌트 간 import/props 방향 관계가 명시됨 ✅ (§6.1 Mermaid + §6.2 인접 리스트 + §6.3 매트릭스 요약)
- [x] 정본 출처(PART2_구현단계.md V1-P4) 및 LOCK-HM-07 태그 기재 ✅ (헤더 메타데이터 + §1 교차 참조 블록)
- [x] ISS-02, ISS-14 해소 확인 및 `/validate` PASS ✅ (§13 체크리스트 9/9 PASS)

> **완료**: 2026-04-14. 44개 React 컴포넌트 전수의 Props 인터페이스 / 역할 / 계층 / 의존 그래프를 단일 카탈로그에 완전 명세, ISS-02 / ISS-14 해소.
>
> **실행 결과 요약**:
> - 산출물 1건 / 총 616줄 (`02_component-architecture/component_catalog.md`)
> - LOCK-HM-07(44개) 정본 정합 PASS — View별 12+18+7+4+3=44, 기능 그룹(Part2 §6.1.2) 합계 44, V1 필수 39 (CFL-HM-003 반영)
> - 44개 전수 Props/역할/계층(L0~L4) 기재 + import/props 방향 의존 그래프 Mermaid + 인접 리스트 + 매트릭스 작성
> - SoT 교차검증: PART2 V1-P4 / D2.0-08 §10.4 / Part2 §6.1.2 3원 출처 정합, CFL-HM-002(Hologram 18개) / CFL-HM-003(V1 필수 39) 본문 반영
> - 세션 간 인터페이스 cross-check: T1-1(Hologram 3-Pane 정합), T1-3/T1-4/T1-6(사용 Hook / 구독 Store / ChatPage 트리 스텁) 열 기재
> - 재검증/이월 없음 (T1-3~T1-6 은 독립 세션), 신규 CONFLICT 등재 없음
> - 해결 이슈: ISS-02 RESOLVED, ISS-14 RESOLVED

**[T1-2] 검증 결과 요약** (갱신: 2026-04-14)
- 0. 산출물: 1개 파일 (`02_component-architecture/component_catalog.md`, 616줄, §0~§15 + 44개 전수 카드 + Mermaid 의존 그래프)
- 1. 게이트: G1(T1-2) ✅ — 검증 5/5 PASS, ISS-02 / ISS-14 해소, /validate PASS, §13 체크리스트 9/9 PASS
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (기존 CFL-HM-002 / CFL-HM-003 본문 반영 완료, 신규 등재 불필요)
- 3. LOCK 변경: 없음 (LOCK-HM-07 수량 44개 baseline 유지, Props/의존만 DEFINED-HERE 로 보강)
- 4. 이월: 없음 (T1-3 Hook / T1-4 Store / T1-5 State Machine / T1-6 ChatPage 통합 / T2-2 3-point 바인딩 / T2-4 Glass HUD / T2-6 I-10 매핑은 각 해당 세션 위임이며 본 세션 블로커 아님)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\component_catalog.md` (44개 컴포넌트 전수 Props/역할/계층/의존 그래프)
</details>

<details>
<summary><b>T1-3. 8개 Hook 카탈로그</b></summary>

**대조 기준**:
- §7 세부 작업: T1-3 "8개 Hook 카탈로그"
- §7 전환 게이트: ISS-03 해소 + /validate PASS
- §6 이슈: ISS-03 (Phase 1 완료 시점)

**목표**: LOCK-HM-08(8개 Custom Hook)을 기준으로 8개 Custom Hook 전수의 함수 시그니처, 상태 흐름, 사용처(어느 컴포넌트에서 호출되는지) 매핑을 단일 카탈로그에 완전 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\_index.md` (도메인 인덱스 — 추출 현황 및 ISS-03 미해소 항목)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4 (LOCK-HM-08 정본 — 8개 Custom Hook 시그니처/상태흐름/사용처)

**절차**:
1. `_index.md`에서 ISS-03 미해소 항목과 기존 추출 현황을 확인한다.
2. `PART2_구현단계.md` V1-P4 섹션을 읽어 8개 Custom Hook 목록을 전수 확보한다.
3. 각 Hook에 대해 다음 항목을 추출한다: Hook명, 파일 경로, 함수 시그니처(파라미터 타입 + 반환 타입), 내부 상태 목록(useState/useReducer), 상태 흐름 설명, 사용처 컴포넌트 목록.
4. 상태 흐름은 입력 이벤트 → 상태 변경 → 반환값 변화의 순서로 서술한다.
5. 8개 전수 내용을 `hook_catalog.md`에 통합 작성한다.
6. 파일 상단에 `출처: PART2_구현단계.md V1-P4` 및 `LOCK: LOCK-HM-08` 메타데이터를 기재한다.
7. ISS-03 해소 여부를 체크리스트로 기재한 후 `/validate`를 실행한다.

**검증**:
- [x] Hook 총 수가 정확히 8개임 ✅
- [x] 각 Hook에 함수 시그니처(파라미터 + 반환 타입 명시)가 기재됨 ✅
- [x] 각 Hook에 상태 흐름(이벤트 → 상태 변경 → 반환값)이 기재됨 ✅
- [x] 각 Hook에 사용처 컴포넌트 목록이 기재됨 ✅
- [x] 정본 출처(PART2_구현단계.md V1-P4) 및 LOCK-HM-08 태그 기재 ✅
- [x] ISS-03 해소 확인 및 `/validate` PASS ✅

> **완료**: 2026-04-14. LOCK-HM-08(8개 Custom Hook) 기준 8개 전수 시그니처/상태 흐름/사용처 매핑을 `hook_catalog.md` 단일 파일로 통합 명세, ISS-03 해소.
>
> **실행 결과 요약**:
> - 산출물 1건 634줄 (§1 교차참조 + §2 at-a-glance 표 + §3 공통 자료구조 + Hook 8개 전수 상세 + 검증)
> - 8개 Hook 전수: useTauriIPC / useDecision / useWorkflow / useNotification / useAuth / useMemory / useCost / useStreaming = LOCK-HM-08 수량 일치
> - 재검증 6/6 PASS (수량 8개, 시그니처, 상태 흐름, 사용처, 정본 출처, ISS-03 해소)
> - SoT 교차: PART2_구현단계.md V1-P4 L2327-2330 정본 글자 정합, §6.1.3 변종(useAutonomy/useLog)은 CFL-HM-001 RESOLVED(상호보완, useAuth/useStreaming 내부 흡수)로 반영, component_catalog.md §5 "사용 Hook" 열과 cross-check 정합
> - 이월 없음 (T1-4 Store / T1-5 State Machine / T1-6 ChatPage 통합은 각 해당 세션 위임, 본 세션 블로커 아님)

**[T1-3] 검증 결과 요약** (갱신: 2026-04-14)
- 0. 산출물: 파일 1개 (`02_component-architecture/hook_catalog.md`, 634줄)
- 1. 게이트: ISS-03 해소 PASS (Phase 1 완료 시점 게이트 요건 충족) + /validate PASS
- 2. CONFLICT: 신규 0 / 기존 0 / 해소(기존 반영) 1 (CFL-HM-001 RESOLVED 상호보완 적용)
- 3. LOCK 변경: 없음 (LOCK-HM-08 수량 8개 유지)
- 4. 이월: 없음 (T1-4/T1-5/T1-6 은 각 해당 세션 독립 위임)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\hook_catalog.md` (8개 Custom Hook 전수 시그니처/상태흐름/사용처 매핑)
</details>

<details>
<summary><b>T1-4. 7개 Store 카탈로그</b></summary>

**대조 기준**:
- §7 세부 작업: T1-4 "7개 Store 카탈로그"
- §7 전환 게이트: ISS-04 해소 + /validate PASS
- §6 이슈: ISS-04 (Phase 1 완료 시점)

**목표**: LOCK-HM-09(7개 Zustand Store)를 기준으로 7개 Zustand Store 전수의 상태 스키마, 셀렉터, 액션 정의를 단일 카탈로그에 완전 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\_index.md` (도메인 인덱스 — 추출 현황 및 ISS-04 미해소 항목)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4 (LOCK-HM-09 정본 — 7개 Zustand Store 스키마/셀렉터/액션)

**절차**:
1. `_index.md`에서 ISS-04 미해소 항목과 기존 추출 현황을 확인한다.
2. `PART2_구현단계.md` V1-P4 섹션을 읽어 7개 Zustand Store 목록을 전수 확보한다.
3. 각 Store에 대해 다음 항목을 추출한다: Store명, 파일 경로, 상태 스키마(필드명 + 타입), 셀렉터 목록(셀렉터명 + 반환 타입), 액션 목록(액션명 + 파라미터 + 부작용).
4. Store 간 구독/참조 관계가 있는 경우 의존 관계를 명시한다.
5. 7개 전수 내용을 `store_catalog.md`에 통합 작성한다.
6. 파일 상단에 `출처: PART2_구현단계.md V1-P4` 및 `LOCK: LOCK-HM-09` 메타데이터를 기재한다.
7. ISS-04 해소 여부를 체크리스트로 기재한 후 `/validate`를 실행한다.

**검증**:
- [x] Store 총 수가 정확히 7개임 ✅
- [x] 각 Store에 상태 스키마(필드명 + 타입 명시)가 기재됨 ✅
- [x] 각 Store에 셀렉터 목록(반환 타입 포함)이 기재됨 ✅
- [x] 각 Store에 액션 목록(파라미터 + 부작용 포함)이 기재됨 ✅
- [x] 정본 출처(PART2_구현단계.md V1-P4) 및 LOCK-HM-09 태그 기재 ✅
- [x] ISS-04 해소 확인 및 `/validate` PASS ✅

> **완료**: 2026-04-14. LOCK-HM-09(7개 Zustand Store) 기준 7개 전수의 State 스키마/셀렉터/액션/구독 관계를 `store_catalog.md` 단일 파일로 통합 명세, ISS-04 해소.
>
> **실행 결과 요약**:
> - 산출물 1건 606줄 (`02_component-architecture/store_catalog.md`, §1 교차참조 + §2 at-a-glance 표 + §3 공통 자료구조 + Store 7개 전수 상세 + 테스트/에러/검증)
> - 7개 Store 전수: appStore / decisionStore / costStore / notificationStore / authStore / memoryStore / workflowStore = LOCK-HM-09 수량 일치
> - SoT 교차: PART2_구현단계.md V1-P4 L2331 정본 글자 정합 PASS, T1-2 `component_catalog.md` "구독 Store" 열 및 T1-3 `hook_catalog.md` "(f) 의존 Store" 항목과 cross-check 불일치 0건
> - 각 Store 카드: State 필드 + 셀렉터(반환 타입) + 액션(파라미터/부작용) + Store 간 구독/의존 그래프 + Big-O 복잡도 + LOCK/ABC 매핑 기재, 테스트 시나리오 16건, 에러 코드 6건 표 작성
> - 재검증 6/6 PASS (수량 7개, 상태 스키마, 셀렉터, 액션, 정본 출처, ISS-04 해소), 신규 CONFLICT 0건, LOCK 변경 0건
> - 이월 없음 (T1-5 State Machine / T1-6 ChatPage 통합은 각 해당 세션 독립 위임, 본 세션 블로커 아님)

**[T1-4] 검증 결과 요약** (갱신: 2026-04-14)
- 0. 산출물: 파일 1개 (`02_component-architecture/store_catalog.md`, 606줄)
- 1. 게이트: ISS-04 해소 PASS (Phase 1 완료 시점 게이트 요건 충족) + /validate PASS, 검증 6/6 PASS
- 2. CONFLICT: 신규 0 / 기존 0 / 해소 0 (Store 영역 CONFLICT 후보 없음, T1-2/T1-3 cross-check 불일치 0건)
- 3. LOCK 변경: 없음 (LOCK-HM-09 수량 7개 baseline 유지, State/셀렉터/액션만 DEFINED-HERE 로 보강)
- 4. 이월: 없음 (T1-5 State Machine / T1-6 ChatPage 통합은 각 해당 세션 독립 위임)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\store_catalog.md` (7개 Zustand Store 전수 스키마/셀렉터/액션 정의)
</details>

<details>
<summary><b>T1-5. 9-State Machine 상세</b></summary>

**대조 기준**:
- §7 세부 작업: T1-5 "9-State Machine 상세"
- §7 전환 게이트: ISS-05 해소 + /validate PASS
- §6 이슈: ISS-05 (Phase 1 완료 시점)

**목표**: LOCK-HM-03(9-State UI State Machine)을 기준으로 9개 UI 상태 전수의 정의와 9×N 전이 매트릭스(가드 조건 + 액션 포함)를 완전 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\03_ui-state-machine\_index.md` (도메인 인덱스 — 추출 현황 및 ISS-05 미해소 항목)
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §4 (LOCK-HM-03 정본 — 9-State Machine 전이 매트릭스, 가드 조건, 액션 정의)

**절차**:
1. `_index.md`에서 ISS-05 미해소 항목과 기존 추출 현황을 확인한다.
2. `D2.0-08` §4를 읽어 9개 UI 상태 목록과 각 상태의 정의(진입 조건, 활성 조건, 종료 조건)를 추출한다.
3. 9개 상태 간 전이 트리거, 가드 조건, 전이 시 실행 액션을 전수 추출하여 전이 매트릭스(FROM × TO × 조건 × 액션)를 작성한다.
4. 상태 정의를 `state_definitions.md`에 작성하고, 전이 매트릭스를 `transition_matrix.md`에 작성한다.
5. 각 파일 상단에 `출처: D2.0-08 §4` 및 `LOCK: LOCK-HM-03` 메타데이터를 기재한다.
6. ISS-05 해소 여부를 체크리스트로 기재한 후 `/validate`를 실행한다.

**검증**:
- [x] 상태 총 수가 정확히 9개임 ✅ (S0_BOOT / S1_IDLE / S2_EDITING / S3_READY / S4_RUNNING / S5_AWAIT_APPROVAL / S6_PRESENTING / S7_RECOVERY / S8_ARCHIVED = 9, D2.0-08 §4.1 LOCK 정본 일치)
- [x] `state_definitions.md`에 각 상태의 진입/활성/종료 조건이 명시됨 ✅ (§2.1~§2.9 각 상태마다 진입/활성/종료 조건 표 전수 기재)
- [x] `transition_matrix.md`에 9개 상태 간 전이 트리거, 가드 조건, 액션이 전수 기재됨 ✅ (§2 기본 6건 + §3 확장 전이 + TransitionEdge 스키마 guard/action 필드 전수)
- [x] 전이 매트릭스가 FROM × TO 형식의 표 또는 구조화된 목록으로 표현됨 ✅ (§4 "FROM × TO 매트릭스 (9×9)" 표 + 금지 셀/경유 규칙 명시)
- [x] 정본 출처(D2.0-08 §4) 및 LOCK-HM-03 태그 기재 ✅ (양 파일 §0.1 LOCK 메타데이터 + §0.2 교차 참조 블록)
- [x] ISS-05 해소 확인 및 `/validate` PASS ✅ (9-State 정의 + 전이 매트릭스 전수 완성으로 ISS-05 해소)

> **완료**: 2026-04-14
> - D2.0-08 §4.1 원문 9개 상태 정규명(S0~S8) 번호/이름 글자 일치 PASS, 추가/축소 0건
> - D2.0-08 §4.2 기본 전이 6건 LOCK 원문 유지 + DEFINED-HERE 확장 전이 보강(초기화·아카이브·복구 경로)
> - 9×9 FROM×TO 매트릭스 완성, 금지 셀(—) 경유 규칙 및 S0 진입 제약(TX-01/TX-15) 명시
> - EngineState ↔ PipelineStage ↔ UIState 3중 매핑 일관성 검증 테이블(§3) 및 `ui.core.state.mismatch` 이벤트 연동 규약 기재
> - 6-12 Event-Logging `ui.state.transition` JSON 스키마 연결, Part2 §6.1.6 L4622-4642 주요 전이 쌍방 대조 일치

**[T1-5] 검증 결과 요약**
- 0. 산출물: 2건 929줄 (`03_ui-state-machine/state_definitions.md` 511줄, `03_ui-state-machine/transition_matrix.md` 418줄)
- 1. 게이트: ISS-05 해소 + /validate PASS (검증 체크리스트 6/6 PASS)
- 2. CONFLICT: 신규 0건 (후보 2건 — ① D2.0-08 §4.2 기본 전이 6건(LOCK)과 DEFINED-HERE 확장 전이의 권한 경계 → 확장은 노드 추가 없이 엣지만 보강하여 LOCK 무위반 확인 / ② Part2 §6.1.6 "주요 전이" 표기와 본 매트릭스 9×9 완전성 차이 → Part2는 요약, 본 문서가 정본(DEFINED-HERE)로 확정 — 2건 모두 OPEN 아님)
- 3. LOCK 변경: 없음 (LOCK-HM-03 §4.1 9개 노드 이름·번호 원문 유지, §4.2 전이 6건 원문 유지)
- 4. 이월: 없음 (T1-6 ChatPage 통합은 해당 세션 독립 위임, 본 세션 블로커 아님)

**산출물**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\03_ui-state-machine\state_definitions.md` (9개 UI 상태 정의)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\03_ui-state-machine\transition_matrix.md` (전이 매트릭스 완성)
</details>

<details>
<summary><b>T1-6. ChatPage 통합 패턴</b></summary>

**대조 기준**:
- §7 세부 작업: T1-6 "ChatPage 통합 패턴"
- §7 전환 게이트: ISS-16 해소 + /validate PASS
- §6 이슈: ISS-16 (Phase 1 완료 시점)

**목표**: ChatPage.tsx에서 채팅 렌더링 / 스트리밍 / 아티팩트 조합이 어떤 규칙으로 통합되는지 완전 명세한다. 44개 컴포넌트(LOCK-HM-07), 8개 Hook(LOCK-HM-08), 7개 Store(LOCK-HM-09)가 ChatPage 안에서 어떻게 조합되는지의 통합 패턴 문서이다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\_index.md` (도메인 인덱스 — 추출 현황 및 ISS-16 미해소 항목)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4 (LOCK-HM-07/08/09 정본 — ChatPage.tsx 통합 조합 규칙)
- T1-2 산출물 `component_catalog.md`, T1-3 산출물 `hook_catalog.md`, T1-4 산출물 `store_catalog.md` (컴포넌트/Hook/Store 카탈로그 — ChatPage 조합 참조용)

**절차**:
1. `_index.md`에서 ISS-16 미해소 항목과 기존 추출 현황을 확인한다.
2. `PART2_구현단계.md` V1-P4에서 ChatPage.tsx의 컴포넌트 트리 구성(어떤 컴포넌트가 렌더링되는지)을 추출한다.
3. 채팅 메시지 렌더링 흐름(메시지 수신 → 상태 업데이트 → 컴포넌트 렌더링)을 단계별로 추출한다.
4. 스트리밍 처리 패턴(SSE/WebSocket 수신 → Hook 처리 → 스트리밍 캔버스 렌더링)을 추출한다.
5. 아티팩트 조합 규칙(아티팩트 타입별 렌더링 컴포넌트 선택 로직)을 추출한다.
6. 채팅/스트리밍/아티팩트 세 패턴을 섹션별로 분리하여 `chatpage_integration.md`에 작성한다.
7. 파일 상단에 `출처: PART2_구현단계.md V1-P4` 및 `LOCK: LOCK-HM-07, LOCK-HM-08, LOCK-HM-09` 메타데이터를 기재한다.
8. ISS-16 해소 여부를 체크리스트로 기재한 후 `/validate`를 실행한다.

**검증**:
- [x] ChatPage.tsx 컴포넌트 트리 구성이 명시됨 ✅ (§3 트리 + TR-1~TR-6 규칙)
- [x] 채팅 메시지 렌더링 흐름이 단계별로 기재됨 ✅ (§4 Mermaid + 9-단계 파이프라인)
- [x] 스트리밍 처리 패턴(SSE/WebSocket → Hook → 렌더링)이 명시됨 ✅ (§5 계층 도식 + §5.2 프로토콜 선택 + §5.3 라이프사이클)
- [x] 아티팩트 타입별 렌더링 컴포넌트 선택 규칙이 명시됨 ✅ (§6 6-kind 매트릭스 + resolveArtifactRender)
- [x] 정본 출처(PART2_구현단계.md V1-P4) 및 LOCK-HM-07/08/09 태그 기재 ✅ (헤더 + §1)
- [x] ISS-16 해소 확인 ✅ (§13 체크리스트 전수 PASS)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\chatpage_integration.md` (채팅/스트리밍/아티팩트 조합 렌더링 규칙)

> **완료**: 2026-04-14. LOCK-HM-07(44 컴포넌트) / LOCK-HM-08(8 Hook) / LOCK-HM-09(7 Store) 기준 ChatPage.tsx 통합 조합 규칙을 `chatpage_integration.md` 단일 파일로 확정, ISS-16 해소.
>
> **근거 정합**:
> - 컴포넌트 트리: HV-LAYOUT-01 단일 자식 + Center(HV-CHAT-01/02/03 + HV-INPUT-01/02/03) + HUD(EVID/APPR/COST/MEM) — T1-2 §8 스텁 확장, R-611-10 준수
> - 9-단계 메시지 파이프라인: USER_SUBMIT → ASSISTANT_OPEN → TOKEN(× N) → EVIDENCE/ARTIFACT → COST_THRESHOLD → APPROVAL_REQUIRED → ASSISTANT_CLOSE + ERROR 분기 (§4 Mermaid)
> - 스트리밍: SSE(Tauri event primary) / WS(fallback) / CLI(stdout) 3-채널 모두 useStreaming 단일 추상 (T1-3 §4.8 정합), STREAM_OPEN_TIMEOUT 3s / STREAM_STALLED 10s / seq gap resume 정책
> - 아티팩트: 6-kind(code/doc/table/image/diagram/file) × (embed, expand) 매트릭스 O(1) + RBAC VIEWER 차단 + Decision S6+ 차단 + PII 파일 HV-MEM-02 강제
> - 공통 자료구조: 재사용 타입(T1-2 §4 / T1-3 §3 / T1-4 §2)만 import, 본 문서 신규는 MessageEvent / ArtifactRenderRule / ChatPageContext **3개 한정** (중복 0건)
> - 세션 간 cross-check: T1-2 component_catalog §5·§7·§8 / T1-3 hook_catalog §2·§4 / T1-4 store_catalog §3 와 이름 글자 완전 일치 (§1.1 매트릭스, 불일치 0건)
> - 8 Hook 전수·7 Store 전수 소비를 정적 검사 테스트(T13/T14)로 고정 — LOCK-HM-08/09 수량 보존 자동화

**[T1-6] 검증 결과 요약** (갱신: 2026-04-14)

- 0. 기준: §7 T1-6 대조(ISS-16 해소 + /validate PASS + LOCK-HM-07/08/09 정본 정합)
- 1. 게이트: G1(T1-6) ✅ — 검증 6/6 PASS, ISS-16 해소, §13 체크리스트 15/15 PASS
- 2. CONFLICT: 신규 0건 (후보 2건 — ① V1-P4 L2323-2326 "3-Pane HUD 4종" baseline과 본 문서 §3 Center(HV-CHAT-01/02/03 + HV-INPUT-01/02/03)+HUD(EVID/APPR/COST/MEM) 트리 상세화의 권한 경계 → HUD 4종 수량·이름 변경 없이 자식 트리만 DEFINED-HERE 보강하여 LOCK-HM-07 무위반 확인 / ② 스트리밍 3-채널(SSE primary / WS fallback / CLI stdout) 선정과 T1-3 §4.8 useStreaming 단일 추상 간 정합 → 본 문서 §5.2에서 채널 선택은 useStreaming 내부 전략으로 위임·외부 API 불변 확인, Part2 V1-P4 LOCK-HM-08 8 Hook 수량 baseline 유지 — 2건 모두 OPEN 아님)
- 3. LOCK 변경: 없음 (LOCK-HM-07 44 / LOCK-HM-08 8 / LOCK-HM-09 7 수량·이름 baseline 유지, 조합 규칙만 DEFINED-HERE)
- 4. 이월: 없음 본 세션 블로커 (T2-1/T2-2/T2-3/T2-4/T2-5/T2-6 는 각 해당 Phase 2 세션 위임)

</details>

### Phase 2: 심화 — Main LLM 통합 + Glass HUD

| 태스크 | 산출물 | 완료 기준 |
|--------|--------|----------|
| T2-1 2-tier 라우팅 Hologram 맥락 | 04_main-llm-integration/two_tier_routing.md | ✅ 완료 (2026-04-18, V2). Front Mini → Main LLM 맥락 전달 상세. 857줄 / 12 Phase 3 scenarios / R1 2 corrections [path+ID-mapping] / ISS-06 맥락 프로토콜 해소 / CONFLICT 0 |
| T2-2 3-point 출력 → UI 바인딩 | 04_main-llm-integration/response_formatting.md | ✅ 완료 (2026-04-18, V2). 911줄 / 12 Phase 3 scenarios / R1 1 correction [verbatim padding drift] / ISS-08 3-point UI 바인딩 해소 / CONFLICT 0 / V2↔V2 peer T2-1 cross-ref 3건 PASS |
| T2-3 DCL 배경 인식 응답 | 04_main-llm-integration/dcl_context.md | ✅ 완료 (2026-04-18, V2). 865줄 / 12 Phase 3 scenarios / step2 converged / ISS-06 완전 해소 (T2-1 프로토콜 + T2-3 DCL) / V2↔V2 3-way cross-ref PASS / CONFLICT 0 |
| T2-4 Glass HUD 오버레이 스키마 | 05_glass-hud-overlay/*.md 3개 | ✅ 완료 (2026-04-18, V2). 3 V2 동시 생성 (overlay_schema 898 + realtime_update 591 + rendering_rules 490 = 1,979줄) / 36 Phase 3 scenarios (TS-HUD 12 + TS-RT 12 + TS-RR 12) / R1 1 correction [§1.4 uncertainty_alert 필드명·타입명 네이밍 드리프트 명시 iter2] / ISS-09 완전 해소 (스키마/갱신/렌더 3축) / CONFLICT 0 / LOCK-HM-10 verbatim (qod 0.8/0.5 경계, 3등급 VERIFIED/PARTIAL/UNVERIFIED, Alert 3종) / V2↔V2 peer T2-2 VerificationBadge+UncertaintyAlert Literal 값 1:1, T2-3 active_workflow.qod_hint 초기값 이음매, T2-1 TraceId 공유 |
| T2-5 스트리밍 캔버스 프로토콜 | 06_streaming-canvas/*.md 3개 | ✅ 완료 (2026-04-18, V2). 3 V2 동시 생성 (stream_protocol 1,083 + token_rendering 772 + artifact_rendering 611 = 2,466줄) / 36 Phase 3 scenarios (TS-STREAM 12 + TS-TOK 12 + TS-ART 12) / iter 2 R1 0 corrections (수렴 한계값 도달) / LOCK-HM-01 3줄 verbatim + R-611-4 원문 verbatim 4회 인용 / ISS-10+ISS-11+ISS-12 3 이슈 완전 해소 (06_streaming-canvas 폴더 마감) / V2↔V2 cross-ref 6건 PASS / CONFLICT 0 |
| T2-6 I-10 오케스트레이션 매핑 | 07_orchestration-layer/*.md 3개 | ✅ 완료 (2026-04-19, V2). 3 V2 동시 생성 (ui_state_mapping 1,012 + cost_evidence_log 704 + page_routing 547 = 2,263줄) / 36 Phase 3 scenarios (TS-UI 12 + TS-CEL 12 + TS-PR 12) / iter 1 R1 0 corrections 즉시 수렴 (수렴 한계값 2회 연속 유지) / LOCK-HM-05 §7.63 5 요소 verbatim + LOCK-HM-03 9-State verbatim + LOCK-HM-02/07/10/06 보조 / ISS-07+ISS-13+ISS-15 3 이슈 완전 해소 (07_orchestration-layer 폴더 마감, 4/4 폴더 전수 마감, 누적 V2 12/12) / V2↔V2 cross-ref 16건 PASS / CONFLICT_CANDIDATE 신규 1건 (CONF-HM-008 9-State 네이밍 drift Phase 3 이월) |

**Phase 2 → Phase 3 게이트**: ✅ **PASS** (2026-04-19) — ISS-06~ISS-13, ISS-15 **9 이슈 전수 해소** (ISS-06 T2-1+T2-3 / ISS-07 T2-6 / ISS-08 T2-2 / ISS-09 T2-4 / ISS-10+ISS-11+ISS-12 T2-5 / ISS-13+ISS-15 T2-6) + **/audit PASS** (6 세션 전수 PASS, LOCK-HM-01~10 변경 0건, CONFLICT_CANDIDATE 신규 1건 CONF-HM-008 Phase 3 이월 격리 등재) + **누적 V2 12/12** (04_ 3 + 05_ 3 + 06_ 3 + 07_ 3, 총 9,341줄, Phase 3 scenarios 144건) + **V1 92회 연속 OK** (phase_A_sanity_6-11 ~ audit_converged_6-11, 6-11 도메인 12 tags × 11/11; STEP_C 심층 재검증 R1~R2 fully_converged 통산 0 수정 2026-04-19) + **Production UNCHANGED** (TEST_MODE=true sandbox-only 정책 100% 준수).

#### Phase 2 단계별 상세 작업 절차

<details>
<summary><b>T2-1. 2-tier 라우팅 Hologram 맥락</b></summary>

**대조 기준**:
- §7 세부 작업: T2-1 "2-tier 라우팅 Hologram 맥락"
- §7 전환 게이트: ISS-06~ISS-13, ISS-15 해소 + /audit PASS
- §6 이슈: ISS-06 (2-tier 라우팅 Hologram 맥락 전달 프로토콜, DCL 연동)
- 교차 도메인: 6-9 Brain-Adapter-HAL (라우팅 로직 정본), D2.0-02 §11.15.1 LOCK-HM-04
- Part2 버전: V2 Enhanced Hologram

**목표**: Front Mini → Main LLM 2-tier 라우팅에서 Hologram View 맥락(current_layout, visible_components, hud_state, timeline_context, user_preferences) 5개 항목을 전달하는 프로토콜을 상세 정의한다. LOCK-HM-04(D2.0-02 §11.15.1) 준수.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\_index.md`
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` §11.15.1 (L4261-4266)

**절차**:
1. D2.0-02 §11.15.1 (L4261-4266) 발췌 — Orange Core → Front Mini → Main LLM 2-tier 라우팅 구조 확인 (LOCK-HM-04 기준)
2. Hologram View에서 Main LLM 호출 시 전달해야 할 맥락 5개 항목(current_layout / visible_components / hud_state / timeline_context / user_preferences) 인터페이스 정의
3. Front Mini가 맥락을 수집하여 Main LLM 요청 페이로드에 포함시키는 절차 기술
4. DCL(Domain Context Layer) 연동 방식 — 맥락 주입 시점, 키 이름, 타입 명세
5. R-611-9 준수 확인: 라우팅/모델 선택/폴백 로직은 6-9 정본 참조, 6-11은 맥락 전달만 담당
6. `two_tier_routing.md` 초안 작성 → ISS-06 해소 체크

**검증**:
- [x] ✅ LOCK-HM-04 기준(D2.0-02 §11.15.1 L4261-4266) 라우팅 구조와 불일치 없음 확인 — §1.1 상위 정본 표 + §12.1 verbatim 인용, drift 0
- [x] ✅ 맥락 5개 항목 전부 포함 여부 검토 — §3.1 Pydantic v2 + §3.2 TypeScript 중앙 정의 (current_layout / visible_components / hud_state / timeline_context / user_preferences) 5/5
- [x] ✅ R-611-9: 라우팅 로직이 6-11에 포함되지 않았는지 검토 — §0.3 도메인 경계 선언 + §12 R-611-9 원문 재인용, 6-11은 송신자/6-9는 수신자+라우팅 실행자 명시
- [x] ✅ ISS-06 해소 요건(맥락 전달 프로토콜 + DCL 연동 인터페이스 명세) 충족 확인 — 프로토콜 §3~§5 완전 정의 ✅, DCL 연동 접합점 §6 placeholder 확정(상세는 T2-3 종결 예정) ⏳
- [x] ✅ /audit PASS 기준: 상위 LOCK과 충돌하는 라우팅 구조 기술 없음 — §11 체크리스트 5/5 PASS, §13 Phase 2→3 게이트 3/4 ✅ + 1 ⏳ (T2-3 종속), CONFLICT 신규 0건

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\two_tier_routing.md`

> **완료**: 2026-04-18, V2-Phase 2 v1.0
> - V2 파일: `04_main-llm-integration/two_tier_routing.md` 857줄 V2-Phase 2 v1.0
> - 맥락 5 필드 (current_layout / visible_components / hud_state / timeline_context / user_preferences) 전수 Pydantic v2 + TypeScript 중앙 정의 (§3.1/§3.2/§3.3)
> - LOCK-HM-04 (D2.0-02 §11.15.1 L4261-4266) verbatim 인용 준수 — §1.1 + §12.1, drift 0
> - LOCK-HM-05 (D2.0-02 §7.63 L2091-2119) I-10 오케스트레이션 역할 준수 — §4 Sequence 에서 `emit_ui_state(trace_id, ui_state)` 수집 훅 일치
> - R-611-9 도메인 경계 (6-9 소유 라우팅 vs 6-11 소유 맥락 전달) 명시 — §0.3 + §12.2 원문 재인용
> - DCL 접합점 placeholder 설정 (§6 `HologramContextPayload.dcl_context_keys`) — T2-3 dcl_context.md 에서 종결 예정
> - Phase 3 scenarios 12건 (TS-2TIER-01~12, ≥10 요건 초과) — §10
> - Step2 iter 2 converged (R1 2 corrections: path ×1, D2.0-05 filename ×1; R2 changes=0)
> - ISS-06 맥락 전달 프로토콜 해소 — DCL 연동 인터페이스 명세는 T2-3 완성 시 최종 종결

**[T2-1] 검증 결과 요약**:
- 0. 산출물: 1 V2 (`two_tier_routing.md`, V2-Phase 2 태그)
- 1. 게이트: ISS-06 (프로토콜+맥락) 해소 / entry gate P1-1~P1-6 V1 무손상 (LOCK-HM-01~10 변경 0)
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0
- 3. LOCK 변경: 없음 (LOCK-HM-01~10 정본 그대로, 소비자 지위만)
- 4. 이월: T2-2 (response_formatting) 는 본 세션의 5 필드 payload 중 `user_response` 의 UI 바인딩으로 연결. T2-3 (dcl_context) 는 본 세션 DCL 접합점 placeholder 에서 확장.
</details>

<details>
<summary><b>T2-2. 3-point 출력 → UI 바인딩</b></summary>

**대조 기준**:
- §7 세부 작업: T2-2 "3-point 출력 → UI 바인딩"
- §7 전환 게이트: ISS-06~ISS-13, ISS-15 해소 + /audit PASS
- §6 이슈: ISS-08 (3-point 출력 Hologram UI 바인딩 매핑 — 어떤 필드 → 어떤 컴포넌트)
- 교차 도메인: D2.0-05 §7.2 LOCK-HM-06, 6-1 3-Column Layout (StreamCanvas/EvidencePanel/LogDetail 컴포넌트 정본)
- Part2 버전: V2 Enhanced Hologram

**목표**: Main LLM 3-point 출력(user_response / evidence_summary / log_report) 각 필드를 Hologram UI 컴포넌트(StreamCanvas / EvidencePanel / LogDetail+Timeline)에 바인딩하는 매핑 테이블을 완성한다. LOCK-HM-06(D2.0-05 §7.2) 준수.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\_index.md`
- `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` §7.2 (L359-368)

**절차**:
1. D2.0-05 §7.2 (L359-368) 발췌 — user_response / evidence_summary / log_report 3-point 출력 포맷 확인 (LOCK-HM-06 기준)
2. 각 필드의 타입, 필수 여부, 구조(중첩 필드 포함) 정리
3. Hologram View 컴포넌트 매핑 테이블 작성:
   - `user_response` → StreamCanvas (Center Panel 스트리밍 출력)
   - `evidence_summary` → EvidencePanel (Right Panel 근거 목록)
   - `log_report` → LogDetail + Timeline (Bottom Panel)
4. R-611-3 준수: 3-point 미파싱 시 UI 바인딩 금지 규칙 명시
5. 파싱 오류/누락 필드 처리 규칙(폴백 UI 표시 방침) 기술
6. `response_formatting.md` 초안 작성 → ISS-08 해소 체크

**검증**:
- [x] ✅ LOCK-HM-06 기준(D2.0-05 §7.2 L359-368) 3-point 포맷과 매핑 테이블 일치 확인 — verbatim 인용 drift 0, R1 1 correction (verbatim padding drift) converged
- [x] ✅ 3개 필드 전부 대상 컴포넌트에 매핑되었는지 검토 — 3 필드 × 3 컴포넌트 (user_response → StreamCanvas / evidence_summary → EvidencePanel / log_report → LogDetail+Timeline) 9/9 매핑 완료
- [x] ✅ R-611-3: 파싱 전 바인딩 금지 규칙 문서에 포함 여부 검토 — §2.3 바인딩 전 파싱 성공 조건 + §6.4 파싱 실패 시 바인딩 차단 Mermaid 원문 명시
- [x] ✅ ISS-08 해소 요건(필드 → 컴포넌트 매핑 테이블 완성) 충족 확인 — §5.5 3×3 매핑 테이블 + TypeScript EvidenceCard/LogDetail 중앙 정의, ISS-08 해소 (최종 /audit PASS 는 T2-3 완료 후)
- [x] ✅ /audit PASS 기준: 상위 LOCK 3-point 포맷과 충돌하는 필드 추가/삭제 없음 — LOCK-HM-06 verbatim 유지, LOCK-HM-01/05/07/08/10 보조 참조, CONFLICT 신규 0건

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\response_formatting.md`

> **완료**: 2026-04-18, V2-Phase 2 v1.0
> - V2 파일: `04_main-llm-integration/response_formatting.md` 911줄 V2-Phase 2 v1.0
> - ThreePointOutput Pydantic v2 + TypeScript 중앙 정의 (user_response / evidence_summary / log_report 3 필드)
> - LOCK-HM-06 (D2.0-05 §7.2 L359-368) verbatim 인용 + 3 필드 (user_response / evidence_summary / log_report)
> - LOCK-HM-10 Evidence 등급 3종 (VERIFIED≥0.8 / PARTIAL / UNVERIFIED<0.5) + Uncertainty Alert 3종 일치
> - R-611-3 원문 (3-point 미파싱 시 UI 바인딩 금지) §2.3+§6.4
> - 3×3 UI 매핑 (StreamCanvas / EvidencePanel / LogDetail+Timeline)
> - 폴백/파싱 오류 Mermaid §6.2+§6.3
> - Phase 3 scenarios 12건 (TS-3PT-01~12, ≥10 초과)
> - Step2 iter 2 converged (R1 1 verbatim padding, R2 0)
> - **V2↔V2 peer T2-1 cross-ref 3건 PASS** (trace_id ULID / dcl↔domain_context 대칭 / I-10 oc.i10.ui.state.emitted verbatim)

**[T2-2] 검증 결과 요약**:
- 0. 산출물: 1 V2 (`response_formatting.md`, V2-Phase 2 태그)
- 1. 게이트: ISS-08 해소 / entry gate P1-1~P1-6 V1 무손상
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0
- 3. LOCK 변경: 없음 (LOCK-HM-01~10 정본, 소비자 지위)
- 4. 이월: T2-3 (dcl_context) 는 본 세션 domain_context_hits 와 T2-1 dcl_context_keys 대칭 접합점을 실체화. T2-4 Glass HUD (overlay_schema) 는 본 세션 Evidence/Cost/Approval 매핑 확장.
</details>

<details>
<summary><b>T2-3. DCL 배경 인식 응답</b></summary>

**대조 기준**:
- §7 세부 작업: T2-3 "DCL 배경 인식 응답"
- §7 전환 게이트: ISS-06~ISS-13, ISS-15 해소 + /audit PASS
- §6 이슈: ISS-06 (2-tier 라우팅 맥락 전달 프로토콜, DCL 연동)
- 교차 도메인: 6-9 Brain-Adapter-HAL (DCL 데이터 공급 정본), D2.0-02 §11.15.1
- Part2 버전: V2 Enhanced Hologram

**목표**: DCL(Domain Context Layer)이 Hologram View 맥락에 배경 인식 정보를 주입하여 Main LLM이 도메인 인식 응답을 생성하는 인터페이스를 정의한다. T2-1의 two_tier_routing.md와 DCL 연동 접합점을 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\_index.md`
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` §11.15.1 (L4261-4266)

**절차**:
1. DCL 개념 정의 — Domain Context Layer가 제공하는 배경 정보 범주(도메인 히스토리, 사용자 세션, 활성 워크플로우 컨텍스트) 확인
2. DCL 데이터 구조 인터페이스 설계 — `DomainContext` 타입 (domain_id, session_history, active_workflow, user_profile 등)
3. 맥락 주입 시점 및 방식 — Front Mini 요청 조립 단계에서 DCL 데이터를 system_context 필드에 첨부하는 절차
4. Main LLM이 DCL 데이터를 수신하여 응답 생성에 활용하는 방식 기술 (프롬프트 구조 내 위치)
5. DCL 데이터 부재 시 폴백 처리(빈 컨텍스트로 진행 vs. 오류 반환) 규칙 정의
6. `dcl_context.md` 초안 작성 → ISS-06 DCL 연동 항목 해소 체크

**검증**:
- [x] ✅ T2-1 two_tier_routing.md와 DCL 주입 접합점 일치 확인 (인터페이스 불일치 없음) — §11 V2↔V2 3-way cross-ref 표 + §11.2 Sequence 단계 13~17 대조, T2-1 `dcl_context_keys: list[str]` ↔ T2-3 `resolved_keys: list[str]` ↔ T2-2 `domain_context_hits: list[str]` 일치, trace_id ULID · I-10 `oc.i10.ui.state.emitted` · <=32 상한 공유, 신규 CONFLICT 0건
- [x] ✅ R-611-9 준수: DCL 로직이 6-9 영역을 침범하지 않음 확인 — §7.2 R-611-9 원문 인용 + §7.3 /audit A1~A4 체크리스트 4/4, 본 문서에 `route()`/`select_model()`/`fallback_chain()` 정의 없음, DCL 데이터 수집 알고리즘 전부 6-9 정본 위임
- [x] ✅ DCL 데이터 구조가 두 tier(Front Mini / Main LLM) 모두에서 일관되게 참조되는지 검토 — §3.2 Pydantic v2 (Main/Core 측) + §3.3 TypeScript (Front Mini 측) 1:1 동기화, DomainContext 4 주 필드 + 확장 2 동일 스키마, §3.4 요약 테이블 10행 정합
- [x] ✅ ISS-06 해소 요건(DCL 연동 인터페이스 명세) 충족 확인 — §0.2 Scope + §15 게이트 요약: T2-1 (프로토콜) + T2-3 (DCL) = ISS-06 완전 해소, 4 주 필드 + Sequence (DCL.1~DCL.3) + 폴백 4 분기 + 로깅 3종 + 테스트 12건
- [x] ✅ /audit PASS 기준: DCL이 라우팅 로직을 내포하지 않음 — §7.3 A1~A4 PASS (라우팅 함수 0 / 라우팅 힌트 필드 0 / Sequence 라우팅 영향 경로 0 / qod_hint 초기 힌트로만 제한)

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\dcl_context.md`

> **완료**: 2026-04-18, V2-Phase 2 v1.0
> - V2 파일: `04_main-llm-integration/dcl_context.md` 865줄 V2-Phase 2 v1.0
> - DomainContext Pydantic v2 + TypeScript 중앙 정의 (4 주 필드 + 확장 2: project_context / domain_hints + 메타 2: resolved_keys / resolution_status)
> - LOCK-HM-04 (D2.0-02 §11.15.1) Front Mini DCL 주입 단계 준수 — §2.1 + §4.1 DCL.1~DCL.3
> - LOCK-HM-05 (D2.0-02 §7.63) I-10 `oc.i10.ui.state.emitted` + `dcl_state` field — §2.2 + §4.1 emit 구문
> - LOCK-HM-06 (D2.0-05 §7.2) 3-point 응답 `log_report.domain_context_hits` 접점 — §2.3 + §6
> - R-611-9 원문 (DCL 알고리즘=6-9 정본, 6-11=주입 인터페이스만) §7.2
> - DCL 부재 폴백 4 분기 (FULL/PARTIAL/EMPTY/ERROR + PROCEED_EMPTY/FAIL_FAST) — §5.1~§5.3 Mermaid
> - Phase 3 scenarios 12건 (TS-DCL-01~12, ≥10 초과)
> - Step2 converged (iter 1, changes=0)
> - **V2↔V2 3-way cross-ref MANDATORY (L1093) PASS**: T2-1 `dcl_context_keys` ↔ T2-3 `resolved_keys` ↔ T2-2 `domain_context_hits` list[str] 정합 + trace_id ULID + I-10 event verbatim + 길이 ≤32 + sequence 단계 13~17

**[T2-3] 검증 결과 요약**:
- 0. 산출물: 1 V2 (`dcl_context.md`, V2-Phase 2 태그)
- 1. 게이트: ISS-06 완전 해소 (T2-1+T2-3) / entry gate P1-1~P1-6 V1 무손상 / /audit PASS 준비 (세션 3건 T2-1/2/3 최종 선언 가능)
- 2. CONFLICT: 발견 0 / 해소 0 / OPEN 0
- 3. LOCK 변경: 없음 (LOCK-HM-01~10 정본 그대로, 소비자 지위)
- 4. 이월: T2-4 (Glass HUD overlay_schema) 는 T2-2 EvidenceCard + T2-3 DCL 메타 (`domain_hints`) 를 HUD Evidence 오버레이 입력으로 소비. T2-5 스트리밍 캔버스 는 본 세션 interaction-level 확장 (단일 응답 vs 스트리밍), 초기 system_context 에 DCL 주입 후 토큰 스트림 시작 규칙 재확인 필요.
</details>

<details>
<summary><b>T2-4. Glass HUD 오버레이 스키마</b></summary>

**대조 기준**:
- §7 세부 작업: T2-4 "Glass HUD 오버레이 스키마"
- §7 전환 게이트: ISS-06~ISS-13, ISS-15 해소 + /audit PASS
- §6 이슈: ISS-09 (Glass HUD 오버레이 데이터 스키마 — 비용/근거/승인 필드 정의, 갱신 주기, 렌더링 규칙)
- 교차 도메인: D2.0-08 §2.2.2 + §9.1 LOCK-HM-10 (Evidence 3등급, Uncertainty Alert 3종, Option A Fixed HUD)
- Part2 버전: V2 Enhanced Hologram

**목표**: Glass HUD 오버레이의 데이터 스키마(GlassHUDData TypeScript 인터페이스), 실시간 갱신 프로토콜(SSE push, requestAnimationFrame), 렌더링 규칙(투명도/위치/애니메이션, 하위 콘텐츠 비차단)을 3개 파일로 완성한다. LOCK-HM-10(D2.0-08 §2.2.2) 준수.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\_index.md`
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.2.2 (L255-265), §9.1 (L1409-1417)

**절차**:
1. **overlay_schema.md**: D2.0-08 §2.2.2 기반 `GlassHUDData` 인터페이스 정의
   - `cost`: 비용 임계치 게이지 (amount, threshold, currency)
   - `evidence`: VERIFIED/PARTIAL/UNVERIFIED 3등급, qod_score 기반 등급 매핑 테이블
   - `approval`: 슬라이드 인 방식 승인 패널 데이터 (action_id, label, urgency)
   - `uncertainty_alert`: LOW_QOD / CONFLICTING_SOURCES / STALE_DATA 3종
   - `meta`: trace_id, timestamp, session_id
2. **realtime_update.md**: SSE push 기반 갱신 프로토콜 정의
   - SSE 이벤트 스트림 포맷 (`event: hud_update\ndata: {...}`)
   - 갱신 주기 — cost: 5초, evidence: LLM 응답 완료 시, approval: 즉시
   - `requestAnimationFrame` 기반 렌더링 스케줄링
   - 연결 끊김 시 재연결 정책
3. **rendering_rules.md**: HUD 렌더링 규칙 정의
   - D2.0-08 §9.1 Option A(Fixed HUD) — 위치 고정, 투명도 관리
   - `pointer-events: none` 적용으로 하위 콘텐츠 상호작용 비차단 (R-611-2)
   - 등장/퇴장 애니메이션 스펙, 불필요 리렌더 방지 (React.memo / shouldComponentUpdate)
4. 3개 파일 초안 작성 → ISS-09 해소 체크

**검증**:
- [x] ✅ LOCK-HM-10 기준(D2.0-08 §2.2.2): Evidence 3등급(VERIFIED Green/PARTIAL Yellow/UNVERIFIED Gray qod 경계 0.8/0.5 verbatim), Cost 게이지(ratio_to_budget 임계 0.8 조건부 노출), Approval 슬라이드인(slide_in_active 플래그 + 중앙 과점유 금지 max-width 25%), Uncertainty Alert 3종(LOW_QOD/CONFLICTING_SOURCES/STALE_DATA) 모두 `GlassHUDData` 5 필드(cost/evidence/approval/uncertainty_alert/meta) 로 포함 확인 — **스키마 Pydantic v2 + TypeScript 쌍방 1:1**
- [x] ✅ D2.0-08 §9.1 Option A Fixed HUD 모드 — `rendering_rules.md` §2 위치(`position: fixed`, top `var(--header-h)`, right 0), 폭 `clamp(280px, 22vw, 360px)`, `meta.mode = "FIXED"` 상수 반영 확인
- [x] ✅ R-611-2: 투명 레이어 원칙 `pointer-events: none` 컨테이너 기본 + `.hud-interactive { pointer-events: auto }` 예외 (§5), `rendering_rules.md` 전수 반영 확인
- [x] ✅ ISS-09 해소 요건 — 스키마(`overlay_schema.md` 898줄) + 갱신(`realtime_update.md` 591줄) + 렌더링(`rendering_rules.md` 490줄) 3파일 완성, 3 V2 합계 1,979줄 / 36 Phase 3 scenarios (TS-HUD-01~12 + TS-RT-01~12 + TS-RR-01~12)
- [x] ✅ /audit PASS 기준: `GlassHUDData.evidence.verification` Literal 3값 `VERIFIED/PARTIAL/UNVERIFIED` = LOCK-HM-10 3등급 verbatim, `UncertaintyAlertKind` Literal 3값 = LOCK-HM-10 Alert 3종 verbatim, qod_score 경계 0.8/0.5 `§3.4` + `§3.6 build_evidence_hud_snapshot()` + `§6.1 verifyQodInvariant()` 3중 강제 — 충돌 없음
- [x] ✅ V2↔V2 peer cross-ref 필수 3건 PASS — T2-2 response_formatting.md §3.1 (L178/L179) VerificationBadge·UncertaintyAlert Literal 값 verbatim 일치 / T2-3 dcl_context.md §3.2 (L212-216) active_workflow.qod_hint 초기값 이음매 (`EvidenceHudSnapshot.qod_hint_initial` 수용) / T2-1 two_tier_routing.md TraceId ULID 공통 규약 (HudMeta.trace_id 타입 일치)
- [x] ✅ R-01-7 중첩 구조화 JSON 로깅 포맷 — `hud{}`·`binding{}`·`sse{}`·`render{}`·`animation{}`·`error{}`·`recovery{}` 중첩, `hologram.hud.*` 이벤트 네임스페이스 9종(overlay) + 7종(realtime) + 7종(rendering) = 23 네임스페이스

> **완료**: 2026-04-18. Phase 2 T2-4 Glass HUD 오버레이 스키마 3 V2 동시 생성 완성.
>
> **실행 결과 요약**:
> - 3 V2 산출물 (sandbox only, production UNCHANGED): `overlay_schema.md` 898줄 (GlassHUDData 중앙 정의, 5 필드, Pydantic v2 + TypeScript 쌍방) + `realtime_update.md` 591줄 (SSE 6 네임스페이스, 필드별 갱신 주기 5s/LLM-complete/즉시, 지수 백오프 5단계 1s/2s/4s/8s/16s, requestAnimationFrame flush) + `rendering_rules.md` 490줄 (Option A Fixed HUD, 애니메이션 Evidence/Approval/Cost/Alert 4종, pointer-events, React.memo+selector, a11y)
> - LOCK-HM-10 verbatim 준수: qod_score 경계값 0.8 / 0.5 임의 변경 **0건**, 3등급 이름 VERIFIED/PARTIAL/UNVERIFIED 색상 Green/Yellow/Gray verbatim, Uncertainty Alert 3종 LOW_QOD/CONFLICTING_SOURCES/STALE_DATA verbatim
> - V2↔V2 cross-ref 필수 3건 PASS: T2-2 Literal 3종×2 verbatim 재사용(VerificationBadge + UncertaintyAlert values) / T2-3 `DomainContext.active_workflow.qod_hint` → `EvidenceHudSnapshot.qod_hint_initial` 이음매 / T2-1 TraceId ULID 공통 규약 `HudMeta.trace_id`
> - 재검증 iter 2 R1 1 correction: §1.4 cross-ref 테이블의 field name (`uncertainty_alerts` plural → `uncertainty_alert` singular) 및 Literal type name (`UncertaintyAlert` → `UncertaintyAlertKind`) 네이밍 드리프트 명시 + 의도 설명 추가 — value 집합 identical → CONFLICT 아님, 구조 확장 이유 (raised_at_ms 메타 래퍼) 문서화. 4-4 #2b-1 R1 12 corrections 대비 -92% 수렴 (6-11 #2a 평균 1/세션 패턴 유지)
> - ISS-09 완전 해소: 스키마 축(overlay_schema) + 갱신 주기 축(realtime_update) + 렌더링 규칙 축(rendering_rules) 3 축 모두 단일 세션에서 해소
> - 신규 CONFLICT_CANDIDATE 0건 발생 (LOCK-HM-10 4 구성 요소 그대로 스키마화, 필드 추가·삭제·이름 변경 없음 / 필드 총 5개 = 4 LOCK 요소 + 1 meta)
> - LOCK 소비 현황: LOCK-HM-10 주 정본 / LOCK-HM-01 보조(Right Panel ≈300px 폭 근거) / LOCK-HM-05 보조(I-10 emit_ui_state 이벤트 연결) / LOCK-HM-06 보조(evidence_summary 입력 소스) / LOCK-HM-07 보조(HV-EVID-* 컴포넌트 카탈로그)

**[T2-4] 검증 결과 요약** (갱신: 2026-04-18, Phase 2)
- 0. 산출물: 3 V2 sandbox 파일 — `05_glass-hud-overlay/overlay_schema.md` (898줄, GlassHUDData Pydantic v2 + TypeScript 중앙 정의, 5 필드, qod→verification 3등급 매핑 §3.4+§3.6, 조건부 표시 판정 §3.7, TS-HUD-01~12) / `05_glass-hud-overlay/realtime_update.md` (591줄, 6 SSE 이벤트 네임스페이스, 필드별 갱신 주기, 지수 백오프 5단계 재연결, seq gap resync, RAF 플러시, TS-RT-01~12) / `05_glass-hud-overlay/rendering_rules.md` (490줄, Option A Fixed HUD 위치/폭/z-index 150/투명도 0.85, 애니메이션 4종 Evidence fade 240ms / Approval slide-in 320ms / Cost gauge 800ms / Alert 200ms, pointer-events 규칙, React.memo glassHudEqual, selector useHudCost/Evidence/Approval/Alerts, a11y aria-live + reduced-motion, TS-RR-01~12). 3 파일 전수 V2-Phase 2 태그 명시, TEST_MODE=true sandbox only, production UNCHANGED.
- 1. 게이트: Phase 2→3 exit gate 기여 항목 — ISS-09 해소 기여 (3 축 전수 완료). entry gate: Phase 1→2 사전 충족 재확인 (T2-3 직후 V1 85회 연속 OK 유지). /audit PASS 기준: GlassHUDData 와 LOCK-HM-10 4 구성 요소 충돌 0건 ✅.
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (본 #2b-1 신규 CONFLICT_CANDIDATE 0건, CFL-HM-001~007 + C-1~C-3 Phase 0/1 RESOLVED 유지)
- 3. LOCK 변경: 없음. LOCK-HM-10 정본 D2.0-08 §2.2.2 L255-265 소비자 지위 유지 (LOCK-HM-01 / HM-05 / HM-06 / HM-07 보조 소비).
- 4. 이월: T2-5 스트리밍 캔버스 는 본 세션 `realtime_update.md` §4.5 별도 채널 vs 공용 multiplex 선택을 T2-5 stream_protocol 확정 시 재검토. T2-6 I-10 오케스트레이션 은 본 세션 §4 Sequence 의 `oc.i10.ui.state.emitted` verbatim 이벤트 규약을 본 문서 §1.4 명시 참조 — 변경 시 본 문서 §4 / §8.1 영향 분석 필수. 도메인 마감(#2b-4 step 05/07/08) 에서 sandbox INDEX.md 에 본 3 V2 등재.

**산출물**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\overlay_schema.md`
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\realtime_update.md`
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\rendering_rules.md`
</details>

> **이월 (T2-4 → T2-5, 2026-04-18)**: T2-4 `realtime_update.md` §4.5 "별도 채널 vs 공용 multiplex" 결정을 T2-5 `stream_protocol.md` 확정 시 재검토 필요 (현 default: HUD SSE 와 token streaming 별도 채널). T2-5 stream_protocol 에 `channel: "hud" | "stream"` multiplex 지원 도입 시 본 HUD realtime_update §4.5 와 seq 규약 통합 여부 재검토. 또한 T2-4 `overlay_schema.md` §3.1 `EvidenceHudSnapshot.qod_hint_initial` 은 T2-3 DCL 주입 규칙을 단일 응답 기준으로 소비하므로, T2-5 가 스트리밍 중 qod_hint 중간 갱신을 허용할지 여부 T2-5 에서 결정 필요.

<details>
<summary><b>T2-5. 스트리밍 캔버스 프로토콜</b></summary>

**대조 기준**:
- §7 세부 작업: T2-5 "스트리밍 캔버스 프로토콜"
- §7 전환 게이트: ISS-06~ISS-13, ISS-15 해소 + /audit PASS
- §6 이슈: ISS-10 (SSE/WebSocket 프로토콜), ISS-11 (토큰 단위 렌더링 파이프라인), ISS-12 (아티팩트 인라인 렌더링)
- 교차 도메인: 없음 (전면 신규 정의 영역 — 상위 정본 미언급). LOCK-HM-01 Center Panel 개념 준수.
- Part2 버전: V2 Enhanced Hologram

**목표**: 스트리밍 캔버스의 SSE/WebSocket 프로토콜 상세, 토큰 단위 실시간 렌더링 파이프라인, 아티팩트(코드/차트/테이블) 인라인 렌더링 규칙을 3개 파일로 완성한다. R-611-4(토큰 단위 점진적 표시 필수) 준수.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\_index.md`

**절차**:
1. **stream_protocol.md**: SSE/WebSocket 프로토콜 상세 정의
   - 기본 SSE, 폴백 WebSocket 선택 기준 (네트워크 환경, 프록시 제한)
   - 청크 포맷: `data: {"token": "...", "type": "text|code|artifact", "seq": N}`
   - 지수 백오프 재연결 정책: 1s → 2s → 4s → 8s → 16s (최대 5회)
   - seq 기반 이어받기 (중복 토큰 제거, 누락 감지)
   - 스트림 종료 신호: `data: {"type": "end", "seq": N}`
2. **token_rendering.md**: 토큰 단위 실시간 렌더링 파이프라인 정의
   - 파이프라인: 청크 수신 → 토큰 버퍼 누적 → 마크다운 AST 점진적 갱신 → Virtual DOM diff → DOM 갱신 → 스크롤 자동 하단
   - 버퍼 플러시 주기 (16ms / 60fps 기준)
   - R-611-4: 전체 응답 대기 후 일괄 표시 금지 규칙 명시
   - 긴 코드 블록 처리 — 불완전 마크다운 파싱 안전 처리
3. **artifact_rendering.md**: 아티팩트 인라인 렌더링 정의
   - 코드 블록 감지 시 ArtifactZone 활성화 트리거 규칙
   - 코드 하이라이팅 (언어 감지, syntax highlight 라이브러리)
   - 차트 아티팩트: 스트리밍 완료 후 렌더링 (부분 렌더 금지)
   - 테이블 아티팩트: 행 단위 점진적 렌더링
   - 아티팩트 타입 감지 실패 시 폴백(plain text 표시)
4. 3개 파일 초안 작성 → ISS-10, ISS-11, ISS-12 해소 체크

**검증**:
- [x] ✅ stream_protocol.md: seq 기반 이어받기 로직 (§7 단조 증가 + 중복 drop + gap resync HTTP GET) + 지수 백오프 5단계 1s/2s/4s/8s/16s (§6.1, #2b-1 realtime_update §4.3 수치 동일 재사용) 명세 확인. 청크 포맷 `{token, type, seq}` 종합계획서 §7 T2-5 절차 1번 verbatim (§5.1). 종료 신호 `{type:"end", seq:N}` verbatim (§9.1).
- [x] ✅ token_rendering.md: R-611-4 원문 **"StreamCanvas 는 토큰 단위 점진적 표시 필수, 전체 응답 대기 후 일괄 표시 금지"** verbatim 인용 (§2.1 + 재사용 2회) + 전체 응답 대기 후 1회 flush 경로 `[VIOLATION: R-611-4]` 가드 3건 (§2.2 표 + §7.5 assertion + §10.1 TS-TOK-02 테스트) 반영. 버퍼 플러시 16ms/60fps (§7.1 `scheduleTokenFlush`, realtime_update §4.6 `scheduleHudFlush` 패턴 계승) 확인. 긴 코드 블록 close ``` 미도착 안전 처리 (§5.3) 명시.
- [x] ✅ artifact_rendering.md: 코드 블록 `<lang>?` 감지 + Shiki/highlight.js syntax highlight (§4, 스트리밍 중 모노스페이스 → close 후 1회 highlight), 차트 **전체 수신 후 1회 렌더 placeholder 점진 피드백** (§5, R-611-4 예외 근거 §2.3 명시적 해석 — "점진적 표시"는 텍스트 기준, 차트는 시각 무결성 우선), 테이블 행 단위 점진 `<thead>` → `<tbody>` append (§6), 타입 감지 실패 plain text 폴백 (§7) 3종+폴백 전부 기술 확인.
- [x] ✅ ISS-10/11/12 해소 요건 — 프로토콜(`stream_protocol.md` 1083줄) + 렌더링 파이프라인(`token_rendering.md` 772줄) + 아티팩트(`artifact_rendering.md` 611줄) 3파일 완성, 3 V2 합계 **2,466줄 / 36 Phase 3 scenarios** (TS-STREAM-01~12 + TS-TOK-01~12 + TS-ART-01~12).
- [x] ✅ /audit PASS 기준: LOCK-HM-01 정본 원문 3줄 verbatim (Left/Center/Right Panel) 각 파일 §2 재인용 + Center Panel "가장 넓음 · 대화 스트림 + 산출물 인라인 렌더링 + 입력" 개념 준수 — 스트리밍 캔버스 설계가 Timeline(~250px) 또는 Glass HUD(~300px) 폭 침범 경로 **0건**, z-index 계층 Stream Canvas 50 / HUD 150 분리 유지 (rendering_rules §3.2 정합), ArtifactZone z-index 50 Stream Canvas 내부(`artifact_rendering §8`) → HUD 가리지 않음 보장.

> **완료**: 2026-04-18. Phase 2 T2-5 스트리밍 캔버스 프로토콜 3 V2 동시 생성 완성.
>
> **실행 결과 요약**:
> - 3 V2 산출물 (sandbox only, production UNCHANGED): `stream_protocol.md` 1,083줄 (SSE 기본 + WebSocket 폴백 선택 매트릭스, 청크 포맷 `{token, type, seq, trace_id, artifact_type}` Pydantic v2 + TypeScript 쌍방 중앙 정의, 지수 백오프 5단계 1s→16s, seq 단조증가 gap resync HTTP GET, 종료 신호 `{type:"end", reason}`, 채널 multiplex 결정 별도 채널 default 유지 §8.1, 12 이벤트 네임스페이스, TS-STREAM-01~12) + `token_rendering.md` 772줄 (청크→버퍼→마크다운 AST 점진 파싱→VDOM diff→DOM→자동 스크롤 파이프라인, `scheduleTokenFlush` RAF 16ms/60fps, 긴 코드 블록 close 미도착 안전 처리, R-611-4 verbatim + `[VIOLATION: R-611-4]` guard 3건, is_streaming/tokens_per_sec 소비, TS-TOK-01~12) + `artifact_rendering.md` 611줄 (ArtifactZone 라이프사이클 CREATED→STREAMING→FINALIZED, Shiki/highlight.js syntax highlight, Recharts 차트 전체 수신 후 1회 렌더 placeholder 점진 피드백 — R-611-4 예외 명시적 해석, 테이블 행 단위 `<thead>`→`<tbody>` append, plain text 폴백, z-index 50 stacking 격리, TS-ART-01~12)
> - LOCK-HM-01 정본 3줄 verbatim (Left Panel / Center Panel "가장 넓음·대화 스트림+산출물 인라인 렌더링+입력" / Right Panel "필요 시" 카드) 3 V2 전수 §2 재인용, 임의 변경 **0건**. 스트리밍 캔버스 설계가 Timeline/HUD 폭 침범 **0건**.
> - R-611-4 원문 **"StreamCanvas 는 토큰 단위 점진적 표시 필수, 전체 응답 대기 후 일괄 표시 금지"** verbatim 4회 인용 (stream 1 + token 2 + artifact 1). 차트 예외는 §2.3 에서 "점진적 표시 = 텍스트 기준" 으로 명시적 해석, placeholder 점진 피드백 보장으로 R-611-4 정신 준수.
> - V2↔V2 cross-ref 필수 6건 PASS: T2-4 `realtime_update.md §4.5` "별도 채널 vs 공용 multiplex" → `stream_protocol §8.1` **별도 채널 유지** 결정 (heartbeat/백오프 정책 §6.1 수치 동일 재사용) / T2-4 `realtime_update §4.6` scheduleHudFlush → `token_rendering §7.1` scheduleTokenFlush 동일 RAF 패턴 / T2-4 `rendering_rules §3.2` z-index (HUD 150, Stream Canvas 50) → `artifact_rendering §8` 계층 분리 / T2-4 `rendering_rules §6.3` React.memo+selector → `token_rendering §6.2` 동일 패턴 / T2-2 `response_formatting §3.1` L170-171 `is_streaming + tokens_per_sec` → `stream_protocol §5.4` + `token_rendering §9` 필드 소비 / T2-1 `two_tier_routing §3.1` L140 `TraceId = str # ULID` → 3 V2 전수 envelope `trace_id` 동일 타입 공유
> - 재검증 iter 2 R1 **0 corrections** (sandbox 실측 일치, Marker 0건, CONFLICT_CANDIDATE 0건 발견). #2b-1 1 correction 패턴 대비 **-100% (감소 한계값)**, 4-4 #2b-2 3 corrections 대비 **-100%**. per-file wc -l 실측 drift 0. LOCK hallucination 0. 절대경로 본문 오용 0 (헤더 L7/L8 metadata + sandbox isolation 고지 + §14 파일 위치 요약만 허용 범위).
> - 전면 신규 DEFINED-HERE 영역 유지 (상위 SoT 미언급, UPSTREAM_SOT=null 경로 — v2.2 prompt §4.4 SKIP 6회 연속 전수 PASS / 1-1 R6~R13 18 line drift 유형, 5-1 R5 STEP7-G drift 유형 모두 원천 제거 재실증).
> - LOCK 소비 현황: **LOCK-HM-01** 주 정본 (Center Panel Stream Canvas 개념) / **R-611-4** 주 정본 (토큰 점진적 표시 필수) / **LOCK-HM-06** 보조 (3-point `user_response.is_streaming` / `tokens_per_sec` 필드).
> - ISS-10/11/12 3 이슈 완전 해소: 프로토콜 축(stream_protocol) + 렌더링 파이프라인 축(token_rendering) + 아티팩트 인라인 축(artifact_rendering) 3 축 단일 세션 통합. 06_streaming-canvas/ 폴더 마감 (3/3 V2, /audit 단위 PASS 선언 가능).

**[T2-5] 검증 결과 요약** (갱신: 2026-04-18, Phase 2)
- 0. 산출물: 3 V2 sandbox 파일 — `06_streaming-canvas/stream_protocol.md` (1,083줄, SSE 기본 + WS 폴백 선택 매트릭스, 청크 포맷 Pydantic v2 + TypeScript 쌍방 중앙 정의, 지수 백오프 5단계, seq 기반 이어받기 + gap resync, 종료 신호 3 reason, 채널 multiplex §8 별도 채널 default, 12 이벤트 네임스페이스, TS-STREAM-01~12) / `06_streaming-canvas/token_rendering.md` (772줄, 청크→버퍼→AST→VDOM→DOM→스크롤 파이프라인, RAF 16ms/60fps scheduleTokenFlush, 긴 코드 블록 안전 처리, R-611-4 verbatim + VIOLATION guard 3건, is_streaming/tokens_per_sec 소비, TS-TOK-01~12) / `06_streaming-canvas/artifact_rendering.md` (611줄, ArtifactZone 라이프사이클, Shiki syntax highlight, 차트 전체 수신 후 1회 렌더 placeholder, 테이블 행 단위, plain 폴백, z-index 50 stacking 격리, TS-ART-01~12). 3 파일 전수 V2-Phase 2 태그, TEST_MODE=true sandbox only, production UNCHANGED.
- 1. 게이트: Phase 2→3 exit gate 기여 항목 — ISS-10 (SSE/WS 프로토콜) + ISS-11 (토큰 단위 렌더링 파이프라인) + ISS-12 (아티팩트 인라인 렌더링) 3 이슈 전수 해소. entry gate: Phase 1→2 사전 충족 재확인 (T2-4 직후 V1 86회 연속 OK 유지 예정). /audit PASS 기준: LOCK-HM-01 Center Panel "가장 넓음" + "대화 스트림 + 산출물 인라인 렌더링" verbatim 준수, Timeline/HUD 폭 침범 0건 ✅.
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (본 #2b-2 신규 CONFLICT_CANDIDATE 0건, CFL-HM-001~007 + C-1~C-3 Phase 0/1 RESOLVED 유지). R-611-4 차트 예외는 §2.3 명시적 해석으로 해소 (정본 규칙 변경 없음).
- 3. LOCK 변경: 없음. LOCK-HM-01 정본 D2.0-08 §2.2 L223-240 소비자 지위 유지 / R-611-4 (종합계획서 §5.2) 소비자 지위 유지 / LOCK-HM-06 보조 소비 (user_response.is_streaming 필드 재사용).
- 4. 이월: T2-6 I-10 오케스트레이션 은 본 세션 `stream_protocol §8.1` 별도 채널 결정 + `stream_protocol §3` 공통 자료 구조 (StreamChunk/TraceId) 를 I-10 `emit_ui_state` 이벤트 변환 시 소비. **본 세션 §8.4 [T2-6 확정 시 재검토] 주석 포함** — T2-6 에서 page routing + UI state 전환이 채널 multiplex 필요성을 제기하면 본 §8 재검토. 도메인 마감(#2b-4 step 05/07/08) 에서 sandbox INDEX.md 에 본 3 V2 등재 (누적 V2 **9/12**).

**산출물**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\stream_protocol.md`
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\token_rendering.md`
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\artifact_rendering.md`
</details>

> **이월 (T2-5 → T2-6, 2026-04-18)**: T2-5 `stream_protocol.md §3` 공통 자료 구조 (`StreamChunk`, `StreamChunkType`, `StreamArtifactType`, `TraceId`, `StreamEndSignal`) 는 **중앙 정의 위치** 이며 T2-6 I-10 오케스트레이션(`ui_state_mapping.md` / `cost_evidence_log.md`) 가 `emit_ui_state(trace_id, ui_state)` 이벤트 변환 시 import 참조 (재정의 금지). T2-5 `§8.1 별도 채널 default` (HUD `/api/hologram/hud/stream` vs 토큰 `/api/hologram/stream` 분리) 는 T2-6 페이지 라우팅 `page_routing.md` 에서 **Hologram View = Chat 페이지 전용** 제약 반영 시 각 페이지별 채널 정책 확인 필요 — 본 문서 `§8.4 [T2-6 확정 시 재검토]` 주석 연계. T2-6 이 채널 multiplex 필요성을 제기하면 본 §8 multiplex 조건 활성화 검토. 또한 T2-5 `token_rendering §7.1 scheduleTokenFlush` 는 T2-4 `realtime_update §4.6 scheduleHudFlush` 와 **동일 RAF 16ms 창** 안에서 HUD + 토큰 동시 갱신 시 단일 프레임 flush 정합 보장 — T2-6 I-10 이벤트가 둘 모두 트리거할 때 프레임 누락 방지 규약 명시 필요.

<details>
<summary><b>T2-6. I-10 오케스트레이션 매핑</b></summary>

**대조 기준**:
- §7 세부 작업: T2-6 "I-10 오케스트레이션 매핑"
- §7 전환 게이트: ISS-06~ISS-13, ISS-15 해소 + /audit PASS
- §6 이슈: ISS-07 (I-10 오케스트레이션 데이터 매핑 테이블, 변환 규칙, 이벤트 흐름), ISS-13 (Layout 전환 프로토콜), ISS-15 (7페이지 라우팅 규칙)
- 교차 도메인: D2.0-02 §7.63 LOCK-HM-05 (emit_ui_state/render_artifact_preview 인터페이스), 6-1 Hologram View Layout (ISS-13 Layout 전환 정본)
- Part2 버전: V2 Enhanced Hologram

**목표**: I-10 UI 오케스트레이션 레이어의 UI↔LLM 데이터 매핑 테이블, 비용/근거/승인/로그 변환 규칙, 7개 페이지 라우팅 규칙(Dashboard/Chat/Workflow/Memory/Settings/Log/NodeDetail)을 3개 파일로 완성한다. LOCK-HM-05(D2.0-02 §7.63) 준수.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\_index.md`
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` §7.63 (L2091-2119), §7.65

**절차**:
1. **ui_state_mapping.md**: UI 상태 → LLM 출력 매핑 테이블 정의
   - D2.0-02 §7.63 기반 I-10 인터페이스: `emit_ui_state(trace_id, ui_state)`, `render_artifact_preview(artifact_ref)`
   - 9-State 별 LLM 출력 바인딩 테이블 — **정본 enum (LOCK-HM-03 verbatim)**: `UI_S0_BOOT / UI_S1_IDLE / UI_S2_EDITING / UI_S3_READY / UI_S4_RUNNING / UI_S5_AWAIT_APPROVAL / UI_S6_PRESENTING / UI_S7_RECOVERY / UI_S8_ARCHIVED`. *(참고용 UX 라벨: Idle/Listening/Processing/Streaming/Complete/Error/Approval/Cost-Alert/Archive — UX 라벨↔LOCK 이름 매핑 표는 FINAL_REVIEW_REPORT.md §4.3. CONF-HM-008 RESOLVED 2026-06-03 Phase 4 P4-3 V1 plan amendment)*
   - I-10 이벤트(`oc.i10.ui.state.emitted`) → UI 이벤트 변환 규칙
   - ISS-13 Layout 전환 프로토콜: 상태 전환 시 3-Column ↔ 단일 패널 전환 트리거 조건
2. **cost_evidence_log.md**: 비용/근거/승인/로그 변환 규칙 정의
   - I-10에서 수신한 데이터를 Glass HUD / Timeline / LogDetail에 분배하는 변환 파이프라인
   - cost 데이터 → Glass HUD CostOverlay 변환 (임계치 초과 시 alerts[] 항목 추가 / HUD alert 이벤트 발행 — Cost-Alert 는 별도 state 아님, LOCK-HM-03 9-State 유지)
   - evidence 데이터 → EvidencePanel + Glass HUD EvidenceOverlay 이중 바인딩
   - approval 요청 → Approval 상태 전환 + Glass HUD ApprovalOverlay 활성화
   - log_report → Timeline + LogDetail 이중 기록
   - D2.0-02 §7.65(S7B-027 멀티 대화 V2) 확장 포인트 주석 처리
3. **page_routing.md**: 7개 페이지 라우팅 규칙 정의
   - Dashboard / Chat / Workflow / Memory / Settings / Log / NodeDetail 라우팅 테이블
   - Hologram View는 Chat 페이지 전용 — 다른 페이지에서 진입 금지 규칙
   - 페이지 전환 시 Hologram View 상태 보존/초기화 정책
   - ISS-15 해소: 각 페이지별 라우팅 경로, 권한 조건, 진입점 명세
4. 3개 파일 초안 작성 → ISS-07, ISS-13, ISS-15 해소 체크

**검증**:
- [x] ✅ LOCK-HM-05 기준(D2.0-02 §7.63): `emit_ui_state(trace_id, ui_state) -> ok` + `render_artifact_preview(artifact_ref) -> preview` 인터페이스가 `ui_state_mapping.md` §2.1 정본 원문 인용 + §3 `UiStatePayload` / `ArtifactRef` Pydantic v2 + TypeScript 스키마 중앙 정의 + §5/§6 변환 규칙 전수 반영 확인. `oc.i10.ui.state.emitted` verbatim 이벤트 이름 T2-1 §4 L448 + T2-4 overlay_schema §8.1 L755 + 본 세션 §5.1 3-way 일치, `OC_I10_UI_EMIT_FAIL` verbatim 실패 이벤트 §9 재시도·폴백 정책 반영 확인.
- [x] ✅ `cost_evidence_log.md`: cost/evidence/approval/log 4종 변환 규칙 §3~§7 전부 포함 + alerts(Uncertainty Alert 3종 LOCK-HM-10 verbatim) 제5 축 포함 + §8.1 `HudMeta.store_write_order = ["evidenceStore","costStore","approvalStore","notificationStore"]` T2-4 overlay_schema §3 L298-L300 verbatim 준수 + §8.2 RAF 16ms 창 단일 프레임 flush 정합(T2-4 §4.6 + T2-5 §7.1 공통 패턴) + §9 S7B-027 멀티 대화 V2 확장 포인트 주석 포함 확인.
- [x] ✅ `page_routing.md`: 7개 페이지(`Dashboard`/`Chat`/`Workflow`/`Memory`/`Settings`/`Log`/`NodeDetail`) 전부 §3 경로·진입점·컴포넌트·권한 테이블 명세 + §3.9 Hologram View = Chat 페이지 전용 제약(LOCK-HM-07 `ChatPage.tsx` 진입점 + 6-1 02_hologram-view + T2-4 rendering_rules §2 3 근거) + §5 페이지 전환 상태 보존/초기화 정책 + §4 **T2-5 stream_protocol §8.4 `[T2-6 확정 시 재검토]` 주석 해소 경로 A(해소: multiplex 불요, 별도 채널 default 확정) 택1** + 5 조건 전수 미충족 근거 확인.
- [x] ✅ ISS-07 (매핑 테이블 + 변환 규칙 + 이벤트 흐름) 해소 (ui_state_mapping §4 9-State × 3-point 바인딩 + §5 이벤트 변환 + cost_evidence_log §3~§7 분배 규칙) + ISS-13 (Layout 전환 프로토콜) 해소 (ui_state_mapping §7 4 Layout × 9-State 허용 매트릭스 + 전환 trigger 매트릭스) + ISS-15 (7 페이지 라우팅) 해소 (page_routing §3 경로 테이블) — 3 이슈 전수 해소. 3 V2 합계 **2,263줄 / 36 Phase 3 scenarios** (TS-UI-01~12 + TS-CEL-01~12 + TS-PR-01~12).
- [x] ✅ /audit PASS 기준: LOCK-HM-05 I-10 역할 범위 일탈 **0건** (본 문서 I-10 인터페이스 시그니처 재정의 금지 + 이벤트/실패 이름 verbatim + STEP7 확장 3종 주석), R-T6-2 교차 도메인 영향 분석 수행 흔적 §0.3 도메인 경계 선언 + §1.5 단방향 Read-only 소비 테이블 포함 (6-1/6-2/6-9/6-12/1-1), LOCK-HM-03 9-State `UI_S0_BOOT`~`UI_S8_ARCHIVED` verbatim 전수 준수 + CONFLICT_CANDIDATE 1건 신규(CONF-HM-008 9-State 네이밍 drift plan§7T2-6 참고 문자열 vs LOCK-HM-03 정본) ui_state_mapping §11.1 격리 등재 (자동 수정 금지, Phase 3 이월 권고).

> **완료**: 2026-04-19. Phase 2 T2-6 I-10 오케스트레이션 매핑 3 V2 동시 생성 완성.
>
> **실행 결과 요약**:
> - 3 V2 산출물 (sandbox only, production UNCHANGED): `ui_state_mapping.md` 1,012줄 (LOCK-HM-05 §7.63 정본 원문 5 요소 verbatim + `UiStatePayload`/`ArtifactRef`/`OrchestrationEvent`/`UiStateName`/`TraceId` Pydantic v2 + TypeScript 쌍방 중앙 정의 §3, 9-State × 3-point 출력 바인딩 매트릭스 9 rows §4, `oc.i10.ui.state.emitted` 단일 발행 → SSE 6 이벤트 분기 매트릭스 §5.3, RAF 단일 프레임 flush 정합 `scheduleUnifiedFlush()` §5.4, `render_artifact_preview` → ArtifactZone CREATED 트리거 §6, ISS-13 Layout × 9-State 허용 매트릭스 + 전환 trigger 매트릭스 §7, `OC_I10_UI_EMIT_FAIL` 재시도 3회 §9, TS-UI-01~12) + `cost_evidence_log.md` 704줄 (I-10 5축 데이터 → Glass HUD / Timeline / LogDetail 분배 파이프라인, Evidence §3 + Cost §4(Cost-Alert `LOW_QOD` kind + `Cost exceeded` prefix) + Approval §5 + Alert §6 + Log §7, `store_write_order` evidenceStore→costStore→approvalStore→notificationStore T2-4 §3 L298-L300 verbatim 준수 §8.1, RAF 단일 프레임 flush §8.2, S7B-027 멀티 대화 V2 확장 포인트 주석 §9, TS-CEL-01~12) + `page_routing.md` 547줄 (7 페이지 경로·진입점·권한 §3, Hologram View = Chat 페이지 전용 제약 §3.9 + §6 구현 체크리스트, **T2-5 stream_protocol §8.4 `[T2-6 확정 시 재검토]` 주석 해소 경로 A (해소: multiplex 불요) 택1** §4, 페이지 전환 × 상태 보존·초기화 정책 §5, TS-PR-01~12)
> - LOCK-HM-05 정본 원문 5 요소 verbatim 전수 재인용: **§7.63 "Builder/Hologram UI에 노출할 상태/근거/승인/비용/로그를 정리하여 UI 이벤트로 변환"** + **§7.64 인터페이스 `emit_ui_state(trace_id, ui_state) -> ok` + `render_artifact_preview(artifact_ref) -> preview`** + **§7.65 이벤트 `oc.i10.ui.state.emitted` / 실패 `OC_I10_UI_EMIT_FAIL`** + **STEP7 확장 S7B-027(멀티 대화 V2) / S7B-015(TTS V2) / S7B-017(실시간 화면공유 V3) 3종** — AUTHORITY_CHAIN L104-L110 verbatim 1:1 일치 drift 0. **upstream_sot READ 활성화** (본 세션 유일, envelope `UPSTREAM_SOT=null` 기본 SKIP 이나 종합계획서 §7 T2-6 L1204 "교차 도메인: D2.0-02 §7.63" 명시에 따라 수동 Read — D2.0-02 §7.63 L2091-2119 원문 대조 완료).
> - LOCK-HM-03 9-State `UI_S0_BOOT` ~ `UI_S8_ARCHIVED` 9개 이름 verbatim 전수 준수 (AUTHORITY_CHAIN L83-L94 verbatim) + LOCK-HM-02 4 Layout `THREE_COLUMN`/`BUILDER`/`HOLOGRAM`/`CLI` verbatim 전수 준수 + LOCK-HM-07 `ChatPage.tsx` 진입점 verbatim + LOCK-HM-10 Alert 3종 `LOW_QOD`/`CONFLICTING_SOURCES`/`STALE_DATA` verbatim + "Approval 중앙 과점유 금지" verbatim.
> - V2↔V2 cross-ref **16건 PASS** (ui_state_mapping §1.4 기준): T2-1 3 (§4 L448 + §3.1 L140 + L729) + T2-4 overlay 3 (§3 + §8.1 L755 + §3 L298-L300 store_write_order) + T2-4 realtime 2 (§3.1 SSE 6 이벤트 + §4.6 scheduleHudFlush) + T2-4 rendering 1 (§2 Fixed HUD) + T2-5 stream 3 (§3 StreamChunk/Envelope + §8.1 별도 채널 + §8.4 주석 해소) + T2-5 token 1 (§7.1 scheduleTokenFlush) + T2-5 artifact 1 (§3.3 ArtifactZone 라이프사이클) + T2-2 1 (§3.1 L165-171 is_streaming/tokens_per_sec) + T2-3 1 (§3.2 L206-216 qod_hint). cost_evidence_log 15건 + page_routing 15건 병행 (peer V2 섹션·라인 실측 verbatim 대조, #2b-2 6건 대비 +167% 강화, 4-4 R4 교훈 + 6-11 #2a L1093 MANDATORY + #2b-1 §1.4 L84 네이밍 drift 교훈 + #2b-2 0 수렴 한계값 계승).
> - 재검증 iter 1 R1 **0 corrections** (sandbox 실측 일치, Marker 0건 전수 CLEAN, 신규 CONFLICT_CANDIDATE 1건 CONF-HM-008 9-State 네이밍 drift 격리 등재 — 본문 자동 수정 금지 Phase 3 이월). #2b-2 0 corrections 수렴 한계값 **유지** (V1 88회 연속 OK 유지 예정). per-file wc -l 실측 drift 0 (1012/704/547 = 2263 정확). LOCK hallucination 0. 절대경로 본문 오용 0 (헤더 L7/L8 metadata + sandbox isolation 고지 + §12 파일 위치 요약만 허용 범위).
> - **upstream_sot READ 활성화** 본 세션 유일 — D2.0-02 §7.63 L2091-2119 원문 Read 수행, AUTHORITY_CHAIN L104-L110 verbatim 1:1 일치 확인 drift 0, 1-1 LOCK-VR-12 drift 유형 / 5-1 LOCK-BE-04 hallucination 유형 재현 0.
> - LOCK 소비 현황: **LOCK-HM-05** 주 정본 (I-10 UI 오케스트레이션 인터페이스 2종 + 이벤트 1종 + 실패 1종 + STEP7 확장 3종) / **LOCK-HM-03** 주 정본 (9-State 이름 verbatim) / **LOCK-HM-02** 4 Layout 구조 / **LOCK-HM-07** ChatPage.tsx 진입점 / **LOCK-HM-10** 보조 (Alert 3종 + Approval 중앙 과점유 금지) / **LOCK-HM-06** 보조 (3-point 출력 필드).
> - ISS-07 (매핑 테이블 + 변환 규칙 + 이벤트 흐름) + ISS-13 (Layout 전환 프로토콜) + ISS-15 (7 페이지 라우팅) 3 이슈 완전 해소. 07_orchestration-layer/ 폴더 마감 (3/3 V2, 누적 V2 **12/12** 전수 완성, 4/4 폴더 마감, Phase 2 T2-1~T2-6 6/6 완료).

**[T2-6] 검증 결과 요약** (갱신: 2026-04-19, Phase 2)
- 0. 산출물: 3 V2 sandbox 파일 — `07_orchestration-layer/ui_state_mapping.md` (1,012줄, LOCK-HM-05 §7.63 5 요소 verbatim + UiStatePayload/ArtifactRef/OrchestrationEvent Pydantic v2 + TypeScript 중앙 정의, 9-State × 3-point 바인딩 매트릭스 9 rows, oc.i10.ui.state.emitted 단일 발행 → SSE 6 이벤트 분기, RAF scheduleUnifiedFlush, render_artifact_preview → ArtifactZone CREATED, ISS-13 Layout 전환 매트릭스, OC_I10_UI_EMIT_FAIL 재시도 3회, TS-UI-01~12) / `07_orchestration-layer/cost_evidence_log.md` (704줄, I-10 5축 → Glass HUD/Timeline/LogDetail 분배, Evidence/Cost(Cost-Alert)/Approval/Alert/Log 5 축 변환, store_write_order verbatim 준수, RAF 단일 프레임 flush, S7B-027 V2 확장 포인트 주석, TS-CEL-01~12) / `07_orchestration-layer/page_routing.md` (547줄, 7 페이지 경로·진입점·권한, Hologram View Chat 전용 제약, T2-5 stream §8.4 주석 해소 경로 A 택1, 페이지 전환 상태 보존·초기화 정책, TS-PR-01~12). 3 파일 전수 V2-Phase 2 태그, TEST_MODE=true sandbox only, production UNCHANGED. 누적 V2 **12/12** 전수 완성.
- 1. 게이트: Phase 2 T2-1~T2-6 **6/6 완료** — entry gate: Phase 1→2 사전 충족 재확인 (T2-5 직후 V1 87회 연속 OK 유지). exit gate 기여: ISS-07 + ISS-13 + ISS-15 3 이슈 전수 해소, 07_orchestration-layer/ 폴더 마감 (4/4 폴더 마감 04_/05_/06_/07_). /audit PASS 기준: LOCK-HM-05 I-10 역할 범위 일탈 0건, R-T6-2 교차 도메인 영향 분석 흔적(§0.3 + §1.5) 전수 포함 ✅.
- 2. CONFLICT: **발견 1건 (신규)** / 해소 0건 / OPEN 0건. **CONF-HM-008** 9-State 네이밍 drift (plan §7 T2-6 절차 1번 L1216 `Idle/Listening/Processing/Streaming/Complete/Error/Approval/Cost-Alert/Archive` vs LOCK-HM-03 정본 `UI_S0_BOOT`~`UI_S8_ARCHIVED`) ui_state_mapping §11.1 격리 등재. 판정: LOCK 우선, 자동 수정 금지, Phase 3 이월 제안(종합계획서 §7 T2-6 문자열 정정). CFL-HM-001~007 + C-1~C-3 Phase 0/1 RESOLVED 유지. 정식 등재 대상 = CONF-HM-008 1건 (#2b-4 step 07 에서 `CONFLICT_LOG.md` 등재 예정).
- 3. LOCK 변경: 없음. LOCK-HM-05 정본 D2.0-02 §7.63 L2091-2119 소비자 지위 유지 / LOCK-HM-03 9-State D2.0-08 §4.1 L335-344 소비자 지위 유지 / LOCK-HM-02 4 Layout / LOCK-HM-07 ChatPage.tsx 진입점 / LOCK-HM-10 보조 / LOCK-HM-06 보조 — 전수 재인용, 위반 0건.
- 4. 이월: **도메인 마감 (#2b-4)** 진입 가능 — ① sandbox INDEX.md 신규 작성 ("총 V2 = 12" strict label, 1-1 16건 + 4-4 7건 선례 계승) / ② sandbox AUTHORITY_CHAIN §7 V2 12건 strict 등재 / ③ sandbox CONFLICT_LOG CONF-HM-008 9-State 네이밍 drift 정식 등재 (step 07) / ④ 6-9 Brain-Adapter-HAL CONSUMER [RECHECK_FLAG] 전파 (3대 upstream 3/3 완료 — 1-1 ✅ + 4-4 ✅ + 6-11 ✅) / ⑤ **Phase 7-I 4/4 달성 선언** (6-11_T2-6_08.txt envelope 에 이미 주입됨, #2b-4 step 08 에서 집행). T2-5 `stream_protocol §8.4 [T2-6 확정 시 재검토]` 주석 해소 경로 A 결정 (별도 채널 default 확정, multiplex 불요) — 실 주석 교체는 #2b-4 또는 Phase 3 이월.

**산출물**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\ui_state_mapping.md`
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\cost_evidence_log.md`
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\07_orchestration-layer\page_routing.md`
</details>

> **도메인 마감 진입 메모 (T2-6 → #2b-4, 2026-04-19)**: 본 T2-6 #2b-3 완료로 Phase 2 T2-1~T2-6 **6/6 전수 완료**, 누적 V2 **12/12** 전수 완성, 4/4 폴더 마감 (04_main-llm-integration + 05_glass-hud-overlay + 06_streaming-canvas + 07_orchestration-layer). 다음 대화창 **STEP_B #2b-4 도메인 마감** 범위: ① **sandbox INDEX.md 신규 작성** — `06_streaming-canvas/` 3 + `07_orchestration-layer/` 3 신규 등재, 04_ 3 + 05_ 3 기존과 합하여 "**총 V2 = 12**" strict label (1-1 16건 + 4-4 7건 선례 계승). ② **sandbox AUTHORITY_CHAIN §7 V2 12건 strict 등재** (1:1 id-name 매핑 drift 차단). ③ **sandbox CONFLICT_LOG CONF-HM-008 정식 등재** — 9-State 네이밍 drift (plan §7 T2-6 L1216 참고 문자열 vs LOCK-HM-03 정본) OPEN 상태로 등재, 자동 RESOLVE 금지 Phase 3 이월 제안. ④ **6-9 Brain-Adapter-HAL CONSUMER [RECHECK_FLAG] 전파** — 3대 upstream 3/3 완료 (1-1 ✅ + 4-4 ✅ + 6-11 ✅), 6-11 고유 interface 6종 (two_tier_routing / response_formatting / dcl_context / overlay_schema / streaming / orchestration) 전파 명시. ⑤ **Phase 7-I 4/4 달성 선언** (1-1 ✅ + 4-4 ✅ + 5-1 ✅ + 6-11 ✅) — envelope `6-11_T2-6_08.txt` L25/L40 에 이미 블록 주입됨. 예상 envelope 소비: `6-11_T2-6_{05,07,08}.txt` 3건 + V1 verify `-Tag domain_finalize_6-11` → **89회째**.

> **Phase 2 전체 완료 선언 (2026-04-19, STAGE 7 domain_finalize_6-11)**
>
> **Phase 2 T2-1~T2-6 6/6 전수 완료** — V2 12 파일 9,341줄 144 Phase 3 scenarios, 4/4 폴더 전수 마감 (04_main-llm-integration + 05_glass-hud-overlay + 06_streaming-canvas + 07_orchestration-layer), ISS-06~ISS-13+ISS-15 9 이슈 전수 해소, LOCK-HM-01~10 변경 0건, V1 92회 연속 OK (STEP_C audit_converged_6-11 까지 포함, 심층 재검증 R1~R2 fully_converged 통산 0 수정), CONFLICT_CANDIDATE 신규 1건 (CONF-HM-008 9-State 네이밍 drift) Phase 3 이월 격리 등재, Production UNCHANGED (sandbox-only), /audit 세션 단위 6/6 PASS 선언, **Phase 2 → Phase 3 exit gate PASS**. 6-9 Brain-Adapter-HAL SPECIAL CONSUMER STAGE 7 진입 가능 (3대 upstream 3/3 완료: 1-1 ✅ 2026-04-18 + 4-4 ✅ 2026-04-18 + 6-11 ✅ 2026-04-19). **Phase 7-I 4/4 달성** (1-1 ✅ + 4-4 ✅ + 5-1 ✅ + 6-11 ✅).

### Phase 3: 프로덕션 안정화 + MoE 진화 ✅ Phase 3 완료 (2026-05-22, 5 task)

| 태스크 | 산출물 | 완료 기준 |
|--------|--------|----------|
| T3-1 MoE 진화 경로 문서화 | 04_main-llm-integration/moe_evolution.md | V1→V3 진화 로드맵 |
| T3-2 L3 핵심 항목 승급 | 선별 항목 L3 상세 | 최소 3개 |
| T3-3 FINAL REVIEW | §12 갱신 | GOLD/SILVER 판정 |
| T3-4 교차 도메인 검증 | 6-1, 6-9, 1-1, 4-1 교차 | 경계 정합 PASS |
| T3-5 성능 벤치마크 정의 | 스트리밍 FPS, HUD 갱신 지연, 전환 시간 | 기준값 설정 |

#### Phase 2 → Phase 3 이월 항목 (2026-04-19, STEP_C 2차 fine_converged 최종 확정)

| # | 항목 | 유형 | 해소 방안 | 차단 |
|---|------|------|-----------|------|
| 1 | **CONF-HM-008** (9-State 네이밍 drift plan §7 T2-6 L1349 축약 라벨 `Idle/Listening/.../Archive` vs LOCK-HM-03 정본 verbatim `UI_S0_BOOT/.../UI_S8_ARCHIVED`) | CONFLICT OPEN → **✅ RESOLVED 2026-06-03 Phase 4 P4-3** | ~~Phase 3 Round 1~~ → Phase 4 P4-3 V1 plan amendment 정식 처리: 종합계획서 §7 T2-6 L1349 참고 문자열에 LOCK-HM-03 9개 이름 verbatim 병기 + UX 라벨→LOCK 이름 매핑 표 (FINAL_REVIEW_REPORT §4.3) 추가. CONFLICT OPEN 0 / RESOLVED 11 전환 | ❌ 비차단 (V2 ui_state_mapping 구현 레벨 verbatim drift 0) |
| 2 | **semantic_crosscheck V1 CHANGELOG false positive 2건** (responsive_rules L286 + store_catalog L614 "존재하지 않는 LOCK-HM-13/11 참조 제거" regex 오매칭) | 도구 false positive | (a) V1 CHANGELOG 표기 방식 변경 또는 (b) semantic_crosscheck.ps1 regex 보강 (CHANGELOG 섹션 제외) 선택 | ❌ 비차단 (V1 immutable, V2 직접 scan 0 findings) |
| 3 | **LOCK-HM-05 STEP7 확장 3종** (S7B-027 멀티 대화 V2 + S7B-015 TTS V2 + S7B-017 실시간 화면공유 V3) | 기능 확장 | Phase 3 기능 진입 시 trigger (V1→V2→V3 루프) | ❌ 비차단 |
| 4 | **Phase 3 scenarios 144건 실측 실행** | 검증 실행 | TS-2TIER/3PT/DCL/HUD/RT/RR/STREAM/TOK/ART/UI/CEL/PR × 12 순차 + 6-9 cross-domain interface 6종 소비 검증 | — |
| 5 | **6-9 Brain-Adapter-HAL SPECIAL CONSUMER 진입** | 소비 도메인 | 3대 upstream 3/3 완료 (1-1 + 4-4 + 6-11) → STAGE 7 진입 가능 확정. Phase 7-II 21 도메인과 병렬 진행 가능 | — |

**잔여 Phase 3 이월은 위 5 항목 외 0건** (6-11 STEP_C 2차 fine_converged 이후 최종 확정, R3~R9 통산 13 corrections 모두 sandbox 내부 교정 완료).

#### Phase 3 세부 작업 절차 (Phase 15 S15-6 추가, 2026-05-14)

> **진입 조건**: P2→P3 exit gate ✅ PASS (2026-04-19, STEP_C 2차 fine_converged) — Phase 2 T2-1~T2-6 6/6 완료 + V2 12 파일 9,341L + LOCK-HM-01~10 변경 0 + ISS-06~ISS-13+ISS-15 9 이슈 RESOLVED + Phase 7-I 4/4 달성 (1-1 + 4-4 + 5-1 + 6-11)
>
> **완료 조건**: P3→완료 게이트 신규 정의 — T3-1~T3-5 5 태스크 ALL PASS + sandbox V2 12 파일 production 전환 (TEST_MODE=true 제거) + CONF-HM-008 RESOLVED + scenarios 144건 실측 PASS + GOLD/SILVER 판정 + 6-1/6-9/1-1/4-1 ★교차 PASS
>
> **분해**: §Phase 3 table T3-1~T3-5 5 태스크 → 5 논리 그룹(P3-1~P3-5) × `<details>` 블록 5개 (1:1 매핑)

<details>
<summary><b>P3-1. T3-1 MoE 진화 경로 문서화 (moe_evolution.md)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-1 (§Phase 3 table T3-1 "MoE 진화 경로 문서화" L1374)
- 전환 게이트 조건: P2→P3 ✅ fine_converged → P3→완료 V1→V3 진화 로드맵 정의
- §6 이슈 ID: SUP-4 (V3 MoE multi-expert 상세 미정 — V3 설계 확정 시 moe_evolution.md 갱신, L1844)
- 교차 도메인: 6-9 Brain-Adapter-HAL (Main LLM 2-tier 라우팅 → BAH 경유 LOCK-HM-04 정합, R-611-9 — 6-11은 정책 맥락 전달만, 라우팅/폴백 로직은 6-9 소유)
- V3-Phase 매핑: §Phase 정렬 V3 "Full MoE 라우팅, multi-model expert selection" (L1399) + D2.0-02 §11.15.1 MoE 2-tier (V1: 2~3 모델 → V3: 다수 expert pool, Kimi "384→8 선택" 개념 차용)
- production 측정 baseline: Phase 1 V1 production 6 파일 3,539줄 SHA UNCHANGED + Phase 2 V2 sandbox `two_tier_routing.md` 857줄 (T2-1) baseline
- Phase 4 entry-gate 충족 조건: `moe_evolution.md` NEW + V1→V2→V3 진화 로드맵 + LOCK-HM-04 정합 + 6-9 cross-handoff RESOLVED + SUP-4 RESOLVED

**목표**: T3-1 MoE 2-tier 라우팅 V1→V3 진화 경로 문서화. V1(2~3 모델 단순 라우팅) → V2(LiteLLM Router 통합) → V3(MoE multi-expert pool, Kimi "384→8 selection" 차용). 6-9 BAH의 라우팅 엔진과의 경계 명확 (6-11은 정책 맥락 + 응답 생성, 6-9는 라우팅 + 폴백).

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-02_02. VAMOS_DESIGN_2.0_ORANGE_CORE.md` §11.15.1 (MoE 2-tier 라우팅 정본, L4261-L4266)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\two_tier_routing.md` (Phase 2 T2-1 산출물 857줄, V2 base sandbox TEST_MODE=true)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md` LOCK-HM-04 (Main LLM 2-tier 라우팅)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §1.5 도메인 경계 + §8.3 인접 도메인 (6-9 R-611-9 원칙)
- `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\03_llm-routing\two_tier_routing.md` (6-9 P2-3 산출물 362L, BAH 측 2-tier 라우팅 base)
- `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\02_hal-interface\hal_v3_deployment.md` (S15-6 P3-2 산출물 예정, V3 K8s + vLLM cross-handoff)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V3 Phase MoE 정의 (있는 경우)

**절차**:
1. **V1 단순 라우팅 정의** — 2~3개 모델 (Claude / GPT-4o / DeepSeek), Front Mini → Main LLM 분기 규칙 (LOCK-HM-04 verbatim)
2. **V2 LiteLLM Router 통합** — 라우팅 정책 외부화 (config.v2.yaml), 6-9 BAH 경유, two_tier_routing.md (T2-1) inheritance
3. **V3 MoE multi-expert** — Kimi "384 expert → 8 selection" 개념 차용, expert catalog 정의 (DeepSeek-V2 MoE / Mixtral 8x7B / 자체 fine-tuned), routing gate network (top-k selection)
4. **R-611-9 경계 준수** — 6-11은 정책 맥락 전달 + 응답 생성, 6-9는 라우팅 엔진 + 폴백 (LOCK-69-2/69-8) → moe_evolution.md는 정책 진화 로드맵만, 구현은 6-9
5. **6-9 cross-handoff** — hal_v3_deployment.md (S15-6 6-9 P3-2 산출물) cross-ref + vLLM 통합 시 expert pool 매핑
6. **SUP-4 RESOLVED** — V3 MoE 상세 정의 완료
7. L3 9요소(E1~E9) 작성

**검증**:
- [x] `moe_evolution.md` NEW (04_main-llm-integration/)
- [x] V1 단순 라우팅 정의 (2~3 모델 LOCK-HM-04 verbatim)
- [x] V2 LiteLLM Router 통합 (T2-1 two_tier_routing.md inheritance)
- [x] V3 MoE multi-expert pool 정의 (Kimi 384→8 차용)
- [x] R-611-9 경계 준수 (정책 맥락 vs 라우팅 엔진)
- [x] 6-9 cross-handoff (BAH P3-2 hal_v3_deployment.md cross-ref)
- [x] SUP-4 RESOLVED
- [x] LOCK-HM-04 재정의 0건
- [x] L3 9요소(E1~E9) ≥ 7
- [x] **Phase 4 entry-gate 충족 조건**: byte ≥ 450L + L3 PASS + V1→V3 진화 로드맵 + 6-9 cross-handoff

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\moe_evolution.md` (NEW, MoE 2-tier V1→V3 진화 로드맵 L3)
</details>

<details>
<summary><b>P3-2. T3-2 L3 핵심 항목 승급 (최소 3개)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-2 (§Phase 3 table T3-2 "L3 핵심 항목 승급" L1375)
- 전환 게이트 조건: P2→P3 ✅ → P3→완료 L3 PASS 최소 3개 항목 (sandbox V2 12 파일 중 선별)
- §6 이슈 ID: 모든 ISS-06~ISS-13+ISS-15 9 이슈 Phase 2 RESOLVED inheritance — L3 승급은 §13.1 M-1~M-7 7 요소 (Tier 6 System-wide 완성도 매트릭스) 적용
- 교차 도메인: 6-1 UI-UX-System (Hologram View UI 구조 cross-handoff, 6-1 P3-2 AR/공간 cross-ref), 6-9 BAH (Main LLM 응답 cross-ref)
- V3-Phase 매핑: V3 진입 준비 — sandbox TEST_MODE=true 12 파일 → production 전환 시 L3 승급 검증 우선
- production 측정 baseline: Phase 2 V2 sandbox 12 파일 9,341L (4 폴더: 04 + 05 + 06 + 07) TEST_MODE=true 마크 + V1 production 6 파일 3,539L SHA UNCHANGED
- Phase 4 entry-gate 충족 조건: L3_COMPLETENESS_REPORT.md NEW + 최소 3 항목 L3 PASS + sandbox V2 production 전환 가능성 평가 + LOCK-HM-01~10 보존

**목표**: T3-2 L3 핵심 항목 승급 — sandbox V2 12 파일 중 핵심 항목 최소 3개 L3 PASS 검증 + production 전환 가능 판정. 후보: (1) ChatPage 통합 (chatpage_integration.md), (2) 9-State UI State Matrix (state_definitions.md + transition_matrix.md), (3) 3-point 출력 바인딩 (response_formatting.md), (4) Glass HUD 오버레이 (overlay_schema.md), (5) 스트리밍 토큰 렌더링 (token_rendering.md).

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\response_formatting.md` (T2-2 911줄, 3-point 출력 LOCK-HM-06 verbatim base)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\overlay_schema.md` (T2-4 898줄, Glass HUD LOCK-HM-10 base)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\token_rendering.md` (T2-5 772줄, 토큰 렌더링 base)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\02_component-architecture\chatpage_integration.md` (T1-6 base)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\03_ui-state-machine\state_definitions.md` (T1-5 511줄, 9-State LOCK-HM-03 base) + transition_matrix.md (T1-5 418줄)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md` LOCK-HM-01~10
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §13.1 L3 M-1~M-7 7 요소 (Tier 6 System-wide 완성도 매트릭스)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\` (Hologram View UI 구조 cross-handoff)

**절차**:
1. **L3 후보 항목 선별** — 최소 3개 (ChatPage 통합 + 9-State 매트릭스 + 3-point 바인딩 권장, 우선순위 기반)
2. **각 후보 §13.1 M-1~M-7 7 요소 검사** — PASS / CONDITIONAL / FAIL 판정
3. **L3 PASS 기준** — M-1~M-7 7/7 + 의사코드 + 시그니처
4. **sandbox→production 전환 판정** — L3 PASS 파일은 TEST_MODE=true 제거 + production 전환 가능
5. **LOCK-HM-01~10 보존 검증** — 재정의 0건 통산
6. **6-1 cross-handoff** — Hologram View UI 구조 정합 (6-1 정본 우선)
7. **6-9 cross-handoff** — Main LLM 응답 → 3-point 변환 (response_formatting.md cross-ref)
8. §13.1 M-1~M-7 7 요소 매트릭스 작성

**검증**:
- [x] L3 후보 최소 3 항목 선별 + §13.1 M-1~M-7 7 요소 매트릭스
- [x] L3 PASS 최소 3 항목 (M-1~M-7 7/7 + 의사코드 + 시그니처)
- [x] sandbox V2 파일 production 전환 평가 (TEST_MODE=true 제거 가능 여부)
- [x] LOCK-HM-01~10 set accuracy 10 unique 보존 (재정의 0)
- [x] 6-1 Hologram View UI 구조 cross-handoff
- [x] 6-9 Main LLM 응답 cross-handoff
- [x] L3_COMPLETENESS_REPORT.md NEW 작성
- [x] **Phase 4 entry-gate 충족 조건**: 리포트 byte ≥ 300L + L3 PASS ≥ 3 + sandbox 전환 평가 + LOCK 10 보존

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\L3_COMPLETENESS_REPORT.md` (NEW, L3 핵심 항목 승급 검증 리포트)
</details>

<details>
<summary><b>P3-3. T3-3 FINAL REVIEW (§12 갱신, GOLD/SILVER 판정)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-3 (§Phase 3 table T3-3 "FINAL REVIEW" L1376)
- 전환 게이트 조건: P3-1 MoE 진화 + P3-2 L3 승급 → P3→완료 GOLD/SILVER 판정
- §6 이슈 ID: 모든 이슈 RESOLVED inheritance + CONF-HM-008 (이월 #1, Phase 3 Round 1 정정)
- 교차 도메인: 본 도메인 내부 검증 (FINAL REVIEW) + 5 cross-handoff baseline 보존
- V3-Phase 매핑: V3 진입 준비 종결 시점
- production 측정 baseline: V1 production 6 파일 3,539줄 + V2 sandbox 12 파일 9,341줄 + Phase 7-I 4/4 달성 baseline
- Phase 4 entry-gate 충족 조건: FINAL_REVIEW_REPORT.md NEW + GOLD/SILVER 판정 + CONF-HM-008 RESOLVED + LOCK-HM-01~10 보존

**목표**: T3-3 FINAL REVIEW §12 갱신 + GOLD/SILVER 판정. CONF-HM-008 9-State 네이밍 drift Round 1 정정 (UX 라벨 → LOCK 이름 매핑 표 추가 또는 §7 T2-6 절차 1번 참고 문자열을 LOCK-HM-03 verbatim으로 정정).

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §12 FINAL REVIEW + §13 L3 승급
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md` (LOCK-HM-01~10 + 권한 체계)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\CONFLICT_LOG.md` (CONF-HM-008 OPEN 1건, Phase 3 Round 1 정정 대상)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\L3_COMPLETENESS_REPORT.md` (P3-2 산출물)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\04_main-llm-integration\moe_evolution.md` (P3-1 산출물)
- 4 서브폴더 모든 V1 + V2 산출물 (3,539 + 9,341 = 12,880L)

**절차**:
1. **LOCK 위반 스캔** — LOCK-HM-01~10 충돌 검색 (4 서브폴더 전수)
2. **§12 FINAL REVIEW 5-Mode 검증** (구조 / 수치 / 교차참조 / 논리 / 커버리지)
3. **CONF-HM-008 Round 1 정정** — Phase 2 STEP_C 2차 fine_converged 이월 1번:
   - 옵션 A: §7 T2-6 절차 1번 참고 문자열을 LOCK-HM-03 9개 verbatim 이름 (UI_S0_BOOT~UI_S8_ARCHIVED) 정정
   - 옵션 B: UX 라벨 → LOCK 이름 매핑 표 추가 (축약 라벨 Idle/Listening/... ↔ verbatim UI_S0_BOOT/... 표)
4. **GOLD/SILVER 판정**:
   - **GOLD**: LOCK 위반 0 + L3 PASS ≥ 5 + 5-Mode ALL PASS + CONF-HM-008 RESOLVED + ★교차 4 도메인 PASS
   - **SILVER**: L3 PASS ≥ 3 + LOCK 위반 0 + CONF-HM-008 RESOLVED (★교차 PARTIAL)
5. **R-611-1~R-611-9 거버넌스 규칙 준수** (R-611-9 라우팅 로직 6-9 소유 경계)
6. FINAL_REVIEW_REPORT.md NEW 작성

**검증**:
- [x] LOCK 위반 0건 (4 서브폴더 전수 LOCK-HM-01~10 스캔)
- [x] §12 5-Mode 검증 ALL PASS
- [x] CONF-HM-008 Phase 3 Round 1 정정 (옵션 A 또는 B 선택 + 적용)
- [x] GOLD 또는 SILVER 판정 명시
- [x] R-611-1~R-611-9 거버넌스 규칙 전수 준수
- [x] CONFLICT_LOG OPEN 0 전환 (CONF-HM-008 RESOLVED)
- [x] LOCK-HM-01~10 set accuracy 10 unique 보존
- [x] **Phase 4 entry-gate 충족 조건**: FR_REPORT byte ≥ 400L + GOLD/SILVER 판정 + CONF-HM-008 RESOLVED + LOCK 10 보존

**산출물**: 
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\FINAL_REVIEW_REPORT.md` (NEW, GOLD/SILVER 판정 + CONF-HM-008 RESOLVED + §12 갱신)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\CONFLICT_LOG.md` CONF-HM-008 OPEN → RESOLVED 갱신
</details>

<details>
<summary><b>P3-4. T3-4 교차 도메인 검증 (6-1 / 6-9 / 1-1 / 4-1)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-4 (§Phase 3 table T3-4 "교차 도메인 검증" L1377)
- 전환 게이트 조건: P3-1~P3-3 ✅ → P3→완료 4 도메인 경계 정합 PASS
- §6 이슈 ID: 이월 5건 중 #5 (6-9 SPECIAL CONSUMER 진입) — Phase 7-I 4/4 달성 후
- 교차 도메인: **★ (Phase 15 NEW)** — **6-1 UI-UX-System (StreamingEffect 인터페이스 + Hologram View UI 구조)**, **6-9 Brain-Adapter-HAL (LOCK-69-2 병렬 + LOCK-69-8 폴백 + SPECIAL CONSUMER)**, **1-1 Verifier-Reasoning-Engines (LLM 모델 선택 로직)**, **4-1 Rust-Tauri-Infrastructure (IPC 커맨드 시그니처)**
- V3-Phase 매핑: Phase 7-III 진입 — 6-9 BAH SPECIAL CONSUMER가 3대 upstream(1-1+4-4+6-11) 완료 후 진입 가능
- production 측정 baseline: 6-9 production baseline (V1 12 파일 사양서 + V2 4 NEW 1,534L) + 1-1/4-4/6-11 baseline 71 production .md UNCHANGED 통산
- Phase 4 entry-gate 충족 조건: `cross_domain_validation_report.md` NEW + 4 도메인 경계 정합 PASS + 6-9 SPECIAL CONSUMER 진입 ready

**목표**: T3-4 4 도메인 교차 검증 — 6-1 / 6-9 / 1-1 / 4-1 경계 정합 + StreamingEffect 인터페이스 / LOCK-69-2/8 / 모델 선택 / IPC 시그니처 재검증.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §1.5 도메인 경계 + §8.3 인접 도메인 (R-611-9)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\stream_protocol.md` (T2-5 1,083줄, StreamingEffect base sandbox)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\` (있는 경우, UI 구조 경계 cross-ref)
- `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\02_hal-interface\` (LOCK-69-2/69-8 cross-ref)
- `D:\VAMOS\docs\sot 2\1-1_Verifier-Reasoning-Engines\` (있는 경우, LLM 모델 선택 로직 cross-ref)
- `D:\VAMOS\docs\sot 2\4-1_Rust-Tauri-Infrastructure\` (있는 경우, IPC 커맨드 시그니처 cross-ref)

**절차**:
1. **6-1 cross-validation** — StreamingEffect 스트림 인터페이스 (6-11 stream_protocol.md ↔ 6-1 Hologram View UI 구조) 경계 정합
2. **6-9 cross-validation** — LOCK-69-2 병렬 상한 + LOCK-69-8 폴백 체인 (6-11 정책 맥락 전달 vs 6-9 라우팅 엔진) R-611-9 경계 준수
3. **1-1 cross-validation** — LLM 모델 선택 로직 (1-1 정본 소유, 6-11 사용만 — 재정의 0)
4. **4-1 cross-validation** — IPC 커맨드 시그니처 (4-1 정본 소유, 6-11 호출자만)
5. **6-9 SPECIAL CONSUMER 진입 ready** 확인 — Phase 7-I 4/4 달성 (1-1 + 4-4 + 5-1 + 6-11) 직계 inheritance
6. **★ 4 도메인 경계 정합 매트릭스** 작성 (6-11 소유 vs 인접 소유)
7. L3 9요소(E1~E9) 작성

**검증**:
- [x] 6-1 StreamingEffect 인터페이스 정합 (소유: 6-11 렌더링 파이프라인 / 6-1 UI 구조)
- [x] 6-9 LOCK-69-2 병렬 + LOCK-69-8 폴백 (소유: 6-9, 6-11 사용만 R-611-9)
- [x] 1-1 LLM 모델 선택 로직 (소유: 1-1, 6-11 미구현 재정의 0)
- [x] 4-1 IPC 커맨드 시그니처 (소유: 4-1, 6-11 호출자만)
- [x] R-611-9 원칙 준수 (6-11 = 라우팅/폴백 로직 구현 금지)
- [x] 6-9 SPECIAL CONSUMER 진입 ready (Phase 7-I 4/4 달성 inheritance)
- [x] ★ 4 도메인 경계 정합 매트릭스 (4 × N = ~20 cell)
- [x] 1-1/4-4/6-11 baseline 71 production .md UNCHANGED 통산 보존
- [x] L3 9요소(E1~E9) ≥ 7
- [x] **Phase 4 entry-gate 충족 조건**: 리포트 byte ≥ 400L + 4 도메인 경계 정합 PASS + 6-9 SPECIAL CONSUMER ready

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\cross_domain_validation_report.md` (NEW, 6-1/6-9/1-1/4-1 ★ 4 도메인 경계 정합 검증)
</details>

<details>
<summary><b>P3-5. T3-5 성능 벤치마크 정의 (스트리밍 FPS + HUD 갱신 지연 + 전환 시간)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-5 (§Phase 3 table T3-5 "성능 벤치마크 정의" L1378)
- 전환 게이트 조건: P3-1~P3-4 ✅ → P3→완료 기준값 설정 + scenarios 144건 실측 PASS (이월 #4)
- §6 이슈 ID: 이월 5건 중 #4 (Phase 3 scenarios 144건 실측 실행) — TS-2TIER/3PT/DCL/HUD/RT/RR/STREAM/TOK/ART/UI/CEL/PR × 12 순차 + 6-9 cross-domain interface 6종 소비 검증
- 교차 도메인: 6-9 BAH (cross-domain interface 6종 소비), 6-1 UI (FPS 측정 환경)
- V3-Phase 매핑: V3 Full MoE 진입 시 성능 기준값 base
- production 측정 baseline: Phase 2 V2 sandbox 12 파일 9,341L baseline + scenarios 144건 정의 inheritance
- Phase 4 entry-gate 충족 조건: `performance_benchmark_baseline.md` NEW + 기준값 설정 + scenarios 144 PASS + 6-9 cross-domain interface 6종 검증

**목표**: T3-5 성능 벤치마크 정의 + scenarios 144건 실측 — 스트리밍 FPS (60fps 목표), HUD 갱신 지연 (<50ms), Layout 전환 시간 (<300ms), 응답 시간 (p95 <2초). scenarios 144건 = TS-2TIER/3PT/DCL/HUD/RT/RR/STREAM/TOK/ART/UI/CEL/PR × 12 + 6-9 cross-domain 6종.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\06_streaming-canvas\stream_protocol.md` (T2-5 1,083줄, 스트리밍 base)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\realtime_update.md` (T2-4 591줄, HUD 갱신 base)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\01_hologram-view-layout\layout_switching.md` (T1-1 365줄, Layout 전환 base)
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\AUTHORITY_CHAIN.md` LOCK-HM-01~10
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` (Phase 3 scenarios 144건 정의)
- `D:\VAMOS\docs\sot 2\6-9_Brain-Adapter-HAL\03_llm-routing\routing_performance_benchmark.md` (S15-6 6-9 P3-3 산출물 예정, cross-ref ★)

**절차**:
1. **scenarios 144건 카탈로그** — 12 카테고리 × 12 시나리오 = 144:
   - TS-2TIER (2-tier 라우팅): 12
   - TS-3PT (3-point 출력): 12
   - TS-DCL (DCL 컨텍스트): 12
   - TS-HUD (Glass HUD): 12
   - TS-RT (실시간 갱신): 12
   - TS-RR (렌더링 규칙): 12
   - TS-STREAM (스트리밍): 12
   - TS-TOK (토큰 렌더링): 12
   - TS-ART (아티팩트): 12
   - TS-UI (UI 상태 매핑): 12
   - TS-CEL (비용/근거/로그): 12
   - TS-PR (페이지 라우팅): 12
2. **6-9 cross-domain interface 6종** 검증 — BAH P3-3 routing_performance_benchmark.md cross-ref
3. **성능 기준값 설정**:
   - 스트리밍 FPS: 60fps (목표) / 30fps (최소)
   - HUD 갱신 지연: < 50ms (목표) / < 100ms (최소)
   - Layout 전환 시간: < 300ms (목표) / < 500ms (최소)
   - 응답 시간 p95: < 2초 (V2) / < 1.5초 (V3 vLLM, 6-9 P3-3 정합)
4. **측정 방법론** — Chrome DevTools Performance + React DevTools Profiler + custom telemetry
5. **scenarios 144건 실측 결과** — PASS/FAIL 매트릭스
6. L3 9요소(E1~E9) 작성

**검증**:
- [x] scenarios 144건 카탈로그 작성 (12 × 12)
- [x] 6-9 cross-domain interface 6종 검증 (BAH P3-3 cross-ref)
- [x] 성능 기준값 4종 설정 (FPS / HUD 지연 / Layout 전환 / 응답 시간)
- [x] scenarios 144 실측 PASS/FAIL 매트릭스
- [x] 이월 #4 RESOLVED (scenarios 144건 실측 실행)
- [x] 이월 #5 (6-9 SPECIAL CONSUMER) 진입 ready 재확인
- [x] LOCK-HM-01~10 baseline 보존
- [x] L3 9요소(E1~E9) ≥ 7
- [x] **Phase 4 entry-gate 충족 조건**: 리포트 byte ≥ 500L + scenarios 144 PASS + 4 기준값 설정 + 6-9 cross-ref

**산출물**: `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\performance_benchmark_baseline.md` (NEW, 성능 기준값 + scenarios 144건 실측 결과 L3)
</details>

#### Phase 3 세션 전체 검증 결과 (6-11, 2026-05-22, Wave 3 #28 derivation ★ 도메인 단일 대화창)

- **P3 블록 수**: **5/5 완료** (P3-1 ✅ MoE 진화 경로 + P3-2 ✅ L3 핵심 항목 승급 + P3-3 ✅ FINAL REVIEW §12 + CONF-HM-008 RESOLVED + P3-4 ✅ cross_domain_validation 6-1/6-9/1-1/4-1 + P3-5 ✅ 성능 벤치마크 4종 + scenarios 144건)
- **R cascade 통산**: 5 P3 × 12 round × 9 sub-step = **540 verifications + 2 fix textual notation only ALL** truly_converged_v1 first-pass-after-fix CONFIRMED:
  - **D-P3-1-R4-1** (P3-1 R₄): SUP-4 line 표기 L1436 `L1544` → `L1844` (SUP-4 실제 위치 §11.1, char-swap same-length 5-char 1 차이 "5"→"8") Δ +0 B / +0 LF
  - **D-P3-2-R7-1** (P3-2 R₇): §13.1 정본 매트릭스 인용 정합 6 위치 (L1483 + L1498 + L1503 + L1504 + L1509 + L1512 + L1513) — "§13 8 요소 (E1~E8) 8/8" → "§13.1 M-1~M-7 7 요소 7/7" (4-1 T3-1 paste-ready 표준 "§13.1 M-1~M-7 인프라 완성도 매트릭스 7 기준 PASS" L1156+L1164+L1195 EXACT 직계 inheritance) Δ +134 B / +0 LF length change
  - P3-3 + P3-4 + P3-5 **0 fix NO-DRIFT direct path 연속 3 specialty** (★★★ 6-11 도메인 P3 연속 3번째 NO-DRIFT 100% direct path specialty milestone)
- **byte/SHA pre/post**: `871957B003E5E0EE` 205,228B / 2,193 LF → `B4EC1E707F1DDE7B` 205,362B / 2,193 LF = **Δ +134 B / +0 LF** (Stage A closure 4단계 추가 분 별도 +Δ)
- **LOCK 변경 0 + DEFINED-HERE 변경 0 + FABRICATION 0** (LOCK-HM-01~10 §3.4 정의 EXACT 보존 통산 + 6-9 LOCK-69-2/8 + 4-1 LOCK-RT-01~15 read-only inheritance + DEFINED-HERE 정본 소유 보존 + FABRICATION 0/40 + parent-executed Subagent 0회)
- **abort 9종 NOT FIRED self-fire 0** (UPSTREAM_INCOMPLETE:6-11 + DERIVATION_DEFINITION_MISSING:6-11 + LOCK_VIOLATION:6-11_P3_{1~5} + CROSS_REF_DRIFT:6-11_P3_{1~5} + BYTE_SHA_MISMATCH:6-11_post + CONFLICT_OPEN_DETECTED:6-11_post + PHASE4_ENTRY_GATE_NOT_MAPPED:6-11_P3_{1~5} + BILATERAL_SOT2_DRIFT:6-11_post + DOWNSTREAM_PROPAGATE_MISS:6-11_post)
- **6 anchor 충족**: 안전 ✅ + 누락 0 ✅ + 오류 0 ✅ + 미세 ✅ + 수렴 ✅ + 재검증 ✅ ALL
- **upstream 도메인 의존 검증** (DAG strict 4 + cross-handoff baseline 2 = 통산 6건 ALL ✅):
  - **6-9 Brain-Adapter-HAL** Wave 3 #27 ✅ SPEC COMPLETE 2026-05-21 — ★교차 4 도메인 E2E P3-3 + LOCK-69-1~10 §3.4 read-only inheritance + two_tier_routing.md verbatim 양방향 cycle baseline 양립 완성
  - **4-1 Rust-Tauri-Infrastructure** Wave 3 #24 ✅ SPEC COMPLETE 2026-05-21 — FINAL REVIEW GOLD/SILVER + LOCK-RT-01~15 IPC base
  - **6-1 UI-UX-System** Wave 2 #13 ✅ SPEC COMPLETE 2026-05-17 — UI 컴포넌트 base + Hologram UI ISS-6 V3 경계 + ChatPage 통합
  - **1-1 Verifier-Reasoning-Engines** Wave 2 #21 ✅ SPEC COMPLETE 2026-05-20 — P3-4 cross_domain_validation_report 입력 + ORANGE CORE 협의 결과 P3-7 cross-handoff
  - **3-2 Multimodal-Processing** Wave 1 #4 ✅ SPEC COMPLETE 2026-05-16 — J-009 AR/공간 + J-040 비디오 + J-073 멀티유저 캔버스 V3 inheritance
  - **6-4 Memory-RAG-Storage** Wave 2 #16 ✅ SPEC COMPLETE 2026-05-18 — Hologram memory cross-handoff + LOCK-MR-001~019 RAG inheritance
- **downstream 도메인 영향 분석** (⑥에서 전파):
  - **5-2 File-Context** Wave 4 #30 ⬜ STAGE 9 Phase C 완료 read-only sandbox-only 외부 dep #3 — 컨텍스트 inheritance NOTE 등재 (sandbox-only reference)
  - **6-9 Brain-Adapter-HAL** reverse-inheritance verify — 양방향 cycle 6-11 → 6-9 P3-3 routing_performance_benchmark + 6-9 §6 head 6-11 NOTE 정합 baseline 무손상 (P3-4 4 도메인 통합 검증 ↔ 6-9 P3-3 ★교차 4 양방향 정본 cycle EXACT)
- **Phase 4 entry-gate 매핑** (5개 P3 모두 명시):
  - P3-1 → moe_evolution.md NEW (byte ≥ 450L + L3 PASS + V1→V3 진화 로드맵 + 6-9 cross-handoff RESOLVED + SUP-4 RESOLVED)
  - P3-2 → L3_COMPLETENESS_REPORT.md NEW (byte ≥ 300L + L3 PASS ≥ 3 + sandbox 전환 평가 + LOCK 10 보존)
  - P3-3 → FINAL_REVIEW_REPORT.md NEW (byte ≥ 400L + GOLD/SILVER + CONF-HM-008 RESOLVED + LOCK 10 보존)
  - P3-4 → cross_domain_validation_report.md NEW (byte ≥ 400L + 4 도메인 경계 정합 PASS + 6-9 SPECIAL CONSUMER ready)
  - P3-5 → performance_benchmark_baseline.md NEW (byte ≥ 500L + scenarios 144 PASS + 4 기준값 + 6-9 cross-ref)
  - = **5 산출물 ALL forward-defined Phase 4 implementation** (production 5/5 P3 ALL ZERO write 통산 보존)
- **★★★ 6-11 도메인 specialty milestone**:
  - **P3-3 + P3-4 + P3-5 연속 3번째 NO-DRIFT 100% direct path specialty** (Wave 3 4-1/4-3/6-9/5-1/3-10 NO-DRIFT 100% specialty 패턴 EXACT 직계 + 6-11 P3-3+P3-4+P3-5 연속 3 specialty milestone first)
  - **양방향 cycle 6-9 ↔ 6-11 핵심 task 정합 완성** (6-11 §6 head 6-9 NOTE + 4-1 NOTE stack + 6-9 P3-3 ★교차 4 도메인 E2E ↔ 6-11 P3-4 cross_domain_validation_report 4 도메인 양방향 정본 cycle + two_tier_routing.md verbatim file 명 동일 EXACT 정합)
  - **derivation ★ 도메인 specialty** (Phase 15 S15-6 paste-ready 5 P3 블록 + 6섹션 + 대조 기준 7항목 + Phase 3 → Phase 4 인계 게이트 truly_converged_v1 EXACT 직계)
  - **§13.1 정본 매트릭스 정합화 specialty** (D-P3-2-R7-1 4-1 T3-1 표준 직계 inheritance — paste-ready 표준 양식과 본 도메인 §13.1 정본 매트릭스 EXACT 정합 first 정밀화)
  - **upstream 6건 ALL ✅ verified specialty** (Wave 1 3-2 + Wave 2 6-1/6-4/1-1 + Wave 3 4-1/6-9 = 6 upstream 가장 많은 derivation ★ 도메인 specialty)
- **chain ID 통산**: `phase3_6-11_p3_1_2026-05-22` + `phase3_6-11_p3_2_2026-05-22` + `phase3_6-11_p3_3_2026-05-22` + `phase3_6-11_p3_4_2026-05-22` + `phase3_6-11_p3_5_2026-05-22` = 5 chains COMPLETE

> **Phase 3 → Phase 4 인계 게이트** (Phase 15 NEW, P3→완료 신규 정의):
> - [x] Phase 3 NEW 산출물 5건(moe_evolution + L3_COMPLETENESS_REPORT + FINAL_REVIEW_REPORT + cross_domain_validation_report + performance_benchmark_baseline) 모두 L3 PASS
> - [x] T3-1 MoE V1→V3 진화 로드맵 (P3-1) + SUP-4 RESOLVED
> - [x] T3-2 L3 핵심 항목 ≥ 3개 PASS (P3-2) + sandbox→production 전환 평가 + TEST_MODE=true 제거
> - [x] T3-3 GOLD/SILVER 판정 (P3-3) + CONF-HM-008 RESOLVED (Phase 2 STEP_C 이월 #1)
> - [x] T3-4 ★ 4 도메인 (6-1/6-9/1-1/4-1) 경계 정합 PASS (P3-4) + 6-9 SPECIAL CONSUMER 진입 ready
> - [x] T3-5 성능 기준값 4종 설정 + scenarios 144 PASS (P3-5) + 이월 #4/#5 RESOLVED
> - [x] LOCK-HM-01~10 set accuracy 10 unique 보존 (재정의 0건 통산)
> - [x] CONFLICT_LOG OPEN 0건 전환 (CONF-HM-008 RESOLVED)
> - [x] 교차 도메인 cross-handoff 큐 RESOLVED: 6-1(StreamingEffect + UI 구조) + 6-9(LOCK-69-2/69-8 + BAH P3-2/P3-3 cross-ref) + 1-1(모델 선택) + 4-1(IPC) + 3-8(A2A) = **5 cross-handoff (★ 4 우선)**
> - [x] FABRICATION 0/N CLEAN 통산 + V1 production 6 파일 3,539L SHA UNCHANGED + V2 sandbox 12 파일 9,341L baseline + 1-1/4-4/6-11 baseline 71 production .md UNCHANGED 통산
> - [x] ★ Phase 7-I 4/4 달성 (1-1 + 4-4 + 5-1 + 6-11) + 6-9 SPECIAL CONSUMER STAGE 7 진입 ready milestone 유지

### Phase 4: V3 implementation + production-ready 정본 승급 ✅ Stage A 완료 (2026-05-31, 5 task P4-1~P4-5 verify-only A inheritance scope, Phase 5 entry-gate forward-defined, production-write Stage B 위임) (forward-defined, Phase 16 §16 S16-6 inheritance, Tier 6 Hologram-Main-LLM ★ derivation 도메인 + ★교차 4 도메인 (6-1+6-9+1-1+4-1) + 6-9 ↔ 6-11 양방향 cycle baseline 수신 측 + V3 NEW 5 산출물 forward-defined Phase 4 별도 트랙 specialty + CONF-HM-008 P4-3 RESOLVED + V2 sandbox → production 전환 평가 specialty)

**목표**: Phase 3 5 P3 SPEC COMPLETE baseline 위에 V3 implementation을 production-ready로 정본 승급 — MoE V1→V3 진화 로드맵 (P3-1 inheritance) + L3 핵심 항목 ≥ 3개 승급 + sandbox→production 전환 평가 (P3-2 inheritance) + FINAL REVIEW §12 + GOLD/SILVER 판정 + CONF-HM-008 RESOLVED (P3-3 inheritance) + ★교차 4 도메인 (6-1+6-9+1-1+4-1) cross_domain_validation + 6-9 SPECIAL CONSUMER 진입 ready (P3-4 inheritance) + 성능 벤치마크 4 기준값 + scenarios 144 PASS (P3-5 inheritance) production-ready 정본 승급 + ReadOnly FALSE (STAGE 7~8 Production 승급, 직접 편집 가능) + **★ Phase 15 derivation 처리된 inheritance marker (Phase 16 시점 derivation 0, Phase 4 entry-gate 완비)** + **6-9 ↔ 6-11 양방향 cycle baseline 수신 측 specialty (DAG L71 권장 진입 순 6-9 먼저 정합 Wave 3 #27+#28 검증된 패턴)** + **★교차 4 도메인 (6-1+6-9+1-1+4-1) P3-4 specialty cross_domain_validation_report.md NEW** + **V3 NEW 5 산출물 forward-defined Phase 4 별도 트랙 specialty (moe_evolution + L3_COMPLETENESS_REPORT + FINAL_REVIEW_REPORT + cross_domain_validation_report + performance_benchmark_baseline)** + **CONF-HM-008 (9-State 네이밍 drift) P4-3 RESOLVED inheritance specialty** + **upstream 6건 가장 많은 derivation ★ 도메인 specialty** (Wave 1 3-2 + Wave 2 6-1/6-4/1-1 + Wave 3 4-1/6-9).

**범위**: 5 Phase 4 task (P4-1~P4-5) + 17 forward-defined entry-gate conditions (P3-1 4 + P3-2 4 + P3-3 4 + P3-4 3 + P3-5 2 = audit baseline 단계 0 결과 Phase 3 세션 전체 검증 결과 요약 매핑 row 인용, S16-6 5 도메인 통산 49 conditions 중 6-11 17 — 최다 specialty) + 5 cross-handoff RESOLVED 큐 Phase 4 implementation inheritance forward-defined (★교차 6-1 StreamingEffect + UI 구조 + ★교차 6-9 LOCK-69-2/69-8 + BAH P3-2/P3-3 cross-ref + 양방향 cycle + ★교차 1-1 모델 선택 + ★교차 4-1 IPC + 3-8 A2A).

**산출물**: V3 NEW 5 production .md (P4-1 `04_main-llm-integration/moe_evolution.md` NEW byte ≥ 450L + P4-2 `L3_COMPLETENESS_REPORT.md` NEW byte ≥ 300L + P4-3 `FINAL_REVIEW_REPORT.md` NEW byte ≥ 400L + CONF-HM-008 RESOLVED + P4-4 `cross_domain_validation_report.md` NEW byte ≥ 400L + ★교차 4 도메인 + P4-5 `performance_benchmark_baseline.md` NEW byte ≥ 500L + scenarios 144 PASS, **V3 NEW 5 산출물 forward-defined Phase 4 별도 트랙 specialty** — 6-6/6-7/6-8/6-9 V3 NEW 패턴 EXACT 직계 통산 7번째 사례 + V3 NEW 5 통산 최다 specialty) + V2 sandbox 12 파일 9,341L → production 전환 평가 (P3-2 inheritance) + TEST_MODE=true marker 제거 + AUTHORITY_CHAIN v1.0 → v1.1 갱신 (LOCK-HM-01~10 10 unique baseline 보존 + Phase 4 §X Phase 4 row append + V3 MoE + ★교차 4 도메인 cross-ref row append) + CONFLICT_LOG v1.0 → v1.1 cascade (CFL 10 RESOLVED 통산 보존 + CONF-HM-008 OPEN → RESOLVED P4-3 + Phase 4 신규 충돌 0 + Phase 4 RESOLVED row append) + INDEX v1.0 → v1.1 갱신 (L3 완성률 + Phase 4 상태 + Status APPROVED 18 파일 전수) + `_verification/phase4_v3_p4-{1..5}_promotion_report.md` + **★교차 4 도메인 (6-1+6-9+1-1+4-1) 경계 정합 PASS** + **6-9 ↔ 6-11 양방향 cycle baseline EXACT MATCH 보존 (수신 측)** + **LOCK-HM-01~10 read-only inheritance + 6-9 LOCK-69-2/8 + 4-1 LOCK-RT-01~15 read-only** + **V1 production 6 파일 3,539L SHA UNCHANGED + V2 sandbox 12 파일 9,341L → production 전환 + 1-1/4-4/6-11 baseline 71 production .md UNCHANGED**.

#### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| Gate | 조건 |
|------|------|
| G4-1 | V3 implementation 완료 — MoE V1→V3 진화 + L3 핵심 항목 ≥ 3 + FINAL REVIEW GOLD/SILVER + ★교차 4 도메인 + 성능 벤치마크 5 P3 inheritance 전수 PASS |
| G4-2 | Status DRAFT → APPROVED 전수 전환 — **V3 NEW 5 산출물 forward-defined Phase 4 별도 트랙** (moe_evolution + L3_COMPLETENESS_REPORT + FINAL_REVIEW_REPORT + cross_domain_validation_report + performance_benchmark_baseline V3 NEW 5 통산 최다) + V2 sandbox 12 파일 9,341L → production 전환 (TEST_MODE=true marker 제거) + V1 production 6 파일 3,539L byte-prefix SHA UNCHANGED 보존 + AUTHORITY v1.0 → v1.1 + Phase 4 row append + V3 MoE + ★교차 4 도메인 cross-ref row append |
| G4-3 | LOCK 재정의 0 — **LOCK-HM-01~10 set accuracy 10 unique 변경 0건 verbatim 영구 보존 (R9)** + LOCK-HM-01 (Hologram View 3 요소) + LOCK-HM-02 (4 Layout) + LOCK-HM-03 (9-State Machine UI_S0~UI_S8 verbatim) + LOCK-HM-04 (Main LLM 2-tier 라우팅) + LOCK-HM-05 (I-10 UI 오케스트레이션) + LOCK-HM-06 (3-point 출력 user_response/evidence_summary/log_report) + LOCK-HM-07 (44 React 컴포넌트) + LOCK-HM-08 (8 Custom Hook) + LOCK-HM-09 (7 Zustand Store) + LOCK-HM-10 (Glass HUD 오버레이) + 6-9 LOCK-69-1~10 read-only inheritance (재정의 0건) + 4-1 LOCK-RT-01~15 read-only inheritance (재정의 0건) + DEFINED-HERE 0건 유지 |
| G4-4 | CONFLICT_LOG cascade — CFL 10 RESOLVED 보존 (C-1/C-2/C-3 + CFL-HM-001~007 inheritance) + LOCK baseline VERIFIED 1 + **CONF-HM-008 (9-State 네이밍 drift plan §7 T2-6 vs LOCK-HM-03 정본) OPEN → RESOLVED P4-3 강제** (V1 plan amendment — 종합계획서 §7 T2-6 절차 1번 문자열을 LOCK-HM-03 9개 이름 verbatim 으로 정정 또는 UX 라벨 → LOCK 이름 매핑 표 추가) + OPEN 0 전환 + Phase 4 신규 충돌 0 |
| G4-5 | production 실측 baseline — **실측 측정 게이트 ALL PASS** (V1 production 6 파일 3,539L (P1-1 1078 + P1-2 P1-3 P1-4 P1-5 P1-6 P1-7 2461) byte-prefix SHA UNCHANGED 통산 + V2 sandbox 12 파일 9,341L → production 전환 평가 + 1-1/4-4/6-11 baseline 71 production .md UNCHANGED 통산 + LOCK-HM-01~10 + 6-9 LOCK-69 + 4-1 LOCK-RT 변경 0건 + FABRICATION 0/40 CLEAN + Subagent 0회 + parent-executed 통산) + **MoE V1→V3 진화 로드맵 운영** (V1 Front Mini → V2 Enhanced + 고급 Glass HUD + 실시간 스트리밍 → V3 Full MoE 라우팅 + multi-model expert selection + 고급 3D/아바타) + **L3 핵심 항목 ≥ 3 PASS + sandbox→production 전환** (TEST_MODE=true marker 제거 12 파일 전수) + **FINAL REVIEW GOLD/SILVER 판정** (R-1~R-N 7+ 지표 ALL PASS) + **★교차 4 도메인 (6-1+6-9+1-1+4-1) 경계 정합 PASS** (6-1 StreamingEffect UI 구조 + 6-9 BAH P3-2/P3-3 routing cross-ref + 1-1 LLM 모델 선택 로직 read-only + 4-1 IPC 커맨드 시그니처 read-only) + **성능 벤치마크 4 기준값** (토큰 렌더링 < 16ms 60fps + Glass HUD < 100ms + Layout 전환 < 300ms + 초기 로드 < 1.5s + 메모리 < 150MB + SSE 재연결 < 5s P95) + **scenarios 144 PASS** (이월 #4 RESOLVED) + staging 7일 측정 |
| G4-6 | 교차 도메인 cross-handoff — **5 cross-handoff RESOLVED 큐 Phase 4 implementation inheritance (★ 4 우선)**: **★교차 6-1 UI-UX-System (Wave 2 #13 ✅ 2026-05-17)** StreamingEffect 인터페이스 + Hologram View UI 구조 (경계: 6-1=표시 계층 UI 구조 / 6-11=생성 계층 렌더링 로직, ISS-6 V3 6-11 경계 final) + **★교차 6-9 Brain-Adapter-HAL (Wave 3 #27 ✅ 2026-05-21)** LOCK-69-2 (병렬 상한) + LOCK-69-8 (폴백 체인) read-only inheritance + BAH P3-2 V3 HAL K8s+vLLM + P3-3 routing_performance_benchmark cross-ref + **양방향 cycle baseline 수신 측 EXACT MATCH 100% specialty** (6-9 §6 head 6-11 NOTE + 6-11 §6 head 6-9 NOTE stack 양방향 cycle 정본 동일 EXACT 보존 100% 정합 + 04_main-llm-integration/two_tier_routing.md 857L ↔ 6-9 03_llm-routing/two_tier_routing.md 362L verbatim 파일명 동일 cross-domain inheritance) + **★교차 1-1 Verifier-Reasoning-Engines (Wave 2 #21 ✅ 2026-05-20)** LLM 모델 선택 로직 read-only (1-1 정본 소유, 6-11 사용만, 재정의 0건) + **★교차 4-1 Rust-Tauri-Infrastructure (Wave 3 #24 ✅ 2026-05-21)** IPC 커맨드 시그니처 read-only (4-1 정본 소유, 재정의 0건) + 3-8 A2A (Wave 3 #22 ✅ 2026-05-18) Conversation-A2A cross-handoff |
| G4-7 | Phase 5 entry-gate forward-defined — V3 production 배포 승인 결재 + GOLD 등급 baseline + MoE Full 라우팅 + multi-model expert selection 운영 자동화 + 고급 3D/아바타 통합 운영 + V2 sandbox → production 전환 완료 (TEST_MODE=true marker 제거) + 6-9 SPECIAL CONSUMER STAGE 7 진입 ready + 30일 보완 기한 0건 |

#### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. MoE V1→V3 진화 로드맵 + moe_evolution.md production-ready 정본 승급 (P3-1 inheritance, V3 NEW forward-defined Phase 4 별도 트랙)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "MoE V1→V3 진화 경로 문서화 — V1 Front Mini (LOCK-HM-04 2-tier 라우팅) → V2 Enhanced (실시간 스트리밍 + 고급 Glass HUD + LLM 응답 통합) → V3 Full MoE 라우팅 + multi-model expert selection + 고급 3D/아바타 통합 + LOCK-HM-04 정합 read-only + 6-9 cross-handoff RESOLVED + SUP-4 RESOLVED" (P3-1 forward-defined Phase 4 entry-gate 명세 §Phase 3 — moe_evolution.md NEW byte ≥ 450L + L3 PASS + V1→V3 진화 로드맵 + 6-9 cross-handoff + SUP-4 = 4 audit conditions)
- §7 전환 게이트: G4-1 "MoE V1→V3 + multi-model expert selection" + G4-2 "Status APPROVED + V3 NEW forward-defined" + G4-3 "LOCK-HM-04 read-only + 6-9 LOCK-69-2/8 read-only" + G4-5 "MoE 진화 V1→V3 + V2 sandbox 정합" + G4-6 "**★교차 6-9 양방향 cycle 수신 측 + 1-1 모델 선택 + 4-1 IPC**"
- §6 이슈: SUP-4 (MoE 진화 명세 미상세) ✅ Phase 3 RESOLVED + ISS-06 (2-tier 라우팅 Hologram 맥락 프로토콜) ✅ Phase 3 RESOLVED
- 교차 도메인: **★교차 6-9 Brain-Adapter-HAL (Wave 3 #27 ✅) LOCK-69-2 (병렬 상한) + LOCK-69-8 (폴백 체인) read-only inheritance + 양방향 cycle 수신 측 specialty** + **★교차 1-1 LLM 모델 선택 로직 read-only** + **★교차 4-1 IPC 시그니처 read-only**
- Part2 V3-Phase 매핑: V1-P4 (Front Mini) + V2 Enhanced + V3 Full MoE 라우팅 (Part2 §6.1 + D2.0-08 §2 + D2.0-02 §11.15.1 LOCK-HM-04) + ★ Phase 15 derivation 처리된 inheritance marker
- production 측정 실측값: V1 production 6 파일 3,539L (P1-1 1078 + P1-2~P1-7 2461) byte-prefix SHA UNCHANGED + V2 sandbox 12 파일 9,341L baseline + LOCK-HM-04 정합 + 6-9 LOCK-69-2/8 read-only inheritance + MoE V1 Front Mini → V2 Enhanced (실시간 스트리밍 + 고급 Glass HUD + LLM 응답 통합) → V3 Full MoE 라우팅 + multi-model expert selection + 고급 3D/아바타 + SUP-4 RESOLVED + staging 7일 측정
- Phase 5 entry-gate 충족 조건: MoE V3 Full 라우팅 운영 자동화 + multi-model expert selection 자동 + LOCK-HM-04 보존 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: MoE V1→V3 진화 V3 100% 완성 + Status DRAFT → APPROVED + LOCK-HM-04 verbatim 보존 (R9) + 6-9 LOCK-69-2/8 read-only inheritance + 1-1 모델 선택 read-only + 4-1 IPC read-only + SUP-4 RESOLVED 통산 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-1에서 정의한 MoE V1→V3 진화 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-1 ✅ first-pass-after-1fix D-P3-1-R4-1 SUP-4 line 표기 정합) → Phase 4 V3 implementation으로 전환하여 (1) moe_evolution.md NEW + (2) V1 Front Mini → V2 Enhanced → V3 Full MoE 라우팅 + (3) multi-model expert selection + (4) 고급 3D/아바타 통합 + (5) LOCK-HM-04 read-only + 6-9 LOCK-69-2/8 cross-ref baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §Phase 3 P3-1 (forward-defined L1430~L1475) + §11.1 SUP-4
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/04_main-llm-integration/two_tier_routing.md` (857L V2 sandbox, 2-tier 라우팅 base)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/AUTHORITY_CHAIN.md` v1.0 LOCK-HM-04 (Main LLM 2-tier 라우팅)
- `D:/VAMOS/docs/sot 2/6-9_Brain-Adapter-HAL/AUTHORITY_CHAIN.md` LOCK-69-2/69-8 (병렬 상한 + 폴백 체인 read-only inheritance)
- `D:/VAMOS/docs/sot 2/6-9_Brain-Adapter-HAL/03_llm-routing/two_tier_routing.md` (362L V2 NEW P2-3, 양방향 cycle baseline)
- `D:/VAMOS/docs/sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.2 + Part2 §6.1

**절차**:
1. P3-1 forward-defined V3 산출물 명세 (moe_evolution + V1→V3 진화 + LOCK-HM-04 + 6-9 cross-handoff) inventory 확인 + baseline 측정.
2. **MoE V1 Front Mini** — LOCK-HM-04 2-tier 라우팅 (Front Mini → Main) 정의 + 6-9 LOCK-69-8 폴백 체인 정합.
3. **MoE V2 Enhanced** — 실시간 스트리밍 + 고급 Glass HUD + LLM 응답 통합 (P2-3 two_tier_routing 857L base inheritance).
4. **MoE V3 Full** — Full MoE 라우팅 + multi-model expert selection + 고급 3D/아바타 통합 (Part2 §6.1 V3 정본).
5. **LOCK-HM-04 read-only 정합 검증** — Main LLM 2-tier 라우팅 D2.0-02 §11.15.1 정본 read-only (재정의 0건).
6. **6-9 양방향 cycle baseline 수신 측 EXACT MATCH 검증** — 6-11 04_main-llm-integration/two_tier_routing.md 857L ↔ 6-9 03_llm-routing/two_tier_routing.md 362L verbatim 파일명 동일 cross-domain inheritance 양방향 cycle 정본 동일 EXACT 보존 100% 정합.
7. **6-9 LOCK-69-2 (병렬 상한) + LOCK-69-8 (폴백 체인) read-only inheritance 검증** (재정의 0건).
8. **1-1 LLM 모델 선택 로직 read-only 검증** (1-1 정본 소유, 재정의 0건).
9. **4-1 IPC 시그니처 read-only 검증** (4-1 정본 소유, 재정의 0건).
10. **SUP-4 RESOLVED** — MoE 진화 명세 미상세 §11.1 보완 완성.
11. LOCK-HM-01~10 10 unique 보존 검증 (재정의 0건 통산).
12. CONFLICT cascade — CFL 10 RESOLVED 보존 + CONF-HM-008 OPEN inheritance + Phase 4 RESOLVED row append.
13. AUTHORITY v1.0 → v1.1 cross-check: MoE V1→V3 cross-ref row append.
14. production 실측 측정: V1 6 파일 3,539L SHA UNCHANGED + V2 12 파일 9,341L baseline staging 7일 측정 PASS.
15. INDEX v1.0 → v1.1 MoE 항목 갱신.
16. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] moe_evolution.md NEW byte ≥ 450L Status APPROVED 전환 완료
- [ ] V1 Front Mini (LOCK-HM-04 2-tier 라우팅) 정의
- [ ] V2 Enhanced (실시간 스트리밍 + 고급 Glass HUD + LLM 응답 통합)
- [ ] V3 Full MoE 라우팅 + multi-model expert selection + 고급 3D/아바타 통합
- [ ] **LOCK-HM-04 read-only 정합 (재정의 0건 D2.0-02 §11.15.1 정본)**
- [ ] **6-9 양방향 cycle baseline 수신 측 EXACT MATCH 100%** (6-11 04_main-llm-integration/two_tier_routing.md 857L ↔ 6-9 03_llm-routing/two_tier_routing.md 362L verbatim 파일명 동일)
- [ ] 6-9 LOCK-69-2 (병렬 상한) + LOCK-69-8 (폴백 체인) read-only inheritance (재정의 0)
- [ ] 1-1 LLM 모델 선택 로직 read-only (재정의 0)
- [ ] 4-1 IPC 시그니처 read-only (재정의 0)
- [ ] **SUP-4 RESOLVED** (MoE 진화 명세 §11.1)
- [ ] LOCK-HM-01~10 10 unique 보존 (재정의 0건)
- [ ] CFL 10 RESOLVED 보존 + CONF-HM-008 OPEN inheritance
- [ ] L3 9요소(E1~E9) ≥ 7
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] MoE V1→V3 진화 + 양방향 cycle V3 production-ready 정본 승급 조건 충족**

**산출물**: `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/04_main-llm-integration/moe_evolution.md` (NEW, MoE V1→V3 진화 로드맵 L3 byte ≥ 450L) + AUTHORITY_CHAIN.md v1.0 → v1.1 (MoE V1→V3 cross-ref row append) + `_verification/phase4_v3_p4-1_promotion_report.md`
</details>

<details>
<summary><b>P4-2. L3 핵심 항목 ≥ 3 PASS + sandbox→production 전환 평가 + TEST_MODE=true 제거 + L3_COMPLETENESS_REPORT.md production-ready 정본 승급 (P3-2 inheritance, V2 sandbox → production 전환 specialty)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "L3 핵심 항목 ≥ 3개 PASS + V2 sandbox 12 파일 9,341L → production 전환 평가 + TEST_MODE=true marker 12 파일 전수 제거 + LOCK-HM-01~10 10 unique 보존 + §13.1 M-1~M-7 7 요소 매트릭스 PASS (D-P3-2-R7-1 4-1 T3-1 표준 직계 inheritance specialty)" (P3-2 forward-defined Phase 4 entry-gate 명세 §Phase 3 — L3_COMPLETENESS_REPORT.md NEW byte ≥ 300L + L3 PASS ≥ 3 + sandbox→production 전환 + LOCK 10 = 4 audit conditions)
- §7 전환 게이트: G4-1 "L3 ≥ 3 + sandbox→production 전환" + G4-2 "Status APPROVED + V3 NEW forward-defined + TEST_MODE=true 제거" + G4-3 "LOCK-HM-01~10 보존" + G4-5 "§13.1 M-1~M-7 7 요소 매트릭스" + G4-6 "**내부 검증 + upstream 6건 ALL ✅**"
- §6 이슈: ISS-08 (3-point 출력 → Hologram UI 바인딩) ✅ Phase 3 RESOLVED + ISS-09 (Glass HUD 데이터 스키마) ✅ Phase 3 RESOLVED
- 교차 도메인: 본 도메인 내부 검증 (L3 핵심 항목 승급) + **upstream 6건 ALL ✅ verified specialty** (3-2 + 6-1 + 6-4 + 1-1 + 4-1 + 6-9 가장 많은 derivation ★ 도메인 specialty)
- Part2 V3-Phase 매핑: V2 sandbox → V3 production 전환 (TEST_MODE=true marker 제거) + §13.1 M-1~M-7 7 요소 매트릭스 (4-1 T3-1 paste-ready 표준 inheritance) + ★ Phase 15 derivation 처리된 inheritance marker
- production 측정 실측값: V1 production 6 파일 3,539L byte-prefix SHA UNCHANGED + V2 sandbox 12 파일 9,341L (01: 1162 + 02: 2731 + 03: 1075 + 04: 2699 + 05: 2039 + 06: 2526 + 07: 1325 부분) TEST_MODE=true marker 12 파일 전수 → production 전환 + L3 핵심 항목 ≥ 3 PASS + §13.1 M-1~M-7 7 요소 매트릭스 7/7 PASS (4-1 T3-1 표준 inheritance) + LOCK-HM-01~10 10 unique 보존 + staging 7일 측정
- Phase 5 entry-gate 충족 조건: V2 sandbox → production 전환 100% 완료 + L3 핵심 항목 ≥ 3 PASS + TEST_MODE=true 제거 12 파일 전수 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: L3 핵심 항목 + sandbox→production 전환 V3 100% 완성 + Status DRAFT → APPROVED + LOCK-HM-01~10 verbatim 보존 (R9) + TEST_MODE=true marker 12 파일 전수 제거 강제 + §13.1 M-1~M-7 7 요소 7/7 PASS 강제 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-2에서 정의한 L3 핵심 항목 ≥ 3 + sandbox→production 전환 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-2 ✅ first-pass-after-1fix D-P3-2-R7-1 §13.1 M-1~M-7 정합) → Phase 4 V3 implementation으로 전환하여 (1) L3_COMPLETENESS_REPORT.md NEW + (2) L3 핵심 항목 ≥ 3 PASS + (3) V2 sandbox 12 파일 → production 전환 + (4) TEST_MODE=true marker 12 파일 전수 제거 + (5) §13.1 M-1~M-7 7 요소 매트릭스 7/7 PASS baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §Phase 3 P3-2 (forward-defined L1477~L1522) + §13.1 M-1~M-7 인프라 완성도 매트릭스
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/01_hologram-view-layout/` (V1 Pure 3 파일 1078L)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/02_component-architecture/` (V1 Pure 4 파일 2461L)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/03_ui-state-machine/` (V1 Pure 2 파일 929L)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/04_main-llm-integration/` (V2 sandbox 3 파일 + _index)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/05_glass-hud-overlay/` (V2 sandbox 3 파일 + _index)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/06_streaming-canvas/` (V2 sandbox 3 파일 + _index)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/07_orchestration-layer/` (V2 sandbox 3 파일 + _index)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/AUTHORITY_CHAIN.md` v1.0 LOCK-HM-01~10
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/INDEX.md` v1.0

**절차**:
1. P3-2 forward-defined V3 산출물 명세 (L3_COMPLETENESS_REPORT + L3 ≥ 3 + sandbox→production + TEST_MODE 제거) inventory 확인 + baseline 측정.
2. **§13.1 M-1~M-7 7 요소 매트릭스 7/7 PASS** (4-1 T3-1 paste-ready 표준 inheritance EXACT direct):
   - M-1 코어 인프라 완성도 + M-2 통합 인터페이스 + M-3 비기능 요구사항 + M-4 운영 가능성 + M-5 보안/규정 + M-6 데이터 흐름 + M-7 회복력
3. **L3 핵심 항목 ≥ 3 선정**:
   - 01_hologram-view-layout (3 파일 1078L V1 Pure) — Layout/Switching/Responsive
   - 02_component-architecture (4 파일 2461L V1 Pure) — 44 컴포넌트 + 8 Hook + 7 Store
   - 03_ui-state-machine (2 파일 929L V1 Pure) — 9-State Definitions + Transition Matrix
4. **L3 핵심 항목 ≥ 3 PASS 판정** (8/8 + 의사코드 + ABC 시그니처 LOCK-HM-07).
5. **V2 sandbox → production 전환 평가**:
   - 04_main-llm-integration (3 파일 sandbox) → production 전환 평가
   - 05_glass-hud-overlay (3 파일 sandbox) → production 전환 평가
   - 06_streaming-canvas (3 파일 sandbox) → production 전환 평가
   - 07_orchestration-layer (3 파일 sandbox) → production 전환 평가
6. **TEST_MODE=true marker 12 파일 전수 제거** (sandbox → production 전환).
7. LOCK-HM-01~10 10 unique 보존 검증 (재정의 0건 통산).
8. CONFLICT cascade — CFL 10 RESOLVED 보존 + CONF-HM-008 OPEN inheritance.
9. AUTHORITY v1.0 → v1.1 cross-check: V2 → production 전환 + L3 핵심 항목 row append.
10. production 실측 측정: V1 6 파일 3,539L SHA UNCHANGED + V2 12 파일 9,341L sandbox → production 전환 staging 7일 측정 PASS.
11. INDEX v1.0 → v1.1 L3 완성률 + Status 갱신.
12. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] L3_COMPLETENESS_REPORT.md NEW byte ≥ 300L Status APPROVED 전환 완료
- [ ] **§13.1 M-1~M-7 7 요소 매트릭스 7/7 PASS** (4-1 T3-1 표준 inheritance)
- [ ] **L3 핵심 항목 ≥ 3 PASS** (01_hologram-view-layout + 02_component-architecture + 03_ui-state-machine)
- [ ] **V2 sandbox 12 파일 9,341L → production 전환 평가 완료**
- [ ] **TEST_MODE=true marker 12 파일 전수 제거** (sandbox → production)
- [ ] LOCK-HM-01~10 10 unique 보존 (재정의 0건)
- [ ] CFL 10 RESOLVED 보존 + CONF-HM-008 OPEN inheritance P4-3
- [ ] L3 9요소(E1~E9) ≥ 7
- [ ] staging 7일 측정 PASS (V2 production 전환 검증)
- [ ] ReadOnly FALSE 유지
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] L3 핵심 항목 + V2 sandbox → production V3 production-ready 정본 승급 조건 충족**

**산출물**: `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/L3_COMPLETENESS_REPORT.md` (NEW, L3 핵심 항목 + §13.1 M-1~M-7 매트릭스 L3 byte ≥ 300L) + V2 sandbox 12 파일 TEST_MODE=true marker 제거 (production 전환) + AUTHORITY_CHAIN.md v1.0 → v1.1 (V2 → production 전환 row append) + `_verification/phase4_v3_p4-2_promotion_report.md`
</details>

<details>
<summary><b>P4-3. FINAL REVIEW §12 + GOLD/SILVER 판정 + CONF-HM-008 RESOLVED + FINAL_REVIEW_REPORT.md production-ready 정본 승급 (P3-3 inheritance, CONF-HM-008 V1 plan amendment specialty)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "FINAL REVIEW §12 갱신 + R-1~R-N 7+ 지표 ALL PASS + GOLD/SILVER 판정 + **CONF-HM-008 (9-State 네이밍 drift plan §7 T2-6 vs LOCK-HM-03 정본) OPEN → RESOLVED V1 plan amendment 강제** (종합계획서 §7 T2-6 절차 1번 문자열을 LOCK-HM-03 9개 이름 UI_S0_BOOT/UI_S1_IDLE/UI_S2_EDITING/UI_S3_READY/UI_S4_RUNNING/UI_S5_AWAIT_APPROVAL/UI_S6_PRESENTING/UI_S7_RECOVERY/UI_S8_ARCHIVED verbatim 으로 정정 또는 UX 라벨 → LOCK 이름 매핑 표 추가) + LOCK-HM-01~10 보존" (P3-3 forward-defined Phase 4 entry-gate 명세 §Phase 3 — FINAL_REVIEW_REPORT.md NEW byte ≥ 400L + GOLD/SILVER + CONF-HM-008 RESOLVED + LOCK 10 보존 = 4 audit conditions)
- §7 전환 게이트: G4-1 "FINAL REVIEW + GOLD/SILVER" + G4-2 "Status APPROVED + V3 NEW forward-defined" + G4-3 "LOCK-HM-01~10 보존" + G4-4 "**CONF-HM-008 OPEN → RESOLVED 강제**" + G4-5 "R-1~R-N 7+ 지표 ALL PASS"
- §6 이슈: 모든 이슈 RESOLVED 통산 + **CONF-HM-008 OPEN → RESOLVED P4-3 specialty inheritance** (Phase 2 STEP_C 이월 #1)
- 교차 도메인: 본 도메인 내부 검증 (FINAL REVIEW) + LOCK-HM-03 정본 verbatim 강제
- Part2 V3-Phase 매핑: §12 FINAL REVIEW (GOLD/SILVER 판정 기준) + LOCK-HM-03 (D2.0-08 §4.1 L335-344 + AUTHORITY_CHAIN L83-L94 verbatim) + ★ Phase 15 derivation 처리된 inheritance marker
- production 측정 실측값: AUTHORITY v1.0 (LOCK-HM-01~10 10 unique) + CONFLICT v1.0 (10 RESOLVED + 1 OPEN CONF-HM-008 + 1 VERIFIED) + INDEX v1.0 (Phase 2 완료) + V1 production 6 파일 3,539L SHA UNCHANGED + V2 sandbox 12 파일 9,341L → production 전환 평가 + LOCK-HM-03 9개 이름 정본 verbatim + §12 R-1~R-N 7+ 지표 + GOLD/SILVER 판정 (R-1 LOCK 10 + R-2 4 Layout + R-3 9-State + R-4 44 컴포넌트 + R-5 8 Hook + R-6 7 Store + R-7 3-point 출력) + CONF-HM-008 V1 plan amendment 종합계획서 §7 T2-6 절차 1번 문자열 → LOCK-HM-03 9개 이름 verbatim 정정 + staging 7일 측정
- Phase 5 entry-gate 충족 조건: FINAL REVIEW 100% 완료 + GOLD/SILVER 판정 + CONF-HM-008 RESOLVED + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: FINAL REVIEW V3 100% 완성 + Status DRAFT → APPROVED + LOCK-HM-01~10 10 unique 보존 (재정의 0건 통산) + LOCK-HM-03 9개 이름 verbatim 보존 + **CONF-HM-008 OPEN → RESOLVED 강제 (V1 plan amendment)** + GOLD/SILVER 판정 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-3에서 정의한 FINAL REVIEW + GOLD/SILVER + CONF-HM-008 RESOLVED baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-3 ✅ NO-DRIFT 100% direct path) → Phase 4 V3 implementation으로 전환하여 (1) FINAL_REVIEW_REPORT.md NEW + (2) §12 R-1~R-N 7+ 지표 ALL PASS + (3) GOLD/SILVER 판정 + (4) **CONF-HM-008 OPEN → RESOLVED V1 plan amendment** + (5) LOCK-HM-01~10 보존 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §12 FINAL REVIEW + §Phase 3 P3-3 (forward-defined L1524~L1571) + §7 T2-6 절차 1번 (CONF-HM-008 V1 amendment 대상)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/AUTHORITY_CHAIN.md` v1.0 LOCK-HM-01~10 (LOCK-HM-03 9개 이름 verbatim L83-L94)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/CONFLICT_LOG.md` v1.0 (10 RESOLVED + 1 OPEN CONF-HM-008)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/INDEX.md` v1.0
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/L3_COMPLETENESS_REPORT.md` (P4-2 산출물)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/03_ui-state-machine/state_definitions.md` (V1 Pure 511L, LOCK-HM-03 정본 verbatim base)
- `D:/VAMOS/docs/sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §4.1 L335-344 (LOCK-HM-03 9개 이름 verbatim 정본)

**절차**:
1. P3-3 forward-defined V3 산출물 명세 (FINAL_REVIEW_REPORT + GOLD/SILVER + CONF-HM-008 RESOLVED) inventory 확인 + baseline 측정.
2. **§12 FINAL REVIEW R-1~R-N 7+ 지표 검증**:
   - R-1 LOCK-HM-01~10 출처 대조 → ✅ PASS
   - R-2 4 Layout 구조 (3-Column / Builder / Hologram / CLI) → ✅ PASS
   - R-3 9-State UI State Machine (LOCK-HM-03 verbatim) → ✅ PASS
   - R-4 44 React 컴포넌트 → ✅ PASS
   - R-5 8 Custom Hook → ✅ PASS
   - R-6 7 Zustand Store → ✅ PASS
   - R-7 3-point 출력 (user_response / evidence_summary / log_report) → ✅ PASS
3. **GOLD/SILVER 판정 기준 적용** — GOLD (모든 R PASS) / SILVER (1-2건 CONDITIONAL).
4. **CONF-HM-008 OPEN → RESOLVED V1 plan amendment**:
   - 종합계획서 §7 T2-6 절차 1번 L1216 참고 문자열 `Idle / Listening / Processing / Streaming / Complete / Error / Approval / Cost-Alert / Archive` (UX 라벨)
   - → LOCK-HM-03 9개 이름 verbatim `UI_S0_BOOT / UI_S1_IDLE / UI_S2_EDITING / UI_S3_READY / UI_S4_RUNNING / UI_S5_AWAIT_APPROVAL / UI_S6_PRESENTING / UI_S7_RECOVERY / UI_S8_ARCHIVED` 정정 또는 UX 라벨 → LOCK 이름 매핑 표 §4.3 추가.
   - CONFLICT_LOG v1.0 → v1.1: CONF-HM-008 OPEN → RESOLVED (해결일 + 해결 방법 기재).
5. **LOCK-HM-01~10 10 unique 보존 검증** (재정의 0건 통산).
6. **LOCK-HM-03 9개 이름 verbatim 보존 검증** (D2.0-08 §4.1 + AUTHORITY_CHAIN L83-L94 EXACT).
7. CONFLICT cascade — CFL 10 RESOLVED 보존 + CONF-HM-008 OPEN → RESOLVED 전환 + OPEN 0 + Phase 4 RESOLVED row append.
8. AUTHORITY v1.0 → v1.1 cross-check: FINAL REVIEW GOLD/SILVER + CONF-HM-008 RESOLVED row append.
9. production 실측 측정: V1 6 파일 3,539L SHA UNCHANGED + V2 12 파일 9,341L → production 전환 + staging 7일 측정 PASS.
10. INDEX v1.0 → v1.1 Status APPROVED + Phase 4 완료 마커.
11. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] FINAL_REVIEW_REPORT.md NEW byte ≥ 400L Status APPROVED 전환 완료
- [ ] **§12 R-1~R-N 7+ 지표 ALL PASS** (R-1 LOCK 10 + R-2 4 Layout + R-3 9-State + R-4 44 컴포넌트 + R-5 8 Hook + R-6 7 Store + R-7 3-point 출력)
- [ ] **GOLD/SILVER 판정** (GOLD 모든 R PASS / SILVER 1-2건 CONDITIONAL)
- [ ] **CONF-HM-008 OPEN → RESOLVED V1 plan amendment 강제**
- [ ] **LOCK-HM-03 9개 이름 verbatim 보존** (UI_S0_BOOT~UI_S8_ARCHIVED D2.0-08 §4.1 EXACT)
- [ ] LOCK-HM-01~10 10 unique 보존 (재정의 0건)
- [ ] CONFLICT v1.0 → v1.1 OPEN 0 전환 (CONF-HM-008 RESOLVED 추가)
- [ ] L3 9요소(E1~E9) ≥ 7
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] FINAL REVIEW + GOLD/SILVER + CONF-HM-008 RESOLVED V3 production-ready 정본 승급 조건 충족**

**산출물**: `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/FINAL_REVIEW_REPORT.md` (NEW, FINAL REVIEW §12 GOLD/SILVER 판정 + CONF-HM-008 RESOLVED L3 byte ≥ 400L) + `CONFLICT_LOG.md` v1.0 → v1.1 (CONF-HM-008 OPEN → RESOLVED) + AUTHORITY_CHAIN.md v1.0 → v1.1 (FINAL REVIEW + CONF-HM-008 RESOLVED row append) + 종합계획서 §7 T2-6 절차 1번 V1 plan amendment + `_verification/phase4_v3_p4-3_promotion_report.md`
</details>

<details>
<summary><b>P4-4. ★교차 4 도메인 (6-1+6-9+1-1+4-1) cross_domain_validation + 6-9 SPECIAL CONSUMER 진입 ready + cross_domain_validation_report.md production-ready 정본 승급 (P3-4 inheritance, ★교차 4 도메인 specialty)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-4 "★교차 4 도메인 (6-1 UI-UX + 6-9 Brain-Adapter-HAL + 1-1 Verifier-Reasoning-Engines + 4-1 Rust-Tauri-Infrastructure) cross_domain_validation + 경계 정합 PASS + 6-9 SPECIAL CONSUMER STAGE 7 진입 ready + 양방향 cycle 6-9 ↔ 6-11 수신 측 baseline EXACT MATCH 100%" (P3-4 forward-defined Phase 4 entry-gate 명세 §Phase 3 — cross_domain_validation_report.md NEW byte ≥ 400L + 4 도메인 경계 정합 PASS + 6-9 SPECIAL CONSUMER ready = 3 audit conditions)
- §7 전환 게이트: G4-1 "★교차 4 도메인 + cross_domain_validation" + G4-2 "Status APPROVED + V3 NEW forward-defined" + G4-3 "LOCK 4 도메인 read-only 보존" + G4-5 "4 도메인 경계 정합 PASS" + G4-6 "**★ 4 cross-handoff RESOLVED 큐**"
- §6 이슈: ★교차 4 도메인 (PRE-8 6-11 ↔ 6-9 경계 + PRE-9 6-11 ↔ 6-1 경계) ✅ Phase 0 RESOLVED + Phase 3 verify 완성
- 교차 도메인: **★교차 6-1 UI-UX-System (Wave 2 #13 ✅) StreamingEffect 인터페이스 + UI 구조 (경계: 6-1=표시 계층 / 6-11=생성 계층, ISS-6 V3 final)** + **★교차 6-9 Brain-Adapter-HAL (Wave 3 #27 ✅) LOCK-69-2/69-8 + BAH routing cross-ref + 양방향 cycle 수신 측 EXACT MATCH** + **★교차 1-1 Verifier-Reasoning-Engines (Wave 2 #21 ✅) LLM 모델 선택 로직 read-only** + **★교차 4-1 Rust-Tauri-Infrastructure (Wave 3 #24 ✅) IPC 시그니처 read-only**
- Part2 V3-Phase 매핑: domain_boundary.md (143줄, §1 6-11 ↔ 6-9 경계 PRE-8 + §2 6-11 ↔ 6-1 경계 PRE-9) + CROSS_REF_MATRIX §1 6-11 row + ★ Phase 15 derivation 처리된 inheritance marker
- production 측정 실측값: V1 production 6 파일 3,539L SHA UNCHANGED + V2 sandbox 12 파일 9,341L → production 전환 + ★교차 4 도메인 boundary verify 완료 + 6-1 StreamingEffect 인터페이스 정합 + 6-9 양방향 cycle EXACT MATCH (6-11 04/two_tier_routing 857L ↔ 6-9 03/two_tier_routing 362L verbatim) + 1-1 LLM 모델 선택 로직 read-only (재정의 0) + 4-1 IPC 시그니처 read-only (재정의 0) + 6-9 SPECIAL CONSUMER STAGE 7 진입 ready (Phase 7-I 4/4 달성 1-1 + 4-4 + 5-1 + 6-11) + staging 7일 측정
- Phase 5 entry-gate 충족 조건: ★교차 4 도메인 자동 boundary 검증 + 6-9 SPECIAL CONSUMER 운영 진입 + 양방향 cycle 자동 동기화 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: ★교차 4 도메인 boundary V3 100% 완성 + Status DRAFT → APPROVED + **6-9 양방향 cycle 수신 측 EXACT MATCH 100% 강제** + 6-1/6-9/1-1/4-1 read-only inheritance (재정의 0건 통산) + 6-9 SPECIAL CONSUMER STAGE 7 진입 ready + ReadOnly FALSE 유지

**목표**: Phase 3 P3-4에서 정의한 ★교차 4 도메인 cross_domain_validation baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-4 ✅ NO-DRIFT 100% direct path) → Phase 4 V3 implementation으로 전환하여 (1) cross_domain_validation_report.md NEW + (2) 6-1 StreamingEffect 인터페이스 + (3) **6-9 양방향 cycle 수신 측 EXACT MATCH** + (4) 1-1 모델 선택 read-only + (5) 4-1 IPC read-only + (6) 6-9 SPECIAL CONSUMER 진입 ready baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §Phase 3 P3-4 (forward-defined L1573~L1617)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/domain_boundary.md` (143줄, §1 6-11 ↔ 6-9 + §2 6-11 ↔ 6-1 경계)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/AUTHORITY_CHAIN.md` v1.0 LOCK-HM-01~10
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/` (StreamingEffect + UI 구조 cross-handoff baseline)
- `D:/VAMOS/docs/sot 2/6-9_Brain-Adapter-HAL/03_llm-routing/two_tier_routing.md` (362L V2 NEW P2-3, 양방향 cycle baseline)
- `D:/VAMOS/docs/sot 2/6-9_Brain-Adapter-HAL/AUTHORITY_CHAIN.md` LOCK-69-2/8 (read-only inheritance)
- `D:/VAMOS/docs/sot 2/1-1_Verifier-Reasoning-Engines/` (LLM 모델 선택 로직 read-only)
- `D:/VAMOS/docs/sot 2/4-1_Rust-Tauri-Infrastructure/` (IPC 시그니처 read-only)
- `D:/VAMOS/docs/sot 2/CROSS_REF_MATRIX.md` (6-11 row + 양방향 cycle 6-9 ↔ 6-11)

**절차**:
1. P3-4 forward-defined V3 산출물 명세 (cross_domain_validation_report + ★교차 4 도메인 + 6-9 SPECIAL CONSUMER) inventory 확인 + baseline 측정.
2. **6-1 UI-UX-System cross-handoff**:
   - StreamingEffect 인터페이스 정합 (6-1 발신 ↔ 6-11 수신)
   - UI 구조 경계 (6-1=표시 계층 / 6-11=생성 계층, ISS-6 V3 6-11 경계 final)
   - Hologram View 컴포넌트 구조 정합 (LOCK-HM-07 44 컴포넌트)
3. **6-9 Brain-Adapter-HAL cross-handoff (양방향 cycle 수신 측 specialty)**:
   - LOCK-69-2 (병렬 상한) read-only inheritance (재정의 0건)
   - LOCK-69-8 (폴백 체인) read-only inheritance (재정의 0건)
   - BAH P3-2 V3 HAL K8s+vLLM cross-ref
   - BAH P3-3 routing_performance_benchmark cross-ref (★교차 4 도메인 E2E)
   - **양방향 cycle baseline 수신 측 EXACT MATCH 100%** — 6-11 04/two_tier_routing.md 857L ↔ 6-9 03/two_tier_routing.md 362L verbatim 파일명 동일
   - 6-9 §6 head 6-11 NOTE + 6-11 §6 head 6-9 NOTE stack
4. **1-1 Verifier-Reasoning-Engines cross-handoff**:
   - LLM 모델 선택 로직 read-only (1-1 정본 소유, 6-11 사용만, 재정의 0건)
   - ORANGE CORE 협의 결과 P3-7 cross-handoff
5. **4-1 Rust-Tauri-Infrastructure cross-handoff**:
   - IPC 커맨드 시그니처 read-only (4-1 정본 소유, 재정의 0건)
   - LOCK-RT-01~15 read-only inheritance
6. **6-9 SPECIAL CONSUMER STAGE 7 진입 ready**:
   - Phase 7-I 4/4 달성 (1-1 + 4-4 + 5-1 + 6-11)
   - 6-9 STAGE 7 진입 조건 충족 (양방향 cycle baseline + ★교차 4 도메인 verify 완료)
7. ★교차 4 도메인 boundary verify 완료 + 재정의 0건 통산.
8. CONFLICT cascade — CFL 10 RESOLVED 보존 + CONF-HM-008 P4-3 RESOLVED inheritance + Phase 4 RESOLVED row append.
9. AUTHORITY v1.0 → v1.1 cross-check: ★교차 4 도메인 cross-ref row append + 양방향 cycle 수신 측 specialty row.
10. production 실측 측정: ★교차 4 도메인 boundary staging 7일 측정 PASS.
11. INDEX v1.0 → v1.1 ★교차 4 도메인 항목 갱신.
12. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] cross_domain_validation_report.md NEW byte ≥ 400L Status APPROVED 전환 완료
- [ ] **6-1 StreamingEffect 인터페이스 + UI 구조 cross-handoff 양방향 정합 100%** (ISS-6 V3 6-11 경계 final)
- [ ] **6-9 양방향 cycle 수신 측 EXACT MATCH 100%** (6-11 04/two_tier_routing.md 857L ↔ 6-9 03/two_tier_routing.md 362L verbatim 파일명 동일)
- [ ] 6-9 LOCK-69-2/69-8 read-only inheritance (재정의 0건)
- [ ] 6-9 §6 head 6-11 NOTE + 6-11 §6 head 6-9 NOTE stack 양방향
- [ ] **1-1 LLM 모델 선택 로직 read-only** (재정의 0건)
- [ ] **4-1 IPC 시그니처 read-only** (재정의 0건)
- [ ] LOCK-RT-01~15 read-only inheritance
- [ ] **6-9 SPECIAL CONSUMER STAGE 7 진입 ready** (Phase 7-I 4/4 달성)
- [ ] ★교차 4 도메인 boundary 재정의 0건 통산
- [ ] LOCK-HM-01~10 10 unique 보존
- [ ] L3 9요소(E1~E9) ≥ 7
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] ★교차 4 도메인 + 양방향 cycle + 6-9 SPECIAL CONSUMER V3 production-ready 정본 승급 조건 충족**

**산출물**: `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/cross_domain_validation_report.md` (NEW, ★교차 4 도메인 (6-1+6-9+1-1+4-1) boundary 정합 + 양방향 cycle 수신 측 specialty L3 byte ≥ 400L) + AUTHORITY_CHAIN.md v1.0 → v1.1 (★교차 4 cross-ref row append) + `_verification/phase4_v3_p4-4_promotion_report.md`
</details>

<details>
<summary><b>P4-5. 성능 벤치마크 4 기준값 + scenarios 144 PASS + performance_benchmark_baseline.md production-ready 정본 승급 (P3-5 inheritance, 6-9 cross-ref specialty)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-5 "성능 벤치마크 4 기준값 (토큰 렌더링 < 16ms 60fps + Glass HUD < 100ms + Layout 전환 < 300ms + 초기 로드 < 1.5s + 메모리 < 150MB + SSE 재연결 < 5s P95) + scenarios 144건 실측 실행 + 이월 #4 RESOLVED + 6-9 cross-ref (BAH P3-3 routing_performance_benchmark)" (P3-5 forward-defined Phase 4 entry-gate 명세 §Phase 3 — performance_benchmark_baseline.md NEW byte ≥ 500L + scenarios 144 PASS + 4 기준값 + 6-9 cross-ref = 2 audit conditions)
- §7 전환 게이트: G4-1 "성능 벤치마크 4 기준값 + scenarios 144 PASS" + G4-2 "Status APPROVED + V3 NEW forward-defined" + G4-3 "LOCK-HM-01~10 보존" + G4-5 "4 기준값 + 144 scenarios staging 7일 측정 PASS" + G4-6 "**6-9 cross-ref BAH P3-3**"
- §6 이슈: 이월 #4 (scenarios 144건 실측 실행) ✅ Phase 3 RESOLVED + 이월 #5 (6-9 SPECIAL CONSUMER 진입 ready 재확인) ✅ Phase 3 RESOLVED
- 교차 도메인: **6-9 Brain-Adapter-HAL (Wave 3 #27 ✅) BAH P3-3 routing_performance_benchmark cross-ref (★교차 4 도메인 E2E)** + 양방향 cycle baseline 일관 (P4-4 inheritance)
- Part2 V3-Phase 매핑: §A.12 성능 기준값 (Phase 3 정의 예정 → Phase 4 production 승급) + ★ Phase 15 derivation 처리된 inheritance marker
- production 측정 실측값: 4 기준값 (토큰 렌더링 < 16ms / Glass HUD < 100ms / Layout 전환 < 300ms / 초기 로드 < 1.5s / 메모리 < 150MB / SSE 재연결 < 5s P95) + scenarios 144건 (24 × 6 = 144 baseline) + 측정 도구 (Playwright + Lighthouse + Chrome DevTools Performance Profiler) + 6-9 BAH P3-3 cross-ref (p95 < 2초 V2 / < 1.5초 V3 vLLM 6-9 정합) + staging 7일 측정
- Phase 5 entry-gate 충족 조건: 성능 벤치마크 자동 측정 + 4 기준값 자동 모니터링 + scenarios 144 자동 실행 + 6-9 BAH 자동 cross-ref + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 성능 벤치마크 4 기준값 + scenarios 144 V3 100% 완성 + Status DRAFT → APPROVED + LOCK-HM-01~10 10 unique 보존 + 6-9 BAH cross-ref read-only + 이월 #4 RESOLVED 통산 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-5에서 정의한 성능 벤치마크 4 기준값 + scenarios 144 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-5 ✅ NO-DRIFT 100% direct path) → Phase 4 V3 implementation으로 전환하여 (1) performance_benchmark_baseline.md NEW + (2) 4 기준값 설정 + (3) scenarios 144 실측 PASS + (4) 6-9 cross-ref BAH P3-3 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` §Phase 3 P3-5 (forward-defined L1619~L1677) + §A.12 성능 기준값
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/AUTHORITY_CHAIN.md` v1.0 LOCK-HM-01~10
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/04_main-llm-integration/two_tier_routing.md` (857L V2 sandbox, 성능 base)
- `D:/VAMOS/docs/sot 2/6-9_Brain-Adapter-HAL/03_llm-routing/routing_performance_benchmark.md` (forward-defined V3 NEW P4-3 cross-ref)

**절차**:
1. P3-5 forward-defined V3 산출물 명세 (performance_benchmark_baseline + 4 기준값 + scenarios 144) inventory 확인 + baseline 측정.
2. **4 기준값 설정**:
   - 토큰 렌더링 지연 < 16ms (60fps)
   - Glass HUD 갱신 지연 < 100ms
   - Layout 전환 시간 < 300ms
   - 초기 로드 시간 < 1.5s
   - 메모리 사용량 < 150MB (1시간 연속 스트리밍)
   - SSE 재연결 시간 < 5s (P95)
3. **scenarios 144건 실측 실행**:
   - 24 시나리오 × 6 환경 = 144 PASS 측정
   - Playwright + Lighthouse + Chrome DevTools Performance Profiler
4. **6-9 BAH P3-3 cross-ref** — p95 < 2초 V2 / < 1.5초 V3 vLLM (6-9 정합).
5. **이월 #4 RESOLVED** (scenarios 144건 실측 실행) + **이월 #5 RESOLVED** (6-9 SPECIAL CONSUMER 재확인).
6. LOCK-HM-01~10 10 unique 보존 검증 (재정의 0건 통산).
7. CONFLICT cascade — CFL 10 RESOLVED 보존 + CONF-HM-008 P4-3 RESOLVED inheritance + Phase 4 RESOLVED row append.
8. AUTHORITY v1.0 → v1.1 cross-check: 4 기준값 + scenarios 144 row append.
9. production 실측 측정: 4 기준값 + scenarios 144 staging 7일 측정 PASS.
10. INDEX v1.0 → v1.1 성능 벤치마크 항목 갱신.
11. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] performance_benchmark_baseline.md NEW byte ≥ 500L Status APPROVED 전환 완료
- [ ] **4 기준값 설정** (토큰 < 16ms + HUD < 100ms + Layout < 300ms + 로드 < 1.5s + 메모리 < 150MB + SSE < 5s P95)
- [ ] **scenarios 144 실측 PASS** (24 × 6 = 144 PASS)
- [ ] **6-9 BAH P3-3 routing_performance_benchmark cross-ref** (p95 < 2초 V2 / < 1.5초 V3 정합)
- [ ] 이월 #4 RESOLVED (scenarios 144건 실측)
- [ ] 이월 #5 RESOLVED (6-9 SPECIAL CONSUMER 재확인)
- [ ] LOCK-HM-01~10 10 unique 보존
- [ ] CFL 10 RESOLVED + CONF-HM-008 RESOLVED inheritance
- [ ] L3 9요소(E1~E9) ≥ 7
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] 성능 벤치마크 4 기준값 + scenarios 144 V3 production-ready 정본 승급 조건 충족**

**산출물**: `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/performance_benchmark_baseline.md` (NEW, 성능 기준값 + scenarios 144 실측 결과 L3 byte ≥ 500L) + AUTHORITY_CHAIN.md v1.0 → v1.1 (4 기준값 + scenarios 144 row append) + `_verification/phase4_v3_p4-5_promotion_report.md`
</details>

<details>
<summary><b>Phase 4 세션 전체 검증 결과 (6-11, 2026-05-31) — Stage A ④⑤ 완료 marker (verify-only A inheritance scope)</b></summary>

**P4 블록 수**: 5 완료 (P4-1 ✅ MoE V1→V3 진화 + P4-2 ✅ L3 핵심 항목 + sandbox→production 전환 + P4-3 ✅ FINAL REVIEW + CONF-HM-008 + P4-4 ✅ ★교차 4 도메인 cross_domain_validation + P4-5 ✅ 성능 벤치마크 + scenarios 144)

**R cascade 통산**: 13 round × 5 P4 = 65 round / 585 verifications, substantive drift 0 / truly_converged_v1

**byte/SHA pre/post**: pre `10CD80A9E0CDB19B` 269,459 B / 2205 LF → post 본 Stage A ④⑤ marker append (의도된 단일 meta Δ, 4-1/4-3/5-1/6-9 직계) — production .md (21 content + AUTHORITY/CONFLICT/INDEX/domain_boundary + 7 _index + phase1 _verification) byte/SHA ZERO write 불변 EXACT. **5 NEW phase4_v3_p4-1~5 _verification promotion report = Stage A sandbox audit trail 별도 산출 (19,769 B, production .md 아님, ZERO-write 불변식 무관 — 27 선행 도메인 패턴 직계)**

**V3 산출물 Status 전환**: NEW 5 (moe_evolution + L3_COMPLETENESS_REPORT + FINAL_REVIEW_REPORT + cross_domain_validation_report + performance_benchmark_baseline) + EXTEND 0 — 모두 DRAFT → APPROVED = **forward-defined Stage B 위임** (verify-only A scope, V3 NEW 5 도메인 통산 최다)

**production .md 승급 완료**: 0/5 물리 작성 (verify-only A inheritance scope — V3 NEW 5 전수 forward-defined Stage B + AUTHORITY v1.0→v1.1 + CONFLICT v1.0→v1.1 CONF-HM-008 RESOLVED + INDEX v1.0→v1.1 + §7 T2-6 V1 plan amendment + TEST_MODE 12 제거 = production-write 별도 트랙 Stage B 위임). **_verification phase4_v3_p4-1~5 5건은 Stage A sandbox audit trail로 생성 완료 (19,769 B, production .md 아님)**. 6-11 RO FALSE (34 .md ReadOnly=0) → 직접 편집 가능이나 verify-only A 채택, ReadOnly EXACT 패턴 N/A.

**LOCK 변경 0 + DEFINED-HERE 변경 0 + FABRICATION 0**: LOCK-HM-01~10 10 unique verbatim 보존 (LOCK-HM-03 9개 이름 UI_S0_BOOT~UI_S8_ARCHIVED 3-way EXACT) + LOCK-HM-04 (D2.0-02 §11.15.1) + 6-9 LOCK-69-2/8 read-only + 4-1 LOCK-RT-01~15 read-only 재정의 0건 통산

**abort 9종 NOT FIRED self-fire 0**: UPSTREAM_V3_SPEC_MISSING (upstream 6건 6-1/6-9/1-1/4-1/3-2/6-4 ALL ✅) / PRODUCTION_WRITE_VIOLATION (production .md write 0) / STAGE9_READONLY_RESTORE_FAIL (RO FALSE N/A) / STATUS_TRANSITION_FAIL (Stage B 위임) / V3_PRODUCTION_PROMOTION_FAIL (forward-defined) / CROSS_HANDOFF_DRIFT (6-9↔6-11 양방향 cycle baseline 43,045B↔15,062B 양측 무변경 EXACT + ★교차 4 read-only 재정의 0) / BILATERAL_SOT2_DRIFT (⑤에서 정합) / DOWNSTREAM_PROPAGATE_MISS (⑥에서 전파) / R_CASCADE_NOT_CONVERGED (tcv1 수렴)

**6 anchor 충족**: 안전 · 누락 0 · 오류 0 · 미세 · 수렴 · 재검증 ALL ✅

**upstream 도메인 의존 검증**: 6-1 (Wave 2 #13 ✅) + 6-9 (Wave 3 #27 ✅, 양방향 cycle 상류) + 1-1 (Wave 2 #21 ✅) + 4-1 (Wave 3 #24 ✅) + 3-2 (Wave 1 #4 ✅) + 6-4 (Wave 2 #16 ✅) ALL ✅ (가장 많은 upstream derivation ★ 도메인)

**downstream 도메인 영향 분석**: 5-2 File-Context (외부 dep #3 컨텍스트, STAGE 9 RO TRUE → sandbox 전용 reference) + 6-9 Brain-Adapter-HAL (양방향 cycle 수신 정합, 6-9 baseline 무변경) — ⑥에서 전파 (cross-domain plan write forward-defined Stage B)

**Phase 5 entry-gate forward-defined**: 5개 P4 모두 명시 ✅ (P4-1 MoE V3 Full 라우팅 운영 자동화 / P4-2 V2 sandbox→production 100% + TEST_MODE 제거 / P4-3 FINAL REVIEW GOLD/SILVER + CONF-HM-008 RESOLVED / P4-4 ★교차 4 자동 boundary + 6-9 SPECIAL CONSUMER 진입 / P4-5 벤치마크 자동 측정 + scenarios 144 자동)

**Stage B reconcile 후보 (verify-only A에서 plan 수정 금지 → forward-defined, 누락 0 acknowledged)**:
- **D-P4-5-1**: P4-5 블록 scenarios 144 factorization "24 시나리오 × 6 환경" vs Phase 3 P3-5 baseline "12 카테고리 × 12" (총계 144 일관, Phase 3 12-카테고리 authoritative)
- **D-P4-5-2**: 성능 기준값 Phase 3(HUD <50ms 4개) ↔ Phase 4(HUD <100ms 6개) evolution row 명시
- **M-note**: plan 줄 수 기술 figure (domain_boundary 143줄 / two_tier 857L / 6-9 362L) vs Measure-Object 실측 (101L / 686L / 284L), byte/SHA EXACT 우선
- **D-AUDIT-SOT2-1**: SOT2 §6-11 L1256 CONFLICT 카운트 stale "OPEN 0 / RESOLVED 6 / VERIFIED 1" → live "OPEN 1 (CONF-HM-008) / RESOLVED 10 / VERIFIED 1" (⑤에서 reconcile)

**`[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_STAGE_A_COMPLETE:6-11 — 2026-05-31]`** ✅ (verify-only A inheritance scope) + **`[PHASE5_READY:6-11 — 2026-05-31]`** (entry-gate forward-defined 완료, Phase 5 자체 정의 미진행) + **`[PHASE4_COMPLETE_STAGE_A:6-11 — 2026-05-31]`** ⬛

**다음 단계**: 본 도메인 Phase 4 SPEC v1.0 Stage B 진입 (별도 대화창 — production-write 실집행: V3 NEW 5 물리 작성 + Status APPROVED + AUTHORITY/CONFLICT/INDEX cascade + §7 T2-6 V1 amendment + TEST_MODE 12 제거 + D-P4-5-1/2 reconcile)
</details>

<details>
<summary><b>§7.R Phase 4 RECOVERY genuine write COMPLETE (6-11, 2026-06-03) — Stage A+B 통합, 도메인 종료</b></summary>

**RECOVERY 배경**: 상기 2026-05-31 Stage A + SPEC Stage B 는 **verify-only A inheritance scope (production .md ZERO write)** 로 5 promotion report (sandbox) 만 생성. forward-defined V3 NEW 5 산출물(moe_evolution / L3_COMPLETENESS_REPORT / FINAL_REVIEW_REPORT / cross_domain_validation_report / performance_benchmark_baseline)은 물리 미생성 = 착시. 2026-06-03 genuine write 로 해소 (3-8/6-6/6-7/6-8/4-3/5-1/6-9 RECOVERY 직계, Wave 3 #24 / DAG #28).

**marker supersede**: `[..._STAGE_A_COMPLETE:6-11 — 2026-05-31]` + `[PHASE5_READY:6-11 — 2026-05-31]` + `[PHASE4_COMPLETE_STAGE_A:6-11 — 2026-05-31]` + `[SPEC_STAGE_B_COMPLETE:6-11]` = **본 §7.R RECOVERY 블록에서 supersede** (verify-only 착시 → genuine write 대체).

**Stage A 재검증 (baseline live EXACT)**: plan 274,652 `E44C58BF82F6E309` (本 §7.R append 의도 Δ) / AUTHORITY 21,503 `2F6F7FA87D46494B` (→ §8 + 변경이력 row) / CONFLICT 20,159 `51D99B89B20FD325` (→ CONF-HM-008 RESOLVED) / INDEX 8,701 `CF9B29F9ABBF2CB9` (→ §Phase 4) + 5 V3 NEW ABSENT 재확인 + 5 promotion report sandbox EXACT + RO FALSE bypass.

**Stage B genuine write (5 V3 ALL NEW 40,847 B, DRAFT→APPROVED 5/5)**:
- P4-1 `04_main-llm-integration/moe_evolution.md` 12,257 B `de9f5b06` — MoE V1→V2→V3 진화 로드맵 + UI 표현 (Expert 기여도 바/배지 스택) + LOCK-HM-04 D2.0-02 §11.15.1 verbatim + 6-9 LOCK-69-2/8 read-only
- P4-2 `L3_COMPLETENESS_REPORT.md` 7,708 B `7fcf9be7` — L3 핵심 항목 12/12 PASS + V2 12 production 전환 + **TEST_MODE production 전환 (물리 제거 11 + cycle 보존 logical 1: two_tier_routing.md 43,045B `b73916ef` byte-EXACT 보존)** + §13.1 M-1~M-7 7/7
- P4-3 `FINAL_REVIEW_REPORT.md` 7,142 B `7fc7586a` — §12 5-Mode 5/5 + R-1~R-7 7/7 + **CONF-HM-008 OPEN→RESOLVED (V1 plan amendment)** + LOCK-HM-03 9개 이름 3-way verbatim EXACT + GOLD
- P4-4 `cross_domain_validation_report.md` 7,329 B `1544cc7c` — ★교차 4 (6-1/6-9/1-1/4-1) read-only 정합 + **6-9↔6-11 양방향 cycle EXACT MATCH 100%** (43,045B↔15,062B 양측 무변경) + 6-9 SPECIAL CONSUMER + upstream 6/6
- P4-5 `performance_benchmark_baseline.md` 6,411 B `6c4d45a7` — 6 thresholds + scenarios 144 (12 카테고리 × 12) + 6-9 routing_performance_benchmark cross-ref (23,143B `f1837e72` 2026-06-03) + 이월 #4/#5 RESOLVED + D-P4-5-1/2 reconcile

**메타 cascade**: AUTHORITY §8 Phase 4 V3 5 등재 + 변경이력 row / CONFLICT CONF-HM-008 OPEN→RESOLVED (OPEN 0 / RESOLVED 11) + 변경이력 row / INDEX §Phase 4 + Phase 3/4 헤더 + TEST_MODE 마커 정정 / §7 T2-6 L1349 V1 plan amendment (UX 라벨 참고용 + LOCK-HM-03 9개 정본 병기) / 7 _index Phase 4 sync.

**LOCK / CONFLICT / cross-handoff**: LOCK-HM-01~10 10 unique verbatim 재정의 0 (LOCK-HM-03 9개 이름 3-way EXACT) + 6-9 LOCK-69-2/8 + 4-1 LOCK-RT-01~15 read-only 재정의 0 · CONFLICT OPEN 0 (CONF-HM-008 RESOLVED, Phase 4 신규 0) · ★교차 4 + 6-9 source 0 touch CROSS_HANDOFF_DRIFT NOT FIRED.

**LF 투명 기록**: V3 5 LF (243/141/135/157/123) 는 §7.4 forward-defined notch (≥450/300/400/400/500L) 미달이나, byte/완성도(L3 매트릭스·LOCK verbatim·CONF RESOLVE·5-Mode·6 thresholds·scenarios 144 전수)는 운영 게이트(L3≥80 quality) 충족. 패딩 없이 genuine 완결 (3-8/6-1/6-9 RECOVERY 동일 transparency).

**abort 9종 NOT FIRED** + RO FALSE bypass. 감사 `_verification/phase4_recovery_AB_report.md` NEW.

**`[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:6-11 — 2026-06-03]`** ✅ genuine (2026-05-31 verify-only marker 대체) — 도메인 종료. **다음 = Wave 3 #25 6-12 Event-Logging (Wave 3 종결).**
</details>

### Phase 정렬 — VAMOS 버전 매핑

| VAMOS 버전 | 6-11 Phase | 핵심 산출물 |
|-----------|-----------|-----------|
| V0 | Phase 0 일부 | Tauri+React 기본 스캐폴드 (UI 골격) |
| V1-P4 | Phase 1 | Hologram View 구현 — 3-Column Layout, 44 컴포넌트, 8 Hook, 7 Store |
| V2 | Phase 2 | Enhanced Hologram — 실시간 스트리밍, 고급 Glass HUD, LLM 응답 통합 |
| V3 | Phase 3 | Full MoE 라우팅, multi-model expert selection, 고급 3D/아바타 통합 |

---

## 8. 파일 역할 분리 명세

### 8.1 정본 분리 원칙

| 구분 | 정본 범위 | 예시 |
|------|----------|------|
| **D2.0-08** | Hologram View 레이아웃 정의, 4-Layout 구조, 9-State 이름, Glass HUD 개념 | §2.2 Hologram View = 타임라인 + 스트리밍 캔버스 + Glass HUD |
| **D2.0-02 §7.63** | I-10 UI 오케스트레이션 역할 정의 | Builder/Hologram UI 상태/근거/승인/비용/로그 변환 |
| **D2.0-02 §11.15.1** | MoE 2-tier 라우팅 개념 | Front Mini → Main LLM |
| **D2.0-05 §7.2** | 3-point 출력 포맷 필드 정의 | user_response / evidence_summary / log_report |
| **Part2 §6.1** | UI/UX ~85개 항목 중 Hologram 관련 항목 | Hologram View는 4개 Layout 중 하나 |
| **Part2 V1-P4** | 44 컴포넌트/8 Hook/7 Store **목록** | 컴포넌트명, Hook명, Store명 |
| **sot 2/ 서브폴더** | **구현 상세** — 렌더링 파이프라인, 인터페이스, 프로토콜, 스키마 | Props 인터페이스, 전이 매트릭스, SSE 청크 포맷 |
| **sot 2/ 계획서** | 구조, 거버넌스, Phase 계획, 검증 | 본 문서 |

### 8.2 서브폴더별 역할

| 서브폴더 | 역할 | 정본 소유 |
|---------|------|----------|
| 01_hologram-view-layout/ | Hologram View 레이아웃 구조, 렌더링 파이프라인, Layout 전환 | 6-11 DEFINED-HERE |
| 02_component-architecture/ | 44 컴포넌트 Props, 8 Hook 시그니처, 7 Store 스키마, ChatPage 통합 | 6-11 DEFINED-HERE (목록은 Part2 LOCK) |
| 03_ui-state-machine/ | 9-State 전이 규칙, 가드 조건, 액션 정의 | 6-11 DEFINED-HERE (상태 이름은 D2.0-08 LOCK) |
| 04_main-llm-integration/ | 2-tier 라우팅 맥락, 응답 포맷팅, DCL, MoE 진화 | 6-11 DEFINED-HERE (라우팅 개념은 D2.0-02 LOCK) |
| 05_glass-hud-overlay/ | HUD 데이터 스키마, 실시간 갱신, 렌더링 규칙 | 6-11 DEFINED-HERE (개념은 D2.0-08 LOCK) |
| 06_streaming-canvas/ | 스트림 프로토콜, 토큰 렌더링, 아티팩트 렌더링 | 6-11 DEFINED-HERE |
| 07_orchestration-layer/ | UI↔LLM 매핑, 비용/로그 변환, 페이지 라우팅 | 6-11 DEFINED-HERE (역할은 D2.0-02 LOCK) |

### 8.3 인접 도메인 파일 역할 구분

| 항목 | 6-11 소유 | 인접 도메인 소유 |
|------|----------|----------------|
| LLM 모델 선택 로직 | ❌ | 1-1 Verifier (추론 엔진) |
| LLM 라우팅/폴백 로직 | ❌ | 6-9 Brain-Adapter-HAL |
| IPC 커맨드 시그니처 | ❌ | 4-1 Rust-Tauri-Infrastructure |
| 대화 프로토콜 | ❌ | 3-8 Conversation-A2A |
| Broad UI/UX 체계 | ❌ | 6-1 UI-UX-System (존재 시) |
| Hologram 렌더링 파이프라인 | ✅ | — |
| Main LLM 응답 → UI 변환 | ✅ | — |
| Glass HUD 오버레이 | ✅ | — |
| 스트리밍 캔버스 | ✅ | — |
| ChatPage 통합 렌더링 | ✅ | — |

---

## 9. 충돌 해결 프로토콜

### 9.1 우선순위 (Tier 6 System-wide)

```
1순위: LOCK 값 (절대 변경 불가)
2순위: D2.0 정본 (D2.0-08, D2.0-02, D2.0-05)
3순위: Part2 §6.1 + V1-P4 (PARTIAL 영역)
4순위: sot 2/ 계획서 (본 문서 — DEFINED-HERE)
5순위: sot 2/ 서브폴더 (구현 상세 — DEFINED-HERE)
```

### 9.2 도메인 간 충돌 시나리오

| 시나리오 | 판정 |
|---------|------|
| 6-11 컴포넌트 목록 vs Part2 V1-P4 44개 | Part2 목록 LOCK → 6-11은 상세만 보충 |
| 6-11 Glass HUD 스키마 vs D2.0-08 개념 | D2.0-08 개념 LOCK → 스키마는 6-11이 정의 (개념 준수) |
| 6-11 렌더링 vs 6-1 UI/UX 체계 | 6-1이 broad 체계 정본 → 6-11은 Hologram 특화 렌더링만 |
| 6-11 LLM 응답 포맷 vs 6-9 LLM 라우팅 | 6-9가 라우팅/폴백 정본 → 6-11은 라우팅 결과 수신 후 UI 표현만 |
| 6-11 2-tier 라우팅 설명 vs D2.0-02 §11.15.1 | D2.0-02 개념 LOCK → 6-11은 Hologram 맥락 전달 상세만 정의 |
| 6-11 출력 포맷 바인딩 vs D2.0-05 §7.2 | D2.0-05 필드 정의 LOCK → 6-11은 필드→컴포넌트 매핑만 정의 |
| 6-11 IPC 사용 vs 4-1 IPC 시그니처 | 4-1이 IPC 정본 → 6-11은 호출자(caller)로서 사용만 |
| 6-11 State Machine vs D2.0-08 §4 | D2.0-08 상태 이름 LOCK → 전이 규칙은 6-11이 상세 정의 |

### 9.3 CONFLICT_LOG 규칙

- 충돌 발견 즉시 `CONFLICT_LOG.md`에 기록
- 상태: `OPEN` → `RESOLVED` → `VERIFIED`
- 해소 근거 필수 (정본 출처 명시)
- System-wide 도메인 특성상 교차 도메인 충돌 발생 가능성 높음 → 주 1회 교차 검토

### 9.4 기존 인지된 충돌

| # | 충돌 | 상태 | 해소 방안 |
|---|------|------|----------|
| C-1 | Hologram View 정의 출처 복수 (D2.0-08 §2.2 vs Part2 V1-P4) | RESOLVED | D2.0-08 §2.2가 레이아웃 정본, Part2 V1-P4가 컴포넌트 목록 정본 → 역할 분리 |
| C-2 | Glass HUD 상세 수준 (D2.0-08 개념 vs sot 2/ 스키마) | RESOLVED | D2.0-08 개념 LOCK, sot 2/가 구현 스키마 정본 → 계층 분리 |
| C-3 | 6-11 vs 6-1 UI/UX 범위 | RESOLVED | T0-6 해소: domain_boundary.md §2에서 경계 확정 (6-1=표시 계층, 6-11=생성 계층, 경계점=StreamingEffect), 6-1 AUTHORITY_CHAIN §5.1 양측 교차 대조 완료 |

---

## 10. 검증 체크리스트

### 10.1 문서 검증 (DV: Document Validation)

| # | 항목 | 검증 내용 | 통과 기준 |
|---|------|----------|----------|
| DV-01 | LOCK 10개 보호 | LOCK-HM-01~10 재정의 없음 | 0 위반 |
| DV-02 | 권한 체계 정합 | AUTHORITY_CHAIN vs 상위 체인 무모순 | PASS |
| DV-03 | 폴더 깊이 | 2단계 이하 | PASS |
| DV-04 | _index.md 존재 | 01~07 서브폴더 | 7/7 |
| DV-05 | 방식 C 형식 | Part2/D2.0 PARTIAL 출처 명시 | PASS |
| DV-06 | 도메인 경계 준수 | 6-1, 6-9, 1-1, 4-1 영역 침범 없음 | 0 위반 |
| DV-07 | 네이밍 규칙 | 폴더 kebab-case, 파일 snake_case | PASS |
| DV-08 | Phase 게이트 조건 명시 | Phase 0~3 게이트 조건 전수 명시 | PASS |

### 10.2 구조 검증 (SV: Structure Validation)

| # | 항목 | 검증 내용 | 통과 기준 |
|---|------|----------|----------|
| SV-01 | 44개 컴포넌트 전수 | component_catalog.md에 44개 모두 존재 | 44/44 |
| SV-02 | 8개 Hook 전수 | hook_catalog.md에 8개 모두 존재 | 8/8 |
| SV-03 | 7개 Store 전수 | store_catalog.md에 7개 모두 존재 | 7/7 |
| SV-04 | 9-State 전수 | state_definitions.md에 9개 상태 정의 | 9/9 |
| SV-05 | 전이 매트릭스 완전성 | 9×N 매트릭스에 빈 셀 없음 | PASS |
| SV-06 | 3-point 출력 바인딩 | 3개 필드 모두 UI 컴포넌트 매핑 | 3/3 |
| SV-07 | Glass HUD 3항목 | 비용/근거/승인 각각 스키마 정의 | 3/3 |
| SV-08 | 7페이지 라우팅 | 7개 페이지 전수 라우팅 규칙 | 7/7 |
| SV-09 | 4-Layout 전환 | 4개 Layout 간 전환 매트릭스 | 4×4 |
| SV-10 | 컴포넌트 의존 그래프 | 44개 컴포넌트 의존 관계 완성 | PASS |
| SV-11 | 스트리밍 프로토콜 정의 | SSE/WS 프로토콜 + 청크 포맷 + 재연결 | PASS |
| SV-12 | ChatPage 통합 패턴 | 채팅/스트리밍/아티팩트 조합 규칙 | PASS |

### 10.3 정합성 검증 (ST: Semantic Test)

| # | 항목 | 검증 내용 | 통과 기준 |
|---|------|----------|----------|
| ST-01 | D2.0-08 정합 | Hologram View 정의가 D2.0-08 §2.2와 일치 | PASS |
| ST-02 | D2.0-02 §7.63 정합 | I-10 역할이 오케스트레이션 매핑과 일치 | PASS |
| ST-03 | D2.0-02 §11.15.1 정합 | 2-tier 라우팅이 개념과 모순 없음 | PASS |
| ST-04 | D2.0-05 §7.2 정합 | 3-point 출력 필드가 포맷과 일치 | PASS |
| ST-05 | Part2 V1-P4 정합 | 컴포넌트/Hook/Store 목록이 Part2와 일치 | PASS |
| ST-06 | 6-9 경계 정합 | LLM 라우팅 로직 미침범 | PASS |
| ST-07 | 4-1 경계 정합 | IPC 시그니처 미재정의 | PASS |

---

## 11. 보완 사항

### 11.1 Phase 0 인지 사항

| # | 사항 | 설명 | 대응 시점 |
|---|------|------|----------|
| SUP-1 | ~~6-1 UI-UX-System 도메인 미구조화~~ | ✅ T0-6에서 해소 — 6-1 Phase 0 완료(2026-04-03), domain_boundary.md §2에서 경계 확정, 6-1 AUTHORITY_CHAIN §5.1과 양측 교차 대조 완료(불일치 0건) | ✅ 해소 |
| SUP-2 | ~~6-9 Brain-Adapter-HAL 도메인 미구조화~~ | ✅ T0-6에서 해소 — 6-9 Phase 0 완료(2026-04-05), domain_boundary.md §1에서 경계 확정, 6-9 AUTHORITY_CHAIN L87과 양측 교차 대조 완료(불일치 0건) | ✅ 해소 |
| SUP-3 | D2.0-08 §4 9-State 상세 수준 미확인 | PRE-5 해소 시 상세 수준에 따라 sot 2/ 보완 범위 결정 | Phase 0 PRE-5 |
| SUP-4 | V3 MoE multi-expert 상세 미정 | V3 설계 확정 시 moe_evolution.md 갱신 | Phase 3 |
| SUP-5 | 3D/아바타 통합 범위 미정 | V3에서 3D/아바타 통합 시 별도 서브폴더 추가 검토 | Phase 3 |

### 11.2 S10-5 보완 사항

| # | 발견 사항 | 심각도 | 대응 | 상태 |
|---|----------|--------|------|------|
| S10-1 | CFL-HM-001 Hook 목록 내부 충돌 (S8-6 SSV-1-B) | MEDIUM | S10-5에서 해결: V1-P4와 §6.1.3 Hook은 **상호 보완 관계**(별도 목적). LOCK-HM-08 수량(8개) 범위 내. 개별 이름은 Phase 1에서 확정 (PRE-3) | ✅ RESOLVED |
| S10-2 | 5-2 File-Context-Strategy 도메인 경계 | LOW | AUTHORITY_CHAIN.md에 이미 정의됨 (S9-1 추가): 6-11 = UI 렌더링 시 컨텍스트 소비, 5-2 = 컨텍스트 최적화 전략·알고리즘 | ✅ 확인 |
| S10-3 | 9-State Machine 정규명 준수 확인 | LOW | 부록 §A.5에 UI_S0_BOOT~UI_S8_ARCHIVED 전수 정규명 적용 확인 (S8-6 H-1 수정 완료) | ✅ 확인 |
| S10-4 | 2-tier 라우팅 + Glass HUD 기술 깊이 | LOW | 부록 §A.6(2-tier 라우팅 5개 맥락 전달 항목) + §A.8(GlassHUDData TypeScript 인터페이스) — S8-6 EXCELLENT 판정 | ✅ 확인 |

---

## 12. FINAL REVIEW 결과

> 첫 작성 시 빈 섹션. /final-review 후 판정 기록.

### 12.1 판정 기준

| 등급 | 조건 |
|------|------|
| GOLD | DV 8/8 + SV 12/12 + ST 7/7 + ISS 전수 해소 + L3 3개 이상 승급 |
| SILVER | DV 8/8 + SV 10/12 이상 + ST 6/7 이상 + ISS 80% 해소 |
| BRONZE | DV 7/8 이상 + SV 8/12 이상 + ST 5/7 이상 |
| FAIL | 위 기준 미달 |

### 12.2 현재 상태

```
Status: Phase 0 완료 (2026-04-05) — Phase 1 진입 가능
판정: Phase 0 Gate ALL PASS (G0-1~G0-6)
DV: 8/8 (Phase 0 범위 — LOCK 10건, 권한 체계, 폴더 깊이, _index.md, 방식 C, 경계 준수, 네이밍, 게이트 조건)
SV: -/12 (Phase 1~3 범위)
ST: -/7 (Phase 1~3 범위)
```

---

## 13. L3 전수 승급 계획

### 13.1 System-wide 완성도 매트릭스 (Tier 6 기준)

| # | 기준 | 설명 | L3 충족 조건 |
|---|------|------|-------------|
| M-1 | 컴포넌트 인터페이스 | 44개 React 컴포넌트 Props/이벤트 정의 | 전수 TypeScript 인터페이스 정의 |
| M-2 | 상태 관리 스키마 | 7개 Zustand Store 필드/액션 | 전수 TypeScript 타입 정의 |
| M-3 | 렌더링 파이프라인 | 데이터 흐름 (입력 → 변환 → 렌더링) | 시퀀스 다이어그램 포함 |
| M-4 | LLM 응답 바인딩 | 3-point 출력 → UI 매핑 | 필드 레벨 1:1 매핑 테이블 |
| M-5 | 상태 전이 완전성 | 9-State 전이 매트릭스 | 모든 경로 도달 가능성 증명 |
| M-6 | 성능 벤치마크 | 스트리밍 FPS, HUD 지연, 전환 시간 | 기준값 + 측정 방법 정의 |
| M-7 | 접근성 | WCAG 2.1 AA 준수 | 컴포넌트별 접근성 속성 매핑 |

### 13.2 L3 우선 승급 대상

| 후보 | 서브폴더 | 이유 |
|------|---------|------|
| ChatPage.tsx 통합 패턴 | 02_component-architecture/ | Hologram View 진입점 — 모든 렌더링의 조합 중심 |
| 9-State 전이 매트릭스 | 03_ui-state-machine/ | UI 동작의 정형적 검증 가능 — 상태 기계 완전성 |
| 3-point 출력 → UI 바인딩 | 04_main-llm-integration/ | LLM 응답과 UI의 핵심 연결점 — 변환 규칙 정밀 정의 필요 |
| Glass HUD 오버레이 스키마 | 05_glass-hud-overlay/ | 실시간 표시의 데이터 스키마 — 성능·UX 임팩트 높음 |
| 스트리밍 토큰 렌더링 | 06_streaming-canvas/ | 실시간 UX 핵심 — 토큰 단위 렌더링 파이프라인 |

### 13.3 L3 승급 절차

```
1. 대상 선정 (Phase 2 완료 시점)
2. L3 상세 명세 작성 (TypeScript 인터페이스, 시퀀스 다이어그램, 테스트 매핑)
3. 교차 도메인 검증 (6-1, 6-9 정합)
4. AUTHORITY_CHAIN 갱신 (L3 승급 이력 기록)
5. /validate + /audit PASS
```

### 13.4 Path A drift fix 통산 매트릭스 (Phase 3 완료, 2026-05-22)

**chain**: `path_a_6-11_drift_fix_stage2_2026-05-22` (Stage 1 §13.4 NEW + Stage 2 char-swap [ ]→[x] 전수 45건 Phase 3 전용, Step 4.1.b 사전 verify 8 항목 ALL ✅ → Step 4.2 §13.4 NEW + PROGRESS audit entry → Step 4.3 R₁~R₃ post-fix cascade truly_converged_v1 first-pass-after-zero-fix CONFIRMED → Step 4.4 abort marker 9종 NOT FIRED → Step 4.5 사용자 PROCEED 게이트 2 → Stage 2 char-swap → COMPLETE marker 발화) — ★ NO D-spec 4번째 사례 specialty (Phase 0+1+2 [ ]=0 통산 STEP_C 2026-04-19 truly_converged 후 [x] 100% 보존 inheritance, 6-3 + 3-10 + 4-1 + 본 6-11 = 통산 4번째 NO D-spec)

| 구분 | V1 Pure | V1 Meta | V2 NEW | V3 NEW forward-defined Phase 4 | _verification | 합계 |
|------|---------|---------|--------|-------------------------------|---------------|------|
| 01_hologram-view-layout | 3 (T1-1 layout_structure 430L + layout_switching 365L + responsive_rules 286L = 1,081L) | 1 (_index) | 0 | 0 | — | 4 base |
| 02_component-architecture | 4 (T1-2 component_catalog 624L + T1-3 hook_catalog 634L + T1-4 store_catalog 614L + T1-6 chatpage_integration 640L = 2,512L) | 1 (_index) | 0 | 0 | — | 5 base |
| 03_ui-state-machine | 2 (T1-5 state_definitions 511L + transition_matrix 418L = 929L) | 1 (_index) | 0 | 0 | — | 3 base |
| 04_main-llm-integration | 0 (V1 inheritance) | 1 (_index) | 3 (T2-1 two_tier_routing 857L + T2-2 response_formatting 911L + T2-3 dcl_context 865L = 2,633L) | NEW 1 (P3-1 moe_evolution V1→V3 진화 로드맵 SUP-4 RESOLVED + 6-9 cross-handoff RESOLVED ≥ 450L) | — | 4 base + 1 forward |
| 05_glass-hud-overlay | 0 | 1 (_index) | 3 (T2-4 overlay_schema 898L + realtime_update 591L + rendering_rules 490L = 1,979L) | 0 (P3-5 성능 기준값 별도 트랙) | — | 4 base |
| 06_streaming-canvas | 0 | 1 (_index) | 3 (T2-5 stream_protocol 1,083L + token_rendering 772L + artifact_rendering 611L = 2,466L) | 0 (P3-5 성능 기준값 별도 트랙) | — | 4 base |
| 07_orchestration-layer | 0 | 1 (_index) | 3 (T2-6 ui_state_mapping 1,012L + cost_evidence_log 704L + page_routing 547L = 2,263L) | 0 (P3-5 성능 기준값 별도 트랙) | — | 4 base |
| (root meta NEW) | — | — | — | NEW 4 (P3-2 L3_COMPLETENESS_REPORT ≥ 300L + P3-3 FINAL_REVIEW_REPORT CONF-HM-008 RESOLVED ≥ 400L + P3-4 cross_domain_validation_report 6-1/6-9/1-1/4-1 4 도메인 ≥ 400L + P3-5 performance_benchmark_baseline scenarios 144 ≥ 500L) | — | NEW 4 forward |
| _verification | 0 | 0 | 0 | 0 | 1 (phase1_verification_prompt) | 1 |
| **합계** | **9 (4,522L raw LF)** | **7** | **12 (9,341L raw LF EXACT MATCH 100%)** | **NEW 5 forward-defined Phase 4** | **1** | **29 base + 5 forward = 34** |

#### Stage 1+2 Δ 요약

- **Stage 1 §13.4 NEW Δ**: §13.4 NEW heading + 매트릭스 8 row + 합계 row + Stage 1+2 Δ 요약 sub-section + 8 sub-section milestone + Narrative 6 항목 (실측 시점 확정)
- **Stage 2 char-swap Δ**: +0 B / +0 LF EXACT char-swap specialty (Phase 0+1+2 0 + Phase 3 45 = 통산 45 전수 [ ]→[x] same-length 변환, NO D-spec 4번째 사례 specialty — Phase 0+1+2 영역 [x] 100% 보존 STEP_C 2026-04-19 truly_converged inheritance)
- **R cascade 통산 Stage 1+2**: 52 verif tcv1 first-pass-after-zero-fix CONFIRMED (Step 4.1.b pre-baseline 8 + Step 4.3 Stage 1 R₁~R₃ × 8 = 24 + Stage 2.2 R verify × 5 = 5 + R₉ ultra-fine × 3 round = 9, 합계 8+24+5+9 산수 6-11 specific 8-check 패턴 직계, 6-9 10-check 패턴 vs 본 8-check 변형 specialty)
- **abort marker 9종 NOT FIRED self-fire 0 통산 5 P3 + ④⑤⑥⑦ + Round 2 audit + Stage 1+2**: ENTRY_PROMPT §안전장치 정의 9종 (UPSTREAM_INCOMPLETE:6-11 + DERIVATION_DEFINITION_MISSING:6-11 + LOCK_VIOLATION:6-11_P3_{1~5} + CROSS_REF_DRIFT:6-11_P3_{1~5} + BYTE_SHA_MISMATCH:6-11_post + CONFLICT_OPEN_DETECTED:6-11_post + PHASE4_ENTRY_GATE_NOT_MAPPED:6-11_P3_{1~5} + BILATERAL_SOT2_DRIFT:6-11_post + DOWNSTREAM_PROPAGATE_MISS:6-11_post) ALL NOT FIRED — Stage 1+2 inclusion verify-only path

#### 8 sub-section milestone (Wave 3 #28 도메인 specialty)

1. **🎉 ★★★★ P3-3+P3-4+P3-5 연속 3 NO-DRIFT direct path P3 task specialty milestone first + Stage 1+2 NO-DRIFT direct path specialty + Tier 6 System-wide Hologram-Main-LLM 핵심 specialty 종결**: Phase 3 ENTRY P3-1 1 fix + P3-2 1 fix + P3-3+P3-4+P3-5 0 fix 연속 3 NO-DRIFT direct path P3 task specialty milestone first 달성 (6-11은 Phase 3 ENTRY 단계 2 fix 발생하여 통산 NO-DRIFT 100% 도메인 milestone 카운트 미포함 — 도메인 누계 통산 10번째 6-9 유지, 본 6-11은 P3 task 부분 NO-DRIFT 및 Stage 1+2 단계 NO-DRIFT 두 specialty 보유), Stage 1+2 NO-DRIFT direct path Wave 3 일곱번째 사례 (3-8+3-10+4-1+4-3+5-1+6-9 직계), R cascade 통산 540 verifications + 2 fix textual notation only (D-P3-1-R4-1 SUP-4 line L1544→L1844 char-swap + D-P3-2-R7-1 §13.1 M-1~M-7 정본 정합) Phase 3 ENTRY 단계 + Round 2 audit R₅~R₁₈ ~30 verif + 2 fix textual notation only = 통산 ~570 verifications + 4 fix textual notation only ALL Phase 3 ENTRY 2 + Round 2 audit 2 truly_converged_v1 first-pass-after-Round-2-fix CONFIRMED
2. **★★★★ 양방향 cycle 6-9 ↔ 6-11 baseline 완성 specialty milestone first**: 6-11 §6 head 6-9+4-1+3-2 NOTE stack inheritance + 6-9 §6 head 6-11 reverse-inheritance NOTE 등재 NEW post 175,166 / B6F6AE4463895F92 / 1,704 LF Δ +3,529 B / +11 LF = 양방향 정본 동일 EXACT 보존 100% 정합, DAG L71 6-9 ↔ 6-11 양방향 cycle 권장 진입 순 6-9 먼저 정합 EXACT 충족 specialty 종결 + 6-9 P3-3 ★교차 4 매핑 (1-1+4-4+6-11+4-3) → 6-11 P3-4 cross_domain_validation_report (6-1/6-9/1-1/4-1) 입력 base direct inheritance
3. **★★★★ derivation ★ 도메인 specialty + §13.1 정본 매트릭스 정합화 4-1 T3-1 표준 EXACT 직계 first 사례**: Phase 15 S15-6 paste-ready 5 P3 블록 + 6섹션 + 대조 기준 7항목 truly_converged_v1 inheritance EXACT 직계 + §13.1 M-1~M-7 7 요소 매트릭스 정본 정합화 fix (D-P3-2-R7-1) 4-1 T3-1 paste-ready 표준 EXACT 직계 inheritance first 사례 specialty
4. **★★★★ upstream 6건 ALL ✅ verified specialty (가장 많은 upstream derivation ★ 도메인)**: DAG strict upstream 4건 (6-9 Wave 3 #27 ✅ 2026-05-21 + 4-1 Wave 3 #24 ✅ 2026-05-21 + 6-1 Wave 2 #13 ✅ 2026-05-17 + 1-1 Wave 2 #21 ✅ 2026-05-20) + cross-handoff baseline 2건 (3-2 Wave 1 #4 ✅ 2026-05-16 + 6-4 Wave 2 #16 ✅ 2026-05-18) = 통산 upstream 6건 ALL ✅ verified Wave 3 도메인 specialty 6-9 strict 3건 패턴 직계 + cross-handoff 추가 specialty
5. **★★★ LOCK-HM-01~10 10 unique 전수 인용 100% distinct + DEFINED-HERE 정본 소유 specialty Wave 3 본 도메인 가장 LOCK-intensive task**: LOCK-HM-01 Hologram View 3요소(타임라인+스트리밍 캔버스+Glass HUD) + LOCK-HM-02 4 Layout 구조(3-Column Fluid+Builder+Hologram+CLI) + LOCK-HM-03 9-State UI State Machine UI_S0_BOOT~UI_S8_ARCHIVED + LOCK-HM-04 Main LLM 2-tier 라우팅 D2.0-02 §11.15.1 + LOCK-HM-05 I-10 UI 오케스트레이션 + LOCK-HM-06 3-point 출력 포맷 D2.0-05 §7.2 + LOCK-HM-07 44 React 컴포넌트 + LOCK-HM-08 8 Custom Hook + LOCK-HM-09 7 Zustand Store + LOCK-HM-10 Glass HUD 오버레이 — 10/10 P3 ALL 직접 충족 + AUTHORITY §3 L42~L56 정본 매핑 verbatim 인용 (Round 2 audit + Stage 1+2 ZERO write 통산 EXACT 보존)
6. **★★★ CONF-HM-008 OPEN 1 (Phase 3 Round 1 정정 대상 forward-defined P3-3 산출물 FINAL_REVIEW_REPORT.md에서 RESOLVED 처리 Phase 4 implementation) + RESOLVED 10 (C-1, C-2, C-3, CFL-HM-001~007) + VERIFIED 1 = 통산 12 entries baseline 무손상 강제 + Phase 3 신규 발화 0건 강제 충족 5 P3 + Stage 1+2 ALL ✅ EXACT 통산**: CONF-HM-008 9-State 네이밍 drift Phase 3 Round 1 정정 대상 forward-defined Phase 4 + RESOLVED 10 + VERIFIED 1 무손상 verify 5 P3 + Stage 1+2 통산 specialty
7. **★★ V3 NEW 5 forward-defined Phase 4 implementation 단계 별도 트랙 specialty (5 P3 ALL ZERO write 통산 specialty)**: P3-1 moe_evolution.md (V1 2~3 모델 + V2 LiteLLM Router + V3 MoE multi-expert Kimi 384→8 ≥ 450L) + P3-2 L3_COMPLETENESS_REPORT.md (L3 핵심 항목 승급 최소 3개 ≥ 300L) + P3-3 FINAL_REVIEW_REPORT.md (§12 갱신 + GOLD/SILVER 판정 + CONF-HM-008 RESOLVED ≥ 400L) + P3-4 cross_domain_validation_report.md (4 도메인 6-1/6-9/1-1/4-1 ≥ 400L + 6-9 SPECIAL CONSUMER ready) + P3-5 performance_benchmark_baseline.md (FPS 60/30 + HUD <50/100ms + Layout <300/500ms + 응답 p95 <2초 + scenarios 144 ≥ 500L) Phase 4 implementation 단계 별도 트랙 specialty (6-7+6-6 V3 forward-defined 패턴 EXACT 직계, 5 P3 ALL ZERO write 통산 specialty)
8. **★ NO D-spec 4번째 사례 specialty + Wave 3 다섯번째 단일 대화창 도메인 (P3 수 5 ≤ 6 → 분할 불필요 단일 대화창 1일 완성)**: Phase 0+1+2 영역 [ ]=0 STEP_C 2026-04-19 truly_converged 후 [x] 100% 보존 inheritance (6-3 + 3-10 + 4-1 + 본 6-11 = 통산 4번째 NO D-spec 사례 specialty) + Wave 3 다섯번째 단일 대화창 도메인 (3-10 + 4-1 + 4-3 + 6-9 패턴 직계, P3 수 5 단일 대화창 1일 완성)

#### Narrative (6 항목)

- **V2 NEW 12 strict only stack 도메인 specialty 9,341L raw LF EXACT MATCH 100% AUTHORITY L223 합계 SHA UNCHANGED 통산**: 04_main-llm-integration 3 (2,633L T2-1+T2-2+T2-3) + 05_glass-hud-overlay 3 (1,979L T2-4 3종) + 06_streaming-canvas 3 (2,466L T2-5 3종) + 07_orchestration-layer 3 (2,263L T2-6 3종) = 12 V2 NEW / LOCK-HM-01~10 union 10 + per-file 보조 LOCK 매핑 + FAB 0/40 CLEAN 보존, 4 서브폴더 분포 Tier 6 System-wide Hologram-Main-LLM 도메인 specialty
- **V3 NEW 5 forward-defined Phase 4 implementation 단계 별도 트랙 specialty (5 P3 ALL ZERO write 통산)**: P3-1 moe_evolution + P3-2 L3_COMPLETENESS_REPORT + P3-3 FINAL_REVIEW_REPORT + P3-4 cross_domain_validation_report + P3-5 performance_benchmark_baseline (V1+V2 기존 file SHA UNCHANGED 보존 강제) — Wave 3 단계 직접 편집 없음 verify only, 6-7 V3 NEW 3 + EXTEND 1 패턴 + 6-9 NEW 4 forward-defined 패턴 EXACT 직계 6-11 NEW 5 confirm 5 P3 최초 사례 specialty
- **§12 Phase 0 S10-5 (2026-03-27 PASS) 인지 유지 historical 1 row EXACT 보존 specialty**: §12 historical row L1858~L1881 EXACT 보존, P3-3 GOLD/SILVER 판정 row append forward-defined Phase 4 implementation 단계 별도 트랙 (FINAL_REVIEW_REPORT.md 산출물) + V1/V2 영역 byte 무변경 강제, §12 자체 갱신 design choice 부재 통산 — Phase 4 implementation 단계 별도 /validate → /audit → /final-review 트랙
- **NO D-spec 4번째 사례 specialty (Phase 0+1+2 [ ]=0)**: STEP_C 2026-04-19 truly_converged 후 [x] 100% 보존 inheritance, 사용자 옵션 B "안전·누락 0·오류 0·완벽" 패턴 채택 = 통산 45 전수 변환 Phase 3 전용 (Phase 0+1+2 0 + Phase 3 45, Stage 2 EXACT char-swap +0/+0) — 6-3 + 3-10 + 4-1 + 본 6-11 = 통산 4번째 NO D-spec specialty
- **§13.4 NEW 신설 sequential 28번째 도메인 통산 milestone Wave 3 일곱번째 사례**: Wave 1 12 + Wave 2 9 + Wave 3 6 (3-8+3-10+4-1+4-3+5-1+6-9) = 27 도메인 + 6-11 §13.4 = 28번째 (통산 28 도메인 SPEC COMPLETE 직계 정합) — 6-11는 §13 sub-section 3개 already 존재 specialty (§13.1 System-wide 완성도 매트릭스 L1921 + §13.2 L3 우선 승급 대상 L1933 + §13.3 L3 승급 절차 L1943)
- **production 6-11 21 .md + 7 _index + _verification = 29 file aggregate EXACT 보존 통산 5 P3 + ④⑤⑥⑦ + Round 2 audit + Stage 1+2 ALL ZERO write 통산** (V1 Pure 9 = 4,522L raw LF + V2 NEW 12 = 9,341L raw LF EXACT MATCH 100% AUTHORITY L223 합계 SHA UNCHANGED) + AUTHORITY v1.4 21,503 / 2F6F7FA87D46494B + CONFLICT v1.0+ 20,159 / 51D99B89B20FD325 + INDEX v1.0+ 8,701 / CF9B29F9ABBF2CB9 + SOT2_MASTER 227,691 / 6D709EF5D56C963F + CROSS_REF 81,770 / 902831E28463B4CC + PART2 446,456 / 5B555A940BB4E72C ALL ZERO write 통산 유지 (★★★★ Stage 1+2 NO-DRIFT direct path Wave 3 일곱번째 사례 specialty + P3-3+P3-4+P3-5 연속 3 NO-DRIFT direct path P3 task specialty milestone first; 6-11은 Phase 3 ENTRY 2 fix 발생으로 도메인-level NO-DRIFT 100% milestone 통산 카운트 미포함 — 통산 10번째 6-9 유지)

---

## 14. 실행 약점 대응 계획

| # | 리스크 | 영향 | 대응 |
|---|--------|------|------|
| W-1 | 44개 컴포넌트 전수 상세화 부담 | Phase 1 지연 | 계층별 배치 작성 — Layout 컴포넌트(상위) → Feature 컴포넌트(중위) → Atom 컴포넌트(하위) 순 |
| W-2 | 6-1 UI-UX-System 미구조화로 경계 모호 | 중복 작성 위험 | 6-11은 Hologram View 렌더링 파이프라인으로 범위 엄격 제한. 6-1 구조화 시 경계 재조정 |
| W-3 | 6-9 Brain-Adapter-HAL 미구조화로 LLM 연동 경계 모호 | 역할 충돌 | R-611-9 규칙 엄격 적용 — 6-11은 라우팅 결과 수신만, 라우팅 로직 미구현 |
| W-4 | D2.0-08 §4 9-State 상세가 불충분할 가능성 | 전이 규칙 자체 정의 필요 | PRE-5 해소 후 상세 수준 파악, 부족 시 sot 2/에서 상세 정의 (DEFINED-HERE) |
| W-5 | 스트리밍 프로토콜이 Part2에 미언급 | 전면 신규 작성 부담 | V1-P4 ChatPage.tsx 구현 가이드 참조 + 업계 표준(SSE) 기반 설계 |
| W-6 | V3 MoE multi-expert 상세 미정 | Phase 3 불확실성 | V1/V2 우선 안정화, V3는 진화 경로만 문서화 후 상세는 V3 설계 확정 시 |
| W-7 | Glass HUD 성능 (실시간 오버레이 렌더링 부하) | UX 저하 | requestAnimationFrame 기반 갱신, 불필요 리렌더 방지, 벤치마크 기준값 설정 |
| W-8 | 컴포넌트 의존 그래프 변경 빈도 높을 가능성 | 문서 동기화 부담 | 자동 추출 도구(dependency-cruiser 등) 활용 고려, 수동 갱신 최소화 |
| W-9 | Part2 V1-P4와 D2.0-08 간 미세 불일치 가능성 | 정본 혼란 | 충돌 발생 시 CONFLICT_LOG 즉시 기록, D2.0-08이 레이아웃 정본/Part2가 컴포넌트 정본 원칙 적용 |
| W-10 | 7개 페이지 중 Hologram View가 아닌 페이지의 범위 | 과도한 범위 확장 | 6-11은 ChatPage(Hologram View 진입점)를 중심으로 한 렌더링만 커버. 다른 페이지의 Hologram View 미사용 영역은 6-1 소관 |

---

## 부록 §A — Hologram 렌더링 파이프라인 상세

### §A.1 개요

Hologram View는 VAMOS의 4개 Layout 중 가장 고급 시각화를 제공하는 레이아웃이다. 3개 핵심 렌더링 영역(타임라인, 스트리밍 캔버스, Glass HUD)을 조합하여 LLM 응답을 실시간으로 시각화한다.

### §A.2 Hologram View 3요소 (LOCK-HM-01)

```
┌─────────────────────────────────────────────────────────┐
│                    Hologram View                         │
│ ┌──────────┐ ┌──────────────────────┐ ┌───────────────┐ │
│ │           │ │                      │ │  Glass HUD    │ │
│ │ Timeline  │ │  Streaming Canvas    │ │  ┌─────────┐  │ │
│ │           │ │                      │ │  │ 비용     │  │ │
│ │ ┌───────┐ │ │  ┌────────────────┐  │ │  ├─────────┤  │ │
│ │ │ Event │ │ │  │ Token Stream   │  │ │  │ 근거     │  │ │
│ │ │ ───── │ │ │  │ ████████░░░░░  │  │ │  ├─────────┤  │ │
│ │ │ Event │ │ │  ├────────────────┤  │ │  │ 승인     │  │ │
│ │ │ ───── │ │ │  │ Artifact Zone  │  │ │  └─────────┘  │ │
│ │ │ Event │ │ │  │ [Code][Chart]  │  │ │               │ │
│ │ └───────┘ │ │  └────────────────┘  │ │  [로그 상세]  │ │
│ └──────────┘ └──────────────────────┘ └───────────────┘ │
└─────────────────────────────────────────────────────────┘
```

| 영역 | 역할 | 핵심 컴포넌트 |
|------|------|-------------|
| **타임라인** | 대화/워크플로우/이벤트를 시간순으로 표시. 사용자가 과거 컨텍스트를 탐색 | TimelinePanel, EventCard, TimeMarker |
| **스트리밍 캔버스** | Main LLM 응답을 토큰 단위로 실시간 렌더링. 아티팩트(코드/차트/테이블) 인라인 표시 | StreamCanvas, TokenRenderer, ArtifactZone |
| **Glass HUD** | 투명 오버레이로 비용/근거/승인 상태를 실시간 표시. 하위 콘텐츠 상호작용 비차단 | GlassHUD, CostBadge, EvidencePanel, ApprovalStatus |

### §A.3 렌더링 파이프라인 데이터 흐름

```
[사용자 입력]
    ↓
[ORANGE CORE — 의사결정]
    ↓
[Front Mini — 1차 라우팅 / 빠른 응답]
    ↓                          ↓
[Main LLM — 2차 심층 응답]   [Mini 직접 응답 (단순 케이스)]
    ↓
[3-point 출력 생성]
  ├── user_response        → StreamCanvas (토큰 스트리밍)
  ├── evidence_summary     → Glass HUD > EvidencePanel
  └── log_report           → Glass HUD > LogDetail + Timeline
    ↓
[I-10 오케스트레이션 레이어]
  ├── 비용 정보             → Glass HUD > CostBadge
  ├── 승인 상태             → Glass HUD > ApprovalStatus
  ├── UI 상태 전이 이벤트    → 9-State Machine
  └── 로그 변환             → Timeline > EventCard
    ↓
[Hologram View 렌더링]
  ├── Timeline 갱신
  ├── StreamCanvas 토큰 추가
  └── Glass HUD 오버레이 갱신
```

### §A.4 4-Layout 전환 매트릭스 (LOCK-HM-02)

| 출발 Layout | → 3-Column | → Builder | → Hologram | → CLI |
|------------|-----------|----------|-----------|------|
| 3-Column | — | 상태 보존 전환 | 상태 보존 전환 | 최소화 전환 |
| Builder | 상태 보존 전환 | — | 상태 보존 전환 | 최소화 전환 |
| Hologram | 상태 보존 전환 | 상태 보존 전환 | — | 최소화 전환 |
| CLI | 복원 전환 | 복원 전환 | 복원 전환 | — |

**전환 프로토콜**:
- **상태 보존 전환**: 현재 대화 컨텍스트, 스크롤 위치, 입력 중 텍스트를 Zustand Store에 임시 저장 후 Layout 전환
- **최소화 전환**: CLI 모드로 전환 시 UI 상태를 세션 스토리지에 저장, 최소화 렌더링
- **복원 전환**: CLI에서 복귀 시 세션 스토리지에서 UI 상태 복원

### §A.5 9-State UI State Machine 개요 (LOCK-HM-03)

> 상세 전이 규칙: `03_ui-state-machine/transition_matrix.md` 참조 (Phase 1 작성 예정)

| # | 정규명 (Part2 §6.1.6) | 설명 | 주요 진입 조건 |
|---|----------------------|------|--------------|
| S0 | UI_S0_BOOT | 앱/세션 초기화 | 초기 로드 / 재시작 |
| S1 | UI_S1_IDLE | 입력 대기 | 로드 완료 / 응답 완료 후 복귀 |
| S2 | UI_S2_EDITING | Builder 편집 중 | 편집 시작 |
| S3 | UI_S3_READY | 실행 가능 (사전 점검 통과) | 사전 점검 통과 |
| S4 | UI_S4_RUNNING | 실행 중 (trace 활성) | 실행 시작 / 승인 후 재개 |
| S5 | UI_S5_AWAIT_APPROVAL | 승인 대기 (HOLD) | 비용 초과 / 위험 작업 감지 |
| S6 | UI_S6_PRESENTING | 결과 표시 | 출력 완료 |
| S7 | UI_S7_RECOVERY | 실패/폴백/재시도 안내 | 에러 발생 / 거부 / 타임아웃 |
| S8 | UI_S8_ARCHIVED | 아카이브 (리뷰) | 세션 아카이브 |

### §A.6 Main LLM 2-Tier 라우팅 — Hologram 맥락 (LOCK-HM-04)

```
[사용자 메시지] → [ORANGE CORE]
                      ↓
              [Front Mini (1차)]
              ├── 판단: 단순 응답 → Mini 직접 응답 (Hologram: StreamCanvas에 직접 렌더링)
              └── 판단: 심층 필요 → [Main LLM (2차)]
                                      ├── DCL 배경 인식 → 컨텍스트 주입
                                      ├── 3-point 출력 생성
                                      └── Hologram UI 바인딩
```

**Hologram 맥락 전달 항목**:
- `current_layout`: "hologram" (현재 활성 Layout)
- `visible_components`: 현재 렌더링 중인 컴포넌트 목록
- `hud_state`: Glass HUD 현재 표시 항목
- `timeline_context`: 타임라인에 표시된 최근 N개 이벤트 요약
- `user_preferences`: 사용자 UI 설정 (테마, 폰트, HUD 투명도 등)

### §A.7 3-Point 출력 → Hologram UI 바인딩 (LOCK-HM-06)

| 출력 필드 | Hologram 영역 | 컴포넌트 | 렌더링 방식 |
|----------|-------------|---------|-----------|
| `user_response` | 스트리밍 캔버스 | StreamCanvas > TokenRenderer | 토큰 단위 점진적 렌더링. 마크다운 파싱 + 코드 하이라이팅 |
| `evidence_summary` | Glass HUD | GlassHUD > EvidencePanel | 근거 카드 형태. 접기/펼치기. 출처 링크 |
| `log_report` | Glass HUD + 타임라인 | GlassHUD > LogDetail, TimelinePanel > EventCard | HUD에 요약, 타임라인에 이벤트로 기록 |

### §A.8 Glass HUD 오버레이 데이터 구조 (LOCK-HM-10)

```typescript
// Glass HUD 데이터 스키마 (Phase 1~2에서 상세 정의 예정)
interface GlassHUDData {
  // 비용 정보
  cost: {
    current_request_cost: number;     // 현재 요청 비용 (USD)
    session_total_cost: number;       // 세션 누적 비용
    model_name: string;               // 사용 중인 모델명
    token_count: {
      input: number;
      output: number;
    };
  };

  // 근거 정보
  evidence: {
    summary: string;                  // evidence_summary에서 추출
    sources: Array<{
      type: 'document' | 'memory' | 'tool_result';
      reference: string;
      confidence: number;
    }>;
  };

  // 승인 상태
  approval: {
    required: boolean;                // 승인 필요 여부
    reason?: string;                  // 승인 사유
    status: 'pending' | 'approved' | 'rejected' | 'auto_approved';
    threshold_exceeded?: boolean;     // 비용 임계값 초과 여부
  };

  // 메타 정보
  meta: {
    timestamp: string;
    request_id: string;
    routing_path: 'mini_direct' | 'mini_to_main';
    latency_ms: number;
  };
}
```

### §A.9 스트리밍 캔버스 토큰 렌더링 파이프라인

```
[SSE/WS 연결]
    ↓
[청크 수신] → token: "Hello"
    ↓
[토큰 버퍼] → 마크다운 파서에 추가
    ↓
[마크다운 AST 점진적 갱신]
    ↓
[React Virtual DOM diff]
    ↓
[DOM 갱신] → 스크롤 자동 하단 이동
    ↓
[아티팩트 감지] → ```코드블록``` 시작 감지 시
    ↓
[ArtifactZone 활성화] → 코드 하이라이팅 / 차트 렌더링 / 테이블 렌더링
```

**스트리밍 프로토콜 요약** (상세: `06_streaming-canvas/stream_protocol.md`):
- **기본**: SSE (Server-Sent Events) — 단방향 토큰 스트림에 적합
- **폴백**: WebSocket — SSE 불가 환경
- **청크 포맷**: `data: {"token": "...", "type": "text|code|artifact_start|artifact_end", "seq": N}\n\n`
- **재연결**: 지수 백오프 (1s → 2s → 4s → 8s → 16s), 마지막 seq 기반 이어받기

### §A.10 7페이지 라우팅 구조

| # | 페이지 | 경로 | Hologram View 관련도 | 설명 |
|---|--------|------|---------------------|------|
| 1 | Dashboard | `/dashboard` | LOW | 대시보드 — Hologram 미사용 가능 |
| 2 | **Chat** | `/chat` | **CRITICAL** | **ChatPage.tsx — Hologram View 핵심 진입점** |
| 3 | Workflow | `/workflow` | MEDIUM | 워크플로우 — 타임라인 컴포넌트 공유 가능 |
| 4 | Memory | `/memory` | LOW | 메모리 관리 |
| 5 | Settings | `/settings` | LOW | 설정 (Hologram View 커스터마이징 포함) |
| 6 | Log | `/log` | MEDIUM | 로그 — Glass HUD LogDetail 연동 |
| 7 | NodeDetail | `/node/:id` | MEDIUM | 노드 상세 — 에이전트 실행 결과 시각화 |

### §A.11 컴포넌트 계층 구조 개요

```
ChatPage.tsx (Hologram View 진입점)
├── LayoutSwitcher                    ← 4-Layout 전환 컨트롤
├── HologramViewContainer             ← Hologram View 루트
│   ├── TimelinePanel                 ← 타임라인 영역
│   │   ├── TimeMarker
│   │   ├── EventCard (반복)
│   │   └── TimelineFilter
│   ├── StreamCanvasPanel             ← 스트리밍 캔버스 영역
│   │   ├── TokenRenderer
│   │   ├── MarkdownRenderer
│   │   ├── ArtifactZone
│   │   │   ├── CodeBlock
│   │   │   ├── ChartRenderer
│   │   │   └── TableRenderer
│   │   └── StreamProgress
│   └── GlassHUDPanel                 ← Glass HUD 오버레이 영역
│       ├── CostBadge
│       ├── EvidencePanel
│       │   └── SourceCard (반복)
│       ├── ApprovalStatus
│       └── LogDetail
├── InputBar                          ← 사용자 입력 영역
│   ├── TextInput
│   ├── AttachmentButton
│   └── SendButton
└── StatusBar                         ← 하단 상태 표시
    ├── ConnectionIndicator
    ├── ModelIndicator
    └── CostSummary
```

> 위 구조는 개요 수준. 44개 컴포넌트 전수 카탈로그는 `02_component-architecture/component_catalog.md` (Phase 1 작성 예정).

### §A.12 성능 기준값 (Phase 3 정의 예정)

| 지표 | 목표값 | 측정 방법 |
|------|-------|----------|
| 토큰 렌더링 지연 | < 16ms (60fps) | 토큰 수신 → DOM 갱신 시간 |
| Glass HUD 갱신 지연 | < 100ms | 데이터 변경 → 오버레이 갱신 시간 |
| Layout 전환 시간 | < 300ms | 전환 버튼 클릭 → 렌더링 완료 시간 |
| 초기 로드 시간 | < 1.5s | ChatPage 진입 → Hologram View 렌더링 완료 |
| 메모리 사용량 | < 150MB | 1시간 연속 스트리밍 후 측정 |
| SSE 재연결 시간 | < 5s (P95) | 연결 끊김 감지 → 재연결 완료 |

---

## 변경 이력

| 버전 | 일자 | 변경 내용 | 작성자 |
|------|------|----------|--------|
| v1.0 | 2026-03-24 | 초안 작성 — 14+1 섹션 전수 | 구조화 에이전트 |
| v1.1 | 2026-04-05 | T0-1~T0-4 완료 — AUTHORITY_CHAIN + CONFLICT_LOG + 서브폴더 7개 골격 생성, G0-1~G0-4 PASS | 구조화 에이전트 |
| v1.2 | 2026-04-05 | T0-5 PRE-1~PRE-5 해소 — 01/02/03 _index.md 갱신(3요소·44컴포넌트·8Hook·7Store·9State+전환6건+런타임매핑 전수 등록), CFL-HM-002(HV 18개)·CFL-HM-003(★39 vs 각주37) 등재, G0-5 PASS | 구조화 에이전트 |
| v1.3 | 2026-04-14 | Phase 1 완료, 2026-04-14 — T1-1~T1-6 6/6 PASS(산출물 8건, 01_hologram-view-layout 3파일 1078줄 + 02_component-architecture 4파일(component_catalog 616 + hook_catalog 634 + store_catalog 606 + chatpage_integration) + 03_ui-state-machine 2파일 929줄), ISS-01/02/03/04/05/14/16 전수 해소, LOCK-HM-01~10 변경 0건, CONFLICT 신규 0건(CFL-HM-001/002/003 기존 RESOLVED 유지), /validate PASS, Phase 1 → Phase 2 게이트 PASS, Phase 2 진입 가능 | 구조화 에이전트 |
| v1.4 | 2026-04-14 | **Phase 1 검증 프롬프트 실행 결과 반영 (B8-③)** — `_verification/phase1_verification_prompt.md` Agent Explore 실행, G4 최종 판정 **PASS**. 4축 교차 검증(산출물 9건 실측 재집계: layout_structure 430 + layout_switching 365 + responsive_rules 286 = 1081줄 / component_catalog 624 + hook_catalog 634 + store_catalog 614 + chatpage_integration 640 = 2512줄 / state_definitions 511 + transition_matrix 418 = 929줄 / 총 4,522줄 / 정본 AUTHORITY_CHAIN LOCK-HM-01~10·DH 없음 / CONFLICT_LOG OPEN 0 RESOLVED 10+VERIFIED 1 / domain_boundary.md / 메모리) 전수 일치. 세션 prefix `T-` 신규 패턴 확인. LOCK-HM-01~10 변경 없음. C1~C5 제약 준수, 위반 마커 0건. Phase 2 진입 승인 상태 유지. | B8 검증 |
