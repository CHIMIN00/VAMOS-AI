# P1-13. 무한 루프 방지 로직 -- LoopDetector 클래스 및 순환 위임 차단 검증

> **도메인**: 6-3_Agent-Teams-PARL / 02_agent-swarm
> **세션**: P1-13
> **작성일**: 2026-04-13
> **대조 기준**: Part2 §6.7 무한 루프 방지, D2.0-03 §1.4 Sub-agent 상호 호출 금지, D2.0-05 §7.3 무한 대화 루프 금지, LOCK-AT-003(무한루프 금지)
> **선행 산출물**: P1-01_lead_agent_definition.md (P1-1), P1-04_sequential_pattern.md (P1-4), P1-05_parallel_pattern.md (P1-5), P1-06_delegation_chain.md (P1-6), P1-07_in_memory_messagebus.md (P1-7), P1-09_execute_tool_restriction.md (P1-9), P1-10_turn_limit.md (P1-10), P1-11_tee_max_iteration.md (P1-11), P1-12_cost_limit.md (P1-12)

---

## 1. 교차 참조 블록

| 문서 | 참조 위치 | 역할 |
|------|----------|------|
| D2.0-03 Conversation Flow | §1.4 L76 | LOCK-AT-003 근거 정본 -- "Sub-agent 간 직접 상호 호출/자유 대화 루프는 금지한다. 모든 호출/실행은 ORANGE CORE의 라우팅/결정 및 07 Gate를 경유한다." |
| D2.0-05 Agent Workflow | §7.3 L381 | LOCK-AT-003 보조 근거 -- "에이전트끼리 자유 상호 호출(무한 대화/루프)은 금지" |
| D2.0-05 Agent Workflow | §7.3 고정3 | 무한 루프 금지 + 도구 호출 제한 원칙 |
| D2.0-02 ORANGE CORE | §2.2 S3 Decision Locked | Lead Agent 단일결정 원칙 -- 순환 차단 시 Lead가 최종 결과 확정 (LOCK-AT-002) |
| D2.0-07 Safety/Cost/Approval | §7 S7E-080 | 위임 체인 깊이 제한과 순환 감지 연계 (LOCK-AT-004) |
| Part2 §6.7 | L5041 (LOCK-AT-003) | LOCK 값 선언 정본: "에이전트 간 자유 상호 호출 / 무한 대화 루프 금지" |
| Part2 §6.7 | L4994-5130 | 구현 요건 정본 (17 LOCK-AT) |
| Part2 §6.7 | L5042 (LOCK-AT-004) | 위임 체인 최대 깊이 3단계 (V1=2) -- 깊이 초과도 루프 방지 보조 |
| Part2 §6.7 | L5040 (LOCK-AT-002) | 단일결정 원칙: 순환 차단 후 결과 확정은 Lead만 수행 |
| Part2 §6.7 | L5045 (LOCK-AT-007) | trace_id 단위 Checkpoint -- 순환 감지 시 trace_id 기반 체인 추적 |
| AUTHORITY_CHAIN.md | §2.1 레지스트리 | LOCK-AT 17건 레지스트리 정본 (AT-003 위반 시나리오: "Agent A->B->A 순환 위임 -> 두 번째 역방향 위임 차단") |
| 종합계획서 §7.3 | P1-13 세부 항목 | 본 세션 작업 정의 |
| 종합계획서 §1.4 | Part2 핵심 내용 요약 | "에이전트 간 자유 상호 호출/무한 대화 루프 금지 (LOCK-AT-003)" |
| 종합계획서 §4.3 | R-63-2 | "Lead Agent(ORANGE CORE) 단일결정 원칙 위반 코드 감지 시 즉시 차단 + CONFLICT_LOG 기록" |
| 종합계획서 부록 §C.1 | LOCK-AT-003 위반 시나리오 | "Agent A->B->A 순환 위임 -> 위임 그래프 순환 탐지 -> 두 번째 역방향 위임 차단" |
| 종합계획서 부록 §C.2 | LOCK-AT 서브폴더 매핑 | AT-003 주 구현: 02_agent-swarm/execution_engine.md, 보조: P1-13 |
| 종합계획서 §8.2 | 02_agent-swarm 파일 역할 | execution_engine.md -> AT-003 무한 루프 금지 |
| P1-01_lead_agent_definition.md | §3 LeadAgent 클래스 | Lead Agent가 순환 차단 후 최종 결과 확정 (LOCK-AT-002) |
| P1-06_delegation_chain.md | §3 DelegationChain 클래스 | CircularDelegationDetected 예외, check_circular() 메서드 -- P1-13 LoopDetector와 연동 선언 |
| P1-07_in_memory_messagebus.md | SS 예외 처리 | "무한 루프 감지: 동일 패턴 3회+ 반복 -> 경고 로그 발행 (차단은 LoopDetector P1-13 담당)" |
| P1-11_tee_max_iteration.md | §3.3 TEELoop | "P1-13: LoopDetector -- 무한 루프 감지 보조 (LOCK-AT-003 연계)" -- TEELoop이 1차 방어선, LoopDetector가 2차 |
| P1-04_sequential_pattern.md | SequentialPipeline | 파이프라인 단계 간 순환 위임 가능성 -- LoopDetector로 사전 검증 |
| P1-05_parallel_pattern.md | ParallelDispatcher | InfiniteLoopDetected 예외 참조 -- 순환 감지 시 즉시 차단 + 전체 배치 취소 |
| P1-10_turn_limit.md | ConversationTracker | 턴 상한(AT-009)과 무한 루프 방지(AT-003) 독립 관리 -- 이중 안전장치 |
| P1-12_cost_limit.md | CostTracker | 비용 상한(AT-011)과 무한 루프 방지(AT-003) 삼중 안전장치 연계 |
| **인접 도메인** | | |
| 3-8 Conversation-A2A | A2A 프로토콜 규격 | Agent 간 메시지 프로토콜 소비 (재정의 금지) |
| 3-10 Agent-Protocol | L0-L4 자율성 정의 | Agent 자율성 레벨 배정 참조 (재정의 금지) |
| 6-2 Security-Governance | 보안 정책 | 순환 위임 시도 보안 체크리스트 우선 적용 (§9.3) |

---

## 2. 무한 루프 방지 개요

### 2.1 무한 루프 방지 식별

| 속성 | 값 |
|------|-----|
| **모듈 ID** | `LoopDetector` |
| **도입 버전** | V1 |
| **적용 범위** | 모든 Agent 간 위임 경로에서 순환(자기 위임, 직접 순환, 간접 순환) 탐지 및 즉시 차단 |
| **감지 대상 1** | 자기 위임: Agent A -> A |
| **감지 대상 2** | 직접 순환: Agent A -> B -> A |
| **감지 대상 3** | 간접 순환: Agent A -> B -> C -> A (N단계 간접 순환) |
| **감지 알고리즘** | 방문 집합(visited set) 기반 깊이 우선 탐색 (DFS) |
| **차단 정책** | `InfiniteLoopDetected` 예외 즉시 발생 + 전체 위임 체인 스냅샷 에러 로그 포함 |
| **LOCK 근거** | LOCK-AT-003 (무한 루프 금지) |
| **방어선 계층** | 1차: TEELoop 반복 카운터(AT-010), 2차: LoopDetector 순환 탐지(AT-003), 3차: ConversationTracker 턴 상한(AT-009) |
| **DelegationChain 연동** | P1-06 DelegationChain.check_circular() -> LoopDetector.detect_cycle() 위임 가능 |
| **MessageBus 연동** | P1-07 InMemoryMessageBus에서 동일 패턴 3회+ 반복 감지 시 LoopDetector에 검증 위임 |
| **Lead 결정 원칙** | LOCK-AT-002: 순환 차단 후 최종 결과 확정은 Lead Agent만 수행 |

### 2.2 LOCK 값 인용

> LOCK-AT-003 (Part2 §6.7 L5041 / D2.0-03 §1.4 L76 / D2.0-05 §7.3 L381):
> "에이전트 간 자유 상호 호출 / 무한 대화 루프 금지"

> LOCK-AT-003 (D2.0-03 §1.4 L76):
> "Sub-agent 간 직접 상호 호출/자유 대화 루프는 금지한다. 모든 호출/실행은 ORANGE CORE의 라우팅/결정 및 07 Gate를 경유한다."

> LOCK-AT-004 (Part2 §6.7 L5042 / D2.0-07 S7E-080):
> "위임 체인 최대 깊이 3단계 (V1 config=2)"

> LOCK-AT-002 (Part2 §6.7 L5040 / D2.0-02 §2.2 S3):
> "단일결정 원칙: 최종 결론은 Lead Agent(ORANGE CORE)만 확정"

> LOCK-AT-007 (Part2 §6.7 L5045 / D2.0-05 §7.3):
> "Checkpoint/Replay/Fork는 trace_id 단위로만 허용"

### 2.3 순환 위임 패턴 분류

```
순환 위임 패턴 유형:

1. 자기 위임 (Self-Delegation):
   Agent A --delegate--> Agent A
   즉시 거부. 동일 agent_id 감지로 O(1) 차단.

2. 직접 순환 (Direct Cycle):
   Agent A --delegate--> Agent B --delegate--> Agent A
   방문 집합에서 A 재방문 감지. O(1) 조회.

3. 간접 순환 (Indirect Cycle):
   Agent A --delegate--> Agent B --delegate--> Agent C --delegate--> Agent A
   N단계 경로에서 A 재방문 감지. O(n) 탐색 (n = 체인 노드 수).

4. 메시지 순환 (Message Loop):
   Agent A --publish(topic_X)--> Agent B --publish(topic_Y)--> Agent A (반복)
   동일 (from, to, topic) 패턴 반복 횟수 추적. 임계값(3회) 초과 시 차단.

적용 규칙:
- 모든 위임/메시지 경로는 LoopDetector.record_edge()로 등록.
- detect_cycle()은 현재 방문 집합 기반으로 O(n) 탐지.
- has_self_loop()은 O(1) 동일 ID 비교.
- 차단 시 전체 체인 경로를 스냅샷으로 에러 로그에 포함.
```

### 2.4 방어선 3중 계층 구조

```
방어선 계층:

[1차 방어선] TEELoop 반복 카운터 (LOCK-AT-010)
   - P0=3, P1=5, P2=10 반복 상한
   - 동일 Task 내 반복 횟수 제한으로 무한 실행 차단
   - P1-11 TEELoop.start_iteration() 에서 카운터 검증
       |
       v
[2차 방어선] LoopDetector 순환 위임 탐지 (LOCK-AT-003) ← 본 세션
   - 위임 경로 그래프에서 순환 패턴 실시간 감지
   - 자기 위임, 직접 순환, 간접 순환, 메시지 순환 4종 탐지
   - DelegationChain(P1-06) + MessageBus(P1-07) 연동
       |
       v
[3차 방어선] ConversationTracker 턴 상한 (LOCK-AT-009)
   - P0=5, P1=10, P2=20 턴 상한
   - 순환이 감지되지 않더라도 전체 대화 턴으로 최종 차단
   - P1-10 ConversationTracker.increment_turn() 에서 검증
       |
       v
[보조 방어선] CostTracker 비용 상한 (LOCK-AT-011)
   - 순환으로 인한 비용 폭주 시 비용 상한으로 자동 차단
   - R-63-5: 비용 상한 + TEE 반복 상한 동시 적용
   - P1-12 CostTracker.record_cost() 에서 검증
```

---

## 3. LoopDetector 클래스 스켈레톤

### 3.1 공통 자료 구조 (§7 공통 자료 구조 선정의)

```python
from __future__ import annotations
from typing import Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import logging
import json

# ---------------------------------------------------------------------------
# 공통 자료 구조 -- P1-06 공유 (DelegationNode, CircularDelegationDetected)
# P1-01 공유 (AgentRole, EscalationPayload)
# P1-07 공유 (InMemoryMessageBus)
# ---------------------------------------------------------------------------
# P1-06_delegation_chain.md §3.1에서 정의된 DelegationNode를 재사용.
# P1-01_lead_agent_definition.md §3.1에서 정의된 AgentRole, EscalationPayload를 재사용.
# P1-07_in_memory_messagebus.md §3에서 정의된 InMemoryMessageBus를 재사용.
# 여기서는 LoopDetector에 필요한 추가 구조만 정의.

# --- P1-06 참조: DelegationNode, DelegationChainSnapshot, CircularDelegationDetected --- (import 가정)
# --- P1-01 참조: AgentRole(9종), EscalationPayload, TaskStatus --- (import 가정)
# --- P1-07 참조: InMemoryMessageBus --- (import 가정)


class LoopType(Enum):
    """순환 위임 유형 분류.

    LOCK-AT-003: 에이전트 간 자유 상호 호출 / 무한 대화 루프 금지.
    """
    SELF_DELEGATION = "self_delegation"          # A -> A
    DIRECT_CYCLE = "direct_cycle"                # A -> B -> A
    INDIRECT_CYCLE = "indirect_cycle"            # A -> B -> C -> A
    MESSAGE_LOOP = "message_loop"                # 동일 메시지 패턴 반복


@dataclass
class DelegationEdge:
    """위임 경로 그래프의 간선.

    from_agent -> to_agent 위임 한 건을 나타낸다.
    """
    from_agent: str                       # 위임자 agent_id
    to_agent: str                         # 수임자 agent_id
    trace_id: str                         # LOCK-AT-007: trace_id 전파
    task_id: str                          # 위임 태스크 ID
    edge_id: str = field(default_factory=lambda: f"edge-{uuid.uuid4().hex[:8]}")
    timestamp: float = field(default_factory=time.time)
    depth: int = 0                        # 현재 위임 깊이


@dataclass
class LoopDetectionSnapshot:
    """순환 감지 시점의 전체 위임 경로 스냅샷.

    에러 로그 및 에스컬레이션 페이로드에 포함하여 디버깅 지원.
    LOCK-AT-007: trace_id 기반 경로 재구성.
    """
    trace_id: str
    detection_id: str
    loop_type: LoopType
    cycle_path: list[str]                 # 순환 경로 [A, B, C, A]
    all_edges: list[DelegationEdge]       # 감지 시점의 전체 간선 목록
    total_nodes: int                      # 전체 노드 수
    total_edges: int                      # 전체 간선 수
    detected_at: float = field(default_factory=time.time)
    message: str = ""


@dataclass
class MessagePattern:
    """메시지 반복 패턴 추적.

    동일 (from_agent, to_agent, topic) 조합의 반복 횟수 추적.
    P1-07 InMemoryMessageBus 연동: 동일 패턴 3회+ 시 경고/차단.
    """
    from_agent: str
    to_agent: str
    topic: str
    count: int = 0
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    trace_ids: list[str] = field(default_factory=list)


@dataclass
class LoopEscalationPayload:
    """무한 루프 감지 시 에스컬레이션 페이로드.

    EscalationPayload (P1-01 §3.1)를 확장하여 루프 감지 컨텍스트 포함.
    Lead Agent에 전달하여 최종 결과 확정에 사용.
    """
    trace_id: str
    escalation_id: str
    task_id: str
    detection_id: str
    loop_type: str                        # LoopType.value
    cycle_path: list[str]                 # 순환 경로
    snapshot: LoopDetectionSnapshot       # 전체 스냅샷
    triggering_edge: DelegationEdge       # 순환을 트리거한 마지막 간선
    reason: str
    error_context: dict[str, Any] = field(default_factory=dict)
    severity: str = "CRITICAL"
    created_at: float = field(default_factory=time.time)
```

### 3.2 예외 클래스 정의

```python
class InfiniteLoopDetected(Exception):
    """LOCK-AT-003 위반: 순환 위임 또는 무한 루프 감지 시 발생.

    자기 위임, 직접 순환, 간접 순환, 메시지 루프 모두 포함.
    종합계획서 부록 §C.1: "Agent A->B->A 순환 위임 -> 위임 그래프 순환 탐지 -> 두 번째 역방향 위임 차단"
    """

    def __init__(self, loop_type: LoopType, cycle_path: list[str],
                 snapshot: Optional[LoopDetectionSnapshot] = None):
        self.loop_type = loop_type
        self.cycle_path = cycle_path
        self.snapshot = snapshot
        cycle_str = " -> ".join(cycle_path)
        super().__init__(
            f"LOCK-AT-003: Infinite loop detected — "
            f"type={loop_type.value}, "
            f"cycle=[{cycle_str}]. "
            f"Immediate block. All delegations in this cycle are rejected."
        )


class SelfDelegationDenied(Exception):
    """LOCK-AT-003 위반: Agent가 자기 자신에게 위임 시도.

    자기 위임은 가장 단순한 무한 루프 형태로, O(1)에 즉시 차단.
    """

    def __init__(self, agent_id: str, task_id: str):
        self.agent_id = agent_id
        self.task_id = task_id
        super().__init__(
            f"LOCK-AT-003: Self-delegation denied — "
            f"agent={agent_id} attempted to delegate task={task_id} to itself. "
            f"Immediate block."
        )


class MessageLoopDetected(Exception):
    """LOCK-AT-003 위반: 동일 메시지 패턴 반복 임계값 초과.

    P1-07 InMemoryMessageBus에서 동일 (from, to, topic) 패턴이 임계값(기본 3회) 이상
    반복될 때 발생. LoopDetector가 차단을 담당.
    """

    def __init__(self, pattern: MessagePattern, threshold: int):
        self.pattern = pattern
        self.threshold = threshold
        super().__init__(
            f"LOCK-AT-003: Message loop detected — "
            f"pattern=({pattern.from_agent} -> {pattern.to_agent}, "
            f"topic={pattern.topic}), "
            f"count={pattern.count} >= threshold={threshold}. "
            f"Immediate block."
        )
```

### 3.3 LoopDetector 인터페이스 정의

```python
class LoopDetector:
    """Agent 간 순환 위임 및 무한 루프 감지기.

    LOCK-AT-003: 에이전트 간 자유 상호 호출 / 무한 대화 루프 금지 -- 실시간 감지 및 차단.
    LOCK-AT-004: 위임 체인 최대 깊이 3단계 (V1=2) -- 깊이 초과도 간접 루프 방지.
    LOCK-AT-002: 순환 차단 후 최종 결론은 Lead Agent(ORANGE CORE)만 확정.
    LOCK-AT-007: trace_id 단위로 위임 경로 추적 및 Checkpoint 허용.

    시간복잡도:
      - record_edge(): O(n) where n = visited nodes in trace (방문 집합 갱신 + 순환 검사)
      - detect_cycle(): O(n) where n = total nodes reachable from source (DFS 탐색)
      - has_self_loop(): O(1) 상수 시간 (동일 ID 비교)
      - check_message_pattern(): O(1) 상수 시간 (해시 조회 + 카운터 증가)
      - get_snapshot(): O(e) where e = total edges (간선 복사)
      - get_cycle_path(): O(n) where n = nodes in cycle (경로 재구성)
      - reset_trace(): O(e) where e = edges in trace (해당 trace 간선 제거)
      - build_escalation_payload(): O(e) where e = total edges (스냅샷 생성)

    ABC 시그니처:
      record_edge(from_agent, to_agent, trace_id, task_id) -> DelegationEdge
      detect_cycle(from_agent, to_agent, trace_id) -> Optional[list[str]]
      has_self_loop(from_agent, to_agent) -> bool
      check_message_pattern(from_agent, to_agent, topic, trace_id) -> bool
      get_snapshot(trace_id) -> LoopDetectionSnapshot
      get_cycle_path(trace_id, start_agent) -> list[str]
      reset_trace(trace_id) -> int
      build_escalation_payload(loop_type, cycle_path, triggering_edge) -> LoopEscalationPayload
    """

    # 메시지 반복 임계값 -- P1-07 InMemoryMessageBus에서 3회+ 반복 감지 기준과 일치
    MESSAGE_LOOP_THRESHOLD: int = 3

    def __init__(self,
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Args:
            logger: 로깅 인스턴스.

        세션간 인터페이스 cross-check:
          - P1-01: LeadAgent -- 순환 차단 후 decide()로 최종 결과 확정
          - P1-04: SequentialPipeline -- 파이프라인 단계 간 위임 시 record_edge() 호출
          - P1-05: ParallelDispatcher -- 병렬 위임 시 InfiniteLoopDetected 예외 처리
          - P1-06: DelegationChain -- check_circular() -> detect_cycle() 위임 연동
          - P1-07: InMemoryMessageBus -- 메시지 패턴 감지 -> check_message_pattern() 위임
          - P1-09: PhaseGuard -- Execute 단계 도구 호출 제한과 독립 (상호 간섭 없음)
          - P1-10: ConversationTracker -- 턴 상한(AT-009) 3차 방어선 연계
          - P1-11: TEELoop -- 반복 카운터(AT-010) 1차 방어선 연계
          - P1-12: CostTracker -- 비용 상한(AT-011) 보조 방어선 연계
          - P1-14: TraceManager -- trace_id 관리 위임 (LOCK-AT-007)
        """
        # 위임 경로 그래프: trace_id -> {from_agent -> [to_agent, ...]}
        self._adjacency: dict[str, dict[str, list[str]]] = {}
        # 간선 기록: trace_id -> [DelegationEdge, ...]
        self._edges: dict[str, list[DelegationEdge]] = {}
        # 방문 집합: trace_id -> set(agent_id)
        self._visited: dict[str, set[str]] = {}
        # 메시지 패턴 추적: (from_agent, to_agent, topic) -> MessagePattern
        self._message_patterns: dict[tuple[str, str, str], MessagePattern] = {}
        self._logger = logger or logging.getLogger("loop_detector")

    # ---------- 핵심 메서드 ----------

    def record_edge(self, from_agent: str, to_agent: str,
                    trace_id: str, task_id: str) -> DelegationEdge:
        """위임 간선을 기록하고 순환 검사를 수행한다.

        1. 자기 위임 검사 (O(1)).
        2. 간선 등록 (인접 리스트 + 방문 집합 갱신).
        3. 순환 탐지 (detect_cycle).
        4. 순환 발견 시 InfiniteLoopDetected 즉시 발생.

        Args:
            from_agent: 위임자 agent_id.
            to_agent: 수임자 agent_id.
            trace_id: 실행 추적 ID (LOCK-AT-007).
            task_id: 위임 태스크 ID.

        Returns:
            DelegationEdge: 등록된 간선.

        Raises:
            SelfDelegationDenied: 자기 위임 시도.
            InfiniteLoopDetected: 순환 위임 감지.

        시간복잡도: O(n) where n = visited nodes in trace
        """
        # 1. 자기 위임 검사 (LOCK-AT-003)
        if self.has_self_loop(from_agent, to_agent):
            self._logger.error(json.dumps({
                "event": "loop_detector.self_delegation_blocked",
                "trace_id": trace_id,
                "task_id": task_id,
                "agent_id": from_agent,
                "violation": {
                    "lock_id": "LOCK-AT-003",
                    "loop_type": LoopType.SELF_DELEGATION.value,
                },
            }))
            raise SelfDelegationDenied(from_agent, task_id)

        # 2. 간선 등록
        if trace_id not in self._adjacency:
            self._adjacency[trace_id] = {}
            self._edges[trace_id] = []
            self._visited[trace_id] = set()

        adj = self._adjacency[trace_id]
        if from_agent not in adj:
            adj[from_agent] = []

        self._visited[trace_id].add(from_agent)
        self._visited[trace_id].add(to_agent)

        edge = DelegationEdge(
            from_agent=from_agent,
            to_agent=to_agent,
            trace_id=trace_id,
            task_id=task_id,
            depth=len(self._edges.get(trace_id, [])),
        )

        # 3. 순환 탐지 (DFS) -- 간선 추가 전에 검사
        cycle_path = self.detect_cycle(from_agent, to_agent, trace_id)
        if cycle_path is not None:
            # 순환 유형 판별
            loop_type = (
                LoopType.DIRECT_CYCLE
                if len(cycle_path) == 3  # [A, B, A]
                else LoopType.INDIRECT_CYCLE
            )
            snapshot = LoopDetectionSnapshot(
                trace_id=trace_id,
                detection_id=f"det-{uuid.uuid4().hex[:8]}",
                loop_type=loop_type,
                cycle_path=cycle_path,
                all_edges=list(self._edges.get(trace_id, [])),
                total_nodes=len(self._visited.get(trace_id, set())),
                total_edges=len(self._edges.get(trace_id, [])),
                message=f"Cycle detected: {' -> '.join(cycle_path)}",
            )
            self._logger.error(json.dumps({
                "event": "loop_detector.cycle_detected",
                "trace_id": trace_id,
                "task_id": task_id,
                "violation": {
                    "lock_id": "LOCK-AT-003",
                    "loop_type": loop_type.value,
                    "cycle_path": cycle_path,
                },
                "snapshot": {
                    "detection_id": snapshot.detection_id,
                    "total_nodes": snapshot.total_nodes,
                    "total_edges": snapshot.total_edges,
                },
            }))
            raise InfiniteLoopDetected(
                loop_type=loop_type,
                cycle_path=cycle_path,
                snapshot=snapshot,
            )

        # 4. 간선 추가 (순환 없음 확인 후)
        adj[from_agent].append(to_agent)
        self._edges[trace_id].append(edge)

        self._logger.info(json.dumps({
            "event": "loop_detector.edge_recorded",
            "trace_id": trace_id,
            "task_id": task_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "edge_id": edge.edge_id,
            "total_edges": len(self._edges[trace_id]),
            "total_nodes": len(self._visited[trace_id]),
        }))
        return edge

    def detect_cycle(self, from_agent: str, to_agent: str,
                     trace_id: str) -> Optional[list[str]]:
        """from_agent -> to_agent 간선 추가 시 순환이 발생하는지 검사한다.

        to_agent에서 from_agent로 도달 가능한 경로가 있으면 순환.
        DFS 기반 경로 탐색.

        Args:
            from_agent: 위임자 agent_id.
            to_agent: 수임자 agent_id (새 간선의 목적지).
            trace_id: 실행 추적 ID.

        Returns:
            None이면 순환 없음.
            list[str]이면 순환 경로 (예: ["A", "B", "C", "A"]).

        시간복잡도: O(n) where n = total nodes reachable from to_agent
        """
        adj = self._adjacency.get(trace_id, {})
        if not adj:
            return None

        # to_agent에서 출발하여 from_agent에 도달 가능한지 DFS
        visited: set[str] = set()
        path: list[str] = [from_agent, to_agent]

        def _dfs(current: str) -> Optional[list[str]]:
            if current == from_agent:
                # 순환 발견: path 자체가 이미 [from_agent, ..., current(=from_agent)] 형태
                return list(path)
            if current in visited:
                return None
            visited.add(current)
            for neighbor in adj.get(current, []):
                path.append(neighbor)
                result = _dfs(neighbor)
                if result is not None:
                    return result
                path.pop()
            return None

        return _dfs(to_agent)

    def has_self_loop(self, from_agent: str, to_agent: str) -> bool:
        """자기 위임 여부 확인. O(1).

        Args:
            from_agent: 위임자 agent_id.
            to_agent: 수임자 agent_id.

        Returns:
            True이면 자기 위임.
        """
        return from_agent == to_agent

    def check_message_pattern(self, from_agent: str, to_agent: str,
                              topic: str, trace_id: str) -> bool:
        """메시지 반복 패턴을 검사한다.

        동일 (from_agent, to_agent, topic) 조합의 반복 횟수를 추적하여
        임계값(MESSAGE_LOOP_THRESHOLD) 초과 시 MessageLoopDetected 발생.

        P1-07 InMemoryMessageBus에서 호출.

        Args:
            from_agent: 메시지 발신 agent_id.
            to_agent: 메시지 수신 agent_id.
            topic: 메시지 토픽.
            trace_id: 실행 추적 ID.

        Returns:
            True이면 안전 (임계값 미달).

        Raises:
            MessageLoopDetected: 임계값 초과.

        시간복잡도: O(1)
        """
        key = (trace_id, from_agent, to_agent, topic)
        if key not in self._message_patterns:
            self._message_patterns[key] = MessagePattern(
                from_agent=from_agent,
                to_agent=to_agent,
                topic=topic,
            )

        pattern = self._message_patterns[key]
        pattern.count += 1
        pattern.last_seen = time.time()
        pattern.trace_ids.append(trace_id)

        if pattern.count >= self.MESSAGE_LOOP_THRESHOLD:
            self._logger.error(json.dumps({
                "event": "loop_detector.message_loop_detected",
                "trace_id": trace_id,
                "violation": {
                    "lock_id": "LOCK-AT-003",
                    "loop_type": LoopType.MESSAGE_LOOP.value,
                    "from_agent": from_agent,
                    "to_agent": to_agent,
                    "topic": topic,
                    "count": pattern.count,
                    "threshold": self.MESSAGE_LOOP_THRESHOLD,
                },
            }))
            raise MessageLoopDetected(pattern, self.MESSAGE_LOOP_THRESHOLD)

        self._logger.debug(json.dumps({
            "event": "loop_detector.message_pattern_tracked",
            "trace_id": trace_id,
            "from_agent": from_agent,
            "to_agent": to_agent,
            "topic": topic,
            "count": pattern.count,
            "threshold": self.MESSAGE_LOOP_THRESHOLD,
        }))
        return True

    def get_snapshot(self, trace_id: str) -> LoopDetectionSnapshot:
        """특정 trace_id의 전체 위임 경로 스냅샷 반환.

        LOCK-AT-007: trace_id 단위로 Checkpoint/Replay 허용.

        Args:
            trace_id: 실행 추적 ID.

        Returns:
            LoopDetectionSnapshot: 스냅샷.

        시간복잡도: O(e) where e = total edges in trace
        """
        edges = list(self._edges.get(trace_id, []))
        nodes = self._visited.get(trace_id, set())
        return LoopDetectionSnapshot(
            trace_id=trace_id,
            detection_id=f"snap-{uuid.uuid4().hex[:8]}",
            loop_type=LoopType.INDIRECT_CYCLE,  # 기본값; 실제 감지 시 갱신
            cycle_path=[],
            all_edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges),
            message=f"Snapshot for trace {trace_id}: {len(nodes)} nodes, {len(edges)} edges",
        )

    def get_cycle_path(self, trace_id: str, start_agent: str) -> list[str]:
        """특정 에이전트에서 시작하는 순환 경로 탐색.

        Args:
            trace_id: 실행 추적 ID.
            start_agent: 시작 에이전트 ID.

        Returns:
            list[str]: 순환 경로 (비어있으면 순환 없음).

        시간복잡도: O(n) where n = nodes in reachable graph
        """
        adj = self._adjacency.get(trace_id, {})
        if not adj:
            return []

        visited: set[str] = set()
        path: list[str] = [start_agent]

        def _dfs(current: str) -> list[str]:
            for neighbor in adj.get(current, []):
                if neighbor == start_agent:
                    return path + [start_agent]
                if neighbor not in visited:
                    visited.add(neighbor)
                    path.append(neighbor)
                    result = _dfs(neighbor)
                    if result:
                        return result
                    path.pop()
            return []

        visited.add(start_agent)
        return _dfs(start_agent)

    def reset_trace(self, trace_id: str) -> int:
        """특정 trace의 모든 간선 및 방문 기록 초기화.

        태스크 완료 또는 Checkpoint 복원 시 사용.

        Args:
            trace_id: 초기화할 추적 ID.

        Returns:
            int: 제거된 간선 수.

        시간복잡도: O(e) where e = edges in trace
        """
        removed = len(self._edges.get(trace_id, []))
        self._adjacency.pop(trace_id, None)
        self._edges.pop(trace_id, None)
        self._visited.pop(trace_id, None)
        self._logger.info(json.dumps({
            "event": "loop_detector.trace_reset",
            "trace_id": trace_id,
            "edges_removed": removed,
        }))
        return removed

    def build_escalation_payload(self, loop_type: LoopType,
                                  cycle_path: list[str],
                                  triggering_edge: DelegationEdge
                                  ) -> LoopEscalationPayload:
        """무한 루프 에스컬레이션 페이로드 생성.

        Lead Agent에 전달하여 최종 결과 확정에 사용.
        LOCK-AT-002: 최종 결론은 Lead Agent(ORANGE CORE)만 확정.

        Args:
            loop_type: 감지된 루프 유형.
            cycle_path: 순환 경로.
            triggering_edge: 순환을 트리거한 마지막 간선.

        Returns:
            LoopEscalationPayload: 에스컬레이션 페이로드.
        """
        snapshot = self.get_snapshot(triggering_edge.trace_id)
        snapshot.loop_type = loop_type
        snapshot.cycle_path = cycle_path
        return LoopEscalationPayload(
            trace_id=triggering_edge.trace_id,
            escalation_id=f"esc-loop-{uuid.uuid4().hex[:8]}",
            task_id=triggering_edge.task_id,
            detection_id=snapshot.detection_id,
            loop_type=loop_type.value,
            cycle_path=cycle_path,
            snapshot=snapshot,
            triggering_edge=triggering_edge,
            reason=(
                f"LOCK-AT-003: {loop_type.value} detected — "
                f"cycle=[{' -> '.join(cycle_path)}]"
            ),
        )
```

---

## 4. Phase별 복구 전략

### 4.1 복구 흐름도

```
순환 위임 감지 시:

[InfiniteLoopDetected / SelfDelegationDenied / MessageLoopDetected 예외 발생]
        |
        v
+------------------------------------------------+
| Phase 0: 즉시 차단                               |
|  - 위임 요청 거부 + 에러 로그 발행               |
|  - 전체 위임 체인 스냅샷을 Lead에 반환           |
|  - 해당 trace의 진행 중 태스크 취소              |
|  - 재시도 불가 -> 새 Task로 경로 재설계 필요      |
+----------------------------+---------------------+
                             | Phase 1+
                             v
+------------------------------------------------+
| Phase 1: 경로 재설계 시도                         |
|  - DelegationChain(P1-06) 초기화 후 대안 경로 탐색 |
|  - CostTracker(P1-12, AT-011) 잔여 예산 확인     |
|  - 예산 잔여 시: 순환 에이전트 제외 후 재위임     |
|  - 예산 소진 시: 즉시 차단 + 에스컬레이션         |
|  - R-63-7: 깊이 재검증 필수                      |
+----------------------------+---------------------+
                             | Phase 2+
                             v
+------------------------------------------------+
| Phase 2: Supervisor 중재                         |
|  - Supervisor Agent가 순환 분석 후 태스크 재분배  |
|  - 순환 원인 에이전트 격리 (임시 비활성화)        |
|  - 이전 LoopDetectionSnapshot 기반 회피 경로 수립 |
|  - trace_id 유지 (LOCK-AT-007 Checkpoint 활용)   |
|  - 3회 이상 순환 재발 시 태스크 실패 처리         |
+------------------------------------------------+
```

### 4.2 복구 판단 매트릭스

| 상황 | Phase 0 | Phase 1 | Phase 2 |
|------|---------|---------|---------|
| 자기 위임 감지 | 즉시 거부, 에러 로그 | 다른 에이전트로 재위임 | Supervisor가 적합 에이전트 배정 |
| 직접 순환 (A->B->A) | 즉시 차단, B의 부분 결과 반환 | A 또는 B 중 하나 제외 후 재위임 | Supervisor가 제3 에이전트 투입 |
| 간접 순환 (A->B->C->A) | 즉시 차단, 전체 체인 스냅샷 반환 | 순환 지점 에이전트 제외 후 재구성 | Supervisor가 태스크 분할 재설계 |
| 메시지 루프 (3회+) | 경고 후 차단 | 메시지 패턴 초기화 + 토픽 변경 | 통신 경로 재설계 |
| 비용 상한 동시 도달 | 비용 차단 우선 (AT-011) | 비용 차단 우선 | 비용 차단 우선 |
| 외부 강제 종료 (Lead) | 즉시 차단 | 즉시 차단 | 즉시 차단 |

---

## 5. 에스컬레이션 페이로드 상세

### 5.1 에스컬레이션 흐름

```
[LoopDetector -- 순환 감지]
        |
        v
[InfiniteLoopDetected 예외 + LoopDetectionSnapshot 포함]
        |
        v
[호출자 (DelegationChain / MessageBus) -- 예외 포착]
        |
        +- build_escalation_payload() 호출
        |
        v
[LoopEscalationPayload 생성]
        |
        +- loop_type: 순환 유형 (self/direct/indirect/message)
        +- cycle_path: 순환 경로 (예: ["A", "B", "C", "A"])
        +- snapshot: 전체 위임 경로 스냅샷
        +- triggering_edge: 순환 트리거 간선
        |
        v
[InMemoryMessageBus (P1-07) -- 에스컬레이션 메시지 전달]
        |
        v
[Lead Agent (P1-01) -- decide()]
        |
        +- LOCK-AT-002: 최종 결과 확정
        +- 순환 원인 분석 후 경로 재설계 또는
        +- 부분 결과 채택 + 태스크 종료 결정
        |
        v
[결과 반환 또는 새 경로로 재위임]
```

### 5.2 로깅 중첩 JSON -- 자기 위임 차단 로그

```json
{
  "event": "loop_detector.self_delegation_blocked",
  "timestamp": "2026-04-13T10:00:00.000Z",
  "severity": "ERROR",
  "trace_id": "trace-abc123",
  "task_id": "task-def456",
  "agent_id": "research-001",
  "violation": {
    "lock_id": "LOCK-AT-003",
    "loop_type": "self_delegation",
    "description": "Agent attempted to delegate task to itself"
  },
  "action": "blocked"
}
```

### 5.3 로깅 중첩 JSON -- 순환 위임 감지 로그

```json
{
  "event": "loop_detector.cycle_detected",
  "timestamp": "2026-04-13T10:05:00.000Z",
  "severity": "ERROR",
  "trace_id": "trace-abc123",
  "task_id": "task-def456",
  "violation": {
    "lock_id": "LOCK-AT-003",
    "loop_type": "indirect_cycle",
    "cycle_path": ["agent-A", "agent-B", "agent-C", "agent-A"],
    "cycle_length": 3,
    "triggering_edge": {
      "from": "agent-C",
      "to": "agent-A",
      "edge_id": "edge-abcd1234"
    }
  },
  "snapshot": {
    "detection_id": "det-ef567890",
    "total_nodes": 3,
    "total_edges": 2,
    "all_edges": [
      {"from": "agent-A", "to": "agent-B", "edge_id": "edge-11111111"},
      {"from": "agent-B", "to": "agent-C", "edge_id": "edge-22222222"}
    ]
  },
  "escalation": {
    "escalation_id": "esc-loop-gh901234",
    "severity": "CRITICAL",
    "action": "immediate_block"
  }
}
```

### 5.4 로깅 중첩 JSON -- 메시지 루프 감지 로그

```json
{
  "event": "loop_detector.message_loop_detected",
  "timestamp": "2026-04-13T10:08:00.000Z",
  "severity": "ERROR",
  "trace_id": "trace-abc123",
  "violation": {
    "lock_id": "LOCK-AT-003",
    "loop_type": "message_loop",
    "from_agent": "agent-A",
    "to_agent": "agent-B",
    "topic": "task_result",
    "count": 3,
    "threshold": 3,
    "pattern_duration_ms": 15000,
    "trace_ids": ["trace-abc123", "trace-abc123", "trace-abc123"]
  },
  "action": "blocked"
}
```

### 5.5 로깅 중첩 JSON -- 간선 정상 등록 로그

```json
{
  "event": "loop_detector.edge_recorded",
  "timestamp": "2026-04-13T10:01:00.000Z",
  "severity": "INFO",
  "trace_id": "trace-abc123",
  "task_id": "task-def456",
  "edge": {
    "from_agent": "agent-A",
    "to_agent": "agent-B",
    "edge_id": "edge-abcd1234",
    "depth": 0
  },
  "graph_state": {
    "total_edges": 1,
    "total_nodes": 2
  }
}
```

---

## 6. 예외 처리 정책 표

| # | 예외 유형 | LOCK 근거 | 트리거 조건 | 자동 대응 | 에스컬레이션 경로 | 심각도 |
|---|----------|----------|-----------|----------|----------------|:------:|
| E-1 | `InfiniteLoopDetected` | LOCK-AT-003 | record_edge()에서 순환 경로 탐지 (DFS로 to_agent에서 from_agent 도달 가능) | 위임 거부 + 전체 체인 스냅샷 로그 + 해당 trace 태스크 취소 | Lead Agent -> 경로 재설계 또는 태스크 종료 결정 | CRITICAL |
| E-2 | `SelfDelegationDenied` | LOCK-AT-003 | record_edge()에서 from_agent == to_agent 감지 | 즉시 거부 + 에러 로그 | Lead Agent -> 다른 에이전트로 재위임 | HIGH |
| E-3 | `MessageLoopDetected` | LOCK-AT-003 | check_message_pattern()에서 동일 패턴 반복 >= MESSAGE_LOOP_THRESHOLD (3) | 메시지 차단 + 패턴 정보 로그 | Lead Agent -> 통신 경로 재설계 | HIGH |
| E-4 | 간접 순환 + 깊이 초과 동시 | LOCK-AT-003, AT-004 | 순환 위임이 깊이 상한과 동시 위반 | InfiniteLoopDetected 우선 (순환이 깊이보다 위험) | Lead Agent -> 양쪽 위반 정보 포함 에스컬레이션 | CRITICAL |
| E-5 | 순환 + 비용 상한 동시 | LOCK-AT-003, AT-011 | 순환 감지 시점에 비용 상한도 도달 | 비용 차단 우선 (AT-011) -> 순환 정보 보조 기록 | Lead Agent -> CostTracker + LoopDetector 양쪽 에스컬레이션 | CRITICAL |
| E-6 | trace 초기화 실패 | LOCK-AT-007 | reset_trace()에서 존재하지 않는 trace_id 시도 | 0 반환 (no-op) + 경고 로그 | 없음 (정상 동작) | LOW |
| E-7 | DelegationChain 연동 실패 | LOCK-AT-003 | P1-06 check_circular()에서 LoopDetector 호출 시 예외 전파 | CircularDelegationDetected로 래핑하여 상위 전파 | DelegationChain 호출자 -> Lead Agent | HIGH |

---

## 7. Phase 2 테스트 케이스

### 7.1 통합 테스트 시나리오 (14건)

| # | 테스트 ID | 시나리오 | 기대 결과 | 검증 LOCK | 우선순위 |
|---|----------|---------|----------|----------|:-------:|
| 1 | `TC-LD-001` | 자기 위임 차단 -- Agent A가 자기 자신에게 위임 시도 | SelfDelegationDenied 발생, agent_id와 task_id 일치 | AT-003 | P0 |
| 2 | `TC-LD-002` | 직접 순환 차단 -- A->B 등록 후 B->A 시도 | InfiniteLoopDetected 발생, cycle_path=["B", "A", "B"] 또는 동등, loop_type=DIRECT_CYCLE | AT-003 | P0 |
| 3 | `TC-LD-003` | 간접 순환 차단 (3단계) -- A->B->C 등록 후 C->A 시도 | InfiniteLoopDetected 발생, cycle_path에 A,B,C,A 포함, loop_type=INDIRECT_CYCLE | AT-003 | P0 |
| 4 | `TC-LD-004` | 정상 위임 경로 -- A->B->C (순환 없음) | 3개 간선 정상 등록, detect_cycle() 모두 None | AT-003 | P0 |
| 5 | `TC-LD-005` | 메시지 루프 감지 -- 동일 패턴 3회 반복 | MessageLoopDetected 발생, count=3, threshold=3 | AT-003 | P0 |
| 6 | `TC-LD-006` | 메시지 패턴 안전 -- 동일 패턴 2회 (임계값 미만) | 정상 반환 True, 예외 없음 | AT-003 | P0 |
| 7 | `TC-LD-007` | 에스컬레이션 페이로드 완전성 | LoopEscalationPayload 전체 필수 필드 비어있지 않음 | -- | P0 |
| 8 | `TC-LD-008` | 스냅샷 정확성 -- 간선 등록 후 스냅샷 내 간선 수 일치 | get_snapshot() 반환값의 total_edges == 등록 간선 수 | AT-007 | P0 |
| 9 | `TC-LD-009` | trace 초기화 -- reset_trace() 후 빈 상태 확인 | reset_trace() 반환값 == 이전 간선 수, 이후 get_snapshot()에서 0개 간선 | AT-007 | P0 |
| 10 | `TC-LD-010` | 독립 trace 격리 -- trace_id A의 간선이 trace_id B에 영향 없음 | 각 trace 독립 관리 확인 | AT-007 | P0 |
| 11 | `TC-LD-011` | DelegationChain 연동 -- check_circular() 호출 시 detect_cycle() 결과 일치 | P1-06 CircularDelegationDetected와 P1-13 InfiniteLoopDetected 동일 순환 경로 | AT-003, AT-004 | P1 |
| 12 | `TC-LD-012` | 4단계 간접 순환 -- A->B->C->D 등록 후 D->A 시도 | InfiniteLoopDetected 발생, cycle_path 길이 5 (A,B,C,D,A) | AT-003 | P1 |
| 13 | `TC-LD-013` | 분기 그래프 순환 -- A->B, A->C, B->D, C->D 등록 후 D->A 시도 | InfiniteLoopDetected 발생, 순환 경로에 A 포함 | AT-003 | P1 |
| 14 | `TC-LD-014` | get_cycle_path() 빈 결과 -- 순환 없는 그래프에서 호출 | 빈 리스트 반환 | -- | P1 |

### 7.2 pytest 테스트 스켈레톤

```python
import pytest


# --- TC-LD-001: 자기 위임 차단 ---
def test_self_delegation_blocked():
    """Agent A가 자기 자신에게 위임 시도 시 SelfDelegationDenied."""
    detector = LoopDetector()
    with pytest.raises(SelfDelegationDenied) as exc_info:
        detector.record_edge(
            from_agent="agent-A", to_agent="agent-A",
            trace_id="trace-001", task_id="task-001",
        )
    assert exc_info.value.agent_id == "agent-A"
    assert exc_info.value.task_id == "task-001"


# --- TC-LD-002: 직접 순환 차단 ---
def test_direct_cycle_blocked():
    """A->B 등록 후 B->A 시도 시 InfiniteLoopDetected."""
    detector = LoopDetector()
    detector.record_edge(
        from_agent="agent-A", to_agent="agent-B",
        trace_id="trace-002", task_id="task-002",
    )
    with pytest.raises(InfiniteLoopDetected) as exc_info:
        detector.record_edge(
            from_agent="agent-B", to_agent="agent-A",
            trace_id="trace-002", task_id="task-002",
        )
    assert exc_info.value.loop_type == LoopType.DIRECT_CYCLE
    assert "agent-A" in exc_info.value.cycle_path
    assert "agent-B" in exc_info.value.cycle_path
    assert exc_info.value.snapshot is not None


# --- TC-LD-003: 간접 순환 차단 (3단계) ---
def test_indirect_cycle_3_step_blocked():
    """A->B->C 등록 후 C->A 시도 시 InfiniteLoopDetected."""
    detector = LoopDetector()
    detector.record_edge(
        from_agent="agent-A", to_agent="agent-B",
        trace_id="trace-003", task_id="task-003",
    )
    detector.record_edge(
        from_agent="agent-B", to_agent="agent-C",
        trace_id="trace-003", task_id="task-003",
    )
    with pytest.raises(InfiniteLoopDetected) as exc_info:
        detector.record_edge(
            from_agent="agent-C", to_agent="agent-A",
            trace_id="trace-003", task_id="task-003",
        )
    assert exc_info.value.loop_type == LoopType.INDIRECT_CYCLE
    cycle = exc_info.value.cycle_path
    # A, B, C, A가 경로에 포함
    assert cycle[0] == "agent-C"
    assert cycle[-1] == "agent-C"
    assert len(cycle) >= 4  # C, A, B, C


# --- TC-LD-004: 정상 위임 경로 (순환 없음) ---
def test_normal_delegation_no_cycle():
    """A->B->C 순차 위임 시 순환 없이 정상 등록."""
    detector = LoopDetector()
    edge1 = detector.record_edge(
        from_agent="agent-A", to_agent="agent-B",
        trace_id="trace-004", task_id="task-004",
    )
    edge2 = detector.record_edge(
        from_agent="agent-B", to_agent="agent-C",
        trace_id="trace-004", task_id="task-004",
    )
    assert edge1.from_agent == "agent-A"
    assert edge2.to_agent == "agent-C"
    snapshot = detector.get_snapshot("trace-004")
    assert snapshot.total_edges == 2
    assert snapshot.total_nodes == 3


# --- TC-LD-005: 메시지 루프 감지 ---
def test_message_loop_detected():
    """동일 패턴 3회 반복 시 MessageLoopDetected."""
    detector = LoopDetector()
    detector.check_message_pattern(
        from_agent="agent-A", to_agent="agent-B",
        topic="task_result", trace_id="trace-005",
    )
    detector.check_message_pattern(
        from_agent="agent-A", to_agent="agent-B",
        topic="task_result", trace_id="trace-005",
    )
    with pytest.raises(MessageLoopDetected) as exc_info:
        detector.check_message_pattern(
            from_agent="agent-A", to_agent="agent-B",
            topic="task_result", trace_id="trace-005",
        )
    assert exc_info.value.pattern.count == 3
    assert exc_info.value.threshold == 3


# --- TC-LD-006: 메시지 패턴 안전 (임계값 미만) ---
def test_message_pattern_safe():
    """동일 패턴 2회 (임계값 미만) 시 정상 반환."""
    detector = LoopDetector()
    result1 = detector.check_message_pattern(
        from_agent="agent-A", to_agent="agent-B",
        topic="status_check", trace_id="trace-006",
    )
    result2 = detector.check_message_pattern(
        from_agent="agent-A", to_agent="agent-B",
        topic="status_check", trace_id="trace-006",
    )
    assert result1 is True
    assert result2 is True


# --- TC-LD-007: 에스컬레이션 페이로드 완전성 ---
def test_escalation_payload_completeness():
    """LoopEscalationPayload 전체 필드 비어있지 않음."""
    detector = LoopDetector()
    detector.record_edge(
        from_agent="agent-A", to_agent="agent-B",
        trace_id="trace-007", task_id="task-007",
    )
    edge = DelegationEdge(
        from_agent="agent-B", to_agent="agent-A",
        trace_id="trace-007", task_id="task-007",
    )
    payload = detector.build_escalation_payload(
        loop_type=LoopType.DIRECT_CYCLE,
        cycle_path=["agent-B", "agent-A", "agent-B"],
        triggering_edge=edge,
    )
    assert payload.trace_id
    assert payload.escalation_id
    assert payload.task_id
    assert payload.detection_id
    assert payload.loop_type == "direct_cycle"
    assert payload.cycle_path
    assert payload.snapshot
    assert payload.triggering_edge
    assert payload.reason
    assert payload.severity == "CRITICAL"


# --- TC-LD-008: 스냅샷 정확성 ---
def test_snapshot_accuracy():
    """간선 등록 후 스냅샷 내 간선 수 일치."""
    detector = LoopDetector()
    detector.record_edge(
        from_agent="agent-A", to_agent="agent-B",
        trace_id="trace-008", task_id="task-008",
    )
    detector.record_edge(
        from_agent="agent-B", to_agent="agent-C",
        trace_id="trace-008", task_id="task-008",
    )
    snapshot = detector.get_snapshot("trace-008")
    assert snapshot.total_edges == 2
    assert snapshot.total_nodes == 3
    assert len(snapshot.all_edges) == 2


# --- TC-LD-009: trace 초기화 ---
def test_trace_reset():
    """reset_trace() 후 빈 상태 확인."""
    detector = LoopDetector()
    detector.record_edge(
        from_agent="agent-A", to_agent="agent-B",
        trace_id="trace-009", task_id="task-009",
    )
    detector.record_edge(
        from_agent="agent-B", to_agent="agent-C",
        trace_id="trace-009", task_id="task-009",
    )
    removed = detector.reset_trace("trace-009")
    assert removed == 2
    snapshot = detector.get_snapshot("trace-009")
    assert snapshot.total_edges == 0
    assert snapshot.total_nodes == 0


# --- TC-LD-010: 독립 trace 격리 ---
def test_independent_trace_isolation():
    """trace_id A의 간선이 trace_id B에 영향 없음."""
    detector = LoopDetector()
    detector.record_edge(
        from_agent="agent-A", to_agent="agent-B",
        trace_id="trace-010a", task_id="task-010a",
    )
    detector.record_edge(
        from_agent="agent-B", to_agent="agent-C",
        trace_id="trace-010b", task_id="task-010b",
    )
    # trace-010a에서 B->A는 순환이지만, trace-010b에서는 A 미등록
    with pytest.raises(InfiniteLoopDetected):
        detector.record_edge(
            from_agent="agent-B", to_agent="agent-A",
            trace_id="trace-010a", task_id="task-010a",
        )
    # trace-010b에서는 C->A 정상 (A가 trace-010b에 없으므로 순환 아님)
    edge = detector.record_edge(
        from_agent="agent-C", to_agent="agent-A",
        trace_id="trace-010b", task_id="task-010b",
    )
    assert edge.to_agent == "agent-A"


# --- TC-LD-011: DelegationChain 연동 ---
def test_delegation_chain_integration():
    """check_circular()와 detect_cycle() 결과 일치 검증.

    P1-06 DelegationChain.check_circular()가 LoopDetector.detect_cycle()에 위임하여
    동일 순환 경로를 반환하는지 확인.
    """
    detector = LoopDetector()
    detector.record_edge(
        from_agent="lead", to_agent="research-001",
        trace_id="trace-011", task_id="task-011",
    )
    # detect_cycle 직접 호출 -- 순환 없음 확인
    result = detector.detect_cycle(
        from_agent="research-001", to_agent="coding-001",
        trace_id="trace-011",
    )
    assert result is None

    detector.record_edge(
        from_agent="research-001", to_agent="coding-001",
        trace_id="trace-011", task_id="task-011",
    )
    # coding-001 -> lead 시 순환 감지
    cycle = detector.detect_cycle(
        from_agent="coding-001", to_agent="lead",
        trace_id="trace-011",
    )
    assert cycle is not None
    assert "lead" in cycle


# --- TC-LD-012: 4단계 간접 순환 ---
def test_indirect_cycle_4_step():
    """A->B->C->D 등록 후 D->A 시도 시 InfiniteLoopDetected."""
    detector = LoopDetector()
    detector.record_edge("agent-A", "agent-B", "trace-012", "task-012")
    detector.record_edge("agent-B", "agent-C", "trace-012", "task-012")
    detector.record_edge("agent-C", "agent-D", "trace-012", "task-012")
    with pytest.raises(InfiniteLoopDetected) as exc_info:
        detector.record_edge("agent-D", "agent-A", "trace-012", "task-012")
    assert exc_info.value.loop_type == LoopType.INDIRECT_CYCLE
    assert len(exc_info.value.cycle_path) >= 5  # D, A, B, C, D


# --- TC-LD-013: 분기 그래프 순환 ---
def test_branching_graph_cycle():
    """A->B, A->C, B->D, C->D 등록 후 D->A 시도."""
    detector = LoopDetector()
    detector.record_edge("agent-A", "agent-B", "trace-013", "task-013")
    detector.record_edge("agent-A", "agent-C", "trace-013", "task-013")
    detector.record_edge("agent-B", "agent-D", "trace-013", "task-013")
    detector.record_edge("agent-C", "agent-D", "trace-013", "task-013")
    with pytest.raises(InfiniteLoopDetected) as exc_info:
        detector.record_edge("agent-D", "agent-A", "trace-013", "task-013")
    assert "agent-A" in exc_info.value.cycle_path


# --- TC-LD-014: get_cycle_path() 빈 결과 ---
def test_get_cycle_path_empty():
    """순환 없는 그래프에서 get_cycle_path() 호출 시 빈 리스트."""
    detector = LoopDetector()
    detector.record_edge("agent-A", "agent-B", "trace-014", "task-014")
    detector.record_edge("agent-B", "agent-C", "trace-014", "task-014")
    path = detector.get_cycle_path("trace-014", "agent-A")
    assert path == []
```

---

## 8. 알고리즘 시간복잡도 + LOCK + ABC 요약

| 메서드 | ABC 시그니처 | 시간복잡도 | 관련 LOCK |
|--------|------------|-----------|----------|
| `record_edge()` | `record_edge(from_agent, to_agent, trace_id, task_id) -> DelegationEdge` | O(n) -- n = visited nodes in trace | AT-003 |
| `detect_cycle()` | `detect_cycle(from_agent, to_agent, trace_id) -> Optional[list[str]]` | O(n) -- n = total nodes reachable from to_agent | AT-003 |
| `has_self_loop()` | `has_self_loop(from_agent, to_agent) -> bool` | O(1) | AT-003 |
| `check_message_pattern()` | `check_message_pattern(from_agent, to_agent, topic, trace_id) -> bool` | O(1) -- 해시 조회 + 카운터 증가 | AT-003 |
| `get_snapshot()` | `get_snapshot(trace_id) -> LoopDetectionSnapshot` | O(e) -- e = total edges in trace | AT-007 |
| `get_cycle_path()` | `get_cycle_path(trace_id, start_agent) -> list[str]` | O(n) -- n = nodes in reachable graph | AT-003 |
| `reset_trace()` | `reset_trace(trace_id) -> int` | O(e) -- e = edges in trace | AT-007 |
| `build_escalation_payload()` | `build_escalation_payload(loop_type, cycle_path, triggering_edge) -> LoopEscalationPayload` | O(e) -- e = total edges (스냅샷 생성) | AT-003, AT-002 |

---

## 9. 세션간 인터페이스 cross-check

| 인접 세션 | 인터페이스 | 본 세션 사용 방식 | 정합성 |
|----------|-----------|-----------------|:------:|
| P1-01 (Lead Agent) | `LeadAgent.decide()` | 순환 차단 후 Lead가 LoopEscalationPayload 기반 최종 결과 확정 (LOCK-AT-002) | OK |
| P1-04 (Sequential) | `SequentialPipeline` | 파이프라인 단계 간 위임 시 record_edge() 호출하여 순환 사전 검증 | OK |
| P1-05 (Parallel) | `ParallelDispatcher.dispatch()` | 병렬 위임 시 InfiniteLoopDetected 예외 발생하면 전체 배치 취소 | OK |
| P1-06 (Delegation) | `DelegationChain.check_circular()` | P1-06의 check_circular()에서 P1-13 detect_cycle()로 위임 가능. CircularDelegationDetected와 InfiniteLoopDetected 동일 순환 경로 | OK |
| P1-07 (MessageBus) | `InMemoryMessageBus.publish()` | "무한 루프 감지: 동일 패턴 3회+ 반복 -> 경고 로그 (차단은 LoopDetector P1-13 담당)" -- check_message_pattern() 연동 | OK |
| P1-09 (Execute Tool) | `PhaseGuard.check_tool_call()` | LoopDetector와 독립 -- 상호 간섭 없음. 각자 LOCK 영역 담당 | OK |
| P1-10 (Turn Limit) | `ConversationTracker.increment_turn()` | 3차 방어선으로 독립 관리. LoopDetector가 2차 방어선 | OK |
| P1-11 (TEE Loop) | `TEELoop.start_iteration()` | 1차 방어선(반복 카운터)과 2차 방어선(순환 탐지) 독립 관리. "LoopDetector -- 무한 루프 감지 보조" 인터페이스 예약 해소 | OK |
| P1-12 (Cost Tracker) | `CostTracker.record_cost()` | 보조 방어선으로 독립 관리. 비용 폭주 시 보조 차단. R-63-5 연계 | OK |
| P1-14 (Trace Manager) | `TraceManager` (예정) | LOCK-AT-007 trace_id 관리 위임 -- 현재 trace_id는 파라미터로 전달 | OK (인터페이스 예약) |

---

## 10. 공통 자료 구조 선정의

### 10.1 본 세션 신규 정의

| 자료 구조 | 용도 | 재사용 가능 세션 |
|----------|------|----------------|
| `LoopType` (Enum) | 순환 위임 유형 분류 (SELF/DIRECT/INDIRECT/MESSAGE) | P1-06 (DelegationChain 순환 유형 분류), Phase 2 감사 로그 |
| `DelegationEdge` (dataclass) | 위임 경로 그래프 간선 | P1-06 (DelegationChain 간선 추적), P1-14 (Checkpoint 간선 목록) |
| `LoopDetectionSnapshot` (dataclass) | 순환 감지 시 전체 경로 스냅샷 | P1-01 (Lead 에스컬레이션), P1-14 (Checkpoint), Phase 2 포렌식 |
| `MessagePattern` (dataclass) | 메시지 반복 패턴 추적 | P1-07 (MessageBus 패턴 감지 연동) |
| `LoopEscalationPayload` (dataclass) | 무한 루프 에스컬레이션 페이로드 | P1-01 (Lead Agent 에스컬레이션 처리) |

### 10.2 참조 자료 구조 (타 세션 정의)

| 자료 구조 | 원본 | 본 세션 참조 방식 |
|----------|------|----------------|
| `AgentRole` (Enum) | P1-01 §3.1 | 위임 간선의 에이전트 역할 식별 |
| `EscalationPayload` (dataclass) | P1-01 §3.1 | LoopEscalationPayload 기반 구조 |
| `DelegationNode` (dataclass) | P1-06 §3.1 | 위임 체인 노드 참조 -- LoopDetector가 간선 레벨로 추적 |
| `DelegationChainSnapshot` (dataclass) | P1-06 §3.1 | 순환 감지 시 체인 스냅샷 보완 참조 |
| `CircularDelegationDetected` (Exception) | P1-06 §3.2 | P1-06의 순환 감지 예외 -- LoopDetector InfiniteLoopDetected와 대응 |

---

## 변경 이력

| 일자 | 변경 내용 | 세션 |
|------|----------|------|
| 2026-04-13 | 초기 작성 -- LoopDetector 클래스 스켈레톤, LoopType/DelegationEdge/LoopDetectionSnapshot/MessagePattern/LoopEscalationPayload 자료 구조 5종, InfiniteLoopDetected/SelfDelegationDenied/MessageLoopDetected 예외 3종, Phase별 복구 전략 + 에스컬레이션 흐름도, 로깅 JSON 4종, 예외 처리 정책 7건, 테스트 14건(TC-LD-001~014), 세션간 인터페이스 10건 cross-check | P1-13 |
| 2026-04-13 | Step 2 재검증 수정 1건: detect_cycle() DFS 반환값 버그 수정 -- `return path + [from_agent]`가 경로 마지막 노드를 중복 추가하여 cycle_path 길이가 1 초과, DIRECT_CYCLE(len==3) 판별 실패 유발 -> `return list(path)`로 교정 (path 자체가 이미 순환 경로 완성 형태) | P1-13 Step2 |

---

> **문서 끝**
> 본 문서는 P1-13 세션 산출물이며, LOCK-AT-003(에이전트 간 자유 상호 호출 / 무한 대화 루프 금지) 정본을 기반으로 작성되었습니다.
