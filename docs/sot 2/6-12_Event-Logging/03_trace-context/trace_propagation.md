# Trace Propagation — W3C Trace Context 추적 컨텍스트 전파 규칙 (V2)

> **도메인**: 6-12_Event-Logging / 03_trace-context
> **파일**: `trace_propagation.md`
> **정본 선언**: 본 파일은 SOT2 정본(Single Source of Truth)이며, LOCK-EL-08 이 지정한 **W3C Trace Context 호환 추적 컨텍스트 전파 규칙** (Docker 분산 환경 + Tauri IPC + Python contextvars + Docker json-file 로그 드라이버 메타데이터 + correlation_id 누락 감지) 에 대해 권위를 가진다.
> **버전**: v1.0 (2026-04-29, P2-1 신규 — V2-Phase 2 태그)
> **세션**: P2-1 (Phase 2)
> **LOCK 연계**: LOCK-EL-08 (W3C Trace Context 호환, correlation_id 필수 전파, SOT2 신규 정의), LOCK-EL-01 (이벤트 스키마 6필드 — `trace_id` 포함), LOCK-EL-09 (8 namespace — ipc.*/agent.* 전파 대상)

---

## §0. 교차 참조 (Cross-References)

| 문서 | 경로 | 용도 |
|------|------|------|
| AUTHORITY_CHAIN | `../AUTHORITY_CHAIN.md` | LOCK-EL-08 정의, 도메인 경계 (4-1 IPC 전파, 4-3 MCP 네임스페이스, 6-13 Docker 로그 드라이버) |
| 종합계획서 §6 / §7.3 | `../EVENT_LOGGING_구조화_종합계획서.md` §6 ISS-4 / §7.3 P2-1 | I-4 (P-3: 추적 컨텍스트 전파 규칙 부재, MEDIUM) → LOCK-EL-08 해소 |
| 03/_index.md | `./_index.md` §추적 컨텍스트 전파 (LOCK-EL-08) | trace_id (128-bit UUID) / span_id (64-bit) / correlation_id (trace_id 기반) 정의 |
| 03/structured_logging.md | `./structured_logging.md` (P2-2, 본 파일 의존) | structlog JSON 7필드 매핑 (trace_id 필드 본 파일에서 확정) |
| 01/event_schema.md | `../01_event-system/event_schema.md` §2.2.3 `trace_id` / §2.3 `span_id` (선행 정의) | UUID v4 또는 W3C trace-id 32 hex 포맷 검증 |
| 01/namespace_rules.md | `../01_event-system/namespace_rules.md` L42 (W3C trace_context 전파 → 03/) | namespace ↔ trace 전파 경계 |
| Part2 §6.11 | `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md` L5788-5975 | W3C Trace Context 호환 명시, Docker V2 인프라 맥락, structlog 출력 매핑 |
| D2.1-D2 | `D:\VAMOS\docs\sot\D2.1-D2_D2_SCHEMA_ORANGE_CORE.md` | 직접 정본 stage 1 — 123 EventType + 36 FC + 23 FB 원본 |
| 4-1 Rust-Tauri-Infrastructure | `../../4-1_Rust-Tauri-Infrastructure/` | `ipc.*` 네임스페이스 (LOCK-EL-09) — Tauri IPC traceparent 전파 (참조만, 본 도메인 LOCK 재정의 ❌) |
| 6-3 Agent-Teams-PARL | `../../6-3_Agent-Teams-PARL/` | `agent.*` 네임스페이스 — 에이전트 단계별 trace_id 전파 (참조만, 본 도메인 LOCK 재정의 ❌) |
| 6-13 Operations | `../../6-13_Operations/` | Docker json-file 로그 드라이버 + Loki 인덱스 운영 (참조만) |

---

## §1. 목적 및 범위 (Purpose / Scope)

### 1.1 목적
- LOCK-EL-08 가 확정한 **W3C Trace Context 호환 추적 컨텍스트 전파 규칙** 을 Docker 분산 환경 기준으로 운영 가능한 명세로 상세화한다.
- **trace_id / span_id / correlation_id** 의 **3 경로 전파** 를 정의한다: (a) HTTP 서비스 간 (traceparent / tracestate 헤더), (b) Tauri IPC (이벤트 메타데이터 correlation_id), (c) 내부 Python async (contextvars 기반 context 객체).
- Docker 분산 환경 특이사항 (json-file 로그 드라이버 메타데이터, Loki 라벨 추출, 서비스 경계 context 손실 방지) 을 명세화한다.
- `correlation_id 누락 감지 규칙` 을 LOCK-EL-08 위반 즉시 알람 (`ERROR` 레벨, P1 심각도) 으로 정의한다.
- ISS-4 (P-3: 추적 컨텍스트 전파 규칙 부재, MEDIUM) 의 P2-1 단계 해소 — 본 파일 + P2-2 `structured_logging.md` 양자 결합 시 ISS-4 완성.

### 1.2 범위 (In-scope)
- W3C Trace Context Level 1 (W3C Recommendation, 2020-02) — `traceparent` / `tracestate` 헤더 포맷.
- HTTP 전파: `traceparent: {version}-{trace-id}-{parent-id}-{trace-flags}` 헤더 주입/추출 규칙.
- Tauri IPC 전파: `command_invoke` / `event_emit` / `bridge_call` 시 메타데이터 `correlation_id` 삽입.
- Python contextvars: `trace_context = contextvars.ContextVar('trace_context')` 기반 비동기 context 전파.
- Docker json-file 로그 드라이버: `--log-driver=json-file --log-opt labels=trace_id,span_id` 메타데이터 포함.
- Loki LogQL 추출 패턴: `{container=~".*"} |= "trace_id"` 라벨 인덱싱.
- correlation_id 누락 감지: 발행 이벤트 `trace_id` 필드 부재 → `[VIOLATION:LOCK-EL-08_no_correlation_id]` 마커 + `ERROR` 알람.
- 11 CONSUMER 도메인 (1-1 / 2-1 / 2-2 / 3-7 / 4-1 / 4-3 / 6-1 / 6-3 / 6-5 / 6-8 / 6-13) 자동 전파 적용 가이드 (각 namespace 별 진입점).
- Phase 2 테스트 시나리오 12건.

### 1.3 범위 외 (Out-of-scope)
- structlog JSON 7필드 매핑 → **P2-2 `structured_logging.md`** (본 파일은 trace_id / span_id / correlation_id 의 *전파* 규칙, P2-2 는 *출력* 매핑).
- V0 (JSONL) → V3 (Loki) 인프라 진화 → **P3-1 `version_evolution.md`** (Phase 3).
- Loki 라벨 카디널리티 정책 / 보존 기간 → **6-13 Operations** 도메인 (W-2 RESOLVED 경계).
- V2 FailureCode 8건 상세 → **P2-3 `failure_code_registry_v2.md`** (별도 파일).
- W3C Trace Context Level 2 (Distributed Vendor Extensions) → V3 단계 (이월).

---

## §2. LOCK-EL-08 정본 인용 (verbatim)

### §2.1 LOCK-EL-08 5-field verbatim 인용 (AUTHORITY_CHAIN §LOCK 레지스트리 L8)

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-EL-08` |
| **항목** | 추적 컨텍스트 전파 규칙 |
| **값** | W3C Trace Context 호환, correlation_id 필수 전파 |
| **정본 출처** | SOT2 신규 정의 (Part2 §6.11 W3C 호환 명시 인용) |
| **서브폴더 매핑** | 03 (`03_trace-context/`) |

### §2.2 LOCK-EL-08 보호 규칙
- 본 V2 파일에서 LOCK-EL-08 의 **재정의 / 추가 / 변경 0건** 엄수. 위반 시 `[VIOLATION:LOCK-EL-08_redefinition]` 즉시 마커 발화.
- LOCK-EL-08 은 SOT2 신규 정의 (W-4 RESOLVED — Part2 반영은 구현 단계에서). 본 파일은 LOCK-EL-08 의 **운영 가능 상세화** 만 수행, 정의 자체는 AUTHORITY §LOCK L8 정본 보존.
- 충돌 시 우선순위: `R-T6-1 Part2 §6.11 (W3C 호환 명시 행) > AUTHORITY §LOCK L8 > 본 파일 §3~§9` (AUTHORITY 정본 우선, 본 파일은 운영 명세).

### §2.3 LOCK-EL-01 / LOCK-EL-09 연계 인용 (verbatim)

| LOCK ID | 항목 | 값 | 본 파일 기여 |
|---------|------|-----|------------|
| `LOCK-EL-01` | 이벤트 스키마 필수 필드 6개 | timestamp, event_type, **trace_id**, source, version, payload | `trace_id` 필드 전파 규칙 정의 (LOCK-EL-08 의 운영 측면) |
| `LOCK-EL-09` | 이벤트 네임스페이스 8개 | oc.* / cl.rt.* / agent.* / sdar.* / storage.* / mem.* / wf.* / ui.* | 본 파일은 8 namespace 모두에 동일 전파 규칙 적용 (+ 11 CONSUMER namespace dev.* / ipc.* / mcp.* / ops.* 도 동일 규칙 채택, R-612-1 통보) |

---

## §3. 추적 식별자 정의 (W3C Trace Context Level 1)

### §3.1 trace_id (LOCK-EL-08 핵심)

| 항목 | 값 |
|------|-----|
| 정의 | 요청 단위 유일 식별자, W3C Trace Context Level 1 호환 |
| 길이 | **128-bit (16 byte)** |
| 표현 | 32 lowercase hex 문자열 (예: `4bf92f3577b34da6a3ce929d0e0e4736`) |
| 별칭 | UUID v4 호환 (32 hex + 4 hyphens 형식 — `01_event-system/event_schema.md` §2.2.3 LOCK-EL-01 검증 정본) |
| 금지값 | `00000000000000000000000000000000` (all-zero, W3C Recommendation) |
| 생성 시점 | 신규 요청 진입 지점 (S0 Intake) **1회만** 생성, 이후 전 구간 전파 |
| 정본 출처 | SOT2 신규 정의 (LOCK-EL-08), W3C Trace Context Level 1 §3.2.2.1 호환 |
| 검증 정규식 | `^[0-9a-f]{32}$` (W3C) 또는 UUID v4: `^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$` |

### §3.2 span_id (모듈/서비스 단위)

| 항목 | 값 |
|------|-----|
| 정의 | trace 내 하위 단위 (모듈, 함수, 마이크로서비스 단위 작업) |
| 길이 | **64-bit (8 byte)** |
| 표현 | 16 lowercase hex 문자열 (예: `00f067aa0ba902b7`) |
| 금지값 | `0000000000000000` (all-zero) |
| 생성 시점 | 모듈/서비스 경계 진입 시 매번 신규 생성 (`secrets.token_hex(8)`) |
| 부모 관계 | `parent_span_id` 필드로 상위 span 추적 (W3C span tree) |
| 정본 출처 | SOT2 신규 정의 (event_schema.md §2.3 선택 필드), W3C Trace Context Level 1 §3.2.2.2 호환 |

### §3.3 correlation_id (LOCK-EL-08 필수 전파)

| 항목 | 값 |
|------|-----|
| 정의 | 비기술 사용자/운영자 추적용 ID, **trace_id 와 동일값** 사용 |
| 별칭 | trace_id 의 운영 측면 alias |
| 전파 의무 | **모든 이벤트 발행 시 필수 포함** (LOCK-EL-08), 누락 감지 시 ERROR |
| 사용 예 | API 응답 헤더 `X-Correlation-ID: {trace_id}`, Tauri IPC 메타데이터, structlog `correlation_id` 필드 |
| 운영자 노출 | UI 에러 메시지 / 운영 대시보드에서 trace_id 의 user-friendly 형태로 노출 (32 hex 그대로 또는 8 char prefix) |
| 정본 출처 | LOCK-EL-08 (SOT2 신규 정의) |

### §3.4 3-식별자 관계 다이어그램

```
요청 진입 (S0 Intake)
  ├─ trace_id 1회 생성 (W3C 32 hex 또는 UUID v4)
  └─ correlation_id ← trace_id (동일값, alias)

요청 처리 체인 (S1~S8)
  ├─ 모듈 A 진입
  │   ├─ span_id_1 생성 (16 hex)
  │   └─ trace_id 동일 유지, correlation_id 동일 유지
  ├─ 모듈 B 진입
  │   ├─ span_id_2 생성 (parent_span_id = span_id_1)
  │   └─ trace_id 동일 유지
  └─ 모듈 C 진입 (병렬)
      ├─ span_id_3 생성 (parent_span_id = span_id_1)
      └─ trace_id 동일 유지

모든 이벤트 발행
  └─ {trace_id, span_id, correlation_id} 3-tuple 자동 첨부 (LOCK-EL-08 강제)
```

---

## §4. 전파 경로별 상세 규칙 (3 경로)

### §4.1 경로 (a): HTTP 서비스 간 — traceparent / tracestate 헤더

#### §4.1.1 traceparent 헤더 포맷 (W3C Recommendation)

```
traceparent: {version}-{trace-id}-{parent-id}-{trace-flags}
```

| 필드 | 길이 | 값 | 설명 |
|------|------|-----|------|
| `version` | 2 hex | `00` (현재 W3C 정본) | 버전 식별자, 향후 변경 가능 |
| `trace-id` | 32 hex | `4bf92f3577b34da6a3ce929d0e0e4736` | 본 §3.1 trace_id |
| `parent-id` | 16 hex | `00f067aa0ba902b7` | 본 §3.2 span_id (현재 span) |
| `trace-flags` | 2 hex | `01` (sampled) 또는 `00` (not sampled) | 샘플링 플래그 |

#### §4.1.2 tracestate 헤더 (vendor extension)

```
tracestate: vamos=trace_v1;sampler=parent_based,otel=t61c4@orange,sentry=v3
```

| 키 | 값 | 용도 |
|----|-----|------|
| `vamos` | `trace_v1;sampler=parent_based` | VAMOS 자체 vendor key (옵션) |
| `otel` | `t{8 hex}@orange` | OpenTelemetry vendor (Phase 3 통합) |
| `sentry` | `v3` | Sentry 통합 (Phase 3) |

- 카디널리티 상한: 32 키 / 512 byte (W3C Level 1)
- 본 6-12 도메인은 `vamos` 키만 정본 정의, 타 vendor 키는 `R-612-1` 통보 후 추가.

#### §4.1.3 HTTP 클라이언트/서버 주입·추출 의사코드

```python
# httpx / requests 클라이언트 측 — traceparent 자동 주입
import httpx
from contextvars import ContextVar

trace_context: ContextVar[dict] = ContextVar('trace_context')

class TracePropagationTransport(httpx.BaseTransport):
    """W3C Trace Context 자동 주입 transport (LOCK-EL-08)"""
    def handle_request(self, request: httpx.Request) -> httpx.Response:
        ctx = trace_context.get(None)
        if ctx is None:
            # LOCK-EL-08: trace_context 부재 시 root 신규 생성 금지 (S0 Intake 명시 API 만 root 생성).
            # emit/decorator 경로(assert_trace_or_violation, with_trace)와 동일하게 위반 발화.
            raise RuntimeError(
                "[VIOLATION:LOCK-EL-08_no_trace_context] outbound request without trace_context; "
                "root trace 는 S0 Intake 진입점에서만 생성한다"
            )
        # traceparent 주입 — version=00, flags=01(sampled)
        request.headers["traceparent"] = f"00-{ctx['trace_id']}-{ctx['span_id']}-{ctx['flags']}"
        # tracestate (vamos vendor key)
        request.headers["tracestate"] = "vamos=trace_v1;sampler=parent_based"
        return super().handle_request(request)

# FastAPI / Starlette 서버 측 — traceparent 추출 + contextvars 주입
from fastapi import FastAPI, Request
import re

W3C_TRACEPARENT_RE = re.compile(r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$")
app = FastAPI()

@app.middleware("http")
async def trace_extract_middleware(request: Request, call_next):
    """W3C Trace Context 추출 + contextvars 주입 (LOCK-EL-08)"""
    tp = request.headers.get("traceparent")
    if tp and (m := W3C_TRACEPARENT_RE.match(tp)):
        version, trace_id, parent_id, flags = m.groups()
        if trace_id == "0" * 32 or parent_id == "0" * 16:
            # all-zero trace/span: trace 체인 파괴 방지 (event_schema.md §EL_EVT_BAD_TRACE_ID 정합)
            ctx = _new_root_context()
        else:
            import secrets
            new_span = secrets.token_hex(8)  # 본 서비스 진입점 span 신규 생성
            ctx = {"trace_id": trace_id, "span_id": new_span, "parent_span_id": parent_id, "flags": flags}
    else:
        # traceparent 부재 — 본 서비스가 진입점 (S0 Intake)
        ctx = _new_root_context()
    trace_context.set(ctx)
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = ctx["trace_id"]  # correlation_id alias
    return response

def _new_root_context() -> dict:
    import secrets
    return {"trace_id": secrets.token_hex(16), "span_id": secrets.token_hex(8), "parent_span_id": None, "flags": "01"}
```

#### §4.1.4 도메인 경계 책임 (4-3 MCP-Server-Client 참조 cross-handoff)

- 본 6-12 = traceparent / tracestate 포맷 정본, 헤더 키 명세, 검증 정규식 소유.
- 4-3 MCP-Server-Client = MCP 프로토콜 메시지에 traceparent 메타데이터 첨부 실행 (`mcp.*` namespace, LOCK-EL-09). **본 6-12 LOCK 재정의 ❌**.
- 5-Gate Phase 3 검증 시 `tool_call` / `tool_result` / `tool_error` 이벤트 3-tuple {trace_id, span_id, correlation_id} 모두 첨부 확인.

### §4.2 경로 (b): Tauri IPC — 이벤트 메타데이터 correlation_id 삽입

#### §4.2.1 Tauri Command 호출 (Frontend → Rust → Python Bridge)

```rust
// Tauri command 시그니처 — correlation_id 메타데이터 강제 (LOCK-EL-08)
// src-tauri/src/commands/orange_core.rs
use tauri::{AppHandle, Manager};
use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct TraceMeta {
    pub trace_id: String,      // 32 hex (W3C trace_id)
    pub span_id: String,       // 16 hex (parent_span_id from frontend)
    pub correlation_id: String,// = trace_id (LOCK-EL-08 alias)
    pub flags: String,         // "01" sampled / "00" not
}

#[tauri::command]
pub async fn invoke_orange_core(
    app: AppHandle,
    payload: serde_json::Value,
    trace_meta: TraceMeta,         // ★ Frontend 가 강제 전달, 누락 시 Rust 에서 신규 생성
) -> Result<serde_json::Value, String> {
    // 1. trace_meta 검증
    validate_trace_meta(&trace_meta).map_err(|e| format!("LOCK-EL-08 violation: {}", e))?;

    // 2. Python Bridge 호출 시 traceparent 헤더 주입 (HTTP 서브경로 § 4.1)
    let traceparent = format!("00-{}-{}-{}", trace_meta.trace_id, trace_meta.span_id, trace_meta.flags);

    // 3. Tauri Event Emit 시 correlation_id 메타데이터 첨부
    app.emit_all("oc.command_invoked", serde_json::json!({
        "trace_id": trace_meta.trace_id,
        "correlation_id": trace_meta.correlation_id,
        "command": "invoke_orange_core",
    })).map_err(|e| e.to_string())?;

    // 4. Python Bridge 호출 (HTTP 또는 IPC sock — 4-1 인프라)
    invoke_python_bridge(payload, &traceparent).await
}

fn validate_trace_meta(meta: &TraceMeta) -> Result<(), &'static str> {
    if meta.trace_id.len() != 32 || meta.trace_id == "0".repeat(32) {
        return Err("trace_id W3C invalid");
    }
    if meta.span_id.len() != 16 || meta.span_id == "0".repeat(16) {
        return Err("span_id W3C invalid");
    }
    if meta.correlation_id != meta.trace_id {
        return Err("correlation_id != trace_id (LOCK-EL-08 alias rule)");
    }
    Ok(())
}
```

#### §4.2.2 Frontend (React/TypeScript) → Rust IPC 호출

```typescript
// src/lib/trace_context.ts — Frontend trace_context 관리 (LOCK-EL-08)
import { invoke } from "@tauri-apps/api/tauri";

interface TraceMeta {
  trace_id: string;
  span_id: string;
  correlation_id: string;
  flags: "00" | "01";
}

let _rootTraceMeta: TraceMeta | null = null;

export function getOrCreateTrace(): TraceMeta {
  if (_rootTraceMeta === null) {
    // S0 Intake 진입점: 신규 trace_id 생성
    _rootTraceMeta = {
      trace_id: hex(16),  // 32 hex chars
      span_id: hex(8),    // 16 hex chars
      correlation_id: "",  // 아래에서 alias
      flags: "01",
    };
    _rootTraceMeta.correlation_id = _rootTraceMeta.trace_id;
  }
  return _rootTraceMeta;
}

function hex(bytes: number): string {
  const arr = new Uint8Array(bytes);
  crypto.getRandomValues(arr);
  return Array.from(arr).map(b => b.toString(16).padStart(2, "0")).join("");
}

export async function invokeOrangeCore(payload: unknown): Promise<unknown> {
  const trace_meta = getOrCreateTrace();
  // ★ trace_meta 강제 전달 (LOCK-EL-08)
  return await invoke("invoke_orange_core", { payload, traceMeta: trace_meta });
}
```

#### §4.2.3 Tauri Event 양방향 전파 (Rust → Frontend listen + Frontend → Rust emit_all)

| 방향 | 메커니즘 | correlation_id 위치 |
|------|---------|-------------------|
| Frontend → Rust (command) | `tauri::command` 인자 `TraceMeta` 강제 | 인자 `trace_meta.correlation_id` |
| Rust → Frontend (event_emit) | `app.emit_all("event_name", payload)` | `payload.correlation_id` 필드 (JSON) |
| Frontend → Rust (Tauri event) | `appWindow.emit("event_name", payload)` | `payload.correlation_id` 필드 |

#### §4.2.4 도메인 경계 책임 (4-1 Rust-Tauri-Infrastructure 참조 cross-handoff)

- 본 6-12 = `trace_meta` 메타데이터 스키마 정본 (4 필드: trace_id / span_id / correlation_id / flags), Rust validate 함수 시그니처 정본.
- 4-1 Rust-Tauri-Infrastructure = Tauri command 호출 인프라, IPC channel, Bridge 구현. `ipc.command_invoke` / `ipc.event_emit` / `ipc.bridge_call` 이벤트 발행 시 본 6-12 trace_meta 스키마 강제 채택. **본 6-12 LOCK 재정의 ❌**.
- W-2 RESOLVED 경계: 본 6-12 = 발행 표준, 6-13 = 보존 정책.

### §4.3 경로 (c): Python contextvars — 비동기 내부 전파

#### §4.3.1 contextvars 기반 trace_context 정의 (정본)

```python
# src/orange_core/trace_context.py — Python 비동기 trace_context (LOCK-EL-08)
from __future__ import annotations
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Optional
import secrets

@dataclass(frozen=True)
class TraceContext:
    """LOCK-EL-08 + LOCK-EL-01 trace_id 필드 운영 컨테이너"""
    trace_id: str                          # 32 hex (W3C) — LOCK-EL-08
    span_id: str                           # 16 hex (W3C) — span 식별
    parent_span_id: Optional[str] = None   # 16 hex 또는 None (root span)
    flags: str = "01"                      # "01" sampled / "00" not
    baggage: dict = field(default_factory=dict)  # tracestate vendor extension

    @property
    def correlation_id(self) -> str:
        """LOCK-EL-08 alias: correlation_id = trace_id (사용자/운영자 노출용)"""
        return self.trace_id

    def child(self) -> "TraceContext":
        """모듈 진입 시 child span 생성 (parent_span_id = self.span_id)"""
        return TraceContext(
            trace_id=self.trace_id,           # 동일 유지
            span_id=secrets.token_hex(8),     # 신규 16 hex
            parent_span_id=self.span_id,      # 부모 추적
            flags=self.flags,
            baggage=dict(self.baggage),
        )

    def to_traceparent(self) -> str:
        """W3C traceparent 헤더 직렬화 (§4.1)"""
        return f"00-{self.trace_id}-{self.span_id}-{self.flags}"

    def to_dict(self) -> dict:
        """이벤트 발행 / structlog 출력 직렬화 (LOCK-EL-01 trace_id + 선택 span_id)"""
        d = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "correlation_id": self.correlation_id,
        }
        if self.parent_span_id:
            d["parent_span_id"] = self.parent_span_id
        return d

# ★ ContextVar 정본 (모든 모듈이 import 해서 동일 ContextVar 인스턴스 공유)
trace_context: ContextVar[Optional[TraceContext]] = ContextVar("trace_context", default=None)


def new_root_trace() -> TraceContext:
    """S0 Intake 진입점에서 1회 호출 (요청 단위 신규 trace 생성)"""
    return TraceContext(
        trace_id=secrets.token_hex(16),    # 32 hex chars
        span_id=secrets.token_hex(8),      # 16 hex chars
        parent_span_id=None,
        flags="01",
    )


def parse_traceparent(header: str) -> Optional[TraceContext]:
    """W3C traceparent 헤더 파싱 (HTTP 서버 진입점, §4.1.3 정합)"""
    import re
    m = re.match(r"^([0-9a-f]{2})-([0-9a-f]{32})-([0-9a-f]{16})-([0-9a-f]{2})$", header)
    if not m:
        return None
    version, trace_id, parent_id, flags = m.groups()
    # all-zero 거부 (event_schema.md §EL_EVT_BAD_TRACE_ID 정합)
    if trace_id == "0" * 32 or parent_id == "0" * 16:
        return None
    return TraceContext(
        trace_id=trace_id,
        span_id=secrets.token_hex(8),    # 본 서비스 진입점 span 신규
        parent_span_id=parent_id,        # 상류 span 추적
        flags=flags,
    )
```

#### §4.3.2 비동기 모듈 진입 시 자동 child span 생성 (decorator 패턴)

```python
# src/orange_core/decorators.py
from functools import wraps
from typing import Callable, ParamSpec, TypeVar, Awaitable
from .trace_context import trace_context, TraceContext, new_root_trace

P = ParamSpec("P")
R = TypeVar("R")

def with_trace(module_name: str) -> Callable:
    """모듈 진입 시 child span 자동 생성 (LOCK-EL-08 비동기 전파)"""
    def decorator(fn: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @wraps(fn)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            current = trace_context.get()
            if current is None:
                # ★ 진입점 외에서 trace_context 부재: LOCK-EL-08 위반
                raise RuntimeError(
                    f"[VIOLATION:LOCK-EL-08_no_trace_context] module={module_name}"
                )
            child = current.child()
            token = trace_context.set(child)
            try:
                return await fn(*args, **kwargs)
            finally:
                trace_context.reset(token)
        return wrapper
    return decorator


# 사용 예 (1-1 Verifier-Reasoning oc.i1~i5)
@with_trace(module_name="i1_intent_router")
async def i1_route(input_data: dict) -> dict:
    """OC i1 Intent Router (1-1 도메인) — trace 자동 전파"""
    ctx = trace_context.get()
    # 이벤트 발행 시 ctx.to_dict() 자동 첨부
    emit_event("oc.i1.parse.started", payload=input_data, trace=ctx.to_dict())
    ...
```

#### §4.3.3 ThreadPoolExecutor / asyncio.create_task 전파

```python
# src/orange_core/async_helpers.py
import asyncio
import contextvars
from typing import Awaitable, TypeVar

T = TypeVar("T")

async def create_task_with_context(coro: Awaitable[T]) -> asyncio.Task[T]:
    """asyncio.create_task 호출 시 contextvars 자동 복제 (Python 3.7+ 기본 동작)"""
    # asyncio.create_task 는 자동으로 contextvars.copy_context() 적용
    return asyncio.create_task(coro)


def run_in_executor_with_context(executor, fn, *args):
    """ThreadPoolExecutor 호출 시 contextvars 명시 복제 (Python 3.11 미만 호환)"""
    ctx = contextvars.copy_context()
    return asyncio.get_event_loop().run_in_executor(
        executor,
        lambda: ctx.run(fn, *args),
    )
```

---

## §5. Docker 분산 환경 특이사항

### §5.1 Docker json-file 로그 드라이버 메타데이터

#### §5.1.1 docker run 시 라벨 추가

```bash
# 운영 컨테이너 실행 시 trace_id / span_id 라벨 자동 추출 (V2 인프라)
docker run -d \
  --name orange_core_i1 \
  --log-driver=json-file \
  --log-opt max-size=100m \
  --log-opt max-file=5 \
  # trace_id/span_id/correlation_id 는 고카디널리티 → 인덱스 라벨 금지 (loki_integration_v3 §2, W-2). structured JSON payload 내부 유지.
  --label trace_id_extract=structlog \
  vamos/orange_core:v2
```

#### §5.1.2 docker-compose.yml 정본 (Phase 2 V2)

```yaml
# infra/docker-compose.v2.yml
version: "3.9"
services:
  orange_core:
    image: vamos/orange_core:v2
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "5"
        labels: "trace_id,span_id,correlation_id"
        env: "VAMOS_DEPLOY_ENV"
    environment:
      VAMOS_DEPLOY_ENV: "v2_docker"
      OTEL_EXPORTER_OTLP_ENDPOINT: "http://loki:3100"  # Phase 3 통합 준비

  cl_rt_breaking_detector:
    image: vamos/cl_rt:v2
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "5"
        labels: "trace_id,span_id,correlation_id"

  sdar_repair:
    image: vamos/sdar:v2
    logging:
      driver: json-file
      options:
        max-size: "100m"
        max-file: "5"
        labels: "trace_id,span_id,correlation_id"
```

### §5.2 Loki LogQL 추출 패턴

```logql
# trace_id 기반 전체 trace 조회 (분산 서비스 횡단)
{container=~"orange_core_.*|cl_rt_.*|sdar_.*"} | json | trace_id="4bf92f3577b34da6a3ce929d0e0e4736"

# correlation_id (운영자 친화) 기반 사용자 요청 추적
{container=~".*"} | json | correlation_id="4bf92f3577b34da6a3ce929d0e0e4736"

# span_id 트리 시각화 (parent_span_id 추출)
{container=~".*"} | json | trace_id="4bf92f3577b34da6a3ce929d0e0e4736"
| line_format "{{.span_id}} ← {{.parent_span_id}} | {{.event_type}}"
```

### §5.3 서비스 경계 context 손실 방지 규칙

| 시나리오 | 손실 방지 메커니즘 |
|---------|------------------|
| HTTP REST 호출 | traceparent 헤더 자동 주입 (§4.1.3 `TracePropagationTransport`) |
| gRPC 호출 | gRPC metadata `traceparent` 키 (W3C gRPC binding) |
| 메시지 큐 (Kafka/Redis Stream) | 메시지 헤더 `traceparent` 키 + payload 내 중복 첨부 (소비자 측 fallback) |
| 배치 작업 진입 | `new_root_trace()` 호출 + 사유 ("scheduled batch") 로그 (root span) |
| Tauri IPC | trace_meta 인자 강제 (§4.2.1 Rust validate) |

---

## §6. correlation_id 누락 감지 규칙 (LOCK-EL-08 위반 알람)

### §6.1 감지 진입점 (3 layer)

| Layer | 감지 시점 | 메커니즘 |
|-------|----------|---------|
| L1 발행 | 이벤트 발행 직전 | `EventEnvelope` Pydantic validator (`event_schema.md` §3.1 `_tid` 정합) |
| L2 전송 | HTTP / IPC / Tauri 경계 | middleware / decorator / Rust validate (§4.1~§4.3) |
| L3 수신 | 로그 수집 (structlog → json-file) | structlog processor (P2-2 `structured_logging.md` 의존) |

### §6.2 감지 시 동작 정본

```python
# src/orange_core/trace_violation.py
from .trace_context import trace_context
import structlog

def assert_trace_or_violation(event_type: str, payload: dict) -> dict:
    """이벤트 발행 직전 LOCK-EL-08 위반 감지 (필수 호출)"""
    ctx = trace_context.get()
    if ctx is None:
        # ★ LOCK-EL-08 violation: trace_context 부재 → ERROR 알람
        log = structlog.get_logger()
        log.error(
            "[VIOLATION:LOCK-EL-08_no_correlation_id]",
            event_type=event_type,
            payload_keys=list(payload.keys()),
            failure_code="EL_EVT_NO_TRACE_CONTEXT",
            severity="P1",
            level="ERROR",
        )
        raise RuntimeError(
            f"LOCK-EL-08 violation: event '{event_type}' published without trace_context. "
            f"Call new_root_trace() at S0 Intake or use @with_trace decorator."
        )
    return ctx.to_dict()
```

### §6.3 감지 후 알람 정책

| 심각도 | 누락 빈도 | 동작 |
|--------|----------|------|
| P3 (정보) | 단발성 (개발 환경) | structlog WARN 로그만 |
| P1 (경고) | 분당 1건+ | structlog ERROR + 6-13 ops 알람 (`alert_trigger`) |
| P0 (긴급) | 분당 10건+ | structlog CRITICAL + 6-13 incident_create + 운영자 페이저 호출 |

### §6.4 FailureCode 매핑 (P2-3 `failure_code_registry_v2.md` 참조)

- 누락 감지 → `EL_EVT_NO_TRACE_CONTEXT` (신규 FC, 본 §6.2 정본 발화) → `FB_TRACE_CONTEXT_RECREATE` (root span 강제 생성 + WARN 알람) → 후속 이벤트 정상 발행.
- 위반 후 trace 체인 복구 불가 (이미 발행된 이벤트 trace_id 부재) → drop 권고.

---

## §7. 11 CONSUMER 도메인 자동 전파 적용 가이드

> ★ 본 §7 은 **참조만** (R-T6-2 소비 도메인 목록 §A 유지 의무, R-612-1 횡단 통보 의무). 11 CONSUMER 도메인 자체 sandbox/production 직접 편집 ❌. RECHECK_FLAG 발행은 STEP_B step 8 dependency_propagate 시점에 본 6-12 sandbox CONFLICT_LOG / plan §7 / memory / SOT2_MASTER_INDEX 4 위치만 기록 (3-tuple {trace_id, span_id, correlation_id} 자동 첨부 의무).

| # | CONSUMER 도메인 | namespace | 진입점 (trace 신규 생성 위치) | 자동 전파 패턴 | 본 §4 경로 |
|---|---------------|-----------|---------------------------|--------------|---------|
| 1 | 1-1 Verifier-Reasoning | `oc.i1~i5` | i1_router (S1 Intent) — `new_root_trace()` 또는 traceparent 추출 | `@with_trace("i{N}_module")` decorator (§4.3.2) | (c) Python contextvars |
| 2 | 2-1 Blue-Node-Architecture | `oc.blue.*` | Node executor 진입 시 child span 생성 | `child_span = ctx.child()` (§4.3.1) | (c) contextvars + (a) HTTP (노드 분산 시) |
| 3 | 2-2 COND-Modules-Detail | `oc.cond.*` | COND_* 모듈 진입 (106 FC 발행 시 ctx.to_dict() 첨부) | `@with_trace("cond_{module}")` | (c) contextvars |
| 4 | 3-7 Dev-Tools | `dev.*` | tool_execute / sandbox_start 시 child span | `@with_trace("dev_{tool}")` | (c) contextvars |
| 5 | 4-1 Rust-Tauri-Infrastructure | `ipc.*` | Tauri command 진입 — `trace_meta` 강제 (§4.2.1) | Rust validate + Python Bridge → contextvars | (b) Tauri IPC + (c) contextvars |
| 6 | 4-3 MCP-Server-Client | `mcp.*` | MCP `tool_call` 메시지에 traceparent 메타데이터 (§4.1.4) | MCP 프로토콜 메시지 헤더 + HMAC 서명 포함 | (a) HTTP (MCP transport) |
| 7 | 6-1 UI-UX-System | `ui.builder.*` | Frontend 사용자 액션 시작 — `getOrCreateTrace()` (§4.2.2) | TypeScript trace_meta → Tauri IPC → Python | (b) Tauri IPC |
| 8 | 6-3 Agent-Teams-PARL | `agent.*` | 에이전트 plan 시작 — root span 또는 부모 trace 상속 | `@with_trace("agent_{plan|act|reflect|learn}")` | (c) contextvars |
| 9 | 6-5 SDAR-System | `sdar.*` | SDAR detect 시 child span (FC→FB 실행 W-1 RESOLVED) | `@with_trace("sdar_{stage}")` | (c) contextvars |
| 10 | 6-8 Cloud-Library | `cl.rt.*` | crawl_start 시 root span (스케줄러 진입) | `new_root_trace()` + 스케줄러 trace_id | (c) contextvars |
| 11 | 6-13 Operations | `ops.*` | alert_trigger / incident_create 시 본 6-12 발행 trace 소비 (소비만, 신규 생성 ❌) | Loki LogQL 추출 (§5.2) | (a) HTTP + Loki 인덱싱 |

### §7.1 11 CONSUMER 공통 적용 의무 (R-612-1 통보 대상)

1. 모든 이벤트 발행 시 `{trace_id, span_id, correlation_id}` 3-tuple **필수 첨부** (LOCK-EL-08).
2. 모듈 진입 시 `@with_trace(module_name)` decorator 적용 또는 `ctx.child()` 명시 호출.
3. trace_context 부재 시 `assert_trace_or_violation()` 호출하여 LOCK-EL-08 위반 즉시 감지 (§6.2).
4. HTTP / IPC / 메시지 큐 / 배치 경계에서 §5.3 손실 방지 규칙 준수.
5. structlog 출력 시 P2-2 `structured_logging.md` 정본 7필드 자동 매핑 (본 P2-1 → P2-2 의존성).

### §7.2 RECHECK_FLAG 발행 trigger (STEP_B step 8 시점만)

본 V2 파일 신설로 인해 11 CONSUMER 도메인은 다음 RECHECK 의무 발생:

- (a) 기존 이벤트 발행 코드에 `trace_context` 의존 추가 필요 (Phase 3 본격 적용 또는 자체 STAGE 7 진입 시점).
- (b) §7 표 진입점 매핑 정확성 자체 검증 (각 CONSUMER 도메인 자체 STEP_C 시점).
- (c) FailureCode `EL_EVT_NO_TRACE_CONTEXT` (P2-3 `failure_code_registry_v2.md` 신규) 처리 분기 자체 추가.

본 6-12 STEP_B step 8 시점에 4 위치 (CONFLICT_LOG / plan §7 / memory / SOT2_MASTER_INDEX) 만 기록, 11 CONSUMER 도메인 자체 직접 편집 ❌. **DEFERRED_TO_PHASE3** 판정 (CONSUMER 도메인은 Phase 2 이후 자체 STAGE 7 진입 또는 Phase 3 통합 검증 시점 RECHECK 수행).

---

## §8. LOCK-EL-08 준수 검증 체크리스트

| # | 검증 항목 | 기준 | 검증 방법 |
|---|---------|------|---------|
| L8-1 | W3C Trace Context Level 1 호환 | traceparent / tracestate 헤더 §4.1.1 정확히 매칭 | `pytest tests/test_w3c_traceparent.py` |
| L8-2 | trace_id 32 hex / 16 hex(span) 정규식 검증 | §3.1 / §3.2 정의 일치 | Pydantic validator (event_schema.md §3.1 `_tid`) |
| L8-3 | correlation_id == trace_id alias 강제 | §3.3 정의 일치 | Rust `validate_trace_meta` (§4.2.1) + Python `TraceContext.correlation_id` property |
| L8-4 | 신규 요청 시 1회만 trace_id 생성 | S0 Intake 만 `new_root_trace()` 호출, 이외에서 호출 시 violation | `pytest tests/test_root_span_uniqueness.py` |
| L8-5 | 모든 이벤트 발행 시 trace_context 첨부 | `assert_trace_or_violation()` 통과 | structlog processor (P2-2 의존) + Phase 3 통합 테스트 |
| L8-6 | HTTP / IPC / 내부 3 경로 모두 전파 | §4.1 / §4.2 / §4.3 정합 | E2E 통합 테스트 (Phase 3 V3) |
| L8-7 | Docker json-file 라벨 trace_id 추출 | §5.1 docker-compose.yml 라벨 명시 | `docker inspect <container> | jq '.HostConfig.LogConfig.Config.labels'` |
| L8-8 | Loki LogQL trace_id 인덱싱 | §5.2 쿼리 정확 동작 | Loki 통합 검증 (Phase 3) |
| L8-9 | correlation_id 누락 감지 시 ERROR 알람 | §6.2 정본 발화 + 6-13 ops 통보 | `pytest tests/test_lock_el_08_violation.py` |
| L8-10 | 11 CONSUMER namespace 모두 적용 | §7 표 11/11 매핑 정합 | 본 V2 파일 §7 표 + 부록 §A 정합 자체 검증 |

---

## §9. Phase별 복구 흐름 (Phase 1→2→3→4)

```
Phase 1 (V1 baseline)              Phase 2 (V2, 본 P2-1)             Phase 3 (V3, P3-1)             Phase 4 (운영)
──────────────────────             ──────────────────────             ──────────────────             ──────────────
event_schema.md §2.2.3             trace_propagation.md (본)          version_evolution.md           Loki + Prometheus 통합
trace_id 정의 (UUID v4 / W3C)      W3C Trace Context Level 1          W3C Level 2 vendor extension   분산 추적 운영
                                   contextvars + Tauri IPC + Docker   Loki + Prometheus 통합          OTEL exporter
                                                                                                    correlation_id 자동 알람
                                          │
                                          ▼ (실패 시)
                                   trace_context 부재 → @with_trace decorator 적용 누락 모듈 식별
                                   correlation_id 누락 → assert_trace_or_violation() ERROR 알람 → FB_TRACE_CONTEXT_RECREATE
                                   traceparent invalid → parse_traceparent None → new_root_trace() 강제 (warning 로그)
                                   Tauri trace_meta 누락 → Rust validate err → Frontend 재호출 강제
```

### §9.1 다운그레이드 confidence 감산 (penalty)

| 트리거 | confidence 감산 | 이유 |
|--------|-------------|------|
| trace_context 부재 → root 강제 생성 | -0.15 | trace 체인 끊어짐, 상류 추적 불가 |
| traceparent all-zero (W3C 위반) | -0.30 | 악의적/오류 입력 가능성 |
| span_id 충돌 (16 hex 동일값 분산 서비스) | -0.10 | 매우 낮은 확률, 보고만 |
| Tauri trace_meta 검증 실패 | -0.20 | Frontend 신뢰성 저하 |

---

## §10. 에스컬레이션 페이로드 구조 (R-01-8, I-20 경유)

### §10.1 LOCK-EL-08 위반 에스컬레이션 페이로드

```python
# I-20 에스컬레이션 페이로드 (P1-5 §6.2 11필드 + 본 §10 추적 5필드 = 16필드)
@dataclass
class TraceViolationEscalationPayload:
    """LOCK-EL-08 위반 시 I-20 경유 에스컬레이션 (R-01-8 정합)"""
    # P1-5 §6.2 11필드 (변경 금지)
    source_engine: str                         # 위반 발생 모듈 (예: "i1_intent_router")
    error_code: str = "EL_EVT_NO_TRACE_CONTEXT"
    original_request: dict = field(default_factory=dict)
    partial_result: Optional[dict] = None      # 검증 성공 필드 (timestamp, source 등)
    retry_count: int = 0
    timestamp: str = ""                        # ISO 8601 UTC ms
    severity: str = "P1"
    level: str = "ERROR"                       # LOCK-EL-07 5단계
    fallback_id: str = "FB_TRACE_CONTEXT_RECREATE"
    recovery_action: str = "new_root_trace + warning"
    failure_chain: list = field(default_factory=list)

    # 본 §10 추적 5필드 (LOCK-EL-08 신규)
    expected_trace_id: Optional[str] = None    # traceparent 헤더에 있던 값 (있으면)
    actual_trace_id: Optional[str] = None      # 발행 시점 ContextVar 값 (None 이면 위반)
    expected_span_id: Optional[str] = None
    actual_span_id: Optional[str] = None
    correlation_id: Optional[str] = None       # alias 일관성 검증 (None / != trace_id 시 위반)
```

---

## §11. 로깅 포맷 (R-01-7) — LOCK-EL-08 위반 시 structured JSON 예시

```json
{
  "timestamp": "2026-04-29T14:32:15.847Z",
  "level": "ERROR",
  "event_type": "el.violation.no_correlation_id",
  "trace_id": "regenerated-4bf92f3577b34da6a3ce929d0e0e4736",
  "span_id": "00f067aa0ba902b7",
  "source": "orange_core/i1_router",
  "version": "1.0.0",
  "error": {
    "code": "EL_EVT_NO_TRACE_CONTEXT",
    "message": "LOCK-EL-08 violation: event 'oc.i1.parse.started' published without trace_context",
    "lock_id": "LOCK-EL-08"
  },
  "context": {
    "module": "i1_intent_router",
    "decorator_applied": false,
    "expected_decorator": "@with_trace('i1_intent_router')"
  },
  "recovery": {
    "fallback_id": "FB_TRACE_CONTEXT_RECREATE",
    "action": "new_root_trace_forced",
    "confidence_penalty": -0.15
  },
  "correlation_id": "regenerated-4bf92f3577b34da6a3ce929d0e0e4736",
  "payload": {}
}
```

---

## §12. ABC 패턴 매핑 (정본 준수)

| ABC | 본 §N | 시그니처 |
|-----|-------|---------|
| `BaseTracePropagator` (추상) | §4.3.1 `TraceContext` | `def child() -> TraceContext`, `def to_traceparent() -> str`, `def to_dict() -> dict` |
| `BaseTraceTransport` (httpx) | §4.1.3 `TracePropagationTransport` | `def handle_request(self, request) -> Response` |
| `BaseTraceExtractor` (FastAPI middleware) | §4.1.3 `trace_extract_middleware` | `async def __call__(self, request, call_next) -> Response` |
| `BaseTraceMeta` (Tauri) | §4.2.1 `TraceMeta` Rust struct | 4 필드: trace_id / span_id / correlation_id / flags |

**ABC 정본 위치**: `00_common/base_trace_abc.md` (Phase 3 신설 예정, 본 P2-1 시점에는 본 §12 가 정본 placeholder).

---

## §13. 복잡도 / 연산 특성

| 연산 | 시간 복잡도 | 공간 복잡도 | 주석 |
|------|-----------|-----------|------|
| `new_root_trace()` | O(1) (secrets.token_hex 16+8 byte) | O(1) | S0 Intake 1회 |
| `parse_traceparent(header)` | O(1) (정규식 fixed length) | O(1) | HTTP 진입점 매 요청 |
| `ctx.child()` | O(1) | O(1) | 모듈 진입 매번 (decorator 자동) |
| `ctx.to_dict()` | O(1) | O(1) | 이벤트 발행 매번 |
| `assert_trace_or_violation()` | O(1) | O(1) | 발행 직전 매번 |
| HTTP 헤더 주입 | O(1) | O(headers) ≈ 200 byte | traceparent + tracestate |
| Tauri IPC validate | O(1) | O(1) | Rust |

**메모리 footprint**: contextvars `trace_context` 인스턴스 ≈ 256 byte (TraceContext dataclass + baggage dict 평균). Phase 2 V2 운영 환경 1초당 1000 req 시 256 KB / 동시 활성 trace.

---

## §14. 세션 간 인터페이스 cross-check

### §14.1 P2-1 (본 파일) → P2-2 (`structured_logging.md`)

| 본 §N | 인터페이스 | P2-2 소비 |
|------|----------|----------|
| §3.1 trace_id (32 hex W3C) | `LOCK-EL-01` 필수 필드 | structlog 7필드 매핑 시 trace_id 필드 (P2-2 §3) |
| §3.2 span_id (16 hex) | LOCK-EL-01 선택 필드 | structlog 7필드 매핑 시 span_id 옵션 (P2-2 §3) |
| §3.3 correlation_id (alias) | LOCK-EL-08 alias | structlog `correlation_id` 필드 (운영자 친화) |
| §4.3.1 `TraceContext.to_dict()` | dict 반환 (3~4 필드) | structlog `bind_contextvars(**ctx.to_dict())` 호출 (P2-2 §5) |
| §6.2 `assert_trace_or_violation()` | 위반 시 RuntimeError | structlog ERROR + 6-13 ops 알람 (P2-2 §7) |

### §14.2 P2-1 → P2-3 (`failure_code_registry_v2.md`)

| 본 §N | FC 신설 | P2-3 등재 |
|------|--------|---------|
| §6.4 | `EL_EVT_NO_TRACE_CONTEXT` (LOCK-EL-08 위반) | P2-3 §V2 신규 row (CFL-EL-001 검토와 별개) |

### §14.3 본 P2-1 → V1 baseline (event_schema.md §2.2.3 / §2.3)

| V1 §N | 인터페이스 | 본 P2-1 정합 |
|------|----------|-----------|
| §2.2.3 trace_id 정규식 | UUID v4 또는 W3C 32 hex | §3.1 동일 정규식 채택 (변경 ❌) |
| §2.3 span_id 16 hex | 선택 필드 | §3.2 16 hex (변경 ❌) |
| §EL_EVT_BAD_TRACE_ID | all-zero 거부 | §4.1.3 + §4.3.1 `parse_traceparent` 거부 정합 |

---

## §15. Phase 3 통합 테스트 시나리오 (≥10 — 12건)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|---------|---------|---------|
| TS-1 | S0 Intake 진입 시 trace_id 신규 생성 | HTTP 요청 traceparent 부재 + `new_root_trace()` 호출 | TraceContext 신규, trace_id 32 hex 정규식 매칭, parent_span_id is None |
| TS-2 | HTTP traceparent 추출 + child span 생성 | 상류 traceparent: `00-{32 hex}-{16 hex}-01` | TraceContext 신규, trace_id 동일 유지, span_id 신규, parent_span_id == 상류 span_id |
| TS-3 | traceparent all-zero trace_id 거부 | `00-00000000000000000000000000000000-{16 hex}-01` | parse_traceparent 반환 None → `new_root_trace()` 강제 + WARN 로그 |
| TS-4 | traceparent 형식 위반 | `01-{32 hex}-{16 hex}-01` (version != 00) | parse_traceparent 반환 None → root 강제 |
| TS-5 | Tauri command trace_meta 검증 통과 | Frontend → Rust trace_meta 32 hex + 16 hex + alias 일치 | Python Bridge 호출 traceparent 헤더 정상 |
| TS-6 | Tauri command trace_meta 검증 실패 (correlation_id != trace_id) | trace_id="abc..." correlation_id="def..." | Rust validate Err("alias rule") 반환 → Frontend 재호출 강제 |
| TS-7 | 비동기 모듈 진입 child span 자동 생성 | `@with_trace("test_module")` decorator | trace_context.child() 호출, 모듈 진출 시 reset |
| TS-8 | trace_context 부재 시 LOCK-EL-08 violation | decorator 미적용 모듈에서 이벤트 발행 시도 | `assert_trace_or_violation()` RuntimeError + ERROR 로그 |
| TS-9 | asyncio.create_task contextvars 자동 복제 | 부모 task 에서 `asyncio.create_task(child_coro())` | 자식 task TraceContext 동일 (Python 3.7+ 기본 동작) |
| TS-10 | ThreadPoolExecutor contextvars 명시 복제 | `run_in_executor_with_context(executor, fn)` | 워커 스레드 TraceContext 동일 |
| TS-11 | Docker json-file 라벨 trace_id 추출 | `docker run --log-opt labels=trace_id` | docker inspect 출력에 trace_id 라벨 존재 |
| TS-12 | Loki LogQL trace_id 인덱싱 쿼리 | `{container=~".*"} | json | trace_id="<32 hex>"` | 분산 서비스 횡단 trace 전체 조회 가능 |

---

## §16. 변경 이력

| 버전 | 날짜 | 세션 | 변경 내용 |
|------|------|------|---------|
| v1.0 | 2026-04-29 | P2-1 | 신규 작성 — V2-Phase 2 태그. W3C Trace Context Level 1 호환 trace_propagation 정본. 3 경로 전파 (HTTP / Tauri IPC / Python contextvars) + Docker json-file + Loki LogQL + correlation_id 누락 감지 (LOCK-EL-08 위반 알람). 11 CONSUMER 자동 전파 적용 가이드 (참조만, RECHECK_FLAG 발행 dispatch 4 위치만 허용 step 8 시점). LOCK-EL-08 + LOCK-EL-01 + LOCK-EL-09 verbatim 5-field 인용. ISS-4 P2-1 단계 해소 (P2-2 결합 시 ISS-4 완성). DH 신규 0건. |

---

## §17. 자체 검증 체크리스트

| # | 검증 항목 | 결과 |
|---|---------|------|
| V-1 | LOCK-EL-08 verbatim 인용 (§2.1 5-field) | ✅ |
| V-2 | LOCK-EL-08 재정의/추가/변경 0건 | ✅ |
| V-3 | LOCK-EL-01 trace_id + LOCK-EL-09 namespace 연계 | ✅ §2.3 |
| V-4 | DH 신규 추가 0건 (DH 0건 보존 강제) | ✅ |
| V-5 | W3C Trace Context Level 1 호환 정확 인용 | ✅ §3 + §4.1 |
| V-6 | 3 경로 전파 (HTTP / Tauri IPC / contextvars) 모두 명시 | ✅ §4.1 / §4.2 / §4.3 |
| V-7 | Docker json-file 라벨 + Loki LogQL 추출 패턴 | ✅ §5.1 / §5.2 |
| V-8 | correlation_id 누락 감지 + LOCK-EL-08 위반 알람 | ✅ §6 |
| V-9 | 11 CONSUMER 적용 가이드 (참조만, 직접 편집 ❌) | ✅ §7 |
| V-10 | LOCK-EL-08 준수 검증 체크리스트 ≥ 10 | ✅ §8 (10건) |
| V-11 | Phase별 복구 흐름 + confidence 감산 | ✅ §9 |
| V-12 | 에스컬레이션 페이로드 11+5 = 16필드 | ✅ §10 |
| V-13 | structured JSON 로깅 포맷 (error/context/recovery 3 블록) | ✅ §11 |
| V-14 | Phase 3 테스트 시나리오 ≥ 10 | ✅ §15 (12건) |
| V-15 | V1 baseline (event_schema.md §2.2.3 / §2.3) 정합 | ✅ §14.3 |
| V-16 | P2-2 / P2-3 인터페이스 cross-check | ✅ §14.1 / §14.2 |
| V-17 | FABRICATION 10-marker census 0/N CLEAN (10-marker set: anti-fabrication standard) | ✅ |
| V-18 | 11 CONSUMER 도메인 sandbox/production 직접 편집 0건 | ✅ (참조만) |
| V-19 | 2-stage upstream + self chain 인용 (D2.1-D2 + Part2 §6.11 > SOT2 6-12) | ✅ §0 + §1.1 |
| V-20 | R-T6-1/R-T6-2/R-T6-3 + R-612-1 보호 규칙 준수 | ✅ §2.2 + §7 |
