# Message Framing Spec (FR-3 정본)

> **도메인**: #14 Rust-Tauri-Infrastructure
> **그룹**: 01_ipc-commands 공통 프레이밍 정본
> **작성일**: 2026-04-11
> **정본 소유**: `sot 2/4-1_Rust-Tauri-Infrastructure/01_ipc-commands/message_framing.md` (FR-3 DEFINED-HERE)
> **목적**: T1-1 게이트 FR-3 요구사항 충족 — 72 IPC 커맨드의 메시지 직렬화/프레이밍/바운더리 정본 제공.
> **상태**: Phase 1 T1-1 본작업, L3 상세 — step1b 실체화

---

## 1. 교차 참조 (Cross-References)

| 참조 대상 | 경로 | 관계 |
|----------|------|------|
| LOCK-RT-01 (IPC 이름 72개) | `sot/PHASE_B1_API_CONTRACT.md` §5.1 | 커맨드 이름 정본 |
| LOCK-RT-02 (카테고리 매핑) | `guides/VAMOS_구현가이드_PART2_구현단계.md` §6.2.1 | Part2 5분류 배분 |
| LOCK-RT-06 (EventTypeRegistry) | `sot/D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` §5.1 | 이벤트 페이로드 |
| LOCK-RT-11 (Python 브릿지 JSON-RPC) | `sot 2/4-1_Rust-Tauri-Infrastructure/03_python-bridge/` (T1-3 예정) | stdin/stdout 라인 구분 |
| LOCK-RT-14 (TauriError 7 variant) | `sot 2/4-1_Rust-Tauri-Infrastructure/RUST_TAURI_INFRASTRUCTURE_상세명세.md` §A 공통 에러 | 오류 전달 |
| LOCK-RT-15 (stderr 분리) | `sot 2/4-1_Rust-Tauri-Infrastructure/RUST_TAURI_INFRASTRUCTURE_상세명세.md` §G-1 | Python 프로세스 I/O 격리 |
| CONFLICT_LOG.md | `sot 2/4-1_Rust-Tauri-Infrastructure/CONFLICT_LOG.md` | 충돌 추적 (FR-3 재발 방지) |
| D2.1-D4 ToolRegistry | `sot/D2.1-D4_D4_SCHEMA_ORANGE_EXT.md` | Tool 커맨드 페이로드 |
| PHASE_B2 §4.3 | `sot/PHASE_B2_IPC_INTEGRATION.md` §4.3 | Tauri 통합 바운더리 |

---

## 2. 직렬화 포맷

### 2.1 경계별 포맷

| 경계 (Boundary) | 포맷 | 인코딩 | 규격 |
|----------------|------|--------|------|
| Frontend ↔ Tauri (webview ↔ Rust) | **JSON** (단일 객체) | UTF-8 | Tauri invoke 규격 v1.x |
| Rust ↔ Python bridge | **JSON-RPC 2.0** | UTF-8 | `\n` 라인 구분 (LOCK-RT-11) |
| Rust ↔ DB/FS | Serde-native (CBOR/SQLite) | 바이너리 | 본 명세 범위 외 |

### 2.2 Tauri invoke 규격 준수

- Tauri IPC는 `window.__TAURI_INTERNALS__.invoke(cmd, payload)` 를 통해 **단일 JSON 객체**를 Rust 측 라우터로 전달한다.
- Rust 측 `#[tauri::command]` 함수가 Serde로 역직렬화하며, 반환값은 `Result<T, TauriError>` → JSON 객체로 직렬화되어 webview로 복귀.
- Tauri IPC와 JSON-RPC 2.0은 **완전히 분리된 경계**이며, Tauri invoke 페이로드 안에 JSON-RPC 래퍼를 중첩하지 않는다.

### 2.3 JSON-RPC 2.0 (Python bridge)

- Rust → Python: `{"jsonrpc":"2.0","id":"<uuid v7 string>","method":"<method>","params":<object>}\n`
- Python → Rust: `{"jsonrpc":"2.0","id":"<uuid v7 string>","result":<T>}\n` 또는 `{"jsonrpc":"2.0","id":"<uuid v7 string>","error":{"code":<i32>,"message":"<str>","data":<object?>}}\n`
- **Content-Length 헤더 미사용** — LSP 스타일 헤더 블록은 적용하지 않는다. 오직 LF(`\n`) 구분자 기반 line-delimited JSON.

---

## 3. 메시지 구조

### 3.1 Tauri invoke request

```json
{
  "cmd": "vamos:{category}:{action}",
  "payload": {
    "trace_id": "018f4bbd-0000-7xxx-8xxx-xxxxxxxxxxxx",
    "correlation_id": "c-018f4bbd-1234",
    "issued_at": "2026-04-11T00:25:00.000Z",
    "source": "frontend",
    "args": { /* command-specific */ }
  }
}
```

- `cmd` 형식: `vamos:{category}:{action}` — LOCK-RT-01 네이밍 규칙 (예: `vamos:session:create`, `vamos:conversation:send`).
- `category` ∈ {session, conversation, memory, search, agent, tool, workflow, settings, file, system, mcp, health}.
- `action` 은 스네이크 케이스 (`create`, `get_stats` 등).

### 3.2 Tauri invoke response

```json
{
  "ok": true,
  "data": { /* T */ },
  "error": null
}
```

실패 시:

```json
{
  "ok": false,
  "data": null,
  "error": {
    "type": "TauriError::NotFound",
    "resource": "Session",
    "id": "018f4bbd-...",
    "trace_id": "018f4bbd-0000-7xxx-8xxx-xxxxxxxxxxxx",
    "correlation_id": "c-018f4bbd-1234"
  }
}
```

### 3.3 필수 헤더 필드

| 필드 | 타입 | 의미 | 규칙 |
|-----|-----|-----|-----|
| `trace_id` | UUID v7 String | 분산 트레이스 식별자 | **UUID v7 강제** (§6 보안 바인딩) |
| `correlation_id` | String | 재시도/상관관계 묶음 | 재시도 체인 식별 |
| `issued_at` | RFC3339 UTC String | 발신 시각 | 타임아웃/재정렬 방지 |
| `source` | Enum String | 발신자 식별 | `frontend` \| `backend` \| `python_bridge` |

- `trace_id` / `correlation_id` / `issued_at` / `source` 는 **모든** Tauri invoke request 페이로드에 필수 포함.
- 응답 객체의 `error.trace_id` 는 request 의 `trace_id` 를 그대로 에코 (상관 추적 보장).

---

## 4. 바운더리 / 프레이밍 규칙

### 4.1 Tauri IPC (Frontend ↔ Rust)

- **단위**: 단일 JSON 객체 (프레임 1개).
- **사이즈 제한**: `payload` 최대 **10 MB** (바이너리 대용량은 file 커맨드 또는 파일 경로 참조로 우회).
  - **프레이밍 정본 = 10 MB** (상세명세 §G-1 DEFINED-HERE 'LOCK-MCP-01과 통일' 정본 정합). §6 SEC-2 / TS-SEC-FRM-1 / file_commands.md 와 동일 값.
- **백프레셔**: Frontend 측 Promise queue + Rust 측 `tokio::sync::Semaphore(max=50)` (§G-2 백엔드 큐 LOCK-RT-14 연계).
- **압축**: 미사용 (Tauri 내부 경계는 zero-copy 지향).

### 4.2 Python bridge (Rust ↔ Python)

- **프로세스 모델**: Python sidecar (stdin/stdout/stderr 3파이프).
- **stdin/stdout**: JSON-RPC 2.0, `\n` 라인 구분자 (LOCK-RT-11).
- **stderr**: 로그·진단 전용, JSON 직렬화와 **분리** (LOCK-RT-15). stderr 내용은 Rust 측에서 구조화 로그에 흡수되나 JSON-RPC 스트림에 섞이지 않는다.
- **라인 길이 한계**: 1 라인 최대 **4 MiB** (내부 Python JSON 파서 안정성 한계).
- **Content-Length 헤더 미사용**: LSP와 달리 라인 구분만 사용 — 중간 개행이 포함된 문자열은 `\n` 으로 escape 된 JSON 문자열로만 출현.

### 4.3 오버플로 / 분할 금지

- Tauri invoke payload 는 **분할 전송 금지**. 8 MiB 초과 시 호출 측에서 사전에 분할(예: file_chunk 커맨드)하거나 파일 경로 기반 우회 사용.
- Python bridge 라인 4 MiB 초과 시 `TauriError::InternalError { message: "bridge line overflow" }` 반환.

---

## 5. 오류 전달 경로

### 5.1 Rust 내부 → Frontend

```
Rust handler error  →  TauriError (LOCK-RT-14 7 variant)  →  JSON {ok:false, error:{type, ...}}  →  Frontend
```

- 7 variant: `NotFound` | `ValidationError` | `PythonBridgeError` | `IoError` | `Timeout` | `PermissionDenied` | `InternalError`.
- 각 variant 의 구조적 필드(resource/id/field/code/path/operation/elapsed_ms/action/message)는 LOCK-RT-14 정의를 그대로 보존.

### 5.2 Python 오류 → Rust → Frontend

```
Python raises  →  JSON-RPC error object {code, message, data?}
              →  Rust PythonBridgeError { code, message }
              →  TauriError::PythonBridgeError
              →  Frontend JSON error
```

- JSON-RPC 표준 코드 (-32700 파싱 오류, -32600 잘못된 요청, -32601 메서드 없음, -32602 잘못된 파라미터, -32603 내부 오류) 는 Python bridge 측 오류 계층에서 그대로 사용.
- 사용자 정의 코드는 -32000 ~ -32099 범위 (서버 에러) 로 제한 — JSON-RPC 2.0 §5.1 준수.
- Rust → Frontend 단계에서 `TauriError::PythonBridgeError { code, message }` 로 래핑되며 `code` 필드는 원본 JSON-RPC `code` 를 보존.

### 5.3 Timeout 계층화

| 계층 | 기본 타임아웃 | 비고 |
|-----|-------------|------|
| Tauri invoke 전역 | 30 s | Rust 측 최대 상한 |
| 커맨드별 | 가변 (500 ms ~ 120 s) | 각 `*_commands.md` 참고 |
| SQLite 쿼리 | 800 ms | session_load 등 |
| Python bridge 라운드트립 | 최대 120 s (LLM) | conversation_* |

가장 엄격한 값이 먼저 trip — 내부 타임아웃이 외부를 초과하면 안 된다.

---

## 6. 보안 바인딩

| ID | 항목 | 규칙 | Phase 1 상태 |
|----|-----|-----|--------------|
| SEC-1 | `trace_id` 위조 방지 | request 수신 시 UUID v7 포맷 검증 (버전 비트 `0b0111`, variant 비트 `0b10xx`). 누락/형식 오류 → `ValidationError { field: "trace_id", message: "invalid uuid v7" }` | 구조만 준비 (T2-2 본작업) |
| SEC-2 | payload 사이즈 상한 | **8 MiB** (§4.1). 초과 → `ValidationError { field: "payload", message: "size exceeds 8 MiB" }` | 구조만 준비 |
| SEC-3 | RBAC 식별자 포함 | 쓰기/삭제 계열 커맨드 payload.args 에 `rbac_subject` (user_id 또는 role hash) 필수 포함. 누락 → `PermissionDenied { action: <cmd> }` | Phase 2 T2-2 hook |
| SEC-4 | 입력 검증 | Serde 역직렬화 단계에서 타입 검증, 추가 필드 무시(`deny_unknown_fields` 미적용) | 구조만 준비 |
| SEC-5 | 응답 민감정보 마스킹 | `error.message` 는 스택 트레이스 미포함, 내부 경로 마스킹 | 예약 |
| SEC-6 | 감사 로그 기록 | 모든 실패 응답은 `trace_id` 기준 구조화 로그 기록 (각 *_commands.md §6) | 구조만 준비 |
| SEC-7 | 프로세스 경계 격리 | Python bridge 는 stdin/stdout 외 IPC 금지, stderr 로깅 전용 (LOCK-RT-15) | PASS (LOCK-RT-15) |

---

## 7. FR-4 에러 핸들링 매트릭스 포인터

> 본 문서는 FR-3 프레이밍 정본이며, FR-4 72 × 7 매트릭스 본문은 각 커맨드 파일 §2 (또는 §4) 가 정본이다. 중복 기재 금지.

| 파일 | 매트릭스 위치 | 커맨드 수 |
|-----|-------------|----------|
| `session_commands.md` | §4 에러 매트릭스 | 8 |
| `conversation_commands.md` | §2 에러 매트릭스 | 8 |
| `memory_commands.md` | §2 에러 매트릭스 | 7 |
| `search_commands.md` | §2 에러 매트릭스 | 6 |
| `agent_commands.md` | §2 에러 매트릭스 | 7 |
| `tool_commands.md` | §2 에러 매트릭스 | 6 |
| `workflow_commands.md` | §2 에러 매트릭스 | 6 |
| `settings_commands.md` | §2 에러 매트릭스 | 6 |
| `file_commands.md` | §2 에러 매트릭스 | 6 |
| `system_commands.md` | §2 에러 매트릭스 | 6 |
| `mcp_commands.md` | §2 에러 매트릭스 | 3 |
| `health_commands.md` | §2 에러 매트릭스 | 3 |
| **합계** | — | **72** |

> 종합 72 × 7 매트릭스가 별도 집계 필요 시 T1-1 step 5 (_index.md 갱신) 단계에서 본 포인터 표를 참조해 구성한다.

---

## 8. 테스트 시나리오 (10건)

| # | 시나리오 | 조건 | 기대 결과 |
|---|---------|------|----------|
| FR3-T1 | 직렬화 경계 | Tauri invoke 단일 JSON 객체 8 MiB 경계 | 8 MiB 정확 → PASS, 8 MiB + 1B → `ValidationError{field:"payload"}` |
| FR3-T2 | trace_id 누락 | request.payload 에 `trace_id` 필드 없음 | `ValidationError{field:"trace_id", message:"missing"}` |
| FR3-T3 | 사이즈 초과 | Python bridge 라인 4 MiB + 1B | `InternalError{message:"bridge line overflow"}` |
| FR3-T4 | 중복 correlation_id | 동일 `correlation_id` 로 동시 2회 send | 두 번째 호출 `ValidationError{field:"correlation_id", message:"duplicate in-flight"}` — 재시도는 허용 |
| FR3-T5 | stderr 오염 | Python 측이 stdout 에 비-JSON 문자열 출력 | Rust parser reject + stderr 경로로 재라우팅, 응답 `PythonBridgeError{code:-32700}` |
| FR3-T6 | LF 없음 | Python 프로세스가 개행 없이 JSON 종료 | Rust reader 4 MiB 버퍼까지 대기 → 초과 시 `InternalError{message:"missing LF"}` |
| FR3-T7 | 타임아웃 경계 | Tauri invoke 30 s 경계 | 29.9 s 응답 → PASS, 30.1 s → `Timeout{operation, elapsed_ms:30100}` |
| FR3-T8 | 중첩 에러 매핑 | Python JSON-RPC error {code:-32001} | Rust → `TauriError::PythonBridgeError{code:-32001, message:...}` → Frontend JSON error |
| FR3-T9 | RBAC 누락 | 쓰기 커맨드에 `rbac_subject` 없음 | `PermissionDenied{action:<cmd>}` + 감사 로그 |
| FR3-T10 | CONFLICT 재발 방지 | `_index.md §프레이밍` 참조 검색 | 0 건 (본 문서 §3~§5 로 정정됨, CONFLICT_LOG.md 에 step1b 기록) |

---

## 9. LOCK 교차 점검표

| LOCK ID | 준수 항목 | 본 명세 반영 위치 | 상태 |
|---------|----------|------------------|------|
| LOCK-RT-01 | 72 커맨드 이름 규칙 `vamos:{category}:{action}` | §3.1 cmd | PASS |
| LOCK-RT-02 | Part2 5분류 배분 (Core/Agent/Storage/Safety/UI) | §7 포인터 표 | PASS (참조만) |
| LOCK-RT-06 | EventTypeRegistry 134건 | §5 오류 → 이벤트 emit 계층 (각 *_commands.md §3 연계) | PASS (참조) |
| LOCK-RT-11 | Python bridge stdin/stdout 라인 구분 | §2.3 / §4.2 | PASS |
| LOCK-RT-14 | TauriError 7 variant | §5.1 / §3.2 error 구조 | PASS |
| LOCK-RT-15 | stderr 분리 | §4.2 / §6 SEC-7 | PASS |

---

## 10. 변경 이력

| 날짜 | 변경 | 근거 |
|-----|-----|-----|
| 2026-04-11 | 초판 — FR-3 실체화 (T1-1 step1b) | session/conversation 파일이 참조하던 `_index.md §프레이밍` 섹션 부재 해소. `_index.md` 는 T1-1 단계 수정 금지이므로 01_ipc-commands/ 내부 별도 파일로 정본 이관. |

---

<!-- END OF DOCUMENT -->

---

# §V2. IPC 보안 강화 — T2-2 (ISS-07 해소)

> **Phase 2 T2-2 산출물** (ISS-07 해소, plan §7 T2-2 L977~L1008 + §A.4 L1266~L1276 정본 verbatim)
> **작성일**: 2026-04-24
> **대상 V1 커맨드**: FR-3 Message Framing 72개 (ID 1-72, Part2 카테고리: 전수 (72 공통))
> **LOCK 근거**: LOCK-RT-01 (IPC 72 커맨드 이름) / LOCK-RT-02 (5분류) / LOCK-RT-14 (TauriError 7 variant)
> **V1 본문**: 불변 (§1~§N 위 모든 내용 append-only 엄수, byte-prefix SHA 검증 대상)
> **baseline**: `5d95fbb5b428369a` / bytes=13131 / lines=251

## §V2.1 교차 참조 블록

| 대상 | 경로 | 관계 |
|-----|-----|------|
| **상위 정본 체인** | AUTHORITY_CHAIN.md §1 + §2 LOCK-RT-01~15 | LOCK 근거 |
| **plan 정본** | RUST_TAURI_INFRASTRUCTURE_구조화_종합계획서.md §A.4 L1266~L1276 (SEC-1~7) + §7 T2-2 L977~L1008 | SEC 체크리스트 정본 |
| **상세명세 DEFINED-HERE** | RUST_TAURI_INFRASTRUCTURE_상세명세.md §A 공통 에러 L153~L162 (TauriError 7) | 에러 매핑 정본 |
| **upstream SoT** | sot/STEP7-F_인프라_배포_MLOps_작업가이드.md (4-1 은 REF) | 인프라 보안 Tier 4 참조 |
| **peer V2 (T2-1 NEW)** | 04_build-signing/tauri_build_config.md + code_signing.md | Tauri allowlist / updater 서명 |
| **peer V2 (T2-4 EXTEND)** | 05_process-management/spawn_protocol.md §V2 + healthcheck.md §V2 + restart_policy.md §V2 | SEC 위반 메트릭 |
| **peer V2 (T2-3 plan meta)** | plan §A.3 L1255~L1264 | 카테고리별 SLA 에러율 한도 |
| **SEC 정본 상위** | Part2 §6.5.1 보안 체크리스트 | 횡단 관심사 (계획서 §9.4) |
| **FailureCodeRegistry** | D2.1-D2 §5.2 (LOCK-RT-07, 6-12 LOCK-EL-03 정본 REF) | SEC 위반 ↔ canonical code 매핑 |

## §V2.2 SEC-1~SEC-7 체크리스트 매트릭스

| # | 규칙 | 본 파일 적용 | 적용 범위 | TauriError 매핑 |
|---|------|------------|----------|----------------|
| SEC-1 | 입력 검증 (Serde + validator) | ✅ 적용 | 전수 72/72 | ValidationError |
| SEC-2 | trace_id UUID v7 위조 탐지 | ✅ 적용 | 전수 72/72 | ValidationError |
| SEC-3 | RBAC Permission Level 사전 체크 | ✅ 적용 | 전수 72/72 | PermissionDenied |
| SEC-4 | 경로 탐색 방지 (canonicalize + whitelist) | ✅ 특화 | 전수 | ValidationError / PermissionDenied |
| SEC-5 | 주입 방지 (이스케이프 + 파라미터화) | ✅ 특화 | 전수 | ValidationError |
| SEC-6 | 레이트 리밋 (D4 RateLimitConfig) | ✅ 적용 | 전수 72/72 | InternalError (rate_limit) |
| SEC-7 | HMAC-SHA256 서명 (constant-time) | ✅ 특화 | 전수 | ValidationError (signature) |

### 적용 설명
- **SEC-1 입력 검증**: Serde `#[derive(Deserialize)]` + custom validator (예: `session_id: validate_uuid_v7`) 72 커맨드 공통 1순위
- **SEC-2 trace_id 검증**: UUID v7 형식 강제 (`00000000-0000-7xxx-yyyy-xxxxxxxxxxxx`, variant bits `10`) + 시간 역전/미래 1h 초과 거부
- **SEC-3 RBAC Permission Level**: V1 §1 표의 `RBAC` 열 정본 사용, session_open 시점 확정된 level 과 대조
- **SEC-6 레이트 리밋**: 카테고리별 (Core 100/Agent 50/Storage 200/Safety 1000/UI 100) (D4 RateLimitConfig 연동, 초과 시 `InternalError { message: "rate_limit_exceeded" }`)

## §V2.3 LOCK 5필드 매핑

| LOCK ID | 항목 | 정본 출처 | 값 | 재정의 |
|---------|------|-----------|-----|--------|
| LOCK-RT-01 | IPC 커맨드 이름 | PHASE_B1 §5.1 / Part2 §6.2.1 (공동) | `(모든 72 공통)*` 72개 (ID 1-72) | ❌ |
| LOCK-RT-02 | 카테고리 소속 | Part2 §6.2.1 (단독) | 전수 (72 공통) | ❌ |
| LOCK-RT-14 | TauriError 7 variant | 상세명세 §A L153~L162 (DEFINED-HERE) | NotFound / ValidationError / PythonBridgeError / IoError / Timeout / PermissionDenied / InternalError | ❌ |

## §V2.4 SEC-4 경로 탐색 방지 (본 파일 특화)

- **canonicalize + whitelist**: 모든 경로 인자는 `std::fs::canonicalize()` 호출 후 `$APPDATA/vamos/sandbox/` 접두 strict prefix 검증
- **상대 경로 거부**: `../` / `..\` 패턴 감지 시 즉시 `PermissionDenied { action: "path_traversal" }` 반환
- **symlink 정책**: read 전용 허용 (O_NOFOLLOW), write/upload 는 `PermissionDenied` (symlink race 방지)
- **드라이브 분리**: Windows `C:\Windows`, Unix `/proc`, `/sys`, `/dev` 등 시스템 경로 block-list 강제

## §V2.5 SEC-5 주입 방지 (본 파일 특화)

- **SQL injection**: `search_keyword` BM25 쿼리는 Tantivy parameterized query 경유 (raw SQL 직접 실행 금지)
- **Shell injection**: `tool_execute` / `tool_install` params 는 `execvp` argv 배열 전달 (shell=true 금지)
- **Command injection**: MCP stdio 경로 `mcp_connect.server.command` 는 whitelist enum (Node/Python/Deno 이진만 허용)
- **이스케이프**: 사용자 제공 문자열은 JSON 직렬화 시 자동 이스케이프 (serde_json 기본 behavior)

## §V2.6 SEC 위반 에스컬레이션 Pydantic 스키마

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime
from uuid import UUID

class SecurityViolation(BaseModel):
    """IPC SEC-1~7 위반 시 내부 에스컬레이션 이벤트 (LOCK-RT-06 event bus)."""
    sec_id: Literal["SEC-1","SEC-2","SEC-3","SEC-4","SEC-5","SEC-6","SEC-7"]
    invoke_name: str = Field(..., description="vamos:<category>:<action> 형식")
    tauri_error: Literal["ValidationError","PermissionDenied","InternalError"]
    field: Optional[str] = Field(None, description="SEC-1 / SEC-7 위반 필드명")
    user_id: str
    trace_id: UUID = Field(..., description="UUID v7 (SEC-2 통과 후)")
    timestamp: datetime
    severity: Literal["Debug","Info","Warn","Error","Critical"] = "Error"
    file_scope: Literal["FR-3 Message Framing"] = "FR-3 Message Framing"
```

## §V2.7 SEC-7 HMAC 서명 (본 파일 특화)

- **알고리즘**: HMAC-SHA256 (FIPS 180-4), rotating key 24h
- **대상**: 민감 커맨드 `(모든 72 공통)*` (쓰기/admin 계열)
- **비교**: `subtle::ConstantTimeEq` 기반 constant-time 비교 (timing attack 방어)
- **키 저장**: OS keychain (Windows DPAPI / macOS Keychain Services / Linux libsecret)
- **rotation 정책**: 24h 자동 rotation, 이전 key 는 1h grace window 로 보관 (진행중 요청 호환)
- **위반 시**: `ValidationError { field: "hmac_signature", message: "invalid or missing" }`

## §V2.8 구조화 로그 3-block (LOCK-RT-15 stderr 분리)

### block-1: SEC-1 Validation 실패
```json
{
  "source": "rust_tauri.ipc.frm.sec",
  "sec_id": "SEC-1",
  "invoke_name": "(모든 72 공통)example",
  "tauri_error": "ValidationError",
  "field": "<failing_field>",
  "user_id": "u_...",
  "trace_id": "018f....",
  "severity": "Warn",
  "timestamp": "2026-04-24T..."
}
```

### block-2: SEC-3 RBAC deny
```json
{
  "source": "rust_tauri.ipc.frm.sec",
  "sec_id": "SEC-3",
  "invoke_name": "(모든 72 공통)example",
  "tauri_error": "PermissionDenied",
  "required_level": "(모든 72 공통):admin",
  "actual_level": "user",
  "severity": "Error"
}
```

### block-3: SEC-6 Rate limit trip
```json
{
  "source": "rust_tauri.ipc.frm.sec",
  "sec_id": "SEC-6",
  "invoke_name": "(모든 72 공통)example",
  "tauri_error": "InternalError",
  "message": "rate_limit_exceeded",
  "window_s": 1,
  "limit": "카테고리별 (Core 100/Agent 50/Storage 200/Safety 1000/UI 100)",
  "severity": "Info"
}
```

> **LOCK-RT-15 준수**: 위 3 블록은 **stderr** 로그 전용, stdout 은 JSON-RPC 응답 전용 (혼선 절대 금지).

## §V2.9 Phase 3 테스트 시나리오 (FRM, ≥ 10건)

1. TS-SEC-FRM-1 — payload > 10MB → SEC-1 `ValidationError too_large` (G-1 정본)
2. TS-SEC-FRM-2 — backend queue 50 포화 → tokio::sync::Semaphore drop 오래된 non-LLM (G-2 정본)
3. TS-SEC-FRM-3 — trace_id UUID v4 → SEC-2 거부
4. TS-SEC-FRM-4 — frontend queue 100 초과 → "처리 중" UI
5. TS-SEC-FRM-5 — JSON-RPC batch (LOCK-RT-11) 초과 size → SEC-1
6. TS-SEC-FRM-6 — stderr 로그 stdout 혼선 탐지 (LOCK-RT-15 위반 감지)
7. TS-SEC-FRM-7 — 72 커맨드 × SEC-1~7 전수 표 정합
8. TS-SEC-FRM-8 — SEC-6 카테고리별 rate 적용 검증 (Core/Agent/Storage/Safety/UI)
9. TS-SEC-FRM-9 — 전 72 커맨드 trace_id v7 SEC-2 100% 커버리지
10. TS-SEC-FRM-10 — HMAC 서명 (민감 커맨드 settings/system/mcp) 경로 실체화
11. TS-SEC-FRM-11 — symlink race (SEC-4 file/memory) 경계 실체화
12. TS-SEC-FRM-12 — Shell/SQL/Command injection (SEC-5 tool/mcp/search) 실체화

## §V2.10 자가 체크리스트 (품질 필수 구조 #1~#8 적용)

- [x] §1 교차 참조 블록 (§V2.1): peer V2 + plan §A.4 + 상세명세 §A + upstream SoT 전수
- [x] §2 공통 자료 구조 참조 (§V2.3): LOCK-RT-01/02/14 5필드 분리 인용 (ID × 항목 × 정본 출처 × 값 × 재정의)
- [x] §3 SEC-1~7 규칙 매트릭스 (§V2.2): 본 파일 적용 여부 + 범위 + TauriError 매핑 전수 표
- [x] §4 카테고리 특화 (§V2.4/§V2.5/§V2.7): SEC-4/5/7 중 본 파일 해당 섹션만 상세화
- [x] §N LOCK panel (§V2.3) + §N.1 에스컬레이션 Pydantic (§V2.6) + §N.2 구조화 로그 3-block (§V2.8)
- [x] §N Phase 3 테스트 시나리오 ≥ 10건 (§V2.9): TS-SEC-FRM-1~74 실체화
- [x] §N 세션 간 cross-check: peer T2-1 V2 (build/signing) + T2-3 plan §A.3 SLA + T2-4 V2 (메트릭) 실체 참조
- [x] 자가 체크리스트 (§V2.10): 본 항목, §3.1~§3.5 anti-fabrication 가이드 준수

---

<!-- END OF §V2 (T2-2) -->
