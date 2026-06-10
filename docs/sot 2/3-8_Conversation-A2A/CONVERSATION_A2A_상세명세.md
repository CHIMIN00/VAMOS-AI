# 3-8. Conversation / A2A (Agent-to-Agent) 상세명세

| 항목 | 내용 |
|------|------|
| **도메인 ID** | `TIER3-DOMAIN-08` |
| **SOT 근거** | STEP7-B, D2.0-05 |
| **Part2 현황** | PARTIAL — A2A 파일 구조만 존재, 대화 프로세스 1줄 기술 |
| **최종 갱신** | 2026-03-22 |
| **상태** | DRAFT v1.0 |

---

## 1. 개요 및 범위

VAMOS의 A2A(Agent-to-Agent) 통신 계층은 Google A2A 프로토콜(2025.04)을 기반으로,
에이전트 간 작업 위임, 상태 공유, 협업 오케스트레이션을 담당한다.
본 명세는 메시지 포맷, 디스커버리, 보안, 고급 대화 기능, 모니터링을 포괄한다.

### 1.1 서브도메인 구성

| # | 서브도메인 | 핵심 내용 | 우선순위 |
|---|-----------|----------|---------|
| A | A2A 메시지 포맷 | JSON-RPC 2.0 스키마, Task Lifecycle | P0 |
| B | 에이전트 디스커버리 | mDNS/DNS-SD, 서비스 등록 | P0 |
| C | A2A 보안 | mTLS + JWT, 권한 위임 | P0 |
| D | 대화 프로세스 고급 기능 | V2 8건, MoA 패턴 | P1 |
| E | A2A 모니터링/테스트 | 대시보드, 테스트 프레임워크 | P1 |

---

## 2. A2A 메시지 포맷 (서브도메인 A)

### 2.1 JSON-RPC 2.0 기반 메시지 상세 스키마

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "A2A-Message",
  "description": "VAMOS A2A JSON-RPC 2.0 메시지 포맷",
  "type": "object",
  "required": ["jsonrpc", "method", "id"],
  "properties": {
    "jsonrpc": { "const": "2.0" },
    "id": {
      "oneOf": [
        { "type": "string", "format": "uuid" },
        { "type": "integer" }
      ]
    },
    "method": {
      "type": "string",
      "enum": [
        "tasks/send",
        "tasks/sendSubscribe",
        "tasks/get",
        "tasks/cancel",
        "tasks/pushNotification/set",
        "tasks/pushNotification/get",
        "tasks/resubscribe",
        "agent/authenticatedExtendedCard"
      ]
    },
    "params": {
      "type": "object",
      "properties": {
        "id": { "type": "string", "description": "Task ID" },
        "sessionId": { "type": "string", "description": "세션 ID" },
        "message": { "$ref": "#/$defs/Message" },
        "metadata": { "type": "object" },
        "pushNotificationConfig": { "$ref": "#/$defs/PushNotificationConfig" }
      }
    }
  },
  "$defs": {
    "Message": {
      "type": "object",
      "required": ["role", "parts"],
      "properties": {
        "role": { "enum": ["user", "agent"] },
        "parts": {
          "type": "array",
          "items": { "$ref": "#/$defs/Part" }
        }
      }
    },
    "Part": {
      "oneOf": [
        {
          "type": "object",
          "properties": {
            "type": { "const": "text" },
            "text": { "type": "string" }
          },
          "required": ["type", "text"]
        },
        {
          "type": "object",
          "properties": {
            "type": { "const": "file" },
            "file": {
              "type": "object",
              "properties": {
                "name": { "type": "string" },
                "mimeType": { "type": "string" },
                "bytes": { "type": "string", "contentEncoding": "base64" },
                "uri": { "type": "string", "format": "uri" }
              }
            }
          },
          "required": ["type", "file"]
        },
        {
          "type": "object",
          "properties": {
            "type": { "const": "data" },
            "data": { "type": "object" }
          },
          "required": ["type", "data"]
        }
      ]
    },
    "PushNotificationConfig": {
      "type": "object",
      "properties": {
        "url": { "type": "string", "format": "uri" },
        "token": { "type": "string" },
        "authentication": {
          "type": "object",
          "properties": {
            "schemes": { "type": "array", "items": { "type": "string" } }
          }
        }
      }
    }
  }
}
```

### 2.2 Task Lifecycle 상태 머신

```
                    ┌──────────┐
         ┌────────▶│ submitted │
         │         └─────┬─────┘
         │               │ agent accepts
   tasks/send            ▼
         │         ┌──────────┐    input-required
         │    ┌───▶│ working  │──────────────────┐
         │    │    └─────┬─────┘                  ▼
         │    │          │                ┌───────────────┐
         │    │    partial result         │ input-required│
         │    │          │                └───────┬───────┘
         │    └──────────┘                        │ user responds
         │               │                        │
         │         completed / failed ◄───────────┘
         │               │
         │    ┌──────────┼──────────┐
         │    ▼          ▼          ▼
         │ ┌─────┐  ┌────────┐  ┌──────────┐
         │ │compl.│ │ failed │  │ canceled │
         │ └─────┘  └────────┘  └──────────┘
```

```typescript
type TaskState = "submitted" | "working" | "input-required"
               | "completed" | "failed" | "canceled";

interface TaskStatusEvent {
  id: string;
  status: {
    state: TaskState;
    timestamp: string;         // ISO 8601
    message?: Message;
    progress?: { current: number; total: number; unit: string };
  };
  final: boolean;
  metadata?: Record<string, unknown>;
}

interface TaskArtifactEvent {
  id: string;
  artifact: {
    name: string;
    description?: string;
    parts: Part[];
    metadata?: Record<string, unknown>;
  };
  last_chunk?: boolean;
}
```

### 2.3 에이전트 카드 스펙

```json
{
  "name": "VAMOS Code Reviewer",
  "description": "AI 기반 코드 리뷰 에이전트",
  "url": "https://agents.vamos.dev/code-reviewer",
  "version": "2.0.0",
  "provider": {
    "organization": "VAMOS Team",
    "url": "https://vamos.dev"
  },
  "capabilities": {
    "streaming": true,
    "pushNotifications": true,
    "stateTransitionHistory": true
  },
  "authentication": {
    "schemes": ["Bearer"],
    "credentials": null
  },
  "defaultInputModes": ["text", "file"],
  "defaultOutputModes": ["text", "file"],
  "skills": [
    {
      "id": "code-review",
      "name": "코드 리뷰",
      "description": "PR 또는 코드 스니펫에 대한 상세 리뷰 수행",
      "tags": ["code", "review", "quality"],
      "examples": [
        "이 PR을 리뷰해 주세요",
        "이 함수의 보안 취약점을 점검해 주세요"
      ]
    }
  ]
}
```

---

## 3. 에이전트 디스커버리 (서브도메인 B)

### 3.1 mDNS/DNS-SD 프로토콜

```
┌──────────┐    mDNS Query     ┌──────────────┐
│  Client  │ ─────────────────▶│ mDNS Responder│
│  Agent   │ ◀─────────────────│  (Agent Host) │
└──────────┘   SRV + TXT       └──────────────┘

DNS-SD Service Type: _vamos-a2a._tcp.local.
TXT Record Fields:
  - v=1                          (프로토콜 버전)
  - path=/a2a                    (엔드포인트 경로)
  - caps=streaming,push          (능력 목록)
  - agent-id=<UUID>              (에이전트 고유 ID)
```

### 3.2 서비스 등록 스키마

```typescript
interface AgentRegistration {
  agent_id: string;                     // UUID v4
  agent_card_url: string;               // /.well-known/agent.json 경로
  endpoint: string;                     // A2A 엔드포인트 URL
  capabilities: AgentCapability[];
  skills: SkillDescriptor[];
  health_check: {
    url: string;
    interval_seconds: number;
    timeout_ms: number;
  };
  metadata: {
    registered_at: string;
    ttl_seconds: number;
    priority: number;                   // 0(최고) ~ 100(최저)
    load_factor: number;                // 0.0 ~ 1.0 현재 부하
  };
}

type AgentCapability = "streaming" | "pushNotifications"
  | "stateTransitionHistory" | "multimodal" | "long_running";
```

### 3.3 에이전트 선택 알고리즘

```python
def select_agent(task: TaskRequest, registry: AgentRegistry) -> Agent:
    """최적 에이전트 선택: 능력매칭 → 부하균형 → 우선순위"""
    candidates = registry.find_by_skills(task.required_skills)

    scored = []
    for agent in candidates:
        skill_match = jaccard_similarity(
            set(task.required_skills),
            set(agent.skills)
        )
        load_score = 1.0 - agent.metadata.load_factor
        priority_score = 1.0 - (agent.metadata.priority / 100.0)
        latency_score = 1.0 / (1.0 + agent.avg_latency_ms / 1000.0)

        total = (
            0.40 * skill_match +
            0.25 * load_score +
            0.20 * priority_score +
            0.15 * latency_score
        )
        scored.append((agent, total))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[0][0] if scored else raise_no_agent_error(task)
```

---

## 4. A2A 보안 (서브도메인 C)

### 4.1 mTLS + JWT 인증 상세

```
┌──────────┐                          ┌──────────┐
│ Agent A  │ ── mTLS Handshake ─────▶ │ Agent B  │
│          │    (X.509 cert verify)   │          │
│          │                          │          │
│          │ ── JWT Bearer Token ───▶ │          │
│          │    (Authorization header)│          │
└──────────┘                          └──────────┘

JWT Claims:
{
  "iss": "vamos-auth.dev",
  "sub": "agent:code-reviewer-001",
  "aud": "agent:code-generator-002",
  "exp": 1711180800,
  "iat": 1711177200,
  "scope": ["tasks/send", "tasks/get"],
  "delegation_chain": ["orchestrator-001", "code-reviewer-001"],
  "vamos:trust_level": "verified"
}
```

### 4.2 권한 위임 체인

```typescript
interface DelegationToken {
  issuer_agent_id: string;
  delegate_agent_id: string;
  permissions: Permission[];
  constraints: {
    max_depth: number;            // 위임 깊이 제한 (기본 3)
    allowed_methods: string[];
    time_limit_seconds: number;
    resource_budget: {
      max_tokens: number;
      max_api_calls: number;
    };
  };
  parent_token?: string;          // 체인 추적용
  signature: string;              // Ed25519 서명
}

type Permission = "task:create" | "task:read" | "task:cancel"
  | "artifact:read" | "artifact:write" | "agent:discover";
```

### 4.3 감사 로깅 스키마

```json
{
  "event_id": "evt_a1b2c3d4",
  "timestamp": "2026-03-22T10:30:00Z",
  "event_type": "a2a.task.send",
  "source_agent": "agent:orchestrator-001",
  "target_agent": "agent:code-reviewer-001",
  "task_id": "task_xyz789",
  "session_id": "sess_abc123",
  "method": "tasks/send",
  "auth": {
    "scheme": "Bearer",
    "jwt_claims_hash": "sha256:abcdef...",
    "delegation_depth": 1
  },
  "result": {
    "status": "accepted",
    "latency_ms": 45
  },
  "metadata": {
    "client_ip": "10.0.1.50",
    "tls_version": "1.3",
    "cert_fingerprint": "sha256:123456..."
  }
}
```

### 4.4 에러 복구 패턴

| 에러 코드 | 상황 | 복구 전략 |
|----------|------|----------|
| `-32001` | Task not found | 세션 재생성 후 재전송 |
| `-32002` | Task cannot be canceled | 상태 폴링 후 완료 대기 |
| `-32003` | Push notification not supported | SSE 스트리밍으로 폴백 |
| `-32004` | Unsupported operation | 에이전트 카드 재조회 후 대체 에이전트 선택 |
| `-32005` | Content type not supported | Part 변환 후 재전송 |
| `408` | Timeout | 지수 백오프 재시도 (최대 3회) |
| `429` | Rate limited | Retry-After 헤더 준수 |
| `503` | Agent unavailable | 레지스트리에서 대체 에이전트 선택 |

---

## 5. 대화 프로세스 고급 기능 (서브도메인 D)

### 5.1 V2 확장 기능 (8건)

| # | 기능 | 설명 | 상태 |
|---|------|------|------|
| 1 | Streaming SSE | Server-Sent Events 기반 실시간 스트리밍 | 구현 |
| 2 | Push Notifications | 웹훅 기반 비동기 알림 | 구현 |
| 3 | State Transition History | Task 상태 변이 이력 조회 | 구현 |
| 4 | Multi-turn Sessions | 세션 기반 다회전 대화 | 구현 |
| 5 | Artifact Chunking | 대용량 아티팩트 분할 전송 | 설계 |
| 6 | Agent Composition | 에이전트 체이닝/병렬 실행 | 설계 |
| 7 | Priority Queuing | 작업 우선순위 큐잉 | 계획 |
| 8 | Conversation Branching | 대화 분기/병합 | 계획 |

### 5.2 대화 상태 머신

```
[idle] ──(user_message)──▶ [awaiting_agent]
                                  │
                    ┌─────────────┼──────────────┐
                    ▼             ▼              ▼
             [agent_thinking] [agent_delegating] [agent_streaming]
                    │             │              │
                    │     [sub_task_waiting]     │
                    │             │              │
                    └─────────────┼──────────────┘
                                  ▼
                          [response_ready]
                                  │
                    ┌─────────────┼──────────────┐
                    ▼             ▼              ▼
              [completed]  [follow_up_needed]  [error]
                                  │
                           (user_message)
                                  │
                          [awaiting_agent] ←──── (루프)
```

### 5.3 MoA (Mixture-of-Agents) 패턴

```python
class MixtureOfAgents:
    """다중 에이전트 합의 기반 응답 생성"""

    def __init__(self, proposer_agents: list[str], aggregator_agent: str):
        self.proposers = proposer_agents
        self.aggregator = aggregator_agent

    async def execute(self, task: TaskRequest) -> TaskResult:
        # Phase 1: 병렬 제안 수집
        proposals = await asyncio.gather(*[
            self.send_task(agent_id, task)
            for agent_id in self.proposers
        ])

        # Phase 2: 집계 에이전트가 최종 응답 합성
        aggregation_task = TaskRequest(
            message=Message(
                role="user",
                parts=[
                    TextPart(f"다음 {len(proposals)}개 제안을 분석하여 최적 응답을 합성하세요:"),
                    *[TextPart(f"[제안 {i+1}]: {p.result}") for i, p in enumerate(proposals)]
                ]
            ),
            metadata={"pattern": "moa", "proposal_count": len(proposals)}
        )
        return await self.send_task(self.aggregator, aggregation_task)
```

---

## 6. A2A 모니터링/테스트 (서브도메인 E)

### 6.1 모니터링 대시보드 메트릭

```typescript
interface A2AMetrics {
  // 트래픽 메트릭
  total_tasks_24h: number;
  active_sessions: number;
  tasks_by_state: Record<TaskState, number>;
  tasks_by_method: Record<string, number>;

  // 성능 메트릭
  avg_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;

  // 안정성 메트릭
  success_rate: number;           // 0.0 ~ 1.0
  error_rate: number;
  timeout_rate: number;
  retry_rate: number;

  // 에이전트별 메트릭
  agents: Array<{
    agent_id: string;
    status: "healthy" | "degraded" | "down";
    tasks_processed: number;
    avg_response_time_ms: number;
    error_count: number;
    load_factor: number;
  }>;
}
```

### 6.2 A2A 테스트 프레임워크

```typescript
interface A2ATestCase {
  name: string;
  description: string;
  type: "unit" | "integration" | "e2e" | "chaos";
  setup: {
    mock_agents: MockAgentConfig[];
    mock_registry: boolean;
  };
  steps: TestStep[];
  assertions: Assertion[];
  cleanup: CleanupAction[];
}

interface TestStep {
  action: "send_task" | "cancel_task" | "wait_status"
        | "inject_fault" | "verify_metric";
  params: Record<string, unknown>;
  timeout_ms: number;
}

// 예시 테스트 케이스
const exampleTest: A2ATestCase = {
  name: "Task delegation with timeout recovery",
  description: "에이전트 타임아웃 시 대체 에이전트로 위임 확인",
  type: "integration",
  setup: {
    mock_agents: [
      { id: "slow-agent", latency_ms: 30000 },
      { id: "fast-agent", latency_ms: 500 }
    ],
    mock_registry: true
  },
  steps: [
    { action: "send_task", params: { target: "slow-agent" }, timeout_ms: 5000 },
    { action: "wait_status", params: { expected: "failed" }, timeout_ms: 10000 },
    { action: "verify_metric", params: { metric: "retry_count", expected: 1 }, timeout_ms: 1000 }
  ],
  assertions: [
    { type: "task_completed", agent: "fast-agent" },
    { type: "audit_log_contains", event: "agent_failover" }
  ],
  cleanup: []
};
```

### 6.3 에러 핸들링 체계

```
[A2A Error] → [Error Classifier]
                     │
           ┌─────────┼──────────┐
           ▼         ▼          ▼
      [Transient] [Permanent] [Unknown]
           │         │          │
    [Retry with    [Report &  [Log &
     backoff]      failover]  escalate]
           │         │          │
           └─────────┼──────────┘
                     ▼
            [Error Resolution]
                     │
           ┌─────────┼──────────┐
           ▼         ▼          ▼
      [Recovered] [Degraded]  [Failed]
                  [mode]
```

---

## 7. 의존성 매트릭스

| 의존 대상 | 도메인 | 의존 유형 |
|-----------|--------|----------|
| Agent Protocol | TIER3-10 | 프로토콜 호환 레이어 |
| MCP Server | TIER4-03 | 도구 호출 위임 |
| Blue Node | TIER2-01 | 오케스트레이션 엔진 |
| Verifier | TIER1-01 | 응답 검증 |
| CI/CD | TIER4-02 | 테스트 자동화 |

---

*본 문서는 STEP7-B 및 D2.0-05 SOT를 기반으로 작성되었으며, A2A 프로토콜 표준 업데이트에 따라 갱신된다.*
