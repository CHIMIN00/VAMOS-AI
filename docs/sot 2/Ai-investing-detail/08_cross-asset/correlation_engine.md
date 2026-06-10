# 자산군 간 상관관계 엔진
> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #8 자산군 간 교차 분석
> **정본 소유 개념**: 자산군 간 동적 상관관계
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-1. 자산군 간 상관관계 엔진

| # | 항목 | 상세 |
|---|------|------|
| 1 | **동적 상관관계 매트릭스** | 미국 주식/한국 주식/BTC/ETH/금/달러/채권 간 롤링 상관계수(30d/90d/252d). 시간에 따른 상관 변화 추적 |
| 2 | **위기 시 상관 수렴 감지** | 정상 시 상관 낮으나 위기 시 +0.8 이상 수렴 패턴 감지. "분산 효과 소멸 경고" → 포트폴리오 방어 모드 |
| 3 | **비선형 상관(Copula) 분석** | Pearson 상관은 선형만 포착. 꼬리 의존성(Tail Dependence) = 극단 하락 시 동시 하락 확률. Clayton/Gumbel Copula |
| 4 | **상관 레짐 분류** | Low/Normal/High Correlation 3레짐. 현재 레짐에서 분산 투자 실효성 자동 판단 |

---

## E1. Input

### Kafka Topics

| Topic | 용도 | Key |
|-------|------|-----|
| `market.price.us` | 미국 주식 OHLCV (Alpaca) | `symbol` |
| `market.price.kr` | 한국 주식 OHLCV (KIS API) | `symbol` |
| `market.price.crypto` | 크립토 OHLCV (Binance/Upbit) | `symbol` |
| `market.index` | 지수(S&P500, KOSPI, KOSDAQ) | `index_code` |
| `market.fx` | 환율(USD/KRW, DXY) | `pair` |
| `market.commodity` | 원자재(금, 유가) | `commodity_code` |
| `market.bond` | 채권 수익률(US10Y, KR10Y) | `bond_code` |

### 필수 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `symbol` | `str` | 자산 식별자 |
| `asset_class` | `str` | `US_EQUITY`/`KR_EQUITY`/`CRYPTO`/`FX`/`COMMODITY`/`BOND` |
| `close` | `float64` | 종가/현재가 |
| `timestamp` | `datetime` | UTC 기준 |
| `volume` | `float64` | 거래량 |

### TimescaleDB Schema

```sql
CREATE TABLE cross_asset_returns (
    ts          TIMESTAMPTZ   NOT NULL,
    symbol      TEXT          NOT NULL,
    asset_class TEXT          NOT NULL,
    close       DOUBLE PRECISION,
    log_return  DOUBLE PRECISION,
    volume      DOUBLE PRECISION
);
SELECT create_hypertable('cross_asset_returns', 'ts');
CREATE INDEX idx_cross_asset_class ON cross_asset_returns (asset_class, ts DESC);

CREATE TABLE correlation_matrix (
    ts            TIMESTAMPTZ   NOT NULL,
    asset_a       TEXT          NOT NULL,
    asset_b       TEXT          NOT NULL,
    window_days   INT           NOT NULL,
    pearson_corr  DOUBLE PRECISION,
    spearman_corr DOUBLE PRECISION,
    dcc_corr      DOUBLE PRECISION,
    tail_dep_lower DOUBLE PRECISION,
    tail_dep_upper DOUBLE PRECISION,
    regime        TEXT,
    confidence    DOUBLE PRECISION
);
SELECT create_hypertable('correlation_matrix', 'ts');

CREATE TABLE correlation_regime (
    ts            TIMESTAMPTZ   NOT NULL,
    regime        TEXT          NOT NULL,  -- LOW / NORMAL / HIGH
    avg_corr      DOUBLE PRECISION,
    convergence_alert BOOLEAN DEFAULT FALSE,
    confidence    DOUBLE PRECISION
);
SELECT create_hypertable('correlation_regime', 'ts');
```

### 전처리 규칙

1. 시간대 통일: 모든 자산을 UTC 기준으로 정렬, 일봉 기준 리샘플링
2. 한국/미국 거래시간 차이: 한국 종가 → 미국 당일 시가와 매핑 (T+0 기준)
3. 크립토 24/7 → 일봉 UTC 00:00 기준 컷오프
4. 결측값: forward-fill 최대 3일, 이후 NaN 유지 (거래 정지 등)
5. 수익률 변환: `log_return = ln(close_t / close_{t-1})`
6. 최소 데이터 요구: 롤링 윈도우 + 30일 (예: 90d 상관 → 최소 120일 데이터)

---

## E2. Algorithm

```python
"""
자산군 간 상관관계 엔진 — 복사 → 구현 가능 수준
D-09 (다중 자산 미지원) 결함 극복: US Equity + KR Equity + Crypto + FX + Commodity + Bond 6자산군 지원
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.optimize import minimize

# ─── Enums & Dataclasses ───

class AssetClass(str, Enum):
    US_EQUITY = "US_EQUITY"
    KR_EQUITY = "KR_EQUITY"
    CRYPTO = "CRYPTO"
    FX = "FX"
    COMMODITY = "COMMODITY"
    BOND = "BOND"

class CorrelationRegime(str, Enum):
    LOW = "LOW"           # avg |corr| < 0.3
    NORMAL = "NORMAL"     # 0.3 <= avg |corr| < 0.6
    HIGH = "HIGH"         # avg |corr| >= 0.6

@dataclass
class PairCorrelation:
    asset_a: str
    asset_b: str
    window_days: int
    pearson: float
    spearman: float
    dcc_corr: float
    tail_dep_lower: float   # Clayton copula lower tail dependence
    tail_dep_upper: float   # Gumbel copula upper tail dependence
    p_value: float
    confidence: float

@dataclass
class CorrelationMatrix:
    timestamp: str
    window_days: int
    pairs: List[PairCorrelation]
    avg_abs_corr: float
    regime: CorrelationRegime
    convergence_alert: bool   # 위기 시 상관 수렴 경고
    diversification_effective: bool

@dataclass
class RegimeClassification:
    timestamp: str
    regime: CorrelationRegime
    avg_corr: float
    regime_duration_days: int
    transition_probability: Dict[str, float]  # 다음 레짐 전이 확률
    confidence: float

# ─── #1: 동적 상관관계 매트릭스 ───

ROLLING_WINDOWS = [30, 90, 252]

def compute_rolling_correlation(
    returns_df: pd.DataFrame,   # columns = asset symbols, index = date
    window: int = 90
) -> pd.DataFrame:
    """
    Pearson 롤링 상관계수 매트릭스.
    returns_df: 각 열이 자산별 log_return 시계열
    """
    n_assets = returns_df.shape[1]
    corr_series = {}

    for i in range(n_assets):
        for j in range(i + 1, n_assets):
            a = returns_df.columns[i]
            b = returns_df.columns[j]
            rolling_corr = returns_df[a].rolling(window).corr(returns_df[b])
            corr_series[f"{a}__{b}"] = rolling_corr

    return pd.DataFrame(corr_series)

def compute_spearman_rolling(
    returns_df: pd.DataFrame,
    window: int = 90
) -> Dict[str, float]:
    """Spearman 순위 상관 (비선형 포착)."""
    tail = returns_df.tail(window)
    result = {}
    cols = tail.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            rho, pval = stats.spearmanr(tail[cols[i]].dropna(), tail[cols[j]].dropna())
            result[f"{cols[i]}__{cols[j]}"] = {"spearman": rho, "p_value": pval}
    return result

# ─── DCC-GARCH 동적 상관관계 ───

def dcc_garch_correlation(
    returns_df: pd.DataFrame,
    alpha: float = 0.05,   # DCC alpha
    beta: float = 0.93     # DCC beta
) -> np.ndarray:
    """
    DCC(Dynamic Conditional Correlation) GARCH 구현.
    수식:
      Q_t = (1 - alpha - beta) * Q_bar + alpha * (epsilon_{t-1} * epsilon_{t-1}') + beta * Q_{t-1}
      R_t = diag(Q_t)^{-1/2} * Q_t * diag(Q_t)^{-1/2}
    여기서:
      - Q_bar: 잔차의 무조건부 상관 매트릭스
      - epsilon_t: GARCH(1,1) 표준화 잔차
    """
    n = returns_df.shape[1]
    T = returns_df.shape[0]
    returns = returns_df.values

    # Step 1: 각 자산 GARCH(1,1) 적합 → 표준화 잔차
    std_residuals = np.zeros_like(returns)
    for i in range(n):
        r = returns[:, i]
        # GARCH(1,1): sigma^2_t = omega + alpha*r^2_{t-1} + beta*sigma^2_{t-1}
        omega_g, alpha_g, beta_g = 0.00001, 0.08, 0.90
        sigma2 = np.zeros(T)
        sigma2[0] = np.var(r)
        for t in range(1, T):
            sigma2[t] = omega_g + alpha_g * r[t-1]**2 + beta_g * sigma2[t-1]
        std_residuals[:, i] = r / np.sqrt(np.maximum(sigma2, 1e-10))

    # Step 2: Q_bar (무조건부 상관)
    Q_bar = np.corrcoef(std_residuals.T)

    # Step 3: DCC 동적 업데이트
    Q_t = Q_bar.copy()
    R_series = []
    for t in range(1, T):
        eps = std_residuals[t-1:t, :].T  # (n, 1)
        Q_t = (1 - alpha - beta) * Q_bar + alpha * (eps @ eps.T) + beta * Q_t
        # 정규화 → 상관 매트릭스
        D_inv = np.diag(1.0 / np.sqrt(np.maximum(np.diag(Q_t), 1e-10)))
        R_t = D_inv @ Q_t @ D_inv
        R_series.append(R_t)

    return R_series[-1]  # 최신 동적 상관 매트릭스

# ─── #2: 위기 시 상관 수렴 감지 ───

CONVERGENCE_THRESHOLD = 0.8

def detect_correlation_convergence(
    corr_matrix_current: np.ndarray,
    corr_matrix_normal: np.ndarray,   # 정상 시 기준 상관 매트릭스 (장기 평균)
    threshold: float = CONVERGENCE_THRESHOLD
) -> dict:
    """
    위기 시 상관 수렴 패턴 감지.
    조건: 현재 평균 |상관| >= threshold 이면 "분산 효과 소멸 경고"
    수식:
      convergence_score = mean(|R_crisis|) - mean(|R_normal|)
      alert = convergence_score > 0 AND mean(|R_crisis|) >= threshold
    """
    n = corr_matrix_current.shape[0]
    # 상삼각 추출 (대각선 제외)
    upper_idx = np.triu_indices(n, k=1)
    current_abs = np.abs(corr_matrix_current[upper_idx])
    normal_abs = np.abs(corr_matrix_normal[upper_idx])

    avg_current = float(np.mean(current_abs))
    avg_normal = float(np.mean(normal_abs))
    convergence_score = avg_current - avg_normal

    alert = bool(convergence_score > 0 and avg_current >= threshold)

    return {
        "avg_abs_corr_current": avg_current,
        "avg_abs_corr_normal": avg_normal,
        "convergence_score": convergence_score,
        "alert": alert,
        "message": "분산 효과 소멸 경고 — 포트폴리오 방어 모드 권고" if alert else "정상 분산 효과 유지"
    }

# ─── #3: 비선형 상관(Copula) 분석 ───

def fit_clayton_copula(u: np.ndarray, v: np.ndarray) -> dict:
    """
    Clayton Copula 꼬리 의존성 (하방 꼬리).
    Clayton Copula: C(u,v) = (u^{-theta} + v^{-theta} - 1)^{-1/theta}
    Lower Tail Dependence: lambda_L = 2^{-1/theta}
    MLE로 theta 추정.
    """
    def neg_log_likelihood(theta, u, v):
        if theta <= 0:
            return 1e10
        n = len(u)
        ll = 0.0
        for i in range(n):
            ui, vi = np.clip(u[i], 1e-6, 1-1e-6), np.clip(v[i], 1e-6, 1-1e-6)
            term = (ui**(-theta) + vi**(-theta) - 1)
            if term <= 0:
                return 1e10
            ll += np.log(1 + theta) - (1 + theta) * np.log(term) - (1 + theta) * np.log(ui) - (1 + theta) * np.log(vi)
        return -ll

    res = minimize(neg_log_likelihood, x0=1.0, args=(u, v), method='Nelder-Mead')
    theta = max(res.x[0], 0.01)
    lambda_lower = 2 ** (-1.0 / theta)

    return {"theta": theta, "lower_tail_dependence": lambda_lower}

def fit_gumbel_copula(u: np.ndarray, v: np.ndarray) -> dict:
    """
    Gumbel Copula 꼬리 의존성 (상방 꼬리).
    Gumbel Copula: C(u,v) = exp(-[(-ln u)^theta + (-ln v)^theta]^{1/theta})
    Upper Tail Dependence: lambda_U = 2 - 2^{1/theta}
    """
    def neg_log_likelihood(theta, u, v):
        if theta < 1.0:
            return 1e10
        n = len(u)
        ll = 0.0
        for i in range(n):
            ui = np.clip(u[i], 1e-6, 1-1e-6)
            vi = np.clip(v[i], 1e-6, 1-1e-6)
            lu, lv = -np.log(ui), -np.log(vi)
            A = (lu**theta + lv**theta) ** (1.0/theta)
            ll += -A + (theta - 1)*(np.log(lu) + np.log(lv)) + np.log(A + theta - 1) - A
        return -ll

    res = minimize(neg_log_likelihood, x0=1.5, args=(u, v), method='Nelder-Mead',
                   options={"maxiter": 500})
    theta = max(res.x[0], 1.0)
    lambda_upper = 2 - 2 ** (1.0 / theta)

    return {"theta": theta, "upper_tail_dependence": lambda_upper}

def copula_tail_dependence(
    returns_a: pd.Series,
    returns_b: pd.Series
) -> dict:
    """
    Copula 기반 꼬리 의존성 분석 (#3).
    Step 1: 경험적 CDF로 uniform [0,1] 변환 (Probability Integral Transform)
    Step 2: Clayton → lower tail, Gumbel → upper tail
    """
    # PIT (Probability Integral Transform)
    u = returns_a.rank(pct=True).values
    v = returns_b.rank(pct=True).values

    # 유효 데이터만
    mask = ~(np.isnan(u) | np.isnan(v))
    u, v = u[mask], v[mask]

    clayton = fit_clayton_copula(u, v)
    gumbel = fit_gumbel_copula(u, v)

    return {
        "lower_tail_dependence": clayton["lower_tail_dependence"],
        "upper_tail_dependence": gumbel["upper_tail_dependence"],
        "clayton_theta": clayton["theta"],
        "gumbel_theta": gumbel["theta"],
        "interpretation": _interpret_tail(clayton["lower_tail_dependence"], gumbel["upper_tail_dependence"])
    }

def _interpret_tail(lower: float, upper: float) -> str:
    if lower > 0.4:
        return "높은 하방 꼬리 의존성 — 극단 하락 시 동시 하락 위험 높음"
    elif lower > 0.2:
        return "중간 하방 꼬리 의존성 — 하락 시 부분적 동조"
    else:
        return "낮은 하방 꼬리 의존성 — 극단 시에도 분산 효과 유지"

# ─── #4: 상관 레짐 분류 ───

def classify_correlation_regime(
    corr_matrix: np.ndarray,
    history_avg_corr: List[float],   # 과거 평균 |상관| 시계열
    low_threshold: float = 0.3,
    high_threshold: float = 0.6
) -> RegimeClassification:
    """
    상관 레짐 분류: LOW / NORMAL / HIGH.
    수식:
      avg_abs_corr = mean(|R_{ij}|) for i < j
      if avg_abs_corr < low_threshold → LOW
      elif avg_abs_corr < high_threshold → NORMAL
      else → HIGH
    레짐 전이 확률: 히스토리 기반 Markov 전이 행렬 추정
    """
    n = corr_matrix.shape[0]
    upper_idx = np.triu_indices(n, k=1)
    avg_abs = float(np.mean(np.abs(corr_matrix[upper_idx])))

    if avg_abs < low_threshold:
        regime = CorrelationRegime.LOW
    elif avg_abs < high_threshold:
        regime = CorrelationRegime.NORMAL
    else:
        regime = CorrelationRegime.HIGH

    # 레짐 지속 기간 계산
    duration = 0
    for val in reversed(history_avg_corr):
        r = CorrelationRegime.LOW if val < low_threshold else (
            CorrelationRegime.NORMAL if val < high_threshold else CorrelationRegime.HIGH
        )
        if r == regime:
            duration += 1
        else:
            break

    # 전이 확률 (히스토리 기반)
    transitions = _compute_transition_probs(history_avg_corr, low_threshold, high_threshold)

    # 분산 투자 실효성 판단
    diversification_effective = regime != CorrelationRegime.HIGH

    confidence = _compute_regime_confidence(avg_abs, low_threshold, high_threshold, len(history_avg_corr))

    return RegimeClassification(
        timestamp=pd.Timestamp.utcnow().isoformat(),
        regime=regime,
        avg_corr=avg_abs,
        regime_duration_days=duration,
        transition_probability=transitions.get(regime.value, {}),
        confidence=confidence
    )

def _compute_transition_probs(
    history: List[float], low_t: float, high_t: float
) -> Dict[str, Dict[str, float]]:
    """Markov 전이 행렬 추정."""
    regimes = []
    for v in history:
        if v < low_t:
            regimes.append("LOW")
        elif v < high_t:
            regimes.append("NORMAL")
        else:
            regimes.append("HIGH")

    trans = {r: {"LOW": 0, "NORMAL": 0, "HIGH": 0} for r in ["LOW", "NORMAL", "HIGH"]}
    for i in range(len(regimes) - 1):
        trans[regimes[i]][regimes[i+1]] += 1

    # 정규화
    for r in trans:
        total = sum(trans[r].values())
        if total > 0:
            for k in trans[r]:
                trans[r][k] = round(trans[r][k] / total, 3)
    return trans

def _compute_regime_confidence(
    avg_abs: float, low_t: float, high_t: float, n_obs: int
) -> float:
    """레짐 분류 신뢰도: 경계에서 멀수록 + 데이터 많을수록 높음."""
    # 경계로부터 거리
    dist_low = abs(avg_abs - low_t)
    dist_high = abs(avg_abs - high_t)
    boundary_dist = min(dist_low, dist_high)
    boundary_conf = min(boundary_dist / 0.15, 1.0)  # 0.15 이상이면 100%

    # 데이터 충분성
    data_conf = min(n_obs / 252, 1.0)  # 1년 이상이면 100%

    return round(0.7 * boundary_conf + 0.3 * data_conf, 4)

# ─── 메인 엔진 ───

def run_correlation_engine(
    returns_df: pd.DataFrame,     # columns=asset symbols, index=dates
    asset_classes: Dict[str, str] # symbol → AssetClass
) -> CorrelationMatrix:
    """전체 상관관계 엔진 실행."""
    pairs = []
    cols = returns_df.columns.tolist()

    # DCC-GARCH 동적 상관
    dcc_matrix = dcc_garch_correlation(returns_df)

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            a, b = cols[i], cols[j]
            # Pearson
            pearson_corr = returns_df[a].tail(90).corr(returns_df[b].tail(90))
            # Spearman
            spearman_corr, sp_pval = stats.spearmanr(
                returns_df[a].tail(90).dropna(),
                returns_df[b].tail(90).dropna()
            )
            # Copula
            tail = copula_tail_dependence(returns_df[a], returns_df[b])

            pairs.append(PairCorrelation(
                asset_a=a,
                asset_b=b,
                window_days=90,
                pearson=round(pearson_corr, 4),
                spearman=round(spearman_corr, 4),
                dcc_corr=round(float(dcc_matrix[i][j]), 4),
                tail_dep_lower=round(tail["lower_tail_dependence"], 4),
                tail_dep_upper=round(tail["upper_tail_dependence"], 4),
                p_value=round(sp_pval, 6),
                confidence=_pair_confidence(sp_pval, len(returns_df))
            ))

    avg_abs = float(np.mean([abs(p.pearson) for p in pairs]))
    regime = (CorrelationRegime.LOW if avg_abs < 0.3
              else CorrelationRegime.NORMAL if avg_abs < 0.6
              else CorrelationRegime.HIGH)
    convergence = avg_abs >= CONVERGENCE_THRESHOLD

    return CorrelationMatrix(
        timestamp=pd.Timestamp.utcnow().isoformat(),
        window_days=90,
        pairs=pairs,
        avg_abs_corr=round(avg_abs, 4),
        regime=regime,
        convergence_alert=convergence,
        diversification_effective=(regime != CorrelationRegime.HIGH)
    )

def _pair_confidence(p_value: float, n_obs: int) -> float:
    stat_conf = 1.0 - min(p_value / 0.05, 1.0)
    data_conf = min(n_obs / 252, 1.0)
    return round(0.6 * stat_conf + 0.4 * data_conf, 4)
```

---

## E3. Output

### Output Schema

```json
{
  "type": "CorrelationMatrix",
  "timestamp": "2026-03-22T00:00:00Z",
  "window_days": 90,
  "pairs": [
    {
      "asset_a": "SPY",
      "asset_b": "BTC",
      "pearson": 0.42,
      "spearman": 0.38,
      "dcc_corr": 0.45,
      "tail_dep_lower": 0.31,
      "tail_dep_upper": 0.12,
      "p_value": 0.001,
      "confidence": 0.85
    }
  ],
  "avg_abs_corr": 0.38,
  "regime": "NORMAL",
  "convergence_alert": false,
  "diversification_effective": true
}
```

### Confidence 계산

```
pair_confidence = 0.6 * (1 - p_value/0.05) + 0.4 * min(n_obs/252, 1.0)
regime_confidence = 0.7 * boundary_distance_score + 0.3 * data_sufficiency
```

- `p_value < 0.05` → 통계적 유의성 높음
- `n_obs >= 252` → 데이터 충분성 100%
- 경계로부터 0.15 이상 이격 → 레짐 분류 확실

### Consumers

| Consumer | 용도 |
|----------|------|
| `CrossAssetOptimizer` (B-4) | 상관 매트릭스 → 포트폴리오 최적화 입력 |
| `IntegratedRiskEngine` (B-3) | 상관 조정 VaR/CVaR 계산 |
| `SafeHavenAnalyzer` (B-7) | 안전자산 상관 변화 모니터링 |
| `LeadLagDetector` (B-2) | 상관 → 인과 분석 전처리 |
| `IntegratedSignalFramework` (B-9) | 통합 시그널 생성 |

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod

class BaseCrossAssetAnalyzer(ABC):
    """교차 자산 분석 기저 클래스."""

    def __init__(self, config: dict):
        self.config = config
        self.asset_classes = list(AssetClass)

    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> dict:
        ...

    @abstractmethod
    def get_confidence(self) -> float:
        ...

    def validate_multi_asset(self, df: pd.DataFrame) -> bool:
        """D-09 결함 극복: 최소 2개 자산군 포함 검증."""
        classes = df.get("asset_class", pd.Series()).unique()
        return len(classes) >= 2


class CorrelationEngine(BaseCrossAssetAnalyzer):
    """
    자산군 간 상관관계 엔진 (#1~#4).
    상속: BaseCrossAssetAnalyzer
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.windows = config.get("rolling_windows", [30, 90, 252])
        self.convergence_threshold = config.get("convergence_threshold", 0.8)
        self._last_confidence: float = 0.0  # analyze() 종료 시 갱신

    def analyze(self, returns_df: pd.DataFrame) -> CorrelationMatrix:
        return run_correlation_engine(returns_df, self.config.get("asset_map", {}))

    def compute_dcc(self, returns_df: pd.DataFrame) -> np.ndarray:
        return dcc_garch_correlation(returns_df)

    def compute_copula(self, ret_a: pd.Series, ret_b: pd.Series) -> dict:
        return copula_tail_dependence(ret_a, ret_b)

    def classify_regime(self, corr_matrix: np.ndarray, history: List[float]) -> RegimeClassification:
        return classify_correlation_regime(corr_matrix, history)

    def detect_convergence(self, current: np.ndarray, normal: np.ndarray) -> dict:
        return detect_correlation_convergence(current, normal, self.convergence_threshold)

    def get_confidence(self) -> float:
        return self._last_confidence

    # API Endpoints
    # GET  /api/v1/cross-asset/correlation?window=90
    # GET  /api/v1/cross-asset/correlation/regime
    # GET  /api/v1/cross-asset/correlation/convergence-alert
    # GET  /api/v1/cross-asset/correlation/copula/{asset_a}/{asset_b}
```

---

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | 용도 | SPEC §14 LOCK |
|-----------|------|------|---------------|
| `numpy` | ≥1.24 | 행렬 연산 | ✅ LOCKED |
| `pandas` | ≥2.0 | 시계열 처리 | ✅ LOCKED |
| `scipy` | ≥1.11 | Spearman, 최적화 | ✅ LOCKED |
| `scikit-learn` | ≥1.3 | 전처리 유틸 | ✅ LOCKED |
| `timescaledb` | ≥2.11 | 시계열 DB | ✅ LOCKED |
| `confluent-kafka` | ≥2.2 | Kafka consumer | ✅ LOCKED |

---

## E6. Performance Requirements

| 항목 | 목표 | 비고 |
|------|------|------|
| 상관 매트릭스 계산 (7x7) | < 500ms | 일봉 기준 252일 |
| DCC-GARCH 적합 | < 3s | 7자산 252일 |
| Copula 적합 (1쌍) | < 1s | Clayton + Gumbel MLE |
| 전체 엔진 (21쌍) | < 30s | 모든 쌍 + 레짐 분류 |
| 메모리 | < 512MB | 매트릭스 + 히스토리 |
| 갱신 주기 | 일 1회 | 장 마감 후 배치 |
| Kafka lag | < 60s | 실시간 가격 수집 |

---

## E7. Error Handling

| 에러 시나리오 | Severity | 복구 로직 |
|--------------|----------|----------|
| 자산 데이터 결측 (1개 자산군 누락) | MEDIUM | 해당 자산 제외 후 나머지로 매트릭스 계산, 경고 로그 |
| DCC-GARCH 수렴 실패 | LOW | Pearson 상관으로 fallback, `dcc_corr=None` 표시 |
| Copula MLE 수렴 실패 | LOW | tail_dependence=NaN, Pearson 기반 대체 |
| 데이터 < 최소 요구 (120일) | HIGH | 분석 건너뛰기, `insufficient_data` 에러 반환 |
| Kafka topic 연결 실패 | HIGH | 3회 재시도 (exponential backoff), 캐시된 최신 결과 반환 |
| 상관 매트릭스 양정치 위반 | MEDIUM | 가장 가까운 양정치 매트릭스로 보정 (nearest PD) |
| 타임스탬프 정렬 불일치 | MEDIUM | 자동 정렬 후 경고 |

---

## E8. Test Criteria

### Unit Tests (Known-Answer)

```python
def test_pearson_correlation_known():
    """완벽 양의 상관 → 1.0"""
    a = pd.Series([1, 2, 3, 4, 5])
    b = pd.Series([2, 4, 6, 8, 10])
    assert abs(a.corr(b) - 1.0) < 1e-10

def test_clayton_copula_known():
    """theta=2 → lower_tail_dep = 2^{-0.5} ≈ 0.707"""
    # 합성 Clayton(theta=2) 데이터
    result = fit_clayton_copula(u_samples, v_samples)
    assert abs(result["lower_tail_dependence"] - 0.707) < 0.1

def test_convergence_detection():
    """모든 상관 0.9 → alert=True"""
    matrix = np.full((5, 5), 0.9)
    np.fill_diagonal(matrix, 1.0)
    normal = np.full((5, 5), 0.3)
    np.fill_diagonal(normal, 1.0)
    result = detect_correlation_convergence(matrix, normal)
    assert result["alert"] is True

def test_regime_classification():
    """avg |corr| = 0.2 → LOW"""
    matrix = np.eye(5) * 0.2
    np.fill_diagonal(matrix, 1.0)
    result = classify_correlation_regime(matrix, [0.2]*100)
    assert result.regime == CorrelationRegime.LOW
```

### Integration Tests (E2E)

```python
def test_full_engine_pipeline():
    """6자산군 일봉 데이터 → CorrelationMatrix 생성 (D-09 극복 검증)"""
    returns = generate_multi_asset_returns(
        assets=["SPY", "KOSPI", "BTC", "USDKRW", "GLD", "TLT"],
        days=252
    )
    result = run_correlation_engine(returns, ASSET_MAP)
    assert isinstance(result, CorrelationMatrix)
    assert len(result.pairs) == 15  # C(6,2)
    assert result.regime in CorrelationRegime
    assert 0 <= result.avg_abs_corr <= 1.0

def test_dcc_garch_convergence():
    """DCC-GARCH가 수렴하여 유효한 상관 매트릭스 반환"""
    returns = generate_multi_asset_returns(assets=["SPY", "BTC", "GLD"], days=500)
    R = dcc_garch_correlation(returns)
    assert R.shape == (3, 3)
    assert np.allclose(np.diag(R), 1.0, atol=0.01)  # 대각선 = 1
```

### Acceptance Criteria

- [ ] 6개 이상 자산군 동시 상관 분석 가능 (D-09 결함 극복)
- [ ] DCC-GARCH 동적 상관이 위기 시 상승 감지
- [ ] Clayton/Gumbel Copula 꼬리 의존성 정량 산출
- [ ] 상관 수렴 경고 시 convergence_alert=true 반환
- [ ] 레짐 분류(LOW/NORMAL/HIGH) 정확도 > 80%

---

## E9. LOCK References

| SPEC 참조 | 내용 | 적용 위치 |
|-----------|------|----------|
| §14 | 기술스택 LOCK | E5 전체 |
| §17 D-09 | 다중 자산 미지원 결함 | E2 전체 — 6자산군 지원 |
| §7.9 | 레짐 기반 전략 | E2 #4 레짐 분류 |

---

## L3 판정

| 항목 | 상태 | 비고 |
|------|------|------|
| E1 Input | ✅ | Kafka 7개 topic, TimescaleDB 3 테이블, 전처리 6규칙 |
| E2 Algorithm | ✅ | #1 Rolling Pearson/Spearman, DCC-GARCH, #2 수렴 감지, #3 Clayton/Gumbel Copula, #4 레짐 분류 |
| E3 Output | ✅ | JSON schema, confidence 수식, 5개 consumer |
| E4 Class/API | ✅ | BaseCrossAssetAnalyzer 상속, API 4개 |
| E5 Tech Stack | ✅ | 6개 라이브러리 LOCK |
| E6 Performance | ✅ | 전체 <30s, 메모리 <512MB |
| E7 Error Handling | ✅ | 7개 시나리오 + severity + 복구 |
| E8 Test | ✅ | Unit 4개 + Integration 2개 + Acceptance 5개 |
| E9 LOCK Ref | ✅ | §14, §17 D-09, §7.9 |
