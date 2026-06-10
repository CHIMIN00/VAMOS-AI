# COND-014: A/B 테스팅 엔진 — L2+ 상세 명세

> **모듈 ID**: COND-014
> **카테고리**: CAT-A (AI/ML Engine)
> **이름**: A/B 테스팅 엔진
> **우선순위**: MEDIUM
> **Phase**: Phase 0
> **L-Level**: L2+ (Performance Benchmark·Integration Test Spec은 Phase 1/2 보강)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC, LOCK-CD-04 Runnable, LOCK-CD-05 ErrorHandlingStandard, LOCK-CD-06 VamosError 필드, LOCK-CD-10 ModuleConfig

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

class VariantConfig(BaseModel):
    """실험 변형 구성"""
    variant_id: str = Field(..., description="변형 고유 ID (예: 'control', 'treatment_a')")
    model_ref: Optional[str] = Field(default=None, description="모델 참조 ID (모델 비교 시)")
    prompt_template: Optional[str] = Field(default=None, description="프롬프트 템플릿 (프롬프트 비교 시)")
    parameters: Optional[dict] = Field(default=None, description="변형별 파라미터 오버라이드")
    description: str = Field(default="", description="변형 설명")

class MetricConfig(BaseModel):
    """측정 메트릭 구성"""
    metric_name: str = Field(..., description="메트릭 이름 (예: 'accuracy', 'latency', 'user_satisfaction')")
    metric_type: Literal["higher_is_better", "lower_is_better"] = Field(
        ..., description="메트릭 방향"
    )
    primary: bool = Field(default=False, description="주요 메트릭 여부 (승자 결정 기준)")

class ExperimentConfig(BaseModel):
    """실험 구성"""
    experiment_id: str = Field(..., description="실험 고유 ID")
    experiment_name: str = Field(..., description="실험 이름")
    variants: list[VariantConfig] = Field(
        ..., min_length=2,
        description="실험 변형 리스트 (최소 2개: control + treatment)"
    )
    traffic_split: dict[str, float] = Field(
        ..., description="트래픽 분할 비율 (variant_id → ratio, 합계=1.0)"
    )
    metrics: list[MetricConfig] = Field(
        ..., min_length=1,
        description="측정 메트릭 리스트 (최소 1개 primary)"
    )
    min_sample_size: int = Field(
        default=1000, ge=100,
        description="통계적 유의성을 위한 최소 샘플 수 (변형당)"
    )
    max_duration_hours: Optional[int] = Field(
        default=168, ge=1,
        description="실험 최대 지속 시간 (시간, 기본 7일)"
    )
    confidence_level: float = Field(
        default=0.95, ge=0.80, le=0.99,
        description="신뢰 수준"
    )
    test_method: Literal["frequentist", "bayesian", "sequential", "bandit"] = Field(
        default="bayesian",
        description="통계 검정 방법"
    )
    auto_stop: bool = Field(
        default=True,
        description="통계적 유의성 도달 시 자동 종료"
    )

class ABTestRequest(BaseModel):
    """COND-014 입력 스키마"""
    experiment_config: ExperimentConfig = Field(
        ..., description="실험 구성"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "experiment_config": {
                    "experiment_id": "exp-2024-prompt-v3",
                    "experiment_name": "프롬프트 v2 vs v3 비교",
                    "variants": [
                        {
                            "variant_id": "control",
                            "prompt_template": "기존 프롬프트 v2 ...",
                            "description": "현행 프롬프트"
                        },
                        {
                            "variant_id": "treatment_a",
                            "prompt_template": "신규 프롬프트 v3 ...",
                            "description": "CoT 강화 프롬프트"
                        }
                    ],
                    "traffic_split": {"control": 0.5, "treatment_a": 0.5},
                    "metrics": [
                        {"metric_name": "accuracy", "metric_type": "higher_is_better", "primary": True},
                        {"metric_name": "latency_ms", "metric_type": "lower_is_better", "primary": False},
                        {"metric_name": "user_satisfaction", "metric_type": "higher_is_better", "primary": False}
                    ],
                    "min_sample_size": 1000,
                    "max_duration_hours": 168,
                    "confidence_level": 0.95,
                    "test_method": "bayesian",
                    "auto_stop": True
                }
            }
        }
```

---

## E2. Output Schema

```python
class VariantMetric(BaseModel):
    """변형별 메트릭 결과"""
    metric_name: str = Field(description="메트릭 이름")
    mean: float = Field(description="평균값")
    std: float = Field(description="표준편차")
    sample_size: int = Field(description="샘플 수")
    ci_lower: float = Field(description="신뢰구간 하한")
    ci_upper: float = Field(description="신뢰구간 상한")

class VariantResult(BaseModel):
    """변형별 결과"""
    variant_id: str = Field(description="변형 ID")
    metrics: list[VariantMetric] = Field(description="메트릭별 결과")
    total_samples: int = Field(description="총 샘플 수")
    traffic_actual_pct: float = Field(description="실제 트래픽 비율 (%)")

class PairwiseComparison(BaseModel):
    """변형 간 쌍별 비교"""
    baseline: str = Field(description="기준 변형 ID")
    challenger: str = Field(description="도전 변형 ID")
    metric_name: str = Field(description="비교 메트릭")
    p_value: Optional[float] = Field(default=None, description="p-value (frequentist)")
    posterior_prob: Optional[float] = Field(
        default=None, description="사후 확률 — challenger가 우수할 확률 (bayesian)"
    )
    effect_size: float = Field(description="효과 크기 (Cohen's d 또는 상대적 차이)")
    ci_lower: float = Field(description="차이의 신뢰구간 하한")
    ci_upper: float = Field(description="차이의 신뢰구간 상한")
    significant: bool = Field(description="통계적 유의성 여부")

class ExperimentResults(BaseModel):
    """COND-014 출력 스키마"""
    experiment_id: str = Field(description="실험 ID")
    status: Literal["running", "completed", "stopped_early", "failed"] = Field(
        description="실험 상태"
    )
    variant_results: list[VariantResult] = Field(description="변형별 결과")
    comparisons: list[PairwiseComparison] = Field(description="쌍별 비교 결과")
    winner: Optional[str] = Field(
        default=None, description="승자 변형 ID (유의미한 차이 없으면 None)"
    )
    winner_confidence: Optional[float] = Field(
        default=None, description="승자 판정 신뢰도"
    )
    recommendation: str = Field(description="권장 사항 (자연어)")
    started_at: datetime = Field(description="실험 시작 시각")
    ended_at: Optional[datetime] = Field(default=None, description="실험 종료 시각")
    execution_time_ms: int = Field(description="결과 산출 소요 시간 (ms)")

    class Config:
        json_schema_extra = {
            "example": {
                "experiment_id": "exp-2024-prompt-v3",
                "status": "completed",
                "variant_results": [
                    {
                        "variant_id": "control",
                        "metrics": [
                            {"metric_name": "accuracy", "mean": 0.82, "std": 0.04, "sample_size": 1200, "ci_lower": 0.798, "ci_upper": 0.842}
                        ],
                        "total_samples": 1200,
                        "traffic_actual_pct": 49.5
                    },
                    {
                        "variant_id": "treatment_a",
                        "metrics": [
                            {"metric_name": "accuracy", "mean": 0.87, "std": 0.03, "sample_size": 1224, "ci_lower": 0.853, "ci_upper": 0.887}
                        ],
                        "total_samples": 1224,
                        "traffic_actual_pct": 50.5
                    }
                ],
                "comparisons": [
                    {
                        "baseline": "control",
                        "challenger": "treatment_a",
                        "metric_name": "accuracy",
                        "posterior_prob": 0.97,
                        "effect_size": 0.42,
                        "ci_lower": 0.028,
                        "ci_upper": 0.072,
                        "significant": True
                    }
                ],
                "winner": "treatment_a",
                "winner_confidence": 0.97,
                "recommendation": "treatment_a (CoT 강화 프롬프트)가 accuracy에서 통계적으로 유의미한 개선(+5pp, 97% 확률)을 보입니다. 전환을 권장합니다.",
                "started_at": "2024-03-08T00:00:00Z",
                "ended_at": "2024-03-12T14:30:00Z",
                "execution_time_ms": 450
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: ABTestRequest) -> ExperimentResults:
    config = request.experiment_config

    # 1. 실험 유효성 검증
    IF ExperimentStore.exists(config.experiment_id):
        RETURN Err(VamosError(COND_014_EXPERIMENT_EXISTS))

    split_sum = sum(config.traffic_split.values())
    IF abs(split_sum - 1.0) > 0.001:
        RETURN Err(VamosError(COND_014_TRAFFIC_SPLIT_INVALID))

    IF NOT any(m.primary for m IN config.metrics):
        RETURN Err(VamosError(COND_014_STATS_ERROR, "No primary metric"))

    # 2. 실험 등록 및 트래픽 라우터 설정
    experiment = ExperimentStore.create(config)
    TrafficRouter.configure(
        experiment_id=config.experiment_id,
        split=config.traffic_split
    )

    # 3. 데이터 수집 (비동기 — 배치 추론은 COND-012에 위임)
    FOR variant IN config.variants:
        batch_requests = generate_variant_requests(variant, config.min_sample_size)
        # A-3: COND-012 배치처리 엔진에 대량 추론 위임
        batch_result = await COND_012.execute(BatchProcessingRequest(
            requests=batch_requests,
            batch_config=BatchConfig(priority_mode="fifo")
        ))
        IF batch_result.is_err():
            RETURN Err(VamosError(COND_014_VARIANT_FAILED,
                        f"Variant {variant.variant_id} batch failed"))
        ExperimentStore.record_results(config.experiment_id, variant.variant_id, batch_result)

    # 4. 통계 분석
    primary_metric = next(m for m IN config.metrics IF m.primary)
    variant_results = []
    comparisons = []

    total_samples = sum(len(ExperimentStore.get_data(config.experiment_id, v.variant_id)) for v in config.variants)
    total_samples = sum(len(ExperimentStore.get_data(config.experiment_id, v.variant_id)) for v in config.variants)
    FOR variant IN config.variants:
        raw_data = ExperimentStore.get_data(config.experiment_id, variant.variant_id)
        IF len(raw_data) < config.min_sample_size:
            RETURN Err(VamosError(COND_014_INSUFFICIENT_SAMPLES))

        metrics = []
        FOR metric_cfg IN config.metrics:
            values = extract_metric_values(raw_data, metric_cfg.metric_name)
            ci = compute_confidence_interval(values, config.confidence_level)
            metrics.append(VariantMetric(
                metric_name=metric_cfg.metric_name,
                mean=mean(values), std=std(values),
                sample_size=len(values),
                ci_lower=ci.lower, ci_upper=ci.upper
            ))
        variant_results.append(VariantResult(
            variant_id=variant.variant_id, metrics=metrics,
            total_samples=len(raw_data),
            traffic_actual_pct=len(raw_data) / total_samples * 100
        ))

    # 5. 쌍별 비교 (control vs each treatment)
    control = config.variants[0]
    FOR treatment IN config.variants[1:]:
        control_data = ExperimentStore.get_metric(config.experiment_id, control.variant_id, primary_metric.metric_name)
        treatment_data = ExperimentStore.get_metric(config.experiment_id, treatment.variant_id, primary_metric.metric_name)

        IF config.test_method == "bayesian":
            comparison = bayesian_ab_test(control_data, treatment_data, config.confidence_level)
        ELIF config.test_method == "frequentist":
            comparison = frequentist_test(control_data, treatment_data, config.confidence_level)
        ELIF config.test_method == "sequential":
            comparison = sequential_test(control_data, treatment_data, config.confidence_level)
        ELIF config.test_method == "bandit":
            comparison = thompson_sampling_evaluate(control_data, treatment_data)

        comparisons.append(comparison)

    # 6. 승자 결정
    winner, winner_conf = determine_winner(comparisons, primary_metric.metric_type)

    # 7. 권장사항 생성
    recommendation = generate_recommendation(winner, comparisons, variant_results, primary_metric)

    RETURN ExperimentResults(
        experiment_id=config.experiment_id,
        status="completed",
        variant_results=variant_results,
        comparisons=comparisons,
        winner=winner,
        winner_confidence=winner_conf,
        recommendation=recommendation,
        started_at=experiment.started_at,
        ended_at=now(),
        execution_time_ms=elapsed_ms()
    )


FUNCTION bayesian_ab_test(control, treatment, confidence) -> PairwiseComparison:
    """Bayesian A/B Test — Beta-Binomial 또는 Normal-Normal 모델"""
    # Beta 사후 분포: Beta(alpha + successes, beta + failures)
    alpha_c = 1 + sum(control)
    beta_c = 1 + len(control) - sum(control)
    alpha_t = 1 + sum(treatment)
    beta_t = 1 + len(treatment) - sum(treatment)

    # Monte Carlo 시뮬레이션으로 P(treatment > control) 추정
    samples_c = Beta(alpha_c, beta_c).sample(100000)
    samples_t = Beta(alpha_t, beta_t).sample(100000)
    posterior_prob = mean(samples_t > samples_c)

    effect_size = cohens_d(treatment, control)
    diff_samples = samples_t - samples_c
    ci = quantile(diff_samples, [(1 - confidence) / 2, (1 + confidence) / 2])

    RETURN PairwiseComparison(
        baseline=control.variant_id,
        challenger=treatment.variant_id,
        metric_name=primary_metric.metric_name,
        posterior_prob=posterior_prob,
        effect_size=effect_size,
        ci_lower=ci[0], ci_upper=ci[1],
        significant=(posterior_prob > confidence)
    )
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_014_EXPERIMENT_EXISTS` | 동일 experiment_id의 실험이 이미 존재 | `F-014-01` | "동일한 ID의 실험이 이미 존재합니다." |
| `COND_014_INSUFFICIENT_SAMPLES` | 최소 샘플 수 미달로 통계 분석 불가 | `F-014-02` | "통계적 유의성을 위한 충분한 샘플이 수집되지 않았습니다." |
| `COND_014_VARIANT_FAILED` | 특정 변형의 추론 실행 실패 | `F-014-03` | "실험 변형의 추론 실행에 실패했습니다." |
| `COND_014_STATS_ERROR` | 통계 검정 연산 중 오류 (수렴 실패 등) | `F-014-04` | "통계 분석 중 오류가 발생했습니다." |
| `COND_014_TRAFFIC_SPLIT_INVALID` | 트래픽 분할 비율 합계가 1.0이 아님 | `F-014-05` | "트래픽 분할 비율의 합이 100%가 아닙니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_014_INSUFFICIENT_SAMPLES",
    message="Insufficient samples for variant '{variant_id}': {actual} < {required}",
    fallback_id="F-014-02",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-A 내부 의존 (§A.2.1)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **소비** (A-3) | COND-014 → COND-012 (배치처리) | 실험 변형별 대량 추론 실행 | ②③ |

> COND-014는 COND-012를 소비 (Level 1)

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `scipy` | ≥1.11 | t-test, chi-squared, Mann-Whitney U |
| `numpy` | ≥1.24 | 수치 연산, Monte Carlo 시뮬레이션 |
| `pymc` | ≥5.0 (optional) | Bayesian 모델링 (정밀 분석 시) |
| `statsmodels` | ≥0.14 | Sequential Testing, 효과 크기 계산 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| ExperimentStore (PostgreSQL) | 실험 구성, 결과 데이터 저장 |
| TrafficRouter (Redis) | 실시간 트래픽 분할 제어 |
| COND-012 (배치처리) | 대량 추론 실행 위임 |

---

## E6. Performance Benchmark

> Phase 1 보강 예정 — basic SLA targets only

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **실험 생성** | ≤ 500ms | 실험 등록 + 트래픽 라우터 설정 |
| **결과 산출 (1K samples)** | ≤ 2,000ms | 통계 분석 + 승자 판정 |
| **결과 산출 (100K samples)** | ≤ 10,000ms | 대규모 데이터 통계 분석 |
| **Bayesian MC 시뮬레이션** | ≤ 5,000ms (100K iterations) | Monte Carlo 수렴 |
| **트래픽 라우팅 지연** | ≤ 5ms | Redis 기반 트래픽 분할 조회 |
| **동시 실험 수** | ≥ 50 | 병렬 실험 운영 |

---

## E7. Integration Test Spec

> Phase 2 보강 예정 — skeleton scenarios only

### 시나리오 1: 기본 Bayesian A/B 테스트
```yaml
name: "basic_bayesian_ab_test"
setup:
  - no_existing_experiment("exp-test-001")
  - register_model("model-a", type="onnx")
  - register_model("model-b", type="onnx")
  - mock_cond_012_batch_results(success=true, sample_size=1000)
input:
  experiment_config:
    experiment_id: "exp-test-001"
    experiment_name: "Model A vs B"
    variants:
      - {variant_id: "control", model_ref: "model://test/model-a"}
      - {variant_id: "treatment", model_ref: "model://test/model-b"}
    traffic_split: {"control": 0.5, "treatment": 0.5}
    metrics:
      - {metric_name: "accuracy", metric_type: "higher_is_better", primary: true}
    min_sample_size: 1000
    test_method: "bayesian"
    confidence_level: 0.95
expected:
  - status == "completed"
  - variant_results.length == 2
  - comparisons.length == 1
  - comparisons[0].posterior_prob is between 0.0 and 1.0
  - winner is not None or significant is false
  - recommendation is not empty
```

### 시나리오 2: 3-way 트래픽 분할
```yaml
name: "three_way_split"
setup:
  - mock_cond_012_batch_results(success=true, sample_size=500)
input:
  experiment_config:
    experiment_id: "exp-test-002"
    experiment_name: "Prompt A vs B vs C"
    variants:
      - {variant_id: "control", prompt_template: "v1..."}
      - {variant_id: "treatment_a", prompt_template: "v2..."}
      - {variant_id: "treatment_b", prompt_template: "v3..."}
    traffic_split: {"control": 0.34, "treatment_a": 0.33, "treatment_b": 0.33}
    metrics:
      - {metric_name: "accuracy", metric_type: "higher_is_better", primary: true}
    min_sample_size: 500
    test_method: "bayesian"
expected:
  - variant_results.length == 3
  - comparisons.length == 2  # control vs treatment_a, control vs treatment_b
```

### 시나리오 3: 에러 — 실험 중복
```yaml
name: "error_experiment_exists"
setup:
  - create_experiment("exp-dup-001")
input:
  experiment_config:
    experiment_id: "exp-dup-001"
    experiment_name: "Duplicate"
    variants: [{variant_id: "a"}, {variant_id: "b"}]
    traffic_split: {"a": 0.5, "b": 0.5}
    metrics: [{metric_name: "accuracy", metric_type: "higher_is_better", primary: true}]
expected:
  - error.failure_code == "COND_014_EXPERIMENT_EXISTS"
  - error.fallback_id == "F-014-01"
```

### 시나리오 4: 에러 — 트래픽 비율 오류
```yaml
name: "error_traffic_split_invalid"
input:
  experiment_config:
    experiment_id: "exp-test-003"
    experiment_name: "Bad Split"
    variants: [{variant_id: "a"}, {variant_id: "b"}]
    traffic_split: {"a": 0.6, "b": 0.6}  # 합계 1.2
    metrics: [{metric_name: "accuracy", metric_type: "higher_is_better", primary: true}]
expected:
  - error.failure_code == "COND_014_TRAFFIC_SPLIT_INVALID"
  - error.fallback_id == "F-014-05"
```

---

## E8. Blue Node Integration

> §B.6.1 CAT-A 연동 프로토콜 (P0-2 산출물) 반영
> > LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.1)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Research Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy, cost, evidence |
| **우선순위** | MEDIUM |

### 호출 패턴
```
User → "새 프롬프트와 기존 프롬프트 성능 비교해줘"
  → ORANGE CORE (I-1 Intent 해석: ab_test_experiment)
    → I-5 라우팅 → Research Node
      → Research Node: COND-014.execute(experiment_config={...})
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (실험 정책 범위 내)
          [2] CostGate ✅ (추론 비용 — COND-012 위임 비용 포함)
          [3] EvidenceGate ✅ (충분한 샘플 수 확보 가능)
          → COND-014 실행 → COND-012 배치 추론 위임
            → ExperimentResults 반환
              → Research Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.a.014.initialized` | initialize() 완료 |
| 실험 시작 | `cond.a.014.execute_start` | execute() 진입 |
| 실험 완료 | `cond.a.014.execute_done` | 정상 반환 |
| 실험 실패 | `cond.a.014.execute_fail` | VamosError 발생 |
| 헬스체크 | `cond.a.014.health` | health_check() 호출 |
| 모듈 종료 | `cond.a.014.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-014", "execution_ms": N, "result_type": "ab_test", "winner": "treatment_a", "confidence": 0.97 }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond014ABTesting(BaseModule):
    """COND-014 A/B 테스팅 엔진"""

    async def initialize(self) -> Result[None, VamosError]:
        """ExperimentStore 연결, TrafficRouter 초기화, COND-012 참조 획득"""
        self._experiment_store = await ExperimentStore.connect()
        self._traffic_router = await TrafficRouter.connect()
        self._batch_engine = self._module_registry.get("COND-012")  # COND-012 참조
        self._emit_event("cond.a.014.initialized")
        return Ok(None)

    async def execute(self, request: ABTestRequest) -> Result[ExperimentResults, VamosError]:
        """Runnable.run() 위임 — A/B 테스트 실행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """ExperimentStore, TrafficRouter, COND-012 가용성 확인"""
        store_ok = await self._experiment_store.ping()
        router_ok = await self._traffic_router.ping()
        batch_ok = (await self._batch_engine.health_check()).is_ok()
        return Ok(HealthStatus(
            healthy=store_ok and router_ok and batch_ok,
            latency_ms=elapsed,
            details={"store": store_ok, "router": router_ok, "batch_engine": batch_ok}
        ))

    async def shutdown(self) -> Result[None, VamosError]:
        """진행 중 실험 상태 저장, 연결 해제"""
        await self._experiment_store.flush_pending()
        await self._experiment_store.disconnect()
        await self._traffic_router.disconnect()
        self._emit_event("cond.a.014.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-014", version="1.0.0",
            capabilities=["ab_testing", "bayesian_test", "sequential_test", "multi_armed_bandit", "traffic_splitting"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond014Config(ModuleConfig):
    """COND-014 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    max_concurrent: int = 10
    timeout_ms: int = 300000  # 5분 (대량 실험 소요)
    retry_policy: RetryPolicy = RetryPolicy(max_retries=1, backoff_ms=2000)

    # COND-014 전용 설정
    default_test_method: Literal["frequentist", "bayesian", "sequential", "bandit"] = "bayesian"
    default_confidence_level: float = 0.95
    default_min_sample_size: int = 1000
    max_variants_per_experiment: int = 10
    max_concurrent_experiments: int = 50
    mc_simulation_iterations: int = 100000  # Monte Carlo 반복 수
    auto_stop_enabled: bool = True
    experiment_store_dsn: str = "postgresql://vamos:***@localhost/experiments"
    traffic_router_url: str = "redis://localhost:6379/1"
    results_cache_ttl_seconds: int = 300
```
