# [Agent 7] 검증 결과 — UI/UX + 멀티모달 검증

**검증 일시**: 2026-03-05
**PART2 버전**: v14.0.0 (1934행)
**Phase 0 참조**: 0-D.json (LOCK/FREEZE 80건)

---

## 읽은 파일 (실제 읽은 수 / 할당 수: 4 / 5)

- [x] VAMOS_구현가이드_PART2_구현단계.md (1934행) — §2 V0-STEP-3(UI), §3 V1-Phase 4(UI), §6.1 전체, §7 GO/NO-GO 전수 열독
- [x] D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md (2776행) — 전수 열독
- [x] PHASE_B_EXHAUSTIVE_ANALYSIS.md (전체) — §B.2 Frontend 구조, hooks/stores/pages 전수 열독 ※ v8 §5 "PHASE_B2 §3.1" 해당
- [x] 0-D.json (80건) — UI/UX 관련 LOCK 항목 추출 완료
- [ ] D2.1-D8 — **파일 미존재** (시스템 전체 검색, 파일 없음) ※ v8 §5 SRC 할당이나 실제 파일 부재

> **주의**: SRC 파일 "D2.1-D8"이 시스템 어디에도 존재하지 않음. v8 매트릭스가 참조하나 실제 파일 부재. Failure/Fallback 에러코드 전체 목록(FM/TL/MC_ERR_* 10개 + 9개 폴백)의 원본 검증 불가.

---

## 검사 통계

- **Dim B** Forward: **12** / MATCH: **5** / MISMATCH: **6** / NO_SOURCE: **1** / Reverse MISSING: **2** (총 **14** 체크)
- **Dim C** Facts checked: **15** / IMP_OK: **12** / IMP_IMPOSSIBLE: **0** / IMP_MISSING: **3** / IMP_CONFLICT: **0**
- **SOURCE_CONFLICT**: **5건** (4건은 MISMATCH #1-4 근인 포함, 1건(B#13 V2 PWA) 독립)
- 수정 전: HIGH **5**건, MEDIUM **8**건 = 총 **13**건
- 수정 후: 미수정

> ※ v8 B#13 (V2 PWA SOURCE_CONFLICT)은 SC #4에서 판정. Forward MATCH/MISMATCH 산출에 미포함.

---

## 심각도 분류 기준

- **BLOCKER**: LOCK 위반, 구현 차단, 순환 의존, 카운트 오류 ±3 이상
- **HIGH**: 값 오류, 누락 스펙, 카운트 오류 ±2
- **MEDIUM**: 근사/구버전 값, 표기 차이, 출처 오기재
- **LOW**: 서식, 약어 vs 전체명, ±1 근사

---

## Dim B — MISMATCH

| # | PART2:행 | PART2 값 | 원본 값 | 원본 출처 | Severity |
|---|---------|---------|--------|----------|----------|
| 1 | L528 | i18n: `ko-KR/en-US` (2개 언어) | ko-KR (default), en-US, **ja** (Japanese) — 3개 언어 | D2.0-08 L54, L1752 "Korean (default), English, Japanese UI strings" | **HIGH** — D2.0-08이 명시한 일본어(ja) 지원이 PART2 §3 V1-Phase 4에서 누락. §6.1에서도 언급 없음 |
| 2 | L807 | Hooks 8개: …**useAutonomy**, **useLog** | Hooks 8개: …**useApproval**, **useConfig** | PHASE_B §B.2 L317-324 | **HIGH** — 2개 Hook 이름 불일치. v11.0.0에서 PHASE_B2 §3.1 정본 교체 기록 있으나 PART2에 이전 버전 잔존 |
| 3 | L809 | Stores 7개: …**authStore** | Stores 7개: …**configStore** | PHASE_B §B.2 L325-332 | **HIGH** — 1개 Store 이름 불일치. v11.0.0 정본 교체 기록 있으나 PART2에 이전 버전 잔존 |
| 4 | L818 | 7 페이지: …**NodeDetail** | 7 페이지: …**CostPage** | PHASE_B §B.2 L308-315 | **HIGH** — 7번째 페이지 불일치. D2.0-08 S7C-074 CostDashboard V1/CRITICAL |
| 5 | L70, L1763 | §2: "React 18", §7: "React 18.3 통일" | `react ^18.3.0` | PHASE_B L716-717 | **MEDIUM** — PART2 내부 불일치 (§2 "React 18" vs §7 "React 18.3"). 구현 차단은 아님 |
| 6 | L528 #14 | CLI: `vamos run/approve/status/cost/memory` (5개) | CLI: 6개 (…+ **policy**) | D2.0-08 §2.3 L286-293 | **MEDIUM** — PART2 §3에서 `policy` 누락. §6.1.1(L784)에서는 6개 정확 기재. PART2 내부 불일치 |

---

## Dim B — NO_SOURCE

| # | PART2:행 | PART2 내용 | 검색한 파일/패턴 | 판정 |
|---|---------|-----------|---------------|------|
| 1 | L787-801 | ~44 React 컴포넌트 (11그룹) | D2.0-08: S7C-001~104 (V1~V3 전체 104개); PHASE_B: 8그룹 ~30개 | **MEDIUM** — D2.0-08 V1/CRITICAL 21개, V1/HIGH 76개. PART2 ~44는 핵심 선별이나 선별 기준 미명시 |

---

## Dim B — MISSING

| # | 구분 | 원본 출처 | 누락 내용 | Severity |
|---|------|----------|---------|----------|
| 1 | 역방향 | D2.0-08 L81-92 | **V3 Reserved Slots** (D8-V3-SLOT-01~04: V3 이벤트 타입, 반응형/모바일, 컴포넌트 라이브러리 확장, 자동 폴백 시각화) — PART2 어디에도 미언급 | **MEDIUM** |
| 2 | 역방향 | D2.0-08 L1236-1254 | **Section 9 FREEZE**: Fixed Dock (Option A) = DEFAULT/FREEZE, Overlay/Collapsible (Option B) = KEEP/Alternative — PART2 §6.1에서 이 UI 고정 결정 미기재 | **MEDIUM** |

---

## Dim B — SOURCE_CONFLICT

| # | 출처A=값 | 출처B=값 | 정본 우선순위 판정 |
|---|---------|---------|------------------|
| 1 | **PART2 §6.1.4** (L818): 7 페이지 = …NodeDetail | **PHASE_B** (L308-315): 7 페이지 = …CostPage | PHASE_B가 구현 디렉터리 구조 정의 → 구현 정본. **권고**: NodeDetail→CostPage 교체 또는 8 페이지로 확장 |
| 2 | **PART2 §6.1.3** (L807): useAutonomy, useLog | **PHASE_B** (L322-323): useApproval, useConfig | v11.0.0 "PHASE_B2 §3.1 정본" 채택 기록 → **PHASE_B 정본** |
| 3 | **PART2 §6.1.3** (L809): authStore | **PHASE_B** (L332): configStore | v11.0.0 "Stores 2/7 정본 교체" 기록 → **PHASE_B 정본** |
| 4 | **D2.0-08** (L1772-1773): V2 = "Tauri+React" + "Next.js+PWA" | **PART2**: PWA 미언급 | D2.0-08이 V2 PWA 명시(S7C-054). PART2 V2 범위에 미반영. **정본**: D2.0-08 |
| 5 | **PART2 §3** (L528): i18n = ko/en (2개) | **D2.0-08** (L1752): i18n = ko/en/**ja** (3개) | **D2.0-08 정본**. PART2에 ja 추가 필요 |

---

## Dim C — IMP_IMPOSSIBLE

| # | PART2:행 | 명세 내용 | 불가 사유 | 대안 제안 | Severity |
|---|---------|---------|---------|---------|----------|
| (해당 없음) | | | | | |

---

## Dim C — IMP_MISSING

| # | PART2:행 | 명세 내용 | 부족 정보 | Severity |
|---|---------|----------|----------|----------|
| 1 | L859-868 | Failure/Fallback UI 규칙 (§6.1.7) — 4개 에러코드 예시 + "전체 목록 D2.1-D2 참조" | D2.1-D2/D2.1-D8 **파일 미존재**. 전체 10개 에러코드 + 9개 폴백 행동 목록이 PART2에 미기재. 원본 검증 불가 | **HIGH** |
| 2 | L803-810 | 7 Store 상호의존성 | 7개 Zustand 스토어 간 **구독/의존 관계** 미정의. 순환 의존 방지 규칙 미기재 | **MEDIUM** |
| 3 | L837-857 | Hologram 스트리밍 (UI_S4 STREAMING) | 스트리밍 프로토콜 미정의: SSE vs WebSocket vs Tauri Event, 청크 크기, 재연결 전략 미기재 | **MEDIUM** |

---

## Dim C — IMP_CONFLICT

| # | 출처A:행:값 | 출처B:행:값 | 충돌 내용 | 판정 |
|---|-----------|-----------|---------|------|
| (해당 없음) | | | | |

---

## Dim C — IMP_OK (12항목)

| # | 항목 | 판정 근거 |
|---|------|----------|
| 1 | 3-Column fluid Tauri WebView | Tauri WebView2(Windows)/WebKit(macOS)에서 CSS Flexbox/Grid 완전 지원. react-resizable-panels 활용 가능 |
| 2 | Builder/Hologram 전환 | React 조건부 렌더링 또는 React Router 중첩 라우트로 구현 가능. 단일 SPA 내 뷰 전환 표준 패턴 |
| 3 | 44 컴포넌트 props | TypeScript 인터페이스 정의. PART2 §6.1.2에 11그룹별 핵심 컴포넌트 명시. Zod 3.24 연동 가능 |
| 4 | 8 Hook 리턴 타입 | 표준 React Custom Hook 패턴. TypeScript 제네릭으로 리턴 타입 정의 가능 |
| 5 | useTauriIPC wrapping | @tauri-apps/api 2.2(PHASE_B L720)의 invoke() 함수를 Custom Hook으로 래핑. 표준 패턴 |
| 6 | UI 9-state 관리 | PART2 §6.1.6에 9개 상태(UI_S0~UI_S8) 전이 테이블 정의. Zustand 또는 XState로 구현 가능 |
| 7 | 7 페이지 라우팅 | react-router-dom 6.28(PHASE_B L718) 활용. 7개 라우트 정의 충분 |
| 8 | i18n 키 관리 | react-i18next + namespace별 JSON 파일(locales/{locale}/{namespace}.json). D2.0-08 L75에 구조 정의 |
| 9 | CSS Custom Properties | 표준 CSS 기능. ORANGE/BLUE 테마 변수 정의 및 다크/라이트 전환 가능 |
| 10 | CLI 통합 | Tauri CLI(Rust clap) + 동일 LogEvent 네임스페이스(ui.cli.*) 공유. D2.0-08 §2.3 L300-303 동기화 규칙 |
| 11 | Flow Edge 애니메이션 | @xyflow/react 12.4(PHASE_B L722) 의존성 포함. Edge 커스텀 렌더링 및 애니메이션 지원 |
| 12 | RBAC 프론트/백엔드 | PART2 §6.1.8에 4역할(OWNER/ADMIN/OPERATOR/VIEWER) 정의. 화면별 접근 제어 테이블 완비 |

---

## Phase 0 교차 참조

| # | 0-D.json 항목 | PART2 값 | 0-D.json 값 | 판정 |
|---|--------------|---------|------------|------|
| 1 | 3-Column 레이아웃 (LOCK) | 좌 250-300px / 중앙 flex / 우 350-400px | 동일 | ✅ MATCH |
| 2 | Builder/Hologram 이중 뷰 (LOCK) | Builder(Cockpit) + Hologram(Experience) | 동일 | ✅ MATCH |
| 3 | Design System 색상 (LOCK) | ORANGE #F97316 / BLUE #00F6FF / BG #1E1E1E | 동일 | ✅ MATCH |
| 4 | i18n 지원 언어 (LOCK) | ko-KR / en-US (2개) | ko / en / ja (3개) | ⚠️ MISMATCH (MISMATCH #1) |

---

## Dim B — MATCH 확인

| # | v8 B# | 검증 항목 | PART2 값 | 원본 값 | 원본 출처 | 판정 |
|---|-------|----------|---------|--------|----------|------|
| 1 | B#7 | Builder/Hologram View | Builder(Cockpit): 리소스 트리+그래프+로그/승인/비용; Hologram(Experience): 타임라인+스트리밍+Glass HUD | 동일 | D2.0-08 §2.1/§2.2 L146-276 | **MATCH** |
| 2 | B#8 | Design System | CSS Custom Properties, ORANGE(#F97316)/BLUE(#00F6FF), 배경 #1E1E1E | 동일 | D2.0-08 §10 L1283-1298 | **MATCH** |
| 3 | B#2 | 3-Column 레이아웃 | 좌(250-300px)/중앙(flex)/우(350-400px) 리사이즈 | Builder View 동일 구조 | D2.0-08 §2.1 L305-315 | **MATCH** |
| 4 | B#10 | UI 구현 결정 4항목 | 4건(레이아웃 수/라우트 수/다크모드 변수/애니메이션) | PART2 자체 정의 (§6.1.4) | PART2 L812-821 | **MATCH** |
| 5 | B#11 | 멀티모달 UI V2/V3 진화 | V2: 음성 입력+이미지 분석, V3: 실시간 협업+AR 확장 | V2/V3 진화 경로 일치 | D2.0-08 §11 | **MATCH** |

> **B#13 (V2 PWA SOURCE_CONFLICT)**: SC #4에서 판정 — D2.0-08이 V2 PWA 명시(S7C-054)하나 PART2 미반영.

---

## 종합 판정

### HIGH (5건)

| # | 유형 | 항목 | 내용 |
|---|------|------|------|
| H-1 | MISMATCH | i18n 일본어(ja) 누락 | D2.0-08이 ko/en/ja 3개 언어 명시, PART2는 ko/en만 기재 |
| H-2 | MISMATCH | Hooks 2개 이름 불일치 | PART2(useAutonomy/useLog) vs PHASE_B 정본(useApproval/useConfig). v11.0.0 정본 교체 후 미반영 |
| H-3 | MISMATCH | Stores 1개 이름 불일치 | PART2(authStore) vs PHASE_B 정본(configStore). v11.0.0 정본 교체 후 미반영 |
| H-4 | MISMATCH | 페이지 목록 불일치 | PART2(NodeDetail) vs PHASE_B(CostPage). D2.0-08 CostDashboard V1/CRITICAL |
| H-5 | IMP_MISSING | Failure/Fallback 전체 목록 미기재 | D2.1-D2/D2.1-D8 파일 미존재. 에러코드 10개+폴백 9개 검증 불가. 구현 시 에러 핸들링 완전성 보장 불가 |

### MEDIUM (8건)

| # | 유형 | 항목 | 내용 |
|---|------|------|------|
| M-1 | MISMATCH | React 18 vs 18.3 내부 불일치 | PART2 §2 "React 18" vs §7 "React 18.3 통일". PHASE_B ^18.3.0 |
| M-2 | MISMATCH | CLI policy 커맨드 누락 | PART2 §3에서 6개 중 policy 누락. §6.1.1에서는 6개 정확 기재 |
| M-3 | NO_SOURCE | ~44 컴포넌트 선별 기준 미명시 | D2.0-08 V1 범위 97개 중 ~44 선별 근거 부재 |
| M-4 | MISSING | V3 Reserved Slots 미반영 | D2.0-08 D8-V3-SLOT-01~04. V3 설계 시 누락 위험 |
| M-5 | MISSING | Section 9 FREEZE 미반영 | D2.0-08 Fixed Dock FREEZE 결정이 PART2 §6.1에 미기재 |
| M-6 | SC | V2 PWA 누락 | D2.0-08이 V2 PWA 명시(S7C-054, Next.js+PWA). PART2 V2 범위에 미반영 |
| M-7 | IMP_MISSING | Store 상호의존성 미정의 | 7개 Zustand 스토어 간 구독/의존 관계 및 순환 의존 방지 규칙 미기재 |
| M-8 | IMP_MISSING | Hologram 스트리밍 프로토콜 미정의 | SSE vs WebSocket vs Tauri Event 미지정. 청크 크기, 재연결 전략 미기재 |

---

## 검증 완료 선언

- 수정 전: HIGH **5**건, MEDIUM **8**건 = 총 **13**건 (SOURCE_CONFLICT **5**건 중 4건은 severity에 포함, 1건(V2 PWA) M-6 독립)
- 수정 후: 미수정
- Dim B: Forward **12** + Reverse **2** = **14** 체크 — MATCH **5**, MISMATCH **6**, NO_SOURCE **1**, MISSING **2**
- Dim C: **15**항목 — IMP_OK **12**, IMP_MISSING **3**, IMP_CONFLICT **0**, IMP_IMPOSSIBLE **0**
- ✅ BLOCKER **0**건 — Phase 2 차단 사유 없음. HIGH **5**건은 Phase 2에서 PART2 수정 필요.
