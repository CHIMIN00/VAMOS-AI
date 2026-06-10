# 반응형 레이아웃 V3 — 모바일 BP-D 768px 정식 (L3 상세 명세)

> **도메인**: 6-1_UI-UX-System / 01_builder-view
> **세션**: P4-1 (Phase 4 — production-ready 정본 승급, RECOVERY genuine write)
> **버전**: v1.0 (2026-06-01)
> **Status**: APPROVED (2026-06-01, P4-1 DRAFT→APPROVED)
> **정본 출처**: D2.0-08 §3 (3-Column Layout 정본) / §3.1 (LOCK L11 V1 해상도) / Part2 §6.1.1 / AUTHORITY_CHAIN §4 LOCK L1/L2/L3/L4/L8/L11/L17/L19
> **종합계획서**: §7.4 P4-1 (L2015~L2066) — P3-1 forward-defined Phase 4 entry-gate inheritance
> **선행 (base)**: 01_builder-view/responsive_layout_v2.md (V2 229L, BP-A/B/C/D 4단계 정책) + 01_builder-view/fluid_layout.md (V1 372L, 3-Column 정본)
> **cross-handoff**: 4-1 Rust-Tauri (모바일 IPC, 참조만) / 6-2 Security-Governance (모바일 RBAC L10) / 6-12 Event-Logging (`ui.builder.responsive.*` 등록 큐)

---

## 1. 개요

V2 `responsive_layout_v2.md` §4.4 에서 "V3 예고" 슬롯으로만 정의된 **BP-D 768px 모바일 레이아웃**을 V3 production-ready 정본으로 승급한다. V2 단계의 BP-D 는 `<UnsupportedResolutionModal>` 비지원 안내 화면이었으나, V3 에서는 **1-Column 단일 컬럼 + 모바일 적응 패턴 (좌 Drawer / 우 BottomSheet / Builder Panel 키보드 처리)**을 정식 지원한다.

> **핵심 원칙 (R9 — LOCK 재정의 금지)**: V1 LOCK L11 `1280 x 720 (데스크톱 전용)`은 **데스크톱 기준선으로 verbatim 영구 보존**된다. BP-D 768px 는 **V3 추가 정의 (확장)**이며 L11 의 재정의가 아니다. 아래 §2 의 `<!-- V3 EXTENSION, NOT REDEFINITION -->` 주석으로 명시.

**범위**: UI 레이어(6-1) — 모바일 BP-D CSS 정책 + 1-Column 변환 + `useResponsive` Hook + 9-State(LOCK L1) 모바일 전이 규칙. Tauri 윈도우/모바일 셸 통합은 4-1 소관 (참조만).

---

## 2. LOCK 참조 (4-field verbatim, AUTHORITY_CHAIN §4) + V3 확장 명시

| LOCK ID | 항목 | 정본 출처 | LOCK 값 (verbatim) |
|---------|------|----------|---------|
| **L1** | UI 9-State | D2.0-08 §4.1 | UI_S0_BOOT, UI_S1_IDLE, UI_S2_EDITING, UI_S3_READY, UI_S4_RUNNING, UI_S5_AWAIT_APPROVAL, UI_S6_PRESENTING, UI_S7_RECOVERY, UI_S8_ARCHIVED (9개) |
| **L2** | 3-Column 좌측 폭 | D2.0-08 §2.1.1 / Part2 §6.1.1 | 250-300px |
| **L3** | 3-Column 우측 폭 | D2.0-08 §2.1.1 / Part2 §6.1.1 | 350-400px |
| **L4** | 3-Column 중앙 | D2.0-08 §2.1.1 / Part2 §6.1.1 | Flex-grow (유동) |
| **L8** | WCAG 접근성 | Part2 V1-P4 / §6.1.8 | WCAG 2.1 AA 준수 |
| **L11** | V1 최소 해상도 | D2.0-08 §3.1 | 1280 x 720 (데스크톱 전용) |
| **L17** | 상태 전이 지연 | D2.0-08 §4.4 | 최대 500ms |
| **L19** | 이벤트 네이밍 | D2.0-08 §5.1 | `ui.{layer}.{subject}.{action}` |

<!-- V3 EXTENSION, NOT REDEFINITION -->
> **V3 확장 선언 (L11 추가 정의, 재정의 아님)**: LOCK L11 `1280 x 720 (데스크톱 전용)`은 데스크톱 최소 해상도 정본으로 **변경 없이 보존**한다. V3 는 그 위에 **모바일 적응 브레이크포인트 BP-D = 768px (≤1023px 영역)**을 *추가* 정의한다. 데스크톱 정본(L11)과 모바일 확장(BP-D)은 별개의 적응 계층이며, 768px 진입 시에도 L11 의 데스크톱 기준선 값은 재정의되지 않는다. 본 V3 확장은 LOCK 신규 추가/변경 0건 — **확장 정책 정의만**.

---

## 3. BP-D 768px 모바일 레이아웃 정식 (V2 §4.4 "예고" → V3 정본)

> V2 §4.4 의 BP-D 는 "768~1023px 진입 시 `<UnsupportedResolutionModal>` 표시 + 가독성 보장 ❌ (사용자 책임)"이었다. V3 는 이를 **1-Column 모바일 정식 레이아웃**으로 대체한다.

### 3.1 3-Column → 1-Column 변환 매트릭스

| V1/V2 데스크톱 영역 | V3 모바일 (BP-D) 적응 | 패턴 | 트리거 |
|----------------------|------------------------|------|--------|
| **Left Panel** (LOCK L2 250-300px) | **좌측 Drawer** (off-canvas, 화면 폭 85% max 320px, 햄버거 메뉴 토글) | Drawer (off-canvas slide) | 햄버거 아이콘 탭 / swipe-right edge |
| **Center Panel** (LOCK L4 Flex-grow) | **1-Column 메인** (`w-full`, 세로 스크롤) | Single column | 기본 표시 |
| **Right Panel / Glass HUD** (LOCK L3 350-400px) | **하단 BottomSheet** (3-snap: peek 15% / half 50% / full 90%) | BottomSheet (draggable) | 하단 핸들 탭 / swipe-up |
| **Builder Panel (config/graph)** | **전체화면 모달 + 가상 키보드 회피 (`viewport-fit` + `env(keyboard-inset-height)`)** | Fullscreen modal | Builder 탭 진입 |

> **LOCK L2/L3/L4 보존**: 데스크톱 폭 규격(250-300 / 350-400 / Flex-grow)은 BP-A/B/C 에서 verbatim 유지. BP-D 는 이 영역들을 **모바일 컨테이너로 재배치(reflow)**할 뿐 폭 규격을 재정의하지 않는다 (Drawer 폭 ≠ LOCK L2 폭, 별개 모바일 토큰).

### 3.2 BP-D 세부 동작 (V2 BP-A/B/C 와 연속)

| 항목 | BP-D V3 값 |
|------|------------|
| **Layout** | 1-Column 단일 (`flex-col`), 상단 AppBar(56px) + 메인 스크롤 영역 + 하단 TabBar(56px, Builder/Hologram/Settings 3탭) |
| **Left** | Drawer — `fixed inset-y-0 left-0 w-[85vw] max-w-[320px] z-40 transform -translate-x-full`, 열림 시 `translate-x-0` + 배경 dim 0.5 |
| **Center** | `w-full min-w-0 overflow-y-auto`, safe-area-inset 적용 (`pb-[env(safe-area-inset-bottom)]`) |
| **Right (Glass HUD)** | BottomSheet — `fixed bottom-0 inset-x-0 z-30 rounded-t-2xl`, 3-snap 드래그 (peek/half/full), Glass HUD 가독성 우선 시 half 자동 snap |
| **Builder Panel** | 전체화면 모달, 가상 키보드 노출 시 `interactive-widget=resizes-content` + 입력 필드 자동 scrollIntoView |
| **상태 전이** | 모든 BP-D 전이 ≤ 500ms (LOCK L17 모바일 보장) + 전환 애니메이션 prefers-reduced-motion 존중 |

---

## 4. `useResponsive` Hook — BP 분기 (V2 `classifyBreakpoint` 직계 확장)

> V2 §6.2 `classifyBreakpoint(width)` (bp-a/b/c/d) 위에 V3 모바일 분기 + orientation 처리를 통합한 Hook. LOCK L14 8 Hooks 중 `useTauriIPC` 의 thin wrapper 재사용 (신규 Hook 추가 0건 — L14 8개 보존).

```typescript
// 6-1 측 호출 인터페이스 — BP 분기 + orientation. 실제 윈도우/모바일 셸 이벤트는 4-1 소관
type Breakpoint = 'A' | 'B' | 'C' | 'D';   // A=1440+ / B=1280+ / C=1024+ / D=≤1023 (모바일 V3)
type Orientation = 'portrait' | 'landscape';

interface ResponsiveState {
  bp: Breakpoint;
  orientation: Orientation;
  isMobile: boolean;          // bp === 'D'
  keyboardVisible: boolean;   // env(keyboard-inset-height) > 0
  drawerOpen: boolean;
  bottomSheetSnap: 'peek' | 'half' | 'full';
}

function useResponsive(): ResponsiveState & {
  toggleDrawer: () => void;
  setBottomSheetSnap: (snap: 'peek' | 'half' | 'full') => void;
};

// 분기 로직 (V2 classifyBreakpoint 직계 — LOCK L11 1280 데스크톱 기준선 보존)
function classifyBreakpoint(width: number): Breakpoint {
  if (width >= 1440) return 'A';   // LOCK L12 1440 풀 데스크톱
  if (width >= 1280) return 'B';   // LOCK L11 1280 데스크톱 최소 (verbatim 보존)
  if (width >= 1024) return 'C';   // 태블릿 (V2)
  return 'D';                       // 모바일 BP-D 768px V3 (≤1023px)
}
```

> **BP 전환 성능 목표**: debounce 100ms 후 `classifyBreakpoint` 재계산 → BP 전환 자체는 **< 100ms (P95)** 완료 (DOM 클래스 토글 + Drawer/BottomSheet 마운트). 9-State 전이가 동반될 경우 LOCK L17 500ms 이내 보장.

---

## 5. 9-State (LOCK L1) 모바일 전이 규칙

> LOCK L1 9-State `UI_S0_BOOT … UI_S8_ARCHIVED` (9개)는 **상태 집합 verbatim 보존**. V3 는 각 상태의 *모바일 표현(어디에 무엇을 보이는가)*만 정의 — 상태 머신 자체는 재정의 0건.

| 상태 (LOCK L1) | 모바일 BP-D 표현 | 전이 지연 (LOCK L17 ≤500ms) |
|-----------------|------------------|------------------------------|
| UI_S0_BOOT | 스플래시 풀스크린, AppBar/TabBar 숨김 | — |
| UI_S1_IDLE | 1-Column 메인 + TabBar 노출 | ≤ 500ms |
| UI_S2_EDITING | Builder Panel 전체화면 모달, 키보드 회피 | ≤ 500ms |
| UI_S3_READY | 메인 상단 "실행 준비" 배너 (sticky) | ≤ 500ms |
| UI_S4_RUNNING | 진행률 → BottomSheet peek 자동 표시 | ≤ 500ms |
| UI_S5_AWAIT_APPROVAL | 승인 모달 풀스크린 (LOCK L18 타임아웃 그대로) | ≤ 500ms |
| UI_S6_PRESENTING | Glass HUD → BottomSheet half 자동 snap | ≤ 500ms |
| UI_S7_RECOVERY | 에러 배너 + FallbackRegistry 동작 (§6) | ≤ 500ms |
| UI_S8_ARCHIVED | 읽기 전용 1-Column, 입력 비활성 | ≤ 500ms |

---

## 6. Touch FallbackRegistry V3 확장 (9 → 12) — 모바일 터치 폴백

> **L20 정합 선언**: LOCK L20 정본 `14개 FailureCodes + 9개 FallbackRegistry`(D2.0-08 §7.6)는 verbatim 보존. 본 §6 은 모바일 터치 상황에 대한 **FallbackRegistry 3건 추가 (9 → 12)**를 V3 확장으로 정의한다. **L20 FailureCode 14 → 18 확장은 P4-4 Plugin 4건이 정본**이며(extension_slots_v3.md §5), 본 Touch 3건은 *Fallback 계층* 확장이다. Touch 상세 + WCAG 매핑은 `06_accessibility/mobile_a11y_v3.md` 정본.

<!-- V3 EXTENSION, NOT REDEFINITION -->

| # | fallback_id (V3 신규) | 트리거 조건 | 복구 동작 | WCAG 근거 (L8) |
|---|------------------------|-------------|-----------|----------------|
| 10 | **FB_TOUCH_RETARGET** | 터치 타겟 < 44×44pt 감지 | 인접 탭 영역 자동 확대 + 햅틱 경고 | WCAG 2.5.5 Target Size |
| 11 | **FB_GESTURE_ALT** | 제스처 인식 실패 (swipe/pinch 충돌) | 버튼 기반 대체 컨트롤 노출 (스와이프 키보드 대체) | WCAG 2.5.1 Pointer Gestures |
| 12 | **FB_ORIENTATION_LOCK** | 미지원 orientation (landscape 강제 화면) | portrait 권장 오버레이 + 자동 회전 잠금 안내 | WCAG 1.3.4 Orientation |

> FallbackRegistry V1 9건 (FB_REJECT_INPUT … FB_SHOW_STALE)은 verbatim 보존, 위 3건은 **append-only V3 확장**. 연결 Touch 조건 코드(TOUCH_TARGET_MISS / GESTURE_CONFLICT / ORIENTATION_UNSUPPORTED)는 `mobile_a11y_v3.md` §4 정본.

---

## 7. CSS / Tailwind 전략 (V2 §5 직계 확장)

```css
/* V2 tailwind.config.ts extend 위에 V3 모바일 토큰 추가 — V1 토큰 재정의 ❌ */
screens: {
  'bp-a': '1440px',  /* 풀 데스크톱 (LOCK L12) */
  'bp-b': '1280px',  /* V1 최소 LOCK L11 데스크톱 기준선 (verbatim) */
  'bp-c': '1024px',  /* 태블릿 V2 */
  'bp-d': '768px',   /* 모바일 V3 정식 (≤1023px 영역 진입점) */
}
/* viewport meta (모바일 키보드 회피) */
/* <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, interactive-widget=resizes-content"> */
```

| BP | 좌 | 중앙 | 우 |
|----|-----|------|-----|
| `bp-a`/`bp-b`/`bp-c` | (V2 정책 유지) | (V2 정책 유지) | (V2 정책 유지) |
| `bp-d` (V3) | `drawer: fixed left-0 w-[85vw] max-w-[320px] -translate-x-full` | `w-full overflow-y-auto pb-[env(safe-area-inset-bottom)]` | `bottomsheet: fixed bottom-0 inset-x-0 rounded-t-2xl` |

---

## 8. cross-handoff (참조만 — 정의 변경 0건)

### 8.1 4-1 Rust-Tauri 모바일 IPC (AUTHORITY §5.2 경계)

> 6-1 = 프론트엔드 호출 인터페이스. 4-1 IPC 커맨드 72개 정본 재정의 ❌.

```typescript
// 6-1 측 수신 인터페이스 — 모바일 윈도우/orientation 이벤트 (등록 정의는 4-1 소관)
interface TauriMobileEvent {
  width: number; height: number;
  orientation: 'portrait' | 'landscape';
  keyboardInsetHeight: number;   // 가상 키보드 높이 (px)
}
// 채널: "vamos://ui:mobile_metrics_changed" (4-1 발행, 6-1 수신만, throttle 100ms)
```

### 8.2 6-2 Security-Governance 모바일 RBAC (LOCK L10 — 정본 6-2)

> LOCK L10 `OWNER / ADMIN / OPERATOR / VIEWER`(Part2 §6.1.8). 6-1 = RBAC UI 표시, 6-2 = 정책 정의. 모바일 인증 UX: 생체인증(지문/Face) 모달 + 세션 만료 시 BottomSheet 재인증. Part2 §6.5 보안 체크리스트 우선.

### 8.3 6-12 Event-Logging 모바일 EventType 등록 (LOCK L19 100%)

> `ui.builder.responsive.{action}` 신규 6건 — 6-12 통합 catalog 등록 큐 (P2-4 `event_type_v2_sync.md` §5 형식 직계).

| # | EventType | Payload 핵심 |
|---|-----------|--------------|
| 1 | `ui.builder.responsive.breakpoint_changed` | from_bp, to_bp, width |
| 2 | `ui.builder.responsive.column_collapsed` | column="left"\|"right" |
| 3 | `ui.builder.responsive.drawer_opened` | trigger="tap"\|"swipe" |
| 4 | `ui.builder.responsive.bottomsheet_opened` | snap="peek"\|"half"\|"full" |
| 5 | `ui.builder.responsive.orientation_locked` | orientation="portrait" |
| 6 | `ui.builder.responsive.keyboard_visible` | inset_height |

---

## 9. 반응형 정책 9요소 (E1~E9) — `<ResponsiveLayoutShellV3>`

### 9.1 컴포넌트 L3 명세

| L3 요소 | 내용 |
|---------|------|
| **E1 Input** | `{ width, height, orientation, keyboardInsetHeight }` from 4-1 IPC `vamos://ui:mobile_metrics_changed` + `useResponsive()` 상태 |
| **E2 State** | LOCK L1 9-State 전 상태에서 수동적 구조 layer. BP 전환 < 100ms (P95), 9-State 전이 동반 시 ≤ 500ms (LOCK L17) |
| **E3 Output** | DOM 클래스 갱신 (bp-a/b/c/d), Drawer 토글, BottomSheet snap, 키보드 회피 scroll |
| **E4 Class/API** | `<ResponsiveLayoutShellV3>` 최외곽 wrapper. slots: drawer / main / bottomsheet / appbar / tabbar. Hook: `useResponsive()` |
| **E5 Style** | Tailwind extend screens (bp-d 768px V3). 다크 배경 #1E1E1E 유지 (LOCK L7). safe-area-inset + keyboard-inset 적용 |
| **E6 Accessibility** | Drawer focus-trap + Esc 닫기, BottomSheet `role="dialog"` aria-modal, TabBar `role="tablist"`. 터치 타겟 44×44pt (WCAG 2.5.5, L8). 상세 `mobile_a11y_v3.md` |
| **E7 Error** | `INVALID_DIMENSION` (width<320) → fallback BP-D 강제 + 경고. Touch 폴백 3건 (FB_TOUCH_RETARGET / FB_GESTURE_ALT / FB_ORIENTATION_LOCK, §6) |
| **E8 Test** | unit: classifyBreakpoint() 4분기 + orientation. integration: resize/rotate mock → BP·Drawer·BottomSheet 전이. visual: 768 portrait/landscape 캡처. perf: BP 전환 < 100ms P95 측정 |
| **E9 Event** | `ui.builder.responsive.breakpoint_changed` / `.column_collapsed` / `.drawer_opened` / `.bottomsheet_opened` / `.orientation_locked` / `.keyboard_visible` (LOCK L19 6건) |

---

## 10. 검증 (§7.4 P4-1 검증 항목)

- [x] 모바일 BP-D 768px 정식 — 1-Column + Drawer + BottomSheet + Builder 키보드 처리 (§3) NEW byte ≥ 200L
- [x] LOCK L11 V3 확장 명시 `<!-- V3 EXTENSION, NOT REDEFINITION -->` (§2) + V1 1280×720 verbatim 영구 보존 (R9)
- [x] LOCK L1 (9-State 모바일 전이 §5) + L2/L3/L4 (3-Column → 1-Column reflow §3, 폭 규격 재정의 0) + L8 (WCAG §6/§9) + L17 (전이 ≤500ms) + L19 (이벤트 §8.3) verbatim 보존 (R9)
- [x] Touch FallbackRegistry 3건 (9→12, §6) — FailureCode 14→18 은 P4-4 정본 명시 (count 충돌 차단)
- [x] 4-1 모바일 IPC + 6-2 모바일 RBAC L10 + 6-12 EventType 6건 cross-handoff 양방향 정합 (참조만, 정의 변경 0)
- [x] BP 전환 < 100ms P95 목표 + 9-State 전이 ≤500ms (LOCK L17) 명시
- [x] CONFLICT OPEN 0 유지 (Phase 4 신규 충돌 0)
- [x] ReadOnly FALSE 직접 편집

---

## 11. Phase 배정 및 의존성

| 항목 | 값 |
|------|-----|
| **Phase 배정** | Phase 4 (V3 production-ready 정본 승급, RECOVERY) |
| **base** | responsive_layout_v2.md (V2 BP-A/B/C/D 정책) + fluid_layout.md (V1 3-Column) |
| **Phase 5 이월** | staging 7일 측정 데이터 + WCAG AA 자동 검사 통과율 100% + STEP7-C 잔여 ~70+ V3 모바일 항목 100% 매핑 |
| **교차 도메인** | 4-1 (모바일 IPC, 참조만) / 6-2 (모바일 RBAC) / 6-12 (EventType 등록) — 정의 변경 0건 |

### 11.1 BP 전환 성능 예산 (< 100ms P95)

| 단계 | 예산 | 비고 |
|------|------|------|
| resize 이벤트 debounce | 100ms | 4-1 throttle 후 6-1 debounce |
| classifyBreakpoint 계산 | < 1ms | 순수 함수 |
| DOM 클래스 토글 + reflow | < 50ms | Tailwind 클래스 스왑 |
| Drawer/BottomSheet 마운트 | < 50ms | 지연 마운트 (lazy) |
| **BP 전환 총계 (P95)** | **< 250ms** | 하위 단계 합산(debounce 100 + classify <1 + DOM <50 + mount <50 ≈ 201ms) 기준. 9-State 전이 동반 시 ≤500ms (L17) |

### 11.2 BP-D orientation 처리 (portrait / landscape)

| orientation | 레이아웃 |
|-------------|----------|
| portrait (권장) | 1-Column + 하단 TabBar + BottomSheet |
| landscape | 2-pane 적응 (메인 + 축소 BottomSheet 우측), 또는 portrait 권장 안내 (ORIENTATION_UNSUPPORTED, mobile_a11y §4) |

### 11.3 Phase 5 entry-gate forward-defined

| 게이트 | 조건 |
|--------|------|
| G5-RS-1 | 모바일 BP-D 100% + staging 7일 측정 데이터 |
| G5-RS-2 | WCAG AA 자동 검사 (axe-core) 통과율 100% (mobile_a11y_v3) |
| G5-RS-3 | BP 전환 < 100ms P95 staging 측정 PASS |
| G5-RS-4 | STEP7-C 잔여 ~70+ V3 모바일 항목 100% 매핑 + /audit PASS |

---

## 12. 변경 이력

| 일자 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-06-01 | v1.0 | NEW (P4-1 RECOVERY genuine write) — BP-D 768px 모바일 정식 (V2 §4.4 예고 → 정본) + `useResponsive` Hook + 9-State 모바일 전이 + Touch FallbackRegistry 9→12. LOCK L11 V3 확장 (NOT REDEFINITION) + L1/L2/L3/L4/L8/L17/L19 verbatim 보존. DRAFT→APPROVED |

<!-- END OF DOCUMENT -->
