# COND-012: 배치처리 엔진 — L2+ 상세 명세

> **모듈 ID**: COND-012
> **카테고리**: CAT-A (AI/ML Engine)
> **이름**: 배치처리 엔진
> **우선순위**: HIGH
> **Phase**: Phase 0
> **L-Level**: L2+ (Performance Benchmark·Integration Test Spec은 Phase 1/2 보강)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC, LOCK-CD-04 Runnable, LOCK-CD-05 ErrorHandlingStandard, LOCK-CD-06 VamosError 필드, LOCK-CD-10 ModuleConfig

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from enum import IntEnum

class PriorityLevel(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3

class InferenceRequest(BaseModel):
    """단일 추론 요청"""
    request_id: str = Field(..., description="고유 요청 ID")
    enqueue_time: datetime = Field(default_factory=datetime.utcnow, description="요청 큐 진입 시각 (지연 측정 기준)")
    model_ref: str = Field(..., description="VAMOS 모델 레지스트리의 모델 참조 ID")
    input_data: dict = Field(..., description="모델 입력 데이터 (텐서 또는 dict)")
    priority: PriorityLevel = Field(
        default=PriorityLevel.NORMAL,
        description="요청 우선순위"
    )
    max_latency_ms: Optional[int] = Field(
        default=None,
        description="개별 요청 최대 허용 지연 시간 (ms)"
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="추가 메타데이터 (caller_id, experiment_id 등)"
    )

class BatchConfig(BaseModel):
    """배치 구성"""
    max_batch_size: int = Field(
        default=32, ge=1, le=512,
        description="최대 배치 크기"
    )
    max_wait_ms: int = Field(
        default=100, ge=10, le=5000,
        description="배치 구성 최대 대기 시간 (ms)"
    )
    priority_mode: Literal["fifo", "priority", "deadline"] = Field(
        default="priority",
        description="스케줄링 모드 — fifo: 선입선출, priority: 우선순위, deadline: 최대 지연 기반"
    )
    enable_continuous_batching: bool = Field(
        default=True,
        description="연속 배칭 활성화 (토큰 단위 동적 배치)"
    )
    gpu_memory_limit_mb: Optional[int] = Field(
        default=None,
        description="GPU 메모리 상한 (MB, None이면 자동 감지)"
    )
    token_bucket_capacity: int = Field(
        default=10000, ge=100,
        description="Token Bucket 용량 (연속 배칭 시)"
    )

class BatchProcessingRequest(BaseModel):
    """COND-012 입력 스키마"""
    requests: list[InferenceRequest] = Field(
        ..., min_length=1,
        description="추론 요청 리스트"
    )
    batch_config: BatchConfig = Field(
        default_factory=BatchConfig,
        description="배치 구성"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "requests": [
                    {
                        "request_id": "req-001",
                        "model_ref": "model://quant-node/stock-predictor-v2",
                        "input_data": {"features": [150.5, 1200000, 65.3, 0.85]},
                        "priority": 2,
                        "max_latency_ms": 500
                    },
                    {
                        "request_id": "req-002",
                        "model_ref": "model://quant-node/stock-predictor-v2",
                        "input_data": {"features": [148.2, 980000, 58.1, -0.32]},
                        "priority": 1
                    }
                ],
                "batch_config": {
                    "max_batch_size": 32,
                    "max_wait_ms": 100,
                    "priority_mode": "priority",
                    "enable_continuous_batching": True,
                    "gpu_memory_limit_mb": 4096,
                    "token_bucket_capacity": 10000
                }
            }
        }
```

---

## E2. Output Schema

```python
class InferenceResult(BaseModel):
    """단일 추론 결과"""
    request_id: str = Field(description="원본 요청 ID")
    output: dict = Field(description="모델 추론 결과")
    latency_ms: int = Field(description="개별 요청 처리 시간 (ms)")
    batch_id: str = Field(description="소속 배치 ID")
    status: Literal["success", "failed", "timeout"] = Field(description="처리 상태")
    error: Optional[str] = Field(default=None, description="실패 시 에러 메시지")

class BatchStatistics(BaseModel):
    """배치 처리 통계"""
    total_requests: int = Field(description="전체 요청 수")
    successful: int = Field(description="성공 요청 수")
    failed: int = Field(description="실패 요청 수")
    total_batches: int = Field(description="생성된 배치 수")
    avg_batch_size: float = Field(description="평균 배치 크기")
    avg_latency_ms: float = Field(description="평균 지연 시간 (ms)")
    p50_latency_ms: float = Field(description="p50 지연 시간")
    p99_latency_ms: float = Field(description="p99 지연 시간")
    throughput_rps: float = Field(description="처리량 (requests/sec)")
    gpu_utilization_pct: float = Field(description="GPU 활용률 (%)")
    gpu_memory_used_mb: float = Field(description="GPU 메모리 사용량 (MB)")
    total_processing_ms: int = Field(description="전체 처리 시간 (ms)")

class BatchProcessingResponse(BaseModel):
    """COND-012 출력 스키마"""
    results: list[InferenceResult] = Field(description="추론 결과 리스트 (입력 순서 유지)")
    batch_stats: BatchStatistics = Field(description="배치 처리 통계")

    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "request_id": "req-001",
                        "output": {"prediction": 0.82, "confidence": 0.91},
                        "latency_ms": 45,
                        "batch_id": "batch-2024-001",
                        "status": "success"
                    },
                    {
                        "request_id": "req-002",
                        "output": {"prediction": 0.34, "confidence": 0.87},
                        "latency_ms": 45,
                        "batch_id": "batch-2024-001",
                        "status": "success"
                    }
                ],
                "batch_stats": {
                    "total_requests": 2,
                    "successful": 2,
                    "failed": 0,
                    "total_batches": 1,
                    "avg_batch_size": 2.0,
                    "avg_latency_ms": 45.0,
                    "p50_latency_ms": 45.0,
                    "p99_latency_ms": 45.0,
                    "throughput_rps": 44.4,
                    "gpu_utilization_pct": 72.5,
                    "gpu_memory_used_mb": 1280.0,
                    "total_processing_ms": 95
                }
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: BatchProcessingRequest) -> BatchProcessingResponse:
    config = request.batch_config
    queue = PriorityQueue() if config.priority_mode == "priority" else FIFOQueue()
    results_map = {}

    # 1. GPU 메모리 프로파일링
    gpu_mem = detect_gpu_memory() if config.gpu_memory_limit_mb is None
              else config.gpu_memory_limit_mb
    model_cache = {}

    # 2. 요청 큐 적재 (우선순위/데드라인 기반 정렬)
    FOR req IN request.requests:
        IF config.priority_mode == "deadline":
            sort_key = req.max_latency_ms or MAX_INT
        ELIF config.priority_mode == "priority":
            sort_key = -req.priority  # 높은 우선순위 먼저
        ELSE:
            sort_key = insertion_order
        queue.push(req, sort_key)

    # 3. 동적 배치 구성
    WHILE NOT queue.empty():
        batch = []
        batch_id = generate_batch_id()
        batch_start = now()

        # 3a. 모델별 그룹핑 — 동일 모델 요청을 하나의 배치로
        current_model = queue.peek().model_ref
        IF current_model NOT IN model_cache:
            model_cache[current_model] = load_model(current_model)
        model = model_cache[current_model]

        # 3b. 배치 크기 동적 결정
        estimated_per_item_mb = estimate_memory(model, queue.peek().input_data)
        max_by_memory = floor(gpu_mem / estimated_per_item_mb)
        effective_batch_size = min(config.max_batch_size, max_by_memory)

        # 3c. 배치 채우기 (max_wait_ms 이내)
        WHILE len(batch) < effective_batch_size AND NOT queue.empty():
            IF queue.peek().model_ref != current_model:
                BREAK  # 다른 모델은 다음 배치
            IF elapsed(batch_start) > config.max_wait_ms AND len(batch) > 0:
                BREAK  # 대기 시간 초과
            batch.append(queue.pop())

        # 4. 배치 추론 실행
        IF config.enable_continuous_batching:
            # Token Bucketing: 토큰 수 기준으로 동적 분할
            token_batches = split_by_token_count(batch, config.token_bucket_capacity)
            FOR t_batch IN token_batches:
                batch_input = collate(t_batch, model)
                batch_output = model.batch_predict(batch_input)  # ONNX Runtime
                scatter_results(t_batch, batch_output, batch_id, results_map)
        ELSE:
            batch_input = collate(batch, model)
            batch_output = model.batch_predict(batch_input)
            scatter_results(batch, batch_output, batch_id, results_map)

    # 5. 결과 정렬 (입력 순서 유지) + 통계 산출
    ordered_results = [results_map[req.request_id] for req IN request.requests]
    stats = compute_batch_stats(ordered_results, gpu_utilization())

    RETURN BatchProcessingResponse(results=ordered_results, batch_stats=stats)


FUNCTION scatter_results(batch, outputs, batch_id, results_map):
    """배치 출력을 개별 결과로 분해"""
    FOR i, req IN enumerate(batch):
        results_map[req.request_id] = InferenceResult(
            request_id=req.request_id,
            output=outputs[i],
            latency_ms=elapsed_since(req.enqueue_time),
            batch_id=batch_id,
            status="success"
        )


FUNCTION estimate_memory(model, sample_input) -> float:
    """단일 입력에 대한 GPU 메모리 추정 (MB)"""
    input_tensor_size = tensor_size_mb(sample_input)
    activation_estimate = model.estimated_activation_mb
    RETURN input_tensor_size + activation_estimate + OVERHEAD_MB
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_012_QUEUE_FULL` | 내부 큐가 최대 용량(max_queue_size) 초과 | `F-012-01` | "배치 큐가 가득 찼습니다. 잠시 후 재시도하세요." |
| `COND_012_GPU_OOM` | GPU 메모리 부족으로 배치 실행 불가 | `F-012-02` | "GPU 메모리 부족입니다. 배치 크기를 줄여 주세요." |
| `COND_012_BATCH_TIMEOUT` | 전체 배치 처리가 timeout_ms 초과 | `F-012-03` | "배치 처리 시간이 초과되었습니다." |
| `COND_012_INFERENCE_FAILED` | 개별 추론 요청 실행 중 모델 오류 | `F-012-04` | "추론 실행 중 오류가 발생했습니다." |
| `COND_012_INVALID_REQUEST` | 요청 데이터가 모델 입력 스키마와 불일치 | `F-012-05` | "요청 데이터가 모델 입력 형식과 맞지 않습니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_012_GPU_OOM",
    message="GPU OOM during batch inference: allocated={alloc_mb}MB, required={req_mb}MB",
    fallback_id="F-012-02",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-A 내부 의존 (§A.2.1)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **제공** (A-2) | COND-085 (CrewAI) → COND-012 | CrewAI 대량 추론 요청 위임 | ②③ |
| **제공** (A-3) | COND-014 (A/B 테스팅) → COND-012 | 실험 변형별 대량 추론 실행 | ②③ |

> COND-012는 **제공 전용** — CAT-A 내부에서 소비하는 모듈 없음 (Level 0)

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |
| **I-8 (Cost)** | 배치 추론 비용 상한 관리 | **추가** |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `onnxruntime` | ≥1.16 | ONNX Runtime 배치 추론 |
| `onnxruntime-gpu` | ≥1.16 | GPU 가속 배치 추론 |
| `numpy` | ≥1.24 | 텐서 연산, collate |
| `torch` | ≥2.1 (optional) | PyTorch 모델 배치 추론 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| GPU (NVIDIA CUDA) | 배치 추론 가속 (필수) |
| GPU 메모리 ≥ 8GB | 동적 배치 크기에 따른 메모리 |
| Redis / 내부 큐 | 우선순위 큐 관리 |

---

## E6. Performance Benchmark

> Phase 1 보강 예정 — basic SLA targets only

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **배치 처리량** | ≥ 1,000 req/s (batch_size=32) | 동일 모델, GPU A100 기준 |
| **배치 구성 지연** | ≤ max_wait_ms (100ms default) | 큐 대기 → 배치 전송 시점 |
| **개별 p99 지연** | ≤ 200ms (batch_size=32) | 큐 진입 → 결과 반환 |
| **GPU 활용률** | ≥ 80% (연속 부하 시) | nvidia-smi 측정 |
| **GPU 메모리 초과 없음** | OOM 발생률 < 0.01% | 동적 배치 크기 조절 검증 |
| **우선순위 역전 없음** | CRITICAL 요청 선처리 보장 | priority 모드 시 순서 검증 |

---

## E7. Integration Test Spec

> Phase 2 보강 예정 — skeleton scenarios only

### 시나리오 1: 기본 배치 처리
```yaml
name: "basic_batch_processing"
setup:
  - register_model("test-model-v1", type="onnx", features=["f1", "f2", "f3"])
  - gpu_available: true
input:
  requests:
    - {request_id: "r1", model_ref: "model://test/test-model-v1", input_data: {features: [1.0, 2.0, 3.0]}, priority: 1}
    - {request_id: "r2", model_ref: "model://test/test-model-v1", input_data: {features: [4.0, 5.0, 6.0]}, priority: 1}
    - {request_id: "r3", model_ref: "model://test/test-model-v1", input_data: {features: [7.0, 8.0, 9.0]}, priority: 1}
  batch_config:
    max_batch_size: 32
    max_wait_ms: 100
    priority_mode: "fifo"
expected:
  - results.length == 3
  - all(r.status == "success" for r in results)
  - batch_stats.total_batches == 1
  - batch_stats.avg_batch_size == 3.0
```

### 시나리오 2: 우선순위 스케줄링
```yaml
name: "priority_scheduling"
setup:
  - register_model("test-model-v1", type="onnx", features=["f1"])
  - configure max_batch_size=2  # 2개씩 배치
input:
  requests:
    - {request_id: "low-1", model_ref: "model://test/test-model-v1", input_data: {features: [1.0]}, priority: 0}
    - {request_id: "critical-1", model_ref: "model://test/test-model-v1", input_data: {features: [2.0]}, priority: 3}
    - {request_id: "high-1", model_ref: "model://test/test-model-v1", input_data: {features: [3.0]}, priority: 2}
  batch_config:
    max_batch_size: 2
    priority_mode: "priority"
expected:
  - results[0].request_id in ["critical-1", "high-1"]  # 높은 우선순위 먼저 배치
  - batch_stats.total_batches == 2
```

### 시나리오 3: GPU OOM 복구
```yaml
name: "gpu_oom_recovery"
setup:
  - register_model("large-model", type="onnx", features=["f1"..."f1000"])
  - simulate_gpu_memory_limit(512)  # 512MB only
input:
  requests: [100 requests with large input_data]
  batch_config:
    max_batch_size: 64
    gpu_memory_limit_mb: 512
expected:
  - batch_stats.avg_batch_size < 64  # 동적으로 줄어듬
  - all(r.status == "success" for r in results)  # OOM 없이 처리
```

### 시나리오 4: 에러 — 큐 가득 참
```yaml
name: "error_queue_full"
setup:
  - set max_queue_size=10
input:
  requests: [20 requests]  # 큐 용량 초과
expected:
  - error.failure_code == "COND_012_QUEUE_FULL"
  - error.fallback_id == "F-012-01"
```

---

## E8. Blue Node Integration

> §B.6.1 CAT-A 연동 프로토콜 (P0-2 산출물) 반영
> > LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.1)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Quant Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy, cost |
| **우선순위** | HIGH |

### 호출 패턴
```
CrewAI Agent → "100개 종목 동시 추론 실행"
  → ORANGE CORE (I-1 Intent 해석: batch_inference)
    → I-5 라우팅 → Quant Node
      → Quant Node: COND-012.execute(requests=[...100 items], batch_config={...})
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (배치 크기 정책 범위 내)
          [2] CostGate ✅ (I-8 비용 상한 이내)
          → COND-012 실행 → BatchProcessingResponse 반환
            → Quant Node → ORANGE CORE → Caller
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.a.012.initialized` | initialize() 완료 |
| 배치 시작 | `cond.a.012.execute_start` | execute() 진입 |
| 배치 완료 | `cond.a.012.execute_done` | 정상 반환 |
| 배치 실패 | `cond.a.012.execute_fail` | VamosError 발생 |
| 헬스체크 | `cond.a.012.health` | health_check() 호출 |
| 모듈 종료 | `cond.a.012.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-012", "execution_ms": N, "result_type": "batch_inference", "batch_count": M }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond012BatchProcessing(BaseModule):
    """COND-012 배치처리 엔진"""

    async def initialize(self) -> Result[None, VamosError]:
        """GPU 디바이스 감지, ONNX Runtime 세션 풀 초기화, 우선순위 큐 생성"""
        self._gpu_devices = await detect_gpu_devices()
        self._session_pool = OnnxSessionPool(max_sessions=self.config.max_concurrent)
        self._priority_queue = PriorityQueue(max_size=self.config.max_queue_size)
        self._model_cache = LRUCache(max_size=16)
        self._emit_event("cond.a.012.initialized")
        return Ok(None)

    async def execute(self, request: BatchProcessingRequest) -> Result[BatchProcessingResponse, VamosError]:
        """Runnable.run() 위임 — 배치 추론 실행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """GPU 가용 상태, 큐 용량, ONNX Runtime 세션 상태 확인"""
        gpu_ok = await self._gpu_devices.check_available()
        queue_usage = self._priority_queue.size / self._priority_queue.max_size
        session_ok = self._session_pool.healthy()
        return Ok(HealthStatus(
            healthy=gpu_ok and session_ok,
            latency_ms=elapsed,
            details={"gpu_available": gpu_ok, "queue_usage_pct": queue_usage * 100}
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        """진행 중 배치 완료 대기, 세션 풀 해제, 큐 비우기"""
        await self._session_pool.drain()
        self._model_cache.clear()
        self._priority_queue.clear()
        self._emit_event("cond.a.012.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-012", version="1.0.0",
            capabilities=["batch_inference", "dynamic_batching", "continuous_batching", "priority_scheduling"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond012Config(ModuleConfig):
    """COND-012 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 4
    timeout_ms: int = 60000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=500)

    # COND-012 전용 설정
    default_max_batch_size: int = 32
    default_max_wait_ms: int = 100
    default_priority_mode: Literal["fifo", "priority", "deadline"] = "priority"
    max_queue_size: int = 10000
    enable_continuous_batching: bool = True
    default_token_bucket_capacity: int = 10000
    gpu_memory_reserve_pct: float = 10.0  # GPU 메모리 예약 비율 (%)
    model_cache_max_entries: int = 16
    onnx_session_pool_size: int = 4
    batch_stats_window_seconds: int = 60  # 통계 수집 윈도우
    cost_limit_per_batch: Optional[float] = None  # I-8 비용 상한 (USD)
```
