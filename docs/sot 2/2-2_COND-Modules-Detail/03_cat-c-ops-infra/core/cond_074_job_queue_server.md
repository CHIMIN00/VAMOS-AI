# COND-074: 작업큐 서버 — L3 상세 명세

> **모듈 ID**: COND-074
> **카테고리**: CAT-C (Ops/Infra) — Core
> **우선순위**: HIGH
> **Phase**: Phase 1
> **L3 수준**: L3
> **LOCK 준수**: LOCK-CD-03/04/05/06/08/10
> **인프라 패턴**: Producer-Consumer Queue, Priority Scheduling, Dead Letter Queue (DLQ), Worker Pool, Retry/Backoff

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional, Any

class JobDefinition(BaseModel):
    task_name: str = Field(..., description="등록된 작업 핸들러 이름")
    params: dict[str, Any] = Field(default_factory=dict)
    priority: Literal["critical", "high", "normal", "low"] = "normal"
    timeout_ms: int = Field(default=60000, ge=100)
    max_retries: int = Field(default=3, ge=0, le=20)
    schedule_at: Optional[str] = Field(default=None, description="ISO-8601 (지연 실행)")
    idempotency_key: Optional[str] = None
    queue: str = Field(default="default")

class JobQueueRequest(BaseModel):
    """COND-074 입력 스키마"""
    operation: Literal["submit", "status", "cancel", "result", "list"] = "submit"
    job: Optional[JobDefinition] = None
    job_id: Optional[str] = None
    queue: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "submit",
                "job": {"task_name": "send_report", "params": {"user_id": "u-1"},
                        "priority": "high", "timeout_ms": 30000, "max_retries": 3,
                        "queue": "notifications"}
            }
        }
```

---

## E2. Output Schema

```python
class JobStatus(BaseModel):
    job_id: str
    state: Literal["queued", "scheduled", "running", "succeeded", "failed", "canceled", "dead"]
    queue: str
    priority: str
    attempts: int
    enqueued_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    worker_id: Optional[str] = None
    error: Optional[str] = None

class JobQueueResponse(BaseModel):
    """COND-074 출력 스키마"""
    operation: str
    job_id: Optional[str] = None
    job_status: Optional[JobStatus] = None
    result: Optional[Any] = None
    jobs: list[JobStatus] = Field(default_factory=list)
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "submit",
                "job_id": "job-9f8e",
                "job_status": {"job_id": "job-9f8e", "state": "queued",
                               "queue": "notifications", "priority": "high",
                               "attempts": 0, "enqueued_at": "2026-04-07T10:00:00Z"},
                "execution_time_ms": 6
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request) -> Result[JobQueueResponse, VamosError]:
    SWITCH request.operation:
      CASE "submit":
          IF request.job IS NULL:
              RETURN Err(VamosError("COND_074_JOB_REQUIRED", ...))
          IF NOT task_registry.has(request.job.task_name):
              RETURN Err(VamosError("COND_074_TASK_NOT_REGISTERED", ...))
          # Idempotency
          IF request.job.idempotency_key:
              existing = job_store.find_by_key(request.job.idempotency_key)
              IF existing: RETURN Ok(... existing job_status ...)
          job_id = uuid7()
          status = JobStatus(job_id, state="queued" IF NOT schedule_at ELSE "scheduled", ...)
          job_store.put(status)
          IF schedule_at:
              scheduler.enqueue_at(job_id, schedule_at, queue=request.job.queue, priority=request.job.priority)
          ELSE:
              priority_queue.push(request.job.queue, job_id, priority=request.job.priority)
          RETURN Ok(JobQueueResponse(operation="submit", job_id=job_id, job_status=status))

      CASE "status":
          status = job_store.get(request.job_id)
          IF status IS NULL:
              RETURN Err(VamosError("COND_074_JOB_NOT_FOUND", ...))
          RETURN Ok(JobQueueResponse(operation="status", job_status=status))

      CASE "cancel":
          status = job_store.get(request.job_id)
          IF status.state IN ("succeeded", "failed", "dead", "canceled"):
              RETURN Err(VamosError("COND_074_NOT_CANCELABLE", ...))
          job_store.update(request.job_id, state="canceled")
          priority_queue.remove(request.job_id)
          RETURN Ok(...)

      CASE "result":
          status = job_store.get(request.job_id)
          IF status.state != "succeeded":
              RETURN Err(VamosError("COND_074_RESULT_NOT_READY", ...))
          result = result_store.get(request.job_id)
          RETURN Ok(JobQueueResponse(operation="result", result=result, job_status=status))

      CASE "list":
          jobs = job_store.list(queue=request.queue, limit=config.list_limit)
          RETURN Ok(JobQueueResponse(operation="list", jobs=jobs))


# 워커 루프 (별도 컴포넌트)
FUNCTION worker_loop(worker_id):
    WHILE running:
        job_id = priority_queue.pop_blocking(worker.assigned_queues)
        WITH timeout(job.timeout_ms):
            handler = task_registry.resolve(job.task_name)
            TRY:
                result = handler(job.params)
                job_store.update(job_id, state="succeeded", finished_at=now())
                result_store.put(job_id, result)
            CATCH (timeout, exception) AS e:
                IF job.attempts < job.max_retries:
                    job_store.update(job_id, state="queued", attempts=job.attempts+1)
                    priority_queue.push_with_backoff(job_id, base=job.attempts ** 2 * 1000)
                ELSE:
                    job_store.update(job_id, state="dead")
                    dlq.push(job_id, reason=str(e))
```

---

## E4. Error Handling

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|-------------|--------------|
| `COND_074_JOB_REQUIRED` | submit 시 job 누락 | `FB_COND_REJECT` | "작업 정의가 필요합니다." |
| `COND_074_TASK_NOT_REGISTERED` | task_name 미등록 | `FB_COND_REJECT` | "지원하지 않는 작업입니다." |
| `COND_074_JOB_NOT_FOUND` | job_id 미존재 | `FB_COND_REJECT` | "작업을 찾을 수 없습니다." |
| `COND_074_NOT_CANCELABLE` | 종료 상태 작업 취소 시도 | `FB_COND_REJECT` | "이미 종료된 작업입니다." |
| `COND_074_RESULT_NOT_READY` | 결과가 아직 없음 | `FB_COND_074_POLL` | "결과가 아직 준비되지 않았습니다." |
| `COND_074_QUEUE_BACKEND_DOWN` | Redis/RabbitMQ 장애 | `FB_COND_SKIP` | "큐 백엔드 일시 장애." |
| `COND_074_DLQ_LIMIT_EXCEEDED` | DLQ 한도 초과 | `FB_COND_074_OPERATOR` | "DLQ 한도 초과. 운영자 확인 필요." |
| `COND_074_EXECUTE_TIMEOUT` | timeout_ms 초과 | `FB_COND_SKIP` | "작업 처리 시간 초과." |

```python
return Err(VamosError(
    failure_code="COND_074_TASK_NOT_REGISTERED",
    message=f"task '{task_name}' not in registry",
    fallback_id="FB_COND_REJECT",
    trace_id=ctx.trace_id,
))
```

---

## E5. Dependency Map

| 관계 | 항목 |
|------|------|
| 소비 | — |
| 제공 | 모든 CAT (비동기 작업 위임) |

| I-Module | 용도 |
|----------|------|
| I-1, I-5, I-6, I-9 | 공통 |

| 인프라 / 라이브러리 | 사양 |
|----------------------|------|
| Redis (≥7.0) / RabbitMQ | 큐 백엔드 |
| PostgreSQL | job_store, result_store |
| `celery` / `dramatiq` / `arq` | 참조 구현 |

---

## E6. Performance Benchmark (I-04)

| 메트릭 | SLA 목표 | 임계값 | 측정 |
|--------|---------|--------|------|
| **submit p99** | ≤ 15 ms | > 50 ms | histogram |
| **enqueue→start latency p99** | ≤ 200 ms | > 1 s | histogram |
| **처리량** | ≥ 5,000 job/s/cluster | < 1,000 | throughput |
| **재시도 성공률** | ≥ 80 % | < 50 % | counter |
| **DLQ 비율** | ≤ 0.5 % | > 2 % | counter |
| **가용성** | 99.95 % | < 99.9 % | uptime |

---

## E7. Integration Test Spec

```yaml
- name: "jq_submit_basic"
  setup: [register_task("noop")]
  input: { operation: "submit", job: {task_name: "noop", params: {}, priority: "normal"} }
  expected: [job_status.state == "queued", job_id != ""]

- name: "jq_idempotency_dedup"
  setup: [register_task("noop"), submit({idempotency_key: "k1"}) -> j1]
  input: { operation: "submit", job: {task_name: "noop", idempotency_key: "k1"} }
  expected: [job_id == j1]

- name: "jq_retry_then_dead"
  setup: [register_failing_task("boom", fail_count: 5), submit({max_retries: 3})]
  expected: [eventually(job_status.state == "dead"), dlq_count == 1]
```

---

## E8. Blue Node Integration

| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | 모든 Node (비동기 작업 위임) |
| **Permission Level** | P0 |
| **게이트 요구** | policy, cost (무거운 작업 시) |
| **호출 패턴** | OpsInfraMixin.submit_job() |

| 이벤트 | event_type |
|--------|------------|
| 초기화 | `cond.c.074.initialized` |
| 실행 시작/완료/실패 | `cond.c.074.execute_start` / `execute_done` / `execute_fail` |
| 헬스체크 | `cond.c.074.health` |
| 종료 | `cond.c.074.shutdown` |

Decision: `optional_signals ← {cond_module_id: "COND-074", op, queue, priority, job_id}`

---

## E9. BaseModule ABC 적합성

```python
class Cond074JobQueue(BaseModule):
    async def initialize(self) -> Result[None, VamosError]:
        self._queue = await PriorityQueue.connect(self.config.queue_dsn)
        self._store = await JobStore.connect(self.config.store_dsn)
        self._results = await ResultStore.connect(self.config.results_dsn)
        self._dlq = await DLQClient.connect(self.config.dlq_dsn)
        self._registry = TaskRegistry.discover()
        self._emit_event("cond.c.074.initialized")
        return Ok(None)

    async def execute(self, request: JobQueueRequest) -> Result[JobQueueResponse, VamosError]:
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        return Ok(HealthStatus(
            healthy=await self._queue.ping() and await self._store.ping() and await self._dlq.ping(),
            latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        await self._dlq.close(); await self._results.close()
        await self._store.close(); await self._queue.close()
        self._emit_event("cond.c.074.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(id="COND-074", version="1.0.0",
                              capabilities=["submit", "status", "cancel", "result", "list"])
```

---

## E10. Configuration

```python
class Cond074Config(ModuleConfig):
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 1000
    timeout_ms: int = 5000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=200)

    queue_dsn: str
    store_dsn: str
    results_dsn: str
    dlq_dsn: str
    queues: list[str] = ["default", "notifications", "long_running"]
    worker_pool_size: int = 32
    result_ttl_seconds: int = 86400
    list_limit: int = 100
    enable_idempotency: bool = True
```
