# P1-05. Parallel 패턴 구현 -- Lead → 최대 3 Agent 병렬 위임 (V1)

> **도메인**: 6-3_Agent-Teams-PARL / 03_team-composition
> **세션**: P1-5
> **작성일**: 2026-04-12
> **대조 기준**: D2.0-05 §Workflow_Pattern Parallel 정의, LOCK-AT-014(병렬 V1=3)
> **선행 산출물**: P1-01_lead_agent_definition.md (P1-1), P1-02_research_agent_definition.md (P1-2), P1-03_coding_agent_definition.md (P1-3), P1-04_sequential_pattern.md (P1-4)

---

## 1. 교차 참조 블록

| 문서 | 참조 위치 | 역할 |
|------|----------|------|
| D2.0-05 Agent Workflow | §Workflow_Pattern Parallel, §7.3 | Parallel 패턴 정본 정의 |
| D2.0-02 ORANGE CORE | S3 Decision Locked | Lead Agent 단일결정 -> 병렬 결과 수집 후 최종 확정 |
| D2.0-07 Safety/Cost/Approval | S7E-080, Gate 정책 | 07 Gate 선행 통과 필수 (각 병렬 Agent별) |
| Part2 §6.7 | L4994-5130 | LOCK-AT 값 선언 정본, 패턴 구현 요건 |
| Part2 §6.7 §7.1 | enum WorkflowPattern | Parallel = 6개 패턴 중 2번째 (CFL-63-001 RESOLVED) |
| SPEC S7-A-008 | L720 | 최대 병렬 에이전트: V1=3, V2=10, V3=50+ |
| AUTHORITY_CHAIN.md | §2.1 레지스트리 | LOCK-AT 17건 레지스트리 정본 |
| 03_team-composition/_index.md | §2 협업 패턴 개요 | 폴더 수준 패턴 총괄 |
| P1-01_lead_agent_definition.md | §3 LeadAgent 클래스 | Lead Agent 위임 인터페이스(delegate, decide) — 결과 집계 전 단일결정 보장 |
| P1-02_research_agent_definition.md | §3 ResearchAgent 클래스 | Research Agent 실행 인터페이스(execute) — 병렬 실행 대상 |
| P1-03_coding_agent_definition.md | §3 CodingAgent 클래스 | Coding Agent 실행 인터페이스(execute) — 병렬 실행 대상 |
| P1-04_sequential_pattern.md | §3 SequentialPipeline 클래스 | Sequential 패턴과의 인터페이스 호환성 (PipelineStageStatus, PipelineResult 재사용) |
| 종합계획서 §7.3 | P1-5 세부 항목 | 본 세션 작업 정의 |
| 종합계획서 §4.3 R-63-12 | 거버넌스 규칙 | 병렬 상한 초과 요청은 큐잉 처리 (거부 아닌 대기) |
| 종합계획서 부록 §A.5 | 협업 패턴 상세 | Parallel 패턴 상세 명세 |
| **인접 도메인** | | |
| 3-8 Conversation-A2A | A2A 프로토콜 규격 | Parallel 위임 메시지 포맷 소비 (재정의 금지) |
| 3-10 Agent-Protocol | L0-L4 자율성 정의 | Agent 자율성 레벨 배정 참조 (재정의 금지) |
| 6-2 Security-Governance | 보안 정책, STRIDE 위협 모델 | 병렬 실행 보안 체크리스트 우선 적용 (§9.3) |

---

## 2. Parallel 패턴 개요

### 2.1 패턴 식별

| 속성 | 값 |
|------|-----|
| **패턴 ID** | `WorkflowPattern.PARALLEL` |
| **도입 버전** | V1 |
| **실행 모델** | 비동기 병렬 (`asyncio.gather` 기반) |
| **최대 동시 실행 (V1)** | 3 (LOCK-AT-014 V1=3) |
| **결과 수집** | 전체 병렬 결과를 Lead에 집계 반환 |
| **부분 실패 정책** | 1개 실패 시 나머지 결과 + 에러 요약 반환 |
| **상한 초과 정책** | R-63-12: 큐잉 처리 (거부 아닌 대기) |

### 2.2 LOCK 값 인용

> LOCK-AT-014 (Part2 §6.7 L5052 / SPEC S7-A-008 L720):
> "V1 병렬 상한=3, V2=10, V3=50+"

> LOCK-AT-002 (Part2 §6.7 L5040 / D2.0-02 §2.2 L319):
> "단일결정 원칙: 최종 결론은 Lead Agent(ORANGE CORE)만 확정"

> LOCK-AT-005 (Part2 §6.7 L5043 / D2.0-05 §7.3 고정1):
> "모든 에이전트 실행은 07 Gate 선행 통과 필수"

> LOCK-AT-007 (Part2 §6.7 L5045 / D2.0-05 §7.3 고정2):
> "Checkpoint/Replay/Fork는 trace_id 단위로만 허용"

> LOCK-AT-015 (Part2 §6.7 L5053 / SPEC S7-A-001 L118):
> "Lead Agent는 직접 실행 금지 (계획/분배/검증만 수행)"

> LOCK-AT-003 (Part2 §6.7 L5041 / D2.0-05 §7.3 L381):
> "에이전트 간 자유 상호 호출 / 무한 대화 루프 금지"

---

## 3. ParallelDispatcher 클래스 스켈레톤

### 3.1 공통 자료 구조 (§7 공통 자료 구조 선정의)

```python
from __future__ import annotations
from typing import Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import asyncio
import logging

# ---------------------------------------------------------------------------
# 공통 자료 구조 -- P1-01 공유 (AgentRole, DelegationMessage, EscalationPayload)
# ---------------------------------------------------------------------------
# 아래 구조는 P1-01_lead_agent_definition.md §3.1에서 정의된 것을 재사용.
# 여기서는 Parallel 패턴에 필요한 추가 구조만 정의.

# --- P1-01 참조: AgentRole(9종), DelegationMessage, DecisionResult,
#     EscalationPayload, TaskStatus --- (import 가정)


class ParallelTaskStatus(Enum):
    """병렬 태스크 개별 상태."""
    QUEUED = "queued"          # 큐잉 대기 (R-63-12)
    DISPATCHED = "dispatched"  # 실행 위임됨
    RUNNING = "running"        # 실행 중
    COMPLETED = "completed"    # 정상 완료
    FAILED = "failed"          # 실패
    CANCELLED = "cancelled"    # 취소 (전체 중단 시)


@dataclass
class ParallelTask:
    """병렬 실행 개별 태스크 정의.

    LOCK-AT-007: 각 태스크 완료 시 Checkpoint 저장 호환.
    LOCK-AT-005: 각 태스크 실행 전 07 Gate 선행 통과 필수.
    """
    task_id: str
    agent_role: str           # AgentRole.value (e.g., "agent.research")
    task_payload: dict[str, Any] = field(default_factory=dict)
    status: ParallelTaskStatus = ParallelTaskStatus.QUEUED
    result: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    checkpoint_id: Optional[str] = None  # LOCK-AT-007 Checkpoint ID
    gate_passed: bool = False  # LOCK-AT-005 Gate 통과 여부


@dataclass
class ParallelBatch:
    """병렬 실행 배치 정의.

    LOCK-AT-014: V1 상한=3. 상한 초과 태스크는 큐잉 (R-63-12).
    """
    batch_id: str
    trace_id: str
    tasks: list[ParallelTask] = field(default_factory=list)
    max_parallel: int = 3     # LOCK-AT-014 V1=3 (하드코딩)
    dispatched_count: int = 0
    completed_count: int = 0
    failed_count: int = 0
    queued_overflow: list[ParallelTask] = field(default_factory=list)


@dataclass
class ParallelResult:
    """병렬 실행 전체 결과.

    LOCK-AT-002: 최종 결과 확정은 Lead Agent만 수행.
    결과 집계 후 Lead Agent의 decide() 메서드로 전달.
    """
    trace_id: str
    batch_id: str
    tasks_completed: int
    tasks_failed: int
    tasks_total: int
    task_results: list[dict[str, Any]] = field(default_factory=list)
    failed_summaries: list[dict[str, Any]] = field(default_factory=list)
    timing_log: list[dict[str, Any]] = field(default_factory=list)
    is_partial_success: bool = False  # 부분 성공 (일부 실패)
    is_full_success: bool = False     # 전체 성공


@dataclass
class ParallelEscalationPayload:
    """Parallel 패턴 실패 시 에스컬레이션 페이로드.

    EscalationPayload (P1-01 §3.1)를 확장하여 병렬 실행 컨텍스트 포함.
    R-01-8 경유, Lead Agent가 처리 불가 시 사용자에게 상위 보고.
    """
    trace_id: str
    escalation_id: str
    batch_id: str
    failed_tasks: list[str]       # 실패한 태스크 ID 목록
    successful_tasks: list[str]   # 성공한 태스크 ID 목록
    reason: str
    partial_results: list[dict[str, Any]] = field(default_factory=list)
    error_context: dict[str, Any] = field(default_factory=dict)
    severity: str = "HIGH"        # HIGH | CRITICAL
```

### 3.2 예외 클래스 정의

```python
class ParallelLimitExceeded(Exception):
    """LOCK-AT-014 위반: 병렬 상한 초과 시 발생.

    V1=3, V2=10, V3=50+ 상한을 초과하는 요청에 대해 발생.
    R-63-12: 상한 초과 요청은 큐잉 처리가 원칙이므로
    이 예외는 큐잉 불가 상황 (큐 용량 초과 등)에서만 사용.
    """

    def __init__(self, requested: int, limit: int, version: str = "V1"):
        self.requested = requested
        self.limit = limit
        self.version = version
        super().__init__(
            f"LOCK-AT-014: Parallel limit exceeded — "
            f"requested={requested}, limit={limit} ({version})"
        )


class ParallelGateFailure(Exception):
    """LOCK-AT-005 위반: 병렬 태스크의 07 Gate 미통과.

    병렬 배치 내 하나 이상의 태스크가 07 Gate를 통과하지 못한 경우.
    """

    def __init__(self, task_id: str, gate_results: dict[str, bool]):
        self.task_id = task_id
        self.gate_results = gate_results
        super().__init__(
            f"LOCK-AT-005: Gate check failed for task {task_id} — "
            f"results={gate_results}"
        )
```

### 3.3 ParallelDispatcher 인터페이스 정의

```python
class ParallelDispatcher:
    """Lead Agent가 최대 3개 Agent를 병렬 위임하는 디스패처.

    LOCK-AT-014: V1 병렬 상한=3 (하드코딩).
    LOCK-AT-002: 최종 결론은 Lead Agent(ORANGE CORE)만 확정.
    LOCK-AT-005: 각 Agent 실행 전 07 Gate 선행 통과 필수.
    LOCK-AT-007: 각 태스크 완료 시 trace_id 단위 Checkpoint 저장.
    LOCK-AT-015: Lead Agent는 직접 실행 금지 (위임만).
    R-63-12: 병렬 상한 초과 요청은 큐잉 처리 (거부 아닌 대기).

    시간복잡도:
      - create_batch(): O(n) where n = number of tasks
      - dispatch(): O(max(T_i)) where T_i = i-th task execution time (병렬)
      - _collect_results(): O(n) where n = completed tasks
      - _queue_overflow(): O(k) where k = overflow tasks
      - cancel_batch(): O(n) where n = active tasks

    ABC 시그니처:
      create_batch(tasks, trace_id) -> ParallelBatch
      dispatch(batch) -> ParallelResult
      cancel_batch(batch, reason) -> ParallelResult
    """

    # LOCK-AT-014: V1=3 하드코딩. V2=10, V3=50+ 확장 시 config 교체.
    MAX_PARALLEL_V1: int = 3
    QUEUE_CAPACITY: int = 10     # 큐잉 대기 최대 용량

    def __init__(self, lead_agent: "LeadAgent",
                 gate_checker: "GateChecker",
                 trace_manager: "TraceManager",
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Args:
            lead_agent: LeadAgent 인스턴스 (P1-01).
            gate_checker: GateChecker 인스턴스 (P1-08, 04_autonomy-levels).
            trace_manager: TraceManager 인스턴스 (P1-14, 02_agent-swarm).
            logger: 로깅 인스턴스.

        세션간 인터페이스 cross-check:
          - lead_agent: P1-01 LeadAgent.delegate(), LeadAgent.decide()
          - gate_checker: P1-08 GateChecker.check_all()
          - trace_manager: P1-14 TraceManager.create_checkpoint()
        """
        self._lead = lead_agent
        self._gate_checker = gate_checker
        self._trace_manager = trace_manager
        self._logger = logger or logging.getLogger("parallel_dispatcher")
        self._active_count: int = 0
        self._overflow_queue: asyncio.Queue[ParallelTask] = asyncio.Queue(
            maxsize=self.QUEUE_CAPACITY
        )

    # ---------- 핵심 메서드 ----------

    def create_batch(self, tasks: list[dict[str, Any]],
                     trace_id: str) -> ParallelBatch:
        """병렬 실행 배치를 구성한다.

        LOCK-AT-014: V1 상한=3. 상한 초과 태스크는 큐잉 (R-63-12).

        Args:
            tasks: 태스크 정의 리스트. 각 dict에 "agent_role", "task" 키 필수.
            trace_id: 실행 추적 ID (LOCK-AT-007).

        Returns:
            ParallelBatch: 구성된 배치 (tasks + queued_overflow 분리).

        Raises:
            ValueError: 태스크 리스트가 비어 있는 경우.
            ParallelLimitExceeded: 큐잉 용량도 초과하는 경우.

        시간복잡도: O(n) where n = len(tasks)
        """
        if not tasks:
            raise ValueError("Parallel batch requires at least 1 task")

        batch_id = f"batch-{uuid.uuid4().hex[:12]}"
        batch = ParallelBatch(
            batch_id=batch_id,
            trace_id=trace_id,
            max_parallel=self.MAX_PARALLEL_V1,
        )

        for i, task_def in enumerate(tasks):
            pt = ParallelTask(
                task_id=f"ptask-{i:02d}-{uuid.uuid4().hex[:8]}",
                agent_role=task_def["agent_role"],
                task_payload=task_def.get("task", {}),
            )
            if i < self.MAX_PARALLEL_V1:
                batch.tasks.append(pt)
            else:
                # R-63-12: 상한 초과 -> 큐잉 (거부 아님)
                batch.queued_overflow.append(pt)

        if len(batch.queued_overflow) > self.QUEUE_CAPACITY:
            raise ParallelLimitExceeded(
                requested=len(tasks),
                limit=self.MAX_PARALLEL_V1 + self.QUEUE_CAPACITY,
                version="V1"
            )

        self._logger.info(
            "Parallel batch created: batch_id=%s, tasks=%d, queued=%d, "
            "trace_id=%s",
            batch_id, len(batch.tasks), len(batch.queued_overflow), trace_id,
        )
        return batch

    async def dispatch(self, batch: ParallelBatch) -> ParallelResult:
        """병렬 배치를 실행한다.

        1. 각 태스크에 대해 07 Gate 검사 (LOCK-AT-005).
        2. asyncio.gather로 병렬 실행 (최대 3개).
        3. 결과 수집 + 부분 실패 처리.
        4. 큐잉된 오버플로 태스크를 순차 처리.
        5. 타이밍 로그 기록.

        LOCK-AT-002: 최종 결과 확정은 반환 후 Lead Agent의 decide()에서 수행.
        LOCK-AT-015: Lead Agent는 이 메서드를 호출하되 직접 실행하지 않음.

        Args:
            batch: create_batch()로 생성된 ParallelBatch.

        Returns:
            ParallelResult: 전체 병렬 실행 결과.

        Raises:
            ParallelGateFailure: 태스크의 07 Gate 미통과 시.

        시간복잡도: O(max(T_i)) for parallel + O(k * max(T_j)) for queued overflow
        """
        timing_log: list[dict[str, Any]] = []
        task_results: list[dict[str, Any]] = []
        failed_summaries: list[dict[str, Any]] = []
        dispatch_start = time.monotonic()

        # --- Phase 1: Gate 검사 (LOCK-AT-005) ---
        for task in batch.tasks:
            gate_result = await self._check_gate(task)
            if not gate_result:
                raise ParallelGateFailure(
                    task_id=task.task_id,
                    gate_results={"safety": False, "cost": False, "approval": False},
                )
            task.gate_passed = True

        # --- Phase 2: 병렬 실행 (asyncio.gather) ---
        self._logger.info(
            "Dispatching %d parallel tasks: batch_id=%s, trace_id=%s",
            len(batch.tasks), batch.batch_id, batch.trace_id,
        )

        async def _execute_single(task: ParallelTask) -> dict[str, Any]:
            """단일 태스크 실행 래퍼."""
            task.status = ParallelTaskStatus.RUNNING
            task.started_at = time.monotonic()
            try:
                # Lead Agent의 delegate()를 통해 위임 (LOCK-AT-015)
                # P1-01 §3.1: delegate(target_role, task, current_depth) -> DelegationMessage
                target_role = self._resolve_role(task.agent_role)
                delegation_msg = self._lead.delegate(
                    target_role=target_role,
                    task=task.task_payload,
                    current_depth=0,  # 병렬 위임은 깊이 1 고정
                )
                delegation_msg.pattern = "parallel"  # 패턴 표기
                result = await self._execute_task(delegation_msg)
                task.status = ParallelTaskStatus.COMPLETED
                task.result = result
                task.completed_at = time.monotonic()

                # LOCK-AT-007: Checkpoint 저장
                task.checkpoint_id = await self._trace_manager.create_checkpoint(
                    trace_id=batch.trace_id,
                    stage_id=task.task_id,
                    state=result,
                )
                return {
                    "task_id": task.task_id,
                    "agent_role": task.agent_role,
                    "status": "completed",
                    "result": result,
                    "duration_ms": (task.completed_at - task.started_at) * 1000,
                }
            except Exception as e:
                task.status = ParallelTaskStatus.FAILED
                task.error = str(e)
                task.completed_at = time.monotonic()
                return {
                    "task_id": task.task_id,
                    "agent_role": task.agent_role,
                    "status": "failed",
                    "error": str(e),
                    "duration_ms": (task.completed_at - task.started_at) * 1000,
                }

        # asyncio.gather: return_exceptions=True로 부분 실패 허용
        gather_results = await asyncio.gather(
            *[_execute_single(t) for t in batch.tasks],
            return_exceptions=True,
        )

        for res in gather_results:
            if isinstance(res, Exception):
                failed_summaries.append({
                    "error_type": type(res).__name__,
                    "message": str(res),
                })
            elif isinstance(res, dict):
                if res.get("status") == "completed":
                    task_results.append(res)
                else:
                    failed_summaries.append(res)

        # --- Phase 3: 큐잉 오버플로 태스크 순차 처리 ---
        for overflow_task in batch.queued_overflow:
            gate_ok = await self._check_gate(overflow_task)
            if gate_ok:
                overflow_task.gate_passed = True
                overflow_result = await _execute_single(overflow_task)
                if overflow_result.get("status") == "completed":
                    task_results.append(overflow_result)
                else:
                    failed_summaries.append(overflow_result)
            else:
                overflow_task.status = ParallelTaskStatus.FAILED
                failed_summaries.append({
                    "task_id": overflow_task.task_id,
                    "agent_role": overflow_task.agent_role,
                    "status": "failed",
                    "error": "LOCK-AT-005: 07 Gate failed (overflow task blocked)",
                })
            else:
                overflow_task.status = ParallelTaskStatus.FAILED
                failed_summaries.append({
                    "task_id": overflow_task.task_id,
                    "agent_role": overflow_task.agent_role,
                    "status": "failed",
                    "error": "LOCK-AT-005: 07 Gate failed (overflow task blocked)",
                })

        dispatch_end = time.monotonic()

        # --- Phase 4: 타이밍 로그 ---
        timing_log.append({
            "event": "parallel_dispatch",
            "batch_id": batch.batch_id,
            "trace_id": batch.trace_id,
            "parallel_count": len(batch.tasks),
            "queued_count": len(batch.queued_overflow),
            "total_duration_ms": (dispatch_end - dispatch_start) * 1000,
            "task_timings": [
                {
                    "task_id": t.task_id,
                    "agent_role": t.agent_role,
                    "duration_ms": (
                        (t.completed_at - t.started_at) * 1000
                        if t.started_at and t.completed_at else None
                    ),
                    "status": t.status.value,
                }
                for t in batch.tasks + batch.queued_overflow
            ],
            "timestamp": time.time(),
        })

        total_tasks = len(batch.tasks) + len(batch.queued_overflow)
        completed = len(task_results)
        failed = len(failed_summaries)

        return ParallelResult(
            trace_id=batch.trace_id,
            batch_id=batch.batch_id,
            tasks_completed=completed,
            tasks_failed=failed,
            tasks_total=total_tasks,
            task_results=task_results,
            failed_summaries=failed_summaries,
            timing_log=timing_log,
            is_partial_success=(completed > 0 and failed > 0),
            is_full_success=(completed == total_tasks and failed == 0),
        )

    async def cancel_batch(self, batch: ParallelBatch,
                           reason: str) -> ParallelResult:
        """실행 중인 배치를 취소한다.

        모든 미완료 태스크를 CANCELLED로 변경하고,
        완료된 태스크 결과는 보존하여 반환한다.

        Args:
            batch: 취소할 ParallelBatch.
            reason: 취소 사유.

        Returns:
            ParallelResult: 취소 시점까지의 부분 결과.

        시간복잡도: O(n) where n = total tasks
        """
        task_results = []
        cancelled_ids = []

        for task in batch.tasks + batch.queued_overflow:
            if task.status == ParallelTaskStatus.COMPLETED:
                task_results.append({
                    "task_id": task.task_id,
                    "agent_role": task.agent_role,
                    "status": "completed",
                    "result": task.result,
                })
            else:
                task.status = ParallelTaskStatus.CANCELLED
                cancelled_ids.append(task.task_id)

        self._logger.warning(
            "Parallel batch cancelled: batch_id=%s, reason=%s, "
            "cancelled=%d, preserved=%d",
            batch.batch_id, reason, len(cancelled_ids), len(task_results),
        )

        return ParallelResult(
            trace_id=batch.trace_id,
            batch_id=batch.batch_id,
            tasks_completed=len(task_results),
            tasks_failed=0,
            tasks_total=len(batch.tasks) + len(batch.queued_overflow),
            task_results=task_results,
            failed_summaries=[{
                "event": "batch_cancelled",
                "reason": reason,
                "cancelled_task_ids": cancelled_ids,
            }],
            timing_log=[],
            is_partial_success=(len(task_results) > 0),
            is_full_success=False,
        )

    # ---------- 내부 메서드 ----------

    async def _check_gate(self, task: ParallelTask) -> bool:
        """07 Gate 검사 (LOCK-AT-005).

        Safety / Cost / Approval 3가지 조건 모두 통과 시 True.

        Args:
            task: 검사 대상 ParallelTask.

        Returns:
            bool: Gate 통과 여부.

        시간복잡도: O(1) gate token verification
        """
        try:
            gate_result = await self._gate_checker.check_all(
                agent_role=task.agent_role,
                task_payload=task.task_payload,
            )
            return gate_result.all_passed
        except Exception as e:
            self._logger.error(
                "Gate check error: task_id=%s, error=%s",
                task.task_id, str(e),
            )
            return False

    def _resolve_role(self, role_value: str) -> "AgentRole":
        """문자열 agent_role을 AgentRole enum으로 변환한다.

        시간복잡도: O(m) where m = number of AgentRole members
        """
        for member in AgentRole:  # type: ignore[attr-defined]
            if member.value == role_value:
                return member
        raise ValueError(f"Unknown agent role: {role_value}")

    async def _execute_task(self, delegation_msg: "DelegationMessage") -> dict[str, Any]:
        """위임된 태스크를 Worker Agent에서 실행한다.

        LOCK-AT-015: Lead Agent는 직접 실행하지 않음.
        실제 실행은 InMemoryMessageBus (P1-07) 경유.

        시간복잡도: O(T) where T = agent execution time
        """
        raise NotImplementedError(
            "Concrete execution via InMemoryMessageBus (02_agent-swarm/P1-07)"
        )

    def _build_escalation(self, batch: ParallelBatch,
                          reason: str,
                          partial_results: list[dict]) -> ParallelEscalationPayload:
        """병렬 실패 시 에스컬레이션 페이로드 생성.

        Args:
            batch: 실패가 발생한 ParallelBatch.
            reason: 에스컬레이션 사유.
            partial_results: 부분 결과 목록.

        Returns:
            ParallelEscalationPayload.
        """
        failed_ids = [
            t.task_id for t in batch.tasks + batch.queued_overflow
            if t.status == ParallelTaskStatus.FAILED
        ]
        success_ids = [
            t.task_id for t in batch.tasks + batch.queued_overflow
            if t.status == ParallelTaskStatus.COMPLETED
        ]

        return ParallelEscalationPayload(
            trace_id=batch.trace_id,
            escalation_id=f"esc-par-{uuid.uuid4().hex[:8]}",
            batch_id=batch.batch_id,
            failed_tasks=failed_ids,
            successful_tasks=success_ids,
            reason=reason,
            partial_results=partial_results,
            error_context={
                "total_tasks": len(batch.tasks) + len(batch.queued_overflow),
                "failed_count": len(failed_ids),
                "success_count": len(success_ids),
            },
            severity="CRITICAL" if len(failed_ids) == len(batch.tasks) else "HIGH",
        )
```

---

## 4. 로깅 중첩 JSON 구조

```json
{
  "log_schema": "parallel_dispatcher_v1",
  "events": [
    {
      "event": "batch_created",
      "batch_id": "batch-abc123def456",
      "trace_id": "trace-uuid-here",
      "parallel_count": 3,
      "queued_overflow_count": 0,
      "max_parallel": 3,
      "timestamp": "2026-04-12T15:30:00.000Z",
      "lock_ref": "LOCK-AT-014 V1=3"
    },
    {
      "event": "gate_check",
      "batch_id": "batch-abc123def456",
      "task_id": "ptask-00-abcd1234",
      "agent_role": "agent.research",
      "gate_results": {
        "safety": true,
        "cost": true,
        "approval": true,
        "all_passed": true
      },
      "lock_ref": "LOCK-AT-005",
      "timestamp": "2026-04-12T15:30:00.010Z"
    },
    {
      "event": "task_dispatched",
      "batch_id": "batch-abc123def456",
      "task_id": "ptask-00-abcd1234",
      "agent_role": "agent.research",
      "pattern": "parallel",
      "delegation": {
        "source": "agent.lead",
        "target": "agent.research",
        "owner_id": "agent.lead",
        "depth": 1
      },
      "timestamp": "2026-04-12T15:30:00.020Z"
    },
    {
      "event": "task_completed",
      "batch_id": "batch-abc123def456",
      "task_id": "ptask-00-abcd1234",
      "agent_role": "agent.research",
      "duration_ms": 150.5,
      "checkpoint_id": "cp-uuid-here",
      "lock_ref": "LOCK-AT-007",
      "timestamp": "2026-04-12T15:30:00.170Z"
    },
    {
      "event": "task_failed",
      "batch_id": "batch-abc123def456",
      "task_id": "ptask-01-efgh5678",
      "agent_role": "agent.coding",
      "error": "TimeoutError: execution exceeded 30s",
      "duration_ms": 30000.0,
      "timestamp": "2026-04-12T15:30:30.020Z"
    },
    {
      "event": "batch_result",
      "batch_id": "batch-abc123def456",
      "trace_id": "trace-uuid-here",
      "tasks_completed": 2,
      "tasks_failed": 1,
      "tasks_total": 3,
      "is_partial_success": true,
      "is_full_success": false,
      "total_duration_ms": 30005.2,
      "timestamp": "2026-04-12T15:30:30.025Z"
    },
    {
      "event": "escalation_created",
      "batch_id": "batch-abc123def456",
      "escalation_id": "esc-par-ijkl9012",
      "severity": "HIGH",
      "failed_tasks": ["ptask-01-efgh5678"],
      "successful_tasks": ["ptask-00-abcd1234", "ptask-02-mnop3456"],
      "reason": "Partial failure in parallel batch",
      "timestamp": "2026-04-12T15:30:30.030Z"
    }
  ]
}
```

---

## 5. Phase별 복구 전략

### 5.1 복구 흐름도

```
[ParallelDispatcher.dispatch()]
        |
        v
  +-- [07 Gate Check (LOCK-AT-005)] --+
  |   (per task)                       |
  | PASS                          FAIL |
  v                                    v
[asyncio.gather]              [ParallelGateFailure]
  |                                    |
  +------+------+                      v
  | T1   | T2   | T3            [Escalation to Lead]
  v      v      v
 OK    FAIL    OK
  |      |      |
  v      v      v
[Collect Results]
  |
  v
[Partial Success?]
  |         |
  YES       NO (all fail)
  |         |
  v         v
[Return    [Escalation
 partial    CRITICAL →
 to Lead]   cancel_batch()]
  |
  v
[Lead.decide()] -- LOCK-AT-002 단일결정
```

### 5.2 복구 시나리오 매트릭스

| 시나리오 | 트리거 | 복구 동작 | LOCK 참조 |
|----------|--------|----------|-----------|
| Gate 미통과 | 07 Gate check_all() 실패 | ParallelGateFailure 예외 → 해당 태스크만 차단, 나머지 진행 | LOCK-AT-005 |
| 단일 태스크 실패 | asyncio.gather 내 예외 | 실패 기록 + 나머지 결과 보존 → is_partial_success=True | - |
| 전체 실패 | 모든 태스크 예외 | cancel_batch() + CRITICAL 에스컬레이션 | LOCK-AT-002 |
| 상한 초과 | len(tasks) > MAX_PARALLEL_V1 | 초과분 큐잉 (R-63-12) → 병렬 완료 후 순차 처리 | LOCK-AT-014, R-63-12 |
| 큐잉 용량 초과 | overflow > QUEUE_CAPACITY | ParallelLimitExceeded 예외 | LOCK-AT-014 |
| Checkpoint 실패 | trace_manager 예외 | 태스크 결과는 보존, checkpoint_id=None 기록 | LOCK-AT-007 |
| 배치 취소 | 외부 cancel 요청 | 미완료 태스크 CANCELLED + 완료 결과 보존 | - |

---

## 6. 예외 처리 정책 표

| 예외 | 발생 조건 | 처리 정책 | 에스컬레이션 | LOCK |
|------|----------|----------|-------------|------|
| `ParallelLimitExceeded` | 큐잉 용량 초과 (tasks > MAX_PARALLEL + QUEUE_CAPACITY) | 즉시 거부 + 에러 반환 | YES (CRITICAL) | AT-014 |
| `ParallelGateFailure` | 07 Gate check_all() 실패 | 해당 태스크 차단 + 나머지 진행 | YES (HIGH) | AT-005 |
| `ValueError` | 빈 태스크 리스트 | 즉시 거부 | NO | - |
| `asyncio.TimeoutError` | 태스크 실행 시간 초과 | 태스크 FAILED + 타이밍 로그 기록 | YES (if all fail) | - |
| `TraceMissing` | trace_id 누락 (P1-14) | 실행 차단 | YES (HIGH) | AT-007 |
| `DelegationDepthExceeded` | 병렬 내 재위임 깊이 초과 (P1-06) | 태스크 FAILED | YES (HIGH) | AT-004 |
| `InfiniteLoopDetected` | 순환 위임 감지 (P1-13) | 즉시 차단 + 전체 배치 취소 | YES (CRITICAL) | AT-003 |

---

## 7. 세션간 인터페이스 cross-check

### 7.1 P1-01 LeadAgent 인터페이스 정합성

| P1-01 메서드 | ParallelDispatcher 사용 | 호환성 |
|-------------|----------------------|--------|
| `LeadAgent.delegate(target_role, task, current_depth)` | dispatch() 내부에서 각 태스크 위임 시 호출 | OK — delegate() 호출 후 pattern="parallel" 설정 |
| `LeadAgent.decide(results)` | dispatch() 반환 후 호출자가 Lead.decide() 호출 | OK — ParallelResult를 decide() 입력으로 전달 |
| `LeadAgent.AGENT_ID` | delegation_msg.source="agent.lead" | OK — 동일값 |
| `LeadAgent.MAX_DELEGATION_DEPTH_V1` | 병렬은 깊이 1 (Lead→Agent), 깊이 제한 미적용 | OK — 병렬 위임은 깊이 1 고정 |
| `LeadAgent._FORBIDDEN_ACTIONS` | Lead는 dispatch() 호출만, 직접 실행 안 함 | OK — LOCK-AT-015 준수 |

### 7.2 P1-04 Sequential 패턴 인터페이스 정합성

| P1-04 자료구조 | P1-05 대응 | 호환성 |
|---------------|-----------|--------|
| `PipelineStageStatus` | `ParallelTaskStatus` | 호환 — 값 체계 일치 (COMPLETED, FAILED 등) |
| `PipelineResult` | `ParallelResult` | 호환 — timing_log, is_success 필드 패턴 일치 |
| `SequentialEscalationPayload` | `ParallelEscalationPayload` | 호환 — EscalationPayload (P1-01) 확장 패턴 일치 |
| `PipelineContext.trace_id` | `ParallelBatch.trace_id` | 동일 — LOCK-AT-007 trace_id 전파 |

### 7.3 P1-08 GateChecker 인터페이스 정합성

| P1-08 메서드 | ParallelDispatcher 사용 | 호환성 |
|-------------|----------------------|--------|
| `GateChecker.check_all(agent_role, task_payload)` | _check_gate() 내부 호출 | OK — LOCK-AT-005 |
| `GateResult.all_passed` | Gate 통과 판정 기준 | OK — bool 반환 |

### 7.4 P1-14 TraceManager 인터페이스 정합성

| P1-14 메서드 | ParallelDispatcher 사용 | 호환성 |
|-------------|----------------------|--------|
| `TraceManager.create_checkpoint(trace_id, stage_id, state)` | 각 태스크 완료 시 호출 | OK — LOCK-AT-007 |

---

## 8. 알고리즘 시간복잡도 + LOCK + ABC 종합표

| 메서드 | 시간복잡도 | 관련 LOCK | ABC 시그니처 |
|--------|-----------|----------|-------------|
| `create_batch(tasks, trace_id)` | O(n) | AT-014 (상한 검증) | `create_batch(list[dict], str) -> ParallelBatch` |
| `dispatch(batch)` | O(max(T_i)) + O(k*T_j) | AT-005, AT-007, AT-014, AT-015 | `dispatch(ParallelBatch) -> ParallelResult` |
| `cancel_batch(batch, reason)` | O(n) | AT-002 | `cancel_batch(ParallelBatch, str) -> ParallelResult` |
| `_check_gate(task)` | O(1) | AT-005 | (internal) |
| `_resolve_role(role_value)` | O(m) | - | (internal) |
| `_execute_task(delegation_msg)` | O(T) | AT-015 | (internal) |
| `_build_escalation(batch, reason, results)` | O(n) | - | (internal) |

---

## 9. Phase 2 통합 테스트 계획

### 9.1 단위 테스트 (P1-5 검증)

| # | 테스트 ID | 시나리오 | 기대 결과 | LOCK |
|---|----------|---------|----------|------|
| 1 | `test_parallel_2_agents_success` | 2병렬 실행 (Research + Coding) | 전체 성공, is_full_success=True | AT-014 |
| 2 | `test_parallel_3_agents_success` | 3병렬 실행 (R + C + R) | 전체 성공, tasks_completed=3 | AT-014 |
| 3 | `test_parallel_4_agents_queued` | 4병렬 요청 | 3실행 + 1큐잉, queued_overflow=1 | AT-014, R-63-12 |
| 4 | `test_parallel_limit_exceeded` | 큐잉 용량 초과 | ParallelLimitExceeded 발생 | AT-014 |
| 5 | `test_parallel_gate_failure` | 1개 태스크 Gate 미통과 | ParallelGateFailure 발생 | AT-005 |
| 6 | `test_parallel_partial_failure` | 3병렬 중 1실패 | is_partial_success=True, tasks_failed=1 | - |
| 7 | `test_parallel_all_failure` | 3병렬 모두 실패 | 에스컬레이션 CRITICAL | AT-002 |
| 8 | `test_parallel_timing_log` | 2병렬 실행 | 타이밍 로그 task_timings 2건 | - |
| 9 | `test_parallel_checkpoint` | 2병렬 성공 | checkpoint_id 2건 생성 | AT-007 |
| 10 | `test_parallel_cancel_batch` | 실행 중 취소 | 완료 결과 보존, 미완료 CANCELLED | - |

### 9.2 Phase 2 통합 테스트

| # | 테스트 ID | 시나리오 | 기대 결과 | LOCK |
|---|----------|---------|----------|------|
| 1 | `test_p2_parallel_10_agents` | V2: 10병렬 실행 | 전체 성공, max_parallel=10 | AT-014 V2=10 |
| 2 | `test_p2_parallel_11_queued` | V2: 11병렬 요청 | 10실행 + 1큐잉 | AT-014, R-63-12 |
| 3 | `test_p2_parallel_hmac_signed` | V2: 병렬 메시지 HMAC 서명 | 모든 메시지 HMAC 검증 통과 | AT-012 |
| 4 | `test_p2_parallel_redis_bus` | V2: Redis MessageBus 경유 병렬 | 메시지 유실 0건 | - |
| 5 | `test_p2_parallel_delegation_depth3` | V2: 병렬 내 재위임 깊이 3 | 정상 통과 | AT-004 V2=3 |
| 6 | `test_p2_parallel_turn_limit_10` | V2: 병렬 태스크 P1 턴 상한 10 | 11턴에서 강제 종료 | AT-009 P1=10 |
| 7 | `test_p2_sequential_then_parallel` | Sequential + Parallel 혼합 | 파이프라인 정상 동작 | - |
| 8 | `test_p2_parallel_cost_threshold` | V2: 80% 비용 경고 | 경고 로그 발행 | AT-011 |
| 9 | `test_p2_parallel_loop_detection` | V2: 병렬 내 순환 위임 시도 | InfiniteLoopDetected + 배치 취소 | AT-003 |
| 10 | `test_p2_parallel_lead_no_execute` | V2: Lead 직접 실행 시도 | 차단 + 에러 | AT-015 |
| 11 | `test_p2_parallel_trace_propagation` | V2: 10 태스크 trace_id 전파 | 전체 trace_id 일치 | AT-007 |
| 12 | `test_p2_parallel_overflow_sequential` | V2: 오버플로 큐 순차 처리 | 큐잉 태스크 순서대로 실행 | R-63-12 |

---

## 10. 공통 자료구조 선정의 요약

| 자료구조 | 정의 위치 | 용도 | 재사용 출처 |
|---------|----------|------|-----------|
| `AgentRole` | P1-01 §3.1 | 9종 에이전트 역할 열거형 | P1-01 정의, P1-02~P1-05 재사용 |
| `DelegationMessage` | P1-01 §3.1 | Lead → Worker 위임 메시지 | P1-01 정의, P1-04/P1-05 재사용 |
| `EscalationPayload` | P1-01 §3.1 | 기본 에스컬레이션 구조 | P1-01 정의, P1-04/P1-05 확장 |
| `ParallelTaskStatus` | P1-05 §3.1 (본 문서) | 병렬 태스크 상태 | 신규 정의 |
| `ParallelTask` | P1-05 §3.1 (본 문서) | 병렬 개별 태스크 | 신규 정의 |
| `ParallelBatch` | P1-05 §3.1 (본 문서) | 병렬 배치 컨테이너 | 신규 정의 |
| `ParallelResult` | P1-05 §3.1 (본 문서) | 병렬 실행 결과 | PipelineResult (P1-04) 패턴 호환 |
| `ParallelEscalationPayload` | P1-05 §3.1 (본 문서) | 병렬 에스컬레이션 | EscalationPayload (P1-01) 확장 |

---

## 11. 이월 사항

없음. P1-5 범위 내 전체 완료.

- G1-2(Sequential/Parallel 패턴 구현) 게이트 기여: Sequential (P1-4) + Parallel (P1-5) 양쪽 완료로 G1-2 충족.

---

## 변경 이력

| 일자 | 내용 | 세션 |
|------|------|------|
| 2026-04-12 | 초기 작성 — ParallelDispatcher 클래스 스켈레톤 + 자료구조 6종 + 예외 2종 + 로깅 JSON + 복구 흐름도 + 테스트 22건 + 시간복잡도/LOCK/ABC 표 + 세션간 인터페이스 cross-check | P1-5 |

---

> **문서 끝**
> 본 문서는 P1-5 태스크 산출물이며, LOCK-AT-014(V1 병렬 상한=3)를 핵심 제약으로 구현합니다.
> LOCK-AT 항목은 본 도메인(sot 2/6-3) 내에서 절대 재정의 불가합니다.
