# COND-112 JIRA/Linear 통합 (Bidirectional Project Management Integration)

> **Status**: V2-Phase 2
> **모듈 ID**: COND-112
> **카테고리**: CAT-G Integration
> **우선순위**: MEDIUM
> **버전**: V2 (Phase 2, 2026-04-19)
> **작성 단계**: STAGE 7 / Phase 7-II / 2-2 STEP_B / 세션 2-3
> **Phase 1 대응**: 종합명세 §#112 + `07_cat-g-integration/_index.md`
> **LOCK 준수**: LOCK-CD-01 / LOCK-CD-03 / LOCK-CD-04 / LOCK-CD-05 / LOCK-CD-06 / LOCK-CD-07 / LOCK-CD-08 / LOCK-CD-10 (+ LOCK-CD-11 §7.2 참조)

---

## §0 교차 참조 블록 (정본)

- **종합계획서**: `COND_MODULES_DETAIL_구조화_종합계획서.md` §7.4 L895~L945 / §13.1
- **종합명세**: `COND_MODULES_종합명세.md` §#112 (I/O 정의 L1425~L1435)
- **AUTHORITY_CHAIN**: `AUTHORITY_CHAIN.md` §4 LOCK-CD-01~11
- **CONFLICT_LOG**: `CONFLICT_LOG.md` CF-2026-04-07 (CAT-C COND-079→COND-033 Saga 재사용 deferral) — 본 모듈 §5/§6 에서 **옵션 (b) Phase 3 이월 placeholder** 채택 (상세 §6.4)
- **Blue Node 정본**: `D2.0-03 §5` (Integration Node P1)
- **ErrorHandlingStandard 정본**: `D2.0-02 §0.3`
- **Runnable Protocol 정본**: `D2.0-02 §1.2-A`
- **교차 도메인**: `6-2 Security-Governance` (OAuth + HMAC webhook) / `6-12 Event-Logging` (COND_112_*) / `3-10 Agent-Protocol-Interoperability` (프로젝트 관리 연동, _index.md L46 verbatim)

---

## §1 개요

### 1.1 목적
JIRA / Linear 프로젝트 관리 도구와 양방향 연동을 제공한다. VAMOS 내부 task → JIRA/Linear 이슈 자동 생성/업데이트, JIRA/Linear 상태 변경 → VAMOS task 동기화, 스프린트 메트릭 조회. 동일 `issue_id` 가 양쪽에서 수정된 경우 field-level last-writer-wins + optimistic lock 으로 해소.

### 1.2 핵심 기술
- **JIRA REST API v3**: Issues / Projects / Sprints / Fields
- **Linear GraphQL API**: Issue / Project / Cycle queries + mutations
- **Webhook 양방향**: JIRA Webhook (payload 스키마 고정) + Linear Webhook (GraphQL subscription 또는 REST callback)
- **Status Mapping**: VAMOS status ↔ JIRA workflow ↔ Linear state 3-way 매핑 테이블
- **OAuth 2.0 AC + PKCE (S256)**: Atlassian OAuth (JIRA) + Linear OAuth
- **HMAC-SHA256 서명 검증**: JIRA Webhook + Linear Webhook
- **Field-level LWW + Optimistic Lock**: 양방향 merge 충돌 해소

### 1.3 Privacy / Security Policy 요약 (§7.4 L942 — 6-2 Security 대조)
- **수집 필드**: JIRA/Linear OAuth refresh_token (KMS), workspace_id, issue_id 매핑 테이블, sync history (field diff), webhook event log
- **처리 목적**: 프로젝트 관리 도구 양방향 동기화. 제3자 배포 금지
- **보존 기간**: OAuth token store **30일** / issue_id 매핑 **90일** / sync history **90일** / webhook event log **30일**
- **삭제 정책**: GDPR Right to Erasure — 72h 내 OAuth refresh_token + Atlassian/Linear revocation + sync history 삭제
- **암호화**: Credentials AES-256-GCM + KMS, in-transit TLS 1.3
- **CSRF**: OAuth `state` CSPRNG 32 bytes + 10분 TTL

### 1.4 LOCK 준수 요약
| LOCK | 준수 내용 |
|---|---|
| LOCK-CD-01 | COND-112 체계 준수 |
| LOCK-CD-03 | BaseModule ABC 4 메서드 구현 |
| LOCK-CD-04 | Runnable 프로토콜 |
| LOCK-CD-05 | Result<T, VamosError> 반환 |
| LOCK-CD-06 | VamosError 4필드 |
| LOCK-CD-07 | 조건 평가 policy_gate > cost_gate > evidence_gate (OAuth 스코프 / rate limit / token 유효성) |
| LOCK-CD-08 | Integration Node **P1 (승인 후 활성)** |
| LOCK-CD-10 | ModuleConfig 5필드 |

---

## §2 Input Schema (Pydantic v2) — §13.1 #1

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal, Optional, Any
from datetime import datetime

class IssueData(BaseModel):
    """JIRA/Linear 이슈 데이터 (공통 canonical 모델)."""
    external_id: Optional[str] = Field(default=None,
        description="JIRA key (PROJ-123) 또는 Linear ID (uuid)")
    title: str = Field(..., min_length=1, max_length=256)
    description: str = Field(default="", max_length=32768)
    status: str = Field(..., description="canonical status (VAMOS side 매핑)")
    assignee_hashed: Optional[str] = Field(default=None, max_length=128)
    labels: list[str] = Field(default_factory=list, max_length=32)
    project_key: str = Field(..., min_length=2, max_length=64)
    priority: Literal["low", "medium", "high", "urgent"] = Field(default="medium")
    estimate_points: Optional[int] = Field(default=None, ge=0, le=100)
    expected_version: Optional[int] = Field(default=None,
        description="optimistic lock 용 (기존 값 기준). update_status / sync 에서 필수")

class ProjectQuery(BaseModel):
    project_key: str = Field(..., min_length=2, max_length=64)
    jql: Optional[str] = Field(default=None, max_length=1024)
    graphql_filter: Optional[dict[str, Any]] = Field(default=None)
    max_results: int = Field(default=50, ge=1, le=200)

class JiraLinearInput(BaseModel):
    """COND-112 실행 입력. 종합명세 §#112 verbatim I/O 준수."""
    user_id_hashed: str = Field(..., min_length=16, max_length=128)
    operation: Literal["create_issue", "update_status", "sync", "query"]
    target_service: Literal["jira", "linear"]
    issue_data: Optional[IssueData] = Field(default=None,
        description="create_issue / update_status 에서 필수")
    query: Optional[ProjectQuery] = Field(default=None,
        description="query 에서 필수")
    sync_scope: Optional[dict[Literal["project_key", "since"], Any]] = Field(default=None,
        description="sync 에서 필수")
    oauth_creds_ref: str = Field(..., description="KMS-enveloped refresh_token ref")
    consent_flags: dict[
        Literal["oauth_target", "bidirectional_write", "webhook_subscribe"], bool
    ] = Field(default_factory=dict)
    trace_id: Optional[str] = Field(default=None)

    @field_validator("issue_data", "query", "sync_scope")
    @classmethod
    def operation_consistency(cls, v, info):
        op = info.data.get("operation")
        name = info.field_name
        if op in ("create_issue", "update_status") and name == "issue_data" and v is None:
            raise ValueError(f"{op} requires issue_data")
        if op == "query" and name == "query" and v is None:
            raise ValueError("query op requires query")
        if op == "sync" and name == "sync_scope" and v is None:
            raise ValueError("sync requires sync_scope")
        return v
```

### 2.1 예시
```json
{
  "user_id_hashed": "SHA256:jl-u-001",
  "operation": "sync",
  "target_service": "jira",
  "sync_scope": {"project_key": "VAMOS", "since": "2026-04-18T00:00:00Z"},
  "oauth_creds_ref": "kms:oauth/jira/ws-abc",
  "consent_flags": {"oauth_target": true, "bidirectional_write": true, "webhook_subscribe": true},
  "trace_id": "trace-jl-001"
}
```

---

## §3 Output Schema (Pydantic v2) — §13.1 #2

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any
from datetime import datetime

class IssueResult(BaseModel):
    external_id: str
    vamos_task_id: Optional[str] = Field(default=None)
    status: str
    version: int = Field(..., ge=0, description="optimistic lock 용")
    url: str
    created_or_updated: Literal["created", "updated"]

class SyncStatus(BaseModel):
    project_key: str
    synced_count: int = Field(..., ge=0)
    conflicts_resolved: int = Field(..., ge=0)
    conflicts_pending_manual: int = Field(..., ge=0)
    errors_count: int = Field(..., ge=0)
    field_lww_applied_count: int = Field(..., ge=0,
        description="field-level last-writer-wins 적용된 이슈 수")
    next_sync_token: Optional[str] = Field(default=None)

class ProjectMetrics(BaseModel):
    project_key: str
    total_issues: int = Field(..., ge=0)
    active_sprint_velocity_points: float = Field(..., ge=0.0)
    blocked_count: int = Field(..., ge=0)
    avg_cycle_time_hours: float = Field(..., ge=0.0)

class JiraLinearOutput(BaseModel):
    operation: Literal["create_issue", "update_status", "sync", "query"]
    issue_result: Optional[IssueResult] = Field(default=None)
    sync_status: Optional[SyncStatus] = Field(default=None)
    project_metrics: Optional[ProjectMetrics] = Field(default=None)
    issues_list: Optional[list[dict[str, Any]]] = Field(default=None,
        description="query op 결과")
    retention_expires_at: datetime
    medical_disclaimer_shown: bool = Field(default=False)
```

### 3.1 예시
```json
{
  "operation": "sync",
  "sync_status": {"project_key": "VAMOS", "synced_count": 24,
                    "conflicts_resolved": 3, "conflicts_pending_manual": 0,
                    "errors_count": 0, "field_lww_applied_count": 3,
                    "next_sync_token": "jira-ckpt-xxx"},
  "retention_expires_at": "2026-07-18T00:00:00Z",
  "medical_disclaimer_shown": false
}
```

---

## §4 Algorithm Pseudocode — §13.1 #3

### 4.1 전체 흐름
```
ALGORITHM JiraLinear(input: JiraLinearInput) -> Result<JiraLinearOutput, VamosError>:
    # 1. LOCK-CD-07 policy_gate
    IF NOT input.consent_flags.get("oauth_target", False):
        RETURN Err(VamosError("COND_112_OAUTH_CONSENT_MISSING", ...))

    # 2. LOCK-CD-07 cost_gate: service rate limit
    IF exceeds_rate_budget(input.target_service):
        RETURN Err("COND_112_RATE_LIMIT_EXCEEDED",
                    fallback_id="FB-coalesce-next-window")

    # 3. LOCK-CD-07 evidence_gate: token 유효성
    oauth_creds = kms_resolve(input.oauth_creds_ref)
    IF now() >= oauth_creds.expires_at:
        refreshed = refresh_oauth(oauth_creds, input.target_service)
        IF refreshed.is_err():
            RETURN Err("COND_112_OAUTH_REFRESH_FAIL",
                        fallback_id=f"FB-reauth-{input.target_service}")

    # 4. Branch by operation
    client = jira_client if input.target_service == "jira" else linear_client
    SWITCH input.operation:
        CASE "create_issue":
            RETURN handle_create(client, input.issue_data)
        CASE "update_status":
            RETURN handle_update_status(client, input.issue_data)
        CASE "sync":
            RETURN handle_sync(client, input.sync_scope,
                                bidirectional=input.consent_flags.get("bidirectional_write", False))
        CASE "query":
            RETURN handle_query(client, input.query)


FUNCTION handle_sync(client, scope, bidirectional) -> Result:
    # 4a. 양쪽 변경 수집
    remote_changes = client.query_changes(scope.project_key, since=scope.since)
    local_changes = vamos_task_store.query_changes(scope.project_key, since=scope.since)

    # 4b. issue_id 매핑으로 충돌 감지
    conflicts = []
    for r in remote_changes:
        l = match_by_external_id(r, local_changes)
        IF l AND both_modified_since(r, l, scope.since):
            conflicts.append(Conflict(remote=r, local=l))

    # 4c. Field-level LWW + optimistic lock
    resolved = []
    pending_manual = []
    FOR c IN conflicts:
        merged = field_level_merge(
            remote=c.remote, local=c.local,
            rule="last_writer_wins_by_field_mtime",
        )
        # optimistic lock: version 비교
        IF merged.remote_version != c.remote.version:
            pending_manual.append(c)         # race detected — manual 필요
            continue
        apply_result = client.update_issue(
            issue_id=merged.external_id,
            changes=merged.fields,
            expected_version=c.remote.version,   # If-Match 헤더
        )
        IF apply_result.is_err():
            IF apply_result.code == "409_CONFLICT":
                pending_manual.append(c)         # version mismatch race
            ELSE:
                # ↓↓↓ CF-2026-04-07 옵션 (b) Phase 3 이월 placeholder ↓↓↓
                # Phase 2 에서는 단순 retry + fallback 만 수행.
                # Saga 보상 트랜잭션 실체 호출 (COND-033 CAT-C) 은 Phase 3 이월.
                # Phase 3 에서 multi-issue rollback 이 필요해지면 compensating action
                # 을 COND-033 Saga pattern 으로 구현 예정 (현 Phase 2 에서는 per-issue
                # best-effort retry + 실패 이슈 dead-letter queue 에 격리).
                retry_once_or_dead_letter(merged)
        resolved.append(apply_result)

    # 4d. non-conflicting changes 적용
    FOR change IN filter_non_conflicting(remote_changes + local_changes, conflicts):
        best_effort_apply(change)

    # 4e. checkpoint
    next_token = client.latest_checkpoint(scope.project_key)

    RETURN Ok(JiraLinearOutput(
        operation="sync",
        sync_status=SyncStatus(
            project_key=scope.project_key,
            synced_count=len(resolved) + len(non_conflicting),
            conflicts_resolved=len(resolved),
            conflicts_pending_manual=len(pending_manual),
            field_lww_applied_count=len([r for r in resolved if r.merge_rule == "last_writer_wins_by_field_mtime"]),
            errors_count=0,
            next_sync_token=next_token,
        ),
        retention_expires_at=now() + timedelta(days=90),
        medical_disclaimer_shown=False,
    ))
```

### 4.2 시간 복잡도
- **Remote query**: `O(N_changes)` — JIRA REST v3 / Linear GraphQL pagination
- **Local query**: `O(N_local_changes)` — VAMOS task store 인덱스 스캔
- **Conflict detect**: `O(N_remote + N_local)` (hash map)
- **Field merge**: `O(N_conflicts · N_fields)` — 이슈당 평균 10 필드
- **Apply**: 외부 API 지배 (JIRA 100 req/min, Linear 1,500 req/min)
- **전체**: `O(N_changes)` 선형, 1,000 이슈 ≤ 30초
- **LOCK 값 참조**: LOCK-CD-11 V2 ₩93K — Atlassian OAuth 무료, Linear 무료 tier, 월 ₩2K 이하

### 4.3 OAuth 2.0 AC + PKCE 플로우 (Atlassian / Linear 공통 스키마)
```
STEP 1 (Authorization — browser redirect):
  GET <service_oauth_endpoint>
    ?client_id=<CLIENT_ID>
    &redirect_uri=<REDIRECT_URI>
    &response_type=code
    &state=<CSPRNG_32B>
    &code_challenge=<SHA256(verifier)_BASE64URL>
    &code_challenge_method=S256             # PKCE S256 필수
    &scope=read:issue:jira write:issue:jira offline_access     # JIRA 예시
            issues:read issues:write app:oauth:issueUpdates    # Linear 예시

STEP 2 (Auth code exchange):
  POST <token_endpoint>
  Body: grant_type=authorization_code
        code=<AUTH_CODE>
        redirect_uri=<REDIRECT_URI>
        code_verifier=<PKCE_VERIFIER>
  → { access_token, refresh_token, expires_in, scope }

STEP 3 (Refresh token rotation):
  POST <token_endpoint>
  Body: grant_type=refresh_token&refresh_token=<...>
  → { access_token_new, refresh_token_new }
  기존 refresh_token grace period 30s

STEP 4 (Revoke — Right to Erasure 또는 사용자 연결 해제):
  POST <revocation_endpoint>  { token, token_type_hint }
```

### 4.4 동기화 전략 매트릭스 (COND-112 행)
| 소스 | 타겟 | 방향 | Conflict Resolution | 증분 기준 |
|---|---|---|---|---|
| JIRA / Linear | VAMOS Task | bidirectional | Merge by issue_id (field-level LWW + optimistic lock) | remote checkpoint + local updated_at |

### 4.5 Webhook HMAC-SHA256 서명 규약 (JIRA / Linear)
```
JIRA Webhook:
  헤더: X-Hub-Signature-256: sha256=<HEX>
  signed_message = body (JIRA 사전 합의 payload)
  expected = HMAC-SHA256(secret=JIRA_WEBHOOK_SECRET, message=body)

Linear Webhook:
  헤더: Linear-Signature: <HEX>
  signed_message = timestamp + body
  expected = HMAC-SHA256(secret=LINEAR_WEBHOOK_SECRET, message=signed_message)

공통 검증:
  constant_time_compare(expected, received)
  replay_window: 5분
  idempotency_key: JIRA webhookEvent.id / Linear updatedAt+issueId 조합
```

### 4.6 Status Mapping (3-way)
```
VAMOS canonical     JIRA workflow           Linear state
────────────────────────────────────────────────────────
backlog              "To Do"                  "Backlog"
in_progress          "In Progress"            "In Progress"
blocked              "Blocked" (커스텀)       "Blocked" (커스텀 label)
review               "In Review"              "In Review"
done                 "Done"                   "Done"
cancelled            "Cancelled"              "Cancelled"

매핑 테이블은 ModuleConfig 에서 override 가능 (기업별 workflow 커스텀).
```

---

## §5 Error Handling — §13.1 #4 (LOCK-CD-05 / LOCK-CD-06)

### 5.1 FailureCode 체계
```python
COND_112_OAUTH_CONSENT_MISSING
COND_112_OAUTH_SCOPE_INSUFFICIENT
COND_112_OAUTH_REFRESH_FAIL
COND_112_PKCE_VERIFIER_MISMATCH
COND_112_STATE_CSRF_MISMATCH
COND_112_WEBHOOK_SIGNATURE_INVALID
COND_112_WEBHOOK_REPLAY_STALE
COND_112_IDEMPOTENCY_KEY_REPLAY
COND_112_TARGET_API_FAIL              # JIRA/Linear 장애
COND_112_RATE_LIMIT_EXCEEDED
COND_112_OPTIMISTIC_LOCK_CONFLICT     # version mismatch
COND_112_BIDIRECTIONAL_WRITE_CONSENT_MISSING
COND_112_STATUS_MAPPING_MISSING
COND_112_PROJECT_NOT_FOUND
COND_112_MULTI_ISSUE_ROLLBACK_REQUIRED  # Phase 3 이월 placeholder (CF-2026-04-07)
COND_112_RETENTION_POLICY_VIOLATION
```

### 5.2 Phase별 복구 전략
```
Phase 1 (Validation/Pydantic): 자동 차단
Phase 2 (OAuth gate LOCK-CD-07 policy_gate): 재동의 + scope upgrade
Phase 3 (OAuth gate LOCK-CD-07 cost_gate): rate limit 도달 시 coalesce + backoff
Phase 4 (OAuth gate LOCK-CD-07 evidence_gate): refresh → re-auth
Phase 5 (Webhook signature): 400 + replay 차단 (idempotency 등재 skip)
Phase 6 (Replay stale): 400 stale timestamp
Phase 7 (Optimistic lock conflict): version mismatch → pending_manual 큐 (사용자 resolve)
Phase 8 (Status mapping missing): ModuleConfig 매핑 override 프롬프트 안내 + 작업 skip
Phase 9 (Target API fault): circuit breaker (3 연속 5xx → 60s open) + cached sync_status 제공
Phase 10 (CF-2026-04-07 Phase 3 이월 경로): multi-issue rollback 필요 시 현 Phase 2 에서는 per-issue dead-letter queue 로 격리, COND-033 Saga pattern 실체 호출은 Phase 3 이월 (상세 §6.4)
Phase 11 (Escalation): I-20 에스컬레이션 (tokens / raw issue body 배제)
```

### 5.3 Escalation Payload
```python
class EscalationPayload(BaseModel):
    source_engine: str = "COND-112"
    error_code: str
    target_service: str                # jira | linear
    project_key: str
    user_id_hashed: str
    operation: str                     # create_issue | update_status | sync | query
    retry_count: int
    conflicts_pending_manual: int
    timestamp: datetime
    # OAuth tokens / issue body / assignee_hashed 등 배제 (external_id, project_key 만 허용)
```

### 5.4 로깅 포맷 (R-01-7)
```json
{
  "trace_id": "trace-jl-...",
  "error": {"code": "COND_112_OPTIMISTIC_LOCK_CONFLICT", "severity": "WARN", "retry_count": 0},
  "context": {"project_key": "VAMOS", "external_id": "VAMOS-123",
               "module": "COND-112", "phase": "sync_apply"},
  "recovery": {"strategy": "enqueue_manual_resolution", "fallback_id": "FB-manual-queue",
                "pending_manual_count": 1}
}
```

### 5.5 CF-2026-04-07 해소 경로 (Phase 3 이월 placeholder — 옵션 (b) 채택)
본 모듈 설계에서 CF-2026-04-07 (CAT-C COND-079 multi-region replication 에서 COND-033 Saga 패턴 재사용 deferral) 를 참조하는 유일한 경로는 **sync 연산 중 multi-issue rollback 이 필요한 실패 시나리오** (예: 연속 3개 이슈 업데이트 중 2번째에서 target API 장애, 기 적용된 1번째 롤백 필요).

**결정**: Phase 2 exit_gate 범위에서는 **옵션 (b) Phase 3 이월 placeholder** 채택.
- Phase 2 에서 본 모듈은 per-issue dead-letter queue 로 실패 이슈를 격리하고 다음 sync 라운드에서 re-attempt (멱등성 전제)
- 이전 이슈 rollback 은 **사용자 결정** 대기 (FailureCode `COND_112_MULTI_ISSUE_ROLLBACK_REQUIRED`) — compensating action 자동 호출 없음
- **Phase 3 에서** multi-issue 원자성 요구가 확인되면 COND-033 (CAT-C Saga pattern) 재사용 경로 실체화 예정. 이때 종합계획서 §A.2 P0-1 의존성 매트릭스 정식 등록 + CONFLICT_LOG.md CF-2026-04-07 상태 `⏳ Phase 2 → RESOLVED-DEFERRED (Phase 3 이월)` 로 전환
- 도메인 마감 step 7 에서 CONFLICT_LOG 업데이트 시 "조치 완료" 열 = `RESOLVED-DEFERRED: Phase 2 범위에서는 per-issue dead-letter queue + 재시도 (Saga 실체는 Phase 3 이월)`

근거:
1. Phase 2 exit_gate 는 L937 "OAuth/Webhook 검증 + 동기화 전략" + L940 "COND-079→033 deferral 해소" 의 해소 기준을 "명시적 경로 결정" 으로 충족 (실체 구현까지 강제하지 않음)
2. **자동 RESOLVE 금지** 원칙 (§H abort 일반 규정) + **V1 불변 원칙** 을 위반하지 않음 (COND-033 V1 본문 미수정)
3. Saga pattern 실체 호출은 Phase 3 범위 — Phase 2 에서 placeholder 로만 명시하는 것이 안전 (선례: 5-1 C-21 / 4-4 CONF-ML-002/003 Phase 3 이월 패턴)

---

## §6 Dependency Map — §13.1 #5

### 6.1 내부 의존 (CAT-G 내부)
| 대상 | 방향 | 이유 |
|---|---|---|
| 없음 | — | JIRA/Linear 통합은 직접 CAT-G 타 모듈과 교차 없음 (COND-111 이 선택적 CONSUMES 역방향) |

### 6.2 외부 의존
| 대상 | 방향 | 이유 |
|---|---|---|
| Atlassian JIRA REST API v3 | CONSUMES+PRODUCES | Issues/Projects/Sprints + Webhook subscription |
| Linear GraphQL API | CONSUMES+PRODUCES | Issues/Projects/Cycles + Webhook subscription |
| `6-2 Security-Governance` | CROSS-DOMAIN | OAuth 토큰 AES-256-GCM + KMS + CSRF state + PKCE S256 + HMAC verify |
| `6-12 Event-Logging` | CROSS-DOMAIN | COND_112_* FailureCode prefix (oauth / webhook / sync / optimistic_lock 이벤트 별도 분류) |
| `3-10 Agent-Protocol-Interoperability` | CROSS-DOMAIN | 프로젝트 관리 연동 (_index.md L46 verbatim) — Agent-to-Agent interop 시 JIRA/Linear 가 공통 task registry 역할 |
| `CAT-C COND-033 Saga pattern` | **PHASE 3 이월 placeholder (CF-2026-04-07 옵션 (b))** | multi-issue rollback 필요 시 Phase 3 에서 compensating action 으로 재사용 예정. Phase 2 범위는 per-issue dead-letter queue 격리로 대체 (§5.5 참조) |
| `#3 Blue Node` | CROSS-DOMAIN | LOCK-CD-08 Integration Node P1 실행 종속 |

### 6.3 의존성 매트릭스 (CAT-G + CAT-C placeholder)
```
            033*  090  110  111  112
COND-112  [  P3   .    .    C    -  ]   P3=Phase 3 이월 (CF-2026-04-07), C=CONSUMES(event from COND-111),
                                          -=self, .=교차 없음
```

### 6.4 §A 매트릭스 cross-check 및 CF-2026-04-07 해소 경로
- **종합계획서 §A.2 P0-1**: CAT-C 내부 의존 (COND-079 → COND-033 Saga 재사용) 은 미수록 deferral 3건 중 1건
- **본 모듈 측 결정 (옵션 (b) 채택)**: §5.5 verbatim 참조
  - Phase 2 범위: per-issue dead-letter queue + 재시도 (Saga 미호출)
  - Phase 3 이월: multi-issue rollback 필요 시 COND-033 Saga pattern 재사용 실체화 (compensating action)
- **도메인 마감 step 7 (별도 대화창)**: `CONFLICT_LOG.md` CF-2026-04-07 행의 "조치 완료" 열을 `⏳ Phase 2` → `RESOLVED-DEFERRED: Phase 2 per-issue dead-letter + Phase 3 Saga 실체 이월` 로 갱신
- **본 세션 (2-3) 에서는** CONFLICT_LOG.md 파일 직접 편집 금지 (공통 산출물 보호) — 결정 근거는 본 문서 §5.5 + resp.txt 03_finalize 에 기록

### 6.5 Phase 1 deferral 인계
- CF-2026-04-07 해소 경로 본 §6.4 에 명시 (자동 RESOLVE 금지 원칙 준수)

---

## §7 Performance Benchmark — §13.1 #6

### 7.1 SLA 기준값
| 지표 | V1 기준 | V2 목표 |
|---|---|---|
| p50 sync 지연 (100 issues) | N/A | ≤ 3,000 ms |
| p99 sync 지연 | N/A | ≤ 10,000 ms |
| Webhook 처리 지연 | N/A | ≤ 400 ms (서명 + idempotency + dispatch) |
| OAuth 토큰 갱신 지연 | N/A | ≤ 500 ms |
| Optimistic lock 성공률 | N/A | ≥ 0.95 (≤ 5% version mismatch pending_manual) |
| Field-level merge 정확도 | N/A | ≥ 0.98 |
| 처리량 (query) | N/A | ≥ 30 req/s (JIRA 100 req/min rate limit 고려) |

### 7.2 비용 상한 참조 (LOCK-CD-11)
- V2 ₩93K 한도 내 설계. Atlassian OAuth 무료 / Linear 무료 tier, 월 ₩2K 이하
- OAuth token + sync history KMS 비용 ~₩0.5K/사용자/년

### 7.3 벤치마크 시나리오
```
BENCH-112-01: 100 issues sync (JIRA) → p50/p99 지연 + field_lww_applied_count
BENCH-112-02: Optimistic lock race 5% 주입 → pending_manual 비율
BENCH-112-03: Webhook payload 500건 burst (Linear) → signature + idempotency 처리량
BENCH-112-04: JIRA rate limit 도달 주입 → coalesce + backoff
BENCH-112-05: Multi-issue rollback 경로 (Phase 3 이월 placeholder 시나리오) → dead-letter queue 격리 + `COND_112_MULTI_ISSUE_ROLLBACK_REQUIRED` 이벤트
```

---

## §8 Integration Test Spec (I-05) — §13.1 #7 (≥ 3 + ⚠️ OAuth/Webhook/동기화/CF-2026-04-07 필수)

### 8.1 I-05-COND112-01: 정상 bidirectional sync
- **목적**: `operation="sync"`, 50 issues 양쪽 변경 없음 (단순 검증)
- **주입**: `since=24h ago`, mock JIRA 25 issues + VAMOS 25 tasks (대부분 겹침)
- **기대**:
  - `Result.is_ok()`, `synced_count >= 25`, `conflicts_resolved == 0`, `field_lww_applied_count == 0`
  - `next_sync_token != null`
- **목 데이터**: `mocks/COND-112/happy_path_sync.json`

### 8.2 I-05-COND112-02: ⚠️ OAuth 토큰 만료 → refresh
- **목적**: `refresh_token` 임박 + 자동 rotation
- **기대**:
  - `Result.is_ok()` (refresh 성공 후 재시도)
  - log: `oauth_refresh_succeeded` INFO (JIRA)
- **목 데이터**: `mocks/COND-112/oauth_expired_ok.json`

### 8.3 I-05-COND112-03: ⚠️ Webhook 서명 위조 → 400 + audit
- **목적**: 잘못된 HMAC 서명 주입
- **기대**:
  - `failure_code == "COND_112_WEBHOOK_SIGNATURE_INVALID"` 400
  - idempotency registry 미등재 + security alert 이벤트
- **목 데이터**: `mocks/COND-112/webhook_forged.json`

### 8.4 I-05-COND112-04 (추가): ⚠️ 동기화 충돌 field-level LWW + optimistic lock
- **목적**: 같은 `VAMOS-123` 이슈가 JIRA 에서 status/assignee 수정, VAMOS 에서 priority/labels 수정 → field disjoint merge
- **기대**:
  - `conflicts_resolved == 1`, `field_lww_applied_count == 1`
  - merged issue: JIRA status/assignee 수용 + VAMOS priority/labels 수용
  - 둘 다 같은 필드 수정한 경우 timestamp mtime 기반 LWW
- **목 데이터**: `mocks/COND-112/field_level_lww.json`

### 8.5 I-05-COND112-05 (추가): ⚠️ Multi-issue rollback 경로 (CF-2026-04-07 Phase 3 이월 검증)
- **목적**: sync 중 3 issues 업데이트 중 2번째 실패 → dead-letter + `COND_112_MULTI_ISSUE_ROLLBACK_REQUIRED` 이벤트 발행
- **기대**:
  - 1번째 이슈: 이미 적용됨 (rollback 안 함, Phase 2 범위)
  - 2번째 이슈: dead-letter queue 격리
  - 3번째 이슈: 처리 중단, 다음 sync 라운드에서 re-attempt
  - `COND_112_MULTI_ISSUE_ROLLBACK_REQUIRED` 이벤트 1건 발행 (Phase 3 이월 placeholder 경로 확인)
  - CONFLICT_LOG.md CF-2026-04-07 행의 "조치 완료" 열은 도메인 마감 step 7 에서 `RESOLVED-DEFERRED` 로 전환 예정 (본 시나리오에서 파일 편집 안 함)
- **목 데이터**: `mocks/COND-112/multi_issue_partial_fail.json`

### 8.6 Phase 3 시나리오 확장 (≥ 5 시나리오)
| ID | 제목 | 주입 | 기대 |
|---|---|---|---|
| 112-S6 | Optimistic lock version mismatch | expected_version 불일치 | `COND_112_OPTIMISTIC_LOCK_CONFLICT` + pending_manual |
| 112-S7 | Status mapping missing | 커스텀 workflow 매핑 부재 | `COND_112_STATUS_MAPPING_MISSING` + skip |
| 112-S8 | JIRA 5xx 연속 → circuit breaker | 3연속 500 | circuit open 60s + cached sync_status |
| 112-S9 | Right to Erasure | delete_user | 72h 내 OAuth refresh_token + sync history 삭제 + Atlassian/Linear revocation |
| 112-S10 | Trace 전파 | `trace_id="T-jl"` | 일치 |
| 112-S11 | PKCE verifier mismatch | 변조된 verifier | `COND_112_PKCE_VERIFIER_MISMATCH` 400 |
| 112-S12 | CSRF state mismatch | state 변조 | `COND_112_STATE_CSRF_MISMATCH` 400 |
| 112-S13 | Rate limit 도달 | JIRA 100 req/min 초과 | `COND_112_RATE_LIMIT_EXCEEDED` + backoff |
| 112-S14 | Query JQL 복잡도 | 깊은 JQL 표현식 | max_results 제한 준수 + pagination next_cursor |

---

## §9 Blue Node Integration (LOCK-CD-04 / LOCK-CD-08) — §13.1 #8

### 9.1 Blue Node 소비 계약
- **Integration Node** / **P1 (승인 후 활성)** / 독립 실행 금지

### 9.2 Runnable 프로토콜
```python
class JiraLinear(BaseModule, Runnable):
    def initialize(self, config: ModuleConfig) -> None: ...
    def execute(self, input: JiraLinearInput) -> Result[JiraLinearOutput, VamosError]: ...
    def run(self, input: JiraLinearInput) -> Result[JiraLinearOutput, VamosError]: ...
    def health_check(self) -> HealthStatus: ...   # JIRA ping + Linear ping
    def get_metadata(self) -> ModuleMetadata: ...
    def shutdown(self) -> None: ...
```

### 9.3 ModuleConfig (LOCK-CD-10)
```python
config = ModuleConfig(
    enabled=True,
    priority=5,                      # MEDIUM
    max_concurrent=4,
    timeout_ms=10000,                # sync 대량 작업 고려
    retry_policy=RetryPolicy(max_retries=2, backoff="exponential",
                              retry_on=["COND_112_TARGET_API_FAIL",
                                        "COND_112_RATE_LIMIT_EXCEEDED"]),
)
```

### 9.4 Permission Level (LOCK-CD-08)
```
P1: Integration Node 승인 후 활성 (OAuth + bidirectional_write 동의 전제)
P0: 관리자 (OAuth CLIENT_SECRET rotation + status mapping override)
```

### 9.5 Blue Node Event (6-12)
```
COND_112_ISSUE_CREATED                  INFO    external_id, project_key, target_service
COND_112_ISSUE_UPDATED                  INFO    external_id, version_new
COND_112_SYNC_SUCCEEDED                 INFO    project_key, synced_count, field_lww_count
COND_112_FIELD_LWW_APPLIED              INFO    external_id, field_names, winner_side
COND_112_OPTIMISTIC_LOCK_CONFLICT       WARN    external_id, expected_version, current_version
COND_112_WEBHOOK_SIGNATURE_INVALID      ERROR   target_service, source_ip_hash (security alert)
COND_112_OAUTH_REFRESH_SUCCEEDED        INFO    target_service, new_expires_at
COND_112_RATE_LIMIT_EXCEEDED            WARN    target_service, next_window_ms
COND_112_MULTI_ISSUE_ROLLBACK_REQUIRED  WARN    project_key, failed_external_id, phase_3_deferred (CF-2026-04-07)
COND_112_STATUS_MAPPING_MISSING         WARN    project_key, unknown_status
```

---

## §10 V2-Phase 2 변경 이력

| 버전 | 일자 | 변경 요약 | 근거 |
|---|---|---|---|
| V1 | 2026-03-22 | 초기 골격 (SHELL L1) | Phase 1 산출 이전 |
| V2 | 2026-04-19 | L3 상세 + OAuth 2.0 AC+PKCE(S256) + Webhook HMAC-SHA256 + Idempotency + bidirectional merge by issue_id (field-level LWW + optimistic lock) + 3-way status mapping + CF-2026-04-07 옵션 (b) Phase 3 이월 placeholder 채택 (§5.5 + §6.4) + Integration Node P1 | STAGE 7 Phase 7-II 2-2 STEP_B 세션 2-3 |

### 10.1 Pydantic 재사용 출처
- `ModuleConfig` 재사용: `common_types.md §3.4` (LOCK-CD-10 정본)
- `VamosError` 재사용: `D2.0-02 §0.3` (LOCK-CD-06 정본)
- `Result[T, E]` 재사용: `D2.0-02 §0.3` (LOCK-CD-05 정본)

---
