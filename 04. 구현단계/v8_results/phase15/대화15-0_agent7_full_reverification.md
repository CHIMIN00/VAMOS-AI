# VAMOS v8.1 Phase 1.5B — Agent 7 전범위 재검증 보고서

**대화**: 15-0
**검증 대상**: Agent 7 (UI/UX + 멀티모달)
**트리거**: 대화14 Spot-check 오판율 1/4 = 25% > 20% 임계값
**OVERTURNED 사유**: Hooks 불일치 카운트 4/8 → 실제 2~3/8 (Agent 13), 본 재검증: PHASE_B2 직접 열독 결과 PART2와 완전 일치 (MATCH)
**검증일**: 2026-03-06
**SRC 열독**: D2.0-08 전문(2,696줄), D2.1-D8 전문, PHASE_B2 §3.1 전문, PART2 전문(3,454줄)

---

## 1. 전수 재검증 테이블

### 1-A. Dim B (13항목) — SRC <-> PART2 내용 정합

| # | 항목 | Agent 7 판정 | Agent 13 판정 | 본 재검증 판정 | 변경 | 근거 |
|---|------|-------------|--------------|--------------|------|------|
| B1 | 프레임워크 스택 Tauri 2.0 + React 18 | MATCH + MM-5(내부 18 vs 18.3) MEDIUM | CONFIRMED | **MATCH** (LOW note) | 유지 | D2.0-08 §11-A.11: "Tauri 2.0 + React 18 (LOCK)". PART2 §2 L71/L77: "React 18 + TypeScript", "Rust Tauri 2.0". §7.2 L3258 "React 18.3 통일 V1-014". 내부 18 vs 18.3은 minor version 차이로 LOW 처리 (주의사항 #5) |
| B2 | 3-Column 레이아웃 | MATCH | CONFIRMED | **MATCH** | 유지 | D2.0-08 §2.1.1: 좌 250-300px/중앙 flex/우 350-400px. PART2 §6.1.1 L2365: 동일 값. 정합 확인 |
| B3 | 7 페이지 | MISMATCH(MM-4) HIGH | REAL_ERROR(MM-6) | **MATCH** | **변경** | PHASE_B2 §3.1: 7 pages (Dashboard/Chat/Workflow/Memory/Settings/Log/NodeDetail). PART2 §6.1.4 L2401: 동일 7 pages. **PART2 갱신으로 정합 달성.** 단, PART2 §3 L1405-1409는 여전히 5 pages만 기재 (내부 비동기) |
| B4 | ~44 React 컴포넌트 | NO_SOURCE(NS-1) MEDIUM | Acceptable | **MATCH** | **변경** | D2.0-08 §10.4 L1475: "총 44개" 명시 (BV 12 + HV 18 + CM 7 + CLI 4 + Dashboard 3). PART2 §6.1.2 L2370-2384: 44개 분해표 합산 = 정확히 44. Agent 7이 §10.4를 미발견하고 "104"로 오인한 것으로 판단 (§6.4 STEP7-J 98건과 혼동 추정) |
| B5 | 8 Custom Hooks | MISMATCH(MM-2) HIGH 4/8 | OVERTURNED 2-3/8 MEDIUM | **MATCH** | **변경** | PHASE_B2 §3.1 L147-154: useTauriIPC, useDecision, useWorkflow, useMemory, useCost, useNotification, **useAutonomy**, **useLog**. PART2 §6.1.3 L2388-2390: useTauriIPC, useDecision, useWorkflow, useMemory, useCost, useNotification, **useAutonomy**, **useLog**. **8/8 완전 일치.** Agent 7의 4/8 불일치 및 Agent 13의 2-3/8 불일치 모두 SRC 오독에 기인. useApproval/useConfig는 현재 PHASE_B2에 존재하지 않음 |
| B6 | 7 Zustand Stores | MISMATCH(MM-3) HIGH | REAL_ERROR + SC-2 | **MATCH** | **변경** | PHASE_B2 §3.1: app/decision/workflow/memory/cost/notification/auth (7개). PART2 §6.1.3 L2391-2392: app/decision/cost/notification/auth/memory/workflow (7개). v11.0.0 갱신(agent→notification, config→auth) 반영으로 **완전 일치.** Agent 7 검증 시점 이후 PART2 수정됨 |
| B7 | Builder/Hologram View | MATCH | CONFIRMED | **MATCH** | 유지 | D2.0-08 §2.1 Builder(Cockpit): 리소스트리+그래프캔버스+로그/승인/비용 탭. §2.2 Hologram(Experience): 세션+채팅스트림+Glass HUD. PART2 §6.1.1 L2366-2367: 동일 구조 |
| B8 | Design System | MATCH | CONFIRMED | **MATCH** | 유지 | D2.0-08 §10.1: ORANGE #F97316, BLUE #00F6FF, BG #1E1E1E. CSS Custom Properties. PART2 §6.1.4 L2403: "ORANGE/BLUE 테마 CSS Custom Properties". 정합 |
| B9 | i18n (ko/en/ja) | MISMATCH(MM-1) HIGH | FALSE_POSITIVE(MM-7) | **MATCH (FP 확인)** | **변경** | D2.0-08 §0 L58-64: "기본 로케일: ko-KR, 보조 로케일: en-US, **확장 로케일(V2): ja-JP**". ja-JP는 명시적 V2 항목. PART2 §3 L1413: "ko-KR/en-US" (2개) — V1 범위에서 정확. Agent 7이 V2 확장 표기를 미확인하여 오판. **FALSE_POSITIVE 확정** |
| B10 | UI 구현 결정 4항목 | MATCH | Acceptable | **MATCH** | 유지 | PART2 §6.1.4 L2395-2404: 레이아웃 수/라우트 수/다크모드 변수/애니메이션 설정. PART2 자기 정의 항목, SRC 참조 합리적 |
| B11 | 멀티모달 UI V2/V3 진화 | MATCH | CONFIRMED | **MATCH** | 유지 | D2.0-08 §6.4: V1(CLIP/OCR/STT/TTS), V2(ImageBind/음성채팅/Computer Use), V3(3D/AR/아바타). PART2 §6.1.5 L2406-2418: 동일 진화 경로 |
| B12 | CLI 인터페이스 | MISMATCH(MM-6) MEDIUM | REAL_ERROR LOW | **PARTIAL_MATCH** | **변경** | D2.0-08 §2.3.1: 6 commands (run/approve/status/cost/memory/**policy**). PART2 §6.1.1 L2368: 6 commands 포함 policy — **SRC와 일치**. 단 PART2 §3 L1415: 5 commands (policy 누락) — **§3 미동기**. Severity: **LOW** (§6.1.1 정본 기준 일치) |
| B13 | V2 PWA SOURCE_CONFLICT | SOURCE_CONFLICT(SC-4) | SC confirmed | **SOURCE_CONFLICT 유지** | 유지 | D2.0-08 §11-A.11: V2 Web = "Next.js + PWA". D2.1-D8 §6-A.1: V2+ Web = "PWA (React)". 프레임워크 불일치 (Next.js vs React). PART2: PWA 미언급 — V1 범위에서 적절 |

### 1-B. Dim C (15항목) — 구현 가능성

| # | 항목 | Agent 7 판정 | Agent 13 판정 | 본 재검증 판정 | 변경 | 근거 |
|---|------|-------------|--------------|--------------|------|------|
| C1 | 3-Column fluid Tauri WebView | IMP_OK | — | **IMP_OK** | 유지 | WebView2/WebKit에서 CSS Flexbox/Grid 완전 지원. react-resizable-panels 의존성 확인 (D2.0-08 S7C-001) |
| C2 | Builder/Hologram 전환 | IMP_OK | — | **IMP_OK** | 유지 | React 조건부 렌더링 또는 중첩 라우트. ViewSwitcher 컴포넌트 CM-34 정의됨 (D2.0-08 §10.4) |
| C3 | 44 컴포넌트 props | IMP_OK | — | **IMP_OK** | 유지 | TypeScript interfaces + Zod 3.24. D2.0-08 §10.4 컴포넌트 레지스트리로 props 추론 가능 |
| C4 | 8 Hook 리턴 타입 | IMP_OK | — | **IMP_OK** | 유지 | 표준 React Custom Hook 패턴. TypeScript 제네릭으로 타입 안전 보장 |
| C5 | useTauriIPC wrapping | IMP_OK | — | **IMP_OK** | 유지 | @tauri-apps/api 2.2 invoke() 래퍼. 표준 패턴 |
| C6 | 7 Store 상호의존성 | IMP_MISSING MEDIUM | — | **IMP_MISSING MEDIUM** | 유지 | PART2/SRC 모두 7 Zustand store 간 구독/의존 관계 미정의. 순환 의존 방지 규칙 부재. 구현 시 아키텍처 결정 필요 |
| C7 | UI 9-state 관리 | IMP_OK | — | **IMP_OK** | 유지 | D2.0-08 §4.1: 9-state(UI_S0~S8) 정의. PART2 §6.1.6 L2420-2440: 동일 9-state 반영. Zustand 또는 XState로 구현 가능 |
| C8 | Hologram 스트리밍 | IMP_MISSING MEDIUM | — | **IMP_OK** | **변경** | D2.0-08 S7C-038 L1758: **"Streamable HTTP (DEC-017 LOCK)"** 명시. "SSE(EventSource)는 DEC-017에 의해 deprecated". 토큰 단위 실시간 표시 + 중지 버튼. Agent 7이 S7C-038을 미발견하여 "프로토콜 미정의"로 오판 |
| C9 | 7 페이지 라우팅 | IMP_OK | — | **IMP_OK** | 유지 | react-router-dom 6.28. PHASE_B2 §3.1: 7 페이지 파일 확인 |
| C10 | i18n 키 관리 | IMP_OK | — | **IMP_OK** | 유지 | D2.0-08 MOD-022: ui.{component}.{key} 패턴. react-i18next + namespace JSON |
| C11 | CSS Custom Properties | IMP_OK | — | **IMP_OK** | 유지 | 표준 CSS 기능. D2.0-08 §10.1 색상 팔레트 + S7C-097 dark/light 모드 |
| C12 | CLI 통합 | IMP_OK | — | **IMP_OK** | 유지 | Tauri CLI (Rust clap) + 공유 LogEvent namespace (ui.cli.*). D2.0-08 §5.6-A: 10 CLI 이벤트 |
| C13 | Flow Edge 애니메이션 | IMP_OK | — | **IMP_OK** | 유지 | @xyflow/react 12.4 사용자 정의 Edge 렌더링. D2.0-08 §2.1.2 L181: "Flow Edge: 실행 중 경로 하이라이트/애니메이션" |
| C14 | Failure/Fallback UI | IMP_MISSING HIGH | REAL_ERROR(MS-3) | **IMP_OK (참조 오류 존재)** | **변경** | D2.0-08 §7 L1266-1379: **14 FailureCodes + 9 FallbackRegistry** 완전 정의. 구현에 필요한 정보가 SRC에 존재. Agent 7이 "D2.1-D2/D2.1-D8 파일 부존재"라 했으나 D2.1-D8은 실제 존재 (DN-005 B로 SOT 없는 문서형 계약). PART2 §6.1.7의 참조 대상 "D2.1-D2"는 **"D2.0-08 §7"**로 정정 필요 (문서 참조 오류, LOW) |
| C15 | RBAC 프론트/백엔드 | IMP_OK | — | **IMP_OK** | 유지 | PART2 §6.1.8 L2453-2460: RBAC 4역할 화면별 접근 제어표 정의. D2.0-08 §8 승인 게이트/마스킹 참조 |

---

## 2. 판정 변경 목록

### 2-A. Agent 7 원본 대비 변경 (8건)

| # | 항목 | Agent 7 판정 | 본 재검증 판정 | 변경 사유 |
|---|------|-------------|--------------|----------|
| 1 | B3: 7 페이지 | MISMATCH HIGH | MATCH | PART2 §6.1.4 갱신으로 7 pages 일치 (PART2 수정) |
| 2 | B4: ~44 컴포넌트 | NO_SOURCE MEDIUM | MATCH | D2.0-08 §10.4에 "총 44개" 명시. Agent 7이 §10.4 미발견 (Agent 7 오류) |
| 3 | B5: 8 Hooks | MISMATCH HIGH 4/8 | MATCH | PHASE_B2 L147-154 직접 열독: useAutonomy/useLog 존재. PART2와 8/8 완전 일치. useApproval/useConfig는 PHASE_B2에 부존재. Agent 7 및 Agent 13 모두 SRC 오독 (Agent 7 오류) |
| 4 | B6: 7 Stores | MISMATCH HIGH | MATCH | PART2 v11.0.0 갱신(agent→notification, config→auth)으로 PHASE_B2와 완전 일치 (PART2 수정) |
| 5 | B9: i18n | MISMATCH HIGH | MATCH (FP) | D2.0-08: ja-JP는 "확장 로케일(V2)" 명시. V1 범위에서 ko/en 2개가 정확 (Agent 7 오류 — V2 주석 미확인) |
| 6 | B12: CLI | MISMATCH MEDIUM | PARTIAL_MATCH LOW | PART2 §6.1.1에 policy 포함(SRC 일치). §3만 누락(내부 비동기). Severity MEDIUM→LOW |
| 7 | C8: Hologram 스트리밍 | IMP_MISSING MEDIUM | IMP_OK | D2.0-08 S7C-038: Streamable HTTP (DEC-017 LOCK) 명시. Agent 7 SRC 미발견 (Agent 7 오류) |
| 8 | C14: Failure/Fallback UI | IMP_MISSING HIGH | IMP_OK | D2.0-08 §7에 14 FailureCodes + 9 FallbackRegistry 완전 정의. D2.1-D8 파일도 실존. Agent 7 "파일 부존재" 오판 (Agent 7 오류) |

**변경 원인 분류**:
- Agent 7 오류 (SRC 미완독/오판): 5건 (B4, B5, B9, C8, C14)
- PART2 갱신 후 해소: 3건 (B3, B6, B12)

### 2-B. Agent 13 판정 대비 변경 (7건)

| # | Agent 13 ID | Agent 13 판정 | 본 재검증 판정 | 변경 사유 |
|---|------------|-------------|--------------|----------|
| 1 | MM-1 (Hooks) | OVERTURNED → REAL_ERROR MEDIUM (2-3/8) | MATCH | PHASE_B2 직접 열독: useAutonomy/useLog 존재. PART2와 8/8 일치. Agent 13도 SRC 오독 |
| 2 | MM-2 (Stores) | REAL_ERROR | MATCH (해소) | PART2 v11.0.0 갱신으로 7 stores 완전 일치 |
| 3 | MM-6 (Pages 5→7) | REAL_ERROR | MATCH (해소) | PART2 §6.1.4에 7 pages 추가 |
| 4 | MS-1 (9-state 부재) | REAL_ERROR | MATCH (해소) | PART2 §6.1.6에 9-state 추가 |
| 5 | MS-2 (Log/NodeDetail 누락) | REAL_ERROR LOW | MATCH (해소) | PART2 §6.1.4에 Log/NodeDetail 포함 |
| 6 | MS-4 (RBAC 부재) | REAL_ERROR | MATCH (해소) | PART2 §6.1.8에 RBAC 접근 제어표 추가 |
| 7 | SC-2 (Stores SC) | SC confirmed | MATCH (해소) | PART2 v11.0.0 갱신으로 SC 해소 |

---

## 3. 신규 발견 목록

| # | 항목 | 분류 | Severity | 상세 |
|---|------|------|----------|------|
| N1 | PART2 §3 <-> §6.1 내부 비동기 패턴 | SC (Internal) | LOW | §3은 이전 데이터 유지 (5 pages, 5 CLI commands), §6.1은 갱신됨 (7 pages, 6 CLI commands). §6.1이 정본이므로 기능적 영향 없으나, §3 동기화 필요 |
| N2 | D2.0-08(44) vs PHASE_B2(36) 컴포넌트 수 불일치 | SC (Inter-SRC) | LOW | D2.0-08 §10.4: BV(12)+HV(18)+CM(7)+CLI(4)+Dashboard(3)=44. PHASE_B2 §3.1: 10개 디렉토리 36 파일. 분류 체계 상이 (View 기반 vs 기능 기반). 44에는 V1.1+ 7개 포함, PHASE_B2는 V1 필수 37개 미만의 36개. 구현 시 §10.4 레지스트리 기준 정렬 필요 |
| N3 | PART2 §3 소스 섹션번호 오류 (2건) | RE | LOW | §3 L1402: layout 출처 "D2.0-08 §4" → 정확: §2/§3 (§4는 UI State Machine). §3 L1410: 컴포넌트 출처 "D2.0-08 §7" → 정확: §10.4 (§7은 Failure/Fallback). Agent 13이 MM-4/MM-5로 기발견했으나 출처 정정이 미반영된 상태 |
| N4 | PART2 §6.1.7 문서 참조 오류 | RE | LOW | Failure/Fallback UI 규칙의 전체 목록 참조를 "D2.1-D2"로 기재. D2.1-D8은 SOT 스키마 없음(DN-005 B). 정확한 참조: **D2.0-08 §7** (14 FailureCodes + 9 FallbackRegistry) |

---

## 4. 최종 요약

### 4-1. 전수 재검증 결과

| 지표 | 수치 |
|------|------|
| Agent 7 원본 대비 변경 | **8건** / 유지 20건 (전체 28건) |
| Agent 13 판정 대비 변경 | **7건** / 유지 10건 (Agent 13 평가 17건 중) |
| 신규 발견 | **4건** (RE 2건 LOW, SC 2건 LOW) |
| 전체 판정 변경율 | 8/28 = **28.6%** |

### 4-2. Agent 7 오판 분석

| 분류 | 건수 | 항목 |
|------|------|------|
| Agent 7 SRC 미완독/오판 | **5건** | B4(§10.4 미발견), B5(Hooks SRC 오독), B9(V2 주석 미확인), C8(S7C-038 미발견), C14(파일 부존재 오판) |
| PART2 갱신으로 해소 | **3건** | B3(pages), B6(stores), B12(CLI policy) |
| Agent 7 순수 오판율 | **5/28 = 17.9%** | (SRC 열독 불완전에 기인) |

### 4-3. 현재 잔존 이슈

| # | 항목 | Severity | 상태 |
|---|------|----------|------|
| 1 | Store 상호의존성 미정의 | MEDIUM | PART2/SRC 모두 미정의 — 구현 시 아키텍처 결정 필요 |
| 2 | V2 PWA SOURCE_CONFLICT (Next.js vs React) | MEDIUM | D2.0-08과 D2.1-D8 간 불일치 — V2 착수 전 해결 필요 |
| 3 | Failure/Fallback PART2 반영 부분적 | MEDIUM | §6.1.7에 4 예시만 기재, D2.0-08 §7의 14+9 전체 반영 또는 정확한 참조 필요 |
| 4 | PART2 §3 <-> §6.1 내부 비동기 | LOW | §3 동기화 필요 (pages 5→7, CLI 5→6) |
| 5 | PART2 소스 섹션번호 오류 (§3, §6.1.7) | LOW | 4건 정정 필요 |

### 4-4. 대화14 통합 판정 영향

| 지표 | 대화14 값 | 본 재검증 값 | 변동 |
|------|----------|------------|------|
| Agent 7 REAL_ERROR | 10건 | **4건** | -6건 (MM-1 Hooks MATCH 확정, MM-2 stores, MM-6 pages, MS-1 9-state, MS-2 Log/NodeDetail, MS-4 RBAC — MM-1은 SRC 오독, 나머지 5건은 PART2 갱신으로 해소) |
| Agent 7 FALSE_POSITIVE | 2건 | **2건** (MM-7 i18n, MS-5 FREEZE) | 변동 없음 |
| Agent 7 OVERTURNED | 1건(2-3/8) | **1건 → MATCH 확정** | PHASE_B2 직접 열독 결과 PART2와 완전 일치. OVERTURNED 사유 자체도 SRC 오독에 기인 |
| Agent 7 SOURCE_CONFLICT | 2건 확인 | **1건** (SC-2 stores 해소) | -1건 |
| Agent 7 Grade | B | — | 재평가 필요 |

---

## 5. 대화14 갱신 필요 사항

### 5-1. 대화14 PART I — Agent 7 섹션 수정 내역

1. **RE 건수**: 10 → 4 (-6건)
   - MM-1 (Hooks 불일치): REAL_ERROR → **MATCH** (PHASE_B2 직접 열독: useAutonomy/useLog 존재, PART2와 8/8 일치. Agent 7/13 모두 SRC 오독)
   - MM-2 (Stores 불일치): REAL_ERROR → **해소** (PART2 v11.0.0 갱신)
   - MM-6 (Pages 5 vs 7): REAL_ERROR → **해소** (PART2 §6.1.4 갱신)
   - MS-1 (9-state 부재): REAL_ERROR → **해소** (PART2 §6.1.6 추가)
   - MS-2 (Log/NodeDetail 누락): REAL_ERROR → **해소** (PART2 §6.1.4)
   - MS-4 (RBAC 부재): REAL_ERROR → **해소** (PART2 §6.1.8 추가)

2. **잔존 RE 4건 상세**:
   - MM-3 (CLI §3 policy 누락): LOW — §6.1.1은 정합, §3만 미동기
   - MM-4 (컴포넌트 소스 섹션번호 오류): LOW
   - MM-5 (레이아웃 소스 섹션번호 오류): LOW
   - MS-3 (Failure/Fallback 부분 반영 + 참조 오류): MEDIUM

3. **FP 2건**: 유지 (MM-7 i18n ja V2 scope, MS-5 FREEZE)

4. **OVERTURNED 1건 → MATCH 확정**: PHASE_B2 직접 열독 결과 Hooks 8/8 완전 일치. Agent 13의 "2-3/8" 판정도 SRC 오독에 기인. 불일치 자체가 존재하지 않음

5. **SC**: SC-2 (Stores) 해소 → 잔존 SC: SC-1 (V2 PWA) 1건만

### 5-2. 대화14 PART III — 통합 수치 변동 내역

| 수치 항목 | 대화14 기존 | 갱신 값 | 변동 |
|----------|-----------|--------|------|
| Agent 7 RE 건수 | 10 | **4** | **-6** |
| Agent 7 SC 건수 | 2 | **1** | **-1** |
| 전체 Agent RE 합산 | (대화14 값 - 6) | | RE 총합 -6 |
| 전체 Agent SC 합산 | (대화14 값 - 1) | | SC 총합 -1 |

> **Note**: 6건 해소 중 5건은 PART2 갱신에 의한 것으로 Agent 13의 검증 시점 기준으로는 정확한 판정이었습니다. 1건(MM-1 Hooks)은 Agent 7과 Agent 13 모두 PHASE_B2의 hook 이름을 오독한 것으로, useApproval/useConfig는 현재 PHASE_B2 L147-154에 존재하지 않으며 실제로는 useAutonomy/useLog입니다.

---

## 부록: Hooks 정밀 대조표 (정정판)

| # | PHASE_B2 §3.1 L147-154 (SRC 정본) | PART2 §6.1.3 L2388-2390 | 일치 |
|---|----------------------------------|-------------------------|------|
| 1 | useTauriIPC | useTauriIPC | O |
| 2 | useDecision | useDecision | O |
| 3 | useWorkflow | useWorkflow | O |
| 4 | useMemory | useMemory | O |
| 5 | useCost | useCost | O |
| 6 | useNotification | useNotification | O |
| 7 | useAutonomy | useAutonomy | O |
| 8 | useLog | useLog | O |

**불일치: 0/8건 — 완전 일치 (MATCH)**

> **정정 사유**: 초판에서 PHASE_B2의 hook #6-7을 useApproval/useConfig로 기재했으나,
> PHASE_B2 L147-154 직접 재확인 결과 useAutonomy/useLog가 정확합니다.
> useApproval/useConfig는 Agent 13 보고서(대화14)에서 인용된 값이며,
> Agent 13도 PHASE_B2를 오독한 것으로 판명되었습니다.
> 본 재검증 초판이 주의사항 #1("SRC 원본 직접 대조")을 위반하여 Agent 13 보고서 값을
> SRC 직접 열독 결과보다 우선 적용한 오류였습니다.

---

*검증 완료: 2026-03-06*
*검증자: Phase 1.5B 전범위 재검증 에이전트*
