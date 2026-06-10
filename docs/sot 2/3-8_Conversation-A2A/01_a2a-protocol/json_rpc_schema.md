# JSON-RPC 2.0 메시지 스키마

> **정본 소유**: sot 2/3-8_Conversation-A2A/01_a2a-protocol/json_rpc_schema.md
> **버전**: v1.0
> **작성일**: 2026-04-10
> **Phase**: 1 (MVP)
> **L3 상태**: L3
> **대응 항목**: §6.1 #1 (전체 스키마), #2~#9 (8개 메서드)

---

## 교차 참조 블록

| 정본 문서 | 참조 섹션 | 관계 |
|-----------|----------|------|
| 종합계획서 §3.4 | LOCK-A2A-01, LOCK-A2A-02, LOCK-A2A-03 | LOCK 값 원본 |
| 종합계획서 §6.1 #1~#9 | 항목 매핑 | 구현 대상 정의 |
| 종합계획서 부록 §A.1 | 8개 메서드 방향·설명 | 프로토콜 스펙 |
| 상세명세 §2.1 | JSON-RPC 2.0 메시지 구조, method enum | 스키마 원본 |
| 상세명세 §2.2 | TaskStatusEvent, TaskArtifactEvent | 이벤트 타입 참조 |
| 상세명세 §2.3 | AgentCard 스펙 | 공통 타입 참조 |
| 상세명세 §4.4 | 에러 복구 패턴 | 에러 응답 구조 |
| `task_lifecycle.md` (P1-2) | Task 상태 머신 | TaskState 공유 |
| `agent_card_spec.md` (P1-3) | AgentCard 스키마 | AgentCard 공유 |
| #13 Agent-Protocol | 프로토콜 추상 계층 | 상위 호환 (CLF-A2A-001) |
| #16 MCP-Server-Client | MCP 도구 스키마 | 위임 인터페이스 (CLF-A2A-002) |

---

## §1. 개요

본 문서는 VAMOS A2A 통신의 핵심인 JSON-RPC 2.0 메시지 포맷을 정의한다. Google A2A 프로토콜(2025.04)을 기반으로 8개 메서드의 요청(Request)/응답(Response) 스키마를 확정하고, 공통 재사용 타입을 분리 정의한다.

**범위**:
- JSON-RPC 2.0 Envelope 구조
- 8개 A2A 메서드 I/O 스키마
- 공통 타입 정의 (Task, TaskState, Message, Part, Artifact, AgentCard 등)
- 에러 응답 구조 (JSON-RPC 2.0 표준 + A2A 커스텀)

**Phase 2 제외 항목**:
- Artifact Chunking 상세 프로토콜 (§6.1 #9, Phase 3)
- Message Part 타입 확장 (§6.1 #10, Phase 2)
- A2A-MCP 브리지 인터페이스 (§6.1 #11, Phase 2)

---

## §2. 공통 자료 구조 (Common Types)

> 여러 메서드 스키마에서 재사용되는 타입을 선정의한다. 개별 메서드에서는 이 타입을 참조만 한다.

### 2.1 TaskState (LOCK-A2A-02)

```typescript
/**
 * Task 상태 열거형
 * LOCK-A2A-02: submitted|working|input-required|completed|failed|canceled
 * 변경 금지 — Google A2A Spec 정본
 */
type TaskState = "submitted" | "working" | "input-required"
               | "completed" | "failed" | "canceled";
```

### 2.2 Message (LOCK-A2A-03)

```typescript
/**
 * 대화 턴 구조
 * LOCK-A2A-03: role: "user"|"agent", parts: Part[]
 */
interface Message {
  role: "user" | "agent";
  parts: Part[];
}
```

### 2.3 Part

```typescript
/**
 * 메시지 파트 — text / file / data 3종
 * Phase 2에서 타입 확장 예정 (§6.1 #10)
 */
type Part = TextPart | FilePart | DataPart;

interface TextPart {
  type: "text";
  text: string;
}

interface FilePart {
  type: "file";
  file: {
    name?: string;
    mimeType?: string;
    bytes?: string;   // base64 encoded
    uri?: string;     // URI reference
  };
}

interface DataPart {
  type: "data";
  data: Record<string, unknown>;
}
```

### 2.4 Artifact

```typescript
interface Artifact {
  name: string;
  description?: string;
  parts: Part[];
  index?: number;
  append?: boolean;
  lastChunk?: boolean;
  metadata?: Record<string, unknown>;
}
```

### 2.5 Task

```typescript
interface Task {
  id: string;                          // Task 고유 ID (UUID v4)
  sessionId?: string;                  // 세션 ID (멀티턴 추적)
  status: TaskStatus;
  artifacts?: Artifact[];
  history?: Message[];                 // 대화 이력 (stateTransitionHistory 지원 시)
  metadata?: Record<string, unknown>;
}

interface TaskStatus {
  state: TaskState;                    // LOCK-A2A-02
  timestamp: string;                   // ISO 8601
  message?: Message;
  progress?: {
    current: number;
    total: number;
    unit: string;
  };
}
```

### 2.6 PushNotificationConfig

```typescript
interface PushNotificationConfig {
  url: string;                         // 웹훅 URL
  token?: string;                      // 인증 토큰
  authentication?: {
    schemes: string[];                 // e.g., ["Bearer"]
  };
}
```

### 2.7 AgentCard

```typescript
/**
 * 에이전트 카드 기본 구조
 * 상세 정의: agent_card_spec.md (P1-3)
 */
interface AgentCard {
  name: string;
  description: string;
  url: string;
  version: string;
  provider: {
    organization: string;
    url: string;
  };
  capabilities: AgentCapabilities;
  authentication: {
    schemes: string[];
    credentials?: string | null;
  };
  defaultInputModes: string[];
  defaultOutputModes: string[];
  skills: SkillDescriptor[];
  /** VAMOS 확장 — 부록 §A.2 */
  "x-vamos-extensions"?: {
    trust_level: "verified" | "unverified" | "internal";
    cost_tier: "free" | "standard" | "premium";
    max_concurrent_tasks: number;
    supported_languages: string[];
    blue_node_type: "research" | "content" | "dev" | "quant" | "trading";
  };
}

interface AgentCapabilities {
  streaming?: boolean;
  pushNotifications?: boolean;
  stateTransitionHistory?: boolean;
}

interface SkillDescriptor {
  id: string;
  name: string;
  description: string;
  tags?: string[];
  examples?: string[];
}
```

### 2.8 TaskIdParams / TaskQueryParams

```typescript
/** 공통 파라미터 — Task ID 기반 조회 */
interface TaskIdParams {
  id: string;                          // Task ID
  metadata?: Record<string, unknown>;
}

/** 공통 파라미터 — Task 전송 */
interface TaskSendParams {
  id: string;                          // Task ID
  sessionId?: string;                  // 세션 ID
  message: Message;                    // LOCK-A2A-03
  metadata?: Record<string, unknown>;
  pushNotificationConfig?: PushNotificationConfig;
  historyLength?: number;              // 이력 포함 길이
  acceptedOutputModes?: string[];      // 수용 가능 출력 모드
}
```

---

## §3. JSON-RPC 2.0 Envelope

### 3.1 Request Envelope

```typescript
/**
 * LOCK-A2A-01: "jsonrpc": "2.0"
 * JSON-RPC 2.0 요청 메시지 공통 구조
 */
interface A2ARequest<TParams = unknown> {
  jsonrpc: "2.0";                      // LOCK-A2A-01 — 고정값
  id: string | number;                 // 요청 ID (UUID 또는 정수)
  method: A2AMethod;                   // 8개 메서드 중 하나
  params?: TParams;                    // 메서드별 파라미터
}

type A2AMethod =
  | "tasks/send"
  | "tasks/sendSubscribe"
  | "tasks/get"
  | "tasks/cancel"
  | "tasks/pushNotification/set"
  | "tasks/pushNotification/get"
  | "tasks/resubscribe"
  | "agent/authenticatedExtendedCard";
```

### 3.2 Response Envelope

```typescript
/** JSON-RPC 2.0 성공 응답 */
interface A2ASuccessResponse<TResult = unknown> {
  jsonrpc: "2.0";                      // LOCK-A2A-01
  id: string | number;
  result: TResult;
}

/** JSON-RPC 2.0 에러 응답 */
interface A2AErrorResponse {
  jsonrpc: "2.0";                      // LOCK-A2A-01
  id: string | number | null;
  error: A2AError;
}

interface A2AError {
  code: number;                        // JSON-RPC 표준 또는 A2A 커스텀
  message: string;
  data?: {
    task_id?: string;
    detail?: string;
    retry_after_ms?: number;
    alternative_agent?: string;
  };
}

type A2AResponse<TResult = unknown> =
  | A2ASuccessResponse<TResult>
  | A2AErrorResponse;
```

### 3.3 SSE Event Envelope (Streaming)

```typescript
/** SSE 이벤트 — tasks/sendSubscribe, tasks/resubscribe 응답 스트림 */
type A2AStreamingEvent = TaskStatusEvent | TaskArtifactEvent;

interface TaskStatusEvent {
  id: string;                          // Task ID
  status: TaskStatus;
  final: boolean;                      // true면 스트림 종료
  metadata?: Record<string, unknown>;
}

interface TaskArtifactEvent {
  id: string;                          // Task ID
  artifact: Artifact;
  lastChunk?: boolean;
}
```

---

## §4. 8개 메서드 I/O 스키마

### 4.1 tasks/send (§6.1 #2)

> **방향**: Client -> Agent
> **설명**: 작업 전송 — 에이전트에 새 작업을 전달하거나 기존 작업에 추가 입력을 제공한다.

**Request**:
```typescript
type TasksSendRequest = A2ARequest<TaskSendParams>;
// method: "tasks/send"
// params: TaskSendParams (§2.8)
```

**Response (성공)**:
```typescript
type TasksSendResponse = A2ASuccessResponse<Task>;
// result: Task (§2.5) — 생성/갱신된 Task 객체
```

**Response (에러)**: `A2AErrorResponse` (§3.2)

**필수 파라미터**: `params.id`, `params.message`
**선택 파라미터**: `params.sessionId`, `params.metadata`, `params.pushNotificationConfig`, `params.historyLength`, `params.acceptedOutputModes`

---

### 4.2 tasks/sendSubscribe (§6.1 #3)

> **방향**: Client -> Agent
> **설명**: 작업 전송 + SSE 스트리밍 구독 — 작업을 전달하고 상태/아티팩트 이벤트를 실시간 수신한다.

**Request**:
```typescript
type TasksSendSubscribeRequest = A2ARequest<TaskSendParams>;
// method: "tasks/sendSubscribe"
// params: TaskSendParams (§2.8) — tasks/send와 동일
```

**Response (SSE Stream)**:
```
Content-Type: text/event-stream

event: status
data: {"id":"task_xyz","status":{"state":"working","timestamp":"..."},"final":false}

event: artifact
data: {"id":"task_xyz","artifact":{"name":"result","parts":[...]},"lastChunk":false}

event: status
data: {"id":"task_xyz","status":{"state":"completed","timestamp":"..."},"final":true}
```

각 SSE 이벤트는 `TaskStatusEvent` 또는 `TaskArtifactEvent` (§3.3) 형태이다.
스트림은 `final: true` 이벤트 수신 시 종료된다.

**에러**: 초기 연결 실패 시 `A2AErrorResponse`, 스트림 중 에러 시 `TaskStatusEvent { status.state: "failed", final: true }`

---

### 4.3 tasks/get (§6.1 #4)

> **방향**: Client -> Agent
> **설명**: 작업 상태 조회 — Task ID로 현재 상태 및 결과를 조회한다.

**Request**:
```typescript
interface TasksGetParams extends TaskIdParams {
  historyLength?: number;              // 반환할 이력 수 (0이면 이력 미포함)
}

type TasksGetRequest = A2ARequest<TasksGetParams>;
// method: "tasks/get"
```

**Response (성공)**:
```typescript
type TasksGetResponse = A2ASuccessResponse<Task>;
// result: Task (§2.5) — 현재 상태의 Task 객체
```

**에러**: Task 미존재 시 `-32001 Task not found`

---

### 4.4 tasks/cancel (§6.1 #5)

> **방향**: Client -> Agent
> **설명**: 작업 취소 — 진행 중인 Task를 취소 요청한다.

**Request**:
```typescript
type TasksCancelRequest = A2ARequest<TaskIdParams>;
// method: "tasks/cancel"
// params: { id: string }
```

**Response (성공)**:
```typescript
type TasksCancelResponse = A2ASuccessResponse<Task>;
// result: Task — status.state가 "canceled"로 전이된 Task
```

**에러**: 이미 완료/실패 상태이면 `-32002 Task cannot be canceled`

---

### 4.5 tasks/pushNotification/set (§6.1 #6)

> **방향**: Client -> Agent
> **설명**: 푸시 알림 설정 — Task의 상태 변경을 웹훅으로 수신하도록 구성한다.

**Request**:
```typescript
interface PushNotificationSetParams {
  id: string;                          // Task ID
  pushNotificationConfig: PushNotificationConfig;  // §2.6
}

type TasksPushNotificationSetRequest = A2ARequest<PushNotificationSetParams>;
// method: "tasks/pushNotification/set"
```

**Response (성공)**:
```typescript
interface PushNotificationSetResult {
  id: string;                          // Task ID
  pushNotificationConfig: PushNotificationConfig;  // 설정된 구성
}

type TasksPushNotificationSetResponse = A2ASuccessResponse<PushNotificationSetResult>;
```

**에러**: Push 미지원 시 `-32003 Push notification not supported`

---

### 4.6 tasks/pushNotification/get (§6.1 #7)

> **방향**: Client -> Agent
> **설명**: 푸시 알림 조회 — Task에 설정된 푸시 알림 구성을 조회한다.

**Request**:
```typescript
type TasksPushNotificationGetRequest = A2ARequest<TaskIdParams>;
// method: "tasks/pushNotification/get"
// params: { id: string }
```

**Response (성공)**:
```typescript
interface PushNotificationGetResult {
  id: string;
  pushNotificationConfig: PushNotificationConfig | null;  // 미설정 시 null
}

type TasksPushNotificationGetResponse = A2ASuccessResponse<PushNotificationGetResult>;
```

**에러**: Task 미존재 시 `-32001 Task not found`

---

### 4.7 tasks/resubscribe (§6.1 #8)

> **방향**: Client -> Agent
> **설명**: SSE 재구독 — 연결 끊김 후 기존 Task의 SSE 스트림에 다시 구독한다.

**Request**:
```typescript
type TasksResubscribeRequest = A2ARequest<TaskIdParams>;
// method: "tasks/resubscribe"
// params: { id: string }
```

**Response (SSE Stream)**:
`tasks/sendSubscribe`와 동일한 SSE 이벤트 스트림 (§3.3).
재구독 시점 이후의 이벤트부터 수신한다.

**에러**:
- Task 미존재: `-32001 Task not found`
- Task 이미 완료: `-32004 Unsupported operation` (완료된 Task는 재구독 불가)

---

### 4.8 agent/authenticatedExtendedCard (§6.1 #9)

> **방향**: Client -> Agent
> **설명**: 인증 후 확장 카드 조회 — mTLS/JWT 인증 후 에이전트의 확장 정보를 포함한 카드를 반환한다.

**Request**:
```typescript
interface AuthenticatedExtendedCardParams {
  /** 요청자의 에이전트 ID (상호 인증용) */
  requestorAgentId?: string;
  /** 필요한 확장 필드 목록 (빈 배열이면 전체) */
  requestedExtensions?: string[];
}

type AgentAuthExtCardRequest = A2ARequest<AuthenticatedExtendedCardParams>;
// method: "agent/authenticatedExtendedCard"
```

**Response (성공)**:
```typescript
type AgentAuthExtCardResponse = A2ASuccessResponse<AgentCard>;
// result: AgentCard (§2.7) — x-vamos-extensions 포함 전체 카드
```

**에러**:
- 인증 실패: JSON-RPC 표준 `-32600 Invalid Request` (Authorization 헤더 누락/만료)
- 미지원 확장: `-32004 Unsupported operation`

---

## §5. 에러 코드 체계

### 5.1 JSON-RPC 2.0 표준 에러

| 코드 | 메시지 | 설명 | recoverable | 처리 |
|------|--------|------|:-----------:|------|
| `-32700` | Parse error | JSON 파싱 실패 | NO | 요청 본문 검증 후 재전송 |
| `-32600` | Invalid Request | 유효하지 않은 JSON-RPC 요청 | NO | 요청 구조 검증 후 재전송 |
| `-32601` | Method not found | 미지원 메서드 | NO | 에이전트 카드 재조회 후 지원 메서드 확인 |
| `-32602` | Invalid params | 잘못된 파라미터 | NO | 파라미터 스키마 대조 후 재전송 |
| `-32603` | Internal error | 서버 내부 오류 | YES | 지수 백오프 재시도 (최대 3회), 실패 시 대체 에이전트 |

### 5.2 A2A 커스텀 에러

| 코드 | 메시지 | 설명 | recoverable | 복구 전략 |
|------|--------|------|:-----------:|----------|
| `-32001` | Task not found | 요청한 Task ID가 존재하지 않음 | YES | 세션 재생성 후 재전송 |
| `-32002` | Task cannot be canceled | 이미 완료/실패 상태인 Task 취소 시도 | NO | 상태 폴링 후 완료 대기 |
| `-32003` | Push notification not supported | 에이전트가 Push 미지원 | YES | SSE 스트리밍으로 폴백 |
| `-32004` | Unsupported operation | 에이전트가 해당 동작 미지원 | YES | 에이전트 카드 재조회 후 대체 에이전트 선택 |
| `-32005` | Content type not supported | 지원하지 않는 Part 타입 | YES | Part 변환 후 재전송 |

### 5.3 HTTP 레벨 에러

| HTTP 코드 | 상황 | recoverable | 복구 전략 |
|-----------|------|:-----------:|----------|
| `408` | Request Timeout | YES | 지수 백오프 재시도 (초기 1초, 최대 60초, 최대 3회) |
| `429` | Rate Limited | YES | `Retry-After` 헤더 값 준수 후 재시도 |
| `503` | Agent Unavailable | YES | 레지스트리에서 대체 에이전트 선택 (`02_agent-discovery/` 연동) |

### 5.4 Circuit Breaker (LOCK-A2A-09)

> LOCK-A2A-09: Circuit Breaker 연속 실패 임계 — 3회 → OPEN, 60초 후 HALF-OPEN

```
CLOSED ──(연속 3회 실패)──> OPEN ──(60초 경과)──> HALF-OPEN
  ^                                                    │
  └────────────────(1회 성공)───────────────────────────┘
                        │
          HALF-OPEN ──(실패)──> OPEN
```

---

## §6. 로깅 포맷 (R-01-7)

모든 A2A JSON-RPC 요청/응답은 다음 structured JSON 포맷으로 로깅한다.

```json
{
  "trace_id": "trc_a2a_20260410_abc123",
  "timestamp": "2026-04-10T11:30:00.000Z",
  "level": "INFO",
  "service": "a2a-gateway",
  "error": {
    "code": null,
    "message": null,
    "stack": null,
    "category": null
  },
  "context": {
    "method": "tasks/send",
    "request_id": "req_xyz789",
    "task_id": "task_001",
    "session_id": "sess_abc",
    "source_agent": "agent:orchestrator-001",
    "target_agent": "agent:code-reviewer-001",
    "auth_scheme": "Bearer",
    "delegation_depth": 1
  },
  "recovery": {
    "action": null,
    "retry_count": 0,
    "fallback_agent": null,
    "circuit_breaker_state": "CLOSED",
    "degraded_mode": false
  }
}
```

에러 발생 시 `error{}` 블록이 채워지고, 복구 동작이 있으면 `recovery{}` 블록이 갱신된다.

---

## §7. Phase별 복구 전략 상세

### 7.1 복구 흐름도

```
[에러 발생]
    │
    ▼
[에러 분류] ── Transient? ──> [Phase 1: 즉시 재시도]
    │                              │
    │                         성공? ──Y──> [완료]
    │                              │
    │                         N (재시도 소진)
    │                              │
    │                              ▼
    ├── Permanent? ──> [Phase 2: 폴백 전환]
    │                      │
    │                 대체 에이전트? ──Y──> [failover 실행]
    │                      │
    │                 N (대체 불가)
    │                      │
    │                      ▼
    ├── Unknown? ──> [Phase 3: 다운그레이드]
    │                      │
    │                 부분 결과? ──Y──> [Degraded Mode 반환]
    │                      │
    │                 N (결과 없음)
    │                      │
    │                      ▼
    └──────────────> [Phase 4: 에스컬레이션]
                           │
                           ▼
                     [I-20 경유 에스컬레이션]
```

### 7.2 다운그레이드 시 Confidence Penalty 표

| 상황 | Confidence 감산 | 결과 상태 | 비고 |
|------|----------------|----------|------|
| 1차 재시도 성공 | -0% | 정상 | 지연만 증가 |
| 2차 재시도 성공 | -5% | 정상 | 지연 경고 로깅 |
| 3차 재시도 성공 | -10% | 정상 | Circuit Breaker 카운터 증가 |
| 대체 에이전트 성공 | -15% | Degraded | 원본 에이전트 비교 불가 |
| 부분 결과 반환 | -30% | Degraded | 불완전 결과 표시 필수 |
| 에스컬레이션 (I-20) | -50% | Failed | 수동 개입 필요 |

### 7.3 에스컬레이션 페이로드 구조

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional

@dataclass
class EscalationPayload:
    """I-20 에스컬레이션 페이로드 (R-01-8)"""
    source_engine: str                          # 발생 엔진/모듈 ID
    error_code: int                             # A2A 에러 코드 또는 HTTP 코드
    original_request: dict[str, Any]            # 원본 JSON-RPC 요청
    partial_result: Optional[dict[str, Any]]    # 부분 결과 (있으면)
    retry_count: int                            # 재시도 횟수
    timestamp: datetime = field(default_factory=datetime.utcnow)
    trace_id: str = ""                          # 추적 ID
    confidence_penalty: float = 0.0             # 누적 감산
    circuit_breaker_state: str = "CLOSED"       # CB 상태
    fallback_agents_tried: list[str] = field(default_factory=list)
```

---

## §8. JSON Schema 정의 (기계 판독용)

> E1(I/O Schema) L3 기준 충족을 위한 JSON Schema 형식 전체 정의

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://vamos.dev/schemas/a2a/v1/json-rpc.schema.json",
  "title": "VAMOS A2A JSON-RPC 2.0 Schema",
  "description": "VAMOS A2A 8개 메서드의 Request/Response JSON Schema",

  "$defs": {
    "TaskState": {
      "type": "string",
      "enum": ["submitted", "working", "input-required", "completed", "failed", "canceled"],
      "description": "LOCK-A2A-02: Task 상태 열거형"
    },
    "Message": {
      "type": "object",
      "required": ["role", "parts"],
      "properties": {
        "role": { "enum": ["user", "agent"], "description": "LOCK-A2A-03 턴 구조" },
        "parts": { "type": "array", "items": { "$ref": "#/$defs/Part" }, "description": "LOCK-A2A-03 Part[]" }
      }
    },
    "Part": {
      "oneOf": [
        {
          "type": "object",
          "required": ["type", "text"],
          "properties": {
            "type": { "const": "text" },
            "text": { "type": "string" }
          }
        },
        {
          "type": "object",
          "required": ["type", "file"],
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
          }
        },
        {
          "type": "object",
          "required": ["type", "data"],
          "properties": {
            "type": { "const": "data" },
            "data": { "type": "object" }
          }
        }
      ]
    },
    "Artifact": {
      "type": "object",
      "required": ["name", "parts"],
      "properties": {
        "name": { "type": "string" },
        "description": { "type": "string" },
        "parts": { "type": "array", "items": { "$ref": "#/$defs/Part" } },
        "index": { "type": "integer" },
        "append": { "type": "boolean" },
        "lastChunk": { "type": "boolean" },
        "metadata": { "type": "object" }
      }
    },
    "TaskStatus": {
      "type": "object",
      "required": ["state"],
      "properties": {
        "state": { "$ref": "#/$defs/TaskState" },
        "timestamp": { "type": "string", "format": "date-time" },
        "message": { "$ref": "#/$defs/Message" },
        "progress": {
          "type": "object",
          "properties": {
            "current": { "type": "number" },
            "total": { "type": "number" },
            "unit": { "type": "string" }
          }
        }
      }
    },
    "Task": {
      "type": "object",
      "required": ["id", "status"],
      "properties": {
        "id": { "type": "string" },
        "sessionId": { "type": "string" },
        "status": { "$ref": "#/$defs/TaskStatus" },
        "artifacts": { "type": "array", "items": { "$ref": "#/$defs/Artifact" } },
        "history": { "type": "array", "items": { "$ref": "#/$defs/Message" } },
        "metadata": { "type": "object" }
      }
    },
    "PushNotificationConfig": {
      "type": "object",
      "required": ["url"],
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
    },
    "A2AError": {
      "type": "object",
      "required": ["code", "message"],
      "properties": {
        "code": { "type": "integer" },
        "message": { "type": "string" },
        "data": {
          "type": "object",
          "additionalProperties": true,
          "properties": {
            "task_id": { "type": "string" },
            "detail": { "type": "string" },
            "retry_after_ms": { "type": "integer" },
            "alternative_agent": { "type": "string" }
          }
        }
      }
    }
  },

  "type": "object",
  "required": ["jsonrpc", "method"],
  "properties": {
    "jsonrpc": {
      "const": "2.0",
      "description": "LOCK-A2A-01: JSON-RPC 2.0 프로토콜 버전 고정"
    },
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
        "agent/authenticatedExtendedCard",
        "artifact.chunk"
      ]
    },
    "params": { "type": "object" },
    "result": {},
    "error": { "$ref": "#/$defs/A2AError" }
  }
}
```

---

## §9. 의존성 명세 (E6)

| 대상 | 방향 | 내용 |
|------|------|------|
| `task_lifecycle.md` (P1-2) | -> 제공 | TaskState, TaskStatus, TaskStatusEvent, TaskArtifactEvent 공통 타입 |
| `agent_card_spec.md` (P1-3) | -> 제공 | AgentCard, AgentCapabilities, SkillDescriptor 공통 타입 |
| `error_codes.md` (P1-6) | -> 제공 | A2AError 구조, 에러 코드 카탈로그 |
| `02_agent-discovery/` (P1-4) | <- 소비 | mDNS TXT 레코드에서 AgentCard URL 획득 |
| `03_security/` (P1-5) | <- 소비 | JWT Claims 구조 (인증 헤더), mTLS 핸드셰이크 |
| #13 Agent-Protocol | -> 상위 호환 | 프로토콜 추상 계층과 A2A 메서드 매핑 |
| #16 MCP-Server-Client | -> 위임 참조 | A2A-MCP 브리지 시 MCP 도구 스키마 참조 (Phase 2) |

---

## §10. Phase 2 테스트 시나리오 (10건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|----------|----------|
| T-01 | tasks/send 정상 전송 | 유효한 TaskSendParams + Message | 200 OK, Task 객체 반환 (state: "submitted") |
| T-02 | tasks/send 필수 필드 누락 | params.message 미포함 | `-32602 Invalid params` |
| T-03 | tasks/get 존재하지 않는 Task | 임의 UUID로 tasks/get | `-32001 Task not found` |
| T-04 | tasks/cancel 완료된 Task | completed 상태 Task에 cancel | `-32002 Task cannot be canceled` |
| T-05 | tasks/sendSubscribe SSE 스트림 | 유효한 파라미터 전송 | SSE 스트림 개시, status/artifact 이벤트 수신, final:true로 종료 |
| T-06 | tasks/pushNotification/set 미지원 에이전트 | pushNotifications=false 에이전트에 설정 | `-32003 Push notification not supported` |
| T-07 | agent/authenticatedExtendedCard 인증 실패 | Authorization 헤더 없이 요청 | `-32600 Invalid Request` |
| T-08 | jsonrpc 버전 불일치 | `"jsonrpc": "1.0"` 전송 | `-32600 Invalid Request` (LOCK-A2A-01 위반) |
| T-09 | 미지원 메서드 호출 | `"method": "tasks/unknown"` | `-32601 Method not found` |
| T-10 | Circuit Breaker 트리거 | 동일 에이전트에 연속 3회 503 주입 | CB OPEN 전이, 60초 후 HALF-OPEN, 이후 요청은 대체 에이전트 |
| T-11 | tasks/resubscribe 완료된 Task | completed 상태 Task에 resubscribe | `-32004 Unsupported operation` |
| T-12 | 대용량 Message Part | 10MB base64 file Part 전송 | 정상 수신 또는 `-32005 Content type not supported` (미지원 시) |
| T-13 | 지수 백오프 재시도 | 408 Timeout 3회 연속 주입 후 4회째 성공 | 1초/2초/4초 간격 재시도 후 성공, recovery 로그 기록 |
| T-14 | 멀티턴 세션 연속 전송 | 동일 sessionId로 tasks/send 3회 | 3회 모두 동일 session context 유지, history 누적 |

---

## §11. LOCK 준수 확인

| LOCK ID | 값 (정본 원본 그대로) | 본 문서 반영 위치 | 정합 |
|---------|---------------------|-----------------|------|
| LOCK-A2A-01 | `"jsonrpc": "2.0"` | §3.1 A2ARequest.jsonrpc, §8 JSON Schema "const": "2.0" | OK |
| LOCK-A2A-02 | `submitted\|working\|input-required\|completed\|failed\|canceled` | §2.1 TaskState, §8 JSON Schema TaskState.enum | OK |
| LOCK-A2A-03 | `role: "user"\|"agent"`, `parts: Part[]` | §2.2 Message, §8 JSON Schema Message | OK |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 — 3회 → OPEN, 60초 후 HALF-OPEN | §5.4 Circuit Breaker | OK |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-10 | v1.0 | P1-1 초기 작성 — 8개 메서드 I/O 스키마, 공통 타입, 에러 체계, JSON Schema |
