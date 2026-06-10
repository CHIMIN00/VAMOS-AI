# COND-100 건강 인사이트 (Health Insights)

> **Status**: V2-Phase 2
> **모듈 ID**: COND-100
> **카테고리**: CAT-F Wellbeing
> **우선순위**: MEDIUM
> **버전**: V2 (Phase 2, 2026-04-19)
> **작성 단계**: STAGE 7 / Phase 7-II / 2-2 STEP_B / 세션 2-2
> **Phase 1 대응**: 종합명세 §100 + `06_cat-f-wellbeing/_index.md`
> **LOCK 준수**: LOCK-CD-01 / LOCK-CD-03 / LOCK-CD-04 / LOCK-CD-05 / LOCK-CD-06 / LOCK-CD-10 + LOCK-CD-08 (Wellness Node P2 종속)

---

## §0 교차 참조 블록 (정본)

- **종합계획서**: `COND_MODULES_DETAIL_구조화_종합계획서.md` §7.4 L836~L893 / §13.1
- **종합명세**: `COND_MODULES_종합명세.md` §#100 (I/O 정의 L1336~L1346)
- **AUTHORITY_CHAIN**: `AUTHORITY_CHAIN.md` §4 LOCK-CD-01~11
- **Blue Node 정본**: `D2.0-03 §5` (Wellness Node P2)
- **ErrorHandlingStandard 정본**: `D2.0-02 §0.3`
- **Runnable Protocol 정본**: `D2.0-02 §1.2-A`
- **교차 도메인**: `3-6 Health-Wellness-EmotionAI` LOCK-HW-01/02/03/04/06/10/11 (집계 허브 역할) / `6-2 Security-Governance` / `6-12 Event-Logging` (COND_100_*)

---

## §1 개요

### 1.1 목적
여러 건강 데이터 소스(수면·운동·식단·감정·사회적 관계)를 통합 분석하여 종합 건강 인사이트를 도출한다. Multi-source Data Fusion + Correlation Analysis + Trend Detection + Personalized Health Scoring 기법으로 다차원 상관관계를 발견하고 개인화된 실행 항목을 제안한다.

### 1.2 핵심 기술
- **Multi-source Data Fusion**: COND-095/096/097/098/099 5 source aggregation (집계형 모듈)
- **Correlation Analysis**: Pearson / Spearman / Kendall (비모수), 시차 상관 (lag 1-7d)
- **Trend Detection**: Mann-Kendall 추세 검정 + STL 분해 (seasonal/trend/residual)
- **Personalized Health Scoring**: VWS 100 점 기반 (LOCK-HW-11 verbatim) — 수면 20 + 운동 20 + 감정 20 + 사회적연결 20 + 생산성균형 20

### 1.3 ⚠️ Medical Disclaimer (LOCK-HW-04 verbatim + 필수 재인용)
> ⚠️ **Medical Disclaimer**: VAMOS는 의료 서비스가 아닙니다. 본 모듈의 통합 건강 인사이트는 건강 참고용이며 의학적 진단·치료·처방이 아닙니다. 특정 상관관계(예: 수면-혈압·체중-우울)가 발견되더라도 의학적 결론을 내릴 수 없습니다. 만성 질환이나 이상 증상이 의심될 경우 반드시 전문의와 상담하십시오. 본 모듈 실행 전 사용자는 opt-in 동의 플로우를 완료해야 합니다.

### 1.4 ⚠️ Privacy Policy 요약 (§7.4 L866~L876 필수 게이트)
- **수집 필드**: **소스 모듈의 집계 결과만 수집**, 원시 데이터 수집 금지 (aggregated_scores, trend_flags, correlations). `IntegratedHealthData.sleep/fitness/nutrition/mood` 는 각 소스 모듈에서 가져온 **집계 뷰** 만 참조
- **처리 목적**: 건강 축 간 상관관계 발견 + 실행 항목 제안. 광고 / 제3자 공유 / 보험 적용 절대 금지 (LOCK-HW-02 PROTECTED 등급)
- **보존 기간**: 집계 인사이트 **365일 (기본)** — 장기 추세 분석 필요. 원본 데이터는 소스 모듈 정책 따름 (수면 30d / 운동 90d / 식단 180d / 감정 365d / 사회 90d)
- **삭제 정책**: GDPR Right to Erasure — 72시간 내 하드 삭제. 원본 데이터 각 소스 모듈 정책 적용
- **암호화**: at-rest **AES-256-GCM + KMS envelope encryption**, in-transit **TLS 1.3**

### 1.5 LOCK 준수 요약
| LOCK | 준수 내용 |
|---|---|
| LOCK-CD-01 | COND-100 체계 준수 |
| LOCK-CD-03 | BaseModule ABC 4 메서드 구현 |
| LOCK-CD-04 | Runnable 프로토콜 |
| LOCK-CD-05 | Result<T, VamosError> 반환 |
| LOCK-CD-06 | VamosError 4필드 필수 |
| LOCK-CD-08 | Wellness Node P2 세션별 승인 |
| LOCK-CD-10 | ModuleConfig 5필드 |

---

## §2 Input Schema (Pydantic v2) — §13.1 #1

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal
from datetime import datetime

class AggregatedSleep(BaseModel):
    """COND-095 소스 집계. 원시 stage 제외."""
    period: str
    avg_quality_score: float = Field(..., ge=0.0, le=100.0)
    pattern: Literal["consistent", "drifting", "fragmented", "insufficient"]
    avg_hygiene_score: int = Field(..., ge=0, le=100)

class AggregatedFitness(BaseModel):
    """COND-096 소스 집계. HR 원시 샘플 제외."""
    period: str
    weekly_hours: float
    ctl: float
    atl: float
    tsb: float
    injury_risk_high_count: int = Field(..., ge=0)

class AggregatedNutrition(BaseModel):
    """COND-097 소스 집계. meal_log 원문 제외."""
    period: str
    avg_daily_kcal: float
    macro_ratio: dict[Literal["carb", "protein", "fat"], float]
    deficiency_score: float = Field(..., ge=0.0, le=1.0)

class AggregatedMood(BaseModel):
    """COND-098 소스 집계. text/distortion 원문 제외."""
    period: str
    avg_valence: float
    avg_arousal: float
    avg_intensity: float
    trend: Literal["improving", "stable", "declining", "volatile"]
    crisis_score_max: float = Field(..., ge=0.0, le=1.0)

class AggregatedSocial(BaseModel):
    """COND-099 소스 집계. contact_hash 제외."""
    period: str
    isolation_risk: float = Field(..., ge=0.0, le=1.0)
    strong_tie_count: int
    avg_weekly_interactions: float

class IntegratedHealthData(BaseModel):
    sleep: AggregatedSleep | None = None
    fitness: AggregatedFitness | None = None
    nutrition: AggregatedNutrition | None = None
    mood: AggregatedMood | None = None
    social: AggregatedSocial | None = None

class HealthInsightsInput(BaseModel):
    """COND-100 실행 입력. 종합명세 §#100 계약 준수 — 집계 데이터만."""
    user_id_hashed: str = Field(..., min_length=16, max_length=128)
    health_data: IntegratedHealthData
    insight_type: Literal["summary", "trend", "correlation"] = "summary"
    analysis_window_days: int = Field(default=30, ge=7, le=365)
    consent_flags: dict[Literal["multi_source_aggregation", "cross_domain_correlation"], bool] = Field(
        default_factory=dict
    )

    @field_validator("health_data")
    @classmethod
    def at_least_two_sources(cls, v: IntegratedHealthData) -> IntegratedHealthData:
        sources = [v.sleep, v.fitness, v.nutrition, v.mood, v.social]
        if sum(s is not None for s in sources) < 2:
            raise ValueError("health_data requires at least 2 sources for correlation")
        return v
```

### 2.1 예시
```json
{
  "user_id_hashed": "SHA256:9a8b...cdef",
  "health_data": {
    "sleep": {"period": "2026-03-20/2026-04-19", "avg_quality_score": 72.0,
               "pattern": "drifting", "avg_hygiene_score": 78},
    "fitness": {"period": "2026-03-20/2026-04-19", "weekly_hours": 5.0,
                 "ctl": 42.0, "atl": 48.0, "tsb": -6.0, "injury_risk_high_count": 0},
    "mood": {"period": "2026-03-20/2026-04-19", "avg_valence": 0.2,
              "avg_arousal": 0.1, "avg_intensity": 5.8, "trend": "stable", "crisis_score_max": 0.15}
  },
  "insight_type": "correlation",
  "analysis_window_days": 30,
  "consent_flags": {"multi_source_aggregation": true, "cross_domain_correlation": true}
}
```

---

## §3 Output Schema (Pydantic v2) — §13.1 #2

```python
from pydantic import BaseModel, Field
from typing import Literal

class HealthInsight(BaseModel):
    insight_id: str
    category: Literal["summary", "correlation", "trend", "deficit", "strength"]
    title: str
    description: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    sources: list[Literal["sleep", "fitness", "nutrition", "mood", "social"]]

class HealthCorrelation(BaseModel):
    correlation_id: str
    source_a: Literal["sleep", "fitness", "nutrition", "mood", "social"]
    source_b: Literal["sleep", "fitness", "nutrition", "mood", "social"]
    metric_a: str
    metric_b: str
    coefficient: float = Field(..., ge=-1.0, le=1.0, description="Pearson/Spearman coefficient")
    lag_days: int = Field(default=0, ge=-7, le=7)
    p_value: float = Field(..., ge=0.0, le=1.0)
    interpretation: str = Field(..., description="비의료 해석 주의")

class ActionItem(BaseModel):
    action_id: str
    priority: Literal["high", "medium", "low"]
    category: str
    title: str
    related_modules: list[str]
    estimated_impact: Literal["minor", "moderate", "significant"]

class VwsScore(BaseModel):
    """LOCK-HW-11 verbatim: 수면(0-20)+운동(0-20)+감정(0-20)+사회적연결(0-20)+생산성균형(0-20)=0-100"""
    sleep: float = Field(..., ge=0.0, le=20.0)
    fitness: float = Field(..., ge=0.0, le=20.0)
    mood: float = Field(..., ge=0.0, le=20.0)
    social: float = Field(..., ge=0.0, le=20.0)
    productivity_balance: float = Field(..., ge=0.0, le=20.0)
    total: float = Field(..., ge=0.0, le=100.0)

class HealthInsightsOutput(BaseModel):
    analysis_id: str
    insights: list[HealthInsight] = Field(..., min_length=1, max_length=20)
    correlations: list[HealthCorrelation] = Field(default_factory=list)
    action_items: list[ActionItem] = Field(default_factory=list, max_length=10)
    vws_score: VwsScore
    pii_removed: bool
    medical_disclaimer_shown: bool
    retention_expires_at: datetime
```

### 3.1 예시
```json
{
  "analysis_id": "HIA-2026-04-19-9a8b",
  "insights": [
    {"insight_id": "HI-1", "category": "correlation",
     "title": "수면 품질 낮은 날 → 2일 후 감정 valence 저하",
     "description": "최근 30일 데이터에서 sleep.avg_quality_score < 60 날 이후 2일 mood.avg_valence 평균 -0.15 (p=0.018). (비의료 해석)",
     "confidence": 0.72, "sources": ["sleep", "mood"]}
  ],
  "correlations": [
    {"correlation_id": "C-1", "source_a": "sleep", "source_b": "mood",
     "metric_a": "avg_quality_score", "metric_b": "avg_valence",
     "coefficient": -0.48, "lag_days": 2, "p_value": 0.018,
     "interpretation": "수면 품질과 2일 후 감정 상관 (의학적 인과 아님)"}
  ],
  "action_items": [
    {"action_id": "AI-1", "priority": "medium", "category": "sleep_hygiene",
     "title": "취침 시간 일관성 개선 (±30분 이내)", "related_modules": ["COND-095"],
     "estimated_impact": "moderate"}
  ],
  "vws_score": {"sleep": 14.4, "fitness": 16.0, "mood": 12.0, "social": 14.0, "productivity_balance": 15.0, "total": 71.4},
  "pii_removed": true,
  "medical_disclaimer_shown": true,
  "retention_expires_at": "2027-04-19T00:00:00Z"
}
```

---

## §4 Algorithm Pseudocode — §13.1 #3

### 4.1 전체 흐름
```
ALGORITHM HealthInsights(input: HealthInsightsInput) -> Result<Output, VamosError>:
    # 1. Consent gate
    IF NOT input.consent_flags.get("multi_source_aggregation", False) THEN
        RETURN Err(VamosError("COND_100_CONSENT_MISSING", ...))

    # 2. 소스 2개 미만 검증 (correlation 불가)
    sources = [s for s in [sleep, fitness, nutrition, mood, social] if s is not None]
    IF len(sources) < 2: RETURN Err("COND_100_INSUFFICIENT_SOURCES")

    # 3. PII 마스킹 검증 (각 소스 집계 결과만 수용, 원시 데이터 감지 시 차단)
    anonymized = verify_no_raw_data(input.health_data)
    VALIDATE no_raw_pii(anonymized)

    # 4. 상관 분석 (pairwise, 시차 1~7일)
    correlations = []
    FOR (a, b) IN combinations(sources, 2):
        FOR lag IN range(-7, 8):
            coeff, p = spearman_rank_correlation(a.time_series, b.time_series, lag=lag)
            IF abs(coeff) >= 0.3 AND p < 0.05:
                correlations.append(HealthCorrelation(
                    source_a=a.name, source_b=b.name,
                    coefficient=coeff, lag_days=lag, p_value=p,
                    interpretation=neutral_text(coeff, "상관 (인과 아님)"),
                ))

    # 5. 추세 감지 (Mann-Kendall + STL)
    trends = {}
    FOR source IN sources:
        mk_stat, mk_p = mann_kendall_test(source.time_series)
        stl = stl_decompose(source.time_series, period=7)
        trends[source.name] = {"direction": sign(mk_stat), "p": mk_p,
                                "seasonal_amplitude": stl.seasonal.std()}

    # 6. 인사이트 생성 (상관 + 추세 + 임계값 기반)
    insights = []
    FOR c IN correlations[:10]:
        insights.append(HealthInsight(category="correlation", sources=[c.source_a, c.source_b], ...))
    FOR name, t IN trends.items():
        IF t["p"] < 0.05:
            insights.append(HealthInsight(category="trend", sources=[name], ...))

    # 7. 실행 항목 생성 (상관이 강한 축에 개입 가능한 실행)
    action_items = []
    FOR c IN top_actionable_correlations(correlations):
        action_items.append(generate_action(c))

    # 8. VWS 스코어 계산 (LOCK-HW-11 verbatim 5축 × 20점)
    sleep_score = sleep_to_20(sleep.avg_quality_score, sleep.avg_hygiene_score) if sleep is not None else 0.0
    fitness_score = fitness_to_20(fitness.weekly_hours, fitness.tsb, fitness.injury_risk_high_count) if fitness is not None else 0.0
    mood_score = mood_to_20(mood.avg_valence, mood.avg_intensity, mood.crisis_score_max) if mood is not None else 0.0
    social_score = social_to_20(social.isolation_risk, social.strong_tie_count) if social is not None else 0.0
    productivity_score = productivity_to_20(sleep, fitness, nutrition) if (sleep is not None or fitness is not None or nutrition is not None) else 0.0
    vws = VwsScore(
        sleep=sleep_score,
        fitness=fitness_score,
        mood=mood_score,
        social=social_score,
        productivity_balance=productivity_score,
        total=sum([sleep_score, fitness_score, mood_score, social_score, productivity_score]),
    )

    # 9. Output 조립 + retention
    expires_at = now() + timedelta(days=365)

    RETURN Ok(HealthInsightsOutput(
        analysis_id=uuid4(),
        insights=insights[:20], correlations=correlations[:30],
        action_items=action_items[:10], vws_score=vws,
        pii_removed=True, medical_disclaimer_shown=True,
        retention_expires_at=expires_at,
    ))
```

### 4.2 시간 복잡도
- **상관 분석**: `O(C(K,2) · (L + 1))` — K=5 sources, L=15 lag range → 10 × 15 = 150 pair-lag 계산
- **Mann-Kendall**: `O(N · log N)` per source, N=time series length ≤ 365
- **STL 분해**: `O(N · P)` per source, P=period=7
- **전체**: `O(K · N log N + C(K,2) · L · N)`; K=5, N=365, L=15 → ≤ 3M ops, p99 ≤ 900ms
- **LOCK 값 참조**: LOCK-CD-11 V2 ₩93K — 경량 통계, 월 ₩5K

### 4.3 VWS Scoring 공식 (LOCK-HW-11 verbatim 5축)
```
LOCK-HW-11 정본: 수면(0-20)+운동(0-20)+감정(0-20)+사회적연결(0-20)+생산성균형(0-20)=0-100

sleep_to_20(q, h)       = 0.7*q/100*20 + 0.3*h/100*20         (quality 주 + hygiene 보조)
fitness_to_20(w, t, i)  = clip(w/5.0*14 + (6+t)/12*4 + (1-i/3)*2, 0, 20)
mood_to_20(v, i, c)     = clip((v+1)/2*12 + i/10*4 + (1-c)*4, 0, 20)
social_to_20(r, t)      = clip((1-r)*12 + min(t, 10)/10*8, 0, 20)
productivity_to_20(...) = sleep_consistency + meal_regularity + workout_adherence 합산
```

### 4.4 비의료 해석 주의 (LOCK-HW-04 + LOCK-HW-09)
- 모든 correlation 의 `interpretation` 필드에 "상관 (인과 아님)" 명시 강제
- "진단" / "치료" / "처방" / "병명" 단어 출력 금지 (출력 필터로 자동 차단)
- 강한 상관 (|coeff| ≥ 0.7) 발견 시에도 "추세 참고 — 의료 상담 권장" 추가 문구

---

## §5 Error Handling — §13.1 #4 (LOCK-CD-05 / LOCK-CD-06)

### 5.1 FailureCode 체계
```python
COND_100_CONSENT_MISSING
COND_100_INSUFFICIENT_SOURCES       # 2 source 미만
COND_100_RAW_DATA_DETECTED           # 집계 아닌 원시 데이터 감지 → 즉시 차단
COND_100_PII_LEAK_DETECTED
COND_100_CORRELATION_COMPUTE_FAIL
COND_100_MEDICAL_TERM_DETECTED       # 출력에 금지 단어 (진단/치료/병명) 감지
COND_100_RETENTION_POLICY_VIOLATION
COND_100_USER_NOT_FOUND
COND_100_MEDICAL_DISCLAIMER_FAIL
```

### 5.2 Phase별 복구 전략
```
Phase 1 (Validation): Pydantic 자동 차단
Phase 2 (Consent gate): 재동의 플로우
Phase 3 (Sources): 2 source 미만 → summary insight 만 반환 (correlation 생략)
Phase 4 (Raw data): 원시 데이터 감지 → fail-closed (LOCK-HW-02 집계만 허용)
Phase 5 (Correlation): 통계 계산 실패 → Pearson 단독 fallback (Spearman 포기)
Phase 6 (Medical term): 금지 단어 감지 → 자동 치환 (예: "진단" → "참고 지표") + warning log
Phase 7 (Escalation): I-20 에스컬레이션 (aggregated data 배제)
```

### 5.3 Escalation Payload
```python
class EscalationPayload(BaseModel):
    source_engine: str = "COND-100"
    error_code: str
    user_id_hashed: str
    vws_total: float | None = None   # 숫자만
    retry_count: int
    timestamp: datetime
    # aggregated source data 배제
```

### 5.4 로깅 포맷 (R-01-7)
```json
{
  "trace_id": "trace-9a8b-...",
  "error": {"code": "COND_100_RAW_DATA_DETECTED", "severity": "ERROR"},
  "context": {"user_id_hashed": "SHA256:9a8b...", "module": "COND-100", "phase": "raw_data_guard"},
  "recovery": {"strategy": "fail_closed", "fallback_id": null}
}
```

---

## §6 Dependency Map — §13.1 #5

### 6.1 내부 의존 (CAT-F 내부) — **집계 허브 성격 (수신측)**
| 대상 | 방향 | 이유 |
|---|---|---|
| COND-095 수면 개선 | CONSUMES | AggregatedSleep 집계 결과 수신 |
| COND-096 운동/피트니스 | CONSUMES | AggregatedFitness 집계 결과 수신 |
| COND-097 식단/영양 | CONSUMES | AggregatedNutrition 집계 결과 수신 |
| COND-098 감정 일지 | CONSUMES | AggregatedMood 집계 결과 수신 |
| COND-099 사회적 관계 | CONSUMES | AggregatedSocial 집계 결과 수신 |
| COND-116 웰빙 대시보드 | PROVIDES | 통합 인사이트 + VWS 점수 공급 |

### 6.2 외부 의존
| 대상 | 방향 | 이유 |
|---|---|---|
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-01 | CROSS-DOMAIN | 감정 분류 모델 정본 (COND-098 간접) |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-02 | CROSS-DOMAIN | PROTECTED 등급 (집계 데이터도 동급) |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-03 | CROSS-DOMAIN | 집계 데이터 365일 retention (연장 opt-in) |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-04 | CROSS-DOMAIN | 비의료 면책 원문 재인용 + 출력 필터 |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-06 | CROSS-DOMAIN | AES-256-GCM |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-10 | CROSS-DOMAIN | VBS-17 기준 (감정인식 ≥ 80%, 웰빙개선 ≥ 10%) — 인사이트 품질 게이트 |
| `3-6 Health-Wellness-EmotionAI` LOCK-HW-11 | CROSS-DOMAIN | **VWS 점수 구조 verbatim 5축 × 20점 = 100 점 체계 소비** |
| `6-2 Security-Governance` | CROSS-DOMAIN | PII 마스킹 + GDPR + 의료 단어 필터 |
| `6-12 Event-Logging` | CROSS-DOMAIN | COND_100_* FailureCode |

### 6.3 의존성 매트릭스 (CAT-F — 집계 허브 중심) — §6 Dependency Map 방향성 주의 (수신측)
```
            095  096  097  098  099  100  101  116
COND-100  [  C    C    C    C    C    -    .    P ]   C=CONSUMES (집계 허브), P=PROVIDES
```

### 6.4 §A 매트릭스 cross-check
§A.1 A↔F: 본 모듈 직접 무관. COND-098 경유로 간접 소비.

### 6.5 Phase 1 deferral 인계
- 본 모듈은 deferral 생성 없음

---

## §7 Performance Benchmark — §13.1 #6

### 7.1 SLA 기준값
| 지표 | V1 기준 | V2 목표 |
|---|---|---|
| p50 응답 시간 | N/A | ≤ 380 ms (상관 분석 지배) |
| p99 응답 시간 | N/A | ≤ 900 ms (5 source × 15 lag) |
| 처리량 | N/A | ≥ 70 req/s |
| 상관 발견 recall | N/A | ≥ 0.85 @ precision ≥ 0.8 | vs. 학술 benchmark |
| PII 마스킹 성공률 | N/A | 100% fail-closed |
| 메모리 사용 | N/A | ≤ 384 MB |

### 7.2 비용 상한 참조 (LOCK-CD-11)
- V2 ₩93K 한도. 경량 통계 → 월 추정 ₩5K
- 365일 집계 retention 스토리지 ₩2K/사용자/년

### 7.3 벤치마크 시나리오
```
BENCH-100-01: 5 source × 365일 × 500회 → p50/p99
BENCH-100-02: 2 source 최소 + short window 7d → minimum viable insights
BENCH-100-03: 원시 데이터 주입 합성 → fail-closed 검증
BENCH-100-04: "진단" 단어 주입 시도 → 자동 치환 동작
```

---

## §8 Integration Test Spec (I-05) — §13.1 #7 (≥ 3 + ⚠️ 프라이버시 침해 필수)

### 8.1 I-05-COND100-01: 정상 5 source 통합 분석
- **목적**: 모든 5 source 집계 + consent 완비 시 완전 인사이트
- **기대**: `insights.length >= 5`, `correlations.length >= 2`, `vws_score.total` 계산 성공, `pii_removed == True`
- **목 데이터**: `mocks/COND-100/happy_path_all_sources.json`

### 8.2 I-05-COND100-02: ⚠️ 프라이버시 침해 — 원시 데이터 주입 (필수)
- **목적**: `health_data.mood` 에 `JournalEntry.text` 원문 포함 시 fail-closed
- **기대**:
  - `Result.is_err()`, `failure_code == "COND_100_RAW_DATA_DETECTED"`
  - **원시 텍스트 응답/로그 0% 노출** (fail-closed)
  - ERROR 이벤트 발행
- **목 데이터**: `mocks/COND-100/privacy_raw_mood_text.json`

### 8.3 I-05-COND100-03: VWS 점수 계산 (LOCK-HW-11 verbatim)
- **목적**: 5 sub-score 각 상한 20점 + 합계 100점 상한 검증
- **주입**: 모든 축 최대값
- **기대**: `vws_score.sleep <= 20`, `.fitness <= 20`, ..., `.total <= 100`, **5 축 합 정확히 일치**
- **목 데이터**: `mocks/COND-100/vws_max.json`

### 8.4 I-05-COND100-04 (추가): 의료 단어 필터 동작
- **목적**: 인사이트 description 에 "진단" / "치료" 합성 주입 → 자동 치환
- **기대**: 출력 description 에서 "진단" → "참고 지표", warning log
- **목 데이터**: `mocks/COND-100/medical_term_filter.json`

### 8.5 Phase 3 시나리오 확장 (≥ 5 시나리오)
| ID | 제목 | 주입 | 기대 |
|---|---|---|---|
| 100-S5 | 2 source 미만 | sleep only | `COND_100_INSUFFICIENT_SOURCES` → summary only fallback |
| 100-S6 | 시차 상관 | 수면-감정 2일 lag 주입 | `lag_days == 2` 상관 발견 |
| 100-S7 | Retention 365일 초과 | old insight | `COND_100_RETENTION_POLICY_VIOLATION` + 자동 폐기 |
| 100-S8 | Right to Erasure | delete_user | 72h 하드 삭제 + 소스 모듈 각자 정책 적용 |
| 100-S9 | Trace 전파 | `trace_id=T-xxx` | 일치 |
| 100-S10 | VBS-17 품질 게이트 | 낮은 품질 mock | LOCK-HW-10 기준 미달 warning |
| 100-S11 | PII 우회 시도 | raw user_id | `COND_100_PII_LEAK_DETECTED` fail-closed |

---

## §9 Blue Node Integration (LOCK-CD-04 / LOCK-CD-08) — §13.1 #8

### 9.1 Blue Node 소비 계약
- **Wellness Node** / **P2 (세션별 승인)** / 독립 실행 금지
- **집계 허브**: 5 source 모듈 출력을 CONSUMES 하는 수신측

### 9.2 Runnable 프로토콜
```python
class HealthInsights(BaseModule, Runnable):
    def initialize(self, config: ModuleConfig) -> None: ...
    def execute(self, input: HealthInsightsInput) -> Result[HealthInsightsOutput, VamosError]: ...
    def run(self, input: HealthInsightsInput) -> Result[HealthInsightsOutput, VamosError]: ...
    def health_check(self) -> HealthStatus: ...
    def get_metadata(self) -> ModuleMetadata: ...
    def shutdown(self) -> None: ...
```

### 9.3 ModuleConfig (LOCK-CD-10)
```python
config = ModuleConfig(
    enabled=True,
    priority=2,
    max_concurrent=10,
    timeout_ms=2500,
    retry_policy=RetryPolicy(max_retries=1, backoff="exponential"),
)
```

### 9.4 Permission Level
```
P2: Wellness Node 세션별 opt-in (multi-source 통합 동의 필요)
P0: 관리자 (인사이트 품질 게이트 업데이트, LOCK-HW-11 공식 조정)
```

### 9.5 Blue Node Event (6-12)
```
COND_100_INSIGHTS_GENERATED       INFO    user_id_hashed, vws_total, insights_count
COND_100_RAW_DATA_DETECTED         ERROR   user_id_hashed, source (fail-closed)
COND_100_MEDICAL_TERM_FILTERED     WARN    user_id_hashed, filter_count
COND_100_CORRELATION_COMPUTE_FAIL  WARN    user_id_hashed, fallback
COND_100_PII_LEAK_DETECTED         ERROR   user_id_hashed, context (fail-closed)
```

---

## §10 V2-Phase 2 변경 이력

| 버전 | 일자 | 변경 요약 | 근거 |
|---|---|---|---|
| V1 | 2026-03-22 | 초기 골격 (SHELL L1) | Phase 1 산출 이전 |
| V2 | 2026-04-19 | L3 상세 + Privacy (집계만 허용) + Medical Disclaimer + VWS LOCK-HW-11 verbatim 5축 + 의료 단어 필터 + 집계 허브 수신측 명시 | STAGE 7 Phase 7-II 2-2 STEP_B 세션 2-2 |

### 10.1 Pydantic 재사용 출처
- `ModuleConfig` 재사용: `common_types.md §3.4` (LOCK-CD-10 정본)
- `VamosError` 재사용: `D2.0-02 §0.3` (LOCK-CD-06 정본)
- `Result[T, E]` 재사용: `D2.0-02 §0.3` (LOCK-CD-05 정본)

---

**[END OF COND-100 V2]** — L3 8 항목 전수 + CAT-F 특수 게이트 전수 + **집계 허브 수신측** 성격 명시 (§6 CAT-F 내부 5 소스 CONSUMES + COND-116 PROVIDES). LOCK-CD-01/03/04/05/06/08/10 + LOCK-HW-01/02/03/04/06/10/11 cross-domain (VWS 5축 verbatim). I-05 11 시나리오 (핵심 4 + 프라이버시 침해 1 필수 + 확장 7). 원시 데이터 차단 + 의료 단어 필터 + 비의료 해석 강제.
