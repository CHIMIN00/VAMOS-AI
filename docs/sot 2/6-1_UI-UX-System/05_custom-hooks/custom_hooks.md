# Custom Hooks 8개 — L3 상세 명세

> **도메인**: 6-1_UI-UX-System / 05_custom-hooks
> **버전**: v1.0
> **작성일**: 2026-04-12 (P1-10)
> **정본 출처**: Part2 §6.1.3 (주 정본), D2.0-08 §4·§5·§7 (설계 참조)
> **LOCK 참조**: L14 (Custom Hooks 수 8개), L1 (9-State), L17 (전이 지연 500ms), L19 (이벤트 네이밍), L20 (FailureCode 14 + FallbackRegistry 9)
> **Phase**: Phase 1 (V1-P4 Week 13-14)
> **산출물 ID**: P1-10

---

## 0. 문서 개요

본 문서는 Part2 §6.1.3 정본 기반 Custom Hooks 8개(LOCK L14)의 L3 상세 명세를 정의한다.

> LOCK (Part2 §6.1.3, L14): Hooks (8개): useTauriIPC, useDecision, useWorkflow, useMemory, useCost, useNotification, useAutonomy, useLog

**L3 기준 (종합계획서 §13)**:
- E1: TypeScript 시그니처 (파라미터 + 반환 타입)
- E2: 상태 전이 규칙 (트리거 조건 + 가드)
- E3: 이벤트 핸들러 (구독 EventType + UI 반응)
- E6: 의존성 명세 (Store/Hook/외부 라이브러리)
- E7: 테스트 시나리오 (최소 3건/Hook: 정상/에러/경계)

---

## 1. useTauriIPC

### 1.1 TypeScript 시그니처

```typescript
// frontend/src/hooks/useTauriIPC.ts

interface UseTauriIPCOptions {
  /** 자동 재연결 활성화 (기본: true) */
  autoReconnect?: boolean;
  /** 재연결 최대 시도 횟수 (기본: 3) */
  maxRetries?: number;
  /** 요청 타임아웃 ms (기본: 5000) */
  timeout?: number;
}

interface UseTauriIPCReturn<T = unknown> {
  /** IPC 커맨드 호출 */
  invoke: <R = T>(command: string, args?: Record<string, unknown>) => Promise<R>;
  /** IPC 이벤트 리스너 등록 — UnlistenFn 반환 */
  listen: (event: string, callback: (payload: unknown) => void) => UnlistenFn;
  /** Tauri 백엔드 연결 상태 */
  isConnected: boolean;
  /** 마지막 에러 (null = 에러 없음) */
  error: Error | null;
  /** 연결 재시도 중 여부 */
  isRetrying: boolean;
}

type UnlistenFn = () => void;

function useTauriIPC(options?: UseTauriIPCOptions): UseTauriIPCReturn;
```

### 1.2 내부 로직 흐름

```
초기화 (mount)
  ├─ 1. Tauri window.__TAURI__ 존재 확인
  │     ├─ 존재 → isConnected = true
  │     └─ 미존재 → isConnected = false, error 설정
  ├─ 2. invoke 함수 생성 (useCallback)
  │     ├─ tauri.invoke(command, args) 호출
  │     ├─ timeout 초과 시 AbortError throw
  │     └─ 에러 시 error 상태 갱신 + 자동 재연결 시도
  ├─ 3. listen 함수 생성 (useCallback)
  │     ├─ tauri.event.listen(event, callback) 호출
  │     └─ UnlistenFn 반환 (cleanup에서 자동 해제)
  └─ 4. 연결 상태 모니터링 시작
        └─ window focus 이벤트에서 heartbeat 체크

구독 (active)
  ├─ IPC invoke 호출 시 trace_id 자동 주입
  ├─ 에러 발생 시 autoReconnect 로직 실행
  └─ maxRetries 초과 시 isConnected = false 확정

정리 (unmount)
  ├─ 등록된 모든 listener unlisten() 호출
  ├─ 진행 중 invoke AbortController.abort()
  └─ 재연결 타이머 clearTimeout
```

### 1.3 의존성

| 구분 | 대상 | 설명 |
|------|------|------|
| **Store** | — | 직접 IPC, Store 비의존 |
| **Hook** | — | 최상위 Hook (다른 Hook에 의존 안 함) |
| **외부** | @tauri-apps/api | invoke, event.listen |
| **경계** | 4-1 Rust-Tauri | AUTHORITY_CHAIN §5.2: 프론트엔드 호출 인터페이스 |

### 1.4 구독 EventType

> LOCK (D2.0-08 §5.1, L19): `ui.{layer}.{subject}.{action}`

| EventType | 트리거 | UI 반응 |
|-----------|--------|---------|
| ui.cli.command.received | CLI 명령 수신 | 명령 에코 표시 |
| ui.cli.command.completed | CLI 명령 완료 | 결과 렌더링 |
| ui.cli.command.failed | CLI 명령 실패 | 에러 메시지 표시 |
| ui.cli.auth.prompted | 인증 요청 | 인증 프롬프트 표시 |
| ui.cli.auth.resolved | 인증 완료 | 프롬프트 닫기 |
| ui.cli.progress.updated | 진행률 갱신 | 프로그레스 바 갱신 |
| ui.cli.output.streamed | 스트림 출력 | 실시간 출력 표시 |
| ui.cli.config.changed | 설정 변경 | 설정 반영 |
| ui.cli.session.started | 세션 시작 | 세션 UI 초기화 |
| ui.cli.session.ended | 세션 종료 | 세션 UI 정리 |

**합계**: 10건 (ui.cli.* 레이어)

### 1.5 리렌더링 최적화

| 패턴 | 적용 대상 | 이유 |
|------|----------|------|
| `useCallback` | invoke, listen 함수 | 참조 안정성 — 하위 컴포넌트 불필요 리렌더링 방지 |
| `useRef` | listener 등록 목록 | 리렌더링 없이 listener 추적 |
| `useMemo` | — | 반환 객체가 primitive + 함수로 구성, 별도 memoize 불필요 |

### 1.6 테스트 전략

```typescript
// __tests__/hooks/useTauriIPC.test.ts
import { renderHook, act } from '@testing-library/react-hooks';

// T1: 정상 — invoke 성공
test('invoke returns IPC response', async () => {
  // Mock: tauri.invoke → { status: 'ok', data: {...} }
  const { result } = renderHook(() => useTauriIPC());
  const response = await result.current.invoke('vamos:workflow:start', { session_id: 's1' });
  expect(response.status).toBe('ok');
  expect(result.current.isConnected).toBe(true);
  expect(result.current.error).toBeNull();
});

// T2: 에러 — IPC 연결 실패
test('sets error on IPC failure', async () => {
  // Mock: tauri.invoke → throw Error('IPC_DISCONNECTED')
  const { result } = renderHook(() => useTauriIPC({ maxRetries: 0 }));
  await act(async () => {
    await expect(result.current.invoke('invalid:cmd')).rejects.toThrow();
  });
  expect(result.current.error).not.toBeNull();
  expect(result.current.isConnected).toBe(false);
});

// T3: 경계 — 타임아웃
test('aborts invoke after timeout', async () => {
  // Mock: tauri.invoke → delay 10s
  const { result } = renderHook(() => useTauriIPC({ timeout: 100 }));
  await act(async () => {
    await expect(result.current.invoke('slow:cmd')).rejects.toThrow('AbortError');
  });
});

// T4: cleanup — unmount 시 listener 해제
test('unlisten all on unmount', () => {
  const unlisten = jest.fn();
  // Mock: tauri.event.listen → returns unlisten
  const { result, unmount } = renderHook(() => useTauriIPC());
  act(() => { result.current.listen('test.event', () => {}); });
  unmount();
  expect(unlisten).toHaveBeenCalled();
});
```

**모킹 대상**: `@tauri-apps/api` (invoke, event.listen)

### 1.7 STEP7-C 매핑

| S7C ID | 설명 | 매핑 |
|--------|------|------|
| S7C-060 | 오프라인 UI 상태 | useTauriIPC.isConnected → appStore.isOnline 동기 |

---

## 2. useDecision

### 2.1 TypeScript 시그니처

```typescript
// frontend/src/hooks/useDecision.ts

interface Decision {
  id: string;
  traceId: string;
  conclusion: string;
  evidence: Evidence[];
  lockedAt: number;
  costEstimate: number;
}

interface Evidence {
  id: string;
  sourceId: string;
  qodScore: number;
  qodLevel: 'high' | 'medium' | 'low';
  content: string;
}

interface UseDecisionParams {
  traceId?: string;
}

interface UseDecisionReturn {
  /** 현재 Decision 객체 (null = 미잠금) */
  decision: Decision | null;
  /** Decision Lock 여부 */
  isLocked: boolean;
  /** 수집된 근거 목록 */
  evidence: Evidence[];
  /** 잠금 시각 (epoch ms, null = 미잠금) */
  lockTimestamp: number | null;
  /** P2 도메인 잠금 상태 */
  p2Status: { domain: string | null; agreed: boolean };
  /** Decision Lock 요청 */
  lockDecision: (decision: Decision) => Promise<void>;
  /** Decision 초기화 */
  clearDecision: () => void;
  /** 로딩 상태 */
  isLoading: boolean;
  /** 에러 상태 */
  error: Error | null;
}

function useDecision(params?: UseDecisionParams): UseDecisionReturn;
```

### 2.2 내부 로직 흐름

```
초기화 (mount)
  ├─ 1. useTauriIPC() 호출 — invoke/listen 획득
  ├─ 2. decisionStore 구독 (selectCurrentDecision, selectIsLocked)
  ├─ 3. traceId 파라미터 있으면 기존 Decision 조회
  │     └─ invoke('vamos:decision:get', { trace_id }) → decisionStore.lockDecision()
  └─ 4. EventType 리스너 등록 (5건)

구독 (active)
  ├─ ui.core.decision.locked → decisionStore.lockDecision()
  │   └─ R-61-5: Lock 이후 "결론 변경" UI 제공 금지
  ├─ ui.core.p2.locked → decisionStore.setP2Domain()
  ├─ ui.core.p2.modal.shown → P2 확인 모달 표시
  ├─ ui.core.p2.modal.confirmed → decisionStore.confirmP2()
  └─ ui.core.p2.modal.cancelled → decisionStore.cancelP2()

갱신
  ├─ lockDecision: invoke('vamos:decision:create', decision) → Store 갱신
  │   └─ 가드: isLocked === false 일 때만 실행 (이미 잠긴 경우 무시)
  └─ clearDecision: decisionStore.clearDecision() → 재시도 흐름 진입

정리 (unmount)
  ├─ 5건 EventType listener unlisten
  └─ Store 구독 해제 (Zustand unsubscribe)
```

### 2.3 의존성

| 구분 | 대상 | 설명 |
|------|------|------|
| **Store** | decisionStore | 현재 Decision + Lock 상태 + P2 도메인 |
| **Hook** | useTauriIPC | Decision Lock IPC invoke |
| **외부** | zustand | Store 구독 (shallow selector) |
| **제약** | R-61-5 | Decision Lock 이후 "결론 변경" UI 제공 금지 |

### 2.4 구독 EventType

| EventType | 트리거 | UI 반응 |
|-----------|--------|---------|
| ui.core.decision.locked | Core에서 Decision 확정 | DecisionLockBanner 표시, 결론 변경 UI 비활성 |
| ui.core.p2.locked | P2 도메인 잠금 | P2 상태 배지 갱신 |
| ui.core.p2.modal.shown | P2 확인 모달 요청 | 확인/취소 모달 렌더링 |
| ui.core.p2.modal.confirmed | P2 확인 | 모달 닫기 + 상태 반영 |
| ui.core.p2.modal.cancelled | P2 취소 | 모달 닫기 + 취소 상태 |

**합계**: 5건 (ui.core.* 레이어)

### 2.5 리렌더링 최적화

| 패턴 | 적용 대상 | 이유 |
|------|----------|------|
| `useCallback` | lockDecision, clearDecision | 액션 함수 참조 안정성 |
| 커스텀 comparator | selectCurrentDecision | Decision 객체 깊은 비교 → `JSON.stringify` 기반 |
| `useMemo` | evidence 배열 | decision 변경 시에만 재계산 |
| shallow selector | selectIsLocked, selectP2Status | primitive 값 비교 |

### 2.6 테스트 전략

```typescript
// __tests__/hooks/useDecision.test.ts

// T1: 정상 — Decision Lock 이벤트 수신
test('locks decision on decision.locked event', async () => {
  const { result } = renderHook(() => useDecision({ traceId: 'trace-1' }));
  // Simulate: ui.core.decision.locked event
  act(() => emitEvent('ui.core.decision.locked', { decision: mockDecision }));
  expect(result.current.isLocked).toBe(true);
  expect(result.current.decision?.id).toBe(mockDecision.id);
});

// T2: 에러 — IPC invoke 실패
test('sets error on IPC failure', async () => {
  // Mock: invoke → throw
  const { result } = renderHook(() => useDecision());
  await act(async () => {
    await result.current.lockDecision(mockDecision);
  });
  expect(result.current.error).not.toBeNull();
  expect(result.current.isLocked).toBe(false);
});

// T3: 경계 — 이미 잠긴 상태에서 재잠금 시도
test('ignores lockDecision when already locked', async () => {
  const { result } = renderHook(() => useDecision());
  // Pre-condition: lock first
  act(() => emitEvent('ui.core.decision.locked', { decision: mockDecision }));
  expect(result.current.isLocked).toBe(true);
  // Attempt re-lock — should be ignored (R-61-5)
  await act(async () => {
    await result.current.lockDecision(anotherDecision);
  });
  expect(result.current.decision?.id).toBe(mockDecision.id); // unchanged
});

// T4: P2 모달 확인/취소
test('handles P2 modal confirm flow', () => {
  const { result } = renderHook(() => useDecision());
  act(() => emitEvent('ui.core.p2.modal.shown', { domain: 'test' }));
  expect(result.current.p2Status.domain).toBe('test');
  act(() => emitEvent('ui.core.p2.modal.confirmed', {}));
  expect(result.current.p2Status.agreed).toBe(true);
});
```

**모킹 대상**: useTauriIPC (invoke/listen), decisionStore (Zustand)

### 2.7 STEP7-C 매핑

| S7C ID | 설명 | 매핑 |
|--------|------|------|
| S7C-069 | 3-Gate 통과 표시 — Policy/Cost/Evidence Gate | useDecision gate 상태 구독 |
| S7C-081 | 3-Gate 상태 표시기 (🟢/🟡/🔴) | decisionStore + costStore 구독 |

---

## 3. useWorkflow

### 3.1 TypeScript 시그니처

```typescript
// frontend/src/hooks/useWorkflow.ts

type PipelineStage =
  | 'S0_RECEIVED' | 'S1_INTENT_PARSED' | 'S2_EVIDENCE_READY'
  | 'S3_DECISION_LOCKED' | 'S4_EXECUTING' | 'S5_OUTPUT_READY'
  | 'S6_SELF_CHECKED' | 'S7_MEMORY_COMMITTED' | 'S8_DONE';

type RunState = 'idle' | 'running' | 'paused' | 'completed' | 'failed';

interface Node {
  id: string;
  type: string;
  label: string;
  status: 'idle' | 'running' | 'completed' | 'failed';
  position: { x: number; y: number };
  metadata?: Record<string, unknown>;
}

interface Edge {
  id: string;
  source: string;
  target: string;
  animated?: boolean;
}

interface UseWorkflowParams {
  sessionId?: string;
}

interface UseWorkflowReturn {
  /** 워크플로우 노드 목록 */
  nodes: Node[];
  /** 워크플로우 엣지 목록 */
  edges: Edge[];
  /** 실행 상태 */
  runState: RunState;
  /** 현재 스텝 (1-based) */
  currentStep: number;
  /** 전체 스텝 수 */
  totalSteps: number;
  /** 파이프라인 스테이지 (S0~S8) */
  pipelineStage: PipelineStage;
  /** 진행률 (0~100) */
  progress: number;
  /** 워크플로우 시작 */
  startWorkflow: (input: string) => Promise<void>;
  /** 워크플로우 중지 */
  stopWorkflow: () => Promise<void>;
  /** 로딩 상태 */
  isLoading: boolean;
  /** 에러 상태 */
  error: Error | null;
}

function useWorkflow(params?: UseWorkflowParams): UseWorkflowReturn;
```

### 3.2 내부 로직 흐름

```
초기화 (mount)
  ├─ 1. useTauriIPC() 호출 — invoke/listen 획득
  ├─ 2. workflowStore 구독 (selectNodes, selectEdges, selectRunState, selectPipelineStage)
  ├─ 3. sessionId 파라미터 있으면 기존 워크플로우 상태 복원
  │     └─ invoke('vamos:workflow:status', { session_id })
  └─ 4. EventType 리스너 등록 (7건)

구독 (active)
  ├─ ui.main.job.queued → workflowStore.updateRunState('running')
  ├─ ui.main.execution.started → workflowStore.setPipelineStage('S0_RECEIVED')
  ├─ ui.main.step.started → workflowStore.advanceStep() + 노드 활성화
  ├─ ui.main.stream.chunk → 스트리밍 출력 버퍼 갱신 (S7C-038)
  ├─ ui.main.artifact.created → 결과 아티팩트 추가
  ├─ ui.node.selected → 노드 선택 상태 갱신
  └─ ui.node.context.loaded → 노드 컨텍스트 로드

갱신
  ├─ startWorkflow: invoke('vamos:workflow:run', { session_id, input }) → runState = 'running'
  ├─ stopWorkflow: invoke('vamos:workflow:stop', { session_id }) → runState = 'paused'
  └─ pipelineStage 변경 시 → progress 자동 재계산 (useMemo)

정리 (unmount)
  ├─ 7건 EventType listener unlisten
  └─ Store 구독 해제
```

### 3.3 의존성

| 구분 | 대상 | 설명 |
|------|------|------|
| **Store** | workflowStore | 노드/엣지/실행 상태/파이프라인 스테이지 |
| **Hook** | useTauriIPC | 워크플로우 실행 IPC invoke |
| **외부** | zustand | Store 구독 |

### 3.4 구독 EventType

| EventType | 트리거 | UI 반응 |
|-----------|--------|---------|
| ui.main.job.queued | 작업 큐잉 | "요청 수신됨" 표시 |
| ui.main.execution.started | 실행 시작 | PipelineStatusBar S0 진입 |
| ui.main.step.started | 스텝 시작 | 현재 스텝 표시 갱신, "검색 중... (N/M)" |
| ui.main.stream.chunk | 스트림 청크 | 실시간 타이핑 효과 (S7C-038) |
| ui.main.artifact.created | 아티팩트 생성 | 결과 패널 추가 |
| ui.node.selected | 노드 선택 | 노드 하이라이트 |
| ui.node.context.loaded | 노드 컨텍스트 로드 | 컨텍스트 패널 갱신 |

**합계**: 7건 (ui.main.* + ui.node.*)

### 3.5 리렌더링 최적화

| 패턴 | 적용 대상 | 이유 |
|------|----------|------|
| `useCallback` | startWorkflow, stopWorkflow | 액션 함수 참조 안정성 |
| `useMemo` | progress | currentStep/totalSteps 비율 계산, 의존성: [currentStep, totalSteps] |
| shallow selector | selectRunState, selectPipelineStage | primitive 값 — shallow 충분 |
| 참조 비교 | selectNodes, selectEdges | 배열 참조 변경 시에만 리렌더 |

### 3.6 테스트 전략

```typescript
// __tests__/hooks/useWorkflow.test.ts

// T1: 정상 — 워크플로우 시작 + 파이프라인 진행
test('starts workflow and tracks pipeline stages', async () => {
  const { result } = renderHook(() => useWorkflow({ sessionId: 'sess-1' }));
  await act(async () => { await result.current.startWorkflow('test input'); });
  expect(result.current.runState).toBe('running');
  // Simulate pipeline progression
  act(() => emitEvent('ui.main.execution.started', {}));
  expect(result.current.pipelineStage).toBe('S0_RECEIVED');
  act(() => emitEvent('ui.main.step.started', { step: 1, total: 7 }));
  expect(result.current.currentStep).toBe(1);
});

// T2: 에러 — 워크플로우 실행 실패
test('handles workflow failure', async () => {
  // Mock: invoke → throw Error
  const { result } = renderHook(() => useWorkflow());
  await act(async () => { await result.current.startWorkflow('bad input'); });
  expect(result.current.error).not.toBeNull();
  expect(result.current.runState).toBe('failed');
});

// T3: 경계 — 스트리밍 중 중지
test('stops workflow mid-stream', async () => {
  const { result } = renderHook(() => useWorkflow());
  await act(async () => { await result.current.startWorkflow('input'); });
  act(() => emitEvent('ui.main.stream.chunk', { chunk: 'partial' }));
  await act(async () => { await result.current.stopWorkflow(); });
  expect(result.current.runState).toBe('paused');
});

// T4: progress 계산
test('calculates progress from step/total', () => {
  const { result } = renderHook(() => useWorkflow());
  act(() => emitEvent('ui.main.step.started', { step: 3, total: 7 }));
  expect(result.current.progress).toBeCloseTo(42.86, 1);
});
```

**모킹 대상**: useTauriIPC, workflowStore

### 3.7 STEP7-C 매핑

| S7C ID | 설명 | 매핑 |
|--------|------|------|
| S7C-038 | 스트리밍 타이핑 효과 | stream.chunk 이벤트 → 실시간 표시 |
| S7C-063 | 에이전트 실행 진행률 표시 | currentStep/totalSteps → progress |
| S7C-070 | 파이프라인 스텝 표시 | pipelineStage S0~S8 UI 매핑 |

---

## 4. useMemory

### 4.1 TypeScript 시그니처

```typescript
// frontend/src/hooks/useMemory.ts

type MemoryLayer = 'L0' | 'L1' | 'L2';
type CandidateStatus = 'pending' | 'committed' | 'discarded';

interface MemoryCandidate {
  id: string;
  content: string;
  layer: MemoryLayer;
  status: CandidateStatus;
  sourceId: string;
  qodScore: number;
  qodLevel: 'high' | 'medium' | 'low';
  createdAt: number;
}

interface UseMemoryParams {
  filter?: {
    layer?: MemoryLayer;
    status?: CandidateStatus;
  };
}

interface UseMemoryReturn {
  /** 필터링된 메모리 후보 목록 */
  candidates: MemoryCandidate[];
  /** 메모리 커밋 */
  commit: (id: string) => Promise<void>;
  /** 메모리 폐기 */
  discard: (id: string) => Promise<void>;
  /** PII 마스킹 활성 여부 */
  isMasked: boolean;
  /** 커밋 이력 */
  commitHistory: CommitRecord[];
  /** 로딩 상태 */
  isLoading: boolean;
  /** 에러 상태 */
  error: Error | null;
}

interface CommitRecord {
  candidateId: string;
  layer: MemoryLayer;
  committedAt: number;
}

function useMemory(params?: UseMemoryParams): UseMemoryReturn;
```

### 4.2 내부 로직 흐름

```
초기화 (mount)
  ├─ 1. useTauriIPC() 호출 — invoke/listen 획득
  ├─ 2. memoryStore 구독 (selectCandidates, selectIsMasking)
  ├─ 3. filter 파라미터 적용 → useMemo로 필터링
  └─ 4. EventType 리스너 등록 (5건)

구독 (active)
  ├─ ui.memory.candidate.found → memoryStore.addCandidate()
  ├─ ui.memory.masking.applied → memoryStore.setMaskingActive(true)
  ├─ ui.memory.commit.success → memoryStore.commitCandidate()
  ├─ ui.memory.commit.denied → notificationStore.enqueue(WARN)
  └─ ui.memory.source.trust_updated → 후보 qodScore 갱신

갱신
  ├─ commit: invoke('vamos:memory:save', { action: 'commit', item_id }) → Store 갱신
  ├─ discard: invoke('vamos:memory:save', { action: 'discard', item_id }) → Store 제거
  └─ filter 변경 시 → candidates 자동 재필터링 (useMemo)

정리 (unmount)
  ├─ 5건 EventType listener unlisten
  └─ Store 구독 해제
```

### 4.3 의존성

| 구분 | 대상 | 설명 |
|------|------|------|
| **Store** | memoryStore | 후보 목록 + 커밋 이력 + 마스킹 상태 |
| **Hook** | useTauriIPC | 메모리 커밋/폐기 IPC invoke |
| **외부** | zustand | Store 구독 |

### 4.4 구독 EventType

| EventType | 트리거 | UI 반응 |
|-----------|--------|---------|
| ui.memory.candidate.found | 메모리 후보 발견 | MemoryCandidatePanel에 항목 추가 |
| ui.memory.masking.applied | PII 마스킹 적용 | MaskingPreview 활성화 |
| ui.memory.commit.success | 커밋 성공 | 성공 토스트 + 이력 갱신 |
| ui.memory.commit.denied | 커밋 거부 | 경고 토스트 (권한/정책 위반) |
| ui.memory.source.trust_updated | 출처 신뢰도 갱신 | QoD 점수 바 갱신 |

**합계**: 5건 (ui.memory.* 레이어)

### 4.5 리렌더링 최적화

| 패턴 | 적용 대상 | 이유 |
|------|----------|------|
| `useCallback` | commit, discard | 액션 함수 참조 안정성 |
| `useMemo` | candidates (필터링) | filter.layer/filter.status 변경 시에만 재계산 |
| shallow selector | selectIsMasking | boolean — shallow 충분 |

### 4.6 테스트 전략

```typescript
// __tests__/hooks/useMemory.test.ts

// T1: 정상 — 후보 발견 + 커밋
test('adds candidate on event and commits', async () => {
  const { result } = renderHook(() => useMemory());
  act(() => emitEvent('ui.memory.candidate.found', { candidate: mockCandidate }));
  expect(result.current.candidates).toHaveLength(1);
  await act(async () => { await result.current.commit(mockCandidate.id); });
  expect(result.current.candidates[0].status).toBe('committed');
});

// T2: 에러 — 커밋 거부
test('handles commit denied', async () => {
  const { result } = renderHook(() => useMemory());
  act(() => emitEvent('ui.memory.candidate.found', { candidate: mockCandidate }));
  // Mock: invoke → denied
  act(() => emitEvent('ui.memory.commit.denied', { id: mockCandidate.id }));
  expect(result.current.candidates[0].status).toBe('pending'); // unchanged
});

// T3: 경계 — 레이어 필터링
test('filters candidates by layer', () => {
  const { result } = renderHook(() => useMemory({ filter: { layer: 'L0' } }));
  act(() => {
    emitEvent('ui.memory.candidate.found', { candidate: { ...mockCandidate, layer: 'L0' } });
    emitEvent('ui.memory.candidate.found', { candidate: { ...mockCandidate, id: '2', layer: 'L2' } });
  });
  expect(result.current.candidates).toHaveLength(1);
  expect(result.current.candidates[0].layer).toBe('L0');
});
```

**모킹 대상**: useTauriIPC, memoryStore

### 4.7 STEP7-C 매핑

| S7C ID | 설명 | 매핑 |
|--------|------|------|
| S7C-072 | 메모리 관리 UI | useMemory candidates/commit/discard |
| S7C-083 | QoD 신뢰도 바 | memoryStore qod_score 구독 |

---

## 5. useCost

### 5.1 TypeScript 시그니처

```typescript
// frontend/src/hooks/useCost.ts

type CostMode = 'V0' | 'V1' | 'V2' | 'V3';

interface Budget {
  sessionLimit: number;
  dailyLimit: number;
  monthlyLimit: number;
}

interface UseCostParams {
  traceId?: string;
}

interface UseCostReturn {
  /** 비용 모드 (V0~V3) */
  mode: CostMode;
  /** 예산 정보 */
  budget: Budget;
  /** 입력 토큰 수 */
  tokenIn: number;
  /** 출력 토큰 수 */
  tokenOut: number;
  /** 예상 비용 (원) */
  estCost: number;
  /** 잔여 예산 (원) */
  budgetRemaining: number;
  /** 다운시프트 실행 (저비용 모드 전환) */
  downshift: () => void;
  /** 80% 경고 상태 */
  isWarning: boolean;
  /** 100% 상한 도달 */
  isCeiling: boolean;
  /** 비용 요약 (일/주/월) */
  costSummary: { session: number; daily: number; monthly: number };
  /** 로딩 상태 */
  isLoading: boolean;
  /** 에러 상태 */
  error: Error | null;
}

function useCost(params?: UseCostParams): UseCostReturn;
```

### 5.2 내부 로직 흐름

```
초기화 (mount)
  ├─ 1. useTauriIPC() 호출 — invoke/listen 획득
  ├─ 2. costStore 구독 (selectCostMode, selectBudget, selectTokens, selectIsWarning, selectIsCeiling)
  ├─ 3. traceId 파라미터 있으면 현재 비용 상태 조회
  │     └─ invoke('vamos:cost:budget_get', { trace_id })
  └─ 4. EventType 리스너 등록 (4건)

구독 (active)
  ├─ ui.gate.cost.calculated → costStore.updateCost()
  │   └─ "이 메시지를 보내면 ~₩50 예상" 표시 (S7C-030)
  ├─ ui.gate.cost.warning → costStore 경고 상태 표시
  ├─ ui.gate.cost.warning_80 → costStore.isWarning80 = true
  │   └─ CostWarningBanner 표시, 80% 경고 배지
  └─ ui.gate.cost.ceiling_100 → costStore.isCeiling100 = true
      └─ 상한 도달 알림, 다운시프트 제안

갱신
  ├─ downshift: costStore.downshift() → invoke('vamos:cost:downshift') → 모드 전환
  └─ costSummary: useMemo([costStore.sessionCost, costStore.dailyCost, costStore.monthlyCost])

정리 (unmount)
  ├─ 4건 EventType listener unlisten
  └─ Store 구독 해제
```

### 5.3 의존성

| 구분 | 대상 | 설명 |
|------|------|------|
| **Store** | costStore | 모드/예산/토큰/경고/상한 상태 |
| **Hook** | useTauriIPC | 비용 조회/다운시프트 IPC invoke |
| **외부** | zustand | Store 구독 |

### 5.4 구독 EventType

| EventType | 트리거 | UI 반응 |
|-----------|--------|---------|
| ui.gate.cost.calculated | 비용 산출 | 비용 미리보기 표시 (S7C-030) |
| ui.gate.cost.warning | 비용 경고 일반 | 경고 배너 |
| ui.gate.cost.warning_80 | 80% 도달 | CostWarningBanner 노란색 경고 |
| ui.gate.cost.ceiling_100 | 100% 도달 | 빨간색 경고 + 다운시프트 제안 |

**합계**: 4건 (ui.gate.cost.*)

### 5.5 리렌더링 최적화

| 패턴 | 적용 대상 | 이유 |
|------|----------|------|
| `useCallback` | downshift | 액션 함수 참조 안정성 |
| `useMemo` | costSummary | sessionCost/dailyCost/monthlyCost 결합 — 변경 시에만 재계산 |
| throttle(100ms) | selectTokens | 실시간 게이지(S7C-082)용, 매 chunk마다 갱신되므로 스로틀 적용 |
| shallow selector | selectIsWarning, selectIsCeiling | boolean — shallow 충분 |

### 5.6 테스트 전략

```typescript
// __tests__/hooks/useCost.test.ts

// T1: 정상 — 비용 계산 이벤트
test('updates cost on calculated event', () => {
  const { result } = renderHook(() => useCost());
  act(() => emitEvent('ui.gate.cost.calculated', {
    token_in: 1000, token_out: 500, est_cost: 50, budget_remaining: 950
  }));
  expect(result.current.tokenIn).toBe(1000);
  expect(result.current.estCost).toBe(50);
});

// T2: 에러 — 80% 경고
test('sets warning at 80%', () => {
  const { result } = renderHook(() => useCost());
  act(() => emitEvent('ui.gate.cost.warning_80', {}));
  expect(result.current.isWarning).toBe(true);
  expect(result.current.isCeiling).toBe(false);
});

// T3: 경계 — 100% 상한 + 다운시프트
test('handles ceiling and downshift', async () => {
  const { result } = renderHook(() => useCost());
  act(() => emitEvent('ui.gate.cost.ceiling_100', {}));
  expect(result.current.isCeiling).toBe(true);
  act(() => { result.current.downshift(); });
  // Verify mode changed to lower tier
  expect(result.current.mode).not.toBe('V3');
});

// T4: costSummary 메모이제이션
test('memoizes costSummary correctly', () => {
  const { result, rerender } = renderHook(() => useCost());
  const summary1 = result.current.costSummary;
  rerender();
  expect(result.current.costSummary).toBe(summary1); // same reference
});
```

**모킹 대상**: useTauriIPC, costStore

### 5.7 STEP7-C 매핑

| S7C ID | 설명 | 매핑 |
|--------|------|------|
| S7C-030 | 비용 미리보기 | cost.calculated → estCost 표시 |
| S7C-074 | 비용 대시보드 | costSummary (일/주/월 차트) |
| S7C-082 | 비용 실시간 게이지 | tokenIn/tokenOut + throttle 구독 |

---

## 6. useNotification

### 6.1 TypeScript 시그니처

```typescript
// frontend/src/hooks/useNotification.ts

type AlertPriority = 'P0_MODAL' | 'P1_SLIDE' | 'P2_TOAST';
type NotificationSeverity = 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL' | 'SUCCESS';

interface NotificationOpts {
  title: string;
  message: string;
  severity: NotificationSeverity;
  priority?: AlertPriority;
  duration?: number;  // ms, 기본 5000. P0=무한, P1=10000, P2=5000
  action?: { label: string; onClick: () => void };
}

interface Notification {
  id: string;
  title: string;
  message: string;
  severity: NotificationSeverity;
  priority: AlertPriority;
  createdAt: number;
  read: boolean;
}

interface Toast {
  id: string;
  title: string;
  message: string;
  severity: NotificationSeverity;
  expiresAt: number;
}

interface UseNotificationReturn {
  /** 알림 표시 — ID 반환 */
  show: (opts: NotificationOpts) => string;
  /** 알림 닫기 */
  dismiss: (id: string) => void;
  /** 대기 큐 */
  queue: Notification[];
  /** 활성 토스트 목록 (최대 maxToasts) */
  activeToasts: Toast[];
  /** 읽지 않은 알림 여부 */
  hasUnread: boolean;
  /** 전체 초기화 */
  clearAll: () => void;
}

function useNotification(): UseNotificationReturn;
```

### 6.2 내부 로직 흐름

```
초기화 (mount)
  ├─ 1. notificationStore 구독 (selectQueue, selectActiveToasts, selectHasUnread)
  └─ 2. EventType 리스너 등록 (5+건 — 다중 레이어)

구독 (active)
  ├─ ui.frontmini.pii.detected → show({ severity: 'CRITICAL', priority: 'P0_MODAL' })
  │   └─ PII 감지 → 즉시 모달 (AlertModal)
  ├─ ui.frontmini.malware.found → show({ severity: 'CRITICAL', priority: 'P0_MODAL' })
  │   └─ 악성코드 감지 → 즉시 모달
  ├─ ui.gate.policy.violated → show({ severity: 'ERROR', priority: 'P1_SLIDE' })
  │   └─ 정책 위반 → 슬라이드 패널
  ├─ ui.policy.blocked → show({ severity: 'WARN', priority: 'P1_SLIDE' })
  │   └─ 정책 차단 → 슬라이드 패널
  └─ ui.gate.approval.required → show({ severity: 'WARN', priority: 'P1_SLIDE' })
      └─ 승인 필요 → 슬라이드 패널 (ApprovalSlidePanel)

갱신
  ├─ show: severity → priority 자동 결정 (CRITICAL→P0, ERROR→P1, WARN→P1, INFO→P2)
  │   └─ notificationStore.enqueue() + showToast() (P2)
  ├─ dismiss: notificationStore.dismissToast(id)
  └─ clearAll: notificationStore.clearAll()

정리 (unmount)
  ├─ EventType listener unlisten
  └─ Store 구독 해제
```

### 6.3 의존성

| 구분 | 대상 | 설명 |
|------|------|------|
| **Store** | notificationStore | 큐 + 토스트 스택 + Alert Priority 3단계 |
| **Hook** | — | 직접 Store 조작, IPC 불필요 |
| **외부** | zustand | Store 구독 |

### 6.4 구독 EventType

| EventType | 트리거 | Priority | UI 반응 |
|-----------|--------|----------|---------|
| ui.frontmini.pii.detected | PII 감지 | P0_MODAL | AlertModal 즉시 표시 |
| ui.frontmini.malware.found | 악성코드 감지 | P0_MODAL | AlertModal 즉시 표시 |
| ui.gate.policy.violated | 정책 위반 | P1_SLIDE | ApprovalSlidePanel |
| ui.policy.blocked | 정책 차단 | P1_SLIDE | ApprovalSlidePanel |
| ui.gate.approval.required | 승인 필요 | P1_SLIDE | ApprovalSlidePanel |

**합계**: 5+건 (다중 레이어: frontmini, gate, policy)

### 6.5 리렌더링 최적화

| 패턴 | 적용 대상 | 이유 |
|------|----------|------|
| `useCallback` | show, dismiss, clearAll | 액션 함수 참조 안정성 |
| `shallow` comparator | selectActiveToasts | 배열 reference 변경 빈번 → shallow 비교 |
| `useMemo` | — | 반환 값 대부분 Store에서 직접 → 별도 memoize 불필요 |

### 6.6 테스트 전략

```typescript
// __tests__/hooks/useNotification.test.ts

// T1: 정상 — PII 감지 → P0 모달
test('shows P0 modal on PII detection', () => {
  const { result } = renderHook(() => useNotification());
  act(() => emitEvent('ui.frontmini.pii.detected', { field: 'email' }));
  expect(result.current.queue).toHaveLength(1);
  expect(result.current.queue[0].priority).toBe('P0_MODAL');
  expect(result.current.queue[0].severity).toBe('CRITICAL');
});

// T2: 에러 — 토스트 최대 수 초과
test('respects maxToasts limit', () => {
  const { result } = renderHook(() => useNotification());
  // Show more than maxToasts (default 5)
  for (let i = 0; i < 8; i++) {
    act(() => { result.current.show({ title: `T${i}`, message: '', severity: 'INFO' }); });
  }
  expect(result.current.activeToasts.length).toBeLessThanOrEqual(5);
});

// T3: 경계 — dismiss + clearAll
test('dismisses and clears all notifications', () => {
  const { result } = renderHook(() => useNotification());
  const id = act(() => result.current.show({ title: 'test', message: '', severity: 'WARN' }));
  act(() => { result.current.dismiss(id); });
  expect(result.current.activeToasts).toHaveLength(0);
  // Add more then clear all
  act(() => { result.current.show({ title: 'a', message: '', severity: 'INFO' }); });
  act(() => { result.current.clearAll(); });
  expect(result.current.queue).toHaveLength(0);
});
```

**모킹 대상**: notificationStore

### 6.7 STEP7-C 매핑

| S7C ID | 설명 | 매핑 |
|--------|------|------|
| — | (직접 매핑 없음) | 다른 Hook의 에러/경고 이벤트를 수집하는 중앙 알림 허브 |

---

## 7. useAutonomy

### 7.1 TypeScript 시그니처

```typescript
// frontend/src/hooks/useAutonomy.ts

type AutonomyLevel = 0 | 1 | 2 | 3 | 4;

interface UseAutonomyReturn {
  /** 현재 자율성 레벨 (L0~L4) */
  level: AutonomyLevel;
  /** 현재 레벨에서 자동 승인 가능 여부 */
  canAutoApprove: boolean;
  /** 자율성 레벨 변경 */
  setLevel: (level: AutonomyLevel) => void;
  /** 자동 승인 범위 확인 */
  isAutoApprovable: (scope: string) => boolean;
}

function useAutonomy(): UseAutonomyReturn;
```

> Hook 이름 주석: §6.1.3 정본명 `useAutonomy` — V1-P4 L2329 `useAuth`와 불일치 (SOURCE_CONFLICT). 본 문서는 §6.1.3 정본 채택.

### 7.2 내부 로직 흐름

```
초기화 (mount)
  ├─ 1. appStore 구독 (selectAutonomyLevel)
  └─ 2. EventType 리스너 등록 (1+건)

구독 (active)
  └─ ui.gate.approval.required → approval_scope 기반 자동 승인 판단
      ├─ canAutoApprove === true + scope 일치 → 자동 승인 바이패스
      └─ canAutoApprove === false → ApprovalCard (HV-APPR-01) 표시

갱신
  ├─ setLevel: appStore.setAutonomyLevel(level)
  │   └─ canAutoApprove 자동 재계산:
  │       L0 = false (항상 수동)
  │       L1 = false (저위험만 안내)
  │       L2 = true (저위험 자동)
  │       L3 = true (중위험까지 자동)
  │       L4 = true (전체 자동, 고위험 제외)
  └─ isAutoApprovable(scope): level + scope 조합으로 자동 승인 여부 판단

정리 (unmount)
  ├─ EventType listener unlisten
  └─ Store 구독 해제
```

### 7.3 의존성

| 구분 | 대상 | 설명 |
|------|------|------|
| **Store** | appStore | 자율성 레벨 (autonomyLevel 필드) |
| **Hook** | — | 직접 Store 조작, IPC 불필요 |
| **외부** | zustand | Store 구독 |

### 7.4 구독 EventType

| EventType | 트리거 | UI 반응 |
|-----------|--------|---------|
| ui.gate.approval.required | 승인 필요 | scope 기반 자동 승인 판단 → 바이패스 또는 ApprovalCard |

**합계**: 1+건 (ui.gate.approval.*)

### 7.5 리렌더링 최적화

| 패턴 | 적용 대상 | 이유 |
|------|----------|------|
| `useCallback` | setLevel, isAutoApprovable | 액션 함수 참조 안정성 |
| `useMemo` | canAutoApprove | level 변경 시에만 재계산 |
| shallow selector | selectAutonomyLevel | number — shallow 충분 |

### 7.6 테스트 전략

```typescript
// __tests__/hooks/useAutonomy.test.ts

// T1: 정상 — 레벨 변경 + canAutoApprove 계산
test('updates canAutoApprove on level change', () => {
  const { result } = renderHook(() => useAutonomy());
  expect(result.current.level).toBe(0);
  expect(result.current.canAutoApprove).toBe(false);
  act(() => { result.current.setLevel(2); });
  expect(result.current.level).toBe(2);
  expect(result.current.canAutoApprove).toBe(true);
});

// T2: 에러/경계 — L0에서 자동 승인 불가
test('L0 never auto-approves', () => {
  const { result } = renderHook(() => useAutonomy());
  act(() => { result.current.setLevel(0); });
  expect(result.current.isAutoApprovable('low_risk')).toBe(false);
  expect(result.current.isAutoApprovable('high_risk')).toBe(false);
});

// T3: 경계 — L4에서도 고위험은 수동
test('L4 auto-approves except high risk', () => {
  const { result } = renderHook(() => useAutonomy());
  act(() => { result.current.setLevel(4); });
  expect(result.current.isAutoApprovable('low_risk')).toBe(true);
  expect(result.current.isAutoApprovable('medium_risk')).toBe(true);
  expect(result.current.isAutoApprovable('high_risk')).toBe(false);
});
```

**모킹 대상**: appStore

### 7.7 STEP7-C 매핑

| S7C ID | 설명 | 매핑 |
|--------|------|------|
| S7C-076 | 모델 설정 — 기본 모델 선택, 비용 한도 | appStore config 상태 (useAutonomy level 연동) |

---

## 8. useLog

### 8.1 TypeScript 시그니처

```typescript
// frontend/src/hooks/useLog.ts

type Severity = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR' | 'CRITICAL';

interface LogEntry {
  id: string;
  traceId: string;
  timestamp: number;
  severity: Severity;
  layer: string;       // frontmini | core | gate | node | main | tool | cli | memory
  subject: string;
  action: string;
  message: string;
  payload?: Record<string, unknown>;
}

interface UseLogParams {
  filter?: {
    traceId?: string;
    severity?: Severity[];
    layer?: string;
  };
}

interface UseLogReturn {
  /** 필터링된 로그 엔트리 목록 */
  logs: LogEntry[];
  /** 실시간 필터 변경 */
  setFilter: (opts: UseLogParams['filter']) => void;
  /** 현재 필터 기준 severity */
  severity: Severity | null;
  /** 스트리밍 중 여부 */
  isStreaming: boolean;
  /** 로그 스트림 일시정지 */
  pause: () => void;
  /** 로그 스트림 재개 */
  resume: () => void;
  /** 로그 초기화 */
  clear: () => void;
}

function useLog(params?: UseLogParams): UseLogReturn;
```

> Hook 이름 주석: §6.1.3 정본명 `useLog` — V1-P4 L2329 `useStreaming`와 불일치 (SOURCE_CONFLICT). 본 문서는 §6.1.3 정본 채택.

### 8.2 내부 로직 흐름

```
초기화 (mount)
  ├─ 1. useTauriIPC() 호출 — listen 획득
  ├─ 2. 전체 ui.*.* 이벤트 스트림 구독 시작
  │     └─ listen('ui.*', onLogEvent) — trace_id 기반 필터링
  ├─ 3. filter 파라미터 적용 (traceId, severity[], layer)
  └─ 4. isStreaming = true

구독 (active)
  ├─ 전체 ui.*.* 이벤트 수신
  │   ├─ filter.traceId 매치 확인
  │   ├─ filter.severity 포함 여부 확인
  │   ├─ filter.layer 매치 확인
  │   └─ 통과 시 logs 배열에 append
  └─ 버퍼: 최대 1000건 유지 (FIFO)

갱신
  ├─ setFilter: filter 변경 → logs 재필터링 (useMemo)
  ├─ pause: isStreaming = false → listener 일시정지
  ├─ resume: isStreaming = true → listener 재개
  └─ clear: logs = [] 초기화

정리 (unmount)
  ├─ 전체 ui.*.* listener unlisten
  └─ logs 버퍼 해제
```

### 8.3 의존성

| 구분 | 대상 | 설명 |
|------|------|------|
| **Store** | — | 직접 IPC 스트림 구독, Store 비의존 |
| **Hook** | useTauriIPC | 로그 스트림 listen 구독 |
| **외부** | @tauri-apps/api | event.listen |

### 8.4 구독 EventType

| EventType 패턴 | 범위 | 건수 |
|----------------|------|------|
| ui.frontmini.* | Front Mini 레이어 | 7 |
| ui.core.* + ui.gate.* | Core/Gate 레이어 | 16 |
| ui.node.* + ui.main.* | Node/Main 레이어 | 13 |
| ui.tool.* | Tool 레이어 | 6 |
| ui.cli.* | CLI 레이어 | 10 |
| ui.memory.* | Memory 레이어 | 5 |

**합계**: 57+건 (전체 ui.*.* — trace_id 기반 필터링)

### 8.5 리렌더링 최적화

| 패턴 | 적용 대상 | 이유 |
|------|----------|------|
| `useCallback` | setFilter, pause, resume, clear | 액션 함수 참조 안정성 |
| `useMemo` | logs (필터링) | filter 변경 시에만 재계산, 원본 버퍼는 useRef |
| `useRef` | logBuffer (원본) | 리렌더 없이 버퍼 관리, 주기적 flush(100ms)로 batch 갱신 |
| batch update | logs 상태 갱신 | 고빈도 이벤트 대응 — requestAnimationFrame 기반 batch |

### 8.6 테스트 전략

```typescript
// __tests__/hooks/useLog.test.ts

// T1: 정상 — 로그 스트림 수신 + 필터링
test('receives and filters log events by traceId', () => {
  const { result } = renderHook(() => useLog({ filter: { traceId: 'trace-1' } }));
  act(() => {
    emitEvent('ui.main.step.started', { trace_id: 'trace-1', message: 'step 1' });
    emitEvent('ui.main.step.started', { trace_id: 'trace-2', message: 'step 2' });
  });
  expect(result.current.logs).toHaveLength(1);
  expect(result.current.logs[0].traceId).toBe('trace-1');
});

// T2: 에러/경계 — severity 필터
test('filters by severity', () => {
  const { result } = renderHook(() => useLog({ filter: { severity: ['ERROR', 'CRITICAL'] } }));
  act(() => {
    emitEvent('ui.gate.cost.warning', { severity: 'WARN', trace_id: 't1' });
    emitEvent('ui.gate.policy.violated', { severity: 'ERROR', trace_id: 't1' });
  });
  expect(result.current.logs).toHaveLength(1);
  expect(result.current.logs[0].severity).toBe('ERROR');
});

// T3: 경계 — 버퍼 최대 1000건 FIFO
test('maintains max 1000 log entries', () => {
  const { result } = renderHook(() => useLog());
  act(() => {
    for (let i = 0; i < 1100; i++) {
      emitEvent('ui.main.stream.chunk', { trace_id: `t-${i}`, message: `msg-${i}` });
    }
  });
  expect(result.current.logs.length).toBeLessThanOrEqual(1000);
});

// T4: pause/resume
test('pauses and resumes log streaming', () => {
  const { result } = renderHook(() => useLog());
  expect(result.current.isStreaming).toBe(true);
  act(() => { result.current.pause(); });
  expect(result.current.isStreaming).toBe(false);
  act(() => emitEvent('ui.main.step.started', { trace_id: 't1' }));
  expect(result.current.logs).toHaveLength(0); // paused, no new logs
  act(() => { result.current.resume(); });
  expect(result.current.isStreaming).toBe(true);
});
```

**모킹 대상**: useTauriIPC (listen)

### 8.7 STEP7-C 매핑

| S7C ID | 설명 | 매핑 |
|--------|------|------|
| — | (직접 매핑 없음) | 로그 인프라 Hook — 모든 이벤트 수집/필터링 |

---

## 9. Hook 간 의존성 그래프

### 9.1 의존성 방향 (DAG)

```
                     ┌─────────────┐
                     │ useTauriIPC │  ← 최상위 (Store 비의존)
                     └──────┬──────┘
                            │
          ┌─────────┬───────┼────────┬──────────┐
          │         │       │        │          │
          ▼         ▼       ▼        ▼          ▼
    useDecision useWorkflow useMemory useCost  useLog
          │         │       │        │
          ▼         ▼       ▼        ▼
    decisionStore workflowStore memoryStore costStore

    ┌───────────────┐   ┌──────────┐
    │useNotification│   │useAutonomy│  ← Store 직접 조작 (IPC 불필요)
    └───────┬───────┘   └─────┬────┘
            ▼                 ▼
    notificationStore     appStore
```

### 9.2 순환 의존성 검증

| 검증 항목 | 결과 |
|----------|------|
| useTauriIPC → (없음) | PASS — 최상위 노드 |
| useDecision → useTauriIPC | PASS — 단방향 |
| useWorkflow → useTauriIPC | PASS — 단방향 |
| useMemory → useTauriIPC | PASS — 단방향 |
| useCost → useTauriIPC | PASS — 단방향 |
| useLog → useTauriIPC | PASS — 단방향 |
| useNotification → (없음) | PASS — Store 직접 |
| useAutonomy → (없음) | PASS — Store 직접 |
| **Hook→Hook 순환** | **없음** — 모든 경로가 useTauriIPC에서 종료 |

### 9.3 Store 간 참조 (교차 읽기)

| Store A | → Store B | 방향 | 순환 여부 |
|---------|----------|------|----------|
| decisionStore | costStore | A→B (est_cost 읽기) | 단방향 |
| workflowStore | decisionStore | A→B (isLocked 읽기) | 단방향 |
| notificationStore | costStore | A→B (warning 이벤트) | 단방향 |
| notificationStore | authStore | A→B (role 확인) | 단방향 |

**Store 순환**: 없음 — 모든 참조가 단방향

---

## 10. Hook ↔ 컴포넌트 매핑 테이블

> #5 (react_components_catalog.md)와 연계 — D2.0-08 §10.4 기반

### 10.1 전체 매핑

| Hook | Builder View (BV-*) | Hologram View (HV-*) | Common (CM-*) | CLI (CLI-*) | Dashboard/Log |
|------|---------------------|----------------------|---------------|-------------|---------------|
| **useTauriIPC** | BV-CONFIG-01 (ConfigEditorPanel) | — | — | CLI-CMD-01~04 | — |
| **useDecision** | BV-PIPE-02 (DecisionLockBanner) | HV-STATE-01 (AgentStatusIndicator), HV-STATE-02 (ProgressTracker) | — | — | — |
| **useWorkflow** | BV-PIPE-01 (PipelineStatusBar) | HV-STATE-01, HV-STATE-02 | — | — | — |
| **useMemory** | — | HV-MEM-01 (MemoryCandidatePanel), HV-MEM-02 (MaskingPreview) | — | — | — |
| **useCost** | BV-DEBUG-02 (CostMeterWidget) | HV-COST-01 (CostWarningBanner), HV-COST-02 (CostBreakdownPopover) | — | — | — |
| **useNotification** | — | — | CM-ALERT-01 (AlertModal P0), CM-ALERT-02 (ApprovalSlidePanel P1), CM-ALERT-03 (ToastNotification P2) | — | — |
| **useAutonomy** | — | HV-APPR-01 (ApprovalCard) | CM-NAV-02 (SettingsPanel) | — | — |
| **useLog** | BV-DEBUG-01 (TraceLogPanel) | — | — | — | LOG-DASH-01, LOG-DASH-02 |

### 10.2 컴포넌트별 Hook 소비 카운트

| 컴포넌트 | Hook 수 | Hook 목록 |
|---------|---------|----------|
| BV-PIPE-01 (PipelineStatusBar) | 1 | useWorkflow |
| BV-PIPE-02 (DecisionLockBanner) | 1 | useDecision |
| BV-DEBUG-01 (TraceLogPanel) | 1 | useLog |
| BV-DEBUG-02 (CostMeterWidget) | 1 | useCost |
| BV-CONFIG-01 (ConfigEditorPanel) | 1 | useTauriIPC |
| HV-STATE-01 (AgentStatusIndicator) | 2 | useDecision, useWorkflow |
| HV-STATE-02 (ProgressTracker) | 2 | useDecision, useWorkflow |
| HV-COST-01 (CostWarningBanner) | 1 | useCost |
| HV-COST-02 (CostBreakdownPopover) | 1 | useCost |
| HV-MEM-01 (MemoryCandidatePanel) | 1 | useMemory |
| HV-MEM-02 (MaskingPreview) | 1 | useMemory |
| HV-APPR-01 (ApprovalCard) | 1 | useAutonomy |
| CM-ALERT-01~03 | 1 | useNotification |
| CM-NAV-02 (SettingsPanel) | 1 | useAutonomy |
| CLI-CMD-01~04 | 1 | useTauriIPC |
| LOG-DASH-01/02 | 1 | useLog |

### 10.3 정합성 검증 (#5 연계)

| 검증 항목 | 결과 |
|----------|------|
| 모든 Hook이 1개 이상 컴포넌트에 매핑 | PASS (8/8) |
| 모든 BV-* 컴포넌트가 Hook 소비 확인 | PASS (5건) |
| 모든 HV-* 컴포넌트가 Hook 소비 확인 | PASS (7건) |
| 모든 CM-* 컴포넌트가 Hook 소비 확인 | PASS (4건) |
| react_components_catalog.md 상태 연동 필드와 일치 | PASS |

---

## 11. STEP7-C 매핑 종합

### 11.1 Hook 직접 매핑 (12건)

| S7C ID | Part | 설명 | 관련 Hook/Store | 우선순위 |
|--------|------|------|----------------|---------|
| S7C-030 | 3 | 비용 미리보기 | useCost / costStore | 🔴 |
| S7C-038 | 4 | 스트리밍 타이핑 효과 | useWorkflow (stream.chunk) | 🔴 |
| S7C-060 | 6 | 오프라인 UI 상태 | useTauriIPC → appStore.isOnline | 🟡 |
| S7C-063 | 7 | 에이전트 실행 진행률 | useWorkflow / workflowStore | 🔴 |
| S7C-069 | 7 | 3-Gate 통과 표시 | useCost + useDecision | 🔴 |
| S7C-070 | 7 | 파이프라인 스텝 표시 | workflowStore.pipelineStage | 🟡 |
| S7C-072 | 8 | 메모리 관리 UI | useMemory / memoryStore | 🟡 |
| S7C-074 | 8 | 비용 대시보드 | costStore (집계) | 🔴 |
| S7C-076 | 8 | 모델 설정 | appStore (useAutonomy level 연동) | 🟡 |
| S7C-081 | 9 | 3-Gate 상태 표시기 | costStore + decisionStore | 🔴 |
| S7C-082 | 9 | 비용 실시간 게이지 | costStore + throttle 메모이제이션 | 🔴 |
| S7C-083 | 9 | QoD 신뢰도 바 | memoryStore (qod_score) | 🔴 |

### 11.2 공유 항목 (04_react-components 참조용, 5건)

| S7C ID | Part | 설명 | 비고 |
|--------|------|------|------|
| S7C-029 | 3 | 토큰 카운터 | 컴포넌트 UI = 04, 상태 = costStore.tokens |
| S7C-040 | 5 | 3-Part 출력 UI | 컴포넌트 UI = 04, 상태 = workflowStore |
| S7C-041 | 5 | 신뢰도 표시바 | 컴포넌트 UI = 04, 상태 = memoryStore.qod |
| S7C-042 | 5 | 비용 표시 | 컴포넌트 UI = 04, 상태 = costStore |
| S7C-065 | 7 | 병렬 에이전트 상태 | 컴포넌트 UI = 04, 상태 = workflowStore |

**합계**: 🔴 8건 / 🟡 4건 = 12건(직접) + 5건(공유) = 17건 매핑 완료

---

## 12. Failure/Recovery Hook 상태 전이

> LOCK (D2.0-08 §7.6, L20): 14개 FailureCodes + 9개 FallbackRegistry

### 12.1 FailureCode → Hook 반응

| FailureCode | 관련 Hook | 반응 |
|-------------|----------|------|
| FM_ERR_FMT, FM_ERR_SIZE, FM_ERR_PII, FM_ERR_ZERO | useNotification | WARN/ERROR 토스트/모달 |
| OC_ERR_NONGOAL, OC_ERR_P2_LOCK | useDecision, useNotification | decisionStore 초기화 + ERROR 알림 |
| OC_ERR_COST_LV, OC_ERR_COST_OV | useCost, useNotification | downshift() + WARN 알림 |
| OC_ERR_NO_ROUTE | useNotification | ERROR 알림 |
| TL_ERR_TIMEOUT, TL_ERR_403, TL_ERR_PARSE | useWorkflow, useNotification | runState='failed' + 알림 |
| MC_ERR_LOW_QOD | useWorkflow, useNotification | 자동 재시도 + WARN |
| MC_ERR_CONFLICT, MC_ERR_STALE | useNotification | WARN 배지 |

### 12.2 FallbackRegistry → Hook 반응

| Fallback ID | 관련 Hook | 반응 |
|------------|----------|------|
| FB_REJECT_INPUT | useNotification | 에러 토스트 |
| FB_MASK_AND_CONFIRM | useMemory | isMasked = true |
| FB_REQ_REUPLOAD | useNotification | 안내 토스트 |
| FB_RETRY_SOFT | useWorkflow | runState='running' (재시도) |
| FB_USE_WEB_SEARCH | useWorkflow | 도구 전환 |
| FB_RETURN_RAW | useWorkflow | 원본 표시 모드 |
| FB_AUTO_REPAIR | useWorkflow, useNotification | 재실행 + 알림 |
| FB_SHOW_CONFLICT | useNotification | WARN |
| FB_SHOW_STALE | useNotification | WARN |

---

## 13. LOCK 참조 테이블

| LOCK | 항목 | 정본 출처 | 값 | 본 문서 준수 |
|------|------|---------|-----|-------------|
| L14 | Custom Hooks 수 | Part2 §6.1.3 | 8개 | MATCH — 8개 정의 |
| L1 | UI 9-State | D2.0-08 §4.1 | UI_S0~UI_S8 (9개) | MATCH — Hook 상태 전이 참조 |
| L17 | 전이 지연 | D2.0-08 §4.4 | 최대 500ms | MATCH — useTauriIPC timeout 기본값 참조 |
| L19 | 이벤트 네이밍 | D2.0-08 §5.1 | `ui.{layer}.{subject}.{action}` | MATCH — 전 Hook EventType 패턴 준수 |
| L20 | FailureCode + Fallback | D2.0-08 §7.6 | 14 + 9 | MATCH — §12 전체 매핑 |

---

## 14. 검증 체크리스트

- [x] Hook 8개가 Part2 §6.1.3 정본과 1:1 대응 (LOCK L14) — 8/8 정의 완료
- [x] 모든 Hook의 TypeScript 시그니처 정의 완료 — 8/8 Interface + Return 타입
- [x] Hook 간 순환 의존성 없음 — DAG 검증 PASS (§9.2)
- [x] Hook ↔ 컴포넌트 매핑이 #5 컴포넌트 목록과 정합 — §10.3 검증 PASS
- [x] STEP7-C Hook 관련 항목 매핑 확인 — 12건(직접) + 5건(공유) = 17건 (§11)
- [x] 리렌더링 최적화 패턴 Hook별 정의 — useMemo/useCallback/shallow/throttle
- [x] 테스트 전략 Hook별 최소 3건 — renderHook 패턴 (정상/에러/경계)
- [x] Failure/Recovery 상태 전이 전체 매핑 — 14 FailureCode + 9 Fallback (§12)
- [x] LOCK 변경 0건 — L14, L1, L17, L19, L20 모두 원본 그대로

---

## 변경 이력

| 일자 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-12 | v1.0 | P1-10 최초 작성. Custom Hooks 8개 L3 상세 명세 (TypeScript 시그니처, 내부 로직 흐름, 의존성, 반환 값 타입, 리렌더링 최적화, 테스트 전략, STEP7-C 매핑, 순환 의존성 검증, Hook↔컴포넌트 매핑, Failure/Recovery 전이) |
