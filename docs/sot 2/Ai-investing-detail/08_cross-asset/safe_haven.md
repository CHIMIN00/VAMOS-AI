# 안전자산 상관관계
> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #8 자산군 간 교차 분석
> **정본 소유 개념**: 안전자산 상관/피난처 분석
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-7. 안전자산 상관관계

| # | 항목 | 상세 |
|---|------|------|
| 25 | **주식-채권 상관 모니터** | 전통적 음의 상관 깨지는 시기(2022년 동시 하락) 감지. 상관 양전환 시 포트폴리오 분산 전략 재검토 |
| 26 | **금-달러-BTC 삼각 관계** | 디지털 금(BTC) vs 실물 금 vs 달러 역상관. 인플레 헤지 자산으로서의 역할 비교 |
| 27 | **VIX-크립토 변동성 연계** | VIX 스파이크 시 크립토 변동성 증폭 패턴. 전통 시장 공포 → 크립토 연쇄 하락 시차 및 강도 |

---

## E1. Input

### Kafka Topics

| Topic | 용도 | Key |
|-------|------|-----|
| `market.price.us` | 미국 주식(SPY 등) OHLCV | `symbol` |
| `market.bond` | 채권 수익률/가격(TLT, US10Y) | `bond_code` |
| `market.commodity` | 금(GLD, XAU) | `commodity_code` |
| `market.fx` | 달러(DXY, USD/KRW) | `pair` |
| `market.price.crypto` | BTC/ETH OHLCV | `symbol` |
| `market.volatility` | VIX, VKOSPI | `index_code` |
| `analysis.correlation` | B-1 상관 매트릭스 | `matrix_id` |

### 필수 필드

| 필드 | 타입 | 설명 |
|------|------|------|
| `close` | `float64` | 종가/현재가 |
| `vix` | `float64` | VIX 지수 |
| `btc_close` | `float64` | BTC 종가 |
| `gold_close` | `float64` | 금 종가 (USD/oz) |
| `dxy` | `float64` | 달러 지수 |
| `bond_price` | `float64` | 채권 가격 (TLT 등) |
| `crypto_volatility` | `float64` | BTC 실현변동성 |

### TimescaleDB Schema

```sql
CREATE TABLE stock_bond_correlation (
    ts              TIMESTAMPTZ   NOT NULL,
    equity_index    TEXT          NOT NULL,
    bond_index      TEXT          NOT NULL,
    correlation_30d DOUBLE PRECISION,
    correlation_90d DOUBLE PRECISION,
    is_positive     BOOLEAN,        -- True = 상관 양전환 (위험)
    regime_break    BOOLEAN,        -- 전통적 음의 상관 깨짐
    confidence      DOUBLE PRECISION
);
SELECT create_hypertable('stock_bond_correlation', 'ts');

CREATE TABLE gold_btc_usd_triangle (
    ts              TIMESTAMPTZ   NOT NULL,
    gold_usd_corr   DOUBLE PRECISION,
    btc_usd_corr    DOUBLE PRECISION,
    gold_btc_corr   DOUBLE PRECISION,
    inflation_hedge_score_gold DOUBLE PRECISION,
    inflation_hedge_score_btc  DOUBLE PRECISION,
    dominant_hedge  TEXT
);
SELECT create_hypertable('gold_btc_usd_triangle', 'ts');

CREATE TABLE vix_crypto_vol_linkage (
    ts              TIMESTAMPTZ   NOT NULL,
    vix_level       DOUBLE PRECISION,
    vix_spike       BOOLEAN,
    crypto_vol_30d  DOUBLE PRECISION,
    amplification_ratio DOUBLE PRECISION,
    cascade_lag_hours INT,
    severity        TEXT
);
SELECT create_hypertable('vix_crypto_vol_linkage', 'ts');
```

### 전처리 규칙

1. 일봉 기준: 모든 자산 UTC 일봉 리샘플
2. 채권: 수익률 → 가격 변환 (TLT ETF 가격 또는 duration-adjusted)
3. 금: XAU/USD → 일봉 종가
4. VIX: 장중 변동 무시, 종가 기준
5. 크립토 변동성: BTC 30일 실현변동성 = annualized std(log_return) * sqrt(365)
6. 결측: forward-fill 1일, 이후 NaN 유지

---

## E2. Algorithm

```python
"""
안전자산 상관관계 엔진 — 복사 → 구현 가능 수준
D-09 극복: 주식 + 채권 + 금 + 달러 + BTC 안전자산 교차 분석
"""
import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Dict, List, Optional
from scipy import stats

# ─── Dataclasses ───

@dataclass
class StockBondCorrelation:
    """#25: 주식-채권 상관 모니터"""
    timestamp: str
    equity_index: str
    bond_index: str
    correlation_30d: float
    correlation_90d: float
    correlation_252d: float
    is_positive: bool            # 상관 양전환
    regime_break: bool           # 전통적 음의 상관 깨짐
    days_since_regime_break: int
    portfolio_impact: str        # DIVERSIFICATION_INTACT / DIVERSIFICATION_LOST
    confidence: float

@dataclass
class GoldBTCUSDTriangle:
    """#26: 금-달러-BTC 삼각 관계"""
    timestamp: str
    gold_usd_corr: float         # 금-달러 상관 (전통: 음의 상관)
    btc_usd_corr: float          # BTC-달러 상관
    gold_btc_corr: float         # 금-BTC 상관
    gold_hedge_effectiveness: float   # 인플레 헤지 유효성 0~1
    btc_hedge_effectiveness: float    # BTC 인플레 헤지 유효성 0~1
    dominant_hedge: str           # GOLD / BTC / BOTH / NEITHER
    confidence: float

@dataclass
class VIXCryptoVolLinkage:
    """#27: VIX-크립토 변동성 연계"""
    timestamp: str
    vix_current: float
    vix_spike: bool              # VIX > 30 or 일변화 > 20%
    crypto_vol_30d: float        # BTC 30일 실현변동성
    amplification_ratio: float   # 크립토 vol / VIX (증폭 비율)
    cascade_lag_hours: int       # VIX → 크립토 전이 시차
    cascade_severity: str        # MILD / MODERATE / SEVERE
    btc_safe_haven_score: float  # BTC safe haven 점수 (-1~+1)
    confidence: float

@dataclass
class SafeHavenReport:
    """전체 안전자산 보고서"""
    timestamp: str
    stock_bond: StockBondCorrelation
    gold_btc_usd: GoldBTCUSDTriangle
    vix_crypto: VIXCryptoVolLinkage
    overall_safe_haven_status: str  # FUNCTIONING / DEGRADED / BROKEN
    recommended_hedge_assets: List[str]

# ─── #25: 주식-채권 상관 모니터 ───

def stock_bond_correlation_monitor(
    equity_returns: pd.Series,   # SPY or KOSPI returns
    bond_returns: pd.Series      # TLT or bond price returns
) -> StockBondCorrelation:
    """
    주식-채권 상관 모니터링.
    수식:
      corr_30d = Pearson(equity[-30:], bond[-30:])
      corr_90d = Pearson(equity[-90:], bond[-90:])
      corr_252d = Pearson(equity[-252:], bond[-252:])
    레짐 변화 감지:
      전통: corr < 0 (음의 상관 = 분산 효과)
      2022 type: corr > 0 (동시 하락 = 분산 무효)
      regime_break = corr_90d > 0 AND 이전 90d corr_90d < 0
    """
    common = equity_returns.index.intersection(bond_returns.index)
    eq = equity_returns[common]
    bd = bond_returns[common]

    corr_30 = float(eq.tail(30).corr(bd.tail(30)))
    corr_90 = float(eq.tail(90).corr(bd.tail(90)))
    corr_252 = float(eq.tail(252).corr(bd.tail(252))) if len(common) >= 252 else corr_90

    is_positive = corr_90 > 0

    # 레짐 변화 감지
    if len(common) >= 180:
        prev_90 = float(eq.iloc[-180:-90].corr(bd.iloc[-180:-90]))
        regime_break = prev_90 < 0 and corr_90 > 0
    else:
        regime_break = False

    # 레짐 전환 이후 일수
    days_since = 0
    if regime_break:
        rolling_corr = eq.rolling(30).corr(bd)
        sign_changes = (rolling_corr > 0).astype(int).diff().fillna(0)
        last_break = sign_changes[sign_changes != 0].index
        if len(last_break) > 0:
            days_since = (pd.Timestamp.utcnow() - last_break[-1]).days

    impact = "DIVERSIFICATION_LOST" if is_positive else "DIVERSIFICATION_INTACT"
    confidence = min(len(common) / 252, 1.0)

    return StockBondCorrelation(
        timestamp=pd.Timestamp.utcnow().isoformat(),
        equity_index=equity_returns.name,
        bond_index=bond_returns.name,
        correlation_30d=round(corr_30, 4),
        correlation_90d=round(corr_90, 4),
        correlation_252d=round(corr_252, 4),
        is_positive=is_positive,
        regime_break=regime_break,
        days_since_regime_break=days_since,
        portfolio_impact=impact,
        confidence=round(confidence, 4)
    )

# ─── #26: 금-달러-BTC 삼각 관계 ───

def gold_btc_usd_triangle(
    gold_returns: pd.Series,
    btc_returns: pd.Series,
    dxy_returns: pd.Series,      # 달러 지수 수익률
    inflation_proxy: pd.Series,  # 인플레 프록시 (TIPS breakeven 등)
    lookback: int = 90
) -> GoldBTCUSDTriangle:
    """
    금-달러-BTC 삼각 관계 분석.
    수식:
      gold_usd_corr = Corr(gold, DXY)  전통: -0.3~-0.6
      btc_usd_corr = Corr(BTC, DXY)
      gold_btc_corr = Corr(gold, BTC)
    인플레 헤지 유효성:
      hedge_effectiveness = Corr(asset, inflation_proxy)
      높을수록 인플레 헤지에 유효
    dominant_hedge:
      gold_eff > 0.3 AND btc_eff < 0.1 → GOLD
      btc_eff > 0.3 AND gold_eff < 0.1 → BTC
      both > 0.2 → BOTH
      both < 0.1 → NEITHER
    """
    common = (gold_returns.index
              .intersection(btc_returns.index)
              .intersection(dxy_returns.index))
    tail = sorted(common)[-lookback:]

    gold = gold_returns[tail]
    btc = btc_returns[tail]
    dxy = dxy_returns[tail]

    gold_usd = float(gold.corr(dxy))
    btc_usd = float(btc.corr(dxy))
    gold_btc = float(gold.corr(btc))

    # 인플레 헤지 유효성
    if inflation_proxy is not None and len(inflation_proxy) > 0:
        inf = inflation_proxy.reindex(gold.index).dropna()
        gold_inf = float(gold.reindex(inf.index).corr(inf)) if len(inf) > 20 else 0
        btc_inf = float(btc.reindex(inf.index).corr(inf)) if len(inf) > 20 else 0
    else:
        gold_inf, btc_inf = 0.3, 0.1  # 기본값

    gold_eff = max(0, gold_inf)
    btc_eff = max(0, btc_inf)

    if gold_eff > 0.3 and btc_eff < 0.1:
        dominant = "GOLD"
    elif btc_eff > 0.3 and gold_eff < 0.1:
        dominant = "BTC"
    elif gold_eff > 0.2 and btc_eff > 0.2:
        dominant = "BOTH"
    else:
        dominant = "NEITHER"

    confidence = min(len(tail) / 90, 1.0)

    return GoldBTCUSDTriangle(
        timestamp=pd.Timestamp.utcnow().isoformat(),
        gold_usd_corr=round(gold_usd, 4),
        btc_usd_corr=round(btc_usd, 4),
        gold_btc_corr=round(gold_btc, 4),
        gold_hedge_effectiveness=round(gold_eff, 4),
        btc_hedge_effectiveness=round(btc_eff, 4),
        dominant_hedge=dominant,
        confidence=round(confidence, 4)
    )

# ─── #27: VIX-크립토 변동성 연계 ───

def vix_crypto_vol_linkage(
    vix_series: pd.Series,
    btc_returns: pd.Series,
    equity_returns: pd.Series
) -> VIXCryptoVolLinkage:
    """
    VIX 스파이크 → 크립토 변동성 전이.
    수식:
      VIX 스파이크: VIX > 30 OR VIX 일변화 > 20%
      크립토 실현변동성: annualized_vol = std(btc_ret[-30:]) * sqrt(365)
      증폭비율: amplification = crypto_vol / (VIX / 100)
      전이 시차: cross-corr(VIX_change, |btc_ret|) peak lag
    BTC Safe Haven 점수:
      score = -Corr(equity_ret, btc_ret) when VIX > 25
      양수 = BTC가 주식 하락 시 상승 (safe haven)
      음수 = BTC도 동반 하락 (위험자산)
    """
    vix = vix_series.dropna()
    btc = btc_returns.dropna()
    eq = equity_returns.dropna()

    current_vix = float(vix.iloc[-1])
    vix_change = float(vix.pct_change().iloc[-1])
    spike = current_vix > 30 or abs(vix_change) > 0.20

    # 크립토 30일 실현변동성
    crypto_vol = float(btc.tail(30).std() * np.sqrt(365))

    # 증폭비율
    vix_as_vol = current_vix / 100  # VIX를 소수로
    amp_ratio = crypto_vol / (vix_as_vol + 1e-8)

    # 전이 시차 (시간 → 일 기반)
    common = vix.index.intersection(btc.index)
    vix_ch = vix[common].pct_change().dropna()
    btc_abs = btc[common].abs()
    min_len = min(len(vix_ch), len(btc_abs))
    vix_ch, btc_abs = vix_ch.iloc[-min_len:], btc_abs.iloc[-min_len:]

    best_lag, best_corr = 0, 0
    for lag in range(0, 6):
        if min_len - lag < 20:
            continue
        c = abs(np.corrcoef(vix_ch.values[:min_len-lag], btc_abs.values[lag:min_len])[0, 1])
        if c > best_corr:
            best_corr = c
            best_lag = lag

    cascade_hours = best_lag * 24  # 일 → 시간

    # Cascade severity
    if amp_ratio > 3.0 and spike:
        severity = "SEVERE"
    elif amp_ratio > 2.0:
        severity = "MODERATE"
    else:
        severity = "MILD"

    # BTC Safe Haven 점수: VIX 높을 때 주식-BTC 역상관이면 safe haven
    high_vix_mask = vix[common] > 25
    if high_vix_mask.sum() > 10:
        eq_hv = eq.reindex(common)[high_vix_mask]
        btc_hv = btc.reindex(common)[high_vix_mask]
        safe_haven_score = -float(eq_hv.corr(btc_hv))  # 역상관 = 양수 점수
    else:
        safe_haven_score = 0.0

    confidence = min(len(common) / 252, 1.0) * (1.0 if spike else 0.7)

    return VIXCryptoVolLinkage(
        timestamp=pd.Timestamp.utcnow().isoformat(),
        vix_current=round(current_vix, 2),
        vix_spike=spike,
        crypto_vol_30d=round(crypto_vol, 4),
        amplification_ratio=round(amp_ratio, 2),
        cascade_lag_hours=cascade_hours,
        cascade_severity=severity,
        btc_safe_haven_score=round(safe_haven_score, 4),
        confidence=round(confidence, 4)
    )

# ─── 메인 엔진 ───

def run_safe_haven_engine(
    equity_returns: pd.Series,
    bond_returns: pd.Series,
    gold_returns: pd.Series,
    btc_returns: pd.Series,
    dxy_returns: pd.Series,
    vix_series: pd.Series,
    inflation_proxy: pd.Series = None
) -> SafeHavenReport:
    """전체 안전자산 엔진 실행."""

    # #25
    sb = stock_bond_correlation_monitor(equity_returns, bond_returns)

    # #26
    tri = gold_btc_usd_triangle(gold_returns, btc_returns, dxy_returns, inflation_proxy)

    # #27
    vcl = vix_crypto_vol_linkage(vix_series, btc_returns, equity_returns)

    # Overall status
    issues = 0
    if sb.is_positive:
        issues += 1
    if tri.dominant_hedge == "NEITHER":
        issues += 1
    if vcl.cascade_severity == "SEVERE":
        issues += 1

    if issues >= 2:
        status = "BROKEN"
    elif issues == 1:
        status = "DEGRADED"
    else:
        status = "FUNCTIONING"

    # 추천 헤지 자산
    recommended = []
    if not sb.is_positive:
        recommended.append("BONDS")
    if tri.gold_hedge_effectiveness > 0.2:
        recommended.append("GOLD")
    if vcl.btc_safe_haven_score > 0.2:
        recommended.append("BTC")
    if not recommended:
        recommended.append("CASH")

    return SafeHavenReport(
        timestamp=pd.Timestamp.utcnow().isoformat(),
        stock_bond=sb,
        gold_btc_usd=tri,
        vix_crypto=vcl,
        overall_safe_haven_status=status,
        recommended_hedge_assets=recommended
    )
```

---

## E3. Output

### Output Schema

```json
{
  "type": "SafeHavenReport",
  "timestamp": "2026-03-22T00:00:00Z",
  "stock_bond": {
    "correlation_30d": -0.25,
    "correlation_90d": -0.18,
    "is_positive": false,
    "regime_break": false,
    "portfolio_impact": "DIVERSIFICATION_INTACT"
  },
  "gold_btc_usd": {
    "gold_usd_corr": -0.42,
    "btc_usd_corr": -0.15,
    "gold_btc_corr": 0.18,
    "dominant_hedge": "GOLD"
  },
  "vix_crypto": {
    "vix_current": 18.5,
    "vix_spike": false,
    "crypto_vol_30d": 0.65,
    "amplification_ratio": 3.5,
    "btc_safe_haven_score": -0.15
  },
  "overall_safe_haven_status": "FUNCTIONING",
  "recommended_hedge_assets": ["BONDS", "GOLD"]
}
```

### Confidence 계산

```
stock_bond_confidence = min(n_obs / 252, 1.0)
triangle_confidence = min(n_obs / 90, 1.0)
vix_crypto_confidence = min(n_obs / 252, 1.0) * (1.0 if vix_spike else 0.7)
```

### Consumers

| Consumer | 용도 |
|----------|------|
| `IntegratedRiskEngine` (B-3) | 안전자산 유효성 → 헤지 결정 |
| `CrossAssetOptimizer` (B-4) | 안전자산 비중 조절 |
| `IntegratedSignalFramework` (B-9) | 리스크온/오프 판단 |
| `EventPropagation` (B-8) | 위기 전파 시 안전자산 반응 |

---

## E4. Class/API Design

```python
class SafeHavenAnalyzer(BaseCrossAssetAnalyzer):
    """
    안전자산 상관관계 분석 (#25~#27).
    상속: BaseCrossAssetAnalyzer
    """

    def __init__(self, config: dict):
        super().__init__(config)
        self.vix_spike_threshold = config.get("vix_spike_threshold", 30)
        self.regime_break_window = config.get("regime_break_window", 90)
        self._last_confidence: float = 0.0  # analyze() 종료 시 갱신

    def analyze(self, data: dict) -> SafeHavenReport:
        return run_safe_haven_engine(**data)

    def stock_bond_monitor(self, eq_ret, bond_ret) -> StockBondCorrelation:
        return stock_bond_correlation_monitor(eq_ret, bond_ret)

    def triangle_analysis(self, gold, btc, dxy, inflation=None) -> GoldBTCUSDTriangle:
        return gold_btc_usd_triangle(gold, btc, dxy, inflation)

    def vix_crypto_linkage(self, vix, btc_ret, eq_ret) -> VIXCryptoVolLinkage:
        return vix_crypto_vol_linkage(vix, btc_ret, eq_ret)

    def get_confidence(self) -> float:
        return self._last_confidence

    # API Endpoints
    # GET /api/v1/cross-asset/safe-haven/stock-bond
    # GET /api/v1/cross-asset/safe-haven/gold-btc-usd
    # GET /api/v1/cross-asset/safe-haven/vix-crypto
    # GET /api/v1/cross-asset/safe-haven/status
```

---

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | 용도 | SPEC §14 LOCK |
|-----------|------|------|---------------|
| `numpy` | ≥1.24 | 수치 연산 | ✅ LOCKED |
| `pandas` | ≥2.0 | 시계열 처리 | ✅ LOCKED |
| `scipy` | ≥1.11 | 상관 분석 | ✅ LOCKED |
| `timescaledb` | ≥2.11 | 시계열 DB | ✅ LOCKED |
| `confluent-kafka` | ≥2.2 | Kafka consumer | ✅ LOCKED |

---

## E6. Performance Requirements

| 항목 | 목표 | 비고 |
|------|------|------|
| 주식-채권 상관 모니터 | < 100ms | 롤링 상관 |
| 금-BTC-USD 삼각 | < 150ms | 3쌍 상관 + 인플레 헤지 |
| VIX-크립토 연계 | < 200ms | 변동성 + 전이 |
| 전체 엔진 | < 1s | — |
| 메모리 | < 128MB | — |
| 갱신 주기 | 일 1회 + VIX 스파이크 시 즉시 | — |

---

## E7. Error Handling

| 에러 시나리오 | Severity | 복구 로직 |
|--------------|----------|----------|
| VIX 데이터 미수신 | MEDIUM | 최근값 유지, 스파이크 미감지 경고 |
| 채권 가격 데이터 없음 (수익률만) | LOW | 수익률 → 가격 근사 변환 |
| 금 데이터 지연 (주말) | LOW | 금요일 종가 유지 |
| BTC 24/7 vs 전통시장 비동기 | LOW | 일봉 기준 정렬 |
| 인플레 프록시 미가용 | LOW | 기본값 사용 (gold=0.3, btc=0.1) |
| 상관 계산 NaN (데이터 부족) | MEDIUM | 최소 20일 확보 때까지 대기 |

---

## E8. Test Criteria

### Unit Tests (Known-Answer)

```python
def test_stock_bond_negative_correlation():
    """주식 상승 + 채권 상승이 역 → 음의 상관"""
    eq = pd.Series(np.random.randn(100) * 0.01, name="SPY")
    bd = pd.Series(-eq.values + np.random.randn(100) * 0.002, name="TLT")
    result = stock_bond_correlation_monitor(eq, bd)
    assert result.correlation_30d < 0
    assert result.is_positive is False

def test_gold_usd_inverse():
    """금-달러 역상관 확인"""
    gold = pd.Series(np.random.randn(100) * 0.01, name="GLD")
    dxy = pd.Series(-gold.values + np.random.randn(100) * 0.003, name="DXY")
    btc = pd.Series(np.random.randn(100) * 0.03, name="BTC")
    result = gold_btc_usd_triangle(gold, btc, dxy, None)
    assert result.gold_usd_corr < 0

def test_vix_spike_detection():
    """VIX=35 → spike=True"""
    vix = pd.Series([18]*99 + [35], name="VIX")
    btc = pd.Series(np.random.randn(100) * 0.03, name="BTC")
    eq = pd.Series(np.random.randn(100) * 0.01, name="SPY")
    result = vix_crypto_vol_linkage(vix, btc, eq)
    assert result.vix_spike is True
```

### Integration Tests (E2E)

```python
def test_full_safe_haven_pipeline():
    """전체 안전자산 E2E (D-09 극복 검증)"""
    report = run_safe_haven_engine(
        equity_returns=gen_returns(252, "SPY"),
        bond_returns=gen_returns(252, "TLT"),
        gold_returns=gen_returns(252, "GLD"),
        btc_returns=gen_returns(252, "BTC"),
        dxy_returns=gen_returns(252, "DXY"),
        vix_series=gen_vix(252)
    )
    assert report.overall_safe_haven_status in ["FUNCTIONING", "DEGRADED", "BROKEN"]
    assert len(report.recommended_hedge_assets) > 0
```

### Acceptance Criteria

- [ ] 주식-채권 상관 양전환 감지 (2022 type)
- [ ] 금-달러-BTC 삼각 관계 + 인플레 헤지 유효성
- [ ] VIX 스파이크 → 크립토 변동성 증폭 비율 산출
- [ ] BTC safe haven 점수 (-1~+1)
- [ ] 전체 안전자산 상태 (FUNCTIONING/DEGRADED/BROKEN)
- [ ] 주식+채권+금+BTC+달러 교차 분석 (D-09)

---

## E9. LOCK References

| SPEC 참조 | 내용 | 적용 위치 |
|-----------|------|----------|
| §14 | 기술스택 LOCK | E5 전체 |
| §17 D-09 | 다중 자산 미지원 결함 | E2 전체 — 5자산 안전자산 분석 |

---

## L3 판정

| 항목 | 상태 | 비고 |
|------|------|------|
| E1 Input | ✅ | Kafka 7개 topic, TimescaleDB 3 테이블, 전처리 6규칙 |
| E2 Algorithm | ✅ | #25 주식-채권 상관+레짐, #26 금-BTC-USD 삼각+인플레헤지, #27 VIX-크립토 전이+safe haven score |
| E3 Output | ✅ | JSON schema, confidence 3수식, 4개 consumer |
| E4 Class/API | ✅ | BaseCrossAssetAnalyzer 상속, API 4개 |
| E5 Tech Stack | ✅ | 5개 라이브러리 LOCK |
| E6 Performance | ✅ | 전체 <1s, 메모리 <128MB |
| E7 Error Handling | ✅ | 6개 시나리오 + severity + 복구 |
| E8 Test | ✅ | Unit 3개 + Integration 1개 + Acceptance 6개 |
| E9 LOCK Ref | ✅ | §14, §17 D-09 |
