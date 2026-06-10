# 자산군 간 선행/후행 관계
> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #8 자산군 간 교차 분석
> **정본 소유 개념**: 자산군 간 선행/후행 인과 관계
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-2. 자산군 간 선행/후행 관계

| # | 항목 | 상세 |
|---|------|------|
| 5 | **Granger 인과성 분석** | A 자산이 B 자산을 선행하는지 통계적 검증. BTC → NASDAQ? 미국 금리 → KOSPI? 시차별 인과 관계 매핑 |
| 6 | **크로스 마켓 리드-래그** | 미국 장 마감 → 한국 장 개시 갭 예측. S&P 500 야간 선물 → KOSPI 시가 갭 추정 모델 |
| 7 | **크립토→주식 전이 효과** | BTC 급등/급락이 테크 주식(MSTR, COIN)에 미치는 영향 정량화. 크립토 심리가 전통 시장에 전이되는 패턴 |
| 8 | **원자재→주식 전이** | 유가→에너지 주식, 구리→건설, 리튬→2차전지. 원자재 가격 변동의 주식 전이 시차 및 탄력성 |

---

## E1. Input

### Kafka Topics

| Topic | 용도 | Key |
|-------|------|-----|
| `market.price.us` | 미국 주식/선물 OHLCV (Alpaca) | `symbol` |
| `market.price.kr` | 한국 주식 OHLCV (KIS API) | `symbol` |
| `market.price.crypto` | 크립토 OHLCV (Binance/Upbit) | `symbol` |
| `market.index` | 지수(S&P500 선물, KOSPI, NASDAQ) | `index_code` |
| `market.commodity` | 원자재(WTI, 구리, 리튬, 금) | `commodity_code` |
| `market.bond` | 채권 수익률(US10Y, US2Y) | `bond_code` |
| `analysis.correlation` | 상관관계 엔진 결과 (B-1) | `pair_key` |

### 필수 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `symbol` | `str` | 자산 식별자 |
| `asset_class` | `str` | US_EQUITY/KR_EQUITY/CRYPTO/COMMODITY/BOND |
| `close` | `float64` | 종가/현재가 |
| `timestamp` | `datetime` | UTC 기준 |
| `volume` | `float64` | 거래량 |
| `log_return` | `float64` | 로그 수익률 (전처리 후) |

### TimescaleDB Schema

```sql
CREATE TABLE lead_lag_granger (
    ts            TIMESTAMPTZ   NOT NULL,
    asset_leader  TEXT          NOT NULL,
    asset_follower TEXT         NOT NULL,
    max_lag       INT           NOT NULL,
    f_statistic   DOUBLE PRECISION,
    p_value       DOUBLE PRECISION,
    optimal_lag   INT,
    is_causal     BOOLEAN,
    confidence    DOUBLE PRECISION
);
SELECT create_hypertable('lead_lag_granger', 'ts');

CREATE TABLE cross_correlation_lag (
    ts            TIMESTAMPTZ   NOT NULL,
    asset_a       TEXT          NOT NULL,
    asset_b       TEXT          NOT NULL,
    lag_days      INT           NOT NULL,
    correlation   DOUBLE PRECISION,
    is_peak       BOOLEAN DEFAULT FALSE
);
SELECT create_hypertable('cross_correlation_lag', 'ts');

CREATE TABLE transfer_entropy (
    ts            TIMESTAMPTZ   NOT NULL,
    source        TEXT          NOT NULL,
    target        TEXT          NOT NULL,
    te_value      DOUBLE PRECISION,
    net_te        DOUBLE PRECISION,
    direction     TEXT,
    confidence    DOUBLE PRECISION
);
SELECT create_hypertable('transfer_entropy', 'ts');

CREATE TABLE market_gap_prediction (
    ts              TIMESTAMPTZ   NOT NULL,
    source_market   TEXT          NOT NULL,
    target_market   TEXT          NOT NULL,
    predicted_gap   DOUBLE PRECISION,
    actual_gap      DOUBLE PRECISION,
    model_r2        DOUBLE PRECISION
);
SELECT create_hypertable('market_gap_prediction', 'ts');
```

### 전처리 규칙

1. 시간대 정렬: 미국(ET) → 한국(KST) → 크립토(UTC) 통일 매핑
2. 비동기 마켓: 미국 종가(16:00 ET) → 한국 익일 시가(09:00 KST) 시차 정렬
3. 결측값: forward-fill 최대 3일, 주말/공휴일 제외
4. 정상성 검정: ADF test p < 0.05 확인, 비정상 → 1차 차분
5. 최소 데이터: Granger test → 최소 60일, Transfer Entropy → 최소 252일
6. 로그 수익률: `log_return = ln(P_t / P_{t-1})`

---

## E2. Algorithm

```python
"""
자산군 간 선행/후행 관계 엔진 — 복사 → 구현 가능 수준
D-09 극복: 주식 + 크립토 + 원자재 + 채권 간 인과성/전이 분석
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from scipy import stats
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant

# ─── Dataclasses ───

@dataclass
class GrangerResult:
    """#5: Granger 인과성 분석 결과"""
    asset_leader: str
    asset_follower: str
    max_lag_tested: int
    optimal_lag: int
    f_statistic: float
    p_value: float
    is_causal: bool          # p_value < 0.05
    direction: str           # "A→B", "B→A", "bidirectional", "none"
    confidence: float

@dataclass
class CrossCorrelationResult:
    """#6: 크로스 마켓 리드-래그 결과"""
    asset_a: str
    asset_b: str
    lag_correlations: Dict[int, float]  # lag → correlation
    peak_lag: int              # 최대 상관 lag (양수=A 선행)
    peak_correlation: float
    gap_prediction: Optional[float]  # 시가 갭 예측치

@dataclass
class TransferEntropyResult:
    """정보 전이 엔트로피 결과"""
    source: str
    target: str
    te_source_to_target: float
    te_target_to_source: float
    net_te: float             # 순 정보 전이량
    dominant_direction: str   # source→target or target→source
    confidence: float

@dataclass
class CommodityTransferResult:
    """#8: 원자재→주식 전이 효과"""
    commodity: str
    stock_sector: str
    transfer_lag_days: int
    elasticity: float         # 원자재 1% 변동 → 주식 X% 변동
    r_squared: float
    confidence: float

@dataclass
class LeadLagReport:
    """전체 리드-래그 분석 보고서"""
    timestamp: str
    granger_results: List[GrangerResult]
    cross_correlations: List[CrossCorrelationResult]
    transfer_entropy: List[TransferEntropyResult]
    commodity_transfers: List[CommodityTransferResult]
    top_lead_lag_pairs: List[Dict]  # 가장 강한 선행/후행 관계

# ─── #5: Granger 인과성 분석 ───

def granger_causality_test(
    returns_a: pd.Series,
    returns_b: pd.Series,
    max_lag: int = 10
) -> GrangerResult:
    """
    Granger 인과성 검정.
    H0: A는 B를 Granger-cause 하지 않음
    수식:
      VAR(unrestricted): B_t = c + sum_{i=1}^{p} alpha_i * B_{t-i} + sum_{i=1}^{p} beta_i * A_{t-i} + e_t
      VAR(restricted):   B_t = c + sum_{i=1}^{p} alpha_i * B_{t-i} + e_t
      F = ((SSR_r - SSR_u) / p) / (SSR_u / (T - 2p - 1))
    p_value < 0.05 → A Granger-causes B
    """
    # 정상성 확인
    adf_a = adfuller(returns_a.dropna())[1]
    adf_b = adfuller(returns_b.dropna())[1]

    series_a = returns_a.dropna()
    series_b = returns_b.dropna()

    # 비정상 → 차분
    if adf_a > 0.05:
        series_a = series_a.diff().dropna()
    if adf_b > 0.05:
        series_b = series_b.diff().dropna()

    # 공통 인덱스
    common = series_a.index.intersection(series_b.index)
    data = pd.DataFrame({"A": series_a[common].values, "B": series_b[common].values})

    # A → B 검정
    try:
        result_ab = grangercausalitytests(data[["B", "A"]], maxlag=max_lag, verbose=False)
        # 최적 lag: 최소 p-value
        best_lag_ab = min(result_ab.keys(),
                         key=lambda k: result_ab[k][0]["ssr_ftest"][1])
        f_stat_ab = result_ab[best_lag_ab][0]["ssr_ftest"][0]
        p_val_ab = result_ab[best_lag_ab][0]["ssr_ftest"][1]
    except Exception:
        best_lag_ab, f_stat_ab, p_val_ab = 1, 0.0, 1.0

    # B → A 검정
    try:
        result_ba = grangercausalitytests(data[["A", "B"]], maxlag=max_lag, verbose=False)
        best_lag_ba = min(result_ba.keys(),
                         key=lambda k: result_ba[k][0]["ssr_ftest"][1])
        p_val_ba = result_ba[best_lag_ba][0]["ssr_ftest"][1]
    except Exception:
        p_val_ba = 1.0

    # 방향 결정
    a_causes_b = p_val_ab < 0.05
    b_causes_a = p_val_ba < 0.05
    if a_causes_b and b_causes_a:
        direction = "bidirectional"
    elif a_causes_b:
        direction = f"{returns_a.name}→{returns_b.name}"
    elif b_causes_a:
        direction = f"{returns_b.name}→{returns_a.name}"
    else:
        direction = "none"

    confidence = _granger_confidence(p_val_ab, len(common), max_lag)

    return GrangerResult(
        asset_leader=returns_a.name,
        asset_follower=returns_b.name,
        max_lag_tested=max_lag,
        optimal_lag=best_lag_ab,
        f_statistic=round(f_stat_ab, 4),
        p_value=round(p_val_ab, 6),
        is_causal=a_causes_b,
        direction=direction,
        confidence=confidence
    )

def _granger_confidence(p_value: float, n_obs: int, max_lag: int) -> float:
    stat_conf = max(0, 1.0 - p_value / 0.05)
    data_conf = min(n_obs / (10 * max_lag), 1.0)
    return round(0.6 * stat_conf + 0.4 * data_conf, 4)

# ─── #6: 크로스 마켓 리드-래그 ───

def cross_market_lead_lag(
    returns_a: pd.Series,
    returns_b: pd.Series,
    max_lag: int = 20
) -> CrossCorrelationResult:
    """
    교차 상관(Cross-Correlation) 기반 리드-래그 탐지.
    수식:
      CCF(k) = Corr(A_t, B_{t+k})
      k > 0 → A가 B를 k일 선행
      k < 0 → B가 A를 |k|일 선행
      peak_lag = argmax_k |CCF(k)|
    """
    a = returns_a.dropna().values
    b = returns_b.dropna().values
    n = min(len(a), len(b))
    a, b = a[:n], b[:n]

    lag_corrs = {}
    for k in range(-max_lag, max_lag + 1):
        if k >= 0:
            corr = np.corrcoef(a[:n-k], b[k:n])[0, 1] if n - k > 10 else 0.0
        else:
            corr = np.corrcoef(a[-k:n], b[:n+k])[0, 1] if n + k > 10 else 0.0
        lag_corrs[k] = round(float(corr), 4) if not np.isnan(corr) else 0.0

    peak_lag = max(lag_corrs, key=lambda k: abs(lag_corrs[k]))
    peak_corr = lag_corrs[peak_lag]

    return CrossCorrelationResult(
        asset_a=returns_a.name,
        asset_b=returns_b.name,
        lag_correlations=lag_corrs,
        peak_lag=peak_lag,
        peak_correlation=peak_corr,
        gap_prediction=None
    )

def predict_market_gap(
    us_close_return: pd.Series,    # S&P500 종가 수익률
    kr_open_return: pd.Series,     # KOSPI 시가 갭
    sp_futures_overnight: pd.Series,  # S&P500 야간 선물 수익률
    lookback: int = 60
) -> dict:
    """
    미국 장 마감 → 한국 장 시가 갭 예측 모델.
    수식:
      KOSPI_gap_t = alpha + beta_1 * SP500_ret_{t-1} + beta_2 * SP_futures_overnight_t + epsilon
    """
    us_close_return = us_close_return.shift(1)  # t-1 lag: 전일 미국 종가 → 당일 한국 시가 (lookahead 방지, 모델식 SP500_ret_{t-1} 정합)
    us_close_return = us_close_return.shift(1)  # t-1 lag: 전일 미국 종가 → 당일 한국 시가 (lookahead 방지, 모델식 SP500_ret_{t-1} 정합)
    common = us_close_return.index.intersection(kr_open_return.index).intersection(
        sp_futures_overnight.index
    )
    tail = sorted(common)[-lookback:]

    X = pd.DataFrame({
        "sp500_close": us_close_return[tail].values,
        "sp_futures": sp_futures_overnight[tail].values
    })
    X = add_constant(X)
    y = kr_open_return[tail].values

    model = OLS(y, X).fit()

    # 최신 예측
    latest_x = X.iloc[-1:]
    predicted_gap = float(model.predict(latest_x)[0])

    return {
        "predicted_gap_pct": round(predicted_gap * 100, 3),
        "r_squared": round(model.rsquared, 4),
        "beta_sp500": round(model.params[1], 4),
        "beta_futures": round(model.params[2], 4),
        "model_pvalue": round(model.f_pvalue, 6)
    }

# ─── #7: 크립토→주식 전이 효과 ───

def crypto_to_equity_transfer(
    btc_returns: pd.Series,
    equity_returns: pd.Series,  # MSTR, COIN 등
    lookback: int = 90
) -> dict:
    """
    BTC 급등/급락이 테크 주식에 미치는 영향 정량화.
    수식:
      equity_ret_t = alpha + beta * btc_ret_{t-lag} + epsilon
      lag = argmax_{1..5} R^2
    전이 효과:
      - BTC 수익률 > 2sigma → "급등 이벤트"
      - BTC 수익률 < -2sigma → "급락 이벤트"
      - 이벤트 후 equity 평균 수익률 측정
    """
    btc = btc_returns.dropna().tail(lookback)
    eq = equity_returns.dropna().tail(lookback)
    common = btc.index.intersection(eq.index)
    btc, eq = btc[common], eq[common]

    # 최적 lag 탐색
    best_r2, best_lag, best_beta = 0, 1, 0
    for lag in range(1, 6):
        if len(btc) <= lag:
            continue
        X = add_constant(btc.iloc[:-lag].values)
        y = eq.iloc[lag:].values
        if len(X) != len(y):
            continue
        model = OLS(y, X).fit()
        if model.rsquared > best_r2:
            best_r2 = model.rsquared
            best_lag = lag
            best_beta = model.params[1] if len(model.params) > 1 else 0

    # 이벤트 분석
    sigma = btc.std()
    surge_mask = btc > 2 * sigma
    crash_mask = btc < -2 * sigma

    avg_eq_after_surge = float(eq.shift(-best_lag)[surge_mask].mean()) if surge_mask.sum() > 0 else 0
    avg_eq_after_crash = float(eq.shift(-best_lag)[crash_mask].mean()) if crash_mask.sum() > 0 else 0

    return {
        "optimal_lag_days": best_lag,
        "beta": round(best_beta, 4),
        "r_squared": round(best_r2, 4),
        "avg_equity_after_btc_surge": round(avg_eq_after_surge * 100, 3),
        "avg_equity_after_btc_crash": round(avg_eq_after_crash * 100, 3),
        "transfer_strength": "STRONG" if best_r2 > 0.3 else "MODERATE" if best_r2 > 0.1 else "WEAK"
    }

# ─── Transfer Entropy (정보 전이) ───

def compute_transfer_entropy(
    source: pd.Series,
    target: pd.Series,
    lag: int = 1,
    bins: int = 10
) -> TransferEntropyResult:
    """
    Transfer Entropy: 비선형 인과성 측정.
    수식:
      TE(X→Y) = H(Y_t | Y_{t-1}) - H(Y_t | Y_{t-1}, X_{t-lag})
      = sum p(y_t, y_{t-1}, x_{t-lag}) * log[ p(y_t | y_{t-1}, x_{t-lag}) / p(y_t | y_{t-1}) ]
    Net TE = TE(X→Y) - TE(Y→X)
      > 0 → X dominates information flow to Y
    """
    s = source.dropna().values
    t_arr = target.dropna().values
    n = min(len(s), len(t_arr)) - lag
    if n < 30:
        return TransferEntropyResult(
            source=source.name, target=target.name,
            te_source_to_target=0, te_target_to_source=0,
            net_te=0, dominant_direction="insufficient_data", confidence=0
        )

    x = s[:n]
    y_current = t_arr[lag:lag+n]
    y_past = t_arr[:n]

    # 이산화 (binning)
    x_binned = pd.qcut(x, bins, labels=False, duplicates='drop')
    yc_binned = pd.qcut(y_current, bins, labels=False, duplicates='drop')
    yp_binned = pd.qcut(y_past, bins, labels=False, duplicates='drop')

    # TE(X→Y) = H(Y_t, Y_{t-1}) + H(Y_{t-1}, X_{t-lag}) - H(Y_{t-1}) - H(Y_t, Y_{t-1}, X_{t-lag})
    def entropy(*arrays):
        joint = np.column_stack(arrays)
        _, counts = np.unique(joint, axis=0, return_counts=True)
        probs = counts / counts.sum()
        return -np.sum(probs * np.log2(probs + 1e-12))

    H_yc_yp = entropy(yc_binned, yp_binned)
    H_yp_x = entropy(yp_binned, x_binned)
    H_yp = entropy(yp_binned)
    H_yc_yp_x = entropy(yc_binned, yp_binned, x_binned)

    te_x_to_y = max(0, H_yc_yp + H_yp_x - H_yp - H_yc_yp_x)

    # TE(Y→X)
    x_current = s[lag:lag+n]
    x_past = s[:n]
    xc_binned = pd.qcut(x_current, bins, labels=False, duplicates='drop')
    xp_binned = pd.qcut(x_past, bins, labels=False, duplicates='drop')

    H_xc_xp = entropy(xc_binned, xp_binned)
    H_xp_y = entropy(xp_binned, yp_binned)
    H_xp = entropy(xp_binned)
    H_xc_xp_y = entropy(xc_binned, xp_binned, yp_binned)

    te_y_to_x = max(0, H_xc_xp + H_xp_y - H_xp - H_xc_xp_y)

    net_te = te_x_to_y - te_y_to_x
    dominant = f"{source.name}→{target.name}" if net_te > 0 else f"{target.name}→{source.name}"

    confidence = min(abs(net_te) / 0.1, 1.0) * min(n / 252, 1.0)

    return TransferEntropyResult(
        source=source.name,
        target=target.name,
        te_source_to_target=round(te_x_to_y, 6),
        te_target_to_source=round(te_y_to_x, 6),
        net_te=round(net_te, 6),
        dominant_direction=dominant,
        confidence=round(confidence, 4)
    )

# ─── #8: 원자재→주식 전이 ───

COMMODITY_SECTOR_MAP = {
    "WTI": ["XLE", "에너지"],           # 유가 → 에너지 주식
    "COPPER": ["XLB", "건설"],          # 구리 → 건설/소재
    "LITHIUM": ["LIT", "2차전지"],      # 리튬 → 2차전지
    "GOLD": ["GDX", "금광"],            # 금 → 금광 주식
}

def commodity_to_stock_transfer(
    commodity_returns: pd.Series,
    stock_returns: pd.Series,
    max_lag: int = 10,
    lookback: int = 252
) -> CommodityTransferResult:
    """
    원자재 가격 변동 → 관련 업종 주식 전이.
    수식:
      stock_ret_t = alpha + sum_{k=0}^{max_lag} beta_k * commodity_ret_{t-k} + epsilon
      전이 시차 = argmax_k |beta_k|
      탄력성 = beta_k (원자재 1% → 주식 beta_k%)
    """
    c = commodity_returns.dropna().tail(lookback)
    s = stock_returns.dropna().tail(lookback)
    common = c.index.intersection(s.index)
    c, s = c[common], s[common]

    best_r2, best_lag, best_elasticity = 0, 0, 0
    for lag in range(0, max_lag + 1):
        if len(c) <= lag + 10:
            continue
        X = add_constant(c.iloc[:len(c)-lag].values) if lag > 0 else add_constant(c.values)
        y = s.iloc[lag:].values if lag > 0 else s.values
        min_len = min(len(X), len(y))
        X, y = X[:min_len], y[:min_len]
        model = OLS(y, X).fit()
        if model.rsquared > best_r2:
            best_r2 = model.rsquared
            best_lag = lag
            best_elasticity = model.params[1] if len(model.params) > 1 else 0

    confidence = min(best_r2 / 0.3, 1.0) * min(len(common) / 252, 1.0)

    return CommodityTransferResult(
        commodity=commodity_returns.name,
        stock_sector=stock_returns.name,
        transfer_lag_days=best_lag,
        elasticity=round(best_elasticity, 4),
        r_squared=round(best_r2, 4),
        confidence=round(confidence, 4)
    )

# ─── 메인 엔진 ───

def run_lead_lag_engine(
    returns_dict: Dict[str, pd.Series],  # symbol → return series
    pairs: List[Tuple[str, str]],        # 분석할 쌍 목록
    commodity_stock_map: Dict[str, str]  # commodity → stock
) -> LeadLagReport:
    """전체 리드-래그 엔진 실행."""
    granger_results = []
    cross_corrs = []
    te_results = []
    commodity_results = []

    for a, b in pairs:
        if a in returns_dict and b in returns_dict:
            # Granger
            gr = granger_causality_test(returns_dict[a], returns_dict[b])
            granger_results.append(gr)
            # Cross-correlation
            cc = cross_market_lead_lag(returns_dict[a], returns_dict[b])
            cross_corrs.append(cc)
            # Transfer Entropy
            te = compute_transfer_entropy(returns_dict[a], returns_dict[b])
            te_results.append(te)

    for comm, stock in commodity_stock_map.items():
        if comm in returns_dict and stock in returns_dict:
            ct = commodity_to_stock_transfer(returns_dict[comm], returns_dict[stock])
            commodity_results.append(ct)

    # Top lead-lag pairs by significance
    top_pairs = sorted(granger_results, key=lambda g: g.p_value)[:5]
    top_list = [{"leader": g.asset_leader, "follower": g.asset_follower,
                 "lag": g.optimal_lag, "p_value": g.p_value} for g in top_pairs]

    return LeadLagReport(
        timestamp=pd.Timestamp.utcnow().isoformat(),
        granger_results=granger_results,
        cross_correlations=cross_corrs,
        transfer_entropy=te_results,
        commodity_transfers=commodity_results,
        top_lead_lag_pairs=top_list
    )
```

---

## E3. Output

### Output Schema

```json
{
  "type": "LeadLagReport",
  "timestamp": "2026-03-22T00:00:00Z",
  "granger_results": [
    {
      "asset_leader": "BTC",
      "asset_follower": "NASDAQ",
      "optimal_lag": 2,
      "f_statistic": 4.32,
      "p_value": 0.012,
      "is_causal": true,
      "direction": "BTC→NASDAQ",
      "confidence": 0.82
    }
  ],
  "cross_correlations": [
    {
      "asset_a": "SPY",
      "asset_b": "KOSPI",
      "peak_lag": 1,
      "peak_correlation": 0.65,
      "gap_prediction": 0.35
    }
  ],
  "transfer_entropy": [
    {
      "source": "US10Y",
      "target": "KOSPI",
      "net_te": 0.045,
      "dominant_direction": "US10Y→KOSPI"
    }
  ],
  "commodity_transfers": [
    {
      "commodity": "WTI",
      "stock_sector": "XLE",
      "transfer_lag_days": 2,
      "elasticity": 0.45
    }
  ],
  "top_lead_lag_pairs": [
    {"leader": "BTC", "follower": "NASDAQ", "lag": 2, "p_value": 0.012}
  ]
}
```

### Confidence 계산

```
granger_confidence = 0.6 * (1 - p_value/0.05) + 0.4 * min(n_obs/(10*max_lag), 1.0)
transfer_entropy_confidence = min(|net_te|/0.1, 1.0) * min(n_obs/252, 1.0)
commodity_confidence = min(r2/0.3, 1.0) * min(n_obs/252, 1.0)
```

### Consumers

| Consumer | 용도 |
|----------|------|
| `IntegratedSignalFramework` (B-9) | 리드-래그 기반 매매 시그널 |
| `EventPropagation` (B-8) | 이벤트 전파 경로 입력 |
| `KoreaUSLinkage` (B-6) | 한미 시가 갭 예측 |
| `CryptoEquitySignal` (B-5) | BTC→주식 전이 시그널 |

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod

class LeadLagDetector(BaseCrossAssetAnalyzer):
    """
    자산군 간 선행/후행 관계 분석 (#5~#8).
    상속: BaseCrossAssetAnalyzer
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.max_lag = config.get("max_lag", 10)
        self.significance_level = config.get("significance", 0.05)

    def analyze(self, returns_dict: Dict[str, pd.Series]) -> LeadLagReport:
        pairs = self._generate_pairs(returns_dict)
        return run_lead_lag_engine(returns_dict, pairs, COMMODITY_SECTOR_MAP)

    def granger_test(self, a: pd.Series, b: pd.Series) -> GrangerResult:
        return granger_causality_test(a, b, self.max_lag)

    def cross_correlation(self, a: pd.Series, b: pd.Series) -> CrossCorrelationResult:
        return cross_market_lead_lag(a, b, self.max_lag)

    def transfer_entropy(self, source: pd.Series, target: pd.Series) -> TransferEntropyResult:
        return compute_transfer_entropy(source, target)

    def predict_gap(self, us_close: pd.Series, kr_open: pd.Series,
                    futures: pd.Series) -> dict:
        return predict_market_gap(us_close, kr_open, futures)

    def get_confidence(self) -> float:
        return self._last_confidence

    def _generate_pairs(self, returns_dict: Dict) -> List[Tuple[str, str]]:
        keys = list(returns_dict.keys())
        return [(keys[i], keys[j]) for i in range(len(keys)) for j in range(i+1, len(keys))]

    # API Endpoints
    # GET  /api/v1/cross-asset/lead-lag/granger?asset_a=BTC&asset_b=NASDAQ
    # GET  /api/v1/cross-asset/lead-lag/cross-correlation?asset_a=SPY&asset_b=KOSPI
    # GET  /api/v1/cross-asset/lead-lag/transfer-entropy?source=BTC&target=MSTR
    # GET  /api/v1/cross-asset/lead-lag/gap-prediction?target=KOSPI
    # GET  /api/v1/cross-asset/lead-lag/commodity-transfer?commodity=WTI&sector=XLE
```

---

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | 용도 | SPEC §14 LOCK |
|-----------|------|------|---------------|
| `numpy` | ≥1.24 | 수치 연산 | ✅ LOCKED |
| `pandas` | ≥2.0 | 시계열 처리 | ✅ LOCKED |
| `scipy` | ≥1.11 | 통계 검정 | ✅ LOCKED |
| `statsmodels` | ≥0.14 | Granger, OLS, ADF | ✅ LOCKED |
| `timescaledb` | ≥2.11 | 시계열 DB | ✅ LOCKED |
| `confluent-kafka` | ≥2.2 | Kafka consumer | ✅ LOCKED |

---

## E6. Performance Requirements

| 항목 | 목표 | 비고 |
|------|------|------|
| Granger test (1쌍, lag=10) | < 200ms | 252일 데이터 |
| Cross-correlation (1쌍) | < 100ms | lag ±20 |
| Transfer Entropy (1쌍) | < 500ms | 252일, 10 bins |
| 시가 갭 예측 모델 | < 100ms | OLS 60일 |
| 전체 엔진 (15쌍) | < 15s | 6자산 C(6,2) |
| 메모리 | < 256MB | — |
| 갱신 주기 | 일 1회 + 이벤트 트리거 | 장 마감 후 |

---

## E7. Error Handling

| 에러 시나리오 | Severity | 복구 로직 |
|--------------|----------|----------|
| ADF 정상성 실패 (차분 필요) | LOW | 자동 1차 차분 후 재검정 |
| Granger test 데이터 부족 | MEDIUM | 해당 쌍 건너뛰기, `insufficient_data` 표시 |
| 야간 선물 데이터 미수신 | MEDIUM | S&P500 종가만으로 갭 예측 (beta_futures=0) |
| Transfer Entropy bins 중복 | LOW | `duplicates='drop'` 처리 |
| 비동기 마켓 시차 정렬 오류 | HIGH | 타임스탬프 기반 자동 정렬, 불일치 로그 |
| 원자재 데이터 지연 | MEDIUM | 최신 가용 데이터 사용, 경고 |
| OLS 다중공선성 | LOW | VIF > 10 경고, 변수 제거 |

---

## E8. Test Criteria

### Unit Tests (Known-Answer)

```python
def test_granger_known_cause():
    """A = noise, B = A shifted by 2 → A Granger-causes B"""
    np.random.seed(42)
    a = pd.Series(np.random.randn(500), name="A")
    b = pd.Series(np.concatenate([[0, 0], a.values[:-2]]) + np.random.randn(500)*0.1, name="B")
    result = granger_causality_test(a, b, max_lag=5)
    assert result.is_causal is True
    assert result.optimal_lag == 2

def test_cross_correlation_sync():
    """동일 시계열 → peak_lag=0, correlation=1.0"""
    a = pd.Series(np.random.randn(100), name="X")
    result = cross_market_lead_lag(a, a, max_lag=5)
    assert result.peak_lag == 0
    assert abs(result.peak_correlation - 1.0) < 0.01

def test_transfer_entropy_direction():
    """명확한 인과 방향 → positive net_te"""
    np.random.seed(42)
    x = pd.Series(np.random.randn(500), name="X")
    y = pd.Series(np.concatenate([[0], x.values[:-1]]) + np.random.randn(500)*0.1, name="Y")
    result = compute_transfer_entropy(x, y)
    assert result.net_te > 0  # X→Y

def test_commodity_transfer_known():
    """commodity = stock * 0.5 shifted → elasticity ≈ 0.5"""
    np.random.seed(42)
    comm = pd.Series(np.random.randn(300), name="OIL")
    stock = pd.Series(np.concatenate([[0, 0], comm.values[:-2]]) * 0.5 + np.random.randn(300)*0.05, name="XLE")
    result = commodity_to_stock_transfer(comm, stock)
    assert abs(result.elasticity - 0.5) < 0.2
```

### Integration Tests (E2E)

```python
def test_full_lead_lag_pipeline():
    """6자산군 리드-래그 엔진 E2E (D-09 극복 검증)"""
    returns = {
        "SPY": gen_returns(252), "KOSPI": gen_returns(252),
        "BTC": gen_returns(252), "WTI": gen_returns(252),
        "US10Y": gen_returns(252), "USDKRW": gen_returns(252)
    }
    pairs = [("SPY", "KOSPI"), ("BTC", "SPY"), ("US10Y", "KOSPI")]
    report = run_lead_lag_engine(returns, pairs, {"WTI": "SPY"})
    assert len(report.granger_results) == 3
    assert len(report.commodity_transfers) == 1
    assert isinstance(report.top_lead_lag_pairs, list)

def test_gap_prediction_model():
    """미국→한국 시가 갭 예측 모델 r2 > 0"""
    result = predict_market_gap(sp500_ret, kospi_gap, sp_futures, lookback=60)
    assert result["r_squared"] > 0
    assert "predicted_gap_pct" in result
```

### Acceptance Criteria

- [ ] Granger 인과성 검정이 p < 0.05에서 선행 자산 식별
- [ ] 교차 상관 peak_lag로 정확한 리드-래그 탐지
- [ ] Transfer Entropy가 비선형 인과도 포착
- [ ] 한국 시가 갭 예측 모델 R² > 0.3
- [ ] 원자재→업종 전이 탄력성 산출 가능
- [ ] 다중 자산군(US/KR/Crypto/Commodity) 전부 포함 (D-09)

---

## E9. LOCK References

| SPEC 참조 | 내용 | 적용 위치 |
|-----------|------|----------|
| §14 | 기술스택 LOCK | E5 전체 |
| §17 D-09 | 다중 자산 미지원 결함 | E2 전체 — 주식+크립토+원자재+채권 |
| §7.9 | 레짐 전략 매핑 | E2 #6 갭 예측 |

---

## L3 판정

| 항목 | 상태 | 비고 |
|------|------|------|
| E1 Input | ✅ | Kafka 7개 topic, TimescaleDB 4 테이블, 전처리 6규칙 |
| E2 Algorithm | ✅ | #5 Granger causality, #6 Cross-correlation + 갭 예측, #7 BTC→주식 전이, #8 원자재→업종, Transfer Entropy |
| E3 Output | ✅ | JSON schema, confidence 3수식, 4개 consumer |
| E4 Class/API | ✅ | BaseCrossAssetAnalyzer 상속, API 5개 |
| E5 Tech Stack | ✅ | 6개 라이브러리 LOCK |
| E6 Performance | ✅ | 전체 <15s, 메모리 <256MB |
| E7 Error Handling | ✅ | 7개 시나리오 + severity + 복구 |
| E8 Test | ✅ | Unit 4개 + Integration 2개 + Acceptance 6개 |
| E9 LOCK Ref | ✅ | §14, §17 D-09, §7.9 |
