# Streaming SSE — Server-Sent Events 실시간 스트리밍

> **도메인**: #11 Conversation-A2A (TIER3-DOMAIN-08)
> **서브폴더**: `04_advanced-features/`
> **V2 세션**: P2-1 (Phase 2 #1, P0)
> **작성일**: 2026-04-22
> **Status**: V2-Phase 2 DRAFT (L3)
> **상세명세 근거**: §2.1 method enum (`tasks/sendSubscribe`, `tasks/resubscribe`), §2.2 TaskStatusEvent/TaskArtifactEvent, §5.1 V2#1 Streaming SSE
> **종합계획서 근거**: §7 Phase 2 테이블 #1, §7.3 P2-1 블록 (L1010~L1045), §6.1 구현 항목 #35 (Streaming SSE) + #46 (agent_streaming 상태)
> **STEP7-B 상위 SoT**: `#61 스트리밍 출력` (L622), `#18 S7B-018 스트리밍 출력 구현` (L711)
> **LOCK 직접 보호**: LOCK-A2A-05 컨텍스트 윈도우 / LOCK-A2A-09 Circuit Breaker
> **LOCK 간접 참조**: LOCK-A2A-01 JSON-RPC 2.0 / LOCK-A2A-02 Task 상태 열거형

---

## 교차 참조

- `_index.md` — 04_advanced-features/ 항목 #1 (SSE 스트리밍 P0) / #2 (SSE 재연결 P1) / #13 (타임아웃 300초 P0)
- `push_notifications.md` — 에러 `-32003 Push notification not supported` 발생 시 SSE 스트리밍으로 폴백 (CONVERSATION_A2A_상세명세.md §4.4 에러 코드 카탈로그)
- `multi_turn_sessions.md` — sessionId 기반 장기 스트리밍 연결 관리
- `conversation_state_machine.md` — agent_streaming 상태를 대화 상태 머신 안에서 awaiting_agent 분기 중 하나로 정의 (§5.2 상태 머신)
- `moa_pattern.md` — MoA proposer 병렬 스트리밍 시 aggregator 집계 단계까지의 progress 이벤트 집약
- `05_monitoring/metrics_dashboard.md` — SSE 활성 연결 수 (`active_sessions`) + stream timeout rate 메트릭 소비
- 상위 아키텍처 정본: `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` §4.4 Circuit Breaker (LOCK-A2A-09 정본), §12.13 컨텍스트 관리 (LOCK-A2A-05 정본)
- 상위 가이드 (벤치마크 참조 전용, CLF-A2A-003 RESOLVED): STEP7-B §G L622 #61 스트리밍 출력 (Claude / GPT / Gemini / Perplexity / Kimo / DeepSeek ✅ 지원, VAMOS ⚠️ 설계만)

---

## 1. 개요

### 1.1 목적

Server-Sent Events(SSE) 프로토콜 기반 단방향 실시간 스트리밍을 통해 A2A Task 의 상태 변화(`TaskStatusEvent`)와 부분 결과(`TaskArtifactEvent`)를 클라이언트 에이전트에게 지연 없이 전달한다. Google A2A Spec `tasks/sendSubscribe` 및 `tasks/resubscribe` method 를 구현한다.

### 1.2 범위

- `tasks/sendSubscribe` — Task 생성 + 즉시 SSE 구독 시작
- `tasks/resubscribe` — 끊어진 SSE 연결 복구 (last-event-id 기반)
- 3 종 SSE 이벤트: `task_status` / `artifact_chunk` / `heartbeat`
- 연결 관리: 타임아웃 300초 (R-11-7), 재연결 백오프, 백프레셔
- `agent_streaming` 상태 전이 (§6.1 #46)
- 회로 차단기 (LOCK-A2A-09) 연동
- 컨텍스트 윈도우 압축 트리거 (LOCK-A2A-05) 연동

### 1.3 범위 외 (Phase 3 이월)

- WebSocket 양방향 스트림 — Phase 3 V3 확장 예정
- Push Notifications (웹훅) — `push_notifications.md` 참조
- HTTP/2 server push — 인프라 계층 결정 후 Phase 3 검토
- Priority Queuing 에 의한 스트림 선점 — `priority_queuing.md` (Phase 3 계획)

---

## 2. SSE 엔드포인트 설계

### 2.1 엔드포인트 경로

| Method | HTTP | 경로 | 설명 |
|--------|------|------|------|
| `tasks/sendSubscribe` | POST | `/a2a/tasks` (JSON-RPC body `method` 필드로 구분) | Task 생성 + SSE 구독 동시 시작 |
| `tasks/resubscribe` | POST | `/a2a/tasks` | 기존 Task 에 대한 SSE 재구독 (`last-event-id` 헤더) |

- `/.well-known/agent.json` `capabilities.streaming=true` 일 때만 지원 (상세명세 §2.3 `capabilities.streaming`).
- 본 문서는 JSON-RPC 2.0 envelope 위에 SSE 응답을 얹는 하이브리드 설계로, `LOCK-A2A-01` JSON-RPC 2.0 프로토콜 버전을 유지한다.

### 2.2 요청 스키마

```json
{
  "jsonrpc": "2.0",
  "id": "req-uuid",
  "method": "tasks/sendSubscribe",
  "params": {
    "id": "task-uuid",
    "sessionId": "sess-uuid",
    "message": { "role": "user", "parts": [{ "type": "text", "text": "..." }] },
    "metadata": { "idempotency_key": "uuid-v4" }
  }
}
```

### 2.3 응답 헤더 (SSE 업그레이드)

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no             # 프록시 버퍼링 금지
X-A2A-Stream-Id: stream-<uuid>    # 재접속 식별자
```

- `X-Accel-Buffering: no` 는 nginx/ingress 프록시에서 중간 버퍼링을 방지한다.
- `X-A2A-Stream-Id` 는 `tasks/resubscribe` 시 서버가 old stream 세션을 식별하는 키.

---

## 3. 이벤트 유형 정의

SSE 스트림은 아래 3 종 이벤트로 구성된다. 각 이벤트는 `event:` 라인 + `id:` 라인 + `data:` 라인 세트로 전송된다.

### 3.1 `task_status` — 상태 전이

- `TaskStatusEvent` (상세명세 §2.2) 를 JSON 직렬화하여 `data:` 라인에 담는다.
- `state` 필드는 LOCK-A2A-02 Task 상태 열거형 (`submitted|working|input-required|completed|failed|canceled`) 만 허용한다.

```
event: task_status
id: evt-1
data: {"id":"task-uuid","status":{"state":"working","timestamp":"2026-04-22T10:12:00Z","progress":{"current":1,"total":5,"unit":"steps"}},"final":false}
```

### 3.2 `artifact_chunk` — 부분 결과

- `TaskArtifactEvent` (상세명세 §2.2) 를 직렬화. `artifact.parts[]` 는 `text` / `file` / `data` part 를 포함할 수 있다.
- 대용량 artifact 는 `last_chunk` 를 `false` 로 유지하며 여러 이벤트에 분할하여 전송 (향후 `artifact_chunking.md` Phase 3 참조).

```
event: artifact_chunk
id: evt-2
data: {"id":"task-uuid","artifact":{"name":"review.md","parts":[{"type":"text","text":"..."}]},"last_chunk":false}
```

### 3.3 `heartbeat` — 생존 신호

- 30 초 간격으로 전송. 데이터 변경 없이 연결 유지 + 프록시 idle-timeout 회피 목적.
- 형식: `data: {"timestamp":"2026-04-22T10:12:30Z"}` — `event:` 생략 시 기본 `message` 로 간주되므로 명시적으로 `event: heartbeat` 선언.

```
event: heartbeat
id: hb-1
data: {"timestamp":"2026-04-22T10:12:30Z"}
```

### 3.4 이벤트 종료 트리거

| `state` (task_status) | `final` | SSE 동작 |
|-----------------------|---------|----------|
| `completed` / `failed` / `canceled` | `true` | 서버는 즉시 마지막 `task_status` 전송 후 연결 close |
| `input-required` | `true` (부분 종료) | 서버가 연결을 유지한 채 클라이언트의 다음 `tasks/send` 를 대기하거나, 연결 close 후 클라이언트 resubscribe 유도 |
| `working` / `submitted` | `false` | 스트림 지속 |

---

## 4. 연결 관리

### 4.1 타임아웃 (R-11-7)

- **상한**: 300 초 (R-11-7 — "SSE 스트리밍 연결 타임아웃 300초"). 종합계획서 §4.3 R-11-7 정본.
- 서버는 300 초가 경과한 idle stream 을 강제 close 하며, `event: task_status` 마지막 이벤트에 `final=false` + `state=working` (미완료 경우) 로 전송 후 전송 계층(transport) 연결만 종료한다. `final=true` 는 LOCK-A2A-02 종단 상태(completed|failed|canceled) 에만 사용하므로 미완료 idle close 시에는 절대 `final=true` 를 사용하지 않는다.
- 클라이언트는 close 후 `tasks/resubscribe` 로 재접속하여 이어서 수신한다.

### 4.2 재연결 로직

1. 클라이언트는 수신한 마지막 `id:` 값을 `last-event-id` 로 보존.
2. 네트워크 단절 감지 시 지수 백오프 (`2^n × 500ms`, n=0..5, 최대 16 초) 후 `POST /a2a/tasks` `method=tasks/resubscribe` 재호출. 본문은 `params.id` + HTTP 헤더 `last-event-id: <evt-id>`.
3. 서버는 `stream-<uuid>` 별 event 버퍼 (최대 256 개 또는 5 분) 를 기준으로 `last-event-id` 이후 이벤트만 재전송. 버퍼가 만료된 경우 `-32001 Task not found` 를 JSON-RPC 에러로 응답하고, 클라이언트는 `tasks/get` 으로 스냅샷 조회 후 폴백.
4. 재연결 실패 누적 3 회 시 LOCK-A2A-09 Circuit Breaker OPEN 전환 (아래 §6.1).

### 4.3 백프레셔

- SSE 는 단방향이지만 TCP 레벨에서 소비자의 수신 윈도우가 포화되면 서버 write() 가 블로킹된다.
- 서버는 각 `stream-<uuid>` 별로 in-memory 큐 (최대 64 이벤트) 를 두고, 큐가 포화되면 **`artifact_chunk` 는 절대 silent drop 하지 않고 `task_status` 와 동일하게 block** (발신 측에 backpressure 전파). 무결성이 필요한 청크는 `artifact_chunking.md` §5 NACK/`missing_indices` 재전송 경로로 복구하여 2단 SHA-256 무결성 보장(§3~§4.2)을 유지한다. `task_status` 도 block (상태 변이는 결코 손실되지 않음 — LOCK-A2A-02 상태 머신 무결성 보장).
- `heartbeat` 는 큐 포화 시 drop 허용 (연결 liveness 는 TCP RST 로 감지).

### 4.4 연결 제한

- 에이전트별 동시 SSE 연결 수 상한: 기본 100 (운영 튜닝 대상). 상세명세 §3.2 `load_factor` 에 실시간 반영.
- 초과 시 `-32029 Too many concurrent streams` (비표준 확장 코드) 응답 후 연결 거절. `push_notifications.md` 경로 안내.

---

## 5. agent_streaming 상태 전이 (§6.1 #46)

### 5.1 상태 정의

`agent_streaming` 은 `conversation_state_machine.md` 의 `awaiting_agent` 분기 3 형태 (agent_thinking / agent_delegating / agent_streaming) 중 하나로, 에이전트가 부분 결과를 실시간 방출 중인 상태를 의미한다.

### 5.2 진입 조건

| 전이 | from → to | 트리거 |
|------|-----------|--------|
| T1 | `awaiting_agent` → `agent_streaming` | `tasks/sendSubscribe` 또는 `tasks/resubscribe` 수신 + 에이전트가 `capabilities.streaming=true` |
| T2 | `agent_streaming` → `agent_streaming` | `artifact_chunk` 이벤트 발생 (상태 내부 반복) |
| T3 | `agent_streaming` → `response_ready` | 마지막 `task_status.final=true && state∈{completed}` 이벤트 |
| T4 | `agent_streaming` → `error` | `task_status.state=failed` 또는 Circuit Breaker OPEN |
| T5 | `agent_streaming` → `awaiting_agent` | `task_status.state=input-required` (사용자 개입 대기 재진입) |
| T6 | `agent_streaming` → `follow_up_needed` | 스트리밍 완료 후 후속 사용자 입력이 필요한 도메인 (multi-turn) |

### 5.3 타임 슬롯

- T1 ↔ T3 사이 평균 지연 <= `avg_latency_ms` 메트릭 (05_monitoring/metrics_dashboard.md)
- heartbeat 간격 30 초 → 일정 하에 연결 idle 판별
- T4 Circuit Breaker 자동 복구: OPEN → HALF-OPEN 60 초 (LOCK-A2A-09)

### 5.4 Pydantic 모델 (세션 간 공유)

```python
# conversation_state_machine.md 와 공유. 중복 정의 금지 (§3.4 산출물 품질 필수 구조 #7)
from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field


class AgentSubState(str, Enum):
    """awaiting_agent 하위 분기. conversation_state_machine.md §5.2 정본."""

    THINKING = "agent_thinking"
    DELEGATING = "agent_delegating"
    STREAMING = "agent_streaming"


class StreamTransition(BaseModel):
    """agent_streaming 진입·탈출 이벤트. metrics_dashboard.md 에서 소비."""

    stream_id: str = Field(..., description="stream-<uuid>")
    task_id: str
    session_id: Optional[str] = None
    from_state: str
    to_state: str
    trigger: Literal["T1", "T2", "T3", "T4", "T5", "T6"]
    timestamp: datetime
    reason: Optional[str] = None  # T4 시 Circuit Breaker reason, T5 시 input-required 사유
```

---

## 6. 에러 처리 + Circuit Breaker 연동

### 6.1 LOCK-A2A-09 Circuit Breaker (연속 실패 3 회 → OPEN, 60 초 후 HALF-OPEN)

**LOCK-A2A-09 verbatim 5필드 분리 인용** (AUTHORITY_CHAIN.md §3):

| 필드 | 값 |
|------|------|
| **LOCK ID** | `LOCK-A2A-09` |
| **항목** | Circuit Breaker 연속 실패 임계 |
| **값** | `3회 → OPEN, 60초 후 HALF-OPEN` |
| **출처** | `D2.0-05 §4.4 (ADD-072)` |
| **변경 조건** | `D2.0-05 변경 시만` |

**적용 규칙**:

1. 단일 에이전트 대상 SSE 연결 수립 실패가 연속 **3 회** 발생하면 CB state = OPEN. 이후 60 초간 해당 에이전트로의 `tasks/sendSubscribe` / `tasks/resubscribe` 를 즉시 `-32030 Circuit breaker open` (비표준 확장 코드) 로 거절.
2. 60 초 경과 후 HALF-OPEN: 최초 1 건만 시험 연결 허용. 성공 시 CLOSED 복귀, 실패 시 다시 OPEN + 60 초 누적 대기.
3. **의도적 차이 (CLF-A2A-004 RESOLVED)**: A2A 3 회 임계와 MCP 5 회 임계는 의도적 차이. A2A 에이전트 간 통신은 실패 시 파급 범위가 크고(다중 에이전트 체인 연쇄 실패 가능), 신속한 차단이 필요하므로 보수적 임계값(3 회) 적용. **5 회로 상향 금지**.
4. CB 상태는 `05_monitoring/metrics_dashboard.md` 의 안정성 메트릭 (`error_rate` + CB 상태 별도 게이지) 로 노출.

### 6.2 SSE 재연결 실패 누적

| 누적 실패 | 동작 |
|-----------|------|
| 1 | 지수 백오프 재시도 (§4.2 2단계) |
| 2 | 지수 백오프 재시도 |
| 3 | LOCK-A2A-09 CB OPEN 전환 + Push fallback 안내 (`push_notifications.md`) |
| 4+ | CB OPEN 유지 (대체 에이전트 선택 로직 위임, 02_agent-discovery/agent_selection 참조) |

### 6.3 에러 코드 매핑 (상세명세 §4.4)

| 코드 | 상황 | SSE 복구 |
|------|------|----------|
| `-32001` | Task not found (재구독 버퍼 만료) | `tasks/get` 스냅샷 조회 후 폴백 |
| `-32003` | Push notification not supported | `push_notifications.md` 에서 SSE 전환 안내 (역방향 폴백) |
| `-32004` | Unsupported operation | 에이전트 카드 재조회 후 대체 에이전트 선택 |
| `-32030` | Circuit breaker open (비표준 확장) | LOCK-A2A-09 60 초 대기 + 대체 경로 |
| `-32029` | Too many concurrent streams (비표준 확장) | Push 폴백 또는 `retry-after` 5 초 |

### 6.4 로깅 포맷 (R-01-7 structured JSON, 중첩 구조 필수)

```json
{
  "trace_id": "trace-uuid",
  "error": {
    "code": "-32030",
    "message": "Circuit breaker open",
    "source": "streaming_sse.cb_guard"
  },
  "context": {
    "stream_id": "stream-uuid",
    "task_id": "task-uuid",
    "agent_id": "agent:code-reviewer-001",
    "attempt": 3,
    "cb_state": "OPEN",
    "cb_open_since": "2026-04-22T10:12:00Z"
  },
  "recovery": {
    "strategy": "push_fallback",
    "next_attempt_after_s": 60,
    "fallback_endpoint": "/a2a/tasks (method=tasks/pushNotification/set)"
  }
}
```

---

## 7. 컨텍스트 윈도우 압축 (LOCK-A2A-05)

### 7.1 LOCK-A2A-05 verbatim 5필드 분리 인용

| 필드 | 값 |
|------|------|
| **LOCK ID** | `LOCK-A2A-05` |
| **항목** | 컨텍스트 윈도우 한계 |
| **값** | `모델별 max_tokens 준수, 초과 시 압축` |
| **출처** | `D2.0-05 §12.13` |
| **변경 조건** | `모델 변경 시 갱신` |

### 7.2 스트리밍 중 트리거 규칙

1. `artifact_chunk` 누적 토큰 수가 에이전트 모델의 `max_tokens × 0.85` 초과 시 압축 트리거.
2. 서버는 다음 `artifact_chunk` 대신 `task_status.metadata.context_compressed=true` 플래그와 함께 압축 결과를 단일 `artifact_chunk` 로 방출.
3. 압축 알고리즘은 에이전트 내부 결정 (요약 체인 / 청킹 기반 MapReduce) — 본 문서 scope 외 (multi_turn_sessions.md §컨텍스트 관리 참조).
4. 스트리밍 중 LOCK-A2A-05 를 위반하여 모델 한계 초과 요청 발생 시 `-32005 Content type not supported` 로 폴백 (상세명세 §4.4).

---

## 8. Phase 3 테스트 시나리오 (10 건 이상)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|----------|----------|----------|
| TS-01 | 정상 SSE 소비 (short task) | `tasks/sendSubscribe` 1 회 호출, 3 초 내 완료 | `task_status: submitted → working → completed (final=true)` 순서, `artifact_chunk` 1~N 건 수신 |
| TS-02 | 정상 SSE 소비 (long task) | `tasks/sendSubscribe` 후 120 초 실행 | heartbeat 4 회(30s 간격) + artifact_chunk 분할 수신 |
| TS-03 | 타임아웃 경계 | 299 초 지속 스트림 | 정상 종료 (300 초 내) |
| TS-04 | 타임아웃 초과 | 301 초 지속 스트림 | 서버 강제 close, 클라이언트 `tasks/resubscribe` 성공 |
| TS-05 | 재연결 성공 (버퍼 내) | 네트워크 단절 5 초 후 `last-event-id` resubscribe | 유실 0 이벤트, 지수 백오프 1 회 |
| TS-06 | 재연결 실패 (버퍼 만료) | 단절 7 분 후 resubscribe | `-32001 Task not found` → `tasks/get` 스냅샷 폴백 |
| TS-07 | Circuit Breaker 개방 | 대상 에이전트 강제 다운 → 3 회 연결 실패 | CB OPEN, 4 번째 시도 `-32030`, 60 초 후 HALF-OPEN 시험 연결 |
| TS-08 | Circuit Breaker 복구 | OPEN 후 60 초 대기 + 에이전트 복구 | HALF-OPEN 1 건 성공 → CLOSED 복귀 |
| TS-09 | 백프레셔 (artifact drop) | 클라이언트 의도적 slow consumer | `artifact_chunk` drop 발생, `metadata.dropped_artifacts=N` 증가, `task_status` 는 손실 0 |
| TS-10 | 컨텍스트 압축 트리거 | 모델 max_tokens 의 85% 초과 생성 | `task_status.metadata.context_compressed=true` + 단일 `artifact_chunk` 로 압축 결과 방출 |
| TS-11 | input-required 분기 | 에이전트가 추가 입력 요청 | `task_status.state=input-required, final=true` → 사용자 `tasks/send` 후 SSE 재개 또는 재구독 |
| TS-12 | 동시 연결 상한 | 동일 에이전트에 101 개 SSE | 101 번째 요청 `-32029 Too many concurrent streams` → Push fallback 안내 |
| TS-13 | 종료 상태 6 종 분기 | completed / failed / canceled 각 시나리오 주입 | 각 경로 정상 종료, `final=true` 표시 |
| TS-14 | MoA proposer 병렬 스트림 | MoA proposer 3 개 동시 SSE | 3 개 스트림 독립 유지, aggregator 집계 단계에서 progress 이벤트 수집 (moa_pattern.md 연계) |
| TS-15 | Heartbeat idle 검증 | 60 초 idle (data 없음) | heartbeat 2 회 수신, 연결 유지 |

---

## 9. LOCK 인용 표 (5필드 분리 강제 — 3-5/3-6/3-7 선례 계승)

| LOCK ID | 항목 | 값 | 출처 | 변경 조건 |
|---------|------|-----|------|----------|
| LOCK-A2A-01 | JSON-RPC 2.0 프로토콜 버전 | `"jsonrpc": "2.0"` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-02 | Task 상태 열거형 | `submitted\|working\|input-required\|completed\|failed\|canceled` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-05 | 컨텍스트 윈도우 한계 | 모델별 max_tokens 준수, 초과 시 압축 | D2.0-05 §12.13 | 모델 변경 시 갱신 |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | D2.0-05 §4.4 (ADD-072) | D2.0-05 변경 시만 |

- LOCK-A2A-01 적용 위치: §2.2 JSON-RPC 요청 스키마, §3.1 data 직렬화
- LOCK-A2A-02 적용 위치: §3.1 state 필드, §3.4 종료 트리거, §5.2 전이 T1~T6 조건
- LOCK-A2A-05 적용 위치: §7 컨텍스트 윈도우 압축 트리거
- LOCK-A2A-09 적용 위치: §6.1 Circuit Breaker 연동

---

## 10. 세션 간 인터페이스 cross-check

| 항목 | 대상 산출물 | 일치 항목 |
|------|------------|----------|
| `AgentSubState` enum (3 상태) | `conversation_state_machine.md` §5.2 | `agent_thinking` / `agent_delegating` / `agent_streaming` 3 상태 식별자 verbatim |
| `StreamTransition` Pydantic | `05_monitoring/metrics_dashboard.md` | `stream_id` / `task_id` / `from_state` / `to_state` 필드 재사용 |
| `TaskStatusEvent` | 상세명세 §2.2 | `state` / `timestamp` / `final` / `progress` / `metadata` 필드 |
| `TaskArtifactEvent` | 상세명세 §2.2 | `artifact.name` / `artifact.parts[]` / `last_chunk` 필드 |
| `PushNotificationConfig` | `push_notifications.md` | SSE → Push 폴백 시 재사용 (§6.3 `-32003`) |
| Circuit Breaker 임계값 | `moa_pattern.md` (proposer 장애) + `metrics_dashboard.md` | LOCK-A2A-09 3 회 / 60 초 verbatim |

---

## 11. 변경 이력

| 날짜 | 변경자 | 내용 |
|------|--------|------|
| 2026-04-22 | STAGE 7 3-8 STEP_B #2a (parent-executed) | V2-Phase 2 NEW 최초 작성 (P2-1 SSE 시범 세션, exit gate "SSE 완성" 직접 충족) |
