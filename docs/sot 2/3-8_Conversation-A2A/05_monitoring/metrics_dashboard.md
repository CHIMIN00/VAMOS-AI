# A2A 모니터링 대시보드 메트릭 — 05_monitoring/

> **문서 위치**: `sot 2/3-8_Conversation-A2A/05_monitoring/metrics_dashboard.md`
> **정본 위계 Level 4 (구현 상세)** — 상위: 상세명세 §6.1 A2AMetrics TypeScript interface 정본 (L475~L508) + D2.0-05 §4.4 Circuit Breaker (LOCK-A2A-09 정본) + 종합계획서 §6.3 v12_C09b_117 OTel 통합 (L1591) + §7.3 P2-5 블록 (L1159~L1196)
> **Phase**: Phase 2 V2-Phase 2 (P2-5 세션, STEP_B #2b)
> **작성일**: 2026-04-22
> **최종 갱신**: 2026-04-22
> **Status**: V2-Phase 2 DRAFT (L3)
> **버전**: v1.0
> **대응 Phase 2→3 게이트**: **"모니터링 메트릭 정의" 직접 충족** (종합계획서 §7 Phase 2→3 전환 게이트 3번 항목)
> **LOCK 직접 보호**: LOCK-A2A-09 Circuit Breaker (CB 상태 게이지 메트릭)
> **LOCK 간접 참조**: LOCK-A2A-02 Task 상태 열거형 (tasks_by_state 6 상태) / LOCK-A2A-08 Agent Mode (MoA 모니터링) / LOCK-A2A-07 JWT delegation chain 깊이 3 (위임 깊이 히스토그램)

---

## 교차 참조

- **구조화 종합계획서**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_구조화_종합계획서.md`
  - §3.4 LOCK-A2A-09 (Circuit Breaker 메트릭 정본)
  - §6.1 #51 트래픽 메트릭 (total_tasks_24h, active_sessions, tasks_by_state) (L307)
  - §6.1 #52 성능 메트릭 (avg / p50 / p95 / p99 latency) (L308)
  - §6.1 #53 안정성 메트릭 (success_rate, error_rate, timeout_rate) (L309)
  - §6.1 #54 에이전트별 메트릭 (status, tasks_processed, load_factor) (L310)
  - §6.3 v12_C09b_117 A2A 모니터링/관측 (OTel): W3C TraceContext + span `a2a.task.{method}` + distributed tracing 연동 (L1591)
  - §6.3 v12_C03_037 A2A Test Framework (L1592, 본 메트릭은 테스트 관측 대상)
  - §6.3 v12_C12_115 VBS-12 에이전트 협업 벤치마크 (L1596, Phase 3 이월)
  - §7.3 P2-5 블록 (L1159~L1196) — 산출물 본 파일 `metrics_dashboard.md`
- **상세명세 A2AMetrics 정본**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONVERSATION_A2A_상세명세.md` §6.1 L475~L508 (TypeScript interface: `total_tasks_24h`, `active_sessions`, `tasks_by_state`, `tasks_by_method`, `avg/p50/p95/p99_latency_ms`, `success_rate`, `error_rate`, `timeout_rate`, `retry_rate`, `agents[].{agent_id, status, tasks_processed, avg_response_time_ms, error_count, load_factor}`) + §6.2 A2ATestCase (테스트 프레임워크) + §6.3 에러 핸들링
- **권한 체계**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\AUTHORITY_CHAIN.md` §3 LOCK-A2A-02 row (L57) + LOCK-A2A-07 row (L62) + LOCK-A2A-09 row (L64) verbatim 5필드
- **충돌 기록**: `D:\VAMOS\docs\sot 2\3-8_Conversation-A2A\CONFLICT_LOG.md` §CLF-A2A-004 (CB 3회 vs MCP 5회 의도적 차이, 5회 상향 금지)
- **상위 아키텍처 정본**: `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md` §4.4 Circuit Breaker (ADD-072, LOCK-A2A-09 정본) + §12.13 컨텍스트 관리 (LOCK-A2A-05 정본 간접)
- **상위 SoT (벤치마크)**: `D:\VAMOS\docs\sot\STEP7-B_대화프로세스_작업가이드.md` — §F L609 #53 자기검증 루프 (VAMOS 설계) + L610 #54 환각 감지 (VAMOS 설계) + L611 #55 EVX 검증 체인 (VAMOS 독자) + L614 #58 비용 실시간 모니터링 (VAMOS 독자) + §I L1006 #79 Rate Limiting/Throttling (VAMOS Cost Gate) + §E L622 #61 스트리밍 출력 (VAMOS 설계만). **CLF-A2A-003 규칙 준수**: STEP7-B 는 시중 AI 벤치마크, D2.0-05 가 아키텍처 정본.
- **peer V2 (04_advanced-features/)**: `streaming_sse.md` §6.1 CB 메트릭 + §5.3 agent_streaming active_sessions / `push_notifications.md` §6.2 CB + 전송 성공률 / `multi_turn_sessions.md` §3.1 active_sessions + 세션 상한 / `conversation_state_machine.md` §4 상태 전이 카운터 / `moa_pattern.md` §6 비용 매트릭스 + §7.5 로깅 컨텍스트

---

## 1. 개요

### 1.1 목적

A2A 통신의 **운영 가시성 (Observability)** 을 확보하기 위한 4종 메트릭 (트래픽 / 성능 / 안정성 / 에이전트별) 을 정의하고, OpenTelemetry (OTel) 기반 분산 트레이싱을 통합한다. 본 문서는 상세명세 §6.1 `A2AMetrics` TypeScript interface 정본을 근거로, VAMOS A2A 환경에서의 L3 구현 설계를 확정한다.

### 1.2 범위

- 4종 메트릭 정의 (Pydantic + TypeScript interface)
- Prometheus 메트릭 네이밍 + 라벨 (a2a_tasks_total, a2a_latency_seconds, a2a_errors_total)
- LOCK-A2A-09 Circuit Breaker 상태 게이지
- OpenTelemetry 통합 (W3C TraceContext + span `a2a.task.{method}` + 8 method 전수 + sampling 전략)
- Grafana 대시보드 JSON 구조 (5 패널)
- 알림 규칙 (error_rate > 5%, p99 > 5s, agent down)
- peer cross-ref (04_advanced-features V2 5 파일)

### 1.3 범위 외 (Phase 3 이월)

- A2ATestCase 테스트 프레임워크 (별도 파일 `test_framework.md` 에서 정의 — Phase 3 이월)
- VBS-12 에이전트 협업 벤치마크 (v12_C12_115, Phase 3 이월 — _index.md 항목 9)
- 분산 추적 백엔드 선택 (Jaeger / Tempo / Zipkin — Phase 3 배포 결정)
- 장기 메트릭 저장 전략 (Retention, Downsampling — Phase 3 운영 결정)

---

## 2. A2AMetrics 정본 인터페이스 (상세명세 §6.1 L475~L508 verbatim)

### 2.1 TypeScript 정본 (상세명세 §6.1 verbatim)

```typescript
interface A2AMetrics {
  // 트래픽 메트릭
  total_tasks_24h: number;
  active_sessions: number;
  tasks_by_state: Record<TaskState, number>;
  tasks_by_method: Record<string, number>;

  // 성능 메트릭
  avg_latency_ms: number;
  p50_latency_ms: number;
  p95_latency_ms: number;
  p99_latency_ms: number;

  // 안정성 메트릭
  success_rate: number;           // 0.0 ~ 1.0
  error_rate: number;
  timeout_rate: number;
  retry_rate: number;

  // 에이전트별 메트릭
  agents: Array<{
    agent_id: string;
    status: "healthy" | "degraded" | "down";
    tasks_processed: number;
    avg_response_time_ms: number;
    error_count: number;
    load_factor: number;
  }>;
}
```

> **정본 소유**: 본 interface 는 `CONVERSATION_A2A_상세명세.md §6.1` (L475~L508) 의 수정 없는 재인용이다. 본 V2 문서에서는 interface 자체는 변경 금지 (정본 소유권 준수), 아래 §3~§9 에서 L3 설계 상세 (Pydantic 모델 / 집계 공식 / LOCK 연동 / OTel 통합 / 알림 규칙) 를 추가 정의한다.

### 2.2 Pydantic 공용 구조 (VAMOS 서버측 구현)

```python
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

class AgentHealthStatus(str, Enum):
    """에이전트 헬스 상태 (상세명세 §6.1 agents[].status 3-state)"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    DOWN = "down"


class AgentMetric(BaseModel):
    """에이전트별 단건 메트릭 (§6.1 agents[] 내부 오브젝트)"""
    agent_id: str
    status: AgentHealthStatus
    tasks_processed: int = Field(ge=0)
    avg_response_time_ms: float = Field(ge=0)
    error_count: int = Field(ge=0)
    load_factor: float = Field(ge=0.0, le=1.0)  # 0=idle, 1=saturated


class TrafficMetrics(BaseModel):
    """트래픽 메트릭 (§6.1 A2AMetrics.트래픽 블록 4 필드)"""
    total_tasks_24h: int = Field(ge=0)
    active_sessions: int = Field(ge=0)
    # LOCK-A2A-02 Task 상태 열거형 6 상태 verbatim
    tasks_by_state: dict[str, int]    # keys ∈ {submitted, working, input-required, completed, failed, canceled}
    tasks_by_method: dict[str, int]   # keys ∈ 8 A2A methods (§3.2)


class PerformanceMetrics(BaseModel):
    """성능 메트릭 (§6.1 A2AMetrics.성능 블록 4 필드)"""
    avg_latency_ms: float = Field(ge=0)
    p50_latency_ms: float = Field(ge=0)
    p95_latency_ms: float = Field(ge=0)
    p99_latency_ms: float = Field(ge=0)


class ReliabilityMetrics(BaseModel):
    """안정성 메트릭 (§6.1 A2AMetrics.안정성 블록 4 필드)"""
    success_rate: float = Field(ge=0.0, le=1.0)
    error_rate: float = Field(ge=0.0, le=1.0)
    timeout_rate: float = Field(ge=0.0, le=1.0)
    retry_rate: float = Field(ge=0.0, le=1.0)


class A2AMetricsSnapshot(BaseModel):
    """A2A 전체 메트릭 스냅샷 (상세명세 §6.1 TypeScript interface 대응 Pydantic 정본)"""
    timestamp: str              # ISO 8601 UTC
    traffic: TrafficMetrics
    performance: PerformanceMetrics
    reliability: ReliabilityMetrics
    agents: list[AgentMetric]
    # VAMOS 확장 (LOCK-A2A-09 CB 상태 추가)
    cb_state_per_agent: dict[str, Literal["CLOSED", "OPEN", "HALF-OPEN"]]
```

---

## 3. 4종 메트릭 상세 정의

### 3.1 트래픽 메트릭 (§6.1 #51)

| 메트릭 | 타입 | 의미 | 집계 공식 |
|--------|------|------|----------|
| `total_tasks_24h` | Counter | 최근 24 시간 누적 Task 수 | `sum(tasks_created[24h])` |
| `active_sessions` | Gauge | 현재 활성 세션 수 (multi_turn_sessions.md §3.1 SessionState ∈ {active, awaiting_input}) | `count(sessions WHERE state IN active_set)` |
| `tasks_by_state` | Gauge | **LOCK-A2A-02 Task 상태별 6 상태** 카운트 (submitted/working/input-required/completed/failed/canceled) | `group_by(state).count()` |
| `tasks_by_method` | Counter | A2A JSON-RPC method 별 호출 수 (8 method, §3.2) | `group_by(method).count()` |

### 3.2 A2A method 8종 verbatim (tasks_by_method keys)

```
tasks/send
tasks/sendSubscribe
tasks/get
tasks/cancel
tasks/pushNotification/set
tasks/pushNotification/get
tasks/resubscribe
agent/authenticatedExtendedCard
```

- 출처: 상세명세 §2.3 Method 목록. OTel span 이름 생성에 그대로 사용 (§5 참조).

### 3.3 성능 메트릭 (§6.1 #52)

| 메트릭 | 타입 | 의미 | 집계 공식 |
|--------|------|------|----------|
| `avg_latency_ms` | Histogram | Task 평균 소요 시간 | `sum(latency) / count(latency)` |
| `p50_latency_ms` | Histogram | 50 분위 (중앙값) | `quantile(0.50, latency)` |
| `p95_latency_ms` | Histogram | 95 분위 | `quantile(0.95, latency)` |
| `p99_latency_ms` | Histogram | 99 분위 | `quantile(0.99, latency)` |

- 측정 구간: `tasks/send` 요청 수신 ~ `TaskResult` 응답 반환 (wall-clock, SSE 는 `completed final=true` 도달 시점).
- Prometheus 히스토그램 버킷: `[10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 30000, 120000]` ms (MoA 타임아웃 상한 120s 까지 커버, `moa_pattern.md` §3.1).

### 3.4 안정성 메트릭 (§6.1 #53)

| 메트릭 | 타입 | 의미 | 집계 공식 |
|--------|------|------|----------|
| `success_rate` | Gauge | 완료 Task / 전체 Task (최근 24h) | `count(state=completed) / count(total)` |
| `error_rate` | Gauge | 실패 Task / 전체 Task | `count(state=failed) / count(total)` |
| `timeout_rate` | Gauge | 타임아웃 에러 / 전체 Task | `count(error_code IN timeout_set) / count(total)` |
| `retry_rate` | Gauge | 재시도 발생 Task / 전체 Task | `count(retry_count > 0) / count(total)` |

- 목표 기준 (알림 임계, §7 참조): `success_rate ≥ 0.95` / `error_rate ≤ 0.05` / `timeout_rate ≤ 0.02` / `retry_rate ≤ 0.10`
- Circuit Breaker 발동률 별도 게이지 (§4 LOCK-A2A-09 연동).

### 3.5 에이전트별 메트릭 (§6.1 #54)

| 메트릭 | 타입 | 의미 |
|--------|------|------|
| `agent_id` | Label | 에이전트 식별자 (e.g., `agent:code-reviewer-001`) |
| `status` | Gauge Enum | 3-state: `healthy` (정상) / `degraded` (부분 장애) / `down` (전면 장애) |
| `tasks_processed` | Counter | 해당 에이전트가 처리 완료한 Task 수 |
| `avg_response_time_ms` | Histogram | 에이전트별 평균 응답 시간 |
| `error_count` | Counter | 해당 에이전트의 누적 에러 수 |
| `load_factor` | Gauge | 부하율 (0=idle ~ 1=saturated), 02_agent-discovery/agent_selection 가중 스코어링 입력 |

- `status` 판정 규칙 (heuristic, Phase 3 에서 튜닝):
  - `healthy`: `error_rate ≤ 5%` AND `load_factor ≤ 0.8`
  - `degraded`: `error_rate IN (5%, 20%]` OR `load_factor IN (0.8, 0.95]`
  - `down`: `error_rate > 20%` OR `load_factor > 0.95` OR CB state = OPEN

---

## 4. LOCK-A2A-09 Circuit Breaker 메트릭

### 4.1 LOCK-A2A-09 verbatim 5필드 분리 인용 (AUTHORITY_CHAIN.md §3 L64)

| 필드 | 값 |
|------|------|
| **LOCK ID** | `LOCK-A2A-09` |
| **항목** | Circuit Breaker 연속 실패 임계 |
| **값** | `3회 → OPEN, 60초 후 HALF-OPEN` |
| **출처** | `D2.0-05 §4.4 (ADD-072)` |
| **변경 조건** | `D2.0-05 변경 시만` |

### 4.2 CB 게이지 메트릭 (VAMOS 확장)

| 메트릭 | 타입 | 의미 |
|--------|------|------|
| `cb_state_per_agent{agent_id}` | Gauge Enum | 에이전트별 CB 상태 3-state (CLOSED=0 / OPEN=1 / HALF-OPEN=2) |
| `cb_open_total{agent_id}` | Counter | CB 가 OPEN 으로 전이된 누적 횟수 |
| `cb_half_open_total{agent_id}` | Counter | CB 가 HALF-OPEN 으로 진입한 누적 횟수 (복구 시도) |
| `cb_open_duration_s{agent_id}` | Histogram | CB OPEN 지속 시간 분포 (60 초 단일 bucket 중심) |
| `cb_trip_reason{agent_id, reason}` | Counter | CB 개방 이유별 분류 (connection_failed / timeout / sse_disconnect / moa_proposer_failed) |

### 4.3 CB ↔ peer V2 연동

- `streaming_sse.md` §6.1 — 단일 에이전트 SSE 연결 실패 3회 시 CB OPEN → `cb_trip_reason="sse_disconnect"`.
- `push_notifications.md` §6.2 — Push 전송 실패 3회 시 CB OPEN → `cb_trip_reason="push_failed"`.
- `moa_pattern.md` §7.1 — proposer 별 CB 독립 관리 (부분 fallback) → `cb_trip_reason="moa_proposer_failed"`.
- **의도적 차이 (CLF-A2A-004 RESOLVED)**: A2A 3회 임계와 MCP 5회 임계는 의도적 차이. A2A 에이전트 간 통신은 실패 시 파급 범위가 크고 신속한 차단 필요 (보수적 임계값 3회). **5 회로 상향 금지** — `cb_state_per_agent` 게이지 알림 임계도 3회 기준 유지.

### 4.4 알림 규칙 (CB)

- `cb_state_per_agent = 1 (OPEN)` 발생 시 즉시 PagerDuty / Slack 알림 (매 에이전트당 60s 쿨다운).
- `cb_open_total` 24시간 내 3회 이상 누적 시 해당 에이전트 degraded 강제 전이 + 02_agent-discovery/agent_selection 에서 제외 권고 (Phase 3 자동 격리 정책 이월).

---

## 5. OpenTelemetry 통합 (종합계획서 §6.3 v12_C09b_117 L1591)

### 5.1 trace context propagation (W3C TraceContext 표준)

- 모든 JSON-RPC 2.0 요청 헤더에 `traceparent` (W3C TraceContext) + `tracestate` 주입.
- A2A 서버는 `traceparent` 파싱 후 span 생성 시 parent trace 로 설정 (cross-service trace 보존).
- 출처: 종합계획서 §6.3 L1591 verbatim "**OpenTelemetry 통합**: trace context propagation (W3C TraceContext), span naming (`a2a.task.{method}`), distributed tracing 연동".

### 5.2 Span naming (§6.3 L1591 verbatim)

Span 명칭은 `a2a.task.{method}` 로 통일. 8 method (§3.2) 전수 적용:

```
a2a.task.tasks/send
a2a.task.tasks/sendSubscribe
a2a.task.tasks/get
a2a.task.tasks/cancel
a2a.task.tasks/pushNotification/set
a2a.task.tasks/pushNotification/get
a2a.task.tasks/resubscribe
a2a.task.agent/authenticatedExtendedCard
```

### 5.3 Span Attributes (OTel 표준 + A2A 확장)

| Attribute | 의미 | 예시 |
|-----------|------|------|
| `a2a.task.id` | Task UUID | `task-7b3c...` |
| `a2a.session.id` | Session UUID (multi_turn_sessions.md §3.1) | `session-9f2a...` |
| `a2a.agent.id` | 대상 에이전트 식별자 | `agent:code-reviewer-001` |
| `a2a.delegation.depth` | 위임 체인 깊이 (LOCK-A2A-07 ≤3) | `0` ~ `3` |
| `a2a.cb.state` | 호출 시점 CB 상태 | `CLOSED` / `OPEN` / `HALF-OPEN` |
| `a2a.moa.proposal_count` | MoA proposer 수 (R-11-6 2~5) | `2` ~ `5` |
| `a2a.moa.aggregation_mode` | MoA 집계 모드 | `majority_voting` / `weighted_average` / `consensus` |
| `a2a.moa.total_cost_usd` | MoA 총 비용 | `0.045` |
| `a2a.stream.chunk_count` | SSE artifact_chunk 개수 | `12` |
| `a2a.stream.dropped_artifacts` | backpressure drop 수 | `0` |

### 5.4 Sampling 전략

- **기본**: head-based sampling (ParentBased + TraceIdRatioBased 10%) — 일반 트래픽.
- **에러 경로**: tail-based sampling 강제 100% — `error_code ≠ null` OR `cb.state IN {OPEN, HALF-OPEN}` OR `status=failed` 발생 시 해당 trace 100% 보존.
- **safety-critical (Consensus MoA)**: 100% sampling 강제 (`a2a.moa.aggregation_mode=consensus` 조건).

### 5.5 LOCK-A2A-07 교차 참조 (delegation 깊이 모니터링)

**LOCK-A2A-07 verbatim 5필드 분리 인용** (AUTHORITY_CHAIN.md §3 L62):

| 필드 | 값 |
|------|------|
| **LOCK ID** | `LOCK-A2A-07` |
| **항목** | JWT delegation chain 최대 깊이 |
| **값** | `3` |
| **출처** | `가이드 §4.3/#11` |
| **변경 조건** | `보안 검토 후만 변경 (LOCK-AT-004 교차: 위임 깊이 최대 3단계 동일)` |

- `a2a.delegation.depth` 히스토그램 버킷: `[0, 1, 2, 3]` (4 bucket, depth=3 초과 시 별도 카운터 `a2a.delegation.depth_exceeded_total` 증가).
- 알림: `a2a.delegation.depth_exceeded_total` 증가 감지 시 즉시 보안팀 알림 (LOCK-AT-013 privilege escalation 방지 준수).

---

## 6. Prometheus 메트릭 네이밍 (_index.md 항목 2)

### 6.1 표준 메트릭 명명

```
# 트래픽
a2a_tasks_total{state, method, agent_id}                  # Counter
a2a_active_sessions                                       # Gauge

# 성능
a2a_latency_seconds{method, agent_id}                     # Histogram (buckets 위 §3.3)

# 안정성
a2a_errors_total{error_code, method, agent_id}            # Counter
a2a_timeouts_total{method, agent_id}                      # Counter
a2a_retries_total{method, agent_id}                       # Counter

# 에이전트별
a2a_agent_status{agent_id, status}                        # Gauge (3-state)
a2a_agent_load_factor{agent_id}                           # Gauge (0.0~1.0)

# Circuit Breaker
a2a_cb_state{agent_id}                                    # Gauge (0=CLOSED, 1=OPEN, 2=HALF-OPEN)
a2a_cb_open_total{agent_id, reason}                       # Counter

# MoA (moa_pattern.md 연계)
a2a_moa_executions_total{aggregation_mode}                # Counter
a2a_moa_proposal_count                                     # Histogram (2~5)
a2a_moa_cost_usd                                           # Histogram

# OTel 통합
a2a_delegation_depth                                       # Histogram (0~3)
a2a_delegation_depth_exceeded_total                        # Counter
```

### 6.2 라벨 카디널리티 제한

- `agent_id`: 최대 100 고유 값 (VAMOS 초기 배포 규모). 초과 시 bucket 라벨 추가 (`agent_group`).
- `method`: 고정 8 값 (§3.2).
- `state`: 고정 6 값 (LOCK-A2A-02).
- `error_code`: 최대 20 고유 값 (상세명세 §4.4 에러 코드 집합 + CB).

---

## 7. 알림 규칙 (_index.md 항목 4)

### 7.1 Critical 알림 (PagerDuty 즉시)

| 알림 | 조건 | 쿨다운 |
|------|------|--------|
| **`CB_OPEN_DETECTED`** | `a2a_cb_state == 1` (OPEN) 발생 | 60s per agent_id |
| **`AGENT_DOWN`** | `a2a_agent_status{status="down"} == 1` 5분 지속 | 5m per agent_id |
| **`ERROR_RATE_HIGH`** | `rate(a2a_errors_total[5m]) / rate(a2a_tasks_total[5m]) > 0.05` | 10m |
| **`P99_LATENCY_HIGH`** | `histogram_quantile(0.99, a2a_latency_seconds_bucket[5m]) > 5` | 10m |
| **`DELEGATION_DEPTH_EXCEEDED`** | `increase(a2a_delegation_depth_exceeded_total[5m]) > 0` | 즉시 보안팀 |

### 7.2 Warning 알림 (Slack)

| 알림 | 조건 | 쿨다운 |
|------|------|--------|
| `TIMEOUT_RATE_ELEVATED` | `timeout_rate > 0.02` 10분 지속 | 30m |
| `RETRY_RATE_ELEVATED` | `retry_rate > 0.10` 10분 지속 | 30m |
| `MOA_COST_SPIKE` | `rate(a2a_moa_cost_usd_sum[10m]) > baseline * 2` | 30m |
| `AGENT_DEGRADED` | `a2a_agent_status{status="degraded"} == 1` 10분 지속 | 1h |

---

## 8. Grafana 대시보드 JSON 구조 (_index.md 항목 3)

### 8.1 패널 구성 (5 패널)

1. **트래픽 개요**: `total_tasks_24h` 선 그래프 + `active_sessions` 게이지 + `tasks_by_state` 스택 차트 + `tasks_by_method` 파이 차트
2. **성능 분포**: p50/p95/p99 latency 선 그래프 (overlay) + avg latency + 히스토그램 heatmap
3. **안정성 보드**: success_rate / error_rate / timeout_rate / retry_rate 4-up 단일값 + 5분 rate 선 그래프
4. **에이전트 상태**: agent_id 별 status 타일 (3-color) + load_factor 게이지 매트릭스 + tasks_processed 순위 바차트
5. **CB + MoA + 위임**: cb_state_per_agent heatmap + moa_proposal_count 히스토그램 + a2a_delegation_depth 히스토그램

### 8.2 대시보드 표준 필터

- `agent_id` (drop-down, 전체 / 단일 선택)
- `method` (drop-down, 전체 / 단일 method)
- `time_range` (기본 24h)

### 8.3 Phase 3 이월

- 대시보드 JSON 파일 정의 (Grafana provisioning YAML) — Phase 3 배포 단계 (_index.md 항목 3 "PLAN" 상태)
- 대시보드 사용자 권한 (읽기/편집) 분리

---

## 9. 로깅 포맷 (R-01-7 structured JSON, 중첩 구조 필수)

```json
{
  "trace_id": "trace-uuid",
  "error": {
    "code": "-32030",
    "message": "Circuit breaker open",
    "source": "metrics.cb_collector"
  },
  "context": {
    "metric_name": "a2a_cb_state",
    "agent_id": "agent:code-reviewer-001",
    "cb_state_transition": "CLOSED→OPEN",
    "cb_open_since": "2026-04-22T10:15:00Z",
    "trip_reason": "sse_disconnect",
    "consecutive_failures": 3
  },
  "recovery": {
    "strategy": "monitor_half_open",
    "next_evaluation_s": 60,
    "alert_channel": "pagerduty"
  }
}
```

---

## 10. Phase 3 테스트 시나리오 (15 건)

| # | 시나리오 | 주입 방법 | 기대 결과 |
|---|----------|----------|----------|
| MET-01 | 트래픽 메트릭 정확성 | 100 Task 각기 다른 state 로 종료 | `tasks_by_state` 합계 = 100, 각 6 state 합 = 100 |
| MET-02 | p99 Latency 계산 | 1000 Task, 마지막 10 개 > 5s | `p99_latency_ms` ≥ 5000 |
| MET-03 | success_rate 경계 | 95 성공 / 5 실패 | `success_rate = 0.95`, 알림 없음 |
| MET-04 | error_rate 알림 트리거 | error_rate 6% 10분 지속 | `ERROR_RATE_HIGH` 알림 발화 |
| MET-05 | 에이전트 down 감지 | agent_id 5분 응답 없음 | `status=down` + `AGENT_DOWN` 알림 |
| MET-06 | load_factor 포화 | agent load = 1.0 | `status=down` 강제 전이, agent_selection 제외 |
| MET-07 | CB OPEN 알림 | 특정 에이전트 3회 연속 실패 | `cb_state_per_agent=1` + `CB_OPEN_DETECTED` 알림, 60s 쿨다운 |
| MET-08 | CB HALF-OPEN 전이 | CB OPEN 60초 후 | `cb_half_open_total` +1, 알림 없음 |
| MET-09 | MoA 비용 스파이크 | MoA consensus 5-proposer 연속 실행 | `MOA_COST_SPIKE` 경고, `a2a_moa_cost_usd_sum` 증가 |
| MET-10 | OTel trace 전파 | 외부 traceparent 헤더 포함 요청 | span `a2a.task.tasks/send` 가 parent trace 에 연결 |
| MET-11 | OTel span attributes | MoA 실행 trace | `a2a.moa.proposal_count` / `aggregation_mode` / `total_cost_usd` 전수 기록 |
| MET-12 | delegation depth 초과 | 위임 체인 4 단계 시도 | `a2a_delegation_depth_exceeded_total` +1 + 보안팀 알림 (LOCK-A2A-07 / LOCK-AT-013) |
| MET-13 | Tail-based sampling 에러 | error_code=-32030 발생 | 해당 trace 100% 보존 (일반 10% vs error 100%) |
| MET-14 | Consensus MoA 100% sampling | `aggregation_mode=consensus` 호출 | 해당 trace 100% 보존 (safety-critical 강제) |
| MET-15 | 라벨 카디널리티 방어 | agent_id 150 고유 값 주입 | 100 초과분은 `agent_group` bucket 라벨로 집계, 전체 시계열 폭증 방지 |

---

## 11. LOCK 인용 표 (5필드 분리 강제 — 3-5/3-6/3-7/3-8 #2a/P2-4 선례 계승)

| LOCK ID | 항목 | 값 | 출처 | 변경 조건 |
|---------|------|-----|------|----------|
| LOCK-A2A-02 | Task 상태 열거형 | `submitted\|working\|input-required\|completed\|failed\|canceled` | Google A2A Spec | 스펙 업데이트 시 검토 |
| LOCK-A2A-07 | JWT delegation chain 최대 깊이 | 3 | 가이드 §4.3/#11 | 보안 검토 후만 변경 *(LOCK-AT-004 교차: 위임 깊이 최대 3단계 동일)* |
| LOCK-A2A-09 | Circuit Breaker 연속 실패 임계 | 3회 → OPEN, 60초 후 HALF-OPEN | D2.0-05 §4.4 (ADD-072) | D2.0-05 변경 시만 |

- LOCK-A2A-02 적용 위치: §3.1 tasks_by_state 6 상태 verbatim + §2.2 Pydantic dict keys comment + §6.2 라벨 카디널리티 6 state 제한
- LOCK-A2A-07 적용 위치: §5.5 `a2a.delegation.depth` 히스토그램 버킷 [0,1,2,3] + `a2a.delegation.depth_exceeded_total` 카운터 + `DELEGATION_DEPTH_EXCEEDED` Critical 알림
- LOCK-A2A-09 적용 위치: §4 전체 CB 게이지 + §4.4 CB 알림 규칙 + §7.1 `CB_OPEN_DETECTED` Critical + §5.3 `a2a.cb.state` OTel span attribute + CLF-A2A-004 의도적 차이 명시

---

## 12. 세션 간 인터페이스 cross-check

| 항목 | 대상 산출물 | 일치 항목 |
|------|------------|----------|
| `A2AMetrics` TypeScript interface | 상세명세 §6.1 L475~L508 | 수정 없는 정본 재인용 (§2.1), 본 문서 interface 변경 금지 |
| `TaskState` 6 enum | 상세명세 §2.2 + AUTHORITY §3 LOCK-A2A-02 | `tasks_by_state` keys 6 state verbatim |
| 8 A2A method | 상세명세 §2.3 | `tasks_by_method` keys + OTel span 8 naming |
| `active_sessions` | `04_advanced-features/multi_turn_sessions.md` §3.1 SessionState | Session active_set 정의 cross-reference |
| SSE dropped_artifacts | `04_advanced-features/streaming_sse.md` §4.3 backpressure | `a2a.stream.dropped_artifacts` span attribute |
| stream chunk_count | `04_advanced-features/streaming_sse.md` §3.2 artifact_chunk | `a2a.stream.chunk_count` span attribute |
| CB 상태 3-state | `04_advanced-features/streaming_sse.md` §6.1 + `push_notifications.md` §6.2 + `moa_pattern.md` §7.1 | CLOSED/OPEN/HALF-OPEN verbatim 전역 일관, LOCK-A2A-09 3 회 / 60 초 |
| TransitionEvent 6 전이군 | `04_advanced-features/conversation_state_machine.md` §4 | 상태 전이 카운터 메트릭 기반 |
| MoA proposal_count | `04_advanced-features/moa_pattern.md` §3.1 + §5.4 | R-11-6 2~5, `a2a.moa.proposal_count` attribute + `a2a_moa_proposal_count` Histogram |
| MoA aggregation_mode | `04_advanced-features/moa_pattern.md` §5 (3 모드) | `majority_voting` / `weighted_average` / `consensus` verbatim |
| MoA total_cost_usd | `04_advanced-features/moa_pattern.md` §6 비용 매트릭스 | `a2a.moa.total_cost_usd` attribute + `a2a_moa_cost_usd` Histogram |
| delegation.depth ≤ 3 | `04_advanced-features/multi_turn_sessions.md` + `conversation_state_machine.md` | LOCK-A2A-07 교차 준수, MoA 중첩 호출 시 누적 모니터링 |

---

## 13. 변경 이력

| 날짜 | 변경자 | 내용 |
|------|--------|------|
| 2026-04-22 | STAGE 7 3-8 STEP_B #2b (parent-executed) | V2-Phase 2 NEW 최초 작성 (P2-5 모니터링 대시보드 메트릭 세션, exit gate "모니터링 메트릭 정의" 직접 충족). 상세명세 §6.1 A2AMetrics TypeScript 정본 재인용 + 4종 메트릭 Pydantic 공용 구조 (TrafficMetrics/PerformanceMetrics/ReliabilityMetrics/AgentMetric/A2AMetricsSnapshot) + LOCK-A2A-09 CB 게이지 (cb_state_per_agent + cb_open_total + cb_trip_reason) + OTel W3C TraceContext + span `a2a.task.{method}` 8 method verbatim + span attributes 10 + sampling 3단 (head 10% / tail error 100% / consensus 100%) + Prometheus 메트릭 명명 + 알림 Critical 5 / Warning 4 + Grafana 5 패널 구조 + 15 MET-NN 테스트 시나리오 + peer cross-ref 12 지점 실체화 |
