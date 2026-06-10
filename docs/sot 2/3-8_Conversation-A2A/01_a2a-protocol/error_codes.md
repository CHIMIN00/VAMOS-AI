# A2A 에러 코드 카탈로그

> **Version**: 1.0
> **Status**: L3 (Phase 1 완성)
> **Session**: P1-6
> **Date**: 2026-04-10
> **Domain**: 3-8_Conversation-A2A / 01_a2a-protocol
> **L3 기준 충족**: E4 (에러 핸들링) — 에러 코드 + 복구 전략 매핑 완전 정의

---

## §1. 교차 참조 블록

| 참조 문서 | 참조 섹션 | 관계 |
|-----------|----------|------|
| `CONVERSATION_A2A_구조화_종합계획서.md` | §3.4 LOCK-A2A-09 (Circuit Breaker 3회→OPEN, 60초→HALF-OPEN) | 정본 규칙 |
| `CONVERSATION_A2A_구조화_종합계획서.md` | §6.1 항목 #31 (A2A 에러 코드 카탈로그), #32 (HTTP 에러 복구), #33 (지수 백오프 재시도), #34 (대체 에이전트 선택) | 이슈 대응 |
| `CONVERSATION_A2A_상세명세.md` | §4.4 에러 복구 패턴 | 정본 SoT |
| `01_a2a-protocol/json_rpc_schema.md` (P1-1) | §5 에러 코드 체계 (§5.1 표준 5건 + §5.2 커스텀 5건 + §5.3 HTTP 3건 + §5.4 CB) | 에러 코드 원본 정의 |
| `03_security/mtls_jwt.md` (P1-5) | §7 인증 실패 에러 처리 (§7.1 에러 코드 매핑 9건) | 인증 에러 정합 |
| `01_a2a-protocol/task_lifecycle.md` (P1-2) | §4 상태 전이 매트릭스 — failed 상태 전이 조건 | Task 에러 연동 |
| `01_a2a-protocol/agent_card_spec.md` (P1-3) | §6 mDNS TXT 매핑, capabilities — failover 대체 에이전트 선택 기준 | Discovery 연동 |
| `02_agent-discovery/mdns_discovery.md` (P1-4) | §5 에이전트 발견 프로토콜 — 대체 에이전트 선택 | Failover 연동 |

---

## §2. 에러 분류 체계

### 2.1 에러 범주 (Error Category)

```
┌─────────────────────────────────────────────────────────┐
│                  A2A Error Taxonomy                      │
├──────────────────┬──────────────────┬───────────────────┤
│  JSON-RPC 2.0    │  A2A Custom      │  HTTP Level       │
│  Standard Errors │  Protocol Errors │  Transport Errors │
│  (-32700~-32603) │  (-32001~-32008) │  (4xx, 5xx)       │
├──────────────────┼──────────────────┼───────────────────┤
│  Protocol Layer  │  Application     │  Transport Layer  │
│  (RFC 7049)      │  Layer (A2A)     │  (HTTP/1.1, 2)    │
└──────────────────┴──────────────────┴───────────────────┘
```

### 2.2 에러 성격 분류 (Transient / Permanent)

| 분류 | 정의 | 복구 가능 | 대표 에러 |
|------|------|:---------:|----------|
| **Transient** | 일시적 장애, 재시도 시 복구 가능 | YES | -32001, -32003, -32005, -32006, -32008, -32603, 408, 429, 503 |
| **Permanent** | 구조적 오류, 재시도만으로 복구 불가 | NO | -32700, -32600, -32601, -32602, -32002, -32004, -32007 |
| **Conditional** | 조건 변경 시 복구 가능 (재시도 자체로는 불가) | CONDITIONAL | -32004 (대체 에이전트), -32007 (위임 체인 단축) |

---

## §3. JSON-RPC 2.0 표준 에러 코드 (5건)

> RFC 7049 JSON-RPC 2.0 Specification 기반

| # | 코드 | 메시지 | 설명 | 분류 | recoverable | 복구 전략 |
|---|------|--------|------|------|:-----------:|----------|
| S-1 | `-32700` | Parse error | JSON 파싱 실패 (malformed JSON) | Permanent | NO | 요청 본문 검증 후 재전송 |
| S-2 | `-32600` | Invalid Request | 유효하지 않은 JSON-RPC 요청 구조 | Permanent | NO | 요청 구조 검증 후 재전송 |
| S-3 | `-32601` | Method not found | 미지원 메서드 호출 | Permanent | NO | 에이전트 카드 재조회 후 지원 메서드 확인 |
| S-4 | `-32602` | Invalid params | 잘못된 파라미터 (스키마 불일치) | Permanent | NO | 파라미터 스키마 대조 후 재전송 |
| S-5 | `-32603` | Internal error | 서버 내부 오류 (예외 미처리) | Transient | YES | 지수 백오프 재시도 (최대 3회), 실패 시 대체 에이전트 |

**P1-1 정합 확인**: `json_rpc_schema.md` §5.1 표준 에러 5건과 코드/메시지/설명/recoverable/복구전략 **전수 일치 (MATCH)**.

---

## §4. A2A 커스텀 에러 코드 (8건)

> 상세명세 §4.4 기반 5건(-32001~-32005) + 도메인 특화 확장 3건(-32006~-32008)

### 4.1 에러 코드 카탈로그

| # | 코드 | 메시지 | 설명 | 분류 | recoverable | 복구 전략 | §6.1 대응 |
|---|------|--------|------|------|:-----------:|----------|----------|
| C-1 | `-32001` | Task not found | 요청한 Task ID가 존재하지 않음 | Transient | YES | 세션 재생성 후 재전송 | #31 |
| C-2 | `-32002` | Task cannot be canceled | 이미 completed/failed 상태인 Task 취소 시도 | Permanent | NO | 상태 폴링 후 완료 대기 | #31 |
| C-3 | `-32003` | Push notification not supported | 에이전트가 Push 알림 미지원 | Transient | YES | SSE 스트리밍으로 폴백 (tasks/sendSubscribe) | #31 |
| C-4 | `-32004` | Unsupported operation | 에이전트가 해당 동작 미지원 | Conditional | YES | 에이전트 카드 재조회 후 대체 에이전트 선택 (#34 failover) | #31, #34 |
| C-5 | `-32005` | Content type not supported | 지원하지 않는 Part 타입 (MIME type) | Transient | YES | Part 변환 후 재전송 | #31 |
| C-6 | `-32006` | Context window exceeded | 메시지가 에이전트 컨텍스트 윈도우 한계 초과 (LOCK-A2A-05) | Transient | YES | 메시지 압축/분할 후 재전송 | 확장 |
| C-7 | `-32007` | Delegation depth exceeded | JWT delegation_chain 깊이가 최대값(3) 초과 (LOCK-A2A-07) | Permanent | NO | 위임 체인 단축 필요 (직접 호출로 전환) | 확장 |
| C-8 | `-32008` | Agent overloaded | 대상 에이전트가 과부하 상태 (load_factor > threshold) | Transient | YES | 대체 에이전트 선택 (#34 failover) 또는 지수 백오프 재시도 | 확장, #34 |

### 4.2 커스텀 에러 상세

#### C-1: `-32001` Task not found

```typescript
interface TaskNotFoundError {
  code: -32001;
  message: "Task not found";
  data: {
    task_id: string;               // 요청된 Task ID
    suggestion: "SESSION_RECREATE"; // 복구 제안
    retry_eligible: true;
  };
}
```

- **발생 조건**: `tasks/get`, `tasks/cancel`, `tasks/pushNotification/set`, `tasks/pushNotification/get`, `tasks/resubscribe` 에서 존재하지 않는 task_id 전달
- **P1-1 정합**: json_rpc_schema.md §4.3(tasks/get), §4.4(tasks/cancel), §4.6(pushNotification/get), §4.7(tasks/resubscribe) 에러 정의와 일치
- **P1-2 연동**: task_lifecycle.md 상태 전이 — Task가 GC(Garbage Collected) 이후 참조 시 발생

#### C-2: `-32002` Task cannot be canceled

```typescript
interface TaskNotCancelableError {
  code: -32002;
  message: "Task cannot be canceled";
  data: {
    task_id: string;
    current_state: "completed" | "failed" | "canceled";  // LOCK-A2A-02
    suggestion: "POLL_AND_WAIT";
    retry_eligible: false;
  };
}
```

- **발생 조건**: `tasks/cancel` 에서 이미 terminal 상태(completed/failed/canceled)인 Task 취소 시도
- **P1-1 정합**: json_rpc_schema.md §4.4 에러 정의와 일치
- **P1-2 연동**: task_lifecycle.md §4.2 금지 전이 F1~F10 중 terminal→canceled 전이 금지와 정합

#### C-3: `-32003` Push notification not supported

```typescript
interface PushNotSupportedError {
  code: -32003;
  message: "Push notification not supported";
  data: {
    agent_id: string;
    supported_modes: string[];      // ["streaming"] — SSE 폴백 안내
    suggestion: "FALLBACK_SSE";
    retry_eligible: true;
  };
}
```

- **발생 조건**: `tasks/pushNotification/set` 에서 `capabilities.pushNotifications = false`인 에이전트에 설정 시도
- **P1-1 정합**: json_rpc_schema.md §4.5 에러 정의와 일치
- **P1-3 연동**: agent_card_spec.md capabilities.pushNotifications 플래그 참조

#### C-4: `-32004` Unsupported operation

```typescript
interface UnsupportedOperationError {
  code: -32004;
  message: "Unsupported operation";
  data: {
    operation: string;              // 요청된 동작
    agent_id: string;
    agent_capabilities: string[];   // 지원 가능 동작 목록
    suggestion: "DISCOVER_ALTERNATIVE";
    retry_eligible: true;           // 대체 에이전트로 재시도 가능
  };
}
```

- **발생 조건**: 에이전트 카드에 선언되지 않은 기능 요청, 완료된 Task에 resubscribe 시도
- **P1-1 정합**: json_rpc_schema.md §4.7(resubscribe), §4.8(authenticatedExtendedCard) 에러 정의와 일치
- **§6.1 #34 대응**: 대체 에이전트 선택 — `02_agent-discovery/` 연동

#### C-5: `-32005` Content type not supported

```typescript
interface ContentTypeNotSupportedError {
  code: -32005;
  message: "Content type not supported";
  data: {
    unsupported_type: string;       // e.g., "application/octet-stream"
    supported_types: string[];      // e.g., ["text/plain", "image/png"]
    suggestion: "CONVERT_PART";
    retry_eligible: true;
  };
}
```

- **발생 조건**: `tasks/send`, `tasks/sendSubscribe` 에서 에이전트가 지원하지 않는 MIME type의 Part 전송
- **P1-1 정합**: json_rpc_schema.md §5.2 에러 정의와 일치

#### C-6: `-32006` Context window exceeded (확장)

```typescript
interface ContextWindowExceededError {
  code: -32006;
  message: "Context window exceeded";
  data: {
    max_tokens: number;             // LOCK-A2A-05: 모델별 max_tokens
    requested_tokens: number;       // 요청 메시지 토큰 수
    suggestion: "COMPRESS_OR_SPLIT";
    retry_eligible: true;
  };
}
```

- **발생 조건**: 메시지 총 토큰 수가 에이전트의 컨텍스트 윈도우 한계(LOCK-A2A-05) 초과
- **LOCK-A2A-05 연동**: "모델별 max_tokens 준수, 초과 시 압축" — 초과 시 본 에러 반환
- **복구 전략**: 메시지 압축 또는 분할 후 재전송

#### C-7: `-32007` Delegation depth exceeded (확장)

```typescript
interface DelegationDepthExceededError {
  code: -32007;
  message: "Delegation depth exceeded";
  data: {
    max_depth: 3;                   // LOCK-A2A-07: 최대 깊이 3
    current_depth: number;
    delegation_chain: string[];     // 현재 위임 체인 에이전트 ID 목록
    suggestion: "SHORTEN_CHAIN";
    retry_eligible: false;
  };
}
```

- **발생 조건**: JWT delegation_chain 깊이가 3 초과 (LOCK-A2A-07 위반)
- **P1-5 정합**: mtls_jwt.md §4.4 검증 알고리즘 "depth > 3 거부", §7.1 에러 코드 `DELEGATION_DEPTH_EXCEEDED` → HTTP 403 매핑과 일치
- **관계**: P1-5 §7.1 `DELEGATION_DEPTH_EXCEEDED` (HTTP 403, JSON-RPC -32600) 은 인증 계층 에러, 본 `-32007`은 애플리케이션 계층 에러로 구분

#### C-8: `-32008` Agent overloaded (확장)

```typescript
interface AgentOverloadedError {
  code: -32008;
  message: "Agent overloaded";
  data: {
    agent_id: string;
    current_load_factor: number;    // 0.0 ~ 1.0
    threshold: number;              // 과부하 임계값
    estimated_availability_ms: number; // 예상 가용 시간 (밀리초)
    suggestion: "FAILOVER_OR_RETRY";
    retry_eligible: true;
  };
}
```

- **발생 조건**: 대상 에이전트 load_factor가 임계값 초과 (사전 거부)
- **§6.1 #34 대응**: 대체 에이전트 선택 — `02_agent-discovery/` 레지스트리 연동
- **Circuit Breaker 연동**: 연속 3회 과부하 시 LOCK-A2A-09 CB OPEN 전이

---

## §5. HTTP 레벨 에러 복구 정책

> §6.1 항목 #32 (HTTP 에러 복구) 대응

### 5.1 HTTP 에러 코드 매핑

| # | HTTP 코드 | 상황 | 분류 | recoverable | 복구 전략 | 재시도 정책 | CB 카운트 |
|---|-----------|------|------|:-----------:|----------|-----------|----------|
| H-1 | `408` | Request Timeout | Transient | YES | 지수 백오프 재시도 | 초기 1초, 최대 60초, 최대 3회 | YES (+1) |
| H-2 | `429` | Rate Limited | Transient | YES | `Retry-After` 헤더 값 준수 | 헤더 값 우선, 없으면 30초 | NO |
| H-3 | `503` | Agent Unavailable | Transient | YES | 레지스트리에서 대체 에이전트 선택 | 대체 에이전트 즉시 시도 | YES (+1) |
| H-4 | `401` | Unauthorized | Conditional | YES (갱신 후) | 토큰/인증서 갱신 후 재시도 | 갱신 완료 후 즉시 1회 | YES (+1) |
| H-5 | `403` | Forbidden | Permanent | NO | 권한 확인, 상위 권한 요청 | 재시도 불가 | NO |

**P1-1 정합 확인**: json_rpc_schema.md §5.3 HTTP 에러 3건(408/429/503)과 코드/상황/recoverable/복구전략 **전수 일치 (MATCH)**.

**P1-5 정합 확인**: mtls_jwt.md §7.1 에러 코드 매핑에서 HTTP 401/403 매핑 9건과 본 카탈로그 H-4/H-5 **정합 (MATCH)**.

### 5.2 HTTP → JSON-RPC 에러 매핑

| HTTP 코드 | JSON-RPC 에러 매핑 | 조건 |
|-----------|-------------------|------|
| `408` | 클라이언트에 전파하지 않음 (내부 재시도) | 재시도 소진 시 `-32603 Internal error` 반환 |
| `429` | 클라이언트에 전파하지 않음 (대기 후 재시도) | Retry-After 초과 시 `-32008 Agent overloaded` 반환 |
| `503` | `-32008 Agent overloaded` 또는 failover | failover 성공 시 투명 처리, 실패 시 에러 반환 |
| `401` | `-32600 Invalid Request` (P1-5 §7.1 정합) | 인증 갱신 실패 시 |
| `403` | `-32600 Invalid Request` (P1-5 §7.1 정합) | 권한 부족 |

---

## §6. 지수 백오프 재시도 정책

> §6.1 항목 #33 (지수 백오프 재시도) 대응

### 6.1 재시도 파라미터

```typescript
interface RetryPolicy {
  /** 초기 대기 시간 (밀리초) */
  initial_delay_ms: 1000;           // 1초

  /** 최대 대기 시간 (밀리초) */
  max_delay_ms: 60000;              // 60초

  /** 최대 재시도 횟수 */
  max_retries: 3;

  /** 백오프 승수 */
  backoff_multiplier: 2.0;

  /** 지터 (jitter) 범위 비율 — 동시 재시도 thundering herd 방지 */
  jitter_factor: 0.1;              // +-10%
}
```

### 6.2 재시도 대상 에러

| 에러 코드 | 재시도 가능 | 재시도 정책 | 비고 |
|----------|:-----------:|-----------|------|
| `-32001` | YES | 표준 지수 백오프 | 세션 재생성 포함 |
| `-32003` | YES | 1회만 (SSE 폴백 시도) | 폴백 모드 전환 |
| `-32005` | YES | 1회만 (Part 변환 후) | 변환 후 재전송 |
| `-32006` | YES | 1회만 (압축 후) | 메시지 압축/분할 |
| `-32008` | YES | 표준 지수 백오프 | 또는 failover |
| `-32603` | YES | 표준 지수 백오프 | Internal error |
| `408` | YES | 표준 지수 백오프 | Timeout |
| `429` | YES | Retry-After 우선 | Rate limit |
| `503` | YES | failover 우선 | Agent unavailable |

### 6.3 재시도 알고리즘

```
시간복잡도: O(max_retries) = O(3) — 상수 시간
공간복잡도: O(1) — 재시도 카운터만 유지

LOCK 참조: LOCK-A2A-09 (CB 3회→OPEN)
ABC 매핑: A=요청 에이전트, B=대상 에이전트, C=레지스트리(failover)
```

```typescript
async function retryWithExponentialBackoff(
  request: A2ARequest,
  policy: RetryPolicy,
  circuitBreaker: CircuitBreakerState
): Promise<A2AResponse> {
  let lastError: A2AError | null = null;

  for (let attempt = 0; attempt <= policy.max_retries; attempt++) {
    // Circuit Breaker 확인 (LOCK-A2A-09)
    if (circuitBreaker.state === "OPEN") {
      if (Date.now() - circuitBreaker.opened_at_ms < 60000) {
        // 60초 미경과 → 즉시 failover
        return attemptFailover(request);
      }
      circuitBreaker.state = "HALF_OPEN"; // 60초 경과 → HALF-OPEN
    }

    try {
      let response = await sendA2ARequest(request);
      if (circuitBreaker.state === "HALF_OPEN") {
        circuitBreaker.state = "CLOSED";  // 성공 시 CLOSED 복귀
        circuitBreaker.failure_count = 0;
      }
      return response;
    } catch (error) {
      lastError = error;

      // Permanent 에러는 즉시 반환 (재시도 불가)
      if (!isRetryEligible(error.code)) {
        return { error: lastError };
      }

      // CB failure 카운트 증가 (§8.3 CB 적용 분류 — -32008/-32603/408/503/401 만 YES)
      if (isCBEligible(error.code)) {
        circuitBreaker.failure_count++;
      }
      if (circuitBreaker.failure_count >= 3) {
        circuitBreaker.state = "OPEN";       // LOCK-A2A-09: 3회 → OPEN
        circuitBreaker.opened_at_ms = Date.now();
        log("WARN", "circuit_breaker_opened", { agent: request.target_agent });
        return attemptFailover(request);     // failover 시도
      }

      // 지수 백오프 대기
      if (attempt < policy.max_retries) {
        let delay = Math.min(
          policy.initial_delay_ms * Math.pow(policy.backoff_multiplier, attempt),
          policy.max_delay_ms
        );
        let jitter = delay * policy.jitter_factor * (Math.random() * 2 - 1);
        await sleep(delay + jitter);
      }
    }
  }

  // 재시도 소진 → failover 시도
  return attemptFailover(request);
}
```

### 6.4 재시도 시퀀스 예시

```
Request → 408 Timeout
  ├─ Attempt 1: wait 1초 (±0.1초 jitter) → retry → 408 Timeout
  ├─ Attempt 2: wait 2초 (±0.2초 jitter) → retry → 408 Timeout
  ├─ Attempt 3: wait 4초 (±0.4초 jitter) → retry → 408 Timeout
  └─ 재시도 소진 → CB failure_count=3 → OPEN
       └─ Failover → 대체 에이전트 선택 (02_agent-discovery/ 연동)
```

---

## §7. 대체 에이전트 선택 (Failover)

> §6.1 항목 #34 (대체 에이전트 선택) 대응

### 7.1 Failover 트리거 조건

| # | 트리거 | 에러 코드 | 선행 조건 |
|---|--------|----------|----------|
| F-1 | 재시도 소진 (3회) | -32603, -32008, 408, 503 | 지수 백오프 3회 실패 |
| F-2 | Circuit Breaker OPEN | (CB 상태) | 연속 3회 실패 (LOCK-A2A-09) |
| F-3 | 기능 미지원 | -32004 | 에이전트 카드 확인 후 대체 필요 |
| F-4 | 에이전트 과부하 | -32008 | load_factor > threshold |

### 7.2 Failover 알고리즘

```
시간복잡도: O(k) where k = 후보 에이전트 수 (레지스트리 쿼리)
공간복잡도: O(k) — 후보 목록 유지
LOCK 참조: LOCK-A2A-04 (mDNS Service Type), LOCK-A2A-09 (CB)
ABC 매핑: A=요청자, B=실패 에이전트, C=대체 에이전트
```

```typescript
async function attemptFailover(
  request: A2ARequest
): Promise<A2AResponse> {
  // 1. 레지스트리에서 대체 에이전트 검색 (02_agent-discovery/ 연동)
  let candidates = await discoverAgents({
    service_type: "_vamos-a2a._tcp.local.",  // LOCK-A2A-04
    required_skills: request.required_skills,
    exclude: [request.target_agent]           // 실패 에이전트 제외
  });

  if (candidates.length === 0) {
    // 대체 에이전트 없음 → 에스컬레이션
    return escalateToI20({
      source_engine: "a2a-gateway",
      error_code: request.last_error.code,
      original_request: request,
      partial_result: null,
      retry_count: request.retry_count,
      escalation_reason: "NO_ALTERNATIVE_AGENT",
      timestamp: new Date().toISOString()
    });
  }

  // 2. 최적 대체 에이전트 선택 (P1-3 AgentCard.capabilities 기반)
  let bestCandidate = candidates
    .filter(a => a.circuit_breaker_state !== "OPEN")
    .sort((a, b) => a.load_factor - b.load_factor)[0];

  // 3. 대체 에이전트로 요청 전달
  return sendA2ARequest({
    ...request,
    target_agent: bestCandidate.agent_id,
    metadata: {
      ...request.metadata,
      failover_from: request.target_agent,
      failover_reason: request.last_error.code
    }
  });
}
```

### 7.3 Failover 제약

| 제약 | 값 | 근거 |
|------|---|------|
| 최대 failover 시도 횟수 | 2회 | 무한 체이닝 방지 |
| failover 대상 CB 상태 | CLOSED 또는 HALF-OPEN만 | LOCK-A2A-09 준수 |
| delegation_chain 깊이 확인 | failover 시 깊이 +1 계산 | LOCK-A2A-07 (최대 3) 준수 |

---

## §8. Circuit Breaker 연동

> LOCK-A2A-09: Circuit Breaker 연속 실패 임계 — 3회 → OPEN, 60초 후 HALF-OPEN

### 8.1 Circuit Breaker 상태 전이

```
CLOSED ──(연속 3회 실패)──> OPEN ──(60초 경과)──> HALF-OPEN
  ^                                                    │
  └────────────────(1회 성공)───────────────────────────┘
                        │
          HALF-OPEN ──(실패)──> OPEN
```

### 8.2 CB 상태 인터페이스

```typescript
interface CircuitBreakerState {
  /** 현재 상태 */
  state: "CLOSED" | "OPEN" | "HALF_OPEN";

  /** 연속 실패 카운트 */
  failure_count: number;

  /** 임계값 (LOCK-A2A-09) */
  failure_threshold: 3;

  /** OPEN 전이 시각 (ISO 8601) */
  opened_at?: string;

  /** 복구 타임아웃 (LOCK-A2A-09: 60초) */
  recovery_timeout_ms: 60000;

  /** 마지막 실패 에러 코드 */
  last_error_code?: string;
}
```

### 8.3 CB 적용/미적용 에러 분류

| 에러 코드 | CB 카운트 적용 | 사유 |
|----------|:-------------:|------|
| `-32001` Task not found | NO | 클라이언트 측 오류 (Task ID 오류) |
| `-32002` Task not cancelable | NO | 상태 로직 오류 |
| `-32003` Push not supported | NO | 기능 부재 (서버 장애 아님) |
| `-32004` Unsupported operation | NO | 기능 부재 |
| `-32005` Content type not supported | NO | 입력 오류 |
| `-32006` Context exceeded | NO | 입력 크기 오류 |
| `-32007` Delegation depth exceeded | NO | 인가 제약 |
| `-32008` Agent overloaded | **YES** | 서버 과부하 (transient 장애) |
| `-32603` Internal error | **YES** | 서버 내부 오류 |
| `-32700` Parse error | NO | 클라이언트 입력 오류 |
| `-32600` Invalid Request | NO | 클라이언트 요청 오류 |
| `-32601` Method not found | NO | 클라이언트 요청 오류 |
| `-32602` Invalid params | NO | 클라이언트 입력 오류 |
| `408` Timeout | **YES** | 네트워크/서버 장애 |
| `429` Rate Limited | NO | 정책적 제한 (장애 아님) |
| `503` Unavailable | **YES** | 서버 불가용 |
| `401` Unauthorized | **YES** | 인증 실패 (P1-5 §6 CB 통합) |

**P1-5 정합 확인**: mtls_jwt.md §6 CB 통합에서 인증 실패(401) 시 CB failure_count 증가 정의와 **일치 (MATCH)**.

---

## §9. 에스컬레이션 페이로드 구조 (I-20)

### 9.1 EscalationPayload 인터페이스

```typescript
interface EscalationPayload {
  /** 발생 엔진/모듈 ID */
  source_engine: string;                      // e.g., "a2a-gateway"

  /** A2A 에러 코드 또는 HTTP 코드 */
  error_code: number;

  /** 원본 JSON-RPC 요청 */
  original_request: A2ARequest;

  /** 부분 결과 (있으면) */
  partial_result: object | null;

  /** 재시도 횟수 */
  retry_count: number;

  /** 에스컬레이션 사유 */
  escalation_reason: EscalationReason;

  /** 에스컬레이션 발생 시각 (ISO 8601) */
  timestamp: string;

  /** 추적 ID */
  trace_id: string;

  /** 관련 에이전트 정보 */
  agent_context: {
    source_agent: string;
    target_agent: string;
    failover_agents_tried: string[];
  };

  /** Circuit Breaker 상태 스냅샷 */
  circuit_breaker_snapshot: CircuitBreakerState;

  /** 심각도 */
  severity: "WARNING" | "ERROR" | "CRITICAL";
}

type EscalationReason =
  | "RETRY_EXHAUSTED"            // 재시도 소진
  | "NO_ALTERNATIVE_AGENT"       // 대체 에이전트 없음
  | "CIRCUIT_BREAKER_OPEN"       // CB OPEN (연속 실패)
  | "DELEGATION_CHAIN_BLOCKED"   // 위임 체인 제약
  | "SECURITY_VIOLATION"         // 보안 침해 의심
  | "CERT_RENEWAL_FAILED";       // 인증서 갱신 실패 (P1-5 연동)
```

**P1-1 정합 확인**: json_rpc_schema.md §6 EscalationPayload 구조(source_engine, error_code, original_request, partial_result, retry_count)와 **필수 필드 일치 (MATCH)**.

### 9.2 에스컬레이션 트리거 조건

| # | 조건 | severity | escalation_reason |
|---|------|----------|-------------------|
| E-1 | 재시도 3회 소진 + failover 실패 | ERROR | `RETRY_EXHAUSTED` |
| E-2 | 대체 에이전트 0건 | ERROR | `NO_ALTERNATIVE_AGENT` |
| E-3 | CB OPEN 전이 | WARNING | `CIRCUIT_BREAKER_OPEN` |
| E-4 | delegation_chain 깊이 제약으로 failover 불가 | ERROR | `DELEGATION_CHAIN_BLOCKED` |
| E-5 | 반복적 인증 실패 (5회/분) | CRITICAL | `SECURITY_VIOLATION` |
| E-6 | 인증서 자동 갱신 3회 실패 | ERROR | `CERT_RENEWAL_FAILED` |

---

## §10. 로깅 포맷 (R-01-7)

### 10.1 에러 이벤트 로깅 구조

```json
{
  "trace_id": "trc_a2a_20260410_err001",
  "timestamp": "2026-04-10T12:00:00.000Z",
  "level": "ERROR",
  "service": "a2a-gateway",
  "error": {
    "code": -32001,
    "message": "Task not found",
    "category": "a2a_custom",
    "classification": "transient",
    "stack": null
  },
  "context": {
    "method": "tasks/get",
    "request_id": "req_xyz789",
    "task_id": "task_missing_001",
    "session_id": "sess_abc",
    "source_agent": "agent:orchestrator-001",
    "target_agent": "agent:code-reviewer-001",
    "auth_scheme": "Bearer",
    "delegation_depth": 1
  },
  "recovery": {
    "action": "SESSION_RECREATE",
    "retry_count": 1,
    "fallback_agent": null,
    "circuit_breaker_state": "CLOSED",
    "degraded_mode": false
  }
}
```

### 10.2 재시도 이벤트 로깅 구조

```json
{
  "trace_id": "trc_a2a_20260410_retry001",
  "timestamp": "2026-04-10T12:01:00.000Z",
  "level": "WARN",
  "service": "a2a-gateway",
  "error": {
    "code": 408,
    "message": "Request Timeout",
    "category": "http_transport",
    "classification": "transient",
    "stack": null
  },
  "context": {
    "method": "tasks/send",
    "request_id": "req_retry_001",
    "task_id": "task_002",
    "session_id": "sess_def",
    "source_agent": "agent:orchestrator-001",
    "target_agent": "agent:translator-001",
    "auth_scheme": "mTLS+Bearer",
    "delegation_depth": 0
  },
  "recovery": {
    "action": "EXPONENTIAL_BACKOFF",
    "retry_count": 2,
    "next_delay_ms": 4000,
    "fallback_agent": null,
    "circuit_breaker_state": "CLOSED",
    "degraded_mode": false
  }
}
```

### 10.3 Circuit Breaker 전이 이벤트 로깅 구조

```json
{
  "trace_id": "trc_a2a_20260410_cb001",
  "timestamp": "2026-04-10T12:02:00.000Z",
  "level": "WARN",
  "service": "a2a-gateway",
  "error": {
    "code": null,
    "message": "Circuit breaker state transition",
    "category": "circuit_breaker",
    "classification": "state_transition",
    "stack": null
  },
  "context": {
    "method": null,
    "request_id": null,
    "task_id": null,
    "session_id": null,
    "source_agent": "agent:orchestrator-001",
    "target_agent": "agent:translator-001",
    "auth_scheme": null,
    "delegation_depth": null
  },
  "recovery": {
    "action": "CB_STATE_TRANSITION",
    "previous_state": "CLOSED",
    "new_state": "OPEN",
    "failure_count": 3,
    "recovery_timeout_ms": 60000,
    "fallback_agent": "agent:translator-002",
    "circuit_breaker_state": "OPEN",
    "degraded_mode": true
  }
}
```

### 10.4 Failover 이벤트 로깅 구조

```json
{
  "trace_id": "trc_a2a_20260410_fo001",
  "timestamp": "2026-04-10T12:02:01.000Z",
  "level": "INFO",
  "service": "a2a-gateway",
  "error": {
    "code": -32008,
    "message": "Agent overloaded",
    "category": "a2a_custom",
    "classification": "transient",
    "stack": null
  },
  "context": {
    "method": "tasks/send",
    "request_id": "req_fo_001",
    "task_id": "task_003",
    "session_id": "sess_ghi",
    "source_agent": "agent:orchestrator-001",
    "target_agent": "agent:translator-002",
    "auth_scheme": "mTLS+Bearer",
    "delegation_depth": 0
  },
  "recovery": {
    "action": "FAILOVER",
    "retry_count": 3,
    "original_target": "agent:translator-001",
    "fallback_agent": "agent:translator-002",
    "circuit_breaker_state": "OPEN",
    "degraded_mode": false
  }
}
```

---

## §11. 예외 처리 정책 표

| # | 예외 상황 | 감지 방법 | 에러 코드 | 처리 정책 | 에스컬레이션 조건 | confidence penalty |
|---|----------|----------|----------|----------|-----------------|-------------------|
| 1 | Task ID 미존재 | tasks/get 응답 -32001 | -32001 | 세션 재생성 후 재전송 (1회) | 재생성 실패 시 | -0.1 |
| 2 | Terminal Task 취소 시도 | tasks/cancel 응답 -32002 | -32002 | 즉시 실패 반환, 상태 폴링 안내 | 반복 시 (3회/분) | -0.05 |
| 3 | Push 미지원 에이전트 | pushNotification/set 응답 -32003 | -32003 | SSE 폴백 (sendSubscribe) | 폴백 실패 시 | -0.1 |
| 4 | 기능 미지원 | 에이전트 카드 확인 후 -32004 | -32004 | 대체 에이전트 선택 (failover) | 대체 에이전트 없음 | -0.2 |
| 5 | MIME type 미지원 | tasks/send 응답 -32005 | -32005 | Part 변환 후 재전송 | 변환 불가 시 | -0.1 |
| 6 | 컨텍스트 초과 | 토큰 계산 후 -32006 | -32006 | 메시지 압축/분할 | 압축 후에도 초과 시 | -0.2 |
| 7 | 위임 깊이 초과 | JWT 검증 시 -32007 | -32007 | 즉시 거부, 체인 단축 안내 | 즉시 (남용 의심) | -0.5 |
| 8 | 에이전트 과부하 | load_factor 확인 -32008 | -32008 | 대체 에이전트 선택 또는 지수 백오프 | CB OPEN 전이 시 | -0.15 |
| 9 | 서버 내부 오류 | -32603 응답 | -32603 | 지수 백오프 재시도 (3회) | 재시도 소진 시 | -0.3 |
| 10 | Request Timeout | HTTP 408 | 408 | 지수 백오프 재시도 (3회) | CB OPEN 전이 시 | -0.2 |
| 11 | Rate Limit | HTTP 429 | 429 | Retry-After 대기 | 60초 초과 대기 시 | -0.1 |
| 12 | Agent Unavailable | HTTP 503 | 503 | 대체 에이전트 즉시 선택 | 대체 에이전트 없음 | -0.3 |
| 13 | 인증 실패 (mTLS/JWT) | HTTP 401 | 401 | 토큰/인증서 갱신 후 재시도 | CB OPEN 전이 시 | -0.3 |
| 14 | 권한 부족 | HTTP 403 | 403 | 즉시 거부, 권한 확인 안내 | 반복 시 (5회/분) | -0.4 |
| 15 | CB OPEN 상태 요청 | CB 상태 확인 | - | failover 또는 60초 대기 | 대체 에이전트 없음 | -0.3 |

---

## §12. 복구/재시도 Phase별 흐름도

### 12.1 Phase 1 (MVP) 복구 흐름도

```
[에러 발생]
    │
    ├─ Permanent? ──YES──▶ [즉시 실패 반환] → [클라이언트 알림]
    │                         │
    │                    [감사 로그 기록]
    │
    └─ Transient? ──YES──▶ [재시도 가능?]
                              │
                         ┌────┴────┐
                    YES  │         │  NO
                         ▼         ▼
                  [지수 백오프]  [failover 시도]
                    │              │
              ┌─────┴─────┐  ┌────┴────┐
              │ 성공      │  │ 대체    │
              ▼           ▼  │ 에이전트│
           [완료]    [실패]  │ 있음?   │
                       │     └────┬────┘
                  [CB +1]     YES │ NO
                       │         ▼    ▼
                  [CB≥3?]    [전달] [I-20 에스컬레이션]
                  YES│ NO
                     ▼    ▼
               [OPEN] [다음 재시도]
                  │
            [failover 시도]
```

### 12.2 Phase 2 (확장) 복구 흐름도 — SSE 스트리밍 에러

```
[SSE 스트림 중 에러]
    │
    ├─ 연결 끊김 (네트워크) ──▶ [자동 재연결 (3회)]
    │                              │
    │                         [재연결 성공?]
    │                         YES │ NO
    │                             ▼    ▼
    │                        [스트림 재개] [I-20 에스컬레이션]
    │
    └─ 서버 에러 (500/503) ──▶ [대체 에이전트 SSE 스트림 개시]
```

### 12.3 Phase 3 (최적화) 복구 흐름도 — 지능형 failover

```
[에러 발생]
    │
    ├─ [에이전트 성능 메트릭 분석]
    │      │
    │      ├─ 과거 실패율 > 50% ──▶ [사전 차단 (preemptive CB)]
    │      └─ 과거 실패율 ≤ 50% ──▶ [표준 재시도]
    │
    └─ [지능형 대체 에이전트 선택]
           │
           ├─ 기술 스코어링 (AgentCard.skills 매칭)
           ├─ 부하 스코어링 (load_factor)
           └─ 신뢰도 스코어링 (과거 성공률)
```

### 12.4 Confidence Penalty 표

| 에러 유형 | 기본 penalty | 재시도 성공 시 회복 | 재시도 실패 시 누적 | 최대 누적 |
|----------|:----------:|:-----------------:|:-----------------:|:--------:|
| Transient (서버) | -0.2 | +0.15 | -0.1 추가 | -0.6 |
| Transient (네트워크) | -0.15 | +0.1 | -0.1 추가 | -0.5 |
| Permanent (입력) | -0.1 | N/A | N/A | -0.1 |
| Permanent (권한) | -0.4 | N/A | N/A | -0.4 |
| CB OPEN 전이 | -0.3 | +0.2 (CLOSED 복귀 시) | -0.15 추가 | -0.7 |
| Failover 성공 | -0.05 | N/A (성공이므로) | N/A | -0.05 |
| Failover 실패 | -0.4 | N/A | -0.2 추가 | -0.8 |

---

## §13. P1-1 / P1-5 세션 간 인터페이스 Cross-Check

### 13.1 P1-1 json_rpc_schema.md 에러 코드 정합 확인

| P1-1 §5 에러 코드 | 본 카탈로그 | 코드 일치 | 메시지 일치 | recoverable 일치 | 복구 전략 일치 | 결과 |
|-------------------|-----------|:---------:|:---------:|:----------------:|:-------------:|:----:|
| §5.1 `-32700` Parse error | §3 S-1 | YES | YES | YES (NO) | YES | MATCH |
| §5.1 `-32600` Invalid Request | §3 S-2 | YES | YES | YES (NO) | YES | MATCH |
| §5.1 `-32601` Method not found | §3 S-3 | YES | YES | YES (NO) | YES | MATCH |
| §5.1 `-32602` Invalid params | §3 S-4 | YES | YES | YES (NO) | YES | MATCH |
| §5.1 `-32603` Internal error | §3 S-5 | YES | YES | YES (YES) | YES | MATCH |
| §5.2 `-32001` Task not found | §4 C-1 | YES | YES | YES (YES) | YES | MATCH |
| §5.2 `-32002` Task cannot be canceled | §4 C-2 | YES | YES | YES (NO) | YES | MATCH |
| §5.2 `-32003` Push notification not supported | §4 C-3 | YES | YES | YES (YES) | YES | MATCH |
| §5.2 `-32004` Unsupported operation | §4 C-4 | YES | YES | YES (YES) | YES | MATCH |
| §5.2 `-32005` Content type not supported | §4 C-5 | YES | YES | YES (YES) | YES | MATCH |
| §5.3 HTTP `408` Timeout | §5 H-1 | YES | YES | YES (YES) | YES | MATCH |
| §5.3 HTTP `429` Rate Limited | §5 H-2 | YES | YES | YES (YES) | YES | MATCH |
| §5.3 HTTP `503` Unavailable | §5 H-3 | YES | YES | YES (YES) | YES | MATCH |
| §5.4 CB 3회→OPEN, 60초→HALF-OPEN | §8 | YES | YES | - | - | MATCH |

**결과**: P1-1 에러 코드 14건 전수 **MATCH**. 본 카탈로그의 확장 3건(-32006/-32007/-32008)은 P1-6 신규 정의.

### 13.2 P1-5 mtls_jwt.md 에러 코드 정합 확인

| P1-5 §7.1 에러 코드 | HTTP Status | JSON-RPC Error | 본 카탈로그 대응 | 결과 |
|---------------------|:-----------:|:--------------:|:---------------:|:----:|
| `INVALID_TOKEN_SIGNATURE` | 401 | -32600 | §5 H-4 (401→인증 갱신) | MATCH |
| `TOKEN_EXPIRED` | 401 | -32600 | §5 H-4 | MATCH |
| `TOKEN_REPLAY_DETECTED` | 401 | -32600 | §5 H-4 | MATCH |
| `CERT_EXPIRED` | 401 | -32600 | §5 H-4 | MATCH |
| `CERT_REVOKED` | 401 | -32600 | §5 H-4 | MATCH |
| `AUDIENCE_MISMATCH` | 403 | -32600 | §5 H-5 (403→권한 확인) | MATCH |
| `INSUFFICIENT_SCOPE` | 403 | -32600 | §5 H-5 | MATCH |
| `DELEGATION_DEPTH_EXCEEDED` | 403 | -32600 | §4 C-7 (-32007, 애플리케이션 계층) + §5 H-5 | MATCH |
| `CIRCUIT_OPEN` | 503 | -32001 | §5 H-3 (503→failover) + §8 CB | MATCH |

**결과**: P1-5 인증 에러 9건 전수 **MATCH**. P1-5는 인증 계층(HTTP/TLS), 본 카탈로그는 애플리케이션 계층(JSON-RPC) — 계층 분리 정합.

**P1-5 §7.1 `CIRCUIT_OPEN` 매핑 참고**: P1-5에서 `-32001`로 매핑한 것은 인증 계층 CB로 인한 Task 불가용 시 반환이며, 본 카탈로그에서는 CB OPEN 시 failover 우선(§7) + 실패 시 에스컬레이션(§9) 경로를 정의. 두 문서의 CB 임계값(3회→OPEN, 60초→HALF-OPEN)은 LOCK-A2A-09 원본과 **character-level 동일**.

---

## §14. Phase 2 통합 테스트 시나리오 (14건)

| # | 시나리오 | 입력 | 기대 결과 | 검증 포인트 |
|---|---------|------|----------|------------|
| T-01 | 표준 에러 -32700 Parse error | malformed JSON 전송 | -32700 에러 응답, CB 미적용 | §3 S-1 + §8.3 CB 미적용 |
| T-02 | 커스텀 에러 -32001 Task not found | 존재하지 않는 task_id로 tasks/get | -32001 에러 응답 + recovery 로그 | §4 C-1 + §10.1 로그 구조 |
| T-03 | 커스텀 에러 -32002 Task not cancelable | completed Task에 tasks/cancel | -32002 에러 응답, 재시도 불가 | §4 C-2 + P1-2 전이 매트릭스 |
| T-04 | 커스텀 에러 -32004 + failover | 미지원 기능 요청 → 대체 에이전트 선택 | -32004 → failover → 대체 에이전트 성공 | §4 C-4 + §7 failover |
| T-05 | 확장 에러 -32006 Context exceeded | max_tokens 초과 메시지 전송 | -32006 에러 + 압축 제안 | §4 C-6 + LOCK-A2A-05 |
| T-06 | 확장 에러 -32007 Delegation depth | depth=4 JWT로 요청 | -32007 에러 + 즉시 거부 | §4 C-7 + LOCK-A2A-07 + P1-5 §4.4 |
| T-07 | 확장 에러 -32008 Agent overloaded | load_factor=0.95 에이전트에 요청 | -32008 에러 + failover 시도 | §4 C-8 + §7 failover |
| T-08 | HTTP 408 + 지수 백오프 | 3회 연속 408 주입 → 4회째 성공 | 1초/2초/4초 간격 재시도 후 성공 | §5 H-1 + §6 백오프 알고리즘 |
| T-09 | HTTP 429 + Retry-After | 429 응답 (Retry-After: 30) | 30초 대기 후 재시도 성공 | §5 H-2 + Retry-After 준수 |
| T-10 | HTTP 503 + failover | 503 응답 → 대체 에이전트 선택 | 대체 에이전트로 투명 전달 | §5 H-3 + §7 failover |
| T-11 | CB OPEN 전이 | 동일 에이전트에 연속 3회 실패 주입 | CB OPEN 전이 + failover | §8 CB + LOCK-A2A-09 |
| T-12 | CB HALF-OPEN → CLOSED 복귀 | CB OPEN 후 60초 대기 → 성공 요청 | HALF-OPEN → CLOSED | §8.1 상태 전이 |
| T-13 | 에스컬레이션 (재시도+failover 소진) | 3회 재시도 실패 + failover 대상 없음 | I-20 에스컬레이션 페이로드 전달 | §9 에스컬레이션 + severity ERROR |
| T-14 | 복합: 인증실패→CB→failover | 연속 3회 인증 실패 → CB OPEN → 대체 에이전트 | 401→CB OPEN→failover 성공 | §8.3 401 CB 적용 + §7 failover + P1-5 §6 |

---

## §15. LOCK 준수 확인

| LOCK ID | 항목 | 값 | 본 문서 반영 | 상태 |
|---------|------|---|------------|------|
| LOCK-A2A-05 | 컨텍스트 윈도우 한계 | 모델별 max_tokens 준수, 초과 시 압축 | §4 C-6 (-32006) | PASS |
| LOCK-A2A-07 | JWT delegation chain 최대 깊이 | 3 | §4 C-7 (-32007) | PASS |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | §8 전체 | PASS |

---

## §16. §6.1 이슈 대응 매핑

| §6.1 항목 | 내용 | 본 문서 대응 섹션 | 상태 |
|----------|------|-----------------|------|
| #31 | A2A 에러 코드 카탈로그 (-32001 ~ -32005) | §4 커스텀 에러 8건 (기본 5건 + 확장 3건) | PASS |
| #32 | HTTP 에러 복구 (408, 429, 503) | §5 HTTP 레벨 에러 복구 정책 5건 | PASS |
| #33 | 지수 백오프 재시도 정책 | §6 재시도 정책 (초기 1초, 최대 60초, 최대 3회) | PASS |
| #34 | 대체 에이전트 선택 (failover) | §7 Failover 알고리즘 + 02_agent-discovery/ 연동 | PASS |

---

## §17. 검증 체크리스트

- [x] 에러 코드 최소 8개 정의: JSON-RPC 표준 5건 + A2A 커스텀 8건 = **13건** (요구사항 8건 초과 충족)
- [x] §6.1 항목 #31~#34 전수 대응: 에러 코드 카탈로그(§4), HTTP 복구(§5), 재시도 정책(§6), failover(§7)
- [x] LOCK-A2A-09 Circuit Breaker "3회→OPEN, 60초→HALF-OPEN" 연동 조건 명시 (§8)
- [x] 각 에러의 분류(Transient/Permanent/Conditional) + 복구 전략 매핑 (§2.2 + §4 + §5)
- [x] E4(에러 핸들링) L3 기준 충족: 에러 코드 카탈로그 + 복구 전략 + CB 연동 + failover 완전 정의
- [x] P1-1 에러 코드 14건 전수 MATCH (§13.1)
- [x] P1-5 인증 에러 9건 전수 MATCH (§13.2)

---

*Generated: 2026-04-10 | Session: P1-6 | Domain: 3-8_Conversation-A2A*
*L3 기준 E4(에러 핸들링) 충족 — 에러 코드 카탈로그 13건 + 복구 전략 매핑 + CB 연동 + Failover + 에스컬레이션*
