# S-4 Performance Monitor — 상세 설계 (L3)

> **수정 정책**: 정본 — Phase 변경 시 갱신 (§8.2)
> **도메인**: 6-6_Self-Evolution-System / 01_s-series-modules
> **Tier**: 6 (System-wide Components)
> **정본 출처**: D2.0-02 §10.4~§10.6 (LOCK), D2.0-01 §5.7 (명칭 LOCK), Part2 V3-Phase 2 (S-4 정의), 종합계획서 부록 A.3 (EWMA)
> **LOCK 매핑**: L1(모듈 목록), L2(I-Module 경유), L6(순차 활성화 — S-3 안정화 후), L7(BaseSelfEvo ABC)
> **Phase**: P1-M3
> **생성일**: 2026-04-14
> **ISS 해결**: ISS-1 (S-4 알고리즘 힌트 소비 — EWMA λ=0.3, 3σ)

---

## 교차 참조 블록 (Rule a)

| 참조 대상 | 관계 |
|----------|------|
| **D2.0-02 §10.4~§10.6** | S-Module 경유 동작 원칙 정본 (LOCK L2) |
| **D2.0-01 §5.7** | S-Module 명칭·카테고리 LOCK (S-4 = "Performance Monitor") |
| **Part2 V3-Phase 2** | S-4 When/Where 정본(상시 5분 주기), BaseSelfEvo ABC 시그니처 정본 |
| **종합계획서 §7 P1-M3, 부록 A.3** | EWMA(Exponentially Weighted Moving Average) 힌트 — λ=0.3, μ±3σ, 경고: QoD<0.85 / latency>2s / cost_daily>일일상한 80% |
| **01_s-series-modules/_index.md** | S-4 역할·I/O·트리거(§1.1), I-Module 접근 매트릭스 §2.3(S-4 = I-6/I-9/I-14 READ), BaseSelfEvo ABC(§3.1), 에러 핸들링(§3.2) 정본 |
| **AUTHORITY_CHAIN.md §4** | LOCK L1/L2/L6/L7 레지스트리 |
| **s02_pattern_miner.md (P1-M1)** | S-4 이상 탐지 → S-2 out-of-band 트리거 대상 (본 파일 §4.5) |
| **s03_strategy_optimizer.md (P1-M2)** | S-4 `oc.self_evo.s04.anomaly`를 관찰 → S-3 재평가 루프(모니터링 루프 — _index.md §1.2) |
| **s06_adaptation_engine.md (P1-M5 예정)** | S-4 `alert` → S-6 트리거(적응 루프 — _index.md §1.2) — 공급 계약 §9 |
| **s08_governance (P2 예정)** | 임계값 자동 조정(evolve)·rollback 의 거버넌스 승인(L3 경유) |
| **02_self-improvement-loop/** | 5단계 루프(L5) 중 "Detect(S-1/S-4)" 단계 (ISS-3) |
| **6-12 Event-Logging** | `oc.self_evo.s04.*` 이벤트 기록 대상 (R-01-7 구조화 로깅) |
| **6-4 Memory-RAG-Storage** | I-15 스냅샷은 S-4 직접 접근 금지, S-8 대행(§3.2 정합) |
| **6-13 Operations / alertmanager** | S-4 alert fan-out 대상 (CRITICAL 등급) |

---

## 1. 개요

S-4 Performance Monitor는 Self-Evolution 서브시스템의 **성능 지표 실시간 추적 엔진**으로, I-9 메트릭 스트림과 I-6 QoD, I-14 QA 결과를 입력으로 **EWMA(Exponentially Weighted Moving Average, λ=0.3)** 기반 추세 추적 및 **μ±3σ 이상 탐지**를 수행한다. 이상 감지 시 (a) S-2 Pattern Miner에 out-of-band 트리거를 emit하고(모니터링 루프), (b) S-6 Adaptation Engine에 `alert`을 전달한다(적응 루프). 임계값 자동 조정·복원은 BaseSelfEvo ABC(L7) 시그니처로 구현하며, S-3 안정화(DH-1) 후 활성화(L6)된다.

### 1.1 책임 요약
- **실시간 추세 추적**: EWMA(λ=0.3) 기반 qod/latency/cost 3 트렌드 산출 (5분 주기)
- **이상 탐지**: 3σ 이탈 + 고정 임계값 2중(OR) 판정 — QoD<0.85, latency_p95>2000ms, cost_daily>일일상한 80%
- **S-2 out-of-band 트리거**: 이상 감지 시 S-2에 패턴 재마이닝 신호 (_index.md §1.2 "모니터링 루프")
- **S-6 alert 공급**: `EnvironmentState`로 투영하여 S-6 트리거 (_index.md §1.2 "적응 루프")
- **임계값 자동 조정(evolve)**: 가짜 경보율(FPR)·놓침율(FNR) 기반 λ·3σ 계수 자동 튜닝 (단, 반영은 S-8 승인 필요 — L3)
- **I-Module 경유(L2)**: I-6 READ, I-9 READ, I-14 READ (접근 매트릭스 §2.3 정본)
- **순차 활성화(L6)**: S-3 안정화(DH-1 통과) 후에만 활성화

### 1.2 입출력 요약 (01/_index.md §1.1 정합)
- **Input**: 시스템 메트릭 스트림 (I-9 READ) + QoD 조회 (I-6 READ) + QA 결과 (I-14 READ)
- **Output**: `PerformanceReport(qod_trend, latency_trend, cost_trend, alerts)`
- **트리거**: 상시 (5분 주기 스케줄) + on-demand (S-3 요청 시)

---

## 2. 공통 자료 구조 선정의 (Pydantic, Rule k)

> 본 모듈이 공급하는 `EnvironmentState`는 s06_adaptation_engine.md가 재사용한다. S-2 out-of-band 트리거 스키마는 s02 §2 `RegressionRequest`와 필드 집합이 다르므로(s02는 change_id/source_module/snapshot_id_before/after/metrics_before/after/applied_at 중심의 **사후 회귀 요청**, s04는 이상 탐지 시점의 **사전 트리거 힌트**) **클래스 명칭을 분리**하여 `S4TriggerRequest`로 정의한다(중복 정의 금지 원칙 준수). s02 측 `RegressionRequest`와는 `trace_id` 필드만 공유하며, S-2는 본 트리거를 받아 즉시 재마이닝을 수행할 뿐 L8 회귀 테스트 경로와는 독립적이다.

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

# ── EWMA 상태 ───────────────────────────────────────────────
class EwmaState(BaseModel):
    """EWMA 추적 상태 — 메트릭당 1건"""
    metric_key: Literal["qod", "latency_p50", "latency_p95",
                        "error_rate", "cost_daily"]
    lam: float = 0.3                 # smoothing factor λ ∈ (0,1]
    mean: float                      # S_t (EWMA 평균)
    var: float                       # EWMVar (EWMA 분산)
    sample_count: int
    last_update: datetime

# ── 입력 보조 스키마 (I-9 스트림) ────────────────────────────
class MetricSample(BaseModel):
    """I-9에서 READ하는 단일 메트릭 샘플"""
    ts: datetime
    qod: Optional[float] = None         # 0.0~1.0
    latency_p50_ms: Optional[float] = None
    latency_p95_ms: Optional[float] = None
    error_rate: Optional[float] = None  # 0.0~1.0
    cost_delta: Optional[float] = None  # 주기 내 누적 비용 증분
    source: Literal["i9_log", "i6_qod", "i14_qa"]

# ── 트렌드 구조 ─────────────────────────────────────────────
class TrendPoint(BaseModel):
    ts: datetime
    value: float
    ewma: float
    upper_3s: float                  # μ + 3σ
    lower_3s: float                  # μ - 3σ
    breached: bool = False

class Trend(BaseModel):
    metric_key: str
    window_start: datetime
    window_end: datetime
    points: list[TrendPoint]
    slope: float                     # 선형 추세(보조)
    recent_mean: float
    recent_std: float

# ── 알림 ───────────────────────────────────────────────────
class PerformanceAlert(BaseModel):
    alert_id: str                    # hash(metric_key+ts+kind)
    metric_key: str
    kind: Literal["threshold_fixed", "anomaly_3sigma", "cost_cap"]
    severity: Literal["info", "warn", "error", "critical"]
    observed: float
    expected_range: dict             # {lower, upper}
    triggered_at: datetime
    message: str

# ── 출력 스키마 (01/_index.md §1.1 정합) ────────────────────
class PerformanceReport(BaseModel):
    """S-4 → S-2(out-of-band), S-6(alert), S-3(관찰) 전달 정본"""
    report_id: str
    window_start: datetime
    window_end: datetime
    qod_trend: Trend
    latency_trend: Trend
    cost_trend: Trend
    alerts: list[PerformanceAlert]
    generated_at: datetime

# ── S-6 공급용 투영 스키마 (s06 재사용) ─────────────────────
class EnvironmentState(BaseModel):
    """S-6 Adaptation Engine 트리거 입력 (_index.md §1.1 S-6 행)"""
    load: float                      # CPU/IO 추정 부하
    error_rate: float
    user_count: int
    qod_level: float
    source_report_id: str

# ── S-2 out-of-band 트리거 스키마 (s02 RegressionRequest와는 독립) ──
class S4TriggerRequest(BaseModel):
    """S-4 → S-2 (모니터링 루프) 이상 탐지 사전 트리거.

    s02 §2 `RegressionRequest`(사후 회귀 요청)와 **필드 집합·목적이 다르므로
    별도 클래스로 정의**한다(중복 정의 금지 원칙 준수). S-2는 본 요청을
    받아 즉시 out-of-band 재마이닝을 수행한다.
    """
    request_id: str
    reason_code: Literal["QOD_DEGRADE", "LATENCY_SPIKE",
                         "ERROR_RATE_SPIKE", "COST_CAP_NEAR",
                         "ANOMALY_3SIGMA"]
    anchor_metric: str
    anchor_value: float
    window_start: datetime
    window_end: datetime
    trace_id: str

# ── BaseSelfEvo 반환 구조 (L7 정본, s02/s03 정합) ───────────
class EvolutionResult(BaseModel):
    module_id: str = "s04"
    report: Optional[PerformanceReport]
    threshold_adjustments: list[dict]   # evolve() 튜닝 결과
    submitted_plans: list[str]          # S-8에 제출된 plan_id (임계값 변경 시)
    approved_count: int = 0
    rejected_count: int = 0
    snapshot_id: Optional[str] = None
    duration_ms: int
    status: Literal["SUCCESS", "PARTIAL", "FAILED"]

class HealthStatus(BaseModel):
    module_id: str = "s04"
    healthy: bool
    last_run_at: Optional[datetime]
    error_count_7d: int
    schema_validation_rate: float
    imodule_call_success_rate: float
    anomaly_fpr_7d: float               # 가짜 경보율
    anomaly_fnr_7d: float               # 놓침율

# ── 에스컬레이션 페이로드 (I-20, R-01-8, s02/s03 정합) ──────
class EscalationPayload(BaseModel):
    source_engine: str = "s04_performance_monitor"
    error_code: str
    original_request: dict
    partial_result: Optional[dict]
    retry_count: int
    timestamp: datetime
    trace_id: str
    severity: Literal["info", "warn", "error", "critical"]
```

---

## 3. BaseSelfEvo ABC 구현 명세 (LOCK L7)

> 정본: 01_s-series-modules/_index.md §3.1. **시그니처 임의 변경 금지(Rule h/i).**
> Part2 V3-P2 정본: `async def evolve()`, `async def evaluate() -> float`, `async def rollback(snapshot_id: str) -> bool`.

### 3.1 클래스 스켈레톤

```python
class PerformanceMonitor(BaseSelfEvo):
    """S-4 Performance Monitor — L7 BaseSelfEvo 구현.

    정본 시그니처 준수:
      - evolve() -> EvolutionResult        # 임계값 자동 조정 제안 (S-8 승인 경유)
      - evaluate() -> float                # 이상 탐지 정확도(FPR/FNR 기반)
      - rollback(snapshot_id: str) -> bool # 이전 임계값·EWMA 상태 복원(S-8 대행)

    순차 활성화(L6): S-3 DH-1 안정화(에러율<1%, 스키마 검증률=100%,
    3주기 연속 PASS) 확인 후에만 활성화.

    주의: 5분 주기 모니터링 루프 본체는 evolve()와 분리된 내부 스케줄로
    동작하며, 이상 탐지 시 S-2/S-6에 직접 트리거한다. evolve()는
    "임계값/λ 자동 튜닝 제안"에 한정되며, 반영은 L3/L4에 따라 S-8 경유.
    """

    MODULE_ID = "s04"
    DEFAULT_LAMBDA = 0.3
    SIGMA_K = 3.0
    CYCLE_SEC = 300  # 5분 주기 (_index.md §1.1)

    async def evolve(self) -> EvolutionResult:
        """임계값·λ 자동 조정 후보 산출 + S-8 승인 제출.

        단계:
          1) INPUT: 최근 7일 alerts + QoD/latency/cost 트렌드
                    (I-6/I-9/I-14 READ)
          2) FPR/FNR 계산: 승인된 S-3 전략과 실제 QoD 개선 비교 후
                           경보↔전략 상관도 기반 FPR, 미트리거↔QoD 하락
                           기반 FNR 추정
          3) λ 튜닝: FPR 높으면 λ↓(평활 강화), FNR 높으면 λ↑(민감도↑)
          4) 3σ 계수 튜닝: 필요 시 k ∈ [2.5, 3.5] 범위
          5) threshold_adjustments[] 구성 → EvolutionPlan 변환 → S-8 제출
          6) I-9 이벤트 기록(oc.self_evo.s04.tuned, trace_id)
          7) S-8 응답 수집 — 자동 반영 경로 보유 금지(L4)
        """

    async def evaluate(self) -> float:
        """모듈 성능 점수 (0.0~1.0).

        공식:
          score = 0.5 * (1 - fpr) + 0.4 * (1 - fnr) + 0.1 * schema_ok_rate
            - fpr: 가짜 경보율 (최근 7일)
            - fnr: 놓침율 (실제 QoD 하락 대비 미트리거)
            - schema_ok_rate: Pydantic 검증률
        DH-1 안정화 기준(에러율<1%, 스키마 100%)을 하한으로 강제.
        """

    async def rollback(self, snapshot_id: str) -> bool:
        """I-15 스냅샷 기반 임계값·EWMA 상태 복원.

        - S-4는 I-15 직접 접근 권한 없음(§3.2, _index.md §2.3)
          → S-8에 복원 요청 emit (s03과 동일 대행 패턴)
        - 실패 시 SELF_EVO_ROLLBACK_FAIL → ADMIN+ 에스컬레이션(I-20)
        """

    def get_module_id(self) -> str:
        return self.MODULE_ID

    async def health_check(self) -> HealthStatus:
        ...

    # ── 내부 모니터링 루프 (ABC 외, 5분 주기) ────────────────
    async def tick(self) -> PerformanceReport:
        """5분 주기 샘플 수집 → EWMA 갱신 → 이상 탐지 → 트리거.

        1) samples ← I9.read_stream(window=5m)  # L2
        2) qod    ← I6.read_qod(window=5m)
        3) qa     ← I14.read_qa(window=5m)
        4) FOR each metric_key: UPDATE_EWMA(state, sample)
        5) alerts ← DETECT_ANOMALIES(states, thresholds)
        6) IF alerts: EMIT_TRIGGERS(alerts)   # S-2, S-6
        7) report  ← BUILD_REPORT(states, alerts)
        8) I9.emit_event("oc.self_evo.s04.report", {report_id,...})
        9) RETURN report
        """
```

### 3.2 I-Module 접근 권한 (정본: 01/_index.md §2.3)

| I-Module | 권한 | 용도 |
|----------|------|------|
| I-6 QoD | **READ** | QoD 시계열 조회 (qod_trend 산출) |
| I-9 로그/메트릭 | **READ** | 메트릭 스트림 조회 + 이벤트 기록 요청 위탁 |
| I-14 QA | **READ** | QA 실패율·회귀 테스트 결과 조회 |
| I-12 워크플로우 | — | 직접 접근 금지 |
| I-15 스냅샷 | — | 직접 접근 금지 (S-8 대행 — L3 정합, rollback 시) |
| I-18 스케줄/메타학습 | — | 직접 접근 금지 (5분 주기는 6-13 Operations가 관리) |
| I-19 승인 | — | **직접 접근 금지** — S-8만 WRITE 보유. 임계값 변경은 S-8 경유(L3) |

> **주의 (Rule j 정합)**: 01/_index.md §2.3 접근 매트릭스 S-4 행은 **I-6 READ, I-9 READ, I-14 READ** 만 허용한다. 종합계획서 §7 P1-M3 절차(line 671) 의 "I-Module 경유 호출 순서: I-9(메트릭 수집) → I-6(QoD 측정) → I-15(스냅샷)" 기술에서 **I-15**는 S-4 직접 호출 대상이 아니라 rollback 시 **S-8이 대행**하는 경유 순서로 해석한다(s03 §3.2 SEVO-C003 확장과 동형). 본 파일은 정본 §2.3을 따르며, I-15 접근은 §4.7에서 S-8 대행 경로로 기술한다. 이 해석은 §10.2 CONFLICT 후보로 등재한다(SEVO-C003의 S-4 확장).

### 3.3 S-Module 간 연계 (트리거 out-edges)

| 대상 | 트리거 조건 | 스키마 | 루프 분류 |
|------|------------|--------|----------|
| **S-2 Pattern Miner** | 이상 탐지(any alert.severity ≥ warn) | `S4TriggerRequest` (§2) | 모니터링 루프 |
| **S-6 Adaptation Engine** | alert.severity ≥ error OR error_rate breach | `EnvironmentState` (§2) | 적응 루프 |
| **S-3 Strategy Optimizer** | `oc.self_evo.s04.anomaly` 이벤트 관찰 | 이벤트만 (pull 모델) | 관찰 루프 |
| **S-8 Governance** | evolve() 임계값 변경 제안 발생 | `EvolutionPlan` | L3 경유 |

---

## 4. 알고리즘 상세 (L3 의사코드, Rule f)

> 시간복잡도(Big-O) + LOCK 참조 + ABC 패턴 매핑.
> 힌트 출처: 종합계획서 부록 A.3 (S-4: EWMA λ=0.3, 3σ), _index.md §2.5 Line 174.

### 4.1 파이프라인 총괄 (tick() 본체 — 5분 주기)

```
ALGORITHM S4_Tick
INPUT:   window = 5min, lam = 0.3, k_sigma = 3.0,
         fixed_thresholds = {qod_min: 0.85,
                             latency_p95_max_ms: 2000,
                             cost_daily_ratio_max: 0.80}
OUTPUT:  PerformanceReport
LOCK:    L1(S-4), L2(I-6/I-9/I-14 READ), L6(S-3 선행 안정화), L7(ABC)
ABC-매핑: 내부 tick (evolve와 분리)

1. IF NOT S3_STABLE():                                  # L6 gate
2.   RETURN PerformanceReport(empty, note="S3_NOT_STABLE")
3. samples_m ← I9.read_metric_stream(window)            # O(n)
4. samples_q ← I6.read_qod_series(window)               # O(n)
5. samples_a ← I14.read_qa_results(window)              # O(n)
6. FOR k IN ["qod","latency_p50","latency_p95",
             "error_rate","cost_daily"]:
7.   state[k] ← UPDATE_EWMA(state[k], samples_for(k), lam)   # O(n)
8. alerts ← DETECT_ANOMALIES(state, fixed_thresholds, k_sigma)  # O(m)
9. report ← BUILD_REPORT(state, alerts, window)
10. FOR a IN alerts:
11.   IF a.severity >= "warn":
12.     EMIT_S2(S4TriggerRequest.from(a))               # 모니터링 루프
13.   IF a.severity >= "error" OR a.kind=="threshold_fixed(error_rate)":
14.     EMIT_S6(EnvironmentState.from(state, a))        # 적응 루프
15. I9.emit_event("oc.self_evo.s04.report",
                  {report_id, alert_count, trace_id})
16. RETURN report
```

**총 시간복잡도**: `O(n + m)`, n=윈도 내 샘플 수(≤ ~600/5min), m=메트릭 수(=5). 상수시간에 수렴하며 SELF_EVO_TIMEOUT(120s) 내부.

### 4.2 EWMA (Exponentially Weighted Moving Average)

```
ALGORITHM UPDATE_EWMA(state, samples, lam)
# Roberts 1959 / Lucas & Saccucci 1990.
# 시간복잡도: O(n), 공간 O(1) — 순차 갱신
# ABC-매핑: tick() 7단계 — 상태 갱신
INPUT:   state: EwmaState, samples: list[float], lam: float ∈ (0,1]
OUTPUT:  EwmaState (mutated)
LOCK:    부록 A.3 정본(λ=0.3 기본)

1. IF state.sample_count == 0:                           # 초기화(콜드)
2.   state.mean ← samples[0]
3.   state.var  ← 0.0
4.   start_idx  ← 1
5. ELSE:
6.   start_idx  ← 0
7. FOR i FROM start_idx TO len(samples)-1:
8.   x ← samples[i]
9.   diff ← x - state.mean
10.  state.mean ← state.mean + lam * diff                # S_t = S_{t-1} + λ·(x-S_{t-1})
11.  state.var  ← (1-lam) * state.var + lam * diff*diff  # EWMVar
12.  state.sample_count += 1
13. state.last_update ← now()
14. RETURN state

POSTCONDITION:
  sigma_hat = sqrt(state.var)                            # σ̂ (EWMA 표준편차)
  bound_upper = state.mean + 3.0 * sigma_hat             # 3σ 상한
  bound_lower = state.mean - 3.0 * sigma_hat             # 3σ 하한
```

**파라미터 기본값**: `λ = 0.3` (부록 A.3), `k_sigma = 3.0`. 높은 λ → 민감(짧은 기억), 낮은 λ → 평활(긴 기억). evolve()가 FPR/FNR 관측 후 튜닝.

### 4.3 DETECT_ANOMALIES

```
ALGORITHM DETECT_ANOMALIES(states, fixed_thr, k_sigma)
# 시간복잡도: O(m), m=|states|=5
INPUT:   states: dict[metric_key → EwmaState], fixed_thr, k_sigma
OUTPUT:  list[PerformanceAlert]

1. alerts ← []
2. # (A) 3σ 이탈 기반 anomaly
3. FOR k, st IN states.items():
3a.  IF st.sample_count < 30: CONTINUE                  # S4_COLD_START — 3σ 경보 억제 (§5), fixed_thr만 활성
4.   latest ← LAST_SAMPLE(k)
5.   sigma  ← sqrt(st.var)
6.   upper  ← st.mean + k_sigma * sigma
7.   lower  ← st.mean - k_sigma * sigma
8.   IF latest > upper OR latest < lower:
9.     alerts.append(PerformanceAlert(
10.        metric_key=k, kind="anomaly_3sigma",
11.        observed=latest, expected_range={lower, upper},
12.        severity=CLASSIFY_SEVERITY(k, latest, st)))
13. # (B) 고정 임계값 기반 threshold_fixed
14. IF latest_qod < fixed_thr.qod_min:
15.   alerts.append(... kind="threshold_fixed", severity="error")
16. IF latest_latency_p95 > fixed_thr.latency_p95_max_ms:
17.   alerts.append(... severity="error")
18. IF cost_daily_ratio > fixed_thr.cost_daily_ratio_max:
19.   alerts.append(... kind="cost_cap", severity="critical")
20. # (C) 중복 제거 (key+kind로)
21. alerts ← DEDUP(alerts, key=lambda a:(a.metric_key,a.kind))
22. RETURN alerts
```

`CLASSIFY_SEVERITY` 기본 규칙:
- qod: 3σ 하향 이탈 → error; 고정 임계(<0.85) → error
- latency_p95: 3σ 상향 → warn; 고정(>2000ms) → error
- error_rate: 3σ 상향 → error; >5% → critical
- cost_daily: ≥80% → critical; 3σ 상향 → warn

### 4.4 BUILD_REPORT

```
ALGORITHM BUILD_REPORT(states, alerts, window) -> PerformanceReport
# 시간복잡도: O(m·w), w=윈도 내 포인트 수
1. qod_trend     ← BUILD_TREND(states["qod"], samples_q, window)
2. latency_trend ← BUILD_TREND(states["latency_p95"], samples_m, window)
3. cost_trend    ← BUILD_TREND(states["cost_daily"], samples_m, window)
4. RETURN PerformanceReport(
      report_id=hash(window.start, module_id),
      window_start=window.start, window_end=window.end,
      qod_trend=qod_trend, latency_trend=latency_trend,
      cost_trend=cost_trend, alerts=alerts,
      generated_at=now())
```

### 4.5 S-2 out-of-band 트리거 (모니터링 루프)

```
ALGORITHM EMIT_S2(alert) -> S4TriggerRequest
LOCK: L2 (I-9 emit만), 모듈 간 버스 경유, 공통 자료구조 §2
1. reason ← MAP_REASON(alert)    # QOD_DEGRADE / LATENCY_SPIKE / ...
2. req ← S4TriggerRequest(
      request_id=hash(alert.alert_id),
      reason_code=reason,
      anchor_metric=alert.metric_key,
      anchor_value=alert.observed,
      window_start=..., window_end=...,
      trace_id=current_trace())
3. S2.receive(req)               # in-process bus or message queue
4. I9.emit_event("oc.self_evo.s04.anomaly",
                 {alert_id, reason, trace_id})
5. RETURN req
POST:
  S-2는 out-of-band request로 재마이닝 수행 (정규 배치와 병행).
  결과 BehaviorPattern은 S-3가 소비 (모니터링 루프 완결).
```

### 4.6 S-6 alert 공급 (적응 루프)

```
ALGORITHM EMIT_S6(state, alert) -> EnvironmentState
LOCK: L2
1. es ← EnvironmentState(
      load=ESTIMATE_LOAD(state),
      error_rate=state["error_rate"].mean,
      user_count=INFER_USER_COUNT(),
      qod_level=state["qod"].mean,
      source_report_id=report.report_id)
2. S6.receive(es)                # _index.md §1.1 S-6 트리거 정본
3. I9.emit_event("oc.self_evo.s04.alert",
                 {alert_id, severity, trace_id})
4. RETURN es
```

### 4.7 I-Module 경유 호출 순서 (정본 해석)

> §3.2 주의 대로 S-4 **직접 호출**은 I-6/I-9/I-14 READ만. I-15는 rollback 시 S-8 대행.

```
STEP  Caller  Module         Action                               LOCK
1     S-4     I-9 READ       MetricSample 스트림 조회             L2
2     S-4     I-6 READ       QoD 시계열 조회                      L2
3     S-4     I-14 READ      QA 실패율/회귀 결과 조회             L2
4     S-4     I-9 emit       oc.self_evo.s04.report               L2
5     S-4     S-2 (bus)      S4TriggerRequest out-of-band 트리거  L2
6     S-4     S-6 (bus)      EnvironmentState 전달                L2
7     S-4     I-9 emit       oc.self_evo.s04.anomaly / .alert     L2
(evolve) S-4 → S-8 (bus)     임계값 변경 EvolutionPlan 제출       L3
(evolve) S-8  I-19 WRITE     ApprovalRequest 대행                 L3
(rollback) S-4 → S-8 (bus)   snapshot_id 복원 요청                L3
(rollback) S-8  I-15 WRITE   스냅샷 복원 대행                     L3
```

---

## 5. 예외 처리 정책 표 (Rule g)

> 01/_index.md §3.2 DH 에러 핸들링 정본 확장.

| error_code | 상황 | recoverable | 처리 | 비고 |
|------------|------|-------------|------|------|
| `SELF_EVO_TIMEOUT` | tick()/evolve() > 120s | ✅ | 실행 중단 → 다음 주기 재시도, confidence penalty ×0.6 | DH-2 |
| `SELF_EVO_EVAL_FAIL` | evaluate() 예외 | ✅ | 이전 점수 유지(최대 3주기) → 초과 시 비활성화 | — |
| `SELF_EVO_ROLLBACK_FAIL` | S-8 대행 복원 실패 | ❌ | I-20 경유 ADMIN+ 즉시 에스컬레이션 | 무결성 보호 |
| `SELF_EVO_IMODULE_FAIL` | I-6/I-9/I-14 호출 실패 | ✅ | 3회 재시도(backoff 1s→2s→4s) → 실패 시 해당 지표 drop | 표준 재시도 |
| `SELF_EVO_SNAPSHOT_FAIL` | S-8이 I-15 실패 응답 | ⚠️ | evolve() 차단, 제안 드롭 | L3 전제 |
| `S4_S3_NOT_STABLE` | S-3 DH-1 미충족 | ✅ | tick() 조기 반환, 이벤트만 기록 | L6 gate |
| `S4_COLD_START` | EWMA 샘플 < 30 | ✅ | 3σ 경보 억제, fixed_thresholds만 활성 | 초기 안정화 |
| `S4_METRIC_GAP` | I-9 스트림 결손 5min 초과 | ✅ | 결손 구간 스킵, 다음 주기 재수집 | 관측성 경보 |
| `S4_ALERT_STORM` | 5분 내 alert > 20 | ✅ | rate-limit 적용(상위 10건만), 나머지 요약 | fan-out 보호 |
| `S4_TRIGGER_DROP_S2` | S-2 bus 거부 (미활성화) | ✅ | 이벤트만 기록, 다음 주기 재시도 | L6 (S-2 선행 보장) |
| `S4_TRIGGER_DROP_S6` | S-6 미활성화 | ✅ | 이벤트만 기록 (적응 루프 비가용) | L6 |
| `S4_APPROVAL_REJECTED` | S-8이 임계값 변경 거부 | ✅ | 정상 흐름, 기존 임계값 유지 | L3 |
| `S4_SCHEMA_VALIDATION_FAIL` | Pydantic 검증 실패 | ❌ | 해당 샘플 drop + 경고 | DH-1 감소 |
| `S4_L4_AUTO_APPLY_ATTEMPT` | 자동 임계값 반영 경로 탐지 | ❌ | 즉시 중단 + 감사 로그 + I-20 | L4 위반 |

---

## 6. Phase별 복구 전략 (Rule e)

### 6.1 Phase 흐름도

```mermaid
flowchart TD
    P1[Phase 1: Detect<br/>메트릭 결손/스키마/호출 실패 식별] --> P2[Phase 2: Local Retry<br/>3회 재시도 w/ backoff<br/>(1s→2s→4s)]
    P2 -- 성공 --> OK[정상 복귀 → 다음 tick]
    P2 -- 실패 --> P3[Phase 3: Degrade<br/>3σ 경보 억제·fixed_thr만 활성<br/>+ confidence penalty]
    P3 -- recoverable --> P3b[다음 주기 재시도]
    P3 -- 연속 3회 --> P4[Phase 4: Escalate<br/>I-20 경유 ADMIN+ 알림]
    P4 --> DEACT[모듈 비활성화<br/>oc.self_evo.s04.deactivated]
```

### 6.2 다운그레이드 시 confidence penalty 표

| 다운그레이드 유형 | confidence 계수 | 누적 한도 |
|-------------------|----------------|-----------|
| Local retry 후 성공 (Phase 2) | ×1.0 | — |
| EWMA 콜드 스타트 (sample_count<30) | ×0.8 | 초기 6주기 한정 |
| I-9 메트릭 결손 (단일 주기) | ×0.7 | 3주기 연속 시 degraded |
| I-6/I-14 호출 실패 → 해당 지표 drop | ×0.8 | 지표별 독립 |
| Alert storm rate-limit 발동 | ×0.7 | 2주기 연속 시 Phase 4 검토 |
| S-2/S-6 bus 드롭 (선행 모듈 미활성화) | ×0.9 | L6 정합, 경보만 |
| Timeout → 이전 주기 report 재사용 | ×0.6, 매 주기 ×0.9 누적 | 연속 5주기 초과 시 비활성화 |
| S-8 임계값 변경 거부 | 영향 없음 | — |

---

## 7. 에스컬레이션 & 로깅 (I-20, R-01-7/R-01-8)

### 7.1 EscalationPayload (I-20 경유, Rule c)

```json
{
  "source_engine": "s04_performance_monitor",
  "error_code": "SELF_EVO_ROLLBACK_FAIL",
  "original_request": {
    "op": "rollback",
    "snapshot_id": "snap_s04_2026-04-14T01-30",
    "trigger": "s8_governance_rollback_request",
    "target_state_keys": ["qod","latency_p95","error_rate"]
  },
  "partial_result": {
    "ewma_state_restored": false,
    "threshold_config_restored": true,
    "restored_items": 3,
    "failed_items": 2
  },
  "retry_count": 1,
  "timestamp": "2026-04-14T01:35:12Z",
  "trace_id": "trc_s04_8a2f",
  "severity": "critical"
}
```

- **대상 경로**: 6-12 Event-Logging I-20 → 6-2 Security-Governance ADMIN+ notify → 6-13 Operations alertmanager.

### 7.2 구조화 JSON 로깅 (R-01-7, Rule d — 중첩)

```json
{
  "ts": "2026-04-14T01:35:12.418Z",
  "level": "error",
  "logger": "self_evo.s04",
  "event": "oc.self_evo.s04.anomaly",
  "module_id": "s04",
  "trace_id": "trc_s04_8a2f",
  "error": {
    "code": "S4_ALERT_STORM",
    "message": "alert count 27 exceeds 5m cap (20); rate-limited to 10",
    "stack_redacted": true
  },
  "context": {
    "window": {"start":"2026-04-14T01:30:00Z","end":"2026-04-14T01:35:00Z"},
    "metrics": {
      "qod":       {"mean": 0.82, "sigma": 0.04, "latest": 0.71, "3s_lower": 0.70},
      "latency_p95_ms": {"mean": 1820, "sigma": 140, "latest": 2380, "3s_upper": 2240},
      "error_rate":{"mean": 0.012, "sigma": 0.004, "latest": 0.031}
    },
    "alert_count_total": 27,
    "alert_count_kept":  10
  },
  "recovery": {
    "action": "rate_limit_and_emit_summary",
    "confidence_penalty": 0.3,
    "next_retry_at": "2026-04-14T01:40:00Z",
    "phase": 3,
    "triggers_emitted": {"s2": true, "s6": true}
  }
}
```

### 7.3 정상 이벤트 목록 (6-12 ocodes)

| 이벤트 | 의미 | level |
|--------|------|-------|
| `oc.self_evo.s04.started` | tick()/evolve() 시작 | info |
| `oc.self_evo.s04.report` | PerformanceReport 생성 완료 | info |
| `oc.self_evo.s04.anomaly` | 이상 탐지 → S-2 트리거 | warn |
| `oc.self_evo.s04.alert` | S-6 alert 공급 | warn |
| `oc.self_evo.s04.tuned` | evolve() 임계값 튜닝 제안 | info |
| `oc.self_evo.s04.submit_plan` | S-8 제출 | info |
| `oc.self_evo.s04.decision_received` | S-8 결정 수신 | info |
| `oc.self_evo.s04.rolled_back` | rollback 완료 | warn |
| `oc.self_evo.s04.error` | 예외 (위 7.2 포맷) | error |
| `oc.self_evo.s04.deactivated` | 모듈 비활성화 | critical |

---

## 8. Phase 2 통합 테스트 시나리오 (Rule e, 10건 이상)

| # | 시나리오 | 입력 | 기대 결과 | 검증 LOCK |
|---|---------|------|-----------|-----------|
| T1 | 정상 메트릭 스트림 5분 | qod≈0.92 안정 | alerts=[], report 정상 생성 | L1 |
| T2 | S-3 DH-1 미충족 | S-3 에러율 3% | `S4_S3_NOT_STABLE`, tick() 조기 반환 | L6 |
| T3 | EWMA 콜드 스타트 | sample_count<30 | 3σ 경보 억제, fixed_thr만 활성 | 부록 A.3 |
| T4 | QoD 급락(0.95→0.70) | 단일 큰 하락 | `anomaly_3sigma` + `threshold_fixed(qod<0.85)` 양쪽 발생, S-2 트리거 | 부록 A.3 |
| T5 | latency p95 스파이크 (1.6s→2.5s) | 네트워크 지연 | error 레벨 alert, S-6 `EnvironmentState` 전달 | _index.md §1.2 |
| T6 | cost_daily 80% 근접 | 비용 누적 | `cost_cap` critical alert, S-6 트리거 + 감사 로그 | §4.3 |
| T7 | error_rate 5% 초과 | 장애 집중 | critical alert, S-2+S-6 동시 트리거 | §4.3 |
| T8 | I-9 스트림 결손(3분 단절) | 메트릭 gap | `S4_METRIC_GAP`, 결손 스킵, 다음 주기 복구 | §5 |
| T9 | I-14 READ 실패 | QA 서비스 다운 | `SELF_EVO_IMODULE_FAIL` → 재시도 3회 → qa 지표 drop | §5 |
| T10 | Alert storm (27건) | 대규모 장애 | `S4_ALERT_STORM`, 상위 10건 유지, 요약 이벤트 | §5 |
| T11 | S-2 미활성화 상태 이상 탐지 | L6 활성화 순서 위배 감지 | `S4_TRIGGER_DROP_S2`, 이벤트만 기록 (활동은 계속) | L6 |
| T12 | S-6 미활성화 alert | 적응 루프 미가용 | `S4_TRIGGER_DROP_S6`, 모니터링 루프는 정상 | L6 |
| T13 | evolve() λ 튜닝 제안 | FPR=0.12 (높음) | λ=0.3→0.2 제안, S-8 제출, 자동 반영 없음 | L3, L4 |
| T14 | S-8 임계값 변경 승인 후 FPR 개선 | 승인 적용 | 신규 λ 반영 후 FPR ≤0.05 확인 | L3 |
| T15 | S-8 임계값 변경 거부 | risk_hint=high | 기존 임계값 유지, bandit 영향 없음 | L3 |
| T16 | rollback 성공 (정상 snapshot) | snapshot_id 유효 | EWMA 상태+threshold 복원 완료, 이벤트 기록 | L7 |
| T17 | rollback 실패 (손상 snapshot) | 무효 snapshot | `SELF_EVO_ROLLBACK_FAIL`, I-20 에스컬레이션 | §7.1 |
| T18 | tick() timeout(147s) | 강제 지연 | `SELF_EVO_TIMEOUT`, Phase 3 degrade | §6 |
| T19 | 자동 임계값 반영 시도 (테스트 하네스) | rogue path | `S4_L4_AUTO_APPLY_ATTEMPT`, 즉시 중단+감사 | L4 |
| T20 | 스키마 검증 실패 1 샘플 | 손상 MetricSample | 해당 건 drop, DH-1 스키마율 감소 경보 | DH-1 |
| T21 | S-3 관찰 루프 확인 | `oc.self_evo.s04.anomaly` emit | S-3가 이벤트 관찰 후 재평가 수행 (s03 T16 정합) | 교차검증 |

---

## 9. 세션 간 인터페이스 cross-check (Rule j)

> 공급·소비 계약 정본화.

| 인터페이스 | 공급자 | 소비자 | 스키마 | 정본 |
|-----------|--------|--------|--------|------|
| `MetricSample` (스트림) | I-9 | **S-4 (본 세션)** | §2 MetricSample | 01/_index.md §1.1 |
| QoD 시계열 | I-6 | **S-4** | 내부 float 시계열 | 01/_index.md §2.3 |
| QA 결과 | I-14 | **S-4** | 내부 구조 | 01/_index.md §2.3 |
| `PerformanceReport` | **S-4** | S-3(관찰), 운영 대시보드 | §2 PerformanceReport | 01/_index.md §1.1 |
| `S4TriggerRequest` | **S-4** | S-2 | §2 S4TriggerRequest (s02 `RegressionRequest`와 독립 — 중복 정의 금지) | 본 파일 §2 |
| `EnvironmentState` | **S-4** | S-6 | §2 EnvironmentState | 01/_index.md §1.1 |
| `EvolutionPlan` (임계값 변경) | **S-4** | S-8 | s03 §2 EvolutionPlan 재사용 | L3 |
| `GovernanceDecision` | S-8 (P2-예정) | **S-4** | s08 예정 | L3 |
| EscalationPayload | **S-4** | I-20 | §2 EscalationPayload | R-01-8 |

### 9.1 선행 세션(P1-M1/M2) cross-check
- **s02_pattern_miner.md §2 RegressionRequest**: s02의 `RegressionRequest`(사후 회귀 테스트 요청)와 본 파일의 `S4TriggerRequest`(이상 탐지 사전 트리거)는 **목적·필드 집합이 다르므로 별도 클래스로 분리** (중복 정의 금지 원칙 준수). 공유 필드는 `trace_id` 단일 항목이며 s02 측 L8 경로와 S-4 측 모니터링 루프 경로는 독립. **정합 — 2026-04-14 재검증 시 명칭 분리 확정.**
- **s03_strategy_optimizer.md §8 T16**: "S-4 트리거(이상 탐지) 경유 S-3 재실행 — alert signal → out-of-band evolve() 1회 실행, bandit 영향 없음". 본 파일 §8 T21은 동일 계약을 S-4 측에서 확인. **정합.**
- **s03 §9.2 후속 계약**: "S-4(P1-M3): `oc.self_evo.s03.proposed` 이벤트를 메트릭으로 관찰. QoD 하락 감지 시 S-3 재실행 트리거". 본 파일은 §4.5 EMIT_S2와 §3.3 "S-3 관찰 루프"로 수용. **정합.**

### 9.2 후속 세션(P1-M4/M5/M6/M7, P2 s08) 공급 계약
- **S-5(P1-M4)**: S-4와 직접 트리거 관계 없음(S-5는 사용자 피드백 수신 시 트리거). 단, S-5가 생성하는 `LearningUpdate`가 QoD 개선에 반영되면 S-4가 해당 개선을 EWMA로 관측한다 (간접 폐루프).
- **S-6(P1-M5)**: 본 파일 `EnvironmentState` 정본을 그대로 소비. s06 작성 시 §2 스키마 정본 준수 필수.
- **S-7(P1-M6)**: S-4가 생성한 임계값 변경 `EvolutionPlan`은 S-7 스케줄 큐에 적재. s07 작성 시 EvolutionPlan 소비 계약 대조.
- **S-8(P2)**: 본 파일 §4.7 rollback 대행 흐름, §3.3 L3 경유 계약을 s08_governance.md 작성 시 반드시 대조.

---

## 10. LOCK 참조 매핑 & CONFLICT 후보

### 10.1 LOCK 참조

| LOCK | 반영 위치 |
|------|-----------|
| L1 S-2~S-8 모듈 목록 | §1, §2 (MODULE_ID="s04") |
| L2 I-Module 경유 원칙 | §3.2 접근 권한, §4.1/§4.7 호출 순서 |
| L3 S-8 거버넌스 승인 필수 | §3.1 evolve()/rollback() 주석, §4.7, §8 T13~T15 |
| L4 자동 적용 금지 | §3.1 evolve() 말미, §5 `S4_L4_AUTO_APPLY_ATTEMPT`, §8 T19 |
| L6 순차 활성화 (S-3 → S-4) | §3.1 클래스 주석, §4.1 line 1 gate, §8 T2 |
| L7 BaseSelfEvo ABC | §3.1 클래스 스켈레톤 (시그니처 정본 준수) |

### 10.2 CONFLICT 후보 기록

**[CONFLICT_CANDIDATE: 종합계획서 §7 P1-M3 본문 line 671의 "I-9(메트릭 수집) → I-6(QoD 측정) → I-15(스냅샷)" 호출 순서 지시와 01/_index.md §2.3 I-Module 접근 매트릭스(S-4 = I-6/I-9/I-14 READ only) 간 불일치 — I-15 직접 접근은 S-4 권한 없음]**

- **불일치 상세**:
  - 종합계획서 §7 P1-M3 본문(line 671): "I-Module 경유 호출 순서: I-9(메트릭 수집) → I-6(QoD 측정) → I-15(스냅샷)"
  - 01/_index.md §2.3 접근 매트릭스: S-4 = {I-6 READ, I-9 READ, I-14 READ}. I-15 권한 없음. §2.3 주의: "S-8만 I-19 WRITE, I-15는 스냅샷 주체(S-6/S-8) 경유".
- **본 파일의 채택**: 01/_index.md §2.3 (FINAL REVIEW 승인 정본) 준수. 본문 line 671의 I-15 참조는 **rollback 시 S-8 대행을 포함한 전체 경유 순서**로 해석하여 §4.7에 명시(Caller 컬럼 분리 — `(rollback) S-8 I-15 WRITE`).
- **근거**: Rule (j) "다른 세션 산출물과의 인터페이스 정합" — P0 산출물 _index.md가 정본. _index.md §2.3은 SEVO-C001/002/003 정합 회로의 최종 형태이며 P1-M1/M2에서도 동일 해석을 적용.
- **등재 ID**: **SEVO-C003 확장(S-4)**(P1-M1 S-2, P1-M2 S-3에 이어 S-4에도 동일 구조로 적용). **상태: ✅ RESOLVED (2026-04-14)** — CONFLICT_LOG.md §3 참조. 결정 요약: 01/_index.md §2.3 접근 매트릭스(A.4)가 정본이며, 종합계획서 §7 P1-M3 본문의 "I-9 → I-6 → I-15" 호출 순서 중 I-15는 **rollback 시 S-8 대행을 포함한 전체 경유 경로(flow)** 로 해석 고정. 본 파일 §4.7 Caller 컬럼 분리(`(rollback) S-8 I-15 WRITE`) 방식이 정본 해석 그대로.

> 파서 마커: CONFLICT_LOG.md §3 SEVO-C003 RESOLVED 정본 반영 완료. flow vs direct call 분리 원칙을 §3.2·§4.7·§10.2에 일관 적용.

---

## 11. 수정 정책

> **정본 — Phase 변경 시 갱신 (§8.2)**.
> 본 파일은 S-4 Performance Monitor의 EWMA 알고리즘·이상 탐지·S-2/S-6 트리거 연계·S-8 승인 경유 흐름의 L3 정본이다. 상위 정본(D2.0-02 §10.4~§10.6, Part2 V3-P2, 01/_index.md §1.1/§2.3/§3.1) 변경이 없는 한 임의 수정 금지.

---

## 12. 변경 이력

| 일자 | 변경 | 세션 |
|------|------|------|
| 2026-04-14 | 초기 작성(P1-M3) — BaseSelfEvo ABC 구현, EWMA(λ=0.3) 의사코드, 3σ+고정임계 이중 판정, S-2 out-of-band 트리거(모니터링 루프)·S-6 alert(적응 루프), S-8 승인 경유 임계값 자동 조정, 접근 매트릭스 정합(§3.2, I-6/I-9/I-14 READ), CONFLICT 후보 SEVO-C003 S-4 확장 기록, Phase 2 테스트 21건 | P1-M3 |
| 2026-04-14 | 심층 재검증 그룹 A — §10.2 SEVO-C003 확장 상태 OPEN → RESOLVED 반영, s02 `RegressionRequest`와 충돌하던 로컬 `RegressionRequest` 클래스를 `S4TriggerRequest`로 분리(중복 정의 금지 원칙 준수), §2/§3.3/§4.1/§4.5/§9/§9.1 참조 일괄 갱신 | 재검증 |

---

## 이월·검증 상태 (step 1 자기 확인)

- 1. 선행 세션(P1-M1 s02, P1-M2 s03) cross-check: PASS
  - s02 `RegressionRequest`(사후 회귀) vs 본 파일 `S4TriggerRequest`(사전 트리거) 명칭 분리·중복 제거 (§2/§9.1)
  - s03 T16 "S-4 이상 탐지 → S-3 재실행" 후속 계약 §8 T21에서 반대편 확인
  - s03 §9.2 "S-4가 `oc.self_evo.s03.proposed` 관찰" 계약 §3.3에서 수용
- 2. CONFLICT: 후보 1건 — **SEVO-C003 확장(S-4)** (§7 P1-M3 본문 line 671 "I-15(스냅샷)" vs 부록 A.4 접근 매트릭스 S-4 = I-6/I-9/I-14 READ only) — **✅ RESOLVED (2026-04-14)** CONFLICT_LOG.md §3 반영 완료
- 3. LOCK 변경: 없음 (L1/L2/L3/L4/L6/L7 인용만, 본문 수정 0건)
- 4. 이월: 없음 — P1-M4 (s05_feedback_loop.md) 순차 진입 가능
- 5. 해결 이슈 ID: ISS-1 S-4 알고리즘 힌트(부록 A.3 EWMA λ=0.3, 3σ) P1-M3 본 세션에서 소비

---

[GUARDS_OK] memory_skipped=YES forbidden_paths=untouched common_artifacts=untouched
