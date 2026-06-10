# 매크로→전략 자동 전환 (Macro-to-Strategy Auto-Switch)
> **버전**: v1.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #3 매크로→섹터→종목 연결 엔진
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9

---

### B-12. 매크로→전략 자동 전환 (Macro-to-Strategy Auto-Switch)

**현재**: §9.5에서 DEFER 상태
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 46 | **매크로 레짐 → 전략 프리셋 매핑** | 4개 매크로 레짐 × 96개 전략 → 레짐별 활성화 전략 셋, 가중치, 파라미터 프리셋. 레짐 전환 시 자동 적용 |
| 47 | **전환 점진성(Gradual Transition)** | 레짐 전환은 이진이 아님. 전환 확률에 따른 점진적 전략 가중치 이동. 90% Expansion → 70% Expansion + 30% Peak 시 혼합 적용 |
| 48 | **전략 유효성 매크로 필터** | 각 전략별 "이 매크로 환경에서 역사적으로 유효했는가?" 메타 데이터. 현재 레짐에서 유효하지 않은 전략 자동 비활성화 |
| 49 | **매크로 이벤트 캘린더 통합** | FOMC, ECB, BOK 금통위, 고용보고서, CPI 발표 등 이벤트 전후 전략 자동 조절. 이벤트 전: 포지션 축소, 이벤트 후: 방향성 전략 활성화 |
| 50 | **매크로 스트레스 테스트** | "금리 +200bp", "유가 $150", "중국 GDP -2%" 등 극단 시나리오별 포트폴리오 영향 시뮬레이션 |

---

### [보완] B-13. 한국 시장 특화 매크로 연결

**현재**: ECOS API 수집 계획만 존재
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 51 | **한국 고유 매크로 지표 활용** | 한국은행 기준금리, 수출입 증가율, 가계부채, 부동산 가격 → 한국 시장 특화 레짐 분류 |
| 52 | **미국→한국 전이 시차 분석** | 미국 경기 변동이 한국에 전이되는 시차(통상 3~6개월) 측정 → 한국 시장 선행 포지셔닝 |

---

## E1. Input

- **데이터 소스**:
  - `MacroRegimeEngine`: 현재 레짐 + 레짐 전환 확률 벡터
  - 전략 메타DB: 96개 전략별 레짐 유효성 메타 데이터 (historical performance by regime)
  - 이벤트 캘린더: FOMC, ECB, BOK 금통위, 고용보고서, CPI 등 일정
  - 스트레스 시나리오: 매크로 변수별 극단값 정의 (금리, 유가, GDP, 환율)
  - 한국 매크로: ECOS API (한국은행 기준금리, 수출입, 가계부채, 부동산)
  - 미국 매크로: FRED API (Fed Funds Rate, GDP, CPI)
- **필수 필드**:
  - `regime_probabilities`: dict[str, float] — {"expansion": 0.7, "peak": 0.3, ...} 합=1
  - `strategy_registry`: list[dict] — 96개 전략 메타 (id, name, regime_validity, params_by_regime)
  - `event_calendar`: list[dict] — [{"event": str, "date": datetime, "importance": str}]
  - `stress_scenarios`: list[dict] — [{"name": str, "shocks": dict[str, float]}]
  - `portfolio_positions`: dict[str, float] — 현재 포트폴리오 포지션
  - `kr_macro_indicators`: dict[str, float] — 한국 매크로 지표 (기준금리, 수출증가율 등)
  - `us_kr_lag_months`: int — 미국→한국 전이 시차 추정값
- **전처리** (필수):
  - 레짐 확률: softmax 정규화 (합=1 보장)
  - 전략 메타 데이터: 레짐별 Sharpe ratio, Win rate, Max DD 사전 산출
  - 이벤트 캘린더: T-7일 ~ T+2일 윈도우로 활성 이벤트 필터링
  - 한국 지표: 계절 조정, 전년 동기 대비 변화율 변환

## E2. Algorithm

```python
# 매크로→전략 자동 전환 + 한국 특화 + 스트레스 테스트
def macro_strategy_switch(inputs: dict) -> dict:
    """
    Step 1: 레짐→전략 프리셋 매핑
    Step 2: 점진적 전환 (확률 가중 혼합)
    Step 3: 전략 유효성 필터
    Step 4: 이벤트 캘린더 조절
    Step 5: 매크로 스트레스 테스트
    Step 6: 한국 고유 매크로 연결
    Step 7: 미국→한국 전이 시차 적용
    """

    # Step 1: 레짐→전략 프리셋 매핑
    # REGIME_STRATEGY_MAP[regime] = {strategy_id: {"weight": float, "params": dict}}
    # 4개 레짐 × 96개 전략 매핑 테이블
    regime_probs = inputs["regime_probabilities"]

    # Step 2: 점진적 전환 — 확률 가중 혼합
    # blended_weight(strategy_i) = Σ_r P(regime_r) * preset_weight(strategy_i, regime_r)
    # blended_params(strategy_i) = Σ_r P(regime_r) * preset_params(strategy_i, regime_r)
    blended_weights = {}
    blended_params = {}
    for strat in inputs["strategy_registry"]:
        sid = strat["id"]
        w = 0.0
        p = {}
        for regime, prob in regime_probs.items():
            preset = REGIME_STRATEGY_MAP[regime].get(sid, {"weight": 0, "params": {}})
            w += prob * preset["weight"]
            for k, v in preset["params"].items():
                p[k] = p.get(k, 0) + prob * v
        blended_weights[sid] = w
        blended_params[sid] = p

    # Step 3: 전략 유효성 매크로 필터
    # 현재 지배적 레짐에서 역사적 유효성 검증
    # 유효 조건: regime_sharpe ≥ 0.5 AND regime_win_rate ≥ 0.48
    dominant_regime = max(regime_probs, key=regime_probs.get)
    active_strategies = {}
    disabled_strategies = []
    for strat in inputs["strategy_registry"]:
        sid = strat["id"]
        validity = strat["regime_validity"].get(dominant_regime, {})
        if validity.get("sharpe", 0) >= 0.5 and validity.get("win_rate", 0) >= 0.48:
            active_strategies[sid] = blended_weights[sid]
        else:
            disabled_strategies.append(sid)
            # 비활성화 전략의 가중치를 활성 전략에 재분배
    # 가중치 재정규화
    total_active = sum(active_strategies.values())
    if total_active > 0:
        active_strategies = {k: v / total_active for k, v in active_strategies.items()}

    # Step 4: 이벤트 캘린더 조절
    # 이벤트 T-7일: 포지션 축소 팩터 (importance별)
    # high importance: 0.5x, medium: 0.7x, low: 0.9x
    # 이벤트 T+2일: 방향성 전략 활성화 (100% 복원)
    event_adjustment = 1.0
    for event in inputs["event_calendar"]:
        days_to = (event["date"] - inputs["as_of"]).days
        if 0 <= days_to <= 7:  # 이벤트 전 7일 (미래 이벤트, days_to 양수)
            factor = {"high": 0.5, "medium": 0.7, "low": 0.9}[event["importance"]]
            event_adjustment = min(event_adjustment, factor)
        elif -2 <= days_to < 0:  # 이벤트 직후 (1~2일 경과)
            event_adjustment = 1.0  # 복원

    adjusted_weights = {k: v * event_adjustment for k, v in active_strategies.items()}

    # Step 5: 매크로 스트레스 테스트
    # 각 시나리오별 포트폴리오 P&L 추정
    # P&L = Σ (position_i * sensitivity_i * shock_j) for each scenario
    stress_results = []
    for scenario in inputs["stress_scenarios"]:
        pnl = 0.0
        for asset, position in inputs["portfolio_positions"].items():
            sensitivity = get_macro_sensitivity(asset, scenario["shocks"])
            pnl += position * sensitivity
        stress_results.append({
            "scenario": scenario["name"],
            "portfolio_pnl": pnl,
            "pnl_pct": pnl / sum(abs(v) for v in inputs["portfolio_positions"].values()),
            "breach": abs(pnl / sum(abs(v) for v in inputs["portfolio_positions"].values())) > inputs.get("max_stress_loss", 0.15)
        })

    # Step 6: 한국 고유 매크로 연결
    # 한국 레짐 분류: BOK 금리 방향 + 수출 증가율 + 가계부채 증가율
    kr = inputs.get("kr_macro_indicators", {})
    kr_regime = classify_korea_regime(
        bok_rate_direction=kr.get("bok_rate_direction"),  # "hiking" | "cutting" | "hold"
        export_growth=kr.get("export_yoy"),               # 수출 전년비
        household_debt_growth=kr.get("debt_yoy"),         # 가계부채 전년비
        housing_price_change=kr.get("housing_mom")        # 부동산 전월비
    )

    # Step 7: 미국→한국 전이 시차
    # 미국 레짐 전환 시점 + lag_months → 한국 시장 선행 포지셔닝
    # us_regime_shift_date + timedelta(months=lag) = kr_expected_shift_date
    lag = inputs.get("us_kr_lag_months", 4)  # 기본 4개월
    # Granger causality 기반 동적 시차 추정
    dynamic_lag = estimate_us_kr_lag(
        us_regime_history=inputs.get("us_regime_history"),
        kr_market_history=inputs.get("kr_market_history"),
        max_lag=12
    )

    return {
        "blended_weights": adjusted_weights,
        "blended_params": blended_params,
        "active_strategies": list(active_strategies.keys()),
        "disabled_strategies": disabled_strategies,
        "event_adjustment_factor": event_adjustment,
        "stress_results": stress_results,
        "kr_regime": kr_regime,
        "us_kr_lag": dynamic_lag,
        "dominant_regime": dominant_regime,
        "confidence": regime_probs[dominant_regime]
    }

def classify_korea_regime(bok_rate_direction, export_growth, household_debt_growth, housing_price_change) -> str:
    """한국 시장 특화 레짐 분류"""
    # 확장: 수출 성장 + 금리 인상 또는 동결
    # 과열: 수출 성장 + 가계부채 급증 + 부동산 상승
    # 수축: 수출 감소 + 금리 인하
    # 저점: 수출 바닥 + 금리 인하 지속
    if export_growth > 5 and bok_rate_direction in ("hiking", "hold"):
        if household_debt_growth > 8 and housing_price_change > 0.5:
            return "overheating"
        return "expansion"
    elif export_growth < -5 and bok_rate_direction == "cutting":
        return "contraction"
    elif export_growth < 0 and bok_rate_direction == "cutting":
        return "trough"
    else:
        return "neutral"
```

## E3. Output

- **스키마**:
```python
@dataclass
class MacroStrategySwitchResult:
    timestamp: datetime
    dominant_regime: str                         # 지배적 매크로 레짐
    regime_probabilities: dict[str, float]       # 레짐별 확률
    active_strategies: list[str]                 # 활성화된 전략 ID 목록
    disabled_strategies: list[str]               # 비활성화된 전략 ID 목록
    blended_weights: dict[str, float]            # 전략별 혼합 가중치
    blended_params: dict[str, dict]              # 전략별 혼합 파라미터
    event_adjustment_factor: float               # 이벤트 조절 팩터 (0~1)
    stress_results: list[dict]                   # 스트레스 테스트 결과
    kr_regime: str                               # 한국 시장 레짐
    us_kr_lag_months: int                         # 미국→한국 전이 시차
    confidence: float                            # 0.0 ~ 1.0

@dataclass
class StressTestResult:
    scenario_name: str
    portfolio_pnl: float                         # 시나리오별 P&L
    pnl_pct: float                               # P&L 비율
    breach: bool                                 # 한도 초과 여부
    worst_asset: str                             # 최대 손실 자산
```
- **confidence 계산**: 지배적 레짐 확률 = confidence. 51% Gate — confidence ≥ 0.51이어야 전략 전환 실행. 미달 시 현행 전략 유지
- **소비자**: `StrategyOrchestrator`, `PortfolioConstructor`, `RiskManager`, `RebalanceEngine`

## E4. Class/API Design

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

class MacroStrategySwitcher:
    """매크로→전략 자동 전환 — 레짐 매핑, 점진 전환, 이벤트, 스트레스, 한국 특화"""

    def __init__(self, config: dict, macro_engine: "MacroRegimeEngine",
                 strategy_registry: "StrategyRegistry", event_calendar: "EventCalendar"):
        self.config = config
        self.macro = macro_engine
        self.registry = strategy_registry
        self.calendar = event_calendar
        self.regime_map: dict = config["regime_strategy_map"]
        self.validity_thresholds: dict = {"sharpe": 0.5, "win_rate": 0.48}
        self.max_stress_loss: float = 0.15  # 최대 스트레스 손실 허용

    def switch(self, as_of: datetime) -> "MacroStrategySwitchResult":
        """전략 전환 메인 진입점 — 레짐→혼합→필터→이벤트→스트레스"""
        ...

    def blend_by_regime_probs(self, regime_probs: dict) -> tuple[dict, dict]:
        """점진적 전환 — 레짐 확률 가중 혼합 가중치 + 파라미터"""
        ...

    def filter_by_validity(self, strategies: dict, dominant_regime: str) -> tuple[dict, list]:
        """매크로 유효성 필터 — 유효하지 않은 전략 비활성화"""
        ...

    def apply_event_adjustment(self, weights: dict, as_of: datetime) -> tuple[dict, float]:
        """이벤트 캘린더 기반 포지션 조절"""
        ...

    def run_stress_test(self, scenarios: list[dict], positions: dict) -> list["StressTestResult"]:
        """매크로 스트레스 테스트 실행"""
        ...

    def classify_korea_regime(self, kr_indicators: dict) -> str:
        """한국 시장 특화 레짐 분류"""
        ...

    def estimate_us_kr_lag(self, us_history: list, kr_history: list) -> int:
        """미국→한국 전이 시차 Granger causality 기반 추정"""
        ...

    def circuit_breaker_check(self, result: "MacroStrategySwitchResult") -> bool:
        """전략 급변 시 Circuit Breaker — 활성 전략 수 50% 이상 변경 시 발동"""
        ...
```

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | ≥2.0 | ☑ | 시계열, 이벤트 캘린더 처리 |
| numpy | ≥1.24 | ☑ | 행렬 연산, 가중치 혼합 |
| statsmodels | ≥0.14 | ☑ | Granger causality (미국→한국 시차) |
| scipy | ≥1.11 | ☑ | 최적화, 통계 검정 |
| requests | ≥2.31 | ☑ | ECOS API, FRED API 호출 |
| pykrx | ≥1.0 | ☑ | 한국 시장 데이터 (KOSPI 등) |

## E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 전략 전환 결정 | ≤ 5초 | 레짐 → 혼합 → 필터 → 결과 |
| 스트레스 테스트 (5 시나리오) | ≤ 10초 | 시나리오별 P&L 시뮬레이션 |
| 이벤트 캘린더 조회 | ≤ 500ms | 활성 이벤트 필터링 |
| 미국→한국 시차 추정 | ≤ 15초 | Granger causality 10년 데이터 |
| 전체 파이프라인 | ≤ 30초 | E2E: 레짐→전환→스트레스→한국 |

## E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 레짐 확률 합 ≠ 1.0 | softmax 재정규화 + 경고 | LOW |
| 전략 메타 데이터 누락 | 해당 전략 기본 가중치(0) 적용 | MEDIUM |
| 이벤트 캘린더 API 실패 | 캐시된 캘린더 사용 + 1일 내 재시도 | MEDIUM |
| 스트레스 시나리오 sensitivity 미정의 | 해당 자산 제외, 부분 결과 반환 | LOW |
| ECOS API 장애 | 캐시된 한국 지표 사용 + 72시간 유효 | MEDIUM |
| 전략 급변 (활성 전략 50% 이상 변경) | Circuit Breaker 발동, 수동 확인 | HIGH |
| 스트레스 테스트 breach (>15% 손실) | 즉시 알림 + 리스크 매니저 트리거 | CRITICAL |

## E8. Test Criteria

- **Unit**: 4개 레짐에서 점진적 전환 (50%/50% 혼합) 시 가중치 수학적 검증. 이벤트 팩터 적용 전후 가중치 변화 검증. 한국 레짐 분류 — 알려진 시기 (2008, 2020, 2022) 매칭
- **Integration**: MacroRegimeEngine 레짐 변경 → 전략 전환 → StrategyOrchestrator 적용 end-to-end. 이벤트 캘린더 → 포지션 축소 → 이벤트 후 복원 파이프라인
- **Acceptance**: 51% Gate — 자동 전환 전략의 정적 배분 대비 Sharpe ratio 개선 확인 (2010~2024). 스트레스 테스트 — 2008/2020 실제 데이터로 breach 정확 감지. 최소 30건

## E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 레짐 4개 (Expansion/Peak/Contraction/Trough) | SPEC §9 | 매크로 레짐 분류 기준 |
| 전략 유효성 Sharpe≥0.5, WR≥48% | SPEC §14 | 레짐별 전략 유효성 임계값 |
| 이벤트 축소 팩터 0.5/0.7/0.9 | SPEC §14 | 이벤트 중요도별 포지션 조절 |
| 스트레스 한도 15% | SPEC §14 | 최대 허용 시나리오 손실 |
| 51% Gate | SPEC §9 | 전략 전환 confidence threshold |
| Circuit Breaker 50% 전략 변경 | SPEC §9.5 | 급격한 전략 변경 자동 정지 |
| 미국→한국 기본 시차 4개월 | SPEC §14 | Granger causality 기본값 |
