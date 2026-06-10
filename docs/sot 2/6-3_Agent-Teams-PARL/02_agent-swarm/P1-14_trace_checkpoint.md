# P1-14. trace_id 단위 Checkpoint -- TraceManager 클래스 및 Checkpoint 저장/복원 검증

> **도메인**: 6-3_Agent-Teams-PARL / 02_agent-swarm
> **세션**: P1-14
> **작성일**: 2026-04-13
> **대조 기준**: Part2 §6.7 추적성 요건, D2.0-05 §7.3 고정2 (Checkpoint/Replay/Fork는 trace_id 단위로만), LOCK-AT-007(Checkpoint/Replay/Fork)
> **선행 산출물**: P1-01_lead_agent_definition.md (P1-1), P1-04_sequential_pattern.md (P1-4), P1-05_parallel_pattern.md (P1-5), P1-06_delegation_chain.md (P1-6), P1-07_in_memory_messagebus.md (P1-7), P1-09_execute_tool_restriction.md (P1-9), P1-10_turn_limit.md (P1-10), P1-11_tee_max_iteration.md (P1-11), P1-12_cost_limit.md (P1-12), P1-13_infinite_loop_prevention.md (P1-13)

---

## 1. 교차 참조 블록

| 문서 | 참조 위치 | 역할 |
|------|----------|------|
| D2.0-05 Agent Workflow | §7.3 고정2 L375 | LOCK-AT-007 근거 정본 -- "Checkpoint/Replay/Fork(재현/분기)는 'VAMOS trace_id 단위'로만 허용한다." |
| D2.0-05 Agent Workflow | §7.3 고정1 L371-372 | 07 Gate 선행 통과 필수 (LOCK-AT-005) -- trace_id 발급은 07 Gate 통과 후 |
| D2.0-02 ORANGE CORE | §2.2 S3 Decision Locked | Lead Agent 단일결정 원칙 -- Checkpoint/Replay 결과 확정은 Lead만 수행 (LOCK-AT-002) |
| Part2 §6.7 | L5045 (LOCK-AT-007) | LOCK 값 선언 정본: "Checkpoint/Replay/Fork는 trace_id 단위로만" |
| Part2 §6.7 | L4994-5130 | 구현 요건 정본 (17 LOCK-AT) |
| Part2 §6.7 | L5040 (LOCK-AT-002) | 단일결정 원칙: Checkpoint 복원 후 재개 결정은 Lead만 수행 |
| Part2 §6.7 | L5041 (LOCK-AT-003) | 무한 루프 금지 -- Checkpoint 복원 시 순환 방지 검증 필수 |
| Part2 §6.7 | L5044 (LOCK-AT-006) | Execute 단계에서만 도구 호출 -- Checkpoint 저장/복원은 Execute 단계 완료 후 |
| Part2 §1.3 | R8 | trace_id 서버 생성 전용 (UUID v4). 클라이언트 전달 금지 |
| AUTHORITY_CHAIN.md | §2.1 레지스트리 L60 | LOCK-AT-007 레지스트리 정본: "Checkpoint/Replay/Fork는 trace_id 단위로만 허용", 주 구현: 02 |
| AUTHORITY_CHAIN.md | §2.2 근거 문서 원문 인용 L83 | D2.0-05 §7.3 고정2 L375: "Checkpoint/Replay/Fork(재현/분기)는 'VAMOS trace_id 단위'로만 허용한다." |
| AUTHORITY_CHAIN.md | §2.3 위반 시나리오 L107 | "trace_id 없는 Checkpoint -> Checkpoint API 입력 검증 -> Checkpoint 거부" |
| 종합계획서 §7.3 | P1-14 세부 항목 | 본 세션 작업 정의 |
| 종합계획서 §3 | LOCK-AT-007 | "Checkpoint/Replay/Fork -- Part2 §6.7 -- trace_id 단위로만" |
| 종합계획서 §8.2 | 02_agent-swarm 파일 역할 | execution_engine.md -> AT-003, AT-006, AT-007, AT-010 (Checkpoint/Replay/Fork 포함) |
| 종합계획서 부록 §C.1 | LOCK-AT-007 위반 시나리오 | "trace_id 없는 Checkpoint -> Checkpoint API 입력 검증 -> Checkpoint 거부" |
| 종합계획서 부록 §C.2 | LOCK-AT 서브폴더 매핑 | AT-007 주 구현: 02_agent-swarm (주구현 매핑 = 02) |
| 종합계획서 부록 §A.7 | 위임 체인 규칙 | trace_id 전파: 위임 체인 전체에 걸쳐 trace_id 전파 필수 |
| P1-01_lead_agent_definition.md | §3 LeadAgent 클래스 | Lead Agent가 Checkpoint 복원 후 재개 결정 확정 (LOCK-AT-002) |
| P1-06_delegation_chain.md | §3 DelegationChain 클래스 | trace_id 전파: 위임 간선마다 동일 trace_id 전파 -- TraceManager가 발급한 trace_id 사용 |
| P1-07_in_memory_messagebus.md | §3 InMemoryMessageBus | 메시지 전달 시 trace_id 포함 -- TraceManager가 발급한 trace_id 사용 |
| P1-10_turn_limit.md | §3 ConversationTracker | trace_id 기반 턴 카운터 -- TraceManager Checkpoint에 턴 상태 포함 |
| P1-11_tee_max_iteration.md | §3 TEELoop | trace_id 기반 반복 카운터 -- TraceManager Checkpoint에 TEE 상태 포함 |
| P1-12_cost_limit.md | §3 CostTracker | trace_id 기반 비용 추적 -- TraceManager Checkpoint에 비용 상태 포함 |
| P1-13_infinite_loop_prevention.md | §3 LoopDetector | trace_id 기반 순환 그래프 -- TraceManager Checkpoint에 LoopDetector 상태 포함 |
| **인접 도메인** | | |
| 3-8 Conversation-A2A | A2A 프로토콜 규격 | Agent 간 메시지 프로토콜 소비 (재정의 금지) |
| 3-10 Agent-Protocol | L0-L4 자율성 정의 | Agent 자율성 레벨 배정 참조 (재정의 금지) |
| 6-2 Security-Governance | 보안 정책 | trace_id 노출 방지 보안 체크리스트 우선 적용 (§9.3) |

---

## 2. trace_id Checkpoint 개요

### 2.1 모듈 식별

| 속성 | 값 |
|------|-----|
| **모듈 ID** | `TraceManager` |
| **도입 버전** | V1 |
| **적용 범위** | 모든 Agent 실행에 대해 trace_id 발급, 전파, Checkpoint 저장/복원, Replay/Fork 관리 |
| **trace_id 형식** | UUID v4 (Part2 §1.3 R8: 서버 생성 전용, 클라이언트 전달 금지) |
| **Checkpoint 저장소** | V1: In-Memory dict (Phase 2에서 Redis/Persistent 확장) |
| **Checkpoint 시점** | 각 Agent 단계(Step) 완료 시 자동 저장 |
| **복원 시점** | trace_id로 마지막 Checkpoint 조회하여 해당 단계부터 재개 |
| **Replay** | 기존 trace_id의 Checkpoint 체인을 순서대로 재실행 |
| **Fork** | 기존 trace_id의 특정 Checkpoint에서 새 trace_id로 분기 |
| **LOCK 근거** | LOCK-AT-007 (Checkpoint/Replay/Fork는 trace_id 단위로만) |
| **trace_id 전파** | 모든 위임(DelegationChain P1-06), 메시지(MessageBus P1-07), 턴(ConversationTracker P1-10), TEE 반복(TEELoop P1-11), 비용(CostTracker P1-12), 순환 감지(LoopDetector P1-13)에 trace_id 전파 필수 |
| **trace_id 누락 시** | `TraceMissing` 예외 즉시 발생 -- Checkpoint 거부 (AUTHORITY_CHAIN.md §2.3) |
| **Lead 결정 원칙** | LOCK-AT-002: Checkpoint 복원 후 재개/폐기 결정은 Lead Agent만 수행 |

### 2.2 LOCK 값 인용

> LOCK-AT-007 (Part2 §6.7 L5045 / D2.0-05 §7.3 고정2 L375):
> "Checkpoint/Replay/Fork(재현/분기)는 'VAMOS trace_id 단위'로만 허용한다."

> LOCK-AT-002 (Part2 §6.7 L5040 / D2.0-02 §2.2 S3):
> "단일결정 원칙: 최종 결론은 Lead Agent(ORANGE CORE)만 확정"

> LOCK-AT-005 (Part2 §6.7 L5043 / D2.0-05 §7.3 고정1 L371-372):
> "모든 에이전트 실행은 07 Gate 선행 통과 필수"

> LOCK-AT-006 (Part2 §6.7 L5044 / D2.0-05 §7.3 고정3(b) L383):
> "Execute 단계에서만 도구 호출 수행"

> LOCK-AT-003 (Part2 §6.7 L5041 / D2.0-03 §1.4 L76):
> "에이전트 간 자유 상호 호출 / 무한 대화 루프 금지"

> Part2 §1.3 R8:
> "trace_id 서버 생성 전용 (UUID v4). 클라이언트 전달 금지"

### 2.3 Checkpoint/Replay/Fork 동작 모델

```
Checkpoint/Replay/Fork 동작:

1. trace_id 발급:
   - TraceManager.create_trace() -- UUID v4 생성 (서버 전용, R8)
   - 07 Gate 통과 후에만 trace_id 발급 (LOCK-AT-005)
   - 발급된 trace_id는 해당 실행의 모든 하위 위임/메시지에 전파

2. Checkpoint 저장:
   - TraceManager.save_checkpoint(trace_id, step_id, state) 
   - 각 Agent 단계 완료 시 호출
   - state: 해당 시점의 전체 실행 상태 스냅샷
   - In-Memory dict: {trace_id: [CheckpointRecord, ...]}
   - 순서 보장: step_sequence 단조증가

3. Checkpoint 복원:
   - TraceManager.restore_checkpoint(trace_id, step_id=None)
   - step_id 지정 시 해당 단계의 Checkpoint 복원
   - step_id 미지정 시 마지막 Checkpoint 복원
   - 복원 후 재개 결정은 Lead Agent만 수행 (LOCK-AT-002)

4. Replay:
   - TraceManager.replay_trace(trace_id)
   - 기존 Checkpoint 체인을 순서대로 재실행
   - 동일 trace_id 내에서만 허용 (LOCK-AT-007)

5. Fork:
   - TraceManager.fork_trace(source_trace_id, fork_step_id)
   - 기존 trace의 특정 Checkpoint에서 새 trace_id로 분기
   - 원본 trace는 불변 유지
   - 새 trace_id 발급하여 분기점 이후 독립 실행

적용 규칙:
- trace_id 없이 Checkpoint/Replay/Fork 시도 시 TraceMissing 예외 즉시 발생
- 모든 Checkpoint 조작은 trace_id 단위로만 수행 (LOCK-AT-007)
- Checkpoint 저장은 Execute 단계 완료 후에만 (LOCK-AT-006 연계)
- 복원 후 순환 방지 재검증 필수 (LOCK-AT-003 / P1-13 LoopDetector 연동)
```

### 2.4 trace_id 전파 아키텍처

```
trace_id 전파 경로:

[TraceManager] -- create_trace() --> trace_id (UUID v4)
       |
       +-- [07 Gate 통과 확인] (LOCK-AT-005)
       |
       v
[Lead Agent (P1-01)] -- plan() 호출 시 trace_id 전파
       |
       +-- [DelegationChain (P1-06)] -- delegate() 호출 시 trace_id 전파
       |       |
       |       +-- [SequentialPipeline (P1-04)] -- execute() 시 trace_id 전파
       |       +-- [ParallelDispatcher (P1-05)] -- dispatch() 시 trace_id 전파
       |
       +-- [InMemoryMessageBus (P1-07)] -- publish() 메시지에 trace_id 포함
       |
       +-- [PhaseGuard (P1-09)] -- check_tool_call() 시 trace_id 로깅
       |
       +-- [ConversationTracker (P1-10)] -- increment_turn() 시 trace_id 기반 추적
       |
       +-- [TEELoop (P1-11)] -- start_iteration() 시 trace_id 기반 추적
       |
       +-- [CostTracker (P1-12)] -- record_cost() 시 trace_id 기반 비용 추적
       |
       +-- [LoopDetector (P1-13)] -- record_edge() 시 trace_id 기반 순환 그래프
       |
       +-- [TraceManager (본 세션)] -- save_checkpoint() 시 trace_id 단위 상태 저장

전파 규칙:
- 모든 하위 호출에 trace_id 파라미터 전달 필수
- trace_id 누락 시 TraceMissing 예외 (LOCK-AT-007 위반)
- trace_id는 서버 생성 전용, 클라이언트 전달 금지 (R8)
```

---

## 3. TraceManager 클래스 스켈레톤

### 3.1 공통 자료 구조 (§7 공통 자료 구조 선정의)

```python
from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import copy
import logging
import json

# ---------------------------------------------------------------------------
# 공통 자료 구조 -- P1-01 공유 (AgentRole, EscalationPayload)
# P1-06 공유 (DelegationChain, DelegationNode)
# P1-10 공유 (ConversationTracker, ConversationSnapshot)
# P1-11 공유 (TEELoop, TEELoopSnapshot)
# P1-12 공유 (CostTracker, CostSnapshot)
# P1-13 공유 (LoopDetector, LoopDetectionSnapshot, DelegationEdge)
# ---------------------------------------------------------------------------
# 여기서는 TraceManager에 필요한 추가 구조만 정의.

# --- P1-01 참조: AgentRole(9종), EscalationPayload, TaskStatus --- (import 가정)
# --- P1-06 참조: DelegationChain, DelegationNode --- (import 가정)
# --- P1-10 참조: ConversationTracker, ConversationSnapshot --- (import 가정)
# --- P1-11 참조: TEELoop, TEELoopSnapshot --- (import 가정)
# --- P1-12 참조: CostTracker, CostSnapshot --- (import 가정)
# --- P1-13 참조: LoopDetector, LoopDetectionSnapshot, DelegationEdge --- (import 가정)


class CheckpointStatus(Enum):
    """Checkpoint 상태 분류.

    LOCK-AT-007: Checkpoint/Replay/Fork는 trace_id 단위로만.
    """
    SAVED = "saved"                # 정상 저장 완료
    RESTORED = "restored"          # 정상 복원 완료
    FORKED = "forked"              # Fork로 새 trace 생성
    REPLAYING = "replaying"        # Replay 진행 중
    INVALIDATED = "invalidated"    # 무효화 (순환 감지 등)


class TraceStatus(Enum):
    """실행 추적 상태.

    trace_id 기반 전체 실행 라이프사이클 관리.
    """
    ACTIVE = "active"              # 실행 중
    COMPLETED = "completed"        # 정상 완료
    FAILED = "failed"              # 실패 종료
    SUSPENDED = "suspended"        # 일시 정지 (Checkpoint 복원 대기)
    FORKED = "forked"              # Fork 원본 (불변)


@dataclass
class CheckpointRecord:
    """단일 Checkpoint 레코드.

    trace_id 단위 상태 스냅샷 한 건.
    LOCK-AT-007: 모든 Checkpoint는 trace_id 기반.
    """
    trace_id: str                          # 실행 추적 ID (LOCK-AT-007)
    checkpoint_id: str                     # 고유 Checkpoint ID
    step_id: str                           # Agent 단계 식별자
    step_sequence: int                     # 단계 순서 (단조증가)
    agent_id: str                          # 해당 단계 실행 Agent
    state: dict[str, Any]                  # 해당 시점 전체 상태 스냅샷
    status: CheckpointStatus = CheckpointStatus.SAVED
    parent_checkpoint_id: Optional[str] = None  # Fork 시 부모 Checkpoint
    created_at: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceRecord:
    """trace_id 단위 실행 추적 레코드.

    하나의 trace_id에 대한 전체 실행 정보.
    """
    trace_id: str                          # UUID v4 (R8: 서버 생성 전용)
    status: TraceStatus = TraceStatus.ACTIVE
    checkpoints: list[CheckpointRecord] = field(default_factory=list)
    fork_source: Optional[str] = None      # Fork 시 원본 trace_id
    fork_step_id: Optional[str] = None     # Fork 시점의 step_id
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    total_steps: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckpointSnapshot:
    """Checkpoint 조회 시 반환되는 스냅샷.

    복원 또는 Replay 시 사용.
    """
    trace_id: str
    checkpoint_id: str
    step_id: str
    step_sequence: int
    agent_id: str
    state: dict[str, Any]
    status: CheckpointStatus
    total_checkpoints_in_trace: int
    is_latest: bool
    created_at: float


@dataclass
class TraceEscalationPayload:
    """trace_id 관련 에스컬레이션 페이로드.

    EscalationPayload (P1-01 §3.1)를 확장하여 trace 컨텍스트 포함.
    Lead Agent에 전달하여 복원/폐기 결정에 사용.
    """
    trace_id: str
    escalation_id: str
    task_id: str
    checkpoint_id: str                     # 문제 발생 Checkpoint
    reason: str
    last_checkpoint: Optional[CheckpointSnapshot] = None
    trace_status: str = ""                 # TraceStatus.value
    error_context: dict[str, Any] = field(default_factory=dict)
    severity: str = "HIGH"
    created_at: float = field(default_factory=time.time)
```

### 3.2 예외 클래스 정의

```python
class TraceMissing(Exception):
    """LOCK-AT-007 위반: trace_id 없이 Checkpoint/Replay/Fork 시도.

    종합계획서 부록 §C.1: "trace_id 없는 Checkpoint -> Checkpoint API 입력 검증 -> Checkpoint 거부"
    AUTHORITY_CHAIN.md §2.3: 위반 시나리오 = trace_id 없는 Checkpoint, 자동 대응 = Checkpoint 거부.
    """

    def __init__(self, operation: str, context: str = ""):
        self.operation = operation
        self.context = context
        super().__init__(
            f"LOCK-AT-007: trace_id missing — "
            f"operation={operation} rejected. "
            f"Checkpoint/Replay/Fork requires valid trace_id. "
            f"{context}"
        )


class CheckpointNotFound(Exception):
    """지정된 Checkpoint를 찾을 수 없음.

    trace_id는 유효하지만 해당 step_id 또는 checkpoint_id의 Checkpoint가 없음.
    """

    def __init__(self, trace_id: str, identifier: str):
        self.trace_id = trace_id
        self.identifier = identifier
        super().__init__(
            f"Checkpoint not found — "
            f"trace_id={trace_id}, identifier={identifier}. "
            f"No checkpoint matches the given criteria."
        )


class TraceAlreadyCompleted(Exception):
    """이미 완료된 trace에 대해 Checkpoint 저장/복원 시도.

    완료된 trace는 불변 (COMPLETED/FORKED 상태에서는 수정 불가).
    """

    def __init__(self, trace_id: str, status: str):
        self.trace_id = trace_id
        self.status = status
        super().__init__(
            f"Trace already completed — "
            f"trace_id={trace_id}, status={status}. "
            f"Cannot modify completed/forked trace."
        )
```

### 3.3 TraceManager 인터페이스 정의

```python
class TraceManager:
    """trace_id 단위 Checkpoint/Replay/Fork 관리자.

    LOCK-AT-007: Checkpoint/Replay/Fork(재현/분기)는 'VAMOS trace_id 단위'로만 허용한다.
    LOCK-AT-002: Checkpoint 복원 후 재개/폐기 결정은 Lead Agent(ORANGE CORE)만 수행.
    LOCK-AT-005: 07 Gate 선행 통과 필수 -- trace_id 발급은 Gate 통과 후.
    LOCK-AT-006: Execute 단계 완료 후 Checkpoint 저장.

    시간복잡도:
      - create_trace(): O(1) 상수 시간 (UUID 생성 + dict 삽입)
      - save_checkpoint(): O(1) 상수 시간 (리스트 append + dict 삽입)
      - restore_checkpoint(): O(n) where n = checkpoints in trace (선형 탐색)
      - get_latest_checkpoint(): O(1) 상수 시간 (리스트 마지막 요소)
      - get_checkpoint_chain(): O(n) where n = checkpoints in trace (전체 복사)
      - replay_trace(): O(n) where n = checkpoints in trace (순차 재실행)
      - fork_trace(): O(k) where k = checkpoints up to fork_step (부분 복사)
      - complete_trace(): O(1) 상수 시간 (상태 전환)
      - get_trace_status(): O(1) 상수 시간 (dict 조회)
      - build_escalation_payload(): O(1) 상수 시간 (스냅샷 생성)
      - validate_trace_id(): O(1) 상수 시간 (존재 여부 확인)

    ABC 시그니처:
      create_trace(task_id, metadata) -> str
      save_checkpoint(trace_id, step_id, agent_id, state) -> CheckpointRecord
      restore_checkpoint(trace_id, step_id) -> CheckpointSnapshot
      get_latest_checkpoint(trace_id) -> CheckpointSnapshot
      get_checkpoint_chain(trace_id) -> list[CheckpointSnapshot]
      replay_trace(trace_id) -> list[CheckpointSnapshot]
      fork_trace(source_trace_id, fork_step_id) -> str
      complete_trace(trace_id, status) -> TraceRecord
      get_trace_status(trace_id) -> TraceStatus
      build_escalation_payload(trace_id, reason, task_id) -> TraceEscalationPayload
      validate_trace_id(trace_id) -> bool
    """

    def __init__(self,
                 logger: Optional[logging.Logger] = None) -> None:
        """TraceManager 초기화.

        Args:
            logger: 로깅 인스턴스.

        세션간 인터페이스 cross-check:
          - P1-01: LeadAgent -- Checkpoint 복원 후 재개/폐기 결정 위임 (LOCK-AT-002)
          - P1-04: SequentialPipeline -- 파이프라인 각 단계 완료 시 save_checkpoint() 호출
          - P1-05: ParallelDispatcher -- 병렬 실행 전후 Checkpoint 저장 (배치 단위)
          - P1-06: DelegationChain -- 위임 체인 각 단계에서 trace_id 전파 + Checkpoint
          - P1-07: InMemoryMessageBus -- 메시지에 trace_id 포함 (발급된 trace_id 사용)
          - P1-09: PhaseGuard -- Execute 단계 확인 후 Checkpoint 저장 허용 (LOCK-AT-006)
          - P1-10: ConversationTracker -- trace_id 기반 턴 추적, Checkpoint에 턴 상태 포함
          - P1-11: TEELoop -- trace_id 기반 반복 추적, Checkpoint에 TEE 상태 포함
          - P1-12: CostTracker -- trace_id 기반 비용 추적, Checkpoint에 비용 상태 포함
          - P1-13: LoopDetector -- trace_id 기반 순환 그래프, Checkpoint 복원 시 순환 재검증
        """
        # trace 저장소: trace_id -> TraceRecord
        self._traces: dict[str, TraceRecord] = {}
        # checkpoint 인덱스: checkpoint_id -> (trace_id, index)
        self._checkpoint_index: dict[str, tuple[str, int]] = {}
        # step sequence 카운터: trace_id -> int (단조증가)
        self._sequence_counters: dict[str, int] = {}
        self._logger = logger or logging.getLogger("trace_manager")

    # ---------- trace_id 발급 ----------

    def create_trace(self, task_id: str,
                     metadata: Optional[dict[str, Any]] = None) -> str:
        """새 trace_id를 발급한다.

        UUID v4 기반 (Part2 §1.3 R8: 서버 생성 전용).
        07 Gate 통과 후에만 호출 (LOCK-AT-005).

        Args:
            task_id: 연관 태스크 ID.
            metadata: 추가 메타데이터.

        Returns:
            str: 새로 생성된 trace_id.

        시간복잡도: O(1)
        """
        trace_id = f"trace-{uuid.uuid4().hex}"
        record = TraceRecord(
            trace_id=trace_id,
            metadata={"task_id": task_id, **(metadata or {})},
        )
        self._traces[trace_id] = record
        self._sequence_counters[trace_id] = 0

        self._logger.info(json.dumps({
            "event": "trace_manager.trace_created",
            "trace_id": trace_id,
            "task_id": task_id,
            "status": TraceStatus.ACTIVE.value,
            "metadata": metadata or {},
        }))
        return trace_id

    # ---------- Checkpoint 저장 ----------

    def save_checkpoint(self, trace_id: str, step_id: str,
                        agent_id: str, state: dict[str, Any]
                        ) -> CheckpointRecord:
        """Checkpoint를 저장한다.

        LOCK-AT-007: trace_id 단위로만 허용.
        LOCK-AT-006 연계: Execute 단계 완료 후 호출.

        Args:
            trace_id: 실행 추적 ID.
            step_id: Agent 단계 식별자.
            agent_id: 해당 단계 실행 Agent ID.
            state: 해당 시점 전체 상태 스냅샷 (deep copy 저장).

        Returns:
            CheckpointRecord: 저장된 Checkpoint.

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.
            CheckpointNotFound: trace_id가 등록되지 않음.
            TraceAlreadyCompleted: 이미 완료된 trace.

        시간복잡도: O(1)
        """
        # trace_id 검증 (LOCK-AT-007)
        if not trace_id:
            self._logger.error(json.dumps({
                "event": "trace_manager.checkpoint_rejected",
                "reason": "trace_id_missing",
                "step_id": step_id,
                "agent_id": agent_id,
                "violation": {
                    "lock_id": "LOCK-AT-007",
                    "description": "Checkpoint requires valid trace_id",
                },
            }))
            raise TraceMissing(
                operation="save_checkpoint",
                context=f"step_id={step_id}, agent_id={agent_id}",
            )

        if trace_id not in self._traces:
            raise CheckpointNotFound(trace_id, step_id)

        trace = self._traces[trace_id]
        if trace.status in (TraceStatus.COMPLETED, TraceStatus.FORKED):
            raise TraceAlreadyCompleted(trace_id, trace.status.value)

        # 순서 카운터 증가
        self._sequence_counters[trace_id] += 1
        seq = self._sequence_counters[trace_id]

        checkpoint = CheckpointRecord(
            trace_id=trace_id,
            checkpoint_id=f"cp-{uuid.uuid4().hex[:12]}",
            step_id=step_id,
            step_sequence=seq,
            agent_id=agent_id,
            state=copy.deepcopy(state),  # 불변성 보장
            status=CheckpointStatus.SAVED,
        )

        trace.checkpoints.append(checkpoint)
        trace.total_steps = seq
        self._checkpoint_index[checkpoint.checkpoint_id] = (
            trace_id, len(trace.checkpoints) - 1
        )

        self._logger.info(json.dumps({
            "event": "trace_manager.checkpoint_saved",
            "trace_id": trace_id,
            "checkpoint_id": checkpoint.checkpoint_id,
            "step_id": step_id,
            "step_sequence": seq,
            "agent_id": agent_id,
            "total_checkpoints": len(trace.checkpoints),
        }))
        return checkpoint

    # ---------- Checkpoint 복원 ----------

    def restore_checkpoint(self, trace_id: str,
                           step_id: Optional[str] = None
                           ) -> CheckpointSnapshot:
        """Checkpoint를 복원한다.

        LOCK-AT-007: trace_id 단위로만 허용.
        LOCK-AT-002: 복원 후 재개/폐기 결정은 Lead Agent만 수행.

        Args:
            trace_id: 실행 추적 ID.
            step_id: 특정 단계 식별자. None이면 마지막 Checkpoint.

        Returns:
            CheckpointSnapshot: 복원된 Checkpoint 스냅샷.

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.
            CheckpointNotFound: 해당 Checkpoint 없음.

        시간복잡도: O(n) where n = checkpoints in trace
        """
        if not trace_id:
            self._logger.error(json.dumps({
                "event": "trace_manager.restore_rejected",
                "reason": "trace_id_missing",
                "step_id": step_id,
                "violation": {
                    "lock_id": "LOCK-AT-007",
                    "description": "Restore requires valid trace_id",
                },
            }))
            raise TraceMissing(
                operation="restore_checkpoint",
                context=f"step_id={step_id}",
            )

        if trace_id not in self._traces:
            raise CheckpointNotFound(trace_id, step_id or "latest")

        trace = self._traces[trace_id]
        if not trace.checkpoints:
            raise CheckpointNotFound(trace_id, step_id or "latest")

        target: Optional[CheckpointRecord] = None
        if step_id is None:
            # 마지막 Checkpoint
            target = trace.checkpoints[-1]
        else:
            # step_id로 검색
            for cp in trace.checkpoints:
                if cp.step_id == step_id:
                    target = cp
                    break
            if target is None:
                raise CheckpointNotFound(trace_id, step_id)

        is_latest = (target == trace.checkpoints[-1])
        target.status = CheckpointStatus.RESTORED

        # trace 상태를 SUSPENDED로 전환 (복원 대기)
        trace.status = TraceStatus.SUSPENDED

        snapshot = CheckpointSnapshot(
            trace_id=target.trace_id,
            checkpoint_id=target.checkpoint_id,
            step_id=target.step_id,
            step_sequence=target.step_sequence,
            agent_id=target.agent_id,
            state=copy.deepcopy(target.state),
            status=CheckpointStatus.RESTORED,
            total_checkpoints_in_trace=len(trace.checkpoints),
            is_latest=is_latest,
            created_at=target.created_at,
        )

        self._logger.info(json.dumps({
            "event": "trace_manager.checkpoint_restored",
            "trace_id": trace_id,
            "checkpoint_id": target.checkpoint_id,
            "step_id": target.step_id,
            "step_sequence": target.step_sequence,
            "is_latest": is_latest,
            "trace_status": TraceStatus.SUSPENDED.value,
        }))
        return snapshot

    # ---------- 최신 Checkpoint 조회 ----------

    def get_latest_checkpoint(self, trace_id: str) -> CheckpointSnapshot:
        """trace_id의 마지막 Checkpoint를 조회한다.

        Args:
            trace_id: 실행 추적 ID.

        Returns:
            CheckpointSnapshot: 마지막 Checkpoint 스냅샷.

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.
            CheckpointNotFound: Checkpoint 없음.

        시간복잡도: O(1)
        """
        if not trace_id:
            raise TraceMissing(operation="get_latest_checkpoint")

        if trace_id not in self._traces:
            raise CheckpointNotFound(trace_id, "latest")

        trace = self._traces[trace_id]
        if not trace.checkpoints:
            raise CheckpointNotFound(trace_id, "latest")

        cp = trace.checkpoints[-1]
        return CheckpointSnapshot(
            trace_id=cp.trace_id,
            checkpoint_id=cp.checkpoint_id,
            step_id=cp.step_id,
            step_sequence=cp.step_sequence,
            agent_id=cp.agent_id,
            state=copy.deepcopy(cp.state),
            status=cp.status,
            total_checkpoints_in_trace=len(trace.checkpoints),
            is_latest=True,
            created_at=cp.created_at,
        )

    # ---------- Checkpoint 체인 조회 ----------

    def get_checkpoint_chain(self, trace_id: str) -> list[CheckpointSnapshot]:
        """trace_id의 전체 Checkpoint 체인을 반환한다.

        Replay 전 Checkpoint 이력 확인 용도.

        Args:
            trace_id: 실행 추적 ID.

        Returns:
            list[CheckpointSnapshot]: Checkpoint 스냅샷 목록 (시간순).

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.
            CheckpointNotFound: trace_id 미등록.

        시간복잡도: O(n) where n = checkpoints in trace
        """
        if not trace_id:
            raise TraceMissing(operation="get_checkpoint_chain")

        if trace_id not in self._traces:
            raise CheckpointNotFound(trace_id, "chain")

        trace = self._traces[trace_id]
        total = len(trace.checkpoints)
        return [
            CheckpointSnapshot(
                trace_id=cp.trace_id,
                checkpoint_id=cp.checkpoint_id,
                step_id=cp.step_id,
                step_sequence=cp.step_sequence,
                agent_id=cp.agent_id,
                state=copy.deepcopy(cp.state),
                status=cp.status,
                total_checkpoints_in_trace=total,
                is_latest=(i == total - 1),
                created_at=cp.created_at,
            )
            for i, cp in enumerate(trace.checkpoints)
        ]

    # ---------- Replay ----------

    def replay_trace(self, trace_id: str) -> list[CheckpointSnapshot]:
        """trace_id의 Checkpoint 체인을 순서대로 Replay한다.

        LOCK-AT-007: 동일 trace_id 내에서만 Replay 허용.
        Replay는 기존 Checkpoint를 읽기 전용으로 순회하여 상태를 재현.

        Args:
            trace_id: Replay 대상 추적 ID.

        Returns:
            list[CheckpointSnapshot]: Replay된 Checkpoint 스냅샷 목록.

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.
            CheckpointNotFound: trace_id 미등록 또는 Checkpoint 없음.

        시간복잡도: O(n) where n = checkpoints in trace
        """
        if not trace_id:
            self._logger.error(json.dumps({
                "event": "trace_manager.replay_rejected",
                "reason": "trace_id_missing",
                "violation": {
                    "lock_id": "LOCK-AT-007",
                    "description": "Replay requires valid trace_id",
                },
            }))
            raise TraceMissing(operation="replay_trace")

        if trace_id not in self._traces:
            raise CheckpointNotFound(trace_id, "replay")

        trace = self._traces[trace_id]
        if not trace.checkpoints:
            raise CheckpointNotFound(trace_id, "replay")

        replay_snapshots: list[CheckpointSnapshot] = []
        total = len(trace.checkpoints)

        for i, cp in enumerate(trace.checkpoints):
            snapshot = CheckpointSnapshot(
                trace_id=cp.trace_id,
                checkpoint_id=cp.checkpoint_id,
                step_id=cp.step_id,
                step_sequence=cp.step_sequence,
                agent_id=cp.agent_id,
                state=copy.deepcopy(cp.state),
                status=CheckpointStatus.REPLAYING,
                total_checkpoints_in_trace=total,
                is_latest=(i == total - 1),
                created_at=cp.created_at,
            )
            replay_snapshots.append(snapshot)

        self._logger.info(json.dumps({
            "event": "trace_manager.trace_replayed",
            "trace_id": trace_id,
            "total_checkpoints": total,
            "replay_status": "completed",
        }))
        return replay_snapshots

    # ---------- Fork ----------

    def fork_trace(self, source_trace_id: str,
                   fork_step_id: str) -> str:
        """기존 trace의 특정 Checkpoint에서 새 trace로 분기한다.

        LOCK-AT-007: Checkpoint/Replay/Fork는 trace_id 단위로만.
        원본 trace는 불변 유지 (FORKED 상태 전환).
        새 trace_id를 발급하여 분기점 이후 독립 실행.

        Args:
            source_trace_id: 원본 trace_id.
            fork_step_id: 분기 시점의 step_id.

        Returns:
            str: 새로 생성된 fork trace_id.

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.
            CheckpointNotFound: 원본 trace 또는 fork_step_id의 Checkpoint 없음.

        시간복잡도: O(k) where k = checkpoints up to fork_step
        """
        if not source_trace_id:
            self._logger.error(json.dumps({
                "event": "trace_manager.fork_rejected",
                "reason": "trace_id_missing",
                "violation": {
                    "lock_id": "LOCK-AT-007",
                    "description": "Fork requires valid trace_id",
                },
            }))
            raise TraceMissing(
                operation="fork_trace",
                context=f"fork_step_id={fork_step_id}",
            )

        if source_trace_id not in self._traces:
            raise CheckpointNotFound(source_trace_id, fork_step_id)

        source = self._traces[source_trace_id]

        # fork_step_id까지의 Checkpoint 복사
        fork_checkpoints: list[CheckpointRecord] = []
        found = False
        for cp in source.checkpoints:
            fork_checkpoints.append(CheckpointRecord(
                trace_id="",  # 새 trace_id로 교체 예정
                checkpoint_id=f"cp-{uuid.uuid4().hex[:12]}",
                step_id=cp.step_id,
                step_sequence=cp.step_sequence,
                agent_id=cp.agent_id,
                state=copy.deepcopy(cp.state),
                status=CheckpointStatus.FORKED,
                parent_checkpoint_id=cp.checkpoint_id,
                metadata=copy.deepcopy(cp.metadata),
            ))
            if cp.step_id == fork_step_id:
                found = True
                break

        if not found:
            raise CheckpointNotFound(source_trace_id, fork_step_id)

        # 새 trace 생성
        new_trace_id = f"trace-{uuid.uuid4().hex}"
        for fcp in fork_checkpoints:
            fcp.trace_id = new_trace_id

        new_trace = TraceRecord(
            trace_id=new_trace_id,
            status=TraceStatus.ACTIVE,
            checkpoints=fork_checkpoints,
            fork_source=source_trace_id,
            fork_step_id=fork_step_id,
            total_steps=fork_checkpoints[-1].step_sequence if fork_checkpoints else 0,
        )
        self._traces[new_trace_id] = new_trace
        self._sequence_counters[new_trace_id] = new_trace.total_steps

        # 원본 trace 상태 업데이트 (분기 정보 기록, 불변 유지)
        # 원본이 ACTIVE인 경우만 FORKED로 전환하지 않음 (원본 실행 계속 가능)
        # 원본 metadata에 fork 기록만 추가
        source.metadata.setdefault("forks", []).append({
            "fork_trace_id": new_trace_id,
            "fork_step_id": fork_step_id,
            "forked_at": time.time(),
        })

        # 새 trace의 checkpoint index 등록
        for i, fcp in enumerate(fork_checkpoints):
            self._checkpoint_index[fcp.checkpoint_id] = (new_trace_id, i)

        self._logger.info(json.dumps({
            "event": "trace_manager.trace_forked",
            "source_trace_id": source_trace_id,
            "new_trace_id": new_trace_id,
            "fork_step_id": fork_step_id,
            "copied_checkpoints": len(fork_checkpoints),
        }))
        return new_trace_id

    # ---------- trace 완료 ----------

    def complete_trace(self, trace_id: str,
                       status: TraceStatus = TraceStatus.COMPLETED
                       ) -> TraceRecord:
        """trace를 완료 상태로 전환한다.

        Args:
            trace_id: 실행 추적 ID.
            status: 완료 상태 (COMPLETED 또는 FAILED).

        Returns:
            TraceRecord: 완료된 TraceRecord.

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.
            CheckpointNotFound: trace_id 미등록.

        시간복잡도: O(1)
        """
        if not trace_id:
            raise TraceMissing(operation="complete_trace")

        if trace_id not in self._traces:
            raise CheckpointNotFound(trace_id, "complete")

        trace = self._traces[trace_id]
        trace.status = status
        trace.completed_at = time.time()

        self._logger.info(json.dumps({
            "event": "trace_manager.trace_completed",
            "trace_id": trace_id,
            "status": status.value,
            "total_steps": trace.total_steps,
            "total_checkpoints": len(trace.checkpoints),
        }))
        return trace

    # ---------- trace 상태 조회 ----------

    def get_trace_status(self, trace_id: str) -> TraceStatus:
        """trace의 현재 상태를 조회한다.

        Args:
            trace_id: 실행 추적 ID.

        Returns:
            TraceStatus: 현재 상태.

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.
            CheckpointNotFound: trace_id 미등록.

        시간복잡도: O(1)
        """
        if not trace_id:
            raise TraceMissing(operation="get_trace_status")

        if trace_id not in self._traces:
            raise CheckpointNotFound(trace_id, "status")

        return self._traces[trace_id].status

    # ---------- 에스컬레이션 페이로드 ----------

    def build_escalation_payload(self, trace_id: str, reason: str,
                                  task_id: str
                                  ) -> TraceEscalationPayload:
        """trace 관련 에스컬레이션 페이로드를 생성한다.

        Lead Agent에 전달하여 Checkpoint 복원/폐기 결정에 사용.
        LOCK-AT-002: 최종 결론은 Lead Agent(ORANGE CORE)만 확정.

        Args:
            trace_id: 실행 추적 ID.
            reason: 에스컬레이션 사유.
            task_id: 연관 태스크 ID.

        Returns:
            TraceEscalationPayload: 에스컬레이션 페이로드.

        시간복잡도: O(1)
        """
        last_cp: Optional[CheckpointSnapshot] = None
        trace_status = ""
        checkpoint_id = ""

        if trace_id and trace_id in self._traces:
            trace = self._traces[trace_id]
            trace_status = trace.status.value
            if trace.checkpoints:
                cp = trace.checkpoints[-1]
                checkpoint_id = cp.checkpoint_id
                last_cp = CheckpointSnapshot(
                    trace_id=cp.trace_id,
                    checkpoint_id=cp.checkpoint_id,
                    step_id=cp.step_id,
                    step_sequence=cp.step_sequence,
                    agent_id=cp.agent_id,
                    state=copy.deepcopy(cp.state),
                    status=cp.status,
                    total_checkpoints_in_trace=len(trace.checkpoints),
                    is_latest=True,
                    created_at=cp.created_at,
                )

        return TraceEscalationPayload(
            trace_id=trace_id or "",
            escalation_id=f"esc-trace-{uuid.uuid4().hex[:8]}",
            task_id=task_id,
            checkpoint_id=checkpoint_id,
            reason=reason,
            last_checkpoint=last_cp,
            trace_status=trace_status,
            error_context={"operation": "escalation", "trace_id": trace_id},
        )

    # ---------- trace_id 검증 ----------

    def validate_trace_id(self, trace_id: str) -> bool:
        """trace_id의 유효성을 확인한다.

        LOCK-AT-007: trace_id 없이 Checkpoint/Replay/Fork 불가.

        Args:
            trace_id: 검증 대상 trace_id.

        Returns:
            True이면 유효한 trace_id (등록됨).
            False이면 미등록.

        Raises:
            TraceMissing: trace_id가 None이거나 빈 문자열.

        시간복잡도: O(1)
        """
        if not trace_id:
            raise TraceMissing(
                operation="validate_trace_id",
                context="trace_id is None or empty",
            )
        return trace_id in self._traces
```

---

## 4. Phase별 복구 전략

### 4.1 복구 흐름도

```
Checkpoint/trace_id 관련 장애 발생 시:

[TraceMissing / CheckpointNotFound / TraceAlreadyCompleted 예외 발생]
        |
        v
+------------------------------------------------+
| Phase 0: 즉시 거부                               |
|  - trace_id 없이 Checkpoint 시도: 즉시 거부       |
|  - TraceMissing 예외 + 에러 로그 발행             |
|  - 해당 작업 중단, 새 trace_id 발급 후 재시작 유도 |
|  - Checkpoint 없는 실행은 복원 불가 (결과 폐기)    |
+----------------------------+---------------------+
                             | Phase 1+
                             v
+------------------------------------------------+
| Phase 1: Checkpoint 기반 복구                     |
|  - 마지막 정상 Checkpoint 조회 (get_latest_checkpoint) |
|  - Lead Agent에 에스컬레이션 (build_escalation_payload) |
|  - Lead가 복원 결정 시: restore_checkpoint() 호출  |
|  - 복원 후 LoopDetector(P1-13) 순환 재검증 필수   |
|  - CostTracker(P1-12) 잔여 예산 확인              |
|  - ConversationTracker(P1-10) 잔여 턴 확인        |
|  - 예산/턴 잔여 시: 복원 시점부터 재개             |
|  - 예산/턴 소진 시: trace 완료 (FAILED) 처리       |
+----------------------------+---------------------+
                             | Phase 2+
                             v
+------------------------------------------------+
| Phase 2: Fork 기반 분기 복구                      |
|  - Supervisor Agent가 장애 분석 후 복구 전략 결정   |
|  - fork_trace()로 장애 발생 이전 Checkpoint에서 분기 |
|  - 새 trace_id로 독립 실행 (원본 trace 보존)       |
|  - 장애 원인 Agent 격리 후 대체 Agent로 재위임      |
|  - replay_trace()로 장애 재현 분석 가능             |
|  - 3회 이상 동일 Checkpoint에서 실패 시 태스크 폐기 |
+------------------------------------------------+
```

### 4.2 복구 판단 매트릭스

| 상황 | Phase 0 | Phase 1 | Phase 2 |
|------|---------|---------|---------|
| trace_id 누락 (TraceMissing) | 즉시 거부, 에러 로그 | 새 trace 발급 후 처음부터 재실행 | Supervisor가 trace 발급 정책 점검 |
| Checkpoint 미존재 | 복구 불가, 결과 폐기 | 새 trace로 재실행 | Supervisor가 Checkpoint 정책 강화 |
| Checkpoint 복원 실패 | 에러 로그 + 폐기 | 이전 Checkpoint로 롤백 시도 | Fork로 분기 후 대체 경로 |
| 복원 후 순환 감지 (AT-003) | 즉시 차단 | 순환 원인 Agent 제외 후 복원 | Supervisor가 경로 재설계 |
| 복원 후 비용 상한 도달 (AT-011) | 비용 차단 우선 | 비용 차단 우선 | 비용 차단 우선 |
| 완료된 trace 수정 시도 | TraceAlreadyCompleted 발생 | Fork로 새 trace 생성 | Supervisor가 Fork 승인 |
| Fork 원본 Checkpoint 손상 | Fork 불가 + 에러 | 원본 이전 Checkpoint에서 Fork | 원본 Replay로 손상 지점 파악 |

---

## 5. 에스컬레이션 페이로드 상세

### 5.1 에스컬레이션 흐름

```
[TraceManager -- 장애/예외 발생]
        |
        v
[TraceMissing / CheckpointNotFound 예외 포착]
        |
        +- build_escalation_payload() 호출
        |
        v
[TraceEscalationPayload 생성]
        |
        +- trace_id: 실행 추적 ID (또는 빈 문자열)
        +- checkpoint_id: 문제 발생 Checkpoint
        +- last_checkpoint: 마지막 정상 Checkpoint 스냅샷
        +- trace_status: 현재 trace 상태
        +- reason: 에스컬레이션 사유
        |
        v
[InMemoryMessageBus (P1-07) -- 에스컬레이션 메시지 전달]
        |
        v
[Lead Agent (P1-01) -- decide()]
        |
        +- LOCK-AT-002: 복원/폐기 결정 확정
        +- 복원 결정 시: restore_checkpoint() 호출
        +- 폐기 결정 시: complete_trace(FAILED) 호출
        +- Fork 결정 시: fork_trace() 호출
        |
        v
[결과: 복원 후 재개 / trace 폐기 / Fork 후 재실행]
```

### 5.2 로깅 중첩 JSON -- trace_id 누락 거부 로그

```json
{
  "event": "trace_manager.checkpoint_rejected",
  "timestamp": "2026-04-13T14:00:00.000Z",
  "severity": "ERROR",
  "reason": "trace_id_missing",
  "step_id": "step-research-001",
  "agent_id": "research-001",
  "violation": {
    "lock_id": "LOCK-AT-007",
    "description": "Checkpoint requires valid trace_id",
    "authority_chain_ref": "§2.3 -- trace_id 없는 Checkpoint -> Checkpoint 거부"
  },
  "action": "rejected"
}
```

### 5.3 로깅 중첩 JSON -- Checkpoint 저장 성공 로그

```json
{
  "event": "trace_manager.checkpoint_saved",
  "timestamp": "2026-04-13T14:05:00.000Z",
  "severity": "INFO",
  "trace_id": "trace-a1b2c3d4e5f6",
  "checkpoint_id": "cp-abc123def456",
  "step_id": "step-research-002",
  "step_sequence": 3,
  "agent_id": "research-001",
  "total_checkpoints": 3,
  "state_keys": ["delegation_chain", "turn_count", "cost_record", "tee_iteration"],
  "metadata": {
    "lock_refs": ["LOCK-AT-007"],
    "phase": "P1"
  }
}
```

### 5.4 로깅 중첩 JSON -- Checkpoint 복원 로그

```json
{
  "event": "trace_manager.checkpoint_restored",
  "timestamp": "2026-04-13T14:10:00.000Z",
  "severity": "INFO",
  "trace_id": "trace-a1b2c3d4e5f6",
  "checkpoint_id": "cp-abc123def456",
  "step_id": "step-research-002",
  "step_sequence": 3,
  "is_latest": true,
  "trace_status": "suspended",
  "restoration": {
    "lock_refs": ["LOCK-AT-007", "LOCK-AT-002"],
    "next_action": "lead_agent_decision_pending",
    "post_restore_checks": [
      "loop_detector_revalidation",
      "cost_tracker_budget_check",
      "conversation_tracker_turn_check"
    ]
  }
}
```

### 5.5 로깅 중첩 JSON -- trace Fork 로그

```json
{
  "event": "trace_manager.trace_forked",
  "timestamp": "2026-04-13T14:15:00.000Z",
  "severity": "INFO",
  "source_trace_id": "trace-a1b2c3d4e5f6",
  "new_trace_id": "trace-f7e8d9c0b1a2",
  "fork_step_id": "step-research-002",
  "copied_checkpoints": 3,
  "fork_context": {
    "lock_refs": ["LOCK-AT-007"],
    "reason": "agent_failure_recovery",
    "original_total_checkpoints": 5,
    "fork_point_sequence": 3
  }
}
```

---

## 6. 예외 처리 정책 표

| # | 예외 유형 | LOCK 근거 | 트리거 조건 | 자동 대응 | 에스컬레이션 경로 | 심각도 |
|---|----------|----------|-----------|----------|----------------|:------:|
| E-1 | `TraceMissing` | LOCK-AT-007 | trace_id가 None/빈 문자열일 때 save_checkpoint/restore_checkpoint/replay_trace/fork_trace/validate_trace_id 호출 | Checkpoint/Replay/Fork 거부 + 에러 로그 | Lead Agent -> 새 trace 발급 판단 | HIGH |
| E-2 | `CheckpointNotFound` | LOCK-AT-007 | 유효한 trace_id이지만 해당 step_id/checkpoint_id의 Checkpoint 미존재, 또는 trace_id 자체가 미등록 | 요청 실패 반환 + 경고 로그 | Lead Agent -> 이전 Checkpoint 사용 또는 재실행 판단 | MEDIUM |
| E-3 | `TraceAlreadyCompleted` | -- | COMPLETED/FORKED 상태의 trace에 save_checkpoint 시도 | 저장 거부 + 에러 로그 | Lead Agent -> Fork로 새 trace 생성 판단 | MEDIUM |
| E-4 | 복원 후 순환 감지 | LOCK-AT-003, AT-007 | Checkpoint 복원 후 LoopDetector(P1-13)에서 순환 탐지 | InfiniteLoopDetected 우선 발생 + Checkpoint 무효화 | Lead Agent -> 순환 원인 Agent 제외 후 재복원 | CRITICAL |
| E-5 | 복원 후 비용 상한 도달 | LOCK-AT-011, AT-007 | Checkpoint 복원 시점에서 CostTracker 예산 소진 | 비용 차단 우선 (AT-011) + trace FAILED 처리 | Lead Agent -> 비용 + Checkpoint 양쪽 에스컬레이션 | CRITICAL |
| E-6 | 복원 후 턴 상한 도달 | LOCK-AT-009, AT-007 | Checkpoint 복원 시점에서 ConversationTracker 턴 소진 | 턴 상한 차단 + trace FAILED 처리 | Lead Agent -> 턴 + Checkpoint 양쪽 에스컬레이션 | HIGH |
| E-7 | Fork 원본 손상 | LOCK-AT-007 | fork_step_id의 Checkpoint가 원본 trace에 없음 | CheckpointNotFound + 에러 로그 | Lead Agent -> 이전 step에서 Fork 시도 | MEDIUM |

---

## 7. Phase 2 테스트 케이스

### 7.1 통합 테스트 시나리오 (15건)

| # | 테스트 ID | 시나리오 | 기대 결과 | 검증 LOCK | 우선순위 |
|---|----------|---------|----------|----------|:-------:|
| 1 | `TC-TC-001` | trace_id 발급 -- create_trace() 호출 시 UUID v4 형식 반환 | trace_id가 "trace-" 접두어 + 32자 hex, ACTIVE 상태 | -- | P0 |
| 2 | `TC-TC-002` | Checkpoint 저장 -- save_checkpoint() 호출 시 정상 저장 | CheckpointRecord 반환, step_sequence 단조증가 | AT-007 | P0 |
| 3 | `TC-TC-003` | trace_id 누락 Checkpoint 거부 -- save_checkpoint(trace_id=None) | TraceMissing 발생, "LOCK-AT-007" 메시지 포함 | AT-007 | P0 |
| 4 | `TC-TC-004` | trace_id 빈 문자열 Checkpoint 거부 -- save_checkpoint(trace_id="") | TraceMissing 발생 | AT-007 | P0 |
| 5 | `TC-TC-005` | Checkpoint 복원 (마지막) -- restore_checkpoint(trace_id, step_id=None) | 마지막 Checkpoint 반환, is_latest=True | AT-007 | P0 |
| 6 | `TC-TC-006` | Checkpoint 복원 (특정 step) -- restore_checkpoint(trace_id, step_id="step-2") | 해당 step의 Checkpoint 반환, state 일치 | AT-007 | P0 |
| 7 | `TC-TC-007` | trace_id 누락 복원 거부 -- restore_checkpoint(trace_id=None) | TraceMissing 발생 | AT-007 | P0 |
| 8 | `TC-TC-008` | 미등록 trace 복원 시도 -- restore_checkpoint("non-existent-trace") | CheckpointNotFound 발생 | AT-007 | P0 |
| 9 | `TC-TC-009` | Fork -- fork_trace()로 새 trace 생성 | 새 trace_id 반환, 원본 Checkpoint 복사, 원본 보존 | AT-007 | P0 |
| 10 | `TC-TC-010` | trace_id 누락 Fork 거부 -- fork_trace(source_trace_id=None) | TraceMissing 발생 | AT-007 | P0 |
| 11 | `TC-TC-011` | Replay -- replay_trace()로 전체 Checkpoint 순회 | Checkpoint 순서대로 스냅샷 반환, REPLAYING 상태 | AT-007 | P0 |
| 12 | `TC-TC-012` | 완료된 trace에 Checkpoint 저장 시도 | TraceAlreadyCompleted 발생 | -- | P0 |
| 13 | `TC-TC-013` | trace 완료 처리 -- complete_trace() 후 상태 COMPLETED | trace 상태 COMPLETED, completed_at 설정 | -- | P1 |
| 14 | `TC-TC-014` | Checkpoint 체인 조회 -- get_checkpoint_chain() 전체 목록 반환 | 시간순 정렬, total_checkpoints 일치 | AT-007 | P1 |
| 15 | `TC-TC-015` | validate_trace_id() -- 등록/미등록 판별 | 등록: True, 미등록: False, None: TraceMissing | AT-007 | P1 |

### 7.2 pytest 테스트 스켈레톤

```python
import pytest


# --- TC-TC-001: trace_id 발급 ---
def test_trace_creation():
    """create_trace() 호출 시 UUID v4 형식 trace_id 반환."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-001")
    assert trace_id.startswith("trace-")
    assert len(trace_id) == 38  # "trace-" (6) + 32 hex
    status = manager.get_trace_status(trace_id)
    assert status == TraceStatus.ACTIVE


# --- TC-TC-002: Checkpoint 저장 ---
def test_checkpoint_save():
    """save_checkpoint() 정상 저장 확인."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-002")
    cp1 = manager.save_checkpoint(
        trace_id=trace_id, step_id="step-1",
        agent_id="research-001",
        state={"turn": 1, "cost": 0.0},
    )
    cp2 = manager.save_checkpoint(
        trace_id=trace_id, step_id="step-2",
        agent_id="coding-001",
        state={"turn": 2, "cost": 0.5},
    )
    assert cp1.step_sequence == 1
    assert cp2.step_sequence == 2
    assert cp1.status == CheckpointStatus.SAVED
    assert cp2.trace_id == trace_id


# --- TC-TC-003: trace_id 누락 Checkpoint 거부 ---
def test_checkpoint_rejected_none_trace_id():
    """save_checkpoint(trace_id=None) 시 TraceMissing."""
    manager = TraceManager()
    with pytest.raises(TraceMissing) as exc_info:
        manager.save_checkpoint(
            trace_id=None, step_id="step-1",
            agent_id="research-001",
            state={"turn": 1},
        )
    assert "LOCK-AT-007" in str(exc_info.value)
    assert exc_info.value.operation == "save_checkpoint"


# --- TC-TC-004: trace_id 빈 문자열 Checkpoint 거부 ---
def test_checkpoint_rejected_empty_trace_id():
    """save_checkpoint(trace_id='') 시 TraceMissing."""
    manager = TraceManager()
    with pytest.raises(TraceMissing):
        manager.save_checkpoint(
            trace_id="", step_id="step-1",
            agent_id="research-001",
            state={"turn": 1},
        )


# --- TC-TC-005: Checkpoint 복원 (마지막) ---
def test_restore_latest_checkpoint():
    """restore_checkpoint(step_id=None) 시 마지막 Checkpoint 반환."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-005")
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-1",
        agent_id="research-001", state={"turn": 1},
    )
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-2",
        agent_id="coding-001", state={"turn": 2},
    )
    snapshot = manager.restore_checkpoint(trace_id)
    assert snapshot.step_id == "step-2"
    assert snapshot.is_latest is True
    assert snapshot.state == {"turn": 2}
    assert snapshot.status == CheckpointStatus.RESTORED


# --- TC-TC-006: Checkpoint 복원 (특정 step) ---
def test_restore_specific_checkpoint():
    """restore_checkpoint(step_id='step-1') 시 해당 Checkpoint 반환."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-006")
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-1",
        agent_id="research-001", state={"turn": 1, "data": "alpha"},
    )
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-2",
        agent_id="coding-001", state={"turn": 2, "data": "beta"},
    )
    snapshot = manager.restore_checkpoint(trace_id, step_id="step-1")
    assert snapshot.step_id == "step-1"
    assert snapshot.state["data"] == "alpha"
    assert snapshot.is_latest is False


# --- TC-TC-007: trace_id 누락 복원 거부 ---
def test_restore_rejected_none_trace_id():
    """restore_checkpoint(trace_id=None) 시 TraceMissing."""
    manager = TraceManager()
    with pytest.raises(TraceMissing) as exc_info:
        manager.restore_checkpoint(trace_id=None)
    assert "LOCK-AT-007" in str(exc_info.value)


# --- TC-TC-008: 미등록 trace 복원 시도 ---
def test_restore_unregistered_trace():
    """미등록 trace_id로 복원 시도 시 CheckpointNotFound."""
    manager = TraceManager()
    with pytest.raises(CheckpointNotFound):
        manager.restore_checkpoint(trace_id="trace-nonexistent")


# --- TC-TC-009: Fork ---
def test_fork_trace():
    """fork_trace()로 새 trace 생성 확인."""
    manager = TraceManager()
    source_id = manager.create_trace(task_id="task-009")
    manager.save_checkpoint(
        trace_id=source_id, step_id="step-1",
        agent_id="research-001", state={"turn": 1},
    )
    manager.save_checkpoint(
        trace_id=source_id, step_id="step-2",
        agent_id="coding-001", state={"turn": 2},
    )
    manager.save_checkpoint(
        trace_id=source_id, step_id="step-3",
        agent_id="critic-001", state={"turn": 3},
    )

    new_id = manager.fork_trace(source_id, fork_step_id="step-2")
    assert new_id.startswith("trace-")
    assert new_id != source_id

    # 새 trace는 step-1, step-2까지의 Checkpoint만 복사
    chain = manager.get_checkpoint_chain(new_id)
    assert len(chain) == 2
    assert chain[-1].step_id == "step-2"

    # 원본 trace 보존 확인
    source_chain = manager.get_checkpoint_chain(source_id)
    assert len(source_chain) == 3


# --- TC-TC-010: trace_id 누락 Fork 거부 ---
def test_fork_rejected_none_trace_id():
    """fork_trace(source_trace_id=None) 시 TraceMissing."""
    manager = TraceManager()
    with pytest.raises(TraceMissing):
        manager.fork_trace(source_trace_id=None, fork_step_id="step-1")


# --- TC-TC-011: Replay ---
def test_replay_trace():
    """replay_trace()로 전체 Checkpoint 순회."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-011")
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-1",
        agent_id="research-001", state={"turn": 1},
    )
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-2",
        agent_id="coding-001", state={"turn": 2},
    )
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-3",
        agent_id="critic-001", state={"turn": 3},
    )

    replay = manager.replay_trace(trace_id)
    assert len(replay) == 3
    assert replay[0].step_sequence == 1
    assert replay[1].step_sequence == 2
    assert replay[2].step_sequence == 3
    assert all(s.status == CheckpointStatus.REPLAYING for s in replay)


# --- TC-TC-012: 완료된 trace에 Checkpoint 저장 시도 ---
def test_save_to_completed_trace():
    """COMPLETED trace에 save_checkpoint 시 TraceAlreadyCompleted."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-012")
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-1",
        agent_id="research-001", state={"turn": 1},
    )
    manager.complete_trace(trace_id, TraceStatus.COMPLETED)
    with pytest.raises(TraceAlreadyCompleted) as exc_info:
        manager.save_checkpoint(
            trace_id=trace_id, step_id="step-2",
            agent_id="coding-001", state={"turn": 2},
        )
    assert exc_info.value.trace_id == trace_id
    assert exc_info.value.status == "completed"


# --- TC-TC-013: trace 완료 처리 ---
def test_trace_completion():
    """complete_trace() 후 상태 COMPLETED 확인."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-013")
    manager.save_checkpoint(
        trace_id=trace_id, step_id="step-1",
        agent_id="research-001", state={"turn": 1},
    )
    result = manager.complete_trace(trace_id, TraceStatus.COMPLETED)
    assert result.status == TraceStatus.COMPLETED
    assert result.completed_at is not None
    assert manager.get_trace_status(trace_id) == TraceStatus.COMPLETED


# --- TC-TC-014: Checkpoint 체인 조회 ---
def test_checkpoint_chain():
    """get_checkpoint_chain() 전체 목록 시간순 반환."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-014")
    for i in range(5):
        manager.save_checkpoint(
            trace_id=trace_id, step_id=f"step-{i+1}",
            agent_id=f"agent-{i+1}", state={"step": i + 1},
        )
    chain = manager.get_checkpoint_chain(trace_id)
    assert len(chain) == 5
    for i, cp in enumerate(chain):
        assert cp.step_sequence == i + 1
        assert cp.is_latest == (i == 4)


# --- TC-TC-015: validate_trace_id ---
def test_validate_trace_id():
    """등록/미등록 판별 + None 시 TraceMissing."""
    manager = TraceManager()
    trace_id = manager.create_trace(task_id="task-015")
    assert manager.validate_trace_id(trace_id) is True
    assert manager.validate_trace_id("trace-nonexistent") is False
    with pytest.raises(TraceMissing):
        manager.validate_trace_id(None)
    with pytest.raises(TraceMissing):
        manager.validate_trace_id("")
```

---

## 8. 알고리즘 시간복잡도 + LOCK + ABC 요약

| 메서드 | ABC 시그니처 | 시간복잡도 | 관련 LOCK |
|--------|------------|-----------|----------|
| `create_trace()` | `create_trace(task_id, metadata) -> str` | O(1) -- UUID 생성 + dict 삽입 | -- (R8: trace_id 서버 생성 전용) |
| `save_checkpoint()` | `save_checkpoint(trace_id, step_id, agent_id, state) -> CheckpointRecord` | O(1) -- 리스트 append + deep copy | AT-007 |
| `restore_checkpoint()` | `restore_checkpoint(trace_id, step_id) -> CheckpointSnapshot` | O(n) -- n = checkpoints in trace (선형 탐색) | AT-007, AT-002 |
| `get_latest_checkpoint()` | `get_latest_checkpoint(trace_id) -> CheckpointSnapshot` | O(1) -- 리스트 마지막 요소 | AT-007 |
| `get_checkpoint_chain()` | `get_checkpoint_chain(trace_id) -> list[CheckpointSnapshot]` | O(n) -- n = checkpoints in trace | AT-007 |
| `replay_trace()` | `replay_trace(trace_id) -> list[CheckpointSnapshot]` | O(n) -- n = checkpoints in trace | AT-007 |
| `fork_trace()` | `fork_trace(source_trace_id, fork_step_id) -> str` | O(k) -- k = checkpoints up to fork_step | AT-007 |
| `complete_trace()` | `complete_trace(trace_id, status) -> TraceRecord` | O(1) -- 상태 전환 | -- |
| `get_trace_status()` | `get_trace_status(trace_id) -> TraceStatus` | O(1) -- dict 조회 | -- |
| `build_escalation_payload()` | `build_escalation_payload(trace_id, reason, task_id) -> TraceEscalationPayload` | O(1) -- 스냅샷 생성 | AT-007, AT-002 |
| `validate_trace_id()` | `validate_trace_id(trace_id) -> bool` | O(1) -- dict 존재 여부 확인 | AT-007 |

---

## 9. 세션간 인터페이스 cross-check

| 인접 세션 | 인터페이스 | 본 세션 사용 방식 | 정합성 |
|----------|-----------|-----------------|:------:|
| P1-01 (Lead Agent) | `LeadAgent.decide()` | Checkpoint 복원/폐기/Fork 결정을 Lead Agent에 에스컬레이션 (LOCK-AT-002). TraceEscalationPayload 전달 | OK |
| P1-04 (Sequential) | `SequentialPipeline` | 파이프라인 각 단계 완료 시 save_checkpoint() 호출하여 중간 상태 저장 | OK |
| P1-05 (Parallel) | `ParallelDispatcher.dispatch()` | 병렬 실행 전후 save_checkpoint() 호출. 실패 시 마지막 Checkpoint 복원 | OK |
| P1-06 (Delegation) | `DelegationChain.delegate()` | 위임 체인 각 단계에서 trace_id 전파 -- TraceManager가 발급한 trace_id 사용. Checkpoint에 위임 상태 포함 | OK |
| P1-07 (MessageBus) | `InMemoryMessageBus.publish()` | 메시지에 trace_id 포함 -- create_trace()로 발급된 trace_id 사용 | OK |
| P1-09 (Execute Tool) | `PhaseGuard.check_tool_call()` | Execute 단계 확인 후에만 save_checkpoint() 허용 (LOCK-AT-006 연계) | OK |
| P1-10 (Turn Limit) | `ConversationTracker.increment_turn()` | trace_id 기반 턴 추적. Checkpoint state에 턴 카운터 포함. 복원 시 턴 잔여 확인 | OK |
| P1-11 (TEE Loop) | `TEELoop.start_iteration()` | trace_id 기반 반복 추적. Checkpoint state에 TEE 반복 카운터 포함 | OK |
| P1-12 (Cost Tracker) | `CostTracker.record_cost()` | trace_id 기반 비용 추적. Checkpoint state에 비용 누적 포함. 복원 시 예산 잔여 확인 | OK |
| P1-13 (Loop Detector) | `LoopDetector.record_edge()` | trace_id 기반 순환 그래프. Checkpoint 복원 시 LoopDetector 재검증 필수 (순환 감지 방지). P1-13에서 "P1-14: TraceManager -- trace_id 관리 위임" 인터페이스 예약 해소 | OK |

---

## 10. 공통 자료 구조 선정의

### 10.1 본 세션 신규 정의

| 자료 구조 | 용도 | 재사용 가능 세션 |
|----------|------|----------------|
| `CheckpointStatus` (Enum) | Checkpoint 상태 분류 (SAVED/RESTORED/FORKED/REPLAYING/INVALIDATED) | Phase 2 감사 로그, P1-10/P1-11/P1-12 Checkpoint 연동 |
| `TraceStatus` (Enum) | 실행 추적 상태 (ACTIVE/COMPLETED/FAILED/SUSPENDED/FORKED) | P1-01 (Lead Agent 상태 관리), Phase 2 모니터링 |
| `CheckpointRecord` (dataclass) | 단일 Checkpoint 레코드 (state 스냅샷 포함) | Phase 2 (Persistent Checkpoint 확장) |
| `TraceRecord` (dataclass) | trace_id 단위 실행 추적 레코드 | Phase 2 (Redis 기반 trace 저장소) |
| `CheckpointSnapshot` (dataclass) | Checkpoint 조회/복원 시 반환 스냅샷 | P1-01 (Lead Agent 복원 결정), P1-06 (위임 체인 복원) |
| `TraceEscalationPayload` (dataclass) | trace 관련 에스컬레이션 페이로드 | P1-01 (Lead Agent 에스컬레이션 처리) |

### 10.2 참조 자료 구조 (타 세션 정의)

| 자료 구조 | 원본 | 본 세션 참조 방식 |
|----------|------|----------------|
| `AgentRole` (Enum) | P1-01 §3.1 | Checkpoint의 agent_id에 대응하는 역할 식별 |
| `EscalationPayload` (dataclass) | P1-01 §3.1 | TraceEscalationPayload 기반 구조 |
| `DelegationChainSnapshot` (dataclass) | P1-06 §3.1 | Checkpoint state에 위임 체인 상태 포함 시 참조 |
| `ConversationSnapshot` (dataclass) | P1-10 §3.1 | Checkpoint state에 턴 상태 포함 시 참조 |
| `TEELoopSnapshot` (dataclass) | P1-11 §3.1 | Checkpoint state에 TEE 반복 상태 포함 시 참조 |
| `CostSnapshot` (dataclass) | P1-12 §3.1 | Checkpoint state에 비용 상태 포함 시 참조 |
| `LoopDetectionSnapshot` (dataclass) | P1-13 §3.1 | Checkpoint 복원 시 LoopDetector 재검증에 사용 |
| `DelegationEdge` (dataclass) | P1-13 §3.1 | Checkpoint state에 위임 간선 기록 포함 시 참조 |

---

## 변경 이력

| 일자 | 변경 내용 | 세션 |
|------|----------|------|
| 2026-04-13 | 초기 작성 -- TraceManager 클래스 스켈레톤, CheckpointStatus/TraceStatus/CheckpointRecord/TraceRecord/CheckpointSnapshot/TraceEscalationPayload 자료 구조 6종, TraceMissing/CheckpointNotFound/TraceAlreadyCompleted 예외 3종, create_trace/save_checkpoint/restore_checkpoint/get_latest_checkpoint/get_checkpoint_chain/replay_trace/fork_trace/complete_trace/get_trace_status/build_escalation_payload/validate_trace_id 인터페이스 11종, Phase별 복구 전략 + 에스컬레이션 흐름도, 로깅 JSON 4종, 예외 처리 정책 7건, 테스트 15건(TC-TC-001~015), 세션간 인터페이스 10건 cross-check | P1-14 |

---

> **문서 끝**
> 본 문서는 P1-14 세션 산출물이며, LOCK-AT-007(Checkpoint/Replay/Fork는 trace_id 단위로만) 정본을 기반으로 작성되었습니다.
