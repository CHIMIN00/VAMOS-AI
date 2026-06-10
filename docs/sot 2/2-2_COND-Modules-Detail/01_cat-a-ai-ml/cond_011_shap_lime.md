# COND-011: SHAP/LIME 설명가능AI — L3 상세 명세

> **모듈 ID**: COND-011
> **카테고리**: CAT-A (AI/ML Engine)
> **이름**: SHAP/LIME 설명가능AI
> **우선순위**: HIGH
> **Phase**: Phase 0
> **L3 수준**: L3 (구현 즉시 투입 가능)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC (§3.4, D2.0-02 §1.2-A + §12.2 기반), LOCK-CD-04 Runnable 프로토콜 (D2.0-02 §1.2-A), LOCK-CD-05 ErrorHandlingStandard (D2.0-02 §0.3), LOCK-CD-06 VamosError 필드 (D2.0-02 §0.3), LOCK-CD-10 ModuleConfig (종합명세 §공통)

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
import pandas as pd

class ShapLimeRequest(BaseModel):
    """COND-011 입력 스키마"""
    model_ref: str = Field(
        ..., description="VAMOS 모델 레지스트리의 모델 참조 ID"
    )
    input_data: dict = Field(
        ..., description="DataFrame으로 변환될 입력 데이터 (columns + rows)"
    )
    explain_type: Literal["local", "global"] = Field(
        default="local",
        description="설명 유형 — local: 개별 예측, global: 전체 모델"
    )
    method: Literal["shap", "lime", "both"] = Field(
        default="both",
        description="사용할 설명 방법"
    )
    target_instance_idx: Optional[int] = Field(
        default=None,
        description="local 설명 시 대상 인스턴스 인덱스"
    )
    max_features: int = Field(
        default=20, ge=1, le=100,
        description="설명에 포함할 최대 피처 수"
    )
    background_sample_size: int = Field(
        default=100, ge=10, le=1000,
        description="SHAP KernelExplainer 배경 데이터 샘플 크기"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model_ref": "model://quant-node/stock-predictor-v2",
                "input_data": {
                    "columns": ["price", "volume", "rsi", "macd"],
                    "rows": [[150.5, 1200000, 65.3, 0.85]]
                },
                "explain_type": "local",
                "method": "both",
                "target_instance_idx": 0,
                "max_features": 10,
                "background_sample_size": 100
            }
        }
```

---

## E2. Output Schema

```python
class FeatureExplanation(BaseModel):
    feature_name: str
    importance: float = Field(description="피처 중요도 (절대값)")
    direction: Literal["positive", "negative"] = Field(
        description="예측에 대한 기여 방향"
    )
    value: Optional[float] = Field(default=None, description="해당 인스턴스의 피처 값")

class ShapLimeResponse(BaseModel):
    """COND-011 출력 스키마"""
    feature_importances: list[FeatureExplanation] = Field(
        description="피처 중요도 리스트 (중요도 내림차순)"
    )
    explanation_plot: Optional[bytes] = Field(
        default=None, description="시각화 이미지 (PNG, base64 인코딩)"
    )
    summary: str = Field(
        description="자연어 설명 요약"
    )
    shap_values: Optional[dict] = Field(
        default=None, description="SHAP values raw data"
    )
    lime_weights: Optional[dict] = Field(
        default=None, description="LIME feature weights"
    )
    base_value: Optional[float] = Field(
        default=None, description="SHAP base value (expected value)"
    )
    prediction: Optional[float] = Field(
        default=None, description="모델 예측값"
    )
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")

    class Config:
        json_schema_extra = {
            "example": {
                "feature_importances": [
                    {"feature_name": "rsi", "importance": 0.45, "direction": "positive", "value": 65.3},
                    {"feature_name": "macd", "importance": 0.32, "direction": "positive", "value": 0.85},
                    {"feature_name": "volume", "importance": 0.15, "direction": "negative", "value": 1200000},
                    {"feature_name": "price", "importance": 0.08, "direction": "positive", "value": 150.5}
                ],
                "summary": "RSI(65.3)와 MACD(0.85)가 매수 신호에 가장 큰 양의 기여를 하고 있으며, 거래량(1.2M)은 소폭 음의 영향을 미칩니다.",
                "base_value": 0.52,
                "prediction": 0.78,
                "execution_time_ms": 1250
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION explain(request: ShapLimeRequest) -> ShapLimeResponse:
    # 1. 모델 로드
    model = ModelRegistry.load(request.model_ref)
    df = DataFrame.from_dict(request.input_data)

    results = {}
    instance = None
    base_value = None
    plot = None

    # 2. SHAP 설명
    IF request.method in ("shap", "both"):
        IF model.type == "tree":
            explainer = shap.TreeExplainer(model)
        ELSE:
            background = shap.sample(df, request.background_sample_size)
            explainer = shap.KernelExplainer(model.predict, background)

        IF request.explain_type == "local":
            instance = df.iloc[request.target_instance_idx]
            shap_values = explainer.shap_values(instance)
            base_value = explainer.expected_value
            plot = shap.waterfall_plot(shap_values, max_display=request.max_features)
        ELSE:  # global
            shap_values = explainer.shap_values(df)
            plot = shap.summary_plot(shap_values, df, max_display=request.max_features)

        results["shap"] = {values: shap_values, base: base_value, plot: plot}

    # 3. LIME 설명
    IF request.method in ("lime", "both"):
        lime_explainer = LimeTabularExplainer(
            training_data=df.values,
            feature_names=df.columns,
            mode="regression" if model.output_type == "continuous" else "classification"
        )

        IF request.explain_type == "local":
            instance = df.iloc[request.target_instance_idx].values
            lime_exp = lime_explainer.explain_instance(
                instance, model.predict, num_features=request.max_features
            )
            results["lime"] = {weights: lime_exp.as_map(), html: lime_exp.as_html()}

    # 4. 피처 중요도 통합
    importances = merge_explanations(results, method=request.method)
    importances.sort(key=lambda x: abs(x.importance), reverse=True)
    importances = importances[:request.max_features]

    # 5. 자연어 요약 생성
    summary = generate_nl_summary(importances, model.name, request.explain_type)

    RETURN ShapLimeResponse(
        feature_importances=importances,
        explanation_plot=encode_plot(plot),
        summary=summary,
        shap_values=results.get("shap", {}).get("values"),
        lime_weights=results.get("lime", {}).get("weights"),
        base_value=results.get("shap", {}).get("base"),
        prediction=model.predict(instance),
        execution_time_ms=elapsed_ms()
    )
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_011_MODEL_NOT_FOUND` | model_ref에 해당하는 모델이 레지스트리에 없음 | `F-011-01` | "지정된 모델을 찾을 수 없습니다." |
| `COND_011_MODEL_INCOMPATIBLE` | 모델이 SHAP/LIME과 호환되지 않는 유형 | `F-011-02` | "해당 모델 유형은 설명가능AI를 지원하지 않습니다." |
| `COND_011_DATA_SCHEMA_MISMATCH` | input_data 컬럼이 모델 입력 스키마와 불일치 | `F-011-03` | "입력 데이터 스키마가 모델과 일치하지 않습니다." |
| `COND_011_INSTANCE_IDX_OOB` | target_instance_idx가 데이터 범위 초과 | `F-011-04` | "대상 인스턴스 인덱스가 범위를 초과했습니다." |
| `COND_011_COMPUTATION_TIMEOUT` | SHAP/LIME 연산이 timeout_ms 초과 | `F-011-05` | "설명 생성 시간이 초과되었습니다. 데이터 크기를 줄여 주세요." |
| `COND_011_MEMORY_EXCEEDED` | 연산 중 메모리 초과 | `F-011-06` | "메모리 한계를 초과했습니다. background_sample_size를 줄여 주세요." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_011_MODEL_NOT_FOUND",
    message="Model not found in registry: {model_ref}",
    fallback_id="F-011-01",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-A 내부 의존 (§A.2.1)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **제공** (A-1) | COND-026 (편향감사) → COND-011 | 편향 원인 분석 시 피처 중요도 참조 | ②③ |

> COND-011은 **제공 전용** — CAT-A 내부에서 소비하는 모듈 없음 (Level 0)

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |
| **I-19 (QoD)** | 설명 결과의 근거 품질 검증 | **추가** |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `shap` | ≥0.43 | SHAP 연산 |
| `lime` | ≥0.2 | LIME 연산 |
| `matplotlib` | ≥3.7 | 시각화 플롯 |
| `numpy` | ≥1.24 | 수치 연산 |
| `pandas` | ≥2.0 | DataFrame 처리 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| GPU (선택) | TreeExplainer 가속 |
| 메모리 ≥ 4GB | KernelExplainer 배경 데이터 처리 |

---

## E6. Performance Benchmark

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **Local SHAP (Tree)** | ≤ 500ms (100 features) | TreeExplainer, 단일 인스턴스 |
| **Local SHAP (Kernel)** | ≤ 5,000ms (100 features, 100 background) | KernelExplainer, 단일 인스턴스 |
| **Global SHAP** | ≤ 30,000ms (1000 rows, 100 features) | TreeExplainer, 전체 데이터셋 |
| **LIME Local** | ≤ 3,000ms (100 features) | LimeTabularExplainer |
| **메모리 사용량** | ≤ 2GB (1000 rows, 100 features) | peak RSS 측정 |
| **시각화 생성** | ≤ 500ms | matplotlib waterfall/summary plot |

### 병목 요인 및 최적화
- **KernelExplainer**: 배경 데이터 크기에 비례하여 느려짐 → `background_sample_size` 제한
- **Global SHAP**: 데이터 크기에 선형 → 샘플링 + 병렬 처리
- **메모리**: 대규모 데이터셋 → chunked 연산 적용

---

## E7. Integration Test Spec

### 시나리오 1: 로컬 SHAP 설명 (Tree 모델)
```yaml
name: "local_shap_tree_model"
setup:
  - register_model("test-tree-v1", type="random_forest", features=["f1", "f2", "f3"])
  - prepare_data(rows=100, features=3)
input:
  model_ref: "model://test/test-tree-v1"
  input_data: {columns: ["f1", "f2", "f3"], rows: [[1.0, 2.0, 3.0]]}
  explain_type: "local"
  method: "shap"
  target_instance_idx: 0
expected:
  - feature_importances.length == 3
  - all(fi.importance >= 0 for fi in feature_importances)
  - sum(fi.importance for fi in feature_importances) > 0
  - summary is not empty
  - execution_time_ms < 1000
```

### 시나리오 2: SHAP + LIME 동시 실행
```yaml
name: "both_shap_lime"
setup:
  - register_model("test-linear-v1", type="logistic_regression", features=["a", "b", "c", "d"])
  - prepare_data(rows=200, features=4)
input:
  model_ref: "model://test/test-linear-v1"
  input_data: {columns: ["a", "b", "c", "d"], rows: [[0.5, 1.5, -0.3, 2.1]]}
  explain_type: "local"
  method: "both"
  target_instance_idx: 0
  max_features: 4
expected:
  - shap_values is not None
  - lime_weights is not None
  - feature_importances.length == 4
  - explanation_plot is not None (PNG bytes)
```

### 시나리오 3: 에러 — 모델 미존재
```yaml
name: "error_model_not_found"
input:
  model_ref: "model://test/nonexistent"
  input_data: {columns: ["x"], rows: [[1.0]]}
  method: "shap"
expected:
  - error.failure_code == "COND_011_MODEL_NOT_FOUND"
  - error.fallback_id == "F-011-01"
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
| **게이트 요구** | policy, evidence |
| **우선순위** | HIGH |

### 호출 패턴
```
User → "이 주식 예측 결과가 왜 이렇게 나왔어?"
  → ORANGE CORE (I-1 Intent 해석: explain_prediction)
    → I-5 라우팅 → Research Node
      → Research Node: COND-011.execute(model_ref="stock-predictor-v2", ...)
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (정책 위반 없음)
          [2] CostGate — 해당 없음 (LLM 추론 비용 미수반)
          [3] EvidenceGate ✅ (근거 QoD 충족)
          → COND-011 실행 → ShapLimeResponse 반환
            → Research Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.a.011.initialized` | initialize() 완료 |
| 설명 시작 | `cond.a.011.execute_start` | execute() 진입 |
| 설명 완료 | `cond.a.011.execute_done` | 정상 반환 |
| 설명 실패 | `cond.a.011.execute_fail` | VamosError 발생 |
| 헬스체크 | `cond.a.011.health` | health_check() 호출 |
| 모듈 종료 | `cond.a.011.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-011", "execution_ms": N, "result_type": "explanation" }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond011ShapLime(BaseModule):
    """COND-011 SHAP/LIME 설명가능AI"""

    async def initialize(self) -> Result[None, VamosError]:
        """모델 레지스트리 연결, SHAP/LIME 라이브러리 초기화"""
        self._registry = await ModelRegistry.connect()
        self._emit_event("cond.a.011.initialized")
        return Ok(None)

    async def execute(self, request: ShapLimeRequest) -> Result[ShapLimeResponse, VamosError]:
        """Runnable.run() 위임 — SHAP/LIME 설명 생성"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """모델 레지스트리 연결 상태 + SHAP/LIME 가용성 확인"""
        registry_ok = await self._registry.ping()
        return Ok(HealthStatus(healthy=registry_ok, latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        """리소스 해제, 캐시 정리"""
        await self._registry.disconnect()
        self._emit_event("cond.a.011.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-011", version="1.0.0",
            capabilities=["shap_explain", "lime_explain", "feature_importance"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond011Config(ModuleConfig):
    """COND-011 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 3
    timeout_ms: int = 30000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=1, backoff_ms=1000)

    # COND-011 전용 설정
    default_method: Literal["shap", "lime", "both"] = "both"
    default_max_features: int = 20
    max_background_samples: int = 500
    enable_gpu_acceleration: bool = True
    plot_format: Literal["png", "svg"] = "png"
    plot_dpi: int = 150
    cache_explanations: bool = True
    cache_ttl_seconds: int = 3600
```
