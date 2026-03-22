# PHASE_B1_API_CONTRACT (v1.0.0)

## 0. 문서 메타

| 항목 | 값 |
|------|-----|
| 문서 ID | PHASE_B1 |
| 문서명 | PHASE_B1_API_CONTRACT |
| 버전 | 1.0.0 |
| 작성일 | 2026-02-22 |
| 역할 | VAMOS AI 에이전트 플랫폼 API/IPC 엔드포인트 계약서 |
| 상위 정본 | BASE 1.3 > PLAN 3.0 > DESIGN 2.0 > D2.1 Schemas |
| 소스 스키마 | D2(Orange Core), D3(Blue Nodes), D4(Infra Core), D5(Agent Workflow), D6(Storage Memory), D7(Safety/Cost/Approval), D8(UI/UX) |
| 기술 스택 | Tauri 2.0 + React (프론트) / Rust (IPC/시스템) / Python (AI/ML 백엔드) |
| 통신 방식 | Tauri IPC (Rust-React) / JSON-RPC over subprocess (Python-Rust) / MCP Streamable HTTP (도구) |

### 규칙

- 모든 요청에 `trace_id: string` 포함 (추적/감사용)
- Tauri IPC command 네이밍: `vamos:{category}:{action}` 패턴
- Python-Rust 통신: V1은 JSON-RPC over subprocess/stdin-stdout, V2+는 gRPC 전환 가능
- MCP 전송: Streamable HTTP only (DEC-017 LOCK, stdio 제거)
- 에러 응답 표준: `{ success: false, error: { code: string, message: string, trace_id: string } }`
- 성공 응답 표준: `{ success: true, data: T, trace_id: string }`
- 모든 엔드포인트는 D2.1 소스 스키마 필드 기반 도출 (추측 아닌 실제 필드)

---

## 1. 개요

### 1.1 API 계층 구조

VAMOS 플랫폼의 API는 3개 계층으로 구성된다.

```
+----------------------------------------------------------+
|  [Layer 1] Tauri IPC Commands (React <-> Rust)           |
|  - invoke: React -> Rust (요청-응답)                      |
|  - event:  Rust -> React (이벤트 푸시)                     |
+----------------------------------------------------------+
         |                               |
         v                               v
+---------------------------+  +---------------------------+
| [Layer 2] Python-Rust API |  | [Layer 3] MCP Tool Proto  |
| - JSON-RPC subprocess     |  | - Streamable HTTP (LOCK)  |
| - LangGraph StateGraph    |  | - Tool Discovery/Invoke   |
| - Embedding/LLM Adapter   |  | - MCP Bridge Layer        |
+---------------------------+  +---------------------------+
```

### 1.2 데이터 흐름

```
React UI  --[invoke]--> Rust IPC Handler
                            |
                  +---------+---------+
                  |                   |
           [JSON-RPC]          [MCP HTTP]
                  |                   |
           Python Backend       MCP Server
           (LangGraph/LLM)     (External Tools)
```

### 1.3 통신 프로토콜 요약

| 계층 | 방향 | 프로토콜 | 버전 |
|------|------|---------|------|
| Tauri IPC | React <-> Rust | Tauri invoke/event | V1+ |
| Python-Rust | Rust -> Python | JSON-RPC over subprocess stdin/stdout | V1 |
| Python-Rust | Rust -> Python | gRPC (선택 전환) | V2+ |
| MCP Tool | Python -> MCP Server | Streamable HTTP (DEC-017 LOCK) | V1+ |

---

## 2. Tauri IPC Commands (Rust <-> React)

> 모든 IPC command는 `vamos:{category}:{action}` 패턴을 따른다.
> 방향: `invoke` = React에서 Rust로 요청-응답, `event` = Rust에서 React로 단방향 푸시.

### 2.1 Core Commands (Decision / Workflow / Session)

#### 2.1.1 Decision 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:decision:create` | invoke | 새 Decision 생성 요청 |
| `vamos:decision:get` | invoke | Decision 조회 |
| `vamos:decision:list` | invoke | Decision 목록 조회 |
| `vamos:decision:lock` | invoke | Decision 잠금 (단일결정 원칙) |
| `vamos:decision:event` | event | Decision 상태 변경 이벤트 |

**`vamos:decision:create`** - Decision 생성

- 방향: invoke
- 소스 스키마: D2 DecisionSchema (v2.2.1)
- 요청 payload:

```typescript
{
  trace_id: string;               // 필수. Trace 연결 ID
  intent_frame_ref: string;       // 필수. IntentFrame 참조 (I-1 결과)
  evidence_pack_ref: string;      // 필수. EvidencePack 참조 (I-2 결과)
  output_spec?: {                 // 선택. 출력 스펙
    format_constraints: string;   // "markdown" 등
  };
}
```

- 응답 타입:

```typescript
{
  success: true;
  data: {
    decision_id: string;          // "dec_01HZX9R1ABCDE"
    trace_id: string;
    timestamp: string;            // ISO8601
    policy_gate: "deny" | "restrict" | "allow";
    approval_required: boolean;
    approval_status: "approved" | "denied";
    cost_gate: "normal" | "downshift" | "split" | "stop";
    routing: {
      selected_blue_node_id: string;
      execution_mode: "mini" | "main" | "tool";
    };
    memory_plan: {
      save_candidate: boolean;
      target_layer: "L0" | "L1" | "L2";
      requires_user_approval: boolean;
    };
    conclusion: "ACCEPT" | "REJECT" | "HOLD" | "ESCALATE";
    locked: boolean;
    optional_signals?: Array<{
      signal_id: string;
      source_module: string;
      name: string;
      value: number;
    }>;
    verify?: {
      chain_used: string[];
      refs: {
        policy_check_id?: string;
        cost_budget_id?: string;
      };
    };
    gates?: {
      result: {
        policy?: { decision: string };
        cost?: { mode: string };
      };
    };
  };
  trace_id: string;
}
```

**`vamos:decision:get`** - Decision 단건 조회

- 방향: invoke
- 요청 payload:

```typescript
{
  trace_id: string;
  decision_id: string;
}
```

- 응답: DecisionSchema 전체 필드

**`vamos:decision:list`** - Decision 목록 조회

- 방향: invoke
- 요청 payload:

```typescript
{
  trace_id: string;
  filter?: {
    conclusion?: "ACCEPT" | "REJECT" | "HOLD" | "ESCALATE";
    locked?: boolean;
    from_timestamp?: string;   // ISO8601
    to_timestamp?: string;     // ISO8601
  };
  pagination?: {
    offset: number;
    limit: number;             // 기본 20, 최대 100
  };
}
```

- 응답: `{ items: DecisionSchema[], total: number }`

**`vamos:decision:lock`** - Decision 잠금

- 방향: invoke
- 요청 payload:

```typescript
{
  trace_id: string;
  decision_id: string;
}
```

- 응답: `{ decision_id: string, locked: true }`

**`vamos:decision:event`** - Decision 상태 변경 이벤트

- 방향: event (Rust -> React)
- 페이로드:

```typescript
{
  event_type: "oc.i5.decision.locked" | "oc.i5.route.selected" | "oc.i5.approval.required";
  decision_id: string;
  trace_id: string;
  conclusion?: string;
  timestamp: string;
}
```

#### 2.1.2 Workflow 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:workflow:start` | invoke | 워크플로우 시작 (5단계 파이프라인 진입) |
| `vamos:workflow:status` | invoke | 현재 워크플로우 상태 조회 |
| `vamos:workflow:cancel` | invoke | 워크플로우 취소 |
| `vamos:workflow:output` | invoke | 워크플로우 최종 출력 조회 |
| `vamos:workflow:stage_event` | event | 워크플로우 단계 전환 이벤트 |
| `vamos:workflow:failure_report` | invoke | 실패 리포트 조회 |

**`vamos:workflow:start`** - 워크플로우 시작

- 방향: invoke
- 소스 스키마: D5 WorkflowStageSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  project_id: string;
  session_id: string;
  user_input: string;             // 사용자 입력 (자연어)
  autonomy_level?: "L0" | "L1" | "L2" | "L3";  // 자율 수준 (D7 §3.2.1)
  constraints?: object;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    workflow_id: string;
    trace_id: string;
    current_stage: "intake" | "plan" | "execute" | "verify" | "deliver";
    started_at: string;          // ISO8601
  };
  trace_id: string;
}
```

**`vamos:workflow:output`** - 워크플로우 최종 출력

- 방향: invoke
- 소스 스키마: D5 WorkflowOutputEnvelopeSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  workflow_id: string;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    user_response: string;         // 최종 결과
    evidence_summary: string;      // 근거/요약
    log_report: {
      trace_id: string;
      events: Array<{
        event_type: string;        // D2 EventTypeRegistry 값
        stage?: string;
      }>;
      approvals?: Array<{
        approval_id: string;
        status: string;
      }>;
    };
  };
  trace_id: string;
}
```

**`vamos:workflow:failure_report`** - 실패 리포트 조회

- 방향: invoke
- 소스 스키마: D5 FailureReportSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  workflow_id: string;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    failure_cause: string;        // "TOOL_TIMEOUT: Execute 단계에서 외부 도구 호출 시간 초과"
    evidence_gap: string;         // "도구 응답 부재로 근거 수집 불가"
    risk_detected: {
      non_goal_violation: boolean;
      policy_violation: boolean;
      notes: string;
    };
    improvement_hint: string;     // "재시도 1회 후 fallback/deny"
  };
  trace_id: string;
}
```

**`vamos:workflow:stage_event`** - 단계 전환 이벤트

- 방향: event (Rust -> React)
- 페이로드:

```typescript
{
  event_type: "wf.stage.enter" | "wf.stage.exit";
  workflow_id: string;
  trace_id: string;
  stage_id: "intake" | "plan" | "execute" | "verify" | "deliver";
  sub_stages?: string[];           // deliver 내부: ["memory", "reflection"]
  timestamp: string;
}
```

#### 2.1.3 Session 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:session:create` | invoke | 새 세션 생성 |
| `vamos:session:get` | invoke | 세션 정보 조회 |
| `vamos:session:list` | invoke | 세션 목록 조회 |
| `vamos:session:close` | invoke | 세션 종료 |

**`vamos:session:create`** - 세션 생성

- 방향: invoke
- 요청 payload:

```typescript
{
  trace_id: string;
  project_id: string;
  user_id?: string;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    session_id: string;
    project_id: string;
    created_at: string;          // ISO8601
  };
  trace_id: string;
}
```

---

### 2.2 Agent Commands (Node / Pipeline)

#### 2.2.1 Node 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:node:dispatch` | invoke | Blue Node에 작업 전달 |
| `vamos:node:response` | event | Blue Node 실행 결과 이벤트 |
| `vamos:node:profile` | invoke | Node Capability Profile 조회 |
| `vamos:node:list` | invoke | 등록된 Node 목록 조회 |
| `vamos:node:register` | invoke | 새 Node 등록 |

**`vamos:node:dispatch`** - Blue Node에 작업 전달

- 방향: invoke
- 소스 스키마: D3 NodeRequestEnvelopeSchema (v2.2.0)
- 요청 payload:

```typescript
{
  // 필수 7개 필드 (D3 AC-D3-004)
  request_id: string;
  project_id: string;
  session_id: string;
  node_id: string;                // 대상 Blue Node ID
  intent_summary: string;         // 의도 요약
  constraints: object;            // 제약 조건
  trace_id: string;
  // 선택 필드
  policy_snapshot_id?: string;
  budget_snapshot_id?: string;
  evidence_refs?: string[];
  decision_id?: string;           // D2 Decision 연결 (D3 §6.0)
  ui_hints?: object;
}
```

- 응답 (즉시): 작업 수락 확인

```typescript
{
  success: true;
  data: {
    request_id: string;
    node_id: string;
    status: "accepted" | "queued";
  };
  trace_id: string;
}
```

**`vamos:node:response`** - Blue Node 실행 결과

- 방향: event (Rust -> React)
- 소스 스키마: D3 NodeResponseEnvelopeSchema (v2.2.0)
- 페이로드:

```typescript
{
  trace_id: string;
  node_id: string;
  domain: string;                  // "research" 등
  inputs: {
    summary: string;
  };
  outputs: {
    result: string;
    evidence_refs: string[];
  };
  status: "success" | "fail";
}
```

**`vamos:node:profile`** - Node Capability Profile 조회

- 방향: invoke
- 소스 스키마: D3 NodeCapabilityProfileSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  node_id: string;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    node_id: string;
    required_tools: string[];       // D4 ToolRegistry 참조
    optional_tools?: string[];
    risk_class: "low" | "med" | "high";
    cost_class: "v0" | "v1" | "v2" | "v3";
    gates_required: Array<"policy" | "cost" | "approval" | "evidence" | "self_check">;
  };
  trace_id: string;
}
```

**`vamos:node:list`** - Node 목록 조회

- 방향: invoke
- 소스 스키마: D3 NodeRegistry
- 요청 payload:

```typescript
{
  trace_id: string;
  filter?: {
    domain?: string;
  };
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    items: Array<{
      node_id: string;
      domain: string;
      capabilities?: object;
      constraints?: object;
    }>;
    total: number;
  };
  trace_id: string;
}
```

#### 2.2.2 Pipeline / Gate 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:pipeline:gate_status` | invoke | 파이프라인 Gate 상태 조회 |
| `vamos:pipeline:gate_mapping` | invoke | Gate-Pipeline 매핑 조회/수정 |
| `vamos:pipeline:verify_chain` | invoke | Verify Chain 상태 조회 |
| `vamos:pipeline:circuit_breaker` | invoke | Circuit Breaker 상태 조회/제어 |
| `vamos:pipeline:hitl_respond` | invoke | HITL 요청에 응답 |
| `vamos:pipeline:hitl_event` | event | HITL 요청 알림 이벤트 |

**`vamos:pipeline:gate_mapping`** - Gate-Pipeline 매핑 조회

- 방향: invoke
- 소스 스키마: D5 GatePipelineMappingSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  stage_id?: "intake" | "plan" | "execute" | "verify" | "deliver";
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    items: Array<{
      mapping_id: string;
      stage_id: "intake" | "plan" | "execute" | "verify" | "deliver";
      gate_type: "policy" | "cost" | "approval" | "evidence" | "self_check";
      required: boolean;
      order: number;
      on_fail: "deny" | "downshift" | "retry" | "approval_required";
    }>;
  };
  trace_id: string;
}
```

**`vamos:pipeline:circuit_breaker`** - Circuit Breaker 상태

- 방향: invoke
- 소스 스키마: D5 CircuitBreakerSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  target_id: string;             // 대상 도구/에이전트/API ID
  action?: "get" | "reset";      // 조회 또는 리셋
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    target_id: string;
    failure_threshold: number;     // 차단 기준 횟수 (예: 3)
    recovery_time_sec: number;     // 복구 대기 (초)
    half_open_requests: number;
    state: "closed" | "open" | "half_open";
    last_failure_at?: string;      // ISO8601
    consecutive_failures?: number;
  };
  trace_id: string;
}
```

**`vamos:pipeline:hitl_respond`** - HITL 요청에 응답

- 방향: invoke
- 소스 스키마: D5 HITLRequestSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  hitl_id: string;
  response: "approve" | "deny" | "modify";
  modification?: object;         // response="modify"인 경우
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    hitl_id: string;
    workflow_trace_id: string;
    stage_id: string;
    response: string;
    processed_at: string;
  };
  trace_id: string;
}
```

**`vamos:pipeline:hitl_event`** - HITL 요청 알림 이벤트

- 방향: event (Rust -> React)
- 소스 스키마: D5 HITLRequestSchema (v2.3.0)
- 페이로드:

```typescript
{
  hitl_id: string;
  workflow_trace_id: string;
  stage_id: string;
  reason: string;
  autonomy_level: "L0" | "L1" | "L2" | "L3";
  options: string[];              // ["approve", "deny", "modify"]
  timeout_sec?: number;
}
```

#### 2.2.3 Agent Marketplace 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:marketplace:list` | invoke | 마켓플레이스 에이전트 목록 |
| `vamos:marketplace:get` | invoke | 에이전트 상세 조회 |
| `vamos:marketplace:install` | invoke | 에이전트 설치 |
| `vamos:marketplace:uninstall` | invoke | 에이전트 제거 |

**`vamos:marketplace:list`** - 에이전트 목록

- 방향: invoke
- 소스 스키마: D5 AgentMarketplaceSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  filter?: {
    provider?: "official" | "community" | "custom";
    risk_class?: "low" | "med" | "high";
    verified?: boolean;
    a2a_compatible?: boolean;
  };
  pagination?: { offset: number; limit: number; };
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    items: Array<{
      agent_id: string;
      name: string;
      version: string;
      provider: "official" | "community" | "custom";
      capabilities: string[];
      risk_class: "low" | "med" | "high";
      verified: boolean;
      sandbox_required: boolean;
      a2a_compatible?: boolean;
    }>;
    total: number;
  };
  trace_id: string;
}
```

---

### 2.3 Storage Commands (Memory / Vector / Cache)

#### 2.3.1 Memory 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:memory:save` | invoke | 메모리 레코드 저장 |
| `vamos:memory:get` | invoke | 메모리 레코드 조회 |
| `vamos:memory:search` | invoke | 메모리 검색 (텍스트/태그) |
| `vamos:memory:delete` | invoke | 메모리 레코드 삭제 |
| `vamos:memory:list` | invoke | 메모리 레코드 목록 |
| `vamos:memory:update_event` | event | 메모리 변경 이벤트 |

**`vamos:memory:save`** - 메모리 레코드 저장

- 방향: invoke
- 소스 스키마: D6 MemoryRecordSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  project_id: string;
  scope: "L0" | "L1" | "L2" | "L3";
  memory_type: "B-1" | "B-2" | "B-3" | "B-4";
  content_summary: string;
  policy_decision: "allow" | "restrict" | "deny";  // D7 PolicyCheck 결과
  // 선택 필드
  ttl?: string;                    // "90d" 등. 기본: L0=session_end, L1=90d, L2=indefinite, L3=policy_based
  tags?: string[];
  source_refs?: string[];
  masked?: boolean;
  activation_state?: "draft" | "approved" | "active" | "deprecated";
  version?: string;
  // L3/B-2 확장 필드
  procedure_id?: string;
  target_scope?: "global" | "project";
  trigger_conditions?: string;
  steps?: string[];
  required_tools?: string[];
  safety_notes?: string;
  provenance?: {
    created_by: string;
    source_refs?: string[];
  };
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    record_id: string;
    project_id: string;
    scope: string;
    created_at: string;            // ISO8601
  };
  trace_id: string;
}
```

**`vamos:memory:search`** - 메모리 검색

- 방향: invoke
- 요청 payload:

```typescript
{
  trace_id: string;
  project_id: string;
  query?: string;                  // 텍스트 검색
  filter?: {
    scope?: "L0" | "L1" | "L2" | "L3";
    memory_type?: "B-1" | "B-2" | "B-3" | "B-4";
    tags?: string[];
    activation_state?: "draft" | "approved" | "active" | "deprecated";
  };
  pagination?: { offset: number; limit: number; };
}
```

- 응답: `{ items: MemoryRecordSchema[], total: number }`

**`vamos:memory:update_event`** - 메모리 변경 이벤트

- 방향: event
- 페이로드:

```typescript
{
  event_type: "mem.reference.updated" | "mem.kb.derived";
  record_id: string;
  project_id: string;
  trace_id: string;
}
```

#### 2.3.2 Vector Store 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:vector:search` | invoke | 벡터 유사도 검색 |
| `vamos:vector:upsert` | invoke | 벡터 삽입/업데이트 |
| `vamos:vector:delete` | invoke | 벡터 삭제 |
| `vamos:vector:adapter_config` | invoke | Vector Store 어댑터 설정 조회 |

**`vamos:vector:search`** - 벡터 유사도 검색

- 방향: invoke
- 소스 스키마: D6 VectorStoreAdapterSchema (v2.3.0), KBEmbeddingRecordSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  query_text: string;
  collection_name?: string;        // 기본: "vamos_default"
  top_k?: number;                  // 기본: 5
  filter?: {
    project_id?: string;
    scope?: string;
  };
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    results: Array<{
      record_id: string;
      content_summary: string;
      score: number;               // 유사도 점수
      embedding_model: string;     // "bge-m3" | "text-embedding-3-small" 등
      chunk_id?: string;
      source_doc_ref?: string;
    }>;
  };
  trace_id: string;
}
```

**`vamos:vector:adapter_config`** - 어댑터 설정 조회

- 방향: invoke
- 소스 스키마: D6 VectorStoreAdapterSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  adapter_id?: string;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    adapter_id: string;
    backend: "chroma" | "qdrant" | "pgvector";
    mode: "embedded" | "server" | "cloud";
    embedding_model: string;
    dimension: number;
    collection_name: string;
    connection_url?: string;
    version_tier: "V1" | "V2" | "V3";
  };
  trace_id: string;
}
```

#### 2.3.3 Semantic Cache 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:cache:semantic_lookup` | invoke | 시맨틱 캐시 조회 |
| `vamos:cache:semantic_save` | invoke | 시맨틱 캐시 저장 |
| `vamos:cache:prompt_lookup` | invoke | 프롬프트 캐시 조회 |
| `vamos:cache:invalidate` | invoke | 캐시 무효화 |

**`vamos:cache:semantic_lookup`** - 시맨틱 캐시 조회

- 방향: invoke
- 소스 스키마: D6 SemanticCacheSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  query_text: string;
  similarity_threshold?: number;   // 기본: 0.95 (LOCK)
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    hit: boolean;
    cache_id?: string;
    response_text?: string;
    hit_count?: number;
    similarity_score?: number;
  };
  trace_id: string;
}
```

**`vamos:cache:prompt_lookup`** - 프롬프트 캐시 조회

- 방향: invoke
- 소스 스키마: D4 PromptCacheManagerSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  prompt_hash: string;            // "sha256:abc123..."
  model_id: string;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    hit: boolean;
    cache_id?: string;
    cached_response?: string;
    hit_count?: number;
    cost_saved_estimate?: number;  // USD
    ttl_sec?: number;
  };
  trace_id: string;
}
```

#### 2.3.4 GraphRAG 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:graphrag:query` | invoke | GraphRAG 질의 (엔티티-관계 순회) |
| `vamos:graphrag:config` | invoke | GraphRAG 설정 조회/수정 |

**`vamos:graphrag:query`** - GraphRAG 질의

- 방향: invoke
- 소스 스키마: D6 GraphRAGConfigSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  query_text: string;
  config_id?: string;              // 기본: 현재 활성 설정
  max_hops?: number;               // 기본: 2
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    entities: Array<{ id: string; label: string; properties: object; }>;
    relationships: Array<{ source: string; target: string; type: string; }>;
    context_text: string;          // 순회 결과 컨텍스트
    graph_backend: "json_file" | "neo4j";
  };
  trace_id: string;
}
```

#### 2.3.5 QoD (Quality of Data) 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:qod:get` | invoke | 소스 QoD 점수 조회 |
| `vamos:qod:compute` | invoke | QoD 점수 재계산 요청 |

**`vamos:qod:get`** - QoD 점수 조회

- 방향: invoke
- 소스 스키마: D6 SourceQoDSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  source_id: string;
  project_id: string;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    source_id: string;
    project_id: string;
    scope?: "L0" | "L1" | "L2" | "L3";
    qod_score: number;            // 0.0~1.0
    freshness: number;            // 0.0~1.0
    reliability: number;          // 0.0~1.0
    completeness: number;         // 0.0~1.0
    computed_at: string;          // ISO8601
  };
  trace_id: string;
}
```

---

### 2.4 Safety Commands (Policy / Cost / Approval / Guardrails)

#### 2.4.1 Policy 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:policy:check` | invoke | 정책 체크 실행 |
| `vamos:policy:result` | invoke | 정책 체크 결과 조회 |
| `vamos:policy:block_event` | event | 정책 차단 이벤트 |

**`vamos:policy:check`** - 정책 체크

- 방향: invoke
- 소스 스키마: D7 PolicyCheckSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  content: string;                 // 체크 대상 콘텐츠
  context?: {
    stage_id?: string;
    node_id?: string;
  };
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    check_id: string;
    decision: "deny" | "restrict" | "allow";
    reasons: string[];
    rule_refs: string[];
    detected_sensitive_types: Array<"PII" | "AUTH" | "MEDICAL" | "LEGAL">;
    fallback_id?: string;          // D2 FallbackRegistry 참조
    required_approval_id?: string; // D7 ApprovalSchema 참조
  };
  trace_id: string;
}
```

#### 2.4.2 Cost 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:cost:budget_get` | invoke | 비용 예산 조회 |
| `vamos:cost:budget_update` | invoke | 비용 사용량 업데이트 |
| `vamos:cost:downshift_status` | invoke | 다운시프트 상태 조회 |
| `vamos:cost:downshift_event` | event | 다운시프트 트리거 이벤트 |

**`vamos:cost:budget_get`** - 비용 예산 조회

- 방향: invoke
- 소스 스키마: D7 CostBudgetSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  budget_id?: string;             // 미지정 시 현재 활성 예산
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    budget_id: string;
    mode: "V1" | "V2" | "V3";
    daily_limit: number;           // 원. V1=1300, V2=3100, V3=8900
    monthly_limit: number;         // 원. V1=40000, V2=93000, V3=266000
    used_today: number;
    used_month: number;
    forecast?: number;
    actual?: number;
    block_on_exceed?: boolean;
  };
  trace_id: string;
}
```

**`vamos:cost:downshift_status`** - 다운시프트 상태

- 방향: invoke
- 소스 스키마: D7 DownshiftSchema (v2.2.0)
- 요청 payload: `{ trace_id: string; }`
- 응답:

```typescript
{
  success: true;
  data: {
    warn_threshold_percent: 80;     // LOCK
    block_threshold_percent: 100;   // LOCK
    trigger_type: "daily" | "monthly";
    near_action: "warn" | "force_mini";
    exceed_action: "block";
    main_requires_approval: boolean;
    current_usage_percent: number;  // 계산된 현재 사용률
  };
  trace_id: string;
}
```

**`vamos:cost:downshift_event`** - 다운시프트 트리거 이벤트

- 방향: event (Rust -> React)
- 페이로드:

```typescript
{
  event_type: "oc.i5.cost.downshifted";
  trigger_type: "daily" | "monthly";
  current_usage_percent: number;
  action_taken: "warn" | "force_mini" | "block";
  trace_id: string;
}
```

#### 2.4.3 Approval 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:approval:request` | invoke | 승인 요청 생성 |
| `vamos:approval:decide` | invoke | 승인/거부 결정 |
| `vamos:approval:get` | invoke | 승인 상태 조회 |
| `vamos:approval:list` | invoke | 미결 승인 목록 조회 |
| `vamos:approval:request_event` | event | 승인 요청 알림 |

**`vamos:approval:request`** - 승인 요청

- 방향: invoke
- 소스 스키마: D7 ApprovalSchema (v2.2.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  approval_stage: "plan" | "execute";
  requester: string;
  scope: "domain" | "cost" | "policy" | "external_action" | "storage";
  description: string;
  expires_at: string;              // ISO8601
  risk_level?: "P0" | "P1" | "P2";
  cost_snapshot?: object;
  policy_snapshot?: object;
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    approval_id: string;
    approval_stage: string;
    status: "approved" | "denied"; // 생성 직후에는 미결 상태
    audit_trace_id: string;
  };
  trace_id: string;
}
```

**`vamos:approval:decide`** - 승인/거부 결정

- 방향: invoke
- 요청 payload:

```typescript
{
  trace_id: string;
  approval_id: string;
  decision: "approved" | "denied";
  decided_by: string;              // 결정 주체 (user_id)
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    approval_id: string;
    status: "approved" | "denied";
    decided_by: string;
    decided_at: string;
  };
  trace_id: string;
}
```

#### 2.4.4 Guardrails 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:guardrails:check` | invoke | 3-Layer Guardrails 검사 실행 |
| `vamos:guardrails:result` | invoke | 검사 결과 조회 |
| `vamos:guardrails:block_event` | event | Guardrails 차단 이벤트 |

**`vamos:guardrails:check`** - 3-Layer 검사

- 방향: invoke
- 소스 스키마: D7 GuardrailsCheckSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  input_text?: string;             // L1 NeMo 입력 레일 대상
  output_text?: string;            // L2 Guardrails AI 출력 검증 대상
  check_layers?: Array<"layer1" | "layer2" | "layer3">;  // 기본: 전체
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    check_id: string;
    trace_id: string;
    layer1_nemo: {
      passed: boolean;
      rail_triggered: string[];
    };
    layer2_guardrails_ai: {
      passed: boolean;
      validators_failed: string[];
    };
    layer3_llamaguard: {
      passed: boolean;
      category: string;           // "safe" | 카테고리명
      confidence: number;
    };
    overall_decision: "allow" | "restrict" | "deny";
    blocked_by?: "layer1" | "layer2" | "layer3";
  };
  trace_id: string;
}
```

#### 2.4.5 RBAC / Autonomy 관련

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:rbac:get_role` | invoke | 현재 사용자 역할 조회 |
| `vamos:rbac:check_permission` | invoke | 권한 확인 |
| `vamos:autonomy:get_level` | invoke | 현재 자율 수준 조회 |
| `vamos:autonomy:set_level` | invoke | 자율 수준 변경 |

**`vamos:rbac:get_role`** - 역할 조회

- 방향: invoke
- 소스 스키마: D7 RBACRoleSchema (v2.3.0)
- 요청 payload: `{ trace_id: string; user_id?: string; }`
- 응답:

```typescript
{
  success: true;
  data: {
    role: "OWNER" | "ADMIN" | "OPERATOR" | "VIEWER";
    permissions: string[];
    max_autonomy_level: "L0" | "L1" | "L2" | "L3";
    cost_approval_limit?: number;
    p2_access: boolean;
  };
  trace_id: string;
}
```

**`vamos:autonomy:set_level`** - 자율 수준 변경

- 방향: invoke
- 소스 스키마: D7 AutonomyLevelSchema (v2.3.0)
- 요청 payload:

```typescript
{
  trace_id: string;
  level: "L0" | "L1" | "L2" | "L3";
}
```

- 응답:

```typescript
{
  success: true;
  data: {
    level: "L0" | "L1" | "L2" | "L3";
    name: string;                  // "수동" | "제안 모드" | "자율+알림" | "완전자율"
    auto_execute: boolean;
    notification_required: boolean;
    approval_required: boolean;
    allowed_domains?: string[];
  };
  trace_id: string;
}
```

---

### 2.5 UI Commands (Event / Config / Theme)

> D8은 SOT 스키마를 소유하지 않으며 (DN-005 B), 문서형 계약으로 UI 이벤트를 정의한다.

| Command | 방향 | 설명 |
|---------|------|------|
| `vamos:ui:log_stream` | event | UI 로그 스트림 (LogEventSchema 기반) |
| `vamos:ui:config_get` | invoke | UI 설정 조회 |
| `vamos:ui:config_set` | invoke | UI 설정 변경 |
| `vamos:ui:theme_set` | invoke | 테마 설정 |
| `vamos:ui:notification` | event | UI 알림 (안전/비용/승인) |

**`vamos:ui:log_stream`** - UI 로그 스트림

- 방향: event (Rust -> React)
- 소스 스키마: D2 LogEventSchema (v2.2.1)
- 페이로드:

```typescript
{
  event_type: string;              // D2 EventTypeRegistry 53개 값 중 하나
  producer: string;                // "I-1", "I-5" 등
  payload: {
    trace_id: string;
    decision_id?: string;
    [key: string]: any;
  };
  severity: "info" | "warn" | "error" | "critical";
  sinks?: string[];                // ["file", "db", "audit"]
  links?: {
    failure_code?: string[];
    fallback_id?: string[];
  };
}
```

**`vamos:ui:notification`** - UI 알림 이벤트

- 방향: event (Rust -> React)
- 페이로드:

```typescript
{
  notification_type: "guardrails_block" | "cost_warning" | "cost_block" | "approval_needed" | "hitl_request" | "circuit_breaker" | "cache_hit";
  priority: "P0" | "P1" | "P2";   // 08 §10.3 Alert Priority
  title: string;
  message: string;
  action_required: boolean;
  related_id?: string;             // 관련 check_id, approval_id 등
  trace_id: string;
}
```

---

## 3. Python <-> Rust Internal API

> V1에서 Python-Rust 통신은 JSON-RPC over subprocess (stdin/stdout) 방식을 사용한다.
> Rust가 Python 프로세스를 spawn하고, JSON-RPC 2.0 메시지를 stdin/stdout으로 교환한다.

### 3.0 JSON-RPC 공통 규격

**요청 (Rust -> Python)**:

```json
{
  "jsonrpc": "2.0",
  "method": "string",
  "params": {},
  "id": "string"
}
```

**성공 응답 (Python -> Rust)**:

```json
{
  "jsonrpc": "2.0",
  "result": {},
  "id": "string"
}
```

**에러 응답 (Python -> Rust)**:

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32000,
    "message": "string",
    "data": {
      "failure_code": "string",
      "trace_id": "string"
    }
  },
  "id": "string"
}
```

---

### 3.1 LangGraph StateGraph 호출 인터페이스

> Agent Framework: LangGraph (LOCK). StateGraph 패턴 기반.
> 5단계 파이프라인: Intake -> Plan -> Execute -> Verify -> Deliver

#### 3.1.1 워크플로우 실행

**method**: `langgraph.workflow.run`

- params:

```json
{
  "trace_id": "string",
  "project_id": "string",
  "session_id": "string",
  "user_input": "string",
  "autonomy_level": "L0|L1|L2|L3",
  "decision_id": "string (optional)",
  "constraints": {}
}
```

- result: D5 WorkflowOutputEnvelopeSchema

```json
{
  "user_response": "string",
  "evidence_summary": "string",
  "log_report": {
    "trace_id": "string",
    "events": [],
    "approvals": []
  }
}
```

#### 3.1.2 단계별 실행 (Step-by-step)

**method**: `langgraph.stage.execute`

- params:

```json
{
  "trace_id": "string",
  "workflow_id": "string",
  "stage_id": "intake|plan|execute|verify|deliver",
  "state": {}
}
```

- result:

```json
{
  "stage_id": "string",
  "status": "completed|failed|pending_approval",
  "state": {},
  "next_stage": "string|null",
  "events": []
}
```

#### 3.1.3 Decision Kernel 호출

**method**: `langgraph.decision.create`

- params:

```json
{
  "trace_id": "string",
  "intent_frame_ref": "string",
  "evidence_pack_ref": "string",
  "output_spec": { "format_constraints": "markdown" }
}
```

- result: D2 DecisionSchema 전체 필드

#### 3.1.4 Node Dispatch (Blue Node 실행)

**method**: `langgraph.node.dispatch`

- params: D3 NodeRequestEnvelopeSchema 전체 필드

```json
{
  "request_id": "string",
  "project_id": "string",
  "session_id": "string",
  "node_id": "string",
  "intent_summary": "string",
  "constraints": {},
  "trace_id": "string",
  "policy_snapshot_id": "string (optional)",
  "budget_snapshot_id": "string (optional)",
  "evidence_refs": [],
  "decision_id": "string (optional)",
  "ui_hints": {}
}
```

- result: D3 NodeResponseEnvelopeSchema

```json
{
  "trace_id": "string",
  "node_id": "string",
  "domain": "string",
  "inputs": { "summary": "string" },
  "outputs": { "result": "string", "evidence_refs": [] },
  "status": "success|fail"
}
```

#### 3.1.5 Verify Chain 실행

**method**: `langgraph.verify.run_chain`

- params:

```json
{
  "trace_id": "string",
  "evx_ids": ["EVX-1", "EVX-2"],
  "decision_id": "string",
  "workflow_state": {}
}
```

- result: D5 VerifyChainEntrySchema 배열

```json
{
  "entries": [
    {
      "evx_id": "EVX-1",
      "purpose": "Code-as-Policy",
      "placement": ["Plan", "Verify"],
      "decision_record": "verify.chain_used += [EVX-1]",
      "block_conditions": ["Policy deny"]
    }
  ],
  "overall_passed": true
}
```

---

### 3.2 Embedding API

#### 3.2.1 BGE-M3 로컬 임베딩 (V1 기본)

**method**: `embedding.encode`

- params:

```json
{
  "trace_id": "string",
  "texts": ["string"],
  "model": "bge-m3",
  "dimension": 1024,
  "matryoshka_dim": 256
}
```

- result:

```json
{
  "embeddings": [[0.1, 0.2, ...]],
  "model": "bge-m3",
  "dimension": 1024,
  "token_count": 128
}
```

#### 3.2.2 OpenAI Cloud 임베딩 (V2+)

**method**: `embedding.encode`

- params:

```json
{
  "trace_id": "string",
  "texts": ["string"],
  "model": "text-embedding-3-small",
  "dimension": 1536
}
```

- result:

```json
{
  "embeddings": [[0.1, 0.2, ...]],
  "model": "text-embedding-3-small",
  "dimension": 1536,
  "token_count": 128,
  "cost_estimate": { "tokens": 128, "usd": 0.0000026 }
}
```

#### 3.2.3 벡터 저장

**method**: `embedding.store`

- params: D6 KBEmbeddingRecordSchema 확장 필드 포함

```json
{
  "trace_id": "string",
  "record_id": "string",
  "collection_name": "vamos_default",
  "embedding": [0.1, 0.2, ...],
  "metadata": {
    "project_id": "string",
    "scope": "L1",
    "memory_type": "B-3",
    "content_summary": "string",
    "chunk_id": "string",
    "chunk_token_count": 512,
    "source_doc_ref": "string",
    "embedding_model": "bge-m3",
    "vector_dim": 1024
  }
}
```

- result:

```json
{
  "stored": true,
  "record_id": "string",
  "collection_name": "string"
}
```

---

### 3.3 LLM API Adapter

> 모든 LLM 호출은 ToolRegistry 경유 (D4 AC-D4-006). 직접 HTTP 호출 금지.

#### 3.3.1 LLM 텍스트 생성

**method**: `llm.generate`

- params:

```json
{
  "trace_id": "string",
  "model_id": "string",
  "prompt": "string",
  "system_prompt": "string (optional)",
  "max_tokens": 4096,
  "temperature": 0.7,
  "tool_id": "llm_openai_text"
}
```

- result: D4 BrainAdapterResponseSchema (v2.2.0)

```json
{
  "output_text": "string",
  "evidence_summary": "string",
  "cost_used_estimate": {
    "input_tokens": 500,
    "output_tokens": 200,
    "total_tokens": 700
  },
  "warnings": [],
  "trace_id": "string",
  "tool_calls": [],
  "qod_hint": {}
}
```

#### 3.3.2 Infra 호출 결과 기록

**method**: `llm.record_invoke`

- params/result: D4 InfraInvokeResultSchema (v2.2.0)

```json
{
  "model_id": "llm_openai_text",
  "trace_id": "string",
  "policy_decision": {
    "decision": "allow",
    "reason_code": "REF:07/PolicyCheck"
  },
  "cost_summary": {
    "tokens": "700",
    "cost": "tbd",
    "latency": "1200ms"
  },
  "summary_text": "요약 텍스트",
  "evidence_refs": []
}
```

#### 3.3.3 Rate Limit 조회

**method**: `llm.rate_limit.get`

- params:

```json
{
  "trace_id": "string",
  "target_id": "string",
  "target_type": "llm|tool|api|embedding"
}
```

- result: D4 RateLimitConfigSchema (v2.3.0)

```json
{
  "target_id": "openai_gpt4o",
  "target_type": "llm",
  "rpm": 60,
  "rpd": 10000,
  "tpm": 150000,
  "burst_allowance": 10,
  "on_exceed": "queue|deny|downshift"
}
```

---

## 4. MCP Tool Protocol

> MCP 전송: Streamable HTTP only (DEC-017 LOCK, stdio 제거).
> 모든 도구 호출은 D4 ToolRegistry 경유 (AC-D4-006).

### 4.1 MCP Bridge 호출 규격

#### 4.1.1 Bridge 설정

- 소스 스키마: D3 MCPBridgeLayerSchema (v2.3.0)

```json
{
  "bridge_id": "mcp_bridge_research",
  "node_id": "bn_web_research",
  "transport": "streamable_http",
  "base_url": "http://localhost:3001",
  "discovered_tools": ["web_search", "browser_render"],
  "auth_config": {
    "type": "bearer",
    "token_env": "MCP_TOKEN"
  },
  "health_check_interval_sec": 30
}
```

#### 4.1.2 Bridge 초기화 API

**method**: `mcp.bridge.init`

- params:

```json
{
  "trace_id": "string",
  "bridge_id": "string",
  "base_url": "string",
  "auth_config": {
    "type": "bearer|api_key",
    "token_env": "string"
  }
}
```

- result:

```json
{
  "bridge_id": "string",
  "status": "connected",
  "discovered_tools": ["string"],
  "transport": "streamable_http"
}
```

#### 4.1.3 Bridge Health Check

**method**: `mcp.bridge.health`

- params: `{ "trace_id": "string", "bridge_id": "string" }`
- result: `{ "bridge_id": "string", "status": "healthy|unhealthy", "latency_ms": 50 }`

---

### 4.2 Tool Discovery / Invocation

#### 4.2.1 Tool Discovery (도구 발견)

**method**: `mcp.tools.discover`

- params:

```json
{
  "trace_id": "string",
  "bridge_id": "string"
}
```

- result: D3 ToolCallRegistrySchema 기반

```json
{
  "tools": [
    {
      "tool_id": "tool.web_search",
      "node_id": "bn_web_research",
      "risk_class": "med",
      "auth_method": "api_key",
      "mcp_endpoint": "http://localhost:3001/mcp",
      "rate_limit": { "rpm": 60, "daily": 1000 },
      "enabled": true
    }
  ]
}
```

#### 4.2.2 Tool Invocation (도구 호출)

**MCP Streamable HTTP 요청**:

```
POST {base_url}/mcp
Content-Type: application/json
Authorization: Bearer {token}
```

요청 body:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "web_search",
    "arguments": {
      "query": "search query text",
      "max_results": 10
    }
  },
  "id": "call_001"
}
```

응답 body:

```json
{
  "jsonrpc": "2.0",
  "result": {
    "content": [
      {
        "type": "text",
        "text": "검색 결과..."
      }
    ],
    "isError": false
  },
  "id": "call_001"
}
```

#### 4.2.3 Tool Registry 조회 (내부)

**method**: `mcp.tool_registry.get`

- params:

```json
{
  "trace_id": "string",
  "tool_id": "string"
}
```

- result: D4 ToolRegistryEntrySchema (v2.2.0)

```json
{
  "tool_id": "tool_playwright",
  "category": "browser.render",
  "adapter_id": "tool_playwright",
  "risk_class": "high",
  "cost_class": "v2",
  "required_gates": ["policy", "cost", "approval"],
  "outputs": ["artifact", "log"],
  "notes": "high-risk, approval required"
}
```

#### 4.2.4 Tool Registry 목록 조회

**method**: `mcp.tool_registry.list`

- params:

```json
{
  "trace_id": "string",
  "filter": {
    "category": "llm.text|llm.vision|llm.embedding|browser.render|api.http|code.exec|data.vector|data.graph|mcp.tool",
    "risk_class": "low|med|high",
    "enabled": true
  }
}
```

- result: `{ "tools": ToolRegistryEntrySchema[] }`

---

## 5. 전체 엔드포인트 요약 표

### 5.1 Tauri IPC Commands (총 72개)

| # | Command | 방향 | 카테고리 | 소스 스키마 |
|---|---------|------|---------|------------|
| 1 | `vamos:decision:create` | invoke | Core | D2 DecisionSchema |
| 2 | `vamos:decision:get` | invoke | Core | D2 DecisionSchema |
| 3 | `vamos:decision:list` | invoke | Core | D2 DecisionSchema |
| 4 | `vamos:decision:lock` | invoke | Core | D2 DecisionSchema |
| 5 | `vamos:decision:event` | event | Core | D2 LogEventSchema |
| 6 | `vamos:workflow:start` | invoke | Core | D5 WorkflowStageSchema |
| 7 | `vamos:workflow:status` | invoke | Core | D5 WorkflowStageSchema |
| 8 | `vamos:workflow:cancel` | invoke | Core | D5 WorkflowStageSchema |
| 9 | `vamos:workflow:output` | invoke | Core | D5 WorkflowOutputEnvelopeSchema |
| 10 | `vamos:workflow:stage_event` | event | Core | D5 WorkflowStageSchema |
| 11 | `vamos:workflow:failure_report` | invoke | Core | D5 FailureReportSchema |
| 12 | `vamos:session:create` | invoke | Core | - |
| 13 | `vamos:session:get` | invoke | Core | - |
| 14 | `vamos:session:list` | invoke | Core | - |
| 15 | `vamos:session:close` | invoke | Core | - |
| 16 | `vamos:node:dispatch` | invoke | Agent | D3 NodeRequestEnvelopeSchema |
| 17 | `vamos:node:response` | event | Agent | D3 NodeResponseEnvelopeSchema |
| 18 | `vamos:node:profile` | invoke | Agent | D3 NodeCapabilityProfileSchema |
| 19 | `vamos:node:list` | invoke | Agent | D3 NodeRegistry |
| 20 | `vamos:node:register` | invoke | Agent | D3 NodeRegistry |
| 21 | `vamos:pipeline:gate_status` | invoke | Agent | D5 GatePipelineMappingSchema |
| 22 | `vamos:pipeline:gate_mapping` | invoke | Agent | D5 GatePipelineMappingSchema |
| 23 | `vamos:pipeline:verify_chain` | invoke | Agent | D5 VerifyChainEntrySchema |
| 24 | `vamos:pipeline:circuit_breaker` | invoke | Agent | D5 CircuitBreakerSchema |
| 25 | `vamos:pipeline:hitl_respond` | invoke | Agent | D5 HITLRequestSchema |
| 26 | `vamos:pipeline:hitl_event` | event | Agent | D5 HITLRequestSchema |
| 27 | `vamos:marketplace:list` | invoke | Agent | D5 AgentMarketplaceSchema |
| 28 | `vamos:marketplace:get` | invoke | Agent | D5 AgentMarketplaceSchema |
| 29 | `vamos:marketplace:install` | invoke | Agent | D5 AgentMarketplaceSchema |
| 30 | `vamos:marketplace:uninstall` | invoke | Agent | D5 AgentMarketplaceSchema |
| 31 | `vamos:memory:save` | invoke | Storage | D6 MemoryRecordSchema |
| 32 | `vamos:memory:get` | invoke | Storage | D6 MemoryRecordSchema |
| 33 | `vamos:memory:search` | invoke | Storage | D6 MemoryRecordSchema |
| 34 | `vamos:memory:delete` | invoke | Storage | D6 MemoryRecordSchema |
| 35 | `vamos:memory:list` | invoke | Storage | D6 MemoryRecordSchema |
| 36 | `vamos:memory:update_event` | event | Storage | D6 MemoryRecordSchema |
| 37 | `vamos:vector:search` | invoke | Storage | D6 VectorStoreAdapterSchema |
| 38 | `vamos:vector:upsert` | invoke | Storage | D6 VectorStoreAdapterSchema |
| 39 | `vamos:vector:delete` | invoke | Storage | D6 VectorStoreAdapterSchema |
| 40 | `vamos:vector:adapter_config` | invoke | Storage | D6 VectorStoreAdapterSchema |
| 41 | `vamos:cache:semantic_lookup` | invoke | Storage | D6 SemanticCacheSchema |
| 42 | `vamos:cache:semantic_save` | invoke | Storage | D6 SemanticCacheSchema |
| 43 | `vamos:cache:prompt_lookup` | invoke | Storage | D4 PromptCacheManagerSchema |
| 44 | `vamos:cache:invalidate` | invoke | Storage | D6 SemanticCacheSchema |
| 45 | `vamos:graphrag:query` | invoke | Storage | D6 GraphRAGConfigSchema |
| 46 | `vamos:graphrag:config` | invoke | Storage | D6 GraphRAGConfigSchema |
| 47 | `vamos:qod:get` | invoke | Storage | D6 SourceQoDSchema |
| 48 | `vamos:qod:compute` | invoke | Storage | D6 SourceQoDSchema |
| 49 | `vamos:policy:check` | invoke | Safety | D7 PolicyCheckSchema |
| 50 | `vamos:policy:result` | invoke | Safety | D7 PolicyCheckSchema |
| 51 | `vamos:policy:block_event` | event | Safety | D7 PolicyCheckSchema |
| 52 | `vamos:cost:budget_get` | invoke | Safety | D7 CostBudgetSchema |
| 53 | `vamos:cost:budget_update` | invoke | Safety | D7 CostBudgetSchema |
| 54 | `vamos:cost:downshift_status` | invoke | Safety | D7 DownshiftSchema |
| 55 | `vamos:cost:downshift_event` | event | Safety | D7 DownshiftSchema |
| 56 | `vamos:approval:request` | invoke | Safety | D7 ApprovalSchema |
| 57 | `vamos:approval:decide` | invoke | Safety | D7 ApprovalSchema |
| 58 | `vamos:approval:get` | invoke | Safety | D7 ApprovalSchema |
| 59 | `vamos:approval:list` | invoke | Safety | D7 ApprovalSchema |
| 60 | `vamos:approval:request_event` | event | Safety | D7 ApprovalSchema |
| 61 | `vamos:guardrails:check` | invoke | Safety | D7 GuardrailsCheckSchema |
| 62 | `vamos:guardrails:result` | invoke | Safety | D7 GuardrailsCheckSchema |
| 63 | `vamos:guardrails:block_event` | event | Safety | D7 GuardrailsCheckSchema |
| 64 | `vamos:rbac:get_role` | invoke | Safety | D7 RBACRoleSchema |
| 65 | `vamos:rbac:check_permission` | invoke | Safety | D7 RBACRoleSchema |
| 66 | `vamos:autonomy:get_level` | invoke | Safety | D7 AutonomyLevelSchema |
| 67 | `vamos:autonomy:set_level` | invoke | Safety | D7 AutonomyLevelSchema |
| 68 | `vamos:ui:log_stream` | event | UI | D2 LogEventSchema |
| 69 | `vamos:ui:config_get` | invoke | UI | D8 문서형 계약 |
| 70 | `vamos:ui:config_set` | invoke | UI | D8 문서형 계약 |
| 71 | `vamos:ui:theme_set` | invoke | UI | D8 문서형 계약 |
| 72 | `vamos:ui:notification` | event | UI | D8 문서형 계약 |

### 5.2 Python-Rust JSON-RPC Methods (총 13개)

| # | Method | 소스 스키마 |
|---|--------|------------|
| 1 | `langgraph.workflow.run` | D5 WorkflowOutputEnvelopeSchema |
| 2 | `langgraph.stage.execute` | D5 WorkflowStageSchema |
| 3 | `langgraph.decision.create` | D2 DecisionSchema |
| 4 | `langgraph.node.dispatch` | D3 NodeRequestEnvelopeSchema / NodeResponseEnvelopeSchema |
| 5 | `langgraph.verify.run_chain` | D5 VerifyChainEntrySchema |
| 6 | `embedding.encode` | D6 KBEmbeddingRecordSchema |
| 7 | `embedding.store` | D6 VectorStoreAdapterSchema |
| 8 | `llm.generate` | D4 BrainAdapterResponseSchema |
| 9 | `llm.record_invoke` | D4 InfraInvokeResultSchema |
| 10 | `llm.rate_limit.get` | D4 RateLimitConfigSchema |
| 11 | `mcp.bridge.init` | D3 MCPBridgeLayerSchema |
| 12 | `mcp.bridge.health` | D3 MCPBridgeLayerSchema |
| 13 | `mcp.tools.discover` | D3 ToolCallRegistrySchema |

### 5.3 MCP Tool Protocol (총 3개)

| # | Method | 프로토콜 | 설명 |
|---|--------|---------|------|
| 1 | `tools/call` | MCP Streamable HTTP | 도구 호출 (JSON-RPC 2.0) |
| 2 | `mcp.tool_registry.get` | 내부 | ToolRegistry 단건 조회 |
| 3 | `mcp.tool_registry.list` | 내부 | ToolRegistry 목록 조회 |

---

## 6. 에러 응답 규격 (D2 FailureCodeRegistry 연동)

### 6.1 표준 에러 응답 구조

모든 IPC/API 에러는 다음 구조를 따른다:

```typescript
{
  success: false;
  error: {
    code: string;                  // D2 FailureCodeRegistry 값
    message: string;               // 사람 읽기 가능한 메시지
    trace_id: string;              // 추적 ID
    fallback_id?: string;          // D2 FallbackRegistry 참조
    details?: object;              // 추가 컨텍스트
  };
}
```

### 6.2 FailureCode -> Fallback 매핑 (D2 정본)

| failure_code | 설명 | fallback_id | 사용자 메시지 예시 |
|--------------|------|-------------|-------------------|
| `OC_I1_PARSE_FAIL` | 의도 파싱 실패 | `FB_INTENT_HEURISTIC_PARSE` | "입력을 이해하지 못했습니다. 다시 시도합니다." |
| `OC_I1_AMBIGUOUS_UNRESOLVED` | 모호한 의도 미해소 | `FB_ASK_CLARIFICATION` | "명확한 요청을 위해 추가 정보가 필요합니다." |
| `OC_I2_RAG_NO_SOURCE` | RAG 소스 없음 | `FB_RAG_RETRY_EXPAND` | "관련 자료를 찾지 못했습니다. 검색 범위를 확장합니다." |
| `OC_I2_EVIDENCE_QOD_LOW` | 근거 품질 낮음 | `FB_RAG_RETRY_EXPAND` | "수집된 근거의 신뢰도가 낮습니다." |
| `OC_I2_SOURCE_POLICY_BLOCK` | 소스 정책 차단 | `FB_RAG_SWITCH_SOURCE` | "정책에 의해 해당 소스가 차단되었습니다." |
| `OC_I2_TIMEOUT` | 소스 조회 타임아웃 | `FB_RAG_SWITCH_SOURCE` | "자료 수집 시간이 초과되었습니다." |
| `OC_I3_MEMORY_POLICY_DENY` | 메모리 정책 거부 | `FB_MEMORY_META_ONLY` | "저장 정책에 의해 원문 저장이 거부되었습니다." |
| `OC_I3_APPROVAL_REQUIRED` | 메모리 승인 필요 | `FB_REQUIRE_APPROVAL` | "저장을 위해 사용자 승인이 필요합니다." |
| `OC_I3_COMMIT_FAIL` | 메모리 커밋 실패 | `FB_DENY_WITH_REASON` | "메모리 저장에 실패했습니다." |
| `OC_I4_OUTPUT_SPEC_VIOLATION` | 출력 스펙 위반 | `FB_OUTPUT_REFORMAT` | "출력 형식을 재조정합니다." |
| `OC_I4_CITATION_MISSING` | 인용 누락 | `FB_POLICY_MASK` | "인용 정보가 누락되었습니다." |
| `OC_I4_MASK_FAIL` | 마스킹 실패 | `FB_POLICY_MASK` | "민감 정보 마스킹에 실패했습니다." |
| `OC_I5_POLICY_BLOCK` | 정책 차단 | `FB_DENY_WITH_REASON` | "정책에 의해 실행이 차단되었습니다." |
| `OC_I5_APPROVAL_REQUIRED` | 실행 승인 필요 | `FB_REQUIRE_APPROVAL` | "실행을 위해 승인이 필요합니다." |
| `OC_I5_COST_OVER_BUDGET` | 비용 초과 | `FB_COST_DOWNSHIFT` | "비용 한도를 초과했습니다. 경량 모델로 전환합니다." |
| `OC_I5_EVIDENCE_INSUFFICIENT` | 근거 부족 | `FB_RAG_RETRY_EXPAND` | "충분한 근거를 확보하지 못했습니다." |
| `OC_I5_ROUTE_NOT_FOUND` | 라우팅 실패 | `FB_ROUTE_SAFE_NODE` | "적합한 실행 노드를 찾지 못했습니다." |
| `POLICY_DENY` | 범용 정책 거부 | `FB_DENY_WITH_REASON` | "정책 위반으로 요청이 거부되었습니다." |
| `GT_ERR_COST_LIMIT` | 비용 상한 에러 | `FB_COST_DOWNSHIFT` | "비용 상한에 도달했습니다." |
| `TOOL_TIMEOUT` | 도구 호출 타임아웃 | `FB_RAG_RETRY_EXPAND` | "외부 도구 호출 시간이 초과되었습니다." |

### 6.3 HTTP 상태 코드 매핑 (MCP/API용)

| 상태 코드 | 용도 |
|-----------|------|
| 200 | 성공 |
| 400 | 잘못된 요청 (파라미터 오류) |
| 401 | 인증 실패 |
| 403 | 권한 없음 (RBAC 차단) |
| 404 | 리소스 없음 |
| 409 | 충돌 (Decision 이미 잠금 등) |
| 429 | Rate Limit 초과 |
| 500 | 내부 서버 에러 |
| 503 | Circuit Breaker 차단 중 |

### 6.4 JSON-RPC 에러 코드 (Python-Rust용)

| 코드 | 의미 |
|------|------|
| -32700 | Parse error (잘못된 JSON) |
| -32600 | Invalid Request |
| -32601 | Method not found |
| -32602 | Invalid params |
| -32603 | Internal error |
| -32000 | VAMOS 비즈니스 에러 (data.failure_code로 상세 구분) |

---

## 7. 인증/권한 (RBAC 연동)

### 7.1 RBAC 역할 체계 (D7 RBACRoleSchema LOCK)

| 역할 | 권한 | 최대 자율 수준 | P2 접근 | 비용 승인 한도 |
|------|------|--------------|---------|-------------|
| **OWNER** | read, write, execute, approve, admin | L3 | O | 266,000원/월 |
| **ADMIN** | read, write, execute, approve | L2 | O | 93,000원/월 |
| **OPERATOR** | read, write, execute | L1 | X | 40,000원/월 |
| **VIEWER** | read | L0 | X | 0 |

### 7.2 자율 수준별 동작 (D7 AutonomyLevelSchema LOCK)

| 수준 | 이름 | 자동 실행 | 알림 필수 | 승인 필수 |
|------|------|----------|----------|----------|
| **L0** | 수동 | X | O | O |
| **L1** | 제안 모드 | X | O | O |
| **L2** | 자율+알림 | O | O | X |
| **L3** | 완전자율 | O | X (선택) | X |

### 7.3 IPC Command별 권한 요구사항

| 카테고리 | 최소 역할 | 비고 |
|---------|----------|------|
| Core (decision/workflow/session) | OPERATOR | 읽기는 VIEWER |
| Agent (node/pipeline) | OPERATOR | Node 등록은 ADMIN |
| Storage (memory/vector/cache) | OPERATOR | 삭제는 ADMIN |
| Safety (policy/cost) | VIEWER (조회) | 변경은 ADMIN |
| Safety (approval) | OPERATOR (요청) | 결정은 ADMIN/OWNER |
| Safety (guardrails) | VIEWER (조회) | 설정 변경은 ADMIN |
| Safety (autonomy) | ADMIN | L3 설정은 OWNER |
| UI | VIEWER | 모든 역할 |

### 7.4 인증 흐름

```
[React UI] --> vamos:rbac:get_role --> [Rust IPC Handler]
                                            |
                                    역할/권한 확인
                                            |
                                   +--------+--------+
                                   |                 |
                              [허용]             [거부]
                                   |                 |
                          Command 실행         에러 응답
                                              { code: "POLICY_DENY" }
```

### 7.5 API 키 / 토큰 관리

| 대상 | 인증 방식 | 저장 위치 | 비고 |
|------|----------|----------|------|
| OpenAI API | API Key | 환경변수 (OPENAI_API_KEY) | D3 ToolCallRegistrySchema.auth_method="api_key" |
| MCP Server | Bearer Token | 환경변수 (MCP_TOKEN) | D3 MCPBridgeLayerSchema.auth_config |
| OAuth2 연동 | OAuth2 | Secure Storage (Tauri) | V2+ 외부 서비스 연동 |
| 로컬 사용자 | Session Token | SQLite (V1) / Postgres (V2+) | Tauri 세션 관리 |

---

## 8. 문서 이력

| 버전 | 일자 | 변경 내용 |
|------|------|----------|
| 1.0.0 | 2026-02-22 | Phase B1 초판 작성. D2~D8 스키마 기반 API 엔드포인트 도출. Tauri IPC 72개, Python-Rust JSON-RPC 13개, MCP Tool 3개 정의. 에러 규격(D2 FailureCode 20개 연동), RBAC 권한 체계, 자율 수준(L0~L3) 매핑 포함. |

---

<\!-- END OF DOCUMENT -->
