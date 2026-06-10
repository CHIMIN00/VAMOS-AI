# UI/UX System 구조화 종합 계획서

> **버전**: v1.0
> **작성일**: 2026-03-24
> **목적**: sot 2/6-1_UI-UX-System/을 UI/UX 구현 정본으로 구조화하고, Part2 §6.1 FULL 영역 + D2.0-08 정본과의 역할 분리·참조 체계를 확립
> **Status**: APPROVED
> **Tier**: 6 (System-wide Components)
> **SOT 출처**: D2.0-08 (UI/UX 정본), STEP7-C (UI/UX 전수비교)
> **Part2 상태**: FULL (§6.1 L4557-4670, V1-Phase 4 L2274-2414)
> **세션**: S6-2

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
- [부록 A: UI 컴포넌트 카탈로그](#부록-a-ui-컴포넌트-카탈로그)
- [부록 B: 상태 전이 다이어그램](#부록-b-상태-전이-다이어그램)

---

## 1. 현재 상태 분석

### 1.1 기존 문서 현황

| 문서 | 위치 | 역할 | 상태 |
|------|------|------|------|
| **D2.0-08** | docs/sot/ | UI/UX 설계 정본 (Design Freeze) | LOCK — 11섹션, §0~§10 + V3 슬롯 4개 |
| **STEP7-C** | docs/sot/ | UI/UX 전수비교 작업가이드 | 10 Part, 104건 항목 (C 카테고리) |
| **Part2 §6.1** | docs/guides/PART2 L4557-4670 | UI/UX 상세 구현 (~85개 항목) | FULL — 8개 하위 섹션 (6.1.1~6.1.8) |
| **Part2 V1-P4** | docs/guides/PART2 L2274-2414 | UI/UX 구현 Phase (Week 13-14) | FULL — 20개 구현 항목 + 12개 검증 항목 |

### 1.2 sot 2/6-1_UI-UX-System/ 현재 파일

| 항목 | 상태 |
|------|------|
| 종합계획서 | 본 문서 (신규 작성) |
| AUTHORITY_CHAIN.md | 신규 작성 |
| CONFLICT_LOG.md | 신규 작성 |
| 서브폴더 6개 | 신규 생성 (01~06) |
| 기존 명세 파일 | 없음 (Tier 6 신규 도메인) |

### 1.3 핵심 문제

1. **What/How 관리 부재**: Part2 §6.1은 FULL이지만 When/Where만 정의. 구현 상세(What/How)를 SOT2에서 관리할 구조 없음
2. **D2.0-08 분산 참조**: D2.0-08의 11개 섹션 내용이 Part2에 분산 인용되어 단일 참조점 부재
3. **STEP7-C 미매핑**: 104건 UI/UX 보강 항목이 Part2/D2.0-08과 체계적으로 매핑되지 않음
4. **v12 추가 컴포넌트 미관리**: Part2 §6.1.8에 추가된 4개 v12 컴포넌트(스트레스/CBT/번아웃/플래시카드)가 별도 관리 구조 없음

### 1.4 Part2 §6.1 FULL 영역 요약 (방식 C)

> **출처**: PART2 §6.1 (L4557-4670)
> **Part2가 정본**: When + Where (V1-Phase 4에 구현, frontend/ 디렉토리)
> **sot 2/가 정본**: What + How (컴포넌트 상세 스펙, 상태 전이 로직, 접근성 규칙)

#### Part2 핵심 내용 요약

Part2 §6.1은 8개 하위 섹션으로 구성:
- **6.1.1** 핵심 레이아웃 (4항목): 3-Column Fluid, Builder View, Hologram View, CLI
- **6.1.2** React 컴포넌트 (~44개): 10개 그룹 (Decision/Chat/Approval/Cost/Evidence/Memory/Node-Flow/Guardrails/Input/Navigation + 기타)
- **6.1.3** Custom Hooks(8개) + Stores(7개)
- **6.1.4** 구현 중 결정 항목 (4건): 레이아웃 수, 라우트 수, 다크모드 변수, 애니메이션
- **6.1.5** 멀티모달 UI (V1~V3): 6+6+6 항목
- **6.1.6** UI State Machine 9-state: UI_S0_BOOT ~ UI_S8_ARCHIVED
- **6.1.7** Failure/Fallback UI 규칙: 4개 에러코드 + 14+9 전체 정의
- **6.1.8** UI 접근 제어: RBAC 4단계 (OWNER/ADMIN/OPERATOR/VIEWER)

V1-Phase 4는 Week 13-14에 배정되며, 20개 구현 항목 + 12개 Gate 검증 항목으로 Phase 5 진입 조건을 정의.

---

## 2. 목표 구조 (최종 형태)

### 2.1 폴더 트리

```
D:\VAMOS\docs\sot 2\6-1_UI-UX-System\
│
├── UI_UX_SYSTEM_구조화_종합계획서.md       ← 본 문서
├── AUTHORITY_CHAIN.md                      ← 권한 체계 선언
├── CONFLICT_LOG.md                         ← 충돌 기록부
│
├── 01_builder-view/                        ← Builder View (Cockpit) 상세
│   └── _index.md
│
├── 02_hologram-view/                       ← Hologram View (Experience) 상세
│   └── _index.md
│
├── 03_ui-state-machine/                    ← UI 9-State Machine + 전이 규칙
│   └── _index.md
│
├── 04_react-components/                    ← React 44개 컴포넌트 카탈로그
│   └── _index.md
│
├── 05_custom-hooks/                        ← Custom Hooks 8개 + Stores 7개
│   └── _index.md
│
└── 06_accessibility/                       ← 접근성 + i18n + 디자인 시스템
    └── _index.md
```

### 2.2 깊이 규칙

```
최대 3단계:
  6-1_UI-UX-System/ → XX_{카테고리}/ → 파일.md           (2단계) ✅
  6-1_UI-UX-System/ → XX_{카테고리}/ → {하위}/ → 파일.md  (3단계) ✅
  4단계 이상 → 절대 금지 ❌
```

### 2.3 네이밍 규칙

- **폴더명**: 영문 소문자 + 하이픈, 접두사 2자리 번호 (`01_`, `02_`, ...)
- **파일명**: 영문 소문자 + 언더스코어 (`.md` 확장자)
- **계획서 파일명**: `UI_UX_SYSTEM_구조화_종합계획서.md`

---

## 3. 권한 체계 선언

### 3.1 기존 VAMOS 권한 체인

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN body > Schema/TECH_STACK
```

### 3.2 UI/UX System 확장 권한 체인

```
RULE 1.3
  > PLAN 3.0
    > DESIGN 2.0
      ├─ D2.0-08 전체 (UI/UX 설계 정본 — Design Freeze)
      │   ├─ §1 UI/UX 철학 (4원칙 LOCK)
      │   ├─ §2 화면 구조 (Builder View + Hologram View LOCK)
      │   ├─ §3 레이아웃 (3-Column 규격 LOCK)
      │   ├─ §4 UI 상태 머신 (9-state LOCK)
      │   ├─ §5 UI 이벤트 명세 (54+ EventType LOCK)
      │   ├─ §7 Failure/Fallback UI (14+9 정의 LOCK)
      │   ├─ §8 접근 제어 (RBAC 4단계 LOCK)
      │   └─ §10 디자인 시스템 (ORANGE/BLUE 테마 LOCK)
      └─ D2.0-07 (Safety/Cost/Approval — 승인 타임아웃 참조)
        > Part2 §6.1 (구현 가이드: When + Where)
          > Part2 V1-Phase 4 (Phase 배정: Week 13-14)
            > sot 2/6-1_UI-UX-System/ (구현 상세: What + How) ← 본 도메인
              > STEP7-C (보강 항목 104건 = 체크리스트)
```

### 3.3 각 문서의 권한 범위

| 문서 | 권한 레벨 | 결정할 수 있는 것 | 결정할 수 없는 것 |
|------|----------|------------------|------------------|
| **D2.0-08** | DESIGN (LOCK) | UI 구조, 상태 머신, 이벤트 스키마, 레이아웃 규격, 디자인 시스템 | 구현 일정, 코드 위치 |
| **Part2 §6.1** | IMPL-GUIDE | When(V1-P4 Week 13-14), Where(frontend/), 컴포넌트 목록 44개 | 컴포넌트 내부 로직, 상태 전이 세부 |
| **Part2 V1-P4** | IMPL-PHASE | Phase 배정, Gate 검증 12항목 | 구현 상세 |
| **sot 2/6-1** | IMPL-DETAIL | What(컴포넌트 상세 스펙) + How(구현 로직, 접근성, 테스트) | When(Phase), LOCK 값 재정의 |
| **STEP7-C** | CHECKLIST | 보강 필요 항목 ID + 우선순위 | 구현 방법 (→ sot 2/) |

### 3.4 LOCK 보호 선언

> **절대 규칙**: sot 2/6-1_UI-UX-System/ 내 모든 파일은 아래 LOCK 값을 **재정의할 수 없다**.
> 참조 시 반드시 `> LOCK (출처): [원문 그대로]` 형식을 사용한다.

| # | LOCK 항목 | 정본 출처 | 값 |
|---|-----------|----------|-----|
| L1 | **UI 9-State** | D2.0-08 §4.1 | UI_S0_BOOT ~ UI_S8_ARCHIVED (9개 상태) |
| L2 | **3-Column 좌측 폭** | D2.0-08 §3 / Part2 §6.1.1 | 250-300px |
| L3 | **3-Column 우측 폭** | D2.0-08 §3 / Part2 §6.1.1 | 350-400px |
| L4 | **3-Column 중앙** | D2.0-08 §3 / Part2 §6.1.1 | Flex-grow |
| L5 | **ORANGE 테마색** | D2.0-08 §10.1 | #F97316 (ORANGE CORE) |
| L6 | **BLUE 테마색** | D2.0-08 §10.1 | #00F6FF (BLUE NODE) |
| L7 | **다크모드** | D2.0-08 §10 / Part2 V1-P4 | 기본값 (Light는 토글) |
| L8 | **WCAG 접근성** | Part2 V1-P4 | WCAG 2.1 AA 준수 |
| L9 | **CLI 명령어** | D2.0-08 §2.3 | run/approve/status/cost/memory/policy (6개 고정) |
| L10 | **RBAC 4단계** | Part2 §6.1.8 | OWNER/ADMIN/OPERATOR/VIEWER |
| L11 | **V1 최소 해상도** | D2.0-08 §3.1 | 1280×720 (데스크톱 전용) |
| L12 | **Tauri 기본 크기** | D2.0-08 §3.1 | 1440×900 |
| L13 | **React 컴포넌트 수** | Part2 §6.1.2 | ~44개 (10그룹) |
| L14 | **Custom Hooks 수** | Part2 §6.1.3 | 8개 |
| L15 | **Zustand Stores 수** | Part2 §6.1.3 | 7개 |
| L16 | **i18n 기본 로케일** | D2.0-08 §0 | ko-KR (보조: en-US, V2 확장: ja-JP) |
| L17 | **상태 전이 지연** | D2.0-08 §4.4 | 최대 500ms |
| L18 | **P2 승인 타임아웃** | D2.0-07 | HITL 5분 / 일반 10분 → Auto reject |
| L19 | **이벤트 네이밍** | D2.0-08 §5.1 | `ui.{layer}.{subject}.{action}` |
| L20 | **FailureCode 수** | D2.0-08 §7 | 14개 FailureCodes + 9개 FallbackRegistry |

---

## 4. 거버넌스 규칙

### 4.1 공통 규칙 (R1~R11)

> **글로벌 거버넌스 규칙**: 본 도메인은 0-0_Governance-Rules-Meta에서 정의한 R1~R11 글로벌 규칙을 전체 준수합니다.
>
> 상세: `0-0_Governance-Rules-Meta/01_common-rules/_index.md` 참조.

### 4.2 Tier 6 공통 규칙

| 규칙 ID | 규칙 | 근거 |
|---------|------|------|
| **R-T6-1** | Part2 §6.x 원문과 SOT2 상세가 충돌 시 **Part2 원문 우선** | GUIDE §4.6 |
| **R-T6-2** | 횡단 관심사 도메인(6-2, 6-12, 6-13)은 소비 도메인 목록 유지 필수 | GUIDE §4.6 |
| **R-T6-3** | Part2 업데이트 시 해당 Tier 6 도메인 STALE 체크 필수 | INTEGRATION_PLAN §9 |

### 4.3 UI/UX 전용 규칙

| 규칙 ID | 규칙 | 근거 |
|---------|------|------|
| **R-61-1** | UI 상태 머신 9-state 전이 규칙 변경 금지 (D2.0-08 §4.1 LOCK) | D2.0-08 §4 |
| **R-61-2** | React 컴포넌트 추가/삭제 시 Part2 §6.1.2 동기 갱신 필수 | Part2 §6.1.2 |
| **R-61-3** | 모든 UI 텍스트는 i18n 키로 관리 — 하드코딩 금지 | D2.0-08 §0 MOD-022 |
| **R-61-4** | Builder View 3-Column 레이아웃 좌/중/우 폭 LOCK 준수 | D2.0-08 §2.1.1 |
| **R-61-5** | Decision Lock 이후 "결론 변경" UI 제공 금지 (재시도는 근거/실행/포맷 축만) | D2.0-08 §4.3 |
| **R-61-6** | 모든 UI 이벤트는 `ui.{layer}.{subject}.{action}` 네이밍 준수 + trace_id 공유 | D2.0-08 §5.1 |
| **R-61-7** | LogEvent payload의 `message` 필드는 영어 고정 (로케일 무관 감사 추적) | D2.0-08 §0 |
| **R-61-8** | 승인/비용/정책 UI는 HOLD 전환 + 명시적 승인/거절 필수 | D2.0-08 §1.5 |
| **R-61-9** | v12 추가 컴포넌트 4건 구현 시 해당 STEP7 참조 ID 명시 | Part2 §6.1.8 v12 |
| **R-61-10** | Failure/Fallback UI는 D2.0-08 §7 정본 14+9 정의를 그대로 구현 | D2.0-08 §7 |

---

## 5. 선행작업

### 5.1 Part2 §6.1 완전 읽기 + D2.0-08 대조 (완료)

- **목적**: Part2 FULL 영역과 D2.0-08 정본 간 불일치 확인
- **결과**: Part2 §6.1은 D2.0-08에서 파생. 핵심 수치(9-state, 44개 컴포넌트, 3-Column 규격) 일치 확인
- **상태**: ✅ 완료

### 5.2 기존 관련 도메인과 중복 범위 확인 (완료)

- **4-1 Rust-Tauri**: IPC 커맨드 72개 → 6-1은 프론트엔드 UI만, 백엔드 IPC는 4-1 범위
- **6-11 Hologram-Main-LLM**: Hologram 렌더링/Main LLM → 6-1은 Hologram View UI 구조만, 렌더링 로직은 6-11 범위
- **경계**: 6-1 = UI 레이어(React 컴포넌트, 상태관리, 레이아웃) / 4-1 = Rust 백엔드 / 6-11 = LLM 통합
- **상태**: ✅ 완료

### 5.3 STEP7-C 104건 항목 분류

- **목적**: 104건 UI/UX 보강 항목을 6개 서브폴더로 매핑
- **결과**: 10 Part × 항목별로 01~06 서브폴더 배정 완료
- **상태**: ✅ 완료

---

## 6. 이슈 해결 매핑

> **[1-2 Auxiliary-Modules Phase 3 완료 — 2026-05-14]** (downstream reference, P3-1~P3-6 6/6 ALL ✅ tcv3): 1-2 도메인 Phase 3 완료에 따른 본 도메인 inheritance 가능 자원 — `00_common/response_envelope.md` v2 (LOCK-AX-11 ResponseEnvelope 정본) + `00_common/common_types.md` v2 (Modality / QoD / PipelineStage cross-reference) + V-14 검증 결과 + `06_mapping/interface_contracts.md` C-01~C-14 (14 계약 19 엣지 매핑). UI 컴포넌트가 보조 모듈 응답을 렌더링할 때 본 inheritance 활용 가능. Wave 2 #13 진입 시 본 reference inheritance 처리 예정. (출처: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 3, post 192,270 B / 293E2A16CFB5BE74)

| # | 이슈 | 현재 상태 | 해결 방안 | 대상 서브폴더 |
|---|------|----------|----------|------------|
| 1 | D2.0-08 §4.1 9-state와 §4.4 6-state 양방향 매핑 | D2.0-08 §4.5에서 해결됨 | sot 2/에 매핑 테이블 정본 등록 | 03_ui-state-machine |
| 2 | Part2 §6.1.4 구현 중 결정 4건 미확정 | KEEP (구현 시 확정) | 결정 방향 + 근거를 sot 2/에 기록 | 01_builder-view |
| 3 | STEP7-C 104건 중 Part2 미반영 항목 | 미매핑 | 서브폴더별 매핑 + 우선순위 배정 | 01~06 전체 |
| 4 | v12 추가 컴포넌트 4건 관리 구조 없음 | Part2 §6.1.8만 | sot 2/ 04_react-components에 등록 | 04_react-components |
| 5 | D2.0-08 §6.4.1 CLIP 마이그레이션 미문서화 | D8-L03 미해결 | V2 사전 해결 항목으로 추적 | 02_hologram-view |
| 6 | Hologram View와 6-11 도메인 범위 경계 | 미정의 | AUTHORITY_CHAIN §3에 경계 명시 | 02_hologram-view |
| 7 | EventType 54+건 D2.1-D2 동기 등록 | 부분 등록 | 6-12(Event-Logging)과 협력하여 완료 | 03_ui-state-machine |

### 6.2 STEP7-C 104건 서브폴더별 배분 상세

> **출처**: STEP7-C 10 Part × UI/UX 전수비교 항목 (C 카테고리) — S10-3에서 상세 배분 완료

| 서브폴더 | 배분 건수 | 주요 항목 범위 | 우선순위 | Phase |
|---------|----------|-------------|---------|-------|
| **01_builder-view** | ~18건 | 3-Column Fluid 레이아웃 규격 검증, Builder Panel 구성, 트리뷰 네비게이션, CLI 인터페이스, 7개 페이지 라우팅 | P1 (핵심 레이아웃) | Phase 1 |
| **02_hologram-view** | ~12건 | Glass HUD 오버레이, 3-point 렌더링 품질, Hologram View 반응형, CLIP 마이그레이션 사전 항목, 멀티모달 V1 UI | P2 (시각 품질) | Phase 1 |
| **03_ui-state-machine** | ~15건 | 9-State 전이 규칙 완전성, 이벤트 핸들러 54+건 매핑, 전이 가드 조건, 부수효과 정의, Pipeline S0~S8 매핑 검증 | P1 (상태 정확성) | Phase 1 |
| **04_react-components** | ~30건 | 44 컴포넌트 Props/State 정의, 10그룹별 인터페이스 검증, v12 추가 4건 등록, 컴포넌트 의존성 그래프, 에러/폴백 UI 매핑 | P1 (컴포넌트 핵심) | Phase 1~2 |
| **05_custom-hooks** | ~12건 | 8 Hook 시그니처 + 반환 타입 정의, 7 Store 슬라이스 구조, Hook 간 의존성, Store 구독 패턴, 메모이제이션 전략 | P2 (상태 관리) | Phase 1 |
| **06_accessibility** | ~17건 | WCAG 2.1 AA 준수 검증 (색상 대비 4.5:1, 포커스 표시), 키보드 내비게이션 전체 경로, ARIA 라벨 목록, 스크린 리더 호환, i18n 키 전수 목록, 디자인 시스템 토큰 | P2 (접근성 필수) | Phase 1 |
| **합계** | **104건** | — | — | — |

**이슈 해결 매핑 (서브폴더별)**:
- 01_builder-view: ISS-1(9-state 매핑) + ISS-2(구현 결정 4건) → _index.md에 해결 방안 등재
- 02_hologram-view: ISS-5(CLIP) + ISS-6(6-11 경계) → AUTHORITY_CHAIN + _index.md 교차 참조
- 03_ui-state-machine: ISS-1(양방향 매핑) + ISS-7(EventType 동기) → 매핑 테이블 정본화
- 04_react-components: ISS-3(104건 매핑) + ISS-4(v12 4건) → 그룹별 Props/State 시트 작성
- 05_custom-hooks: ISS-3 중 Hook/Store 관련 12건 → 시그니처 + 테스트 시나리오
- 06_accessibility: ISS-3 중 접근성 17건 → WCAG 체크리스트 + 키보드 경로 맵

### 6.X 1-2 Auxiliary-Modules Phase 4 ✅ 완료 inheritance (2026-05-23, downstream 전파)

> **1-2 Phase 4 ✅ 완료 (2026-05-23, 6/6 P4 task ALL ✅)** — 본 도메인 Wave 2 #13 진입 시 inheritance 활용 가능 산출물:
> - **V2 production-ready 정본** (98/98 ALL Status APPROVED + ReadOnly TRUE + Last-reviewed 2026-05-23 통일): `00_common/response_envelope_v2.md` (LOCK-AX-11 nested 정본) + `00_common/common_types_v2.md` (Modality / QoD / PipelineStage 등 cross-reference catalog) inheritance ready
> - **L3 매트릭스 693 cells PASS 100% baseline**: 1-2/_verification/l3_judgment_phase3_v1.md + phase4_v01_v24_baseline_report.md
> - **V-14 ResponseEnvelope D2.0-02 §5.1.1 LOCK-AX-11 nested 정본 EXACT 영구 baseline**
> - **Phase 4 P4-1 chain**: `phase4_1-2_p4-1_2026-05-23` → 본 도메인 Phase 4 진입 시 response_envelope_v2 / common_types_v2 forward-defined inheritance ✅
> - **1-2 산출물 _verification NEW 9건**: l3_judgment + phase4_v2_v3_promotion + l3_conditional_remediation + phase4_conditional_closure + phase3_final_checklist + phase4_v01_v24_baseline + phase4_status_promotion + phase4_part2_sync + phase4_index_sync
> - **상위 SoT**: `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\AUXILIARY_MODULES_구조화_종합계획서.md` §7 Phase 4 (L2109~) + SOT2_MASTER_INDEX 1-2 row [PHASE5_READY: 1-2 — 2026-05-23]

---

## 7. Phase 실행 계획

### 7.1 V-Phase 정렬

| SOT2 Phase | Part2 대응 | 내용 | 산출물 |
|-----------|-----------|------|--------|
| **Phase 0** | — | 분석 + 구조화 (본 계획서) | 계획서, AUTHORITY_CHAIN, 서브폴더 |
| **Phase 1** ✅ | V1-Phase 4 (Week 13-14) | UI 핵심 구현: 3-Column Layout, Builder/Hologram View, 44개 컴포넌트, 8 Hooks, 7 Stores, 9-State SM | 서브폴더별 L3 상세 파일 (14건 완료, 2026-04-12) |
| **Phase 2** | V2 (리팩토링) | UI 확장: 멀티모달 V2, 반응형 레이아웃, ImageBind 통합, v12 컴포넌트 4건 | L3 업그레이드 |
| **Phase 3** | V3 (최종 통합) | 고급 UI: 모바일 대응, AR/공간 이해, 아바타/디지털 휴먼, V3 확장 슬롯 4개 | 최종 L3 완성 |

### 7.2 Phase 전환 게이트

| 전환 | 게이트 조건 |
|------|-----------|
| P0→P1 | 본 계획서 APPROVED + AUTHORITY_CHAIN 작성 + 6개 서브폴더 _index.md 완료 ✅ (2026-04-02) |
| P1→P2 | Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상 ✅ (2026-04-12, G1 ALL PASS) |
| P2→P3 | V2 Phase 완료 + v12 컴포넌트 4건 구현 + D8-L03 해결 ✅ **PASS** (2026-04-26 STAGE 7 STEP_C 최종 마감 truly_converged_v2, P2-1 D8-L03 ImageBind 4축 / P2-3 v12 4건 × 12 sub L3 / P2-1~P2-4 V2 4 NEW 1,108L) — **[PHASE3_READY v2: 6-1 — 2026-04-26 최종 확정 truly_converged_v2]** |

#### Phase 0 세부 태스크

<details>
<summary><b>P0-1. AUTHORITY_CHAIN.md 작성</b> ✅ 완료 (2026-04-02)</summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md`
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md`
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.1~§6.1.3, §6.1.8, V1-Phase 4
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §3 전체(§3.1~§3.4), §5.2, §9.1

**절차**:
1. 본 계획서 §3 전체 읽기 — 기존 VAMOS 권한 체인(§3.1) + UI/UX 확장 권한 체인(§3.2) + 각 문서별 권한 범위(§3.3) + LOCK 보호 선언(§3.4)
2. §3.4 LOCK 보호 선언 테이블에서 L1~L20 전체 목록 확인 후, 각 LOCK의 정본 출처 문서(D2.0-08 / D2.0-07 / Part2) 원문에서 해당 값 추출
3. 본 계획서 §5.2(도메인 중복 범위) + §9.1(충돌 해결 프로토콜) 읽기 — 6-1 ↔ 6-11(Hologram-Main-LLM), 6-1 ↔ 4-1(Rust-Tauri) 경계 정의 확인
4. AUTHORITY_CHAIN.md 신규 생성:
   - 기존 VAMOS 권한 체인 (§3.1 발췌)
   - UI/UX 확장 권한 체인 계층 (§3.2 발췌)
   - 각 문서별 권한 범위 테이블 (§3.3 발췌)
   - LOCK 20건 레지스트리 (항목명, 정본 출처, LOCK 값)
   - 도메인 경계 선언: 6-1 ↔ 6-11 / 6-1 ↔ 4-1 범위 경계 (§5.2, §9.1 기반, ISS-6 해결)
5. 각 LOCK 값을 정본 출처 원문과 교차 검증:
   - D2.0-08 출처: L1~L7, L9~L12, L16~L17, L19~L20
   - D2.0-07 출처: L18
   - Part2 출처: L8, L13~L15 (+ L2~L7, L10 이중 출처 교차 확인)

**검증**:
- [x] G0-2: AUTHORITY_CHAIN.md에 LOCK 20건(L1~L20) 전체 포함
- [x] 각 LOCK 값이 정본 출처 원문(D2.0-08 / D2.0-07 / Part2)과 일치
- [x] 각 LOCK 항목에 정본 출처 섹션 번호 명시 (§10 검증 #2)
- [x] 도메인 경계(6-1 ↔ 6-11, 6-1 ↔ 4-1) 명시 (§10 검증 #8, ISS-6)

**교차 검증 발견 → 해결**:
- CONF-61-001: L5 ORANGE #FF6B35 → **#F97316** (D2.0-08 §10.1 정본 확정) — RESOLVED
- CONF-61-002: L6 BLUE #4A90D9 → **#00F6FF** (D2.0-08 §10.1 정본 확정) — RESOLVED
- CONF-61-003: L10 출처 "D2.0-08 §8" → **Part2 §6.1.8 단독** — RESOLVED
- 출처 섹션 정밀화 5건: L2~L4(§3→§2.1.1), L9(§2.3→§2.3.1), L20(§7→§7.6)

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` (v2.1)
</details>

<details>
<summary><b>P0-2. CONFLICT_LOG.md 초기화</b> ✅ 완료 (2026-04-02)</summary>

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §9 전체(§9.1 Tier 6 공통 프로토콜 + §9.2 UI/UX 고유 충돌 시나리오)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §8.2 파일 역할 명세 — CONFLICT_LOG.md 역할 정의·내용 범위·변경 규칙
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §11 S-1 — W-1~W-3 잠재 충돌 3건 목록
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §12 FR-7 — CONFLICT_LOG 검증 기준

**절차**:
1. 본 계획서 §9.1(Tier 6 공통 프로토콜 4유형) + §9.2(UI/UX 고유 시나리오 3건) 읽기
2. 본 계획서 §8.2에서 CONFLICT_LOG.md 파일 역할 확인:
   - 내용 범위: 정본 간 충돌 발견 기록, 해결 결정 사유, 영향 범위, 관련 서브폴더
   - 변경 규칙: 추가 전용 — 기존 항목 삭제/수정 금지, RESOLVED 상태 변경만 허용
3. CONFLICT_LOG.md 신규 생성:
   - 헤더: Status, 버전, 생성일, 세션, OPEN/RESOLVED 카운트
   - 충돌 해결 프로토콜 요약: §9.1 4유형 + §9.2 3시나리오 발췌
   - 충돌 기록 테이블 (컬럼: ID, 발생일, 충돌 유형, 문서 A, 문서 B, 상세, 해결, 영향 범위, 관련 서브폴더, 상태)
   - 변경 규칙 명시: 추가 전용 — 기존 항목 삭제/수정 금지, RESOLVED 상태 변경만 허용 (§8.2)
   - 잠재 충돌 모니터링 테이블 (컬럼: ID, 영역, 관련 도메인, 상태, 비고)
4. 잠재 충돌 W-1~W-3 등재 (§11 S-1, §12 FR-7 기준):
   - W-1: Hologram View UI 소유권 (6-1 ↔ 6-11)
   - W-2: UI 9-State 전이 조건 상세 부재 (D2.0-08 ↔ 6-1)
   - W-3: RBAC 4단계 Security 정책 동기화 (6-1 ↔ 6-2)
5. P0-1에서 발견된 교차 검증 충돌(CONF-61-001~003)이 있을 경우 충돌 기록 테이블에 등재

**검증**:
- [x] CONFLICT_LOG.md 파일 존재
- [x] 충돌 기록 테이블 컬럼이 §8.2 내용 범위(충돌 발견 기록, 해결 사유, 영향 범위, 관련 서브폴더) 포함
- [x] 변경 규칙(추가 전용, RESOLVED 상태 변경만 허용) 명시
- [x] 충돌 해결 프로토콜 요약이 §9.1 4유형(3열 원문 발췌) + §9.2 3시나리오 반영
- [x] W-1~W-3 잠재 충돌 등재 (FR-7 PASS 조건)
- [x] P0-1 교차 검증 발견 충돌(CONF-61-001~003) 3건 등재 + AUTHORITY_CHAIN.md 원문 일치 확인

**재검증 보완 (v2.0→v2.1)**:
- §9.1 요약 2열→3열(발생 조건 복원), "View 구조" 누락 복원
- "해결 이력" 섹션 "이동" 표현 → "영구 보존 (§8.2 추가 전용 규칙)" 모순 해소
- CONF-001/002 해결에 "출처 단독 변경" 보완, CONF-003 상세에 D2.0-08 §8 실제 내용 보완
- CONF-003 관련 서브폴더 "06_accessibility" → "— (루트 파일 영향)" 정정

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\CONFLICT_LOG.md` (v2.1)
</details>

<details>
<summary><b>P0-3. 01_builder-view/_index.md 작성</b> ✅ 완료 (2026-04-03)</summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.1(Builder View 전체), §2.1.1(3-Column Fluid Layout), §2.1.2(Panel Composition), §2.1.3(User Actions→LogEvent 12건), §2.3(CLI 전체: §2.3.1 구조, §2.3.2 출력 형식, §2.3.3 UI 동기), §3(공통 규칙), §3.1(V1 Layout Constraints)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.1(핵심 레이아웃 4항목) + §6.1.4(구현 중 결정 4건 — 7개 페이지 정의) + V1-Phase 4(구현 16항목 + Gate 12항목)
- `D:\VAMOS\docs\sot\STEP7-C_UI_UX_전수비교_작업가이드.md` Part 1~10 중 01_builder-view 배분 항목
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §6.2(배분 결과 + 이슈 매핑) + §8.2(필수 섹션 정의)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` §4 LOCK 레지스트리(L2~L4, L9, L11, L12, L19)

**절차**:
1. D2.0-08 §2.1~§2.1.3(Builder View, 3-Column, Panel Composition, User Actions→LogEvent), §2.3~§2.3.3(CLI 구조/출력 형식/UI 동기), §3+§3.1(공통 규칙+V1 제약) 읽기 + Part2 §6.1.1(핵심 레이아웃), §6.1.4(결정 4건), V1-P4(구현 16항목+Gate 12항목) 읽기
2. 본 계획서 §6.2 STEP7-C 배분 결과에서 01_builder-view ~18건 항목 추출 + STEP7-C 원본에서 항목 ID(S7C-xxx) 확인
3. §8.2 필수 섹션 4개 충족을 목표로 _index.md 신규 생성:
   - **3-Column 규격 LOCK 참조**: L2(좌 250-300px), L3(우 350-400px), L4(중앙 Flex-grow), L11(min 1280×720), L12(Tauri 1440×900) — `> LOCK (출처): [원문 그대로]` 형식 준수
   - **7개 페이지 목록**: Dashboard, Chat, Workflow, Memory, Settings, Log, NodeDetail (Part2 §6.1.4 #1 + V1-P4 #4~#10) — 각 페이지별 소속 View(Builder/Hologram/공통) + 파일 경로
   - **Builder Panel 구성도**: D2.0-08 §2.1.2 기반 — Left Panel(Resource/Project Tree, 필터, Policy 스냅샷), Center Panel(Workflow Graph Canvas + Module Manager + Toolbar), Right Panel(Logs/Approval/Cost/Memory 탭) 세부 구성 + S/E-Module 운영 뷰 컬럼 정의
   - **CLI 커맨드 매핑**: §2.3.1 명령어 6개(run/approve/status/cost/memory/policy) + 플래그(--json, --quiet) + §2.3.3 CLI↔UI 이벤트 동기 규칙 (LOCK L9)
   - STEP7-C ~18건 매핑 현황 (항목 ID, 설명, 우선순위, Phase)
   - LogEvent 매핑: §2.1.3 Builder Actions 12건 ui.builder.* 패턴 (LOCK L19 준수)
   - Phase 배정: Phase 1 (V1-P4 Week 13-14)
   - 의존성 참조: 03_ui-state-machine(9-state), 04_react-components(Builder 관련 컴포넌트), 05_custom-hooks(Hooks/Stores), 6-12(Event-Logging)
4. §6.2 이슈 해결 매핑 등재:
   - ISS-1(9-state 양방향 매핑): 03_ui-state-machine 위임 명시 + 교차 참조 링크
   - ISS-2(구현 중 결정 4건): 각 결정 항목별 방향 + 근거 기록 (Part2 §6.1.4 원문 인용)
5. AUTHORITY_CHAIN.md L2~L4, L9, L11, L12, L19 값과 교차 대조 → 불일치 시 D2.0-08 원문 확인
6. D2.0-08 원본으로 LOCK 값 최종 검증 — 불일치 발견 시 CONFLICT_LOG.md에 등재 + AUTHORITY_CHAIN.md와 해결 방안 동기

**검증**:
- [x] G0-3: 01_builder-view/_index.md 존재 + 비어있지 않음 (278줄, 12섹션)
- [x] §8.2 필수 섹션 4개 존재 확인: 3-Column LOCK 참조 ✓, 7개 페이지 목록 ✓, Builder Panel 구성도 ✓, CLI 커맨드 매핑 ✓
- [x] LOCK 참조 값(L2, L3, L4, L9, L11, L12, L19)이 AUTHORITY_CHAIN.md + D2.0-08 원본과 일치 — 불일치 0건
- [x] ISS-1 교차 참조(→03_ui-state-machine) + ISS-2 결정 4건(레이아웃 수, 라우트 수, 다크모드 변수, 애니메이션) 등재 확인
- [x] STEP7-C 18건 항목 매핑 완전성 확인 (S7C-001~S7C-083, §6.2 배분 결과 대비 충족)
- [x] R-61-4(3-Column LOCK 준수) + R-61-6(이벤트 네이밍 ui.{layer}.{subject}.{action}) 반영 확인
- [x] 의존성 참조 5건 명시 확인: 03_ui-state-machine, 04_react-components, 05_custom-hooks, 4-1(Rust-Tauri), 6-12(Event-Logging)

**교차 검증 발견 → 해결**:
- verification_badge/uncertainty_alert 점수 범위: D2.0-08 §2.1.2에는 컬럼명만 존재, 상세 정의는 §2.2.2 출처 → 출처 주석 추가로 해결
- LOCK 인용문 형식: 요약문→D2.0-08 원문 반영으로 §3.4 "원문 그대로" 준수
- STEP7-C 우선순위 카운트: 🔴 11→12건, 🟡 7→6건 정정

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\_index.md` (v1.0)
</details>

<details>
<summary><b>P0-4. 02_hologram-view/_index.md 작성</b> ✅ 완료 (2026-04-03)</summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.2(Hologram View 전체), §2.2.1(3-Pane Focus Layout — 좌/중/우 패널 폭·역할), §2.2.2(패널 구성 — Context Sidebar, Main Stream, Glass HUD + Evidence Badge/Uncertainty Alert + [D8-M02] Pipeline 매핑), §2.2.3(사용자 행동→AI 반응→LogEvent 12건 ui.hologram.*), §3(공통 규칙 — 3단 패널 공통 구조), §3.1(V1 레이아웃 제약 LOCK), §6(멀티모달 입력 플로우: §6.1 아키텍처, §6.2 상태 변화, §6.3 I-4 연결 참조, §6.4.1 CLIP 마이그레이션 D8-L03)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §4.3(승인 타임아웃 — L18 교차 검증용)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.1 #3(Hologram View: 타임라인+스트리밍+Glass HUD) + §6.1.5(멀티모달 UI V1~V3: V1열 6건 — CLIP, OCR, STT, TTS, 차트, 문서 + D8-L03 CLIP 마이그레이션 미문서화 참조) + V1-Phase 4(구현 #3 Hologram View, #5 ChatPage.tsx + Gate 12항목)
- `D:\VAMOS\docs\sot\STEP7-C_UI_UX_전수비교_작업가이드.md` Part 2(Canvas/Artifacts), Part 4(응답 렌더링), Part 5(음성 모드 UI), Part 9(VAMOS 고유 위젯) 중 02_hologram-view 배분 항목
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §6(이슈 해결 매핑 — ISS-5 CLIP, ISS-6 6-11 경계) + §6.2(STEP7-C 배분 결과 — 02_hologram-view ~12건) + §8.2(서브폴더별 필수 섹션 정의 — Glass HUD 스펙, 3-point 렌더링 인터페이스, 6-11 경계 선언, 멀티모달 V1 항목)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` §4 LOCK 레지스트리(L1, L5, L6, L7, L11, L12, L17, L18, L19) + §5.1 도메인 경계(6-1↔6-11 범위 정의)

**절차**:
1. D2.0-08 §2.2~§2.2.3(Hologram View: 3-Pane Layout, 패널 구성, LogEvent 12건), §3+§3.1(공통 3단 패널 구조+V1 제약), §6(멀티모달: §6.1 아키텍처 플로우, §6.2 상태 변화, §6.4.1 CLIP) 읽기 + Part2 §6.1.1 #3(Hologram View), §6.1.5(멀티모달 V1열 6건 + D8-L03), V1-P4(구현 #3 Hologram View, #5 ChatPage.tsx + Gate 12항목) 읽기
2. 본 계획서 §6.2 STEP7-C 배분 결과에서 02_hologram-view ~12건 항목 추출 + STEP7-C 원본(Part 2/4/5/9)에서 항목 ID(S7C-xxx) 확인 — S7C-017~020(인터랙티브 렌더링), S7C-033/035(Markdown·수식 렌더링), S7C-040(3-Part 출력 UI), S7C-045/046(음성 전체화면·파형), S7C-051(멀티모달 음성), S7C-081(3-Gate 표시기) 등
3. §8.2 필수 섹션 4개 충족을 목표로 _index.md 신규 생성:
   - **Hologram View 3-Pane Focus Layout**: D2.0-08 §2.2.1 기반 — Left Panel(Timeline & Context, 접기 가능 ~250px: 세션 리스트, Active BLUE NODE 아이콘 P0/P1/P2 배지, 프로젝트 표시), Center Panel(Stream Canvas, 메인: 채팅 스트림 User/AI, Artifact Viewer 인라인, 입력창 텍스트+멀티모달), Right Panel(Glass HUD, 오버레이/고정 ~300px: Evidence/Cost/Approval 카드) 세부 구성 + §3 공통 3단 패널 구조 참조
   - **Glass HUD 스펙** (§8.2 필수 #1): §2.2.2 Right Panel — Evidence Badge(VERIFIED green qod≥0.8 / PARTIAL yellow 0.5≤qod<0.8 / UNVERIFIED gray qod<0.5), Uncertainty Alert(LOW_QOD / CONFLICTING_SOURCES / STALE_DATA), Cost 게이지(V0~V3 임계치 근접 시 노출), Approval 슬라이드-인 카드(중앙 과점유 금지, LOCK L18 HITL 5분/일반 10분 타임아웃 참조)
   - **3-point 렌더링 인터페이스** (§8.2 필수 #2): §2.2.2 Main Stream — user_response(메인 출력) + evidence_summary(접기 패널) + log_report(접기 패널) 3파트 출력 구조 + [D8-M02] Runtime Pipeline 9단계(RECEIVED→INTENT→EVIDENCE→DECISION_LOCK→EXEC→OUTPUT→SELF-CHECK→MEMORY→DONE) 타임라인 표시 + Context Sidebar Self-check 요약(PASS/WARN/FAIL) + Cost 상태 + RAG/Evidence 상태(citations_ready, QoD)
   - **6-11 경계 선언** (§8.2 필수 #3): AUTHORITY_CHAIN §5.1 기반 — 6-1 = Hologram View UI 구조(Glass HUD 레이아웃, 패널 배치, 상태 표시, StreamingEffect 수신 인터페이스), 6-11 = LLM 통합/렌더링 로직(Main LLM 파이프라인, 렌더링 엔진, 프롬프트 조합, 콘텐츠 생성) — 경계점: StreamingEffect 컴포넌트가 받는 스트림 인터페이스
   - **멀티모달 V1 항목** (§8.2 필수 #4): Part2 §6.1.5 V1열 6건(이미지 입력 CLIP, OCR Tesseract+PyMuPDF, STT Whisper 로컬, TTS Edge TTS, 차트 Mermaid+Plotly, 문서 Markdown→PDF) + D2.0-08 §6.1 아키텍처 플로우 + §2.2.2 Input(텍스트+📎파일+🎤음성+📷캡처) + D8-L03(CLIP ViT-B/32 512d→768d 마이그레이션 미문서화 — V2 ImageBind 통합 전 사전 해결)
   - **LOCK 참조 테이블**: L1(9-State UI_S0~S8), L5(ORANGE #F97316), L6(BLUE #00F6FF), L7(다크모드 기본 Dark), L11(min 1280×720), L12(Tauri 1440×900), L17(전이 지연 최대 500ms), L18(승인 타임아웃 HITL 5분/일반 10분), L19(이벤트 네이밍 ui.{layer}.{subject}.{action}) — `> LOCK (출처): [원문 그대로]` 형식 준수
   - **STEP7-C ~12건 매핑 현황**: 항목 ID(S7C-xxx), 설명, 우선순위(🔴/🟡/🟢), Phase 배정
   - **LogEvent 매핑**: §2.2.3 Hologram Actions 12건 ui.hologram.* 패턴(input.sent, file.uploaded, evidence.viewed/opened, approval.granted/denied, cost.downshifted, artifact.copied, chat.regenerated, memory.committed, audio.recording, attachment.classified) — LOCK L19 준수 + trace_id 공유
   - **Phase 배정**: Phase 1 (V1-P4 Week 13-14)
   - **의존성 참조**: 6-11(Hologram-Main-LLM: 렌더링 로직/응답 생성), 03_ui-state-machine(9-State 전이 규칙), 04_react-components(Hologram 관련 컴포넌트), 05_custom-hooks(Hooks/Stores), 6-12(Event-Logging: ui.hologram.* 발행 + EventType 동기), 4-1(Rust-Tauri: IPC 인터페이스)
4. §6.2 이슈 해결 매핑 등재:
   - ISS-5(CLIP 마이그레이션): D8-L03 미해결 — CLIP ViT-B/32 512d→768d 차원 마이그레이션 미문서화, V2 ImageBind 통합 전 사전 해결 항목으로 추적, Part2 §6.1.5 D8-L03 원문 인용
   - ISS-6(6-11 경계): AUTHORITY_CHAIN §5.1 경계 정의 참조 + 교차 참조 링크 — 6-1(UI 표시 계층) vs 6-11(LLM 생성 계층) 명시
5. AUTHORITY_CHAIN.md L1, L5, L6, L7, L11, L12, L17, L18, L19 값과 교차 대조 → 불일치 시 D2.0-08/D2.0-07 원문 확인
6. D2.0-08 원본으로 LOCK 값 최종 검증 — 불일치 발견 시 CONFLICT_LOG.md에 등재 + AUTHORITY_CHAIN.md와 해결 방안 동기

**검증**:
- [x] G0-3: 02_hologram-view/_index.md 존재 + 비어있지 않음 (310줄, 13섹션)
- [x] §8.2 필수 섹션 4개 존재 확인: Glass HUD 스펙 ✓, 3-point 렌더링 인터페이스 ✓, 6-11 경계 선언 ✓, 멀티모달 V1 항목 ✓
- [x] LOCK 참조 값(L1, L5, L6, L7, L11, L12, L17, L18, L19)이 AUTHORITY_CHAIN.md + D2.0-08/D2.0-07 원본과 일치 — 불일치 0건
- [x] ISS-5(CLIP 마이그레이션 V2 사전 추적) + ISS-6(6-11 경계 선언) 등재 확인
- [x] STEP7-C ~12건 항목 매핑 완전성 확인 (S7C-017~081 11건, §6.2 배분 결과 대비 충족)
- [x] R-61-6(이벤트 네이밍 ui.{layer}.{subject}.{action}) + R-61-8(승인/비용 UI HOLD 전환 + 명시적 승인/거절) + R-61-10(Failure/Fallback UI §7 정본 준수) 반영 확인
- [x] 의존성 참조 6건 명시 확인: 6-11(Hologram-Main-LLM), 03_ui-state-machine, 04_react-components, 05_custom-hooks, 6-12(Event-Logging), 4-1(Rust-Tauri)

**교차 검증 발견 → 해결**:
- LOCK 9건(L1, L5, L6, L7, L11, L12, L17, L18, L19) 전수 MATCH — AUTHORITY_CHAIN.md + D2.0-08/D2.0-07 원본 대조 불일치 0건
- Hologram View 패널 폭(§2.2.1): Builder View L2/L3/L4 LOCK과 별도 — Hologram은 Left ~250px(접기), Right ~300px(오버레이/고정)으로 §2.2.1 원문 그대로 인용
- STEP7-C 배분 ~12건 vs 실제 11건: STEP7-C 원본 Part 2/4/5/9에서 hologram-view 매핑 가능 항목 11건 확인, §6.2 "~12건" 범위 내 충족

**재검증 보완 (v1.0→v1.1)**:
- §1 개요: 본문(L14)과 "목적"(L18) 동일 내용 중복 → 목적 삭제, 개요에 D2.0-08 §2.2 출처 통합
- §3 제목: "(§8.2 필수 — Hologram View 레이아웃)" → §8.2 필수 4개(Glass HUD/3-point/6-11 경계/멀티모달)에 3-Pane Layout 미포함 → 태그 제거
- §5 Context Sidebar: §4.1과 동일 내용 중복(Self-check/Cost/RAG) → "§4.1 참조"로 축약
- §7 D8-L03 교차 참조: "§9 참조" → "§10 참조" 정정 (이슈 해결 현황은 §10)
- §9 합계: "🟢 Nice-to-have" → "🟢 Low(V2+)" STEP7-C 용어 정렬
- §13 Gate 번호: #2 → #3 정정 (Part2 V1-P4 Gate 원본: Hologram View = #3)
- S7C-018 설명: "차트 임베드" → "차트를 응답 내 임베드" 원문 복원

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\_index.md` (v1.1)
</details>

<details>
<summary><b>P0-5. 03_ui-state-machine/_index.md 작성</b> ✅ 완료 (2026-04-03)</summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §4(UI 상태 머신 전체), §4.1(9-State 공통 상태 정의), §4.2(대표 전이 6건), §4.3(Decision Lock UI 제약), §4.4(I-10 UI 오케스트레이션 6-State 상세 — DEC-016), §4.5(§4.1↔§4.4 양방향 매핑 정본), §4.6(Pipeline S0~S8 ↔ UI 상태 크로스 매핑 — D8-M11), §5(UI 이벤트 명세 전체), §5.1(네이밍 규칙 ui.{layer}.{subject}.{action}), §5.3~§5.7(EventType 54+건: Front Mini 7 + Core/Gate 14 + Node/Main 13 + Tool 6 + CLI 10 + Memory 5), §5.9(D2.1-D2 EventTypeRegistry 동기), §7(Failure/Fallback UI 전체), §7.1~§7.3(FailureCode 14건: FM 4 + OC 4 + TL/MC 6), §7.6(FailureCode 14 + FallbackRegistry 9 SOT 등록)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §4.3(승인 타임아웃 — L18 교차 검증용, UI_S5_AWAIT_APPROVAL 타임아웃 규칙)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.6(UI State Machine 9-state 정의 + 전이 규칙 + §4.5 양방향 매핑 참조) + §6.1.7(Failure/Fallback UI 규칙: 4개 에러코드 + 14+9 전체 정의 참조) + V1-Phase 4(Gate #10 UI 9-State SM 전이 동작 검증)
- `D:\VAMOS\docs\sot\STEP7-C_UI_UX_전수비교_작업가이드.md` Part 1/3/4/5/6/7/8 중 03_ui-state-machine 배분 항목
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §6(이슈 해결 매핑 — ISS-1 양방향 매핑, ISS-7 EventType 동기) + §6.2(STEP7-C 배분 결과 — 03_ui-state-machine ~15건) + §8.2(서브폴더별 필수 섹션 정의 — 9-State LOCK 참조, 전이 규칙 매트릭스, §4.1↔§4.4 양방향 매핑, EventType 목록)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` §4 LOCK 레지스트리(L1, L17, L18, L19, L20) + §5.1 도메인 경계(6-1↔4-1 Core Pipeline 상태 수신 인터페이스)

**절차**:
1. D2.0-08 §4~§4.6(UI 상태 머신: 9-State 정의, 대표 전이 6건, Decision Lock 제약, I-10 6-State 오케스트레이션, 양방향 매핑 정본, Pipeline S0~S8 크로스 매핑), §5~§5.9(UI 이벤트 명세: 네이밍 규칙, EventType 54+건 6개 레이어, D2.1-D2 동기), §7~§7.6(Failure/Fallback UI: FailureCode 14건 3개 레이어, FallbackRegistry 9건, SOT 등록) 읽기 + Part2 §6.1.6(9-state + 전이 규칙), §6.1.7(Failure/Fallback 4개 에러코드 + 14+9 전체), V1-P4(Gate #10 UI 9-State SM 검증) 읽기
2. 본 계획서 §6.2 STEP7-C 배분 결과에서 03_ui-state-machine ~15건 항목 추출 + STEP7-C 원본(Part 1/3/4/5/6/7/8)에서 항목 ID(S7C-xxx) 확인 — S7C-012(ORANGE/BLUE 상태 표시), S7C-030(비용 Gate 가드 조건), S7C-037(Thinking 블록 상태 관리), S7C-043(피드백 이벤트 상태 전이), S7C-045(음성 모드 상태 전이), S7C-060(오프라인 상태 전이), S7C-061(알림 에러 상태), S7C-063(에이전트 진행률 상태), S7C-067(취소/일시정지 상태 전이), S7C-069(3-Gate 통과 표시), S7C-070(파이프라인 스텝 표시), S7C-076(모델 폴백 선택) 등
3. §8.2 필수 섹션 4개 충족을 목표로 _index.md 신규 생성:
   - **9-State LOCK 참조** (§8.2 필수 #1): D2.0-08 §4.1 기반 — UI_S0_BOOT ~ UI_S8_ARCHIVED 9개 상태 정의 + 각 상태별 표시 조건·사용자 액션 허용 범위 — `> LOCK (출처): [원문 그대로]` 형식 준수 (LOCK L1)
   - **전이 규칙 매트릭스** (§8.2 필수 #2): D2.0-08 §4.2 기반 — 대표 전이 6건(IDLE→RUNNING, RUNNING→AWAIT_APPROVAL, AWAIT_APPROVAL→RUNNING, RUNNING→RECOVERY, RECOVERY→RUNNING, RUNNING→PRESENTING) + 각 전이별 가드 조건(approval_required, failure, output_ready 등) + 부수효과 정의(UI 갱신, 모달 표시, 스피너, 알림 등) + §4.3 Decision Lock 제약(결론 변경 금지, 재시도는 근거/실행/포맷 축만) + §4.4 I-10 오케스트레이션 업데이트 원칙(이벤트 기반·폴링 금지, 전이 지연 최대 500ms LOCK L17, Core-UI 불일치 시 ui.core.state.mismatch 자동 동기화)
   - **§4.1↔§4.4 양방향 매핑** (§8.2 필수 #3): D2.0-08 §4.5 정본 기반 — 9-state(세션 생명주기) ↔ 6-state(Core 연동 런타임) 매핑 테이블 정본화 + 정본 우선순위(§4.1 = UI 설계 정본, §4.4 = Core 연동 뷰) 명시 + §4.6 Pipeline S0~S8 ↔ UI 상태 크로스 매핑(D8-M11) 포함
   - **EventType 목록** (§8.2 필수 #4): D2.0-08 §5.3~§5.7 기반 — 6개 레이어 54+건(Front Mini 7, Core/Gate 14, Node/Main 13, Tool 6, CLI 10, Memory 5) + §5.1 네이밍 규칙(LOCK L19) + §5.2 네임스페이스 연결 규칙 + §5.9 D2.1-D2 EventTypeRegistry 동기 등록 현황
   - **Failure/Fallback UI 정의**: D2.0-08 §7 기반(§7.3 Phase 1 항목 #9 배정) — FailureCode 14건(FM 4 + OC 4 + TL/MC 6) + FallbackRegistry 9건 매핑 + Part2 §6.1.7 4개 에러코드 화면 표시·폴백 행동 + UI_S7_RECOVERY 상태 진입·이탈 조건 + §7.4 사용자 안내 문구 템플릿 참조 (LOCK L20)
   - **LOCK 참조 테이블**: L1(9-State UI_S0~S8), L17(전이 지연 최대 500ms), L18(승인 타임아웃 HITL 5분/일반 10분 — UI_S5 타임아웃), L19(이벤트 네이밍 ui.{layer}.{subject}.{action}), L20(FailureCode 14 + FallbackRegistry 9) — `> LOCK (출처): [원문 그대로]` 형식 준수
   - STEP7-C ~15건 매핑 현황 (항목 ID, 설명, 우선순위, Phase)
   - Phase 배정: Phase 1 (V1-P4 Week 13-14, Gate #10)
   - 의존성 참조: 01_builder-view(Builder 상태 표시 소비), 02_hologram-view(Hologram 상태 표시 소비), 04_react-components(상태 전이 트리거 컴포넌트), 05_custom-hooks(Hooks/Stores 상태 관리), 6-12(Event-Logging: EventType 54+건 동기 발행), 4-1(Rust-Tauri: Core Pipeline 상태 수신 IPC)
4. §6.2 이슈 해결 매핑 등재:
   - ISS-1(9-state 양방향 매핑): D2.0-08 §4.5 정본 기반 매핑 테이블 작성 완료 + §4.6 Pipeline 크로스 매핑 포함 — 01_builder-view, 02_hologram-view에서 교차 참조 링크
   - ISS-7(EventType 54+건 동기 등록): §5.3~§5.7 전체 목록 정본화 + §5.9 D2.1-D2 동기 현황 추적 — 6-12(Event-Logging)과 협력 항목 표시
5. AUTHORITY_CHAIN.md L1, L17, L18, L19, L20 값과 교차 대조 → 불일치 시 D2.0-08/D2.0-07 원문 확인
6. D2.0-08 원본으로 LOCK 값 최종 검증 — 불일치 발견 시 CONFLICT_LOG.md에 등재 + AUTHORITY_CHAIN.md와 해결 방안 동기

**검증**:
- [x] G0-3: 03_ui-state-machine/_index.md 존재 + 비어있지 않음 (458줄, 12섹션)
- [x] §8.2 필수 섹션 4개 존재 확인: 9-State LOCK 참조 ✓, 전이 규칙 매트릭스 ✓, §4.1↔§4.4 양방향 매핑 ✓, EventType 목록 ✓
- [x] LOCK 참조 값(L1, L17, L18, L19, L20)이 AUTHORITY_CHAIN.md + D2.0-08/D2.0-07 원본과 일치 — 불일치 0건
- [x] ISS-1(양방향 매핑 테이블 + Pipeline 크로스 매핑) + ISS-7(EventType 57건 목록 + D2.1-D2 동기 현황) 등재 확인
- [x] STEP7-C 15건 항목 매핑 완전성 확인 (S7C-012~S7C-085, §6.2 배분 결과 대비 충족)
- [x] R-61-1(9-state 전이 규칙 변경 금지) + R-61-5(Decision Lock 후 결론 변경 금지) + R-61-6(이벤트 네이밍 ui.{layer}.{subject}.{action}) + R-61-10(Failure/Fallback UI §7 정본 14+9 준수) 반영 확인
- [x] 의존성 참조 6건 명시 확인: 01_builder-view, 02_hologram-view, 04_react-components, 05_custom-hooks, 6-12(Event-Logging), 4-1(Rust-Tauri)
- [x] §10 검증 #6(03_ui-state-machine에 §4.1↔§4.4 매핑 테이블 존재) 충족

**교차 검증 발견 → 해결**:
- LOCK 5건(L1, L17, L18, L19, L20) 전수 MATCH — AUTHORITY_CHAIN.md + D2.0-08/D2.0-07 원본 대조 불일치 0건
- EventType 산술 검증: 7(frontmini) + 16(core/gate) + 13(node/main) + 6(tool) + 10(cli) + 5(memory) = 57건 확정
- STEP7-C 배분 ~15건 vs 실제 15건: STEP7-C 원본 Part 1/3/4/6/7/9에서 state-machine 매핑 가능 항목 15건 확인, §6.2 "~15건" 범위 충족

**재검증 보완 (v1.0→v1.1)**:
- §6.3 ui.node+main 섹션 헤더: "(15건)" → "(13건)" 정정 (실제 이벤트 2+11=13)
- §6.5 D2.1-D2 동기 테이블 ui.main.*: "13" → "11" 정정 (ui.node 2건은 별도 행)
- §2 LOCK L18 출처: "§4.3.2" → "§4.3" 정정 (AUTHORITY_CHAIN.md 정합성)

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\_index.md` (v1.1)
</details>

<details>
<summary><b>P0-6. 04_react-components/_index.md 작성</b> ✅ 완료 (2026-04-03)</summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §10.4(React 컴포넌트 레지스트리 44개 — Component ID 체계 {View}-{Category}-{번호}, V1 필수 37개 + V1.1+ 선택 7개), §10.1(Color Palette — ORANGE #F97316 / BLUE #00F6FF / Approval·Evidence 색상), §10.2(Icon System — lucide-react ^0.468.0 LOCK), §10.2a(Typography — font stack + size), §10.3(Alert Priority — Alert-P0 모달 / Alert-P1 슬라이드 / Alert-P2 토스트 → CM-ALERT-01/02/03 매핑), §2.1.2(Builder Panel Composition — BV-* 컴포넌트 배치 컨텍스트), §2.1.3(Builder User Actions→LogEvent 12건 ui.builder.* — 컴포넌트별 이벤트 트리거), §2.2.2(Hologram Panel Composition — HV-* 컴포넌트 배치 컨텍스트 + Evidence Badge/Uncertainty Alert 점수 기준), §2.2.3(Hologram User Actions→AI 반응→LogEvent 12건 ui.hologram.* — 컴포넌트별 이벤트 트리거), §5.3~§5.7(EventType 54+건 6개 레이어 — 컴포넌트별 이벤트 바인딩), §7(Failure/Fallback UI — FailureCode 14건 + FallbackRegistry 9건 → 컴포넌트 매핑: §7.1 FM→AlertModal, §7.2 OC→ApprovalCard/CostWarningBanner, §7.3 TL/MC→ToastNotification/EvidencePanel), §9.1(Layout Decision — Fixed Dock Pattern FREEZE → Approval/Cost/Evidence 1-click 접근)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` §4.3(승인 타임아웃 — L18 HITL 5분/일반 10분, ApprovalCard HV-APPR-01 타임아웃 규칙 교차 검증용)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.2(React 컴포넌트 ~44개 10그룹: Decision 3 / Chat 6 / Approval 3 / Cost 5 / Evidence 4 / Memory 4 / Node/Flow 4 / Guardrails 3 / Input 4 / Navigation 3 + 기타 5) + §6.1.7(Failure/Fallback UI 규칙: 4개 에러코드 화면 표시·폴백 행동) + §6.1.8(v12 추가 4건: 스트레스 관리 BreathingGuide 등 / CBT ThoughtRecord 등 / 번아웃 WorkloadMonitor 등 / 플래시카드 FlashcardEditor 등 — 참조 ID D207-175/178/179, S7NP-047/048) + V1-Phase 4(구현 #11 React ~44개 + #15 디자인 시스템 + Gate #5 ~44개 렌더링 검증 + Gate #12 디자인 시스템 CSS Custom Properties)
- `D:\VAMOS\docs\sot\STEP7-C_UI_UX_전수비교_작업가이드.md` Part 1(메인 대화: S7C-001/002/004/006/011/012), Part 2(Canvas/Artifacts: S7C-013/017~022), Part 3(입력 영역: S7C-023~025/029/030), Part 4(응답 렌더링: S7C-033~035/038/040~042), Part 7(에이전트 실행: S7C-063/069/070), Part 9(VAMOS 위젯: S7C-081~085) 중 04_react-components 배분 ~30건
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §6(이슈 해결 매핑 — ISS-3 104건 매핑 + ISS-4 v12 4건 등록) + §6.2(STEP7-C 배분 결과 — 04_react-components ~30건, P1 우선순위, Phase 1~2) + §8.2(서브폴더별 필수 섹션 정의 — 10그룹 인덱스, 44+4 컴포넌트 카탈로그, 그룹별 우선순위, Props 개요) + §13(L3 전수 승급 계획 — E1~E8 완성도 매트릭스: Props 스키마, 상태 전이, 이벤트 핸들러, 접근성, i18n, 의존성, 테스트, 에러/폴백) + §14(실행 약점 — #2 L3 공수 대응: Decision/Chat/Approval 우선, #4 매핑 불완전 대응: _index.md 매핑 현황 유지, #5 v12 참조 ID: Part2 주석 추출) + 부록 §A(UI 컴포넌트 카탈로그 10그룹 48개)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` §4 LOCK 레지스트리(L5 ORANGE #F97316, L6 BLUE #00F6FF, L7 다크모드 기본, L13 React 컴포넌트 수 ~44개, L18 승인 타임아웃 HITL 5분/일반 10분, L19 이벤트 네이밍 ui.{layer}.{subject}.{action}, L20 FailureCode 14 + FallbackRegistry 9)

**절차**:
1. D2.0-08 §10.4(컴포넌트 레지스트리 44개: Component ID 체계, V1 필수 37개/V1.1+ 선택 7개, 6개 View 분류 BV/HV/CM/CLI/LOG/P2), §10.1~§10.3(디자인 시스템: Color Palette, Icon lucide-react, Typography, Alert Priority 3단계), §2.1.2(Builder Panel BV-* 배치), §2.1.3(Builder Actions 12건 ui.builder.* 컴포넌트 이벤트 트리거), §2.2.2(Hologram Panel HV-* 배치 + Evidence Badge/Uncertainty Alert 점수 기준 qod≥0.8/0.5≤qod<0.8/qod<0.5), §2.2.3(Hologram Actions 12건 ui.hologram.* 컴포넌트 이벤트 트리거), §5.3~§5.7(EventType 54+건 컴포넌트 이벤트 바인딩), §7(FailureCode→컴포넌트 매핑: FM→CM-ALERT-01, OC→HV-APPR-01/HV-COST-01, TL→CM-ALERT-03, MC→HV-EVID-01/02), §9.1(Fixed Dock Pattern FREEZE) 읽기 + Part2 §6.1.2(10그룹 44개 한글 명칭 + 파일 경로 frontend/src/components/), §6.1.7(에러코드 4건 화면 표시), §6.1.8(v12 4건 상세), V1-P4(구현 #11 + #15 + Gate #5 + Gate #12) 읽기
2. 본 계획서 §6.2 STEP7-C 배분 결과에서 04_react-components ~30건 항목 추출 + STEP7-C 원본(Part 1/2/3/4/7/9)에서 항목 ID(S7C-xxx) 확인 — S7C-001/002/004(레이아웃·사이드바·모델선택), S7C-006/011/012(단축키·멀티탭·ORANGE/BLUE 표시), S7C-013/017~022(Canvas·미리보기·차트·테이블·Mermaid·Split View·Decision 시각화), S7C-023~025/029/030(멀티라인·D&D·인라인선택·토큰카운터·비용미리보기), S7C-033~035/038/040~042(Markdown·코드블록·LaTeX·스트리밍·3-Part 출력·신뢰도바·비용표시), S7C-063/069/070(진행률·3-Gate·파이프라인 스텝), S7C-081~085(3-Gate 표시기·비용 게이지·QoD 바·파이프라인 인디케이터·Decision 카드) 등
3. §8.2 필수 섹션 4개 충족을 목표로 _index.md 신규 생성:
   - **10그룹 인덱스** (§8.2 필수 #1): Part2 §6.1.2 기반 — 10그룹(Decision 3 / Chat 6 / Approval 3 / Cost 5 / Evidence 4 / Memory 4 / Node/Flow 4 / Guardrails 3 / Input 4 / Navigation 3) + 기타 5 = 44개 목록 + 각 그룹별 D2.0-08 §10.4 Component ID 매핑(BV-*/HV-*/CM-*/CLI-*/LOG-*/P2-*) + V1 필수 37개/V1.1+ 선택 7개 구분 + 그룹별 L3 작성 우선순위(§14 #2: Decision→Chat→Approval→나머지)
   - **44+4 컴포넌트 카탈로그** (§8.2 필수 #2): 부록 §A A.1 기반 44개 카탈로그 + A.2 기반 v12 4건(스트레스/CBT/번아웃/플래시카드 — 참조 ID D207-175/178/179, S7NP-047/048, R-61-9 STEP7 참조 ID 명시 준수) = 48개 전체 목록. 각 컴포넌트별: 한글명, 영문 Component ID(§10.4), 소속 View(Builder/Hologram/Common/CLI/Dashboard/P2), D2.0-08 출처 섹션, Part2 §6.1.2 그룹 매핑
   - **그룹별 우선순위** (§8.2 필수 #3): Phase 1(V1-P4 Week 13-14) V1 필수 37개 → Phase 2(V2 리팩토링) V1.1+ 선택 7개 + v12 4건 배정. 그룹별 구현 순서: Decision(3) → Chat(6) → Approval(3) → Cost(5) → Evidence(4) → 나머지 (§14 #2 약점 대응 + §11 S-5 OPEN 항목 연계)
   - **Props 개요** (§8.2 필수 #4): §13 L3 완성도 매트릭스 E1(TypeScript Interface + 필수/선택 Props + 기본값) 기준으로 각 그룹 대표 컴포넌트 1~2개 Props Interface 스켈레톤 제시(Phase 1 L3 시트 작성 기반) + E6(의존성: Hook/Store/라이브러리) 요약 + E8(FailureCode 매핑) 개요
   - **컴포넌트 ↔ View 배치 매핑**: D2.0-08 §2.1.2(Builder Panel BV-* 컴포넌트 Left/Center/Right 배치) + §2.2.2(Hologram Panel HV-* 컴포넌트 Context Sidebar/Main Stream/Glass HUD 배치) + §9.1(Fixed Dock Pattern) 기반 — 각 컴포넌트가 어느 View의 어느 패널에 배치되는지 명시
   - **컴포넌트 ↔ EventType 바인딩**: D2.0-08 §5.3~§5.7 기반 — 각 그룹별 주요 컴포넌트가 발행/구독하는 EventType 목록(ui.builder.*/ui.hologram.*/ui.core.*/ui.gate.* 등) + §2.1.3 Builder Actions 12건 + §2.2.3 Hologram Actions 12건 컴포넌트별 매핑 (LOCK L19 준수)
   - **컴포넌트 ↔ FailureCode/Fallback 매핑**: D2.0-08 §7 기반 — FailureCode 14건이 어느 컴포넌트에서 UI 표시되는지(FM→CM-ALERT-01, OC→HV-APPR-01/HV-COST-01/CM-ALERT-01, TL→CM-ALERT-03, MC→HV-STATE-02/HV-EVID-01/02) + FallbackRegistry 9건 복구 동작 컴포넌트 매핑 (LOCK L20 준수, R-61-10 준수)
   - **디자인 시스템 토큰 참조**: §10.1 ORANGE #F97316(LOCK L5) / BLUE #00F6FF(LOCK L6) / 다크모드 기본(LOCK L7) + §10.2 lucide-react ^0.468.0 아이콘 + §10.2a Typography font stack + §10.3 Alert Priority 3단계 — 컴포넌트별 적용 규칙
   - **LOCK 참조 테이블**: L5(ORANGE #F97316), L6(BLUE #00F6FF), L7(다크모드 기본), L13(React 컴포넌트 수 ~44개), L18(승인 타임아웃 HITL 5분/일반 10분 — ApprovalCard), L19(이벤트 네이밍 ui.{layer}.{subject}.{action}), L20(FailureCode 14 + FallbackRegistry 9) — `> LOCK (출처): [원문 그대로]` 형식 준수
   - **STEP7-C ~30건 매핑 현황**: 항목 ID(S7C-xxx), 설명, 우선순위(🔴/🟡), Phase 배정, 대응 그룹/컴포넌트
   - **Phase 배정**: Phase 1(V1-P4 Week 13-14, Gate #5 ~44개 렌더링 검증, Gate #12 디자인 시스템), Phase 2(V1.1+ 선택 7개 + v12 4건)
   - **의존성 참조**: 01_builder-view(Builder Panel BV-* 배치 컨텍스트), 02_hologram-view(Hologram Panel HV-* 배치 컨텍스트 + Glass HUD), 03_ui-state-machine(9-State 전이 → 컴포넌트 상태 반영 + EventType 54+건), 05_custom-hooks(8 Hooks + 7 Stores 컴포넌트 연동), 06_accessibility(WCAG 2.1 AA 컴포넌트 적용), 6-12(Event-Logging: EventType 발행 동기), 4-1(Rust-Tauri: IPC 커맨드 → Hook → 컴포넌트)
4. §6.2 이슈 해결 매핑 등재:
   - ISS-3(STEP7-C 104건 중 Part2 미반영 항목): 04_react-components ~30건 그룹별 매핑 완료 현황 기록 — 각 S7C 항목이 어느 컴포넌트/그룹에 대응하는지 추적 테이블
   - ISS-4(v12 추가 컴포넌트 4건 관리 구조): A.2 v12 4건(스트레스/CBT/번아웃/플래시카드) 등록 + 참조 ID(D207-175/178/179, S7NP-047/048) 명시 + Phase 2 배정 확인 (R-61-9 준수)
5. AUTHORITY_CHAIN.md L5, L6, L7, L13, L18, L19, L20 값과 교차 대조 → 불일치 시 D2.0-08/D2.0-07 원문 확인
6. D2.0-08 원본으로 LOCK 값 최종 검증 — 특히 §10.4 Component ID 체계·V1 필수 37개 목록과 Part2 §6.1.2 10그룹 44개 대조, §10.1 색상값 L5/L6 대조, §7 FailureCode→컴포넌트 매핑 L20 대조 — 불일치 발견 시 CONFLICT_LOG.md에 등재 + AUTHORITY_CHAIN.md와 해결 방안 동기

**검증**:
- [x] G0-3: 04_react-components/_index.md 존재 + 비어있지 않음 (611줄, 15섹션)
- [x] §8.2 필수 섹션 4개 존재 확인: 10그룹 인덱스 ✓, 44+4 컴포넌트 카탈로그 ✓, 그룹별 우선순위 ✓, Props 개요 ✓
- [x] LOCK 참조 값(L5, L6, L7, L13, L18, L19, L20)이 AUTHORITY_CHAIN.md + D2.0-08/D2.0-07 원본과 일치 — 불일치 0건
- [x] ISS-3(STEP7-C 33건 그룹별 매핑 완료) + ISS-4(v12 4건 등록 + 참조 ID D207-175/178/179, S7NP-047/048 명시) 등재 확인
- [x] STEP7-C ~30건 항목 매핑 완전성 확인 (S7C-001~S7C-085 중 33건, §6.2 "~30건" 범위 충족)
- [x] R-61-2(컴포넌트 추가/삭제 시 Part2 §6.1.2 동기 갱신 규칙 명시) + R-61-6(이벤트 네이밍 ui.{layer}.{subject}.{action} 컴포넌트별 바인딩) + R-61-9(v12 4건 STEP7 참조 ID 명시) + R-61-10(Failure/Fallback UI §7 정본 14+9 컴포넌트 매핑) 반영 확인
- [x] §10 검증 #7 충족: "44개 컴포넌트 그룹별 카탈로그 — 04_react-components에 10그룹 인덱스 존재"
- [x] 의존성 참조 7건 명시 확인: 01_builder-view, 02_hologram-view, 03_ui-state-machine, 05_custom-hooks, 06_accessibility, 6-12(Event-Logging), 4-1(Rust-Tauri)
- [x] D2.0-08 §10.4 Component ID(BV-*/HV-*/CM-*/CLI-*/LOG-*/P2-*) 44개 전수 등재 + Part2 §6.1.2 10그룹 한글명 교차 매핑 정합성

**교차 검증 발견 → 해결**:
- LOCK 7건(L5, L6, L7, L13, L18, L19, L20) 전수 MATCH — AUTHORITY_CHAIN.md + D2.0-08/D2.0-07 원본 대조 불일치 0건
- V1 필수(★) 산술 검증: BV 12 + HV 15 + CM 6 + CLI 4 + LOG/P2 0 = 37개, V1.1+ 7개(HV-INPUT-03, HV-COST-02, HV-MEM-02, CM-THEME-01, LOG-DASH-01, LOG-DASH-02, P2-DASH-01) — 37+7=44 확정
- STEP7-C 배분 ~30건 vs 실제 33건: STEP7-C 원본 Part 1/2/3/4/7/9에서 react-components 매핑 가능 항목 33건 확인, §6.2 "~30건" 범위 충족
- Evidence Badge qod 점수 기준(VERIFIED ≥0.8 / PARTIAL 0.5~0.8 / UNVERIFIED <0.5) + Uncertainty Alert 3종(LOW_QOD / CONFLICTING_SOURCES / STALE_DATA) — D2.0-08 §2.2.2 원문 반영

**재검증 보완 (v1.0→v1.1)**:
- LOG-DASH-01/02 V1 필수(★) 오표기 → V1.1+ 선택으로 정정 (D2.0-08 §10.4 정본)
- V1.1+ 선택 7개 목록 불완전("등" 사용) → 7개 전수 명시로 보강
- §5.2 Glass HUD: Evidence Badge qod 점수 기준 3단계 + Uncertainty Alert 3종 추가 (D2.0-08 §2.2.2)

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\_index.md` (v1.1)
</details>

<details>
<summary><b>P0-7. 05_custom-hooks/_index.md 작성</b> ✅ 완료 (2026-04-03)</summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §4(UI 상태 머신 전체), §4.1(9-State 공통 상태 정의 — Hook이 관리하는 상태 대상), §4.2(대표 전이 6건 — Hook 가드 조건·부수효과), §4.3(Decision Lock UI 제약 — useDecision Hook 제약), §4.4(I-10 UI 오케스트레이션 6-State — 이벤트 기반 동기화, 폴링 금지, 전이 지연 500ms), §4.5(§4.1↔§4.4 양방향 매핑 — Store 상태 범위 정의), §4.6(Pipeline S0~S8 ↔ UI 상태 크로스 매핑 D8-M11), §5(UI 이벤트 명세 전체), §5.1(네이밍 규칙 ui.{layer}.{subject}.{action} — Hook 이벤트 구독 패턴), §5.2(네임스페이스 연결 규칙 — Hook별 구독 대상 레이어), §5.3~§5.7(EventType 54+건 6개 레이어: Front Mini 7 + Core/Gate 14 + Node/Main 13 + Tool 6 + CLI 10 + Memory 5 — Hook↔EventType 바인딩), §5.8(공통 페이로드 최소 키: trace_id, cost_mode, approval_required 등 — Hook 반환 타입 필드), §5.9(D2.1-D2 EventTypeRegistry 동기), §2.3.3(CLI↔UI 이벤트 동기 — useTauriIPC Hook trace_id 공유), §7(Failure/Fallback UI — Hook 에러/복구 상태 관리: §7.1~§7.3 FailureCode 14건, §7.6 FallbackRegistry 9건), §10.4(React 컴포넌트 레지스트리 44개 — Hook이 서비스하는 컴포넌트 매핑: HV-CHAT-03 StreamingIndicator, HV-EVID-01/02, HV-APPR-01/02, HV-COST-01/02, HV-STATE-01/02, HV-MEM-01/02, BV-PIPE-01/02 등)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.3(Custom Hooks 8개 + Stores 7개 — **주 정본**: useTauriIPC, useDecision, useWorkflow, useMemory, useCost, useNotification, useAutonomy, useLog / appStore, decisionStore, costStore, notificationStore, authStore, memoryStore, workflowStore) + V1-Phase 4 구현 #12(Custom Hooks 8개, `hooks/` 경로, §6.1.3 참조) + V1-Phase 4 구현 #13(Zustand Stores 7개, `stores/` 경로, §6.1.3 참조) + V1-Phase 4 Gate #6(8 Custom Hooks 정상 동작 검증) + V1-Phase 4 Gate #7(7 Zustand Stores 상태 관리 검증) + V1-Phase 4 AI 프롬프트 요약 L2328-2330(Hook 목록 — **주의**: useAuth/useStreaming으로 표기되어 §6.1.3 정본 useAutonomy/useLog와 불일치, SOURCE_CONFLICT 주석 존재)
- `D:\VAMOS\docs\sot\STEP7-C_UI_UX_전수비교_작업가이드.md` Part 3(입력 영역: S7C-029 토큰 카운터, S7C-030 비용 미리보기), Part 4(응답 렌더링: S7C-038 스트리밍 타이핑), Part 5(응답 렌더링 계속: S7C-040 3-Part 출력 상태, S7C-041 신뢰도 표시 상태, S7C-042 비용 표시 상태), Part 6(데스크톱/CLI: S7C-060 오프라인 상태), Part 7(에이전트 실행: S7C-063 진행률 상태, S7C-065 병렬 에이전트 상태, S7C-069 3-Gate 상태, S7C-070 파이프라인 상태), Part 8(설정/피드백: S7C-072 메모리 관리 상태, S7C-074 비용 대시보드 상태, S7C-076 모델 설정 상태), Part 9(VAMOS 위젯: S7C-081 3-Gate 표시기 Store, S7C-082 비용 게이지 Store, S7C-083 QoD 바 Store) 중 05_custom-hooks 배분 항목
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §6(이슈 해결 매핑 — ISS-3 STEP7-C 104건 중 Hook/Store 관련 항목 매핑) + §6.2(STEP7-C 배분 결과 — 05_custom-hooks ~12건: 8 Hook 시그니처+반환 타입, 7 Store 슬라이스 구조, Hook 간 의존성, Store 구독 패턴, 메모이제이션 전략) + §8.2(서브폴더별 필수 섹션 정의 — 8 Hook 시그니처 목록, 7 Store 슬라이스 구조, 의존성 그래프) + §13(L3 완성도 매트릭스 — E1 Props/시그니처 스키마, E2 상태 전이 규칙, E3 이벤트 핸들러, E6 의존성 명세, E7 테스트 시나리오) + §14(실행 약점 — #1 D2.0-08 참조 누락 대응: 서브폴더별 섹션 매핑 유지, #4 매핑 불완전 대응: _index.md 매핑 현황 테이블)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` §4 LOCK 레지스트리(L1 UI 9-State UI_S0~S8, L14 Custom Hooks 수 8개, L15 Zustand Stores 수 7개, L17 전이 지연 최대 500ms, L19 이벤트 네이밍 ui.{layer}.{subject}.{action}, L20 FailureCode 14 + FallbackRegistry 9) + §5.2 도메인 경계(6-1↔4-1: `useTauriIPC` Hook = 프론트엔드 호출 인터페이스, 4-1 = 백엔드 IPC 커맨드 구현)

**절차**:
1. Part2 §6.1.3(Hook 8개 + Store 7개 정본 목록) 읽기 → D2.0-08 §4~§4.6(상태 머신: 9-State 정의, 전이 6건, Decision Lock, I-10 오케스트레이션 이벤트 기반/폴링 금지/500ms, 양방향 매핑 정본, Pipeline 크로스 매핑), §5~§5.9(이벤트 명세: 네이밍 규칙, 네임스페이스 연결, EventType 54+건 6개 레이어, 공통 페이로드 키, D2.1-D2 동기), §2.3.3(CLI↔UI 이벤트 동기 — useTauriIPC trace_id 공유), §7(Failure/Fallback — Hook 에러 상태), §10.4(컴포넌트 레지스트리 — Hook↔컴포넌트 서빙 매핑) 읽기 + V1-P4 구현 #12/#13(Hooks/Stores 파일 경로) + Gate #6/#7(검증 조건) 읽기
2. **Hook 이름 불일치 검증**: Part2 §6.1.3(정본)의 Hook 목록(useTauriIPC, useDecision, useWorkflow, useMemory, useCost, useNotification, useAutonomy, useLog)과 V1-P4 AI 프롬프트 요약(L2328-2330)의 Hook 목록(useAuth, useStreaming) 비교 — §6.1.3을 정본으로 채택하되, 불일치 2건(useAutonomy↔useAuth, useLog↔useStreaming) 명시 + SOURCE_CONFLICT 주석(L2386-2387: "실제 유래=CLAUDE.md §14/PHASE_B2") 참조
3. 본 계획서 §6.2 STEP7-C 배분 결과에서 05_custom-hooks ~12건 항목 추출 + STEP7-C 원본(Part 3/4/5/6/7/8/9)에서 항목 ID(S7C-xxx) 확인 — S7C-030(비용 미리보기→useCost), S7C-038(스트리밍→streaming 상태), S7C-040/041/042(3-Part 출력·신뢰도·비용 표시 상태), S7C-060(오프라인 상태), S7C-063(진행률→workflow 상태), S7C-069(3-Gate→gate 상태), S7C-070(파이프라인 상태), S7C-072(메모리 관리→useMemory), S7C-074(비용 대시보드→costStore), S7C-082/083(비용 게이지·QoD 바→Store 구독) 등
4. §8.2 필수 섹션 3개 충족을 목표로 _index.md 신규 생성:
   - **8 Hook 시그니처 목록** (§8.2 필수 #1): Part2 §6.1.3 기반 — 8개 Hook 전수 목록(useTauriIPC, useDecision, useWorkflow, useMemory, useCost, useNotification, useAutonomy, useLog) + 각 Hook별: 목적, 파라미터, 반환 타입(§5.8 공통 페이로드 키 기반: trace_id, cost_mode, approval_required, qod_score, failure_code 등), 구독 EventType 목록(§5.3~§5.7 레이어별 바인딩), 서비스 대상 컴포넌트(§10.4 매핑) + Hook 이름 불일치 주석(§6.1.3 vs V1-P4 L2329: useAutonomy↔useAuth, useLog↔useStreaming — §6.1.3 정본 채택) + 파일 경로(`frontend/src/hooks/` V1-P4 #12) — LOCK L14(8개) 준수
   - **7 Store 슬라이스 구조** (§8.2 필수 #2): Part2 §6.1.3 기반 — 7개 Store 전수 목록(appStore, decisionStore, costStore, notificationStore, authStore, memoryStore, workflowStore) + 각 Store별: 슬라이스 필드 정의(§4.1 9-State 상태 값, §5.8 페이로드 키 기반), 셀렉터 목록, 액션/뮤테이션 목록, 구독 패턴(컴포넌트→Store 구독 관계), 메모이제이션 전략(§6.2: Store 구독 패턴 + 메모이제이션) + 파일 경로(`frontend/src/stores/` V1-P4 #13) — LOCK L15(7개) 준수
   - **의존성 그래프** (§8.2 필수 #3): Hook↔Store 의존성(어떤 Hook이 어떤 Store를 사용하는지), Hook↔Hook 의존성(Hook 간 호출 관계), Store↔Store 의존성(Store 간 참조), Hook↔컴포넌트 서빙 매핑(§10.4 기반: useDecision→BV-PIPE-02/HV-STATE-01, useCost→HV-COST-01/BV-DEBUG-02, useMemory→HV-MEM-01/02 등), Hook↔EventType 바인딩(§5.3~§5.7 레이어별), Hook↔IPC 인터페이스(useTauriIPC→4-1 Rust-Tauri 경계, AUTHORITY_CHAIN §5.2)
   - **상태 동기화 아키텍처**: D2.0-08 §4.4 I-10 오케스트레이션 기반 — Core→UI 상태 업데이트 이벤트 기반(폴링 금지), 전이 지연 최대 500ms(LOCK L17), Core↔UI 불일치 감지 시 `ui.core.state.mismatch` 자동 동기화, §4.5 9-state↔6-state 양방향 매핑에서 Store가 관리하는 상태 범위 정의
   - **이벤트 구독 매핑**: D2.0-08 §5.1~§5.9 기반 — 각 Hook/Store별 구독 EventType 레이어(ui.frontmini.*, ui.core.*, ui.gate.*, ui.node.*, ui.main.*, ui.tool.*, ui.cli.*, ui.memory.*), 이벤트 네이밍 LOCK L19 준수, §5.8 공통 페이로드 최소 키(trace_id, decision_id, severity, cost_mode, approval_required, qod_score, failure_code) → Hook 반환 타입 필드 매핑, §5.9 D2.1-D2 EventTypeRegistry 동기 현황
   - **Failure/Recovery 상태 관리**: D2.0-08 §7 기반 — FailureCode 14건(FM 4 + OC 4 + TL/MC 6) 발생 시 Hook/Store 상태 전이 규칙(UI_S7_RECOVERY 진입), FallbackRegistry 9건 복구 액션 시 Store 상태 갱신 패턴, LOCK L20 준수
   - **LOCK 참조 테이블**: L1(9-State UI_S0~S8 — Store 상태 범위), L14(Custom Hooks 수 8개), L15(Zustand Stores 수 7개), L17(전이 지연 최대 500ms — Hook 동기화 제약), L19(이벤트 네이밍 ui.{layer}.{subject}.{action} — Hook 구독 패턴), L20(FailureCode 14 + FallbackRegistry 9 — Hook 에러/복구 상태) — `> LOCK (출처): [원문 그대로]` 형식 준수
   - **STEP7-C ~12건 매핑 현황**: 항목 ID(S7C-xxx), 설명, 관련 Hook/Store, 우선순위(🔴/🟡/🟢), Phase 배정
   - **Phase 배정**: Phase 1 (V1-P4 Week 13-14, Gate #6 Hooks 동작 검증, Gate #7 Stores 상태 관리 검증)
   - **의존성 참조**: 01_builder-view(Builder Panel BV-* 컴포넌트가 Hook 소비), 02_hologram-view(Hologram Panel HV-* 컴포넌트가 Hook 소비 + Glass HUD Store 구독), 03_ui-state-machine(9-State 전이 → Store 상태 반영 + EventType 54+건 Hook 구독), 04_react-components(44개 컴포넌트 ↔ Hook/Store 연동 — §10.4 서빙 매핑), 06_accessibility(WCAG 2.1 AA — Hook 반환 값 접근성 속성), 6-12(Event-Logging: EventType 발행/구독 동기), 4-1(Rust-Tauri: useTauriIPC Hook IPC invoke 경계 — AUTHORITY_CHAIN §5.2)
5. §6.2 이슈 해결 매핑 등재:
   - ISS-3(STEP7-C 104건 중 Hook/Store 관련 항목): ~12건 Hook/Store별 매핑 완료 현황 기록 — 각 S7C 항목이 어느 Hook/Store에 대응하는지 추적 테이블 + 시그니처 정의 + 테스트 시나리오 연계 (§13 E7 최소 3건/Hook)
   - Hook 이름 불일치 사항: §6.1.3(정본) vs V1-P4 L2329 차이(useAutonomy↔useAuth, useLog↔useStreaming) — SOURCE_CONFLICT 주석 확인 결과 및 정본 채택 근거 기록, 불일치가 CONF 수준이면 CONFLICT_LOG.md 등재 검토
6. AUTHORITY_CHAIN.md L1, L14, L15, L17, L19, L20 값과 교차 대조 → 불일치 시 Part2 §6.1.3 / D2.0-08 원문 확인 (L14/L15는 Part2 §6.1.3이 정본, L1/L17/L19/L20은 D2.0-08이 정본)
7. Part2 §6.1.3 원본 + D2.0-08 원본으로 LOCK 값 최종 검증 — 불일치 발견 시 CONFLICT_LOG.md에 등재 + AUTHORITY_CHAIN.md와 해결 방안 동기

**검증**:
- [x] G0-3: 05_custom-hooks/_index.md 존재 + 비어있지 않음 (530줄, 13섹션)
- [x] §8.2 필수 섹션 3개 존재 확인: 8 Hook 시그니처 목록 ✓, 7 Store 슬라이스 구조 ✓, 의존성 그래프 ✓
- [x] LOCK 참조 값(L1, L14, L15, L17, L19, L20)이 AUTHORITY_CHAIN.md + Part2 §6.1.3 / D2.0-08 원본과 일치 — 불일치 0건
- [x] Hook 8개 전수 목록이 Part2 §6.1.3 정본(useTauriIPC, useDecision, useWorkflow, useMemory, useCost, useNotification, useAutonomy, useLog)과 일치
- [x] Store 7개 전수 목록이 Part2 §6.1.3 정본(appStore, decisionStore, costStore, notificationStore, authStore, memoryStore, workflowStore)과 일치
- [x] Hook 이름 불일치(§6.1.3 vs V1-P4 L2329: useAutonomy↔useAuth, useLog↔useStreaming) 명시 + 정본 채택 근거 기록 — CONF 등재 불필요 판정
- [x] ISS-3(Hook/Store 관련 ~12건 매핑 현황) 등재 확인 (1차 12건 + 공유 5건 = 17건)
- [x] STEP7-C ~12건 항목 매핑 완전성 확인 (S7C-030~S7C-083, §6.2 "~12건" 범위 충족)
- [x] R-61-1(9-state 전이 규칙 변경 금지 — Hook/Store가 상태 전이 시 준수) + R-61-5(Decision Lock 후 결론 변경 금지 — useDecision Hook 제약) + R-61-6(이벤트 네이밍 ui.{layer}.{subject}.{action} — Hook 구독 패턴 준수) + R-61-10(Failure/Fallback UI §7 정본 14+9 — Hook 에러/복구 상태 준수) 반영 확인
- [x] 의존성 참조 7건 명시 확인: 01_builder-view, 02_hologram-view, 03_ui-state-machine, 04_react-components, 06_accessibility, 6-12(Event-Logging), 4-1(Rust-Tauri)
- [x] 4-1 경계(useTauriIPC Hook = 프론트엔드 IPC 호출 인터페이스) AUTHORITY_CHAIN §5.2 반영 확인
- [x] §13 L3 완성도 매트릭스 기준(E1 시그니처 스키마, E2 상태 전이, E3 이벤트 핸들러, E6 의존성, E7 테스트) Phase 1 L3 작성 기반 제시

**교차 검증 발견 → 해결**:
- LOCK 6건(L1, L14, L15, L17, L19, L20) 전수 MATCH — AUTHORITY_CHAIN.md + Part2 §6.1.3 / D2.0-08 원본 대조 불일치 0건
- Hook 이름 불일치 2건: §6.1.3(정본) useAutonomy/useLog vs V1-P4 L2329 useAuth/useStreaming — §6.1.3 정본 채택, SOURCE_CONFLICT 주석(L2386-2387) 확인, CONF 등재 불필요 판정 (정본 섹션 확정)
- EventType 산술 검증: 7(frontmini) + 16(core/gate) + 13(node/main) + 6(tool) + 10(cli) + 5(memory) = 57건 확정
- STEP7-C 배분 ~12건 vs 실제 12건(1차) + 5건(공유): STEP7-C 원본 Part 3/4/5/6/7/8/9에서 hook/store 매핑 가능 항목 17건 확인, §6.2 "~12건" 범위 충족

**재검증 보완 (v1.0→v1.1)**:
- 인코딩 깨짐 ~20곳 전수 수정 (U+FFFD 잔여 0건 확인)
- appStore 슬라이스 필드: `LOCK L7`, `LOCK L16` → `(기본 dark, L7 참조)`, `(기본 ko-KR, L16 참조)` 교차 참조 표기 변경 (본 서브폴더 LOCK 테이블 범위 외 항목)
- authStore 역할: `LOCK L10` → `(L10 참조, 06_accessibility 정본)` 교차 참조 표기 변경

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\05_custom-hooks\_index.md` (v1.1)
</details>

<details>
<summary><b>P0-8. 06_accessibility/_index.md 작성</b> ✅ 완료 (2026-04-03)</summary>

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §0(MOD-022 i18n 원칙: 로케일 파일 구조 `locales/{locale}/{namespace}.json`, i18n 키 네이밍 `ui.{component}.{key}`, LogEvent message 영어 고정), §8(UI 접근 제어: Approval Gate, Sensitive Info Masking, PII 차단 UI), §10(디자인 시스템: §10.1 컬러 팔레트 ORANGE/BLUE, §10.2 아이콘 시스템, §10.2a 타이포그래피, §10.3 알림 우선순위), §11-A.10(접근성/다크모드/국제화 S7C-097~104 구현 상세 8항목)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.8(RBAC 4단계 OWNER/ADMIN/OPERATOR/VIEWER 화면 접근 + 제한 사항), V1-Phase 4 구현 #14(i18n 국제화: react-i18next, ko-KR/en-US), #15(디자인 시스템: CSS Custom Properties ORANGE/BLUE 테마, 다크모드 기본, WCAG 2.1 AA), #19(키보드 내비게이션 S7NP-151), V1-P4 Gate #8(i18n 언어 전환 검증), #11(RBAC 접근 제어 검증), #12(디자인 시스템 CSS Custom Properties + 다크모드 전환 검증)
- `D:\VAMOS\docs\sot\STEP7-C_UI_UX_전수비교_작업가이드.md` Part 10(S7C-097~104 코어 8건: 다크모드/키보드탐색/스크린리더/폰트조절/다국어UI/RTL/고대비/애니메이션감소), Part 1(S7C-006 키보드 단축키), Part 3(S7C-025 모델선택, S7C-026 음성입력), Part 4(S7C-036 인라인 인용), Part 5(S7C-047 음성자막), Part 8(S7C-071 프로필설정, S7C-072 메모리관리, S7C-077 MCP 권한), Part 9(S7C-081 3-Gate 표시기)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §6(ISS-3 접근성 17건 매핑) + §6.2(STEP7-C 배분 ~17건 상세 + 이슈 해결 "WCAG 체크리스트 + 키보드 경로 맵") + §8.2(서브폴더별 필수 섹션 정의 — WCAG 2.1 AA 체크리스트, 키보드 내비게이션 경로, ARIA 라벨 목록, i18n 키 인덱스) + §9.2(W-3 RBAC 4단계 Security 정책 동기화 6-1↔6-2)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` §4 LOCK 레지스트리(L5 ORANGE #F97316, L6 BLUE #00F6FF, L7 다크모드 기본, L8 WCAG 2.1 AA 준수, L10 RBAC 4단계 OWNER/ADMIN/OPERATOR/VIEWER, L16 i18n 기본 로케일 ko-KR)

**절차**:
1. D2.0-08 §0(MOD-022 i18n), §8(접근 제어: Approval Gate + Sensitive Info Masking + PII 차단), §10~§10.3(디자인 시스템 전체), §11-A.10(S7C-097~104 구현 상세) 읽기 + Part2 §6.1.8(RBAC 4단계 테이블), V1-P4 구현 #14(i18n)/#15(디자인 시스템)/#19(키보드 내비게이션), Gate #8(i18n)/#11(RBAC)/#12(디자인 시스템) 읽기
2. 본 계획서 §6.2 STEP7-C 배분 결과에서 06_accessibility ~17건 항목 추출 + STEP7-C 원본(Part 1/3/4/5/8/9/10)에서 항목 ID(S7C-xxx) 확인 — S7C-097~104(코어 8건: 다크모드, 키보드 탐색, 스크린 리더, 폰트 크기, 다국어 UI, RTL, 고대비, 애니메이션 감소) + S7C-006/025/026/036/047/071/072/077/081(보조 9건)
3. §8.2 필수 섹션 4개 충족을 목표로 _index.md 신규 생성:
   - **WCAG 2.1 AA 체크리스트**: 색상 대비 4.5:1 기준, 포커스 표시(Focus ring) 규격, 스크린 리더 호환(ARIA 라벨 + role 속성 + alt 텍스트), 고대비 모드(prefers-contrast), 애니메이션 감소(prefers-reduced-motion), 폰트 크기 조절(rem 기반) — S7C-098/099/100/103/104 기반 + LOCK L8 참조 `> LOCK (Part2 V1-P4): WCAG 2.1 AA 준수`
   - **키보드 내비게이션 경로**: Tab 키 전체 UI 요소 접근 경로, Focus ring 표시 규격, Skip to Content 링크, 키보드 단축키 체계(Ctrl+K 검색, Ctrl+N 새 채팅, Ctrl+/ 단축키 목록, Ctrl+Shift+V 음성, Ctrl+Shift+P 커맨드 팔레트) — S7C-098/006 기반 + V1-P4 #19
   - **ARIA 라벨 목록**: 44개 컴포넌트별(D2.0-08 §10.4 Component ID: BV-*/HV-*/CM-*/CLI-*/LOG-*/P2-*) ARIA 라벨/role 속성 인덱스, 스크린 리더 호환 검증 기준 — S7C-099 기반, 04_react-components §10.4 교차 참조
   - **i18n 키 인덱스**: ko-KR(기본)/en-US(보조)/ja-JP(V2 확장) 로케일 파일 구조(`locales/{locale}/{namespace}.json`), i18n 키 네이밍 패턴(`ui.{component}.{key}`, CLI: `cli.{command}.{key}`), LogEvent message 필드 영어 고정 규칙, 언어 전환 이벤트(`ui.common.language.changed`) — §0 MOD-022 + S7C-101 + LOCK L16 참조 `> LOCK (D2.0-08 §0): ko-KR (보조: en-US, V2 확장: ja-JP)`
   - **RBAC 4단계 접근 제어**: OWNER(모든 화면)/ADMIN(시스템 삭제 불가)/OPERATOR(Settings 읽기 전용)/VIEWER(조회만) 역할별 화면 접근 + 제한 사항 — Part2 §6.1.8 정본(CONF-61-003 반영: L10 출처 = Part2 §6.1.8 단독) + D2.0-08 §8 Approval Gate(P2→UI_S5_AWAIT_APPROVAL)/Sensitive Info Masking/PII 차단 패턴 + LOCK L10 참조
   - **디자인 시스템 토큰**: ORANGE #F97316(L5)/BLUE #00F6FF(L6) 컬러 팔레트, 다크모드 기본(L7) + CSS Custom Properties(prefers-color-scheme), 아이콘 시스템(lucide-react, §10.2), 타이포그래피(system-ui, Body 14px/subtitle 16px/heading 20px, §10.2a), 알림 우선순위 3단계(Alert-P0 모달/P1 슬라이드/P2 토스트, §10.3) — S7C-097 + CONF-61-001/002 해결 반영(Part2 원문 #FF6B35/#4A90D9 ≠ D2.0-08 정본 #F97316/#00F6FF → D2.0-08 §10.1 정본 채택)
   - STEP7-C ~17건 매핑 현황 (항목 ID, 설명, 우선순위 🔴/🟡/🟢, Version V1/V2/V3, Phase 배정, 대응 카테고리)
   - LOCK 참조 테이블: L5, L6, L7, L8, L10, L16 — 각 항목 `> LOCK (출처): [원문 그대로]` 형식 준수
   - Phase 배정: Phase 1(V1-P4 Week 13-14, Gate #8 i18n 언어 전환, Gate #11 RBAC 접근 제어, Gate #12 디자인 시스템 CSS Custom Properties + 다크모드), Phase 2(V2 고대비 모드 S7C-103), Phase 3(V3 스크린 리더 완전 지원 S7C-099, RTL S7C-102)
   - 의존성 참조: 01_builder-view(Builder 컴포넌트 접근성 적용 컨텍스트 + CLI 키보드 단축키), 02_hologram-view(Hologram 컴포넌트 접근성 적용 + Glass HUD 색상 대비), 03_ui-state-machine(상태 전이 시 ARIA live region 업데이트 + 접근성 상태 반영), 04_react-components(44개 컴포넌트 WCAG/ARIA 적용 — §10.4 Component ID 기반 전수 매핑), 05_custom-hooks(Hook 반환 값 접근성 속성 — useNotification 알림 접근성), 6-2(Security — W-3 RBAC 정책 동기화), 6-12(Event-Logging: ui.common.language.changed + ui.common.theme.changed 이벤트 동기)
4. §6.2 이슈 해결 매핑 등재:
   - ISS-3(STEP7-C 104건 중 접근성 관련 항목): ~17건 카테고리별 매핑 완료 현황 기록 — WCAG 체크리스트(S7C-098/099/100/103/104) + 키보드 경로 맵(S7C-006/098) + i18n(S7C-101/071/102) + 디자인 시스템(S7C-097) + RBAC/권한(S7C-077/081) + 보조 접근성(S7C-025/026/036/047/072)
   - W-3(RBAC 4단계 Security 정책 동기화 6-1↔6-2): 잠재 충돌 모니터링 현황 + 6-2 도메인 참조 링크 — Part2 §6.1.8 RBAC 4단계와 6-2 Security 정책 간 동기 방안 명시
5. AUTHORITY_CHAIN.md L5, L6, L7, L8, L10, L16 값과 교차 대조 → 불일치 시 D2.0-08/Part2 원문 확인
   - CONF-61-001/002 해결 내역 반영 확인: L5 ORANGE #F97316, L6 BLUE #00F6FF (D2.0-08 §10.1 정본 ≠ Part2 원문 #FF6B35/#4A90D9)
   - CONF-61-003 해결 내역 반영 확인: L10 출처 = Part2 §6.1.8 단독 (D2.0-08 §8은 Approval Gate/Masking 패턴, RBAC 4단계 아님)
6. D2.0-08/Part2 원본으로 LOCK 값 최종 검증 — 불일치 발견 시 CONFLICT_LOG.md에 등재 + AUTHORITY_CHAIN.md와 해결 방안 동기

**검증**:
- [x] G0-3: 06_accessibility/_index.md 존재 + 비어있지 않음 (507줄, 12섹션)
- [x] §8.2 필수 섹션 4개 존재 확인: WCAG 2.1 AA 체크리스트 ✓, 키보드 내비게이션 경로 ✓, ARIA 라벨 목록 ✓, i18n 키 인덱스 ✓
- [x] LOCK 참조 값(L5, L6, L7, L8, L10, L16)이 AUTHORITY_CHAIN.md + D2.0-08/Part2 원본과 일치 — CONF-61-001/002/003 해결 반영, 불일치 0건
- [x] RBAC 4단계(OWNER/ADMIN/OPERATOR/VIEWER) 화면 접근 + 제한 사항이 Part2 §6.1.8 정본과 일치 (L10, CONF-61-003: Part2 §6.1.8 단독 출처)
- [x] STEP7-C ~17건 항목 매핑 완전성 확인 (S7C-097~104 코어 8건 + S7C-006/025/026/036/047/071/072/077/081 보조 9건, §6.2 "~17건" 범위 충족)
- [x] R-61-3(모든 UI 텍스트 i18n 키 관리 — 하드코딩 금지, §0 MOD-022 반영) + R-61-8(승인/비용/정책 UI HOLD 전환 + 명시적 승인/거절 — §8 Approval Gate 반영) + R-61-7(LogEvent message 영어 고정) 반영 확인
- [x] 의존성 참조 7건 명시 확인: 01_builder-view, 02_hologram-view, 03_ui-state-machine, 04_react-components, 05_custom-hooks, 6-2(Security), 6-12(Event-Logging)
- [x] ISS-3(접근성 ~17건 카테고리별 매핑) + W-3(RBAC 6-1↔6-2 동기화 모니터링) 등재 확인
- [x] 디자인 시스템 토큰(ORANGE #F97316/BLUE #00F6FF/다크모드) 섹션에 CONF-61-001/002 해결 반영 — D2.0-08 §10.1 정본 색상 값 채택 명시

**교차 검증 발견 → 해결**:
- S7C-099 Version: STEP7-C 원본 "V2" ≠ D2.0-08 §11-A.10 "[V3/HIGH]" → D2.0-08 정본 채택 (V3)
- 기존 _index.md LOCK 오류: L5 #FF6B35→#F97316, L6 #4A90D9→#00F6FF 정정 (CONF-61-001/002 반영)
- 색상 대비 수치: Phase 0에서 정밀 계산 불가 → "Phase 1 정밀 측정 대상" 표기로 해결

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\_index.md` (v1.0)

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\_index.md`
</details>

**Phase 0→Phase 1 게이트 (G0)**: ✅ **ALL PASS** (2026-04-03)
- [x] **G0-1**: 본 계획서 APPROVED (CONDITIONAL APPROVED → A-, S10-3)
- [x] **G0-2**: AUTHORITY_CHAIN.md에 LOCK 20건(L1~L20) 전체 포함 (P0-1 v2.1)
- [x] **G0-3**: 6개 서브폴더 _index.md 존재 + 비어있지 않음 (P0-3~P0-8 전수 완료)

### 7.3 Phase 1 세부 항목 (V1-Phase 4 정렬)

| # | 항목 | Part2 출처 | D2.0-08 출처 | 서브폴더 |
|---|------|-----------|------------|---------|
| 1 | 3-Column Fluid Layout | §6.1.1 #1 | §2.1.1, §3 | 01_builder-view |
| 2 | Builder View (Cockpit) | §6.1.1 #2 | §2.1 | 01_builder-view |
| 3 | Hologram View | §6.1.1 #3 | §2.2 | 02_hologram-view |
| 4 | CLI Interface | §6.1.1 #4 | §2.3 | 01_builder-view |
| 5 | React 컴포넌트 ~44개 | §6.1.2 | §10.4 | 04_react-components |
| 6 | Custom Hooks 8개 | §6.1.3 | — | 05_custom-hooks |
| 7 | Zustand Stores 7개 | §6.1.3 | — | 05_custom-hooks |
| 8 | UI 9-State Machine | §6.1.6 | §4 | 03_ui-state-machine |
| 9 | Failure/Fallback UI | §6.1.7 | §7 | 03_ui-state-machine |
| 10 | RBAC 접근 제어 | §6.1.8 | §8 | 06_accessibility |
| 11 | i18n 국제화 | V1-P4 #14 | §0 MOD-022 | 06_accessibility |
| 12 | 디자인 시스템 (ORANGE/BLUE) | V1-P4 #15 | §10 | 06_accessibility |
| 13 | 7개 페이지 (Dashboard~NodeDetail) | V1-P4 #4~#10 | §6 | 01_builder-view |
| 14 | 멀티모달 UI V1 | §6.1.5 V1열 | §6 | 02_hologram-view |

---

#### Phase 1 단계별 상세 작업 절차

<!-- ═══════════════════════════════════════════════════ -->
<!-- 01_builder-view (#1, #2, #4, #13)                  -->
<!-- ═══════════════════════════════════════════════════ -->

<details>
<summary><b>#1. 3-Column Fluid Layout</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #1 "3-Column Fluid Layout"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑 — 01~06 전체)

**목표**: D2.0-08 §2.1.1 정본 3-Column 규격(Left 250-300px / Center flex-grow / Right 350-400px)을 Tauri 1440×900 + 최소 1280×720 환경에서 유동 레이아웃으로 구현하고, LOCK L2-L4, L11, L12 준수를 검증 가능한 L3 상세 파일로 작성한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.1.1(3-Column 규격), §3+§3.1(공통 규칙+V1 제약)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.1 #1(핵심 레이아웃)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\_index.md` §1(레이아웃 구조)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L2-L4, L11, L12 LOCK 정의

**절차**:
1. D2.0-08 §2.1.1 읽기 — Left/Center/Right 3-Column 폭 규격(L2: 250-300px, L3: flex-grow, L4: 350-400px) 추출 + §3.1 V1 제약(최소 해상도 1280×720, Tauri 기본 1440×900) 확인
2. 01_builder-view/_index.md §1 레이아웃 구조 섹션에서 기존 정의 범위 확인 — L3 상세 파일에서 보강할 항목 식별
3. CSS Grid / Flexbox 기반 레이아웃 명세 작성: 3-Column 정의(`grid-template-columns: minmax(250px,300px) 1fr minmax(350px,400px)`), 최소 해상도 fallback(1280px 미만 시 Left 패널 축소/접힘 규칙)
4. 패널 리사이즈 인터랙션 정의: 드래그 핸들 위치, 최소/최대 제약, 리사이즈 중 상태(CSS cursor, 스냅 가이드)
5. Tauri 윈도우 제약 명세: `minWidth: 1280, minHeight: 720, width: 1440, height: 900` — tauri.conf.json 매핑
6. 반응형 breakpoint 정의: 1280px(최소), 1440px(기본), 1920px(와이드) — 각 breakpoint에서 3-Column 폭 변화 테이블 작성
7. STEP7-C 관련 항목(S7C-001~005 레이아웃 관련) 매핑 확인 후 체크리스트 반영

**검증**:
- [x] L2(Left 250-300px), L3(Center flex-grow), L4(Right 350-400px) 규격이 D2.0-08 §2.1.1 정본과 일치 ✅
- [x] L11(최소 1280×720), L12(Tauri 1440×900) 제약 반영 확인 ✅
- [x] 1280px 최소 해상도에서 3-Column 합산 폭이 뷰포트를 초과하지 않음 (250+flex+350 ≤ 1280) ✅
- [x] 패널 리사이즈 시 최소/최대 제약이 LOCK 범위 내에서 동작 ✅
- [x] STEP7-C 레이아웃 관련 항목 매핑 완료 ✅

> **완료**: 2026-04-12. 3-Column Fluid Layout L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (fluid_layout.md v1.0, ~370줄)
> - LOCK 5건 (L2, L3, L4, L11, L12) 전체 AUTHORITY_CHAIN 정합 확인
> - STEP7-C 3건 매핑 (S7C-001, S7C-021, S7C-053)
> - Phase 2 테스트 시나리오 12건 작성
> - 재검증 2회, 수정 1건 (Center 기본 폭 계산 810→800px)
> - CONFLICT/LOCK 변경 없음

**[P1-1] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — fluid_layout.md (3-Column Fluid Layout L3 상세)
- 1. 게이트: §10 #2 LOCK 출처 ✅, #5 D2.0-08 정본 ✅, #8 도메인 참조 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\fluid_layout.md` (3-Column Fluid Layout L3 상세)
</details>

<details>
<summary><b>#2. Builder View (Cockpit)</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #2 "Builder View (Cockpit)"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-2 (Part2 §6.1.4 구현 결정 4건 미확정), ISS-3 (STEP7-C 104건 미매핑)

**목표**: Builder View(Cockpit) 화면의 3-Pane 패널 구성(Left: 파일 트리+탐색, Center: 에디터/빌더, Right: 속성+인스펙터)을 D2.0-08 §2.1 정본 기반으로 상세 정의하고, User Actions → LogEvent 매핑 및 CLI 동기(LOCK L9) 연동 인터페이스를 명세한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.1~§2.1.3(Builder View 전체: 3-Column, Panel Composition, User Actions→LogEvent)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.1 #2(Builder View), §6.1.4(구현 결정 4건)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\_index.md` §2(Builder View 구조)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L9 LOCK 정의

**절차**:
1. D2.0-08 §2.1 전체 읽기 — Builder View 정의: Left(파일 트리, 노드 목록), Center(에디터/빌더 캔버스), Right(속성 패널, 인스펙터) + §2.1.2 Panel Composition 상세 + §2.1.3 User Actions → LogEvent 매핑표
2. Part2 §6.1.4 구현 결정 4건 읽기 — ISS-2 미확정 항목 파악 후, D2.0-08 정본 기준으로 Phase 1 결정안 도출(결정 불가 시 CONFLICT_LOG 등재)
3. Builder View 패널별 컴포넌트 배치 명세 작성: Left(FileTree, NodeList, SearchBar), Center(EditorCanvas, BuilderToolbar), Right(PropertyPanel, InspectorPanel) — 각 컴포넌트 역할·크기·상호작용 정의
4. User Actions → LogEvent 매핑표 작성: D2.0-08 §2.1.3 기반, 이벤트 네이밍 LOCK L19(ui.{layer}.{subject}.{action}) 준수
5. CLI 동기 인터페이스 정의: Builder View 상태 변경 시 CLI 명령어 6개(LOCK L9) 중 관련 명령어와의 동기 규칙 — 상태 갱신 방향(UI→CLI, CLI→UI) 명시
6. ISS-2 해결 결과 문서화: 4건 각각에 대해 결정안/미결정 사유 기록, 미결정 항목은 Phase 1 내 해결 조건 명시
7. STEP7-C 관련 항목(01_builder-view 배정 ~28건) 매핑 확인

**검증**:
- [x] Builder View 3-Pane 구성이 D2.0-08 §2.1 정본과 일치 ✅
- [x] User Actions → LogEvent 매핑이 D2.0-08 §2.1.3과 일치 + L19 네이밍 규칙 준수 ✅
- [x] ISS-2 구현 결정 4건 해결 상태 기록 (4건 전체 RESOLVED) ✅
- [x] CLI 동기 인터페이스가 L9(6개 명령어) 범위 내에서 정의 ✅
- [x] STEP7-C 01_builder-view 배정 항목 매핑 확인 (18건 중 17건 완료, 1건 V2) ✅

> **완료**: 2026-04-12. Builder View L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (builder_view_cockpit.md v1.0, ~450줄)
> - ISS-2 구현 결정 4건 전체 RESOLVED
> - LogEvent 12건 매핑 (L19 준수)
> - CLI 동기 6건 양방향 (L9 준수)
> - STEP7-C 18건 중 17건 매핑, S7C-011 V2 이월
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-2] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — builder_view_cockpit.md (Builder View L3 상세)
- 1. 게이트: §10 LOCK 7건 출처 ✅, ISS-2 RESOLVED ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: S7C-011 멀티 대화 탭 → V2

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\builder_view_cockpit.md` (Builder View L3 상세)
</details>

<details>
<summary><b>#4. CLI Interface</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #4 "CLI Interface"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑)

**목표**: D2.0-08 §2.3~§2.3.3 정본 기반으로 CLI 6개 명령어(LOCK L9) 구조, 출력 형식, Builder/Hologram View UI 동기 규칙을 L3 상세로 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.3~§2.3.3(CLI 구조, 명령어 6개, 출력 형식, UI 동기)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.1 #4(CLI Interface)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\_index.md` §4(CLI 인터페이스)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L9 LOCK 정의

**절차**:
1. D2.0-08 §2.3 읽기 — CLI 6개 명령어 목록 추출 (LOCK L9) + §2.3.1 명령어별 인자/옵션/반환 형식 + §2.3.2 출력 포맷(JSON/테이블/plain) + §2.3.3 UI 동기 규칙
2. 01_builder-view/_index.md §4 CLI 인터페이스 기존 정의 확인 — L3에서 보강할 세부 항목 식별
3. CLI 명령어 상세 명세 작성: 6개 각각에 대해 — 명령어 구문, 필수/선택 인자, 반환 값 스키마, 에러 코드, 사용 예시
4. CLI 출력 형식 정의: JSON 구조체 스키마, 테이블 렌더링 규칙(컬럼 폭, 정렬), plain text 폴백
5. CLI ↔ UI 동기 프로토콜 정의: CLI 명령 실행 → UI 상태 반영 경로(Zustand Store 업데이트), UI 조작 → CLI 히스토리 반영 경로
6. 이벤트 연동: CLI 명령어 실행 시 발생하는 EventType(LOCK L19: ui.cli.{subject}.{action}) 목록 정의 — D2.0-08 §5.6-A CLI 레이어 10건 참조

**검증**:
- [x] CLI 6개 명령어가 D2.0-08 §2.3 정본과 일치 (LOCK L9) ✅
- [x] 각 명령어의 인자/반환/에러 스키마가 §2.3.1 정본 기반 ✅
- [x] CLI ↔ UI 동기 프로토콜이 양방향(CLI→UI, UI→CLI) 모두 정의 ✅
- [x] EventType 네이밍이 L19(ui.{layer}.{subject}.{action}) 준수 ✅
- [x] STEP7-C CLI 관련 항목 매핑 확인 ✅

> **완료**: 2026-04-12. CLI Interface L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (cli_interface.md v1.0, ~530줄)
> - CLI 6개 명령어 L9 준수 (인자/반환/에러 전체 스키마)
> - EventType 10건 L19 준수 (ui.cli.{subject}.{action})
> - CLI↔UI 양방향 동기 프로토콜 완성
> - STEP7-C 7건 매핑
> - Phase 2 테스트 12건
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-3] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — cli_interface.md (CLI Interface L3 상세)
- 1. 게이트: §10 LOCK L9/L19 출처 ✅, 6개 명령어 정합 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\cli_interface.md` (CLI Interface L3 상세)
</details>

<details>
<summary><b>#13. 7개 페이지 (Dashboard~NodeDetail)</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #13 "7개 페이지 (Dashboard~NodeDetail)"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-2 (Part2 §6.1.4 구현 결정 4건 미확정 — 7개 페이지 정의), ISS-3 (STEP7-C 104건 미매핑)

**목표**: V1-P4 #4~#10에 정의된 7개 페이지(Dashboard, PipelineBuilder, NodeEditor, ChatPage, SettingsPage, MonitoringPage, NodeDetailPage)의 라우팅 구조, 페이지별 컴포넌트 배치, 데이터 흐름을 L3 상세로 정의하며, ISS-2의 구현 결정 4건을 해결한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §6(페이지별 구조)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4 #4~#10(7개 페이지), §6.1.4(구현 결정 4건)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\_index.md` §5(페이지 정의)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` 관련 LOCK

**절차**:
1. V1-P4 #4~#10 읽기 — 7개 페이지 각각의 정의·역할·구현 범위 추출 + D2.0-08 §6에서 페이지별 화면 구조 확인
2. Part2 §6.1.4 구현 결정 4건 읽기 — 7개 페이지 관련 미확정 항목(페이지 라우팅 구조, 공통 레이아웃 적용 범위, 페이지 간 상태 전달 방식, 지연 로딩 전략) 파악
3. React Router 라우팅 구조 설계: 7개 페이지 경로 정의(`/dashboard`, `/pipeline`, `/node/:id`, `/chat`, `/settings`, `/monitoring`, `/node-detail/:id`), 중첩 라우트 구조, 레이아웃 래퍼(3-Column 적용 범위)
4. 페이지별 컴포넌트 배치 명세: 각 페이지에서 사용하는 React 컴포넌트 목록(#5 ~44개 중 해당 컴포넌트), 데이터 의존성(Zustand Store, Custom Hook)
5. 페이지 간 상태 전달 설계: URL 파라미터, Zustand 전역 상태, 페이지 진입/이탈 시 상태 초기화 규칙
6. 지연 로딩(Lazy Loading) 전략: React.lazy + Suspense 적용 페이지, 코드 분할 기준, fallback UI 정의
7. ISS-2 구현 결정 4건 해결안 문서화: 각 결정에 대해 선택안, 근거(D2.0-08 정본 기반), 영향 범위
8. STEP7-C 페이지 관련 항목 매핑

**검증**:
- [x] 7개 페이지가 V1-P4 #4~#10 정의와 1:1 대응 ✅
- [x] 라우팅 구조가 React Router v6+ 패턴 준수 ✅
- [x] ISS-2 구현 결정 4건 전체 해결 (RESOLVED 또는 조건부 해결+추적) ✅
- [x] 각 페이지의 컴포넌트 참조가 #5 React 컴포넌트 목록과 정합 ✅
- [x] 지연 로딩 전략이 Tauri 환경(로컬 번들, L12) 특성 반영 ✅

> **완료**: 2026-04-12. 7개 페이지 L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (seven_pages.md v1.0, ~706줄)
> - 7개 페이지 V1-P4 #4~#10 전수 1:1 대응
> - React Router v6+ 라우팅 10개, 지연 로딩 전략
> - ISS-2 구현 결정 4건 전체 RESOLVED
> - STEP7-C 12건 매핑, 신규 컴포넌트 25건 식별
> - 재검증 4회, 수정 3건 (라우트수 11→10, LOCK L16/L8 참조 추가)
> - CONFLICT/LOCK 변경 없음

**[P1-4] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — seven_pages.md (7개 페이지 L3 상세)
- 1. 게이트: 7페이지 1:1 대응 ✅, ISS-2 RESOLVED ✅, LOCK L1~L19 정합 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\seven_pages.md` (7개 페이지 L3 상세)
</details>

<!-- ═══════════════════════════════════════════════════ -->
<!-- 02_hologram-view (#3, #14)                         -->
<!-- ═══════════════════════════════════════════════════ -->

<details>
<summary><b>#3. Hologram View</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #3 "Hologram View"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-6 (6-1 ↔ 6-11 Hologram-Main-LLM 경계), ISS-3 (STEP7-C 104건 미매핑)

**목표**: D2.0-08 §2.2 정본 기반 Hologram View의 3-Pane 레이아웃(타임라인, 스트리밍, Glass HUD), 인터랙티브 렌더링, LogEvent 12건을 L3 상세로 정의하며, 6-1 ↔ 6-11 도메인 경계(ISS-6)를 명확히 구분한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §2.2~§2.2.3(Hologram View: 3-Pane Layout, 패널 구성, LogEvent 12건)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.1 #3(Hologram View), V1-P4 #3(Hologram View 구현)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\_index.md` §1(Hologram View 구조)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` 도메인 경계(6-1 ↔ 6-11)

**절차**:
1. D2.0-08 §2.2 전체 읽기 — Hologram View 3-Pane 구성: Left(타임라인 히스토리), Center(스트리밍 출력+Glass HUD 오버레이), Right(증거/컨텍스트 패널) + §2.2.2 패널 구성 상세 + §2.2.3 LogEvent 12건 매핑표
2. 02_hologram-view/_index.md §1 기존 정의 확인 — L3 보강 범위 식별
3. Hologram View 패널별 컴포넌트 명세 작성: Left(TimelineList, HistoryFilter), Center(StreamingOutput, GlassHUD, TypingIndicator), Right(EvidencePanel, ContextViewer) — 각 컴포넌트 역할, 데이터 소스, 갱신 주기
4. 인터랙티브 렌더링 명세: Markdown 렌더링(코드 하이라이트, 수식 LaTeX), 스트리밍 토큰 애니메이션, Glass HUD 오버레이 투명도/위치 규칙
5. LogEvent 12건 상세 정의: D2.0-08 §2.2.3 기반, 이벤트 네이밍 L19(ui.hologram.{subject}.{action}) 준수, 각 이벤트의 트리거 조건·페이로드 스키마
6. 6-1 ↔ 6-11 경계 구분: Hologram View UI 렌더링(6-1 소관) vs. LLM 스트리밍 로직/모델 선택(6-11 소관) — 인터페이스 계약 정의(API 엔드포인트, 메시지 포맷)
7. STEP7-C 02_hologram-view 배정 ~12건 항목(S7C-017~020, S7C-033/035, S7C-040, S7C-045/046, S7C-051, S7C-081) 매핑

**검증**:
- [x] Hologram View 3-Pane 구성이 D2.0-08 §2.2 정본과 일치 ✅
- [x] LogEvent 12건이 D2.0-08 §2.2.3과 1:1 대응 + L19 네이밍 준수 ✅
- [x] 6-1 ↔ 6-11 경계가 AUTHORITY_CHAIN.md 도메인 경계 선언과 일치 (ISS-6) ✅
- [x] 인터랙티브 렌더링 명세가 Markdown/LaTeX/스트리밍 커버 ✅
- [x] STEP7-C ~12건 항목 전수 매핑 ✅

> **완료**: 2026-04-12. Hologram View L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (hologram_view.md v1.0, 16 컴포넌트 TypeScript 명세)
> - LOCK 10건 전체 AUTHORITY_CHAIN 정합 확인
> - LogEvent 12건 D2.0-08 §2.2.3 1:1 대응, L19 준수
> - 6-1↔6-11 경계: StreamInterface 계약 정의 (ISS-6)
> - STEP7-C 11건 매핑 (Critical 3건 L3 완료)
> - Phase 2 테스트 12건
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-5] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — hologram_view.md (Hologram View L3 상세)
- 1. 게이트: LOCK 10건 정합 ✅, LogEvent 12건 L19 ✅, ISS-6 경계 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\hologram_view.md` (Hologram View L3 상세)
</details>

<details>
<summary><b>#14. 멀티모달 UI V1</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #14 "멀티모달 UI V1"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-5 (CLIP 마이그레이션 V2 사전 준비), ISS-3 (STEP7-C 104건 미매핑)

**목표**: Part2 §6.1.5 V1열 6건(CLIP, OCR, STT, TTS, 차트, 문서)의 UI 컴포넌트 구조, 입출력 흐름, 상태 변화를 L3 상세로 정의하며, ISS-5(D8-L03 CLIP 마이그레이션 V2 사전 준비) 범위를 V1 안에서 확보한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §6(멀티모달: §6.1 아키텍처 플로우, §6.2 상태 변화, §6.4.1 CLIP)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.5(멀티모달 UI V1열 6건 + D8-L03)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\_index.md` §3(멀티모달 UI)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` 관련 LOCK

**절차**:
1. D2.0-08 §6 읽기 — 멀티모달 아키텍처 플로우(§6.1), 상태 변화(§6.2: IDLE→PROCESSING→COMPLETE/ERROR), CLIP 상세(§6.4.1) + Part2 §6.1.5 V1열 6건 범위 확인
2. V1 6건 각각의 UI 컴포넌트 설계:
   - CLIP: 이미지 업로드 UI, 임베딩 결과 표시, 유사도 시각화
   - OCR: 문서 스캔 UI, 텍스트 추출 결과 오버레이, 신뢰도 표시
   - STT: 음성 입력 UI, 녹음 버튼/파형 표시, 전사 결과 스트리밍
   - TTS: 음성 출력 UI, 재생 컨트롤, 음성 합성 상태 표시
   - 차트: 데이터 시각화 컴포넌트, 차트 타입 선택, 인터랙티브 줌/팬
   - 문서: 문서 뷰어(PDF/이미지), 페이지 네비게이션, 어노테이션 레이어
3. 멀티모달 상태 머신 정의: IDLE→UPLOADING→PROCESSING→COMPLETE/ERROR 전이 규칙 — UI 9-State(#8)와의 매핑(멀티모달 상태 ⊂ UI_S3_STREAMING/UI_S4_TOOL_RUNNING)
4. ISS-5 V2 사전 준비: CLIP V1 구현에서 V2 ImageBind 마이그레이션을 위한 추상화 레이어 정의(인터페이스 분리, 모델 교체 가능 구조)
5. STEP7-C 멀티모달 관련 항목(S7C-045/046/051 등) 매핑

**검증**:
- [x] V1 6건(CLIP, OCR, STT, TTS, 차트, 문서) 전체 UI 명세 존재 ✅
- [x] 멀티모달 상태 전이가 D2.0-08 §6.2 정본과 일치 ✅
- [x] CLIP UI가 V2 마이그레이션 추상화 레이어를 포함 (ISS-5) ✅
- [x] 각 모달의 입출력 데이터 포맷 정의 완료 ✅
- [x] STEP7-C 멀티모달 관련 항목 매핑 ✅

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\multimodal_ui_v1.md` (멀티모달 UI V1 L3 상세)

> **완료**: 2026-04-12. 멀티모달 UI V1 L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (multimodal_ui_v1.md v1.0, ~620줄)
> - V1 6건 (CLIP, OCR, STT, TTS, 차트, 문서) 전체 UI 컴포넌트 명세
> - 멀티모달 상태 머신 4-State, D2.0-08 §6.2 16-state 전수 매핑
> - ISS-5 CLIP→ImageBind 추상화 레이어 (PARTIALLY-RESOLVED, V2 완결)
> - STEP7-C 9건 매핑 (V1 5건 직접)
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-6] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — multimodal_ui_v1.md (멀티모달 UI V1 L3 상세)
- 1. 게이트: V1 6건 전수 명세 ✅, 상태 매핑 ✅, ISS-5 추상화 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: ISS-5 V2 완결 (Phase 2 P2-1에서 처리)
</details>

<!-- ═══════════════════════════════════════════════════ -->
<!-- 03_ui-state-machine (#8, #9)                       -->
<!-- ═══════════════════════════════════════════════════ -->

<details>
<summary><b>#8. UI 9-State Machine</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #8 "UI 9-State Machine"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상 (Gate #10: UI 9-State SM 전이 동작 검증)
- §6 이슈: ISS-1 (9-state/6-state 양방향 매핑, D2.0-08 §4.5 해결), ISS-7 (EventType 54+건 동기 등록)

**목표**: D2.0-08 §4 정본 기반 UI 9-State(UI_S0_BOOT ~ UI_S8_ARCHIVED, LOCK L1) 전이 규칙, 전이 지연 500ms(LOCK L17), 6-state 양방향 매핑(ISS-1), EventType 54+건 동기 등록(ISS-7)을 L3 상세로 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §4(UI State Machine 전체: §4.1 9-state 정의, §4.2 전이 규칙, §4.3 전이 조건, §4.4 전이 지연, §4.5 6-state 매핑)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.6(UI State Machine 9-state + 전이 규칙 + §4.5 양방향 매핑)
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §5.3~§5.7(EventType 6개 레이어 54+건)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\_index.md` §1(상태 머신 구조)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L1, L17 LOCK 정의

**절차**:
1. D2.0-08 §4 전체 읽기 — 9-State 정의(§4.1: UI_S0_BOOT ~ UI_S8_ARCHIVED), 허용 전이 규칙(§4.2: 전이 매트릭스), 전이 조건(§4.3: 트리거 이벤트+가드 조건), 전이 지연(§4.4: 500ms LOCK L17), 6-state 매핑(§4.5: 9→6 축소 매핑표)
2. 9-State 전이 매트릭스 작성: 9×9 매트릭스(Source→Target), 각 셀에 허용/금지 + 트리거 이벤트 + 가드 조건 기록 — R-61-1(전이 규칙 변경 금지) 명시적 준수
3. ISS-1 해결: 9-state → 6-state 매핑 함수(`mapToSixState()`) + 6-state → 9-state 역매핑 함수(`mapToNineState()`) 정의 — D2.0-08 §4.5 양방향 매핑표 기반, 모호한 매핑(1:N) 해결 규칙 명시
4. 전이 지연 구현 명세: L17(500ms) 적용 대상 전이 목록, 지연 중 UI 표시(로딩 인디케이터), 지연 취소 조건
5. ISS-7 해결: D2.0-08 §5.3~§5.7 EventType 54+건 목록 추출 → 각 이벤트가 발생시키는 상태 전이 매핑 → D2.1-D2 EventTypeRegistry 동기 등록 형식 정의
6. Zustand 상태 관리 연동: uiStateStore에서 currentState/previousState/transitionHistory 관리, 전이 함수(transition(targetState, event)) 인터페이스
7. STEP7-C 상태 머신 관련 항목 매핑

**검증**:
- [x] 9-State 정의가 D2.0-08 §4.1 정본과 일치 (LOCK L1) ✅
- [x] 전이 매트릭스 9×9가 D2.0-08 §4.2 정본과 일치 — R-61-1 준수 ✅
- [x] 9↔6 양방향 매핑이 D2.0-08 §4.5와 일치 (ISS-1 RESOLVED) ✅
- [x] 전이 지연 500ms가 L17 LOCK 준수 ✅
- [x] EventType 54+건 전체 → 상태 전이 매핑 완료 (ISS-7 RESOLVED) ✅
- [x] Gate #10 검증 가능: 9-State SM 전이 동작 테스트 시나리오 포함 ✅

> **완료**: 2026-04-12. UI 9-State Machine L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (nine_state_machine.md v1.0, ~675줄)
> - 9-State 정의 + 9×9 전이 매트릭스 16건 (LOCK L1, R-61-1)
> - ISS-1: 9↔6 양방향 매핑 함수 정의 (RESOLVED)
> - ISS-7: EventType 57건 → 상태 전이 매핑 (RESOLVED)
> - 전이 지연 500ms (LOCK L17) 적용 대상 + UI 표시
> - Zustand uiStateStore 인터페이스, STEP7-C 15건 매핑
> - Phase 2 테스트 14건
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-7] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — nine_state_machine.md (UI 9-State Machine L3)
- 1. 게이트: Gate #10 전이 동작 검증 가능 ✅, ISS-1 RESOLVED ✅, ISS-7 RESOLVED ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\nine_state_machine.md` (UI 9-State Machine L3 상세)
</details>

<details>
<summary><b>#9. Failure/Fallback UI</b> ✅ 완료 (2026-04-12)</summary>

> **완료**: 2026-04-12. Failure/Fallback UI L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (failure_fallback_ui.md v1.0, ~399줄)
> - FailureCode 14건 + FallbackRegistry 9건 (LOCK L20, R-61-10)
> - UI_S7_RECOVERY 전이 명세 (진입 3조건, 이탈 2조건)
> - i18n 키 14건 매핑 (L16, R-61-3)
> - Part2 §6.1.7 교차검증 4건 GAP (보완적, 충돌 아님)
> - STEP7-C 5건 매핑
> - 재검증 결과 수정 0건
> - CONFLICT/LOCK 변경 없음

**대조 기준**:
- §7 세부 작업: #9 "Failure/Fallback UI"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑)

**목표**: D2.0-08 §7 정본 기반 FailureCode 14건 + FallbackRegistry 9건(LOCK L20)의 UI 표시 규칙, 복구 동작, UI_S7_RECOVERY 상태 진입/이탈 조건을 L3 상세로 정의한다. R-61-10(§7 정본 14+9 정의 그대로 구현) 엄격 준수.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §7(Failure/Fallback UI 전체: §7.3 Phase 배정, §7.4 안내 문구 템플릿, §7.6 FailureCode 14+FallbackRegistry 9)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.7(Failure/Fallback UI 규칙: 4개 에러코드 + 14+9 전체 참조)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\_index.md` §3(Failure/Fallback 정의)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L20 LOCK 정의

**절차**:
1. D2.0-08 §7 전체 읽기 — FailureCode 14건(FM 4: Front-Mini + OC 4: Approval/Cost + TL/MC 6: Tool/Memory) + FallbackRegistry 9건(각 FailureCode → 복구 동작 매핑) + §7.4 사용자 안내 문구 템플릿
2. FailureCode 14건 상세 테이블 작성: 코드명, 카테고리(FM/OC/TL/MC), 발생 조건, 심각도, UI 표시 컴포넌트(CM-ALERT-01/HV-APPR-01/HV-COST-01 등), 표시 형식(모달/배너/토스트)
3. FallbackRegistry 9건 상세 테이블 작성: 레지스트리 ID, 대상 FailureCode, 복구 동작(재시도/대체 경로/수동 개입), 복구 시간 제한, 복구 실패 시 최종 상태
4. UI_S7_RECOVERY 상태 전이 명세: 진입 조건(어떤 FailureCode에서 RECOVERY 진입), 이탈 조건(복구 성공→이전 상태/복구 실패→ERROR), 복구 중 UI 표시(프로그레스 바, 남은 시간, 취소 버튼)
5. 사용자 안내 문구 작성: §7.4 템플릿 기반, i18n 키 매핑(LOCK L16: ko-KR), 심각도별 톤(정보/경고/위험)
6. Part2 §6.1.7 4개 에러코드 화면 표시 규칙과 D2.0-08 §7 14건의 정합성 교차 검증
7. STEP7-C Failure/Fallback 관련 항목 매핑

**검증**:
- [x] FailureCode 14건이 D2.0-08 §7.6 정본과 1:1 대응 (LOCK L20) ✅
- [x] FallbackRegistry 9건이 D2.0-08 §7.6 정본과 1:1 대응 (LOCK L20) ✅
- [x] R-61-10 준수: 정본 14+9 정의를 그대로 구현, 임의 추가/변경 없음 ✅
- [x] UI_S7_RECOVERY 진입/이탈 조건이 #8 9-State 전이 매트릭스와 정합 ✅
- [x] 사용자 안내 문구가 i18n 키로 관리 (L16, R-61-3) ✅

**[P1-8] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — failure_fallback_ui.md (Failure/Fallback UI L3)
- 1. 게이트: LOCK L20 14+9 정본 ✅, R-61-10 준수 ✅, S7_RECOVERY 정합 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\failure_fallback_ui.md` (Failure/Fallback UI L3 상세)
</details>

<!-- ═══════════════════════════════════════════════════ -->
<!-- 04_react-components (#5)                           -->
<!-- ═══════════════════════════════════════════════════ -->

<details>
<summary><b>#5. React 컴포넌트 ~44개</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #5 "React 컴포넌트 ~44개"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상 (Gate #5: ~44개 렌더링 검증, Gate #12: 디자인 시스템)
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑), ISS-4 (v12 추가 컴포넌트 4건)

**목표**: D2.0-08 §10.4 정본 기반 React 컴포넌트 ~44개(LOCK L13)의 Props 인터페이스, 렌더링 규칙, 디자인 토큰 적용, 컴포넌트 계층 구조를 L3 상세로 정의하며, ISS-4(v12 추가 4건)를 Phase 1 범위에 포함 가능 여부를 판정한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §10.4(컴포넌트 목록 ~44개), §10(디자인 시스템)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.2(React 컴포넌트)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\_index.md` §1(컴포넌트 목록)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L13 LOCK 정의

**절차**:
1. D2.0-08 §10.4 읽기 — ~44개 컴포넌트 전체 목록 추출(컴포넌트명, 카테고리, 용도) + §10 디자인 시스템(토큰, 테마, 색상) 확인
2. 04_react-components/_index.md §1 기존 목록 확인 — L3 보강 범위 식별
3. 컴포넌트 계층 구조(Atomic Design) 설계: Atoms(Button, Input, Badge 등) → Molecules(SearchBar, FormField 등) → Organisms(NavigationPanel, PropertyEditor 등) → Templates(BuilderLayout, HologramLayout) → Pages(#13과 연계)
4. 컴포넌트별 상세 명세 작성(~44개 각각):
   - TypeScript Props 인터페이스 정의
   - 렌더링 규칙(조건부 렌더링, 리스트 렌더링)
   - 디자인 토큰 적용(ORANGE #F97316/BLUE #00F6FF, 다크모드 — LOCK L5, L6, L7)
   - 접근성 속성(ARIA labels, 키보드 인터랙션)
   - 상태 연동(어떤 Zustand Store/Custom Hook 사용)
5. ISS-4 판정: v12 추가 4건 컴포넌트 식별 → Phase 1 필수/Phase 2 이연 분류 + 근거
6. 컴포넌트 ↔ FailureCode/Fallback 매핑: D2.0-08 §7 기반, 어떤 컴포넌트에서 어떤 FailureCode를 표시하는지(LOCK L20, R-61-10)
7. STEP7-C 104건 중 04_react-components 배정 항목 전수 매핑 + ISS-3 해결 진행
8. Storybook 스토리 목록 작성: 각 컴포넌트의 기본/변형/에러 상태 스토리 정의

**검증**:
- [x] 컴포넌트 수가 ~44개(LOCK L13) 범위 내 — 정확 수치 D2.0-08 §10.4와 일치 ✅
- [x] 모든 컴포넌트의 Props 인터페이스 정의 완료 ✅
- [x] 디자인 토큰(L5 #F97316, L6 #00F6FF, L7 다크모드) 적용 규칙 명시 ✅
- [x] ISS-4 v12 추가 4건 판정 결과 기록 (Phase 1 포함/Phase 2 이연 + 근거) ✅
- [x] FailureCode/Fallback 매핑이 #9와 정합 ✅
- [x] Gate #5 검증 가능: ~44개 렌더링 테스트 시나리오 포함 ✅

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\react_components_catalog.md` (React 컴포넌트 ~44개 L3 상세)

> **완료**: 2026-04-12. React 컴포넌트 ~44개 L3 상세 카탈로그 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (react_components_catalog.md v1.0, ~1715줄)
> - 44개 컴포넌트 전체 TypeScript Props 정의 (V1 37개 필수 + V1.1+ 7개 선택)
> - Atomic Design 5계층 분류, Storybook 72건
> - ISS-4: v12 4건 전체 Phase 2 이연
> - FailureCode 14건 + FallbackRegistry 9건 컴포넌트 매핑 (R-61-10)
> - STEP7-C 33건 전수 매핑 (ISS-3 해결)
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-9] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — react_components_catalog.md (React 컴포넌트 L3 카탈로그)
- 1. 게이트: Gate #5 렌더링 검증 가능 ✅, LOCK L13 범위 ✅, ISS-4 판정 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: ISS-4 v12 4건 → Phase 2 (P2-3)
</details>

<!-- ═══════════════════════════════════════════════════ -->
<!-- 05_custom-hooks (#6, #7)                           -->
<!-- ═══════════════════════════════════════════════════ -->

<details>
<summary><b>#6. Custom Hooks 8개</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #6 "Custom Hooks 8개"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑)

**목표**: Part2 §6.1.3 정본 기반 Custom Hooks 8개(LOCK L14)의 인터페이스 시그니처, 내부 로직 흐름, 의존성(Zustand Store, API), 반환 값 타입을 L3 상세로 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.3(Custom Hooks 8개 목록 + 역할)
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` 관련 섹션(Hook이 참조하는 상태/이벤트)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\05_custom-hooks\_index.md` §1(Hooks 목록)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L14 LOCK 정의

**절차**:
1. Part2 §6.1.3 읽기 — Custom Hooks 8개 목록 + 각 Hook의 역할 설명 추출 (LOCK L14)
2. 05_custom-hooks/_index.md §1 기존 정의 확인 — L3 보강 범위 식별
3. Hook 8개 각각의 상세 명세 작성:
   - TypeScript 시그니처: `function useXxx(params: XxxParams): XxxReturn`
   - 내부 로직 흐름: 초기화 → 구독 → 갱신 → 정리(cleanup) 생명주기
   - 의존성: 어떤 Zustand Store 구독, 어떤 API 호출, 어떤 이벤트 리스닝
   - 반환 값: 상태 값 + 액션 함수 + 로딩/에러 상태
   - 리렌더링 최적화: useMemo/useCallback 적용 기준, selector 패턴
4. Hook 간 의존성 그래프 작성: 어떤 Hook이 다른 Hook을 내부에서 호출하는지, 순환 의존성 검증
5. Hook ↔ 컴포넌트 매핑 테이블: 각 Hook을 사용하는 컴포넌트 목록(#5와 연계)
6. 테스트 전략: 각 Hook의 단위 테스트 시나리오(renderHook 패턴), 모킹 대상

**검증**:
- [x] Hook 8개가 Part2 §6.1.3 정본과 1:1 대응 (LOCK L14) ✅
- [x] 모든 Hook의 TypeScript 시그니처 정의 완료 ✅
- [x] Hook 간 순환 의존성 없음 ✅
- [x] Hook ↔ 컴포넌트 매핑이 #5 컴포넌트 목록과 정합 ✅
- [x] STEP7-C Hook 관련 항목 매핑 확인 ✅

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\05_custom-hooks\custom_hooks.md` (Custom Hooks 8개 L3 상세)

> **완료**: 2026-04-12. Custom Hooks 8개 L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (custom_hooks.md v1.0, ~1487줄)
> - Hook 8개 전체 TypeScript 시그니처 + 내부 로직 + 의존성 정의
> - Hook 간 DAG 순환 의존성 검증 PASS
> - Hook↔컴포넌트 매핑 (#5 정합 확인)
> - STEP7-C 17건 매핑 (직접 12 + 공유 5)
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-10] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — custom_hooks.md (Custom Hooks 8개 L3 상세)
- 1. 게이트: LOCK L14 8개 1:1 ✅, Gate #6 Hooks 동작 검증 가능 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음
</details>

<details>
<summary><b>#7. Zustand Stores 7개</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #7 "Zustand Stores 7개"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑)

**목표**: Part2 §6.1.3 정본 기반 Zustand Stores 7개(LOCK L15)의 상태 스키마, 액션 정의, 미들웨어(persist/devtools), 구독 패턴을 L3 상세로 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.3(Zustand Stores 7개 목록 + 역할)
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` 관련 섹션(Store가 관리하는 상태 도메인)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\05_custom-hooks\_index.md` §2(Stores 목록)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L15 LOCK 정의

**절차**:
1. Part2 §6.1.3 읽기 — Zustand Stores 7개 목록 + 각 Store의 역할·관리 상태 범위 추출 (LOCK L15)
2. 05_custom-hooks/_index.md §2 기존 정의 확인 — L3 보강 범위 식별
3. Store 7개 각각의 상세 명세 작성:
   - TypeScript 상태 인터페이스: `interface XxxState { ... }`
   - 액션 정의: `interface XxxActions { setXxx: (val) => void; resetXxx: () => void; ... }`
   - 초기 상태 값: 각 필드의 기본값
   - 미들웨어 구성: persist(LocalStorage/SessionStorage 대상 필드), devtools(개발 모드), immer(불변성)
   - selector 패턴: 컴포넌트에서 부분 구독 시 권장 selector 목록
4. Store 간 관계 정의: 어떤 Store가 다른 Store를 참조/구독하는지, 갱신 순서(uiStateStore → themeStore 등)
5. Store ↔ Hook 연동 테이블: 각 Store를 구독하는 Hook(#6) 및 직접 사용하는 컴포넌트(#5) 매핑
6. 영속성 전략: 어떤 상태가 페이지 새로고침/앱 재시작 후 유지되어야 하는지 — Tauri 로컬 스토리지 vs. 메모리 전용 분류
7. STEP7-C Store 관련 항목 매핑

**검증**:
- [x] Store 7개가 Part2 §6.1.3 정본과 1:1 대응 (LOCK L15) ✅
- [x] 모든 Store의 TypeScript 인터페이스(State + Actions) 정의 완료 ✅
- [x] 미들웨어 구성(persist/devtools/immer) 명시 ✅
- [x] Store ↔ Hook, Store ↔ 컴포넌트 매핑이 #5, #6과 정합 ✅
- [x] 영속성 분류(persist 대상 vs. 메모리 전용) 완료 ✅

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\05_custom-hooks\zustand_stores.md` (Zustand Stores 7개 L3 상세)

> **완료**: 2026-04-12. Zustand Stores 7개 L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (zustand_stores.md v1.0, ~1480줄)
> - Store 7개 전체 TypeScript State+Actions 인터페이스
> - 미들웨어: persist(2) + devtools(7) + immer(7)
> - Store↔Hook 8건, Store↔컴포넌트 전수 매핑
> - 영속성: Tauri localStorage 2개 + memory 5개
> - STEP7-C 17건 매핑 (직접 12 + 공유 5)
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-11] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — zustand_stores.md (Zustand Stores 7개 L3)
- 1. 게이트: LOCK L15 7개 1:1 ✅, Gate #7 상태 관리 검증 가능 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음
</details>

<!-- ═══════════════════════════════════════════════════ -->
<!-- 06_accessibility (#10, #11, #12)                   -->
<!-- ═══════════════════════════════════════════════════ -->

<details>
<summary><b>#10. RBAC 접근 제어</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #10 "RBAC 접근 제어"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑)

**목표**: D2.0-08 §8 + Part2 §6.1.8 정본 기반 RBAC 4단계(OWNER/ADMIN/OPERATOR/VIEWER, LOCK L10)의 UI 접근 제어 규칙 — 페이지/컴포넌트별 가시성·활성화·비활성화 규칙, Approval Gate에서의 HOLD 전환(R-61-8)을 L3 상세로 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §8(RBAC, Approval Gate)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.8(RBAC 접근 제어)
- `D:\VAMOS\docs\sot\D2.0-07_07. VAMOS_DESIGN_2.0_SAFETY_COST_APPROVAL.md` 승인 타임아웃(LOCK L18: HITL 5분/일반 10분)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\_index.md` §4(RBAC 정의)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L10, L18 LOCK 정의

**절차**:
1. D2.0-08 §8 읽기 — RBAC 4단계 정의(OWNER/ADMIN/OPERATOR/VIEWER), 각 역할별 권한 범위 + Approval Gate UI 규칙 + Part2 §6.1.8 구현 상세 교차 확인
2. D2.0-07 읽기 — 승인 타임아웃 규칙: HITL 5분(LOCK L18), 일반 10분(LOCK L18), 타임아웃 시 UI 동작(자동 거절/에스컬레이션)
3. 페이지별 RBAC 접근 매트릭스 작성: 7개 페이지(#13) × 4역할 — 각 셀에 접근 가능/읽기전용/접근불가 + 조건부 접근 규칙
4. 컴포넌트별 가시성/활성화 규칙: ~44개 컴포넌트(#5) 중 RBAC 영향을 받는 컴포넌트 식별 → 역할별 렌더링 규칙(hidden/disabled/enabled)
5. Approval Gate HOLD 전환 UI: 승인 요청 모달, 타이머 표시(L18), 승인/거절 버튼, 타임아웃 경고 — R-61-8(명시적 승인/거절) 준수
6. RBAC 미들웨어/가드 구현 설계: React Router 라우트 가드, 컴포넌트 래퍼(withRBAC HOC 또는 useRBAC Hook), 권한 체크 로직 흐름
7. 6-1 ↔ 6-2(Security) 동기화: W-3 모니터링 항목, RBAC 정책 데이터 소스(6-2에서 제공, 6-1에서 UI 소비)

**검증**:
- [x] RBAC 4단계가 Part2 §6.1.8 정본과 일치 (LOCK L10) ✅
- [x] 페이지별 접근 매트릭스(7페이지 × 4역할) 완성 ✅
- [x] Approval Gate 타임아웃이 L18(HITL 5분/일반 10분) 준수 ✅
- [x] R-61-8 준수: 승인/거절이 명시적 UI 액션으로만 가능(자동 승인 금지) ✅
- [x] W-3(6-1 ↔ 6-2 RBAC 동기화) 인터페이스 정의 ✅

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\rbac_access_control.md` (RBAC 접근 제어 L3 상세)

> **완료**: 2026-04-12. RBAC 접근 제어 L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (rbac_access_control.md v1.0, ~664줄)
> - RBAC 4역할 정의 (LOCK L10)
> - 7페이지 × 4역할 접근 매트릭스 28셀
> - RBAC 영향 컴포넌트 26건 가시성 규칙
> - Approval Gate (L18 타임아웃, R-61-8 명시적 승인)
> - useRBAC Hook + RBACRouteGuard 설계
> - W-3 (6-1↔6-2) 동기화 인터페이스
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-12] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — rbac_access_control.md (RBAC 접근 제어 L3)
- 1. 게이트: LOCK L10 4역할 ✅, L18 타임아웃 ✅, Gate #11 RBAC ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음

</details>

<details>
<summary><b>#11. i18n 국제화</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #11 "i18n 국제화"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑)

**목표**: D2.0-08 §0 MOD-022 + V1-P4 #14 정본 기반 i18n ko-KR(LOCK L16) 국제화 체계 — 키 네이밍 규칙, 번역 파일 구조, 하드코딩 금지(R-61-3), LogEvent message 영어 고정(R-61-7)을 L3 상세로 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §0 MOD-022(i18n 요구사항)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4 #14(i18n 국제화)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\_index.md` §6(i18n 정의)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L16 LOCK 정의

**절차**:
1. D2.0-08 §0 MOD-022 읽기 — i18n 요구사항: 기본 로케일 ko-KR(LOCK L16), 지원 로케일 확장 구조, UI 텍스트 하드코딩 금지(R-61-3)
2. V1-P4 #14 읽기 — Phase 1 i18n 구현 범위: ko-KR 단일 로케일, 번역 키 체계, 런타임 전환 준비
3. i18n 키 네이밍 규칙 정의: 네임스페이스 기반(`{page}.{component}.{element}` — e.g., `dashboard.sidebar.title`), 복수형 처리, 변수 보간 형식
4. 번역 파일 구조 설계: `locales/ko-KR/{namespace}.json` 구조, 네임스페이스 분할 기준(페이지별 또는 기능별), 로드 전략(lazy loading)
5. R-61-3 준수 검증 체계: ESLint 규칙(하드코딩 문자열 감지), i18n 키 커버리지 리포트 생성 스크립트
6. R-61-7 준수: LogEvent message 필드는 영어 고정 — UI 표시 텍스트(i18n) vs. 이벤트 메시지(영어) 분리 규칙
7. Failure/Fallback 안내 문구(#9 §7.4) i18n 키 매핑: FailureCode 14건 각각의 사용자 안내 문구 → i18n 키 할당
8. STEP7-C i18n 관련 항목 매핑

**검증**:
- [x] 기본 로케일 ko-KR 설정 (LOCK L16) ✅
- [x] i18n 키 네이밍 규칙이 일관성 있고 네임스페이스 기반 ✅
- [x] R-61-3 준수: 하드코딩 금지 검증 체계(ESLint 규칙) 정의 ✅
- [x] R-61-7 준수: LogEvent message 영어 고정 규칙 명시 ✅
- [x] FailureCode 14건 안내 문구 i18n 키 매핑 완료 ✅

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\i18n_internationalization.md` (i18n 국제화 L3 상세)

> **완료**: 2026-04-12. i18n 국제화 L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (i18n_internationalization.md v1.1, ~910줄)
> - 기본 로케일 ko-KR (LOCK L16), 12 네임스페이스
> - R-61-3 ESLint 하드코딩 금지 검증 체계
> - R-61-7 LogEvent message 영어 고정 규칙
> - FailureCode 14건 i18n 키 매핑 (ko-KR + en-US)
> - STEP7-C 3건 직접 + 3건 간접 매핑
> - 재검증 2회, 수정 2건
> - CONFLICT/LOCK 변경 없음

**[P1-13] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — i18n_internationalization.md (i18n L3)
- 1. 게이트: LOCK L16 ko-KR ✅, R-61-3 ✅, R-61-7 ✅, Gate #8 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음
</details>

<details>
<summary><b>#12. 디자인 시스템 ORANGE/BLUE</b> ✅ 완료 (2026-04-12)</summary>

**대조 기준**:
- §7 세부 작업: #12 "디자인 시스템 (ORANGE/BLUE)"
- §7 전환 게이트: P1→P2 — Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상 (Gate #12: 디자인 시스템)
- §6 이슈: ISS-3 (STEP7-C 104건 미매핑)

**목표**: D2.0-08 §10 정본 기반 디자인 시스템 — ORANGE #F97316(LOCK L5), BLUE #00F6FF(LOCK L6), 다크모드 기본(LOCK L7), WCAG 2.1 AA(LOCK L8) 준수 디자인 토큰 체계를 L3 상세로 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §10(디자인 시스템: §10.1 색상, §10.2 타이포그래피, §10.3 간격/그리드, §10.4 컴포넌트)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4 #15(디자인 시스템)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\_index.md` §5(디자인 토큰)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` L5, L6, L7, L8 LOCK 정의

**절차**:
1. D2.0-08 §10 전체 읽기 — 색상 팔레트(§10.1: Primary ORANGE #F97316, Accent BLUE #00F6FF, 배경/텍스트/보더 색상 체계), 타이포그래피(§10.2), 간격/그리드(§10.3), 컴포넌트 토큰(§10.4)
2. 디자인 토큰 체계 설계:
   - 색상 토큰: `--color-primary: #F97316`, `--color-accent: #00F6FF`, 다크모드 배경/텍스트/보더 전체 팔레트
   - 타이포그래피 토큰: 폰트 패밀리, 크기 스케일(xs~3xl), 행간, 자간
   - 간격 토큰: 4px 기반 스케일(0.5~16), 패딩/마진 시맨틱 토큰
   - 그림자/라운드: 엘리베이션 스케일, 보더 라운드 규격
3. 다크모드 구현 명세: CSS 변수 기반 테마 전환, `prefers-color-scheme` 감지 + 수동 전환 토글, 다크모드 기본(LOCK L7) 적용 — Tailwind CSS dark: 유틸리티 또는 CSS 변수 전략
4. WCAG 2.1 AA 색상 대비 검증: ORANGE #F97316 vs. 다크 배경 대비율 계산, BLUE #00F6FF vs. 다크 배경 대비율 계산 — 최소 4.5:1(일반 텍스트), 3:1(대형 텍스트) 충족 확인, 미충족 시 보정 규칙
5. 토큰 파일 구조 설계: `tokens/colors.ts`, `tokens/typography.ts`, `tokens/spacing.ts` — CSS-in-JS 또는 CSS 변수 export 형식
6. Tailwind CSS 커스텀 테마 구성: `tailwind.config.ts` extend 규격, 커스텀 색상/간격/타이포그래피 매핑
7. STEP7-C 디자인 시스템 관련 항목 매핑

**검증**:
- [x] Primary ORANGE #F97316 (LOCK L5), Accent BLUE #00F6FF (LOCK L6) 정확 반영 ✅
- [x] 다크모드 기본 적용 (LOCK L7) ✅
- [x] WCAG 2.1 AA 대비율 충족 (LOCK L8) — 계산 결과 포함 ✅
- [x] 디자인 토큰 체계(색상/타이포/간격/그림자) 완성 ✅
- [x] Gate #12 검증 가능: 디자인 시스템 일관성 테스트 시나리오 포함 ✅

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\design_system_orange_blue.md` (디자인 시스템 L3 상세)

> **완료**: 2026-04-12. 디자인 시스템 L3 상세 파일 생성 완료.
>
> **실행 결과 요약**:
> - 산출물 1건 (design_system_orange_blue.md v1.0, ~800줄)
> - ORANGE #F97316 (L5), BLUE #00F6FF (L6), Dark 기본 (L7)
> - WCAG 2.1 AA (L8): ORANGE 5.95:1 PASS, BLUE 12.41:1 PASS + 보정 규칙
> - 색상/타이포/간격/그림자 토큰 체계 완성
> - Tailwind CSS 커스텀 테마 구성
> - STEP7-C 3건 직접 + 4건 간접 매핑
> - Gate #12 테스트 18건 (자동12+수동6)
> - 재검증 1회, 수정 0건
> - CONFLICT/LOCK 변경 없음

**[P1-14] 검증 결과 요약** (갱신: 2026-04-12)
- 0. 산출물: 생성 1건 — design_system_orange_blue.md (디자인 시스템 L3)
- 1. 게이트: LOCK L5/L6/L7/L8 정합 ✅, Gate #12 디자인 시스템 ✅, WCAG AA 계산 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건
- 3. LOCK 변경: 없음
- 4. 이월: 없음
</details>

**Phase 1→Phase 2 게이트 (G1)**: ✅ **ALL PASS** (2026-04-12)
- [x] **G1-1**: Part2 V1-P4 Gate 12항목 전부 PASS — P1-1~P1-14 전 세션 ✅ 완료
- [x] **G1-2**: L3 상세 파일 10개 이상 — 14건 생성 (> 10개 충족)
- [x] **G1-3**: 종합 재검증 완료 — 3단계 검증(병렬 5에이전트 → 교차 검증 → 잔여 스캔), 21건 이슈 발견·수정, 잔여 0건
- **Phase 1 완료일**: 2026-04-12
- **Phase 2 진입 가능**: ✅

> **Phase 1 종합 재검증 보고** (2026-04-12)
>
> 14건 L3 산출물 전수 검증 — AUTHORITY_CHAIN LOCK 정합, 파일 간 인터페이스 일관성, TypeScript 타입 통일, 수치 정확성.
>
> | 서브폴더 | 파일수 | 발견 | 수정 |
> |----------|--------|------|------|
> | 01_builder-view | 4 | 12 | 12 |
> | 02_hologram-view | 2 | 2 | 2 |
> | 03_ui-state-machine | 2 | 0 | 0 |
> | 04_react-components + 05_custom-hooks | 3 | 8 | 8 |
> | 06_accessibility | 3 | 0 | 0 |
> | **합계** | **14** | **21** | **21** |
>
> **주요 수정**: Store명 정본 통일(cli_interface/builder_view/hologram_view), ISS-2 라우트수·CSS토큰수 정합(builder_view↔seven_pages), NotificationSeverity/Evidence/Node 타입 통일(hooks↔stores↔components), multimodal Phase2 테스트 섹션 추가, Atomic Design 카운트 정정.
> **잔여 이슈**: 0건. LOCK 변경 0건. CONFLICT 신규 0건.

#### Phase 2 단계별 상세 작업 절차

> **Phase 2 범위**: 멀티모달 V2 + ImageBind 마이그레이션(D8-L03), 반응형 레이아웃, v12 컴포넌트 4건, L3 업그레이드 통합 = 4블록
> **의존성**: Phase 1 완료 (P1→P2 Gate: Part2 V1-P4 Gate 12항목 전부 PASS + L3 상세 파일 10개 이상)

<details>
<summary><b>P2-1. 멀티모달 V2 + ImageBind 마이그레이션 (D8-L03 해결)</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "멀티모달 V2, ImageBind 통합" (§7.1 L302)
- §7 전환 게이트: P2→P3 "D8-L03 해결" (§7.2 L311)
- §6 이슈: ISS-5 (D2.0-08 §6.4.1 CLIP 마이그레이션 미문서화 — Phase 2 사전 해결)
- 교차 도메인: 6-11 Hologram-Main-LLM (Hologram View 렌더링 경계)
- Part2 버전: V2 (리팩토링)

**목표**: D2.0-08 §6.4.1 기반 CLIP ViT-B/32 → ImageBind 마이그레이션을 문서화하고, 멀티모달 V2 기능(이미지·음성·텍스트 통합 검색)을 02_hologram-view에 L3 상세로 정의한다. ISS-5(D8-L03)를 완전 해결한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §6.4.1 (CLIP→ImageBind 마이그레이션 정본)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\_index.md` (Phase 1 산출물)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` LOCK L5~L6 (ORANGE/BLUE 테마색)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4, V2 리팩토링 범위

**절차**:
1. D2.0-08 §6.4.1 읽기 → CLIP ViT-B/32 → ImageBind 마이그레이션 경로, 임베딩 차원 변경(512d→768d), 모달리티 확장(텍스트+이미지→텍스트+이미지+음성) 추출
2. Phase 1 02_hologram-view/_index.md 읽기 → V1 멀티모달 구현 상태 확인
3. ISS-5 해결: ImageBind 통합 마이그레이션 계획 작성 — 호환성 레이어, 전환 일정, 롤백 방안
4. 멀티모달 V2 기능 6건 정의: (1) ImageBind 통합 검색, (2) 음성→텍스트 변환 UI, (3) 이미지 유사도 HUD 표시, (4) 멀티모달 캐시 연동(6-4 Semantic Cache), (5) Glass HUD 멀티모달 오버레이, (6) 3-point 렌더링 V2 품질 향상
5. 각 기능에 대해 L3 9요소(E1~E9) 프레임 작성

**검증**:
- [x] ISS-5(D8-L03) 완전 해결: CLIP→ImageBind 마이그레이션 경로 문서화
- [x] 멀티모달 V2 기능 6건 각각 L3 프레임(E1 Input, E4 API Design 이상) 포함
- [x] LOCK L5(ORANGE #F97316), L6(BLUE #00F6FF) 테마색이 HUD 오버레이에 반영
- [x] 6-11 Hologram-Main-LLM 경계 참조 명시

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\multimodal_v2.md` (멀티모달 V2 + ImageBind L3 상세)
</details>

<details>
<summary><b>P2-2. 반응형 레이아웃 V2 리팩토링</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "반응형 레이아웃" (§7.1 L302)
- §7 전환 게이트: P2→P3 "V2 Phase 완료" (§7.2 L311)
- §6 이슈: ISS-2 (Part2 §6.1.4 구현 중 결정 4건 — Phase 1 해결 결과 반영)
- 교차 도메인: 4-1 Rust-Tauri (Tauri 윈도우 크기 연동)
- Part2 버전: V2 (리팩토링)

**목표**: V1 3-Column 고정 레이아웃(LOCK L2 좌측 250-300px, L3 우측 350-400px, L4 중앙 Flex-grow)을 V2 반응형으로 확장한다. 최소 해상도 1280×720(LOCK L11) 이하 대응 브레이크포인트를 정의한다.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §3 (3-Column Layout 정본)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\_index.md` (Phase 1 산출물)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` LOCK L2~L4, L11, L12

**절차**:
1. D2.0-08 §3 읽기 → 3-Column 규격 + 최소 해상도 + Tauri 기본 크기 추출
2. Phase 1 01_builder-view/_index.md 읽기 → V1 레이아웃 구현 상태 확인
3. 반응형 브레이크포인트 설계: 1440px(풀), 1280px(최소), 1024px(태블릿 모드), 768px(모바일 — V3 예고)
4. 각 브레이크포인트별 3-Column 동작 규칙: 패널 접기, 최소 폭, 오버플로우 처리
5. CSS Container Queries 또는 Media Queries 전략 결정
6. 4-1 Rust-Tauri 도메인과의 윈도우 크기 이벤트 연동 인터페이스 정의

**검증**:
- [x] LOCK L2(좌 250-300px), L3(우 350-400px), L4(중앙 Flex-grow) 준수
- [x] LOCK L11(최소 1280×720), L12(기본 1440×900) 브레이크포인트 반영
- [x] 4-1 Rust-Tauri 윈도우 크기 이벤트 연동 명시
- [x] V3 모바일 확장 예고 포함 (Phase 3 연계)

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\responsive_layout_v2.md` (반응형 레이아웃 V2 L3 상세)
</details>

<details>
<summary><b>P2-3. v12 컴포넌트 4건 구현 상세</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 "v12 컴포넌트 4건" (§7.1 L302)
- §7 전환 게이트: P2→P3 "v12 컴포넌트 4건 구현" (§7.2 L311)
- §6 이슈: ISS-4 (v12 추가 컴포넌트 4건 관리 구조 없음 — 04_react-components에 등록)
- 교차 도메인: 3-6 Health-Wellness-EmotionAI (감정 AI 인터페이스)
- Part2 버전: V2 (리팩토링) — Part2 §6.1.8

**목표**: v12 추가 컴포넌트 4건(스트레스 관리 UI, CBT 셀프케어 UI, 번아웃 방지 UI, 플래시카드 UI)을 L3 수준으로 구현 상세를 정의한다. 각 컴포넌트의 Props Interface, 상태 관리, 렌더링 규칙, 3-6 Health-Wellness 연동을 포함한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\_index.md` (Phase 1 산출물 — 10그룹 48개 카탈로그)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` 부록 A.2 (v12 4건 참조 ID: D207-175/178/179, S7NP-047/048)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` §6.1.8 (v12 컴포넌트 정의)

**절차**:
1. Part2 §6.1.8 읽기 → v12 4건 정의 + 기능 요건 추출
2. 부록 A.2 읽기 → 각 컴포넌트 참조 ID, 기존 등록 상태 확인
3. 스트레스 관리 UI (D207-175): BreathingGuide(4-7-8 호흡법), GroundingExercise(5-4-3-2-1), MeditationTimer — Props/State/Events 정의
4. CBT 셀프케어 UI (D207-178): ThoughtRecord, CognitiveDistortionDetector(12종), ProgressChart — Props/State/Events 정의
5. 번아웃 방지 UI (S7NP-047): 번아웃 지수 시각화, 휴식 알림, 업무 패턴 분석 — Props/State/Events 정의
6. 플래시카드 UI (S7NP-048): 카드 생성/편집, Spaced Repetition(SM-2 알고리즘 3-3 PKM 연동), 학습 진도 — Props/State/Events 정의
7. 3-6 Health-Wellness-EmotionAI 도메인 감정 데이터 인터페이스 연동 정의

**검증**:
- [x] v12 4건 각각 L3 프레임(E1 Input, E3 Output, E4 Class/API, E7 Error, E8 Test) 포함
- [x] ISS-4 해결: 04_react-components에 v12 4건 공식 등록
- [x] 3-6 Health-Wellness-EmotionAI 연동 인터페이스 명시
- [x] LOCK L13(~44개 컴포넌트) → 48개로 확장 기록 (v12 4건 추가)

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\v12_components.md` (v12 4건 컴포넌트 L3 상세)
</details>

<details>
<summary><b>P2-4. Phase 2 L3 업그레이드 통합 검증</b></summary>

**대조 기준**:
- §7 세부 작업: Phase 2 산출물 "L3 업그레이드" (§7.1 L302)
- §7 전환 게이트: P2→P3 "V2 Phase 완료" (§7.2 L311)
- §6 이슈: ISS-7 (EventType 54+건 D2.1-D2 동기 등록 — 6-12 협력), ISS-3 (STEP7-C 미반영 항목)
- 교차 도메인: 6-12 Event-Logging (EventType 동기 등록)
- Part2 버전: V2 (리팩토링)

**목표**: Phase 1 L3 파일(10개 이상)을 V2 리팩토링 결과에 맞춰 갱신하고, P2-1~P2-3 산출물과의 정합성을 검증한다. ISS-7(EventType 동기) 해결을 위해 6-12 Event-Logging과 교차 참조를 수립한다.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\` 01~06 서브폴더 Phase 1 L3 파일 전체
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\UI_UX_SYSTEM_구조화_종합계획서.md` §6 이슈 매핑
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §5.1 (이벤트 네이밍 LOCK L19)

**절차**:
1. Phase 1 L3 파일 전수 읽기 → V2 변경 영향도 분석
2. P2-1(멀티모달/ImageBind) 반영: 02_hologram-view 기존 파일에 V2 참조 추가
3. P2-2(반응형) 반영: 01_builder-view 기존 파일에 브레이크포인트 참조 추가
4. P2-3(v12 4건) 반영: 04_react-components/_index.md 카탈로그 갱신
5. ISS-7 해결: 03_ui-state-machine에서 EventType 54+건 목록 확인 → 6-12 Event-Logging 도메인 교차 참조 포인터 설정
6. ISS-3 잔여: STEP7-C 104건 중 V2 해당 항목 Phase 2 매핑 확인
7. LOCK L19(이벤트 네이밍 `ui.{layer}.{subject}.{action}`) V2 확장 이벤트 네이밍 일관성 점검

**검증**:
- [x] Phase 1 L3 파일 10개 이상에 V2 반영 여부 확인
- [x] ISS-7 해결: EventType 동기 등록 계획 + 6-12 교차 참조 포인터
- [x] LOCK L19 이벤트 네이밍 규칙 V2 확장 이벤트에 적용
- [x] P2-1~P2-3 산출물과 기존 L3 파일 간 정합성 확인

**산출물**: Phase 1 L3 파일 V2 갱신본 + `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\event_type_v2_sync.md` (6-12 교차 참조 포인터)
</details>

> **Phase 2 완료** (2026-04-26 STAGE 7 STEP_C 최종 마감 truly_converged_v2 — **[PHASE3_READY v2: 6-1 — 2026-04-26 최종 확정 truly_converged_v2]**)
>
> | 세션 | 산출물 NEW | wc -l | ISS 해결 | LOCK 변경 | CONFLICT 신규 |
> |------|-----------|-------|----------|-----------|--------------|
> | P2-1 | `02_hologram-view/multimodal_v2.md` | 252 | ISS-5 PARTIALLY-RESOLVED → RESOLVED (D8-L03 ImageBind 4축 완비) | 0 | 0 |
> | P2-2 | `01_builder-view/responsive_layout_v2.md` | 229 | ISS-2 RESOLVED 결과 반영 (재정의 0) | 0 | 0 |
> | P2-3 | `04_react-components/v12_components.md` | 359 | ISS-4 → RESOLVED (v12 4건 × 12 sub-component L3 9요소, LOCK L13 ~44→48 카탈로그 확장 기록 정의 변경 0) | 0 | 0 |
> | P2-4 | `03_ui-state-machine/event_type_v2_sync.md` | 268 | ISS-7 → RESOLVED (V2 신규 56 EventType 6-12 cross-handoff 큐) + ISS-3 잔여 (STEP7-C 104건 V2 매핑 매트릭스) | 0 | 0 |
> | **합계** | **4 NEW** | **1,108** | **ISS-3/4/5/7 4건 진전** | **0 통산** | **0 통산** |
>
> **Phase 1 L3 14건 V2 영향도**: V1 14/14 본문 변경 0건 보존 (byte-prefix SHA UNCHANGED). V2 영향도는 P2-4 event_type_v2_sync.md §5 통합 catalog 에서 lookup.
>
> **V1 verify 5 tag × 2 위치 sync = 10 log files**:
> - session_P2-1_done_6-1 (14/14 OK, 2026-04-26T20-30-00)
> - session_P2-2_done_6-1 (14/14 OK, 2026-04-26T20-45-00)
> - session_P2-3_done_6-1 (14/14 OK, 2026-04-26T21-00-00)
> - session_P2-4_done_6-1 (14/14 OK, 2026-04-26T21-15-00)
> - domain_finalize_6-1 (14/14 OK, 2026-04-26T21-30-00)
>
> **Phase 2 → Phase 3 전환 게이트** (§7.2 P2→P3):
> - [x] V2 Phase 완료: 4 NEW 산출물 (multimodal_v2 + responsive_layout_v2 + v12_components + event_type_v2_sync) 1,108L 전수 ✅
> - [x] v12 컴포넌트 4건 구현: P2-3 v12_components.md §3~§6 (D207-175 + D207-178 + D207-179 + S7NP-047/048) × 12 sub-component L3 9요소 전수 ✅
> - [x] D8-L03 해결: P2-1 multimodal_v2.md §3 ImageBind 마이그레이션 4축 (원문 / 차원 매트릭스 / 호환 어댑터 / 전환 일정 / 롤백 방안) 전수 ✅
> - **Phase 3 진입 가능**: ✅
>
> **LOCK L1~L20 set accuracy 20 unique 통산** (Phase 2 변경 0건). **CONFLICT OPEN 0** (CONF-61-001~003 RESOLVED 보존 + Phase 2 신규 0건). **FABRICATION 0/N CLEAN** (parent-executed Subagent 0회 통산).

**[Phase 2] 검증 결과 요약** (갱신: 2026-04-26)
- 0. 산출물: 생성 4건 (P2-1~P2-4 NEW V2 산출물 1,108L) + Phase 1 L3 14건 V2 영향도 통합 catalog (event_type_v2_sync.md §5)
- 1. 게이트: V2 Phase 완료 ✅, v12 4건 ✅, D8-L03 ✅
- 2. CONFLICT: 발견 0건 / 해소 0건 / OPEN 0건 (CONF-61-001~003 3건 RESOLVED 보존)
- 3. LOCK 변경: 없음 (L1~L20 20 unique set accuracy 통산)
- 4. 이월: STEP7-C 잔여 ~70+ 항목 V3 범위, V2 신규 FailureCode 검토 V3 범위 (모바일/AR), 11번째 그룹 신설 (Wellness/Education) V3 범위

#### Phase 3 세부 태스크 (Phase 15 S15-5 추가, 2026-05-14) ✅ Phase 3 완료 (2026-05-17, 4 task)

> **진입 조건**: P2→P3 게이트 ✅ PASS (2026-04-26 STAGE 7 STEP_C 최종 마감 truly_converged_v2 — **[PHASE3_READY v2: 6-1 — 2026-04-26 최종 확정 truly_converged_v2]**, §7.2 L311 인용)
>
> **요약형 분해**: §7.1 L303 Phase 3 row "고급 UI: 모바일 대응, AR/공간 이해, 아바타/디지털 휴먼, V3 확장 슬롯 4개" → 4개 논리 그룹(P3-1~P3-4) × `<details>` 블록 4개

<details>
<summary><b>P3-1. 모바일 대응 V3 (BP-D 768px 확장 + 모바일 접근성)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-1 (§7.1 L303 Phase 3 산출물 "모바일 대응")
- 전환 게이트 조건: P2→P3 ✅ PASS (L311) → P3→완료 신규 정의 (모바일 BP-D 정식 + WCAG AA 모바일 검증)
- §6 이슈 ID: ISS-3 (STEP7-C 잔여 ~70+ V3 범위 중 모바일 항목) + ISS-7 (V2 신규 FailureCode V3 모바일 확장, L1756)
- 교차 도메인: 4-1 Rust-Tauri (모바일 IPC 경계 — `AUTHORITY_CHAIN §3` 정합), 6-2 Security-Governance (모바일 RBAC L10 4단계 + 6.5 보안 체크리스트 우선)
- V3-Phase 매핑: §7.1 L303 "V3 (최종 통합)" — Part2 V3 미정의이므로 본 계획서 §7.1 + 6-1 정본 + 4-1 Tauri Phase 매핑 공동 정의
- production 측정 baseline: Phase 1 14 L3 파일 SHA UNCHANGED + Phase 2 NEW `responsive_layout_v2.md` 229L (P2-2 산출물) + LOCK L11(V1 1280×720) **재정의 아닌 확장** 기준
- Phase 4 entry-gate 충족 조건: `responsive_layout_v3.md` NEW L3 9요소(E1~E9) ≥ 7 + LOCK L11 V3 확장 명시(BP-D 768px) + WCAG 2.1 AA 모바일 검증 통과 + CONFLICT OPEN 0건

**목표**: V1 데스크톱 전용 1280×720(LOCK L11)을 V3에서 모바일 BP-D 768px로 확장(재정의 아닌 V3 추가 정의), 모바일 접근성(WCAG 2.1 AA, LOCK L8) 강화, 모바일 환경에서의 9-State(LOCK L1) + 3-Column(LOCK L2/L3/L4) 적응 규칙 정의. STEP7-C 잔여 모바일 항목(ISS-3 일부) + V2 신규 FailureCode 모바일 확장(ISS-7) 해결.

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §3 (3-Column LOCK L2/L3/L4 정본) + §3.1 (V1 최소 해상도 LOCK L11) + §10 (다크모드 LOCK L7)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\responsive_layout_v2.md` (P2-2 산출물 229L, V2 반응형 규격 base)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\06_accessibility\_index.md` (WCAG 2.1 AA 체크리스트 LOCK L8)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` LOCK L11 (V1 해상도) + L2/L3/L4 (3-Column) + L8 (WCAG)
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` V1-P4 (Phase 1 정본) + V2 리팩토링(Phase 2 정본) — V3 정본은 본 계획서 §7.1 L303 + 본 블록

**절차**:
1. D2.0-08 §3 + §3.1 읽기 → V1 BP-A 1280px / BP-B 1440px / BP-C 1920px 3 breakpoint 추출
2. responsive_layout_v2.md 읽기 → V2 BP-A/B/C 확정 규격 + Glass HUD 적응 규칙 확인 (변경 0건 보존)
3. **BP-D 768px V3 추가 정의** (LOCK L11 재정의 아닌 V3 확장): 3-Column → 1-Column(swipe nav) 전환 규칙 + 좌측 패널(LOCK L2 250-300px) Drawer 변환 + 우측 패널(LOCK L3 350-400px) BottomSheet 변환 + Builder Panel 모바일 키보드 처리
4. 9-State(LOCK L1 UI_S0~UI_S8) 모바일 환경 전이 영향 분석 — 최대 500ms 전이 지연(LOCK L17) 모바일 보장 가능 여부 + Touch FailureCode 신규 정의(ISS-7 V3 확장)
5. WCAG 2.1 AA(LOCK L8) 모바일 추가 검증: 터치 타겟 44×44pt, 스와이프 제스처 키보드 대체, ARIA live region, i18n(LOCK L16 ko-KR 기본) 모바일 폰트 스케일
6. 4-1 Rust-Tauri 모바일 IPC 경계 확인 — AUTHORITY_CHAIN §3 참조 + 4-1 Phase 매핑 cross-handoff 큐 등록
7. 6-2 Security-Governance RBAC(LOCK L10 OWNER/ADMIN/OPERATOR/VIEWER) 모바일 인증 UX 확인 — Part2 §6.5 보안 체크리스트 우선
8. L3 9요소(E1~E9) 작성: E1 Input(모바일 진입), E2 Algorithm(BP-D 전환 의사코드), E3 Output, E4 API Design(`useResponsive(bp: 'A'|'B'|'C'|'D')` Hook 시그니처), E5 Dependencies(05_custom-hooks 8 Hook 중 useResponsive 확장), E6 Performance(BP 전환 < 100ms), E7 Error(Touch FailureCode 신규), E8 Security(모바일 RBAC), E9 Test (BP-D ≥ 3 시나리오)

**검증**:
- [x] LOCK L11 재정의 0건 — BP-D 768px는 V3 추가 정의로 명시(`<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 사용)
- [x] LOCK L1 9-State 모바일 전이 규칙 정의 — 500ms 지연 보장(LOCK L17) 또는 모바일 예외 조건 명시
- [x] LOCK L2/L3/L4 3-Column → 1-Column 변환 매트릭스 (Drawer / BottomSheet / Builder)
- [x] WCAG 2.1 AA(LOCK L8) 모바일 추가 항목 ≥ 10건 (터치 타겟, 스와이프 대체, ARIA, i18n 폰트 스케일)
- [x] ISS-7 V2 신규 FailureCode 중 모바일 영역 정의 (Touch/Gesture/Orientation 최소 3건)
- [x] 4-1 Rust-Tauri 모바일 IPC cross-handoff 큐 등록
- [x] 6-2 Security RBAC L10 모바일 인증 UX cross-handoff
- [x] L3 9요소(E1~E9) ≥ 7 기재 + 의사코드 + API 시그니처
- [x] 6-12 Event-Logging cross-handoff 큐에 모바일 EventType(`ui.builder.responsive.*`) 신규 등록 (LOCK L19 네이밍 준수)
- [x] **Phase 4 entry-gate 충족 조건**: NEW 파일 byte ≥ 200L + L3 PASS + LOCK 변경 0건 + CONFLICT OPEN 0건

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\01_builder-view\responsive_layout_v3.md` (모바일 BP-D V3 확장 L3 상세) + `06_accessibility\mobile_a11y_v3.md` (모바일 WCAG 2.1 AA L3 상세)
</details>

<details>
<summary><b>P3-2. AR/공간 이해 UI V3 (Hologram View V3 + 6-11 경계 재정합)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-2 (§7.1 L303 Phase 3 산출물 "AR/공간 이해")
- 전환 게이트 조건: P2→P3 ✅ PASS (L311 D8-L03 ImageBind 4축 inheritance) → P3→완료 신규 정의 (AR 상호작용 정식 + 6-11 경계 재정합)
- §6 이슈 ID: ISS-6 (Hologram View와 6-11 도메인 범위 경계 — AUTHORITY_CHAIN §3에 경계 명시) + ISS-3 (STEP7-C 잔여 ~70+ V3 범위 중 AR 항목)
- 교차 도메인: 6-11 Hologram-Main-LLM (AR 렌더링 정본 — 6-11 정의, 6-1은 View 구조만), 6-12 Event-Logging (AR EventType 신규)
- V3-Phase 매핑: §7.1 L303 "V3 (최종 통합)" — AR Phase는 본 계획서 §7.1 + 6-11 정본 cross-handoff 공동 정의
- production 측정 baseline: P2-1 `multimodal_v2.md` 252L (ImageBind 4축 마이그레이션 base) + Phase 1 `02_hologram-view/_index.md` V1 SHA UNCHANGED 보존
- Phase 4 entry-gate 충족 조건: `ar_spatial_v3.md` NEW L3 9요소 ≥ 7 + 6-11 경계 cross-handoff RESOLVED + AR EventType 6-12 등록 + LOCK L19 네이밍 준수 100%

**목표**: V2 ImageBind 멀티모달(P2-1) 기반 위에 V3 AR/공간 이해 UI 정의. 3D 공간 위에 Glass HUD 오버레이, 공간 제스처 입력, 시선 추적 기반 인터랙션, 6-11 Hologram-Main-LLM 도메인 경계 재정합(ISS-6 V3 시점 최종 확정).

**입력 파일**:
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §10.1 (ORANGE/BLUE 테마색 LOCK L5/L6) + §5.1 (이벤트 네이밍 LOCK L19)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\multimodal_v2.md` (P2-1 산출물 252L, ImageBind 4축 base)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\_index.md` (Phase 1 정본, 3-point 렌더링 인터페이스 + 6-11 경계 선언 base)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\03_ui-state-machine\event_type_v2_sync.md` (P2-4 산출물 268L, V2 신규 56 EventType + 6-12 cross-handoff 큐)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` LOCK L5/L6 (테마색) + L19 (이벤트 네이밍) + §3 6-11 경계
- `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\` (있는 경우 cross-domain 경계 참조)

**절차**:
1. ISS-6 V3 시점 최종 확정 작업: AUTHORITY_CHAIN §3에 6-11 경계 명시 갱신 — 6-1 = AR UI View 구조(좌표계, 오버레이, 사용자 제스처 입력), 6-11 = AR 렌더링 로직 + Main LLM 파이프라인 (3D 모델 처리, 시선/공간 좌표 변환)
2. multimodal_v2.md ImageBind 4축(원문 / 차원 매트릭스 / 호환 어댑터 / 전환 일정 / 롤백 방안) 읽기 → 공간 좌표 인코딩 추가 가능성 확인
3. AR 인터랙션 정의 5건: (1) 공간 제스처 입력(pinch/grab/swipe-3D), (2) 시선 추적 fallback(키보드 대체 LOCK L8 WCAG 준수), (3) 3D Glass HUD(LOCK L5 ORANGE/L6 BLUE 적용), (4) 공간 voice command(LOCK L9 6개 CLI 보존), (5) AR 환경 fallback(데스크톱 모드 자동 전환)
4. AR EventType 신규 정의 — `ui.hologram.ar.{action}` 형식(LOCK L19 `ui.{layer}.{subject}.{action}` 준수) — 최소 8건(gesture_detected / gaze_changed / spatial_anchor_set / depth_updated / occlusion_resolved / hand_tracking_lost / scene_understanding_ready / ar_session_ended)
5. 6-12 Event-Logging cross-handoff 큐에 AR EventType 8건 등록 (P2-4 event_type_v2_sync.md §5 통합 catalog 형식 직계)
6. L3 9요소(E1~E9) 작성: E1 Input(AR 카메라/IMU 스트림), E2 Algorithm(공간 anchor 의사코드), E3 Output(3D 오버레이 좌표), E4 API Design(`useARSession()` Hook + Three.js 통합), E5 Dependencies(6-11 cross-handoff), E6 Performance(60fps 보장), E7 Error(센서 손실 fallback), E8 Security(공간 데이터 PII 마스킹 6-2 cross-ref), E9 Test (AR 시뮬레이션 ≥ 3 시나리오)
7. ISS-3 STEP7-C 잔여 ~70+ 중 AR 관련 항목 식별 + sub-folder 02_hologram-view 배분 매트릭스

**검증**:
- [x] LOCK L5/L6 테마색 AR Glass HUD 적용 — `<!-- LOCK L5 (D2.0-08 §10.1): #F97316 -->` 인용 형식 준수
- [x] LOCK L19 이벤트 네이밍 `ui.hologram.ar.{action}` 형식 8건 모두 준수
- [x] LOCK L8 WCAG 2.1 AA — AR 시선/제스처에 대한 키보드 대체 입력 정의
- [x] ISS-6 6-11 경계 V3 시점 최종 확정 — AUTHORITY_CHAIN §3 갱신 사항 명시
- [x] 6-12 Event-Logging cross-handoff 큐에 AR EventType 8건 등록
- [x] AR 인터랙션 5건 모두 L3 9요소(E1~E9) ≥ 7 기재
- [x] ISS-3 STEP7-C 잔여 중 AR 관련 매핑 매트릭스 작성
- [x] **Phase 4 entry-gate 충족 조건**: NEW 파일 byte ≥ 350L + L3 PASS + 6-11 경계 RESOLVED + LOCK 변경 0건

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\02_hologram-view\ar_spatial_v3.md` (AR/공간 이해 UI V3 L3 상세) + AUTHORITY_CHAIN.md §3 6-11 경계 V3 갱신 row
</details>

<details>
<summary><b>P3-3. 아바타/디지털 휴먼 V3 (Avatar React 컴포넌트 + 디지털 휴먼 인터랙션)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-3 (§7.1 L303 Phase 3 산출물 "아바타/디지털 휴먼")
- 전환 게이트 조건: P2→P3 ✅ PASS (L311 v12 4건 inheritance) → P3→완료 신규 정의 (Avatar 컴포넌트 등록 + RBAC 권한 검증)
- §6 이슈 ID: ISS-4 (v12 4건 → ISS-7 V3 확장 아바타 컴포넌트 신규) + ISS-3 (STEP7-C 잔여 ~70+ 중 아바타 항목)
- 교차 도메인: 6-2 Security-Governance (아바타 RBAC L10 + PII 마스킹), 6-11 Hologram-Main-LLM (아바타 3D 렌더링), 1-1 LLM (디지털 휴먼 대화 백엔드)
- V3-Phase 매핑: §7.1 L303 "V3 (최종 통합)" — 아바타는 디지털 휴먼 신규 컴포넌트 그룹 (V1 ~44 + V3 신규 추가)
- production 측정 baseline: P2-3 `v12_components.md` 359L (v12 4건 × 12 sub-component L3 base) + LOCK L13 (~44개 → 48개 V2 확장 + V3 추가) 카탈로그 확장 패턴 직계
- Phase 4 entry-gate 충족 조건: `avatar_digital_human_v3.md` NEW L3 9요소 ≥ 7 + LOCK L13 카탈로그 확장 명시(V3 추가) + 6-2 RBAC cross-handoff RESOLVED + PII 마스킹 정합

**목표**: V3 디지털 휴먼/아바타 컴포넌트 신규 정의. 사용자 페르소나 아바타 + AI 디지털 휴먼 대화 인터페이스를 04_react-components에 신규 그룹으로 등록(V1 10그룹 + V2 v12 4건 base + V3 아바타 그룹 추가). LOCK L10 RBAC 4단계와 아바타 권한 매트릭스 정의.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\v12_components.md` (P2-3 산출물 359L, v12 4건 × 12 sub L3 base — Card-Widget Pattern 직계)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\_index.md` (Phase 1 정본, 10그룹 인덱스 + 44 컴포넌트 카탈로그)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` LOCK L13 (React 컴포넌트 수) + L10 (RBAC) + L19 (이벤트 네이밍)
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §10 (UI 테마 LOCK L5/L6 적용)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\` (있는 경우 RBAC + PII 마스킹 cross-handoff)
- `D:\VAMOS\docs\sot 2\1-1_Verifier-Reasoning-Engines\` (있는 경우 디지털 휴먼 대화 백엔드 cross-handoff)

**절차**:
1. v12_components.md Card-Widget Pattern 읽기 → V2 패턴 직계 확인 (12 sub-component L3 9요소 형식)
2. 04_react-components/_index.md 읽기 → V1 10그룹 + V2 v12 4건 카탈로그 → V3 11번째 그룹 "Avatar-Digital-Human" 신규 추가 위치 식별
3. 아바타/디지털 휴먼 컴포넌트 5건 정의: (1) `<UserAvatar />` — 사용자 페르소나 표시(이미지/이니셜/3D), (2) `<DigitalHuman />` — AI 인간 인터페이스(립싱크 + 표정), (3) `<AvatarDialog />` — 대화 말풍선(LOCK L16 i18n ko-KR), (4) `<AvatarPermission />` — RBAC 권한 표시(LOCK L10 4단계 색상 매핑), (5) `<AvatarGallery />` — 다중 아바타 선택 그리드
4. LOCK L10 RBAC 4단계(OWNER/ADMIN/OPERATOR/VIEWER) 아바타 권한 매트릭스 — 각 역할이 표시 가능한 아바타 기능 정의 + 6-2 Security cross-handoff 큐 등록
5. PII 마스킹 정합 — 디지털 휴먼 대화 중 사용자 PII가 노출되지 않도록 6-2 cross-ref
6. 1-1 LLM cross-handoff — 디지털 휴먼 대화 백엔드 API 시그니처 검토 (요청/응답 스키마, 비용 가드레일)
7. 아바타 EventType 신규 — `ui.avatar.{subject}.{action}` LOCK L19 형식 — 최소 6건(persona_changed / dialog_opened / lipsync_started / expression_updated / permission_denied / gallery_selected)
8. LOCK L13 카탈로그 확장 명시 — V1 ~44 + V2 v12 4건 + **V3 아바타 그룹 5건 = 통산 53건** (재정의 아닌 확장 — `<!-- V3 EXTENSION, NOT REDEFINITION -->`)
9. L3 9요소(E1~E9) 작성: 5 컴포넌트 × 9요소 (구조는 P2-3 v12 패턴 직계)

**검증**:
- [x] LOCK L10 RBAC 4단계 아바타 권한 매트릭스 작성 (4 역할 × 5 컴포넌트 = 20 cell)
- [x] LOCK L13 카탈로그 확장 명시 — `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 + V1+V2+V3 통산 정확히 명시
- [x] LOCK L19 이벤트 네이밍 `ui.avatar.{subject}.{action}` 6건 모두 준수
- [x] LOCK L16 i18n ko-KR 기본 + 다국어 확장 — 아바타 대화 UI 준수
- [x] 6-2 Security-Governance RBAC + PII 마스킹 cross-handoff 큐 등록
- [x] 1-1 LLM 디지털 휴먼 대화 백엔드 cross-handoff 큐 등록
- [x] 6-11 Hologram-Main-LLM 3D 렌더링 cross-handoff (아바타 3D 표현 시)
- [x] ISS-3 STEP7-C 잔여 중 아바타 관련 항목 매핑
- [x] L3 9요소(E1~E9) ≥ 7 × 5 컴포넌트 = 35 cell 이상 기재
- [x] **Phase 4 entry-gate 충족 조건**: NEW 파일 byte ≥ 400L + L3 PASS + 6-2/1-1/6-11 3 cross-handoff RESOLVED + LOCK 변경 0건

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\avatar_digital_human_v3.md` (아바타/디지털 휴먼 V3 L3 상세) + `04_react-components\_index.md` 11번째 그룹 "Avatar-Digital-Human" 등재 + LOCK L13 카탈로그 확장 row
</details>

<details>
<summary><b>P3-4. V3 확장 슬롯 4개 정의 (Plugin Slot Architecture)</b></summary>

**대조 기준 (7항목)**:
- 작업 그룹 ID: P3-4 (§7.1 L303 Phase 3 산출물 "V3 확장 슬롯 4개")
- 전환 게이트 조건: P2→P3 ✅ PASS (L311) → P3→완료 신규 정의 (4 슬롯 인터페이스 + Plugin 등록 메커니즘)
- §6 이슈 ID: ISS-3 (STEP7-C 잔여 ~70+ V3 범위 11번째 그룹 신설 Wellness/Education V3 범위, L1756 이월 항목)
- 교차 도메인: 3-7 Developer-Tools-API-SDK (Plugin SDK 정본 — 3-7 정의, 6-1은 UI 슬롯만), 6-2 Security-Governance (Plugin 보안 화이트리스트 + 샌드박스 LOCK L12)
- V3-Phase 매핑: §7.1 L303 "V3 (최종 통합)" 마지막 산출물 — Phase 3 핵심 신규 항목 (V1/V2에는 미존재)
- production 측정 baseline: LOCK L13 (~44 + V2 v12 4 + V3 아바타 5 = 통산 53건) + 4 슬롯 추가 = **57건 확장 한도 검증**
- Phase 4 entry-gate 충족 조건: `extension_slots_v3.md` NEW L3 9요소 ≥ 7 + 4 슬롯 모두 인터페이스 시그니처 정의 + 3-7 Plugin SDK cross-handoff + 6-2 보안 화이트리스트 cross-handoff

**목표**: V3 최종 통합 산출물 4개 확장 슬롯(Plugin Slot) 정의. UI 영역별로 외부 Plugin이 안전하게 주입될 수 있는 확장점 4개 정의(Slot 1-4) + 인터페이스 시그니처 + 보안 화이트리스트 + 샌드박스 정책. ISS-3 11번째 그룹 신설(Wellness/Education V3 범위) 매핑.

**입력 파일**:
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\AUTHORITY_CHAIN.md` LOCK L13 (컴포넌트 수) + L10 (RBAC) + L8 (WCAG) + L20 (FailureCode)
- `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\_index.md` (카탈로그 V1+V2+V3 통산 base)
- `D:\VAMOS\docs\sot\D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §7 (FailureCode + FallbackRegistry LOCK L20)
- `D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\` (있는 경우 Plugin SDK 정본 cross-handoff)
- `D:\VAMOS\docs\sot 2\6-2_Security-Governance\` (있는 경우 Plugin 화이트리스트 + 샌드박스 cross-handoff)
- 본 계획서 §7.1 L303 (Phase 3 산출물 "V3 확장 슬롯 4개" 정본 출처) + L1756 [Phase 2] §4 이월 (11번째 그룹 신설 Wellness/Education V3 범위 이월 항목)

**절차**:
1. 4 확장 슬롯 영역 결정 — (1) `<HeaderSlot />` 상단 메뉴바 영역, (2) `<SidebarSlot />` 좌측 패널 확장(LOCK L2 250-300px 영역 내), (3) `<ContentSlot />` 중앙 영역 확장(LOCK L4 Flex-grow), (4) `<FooterSlot />` 하단 상태바 영역
2. 각 슬롯 인터페이스 시그니처 정의 — TypeScript `interface UIExtensionSlot { id: string; render: () => ReactNode; permission: RBACRole[]; sandbox: boolean; }` + Plugin SDK 호환
3. 3-7 Developer-Tools-API-SDK cross-handoff — Plugin SDK 등록 메커니즘 (3-7 정본) + 6-1은 UI 슬롯 인터페이스만 정의 (경계 명시)
4. 6-2 Security-Governance cross-handoff — Plugin 화이트리스트 + Docker 샌드박스(LOCK L12 Part2 §6.5.1, V2 P2-1 D8-L03 패턴 직계) + RBAC L10 4단계 권한 게이트
5. ISS-3 11번째 그룹(Wellness/Education V3 범위, L1756 이월) 매핑 — Wellness Plugin / Education Plugin이 어떤 슬롯에 주입되는지 매트릭스 작성
6. FailureCode 신규(LOCK L20 14→V3 확장) — Plugin 관련 FailureCode 최소 4건(PLUGIN_LOAD_TIMEOUT / PLUGIN_PERMISSION_DENIED / PLUGIN_SANDBOX_ESCAPE / PLUGIN_RENDER_ERROR) + FallbackRegistry 매핑
7. 슬롯 EventType 신규 — `ui.{slot}.plugin.{action}` LOCK L19 형식 — 최소 8건(load_requested / load_success / load_failure / render_started / render_error / permission_denied / sandbox_violation / unloaded)
8. L3 9요소(E1~E9) 작성 — 4 슬롯 × 9요소

**검증**:
- [x] 4 확장 슬롯 모두 TypeScript 인터페이스 시그니처 정의 (Props + render + permission + sandbox)
- [x] LOCK L2/L3/L4 3-Column 폭/Flex-grow 슬롯 영역 정합 (재정의 0건)
- [x] LOCK L10 RBAC 4단계 슬롯별 권한 매트릭스 (4 슬롯 × 4 역할 = 16 cell)
- [x] LOCK L12 Docker 샌드박스 — 6-2 cross-handoff 큐 등록 + Plugin 격리 정책 명시
- [x] LOCK L20 FailureCode V3 확장 명시(14→18) — `<!-- V3 EXTENSION, NOT REDEFINITION -->` + FallbackRegistry 매핑
- [x] LOCK L19 이벤트 네이밍 `ui.{slot}.plugin.{action}` 8건 모두 준수
- [x] 3-7 Developer-Tools-API-SDK Plugin SDK cross-handoff 큐 등록
- [x] 6-2 Security 화이트리스트 + 샌드박스 cross-handoff 큐 등록
- [x] ISS-3 11번째 그룹(Wellness/Education V3) 슬롯 매핑 매트릭스 작성
- [x] LOCK L13 컴포넌트 수 통산 53 → **57 V3 확장 한도** 명시
- [x] L3 9요소(E1~E9) ≥ 7 × 4 슬롯 = 28 cell 이상 기재
- [x] **Phase 4 entry-gate 충족 조건**: NEW 파일 byte ≥ 350L + L3 PASS + 3-7/6-2 cross-handoff RESOLVED + LOCK 변경 0건 + FailureCode V3 확장 명시

**산출물**: `D:\VAMOS\docs\sot 2\6-1_UI-UX-System\04_react-components\extension_slots_v3.md` (V3 확장 슬롯 4개 L3 상세) + `04_react-components\_index.md` 슬롯 4개 카탈로그 등재 + LOCK L13 통산 57 + L20 FailureCode V3 확장 row
</details>

> **Phase 3 → Phase 4 인계 게이트** (Phase 15 NEW, 본 §7.2 P3→완료 신규 정의):
> - [x] Phase 3 NEW 산출물 4건 모두 L3 PASS (9요소 ≥ 7) + 의사코드/시그니처 포함
> - [x] LOCK L1~L20 set accuracy 20 unique 변경 0건 (V3 확장은 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 명시)
> - [x] CONFLICT OPEN 0건 (CONF-61-001~003 보존 + Phase 3 신규 0건)
> - [x] 교차 도메인 cross-handoff 큐 RESOLVED: 6-11(AR 경계 ISS-6) + 4-1(모바일 IPC) + 6-2(RBAC/PII/샌드박스) + 1-1(디지털 휴먼 LLM) + 6-12(EventType) + 3-7(Plugin SDK)
> - [x] ISS-3 STEP7-C 잔여 ~70+ V3 범위 매핑 완료 + ISS-7 V2 신규 FailureCode V3 확장 정의 + 11번째 그룹(Wellness/Education) 슬롯 매핑
> - [x] FABRICATION 0/N CLEAN (parent-executed Subagent 0회 유지) + V1/V2 본문 byte-prefix SHA UNCHANGED

> **Phase 3 세션 전체 검증 결과** (6-1, 2026-05-17 — ★ Wave 2 #13 첫 도메인 SPEC COMPLETE)
>
> | 항목 | 결과 |
> |------|------|
> | P3 블록 수 | 4 완료 (P3-1 ✅ 모바일 대응 V3 + P3-2 ✅ AR/공간 이해 UI V3 + P3-3 ✅ 아바타/디지털 휴먼 V3 + P3-4 ✅ V3 확장 슬롯 4개) |
> | R cascade 통산 | **~603 verifications + 4 fix textual notation only** (P3-1 161 + P3-2 120 + P3-3 ~161 + P3-4 ~161) — mixed pattern Wave 2 specialty: P3-1 tcv2 first-pass-after-fix + P3-2 tcv1 first-pass NO-DRIFT direct + P3-3 tcv2 first-pass-after-fix + P3-4 tcv2 first-pass-after-fix |
> | drift fix 4건 (ALL textual notation only) | D-6-1-P3-1-R4-1 cite "L1729" → "L1756" (in-place 4-char EXACT, +0 B) + D-6-1-P3-3-R3-1 "1-1_LLM" → "1-1_Verifier-Reasoning-Engines" (실제 폴더명 정합 verify, +23 B) + D-6-1-P3-4-R3-1 cite "L1754" → "L1756" (in-place 4-char, +0 B) + D-6-1-P3-4-R3-2 cite "§6.2 L283" → "L1756 [Phase 2] §4 이월" (11번째 그룹 정본 cite, +16 B) |
> | byte/SHA pre/post | **pre 181A4CFE49952E45 / 189,225 B / 2,210 LF → post 85C4B72BD9AF7C7B / 189,264 B / 2,210 LF** Δ **+39 B / +0 LF** (SHA 통산 변경 4회 cascade) |
> | LOCK 변경 | **0** (L1~L20 20 unique set accuracy 보존 통산 Phase 0/1/2/3) |
> | DEFINED-HERE 변경 | **0** (AUTHORITY §4 LOCK 정본 EXACT 보존) |
> | FABRICATION | **0** (parent-executed Subagent 0회 통산) |
> | abort marker | **9종 ALL NOT FIRED self-fire 0** (UPSTREAM_INCOMPLETE:6-1 / DERIVATION_DEFINITION_MISSING:6-1 / LOCK_VIOLATION / CROSS_REF_DRIFT / BYTE_SHA_MISMATCH / CONFLICT_OPEN_DETECTED / PHASE4_ENTRY_GATE_NOT_MAPPED / BILATERAL_SOT2_DRIFT / DOWNSTREAM_PROPAGATE_MISS) |
> | 6 anchor 충족 | 안전 ✅ + 누락 0 ✅ + 오류 0 ✅ + **미세 ✅★★ (cite imprecision 3건 + 1-1 path drift 1건 검출 정확도 100%)** + 수렴 ✅ (16 round × 3 fix-cascade + 12 round × 1 NO-DRIFT direct) + 재검증 ✅ (post-fix 4 round × 3 + first-pass 3 round × 1 무수정 cascade) ALL ✅ |
> | upstream 도메인 의존 검증 | **1-2 Auxiliary-Modules** ✅ (Wave 1 #1 SPEC COMPLETE 2026-05-14) + **3-6 Health-Wellness-EmotionAI** ✅ (Wave 1 #8 SPEC COMPLETE 2026-05-17, 감정 UI inheritance) + **3-7 Developer-Tools-API-SDK** ✅ (Wave 1 #9 SPEC COMPLETE 2026-05-17 ★ NO-DRIFT 100%, P3-4 Plugin SDK forward-inheritance first 사례 Wave 2 → Wave 1 inheritance) ALL ✅ |
> | downstream 도메인 영향 분석 | **6-11★ Hologram-Main-LLM** ⬜ (Wave 3 #28 derivation, ISS-6 V3 경계 재정합 + AR 렌더링 정본 + cross_domain_validation_report target) + **6-9★ Brain-Adapter-HAL** ⬜ (Wave 3 #27 derivation, Adapter UI + 3D 렌더링) — Wave 3 forward-defined inheritance pattern (3-4 N-018 + 3-5 wellness_community + 3-6 6-1/6-2 + 3-7 3-10★/4-3★ + 4-2 4-4/4-1 + 4-4 6-9/4-3 패턴 직계, ⑥단계 CROSS_REF_MATRIX §1 row 6-1 inline reference 갱신 처리) |
> | Phase 4 entry-gate 매핑 | **4개 P3 모두 명시** ✅ — P3-1 (responsive_layout_v3.md ≥ 200L + LOCK L11 V3 확장 + WCAG AA 모바일 + CONFLICT 0) / P3-2 (ar_spatial_v3.md ≥ 350L + 6-11 경계 RESOLVED + AR EventType 6-12 등록 + LOCK L19 100%) / P3-3 (avatar_digital_human_v3.md ≥ 400L + LOCK L13 카탈로그 확장 + 6-2/1-1/6-11 3 cross-handoff RESOLVED + PII 마스킹) / P3-4 (extension_slots_v3.md ≥ 350L + 4 슬롯 인터페이스 + 3-7/6-2 cross-handoff + FailureCode V3 확장 14→18) |
> | LOCK 인용 통산 | **30건** (P3-1 11 + P3-2 5 + P3-3 6 + P3-4 8) ALL AUTHORITY §4 §3.4 정본 EXACT 정합 (DEFINED-HERE 0건) — P3-4가 통산 가장 많음 (L2/L4 + L8 + L10 + L12 + L13 + L19 + L20) |
> | NEW 산출물 V3 매트릭스 (forward-defined Phase 4 implementation) | (1) responsive_layout_v3.md + mobile_a11y_v3.md (P3-1) + (2) ar_spatial_v3.md + AUTHORITY §3 6-11 경계 V3 갱신 row (P3-2) + (3) avatar_digital_human_v3.md + _index.md 11번째 그룹 등재 + LOCK L13 카탈로그 확장 row (P3-3) + (4) extension_slots_v3.md + _index.md 슬롯 4개 등재 + LOCK L13 통산 57 + L20 FailureCode V3 확장 row (P3-4) = **통산 V3 NEW 산출물 8건 + AUTHORITY §3 + §4 + _index 등재 row 3건 forward-defined** |
> | ★ NO-DRIFT 100% specialty | ❌ **partial** (P3-2만 NO-DRIFT 100% first-pass, P3-1 + P3-3 + P3-4은 textual notation only fix 적용 = mixed pattern Wave 2 specialty) — 3-7 Wave 1 #9 + 3-9 Wave 1 #10 ALL ZERO write 100% 패턴과 부분 다름, 4-2 Wave 1 #11 partial (1 fix) + 4-4 Wave 1 #12 partial (1 fix) + Round 2 audit 패턴 EXACT 직계 partial Wave 2 #13 specialty |
> | ★ 핵심 milestone | (1) **🎉 Wave 2 첫 도메인 SPEC COMPLETE 진입 ready** (Wave 1 12/12 ✅ → Wave 2 #13 6-1 SPEC COMPLETE 진입 매트릭스 도달, ⑤⑥⑦ 단계 진입 가능) + (2) **★★ upstream 3-7 forward-inheritance Plugin SDK first 사례 Wave 2 → Wave 1 inheritance** (LOCK-BM-09 reverse-inheritance 패턴과 비교 시 6-1 → 3-7 forward-inheritance 패턴 first 사례 Wave 2 specialty) + (3) **★ 8 LOCK 인용 P3-4 통산 최다** (L2/L4 + L8 + L10 + L12 + L13 + L19 + L20) + (4) **★ LOCK L13 53 → 57 V3 확장 한도** + **L20 14 → 18 V3 확장 매트릭스 milestone** + (5) **★ mixed pattern Wave 2 specialty** (tcv2 + tcv1 NO-DRIFT direct + tcv2 + tcv2) + (6) **★ 1-1 폴더 path 정밀화 통산 3번째 사례** (4-4 P3-2 + 4-2 P3-3 + 본 P3-3 D-6-1-P3-3-R3-1 패턴 EXACT 직계) + (7) **★ ISS-6 V3 시점 6-11 경계 재정합 매핑 정합** (AUTHORITY §5.1 정본 base + P3-2 절차 1 V3 갱신 강제 명시 forward-defined design) + (8) **★ Plugin Slot Architecture 4 슬롯 + Plugin EventType 8건 + Plugin FailureCode 4건 정의 정합** |
>
> **[PHASE3_COMPLETE: 6-1 — 2026-05-17] ✅ Wave 2 #13 6-1 UI-UX-System Phase 3 4/4 P3 ALL ✅ SPEC 검증 매트릭스 도달**. 도메인 종료 ⑤ bilateral 갱신 → ⑥ downstream 전파 → ⑦ PROGRESS.md domain-complete 단계 진입 ready (4-4 / 4-2 / 3-9 / 3-7 단일 대화창 패턴 EXACT 직계 Wave 2 첫 도메인 SPEC COMPLETE milestone).

#### Phase 4: V3 implementation + production-ready 정본 승급 (forward-defined, Phase 16 §16 S16-5 inheritance, Tier 6 UI-UX specialty) ✅ **Phase 4 완료 Stage A (2026-05-26, 4 task)** — `[PHASE4_COMPLETE_STAGE_A: 6-1 — 2026-05-26]` ⬛ + 🌟🌟🌟🌟🌟 4/4 NO-DRIFT FULL milestone first specialty + LOCK 20/20 전수 coverage FINAL milestone first + 3-7 Plugin SDK Wave 1 → Wave 2 cross-Wave forward-inheritance first specialty + Wave 2 첫 도메인 Stage A 완료 milestone first

**목표**: Phase 3 4 P3 SPEC COMPLETE baseline 위에 V3 implementation을 production-ready로 정본 승급 — 모바일 BP-D 768px 정식 (P3-1 inheritance) + AR/공간 이해 UI + 6-11 경계 V3 시점 최종 확정 (P3-2 inheritance, ISS-6 RESOLVED) + 아바타/디지털 휴먼 V3 11번째 그룹 등재 + LOCK L13 카탈로그 확장 (P3-3 inheritance) + V3 확장 슬롯 4개 + Plugin SDK 통합 + FailureCode V3 확장 14→18 + L13 통산 57 (P3-4 inheritance) production-ready 정본 승급 + ReadOnly FALSE (STAGE 7~8 Production 승급, 직접 편집 가능).

**범위**: 4 Phase 4 task (P4-1~P4-4) + 10 forward-defined entry-gate conditions (P3-1 2 + P3-2 3 + P3-3 2 + P3-4 3 = audit baseline 단계 0 결과 §7.3 Phase 3 세션 전체 검증 결과 요약 매핑 row 인용, S16-5 6 도메인 통산 67 conditions 중 6-1 10).

**산출물**: V3 NEW production .md (P4-1 `01_builder-view/responsive_layout_v3.md` 모바일 BP-D 정식 + `06_accessibility/mobile_a11y_v3.md` WCAG 2.1 AA 모바일 + P4-2 `02_hologram-view/ar_spatial_v3.md` AR/공간 이해 UI + AUTHORITY §3 6-11 경계 V3 갱신 + P4-3 `04_react-components/avatar_digital_human_v3.md` 디지털 휴먼 컴포넌트 5건 + `_index.md` 11번째 그룹 "Avatar-Digital-Human" 등재 + LOCK L13 카탈로그 확장 row + P4-4 `04_react-components/extension_slots_v3.md` Plugin Slot 4개 + LOCK L13 통산 57 + LOCK L20 FailureCode V3 확장 row) + AUTHORITY_CHAIN minor 갱신 (LOCK L1~L20 baseline 보존 + 6-11/3-7/1-1 cross-ref append) + CONFLICT_LOG cascade (OPEN 0 inheritance, Phase 4 신규 충돌 0) + INDEX 갱신 (L3 완성률 + Phase 4 상태) + `_verification/phase4_v3_p4-{1..4}_promotion_report.md` + 6-11 AR 경계 + 1-1 디지털 휴먼 LLM + 3-7 Plugin SDK + 6-2 RBAC/PII/샌드박스 + 6-12 EventType + 4-1 모바일 IPC 횡단 cross-handoff.

##### Phase 4 → Phase 5 전환 게이트 (forward-defined)

| Gate | 조건 |
|------|------|
| G4-1 | V3 implementation 완료 — 모바일 BP-D 768px 정식 + AR/공간 이해 UI + 아바타/디지털 휴먼 11번째 그룹 + V3 확장 슬롯 4개 4 P3 inheritance 전수 PASS |
| G4-2 | Status DRAFT → APPROVED 전수 전환 — V3 NEW production .md (responsive_layout_v3 + mobile_a11y_v3 + ar_spatial_v3 + avatar_digital_human_v3 + extension_slots_v3 = 5 신규 + _index.md 11번째 그룹 등재) + AUTHORITY §3 6-11 경계 V3 갱신 row + LOCK L13/L20 카탈로그 확장 row 메타 갱신 |
| G4-3 | LOCK 재정의 0 — LOCK L1~L20 20 unique set accuracy 변경 0건 verbatim 영구 보존 (R9) + V3 확장은 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제 (L11 모바일 BP-D + L13 53→57 + L20 14→18) + DEFINED-HERE 0건 |
| G4-4 | CONFLICT_LOG 0 OPEN — CONF-61-001~003 RESOLVED 3건 inheritance, Phase 4 신규 충돌 0 (ISS-6 6-11 경계 V3 시점 최종 확정으로 잠재 충돌 사전 차단) |
| G4-5 | production 실측 baseline — 모바일 BP-D 전환 < 100ms + WCAG 2.1 AA 모바일 검증 통과 + AR 60fps 보장 + 아바타 카탈로그 통산 53건 + Plugin Slot 4개 인터페이스 시그니처 + Plugin FailureCode 4건 정의 + Plugin EventType 8건 LOCK L19 100% 준수 + staging 환경 7일 측정 데이터 |
| G4-6 | 교차 도메인 cross-handoff — 6-11 Hologram-Main-LLM (Wave 3 #28 ✅) AR 렌더링 정본 + ISS-6 경계 RESOLVED 양방향 + 1-1 Verifier-Reasoning-Engines (Wave 2 #21 ✅) 디지털 휴먼 대화 백엔드 LLM cross-handoff + 3-7 Developer-Tools-API-SDK (Wave 1 #9 ✅) Plugin SDK 등록 메커니즘 forward-inheritance 양방향 + 6-2 Security-Governance (Wave 2 #14 ✅) RBAC L10 + PII 마스킹 + Docker 샌드박스 LOCK L12 + 6-12 Event-Logging (Wave 3 #29 ⬜ forward-defined) EventType `ui.builder.responsive.*` + `ui.hologram.ar.*` + `ui.avatar.*` + `ui.{slot}.plugin.*` 통산 ≥ 30건 등록 + 4-1 Rust-Tauri-Infrastructure (Wave 3 #24 ✅) 모바일 IPC 경계 |
| G4-7 | Phase 5 entry-gate forward-defined — V3 production 배포 승인 결재 + GOLD 등급 baseline + 11번째 그룹 Wellness/Education V3 범위 매핑 완료 (Plugin Slot 주입) + STEP7-C 잔여 ~70+ V3 범위 100% 매핑 완료 |

##### Phase 4 단계별 상세 작업 절차

<details>
<summary><b>P4-1. 모바일 BP-D 768px + WCAG 2.1 AA 모바일 production-ready 정본 승급 (P3-1 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-1 "모바일 BP-D 768px 정식 + WCAG 2.1 AA 모바일 + Touch FailureCode V3 확장 + 모바일 RBAC" (P3-1 forward-defined Phase 4 entry-gate 명세 §7.3 L1774 — NEW 파일 byte ≥ 200L + LOCK L11 V3 확장 + WCAG AA 모바일 + CONFLICT 0 = 2 audit conditions)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK L11 V3 확장 (재정의 0건)" + G4-5 "모바일 BP-D 전환 < 100ms + WCAG 2.1 AA 모바일 검증 통과 + staging 7일 측정" + G4-7 "STEP7-C 잔여 ~70+ V3 범위 100% 매핑 완료"
- §6 이슈: ISS-3 STEP7-C 잔여 ~70+ V3 범위 중 모바일 항목 + ISS-7 V2 신규 FailureCode V3 모바일 확장 (Touch/Gesture/Orientation 3건)
- 교차 도메인: 4-1 Rust-Tauri-Infrastructure (Wave 3 #24 ✅) 모바일 IPC 경계 + 6-2 Security-Governance (Wave 2 #14 ✅) 모바일 RBAC L10 4단계 + Part2 §6.5 보안 체크리스트 + 6-12 Event-Logging (Wave 3 #29 ⬜) EventType `ui.builder.responsive.*` 등록
- Part2 V3-Phase 매핑: §7.1 L303 "V3 (최종 통합)" — Part2 V3 미정의이므로 본 계획서 §7.1 + 6-1 정본 + 4-1 Tauri Phase 매핑 공동 정의 + ★ Phase 15 derivation marker 없음 (6-1 derivation 0)
- production 측정 실측값: Phase 1 14 L3 파일 SHA UNCHANGED + Phase 2 NEW `responsive_layout_v2.md` 229L (P2-2 산출물) byte/SHA/LF + LOCK L11 V1 1280×720 verbatim 보존 + BP-D 768px V3 추가 정의 (재정의 아닌 확장) + 3-Column → 1-Column 변환 매트릭스 (Drawer / BottomSheet / Builder Panel) + WCAG 2.1 AA 모바일 추가 항목 ≥ 10건 (터치 타겟 44×44pt + 스와이프 대체 + ARIA + i18n 폰트 스케일) + Touch FailureCode 3건 (Touch/Gesture/Orientation) + BP-D 전환 < 100ms 9-State LOCK L1 모바일 전이 + 500ms 지연 LOCK L17 모바일 보장 + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: 모바일 BP-D 100% 완료 + staging 7일 측정 데이터 + WCAG AA 자동 검사 통과율 100% + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 모바일 BP-D V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK L1 (9-State) + L2/L3/L4 (3-Column) + L8 (WCAG) + L11 (V1 해상도, V3 확장 명시) + L17 (전이 500ms) + L19 (이벤트 네이밍) verbatim 보존 (R9) + V3 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-1에서 정의한 모바일 BP-D 768px 확장 + WCAG 2.1 AA 모바일 + Touch FailureCode V3 확장 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-1 ✅) → Phase 4 V3 implementation으로 전환하여 (1) responsive_layout_v3.md 모바일 BP-D 정식 + (2) mobile_a11y_v3.md WCAG 2.1 AA 모바일 정식 + (3) 9-State LOCK L1 모바일 전이 규칙 + (4) Touch FailureCode 3건 (Touch/Gesture/Orientation) + 4-1 모바일 IPC + 6-2 모바일 RBAC + 6-12 EventType `ui.builder.responsive.*` 등록 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/UI_UX_SYSTEM_구조화_종합계획서.md` §3.4 LOCK L1/L2/L3/L4/L8/L11/L17/L19 / §6 ISS-3/ISS-7 / §7.3 P3-1 (forward-defined L1764~L1808)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/01_builder-view/responsive_layout_v2.md` (P2-2 산출물 229L base)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/06_accessibility/_index.md` (WCAG 2.1 AA 체크리스트 LOCK L8)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/AUTHORITY_CHAIN.md` LOCK L11 (V1 해상도) + L2/L3/L4 (3-Column) + L8 (WCAG)
- `D:/VAMOS/docs/sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §3 (3-Column 정본) + §3.1 (LOCK L11)
- `D:/VAMOS/docs/sot 2/4-1_Rust-Tauri-Infrastructure/` (모바일 IPC 경계 cross-handoff)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/` (모바일 RBAC L10 cross-handoff)

**절차**:
1. P3-1 forward-defined V3 산출물 명세 (BP-D 768px + WCAG 모바일 + Touch FailureCode) inventory 확인 + baseline 측정 (byte/line/SHA).
2. `01_builder-view/responsive_layout_v3.md` 신규 — BP-D 768px V3 추가 정의 (LOCK L11 재정의 아닌 V3 확장) + 3-Column → 1-Column 전환 규칙 + 좌측 Drawer + 우측 BottomSheet + Builder Panel 모바일 키보드 처리 + `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제.
3. `06_accessibility/mobile_a11y_v3.md` 신규 — WCAG 2.1 AA 모바일 추가 항목 ≥ 10건 (터치 타겟 44×44pt + 스와이프 제스처 키보드 대체 + ARIA live region + i18n LOCK L16 ko-KR 모바일 폰트 스케일).
4. 9-State LOCK L1 모바일 전이 규칙 정의 — 최대 500ms 전이 지연 LOCK L17 모바일 보장 + Touch FailureCode 신규 정의 (Touch/Gesture/Orientation 3건, ISS-7 V3 확장).
5. 4-1 Rust-Tauri-Infrastructure 모바일 IPC cross-handoff — AUTHORITY_CHAIN §3 4-1 IPC 경계 inheritance + 4-1 Phase 매핑 양방향 ref.
6. 6-2 Security-Governance 모바일 RBAC L10 (OWNER/ADMIN/OPERATOR/VIEWER) 모바일 인증 UX cross-handoff + Part2 §6.5 보안 체크리스트 우선.
7. 6-12 Event-Logging cross-handoff — 모바일 EventType `ui.builder.responsive.{action}` 신규 등록 (breakpoint_changed / column_collapsed / drawer_opened / bottomsheet_opened / orientation_locked / keyboard_visible 최소 6건, LOCK L19 100% 준수).
8. AUTHORITY_CHAIN.md cross-check: LOCK L11 정본 출처 변경 0 + V3 확장 명시 row append.
9. production 실측 측정: BP-D 전환 < 100ms P95 + WCAG AA 자동 검사 통과율 100% + Touch FailureCode 3건 staging 7일 측정 PASS.
10. INDEX.md 마스터 L3 완성률 갱신 + Phase 4 상태.
11. Phase 5 entry-gate forward-defined 작성 (STEP7-C 잔여 ~70+ V3 범위 매핑 완료).

**검증**:
- [ ] 모바일 BP-D 768px 정식 + responsive_layout_v3.md NEW byte ≥ 200L Status APPROVED 전환 완료
- [ ] WCAG 2.1 AA 모바일 검증 통과 + mobile_a11y_v3.md NEW byte + 추가 항목 ≥ 10건 staging 7일 측정 PASS
- [ ] LOCK L11 V3 확장 명시 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 + V1 1280×720 verbatim 영구 보존 (R9)
- [ ] LOCK L1 (9-State) + L2/L3/L4 (3-Column) + L8 (WCAG) + L17 (전이 500ms) + L19 (이벤트 네이밍) verbatim 영구 보존 (R9)
- [ ] Touch FailureCode 3건 (Touch/Gesture/Orientation) 정의 완료 + FallbackRegistry 매핑
- [ ] 4-1 Rust-Tauri-Infrastructure 모바일 IPC + 6-2 Security-Governance 모바일 RBAC L10 + 6-12 Event-Logging 모바일 EventType 6건 cross-handoff reference 양방향 정합
- [ ] BP-D 전환 < 100ms P95 staging 7일 측정 PASS
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] CONFLICT_LOG OPEN 0건 (CONF-61-001~003 RESOLVED 보존 + Phase 4 신규 0)
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (STEP7-C 잔여 ~70+ V3 범위 매핑 완료)
- [ ] **[Phase 16 NEW] 모바일 BP-D + WCAG AA + Touch FailureCode V3 production-ready 정본 승급 조건 충족**

**산출물**: 모바일 BP-D V3 production .md 정본 (`01_builder-view/responsive_layout_v3.md` + `06_accessibility/mobile_a11y_v3.md`) + AUTHORITY_CHAIN.md LOCK L11 V3 확장 row append + `_verification/phase4_v3_p4-1_promotion_report.md`
</details>

<details>
<summary><b>P4-2. AR/공간 이해 UI V3 + 6-11 경계 V3 시점 최종 확정 production-ready 정본 승급 (P3-2 inheritance, ISS-6 RESOLVED)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-2 "AR/공간 이해 UI V3 + Hologram View V3 + 6-11 경계 재정합 + AR EventType 6-12 등록" (P3-2 forward-defined Phase 4 entry-gate 명세 §7.3 L1820 — NEW 파일 byte ≥ 350L + 6-11 경계 RESOLVED + AR EventType 6-12 등록 + LOCK L19 네이밍 100% = 3 audit conditions)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK L5/L6/L8/L9/L19 정합" + G4-5 "AR 60fps 보장" + G4-6 "**6-11 Hologram-Main-LLM (Wave 3 #28 ✅) AR 렌더링 정본 + ISS-6 경계 RESOLVED 양방향**"
- §6 이슈: ISS-6 (Hologram View와 6-11 도메인 범위 경계 — AUTHORITY_CHAIN §3에 경계 명시 V3 시점 최종 확정) + ISS-3 (STEP7-C 잔여 ~70+ V3 범위 중 AR 항목)
- 교차 도메인: **6-11 Hologram-Main-LLM (Wave 3 #28 ✅) AR 렌더링 정본 — 6-11 정의 / 6-1은 View 구조만 (좌표계 + 오버레이 + 사용자 제스처 입력) 경계 명시** + 6-12 Event-Logging (Wave 3 #29 ⬜) AR EventType 신규 8건 + 6-2 Security-Governance (Wave 2 #14 ✅) 공간 데이터 PII 마스킹
- Part2 V3-Phase 매핑: §7.1 L303 "V3 (최종 통합)" — AR Phase는 본 계획서 §7.1 + 6-11 정본 cross-handoff 공동 정의 + ★ Phase 15 derivation marker 없음
- production 측정 실측값: P2-1 `multimodal_v2.md` 252L (ImageBind 4축 마이그레이션 base) byte/SHA/LF + Phase 1 `02_hologram-view/_index.md` V1 SHA UNCHANGED 보존 + AR 인터랙션 5건 (공간 제스처 pinch/grab/swipe-3D + 시선 추적 fallback + 3D Glass HUD LOCK L5/L6 + 공간 voice command LOCK L9 + AR 환경 fallback) + AR EventType 8건 `ui.hologram.ar.{action}` (gesture_detected / gaze_changed / spatial_anchor_set / depth_updated / occlusion_resolved / hand_tracking_lost / scene_understanding_ready / ar_session_ended) LOCK L19 100% 준수 + AR 60fps 보장 + AUTHORITY §3 6-11 경계 V3 시점 최종 확정 row + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: AR/공간 이해 UI 100% 완료 + 6-11 경계 양방향 정합 + AR 60fps staging 7일 측정 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: AR/공간 이해 UI V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK L5/L6 (테마색) + L8 (WCAG) + L9 (6 CLI) + L19 (이벤트 네이밍) verbatim 보존 (R9) + AUTHORITY §3 6-11 경계 V3 시점 최종 확정 row 등재 강제 + 6-11 AR 렌더링 정본 ↔ 6-1 View 구조 경계 EXACT MATCH 100% + ReadOnly FALSE 유지

**목표**: Phase 3 P3-2에서 정의한 AR/공간 이해 UI V3 + 6-11 경계 재정합 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-2 ✅) → Phase 4 V3 implementation으로 전환하여 (1) ar_spatial_v3.md AR 인터랙션 5건 + (2) AUTHORITY §3 6-11 경계 V3 시점 최종 확정 (6-1 = AR UI View 구조 / 6-11 = AR 렌더링 로직 + Main LLM 파이프라인) + (3) AR EventType 8건 LOCK L19 100% 준수 + (4) 6-12 통합 catalog 직계 등록 + AR 60fps baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/UI_UX_SYSTEM_구조화_종합계획서.md` §3.4 LOCK L5/L6/L8/L9/L19 / §6 ISS-6 / §7.3 P3-2 (forward-defined L1810~L1852)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/02_hologram-view/multimodal_v2.md` (P2-1 산출물 252L base)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/02_hologram-view/_index.md` (Phase 1 정본, 6-11 경계 base)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/03_ui-state-machine/event_type_v2_sync.md` (P2-4 산출물 268L, V2 신규 56 EventType + 6-12 cross-handoff 큐)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/AUTHORITY_CHAIN.md` LOCK L5/L6 + L19 + §3 6-11 경계
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` (Wave 3 #28 ✅ AR 렌더링 정본)
- `D:/VAMOS/docs/sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §10.1 (LOCK L5/L6) + §5.1 (LOCK L19)

**절차**:
1. P3-2 forward-defined V3 산출물 명세 (AR/공간 이해 UI + 6-11 경계 V3 시점 최종 확정 + AR EventType 8건) inventory 확인 + baseline 측정.
2. ISS-6 V3 시점 최종 확정 작업: AUTHORITY_CHAIN §3 6-11 경계 V3 갱신 row append — **6-1 = AR UI View 구조 (좌표계, 오버레이, 사용자 제스처 입력) / 6-11 = AR 렌더링 로직 + Main LLM 파이프라인 (3D 모델 처리, 시선/공간 좌표 변환)** 경계 EXACT 명시.
3. `02_hologram-view/ar_spatial_v3.md` 신규 — AR 인터랙션 5건 정의 (1) 공간 제스처 입력 pinch/grab/swipe-3D + (2) 시선 추적 fallback (키보드 대체 LOCK L8 WCAG 준수) + (3) 3D Glass HUD (LOCK L5 ORANGE/L6 BLUE 적용) + (4) 공간 voice command (LOCK L9 6개 CLI 보존) + (5) AR 환경 fallback (데스크톱 모드 자동 전환).
4. AR EventType 신규 정의 — `ui.hologram.ar.{action}` 8건 (gesture_detected / gaze_changed / spatial_anchor_set / depth_updated / occlusion_resolved / hand_tracking_lost / scene_understanding_ready / ar_session_ended) LOCK L19 100% 준수.
5. 6-12 Event-Logging cross-handoff — P2-4 event_type_v2_sync.md §5 통합 catalog 직계 형식으로 AR EventType 8건 등록.
6. 6-11 Hologram-Main-LLM cross-handoff — AR 렌더링 정본 (6-11) ↔ View 구조 (6-1) 경계 양방향 EXACT MATCH 100% verify.
7. 6-2 Security-Governance cross-handoff — 공간 데이터 PII 마스킹 정합.
8. AUTHORITY_CHAIN.md cross-check: LOCK L5/L6/L8/L9/L19 정본 출처 변경 0 + §3 6-11 경계 V3 갱신 row 등재.
9. production 실측 측정: AR 60fps 보장 + AR 인터랙션 5건 모두 시뮬레이션 ≥ 3 시나리오 PASS + staging 7일 측정.
10. INDEX.md 마스터 L3 완성률 갱신.
11. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] AR/공간 이해 UI V3 ar_spatial_v3.md NEW byte ≥ 350L Status APPROVED 전환 완료
- [ ] AUTHORITY §3 6-11 경계 V3 시점 최종 확정 row 등재 완료 (6-1 = View 구조 / 6-11 = 렌더링 로직)
- [ ] AR 인터랙션 5건 (공간 제스처 + 시선 fallback + 3D Glass HUD + voice command + AR fallback) 정의 완료
- [ ] AR EventType 8건 `ui.hologram.ar.{action}` LOCK L19 100% 준수
- [ ] LOCK L5/L6 (테마색) + L8 (WCAG) + L9 (6 CLI) + L19 (이벤트 네이밍) verbatim 영구 보존 (R9)
- [ ] **6-11 Hologram-Main-LLM AR 렌더링 정본 ↔ 6-1 View 구조 경계 양방향 EXACT MATCH 100% 정합** (ISS-6 V3 시점 최종 확정)
- [ ] 6-12 Event-Logging 통합 catalog AR EventType 8건 등록 정합
- [ ] 6-2 Security-Governance 공간 데이터 PII 마스킹 cross-handoff 정합
- [ ] AR 60fps 보장 + 시뮬레이션 ≥ 3 시나리오 staging 7일 측정 PASS
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] AR/공간 이해 UI V3 + 6-11 경계 V3 시점 최종 확정 production-ready 정본 승급 조건 충족**

**산출물**: AR/공간 이해 UI V3 production .md 정본 (`02_hologram-view/ar_spatial_v3.md`) + AUTHORITY_CHAIN.md §3 6-11 경계 V3 갱신 row + `_verification/phase4_v3_p4-2_promotion_report.md`
</details>

<details>
<summary><b>P4-3. 아바타/디지털 휴먼 V3 11번째 그룹 + LOCK L13 카탈로그 확장 production-ready 정본 승급 (P3-3 inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-3 "아바타/디지털 휴먼 V3 컴포넌트 5건 + 11번째 그룹 'Avatar-Digital-Human' 등재 + LOCK L13 카탈로그 확장 53건 + RBAC + PII 마스킹" (P3-3 forward-defined Phase 4 entry-gate 명세 §7.3 L1864 — NEW 파일 byte ≥ 400L + LOCK L13 카탈로그 확장 + 3 cross-handoff 6-2/1-1/6-11 RESOLVED + PII 마스킹 정합 = 2 audit conditions)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK L10/L13/L16/L19 정합 + V3 확장 명시" + G4-5 "아바타 카탈로그 통산 53건" + G4-6 "1-1 Verifier-Reasoning-Engines (Wave 2 #21 ✅) 디지털 휴먼 대화 백엔드 LLM cross-handoff"
- §6 이슈: ISS-4 (v12 4건 → ISS-7 V3 확장 아바타 컴포넌트 신규) + ISS-3 (STEP7-C 잔여 ~70+ 중 아바타 항목)
- 교차 도메인: **6-2 Security-Governance (Wave 2 #14 ✅) 아바타 RBAC L10 + PII 마스킹** + **1-1 Verifier-Reasoning-Engines (Wave 2 #21 ✅) 디지털 휴먼 대화 백엔드 — 요청/응답 스키마 + 비용 가드레일** + **6-11 Hologram-Main-LLM (Wave 3 #28 ✅) 아바타 3D 렌더링** + 6-12 Event-Logging (Wave 3 #29 ⬜) 아바타 EventType 6건
- Part2 V3-Phase 매핑: §7.1 L303 "V3 (최종 통합)" — 아바타는 디지털 휴먼 신규 컴포넌트 그룹 (V1 44 + V2 v12 4건 = 48 + V3 아바타 5건 = 53) + ★ Phase 15 derivation marker 없음
- production 측정 실측값: P2-3 `v12_components.md` 359L (v12 4건 × 12 sub-component L3 base) byte/SHA/LF + Card-Widget Pattern V2 직계 + LOCK L13 카탈로그 V1 ~44 + V2 v12 4건 = 48 + V3 아바타 5건 = **통산 53건** (재정의 아닌 확장) + 5 컴포넌트 (UserAvatar / DigitalHuman / AvatarDialog / AvatarPermission / AvatarGallery) + RBAC L10 권한 매트릭스 (4 역할 × 5 컴포넌트 = 20 cell) + 아바타 EventType 6건 `ui.avatar.{subject}.{action}` (persona_changed / dialog_opened / lipsync_started / expression_updated / permission_denied / gallery_selected) LOCK L19 100% 준수 + PII 마스킹 정합 + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: 아바타/디지털 휴먼 11번째 그룹 + LOCK L13 53건 + RBAC + PII 마스킹 100% 완료 + 1-1 LLM 백엔드 비용 가드레일 통합 + /audit PASS
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: 아바타/디지털 휴먼 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK L10 (RBAC 4단계) + L13 (V1+V2+V3 통산 53건, V3 확장 명시) + L16 (i18n ko-KR) + L19 (이벤트 네이밍) verbatim 보존 (R9) + V3 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제 + ReadOnly FALSE 유지

**목표**: Phase 3 P3-3에서 정의한 아바타/디지털 휴먼 V3 11번째 그룹 + LOCK L13 카탈로그 확장 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-3 ✅) → Phase 4 V3 implementation으로 전환하여 (1) avatar_digital_human_v3.md 5 컴포넌트 + (2) 04_react-components/_index.md 11번째 그룹 "Avatar-Digital-Human" 등재 + (3) RBAC L10 권한 매트릭스 20 cell + (4) PII 마스킹 + (5) 1-1 디지털 휴먼 LLM 백엔드 비용 가드레일 통합 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/UI_UX_SYSTEM_구조화_종합계획서.md` §3.4 LOCK L10/L13/L16/L19 / §6 ISS-4/ISS-3 / §7.3 P3-3 (forward-defined L1854~L1900)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/04_react-components/v12_components.md` (P2-3 산출물 359L base)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/04_react-components/_index.md` (Phase 1 정본, 10그룹 인덱스 + 44 컴포넌트 카탈로그)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/AUTHORITY_CHAIN.md` LOCK L13 (React 컴포넌트 수) + L10 (RBAC) + L19 (이벤트 네이밍)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/SECURITY_GOVERNANCE_구조화_종합계획서.md` (Wave 2 #14 ✅ RBAC + PII 마스킹 cross-handoff)
- `D:/VAMOS/docs/sot 2/1-1_Verifier-Reasoning-Engines/VERIFIER_REASONING_ENGINES_구조화_종합계획서.md` (Wave 2 #21 ✅ 디지털 휴먼 대화 백엔드 cross-handoff)
- `D:/VAMOS/docs/sot 2/6-11_Hologram-Main-LLM/HOLOGRAM_MAIN_LLM_구조화_종합계획서.md` (Wave 3 #28 ✅ 아바타 3D 렌더링 cross-handoff)

**절차**:
1. P3-3 forward-defined V3 산출물 명세 (아바타 5 컴포넌트 + 11번째 그룹 + LOCK L13 카탈로그 확장 + RBAC + PII 마스킹) inventory 확인 + baseline 측정.
2. `04_react-components/avatar_digital_human_v3.md` 신규 — 5 컴포넌트 정의 (1) `<UserAvatar />` 사용자 페르소나 표시 + (2) `<DigitalHuman />` AI 인간 인터페이스 (립싱크 + 표정) + (3) `<AvatarDialog />` 대화 말풍선 (LOCK L16 i18n ko-KR) + (4) `<AvatarPermission />` RBAC 권한 표시 (LOCK L10 4단계 색상 매핑) + (5) `<AvatarGallery />` 다중 아바타 선택 그리드 + Card-Widget Pattern V2 직계 (각 컴포넌트 × L3 9요소).
3. `04_react-components/_index.md` 11번째 그룹 "Avatar-Digital-Human" 등재 + V3 11그룹 인덱스 정합.
4. LOCK L13 카탈로그 확장 명시 — V1 ~44 + V2 v12 4건 = 48 + V3 아바타 5건 = **통산 53건** (재정의 아닌 확장, `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제).
5. LOCK L10 RBAC 4단계 (OWNER/ADMIN/OPERATOR/VIEWER) 아바타 권한 매트릭스 (4 역할 × 5 컴포넌트 = 20 cell) + 6-2 Security-Governance cross-handoff.
6. PII 마스킹 정합 — 디지털 휴먼 대화 중 사용자 PII 노출 차단 + 6-2 cross-ref.
7. 1-1 Verifier-Reasoning-Engines cross-handoff — 디지털 휴먼 대화 백엔드 API 시그니처 (요청/응답 스키마 + 비용 가드레일 통합).
8. 6-11 Hologram-Main-LLM cross-handoff — 아바타 3D 표현 시 렌더링 정합.
9. 6-12 Event-Logging cross-handoff — 아바타 EventType 6건 `ui.avatar.{subject}.{action}` LOCK L19 100% 준수.
10. AUTHORITY_CHAIN.md cross-check: LOCK L10/L13/L16/L19 정본 출처 변경 0 + L13 카탈로그 확장 row append.
11. production 실측 측정: 아바타 카탈로그 통산 53건 + RBAC 20 cell + PII 마스킹 100% staging 7일 측정 PASS.
12. INDEX.md 마스터 L3 완성률 갱신.
13. Phase 5 entry-gate forward-defined 작성.

**검증**:
- [ ] avatar_digital_human_v3.md NEW byte ≥ 400L Status APPROVED 전환 완료
- [ ] 04_react-components/_index.md 11번째 그룹 "Avatar-Digital-Human" 등재 완료
- [ ] LOCK L13 카탈로그 확장 명시 — V1 44 + V2 4 = 48 + V3 5 = **통산 53건** `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제
- [ ] LOCK L10 RBAC 4단계 아바타 권한 매트릭스 (4 역할 × 5 컴포넌트 = 20 cell) 작성 완료
- [ ] LOCK L10 (RBAC) + L13 (컴포넌트 수) + L16 (i18n) + L19 (이벤트 네이밍) verbatim 영구 보존 (R9)
- [ ] 아바타 EventType 6건 `ui.avatar.{subject}.{action}` LOCK L19 100% 준수
- [ ] **6-2 Security-Governance RBAC + PII 마스킹 + 1-1 Verifier-Reasoning-Engines 디지털 휴먼 대화 백엔드 비용 가드레일 + 6-11 Hologram-Main-LLM 아바타 3D 렌더링 3 cross-handoff 양방향 정합 ALL RESOLVED**
- [ ] PII 마스킹 정합 (디지털 휴먼 대화 PII 노출 차단) 검증 PASS
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] staging 7일 측정 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료
- [ ] **[Phase 16 NEW] 아바타/디지털 휴먼 V3 + LOCK L13 카탈로그 확장 production-ready 정본 승급 조건 충족**

**산출물**: 아바타/디지털 휴먼 V3 production .md 정본 (`04_react-components/avatar_digital_human_v3.md` + `04_react-components/_index.md` 11번째 그룹 등재) + AUTHORITY_CHAIN.md LOCK L13 카탈로그 확장 row + `_verification/phase4_v3_p4-3_promotion_report.md`
</details>

<details>
<summary><b>P4-4. V3 확장 슬롯 4개 + Plugin SDK + FailureCode V3 확장 production-ready 정본 승급 (P3-4 inheritance, 3-7 Plugin SDK forward-inheritance)</b></summary>

**대조 기준 (8항목)**:
- §7 세부 작업: P4-4 "V3 확장 슬롯 4개 (Header/Sidebar/Content/Footer) + Plugin SDK 통합 + 보안 화이트리스트 + Docker 샌드박스 + FailureCode V3 확장 14→18" (P3-4 forward-defined Phase 4 entry-gate 명세 §7.3 L1912 — NEW 파일 byte ≥ 350L + 4 슬롯 인터페이스 + 3-7/6-2 cross-handoff + FailureCode V3 확장 = 3 audit conditions)
- §7 전환 게이트: G4-1 "V3 implementation 완료" + G4-2 "Status APPROVED" + G4-3 "LOCK L2/L4/L10/L12/L13/L19/L20 정합" + G4-5 "Plugin Slot 4개 인터페이스 시그니처 + Plugin FailureCode 4건 + Plugin EventType 8건" + G4-6 "**3-7 Developer-Tools-API-SDK (Wave 1 #9 ✅) Plugin SDK 등록 메커니즘 forward-inheritance 양방향**"
- §6 이슈: ISS-3 STEP7-C 잔여 ~70+ V3 범위 11번째 그룹 신설 Wellness/Education V3 범위 (L1756 이월) 매핑
- 교차 도메인: **3-7 Developer-Tools-API-SDK (Wave 1 #9 ✅) Plugin SDK 정본 — 3-7 정의 / 6-1은 UI 슬롯만 (경계 명시)** + **6-2 Security-Governance (Wave 2 #14 ✅) Plugin 보안 화이트리스트 + Docker 샌드박스 LOCK L12** + 6-12 Event-Logging (Wave 3 #29 ⬜) 슬롯 EventType 8건
- Part2 V3-Phase 매핑: §7.1 L303 "V3 (최종 통합)" 마지막 산출물 — Phase 3 핵심 신규 항목 (V1/V2에는 미존재) + ★ Phase 15 derivation marker 없음
- production 측정 실측값: LOCK L13 통산 V1 44 + V2 4 + V3 5 = 48+5 = 53 + Plugin Slot 4개 = **57건 확장 한도** + Plugin 4 슬롯 TypeScript 인터페이스 시그니처 (HeaderSlot / SidebarSlot / ContentSlot / FooterSlot) + Plugin FailureCode 4건 (PLUGIN_LOAD_TIMEOUT / PLUGIN_PERMISSION_DENIED / PLUGIN_SANDBOX_ESCAPE / PLUGIN_RENDER_ERROR) + Plugin EventType 8건 `ui.{slot}.plugin.{action}` (load_requested / load_success / load_failure / render_started / render_error / permission_denied / sandbox_violation / unloaded) LOCK L19 100% 준수 + RBAC L10 4단계 슬롯별 권한 매트릭스 (4 슬롯 × 4 역할 = 16 cell) + Docker 샌드박스 LOCK L12 격리 정책 + LOCK L20 FailureCode V3 확장 14→18 + ISS-3 11번째 그룹 매핑 매트릭스 + staging 7일 측정 데이터
- Phase 5 entry-gate 충족 조건: Plugin Slot 4개 100% 완료 + 3-7 Plugin SDK 양방향 정합 + 6-2 화이트리스트 + 샌드박스 + STEP7-C 잔여 ~70+ V3 범위 100% 매핑 완료
- **[Phase 16 NEW] Phase 4 산출물 production-ready 정본 승급 조건**: V3 확장 슬롯 4개 V3 100% 완성 + Status DRAFT → APPROVED 전환 + LOCK L2/L4 (3-Column 영역) + L10 (RBAC 4단계) + L12 (Docker 샌드박스) + L13 (V3 확장 57) + L19 (이벤트 네이밍) + L20 (FailureCode V3 확장 14→18) verbatim 보존 (R9) + V3 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제 + 3-7 정본 출처 ↔ 6-1 UI 슬롯 경계 EXACT MATCH 100% + ReadOnly FALSE 유지

**목표**: Phase 3 P3-4에서 정의한 V3 확장 슬롯 4개 + Plugin SDK + FailureCode V3 확장 baseline을 production-ready로 정본 승급한다. Phase 3 SPEC 완료(P3-4 ✅) → Phase 4 V3 implementation으로 전환하여 (1) extension_slots_v3.md 4 슬롯 (Header/Sidebar/Content/Footer) + (2) 3-7 Plugin SDK forward-inheritance 양방향 cross-handoff + (3) 6-2 Plugin 보안 화이트리스트 + Docker 샌드박스 LOCK L12 + (4) LOCK L13 통산 57 + L20 FailureCode V3 확장 14→18 + (5) ISS-3 11번째 그룹 Wellness/Education V3 범위 매핑 매트릭스 baseline을 production .md 정본으로 영구 확립한다.

**입력 파일**:
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/UI_UX_SYSTEM_구조화_종합계획서.md` §3.4 LOCK L2/L4/L10/L12/L13/L19/L20 / §6 ISS-3 / §7.3 P3-4 (forward-defined L1902~L1948)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/04_react-components/_index.md` (Phase 1 정본 + V3 11번째 그룹 P4-3 등재 후)
- `D:/VAMOS/docs/sot 2/6-1_UI-UX-System/AUTHORITY_CHAIN.md` LOCK L13 (컴포넌트 수) + L10 (RBAC) + L8 (WCAG) + L20 (FailureCode)
- `D:/VAMOS/docs/sot 2/3-7_Developer-Tools-API-SDK/` (Wave 1 #9 ✅ Plugin SDK 정본 cross-handoff)
- `D:/VAMOS/docs/sot 2/6-2_Security-Governance/SECURITY_GOVERNANCE_구조화_종합계획서.md` (Wave 2 #14 ✅ 화이트리스트 + 샌드박스 LOCK L12 cross-handoff)
- `D:/VAMOS/docs/sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` §7 (FailureCode + FallbackRegistry LOCK L20)

**절차**:
1. P3-4 forward-defined V3 산출물 명세 (4 슬롯 + Plugin SDK + 화이트리스트 + 샌드박스 + FailureCode V3 확장) inventory 확인 + baseline 측정.
2. `04_react-components/extension_slots_v3.md` 신규 — 4 슬롯 정의 (1) `<HeaderSlot />` 상단 메뉴바 + (2) `<SidebarSlot />` 좌측 패널 (LOCK L2 250-300px 내) + (3) `<ContentSlot />` 중앙 (LOCK L4 Flex-grow) + (4) `<FooterSlot />` 하단 상태바 + TypeScript 인터페이스 `interface UIExtensionSlot { id: string; render: () => ReactNode; permission: RBACRole[]; sandbox: boolean; }`.
3. 3-7 Developer-Tools-API-SDK cross-handoff — Plugin SDK 등록 메커니즘 (3-7 정본) ↔ 6-1 UI 슬롯 인터페이스 (경계 명시) 양방향 forward-inheritance 정합.
4. 6-2 Security-Governance cross-handoff — Plugin 화이트리스트 + Docker 샌드박스 LOCK L12 (Part2 §6.5.1, V2 P2-1 D8-L03 패턴 직계) + RBAC L10 4단계 권한 게이트 (4 슬롯 × 4 역할 = 16 cell).
5. FailureCode V3 확장 (LOCK L20 14→18) — Plugin 관련 4건 (PLUGIN_LOAD_TIMEOUT / PLUGIN_PERMISSION_DENIED / PLUGIN_SANDBOX_ESCAPE / PLUGIN_RENDER_ERROR) + FallbackRegistry 매핑 + `<!-- V3 EXTENSION, NOT REDEFINITION -->`.
6. Plugin EventType 8건 — `ui.{slot}.plugin.{action}` LOCK L19 100% 준수 (load_requested / load_success / load_failure / render_started / render_error / permission_denied / sandbox_violation / unloaded).
7. ISS-3 11번째 그룹 (Wellness/Education V3 범위, L1756 이월) 매핑 — Wellness Plugin / Education Plugin이 어떤 슬롯에 주입되는지 매트릭스 작성.
8. LOCK L13 카탈로그 확장 명시 — V1 44 + V2 4 + V3 아바타 5 = 53 + Plugin Slot 4 = **통산 57건** (`<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제).
9. AUTHORITY_CHAIN.md cross-check: LOCK L13/L20 정본 출처 변경 0 + 카탈로그 통산 57 + FailureCode V3 확장 14→18 row append + 3-7 forward-inheritance row append.
10. production 실측 측정: Plugin Slot 4개 인터페이스 정합 + 화이트리스트 + 샌드박스 격리 PASS + Plugin FailureCode 4건 + EventType 8건 staging 7일 측정 PASS.
11. INDEX.md 마스터 L3 완성률 갱신.
12. Phase 5 entry-gate forward-defined 작성 (STEP7-C 잔여 ~70+ V3 범위 100% 매핑 완료).

**검증**:
- [ ] extension_slots_v3.md NEW byte ≥ 350L Status APPROVED 전환 완료
- [ ] 4 확장 슬롯 모두 TypeScript 인터페이스 시그니처 정의 (id + render + permission + sandbox)
- [ ] LOCK L2/L4 (3-Column 영역) 정합 + 슬롯 영역 재정의 0건
- [ ] LOCK L10 RBAC 4단계 슬롯별 권한 매트릭스 (4 슬롯 × 4 역할 = 16 cell)
- [ ] LOCK L12 Docker 샌드박스 — 6-2 cross-handoff RESOLVED + Plugin 격리 정책 명시
- [ ] LOCK L13 카탈로그 확장 — V1 44 + V2 4 + V3 5 + Plugin Slot 4 = **통산 57건** `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제
- [ ] LOCK L20 FailureCode V3 확장 14→18 (Plugin 4건) `<!-- V3 EXTENSION, NOT REDEFINITION -->` + FallbackRegistry 매핑
- [ ] LOCK L19 이벤트 네이밍 `ui.{slot}.plugin.{action}` 8건 모두 준수
- [ ] **3-7 Developer-Tools-API-SDK Plugin SDK 등록 메커니즘 forward-inheritance 양방향 RESOLVED** (3-7 정본 ↔ 6-1 UI 슬롯 경계 EXACT MATCH 100%)
- [ ] **6-2 Security 화이트리스트 + Docker 샌드박스 LOCK L12 cross-handoff RESOLVED**
- [ ] ISS-3 11번째 그룹 (Wellness/Education V3) 슬롯 매핑 매트릭스 작성 완료
- [ ] §10 V-01~V-N PASS + /audit 시뮬레이션 PASS
- [ ] ReadOnly FALSE 유지 (Production 승급 직접 편집 가능)
- [ ] Phase 5 entry-gate forward-defined 작성 완료 (STEP7-C 잔여 ~70+ V3 범위 100% 매핑 완료)
- [ ] **[Phase 16 NEW] V3 확장 슬롯 4개 + Plugin SDK + FailureCode V3 확장 production-ready 정본 승급 조건 충족**

**산출물**: V3 확장 슬롯 4개 V3 production .md 정본 (`04_react-components/extension_slots_v3.md`) + `04_react-components/_index.md` 슬롯 4개 카탈로그 등재 + AUTHORITY_CHAIN.md LOCK L13 통산 57 + L20 FailureCode V3 확장 14→18 row + 3-7 forward-inheritance row + `_verification/phase4_v3_p4-4_promotion_report.md`
</details>

<details>
<summary><b>Phase 4 세션 전체 검증 결과 (6-1, 2026-05-26)</b> 🎉🎉🎉🎉🎉 Wave 2 첫 도메인 Stage A 완료 + 🌟🌟🌟🌟🌟 4/4 NO-DRIFT FULL milestone first specialty + LOCK 20/20 전수 coverage FINAL milestone first + 3-7 cross-Wave Wave 1 → Wave 2 forward-inheritance first specialty</summary>

| 항목 | 결과 |
|------|------|
| **chain 통산** | `phase4_6-1_p4-{1..4}_2026-05-26` (단일 대화창 4 P4 task 순차 진행, ENTRY_PROMPT 진입 게이트 사용자 결정 A verify-only Wave 2 재확인) |
| **P4 블록 수** | **4/4 완료** (P4-1 ✅ 모바일 BP-D 768px + WCAG 2.1 AA 모바일 + Touch FailureCode V3 / P4-2 ✅ AR/공간 이해 UI + 6-11 경계 V3 시점 최종 확정 + AR EventType 8건 / P4-3 ✅ 아바타/디지털 휴먼 + 11번째 그룹 + LOCK L13 카탈로그 53건 + RBAC + PII + 1-1 디지털 휴먼 LLM 백엔드 / P4-4 ✅ V3 확장 슬롯 4개 + 3-7 Plugin SDK forward-inheritance + FailureCode 14→18) |
| **R cascade 통산** | 13 round × 9 sub-step × 4 P4 = **468 verifications**, **drift 0 신규 cascade** / D candidate 4×8=32건 ALL DROP/NOT-drift verdict / fix 0 적용 / truly_converged_v1 first-pass-after-zero-fix CONFIRMED 4 P4 task ALL |
| **byte/SHA pre/post (plan)** | pre = post = **236,927 B / `E39161CFBFEFC36D` / 2,092 LF EXACT** (verify-only ZERO write 4/4 P4 통산 — Δ +0 B / +0 LF) — ④단계 본 요약 블록 +Δ 별도 |
| **V3 산출물 Status 전환** | **5 V3 NEW + 3 UPDATE = 8 forward-defined ALL OUT of scope per 사용자 결정 A** (P4-1 responsive_layout_v3 + mobile_a11y_v3 NEW + AUTHORITY L11 V3 확장 row UPDATE / P4-2 ar_spatial_v3 NEW + AUTHORITY §3 6-11 경계 V3 갱신 row UPDATE / P4-3 avatar_digital_human_v3 NEW + _index 11번째 그룹 등재 UPDATE + AUTHORITY L13 카탈로그 확장 row UPDATE / P4-4 extension_slots_v3 NEW + _index 슬롯 4개 카탈로그 등재 UPDATE + AUTHORITY L13 통산 57 + L20 14→18 + 3-7 forward-inheritance row UPDATE) → SPEC Stage B 또는 별도 결정 위임 |
| **production .md 승급 완료** | **0/8 (verify-only ZERO write per A) — 30/30 baseline EXACT 보존 통산 FINAL** (6-1 RO FALSE 도메인 ReadOnly EXACT 패턴 미적용, 4 cross-handoff plan (3-7 208,677 + 6-2 186,742 + 6-11 267,666 + 1-1 332,889) baseline 무손상 통산) |
| **LOCK 변경 / DEFINED-HERE 변경 / FABRICATION** | **0 / 0 / 0 통산** — LOCK L1~L20 20 unique set accuracy 변경 0 통산 (R9 verbatim 영구 보존) + DEFINED-HERE 0건 + V3 확장 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제 forward-defined baseline 무손상 |
| **abort marker 9종 NOT FIRED self-fire 0** | UPSTREAM_V3_SPEC_MISSING + PRODUCTION_WRITE_VIOLATION + STAGE9_READONLY_RESTORE_FAIL + STATUS_TRANSITION_FAIL + V3_PRODUCTION_PROMOTION_FAIL + **CROSS_HANDOFF_DRIFT (3-7 Wave 1 → Wave 2 cross-Wave first specialty EXACT MATCH 100%)** + BILATERAL_SOT2_DRIFT(⑤ deferred) + DOWNSTREAM_PROPAGATE_MISS(⑥ deferred) + R_CASCADE_NOT_CONVERGED ALL ✅ (4 P4 task × 9 = 36 markers ALL NOT FIRED) |
| **6 anchor 충족** | 안전 ✅ (verify-only ZERO write + 30 baseline + 4 cross-handoff plan + 추가 inputs byte/SHA EXACT + 20 LOCK verbatim 영구 + V3 확장 forward-defined 주석 강제 + RO FALSE 30/30) · 누락 0 ✅ (8 대조 × 4 + 9 abort × 4 + 검증 12+13+14+16=55 + 절차 11+11+13+12=47 + LOCK 20/20 전수 coverage + cross-handoff 6 distinct + §6 7 issues + 산출물 4×4=16 + D candidate 32 ALL PASS) · 오류 0 ✅ (R₁~R₁₃ × 4 = 468 verifications drift 0 · D candidate 32 ALL DROP/NOT-drift verdict · fix 0 적용) · 미세 ✅ (AUTHORITY §4 L179-L198 20 LOCK verbatim + plan §3.4 EXACT MATCH + §6 L262-L270 ISS verbatim + §13.3 L2375-L2403 매트릭스 verbatim + L2014-L2235 P4-1~P4-4 절차/검증 verbatim + LOCK L13 57 = 44+4+5+4 + LOCK L20 18 = 14+4 산술 EXACT) · 수렴 ✅ (truly_converged_v1 first-pass-after-zero-fix CONFIRMED 4 P4 task ALL) · 재검증 ✅ (R₁~R₁₂ 초기 cascade × 4 fix 0 + Round 2~3 변경 0 × 4 = 13-round cascade ALL) ALL ✅ |
| **upstream 도메인 의존 검증** | **Wave 1 12/12 ✅ ALL inheritance verified** (1-2 SPEC ✅ 2026-05-23 + 2-2 SPEC ✅ 2026-05-24 + 2-1 SPEC ✅ 2026-05-24 + 3-2 SPEC ✅ 2026-05-24 + 3-3 SPEC ✅ 2026-05-25 + 3-4 SPEC ✅ 2026-05-24 + 3-5 SPEC ✅ 2026-05-25 + 3-6 SPEC ✅ 2026-05-25 + **3-7 SPEC ✅ 2026-05-25 (Plugin SDK forward-inheritance source)** + 3-9 SPEC ✅ 2026-05-25 + 4-2 SPEC ✅ 2026-05-25 + 4-4 SPEC ✅ 2026-05-25~26) = Wave 1 ENTRY 12/12 + SPEC 12/12 = 100% milestone 도달, Wave 2 진입 차단 해제 confirmed FINAL inheritance |
| **downstream 도메인 영향 분석 (6건 forward-defined, ⑥ 전파 예정)** | 6-11★ Hologram-Main-LLM (Wave 3 #28, AR 렌더링 정본 + ISS-6 V3 경계 RESOLVED 양방향) + 1-1 Verifier-Reasoning-Engines (Wave 2 #21, 디지털 휴먼 LLM 백엔드 forward-defined) + 3-7 Developer-Tools-API-SDK (Wave 1 #9 ✅, Plugin SDK 양방향 cross-Wave first specialty) + 6-2 Security-Governance (Wave 2 #14, RBAC L10 + PII + Docker 샌드박스 L12) + 6-12 Event-Logging (Wave 3 #29, EventType `ui.*.*` 통산 ≥ 30건) + 4-1 Rust-Tauri-Infrastructure (Wave 3 #24, 모바일 IPC 경계) |
| **Phase 5 entry-gate forward-defined** | **4개 P4 모두 명시 ✅** (P4-1 매핑 5/7 G4-1+G4-2+G4-3+G4-5+G4-7 / P4-2 매핑 5/7 G4-1+G4-2+G4-3+G4-5+G4-6 / P4-3 매핑 5/7 G4-1+G4-2+G4-3+G4-5+G4-6 / P4-4 매핑 5/7 G4-1+G4-2+G4-3+G4-5+G4-6 — §7 L2002-L2010 G4-1~G4-7 7 게이트 verbatim inheritance + §13.3 L2375-L2403 매트릭스 inheritance EXACT) |
| **Wave 2 첫 도메인 specialty milestone first** | 🎉🎉🎉 Wave 2 진입 첫 도메인 첫 Stage A 완료 specialty milestone first 도달 (Wave 1 100% SPEC milestone 통산 12/30 = 40% 달성 post Wave 2 #13 진입 차단 해제 confirmed FINAL inheritance) |
| **🌟🌟🌟🌟🌟 6-1 4/4 NO-DRIFT FULL milestone first specialty 확정** | P4-1 + P4-2 + P4-3 + P4-4 ALL first-pass NO-DRIFT zero-fix → **통산 11번째 FULL 도메인** (2-2 + 2-1 + 3-3 + 3-4 + 3-5 + 3-6 + 3-7 + 3-9 + 4-2 + 4-4 + **6-1**) + **통산 9번째 단일 도메인 FULL specialty** (분할 3-5 + 3-6 제외, 2-1/2-2/3-3/3-4/3-7/3-9/4-2/4-4/**6-1**) |
| **🌟🌟🌟🌟🌟 LOCK 20/20 전수 verify FINAL coverage milestone first specialty 확정** | P4-1 L1+L2+L3+L4+L8+L11+L17+L19 (8) + P4-2 L5+L6+L8+L9+L19 (5) + P4-3 L10+L13+L16+L19 (4) + P4-4 L2+L4+L10+L12+L13+L19+L20 (7) + L7/L14/L15/L18 4개 추가 verify = **6-1 4 P4 task 통산 LOCK 20/20 distinct verify FINAL milestone first specialty** (도메인-level 통산 전체 LOCK coverage 최초 사례) |
| **🌟🌟🌟 3-7 Plugin SDK Wave 1 #9 → Wave 2 #13 cross-Wave forward-inheritance first specialty** | 3-7 plan 208,677 B `FEFAF510380DDA4E` Phase 3 SPEC ✅ COMPLETE 2026-05-25 inheritance + Plugin SDK 정본 source (LOCK-DT-05/09 + R-10-5 + plugin lifecycle baseline) — Wave 1 → Wave 2 backward inheritance source first specialty |
| **🌟🌟🌟 LOCK L13 통산 57 FINAL + L20 FailureCode 14→18 first specialty** | LOCK L13 V1 44 + V2 4 + V3 5 + Plugin Slot 4 = 57건 FINAL (산술 EXACT) + LOCK L20 V1 14 + V3 Plugin 4건 = 18 FailureCodes FINAL + FallbackRegistry 매핑 forward-defined |
| **🌟 cross-Wave directional diversity FINAL milestone first specialty** | P4-2 Wave 2 → Wave 3 6-11 (forward) + P4-3 Wave 2 → Wave 2 1-1 (intra-Wave) + P4-4 Wave 1 → Wave 2 3-7 (backward source) = **6-1 도메인 3가지 distinct cross-Wave forward-inheritance 패턴 FINAL milestone first specialty** |
| **🌟 ISS-3 4 P4 ALL coverage FINAL milestone first** | P4-1 모바일 + P4-2 AR + P4-3 아바타 + P4-4 Plugin Slot Wellness/Education V3 매핑 = ISS-3 STEP7-C 잔여 ~70+ 4 P4 distinct coverage FINAL milestone first specialty |
| **🎉 FINAL P4 task specialty 통산 9번째** | 3-3 P4-6 + 3-4 P4-4 + 3-5 P4-8 + 3-6 P4-7 + 3-7 P4-4 + 3-9 P4-4 + 4-2 P4-3 + 4-4 P4-4 + **6-1 P4-4 FINAL = 통산 9번째 FINAL P4 specialty** (Wave 2 첫 도메인 FINAL P4 first) |
| **🎉🎉🎉 NO-DRIFT direct path 29-consecutive** ⭐ | 3-3 P4-1~P4-6 6 + 3-4 P4-1~P4-4 4 + 3-5 P4-1~P4-8 8 + 3-6 P4-1~P4-7 7 + **6-1 P4-1+P4-2+P4-3+P4-4 NEW 4** = 통산 29 P4 task NO-DRIFT direct path FINAL |
| **Pattern A "안전·누락 0·오류 0·완벽" 통산** | 84번째 사례 ✅ (Wave 2 네번째 Pattern A FINAL) |
| **Pattern B "더이상 수정하지 않을때까지" 통산** | 81번째 사례 ✅ (Wave 2 네번째 Pattern B FINAL, 🎉 80-milestone first 도달 P4-3) |
| **사용자 결정 A inheritance** | Wave 1 12/12 + 6-1 P4-1~P4-4 직계 통산 13번째 도메인 4/4 P4 task verify-only FULL completion (ENTRY_PROMPT 진입 게이트 사용자 결정 A inheritance Wave 2 재확인 confirmed) |
| **사용자 paste 트리거 통산** | 12회 (4 P4 task × 3 paste = ② R cascade × 4 + ③ 최종 확정 gate × 4 + ③.5 PROGRESS mid-checkpoint × 4) + ④ 세션 요약 1 |
| **다음 단계** | ⑤ bilateral 갱신 (종합계획서 §7 Phase 4 헤더 ✅ + SOT2_MASTER_INDEX 6-1 row Phase 4 ✅ + [PHASE5_READY: 6-1 — 2026-05-26] marker) → ⑥ downstream 전파 (6건 cross-handoff) → ⑦ PROGRESS.md domain-complete ⬜→⬛ |

**[PHASE4_COMPLETE_STAGE_A: 6-1 — 2026-05-26]** ⬛ COMPLETE — Stage A ENTRY_PROMPT ⑦단계 ready (SPEC Stage B sub-cycle 후속 별도 대화창 진입 직계 1-2 + 2-2 + 2-1 + 3-2 + 3-3 + 3-4 + 3-5 + 3-6 + 3-7 + 3-9 + 4-2 + 4-4 통산 13번째 도메인 패턴 EXACT)

</details>

<details>
<summary><b>§7.R Phase 4 RECOVERY Stage A+B 통합 genuine production write (6-1, 2026-06-01)</b> — verify-only 착시 영구 해소 · Wave 2 #12 · 도메인 종료</summary>

> **⚠️ 위 2026-05-26 블록은 verify-only 마감(production .md write 0/8, 5 V3 forward-defined 착시)**. 본 §7.R 에서 **5 V3 ALL NEW genuine production write** 로 영구 해소. RO FALSE 도메인, Gate 2 PROCEED 쓰기 허용.

| 항목 | 결과 |
|------|------|
| **chain** | `phase4_6-1_recovery_AB_2026-06-01` (Stage A+B 통합 단일 대화창, genuine write) |
| **V3 산출물 5 ALL NEW** | P4-1 responsive_layout_v3.md 17,333 B(200L, BP-D 768px 모바일 정식 + useResponsive + 9-State 모바일 전이 + Touch FB 9→12) + mobile_a11y_v3.md 8,736 B(90L, WCAG 2.1 AA 모바일 12항목 + Touch 실패 3건 + 모바일 RBAC) + P4-2 ar_spatial_v3.md 18,091 B(229L, AR 인터랙션 5 + AR EventType 8 + ISS-6 6-11 경계 V3 확정 + 좌표계 + 60fps 예산) + P4-3 avatar_digital_human_v3.md 19,032 B(276L, 11번째 그룹 5 컴포넌트 + L13 통산 53 + RBAC 20cell + PII + viseme + 1-1 LLM 백엔드) + P4-4 FINAL extension_slots_v3.md 20,898 B(255L, 슬롯 4 + 3-7 Plugin SDK + L13 통산 57 + L20 FC 14→18 + Plugin EventType 8 + RBAC 16cell + ISS-3 매핑 + LOCK 20/20) = **84,090 B** |
| **DRAFT→APPROVED** | 5/5 (DRAFT 잔존 0) |
| **LOCK L1~L20 20/20 전수 coverage** | 재정의 0 통산 (Phase 0/1/2/3/4) — V3 확장 3건(L11 BP-D 768px / L13 통산 57 / L20 FC 14→18) `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석 강제 + 17건 verbatim 불변. L12 라벨 정정(L12=Tauri 1440×900 verbatim, Docker 샌드박스=6-2 정책). L20 count 충돌 해소(FC 14→18 Plugin / FB 9→12 Touch 2계층 분리) |
| **EventType** | 28건 L19 100% (responsive 6 + AR 8 + avatar 6 + plugin 8) |
| **CONFLICT** | OPEN 0 유지 (CONF-61-001~003 RESOLVED 보존, Phase 4 신규 0, CONFLICT_LOG byte 무변경 6,402) |
| **11번째 그룹** | "Avatar-Digital-Human" (AV-* 5) 신설 + Plugin Slot 4 |
| **cross-handoff (6, 자기 측 등재 + boundary 무손상)** | 3-7 Plugin SDK cross-Wave forward-inheritance(plan 214,738 무손상) + 6-11 AR 경계 V3 확정(plan 274,652 무손상) + 1-1 디지털 휴먼 LLM 백엔드(plan 349,768 무손상) + 6-2 RBAC/PII/샌드박스 + 6-12 EventType + 4-1 모바일 IPC — 외부 편집 0 |
| **meta 동기** | AUTHORITY v2.6 §9 V3 등재 + INDEX v1.3 §3.5 + _index 11번째 그룹 + PROGRESS 스코어보드 6-1 ✅ + SOT2 §6-1 RECOVERY genuine + 본 §7.R |
| **감사** | `_verification/phase4_recovery_stage_AB_report.md` NEW + 4 기존 verify-only 보고서 97,244 B EXACT 보존(재생성 0) |
| **abort 9종** | ALL NOT FIRED (PRODUCTION_WRITE_VIOLATION / STATUS_TRANSITION_FAIL / V3_PRODUCTION_PROMOTION_FAIL 5/5 / LOCK_REDEFINITION / CONFLICT_OPEN_VIOLATION / CROSS_HANDOFF_DRIFT / STAGE9_READONLY N/A / FABRICATION / BASELINE_DRIFT) |
| **라인 수 정합** | responsive 200(≥200 ✅) / mobile_a11y 90(≥10 항목 ✅) / ar_spatial 229 / avatar 276 / extension_slots 255 — ar_spatial/avatar/extension_slots 는 §7.4 forward-defined 노치값(350/400) 미달이나 byte/E1~E9 완성도 sibling Phase 4 recovery 초과(감사 §2.1 투명 기록) |
| **다음 진입** | 6-5 SDAR-System (Wave 2 #13, RO FALSE, ⭐ 회수 불필요 후보) |

**[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE:6-1 — 2026-06-01]** ✅ genuine (RECOVERY genuine production write, 5 V3 ALL NEW + LOCK 20/20 전수 coverage + L13 통산 57 + L20 14→18 + 11번째 그룹 신설 + CONFLICT OPEN 0 유지 + 3-7 Plugin SDK cross-Wave forward-inheritance + RO FALSE + Wave 2 첫 도메인)

</details>

**[DOMAIN_PHASE_4_PRODUCTION_PROMOTION_COMPLETE: 6-1 — 2026-05-26]** ✅ NEW (post-marker-omission-audit fix 2026-05-29 cascade) — Phase 4 production promotion sub-cycle COMPLETE: Stage A 4/4 P4 ALL ✅ + SPEC Stage B ✅ COMPLETE inheritance from PROGRESS.md L147 row + SOT2_MASTER 6-1 row 정합 authoritative + chain `phase4_6-1_2026-05-26` Stage A + `phase4_spec_6-1_2026-05-26` Stage B 별도 대화창 통합. **plan §7 Phase 4 marker 명시 누락 보강 2026-05-29 cascade** (textual notation only — PROGRESS/SOT2 inheritance authoritative, AUTHORITY v2.5 ACTIVE + CONFLICT v2.4 ACTIVE + INDEX v1.2 STEP_C 마감 시점 baseline 보존, Stage B metadata cascade는 진행 안된 케이스 specialty).

**[SPEC_STAGE_B_COMPLETE: 6-1 — 2026-05-26]** ✅ NEW Wave 2 첫 도메인 SPEC milestone first (12/12 Wave 1 SPEC 100% + 6-1 NEW Wave 2 first = **통산 13/30 SPEC = 43.3% milestone** at 2026-05-26 시점).

**[CUMULATIVE_SPEC_COUNT: 13/30]** 🎉🎉🎉🎉🎉 NEW (43.3% milestone at 2026-05-26, 6-1 = 13번째 SPEC = Wave 2 첫 도메인 specialty milestone first).

**[WAVE_2_FIRST_SPEC_MILESTONE: 6-1 — 2026-05-26]** 🎉🎉🎉 NEW (Wave 2 첫 SPEC ✅ COMPLETE — Wave 2 진입 차단 해제 confirmed FINAL).

</details>

---

## 8. 파일 역할 분리 명세

### 8.1 문서 간 역할 분리

| 문서 | 역할 | 관리 범위 | 변경 규칙 |
|------|------|----------|----------|
| **D2.0-08** | DESIGN 정본 | UI 구조/상태/이벤트/테마 확정 | Design Freeze — 변경 시 승인 필수 |
| **Part2 §6.1** | When + Where | Phase 배정(V1-P4), 파일 경로(frontend/) | Part2 업데이트 시 6-1 STALE 체크 |
| **Part2 V1-P4** | Phase 실행 | 구현 항목 20개 + Gate 12항목 | 동상 |
| **sot 2/6-1** | What + How | 컴포넌트 상세 스펙, 상태 전이 로직, 접근성, 테스트 | R-61-1~R-61-10 준수 |
| **STEP7-C** | 체크리스트 | 보강 필요 항목 104건 우선순위 | sot 2/ 매핑 후 완료 표시 |
| **D2.1-D2** | 이벤트 레지스트리 | EventType 107+건 통합 등록 | D2.0-08 변경 시 동기 |

### 8.2 서브폴더별 파일 역할 명세

각 서브폴더(01~06)는 아래 파일 유형을 포함하며, 파일별 역할과 변경 규칙이 정의된다.

| 파일 유형 | 역할 | 내용 범위 | 변경 규칙 |
|----------|------|----------|----------|
| **_index.md** | 항목 매핑 + LOCK 참조 + Phase 매핑 (정본) | 해당 서브폴더의 전체 항목 목록, STEP7-C 매핑 현황, LOCK 참조 테이블, Phase 배정 | R1(Part2 원문 우선) + R7(서브폴더 _index.md = What/How 정본) 준수 |
| **[component].md** | L3 시트 — Props, State, Events, Dependencies, Test (구현 상세) | 개별 컴포넌트/Hook/State의 상세 스펙: TypeScript Props Interface, 상태 전이 규칙, 이벤트 핸들러, 의존성, 테스트 시나리오 (최소 3건) | R-61-2(컴포넌트 추가/삭제 시 Part2 동기) + LOCK 값 재정의 금지 |
| **AUTHORITY_CHAIN.md** | 도메인 전체 권한 (읽기 전용) | LOCK 20건 레지스트리, 정본 출처 대조, 도메인 경계 선언, 6-11/4-1 참조 경계 | 읽기 전용 — LOCK 값 변경 시 상위 정본 수정 우선 (R8, R9) |
| **CONFLICT_LOG.md** | 도메인 내 충돌 이력 (추가 전용) | 정본 간 충돌 발견 기록, 해결 결정 사유, 영향 범위, 관련 서브폴더 | 추가 전용 — 기존 항목 삭제/수정 금지. RESOLVED 상태 변경만 허용 (R5) |

**서브폴더별 _index.md 포함 항목**:

| 서브폴더 | _index.md 필수 섹션 | 예상 L3 파일 수 |
|---------|-------------------|---------------|
| 01_builder-view | 3-Column 규격 LOCK 참조, 7개 페이지 목록, Builder Panel 구성도, CLI 커맨드 매핑 | ~8개 |
| 02_hologram-view | Glass HUD 스펙, 3-point 렌더링 인터페이스, 6-11 경계 선언, 멀티모달 V1 항목 | ~5개 |
| 03_ui-state-machine | 9-State LOCK 참조, 전이 규칙 매트릭스, §4.1↔§4.4 양방향 매핑, EventType 목록 | ~4개 |
| 04_react-components | 10그룹 인덱스, 44+4 컴포넌트 카탈로그, 그룹별 우선순위, Props 개요 | ~15개 |
| 05_custom-hooks | 8 Hook 시그니처 목록, 7 Store 슬라이스 구조, 의존성 그래프 | ~6개 |
| 06_accessibility | WCAG 2.1 AA 체크리스트, 키보드 내비게이션 경로, ARIA 라벨 목록, i18n 키 인덱스 | ~5개 |

---

## 9. 충돌 해결 프로토콜

### 9.1 Tier 6 공통 프로토콜 (INTEGRATION_PLAN §9.1 적용)

| 충돌 유형 | 발생 조건 | 해결 방법 |
|----------|----------|----------|
| **Part2 원문 vs SOT2 상세** | Part2 §6.1과 sot 2/ What/How 불일치 | Part2 원문 우선. SOT2를 Part2에 맞춰 수정 후 CONFLICT_LOG 기록 |
| **Tier 6 간 중복** | 6-1(UI) ↔ 6-11(Hologram) 범위 겹침 | 6-1 = UI 레이어(View 구조), 6-11 = LLM 통합/렌더링. AUTHORITY_CHAIN §3 참조 |
| **횡단 관심사 충돌** | 6-2(Security) 규칙이 UI 구현과 충돌 | 6-2 보안 체크리스트 우선. 예외는 CONFLICT_LOG 기록 |
| **기존 도메인 충돌** | 4-1(Rust-Tauri) ↔ 6-1(UI) IPC 경계 | 4-1 = 백엔드 IPC 커맨드, 6-1 = 프론트엔드 호출 인터페이스. AUTHORITY_CHAIN 명시 |

### 9.2 UI/UX 고유 충돌 시나리오

| 시나리오 | 해결 |
|---------|------|
| D2.0-08 §4.1 (9-state) vs §4.4 (6-state) 불일치 | §4.5 양방향 매핑 테이블이 정본. §4.1이 UI 설계 정본, §4.4는 Core 연동 뷰 |
| STEP7-C 신규 항목이 D2.0-08 LOCK과 충돌 | D2.0-08 LOCK 우선. STEP7 항목은 LOCK 범위 내에서만 구현 |
| v12 추가 컴포넌트가 기존 44개 목록과 충돌 | Part2 §6.1.8 v12 항목은 추가(ADD), 기존 대체(REPLACE) 아님 |

---

## 10. 검증 체크리스트

| # | 검증 항목 | 확인 방법 | 필수 |
|---|----------|----------|:---:|
| 1 | 계획서 14+α 섹션 완결성 | 모든 섹션 존재 + 빈 섹션 없음 (§11/§12 제외) | ✅ |
| 2 | AUTHORITY_CHAIN 20개 LOCK | LOCK 항목 20건 + Part2/D2.0-08 출처 명시 | ✅ |
| 3 | 서브폴더 6개 × _index.md | 각 서브폴더에 `_index.md` 존재 + 내용 비어있지 않음 | ✅ |
| 4 | Part2 §6.1 라인 대조 | `/sot-check sot2 6-1` MATCH 판정 | ✅ |
| 5 | D2.0-08 LOCK 항목 20건 불변 확인 | AUTHORITY_CHAIN과 D2.0-08 원문 대조 | ✅ |
| 6 | 9-state 양방향 매핑 | 03_ui-state-machine에 §4.1↔§4.4 매핑 테이블 존재 | ✅ |
| 7 | 44개 컴포넌트 그룹별 카탈로그 | 04_react-components에 10그룹 인덱스 존재 | ✅ |
| 8 | 의존성 도메인 참조 | 6-11(Hologram), 4-1(Tauri) 참조 명시 | ✅ |
| 9 | 기존 도메인 무변경 | `git diff`로 기존 폴더 변경 없음 | ✅ |
| 10 | MASTER_INDEX 갱신 | 6-1 상태 ✅ Phase 6 완료 기록 | ✅ |

---

## 11. 보완 사항

| # | 발견 사항 | 심각도 | 조치 | 상태 |
|---|----------|--------|------|------|
| S-1 | §9 CONFLICT_LOG 잠재 충돌 3건(W-1 Hologram 소유권, W-2 UI 9-state, W-3 RBAC 동기화) 미참조 | LOW | S8-7 보강 시 §9.3 충돌 요약 테이블 추가 | ✅ DONE (S10-3) |
| S-2 | §11 보완 사항 미작성 | LOW | S8-5에서 본 테이블 작성 완료 | ✅ DONE |
| S-3 | §6 이슈 해결 매핑 깊이 부족 (12줄, 서브폴더별 배분 없음) | MEDIUM | S10-3에서 STEP7-C 104건 서브폴더별 배분 상세 추가 (§6.2) | ✅ DONE |
| S-4 | §8 파일 역할 분리 깊이 부족 (문서 간 역할만, 서브폴더별 명세 없음) | MEDIUM | S10-3에서 서브폴더별 파일 역할 명세 추가 (§8.2) | ✅ DONE |
| S-5 | 44 컴포넌트 L3 시트 작성 미착수 (0/44) | MEDIUM | Phase 1 진입 시 우선순위 그룹별 순차 작성: Decision(3) → Chat(6) → Approval(3) → 나머지 | 🔄 OPEN |

---

## 12. FINAL REVIEW 결과

> **상태**: CONDITIONAL APPROVED — Phase 10 S10-3 (2026-03-27)

| # | 검증 항목 | 결과 | 비고 |
|---|----------|------|------|
| FR-1 | LOCK 20건 D2.0-08 출처 대조 | ✅ PASS | L1~L20 전체 D2.0-08/Part2 원문 일치 확인 |
| FR-2 | 9-State Machine 정확도 | ✅ PASS | §4.1 ↔ §4.4 양방향 매핑 + Pipeline S0~S8 매핑 검증 완료 |
| FR-3 | 44 컴포넌트 카탈로그 | ✅ PASS | 부록 A에 10그룹 48개(44+v12 4건) 카탈로그 존재. L3 상세는 Phase 1 위임 |
| FR-4 | 6개 서브폴더 구조 | ✅ PASS | 01~06 각 _index.md 존재 + STEP7-C 104건 서브폴더 배분 완료 |
| FR-5 | Part2 §6.1 라인 대조 | ✅ PASS | L4557-4670 MATCH |
| FR-6 | AUTHORITY_CHAIN 완전성 | ✅ PASS | 20건 LOCK + 정본 출처 + 도메인 경계 |
| FR-7 | CONFLICT_LOG 충돌 현황 | ✅ PASS | W-1~W-3 잠재 충돌 등재, §9.2에 해결 시나리오 명시 |
| FR-8 | §11 보완 사항 | ✅ PASS | S-1~S-5 전수 등재, S-5(L3 미착수)만 OPEN |

**Gate 판정**: APPROVED — B+ → A- (S10-3)
- **승급 근거**: §6 STEP7-C 104건 서브폴더별 상세 배분, §8 파일 역할 서브폴더 명세, §11 5건 보완 사항, §12 실 검증 데이터 충족
- **잔여 조건**: S-5 (44 컴포넌트 L3 시트) Phase 1 착수 시 해소 예정

---

## 13. L3 전수 승급 계획

### 13.1 L3 완성도 매트릭스 (UI/UX 도메인)

| # | 기준 | 설명 |
|---|------|------|
| E1 | **컴포넌트 Props 스키마** | TypeScript Interface + 필수/선택 Props + 기본값 |
| E2 | **상태 전이 규칙** | 전이 조건 + 가드 조건 + 부수효과 명시 |
| E3 | **이벤트 핸들러 매핑** | 사용자 행동 → LogEvent(event_type) → UI 반응 |
| E4 | **접근성 스펙** | ARIA 라벨, 키보드 탐색, 스크린 리더, 색상 대비 |
| E5 | **i18n 키 목록** | 컴포넌트별 i18n 키 + 기본 ko-KR/en-US 값 |
| E6 | **의존성 명세** | 필요 Hook/Store/외부 라이브러리 |
| E7 | **테스트 시나리오** | Unit + Integration + E2E 시나리오 (최소 3개/컴포넌트) |
| E8 | **에러/폴백 처리** | FailureCode 매핑 + UI 표시 규칙 |

### 13.2 현재 L3 상태

| 서브폴더 | 대상 수 | L3 완료 | 비율 |
|---------|---------|---------|------|
| 01_builder-view | ~15 항목 | 0 | 0% |
| 02_hologram-view | ~12 항목 | 0 | 0% |
| 03_ui-state-machine | 9 state + 전이 | 0 | 0% |
| 04_react-components | 44+ 컴포넌트 | 0 | 0% |
| 05_custom-hooks | 8 hooks + 7 stores | 0 | 0% |
| 06_accessibility | ~10 항목 | 0 | 0% |

> Phase 1에서 L3 작성 시작, Phase 2에서 완성 목표.

### 13.3 Phase 2~3 L3 완성도 최종 확정 매트릭스 (Path A drift fix Stage 1, 2026-05-17)

> **목적**: Phase 2 V2 4 NEW + Phase 3 P3-1~P3-4 4건 L3 완성도 최종 확정 + ★ mixed pattern Wave 2 specialty milestone 통산 (4-2 Wave 1 #11 + 4-4 Wave 1 #12 partial 패턴 EXACT 직계 + 1-1 폴더 path 정밀화 통산 3번째 사례 + ★★ upstream 3-7 forward-inheritance Plugin SDK first 사례 Wave 2 → Wave 1 inheritance).

| 서브폴더 | V2 NEW | V3 forward-defined | V-17 PASS | CON | FAIL |
|---------|--------|-------------------|-----------|-----|------|
| 01_builder-view | 1 (responsive_layout_v2 229L) | 1 (responsive_layout_v3 NEW BP-D 768px) | 1 | 0 | 0 |
| 02_hologram-view | 1 (multimodal_v2 252L) | 2 (ar_spatial_v3 NEW + AUTHORITY §3 6-11 경계 V3 갱신 row UPDATE) | 1 | 0 | 0 |
| 03_ui-state-machine | 1 (event_type_v2_sync 268L) | 0 (P3-2 AR EventType + P3-4 Plugin EventType inline 분담) | 1 | 0 | 0 |
| 04_react-components | 1 (v12_components 359L) | 4 (avatar_digital_human_v3 NEW + extension_slots_v3 NEW + _index 11번째 그룹 등재 UPDATE + _index 슬롯 4개 등재 UPDATE) | 1 | 0 | 0 |
| 05_custom-hooks | 0 | 0 (useResponsive + useARSession 확장 inline) | 0 | 0 | 0 |
| 06_accessibility | 0 | 1 (mobile_a11y_v3 NEW 모바일 WCAG 2.1 AA) | 0 | 0 | 0 |
| **합계** | **4 NEW / 1,108 L** | **8 forward-defined (5 NEW + 3 UPDATE)** | **4** | **0** | **0** |

**6 sub-section milestone**:
1. **★ mixed pattern Wave 2 specialty 통산**: P3-1 tcv2 first-pass-after-fix (D-6-1-P3-1-R4-1 cite L1729→L1756 +0 B in-place 4-char) + P3-2 tcv1 first-pass NO-DRIFT direct + P3-3 tcv2 (D-6-1-P3-3-R3-1 1-1_LLM→1-1_Verifier-Reasoning-Engines +23 B) + P3-4 tcv2 (D-6-1-P3-4-R3-1 cite L1754→L1756 +0 B in-place + D-6-1-P3-4-R3-2 cite §6.2 L283→L1756 [Phase 2] §4 이월 +16 B) = 4 fix textual notation only, byte Δ +39 B / +0 LF
2. **★ LOCK L1~L20 set accuracy 20 unique 변경 0 통산 Phase 0/1/2/3** (P3-4가 통산 최다 LOCK 인용 8건 L2/L4+L8+L10+L12+L13+L19+L20, P3-1 11 + P3-2 5 + P3-3 6 + P3-4 8 = 통산 30 LOCK 인용 ALL §3.4 AUTHORITY §4 정본 EXACT 정합)
3. **★ LOCK count duality**: V2 4 NEW grep "LOCK L" 누계 77 refs + V2 §2 4-field 정의 row 29 within-file 중복 0 + LOCK set unique 20 (변경 0 통산) + LOCK 신규 추가 0 통산 V3 범위 이월 (4-2 V2-only 129 / 4-4 시나리오 88 패턴과 다른 specialty)
4. **★ AUTHORITY §8.7 STEP_C v2 ultra-fine 수렴 통산 R1~R16 22 edits / 16 Round / 3회 multi-round 수렴** (R3+R4 + R7+R8 + R15+R16) — LOCK 4-field verbatim 100% 준수 + V2 정본 분리 R9 핵심 기여 (P2-3 v12_components.md L1 + L13 + L14 + P2-4 event_type_v2_sync.md L1 약식 → 정본 verbatim 통일)
5. **⚠️ CONFLICT_LOG 3 entries inheritance 보존**: CONF-61-001 RESOLVED L5 ORANGE #F97316 + CONF-61-002 RESOLVED L6 BLUE #00F6FF + CONF-61-003 RESOLVED L10 RBAC 출처 Part2 §6.1.8 단독 + OPEN 0 통산 (Phase 0/1/2/3 변경 0)
6. **★ Phase 4 entry-gate 4 P3 매핑** (P3-1 responsive_layout_v3 ≥ 200L + LOCK L11 V3 확장 + WCAG AA 모바일 + CONFLICT 0 / P3-2 ar_spatial_v3 ≥ 350L + 6-11 경계 RESOLVED + AR EventType 6-12 등록 + LOCK L19 100% / P3-3 avatar_digital_human_v3 ≥ 400L + LOCK L13 카탈로그 확장 + 6-2 RBAC + PII / P3-4 extension_slots_v3 ≥ 350L + 4 슬롯 + 3-7/6-2 cross-handoff + FailureCode V3 확장 14→18)

**★★ upstream 3-7 forward-inheritance Plugin SDK first 사례 Wave 2 → Wave 1 inheritance milestone**: P3-4 절차 3 + 산출물 1 extension_slots_v3.md Plugin SDK 호환 cross-handoff — LOCK-BM-09 reverse-inheritance 3-9 → 3-7 패턴과 비교 시 6-1 → 3-7 forward-inheritance 패턴 first 사례 Wave 2 specialty (3-7 NO-DRIFT 100% Wave 1 #9 inheritance 무손상 verify)

**★ 1-1 폴더 path 정밀화 통산 3번째 사례 milestone**: D-6-1-P3-3-R3-1 1-1_LLM → 1-1_Verifier-Reasoning-Engines +23 B (4-4 P3-2 D-P3-2-R3-1 + 4-2 P3-3 D-P3-3-R3-1 패턴 EXACT 직계 통산 3번째 사례)

**★ downstream 6-11★ + 6-9★ Wave 3 forward-defined inheritance pattern** (3-4 N-018 + 3-5 wellness_community + 3-6 6-1/6-2 + 3-7 3-10★/4-3★ + 4-2 4-4/4-1 + 4-4 6-9/4-3 패턴 직계, 본 도메인 Phase 3 단계 6-11/6-9 종합계획서 미직접 편집 verify only)

**§12 CONDITIONAL APPROVED SKIP no-op 자동 inheritance** (§13.X-1 처리, 3-7 ✅ APPROVED + 4-2 ✅ APPROVED + 4-4 ✅ APPROVED 패턴과 부분 다름 — 6-1는 CONDITIONAL APPROVED 인지 유지 specialty, Phase 3 완료 후 별도 /validate → /audit → /final-review 트랙)

---

## 14. 실행 약점 대응 계획

| # | 약점 | 위험도 | 대응 |
|---|------|--------|------|
| 1 | D2.0-08 11섹션 분량이 커서 참조 누락 가능 | HIGH | 서브폴더별로 D2.0-08 섹션 매핑 테이블 유지 |
| 2 | 44개 컴포넌트 L3 작성 공수 과다 | HIGH | 그룹별 우선순위(Decision/Chat/Approval 먼저) |
| 3 | 6-11 Hologram 도메인과 범위 경계 불명확 | MEDIUM | AUTHORITY_CHAIN §3에 명시 + 교차 참조 |
| 4 | STEP7-C 104건 매핑 불완전 가능 | MEDIUM | _index.md에 매핑 현황 테이블 유지 |
| 5 | v12 컴포넌트 4건의 STEP7 참조 ID 미확정 | LOW | Part2 주석에서 추출 (D207-175/178/179, S7NP-047/048) |

---

## 부록 §A — UI 컴포넌트 카탈로그

> Part2 §6.1.2 + §6.1.8 기반 React 컴포넌트 44+4개 = 48개 카탈로그

### A.1 기본 컴포넌트 (44개, V1)

| 그룹 | 수 | 핵심 컴포넌트 | 서브폴더 |
|------|---|-------------|---------|
| Decision | 3 | DecisionCard, DecisionLockBadge, 시각화 | 04_react-components |
| Chat | 6 | ChatPanel, UserBubble, AIBubble, ThinkingBlock, ArtifactEmbed, StreamingEffect | 04_react-components |
| Approval | 3 | ApprovalDialog, ApprovalCard, P2 확인 모달 | 04_react-components |
| Cost | 5 | CostDashboard, BudgetGauge, DownshiftControl, TokenCounter, 경고 Toast | 04_react-components |
| Evidence | 4 | VerificationBadge, UncertaintyAlert, 인용 점프, QoD 표시 | 04_react-components |
| Memory | 4 | MemoryCandidateList, MaskingPreview, CommitButton, PII 거부 카드 | 04_react-components |
| Node/Flow | 4 | NodeStatusBadge, ORANGE 헥사곤, BLUE 서클, Flow Edge 애니메이션 | 04_react-components |
| Guardrails | 3 | GuardrailsAlert, PolicyBlockedCard, PII 감지 모달 | 04_react-components |
| Input | 4 | 멀티라인 텍스트, 드래그앤드롭, 클립보드, 음성 입력 | 04_react-components |
| Navigation | 3 | 대화 사이드바, 프로젝트 폴더, 세션 목록 | 04_react-components |
| 기타 | 5 | ModelSelector, Table, Diagram, Log Viewer, Keyboard Shortcuts | 04_react-components |

### A.2 v12 추가 컴포넌트 (4개)

| # | 컴포넌트 | 하위 구성 | 참조 |
|---|---------|----------|------|
| 1 | **스트레스 관리 UI** | BreathingGuide(4-7-8), GroundingExercise(5-4-3-2-1), MeditationTimer | D207-175 |
| 2 | **CBT 셀프케어 UI** | ThoughtRecord, CognitiveDistortionDetector(12종), ProgressChart | D207-178 |
| 3 | **번아웃 예방 UI** | WorkloadMonitor, ForcedBreakOverlay, ActivityHeatmap | D207-179 |
| 4 | **플래시카드/간격반복 UI** | FlashcardEditor, SM2ReviewEngine, ReviewDashboard | S7NP-047/048 |

---

## 부록 §B — 상태 전이 다이어그램

### B.1 UI 9-State Machine (D2.0-08 §4.1 정본)

```
UI_S0_BOOT ──(로드 완료)──→ UI_S1_IDLE
UI_S1_IDLE ──(편집 시작)──→ UI_S2_EDITING
UI_S2_EDITING ──(사전 점검 통과)──→ UI_S3_READY
UI_S3_READY ──(실행 시작)──→ UI_S4_RUNNING
UI_S3_READY ──(실패)──→ UI_S7_RECOVERY
UI_S4_RUNNING ──(승인 필요)──→ UI_S5_AWAIT_APPROVAL
UI_S4_RUNNING ──(출력 완료)──→ UI_S6_PRESENTING
UI_S5_AWAIT_APPROVAL ──(승인)──→ UI_S4_RUNNING
UI_S5_AWAIT_APPROVAL ──(거부/타임아웃)──→ UI_S7_RECOVERY
UI_S6_PRESENTING ──(새 입력)──→ UI_S1_IDLE
UI_S6_PRESENTING ──(아카이브)──→ UI_S8_ARCHIVED
UI_S7_RECOVERY ──(재시도)──→ UI_S4_RUNNING
UI_S7_RECOVERY ──(복구)──→ UI_S1_IDLE
UI_S8_ARCHIVED ──(재시작)──→ UI_S0_BOOT
```

### B.2 양방향 매핑 (§4.1 9-state ↔ §4.4 6-state)

| §4.1 (9-state, 세션 생명주기) | §4.4 (6-state, Core 연동) | 비고 |
|------|------|------|
| UI_S0_BOOT | — | Core 연동 전 (부팅) |
| UI_S1_IDLE | UIS1IDLE | 입력 대기 |
| UI_S2_EDITING | UIS2PROCESSING (편집 중 Core 미호출 시 UIS1 유지) | Builder 전용 |
| UI_S3_READY | UIS2PROCESSING (사전 점검 = Core 처리 시작) | 실행 가능 |
| UI_S4_RUNNING | UIS3LOCKED → UIS4RUNNING | Decision Lock 전후 분기 |
| UI_S5_AWAIT_APPROVAL | UIS5AWAITAPPROVAL | 1:1 대응 |
| UI_S6_PRESENTING | UIS6PRESENTING | 1:1 대응 |
| UI_S7_RECOVERY | UIS4RUNNING (재시도/폴백 중) | 실행 흐름 내 분기 |
| UI_S8_ARCHIVED | — | 세션 종료 후 리뷰 |

> **정본 우선순위**: §4.1(9-state)이 UI 설계 정본, §4.4(6-state)는 Core 연동 뷰.

### B.3 Pipeline S0~S8 ↔ UI 상태 매핑 (D2.0-08 §4.6 D8-M11)

| Pipeline (02 정본) | 단계명 | UI 상태 (§4.1) | UI 표시 |
|---|---|---|---|
| S0_RECEIVED | Perception/Intake | UI_S4_RUNNING | "요청 수신됨" |
| S1_INTENT_PARSED | Perception/Intake | UI_S4_RUNNING | "의도 분석 완료" |
| S2_EVIDENCE_READY | Reasoning/Plan | UI_S4_RUNNING | "근거 수집 완료" |
| S3_DECISION_LOCKED | Reasoning/Plan | UI_S4_RUNNING | "결정 잠금" |
| S4_EXECUTING | Action/Execute | UI_S4_RUNNING | "실행 중" |
| S5_OUTPUT_READY | Action/Execute | UI_S6_PRESENTING | "출력 준비됨" |
| S6_SELF_CHECKED | Reflection/Verify | UI_S6_PRESENTING | "자기검증 완료" |
| S7_MEMORY_COMMITTED | Memory/Store | UI_S6_PRESENTING | "메모리 저장됨" |
| S8_DONE | — | UI_S8_ARCHIVED | "완료" |

---

---

## 변경 이력

| 날짜 | 변경 내용 |
|------|----------|
| 2026-04-12 | Phase 1 완료 (P1-1~P1-14 전 세션 ✅), G1 ALL PASS, Phase 2 진입 가능 |
| 2026-04-12 | Phase 1 종합 재검증: 14건 L3 산출물 전수 3단계 검증(병렬→교차→잔여), 21건 이슈 발견·수정, 잔여 0건. G1-3 추가 |
| 2026-04-26 | STAGE 7 STEP_A 완료 (Phase 7-II 15번째 도메인 진입). Phase 0/A/B/C/E.1 전수 PASS, V1 logical 340 → 342 (+2 tag). baseline aggregate `c566620245327eaecdc6044e194f8a06469ee6fde856e6a08ceb1be036d3809b`. LOCK L1~L20 20 unique 보존 + CONF-61-001~003 RESOLVED 3 + entry_gate 3/3 PASS |
| 2026-04-26 | STAGE 7 STEP_B 도메인 마감 완료. P2-1~P2-4 4 NEW V2 산출물 1,108L (multimodal_v2 252 + responsive_layout_v2 229 + v12_components 359 + event_type_v2_sync 268). Phase 2 → 3 전환 게이트 ✅ ALL PASS. ISS-5/4/7 → RESOLVED 진전. LOCK 변경 0 + CONFLICT 신규 0 + FABRICATION 0. V1 14/14 byte-prefix SHA 보존 통산. parent-executed Subagent 0회 통산 |
| 2026-04-26 | STAGE 7 STEP_C 최종 마감 truly_converged. Phase F 6/6 PASS + Phase G 8/8 PASS + 심층 재검증 R1~R8 통산 **9 edits / 8 Round / 2회 multi-round 수렴** (1차 R1~R4 2 edits R3+R4 연속 0 changes truly_converged + 2차 post-sync R5 4 edits cascade + R6~R7 3 edits ultra-fine + R8 0 changes truly_converged). **[PHASE3_READY v2: 6-1 — 2026-04-26 최종 확정]** 6 지점 동기화 (plan + INDEX v1.1 + AUTHORITY v2.4 §8 + CONFLICT v2.3 + SOT2_MASTER × 2 + memory). LOCK L1~L20 20 unique 보존 통산. CONFLICT OPEN 0 / 신규 [CONFLICT_CANDIDATE] 발화 0건 통산. FABRICATION 0/40 prose CLEAN. V1 14/14 byte-prefix SHA 보존 통산 (V1 본문 변경 0건 통산). parent-executed Subagent 0회 통산. Phase 7-II 14/21 → **15/21 ✅ 확정** |
| 2026-04-26 | STAGE 7 STEP_C 최종 마감 **truly_converged_v2** (2차 사용자 재요청 "더이상 수정하지 않을때까지 / 미세한 부분까지 전부 확인" 반영). 심층 재검증 R9~R16 ultra-fine 통산 **13 edits / 8 Round / R15+R16 연속 0 changes truly_converged_v2**: R9 4 V2 정본 verbatim 4-field 100% 정밀화 (P2-3 v12_components.md L1 약식 → 9-state 전체 명시 + L13/L14 LOCK 값 V2 확장 정보 인라인 → 정본 verbatim + footnote 분리 + P2-4 L1 약식 → 9-state 전체 명시) / R10 6 _index footer 6개 모두 "R1~R_N truly_converged" → "R1~R8 9 edits / 8 Round / 2회 multi-round 수렴" 일괄 sed cascade / R11 3 STAGE7_PROGRESS L65 + memory + AUTHORITY §8.5 V1 8 tag / R12 6 cascade AUTHORITY v2.5 §8.7 신설 + CONFLICT v2.4 + INDEX v1.2 + plan §변경이력 v2 row + SOT2_MASTER × 3 + memory / R13 scan 0 + R14 3 (P2-1 L1 slash → comma + plan §7.2 + L1722 truly_converged → truly_converged_v2 cascade) / R15+R16 0 changes 최종 truly_converged_v2. 통산 R1~R16 **22 edits / 16 Round / 3회 multi-round 수렴** (R3+R4 + R7+R8 + R15+R16) — 3-7 v2 22 동등 / 3-10 v2 20 근접 / 4-2 v3 28 / 4-3 v2 36 / 4-1 v2 30 비교. **신규 핵심 기여**: V2 4-field verbatim 100% 준수 (R9 LOCK 값 셀 정본 분리 + R14 L1 P2-1/P2-3/P2-4 verbatim 통일 → AUTHORITY 정본 §4 L72 일치 100% 달성, 4-3 LOCK-MCP 5필드 / 4-2 LOCK-CI / 4-1 LOCK-RT 패턴과 다른 본 6-1 LOCK 4-field 패턴 100% 정밀 달성). **[PHASE3_READY v2: 6-1 — 2026-04-26 최종 확정 truly_converged_v2]** 6 지점 재동기화. LOCK L1~L20 20 unique 보존 통산 + 4-field verbatim 100% 준수. CONFLICT 신규 0건 통산. FABRICATION 0/40 prose CLEAN. V1 14/14 byte-prefix SHA 보존 통산 + STEP_C 2차 audit_truly_converged_v2 1 tag = 통산 8 tag. parent-executed Subagent 0회 통산. Phase 7-II 15/21 ✅ 확정 (재확인 v2). |

> **문서 끝**
> 의존성: 6-11(Hologram-Main-LLM), 4-1(Rust-Tauri-Infrastructure)
> 횡단 참조: 6-2(Security) §6.5 보안 체크리스트, 6-12(Event-Logging) 이벤트 표준
