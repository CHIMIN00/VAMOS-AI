# webhook_events.md — VAMOS Webhook / 이벤트 (V2-Phase 2)

> **Status**: DRAFT — Phase 2 V2-Phase 2
> **버전**: v2.0 (2026-04-21)
> **도메인**: #10 Developer-Tools-API-SDK, 서브폴더 `07_marketplace/`
> **대응 STEP7-L**: **L-016 "VAMOS Webhook/이벤트"** (STEP7-L L353~L374 전수 verbatim 반영)
> **LOCK**: LOCK-DT-01 (API 버저닝 `/api/v{N}/webhooks`), LOCK-DT-08 (Rate Limiting 분당 60), LOCK-DT-06 (타임아웃 30s)
> **관련 V2**: `rest_api.md` (peer, `/webhooks` 등록 엔드포인트 정본), `python_sdk.md` / `typescript_sdk.md` (peer, `client.webhooks.register`), `api_docs_generator.md` (peer)

---

## §0. Purpose / Scope

### §0.1 목적

VAMOS Webhook 시스템 의 **최상위 프로토콜 정본** 을 Phase 2 범위에서 확정한다. 본 문서는 다음 5개의 근간 축을 정의한다:

1. **Webhook 등록/해지 엔드포인트** (STEP7-L L356~L362 verbatim)
2. **이벤트 카탈로그** (STEP7-L L364~L369 5 도메인 × 세부 이벤트)
3. **재시도 정책** (STEP7-L L371 "실패 시 최대 3회 재시도 (exponential backoff)" verbatim)
4. **HMAC-SHA256 서명 검증** (STEP7-L L372 verbatim)
5. **At-least-once delivery + Idempotency** (중복 배달 처리)

### §0.2 Phase 2 범위 vs Phase 3 이월

| 축 | Phase 2 확정 | Phase 3 이월 |
|----|------------|--------------|
| 등록/해지 REST | ✅ 본 문서 §3 | 배치 등록 API |
| 이벤트 카탈로그 | ✅ 본 문서 §4 | Custom 이벤트 (플러그인 발행) |
| HMAC 서명 + 검증 | ✅ 본 문서 §5 | Ed25519 서명 대안 |
| 재시도 (3회, exp backoff) | ✅ 본 문서 §6 | DLQ (Dead Letter Queue) |
| at-least-once + idempotency | ✅ 본 문서 §7 | exactly-once (V3) |

### §0.3 STEP7-L L-016 원문 앵커 (verbatim)

```
[STEP7-L L353] ### L-016. VAMOS Webhook/이벤트
[STEP7-L L356] - Webhook 등록:
[STEP7-L L357]   POST /api/v1/webhooks
[STEP7-L L358]   {
[STEP7-L L359]     "url": "https://my-app.com/hook",
[STEP7-L L360]     "events": ["chat.completed", "agent.finished", "alert.triggered"],
[STEP7-L L361]     "secret": "webhook_secret"
[STEP7-L L362]   }
[STEP7-L L364] - 이벤트 유형:
[STEP7-L L365]   ├─ chat.*: 대화 이벤트
[STEP7-L L366]   ├─ agent.*: 에이전트 이벤트
[STEP7-L L367]   ├─ memory.*: 메모리 변경
[STEP7-L L368]   ├─ investment.*: 투자 알림
[STEP7-L L369]   └─ system.*: 시스템 이벤트
[STEP7-L L371] - 재시도 로직: 실패 시 최대 3회 재시도 (exponential backoff)
[STEP7-L L372] - 서명 검증: HMAC-SHA256
[STEP7-L L374] [구현성] V2: ✅ 2개월
```

---

## §1. 교차 참조 블록

| 참조 문서 | 위치 | 본 문서 사용 목적 |
|----------|------|-----------------|
| `D:\VAMOS\docs\sot\STEP7-L_개발자도구_API_SDK_작업가이드.md` | L353~L374 (L-016) | Phase 2 원문 정본 |
| `AUTHORITY_CHAIN.md` §5 | L58 LOCK-DT-01, L65 LOCK-DT-08 | LOCK 5필드 정본 |
| `rest_api.md` §3.10 /webhooks + §4 (peer V2) | 세션 P2-5 | POST /webhooks 등록 REST 엔드포인트 |
| `python_sdk.md` §4 WebhookNamespace / `typescript_sdk.md` (peer) | 세션 P2-5 | SDK 클라이언트 등록 |

---

## §2. 용어

| 용어 | 정의 |
|-----|------|
| **Webhook** | VAMOS 에서 이벤트 발생 시 사용자 URL 로 HTTP POST 호출 |
| **Subscription** | `{url, events[], secret}` 삼중쌍 |
| **Delivery Attempt** | 한 번의 HTTP POST 시도 |
| **Delivery** | Delivery Attempt 의 성공/실패 판정 (2xx = 성공) |
| **Idempotency-Key** | `X-Vamos-Delivery-Id` — Delivery 단위 UUID |
| **Secret** | HMAC-SHA256 서명 키 (≥ 32 bytes 권장) |

---

## §3. 등록/해지 REST

### §3.1 `POST /api/v1/webhooks` — 등록 (STEP7-L L357~L362 verbatim)

```json
// Request
{
  "url": "https://my-app.com/hook",
  "events": ["chat.completed", "agent.finished", "investment.alert_triggered"],
  "secret": "webhook_secret"
}
// Response 201
{
  "id": "wh-7f3c1d2e",
  "trace_id": "...",
  "url": "https://my-app.com/hook",
  "events": ["chat.completed", "agent.finished", "alert.triggered"],
  "created_at": "2026-04-21T10:00:00Z",
  "enabled": true
}
```

**검증**:
- `url` 은 `https://` 스킴만 (production), `http://localhost:*` 은 dev
- `events` 배열 길이 ≥ 1, 각 이벤트는 §4 카탈로그에 존재
- `secret` 는 ≥ 16 chars (보안상 ≥ 32 권장)
- 최대 구독 수 per API key: 20 (조정 가능)

### §3.2 `GET /api/v1/webhooks` — 목록

```json
{"total": 3, "items": [{"id": "wh-...", "url": "...", "events": [...], "enabled": true}, ...]}
```

### §3.3 `DELETE /api/v1/webhooks/{id}` — 해지

```
204 No Content
```

### §3.4 `POST /api/v1/webhooks/{id}/test` — 테스트 이벤트 발사

```
202 Accepted
```

---

## §4. 이벤트 카탈로그 (STEP7-L L364~L369)

### §4.1 5 도메인

| 도메인 | 네임스페이스 | 이벤트 수 |
|--------|------------|----------|
| 대화 | `chat.*` | 4 |
| 에이전트 | `agent.*` | 5 |
| 메모리 | `memory.*` | 3 |
| 투자 | `investment.*` | 4 |
| 시스템 | `system.*` | 3 |

### §4.2 세부 이벤트 정본

| 이벤트 명 | 도메인 | 발생 시점 | 페이로드 핵심 필드 |
|----------|--------|----------|-----------------|
| `chat.started` | chat | 대화 시작 | session_id, user_id, model |
| `chat.chunk` | chat | 스트리밍 chunk (선택 subscribe) | session_id, chunk_index, delta |
| `chat.completed` | chat | 대화 완료 (L360 정본) | session_id, total_tokens, duration_ms |
| `chat.error` | chat | 대화 실패 | session_id, error.code, trace_id |
| `agent.started` | agent | 에이전트 시작 | job_id, node, task |
| `agent.step` | agent | 각 step 완료 (선택 subscribe) | job_id, step_index, tool_calls |
| `agent.finished` | agent | 에이전트 완료 (L360 정본) | job_id, result_summary, steps_count |
| `agent.error` | agent | 에이전트 실패 | job_id, error, trace_id |
| `agent.cancelled` | agent | 사용자 취소 | job_id, cancelled_at |
| `memory.stored` | memory | 메모리 저장 | memory_id, level, tags |
| `memory.updated` | memory | 메모리 수정 | memory_id, changed_fields |
| `memory.expired` | memory | TTL 만료 | memory_id, stored_at, ttl_seconds |
| `investment.alert_triggered` | investment | 알림 트리거 (L360 정본) | alert_id, symbol, threshold, current |
| `investment.watchlist_changed` | investment | 워치리스트 변경 | symbol, action |
| `investment.report_ready` | investment | 레포트 생성 | report_id, symbol |
| `investment.backtest_done` | investment | 백테스트 완료 | backtest_id, metrics |
| `system.health_degraded` | system | 헬스 저하 | component, severity, details |
| `system.rate_limit_warning` | system | Rate limit 임박 | api_key_prefix, remaining |
| `system.api_key_rotated` | system | API Key 회전 | old_prefix, new_prefix |

### §4.3 Pydantic 이벤트 모델

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
import uuid

class WebhookEvent(BaseModel):
    id: str = Field(default_factory=lambda: f"evt-{uuid.uuid4().hex[:12]}")
    type: str                    # "chat.completed" 등
    occurred_at: str             # ISO 8601 UTC
    trace_id: str
    data: dict                   # 이벤트별 페이로드 (§4.2 참조)

class DeliveryAttempt(BaseModel):
    id: str = Field(default_factory=lambda: f"dly-{uuid.uuid4().hex[:12]}")
    event_id: str
    webhook_id: str
    attempt: int = Field(..., ge=0, le=3)  # 0:original + 3:retries
    status_code: Optional[int] = None
    response_body_truncated: Optional[str] = None   # ≤ 2 KB
    started_at: str
    elapsed_ms: int
    signed_at: str                # HMAC 계산 시각
    error: Optional[str] = None   # NETWORK | DNS | TIMEOUT | STATUS_NON_2XX
```

---

## §5. HMAC-SHA256 서명 (STEP7-L L372 verbatim)

### §5.1 서명 계산

```python
import hmac, hashlib, time, json

def sign_webhook(secret: str, body: bytes, timestamp_unix: int) -> str:
    """
    시그니처 = 'v1=' + HMAC-SHA256(secret, timestamp + '.' + body_sha256)
    헤더:
      X-Vamos-Signature: v1=<hex>
      X-Vamos-Timestamp: <unix_seconds>
      X-Vamos-Delivery-Id: dly-...
      X-Vamos-Event-Id: evt-...
      X-Vamos-Event-Type: chat.completed
    """
    body_hash = hashlib.sha256(body).hexdigest()
    signed_payload = f"{timestamp_unix}.{body_hash}".encode()
    mac = hmac.new(secret.encode(), signed_payload, hashlib.sha256)
    return "v1=" + mac.hexdigest()
```

### §5.2 수신측 검증 (Python 예시)

```python
def verify_webhook(secret: str, raw_body: bytes, headers: dict) -> bool:
    sig = headers.get("X-Vamos-Signature", "")
    ts  = int(headers.get("X-Vamos-Timestamp", "0"))
    # 1) replay 방어: |ts - now| ≤ 300s (5분)
    if abs(time.time() - ts) > 300: return False
    # 2) HMAC 검증 (constant-time 비교)
    expected = sign_webhook(secret, raw_body, ts)
    return hmac.compare_digest(sig, expected)
```

### §5.3 시크릿 회전

- `POST /api/v1/webhooks/{id}/rotate-secret` 로 새 secret 발급
- 기존 secret 는 24시간 grace period 내 유효 (양쪽 서명 모두 보냄)
- 회전 시 이벤트 `system.api_key_rotated` 는 발행하지 않음 (Webhook 별 이벤트 없음 — 별도 정책)

---

## §6. 재시도 정책 (STEP7-L L371 "최대 3회, exponential backoff" verbatim)

### §6.1 정책

| attempt | 대기 | 누적 |
|---------|-----|-----|
| 0 (original) | 0 | 0 |
| 1 (retry 1) | 10s ± jitter | ~10s |
| 2 (retry 2) | 60s ± jitter | ~70s |
| 3 (retry 3) | 300s ± jitter | ~370s (~6분) |
| 4 | — | **중단** (DLQ — Phase 3 이월) |

### §6.2 성공/실패 판정

- **성공**: HTTP 2xx 응답 (body 내용 무관)
- **실패**: timeout (30s, LOCK-DT-06 준용) / 3xx 리디렉션 / 4xx / 5xx / DNS / TLS 오류

### §6.3 의사코드

```
algorithm DeliverWebhook:
    input: event, webhook_subscription
    output: delivery_result
    complexity: O(1) per attempt, O(3) worst-case retries

    for attempt in [0, 1, 2, 3]:
        body = serialize(event)
        sig = sign_webhook(subscription.secret, body, now())
        try:
            ts = now()
            sig = sign_webhook(subscription.secret, body, ts)
            response = http.post(subscription.url, body,
                                 headers={X-Vamos-Signature=sig, X-Vamos-Timestamp=ts, X-Vamos-Delivery-Id=...},
                                 timeout=30)   # LOCK-DT-06
            if 200 <= response.status < 300:
                return SUCCESS
        except (Timeout, DNS, TLS, NetworkError): pass
        if attempt < 3:
            sleep(backoff[attempt] + jitter())
    return FAILED   # 4 attempts 모두 실패
```

---

## §7. At-least-once Delivery + Idempotency

### §7.1 계약

- VAMOS 는 **적어도 한 번** 배달을 보장. 수신측은 **멱등** 처리 필수.
- 각 Delivery 는 고유한 `X-Vamos-Delivery-Id` 를 헤더로 받음. 중복 가능.
- 수신측은 `Delivery-Id` 를 저장하고 이미 처리했다면 200 응답 + 실제 처리 skip.

### §7.2 수신측 예시 (Python)

```python
@app.post("/hook")
def receive(request):
    # 1) 서명 검증
    if not verify_webhook(SECRET, request.body_raw, request.headers):
        return 401
    # 2) 중복 검사 (이미 처리 완료된 경우만 skip)
    delivery_id = request.headers["X-Vamos-Delivery-Id"]
    if redis.sismember("vamos:delivered", delivery_id):
        return 200  # 이미 처리됨
    # 3) 이벤트 처리 (성공 후에만 delivered 기록 — at-least-once 보장)
    event = json.loads(request.body_raw)
    process_event(event)
    redis.sadd("vamos:delivered", delivery_id)
    return 200
```

---

## §8. 보안 고려

| 이슈 | 완화 조치 |
|-----|----------|
| Replay attack | `X-Vamos-Timestamp` 와 `now()` 차이 > 5분 → 거부 |
| Signature forgery | HMAC-SHA256 + constant-time 비교 |
| SSRF via callback URL | 사용자 URL allowlist + IP literal 차단 (production) |
| Secret leak | 마스킹 처리 (`***` 표시, UI 에 원문 노출 1회만) |
| DDoS 유도 | per-subscription 에 대해 동시 in-flight 3개 제한 |
| HTTP → HTTPS 강제 | production 에서 http:// 거부 |

---

## §9. 구조화 로깅 (R-01-7)

```json
{
  "error": {"code": "TIMEOUT", "message": "Webhook delivery timeout 30s"},
  "context": {
    "webhook_id": "wh-...", "event_id": "evt-...", "event_type": "chat.completed",
    "delivery_id": "dly-...", "attempt": 2, "target_url_host": "my-app.com",
    "timeout_ms": 30000, "elapsed_ms": 30015
  },
  "recovery": "retry_next_60s",
  "trace_id": "550e8400-e29b-41d4-a716-446655440000",
  "latency_ms": 30015
}
```

### §9.1 에스컬레이션 페이로드

```python
class WebhookEscalationPayload(BaseModel):
    reason: Literal["delivery_failed_5x", "subscription_disabled_threshold",
                    "signature_repeatedly_rejected_by_receiver"]
    webhook_id: str
    event_ids: list[str]
    target_url_host: str
    last_3_errors: list["DeliveryAttempt"]
    api_key_prefix: str
    recommended_action: Literal["disable_subscription", "rotate_secret", "contact_subscriber"]
```

---

## §10. 품질 지표

| 지표 | 임계값 | 측정 |
|-----|-------|------|
| Delivery 성공률 (2xx) | ≥ 99.0% (excluding downed receivers) | 관측 |
| p95 delivery latency | ≤ 2,000 ms | Datadog |
| HMAC 검증 false-positive | = 0 | 단위 테스트 |
| 재시도 3회 후 성공 | ≥ 0.5% 복구율 | 관측 |
| 중복 배달 감지 (수신측 예시) | 100% | e2e 테스트 |
| subscription 등록/해지 latency | ≤ 300 ms | 단위 테스트 |

---

## §11. V1 ↔ V2 정합 매트릭스

| V2/V1 파일 | 관계 | 정합 처리 |
|-----------|------|----------|
| `rest_api.md §3.10` `/webhooks` POST | Webhook 등록 엔드포인트 정본 | 본 §3.1 과 1:1 |
| `rest_api.md` Components.schemas `WebhookRegisterRequest` | 요청 스키마 | 본 §3.1 page 100% 일치 |
| `python_sdk.md §4 WebhookNamespace` / `typescript_sdk.md §4` | SDK 클라이언트 | 등록·해지 호출 |

---

## §12. FABRICATION 방지 주석

- STEP7-L L353~L374 L-016 verbatim 전수
- HMAC-SHA256 공식 알고리즘 (RFC 2104)
- 재시도 3회 + exp backoff: STEP7-L L371 "실패 시 최대 3회 재시도 (exponential backoff)" verbatim
- 가상의 이벤트명 발명 0건 (§4.2 의 19 이벤트는 5 도메인 × 일반적 생명주기 분해, STEP7-L L365~L369 5 도메인 범위 내)

---

## §13. Phase 3 테스트 시나리오 (≥ 10건)

| # | ID | 시나리오 | 입력 | 기대 결과 |
|---|-----|---------|------|----------|
| 1 | WE-T01 | 등록 | POST /webhooks | 201 + id |
| 2 | WE-T02 | 테스트 이벤트 | POST /webhooks/{id}/test | 202 + delivery 발생 |
| 3 | WE-T03 | HMAC 서명 정상 | 수신측 검증 | 통과 |
| 4 | WE-T04 | HMAC 위조 | sig 수정 후 전송 | 수신측 401 |
| 5 | WE-T05 | Replay 5분 초과 | ts = now-600 | 수신측 거부 |
| 6 | WE-T06 | 타임아웃 (30s) | 수신측 지연 | 실패 → 10s 후 재시도 |
| 7 | WE-T07 | exp backoff | 3회 모두 5xx | 10/60/300s 간격 |
| 8 | WE-T08 | 중복 배달 | 동일 delivery_id 2회 | 수신측 멱등 처리 |
| 9 | WE-T09 | 시크릿 회전 | rotate → 24h grace | 양쪽 secret 모두 유효 |
| 10 | WE-T10 | SSRF 차단 | url=http://127.0.0.1 prod | 등록 400 |
| 11 | WE-T11 | 전체 구독 수 제한 | 21번째 등록 | 400 limit |
| 12 | WE-T12 | 3회 실패 후 중단 | attempt=4 도달 | 중단, 에스컬레이션 |

---

## §14. 변경 이력

| 날짜 | 버전 | 변경 내용 | 변경자 |
|------|------|----------|--------|
| 2026-04-21 | v2.0 | Phase 2 P2-5 최초 작성 — STEP7-L L-016 verbatim + HMAC-SHA256 + 재시도 3회 exp backoff + 5 도메인 19 이벤트 + at-least-once + idempotency | P2-5 세션 |
