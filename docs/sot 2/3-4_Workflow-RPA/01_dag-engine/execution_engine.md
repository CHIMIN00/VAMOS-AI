# 워크플로우 실행 관리 엔진 — L3 상세 명세

> **N-ID**: N-006 (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 01_dag-engine
> **정본**: sot 2/3-4_Workflow-RPA/01_dag-engine/execution_engine.md

---

## 1. 개요

워크플로우 실행 엔진은 DAG 기반 워크플로우의 실행 수명 주기를 관리한다. 상태 머신 기반 실행 추적, 동시 실행 제한, 실시간 모니터링, 실행 제어(일시정지/재개/취소) 기능을 제공한다.

> LOCK (STEP7-N / LOCK-WF-05): LangGraph StateGraph 기반, 최대 동시 실행 수 = 10

> LOCK (기존 명세 §2 / LOCK-WF-09): PENDING → RUNNING → (SUCCESS | FAILED | CANCELLED | TIMEOUT)

---

## 2. 워크플로우 상태 머신 (LOCK-WF-09)

### 2.1 상태 정의

| 상태 | 설명 | 진입 조건 |
|------|------|----------|
| **PENDING** | 실행 대기 중 | 워크플로우 실행 요청 시 초기 상태 |
| **RUNNING** | 실행 중 | 실행 큐에서 슬롯 할당 시 |
| **SUCCESS** | 성공 완료 | 모든 노드 정상 완료 |
| **FAILED** | 실패 | 에러 핸들러 미복구 에러 발생 |
| **CANCELLED** | 사용자 취소 | 사용자가 실행 취소 요청 |
| **TIMEOUT** | 타임아웃 | 워크플로우 전체 타임아웃 초과 |

### 2.2 상태 전이 테이블

| 현재 상태 | 이벤트 | 다음 상태 | 조건 |
|-----------|--------|-----------|------|
| PENDING | slot_available | RUNNING | 동시 실행 수 < 10 (LOCK-WF-05) |
| PENDING | cancel_requested | CANCELLED | 사용자 취소 |
| PENDING | queue_timeout | TIMEOUT | 큐 대기 시간 초과 (기본 300초) |
| RUNNING | all_nodes_complete | SUCCESS | 모든 종료 노드 도달 |
| RUNNING | unrecoverable_error | FAILED | ErrorHandler 미처리 에러 |
| RUNNING | cancel_requested | CANCELLED | 현재 노드 완료 후 중단 |
| RUNNING | global_timeout | TIMEOUT | 워크플로우 타임아웃 초과 |
| RUNNING | pause_requested | PAUSED | 사용자 일시정지 요청 |
| PAUSED | resume_requested | RUNNING | 사용자 재개 요청 |
| PAUSED | cancel_requested | CANCELLED | 사용자 취소 |
| PAUSED | unrecoverable_error | FAILED | 일시정지 중 복구 불가 에러 (ErrorHandler 미처리) |
| PAUSED | pause_timeout | TIMEOUT | 일시정지 최대 24시간 초과 |

> **참고**: PAUSED는 RUNNING의 하위 상태로 간주. LOCK-WF-09 최종 상태는 SUCCESS/FAILED/CANCELLED/TIMEOUT 4종.

### 2.3 상태 전이 다이어그램

```
                    ┌──────────────┐
                    │   PENDING    │
                    └──────┬───────┘
                           │ slot_available
               cancel ─────┼──────── queue_timeout
               → CANCELLED │        → TIMEOUT
                           ▼
                    ┌──────────────┐
              ┌────►│   RUNNING    │◄────┐
              │     └──┬───┬───┬───┘     │
              │        │   │   │         │ resume
              │        │   │   │    ┌────┴─────┐
              │        │   │   └───►│  PAUSED   │
              │        │   │  pause └──────────┘
              │        │   │
     all_done │   error│   │ cancel / timeout
              │        │   │
              ▼        ▼   ▼
         ┌────────┐ ┌──────┐ ┌───────────┐ ┌─────────┐
         │SUCCESS │ │FAILED│ │CANCELLED  │ │TIMEOUT  │
         └────────┘ └──────┘ └───────────┘ └─────────┘
```

---

## 3. 동시 실행 제한 및 큐 관리

### 3.1 실행 큐 아키텍처

> LOCK (STEP7-N / LOCK-WF-05): 최대 동시 실행 수 = 10

```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class ExecutionQueue:
    """워크플로우 동시 실행 제한 큐 — 최대 10개 동시 실행."""

    MAX_CONCURRENT = 10              # LOCK-WF-05
    QUEUE_TIMEOUT = 300              # 큐 대기 타임아웃 (초)

    def __init__(self):
        self._semaphore = asyncio.Semaphore(self.MAX_CONCURRENT)
        self._queue: deque[ExecutionRequest] = deque()
        self._active: dict[str, ExecutionContext] = {}

    async def submit(self, request: ExecutionRequest) -> str:
        """워크플로우 실행 요청 제출 → execution_id 반환."""
        execution_id = generate_uuid_v7()
        request.execution_id = execution_id
        request.status = "PENDING"
        request.queued_at = datetime.utcnow()

        self._queue.append(request)
        asyncio.create_task(self._process(request))
        return execution_id

    async def _process(self, request: ExecutionRequest):
        """슬롯 획득 후 실행."""
        try:
            acquired = await asyncio.wait_for(
                self._semaphore.acquire(),
                timeout=self.QUEUE_TIMEOUT
            )
        except asyncio.TimeoutError:
            request.status = "TIMEOUT"
            self._queue.remove(request)
            return

        try:
            request.status = "RUNNING"
            self._active[request.execution_id] = request
            self._queue.remove(request)
            await self._execute(request)
        finally:
            self._semaphore.release()
            self._active.pop(request.execution_id, None)

    def get_queue_status(self) -> dict:
        """현재 큐 상태 조회."""
        return {
            "active_count": len(self._active),
            "max_concurrent": self.MAX_CONCURRENT,
            "queued_count": len(self._queue),
            "active_executions": list(self._active.keys()),
        }
```

### 3.2 우선순위 큐 정책

| 우선순위 | 조건 | 설명 |
|----------|------|------|
| HIGH | Manual 트리거 + 사용자 대기 중 | 사용자가 직접 실행하고 결과를 기다리는 경우 |
| NORMAL | Schedule/Event 트리거 | 자동 실행 워크플로우 |
| LOW | 백그라운드 ETL/정기 배치 | 긴급하지 않은 배치 작업 |

---

## 4. 실행 컨텍스트 및 모니터링

### 4.1 실행 컨텍스트

```typescript
interface ExecutionContext {
  execution_id: string;              // UUID v7
  workflow_id: string;
  workflow_version: number;
  status: WorkflowStatus;           // LOCK-WF-09
  trigger_type: string;             // 트리거 유형
  started_at: string;               // ISO 8601
  completed_at?: string;
  elapsed_ms: number;

  // 노드별 실행 상태
  node_states: Record<string, NodeExecutionState>;

  // 공유 변수
  variables: Record<string, any>;

  // 에러 스택
  errors: ExecutionError[];

  // 실행 히스토리 (30일 보관)
  history_retention_days: number;    // 기본 30
}

interface NodeExecutionState {
  node_id: string;
  node_type: string;
  status: "pending" | "running" | "completed" | "failed" | "skipped";
  started_at?: string;
  completed_at?: string;
  elapsed_ms?: number;
  input_data?: any;
  output_data?: any;
  error?: string;
  retry_count: number;
}
```

### 4.2 실시간 모니터링

```python
class ExecutionMonitor:
    """실행 중인 워크플로우의 실시간 상태 모니터링."""

    async def get_live_status(self, execution_id: str) -> LiveStatus:
        """실시간 진행 상태 조회."""
        ctx = await self._get_context(execution_id)
        total = len(ctx.node_states)
        completed = sum(1 for ns in ctx.node_states.values() if ns.status == "completed")
        return LiveStatus(
            execution_id=execution_id,
            status=ctx.status,
            progress=completed / total if total > 0 else 0,
            current_node=self._get_current_node(ctx),
            elapsed_ms=ctx.elapsed_ms,
            node_states=ctx.node_states,
        )

    async def get_node_detail(self, execution_id: str, node_id: str) -> NodeExecutionState:
        """특정 노드의 실행 상세 (입출력 데이터, 에러 로그, 실행 시간)."""
        ctx = await self._get_context(execution_id)
        return ctx.node_states[node_id]

    async def get_execution_log(self, execution_id: str) -> list[LogEntry]:
        """실행 로그 + 스택 트레이스 조회."""
        return await self._log_store.query(execution_id=execution_id)
```

---

## 5. 실행 제어

### 5.1 제어 API

```python
class ExecutionController:
    """워크플로우 실행 제어 — 일시정지/재개/취소/재실행."""

    async def pause(self, execution_id: str) -> bool:
        """실행 일시정지 — 현재 노드 완료 후 정지."""
        ctx = await self._get_context(execution_id)
        if ctx.status != "RUNNING":
            raise InvalidStateError(f"RUNNING 상태에서만 일시정지 가능 (현재: {ctx.status})")
        ctx.status = "PAUSED"
        await self._save_context(ctx)
        return True

    async def resume(self, execution_id: str) -> bool:
        """일시정지 해제 — 다음 노드부터 재개."""
        ctx = await self._get_context(execution_id)
        if ctx.status != "PAUSED":
            raise InvalidStateError(f"PAUSED 상태에서만 재개 가능 (현재: {ctx.status})")
        ctx.status = "RUNNING"
        await self._save_context(ctx)
        await self._resume_execution(ctx)
        return True

    async def cancel(self, execution_id: str) -> bool:
        """실행 취소 — 현재 노드 완료 후 중단, 상태 CANCELLED로 전이."""
        ctx = await self._get_context(execution_id)
        if ctx.status not in ("RUNNING", "PAUSED", "PENDING"):
            raise InvalidStateError(f"취소 불가 상태: {ctx.status}")
        ctx.status = "CANCELLED"
        ctx.completed_at = datetime.utcnow().isoformat()
        await self._save_context(ctx)
        return True

    async def retry_from_node(self, execution_id: str, node_id: str) -> str:
        """특정 노드부터 재실행 — 새 execution_id 생성."""
        original_ctx = await self._get_context(execution_id)
        # 해당 노드 이전까지의 결과 보존, 이후 노드 초기화
        new_ctx = self._clone_context_until(original_ctx, node_id)
        new_ctx.execution_id = generate_uuid_v7()
        new_ctx.status = "PENDING"
        await self._save_context(new_ctx)
        await self._queue.submit(new_ctx)
        return new_ctx.execution_id
```

---

## 6. 실행 히스토리

### 6.1 히스토리 스키마

```typescript
interface ExecutionHistory {
  execution_id: string;
  workflow_id: string;
  workflow_version: number;
  status: WorkflowStatus;
  trigger_type: string;
  started_at: string;
  completed_at: string;
  elapsed_ms: number;
  node_count: number;
  error_count: number;
  // 30일 보관 (STEP7-N N-006)
  expires_at: string;
}
```

### 6.2 히스토리 조회 API

```python
class ExecutionHistoryStore:
    RETENTION_DAYS = 30

    async def list_executions(
        self,
        workflow_id: str,
        status_filter: list[str] | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ExecutionHistory]:
        """워크플로우별 실행 히스토리 조회 (최근 30일)."""
        ...

    async def get_statistics(self, workflow_id: str) -> ExecutionStats:
        """실행 통계 — 성공률, 평균 실행 시간, 에러 빈도."""
        return ExecutionStats(
            total_executions=...,
            success_rate=...,
            avg_elapsed_ms=...,
            error_distribution=...,   # {error_type: count}
        )

    async def cleanup_expired(self):
        """30일 경과 히스토리 자동 삭제."""
        cutoff = datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
        await self._store.delete_before(cutoff)
```

---

## 변경 이력

| 버전 | 날짜 | 변경 내용 |
|------|------|----------|
| L3 v1.0 | 2026-04-09 | Phase 1 1-1 — 상태 머신 전이 테이블, 동시 실행 큐, 모니터링, 실행 제어 API |
