# 3-10. Agent Protocol / Interoperability 상세명세

| 항목 | 내용 |
|------|------|
| **도메인 ID** | `TIER3-DOMAIN-10` |
| **SOT 근거** | STEP7-K (86 items) — Parts 3-8 중 ~50 items 미매핑 |
| **Part2 현황** | PARTIAL — 약 50개 항목이 구현 가이드에 미반영 |
| **최종 갱신** | 2026-03-22 |
| **상태** | DRAFT v1.0 |

---

## 1. 개요 및 범위

VAMOS 에이전트 프로토콜 및 상호운용성 계층은 외부 에이전트 프레임워크 통합,
서비스 간 통신, 에이전트 배포/스케일링, 그리고 VAMOS 고유의 차별화 전략을 포괄한다.
STEP7-K의 86개 항목 중 기존 미매핑 ~50개 항목을 중점 커버한다.

### 1.1 서브도메인 구성

| # | 서브도메인 | 항목 수 | 우선순위 |
|---|-----------|---------|---------|
| A | 멀티 에이전트 프레임워크 통합 | 12 | P0 |
| B | 외부 서비스 통합 프로토콜 | 10 | P0 |
| C | 데이터 교환 포맷 | 8 | P1 |
| D | 에이전트 배포/스케일링 | 8 | P1 |
| E | VAMOS 에이전트 차별화 전략 | 7 | P1 |
| F | 에이전트 자율성/안전성 | 5 | P0 |

### 1.2 아키텍처 개요

```
┌─────────────────────────────────────────────────────┐
│                  VAMOS Agent Platform                │
│  ┌───────────────────────────────────────────────┐  │
│  │           Interoperability Layer               │  │
│  │  ┌──────────┬──────────┬──────────┬────────┐  │  │
│  │  │ CrewAI   │ AutoGen  │ LangGraph│ Custom │  │  │
│  │  │ Adapter  │ Adapter  │ Adapter  │ Adapter│  │  │
│  │  └────┬─────┴────┬─────┴────┬─────┴───┬────┘  │  │
│  │       └──────────┼──────────┘         │       │  │
│  │           ┌──────▼──────┐             │       │  │
│  │           │  Protocol   │◄────────────┘       │  │
│  │           │  Translator │                     │  │
│  │           └──────┬──────┘                     │  │
│  │                  ▼                            │  │
│  │  ┌─────────────────────────────────────┐      │  │
│  │  │     VAMOS Unified Agent Bus          │      │  │
│  │  │  (A2A + MCP + REST/gRPC/WebSocket)  │      │  │
│  │  └─────────────────────────────────────┘      │  │
│  └───────────────────────────────────────────────┘  │
│  ┌──────────┐ ┌──────────────┐ ┌─────────────────┐ │
│  │ Deployer │ │ Safety Guard │ │ Self-Evolution  │ │
│  └──────────┘ └──────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────┘
```

---

## 2. 멀티 에이전트 프레임워크 통합 (서브도메인 A)

### 2.1 프레임워크 호환 레이어

```typescript
interface FrameworkAdapter {
  framework_id: string;
  framework_name: "crewai" | "autogen" | "langgraph" | "custom";
  version_range: string;
  capabilities: AdapterCapability[];
  translate_to_vamos(external_msg: unknown): VAMOSMessage;
  translate_from_vamos(vamos_msg: VAMOSMessage): unknown;
}

type AdapterCapability =
  | "task_delegation"      // 작업 위임
  | "state_sync"          // 상태 동기화
  | "tool_sharing"        // 도구 공유
  | "memory_bridge"       // 메모리 브릿지
  | "event_forwarding";   // 이벤트 전달
```

### 2.2 CrewAI 연동 패턴

```python
class CrewAIAdapter(FrameworkAdapter):
    """CrewAI ↔ VAMOS 프로토콜 변환기"""

    def translate_to_vamos(self, crew_task: CrewAITask) -> VAMOSMessage:
        return VAMOSMessage(
            method="tasks/send",
            params={
                "id": str(uuid4()),
                "message": {
                    "role": "user",
                    "parts": [{"type": "text", "text": crew_task.description}]
                },
                "metadata": {
                    "source_framework": "crewai",
                    "crew_name": crew_task.crew_name,
                    "agent_role": crew_task.agent.role,
                    "expected_output": crew_task.expected_output,
                    "tools": [t.name for t in crew_task.tools]
                }
            }
        )

    def translate_from_vamos(self, vamos_response: TaskResult) -> CrewAIOutput:
        return CrewAIOutput(
            raw=vamos_response.artifacts[0].parts[0].text,
            agent=vamos_response.metadata.get("agent_id"),
            tasks_output=self._map_artifacts(vamos_response.artifacts)
        )

    def bridge_tools(self, crew_tools: list[CrewAITool]) -> list[MCPTool]:
        """CrewAI 도구를 MCP 도구 형식으로 변환"""
        return [
            MCPTool(
                name=tool.name,
                description=tool.description,
                input_schema=self._infer_schema(tool.func),
                handler=lambda params: tool.func(**params)
            )
            for tool in crew_tools
        ]
```

### 2.3 AutoGen 연동 패턴

```python
class AutoGenAdapter(FrameworkAdapter):
    """AutoGen ↔ VAMOS 대화 프로토콜 매핑"""

    def map_autogen_agents(self, groupchat: AutoGenGroupChat) -> list[VAMOSAgent]:
        agents = []
        for ag in groupchat.agents:
            agents.append(VAMOSAgent(
                agent_card={
                    "name": ag.name,
                    "description": ag.system_message[:200],
                    "skills": self._extract_skills(ag),
                    "capabilities": {"streaming": True}
                },
                a2a_endpoint=f"/autogen-bridge/{ag.name}"
            ))
        return agents

    def translate_conversation(self, autogen_msgs: list) -> list[A2AMessage]:
        """AutoGen 대화 히스토리를 A2A 메시지 시퀀스로 변환"""
        return [
            A2AMessage(
                role="agent" if msg["role"] == "assistant" else "user",
                parts=[TextPart(msg["content"])],
                metadata={"autogen_sender": msg.get("name")}
            )
            for msg in autogen_msgs
        ]
```

### 2.4 LangGraph 연동 패턴

```python
class LangGraphAdapter(FrameworkAdapter):
    """LangGraph 상태 그래프 ↔ VAMOS Task 매핑"""

    def graph_to_task_chain(self, graph: LangGraph) -> list[VAMOSTask]:
        """LangGraph의 노드/엣지를 VAMOS Task 체인으로 변환"""
        tasks = []
        for node in graph.topological_sort():
            task = VAMOSTask(
                id=f"lg-{node.id}",
                dependencies=[f"lg-{dep}" for dep in node.input_edges],
                message=Message(
                    role="user",
                    parts=[TextPart(node.prompt_template)]
                ),
                metadata={
                    "langgraph_node": node.id,
                    "node_type": node.type,   # "agent" | "tool" | "condition"
                    "state_keys": list(node.state_schema.keys())
                }
            )
            tasks.append(task)
        return tasks

    def sync_state(self, lg_state: dict, vamos_context: dict) -> dict:
        """LangGraph 상태와 VAMOS 컨텍스트 양방향 동기화"""
        merged = {**lg_state}
        for key in self.state_mapping:
            if key in vamos_context:
                merged[self.state_mapping[key]] = vamos_context[key]
        return merged
```

---

## 3. 외부 서비스 통합 프로토콜 (서브도메인 B)

### 3.1 프로토콜 어댑터 아키텍처

```
┌──────────────────────────────────────────┐
│          Service Adapter Layer            │
│  ┌──────────┬───────────┬─────────────┐  │
│  │   REST   │   gRPC    │  WebSocket  │  │
│  │ Adapter  │  Adapter  │  Adapter    │  │
│  └────┬─────┴─────┬─────┴──────┬──────┘  │
│       └───────────┼────────────┘         │
│            ┌──────▼──────┐               │
│            │  Unified    │               │
│            │  Service    │               │
│            │  Interface  │               │
│            └──────┬──────┘               │
│                   ▼                      │
│         ┌─────────────────┐              │
│         │ Service Registry│              │
│         │ + Health Check  │              │
│         └─────────────────┘              │
└──────────────────────────────────────────┘
```

### 3.2 서비스 레지스트리 스키마

```typescript
interface ServiceRegistration {
  service_id: string;
  name: string;
  protocol: "rest" | "grpc" | "websocket" | "a2a";
  endpoints: Endpoint[];
  health_check: HealthCheckConfig;
  auth: AuthConfig;
  rate_limits: RateLimitConfig;
  metadata: Record<string, unknown>;
}

interface Endpoint {
  url: string;
  protocol_version: string;
  methods: MethodDescriptor[];
  tls_required: boolean;
  region: string;
  weight: number;                   // 로드밸런싱 가중치
}

interface HealthCheckConfig {
  type: "http" | "grpc" | "tcp";
  path: string;                     // "/health" or grpc.health.v1
  interval_seconds: number;
  timeout_ms: number;
  healthy_threshold: number;        // 연속 성공 횟수
  unhealthy_threshold: number;      // 연속 실패 횟수
}

interface MethodDescriptor {
  name: string;
  http_method?: "GET" | "POST" | "PUT" | "DELETE";
  path?: string;
  grpc_service?: string;
  input_schema: JSONSchema;
  output_schema: JSONSchema;
  streaming: boolean;
  timeout_ms: number;
}
```

### 3.3 헬스 체크 상태 머신

```
[unknown] ──(첫 체크 성공)──▶ [healthy]
    │                            │
    │                     (실패 1~N회)
    │                            ▼
    │                       [degraded]
    │                            │
    │                   (threshold 초과)
    │                            ▼
    └──(첫 체크 실패)──▶    [unhealthy]
                                │
                         (재시도 성공)
                                ▼
                          [recovering] ──(threshold 충족)──▶ [healthy]
```

---

## 4. 데이터 교환 포맷 (서브도메인 C)

### 4.1 에이전트 간 메시지 스키마

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "VAMOS-AgentMessage",
  "type": "object",
  "required": ["header", "body"],
  "properties": {
    "header": {
      "type": "object",
      "required": ["message_id", "version", "timestamp", "source", "target"],
      "properties": {
        "message_id": { "type": "string", "format": "uuid" },
        "version": { "type": "string", "pattern": "^\\d+\\.\\d+$" },
        "timestamp": { "type": "string", "format": "date-time" },
        "source": {
          "type": "object",
          "properties": {
            "agent_id": { "type": "string" },
            "framework": { "type": "string" },
            "instance_id": { "type": "string" }
          }
        },
        "target": {
          "type": "object",
          "properties": {
            "agent_id": { "type": "string" },
            "broadcast": { "type": "boolean", "default": false }
          }
        },
        "correlation_id": { "type": "string" },
        "trace_id": { "type": "string" },
        "priority": { "type": "integer", "minimum": 0, "maximum": 10 },
        "ttl_seconds": { "type": "integer" }
      }
    },
    "body": {
      "type": "object",
      "properties": {
        "content_type": {
          "enum": ["task", "result", "event", "heartbeat", "control"]
        },
        "encoding": { "enum": ["json", "msgpack", "protobuf", "cbor"] },
        "payload": {},
        "attachments": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "name": { "type": "string" },
              "mime_type": { "type": "string" },
              "size_bytes": { "type": "integer" },
              "data": { "type": "string" },
              "uri": { "type": "string", "format": "uri" }
            }
          }
        }
      }
    }
  }
}
```

### 4.2 직렬화/역직렬화 전략

| 포맷 | 사용 시나리오 | 장점 | 단점 |
|------|-------------|------|------|
| JSON | 기본 통신, 디버깅 | 가독성, 호환성 | 크기, 파싱 속도 |
| MessagePack | 고빈도 메시지 | 소형, 빠른 파싱 | 가독성 낮음 |
| Protocol Buffers | gRPC 서비스 | 타입 안전, 소형 | 스키마 관리 |
| CBOR | IoT/경량 에이전트 | 초소형, 바이너리 | 도구 지원 제한 |

```python
class MessageSerializer:
    """에이전트 메시지 다중 포맷 직렬화/역직렬화"""

    SERIALIZERS = {
        "json": (json.dumps, json.loads),
        "msgpack": (msgpack.packb, msgpack.unpackb),
        "protobuf": (proto_serialize, proto_deserialize),
        "cbor": (cbor2.dumps, cbor2.loads),
    }

    def serialize(self, msg: AgentMessage, encoding: str = "json") -> bytes:
        serialize_fn, _ = self.SERIALIZERS[encoding]
        header = self._serialize_header(msg.header)
        body = serialize_fn(msg.body.to_dict())
        return header + body

    def deserialize(self, data: bytes, encoding: str = "json") -> AgentMessage:
        _, deserialize_fn = self.SERIALIZERS[encoding]
        header, body_bytes = self._split_header(data)
        body = deserialize_fn(body_bytes)
        return AgentMessage(header=header, body=AgentBody.from_dict(body))
```

### 4.3 스키마 버전 관리

```yaml
schema_versioning:
  strategy: "semantic_versioning"
  compatibility_rules:
    - "MINOR 버전: 필드 추가만 허용 (하위 호환)"
    - "MAJOR 버전: 호환 깨지는 변경 허용"
    - "모든 메시지에 version 필드 포함"

  migration:
    registry_url: "https://schema.vamos.dev/agent-messages"
    auto_upgrade: true
    max_version_gap: 2       # 2 버전 이상 차이 시 업그레이드 강제

  negotiation:
    # 에이전트 간 스키마 버전 협상
    algorithm: |
      1. 연결 시 지원 버전 목록 교환
      2. 양쪽 모두 지원하는 최신 버전 선택
      3. 합의 실패 시 JSON 기본 포맷으로 폴백
```

---

## 5. 에이전트 배포/스케일링 (서브도메인 D)

### 5.1 컨테이너화 스펙

```yaml
# VAMOS Agent Dockerfile 표준
agent_container_spec:
  base_image: "vamos/agent-runtime:2.0"
  required_labels:
    - "vamos.agent.id"
    - "vamos.agent.version"
    - "vamos.agent.capabilities"
    - "vamos.agent.resource-class"

  resource_classes:
    light:
      cpu: "0.5"
      memory: "512Mi"
      gpu: null
      use_case: "텍스트 처리, 간단한 도구 호출"
    standard:
      cpu: "2"
      memory: "4Gi"
      gpu: null
      use_case: "코드 생성, 멀티턴 대화"
    heavy:
      cpu: "4"
      memory: "16Gi"
      gpu: "1x T4"
      use_case: "로컬 LLM 추론, 멀티모달"

  health_probes:
    liveness:
      path: "/health/live"
      period_seconds: 10
    readiness:
      path: "/health/ready"
      period_seconds: 5
    startup:
      path: "/health/startup"
      failure_threshold: 30
```

### 5.2 오토스케일링 정책

```typescript
interface AutoScalingPolicy {
  agent_type: string;
  min_replicas: number;
  max_replicas: number;
  metrics: ScalingMetric[];
  cooldown_seconds: number;
  scale_up_stabilization_seconds: number;
  scale_down_stabilization_seconds: number;
}

interface ScalingMetric {
  type: "cpu" | "memory" | "queue_depth" | "latency" | "custom";
  target_value: number;
  target_type: "average" | "total";
}

const defaultPolicy: AutoScalingPolicy = {
  agent_type: "code-generator",
  min_replicas: 2,
  max_replicas: 20,
  metrics: [
    { type: "cpu", target_value: 70, target_type: "average" },
    { type: "queue_depth", target_value: 10, target_type: "average" },
    { type: "latency", target_value: 2000, target_type: "average" }  // ms
  ],
  cooldown_seconds: 60,
  scale_up_stabilization_seconds: 30,
  scale_down_stabilization_seconds: 300
};
```

### 5.3 리소스 할당 알고리즘

```python
def allocate_resources(task: TaskRequest, available: ResourcePool) -> Allocation:
    """작업 복잡도 기반 동적 리소스 할당"""
    complexity = estimate_task_complexity(task)
    priority = task.metadata.get("priority", 5)

    if complexity < 0.3:
        resource_class = "light"
    elif complexity < 0.7:
        resource_class = "standard"
    else:
        resource_class = "heavy"

    # 우선순위 기반 큐 삽입
    queue_position = calculate_queue_position(priority, available.queue_length)

    # 리소스 예약
    allocation = available.reserve(
        resource_class=resource_class,
        timeout_ms=task.metadata.get("timeout_ms", 30000),
        preemptible=(priority < 3)
    )

    return Allocation(
        resource_class=resource_class,
        instance_id=allocation.instance_id,
        estimated_start_ms=queue_position * avg_processing_time,
        resources=allocation.resources
    )
```

---

## 6. VAMOS 에이전트 차별화 전략 (서브도메인 E)

### 6.1 자기 진화 (Self-Evolution) 아키텍처

```
┌─────────────────────────────────────────────┐
│            Self-Evolution Loop               │
│                                              │
│  [Task Execution] → [Outcome Evaluation]     │
│        ▲                    │                │
│        │             [Performance Metrics]    │
│        │                    │                │
│  [Updated Strategy] ← [Learning Engine]      │
│        │                    │                │
│  [Strategy Store]    [Experience Memory]      │
│                                              │
└─────────────────────────────────────────────┘
```

```typescript
interface SelfEvolutionConfig {
  learning_rate: number;            // 전략 업데이트 속도
  evaluation_window: number;        // 평가 기간 (작업 수)
  metrics_tracked: string[];        // 추적 메트릭
  evolution_triggers: EvolutionTrigger[];
  safety_bounds: {
    max_strategy_drift: number;     // 최대 전략 변경 폭
    require_human_approval: boolean;
    rollback_on_degradation: boolean;
  };
}

interface EvolutionTrigger {
  condition: "performance_drop" | "new_pattern_detected" | "scheduled";
  threshold: number;
  action: "fine_tune_prompt" | "adjust_parameters" | "request_review";
}
```

### 6.2 멀티 브레인 패턴

```
┌──────────── VAMOS Multi-Brain Agent ────────────┐
│                                                   │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Reasoning│ │ Creative │ │ Domain Expert    │ │
│  │ Brain    │ │ Brain    │ │ Brain            │ │
│  │ (논리추론)│ │ (창의생성)│ │ (도메인전문지식)   │ │
│  └────┬─────┘ └────┬─────┘ └───────┬──────────┘ │
│       └────────────┼───────────────┘             │
│             ┌──────▼──────┐                      │
│             │ Brain Router│ ← 작업 특성 분석       │
│             │ & Merger    │ → 응답 합성           │
│             └─────────────┘                      │
└──────────────────────────────────────────────────┘
```

### 6.3 VAMOS 프로토콜 확장

```typescript
// VAMOS 전용 A2A 확장 메서드
interface VAMOSProtocolExtensions {
  // 자기 진화 관련
  "vamos/evolution/getStrategy": {
    params: { agent_id: string };
    result: EvolutionStrategy;
  };
  "vamos/evolution/reportOutcome": {
    params: { task_id: string; outcome: TaskOutcome; metrics: Record<string, number> };
    result: { acknowledged: boolean };
  };

  // 멀티 브레인 관련
  "vamos/brain/route": {
    params: { task: TaskRequest; brain_preferences?: string[] };
    result: { selected_brain: string; confidence: number };
  };

  // 안전성 관련
  "vamos/safety/checkAction": {
    params: { action: ProposedAction; context: SafetyContext };
    result: { approved: boolean; reason: string; constraints: Constraint[] };
  };

  // 신뢰 관련
  "vamos/trust/getLevel": {
    params: { agent_id: string };
    result: { trust_level: number; history: TrustEvent[] };
  };
}
```

---

## 7. 에이전트 자율성/안전성 (서브도메인 F)

### 7.1 자율 레벨 정의

| 레벨 | 이름 | 설명 | 인간 개입 |
|------|------|------|----------|
| L0 | Manual | 인간이 모든 결정, 에이전트는 보조 | 모든 액션 승인 |
| L1 | Assisted | 에이전트가 제안, 인간이 승인 | 실행 전 확인 |
| L2 | Supervised | 에이전트가 실행, 인간이 모니터링 | 이상 시 개입 |
| L3 | Conditional | 범위 내 자율, 범위 외 승인 요청 | 경계 초과 시 |
| L4 | Autonomous | 완전 자율 실행, 사후 보고 | 사후 감사 |

### 7.2 안전 가드레일 스키마

```typescript
interface SafetyGuardrail {
  id: string;
  name: string;
  type: "pre_action" | "runtime" | "post_action";
  rules: SafetyRule[];
  enforcement: "block" | "warn" | "log";
}

interface SafetyRule {
  id: string;
  condition: string;                  // CEL (Common Expression Language)
  action_on_violation: "deny" | "escalate" | "modify" | "log";
  message: string;
}

const guardrails: SafetyGuardrail[] = [
  {
    id: "SG-001",
    name: "리소스 사용 제한",
    type: "pre_action",
    rules: [
      {
        id: "R-001",
        condition: "action.estimated_cost_usd > agent.budget_remaining",
        action_on_violation: "deny",
        message: "예산 초과: 에이전트 잔여 예산 부족"
      },
      {
        id: "R-002",
        condition: "action.api_calls_count > 100",
        action_on_violation: "escalate",
        message: "대량 API 호출: 인간 승인 필요"
      }
    ],
    enforcement: "block"
  },
  {
    id: "SG-002",
    name: "데이터 접근 제어",
    type: "pre_action",
    rules: [
      {
        id: "R-003",
        condition: "action.data_scope contains 'PII'",
        action_on_violation: "escalate",
        message: "PII 데이터 접근: 인간 승인 필요"
      },
      {
        id: "R-004",
        condition: "action.target_system in PRODUCTION_SYSTEMS",
        action_on_violation: "deny",
        message: "프로덕션 직접 접근 차단"
      }
    ],
    enforcement: "block"
  },
  {
    id: "SG-003",
    name: "실행 시간 모니터링",
    type: "runtime",
    rules: [
      {
        id: "R-005",
        condition: "execution.duration_ms > action.timeout_ms * 2",
        action_on_violation: "escalate",
        message: "실행 시간 초과: 태스크 점검 필요"
      }
    ],
    enforcement: "warn"
  }
];
```

### 7.3 인간 개입 포인트 (Human-in-the-Loop)

```
[에이전트 실행] → [가드레일 체크]
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
          [PASS]   [WARN]    [BLOCK]
              │        │        │
              ▼        ▼        ▼
          [계속]   [로그+계속]  [인간 큐 전달]
                                │
                     ┌──────────┼──────────┐
                     ▼          ▼          ▼
                [승인]      [수정]      [거부]
                  │          │          │
                  ▼          ▼          ▼
              [재실행]   [수정 후    [작업 취소]
                         재실행]
```

```typescript
interface HumanInterventionRequest {
  request_id: string;
  agent_id: string;
  task_id: string;
  urgency: "low" | "medium" | "high" | "critical";
  type: "approval" | "decision" | "review" | "error_resolution";
  context: {
    action_description: string;
    risk_assessment: string;
    guardrail_violations: string[];
    suggested_options: Option[];
  };
  timeout_seconds: number;
  default_action: "approve" | "deny" | "escalate";
  notification_channels: ("email" | "slack" | "ui" | "sms")[];
}
```

---

## 8. 의존성 매트릭스

| 의존 대상 | 도메인 | 의존 유형 |
|-----------|--------|----------|
| A2A/Conversation | TIER3-08 | A2A 프로토콜 기반 |
| Blue Node | TIER2-01 | 오케스트레이션 연동 |
| MCP Server/Client | TIER4-03 | 도구 프로토콜 |
| Verifier | TIER1-01 | 안전성 검증 |
| CI/CD | TIER4-02 | 배포 파이프라인 |
| Dev Tools | TIER3-07 | Plugin SDK 연동 |

---

## 9. 버전 로드맵

| 버전 | 시기 | 핵심 기능 |
|------|------|----------|
| v0.1 | Q2 2026 | REST 어댑터, 기본 서비스 레지스트리 |
| v0.2 | Q3 2026 | CrewAI/LangGraph 어댑터, 메시지 포맷 v1 |
| v0.3 | Q4 2026 | 오토스케일링, 안전 가드레일 v1 |
| v1.0 | Q1 2027 | 전체 프레임워크 통합, 자기 진화 MVP |
| v1.5 | Q3 2027 | 멀티 브레인 GA, 자율 레벨 L3 지원 |

---

*본 문서는 STEP7-K SOT 86개 항목(특히 Parts 3-8 미매핑 ~50개)을 기반으로 작성되었으며, 프로토콜 표준 업데이트에 따라 갱신된다.*
