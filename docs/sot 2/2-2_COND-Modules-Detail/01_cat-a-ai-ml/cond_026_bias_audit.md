# COND-026: 편향감사 엔진 — L3 상세 명세

> **모듈 ID**: COND-026
> **카테고리**: CAT-A (AI/ML Engine)
> **이름**: 편향감사 엔진
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

class BiasAuditRequest(BaseModel):
    """COND-026 입력 스키마"""
    model_ref: str = Field(
        ..., description="VAMOS 모델 레지스트리의 모델 참조 ID"
    )
    test_dataset: dict = Field(
        ..., description="DataFrame으로 변환될 테스트 데이터셋 (columns + rows)"
    )
    protected_attributes: list[str] = Field(
        ..., min_length=1,
        description="보호 속성 목록 (예: gender, race, age)"
    )
    fairness_metrics: list[str] = Field(
        default=["disparate_impact", "statistical_parity", "equalized_odds"],
        min_length=1,
        description="적용할 공정성 메트릭 목록"
    )
    label_column: str = Field(
        default="label",
        description="실제 라벨 컬럼명"
    )
    favorable_label: int = Field(
        default=1,
        description="유리한 결과 라벨 값"
    )
    threshold: float = Field(
        default=0.8, ge=0.0, le=1.0,
        description="Disparate Impact 허용 임계값 (0.8 = 80% rule)"
    )
    include_shap_analysis: bool = Field(
        default=True,
        description="COND-011 SHAP 연동을 통한 편향 원인 분석 포함 여부"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "model_ref": "model://quant-node/credit-scorer-v3",
                "test_dataset": {
                    "columns": ["income", "age", "gender", "race", "credit_score", "label"],
                    "rows": [
                        [50000, 35, "M", "white", 720, 1],
                        [48000, 32, "F", "black", 710, 0],
                        [52000, 40, "M", "asian", 730, 1]
                    ]
                },
                "protected_attributes": ["gender", "race"],
                "fairness_metrics": ["disparate_impact", "statistical_parity", "equalized_odds"],
                "label_column": "label",
                "favorable_label": 1,
                "threshold": 0.8,
                "include_shap_analysis": true
            }
        }
```

---

## E2. Output Schema

```python
class FairnessMetricResult(BaseModel):
    metric_name: str = Field(description="메트릭 이름")
    attribute: str = Field(description="보호 속성")
    privileged_group: str = Field(description="특권 그룹 값")
    unprivileged_group: str = Field(description="비특권 그룹 값")
    value: float = Field(description="메트릭 산출값")
    threshold: float = Field(description="허용 임계값")
    passed: bool = Field(description="임계값 충족 여부")
    interpretation: str = Field(description="결과 해석 (자연어)")

class BiasReport(BaseModel):
    overall_bias_detected: bool = Field(description="편향 감지 여부")
    metrics: list[FairnessMetricResult] = Field(description="메트릭별 결과")
    most_biased_attribute: Optional[str] = Field(
        default=None, description="가장 편향이 심한 보호 속성"
    )
    bias_severity: Literal["none", "low", "medium", "high", "critical"] = Field(
        description="편향 심각도"
    )
    shap_bias_factors: Optional[list[dict]] = Field(
        default=None, description="COND-011 연동 SHAP 편향 원인 분석 (피처별 기여)"
    )

class MitigationAction(BaseModel):
    action_type: Literal["reweighting", "resampling", "threshold_adjustment", "feature_removal", "adversarial_debiasing"] = Field(
        description="완화 조치 유형"
    )
    target_attribute: str = Field(description="대상 보호 속성")
    description: str = Field(description="조치 상세 설명")
    expected_improvement: float = Field(
        ge=0.0, le=1.0, description="예상 개선 비율"
    )

class MitigationPlan(BaseModel):
    actions: list[MitigationAction] = Field(description="권고 완화 조치 목록")
    priority_order: list[int] = Field(description="우선순위 순서 (actions 인덱스)")
    estimated_effort: Literal["low", "medium", "high"] = Field(
        description="예상 구현 노력"
    )

class BiasAuditResponse(BaseModel):
    """COND-026 출력 스키마"""
    bias_report: BiasReport = Field(
        description="편향 감사 보고서"
    )
    recommendations: list[str] = Field(
        description="편향 완화 권고사항 (자연어)"
    )
    mitigation_plan: MitigationPlan = Field(
        description="편향 완화 계획"
    )
    dataset_stats: dict = Field(
        description="테스트 데이터셋 통계 (그룹별 분포)"
    )
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")

    class Config:
        json_schema_extra = {
            "example": {
                "bias_report": {
                    "overall_bias_detected": True,
                    "metrics": [
                        {
                            "metric_name": "disparate_impact",
                            "attribute": "gender",
                            "privileged_group": "M",
                            "unprivileged_group": "F",
                            "value": 0.65,
                            "threshold": 0.8,
                            "passed": False,
                            "interpretation": "여성 그룹의 승인율이 남성 대비 65%로 80% 임계값 미달"
                        },
                        {
                            "metric_name": "statistical_parity",
                            "attribute": "gender",
                            "privileged_group": "M",
                            "unprivileged_group": "F",
                            "value": -0.18,
                            "threshold": 0.1,
                            "passed": False,
                            "interpretation": "여성 그룹의 승인률 차이 -18%p로 허용 범위 초과"
                        }
                    ],
                    "most_biased_attribute": "gender",
                    "bias_severity": "high",
                    "shap_bias_factors": [
                        {"feature": "income", "contribution_to_bias": 0.35},
                        {"feature": "credit_score", "contribution_to_bias": 0.25}
                    ]
                },
                "recommendations": [
                    "gender 속성에 대해 reweighting 기법 적용 권고",
                    "income 피처의 그룹간 분포 차이 검토 필요",
                    "승인 임계값의 그룹별 보정 고려"
                ],
                "mitigation_plan": {
                    "actions": [
                        {
                            "action_type": "reweighting",
                            "target_attribute": "gender",
                            "description": "학습 데이터에 그룹별 가중치 부여하여 균형 확보",
                            "expected_improvement": 0.15
                        },
                        {
                            "action_type": "threshold_adjustment",
                            "target_attribute": "gender",
                            "description": "그룹별 결정 임계값 차등 적용",
                            "expected_improvement": 0.10
                        }
                    ],
                    "priority_order": [0, 1],
                    "estimated_effort": "medium"
                },
                "dataset_stats": {
                    "total_rows": 10000,
                    "gender": {"M": 5500, "F": 4500},
                    "favorable_rate": {"M": 0.72, "F": 0.47}
                },
                "execution_time_ms": 4500
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION audit_bias(request: BiasAuditRequest) -> BiasAuditResponse:
    # 1. 모델 로드
    model = ModelRegistry.load(request.model_ref)
    IF model is None:
        RETURN Err(COND_026_MODEL_NOT_FOUND)

    # 2. 데이터셋 구성
    df = DataFrame.from_dict(request.test_dataset)
    IF len(df) < MIN_DATASET_SIZE:
        RETURN Err(COND_026_DATASET_TOO_SMALL)

    # 3. 보호 속성 검증
    FOR attr IN request.protected_attributes:
        IF attr NOT IN df.columns:
            RETURN Err(COND_026_ATTRIBUTE_NOT_FOUND, attribute=attr)

    # 4. 모델 예측 생성
    feature_cols = [c for c in df.columns if c != request.label_column and c not in request.protected_attributes]
    predictions = model.predict(df[feature_cols])
    df["prediction"] = predictions

    # 5. 그룹별 통계 산출
    dataset_stats = compute_group_stats(df, request.protected_attributes, request.label_column)

    # 6. 공정성 메트릭 계산
    metric_results = []
    FOR metric_name IN request.fairness_metrics:
        FOR attr IN request.protected_attributes:
            groups = df[attr].unique()
            privileged, unprivileged = identify_groups(df, attr, request.label_column)
            rate_priv = df[df[attr]==privileged]["prediction"].mean()
            rate_unpriv = df[df[attr]==unprivileged]["prediction"].mean()
            rate_priv = df[df[attr]==privileged]["prediction"].mean()
            rate_unpriv = df[df[attr]==unprivileged]["prediction"].mean()

            TRY:
                IF metric_name == "disparate_impact":
                    # DI = P(Y=1|unprivileged) / P(Y=1|privileged)
                    rate_priv = df[df[attr]==privileged]["prediction"].mean()
                    rate_unpriv = df[df[attr]==unprivileged]["prediction"].mean()
                    value = rate_unpriv / rate_priv IF rate_priv > 0 ELSE 0
                    passed = value >= request.threshold

                ELIF metric_name == "statistical_parity":
                    # SPD = P(Y=1|unprivileged) - P(Y=1|privileged)
                    value = rate_unpriv - rate_priv
                    passed = abs(value) <= (1 - request.threshold)

                ELIF metric_name == "equalized_odds":
                    # EOD: TPR difference + FPR difference
                    tpr_diff = compute_tpr_diff(df, attr, privileged, unprivileged, request.label_column)
                    fpr_diff = compute_fpr_diff(df, attr, privileged, unprivileged, request.label_column)
                    value = max(abs(tpr_diff), abs(fpr_diff))
                    passed = value <= (1 - request.threshold)

            EXCEPT ComputationError:
                RETURN Err(COND_026_METRIC_COMPUTATION_FAILED, metric=metric_name, attribute=attr)

            interpretation = generate_metric_interpretation(metric_name, attr, value, passed)
            metric_results.append(FairnessMetricResult(
                metric_name=metric_name, attribute=attr,
                privileged_group=privileged, unprivileged_group=unprivileged,
                value=value, threshold=request.threshold,
                passed=passed, interpretation=interpretation
            ))

    # 7. SHAP 편향 원인 분석 (COND-011 연동)
    shap_bias_factors = None
    IF request.include_shap_analysis:
        shap_result = COND_011.execute(ShapLimeRequest(
            model_ref=request.model_ref,
            input_data=request.test_dataset,
            explain_type="global",
            method="shap"
        ))
        IF shap_result.is_err():
            RETURN Err(COND_026_SHAP_INTEGRATION_FAILED)
        shap_bias_factors = correlate_shap_with_bias(
            shap_result.value.feature_importances, request.protected_attributes
        )

    # 8. 편향 보고서 생성
    overall_biased = any(NOT m.passed for m in metric_results)
    most_biased = find_most_biased_attribute(metric_results)
    severity = compute_severity(metric_results)

    bias_report = BiasReport(
        overall_bias_detected=overall_biased,
        metrics=metric_results,
        most_biased_attribute=most_biased,
        bias_severity=severity,
        shap_bias_factors=shap_bias_factors
    )

    # 9. 권고사항 및 완화 계획 생성
    recommendations = generate_recommendations(bias_report)
    mitigation_plan = generate_mitigation_plan(bias_report, df)

    RETURN BiasAuditResponse(
        bias_report=bias_report,
        recommendations=recommendations,
        mitigation_plan=mitigation_plan,
        dataset_stats=dataset_stats,
        execution_time_ms=elapsed_ms()
    )
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_026_MODEL_NOT_FOUND` | model_ref에 해당하는 모델이 레지스트리에 없음 | `F-026-01` | "지정된 모델을 찾을 수 없습니다." |
| `COND_026_DATASET_TOO_SMALL` | 테스트 데이터셋 크기가 통계적 유의성 기준 미달 | `F-026-02` | "데이터셋이 너무 작습니다. 최소 100건 이상의 데이터가 필요합니다." |
| `COND_026_ATTRIBUTE_NOT_FOUND` | protected_attributes에 지정된 컬럼이 데이터셋에 없음 | `F-026-03` | "보호 속성 '{attribute}'이(가) 데이터셋에 존재하지 않습니다." |
| `COND_026_METRIC_COMPUTATION_FAILED` | 공정성 메트릭 연산 중 오류 (분모 0, NaN 등) | `F-026-04` | "메트릭 '{metric}' 연산에 실패했습니다. 데이터 분포를 확인해 주세요." |
| `COND_026_SHAP_INTEGRATION_FAILED` | COND-011 SHAP 분석 연동 실패 | `F-026-05` | "편향 원인 분석(SHAP)에 실패했습니다. SHAP 분석 없이 결과를 제공합니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_026_MODEL_NOT_FOUND",
    message="Model not found in registry: {model_ref}",
    fallback_id="F-026-01",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-A 내부 의존 (§A.2.1)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| **소비** (A-1) | COND-026 → COND-011 (SHAP/LIME) | 편향 원인 분석 시 피처 중요도 참조 | ②③ |

> COND-026은 COND-011을 **소비** (Level 1) — SHAP 결과로 편향 기여 피처 식별

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |
| **I-19 (QoD)** | 편향 결과의 근거 품질 검증 | **추가** |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `aif360` | ≥0.6 | IBM AI Fairness 360 메트릭 연산 |
| `fairlearn` | ≥0.9 | Microsoft Fairlearn 편향 완화 |
| `numpy` | ≥1.24 | 수치 연산 |
| `pandas` | ≥2.0 | DataFrame 처리 |
| `scikit-learn` | ≥1.3 | 모델 예측 + 메트릭 보조 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| CPU 충분 | 메트릭 연산 (GPU 불필요) |
| 메모리 ≥ 4GB | 대규모 테스트 데이터셋 처리 |

---

## E6. Performance Benchmark

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **DI 계산** | ≤ 500ms (10K rows, 5 attributes) | 그룹별 비율 연산 |
| **SPD 계산** | ≤ 500ms (10K rows, 5 attributes) | 그룹별 확률 차이 |
| **EOD 계산** | ≤ 1,000ms (10K rows, 5 attributes) | TPR/FPR 그룹별 비교 |
| **전체 감사 (SHAP 미포함)** | ≤ 5,000ms (10K rows, 3 metrics, 3 attributes) | 전체 파이프라인 |
| **전체 감사 (SHAP 포함)** | ≤ 35,000ms (10K rows) | SHAP 연동 포함 |
| **완화 계획 생성** | ≤ 2,000ms | 메트릭 결과 기반 규칙 엔진 |
| **메모리 사용량** | ≤ 2GB (50K rows, 100 features) | peak RSS 측정 |

### 병목 요인 및 최적화
- **SHAP 연동**: COND-011 호출 비용 → `include_shap_analysis=false` 옵션으로 스킵 가능
- **대규모 데이터셋**: 메트릭 연산 → 샘플링 + 부트스트랩 신뢰구간
- **다중 속성**: 속성별 병렬 연산

---

## E7. Integration Test Spec

### 시나리오 1: 성별 편향 감지 (DI 위반)
```yaml
name: "gender_bias_disparate_impact"
setup:
  - register_model("test-classifier-v1", type="logistic_regression", features=["f1", "f2", "f3"])
  - prepare_biased_dataset(rows=1000, bias_attribute="gender", bias_ratio=0.6)
input:
  model_ref: "model://test/test-classifier-v1"
  test_dataset: {columns: ["f1", "f2", "f3", "gender", "label"], rows: "...1000 rows..."}
  protected_attributes: ["gender"]
  fairness_metrics: ["disparate_impact", "statistical_parity"]
  label_column: "label"
  favorable_label: 1
  threshold: 0.8
  include_shap_analysis: false
expected:
  - bias_report.overall_bias_detected == true
  - bias_report.most_biased_attribute == "gender"
  - bias_report.bias_severity in ("medium", "high", "critical")
  - len(bias_report.metrics) == 2
  - any(not m.passed for m in bias_report.metrics)
  - len(recommendations) >= 1
  - len(mitigation_plan.actions) >= 1
  - execution_time_ms < 5000
```

### 시나리오 2: 편향 없는 모델 확인
```yaml
name: "no_bias_detected"
setup:
  - register_model("test-fair-v1", type="random_forest", features=["f1", "f2", "f3"])
  - prepare_fair_dataset(rows=1000, attributes=["gender", "race"])
input:
  model_ref: "model://test/test-fair-v1"
  test_dataset: {columns: ["f1", "f2", "f3", "gender", "race", "label"], rows: "...1000 rows..."}
  protected_attributes: ["gender", "race"]
  fairness_metrics: ["disparate_impact", "statistical_parity", "equalized_odds"]
  threshold: 0.8
  include_shap_analysis: true
expected:
  - bias_report.overall_bias_detected == false
  - bias_report.bias_severity == "none"
  - all(m.passed for m in bias_report.metrics)
  - bias_report.shap_bias_factors is not None
```

### 시나리오 3: 에러 — 보호 속성 미존재
```yaml
name: "error_attribute_not_found"
input:
  model_ref: "model://test/test-classifier-v1"
  test_dataset: {columns: ["f1", "f2", "label"], rows: [[1.0, 2.0, 1]]}
  protected_attributes: ["gender"]
  fairness_metrics: ["disparate_impact"]
expected:
  - error.failure_code == "COND_026_ATTRIBUTE_NOT_FOUND"
  - error.fallback_id == "F-026-03"
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
User → "이 신용 평가 모델에 성별 편향이 있는지 감사해줘"
  → ORANGE CORE (I-1 Intent 해석: bias_audit)
    → I-5 라우팅 → Research Node
      → Research Node: COND-026.execute(model_ref="credit-scorer-v3", ...)
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (정책 위반 없음)
          [2] CostGate — 해당 없음 (LLM 추론 비용 미수반)
          [3] EvidenceGate ✅ (메트릭 근거 QoD 충족, I-19 검증)
          → COND-026 실행 → BiasAuditResponse 반환
            → (내부) COND-011.execute() SHAP 연동
            → Research Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.a.026.initialized` | initialize() 완료 |
| 감사 시작 | `cond.a.026.execute_start` | execute() 진입 |
| 감사 완료 | `cond.a.026.execute_done` | 정상 반환 |
| 감사 실패 | `cond.a.026.execute_fail` | VamosError 발생 |
| 헬스체크 | `cond.a.026.health` | health_check() 호출 |
| 모듈 종료 | `cond.a.026.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-026", "execution_ms": N, "result_type": "bias_report" }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond026BiasAudit(BaseModule):
    """COND-026 편향감사 엔진"""

    async def initialize(self) -> Result[None, VamosError]:
        """모델 레지스트리 연결, AIF360/Fairlearn 초기화, COND-011 참조 획득"""
        self._registry = await ModelRegistry.connect()
        self._cond_011 = await ModuleRegistry.get("COND-011")  # SHAP 연동
        self._aif360 = AIF360Wrapper()
        self._fairlearn = FairlearnWrapper()
        self._emit_event("cond.a.026.initialized")
        return Ok(None)

    async def execute(self, request: BiasAuditRequest) -> Result[BiasAuditResponse, VamosError]:
        """Runnable.run() 위임 — 편향 감사 실행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """모델 레지스트리 연결 상태 + COND-011 가용성 확인"""
        registry_ok = await self._registry.ping()
        cond_011_ok = await self._cond_011.health_check() if self._cond_011 else True
        return Ok(HealthStatus(healthy=registry_ok and cond_011_ok, latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        """리소스 해제"""
        await self._registry.disconnect()
        self._emit_event("cond.a.026.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-026", version="1.0.0",
            capabilities=["bias_detection", "fairness_metrics", "mitigation_planning", "shap_bias_analysis"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond026Config(ModuleConfig):
    """COND-026 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "high"
    max_concurrent: int = 3
    timeout_ms: int = 35000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=1, backoff_ms=1000)

    # COND-026 전용 설정
    default_metrics: list[str] = ["disparate_impact", "statistical_parity", "equalized_odds"]
    default_threshold: float = 0.8
    min_dataset_size: int = 100
    min_group_size: int = 30
    enable_shap_integration: bool = True
    shap_timeout_ms: int = 30000
    severity_thresholds: dict[str, float] = {
        "critical": 0.5, "high": 0.65, "medium": 0.75, "low": 0.80
    }
    bootstrap_iterations: int = 1000
    confidence_level: float = 0.95
    report_format: Literal["json", "html", "pdf"] = "json"
    cache_audit_results: bool = True
    cache_ttl_seconds: int = 7200
```
