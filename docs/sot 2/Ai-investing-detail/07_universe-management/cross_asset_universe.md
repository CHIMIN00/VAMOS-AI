# 크로스 자산 유니버스 관리
> **버전**: v2.1
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #7 투자 유니버스 관리
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-8. 크로스 자산 유니버스 관리

| # | 항목 | 상세 |
|---|------|------|
| 30 | **자산군 간 통합 유니버스 뷰** | 미국 주식 + 한국 주식 + 크립토를 하나의 통합 뷰에서 관리. 통화 단위 정규화(USD 기준) |
| 31 | **자산군 간 대체 가능성 분석** | 비트코인 vs 금, KOSPI vs S&P 500 등 자산 간 대체/보완 관계 분석 |
| 32 | **환율 노출 관리** | 유니버스 전체의 통화별 노출도. 원화/달러/크립토(USD 기준) 비중 모니터링 |
| 33 | **글로벌 유니버스 확장 준비** | 현재: 미국+한국+크립토. 향후: 일본, 유럽, 동남아 추가 시 유니버스 확장 프레임워크 |
| 34 | **ETF/인덱스 유니버스** | 개별 종목 외 ETF(SPY, QQQ, ARKK 등) 투자 가능 유니버스. 레버리지/인버스 ETF 특수 규칙 |
| 35 | **유니버스 사이즈 최적화** | 너무 넓으면 분석 비용 과다, 너무 좁으면 기회 누락. API 비용(D2.0-07), 계산 자원과 균형 |

---

## E1. Input

### Kafka Topics

| Topic | 용도 | Key |
|-------|------|-----|
| `universe.definition.snapshot` | 자산군별 유니버스 스냅샷 | `universe_id` |
| `market.price.daily` | 일별 가격 (통화 환산용) | `symbol` |
| `market.forex.rates` | 환율 데이터 (KRW/USD, JPY/USD 등) | `currency_pair` |
| `market.etf.metadata` | ETF 메타데이터 (구성종목, 레버리지 배수 등) | `symbol` |
| `system.resource.metrics` | API 호출 비용, 계산 자원 사용량 | `resource_id` |
| `universe.config.update` | 유니버스 설정 변경 | `universe_id` |

### Required Fields

```
forex_rate:
  - currency_pair: str           # "KRW/USD", "JPY/USD", "EUR/USD"
  - rate: float                  # 1 USD = N KRW
  - timestamp: datetime
  - source: str                  # "ECB", "BOK", "INTERNAL"

etf_metadata:
  - symbol: str                  # "SPY", "QQQ", "ARKK"
  - name: str
  - asset_class: str             # "EQUITY", "BOND", "COMMODITY", "MULTI"
  - is_leveraged: bool
  - leverage_factor: float       # 1.0, 2.0, 3.0, -1.0, -2.0
  - expense_ratio: float         # 연간 보수 (%)
  - aum: float                   # 운용자산 (USD)
  - holdings_count: int
  - top_holdings: List[dict]     # [{symbol, weight_pct}]
  - index_tracked: str           # 추종 인덱스

resource_metrics:
  - resource_id: str
  - api_calls_today: int
  - api_calls_limit: int
  - compute_cpu_pct: float
  - compute_memory_mb: float
  - storage_gb: float
  - cost_usd_today: float

unified_asset:
  - symbol: str
  - asset_class: str             # "US_STOCK", "KR_STOCK", "CRYPTO", "ETF"
  - market_cap_usd: float        # USD 환산 시가총액
  - price_usd: float             # USD 환산 가격
  - native_currency: str         # "USD", "KRW"
  - native_price: float          # 원래 통화 가격
  - exchange_rate: float         # 적용된 환율
```

### TimescaleDB Schema

```sql
-- 통합 유니버스 뷰
CREATE TABLE unified_universe (
    universe_id       TEXT NOT NULL,
    symbol            TEXT NOT NULL,
    asset_class       TEXT NOT NULL,
    native_currency   TEXT NOT NULL,
    price_usd         DOUBLE PRECISION,
    market_cap_usd    DOUBLE PRECISION,
    weight_pct        DOUBLE PRECISION,     -- 통합 유니버스 내 비중
    exchange_rate     DOUBLE PRECISION,
    updated_at        TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (universe_id, symbol)
);

-- 환율 이력 (hypertable)
CREATE TABLE forex_history (
    ts                TIMESTAMPTZ NOT NULL,
    currency_pair     TEXT NOT NULL,
    rate              DOUBLE PRECISION,
    source            TEXT
);
SELECT create_hypertable('forex_history', 'ts');

-- 자산군 간 상관관계
CREATE TABLE cross_asset_correlation (
    ts                TIMESTAMPTZ NOT NULL,
    asset_a           TEXT NOT NULL,         -- "US_STOCK", "KR_STOCK", "CRYPTO", "BTC", "GOLD"
    asset_b           TEXT NOT NULL,
    correlation       DOUBLE PRECISION,
    window_days       INT,
    beta              DOUBLE PRECISION       -- asset_a에 대한 asset_b의 베타
);
SELECT create_hypertable('cross_asset_correlation', 'ts');

-- ETF 유니버스
CREATE TABLE etf_universe (
    symbol            TEXT PRIMARY KEY,
    name              TEXT NOT NULL,
    asset_class       TEXT,
    is_leveraged      BOOLEAN DEFAULT FALSE,
    leverage_factor   DOUBLE PRECISION DEFAULT 1.0,
    expense_ratio     DOUBLE PRECISION,
    aum_usd           DOUBLE PRECISION,
    index_tracked     TEXT,
    is_active         BOOLEAN DEFAULT TRUE,
    updated_at        TIMESTAMPTZ DEFAULT NOW()
);

-- 유니버스 사이즈 메트릭 (hypertable)
CREATE TABLE universe_size_metrics (
    ts                TIMESTAMPTZ NOT NULL,
    universe_id       TEXT NOT NULL,
    total_symbols     INT,
    api_calls_daily   INT,
    compute_cost_usd  DOUBLE PRECISION,
    storage_cost_usd  DOUBLE PRECISION,
    coverage_score    DOUBLE PRECISION,      -- 기회 커버리지 점수
    efficiency_score  DOUBLE PRECISION       -- 비용 대비 효율
);
SELECT create_hypertable('universe_size_metrics', 'ts');

-- 글로벌 확장 설정
CREATE TABLE global_market_config (
    market_id         TEXT PRIMARY KEY,      -- "JP", "EU", "SEA"
    market_name       TEXT NOT NULL,
    currency          TEXT NOT NULL,
    exchanges         TEXT[],                -- ["TSE", "EURONEXT"]
    index_base        TEXT[],                -- ["NIKKEI225", "STOXX600"]
    status            TEXT DEFAULT 'PLANNED', -- 'PLANNED', 'TESTING', 'ACTIVE'
    api_provider      TEXT,
    enabled_at        TIMESTAMPTZ
);
```

### Preprocessing Rules

| 항목 | 전처리 규칙 |
|------|------------|
| 환율 | 실시간 갱신 (장중), 장 마감 후 일별 확정 환율 적용 |
| 통화 환산 | 모든 가격/시가총액 USD 기준 정규화, KRW÷환율 |
| ETF 메타데이터 | 일 1회 갱신, AUM/구성종목 비중 업데이트 |
| 레버리지 ETF | 별도 플래그, 포트폴리오 비중 제한 (최대 10%) |
| API 비용 | 종목당 일평균 API 호출 수 × 단가로 비용 추정 |

---

## E2. Algorithm

```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from datetime import datetime, date
from enum import Enum
import math


class MarketRegion(Enum):
    US = "US"
    KR = "KR"
    JP = "JP"
    EU = "EU"
    SEA = "SEA"
    CRYPTO = "CRYPTO"


@dataclass
class UnifiedAsset:
    """통합 유니버스 자산"""
    symbol: str
    asset_class: str
    market_region: MarketRegion
    native_currency: str
    native_price: float
    price_usd: float
    market_cap_usd: float
    weight_pct: float            # 통합 유니버스 내 비중
    exchange_rate: float


@dataclass
class CrossAssetCorrelation:
    """자산군 간 상관관계"""
    asset_a: str
    asset_b: str
    correlation: float
    beta: float
    substitutability: str        # "HIGH_SUBSTITUTE", "COMPLEMENT", "INDEPENDENT"


@dataclass
class CurrencyExposure:
    """통화 노출도"""
    currency: str
    exposure_pct: float          # 포트폴리오 내 비중
    notional_usd: float
    symbol_count: int


@dataclass
class UniverseSizeOptimization:
    """유니버스 사이즈 최적화 결과"""
    current_size: int
    optimal_size: int
    api_cost_daily_usd: float
    compute_cost_daily_usd: float
    coverage_score: float        # 0~100 (기회 커버리지)
    efficiency_score: float      # 0~100 (비용 대비 효율)
    recommendation: str


@dataclass
class CrossAssetUniverseResult:
    """크로스 자산 유니버스 관리 종합 결과"""
    universe_id: str
    timestamp: datetime
    unified_view: List[UnifiedAsset]
    total_assets: int
    by_asset_class: Dict[str, int]
    by_currency: Dict[str, CurrencyExposure]
    cross_correlations: List[CrossAssetCorrelation]
    size_optimization: UniverseSizeOptimization
    etf_count: int
    confidence: float


# ── 30. 자산군 간 통합 유니버스 뷰 ───────────────────────────

def build_unified_universe_view(universes: Dict[str, list],
                                forex_rates: dict) -> List[UnifiedAsset]:
    """
    자산군별 유니버스를 USD 기준 통합 뷰로 병합

    통화 환산:
      US_STOCK: native=USD → 환산 불필요
      KR_STOCK: native=KRW → price_usd = native_price / KRW_USD_rate
      CRYPTO:   native=USD → 환산 불필요
      JP_STOCK: native=JPY → price_usd = native_price / JPY_USD_rate

    비중 계산:
      weight_pct = market_cap_usd / Σ(market_cap_usd) × 100
    """
    unified = []
    total_mcap = 0.0

    currency_map = {
        "US_STOCK": ("USD", 1.0),
        "KR_STOCK": ("KRW", forex_rates.get("KRW/USD", 1300.0)),
        "CRYPTO": ("USD", 1.0),
        "ETF": ("USD", 1.0),
        "JP_STOCK": ("JPY", forex_rates.get("JPY/USD", 150.0)),
        "EU_STOCK": ("EUR", forex_rates.get("EUR/USD", 0.92)),
    }

    for asset_class, assets in universes.items():
        currency, rate = currency_map.get(asset_class, ("USD", 1.0))
        region = _asset_class_to_region(asset_class)

        for asset in assets:
            native_price = asset.get("price", 0)
            native_mcap = asset.get("market_cap", 0)

            if currency == "USD":
                price_usd = native_price
                mcap_usd = native_mcap
            else:
                price_usd = native_price / rate
                mcap_usd = native_mcap / rate

            ua = UnifiedAsset(
                symbol=asset["symbol"],
                asset_class=asset_class,
                market_region=region,
                native_currency=currency,
                native_price=native_price,
                price_usd=price_usd,
                market_cap_usd=mcap_usd,
                weight_pct=0,  # 아래에서 계산
                exchange_rate=rate
            )
            unified.append(ua)
            total_mcap += mcap_usd

    # 비중 계산
    for ua in unified:
        ua.weight_pct = (ua.market_cap_usd / max(total_mcap, 1)) * 100

    return unified


def _asset_class_to_region(asset_class: str) -> MarketRegion:
    mapping = {
        "US_STOCK": MarketRegion.US,
        "KR_STOCK": MarketRegion.KR,
        "CRYPTO": MarketRegion.CRYPTO,
        "JP_STOCK": MarketRegion.JP,
        "EU_STOCK": MarketRegion.EU,
    }
    return mapping.get(asset_class, MarketRegion.US)


# ── 31. 자산군 간 대체 가능성 분석 ───────────────────────────

def analyze_cross_asset_substitutability(returns_a: List[float], returns_b: List[float],
                                         label_a: str, label_b: str,
                                         window: int = 252) -> CrossAssetCorrelation:
    """
    자산군 간 대체/보완 관계 분석

    상관계수:
      ρ = Cov(R_a, R_b) / (σ_a × σ_b)

    베타:
      β = Cov(R_a, R_b) / Var(R_a)
      R_b의 R_a에 대한 민감도

    대체 가능성 판정:
      ρ > 0.7  → HIGH_SUBSTITUTE (대체 가능, 분산 효과 낮음)
      ρ < -0.3 → COMPLEMENT (보완 관계, 분산 효과 높음)
      else     → INDEPENDENT (독립적)

    대표 자산 쌍:
      BTC vs GOLD (디지털 금?)
      KOSPI vs S&P500 (한미 시장 동조화)
      US_STOCK vs CRYPTO (위험자산 상관)
    """
    n = min(len(returns_a), len(returns_b), window)
    ra = returns_a[-n:]
    rb = returns_b[-n:]

    if n < 30:
        return CrossAssetCorrelation(
            asset_a=label_a, asset_b=label_b,
            correlation=0, beta=0, substitutability="INDEPENDENT"
        )

    mean_a = sum(ra) / n
    mean_b = sum(rb) / n
    cov = sum((a - mean_a) * (b - mean_b) for a, b in zip(ra, rb)) / (n - 1)
    var_a = sum((a - mean_a) ** 2 for a in ra) / (n - 1)
    std_a = math.sqrt(var_a)
    std_b = math.sqrt(sum((b - mean_b) ** 2 for b in rb) / (n - 1))

    corr = cov / (std_a * std_b) if (std_a > 0 and std_b > 0) else 0
    beta = cov / var_a if var_a > 0 else 0

    if corr > 0.7:
        subst = "HIGH_SUBSTITUTE"
    elif corr < -0.3:
        subst = "COMPLEMENT"
    else:
        subst = "INDEPENDENT"

    return CrossAssetCorrelation(
        asset_a=label_a, asset_b=label_b,
        correlation=round(corr, 4), beta=round(beta, 4),
        substitutability=subst
    )


# ── 32. 환율 노출 관리 ───────────────────────────────────────

def compute_currency_exposure(unified_view: List[UnifiedAsset]) -> Dict[str, CurrencyExposure]:
    """
    통합 유니버스 통화별 노출도 계산

    노출도:
      exposure_pct = Σ(weight_pct of assets in currency) / Σ(weight_pct) × 100

    경고 조건:
      단일 통화 노출 > 80% → 통화 집중 경고
      KRW 노출 있을 때 환헤지 고려 필요
    """
    by_currency: Dict[str, Dict] = {}

    for asset in unified_view:
        cur = asset.native_currency
        if cur not in by_currency:
            by_currency[cur] = {
                "exposure_pct": 0.0,
                "notional_usd": 0.0,
                "symbol_count": 0
            }
        by_currency[cur]["exposure_pct"] += asset.weight_pct
        by_currency[cur]["notional_usd"] += asset.market_cap_usd
        by_currency[cur]["symbol_count"] += 1

    result = {}
    for cur, data in by_currency.items():
        result[cur] = CurrencyExposure(
            currency=cur,
            exposure_pct=round(data["exposure_pct"], 2),
            notional_usd=round(data["notional_usd"], 2),
            symbol_count=data["symbol_count"]
        )

    return result


# ── 33. 글로벌 유니버스 확장 준비 ────────────────────────────

def prepare_market_expansion(target_market: str,
                             market_config: dict) -> dict:
    """
    글로벌 시장 확장 프레임워크

    확장 절차:
      1. 시장 설정 등록 (통화, 거래소, 인덱스)
      2. API 프로바이더 연결 검증
      3. 데이터 품질 테스트 (30일 파일럿)
      4. 유동성/시가총액 기준 설정
      5. 유니버스 빌드 테스트
      6. 프로덕션 활성화

    지원 예정 시장:
      JP: 일본 (NIKKEI225, TOPIX) - JPY
      EU: 유럽 (STOXX600, DAX, CAC40) - EUR
      SEA: 동남아 (STI, SET, IDX) - SGD, THB, IDR
    """
    expansion_plan = {
        "market_id": target_market,
        "market_name": market_config.get("market_name", ""),
        "currency": market_config.get("currency", ""),
        "exchanges": market_config.get("exchanges", []),
        "index_base": market_config.get("index_base", []),
        "api_provider": market_config.get("api_provider", ""),
        "status": "PLANNED",
        "phases": [
            {"phase": 1, "name": "설정 등록", "status": "PENDING"},
            {"phase": 2, "name": "API 연결 검증", "status": "PENDING"},
            {"phase": 3, "name": "30일 데이터 파일럿", "status": "PENDING"},
            {"phase": 4, "name": "유동성/시총 기준 설정", "status": "PENDING"},
            {"phase": 5, "name": "유니버스 빌드 테스트", "status": "PENDING"},
            {"phase": 6, "name": "프로덕션 활성화", "status": "PENDING"},
        ],
        "estimated_symbols": market_config.get("estimated_symbols", 0),
        "estimated_api_cost_daily": market_config.get("estimated_api_cost", 0),
    }
    return expansion_plan


# ── 34. ETF/인덱스 유니버스 ──────────────────────────────────

def build_etf_universe(etf_metadata: list,
                       config: dict) -> List[dict]:
    """
    ETF 유니버스 구성

    편입 기준:
      - AUM >= $100M (소규모 ETF 제외)
      - 일평균 거래량 >= $10M
      - 설정 후 최소 1년 경과

    레버리지/인버스 ETF 특수 규칙:
      - 레버리지 ETF (2x, 3x): 별도 플래그, 포트폴리오 비중 최대 10%
      - 인버스 ETF (-1x, -2x, -3x): 별도 플래그, 헤지 목적만 허용
      - 일일 리밸런싱 특성 → 장기 보유 부적합 경고
    """
    min_aum = config.get("etf_min_aum", 100_000_000)
    min_volume = config.get("etf_min_volume", 10_000_000)
    min_age_days = config.get("etf_min_age_days", 365)

    etf_universe = []
    today = date.today()

    for etf in etf_metadata:
        aum = etf.get("aum", 0)
        volume = etf.get("avg_daily_volume", 0)
        inception = etf.get("inception_date")

        # 기본 필터
        if aum < min_aum:
            continue
        if volume < min_volume:
            continue
        if inception and (today - inception).days < min_age_days:
            continue

        leverage = etf.get("leverage_factor", 1.0)
        is_leveraged = abs(leverage) > 1.0 or leverage < 0
        is_inverse = leverage < 0

        etf_entry = {
            "symbol": etf["symbol"],
            "name": etf.get("name", ""),
            "asset_class": etf.get("asset_class", "EQUITY"),
            "is_leveraged": is_leveraged,
            "is_inverse": is_inverse,
            "leverage_factor": leverage,
            "expense_ratio": etf.get("expense_ratio", 0),
            "aum_usd": aum,
            "index_tracked": etf.get("index_tracked", ""),
            "max_weight_pct": 10.0 if is_leveraged else 100.0,
            "holding_warning": "일일 리밸런싱 - 장기보유 부적합" if is_leveraged else None,
        }
        etf_universe.append(etf_entry)

    return etf_universe


# ── 35. 유니버스 사이즈 최적화 ────────────────────────────────

def optimize_universe_size(current_universe: list,
                           resource_metrics: dict,
                           config: dict) -> UniverseSizeOptimization:
    """
    유니버스 사이즈 최적화

    비용 모델:
      api_cost = symbols × calls_per_symbol × cost_per_call
      compute_cost = symbols × compute_per_symbol

    커버리지 모델 (수확 체감):
      coverage = 100 × (1 - e^(-k × symbols))
      k = ln(2) / half_coverage_size
      half_coverage_size: 커버리지 50% 달성에 필요한 종목 수

    효율 점수:
      efficiency = coverage / (api_cost + compute_cost)

    최적 사이즈:
      marginal_benefit / marginal_cost 가 1.0이 되는 지점
      = d(coverage)/d(symbols) = api_cost_per_symbol + compute_cost_per_symbol
    """
    current_size = len(current_universe)

    # 비용 계산
    calls_per_symbol = config.get("api_calls_per_symbol_daily", 10)
    cost_per_call = config.get("api_cost_per_call", 0.001)  # $0.001
    compute_per_symbol = config.get("compute_cost_per_symbol_daily", 0.005)

    api_cost = current_size * calls_per_symbol * cost_per_call
    compute_cost = current_size * compute_per_symbol
    total_cost = api_cost + compute_cost

    # 커버리지 계산
    half_cov_size = config.get("half_coverage_size", 500)
    k = math.log(2) / max(half_cov_size, 1)
    coverage = 100 * (1 - math.exp(-k * current_size))

    # 효율 점수
    efficiency = coverage / max(total_cost, 0.01) * 10  # 스케일링

    # 최적 사이즈 계산 (한계 비용 = 한계 이득)
    marginal_cost = (calls_per_symbol * cost_per_call + compute_per_symbol)
    # d(coverage)/d(n) = 100 * k * e^(-k*n)
    # 100 * k * e^(-k*n_opt) = marginal_cost
    # n_opt = -ln(marginal_cost / (100*k)) / k
    if marginal_cost > 0 and k > 0:
        ratio = marginal_cost / (100 * k)
        if 0 < ratio < 1:
            optimal = int(-math.log(ratio) / k)
        else:
            optimal = current_size
    else:
        optimal = current_size

    optimal = max(100, min(optimal, 5000))  # 100~5000 범위

    # 추천
    if current_size > optimal * 1.3:
        rec = f"유니버스 축소 권장: {current_size} → {optimal} (비용 절감 {((current_size-optimal)/current_size)*100:.0f}%)"
    elif current_size < optimal * 0.7:
        rec = f"유니버스 확대 권장: {current_size} → {optimal} (커버리지 개선)"
    else:
        rec = f"현재 사이즈 적정 (최적 근처: {optimal})"

    return UniverseSizeOptimization(
        current_size=current_size,
        optimal_size=optimal,
        api_cost_daily_usd=round(api_cost, 2),
        compute_cost_daily_usd=round(compute_cost, 2),
        coverage_score=round(coverage, 2),
        efficiency_score=round(min(efficiency, 100), 2),
        recommendation=rec
    )


# ── 전체 크로스 자산 유니버스 오케스트레이터 ──────────────────

def build_cross_asset_universe(universes: Dict[str, list],
                               forex_rates: dict,
                               returns_by_class: dict,
                               etf_metadata: list,
                               resource_metrics: dict,
                               config: dict) -> CrossAssetUniverseResult:
    """
    크로스 자산 유니버스 전체 빌드

    1. 통합 유니버스 뷰 구성 (USD 정규화)
    2. 환율 노출도 계산
    3. 자산군 간 상관관계 분석
    4. ETF 유니버스 통합
    5. 사이즈 최적화
    """
    # 1. 통합 뷰
    unified = build_unified_universe_view(universes, forex_rates)

    # 2. 환율 노출
    currency_exposure = compute_currency_exposure(unified)

    # 3. 자산군 간 상관관계
    correlations = []
    class_pairs = [
        ("US_STOCK", "KR_STOCK"),
        ("US_STOCK", "CRYPTO"),
        ("KR_STOCK", "CRYPTO"),
        ("BTC", "GOLD"),
    ]
    for a, b in class_pairs:
        ra = returns_by_class.get(a, [])
        rb = returns_by_class.get(b, [])
        if ra and rb:
            corr = analyze_cross_asset_substitutability(ra, rb, a, b)
            correlations.append(corr)

    # 4. ETF 유니버스
    etf_univ = build_etf_universe(etf_metadata, config)

    # 5. 사이즈 최적화
    all_assets = unified + [{"symbol": e["symbol"]} for e in etf_univ]
    size_opt = optimize_universe_size(all_assets, resource_metrics, config)

    # 집계
    by_class = {}
    for ua in unified:
        by_class[ua.asset_class] = by_class.get(ua.asset_class, 0) + 1

    return CrossAssetUniverseResult(
        universe_id=config.get("universe_id", "cross_asset"),
        timestamp=datetime.utcnow(),
        unified_view=unified,
        total_assets=len(unified) + len(etf_univ),
        by_asset_class=by_class,
        by_currency=currency_exposure,
        cross_correlations=correlations,
        size_optimization=size_opt,
        etf_count=len(etf_univ),
        confidence=0.90
    )
```

---

## E3. Output

### Output Dataclass

```python
@dataclass
class CrossAssetUniverseResult:
    universe_id: str
    timestamp: datetime
    unified_view: List[UnifiedAsset]
    total_assets: int
    by_asset_class: Dict[str, int]
    by_currency: Dict[str, CurrencyExposure]
    cross_correlations: List[CrossAssetCorrelation]
    size_optimization: UniverseSizeOptimization
    etf_count: int
    confidence: float
```

### Kafka Output Topics

| Topic | 내용 | Key |
|-------|------|-----|
| `universe.crossasset.unified` | 통합 유니버스 뷰 스냅샷 | `universe_id` |
| `universe.crossasset.correlation` | 자산군 간 상관관계 | `asset_pair` |
| `universe.crossasset.currency` | 통화 노출도 리포트 | `universe_id` |
| `universe.crossasset.size` | 사이즈 최적화 결과 | `universe_id` |
| `universe.crossasset.alert` | 통화 집중/사이즈 경고 | `universe_id` |

### Confidence Levels

| Level | 범위 | 의미 |
|-------|------|------|
| HIGH | 0.90 ~ 1.0 | 환율 최신, 모든 자산군 데이터 확보 |
| MEDIUM | 0.70 ~ 0.89 | 일부 환율 지연 또는 자산군 데이터 부분 결측 |
| LOW | < 0.70 | 주요 환율 미갱신 또는 자산군 데이터 대량 결측 |

### Consumers

| Consumer | 용도 |
|----------|------|
| Portfolio Optimizer | 통합 유니버스 기반 자산배분 |
| Risk Manager | 환율 노출, 자산군 상관관계 |
| Universe Definition (B-1) | 사이즈 최적화 피드백 |
| Strategy Engine | 자산군 간 대체 관계 참조 |
| Cost Manager | API/계산 비용 모니터링 |

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod


class BaseCrossAssetManager(ABC):
    """크로스 자산 유니버스 관리 기본 클래스"""

    @abstractmethod
    def build_unified_view(self) -> List[UnifiedAsset]:
        """통합 유니버스 뷰 구성"""
        ...

    @abstractmethod
    def get_currency_exposure(self) -> Dict[str, CurrencyExposure]:
        """통화 노출도 조회"""
        ...


class CrossAssetUniverseService(BaseCrossAssetManager):
    """
    크로스 자산 유니버스 관리 서비스

    Responsibilities:
      - 자산군별 유니버스 통합 (USD 정규화)
      - 자산군 간 대체/보완 관계 분석
      - 환율 노출도 관리
      - ETF 유니버스 관리
      - 글로벌 확장 프레임워크
      - 유니버스 사이즈 최적화
    """

    def __init__(self, db_pool, kafka_producer, universe_services: dict,
                 forex_service, etf_service):
        self.db = db_pool
        self.producer = kafka_producer
        self.universe_svcs = universe_services
        self.forex_svc = forex_service
        self.etf_svc = etf_service

    def build_unified_view(self) -> List[UnifiedAsset]:
        """모든 자산군 통합 뷰 구성"""
        ...

    def get_currency_exposure(self) -> Dict[str, CurrencyExposure]:
        """현재 통화 노출도 계산"""
        ...

    def analyze_substitutability(self, asset_a: str,
                                 asset_b: str) -> CrossAssetCorrelation:
        """자산군 간 대체 가능성 분석"""
        ...

    def build_etf_universe(self) -> List[dict]:
        """ETF 유니버스 구성"""
        ...

    def optimize_size(self) -> UniverseSizeOptimization:
        """유니버스 사이즈 최적화"""
        ...

    def prepare_expansion(self, market: str) -> dict:
        """글로벌 시장 확장 준비"""
        ...

    def get_full_report(self) -> CrossAssetUniverseResult:
        """전체 크로스 자산 리포트"""
        ...
```

---

## E5. Tech Stack Dependency

| Library | Version | LOCK Status | 용도 |
|---------|---------|-------------|------|
| `asyncpg` | 0.29.x | §14 LOCK | TimescaleDB 비동기 접속 |
| `confluent-kafka` | 2.3.x | §14 LOCK | Kafka produce/consume |
| `pandas` | 2.1.x | §14 LOCK | 통합 뷰 구성, 상관관계 계산 |
| `numpy` | 1.26.x | §14 LOCK | 수치 계산, 매트릭스 연산 |
| `pydantic` | 2.5.x | §14 LOCK | 스키마 검증 |
| `httpx` | 0.27.x | §14 LOCK | 환율/ETF API 호출 |
| `redis` | 5.0.x | §14 LOCK | 환율/통합 뷰 캐시 |

---

## E6. Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| 통합 유니버스 뷰 빌드 | ≤ 15s | 전체 자산군 통합 + USD 환산 |
| 자산군 상관관계 분석 | ≤ 10s | 4개 자산군 쌍 분석 |
| 환율 노출도 계산 | ≤ 3s | 전체 통합 유니버스 |
| ETF 유니버스 빌드 | ≤ 5s | 500 ETF 필터링 |
| 사이즈 최적화 계산 | ≤ 2s | 비용/커버리지 모델 |
| 메모리 사용량 | ≤ 512MB | 통합 뷰 + 상관관계 |

---

## E7. Error Handling

| Error Scenario | Recovery Logic | Severity |
|----------------|---------------|----------|
| 환율 데이터 미수신 | 마지막 유효 환율 사용 (1시간 TTL), 1일 이상 → 경고 | HIGH |
| 자산군 유니버스 일부 미로드 | 로드된 자산군만으로 부분 통합 뷰, 미로드 자산군 경고 | MEDIUM |
| ETF 메타데이터 API 실패 | 캐시된 메타데이터 사용, 1주 이상 미갱신 시 경고 | MEDIUM |
| 사이즈 최적화 계산 오류 | 현재 사이즈 유지, 수동 검토 요청 | LOW |
| 글로벌 확장 API 연결 실패 | 해당 시장 상태를 "TESTING_FAILED"로 갱신, 재시도 스케줄 | MEDIUM |
| 통화 변환 0으로 나누기 | rate=0 → 기본 환율(하드코딩) 사용, 경고 로그 | HIGH |

---

## E8. Test Criteria

### Unit Tests

| Test ID | 시나리오 | Expected Result |
|---------|---------|-----------------|
| UT-CA-01 | KRW 1,300,000원 + 환율 1300 → USD 환산 | price_usd=$1,000 |
| UT-CA-02 | USD 자산 → 환산 | price_usd=native_price (변환 없음) |
| UT-CA-03 | 3개 자산군 통합 → 비중 합계 | Σ(weight_pct)=100% |
| UT-CA-04 | ρ=0.85 자산쌍 → 대체 분석 | substitutability="HIGH_SUBSTITUTE" |
| UT-CA-05 | ρ=-0.4 자산쌍 → 대체 분석 | substitutability="COMPLEMENT" |
| UT-CA-06 | USD 70%, KRW 30% → 환율 노출 | exposure 정확 |
| UT-CA-07 | 레버리지 ETF (3x) → ETF 유니버스 | max_weight=10%, warning 포함 |
| UT-CA-08 | AUM $50M ETF → ETF 유니버스 | 미포함 (기준 미달) |
| UT-CA-09 | 종목 800, half_cov=500 → 사이즈 최적화 | coverage ≈ 67%, 최적 사이즈 계산 |
| UT-CA-10 | 종목 2000 + 높은 비용 → 사이즈 최적화 | 축소 권장 |

### Integration Tests

| Test ID | 시나리오 | Expected Result |
|---------|---------|-----------------|
| IT-CA-01 | 3개 자산군 유니버스 → 통합 뷰 → DB 저장 | 15초 이내, USD 환산 정확 |
| IT-CA-02 | 환율 변경 → 통합 뷰 재계산 → 노출도 갱신 | 실시간 반영 |
| IT-CA-03 | ETF 메타데이터 갱신 → ETF 유니버스 재빌드 | 레버리지 규칙 적용 확인 |

### Acceptance Criteria

- [ ] US/KR/Crypto 3개 자산군 USD 기준 통합 뷰 정상 생성
- [ ] 자산군 간 대체/보완 관계 분석 (상관계수 + 베타)
- [ ] 통화별 노출도 실시간 모니터링
- [ ] ETF 유니버스 레버리지/인버스 특수 규칙 적용
- [ ] 유니버스 사이즈 비용-커버리지 최적화 추천
- [ ] 글로벌 확장 프레임워크 6단계 구조 준비

---

## E9. LOCK References

| LOCK 항목 | Source | 적용 |
|-----------|--------|------|
| §14 기술스택 | SPEC §14 | asyncpg, confluent-kafka, pandas, numpy, pydantic, httpx, redis |
| §7 유니버스 관리 | SPEC §7 | 크로스 자산 통합 관리 |
| §6 자산군 정의 | SPEC §6 | US_STOCK, KR_STOCK, CRYPTO + ETF 확장 |
| §8 리스크 관리 | SPEC §8 | 환율 노출, 자산군 상관관계 |
| D2.0-07 API 비용 | SPEC D2.0 | API 호출 비용, 유니버스 사이즈 최적화 |

---

---

## STEP7-I 보강: 한국 펀드/ETF 비교 분석 프레임워크 (S7I-038)

> **보강 근거**: step7i_mapping.md PARTIAL — 한국 시장 펀드/ETF 비교 분석(수익률, 보수(TER), 추적오차, 괴리율, 순자산, 설정일, 분배금) 프레임워크 상세 누락
> **Priority**: HIGH

### E1. Input
- **데이터**: 금융투자협회(KOFIA) API, KRX 정보데이터시스템, 펀드/ETF 운용보고서
- **필수 필드**:
  - `fund_codes: List[str]` — 펀드/ETF 코드 리스트 (표준코드 또는 종목코드)
  - `fund_type: str` — `"ETF"` | `"FUND"` | `"ALL"`
  - `category: str` — 투자 카테고리 (예: `"국내주식형"`, `"해외주식형"`, `"채권형"`, `"혼합형"`)
  - `benchmark_code: str` — 벤치마크 인덱스 코드 (KOSPI, KOSDAQ, KRX300 등)
  - `analysis_period: Tuple[date, date]` — 분석 기간
  - `peer_group_method: str` — 피어 그룹 방식 `"category"` | `"benchmark"` | `"custom"`
  - `comparison_metrics: List[str]` — 비교 지표 `["return", "ter", "tracking_error", "nav_discount", "aum", "distribution"]`
- **전처리**:
  1. 펀드 코드 표준화: 6자리 → ISIN 변환
  2. NAV 데이터 영업일 기준 정렬, 비영업일 제거
  3. 보수(TER) 연율화, 거래비용 포함 총보수비용(TCO) 산출
  4. 분배금 재투자 가정 수익률 (TR index) 계산

### E2. Algorithm
```python
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from datetime import date, datetime
import numpy as np

# ── 한국 펀드/ETF 상수 ──
MIN_AUM_KRW = 10_000_000_000          # 최소 순자산 100억원
MIN_LISTING_DAYS = 180                 # 최소 설정/상장 6개월
ETF_TRACKING_ERROR_WARN = 0.02        # 추적오차 2% 초과 시 경고
ETF_NAV_DISCOUNT_WARN = 0.015         # 괴리율 1.5% 초과 시 경고
KOFIA_API_BASE = "https://dis.kofia.or.kr/proframeWeb/XMLSERVICES"

@dataclass
class KoreanFundInfo:
    """한국 펀드/ETF 정보"""
    fund_code: str
    isin: str
    fund_name: str
    fund_type: str                      # "ETF" | "FUND"
    category: str                       # "국내주식형", "해외주식형" 등
    management_company: str             # 운용사
    inception_date: date                # 설정일
    benchmark: str                      # 벤치마크
    # 수익률
    return_1m: float                    # 1개월 수익률
    return_3m: float
    return_6m: float
    return_1y: float
    return_ytd: float
    return_since_inception: float
    # 비용
    ter: float                          # 총보수비용률 (연율)
    management_fee: float               # 운용보수
    sales_fee: float                    # 판매보수
    custody_fee: float                  # 수탁보수
    # ETF 특화
    tracking_error: Optional[float] = None     # 추적오차 (연율)
    nav_discount_rate: Optional[float] = None  # 괴리율 (시장가/NAV - 1)
    avg_spread_bps: Optional[float] = None     # 평균 호가 스프레드 (bps)
    # 공통
    aum_krw: float = 0                  # 순자산 (원)
    nav_per_unit: float = 0             # 기준가격
    distribution_yield: float = 0       # 분배금 수익률 (연율)
    distribution_frequency: str = ""    # 분배금 주기 ("monthly", "quarterly", "annually", "none")
    sharpe_ratio: float = 0
    max_drawdown: float = 0
    volatility: float = 0

@dataclass
class FundComparisonResult:
    """펀드/ETF 비교 결과"""
    category: str
    analysis_period: Tuple[date, date]
    benchmark: str
    funds: List[KoreanFundInfo]
    rankings: Dict[str, List[Dict]]     # metric → [{fund_code, rank, value}]
    recommendation: List[Dict]          # 종합 추천 리스트
    warnings: List[str]
    generated_at: datetime = field(default_factory=datetime.utcnow)

class KoreanFundComparator:
    """한국 펀드/ETF 비교 분석 엔진"""

    def __init__(self, kofia_client, krx_client, config: Dict = None):
        self.kofia = kofia_client
        self.krx = krx_client
        self.config = config or {}

    # ── 1. 펀드 데이터 수집 (금융투자협회 API) ──
    def fetch_fund_data(self, fund_codes: List[str],
                         start_date: date, end_date: date) -> List[KoreanFundInfo]:
        """
        금융투자협회(KOFIA) + KRX API → 펀드/ETF 상세 정보 수집.
        - 기본 정보: 펀드명, 설정일, 운용사, 카테고리, 벤치마크
        - NAV 시계열: 일별 기준가격 → 수익률 계산
        - 보수 정보: TER = 운용보수 + 판매보수 + 수탁보수 + 기타
        - ETF: 시장가, NAV, 괴리율, 추적오차
        - 분배금: 분배 이력 → 연간 수익률 환산
        """
        funds = []
        for code in fund_codes:
            # KOFIA API: 펀드 기본 정보
            basic_info = self.kofia.get_fund_info(code)
            # KOFIA API: NAV 시계열
            nav_series = self.kofia.get_nav_series(code, start_date, end_date)
            # KRX: ETF 시장가 (ETF인 경우)
            market_prices = self.krx.get_etf_prices(code, start_date, end_date) if basic_info["type"] == "ETF" else None

            # 수익률 계산
            returns = self._calculate_returns(nav_series, start_date, end_date)

            # 보수 계산
            ter = (basic_info.get("management_fee", 0) +
                   basic_info.get("sales_fee", 0) +
                   basic_info.get("custody_fee", 0) +
                   basic_info.get("other_fee", 0))

            # ETF 추적오차/괴리율
            tracking_error = None
            nav_discount = None
            if market_prices is not None and nav_series is not None:
                # 추적오차 = std(fund_return - benchmark_return) * sqrt(252)
                benchmark_returns = self._get_benchmark_returns(basic_info["benchmark"], start_date, end_date)
                fund_returns = np.diff(np.log(nav_series)) if len(nav_series) > 1 else []
                if len(fund_returns) > 0 and len(benchmark_returns) > 0:
                    min_len = min(len(fund_returns), len(benchmark_returns))
                    diff = np.array(fund_returns[-min_len:]) - np.array(benchmark_returns[-min_len:])
                    tracking_error = float(np.std(diff) * np.sqrt(252))

                # 괴리율 = (시장가 - NAV) / NAV
                if len(market_prices) > 0 and len(nav_series) > 0:
                    nav_discount = float((market_prices[-1] - nav_series[-1]) / max(nav_series[-1], 1))

            # 분배금 수익률
            distributions = self.kofia.get_distributions(code, start_date, end_date)
            dist_total = sum(d.get("amount", 0) for d in distributions)
            dist_yield = dist_total / max(nav_series[0], 1) if nav_series else 0
            # 연율화
            days = (end_date - start_date).days
            dist_yield_annual = dist_yield * (365 / max(days, 1))

            # Sharpe, MDD, 변동성
            if len(fund_returns) > 20:
                vol = float(np.std(fund_returns) * np.sqrt(252))
                avg_ret = float(np.mean(fund_returns) * 252)
                sharpe = (avg_ret - 0.035) / max(vol, 1e-8)  # 무위험 3.5% 가정
                cum_returns = np.exp(np.cumsum(np.array(fund_returns)))
                running_max = np.maximum.accumulate(cum_returns)
                drawdowns = (cum_returns - running_max) / running_max
                mdd = float(np.min(drawdowns))
            else:
                vol, sharpe, mdd = 0, 0, 0

            fund = KoreanFundInfo(
                fund_code=code,
                isin=basic_info.get("isin", ""),
                fund_name=basic_info.get("name", ""),
                fund_type=basic_info.get("type", "FUND"),
                category=basic_info.get("category", ""),
                management_company=basic_info.get("company", ""),
                inception_date=basic_info.get("inception_date", start_date),
                benchmark=basic_info.get("benchmark", ""),
                return_1m=returns.get("1m", 0),
                return_3m=returns.get("3m", 0),
                return_6m=returns.get("6m", 0),
                return_1y=returns.get("1y", 0),
                return_ytd=returns.get("ytd", 0),
                return_since_inception=returns.get("since_inception", 0),
                ter=ter,
                management_fee=basic_info.get("management_fee", 0),
                sales_fee=basic_info.get("sales_fee", 0),
                custody_fee=basic_info.get("custody_fee", 0),
                tracking_error=tracking_error,
                nav_discount_rate=nav_discount,
                aum_krw=basic_info.get("aum", 0),
                nav_per_unit=nav_series[-1] if nav_series else 0,
                distribution_yield=round(dist_yield_annual, 4),
                distribution_frequency=self._infer_dist_freq(distributions),
                sharpe_ratio=round(sharpe, 4),
                max_drawdown=round(mdd, 4),
                volatility=round(vol, 4),
            )
            funds.append(fund)

        return funds

    def _calculate_returns(self, nav_series, start_date, end_date) -> Dict[str, float]:
        """NAV 시계열로부터 기간별 수익률 계산"""
        if not nav_series or len(nav_series) < 2:
            return {}
        current = nav_series[-1]
        returns = {}
        periods = {"1m": 21, "3m": 63, "6m": 126, "1y": 252}
        for label, days in periods.items():
            if len(nav_series) > days:
                prev = nav_series[-(days+1)]
                returns[label] = (current - prev) / max(prev, 1)
        returns["since_inception"] = (current - nav_series[0]) / max(nav_series[0], 1)
        returns["ytd"] = returns.get("1y", 0)  # 간소화
        return returns

    def _get_benchmark_returns(self, benchmark: str, start: date, end: date):
        """벤치마크 수익률 시계열 조회"""
        return self.krx.get_index_returns(benchmark, start, end)

    def _infer_dist_freq(self, distributions) -> str:
        """분배금 이력으로부터 분배 주기 추론"""
        if not distributions:
            return "none"
        n = len(distributions)
        if n >= 10:
            return "monthly"
        elif n >= 3:
            return "quarterly"
        else:
            return "annually"

    # ── 2. 피어 그룹 구성 ──
    def group_peers(self, funds: List[KoreanFundInfo],
                     method: str = "category") -> Dict[str, List[KoreanFundInfo]]:
        """
        펀드를 피어 그룹으로 분류.
        - category: 동일 카테고리 (국내주식형, 해외주식형 등)
        - benchmark: 동일 벤치마크 추종
        - custom: 사용자 지정 그룹
        """
        groups: Dict[str, List[KoreanFundInfo]] = {}
        for fund in funds:
            if method == "category":
                key = fund.category
            elif method == "benchmark":
                key = fund.benchmark
            else:
                key = "custom"
            groups.setdefault(key, []).append(fund)
        return groups

    # ── 3. 지표별 메트릭 계산 및 정규화 ──
    def compute_metrics(self, funds: List[KoreanFundInfo]) -> Dict[str, List[Dict]]:
        """
        각 비교 지표별 값 산출 + 그룹 내 백분위 계산.
        지표: 수익률(높을수록 좋음), 보수(낮을수록 좋음), 추적오차(낮을수록 좋음),
              괴리율(0에 가까울수록 좋음), 순자산(높을수록 좋음), 분배금(높을수록 좋음)
        """
        metrics = {}

        # 수익률 순위 (높을수록 좋음)
        metrics["return_1y"] = sorted(
            [{"fund_code": f.fund_code, "value": f.return_1y, "fund_name": f.fund_name} for f in funds],
            key=lambda x: x["value"], reverse=True
        )

        # TER 순위 (낮을수록 좋음)
        metrics["ter"] = sorted(
            [{"fund_code": f.fund_code, "value": f.ter, "fund_name": f.fund_name} for f in funds],
            key=lambda x: x["value"]
        )

        # 추적오차 순위 (ETF만, 낮을수록 좋음)
        etf_funds = [f for f in funds if f.tracking_error is not None]
        if etf_funds:
            metrics["tracking_error"] = sorted(
                [{"fund_code": f.fund_code, "value": f.tracking_error, "fund_name": f.fund_name} for f in etf_funds],
                key=lambda x: x["value"]
            )

        # 괴리율 순위 (ETF만, |값| 작을수록 좋음)
        if etf_funds:
            metrics["nav_discount"] = sorted(
                [{"fund_code": f.fund_code, "value": abs(f.nav_discount_rate or 0), "fund_name": f.fund_name} for f in etf_funds],
                key=lambda x: x["value"]
            )

        # 순자산 순위 (높을수록 좋음 — 유동성)
        metrics["aum"] = sorted(
            [{"fund_code": f.fund_code, "value": f.aum_krw, "fund_name": f.fund_name} for f in funds],
            key=lambda x: x["value"], reverse=True
        )

        # 분배금 수익률 순위 (높을수록 좋음)
        metrics["distribution"] = sorted(
            [{"fund_code": f.fund_code, "value": f.distribution_yield, "fund_name": f.fund_name} for f in funds],
            key=lambda x: x["value"], reverse=True
        )

        # Sharpe 순위
        metrics["sharpe"] = sorted(
            [{"fund_code": f.fund_code, "value": f.sharpe_ratio, "fund_name": f.fund_name} for f in funds],
            key=lambda x: x["value"], reverse=True
        )

        # 순위 부여
        for metric_name, ranked_list in metrics.items():
            for i, item in enumerate(ranked_list):
                item["rank"] = i + 1

        return metrics

    # ── 4. 종합 순위 및 추천 ──
    def rank_funds(self, funds: List[KoreanFundInfo],
                    metrics: Dict[str, List[Dict]]) -> List[Dict]:
        """
        종합 점수 산출 → 순위 결정 → 추천.
        종합 점수 = Σ(가중치_i × 백분위_i)
        가중치: 수익률 30%, Sharpe 25%, 보수 20%, 추적오차 10%, 유동성 10%, 분배금 5%
        """
        weights = {
            "return_1y": 0.30,
            "sharpe": 0.25,
            "ter": 0.20,           # 역순위 (낮을수록 좋음)
            "tracking_error": 0.10, # 역순위
            "aum": 0.10,
            "distribution": 0.05,
        }

        fund_scores: Dict[str, float] = {}
        n = len(funds)

        for fund in funds:
            score = 0.0
            for metric_name, w in weights.items():
                if metric_name not in metrics:
                    continue
                ranked = metrics[metric_name]
                rank_entry = next((r for r in ranked if r["fund_code"] == fund.fund_code), None)
                if rank_entry is None:
                    continue
                # 백분위: (n - rank + 1) / n → 1위 = 1.0, 꼴찌 = 1/n
                percentile = (n - rank_entry["rank"] + 1) / max(n, 1)
                score += w * percentile

            fund_scores[fund.fund_code] = round(score, 4)

        # 종합 순위
        sorted_funds = sorted(fund_scores.items(), key=lambda x: x[1], reverse=True)
        result = []
        for rank, (code, score) in enumerate(sorted_funds, 1):
            fund = next(f for f in funds if f.fund_code == code)
            result.append({
                "rank": rank,
                "fund_code": code,
                "fund_name": fund.fund_name,
                "composite_score": score,
                "return_1y": fund.return_1y,
                "ter": fund.ter,
                "sharpe": fund.sharpe_ratio,
                "aum_krw": fund.aum_krw,
                "recommendation": "추천" if score >= 0.7 else "보통" if score >= 0.4 else "주의",
            })

        return result

    # ── 5. 비교 보고서 생성 ──
    def generate_comparison(self, fund_codes: List[str], category: str,
                             benchmark: str, period: Tuple[date, date]) -> FundComparisonResult:
        """전체 비교 분석 파이프라인 실행"""
        # 1. 데이터 수집
        funds = self.fetch_fund_data(fund_codes, period[0], period[1])

        # 2. 필터링 (최소 기준)
        filtered = [f for f in funds
                    if f.aum_krw >= MIN_AUM_KRW
                    and (datetime.now().date() - f.inception_date).days >= MIN_LISTING_DAYS]

        # 3. 지표 계산
        metrics = self.compute_metrics(filtered)

        # 4. 종합 순위
        rankings = self.rank_funds(filtered, metrics)

        # 5. 경고 생성
        warnings = []
        for f in filtered:
            if f.tracking_error and f.tracking_error > ETF_TRACKING_ERROR_WARN:
                warnings.append(f"{f.fund_name}: 추적오차 {f.tracking_error*100:.2f}% (기준 {ETF_TRACKING_ERROR_WARN*100:.1f}% 초과)")
            if f.nav_discount_rate and abs(f.nav_discount_rate) > ETF_NAV_DISCOUNT_WARN:
                warnings.append(f"{f.fund_name}: 괴리율 {f.nav_discount_rate*100:.2f}% (기준 ±{ETF_NAV_DISCOUNT_WARN*100:.1f}% 초과)")

        return FundComparisonResult(
            category=category,
            analysis_period=period,
            benchmark=benchmark,
            funds=filtered,
            rankings=metrics,
            recommendation=rankings,
            warnings=warnings,
        )
```

### E3. Output
- **스키마**:
  ```python
  @dataclass
  class FundComparisonResult:
      category: str
      analysis_period: Tuple[date, date]
      benchmark: str
      funds: List[KoreanFundInfo]
      rankings: Dict[str, List[Dict]]       # 지표별 순위
      recommendation: List[Dict]            # 종합 추천 [{rank, fund_code, composite_score, ...}]
      warnings: List[str]                   # 추적오차/괴리율 경고
      generated_at: datetime
  ```
- **소비자**: 포트폴리오 최적화 엔진 (ETF 선택), 사용자 대시보드 (비교표), `CrossAssetUniverseService` (ETF 유니버스 품질 피드백)

### E4. Class/API Design
```python
class KoreanFundComparator:
    """한국 펀드/ETF 비교 분석 엔진.

    금융투자협회/KRX 데이터 기반 수익률, 보수, 추적오차, 괴리율, 순자산, 분배금 비교.
    """

    def __init__(self, kofia_client, krx_client, config: Dict = None): ...

    def fetch_fund_data(self, fund_codes: List[str],
                         start_date: date, end_date: date) -> List[KoreanFundInfo]:
        """금융투자협회+KRX API → 펀드/ETF 상세 데이터 수집."""
        ...

    def group_peers(self, funds: List[KoreanFundInfo],
                     method: str = "category") -> Dict[str, List[KoreanFundInfo]]:
        """펀드 피어 그룹 분류 (카테고리/벤치마크/커스텀)."""
        ...

    def compute_metrics(self, funds: List[KoreanFundInfo]) -> Dict[str, List[Dict]]:
        """7대 비교 지표 산출 + 그룹 내 순위."""
        ...

    def rank_funds(self, funds: List[KoreanFundInfo],
                    metrics: Dict[str, List[Dict]]) -> List[Dict]:
        """가중 종합 점수 → 추천 순위."""
        ...

    def generate_comparison(self, fund_codes: List[str], category: str,
                             benchmark: str, period: Tuple[date, date]) -> FundComparisonResult:
        """전체 비교 파이프라인: 수집→그룹→메트릭→순위→보고서."""
        ...
```

### E5. Tech Stack Dependency
| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | ≥2.0 | ☑ | NAV 시계열 처리, 수익률 계산 |
| numpy | ≥1.24 | ☑ | 통계량 (Sharpe, MDD, 추적오차) |
| httpx | 0.27.x | ☑ | KOFIA/KRX API 비동기 호출 |
| pydantic | 2.5.x | ☑ | 펀드 데이터 스키마 검증 |
| redis | 5.0.x | ☑ | 펀드 메타데이터 캐시 (1일 TTL) |

### E6. Performance Requirements
| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 단일 펀드 데이터 수집 | ≤ 5s | KOFIA + KRX API RTT |
| 50개 펀드 배치 수집 | ≤ 60s | 병렬 처리 포함 |
| 지표 계산 + 순위 산출 | ≤ 2s | 50개 펀드 기준 |
| 비교 보고서 전체 생성 | ≤ 90s | 수집 + 분석 + 렌더링 |
| 메모리 사용 | ≤ 256MB | 50개 펀드 1년 NAV 기준 |

### E7. Error Handling
| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| KOFIA API 타임아웃 | 캐시 사용 (1일 TTL) + 재시도 (3회) | MEDIUM |
| 펀드 코드 미존재 | 해당 펀드 제외, WARNING 로그 | LOW |
| NAV 데이터 결측 (>5일 연속) | 해당 기간 수익률 NaN, 순위 산출 제외 | MEDIUM |
| 추적오차 계산 불가 (벤치마크 미매칭) | tracking_error=None, 해당 지표 순위 제외 | LOW |
| TER 정보 미공개 | ter=0 처리, WARNING ("보수 정보 미공개") | MEDIUM |
| 순자산 100억 미만 | 분석 대상 제외, 사유 안내 | INFO |

### E8. Test Criteria
- **Unit**:
  - KODEX 200 vs TIGER 200: 동일 벤치마크, TER 차이 확인
  - 추적오차 계산: 인위적 데이터 → 기대값과 ±0.1% 일치
  - 괴리율: 시장가 10,100원, NAV 10,000원 → 괴리율 1.0%
  - 종합 점수: 수익률 1위 + 보수 1위 → 최상위 점수
  - 분배금 수익률: 연 4회 분배, 회당 100원, NAV 10,000원 → 4.0%
- **Integration**:
  - KOFIA API mock → fetch_fund_data → 50개 펀드 데이터 정상 수집
  - 전체 파이프라인: 수집 → 그룹 → 메트릭 → 순위 → 보고서 E2E
- **Acceptance**:
  - 실제 국내 주식형 ETF 20개 비교 → 순위 합리성 검증 (전문가 리뷰)
  - 추적오차/괴리율 경고가 실제 문제 ETF와 일치 (precision ≥ 80%)

### E9. LOCK References
| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 최소 순자산 100억원 | 본 문서 정의 | 유동성 부족 펀드 제외 |
| 최소 설정 6개월 | 본 문서 정의 | 신규 펀드 성과 미확정 |
| 추적오차 경고 2% | 본 문서 정의 | ETF 품질 모니터링 |
| 괴리율 경고 1.5% | 본 문서 정의 | ETF 시장 효율성 모니터링 |
| 종합 점수 가중치 | 본 문서 정의 | 수익률 30%, Sharpe 25%, 보수 20%, TE 10%, AUM 10%, 분배 5% |
| SPEC §14 기술스택 | SPEC §14 | pandas, numpy, httpx, pydantic, redis |

---

## L3 판정

| 섹션 | 상태 | 비고 |
|------|------|------|
| E1. Input | ✅ | Kafka 6개 토픽, TimescaleDB 6개 테이블, 전처리 규칙 |
| E2. Algorithm | ✅ | 6개 항목 전체 Python 구현, 환율 환산/상관계수/커버리지 수식 |
| E3. Output | ✅ | 출력 스키마, Kafka 5개 출력 토픽, confidence 3단계 |
| E4. Class/API Design | ✅ | BaseCrossAssetManager → CrossAssetUniverseService 계층 |
| E5. Tech Stack | ✅ | 7개 라이브러리 §14 LOCK |
| E6. Performance | ✅ | 6개 메트릭 정량 목표 |
| E7. Error Handling | ✅ | 6개 에러 시나리오, 복구 로직, 심각도 |
| E8. Test Criteria | ✅ | UT 10개, IT 3개, AC 6개 |
| E9. LOCK References | ✅ | 5개 SPEC 참조 |
