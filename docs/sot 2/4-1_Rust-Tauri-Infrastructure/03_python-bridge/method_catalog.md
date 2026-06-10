# method_catalog.md — JSON-RPC 13 Method Catalog (LOCK-RT-03)

> **도메인**: 4-1_Rust-Tauri-Infrastructure (#14)
> **서브폴더**: 03_python-bridge
> **세션**: T1-3 (Phase 1)
> **작성일**: 2026-04-11
> **상태**: **APPROVED** (Phase 4 T3-1 L3 production 승급 완료 2026-06-03 — §5 `process_message` (langgraph.decision.create 1:1, 120s) 정본, T1-3 산출물 기반; content byte-EXACT 보존)
> **정본 소스**: Part2 §6.2.2 (13개 메서드명 LOCK) + 상세명세 §C (verb_noun 13개 참조 스키마) + T1-2 Serde 모델
> **LOCK**: LOCK-RT-03 (13개 메서드명), LOCK-RT-04 (핵심 모듈 4개), LOCK-RT-11/15 (프로토콜 — rpc_protocol.md 정본)

---

## §1. 교차 참조

### 1.1 직접 참조 문서

| 문서 | 섹션 | 본 파일에서의 역할 |
|---|---|---|
| `RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md` | §7 Phase 1 T1-3, §B.2 13 메서드 요약, §B.2 NOTE (PRE-3 매핑 갭 6건) | 본 파일 §2 PRE-3 해소 근거 |
| `RUST_TAURI_INFRASTRUCTURE_상세명세.md` | §B (25 Serde 모델), §C (13 verb_noun 스키마) | 본 파일 §3/§4 스키마 인용 + §7 Rust struct 매핑 |
| `AUTHORITY_CHAIN.md` | §2 LOCK-RT-03 메서드명 전수 | 본 파일 §3 13개 정본 출처 |
| `CONFLICT_LOG.md` | CFL-RT-002 RESOLVED (네이밍 컨벤션 차이) | 본 파일 §2 PRE-3 판정 근거 |
| `D2.1-D4_D4_SCHEMA_INFRA_CORE.md` | ToolRegistryEntry, BrainAdapterResponse, InfraInvokeResult, PromptCacheManager, RateLimitConfig | 본 파일 §3 `mcp.tools.discover`/`llm.rate_limit.get` 스키마 근거 |
| `PHASE_B2_PROJECT_STRUCTURE.md` | §4.3 python_manager.rs / ipc_protocol.rs 인터페이스 | 본 파일 §8 경계 |
| `VAMOS_구현가이드_PART2_구현단계.md` | §6.2.2 (line 4683~4696, 842~855, 897~910) — 13 메서드명 3회 나열 | 본 파일 §3 LOCK 원본 대조 |
| `_index.md` | `[PRE-3 완료 후 갱신]` 마커 (line 92~93) | 본 파일 §2 결과는 step 5 에서 _index.md 로 복사 대상 (본 step 에서 _index.md 미수정) |
| `rpc_protocol.md` (본 서브폴더) | §2.5 공통 자료구조 (RpcRequest/Response/Error/Meta) | 본 파일 §4 스키마 재사용 |
| T1-1 (`01_ipc-commands/`) | 72 IPC 커맨드 시그니처 | 본 파일 §8 IPC → JSON-RPC 흐름 |
| T1-2 (`02_serde-models/`) | core/memory/agent/workflow_event_config 25개 모델 | 본 파일 §7 params/result 매핑 |
| T1-4 (`05_process-management/`) | spawn/healthcheck/restart | 본 파일 §4 `_lifecycle` 메서드 협조 |

### 1.2 LOCK 범위

| LOCK ID | 본 파일 적용 |
|---|---|
| LOCK-RT-03 | §3 13 메서드명 = Part2 §6.2.2 정본 복제. 재정의 금지. |
| LOCK-RT-04 | §7 Rust struct 25개 참조 (T1-2). 신규 struct 선언 금지 — T1-2 의 파일에서 정의. |
| LOCK-RT-11 | §4 모든 req/resp 는 rpc_protocol.md §2~§3 프레이밍 규칙 준수. |
| LOCK-RT-12/13 | §6 타임아웃 매핑표 및 rpc_protocol.md §6 참조. |
| LOCK-RT-14 | §4 각 메서드 "가능한 error" 는 rpc_protocol.md §5.3 TauriError 매핑으로 해석. |
| LOCK-RT-15 | 본 파일은 프레이밍 세부 미중복 — rpc_protocol.md 단일 정본. |

---

## §2. PRE-3 해소 — Part2 §6.2.2 vs 상세명세 §C 매핑 갭 6건

### 2.1 배경

- **CFL-RT-002 RESOLVED**: Part2 §6.2.2 (namespace.action) = LOCK 외부 인터페이스. 상세명세 §C (verb_noun) = 참조용 상세 스키마.
- **§B.2 NOTE**: 13 × 13 교차 매핑 시 6건의 Part2 메서드가 상세명세에 1:1 대응 없음.
  - Part2 gap (6): `langgraph.stage.execute`, `langgraph.verify.run_chain`, `llm.generate`, `llm.record_invoke`, `llm.rate_limit.get`, `mcp.bridge.init`
  - 상세명세 orphan (6): `initialize`, `store_memory`, `consolidate_memory`, `get_agent_state`, `stop_agent`, `shutdown`
- **_index.md 기존 매핑**: 7건의 1:1 매핑이 표에 기재되어 있음. 일부는 semantic 불일치가 의심됨 — §2.3 RESOLVED 기록(CFL-RT-006/007/008) 참조.
- **해소 원칙**:
  1. Part2 13개 = 외부 인터페이스 LOCK — 본 카탈로그는 Part2 이름을 전수 기재.
  2. 상세명세와 1:1 semantic match 가 있는 경우 해당 스키마를 재사용 (sot 2/ 정본 = 상세명세 DEFINED-HERE).
  3. 1:1 match 가 없는 경우 (gap) Part2 §6.2.2 에 기재된 설명 주석(line 898~910) + D2.1-D4 스키마 + Part2 §3 정책을 근거로 **본 파일에서 신규 스키마를 DEFINED-HERE 으로 정의** — 이는 §9.1 우선순위 5순위(상세명세)와 동급 정본 지위.
  4. 상세명세 orphan 6개 (`initialize`, `store_memory`, ...) 는 LOCK-RT-03 13개에 포함되지 **않으므로** 본 카탈로그의 13 메서드에 포함되지 않는다. 대신 `_lifecycle` / `_auxiliary` 영역에 **비-LOCK 보조 메서드** 로 §4.14 에 기록하여 Python 엔진 내부 생명주기 (spawn 후 초기화, 종료) 및 Phase 1 구현 중 참조용으로만 사용한다.

### 2.2 해소 결과 테이블 (13 Part2 메서드 → 상세명세 매핑)

| # | Part2 메서드 (LOCK-RT-03) | 설명 (Part2 §6.2.2 주석) | 매핑 상태 | 1:1 상세명세 메서드 | 정본 스키마 출처 | 타임아웃 |
|---|---|---|---|---|---|---|
| 1 | `langgraph.workflow.run` | 워크플로우 실행 | **1:1** | `run_workflow` | 상세명세 §C #10 | 30s |
| 2 | `langgraph.stage.execute` | 스테이지 개별 실행 | **GAP → NEW** | (없음) | 본 파일 §4.2 DEFINED-HERE. 근거: Part2 §6.2.2 "스테이지 개별 실행" + D2.1-D2 LogEventSchema wf.stage.* 이벤트 | 60s |
| 3 | `langgraph.decision.create` | Decision 생성 | **1:1** | `process_message` | 상세명세 §C #2 (LLM turn processing → Decision 생성) | 120s |
| 4 | `langgraph.node.dispatch` | 노드 디스패치 | **1:1** | `start_agent` | 상세명세 §C #7 (agent_type = node_type 해석) | 30s |
| 5 | `langgraph.verify.run_chain` | 검증 체인 실행 | **GAP → NEW** | (없음) | 본 파일 §4.5 DEFINED-HERE. 근거: Part2 §6.2.2 "검증 체인 실행" + 도메인 #1 Verifier-Reasoning 연결 | 90s |
| 6 | `embedding.encode` | 임베딩 인코딩 | **1:1** | `get_embeddings` | 상세명세 §C #11 | 30s |
| 7 | `embedding.store` | 임베딩 저장 | **1:1** | `search_memory` → **정정**: `store_memory` (§2.3 CC-A) | 상세명세 §C #5 (semantic match 우선) | 30s |
| 8 | `llm.generate` | LLM 텍스트 생성 | **GAP → NEW** | (없음 — `process_message` 는 대화형 turn 처리로 구분) | 본 파일 §4.8 DEFINED-HERE. 근거: Part2 §6.2.2 "LLM 텍스트 생성" + D2.1-D4 BrainAdapterResponse | 60s |
| 9 | `llm.record_invoke` | LLM 호출 기록 | **GAP → NEW** | (없음) | 본 파일 §4.9 DEFINED-HERE. 근거: Part2 §6.2.2 "LLM 호출 기록" + D2.1-D2 LogEventSchema + LOCK-RT-06 EventTypeRegistry `oc.*` | 30s |
| 10 | `llm.rate_limit.get` | 레이트리밋 조회 | **GAP → NEW** | (없음) | 본 파일 §4.10 DEFINED-HERE. 근거: Part2 §6.2.2 "레이트리밋 조회" + D2.1-D4 RateLimitConfig | 10s |
| 11 | `mcp.bridge.init` | MCP 브릿지 초기화 | **GAP → NEW** | (없음 — 상세명세 `initialize` 는 Python 엔진 전체 초기화로 구분) | 본 파일 §4.11 DEFINED-HERE. 근거: Part2 §6.2.2 "MCP 브릿지 초기화" + D2.1-D3 MCPBridgeLayer | 30s |
| 12 | `mcp.bridge.health` | MCP 헬스체크 | **1:1** | `health_check` | 상세명세 §C #12 | 5s |
| 13 | `mcp.tools.discover` | MCP 도구 탐색 | **1:1 (정정)** | `execute_tool` → **정정**: 신규 discover 방식 (§2.3 CC-B) | 본 파일 §4.13 DEFINED-HERE. 근거: Part2 §6.2.2 "MCP 도구 탐색" + D2.1-D4 ToolRegistryEntry | 15s |

### 2.3 CONFLICT 해소 기록 (RESOLVED — CONFLICT_LOG v1.2, 2026-04-11)

#### [CFL-RT-006 RESOLVED 2026-04-11 / CC-A] embedding.store ↔ search_memory 매핑 의심

- **출처 A**: `03_python-bridge/_index.md` line 18 — "embedding.store / embedding.encode → search_memory"
- **출처 B**: 상세명세 §C #3 `search_memory` = `{ query, top_k, filters } → { results[] }` (검색 메서드, 저장 아님)
- **본 파일 판정**: embedding.store 는 `store_memory` (§C #5) 에 semantic match. search_memory 는 검색 전용.
- **근거**: `embedding.store` 주석 = "임베딩 저장" (Part2 §6.2.2 line 849, 904). `search_memory` 는 "메모리 검색" 의미로 상충.
- **심각도**: MEDIUM. _index.md 오류로 추정.
- **해소 방향**: step 5 에서 _index.md 의 행 #3/#11 재배치 + 본 파일 §2.2 기준 정렬.
- **조치**: CONFLICT_LOG v1.2 에 CFL-RT-006 RESOLVED 등재 완료 (2026-04-11).

#### [CFL-RT-007 RESOLVED 2026-04-11 / CC-B] mcp.tools.discover ↔ execute_tool 매핑 의심

- **출처 A**: `03_python-bridge/_index.md` line 19 — "mcp.tools.discover → execute_tool"
- **출처 B**: Part2 §6.2.2 주석 (line 910) = "MCP 도구 탐색"; 상세명세 §C #4 `execute_tool` = 도구 실행(invocation), 탐색 아님.
- **본 파일 판정**: `mcp.tools.discover` 는 도구 목록 탐색(list/discover) 이므로 `execute_tool` 과 semantic mismatch. 신규 스키마 정의 (§4.13).
- **근거**: 1) Part2 주석, 2) D2.1-D4 ToolRegistryEntry 가 discover 결과물의 표준 스키마, 3) execute_tool 은 별도 Tauri IPC 커맨드(vamos:tool:invoke, LOCK-RT-01)에서 처리하거나 `langgraph.node.dispatch` 내부에서 호출.
- **심각도**: MEDIUM.
- **해소 방향**: step 5 에서 _index.md 행 #4 를 본 파일 §2.2 로 정렬.
- **조치**: CONFLICT_LOG v1.2 에 CFL-RT-007 RESOLVED 등재 완료 (2026-04-11).

#### [CFL-RT-008 RESOLVED 2026-04-11 / CC-C] `initialize` / `store_memory` / `consolidate_memory` / `get_agent_state` / `stop_agent` / `shutdown` — LOCK-RT-03 외부 존재

- **출처 A**: 상세명세 §C 에 `initialize` / `shutdown` / `consolidate_memory` 등 존재.
- **출처 B**: LOCK-RT-03 = Part2 13 메서드명. 해당 6개는 Part2 에 없음.
- **본 파일 판정**: LOCK-RT-03 = 외부 인터페이스 13 건만. 상세명세 6개 orphan 은 **비-LOCK 보조 메서드** (`_lifecycle` 영역, §4.14) 로 유지. 프론트엔드(React/Tauri)는 직접 호출하지 않으며, Rust `python_manager.rs` 내부에서만 호출.
- **심각도**: LOW (아키텍처 경계 명시로 해소 가능).
- **해소 방향**: 본 파일 §4.14 에 보조 메서드 문서화. LOCK 변경 불필요.
- **조치**: CONFLICT_LOG v1.2 에 CFL-RT-008 RESOLVED 등재 완료 (2026-04-11). _index.md 의 (해당없음) 행 6개는 "보조 메서드" 주석으로 갱신 완료.

### 2.4 해소 요약

- PRE-3 매핑 갭 6건 → 6건 모두 DEFINED-HERE 으로 해소 (§4.2/§4.5/§4.8/§4.9/§4.10/§4.11).
- 기존 _index.md 매핑 중 CC-A/CC-B 2건은 본 파일 §2.2 가 정본으로 판정. step 5 에서 _index.md 정렬.
- CC-C 보조 메서드 6건은 §4.14 에 문서화.
- LOCK-RT-03 13개 메서드명은 **변경 없음** — Part2 §6.2.2 LOCK 준수.

---

## §3. 메서드 카탈로그 목록 (LOCK-RT-03)

### 3.1 13 메서드 네임스페이스별 요약

#### `langgraph.*` (5개)

| # | 메서드 | 용도 | 타임아웃 | L3 상태 |
|---|---|---|---|---|
| 1 | `langgraph.workflow.run` | 워크플로우 전체 실행 (run_id 반환) | 30s | L2 |
| 2 | `langgraph.stage.execute` | 워크플로우 내 특정 스테이지 개별 실행 | 60s | L2 |
| 3 | `langgraph.decision.create` | LLM turn 처리 → Decision 생성 (process_message 대응) | 120s | **L3 (§5)** |
| 4 | `langgraph.node.dispatch` | 노드 디스패치 (에이전트/툴 실행 위임) | 30s | L2 |
| 5 | `langgraph.verify.run_chain` | 검증 체인 실행 (#1 Verifier 연결) | 90s | L2 |

#### `embedding.*` (2개)

| # | 메서드 | 용도 | 타임아웃 |
|---|---|---|---|
| 6 | `embedding.encode` | 텍스트 임베딩 벡터 생성 (get_embeddings 대응) | 30s |
| 7 | `embedding.store` | 임베딩 + 메타를 메모리 계층에 저장 (store_memory 대응) | 30s |

#### `llm.*` (3개)

| # | 메서드 | 용도 | 타임아웃 |
|---|---|---|---|
| 8 | `llm.generate` | Raw LLM 텍스트 생성 (프롬프트 → 응답) | 60s |
| 9 | `llm.record_invoke` | LLM 호출 이력 기록 (과금/감사) | 30s |
| 10 | `llm.rate_limit.get` | 현재 레이트리밋 상태 조회 | 10s |

#### `mcp.*` (3개)

| # | 메서드 | 용도 | 타임아웃 |
|---|---|---|---|
| 11 | `mcp.bridge.init` | MCP 브릿지 초기화 (서버 연결 + 세션) | 30s |
| 12 | `mcp.bridge.health` | MCP 브릿지 헬스체크 | 5s |
| 13 | `mcp.tools.discover` | MCP 서버에서 제공하는 도구 목록 탐색 | 15s |

### 3.2 타임아웃 근거

- `process_message` 120s: 계획서 §B.2 + 상세명세 §C #2 정본 (핵심 메서드). 본 파일에서는 `langgraph.decision.create` 에 동일값 적용.
- 기타 11개 30s: 계획서 §B.2 기본값. DEFINED-HERE 메서드(2/5/8/9/10/11/13)는 semantic 특성상 개별 조정.
- `health_check` 5s: 계획서 §B.2. `mcp.bridge.health` 동일.
- 프레이밍/전송 규격은 rpc_protocol.md §3 단일 정본.

---

## §4. 각 메서드 req/resp 스키마 (13 + 보조 6)

> 각 스키마는 rpc_protocol.md §2.5 의 `RpcRequest<P>` / `RpcResponse<R>` 를 wrapper 로 사용. 본 절에서는 `P` (params type) 및 `R` (result type) 만 정의. 모든 params 는 `_meta: RpcMeta` 를 예약 필드로 포함하며, 본 절 예제 JSON 에서는 가독성을 위해 생략 가능.

### §4.1 `langgraph.workflow.run` (#1, 1:1)

- **정본**: 상세명세 §C #10 `run_workflow`
- **Rust types**: T1-2 workflow_event_config_models.rs — `WorkflowRunInput`, `WorkflowRunHandle`
- **타임아웃**: 30s
- **가능한 error**: `-32602 invalid_params`, `-32001 python_bridge_timeout`, `-32010 model_not_found`, `-32020 workflow_cancelled`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct LanggraphWorkflowRunParams {
    pub workflow_id: String,        // e.g. "wf_plan_execute"
    pub input: serde_json::Value,   // workflow-specific input (untyped at bridge layer)
    pub trace_context: Option<TraceContext>,  // T1-2
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct LanggraphWorkflowRunResult {
    pub run_id: String,
    pub status: WorkflowRunStatus,   // Pending | Running | Completed | Failed
    pub started_at: DateTime<Utc>,
    pub _meta: RpcMeta,
}
```

**예제 request**

```json
{
  "jsonrpc":"2.0",
  "id":"01930e8e-0001-7000-8000-000000000001",
  "method":"langgraph.workflow.run",
  "params":{
    "workflow_id":"wf_plan_execute",
    "input":{"query":"Summarize today's tasks","user_id":"u_42"},
    "_meta":{"trace_id":"01930e8e-0001-7000-8000-000000000001","correlation_id":"req_1713480000_0001","issued_at":"2026-04-11T02:00:00.123Z","deadline_ms":30000}
  }
}
```

**예제 response**

```json
{
  "jsonrpc":"2.0",
  "id":"01930e8e-0001-7000-8000-000000000001",
  "result":{
    "run_id":"run_abc123",
    "status":"Running",
    "started_at":"2026-04-11T02:00:00.234Z",
    "_meta":{"trace_id":"01930e8e-0001-7000-8000-000000000001","correlation_id":"req_1713480000_0001","completed_at":"2026-04-11T02:00:00.289Z","elapsed_ms":166}
  }
}
```

---

### §4.2 `langgraph.stage.execute` (#2, GAP → NEW, DEFINED-HERE)

- **근거**: Part2 §6.2.2 주석 "스테이지 개별 실행" + D2.1-D2 LogEventSchema `wf.stage.started`/`wf.stage.completed` 이벤트 체계.
- **용도**: 실행 중인 workflow 의 특정 stage 를 단독 호출 (디버깅/재실행/부분 재시도).
- **Rust types**: T1-2 workflow_event_config_models.rs — `StageExecuteInput`, `StageExecuteResult` (신규 추가 대상 — T1-2 연동).
- **타임아웃**: 60s
- **가능한 error**: `-32602 invalid_params`, `-32001 python_bridge_timeout`, `-32010 model_not_found` (workflow 미존재), `-32020 workflow_cancelled`

```rust
#[derive(Serialize, Deserialize)]
pub struct LanggraphStageExecuteParams {
    pub run_id: String,                 // 이전 workflow.run 의 run_id (신규 실행 시 null)
    pub workflow_id: String,            // 대상 워크플로우
    pub stage_id: String,               // 스테이지 식별자
    pub stage_input: serde_json::Value, // 스테이지 입력
    pub overrides: Option<StageOverrides>,  // 타임아웃/모델 등 override
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct LanggraphStageExecuteResult {
    pub run_id: String,
    pub stage_id: String,
    pub output: serde_json::Value,
    pub status: StageStatus,            // Completed | Skipped | Failed
    pub events: Vec<LogEventRef>,       // D2.1-D2 wf.stage.* 이벤트 참조
    pub elapsed_ms: u64,
    pub _meta: RpcMeta,
}
```

**예제**

```json
// req
{"jsonrpc":"2.0","id":"...","method":"langgraph.stage.execute","params":{"run_id":"run_abc123","workflow_id":"wf_plan_execute","stage_id":"stage_plan","stage_input":{"goal":"summarize"},"overrides":null,"_meta":{"...":"..."}}}
// resp
{"jsonrpc":"2.0","id":"...","result":{"run_id":"run_abc123","stage_id":"stage_plan","output":{"plan":["step1","step2"]},"status":"Completed","events":[{"event_id":"evt_1","type":"wf.stage.completed"}],"elapsed_ms":1234,"_meta":{"...":"..."}}}
```

---

### §4.3 `langgraph.decision.create` (#3, 1:1 = process_message)

- **정본**: 상세명세 §C #2 `process_message` — `{ session_id, message, context: Turn[] }` → `{ response: str, tool_calls?: ToolCall[], tokens: u32 }`
- **§5 L3 상세화 대상**: 본 메서드는 §5 에서 시퀀스/에러/재시도 상세화.
- **Rust types**: T1-2 core_models.rs — `Turn`, `ToolCall`, `DecisionRecord` (D2.1-D2 DecisionSchema)
- **타임아웃**: 120s (계획서 §B.2 핵심 메서드)
- **가능한 error**: `-32602 invalid_params`, `-32001 python_bridge_timeout`, `-32010 model_not_found`, `-32011 embedding_failure` (컨텍스트 임베딩 생성 실패), `-32013 rate_limit_exceeded`, `-32020 workflow_cancelled`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct LanggraphDecisionCreateParams {
    pub session_id: String,
    pub message: String,
    pub context: Vec<Turn>,               // 최근 대화 이력 (T1-2 core_models.rs)
    pub tool_policy: Option<ToolPolicy>,  // 도구 사용 정책 (선택)
    pub stream: bool,                     // false=동기, true=스트리밍 (Phase 2)
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct LanggraphDecisionCreateResult {
    pub decision_id: String,
    pub response: String,
    pub tool_calls: Option<Vec<ToolCall>>,
    pub tokens: TokenUsage,               // prompt/completion/total
    pub citations: Vec<Citation>,         // RAG 근거
    pub confidence: f32,                  // [0, 1]
    pub _meta: RpcMeta,
}
```

**예제**

```json
// req
{"jsonrpc":"2.0","id":"01930e8e-0003-7000-8000-000000000003","method":"langgraph.decision.create","params":{"session_id":"sess_abc","message":"오늘 할 일 요약","context":[{"role":"user","content":"안녕"},{"role":"assistant","content":"안녕하세요"}],"tool_policy":null,"stream":false,"_meta":{"trace_id":"01930e8e-0003-...","correlation_id":"req_...","issued_at":"2026-04-11T02:00:00Z","deadline_ms":120000}}}
// resp
{"jsonrpc":"2.0","id":"01930e8e-0003-7000-8000-000000000003","result":{"decision_id":"dec_xyz","response":"오늘의 할 일: ...","tool_calls":null,"tokens":{"prompt":1200,"completion":300,"total":1500},"citations":[],"confidence":0.92,"_meta":{"...":"..."}}}
```

---

### §4.4 `langgraph.node.dispatch` (#4, 1:1 = start_agent)

- **정본**: 상세명세 §C #7 `start_agent` — `{ agent_type, task, config }` → `{ agent_id }`
- **해석**: Part2 "노드 디스패치" = LangGraph node 를 에이전트로 해석, start_agent 시그니처와 semantic 일치.
- **Rust types**: T1-2 agent_models.rs — `AgentType`, `AgentConfig`, `AgentHandle` + D2.1-D3 NodeRegistry
- **타임아웃**: 30s
- **가능한 error**: `-32602 invalid_params`, `-32010 model_not_found` (node_id 미등록), `-32021 permission_denied`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct LanggraphNodeDispatchParams {
    pub node_id: String,              // D2.1-D3 NodeRegistry 등록된 node_id
    pub task: String,                 // 작업 지시문
    pub config: AgentConfig,          // T1-2 agent_models.rs
    pub parent_run_id: Option<String>, // workflow.run 상위 run_id (tracking)
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct LanggraphNodeDispatchResult {
    pub agent_id: String,             // 디스패치된 에이전트 인스턴스 id
    pub node_id: String,
    pub status: AgentStatus,          // Dispatched | Running | Queued
    pub _meta: RpcMeta,
}
```

---

### §4.5 `langgraph.verify.run_chain` (#5, GAP → NEW, DEFINED-HERE)

- **근거**: Part2 §6.2.2 주석 "검증 체인 실행" + 도메인 #1 Verifier-Reasoning 교차 경계 (AUTHORITY_CHAIN §6).
- **용도**: Verifier 도메인의 verification chain 을 Python 엔진 측에서 실행하고 결과를 Rust 로 반환.
- **Rust types**: T1-2 workflow_event_config_models.rs — `VerifyChainInput`, `VerifyChainResult` (신규, #1 Verifier 경계에서 참조 스키마 공유 필요 — 본 T1-3 에서는 stub 으로 정의, #1 도메인 정본 확정 후 정렬).
- **타임아웃**: 90s
- **가능한 error**: `-32602 invalid_params`, `-32001 python_bridge_timeout`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct LanggraphVerifyRunChainParams {
    pub chain_id: String,              // 검증 체인 식별자 (#1 Verifier 정본)
    pub target: VerifyTarget,          // { decision_id | response | claims[] }
    pub evidence: Vec<Evidence>,       // 검증 근거
    pub confidence_threshold: Option<f32>,  // 기본 0.7
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct LanggraphVerifyRunChainResult {
    pub chain_id: String,
    pub verdict: VerifyVerdict,        // Passed | Failed | Inconclusive
    pub confidence: f32,
    pub findings: Vec<Finding>,
    pub elapsed_ms: u64,
    pub _meta: RpcMeta,
}
```

> **주의**: `VerifyTarget`/`VerifyVerdict`/`Finding` 은 도메인 #1 Verifier-Reasoning 정본이 있을 경우 해당 정본을 채택하고 본 파일 stub 은 정렬 대상. 본 T1-3 단독 결론 금지 → 후속 세션에서 #1 도메인과 교차 확인 시 신규 CFL 등재 가능성 있음 (현재 OPEN 없음).

---

### §4.6 `embedding.encode` (#6, 1:1 = get_embeddings)

- **정본**: 상세명세 §C #11 `get_embeddings` — `{ texts: str[], model? }` → `{ embeddings: float[][] }`
- **Rust types**: T1-2 core_models.rs — `EmbeddingVector` (Vec<f32>), `EmbeddingModel`
- **타임아웃**: 30s
- **가능한 error**: `-32602 invalid_params`, `-32010 model_not_found`, `-32011 embedding_failure`, `-32002 python_bridge_oversized` (texts 합계 > 4 MiB), `-32001 python_bridge_timeout`

```rust
#[derive(Serialize, Deserialize)]
pub struct EmbeddingEncodeParams {
    pub texts: Vec<String>,
    pub model: Option<String>,        // 기본: config.default_embedding_model
    pub normalize: bool,              // L2 정규화 여부 (기본 true)
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct EmbeddingEncodeResult {
    pub model: String,
    pub dimensions: u32,
    pub embeddings: Vec<Vec<f32>>,    // texts.len() × dimensions
    pub _meta: RpcMeta,
}
```

---

### §4.7 `embedding.store` (#7, 1:1 정정 = store_memory) [CC-A]

- **정본**: 상세명세 §C #5 `store_memory` — `{ content, level, tags }` → `{ id }`. (CC-A 로 _index.md 의 `search_memory` 매핑 정정.)
- **Rust types**: T1-2 memory_models.rs — `MemoryLevel` (WorkingMemory/EpisodicMemory/SemanticMemory/LongTermMemory), `MemoryEntry`, `MemoryId`
- **타임아웃**: 30s
- **가능한 error**: `-32602 invalid_params`, `-32011 embedding_failure` (embedding 생성 실패), `-32001 python_bridge_timeout`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct EmbeddingStoreParams {
    pub content: String,
    pub level: MemoryLevel,
    pub tags: Vec<String>,
    pub metadata: Option<serde_json::Value>,
    pub embedding: Option<Vec<f32>>,   // 사전 계산된 임베딩 (선택)
    pub model: Option<String>,         // embedding.encode 와 동일 모델 참조
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct EmbeddingStoreResult {
    pub id: String,                    // MemoryId
    pub level: MemoryLevel,
    pub indexed: bool,                 // 벡터 인덱스 등록 여부
    pub _meta: RpcMeta,
}
```

---

### §4.8 `llm.generate` (#8, GAP → NEW, DEFINED-HERE)

- **근거**: Part2 §6.2.2 주석 "LLM 텍스트 생성" + D2.1-D4 BrainAdapterResponse. `langgraph.decision.create` 와 구분되는 "raw completion" 목적.
- **Rust types**: T1-2 (신규 또는 core_models.rs) — `LlmModel`, `LlmGenerateRequest`, `LlmGenerateResponse`, D2.1-D4 BrainAdapterResponse 정렬
- **타임아웃**: 60s
- **가능한 error**: `-32602 invalid_params`, `-32010 model_not_found`, `-32013 rate_limit_exceeded`, `-32001 python_bridge_timeout`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct LlmGenerateParams {
    pub model: String,                 // e.g. "claude-opus-4-6"
    pub prompt: String,                // raw prompt
    pub system: Option<String>,        // system 지시문
    pub max_tokens: u32,
    pub temperature: f32,              // [0.0, 1.0] (Anthropic 범위; >1.0 거부 — claude-* 대상)
    pub stop: Option<Vec<String>>,
    pub stream: bool,                  // Phase 2 스트리밍
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct LlmGenerateResult {
    pub model: String,
    pub text: String,
    pub finish_reason: FinishReason,   // Stop | Length | ContentFilter | Error
    pub tokens: TokenUsage,
    pub invoke_id: String,             // llm.record_invoke 로 연결
    pub _meta: RpcMeta,
}
```

---

### §4.9 `llm.record_invoke` (#9, GAP → NEW, DEFINED-HERE)

- **근거**: Part2 §6.2.2 주석 "LLM 호출 기록" + D2.1-D2 LogEventSchema + LOCK-RT-06 EventTypeRegistry `oc.*` (operational).
- **용도**: 과금/감사/메트릭 목적의 LLM 호출 이력 기록.
- **Rust types**: T1-2 workflow_event_config_models.rs — `LlmInvokeRecord`, D2.1-D2 LogEventSchema 정렬 (CFL-RT-004 와 교차 대응).
- **타임아웃**: 30s
- **가능한 error**: `-32602 invalid_params`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct LlmRecordInvokeParams {
    pub invoke_id: String,             // llm.generate 의 invoke_id
    pub model: String,
    pub tokens: TokenUsage,
    pub latency_ms: u64,
    pub cost_usd: Option<f64>,         // 측정 가능한 경우
    pub outcome: InvokeOutcome,        // Success | Error | Cancelled
    pub error: Option<String>,
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct LlmRecordInvokeResult {
    pub record_id: String,
    pub event_id: String,              // D2.1-D2 LogEventSchema event_id 참조
    pub _meta: RpcMeta,
}
```

---

### §4.10 `llm.rate_limit.get` (#10, GAP → NEW, DEFINED-HERE)

- **근거**: Part2 §6.2.2 주석 "레이트리밋 조회" + D2.1-D4 RateLimitConfig.
- **용도**: 현재 모델별 레이트리밋 상태 조회 (남은 토큰, reset 시각).
- **Rust types**: T1-2 (D2.1-D4 RateLimitConfig 참조)
- **타임아웃**: 10s (조회 성격)
- **가능한 error**: `-32602 invalid_params`, `-32010 model_not_found`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct LlmRateLimitGetParams {
    pub model: Option<String>,         // None = 전체 모델 상태
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct LlmRateLimitGetResult {
    pub entries: Vec<RateLimitEntry>,
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct RateLimitEntry {
    pub model: String,
    pub window: RateLimitWindow,       // PerMinute | PerHour | PerDay
    pub limit: u64,                    // 정책 상한
    pub remaining: u64,                // 남은 quota
    pub reset_at: DateTime<Utc>,       // RFC3339
    pub config: RateLimitConfig,       // D2.1-D4 정본
}
```

---

### §4.11 `mcp.bridge.init` (#11, GAP → NEW, DEFINED-HERE)

- **근거**: Part2 §6.2.2 주석 "MCP 브릿지 초기화" + D2.1-D3 MCPBridgeLayer.
- **용도**: MCP 서버 연결 + 세션 수립. `initialize` (상세명세 §C #1, Python 엔진 전체 초기화) 와는 **구분**.
- **Rust types**: T1-2 (D2.1-D3 MCPBridgeLayer 참조), T1-1 mcp_* IPC 커맨드와 경계.
- **타임아웃**: 30s
- **가능한 error**: `-32602 invalid_params`, `-32012 mcp_error`, `-32001 python_bridge_timeout`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct McpBridgeInitParams {
    pub server_uri: String,            // MCP 서버 엔드포인트
    pub auth: Option<McpAuth>,         // Bearer / ApiKey / OAuth
    pub capabilities: Vec<String>,     // 클라이언트 capability 선언
    pub timeout_ms: Option<u64>,       // override
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct McpBridgeInitResult {
    pub session_id: String,            // MCP 세션 식별자
    pub server_info: McpServerInfo,    // name, version, capabilities
    pub negotiated_protocol: String,   // MCP 프로토콜 버전
    pub _meta: RpcMeta,
}
```

---

### §4.12 `mcp.bridge.health` (#12, 1:1 = health_check)

- **정본**: 상세명세 §C #12 `health_check` — `{}` → `{ status, uptime_s, memory_mb }`. MCP 브릿지 컨텍스트에서 적용.
- **Rust types**: T1-2 (D2.1-D4 BrainAdapterResponse.health 정렬 가능)
- **타임아웃**: 5s (LOCK-RT-12 과 별개 — RPC 층 타임아웃)
- **가능한 error**: `-32012 mcp_error`, `-32001 python_bridge_timeout`

```rust
#[derive(Serialize, Deserialize)]
pub struct McpBridgeHealthParams {
    pub session_id: Option<String>,    // 특정 세션 대상 (None = 브릿지 전체)
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct McpBridgeHealthResult {
    pub status: HealthStatus,          // Healthy | Degraded | Unhealthy
    pub uptime_s: u64,
    pub memory_mb: u32,
    pub active_sessions: u32,
    pub last_error: Option<String>,
    pub _meta: RpcMeta,
}
```

---

### §4.13 `mcp.tools.discover` (#13, 1:1 정정 → NEW, DEFINED-HERE) [CC-B]

- **근거**: Part2 §6.2.2 주석 "MCP 도구 탐색" + D2.1-D4 ToolRegistryEntry (tool_id, category, adapter_id, risk_class, cost_class, required_gates, outputs, notes). `execute_tool` 매핑 정정.
- **Rust types**: T1-2 — `ToolRegistryEntry` (D2.1-D4 정본)
- **타임아웃**: 15s
- **가능한 error**: `-32602 invalid_params`, `-32012 mcp_error`, `-32001 python_bridge_timeout`, `-32603 internal_error`

```rust
#[derive(Serialize, Deserialize)]
pub struct McpToolsDiscoverParams {
    pub session_id: String,            // mcp.bridge.init 결과
    pub filter: Option<ToolFilter>,    // category / risk_class 필터
    pub refresh: bool,                 // 서버 재조회 강제 (기본 false=캐시)
    pub _meta: RpcMeta,
}

#[derive(Serialize, Deserialize)]
pub struct McpToolsDiscoverResult {
    pub session_id: String,
    pub tools: Vec<ToolRegistryEntry>, // D2.1-D4 구조
    pub cached: bool,
    pub cache_expires_at: Option<DateTime<Utc>>,
    pub _meta: RpcMeta,
}
```

---

### §4.14 보조 생명주기 메서드 (비-LOCK, `_lifecycle`)

> **범위**: LOCK-RT-03 외부. 프론트엔드 직접 호출 금지. Rust `python_manager.rs` 내부에서만 호출하며, `_` prefix 로 비공개 구분.

| 메서드 | 상세명세 대응 | 용도 | 호출 지점 |
|---|---|---|---|
| `_lifecycle.initialize` | §C #1 `initialize` | 전체 Python 엔진 초기화 (config 주입, 모델 로드) | spawn_protocol 6번 절차 |
| `_lifecycle.store_memory` | §C #5 `store_memory` | `embedding.store` 내부에서 호출되는 raw store | embedding.store 위임 |
| `_lifecycle.consolidate_memory` | §C #6 `consolidate_memory` | 메모리 통합 배치 (cron 또는 임계치 트리거) | 백그라운드 tick |
| `_lifecycle.get_agent_state` | §C #8 `get_agent_state` | 에이전트 상태 조회 | `langgraph.node.dispatch` 후속 조회 |
| `_lifecycle.stop_agent` | §C #9 `stop_agent` | 에이전트 중단 | `langgraph.workflow.run` 취소 경로 |
| `_lifecycle.shutdown` | §C #13 `shutdown` | Graceful shutdown | python_manager::shutdown() |

- **메서드명 네임스페이스**: `_lifecycle.*` prefix 로 LOCK-RT-03 패턴 (`langgraph.*/embedding.*/llm.*/mcp.*`) 과 분리.
- **검증**: method_not_found 검증 시 `_lifecycle.*` 는 허용 범위 (화이트리스트) 에 추가.
- **Phase 2 확장**: 향후 필요 시 LOCK-RT-03 확장 (15개로 증가) 을 CONFLICT_LOG 로 제안.

---

## §5. `process_message` / `langgraph.decision.create` L3 상세화 (§13 L3 승급)

> 계획서 §13 에서 "process_message" 를 최우선 L3 상세화 대상으로 지정. Part2 명 `langgraph.decision.create` = 상세명세 명 `process_message` 1:1 매핑 (§2.2).

### 5.1 시퀀스 다이어그램

```
[React UI]   [Tauri IPC]   [python_manager]   [Python rpc/server]   [LangGraph]   [LLM]
    |             |               |                    |                 |         |
    |--send_msg-->|               |                    |                 |         |
    |             |--build req--->|                    |                 |         |
    |             |               |--uuid v7 issue--.  |                 |         |
    |             |               |  register pending  |                 |         |
    |             |               |  (BTree insert)    |                 |         |
    |             |               |--stdin write------>|                 |         |
    |             |               |                    |--parse-->       |         |
    |             |               |                    |--validate------>|         |
    |             |               |                    |                 |--query memory
    |             |               |                    |                 |<-----results
    |             |               |                    |                 |--call--->|
    |             |               |                    |                 |<-resp---|
    |             |               |                    |--build Decision |         |
    |             |               |                    |<--result--------|         |
    |             |               |<---stdout resp-----|                 |         |
    |             |               |--match pending--.  |                 |         |
    |             |               |  (oneshot send)    |                 |         |
    |             |<---result-----|                    |                 |         |
    |<---event----|               |                    |                 |         |
```

### 5.2 에러 시나리오 (LOCK-RT-14 매핑)

| # | 시나리오 | 감지 시점 | 응답 코드 | TauriError | 재시도 정책 | 사용자 노출 |
|---|---|---|---|---|---|---|
| E1 | params 누락 (session_id) | Python 측 validate | -32602 | ValidationError | 불가 | "요청 형식 오류" |
| E2 | session_id 미존재 | Python 측 memory 조회 | -32010 | NotFound | 불가 | "세션을 찾을 수 없습니다" |
| E3 | LLM 모델 미설정 | Python 측 model registry | -32010 | NotFound | 불가 | "모델 설정 필요" |
| E4 | LLM rate limit | LLM API 호출 | -32013 | PermissionDenied | 1회 60s 대기 후 재시도 | "잠시 후 다시 시도" |
| E5 | LLM timeout (120s 초과) | Rust tokio::timeout | -32001 | Timeout | 1회 재시도 (cached context) | "응답 지연 — 재시도 중" |
| E6 | LLM content filter | LLM API 응답 | -32020 | Timeout (re-label) | 불가 (컨텐츠 수정 필요) | "안전 정책으로 응답 제한" |
| E7 | Python 프로세스 크래시 | stdout EOF | -32004 | PythonBridgeError | LOCK-RT-13 restart 후 1회 재시도 | "연결 복구 중..." |
| E8 | OOM | exit 137 | -32003 | PythonBridgeError | 5s backoff × 3 restart 후 재시도 | "메모리 부족 — 재시도 중" |
| E9 | embedding 생성 실패 (컨텍스트) | Python 측 | -32011 | InternalError | 1회 재시도 | "메모리 검색 실패" |
| E10 | tool_call 권한 거부 | Python 측 | -32021 | PermissionDenied | 사용자 승인 요청 | 구체적 권한 안내 |

### 5.3 재시도 정책

```
retry_policy(error, attempt):
  match error.code:
    -32004 (crash), -32003 (oom), -32000 (unhealthy):
      # Python 프로세스 레벨 — python_manager::restart() 가 선행
      if attempt < 1 and process_state == Running:
        return RetryAfter(Duration::ZERO)
      else:
        return GiveUp
    -32013 (rate_limit):
      if attempt < 1:
        return RetryAfter(Duration::from_secs(60))
      else:
        return GiveUp
    -32001 (timeout):
      if attempt < 1 and params.context.len() > 0:
        # 컨텍스트 축소 후 재시도 (Phase 2)
        return RetryWith(params.truncate_context(50%))
      else:
        return GiveUp
    -32011 (embedding_failure):
      if attempt < 1:
        return RetryAfter(Duration::from_millis(500))
      else:
        return GiveUp
    _:
      return GiveUp   # -32602, -32010, -32021 등은 즉시 실패
```

### 5.4 타임아웃 계층 적용

| 계층 | 값 | 감지 방식 | 위반 시 |
|---|---|---|---|
| L0 Spawn | 5s × 3 | 선행 (RPC 이전) | spawn_failed |
| L1 HC | 15s interval | 병렬 | 3회 실패 → Unhealthy |
| L2 RPC (본 메서드) | 120s | tokio::timeout | -32001 python_bridge_timeout |
| L2 RPC Python 측 | 119.5s | deadline_ms - 500ms | -32020 workflow_cancelled |
| L3 Graceful shutdown | 5s | shutdown 호출 시 | drain 후 SIGKILL |

### 5.5 의사코드: python_manager::send() L3 흐름

```
fn send(method, params, timeout_ms):          # O(log N) + network
  1. assert state == Running                   # O(1) AtomicU8
  2. permit = semaphore.acquire()               # O(1) amortized
  3. id = uuid_v7()                             # O(1)
  4. meta = RpcMeta { trace_id, correlation_id, issued_at, deadline_ms }
  5. req = RpcRequest { jsonrpc, id, method, params + meta }
  6. line = serde_json::to_string(req)          # O(payload)
  7. pending.lock().insert(id, entry)           # O(log N) BTreeMap
  8. stdin_mutex.lock():                        # O(1)
       stdin.write_all(line + "\n")             # O(line_len)
       stdin.flush()
  9. result = tokio::timeout(timeout_ms + 1000, rx.recv())  # network-bound
 10. match result:
       Ok(Ok(resp)): return map_result(resp)
       Ok(Err(_)):  return error(-32603)         # oneshot dropped
       Err(_):      pending.remove(id)           # O(log N)
                    return error(-32001)
```

---

## §6. FR-8 타임아웃 캐스케이드 — 메서드별 매핑표

> rpc_protocol.md §6 L0~L3 계층과 정합. 메서드별 override 는 config.rs 에서 제공 가능 (LOCK 수치 제외).

| Part2 메서드 | RPC Timeout (L2) | Python 측 early-cancel | Rust grace | config override key |
|---|---|---|---|---|
| langgraph.workflow.run | 30s | 29.5s | +1s | python_bridge.workflow_run_timeout_ms |
| langgraph.stage.execute | 60s | 59.5s | +1s | python_bridge.stage_execute_timeout_ms |
| **langgraph.decision.create** | **120s** | 119.5s | +1s | 불가 (핵심 LOCK) |
| langgraph.node.dispatch | 30s | 29.5s | +1s | python_bridge.node_dispatch_timeout_ms |
| langgraph.verify.run_chain | 90s | 89.5s | +1s | python_bridge.verify_chain_timeout_ms |
| embedding.encode | 30s | 29.5s | +1s | python_bridge.embedding_encode_timeout_ms |
| embedding.store | 30s | 29.5s | +1s | python_bridge.embedding_store_timeout_ms |
| llm.generate | 60s | 59.5s | +1s | python_bridge.llm_generate_timeout_ms |
| llm.record_invoke | 30s | 29.5s | +1s | python_bridge.llm_record_timeout_ms |
| llm.rate_limit.get | 10s | 9.5s | +1s | python_bridge.rate_limit_get_timeout_ms |
| mcp.bridge.init | 30s | 29.5s | +1s | python_bridge.mcp_init_timeout_ms |
| mcp.bridge.health | 5s | 4.5s | +1s | 불가 (HC 경계 LOCK-RT-12 참조) |
| mcp.tools.discover | 15s | 14.5s | +1s | python_bridge.mcp_discover_timeout_ms |

- 공통 grace: Rust 측 `tokio::time::timeout = RPC timeout + 1s`. Python 측 early-cancel 0.5s 여유.
- L0 Spawn / L1 HC / L3 Graceful 은 rpc_protocol.md §6.2 정본 참조.

---

## §7. T1-2 Serde 모델 참조 매트릭스

> 각 메서드 params/result 가 T1-2 산출물 (02_serde-models/) 의 어떤 struct 를 사용하는지 매핑. T1-2 완료 후 본 파일 업데이트 대상.

| Part2 메서드 | params 주요 struct | result 주요 struct | 소속 파일 |
|---|---|---|---|
| langgraph.workflow.run | WorkflowRunInput (신규) | WorkflowRunHandle (신규) | workflow_event_config_models.rs |
| langgraph.stage.execute | StageExecuteInput (신규) | StageExecuteResult (신규) | workflow_event_config_models.rs |
| langgraph.decision.create | Turn[], ToolPolicy | DecisionRecord, TokenUsage, Citation | core_models.rs (D2.1-D2 DecisionSchema) |
| langgraph.node.dispatch | AgentConfig (D2.1-D3 NodeRegistry) | AgentHandle | agent_models.rs |
| langgraph.verify.run_chain | VerifyTarget, Evidence (stub) | VerifyVerdict, Finding (stub) | workflow_event_config_models.rs (또는 #1 Verifier 공유) |
| embedding.encode | (primitive) | Vec<Vec<f32>>, EmbeddingModel | core_models.rs |
| embedding.store | MemoryLevel, MemoryEntry (부분) | MemoryId | memory_models.rs |
| llm.generate | LlmGenerateRequest (신규) | LlmGenerateResponse + BrainAdapterResponse (D2.1-D4) | core_models.rs |
| llm.record_invoke | LlmInvokeRecord (신규) | LogEventRef (D2.1-D2) | workflow_event_config_models.rs |
| llm.rate_limit.get | (primitive) | RateLimitEntry, RateLimitConfig (D2.1-D4) | workflow_event_config_models.rs |
| mcp.bridge.init | McpAuth (신규) | McpServerInfo, MCPBridgeLayer (D2.1-D3) | agent_models.rs (또는 별도 mcp_models.rs — FR-2 확장 고려) |
| mcp.bridge.health | (primitive) | HealthStatus | agent_models.rs |
| mcp.tools.discover | ToolFilter (신규) | ToolRegistryEntry (D2.1-D4) | agent_models.rs |

### 7.1 T1-2 연동 체크리스트

- [ ] T1-2 산출물에 위 "신규" 표시 struct 가 포함되는지 확인 (step 5 인덱스 갱신 시 검증)
- [ ] CFL-RT-004 (EventLog 필드명 불일치) 해소 시 llm.record_invoke 의 LogEventRef 재정렬
- [ ] CFL-RT-005 (25개 Serde 수치) 해소 시 본 파일 §7 매트릭스에서 실제 struct 수 확인

---

## §8. T1-1 IPC 경계 (IPC → python_manager → JSON-RPC 흐름)

### 8.1 흐름 다이어그램

```
┌──────────────────────────┐
│  React UI (Tauri invoke)  │
│  e.g. "vamos:conversation:send" │
└────────────┬─────────────┘
             │ Tauri IPC (serde_json, 10 MB LOCK-MCP-01)
             v
┌──────────────────────────┐
│  ipc_protocol.rs (T1-1)   │
│  72개 #[tauri::command]    │
│    - UUID v7 trace_id 발급 │
│    - params 검증 (serde)   │
│    - LOCK-RT-14 에러 매핑  │
└────────────┬─────────────┘
             │ Rust function call
             v
┌──────────────────────────┐
│  python_manager.rs (T1-3) │
│  send<P, R>(method, P, ms) │
│    - rpc_protocol.md §7    │
│    - pending BTreeMap      │
└────────────┬─────────────┘
             │ JSON-RPC 2.0 (stdin/stdout, \n, 4 MiB)
             v
┌──────────────────────────┐
│  Python rpc/server.py     │
│  13 methods + _lifecycle  │
└──────────────────────────┘
```

### 8.2 IPC ↔ JSON-RPC 매핑 (대표 예시)

> 72 IPC 커맨드(LOCK-RT-01) 중 Python 브릿지 호출 대상 매핑 예시. 전수 매핑은 T1-1 산출물 01_ipc-commands/ 에서 정의.

| IPC 커맨드 (T1-1) | 호출 JSON-RPC 메서드 (T1-3) | 타임아웃 |
|---|---|---|
| vamos:conversation:send | langgraph.decision.create | 120s |
| vamos:memory:search | embedding.encode → (내부 벡터 검색) → (결과) | 30s |
| vamos:memory:store | embedding.store | 30s |
| vamos:agent:dispatch | langgraph.node.dispatch | 30s |
| vamos:workflow:run | langgraph.workflow.run | 30s |
| vamos:workflow:stage | langgraph.stage.execute | 60s |
| vamos:mcp:connect | mcp.bridge.init | 30s |
| vamos:mcp:list_tools | mcp.tools.discover | 15s |
| vamos:health:python | mcp.bridge.health | 5s |
| vamos:llm:generate | llm.generate | 60s |
| vamos:llm:rate_limit | llm.rate_limit.get | 10s |
| vamos:verify:run | langgraph.verify.run_chain | 90s |

- 매핑 표준은 T1-1 의 IPC 시그니처 정본 확정 후 갱신. 본 표는 T1-3 관점 설계 의도만 표시 (CONFLICT 가능).

### 8.3 경계 원칙

1. **Tauri IPC 커맨드는 JSON-RPC 메서드명과 독립**. 72 IPC 이름 (vamos:*:*) vs 13 JSON-RPC 이름 (namespace.action) 은 서로 다른 네이밍 체계.
2. **Python 호출은 반드시 python_manager::send() 경유** — 직접 subprocess 통신 금지.
3. **TauriError 매핑은 ipc_protocol.rs 에서 수행** — JSON-RPC 층은 RpcError 로 반환, IPC 층에서 TauriError 로 변환 (rpc_protocol.md §5.3).
4. **trace_id 전파**: IPC 층에서 UUID v7 발급 → RpcMeta 에 주입 → Python structlog 컨텍스트에 바인딩 (rpc_protocol.md §4.2).

---

## §9. Phase 2 테스트 시나리오 (메서드 카탈로그 관점, 10건 이상)

> rpc_protocol.md §8 의 TC-01~TC-14 와 보완 관계. 본 절은 메서드별 스키마 검증 중심.

### MC-01 — 13 메서드 전수 req/resp 왕복
- 13 개 메서드 각 happy path 1회 × 13 = 13 왕복.
- 검증: 모든 메서드의 params/result 가 T1-2 struct 로 정상 역직렬화, elapsed_ms 수집, trace_id 매칭.

### MC-02 — langgraph.decision.create — 대화 컨텍스트 10 턴
- context: 10 Turn, message 1KB, expected response ≤ 4KB.
- 검증: tokens.total ≤ model.max_tokens, confidence ∈ [0, 1], citations[] 직렬화 정상.

### MC-03 — langgraph.workflow.run → stage.execute → verify.run_chain 파이프라인
- workflow.run → 반환된 run_id 로 stage.execute 3회 → verify.run_chain 1회.
- 검증: run_id/stage_id 전파, verdict = Passed, 전체 elapsed ≤ 300s.

### MC-04 — embedding.encode (배치 32 텍스트)
- texts: 32 × 평균 500 bytes.
- 검증: embeddings.len() == 32, dimensions == model.dim, 총 응답 크기 < 4 MiB.

### MC-05 — embedding.store + 후속 embedding.encode 동일 모델 검증
- store(content, model="A") → encode(texts=[content], model="A") → 동일 벡터 확인 (normalize 적용).
- 검증: 코사인 유사도 ≥ 0.999.

### MC-06 — llm.generate + llm.record_invoke 연결
- generate → invoke_id 반환 → record_invoke(invoke_id) 호출 → event_id 반환.
- 검증: event_id 가 D2.1-D2 LogEventSchema 형식 준수, oc.* EventType.

### MC-07 — llm.rate_limit.get — 전체 모델
- model: None → entries 에 설정된 모든 모델 포함.
- 검증: 각 entry 의 remaining ≤ limit, reset_at 미래 시각.

### MC-08 — mcp.bridge.init → mcp.tools.discover → 재사용 (CC-B 검증)
- init → session_id → discover(session_id, refresh=false) → discover(session_id, refresh=true).
- 검증: 1회차 cached=false, 2회차 cached=true, 3회차 refresh → cached=false 재조회.

### MC-09 — mcp.bridge.health 주기 호출 (5s × 10)
- 10회 반복 호출, 각 타임아웃 5s.
- 검증: 모든 응답 status=Healthy, elapsed_ms < 1000 평균.

### MC-10 — method_not_found (LOCK-RT-03 범위 외)
- method: "langgraph.unknown", "embedding.flush" (가짜) 전송.
- 검증: -32601 응답, 프로세스 상태 Running 유지.

### MC-11 — invalid_params (필수 필드 누락)
- langgraph.workflow.run without workflow_id → -32602.
- embedding.encode with texts=[] → -32602 (empty batch 거부).
- 검증: error.data.missing_fields / invalid_fields 정보 포함.

### MC-12 — _lifecycle.initialize 실패 시 전체 spawn 실패 (§4.14)
- Python 측 initialize 응답을 일부러 지연 (6s > 5s timeout).
- 검증: spawn 단계 L0 Spawn Timeout 감지 → -32005 python_bridge_spawn_failed → 3회 재시도.

### MC-13 — 13 메서드 concurrent 혼합 부하
- 13 개 메서드 각 10 concurrent = 130 request, Semaphore(50) 초과.
- 검증: 드롭 0건, 모든 응답 성공, elapsed_ms 분포 수집.

### MC-14 — CC-A / CC-B 검증 (정본 매핑 준수)
- embedding.store 호출 시 Python 측이 store_memory 로 위임되었는지 확인 (내부 로그 grep).
- mcp.tools.discover 호출 시 Python 측이 execute_tool 을 호출하지 않음을 확인.

---

## §10. 구조화 로그 JSON (메서드 카탈로그 관점)

### 10.1 공통 이벤트 (rpc_protocol.md §9.2 재사용)

```json
{
  "timestamp": "2026-04-11T02:00:00.345Z",
  "level": "info",
  "logger": "bridge.python_manager.method_catalog",
  "event": "python_bridge_rpc_response",
  "trace_id": "01930e8e-0003-7000-8000-000000000003",
  "correlation_id": "req_1713480000_0003",
  "context": {
    "method": "langgraph.decision.create",
    "decision_id": "dec_xyz",
    "elapsed_ms": 8421,
    "tokens": {"prompt": 1200, "completion": 300, "total": 1500},
    "confidence": 0.92,
    "citations_count": 3,
    "tool_calls_count": 0,
    "result_size_bytes": 4096,
    "model": "claude-opus-4-6"
  },
  "recovery": null
}
```

### 10.2 메서드별 추가 context 필드

| 메서드 | 추가 context 필드 |
|---|---|
| langgraph.workflow.run | run_id, workflow_id |
| langgraph.stage.execute | run_id, workflow_id, stage_id |
| langgraph.decision.create | decision_id, tokens, citations_count, tool_calls_count, confidence |
| langgraph.node.dispatch | agent_id, node_id |
| langgraph.verify.run_chain | chain_id, verdict, confidence |
| embedding.encode | model, texts_count, dimensions, total_bytes |
| embedding.store | id, level, indexed |
| llm.generate | model, tokens, finish_reason |
| llm.record_invoke | invoke_id, record_id, cost_usd |
| llm.rate_limit.get | models_count |
| mcp.bridge.init | session_id, server_name, protocol |
| mcp.bridge.health | session_id, status, uptime_s, memory_mb |
| mcp.tools.discover | session_id, tools_count, cached |

---

## §11. LOCK 교차 점검표

| LOCK ID | 본 파일 준수 증거 | 검증 |
|---|---|---|
| LOCK-RT-03 | §3 13 메서드명 Part2 §6.2.2 정본 복제. 네임스페이스 4개 (langgraph(5)/embedding(2)/llm(3)/mcp(3)) 준수. | §3.1 |
| LOCK-RT-04 | §7 Rust struct 매트릭스 — 25 Serde 모델 T1-2 참조. 신규 struct 선언 없음 (T1-2 정본 위임). | §7 |
| LOCK-RT-11 | 모든 req/resp 가 rpc_protocol.md §2.5 공통 자료구조 재사용. JSON-RPC 2.0 필드 (jsonrpc, id, method, params, result, error) 준수. | §4.* |
| LOCK-RT-12 | 타임아웃 5s (mcp.bridge.health) = LOCK 수치만 인용. HC 15초 interval 은 rpc_protocol.md §6 참조. | §6 |
| LOCK-RT-13 | 본 파일은 메서드 층 — restart backoff 직접 참조 없음. rpc_protocol.md §6/§7.7 위임. | — |
| LOCK-RT-14 | §4 각 메서드 "가능한 error" → TauriError 매핑은 rpc_protocol.md §5.3 단일 정본 재사용. | §5.2 E1~E10 |
| LOCK-RT-15 | 본 파일은 메서드 스키마 중심 — stderr 분리 규정 재기재 없음. rpc_protocol.md §3.2 단일 정본. | — |

- **LOCK 재정의**: 없음.
- **LOCK 변경 필요**: 없음. (필요 시 `[LOCK_CHANGE_NEEDED]` — 본 파일 해당 없음.)
- **CONFLICT 기록**: CFL-RT-006 (CC-A embedding.store↔search_memory), CFL-RT-007 (CC-B mcp.tools.discover↔execute_tool), CFL-RT-008 (CC-C 상세명세 6 orphan → 보조 메서드 처리) — 전부 RESOLVED (CONFLICT_LOG v1.2, 2026-04-11). §2.3 참조.

---

## §12. 변경 이력

| 버전 | 일자 | 변경 내용 | 작성자 |
|---|---|---|---|
| v0.1 | 2026-04-11 | 초기 작성 (T1-3 step 1). §1~§11 신규. PRE-3 매핑 갭 6건 해소 (4.2/4.5/4.8/4.9/4.10/4.11 신규 DEFINED-HERE 스키마). CC-A/CC-B/CC-C 3건 CONFLICT_CANDIDATE 등재. 13 메서드 전수 req/resp 스키마 + 보조 6 메서드 §4.14. process_message L3 상세화 §5. FR-8 타임아웃 매핑표 §6. T1-1/T1-2/T1-4 경계 §7/§8. Phase 2 테스트 시나리오 14건 §9. | T1-3 Subagent |
| v0.2 | 2026-04-11 | 4-1 Deep Reverify — §2.3 `[CONFLICT_CANDIDATE CC-A/B/C]` 마커 3건을 `[CFL-RT-006/007/008 RESOLVED 2026-04-11]` 정규 참조로 정정 (CONFLICT_LOG v1.2 반영). §10 LOCK 교차 점검표의 CONFLICT_CANDIDATE 행을 RESOLVED 표기로 갱신. §4.5 stub 주의 문구에서 stale `[CONFLICT_CANDIDATE]` 토큰 제거. | Deep Reverify |

---

<!-- END OF DOCUMENT -->
