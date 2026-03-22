# VAMOS Agent Teams 통합 설계 명세서

> **문서 ID**: S7-A-001-FULL
> **버전**: v1.0.0 | **생성일**: 2026-02-23
> **원본 참조**: D2.0-02 §12 (S7-A-001 TITLE_ONLY) → 본 문서에서 95~100% 상세 확장
> **소스**: D2.0-02 (ORANGE CORE), D2.0-03 (BLUE NODES), D2.0-05 (AGENT WORKFLOW), D2.0-07 (SAFETY/COST/APPROVAL), STEP7 작업가이드, STEP7-K (에이전트 프로토콜)
> **LOCK 기준**: VAMOS RULE 1.3 BASE, PLAN-3.0, DESIGN 2.0 전 문서

---

## 목차

1. [시스템 개요 및 설계 철학](#1-시스템-개요-및-설계-철학)
2. [Agent Teams 아키텍처](#2-agent-teams-아키텍처)
3. [위임(Delegation) 시스템](#3-위임delegation-시스템)
4. [Agent 유형별 상세](#4-agent-유형별-상세)
5. [협업 패턴](#5-협업-패턴)
6. [VAMOS 기존 시스템 통합](#6-vamos-기존-시스템-통합)
7. [Pydantic v2 스키마](#7-pydantic-v2-스키마)
8. [API 엔드포인트](#8-api-엔드포인트)
9. [V1/V2/V3 로드맵](#9-v1v2v3-로드맵)
10. [LOCK 결정사항](#10-lock-결정사항)
11. [안전/비용 제약](#11-안전비용-제약)

---

# 1. 시스템 개요 및 설계 철학

## 1.1 목적

VAMOS Agent Teams는 Claude Agent Teams 패턴(Lead Agent + Sub-agents 위임 구조)을 VAMOS 고유의 3계층 아키텍처(ORANGE CORE → BLUE NODES → OTHER BRAINS)에 통합하여, 복합 작업을 다수의 전문화된 에이전트가 협업으로 수행하는 시스템이다.

**핵심 가치**:
- **단일결정 원칙(Single Decision Principle)**: 최종 결론은 반드시 ORANGE CORE(Lead Agent)가 확정한다
- **위임 기반 실행(Delegation-Based Execution)**: Lead는 계획만 수립하고 실행은 Sub-agents에 위임한다
- **Gate 선행 원칙(Gate-First Principle)**: 모든 에이전트 실행은 07 Gate(PolicyCheck/Approval/Cost)를 선행 통과해야 한다
- **격리된 컨텍스트(Isolated Context)**: 에이전트 간 자유 상호 호출/무한 대화 금지, 제어된 메시징만 허용

## 1.2 VAMOS ↔ Claude Agent Teams 매핑

| Claude Agent Teams | VAMOS 대응 | 설명 |
|-------------------|-----------|------|
| Lead Agent (Orchestrator) | **ORANGE CORE** (I-5 Decision Engine) | 계획 수립, 작업 분배, 결과 검증, 최종 결론 확정 |
| Sub-Agent (Worker) | **BLUE NODE** (도메인 실행 모듈) | 도메인별 전문 작업 수행 |
| Tool Use | **OTHER BRAINS** + MCP Servers | 외부 도구/API 호출, ToolRegistry 경유 |
| Shared Context | **Context Variables** (§12.5.3) | trace_id 기반 워크플로우 전체 공유 변수 |
| Handoff | **AgentHandoff Protocol** (§12.4.5) | 에이전트 간 작업 인계 |

**차이점(VAMOS 차별화)**:
- VAMOS는 **5-Gate 안전장치**(G0~G4)가 전 파이프라인에 내장되어 있어 Claude Teams에는 없는 정책/비용/승인 제어를 제공한다
- **P0/P1/P2 도메인 분류**에 의한 계층적 접근 제어가 에이전트 수준에서 적용된다
- **비용 추적이 에이전트 단위**로 분리되어 리드는 Opus급, 팀원은 Sonnet/Haiku급 등 차등 모델 사용이 가능하다

## 1.3 아키텍처 다이어그램

```
┌─────────────────────────────────────────────────────────────────────┐
│                        VAMOS AGENT TEAMS                            │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    ORANGE CORE (Lead Agent)                    │  │
│  │                                                               │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐│  │
│  │  │ I-1      │ │ I-5      │ │ I-6      │ │ I-8              ││  │
│  │  │ Intent   │ │ Decision │ │ Self-    │ │ Policy           ││  │
│  │  │ Parser   │ │ Engine   │ │ Check    │ │ Engine           ││  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────────┘│  │
│  │                                                               │  │
│  │  ┌──────────────────────────────────────────────────────────┐│  │
│  │  │            Task Decomposer + Delegation Engine           ││  │
│  │  │  plan() → decompose() → assign() → monitor() → merge()  ││  │
│  │  └──────────────────────────────────────────────────────────┘│  │
│  └───────────────┬───────────────┬───────────────┬──────────────┘  │
│                  │               │               │                  │
│         ┌────────▼──────┐ ┌─────▼───────┐ ┌─────▼───────┐         │
│         │  MessageBus   │ │  TaskBoard  │ │  EventBus   │         │
│         │  (메시지 큐)   │ │  (작업 보드) │ │  (이벤트)    │         │
│         └───┬───┬───┬───┘ └─────────────┘ └─────────────┘         │
│             │   │   │                                               │
│  ┌──────────▼┐ ┌▼────────┐ ┌▼──────────┐ ┌───────────┐            │
│  │ Research  │ │ Coding   │ │ Quant     │ │ Content   │  ...       │
│  │ Agent     │ │ Agent    │ │ Agent     │ │ Agent     │            │
│  │ (Blue     │ │ (Blue    │ │ (Blue     │ │ (Blue     │            │
│  │  Node)    │ │  Node)   │ │  Node)    │ │  Node)    │            │
│  └─────┬─────┘ └────┬────┘ └─────┬─────┘ └─────┬─────┘            │
│        │            │            │              │                   │
│  ┌─────▼────────────▼────────────▼──────────────▼──────────┐       │
│  │              OTHER BRAINS + MCP Servers                  │       │
│  │  [Web Search] [Code Exec] [Financial API] [RAG] [...]   │       │
│  └──────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                 07 SAFETY / COST / APPROVAL                  │   │
│  │  [G0 Input] [G1 Policy] [G2 Cost] [G3 Quality] [G4 Final]  │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
```

---

# 2. Agent Teams 아키텍처

## 2.1 Lead Agent 역할 및 책임

Lead Agent는 ORANGE CORE의 Decision Engine(I-5)을 확장한 오케스트레이터이다.

### 2.1.1 역할 정의 (LOCK)

| 역할 | 설명 | 제약 |
|------|------|------|
| **계획 수립 (Planning)** | 사용자 요청을 분석하고 실행 계획을 수립한다 | TEE Think 단계에서 수행 |
| **작업 분배 (Assignment)** | 계획을 하위 작업으로 분해하여 적합한 Sub-agent에 할당한다 | 할당 전 G1(정책)/G2(비용) 통과 필수 |
| **진행 감독 (Monitoring)** | Sub-agent의 진행 상황을 실시간 추적한다 | LogEvent 기록, 타임아웃 감시 |
| **결과 병합 (Merging)** | Sub-agent 결과를 수집하여 최종 응답을 구성한다 | 충돌 해결은 Lead만 수행 |
| **품질 검증 (Verification)** | 병합된 결과의 품질을 Self-check + EVX 체인으로 검증한다 | QoD 기준 미달 시 Soft loop |
| **최종 결론 확정 (Decision Lock)** | S3_DECISION_LOCKED 상태로 전이하여 결론을 잠근다 | 단일결정 원칙 적용 |

**핵심 제약**: Lead Agent는 **직접 코드 작성, 데이터 분석, 웹 검색 등 실행 작업을 수행하지 않는다**. 모든 실행은 Sub-agent에 위임한다 (S7-A-001 정의).

### 2.1.2 Lead Agent 상태 머신

```
IDLE → PLANNING → ASSIGNING → MONITORING → MERGING → VERIFYING → DELIVERING → IDLE
  │                                 │            │
  │                                 ▼            ▼
  │                            ESCALATING   SOFT_LOOPING
  │                            (사용자에게   (재실행 요청)
  │                             승인 요청)
  └────────────────── ABORTED (Gate deny 또는 비용 초과)
```

### 2.1.3 Lead Agent 코드 구조

```python
class LeadAgent:
    """ORANGE CORE의 Agent Teams 오케스트레이터.

    Lead Agent는 직접 실행하지 않고, 계획-분배-감독-병합만 수행한다.
    모든 실행은 Sub-agent(BLUE NODE)에 위임된다.
    """

    def __init__(self, config: AgentTeamConfig):
        self.team_id: str = generate_team_id()
        self.config = config
        self.task_board = TaskBoard()
        # [PART1 SP-01] V1: MessageBus 미구현(V2 전용). V1은 in-memory direct dispatcher 사용
        self.message_bus = InMemoryDispatcher()  # V1: direct dispatch, V2+: MessageBus(Redis)
        self.sub_agents: Dict[str, SubAgent] = {}
        self.cost_tracker = CostTracker(budget=config.budget)
        self.gate_client = GateClient()  # 07 Gate 연동

    async def plan(self, user_request: UserRequest) -> DelegationPlan:
        """TEE Think: 사용자 요청 분석 → 실행 계획 수립"""
        # G1 정책 검사
        policy_result = await self.gate_client.check_policy(user_request)
        if policy_result.status == "deny":
            raise PolicyDenyError(policy_result.reason)

        # G2 비용 예측
        cost_estimate = await self.cost_tracker.estimate(user_request)
        if cost_estimate.exceeds_budget:
            raise CostExceededError(cost_estimate)

        # 작업 분해
        tasks = await self._decompose_task(user_request)

        # 에이전트 할당 결정
        assignments = await self._assign_agents(tasks)

        return DelegationPlan(
            team_id=self.team_id,
            trace_id=user_request.trace_id,
            tasks=tasks,
            assignments=assignments,
            estimated_cost=cost_estimate,
            max_parallel=self.config.max_parallel_agents,
        )

    async def execute_plan(self, plan: DelegationPlan) -> TeamResult:
        """TEE Execute: 계획에 따라 Sub-agent에 작업 위임"""
        results: Dict[str, AgentResult] = {}

        # 순차/병렬 실행 전략에 따라 실행
        for batch in plan.execution_batches:
            batch_results = await asyncio.gather(*[
                self._delegate_to_agent(assignment)
                for assignment in batch
            ])
            for result in batch_results:
                results[result.task_id] = result

        # 결과 병합
        merged = await self._merge_results(results, plan)

        # TEE Evaluate: 품질 검증
        verified = await self._verify_result(merged)

        return TeamResult(
            team_id=self.team_id,
            trace_id=plan.trace_id,
            merged_result=verified,
            agent_results=results,
            total_cost=self.cost_tracker.total_spent,
        )

    async def _delegate_to_agent(self, assignment: AgentAssignment) -> AgentResult:
        """Sub-agent에 작업 위임 (V1: InMemoryDispatcher / V2+: MessageBus 경유)"""
        agent = self.sub_agents[assignment.agent_id]

        # 위임 메시지 전송
        message = DelegationMessage(
            task_id=assignment.task_id,
            task_spec=assignment.task_spec,
            context=assignment.context,
            constraints=assignment.constraints,
            deadline=assignment.deadline,
        )

        # LogEvent 기록
        await log_event("agent.delegation.sent", {
            "team_id": self.team_id,
            "agent_id": assignment.agent_id,
            "task_id": assignment.task_id,
        })

        # [PART1 SP-01] V1: direct dispatch (in-memory), V2+: MessageBus.send_and_wait(Redis)
        result = await self.message_bus.send_and_wait(
            target=agent.agent_id,
            message=message,
            timeout=assignment.timeout,
        )

        return result
```

## 2.2 Sub-Agent 유형 및 분류 (BLUE NODE 매핑)

### 2.2.1 Sub-Agent ↔ BLUE NODE 매핑 테이블

| Sub-Agent 유형 | BLUE NODE | P등급 | 모델 Tier | 주요 Skill | MCP 도구 |
|---------------|-----------|-------|-----------|-----------|----------|
| **Research Agent** | Research Node | P0 | Sonnet | web_search, rag, fact_check | Brave Search, Exa |
| **Coding Agent** | Dev Node | P0 | Sonnet/Haiku | code_gen, debug, refactor, test | GitHub, Docker |
| **Quant Agent** | Data & Quant Node | P1 | Sonnet | data_analysis, backtest, visualization | yfinance, DART API |
| **Content Agent** | Content Node | P1 | Haiku | document_write, translate, summarize | Markdown, PDF |
| **Trading Analysis Agent** | Trading Node | P2 | Opus | investment_analysis, portfolio_opt, risk_calc | Broker API (Paper) |
| **SDAR Agent** | SDAR Module (I-25) | P0 | Haiku/Sonnet | self_diagnosis, auto_repair, health_check | System Monitor |
| **Critic Agent** | (내부 검증용) | P0 | Sonnet | verify, adversarial_check, fact_check | - |
| **Productivity Agent** | Productivity Node | P0 | Haiku | scheduling, reminders, note_taking | Calendar, Todo |

### 2.2.2 Sub-Agent 기본 인터페이스

```python
class SubAgent(ABC):
    """BLUE NODE 기반 Sub-Agent 베이스 클래스.

    모든 Sub-Agent는 이 인터페이스를 구현해야 한다.
    CORE 규칙(Non-goal/승인/비용/저장)을 동일하게 상속한다.
    """

    agent_id: str
    agent_type: AgentType
    node_id: str           # 연결된 BLUE NODE ID
    model_tier: ModelTier  # opus | sonnet | haiku
    skills: List[str]
    tools: List[str]       # 사용 가능한 MCP 도구
    permission_policy: AgentPermissionPolicy

    @abstractmethod
    async def execute(self, task: AgentTask) -> AgentResult:
        """주어진 작업을 수행하고 결과를 반환한다."""
        ...

    @abstractmethod
    async def report_progress(self) -> ProgressReport:
        """현재 진행 상황을 보고한다."""
        ...

    async def request_help(self, reason: str) -> None:
        """Lead Agent에게 도움을 요청한다 (EventBus 경유)."""
        await self.event_bus.emit("agent.needs_help", {
            "agent_id": self.agent_id,
            "task_id": self.current_task_id,
            "reason": reason,
        })
```

## 2.3 Agent 간 통신 프로토콜

### 2.3.0 V1/V2 통신 방식 구분 (LOCK)

| 버전 | 통신 방식 | 구현 | 근거 |
|------|----------|------|------|
| **V1** | **Lead Agent 경유 단방향 위임만** | `InMemoryDispatcher` — Sub-agent 간 직접 A2A 금지, 모든 메시지는 Lead를 경유 | D2.0-03 §1.4 FREEZE, READINESS_GUIDE V2-003 |
| **V2+** | **MessageBus (Redis) 경유** | `RedisMessageBus` — Pub/Sub 기반 다대다 통신, Sub-agent 간 HANDOFF 허용 (Lead 감사 하에) | DEFER-AT-001 Redis 확정 |

> V1에서 Sub-agent 간 직접 통신이 금지되는 이유: 에이전트 3개(Lead+2Sub) 환경에서 메시지 순서 보장과 디버깅 단순화를 위해 Lead 허브 패턴을 적용한다.

### 2.3.1 메시지 포맷 (LOCK)

Agent 간 모든 통신은 **MessageBus**를 경유하며, ORANGE CORE가 모든 메시지를 감사(audit)한다. 에이전트 간 직접 상호 호출은 금지된다 (D2.0-03 §1.4 FREEZE).

```python
class AgentMessage(BaseModel):
    """에이전트 간 표준 메시지 포맷"""

    message_id: str = Field(default_factory=lambda: f"msg_{ulid.new()}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # V1-005: utcnow() deprecated → now(timezone.utc)
    trace_id: str                    # 워크플로우 trace_id (일관성 유지)
    team_id: str                     # Agent Team ID
    sender_id: str                   # 발신 에이전트 ID
    receiver_id: str                 # 수신 에이전트 ID
    message_type: MessageType        # delegation | result | progress | handoff | help_request
    priority: Priority               # critical | high | normal | low
    payload: Dict[str, Any]          # 메시지 본문
    context: Optional[Dict] = None   # 공유 컨텍스트 (읽기 전용)
    hmac_signature: str              # HMAC 무결성 검증 (S7E-078)

    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "msg_01HZ0001ABCDEF",
                "trace_id": "tr_01HZXXABCDEF",
                "team_id": "team_01HZ001",
                "sender_id": "lead_001",
                "receiver_id": "research_agent_001",
                "message_type": "delegation",
                "priority": "normal",
                "payload": {
                    "task_id": "task_001",
                    "instruction": "최근 NVIDIA 실적 리포트를 분석하세요",
                    "constraints": {"max_tokens": 4000, "deadline_seconds": 120}
                },
                "hmac_signature": "sha256:abc123..."
            }
        }

class MessageType(str, Enum):
    DELEGATION = "delegation"          # Lead → Sub: 작업 위임
    RESULT = "result"                  # Sub → Lead: 결과 반환
    PROGRESS = "progress"              # Sub → Lead: 진행 보고
    HANDOFF = "handoff"                # Sub → Sub: 작업 인계 (Lead 경유)
    HELP_REQUEST = "help_request"      # Sub → Lead: 도움 요청
    ABORT = "abort"                    # Lead → Sub: 작업 중단 명령
    CONTEXT_UPDATE = "context_update"  # Lead → All: 컨텍스트 업데이트
```

### 2.3.2 이벤트 시스템

```python
class AgentEvent(str, Enum):
    """에이전트 라이프사이클 이벤트 (LogEvent에 기록)"""

    # 팀 이벤트
    TEAM_CREATED = "agent.team.created"
    TEAM_STARTED = "agent.team.started"
    TEAM_COMPLETED = "agent.team.completed"
    TEAM_ABORTED = "agent.team.aborted"

    # 위임 이벤트
    DELEGATION_SENT = "agent.delegation.sent"
    DELEGATION_ACCEPTED = "agent.delegation.accepted"
    DELEGATION_REJECTED = "agent.delegation.rejected"
    DELEGATION_TIMEOUT = "agent.delegation.timeout"

    # 에이전트 라이프사이클
    AGENT_SPAWNED = "agent.spawned"
    AGENT_ACTIVE = "agent.active"
    AGENT_SUSPENDED = "agent.suspended"
    AGENT_TERMINATED = "agent.terminated"

    # 협업 이벤트
    HANDOFF_INITIATED = "agent.handoff.initiated"
    HANDOFF_COMPLETED = "agent.handoff.completed"
    PROGRESS_REPORTED = "agent.progress.reported"
    HELP_REQUESTED = "agent.help.requested"

    # 안전 이벤트
    GATE_CHECKED = "agent.gate.checked"
    COST_WARNING = "agent.cost.warning"
    COST_EXCEEDED = "agent.cost.exceeded"
    PERMISSION_DENIED = "agent.permission.denied"
```

### 2.3.3 MessageBus 아키텍처

```
┌──────────────┐     ┌─────────────────────────────┐     ┌──────────────┐
│  Lead Agent  │────>│       MessageBus             │────>│ Sub-Agent A  │
│              │<────│                               │<────│              │
└──────────────┘     │  ┌───────────────────────┐   │     └──────────────┘
                     │  │  ORANGE CORE Auditor   │   │
                     │  │  - 메시지 감사          │   │     ┌──────────────┐
                     │  │  - HMAC 검증           │   │────>│ Sub-Agent B  │
                     │  │  - 정책 필터링          │   │<────│              │
                     │  │  - 비용 모니터링        │   │     └──────────────┘
                     │  └───────────────────────┘   │
                     │                               │     ┌──────────────┐
                     │  ┌───────────────────────┐   │────>│ Sub-Agent C  │
                     │  │  Message Queue         │   │<────│              │
                     │  │  (In-Memory / Redis)   │   │     └──────────────┘
                     │  └───────────────────────┘   │
                     └─────────────────────────────┘
```

**통신 보안 규칙** (S7E-078):
- 모든 메시지에 HMAC 무결성 서명 필수
- Agent ID 인증 (허위 Agent 방지)
- 전송 암호화 (TLS 1.3)
- 민감 정보 자동 마스킹

## 2.4 Agent Lifecycle (생성 → 할당 → 실행 → 보고 → 종료)

### 2.4.1 상태 흐름 (LOCK)

```
created → initialized → active → (suspended | terminated) → archived
   │           │          │            │           │
   │           │          │            │           └──> 이력 보존 (06 STORAGE)
   │           │          │            └──> 리소스 부족/정책 위반
   │           │          └──> 태스크 수행 가능
   │           └──> 도구 연결 + Skill 로드 + Gate 등록
   └──> 프로필 + 기본 설정
```

### 2.4.2 라이프사이클 상세

| 단계 | 상태 | 동작 | LogEvent |
|------|------|------|----------|
| **생성 (Created)** | `created` | AgentProfile 생성, model_tier 할당, 기본 permission 설정 | `agent.spawned` |
| **초기화 (Initialized)** | `initialized` | MCP 도구 연결, Skill 로드, ToolRegistry 등록, Gate 등록 | `agent.initialized` |
| **활성 (Active)** | `active` | 태스크 수신 대기 → 수신 시 TEE 루프 진입 → 결과 반환 | `agent.active` |
| **일시정지 (Suspended)** | `suspended` | 리소스 부족/비용 초과/정책 위반 시 자동 전환. 현재 상태 체크포인트 저장 | `agent.suspended` |
| **종료 (Terminated)** | `terminated` | 태스크 완료 또는 에러. 결과 반환 후 리소스 해제 | `agent.terminated` |
| **보관 (Archived)** | `archived` | 실행 이력/결과를 06(STORAGE) L2 프로젝트 메모리에 보존 | `agent.archived` |

### 2.4.3 라이프사이클 코드

```python
class AgentLifecycleManager:
    """에이전트 라이프사이클 관리자"""

    async def spawn_agent(
        self,
        agent_type: AgentType,
        model_tier: ModelTier,
        skills: List[str],
        budget: CostBudget,
    ) -> SubAgent:
        """에이전트 생성 → 초기화 → 활성화"""

        # 1. 생성
        agent = AgentFactory.create(agent_type, model_tier)
        await log_event(AgentEvent.AGENT_SPAWNED, {"agent_id": agent.agent_id})

        # 2. 초기화: 도구 연결 + Skill 로드
        tools = await self.tool_registry.get_tools_for(agent_type)
        for tool in tools:
            await agent.register_tool(tool)

        # 3. Gate 등록
        await self.gate_client.register_agent(agent.agent_id, agent.permission_policy)

        # 4. 비용 할당
        agent.cost_tracker = CostTracker(budget=budget)

        # 5. 활성화
        agent.state = AgentState.ACTIVE
        await log_event(AgentEvent.AGENT_ACTIVE, {"agent_id": agent.agent_id})

        return agent

    async def terminate_agent(self, agent: SubAgent, reason: str) -> None:
        """에이전트 종료 + 리소스 해제"""
        agent.state = AgentState.TERMINATED

        # 결과 보관
        await self.storage.archive_agent_history(agent.agent_id)

        # 리소스 해제
        await agent.release_tools()
        await self.gate_client.unregister_agent(agent.agent_id)

        await log_event(AgentEvent.AGENT_TERMINATED, {
            "agent_id": agent.agent_id,
            "reason": reason,
            "total_cost": agent.cost_tracker.total_spent,
        })
```

---

# 3. 위임(Delegation) 시스템

## 3.1 위임 결정 알고리즘

Lead Agent는 다음 알고리즘으로 작업을 분해하고 위임 대상을 결정한다.

### 3.1.1 위임 결정 흐름

```
사용자 요청
    │
    ▼
[1. 의도 분석] ──── I-1 Intent Parser
    │
    ▼
[2. 복잡도 판정] ──── 단일 작업? 복합 작업?
    │                      │
    │ (단일)               │ (복합)
    ▼                      ▼
[직접 라우팅]      [3. 작업 분해 (Task Decomposition)]
(기존 파이프라인)          │
                          ▼
                   [4. 에이전트 매칭 (Agent Matching)]
                          │
                          ▼
                   [5. 비용 예측 (Cost Estimation)]
                          │
                          ▼
                   [6. Gate 검증] ──── G1(정책) + G2(비용)
                          │
                          ▼ (pass)
                   [7. 위임 실행 (Delegation)]
```

### 3.1.2 에이전트 매칭 스코어링

```python
class AgentMatcher:
    """작업-에이전트 매칭 알고리즘"""

    def match(self, task: AgentTask, available_agents: List[SubAgent]) -> AgentAssignment:
        """최적의 에이전트를 선택하여 할당한다."""

        scores = []
        for agent in available_agents:
            score = self._calculate_match_score(task, agent)
            scores.append((agent, score))

        # 점수 내림차순 정렬
        scores.sort(key=lambda x: x[1].total, reverse=True)
        best_agent, best_score = scores[0]

        if best_score.total < self.min_match_threshold:
            raise NoSuitableAgentError(task, scores)

        return AgentAssignment(
            task_id=task.task_id,
            agent_id=best_agent.agent_id,
            match_score=best_score,
        )

    def _calculate_match_score(self, task: AgentTask, agent: SubAgent) -> MatchScore:
        """매칭 점수 산출 (0.0~1.0)"""

        # 1. 스킬 적합도 (40%)
        skill_overlap = len(set(task.required_skills) & set(agent.skills))
        skill_score = skill_overlap / len(task.required_skills) if task.required_skills else 0

        # 2. 도구 가용성 (20%)
        tool_overlap = len(set(task.required_tools) & set(agent.tools))
        tool_score = tool_overlap / len(task.required_tools) if task.required_tools else 1.0

        # 3. 비용 효율 (20%)
        cost_score = 1.0 - (agent.estimated_cost(task) / task.budget_limit)
        cost_score = max(0.0, min(1.0, cost_score))

        # 4. 현재 부하 (10%)
        load_score = 1.0 - (agent.current_load / agent.max_capacity)

        # 5. 과거 성공률 (10%)
        history_score = agent.success_rate_for(task.domain)

        return MatchScore(
            skill=skill_score * 0.4,
            tool=tool_score * 0.2,
            cost=cost_score * 0.2,
            load=load_score * 0.1,
            history=history_score * 0.1,
            total=skill_score*0.4 + tool_score*0.2 + cost_score*0.2 + load_score*0.1 + history_score*0.1,
        )
```

## 3.2 Task Decomposition (복합 작업 → 하위 작업 분해)

### 3.2.1 분해 전략

| 전략 | 설명 | 사용 시점 |
|------|------|----------|
| **Sequential Decomposition** | A→B→C 순서 의존 분해 | 이전 단계 결과가 다음 단계 입력인 경우 |
| **Parallel Decomposition** | A, B, C 독립 병렬 분해 | 서로 독립적인 하위 작업 |
| **Hybrid Decomposition** | (A‖B)→C 혼합 분해 | 병렬+순차 복합 패턴 |
| **Recursive Decomposition** | A → (A1, A2(→A2.1, A2.2)) 재귀 분해 | 하위 작업이 다시 복합 작업인 경우 |

### 3.2.2 분해 알고리즘

```python
class TaskDecomposer:
    """복합 작업 → 하위 작업 분해기"""

    async def decompose(self, request: UserRequest) -> List[AgentTask]:
        """사용자 요청을 실행 가능한 하위 작업으로 분해한다."""

        # LLM을 사용하여 작업 분해 (Lead Agent의 모델)
        decomposition_prompt = self._build_decomposition_prompt(request)
        raw_plan = await self.llm.generate(decomposition_prompt)

        # 구조화된 태스크 목록으로 파싱
        tasks = self._parse_tasks(raw_plan)

        # 의존성 그래프 생성
        dependency_graph = self._build_dependency_graph(tasks)

        # 실행 배치 계산 (병렬 가능 그룹)
        execution_batches = self._topological_batch(dependency_graph)

        # 각 태스크에 예상 비용/시간 할당
        for task in tasks:
            task.estimated_cost = await self._estimate_task_cost(task)
            task.estimated_duration = await self._estimate_task_duration(task)

        return tasks

    def _topological_batch(self, graph: Dict) -> List[List[AgentTask]]:
        """의존성 그래프를 위상 정렬하여 병렬 실행 가능한 배치로 나눈다.

        예: A→C, B→C, C→D 이면
            batch_0: [A, B]  (병렬)
            batch_1: [C]     (A,B 완료 후)
            batch_2: [D]     (C 완료 후)
        """
        # 위상 정렬 + 레벨 그룹핑
        ...
```

### 3.2.3 분해 예시: "NVIDIA 종합 투자 분석 리포트 작성"

```yaml
decomposition:
  request: "NVIDIA 종합 투자 분석 리포트 작성"
  strategy: hybrid

  tasks:
    - task_id: T1
      name: "실적/재무 데이터 수집"
      agent_type: research
      skills: [web_search, financial_data]
      dependencies: []
      batch: 0  # 병렬 실행

    - task_id: T2
      name: "기술 차트 분석"
      agent_type: quant
      skills: [chart_analysis, technical_indicator]
      dependencies: []
      batch: 0  # 병렬 실행

    - task_id: T3
      name: "뉴스/감성 분석"
      agent_type: research
      skills: [news_search, sentiment_analysis]
      dependencies: []
      batch: 0  # 병렬 실행

    - task_id: T4
      name: "경쟁사 비교 분석"
      agent_type: research
      skills: [web_search, comparative_analysis]
      dependencies: []
      batch: 0  # 병렬 실행

    - task_id: T5
      name: "리스크 평가"
      agent_type: quant  # Trading Node도 가능
      skills: [risk_assessment, var_calculation]
      dependencies: [T1, T2]
      batch: 1  # T1, T2 완료 후

    - task_id: T6
      name: "종합 리포트 작성"
      agent_type: content
      skills: [report_generation, summarization]
      dependencies: [T1, T2, T3, T4, T5]
      batch: 2  # 전체 완료 후

    - task_id: T7
      name: "결과 검증 (Critic)"
      agent_type: critic
      skills: [fact_check, adversarial_check]
      dependencies: [T6]
      batch: 3  # 리포트 완료 후
```

## 3.3 위임 체인 (Lead → Sub → Sub-sub 계층)

### 3.3.1 위임 체인 구조

```
Level 0: Lead Agent (ORANGE CORE)
    │
    ├── Level 1: Research Agent ──── 직접 실행 (MCP 도구 호출)
    │
    ├── Level 1: Coding Agent
    │       │
    │       └── Level 2: Test Runner Sub-agent ──── 테스트 실행
    │
    └── Level 1: Quant Agent
            │
            └── Level 2: Backtesting Sub-agent ──── 백테스팅 실행
                    │
                    └── Level 3: ❌ 금지 (최대 깊이 초과)
```

### 3.3.2 위임 체인 규칙 (LOCK)

| 규칙 | 값 | 근거 |
|------|------|------|
| **최대 위임 깊이** | 3단계 (Lead → Sub → Sub-sub) | S7E-080 Delegation Attack 방어 |
| **최대 병렬 에이전트** | V1=3, V2=10, V3=50+ | S7-A-008, D2.0-05 §12 |
| **위임 시 권한** | 원래 요청자(OWNER)의 권한으로 실행 | 권한 상속/상승 방지 |
| **위임 감사** | ORANGE CORE가 모든 위임 요청 감사 | S7E-080 |
| **위임 타임아웃** | P0=30초, P1=120초, P2=300초 | 비용 제어 |

## 3.4 위임 제약 (LOCK)

```python
class DelegationConstraints(BaseModel):
    """위임 제약 사항 (LOCK)"""

    # 깊이 제한
    max_delegation_depth: int = 3               # 최대 위임 깊이

    # 병렬 제한
    max_parallel_agents_v1: int = 3             # V1: 최대 3 병렬
    max_parallel_agents_v2: int = 10            # V2: 최대 10 병렬
    max_parallel_agents_v3: int = 50            # V3: 최대 50 병렬

    # 비용 제한
    agent_budget_ratio: float = 0.8             # 팀 예산의 80%까지 Sub-agent에 할당
    lead_agent_budget_ratio: float = 0.2        # 리드는 20% (계획/검증용)

    # 시간 제한
    delegation_timeout_p0: int = 30             # 초
    delegation_timeout_p1: int = 120
    delegation_timeout_p2: int = 300

    # 대화 턴 제한 (D2.0-05 §12.4.4)
    max_conversation_turns_p0: int = 5
    max_conversation_turns_p1: int = 10
    max_conversation_turns_p2: int = 20

    # TEE 루프 제한 (D2.0-05 §12.5.1)
    max_tee_iterations_p0: int = 3
    max_tee_iterations_p1: int = 5
    max_tee_iterations_p2: int = 10
```

---

# 4. Agent 유형별 상세

## 4.1 Research Agent (웹 검색, 문서 분석)

```python
class ResearchAgent(SubAgent):
    """Research Blue Node 기반 리서치 에이전트"""

    agent_type = AgentType.RESEARCH
    node_id = "blue_node_research"
    model_tier = ModelTier.SONNET

    skills = [
        "web_search",           # 실시간 웹 검색 (Brave Search MCP)
        "rag_retrieval",        # 로컬 벡터DB 검색 (Chroma)
        "document_analysis",    # 문서/PDF 분석
        "fact_check",           # 사실 확인
        "news_aggregation",     # 뉴스 수집/요약
        "sentiment_analysis",   # 감성 분석
    ]

    tools = [
        "brave_search",         # MCP: Brave Web Search
        "exa_search",           # MCP: Exa AI Search
        "arxiv_search",         # MCP: arXiv 논문 검색
        "news_api",             # MCP: 뉴스 API
        "rag_retriever",        # 내부: RAG 파이프라인
    ]

    async def execute(self, task: AgentTask) -> AgentResult:
        """리서치 작업 실행: 검색 → 분석 → 근거 수집"""
        # 1. 검색 쿼리 생성
        queries = await self._generate_search_queries(task)

        # 2. 멀티소스 검색 (병렬)
        search_results = await asyncio.gather(*[
            self._search_source(source, query)
            for source, query in queries
        ])

        # 3. 결과 랭킹 + 필터링
        ranked = await self._rank_and_filter(search_results)

        # 4. EvidenceBundle 구성
        evidence = EvidenceBundle(
            sources=ranked,
            confidence=self._calculate_confidence(ranked),
            search_metadata={"queries": queries, "total_results": len(search_results)},
        )

        return AgentResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            status="completed",
            output=evidence,
            cost=self.cost_tracker.current_cost,
        )
```

## 4.2 Coding Agent (코드 생성/디버깅/리팩토링)

```python
class CodingAgent(SubAgent):
    """Dev Blue Node 기반 코딩 에이전트"""

    agent_type = AgentType.CODING
    node_id = "blue_node_dev"
    model_tier = ModelTier.SONNET  # 코딩은 Sonnet이 비용 대비 최적

    skills = [
        "code_generation",      # 코드 작성
        "code_review",          # 코드 리뷰
        "debugging",            # 디버깅
        "refactoring",          # 리팩토링
        "test_writing",         # 테스트 작성
        "documentation",        # 코드 문서화
    ]

    tools = [
        "code_executor",        # 샌드박스 코드 실행 (Docker)
        "github_mcp",           # MCP: GitHub 연동
        "file_system",          # MCP: 파일 시스템 접근
        "linter",               # 코드 린터
        "test_runner",          # 테스트 실행기
    ]

    # 파일 소유권 (S7-A-004): 수정 가능 파일 영역 제한
    file_ownership: FileOwnership = FileOwnership(
        writable_paths=["src/", "tests/"],
        readonly_paths=["config/", "docs/"],
        forbidden_paths=[".env", "credentials/", "secrets/"],
    )
```

## 4.3 Quant Agent (데이터 분석, 백테스팅)

```python
class QuantAgent(SubAgent):
    """Data & Quant Blue Node 기반 정량 분석 에이전트"""

    agent_type = AgentType.QUANT
    node_id = "blue_node_quant"
    model_tier = ModelTier.SONNET

    skills = [
        "data_analysis",        # 데이터 분석
        "statistical_modeling",  # 통계 모델링
        "chart_analysis",       # 기술적 차트 분석
        "backtesting",          # 전략 백테스팅
        "portfolio_optimization", # 포트폴리오 최적화
        "risk_calculation",     # VaR/MDD 등 리스크 계산
    ]

    tools = [
        "yfinance",             # 금융 데이터
        "dart_api",             # DART 공시 데이터
        "backtrader",           # 백테스팅 엔진 (DEC-018)
        "vectorbt",             # 벡터 백테스팅 (전략 >= 3)
        "matplotlib_renderer",  # 차트 생성
    ]
```

## 4.4 Content Agent (문서 작성, 번역)

```python
class ContentAgent(SubAgent):
    """Content Blue Node 기반 콘텐츠 에이전트"""

    agent_type = AgentType.CONTENT
    node_id = "blue_node_content"
    model_tier = ModelTier.HAIKU  # 콘텐츠 생성은 Haiku로 비용 절감

    skills = [
        "document_writing",     # 문서/리포트 작성
        "summarization",        # 요약
        "translation",          # 번역 (한↔영 등)
        "formatting",           # 포맷팅 (Markdown, PDF)
        "proofreading",         # 교정
    ]

    tools = [
        "markdown_renderer",    # Markdown → HTML/PDF
        "pdf_generator",        # PDF 생성
        "chart_embedder",       # 차트 삽입
        "template_engine",      # 문서 템플릿
    ]
```

## 4.5 Trading Analysis Agent (투자 분석, AINV 연동)

```python
class TradingAnalysisAgent(SubAgent):
    """Trading Blue Node 기반 투자 분석 에이전트.

    주의: P2 등급 — 항상 명시적 승인 필요, 세션 종료 시 자동 OFF.
    실제 매매 실행은 절대 자동으로 수행하지 않는다.
    """

    agent_type = AgentType.TRADING_ANALYSIS
    node_id = "blue_node_trading"
    model_tier = ModelTier.OPUS  # 투자 분석은 최고 품질 모델
    priority_class = "P2"  # 승인 필수

    skills = [
        "investment_analysis",   # 종합 투자 분석
        "strategy_evaluation",   # 전략 평가
        "portfolio_review",      # 포트폴리오 리뷰
        "risk_assessment",       # 리스크 평가
        "market_commentary",     # 시장 해설
    ]

    tools = [
        "broker_api_paper",     # Paper Trading API만 (실전 X)
        "portfolio_optimizer",  # 포트폴리오 최적화
        "risk_calculator",      # VaR, Sharpe Ratio
        "policy_checker",       # 규제 확인
    ]

    # P2 제약
    requires_approval: bool = True
    auto_off_on_session_end: bool = True  # 세션 종료 시 자동 OFF
```

## 4.6 SDAR Agent (자가진단/자동복구)

```python
class SDARAgent(SubAgent):
    """SDAR(Self-Diagnosis & Auto-Repair) 에이전트.

    VAMOS 시스템 자체의 건강 상태를 모니터링하고,
    오류 발생 시 자동 또는 반자동으로 복구한다.
    VAMOS_SDAR_DESIGN_SPECIFICATION v1.0.0 참조.
    """

    agent_type = AgentType.SDAR
    node_id = "sdar_module_i25"
    model_tier = ModelTier.HAIKU  # 시스템 진단은 경량 모델

    skills = [
        "health_monitoring",    # 시스템 건강 상태 감시
        "error_detection",      # 오류 탐지
        "root_cause_analysis",  # 근본 원인 분석
        "auto_repair",          # 자동 수리 (AR-L2: 재시도/재시작)
        "incident_reporting",   # 장애 리포트 생성
    ]

    # Graduated Autonomy (단계적 자율 수준)
    autonomy_levels = {
        "AR-L0": "알림만 (사람이 결정)",
        "AR-L1": "제안 + 알림 (사람이 승인)",
        "AR-L2": "자동 실행 (안전: 재시도, 캐시 초기화, 재시작)",
        "AR-L3": "자동 실행 + 알림 (중간: Config/Prompt 패치, Reversible)",
        "AR-L4": "스냅샷 + 알림 (고위험: 코드 패치, Migration)",
    }
```

---

# 5. 협업 패턴

## 5.1 Sequential (순차 실행)

```
Agent A ──→ Agent B ──→ Agent C ──→ Lead (결과 병합)
  결과 A ─────→ 입력 B ─────→ 입력 C
```

**사용 시점**: 이전 단계 결과가 다음 단계의 필수 입력인 경우

```python
async def sequential_execution(plan: DelegationPlan) -> TeamResult:
    """순차 실행 패턴"""
    context = {}
    for task in plan.tasks:
        agent = team.agents[task.agent_id]
        result = await agent.execute(task.with_context(context))
        context[task.task_id] = result.output
    return merge_results(context)
```

**예시**: 코드 작성 → 코드 리뷰 → 테스트 작성 → 테스트 실행

## 5.2 Parallel (병렬 실행)

```
         ┌──→ Agent A ──┐
Lead ────┼──→ Agent B ──┼──→ Lead (결과 병합)
         └──→ Agent C ──┘
```

**사용 시점**: 서로 독립적인 하위 작업을 동시에 수행할 때

```python
async def parallel_execution(plan: DelegationPlan) -> TeamResult:
    """병렬 실행 패턴 — 최대 병렬 수 제한 적용"""
    semaphore = asyncio.Semaphore(plan.max_parallel)

    async def run_with_limit(task):
        async with semaphore:
            agent = team.agents[task.agent_id]
            return await agent.execute(task)

    results = await asyncio.gather(*[
        run_with_limit(task) for task in plan.parallel_tasks
    ])
    return merge_results(results)
```

**예시**: 뉴스 수집 ‖ 재무 분석 ‖ 기술 차트 분석 → 종합

## 5.3 Debate (에이전트 간 토론)

A-4 Debate Mode와 연동하여, 서로 상충하는 관점을 가진 에이전트가 토론을 통해 결론을 도출한다.

```
Lead Agent (Moderator)
    │
    ├──→ Bull Agent: "매수 추천" (근거 A, B, C)
    │
    ├──→ Bear Agent: "매도 추천" (근거 D, E, F)
    │
    ├──→ [토론 라운드 1~N]
    │       Bull 반론 → Bear 반론 → ...
    │
    └──→ Lead: 양측 근거 종합 → 최종 결론 확정 (단일결정 원칙)
```

```python
class DebatePattern:
    """에이전트 간 토론 패턴 (A-4 Debate Mode)

    제약 (LOCK):
    - 토론 라운드: 최대 P0=2, P1=3, P2=5 라운드
    - 무한 루프 금지 (D2.0-05 §7.3 고정3)
    - 최종 결론은 Lead Agent만 확정 (단일결정 원칙)
    - V1=OFF, V2=조건부(COND), V3=ON
    """

    async def execute_debate(
        self,
        topic: str,
        proposer: SubAgent,     # 찬성 측
        opponent: SubAgent,     # 반대 측
        max_rounds: int = 3,
    ) -> DebateResult:
        rounds = []

        # 초기 주장
        pro_argument = await proposer.execute(AgentTask(
            instruction=f"다음 주제에 대해 찬성 입장을 논증하세요: {topic}",
        ))
        con_argument = await opponent.execute(AgentTask(
            instruction=f"다음 주제에 대해 반대 입장을 논증하세요: {topic}",
        ))
        rounds.append(DebateRound(round=0, pro=pro_argument, con=con_argument))

        # 토론 라운드
        for i in range(1, max_rounds):
            pro_rebuttal = await proposer.execute(AgentTask(
                instruction=f"반대 측 주장에 반론하세요: {con_argument.output}",
                context={"previous_rounds": rounds},
            ))
            con_rebuttal = await opponent.execute(AgentTask(
                instruction=f"찬성 측 주장에 반론하세요: {pro_rebuttal.output}",
                context={"previous_rounds": rounds},
            ))
            rounds.append(DebateRound(round=i, pro=pro_rebuttal, con=con_rebuttal))

            # 수렴 판정: 양측 주장 차이가 줄어들면 조기 종료
            if self._check_convergence(rounds):
                break

        return DebateResult(topic=topic, rounds=rounds)
```

**활용 시나리오**:
- 투자 분석: Bull vs Bear Analyst
- 코드 리뷰: Developer vs Reviewer
- 전략 평가: Optimist vs Pessimist

## 5.4 Supervisor (감독 패턴)

Lead Agent가 실행 중인 Sub-agent를 실시간으로 감독하며, 필요 시 개입한다.

```
Lead Agent (Supervisor)
    │ [실시간 모니터링]
    │
    ├──→ Agent A: 실행 중... progress 40%
    │       │ ← [Lead: 방향 수정 지시]
    │       └──→ 수정 후 계속 실행
    │
    ├──→ Agent B: 실행 중... progress 80%
    │       │ ← [Lead: OK, 계속]
    │
    └──→ Agent C: 오류 발생!
            │ ← [Lead: 중단 + Agent D로 교체]
            └──→ Agent D: 대체 실행
```

```python
class SupervisorPattern:
    """감독 패턴: Lead가 Sub-agent를 실시간 감독"""

    async def supervised_execution(
        self,
        assignments: List[AgentAssignment],
        check_interval: float = 5.0,  # 초 단위 감시 주기
    ) -> List[AgentResult]:

        # 모든 에이전트 비동기 시작
        running_tasks = {
            a.task_id: asyncio.create_task(self._run_agent(a))
            for a in assignments
        }

        while running_tasks:
            await asyncio.sleep(check_interval)

            for task_id, task in list(running_tasks.items()):
                if task.done():
                    result = task.result()
                    if result.status == "failed":
                        # 실패 시 대체 에이전트로 교체
                        replacement = await self._find_replacement(task_id)
                        if replacement:
                            running_tasks[task_id] = asyncio.create_task(
                                self._run_agent(replacement)
                            )
                    del running_tasks[task_id]
                else:
                    # 진행 상황 확인
                    progress = await self._check_progress(task_id)
                    if progress.needs_intervention:
                        await self._intervene(task_id, progress)
```

## 5.5 Handoff (인계 패턴)

한 에이전트가 작업 완료 후 다음 에이전트에게 컨텍스트와 함께 작업을 인계한다.

```python
class HandoffPacket(BaseModel):
    """에이전트 간 인계 패킷 (S7-A-006)"""

    handoff_id: str = Field(default_factory=lambda: f"hof_{ulid.new()}")
    source_agent_id: str          # 인계 에이전트
    target_agent_id: str          # 인수 에이전트
    task_id: str                  # 작업 ID (trace_id 유지)
    context: Dict[str, Any]       # 공유 컨텍스트
    partial_result: Any           # 부분 결과 (인계 시점까지의 산출물)
    handoff_reason: str           # 인계 사유
    remaining_instructions: str   # 남은 작업 지시사항
    metadata: Dict[str, Any] = {} # 추가 메타데이터

    class Config:
        json_schema_extra = {
            "example": {
                "source_agent_id": "research_001",
                "target_agent_id": "content_001",
                "task_id": "task_analysis_nvda",
                "context": {"company": "NVIDIA", "analysis_type": "comprehensive"},
                "partial_result": {"financial_data": {...}, "news_summary": "..."},
                "handoff_reason": "리서치 완료, 리포트 작성 단계로 인계",
                "remaining_instructions": "수집된 데이터를 바탕으로 투자 리포트 작성",
            }
        }
```

인계 프로토콜:
1. 인계 에이전트가 `handoff_packet`을 생성하여 Lead Agent에게 전송
2. Lead Agent가 인계 대상 에이전트의 가용성/적합성 확인
3. Lead Agent가 인계 승인 → MessageBus를 통해 인수 에이전트에 전달
4. 인수 에이전트가 context를 검증한 후 실행 시작
5. 인계 이벤트 LogEvent 기록 (`agent.handoff.completed`)

---

# 6. VAMOS 기존 시스템 통합

## 6.1 LangGraph 기반 워크플로우 (LOCK)

Agent Teams는 VAMOS 표준 5단계 Pipeline(Intake→Plan→Execute→Verify→Deliver) 위에서 동작하며, LangGraph StateGraph 패턴을 참조한다.

```
┌─────────────────────────────────────────────────────────────┐
│                    VAMOS 5-Stage Pipeline                     │
│                                                               │
│  Intake → Plan → [Gate] → Execute → Verify → Deliver        │
│    │        │       │        │         │        │            │
│    │        │       │    ┌───┴───┐     │        │            │
│    │        │       │    │ Agent │     │        │            │
│    │     Task       │    │ Teams │     │        │            │
│    │     Decomp     │    │ 실행   │   Self-    3단            │
│    │     + Agent    │    │       │   Check    출력            │
│    │     Match      │    └───────┘  + EVX                    │
│    │                │                                         │
│    G0          G1+G2                G3         G4            │
│  입력검증    정책+비용              품질검사   최종승인         │
└─────────────────────────────────────────────────────────────┘
```

**Pipeline 내 Agent Teams 동작 시점**:

| Pipeline 단계 | Agent Teams 동작 | Gate |
|--------------|-----------------|------|
| **Intake** | 사용자 요청 수신, 복잡도 판정 | G0: 입력 검증 |
| **Plan** | Task Decomposition + Agent Matching + DelegationPlan 생성 | G1: 정책, G2: 비용 |
| **Execute** | Lead → Sub-agents 위임 실행 (순차/병렬/토론/감독) | 07 Gate 선행 완료 |
| **Verify** | Lead Agent가 결과 병합 + Self-check + EVX 체인 검증 | G3: 품질 (QoD+EVX) |
| **Deliver** | 3단 출력(user_response + evidence_summary + log_report) | G4: 최종 승인 |

## 6.2 5 Gates와의 연동

```python
class AgentTeamGateIntegration:
    """Agent Teams ↔ 5 Gates 통합"""

    async def run_with_gates(self, plan: DelegationPlan) -> TeamResult:
        # G0: 입력 검증 (Intake에서 이미 통과)

        # G1: 정책 검사 — 전체 팀 실행 계획의 정책 적합성
        g1_result = await self.gate.policy_check(plan)
        if g1_result.status == "deny":
            return TeamResult(status="denied", reason=g1_result.reason)

        # G2: 비용 검사 — 전체 팀 예상 비용
        g2_result = await self.gate.cost_check(plan.estimated_total_cost)
        if g2_result.status == "deny":
            return TeamResult(status="cost_exceeded")
        if g2_result.status == "downshift":
            plan = await self._downshift_plan(plan)  # 저비용 모델로 전환

        # Execute: Agent Teams 실행
        result = await self.lead_agent.execute_plan(plan)

        # G3: 품질 검사 — 병합된 결과의 QoD + EVX 체인
        g3_result = await self.gate.quality_check(result)
        if g3_result.status == "fail":
            # Soft loop 1회 재시도
            result = await self.lead_agent.execute_plan(plan)
            g3_retry = await self.gate.quality_check(result)
            if g3_retry.status == "fail":
                return TeamResult(status="quality_insufficient")

        # G4: 최종 승인 (P1 이상)
        if plan.requires_approval:
            g4_result = await self.gate.final_approval(result)
            if g4_result.status == "deny":
                return TeamResult(status="approval_denied")

        return result
```

## 6.3 9-State Machine과의 매핑

| State | Agent Teams 동작 |
|-------|-----------------|
| **S0_RECEIVED** | 사용자 요청 수신 |
| **S1_INTENT_PARSED** | 의도 분석 + 복잡도 판정 (단일 vs 복합 작업) |
| **S2_EVIDENCE_READY** | Task Decomposition 완료 + Agent Matching + 비용 예측 |
| **S3_DECISION_LOCKED** | DelegationPlan 확정 (어떤 에이전트가 어떤 작업을 수행할지 잠금) |
| **S4_EXECUTING** | Agent Teams 실행 (Lead가 Sub-agents에 위임, 병렬/순차) |
| **S5_OUTPUT_READY** | 모든 Sub-agent 결과 수집 완료, Lead가 결과 병합 |
| **S6_SELF_CHECKED** | Self-check + EVX 체인 검증 완료 |
| **S7_MEMORY_COMMITTED** | 실행 이력 L1/L2 메모리 커밋, 에이전트 결과 아카이빙 |
| **S8_DONE** | 3단 출력 전달, 에이전트 종료 |

## 6.4 I/E/S/A 시리즈 모듈과의 연계

| 모듈 | Agent Teams 연계 |
|------|-----------------|
| **I-1** (Intent) | 복합 작업 의도 인식 → Team 활성화 판단 |
| **I-2** (RAG) | Research Agent의 RAG 파이프라인 호출 |
| **I-3** (Memory) | 에이전트 실행 이력 L2 메모리 커밋 |
| **I-5** (Decision) | Lead Agent의 DelegationPlan = Decision 확장 |
| **I-6** (Self-check) | 팀 결과 품질 검증 |
| **I-8** (Policy Engine) | 에이전트별 정책 검사 + 팀 정책 관리 |
| **I-9** (Cost Manager) | 에이전트별 비용 추적 + 팀 총비용 관리 |
| **I-10** (Tool Registry/Router) | Sub-agent의 MCP 도구 호출 라우팅 |
| **I-11** (Output Composer) | 팀 결과 병합 및 최종 출력 구성 |
| **I-13** (Template) | 에이전트별 프롬프트 템플릿 |
| **I-18** (Meta-learning) | 팀 실행 패턴 학습 → 향후 자동 개선 |
| **I-25** (SDAR) | SDAR Agent 연동, 시스템 자가진단 |
| **E-1~E-n** (External) | MCP 서버를 통한 외부 도구 접근 |
| **S-1** (Logging) | 구조화된 로깅 표준 준수 |
| **S-4** (Error) | 에이전트 오류 처리 + Circuit Breaker |
| **S-8** (Metric) | 에이전트별 성능 메트릭 수집 |
| **A-4** (Debate) | Debate 협업 패턴 연동 |

## 6.5 RBAC 및 보안 제약

### 6.5.1 Agent RBAC 매핑 (LOCK)

```python
class AgentRBACPolicy:
    """에이전트 역할별 접근 제어 (D2.0-07 §3.6 확장)"""

    AGENT_PERMISSIONS = {
        # Lead Agent: AGENT 역할 (PolicyCheck 결과 내 자동 허용 범위)
        AgentType.LEAD: {
            "can_delegate": True,
            "can_approve": False,       # 승인은 OWNER만
            "can_access_p2": False,     # P2는 OWNER 승인 필요
            "max_cost_per_task": None,  # 팀 예산 내에서 자유
            "tool_access": "allowlist", # Allowlist 내 도구만
        },

        # Sub-Agent: 더 제한된 AGENT 역할
        AgentType.RESEARCH: {
            "can_delegate": False,      # 재위임 금지 (Level 1 한정)
            "can_approve": False,
            "can_access_p2": False,
            "max_cost_per_task": "assigned_budget",
            "tool_access": "assigned_tools_only",
            "file_access": "readonly",  # 파일 읽기 전용
        },

        AgentType.CODING: {
            "can_delegate": True,       # Level 2까지 가능 (Test Runner)
            "can_approve": False,
            "can_access_p2": False,
            "max_cost_per_task": "assigned_budget",
            "tool_access": "assigned_tools_only",
            "file_access": "file_ownership",  # FileOwnership 범위 내
        },

        AgentType.TRADING_ANALYSIS: {
            "can_delegate": False,
            "can_approve": False,
            "can_access_p2": True,      # P2 접근 가능 (단, OWNER 승인 필수)
            "max_cost_per_task": "assigned_budget",
            "tool_access": "assigned_tools_only",
            "file_access": "readonly",
            "requires_explicit_approval": True,
        },
    }
```

### 6.5.2 Delegation Attack 방어 (S7E-080, LOCK)

```python
class DelegationSecurityGuard:
    """위임 공격 방어 시스템"""

    # 규칙 1: 위임 체인 깊이 제한
    MAX_CHAIN_DEPTH = 3

    # 규칙 2: 권한 상승 감지
    async def check_privilege_escalation(
        self, source: SubAgent, target_action: str
    ) -> bool:
        """위임 시 권한 상승 시도를 감지한다."""
        source_permissions = self.rbac.get_permissions(source.agent_id)
        if target_action not in source_permissions.allowed_actions:
            await log_event("agent.security.privilege_escalation_blocked", {
                "source_agent": source.agent_id,
                "attempted_action": target_action,
            })
            return False
        return True

    # 규칙 3: 원래 요청자 권한으로 실행
    async def enforce_original_requester_permission(
        self, delegation_chain: List[str], action: str
    ) -> bool:
        """위임 체인의 최초 요청자(OWNER) 권한으로 실행한다.
        중간 에이전트의 권한이 아닌, 원래 사용자의 권한을 적용한다."""
        original_requester = delegation_chain[0]  # 항상 OWNER
        return self.rbac.check_permission(original_requester, action)

    # 규칙 4: 모든 위임 감사
    async def audit_delegation(self, message: DelegationMessage) -> None:
        """ORANGE CORE가 모든 위임 요청을 감사 로그에 기록한다."""
        await log_event("agent.delegation.audited", {
            "delegation_id": message.message_id,
            "chain_depth": message.chain_depth,
            "source": message.sender_id,
            "target": message.receiver_id,
            "action": message.payload.get("instruction", ""),
        })
```

## 6.6 비용 관리 (에이전트별 비용 추적)

### 6.6.1 비용 할당 전략

```python
class TeamCostManager:
    """Agent Team 비용 관리자"""

    def __init__(self, team_budget: CostBudget):
        self.team_budget = team_budget
        self.agent_budgets: Dict[str, CostBudget] = {}
        self.spent: Dict[str, float] = {}

    def allocate_budgets(self, plan: DelegationPlan) -> Dict[str, CostBudget]:
        """팀 예산을 에이전트별로 할당한다.

        할당 규칙:
        - Lead Agent: 팀 예산의 20% (계획/검증용)
        - Sub-agents: 팀 예산의 80%를 작업 복잡도 비례 배분
        - 예비비: 전체의 10%를 Soft loop/재시도용으로 예약
        """
        total = self.team_budget.amount
        reserve = total * 0.10    # 10% 예비비
        lead_budget = total * 0.18 # 18% Lead (20% - 2% reserve)
        sub_budget = total * 0.72  # 72% Sub-agents

        # 작업 복잡도 기반 비례 배분
        total_complexity = sum(t.complexity_score for t in plan.tasks)
        for task in plan.tasks:
            agent_share = (task.complexity_score / total_complexity) * sub_budget
            self.agent_budgets[task.agent_id] = CostBudget(
                amount=agent_share,
                currency="KRW",
            )

        return self.agent_budgets

    async def check_and_warn(self, agent_id: str, spent: float) -> CostCheckResult:
        """에이전트별 비용 확인 + 경고"""
        budget = self.agent_budgets[agent_id]
        ratio = spent / budget.amount

        if ratio >= 1.0:
            await log_event(AgentEvent.COST_EXCEEDED, {"agent_id": agent_id})
            return CostCheckResult(status="exceeded", action="terminate")
        elif ratio >= 0.8:
            await log_event(AgentEvent.COST_WARNING, {"agent_id": agent_id})
            return CostCheckResult(status="warning", action="downshift")

        return CostCheckResult(status="ok")
```

### 6.6.2 에이전트별 모델 비용 차등

| 에이전트 | 기본 모델 | 토큰 단가 (입/출) | 비용 비율 |
|---------|----------|-----------------|----------|
| Lead Agent | Opus | 입력 $15/1M, 출력 $75/1M | 기준 (100%) |
| Research Agent | Sonnet | 입력 $3/1M, 출력 $15/1M | 20% |
| Coding Agent | Sonnet | 입력 $3/1M, 출력 $15/1M | 20% |
| Quant Agent | Sonnet | 입력 $3/1M, 출력 $15/1M | 20% |
| Content Agent | Haiku | 입력 $0.25/1M, 출력 $1.25/1M | 1.7% |
| SDAR Agent | Haiku | 입력 $0.25/1M, 출력 $1.25/1M | 1.7% |
| Critic Agent | Sonnet | 입력 $3/1M, 출력 $15/1M | 20% |

> S7-A-013: 리드 에이전트는 Opus급, 팀원 에이전트는 Sonnet/Haiku급 모델 사용으로 비용 절감

---

# 7. Pydantic v2 스키마

## 7.1 핵심 스키마 정의

```python
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import ulid


# ─── Enums ───

class AgentType(str, Enum):
    LEAD = "lead"
    RESEARCH = "research"
    CODING = "coding"
    QUANT = "quant"
    CONTENT = "content"
    TRADING_ANALYSIS = "trading_analysis"
    SDAR = "sdar"
    CRITIC = "critic"
    PRODUCTIVITY = "productivity"

class AgentState(str, Enum):
    CREATED = "created"
    INITIALIZED = "initialized"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ARCHIVED = "archived"

class ModelTier(str, Enum):
    OPUS = "opus"           # 최고 품질 (Lead, Trading)
    SONNET = "sonnet"       # 균형 (Research, Coding, Quant, Critic)
    HAIKU = "haiku"         # 경량 (Content, SDAR, Productivity)

class TaskStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class DelegationStatus(str, Enum):
    PLANNED = "planned"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    FAILED = "failed"

class CollaborationPattern(str, Enum):
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    DEBATE = "debate"
    SUPERVISOR = "supervisor"
    HANDOFF = "handoff"
    HYBRID = "hybrid"


# ─── Core Schemas ───

class AgentTeamConfig(BaseModel):
    """Agent Team 전체 설정"""

    team_id: str = Field(default_factory=lambda: f"team_{ulid.new()}")
    name: str = Field(..., description="팀 이름")
    description: str = Field("", description="팀 설명")
    version: str = Field("v1", description="V1|V2|V3")

    # 에이전트 구성
    lead_model_tier: ModelTier = Field(ModelTier.OPUS, description="Lead Agent 모델 등급")
    default_sub_model_tier: ModelTier = Field(ModelTier.SONNET, description="Sub-agent 기본 모델 등급")
    max_agents: int = Field(3, description="최대 에이전트 수 (V1=3, V2=10, V3=50)")

    # 비용 제약
    budget: CostBudget = Field(..., description="팀 총 예산")
    lead_budget_ratio: float = Field(0.2, description="Lead Agent 예산 비율")

    # 위임 제약
    max_delegation_depth: int = Field(3, description="최대 위임 깊이")
    max_parallel_agents: int = Field(3, description="최대 병렬 에이전트")
    delegation_timeout: int = Field(120, description="위임 타임아웃 (초)")

    # 협업 패턴
    default_pattern: CollaborationPattern = Field(
        CollaborationPattern.PARALLEL,
        description="기본 협업 패턴"
    )
    debate_enabled: bool = Field(False, description="V2+에서 Debate Mode 활성화")
    max_debate_rounds: int = Field(3, description="최대 토론 라운드")

    # TEE 루프 제한
    max_tee_iterations: int = Field(5, description="TEE 루프 최대 반복")
    max_conversation_turns: int = Field(10, description="대화 턴 상한")


class CostBudget(BaseModel):
    """비용 예산"""
    amount: float = Field(..., description="예산 금액 (KRW)")
    currency: str = Field("KRW", description="통화")
    daily_limit: Optional[float] = Field(None, description="일일 한도")
    per_task_limit: Optional[float] = Field(None, description="작업별 한도")


class AgentTask(BaseModel):
    """에이전트에 할당되는 작업 단위"""

    task_id: str = Field(default_factory=lambda: f"task_{ulid.new()}")
    trace_id: str = Field(..., description="워크플로우 trace_id")
    team_id: str = Field(..., description="팀 ID")

    name: str = Field(..., description="작업 이름")
    instruction: str = Field(..., description="상세 지시사항")

    # 실행 요구사항
    required_skills: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    domain: str = Field("general", description="도메인 (dev|research|quant|content|trading)")
    priority_class: str = Field("P0", description="P0|P1|P2")

    # 의존성
    dependencies: List[str] = Field(default_factory=list, description="선행 task_id 목록")

    # 제약
    budget_limit: float = Field(1000.0, description="작업별 비용 한도 (KRW)")
    timeout: int = Field(120, description="타임아웃 (초)")

    # 컨텍스트
    context: Dict[str, Any] = Field(default_factory=dict, description="공유 컨텍스트")

    # 메타
    status: TaskStatus = Field(TaskStatus.PENDING)
    assigned_agent_id: Optional[str] = None
    complexity_score: float = Field(1.0, description="복잡도 점수 (비용 배분용)")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentResult(BaseModel):
    """에이전트 실행 결과"""

    result_id: str = Field(default_factory=lambda: f"res_{ulid.new()}")
    task_id: str
    agent_id: str
    team_id: str
    trace_id: str

    status: str = Field(..., description="completed|failed|timeout|cancelled")
    output: Any = Field(None, description="실행 결과물")
    evidence: Optional[Dict] = Field(None, description="근거/출처")
    error: Optional[str] = Field(None, description="에러 메시지 (실패 시)")

    # 비용
    tokens_used: Dict[str, int] = Field(
        default_factory=dict,
        description="토큰 사용량 {'input': N, 'output': M}"
    )
    cost: float = Field(0.0, description="실제 비용 (KRW)")
    model_used: str = Field("", description="사용된 모델")

    # 품질
    qod_score: Optional[float] = Field(None, description="Quality of Decision 점수")
    self_check_passed: Optional[bool] = None

    # 시간
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[float] = None


class DelegationPlan(BaseModel):
    """위임 계획 (Lead Agent가 생성)"""

    plan_id: str = Field(default_factory=lambda: f"plan_{ulid.new()}")
    team_id: str
    trace_id: str

    # 작업 목록
    tasks: List[AgentTask]

    # 에이전트 할당
    assignments: List[AgentAssignment]

    # 실행 전략
    pattern: CollaborationPattern
    execution_batches: List[List[str]] = Field(
        default_factory=list,
        description="병렬 실행 배치 [[task_id, ...], [task_id, ...], ...]"
    )

    # 비용 예측
    estimated_total_cost: float
    agent_budgets: Dict[str, float] = Field(default_factory=dict)

    # 제약
    max_parallel: int = 3
    max_delegation_depth: int = 3
    requires_approval: bool = False  # P2 작업 포함 여부

    # 메타
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: DelegationStatus = DelegationStatus.PLANNED


class AgentAssignment(BaseModel):
    """에이전트-작업 할당"""

    task_id: str
    agent_id: str
    agent_type: AgentType
    model_tier: ModelTier
    match_score: float = Field(..., ge=0.0, le=1.0)
    allocated_budget: float
    timeout: int = 120
    context: Dict[str, Any] = Field(default_factory=dict)
    constraints: Dict[str, Any] = Field(default_factory=dict)


class TeamResult(BaseModel):
    """Agent Team 전체 실행 결과"""

    team_id: str
    trace_id: str
    plan_id: str

    status: str  # completed | failed | partial | denied | cost_exceeded

    # 결과
    merged_result: Any = None
    agent_results: Dict[str, AgentResult] = Field(default_factory=dict)

    # 3단 출력 (D2.0-05 §7.2)
    user_response: str = ""
    evidence_summary: str = ""
    log_report: Dict[str, Any] = Field(default_factory=dict)

    # 비용
    total_cost: float = 0.0
    cost_breakdown: Dict[str, float] = Field(default_factory=dict)

    # 품질
    overall_qod: Optional[float] = None
    verification_chain: List[str] = Field(default_factory=list)

    # 시간
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    total_duration_seconds: Optional[float] = None


class MatchScore(BaseModel):
    """에이전트 매칭 점수"""
    skill: float = Field(ge=0.0, le=1.0)
    tool: float = Field(ge=0.0, le=1.0)
    cost: float = Field(ge=0.0, le=1.0)
    load: float = Field(ge=0.0, le=1.0)
    history: float = Field(ge=0.0, le=1.0)
    total: float = Field(ge=0.0, le=1.0)


class AgentPermissionPolicy(BaseModel):
    """에이전트 권한 정책 (S7-A-011)"""

    agent_id: str
    agent_type: AgentType

    # 도구 접근 권한
    allowed_tools: List[str] = Field(default_factory=list)
    denied_tools: List[str] = Field(default_factory=list)

    # 파일 접근 권한
    writable_paths: List[str] = Field(default_factory=list)
    readonly_paths: List[str] = Field(default_factory=list)
    forbidden_paths: List[str] = Field(default_factory=list)

    # 비용 한도
    max_cost_per_task: Optional[float] = None
    max_cost_per_session: Optional[float] = None

    # 위임 권한
    can_delegate: bool = False
    max_delegation_depth: int = 1

    # 도메인 접근
    allowed_domains: List[str] = Field(default_factory=list)
    priority_access: str = Field("P0", description="최대 접근 가능 P등급")
```

---

# 8. API 엔드포인트

## 8.1 Tauri IPC 커맨드

VAMOS는 Tauri 기반 데스크톱 앱이므로, Agent Teams API는 Tauri IPC 커맨드로 노출된다.

```rust
// Tauri IPC Commands (Rust)

#[tauri::command]
async fn create_agent_team(config: AgentTeamConfig) -> Result<TeamCreatedResponse, VamosError> {
    // 1. 팀 생성
    // 2. 에이전트 스폰
    // 3. Gate 등록
    Ok(TeamCreatedResponse { team_id, agents })
}

#[tauri::command]
async fn submit_team_task(
    team_id: String,
    request: UserRequest,
) -> Result<TeamResult, VamosError> {
    // 1. Plan: Task Decomposition + Agent Matching
    // 2. Execute: Delegation
    // 3. Verify: Quality Check
    // 4. Deliver: 3단 출력
    Ok(result)
}

#[tauri::command]
async fn get_team_status(team_id: String) -> Result<TeamStatus, VamosError> {
    // 팀 상태 조회 (에이전트별 진행 상황 포함)
    Ok(status)
}

#[tauri::command]
async fn cancel_team_task(
    team_id: String,
    task_id: String,
) -> Result<CancelResult, VamosError> {
    // 실행 중인 작업 취소
    Ok(cancel_result)
}

#[tauri::command]
async fn get_agent_cost_report(team_id: String) -> Result<CostReport, VamosError> {
    // 에이전트별 비용 리포트
    Ok(cost_report)
}
```

### Tauri IPC 커맨드 전체 목록

| 커맨드 | 파라미터 | 반환 | 설명 |
|--------|---------|------|------|
| `create_agent_team` | `AgentTeamConfig` | `TeamCreatedResponse` | 팀 생성 + 에이전트 스폰 |
| `submit_team_task` | `team_id, UserRequest` | `TeamResult` | 팀에 작업 제출 → 실행 → 결과 |
| `get_team_status` | `team_id` | `TeamStatus` | 팀/에이전트 실시간 상태 |
| `cancel_team_task` | `team_id, task_id` | `CancelResult` | 작업 취소 |
| `get_agent_cost_report` | `team_id` | `CostReport` | 에이전트별 비용 리포트 |
| `list_active_teams` | - | `List[TeamSummary]` | 활성 팀 목록 |
| `terminate_team` | `team_id` | `TerminateResult` | 팀 종료 + 리소스 해제 |
| `get_delegation_log` | `team_id` | `List[DelegationEvent]` | 위임 감사 로그 |
| `update_team_config` | `team_id, partial_config` | `TeamConfig` | 팀 설정 변경 (Gate 승인 필요) |
| `approve_agent_action` | `approval_id, decision` | `ApprovalResult` | 에이전트 행동 승인/거부 |

## 8.2 JSON-RPC 메서드

외부 도구/MCP 클라이언트에서 Agent Teams를 호출하기 위한 JSON-RPC 인터페이스.

```json
// JSON-RPC 2.0 Method: agent_teams.create
{
    "jsonrpc": "2.0",
    "method": "agent_teams.create",
    "params": {
        "name": "Investment Analysis Team",
        "max_agents": 5,
        "budget": {"amount": 5000, "currency": "KRW"},
        "pattern": "parallel"
    },
    "id": 1
}

// Response
{
    "jsonrpc": "2.0",
    "result": {
        "team_id": "team_01HZ001ABC",
        "status": "created",
        "agents": [
            {"agent_id": "lead_001", "type": "lead", "model": "opus"},
            {"agent_id": "research_001", "type": "research", "model": "sonnet"},
            {"agent_id": "quant_001", "type": "quant", "model": "sonnet"}
        ]
    },
    "id": 1
}
```

### JSON-RPC 메서드 전체 목록

| 메서드 | 설명 |
|--------|------|
| `agent_teams.create` | 팀 생성 |
| `agent_teams.submit_task` | 작업 제출 |
| `agent_teams.get_status` | 상태 조회 |
| `agent_teams.cancel` | 작업 취소 |
| `agent_teams.terminate` | 팀 종료 |
| `agent_teams.list` | 활성 팀 목록 |
| `agent_teams.get_cost` | 비용 리포트 |
| `agent_teams.get_delegation_log` | 위임 로그 |
| `agent_teams.approve` | 승인/거부 |
| `agent_teams.update_config` | 설정 변경 |
| `agent_teams.spawn_agent` | 에이전트 추가 스폰 (V2+) |
| `agent_teams.remove_agent` | 에이전트 제거 (V2+) |

---

# 9. V1/V2/V3 로드맵

## 9.1 V1: 기본 Lead+Sub 구조 (2~3 에이전트)

| 항목 | V1 범위 |
|------|---------|
| **에이전트 수** | Lead + 최대 2 Sub-agents (총 3) |
| **협업 패턴** | Sequential, Parallel만 |
| **위임 깊이** | 최대 2단계 (Lead → Sub) — config 제한. LOCK-AT-004 절대상한=3단계 |
| **병렬 수** | 최대 3 |
| **모델** | Lead=Sonnet(비용 절감), Sub=Haiku |
| **오케스트레이션** | Centralized (CORE 단독 제어) |
| **Debate Mode** | OFF |
| **Agent SDK** | 내부 @vamos.agent 베이스만 |
| **비용 상한** | 일일 1,300원 / 월 40,000원 |
| **구현 우선순위** | S7-A-001(역할 분리), S7-A-008(Coordination 패턴) |

```python
# V1 팀 구성 예시
v1_team = AgentTeamConfig(
    name="V1 Basic Team",
    version="v1",
    lead_model_tier=ModelTier.SONNET,
    default_sub_model_tier=ModelTier.HAIKU,
    max_agents=3,
    max_parallel_agents=3,
    max_delegation_depth=2,
    budget=CostBudget(amount=1300, currency="KRW", daily_limit=1300),
    debate_enabled=False,
    default_pattern=CollaborationPattern.PARALLEL,
)
```

## 9.2 V2: 병렬 실행, Debate Mode, 5+ 에이전트

| 항목 | V2 범위 |
|------|---------|
| **에이전트 수** | Lead + 최대 9 Sub-agents (총 10) |
| **협업 패턴** | Sequential, Parallel, Debate, Supervisor, Handoff |
| **위임 깊이** | 최대 3단계 (Lead → Sub → Sub-sub) |
| **병렬 수** | 최대 10 |
| **모델** | Lead=Opus, Sub=Sonnet/Haiku 차등 |
| **오케스트레이션** | Centralized + Hierarchical |
| **Debate Mode** | 조건부 ON (COND) |
| **Agent SDK** | @vamos.agent, @vamos.tool, @vamos.gate 데코레이터 |
| **MessageBus** | Redis 기반 메시지 큐 |
| **GroupChat** | 공유 컨텍스트 채팅 (발화 순서 CORE 조율) |
| **Crew** | 역할 기반 팀 (Researcher/Coder/Critic) |
| **비용 상한** | 일일 3,100원 / 월 93,000원 |
| **에이전트 상태 UI** | 병렬 에이전트 상태 패널 (S7C-065) |

```python
# V2 투자 분석 팀 예시
v2_investment_team = AgentTeamConfig(
    name="V2 Investment Analysis Team",
    version="v2",
    lead_model_tier=ModelTier.OPUS,
    default_sub_model_tier=ModelTier.SONNET,
    max_agents=10,
    max_parallel_agents=10,
    max_delegation_depth=3,
    budget=CostBudget(amount=3100, currency="KRW", daily_limit=3100),
    debate_enabled=True,
    max_debate_rounds=3,
    default_pattern=CollaborationPattern.HYBRID,
)
```

## 9.3 V3: 자율 에이전트 팀, 동적 생성/해체

| 항목 | V3 범위 |
|------|---------|
| **에이전트 수** | 최대 50+ (동적 생성/해체) |
| **협업 패턴** | 전체 패턴 + Multi-Agent Mesh + Federated |
| **위임 깊이** | 3단계 (안전 유지) |
| **병렬 수** | 최대 50+ (LOCK-AT-014 기준) |
| **모델** | 에이전트별 자동 최적 모델 선택 |
| **오케스트레이션** | Centralized + Hierarchical + Market-based + Stigmergic |
| **Debate Mode** | 항상 ON |
| **Agent Mesh** | P2P 에이전트 네트워크 (ADD-080) |
| **Federated Agent** | 외부 에이전트 연합 (ADD-084) |
| **A2A Protocol** | Google A2A + MCP 양방향 |
| **자율 루프** | Plan→Execute→Verify 자율 수행 (HITL 유지) |
| **동적 팀 구성** | 작업에 따라 에이전트 자동 스폰/해체 |
| **비용 상한** | 일일 8,900원 / 월 266,000원 |

```
V3 Multi-Agent Mesh 다이어그램:

    ┌───────┐     ┌───────┐     ┌───────┐
    │Agent A│◄───►│Agent B│◄───►│Agent C│
    └───┬───┘     └───┬───┘     └───┬───┘
        │             │             │
        └─────────────┼─────────────┘
                      │
              ┌───────▼───────┐
              │  ORANGE CORE  │  (여전히 최종 결정권)
              │  (Supervisor) │
              └───────────────┘
```

---

# 10. LOCK 결정사항

## 10.1 확정된 결정 (변경 불가)

| LOCK ID | 결정 내용 | 근거 |
|---------|----------|------|
| **LOCK-AT-001** | VAMOS V1은 자체 경량 프레임워크를 기본으로 한다. 외부 엔진은 어댑터로만 연결 | D2.0-05 §5.1 |
| **LOCK-AT-002** | 단일결정 원칙: 최종 결론은 ORANGE CORE(Lead Agent)만 확정 | D2.0-02 §2.2 S3 |
| **LOCK-AT-003** | 에이전트 간 자유 상호 호출/무한 대화 루프 금지 | D2.0-03 §1.4, D2.0-05 §7.3 고정3 |
| **LOCK-AT-004** | 위임 체인 최대 깊이 3단계 | S7E-080 |
| **LOCK-AT-005** | 모든 에이전트 실행은 07 Gate 선행 통과 필수 | D2.0-05 §7.3 고정1 |
| **LOCK-AT-006** | Execute 단계에서만 도구 호출 수행 | D2.0-05 §7.3 고정2 |
| **LOCK-AT-007** | Checkpoint/Replay/Fork는 trace_id 단위로만 허용 | D2.0-05 §7.3 고정2 |
| **LOCK-AT-008** | P2 에이전트(Trading)는 기본 OFF, 세션별 승인, 세션 종료 시 자동 OFF | RULE 1.3 §3.3 |
| **LOCK-AT-009** | 대화 턴 상한: P0=5턴, P1=10턴, P2=20턴 | D2.0-05 §12.4.4 |
| **LOCK-AT-010** | TEE 최대 반복: P0=3회, P1=5회, P2=10회 | D2.0-05 §12.5.1 |
| **LOCK-AT-011** | 비용 상한 초과 호출은 승인 없이 자동 차단 | RULE 1.3 §5 |
| **LOCK-AT-012** | Agent 메시지에 HMAC 무결성 서명 필수 | S7E-078 |
| **LOCK-AT-013** | 위임 시 원래 요청자(OWNER) 권한으로 실행 (권한 상승 방지) | S7E-080 |
| **LOCK-AT-014** | V1 병렬 상한=3, V2=10, V3=50+ | S7-A-008 |
| **LOCK-AT-015** | Lead Agent는 직접 실행 금지 (계획/분배/검증만 수행) | S7-A-001 |
| **LOCK-AT-016** | LangChain import 금지 (패턴 개념만 참조) | DEC-002 |
| **LOCK-AT-017** | 노코드 빌더는 n8n + Flowise 듀얼 구조 | D2.0-05 §12.10.2 |

## 10.2 결정 필요 (V1.1 또는 V2에서 확정)

| DEFER ID | 항목 | 결정 시점 |
|----------|------|----------|
| DEFER-AT-001 | MessageBus 구현 (In-Memory vs Redis) | V1.1 |
| DEFER-AT-002 | GroupChat 발화 순서 알고리즘 | V2 |
| DEFER-AT-003 | Agent Marketplace 등록/공유 기준 | V2 |
| DEFER-AT-004 | Federated Agent 연합 승인 정책 | V3 |
| DEFER-AT-005 | A2A 프로토콜 구현 범위 | V3 |

---

# 11. 안전/비용 제약

## 11.1 안전 제약 종합

### 11.1.1 Delegation Attack 방어 (S7E-080, LOCK)

| 방어 메커니즘 | 설명 |
|-------------|------|
| **체인 깊이 제한** | 최대 3단계. 초과 시 즉시 차단 + `DELEGATION_DEPTH_EXCEEDED` failure_code |
| **권한 상승 감지** | 하위 에이전트가 상위 권한 작업 시도 시 차단 + `PRIVILEGE_ESCALATION_BLOCKED` |
| **원본 권한 실행** | 위임 체인 전체에서 최초 요청자(OWNER) 권한만 적용 |
| **전수 감사** | ORANGE CORE가 모든 위임 요청을 감사 로그에 기록 |
| **순환 참조 감지** | Agent A → B → A 순환 위임 자동 감지/차단 |

### 11.1.2 Prompt Injection 방어

| 방어 계층 | 적용 위치 |
|----------|----------|
| **L1 NeMo Guardrails** | Intake 단계 — 입력 필터링 |
| **L2 Guardrails AI** | Plan 단계 — 정책 검사 |
| **L3 LlamaGuard** | Execute 단계 — 출력 안전성 |
| **L4 Post-delivery Audit** | Deliver 이후 — 사후 감사 |
| **Instruction Hierarchy** | 시스템 프롬프트 > 사용자 프롬프트 > 도구 결과 |
| **Canary Token** | 도구 결과에 삽입된 악성 프롬프트 감지 |

### 11.1.3 에이전트 격리

```python
class AgentIsolationPolicy:
    """에이전트 실행 격리 정책"""

    # 컨텍스트 격리
    CONTEXT_ISOLATION = True  # 각 에이전트 독립 컨텍스트
    SHARED_VIA_CONTEXT_VARS_ONLY = True  # 공유는 Context Variables만

    # 파일 시스템 격리
    FILE_OWNERSHIP_ENFORCED = True  # FileOwnership 범위 강제

    # 도구 격리
    TOOL_ACCESS_BY_ALLOWLIST = True  # Allowlist 기반 도구 접근

    # 네트워크 격리
    NETWORK_ACCESS_VIA_MCP_ONLY = True  # MCP 서버를 통해서만 네트워크 접근

    # 코드 실행 격리
    CODE_EXECUTION_SANDBOXED = True  # Docker 기반 샌드박스
```

## 11.2 비용 제약 종합

### 11.2.1 버전별 Agent Teams 비용 한도

| 버전 | 일일 한도 | 월 한도 | 팀당 기본 예산 | Lead 모델 | Sub 모델 |
|------|-----------|---------|--------------|----------|---------|
| **V1** | ₩1,300 ($1) | ₩40,000 ($30) | ₩500/작업 | Sonnet | Haiku |
| **V2** | ₩3,100 ($2.3) | ₩93,000 ($70) | ₩2,000/작업 | Opus | Sonnet |
| **V3** | ₩8,900 ($6.7) | ₩266,000 ($200) | ₩5,000/작업 | Opus | Sonnet/Haiku 자동 |

### 11.2.2 비용 제어 메커니즘

```python
class TeamCostGuard:
    """Agent Team 비용 제어"""

    async def enforce_cost_limits(self, team: AgentTeam) -> None:
        """비용 제한을 강제한다."""

        # 1. 작업 시작 전: 예상 비용 확인
        estimated = await self.estimate_team_cost(team.current_plan)
        if estimated > team.budget.amount:
            raise CostExceededError("예상 비용이 예산을 초과합니다")

        # 2. 실행 중: 실시간 비용 모니터링
        # - 각 에이전트의 토큰 사용량 추적 (tiktoken)
        # - 에이전트별 예산 80% 도달 시 경고
        # - 에이전트별 예산 100% 도달 시 해당 에이전트 중단

        # 3. 팀 전체 비용 80% 경고
        if team.total_spent >= team.budget.amount * 0.8:
            await self.send_cost_warning(team)

        # 4. 팀 전체 비용 100% 도달 시 팀 전체 중단
        if team.total_spent >= team.budget.amount:
            await self.terminate_team(team, reason="budget_exceeded")

        # 5. 비용 다운시프트: G2 downshift 시 저비용 모델로 자동 전환
        # Opus → Sonnet, Sonnet → Haiku
```

### 11.2.3 비용 리포트 스키마

```python
class TeamCostReport(BaseModel):
    """팀 비용 리포트"""

    team_id: str
    report_period: str  # "2026-02-23 14:00~15:30"

    # 총계
    total_budget: float
    total_spent: float
    remaining: float
    utilization_ratio: float  # spent / budget

    # 에이전트별 상세
    agent_costs: List[AgentCostEntry] = []

    # 모델별 상세
    model_costs: Dict[str, float] = {}  # {"opus": 500, "sonnet": 200, "haiku": 50}

    # 토큰 상세
    total_input_tokens: int = 0
    total_output_tokens: int = 0

class AgentCostEntry(BaseModel):
    agent_id: str
    agent_type: AgentType
    model_used: str
    budget_allocated: float
    spent: float
    input_tokens: int
    output_tokens: int
    tasks_completed: int
    tasks_failed: int
```

---

# 부록 A: 참조 문서 매핑

| 본 문서 섹션 | 참조 원본 문서 | 섹션 |
|-------------|-------------|------|
| §1 시스템 개요 | D2.0-02 ORANGE CORE | §12 S7-A-001 |
| §2.1 Lead Agent | D2.0-02 ORANGE CORE | §3 Analysis Stage, §5 Execution |
| §2.2 Sub-Agent | D2.0-03 BLUE NODES | §1 정의, §2 계층구조 |
| §2.3 통신 프로토콜 | STEP7 작업가이드 | A-1 §S7-A-002 |
| §2.4 Lifecycle | D2.0-05 AGENT WORKFLOW | §12.8.2 |
| §3 위임 시스템 | STEP7 작업가이드 | A-1 §S7-A-005 |
| §4 Agent 유형 | D2.0-03 BLUE NODES | §6 NODE 레지스트리 |
| §5 협업 패턴 | D2.0-05 AGENT WORKFLOW | §5, §12.4~12.12 |
| §6.1 Pipeline | D2.0-05 AGENT WORKFLOW | §7.1 5단계 Pipeline |
| §6.2 Gates | D2.0-07 SAFETY/COST | §3~5, VAMOS_MASTER §7.5 |
| §6.3 State Machine | D2.0-02 ORANGE CORE | §2.2 |
| §6.5 RBAC | D2.0-07 SAFETY/COST | §3.6 |
| §6.6 비용 | D2.0-07 SAFETY/COST | §4 |
| §7 스키마 | D2.1-D5 SCHEMA | §4 |
| §10 LOCK | RULE 1.3 BASE | 전체 |
| §11 안전 | D2.0-07 SAFETY/COST | §1~3, S7E-077~084 |

---

# 부록 B: 용어 사전

| 용어 | 영문 | 정의 |
|------|------|------|
| 리드 에이전트 | Lead Agent | ORANGE CORE 기반 오케스트레이터. 계획/분배/검증만 수행 |
| 서브 에이전트 | Sub-Agent | BLUE NODE 기반 실행 에이전트. 도메인 전문 작업 수행 |
| 위임 | Delegation | Lead가 Sub에게 작업을 인계하는 행위 |
| 위임 계획 | DelegationPlan | 작업 분해 + 에이전트 할당 결과 |
| 작업 분해 | Task Decomposition | 복합 작업을 실행 가능한 하위 작업으로 나누는 과정 |
| 메시지 버스 | MessageBus | 에이전트 간 제어된 통신 채널 |
| 작업 보드 | TaskBoard | 에이전트 간 가시적 태스크 공유 보드 |
| 인계 | Handoff | 에이전트 간 컨텍스트와 함께 작업을 넘기는 것 |
| 게이트 | Gate | 정책/비용/승인/품질 검증 관문 (G0~G4) |
| TEE 루프 | TEE Loop | Think-Execute-Evaluate 반복 실행 패턴 |
| QoD | Quality of Decision | 결정 품질 점수 (0.0~1.0) |
| EVX 체인 | EVX Chain | 검증 체인 (EVX-1~EVX-6) |
| 단일결정 원칙 | Single Decision Principle | 최종 결론은 ORANGE CORE만 확정 |
| Circuit Breaker | Circuit Breaker | 연속 실패 시 자동 차단 패턴 |

---

> **문서 이력**
>
> | 버전 | 날짜 | 변경 내용 |
> |------|------|----------|
> | v1.0.0 | 2026-02-23 | 초기 작성. S7-A-001 TITLE_ONLY → 95~100% 상세 확장 |

---

<\!-- END OF DOCUMENT -->
