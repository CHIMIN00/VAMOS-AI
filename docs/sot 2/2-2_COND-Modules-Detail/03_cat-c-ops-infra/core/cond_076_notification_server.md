# COND-076: 알림 서버 — L3 상세 명세

> **모듈 ID**: COND-076
> **카테고리**: CAT-C (Ops/Infra) — Core
> **우선순위**: MEDIUM
> **Phase**: Phase 1
> **L3 수준**: L3
> **LOCK 준수**: LOCK-CD-03/04/05/06/08/10
> **인프라 패턴**: Multi-channel Fan-out, Template Engine, **Outbox Pattern**, **Circuit Breaker per provider**, Subscription Index

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

class Notification(BaseModel):
    channel: Literal["push", "email", "sms", "slack", "in_app", "webhook"]
    recipient: str
    template: str = Field(..., description="템플릿 ID")
    data: dict[str, Any] = Field(default_factory=dict)
    locale: str = "ko-KR"
    priority: Literal["critical", "high", "normal", "low"] = "normal"
    schedule_at: Optional[str] = None
    deduplication_key: Optional[str] = None

class Subscription(BaseModel):
    user_id: str
    topic: str
    channels: list[Literal["push", "email", "sms", "slack", "in_app", "webhook"]]
    enabled: bool = True

class NotificationRequest(BaseModel):
    """COND-076 입력 스키마"""
    operation: Literal["send", "schedule", "cancel", "subscribe", "unsubscribe", "status"] = "send"
    notification: Optional[Notification] = None
    notification_id: Optional[str] = None
    subscription: Optional[Subscription] = None

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "send",
                "notification": {"channel": "slack", "recipient": "#alerts",
                                 "template": "deploy_done",
                                 "data": {"version": "v9.0.1"},
                                 "priority": "high"}
            }
        }
```

---

## E2. Output Schema

```python
class DeliveryAttempt(BaseModel):
    attempt_no: int
    provider: str
    status: Literal["queued", "sent", "delivered", "failed", "bounced"]
    timestamp: str
    error: Optional[str] = None

class DeliveryStatus(BaseModel):
    notification_id: str
    state: Literal["queued", "scheduled", "sending", "delivered", "failed", "canceled"]
    channel: str
    recipient: str
    attempts: list[DeliveryAttempt]

class NotificationResponse(BaseModel):
    """COND-076 출력 스키마"""
    operation: str
    notification_id: Optional[str] = None
    delivery_status: Optional[DeliveryStatus] = None
    subscription: Optional[Subscription] = None
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "send",
                "notification_id": "ntf-7a",
                "delivery_status": {"notification_id": "ntf-7a", "state": "queued",
                                    "channel": "slack", "recipient": "#alerts", "attempts": []},
                "execution_time_ms": 7
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request) -> Result[NotificationResponse, VamosError]:
    SWITCH request.operation:
      CASE "send" | "schedule":
          n = request.notification
          IF NOT template_store.has(n.template, n.locale):
              RETURN Err(VamosError("COND_076_TEMPLATE_NOT_FOUND", ...))
          # Dedup
          IF n.deduplication_key AND outbox.has(n.deduplication_key, ttl=config.dedup_ttl):
              RETURN Ok(... existing notification_id ...)

          rendered = template_engine.render(n.template, n.locale, n.data)
          notification_id = uuid7()
          outbox.append(notification_id, channel=n.channel, payload=rendered,
                        recipient=n.recipient, priority=n.priority,
                        schedule_at=n.schedule_at)   # Outbox Pattern → DB tx와 함께 커밋

          IF request.operation == "send" AND n.schedule_at IS NULL:
              dispatcher.enqueue(notification_id)   # 비동기 전송
          status = DeliveryStatus(notification_id, state="queued" IF request.operation == "send" ELSE "scheduled", ...)
          RETURN Ok(NotificationResponse(operation=..., notification_id=notification_id,
                                         delivery_status=status))

      CASE "cancel":
          status = outbox.find(request.notification_id)
          IF status IS NULL:
              RETURN Err(VamosError("COND_076_NOTIFICATION_NOT_FOUND", ...))
          IF status.state IN ("delivered", "failed"):
              RETURN Err(VamosError("COND_076_NOT_CANCELABLE", ...))
          outbox.cancel(request.notification_id)
          RETURN Ok(...)

      CASE "subscribe":
          subscription_store.upsert(request.subscription)
          RETURN Ok(...)
      CASE "unsubscribe":
          subscription_store.delete(request.subscription.subscription_id)
          RETURN Ok(...)

      CASE "status":
          status = delivery_store.get(request.notification_id)
          RETURN Ok(NotificationResponse(operation="status", delivery_status=status))


# Dispatcher (별도 컴포넌트)
FUNCTION dispatcher_loop():
    FOR notification IN outbox.poll():
        provider = provider_router.select(notification.channel)
        breaker = breaker_store.get(provider.name)
        IF breaker.is_open():
            outbox.requeue(notification, delay=breaker.cool_down)
            CONTINUE
        result = provider.send(notification)
        IF result.ok:
            delivery_store.append_attempt(notification.id, "delivered")
        ELSE:
            breaker.record_failure()
            IF notification.attempt < config.max_retries:
                outbox.requeue(notification, delay=exp_backoff(notification.attempt))
            ELSE:
                delivery_store.update(notification.id, state="failed")
                dlq.push(notification.id)
```

---

## E4. Error Handling

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|-------------|--------------|
| `COND_076_TEMPLATE_NOT_FOUND` | template+locale 미존재 | `FB_COND_076_DEFAULT_TEMPLATE` | "기본 템플릿으로 발송합니다." |
| `COND_076_NOTIFICATION_NOT_FOUND` | id 미존재 | `FB_COND_REJECT` | "알림을 찾을 수 없습니다." |
| `COND_076_NOT_CANCELABLE` | 종료 상태 취소 시도 | `FB_COND_REJECT` | "이미 종료된 알림입니다." |
| `COND_076_PROVIDER_UNAVAILABLE` | 외부 채널 장애 | `FB_COND_076_FALLBACK_CHANNEL` | "보조 채널로 전송합니다." |
| `COND_076_RATE_LIMITED` | 사용자/채널 한도 초과 | `FB_COND_076_DEFER` | "발송 빈도 한도를 초과했습니다." |
| `COND_076_RECIPIENT_OPTED_OUT` | 사용자 구독 해제 상태 | `FB_COND_076_DROP` | "사용자가 구독 해제 상태입니다." |
| `COND_076_OUTBOX_DOWN` | outbox DB 장애 | `FB_COND_SKIP` | "발송 저장소 일시 장애." |
| `COND_076_EXECUTE_TIMEOUT` | timeout_ms 초과 | `FB_COND_SKIP` | "처리 시간 초과." |

```python
return Err(VamosError(
    failure_code="COND_076_TEMPLATE_NOT_FOUND",
    message=f"template '{template}' for locale '{locale}' not found",
    fallback_id="FB_COND_076_DEFAULT_TEMPLATE",
    trace_id=ctx.trace_id,
))
```

---

## E5. Dependency Map

| 관계 | 항목 |
|------|------|
| 소비 | — |
| 제공 | 모든 CAT (사용자/시스템 알림) |

| I-Module | 용도 |
|----------|------|
| I-1, I-5, I-6, I-9 | 공통 |

| 인프라 / 라이브러리 | 사양 |
|----------------------|------|
| PostgreSQL | outbox, delivery_store, subscription_store |
| Redis | rate limit, breaker state |
| FCM / APNs | 푸시 |
| SendGrid / SES | 이메일 |
| Twilio | SMS |
| Slack Webhook | 메신저 |
| `jinja2` / Mustache | 템플릿 엔진 |

---

## E6. Performance Benchmark (I-04)

| 메트릭 | SLA 목표 | 임계값 | 측정 |
|--------|---------|--------|------|
| **send p99 (큐 등록)** | ≤ 20 ms | > 80 ms | histogram |
| **delivery latency p95 (push)** | ≤ 2 s | > 10 s | histogram |
| **delivery latency p95 (email)** | ≤ 30 s | > 120 s | histogram |
| **deliverability** | ≥ 99 % | < 95 % | counter |
| **provider 장애 자동 우회** | < 5 s | > 30 s | breaker timer |
| **가용성** | 99.9 % | < 99.5 % | uptime |

---

## E7. Integration Test Spec

```yaml
- name: "ntf_send_slack"
  setup: [register_template("deploy_done", "ko-KR"), stub_provider("slack")]
  input: { operation: "send", notification: {channel: "slack", recipient: "#x",
            template: "deploy_done", data: {version: "v1"}} }
  expected: [delivery_status.state == "queued", notification_id != ""]

- name: "ntf_dedup"
  setup: [send({deduplication_key: "k1"}) -> id1]
  input: { operation: "send", notification: {deduplication_key: "k1", ...} }
  expected: [notification_id == id1]

- name: "ntf_provider_breaker_opens"
  setup: [stub_provider("email", fail_count: 10)]
  input: { operation: "send", notification: {channel: "email", ...} }
  expected: [eventually(breaker_state("sendgrid") == "open")]
```

---

## E8. Blue Node Integration

| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | 모든 Node (이벤트→사용자 알림) |
| **Permission Level** | P0 |
| **게이트 요구** | policy (스팸/구독 정책) |
| **호출 패턴** | 도메인 이벤트가 OpsInfraMixin.notify() |

| 이벤트 | event_type |
|--------|------------|
| 초기화 | `cond.c.076.initialized` |
| 실행 시작/완료/실패 | `cond.c.076.execute_start` / `execute_done` / `execute_fail` |
| 헬스체크 | `cond.c.076.health` |
| 종료 | `cond.c.076.shutdown` |

Decision: `optional_signals ← {cond_module_id: "COND-076", op, channel, notification_id, dedup_hit}`

---

## E9. BaseModule ABC 적합성

```python
class Cond076Notification(BaseModule):
    async def initialize(self) -> Result[None, VamosError]:
        self._outbox = await OutboxStore.connect(self.config.outbox_dsn)
        self._delivery = await DeliveryStore.connect(self.config.delivery_dsn)
        self._templates = await TemplateStore.connect(self.config.templates_dsn)
        self._providers = ProviderRegistry.from_config(self.config)
        self._emit_event("cond.c.076.initialized")
        return Ok(None)

    async def execute(self, request: NotificationRequest) -> Result[NotificationResponse, VamosError]:
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        return Ok(HealthStatus(
            healthy=await self._outbox.ping() and await self._delivery.ping(),
            latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        await self._templates.close(); await self._delivery.close(); await self._outbox.close()
        self._emit_event("cond.c.076.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(id="COND-076", version="1.0.0",
                              capabilities=["send", "schedule", "cancel", "subscribe", "status"])
```

---

## E10. Configuration

```python
class Cond076Config(ModuleConfig):
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 500
    timeout_ms: int = 3000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=5, backoff_ms=500)

    outbox_dsn: str
    delivery_dsn: str
    templates_dsn: str
    providers: dict[str, dict] = {
        "slack": {"webhook_secret": "secret://slack"},
        "email": {"provider": "sendgrid", "api_key_secret": "secret://sendgrid"},
        "sms":   {"provider": "twilio", "api_key_secret": "secret://twilio"},
        "push":  {"provider": "fcm", "api_key_secret": "secret://fcm"},
    }
    dedup_ttl_seconds: int = 3600
    user_rate_limit_per_min: int = 30
    enable_outbox_pattern: bool = True
    breaker_open_threshold: float = 0.5
```
