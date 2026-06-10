# COND-102: Qwen3 통합 — L2+ 상세 명세

> **모듈 ID**: COND-102
> **카테고리**: CAT-A (AI/ML Engine)
> **이름**: Qwen3 통합
> **우선순위**: MEDIUM
> **Phase**: Phase 0
> **L-Level**: L2+ (Performance Benchmark·Integration Test Spec은 Phase 1/2 보강)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC, LOCK-CD-04 Runnable, LOCK-CD-05 ErrorHandlingStandard, LOCK-CD-06 VamosError 필드, LOCK-CD-10 ModuleConfig

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class InferenceParams(BaseModel):
    """추론 파라미터"""
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="샘플링 온도")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0, description="nucleus sampling")
    top_k: int = Field(default=50, ge=0, description="top-k sampling")
    max_tokens: int = Field(default=2048, ge=1, le=32768, description="최대 생성 토큰 수")
    stop_sequences: list[str] = Field(default_factory=list, description="생성 중단 시퀀스")
    repetition_penalty: float = Field(default=1.0, ge=0.0, le=2.0, description="반복 억제 패널티")
    lora_adapter_id: Optional[str] = Field(default=None, description="적용할 LoRA 어댑터 ID")

class Qwen3Request(BaseModel):
    """COND-102 입력 스키마"""
    prompt: str = Field(
        ..., description="Qwen3 모델에 전달할 프롬프트"
    )
    model_variant: Literal["qwen3-7b", "qwen3-14b", "qwen3-72b"] = Field(
        default="qwen3-14b",
        description="사용할 Qwen3 모델 변형"
    )
    params: InferenceParams = Field(
        default_factory=InferenceParams,
        description="추론 파라미터"
    )
    system_prompt: Optional[str] = Field(
        default=None,
        description="시스템 프롬프트 (역할/맥락 지정)"
    )
    language_hint: Optional[Literal["zh", "ko", "ja", "en", "auto"]] = Field(
        default="auto",
        description="다국어 처리 힌트"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "다음 Python 코드의 시간 복잡도를 분석하고 최적화 방안을 제시하세요.",
                "model_variant": "qwen3-14b",
                "params": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 4096,
                    "lora_adapter_id": "lora://code-analysis-v2"
                },
                "system_prompt": "당신은 숙련된 소프트웨어 엔지니어입니다.",
                "language_hint": "ko"
            }
        }
```

---

## E2. Output Schema

```python
class TokenUsage(BaseModel):
    prompt_tokens: int = Field(description="입력 프롬프트 토큰 수")
    completion_tokens: int = Field(description="생성된 토큰 수")
    total_tokens: int = Field(description="총 토큰 수")
    cost_estimate_usd: Optional[float] = Field(default=None, description="추정 비용 (USD)")

class ModelMetadata(BaseModel):
    model_name: str = Field(description="사용된 모델 이름")
    model_version: str = Field(description="모델 버전")
    serving_backend: Literal["vllm", "transformers", "api"] = Field(description="서빙 백엔드")
    lora_applied: bool = Field(default=False, description="LoRA 어댑터 적용 여부")
    quantization: Optional[str] = Field(default=None, description="양자화 설정 (e.g., AWQ, GPTQ)")

class Qwen3Response(BaseModel):
    """COND-102 출력 스키마"""
    response: str = Field(
        description="Qwen3 모델 생성 응답"
    )
    usage: TokenUsage = Field(
        description="토큰 사용량"
    )
    model_metadata: ModelMetadata = Field(
        description="모델 메타데이터"
    )
    finish_reason: Literal["stop", "length", "error"] = Field(
        description="생성 종료 사유"
    )
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "이 코드의 시간 복잡도는 O(n^2)입니다. 중첩 루프를 해시맵으로 대체하면 O(n)으로 최적화할 수 있습니다...",
                "usage": {
                    "prompt_tokens": 128,
                    "completion_tokens": 512,
                    "total_tokens": 640,
                    "cost_estimate_usd": 0.0032
                },
                "model_metadata": {
                    "model_name": "qwen3-14b",
                    "model_version": "3.0.1",
                    "serving_backend": "vllm",
                    "lora_applied": True,
                    "quantization": "AWQ-4bit"
                },
                "finish_reason": "stop",
                "execution_time_ms": 2340
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: Qwen3Request) -> Qwen3Response:
    # 1. 모델 로드 / vLLM 엔드포인트 확인
    backend = resolve_serving_backend(request.model_variant)
    IF backend == "vllm":
        endpoint = VllmEndpointRegistry.get(request.model_variant)
        IF endpoint is None OR NOT endpoint.is_healthy():
            RETURN Err(VamosError("COND_102_VLLM_UNAVAILABLE", ...))
    ELSE:
        model = ModelRegistry.load(request.model_variant)

    # 2. LoRA 어댑터 적용 (요청 시)
    adapter = None
    IF request.params.lora_adapter_id is not None:
        adapter = LoraRegistry.load(request.params.lora_adapter_id)
        IF adapter is None:
            RETURN Err(VamosError("COND_102_LORA_ADAPTER_ERROR", ...))
        apply_lora(model_or_endpoint, adapter)

    # 3. 토큰화 및 제한 검사
    tokenizer = Qwen3Tokenizer.for_variant(request.model_variant)
    prompt_tokens = tokenizer.encode(request.prompt)
    IF len(prompt_tokens) + request.params.max_tokens > MODEL_CONTEXT_LIMIT[request.model_variant]:
        RETURN Err(VamosError("COND_102_TOKEN_LIMIT_EXCEEDED", ...))

    # 4. 다국어 힌트 반영
    IF request.language_hint != "auto":
        prompt = prepend_language_tag(request.prompt, request.language_hint)
    ELSE:
        prompt = request.prompt

    # 5. 추론 실행
    start = now()
    TRY with timeout(config.timeout_ms):
        IF backend == "vllm":
            raw_response = endpoint.generate(
                prompt=prompt,
                system_prompt=request.system_prompt,
                temperature=request.params.temperature,
                top_p=request.params.top_p,
                top_k=request.params.top_k,
                max_tokens=request.params.max_tokens,
                stop=request.params.stop_sequences,
                repetition_penalty=request.params.repetition_penalty
            )
        ELSE:
            raw_response = model.generate(prompt, request.params)
    CATCH TimeoutError:
        RETURN Err(VamosError("COND_102_INFERENCE_TIMEOUT", ...))
    elapsed = now() - start

    # 6. 토큰 사용량 집계 및 비용 추정
    usage = TokenUsage(
        prompt_tokens=len(prompt_tokens),
        completion_tokens=raw_response.num_tokens,
        total_tokens=len(prompt_tokens) + raw_response.num_tokens,
        cost_estimate_usd=estimate_cost(request.model_variant, total_tokens)
    )

    # 7. 응답 구성
    RETURN Ok(Qwen3Response(
        response=raw_response.text,
        usage=usage,
        model_metadata=build_metadata(request, backend, adapter),
        finish_reason=raw_response.finish_reason,
        execution_time_ms=elapsed
    ))
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_102_MODEL_LOAD_FAILED` | Qwen3 모델 파일 로드 실패 또는 체크포인트 손상 | `F-102-01` | "Qwen3 모델을 로드할 수 없습니다." |
| `COND_102_INFERENCE_TIMEOUT` | 추론이 timeout_ms 내에 완료되지 않음 | `F-102-02` | "추론 시간이 초과되었습니다. max_tokens를 줄여 주세요." |
| `COND_102_TOKEN_LIMIT_EXCEEDED` | 프롬프트 + max_tokens가 컨텍스트 한계 초과 | `F-102-03` | "토큰 한도를 초과했습니다. 프롬프트를 줄이거나 max_tokens를 조정하세요." |
| `COND_102_VLLM_UNAVAILABLE` | vLLM 서빙 엔드포인트 미응답 또는 비가용 | `F-102-04` | "vLLM 서빙 엔드포인트에 연결할 수 없습니다." |
| `COND_102_LORA_ADAPTER_ERROR` | 지정된 LoRA 어댑터 로드/적용 실패 | `F-102-05` | "LoRA 어댑터를 적용할 수 없습니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_102_VLLM_UNAVAILABLE",
    message="vLLM endpoint unreachable for model: qwen3-14b",
    fallback_id="F-102-04",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-A 내부 의존 (§A.2.1)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| — | — | **완전 독립** (Level 0) — CAT-A 내부 의존 없음 | — |

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |
| **I-8 (Cost)** | LLM 추론 비용 관리 | **추가** |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `vllm` | ≥0.4 | Qwen3 모델 서빙 |
| `transformers` | ≥4.40 | Qwen3 토크나이저, 모델 로딩 |
| `peft` | ≥0.10 | LoRA 어댑터 관리 |
| `torch` | ≥2.2 | 텐서 연산 / GPU 추론 |
| `tiktoken` | ≥0.6 | 토큰 카운팅 (보조) |

### 인프라
| 인프라 | 용도 |
|--------|------|
| GPU (필수) | Qwen3 추론 가속 (최소 A10G / L4) |
| vLLM 서빙 클러스터 | 모델 서빙 엔드포인트 |
| 메모리 ≥ 16GB (7B) / 32GB (14B) / 80GB (72B) | 모델 가중치 로딩 |

---

## E6. Performance Benchmark

> Phase 1 보강 예정

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **TTFT (Time to First Token)** | ≤ 500ms | vLLM 서빙, 단일 요청 |
| **Throughput (7B)** | ≥ 50 tokens/s | 단일 GPU, batch=1 |
| **Throughput (14B)** | ≥ 30 tokens/s | 단일 GPU, batch=1 |
| **Throughput (72B)** | ≥ 10 tokens/s | 멀티 GPU, batch=1 |
| **동시 요청** | ≥ 8 concurrent | vLLM continuous batching |
| **LoRA 전환 지연** | ≤ 200ms | 어댑터 핫스왑 |

---

## E7. Integration Test Spec

> Phase 2 보강 예정

### 시나리오 1: 기본 추론 (14B 모델)
```yaml
name: "qwen3_basic_inference_14b"
setup:
  - ensure_vllm_endpoint("qwen3-14b", healthy=true)
input:
  prompt: "Python으로 퀵소트 알고리즘을 구현하세요."
  model_variant: "qwen3-14b"
  params:
    temperature: 0.3
    max_tokens: 1024
expected:
  - response is not empty
  - "def" in response  # Python 코드 포함
  - usage.total_tokens > 0
  - usage.prompt_tokens > 0
  - finish_reason == "stop"
  - execution_time_ms < 30000
```

### 시나리오 2: LoRA 어댑터 적용 추론
```yaml
name: "qwen3_lora_adapter"
setup:
  - ensure_vllm_endpoint("qwen3-7b", healthy=true)
  - register_lora("lora://test-adapter-v1")
input:
  prompt: "이 코드를 리팩토링하세요: for i in range(len(arr)): print(arr[i])"
  model_variant: "qwen3-7b"
  params:
    temperature: 0.2
    max_tokens: 512
    lora_adapter_id: "lora://test-adapter-v1"
expected:
  - response is not empty
  - model_metadata.lora_applied == true
  - finish_reason in ["stop", "length"]
```

### 시나리오 3: 에러 — 토큰 한계 초과
```yaml
name: "error_token_limit_exceeded"
input:
  prompt: "<very_long_prompt_exceeding_context_window>"
  model_variant: "qwen3-7b"
  params:
    max_tokens: 32768
expected:
  - error.failure_code == "COND_102_TOKEN_LIMIT_EXCEEDED"
  - error.fallback_id == "F-102-03"
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
| **우선순위** | MEDIUM |

### 호출 패턴
```
User → "이 코드의 시간 복잡도를 분석해줘"
  → ORANGE CORE (I-1 Intent 해석: code_analysis)
    → I-5 라우팅 → Quant Node
      → Quant Node: COND-102.execute(prompt="...", model_variant="qwen3-14b", ...)
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (정책 위반 없음)
          [2] CostGate ✅ (I-8 비용 한도 내)
          → COND-102 실행 → Qwen3Response 반환
            → Quant Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.a.102.initialized` | initialize() 완료 |
| 추론 시작 | `cond.a.102.execute_start` | execute() 진입 |
| 추론 완료 | `cond.a.102.execute_done` | 정상 반환 |
| 추론 실패 | `cond.a.102.execute_fail` | VamosError 발생 |
| 헬스체크 | `cond.a.102.health` | health_check() 호출 |
| 모듈 종료 | `cond.a.102.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-102", "execution_ms": N, "result_type": "inference" }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond102Qwen3Integration(BaseModule):
    """COND-102 Qwen3 통합"""

    async def initialize(self) -> Result[None, VamosError]:
        """vLLM 엔드포인트 연결, 토크나이저 로드, LoRA 레지스트리 초기화"""
        self._vllm_client = await VllmClient.connect(self.config.vllm_endpoint)
        self._tokenizer = Qwen3Tokenizer.load(self.config.default_variant)
        self._lora_registry = await LoraRegistry.connect()
        self._emit_event("cond.a.102.initialized")
        return Ok(None)

    async def execute(self, request: Qwen3Request) -> Result[Qwen3Response, VamosError]:
        """Runnable.run() 위임 — Qwen3 추론 실행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """vLLM 엔드포인트 상태 + GPU 가용성 확인"""
        vllm_ok = await self._vllm_client.ping()
        gpu_ok = await check_gpu_availability()
        return Ok(HealthStatus(healthy=vllm_ok and gpu_ok, latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        """vLLM 클라이언트 해제, 리소스 정리"""
        await self._vllm_client.disconnect()
        await self._lora_registry.disconnect()
        self._emit_event("cond.a.102.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-102", version="1.0.0",
            capabilities=["qwen3_inference", "multilingual", "code_generation", "math_reasoning", "lora_adaptation"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond102Config(ModuleConfig):
    """COND-102 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    max_concurrent: int = 8
    timeout_ms: int = 60000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=2000)

    # COND-102 전용 설정
    default_variant: Literal["qwen3-7b", "qwen3-14b", "qwen3-72b"] = "qwen3-14b"
    vllm_endpoint: str = "http://localhost:8000"
    max_context_length: dict[str, int] = {
        "qwen3-7b": 32768,
        "qwen3-14b": 32768,
        "qwen3-72b": 65536
    }
    default_temperature: float = 0.7
    enable_lora: bool = True
    lora_hot_swap: bool = True
    cost_tracking_enabled: bool = True
    cost_limit_usd_per_hour: float = 10.0
```
