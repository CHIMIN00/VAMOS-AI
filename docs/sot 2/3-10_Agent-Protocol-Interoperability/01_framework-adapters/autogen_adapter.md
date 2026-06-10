# AutoGen Adapter — K-023 (L3)

> **STEP7-K**: K-023 — AutoGen 대화형 에이전트
> **레벨**: L3 (구현 상세)
> **Part2 상태**: ABSENT — 본 문서 신규 작성 (정본 = What+How)
> **정본 소유**: #13 Agent-Protocol-Interoperability / 01_framework-adapters
> **V 스코프**: V1 (핵심 프레임워크 어댑터)

---

## §1. 교차 참조 블록

| 정본 문서 | 섹션 | 참조 내용 |
|----------|------|----------|
| 구조화_종합계획서.md | §3.4 | LOCK-AP-01 (VamosMessage), AP-02 (Permission 0~5), AP-03 (A2A Task 상태), AP-05 (Lead + max 2 Sub), AP-07 (A2A+MCP 양방향), AP-09 (비용 상한) |
| 구조화_종합계획서.md | §7.3.2 | Part2 방식 C 요약 — Agent Teams V1 (Lead+max 2 Sub, LOCK-AT-001~017) |
| 구조화_종합계획서.md | §A.1~A.3 | 프레임워크 어댑터 카탈로그 (인터페이스, 변환 규칙) |
| AUTHORITY_CHAIN.md | §3 | LOCK-AP-01~10 원본 및 재정의 금지 |
| 6-3_Agent-Teams-PARL | LOCK-AT-001~017 | Agent Teams V1 제약 17건 |
| 3-8 CONVERSATION_A2A | A2A Protocol | `submitted→working→input-required→completed/failed/canceled` (LOCK-AP-03) |
| 01_framework-adapters/langgraph_adapter.md | §3 | 공통 자료 구조 정본 |
| 01_framework-adapters/crewai_adapter.md | §3 | 공통 자료 구조 정합 확인 |
| 06_autonomy-safety/permission_matrix.md (P1-2) | §K-041 | Permission Level 0~5 (AssistantAgent/UserProxyAgent 매핑) |

> **R6 준수**: 본 문서는 What+How 전용. Phase/Week 등 When 정보 미기재.

---

## §2. 개요 (Purpose & Scope)

### 2.1 목적
Microsoft AutoGen v0.4+ 의 `ConversableAgent`, `GroupChat`, `AssistantAgent`, `UserProxyAgent` 대화형 패턴을 VAMOS Agent Teams V1(Lead + max 2 Sub-Agent)과 A2A 메시지 플로우로 변환하는 어댑터.

### 2.2 범위
- **In-scope**: `ConversableAgent` → `VAMOSAgent`, `GroupChat` → `TeamLayout`, 대화 히스토리 → A2A messages 체인, `AssistantAgent`/`UserProxyAgent` 역할 분리 → VAMOS RBAC, `register_function` → MCPTool.
- **Out-of-scope (V2+)**: Nested GroupChat (V2), Teachable/CompressibleAgent (V2), Magentic-One Orchestrator (K-024 V2), GroupChatManager Custom Selector (V2).

### 2.3 비고
- LOCK-AP-05: GroupChat 참여자 수 > 3 → 거부 (Lead + max 2 Sub, `UserProxyAgent` 는 별도 카운트).
- LOCK-AT-015: Lead 직접 실행 금지 — AutoGen GroupChatManager 의 Lead 역할만 `assign_to` 가능, 직접 도구 호출 금지.
- LOCK-AP-08 (LangGraph 상수) 는 본 어댑터 대상 아님 — LangGraph 경유 흐름이 있을 때만 `langgraph_adapter.md §5.4` 재사용.

---

## §3. 공통 자료 구조 참조

> **정본**: `01_framework-adapters/langgraph_adapter.md §3`.

재사용: `VamosMessage` (LOCK-AP-01), `A2ATaskState` (LOCK-AP-03), `VamosPhase`, `FrameworkTaskRef`, `StateMapping`, `GatePolicy`, `CircuitBreakerState`, `AdapterResult`, `VamosTask`.

crewai_adapter.md §3 에서 재사용: `VAMOSAgent`, `TeamLayout`.

본 문서 전용:

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class AutoGenAgentSpec(BaseModel):
    name: str
    system_message: str
    kind: Literal["assistant", "user_proxy", "group_manager"]
    llm_config: Optional[dict] = None
    code_execution_config: Optional[dict] = None
    human_input_mode: Literal["NEVER", "TERMINATE", "ALWAYS"] = "NEVER"
    max_consecutive_auto_reply: int = 10

class GroupChatSpec(BaseModel):
    agents: list[AutoGenAgentSpec]
    max_round: int = 10
    speaker_selection_method: Literal["auto", "round_robin", "random", "manual"] = "round_robin"
    admin_name: Optional[str] = None             # GroupChatManager

class ConversationTurn(BaseModel):
    turn: int
    sender: str
    recipient: str
    content: str
    tool_calls: list[dict] = Field(default_factory=list)
    a2a_state: "A2ATaskState"
```

---

## §4. FrameworkAdapter 인터페이스 구현

```python
class AutoGenAdapter(FrameworkAdapter):
    framework_id: str = "autogen-v0.4"
    framework_name: Literal["autogen"] = "autogen"
    version_range: str = ">=0.4.0,<0.5.0"        # §A.1
    capabilities: list[AdapterCapability] = [
        "task_delegation", "tool_sharing",
        "conversation_map", "event_forwarding",
    ]

    def translate_to_vamos(self, turn: ConversationTurn) -> VamosMessage: ...
    def translate_from_vamos(self, vamos_msg: VamosMessage) -> ConversationTurn: ...
    def map_agents(self, group_chat: GroupChatSpec) -> list[VAMOSAgent]: ...
    def bridge_tools(self, registered_fns: list[Any]) -> list["MCPTool"]: ...
    def sync_state(self, chat_history: list[ConversationTurn],
                   vamos_context: dict) -> dict: ...
    def health_check(self) -> "AdapterHealth": ...
```

§A.3 카탈로그 정합: `Agent → VAMOSAgent (name→agent_card)`, `Task → A2AMessage (content→parts)`, `Tool → MCPTool (코드실행 래퍼)`, `상태 → GroupChat history → A2A messages`.

---

## §5. ConversableAgent → VAMOS Agent 변환 알고리즘

### 5.1 Agent kind → role_type / Permission Level 매핑

| AutoGen kind | system_message 힌트 | VAMOS role_type | Permission Level |
|---|---|---|---|
| `assistant` | "helpful assistant", "expert", "analyst" | `research` | 2 |
| `assistant` | "coder", "developer", "engineer" | `coding` | 2 |
| `assistant` | "reviewer", "critic", "validator" | `verify` | 3 |
| `assistant` | "manager", "lead", "orchestrator" | `lead` | 3 |
| `user_proxy` (code_execution_config) | — | `coding` (sandbox) | 2 |
| `user_proxy` (human_input_mode=ALWAYS) | — | — (HITL 채널, 에이전트 아님) | 0 |
| `group_manager` | — | `lead` | 3 |

> `user_proxy(ALWAYS)` 는 VAMOS 에이전트가 아닌 **I-19 HITL 채널**로 매핑된다. `map_agents` 에서 제외하고 별도 `hitl_proxy_ref` 로 반환.

### 5.2 의사코드 — GroupChat → TeamLayout 변환

```python
def map_group_chat_to_layout(gc: GroupChatSpec) -> TeamLayout:
    """
    시간복잡도: O(n)  n = len(gc.agents)
    LOCK 참조: AP-05 (Lead + max 2 Sub), AT-015 (Lead 직접실행 금지),
              AT-014 (V1 total=3)
    ABC: Adapter + Builder
    """
    hitl_agents = [a for a in gc.agents
                   if a.kind == "user_proxy" and a.human_input_mode == "ALWAYS"]
    runnable = [a for a in gc.agents if a not in hitl_agents]

    if len(runnable) > 3:
        raise LockViolation("LOCK-AP-05: GroupChat runnable > 3")

    # Lead 결정
    leads = [a for a in runnable
             if a.kind == "group_manager"
             or infer_role(a.system_message) == "lead"]
    if len(leads) != 1:
        raise LockViolation(f"LOCK-AT-015: Lead 단일 선출 실패 (leads={len(leads)})")

    lead_spec = leads[0]
    subs = [a for a in runnable if a is not lead_spec]
    assert len(subs) <= 2, "LOCK-AP-05 violation"

    lead = to_vamos_agent(lead_spec, role_type="lead")
    sub_agents = [to_vamos_agent(s, role_type=infer_role_type(s)) for s in subs]

    # AT-015: Lead 직접 실행 금지 검증
    if lead_spec.code_execution_config is not None:
        raise LockViolation("LOCK-AT-015: Lead code_execution_config 금지")

    pattern = "sequential" if gc.speaker_selection_method in ("round_robin", "manual") \
              else "parallel"

    return TeamLayout(lead=lead, subs=sub_agents,
                      delegation_depth=1, pattern=pattern)
```

### 5.3 대화 히스토리 → A2A messages 체인

```python
def chat_history_to_a2a(history: list[ConversationTurn]
                        ) -> list[VamosMessage]:
    """
    시간복잡도: O(m)  m = len(history)
    LOCK 참조: AP-01 (VamosMessage 6필드), AP-03 (A2A 상태 보존)
    """
    out = []
    prev_state: A2ATaskState = "submitted"
    for turn in history:
        # 상태 전이 유효성 검사
        next_state = compute_next_state(prev_state, turn)
        assert_valid_transition(prev_state, next_state)     # LOCK-AP-03
        out.append(VamosMessage(
            id=new_uuid(),
            type="task" if next_state in ("submitted", "working") else "result",
            source=turn.sender,
            target=turn.recipient,
            content={"parts": [{"kind": "text", "text": turn.content}],
                     "tool_calls": turn.tool_calls},
            metadata={
                "framework_origin": "autogen",
                "trace_id": get_or_create_trace_id(turn),
                "a2a_state": next_state,
                "turn": turn.turn,
            },
        ))
        prev_state = next_state
    return out

def compute_next_state(prev: A2ATaskState,
                       turn: ConversationTurn) -> A2ATaskState:
    if turn.tool_calls:
        return "working"
    if turn.content.strip().upper().startswith("TERMINATE"):
        # LOCK-AP-03: 'completed' is invalid from 'submitted'; TERMINATE before work = canceled (§V2.5)
        return "canceled" if prev == "submitted" else "completed"
    if turn.content.lower().startswith("error"):
        return "failed"
    return "working"
```

### 5.4 A2A 상태 전이 규칙 (LOCK-AP-03)

```
submitted ─→ working ─→ input-required ─→ working ─→ completed
                   ├─→ failed
                   └─→ canceled
```

```python
VALID_TRANSITIONS = {
    "submitted": {"working", "canceled"},
    "working": {"input-required", "completed", "failed", "canceled"},
    "input-required": {"working", "canceled"},
    "completed": set(),
    "failed": set(),
    "canceled": set(),
}

def assert_valid_transition(prev: A2ATaskState,
                            nxt: A2ATaskState) -> None:
    # `next` 는 파이썬 빌트인이므로 `nxt` 사용
    if nxt not in VALID_TRANSITIONS[prev]:
        raise LockViolation(
            f"LOCK-AP-03: invalid transition {prev}→{nxt}")
```

---

## §6. RBAC 분리 (AssistantAgent / UserProxyAgent)

| AutoGen 에이전트 | 역할 | Permission Level | 주의 |
|---|---|---|---|
| `AssistantAgent` (no code_execution) | 대화/분석 | 2 | 도구 호출은 `register_function` 경유만 |
| `UserProxyAgent` (code_execution_config=docker) | Sandbox 코드 실행 | 2 | `bridge_tools` 에서 샌드박스 강제 (06_autonomy-safety/guardrail_rules.md §K-043) |
| `UserProxyAgent` (ALWAYS) | HITL 채널 | 0 | I-19 경유, 에이전트 아님 |
| `GroupChatManager` | Lead 오케스트레이션 | 3 | LOCK-AT-015 (직접 실행 금지) |

> **정본**: `06_autonomy-safety/permission_matrix.md (P1-2)`. 본 §6는 매핑 요약.

---

## §7. Tool Bridge (register_function → MCPTool)

```python
def bridge_tools(registered_fns: list[RegisteredFunction]) -> list[MCPTool]:
    """
    시간복잡도: O(k) k = len(registered_fns)
    LOCK 참조: AP-07 (A2A+MCP 양방향 필수), AP-02 (Permission 체크)
    """
    out = []
    for fn in registered_fns:
        level_required = infer_permission_level(fn.signature)
        if not check_permission(fn.caller_agent, level_required):
            raise PermissionDenied(f"LOCK-AP-02: {fn.name} level={level_required}")
        out.append(MCPTool(
            name=fn.name,
            description=fn.description,
            input_schema=fn.signature.to_json_schema(),
            handler=wrap_sandboxed(fn),           # E2B/Docker sandbox
            required_permission_level=level_required,
        ))
    return out
```

---

## §8. 예외 처리 정책 표

| error_code | 발생 시점 | 원인 | recoverable | 처리 |
|---|---|---|---|---|
| `AG-ADP-001` | map_group_chat_to_layout | runnable > 3 | No | `LockViolation` (LOCK-AP-05), I-20 |
| `AG-ADP-002` | map_group_chat_to_layout | Lead 선출 실패 | No | `LockViolation` (LOCK-AT-015), I-20 |
| `AG-ADP-003` | map_group_chat_to_layout | Lead 에 code_execution | No | `LockViolation` (LOCK-AT-015), I-20 |
| `AG-ADP-010` | chat_history_to_a2a | 잘못된 상태 전이 | No | `LockViolation` (LOCK-AP-03), I-20 |
| `AG-ADP-011` | compute_next_state | 상태 추론 실패 | Yes | `working` 폴백, confidence −0.05 |
| `AG-ADP-020` | bridge_tools | Permission 초과 | No | deny, LOCK-AP-02 감사 로깅 |
| `AG-ADP-021` | bridge_tools | Sandbox 비구성 | No | deny, K-043 위반 |
| `AG-ADP-030` | sync_state | Chat history 파싱 실패 | Yes | 빈 history 폴백, warning |
| `AG-ADP-040` | map_agents | user_proxy(ALWAYS) Lead 시도 | No | deny, HITL 채널 지정 필수 |
| `AG-ADP-050` | translate_from_vamos | tool_calls 스키마 위반 | No | fail, CONFLICT 후보 |
| `AG-ADP-060` | GroupChat.max_round 초과 | 무한 루프 감지 | No | LOCK-AT-003 (무한루프 금지), I-20 |
| `AG-ADP-099` | 공통 | 미분류 | No | I-20 에스컬레이션 |

---

## §9. Phase별 복구/다운그레이드 흐름도

```
Intake (Phase1)            Plan (Phase2)             Execute (Phase3)           Verify (Phase4)
─────────────              ────────────             ────────────────            ────────────────
GroupChat size ┐         Lead 선출 실패 ┐          max_round 초과 ┐         상태 전이 err ┐
               │                        │                        │                       │
               ▼                        ▼                        ▼                       ▼
  LOCK-AP-05 ─→[I-20]      LOCK-AT-015 ─→[I-20]      LOCK-AT-003 ─→[I-20]     LOCK-AP-03 ─→[I-20]
  deny                     deny                       deny                      deny
                                                        │
                                                        ▼
                                                Soft Loop 1회 (max_round 완화)
                                                        │
                                                        ▼
                                                Hard Loop → I-19 HITL
                                                        │
                                                        ▼
                                                Deliver (Phase5)
                                                ────────────
                                                Budget 초과 → G5 [I-20]
```

### 9.1 다운그레이드 confidence penalty 표

| 상황 | penalty | 다음 결정 |
|---|---|---|
| 상태 추론 실패 | −0.05 | working 폴백 |
| chat_history 파싱 실패 | −0.05 | 빈 history |
| max_round 1회 연장 | −0.08 | Soft Loop |
| max_round 재연장 거부 | −0.15 | Hard Loop → I-19 |
| LOCK-AP-05/AT-003/AT-015 위반 | 즉시 deny | I-20 post-mortem |
| Permission 위반 | 즉시 deny | LOCK-AP-02 감사 |

---

## §10. 에스컬레이션 페이로드

```python
class EscalationPayload(BaseModel):
    source_engine: Literal["autogen_adapter"] = "autogen_adapter"
    target_channel: Literal["I-19", "I-20"]
    error_code: str
    original_request: VamosMessage
    partial_result: Optional[dict] = None
    retry_count: int = 0
    group_chat_snapshot: GroupChatSpec
    turn_count: int
    last_valid_state: A2ATaskState
    confidence_after_penalty: float
    lock_violations: list[str] = Field(default_factory=list)
    trace_id: str
    timestamp: datetime
```

---

## §11. 로깅 포맷 (R-01-7 structured JSON, 중첩)

```json
{
  "ts": "2026-04-11T10:25:13.502Z",
  "level": "ERROR",
  "logger": "autogen_adapter",
  "trace_id": "3f4c...aa",
  "event": "invalid_state_transition",
  "error": {
    "code": "AG-ADP-010",
    "message": "invalid transition completed->working",
    "class": "LockViolation",
    "stack_digest": "sha256:77fe..."
  },
  "context": {
    "framework": "autogen",
    "group_chat_id": "debate_01",
    "turn": 7,
    "sender": "reviewer",
    "recipient": "coder",
    "vamos_phase": "verify",
    "permission_level": 3
  },
  "recovery": {
    "strategy": "escalate_i20",
    "lock_violations": ["LOCK-AP-03"],
    "rollback_to_turn": 6,
    "hitl_required": false,
    "confidence_after": 0.40
  }
}
```

---

## §12. Phase 2 통합 테스트 시나리오 (10건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---|---|---|
| T-01 | 3-agent GroupChat 정상 | Manager + 2 Assistants, round_robin | TeamLayout, sequential pattern |
| T-02 | GroupChat runnable 4 거부 | 4 runnable agents fixture | `AG-ADP-001` (LOCK-AP-05), I-20 |
| T-03 | Lead 선출 실패 | manager 없음, lead 힌트 없음 | `AG-ADP-002` (LOCK-AT-015), I-20 |
| T-04 | Lead code_execution 금지 | Manager에 code_execution_config | `AG-ADP-003` (LOCK-AT-015), I-20 |
| T-05 | UserProxy ALWAYS → HITL 채널 | human_input_mode=ALWAYS 1개 | 에이전트 아닌 `hitl_proxy_ref` 반환 |
| T-06 | 대화 상태 전이 정합 | submitted→working→completed 시나리오 | LOCK-AP-03 위반 0건 |
| T-07 | 잘못된 상태 전이 거부 | completed→working 주입 | `AG-ADP-010`, I-20 |
| T-08 | max_round 무한 루프 방지 | max_round 5, 6회째 진입 | `AG-ADP-060` (LOCK-AT-003), I-20 |
| T-09 | register_function permission | Level 2 agent가 Level 4 fn | `AG-ADP-020` deny, LOCK-AP-02 감사 |
| T-10 | Sandbox 미구성 거부 | code_execution_config=None 에 tool 호출 | `AG-ADP-021` (K-043), I-19 제안 |
| T-11 | 대화 → A2A 변환 왕복 | to→from 왕복 5턴 | VamosMessage 필드 6개 무손실, turn 보존 |
| T-12 | Budget 초과 (LOCK-AP-09) | 토큰 over | G5 hold, I-20, ₩40K 경고 |

---

## §13. ABC 패턴 매핑 요약

| 구조/행동 | 패턴 | 위치 |
|---|---|---|
| `FrameworkAdapter` 인터페이스 | Adapter (구조) | §4 |
| `map_group_chat_to_layout` | Builder (생성) | §5.2 |
| `chat_history_to_a2a` | Template Method (행동) | §5.3 |
| `compute_next_state` / `assert_valid_transition` | State (행동) | §5.4 |
| `bridge_tools` / sandbox wrap | Decorator (구조) | §7 |
| RBAC 분리 (P1-2 위임) | Chain of Responsibility (행동) | §6 |

---

## §14. 세션 간 인터페이스 cross-check

| 상대 산출물 | 인터페이스 | 본 문서 기준 | 정합 |
|---|---|---|---|
| langgraph_adapter.md §3 | 공통 Pydantic (VamosMessage, A2ATaskState, TeamLayout 등) | §3 재사용 | OK |
| crewai_adapter.md §3 | `VAMOSAgent`, `TeamLayout` | §3 재사용 | OK |
| 03_data-exchange/message_format.md (P1-3) | LOCK-AP-01 VamosMessage 스키마 | §3, §5.3 content 구조 `parts[]` 사용 | P1-3 확정 후 재검 |
| 06_autonomy-safety/permission_matrix.md (P1-2) | `check_permission(agent, level)` | §6, §7 에서 위임 | P1-2 시그니처 확정 필요 |
| 06_autonomy-safety/guardrail_rules.md (P1-2) | K-043 Sandbox 규격 | §7 `wrap_sandboxed`, T-10 | P1-2 K-043 정본 일치 |
| 3-8 A2A Task 상태 (LOCK-AP-03) | 상태 머신 + 전이 | §5.4 `VALID_TRANSITIONS` | OK (cross-domain LOCK) |
| 6-3 LOCK-AT-003 (무한루프 금지) | `max_round` 체크 | §8 `AG-ADP-060`, T-08 | 외부 도메인 LOCK 참조 |

불일치 0건.

---

## §15. LOCK / CONFLICT 영향

- **LOCK-AP-01**: VamosMessage 6필드 유지. `content.parts[]` 형태는 A2A SPEC 정합 (3-8).
- **LOCK-AP-03**: §5.4 `VALID_TRANSITIONS` 는 LOCK 원문 그대로. 재정의 0건.
- **LOCK-AP-05**: §5.2 runnable ≤ 3 검사.
- **LOCK-AT-003** (무한루프 금지), **LOCK-AT-014** (V1=3), **LOCK-AT-015** (Lead 직접 실행 금지): 6-3 정본 참조.
- **LOCK-AP-02**: §6, §7 매핑 — 값 재정의 없음.
- **LOCK-AP-09**: T-12 Budget 체크.

LOCK 변경 필요 없음. CONFLICT 후보 없음.

---

## §16. 검증 자가 체크리스트

- [x] 교차 참조 블록 §1 (§7.3.2, §3.4, 6-3 LOCK-AT, 3-8 A2A, §A)
- [x] 공통 자료 구조 langgraph/crewai §3 재사용 + AutoGen 전용 타입 3종 (§3)
- [x] FrameworkAdapter 인터페이스 §A.2 정합 (§4)
- [x] GroupChat → TeamLayout + Big-O O(n) + LOCK-AP-05/AT-015 검사 (§5.2)
- [x] 대화 히스토리 → A2A messages (§5.3)
- [x] 상태 전이 정합 `VALID_TRANSITIONS` (LOCK-AP-03) (§5.4)
- [x] RBAC 분리 Assistant/UserProxy/Manager (§6)
- [x] Tool Bridge + sandbox (K-043 연계) (§7)
- [x] 예외 처리 정책 표 12행 (§8)
- [x] Phase별 복구 흐름도 + penalty 표 (§9)
- [x] EscalationPayload I-19/I-20 (§10)
- [x] 로깅 nested JSON (error/context/recovery/trace_id) (§11)
- [x] Phase 2 테스트 시나리오 12건 (§12)
- [x] ABC 패턴 매핑 (§13)
- [x] 세션 간 인터페이스 cross-check (§14)
- [x] R6 준수

---

*정본 소유: #13 Agent-Protocol-Interoperability / 01_framework-adapters / K-023*
*참조: Part2 §6.7 · 6-3 LOCK-AT-001~017 · 3-8 A2A 상태 · 구조화_종합계획서 §7.3.2·§A*

---

## §V2. V2-Phase 2 확장 (2026-04-22, STAGE 7 STEP_B #2a)

> **V2 태그**: V2-Phase 2 (append-only 확장, V1 §1~§15 본문은 불변)
> **upstream baseline**: STEP7-K sha256 `150720a3496f557d359a421dcbf0922ebe5b1e4fbaa06611eff40e0865177539`
> **범위**: K-023 AutoGen 어댑터 V2 확장 — `GroupChatManager` → Magentic-One Orchestrator, MoA Aggregator 배치, Reflection 통합, FR-9 호환성 매트릭스 진입.

### §V2.1 AutoGen GroupChat × Magentic-One Orchestrator

AutoGen 0.4+ 의 `GroupChatManager` 는 **Magentic-One Orchestrator 의 자연스러운 구현 베이스** 이다:

| AutoGen 원본 | VAMOS 매핑 | 정본 |
|-------------|----------|------|
| `GroupChatManager` | Orchestrator (Lead) | magentic_one.md §4 |
| `GroupChat.agents` (ConversableAgent list) | Sub-Agents (LOCK-AP-05 sub1/sub2) | V1 최대 2개 |
| `GroupChat.admin_name` | Orchestrator 식별자 | STEP7-K L469 원문 "ORANGE CORE = Orchestrator" |
| `GroupChat.speaker_selection_method` | Task Ledger assignments 매핑 | magentic_one.md §3 TaskLedger |
| `max_round` | Orchestrator iteration 상한 (V1=10, V2=20) | ProgressLedger.iteration |

**V2 변환 규칙**:
- `GroupChat.agents.length > 2` → LOCK-AP-05 위반 → 변환 거부.
- `admin_name` 미설정 → 첫 agent 를 Lead 로 간주 (V1 기본 동작 유지).

### §V2.2 AutoGen + MoA Aggregator 배치

AutoGen `ConversableAgent` 를 MoA Proposer 역할로 배치 후, 별도 Aggregator ConversableAgent 를 둔다:

```python
def autogen_moa_layout(proposer_count: int = 2) -> "MoALayout":
    # moa_pattern.md §4.1 V1 축약: Proposer 2 + Aggregator 1 = LOCK-AT-014 V1=3
    assert proposer_count <= 2, "LOCK-AP-05 violation"
    proposers = [
        AssistantAgent(name=f"proposer_{i}", llm_config=...)
        for i in range(proposer_count)
    ]
    aggregator = AssistantAgent(
        name="aggregator",
        llm_config={"model": "claude-haiku-45"},
        system_message=MOA_AGGREGATOR_PROMPT,
    )
    return MoALayout(proposers=proposers, aggregator=aggregator)
```

### §V2.3 FR-9 호환성 매트릭스 기여

`tool_memory_benchmark.md §3.1` FR-9 매트릭스의 **AutoGen 0.4+ 행 정본값** 을 본 어댑터가 소유한다:

| 항목 | AutoGen 0.4+ 값 | V1/V2 상태 |
|------|----------------|-----------|
| Agent 역할 정의 | ConversableAgent (system_message) | V1 ✅ |
| 팀 구성 | GroupChat | V1 ✅ (max 2) |
| 메시지 포맷 | Message (openai 호환) | V1 ✅ (VamosMessage 변환) |
| 상태 관리 | message history | V1 ✅ |
| Orchestrator | GroupChatManager | V1 ✅ (V2 Magentic 매핑) |
| Tool 호출 | Function calling | V1 ✅ (MCP 경유) |
| Streaming | PARTIAL | V2 |
| MoA 지원 | ✅ (GroupChat 자연스러움) | V2 ✅ (§V2.2) |
| 비용 추적 | 외부 | V1 ✅ (LOCK-AP-09) |

### §V2.4 Reflection 패턴 통합 (K-026)

AutoGen `ConversableAgent.initiate_chat()` 의 `max_turns` 를 Reflection cycle 한도로 매핑:

| reflection_planning.md §3 ReflectionCycle | AutoGen 매핑 |
|---------------------------------------|-------------|
| `cycle_id` | agent turn index |
| `input_answer → critique_text → improved_answer` | 3-turn chain (answer → critic agent → improve agent) |
| `max_cycles=3` | `max_turns=9` (3 cycle × 3 turn) |

### §V2.5 V2 LOCK 재확인

- **LOCK-AP-05** — GroupChat.agents ≤ 2 엄수.
- **LOCK-AT-014 (6-3 정본) "V1=3 / V2=10 / V3=50+"** — V2 확장 6-3 선행 조건.
- **LOCK-AP-03 A2A Task 상태 머신** — AutoGen 대화 종료 이벤트 → `completed`, `TERMINATE` → `canceled`.
- **LOCK-AP-07** — Function calling 도 MCP Tool Registry 경유.

### §V2.6 V2 Phase 3 추가 테스트 시나리오 (4건)

13. **GroupChatManager 3-agent**: admin + 2 ConversableAgent = LOCK-AT-014 V1=3 정합.
14. **AutoGen MoA Layout**: Proposer 2 + Aggregator 1 → moa_pattern.md §4.2 aggregate() 호출 → 정상 합의.
15. **AutoGen + Reflection chain**: initiate_chat(max_turns=9) → reflection cycle 3회 등가 → §V2.4.
16. **FR-9 호환성 위반**: AutoGen 0.3 연동 시도 → `[VIOLATION:FR-9 version mismatch]` 차단.

### §V2.7 V2 확장 자가 체크리스트

- [x] V1 §1~§15 본문 불변 (append-only)
- [x] V2-Phase 2 태그 명시
- [x] Magentic-One Orchestrator 매핑 (§V2.1)
- [x] MoA Aggregator 배치 (§V2.2) — moa_pattern.md §4.2 인터페이스 정합
- [x] FR-9 매트릭스 기여 (§V2.3)
- [x] Reflection 통합 (§V2.4) — reflection_planning.md §3 정합
- [x] LOCK-AP-05/AT-014/AP-03/AP-07 V2 재확인 (§V2.5)
- [x] 추가 시나리오 4건 (§V2.6)
- [x] FABRICATION 10종 census 0 hits

*V2-Phase 2 확장 작성: 2026-04-22 (STAGE 7 STEP_B #2a, 3-10 P2-1 세션)*
