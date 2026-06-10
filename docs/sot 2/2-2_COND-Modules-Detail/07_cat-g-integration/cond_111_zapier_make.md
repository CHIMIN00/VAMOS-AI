# COND-111 Zapier/Make 호환 (Zapier/Make Compatibility)

> **Status**: V2-Phase 2
> **모듈 ID**: COND-111
> **카테고리**: CAT-G Integration
> **우선순위**: LOW
> **버전**: V2 (Phase 2, 2026-04-19)
> **작성 단계**: STAGE 7 / Phase 7-II / 2-2 STEP_B / 세션 2-3
> **Phase 1 대응**: 종합명세 §#111 + `07_cat-g-integration/_index.md`
> **LOCK 준수**: LOCK-CD-01 / LOCK-CD-03 / LOCK-CD-04 / LOCK-CD-05 / LOCK-CD-06 / LOCK-CD-07 / LOCK-CD-08 / LOCK-CD-10 (+ LOCK-CD-11 §7.2 참조)

---

## §0 교차 참조 블록 (정본)

- **종합계획서**: `COND_MODULES_DETAIL_구조화_종합계획서.md` §7.4 L895~L945 / §13.1
- **종합명세**: `COND_MODULES_종합명세.md` §#111 (I/O 정의 L1413~L1423, 이름 verbatim "Zapier/Make 호환")
- **AUTHORITY_CHAIN**: `AUTHORITY_CHAIN.md` §4 LOCK-CD-01~11
- **Blue Node 정본**: `D2.0-03 §5` (Integration Node P1)
- **ErrorHandlingStandard 정본**: `D2.0-02 §0.3`
- **Runnable Protocol 정본**: `D2.0-02 §1.2-A`
- **교차 도메인**: `6-2 Security-Governance` (OAuth + HMAC webhook + CSRF) / `6-12 Event-Logging` (COND_111_*) / `3-4 Workflow-RPA` (자동화 워크플로우 연동, _index.md L45 verbatim)

---

## §1 개요

### 1.1 목적
VAMOS 를 Zapier / Make (Integromat) 의 앱으로 노출한다. Trigger (VAMOS 이벤트 발생 → Zapier Zap 실행) / Action (Zapier → VAMOS 명령 실행) / Search (Zapier → VAMOS 조회) 3 연동 타입을 지원한다. OAuth 2.0 AC + PKCE 로 Zapier 사용자가 VAMOS 계정 연결, Webhook (Zapier Platform) 으로 실시간 Zap trigger.

### 1.2 핵심 기술
- **Zapier Platform API**: Trigger / Action / Search definitions, Polling vs Webhook subscription
- **Make (Integromat) Webhook**: Standard webhook endpoint (Zapier 과 호환 스키마)
- **REST Trigger/Action Spec**: OpenAPI 3.0 스펙으로 Zapier CLI 자동 매핑
- **OAuth2 AC + PKCE (S256)**: Zapier app 사용자 계정 연결
- **Webhook HMAC-SHA256 + Idempotency-Key**: Zapier → VAMOS 콜백 인증

### 1.3 Privacy / Security Policy 요약 (§7.4 L942 — 6-2 Security 대조)
- **수집 필드**: Zapier OAuth refresh_token (KMS), zap_id, trigger_subscriptions, action audit log
- **처리 목적**: Zapier Zap 연동. 제3자 데이터 공유는 Zap user 가 명시적으로 지정한 대상만
- **보존 기간**: OAuth token store **30일** / zap subscription metadata **90일** / action audit log **30일**
- **삭제 정책**: GDPR Right to Erasure — 72h 내 OAuth refresh_token + subscription 폐기
- **암호화**: Credentials AES-256-GCM + KMS, in-transit TLS 1.3
- **CSRF**: OAuth `state` 파라미터 CSPRNG 32 bytes + 10분 TTL

### 1.4 LOCK 준수 요약
| LOCK | 준수 내용 |
|---|---|
| LOCK-CD-01 | COND-111 체계 준수 |
| LOCK-CD-03 | BaseModule ABC 4 메서드 구현 |
| LOCK-CD-04 | Runnable 프로토콜 |
| LOCK-CD-05 | Result<T, VamosError> 반환 |
| LOCK-CD-06 | VamosError 4필드 |
| LOCK-CD-07 | OAuth 조건 평가 policy_gate > cost_gate > evidence_gate (VAMOS-as-app 측) |
| LOCK-CD-08 | Integration Node **P1 (승인 후 활성)** |
| LOCK-CD-10 | ModuleConfig 5필드 |

---

## §2 Input Schema (Pydantic v2) — §13.1 #1

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Any
from datetime import datetime

class ZapierSubscription(BaseModel):
    """Zapier Zap 구독 정보 (Trigger 타입 전용)."""
    zap_id: str = Field(..., min_length=4, max_length=64)
    user_account_hashed: str = Field(..., min_length=16, max_length=128)
    event_name: str = Field(..., description="VAMOS trigger event key (예: 'note_created')")
    target_webhook_url: str = Field(..., description="Zapier webhook endpoint")
    subscription_expires_at: Optional[datetime] = Field(default=None)

class WebhookPayload(BaseModel):
    """Zapier → VAMOS 콜백 payload (Action/Search 타입)."""
    zap_id: str
    event_type: str
    data: dict[str, Any] = Field(default_factory=dict)
    idempotency_key: str = Field(..., max_length=128,
        description="Zapier Zap execution ID 또는 CSPRNG nonce")
    timestamp: datetime
    signature: str = Field(..., description="HMAC-SHA256 헤더 X-Zapier-Signature")

class ActionParams(BaseModel):
    """Zapier → VAMOS Action 실행 인자."""
    action_name: str = Field(..., min_length=3, max_length=64)
    params: dict[str, Any] = Field(default_factory=dict)
    dry_run: bool = Field(default=False, description="검증만 수행 (fail-safe)")

class ZapierInput(BaseModel):
    """COND-111 실행 입력. 종합명세 §#111 verbatim I/O 준수."""
    user_id_hashed: str = Field(..., min_length=16, max_length=128)
    integration_type: Literal["trigger", "action", "search"]
    webhook_payload: Optional[WebhookPayload] = Field(default=None,
        description="action/search 에서 필수, trigger 구독 등록 시 None")
    action_params: Optional[ActionParams] = Field(default=None,
        description="integration_type=action 시 필수")
    subscription: Optional[ZapierSubscription] = Field(default=None,
        description="integration_type=trigger 시 필수")
    consent_flags: dict[
        Literal["oauth_zapier", "event_emission", "zapier_action_exec"], bool
    ] = Field(default_factory=dict)
    trace_id: Optional[str] = Field(default=None)

    @field_validator("webhook_payload", "action_params", "subscription")
    @classmethod
    def type_consistency(cls, v, info):
        t = info.data.get("integration_type")
        name = info.field_name
        if t == "trigger" and name == "subscription" and v is None:
            raise ValueError("trigger requires subscription")
        if t in ("action", "search") and name == "webhook_payload" and v is None:
            raise ValueError("action/search requires webhook_payload")
        if t == "action" and name == "action_params" and v is None:
            raise ValueError("action requires action_params")
        return v
```

### 2.1 예시
```json
{
  "user_id_hashed": "SHA256:zap-u-001",
  "integration_type": "action",
  "webhook_payload": {
    "zap_id": "zap-123abc", "event_type": "vamos.note.create",
    "data": {"title": "From Gmail", "body": "..."},
    "idempotency_key": "zap-exec-xxx-001",
    "timestamp": "2026-04-19T12:00:00Z",
    "signature": "sha256=a1b2c3..."
  },
  "action_params": {"action_name": "create_note", "params": {"folder": "/inbox"},
                    "dry_run": false},
  "consent_flags": {"oauth_zapier": true, "zapier_action_exec": true},
  "trace_id": "trace-zap-001"
}
```

---

## §3 Output Schema (Pydantic v2) — §13.1 #2

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from datetime import datetime

class WebhookResponse(BaseModel):
    """Zapier 에 반환하는 webhook 응답."""
    http_status: int = Field(..., ge=200, le=599)
    event_ack: str
    body: dict[str, Any] = Field(default_factory=dict)

class ActionResult(BaseModel):
    action_name: str
    succeeded: bool
    result_data: dict[str, Any] = Field(default_factory=dict)
    idempotency_replay_skipped: bool = Field(default=False,
        description="True 면 이미 실행된 idempotency_key — 재시도 안전")

class TriggerData(BaseModel):
    """Trigger 타입: VAMOS 이벤트 → Zapier 전달용 ndjson 리스트."""
    event_name: str
    events: list[dict[str, Any]] = Field(..., max_length=100,
        description="이벤트 폴링/푸시 배치")
    next_cursor: Optional[str] = Field(default=None)

class ZapierOutput(BaseModel):
    integration_type: Literal["trigger", "action", "search"]
    action_result: Optional[ActionResult] = Field(default=None)
    trigger_data: Optional[TriggerData] = Field(default=None)
    webhook_response: Optional[WebhookResponse] = Field(default=None)
    retention_expires_at: datetime
    medical_disclaimer_shown: bool = Field(default=False)
```

### 3.1 예시
```json
{
  "integration_type": "action",
  "action_result": {"action_name": "create_note", "succeeded": true,
                     "result_data": {"note_id": "n-001"},
                     "idempotency_replay_skipped": false},
  "webhook_response": {"http_status": 200, "event_ack": "ack-xyz",
                        "body": {"note_id": "n-001"}},
  "retention_expires_at": "2026-07-18T00:00:00Z",
  "medical_disclaimer_shown": false
}
```

---

## §4 Algorithm Pseudocode — §13.1 #3

### 4.1 전체 흐름
```
ALGORITHM Zapier(input: ZapierInput) -> Result<ZapierOutput, VamosError>:
    # 1. LOCK-CD-07 policy_gate: OAuth scope
    IF NOT input.consent_flags.get("oauth_zapier", False):
        RETURN Err(VamosError("COND_111_OAUTH_CONSENT_MISSING", ...))

    # 2. Branch by integration_type
    IF input.integration_type == "trigger":
        RETURN handle_trigger(input.subscription, consent=input.consent_flags)
    ELIF input.integration_type == "action":
        RETURN handle_action(input.webhook_payload, input.action_params,
                              consent=input.consent_flags)
    ELSE:  # search
        RETURN handle_search(input.webhook_payload)


FUNCTION handle_action(wp: WebhookPayload, ap: ActionParams, consent) -> Result:
    # 2a. Webhook HMAC-SHA256 서명 검증
    expected = hmac_sha256(
        secret=ZAPIER_WEBHOOK_SECRET,
        message=f"{wp.timestamp.isoformat()}\n{wp.idempotency_key}\n{json.dumps(wp.data)}",
    )
    IF NOT constant_time_equal(expected, wp.signature.replace("sha256=", "")):
        RETURN Err("COND_111_WEBHOOK_SIGNATURE_INVALID")

    # 2b. Replay window
    IF abs(now() - wp.timestamp) > 300s:     # 5분
        RETURN Err("COND_111_WEBHOOK_REPLAY_STALE")

    # 2c. Idempotency check
    IF idempotency_registry.contains(wp.idempotency_key):
        prev = idempotency_registry.get(wp.idempotency_key)
        RETURN Ok(ZapierOutput(
            integration_type="action",
            action_result=ActionResult(action_name=ap.action_name, succeeded=True,
                                        result_data=prev.result_data,
                                        idempotency_replay_skipped=True),
            webhook_response=WebhookResponse(http_status=200,
                                              event_ack=prev.event_ack,
                                              body=prev.result_data),
        ))

    # 2d. LOCK-CD-07 cost_gate: action 실행 비용 (VAMOS 내부 호출)
    IF exceeds_action_budget(ap.action_name):
        RETURN Err("COND_111_RATE_LIMIT_EXCEEDED",
                    fallback_id="FB-coalesce-next-window")

    # 2e. LOCK-CD-07 evidence_gate: 사용자 action_exec 동의
    IF NOT consent.get("zapier_action_exec", False):
        RETURN Err("COND_111_ACTION_EXEC_CONSENT_MISSING")

    # 2f. Dry-run 단축
    IF ap.dry_run:
        RETURN Ok(build_dry_run_output(ap))

    # 2g. 실제 VAMOS internal action dispatch
    result = vamos_action_dispatcher.execute(
        action_name=ap.action_name, params=ap.params,
        trace_id=input.trace_id,
    )
    IF result.is_err():
        RETURN Err("COND_111_ACTION_EXEC_FAIL",
                    fallback_id="FB-dry-run-retry")

    # 2h. Idempotency 등재
    idempotency_registry.put(wp.idempotency_key, result, TTL=7d)

    # 2i. Response + audit log
    audit_log.append(user_id=user_id_hashed, zap_id=wp.zap_id, action=ap.action_name, ok=True)
    expires = now() + timedelta(days=30)
    RETURN Ok(ZapierOutput(
        integration_type="action",
        action_result=ActionResult(...),
        webhook_response=WebhookResponse(http_status=200, event_ack=uuid4(),
                                          body=result.result_data),
        retention_expires_at=expires,
    ))


FUNCTION handle_trigger(sub: ZapierSubscription, consent) -> Result:
    IF NOT consent.get("event_emission", False):
        RETURN Err("COND_111_EVENT_EMISSION_CONSENT_MISSING")

    events = vamos_event_bus.poll(
        event_name=sub.event_name,
        user=sub.user_account_hashed,
        since=sub.last_polled_at,
        max=100,
    )

    # 본 호출은 폴링 결과 반환 — Zapier 서버가 이 결과를 Zap 에 전달
    RETURN Ok(ZapierOutput(
        integration_type="trigger",
        trigger_data=TriggerData(event_name=sub.event_name,
                                  events=events, next_cursor=next_cursor(events)),
    ))
```

### 4.2 시간 복잡도
- **Webhook 서명 검증**: `O(|payload|)` — HMAC-SHA256 single pass
- **Idempotency lookup**: `O(1)` (Redis)
- **Action dispatch**: VAMOS 내부 호출 비용에 지배 (외부 네트워크 없음)
- **Trigger polling**: `O(|events|)` ≤ 100 events/poll
- **전체**: `O(|payload| + |events|)` — 외부 네트워크 없음 (단 response 반환 시 Zapier 클라이언트 I/O)
- **LOCK 값 참조**: LOCK-CD-11 V2 ₩93K — Zapier Platform free tier (100 tasks/월 무료), VAMOS 내부 action dispatch 공유 인프라, 월 ₩1K 이하

### 4.3 OAuth 2.0 AC + PKCE 플로우 (Zapier-as-client, VAMOS-as-auth-server)
```
STEP 1 (Zapier 사용자 Zap 설정 시, Zapier → VAMOS auth redirect):
  GET https://vamos.example/oauth/authorize
    ?client_id=ZAPIER_APP_CLIENT_ID
    &redirect_uri=https://zapier.com/auth/callback
    &response_type=code
    &state=<CSPRNG_32B>
    &code_challenge=<SHA256(verifier)_BASE64URL>
    &code_challenge_method=S256            # PKCE S256 필수
    &scope=trigger action search

STEP 2 (사용자 승인 후 VAMOS → Zapier 리다이렉트):
  /auth/callback?code=<AUTH_CODE>&state=<STATE>
  VAMOS 내부: validate state CSRF + 10분 TTL

STEP 3 (Zapier backend → VAMOS token exchange):
  POST https://vamos.example/oauth/token
  Authorization: Basic <BASE64(CLIENT_ID:CLIENT_SECRET)>
  Body: grant_type=authorization_code
        code=<AUTH_CODE>
        redirect_uri=<REDIRECT_URI>
        code_verifier=<PKCE_VERIFIER>
  → { access_token, refresh_token, expires_in, scope }

STEP 4 (Zapier → VAMOS refresh):
  POST /oauth/token
  Body: grant_type=refresh_token&refresh_token=<...>
  → refresh_token rotation (기존 30s grace)

STEP 5 (Revoke — Zap 삭제 시):
  POST /oauth/revoke { token, token_type_hint }
```

### 4.4 동기화 전략 매트릭스 (COND-111 행)
| 소스 | 타겟 | 방향 | Conflict Resolution | 증분 기준 |
|---|---|---|---|---|
| Zapier Triggers | VAMOS Actions | unidirectional (event-driven) | N/A (이벤트 기반 + Zap-id idempotency) | `idempotency_key` + timestamp |

### 4.5 Webhook HMAC-SHA256 서명 규약
```
헤더:
  X-Zapier-Signature: sha256=<HEX>
  X-Zapier-Timestamp: <ISO8601>
  X-Zapier-Idempotency-Key: <Zap execution ID>

signed_message = timestamp + "\n" + idempotency_key + "\n" + body
expected       = HMAC-SHA256(secret=ZAPIER_WEBHOOK_SECRET, message=signed_message)
validate:      constant_time_compare(expected, received_hex)
replay_window: 5분
```

---

## §5 Error Handling — §13.1 #4 (LOCK-CD-05 / LOCK-CD-06)

### 5.1 FailureCode 체계
```python
COND_111_OAUTH_CONSENT_MISSING
COND_111_OAUTH_SCOPE_INSUFFICIENT
COND_111_OAUTH_REFRESH_FAIL
COND_111_PKCE_VERIFIER_MISMATCH
COND_111_STATE_CSRF_MISMATCH
COND_111_WEBHOOK_SIGNATURE_INVALID
COND_111_WEBHOOK_REPLAY_STALE
COND_111_IDEMPOTENCY_KEY_REPLAY
COND_111_ACTION_EXEC_CONSENT_MISSING
COND_111_ACTION_NOT_FOUND
COND_111_ACTION_EXEC_FAIL
COND_111_RATE_LIMIT_EXCEEDED
COND_111_EVENT_EMISSION_CONSENT_MISSING
COND_111_TRIGGER_POLL_FAIL
COND_111_RETENTION_POLICY_VIOLATION
```

### 5.2 Phase별 복구 전략
```
Phase 1 (Validation/Pydantic): 자동 차단
Phase 2 (OAuth gate LOCK-CD-07 policy_gate): 재동의 + scope upgrade 안내
Phase 3 (OAuth gate LOCK-CD-07 cost_gate): action rate limit 도달 시 coalesce / Zap 실행 backoff
Phase 4 (OAuth gate LOCK-CD-07 evidence_gate): token 만료 → refresh / 실패 시 reauth 리다이렉트
Phase 5 (Webhook signature): 400 + replay 차단 (idempotency 등재 skip)
Phase 6 (Webhook replay stale): 400 + stale timestamp
Phase 7 (Idempotency replay): 200 ack (skip 실행, 이전 결과 반환)
Phase 8 (Action not found): 400 — Zap 정의 오류 힌트 (valid actions list)
Phase 9 (Action exec fail): retry 1회 (idempotency 전제), 2회 실패 시 `FB-dry-run-retry` fallback
Phase 10 (Trigger poll fail): event bus 장애 → cached last event list fallback (품질 저하 표기)
Phase 11 (Escalation): I-20 에스컬레이션 (tokens / raw payload 배제)
```

### 5.3 Escalation Payload
```python
class EscalationPayload(BaseModel):
    source_engine: str = "COND-111"
    error_code: str
    zap_id: str | None = None
    user_id_hashed: str
    integration_type: str              # trigger | action | search
    retry_count: int
    timestamp: datetime
    # OAuth tokens / webhook body / action params 원문 배제 (action_name 만 허용)
```

### 5.4 로깅 포맷 (R-01-7)
```json
{
  "trace_id": "trace-zap-...",
  "error": {"code": "COND_111_WEBHOOK_SIGNATURE_INVALID", "severity": "ERROR"},
  "context": {"zap_id": "zap-123abc", "module": "COND-111",
               "phase": "webhook_verify", "source_ip": "ip-hash"},
  "recovery": {"strategy": "reject_400_no_registry_put", "fallback_id": null,
                "security_alert": true}
}
```

---

## §6 Dependency Map — §13.1 #5

### 6.1 내부 의존 (CAT-G 내부)
| 대상 | 방향 | 이유 |
|---|---|---|
| COND-090 Notion/Obsidian 통합 | CONSUMES (event) | COND-090 동기화 성공 이벤트를 Zapier trigger 로 노출 |
| COND-112 JIRA/Linear | 선택적 CONSUMES | JIRA 이슈 이벤트를 Zap 으로 재노출 가능 |

### 6.2 외부 의존
| 대상 | 방향 | 이유 |
|---|---|---|
| Zapier Platform | CONSUMES+PRODUCES | Trigger/Action/Search API, VAMOS-as-app |
| Make (Integromat) | CONSUMES+PRODUCES | 동일 스키마 webhook compatibility |
| `6-2 Security-Governance` | CROSS-DOMAIN | OAuth 토큰 AES-256-GCM + KMS + CSRF state + PKCE S256 + HMAC verify |
| `6-12 Event-Logging` | CROSS-DOMAIN | COND_111_* FailureCode prefix (oauth / webhook / action 이벤트 별도 분류) |
| `3-4 Workflow-RPA` | CROSS-DOMAIN | 자동화 워크플로우 연동 (_index.md L45 verbatim) — Zapier Zap 이 VAMOS 를 Action 으로 호출하는 표준 경로 |
| `#3 Blue Node` | CROSS-DOMAIN | LOCK-CD-08 Integration Node P1 실행 종속 |

### 6.3 의존성 매트릭스 (CAT-G + 인접)
```
            090  110  111  112
COND-111  [  C    .    -    C  ]   C=CONSUMES(event), -=self
```

### 6.4 §A 매트릭스 cross-check
- **종합계획서 §A.2 P0-1**: CAT-G ↔ 3-4 Workflow-RPA 자동화 연동 (_index.md L45) — 본 모듈이 PROVIDES (VAMOS-as-Zapier-app 표준 경로)
- 별도 deferral 생성 없음

### 6.5 Phase 1 deferral 인계
- 본 모듈은 deferral 생성 없음

---

## §7 Performance Benchmark — §13.1 #6

### 7.1 SLA 기준값
| 지표 | V1 기준 | V2 목표 |
|---|---|---|
| Webhook 처리 지연 (서명+idempotency+dispatch) | N/A | ≤ 300 ms |
| Action dispatch 성공률 | N/A | ≥ 0.995 |
| Trigger poll 처리량 | N/A | ≥ 50 polls/s (100 events/poll) |
| OAuth 토큰 발급 지연 | N/A | ≤ 500 ms |
| HMAC 서명 검증 실패 감지율 | N/A | 100% (false negative 0) |

### 7.2 비용 상한 참조 (LOCK-CD-11)
- V2 ₩93K 한도 내 설계. Zapier Platform free tier (100 tasks/월 무료), VAMOS 내부 action dispatch 는 공유 인프라, 월 ₩1K 이하
- OAuth token AES-256-GCM KMS envelope 비용 ~₩0.3K/사용자/년

### 7.3 벤치마크 시나리오
```
BENCH-111-01: Action webhook 100건 burst → p50/p99 지연
BENCH-111-02: Idempotency replay 50% 주입 → skip 비율 + 지연
BENCH-111-03: Trigger polling 10분간 지속 → 이벤트 loss 0 확인
BENCH-111-04: OAuth refresh 만료 임박 주입 → rotation 성공률
BENCH-111-05: HMAC signature 위조 100건 주입 → 100% 차단 + audit log
```

---

## §8 Integration Test Spec (I-05) — §13.1 #7 (≥ 3 + ⚠️ OAuth/Webhook/동기화 필수)

### 8.1 I-05-COND111-01: 정상 Action webhook 실행
- **목적**: Zapier → VAMOS `create_note` action dispatch
- **주입**: `integration_type="action"`, valid HMAC signature, valid idempotency_key
- **기대**:
  - `Result.is_ok()`, `action_result.succeeded == True`
  - `webhook_response.http_status == 200`
  - `idempotency_replay_skipped == False`
- **목 데이터**: `mocks/COND-111/happy_path_action.json`

### 8.2 I-05-COND111-02: ⚠️ Webhook 서명 위조 감지 → 400 + audit
- **목적**: 잘못된 HMAC signature 주입
- **기대**:
  - `Result.is_err()`, `failure_code == "COND_111_WEBHOOK_SIGNATURE_INVALID"`
  - HTTP 400, idempotency registry **등재 안 됨**
  - security alert 이벤트 발행 (source_ip_hash + zap_id)
- **목 데이터**: `mocks/COND-111/webhook_forged_signature.json`

### 8.3 I-05-COND111-03: ⚠️ Idempotency replay → 200 ack skip
- **목적**: 동일 idempotency_key 2회 연속 주입
- **기대**:
  - 1회차: `succeeded == True`, 실제 action dispatch
  - 2회차: `succeeded == True`, `idempotency_replay_skipped == True`, 재실행 안 됨
  - `webhook_response.body` 동일 (prev result 반환)
- **목 데이터**: `mocks/COND-111/idempotency_replay.json`

### 8.4 I-05-COND111-04 (추가): ⚠️ OAuth 토큰 만료 → refresh
- **목적**: refresh_token 만료 주입
- **기대**: `failure_code == "COND_111_OAUTH_REFRESH_FAIL"`, `fallback_id == "FB-reauth-zapier"`
- **목 데이터**: `mocks/COND-111/oauth_expired.json`

### 8.5 Phase 3 시나리오 확장 (≥ 5 시나리오)
| ID | 제목 | 주입 | 기대 |
|---|---|---|---|
| 111-S5 | Replay window stale | timestamp 10분 전 | `COND_111_WEBHOOK_REPLAY_STALE` 400 |
| 111-S6 | Action not found | `action_name="nonexistent"` | `COND_111_ACTION_NOT_FOUND` 400 + valid list hint |
| 111-S7 | Dry-run 실행 | `dry_run=True` | action dispatch 안 함, 검증만 OK 반환 |
| 111-S8 | Trigger polling 성공 | 50 events | `trigger_data.events.length == 50`, next_cursor |
| 111-S9 | PKCE verifier mismatch | 변조된 verifier | `COND_111_PKCE_VERIFIER_MISMATCH` 400 |
| 111-S10 | CSRF state mismatch | state 변조 | `COND_111_STATE_CSRF_MISMATCH` 400 |
| 111-S11 | Rate limit 도달 | 초당 100 action | `COND_111_RATE_LIMIT_EXCEEDED` + backoff |
| 111-S12 | Right to Erasure | delete_user | 72h 내 OAuth refresh_token + subscription 폐기 |
| 111-S13 | Trace 전파 | `trace_id="T-zap"` | 일치 |

---

## §9 Blue Node Integration (LOCK-CD-04 / LOCK-CD-08) — §13.1 #8

### 9.1 Blue Node 소비 계약
- **Integration Node** / **P1 (승인 후 활성)** / 독립 실행 금지

### 9.2 Runnable 프로토콜
```python
class ZapierMake(BaseModule, Runnable):
    def initialize(self, config: ModuleConfig) -> None: ...
    def execute(self, input: ZapierInput) -> Result[ZapierOutput, VamosError]: ...
    def run(self, input: ZapierInput) -> Result[ZapierOutput, VamosError]: ...
    def health_check(self) -> HealthStatus: ...   # Zapier ping + VAMOS event bus
    def get_metadata(self) -> ModuleMetadata: ...
    def shutdown(self) -> None: ...
```

### 9.3 ModuleConfig (LOCK-CD-10)
```python
config = ModuleConfig(
    enabled=True,
    priority=3,                      # LOW
    max_concurrent=10,
    timeout_ms=2000,
    retry_policy=RetryPolicy(max_retries=1, backoff="linear",
                              retry_on=["COND_111_ACTION_EXEC_FAIL"]),
)
```

### 9.4 Permission Level (LOCK-CD-08)
```
P1: Integration Node 승인 후 활성 (OAuth + action_exec 동의 전제)
P0: 관리자 (Zapier app CLIENT_SECRET rotation)
```

### 9.5 Blue Node Event (6-12)
```
COND_111_WEBHOOK_RECEIVED           INFO    zap_id, idempotency_key, signature_ok
COND_111_WEBHOOK_SIGNATURE_INVALID  ERROR   zap_id, source_ip_hash (security alert)
COND_111_WEBHOOK_REPLAY_STALE       WARN    zap_id, ts_delta_s
COND_111_ACTION_EXECUTED            INFO    zap_id, action_name, succeeded
COND_111_ACTION_REPLAY_SKIPPED      INFO    idempotency_key, original_ts
COND_111_TRIGGER_EMITTED            INFO    event_name, events_count, user_id_hashed
COND_111_OAUTH_REFRESH_SUCCEEDED    INFO    zap_id, new_expires_at
COND_111_RATE_LIMIT_EXCEEDED        WARN    zap_id, next_window_ms
```

---

## §10 V2-Phase 2 변경 이력

| 버전 | 일자 | 변경 요약 | 근거 |
|---|---|---|---|
| V1 | 2026-03-22 | 초기 골격 (SHELL L1, 이름 "Zapier/Make 호환" verbatim) | Phase 1 산출 이전 |
| V2 | 2026-04-19 | L3 상세 + OAuth 2.0 AC+PKCE(S256) + Webhook HMAC-SHA256 + Idempotency-Key + Trigger/Action/Search 3 타입 + Zap-id idempotency + 3-4 Workflow-RPA 연동 | STAGE 7 Phase 7-II 2-2 STEP_B 세션 2-3 |

### 10.1 Pydantic 재사용 출처
- `ModuleConfig` 재사용: `common_types.md §3.4` (LOCK-CD-10 정본)
- `VamosError` 재사용: `D2.0-02 §0.3` (LOCK-CD-06 정본)
- `Result[T, E]` 재사용: `D2.0-02 §0.3` (LOCK-CD-05 정본)

---
