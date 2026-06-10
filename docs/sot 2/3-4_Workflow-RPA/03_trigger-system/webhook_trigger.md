# Webhook 트리거 (외부 웹훅 수신) — L3 상세 명세

> **N-ID**: N-003d (EXTEND)
> **V단계**: V1
> **도메인**: 3-4_Workflow-RPA / 03_trigger-system
> **정본**: sot 2/3-4_Workflow-RPA/03_trigger-system/webhook_trigger.md
> **교차참조**: event_trigger.md (EventBus "webhook" 채널), variable_secret_management.md (HMAC 시크릿)

---

## 1. 개요

Webhook 트리거는 외부 시스템이 HTTP 요청을 보내면 해당 워크플로우를 즉시 실행하는 push 기반 트리거이다. 워크플로우별 고유 엔드포인트를 자동 생성하고, HMAC-SHA256 서명 검증 또는 API Key 인증으로 보안을 확보한다. 수신된 JSON 페이로드는 워크플로우 입력 변수로 자동 매핑된다.

> LOCK (기존 명세 §4(5종) + STEP7-N N-003(+2종) / LOCK-WF-06): Time(cron), Event(이벤트), Condition(조건), Webhook(웹훅), Manual(수동), Conversation(대화 기반), Ambient(앰비언트) — 7유형 트리거 체계

---

## 2. 핵심 제약 (LOCK)

> LOCK (기존 명세 §4(5종) + STEP7-N N-003(+2종) / LOCK-WF-06): Time(cron), Event(이벤트), Condition(조건), Webhook(웹훅), Manual(수동), Conversation(대화 기반), Ambient(앰비언트) — 7유형 트리거 체계

> LOCK (가이드 R-07-2 / LOCK-WF-03): Human Approval 타임아웃 = 10분 (600초)

---

## 3. 입력 스키마

```typescript
interface WebhookTriggerConfig {
  type: "webhook";
  trigger_id: string;                  // UUID v7
  workflow_id: string;                 // 대상 워크플로우 ID

  // --- 엔드포인트 ---
  endpoint_path: string;               // 자동 생성: "/api/v1/webhooks/{trigger_id}"
  allowed_methods: ("POST" | "PUT" | "GET")[];  // 허용 HTTP 메서드 (기본: ["POST"])

  // --- 인증 ---
  auth_mode: "none" | "api_key" | "hmac_sha256";
  secret_id?: string;                  // 시크릿 저장소 참조 (auth_mode != "none")

  // --- 페이로드 매핑 ---
  payload_mapping?: PayloadMapping[];  // JSON 필드 → 워크플로우 변수 매핑
  accept_raw: boolean;                 // true: 매핑 없이 전체 body를 변수로 전달

  // --- Rate Limiting ---
  rate_limit: {
    max_requests_per_minute: number;   // 기본 100
    burst: number;                     // 버스트 허용량 (기본 10)
  };

  // --- IP 화이트리스트 ---
  ip_whitelist?: string[];             // CIDR 표기 (빈 배열 = 모든 IP 허용)

  // --- 메타데이터 ---
  enabled: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

interface PayloadMapping {
  source_path: string;                 // JSON 경로 (dot notation): "data.user.id"
  target_variable: string;             // 워크플로우 변수명: "user_id"
  required: boolean;                   // 필수 여부 (true면 누락 시 400 응답)
  default_value?: any;                 // required=false 시 기본값
}
```

---

## 4. 웹훅 수신 처리

### 4.1 수신 파이프라인

```
[외부 HTTP 요청]
    │
    ▼
[Step 1: IP 화이트리스트 검증] ─── 미허용 IP → 403 Forbidden
    │
    ▼
[Step 2: Rate Limit 검증] ─── 초과 → 429 Too Many Requests
    │
    ▼
[Step 3: HTTP 메서드 검증] ─── 미허용 메서드 → 405 Method Not Allowed
    │
    ▼
[Step 4: 인증 검증] ─── 실패 → 401 Unauthorized
    │
    ▼
[Step 5: 페이로드 파싱 + 매핑] ─── 필수 필드 누락 → 400 Bad Request
    │
    ▼
[Step 6: 트리거 이벤트 발행] → EventBus "internal" 채널 → 실행 큐 등록
    │
    ▼
[202 Accepted + execution_id 반환]
```

### 4.2 핸들러 구현

```python
# webhook_handler.py
class WebhookHandler:
    """웹훅 HTTP 엔드포인트 핸들러"""

    async def handle_request(self, request: Request) -> Response:
        trigger_id = request.path_params["trigger_id"]
        config = await self.store.get(trigger_id)

        if not config or not config.enabled:
            return Response(status_code=404, body={"error": "Webhook not found"})

        # Step 1: IP 화이트리스트
        if config.ip_whitelist:
            client_ip = request.client.host
            if not self._is_ip_allowed(client_ip, config.ip_whitelist):
                return Response(status_code=403, body={"error": "IP not allowed"})

        # Step 2: Rate limit
        if not await self._check_rate_limit(trigger_id, config.rate_limit):
            return Response(status_code=429, body={"error": "Rate limit exceeded"})

        # Step 3: HTTP 메서드
        if request.method not in config.allowed_methods:
            return Response(status_code=405, body={"error": "Method not allowed"})

        # Step 4: 인증
        if not await self._verify_auth(request, config):
            return Response(status_code=401, body={"error": "Authentication failed"})

        # Step 5: 페이로드 파싱 + 매핑
        try:
            payload = await request.json()
            variables = self._map_payload(payload, config)
        except ValidationError as e:
            return Response(status_code=400, body={"error": str(e)})

        # Step 6: 트리거 이벤트 발행
        trigger_event = TriggerEvent(
            trigger_id=trigger_id,
            trigger_type="webhook",
            workflow_id=config.workflow_id,
            fired_at=datetime.utcnow().isoformat(),
            payload={
                "source_ip": request.client.host,
                "http_method": request.method,
                # 인증/서명/쿠키 헤더 제거 — 안전 헤더 allowlist만 전달 (자격증명 유출 방지)
                "headers": {k: v for k, v in request.headers.items() if k.lower() in ("content-type", "user-agent", "x-github-event", "x-request-id")},
                "variables": variables,
            },
        )
        await self.event_bus.publish("internal", trigger_event)

        return Response(
            status_code=202,
            body={
                "accepted": True,
                "trigger_id": trigger_id,
                "workflow_id": config.workflow_id,
            },
        )
```

---

## 5. 인증 메커니즘

### 5.1 HMAC-SHA256 서명 검증

```python
async def _verify_hmac(self, request: Request, config: WebhookTriggerConfig) -> bool:
    """HMAC-SHA256 서명 검증"""
    signature_header = request.headers.get("X-Webhook-Signature-256")
    if not signature_header:
        return False

    # 시크릿 저장소에서 HMAC 키 조회
    secret = await self.secret_store.get(config.secret_id)
    body = await request.body()

    expected = "sha256=" + hmac.new(
        secret.encode(), body, hashlib.sha256,
    ).hexdigest()

    return hmac.compare_digest(expected, signature_header)
```

### 5.2 API Key 인증

```python
async def _verify_api_key(self, request: Request, config: WebhookTriggerConfig) -> bool:
    """API Key 헤더 검증"""
    api_key = request.headers.get("X-API-Key")
    if not api_key:
        return False

    stored_key = await self.secret_store.get(config.secret_id)
    return hmac.compare_digest(api_key, stored_key)
```

### 5.3 인증 선택

```python
async def _verify_auth(self, request: Request, config: WebhookTriggerConfig) -> bool:
    match config.auth_mode:
        case "none":        return True
        case "api_key":     return await self._verify_api_key(request, config)
        case "hmac_sha256": return await self._verify_hmac(request, config)
```

---

## 6. 페이로드 매핑

```python
def _map_payload(self, payload: dict, config: WebhookTriggerConfig) -> dict:
    """JSON 페이로드 → 워크플로우 변수 매핑"""
    if config.accept_raw:
        return {"webhook_payload": payload}

    variables = {}
    for mapping in config.payload_mapping or []:
        value = self._get_nested_value(payload, mapping.source_path)

        if value is None:
            if mapping.required:
                raise ValidationError(f"Required field missing: {mapping.source_path}")
            value = mapping.default_value

        variables[mapping.target_variable] = value

    return variables
```

---

## 7. Rate Limiting

```python
class WebhookRateLimiter:
    """Token Bucket 기반 Rate Limiter (Redis 사용)"""

    async def check(self, trigger_id: str, limit: dict) -> bool:
        """True = 허용, False = 제한 초과"""
        key = f"ratelimit:webhook:{trigger_id}"
        now = time.time()

        # Lua 스크립트로 원자적 토큰 버킷 구현
        result = await self.redis.eval(
            self.TOKEN_BUCKET_SCRIPT,
            keys=[key],
            args=[
                limit["max_requests_per_minute"],
                limit["burst"],
                now,
            ],
        )
        return result == 1

    TOKEN_BUCKET_SCRIPT = """
    local key = KEYS[1]
    local rate = tonumber(ARGV[1])
    local burst = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])

    local data = redis.call('HMGET', key, 'tokens', 'last_refill')
    local tokens = tonumber(data[1]) or burst
    local last_refill = tonumber(data[2]) or now

    -- 토큰 보충
    local elapsed = now - last_refill
    local refill = elapsed * (rate / 60.0)
    tokens = math.min(burst, tokens + refill)

    if tokens >= 1 then
        tokens = tokens - 1
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 120)
        return 1
    else
        redis.call('HMSET', key, 'tokens', tokens, 'last_refill', now)
        redis.call('EXPIRE', key, 120)
        return 0
    end
    """
```

---

## 8. 트리거 이벤트 스키마

```typescript
interface TriggerEvent {
  event_id: string;                    // UUID v7
  trigger_id: string;
  trigger_type: "webhook";
  workflow_id: string;
  fired_at: string;                    // ISO 8601
  payload: {
    source_ip: string;                 // 요청 IP
    http_method: string;
    headers: Record<string, string>;
    variables: Record<string, any>;    // 매핑된 워크플로우 변수
    raw_body_size: number;             // 원본 페이로드 크기 (bytes)
  };
}
```

---

## 9. 관리 API

```python
class WebhookTriggerManager:
    """웹훅 트리거 CRUD + 시크릿 관리"""

    async def create(self, config: WebhookTriggerConfig) -> TriggerResult:
        """웹훅 트리거 생성 → 엔드포인트 등록"""
        config.endpoint_path = f"/api/v1/webhooks/{config.trigger_id}"

        # 인증 시크릿 자동 생성 (auth_mode != "none")
        if config.auth_mode != "none" and not config.secret_id:
            secret = secrets.token_hex(32)
            config.secret_id = await self.secret_store.save(
                name=f"webhook-{config.trigger_id}",
                value=secret,
            )

        await self.store.save(config)
        return TriggerResult(
            success=True,
            trigger_id=config.trigger_id,
            endpoint_url=config.endpoint_path,
            secret_id=config.secret_id,
        )

    async def rotate_secret(self, trigger_id: str) -> str:
        """웹훅 시크릿 교체 (grace period 5분간 이전 키도 수용)"""
        config = await self.store.get(trigger_id)
        new_secret = secrets.token_hex(32)

        # 이전 키 grace period 설정
        await self.secret_store.set_grace_period(config.secret_id, grace_seconds=300)

        # 새 시크릿 저장
        config.secret_id = await self.secret_store.save(
            name=f"webhook-{trigger_id}",
            value=new_secret,
        )
        await self.store.save(config)
        return new_secret

    async def get_delivery_log(
        self, trigger_id: str, limit: int = 20,
    ) -> list[DeliveryLogEntry]:
        """최근 웹훅 수신 로그 조회"""
        return await self.log_store.get_recent(trigger_id, limit)
```

---

## 10. 사용 예시

### 10.1 GitHub Webhook → PR 자동 리뷰

```json
{
  "type": "webhook",
  "auth_mode": "hmac_sha256",
  "allowed_methods": ["POST"],
  "payload_mapping": [
    {"source_path": "action", "target_variable": "pr_action", "required": true},
    {"source_path": "pull_request.html_url", "target_variable": "pr_url", "required": true},
    {"source_path": "pull_request.diff_url", "target_variable": "diff_url", "required": true}
  ],
  "rate_limit": {"max_requests_per_minute": 30, "burst": 5}
}
```

### 10.2 Stripe 결제 완료 Webhook

```json
{
  "type": "webhook",
  "auth_mode": "hmac_sha256",
  "payload_mapping": [
    {"source_path": "data.object.id", "target_variable": "payment_id", "required": true},
    {"source_path": "data.object.amount", "target_variable": "amount", "required": true},
    {"source_path": "data.object.customer", "target_variable": "customer_id", "required": true}
  ],
  "ip_whitelist": ["3.18.12.63/32", "3.130.192.231/32"]
}
```

---

## 11. 교차참조

| 참조 대상 | 관계 |
|----------|------|
| `event_trigger.md` | Event 타입 트리거의 webhook event_source와 구분: Webhook 타입은 직접 HTTP 수신 → "internal" 채널 발행 |
| `variable_secret_management.md` | HMAC 시크릿·API Key 저장 (AES-256-GCM, LOCK-WF-10) |
| `execution_engine.md` | 트리거 발화 → 워크플로우 실행 큐 등록 |
| 부록 §B.4 | Webhook 트리거 설정 정본 |

---

## 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|----------|
| 2026-04-09 | v1.0 | L3 초판 작성 (N-003d EXTEND, HMAC/API Key 인증, 페이로드 매핑, Token Bucket Rate Limit) |
