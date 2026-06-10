# P1-10. 대화 턴 상한 (P0=5) — ConversationTracker 클래스 및 강제 종료 검증

> **도메인**: 6-3_Agent-Teams-PARL / 03_team-composition
> **세션**: P1-10
> **작성일**: 2026-04-13
> **대조 기준**: Part2 §6.7 대화 턴 제한, D2.0-05 §12.4.4 AutoGen Conversation 패턴, LOCK-AT-009(턴상한 P0=5)
> **선행 산출물**: P1-01_lead_agent_definition.md (P1-1), P1-04_sequential_pattern.md (P1-4), P1-05_parallel_pattern.md (P1-5), P1-06_delegation_chain.md (P1-6), P1-07_in_memory_messagebus.md (P1-7)

---

## 1. 교차 참조 블록

| 문서 | 참조 위치 | 역할 |
|------|----------|------|
| D2.0-05 Agent Workflow | §12.4.4 AutoGen Conversation 패턴 | 대화 턴 상한 정본 근거 — "대화 턴 상한: P0=5턴, P1=10턴, P2=20턴" |
| D2.0-05 Agent Workflow | §7.3 L381 | 무한 루프 대화 금지 (LOCK-AT-003 연계) |
| D2.0-02 ORANGE CORE | §2.2 S3 Decision Locked | Lead Agent 단일결정 원칙 — 강제 종료 시 Lead가 결과 요약 확정 |
| D2.0-07 Safety/Cost/Approval | §Cost_Control | 비용 상한과 턴 상한 이중 안전장치 연계 |
| Part2 §6.7 | L5047 (LOCK-AT-009) | LOCK 값 선언 정본: "대화 턴 상한: P0=5, P1=10, P2=20" |
| Part2 §6.7 | L4994-5130 | 구현 요건 정본 (17 LOCK-AT) |
| Part2 §6.7 | L5060 | P-level 턴 제한 vs 세션 max_turns 관계 — 단일 액션 내 턴 상한 |
| AUTHORITY_CHAIN.md | §2.1 레지스트리 | LOCK-AT 17건 레지스트리 정본 (AT-009 위반 시 "5턴에서 자동 종료") |
| 종합계획서 §7.3 | P1-10 세부 항목 | 본 세션 작업 정의 |
| 종합계획서 §1.4 | Part2 핵심 내용 요약 | "대화 턴 상한: P0=5, P1=10, P2=20 (LOCK-AT-009)" |
| 종합계획서 부록 §C.1 | LOCK-AT-009 위반 시나리오 | "P0 대화 6턴 시도 → 턴 카운터 → 5턴에서 자동 종료" |
| P1-01_lead_agent_definition.md | §3 LeadAgent 클래스 | Lead Agent가 강제 종료 시 결과 요약 확정 (LOCK-AT-002) |
| P1-04_sequential_pattern.md | §9 인터페이스 | "P1-10 ConversationTracker max_turns=5 (P0) — 파이프라인 전체 턴 수 제한 참조" |
| P1-06_delegation_chain.md | §3 DelegationChain | 위임 체인 내 턴 카운트 전파 참조 |
| P1-07_in_memory_messagebus.md | §3 InMemoryMessageBus | 메시지 교환 시 턴 카운트 증가 트리거 |
| **인접 도메인** | | |
| 3-8 Conversation-A2A | A2A 프로토콜 규격 | 대화 턴 메시지 포맷 소비 (재정의 금지) |
| 3-10 Agent-Protocol | L0-L4 자율성 정의 | Agent 자율성 레벨 배정 참조 (재정의 금지) |
| 6-2 Security-Governance | 보안 정책 | 턴 상한 우회 시도 보안 체크리스트 우선 적용 (§9.3) |

---

## 2. 대화 턴 상한 개요

### 2.1 턴 상한 식별

| 속성 | 값 |
|------|-----|
| **모듈 ID** | `ConversationTracker` |
| **도입 버전** | V1 |
| **P0 턴 상한** | 5 (LOCK-AT-009 P0=5) — 하드코딩 |
| **P1 턴 상한** | 10 (LOCK-AT-009 P1=10) — Phase 2 확장 시 적용 |
| **P2 턴 상한** | 20 (LOCK-AT-009 P2=20) — Phase 2 확장 시 적용 |
| **적용 범위** | 단일 액션(task) 내 에이전트 대화 턴 (세션 전체 아님) |
| **세션 관계** | `Sigma(action_turns) <= max_turns_per_session` (V0=50, V2=100) |
| **초과 정책** | `TurnLimitExceeded` 예외 + 강제 종료 + 현재까지 결과 요약 반환 |
| **무한 루프 연계** | LOCK-AT-003 (무한 대화 루프 금지) — ConversationTracker가 1차 방어선 |

### 2.2 LOCK 값 인용

> LOCK-AT-009 (Part2 §6.7 L5047 / D2.0-05 §12.4.4):
> "대화 턴 상한: P0=5, P1=10, P2=20"

> LOCK-AT-003 (Part2 §6.7 L5041 / D2.0-05 §7.3 L381):
> "에이전트 간 자유 상호 호출 / 무한 대화 루프 금지"

> LOCK-AT-002 (Part2 §6.7 L5040 / D2.0-02 §2.2 S3):
> "단일결정 원칙: 최종 결론은 Lead Agent(ORANGE CORE)만 확정"

> LOCK-AT-007 (Part2 §6.7 L5045 / D2.0-05 §7.3):
> "Checkpoint/Replay/Fork는 trace_id 단위로만 허용"

> Part2 §6.7 L5060 (P-level vs 세션 관계):
> "LOCK-AT-009의 P0=5/P1=10/P2=20은 **단일 액션(task) 내** 에이전트 대화 턴 상한이고,
> config.v*.toml의 max_turns_per_session(V0=50, V2=100)은 **전체 세션** 누적 턴 상한.
> 관계: Sigma(action_turns) <= max_turns_per_session."

### 2.3 턴 카운트 규칙

```
턴(turn) 정의:
- Lead Agent가 Worker Agent에게 메시지를 보내고(request),
  Worker Agent가 응답(response)을 반환하는 **1회 왕복** = 1턴.
- Lead → Worker 메시지만 턴 카운트 증가 (Worker 내부 처리는 미포함).

P-level 적용:
- P0 (Phase 0/1 기본): max_turns = 5
- P1 (Phase 2 확장):   max_turns = 10
- P2 (Phase 2 고급):   max_turns = 20

세션 관계:
- 세션 내 여러 액션이 각각 P-level 상한 준수
- 세션 전체: Sigma(action_turns) <= max_turns_per_session
```

---

## 3. ConversationTracker 클래스 스켈레톤

### 3.1 공통 자료 구조 (§7 공통 자료 구조 선정의)

```python
from __future__ import annotations
from typing import Any, Optional, Callable, Awaitable
from dataclasses import dataclass, field
from enum import Enum
import uuid
import time
import logging
import json

# ---------------------------------------------------------------------------
# 공통 자료 구조 -- P1-01 공유 (AgentRole, EscalationPayload)
# ---------------------------------------------------------------------------
# 아래 구조는 P1-01_lead_agent_definition.md §3.1에서 정의된 것을 재사용.
# 여기서는 대화 턴 상한에 필요한 추가 구조만 정의.

# --- P1-01 참조: AgentRole(9종), DelegationMessage, DecisionResult,
#     EscalationPayload, TaskStatus --- (import 가정)


class TurnPhaseLevel(Enum):
    """P-level 턴 상한 등급.

    LOCK-AT-009: P0=5, P1=10, P2=20.
    Part2 §6.7 L5060: 단일 액션(task) 내 에이전트 대화 턴 상한.
    """
    P0 = 5    # Phase 0/1 기본
    P1 = 10   # Phase 2 확장
    P2 = 20   # Phase 2 고급


@dataclass
class TurnRecord:
    """단일 턴(대화 왕복) 기록.

    Lead → Worker 요청 + Worker → Lead 응답 = 1턴.
    """
    turn_number: int
    trace_id: str
    action_id: str
    sender_id: str          # 요청 발신자 (Lead Agent ID)
    receiver_id: str        # 응답자 (Worker Agent ID)
    request_summary: str    # 요청 요약 (로깅용)
    response_summary: str = ""   # 응답 요약 (완료 후 기록)
    started_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    duration_ms: Optional[float] = None
    is_final: bool = False  # 마지막 턴 여부


@dataclass
class ConversationSnapshot:
    """대화 세션 전체 스냅샷.

    강제 종료 시 Lead Agent에 전달하여 결과 요약 생성에 사용.
    LOCK-AT-007: trace_id 단위로만 Checkpoint/Replay 허용.
    """
    trace_id: str
    action_id: str
    conversation_id: str
    turns: list[TurnRecord] = field(default_factory=list)
    total_turns: int = 0
    max_allowed_turns: int = 5    # LOCK-AT-009 P0 기본값
    phase_level: str = "P0"
    is_terminated: bool = False
    termination_reason: Optional[str] = None
    partial_results: list[dict[str, Any]] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    terminated_at: Optional[float] = None


@dataclass
class TurnLimitEscalationPayload:
    """턴 상한 초과 시 에스컬레이션 페이로드.

    EscalationPayload (P1-01 §3.1)를 확장하여 대화 턴 컨텍스트 포함.
    강제 종료 시 Lead Agent에 전달.
    """
    trace_id: str
    escalation_id: str
    action_id: str
    conversation_id: str
    violation_type: str          # "TURN_LIMIT_EXCEEDED"
    conversation_snapshot: ConversationSnapshot
    current_turn: int
    max_allowed_turn: int
    phase_level: str             # "P0" | "P1" | "P2"
    partial_results_summary: str  # 강제 종료 시점까지 결과 요약
    sender_id: str               # 마지막 요청 발신자
    receiver_id: str             # 마지막 응답 대상
    reason: str
    error_context: dict[str, Any] = field(default_factory=dict)
    severity: str = "HIGH"
    created_at: float = field(default_factory=time.time)
```

### 3.2 예외 클래스 정의

```python
class TurnLimitExceeded(Exception):
    """LOCK-AT-009 위반: 대화 턴 상한 초과 시 발생.

    P0=5, P1=10, P2=20.
    강제 종료 + 현재까지 결과 요약 반환.
    종합계획서 부록 §C.1: "P0 대화 6턴 시도 → 턴 카운터 → 5턴에서 자동 종료"
    """

    def __init__(self, current_turn: int, max_turns: int,
                 conversation_snapshot: Optional[ConversationSnapshot] = None,
                 phase_level: str = "P0"):
        self.current_turn = current_turn
        self.max_turns = max_turns
        self.conversation_snapshot = conversation_snapshot
        self.phase_level = phase_level
        super().__init__(
            f"LOCK-AT-009: Turn limit exceeded — "
            f"attempted_turn={current_turn + 1}, max_turns={max_turns} ({phase_level}). "
            f"Forced termination with partial results summary."
        )


class ConversationAlreadyTerminated(Exception):
    """이미 종료된 대화 세션에 턴 추가 시도 시 발생.

    강제 종료 후 추가 메시지 교환 차단 — LOCK-AT-003 무한 루프 방지 보완.
    """

    def __init__(self, conversation_id: str, termination_reason: str):
        self.conversation_id = conversation_id
        self.termination_reason = termination_reason
        super().__init__(
            f"Conversation {conversation_id} already terminated: {termination_reason}. "
            f"LOCK-AT-003: No further turns allowed."
        )
```

### 3.3 ConversationTracker 인터페이스 정의

```python
class ConversationTracker:
    """Agent 간 대화 턴 상한 관리자.

    LOCK-AT-009: 대화 턴 상한 P0=5, P1=10, P2=20 — 하드코딩.
    LOCK-AT-003: 무한 대화 루프 금지 — ConversationTracker가 1차 방어선.
    LOCK-AT-002: 강제 종료 시 Lead Agent(ORANGE CORE)만 결과 요약 확정.
    LOCK-AT-007: trace_id 단위로 Checkpoint/Replay 허용.

    시간복잡도:
      - increment_turn(): O(1) 상수 시간 (턴 카운터 증가 + 상한 비교)
      - get_snapshot(): O(t) where t = total turns (턴 기록 복사)
      - force_terminate(): O(t) where t = total turns (스냅샷 생성 포함)
      - get_remaining_turns(): O(1) 상수 시간
      - is_within_limit(): O(1) 상수 시간

    ABC 시그니처:
      increment_turn(sender_id, receiver_id, request_summary, trace_id) -> TurnRecord
      complete_turn(turn_number, response_summary, partial_result) -> TurnRecord
      force_terminate(reason) -> ConversationSnapshot
      get_snapshot() -> ConversationSnapshot
      get_remaining_turns() -> int
      is_within_limit() -> bool
    """

    # LOCK-AT-009: P0=5 하드코딩. Phase 2 확장 시 P1=10, P2=20으로 교체.
    MAX_TURNS_P0: int = 5

    def __init__(self,
                 action_id: str,
                 trace_id: str,
                 phase_level: TurnPhaseLevel = TurnPhaseLevel.P0,
                 logger: Optional[logging.Logger] = None) -> None:
        """
        Args:
            action_id: 현재 액션(task) ID — 턴 상한 적용 단위.
            trace_id: 실행 추적 ID (LOCK-AT-007).
            phase_level: P-level 등급 (P0/P1/P2). 기본값 P0.
            logger: 로깅 인스턴스.

        세션간 인터페이스 cross-check:
          - P1-01: LeadAgent — 강제 종료 시 decide()로 결과 요약 확정
          - P1-04: SequentialPipeline — 파이프라인 각 단계별 턴 카운트 참조
          - P1-05: ParallelDispatcher — 병렬 태스크 각각 독립 ConversationTracker
          - P1-06: DelegationChain — 위임 체인 내 턴 카운트 전파
          - P1-07: InMemoryMessageBus — 메시지 교환 시 턴 카운트 트리거
          - P1-11: TEELoop — TEE 반복과 턴 상한 독립 관리 (이중 안전장치)
          - P1-12: CostTracker — 비용 상한과 턴 상한 동시 모니터링
          - P1-13: LoopDetector — 무한 루프 감지 보조 (LOCK-AT-003 연계)
        """
        self._action_id = action_id
        self._trace_id = trace_id
        self._phase_level = phase_level
        self._max_turns = phase_level.value  # P0=5, P1=10, P2=20
        self._conversation_id = f"conv-{uuid.uuid4().hex[:12]}"
        self._turns: list[TurnRecord] = []
        self._current_turn: int = 0
        self._is_terminated: bool = False
        self._termination_reason: Optional[str] = None
        self._partial_results: list[dict[str, Any]] = []
        self._logger = logger or logging.getLogger("conversation_tracker")

    # ---------- 핵심 메서드 ----------

    def increment_turn(self, sender_id: str, receiver_id: str,
                       request_summary: str,
                       trace_id: Optional[str] = None) -> TurnRecord:
        """새 턴을 시작한다 (Lead → Worker 메시지 전송 시 호출).

        1. 종료 상태 확인 — 이미 종료된 대화면 차단.
        2. 턴 상한 검사 (LOCK-AT-009) — 초과 시 강제 종료.
        3. 턴 카운터 증가 + TurnRecord 생성.

        Args:
            sender_id: 요청 발신자 ID (보통 Lead Agent).
            receiver_id: 응답 대상 Worker Agent ID.
            request_summary: 요청 요약 (로깅용).
            trace_id: 추적 ID. None이면 초기화 시 설정된 trace_id 사용.

        Returns:
            TurnRecord: 생성된 턴 기록.

        Raises:
            ConversationAlreadyTerminated: 이미 종료된 대화.
            TurnLimitExceeded: LOCK-AT-009 턴 상한 초과.

        시간복잡도: O(1) 상수 시간
        """
        # 1. 종료 상태 확인
        if self._is_terminated:
            self._logger.warning(
                "LOCK-AT-003: Attempted turn on terminated conversation — "
                "conversation_id=%s, reason=%s",
                self._conversation_id, self._termination_reason,
            )
            raise ConversationAlreadyTerminated(
                conversation_id=self._conversation_id,
                termination_reason=self._termination_reason or "unknown",
            )

        # 2. 턴 상한 검사 — 현재 턴 수가 max_turns에 도달하면 차단
        if self._current_turn >= self._max_turns:
            self._logger.error(
                "LOCK-AT-009 VIOLATED: Turn limit exceeded — "
                "attempted_turn=%d, max_turns=%d (%s), "
                "trace_id=%s, action_id=%s, sender=%s, receiver=%s",
                self._current_turn + 1, self._max_turns,
                self._phase_level.name,
                self._trace_id, self._action_id,
                sender_id, receiver_id,
            )

            # 강제 종료 + 현재까지 결과 요약 반환
            snapshot = self.force_terminate(
                reason=f"LOCK-AT-009: Turn {self._current_turn + 1} > "
                       f"max {self._max_turns} ({self._phase_level.name})"
            )

            raise TurnLimitExceeded(
                current_turn=self._current_turn,
                max_turns=self._max_turns,
                conversation_snapshot=snapshot,
                phase_level=self._phase_level.name,
            )

        # 3. 턴 카운터 증가 + 레코드 생성
        self._current_turn += 1
        effective_trace_id = trace_id or self._trace_id

        record = TurnRecord(
            turn_number=self._current_turn,
            trace_id=effective_trace_id,
            action_id=self._action_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            request_summary=request_summary,
        )
        self._turns.append(record)

        self._logger.info(
            "Turn %d/%d started: %s → %s (trace=%s, action=%s)",
            self._current_turn, self._max_turns,
            sender_id, receiver_id,
            effective_trace_id, self._action_id,
        )

        return record

    def complete_turn(self, turn_number: int,
                      response_summary: str,
                      partial_result: Optional[dict[str, Any]] = None
                      ) -> TurnRecord:
        """턴을 완료한다 (Worker → Lead 응답 수신 시 호출).

        Args:
            turn_number: 완료할 턴 번호.
            response_summary: 응답 요약 (로깅용).
            partial_result: 이 턴에서 얻은 부분 결과 (강제 종료 시 보존).

        Returns:
            TurnRecord: 갱신된 턴 기록.

        Raises:
            ValueError: 존재하지 않는 턴 번호.

        시간복잡도: O(1) — 인덱스 접근
        """
        if turn_number < 1 or turn_number > len(self._turns):
            raise ValueError(
                f"Invalid turn_number={turn_number}. "
                f"Valid range: 1~{len(self._turns)}"
            )

        record = self._turns[turn_number - 1]
        record.response_summary = response_summary
        record.completed_at = time.time()
        record.duration_ms = (record.completed_at - record.started_at) * 1000

        if partial_result:
            self._partial_results.append(partial_result)

        # 마지막 턴 자동 표시
        if turn_number == self._max_turns:
            record.is_final = True

        self._logger.info(
            "Turn %d/%d completed: response from %s (duration=%.1fms, trace=%s)",
            turn_number, self._max_turns,
            record.receiver_id, record.duration_ms,
            record.trace_id,
        )

        return record

    def force_terminate(self, reason: str) -> ConversationSnapshot:
        """대화를 강제 종료하고 현재까지 결과 요약을 반환한다.

        LOCK-AT-009: 턴 상한 초과 시 호출.
        LOCK-AT-002: Lead Agent에 ConversationSnapshot을 전달하여
                      결과 요약 확정을 위임.

        Args:
            reason: 종료 사유.

        Returns:
            ConversationSnapshot: 대화 전체 스냅샷 (부분 결과 포함).

        시간복잡도: O(t) where t = total turns
        """
        if self._is_terminated:
            # 멱등성: 이미 종료된 경우 중복 종료/감사 레코드 방지
            return self.get_snapshot()
        if self._is_terminated:
            # 멱등성: 이미 종료된 경우 중복 종료/감사 레코드 방지
            return self.get_snapshot()
        self._is_terminated = True
        self._termination_reason = reason

        snapshot = ConversationSnapshot(
            trace_id=self._trace_id,
            action_id=self._action_id,
            conversation_id=self._conversation_id,
            turns=list(self._turns),
            total_turns=self._current_turn,
            max_allowed_turns=self._max_turns,
            phase_level=self._phase_level.name,
            is_terminated=True,
            termination_reason=reason,
            partial_results=list(self._partial_results),
            terminated_at=time.time(),
        )

        self._logger.warning(
            "Conversation FORCE TERMINATED: conversation_id=%s, "
            "turns=%d/%d, reason=%s, trace_id=%s",
            self._conversation_id, self._current_turn,
            self._max_turns, reason, self._trace_id,
        )

        return snapshot

    def get_snapshot(self) -> ConversationSnapshot:
        """현재 대화 상태의 스냅샷을 반환한다.

        LOCK-AT-007: trace_id 단위로 Checkpoint 가능.

        Returns:
            ConversationSnapshot: 현재 상태 스냅샷.

        시간복잡도: O(t) where t = total turns
        """
        return ConversationSnapshot(
            trace_id=self._trace_id,
            action_id=self._action_id,
            conversation_id=self._conversation_id,
            turns=list(self._turns),
            total_turns=self._current_turn,
            max_allowed_turns=self._max_turns,
            phase_level=self._phase_level.name,
            is_terminated=self._is_terminated,
            termination_reason=self._termination_reason,
            partial_results=list(self._partial_results),
        )

    def get_remaining_turns(self) -> int:
        """남은 턴 수를 반환한다.

        Returns:
            int: max_turns - current_turn. 0이면 상한 도달.

        시간복잡도: O(1) 상수 시간
        """
        return max(0, self._max_turns - self._current_turn)

    def is_within_limit(self) -> bool:
        """현재 턴 수가 상한 이내인지 확인한다.

        Returns:
            bool: True면 추가 턴 가능, False면 상한 도달.

        시간복잡도: O(1) 상수 시간
        """
        return self._current_turn < self._max_turns and not self._is_terminated

    # ---------- 결과 요약 ----------

    def build_partial_results_summary(self) -> str:
        """현재까지 부분 결과를 요약 문자열로 반환한다.

        강제 종료 시 Lead Agent에 전달할 결과 요약.
        LOCK-AT-002: Lead가 이 요약을 기반으로 최종 결론 확정.

        Returns:
            str: 부분 결과 요약 문자열.
        """
        if not self._partial_results:
            return f"[No partial results after {self._current_turn} turns]"

        summaries = []
        for i, result in enumerate(self._partial_results, 1):
            summary = result.get("summary", str(result))
            summaries.append(f"Turn {i}: {summary}")

        return (
            f"Partial results after {self._current_turn}/{self._max_turns} turns "
            f"({self._phase_level.name}):\n"
            + "\n".join(summaries)
        )

    # ---------- 에스컬레이션 ----------

    def build_escalation_payload(self) -> TurnLimitEscalationPayload:
        """턴 상한 초과 에스컬레이션 페이로드를 생성한다.

        Returns:
            TurnLimitEscalationPayload: Lead Agent에 전달할 에스컬레이션 정보.
        """
        snapshot = self.get_snapshot()
        last_turn = self._turns[-1] if self._turns else None

        return TurnLimitEscalationPayload(
            trace_id=self._trace_id,
            escalation_id=f"esc-turn-{uuid.uuid4().hex[:8]}",
            action_id=self._action_id,
            conversation_id=self._conversation_id,
            violation_type="TURN_LIMIT_EXCEEDED",
            conversation_snapshot=snapshot,
            current_turn=self._current_turn,
            max_allowed_turn=self._max_turns,
            phase_level=self._phase_level.name,
            partial_results_summary=self.build_partial_results_summary(),
            sender_id=last_turn.sender_id if last_turn else "unknown",
            receiver_id=last_turn.receiver_id if last_turn else "unknown",
            reason=(
                f"LOCK-AT-009: Turn limit exceeded — "
                f"turns={self._current_turn}, max={self._max_turns} "
                f"({self._phase_level.name})"
            ),
        )
```

---

## 4. Phase별 복구 전략

### 4.1 턴 상한 복구 흐름도

```
[Lead → Worker 메시지 전송]
    │
    ▼
[1. 종료 상태 확인] ──(종료됨)──> [ConversationAlreadyTerminated]
    │                                │
    │ (활성)                         ▼
    ▼                            [LOCK-AT-003 차단]
[2. 턴 상한 검사] ──(초과)──> [TurnLimitExceeded]
    │                           │
    │ (이내)                    ▼
    ▼                       [force_terminate() 호출]
[3. 턴 카운터 증가]             │
    │                           ▼
    ▼                  ┌──────────────────────────┐
[4. TurnRecord 생성]   │ ConversationSnapshot 생성  │
    │                 │ + 부분 결과 요약 반환        │
    ▼                 └──────────────────────────┘
[5. Worker 응답 대기]           │
    │                           ▼
    ▼                  ┌──────────────────────────┐
[6. complete_turn()]   │ Lead Agent에 전달          │
    │                 │ (TurnLimitEscalationPayload)│
    ▼                 └──────────────────────────┘
[턴 성공 완료]                  │
                                ▼
                       [Lead decide() → 결과 요약 확정]
                       [LOCK-AT-002 단일결정 원칙]
```

### 4.2 Phase별 복구 정책

| Phase | 장애 유형 | 복구 전략 | 비고 |
|:-----:|----------|----------|------|
| Phase 0 | P0 턴 상한 초과 (6턴 시도) | 즉시 강제 종료 + `TurnLimitExceeded` + 부분 결과 요약 반환 | max_turns=5 하드코딩 |
| Phase 0 | 종료 후 추가 턴 시도 | 즉시 차단 + `ConversationAlreadyTerminated` | LOCK-AT-003 보완 |
| Phase 0 | 턴 카운터 불일치 (내부 오류) | Checkpoint 기반 스냅샷 저장 + 마지막 유효 상태 복원 | LOCK-AT-007 |
| Phase 1 | P1 턴 상한 확장 (max=10) | config 기반 동적 max_turns 적용 | P-level 기반 확장 |
| Phase 1 | 비용 상한과 턴 상한 동시 도달 | 비용 상한 우선 차단 (LOCK-AT-011) → 턴 상한은 보조 | 이중 안전장치 |
| Phase 2 | P2 턴 상한 확장 (max=20) | config 기반 동적 max_turns 적용 | 세션 max_turns와 조합 |
| Phase 2 | 분산 환경 턴 카운터 동기화 | Redis 기반 턴 카운터 + 원자적 증가 (V2 MessageBus 연동) | InMemoryMessageBus → Redis |
| Phase 2 | 세션 전체 턴 합산 초과 | 세션 레벨 모니터: Sigma(action_turns) > max_turns_per_session → 세션 종료 | V0=50, V2=100 |

### 4.3 에스컬레이션 흐름

```
[턴 상한 초과 감지]
    │
    ▼
[TurnLimitEscalationPayload 생성]
    ├── trace_id, action_id, conversation_id
    ├── violation_type: TURN_LIMIT_EXCEEDED
    ├── conversation_snapshot: 대화 전체 상태 + 부분 결과
    ├── current_turn / max_allowed_turn / phase_level
    └── partial_results_summary: 강제 종료까지 결과 요약
    │
    ▼
[Lead Agent에 전달]
    │
    ├──(결과 충분)──> [Lead Agent decide() — 부분 결과 기반 최종 결론 확정]
    │                    ├── ConversationSnapshot.partial_results 활용
    │                    └── LOCK-AT-002 단일결정: Lead만 최종 확정
    │
    ├──(결과 부족)──> [Lead Agent → 새 액션으로 이관]
    │                    ├── 새 ConversationTracker 생성 (턴 카운터 리셋)
    │                    └── 이전 부분 결과를 초기 컨텍스트로 전달
    │
    └──(처리 불가)──> [사용자 에스컬레이션]
                         ├── 에스컬레이션 ID 포함
                         └── 대화 스냅샷 + 부분 결과 요약
```

---

## 5. 로깅 중첩 JSON 구조

### 5.1 턴 시작 로그

```json
{
  "event": "conversation.turn_started",
  "timestamp": "2026-04-13T10:00:00.000Z",
  "trace_id": "trace-abc123",
  "action_id": "action-def456",
  "conversation_id": "conv-ghi789",
  "turn": {
    "number": 3,
    "max_allowed": 5,
    "remaining": 2,
    "phase_level": "P0",
    "sender_id": "lead-001",
    "receiver_id": "research-001",
    "request_summary": "Gather financial data for AAPL Q4 2025"
  },
  "lock_compliance": {
    "LOCK-AT-009": {"status": "PASS", "turn": 3, "max": 5, "phase": "P0"},
    "LOCK-AT-003": {"status": "PASS", "terminated": false}
  }
}
```

### 5.2 턴 완료 로그

```json
{
  "event": "conversation.turn_completed",
  "timestamp": "2026-04-13T10:00:15.000Z",
  "trace_id": "trace-abc123",
  "action_id": "action-def456",
  "conversation_id": "conv-ghi789",
  "turn": {
    "number": 3,
    "max_allowed": 5,
    "remaining": 2,
    "phase_level": "P0",
    "sender_id": "lead-001",
    "receiver_id": "research-001",
    "response_summary": "AAPL Q4 2025 revenue: $119.6B, EPS: $2.40",
    "duration_ms": 15000.0,
    "is_final": false
  },
  "partial_result": {
    "type": "financial_data",
    "summary": "AAPL Q4 2025 fundamental data gathered"
  }
}
```

### 5.3 턴 상한 초과 에러 로그

```json
{
  "event": "conversation.turn_limit_exceeded",
  "timestamp": "2026-04-13T10:05:00.000Z",
  "severity": "ERROR",
  "trace_id": "trace-abc123",
  "action_id": "action-def456",
  "conversation_id": "conv-ghi789",
  "violation": {
    "lock_id": "LOCK-AT-009",
    "attempted_turn": 6,
    "max_allowed_turns": 5,
    "phase_level": "P0"
  },
  "conversation_snapshot": {
    "total_turns": 5,
    "turns": [
      {"number": 1, "sender": "lead-001", "receiver": "research-001", "duration_ms": 12000},
      {"number": 2, "sender": "lead-001", "receiver": "coding-001", "duration_ms": 18000},
      {"number": 3, "sender": "lead-001", "receiver": "research-001", "duration_ms": 15000},
      {"number": 4, "sender": "lead-001", "receiver": "coding-001", "duration_ms": 20000},
      {"number": 5, "sender": "lead-001", "receiver": "research-001", "duration_ms": 10000}
    ],
    "partial_results_count": 5
  },
  "escalation": {
    "escalation_id": "esc-turn-abcd1234",
    "severity": "HIGH",
    "action": "force_terminated",
    "partial_results_summary": "Partial results after 5/5 turns (P0): ..."
  }
}
```

### 5.4 종료 후 추가 턴 차단 로그

```json
{
  "event": "conversation.post_termination_blocked",
  "timestamp": "2026-04-13T10:06:00.000Z",
  "severity": "WARNING",
  "trace_id": "trace-abc123",
  "action_id": "action-def456",
  "conversation_id": "conv-ghi789",
  "violation": {
    "lock_id": "LOCK-AT-003",
    "termination_reason": "LOCK-AT-009: Turn 6 > max 5 (P0)",
    "attempted_sender": "lead-001",
    "attempted_receiver": "research-001"
  },
  "action": "blocked"
}
```

---

## 6. 예외 처리 정책 표

| # | 예외 유형 | LOCK 근거 | 트리거 조건 | 자동 대응 | 에스컬레이션 경로 | 심각도 |
|---|----------|----------|-----------|----------|----------------|:------:|
| E-1 | `TurnLimitExceeded` | LOCK-AT-009 | 턴 수 >= max_turns 상태에서 추가 턴 시도 (P0: 6턴째) | 강제 종료 + 부분 결과 요약 반환 + 에러 로그 | Lead Agent → 결과 요약 확정 또는 새 액션 이관 | HIGH |
| E-2 | `ConversationAlreadyTerminated` | LOCK-AT-003 | 이미 종료된 대화에 턴 추가 시도 | 즉시 차단 + 경고 로그 | Lead Agent → 새 ConversationTracker 생성 필요 | MEDIUM |
| E-3 | `ValueError` (잘못된 턴 번호) | — | complete_turn()에 범위 밖 턴 번호 전달 | 거부 + 경고 로그 | 호출자에 에러 반환 | LOW |
| E-4 | 턴 카운터 비정상 (내부 불일치) | LOCK-AT-007 | 턴 카운터와 turns 리스트 길이 불일치 | Checkpoint 스냅샷 저장 + 경고 로그 | Lead Agent → 스냅샷 기반 복구 | MEDIUM |
| E-5 | 비용+턴 동시 초과 | LOCK-AT-009, AT-011 | 비용 상한과 턴 상한 동시 도달 | 비용 상한 우선 차단 (AT-011) → 턴 종료는 보조 | Lead Agent → CostTracker + ConversationTracker 양쪽 에스컬레이션 | HIGH |
| E-6 | 분산 환경 턴 카운터 동기화 실패 (V2+) | LOCK-AT-009, AT-007 | Redis 기반 분산 카운터 불일치 | 로컬 카운터 우선 (보수적) + 동기화 재시도 | Lead Agent → 로컬 fallback | HIGH |
| E-7 | 세션 레벨 합산 초과 | LOCK-AT-009 | Sigma(action_turns) > max_turns_per_session | 세션 전체 종료 + 전체 부분 결과 요약 | 사용자 에스컬레이션 (세션 재시작 필요) | CRITICAL |

---

## 7. Phase 2 테스트 케이스

### 7.1 통합 테스트 시나리오 (14건)

| # | 테스트 ID | 시나리오 | 기대 결과 | 검증 LOCK | 우선순위 |
|---|----------|---------|----------|----------|:-------:|
| 1 | `TC-TL-001` | 4턴 성공 종료 — Lead ↔ Research 4회 왕복 후 정상 완료 | 4턴 모두 정상 완료, is_terminated=False, remaining=1 | AT-009 | P0 |
| 2 | `TC-TL-002` | 5턴 정상 종료 — Lead ↔ Coding 5회 왕복 후 상한 도달 정상 완료 | 5턴 모두 정상 완료, remaining=0, is_final=True (마지막 턴) | AT-009 | P0 |
| 3 | `TC-TL-003` | 6턴 강제 차단 — 5턴 완료 후 6번째 턴 시도 시 `TurnLimitExceeded` 발생 | `TurnLimitExceeded` 예외 + conversation_snapshot 포함 + partial_results | AT-009 | P0 |
| 4 | `TC-TL-004` | 강제 종료 후 결과 요약 포함 확인 | ConversationSnapshot.partial_results 비어있지 않음 + 요약 문자열 생성 | AT-009, AT-002 | P0 |
| 5 | `TC-TL-005` | 종료 후 추가 턴 차단 | 강제 종료 후 increment_turn() 호출 시 `ConversationAlreadyTerminated` 발생 | AT-003 | P0 |
| 6 | `TC-TL-006` | TurnLimitEscalationPayload 완전성 확인 | 에스컬레이션 페이로드 전체 필수 필드 비어있지 않음 | — | P0 |
| 7 | `TC-TL-007` | get_remaining_turns() 정확성 — 각 턴 후 남은 턴 수 확인 | 턴 1 후 remaining=4, 턴 2 후 remaining=3, ..., 턴 5 후 remaining=0 | AT-009 | P0 |
| 8 | `TC-TL-008` | ConversationSnapshot 정합성 — 전체 필드 확인 | snapshot.total_turns == 실제 턴 수, turns 리스트 길이 일치 | AT-007 | P1 |
| 9 | `TC-TL-009` | P1 phase_level 턴 상한 10 적용 | TurnPhaseLevel.P1 설정 시 10턴까지 허용, 11턴째 차단 | AT-009 | P1 |
| 10 | `TC-TL-010` | P2 phase_level 턴 상한 20 적용 | TurnPhaseLevel.P2 설정 시 20턴까지 허용, 21턴째 차단 | AT-009 | P1 |
| 11 | `TC-TL-011` | 병렬 태스크 독립 ConversationTracker 검증 | 각 병렬 태스크가 독립 턴 카운터, 한쪽 상한 초과가 다른 쪽에 영향 없음 | AT-009, AT-014 | P1 |
| 12 | `TC-TL-012` | trace_id 전파 — 전체 턴 동일 trace_id 유지 | 모든 TurnRecord의 trace_id 동일 | AT-007 | P0 |
| 13 | `TC-TL-013` | complete_turn() 잘못된 턴 번호 → ValueError | turn_number=0 또는 turn_number > len(turns) 시 ValueError | — | P1 |
| 14 | `TC-TL-014` | build_partial_results_summary() 빈 결과 처리 | partial_results 없을 때 "[No partial results...]" 메시지 반환 | — | P1 |

### 7.2 pytest 테스트 스켈레톤

```python
import pytest


# --- TC-TL-001: 4턴 성공 종료 ---
def test_4_turns_success():
    """4턴 완료 후 정상 상태 확인."""
    tracker = ConversationTracker(
        action_id="action-001", trace_id="trace-001",
        phase_level=TurnPhaseLevel.P0,
    )
    for i in range(4):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id=f"worker-{i:03d}",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(
            turn_number=record.turn_number,
            response_summary=f"Response {i + 1}",
            partial_result={"summary": f"Result {i + 1}"},
        )
    assert tracker.get_remaining_turns() == 1
    assert tracker.is_within_limit() is True


# --- TC-TL-002: 5턴 정상 종료 (상한 도달) ---
def test_5_turns_at_limit():
    """5턴 완료 후 상한 도달 — 정상 완료."""
    tracker = ConversationTracker(
        action_id="action-002", trace_id="trace-002",
        phase_level=TurnPhaseLevel.P0,
    )
    for i in range(5):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(
            turn_number=record.turn_number,
            response_summary=f"Response {i + 1}",
        )
    assert tracker.get_remaining_turns() == 0
    # 5턴 정상 완료 후 is_within_limit은 False (추가 불가)
    assert tracker.is_within_limit() is False
    # 하지만 강제 종료는 아님
    snapshot = tracker.get_snapshot()
    assert snapshot.is_terminated is False


# --- TC-TL-003: 6턴 강제 차단 ---
def test_6th_turn_blocked():
    """5턴 완료 후 6번째 턴 시도 시 TurnLimitExceeded 발생."""
    tracker = ConversationTracker(
        action_id="action-003", trace_id="trace-003",
        phase_level=TurnPhaseLevel.P0,
    )
    for i in range(5):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(
            turn_number=record.turn_number,
            response_summary=f"Response {i + 1}",
            partial_result={"summary": f"Result {i + 1}"},
        )
    with pytest.raises(TurnLimitExceeded) as exc_info:
        tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary="Task 6 — should be blocked",
        )
    assert exc_info.value.current_turn == 5
    assert exc_info.value.max_turns == 5
    assert exc_info.value.conversation_snapshot is not None
    assert exc_info.value.phase_level == "P0"


# --- TC-TL-004: 강제 종료 후 결과 요약 포함 ---
def test_forced_termination_partial_results():
    """강제 종료 시 부분 결과 요약 반환 확인."""
    tracker = ConversationTracker(
        action_id="action-004", trace_id="trace-004",
        phase_level=TurnPhaseLevel.P0,
    )
    for i in range(5):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(
            turn_number=record.turn_number,
            response_summary=f"Response {i + 1}",
            partial_result={"summary": f"Partial result {i + 1}"},
        )
    try:
        tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary="Blocked task",
        )
    except TurnLimitExceeded as e:
        snapshot = e.conversation_snapshot
        assert len(snapshot.partial_results) == 5
        assert snapshot.is_terminated is True
        summary = tracker.build_partial_results_summary()
        assert "Partial results after 5/5 turns" in summary


# --- TC-TL-005: 종료 후 추가 턴 차단 ---
def test_post_termination_blocked():
    """강제 종료 후 추가 increment_turn() 시 ConversationAlreadyTerminated."""
    tracker = ConversationTracker(
        action_id="action-005", trace_id="trace-005",
        phase_level=TurnPhaseLevel.P0,
    )
    for i in range(5):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(turn_number=record.turn_number,
                              response_summary=f"Resp {i + 1}")
    # 6턴째 — TurnLimitExceeded로 강제 종료
    with pytest.raises(TurnLimitExceeded):
        tracker.increment_turn("lead-001", "research-001", "Task 6")
    # 7턴째 — ConversationAlreadyTerminated
    with pytest.raises(ConversationAlreadyTerminated):
        tracker.increment_turn("lead-001", "research-001", "Task 7")


# --- TC-TL-006: 에스컬레이션 페이로드 완전성 ---
def test_escalation_payload_completeness():
    """TurnLimitEscalationPayload 전체 필드 비어있지 않음."""
    tracker = ConversationTracker(
        action_id="action-006", trace_id="trace-006",
        phase_level=TurnPhaseLevel.P0,
    )
    for i in range(5):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(turn_number=record.turn_number,
                              response_summary=f"Resp {i + 1}")
    tracker.force_terminate("LOCK-AT-009 test")
    payload = tracker.build_escalation_payload()
    assert payload.trace_id
    assert payload.escalation_id
    assert payload.action_id
    assert payload.conversation_id
    assert payload.violation_type == "TURN_LIMIT_EXCEEDED"
    assert payload.conversation_snapshot
    assert payload.partial_results_summary
    assert payload.reason


# --- TC-TL-007: get_remaining_turns() 정확성 ---
def test_remaining_turns_accuracy():
    """각 턴 후 남은 턴 수 정확성."""
    tracker = ConversationTracker(
        action_id="action-007", trace_id="trace-007",
        phase_level=TurnPhaseLevel.P0,
    )
    assert tracker.get_remaining_turns() == 5
    for i in range(5):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(turn_number=record.turn_number,
                              response_summary=f"Resp {i + 1}")
        assert tracker.get_remaining_turns() == 4 - i


# --- TC-TL-008: ConversationSnapshot 정합성 ---
def test_snapshot_integrity():
    """스냅샷 total_turns == 실제 턴 수."""
    tracker = ConversationTracker(
        action_id="action-008", trace_id="trace-008",
        phase_level=TurnPhaseLevel.P0,
    )
    for i in range(3):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(turn_number=record.turn_number,
                              response_summary=f"Resp {i + 1}")
    snapshot = tracker.get_snapshot()
    assert snapshot.total_turns == 3
    assert len(snapshot.turns) == 3
    assert snapshot.max_allowed_turns == 5
    assert snapshot.phase_level == "P0"


# --- TC-TL-009: P1 phase_level (max=10) ---
def test_p1_phase_level_10_turns():
    """P1 phase_level에서 10턴까지 허용, 11턴째 차단."""
    tracker = ConversationTracker(
        action_id="action-009", trace_id="trace-009",
        phase_level=TurnPhaseLevel.P1,
    )
    for i in range(10):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(turn_number=record.turn_number,
                              response_summary=f"Resp {i + 1}")
    assert tracker.get_remaining_turns() == 0
    with pytest.raises(TurnLimitExceeded) as exc_info:
        tracker.increment_turn("lead-001", "research-001", "Task 11")
    assert exc_info.value.max_turns == 10
    assert exc_info.value.phase_level == "P1"


# --- TC-TL-010: P2 phase_level (max=20) ---
def test_p2_phase_level_20_turns():
    """P2 phase_level에서 20턴까지 허용, 21턴째 차단."""
    tracker = ConversationTracker(
        action_id="action-010", trace_id="trace-010",
        phase_level=TurnPhaseLevel.P2,
    )
    for i in range(20):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        tracker.complete_turn(turn_number=record.turn_number,
                              response_summary=f"Resp {i + 1}")
    assert tracker.get_remaining_turns() == 0
    with pytest.raises(TurnLimitExceeded) as exc_info:
        tracker.increment_turn("lead-001", "research-001", "Task 21")
    assert exc_info.value.max_turns == 20
    assert exc_info.value.phase_level == "P2"


# --- TC-TL-011: 병렬 태스크 독립 ConversationTracker ---
def test_parallel_independent_trackers():
    """병렬 태스크 각각 독립 턴 카운터.

    P1-05 ParallelDispatcher 연동 — 각 병렬 태스크는
    독립 ConversationTracker로 턴 관리.
    """
    tracker_a = ConversationTracker(
        action_id="action-parallel-a", trace_id="trace-parallel-a",
        phase_level=TurnPhaseLevel.P0,
    )
    tracker_b = ConversationTracker(
        action_id="action-parallel-b", trace_id="trace-parallel-b",
        phase_level=TurnPhaseLevel.P0,
    )
    # tracker_a: 5턴 소진
    for i in range(5):
        r = tracker_a.increment_turn("lead-001", "research-001", f"A-{i + 1}")
        tracker_a.complete_turn(r.turn_number, f"A-resp-{i + 1}")
    # tracker_b: 여전히 5턴 가용
    assert tracker_b.get_remaining_turns() == 5
    r = tracker_b.increment_turn("lead-001", "coding-001", "B-1")
    assert r.turn_number == 1
    # tracker_a: 상한 도달 확인
    with pytest.raises(TurnLimitExceeded):
        tracker_a.increment_turn("lead-001", "research-001", "A-6")


# --- TC-TL-012: trace_id 전파 ---
def test_trace_id_propagation():
    """전체 턴 동일 trace_id 유지 확인."""
    tracker = ConversationTracker(
        action_id="action-012", trace_id="trace-012",
        phase_level=TurnPhaseLevel.P0,
    )
    for i in range(3):
        record = tracker.increment_turn(
            sender_id="lead-001",
            receiver_id="research-001",
            request_summary=f"Task {i + 1}",
        )
        assert record.trace_id == "trace-012"
        tracker.complete_turn(turn_number=record.turn_number,
                              response_summary=f"Resp {i + 1}")
    snapshot = tracker.get_snapshot()
    for turn in snapshot.turns:
        assert turn.trace_id == "trace-012"


# --- TC-TL-013: 잘못된 턴 번호 ValueError ---
def test_invalid_turn_number():
    """complete_turn()에 범위 밖 턴 번호 → ValueError."""
    tracker = ConversationTracker(
        action_id="action-013", trace_id="trace-013",
        phase_level=TurnPhaseLevel.P0,
    )
    tracker.increment_turn("lead-001", "research-001", "Task 1")
    with pytest.raises(ValueError):
        tracker.complete_turn(turn_number=0, response_summary="Invalid")
    with pytest.raises(ValueError):
        tracker.complete_turn(turn_number=99, response_summary="Invalid")


# --- TC-TL-014: 빈 결과 요약 처리 ---
def test_empty_partial_results_summary():
    """partial_results 없을 때 적절한 메시지 반환."""
    tracker = ConversationTracker(
        action_id="action-014", trace_id="trace-014",
        phase_level=TurnPhaseLevel.P0,
    )
    tracker.increment_turn("lead-001", "research-001", "Task 1")
    tracker.complete_turn(turn_number=1, response_summary="Resp 1")
    # partial_result 없이 complete_turn
    summary = tracker.build_partial_results_summary()
    assert "[No partial results after 1 turns]" in summary
```

---

## 8. 알고리즘 시간복잡도 + LOCK + ABC 요약

| 메서드 | ABC 시그니처 | 시간복잡도 | 관련 LOCK |
|--------|------------|-----------|----------|
| `increment_turn()` | `increment_turn(sender_id, receiver_id, request_summary, trace_id) -> TurnRecord` | O(1) | AT-009, AT-003 |
| `complete_turn()` | `complete_turn(turn_number, response_summary, partial_result) -> TurnRecord` | O(1) | — |
| `force_terminate()` | `force_terminate(reason) -> ConversationSnapshot` | O(t) — t = total turns | AT-009, AT-002 |
| `get_snapshot()` | `get_snapshot() -> ConversationSnapshot` | O(t) — t = total turns | AT-007 |
| `get_remaining_turns()` | `get_remaining_turns() -> int` | O(1) | AT-009 |
| `is_within_limit()` | `is_within_limit() -> bool` | O(1) | AT-009, AT-003 |
| `build_partial_results_summary()` | `build_partial_results_summary() -> str` | O(r) — r = partial_results count | AT-002 |
| `build_escalation_payload()` | `build_escalation_payload() -> TurnLimitEscalationPayload` | O(t) — t = total turns | AT-009 |

---

## 9. 세션간 인터페이스 cross-check

| 인접 세션 | 인터페이스 | 본 세션 사용 방식 | 정합성 |
|----------|-----------|-----------------|:------:|
| P1-01 (Lead Agent) | `LeadAgent.decide()` | 강제 종료 시 Lead가 ConversationSnapshot 기반 결과 요약 확정 (LOCK-AT-002) | OK |
| P1-04 (Sequential) | `SequentialPipeline` | 파이프라인 전체 턴 수 제한 참조 — P1-04 §9 인터페이스 "P1-10 ConversationTracker max_turns=5 (P0)" 명시 | OK |
| P1-05 (Parallel) | `ParallelDispatcher.dispatch()` | 병렬 태스크 각각 독립 ConversationTracker 생성 (TC-TL-011 검증) | OK |
| P1-06 (Delegation Chain) | `DelegationChain.delegate()` | 위임 체인 내 턴 카운트 전파 — DelegationNode의 trace_id를 ConversationTracker에 전달 | OK |
| P1-07 (MessageBus) | `InMemoryMessageBus.publish()` | 메시지 교환 시 increment_turn() 트리거 — 토픽 라우팅과 연동 | OK |
| P1-11 (TEE Loop) | `TEELoop` (예정) | TEE 반복 상한(AT-010)과 턴 상한(AT-009) 독립 관리 — 이중 안전장치 | OK (인터페이스 예약) |
| P1-12 (Cost Tracker) | `CostTracker` (예정) | 비용 상한(AT-011)과 턴 상한(AT-009) 동시 모니터링 — 비용 우선 차단 | OK (인터페이스 예약) |
| P1-13 (Loop Detector) | `LoopDetector` (예정) | LOCK-AT-003 무한 루프 감지 보조 — ConversationTracker가 1차 방어선, LoopDetector가 2차 | OK (인터페이스 예약) |
| P1-14 (Trace Manager) | `TraceManager` (예정) | LOCK-AT-007 trace_id 관리 위임 — 현재 trace_id는 파라미터로 전달 | OK (인터페이스 예약) |

---

## 10. 공통 자료 구조 선정의

### 10.1 본 세션 신규 정의

| 자료 구조 | 용도 | 재사용 가능 세션 |
|----------|------|----------------|
| `TurnPhaseLevel` (Enum) | P-level 턴 상한 등급 (P0=5, P1=10, P2=20) | P1-11 (TEELoop), P1-12 (CostTracker), Phase 2 전체 |
| `TurnRecord` (dataclass) | 단일 턴 기록 | P1-07 (MessageBus 로그 연동), Phase 2 턴 분석 |
| `ConversationSnapshot` (dataclass) | 대화 전체 스냅샷 | P1-01 (Lead 에스컬레이션), P1-14 (Checkpoint), Phase 2 Replay |
| `TurnLimitEscalationPayload` (dataclass) | 턴 상한 에스컬레이션 | P1-01 (Lead Agent 에스컬레이션 처리) |

### 10.2 P1-01 참조 자료 구조

| 자료 구조 | 원본 | 본 세션 참조 방식 |
|----------|------|----------------|
| `AgentRole` (Enum) | P1-01 §3.1 | TurnRecord의 sender/receiver 역할 식별 |
| `EscalationPayload` (dataclass) | P1-01 §3.1 | TurnLimitEscalationPayload 기반 구조 |
| `TaskStatus` (Enum) | P1-01 §3.1 | 턴 진행 상태 추적 |

---

## 변경 이력

| 일자 | 변경 내용 | 세션 |
|------|----------|------|
| 2026-04-13 | 초기 작성 — ConversationTracker 클래스 스켈레톤, TurnPhaseLevel/TurnRecord/ConversationSnapshot 자료 구조, Phase 2 테스트 14건, 복구 흐름도, 로깅 JSON 4종, 예외 처리 정책 7건 | P1-10 |

---

> **문서 끝**
> 본 문서는 P1-10 세션 산출물이며, LOCK-AT-009(대화 턴 상한 P0=5, P1=10, P2=20) 정본을 기반으로 작성되었습니다.
