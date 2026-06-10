# rpc_protocol.md — JSON-RPC 2.0 Wire Protocol & python_manager.rs Internals

> **도메인**: 4-1_Rust-Tauri-Infrastructure (#14)
> **서브폴더**: 03_python-bridge
> **세션**: T1-3 (Phase 1)
> **작성일**: 2026-04-11
> **상태**: DRAFT (Phase 1 T1-3 step 1 산출물)
> **LOCK**: LOCK-RT-11 (JSON-RPC 2.0 over stdin/stdout, `\n` 구분), LOCK-RT-15 (stderr 로그 분리), LOCK-RT-03 (13개 메서드명), LOCK-RT-04 (Rust 핵심 모듈 4개)
> **해소 대상**: ISS-02 (13개 req/resp 스키마 — method_catalog.md 협조), ISS-04 (python_manager.rs 내부 구조 + 인터페이스)

---

## §1. 교차 참조 (AUTHORITY_CHAIN)

### 1.1 상위 정본 체인

```
BASE 1.3 → PLAN 3.0 → DESIGN 2.0 (D2.0-04 INFRA_CORE)
  ├── D2.1-D4 v3.0.0 (INFRA CORE Schema — REF-only)
  ├── PHASE_B2 §4.3 (python_manager.rs, config.rs 인터페이스 + JSON-RPC stdin/stdout 프로토콜 LOCK)
  └── Part2 §6.2.2 (JSON-RPC 13개 메서드명 namespace.action LOCK)
        └── sot 2/ 상세명세 §B (Serde 모델) / §C (13개 req/resp 스키마) / §D (프로세스 관리)
              └── 03_python-bridge/ (본 파일 + method_catalog.md)
```

### 1.2 LOCK 직접 참조

| LOCK ID | 내용 | 정본 | 본 파일 적용 섹션 |
|--------|------|-----|--------------------|
| LOCK-RT-03 | 13개 JSON-RPC 메서드명 (`langgraph.*`/`embedding.*`/`llm.*`/`mcp.*`) | Part2 §6.2.2 | §5(에러 커스텀 범위) · §10 · method_catalog.md |
| LOCK-RT-04 | Rust 핵심 모듈 4개 (ipc_protocol.rs, python_manager.rs, config.rs, serde 25개) | Part2 §6.2.3 / PHASE_B2 §4.3 | §7 python_manager.rs 내부 구조 |
| LOCK-RT-11 | JSON-RPC 2.0 over stdin/stdout, `\n` 구분, serde_json↔orjson | PHASE_B2 §4.3 / Part2 V0-STEP-3 | §2/§3 |
| LOCK-RT-12 | HC 15초 간격 / 5초 타임아웃 / 3회 연속 실패 | 상세명세 §D-2 | §6 FR-8 타임아웃 계층 |
| LOCK-RT-13 | Restart backoff 1s→2s→4s→8s→16s / OOM 5s 고정 / HC 2s→4s→8s | 상세명세 §D-3 | §6 FR-8 타임아웃 계층 |
| LOCK-RT-14 | TauriError enum 7 variant | 상세명세 §A | §5 에러 매핑 |
| LOCK-RT-15 | stderr 로그 분리 (stdout=JSON-RPC 전용, stderr=로그 전용) | PHASE_B2 / Part2 V0-STEP-3 M-5 | §3 stdout/stderr 분리 |

### 1.3 교차 문서 참조

- **CONFLICT_LOG**:
  - CFL-RT-002 RESOLVED — Part2 namespace.action vs 상세명세 verb_noun. Part2 LOCK 채택, 상세 스키마는 sot 2/ 정본. method_catalog.md §2에 PRE-3 해소 결과 반영.
- **PHASE_B2 §4.3**: python_manager.rs (subprocess 생명주기 관리) + ipc_protocol.rs (JSON-RPC over stdin/stdout) 인터페이스 정본.
- **Part2 §6.2.2**: 13개 메서드명 나열 (4683~4696, 897~910 두 곳 출현).
- **Part2 §6.2.3**: Rust 핵심 모듈 4개 (ipc_protocol/python_manager/config/serde 25개).
- **상세명세 §B**: 25개 Serde 모델 (VamosConfig, Turn, SearchResult, ToolResult, AgentState, Decision 등) — method_catalog.md §7에서 재참조.
- **상세명세 §C**: 13개 verb_noun 스키마 (initialize, process_message, search_memory, ...) — method_catalog.md §2 PRE-3 매핑 근거.
- **상세명세 §D-1~D-5**: Spawn/HC/Restart/Stderr/리소스 — §7/§6에서 참조.
- **상세명세 §F-2**: 동시성 가드 (Tokio Mutex, AtomicU8 상태, drain 패턴) — §7 구현 근거.
- **상세명세 §G-1**: 메시지 프레이밍 — §3에서 8 MiB 보강.
- **_index.md**: `[PRE-3 완료 후 매핑 갭 6건 해소 갱신]` 마커 존재 (§92~93). **본 step에서는 _index.md 미수정** — step 5 대상. method_catalog.md §2에 해소 결과를 기재하여 step 5가 복사만 하면 되도록 함.

---

## §2. JSON-RPC 2.0 규격 준수

### 2.1 기본 원칙

- **프로토콜 버전**: JSON-RPC 2.0 (LOCK-RT-11)
- **필수 필드**:
  - Request: `jsonrpc: "2.0"`, `id`, `method`, `params`
  - Response (성공): `jsonrpc: "2.0"`, `id`, `result`
  - Response (실패): `jsonrpc: "2.0"`, `id`, `error: { code, message, data? }`
- **Notification**: 본 브릿지는 **양방향 요청/응답만 지원**. Notification (id 없는 요청) 사용 금지 — 모든 요청은 id를 포함하여 correlation map 추적 대상이 된다.
- **배치 요청**: Part2 §B.2 + 상세명세 §C 정본에 따라 **`process_message` 외에는 배치 요청 가능**. 단, 초기 Phase 1 구현은 단일 요청만 지원, 배치는 Phase 2에서 활성화 (§8 시나리오 TC-08).
- **직렬화**: Rust `serde_json` ↔ Python `orjson` (LOCK-RT-11).

### 2.2 Request 표준 형식

```json
{
  "jsonrpc": "2.0",
  "id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
  "method": "langgraph.workflow.run",
  "params": {
    "workflow_id": "wf_plan_execute",
    "input": { "query": "Summarize today's tasks" },
    "_meta": {
      "trace_id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
      "correlation_id": "req_1713480000_0001",
      "issued_at": "2026-04-11T02:00:00.123456Z",
      "deadline_ms": 120000
    }
  }
}
```

### 2.3 Response 표준 형식 (성공)

```json
{
  "jsonrpc": "2.0",
  "id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
  "result": {
    "run_id": "run_abc123",
    "_meta": {
      "trace_id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
      "correlation_id": "req_1713480000_0001",
      "completed_at": "2026-04-11T02:00:00.456789Z",
      "elapsed_ms": 333
    }
  }
}
```

### 2.4 Response 표준 형식 (실패)

```json
{
  "jsonrpc": "2.0",
  "id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
  "error": {
    "code": -32001,
    "message": "python_bridge_timeout",
    "data": {
      "trace_id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
      "method": "langgraph.workflow.run",
      "elapsed_ms": 120050,
      "deadline_ms": 120000,
      "recovery_hint": "retry_with_smaller_payload",
      "upstream_error": null
    }
  }
}
```

### 2.5 Rust 공통 자료구조 선정의 (method_catalog.md 재사용)

본 절에서 정의된 `RpcRequest<P>`, `RpcResponse<R>`, `RpcError`, `RpcMeta` 는 method_catalog.md §4의 13개 메서드 전수 스키마에서 **단일 출처**로 재사용된다.

```rust
// crates/app/src/bridge/rpc_protocol.rs (LOCK-RT-04 ipc_protocol.rs 내부)

use serde::{Deserialize, Serialize};
use serde_json::Value;
use uuid::Uuid;
use chrono::{DateTime, Utc};

/// JSON-RPC 2.0 request envelope — params 타입은 메서드별 struct (method_catalog.md §4).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RpcRequest<P> {
    pub jsonrpc: JsonRpcVersion,          // "2.0" (직렬화 검증)
    pub id: String,                        // UUID v7
    pub method: String,                    // LOCK-RT-03 13개 중 하나
    pub params: P,                         // 메서드별 params struct
}

/// JSON-RPC 2.0 response envelope — 성공 또는 에러 (둘 중 하나).
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RpcResponse<R> {
    pub jsonrpc: JsonRpcVersion,
    pub id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result: Option<R>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<RpcError>,
}

/// JSON-RPC 2.0 error object — code + message + data.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RpcError {
    pub code: i32,                         // §5 에러 코드 범위
    pub message: String,                    // 영문 식별자 (예: "python_bridge_timeout")
    #[serde(skip_serializing_if = "Option::is_none")]
    pub data: Option<RpcErrorData>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RpcErrorData {
    pub trace_id: String,
    pub method: String,
    pub elapsed_ms: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub deadline_ms: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub recovery_hint: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub upstream_error: Option<Value>,
}

/// 공통 메타 — params._meta / result._meta 양쪽에 주입.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RpcMeta {
    pub trace_id: String,                   // UUID v7 (§4)
    pub correlation_id: String,              // 호출 체인 추적
    pub issued_at: DateTime<Utc>,            // RFC3339
    #[serde(skip_serializing_if = "Option::is_none")]
    pub completed_at: Option<DateTime<Utc>>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub elapsed_ms: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub deadline_ms: Option<u64>,
}

/// "2.0" 고정 직렬화 가드.
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
#[serde(try_from = "String", into = "String")]
pub struct JsonRpcVersion;

impl From<JsonRpcVersion> for String { fn from(_: JsonRpcVersion) -> Self { "2.0".into() } }
impl TryFrom<String> for JsonRpcVersion {
    type Error = &'static str;
    fn try_from(s: String) -> Result<Self, &'static str> {
        if s == "2.0" { Ok(JsonRpcVersion) } else { Err("jsonrpc must be \"2.0\"") }
    }
}
```

> method_catalog.md §4는 본 `RpcRequest<P>`/`RpcResponse<R>` 를 그대로 사용하고 P/R 타입만 메서드별로 지정한다. 동일 자료구조 중복 선언 금지 — 본 파일이 단일 정본.

---

## §3. 전송 프로토콜 (stdin/stdout 프레이밍)

### 3.1 프레이밍 규칙 (LOCK-RT-11)

| 속성 | 값 | 근거 |
|-----|----|------|
| 전송 | Rust→Python: child.stdin.write_all / Python→Rust: child.stdout.read_line | PHASE_B2 §4.3 |
| 라인 구분자 | `\n` (single LF, 0x0A) | LOCK-RT-11 |
| 인코딩 | UTF-8 (BOM 금지) | LOCK-RT-11 |
| 직렬화 형식 | 단일 라인 minified JSON (pretty-print 금지, 내부 `\n` 금지) | LOCK-RT-11 세부 규정 |
| 최대 라인 크기 | **4 MiB** (4,194,304 바이트) 기본값. `settings.python_bridge_max_line_bytes`로 조정 가능. 초과 시 request 거부 `-32600 invalid_request` / response 수신 시 `python_bridge_oversized` 에러 | 본 문서 DEFINED-HERE (상세명세 §G-1의 Tauri IPC 10MB LOCK-MCP-01 과는 별개 — Python 브릿지 내부 한계. FR-3 메시지 프레이밍과 정렬) |
| 압축 | 미사용 (plain JSON) | Phase 1 |
| 스트리밍 | 미지원 — 단일 request/response per line. 스트림 의사 지원은 Phase 2 (`_stream_chunk` 이벤트 채널로 분리, §8 TC-10) |

### 3.2 stdout / stderr 분리 (LOCK-RT-15)

```
+-------------+          (JSON-RPC lines, \n 구분)         +---------------+
|   Rust      | <---------------- stdout  ---------------- |    Python     |
|             |                                             |               |
|             | ----------------  stdin  -----------------> |               |
|             |                                             |               |
|             | <---------------- stderr ----------------  |               |
+-------------+      (structlog lines → log collector)     +---------------+
```

- **stdout = JSON-RPC 전용**: Python 측은 `sys.stdout.write(json + "\n")` 후 즉시 flush. `print()` 금지 (버퍼링/개행 이슈).
- **stderr = 로그 전용**: Python `structlog` → stderr. Rust 측은 별도 `tokio::process::ChildStderr` 를 `log_collector` 태스크로 전달하여 `logs/python_engine.log` 에 기록 (상세명세 §D-4: 10MB 로테이션, 7일/5파일).
- **혼선 금지** (R-14-6): Python 측에서 `logging.basicConfig(stream=sys.stdout)` 등 stdout 로 로그가 유입되면 JSON-RPC 파서가 라인 단위로 파싱 실패하여 `python_bridge_malformed_frame` 에러 발생. Python 부트스트랩 시 `sys.stdout = sys.__stdout__` 초기화 + structlog 기본 처리기 stderr 고정.
- **Ready 라인 예외**: Python 엔진 기동 시 최초 한 줄 `{"jsonrpc":"2.0","method":"_ready","params":{"pid":12345,"capabilities":[...]}}` 을 stdout 으로 송출 (상세명세 §D-1 4번 절차). Rust 측 spawn_protocol 은 이 라인을 JSON-RPC notification 으로 해석하여 Running 전환 신호로 사용.

### 3.3 Flush 및 버퍼링 규칙

- **Rust 측 stdin write**: `tokio::io::AsyncWriteExt::write_all` + `flush()` — 쓰기 단위는 "한 줄 JSON + `\n`". 부분 write 허용 안 함 (한 줄 단위 원자 write).
- **Python 측 stdout**: `sys.stdout.buffer.write(json_bytes + b"\n")` + `sys.stdout.flush()`. Python `-u` (unbuffered) 옵션을 spawn 시 기본 활성화.
- **Rust 측 stdout read**: `tokio::io::BufReader::new(child.stdout).lines()` — 라인 스트림으로 소비. 라인당 4 MiB 상한 초과 시 조기 close + `-32002 python_bridge_oversized`.

### 3.4 프레임 에러 복구

| 상황 | 탐지 | 복구 |
|-----|-----|-----|
| JSON 파싱 실패 | `serde_json::from_str` Err | 라인 드롭 + `-32700 parse_error` + trace 로그. 2회 연속 발생 시 프로세스 재시작. |
| id 없는 응답 | `v.get("id").is_none()` 이며 `method != "_ready"` | 드롭 + debug 로그 (unsolicited notification). `_ready` 는 §3.2 예외. |
| 미지의 id | correlation map 조회 실패 (응답의 id가 맵에 없음) | 드롭 + warn 로그 (이미 타임아웃된 요청일 수 있음). |
| partial read | 라인 종료 없이 EOF | 프로세스 사망 판정 → spawn_protocol restart 트리거. |
| 라인 > 4 MiB | BufReader 내부 카운터 | 스트림 close + restart. |

---

## §4. 헤더 / 메타 필드

모든 요청/응답의 `params._meta` / `result._meta` / `error.data` 는 공통 메타 필드를 포함한다. 메타는 `params`/`result` 스키마의 예약 필드로서 **필수 (required)** 이다.

| 필드 | 타입 | 생성 주체 | 설명 |
|-----|-----|----------|-----|
| `trace_id` | String (UUID v7) | Rust (요청 생성 시) | 분산 추적 ID. 동일 사용자 요청 체인 전체에 유지. IPC→JSON-RPC 경계에서 상속 (T1-1). |
| `correlation_id` | String | Rust (요청 생성 시) | `req_{epoch_ms}_{seq4}` 형식. 단일 RPC 호출의 고유 식별자. Rust↔Python 로그 상관. |
| `issued_at` | String (RFC3339 UTC) | Rust | 요청 생성 시각. |
| `completed_at` | String (RFC3339 UTC) | Python (응답 시) | 응답 생성 시각. |
| `elapsed_ms` | u64 | Rust (수신 시 계산) | `now() - issued_at` 밀리초. 모니터링 메트릭 원천. |
| `deadline_ms` | u64 | Rust | 메서드별 타임아웃 (§6) 값. Python 측이 초과 감지 시 조기 취소 가능. |

### 4.1 UUID v7 선택 근거

- UUID v7 은 시간순 정렬 가능 (ms precision timestamp + random tail) → correlation map(§7.4)에서 O(log N) BTree 조회 + 오래된 엔트리 일괄 제거(range query)에 유리.
- crate: `uuid = { version = "1", features = ["v7", "serde"] }`. Rust 1.80 이상 지원.
- fallback: v7 미사용 환경에서는 v4 허용 (단 correlation map 일괄 청소 효율 저하).

### 4.2 trace_id 전파 규칙 (T1-1 IPC 경계)

```
React UI (Tauri invoke)
  └─ trace_id 없음
       ↓ (Rust IPC 핸들러가 신규 UUID v7 발급)
Rust ipc_protocol.rs
  └─ trace_id = Uuid::now_v7()
       ↓ (python_manager.rs 에 그대로 전달)
Rust python_manager.rs (본 파일)
  └─ params._meta.trace_id = 상속
       ↓ (stdin 송출)
Python rpc/server.py
  └─ structlog.contextvars.bind(trace_id=...) — 모든 로그에 자동 첨부
       ↓ (stdout 응답 + stderr 로그)
Rust response 수신
  └─ result._meta.trace_id 검증 (요청과 동일한지 확인)
```

---

## §5. 에러 코드 체계

### 5.1 JSON-RPC 2.0 표준 에러 (-32700 ~ -32603)

| 코드 | 이름 | 원인 | TauriError 매핑 (LOCK-RT-14) |
|-----|------|-----|------|
| -32700 | parse_error | stdout 라인의 JSON 파싱 실패 | `PythonBridgeError` |
| -32600 | invalid_request | JSON은 유효하나 JSON-RPC 필수 필드 누락/형식 오류 | `ValidationError` |
| -32601 | method_not_found | method 필드가 LOCK-RT-03 13개 중 어디에도 속하지 않음 | `ValidationError` |
| -32602 | invalid_params | params 스키마 검증 실패 (method_catalog.md §4 참조) | `ValidationError` |
| -32603 | internal_error | Python 측 uncaught exception (정의되지 않은 에러) | `InternalError` |

### 5.2 커스텀 에러 범위 (-32000 ~ -32099) — DEFINED-HERE

> LOCK-RT-14 TauriError 7 variant 매핑 필수. FailureCodeRegistry(LOCK-RT-07, 48건) 중 Python 브릿지 관련 코드는 T1-4 에서 매핑 (본 파일에서는 RPC 층 에러만 정의).

| 코드 | 이름 | 원인 | TauriError | 복구 | 메서드 범위 |
|-----|------|-----|-----|------|---|
| -32000 | python_bridge_unhealthy | HC 3회 연속 실패 판정 후 도착한 요청 | `PythonBridgeError` | Restart 후 재시도 (1회) | 전체 |
| -32001 | python_bridge_timeout | `deadline_ms` 초과 (§6) | `Timeout` | 사용자 재시도 / 캐시 폴백 | 전체 |
| -32002 | python_bridge_oversized | 라인 크기 > 4 MiB | `ValidationError` | 입력 축소 | params 대용량 메서드 |
| -32003 | python_bridge_oom | Python 측 OOM (exit 137) 탐지 | `PythonBridgeError` | Restart + backoff 5s | 전체 |
| -32004 | python_bridge_crash | Python 프로세스 비정상 종료 (exit != 0, 137 제외) | `PythonBridgeError` | Restart (LOCK-RT-13 backoff) | 전체 |
| -32005 | python_bridge_spawn_failed | Spawn 단계 실패 (venv 경로, 권한, 실행 파일 없음) | `PythonBridgeError` | 3회 재시도 후 Dead | Spawn 시 |
| -32006 | python_bridge_malformed_frame | stdout 라인이 JSON-RPC 규격 미준수 | `PythonBridgeError` | 2회 누적 시 Restart | 전체 |
| -32010 | model_not_found | `langgraph.*` / `llm.*` 메서드에서 모델 ID 미존재 | `NotFound` | 사용자에게 설정 제안 | langgraph/llm |
| -32011 | embedding_failure | `embedding.*` 메서드 내부 실패 (모델 로드 실패, GPU OOM 등) | `InternalError` | 1회 재시도 후 실패 | embedding.* |
| -32012 | mcp_error | `mcp.*` 메서드 상류 MCP 서버 오류 | `InternalError` | Circuit Breaker (3회) | mcp.* |
| -32013 | rate_limit_exceeded | `llm.generate` / `llm.record_invoke` 레이트리밋 초과 | `PermissionDenied` | 대기 후 재시도 | llm.* |
| -32020 | workflow_cancelled | 사용자 취소 또는 deadline 직전 Python 측이 정리 완료 | `Timeout` | — | langgraph.* (workflow/stage/decision/node/verify) |
| -32021 | permission_denied | Python 측 Tool 실행 권한 거부 | `PermissionDenied` | 사용자 승인 요청 | mcp.*, langgraph.node.* |

### 5.3 JSON-RPC error ↔ TauriError 매핑 테이블 (LOCK-RT-14)

```rust
impl From<RpcError> for TauriError {
    fn from(e: RpcError) -> Self {
        match e.code {
            -32700 | -32000 | -32003..=-32006 => TauriError::PythonBridgeError(e.message),
            -32600 | -32601 | -32602 | -32002 => TauriError::ValidationError(e.message),
            -32001 | -32020                  => TauriError::Timeout(e.message),
            -32010                           => TauriError::NotFound(e.message),
            -32013 | -32021                  => TauriError::PermissionDenied(e.message),
            _                                => TauriError::InternalError(e.message),
        }
    }
}
```

---

## §6. 타임아웃 정의 (FR-8 타임아웃 캐스케이드)

> FR-8: Spawn / HC / RPC / Graceful Shutdown 타임아웃 계층 구조. 본 파일은 RPC 층 기본값을 정의하고, 메서드별 override 값은 method_catalog.md §6 매핑표에서 정의.

### 6.1 타임아웃 계층

```
┌────────────────────────────────────────────────────────────────────┐
│  L0: Spawn Timeout — 5s × 3 retry (LOCK-RT-11 유래 / 상세명세 §D-1) │
│       |                                                               │
│       v (Running 상태 전환)                                           │
│  L1: HC Timeout — 15s interval / 5s per-call / 3 fail → restart       │
│       (LOCK-RT-12, 상세명세 §D-2)                                     │
│       |                                                               │
│       v (정상 운영)                                                   │
│  L2: RPC Timeout — 120s (process_message 핵심) / 30s (기타 11개) /     │
│       5s (health_check) / 10s (shutdown)                              │
│       (§B.2 타임아웃 열 정본 + 메서드별 override: method_catalog §6)    │
│       |                                                               │
│       v (종료 또는 에러)                                              │
│  L3: Graceful Shutdown Timeout — 5s                                   │
│       SIGTERM → drain pending requests → SIGKILL fallback             │
│       (상세명세 §D-3 "SIGTERM → 5s 대기 → SIGKILL")                   │
└────────────────────────────────────────────────────────────────────┘
```

### 6.2 타임아웃 수치 정본

| 계층 | 수치 | 정본 | override 경로 |
|-----|-----|------|-----|
| Spawn attempt | 5s | 상세명세 §D-1 | `settings.python_bridge_spawn_timeout_ms` |
| Spawn retry | 3회 | 상세명세 §D-1 | `settings.python_bridge_spawn_retry` |
| HC interval | 15s | LOCK-RT-12 | 불가 (LOCK) |
| HC per-call | 5s | LOCK-RT-12 | 불가 (LOCK) |
| HC fail threshold | 3회 | LOCK-RT-12 | 불가 (LOCK) |
| RPC default | 30s | 계획서 §B.2 | 메서드별 override (method_catalog §6) |
| RPC process_message | 120s | 계획서 §B.2 / 상세명세 §C | 불가 (핵심 메서드) |
| RPC health_check | 5s | 계획서 §B.2 | 불가 |
| RPC shutdown | 10s | 계획서 §B.2 | 불가 |
| Graceful shutdown | 5s | 상세명세 §D-3 | `settings.python_bridge_graceful_shutdown_ms` |

### 6.3 deadline_ms 계산 및 전파

```
issued_at (T0)
   + RPC timeout (method별)
   = deadline_ms (Python 측에 전달)

Python 측:
   if now() >= deadline_ms - 500ms (500ms 예비 버퍼):
       early_cancel() → -32020 workflow_cancelled 응답

Rust 측:
   tokio::time::timeout(RPC timeout + 1s grace, response_rx.recv())
     Err(_) → -32001 python_bridge_timeout (Python 응답 없음)
     Ok(RpcError(-32020)) → Timeout (Python 측 취소)
```

---

## §7. python_manager.rs 내부 구조 (ISS-04)

### 7.1 모듈 경계 (LOCK-RT-04)

```
src/bridge/
  ├── ipc_protocol.rs       (LOCK-RT-04)  — T1-1 IPC 경계와 접점
  │     └─ Tauri invoke → RpcRequest<P> 빌드
  │        └─ python_manager::send() 호출
  │
  ├── python_manager.rs     (LOCK-RT-04)  — 본 파일 §7 상세 대상
  │     ├─ struct PythonManager
  │     ├─ async fn spawn()       → T1-4 spawn_protocol.md 협조
  │     ├─ async fn send<P, R>()  → 본 파일 §7.4
  │     ├─ async fn healthcheck() → T1-4 healthcheck.md 협조
  │     └─ async fn shutdown()    → §6 L3
  │
  ├── rpc_protocol.rs       (본 파일 §2.5 공통 자료구조)
  │     ├─ RpcRequest / RpcResponse / RpcError / RpcMeta
  │     └─ JsonRpcVersion
  │
  ├── config.rs             (LOCK-RT-04)
  │     └─ PythonBridgeConfig (타임아웃, 재시도, 경로)
  │
  └── models/               (LOCK-RT-04 — 25개 Serde 모델, T1-2)
        ├── core_models.rs
        ├── memory_models.rs
        ├── agent_models.rs
        └── workflow_event_config_models.rs
```

### 7.2 PythonManager 구조체

```rust
use std::sync::Arc;
use tokio::process::{Child, ChildStdin, ChildStdout};
use tokio::sync::{Mutex, RwLock, Semaphore, oneshot};
use std::collections::BTreeMap;
use std::sync::atomic::{AtomicU8, Ordering};

pub struct PythonManager {
    /// Python child process handle — Spawning/Restarting 시 교체되므로 RwLock.
    child: Arc<RwLock<Option<Child>>>,

    /// stdin writer — 단일 writer만 허용 (tokio::io::AsyncWriteExt::write_all).
    /// Mutex 로 감싸 동시 write 방지 (한 줄 단위 원자성 보장).
    stdin: Arc<Mutex<Option<ChildStdin>>>,

    /// 프로세스 상태 플래그 (상세명세 §F-1/§F-2 CAS).
    /// 0=Idle, 1=Spawning, 2=Running, 3=Unhealthy, 4=Restarting, 5=Dead
    state: Arc<AtomicU8>,

    /// correlation map: id(UUID v7) → oneshot::Sender<RpcResponse<Value>>
    /// BTreeMap 선택: O(log N) 조회/삽입/삭제 + time-ordered range query (§7.4).
    pending: Arc<Mutex<BTreeMap<String, PendingEntry>>>,

    /// 동시 RPC 한도 (상세명세 §G-2: Semaphore(50)).
    concurrency: Arc<Semaphore>,

    /// Spawn/Restart 전용 Mutex (FR-5 동시성 가드, 상세명세 §F-2).
    spawn_mutex: Arc<Mutex<()>>,

    /// 설정 (config.rs) — 타임아웃, 재시도 등.
    config: Arc<PythonBridgeConfig>,

    /// 모니터링 메트릭 sink (T2-4 협조).
    metrics: Arc<MetricsSink>,
}

struct PendingEntry {
    sender: oneshot::Sender<RpcResponse<serde_json::Value>>,
    method: String,
    issued_at: std::time::Instant,
    deadline_at: std::time::Instant,
    trace_id: String,
}

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ProcessState {
    Idle = 0,
    Spawning = 1,
    Running = 2,
    Unhealthy = 3,
    Restarting = 4,
    Dead = 5,
}
```

### 7.3 비동기 I/O 파이프라인 (tokio::process + tokio::io)

```
                ┌─────────────────────────────────────┐
                │   PythonManager::send<P, R>()       │
                │                                     │
  RpcRequest<P>─┼──> serde_json::to_string ──┐        │
                │                             │        │
                │            ┌────────────────v────┐   │
                │            │  stdin_tx (mpsc)     │   │
                │            │  (writer task)       │   │
                │            └────────────────┬────┘   │
                │                             │        │
                │                             v        │
                │          Mutex<ChildStdin>.write_all │
                │             + write b"\n" + flush    │
                └─────────────────────┬───────────────┘
                                      │ (stdin)
                                      v
                              [Python process]
                                      │ (stdout)
                                      v
                ┌─────────────────────┴───────────────┐
                │   reader task (spawn 시 1회 기동)    │
                │   BufReader<ChildStdout>.lines()     │
                │         │                            │
                │         v  (line-by-line)            │
                │   serde_json::from_str<RpcResponse>  │
                │         │                            │
                │         v                            │
                │   pending.lock().remove(&id)         │
                │         │                            │
                │         v                            │
                │   oneshot::Sender::send(response)    │
                └─────────────────────────────────────┘

                ┌─────────────────────────────────────┐
                │   stderr task (spawn 시 1회 기동)    │
                │   BufReader<ChildStderr>.lines()     │
                │         │                            │
                │         v                            │
                │   logs/python_engine.log 로테이션 저장 │
                │   CRITICAL/FATAL 감지 → 알림 이벤트    │
                └─────────────────────────────────────┘
```

- **stdin writer (Mutex 단일 writer)**: §7.2 `stdin: Arc<Mutex<Option<ChildStdin>>>` 를 `send()` 가 직접 lock 하여 직렬화된 라인을 write + `b"\n"` + flush (§7.4 L600-607). 별도 mpsc writer 태스크는 사용하지 않으며, Mutex 가드가 한 줄 단위 원자성/프레임 interleaving 방지를 보장한다.
- **stdout reader task**: spawn 시 단일 태스크로 기동. `BufReader::lines()` 스트림을 consume 하며 각 라인을 `RpcResponse<Value>` 로 파싱 후 correlation map 조회.
- **stderr reader task**: LOCK-RT-15 준수 — stdout 과 독립적으로 소비.

### 7.4 correlation map (id → oneshot::Sender)

```rust
impl PythonManager {
    pub async fn send<P: Serialize, R: DeserializeOwned>(
        &self,
        method: &str,
        params: P,
        timeout_ms: u64,
    ) -> Result<R, TauriError> {
        // 1. 상태 검증 (O(1))
        let state = self.state.load(Ordering::Acquire);
        if state != ProcessState::Running as u8 {
            return Err(TauriError::PythonBridgeError(
                "python_bridge_unhealthy".into(),
            ));
        }

        // 2. Semaphore 취득 (백프레셔, 상세명세 §G-2)
        let _permit = self.concurrency.clone().acquire_owned().await?;

        // 3. trace_id / correlation_id 발급 (§4)
        let id = Uuid::now_v7().to_string();                         // O(1)
        let meta = RpcMeta { /* ... */ };

        // 4. RpcRequest 직렬화 (O(payload))
        let req = RpcRequest {
            jsonrpc: JsonRpcVersion,
            id: id.clone(),
            method: method.to_string(),
            params,
        };
        let line = serde_json::to_string(&req)?;

        // 5. correlation map 등록 (O(log N))
        let (tx, rx) = oneshot::channel();
        let now = std::time::Instant::now();
        let deadline = now + std::time::Duration::from_millis(timeout_ms);
        {
            let mut pending = self.pending.lock().await;         // O(log N) acquire
            pending.insert(id.clone(), PendingEntry {            // O(log N) BTree insert
                sender: tx,
                method: method.into(),
                issued_at: now,
                deadline_at: deadline,
                trace_id: meta.trace_id.clone(),
            });
        }

        // 6. stdin 송출 (Mutex 보호, O(line_len))
        {
            let mut stdin_guard = self.stdin.lock().await;
            let stdin = stdin_guard.as_mut().ok_or(/* ... */)?;
            stdin.write_all(line.as_bytes()).await?;
            stdin.write_all(b"\n").await?;
            stdin.flush().await?;
        }

        // 7. 응답 대기 (타임아웃 포함)
        let grace = std::time::Duration::from_millis(timeout_ms + 1000);
        let response = tokio::time::timeout(grace, rx).await
            .map_err(|_| {
                // pending map 에서 cleanup (O(log N))
                let id = id.clone();
                tokio::spawn(async move { /* remove(&id) */ });
                TauriError::Timeout("python_bridge_timeout".into())
            })??;

        // 8. 에러 매핑 또는 result 역직렬화
        if let Some(err) = response.error {
            return Err(TauriError::from(err));
        }
        let result: R = serde_json::from_value(response.result.unwrap_or_default())?;
        Ok(result)
    }
}
```

**시간복잡도 표기**:

| 단계 | 복잡도 | 비고 |
|-----|------|-----|
| 상태 조회 (AtomicU8) | O(1) | Acquire load |
| Semaphore 취득 | O(1) amortized | contention 시 park |
| UUID v7 발급 | O(1) | |
| JSON 직렬화 | O(n), n=payload 크기 | serde_json |
| correlation map 삽입 | O(log N), N=동시 pending 수 | BTreeMap |
| stdin write | O(line_len) | 원자 쓰기 (Mutex 보호) |
| 응답 매칭 (reader task) | O(log N) | BTreeMap remove |
| deadline 일괄 청소 (background) | O(log N + K), K=만료 건수 | range query + remove |

### 7.5 reader task — pending 응답 매칭

```rust
async fn stdout_reader_task(
    stdout: ChildStdout,
    pending: Arc<Mutex<BTreeMap<String, PendingEntry>>>,
    state: Arc<AtomicU8>,
) {
    let mut lines = tokio::io::BufReader::new(stdout).lines();
    while let Ok(Some(line)) = lines.next_line().await {
        if line.len() > MAX_LINE_BYTES {
            tracing::error!(
                frame_len = line.len(),
                "python_bridge_oversized — closing stream"
            );
            state.store(ProcessState::Unhealthy as u8, Ordering::Release);
            break;
        }

        // 1차 파싱: untyped Value — notification(id 없음) 과 response(id 있음) 를 구분.
        let v: serde_json::Value = match serde_json::from_str(&line) {
            Ok(v) => v,
            Err(e) => {
                tracing::warn!(error=%e, line=%line, "malformed JSON-RPC frame");
                continue;  // 2회 연속 → Unhealthy (별도 카운터)
            }
        };

        // Ready notification 예외 처리 (§3.2) — id 필드 부재 = JSON-RPC 2.0 notification.
        // RpcResponse<R> 는 id: String 필수이므로 Value 단계에서 먼저 판별한다.
        if v.get("id").is_none() {
            if v.get("method").and_then(|m| m.as_str()) == Some("_ready") {
                tracing::info!(params=?v.get("params"), "python_bridge_ready");
                state.compare_exchange(
                    ProcessState::Spawning as u8,
                    ProcessState::Running as u8,
                    Ordering::AcqRel, Ordering::Acquire,
                ).ok();
            } else {
                tracing::debug!(line=%line, "unsolicited notification ignored");
            }
            continue;
        }

        // 2차 파싱: 정식 RpcResponse<Value>.
        let response: RpcResponse<serde_json::Value> = match serde_json::from_value(v) {
            Ok(r) => r,
            Err(e) => {
                tracing::warn!(error=%e, "malformed RpcResponse structure");
                continue;
            }
        };

        // correlation map 조회 + 제거 (O(log N))
        let entry = {
            let mut map = pending.lock().await;
            map.remove(&response.id)
        };
        if let Some(entry) = entry {
            let _ = entry.sender.send(response);  // 수신자가 dropped 되어도 무시
        } else {
            tracing::warn!(id=%response.id, "unknown correlation id (likely timed out)");
        }
    }

    // EOF → 프로세스 사망 판정
    state.store(ProcessState::Dead as u8, Ordering::Release);
    // restart trigger (T1-4 restart_policy.md)
}
```

### 7.6 T1-1 IPC 경계 인터페이스

```rust
// ipc_protocol.rs 내부 (T1-1 담당)
#[tauri::command]
async fn vamos_conversation_send(
    state: tauri::State<'_, AppState>,
    session_id: String,
    message: String,
) -> Result<ConversationResponse, TauriError> {
    let params = LanggraphDecisionCreateParams {
        session_id,
        message,
        context: vec![],
        _meta: RpcMeta::new_from_ipc(&state),
    };
    let result: LanggraphDecisionCreateResult = state
        .python_manager
        .send("langgraph.decision.create", params, 120_000)
        .await?;
    Ok(result.into())
}
```

- **경계**: Tauri IPC 커맨드(LOCK-RT-01 72개)는 `python_manager::send()` 호출로 JSON-RPC 층으로 위임. Tauri 커맨드 이름(`vamos:category:action`)은 `langgraph.*/embedding.*/llm.*/mcp.*` 메서드 이름과 **서로 독립**이며, 72 IPC 커맨드 중 어느 것이 어떤 JSON-RPC 메서드를 호출하는지는 T1-1 IPC 명세에서 정의.

### 7.7 T1-4 프로세스 관리 경계 인터페이스 (미완 대비 L1 선정의)

> T1-4 (spawn_protocol / healthcheck / restart_policy) 세션이 별도 진행되지만, 인터페이스 계약은 본 파일에서 선정의한다. T1-4 결과가 본 계약과 충돌 시 CONFLICT_LOG 등록.

```rust
impl PythonManager {
    // T1-4 spawn_protocol.md 협조 — 구체 로직은 T1-4 정본
    pub async fn spawn(&self) -> Result<(), TauriError> {
        let _guard = self.spawn_mutex.lock().await;  // FR-5 동시성 가드
        // 1. state CAS Idle→Spawning (또는 Dead→Spawning)
        // 2. Command::new(python).spawn() — L0 5s timeout
        // 3. stdin/stdout/stderr 파이프 추출 → child/stdin 필드 세팅
        // 4. reader/writer/stderr task 3개 기동
        // 5. _ready 라인 대기 (L0 5s timeout)
        // 6. initialize RPC 송출 (여기서는 "mcp.bridge.init" 이 사용됨 — method_catalog §2 PRE-3 참조)
        // 7. state CAS Spawning→Running
        unimplemented!("T1-4")
    }

    // T1-4 healthcheck.md 협조 — LOCK-RT-12
    pub async fn healthcheck(&self) -> HealthStatus {
        // 15초 간격 루프 (별도 태스크). 본 함수는 단일 틱.
        // mcp.bridge.health RPC 호출 (5s timeout)
        // 3회 연속 실패 시 state → Unhealthy → restart trigger
        unimplemented!("T1-4")
    }

    // T1-4 restart_policy.md 협조 — LOCK-RT-13
    pub async fn restart(&self, cause: RestartCause) -> Result<(), TauriError> {
        let _guard = self.spawn_mutex.lock().await;  // FR-5
        // 1. drain pending: 모든 PendingEntry 에 -32000 python_bridge_unhealthy 응답
        // 2. SIGTERM → 5s 대기 → SIGKILL (L3 Graceful Shutdown)
        // 3. backoff (1→2→4→8→16s / OOM 5s / HC 2→4→8s)
        // 4. spawn() 재진입
        unimplemented!("T1-4")
    }

    // Graceful shutdown — L3 (§6)
    pub async fn shutdown(&self) -> Result<(), TauriError> {
        // 1. state → Restarting (신규 요청 거부)
        // 2. shutdown RPC 송출 (10s timeout)
        // 3. 5s drain pending
        // 4. SIGTERM → SIGKILL fallback
        unimplemented!("T1-4")
    }
}
```

### 7.8 pending map 배경 청소 (deadline expiry)

```rust
async fn pending_janitor_task(
    pending: Arc<Mutex<BTreeMap<String, PendingEntry>>>,
) {
    let mut tick = tokio::time::interval(Duration::from_millis(500));
    loop {
        tick.tick().await;
        let now = Instant::now();
        let expired: Vec<String> = {
            let map = pending.lock().await;
            // BTreeMap 는 UUID v7 id 로 정렬 → ms 시각순 → range 청소 최적화 가능
            map.iter()
                .filter(|(_, e)| e.deadline_at <= now)
                .map(|(k, _)| k.clone())
                .collect()
        };
        if !expired.is_empty() {
            let mut map = pending.lock().await;
            for id in expired {
                if let Some(entry) = map.remove(&id) {
                    let err_response = RpcResponse {
                        jsonrpc: JsonRpcVersion,
                        id: id.clone(),
                        result: None,
                        error: Some(RpcError {
                            code: -32001,
                            message: "python_bridge_timeout".into(),
                            data: Some(RpcErrorData { /* ... */ }),
                        }),
                    };
                    let _ = entry.sender.send(err_response);
                }
            }
        }
    }
}
```

- 시간 복잡도: 수집 O(N), 제거 O(K log N). UUID v7 시간순 정렬 활용 시 초기 구간 range 청소 O(K + log N) 가능 (Phase 2 최적화).

---

## §8. Phase 2 테스트 시나리오 (10건 이상)

> Phase 2 T2-1~T2-4 통합 검증 대상. 각 시나리오는 통합 테스트 (Rust↔Python real subprocess) 기준. 계획서 §7 전환 게이트 /audit PASS 조건 기여.

### TC-01 — Happy path: 단일 RPC 왕복
- **준비**: PythonManager::spawn() 후 Running.
- **조건**: `langgraph.workflow.run` request 1건, params.workflow_id="wf_echo".
- **기대**: result.run_id 존재, elapsed_ms < 500ms, trace_id 일치.
- **검증**: `RpcRequest.id == RpcResponse.id`, structured 로그에 trace_id 2회 (req/resp).

### TC-02 — 타임아웃 (RPC deadline 초과)
- **조건**: `process_message` with params 유도 (Python 측 sleep 130s mock).
- **기대**: 121s 경과 후 `-32001 python_bridge_timeout`, pending map 에서 제거, Python 측도 `-32020 workflow_cancelled` 응답 가능 (race 허용).
- **검증**: Rust 측 elapsed_ms ∈ [120000, 121500], 프로세스 상태 Running 유지 (재시작 없음).

### TC-03 — Python 프로세스 크래시 (exit code 1)
- **조건**: Python 측 uncaught exception → SystemExit(1).
- **기대**: stdout EOF 감지 → state=Dead, pending 전체에 `-32000 python_bridge_unhealthy`, LOCK-RT-13 backoff 1s→2s→4s→8s→16s 로 재시작.
- **검증**: 메트릭 `python_bridge_restart_total` +1, 로그에 exit code 1 + backoff 단계 기록.

### TC-04 — OOM 재시작
- **조건**: Python 측 exit 137 (메모리 제한 초과).
- **기대**: `-32003 python_bridge_oom`, 5s 고정 backoff × 3회 (상세명세 §D-3), 메모리 상향 후 재시작.
- **검증**: backoff interval 5000±200ms, 최대 3회 후 Dead (상세명세 §D-3).

### TC-05 — Healthcheck 실패 3회 → 재시작
- **조건**: `mcp.bridge.health` 15초 주기 호출에 Python 측이 무응답 (5s timeout × 3회).
- **기대**: state Running→Unhealthy→Restarting, LOCK-RT-13 HC backoff 2s→4s→8s.
- **검증**: LOCK-RT-12 15s 주기 유지, 3회 연속 실패 확정 후 restart.

### TC-06 — stderr 로그 수집 (LOCK-RT-15)
- **조건**: Python 측 structlog.error("test") × 100 건, stdout 에는 정상 JSON-RPC 응답만.
- **기대**: `logs/python_engine.log` 에 100 라인 기록, stdout 파서 에러 0건, JSON-RPC 왕복 정상.
- **검증**: stdout 라인 중 JSON 파싱 실패 0건.

### TC-07 — 프레임 오염 (stdout 에 비-JSON 혼입)
- **조건**: Python 측 버그로 `print("debug")` 가 stdout 에 1회 혼입.
- **기대**: `-32700 parse_error` 로그, 해당 라인 드롭, 후속 정상 RPC 영향 없음. 2회 누적 시 restart (§3.4).
- **검증**: 1회 발생 시 restart 없음, 2회 연속 발생 시 restart.

### TC-08 — 배치 요청 (Phase 2 활성화)
- **조건**: `[req1(search_memory), req2(get_embeddings)]` 배열 전송. `process_message` 는 배치 금지.
- **기대**: `[resp1, resp2]` 배열 응답, id 순서 보존, 각 elapsed_ms 개별 기록.
- **검증**: `process_message` 를 배치에 포함 시 `-32600 invalid_request`.

### TC-09 — trace_id 전파 (T1-1 IPC → JSON-RPC → Python structlog)
- **조건**: React UI 에서 Tauri invoke, Rust IPC 핸들러가 UUID v7 발급.
- **기대**: JSON-RPC req/resp 양쪽 _meta.trace_id 동일, Python structlog 모든 로그에 trace_id 첨부.
- **검증**: `logs/python_engine.log` grep trace_id → 2+ 라인.

### TC-10 — 대용량 params (4 MiB 경계)
- **조건**: `get_embeddings` texts[] 총 3.9 MiB payload.
- **기대**: 정상 처리, result 역직렬화 성공.
- **변형**: 4.1 MiB → `-32002 python_bridge_oversized` 즉시 반환, stdin write 미발생.

### TC-11 — 동시성 한계 (Semaphore 50)
- **조건**: 60 동시 `search_memory` request 발행.
- **기대**: 50 건은 즉시 송출, 10 건은 대기, 선행 완료 후 순차 송출. 드롭 0건.
- **검증**: `python_bridge_rpc_duration_seconds` 히스토그램에 60 건 기록, 타임아웃 0건.

### TC-12 — Graceful shutdown (L3 5s)
- **조건**: 진행 중 RPC 3건 상태에서 `PythonManager::shutdown()` 호출.
- **기대**: state→Restarting, 신규 RPC 거부(-32000), 진행 중 3건 5s 내 완료, shutdown RPC 10s 내 완료, SIGTERM 전송.
- **검증**: 5s 초과 시 SIGKILL fallback, 메트릭 `python_bridge_graceful_shutdown_total` +1.

### TC-13 — method_not_found
- **조건**: 클라이언트 악성/버그로 `"method": "langgraph.unknown"` 전송.
- **기대**: `-32601 method_not_found` 응답, 프로세스 영향 없음.

### TC-14 — params 검증 실패
- **조건**: `langgraph.workflow.run` 에 workflow_id 누락.
- **기대**: `-32602 invalid_params`, `data.missing_fields=["workflow_id"]`.

---

## §9. 구조화 로그 JSON (중첩 구조)

### 9.1 로그 스키마

```json
{
  "timestamp": "2026-04-11T02:00:00.123Z",
  "level": "error",
  "logger": "bridge.python_manager",
  "event": "python_bridge_timeout",
  "trace_id": "01930e8e-6b4c-7e00-9c1a-1f3c5b8e9d4a",
  "correlation_id": "req_1713480000_0001",
  "error": {
    "code": -32001,
    "name": "python_bridge_timeout",
    "message": "deadline exceeded",
    "upstream_error": null
  },
  "context": {
    "method": "langgraph.workflow.run",
    "process_state": "Running",
    "pending_count": 7,
    "elapsed_ms": 120050,
    "deadline_ms": 120000,
    "params_size_bytes": 1024,
    "pid": 12345
  },
  "recovery": {
    "action": "cleanup_pending",
    "retry_count": 0,
    "backoff_ms": null,
    "next_state": "Running"
  }
}
```

### 9.2 로그 이벤트 카탈로그

| event | level | 발생 시점 | 필수 context |
|-----|-----|--------|----|
| `python_bridge_spawn_attempt` | info | spawn() 호출 | attempt, venv_path |
| `python_bridge_ready` | info | _ready 라인 수신 | pid, capabilities |
| `python_bridge_rpc_request` | debug | send() 직전 | method, params_size_bytes |
| `python_bridge_rpc_response` | debug | reader task 수신 | method, elapsed_ms, result_size_bytes |
| `python_bridge_rpc_error` | error | RpcError 수신 | error.code, error.name |
| `python_bridge_timeout` | error | tokio::timeout Err | method, elapsed_ms, deadline_ms |
| `python_bridge_malformed_frame` | warn | JSON 파싱 실패 | line_preview (최대 200자) |
| `python_bridge_healthcheck_fail` | warn | HC 응답 실패/타임아웃 | consecutive_fails |
| `python_bridge_restart` | info | restart() 진입 | cause, attempt, backoff_ms |
| `python_bridge_shutdown` | info | shutdown() 완료 | drained_count, elapsed_ms |
| `python_bridge_oom` | error | exit 137 감지 | memory_limit_mb |
| `python_bridge_crash` | error | exit != 0 (137 제외) | exit_code |

### 9.3 LOCK-RT-15 준수

- 모든 구조화 로그는 **Rust 측 `tracing` crate → 파일 sink (`logs/rust_bridge.log`)**. Python 엔진의 stderr 로그는 별도로 `logs/python_engine.log` 에 기록 (상세명세 §D-4).
- **금지**: Rust 측 구조화 로그를 Python 측 stdout/stderr 로 전송 — LOCK-RT-15 위반.

---

## §10. LOCK 교차 점검표

| LOCK ID | 본 파일 준수 항목 | 섹션 |
|-----|--------|----|
| LOCK-RT-03 | 13개 메서드명 범위 (`langgraph.*/embedding.*/llm.*/mcp.*`) | §5.2 커스텀 에러 범위 주석 / method_catalog.md §3 정본 |
| LOCK-RT-04 | python_manager.rs 단일 정본, ipc_protocol.rs와 경계, config.rs 설정 분리, 25 Serde 모델 method_catalog §7 참조 | §7.1 모듈 경계 |
| LOCK-RT-11 | JSON-RPC 2.0, stdin/stdout, `\n` 구분, serde_json↔orjson | §2/§3 |
| LOCK-RT-12 | HC 15s/5s/3회 — 정본 수치만 인용, 재정의 없음 | §6.2 |
| LOCK-RT-13 | Restart backoff 1→2→4→8→16s / OOM 5s / HC 2→4→8s — 정본 수치만 인용 | §6/§7.7 |
| LOCK-RT-14 | TauriError 7 variant 매핑 (NotFound/ValidationError/PythonBridgeError/IoError/Timeout/PermissionDenied/InternalError) | §5.3 |
| LOCK-RT-15 | stdout = JSON-RPC 전용, stderr = 로그 전용, 혼선 금지 (R-14-6) | §3.2/§9.3 |

- **LOCK 재정의 여부**: 없음 — 본 파일은 정본 수치 참조 + 상세화(DEFINED-HERE 영역).
- **LOCK 변경 필요 여부**: 없음. (변경 필요 시 `[LOCK_CHANGE_NEEDED]` 표기 — 본 파일은 해당 없음.)

---

## §11. 변경 이력

| 버전 | 일자 | 변경 내용 | 작성자 |
|-----|-----|--------|------|
| v0.1 | 2026-04-11 | 초기 작성 (T1-3 step 1). §1~§10 신규 작성. LOCK-RT-03/04/11/12/13/14/15 전수 준수. python_manager.rs 내부 구조 + correlation map + pending janitor + FR-8 타임아웃 캐스케이드 상세화. Phase 2 테스트 시나리오 14건 작성. | T1-3 Subagent |
| v0.2 | 2026-04-11 | T1-3 step 2 재검증. §7.5 stdout_reader_task 에서 JSON-RPC notification(id 부재) 처리 버그 수정 — 1차 untyped Value 파싱 후 `_ready` 감지 및 Spawning→Running CAS, 그 외 notification 은 debug 로그. §3.4 표 id-공백 행 문구를 신규 동작에 맞춰 재작성. | T1-3 Subagent |

---

<!-- END OF DOCUMENT -->
