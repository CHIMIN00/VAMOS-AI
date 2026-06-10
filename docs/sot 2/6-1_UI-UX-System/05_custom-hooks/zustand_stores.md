# Zustand Stores 7개 -- L3 상세 명세

> **도메인**: 6-1_UI-UX-System / 05_custom-hooks
> **버전**: v1.0
> **작성일**: 2026-04-12 (P1-11)
> **정본 출처**: Part2 §6.1.3 (주 정본), D2.0-08 §4·§5·§7·§10.4 (설계 참조)
> **LOCK 참조**: L15 (Zustand Stores 수 7개), L1 (9-State), L7 (다크모드 기본 Dark), L10 (RBAC 4단계), L16 (i18n 기본 ko-KR), L17 (전이 지연 500ms), L19 (이벤트 네이밍), L20 (FailureCode 14 + FallbackRegistry 9)
> **Phase**: Phase 1 (V1-P4 Week 13-14)
> **산출물 ID**: P1-11

---

## 0. 문서 개요

본 문서는 Part2 §6.1.3 정본 기반 Zustand Stores 7개(LOCK L15)의 L3 상세 명세를 정의한다.

> LOCK (Part2 §6.1.3, L15): Stores (7개): appStore, decisionStore, costStore, notificationStore, authStore, memoryStore, workflowStore

**L3 기준 (종합계획서 §13)**:
- E1: TypeScript 인터페이스 (State + Actions)
- E2: 초기 상태 값 (모든 필드의 기본값)
- E3: 미들웨어 구성 (persist / devtools / immer)
- E6: Selector 패턴 (부분 구독 권장 목록)
- E7: Store 간 관계 정의 (참조/구독/갱신 순서)

**파일 경로**: `frontend/src/stores/` (V1-P4 구현 #13)
**네이밍 교정** (PHASE_B2 §3.1 정본): agent -> notification, config -> auth

---

## 1. appStore

### 1.1 TypeScript 인터페이스

```typescript
// frontend/src/stores/appStore.ts

/** 앱 전역 상태 -- 테마, 언어, 자율성 레벨, 세션 정보 */
interface AppState {
  /** 테마 모드 */
  theme: 'dark' | 'light';
  /** i18n 로케일 */
  locale: string;
  /** 자율성 레벨 L0~L4 */
  autonomyLevel: 0 | 1 | 2 | 3 | 4;
  /** 현재 세션 ID */
  sessionId: string | null;
  /** 네트워크 연결 상태 */
  isOnline: boolean;
  /** 현재 UI 상태 (9-State 중 BOOT/IDLE/ARCHIVED) */
  uiState: 'UI_S0_BOOT' | 'UI_S1_IDLE' | 'UI_S8_ARCHIVED';
  /** 사이드바 접힘 여부 */
  isSidebarCollapsed: boolean;
}

interface AppActions {
  /** 테마 변경 (dark/light 토글) */
  setTheme: (theme: 'dark' | 'light') => void;
  /** 로케일 변경 */
  setLocale: (locale: string) => void;
  /** 자율성 레벨 변경 (0~4) */
  setAutonomyLevel: (level: 0 | 1 | 2 | 3 | 4) => void;
  /** 세션 ID 설정 */
  setSessionId: (sessionId: string | null) => void;
  /** 네트워크 상태 갱신 */
  setOnlineStatus: (isOnline: boolean) => void;
  /** UI 상태 전이 (appStore 관할: BOOT/IDLE/ARCHIVED) */
  setUiState: (state: 'UI_S0_BOOT' | 'UI_S1_IDLE' | 'UI_S8_ARCHIVED') => void;
  /** 사이드바 토글 */
  toggleSidebar: () => void;
  /** 전체 상태 초기화 (로그아웃/앱 재시작) */
  reset: () => void;
}

type AppStore = AppState & AppActions;
```

### 1.2 초기 상태 값

```typescript
const initialAppState: AppState = {
  theme: 'dark',           // LOCK (D2.0-08 §10.1, L7): 기본값 = Dark (#1E1E1E)
  locale: 'ko-KR',        // LOCK (D2.0-08 §0, L16): ko-KR (보조: en-US, V2 확장: ja-JP)
  autonomyLevel: 0,        // L0 = 완전 수동 (안전한 기본값)
  sessionId: null,         // 세션 미시작
  isOnline: true,          // 낙관적 초기화, mount 시 실제 상태 확인
  uiState: 'UI_S0_BOOT',  // LOCK (D2.0-08 §4.1, L1): 앱 시작 = BOOT
  isSidebarCollapsed: false,
};
```

### 1.3 미들웨어 구성

```typescript
import { create } from 'zustand';
import { persist, devtools } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';

const useAppStore = create<AppStore>()(
  devtools(
    persist(
      immer((set) => ({
        ...initialAppState,
        setTheme: (theme) => set((state) => { state.theme = theme; }),
        setLocale: (locale) => set((state) => { state.locale = locale; }),
        setAutonomyLevel: (level) => set((state) => { state.autonomyLevel = level; }),
        setSessionId: (sessionId) => set((state) => { state.sessionId = sessionId; }),
        setOnlineStatus: (isOnline) => set((state) => { state.isOnline = isOnline; }),
        setUiState: (uiState) => set((state) => { state.uiState = uiState; }),
        toggleSidebar: () => set((state) => { state.isSidebarCollapsed = !state.isSidebarCollapsed; }),
        reset: () => set(() => initialAppState),
      })),
      {
        name: 'vamos-app-store',
        // persist 대상 필드 (영속성: Tauri localStorage)
        partialize: (state) => ({
          theme: state.theme,
          locale: state.locale,
          autonomyLevel: state.autonomyLevel,
          isSidebarCollapsed: state.isSidebarCollapsed,
        }),
        // Tauri 환경: @tauri-apps/plugin-store 또는 localStorage 폴백
        storage: createTauriStorage(),
      }
    ),
    { name: 'appStore', enabled: process.env.NODE_ENV === 'development' }
  )
);
```

| 미들웨어 | 적용 | 이유 |
|---------|------|------|
| **persist** | O | theme, locale, autonomyLevel, sidebarCollapsed -- 앱 재시작 후 유지 필요 |
| **devtools** | O (dev only) | Redux DevTools 연동 -- 개발 시 상태 추적 |
| **immer** | O | 중첩 객체 없으나 일관성 위해 전역 적용 |

### 1.4 Selector 패턴

```typescript
// 권장 selector -- 부분 구독으로 불필요 리렌더 방지
const selectTheme = (state: AppStore) => state.theme;
const selectLocale = (state: AppStore) => state.locale;
const selectAutonomyLevel = (state: AppStore) => state.autonomyLevel;
const selectIsOnline = (state: AppStore) => state.isOnline;
const selectUiState = (state: AppStore) => state.uiState;
const selectSessionId = (state: AppStore) => state.sessionId;

// 사용 예시
const theme = useAppStore(selectTheme);           // 테마만 구독
const isOnline = useAppStore(selectIsOnline);      // 온라인 상태만 구독
```

**메모이제이션 전략**: `selectTheme`, `selectLocale` -- 변경 빈도 낮아 shallow compare 충분.

### 1.5 영속성 전략

| 필드 | 영속성 | 저장소 | 근거 |
|------|--------|--------|------|
| theme | **persist** | Tauri localStorage | 사용자 테마 설정 유지 (L7) |
| locale | **persist** | Tauri localStorage | 언어 설정 유지 (L16) |
| autonomyLevel | **persist** | Tauri localStorage | 자율성 레벨 유지 |
| isSidebarCollapsed | **persist** | Tauri localStorage | UI 레이아웃 유지 |
| sessionId | **memory** | -- | 세션별 초기화 |
| isOnline | **memory** | -- | 실시간 감지 |
| uiState | **memory** | -- | 상태 머신 런타임 |

### 1.6 관할 UI 상태 범위 (9-State 매핑)

> 출처: _index.md §5.2

| 9-State | appStore 관할 | 비고 |
|---------|-------------|------|
| UI_S0_BOOT | O | Core 미연결, 부팅 전 단계 |
| UI_S1_IDLE | O | 입력 대기 |
| UI_S8_ARCHIVED | O | 세션 종료 후 리뷰용 |

---

## 2. decisionStore

### 2.1 TypeScript 인터페이스

```typescript
// frontend/src/stores/decisionStore.ts

interface Decision {
  id: string;
  traceId: string;
  conclusion: string;
  confidence: number;
  lockedAt: number;
}

interface Evidence {
  id: string;
  sourceId: string;
  qodScore: number;
  qodLevel: 'high' | 'medium' | 'low';
  content: string;
}

/** Decision Lock 상태 + 이력 관리 */
interface DecisionState {
  /** 현재 Decision 객체 */
  currentDecision: Decision | null;
  /** Decision Lock 여부 */
  isLocked: boolean;
  /** Lock 타임스탬프 */
  lockTimestamp: number | null;
  /** Decision 이력 */
  history: Decision[];
  /** P2 도메인 잠금 대상 */
  p2Domain: string | null;
  /** P2 합의 완료 여부 */
  p2Agreed: boolean;
  /** 현재 근거 목록 */
  evidence: Evidence[];
}

interface DecisionActions {
  /** Decision Lock 설정 */
  lockDecision: (decision: Decision, evidence: Evidence[]) => void;
  /** Decision 해제 (세션 초기화) */
  clearDecision: () => void;
  /** P2 도메인 설정 */
  setP2Domain: (domain: string) => void;
  /** P2 합의 확인 */
  confirmP2: () => void;
  /** P2 합의 취소 */
  cancelP2: () => void;
  /** 근거 추가 */
  addEvidence: (evidence: Evidence) => void;
  /** 이력에 Decision 추가 */
  archiveDecision: () => void;
}

type DecisionStore = DecisionState & DecisionActions;
```

### 2.2 초기 상태 값

```typescript
const initialDecisionState: DecisionState = {
  currentDecision: null,
  isLocked: false,
  lockTimestamp: null,
  history: [],
  p2Domain: null,
  p2Agreed: false,
  evidence: [],
};
```

### 2.3 미들웨어 구성

```typescript
const useDecisionStore = create<DecisionStore>()(
  devtools(
    immer((set, get) => ({
      ...initialDecisionState,
      lockDecision: (decision, evidence) => set((state) => {
        state.currentDecision = decision;
        state.isLocked = true;
        state.lockTimestamp = Date.now();
        state.evidence = evidence;
      }),
      clearDecision: () => set(() => initialDecisionState),
      setP2Domain: (domain) => set((state) => { state.p2Domain = domain; }),
      confirmP2: () => set((state) => { state.p2Agreed = true; }),
      cancelP2: () => set((state) => {
        state.p2Domain = null;
        state.p2Agreed = false;
      }),
      addEvidence: (evidence) => set((state) => {
        state.evidence.push(evidence);
      }),
      archiveDecision: () => set((state) => {
        if (state.currentDecision) {
          state.history.push(state.currentDecision);
          state.currentDecision = null;
          state.isLocked = false;
          state.lockTimestamp = null;
          state.evidence = [];
        }
      }),
    })),
    { name: 'decisionStore', enabled: process.env.NODE_ENV === 'development' }
  )
);
```

| 미들웨어 | 적용 | 이유 |
|---------|------|------|
| **persist** | X | 세션 종료 시 초기화 (영속성: session) |
| **devtools** | O (dev only) | Decision Lock 상태 추적 |
| **immer** | O | Decision/Evidence 중첩 객체 불변 갱신 |

### 2.4 Selector 패턴

```typescript
const selectCurrentDecision = (state: DecisionStore) => state.currentDecision;
const selectIsLocked = (state: DecisionStore) => state.isLocked;
const selectP2Status = (state: DecisionStore) => ({
  domain: state.p2Domain,
  agreed: state.p2Agreed,
});
const selectEvidence = (state: DecisionStore) => state.evidence;
const selectDecisionHistory = (state: DecisionStore) => state.history;

// 커스텀 comparator -- Decision 객체 깊은 비교
const selectCurrentDecisionDeep = (state: DecisionStore) => state.currentDecision;
// 사용: useDecisionStore(selectCurrentDecisionDeep, (a, b) => JSON.stringify(a) === JSON.stringify(b))
```

**메모이제이션 전략**: `selectCurrentDecision` -- Decision 객체 깊은 비교 필요, `JSON.stringify` 기반 커스텀 comparator 사용.

### 2.5 영속성 전략

| 필드 | 영속성 | 저장소 | 근거 |
|------|--------|--------|------|
| currentDecision | **session** | sessionStorage | 세션 내 유지, 탭 닫기 시 초기화 |
| isLocked | **session** | sessionStorage | Decision Lock 상태 세션 내 유지 |
| history | **session** | sessionStorage | 세션 이력 유지 |
| p2Domain / p2Agreed | **memory** | -- | P2 모달 흐름 임시 상태 |
| evidence | **session** | sessionStorage | 세션 내 근거 유지 |

> **참고**: persist 미들웨어 미적용이나, 승인 대기 중 새로고침 복원 시 세션 복원 로직에서 `lockDecision()`을 재호출하여 UI_S5_AWAIT_APPROVAL 상태를 복원한다 (_index.md §5.1 참조).

### 2.6 관할 UI 상태 범위

| 9-State | decisionStore 관할 | 비고 |
|---------|-------------------|------|
| UI_S4_RUNNING | 부분 (S3_DECISION_LOCKED 시 isLocked = true) | workflowStore와 공동 관할 |
| UI_S5_AWAIT_APPROVAL | O (authStore와 공동) | 승인 대기 (1:1 대응) |

### 2.7 R-61-5 제약

> LOCK (D2.0-08 §4.3): Decision Lock 이후 "결론 변경" UI 제공 금지 -- 재시도는 근거/실행/포맷 축만.

`lockDecision()` 호출 이후 `currentDecision.conclusion` 변경 액션이 존재하지 않음 (설계 의도). 결론 변경이 필요한 경우 `clearDecision()` -> 새 Decision 생성 흐름만 허용.

---

## 3. costStore

### 3.1 TypeScript 인터페이스

```typescript
// frontend/src/stores/costStore.ts

type CostMode = 'V0' | 'V1' | 'V2' | 'V3';

interface Budget {
  daily: number;
  monthly: number;
  remaining: number;
}

/** 비용 모드 + 예산 잔여 + 토큰 카운터 */
interface CostState {
  /** 비용 모드 V0(무료)~V3(프리미엄) */
  mode: CostMode;
  /** 예산 잔여액 */
  budgetRemaining: number;
  /** 입력 토큰 수 */
  tokenIn: number;
  /** 출력 토큰 수 */
  tokenOut: number;
  /** 예상 비용 (원화) */
  estCost: number;
  /** 80% 경고 상태 */
  isWarning80: boolean;
  /** 100% 상한 도달 */
  isCeiling100: boolean;
  /** 현재 세션 비용 */
  sessionCost: number;
  /** 일일 누적 비용 */
  dailyCost: number;
  /** 월간 누적 비용 */
  monthlyCost: number;
}

interface CostActions {
  /** 비용 정보 갱신 (이벤트 수신 시) */
  updateCost: (payload: {
    tokenIn: number;
    tokenOut: number;
    estCost: number;
    budgetRemaining: number;
  }) => void;
  /** 다운시프트 (비용 절감 모드 전환) */
  downshift: () => void;
  /** 세션 비용 초기화 */
  resetSession: () => void;
  /** 비용 모드 변경 */
  setMode: (mode: CostMode) => void;
  /** 경고 상태 업데이트 */
  updateWarningStatus: () => void;
}

type CostStore = CostState & CostActions;
```

### 3.2 초기 상태 값

```typescript
const initialCostState: CostState = {
  mode: 'V1',              // 기본 비용 모드
  budgetRemaining: 0,      // 서버에서 초기값 수신
  tokenIn: 0,
  tokenOut: 0,
  estCost: 0,
  isWarning80: false,
  isCeiling100: false,
  sessionCost: 0,
  dailyCost: 0,
  monthlyCost: 0,
};
```

### 3.3 미들웨어 구성

```typescript
const useCostStore = create<CostStore>()(
  devtools(
    immer((set, get) => ({
      ...initialCostState,
      updateCost: (payload) => set((state) => {
        state.tokenIn += payload.tokenIn;
        state.tokenOut += payload.tokenOut;
        state.estCost = payload.estCost;
        state.budgetRemaining = payload.budgetRemaining;
        state.sessionCost += payload.estCost;
        // 경고 상태 자동 갱신
        const usageRatio = state.dailyCost / (state.dailyCost + payload.budgetRemaining || 1);
        state.isWarning80 = usageRatio >= 0.8;
        state.isCeiling100 = usageRatio >= 1.0;
      }),
      downshift: () => set((state) => {
        const modes: CostMode[] = ['V3', 'V2', 'V1', 'V0'];
        const currentIdx = modes.indexOf(state.mode);
        if (currentIdx < modes.length - 1) {
          state.mode = modes[currentIdx + 1];
        }
      }),
      resetSession: () => set((state) => {
        state.tokenIn = 0;
        state.tokenOut = 0;
        state.estCost = 0;
        state.sessionCost = 0;
        state.isWarning80 = false;
        state.isCeiling100 = false;
      }),
      setMode: (mode) => set((state) => { state.mode = mode; }),
      updateWarningStatus: () => set((state) => {
        // 예산 대비 사용률 기반 경고
        const budget = state.dailyCost + state.budgetRemaining;
        if (budget > 0) {
          const ratio = state.dailyCost / budget;
          state.isWarning80 = ratio >= 0.8;
          state.isCeiling100 = ratio >= 1.0;
        }
      }),
    })),
    { name: 'costStore', enabled: process.env.NODE_ENV === 'development' }
  )
);
```

| 미들웨어 | 적용 | 이유 |
|---------|------|------|
| **persist** | X | 세션 종료 시 초기화 (영속성: session) |
| **devtools** | O (dev only) | 비용 추적, 다운시프트 디버깅 |
| **immer** | O | updateCost 빈번한 부분 갱신 |

### 3.4 Selector 패턴

```typescript
const selectCostMode = (state: CostStore) => state.mode;
const selectBudget = (state: CostStore) => state.budgetRemaining;
const selectTokens = (state: CostStore) => ({
  tokenIn: state.tokenIn,
  tokenOut: state.tokenOut,
});
const selectIsWarning = (state: CostStore) => state.isWarning80;
const selectIsCeiling = (state: CostStore) => state.isCeiling100;
const selectCostSummary = (state: CostStore) => ({
  sessionCost: state.sessionCost,
  dailyCost: state.dailyCost,
  monthlyCost: state.monthlyCost,
  budgetRemaining: state.budgetRemaining,
  mode: state.mode,
});
```

**메모이제이션 전략**:
- `selectCostSummary` -- 다수 필드 결합, `useMemo` + 의존성 배열 최소화
- `selectTokens` -- 실시간 게이지(S7C-082)용, 매 chunk마다 갱신되므로 **throttle(100ms)** 적용

### 3.5 영속성 전략

| 필드 | 영속성 | 저장소 | 근거 |
|------|--------|--------|------|
| mode | **session** | sessionStorage | 세션 내 비용 모드 유지 |
| tokenIn / tokenOut | **memory** | -- | 실시간 카운터, 세션 초기화 |
| estCost | **memory** | -- | 실시간 계산값 |
| budgetRemaining | **memory** | -- | 서버 동기화 |
| sessionCost | **memory** | -- | 세션별 초기화 |
| dailyCost / monthlyCost | **memory** | -- | 서버에서 수신 |
| isWarning80 / isCeiling100 | **memory** | -- | 계산 파생값 |

---

## 4. notificationStore

### 4.1 TypeScript 인터페이스

```typescript
// frontend/src/stores/notificationStore.ts

type AlertPriority = 'P0_MODAL' | 'P1_SLIDE' | 'P2_TOAST';
// P0_MODAL: 모달 (CM-ALERT-01) -- 즉시 확인 필요
// P1_SLIDE: 슬라이드 (CM-ALERT-02) -- 주의 필요
// P2_TOAST: 토스트 (CM-ALERT-03) -- 정보성

type NotificationSeverity = 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL' | 'SUCCESS';

interface Notification {
  id: string;
  priority: AlertPriority;
  severity: NotificationSeverity;
  title: string;
  message: string;
  /** i18n 키 (LOCK L16: ko-KR) */
  i18nKey?: string;
  /** 관련 FailureCode (L20) */
  failureCode?: string;
  /** 자동 닫힘 시간 ms (P2 토스트 전용, 0 = 수동 닫기) */
  autoDismissMs: number;
  /** 생성 타임스탬프 */
  createdAt: number;
  /** 읽음 여부 */
  isRead: boolean;
}

interface Toast {
  id: string;
  notification: Notification;
  /** 표시 시작 시간 */
  shownAt: number;
}

/** 알림 큐 + 토스트 스택 + Alert Priority 3단계 (D2.0-08 §10.3) */
interface NotificationState {
  /** 알림 큐 (시간순) */
  queue: Notification[];
  /** 현재 표시 중인 토스트 스택 */
  activeToasts: Toast[];
  /** 최대 동시 표시 토스트 수 */
  maxToasts: number;
}

interface NotificationActions {
  /** 알림 큐에 추가 */
  enqueue: (notification: Omit<Notification, 'id' | 'createdAt' | 'isRead'>) => string;
  /** 큐에서 제거 */
  dequeue: (id: string) => void;
  /** 토스트 표시 */
  showToast: (notificationId: string) => void;
  /** 토스트 닫기 */
  dismissToast: (id: string) => void;
  /** 전체 알림 초기화 */
  clearAll: () => void;
  /** 알림 읽음 처리 */
  markAsRead: (id: string) => void;
  /** 읽지 않은 알림 수 조회 (파생) */
  getUnreadCount: () => number;
}

type NotificationStore = NotificationState & NotificationActions;
```

### 4.2 초기 상태 값

```typescript
const initialNotificationState: NotificationState = {
  queue: [],
  activeToasts: [],
  maxToasts: 5,   // 동시 표시 최대 5개
};
```

### 4.3 미들웨어 구성

```typescript
const useNotificationStore = create<NotificationStore>()(
  devtools(
    immer((set, get) => ({
      ...initialNotificationState,
      enqueue: (notification) => {
        const id = crypto.randomUUID();
        set((state) => {
          state.queue.push({
            ...notification,
            id,
            createdAt: Date.now(),
            isRead: false,
          });
        });
        return id;
      },
      dequeue: (id) => set((state) => {
        state.queue = state.queue.filter((n) => n.id !== id);
      }),
      showToast: (notificationId) => set((state) => {
        const notification = state.queue.find((n) => n.id === notificationId);
        if (notification && state.activeToasts.length < state.maxToasts) {
          state.activeToasts.push({
            id: crypto.randomUUID(),
            notification,
            shownAt: Date.now(),
          });
        }
      }),
      dismissToast: (id) => set((state) => {
        state.activeToasts = state.activeToasts.filter((t) => t.id !== id);
      }),
      clearAll: () => set(() => initialNotificationState),
      markAsRead: (id) => set((state) => {
        const notif = state.queue.find((n) => n.id === id);
        if (notif) notif.isRead = true;
      }),
      getUnreadCount: () => get().queue.filter((n) => !n.isRead).length,
    })),
    { name: 'notificationStore', enabled: process.env.NODE_ENV === 'development' }
  )
);
```

| 미들웨어 | 적용 | 이유 |
|---------|------|------|
| **persist** | X | 메모리 전용 -- 새로고침 시 초기화 (영속성: memory) |
| **devtools** | O (dev only) | 알림 큐 디버깅 |
| **immer** | O | 큐/스택 배열 조작 |

### 4.4 Selector 패턴

```typescript
const selectQueue = (state: NotificationStore) => state.queue;
const selectActiveToasts = (state: NotificationStore) => state.activeToasts;
const selectHasUnread = (state: NotificationStore) =>
  state.queue.some((n) => !n.isRead);
const selectUnreadCount = (state: NotificationStore) =>
  state.queue.filter((n) => !n.isRead).length;
const selectByPriority = (priority: AlertPriority) =>
  (state: NotificationStore) => state.queue.filter((n) => n.priority === priority);
```

**메모이제이션 전략**: `selectActiveToasts` -- 배열 reference 변경 빈번, `shallow` comparator 적용.

### 4.5 영속성 전략

| 필드 | 영속성 | 저장소 | 근거 |
|------|--------|--------|------|
| queue | **memory** | -- | 페이지 새로고침 시 초기화 |
| activeToasts | **memory** | -- | 실시간 토스트 스택 |
| maxToasts | **memory** | -- | 상수 (설정 변경 시 appStore config로 이동 가능) |

---

## 5. authStore

### 5.1 TypeScript 인터페이스

```typescript
// frontend/src/stores/authStore.ts

/** LOCK (Part2 §6.1.8, L10): RBAC 4단계 */
type RBACRole = 'OWNER' | 'ADMIN' | 'OPERATOR' | 'VIEWER';

interface User {
  id: string;
  name: string;
  email: string;
  avatarUrl?: string;
}

interface Permission {
  resource: string;
  actions: ('read' | 'write' | 'execute' | 'delete')[];
}

/** 인증/RBAC 상태 -- OWNER/ADMIN/OPERATOR/VIEWER 4단계 (L10) */
interface AuthState {
  /** 현재 사용자 */
  user: User | null;
  /** RBAC 역할 */
  role: RBACRole;
  /** 인증 완료 여부 */
  isAuthenticated: boolean;
  /** 권한 목록 */
  permissions: Permission[];
  /** 인증 토큰 만료 시각 */
  tokenExpiresAt: number | null;
}

interface AuthActions {
  /** 사용자 설정 (로그인 성공 시) */
  setUser: (user: User) => void;
  /** 역할 변경 */
  setRole: (role: RBACRole) => void;
  /** 로그아웃 */
  logout: () => void;
  /** 권한 확인 (리소스 + 액션) */
  hasPermission: (resource: string, action: 'read' | 'write' | 'execute' | 'delete') => boolean;
  /** 권한 목록 설정 */
  setPermissions: (permissions: Permission[]) => void;
  /** 토큰 만료 시각 갱신 */
  setTokenExpiry: (expiresAt: number) => void;
}

type AuthStore = AuthState & AuthActions;
```

### 5.2 초기 상태 값

```typescript
const initialAuthState: AuthState = {
  user: null,
  role: 'VIEWER',         // 최소 권한 원칙 (안전 기본값)
  isAuthenticated: false,
  permissions: [],
  tokenExpiresAt: null,
};
```

### 5.3 미들웨어 구성

```typescript
const useAuthStore = create<AuthStore>()(
  devtools(
    persist(
      immer((set, get) => ({
        ...initialAuthState,
        setUser: (user) => set((state) => {
          state.user = user;
          state.isAuthenticated = true;
        }),
        setRole: (role) => set((state) => { state.role = role; }),
        logout: () => set(() => initialAuthState),
        hasPermission: (resource, action) => {
          const { permissions, role } = get();
          if (role === 'OWNER') return true; // OWNER = 모든 권한
          return permissions.some(
            (p) => p.resource === resource && p.actions.includes(action)
          );
        },
        setPermissions: (permissions) => set((state) => {
          state.permissions = permissions;
        }),
        setTokenExpiry: (expiresAt) => set((state) => {
          state.tokenExpiresAt = expiresAt;
        }),
      })),
      {
        name: 'vamos-auth-store',
        partialize: (state) => ({
          user: state.user,
          role: state.role,
          isAuthenticated: state.isAuthenticated,
          tokenExpiresAt: state.tokenExpiresAt,
        }),
        storage: createTauriStorage(),
      }
    ),
    { name: 'authStore', enabled: process.env.NODE_ENV === 'development' }
  )
);
```

| 미들웨어 | 적용 | 이유 |
|---------|------|------|
| **persist** | O | 세션 간 인증 상태 유지 (Tauri localStorage) |
| **devtools** | O (dev only) | RBAC 역할 변경 추적 |
| **immer** | O | Permission 배열 불변 갱신 |

### 5.4 Selector 패턴

```typescript
const selectUser = (state: AuthStore) => state.user;
const selectRole = (state: AuthStore) => state.role;
const selectIsAuthenticated = (state: AuthStore) => state.isAuthenticated;
// 파라미터화 selector -- useCallback 래핑
const selectHasPermission = (resource: string, action: string) =>
  (state: AuthStore) => state.permissions.some(
    (p) => p.resource === resource && p.actions.includes(action as any)
  );
```

**메모이제이션 전략**: `selectHasPermission` -- 파라미터화 셀렉터, `useCallback` 래핑.

### 5.5 영속성 전략

| 필드 | 영속성 | 저장소 | 근거 |
|------|--------|--------|------|
| user | **persist** | Tauri localStorage | 로그인 상태 유지 |
| role | **persist** | Tauri localStorage | RBAC 역할 유지 |
| isAuthenticated | **persist** | Tauri localStorage | 인증 상태 유지 |
| permissions | **memory** | -- | 앱 시작 시 서버에서 재수신 |
| tokenExpiresAt | **persist** | Tauri localStorage | 토큰 만료 확인 |

### 5.6 RBAC 접근 제어 매핑 (Part2 §6.1.8)

> LOCK (Part2 §6.1.8, L10): OWNER / ADMIN / OPERATOR / VIEWER

| RBAC 역할 | 접근 가능 화면 | 제한 사항 |
|----------|-------------|----------|
| OWNER | 모든 화면 | 없음 |
| ADMIN | 모든 화면 | 시스템 삭제 불가 |
| OPERATOR | Dashboard, Chat, Workflow, Memory | Settings 읽기 전용 |
| VIEWER | Dashboard, Chat (읽기) | 입력/실행 불가, 조회만 가능 |

---

## 6. memoryStore

### 6.1 TypeScript 인터페이스

```typescript
// frontend/src/stores/memoryStore.ts

type MemoryLayer = 'L0' | 'L1' | 'L2';
type CandidateStatus = 'pending' | 'committed' | 'discarded';

interface MemoryCandidate {
  id: string;
  layer: MemoryLayer;
  content: string;
  sourceId: string;
  qodScore: number;
  qodLevel: 'high' | 'medium' | 'low';
  status: CandidateStatus;
  createdAt: number;
}

interface CommitRecord {
  candidateId: string;
  committedAt: number;
  layer: MemoryLayer;
}

/** 메모리 후보 + L0/L1/L2 상태 + 커밋 이력 */
interface MemoryState {
  /** 메모리 후보 목록 */
  candidates: MemoryCandidate[];
  /** 커밋 이력 */
  commitHistory: CommitRecord[];
  /** 마스킹 활성 상태 (PII 마스킹) */
  isMaskingActive: boolean;
  /** 선택된 계층 필터 */
  selectedLayer: MemoryLayer | 'ALL';
}

interface MemoryActions {
  /** 후보 추가 */
  addCandidate: (candidate: Omit<MemoryCandidate, 'id' | 'createdAt' | 'status'>) => void;
  /** 후보 제거 (ID 기반) */
  removeCandidateById: (id: string) => void;
  /** 후보 커밋 */
  commitCandidate: (id: string) => void;
  /** 후보 폐기 */
  discardCandidate: (id: string) => void;
  /** 마스킹 활성화/비활성화 */
  setMaskingActive: (active: boolean) => void;
  /** 계층 필터 변경 */
  setSelectedLayer: (layer: MemoryLayer | 'ALL') => void;
  /** 전체 초기화 */
  reset: () => void;
}

type MemoryStore = MemoryState & MemoryActions;
```

### 6.2 초기 상태 값

```typescript
const initialMemoryState: MemoryState = {
  candidates: [],
  commitHistory: [],
  isMaskingActive: false,
  selectedLayer: 'ALL',
};
```

### 6.3 미들웨어 구성

```typescript
const useMemoryStore = create<MemoryStore>()(
  devtools(
    immer((set) => ({
      ...initialMemoryState,
      addCandidate: (candidate) => set((state) => {
        state.candidates.push({
          ...candidate,
          id: crypto.randomUUID(),
          createdAt: Date.now(),
          status: 'pending',
        });
      }),
      removeCandidateById: (id) => set((state) => {
        state.candidates = state.candidates.filter((c) => c.id !== id);
      }),
      commitCandidate: (id) => set((state) => {
        const candidate = state.candidates.find((c) => c.id === id);
        if (candidate) {
          candidate.status = 'committed';
          state.commitHistory.push({
            candidateId: id,
            committedAt: Date.now(),
            layer: candidate.layer,
          });
        }
      }),
      discardCandidate: (id) => set((state) => {
        const candidate = state.candidates.find((c) => c.id === id);
        if (candidate) candidate.status = 'discarded';
      }),
      setMaskingActive: (active) => set((state) => {
        state.isMaskingActive = active;
      }),
      setSelectedLayer: (layer) => set((state) => {
        state.selectedLayer = layer;
      }),
      reset: () => set(() => initialMemoryState),
    })),
    { name: 'memoryStore', enabled: process.env.NODE_ENV === 'development' }
  )
);
```

| 미들웨어 | 적용 | 이유 |
|---------|------|------|
| **persist** | X | 세션 종료 시 초기화 (영속성: session) |
| **devtools** | O (dev only) | 메모리 후보 커밋/폐기 추적 |
| **immer** | O | 후보 배열 + 중첩 상태 갱신 |

### 6.4 Selector 패턴

```typescript
const selectCandidates = (state: MemoryStore) => state.candidates;
const selectByLayer = (layer: MemoryLayer) =>
  (state: MemoryStore) => state.candidates.filter((c) => c.layer === layer);
const selectCommitHistory = (state: MemoryStore) => state.commitHistory;
const selectIsMasking = (state: MemoryStore) => state.isMaskingActive;
const selectPendingCandidates = (state: MemoryStore) =>
  state.candidates.filter((c) => c.status === 'pending');
const selectByQodLevel = (level: 'high' | 'medium' | 'low') =>
  (state: MemoryStore) => state.candidates.filter((c) => c.qodLevel === level);
```

**메모이제이션 전략**: `selectByLayer` -- 파라미터화 필터, `useMemo` + layer 의존성.

### 6.5 영속성 전략

| 필드 | 영속성 | 저장소 | 근거 |
|------|--------|--------|------|
| candidates | **session** | sessionStorage | 세션 내 후보 유지 |
| commitHistory | **session** | sessionStorage | 세션 내 이력 유지 |
| isMaskingActive | **memory** | -- | 실시간 마스킹 상태 |
| selectedLayer | **memory** | -- | UI 필터 상태 |

---

## 7. workflowStore

### 7.1 TypeScript 인터페이스

```typescript
// frontend/src/stores/workflowStore.ts

type RunState = 'idle' | 'running' | 'paused' | 'completed' | 'failed';

type PipelineStage =
  | 'S0_RECEIVED'
  | 'S1_INTENT_PARSED'
  | 'S2_EVIDENCE_READY'
  | 'S3_DECISION_LOCKED'
  | 'S4_EXECUTING'
  | 'S5_OUTPUT_READY'
  | 'S6_SELF_CHECKED'
  | 'S7_MEMORY_COMMITTED'
  | 'S8_DONE';

interface Node {
  id: string;
  type: string;
  label: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  position: { x: number; y: number };
}

interface Edge {
  id: string;
  source: string;
  target: string;
  animated: boolean;
}

/** 워크플로우 그래프 + 실행 상태 + 파이프라인 S0~S8 추적 */
interface WorkflowState {
  /** 워크플로우 노드 목록 */
  nodes: Node[];
  /** 워크플로우 엣지 목록 */
  edges: Edge[];
  /** 실행 상태 */
  runState: RunState;
  /** 현재 실행 스텝 */
  currentStep: number;
  /** 전체 스텝 수 */
  totalSteps: number;
  /** 파이프라인 단계 (S0~S8) */
  pipelineStage: PipelineStage;
  /** 스트리밍 청크 버퍼 (S7C-038) */
  streamBuffer: string;
  /** 스트리밍 활성 여부 */
  isStreaming: boolean;
}

interface WorkflowActions {
  /** 노드 목록 설정 */
  setNodes: (nodes: Node[]) => void;
  /** 엣지 목록 설정 */
  setEdges: (edges: Edge[]) => void;
  /** 실행 상태 변경 */
  updateRunState: (runState: RunState) => void;
  /** 다음 스텝으로 진행 */
  advanceStep: () => void;
  /** 파이프라인 단계 변경 */
  setPipelineStage: (stage: PipelineStage) => void;
  /** 노드 상태 업데이트 */
  updateNodeStatus: (nodeId: string, status: Node['status']) => void;
  /** 스트림 청크 추가 */
  appendStreamChunk: (chunk: string) => void;
  /** 스트림 버퍼 초기화 */
  clearStreamBuffer: () => void;
  /** 전체 초기화 */
  reset: () => void;
}

type WorkflowStore = WorkflowState & WorkflowActions;
```

### 7.2 초기 상태 값

```typescript
const initialWorkflowState: WorkflowState = {
  nodes: [],
  edges: [],
  runState: 'idle',
  currentStep: 0,
  totalSteps: 0,
  pipelineStage: 'S0_RECEIVED',
  streamBuffer: '',
  isStreaming: false,
};
```

### 7.3 미들웨어 구성

```typescript
const useWorkflowStore = create<WorkflowStore>()(
  devtools(
    immer((set) => ({
      ...initialWorkflowState,
      setNodes: (nodes) => set((state) => { state.nodes = nodes; }),
      setEdges: (edges) => set((state) => { state.edges = edges; }),
      updateRunState: (runState) => set((state) => { state.runState = runState; }),
      advanceStep: () => set((state) => {
        if (state.currentStep < state.totalSteps) {
          state.currentStep += 1;
        }
      }),
      setPipelineStage: (stage) => set((state) => {
        state.pipelineStage = stage;
      }),
      updateNodeStatus: (nodeId, status) => set((state) => {
        const node = state.nodes.find((n) => n.id === nodeId);
        if (node) node.status = status;
      }),
      appendStreamChunk: (chunk) => set((state) => {
        state.streamBuffer += chunk;
        state.isStreaming = true;
      }),
      clearStreamBuffer: () => set((state) => {
        state.streamBuffer = '';
        state.isStreaming = false;
      }),
      reset: () => set(() => initialWorkflowState),
    })),
    { name: 'workflowStore', enabled: process.env.NODE_ENV === 'development' }
  )
);
```

| 미들웨어 | 적용 | 이유 |
|---------|------|------|
| **persist** | X | 세션 종료 시 초기화 (영속성: session) |
| **devtools** | O (dev only) | 파이프라인 S0~S8 진행 추적 |
| **immer** | O | 노드 배열 + 중첩 상태 빈번 갱신 |

### 7.4 Selector 패턴

```typescript
const selectNodes = (state: WorkflowStore) => state.nodes;
const selectEdges = (state: WorkflowStore) => state.edges;
const selectRunState = (state: WorkflowStore) => state.runState;
const selectPipelineStage = (state: WorkflowStore) => state.pipelineStage;
const selectProgress = (state: WorkflowStore) => ({
  currentStep: state.currentStep,
  totalSteps: state.totalSteps,
  percentage: state.totalSteps > 0 ? (state.currentStep / state.totalSteps) * 100 : 0,
});
const selectStreamBuffer = (state: WorkflowStore) => state.streamBuffer;
const selectIsStreaming = (state: WorkflowStore) => state.isStreaming;
const selectNodeById = (nodeId: string) =>
  (state: WorkflowStore) => state.nodes.find((n) => n.id === nodeId);
```

**메모이제이션 전략**:
- `selectProgress` -- `currentStep/totalSteps` 비율 계산, `useMemo` 적용
- `selectPipelineStage` -- S0~S8 이벤트 기반 갱신, throttle 불필요 (D2.0-08 §4.4)
- `selectStreamBuffer` -- 매 chunk마다 갱신, 컴포넌트에서 `requestAnimationFrame` 기반 렌더링

### 7.5 영속성 전략

| 필드 | 영속성 | 저장소 | 근거 |
|------|--------|--------|------|
| nodes / edges | **session** | sessionStorage | 워크플로우 그래프 세션 유지 |
| runState | **memory** | -- | 실행 상태 실시간 |
| currentStep / totalSteps | **memory** | -- | 진행 상태 실시간 |
| pipelineStage | **memory** | -- | S0~S8 실시간 |
| streamBuffer | **memory** | -- | 스트리밍 임시 버퍼 |

### 7.6 관할 UI 상태 범위

| 9-State | workflowStore 관할 | 비고 |
|---------|-------------------|------|
| UI_S2_EDITING | O | Builder 편집 중 |
| UI_S3_READY | O | 사전 점검 통과 |
| UI_S4_RUNNING | O (decisionStore와 공동) | 실행 중 + Decision Lock |
| UI_S6_PRESENTING | O | 결과 표시 |
| UI_S7_RECOVERY | O (notificationStore와 공동) | 실패/폴백/재시도 |

---

## 8. Store 간 관계 정의

### 8.1 Store 간 참조/구독 그래프

```
appStore (전역)
  │
  ├── [참조됨] workflowStore.pipelineStage === 'S8_DONE'
  │     → appStore.setUiState('UI_S8_ARCHIVED')
  │
  └── [참조됨] authStore.isAuthenticated
        → appStore 초기화 시 인증 상태 확인

decisionStore
  │
  ├── [참조] costStore.estCost
  │     → Decision 시 비용 근거 참조
  │
  └── [참조됨] workflowStore.setPipelineStage('S3_DECISION_LOCKED')
        → decisionStore.isLocked = true 동기

costStore
  │
  └── [참조됨] notificationStore.enqueue()
        → cost.warning / cost.ceiling 이벤트 시 알림 생성

notificationStore
  │
  ├── [참조] costStore (비용 경고 이벤트)
  │     → isWarning80 / isCeiling100 변경 시 알림 enqueue
  │
  └── [참조] authStore.role
        → 승인 요청 시 역할 기반 표시 여부 판단

authStore
  │
  └── [참조됨] notificationStore (역할 기반 알림)
        → RBAC 권한에 따른 알림 표시 필터

memoryStore
  │
  └── [참조됨] workflowStore.setPipelineStage('S7_MEMORY_COMMITTED')
        → commitHistory 추가

workflowStore
  │
  ├── [참조] decisionStore.isLocked
  │     → S3_DECISION_LOCKED 시 동기
  │
  └── [참조됨] appStore (S8_DONE → ARCHIVED 전이)
```

### 8.2 갱신 순서 규칙

| 순번 | 이벤트 | Store 갱신 순서 | 근거 |
|------|--------|---------------|------|
| 1 | Decision Lock | costStore.estCost 참조 -> decisionStore.lockDecision() -> workflowStore.setPipelineStage('S3') | 비용 선확인 후 잠금 |
| 2 | Cost Warning (80%) | costStore.updateCost() -> costStore.isWarning80 = true -> notificationStore.enqueue(WARN) | 비용 갱신 후 알림 |
| 3 | Cost Ceiling (100%) | costStore.updateCost() -> costStore.isCeiling100 = true -> costStore.downshift() -> notificationStore.enqueue(ERROR) | 상한 후 다운시프트 + 알림 |
| 4 | 승인 요청 | authStore.role 확인 -> decisionStore (승인 대기) -> notificationStore.enqueue(P0) | 권한 확인 후 대기 |
| 5 | 메모리 커밋 | memoryStore.commitCandidate() -> workflowStore.setPipelineStage('S7') | 커밋 후 파이프라인 진행 |
| 6 | 세션 완료 | workflowStore.setPipelineStage('S8') -> appStore.setUiState('UI_S8_ARCHIVED') | 파이프라인 종료 후 아카이브 |

---

## 9. Store <-> Hook 매핑

### 9.1 Store 구독 Hook

| Store | 주 구독 Hook | 직접 사용 가능 컴포넌트 |
|-------|------------|---------------------|
| appStore | useAutonomy | CM-THEME-01, CM-I18N-01, CM-NAV-02 |
| decisionStore | useDecision | BV-PIPE-02, HV-STATE-01, HV-STATE-02 |
| costStore | useCost | HV-COST-01, HV-COST-02, BV-DEBUG-02 |
| notificationStore | useNotification | CM-ALERT-01, CM-ALERT-02, CM-ALERT-03 |
| authStore | (직접 구독) | CM-NAV-02, HV-APPR-01 |
| memoryStore | useMemory | HV-MEM-01, HV-MEM-02 |
| workflowStore | useWorkflow | BV-PIPE-01, HV-STATE-01, HV-STATE-02 |

### 9.2 Hook -> Store 의존성 (custom_hooks.md 교차 참조)

| Hook | 의존 Store | 읽기/쓰기 |
|------|----------|----------|
| useTauriIPC | -- (직접 IPC) | -- |
| useDecision | decisionStore | R/W |
| useWorkflow | workflowStore | R/W |
| useMemory | memoryStore | R/W |
| useCost | costStore | R/W |
| useNotification | notificationStore | R/W |
| useAutonomy | appStore | R/W (autonomyLevel) |
| useLog | -- (직접 IPC 스트림) | -- |

---

## 10. Store <-> 컴포넌트 매핑

### 10.1 Builder View (BV-*)

| 컴포넌트 ID | 컴포넌트 이름 | 구독 Store | 구독 필드 |
|------------|------------|-----------|----------|
| BV-PIPE-01 | PipelineStatusBar | workflowStore | pipelineStage, runState, currentStep, totalSteps |
| BV-PIPE-02 | DecisionLockBanner | decisionStore | isLocked, currentDecision, lockTimestamp |
| BV-DEBUG-01 | TraceLogPanel | -- (useLog 직접) | -- |
| BV-DEBUG-02 | CostMeterWidget | costStore | tokenIn, tokenOut, estCost, budgetRemaining |
| BV-CONFIG-01 | ConfigEditorPanel | appStore | -- (useTauriIPC 경유) |

### 10.2 Hologram View (HV-*)

| 컴포넌트 ID | 컴포넌트 이름 | 구독 Store | 구독 필드 |
|------------|------------|-----------|----------|
| HV-STATE-01 | AgentStatusIndicator | workflowStore, decisionStore | runState, pipelineStage, isLocked |
| HV-STATE-02 | ProgressTracker | workflowStore, decisionStore | currentStep, totalSteps, pipelineStage |
| HV-COST-01 | CostWarningBanner | costStore | isWarning80, isCeiling100, mode |
| HV-COST-02 | CostBreakdownPopover | costStore | sessionCost, dailyCost, monthlyCost, tokenIn, tokenOut |
| HV-MEM-01 | MemoryCandidatePanel | memoryStore | candidates, selectedLayer |
| HV-MEM-02 | MaskingPreview | memoryStore | isMaskingActive, candidates |
| HV-APPR-01 | ApprovalCard | authStore, decisionStore | role, isAuthenticated, isLocked |

### 10.3 Common (CM-*)

| 컴포넌트 ID | 컴포넌트 이름 | 구독 Store | 구독 필드 |
|------------|------------|-----------|----------|
| CM-ALERT-01 | AlertModal (P0) | notificationStore | queue (priority === 'P0_MODAL') |
| CM-ALERT-02 | ApprovalSlidePanel (P1) | notificationStore | queue (priority === 'P1_SLIDE') |
| CM-ALERT-03 | ToastNotification (P2) | notificationStore | activeToasts |
| CM-THEME-01 | ThemeToggle | appStore | theme |
| CM-I18N-01 | LanguageSelector | appStore | locale |
| CM-NAV-02 | SettingsPanel | appStore, authStore | autonomyLevel, role, theme, locale |

---

## 11. 영속성 전략 총괄

### 11.1 저장소 분류

| 저장소 유형 | Store | persist 대상 필드 | 복원 시점 |
|-----------|-------|-----------------|----------|
| **Tauri localStorage** | appStore | theme, locale, autonomyLevel, isSidebarCollapsed | 앱 시작 시 자동 복원 |
| **Tauri localStorage** | authStore | user, role, isAuthenticated, tokenExpiresAt | 앱 시작 시 자동 복원 + 토큰 만료 검증 |
| **sessionStorage** | decisionStore | -- (persist 미적용, 세션 복원 로직 별도) | 승인 대기 중 새로고침 시 IPC 재조회 |
| **memory only** | costStore | -- | 앱 시작/세션 시작 시 서버 조회 |
| **memory only** | notificationStore | -- | 새로고침 시 초기화 (의도적) |
| **memory only** | memoryStore | -- | 세션 시작 시 서버 조회 |
| **memory only** | workflowStore | -- | 세션 시작 시 서버 조회 |

### 11.2 Tauri Storage 어댑터

```typescript
// frontend/src/stores/utils/tauriStorage.ts

import { Store as TauriStore } from '@tauri-apps/plugin-store';

/**
 * Zustand persist용 Tauri Storage 어댑터
 * Tauri 환경에서는 @tauri-apps/plugin-store 사용
 * 비Tauri 환경(테스트)에서는 localStorage 폴백
 */
function createTauriStorage() {
  const isTauri = typeof window !== 'undefined' && '__TAURI__' in window;

  if (isTauri) {
    const store = new TauriStore('.vamos-settings.dat');
    return {
      getItem: async (name: string) => {
        const value = await store.get<string>(name);
        return value ?? null;
      },
      setItem: async (name: string, value: string) => {
        await store.set(name, value);
        await store.save();
      },
      removeItem: async (name: string) => {
        await store.delete(name);
        await store.save();
      },
    };
  }

  // 폴백: localStorage (개발/테스트 환경)
  return {
    getItem: (name: string) => localStorage.getItem(name),
    setItem: (name: string, value: string) => localStorage.setItem(name, value),
    removeItem: (name: string) => localStorage.removeItem(name),
  };
}

export { createTauriStorage };
```

### 11.3 승인 대기 상태 복원 (D2.0-08 §5.1 참조)

> _index.md §5.1: "승인 대기 상태에서 UI 닫힘/새로고침 시 -> 세션 복원 시 UI_S5_AWAIT_APPROVAL 복원"

```typescript
// 앱 초기화 시 세션 복원 흐름
async function restoreSession() {
  const sessionId = useAppStore.getState().sessionId;
  if (!sessionId) return;

  // 1. 서버에서 현재 세션 상태 조회
  const serverState = await invoke('session:status', { sessionId });

  // 2. 승인 대기 상태인 경우 decisionStore 복원
  if (serverState.awaitingApproval) {
    useDecisionStore.getState().lockDecision(
      serverState.decision,
      serverState.evidence
    );
    useAppStore.getState().setUiState('UI_S5_AWAIT_APPROVAL'); // -> UI_S5_AWAIT_APPROVAL 전이
  }

  // 3. 워크플로우 복원
  if (serverState.workflow) {
    useWorkflowStore.getState().setNodes(serverState.workflow.nodes);
    useWorkflowStore.getState().setEdges(serverState.workflow.edges);
    useWorkflowStore.getState().setPipelineStage(serverState.workflow.pipelineStage);
  }
}
```

---

## 12. STEP7-C Store 관련 항목 매핑

### 12.1 직접 매핑 (12건)

| S7C ID | Part | 설명 | 관련 Store | Store 필드/액션 | 우선순위 |
|--------|------|------|-----------|---------------|---------|
| S7C-030 | 3 | 비용 미리보기 | costStore | estCost, tokenIn, tokenOut | HIGH |
| S7C-038 | 4 | 스트리밍 타이핑 효과 | workflowStore | streamBuffer, appendStreamChunk() | HIGH |
| S7C-060 | 6 | 오프라인 UI 상태 | appStore | isOnline, setOnlineStatus() | MEDIUM |
| S7C-063 | 7 | 에이전트 실행 진행률 | workflowStore | currentStep, totalSteps, advanceStep() | HIGH |
| S7C-069 | 7 | 3-Gate 통과 표시 | costStore + decisionStore | isWarning80, isCeiling100, isLocked | HIGH |
| S7C-070 | 7 | 파이프라인 스텝 표시 | workflowStore | pipelineStage, setPipelineStage() | MEDIUM |
| S7C-072 | 8 | 메모리 관리 UI | memoryStore | candidates, commitCandidate(), discardCandidate() | MEDIUM |
| S7C-074 | 8 | 비용 대시보드 | costStore | sessionCost, dailyCost, monthlyCost | HIGH |
| S7C-076 | 8 | 모델 설정 | appStore | autonomyLevel, setAutonomyLevel() | MEDIUM |
| S7C-081 | 9 | 3-Gate 상태 표시기 | costStore + decisionStore | isWarning80, isCeiling100, isLocked | HIGH |
| S7C-082 | 9 | 비용 실시간 게이지 | costStore | sessionCost, dailyCost, monthlyCost, budgetRemaining | HIGH |
| S7C-083 | 9 | QoD 신뢰도 바 | memoryStore | candidates[].qodScore, candidates[].qodLevel | HIGH |

### 12.2 공유 항목 (04_react-components 공유 -- 5건)

| S7C ID | Part | 설명 | Store 상태 기여 |
|--------|------|------|---------------|
| S7C-029 | 3 | 토큰 카운터 | costStore.tokenIn, costStore.tokenOut |
| S7C-040 | 5 | 3-Part 출력 UI | workflowStore.runState, workflowStore.pipelineStage |
| S7C-041 | 5 | 신뢰도 표시바 | memoryStore.candidates[].qodScore |
| S7C-042 | 5 | 비용 표시 | costStore.estCost, costStore.mode |
| S7C-065 | 7 | 병렬 에이전트 상태 | workflowStore.nodes[].status |

**합계**: 직접 12건 (HIGH 8건 / MEDIUM 4건) + 공유 5건 = 17건

---

## 13. LOCK 참조 테이블

| LOCK | 항목 | 정본 출처 | 값 | 본 문서 적용 |
|------|------|---------|-----|------------|
| L1 | UI 9-State | D2.0-08 §4.1 | UI_S0~UI_S8 (9개) | §1.6, §2.6, §7.6 관할 매핑 |
| L7 | 다크모드 | D2.0-08 §10.1 | 기본 Dark (#1E1E1E) | appStore 초기 theme = 'dark' |
| L10 | RBAC 4단계 | Part2 §6.1.8 | OWNER/ADMIN/OPERATOR/VIEWER | authStore.role 타입 |
| L15 | Zustand Stores 수 | Part2 §6.1.3 | 7개 | 본 문서 전체 (7 Store) |
| L16 | i18n 기본 로케일 | D2.0-08 §0 | ko-KR | appStore 초기 locale = 'ko-KR' |
| L17 | 전이 지연 | D2.0-08 §4.4 | 최대 500ms | Store 갱신 이벤트 기반 (폴링 금지) |
| L19 | 이벤트 네이밍 | D2.0-08 §5.1 | `ui.{layer}.{subject}.{action}` | Store 갱신 이벤트 패턴 |
| L20 | FailureCode + Fallback | D2.0-08 §7.6 | 14 + 9 | _index.md §7 참조 (Store 상태 전이) |

---

## 14. 검증 체크리스트

- [x] Store 7개가 Part2 §6.1.3 정본과 1:1 대응 (LOCK L15): appStore, decisionStore, costStore, notificationStore, authStore, memoryStore, workflowStore
- [x] 모든 Store의 TypeScript 인터페이스(State + Actions) 정의 완료 (§1~§7)
- [x] 초기 상태 값 전체 정의 완료 (§1.2~§7.2)
- [x] 미들웨어 구성(persist/devtools/immer) 명시 (§1.3~§7.3)
- [x] Selector 패턴 + 메모이제이션 전략 정의 (§1.4~§7.4)
- [x] Store 간 관계 정의 + 갱신 순서 규칙 (§8)
- [x] Store <-> Hook 매핑이 custom_hooks.md(P1-10)와 정합 (§9)
- [x] Store <-> 컴포넌트 매핑이 _index.md §4.4와 정합 (§10)
- [x] 영속성 분류(persist 대상 vs. 메모리 전용) 완료 (§11)
- [x] Tauri localStorage 어댑터 정의 (§11.2)
- [x] STEP7-C Store 관련 항목 매핑 17건 (§12)
- [x] LOCK 참조 테이블 8건 정합 (§13)

---

## 15. 교차 검증 결과

### 15.1 Part2 §6.1.3 대조

| 검증 항목 | 결과 | 비고 |
|----------|------|------|
| Store 7개 이름 일치 | MATCH | appStore, decisionStore, costStore, notificationStore, authStore, memoryStore, workflowStore |
| LOCK L15 = 7개 | MATCH | 임의 추가/삭제 없음 |
| 네이밍 교정 반영 | MATCH | PHASE_B2 §3.1: agent -> notification, config -> auth |

### 15.2 _index.md §3 대조

| 검증 항목 | 결과 | 비고 |
|----------|------|------|
| Store별 역할 | MATCH | _index.md §3.1~§3.7 역할 정의와 일치 |
| 슬라이스 필드 | MATCH (확장) | L3 상세에서 TypeScript 타입 보강, 필드 추가 없음 |
| 셀렉터 목록 | MATCH (확장) | 추가 selector는 기존 패턴 연장 |

### 15.3 custom_hooks.md (P1-10) 대조

| 검증 항목 | 결과 | 비고 |
|----------|------|------|
| Hook -> Store 의존성 | MATCH | §9.2 매핑이 custom_hooks.md 의존성과 일치 |
| Store 인터페이스 호환 | MATCH | Hook 반환 타입이 Store State 필드 참조 |

### 15.4 CONFLICT / LOCK 변경 사항

- **CONFLICT 발견**: 0건
- **LOCK 변경**: 0건 (L1, L7, L10, L15, L16, L17, L19, L20 전체 변경 없음)

---

## 변경 이력

| 일자 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-12 | v1.0 | P1-11 초기 작성. Zustand Stores 7개 L3 상세 명세 (TypeScript 인터페이스, 초기 상태, 미들웨어, selector, Store 간 관계, Hook/컴포넌트 매핑, 영속성 전략, STEP7-C 17건 매핑) |
