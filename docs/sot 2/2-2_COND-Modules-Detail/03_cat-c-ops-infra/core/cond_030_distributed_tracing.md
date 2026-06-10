# COND-030: 분산트레이싱 — L3 상세 명세

> **모듈 ID**: COND-030
> **카테고리**: CAT-C (Ops/Infra) — Core
> **우선순위**: HIGH
> **Phase**: Phase 1
> **L3 수준**: L3
> **LOCK 준수**: LOCK-CD-03/04/05/06/08/10
> **인프라 패턴**: Sampling (head/tail), Span Correlation, W3C TraceContext Propagation

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class TraceConfig(BaseModel):
    sample_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    propagation_format: Literal["w3c", "b3", "jaeger"] = "w3c"
    export_endpoint: str = Field(..., description="OTLP gRPC/HTTP endpoint")
    sampler_type: Literal["head", "tail", "adaptive"] = "head"
    max_spans_per_trace: int = Field(default=200, ge=1)

class TracingRequest(BaseModel):
    """COND-030 입력 스키마"""
    operation: Literal["start_trace", "end_trace", "query", "export", "configure"]
    trace_config: Optional[TraceConfig] = None
    trace_id: Optional[str] = Field(default=None, pattern=r"^[0-9a-f]{32}$")
    service: Optional[str] = None
    time_range_seconds: int = Field(default=300, ge=1, le=86400)
    filter: Optional[dict] = None  # service, span_name, status

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "query",
                "service": "research-node",
                "time_range_seconds": 300,
                "filter": {"status": "error"}
            }
        }
```

---

## E2. Output Schema

```python
class Span(BaseModel):
    span_id: str
    parent_span_id: Optional[str]
    name: str
    service: str
    start_time_ns: int
    duration_ms: float
    status: Literal["ok", "error", "unset"]
    attributes: dict[str, str]

class Trace(BaseModel):
    trace_id: str
    spans: list[Span]
    duration_ms: float
    status: Literal["ok", "error"]
    root_service: str

class ServiceMapEdge(BaseModel):
    src: str
    dst: str
    call_count: int
    error_rate: float
    p99_latency_ms: float

class ServiceMap(BaseModel):
    nodes: list[str]
    edges: list[ServiceMapEdge]

class Bottleneck(BaseModel):
    span_name: str
    service: str
    p99_latency_ms: float
    contribution_pct: float

class TracingResponse(BaseModel):
    """COND-030 출력 스키마"""
    operation: str
    traces: list[Trace] = Field(default_factory=list)
    service_map: Optional[ServiceMap] = None
    bottlenecks: list[Bottleneck] = Field(default_factory=list)
    sample_rate_effective: Optional[float] = None
    execution_time_ms: int

    class Config:
        json_schema_extra = {
            "example": {
                "operation": "query",
                "traces": [{"trace_id": "a"*32, "spans": [], "duration_ms": 142.0,
                            "status": "ok", "root_service": "research-node"}],
                "bottlenecks": [{"span_name": "rag.retrieve", "service": "research-node",
                                 "p99_latency_ms": 380.0, "contribution_pct": 42.5}],
                "sample_rate_effective": 0.1, "execution_time_ms": 35
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request) -> Result[TracingResponse, VamosError]:
    SWITCH request.operation:
      CASE "configure":
          IF request.trace_config IS NULL:
              RETURN Err(VamosError("COND_030_CONFIG_REQUIRED", ...))
          otel_sdk.configure(
              sampler=build_sampler(request.trace_config.sampler_type, request.trace_config.sample_rate),
              propagator=build_propagator(request.trace_config.propagation_format),
              exporter=OTLPExporter(request.trace_config.export_endpoint))
          RETURN Ok(...)

      CASE "start_trace":
          ctx = otel_sdk.start_span(name=request.service, kind="server")
          inject_w3c_traceparent(ctx)
          RETURN Ok(TracingResponse(traces=[Trace(trace_id=ctx.trace_id, ...)]))

      CASE "end_trace":
          IF NOT span_registry.has(request.trace_id):
              RETURN Err(VamosError("COND_030_TRACE_NOT_FOUND", ...))
          span_registry.end(request.trace_id, status="ok")
          RETURN Ok(...)

      CASE "query":
          IF time_range > config.max_query_window_seconds:
              RETURN Err(VamosError("COND_030_QUERY_TOO_LARGE", ...))
          traces = trace_store.query(service=request.service,
                                     since=now() - request.time_range_seconds,
                                     filter=request.filter,
                                     limit=config.max_query_results)
          # 서비스 맵 구축
          service_map = build_service_map(traces)
          # 병목 분석 (p99 정렬, contribution_pct 산출)
          bottlenecks = analyze_bottlenecks(traces, top_k=config.bottleneck_top_k)
          RETURN Ok(TracingResponse(traces=traces, service_map=service_map, bottlenecks=bottlenecks))

      CASE "export":
          batch = span_buffer.drain(max=config.max_spans_per_trace or 1000)
          result = otlp_client.export(batch)
          IF result.failed:
              RETURN Err(VamosError("COND_030_EXPORT_FAIL", ...))
          RETURN Ok(...)
```

---

## E4. Error Handling

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|-------------|--------------|
| `COND_030_CONFIG_REQUIRED` | configure 시 trace_config 누락 | `FB_COND_REJECT` | "트레이싱 설정이 필요합니다." |
| `COND_030_TRACE_NOT_FOUND` | trace_id 미존재 | `FB_COND_SKIP` | "트레이스를 찾을 수 없습니다." |
| `COND_030_EXPORT_FAIL` | OTLP 익스포트 실패 | `FB_COND_030_LOCAL_BUFFER` | "원격 저장소 일시 장애. 로컬 버퍼링." |
| `COND_030_QUERY_TOO_LARGE` | time_range/filter 과대 | `FB_COND_030_NARROW_QUERY` | "쿼리 범위가 너무 큽니다." |
| `COND_030_PROPAGATION_INVALID` | traceparent 헤더 파싱 실패 | `FB_COND_030_NEW_TRACE` | "트레이스 컨텍스트가 유효하지 않습니다." |
| `COND_030_BACKEND_DOWN` | trace store 장애 | `FB_COND_SKIP` | "트레이스 백엔드 장애." |
| `COND_030_EXECUTE_TIMEOUT` | timeout_ms 초과 | `FB_COND_SKIP` | "처리 시간 초과." |

```python
return Err(VamosError(
    failure_code="COND_030_EXPORT_FAIL",
    message=f"OTLP export failed to {endpoint}: {reason}",
    fallback_id="FB_COND_030_LOCAL_BUFFER",
    trace_id=ctx.trace_id,
))
```

---

## E5. Dependency Map

| 관계 | 항목 |
|------|------|
| 소비 | — |
| 제공 | 모든 CAT (자동 계측) |

| I-Module | 용도 |
|----------|------|
| I-1, I-5, I-6, I-9 | 공통 |

| 인프라 / 라이브러리 | 사양 |
|----------------------|------|
| `opentelemetry-sdk` | ≥1.24 |
| `opentelemetry-exporter-otlp` | gRPC/HTTP |
| Tempo / Jaeger / Grafana Tempo | 트레이스 저장소 |
| Elasticsearch (선택) | 트레이스 인덱싱 |

---

## E6. Performance Benchmark (I-04)

| 메트릭 | SLA 목표 | 임계값 | 측정 |
|--------|---------|--------|------|
| **span 발행 오버헤드(p99)** | ≤ 0.5 ms | > 2 ms | micro-bench |
| **export batch p99 (1000 spans)** | ≤ 200 ms | > 1 s | gRPC histogram |
| **query p99 (5분 윈도)** | ≤ 800 ms | > 3 s | histogram |
| **샘플 손실율** | ≤ 0.1 % | > 1 % | counter |
| **저장소 retention** | ≥ 7 d | < 3 d | 운영 정책 |
| **가용성** | 99.9 % | < 99.5 % | uptime |

---

## E7. Integration Test Spec

```yaml
- name: "trace_propagation_w3c"
  setup: [configure(propagation_format: "w3c", sample_rate: 1.0)]
  input: { operation: "start_trace", service: "test-svc" }
  expected: [traces[0].trace_id matches "^[0-9a-f]{32}$"]

- name: "trace_query_error_filter"
  setup: [seed_traces(error: 5, ok: 95)]
  input: { operation: "query", service: "test-svc", filter: {status: "error"} }
  expected: [traces.length == 5]

- name: "trace_export_fail_buffered"
  setup: [otlp_endpoint_down()]
  input: { operation: "export" }
  expected: [error.failure_code == "COND_030_EXPORT_FAIL", fallback_id == "FB_COND_030_LOCAL_BUFFER"]
```

---

## E8. Blue Node Integration

| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | 모든 Node (자동 계측) |
| **Permission Level** | P0 |
| **게이트 요구** | policy |
| **호출 패턴** | OpsInfraMixin auto-instrumentation, span context 전파 |

| 이벤트 | event_type |
|--------|------------|
| 초기화 | `cond.c.030.initialized` |
| 실행 시작/완료/실패 | `cond.c.030.execute_start` / `execute_done` / `execute_fail` |
| 헬스체크 | `cond.c.030.health` |
| 종료 | `cond.c.030.shutdown` |

Decision: `optional_signals ← {cond_module_id: "COND-030", op, trace_count, sample_rate}`

---

## E9. BaseModule ABC 적합성

```python
class Cond030DistributedTracing(BaseModule):
    async def initialize(self) -> Result[None, VamosError]:
        self._tracer = OtelTracerProvider.from_config(self.config)
        self._exporter = OTLPExporter(endpoint=self.config.export_endpoint)
        self._store = await TraceStore.connect(self.config.store_dsn)
        self._emit_event("cond.c.030.initialized")
        return Ok(None)

    async def execute(self, request: TracingRequest) -> Result[TracingResponse, VamosError]:
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        return Ok(HealthStatus(healthy=await self._store.ping(), latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        await self._exporter.flush(); await self._store.close()
        self._emit_event("cond.c.030.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(id="COND-030", version="1.0.0",
                              capabilities=["start_trace", "end_trace", "query", "export", "service_map"])
```

---

## E10. Configuration

```python
class Cond030Config(ModuleConfig):
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 500
    timeout_ms: int = 2000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=3, backoff_ms=200)

    export_endpoint: str
    store_dsn: str
    sample_rate: float = 0.1
    sampler_type: Literal["head", "tail", "adaptive"] = "head"
    propagation_format: Literal["w3c", "b3", "jaeger"] = "w3c"
    max_spans_per_trace: int = 200
    max_query_window_seconds: int = 86400
    max_query_results: int = 1000
    bottleneck_top_k: int = 5
    retention_days: int = 7
```
