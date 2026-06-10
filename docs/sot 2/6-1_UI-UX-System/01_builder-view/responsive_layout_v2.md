# 반응형 레이아웃 V2 — L3 상세 명세

> **도메인**: 6-1_UI-UX-System / 01_builder-view
> **세션**: P2-2 (Phase 2)
> **버전**: v1.0 (2026-04-26)
> **정본 출처**: D2.0-08 §3 (3-Column Layout 정본) / Part2 §6.1.1 (3-Column 핵심 레이아웃) / Part2 §6.1.4 (구현 결정 4건 ISS-2 RESOLVED) / AUTHORITY_CHAIN §4 LOCK L2~L4/L11/L12
> **종합계획서**: §7.3 P2-2 (L1618~L1650)
> **상위 SoT**: STEP7-C UI/UX 전수비교 작업가이드 (manifest L72 단일, 235 L)
> **선행**: 01_builder-view/fluid_layout.md (V1 372L, 3-Column 정본)

---

## 1. 개요

V1 3-Column 고정 레이아웃 (좌 250-300px / 중앙 Flex-grow / 우 350-400px, 최소 1280×720) 위에 V2 반응형 브레이크포인트 4 단계 (1440 / 1280 / 1024 / 768)를 정의하고, 각 단계의 동작 규칙 (패널 접기 / 최소 폭 / 오버플로우)를 L3 로 명시한다. 4-1 Rust-Tauri 윈도우 크기 이벤트 인터페이스는 정의만 (4-1 IPC 커맨드 72 재정의 ❌).

**범위**: UI 레이어(6-1) — CSS Container Queries / Media Queries / 패널 표시 정책. Tauri 백엔드 윈도우 관리는 4-1 소관.

---

## 2. LOCK 참조 (4-field verbatim, AUTHORITY_CHAIN §4)

| LOCK ID | 항목 | 정본 출처 | LOCK 값 |
|---------|------|----------|---------|
| **L2** | 3-Column 좌측 폭 | D2.0-08 §2.1.1 / Part2 §6.1.1 | 250-300px |
| **L3** | 3-Column 우측 폭 | D2.0-08 §2.1.1 / Part2 §6.1.1 | 350-400px |
| **L4** | 3-Column 중앙 | D2.0-08 §2.1.1 / Part2 §6.1.1 | Flex-grow (유동) |
| **L11** | V1 최소 해상도 | D2.0-08 §3.1 | 1280 x 720 (데스크톱 전용) |
| **L12** | Tauri 기본 크기 | D2.0-08 §3.1 | 1440 x 900 |
| **L7** | 다크모드 | D2.0-08 §10.1 / Part2 V1-P4 | 기본값 = Dark (#1E1E1E), Light는 토글 |
| **L17** | 상태 전이 지연 | D2.0-08 §4.4 | 최대 500ms |
| **L19** | 이벤트 네이밍 | D2.0-08 §5.1 | `ui.{layer}.{subject}.{action}` |

> 본 V2 문서는 LOCK 신규 추가/변경 0건 — 1280×720 (V1 최소 LOCK L11)은 데스크톱 전용 기준선 유지. 768/1024 브레이크포인트는 **V3 모바일 확장 예고** 슬롯 (반응형 정책 정의만, V3 실체화 시점 LOCK 재평가).

---

## 3. ISS-2 구현 결정 4건 (Part2 §6.1.4 RESOLVED 결과 반영)

> **Part2 §6.1.4 L4597~L4606 정본 인용**:

| # | 항목 | V2 결정 | 근거 |
|---|------|---------|------|
| 1 | 화면 레이아웃 수 | 4 레이아웃 (3-Column / Builder / Hologram / CLI) + 7 페이지 (V1 확정) | D2.0-08 §4, §6 (§6.1.4) S5-232 v26 |
| 2 | 라우트 수 | 10 라우트 확정 (1 루트 레이아웃 + 7 페이지 + 1 리디렉트 + 1 404) | D2.0-08 §6, PHASE_B2 §3.1 (seven_pages.md §3 RESOLVED) |
| 3 | 다크모드 변수 | ORANGE/BLUE 테마 CSS Custom Properties (Tailwind extend, V1 확정) | D2.0-08 §10 |
| 4 | 애니메이션 설정 | CSS transition 기본 + 제한적 Framer Motion (혼합 전략) — 단순 전환은 CSS, Graph Canvas/드래그 등 복잡 인터랙션은 Framer Motion. reduce-motion 사용자 설정 존중 | D2.0-08 §2.1.2/§10.2 (seven_pages.md §7.4 RESOLVED) |

> ISS-2 RESOLVED 결과는 V1 phase 1 단계 확정. V2 반응형 작업은 4 결정값 기반 위에 build (재정의 0건).

---

## 4. 반응형 브레이크포인트 4 단계 정의

> 본 §4 가 V2 반응형 정책 정본. 1440 풀 / 1280 최소 (LOCK L11) / 1024 태블릿 / 768 모바일 (V3 예고).

### 4.1 BP-A: 1440px+ (풀 데스크톱, LOCK L12 기준)

| 항목 | 값 |
|------|-----|
| **Layout** | 3-Column 정상 — 좌 280px / 중앙 flex-grow / 우 380px (LOCK L2/L3/L4 권장값 중간) |
| **패널 동작** | 좌/우 패널 모두 펼침. 좌 패널 리사이즈 250-300px, 우 패널 리사이즈 350-400px. 사용자 드래그 가능. |
| **오버플로우** | 중앙 패널 콘텐츠 자동 스크롤. 좌/우는 콘텐츠 길이에 따라 내부 스크롤. |
| **Glass HUD** | 우측 패널에 fix overlay (P2-1 기능 #5 `MultimodalGlassHUD`) |

### 4.2 BP-B: 1280-1439px (V1 최소, LOCK L11)

| 항목 | 값 |
|------|-----|
| **Layout** | 3-Column 압축 — 좌 250px (LOCK L2 최소) / 중앙 flex-grow / 우 350px (LOCK L3 최소) |
| **패널 동작** | 좌/우 모두 최소값 고정 (드래그로 더 줄일 수 없음). 사용자 토글 시 좌 패널 접기 가능 (펼침 ↔ 접힘 50px 아이콘 모드) |
| **오버플로우** | 중앙 패널 우선. 우 패널 접근성 보장 (Glass HUD 가독성) |
| **Glass HUD** | 우측 패널 fix overlay 유지. 알림 토스트 중앙 상단으로 이동 (좌 패널 침범 방지) |

### 4.3 BP-C: 1024-1279px (태블릿 모드, V2 신규)

| 항목 | 값 |
|------|-----|
| **Layout** | 2-Column — 좌 패널 자동 접기 (50px 아이콘 모드, hover/click 시 250px 슬라이드 인 오버레이) / 중앙 flex-grow / 우 350px |
| **패널 동작** | 좌 패널 = drawer (오버레이, 외부 클릭 시 자동 닫기). 우 패널은 `<UnifiedSearchPanel>` 등 Glass HUD 우선순위 유지. |
| **오버플로우** | 좌 drawer 열림 시 중앙/우 패널은 dim 처리 (반투명 black overlay 0.4 opacity) |
| **Glass HUD** | 우측 패널 유지. 알림 토스트는 중앙 하단으로 이동 (방해 최소화) |
| **상태 전이** | window resize → drawer 자동 전환 ≤ 500ms (LOCK L17) |

### 4.4 BP-D: ~1023px / 768-1023px (모바일 V3 예고)

| 항목 | 값 |
|------|-----|
| **Layout** | 1-Column 단일 (V3 정식 출시 시점 확정. V2 단계는 "비지원 안내 화면" 표시 + 1280px+ 디스플레이 사용 안내) |
| **패널 동작** | V2 단계: 좌/우 모두 모달 형태로 전환 — 하단 탭 바 (Builder / Hologram / Settings) |
| **오버플로우** | 중앙 단일 컬럼 세로 스크롤 |
| **Glass HUD** | V3 모바일에서 floating bottom sheet 로 재설계 예정 (V2 비지원) |
| **V2 동작** | 768~1023px 진입 시 한 번 `<UnsupportedResolutionModal>` 표시 + dismiss 후에도 사용 가능하나 layout 가독성 보장 ❌ (사용자 책임) |

> **Phase 3 연계**: BP-D 768px 모바일 V3 정식 출시 시점에 LOCK L11 재평가 필요 (현 V1 LOCK L11 = 1280×720 데스크톱 전용 — V3 시점 까지 유효).

---

## 5. CSS 전략 결정

### 5.1 Container Queries vs Media Queries

| 전략 | 채택 | 사유 |
|------|------|------|
| **Media Queries (`@media`)** | ✅ 주력 | window 전체 크기 기반 BP-A/B/C/D 분기 단순. 모든 브라우저 지원 (Chromium-based Tauri 환경) |
| **Container Queries (`@container`)** | 보조 | 우측 Glass HUD 패널 내부 카드 가독성 (≤ 350px 폭 컨테이너에서 검색 결과 셀 자동 1열 ↔ 2열 토글) |
| **JS resize listener** | 회피 | reflow 비용 + Tauri 환경에서 native resize 이벤트 (4-1 IPC) 가 더 정확 |

### 5.2 Tailwind CSS 전략

```css
/* V1 design_system_orange_blue.md 의 토큰 체계 위에 V2 반응형 추가 — 토큰 재정의 ❌ */
/* tailwind.config.ts extend (V1 확정) */
screens: {
  'bp-a': '1440px',  /* 풀 데스크톱 */
  'bp-b': '1280px',  /* V1 최소 LOCK L11 */
  'bp-c': '1024px',  /* 태블릿 V2 */
  'bp-d': '768px',   /* 모바일 V3 예고 */
}
```

### 5.3 페이지 레이아웃 클래스 정책

| BP | 좌 패널 | 중앙 | 우 패널 |
|----|---------|------|---------|
| `bp-a` | `w-[280px] flex-shrink-0` | `flex-1 min-w-0` | `w-[380px] flex-shrink-0` |
| `bp-b` | `w-[250px] flex-shrink-0` | `flex-1 min-w-0` | `w-[350px] flex-shrink-0` |
| `bp-c` | `fixed inset-y-0 left-0 w-[250px] z-30 transform` (drawer) | `flex-1 min-w-0` | `w-[350px] flex-shrink-0` |
| `bp-d` | `hidden` (V2: 모달) | `w-full` | `hidden` (V2: 모달) |

---

## 6. 4-1 Rust-Tauri 윈도우 크기 이벤트 인터페이스 (참조만)

> **AUTHORITY_CHAIN §5.2 정본 인용** — 6-1 = 프론트엔드 호출 인터페이스. 4-1 IPC 커맨드 72개 정본 재정의 ❌.

### 6.1 6-1 측 사용 인터페이스 (프론트엔드 호출부)

```typescript
// 6-1 측 호출 인터페이스 정의 — 실제 IPC 핸들러는 4-1 소관
interface TauriWindowEvent {
  width: number;
  height: number;
  // 6-1 은 width 만 BP 분기에 사용. height 는 향후 가로 모드 지원 시 확장.
}

// 6-1 useTauriWindow Hook (이미 V1 LOCK L14 8 Hooks 중 useTauriIPC 의 thin wrapper)
function useTauriWindowResize(callback: (event: TauriWindowEvent) => void): void;

// 4-1 측 등록되어야 하는 이벤트 채널 (참조만, 등록 정의는 4-1 소관)
//   채널: "vamos://ui:window_resized"
//   페이로드: TauriWindowEvent
//   발행 빈도: throttle 100ms (4-1 측 정책, 6-1 은 수신만)
```

### 6.2 6-1 측 BP 분기 로직

```typescript
function classifyBreakpoint(width: number): "bp-a" | "bp-b" | "bp-c" | "bp-d" {
  if (width >= 1440) return "bp-a";
  if (width >= 1280) return "bp-b";  // LOCK L11 minimum
  if (width >= 1024) return "bp-c";
  return "bp-d";  // V3 예고 영역
}

// debounce 200ms 후 BP 변경 시점에 ui.builder.layout.bp_changed 이벤트 발행 (LOCK L19 네이밍 준수)
```

> **본 §6 가 정의하지 않는 것** (4-1 소관): Tauri 윈도우 생성 / `set_size` / `set_min_size` 1280×720 강제 / OS 별 윈도우 매니저 통합. 4-1 IPC 커맨드 72개 (Storage 18 + Safety 19 + Core 15 + Agent 15 + UI 5) 중 UI 5 그룹의 `vamos:ui:*` 가 본 인터페이스 발행자.

---

## 7. 반응형 정책 9요소 (E1~E9)

### 7.1 Layout Resize 컴포넌트 (`<ResponsiveLayoutShell>`)

| L3 요소 | 내용 |
|---------|------|
| **E1 Input** | { width: number, height: number } from 4-1 IPC `vamos://ui:window_resized` |
| **E2 State** | UI_S0~UI_S8 모든 상태에서 수동적 (구조 layer). BP 변경 시 BP 전이 ≤ 500ms (LOCK L17). |
| **E3 Output** | DOM 클래스 갱신 (BP-A/B/C/D), drawer 토글 (BP-C), 모달 표시 (BP-D) |
| **E4 Class/API** | `<ResponsiveLayoutShell>` 최외곽 wrapper, slot: left / center / right |
| **E5 Style** | Tailwind extend screens (bp-a/bp-b/bp-c/bp-d). 다크 배경 #1E1E1E 유지 (LOCK L7) |
| **E6 Accessibility** | drawer (BP-C) 키보드 Esc 닫기. 모달 (BP-D) focus trap. role="navigation" / role="main" / role="complementary" 3 영역 명확 분리 |
| **E7 Error** | `INVALID_DIMENSION` (width<320 / height<200) → fallback BP-D + 경고 토스트 |
| **E8 Test** | unit: classifyBreakpoint() 4 분기. integration: window resize mock → BP 전이. visual: 1440 / 1280 / 1024 / 768 4 캡처 |
| **E9 Event** | `ui.builder.layout.bp_changed` / `.drawer_opened` / `.drawer_closed` / `.unsupported_resolution_shown` (LOCK L19) |

---

## 8. STEP7-C 상위 SoT 매핑 (P2-2 범위)

| STEP7-C 항목 ID | 출처 (235L) | V2 P2-2 매핑 |
|-----------------|-------------|--------------|
| S7C-001 3-Column 레이아웃 | Part 1 (L45) | §4 BP-A/B/C 전체 |
| S7C-002 대화 목록 사이드바 | Part 1 (L46) | §4.3 BP-C drawer 동작 (좌 패널 = 대화 목록) |
| S7C-007 반응형/모바일 대응 | Part 1 (L51) | §4.3 BP-C 태블릿 + §4.4 BP-D 모바일 V3 예고 |

> **upstream baseline**: STEP7-C `9c7b4ea26c2d1d1d6cf32eaa8089e41ee5a16ce913c6f3cb4eed1e1b0f11f709` (235 L) UNCHANGED.

---

## 9. Phase 배정 및 의존성

| 항목 | 값 |
|------|-----|
| **Phase 배정** | Phase 2 (V2 반응형 리팩토링) |
| **Phase 1 의존성** | fluid_layout.md (V1 3-Column 정본) / builder_view_cockpit.md (Builder Cockpit) |
| **Phase 3 이월** | BP-D 768px 모바일 정식 V3 출시 (1-Column + bottom navigation), LOCK L11 재평가 (모바일 영역 추가 시) |
| **교차 도메인** | 4-1 Rust-Tauri (인터페이스 명세만, IPC 72 재정의 ❌, 참조만) |

---

## 10. 검증 (§7.3 P2-2 검증 항목 4/4 충족)

- [x] **LOCK L2/L3/L4 준수**: §4.1~§4.3 좌 250-300 / 우 350-400 / 중앙 flex-grow 모든 BP 에서 명시 (BP-A 280/380, BP-B 250/350, BP-C 250(drawer)/350)
- [x] **LOCK L11/L12 반영**: §4.2 BP-B = LOCK L11 1280 최소, §4.1 BP-A = LOCK L12 1440 풀
- [x] **4-1 Rust-Tauri 윈도우 크기 이벤트 연동 명시**: §6 인터페이스 + AUTHORITY §5.2 경계 인용 (4-1 IPC 72 재정의 ❌)
- [x] **V3 모바일 확장 예고**: §4.4 BP-D + §9 Phase 3 이월

---

## 11. 변경 이력

| 일자 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-26 | v1.0 | NEW (P2-2) — V2 반응형 BP-A/B/C/D 4 단계 + Tailwind extend + 4-1 인터페이스 (참조만). ISS-2 RESOLVED 결과 위에 빌드 (재정의 0) |

<!-- END OF DOCUMENT -->
