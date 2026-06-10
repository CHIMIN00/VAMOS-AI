# 4-1. Rust/Tauri Infrastructure 상세명세

> **Tier**: 4 - Infrastructure
> **Part2 상태**: PARTIAL (108 items covered in ~20 lines)
> **SOT 근거**: PHASE_B1, PHASE_B2, D2.1-D2~D4
> **Part2 위치**: V1-Phase 2 Infrastructure 섹션

---

## 개요

VAMOS AI의 데스크톱 애플리케이션 기반인 Rust/Tauri 인프라 계층. Part2에는 IPC 커맨드 이름 목록, Serde 모델 이름, JSON-RPC 메서드 이름이 나열되어 있으나, 함수 시그니처, 페이로드 스키마, 에러 처리, 프로세스 관리 프로토콜 등 구현 상세가 부재.

---

## 섹션 A: 72개 IPC 커맨드 핸들러

### A-1. Session 커맨드 (8개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 1 | `session_create` | `(config: SessionConfig) -> Result<SessionId, TauriError>` | 새 세션 생성, UUID v7 발급 |
| 2 | `session_load` | `(id: SessionId) -> Result<SessionState, TauriError>` | 저장된 세션 로드 |
| 3 | `session_save` | `(state: SessionState) -> Result<(), TauriError>` | 세션 상태 디스크 저장 |
| 4 | `session_delete` | `(id: SessionId) -> Result<(), TauriError>` | 세션 삭제 (soft delete) |
| 5 | `session_list` | `(filter: SessionFilter) -> Result<Vec<SessionSummary>, TauriError>` | 세션 목록 조회 |
| 6 | `session_export` | `(id: SessionId, format: ExportFormat) -> Result<Vec<u8>, TauriError>` | JSON/CBOR 내보내기 |
| 7 | `session_import` | `(data: Vec<u8>, format: ExportFormat) -> Result<SessionId, TauriError>` | 세션 가져오기 |
| 8 | `session_get_stats` | `(id: SessionId) -> Result<SessionStats, TauriError>` | 턴수, 토큰량, 시간 통계 |

### A-2. Conversation 커맨드 (8개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 9 | `conversation_send` | `(msg: UserMessage) -> Result<AssistantResponse, TauriError>` | 메시지 전송→응답 수신 |
| 10 | `conversation_stream` | `(msg: UserMessage) -> Result<StreamHandle, TauriError>` | 토큰 스트리밍 (§G-1 정합: Tauri IPC는 단일 메시지 단위이므로 invoke 는 StreamHandle 만 반환하고 토큰은 Tauri 이벤트 emit 로 전달; SSE-over-IPC 아님) |
| 11 | `conversation_retry` | `(turn_id: TurnId) -> Result<AssistantResponse, TauriError>` | 특정 턴 재시도 |
| 12 | `conversation_edit` | `(turn_id: TurnId, new_content: str) -> Result<(), TauriError>` | 사용자 턴 수정 |
| 13 | `conversation_branch` | `(turn_id: TurnId) -> Result<BranchId, TauriError>` | 대화 분기점 생성 |
| 14 | `conversation_get_history` | `(session_id: SessionId, range: Range) -> Result<Vec<Turn>, TauriError>` | 대화 이력 조회 |
| 15 | `conversation_clear` | `(session_id: SessionId) -> Result<(), TauriError>` | 대화 초기화 |
| 16 | `conversation_summarize` | `(session_id: SessionId) -> Result<String, TauriError>` | 대화 요약 생성 |

### A-3. Memory 커맨드 (7개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 17 | `memory_store` | `(record: MemoryRecord) -> Result<MemoryId, TauriError>` | 메모리 저장 (L0~L3 자동 분류) |
| 18 | `memory_retrieve` | `(query: MemoryQuery) -> Result<Vec<MemoryRecord>, TauriError>` | 메모리 검색 |
| 19 | `memory_update` | `(id: MemoryId, patch: MemoryPatch) -> Result<(), TauriError>` | 메모리 수정 |
| 20 | `memory_delete` | `(id: MemoryId) -> Result<(), TauriError>` | 메모리 삭제 |
| 21 | `memory_consolidate` | `() -> Result<ConsolidateReport, TauriError>` | L0→L1 승격, 중복 제거 |
| 22 | `memory_get_stats` | `() -> Result<MemoryStats, TauriError>` | 레벨별 항목 수, 용량 |
| 23 | `memory_export` | `(format: ExportFormat) -> Result<Vec<u8>, TauriError>` | 메모리 내보내기 |

### A-4. Search 커맨드 (6개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 24 | `search_hybrid` | `(query: SearchQuery) -> Result<Vec<SearchResult>, TauriError>` | BM25 + Vector 하이브리드 검색 |
| 25 | `search_semantic` | `(query: str, top_k: u32) -> Result<Vec<SearchResult>, TauriError>` | 벡터 유사도 검색 |
| 26 | `search_keyword` | `(query: str, filters: SearchFilters) -> Result<Vec<SearchResult>, TauriError>` | BM25 키워드 검색 |
| 27 | `search_rerank` | `(results: Vec<SearchResult>, query: str) -> Result<Vec<SearchResult>, TauriError>` | Cross-encoder 리랭킹 |
| 28 | `search_suggest` | `(prefix: str) -> Result<Vec<String>, TauriError>` | 자동완성 제안 |
| 29 | `search_index_rebuild` | `() -> Result<IndexStats, TauriError>` | 인덱스 재구축 |

### A-5. Agent 커맨드 (7개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 30 | `agent_start` | `(config: AgentConfig) -> Result<AgentId, TauriError>` | 에이전트 태스크 시작 |
| 31 | `agent_stop` | `(id: AgentId) -> Result<(), TauriError>` | 에이전트 중단 |
| 32 | `agent_get_state` | `(id: AgentId) -> Result<AgentState, TauriError>` | 현재 상태 조회 |
| 33 | `agent_list_active` | `() -> Result<Vec<AgentSummary>, TauriError>` | 활성 에이전트 목록 |
| 34 | `agent_send_feedback` | `(id: AgentId, feedback: Feedback) -> Result<(), TauriError>` | HITL 피드백 전달 |
| 35 | `agent_get_plan` | `(id: AgentId) -> Result<AgentPlan, TauriError>` | 에이전트 계획 조회 |
| 36 | `agent_override_step` | `(id: AgentId, step: StepOverride) -> Result<(), TauriError>` | 사용자 개입으로 스텝 변경 |

### A-6. Tool 커맨드 (6개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 37 | `tool_execute` | `(name: str, params: Value) -> Result<ToolResult, TauriError>` | 도구 실행 |
| 38 | `tool_list` | `() -> Result<Vec<ToolInfo>, TauriError>` | 사용 가능 도구 목록 |
| 39 | `tool_get_schema` | `(name: str) -> Result<Value, TauriError>` | 도구 JSON Schema 조회 |
| 40 | `tool_install` | `(source: ToolSource) -> Result<(), TauriError>` | MCP 도구 설치 |
| 41 | `tool_uninstall` | `(name: str) -> Result<(), TauriError>` | 도구 제거 |
| 42 | `tool_get_result` | `(execution_id: str) -> Result<ToolResult, TauriError>` | 비동기 실행 결과 조회 |

### A-7. Workflow 커맨드 (6개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 43 | `workflow_create` | `(def: WorkflowDef) -> Result<WorkflowId, TauriError>` | 워크플로우 정의 생성 |
| 44 | `workflow_run` | `(id: WorkflowId, input: Value) -> Result<WorkflowRunId, TauriError>` | 워크플로우 실행 |
| 45 | `workflow_pause` | `(run_id: WorkflowRunId) -> Result<(), TauriError>` | 실행 일시정지 |
| 46 | `workflow_resume` | `(run_id: WorkflowRunId) -> Result<(), TauriError>` | 실행 재개 |
| 47 | `workflow_get_status` | `(run_id: WorkflowRunId) -> Result<WorkflowStatus, TauriError>` | 실행 상태 조회 |
| 48 | `workflow_list` | `() -> Result<Vec<WorkflowSummary>, TauriError>` | 워크플로우 목록 |

### A-8. Settings 커맨드 (6개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 49 | `settings_get` | `(key: str) -> Result<Value, TauriError>` | 설정값 조회 |
| 50 | `settings_set` | `(key: str, value: Value) -> Result<(), TauriError>` | 설정값 저장 |
| 51 | `settings_get_all` | `() -> Result<VamosConfig, TauriError>` | 전체 설정 조회 |
| 52 | `settings_reset` | `(key: str) -> Result<(), TauriError>` | 기본값 복원 |
| 53 | `settings_export` | `() -> Result<String, TauriError>` | 설정 JSON 내보내기 |
| 54 | `settings_import` | `(json: str) -> Result<(), TauriError>` | 설정 가져오기 |

### A-9. File 커맨드 (6개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 55 | `file_read` | `(path: str) -> Result<FileContent, TauriError>` | 파일 읽기 (sandbox 검증) |
| 56 | `file_write` | `(path: str, content: Vec<u8>) -> Result<(), TauriError>` | 파일 쓰기 |
| 57 | `file_list` | `(dir: str, filter: FileFilter) -> Result<Vec<FileInfo>, TauriError>` | 디렉토리 목록 |
| 58 | `file_watch` | `(path: str) -> Result<WatchHandle, TauriError>` | 파일 변경 감시 |
| 59 | `file_upload` | `(data: Vec<u8>, name: str) -> Result<String, TauriError>` | 파일 업로드 |
| 60 | `file_get_metadata` | `(path: str) -> Result<FileMetadata, TauriError>` | 파일 메타데이터 |

### A-10. System 커맨드 (6개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 61 | `system_get_info` | `() -> Result<SystemInfo, TauriError>` | OS/CPU/RAM/GPU 정보 |
| 62 | `system_get_metrics` | `() -> Result<SystemMetrics, TauriError>` | CPU/RAM/디스크 사용량 |
| 63 | `system_check_updates` | `() -> Result<UpdateInfo, TauriError>` | 업데이트 확인 |
| 64 | `system_apply_update` | `(version: str) -> Result<(), TauriError>` | 업데이트 적용 |
| 65 | `system_get_logs` | `(filter: LogFilter) -> Result<Vec<LogEntry>, TauriError>` | 로그 조회 |
| 66 | `system_clear_cache` | `() -> Result<CacheClearReport, TauriError>` | 캐시 정리 |

### A-11. MCP 커맨드 (3개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 67 | `mcp_connect` | `(server: McpServerConfig) -> Result<ConnectionId, TauriError>` | MCP 서버 연결 |
| 68 | `mcp_disconnect` | `(conn_id: ConnectionId) -> Result<(), TauriError>` | MCP 서버 연결 해제 |
| 69 | `mcp_list_tools` | `(conn_id: ConnectionId) -> Result<Vec<ToolInfo>, TauriError>` | 연결된 서버 도구 목록 |

### A-12. Health 커맨드 (3개)

| # | 커맨드 | 시그니처 | 설명 |
|---|--------|----------|------|
| 70 | `health_check` | `() -> Result<HealthReport, TauriError>` | 전체 헬스체크 |
| 71 | `health_python_status` | `() -> Result<PythonProcessStatus, TauriError>` | Python 프로세스 상태 |
| 72 | `health_db_status` | `() -> Result<DbStatus, TauriError>` | 데이터베이스 연결 상태 |

### 공통 에러 타입

```rust
#[derive(Debug, Serialize, Deserialize)]
pub enum TauriError {
    NotFound { resource: String, id: String },
    ValidationError { field: String, message: String },
    PythonBridgeError { code: i32, message: String },
    IoError { path: String, message: String },
    Timeout { operation: String, elapsed_ms: u64 },
    PermissionDenied { action: String },
    InternalError { message: String },
}
```

---

## 섹션 B: 25개 Serde 모델 정의

> D2.1 스키마에 대응하는 Rust 구조체. `serde::Serialize`, `serde::Deserialize` derive 필수.

### B-1. Core 모델

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VamosConfig {
    pub version: String,                    // "1.0.0"
    pub language: String,                   // "ko" | "en"
    pub theme: Theme,                       // Light | Dark | System
    pub llm_provider: LlmProviderConfig,
    pub memory: MemoryConfig,
    pub search: SearchConfig,
    pub agent: AgentConfig,
    pub security: SecurityConfig,
    pub telemetry: TelemetryConfig,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionState {
    pub id: String,                         // UUID v7
    pub title: String,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
    pub turn_count: u32,
    pub total_tokens: u64,
    pub active_agent: Option<String>,
    pub metadata: HashMap<String, Value>,
    pub status: SessionStatus,              // Active | Paused | Archived
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConversationTurn {
    pub id: String,
    pub session_id: String,
    pub role: Role,                         // User | Assistant | System | Tool
    pub content: String,
    pub timestamp: DateTime<Utc>,
    pub tokens_used: u32,
    pub model: String,
    pub tool_calls: Option<Vec<ToolCall>>,
    pub metadata: TurnMetadata,
}
```

### B-2. Memory 모델

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MemoryRecord {
    pub id: String,
    pub level: MemoryLevel,                 // L0 | L1 | L2 | L3
    pub content: String,
    pub embedding: Option<Vec<f32>>,        // 768-dim or 1024-dim
    pub source: MemorySource,
    pub created_at: DateTime<Utc>,
    pub accessed_at: DateTime<Utc>,
    pub access_count: u32,
    pub importance: f32,                    // 0.0~1.0
    pub tags: Vec<String>,
    pub relations: Vec<MemoryRelation>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SearchResult {
    pub id: String,
    pub content: String,
    pub score: f32,                         // 0.0~1.0 정규화
    pub source: SearchSource,
    pub highlights: Vec<Highlight>,
    pub metadata: HashMap<String, Value>,
}
```

### B-3. Agent 모델

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AgentState {
    pub id: String,
    pub agent_type: String,
    pub status: AgentStatus,                // Idle | Planning | Executing | WaitingHITL | Done | Error
    pub current_step: u32,
    pub total_steps: Option<u32>,
    pub plan: Option<AgentPlan>,
    pub results: Vec<StepResult>,
    pub started_at: DateTime<Utc>,
    pub elapsed_ms: u64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ToolResult {
    pub tool_name: String,
    pub execution_id: String,
    pub status: ToolStatus,                 // Success | Error | Timeout | Cancelled
    pub output: Value,
    pub error: Option<String>,
    pub duration_ms: u64,
    pub tokens_used: Option<u32>,
}
```

### B-4. Workflow / Event / Config 모델

```rust
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WorkflowDef {
    pub id: String,
    pub name: String,
    pub description: String,
    pub steps: Vec<WorkflowStep>,
    pub triggers: Vec<WorkflowTrigger>,
    pub error_policy: ErrorPolicy,          // Abort | Retry(u32) | Skip | Fallback(String)
    pub timeout_ms: Option<u64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct EventLog {
    pub id: String,
    pub event_type: String,
    pub timestamp: DateTime<Utc>,
    pub source: String,
    pub payload: Value,
    pub severity: Severity,                 // Debug | Info | Warn | Error | Critical
}
```

> 나머지 모델: `LlmProviderConfig`, `MemoryConfig`, `SearchConfig`, `AgentConfig`, `SecurityConfig`, `TelemetryConfig`, `SessionFilter`, `SessionSummary`, `SessionStats`, `MemoryQuery`, `MemoryPatch`, `FileContent`, `SystemInfo`, `HealthReport` — 각각 3~8개 필드로 구성. D2.1 스키마 Section 3~5 참조.

---

## 섹션 C: 13개 Python-Rust JSON-RPC 메서드

> Rust → Python: JSON-RPC 2.0 over stdin/stdout. 각 메서드의 request/response 스키마.

| # | 메서드 | Request Params | Response Result | 설명 |
|---|--------|----------------|-----------------|------|
| 1 | `initialize` | `{ config: VamosConfig }` | `{ status: "ok", capabilities: string[] }` | Python 엔진 초기화 |
| 2 | `process_message` | `{ session_id, message, context: Turn[] }` | `{ response: str, tool_calls?: ToolCall[], tokens: u32 }` | 메시지 처리 (핵심) |
| 3 | `search_memory` | `{ query: str, top_k: u32, filters?: {} }` | `{ results: SearchResult[] }` | 메모리 검색 |
| 4 | `execute_tool` | `{ tool_name: str, params: {} }` | `{ result: ToolResult }` | 도구 실행 |
| 5 | `store_memory` | `{ content: str, level: str, tags: str[] }` | `{ id: str }` | 메모리 저장 |
| 6 | `consolidate_memory` | `{}` | `{ promoted: u32, merged: u32, deleted: u32 }` | 메모리 통합 |
| 7 | `start_agent` | `{ agent_type: str, task: str, config: {} }` | `{ agent_id: str }` | 에이전트 시작 |
| 8 | `get_agent_state` | `{ agent_id: str }` | `{ state: AgentState }` | 에이전트 상태 조회 |
| 9 | `stop_agent` | `{ agent_id: str }` | `{ status: "stopped" }` | 에이전트 중단 |
| 10 | `run_workflow` | `{ workflow_id: str, input: {} }` | `{ run_id: str }` | 워크플로우 실행 |
| 11 | `get_embeddings` | `{ texts: str[], model?: str }` | `{ embeddings: float[][] }` | 임베딩 벡터 생성 |
| 12 | `health_check` | `{}` | `{ status: "healthy", uptime_s: u64, memory_mb: u32 }` | 헬스체크 |
| 13 | `shutdown` | `{}` | `{ status: "shutting_down" }` | 정상 종료 |

### JSON-RPC 통신 프로토콜

```
[Rust Process]              [Python Process]
     |                            |
     |-- JSON-RPC Request -->     |  (stdin으로 전송, \n 구분)
     |                            |-- 처리 (async)
     |<-- JSON-RPC Response --    |  (stdout으로 응답)
     |                            |
     |   stderr → 로그 전용        |  (stderr는 로그 파이프)
```

- **직렬화**: `serde_json` (Rust) ↔ `orjson` (Python)
- **타임아웃**: 메서드별 개별 설정 (process_message: 120s, 나머지: 30s)
- **배치**: `process_message` 외에는 배치 요청 가능 (`[req1, req2, ...]`)

---

## 섹션 D: Python 프로세스 관리

### D-1. Spawn 프로토콜

```
1. Rust: 임베딩 venv 경로 확인 (settings.python_venv_path)
2. Rust: Command::new(python_path).args(["--json-rpc"]).spawn()
3. Rust: stdout 첫 줄 대기 → {"jsonrpc":"2.0","method":"_ready","params":{"pid":12345,"capabilities":[...]}} (JSON-RPC 2.0 notification, rpc_protocol §3.2 정본)
4. Rust: initialize RPC 호출
5. 정상 → 상태 = Running
6. 5초 내 ready 미수신 → 재시도 (최대 3회)
```

### D-2. Healthcheck 프로토콜

- **주기**: 15초마다 `health_check` RPC 호출
- **타임아웃**: 5초 내 응답 없으면 unhealthy 카운트 +1
- **임계치**: unhealthy 3회 연속 → 프로세스 재시작
- **메트릭 수집**: RSS 메모리, CPU%, 처리 큐 길이

### D-3. Restart Policy

| 조건 | 동작 | 최대 재시도 | 백오프 |
|------|------|------------|--------|
| 비정상 종료 (exit code != 0) | 즉시 재시작 | 5회 | 1s, 2s, 4s, 8s, 16s |
| OOM (exit code 137) | 메모리 제한 상향 후 재시작 | 3회 | 5s 고정 |
| Healthcheck 실패 | SIGTERM → 5s 대기 → SIGKILL → 재시작 | 3회 | 2s, 4s, 8s |
| 사용자 명시적 중지 | 재시작 안 함 | - | - |

### D-4. Stderr 분리

- Python stderr → `logs/python_engine.log` 로테이션 저장
- 로그 레벨: `VAMOS_LOG_LEVEL` 환경변수 (기본 INFO)
- 로테이션: 10MB 또는 7일, 최대 5개 파일 보관
- 에러 감지: stderr에 `CRITICAL` 또는 `FATAL` 포함 시 Rust 측 알림 이벤트 발생

### D-5. 리소스 관리

- **메모리 제한**: 기본 2GB, 설정 가능 (`settings.python_max_memory_mb`)
- **CPU 친화도**: 기본 OS 스케줄러 위임, 옵션으로 코어 고정 가능
- **GPU**: Python 측에서 CUDA/MPS 자동 감지, Rust에 capability 보고
- **임시 파일**: `{app_data}/tmp/python/` 하위, 세션 종료 시 정리

---

## E. IPC 에러 핸들링 매트릭스

### E-1 커맨드별 에러 매핑 (대표 패턴)

| 커맨드 카테고리 | 주요 에러 | 복구 전략 | 사용자 노출 |
|---------------|----------|----------|-----------|
| Session (A-1) | NotFound, Timeout | 세션 재생성 제안, 자동 재시도 1회 | "세션을 찾을 수 없습니다" |
| Memory (A-3) | IoError, Timeout | 로컬 캐시 폴백, 비동기 재시도 | "일시적 저장 오류" |
| Agent (A-5) | PythonBridgeError, Timeout | Python 프로세스 재시작 후 재시도 | "에이전트 연결 중..." |
| Tool (A-6) | PermissionDenied, ValidationError | 권한 확인 프롬프트, 입력 검증 메시지 | 구체적 권한/검증 안내 |
| MCP (A-11) | Timeout, InternalError | Circuit Breaker 패턴 (3회 실패 → OPEN) | "외부 도구 일시 불가" |
| Health (A-12) | InternalError | 로그 기록 + 관리자 알림 | 비노출 (백그라운드) |

### E-2 에러 우선순위
1. **PythonBridgeError** → 즉시 프로세스 상태 확인 → 재시작 시도
2. **Timeout** → 현재 작업 취소 → 사용자에게 재시도 제안
3. **PermissionDenied** → 차단 + 감사 로그 기록
4. **ValidationError** → 요청 거부 + 구체적 필드 오류 반환
5. **NotFound** → 리소스 유효성 검사 → 대안 제안
6. **InternalError** → 스택트레이스 로깅 + 일반 오류 메시지

## F. Python 프로세스 상태 머신

### F-1 상태 전이

```
[Idle] ──(spawn 요청)──→ [Spawning]
   ↑                        │
   │                    (5초 내 ready)
   │                        ↓
   │                    [Running] ←──(healthcheck OK)──┐
   │                        │                          │
   │                  (healthcheck 3× fail)            │
   │                        ↓                          │
   │                    [Unhealthy]                     │
   │                        │                          │
   │                  (restart 시도)                     │
   │                        ↓                          │
   │                    [Restarting] ──(성공)──→────────┘
   │                        │
   │                  (5회 실패)
   │                        ↓
   └──(수동 개입)─── [Dead]
```

### F-2 동시성 가드
- **Mutex 잠금**: 스폰/재시작 작업은 단일 스레드에서만 실행 (Tokio Mutex)
- **상태 원자적 전이**: AtomicU8로 상태 플래그 관리, CAS(Compare-And-Swap) 연산
- **진행 중 요청 처리**: Unhealthy 전환 시 대기 중 요청에 PythonBridgeError 반환 (drain 패턴)
- **좀비 방지**: 프로세스 그룹 ID 기록, SIGKILL 후 30초 타이머로 좀비 스캔

## G. IPC 전송 계층

### G-1 메시지 프레이밍
- **직렬화**: JSON (Tauri invoke 기본)
- **최대 페이로드**: 10MB (LOCK-MCP-01과 통일)
- **인코딩**: UTF-8
- **구분자**: Tauri IPC는 단일 메시지 단위 (스트리밍 없음)

### G-2 백프레셔
- **프론트엔드 큐**: 최대 100 동시 요청 (초과 시 사용자에게 "처리 중" 표시)
- **백엔드 큐**: Rust 측 tokio::sync::Semaphore(50) — 동시 Python 요청 제한
- **타임아웃 계층**: invoke 30s (기본) / process_message 120s (LLM) / healthcheck 15s
- **드롭 정책**: 큐 포화 시 가장 오래된 비-LLM 요청 우선 드롭, LLM 요청은 대기
