# Push Notifications — 웹훅 기반 비동기 알림 + State Transition History

> **도메인**: #11 Conversation-A2A (TIER3-DOMAIN-08)
> **서브폴더**: `04_advanced-features/`
> **V2 세션**: P2-2 (Phase 2 #2, P0)
> **작성일**: 2026-04-22
> **Status**: V2-Phase 2 DRAFT (L3)
> **상세명세 근거**: §2.1 method enum (`tasks/pushNotification/set`, `tasks/pushNotification/get`), §2.1 `$defs.PushNotificationConfig`, §5.1 V2#2 Push Notifications + V2#3 State Transition History
> **종합계획서 근거**: §7 Phase 2 테이블 #2, §7.3 P2-2 블록 (L1047~L1080), §6.1 구현 항목 #36 (Push) + #37 (State Transition History)
> **STEP7-B 상위 SoT**: `#47 Hook 시스템` (L598, VAMOS 미적용), `#69 세션 영속성` (L991, 설계만), `#37` 간접 (상태 이력 = Hook post 연동)
> **LOCK 직접 보호**: LOCK-A2A-01 JSON-RPC 2.0 / LOCK-A2A-02 Task 상태 열거형
> **LOCK 간접 참조**: LOCK-A2A-09 Circuit Breaker (웹훅 장애 복구), LOCK-A2A-06 mTLS 인증서 (콜백 엔드포인트 인증)

---

## 교차 참조

- `_index.md` — 04_advanced-features/ 항목 #3 (Push Notifications P0) / #4 (State Transition History P1)
- `streaming_sse.md` — `-32003 Push notification not supported` 시 SSE 폴백 (streaming_sse.md §6.3)
- `multi_turn_sessions.md` — sessionId 기반 장기 대화의 상태 전이 이력 누적
- `conversation_state_machine.md` — State Transition History 의 from/to state 값은 대화 상태 머신 전이 6 종 + Task Lifecycle 6 상태
- `moa_pattern.md` — MoA aggregator 완료 시점 Push 알림 (proposer 병렬 실행 후 단일 결과)
- `05_monitoring/metrics_dashboard.md` — Push 전송 성공률 + 재시도 카운터 + audit chain 크기
- `03_security/audit_logging.md` — Push 이벤트 audit trail (mTLS + JWT + delegation_chain)
- 상위 아키텍처 정본: `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` Agent Workflow / Hook 시스템 연계
- 상위 가이드 (벤치마크 참조 전용, CLF-A2A-003 RESOLVED): STEP7-B §E L598 #47 Hook 시스템 (Claude ✅ 6종, 타 AI ❌, VAMOS ❌ 미적용), §H L991 #69 세션 영속성 (10종 AI ✅/VAMOS ⚠️ 설계만)

---

## 1. 개요

### 1.1 목적

A2A Task 의 비동기 상태 전이를 구독 에이전트(또는 외부 웹훅 엔드포인트)에게 능동적으로 통지하는 메커니즘을 정의한다. Google A2A Spec `tasks/pushNotification/set` / `tasks/pushNotification/get` method 를 구현하며, 동시에 Task Lifecycle 6 상태 (LOCK-A2A-02) 의 **State Transition History** 저장/조회 API 를 제공한다.

### 1.2 범위

- `tasks/pushNotification/set` — Task 단위 Push 구독 등록 (`PushNotificationConfig` 포함)
- `tasks/pushNotification/get` — 등록된 구독 조회
- 알림 페이로드 스키마 (JSON-RPC 2.0 envelope + Task 상태 diff)
- 상태 전이 이력 저장 스키마 (append-only ledger, LOCK-A2A-02 6 상태 enum 엄수)
- 구독 관리 API (등록 / 조회 / 해제 / 만료)
- 웹훅 콜백 재시도 + Circuit Breaker 연동 (LOCK-A2A-09)
- 콜백 엔드포인트 인증 (mTLS + Bearer + HMAC-SHA256 이중 검증)

### 1.3 범위 외 (Phase 3 이월)

- WebSocket 양방향 스트림 기반 실시간 push — Phase 3 V3
- 이메일 / 슬랙 / MS Teams 등 인간 대상 채널 — Phase 3 `notification_channels.md`
- Push 기반 체인 트리거 오케스트레이션 — Phase 3 `agent_composition.md`

---

## 2. tasks/pushNotification method 설계

### 2.1 요청 스키마 — `tasks/pushNotification/set`

**LOCK-A2A-01 JSON-RPC 2.0 프로토콜 버전 verbatim 준수** — `"jsonrpc": "2.0"` 필드 고정.

```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid",
  "method": "tasks/pushNotification/set",
  "params": {
    "id": "task-uuid",
    "pushNotificationConfig": {
      "url": "https://agent-b.vamos.dev/callbacks/a2a",
      "token": "Bearer eyJhbGciOi...",
      "authentication": {
        "schemes": ["Bearer", "mTLS"]
      }
    }
  }
}
```

- `pushNotificationConfig` 는 상세명세 §2.1 `$defs.PushNotificationConfig` schema verbatim 준수.
- `url` 은 HTTPS + 유효한 mTLS 인증서 보유 엔드포인트만 허용.
- `token` 은 Bearer JWT (상세명세 §4.1 JWT Claims 준수) 또는 HMAC-SHA256 shared secret.

### 2.2 응답 스키마

```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid",
  "result": {
    "subscription_id": "sub-uuid",
    "task_id": "task-uuid",
    "registered_at": "2026-04-22T10:12:00Z",
    "ttl_seconds": 86400,
    "events_subscribed": ["task_status", "task_artifact"]
  }
}
```

### 2.3 `tasks/pushNotification/get`

```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid-2",
  "method": "tasks/pushNotification/get",
  "params": { "id": "task-uuid" }
}
```

응답: 등록된 모든 `PushNotificationConfig` 배열 반환 (여러 구독자 가능).

### 2.4 `-32003 Push notification not supported`

상세명세 §4.4: 에이전트 카드 `capabilities.pushNotifications=false` 또는 인프라 미지원 시 해당 코드로 응답. 클라이언트는 `streaming_sse.md` 의 `tasks/sendSubscribe` 경로로 폴백.

---

## 3. 알림 페이로드 스키마

### 3.1 웹훅 → 구독자 HTTP 콜백 포맷

서버는 Task 상태 전이 발생 시 구독된 `url` 로 HTTP POST 호출한다. 바디는 JSON-RPC 2.0 notification (id 필드 없음) 형태.

```http
POST /callbacks/a2a HTTP/1.1
Host: agent-b.vamos.dev
Content-Type: application/json
Authorization: Bearer <JWT>
X-A2A-Signature: sha256=<HMAC>
X-A2A-Subscription-Id: sub-uuid
X-A2A-Delivery-Id: dlv-uuid
X-A2A-Timestamp: 2026-04-22T10:12:05Z

{
  "jsonrpc": "2.0",
  "method": "a2a.push.task_status",
  "params": {
    "subscription_id": "sub-uuid",
    "task_id": "task-uuid",
    "event": {
      "event_type": "task_status",
      "from_state": "working",
      "to_state": "completed",
      "timestamp": "2026-04-22T10:12:05Z",
      "final": true,
      "artifact_hint": { "name": "review.md", "last_chunk": true }
    }
  }
}
```

### 3.2 이벤트 타입

| `event.event_type` | 의미 | `final` |
|--------------------|------|---------|
| `task_status` | Task Lifecycle 상태 전이 (LOCK-A2A-02 6 상태 enum) | `state∈{completed, failed, canceled}` (종단 상태) 시 `true`, `input-required` 는 비종단이므로 `false` |
| `task_artifact` | 새 artifact 생성 (chunking 포함) | `last_chunk=true` 시만 true |
| `context_transition` | 대화 상태 머신 전이 (`conversation_state_machine.md` §5.2) | N/A |

### 3.3 HMAC 서명 (`X-A2A-Signature`)

- `sha256=` prefix + lowercase hex.
- 원본: `<X-A2A-Timestamp>.<request_body_sha256>` concatenation.
- 구독자는 서명 검증 실패 시 즉시 401 응답.

### 3.4 중복 전달 방지

- `X-A2A-Delivery-Id` 는 UUID v4. 구독자는 최근 1 시간 내 동일 delivery-id 재수신 시 idempotent 처리 (노-op 응답 204).

---

## 4. State Transition History — 상태 전이 이력 저장

### 4.1 저장 스키마 (append-only ledger)

```python
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


class TaskState(str, Enum):
    """LOCK-A2A-02 Task 상태 열거형 verbatim."""

    SUBMITTED = "submitted"
    WORKING = "working"
    INPUT_REQUIRED = "input-required"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class TransitionEventRecord(BaseModel):
    """State Transition History 단일 엔트리.
    append-only, 수정·삭제 금지. 하나의 Task 는 최소 2 row (submitted + terminal) 보장."""

    record_id: str = Field(..., description="UUID v4, 전역 유일")
    task_id: str
    session_id: Optional[str] = None
    sequence_num: int = Field(..., ge=1, description="task 내 단조 증가 시퀀스 (1-base)")
    from_state: Optional[TaskState] = Field(None, description="최초 submit 시 null")
    to_state: TaskState
    transitioned_at: datetime
    trigger: Literal[
        "user_request",          # tasks/send 수신
        "agent_action",          # 에이전트 내부 상태 전이
        "subtask_complete",      # 위임 에이전트 완료
        "timeout",               # SSE 300s 또는 internal timer
        "circuit_breaker",       # LOCK-A2A-09 OPEN 전환
        "user_cancel",           # tasks/cancel 수신
    ]
    payload_hash: str = Field(..., description="전이 시점 Task context snapshot의 sha256")
    delegation_depth: int = Field(0, ge=0, le=3, description="LOCK-A2A-07 max 3")
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

- `delegation_depth` 는 LOCK-A2A-07 JWT 위임 체인 최대 깊이 3 준수 검증용.
- `from_state=None && to_state=SUBMITTED` 는 task 생성 시점의 최초 row.
- 스토리지는 append-only DB (immudb / QLDB) 또는 Merkle-tree ledger 권장.

### 4.2 조회 API (`tasks/stateHistory`)

> 상세명세 §2.1 method enum 에는 명시되지 않은 **확장 method** (A2A Spec 표준 method 외 VAMOS 확장). `agent/authenticatedExtendedCard` 와 동일하게 에이전트 카드 `capabilities.stateTransitionHistory=true` 일 때만 지원.

```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid-3",
  "method": "tasks/stateHistory",
  "params": {
    "id": "task-uuid",
    "limit": 100,
    "since_sequence": 1
  }
}
```

응답: `TransitionEventRecord[]` 최신 순. 최대 1,000 레코드/요청 (페이지네이션).

### 4.3 LOCK-A2A-02 Task 상태 열거형 verbatim 5필드 분리 인용

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-02` |
| **항목** | Task 상태 열거형 |
| **값** | `submitted\|working\|input-required\|completed\|failed\|canceled` |
| **출처** | `Google A2A Spec` |
| **변경 조건** | `스펙 업데이트 시 검토` |

- 적용 위치: §4.1 `TaskState` Enum verbatim / §3.2 event_type / §4.4 허용 전이 DAG.

### 4.4 허용 전이 DAG (LOCK-A2A-02 기반)

```
submitted ──┬─▶ working ──┬─▶ completed   (정상 종료)
            │             ├─▶ failed      (실패 종료)
            │             ├─▶ canceled    (사용자 취소)
            │             └─▶ input-required
            │                    │
            │                    └─(user_request)──▶ working  (루프 허용)
            └─▶ canceled                             (submit 즉시 취소)
```

- DAG 위반 전이 (예: `completed → working`) 발생 시 서버는 `-32000 Invalid transition` 응답, 전이 이력 미기록.

---

## 5. 구독 관리 API

### 5.1 라이프사이클

| 이벤트 | method | 결과 |
|--------|--------|------|
| 등록 | `tasks/pushNotification/set` | `subscription_id` 발급, ttl 24h 기본 |
| 조회 | `tasks/pushNotification/get` | 등록된 모든 config 반환 |
| 갱신 | `tasks/pushNotification/set` 재호출 | 동일 task_id+url 조합 재등록 시 ttl 연장 |
| 해제 | `tasks/pushNotification/set` with `null` config (확장) | 즉시 해제, 209 No Content |
| 만료 | ttl 경과 | 자동 해제, `-32031 Subscription expired` 반환 |

### 5.2 권한 체크 (mTLS + JWT)

- `tasks/pushNotification/set` 호출자는 해당 `task_id` 에 대한 `task:read` Permission 보유 필수 (상세명세 §4.2 DelegationToken).
- 콜백 엔드포인트의 mTLS 인증서는 LOCK-A2A-06 "30일 전 자동 갱신" 정책 준수 (AUTHORITY §3 LOCK-A2A-06 verbatim).

---

## 6. 웹훅 재시도 + Circuit Breaker 연동

### 6.1 재시도 정책

- 구독자 엔드포인트 응답 시간 상한 5 초 (HTTP timeout).
- 재시도: 2^n × 500ms 지수 백오프, n=0..4 (최대 8 초).
- 최대 재시도 5 회. 모두 실패 시 Dead Letter Queue (DLQ) 이동.

### 6.2 LOCK-A2A-09 Circuit Breaker 연동

**LOCK-A2A-09 verbatim 5필드 분리 인용**:

| 필드 | 값 |
|------|-----|
| **LOCK ID** | `LOCK-A2A-09` |
| **항목** | Circuit Breaker 연속 실패 임계 |
| **값** | `3회 → OPEN, 60초 후 HALF-OPEN` |
| **출처** | `D2.0-05 §4.4 (ADD-072)` |
| **변경 조건** | `D2.0-05 변경 시만` |

- 동일 구독 url 에 대한 연속 3 회 실패 시 해당 구독 CB OPEN. 60 초 간 push 시도 스킵 (이벤트는 `State Transition History` 에 보존, 재접속 시 catch-up).
- 60 초 후 HALF-OPEN: 1 건 시험 전송, 성공 시 CLOSED 복귀.
- 의도적 차이 (CLF-A2A-004 RESOLVED): A2A 3 회 vs MCP 5 회 — 다중 에이전트 체인 파급 방지, 5 회 상향 금지.

### 6.3 SSE 폴백 (역방향)

- Push 구독 CB OPEN 상태에서 클라이언트가 상태를 놓치지 않도록 `tasks/sendSubscribe` 또는 `tasks/resubscribe` 로 SSE 전환 권장 (`streaming_sse.md` §6.3 `-32003` 정방향과 역방향 대칭).

---

## 7. audit_logging 연계 (03_security)

- 모든 push 전송 시도는 `03_security/audit_logging.md` schema 에 따라 audit event 기록 (상세명세 §4.3).
- `event_type=a2a.push.delivery.success` / `a2a.push.delivery.failure` / `a2a.push.cb.open`.
- delegation_chain 필드 포함 (LOCK-A2A-07 위임 깊이 증빙).

---

## 8. Phase 3 테스트 시나리오 (12 건)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|----------|----------|----------|
| PN-01 | 정상 Push 구독 + 전이 알림 | `tasks/pushNotification/set` → 3 초 후 task `working→completed` | 구독자 콜백 1 회 (task_status.completed), HMAC 서명 검증 통과 |
| PN-02 | 구독 조회 | `tasks/pushNotification/get` | 등록 직후 1 건 반환 |
| PN-03 | 구독 해제 (null config) | 해제 요청 → 이후 전이 | 해제 후 콜백 0 건 |
| PN-04 | 구독 만료 (ttl) | ttl 86400s 경과 시점 전이 | `-32031 Subscription expired` 응답 |
| PN-05 | 웹훅 재시도 (일시 5xx) | 구독 url 첫 2 회 503, 3 회 200 | 3 번째 시도 성공, DLQ 진입 0 |
| PN-06 | 웹훅 DLQ | 구독 url 5 회 연속 실패 | DLQ 진입 1 건, CB OPEN |
| PN-07 | Circuit Breaker 60 초 복구 | CB OPEN 후 60 초 경과 + 엔드포인트 복구 | HALF-OPEN 1 건 성공 → CLOSED 복귀, 누락 이벤트 catch-up |
| PN-08 | `-32003 Push not supported` | 에이전트 카드 `pushNotifications=false` | SSE 폴백 유도 응답 |
| PN-09 | HMAC 서명 위조 | 임의 변조된 X-A2A-Signature | 구독자 401 응답, 서버는 실패 카운터 증가 |
| PN-10 | 중복 delivery-id | 동일 delivery-id 1 시간 내 2 회 전송 | 2 번째 204 No Content (idempotent) |
| PN-11 | State Transition History 조회 | Task 종료 후 `tasks/stateHistory limit=100` | 최소 2 row (submitted + terminal), append-only 확인 |
| PN-12 | LOCK-A2A-07 깊이 3 초과 Push | delegation_depth=4 상태 전이 | `-32000` 거절 + audit event `depth_violation` |
| PN-13 | DAG 위반 전이 | `completed → working` 강제 주입 | `-32000 Invalid transition`, 이력 미기록 |
| PN-14 | MoA aggregator 완료 Push | `moa_pattern.md` aggregator 종료 후 단일 Push | 1 회 `task_status.completed`, proposer 단위 중간 Push 0 회 (aggregator-only 정책) |

---

## 9. LOCK 인용 표 (5필드 분리 강제)

| LOCK ID | 항목 | 값 | 출처 | 변경 조건 |
|---------|------|-----|------|----------|
| LOCK-A2A-01 | JSON-RPC 2.0 프로토콜 버전 | `"jsonrpc": "2.0"` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-02 | Task 상태 열거형 | `submitted\|working\|input-required\|completed\|failed\|canceled` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-06 | mTLS 인증서 만료 자동 갱신 | 30일 전 | 가이드 §4.3/#11 | 변경 금지 |
| LOCK-A2A-07 | JWT delegation chain 최대 깊이 | 3 | 가이드 §4.3/#11 | 보안 검토 후만 변경 |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | D2.0-05 §4.4 (ADD-072) | D2.0-05 변경 시만 |

- LOCK-A2A-01 적용: §2.1 요청 스키마 / §3.1 콜백 포맷
- LOCK-A2A-02 적용: §4.1 TaskState Enum / §4.4 전이 DAG
- LOCK-A2A-06 적용: §5.2 mTLS 인증서 만료 갱신 참조
- LOCK-A2A-07 적용: §4.1 `delegation_depth ≤ 3` 검증 / PN-12 시나리오
- LOCK-A2A-09 적용: §6.2 Circuit Breaker

---

## 10. 세션 간 인터페이스 cross-check

| 항목 | 대상 산출물 | 일치 항목 |
|------|------------|----------|
| `TaskState` enum | `streaming_sse.md` §3.1 state field + `multi_turn_sessions.md` | 6 상태 verbatim |
| `TransitionEventRecord` Pydantic | `multi_turn_sessions.md` + `conversation_state_machine.md` | sequence_num 단조성 + append-only |
| `PushNotificationConfig` | 상세명세 §2.1 `$defs.PushNotificationConfig` | url / token / authentication.schemes 필드 verbatim |
| HMAC X-A2A-Signature 규칙 | `03_security/audit_logging.md` | tamper-evident chain 설계와 정합 |
| CB 3 회 임계 | `streaming_sse.md` §6.1 + `moa_pattern.md` + `metrics_dashboard.md` | LOCK-A2A-09 verbatim 3 회 / 60 초 |
| delegation_depth 3 | `03_security/audit_logging.md` + `03_security/mtls_jwt.md` | LOCK-A2A-07 verbatim max_depth 3 |

---

## 11. 변경 이력

| 날짜 | 변경자 | 내용 |
|------|--------|------|
| 2026-04-22 | STAGE 7 3-8 STEP_B #2a (parent-executed) | V2-Phase 2 NEW 최초 작성 (P2-2 Push Notifications + State Transition History, push_notifications.md 별도 파일로 배치 — plan L1078 "multi_turn_sessions.md 통합" vs _index.md "streaming_sse.md 통합" 3원 불일치, 사용자 정밀성 우선 결정에 따라 Push/State 결합 독립 파일 채택, [CONFLICT_CANDIDATE:push_file_placement] #2c step 7 추적) |
