# 팩터 타이밍 엔진 (Factor Timing Engine)
> **버전**: v1.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #3 매크로→섹터→종목 연결 엔진
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9

---

### B-6. 팩터 타이밍 엔진 (Factor Timing Engine)

**현재**: 8개 팩터 전략이 정적으로 나열만 됨
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 24 | **매크로 레짐별 팩터 유효성 매핑** | 성장 확장기 → Momentum/Growth 유효, 경기 둔화기 → Value/Quality 유효, 고금리기 → Dividend Yield 유효. 현재 레짐에서 각 팩터의 기대 수익률 자동 조절 |
| 25 | **팩터 크라우딩(Crowding) 감지** | 특정 팩터에 자금 과도 집중 시 "팩터 리버설" 위험. 팩터 밸류에이션 스프레드(저평가-고평가 갭) + 자금 흐름 → 크라우딩 경고 |
| 26 | **팩터 모멘텀 분석** | 최근 6~12개월 팩터별 수익률 모멘텀 추적. 모멘텀 상위 팩터 오버웨이트, 하위 팩터 언더웨이트 |
| 27 | **팩터 상관관계 동적 분석** | 위기 시 팩터 간 상관 급등(분산 효과 소멸) 감지. 정상 시 상관 < 0.3 → 위기 시 > 0.7 전환 시 팩터 분산 무효 경고 |

---

## E1. Input

- **데이터 소스**:
  - 팩터 수익률: `Fama-French / AQR` 일간 팩터 수익률 (Momentum, Value, Quality, Size, Growth, Dividend, Low-Vol, Profitability)
  - 매크로 레짐: `MacroRegimeEngine` 출력 (EXPANSION, SLOWDOWN, RECESSION, RECOVERY)
  - 팩터 밸류에이션: `Bloomberg / Quantopian` 팩터 스프레드 (롱-숏 포트폴리오 밸류에이션 갭)
  - 자금 흐름: `EPFR` 스타일별 펀드 플로우 (Value Fund, Growth Fund, Momentum ETF 등)
  - 팩터 ETF AUM: `ETF.com / Bloomberg` 팩터별 ETF 순자산 추이
- **필수 필드**:
  - `factor_name` (str): MOMENTUM, VALUE, QUALITY, SIZE, GROWTH, DIVIDEND, LOW_VOL, PROFITABILITY
  - `daily_return` (float64): 일간 팩터 수익률
  - `timestamp` (datetime): 거래일
  - `macro_regime` (str): 현재 매크로 레짐
  - `valuation_spread` (float64): 롱-숏 밸류에이션 스프레드
  - `fund_flow` (float64): 주간 자금 유입/유출 (백만 USD)
- **전처리 규칙**:
  - 팩터 수익률 winsorize: 상하위 1% clip
  - 결측 거래일 forward-fill (최대 3일)
  - 수익률 → 누적 수익률 변환 (6개월, 12개월 rolling)
  - 밸류에이션 스프레드 z-score 정규화 (rolling 5년 기준)

## E2. Algorithm

```python
# 팩터 타이밍 엔진 의사코드 — 복사 → 구현 가능 수준
import numpy as np
import pandas as pd
from scipy.stats import zscore

FACTORS = ["MOMENTUM", "VALUE", "QUALITY", "SIZE", "GROWTH", "DIVIDEND", "LOW_VOL", "PROFITABILITY"]

# ── 항목 24: 매크로 레짐별 팩터 유효성 매핑 ──
# 레짐→팩터 기대 수익률 prior (학술 연구 + 백테스트 기반)
REGIME_FACTOR_PRIOR = {
    "EXPANSION":  {"MOMENTUM": 1.2, "GROWTH": 1.1, "VALUE": 0.7, "QUALITY": 0.8, "SIZE": 1.0, "DIVIDEND": 0.6, "LOW_VOL": 0.5, "PROFITABILITY": 0.9},
    "SLOWDOWN":   {"MOMENTUM": 0.6, "GROWTH": 0.5, "VALUE": 1.1, "QUALITY": 1.3, "SIZE": 0.7, "DIVIDEND": 1.2, "LOW_VOL": 1.1, "PROFITABILITY": 1.0},
    "RECESSION":  {"MOMENTUM": 0.4, "GROWTH": 0.3, "VALUE": 0.8, "QUALITY": 1.4, "SIZE": 0.5, "DIVIDEND": 1.3, "LOW_VOL": 1.4, "PROFITABILITY": 1.1},
    "RECOVERY":   {"MOMENTUM": 1.0, "GROWTH": 0.9, "VALUE": 1.3, "QUALITY": 0.9, "SIZE": 1.2, "DIVIDEND": 0.8, "LOW_VOL": 0.7, "PROFITABILITY": 0.8},
}

def regime_factor_adjustment(factor_returns: pd.DataFrame,
                              current_regime: str,
                              lookback: int = 252) -> pd.Series:
    """
    현재 레짐에서 각 팩터의 기대 수익률 조정 가중치 반환
    = prior × 실증 레짐 성과 blend
    """
    prior = REGIME_FACTOR_PRIOR.get(current_regime, {f: 1.0 for f in FACTORS})
    # 실증: 해당 레짐 기간 동안의 평균 팩터 수익률 (최근 lookback일)
    empirical_mean = factor_returns.tail(lookback).mean()
    empirical_rank = empirical_mean.rank(pct=True)

    # Blend: 0.6 * prior + 0.4 * empirical rank
    blended = {}
    for f in FACTORS:
        blended[f] = 0.6 * prior.get(f, 1.0) + 0.4 * empirical_rank.get(f, 0.5) * 2
    return pd.Series(blended)


# ── 항목 25: 팩터 크라우딩 감지 ──
def detect_factor_crowding(valuation_spreads: pd.DataFrame,
                            fund_flows: pd.DataFrame,
                            zscore_window: int = 1260) -> pd.DataFrame:
    """
    크라우딩 스코어 = z-score(밸류에이션 스프레드 축소) + z-score(자금 유입 급증)
    스프레드 축소 = 과거 대비 롱-숏 갭이 줄어듦 → 팩터 비싸짐
    """
    # 밸류에이션 스프레드 z-score (음수 = 스프레드 축소 = 비쌈)
    val_z = valuation_spreads.rolling(zscore_window).apply(
        lambda x: (x.iloc[-1] - x.mean()) / x.std() if x.std() > 0 else 0
    )

    # 자금 유입 z-score (양수 = 과도 유입)
    flow_z = fund_flows.rolling(52).apply(  # 주간 데이터 → 52주
        lambda x: (x.iloc[-1] - x.mean()) / x.std() if x.std() > 0 else 0
    )

    # 크라우딩 스코어: 스프레드 축소(음수) + 자금 유입(양수) → 종합
    crowding = -val_z + flow_z  # 높을수록 크라우딩 위험
    crowding_alert = crowding.apply(lambda x: x > 2.0)  # z > 2.0 → 리버설 경고

    return pd.DataFrame({"crowding_score": crowding.iloc[-1] if len(crowding) > 0 else 0,
                          "alert": crowding_alert.iloc[-1] if len(crowding_alert) > 0 else False})


# ── 항목 26: 팩터 모멘텀 분석 ──
def factor_momentum_signal(factor_returns: pd.DataFrame,
                            short_window: int = 126,
                            long_window: int = 252) -> pd.Series:
    """
    팩터 모멘텀 = 최근 6개월 누적 수익률 순위
    상위 팩터 오버웨이트, 하위 팩터 언더웨이트
    """
    cum_short = factor_returns.tail(short_window).sum()  # 6개월 누적
    cum_long = factor_returns.tail(long_window).sum()     # 12개월 누적

    # 복합 모멘텀 = 0.6 * 6M + 0.4 * 12M
    composite = 0.6 * cum_short + 0.4 * cum_long
    rank = composite.rank(pct=True)  # 0~1 백분위

    # 가중치: 상위 50% → 오버웨이트 (1.0 + rank_excess), 하위 50% → 언더웨이트
    weights = rank.apply(lambda r: 1.0 + (r - 0.5) * 0.6)  # 0.7 ~ 1.3 범위
    return weights / weights.sum() * len(weights)  # 합 = N (동일 비중 기준 정규화)


# ── 항목 27: 팩터 상관관계 동적 분석 ──
def dynamic_factor_correlation(factor_returns: pd.DataFrame,
                                 short_window: int = 60,
                                 long_window: int = 252) -> dict:
    """
    단기/장기 상관행렬 비교 → 위기 시 상관 급등 감지
    """
    corr_short = factor_returns.tail(short_window).corr()
    corr_long = factor_returns.tail(long_window).corr()

    n = len(corr_short)
    # 상삼각 평균
    upper_idx = np.triu_indices(n, k=1)
    avg_corr_short = np.mean(corr_short.values[upper_idx])
    avg_corr_long = np.mean(corr_long.values[upper_idx])

    # 상관 급등 = 단기 평균 - 장기 평균
    corr_spike = avg_corr_short - avg_corr_long

    # 경고: 단기 평균 상관 > 0.7 → 팩터 분산 무효
    diversification_valid = avg_corr_short < 0.7

    return {
        "avg_corr_short": avg_corr_short,
        "avg_corr_long": avg_corr_long,
        "corr_spike": corr_spike,
        "diversification_valid": diversification_valid,
        "corr_matrix_short": corr_short,
    }
```

## E3. Output

- **스키마**:
  ```python
  @dataclass
  class FactorTimingResult:
      timestamp: datetime
      regime: str                        # 현재 매크로 레짐
      factor_weights: dict               # {factor_name: weight, ...} 레짐 조정 가중치
      crowding_alerts: dict              # {factor_name: {"score": float, "alert": bool}, ...}
      momentum_weights: dict             # {factor_name: weight, ...} 모멘텀 기반 가중치
      avg_factor_corr: float             # 단기 평균 팩터 상관
      diversification_valid: bool        # True = 팩터 분산 유효
      final_allocation: dict             # {factor_name: weight, ...} 최종 배분 (레짐 × 모멘텀 × 크라우딩 조정)
      confidence: float                  # 0.0 ~ 1.0
      metadata: dict
  ```
- **confidence 계산**: `mean(레짐 확신도, 크라우딩 데이터 품질, 모멘텀 안정성)`
  - 레짐 확신도: `MacroRegimeEngine` 출력 confidence 그대로 사용
  - 크라우딩 데이터 품질: 밸류에이션 스프레드 + 자금 흐름 모두 최신이면 1.0
  - 모멘텀 안정성: 6M vs 12M 모멘텀 순위 상관 (Spearman) → 높을수록 안정
- **소비자 모듈**: `PortfolioOptimizer` (팩터 배분), `RiskManager` (분산 무효 경고), `51% Gate`

## E4. Class/API Design

```python
from engines.base import BaseEngine
from models.factor import FactorTimingResult

class FactorTimingEngine(BaseEngine):
    """팩터 타이밍 엔진.

    SPEC §3 매크로→섹터→종목 연결: 항목 24~27
    구현 우선순위: P1 (V2 대상)
    """

    # LOCK 파라미터 (SPEC §14)
    MOMENTUM_SHORT_WINDOW: int = 126     # 6개월 팩터 모멘텀
    MOMENTUM_LONG_WINDOW: int = 252      # 12개월 팩터 모멘텀
    CROWDING_ZSCORE_WINDOW: int = 1260   # 5년 밸류에이션 z-score
    CORR_SHORT_WINDOW: int = 60          # 단기 상관 윈도우
    CORR_LONG_WINDOW: int = 252          # 장기 상관 윈도우
    CORR_CRISIS_THRESHOLD: float = 0.7   # 위기 상관 임계값
    CROWDING_ALERT_Z: float = 2.0        # 크라우딩 경고 z-score

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "FactorTiming"

    def compute_regime_weights(self, factor_returns: "pd.DataFrame",
                                current_regime: str) -> "pd.Series":
        """항목24: 매크로 레짐별 팩터 기대 수익률 조정 가중치 산출."""
        pass

    def detect_crowding(self, valuation_spreads: "pd.DataFrame",
                        fund_flows: "pd.DataFrame") -> "pd.DataFrame":
        """항목25: 팩터 크라우딩 감지 → 리버설 경고 발행."""
        pass

    def compute_momentum(self, factor_returns: "pd.DataFrame") -> "pd.Series":
        """항목26: 팩터 모멘텀 (6M/12M 복합) → 오버/언더웨이트."""
        pass

    def analyze_correlation(self, factor_returns: "pd.DataFrame") -> dict:
        """항목27: 팩터 간 상관관계 동적 분석 → 분산 유효성 판정."""
        pass

    def run(self, data: dict) -> FactorTimingResult:
        """전체 팩터 타이밍 실행 → FactorTimingResult 반환.
        최종 배분 = regime_weights × momentum × (1 - crowding_penalty).
        51% Gate confidence 기준 충족 시에만 유효 신호 발행.
        """
        pass
```

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | >= 2.0 | Yes | 시계열 처리, rolling 연산 |
| numpy | >= 1.24 | Yes | 상관행렬, 선형대수 |
| scipy | >= 1.11 | Yes | z-score, Spearman 상관 |
| statsmodels | >= 0.14 | Yes | 회귀 분석 보조 |

## E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 레짐별 팩터 가중치 | < 100ms (8팩터 × 252일) | `time.perf_counter()` |
| 크라우딩 감지 | < 500ms (8팩터 × 5년 스프레드) | z-score rolling 포함 |
| 팩터 모멘텀 | < 50ms (8팩터 × 252일) | 누적 수익률 + 순위 |
| 상관 분석 | < 100ms (8×8 행렬 × 2 윈도우) | 상관행렬 2회 계산 |
| 전체 파이프라인 | < 2s | 4개 항목 순차 실행 |
| 메모리 | < 50MB | `tracemalloc` 프로파일링 |

## E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 매크로 레짐 미확정 | REGIME_FACTOR_PRIOR에서 "NEUTRAL" 기본값 (all 1.0) 사용 | HIGH |
| 팩터 수익률 결측 (특정 팩터) | 해당 팩터 제외, 나머지 재정규화 | WARNING |
| 밸류에이션 스프레드 데이터 부족 (< 1260일) | 가용 데이터로 z-score 계산, confidence 감쇄 | WARNING |
| 상관행렬 특이행렬 | 대각 정규화 (shrinkage toward identity) | LOW |
| 크라우딩 z > 3.0 (극단 크라우딩) | 해당 팩터 가중치 0으로 강제, 경고 로그 | CRITICAL |
| 모멘텀 6M/12M 순위 불일치 (Spearman < 0.3) | confidence 0.5배 감쇄, 모멘텀 신호 약화 | WARNING |
| Circuit Breaker 발동 (-3%) | 팩터 타이밍 신호 전체 비활성화 | CRITICAL |

## E8. Test Criteria

- **Unit**:
  - 레짐 가중치: EXPANSION 레짐 → MOMENTUM 가중치 > VALUE 가중치 확인
  - 크라우딩: 밸류에이션 스프레드 극단 축소 + 자금 유입 급증 → alert=True 확인
  - 팩터 모멘텀: 수익률 상위 팩터 weight > 1.0, 하위 < 1.0 확인
  - 상관 분석: 합성 위기 데이터 (all corr=0.9) → diversification_valid=False 확인
  - Edge case: 단일 팩터만 존재, 모든 수익률 동일, 252일 미만 데이터
- **Integration**:
  - `FactorTimingResult` → `PortfolioOptimizer` 정상 전달 확인
  - `MacroRegimeEngine` → `FactorTimingEngine` 레짐 연계 E2E
  - 51% Gate 통과: confidence >= 0.51 시에만 팩터 배분 신호 전파
- **Acceptance**:
  - 레짐 기반 팩터 배분 → 동일 비중 대비 연환산 초과 수익 >= 1% (백테스트 2015~2024)
  - 크라우딩 경고 후 3개월 내 해당 팩터 리버설 발생 적중률 >= 55%
  - 전체 파이프라인 < 2s 성능 기준 충족

## E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 51% Gate threshold = 0.51 | SPEC §6.1 | confidence >= 0.51이어야 팩터 배분 신호 전파 |
| Circuit Breaker -3% | SPEC §10.2 | 일일 손실 -3% 시 팩터 타이밍 비활성화 |
| 팩터 모멘텀 윈도우 (126일, 252일) | SPEC §14 | 6M/12M 기간 변경 불가, LOCK 해제 절차 필요 |
| 크라우딩 z-score 임계값 = 2.0 | SPEC §14 | 경고 기준, 변경 시 LOCK 해제 필요 |
| 상관 위기 임계값 = 0.7 | SPEC §14 | 팩터 분산 무효 판정 기준 |
| 레짐→팩터 prior 매핑 | SPEC §14 | REGIME_FACTOR_PRIOR 테이블 변경 시 LOCK 해제 필요 |

---

> **L3 판정**: 9요소 전수 기재 완료 (E1~E9). **L3 PASS**.
> **검증일**: 2026-03-22
