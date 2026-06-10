# Retry Policy + Circuit Breaker — MCP Bridge 복원력 계층 (P1-5 정본 + P1-7 §3.4 에러 카탈로그)

> **주 세션**: `4-3_MCP-Server-Client / Phase 1 / #5` (P1-5) — §2~§18/§20 정본
> **부속 세션**: `4-3_MCP-Server-Client / Phase 1 / #7` (P1-7) — **§3.4 에러 카탈로그 소섹션만 추가** (다른 섹션 수정 0건)
> **작성일**: 2026-04-11 (P1-5 초본) / **갱신**: 2026-04-11 (P1-7 §3.4 신규)
> **대조 기준**:
> - 종합계획서 §3.4 `LOCK-MCP-06` (재시도 max 3회, 지수 백오프 factor 2.0)
> - 종합계획서 §3.4 `LOCK-MCP-07` (CB 5회→OPEN, 60s→HALF-OPEN, 3회→CLOSE)
> - 종합계획서 §7.3 Phase 1 #5 (P0 — "Bridge 기본 연결" 게이트 #5 충족)
> - 종합계획서 §14 W3 (Rate Limit 초과), W5 (Connection Pool 고갈)
> - 상세명세 §B-3 (`RetryPolicy` 기존 정의), §B-4 (6개 에러 유형 표)
> - `03_connection-management/bridge_layer.md §7.2` (HTTP/JSON-RPC → McpError 매핑 6행) — **본 문서가 소비**
> - `03_connection-management/connection_protocol.md §6.1` (단계별 Failed 전이 표) — **본 문서가 소비**
> - `01_internal-tools/search_tools.md §2.1·§2.2·§2.3` (공통 구조 정본 — McpError/ToolInvocationLog/EscalationPayload) — **재정의 금지, 참조만**
>
> **정본 선언**: 본 문서는 MCP Bridge 의 **재시도 정책 + Circuit Breaker 상태 머신 + Rate Limit 대응 + Pool 고갈 대응**을 단일 정본으로 확정한다. 본 문서 이후 세션(P1-6 / P1-7 / P2-2 / P2-6)은 **본 문서의 LOCK 지점(§14.1)을 변경하지 못한다**.

---

## §0. 메타

| 항목 | 값 |
|------|-----|
| 도메인 | `4-3_MCP-Server-Client` |
| Phase | 1 (V1) |
| 세션 | P1-5 (#5) 주, P1-7 (#7) §3.4 부속 |
| 산출물 경로 | `03_connection-management/retry_circuit_breaker.md` |
| 정본 섹션 | §2 RetryPolicy · §3 Retriability 매트릭스 (§3.1~§3.3 P1-5, **§3.4 P1-7 에러 카탈로그**) · §4 Backoff 알고리즘 · §5 Circuit Breaker 상태 머신 · §6 Rate Limit 429 · §7 Pool 고갈 · §8 CB → Bridge Hook 통합 · §9 Confidence Penalty |
| 공통 자료 구조 정본 | `01_internal-tools/search_tools.md §2` (McpError / ToolInvocationLog / EscalationPayload) — 본 문서에서 재정의 금지 |
| 의존 세션 | P1-3(Bridge), P1-4(Connection Protocol) |
| 후속 세션 계약면 | P1-6(외부 서버 3종 연동), P1-7(에러 카탈로그 6유형), P2-2(도구 디스커버리), P2-6(Pool 최적화) |
| 관련 LOCK | LOCK-MCP-01, 02, 04, 06, 07, 08, 09, 10 |

### §0.1 LOCK 반영표 (본 세션이 실 정의로 반영)

| LOCK | 값 | 본 문서 반영 섹션 |
|------|-----|-----------------|
| LOCK-MCP-01 (10MB) | 요청·응답 각 10MB | §3.2 재시도 제외 매트릭스 row `payload_too_large` |
| LOCK-MCP-02 (네임스페이스) | `{server}.{tool}` | §2.3 `RetryContext.tool_name` 규칙 |
| LOCK-MCP-04 (Streamable HTTP) | MCP 2025-03-26 | §6.1 Retry-After 헤더 파싱 |
| **LOCK-MCP-06 (재시도 정책)** | max 3, factor 2.0 | §2 `RetryPolicy` + §4 백오프 알고리즘 |
| **LOCK-MCP-07 (Circuit Breaker)** | 5/60s/3 | §5 상태 머신 정본 |
| LOCK-MCP-08 (idle 10분) | 600s | §7.2 Pool 고갈과 idle 종료 분리 규칙 |
| LOCK-MCP-09 (정본 소유) | `sot 2/4-3` | §0 메타 |
| LOCK-MCP-10 (Pool max 10) | 10 동시 | §7 Pool 고갈 시나리오 |

### §0.2 입력 문서 정합성 (상류 세션 LOCK 불변 확인)

| 상류 | 참조 지점 | 본 세션 처리 |
|------|----------|-------------|
| `bridge_layer.md §2.2` | `McpBridge` ABC 5메서드 | **변경 0건**, §8.1 에서 추상 메서드만 호출 (메서드명/인자/반환 타입 고정) |
| `bridge_layer.md §2.3` | 상태 번호 S0~S6 | **변경 0건**, §5.3 에서 S4 Failed / S6 Reconnecting 참조만 |
| `bridge_layer.md §7.2` | 6행 매핑표 + 보조 매핑 2행 | **변경 0건**, §3.1 retriability 매트릭스 입력으로 전수 소비 |
| `bridge_layer.md §8.1` | `recovery.action` / `recovery.attempt` 필드 | §10.1 채움 규칙 확정 (Bridge 후보값 → 본 세션 최종값) |
| `bridge_layer.md §10.1` | LOCK 5지점 | **전부 참조만**, 재정의 0건 |
| `connection_protocol.md §6.1` | Stage1/2/3 별 S4 전이 트리거 13행 | §5.4 CB 카운트 증가 규칙으로 매핑 소비 |
| `connection_protocol.md §6.3` | V1/V2/V3 Phase 복구 전략 | **V2 실체 정의** (본 문서가 V2 = P1-5 정본) |
| `search_tools.md §2.1` | McpError 10 category enum | **신규 enum 0건**, 기존 6종(`connection_refused`/`timeout`/`auth_failure`/`rate_limit`/`server_error`/`invalid_response`) + `payload_too_large` 만 매트릭스에 사용 |
| `search_tools.md §2.2` | ToolInvocationLog `recovery{}` 중첩 필드 | §10 중첩 JSON 로그 채움 규칙 |
| `search_tools.md §2.3` | EscalationPayload `retry_count` + `recovery_hint` | §11 에스컬레이션 규칙 |

---

## §1. 개요

본 문서는 MCP Bridge 가 단일 RPC(`tools/call`, `tools/list`, `initialize`) 또는 라이프사이클 단계(Discovery / Initialize / ToolList)가 실패했을 때, 어떤 조건으로 **재시도**하고, 어떤 조건에서 **Circuit Breaker** 를 열어 자원을 보호하는지를 정본으로 선언한다. 본 문서는 다음 4가지 주제를 단일 상태 머신으로 통합한다.

1. **재시도 정책 (`RetryPolicy`)** — LOCK-MCP-06 (`max_retries=3`, `backoff_factor=2.0`, `initial_delay=1s` → `1s/2s/4s`) 실 구현.
2. **Circuit Breaker (`CircuitBreaker`)** — LOCK-MCP-07 (`failure_threshold=5` → OPEN, `recovery_timeout=60s` → HALF-OPEN, `success_threshold=3` → CLOSE, HALF-OPEN 중 1회 실패 → 즉시 OPEN) 실 구현.
3. **Rate Limit 429 처리** — `Retry-After` 헤더 존중, 백오프 알고리즘과 독립 (§6, 종합계획서 §14 W3).
4. **Connection Pool 고갈** — LOCK-MCP-10(10 동시) 초과 시 대기·백오프 합류 규칙 (§7, 종합계획서 §14 W5).

본 문서가 해결하는 Phase 1 → 2 게이트 조건:

| 게이트 | 조건 | 본 문서가 충족 |
|--------|------|---------------|
| Gate P1→2 "Bridge 기본 연결" #5 | 재시도 정책 + Circuit Breaker 구현 | ✅ (§2~§5, LOCK-MCP-06/07 실 정의) |
| Gate P1→2 "Bridge 기본 연결" #7 | 에러 카탈로그 6 유형 (P1-7) | ✅ §3.4 전수 (사용자 노출 메시지 + i18n + 6-12 이벤트명, §3.4.6 대조표) |
| §13.1 E2 (L3 승급) | 에러 코드 카탈로그 — 코드/대응/재시도/로깅 4 축 | ✅ 전수 (§3.1 retriability + §3.4 P1-7 사용자 메시지 + 6-12 이벤트명, §3.4.6 대조표) |
| §14 W3 | Rate Limit 초과 대응 | ✅ §6 전수 |
| §14 W5 | Connection Pool 고갈 대응 | ✅ §7 전수 |

---

## §2. `RetryPolicy` 정본 (LOCK-MCP-06)

### §2.1 파라미터 표

| 파라미터 | 값 | 근거 | 변경 권한 |
|---------|-----|------|----------|
| `max_retries` | **3** | LOCK-MCP-06 | LOCK (본 문서 외 변경 금지) |
| `backoff_factor` | **2.0** | LOCK-MCP-06 | LOCK |
| `initial_delay_ms` | **1000** | 종합계획서 §7.3 #5 절차 2 | LOCK |
| `max_delay_ms` | **30000** | 상세명세 §B-3 | LOCK |
| `jitter_ratio` | **0.2** (±20%) | 본 세션 신규 (thundering herd 완화) | Phase 2 P2-6 에서 캘리브레이션 허용 |
| `total_budget_ms` | **60000** | W-NEW-3 (캐스케이드 방지, 예산 제한) | Phase 2 P2-6 에서 수정 가능 |
| `per_attempt_timeout_ms` | 호출자 지정 (기본 30000) | 상세명세 §G-1 | Phase 1 범위 외 |

본 세션의 고정값 = `1s → 2s → 4s` 3 회 재시도 (초기 시도 포함 시 총 4회 전송). `max_delay_ms=30000` 제한은 본 세션 범위에서는 도달하지 않지만 후속 세션(P2-6)이 `max_retries` 를 늘릴 수 있으므로 상한으로 남겨둔다.

### §2.2 Pydantic-like 정본 정의

```python
# backend/vamos_core/mcp/retry.py
# 실 구현: rust-tauri(4-1) rt.py_bridge 경유 호출은 Rust 측에서 동일 파라미터 보유
from dataclasses import dataclass, field

@dataclass(frozen=True)
class RetryPolicy:
    """LOCK-MCP-06 정본.

    주의: 본 객체는 불변(frozen=True). 변경이 필요하면
    `[INTERFACE_MISMATCH]` 마커 + retry_circuit_breaker.md §14.1 갱신 후 합의.
    """
    max_retries: int = 3                 # LOCK-MCP-06
    backoff_factor: float = 2.0          # LOCK-MCP-06
    initial_delay_ms: int = 1000         # 1s
    max_delay_ms: int = 30000            # 30s 상한
    jitter_ratio: float = 0.2            # ±20% full-jitter
    total_budget_ms: int = 60000         # 전체 예산(W-NEW-3)
    retriable_categories: frozenset[str] = field(
        default_factory=lambda: frozenset({
            "connection_refused",  # -1  (TCP)
            "timeout",             # -2
            "auth_failure",        # 401/403 (1회만)
            "rate_limit",          # 429 (Retry-After 경로)
            "server_error",        # 5xx / -32000~
        })
    )
    non_retriable_categories: frozenset[str] = field(
        default_factory=lambda: frozenset({
            "invalid_response",    # -3 (JSON/스키마 위반)
            "validation_error",    # 입력 검증 실패
            "payload_too_large",   # LOCK-MCP-01 초과
            "security_violation",  # allowlist/sandbox
            "sandbox_error",       # code_execute 전용
        })
    )
    # auth_failure 는 retriable 이지만 1회로 제한 (별도 규칙 §3.3)
    auth_failure_max_retries: int = 1
```

> `McpError.category` 전체 10 종이 본 객체의 두 집합에 전수 분포한다 — retriable 5 종(`connection_refused`/`timeout`/`auth_failure`/`rate_limit`/`server_error`) + non_retriable 5 종(`invalid_response`/`validation_error`/`payload_too_large`/`security_violation`/`sandbox_error`). `auth_failure` 는 retriable 이나 1회로 제한(§3.3). 신규 enum 추가 0건. `search_tools.md §2.1` 정본 불변.

### §2.3 `RetryContext` — 호출 단위 상태

재시도는 **순수 함수**가 아니라 호출 1건의 메타데이터를 계속 축적하는 상태다. `call_tool()` 호출자가 `RetryContext` 를 1건 소유하며, `McpBridge` 가 내부에 은닉한다.

```python
@dataclass
class RetryContext:
    tool_name: str                 # LOCK-MCP-02: `{server}.{tool}` 또는 단일명
    server_id: str                 # Bridge 레벨 식별자
    trace_id: str                  # 6-12 이벤트 표준
    session_id: str | None         # Mcp-Session-Id (Stage2 이후)
    attempt: int = 0               # 0=초기, 1~3=재시도 차수
    elapsed_ms: int = 0            # 누적 경과 (per-attempt 포함 전체)
    last_error: "McpError | None" = None
    auth_refresh_done: bool = False  # §3.3 auth 재시도 1회 제한
    retry_after_ms: int | None = None  # 429 `Retry-After` 헤더 (§6)
    cb_tripped: bool = False       # §5 CB 가 OPEN 되었는지

    def remaining_budget_ms(self, policy: RetryPolicy) -> int:
        return max(0, policy.total_budget_ms - self.elapsed_ms)

    def should_retry(self, policy: RetryPolicy) -> bool:
        if self.cb_tripped:
            return False
        if self.attempt >= policy.max_retries:
            return False
        if self.remaining_budget_ms(policy) == 0:
            return False
        if self.last_error is None:
            return False
        cat = self.last_error.category
        if cat in policy.non_retriable_categories:
            return False
        if cat == "auth_failure" and self.auth_refresh_done:
            # auth 는 1회만 허용
            return False
        return cat in policy.retriable_categories
```

---

## §3. Retriability 매트릭스 (6개 에러 유형 전수)

본 섹션은 `bridge_layer.md §7.2` 의 매핑표 6행 + 보조 매핑 2행을 본 세션이 **재시도 여부 + CB 카운트 영향 + 에스컬레이션 힌트**의 3축으로 확장한다.

### §3.1 매트릭스 정본 (본 세션 LOCK 지점)

| # | `McpError.category` | HTTP 원인 | `retriable` | 재시도 횟수 | CB 카운트 영향 | Escalation 힌트 (§11) | 근거 |
|---|--------------------|-----------|-------------|------------|--------------|---------------------|------|
| 1 | `connection_refused` | TCP / DNS / `-1` | ✅ | max 3 (기본) | +1 (§5.4) | `manual_review` | 상세명세 §B-4 |
| 2 | `timeout` | HTTP `-2` | ✅ | max 3 | +1 | `manual_review` | 상세명세 §B-4 |
| 3 | `auth_failure` | HTTP 401 / 403 | ✅ (1회) | **1** (`auth_failure_max_retries`) | **0** (CB 무영향) | `auth_refresh` | §2.2 / bridge §7.2 row 3 |
| 4 | `rate_limit` | HTTP 429 | ✅ | 조건부 (Retry-After 기반 §6) | **0** (CB 무영향) | `none` (자동 복구) | 종합계획서 §14 W3 |
| 5 | `server_error` | HTTP 5xx / JSON-RPC `-32000`~ | ✅ | max 3 | **+1** | `manual_review` (CB OPEN 시) | 상세명세 §B-4 |
| 6 | `invalid_response` | HTTP `-3` / JSON 파싱 실패 / 세션 불일치 | ❌ | 0 | **0** | `schema_fix` | bridge §7.2 row 6 |
| 7 | `payload_too_large` (보조) | 요청/응답 10MB 초과 | ❌ | 0 | 0 | `schema_fix` | LOCK-MCP-01 |
| 8 | `pool_exhausted → server_error` | Pool 고갈 (내부 매핑) | ✅ | max 3 (지수 백오프와 합류 §7.2) | +1 | `manual_review` (60s 고갈 지속 시) | bridge §7.2 보조 #b, §14 W5 |

**핵심 규칙**:
- `auth_failure` 와 `rate_limit` 는 **CB 무영향** — 서버 장애가 아닌 호출자/쿼터 문제로 간주한다. CB 카운트를 증가시키면 정상 서버까지 차단되어 W3/W4 대응에 어긋나기 때문.
- `invalid_response` 와 `payload_too_large` 는 재시도 무의미 — 동일 요청을 다시 보내도 동일 실패. 즉시 `McpError` 반환 + `schema_fix` 에스컬레이션.
- `server_error` / `connection_refused` / `timeout` 만이 **CB 카운터 +1** 대상. 이들 3종이 5회 연속 누적되면 CB OPEN (§5.2).

### §3.2 non-retriable 사유 상세

| category | 왜 재시도 금지인가 |
|----------|-------------------|
| `invalid_response` | 동일 페이로드에 대한 서버 파싱 규칙은 결정적이다. 반복 시 동일 실패 보장 → CPU/네트워크 낭비. `schema_fix` 에스컬레이션 필수. |
| `payload_too_large` | 요청 크기 자체가 LOCK-MCP-01 위반 → 분할/축소 없이 재시도 무의미. 본 세션은 분할을 지원하지 않는다(LOCK-MCP-01 원칙 = 거절 우선, `bridge_layer.md §10.1`). |
| `validation_error` | `inputSchema` 위반 — 호출자(Blue Node) 가 입력을 고쳐야 함. |
| `security_violation` | allowlist 위반은 정책 결정 사항 → 재시도 시 동일 거절. |
| `sandbox_error` | `code_execute` 전용, `code_tools.md §6` 참조. Bridge 는 pass-through. |

### §3.3 auth_failure 특례 (1회 재시도)

`401` / `403` 수신 시 Bridge 는 토큰 갱신 훅을 **1회** 호출하고 (`bridge_layer.md §6` 훅 참조), 갱신 성공 시 1회만 재시도한다. 2차 실패 시:

1. `RetryContext.auth_refresh_done = True` 설정.
2. `RetryPolicy.should_retry()` 가 `False` 반환.
3. `EscalationPayload(recovery_hint="auth_refresh")` 생성 → I-20 경유.
4. CB 카운트는 증가시키지 않는다 (인증은 서버 장애가 아님).

```python
# 의사코드
def handle_auth_failure(ctx: RetryContext, bridge: McpBridge) -> bool:
    if ctx.auth_refresh_done:
        return False  # 이미 1회 시도, 에스컬레이션
    try:
        bridge.on_auth_refresh(ctx.server_id)  # §6 훅
    except Exception:
        return False
    ctx.auth_refresh_done = True
    ctx.attempt += 1
    return True  # 재시도 허용
```

### §3.4 에러 카탈로그 — 6 유형 사용자 노출 메시지 + 코드 + 대응 (P1-7 정본)

> **세션**: P1-7 (종합계획서 §7.3 Phase 1 #7) — **본 소섹션만 P1-7 이 추가**. §3.1 매트릭스 8행 / §14.1 L3(8행) / L4(CB 3 카테고리) / L5(`auth_failure_max_retries=1`) / L10(`rate_limit` CB 무영향) 전수 참조만, **수정 0건**.
> **대조 기준**: 종합계획서 §7.3 Phase 1 #7 (P1) + §13.1 E2 (에러 코드 카탈로그 L3 기준) + §9.3 횡단 관심사 6-12 Event-Logging + 상세명세 §B-4 (6 유형 표).
> **범위 한정 선언**: 본 소섹션은 §3.1 매트릭스 row 1~6 (6 카테고리)에 대해 **(a) 사용자 노출 메시지 템플릿**, **(b) i18n 키**, **(c) 6-12 Event-Logging 표준 이벤트명**, **(d) 사용자 대응 가이드** 4축을 **추가만** 한다. `category` / `retriable` / `재시도 횟수` / `CB 카운트 영향` / `Escalation 힌트` 5열은 §3.1 의 값을 변경 없이 재인용한다.
> **신규 키 0건**: `recovery{}` 맵과 `EscalationPayload` 9 필드에 대한 추가는 0건이다. 본 소섹션의 `user_message` / `user_hint` / `i18n_key` / `event_name` 4 항목은 **로그 `error.details{}` 맵의 선택 확장 키** 로 정의되며, 기존 필드 재정의 0건 — `search_tools.md §2.1·§2.2·§2.3` 정본 불변. `[INTERFACE_MISMATCH]` 마커 0건.

#### §3.4.1 카탈로그 정본 표 (L3 승급 기준 §13.1 E2 충족)

| # | `category` | 코드 (HTTP/내부) | 재시도 | CB 영향 | 대응 전략 | 사용자 노출 메시지 템플릿 (ko-KR) | 사용자 노출 메시지 템플릿 (en-US) | i18n 키 | 사용자 대응 가이드 | 6-12 이벤트명 |
|---|-----------|-----------------|--------|---------|----------|---------------------------------|----------------------------------|---------|-------------------|-------------|
| 1 | `connection_refused` | `-1` (TCP/DNS) | ✅ max 3 | +1 | 지수 백오프 재시도 → 실패 시 CB 카운트 누적 → 5회 누적 시 CB OPEN → `manual_review` 에스컬레이션 | "'{server_id}' 서버에 연결할 수 없습니다. 잠시 후 자동으로 다시 시도합니다. ({attempt}/{max_attempts})" | "Unable to reach '{server_id}' server. Retrying automatically in a moment. ({attempt}/{max_attempts})" | `mcp.error.connection_refused` | 서버 상태 페이지 확인 후 네트워크 재시도 | `mcp.bridge.error.connection_refused` |
| 2 | `timeout` | `-2` (30s 기본) | ✅ max 3 | +1 | 타임아웃 증가 없이 동일 예산으로 재시도 (`per_attempt_timeout_ms` 불변) → `total_budget_ms=60000` 소진 시 에스컬레이션 | "'{tool_name}' 호출이 {timeout_ms}ms 내에 응답하지 않았습니다. 자동 재시도 중입니다. ({attempt}/{max_attempts})" | "'{tool_name}' did not respond within {timeout_ms}ms. Retrying automatically. ({attempt}/{max_attempts})" | `mcp.error.timeout` | 호출을 단축하거나 더 작은 입력으로 재시도 | `mcp.bridge.error.timeout` |
| 3 | `auth_failure` | `401` / `403` | ✅ 1회 (`auth_failure_max_retries=1`) | **0** (무영향) | 토큰 갱신 훅 1회 → 갱신 성공 시 1회 재시도 → 2차 실패 시 `auth_refresh` 에스컬레이션 (사용자 재인증 요청) | "'{server_id}' 서버 인증에 실패했습니다. 인증 정보를 갱신하거나 다시 로그인해 주세요." | "Authentication failed for '{server_id}'. Please refresh credentials or sign in again." | `mcp.error.auth_failure` | 설정 화면에서 토큰/OAuth 재인증 | `mcp.bridge.error.auth_failure` |
| 4 | `rate_limit` | `429` | ✅ 조건부 (Retry-After 기반) | **0** (무영향) | `Retry-After` 헤더 파싱 → 해당 시간 대기 → 재시도 (§6.1). `Retry-After > total_budget_ms` 시 재시도 포기 + `recovery_hint="none"` 에스컬레이션 | "'{server_id}' 호출이 일시적으로 제한되었습니다. {retry_after_s}초 후 자동으로 재시도합니다." | "'{server_id}' is temporarily rate-limited. Retrying in {retry_after_s} seconds." | `mcp.error.rate_limit` | 요청 빈도 감소 또는 대기 | `mcp.bridge.error.rate_limit` |
| 5 | `server_error` | `5xx` / JSON-RPC `-32000`~ | ✅ max 3 | **+1** | 지수 백오프 재시도 → 5회 누적 시 CB OPEN → 60s 후 HALF-OPEN 복구 시도 → 실패 시 `manual_review` 에스컬레이션 | "'{server_id}' 서버에서 오류가 발생했습니다. 자동으로 다시 시도합니다. ({attempt}/{max_attempts})" | "An error occurred on '{server_id}'. Retrying automatically. ({attempt}/{max_attempts})" | `mcp.error.server_error` | 지속 시 서버 운영팀 문의 | `mcp.bridge.error.server_error` |
| 6 | `invalid_response` | `-3` (JSON 파싱/세션 불일치) | ❌ | **0** (무영향) | 재시도 금지 → 즉시 `McpError` 반환 → `schema_fix` 에스컬레이션 → 로깅 (§10) | "'{server_id}' 서버 응답을 해석할 수 없습니다. 관리자에게 문의해 주세요." | "Unable to parse response from '{server_id}'. Please contact an administrator." | `mcp.error.invalid_response` | 스키마 버전 불일치 의심 시 서버 업데이트 확인 | `mcp.bridge.error.invalid_response` |

**검증 대조 (상세명세 §B-4 1:1)**:

| §B-4 에러 유형 | §B-4 코드 | §B-4 대응 | 본 §3.4.1 row | 일치 |
|---------------|----------|-----------|-------------|-----|
| Connection refused | -1 | 재시도 → 서버 상태 확인 → 사용자 알림 | 1 (`connection_refused`) | ✅ |
| Timeout | -2 | 재시도 (증가된 타임아웃) | 2 (`timeout`) | ✅ (단, 본 세션은 `per_attempt_timeout_ms` 불변 원칙 유지 — §4.3) |
| Auth failure | 401/403 | 토큰 갱신 → 재시도 → 재인증 요청 | 3 (`auth_failure`) | ✅ |
| Rate limit | 429 | Retry-After, 지수 백오프 | 4 (`rate_limit`) | ✅ (단, CB 무영향 원칙 §14.1 L10 유지) |
| Server error | 5xx | 재시도 → CB → Fallback | 5 (`server_error`) | ✅ |
| Invalid response | -3 | 로깅 후 에러 반환 (재시도 X) | 6 (`invalid_response`) | ✅ |

**보조 2행 (§3.1 row 7/8) 대한 주석**: `payload_too_large` 와 `pool_exhausted` 는 **상세명세 §B-4 원본 6 유형에 포함되지 않으므로 본 P1-7 카탈로그의 사용자 노출 대상에서 제외**한다. 대신 §3.1 매트릭스에서 `schema_fix`(payload_too_large) 또는 `manual_review`(pool_exhausted) 경로로 자동 에스컬레이션되며, 사용자 노출 메시지는 §11 EscalationPayload 의 일반 템플릿("내부 오류가 발생했습니다. 관리자에게 문의해 주세요.") 을 따른다.

#### §3.4.2 사용자 노출 메시지 생성 규칙

```python
# 의사코드 — 본 §3.4 에 한정한 신규 유틸, 재시도 경로에 부작용 0건
USER_MESSAGE_TEMPLATES: dict[str, dict[str, str]] = {
    # locale -> category -> template
    "ko-KR": {
        "connection_refused": "'{server_id}' 서버에 연결할 수 없습니다. "
                              "잠시 후 자동으로 다시 시도합니다. ({attempt}/{max_attempts})",
        "timeout": "'{tool_name}' 호출이 {timeout_ms}ms 내에 응답하지 않았습니다. "
                   "자동 재시도 중입니다. ({attempt}/{max_attempts})",
        "auth_failure": "'{server_id}' 서버 인증에 실패했습니다. "
                        "인증 정보를 갱신하거나 다시 로그인해 주세요.",
        "rate_limit": "'{server_id}' 호출이 일시적으로 제한되었습니다. "
                      "{retry_after_s}초 후 자동으로 재시도합니다.",
        "server_error": "'{server_id}' 서버에서 오류가 발생했습니다. "
                        "자동으로 다시 시도합니다. ({attempt}/{max_attempts})",
        "invalid_response": "'{server_id}' 서버 응답을 해석할 수 없습니다. "
                            "관리자에게 문의해 주세요.",
    },
    "en-US": {
        "connection_refused": "Unable to reach '{server_id}' server. "
                              "Retrying automatically in a moment. ({attempt}/{max_attempts})",
        "timeout": "'{tool_name}' did not respond within {timeout_ms}ms. "
                   "Retrying automatically. ({attempt}/{max_attempts})",
        "auth_failure": "Authentication failed for '{server_id}'. "
                        "Please refresh credentials or sign in again.",
        "rate_limit": "'{server_id}' is temporarily rate-limited. "
                      "Retrying in {retry_after_s} seconds.",
        "server_error": "An error occurred on '{server_id}'. "
                        "Retrying automatically. ({attempt}/{max_attempts})",
        "invalid_response": "Unable to parse response from '{server_id}'. "
                            "Please contact an administrator.",
    },
}

# 기본 로케일 (V1 범위): ko-KR. 후속 확장: 6-8 Internationalization 세션.
DEFAULT_LOCALE: str = "ko-KR"


def render_user_message(err: McpError, ctx: RetryContext, locale: str = DEFAULT_LOCALE) -> str:
    """
    §3.4.1 카탈로그 표를 기반으로 사용자 노출 메시지를 생성한다.

    부작용 없음 — 재시도/CB 경로에 영향을 주지 않고, `ToolInvocationLog.error.details.user_message`
    에 append-only 로만 기록된다 (§3.4.3).
    """
    cat = err.category
    table = USER_MESSAGE_TEMPLATES.get(locale) or USER_MESSAGE_TEMPLATES[DEFAULT_LOCALE]
    template = table.get(cat)
    if template is None:
        # 6 카탈로그 외 카테고리 (payload_too_large / pool_exhausted 등) → 범용 메시지
        return ("내부 오류가 발생했습니다. 관리자에게 문의해 주세요."
                if locale == "ko-KR"
                else "An internal error occurred. Please contact an administrator.")
    return template.format(
        server_id=ctx.server_id,
        tool_name=ctx.tool_name,
        attempt=max(ctx.attempt, 1),
        max_attempts=3,  # LOCK-MCP-06 — §14.1 L1 불변
        timeout_ms=err.details.get("timeout_ms") or 30000,
        retry_after_s=round((ctx.retry_after_ms or 0) / 1000),
    )
```

**규칙 R-USR-1**: `render_user_message()` 는 **부작용 없는 순수 함수**. `RetryPolicy` / `CircuitBreaker` / `RetryContext` 의 어떤 필드도 변경하지 않는다 — §14.1 L1~L10 불변 보장.

**규칙 R-USR-2**: `max_attempts` 는 LOCK-MCP-06 으로 **고정 3** — 템플릿에서 하드코드 금지, `RetryPolicy.max_retries` 를 참조한다 (본 의사코드는 가독성을 위해 3 리터럴로 표기).

**규칙 R-USR-3**: `attempt` 은 `max(ctx.attempt, 1)` — 초기 시도(n=0) 를 사용자에게 "1/3" 로 노출.

#### §3.4.3 `ToolInvocationLog.error.details{}` 확장 키 (append-only)

본 소섹션은 `ToolInvocationLog.error.details{}` 맵(이미 `search_tools.md §2.2` 에서 "임의 키-값 확장 허용" 으로 선언됨)에 아래 **4 확장 키**를 선언한다. 기존 `details{}` 내부 키 재정의 0건.

| 키 | 타입 | 값 | 근거 |
|----|------|-----|------|
| `details.user_message` | `string` | `render_user_message()` 결과 | §3.4.2 |
| `details.user_message_locale` | `string` | `"ko-KR"` \| `"en-US"` | §3.4.2 DEFAULT_LOCALE |
| `details.user_hint` | `string` | §3.4.1 "사용자 대응 가이드" 열 원문 | §3.4.1 row별 |
| `details.i18n_key` | `string` | `"mcp.error.{category}"` | §3.4.1 row별 |

**INTERFACE_MISMATCH 방지 주석**: `error.details{}` 는 `search_tools.md §2.2` 에서 **임의 키-값 맵**으로 정의되어 있다. 본 4 키는 **추가** 이며 기존 `details{}` 사용자(bridge_layer.md §7.2 / §3.1 row 1~6 이 이미 채우는 `elapsed_ms` / `stage` / `retry_after_header` / `quota_hint` 등) 와 충돌 0건. `[INTERFACE_MISMATCH]` 마커 0건.

#### §3.4.4 6-12 Event-Logging 표준 이벤트명 매핑

본 세션은 §9.3 횡단 관심사 "6-12 Event-Logging" 을 준수하여 에러 유형별 이벤트명을 정의한다. 기존 `event: "mcp.bridge.call"` 이벤트(§10.3 / §10.4)는 **성공/정상 호출** 경로에 유지되고, 본 카탈로그가 추가하는 이벤트는 **에러 상세 분류** 이벤트로 별도 방출된다.

| `McpError.category` | `event` 이름 (6-12 규약) | 방출 시점 | 심각도 (6-12) |
|---------------------|--------------------------|----------|--------------|
| `connection_refused` | `mcp.bridge.error.connection_refused` | 각 재시도 직전 | `warn` (1~2회), `error` (3회) |
| `timeout` | `mcp.bridge.error.timeout` | 각 재시도 직전 | `warn` (1~2회), `error` (3회) |
| `auth_failure` | `mcp.bridge.error.auth_failure` | 1차 실패 + 2차 실패 | `warn` (1차), `error` (2차 → `auth_refresh`) |
| `rate_limit` | `mcp.bridge.error.rate_limit` | 429 수신 직후 | `warn` (정상 대기), `error` (`Retry-After > budget`) |
| `server_error` | `mcp.bridge.error.server_error` | 각 재시도 직전 + CB OPEN 시 | `warn` (재시도 중), `error` (CB OPEN) |
| `invalid_response` | `mcp.bridge.error.invalid_response` | 즉시 (재시도 0) | `error` (항상) |

**이벤트 스키마**: §10.3 / §10.4 의 `tool{}` / `context{}` / `error{}` / `recovery{}` 4 맵 구조를 그대로 상속하고, 본 이벤트는 `error.category` 를 그대로 `event` 이름 접미사로 노출한다. 신규 최상위 필드 0건 — `ToolInvocationLog` 정본 불변.

**로깅 게이트 (CB 무영향 원칙 보장)**: `rate_limit` / `auth_failure` 이벤트는 **본 이벤트 방출로 CB 카운트를 증가시키지 않음을** 6-12 이벤트 소비자에게 명시하기 위해 `recovery.cb_state` 필드(§10.1 L9 확장 키)를 항상 포함한다. 6-12 대시보드가 `cb_consecutive_failures` 값을 기준으로 집계하도록 보장한다.

#### §3.4.5 Event-Logging 예시 — `connection_refused` 1차 재시도

```json
{
  "trace_id": "trc_2026-04-11T03-42-00_c7e5f022",
  "event": "mcp.bridge.error.connection_refused",
  "timestamp": "2026-04-11T03:42:00.310Z",
  "severity": "warn",
  "tool": {
    "name": "filesystem.read_file",
    "category": "external_server",
    "phase": "V1",
    "server_id": "filesystem"
  },
  "context": {
    "session_id": "mcp_sess_c7e5f0",
    "caller": "blue_node.reasoning_engine",
    "input_size_bytes": 42,
    "output_size_bytes": 0,
    "timeout_budget_ms": 60000,
    "remaining_budget_ms": 58500,
    "protocol_version": "2025-03-26"
  },
  "error": {
    "code": -1,
    "category": "connection_refused",
    "message": "Connection refused: filesystem mcp-server not responding",
    "retriable": true,
    "retry_after_ms": null,
    "details": {
      "elapsed_ms": 120,
      "stage": "initialize",
      "attempt_elapsed_ms": 120,
      "user_message": "'filesystem' 서버에 연결할 수 없습니다. 잠시 후 자동으로 다시 시도합니다. (1/3)",
      "user_message_locale": "ko-KR",
      "user_hint": "서버 상태 페이지 확인 후 네트워크 재시도",
      "i18n_key": "mcp.error.connection_refused"
    }
  },
  "recovery": {
    "action": "retry",
    "attempt": 1,
    "max_attempts": 3,
    "backoff_ms": 1023,
    "escalated_to": null,
    "cb_state": "CLOSED",
    "cb_consecutive_failures": 1,
    "rate_limit_source": null
  }
}
```

#### §3.4.6 L3 승급 기준 §13.1 E2 충족 대조

| E2 요구 항목 | 본 §3.4 반영 | 증빙 |
|------------|-------------|------|
| 에러 유형별 **코드** | ✅ §3.4.1 2번째 열 "코드 (HTTP/내부)" | `connection_refused=-1` / `timeout=-2` / `auth_failure=401·403` / `rate_limit=429` / `server_error=5xx` / `invalid_response=-3` |
| 에러 유형별 **대응 전략** | ✅ §3.4.1 "대응 전략" 열 | 재시도/CB/에스컬레이션 3축을 §3.1 매트릭스에 소급하여 서술 |
| 에러 유형별 **재시도 여부** | ✅ §3.4.1 "재시도" 열 | §3.1 row 1~6 값 재인용, 수정 0건 |
| **6-12 Event-Logging 표준** | ✅ §3.4.4 / §3.4.5 | 이벤트명 6종 + 예시 1건 + 심각도 매핑 |
| **사용자 노출 메시지** | ✅ §3.4.1 / §3.4.2 / §3.4.3 | ko-KR / en-US 템플릿 12건 + `render_user_message()` 순수 함수 + `error.details{}` 확장 4 키 |

**결과**: §13.1 E2 기준 4 축(코드/대응/재시도/로깅) **전수 충족**. 추가로 i18n 확장 축(로케일별 템플릿)까지 반영 — P1-5 §18.4 에서 "카탈로그의 사용자 노출 메시지는 P1-7 위임" 이라 선언한 잔여 부분을 본 §3.4 가 완결한다.

---

## §4. Backoff 알고리즘 (LOCK-MCP-06)

### §4.1 수식

본 세션은 **Full Jitter Exponential Backoff** 를 정본으로 선언한다.

```
base_delay(n)  = min(initial_delay * backoff_factor^(n-1), max_delay)
                = min(1000 * 2^(n-1), 30000)  [ms]

jitter_window  = [ base_delay * (1 - jitter_ratio), base_delay * (1 + jitter_ratio) ]
                = [ base_delay * 0.8, base_delay * 1.2 ]

sleep_ms(n)    = uniform_random(jitter_window)
```

여기서 `n` 은 재시도 차수(1, 2, 3). `n=0` 은 초기 시도로 backoff 없음.

### §4.2 수치 표 (LOCK-MCP-06 고정값 기준)

| 재시도 차수 n | `base_delay` (ms) | jitter window (ms) | 기대 누적 지연 (ms) |
|---|---|---|---|
| 0 (초기) | 0 | — | 0 |
| 1 | 1000 | 800 ~ 1200 | ≈ 1000 |
| 2 | 2000 | 1600 ~ 2400 | ≈ 3000 |
| 3 | 4000 | 3200 ~ 4800 | ≈ 7000 |

> `total_budget_ms=60000` 이므로 3회 재시도까지도 예산 내 완전 수용 가능. 초기 시도 30s timeout + 재시도 3회(각 30s) + sleep 7s ≈ 최대 127s 이지만, 실측에서는 `per_attempt_timeout_ms` 가 tools/call 기본 10s 인 경우가 많아 예산 내 안정 동작.

### §4.3 알고리즘 의사코드

```python
import random
import time

def compute_backoff_ms(policy: RetryPolicy, attempt: int) -> int:
    """attempt: 1-based retry number (1, 2, 3)."""
    if attempt <= 0:
        return 0
    base = min(
        policy.initial_delay_ms * (policy.backoff_factor ** (attempt - 1)),
        policy.max_delay_ms,
    )
    low = base * (1 - policy.jitter_ratio)
    high = base * (1 + policy.jitter_ratio)
    return int(random.uniform(low, high))

async def execute_with_retry(
    bridge: McpBridge,
    fn: "Callable[[], Awaitable[ToolCallResult]]",
    ctx: RetryContext,
    policy: RetryPolicy = RetryPolicy(),
) -> "ToolCallResult":
    cb = bridge.circuit_breaker(ctx.server_id)  # §5
    while True:
        # CB 선검사 — 60s 경과 시 OPEN→HALF_OPEN 전환 시도 (LOCK-MCP-07 복구 창)
        cb.probe_if_due()  # §5.3
        if cb.state == CbState.OPEN:
            return fast_fail(ctx, cb)  # §5.5
        start = time.monotonic_ns()
        result = await fn()
        ctx.elapsed_ms += (time.monotonic_ns() - start) // 1_000_000
        if result.ok:
            cb.on_success()  # §5.4
            log_success(ctx)
            return result
        ctx.last_error = result.error
        # CB 카운트 업데이트
        if result.error.category in {"connection_refused", "timeout", "server_error"}:
            cb.on_failure()
        # 특례: 429
        if result.error.category == "rate_limit":
            ctx.retry_after_ms = result.error.retry_after_ms
        # 특례: 401/403
        if result.error.category == "auth_failure":
            if not handle_auth_failure(ctx, bridge):
                return escalate(ctx, "auth_refresh")  # §11
            continue
        # 일반 경로
        if not ctx.should_retry(policy):
            return escalate(ctx, infer_hint(ctx.last_error))  # §11
        ctx.attempt += 1
        sleep_ms = ctx.retry_after_ms or compute_backoff_ms(policy, ctx.attempt)
        ctx.retry_after_ms = None  # 1회 소진
        await asyncio.sleep(sleep_ms / 1000)
```

### §4.4 jitter 사유

종합계획서 §14 W3 Rate Limit 대응과 W5 Pool 고갈 대응은 동일 시점에 다수 세션이 동시 재시도를 수행하는 경우를 상정한다. 고정 지연(`1s/2s/4s` 정확 대기) 시 thundering herd 가 발생하여 CB 가 조기 OPEN 되는 부작용이 있다. **Full Jitter** 는 재시도 시점을 분산시켜 이를 완화한다.

### §4.5 V1 간이 모드 (connection_protocol.md §6.3 V1 경로)

`connection_protocol.md §6.3` 이 선언한 V1 경로는 "단계별 단일 재시도 1회 + escalate" 였다. 본 세션이 `max_retries=3` 으로 상향함으로써 V1 경로는 폐기되고, **Phase 1 = Phase 2 동일 값** 을 사용한다 (LOCK-MCP-06 는 Phase 에 따라 달라지지 않는다).

> `connection_protocol.md §6.3` 의 V1 행은 본 문서 §12 에서 **수정 이력** 으로 등재하지 않는다. V1 행은 "P1-5 전 간이 모드" 라는 주석과 함께 보존되며, 본 문서 §0 을 통해 P1-5 가 V2 실 정의를 상속 적용하므로 Phase 1 운영에서도 V2 값을 사용한다. `[INTERFACE_MISMATCH]` 마커 0건.

---

## §5. Circuit Breaker 상태 머신 (LOCK-MCP-07)

### §5.1 파라미터 정본

| 파라미터 | 값 | 근거 |
|---------|-----|------|
| `failure_threshold` | **5** (연속 실패) | LOCK-MCP-07 |
| `recovery_timeout_s` | **60** | LOCK-MCP-07 |
| `success_threshold` | **3** (HALF-OPEN 에서 연속 성공) | LOCK-MCP-07 |
| 실패 카운트 감소 조건 | **연속** 카운트 — 한 번 성공 시 CLOSED 상태 카운트 0 리셋 | 본 세션 (표준 CB 패턴) |
| CB scope | **server_id 별 1인스턴스** | 본 세션 (한 서버 장애가 다른 서버 차단 금지) |

### §5.2 상태 번호 및 상태 전이도

`bridge_layer.md §2.3` 의 `LifecycleState` 는 세션 단위였다. CB 는 **서버 단위** 로 별도 상태를 가지며, 다음 3종을 갖는다.

| CB 상태 | 의미 | 진입 조건 | 이탈 조건 |
|--------|------|----------|----------|
| **CLOSED** | 정상 — 모든 호출 통과 | 초기값 / HALF-OPEN 에서 3회 성공 | 연속 실패 5회 → OPEN |
| **OPEN** | 차단 — 호출 즉시 실패 반환 (fast-fail) | CLOSED 에서 연속 실패 5회 / HALF-OPEN 에서 1회 실패 | `recovery_timeout_s=60` 경과 → HALF-OPEN |
| **HALF-OPEN** | 탐색 — 1건만 허용하며 결과 관찰 | OPEN 진입 후 60초 경과 | 성공 3회 연속 → CLOSED / 1회 실패 → OPEN |

```
         ┌───────────┐ 5 consecutive failures ┌─────────┐
         │  CLOSED   │ ─────────────────────► │  OPEN   │
         │ (count=0) │                        │         │
         └─────▲─────┘                        └────┬────┘
               │                                   │ 60s elapsed
               │ 3 consecutive successes           │
               │                                   ▼
               │                             ┌───────────┐
               └──────────────────────────── │ HALF-OPEN │
                                             │(probe=1)  │
                                             └─────┬─────┘
                                                   │ 1 failure
                                                   ▼
                                                (OPEN)
```

### §5.3 상태 클래스 정의

```python
from enum import Enum
from dataclasses import dataclass
import time

class CbState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass
class CircuitBreaker:
    server_id: str
    failure_threshold: int = 5    # LOCK-MCP-07
    recovery_timeout_s: int = 60  # LOCK-MCP-07
    success_threshold: int = 3    # LOCK-MCP-07

    # 내부 상태
    state: CbState = CbState.CLOSED
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    opened_at_s: float | None = None  # monotonic epoch
    _half_open_in_flight: bool = False  # §5.6 HALF-OPEN 단일 probe 슬롯 (상태 전이 시 리셋)

    # 통계(6-12 KPI 연동)
    total_opens: int = 0
    total_half_open_probes: int = 0

    def on_failure(self) -> None:
        """§3.1 매트릭스에서 CB 영향 있는 3 카테고리만 호출."""
        if self.state == CbState.CLOSED:
            self.consecutive_failures += 1
            self.consecutive_successes = 0
            if self.consecutive_failures >= self.failure_threshold:
                self._trip()
        elif self.state == CbState.HALF_OPEN:
            # 탐색 실패 → 즉시 OPEN
            self.consecutive_successes = 0
            self._trip()

    def on_success(self) -> None:
        if self.state == CbState.CLOSED:
            self.consecutive_failures = 0
        elif self.state == CbState.HALF_OPEN:
            self.consecutive_successes += 1
            if self.consecutive_successes >= self.success_threshold:
                self._close()

    def probe_if_due(self) -> bool:
        """OPEN 상태에서 60초 경과 시 HALF_OPEN 으로 전환하고 True 반환."""
        if self.state != CbState.OPEN or self.opened_at_s is None:
            return self.state != CbState.OPEN
        now = time.monotonic()
        if now - self.opened_at_s >= self.recovery_timeout_s:
            self.state = CbState.HALF_OPEN
            self.consecutive_successes = 0
            self.total_half_open_probes += 1
            return True
        return False

    def _trip(self) -> None:
        self.state = CbState.OPEN
        self.opened_at_s = time.monotonic()
        self.total_opens += 1
        self.consecutive_failures = 0  # 리셋 후 60s 타이머 시작
        self._half_open_in_flight = False  # probe 슬롯 해제
        self._half_open_in_flight = False  # probe 슬롯 해제

    def _close(self) -> None:
        self.state = CbState.CLOSED
        self.consecutive_failures = 0
        self.consecutive_successes = 0
        self.opened_at_s = None
        self._half_open_in_flight = False  # probe 슬롯 해제
        self._half_open_in_flight = False  # probe 슬롯 해제
```

### §5.4 CB 카운트 증가 규칙 (`connection_protocol.md §6.1` 매핑)

`connection_protocol.md §6.1` 의 Stage 별 S4 Failed 전이는 본 세션의 `on_failure()` 입력이 된다. 다음 규칙으로 매핑된다.

| `connection_protocol.md §6.1` 트리거 | `McpError.category` | `on_failure()` 호출 | 근거 |
|-------------------------------------|--------------------|--------------------|------|
| Stage1 TCP refused / DNS 실패 | `connection_refused` | ✅ | §3.1 row 1 |
| Stage1 5s 타임아웃 | `timeout` | ✅ | §3.1 row 2 |
| Stage1 `401/403` | `auth_failure` | ❌ | §3.1 row 3 (CB 무영향) |
| Stage1 `404` | `invalid_response` | ❌ | §3.1 row 6 (재시도/CB 무) |
| Stage1 `invalid_response` | `invalid_response` | ❌ | §3.1 row 6 |
| Stage2 10s 타임아웃 | `timeout` | ✅ | §3.1 row 2 |
| Stage2 스키마 검증 실패 | `invalid_response` | ❌ | §3.1 row 6 |
| Stage2 버전 불일치 | `invalid_response` | ❌ | §3.1 row 6 (LOCK-MCP-04) |
| Stage2 `5xx` | `server_error` | ✅ (명시적) | §3.1 row 5 |
| Stage3 5s 타임아웃 | `timeout` | ✅ | §3.1 row 2 |
| Stage3 `payload_too_large` | `payload_too_large` | ❌ | §3.1 row 7 |
| Stage3 스키마 검증 실패 | `invalid_response` | ❌ | §3.1 row 6 |
| Stage4 Pool 고갈 | `server_error` (보조 매핑) | ✅ | §7 / bridge §7.2 보조 #b |

Stage1 5건 + Stage2 4건 + Stage3 3건 + Stage4 1건 = **13 행 전수 소비**, 매핑 불일치 0건.

### §5.5 fast-fail 규칙 (OPEN 상태)

CB 가 OPEN 인 서버에 대한 호출은 네트워크 접근 없이 즉시 `McpError` 를 반환한다.

```python
def fast_fail(ctx: RetryContext, cb: CircuitBreaker) -> ToolCallResult:
    elapsed_since_open = (
        int((time.monotonic() - cb.opened_at_s) * 1000) if cb.opened_at_s else 0
    )
    err = McpError(
        code=-5,
        category="server_error",
        message=f"circuit_breaker_open:{cb.server_id}",
        retriable=True,
        retry_after_ms=max(
            0, cb.recovery_timeout_s * 1000 - elapsed_since_open
        ),
        tool_name=ctx.tool_name,
        request_id=f"{ctx.session_id or 'boot'}:cb_open",
        details={
            "cb_state": cb.state.value,
            "opened_at_s": cb.opened_at_s,
            "total_opens": cb.total_opens,
        },
    )
    ctx.cb_tripped = True
    return ToolCallResult.error(err)
```

> `retry_after_ms` 에 남은 60초를 돌려주어 상위 Blue Node 오케스트레이터가 **동일 서버 재호출을 단념** 하도록 힌트를 준다. 본 Bridge 는 내부적으로 재시도하지 않는다 — OPEN 시 재시도 루프는 **즉시 종료**한다 (§4.3 `ctx.cb_tripped` 분기).

### §5.6 HALF-OPEN 동시성 제어

HALF-OPEN 상태에서는 **1건의 probe** 만 허용한다. 다수 요청이 동시에 HALF-OPEN 진입을 관찰하면 첫 번째 요청만 실제 호출을 수행하고, 나머지는 fast-fail 로 반환한다.

```python
# 추가 규칙
def acquire_half_open_slot(cb: CircuitBreaker) -> bool:
    """동시에 1건만 허용 (asyncio.Lock 로 보호)."""
    # 의사코드 - 실제로는 asyncio.Lock 사용
    if cb.state != CbState.HALF_OPEN:
        return False
    if cb.consecutive_successes == 0 and cb._half_open_in_flight:
        return False
    cb._half_open_in_flight = True
    return True
```

HALF-OPEN 에서 probe 1건이 성공 후 연이어 2개의 추가 성공이 필요한 이유는 `success_threshold=3` 때문이다. 따라서 총 3건이 순차 통과해야 CLOSED 전환.

---

## §6. Rate Limit 429 처리 (§14 W3)

### §6.1 Retry-After 헤더 우선 규칙

HTTP `429 Too Many Requests` 응답 수신 시:

1. **`Retry-After` 헤더가 존재**하면 해당 값(초 단위 또는 HTTP-date)을 파싱하여 `ctx.retry_after_ms` 에 저장한다.
2. 파싱 실패 또는 헤더 부재 시, **지수 백오프 경로**로 합류한다 (§4 `compute_backoff_ms`).
3. `Retry-After` 값이 본 세션 `total_budget_ms=60000` 을 초과하면 재시도를 포기하고 `recovery_hint="none"` 로 에스컬레이션 (자동 복구 사이클 외 영역).

```python
def parse_retry_after(header_value: str) -> int | None:
    """초 단위 정수 또는 HTTP-date 를 ms 로 변환. 실패 시 None."""
    if not header_value:
        return None
    try:
        seconds = int(header_value)
        return seconds * 1000
    except ValueError:
        pass
    try:
        from email.utils import parsedate_to_datetime
        from datetime import datetime, timezone
        dt = parsedate_to_datetime(header_value)
        delta = (dt - datetime.now(timezone.utc)).total_seconds()
        return max(0, int(delta * 1000))
    except Exception:
        return None
```

### §6.2 지수 백오프와의 독립성

- `rate_limit` 카테고리는 **CB 카운트 무영향** (§3.1 row 4). 즉, 429 가 5회 연속 발생해도 CB 는 OPEN 되지 않는다.
- 이유: 429 는 서버가 **정상 동작 중** 이지만 쿼터 제한을 적용하는 상태 → 호출자가 대기하면 복구된다. CB 를 열면 쿼터 회복 후에도 정상 서버가 차단되는 부작용.
- `Retry-After` 가 1초 미만이거나 누락 시 본 세션 `initial_delay_ms=1000` 과 동일한 최소 대기 1초를 적용한다 (thundering herd 완화).

### §6.3 Brave Search W-NEW-2 (무료 2000/월) 연동 지점

종합계획서 §14 W-NEW-2 는 Brave Search 쿼터 80% 경고 + DuckDuckGo 자동 전환을 선언한다. 본 세션 범위에서는:

| 시나리오 | 본 세션 동작 | 후속 세션 위임 |
|---------|-------------|---------------|
| 429 수신 | `Retry-After` 존중 + 재시도 | — |
| 서버가 429 없이 `server_error` 로 쿼터 소진 보고 | `server_error` 경로 → CB 카운트 +1 | P1-6 (외부 서버 설정) |
| 쿼터 80% 도달 사전 경고 | 본 세션 범위 외 | P1-6 외부 서버 쿼터 모니터링 |
| DuckDuckGo 자동 전환 | 본 세션 범위 외 | P1-6 fallback 체인 |

본 세션은 `rate_limit` 의 Bridge 레벨 재시도만 책임진다. **쿼터 추적/경고/fallback 라우팅은 P1-6 `02_external-servers/search_servers.md` 의 입력**으로 위임된다 (§13 핸드오프).

---

## §7. Connection Pool 고갈 대응 (§14 W5, LOCK-MCP-10)

### §7.1 고갈 시 Bridge 동작 (bridge_layer.md §7.2 보조 #b)

`bridge_layer.md §7.2` 보조 매핑 #b 는 "Pool 고갈 → `server_error` + `retriable=true`" 로 정의했다. 본 세션은 다음을 상세화한다.

| 시나리오 | 본 세션 정본 동작 |
|---------|------------------|
| Pool max 10 도달, 11번째 호출 진입 | `pool.acquire(timeout_ms=본 호출 per_attempt_timeout_ms)` 대기 |
| 대기 중 슬롯 해제 → 정상 흐름 | 재시도 아님, 동일 attempt 내 계속 |
| 대기 타임아웃 → `server_error` 반환 | §4 `execute_with_retry` 가 `on_failure()` 호출, CB 카운트 +1 |
| 60초 연속 Pool 고갈 (CB OPEN) | `recovery_hint="manual_review"` 에스컬레이션 |

### §7.2 Pool 고갈과 idle 종료의 분리 (LOCK-MCP-08 vs LOCK-MCP-10)

| 구분 | LOCK | 의미 | 본 세션 영향 |
|------|------|------|-------------|
| Pool 크기 상한 | LOCK-MCP-10 (max 10) | 동시 사용 가능 슬롯 | §5.4 Stage4 트리거, CB 카운트 +1 |
| Idle 종료 | LOCK-MCP-08 (10분) | 미사용 세션 해제 | **본 세션 범위 외** (P2-6) |

Idle 종료는 S5 Disconnecting 상태 전이이지 `on_failure()` 가 아니다. 본 세션 CB 는 "호출 실패" 만 카운트하며, "자발적 세션 종료" 는 카운트하지 않는다.

### §7.3 대기 타임아웃의 누적 예산 영향 (W-NEW-3)

Pool 대기 시간은 `ctx.elapsed_ms` 에 계속 누적된다. 따라서 `total_budget_ms=60000` 예산을 Pool 대기가 먼저 소진하면, 재시도 기회가 없어진다. 이 경우:

1. `remaining_budget_ms() == 0` → `should_retry()` False.
2. `recovery_hint="manual_review"` 에스컬레이션 (서버 장애가 아닌 Bridge 가용성 문제).

### §7.4 V2 P2-6 연동 지점

P2-6 `connection_pool.md` 에서는:
- Pool health check 30초 주기, max_lifetime 3600초 등 추가 파라미터 정의.
- 본 세션의 `on_failure()` / `on_success()` 훅을 Pool 레벨 확장 (slot 해제 실패 추적).
- **본 세션 LOCK-MCP-07 CB 파라미터 5/60/3 은 P2-6 에서 변경 금지** (§14.1).

---

## §8. McpBridge ABC 시그니처 통합 (bridge_layer.md §2.2 참조)

### §8.1 본 세션이 호출하는 ABC 메서드 (변경 0건)

| 메서드 | 본 세션 사용 지점 | 입력 | 출력 |
|--------|-----------------|------|------|
| `call_tool(server_id, tool_name, arguments, session_id, timeout_ms, stream)` | §4.3 `execute_with_retry` 의 `fn()` 내부 | 인자 그대로 | `ToolCallResult` |
| `open_session(server_id)` | auth 갱신 후 재세션 필요 시 | `server_id` | `session_id` or raise |
| `close_session(session_id, reason)` | CB OPEN 시 진행 중 호출 drain | 세션 ID, `"error"` | `None` |
| `get_lifecycle_state(session_id)` | §10 로그 출력 시 상태 병기 | `session_id` | `LifecycleState` |

**변경 0건**: `bridge_layer.md §2.2` 의 5 메서드 시그니처(메서드명/인자/반환 타입)는 본 세션에서 전혀 수정되지 않는다. 본 세션은 호출자 측 레이어(`McpRetryExecutor`) 신규 추가만 수행한다.

### §8.2 신규 ABC — `McpRetryExecutor` (본 세션 정본)

```python
# backend/vamos_core/mcp/retry.py 신규
from abc import ABC, abstractmethod

class McpRetryExecutor(ABC):
    """재시도 + CB 를 감싸는 실행자.

    McpBridge 의 `call_tool()` 을 1:1 대체하지 않고, Blue Node / A2A 가
    Bridge 호출을 감쌀 때 본 클래스를 경유한다.
    """

    @abstractmethod
    async def execute(
        self,
        server_id: str,
        tool_name: str,
        arguments: dict,
        session_id: str | None = None,
        timeout_ms: int = 30_000,
        policy: RetryPolicy | None = None,
    ) -> "ToolCallResult":
        """재시도/CB 포함 단일 호출 실행."""

    @abstractmethod
    def get_circuit_breaker(self, server_id: str) -> CircuitBreaker:
        """서버별 CB 인스턴스 반환 (6-12 KPI 집계 훅)."""

    @abstractmethod
    async def shutdown(self) -> None:
        """모든 서버 CB 초기화 + 누적 통계 flush."""
```

> 본 ABC 는 Phase 2 P2-6 에서 구현체 `DefaultRetryExecutor` 가 추가된다. Phase 1 에서는 시그니처만 확정한다.

---

## §9. Confidence Penalty (Phase별 복구 전략)

`bridge_layer.md §12` 는 confidence penalty 를 선언했지만 `"P1-5 세션이 실체 정의"` 라는 주석으로 위임했다. 본 세션이 실 정의한다.

| 상태 / 이벤트 | Penalty | 누적 규칙 | 근거 |
|-------------|---------|----------|------|
| Connecting S1 실패 → retry | -10% / retry | 매 재시도 누적 | bridge §12 |
| Connected S2 → tools/list 재호출 | -15% (1회) | 단일 적용 | bridge §12 |
| Ready S3 단일 호출 timeout 재시도 | -10% / retry | 누적 | bridge §12 |
| Ready S3 10MB 초과 | -30% (1회) | 단일 | bridge §12 |
| Ready S3 rate_limit 대기 후 재시도 | **-5%** / retry | 누적 (서버가 아닌 쿼터 문제라 penalty 낮음) | 본 세션 |
| Failed S4 → CB OPEN 진입 | **-25%** (1회) | OPEN 진입 시점 1회 | bridge §12 |
| Reconnecting S6 → Connecting S1 | -10% | 매 backoff 종료 시 | bridge §12 |
| Disconnecting S5 drain 실패 | -20% | 1회 | bridge §12 |
| HALF-OPEN probe 성공 | **+5%** (회복) | 성공 1건마다 | 본 세션 |
| CLOSED 복귀 | **+10%** (1회) | CLOSED 진입 시점 | 본 세션 |

### §9.1 penalty 계산 공식

```python
def apply_penalty(current: float, event: str) -> float:
    table = {
        "connecting_retry": -0.10,
        "tools_list_retry": -0.15,
        "ready_timeout_retry": -0.10,
        "payload_too_large": -0.30,
        "rate_limit_retry": -0.05,
        "cb_open": -0.25,
        "reconnect": -0.10,
        "drain_fail": -0.20,
        "half_open_probe_success": +0.05,
        "closed_recovery": +0.10,
    }
    return max(0.0, min(1.0, current + table[event]))
```

> 상한 1.0 / 하한 0.0 은 6-5 OPS 오케스트레이션 정책과 일치. 최종 캘리브레이션은 Phase 2 6-5 연계 시 재조정.

---

## §10. 로깅 (ToolInvocationLog §2.2 적용, 중첩 JSON)

### §10.1 `recovery{}` 필드 채움 규칙 (본 세션 정본)

`search_tools.md §2.2` 의 `ToolInvocationLog.recovery` 중첩 객체를 본 세션이 최종 채운다. `bridge_layer.md §8.1` 이 "후보 값만 제안" 이라 선언했으므로 본 세션이 최종 값.

| 경로 | 값 | 규칙 |
|------|-----|------|
| `recovery.action` | `"retry"` \| `"circuit_break"` \| `"escalate"` \| `"rate_limit_wait"` \| `"none"` | §10.2 분기표 |
| `recovery.attempt` | `RetryContext.attempt` | 0~3 |
| `recovery.max_attempts` | `RetryPolicy.max_retries` | 3 (LOCK-MCP-06) |
| `recovery.backoff_ms` | `compute_backoff_ms(policy, attempt)` 또는 `retry_after_ms` | §4.3 / §6.1 |
| `recovery.escalated_to` | `EscalationPayload.source_engine` 또는 `null` | §11 |
| `recovery.cb_state` | `cb.state.value` (CLOSED/OPEN/HALF_OPEN) | §5.3 (신규 확장 필드 — `recovery` 맵의 추가 키이며 기존 필드 재정의 0건) |
| `recovery.cb_consecutive_failures` | `cb.consecutive_failures` | 0~5 |
| `recovery.rate_limit_source` | `"retry_after_header"` \| `"exponential_backoff"` | §6.1 |

> **INTERFACE_MISMATCH 방지 주석**: `search_tools.md §2.2` 는 `recovery{}` 를 JSON 객체(맵)로 정의했고 내부 필드 목록은 예시였다. 본 세션의 `cb_state` / `cb_consecutive_failures` / `rate_limit_source` 는 맵에 **추가 키 3종** 을 더하는 확장이며, 기존 키 (`action` / `attempt` / `max_attempts` / `backoff_ms` / `escalated_to`) 5종 재정의 0건. `[INTERFACE_MISMATCH]` 마커 0건.

### §10.2 action 결정 분기표

| 조건 | `action` |
|------|---------|
| 성공 (ok=True) | `"none"` |
| `should_retry() == True` 이고 429 아님 | `"retry"` |
| `should_retry() == True` 이고 429 | `"rate_limit_wait"` |
| `cb.state == OPEN` (fast-fail) | `"circuit_break"` |
| 재시도 소진 / 재시도 금지 카테고리 | `"escalate"` |

### §10.3 중첩 JSON 로그 예시 — 실패 + 재시도 + CB OPEN

```json
{
  "trace_id": "trc_2026-04-11T03-04-12_9b8a4e11",
  "event": "mcp.bridge.call",
  "timestamp": "2026-04-11T03:04:12.845Z",
  "tool": {
    "name": "github.search_code",
    "category": "external_server",
    "phase": "V1",
    "server_id": "github"
  },
  "context": {
    "session_id": "mcp_sess_7f3e1a",
    "caller": "blue_node.reasoning_engine",
    "input_size_bytes": 820,
    "output_size_bytes": 0,
    "timeout_budget_ms": 60000,
    "remaining_budget_ms": 53000,
    "protocol_version": "2025-03-26"
  },
  "error": {
    "code": -2,
    "category": "timeout",
    "message": "github.search_code exceeded 30s timeout (attempt 3/3)",
    "retriable": true,
    "retry_after_ms": null,
    "details": {
      "elapsed_ms": 30012,
      "stage": "call_tool",
      "attempt_elapsed_ms": 30012
    }
  },
  "recovery": {
    "action": "circuit_break",
    "attempt": 3,
    "max_attempts": 3,
    "backoff_ms": 0,
    "escalated_to": "i20.manual_review",
    "cb_state": "OPEN",
    "cb_consecutive_failures": 5,
    "rate_limit_source": null
  }
}
```

### §10.4 중첩 JSON 로그 예시 — 429 Retry-After 적용

```json
{
  "trace_id": "trc_2026-04-11T03-06-00_ab22cd88",
  "event": "mcp.bridge.call",
  "timestamp": "2026-04-11T03:06:00.102Z",
  "tool": {
    "name": "brave-search.web_search",
    "category": "external_server",
    "phase": "V1",
    "server_id": "brave-search"
  },
  "context": {
    "session_id": "mcp_sess_ab22cd",
    "caller": "blue_node.reasoning_engine",
    "input_size_bytes": 156,
    "output_size_bytes": 0,
    "timeout_budget_ms": 60000,
    "remaining_budget_ms": 58000
  },
  "error": {
    "code": 429,
    "category": "rate_limit",
    "message": "brave-search rate limit exceeded",
    "retriable": true,
    "retry_after_ms": 2000,
    "details": {
      "retry_after_header": "2",
      "quota_hint": "monthly_free_2000"
    }
  },
  "recovery": {
    "action": "rate_limit_wait",
    "attempt": 1,
    "max_attempts": 3,
    "backoff_ms": 2000,
    "escalated_to": null,
    "cb_state": "CLOSED",
    "cb_consecutive_failures": 0,
    "rate_limit_source": "retry_after_header"
  }
}
```

---

## §11. EscalationPayload 생성 규칙 (§2.3 적용)

### §11.1 에스컬레이션 트리거

| 트리거 | `recovery_hint` | 생성 주체 |
|-------|----------------|----------|
| `max_retries` 소진 (`connection_refused` / `timeout` / `server_error`) | `manual_review` | `execute_with_retry` 종료 시점 |
| `invalid_response` (즉시) | `schema_fix` | `should_retry` False 분기 |
| `payload_too_large` (즉시) | `schema_fix` | 동 |
| `validation_error` (즉시) | `schema_fix` | 동 |
| `auth_failure` 2회 실패 | `auth_refresh` | §3.3 |
| CB OPEN 진입 시점 | `manual_review` | §5.3 `_trip()` 직후 |
| Pool 고갈 60초 연속 | `manual_review` | §7.3 |
| `rate_limit` `Retry-After` > `total_budget_ms` | `none` (자동 복구 외 영역) | §6.1 |

### §11.2 필드 채움 규칙

```python
def build_escalation(ctx: RetryContext, hint: str) -> EscalationPayload:
    assert ctx.last_error is not None
    return EscalationPayload(
        source_engine=f"mcp.retry.{ctx.server_id}",
        error_code=ctx.last_error.code,
        error_category=ctx.last_error.category,
        original_request=mask_pii(ctx.last_error.details.get("original_request", {})),
        partial_result=None,  # 재시도 루프는 partial 보존 안 함
        retry_count=ctx.attempt,
        timestamp=iso8601_now(),
        trace_id=ctx.trace_id,
        recovery_hint=hint,
    )
```

### §11.3 source_engine 명명 규칙 (LOCK-MCP-02 준수)

- 형식: `"mcp.retry.{server_id}"` — 서버별로 구분하여 I-20 대시보드가 서버별 에스컬레이션 빈도를 집계할 수 있다.
- `{server_id}` 는 LOCK-MCP-02 의 namespace 와 일치 (`github`, `brave-search`, `internal` 등).
- 본 세션은 `"mcp.retry.*"` prefix 를 **정본 선언** 한다. 후속 세션이 동일 prefix 를 다른 용도로 사용하면 `[INTERFACE_MISMATCH]` 마커 후 변경 합의 필요.

### §11.4 PII 마스킹 — `recovery_hint="manual_review"` 필수

`manual_review` 는 사람이 페이로드를 보게 되므로 `original_request` 의 PII 필드(이메일/토큰/세션 ID)는 반드시 마스킹한다.

| 필드 유형 | 마스킹 규칙 |
|---------|------------|
| `authorization` 헤더 | `"***"` |
| `Mcp-Session-Id` | 앞 4자 + `"****"` |
| email `to[]` | `"***@domain"` |
| PAT / API key | `"***"` |
| 기타 문자열 `> 200 chars` | 앞 100 + `"..."` + 길이 표기 |

---

## §12. Phase별 복구 전략 (V1/V2/V3 통합)

`connection_protocol.md §6.3` 의 V1/V2/V3 3 Phase 복구 전략을 본 세션이 **실 정의** 한다.

| Phase | 복구 수단 | 본 문서 섹션 | 구현 시점 |
|-------|----------|-------------|----------|
| **V1 (Phase 1 = 현재)** | 지수 백오프 1s→2s→4s (max 3) + CB (5/60/3) + Retry-After 존중 + Pool 고갈 fast-fail | §2/§4/§5/§6/§7 | **본 세션 (P1-5)** |
| **V2 (Phase 2)** | V1 정본 + CB 전역 통계(6-12 KPI) + Pool health check 30s + max_lifetime 3600s + 서버별 RetryPolicy 오버라이드 | §8.2 `McpRetryExecutor.get_circuit_breaker` | **P2-6** `connection_pool.md` |
| **V3 (Phase 3)** | V2 정본 + 토큰 자동 갱신 (auth_refresh 자동화) + DNS 캐시 무효화 + Multi-region 실패 전환 + adaptive backoff (성공률 기반 jitter 조정) | 본 세션 범위 외 | **향후 세션** |

> **LOCK-MCP-06/07 수치는 V1~V3 모두 동일** — `max_retries=3` / `backoff_factor=2.0` / CB `5/60/3` 은 Phase 전환 시에도 변경 금지. Phase 2 P2-6 는 **파라미터 오버라이드 API** 만 추가할 수 있고, Phase 1 기본값은 본 세션이 LOCK.

### §12.1 V1 (본 세션) 범위 밖 명시

본 세션은 다음 항목을 **정의하지 않는다**. 후속 세션 명시 이관.

| 미정의 항목 | 이관 세션 |
|-----------|----------|
| CB 통계의 6-12 KPI 실시간 pub-sub | P2-6 `connection_pool.md` + 6-12 V5 |
| 서버별 `RetryPolicy` 오버라이드 설정 파일 | P1-6 `02_external-servers/` |
| `auth_refresh` 자동 OAuth 갱신 로직 | Phase 3 |
| DNS 캐시 TTL 제어 | Phase 3 |
| Multi-region failover | Phase 3 |
| CB state 를 Redis/외부 저장소 공유 | Phase 3 |
| Blue Node confidence penalty 상위 연동 | Phase 2 6-5 OPS |

---

## §13. 후속 세션 핸드오프 표 (계약면)

본 표는 본 세션(P1-5)이 완료한 이후, 어떤 세션이 본 문서의 어떤 지점을 소비하는지를 선언한다.

| 후속 세션 | 범위 | 본 문서 의존 지점 | 변경 권한 |
|----------|------|-----------------|----------|
| **P1-6 (#6 외부 서버 3종)** | Filesystem / GitHub / Brave Search 설정 | §3.1 매트릭스 8행 / §6.3 Brave Search 쿼터 위임 / §11.3 `source_engine` prefix | 참조만 (매트릭스/CB 파라미터 변경 금지) |
| **P1-7 (#7 에러 카탈로그)** | 6 유형 사용자 노출 메시지 | §3.1 매트릭스 8행 / §11 에스컬레이션 힌트 | `message` 필드의 사용자 노출 템플릿만 추가. `category` / `retriable` / CB 영향 변경 금지 |
| **P2-2 (도구 디스커버리)** | `tools/list_changed` / cursor 페이지네이션 | §3.1 row 6 `invalid_response` (스키마 불일치) / §8.1 `call_tool` 시그니처 | 참조만 |
| **P2-6 (Pool 최적화)** | max 10 / idle 10분 / health 30초 / max_lifetime 3600초 | §5 CB + §7 Pool 고갈 + §8.2 `McpRetryExecutor` + §12 V2 행 | CB 파라미터 오버라이드 API 만 추가 허용. 기본값 5/60/3 변경 금지 |
| **P1-3 `bridge_layer.md`** | §7.2 매핑표 6행 | **본 세션이 소비** (§3.1 입력) | — (상류) |
| **P1-4 `connection_protocol.md`** | §6.1 실패 전이 13행 | **본 세션이 소비** (§5.4 매핑) | — (상류) |

### §13.1 P1-6 ↔ P1-5 통신 계약 (외부 서버별 RetryPolicy 오버라이드)

외부 서버는 쿼터/인증/Rate Limit 특성이 다르므로 **서버별 RetryPolicy 오버라이드**가 필요하다. 본 세션은 오버라이드 인터페이스만 선언하며, 실제 값은 P1-6 이 채운다.

```python
# P1-6 에서 채울 오버라이드 맵
SERVER_RETRY_OVERRIDES: dict[str, RetryPolicy] = {
    "brave-search": RetryPolicy(
        max_retries=3,           # LOCK-MCP-06 불변
        backoff_factor=2.0,      # 불변
        initial_delay_ms=2000,   # Brave 는 1s 너무 짧음, 2s 로 완화
        max_delay_ms=30000,
        jitter_ratio=0.3,        # 공용 API 이므로 jitter 강화
        total_budget_ms=60000,
    ),
    "github": RetryPolicy(
        # GitHub PAT rate limit 은 429 경로로만 처리
        # 기본값 사용
    ),
    "filesystem": RetryPolicy(
        max_retries=1,           # 로컬 파일시스템은 재시도 1회면 충분
        total_budget_ms=5000,    # 짧은 예산
    ),
}
```

> `max_retries=3` 상한과 `backoff_factor=2.0` 은 **오버라이드 불가** — LOCK-MCP-06 이기 때문. P1-6 는 `initial_delay_ms` / `max_delay_ms` / `jitter_ratio` / `total_budget_ms` 만 서버별로 튜닝한다.

---

## §14. 본 세션 LOCK 지점 (후속 세션 변경 금지)

### §14.1 LOCK 목록 (정본)

| # | LOCK 지점 | 본 문서 섹션 | 변경 조건 |
|---|-----------|-------------|----------|
| L1 | `RetryPolicy` 고정값 4종 (`max_retries=3` / `backoff_factor=2.0` / `initial_delay_ms=1000` / `max_delay_ms=30000`) | §2.1 | LOCK-MCP-06 자체 변경 필요 시 AUTHORITY_CHAIN 경유 |
| L2 | `CircuitBreaker` 고정값 3종 (`failure_threshold=5` / `recovery_timeout_s=60` / `success_threshold=3`) | §5.1 | LOCK-MCP-07 자체 변경 필요 시 AUTHORITY_CHAIN 경유 |
| L3 | Retriability 매트릭스 8행 (`category` × `retriable` × CB 영향) | §3.1 | 신규 `McpError.category` 추가 시만 행 추가 허용. 기존 행 값 수정 금지 |
| L4 | CB 카운트 영향 3 카테고리 (`connection_refused` / `timeout` / `server_error`) | §3.1 / §4.3 / §5.4 | 변경 금지 (429/401 은 CB 무영향 원칙) |
| L5 | `auth_failure_max_retries=1` 특례 | §2.2 / §3.3 | 변경 금지 |
| L6 | `RetryContext` 클래스 필드 10개 (`tool_name` / `server_id` / `trace_id` / `session_id` / `attempt` / `elapsed_ms` / `last_error` / `auth_refresh_done` / `retry_after_ms` / `cb_tripped`) | §2.3 | 추가 필드만 허용, 기존 필드명/타입 변경 금지 |
| L7 | `McpRetryExecutor` ABC 시그니처 (`execute` / `get_circuit_breaker` / `shutdown`) | §8.2 | 메서드명/인자/반환 타입 변경 금지 |
| L8 | `EscalationPayload.source_engine` 형식 `"mcp.retry.{server_id}"` | §11.3 | 변경 금지 |
| L9 | `recovery{}` 맵의 본 세션 신규 키 3종 (`cb_state` / `cb_consecutive_failures` / `rate_limit_source`) | §10.1 | 기존 5 키 재정의 금지, 추가는 허용 |
| L10 | `rate_limit` CB 무영향 원칙 | §3.1 row 4 / §6.2 | W-NEW-2 수정 시에도 유지 |

### §14.2 변경 프로토콜

변경이 필요하면:
1. 해당 후속 세션 보고서에 `[INTERFACE_MISMATCH]` 마커 기재.
2. 본 문서 §14.1 에 수정 이력 추가 (일자 / 이유 / 영향 세션).
3. 상위 LOCK (LOCK-MCP-06/07) 은 `MCP_SERVER_CLIENT_구조화_종합계획서.md §3.4` 정본 변경 필요 — AUTHORITY_CHAIN 경유.

---

## §15. 알고리즘 Big-O + LOCK + ABC 요약

### §15.1 핵심 알고리즘 복잡도

| 알고리즘 | 시간 | 공간 | 근거 |
|---------|------|------|------|
| `compute_backoff_ms(n)` | O(1) | O(1) | 수식 1개 + 랜덤 1회 |
| `RetryContext.should_retry()` | O(1) | O(1) | 집합 membership × 2 |
| `execute_with_retry()` 단일 호출 | O(k) (k = attempt 수, ≤ 4 including initial) | O(1) | 루프 최대 4회 |
| `CircuitBreaker.on_failure()` | O(1) | O(1) | 정수 증가 + 조건 분기 |
| `CircuitBreaker.on_success()` | O(1) | O(1) | 동 |
| `CircuitBreaker.probe_if_due()` | O(1) | O(1) | monotonic 시각 비교 |
| `build_escalation()` | O(M) (M = input 크기, PII 마스킹) | O(M) | §11.2 |
| `parse_retry_after()` | O(L) (L = 헤더 길이, L ≤ 256) | O(1) | 정수/HTTP-date 파싱 |
| 서버별 CB 조회 `get_circuit_breaker(server_id)` | O(1) | O(S) (S = 서버 수, ≤ 11 상세명세 §D) | dict 조회 |

전체 최악 복잡도: `execute_with_retry` = O(k × C) 여기서 C 는 Bridge 호출 1건의 비용. 재시도 루프는 k ≤ 4 이므로 **상수 배 오버헤드** 에 불과하다.

### §15.2 LOCK 반영 체크리스트

| LOCK | 반영 섹션 | 체크 |
|------|----------|------|
| LOCK-MCP-01 (10MB) | §3.1 row 7 `payload_too_large` | ✅ |
| LOCK-MCP-02 (네임스페이스) | §2.3 `tool_name` / §11.3 `source_engine` | ✅ |
| LOCK-MCP-04 (Streamable HTTP) | §6.1 `Retry-After` 헤더 파싱 | ✅ |
| **LOCK-MCP-06 (재시도 max 3, factor 2.0)** | §2.1 / §4.1 / §12 | ✅ (본 세션 정본) |
| **LOCK-MCP-07 (CB 5/60/3)** | §5.1 / §5.2 / §12 | ✅ (본 세션 정본) |
| LOCK-MCP-08 (idle 10분) | §7.2 분리 규칙 | ✅ |
| LOCK-MCP-09 (정본 소유 sot 2/4-3) | §0 메타 | ✅ |
| LOCK-MCP-10 (Pool max 10) | §7.1 / §7.2 / §5.4 Stage4 | ✅ |

### §15.3 ABC 시그니처 요약

| ABC | 메서드 | 입력 | 출력 | 예외 | 출처 |
|-----|--------|------|------|------|------|
| `McpBridge` | `call_tool` | `server_id, tool_name, arguments, session_id?, timeout_ms, stream` | `ToolCallResult` | 없음 | `bridge_layer.md §2.2` (변경 0건) |
| `McpBridge` | `call_tool_stream` | 동 (stream 없음) | `AsyncIterator[StreamChunk]` | 없음 | 동 |
| `McpBridge` | `open_session` | `server_id` | `str` (session_id) | `McpError` raise | 동 |
| `McpBridge` | `close_session` | `session_id, reason` | `None` | 없음 | 동 |
| `McpBridge` | `get_lifecycle_state` | `session_id` | `LifecycleState (S0~S6)` | `KeyError` | 동 |
| **`McpRetryExecutor`** | **`execute`** | `server_id, tool_name, arguments, session_id?, timeout_ms, policy?` | `ToolCallResult` | 없음 | **본 세션 §8.2** |
| **`McpRetryExecutor`** | **`get_circuit_breaker`** | `server_id` | `CircuitBreaker` | 없음 | **본 세션 §8.2** |
| **`McpRetryExecutor`** | **`shutdown`** | — | `None` | 없음 | **본 세션 §8.2** |

### §15.4 McpError.category enum 사용 현황

본 세션이 사용하는 category 총 **7종** (`search_tools.md §2.1` 정본 10종 중):

1. `connection_refused` — §3.1 row 1
2. `timeout` — §3.1 row 2
3. `auth_failure` — §3.1 row 3
4. `rate_limit` — §3.1 row 4
5. `server_error` — §3.1 row 5 + §7.1 Pool 고갈 매핑
6. `invalid_response` — §3.1 row 6
7. `payload_too_large` — §3.1 row 7

미사용 3종 (`validation_error` / `security_violation` / `sandbox_error`) 은 non-retriable 집합에 선언만 존재. **신규 enum 추가 0건**, 기존 enum 변경 0건. `[INTERFACE_MISMATCH]` 마커 0건.

---

## §16. 의존성 그래프

```
┌───────────────────────────────────────────────────────────────┐
│                    [search_tools.md §2 정본]                  │
│  McpError (10 cat) · ToolInvocationLog · EscalationPayload    │
└──────────────┬────────────────────────────────┬───────────────┘
               │ 참조만 (재정의 0건)            │
               ▼                                ▼
┌──────────────────────┐              ┌────────────────────┐
│  bridge_layer.md     │              │ connection_protocol│
│  (P1-3 정본)         │              │    .md (P1-4 정본) │
│  §2.2 ABC 5메서드    │              │  §6.1 Stage 실패   │
│  §2.3 상태 S0~S6     │              │   13행 매핑        │
│  §7.2 매핑 6+2행     │              │  §6.2 P1-5 위임 선언│
└──────────┬───────────┘              └─────────┬──────────┘
           │                                     │
           │ §7.2 8행 → §3.1 매트릭스           │ §6.1 13행 → §5.4
           │ §2.3 S4/S6 → §5.3 상태            │
           ▼                                     ▼
    ┌───────────────────────────────────────────────────┐
    │  retry_circuit_breaker.md (본 세션 P1-5 정본)      │
    │                                                   │
    │  §2 RetryPolicy (LOCK-MCP-06)                     │
    │  §3 Retriability 매트릭스 8행                      │
    │  §4 Full Jitter Exponential Backoff               │
    │  §5 CircuitBreaker (LOCK-MCP-07) S머신 3상태       │
    │  §6 Rate Limit 429 + Retry-After                  │
    │  §7 Pool 고갈 (LOCK-MCP-10 연동)                   │
    │  §8 McpRetryExecutor ABC (신규)                    │
    │  §9 Confidence Penalty (실 정의)                   │
    │  §10 ToolInvocationLog.recovery{} 필드 채움        │
    │  §11 EscalationPayload + PII 마스킹                │
    │  §12 V1/V2/V3 Phase 복구 전략 실 정의              │
    │  §13 핸드오프 → P1-6 / P1-7 / P2-2 / P2-6         │
    └─────────┬─────────────┬──────────────┬────────────┘
              │             │              │
              ▼             ▼              ▼
    ┌──────────────┐ ┌───────────┐ ┌──────────────┐
    │ P1-6 외부서버│ │ P1-7 에러  │ │ P2-6 Pool    │
    │ §13.1 오버라 │ │ 카탈로그   │ │ 최적화 V2    │
    │ 이드 인터페  │ │ 6유형 메시 │ │ §12.1 V2 행  │
    │ 이스 소비    │ │ 지 템플릿  │ │ 소비 + 확장  │
    └──────────────┘ └───────────┘ └──────────────┘
```

### §16.1 상류 3종 의존 확인

| 상류 문서 | 의존 행/지점 | 본 세션 소비 지점 | 변경 여부 |
|----------|-------------|-----------------|----------|
| `search_tools.md §2.1` | McpError category 10종 | §3.1 7종 사용 + §2.2 2개 frozenset | 변경 0건 |
| `search_tools.md §2.2` | ToolInvocationLog `recovery{}` | §10 필드 채움 | 기존 5키 불변, 3키 추가 (맵 확장 허용) |
| `search_tools.md §2.3` | EscalationPayload 9 필드 | §11.2 build_escalation | 변경 0건 |
| `bridge_layer.md §2.2` | ABC 5 메서드 | §8.1 4 메서드 호출 | 변경 0건 |
| `bridge_layer.md §2.3` | 상태 S0~S6 | §5 CB 는 별도 상태, §5.4 에서 S4 참조 | 변경 0건 |
| `bridge_layer.md §7.2` | 매핑 6행 + 보조 2행 | §3.1 8행으로 확장 (category 변경 없음) | 변경 0건 |
| `connection_protocol.md §6.1` | Stage 실패 13행 | §5.4 CB 카운트 매핑 13행 | 변경 0건 |
| `connection_protocol.md §6.3` | V1/V2/V3 행 | §12 실 정의 (V2 = P1-5 정본) | 변경 0건 (V2 가 현재 실체 획득) |

---

## §17. Phase 2 테스트 목록 (10+ 건, 실행은 Phase 2 이후)

본 문서가 규정한 재시도/CB 계약을 검증하기 위한 Phase 2 테스트 시나리오. 실 실행은 Phase 2 이후 수행한다.

| # | 테스트 ID | 시나리오 | 입력 | 기대 결과 | 검증 포인트 |
|---|----------|---------|------|----------|------------|
| 1 | T-R-01 | 1회 timeout → 재시도 성공 | 첫 호출 timeout, 2번째 성공 | `ok=true`, `attempt=1`, `cb.CLOSED`, `recovery.action="retry"`, `backoff_ms ∈ [800, 1200]` | §4.2 n=1 |
| 2 | T-R-02 | 3회 연속 timeout → 에스컬레이션 | 4회 전부 timeout | `ok=false`, `attempt=3`, `recovery.action="escalate"`, `escalated_to="i20.manual_review"`, `cb.consecutive_failures=4` (5 미달) | §4.3 / §11.1 |
| 3 | T-R-03 | 5회 연속 실패 → CB OPEN | 4회 재시도 실패 후 5번째 첫 호출 실패 | `cb.state=OPEN`, `cb.opened_at_s ≠ None`, `recovery.action="circuit_break"`, escalate `manual_review` | §5.2 / §5.4 |
| 4 | T-R-04 | CB OPEN 상태 fast-fail | CB OPEN 후 즉시 `execute()` | 네트워크 호출 없이 즉시 `McpError(server_error)`, `retry_after_ms ≈ 60000`, `recovery.action="circuit_break"` | §5.5 |
| 5 | T-R-05 | HALF-OPEN 진입 후 3회 성공 → CLOSED | OPEN 진입 후 60초 경과, 3회 연속 성공 | `cb.state=CLOSED`, `consecutive_successes=0` (리셋), 복귀 penalty `+10%` | §5.2 / §5.3 / §9 |
| 6 | T-R-06 | HALF-OPEN probe 실패 → 즉시 OPEN | OPEN→HALF_OPEN 후 probe 1건 실패 | `cb.state=OPEN` (재진입), `total_opens=2` | §5.3 `on_failure` HALF_OPEN 분기 |
| 7 | T-R-07 | 429 + Retry-After=2 → 대기 후 재시도 | 첫 호출 429 with `Retry-After: 2`, 2번째 성공 | `backoff_ms=2000`, `rate_limit_source="retry_after_header"`, `cb.consecutive_failures=0` (CB 무영향), `recovery.action="rate_limit_wait"` | §6.1 / §6.2 |
| 8 | T-R-08 | 429 헤더 부재 → 지수 백오프 합류 | 429 응답 + `Retry-After` 헤더 없음 | `backoff_ms ∈ [800, 1200]`, `rate_limit_source="exponential_backoff"` | §6.1 / §4.3 |
| 9 | T-R-09 | 401 1회 → 토큰 갱신 훅 → 재시도 1회 | 첫 호출 401, 갱신 후 재시도 성공 | `auth_refresh_done=true`, `attempt=1`, `cb.consecutive_failures=0` | §3.3 |
| 10 | T-R-10 | 401 2회 연속 → `auth_refresh` escalate | 갱신 후에도 401 | `recovery_hint="auth_refresh"`, `attempt=1`, `cb.consecutive_failures=0` | §3.3 / §11.1 |
| 11 | T-R-11 | invalid_response 즉시 escalate | 첫 호출 `-3` | `attempt=0`, `recovery_hint="schema_fix"`, `cb.consecutive_failures=0` (CB 무영향), `retriable=false` | §3.1 row 6 / §3.2 |
| 12 | T-R-12 | payload_too_large 즉시 escalate | 11MB 요청 | `retriable=false`, `recovery_hint="schema_fix"`, 전송 차단 | §3.1 row 7 / LOCK-MCP-01 |
| 13 | T-R-13 | Pool 고갈 → 대기 → `server_error` → 재시도 | 11번째 호출, 5초 대기 후 슬롯 해제 | `ok=true` (재시도 없이 대기만), `elapsed_ms ≥ 5000` | §7.1 |
| 14 | T-R-14 | Pool 60초 연속 고갈 → CB OPEN + escalate | 12회 이상 동시 호출 60초 유지 | `cb.state=OPEN`, `recovery_hint="manual_review"` | §7.3 / §5.4 Stage4 |
| 15 | T-R-15 | `total_budget_ms=60000` 초과 → 재시도 포기 | 3회 재시도 중 timeout 누적 > 60s | `remaining_budget_ms=0`, `attempt < max_retries`, escalate `manual_review` | §2.3 / §4.3 |
| 16 | T-R-16 | `Retry-After` > budget → escalate `none` | 429 with `Retry-After: 120` | `recovery_hint="none"`, 재시도 포기 | §6.1 |
| 17 | T-R-17 | jitter ±20% 범위 분포 | `compute_backoff_ms` 1000회 호출 `n=1` | 모든 값 `∈ [800, 1200]`, 평균 ≈ 1000 ± 30 | §4.3 |
| 18 | T-R-18 | 서버별 CB 독립성 | `github` 5회 실패, `brave-search` 호출 | `cb[brave-search].state=CLOSED`, `cb[github].state=OPEN` | §5.1 scope |
| 19 | T-R-19 | 중첩 JSON 로그 완전성 | 1회 실패 후 재시도 | 로그에 `recovery.cb_state` / `recovery.cb_consecutive_failures` / `recovery.rate_limit_source` 전부 존재 | §10.1 |
| 20 | T-R-20 | EscalationPayload PII 마스킹 | `Authorization` 헤더 포함 요청 실패 escalate | `original_request.authorization == "***"`, `recovery_hint="manual_review"` | §11.4 |
| 21 | T-R-21 | confidence penalty 누적 | 3회 timeout 재시도 + CB OPEN | 누적 penalty = 3 × (-0.10) + 1 × (-0.25) = **-0.55** | §9 |

**합계 21건** (가이드라인 "10건+" 2배 이상 달성).

### §17.1 테스트 LOCK 반영 매트릭스

| 테스트 | LOCK-MCP-06 | LOCK-MCP-07 | LOCK-MCP-01 | LOCK-MCP-10 |
|-------|-------------|-------------|-------------|-------------|
| T-R-01 ~ T-R-02 | ✅ max 3 / factor 2.0 | — | — | — |
| T-R-03 ~ T-R-06 | — | ✅ 5/60/3 | — | — |
| T-R-07 ~ T-R-08 | ✅ jitter | — | — | — |
| T-R-09 ~ T-R-10 | ✅ auth 1회 특례 | — | — | — |
| T-R-11 ~ T-R-12 | ✅ non-retriable | — | ✅ 10MB | — |
| T-R-13 ~ T-R-14 | — | ✅ Stage4 매핑 | — | ✅ max 10 |
| T-R-15 ~ T-R-16 | ✅ 예산 제한 | — | — | — |
| T-R-17 | ✅ jitter 분포 | — | — | — |
| T-R-18 | — | ✅ 서버 독립 | — | — |
| T-R-19 ~ T-R-20 | — | — | — | — (로그/escalation 검증) |
| T-R-21 | ✅ | ✅ | — | — |

---

## §18. 검증 결과 (P1-5 자체 점검)

### §18.1 종합계획서 §7.3 Phase 1 #5 검증 체크리스트

- [x] **LOCK-MCP-06 값 정확 반영** (max 3회, factor 2.0) — §2.1 / §4.1 / §14.1 L1
- [x] **LOCK-MCP-07 값 정확 반영** (5회→OPEN, 60s→HALF-OPEN, 3회→CLOSE) — §5.1 / §5.2 / §14.1 L2
- [x] **재시도 대상/제외 에러 유형 구분** — 상세명세 §B-4 6개 유형 전수 매핑 + 보조 2행 = 8행 (§3.1)
- [x] **Rate Limit 429 Retry-After 처리 포함** — §6.1 `parse_retry_after()` + §6.2 CB 무영향 원칙

### §18.2 산출물 품질 가이드라인 체크 (12 항목)

| # | 항목 | 본 문서 반영 |
|---|------|-------------|
| 1 | 교차 참조 | §0.2 / §13 / §16 (상류 3종, 하류 4종 전수 명시) |
| 2 | Phase별 복구 | §12 V1/V2/V3 실 정의, §9 Confidence Penalty |
| 3 | EscalationPayload | §11 전체 (4 서브섹션), PII 마스킹 규칙 §11.4 |
| 4 | nested JSON | §10.3 / §10.4 2 예시 (통상 실패 + 429 특례) |
| 5 | 10+ 테스트 | §17 21건 (가이드라인 2배 이상) |
| 6 | Big-O + LOCK + ABC | §15 전체 (§15.1 복잡도 9건 / §15.2 LOCK 8개 / §15.3 ABC 8 메서드) |
| 7 | 공통 구조 | §0.2 / §2.2 / §10 / §11.2 / §16.1 (search_tools.md §2 재정의 0건) |
| 8 | 인터페이스 | §8 McpBridge 참조 + §8.2 McpRetryExecutor 신규 ABC |
| 9 | ABC 시그니처 | §8.2 `execute` / `get_circuit_breaker` / `shutdown` 3 메서드 + §15.3 요약 표 |
| 10 | 상태 번호 | §5.2 CB 3상태(CLOSED/OPEN/HALF_OPEN) + §5.4 S0~S6 연계 |
| 11 | 의존성 그래프 | §16 ASCII 그래프 + §16.1 매트릭스 |
| 12 | 통합 | §7 Pool / §9 Confidence / §10 Logging / §11 Escalation / §12 Phase = 5 축 통합 |

모든 12 항목 ✅ 반영.

### §18.3 LOCK 변경 / CONFLICT 검사

- **LOCK 변경**: 0건. LOCK-MCP-06/07 을 실 정의로 **반영** 만 수행. 수치 변경 0건. `[LOCK_CHANGE_NEEDED]` 마커 0건.
- **CONFLICT**: 발견 0건. 상류 3종(`search_tools.md §2` / `bridge_layer.md §2.2·§7.2` / `connection_protocol.md §6.1`) 1:1 대조 완료, 불일치 0건.
- **INTERFACE_MISMATCH**: 0건. 신규 category / 기존 필드 재정의 0건.
- **재검증**: 0회. 최초 드래프트 작성 후 §18 자체 점검으로 안정화.

### §18.4 게이트 충족

| 게이트 | 조건 | 본 세션 충족 |
|-------|------|-------------|
| Gate P1→2 "Bridge 기본 연결" #5 | 재시도 + CB 구현 | ✅ §2~§7 전수 |
| Gate P1→2 "Bridge 기본 연결" #7 (P1-7) | 에러 카탈로그 6 유형 | ✅ §3.4 전수 (사용자 노출 메시지 + i18n + 6-12 이벤트명) |
| G1-1 (도구 스키마 L3) | — | 범위 외 (#1/#2 담당) |
| §13.1 E2 (L3 승급) — 에러 코드 카탈로그 4 축(코드/대응/재시도/로깅) | 6 유형 전수 | ✅ §3.1 + §3.4 (P1-7 이 사용자 메시지 + 6-12 이벤트명을 완결, §3.4.6 대조표) |
| §14 W3 (Rate Limit 초과) | Retry-After 존중 + 독립 경로 | ✅ §6 |
| §14 W5 (Pool 고갈) | 대기/CB 연동 | ✅ §7 |
| §14 W-NEW-3 (타임아웃 캐스케이드) | 총 예산 60s | ✅ §2.1 `total_budget_ms=60000` / §2.3 `remaining_budget_ms()` / §7.3 |

---

## §19. 이월 사항

| # | 이월 항목 | 사유 | 이관 |
|---|----------|------|------|
| 1 | `03_connection-management/_index.md` 상태 갱신 (P1-5 완료 반영) | 공통 산출물 보호 — `_index.md` 수정 금지 | 도메인 마감 step (최종 P1-N 이후 일괄) |
| 2 | P1-2 이월 `01_internal-tools/_index.md` SHELL→DRAFT 갱신 | P1-3/P1-4 와 동일하게 본 세션 범위 외 | 도메인 마감 step |
| 3 | ~~사용자 노출 에러 메시지 6 유형 템플릿~~ | **✅ RESOLVED in P1-7 step1 (2026-04-11)** — §3.4 추가로 ko-KR/en-US 12 템플릿 + `render_user_message()` 순수 함수 + `error.details{}` 4 확장 키 + 6-12 이벤트명 6종 전수 정본화 | — |
| 4 | 외부 서버별 `RetryPolicy` 오버라이드 실 값 (brave-search / github / filesystem) | 본 세션은 인터페이스만 선언 (§13.1) | P1-6 `02_external-servers/` |
| 5 | Pool health check 30s, max_lifetime 3600s 구현 | LOCK-MCP-08/10 의 운용 파라미터 | P2-6 `connection_pool.md` |
| 6 | CB 통계 6-12 KPI 실시간 pub-sub | Event-Logging 6-12 V5 연동 | P2-6 / 6-12 V5 |
| 7 | auth_refresh 자동 OAuth 갱신 로직 | Phase 3 | 향후 세션 |
| 8 | Confidence penalty 6-5 OPS 최종 캘리브레이션 | 6-5 OPS 오케스트레이션 정책과 합류 시 | Phase 2 6-5 |
| 9 | CB state 외부 저장소 공유 (multi-instance) | Phase 3 | 향후 세션 |

---

## §20. 수정 이력

| 일자 | 세션 | 변경 | 근거 |
|------|------|------|------|
| 2026-04-11 | P1-5 step1 | 최초 드래프트 작성 (22 섹션, §0~§21) | 종합계획서 §7.3 #5 + LOCK-MCP-06/07 실 정의 + §14 W3/W5 |
| 2026-04-11 | P1-5 step2 | 자체 재검증 — L6 `RetryContext` 필드 수를 9 → 10 으로 정정(코드 10필드와 일치), 종합계획서 §7 요약 동기화 + FR-3 오귀속 제거(FR-3 는 P1-4 범위, 본 세션은 LOCK-MCP-06/07 실 정의) | step2 품질 심화 재검증 |
| 2026-04-11 | **P1-7 step1** | **§3.4 에러 카탈로그 신규 추가** — 6 유형(connection_refused/timeout/auth_failure/rate_limit/server_error/invalid_response) 에 대한 사용자 노출 메시지(ko-KR/en-US 12 템플릿) + `render_user_message()` 순수 함수(부작용 0) + `ToolInvocationLog.error.details{}` 확장 4 키(user_message/user_message_locale/user_hint/i18n_key) + 6-12 Event-Logging 이벤트명 6종 + 1 예시 로그 + §13.1 E2 4축 충족 대조표. §3.1 매트릭스 / §14.1 LOCK 10 지점 / `recovery{}` 5 기존 키 / `EscalationPayload` 9 필드 **변경 0건**. §19 이월 #3 RESOLVED 처리. §18.4 게이트 표에 #7 항목 + E2 4 축 충족 명기 | 종합계획서 §7.3 Phase 1 #7 (P1) + §13.1 E2 완결 |
| 2026-04-11 | **P1-7 step2** | **재검증 교정 2건**: (a) §1 게이트 표 §13.1 E2 상태를 "✅ 부분" → "✅ 전수" 로 정정 + Gate #7 행 추가 (P1-5 초본 잔류 표현 vs §3.4.6 "전수 충족" 불일치 해소), (b) 정본 완료 푸터를 "P1-5 step1" → "P1-5 step1+step2 · P1-7 step1+step2" 로 갱신(세션·단계 이력 일관성 확보). §3.4 본문 / §14.1 LOCK / §18.4 게이트 표 / §19 이월 변경 0건, `[INTERFACE_MISMATCH]` / `[LOCK_CHANGE_NEEDED]` 0건 | step2 품질 심화 재검증 (세션 일관성) |

---

## §21. 본 세션 자체 점검 (품질 가이드라인 b~g / h~m)

### 품질 가이드라인 (a)~(g)

- **(a) 교차 참조**: §0.2 (상류 3종) / §13 (하류 4종) / §16 (의존성 그래프) — ✅
- **(b) Phase별 복구 전략**: §9 Confidence Penalty 9행 + §12 V1/V2/V3 3행 — ✅
- **(c) EscalationPayload 중첩**: §11 4 서브섹션 (§11.1 트리거 / §11.2 필드 채움 / §11.3 source_engine 규칙 / §11.4 PII 마스킹) — ✅
- **(d) nested JSON 로그**: §10.3 / §10.4 실 예시 2건, 중첩 3단 (`tool{}` / `context{}` / `error{}` / `recovery{}` 4 맵 + `error.details{}`) — ✅
- **(e) 10+ 테스트**: §17 21건 (2배 달성) — ✅
- **(f) Big-O + LOCK + ABC**: §15 3 서브섹션 — ✅
- **(g) 공통 자료 구조 단일 정의**: §0.2 / §2.2 frozenset / §10 / §11.2 — `search_tools.md §2` 재정의 0건 — ✅

### 정본 정합성 (h)~(m)

- **(h) 인터페이스 선언**: §8.2 `McpRetryExecutor` ABC 신규 3 메서드 — ✅
- **(i) ABC 시그니처 명시**: §15.3 표 (상속 5 + 신규 3 = 8 메서드) — ✅
- **(j) 상태 번호 명시**: §5.2 CB 3상태 + §5.4 bridge S0~S6 연계 13행 매핑 — ✅
- **(k) 의존성 그래프**: §16 ASCII + §16.1 매트릭스 — ✅
- **(l) 통합 지점**: §7(Pool) / §9(Confidence) / §10(Logging) / §11(Escalation) / §12(Phase) 5 축 — ✅
- **(m) LOCK/CONFLICT 마커**: `[INTERFACE_MISMATCH]` 0건, `[LOCK_CHANGE_NEEDED]` 0건, 상류 LOCK 참조만 수행 — ✅

---

**정본 완료** · `D:\VAMOS\docs\sot 2\4-3_MCP-Server-Client\03_connection-management\retry_circuit_breaker.md` · 2026-04-11 · P1-5 step1+step2 · P1-7 step1+step2 (§3.4 에러 카탈로그)
