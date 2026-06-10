# COND-031: 백프레셔 제어 — L3 상세 명세

> **모듈 ID**: COND-031
> **카테고리**: CAT-C (Ops/Infra) — Core
> **우선순위**: HIGH
> **Phase**: Phase 1
> **L3 수준**: L3
> **LOCK 준수**: LOCK-CD-03/04/05/06/08/10
> **인프라 패턴**: Token Bucket, Adaptive Rate Limiting, **Circuit Breaker** (CLOSED/OPEN/HALF_OPEN)

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class SystemMetrics(BaseModel):
    queue_depth: int = Field(..., ge=0)
    cpu_usage: float = Field(..., ge=0.0, le=1.0)
    memory_usage: float = Field(..., ge=0.0, le=1.0)
    latency_p99_ms: float = Field(..., ge=0.0)
    error_rate: float = Field(default=0.0, ge=0.0, le=1.0)

class BackpressureRequest(BaseModel):
    """COND-031 입력 스키마"""
    operation: Literal["evaluate", "reset", "status"] = "evaluate"
    metrics: Optional[SystemMetrics] = None
    target_service: str = Field(..., description="제어 대상 서비스 식별자")
    priority_floor: Optional[Literal["critical", "high", "medium", "low"]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "evaluate",
                "target_service": "research-node",
                "metrics": {"queue_depth": 12000, "cpu_usage": 0.92,
                            "memory_usage": 0.78, "latency_p99_ms": 1200.0,
                            "error_rate": 0.04}
            }
        }
```

---

## E2. Output Schema

```python
class BackpressureAction(BaseModel):
    throttle_rate: float = Field(ge=0.0, le=1.0, description="허용 비율 (1.0=정상)")
    reject_threshold: float = Field(ge=0.0, le=1.0, description="거부 시작 임계 점수")
    priority_cutoff: Literal["critical", "high", "medium", "low"]
    breaker_state: Literal["closed", "open", "half_open"]
    cool_down_seconds: int

class SystemStatus(BaseModel):
    target_service: str
    health_score: float = Field(ge=0.0, le=1.0)
    last_state_change: str  # ISO-8601
    consecutive_overload_seconds: int

class BackpressureResponse(BaseModel):
    """COND-031 출력 스키마"""
    operation: str
    action: Optional[BackpressureAction] = None
    status: SystemStatus
    decision_reason: str
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "evaluate",
                "action": {"throttle_rate": 0.4, "reject_threshold": 0.6,
                           "priority_cutoff": "high", "breaker_state": "half_open",
                           "cool_down_seconds": 15},
                "status": {"target_service": "research-node", "health_score": 0.32,
                           "last_state_change": "2026-04-07T10:00:00Z",
                           "consecutive_overload_seconds": 45},
                "decision_reason": "cpu>0.9 AND latency_p99>1000",
                "execution_time_ms": 3
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION evaluate(request) -> Result[BackpressureResponse, VamosError]:
    IF request.metrics IS NULL AND request.operation == "evaluate":
        RETURN Err(VamosError("COND_031_METRICS_REQUIRED", ...))
    m = request.metrics

    # 1. Health Score = weighted(cpu, memory, latency, queue, errors) [0..1]
    score = 1.0 - clamp(
        0.30 * m.cpu_usage +
        0.20 * m.memory_usage +
        0.20 * normalize(m.latency_p99_ms, baseline=config.latency_p99_baseline_ms) +
        0.20 * normalize(m.queue_depth, baseline=config.queue_baseline) +
        0.10 * m.error_rate,
        0.0, 1.0)

    # 2. Circuit Breaker 상태 전이
    state = breaker_store.get(request.target_service)
    cool_down = 0
    IF score < config.open_threshold:
        state.transition_to("open", reason="overload")
        cool_down = config.cool_down_seconds
    ELIF state.current == "open" AND elapsed_since_open >= config.cool_down_seconds:
        state.transition_to("half_open", reason="probe")
    ELIF state.current == "half_open" AND score > config.recovery_threshold:
        state.transition_to("closed", reason="recovered")

    # 3. Action 산출 — Token Bucket throttle 비율
    SWITCH state.current:
        CASE "closed":     throttle = 1.0; cutoff = "low"
        CASE "half_open":  throttle = max(0.2, score); cutoff = "high"
        CASE "open":       throttle = 0.0; cutoff = "critical"

    # 4. priority_floor 적용
    IF request.priority_floor:
        cutoff = max(cutoff, request.priority_floor, key=priority_rank)

    # 5. Adaptive 조정 — 연속 과부하 시간 비례 강화
    IF state.consecutive_overload_seconds > config.max_overload_seconds:
        throttle *= 0.5

    breaker_store.put(request.target_service, state)
    emit_event("cond.c.031.execute_done", {service, score, state, throttle})

    RETURN Ok(BackpressureResponse(
        action=BackpressureAction(throttle_rate=throttle, reject_threshold=1-score,
                                  priority_cutoff=cutoff, breaker_state=state.current,
                                  cool_down_seconds=cool_down),
        status=SystemStatus(...),
        decision_reason=explain(score, m, state),
    ))
```

---

## E4. Error Handling

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|-------------|--------------|
| `COND_031_METRICS_REQUIRED` | evaluate 시 metrics 누락 | `FB_COND_031_LAST_KNOWN` | "메트릭이 없어 직전 상태를 적용합니다." |
| `COND_031_INVALID_METRICS` | 값 범위 이탈 | `FB_COND_031_LAST_KNOWN` | "메트릭 값이 유효하지 않습니다." |
| `COND_031_BREAKER_STORE_DOWN` | breaker_store(Redis) 장애 | `FB_COND_031_FAIL_OPEN` | "안전 모드(통과)로 전환." |
| `COND_031_TARGET_UNKNOWN` | target_service 미등록 | `FB_COND_031_DEFAULT_POLICY` | "기본 정책 적용." |
| `COND_031_EXECUTE_TIMEOUT` | timeout_ms 초과 | `FB_COND_SKIP` | "처리 시간 초과." |

> **주의**: BREAKER_STORE 장애 시 fail-open(통과)을 채택하나, fallback_id 명시로 거버넌스 추적 가능. (운영 정책에 따라 fail-closed로 전환 가능)

```python
return Err(VamosError(
    failure_code="COND_031_BREAKER_STORE_DOWN",
    message=f"Breaker store unreachable: {dsn}",
    fallback_id="FB_COND_031_FAIL_OPEN",
    trace_id=ctx.trace_id,
))
```

---

## E5. Dependency Map

| 관계 | 항목 |
|------|------|
| 소비 | — |
| 제공 | 모든 CAT (호출 진입점에서 사전 필터) |

| I-Module | 용도 |
|----------|------|
| I-1, I-5, I-6, I-9 | 공통 |

| 인프라 / 라이브러리 | 사양 |
|----------------------|------|
| Redis | breaker state store |
| Prometheus | 메트릭 소스 |
| `pybreaker` (참조 구현) | Circuit Breaker |

---

## E6. Performance Benchmark (I-04)

| 메트릭 | SLA 목표 | 임계값 | 측정 |
|--------|---------|--------|------|
| **p99 evaluate** | ≤ 5 ms | > 20 ms | histogram |
| **처리량** | ≥ 20,000 req/s/instance | < 5,000 | load test |
| **오탐율(정상→open 전환)** | ≤ 1 % | > 5 % | shadow test |
| **복구 지연(half_open→closed)** | ≤ 30 s | > 120 s | incident |
| **가용성** | 99.95 % | < 99.9 % | uptime |

---

## E7. Integration Test Spec

```yaml
- name: "bp_high_cpu_opens_breaker"
  setup: [breaker_state(target: "svc1", state: "closed")]
  input: { operation: "evaluate", target_service: "svc1",
           metrics: {queue_depth: 5000, cpu_usage: 0.97, memory_usage: 0.5, latency_p99_ms: 1500, error_rate: 0.1} }
  expected:
    - action.breaker_state == "open"
    - action.throttle_rate == 0.0

- name: "bp_recovery_to_closed"
  setup: [breaker_state(target: "svc1", state: "half_open"), wait(15s)]
  input: { operation: "evaluate", target_service: "svc1",
           metrics: {queue_depth: 100, cpu_usage: 0.4, memory_usage: 0.4, latency_p99_ms: 200, error_rate: 0.0} }
  expected: [action.breaker_state == "closed"]

- name: "bp_breaker_store_down_fail_open"
  setup: [redis_down()]
  input: { operation: "evaluate", target_service: "svc1", metrics: {...} }
  expected: [error.failure_code == "COND_031_BREAKER_STORE_DOWN", fallback_id == "FB_COND_031_FAIL_OPEN"]
```

---

## E8. Blue Node Integration

| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | 모든 Node (호출 사전 필터) |
| **Permission Level** | P0 |
| **게이트 요구** | policy |
| **호출 패턴** | OpsInfraMixin이 호출 직전 evaluate() 호출 → action에 따라 reject/throttle |

| 이벤트 | event_type |
|--------|------------|
| 초기화 | `cond.c.031.initialized` |
| 실행 시작/완료/실패 | `cond.c.031.execute_start` / `execute_done` / `execute_fail` |
| 헬스체크 | `cond.c.031.health` |
| 종료 | `cond.c.031.shutdown` |

Decision: `optional_signals ← {cond_module_id: "COND-031", breaker_state, throttle_rate}`

---

## E9. BaseModule ABC 적합성

```python
class Cond031Backpressure(BaseModule):
    async def initialize(self) -> Result[None, VamosError]:
        self._store = await BreakerStore.connect(self.config.store_dsn)
        self._emit_event("cond.c.031.initialized")
        return Ok(None)

    async def execute(self, request: BackpressureRequest) -> Result[BackpressureResponse, VamosError]:
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        return Ok(HealthStatus(healthy=await self._store.ping(), latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        await self._store.close()
        self._emit_event("cond.c.031.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(id="COND-031", version="1.0.0",
                              capabilities=["evaluate", "reset", "status", "circuit_breaker"])
```

---

## E10. Configuration

```python
class Cond031Config(ModuleConfig):
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "critical"
    max_concurrent: int = 1000
    timeout_ms: int = 50
    retry_policy: RetryPolicy = RetryPolicy(max_retries=0, backoff_ms=0)

    store_dsn: str
    open_threshold: float = 0.3        # health_score 미만 시 open
    recovery_threshold: float = 0.7
    cool_down_seconds: int = 15
    max_overload_seconds: int = 60
    latency_p99_baseline_ms: float = 500.0
    queue_baseline: int = 5000
    fail_mode: Literal["open", "closed"] = "open"
```
