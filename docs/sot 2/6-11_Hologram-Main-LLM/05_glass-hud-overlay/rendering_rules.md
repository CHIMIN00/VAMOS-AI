# rendering_rules.md — Glass HUD 렌더링 규칙 (Option A Fixed HUD)

| 항목 | 값 |
|------|----|
| **도메인** | 6-11_Hologram-Main-LLM / 05_glass-hud-overlay |
| **세션 (TASK_ID)** | Phase 2 T2-4 (6-11_T2-4_01) |
| **산출물 경로 (sandbox)** | `D:\VAMOS\docs\test_iso_p2\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\rendering_rules.md` |
| **정본 산출물 경로 (production)** | `D:\VAMOS\docs\sot 2\6-11_Hologram-Main-LLM\05_glass-hud-overlay\rendering_rules.md` |
| **LOCK** | **LOCK-HM-10** (Glass HUD Approval 중앙 과점유 금지 + Alert 3종), **D2.0-08 §9.1 Option A Fixed HUD LOCK** (위치 고정), **LOCK-HM-01** (Right Panel ≈300px) |
| **정본 소유** | 6-11 DEFINED-HERE — HUD 위치·투명도·애니메이션 스펙·`pointer-events` 규칙·리렌더 방지 규칙. CSS 변수/테마 팔레트는 6-1 UI-UX-System 정본 소비. |
| **해소 이슈** | **ISS-09** (렌더링 규칙 축) |
| **Phase 배정** | Phase 2 T2-4 |
| **Part2 버전 태그** | V2-Phase 2 (Enhanced Hologram) |
| **작성일** | 2026-04-18 |
| **Version** | v1.0 (초안) |
| **TEST_MODE** | false — Phase 4 production promotion 2026-06-03 (sandbox → production 전환 완료) |

---

## §0. 목적 & Scope

### §0.1 목적

Glass HUD 오버레이의 **렌더링 규칙** 을 확정한다. D2.0-08 §9.1 (L1409-1417) Design Freeze 결정인 **Option A Fixed HUD** 를 근거로 위치 고정·폭/투명도·애니메이션·`pointer-events: none` 하위 콘텐츠 비차단(R-611-2)·불필요 리렌더 방지(`React.memo` + selector + `requestAnimationFrame` 단일 flush) 규칙을 세부 정의한다. **ISS-09 의 렌더링 규칙 축** 을 본 문서에서 해소한다.

### §0.2 Scope

| 구분 | 범위 |
|------|------|
| **In** (본 문서에서 확정) | (a) Fixed HUD 위치 좌표·폭·z-index·투명도, (b) `pointer-events: none` 하위 콘텐츠 비차단 규칙(R-611-2) + 대화형 자식 요소 예외(Approval 카드 내부 버튼), (c) 등장/퇴장 애니메이션 스펙(Evidence fade / Approval slide-in / Alert toast stack / Cost 점진), (d) `React.memo` + selector 기반 리렌더 방지 규칙, (e) `realtime_update.md` 의 RAF 플러시와 정합하는 프레임 단일 렌더 규칙, (f) 접근성(a11y) 규칙(aria-live, focus 관리), (g) Phase 3 테스트 시나리오 12건(TS-RR-01~12). |
| **Out** (타 세션/문서 위임) | (a) `GlassHUDData` 스키마 정의 → **`overlay_schema.md` (peer)**, (b) SSE 갱신 프로토콜 → **`realtime_update.md` (peer)**, (c) HV-EVID-* / Glass HUD CostGauge / ApprovalCard 컴포넌트 **내부 구현** → **6-1 UI-UX-System + 02_component-architecture Phase 1**, (d) 컬러 팔레트 / 다크모드 토큰 → 6-1 UI-UX-System 정본(`hudColorTokens`). |
| **관련 이슈** | ISS-09 (렌더링 규칙 축 해소) |

### §0.3 도메인 경계 선언 (R-611-2)

- **6-11 소유** (본 문서): HUD 레이아웃·애니메이션·상호작용 **정책 규칙**.
- **6-1 UI-UX-System 소유**: 개별 컴포넌트의 DOM 구조·스타일 토큰·테마 변수. 본 문서는 CSS 변수 이름만 소비(`var(--hud-bg-translucent)` 등).
- **R-611-2 원문 verbatim**: 투명 레이어 원칙 — 하위 콘텐츠 상호작용 비차단. 본 문서 §5 가 강제.

---

## §1. 교차 참조 블록

### §1.1 상위 정본 (LOCK 근거)

| 참조 문서 | 섹션 / 라인 | 역할 |
|-----------|-------------|------|
| `../../../sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | §9.1 (L1409-1417) | **Design Freeze Option A Fixed HUD LOCK** — 위치 고정, Right Panel 내부. Option B 기각. |
| `../../../sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | §2.2 (L223-282) | **LOCK-HM-01** — Right Panel ≈300px 폭. 본 문서 §2.1 폭 확정 근거 |
| `../../../sot/D2.0-08_08. VAMOS_DESIGN_2.0_UI_UX.md` | §2.2.2 (L255-265) | **LOCK-HM-10** — Approval 슬라이드 인 + 중앙 과점유 금지 (본 문서 §4.2 강제) |

### §1.2 AUTHORITY_CHAIN / CONFLICT_LOG

| 참조 | 역할 |
|------|------|
| `../AUTHORITY_CHAIN.md` §LOCK L1 (HM-01) / L7 (HM-10) + 정본 원문 L131-L140 + D2.0-08 §9.1 인용 | LOCK 근거 Read 완료. Option A Fixed 모드 확정. |
| `../domain_boundary.md` | R-611-2 원문 verbatim |
| `../CONFLICT_LOG.md` | 본 세션 신규 CONFLICT 0 예상 |

### §1.3 로컬 Phase 1 산출물

| 참조 | 사용 목적 |
|------|----------|
| `01_hologram-view-layout/layout_structure.md` | 3-Pane Right Panel 위치 좌표 정본 (본 문서 §2 재사용) |
| `01_hologram-view-layout/responsive_rules.md` | 반응형 분기점(breakpoint) — 화면 너비 <1280px 시 HUD 폭 재계산 규칙 |
| `02_component-architecture/component_catalog.md` | HV-EVID-* / Glass HUD CostGauge / ApprovalCard DOM 구조 |
| `02_component-architecture/hook_catalog.md` | `useHUD` 훅 selector 패턴 |
| `03_ui-state-machine/state_definitions.md` | `UI_S5_AWAIT_APPROVAL` → Approval slide-in 트리거 |
| `05_glass-hud-overlay/overlay_schema.md` (peer) | `GlassHUDData` import |
| `05_glass-hud-overlay/realtime_update.md` (peer) | RAF 플러시(`scheduleHudFlush`) 연계 |

### §1.4 Peer V2 세션 이음매 (V2↔V2 cross-reference)

| 피어 세션 | 이음매 | 검증 포인트 |
|-----------|--------|------------|
| **overlay_schema.md** (본 세션 peer) | `meta.mode = "FIXED"` 상수 → 본 문서 §2 Option A 강제. `approval.slide_in_active` → 본 문서 §4.2 애니메이션 트리거. | overlay_schema §3.5 `HudMode` Literal 재사용 |
| **realtime_update.md** (본 세션 peer) | `scheduleHudFlush()` RAF 큐 = 본 문서 §6 `React.memo` + selector 결합으로 리렌더 최소화. 애니메이션 중 cost 갱신 프레임 누락 금지(§4.1 frame budget). | realtime_update §4.6 |
| **T2-2 response_formatting.md** (911줄) | T2-2 §5.4 `APPROVAL_REQUESTED` 이벤트 → overlay_schema `approval.slide_in_active=true` → 본 문서 §4.2 slide-in 애니메이션 트리거. T2-2 §5.4 `MEMORY_SAVED` / `ARTIFACT_SAVED` 하이라이트는 Timeline 소관이며 HUD 와 독립. | T2-2 §5.4 이벤트 매핑 |
| **T2-3 dcl_context.md** (865줄) | `active_workflow.qod_hint` 변경 시 본 문서 §4.1 Evidence fade transition. (UI_S4_RUNNING → qod_hint 갱신) | T2-3 §3.2 qod_hint |
| **T2-1 two_tier_routing.md** (857줄) | `trace_id` 공통 — 본 문서 §7 a11y aria-attributes 에 `data-trace-id` 포함. | TraceId 일관 |
| **T2-5 06_streaming-canvas/** (대기) | 본 문서 §3 `z-index` 와 T2-5 스트리밍 캔버스 z-index 의 stacking context 분리(HUD는 더 높은 stacking). T2-5 확정 시 재검토. | T2-5 `rendering_rules` 있으면 교차 검토 |

### §1.5 Cross-domain 소비

| 도메인 | 소비 대상 | 사용처 |
|--------|-----------|--------|
| **6-1 UI-UX-System** | CSS 변수(`--hud-bg-translucent`, `--hud-verified`, `--hud-partial`, `--hud-unverified`, `--hud-elev`) | §2.4 CSS snippet |
| **6-2 Security-Governance** | focus trap 정책(HUD 가 focus 탈취 금지) | §7 a11y |
| **6-12 Event-Logging** | 렌더 지표 로그(frame_flush, animation_drop) | §8 |

> **R-T6-2 준수**: 본 문서는 소비만 수행. LOCK 재정의 없음.

---

## §2. Option A Fixed HUD 위치·레이아웃

### §2.1 위치·폭·z-index 규칙

| 항목 | 값 | 근거 |
|------|----|------|
| **HUD 컨테이너 위치** | `position: fixed` + `top: var(--header-h)` + `right: 0` | D2.0-08 §9.1 Option A LOCK |
| **폭** | `width: clamp(280px, 22vw, 360px)` — 기본 ≈300px | LOCK-HM-01 Right Panel ≈300px |
| **높이** | `height: calc(100vh - var(--header-h) - var(--footer-h))` | 3-Pane Layout 정합 |
| **z-index 계층** | HUD 컨테이너: `150` / Alert Toast: `200` / Modal: `300` (HUD 보다 위) | Stacking context 분리 |
| **배경 투명도** | `background: var(--hud-bg-translucent, rgba(255,255,255,0.85))` + `backdrop-filter: blur(8px)` | 투명 레이어 원칙 |
| **모드 상수** | `meta.mode = "FIXED"` (overlay_schema §3.5) | Option B(Floating) 값 없음 |

### §2.2 Right Panel 안 vs 오버레이

- **정본 해석**: D2.0-08 §9.1 "Fixed HUD" 는 **Right Panel 내부 고정** 을 기본으로 함. 즉 HUD 는 3-Pane 의 Right Panel 컨테이너 안에 렌더되며 Right Panel 자체의 `position: relative` 안에서 고정.
- **실용 구현**: Right Panel 이 `position: relative` 이면 HUD 는 `position: sticky; top: 0;` 로 구현해도 동등. 본 문서는 `position: fixed` 를 **viewport 기준이 아닌 Right Panel 기준** 로 해석 (Right Panel 이 `contain: layout` 일 때 fixed 가 로컬 containing block 이 됨).
- **반응형**: 화면 너비 `<1280px` 에서 HUD 는 접힘 버튼 토글(`rendering_rules` 는 너비 조정 규칙만 정의, 접힘 애니메이션은 §4.3).

### §2.3 Approval 중앙 과점유 금지 규칙

| 규칙 | 값 |
|------|----|
| ApprovalCard 최대 폭 | `max-width: calc(100% - 16px)` (Right Panel 내부 패딩 고려) |
| ApprovalCard 스크린 점유 상한 | 뷰포트 너비의 **25%** 초과 금지 (중앙 과점유 차단) |
| 중앙 Stream Canvas 겹침 금지 | HUD 컨테이너 `right: 0` 유지 — Stream Canvas 영역 침범 금지 |
| Dialog/Modal 금지 | Approval 은 모달(`role="dialog"`) 이 **아님** — 슬라이드 인 카드. focus 탈취 금지. |

### §2.4 CSS 스니펫 (토큰 소비 예시)

```css
/* frontend/src/hologram/glassHud.css — 6-1 UI-UX-System CSS 변수 소비 */
.hud-container {
  position: fixed;
  top: var(--header-h, 48px);
  right: 0;
  width: clamp(280px, 22vw, 360px);
  height: calc(100vh - var(--header-h, 48px) - var(--footer-h, 0px));
  z-index: 150;
  background: var(--hud-bg-translucent, rgba(255, 255, 255, 0.85));
  backdrop-filter: blur(8px);
  overflow-y: auto;
  pointer-events: none;   /* §5 규칙 — 하위 콘텐츠 비차단 */
}

.hud-container > .hud-interactive {
  pointer-events: auto;   /* 버튼/입력만 이벤트 허용 */
}

.hud-verification.verified  { color: var(--hud-verified, #21a957); }    /* Green */
.hud-verification.partial   { color: var(--hud-partial, #f3b700); }     /* Yellow */
.hud-verification.unverified{ color: var(--hud-unverified, #8b8b8b); }  /* Gray */

.hud-alert-toast-stack {
  position: absolute;
  right: 8px;
  top: 8px;
  z-index: 200;
}
```

---

## §3. 투명도·z-index·stacking context

### §3.1 투명도 규칙

| 상태 | 불투명도 | 비고 |
|------|--------|------|
| 기본 | 0.85 (backdrop-filter blur 8px) | 하위 콘텐츠 가독성 확보 |
| hover (HUD 내부) | 0.95 | 카드 초점 |
| `UI_S5_AWAIT_APPROVAL` 활성 카드 | 0.98 | 승인 강조 (중앙 과점유 금지는 여전) |
| 비활성/대기 | 0.70 | `UI_S1_IDLE` / `UI_S8_ARCHIVED` |

### §3.2 z-index 계층

```
          Modal  (300)
           ↑
  Alert Toast  (200)
           ↑
HUD Container  (150)
           ↑
Right Panel Content  (100)
           ↑
Stream Canvas  (50)
           ↑
Timeline  (40)
```

- **원칙**: 위에서 아래로 이벤트/시각 우선순위. Modal 이 유일하게 HUD 위.
- **금지**: Alert Toast 가 Modal 을 가리는 구현 금지. Modal 활성 시 Toast 는 Modal 아래로 내려감(`z-index: 280`).

### §3.3 Stacking context 분리

- HUD 컨테이너는 `contain: layout style` + `isolation: isolate` → 자식 요소의 z-index 가 전역 stacking 을 오염시키지 않음.
- Alert Toast Stack 은 HUD 컨테이너의 자식이되 `position: absolute` 로 내부 고정.

---

## §4. 애니메이션 스펙

### §4.1 Evidence fade transition

| 트리거 | 애니메이션 | 지속 |
|-------|----------|------|
| `hud.evidence.update` (qod_hint → 최종 qod) | `opacity 0.6 → 1.0` + `transform: translateY(-2px) → 0` | 240ms, ease-out |
| VERIFIED → PARTIAL (downgrade) | 색상 cross-fade 180ms + "재검증 완료" 텍스트 fade 120ms | 300ms 합계 |
| PARTIAL → VERIFIED (upgrade) | 색상 cross-fade 180ms + 체크마크 scale 0.8→1 bounce | 300ms |

### §4.2 Approval slide-in

| 트리거 | 애니메이션 | 지속 |
|-------|----------|------|
| `approval.slide_in_active: false → true` | `transform: translateX(120%) → 0` + `opacity 0 → 1` | 320ms, cubic-bezier(0.2, 0.8, 0.2, 1.0) |
| dismiss (GRANTED/REJECTED/expire) | `transform: translateX(0) → 120%` + `opacity 1 → 0` | 220ms, ease-in |
| urgency=CRITICAL | 등장 시 추가 `box-shadow` pulse 2회 (800ms 총) — R-611-2 유지 (차단 금지) | overlay 2 pulse |

**중앙 과점유 금지 연계**: 슬라이드 인 종료 위치는 Right Panel 내부. `left` 속성 사용 금지 — `right: 16px` 고정.

### §4.3 Cost gauge 점진

| 트리거 | 애니메이션 | 지속 |
|-------|----------|------|
| `ratio_to_budget` 증가 | 진행 바 `width` transition | 800ms, linear (값 비약 방지) |
| 임계치 0.8 최초 돌파 | 색상 Green → Yellow cross-fade + `hud-threshold-crossed` 발신 | 300ms |
| 0.95 초과 | Yellow → Red + pulse | 400ms |

### §4.4 Uncertainty Alert Toast stack

| 트리거 | 애니메이션 | 지속 |
|-------|----------|------|
| `hud.alert.raise` 수신 | 오른쪽 상단에서 slide-in + fade-in | 200ms |
| dismiss (자동/수동) | slide-out (오른쪽) + fade-out | 160ms |
| 같은 kind 재발생 | 기존 토스트 wobble (8px 진폭 2회) | 300ms (신규 추가 금지) |

### §4.5 Reduced motion (prefers-reduced-motion)

```css
@media (prefers-reduced-motion: reduce) {
  .hud-container *, .hud-alert-toast-stack * {
    animation-duration: 1ms !important;
    transition-duration: 1ms !important;
  }
}
```

- 접근성 옵션 활성 시 모든 HUD 애니메이션 사실상 무효. 상태 변화는 즉시 반영.

### §4.6 Frame budget

- 단일 프레임(16ms) 내 HUD 전체 렌더 완료 목표.
- 프레임 초과 감지 시 `hologram.hud.frame_budget_exceeded` WARN 로그(10초당 최대 1건 샘플링).

---

## §5. `pointer-events: none` 하위 콘텐츠 비차단 규칙 (R-611-2)

### §5.1 원칙

R-611-2 원문 verbatim:
```
Glass HUD 오버레이는 투명 레이어로 구현 — 하위 콘텐츠 상호작용 차단 금지
```

- **컨테이너 기본**: `.hud-container { pointer-events: none; }`
- **자식 대화형 요소만 허용**: 버튼/링크/입력/ApprovalCard 액션에 `.hud-interactive { pointer-events: auto; }` 적용.
- **영향 범위**: HUD 가 Right Panel 내부이므로 하위 콘텐츠 차단 이슈는 주로 **Approval 슬라이드 인 구간** 에서 발생. 카드 자체는 `pointer-events: auto` 로 설정하되 **카드 바깥 영역은 빈 공간** 이므로 하위 콘텐츠에 영향 없음.

### §5.2 예외 케이스

| 케이스 | 정책 |
|-------|------|
| ApprovalCard 내부 버튼 | `pointer-events: auto` — 승인 요청 상호작용 허용 |
| Evidence 뱃지 툴팁 | hover 시만 `pointer-events: auto` |
| Cost gauge tooltip | hover 시 (동일) |
| Alert toast close 버튼 | `pointer-events: auto` — dismiss 허용 |
| 기타 HUD 텍스트/아이콘 | `pointer-events: none` 유지 |

### §5.3 차단 테스트 가드

- Cypress/Playwright 테스트에서 HUD 아래 DOM 요소를 프로그램적으로 click 하여 클릭 수신을 확인한다(TS-RR-03).

---

## §6. 리렌더 방지 규칙 (React.memo + selector + RAF)

### §6.1 `React.memo` 래핑

```typescript
// frontend/src/hologram/components/GlassHud.tsx
import { memo } from "react";
import type { GlassHUDData } from "../types/glassHudData";
import { useHUD } from "../hooks/useHUD";  // Phase 1 정본 훅

function glassHudEqual(prev: { data: GlassHUDData }, next: { data: GlassHUDData }) {
  const a = prev.data, b = next.data;
  return (
    a.meta.updated_at_ms === b.meta.updated_at_ms
    && a.cost.ratio_to_budget === b.cost.ratio_to_budget
    && a.evidence.qod_score === b.evidence.qod_score
    && a.evidence.verification === b.evidence.verification
    && (a.approval?.action_id ?? null) === (b.approval?.action_id ?? null)
    && (a.approval?.slide_in_active ?? false) === (b.approval?.slide_in_active ?? false)
    && a.uncertainty_alert.items.length === b.uncertainty_alert.items.length
    && a.uncertainty_alert.items.every((it, i) =>
         it.kind === b.uncertainty_alert.items[i].kind
         && it.raised_at_ms === b.uncertainty_alert.items[i].raised_at_ms
         && it.message === b.uncertainty_alert.items[i].message)
    && a.uncertainty_alert.items.every((it, i) =>
         it.kind === b.uncertainty_alert.items[i].kind
         && it.raised_at_ms === b.uncertainty_alert.items[i].raised_at_ms
         && it.message === b.uncertainty_alert.items[i].message)
  );
}

export const GlassHud = memo(function GlassHud({ data }: { data: GlassHUDData }) {
  // 렌더 구현 생략 — 6-1 UI-UX-System 정본 컴포넌트 소비
  return <div className="hud-container" data-trace-id={data.meta.trace_id}>{/* ... */}</div>;
}, glassHudEqual);
```

### §6.2 Selector 패턴 (Zustand)

```typescript
// frontend/src/hologram/hooks/useHudSelectors.ts
import type { GlassHUDData } from "../types/glassHudData";
import { useHUD } from "./useHUD";   // 통합 훅 (전체 GlassHUDData 구독 금지)

export const useHudCost      = () => useHUD((d: GlassHUDData) => d.cost);
export const useHudEvidence  = () => useHUD((d: GlassHUDData) => d.evidence);
export const useHudApproval  = () => useHUD((d: GlassHUDData) => d.approval);
export const useHudAlerts    = () => useHUD((d: GlassHUDData) => d.uncertainty_alert);
```

- 각 HUD 자식 컴포넌트는 자신의 필드만 구독 → 다른 필드 변경 시 리렌더 제외.

### §6.3 RAF 단일 flush 연계

- `realtime_update.md §4.6` 의 `scheduleHudFlush()` 로 16ms 창 내 갱신을 합친다.
- `React` 렌더는 `useSyncExternalStore` 의 `getSnapshot` 이 RAF 이후 stable → 단일 commit.

### §6.4 리렌더 측정 지표

| 지표 | 임계 |
|------|------|
| 초당 HUD 리렌더 수 | ≤30/s (평시 ≤5/s) |
| 평균 리렌더 시간 | ≤4ms |
| frame budget 초과 비율 | ≤1% |

---

## §7. 접근성 (a11y) 규칙

### §7.1 aria-live 영역

| 구성 요소 | role / aria-live |
|----------|------------------|
| VerificationBadge | `role="status"` + `aria-live="polite"` |
| Cost gauge | `role="meter"` + `aria-valuenow/min/max` + `aria-live="polite"` |
| ApprovalCard | `role="region"` + `aria-label="승인 요청"` — **`role="dialog"` 사용 금지** (focus 탈취 방지) |
| Alert toast | `role="status"` + `aria-live="assertive"` (LOW_QOD/CONFLICTING_SOURCES/STALE_DATA 알림) |

### §7.2 Focus 관리

- HUD 가 생성되어도 자동 focus 이동 금지(사용자 흐름 방해 방지).
- ApprovalCard 는 `autoFocus` 금지. 대신 첫 번째 액션 버튼에 `tabIndex=0` 기본 포커스 가능 상태 유지.
- Keyboard 사용자: `Tab` 으로 HUD 내부 접근 가능, `Escape` 로 Approval 카드 close (GRANTED/REJECTED 아닌 "보기 접기" 동작).

### §7.3 i18n

| 라벨 | ko-KR | en-US |
|------|-------|-------|
| Verification VERIFIED | 검증됨 | Verified |
| Verification PARTIAL | 부분 검증 | Partial |
| Verification UNVERIFIED | 미검증 | Unverified |
| Alert LOW_QOD | 근거 품질 낮음 | Low QoD |
| Alert CONFLICTING_SOURCES | 출처 충돌 | Conflicting Sources |
| Alert STALE_DATA | 오래된 정보 | Stale Data |
| Cost over threshold | 예산 임계 접근 | Cost threshold approaching |

- 6-1 UI-UX-System 의 `i18n` 테이블에 동일 키로 등재 필요 — 본 문서는 **권장 라벨** 제시, 최종 번역은 6-1 정본.

### §7.4 reduced-motion (§4.5 재확인)

- `prefers-reduced-motion: reduce` 존중.
- 애니메이션 대체: 즉시 상태 전환, 단 색상 contrast 는 동일 유지.

---

## §8. 로깅 포맷 (R-01-7 구조화 JSON)

### §8.1 이벤트 네임스페이스

| 이벤트 | 트리거 | 레벨 |
|-------|-------|-----|
| `hologram.hud.rendered` | `GlassHud` 최초 마운트 | INFO |
| `hologram.hud.rerender` | `glassHudEqual` false 판정 후 리렌더 | DEBUG (샘플링 1:10) |
| `hologram.hud.frame_budget_exceeded` | 16ms 프레임 초과 | WARN (샘플링 1:10s) |
| `hologram.hud.animation_dropped` | 애니메이션 프레임 누락 >20% | WARN |
| `hologram.hud.pointer_events_leak` | HUD 하위 요소가 이벤트 차단(테스트 검출) | ERROR |
| `hologram.hud.approval_slide_in` | Approval 카드 slide-in 시작 | INFO |
| `hologram.hud.alert_toast_shown` | Alert toast 마운트 | INFO |

### §8.2 로그 스키마 (중첩 JSON)

```json
{
  "ts": "2026-04-18T12:34:56.789Z",
  "level": "WARN",
  "event": "hologram.hud.frame_budget_exceeded",
  "trace_id": "01HV8M3J7K9P2Q4R6S8T",
  "session_id": "sess_01HV...",
  "render": {
    "frame_duration_ms": 22.4,
    "budget_ms": 16,
    "rerender_count_last_10s": 45,
    "component": "GlassHud.ApprovalCard"
  },
  "animation": {
    "in_progress": ["approval.slide_in"],
    "dropped_frames_ratio": 0.12
  },
  "error": {
    "code": "HUD-FRAME-BUDGET-01",
    "message": "frame 22.4ms > 16ms"
  },
  "recovery": {
    "plan": "throttle next rerender, skip non-essential animations",
    "applied": true
  },
  "mode": "FIXED",
  "ui_state": "UI_S5_AWAIT_APPROVAL",
  "part2_phase_tag": "V2"
}
```

### §8.3 R-01-7 준수 체크

| 요구 | 충족 |
|------|------|
| 구조화 JSON 중첩 | ✅ `render{}` / `animation{}` / `error{}` / `recovery{}` |
| `trace_id` 필수 | ✅ |
| 이벤트 네임스페이스 | ✅ `hologram.hud.*` |
| PII 마스킹 | ⚡ 본 문서 범위에 PII 노출 없음 |

---

## §9. Phase 3 테스트 시나리오 (12건, ≥10 요건 초과)

| TS-ID | 시나리오 | 입력 | 기대 렌더 결과 | 검증 포인트 |
|-------|---------|------|-------------|-----------|
| **TS-RR-01** | Fixed HUD 위치 고정 | 창 스크롤 1000px | HUD 위치 viewport 내 `top: var(--header-h)`·`right: 0` 유지 | §2.1 |
| **TS-RR-02** | 폭 반응형 | 창 너비 1400 → 1100 → 800 | clamp(280,22vw,360) → 클램프 값 → 접힘 토글 | §2.1 + responsive_rules.md |
| **TS-RR-03** | pointer-events 하위 비차단 | HUD 위 좌표에서 하위 canvas 클릭 | 클릭이 canvas 에 도달 | §5 R-611-2 |
| **TS-RR-04** | ApprovalCard 액션 버튼 클릭 | 카드 내부 "승인" 버튼 클릭 | 이벤트 수신 (pointer-events auto) | §5.2 |
| **TS-RR-05** | Evidence fade transition | qod 0.6 → 0.91 | 240ms 색상 cross-fade | §4.1 |
| **TS-RR-06** | Approval slide-in | `slide_in_active: false→true` | 320ms translateX, right 고정 | §4.2 + §2.3 |
| **TS-RR-07** | Approval CRITICAL pulse | urgency=CRITICAL | 2회 box-shadow pulse, 차단 금지 유지 | §4.2 + §5 |
| **TS-RR-08** | Cost gauge 임계 돌파 | ratio 0.78 → 0.82 | Green→Yellow cross-fade 300ms | §4.3 |
| **TS-RR-09** | reduced-motion 준수 | `prefers-reduced-motion: reduce` | 모든 애니메이션 1ms | §4.5 |
| **TS-RR-10** | React.memo 차단 | log_report 갱신만(cost/evidence 불변) | GlassHud 리렌더 스킵 | §6.1 + §6.2 |
| **TS-RR-11** | RAF 단일 flush | 16ms 창 evidence+cost 2 갱신 | 1 commit | §6.3 + realtime_update §4.6 |
| **TS-RR-12** | a11y aria-live | VerificationBadge 변경 | 스크린 리더 polite 알림 | §7.1 |

### §9.1 시나리오 cross-check

| TS-ID | LOCK/규칙 | 관련 §본 문서 | 관련 peer V2 |
|-------|----------|--------------|-------------|
| TS-RR-01/02 | Option A Fixed HUD LOCK / LOCK-HM-01 | §2 | — |
| TS-RR-03/04 | R-611-2 | §5 | — |
| TS-RR-05~08 | LOCK-HM-10 애니메이션 | §4 | overlay_schema §3, realtime_update §5 |
| TS-RR-09 | a11y | §4.5, §7.4 | — |
| TS-RR-10/11 | 리렌더 방지 | §6 | realtime_update §4.6 |
| TS-RR-12 | a11y | §7.1 | — |

---

## §10. 산출물 요약

- **파일**: `05_glass-hud-overlay/rendering_rules.md` (production-promoted 2026-06-03 Phase 4)
- **구조**: §0~§9 총 10개 섹션
- **핵심 정의**: Option A Fixed HUD 위치·폭·z-index·투명도 + 애니메이션 스펙 4종(Evidence/Approval/Cost/Alert) + `pointer-events: none` + React.memo/selector + a11y
- **LOCK 준수**: D2.0-08 §9.1 Option A LOCK, LOCK-HM-01 Right Panel 폭, LOCK-HM-10 Approval 중앙 과점유 금지, R-611-2 투명 레이어 원칙
- **Peer V2 cross-ref**: overlay_schema(`meta.mode=FIXED` 상수 소비 + `GlassHUDData` import) / realtime_update(RAF flush 정합) / T2-2(APPROVAL_REQUESTED 트리거) / T2-3(qod_hint fade) / T2-1(trace_id)
- **테스트 시나리오**: 12건 (TS-RR-01~12, ≥10 요건 초과)
- **ISS-09 렌더링 규칙 축 해소**: 완료 — ISS-09 전체 3 축(스키마·갱신·렌더) 모두 3 V2 파일로 해소

### §10.1 검증 체크리스트 (종합계획서 §7 T2-4 대조)

- [x] Option A Fixed HUD 위치·폭·z-index 규칙 (§2.1) ✅
- [x] `pointer-events: none` 하위 콘텐츠 비차단 (§5) — R-611-2 verbatim ✅
- [x] 등장/퇴장 애니메이션 스펙 Evidence/Approval/Cost/Alert 4종 (§4) ✅
- [x] `React.memo` + selector 기반 불필요 리렌더 방지 (§6) ✅
- [x] Approval 슬라이드 인 + 중앙 과점유 금지(Right Panel 바깥 배치 금지) (§2.3 + §4.2) ✅
- [x] reduced-motion 접근성 (§4.5 + §7.4) ✅
- [x] a11y aria-live + focus 관리 (§7) ✅
- [x] V2-Phase 2 태그 헤더 ✅
- [x] overlay_schema.md 타입 재사용(재정의 없음) ✅
- [x] Phase 3 시나리오 12건 ≥10 ✅

---

**[END of rendering_rules.md — Glass HUD 렌더링 규칙, 6-11 / 05_glass-hud-overlay, Phase 2 T2-4, v1.0, 2026-04-18]**
