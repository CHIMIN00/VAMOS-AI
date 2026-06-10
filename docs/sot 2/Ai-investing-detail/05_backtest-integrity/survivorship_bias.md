# Survivorship Bias 방지 시스템
> **버전**: v1.0
> **Status**: APPROVED
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #5 백테스트 진실성
> **정본 소유 개념**: 백테스트 프레임워크 (폴더 전체)
> **기술스택 의존성**: SPEC §14 LOCK 범위 내

---

### B-2. Survivorship Bias 방지 시스템

**현재**: 완전히 없음
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 6 | **상장폐지 종목 포함(Delisted Stocks DB)** | 백테스트 유니버스에 과거 상장폐지된 종목 포함. S&P 500 과거 구성 종목(현재 제외된 종목 포함) 사용 |
| 7 | **인덱스 히스토리컬 구성 추적** | S&P 500, KOSPI 200 등 지수의 **과거 시점 구성 종목** 사용. 현재 구성으로 과거를 테스트하면 생존자만 포함 |
| 8 | **크립토 디리스팅 반영** | 거래소에서 상장폐지된 코인 포함. Binance 디리스팅 코인 히스토리, 러그풀/스캠 코인의 -100% 반영 |
| 9 | **뮤추얼펀드/ETF 생존 편향** | 벤치마크 비교 시 현재 존재하는 펀드만 비교하면 편향. 청산된 펀드 포함 데이터베이스 |

---

## E1. Input - 데이터, 필수 필드, 전처리

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `ticker` | `str` | Y | 종목/펀드/코인 식별자 |
| `listing_date` | `datetime` | Y | 상장일 |
| `delisting_date` | `datetime` | N | 상장폐지일 (None = 현재 상장 중) |
| `delisting_reason` | `str` | N | 폐지 사유 (합병, 파산, 자진 폐지 등) |
| `delisting_return` | `float` | N | 상장폐지 시 최종 수익률 (파산=-1.0) |
| `index_name` | `str` | Y | 소속 지수 (S&P500, KOSPI200 등) |
| `constituent_date` | `datetime` | Y | 해당 지수 구성 종목 시점 |
| `is_constituent` | `bool` | Y | 해당 시점에 지수 구성 종목 여부 |
| `asset_type` | `str` | Y | "equity" / "crypto" / "fund" / "etf" |
| `price_history` | `DataFrame` | Y | OHLCV 시계열 (상장~폐지 전 기간 포함) |

**전처리**:
1. `delisting_date`가 있는 종목: `delisting_return` 필수 확인 → 없으면 -100% 가정 (보수적)
2. 지수 구성 종목: 월별 스냅샷 → 시점별 유니버스 재구성
3. 크립토 디리스팅: 거래소별 디리스팅 히스토리 병합, 러그풀/스캠 분류 태깅

---

## E2. Algorithm - 복사→구현 가능 의사코드 with REAL formulas

```python
# === 상장폐지 종목 포함 유니버스 구성 ===
def build_survivorship_free_universe(
    all_securities: DataFrame,
    as_of_date: datetime,
    index_name: str
) -> list[str]:
    """특정 시점 기준 생존편향 없는 유니버스 반환"""
    # 해당 시점에 상장되어 있었던 모든 종목 (폐지 종목 포함)
    universe = all_securities[
        (all_securities['listing_date'] <= as_of_date) &
        ((all_securities['delisting_date'].isna()) |
         (all_securities['delisting_date'] > as_of_date))
    ]
    # 지수 구성 필터 적용 (해당 시점 구성 종목만)
    if index_name:
        constituents = get_index_constituents(index_name, as_of_date)
        universe = universe[universe['ticker'].isin(constituents)]
    return universe['ticker'].tolist()

# === 인덱스 히스토리컬 구성 추적 (재구성 리플레이) ===
def get_index_constituents(index_name: str, as_of_date: datetime) -> list[str]:
    """지수의 특정 시점 구성 종목 반환 (현재가 아닌 과거 시점)"""
    # 월별 스냅샷에서 as_of_date 이전 가장 가까운 스냅샷 조회
    snapshot = index_history_db[
        (index_history_db["index_name"] == index_name)
        & (index_history_db["constituent_date"] <= as_of_date)
    ].sort_values('constituent_date').iloc[-1]
    return snapshot['tickers']  # 해당 시점 구성 종목 리스트

# === 상장폐지 수익률 반영 ===
def apply_delisting_return(portfolio: DataFrame, delisted: DataFrame) -> DataFrame:
    """상장폐지 종목의 최종 수익률을 포트폴리오에 반영"""
    for _, row in delisted.iterrows():
        ticker = row['ticker']
        delist_date = row['delisting_date']
        delist_return = row.get('delisting_return', -1.0)  # 기본값: -100%

        if ticker in portfolio.columns:
            # 폐지일에 최종 수익률 반영
            portfolio.loc[delist_date, ticker] = delist_return
            # 폐지 이후 NaN 처리 (더 이상 거래 불가)
            portfolio.loc[portfolio.index > delist_date, ticker] = float('nan')
    return portfolio

# === 생존편향 영향도 측정 ===
def measure_survivorship_impact(
    strategy_returns_with_delisted: Series,
    strategy_returns_survivors_only: Series
) -> dict:
    """생존편향 포함/미포함 성과 차이 측정"""
    sharpe_full = compute_sharpe(strategy_returns_with_delisted)
    sharpe_survivors = compute_sharpe(strategy_returns_survivors_only)
    bias_magnitude = sharpe_survivors - sharpe_full  # 양수 = 편향 크기
    return {
        'sharpe_full_universe': sharpe_full,
        'sharpe_survivors_only': sharpe_survivors,
        'survivorship_bias_magnitude': bias_magnitude,
        'bias_pct': bias_magnitude / abs(sharpe_full) * 100 if sharpe_full != 0 else float('inf')
    }
```

---

## E3. Output - @dataclass, confidence, 소비자

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class DelistedSecurity:
    ticker: str
    delisting_date: datetime
    delisting_reason: str
    delisting_return: float
    included_in_backtest: bool

@dataclass
class SurvivorshipBiasReport:
    """Survivorship Bias 검증 리포트"""
    total_securities: int = 0
    delisted_count: int = 0
    delisted_included: int = 0          # 백테스트에 포함된 폐지 종목 수
    delisted_missing: int = 0           # 누락된 폐지 종목 수
    index_snapshots_used: int = 0       # 사용된 지수 구성 스냅샷 수
    bias_magnitude_sharpe: float = 0.0  # 생존편향으로 인한 Sharpe 과대추정
    bias_magnitude_pct: float = 0.0     # 퍼센트
    confidence: float = 0.0             # 0.0~1.0
    passed: bool = False
    details: list[DelistedSecurity] = field(default_factory=list)

    def compute_confidence(self):
        if self.delisted_count == 0:
            self.confidence = 1.0
        else:
            self.confidence = self.delisted_included / self.delisted_count
        self.passed = self.confidence >= 0.95  # 95% 이상 포함 시 통과
```

**소비자**: 백테스트 엔진 (유니버스 구성), 전략 검증 파이프라인, 성과 보고서

---

## E4. Class/API Design - class with methods

```python
class SurvivorshipBiasGuard:
    """Survivorship Bias 방지 통합 클래스"""

    def __init__(self, securities_db: SecuritiesDB, index_history_db: IndexHistoryDB):
        self.securities_db = securities_db
        self.index_history_db = index_history_db

    # --- 상장폐지 종목 포함 유니버스 ---
    def get_universe(self, as_of_date: datetime, index_name: str = None) -> list[str]:
        """생존편향 없는 유니버스 반환"""
        ...

    # --- 인덱스 재구성 리플레이 ---
    def get_index_constituents(self, index_name: str, as_of_date: datetime) -> list[str]:
        """과거 시점 지수 구성 종목 조회"""
        ...

    # --- 상장폐지 수익률 반영 ---
    def apply_delisting_returns(self, portfolio: DataFrame) -> DataFrame:
        """폐지 종목 최종 수익률 포트폴리오에 반영"""
        ...

    # --- 크립토 디리스팅 처리 ---
    def handle_crypto_delisting(self, exchange: str, as_of_date: datetime) -> list[str]:
        """거래소별 디리스팅 코인 포함"""
        ...

    # --- 펀드/ETF 생존편향 ---
    def get_fund_universe(self, as_of_date: datetime, include_liquidated: bool = True) -> list[str]:
        """청산된 펀드 포함 유니버스"""
        ...

    # --- 편향 영향도 측정 ---
    def measure_bias_impact(self, strategy_returns: Series) -> SurvivorshipBiasReport:
        """생존편향 포함/미포함 성과 비교"""
        ...

    # --- 통합 감사 ---
    def audit(self, backtest_config: dict) -> SurvivorshipBiasReport:
        """전체 생존편향 감사"""
        ...
```

---

## E5. Tech Stack Dependency

| 구성 요소 | 기술 | 버전 | 용도 |
|-----------|------|------|------|
| 종목 마스터 DB | PostgreSQL | ≥15.0 | 상장/폐지 이력, 지수 구성 히스토리 |
| 지수 구성 데이터 | S&P Global / KRX | - | 월별 지수 구성 종목 스냅샷 |
| 크립토 디리스팅 | CoinGecko API / Binance API | - | 거래소 디리스팅 히스토리 |
| 펀드 데이터 | Morningstar / CRSP | - | 청산 펀드 포함 DB |
| 데이터 처리 | Pandas / Polars | ≥2.0 / ≥0.20 | 유니버스 필터링, 수익률 계산 |
| SPEC 참조 | LOCK §14 | - | 기술스택 범위 제약 |

---

## E6. Performance Requirements

| 지표 | 목표 | 허용 한계 | 측정 방법 |
|------|------|-----------|-----------|
| 유니버스 구성 쿼리 | < 100ms | < 500ms | 단일 시점 유니버스 조회 p99 |
| 지수 구성 조회 | < 50ms | < 200ms | 단일 지수/시점 조회 |
| 전체 백테스트 유니버스 (10년) | < 10s | < 30s | 2,520 거래일 유니버스 일괄 구성 |
| 폐지 종목 포함률 | ≥ 95% | ≥ 90% | delisted_included / delisted_count |
| 지수 구성 스냅샷 갱신 | 월 1회 | 분기 1회 | 데이터 신선도 |
| 메모리 사용량 | < 1GB | < 2GB | 전체 유니버스 히스토리 로드 |

---

## E7. Error Handling

| 에러 코드 | 상황 | 처리 방법 | 심각도 |
|-----------|------|-----------|--------|
| `SVB-001` | 폐지 종목 delisting_return 누락 | -100% 보수적 가정 적용, WARNING 로그 | WARNING |
| `SVB-002` | 지수 구성 스냅샷 누락 (특정 월) | 직전 스냅샷 사용, 보간 플래그 | WARNING |
| `SVB-003` | 폐지 종목 가격 히스토리 불완전 | 가용 기간까지만 사용, 누락 기간 로그 | WARNING |
| `SVB-004` | 크립토 디리스팅 API 실패 | 캐시 데이터 사용, 스테일 경고 | WARNING |
| `SVB-005` | 유니버스에 폐지 종목 0건 | 백테스트 중단 → 데이터 소스 점검 필요 | CRITICAL |
| `SVB-006` | 생존편향 영향도 > 0.5 Sharpe | 전략 성과 신뢰도 경고 | CRITICAL |

---

## E8. Test Criteria - Unit / Integration / Acceptance

**Unit Tests**:
- `test_universe_includes_delisted`: 2008년 시점 유니버스에 Lehman Brothers 포함 확인
- `test_index_constituents_historical`: 2010-01 S&P500 구성 ≠ 2024-01 구성 확인
- `test_delisting_return_applied`: 폐지 종목에 -100% 수익률 반영 확인
- `test_crypto_delisting_inclusion`: 디리스팅된 코인이 유니버스에 포함 확인

**Integration Tests**:
- `test_full_backtest_survivorship_free`: 10년 백테스트 전 기간에 걸쳐 폐지 종목 포함 확인
- `test_bias_measurement`: survivors-only vs full universe Sharpe 차이 계산 정확성
- `test_index_reconstitution_replay`: 지수 재구성 이벤트 전후 유니버스 변경 정확

**Acceptance Tests**:
- 폐지 종목 포함률 ≥ 95%
- 생존편향 영향도 보고서 생성 완료
- 5개 주요 위기 기간(2000, 2008, 2011, 2020, 2022) 폐지 종목 모두 포함

---

## E9. LOCK References

| LOCK 항목 | 참조 | 연관 |
|-----------|------|------|
| SPEC §14 | 기술스택 범위 | PostgreSQL, Python 사용 범위 내 |
| SPEC §5 | 백테스트 진실성 | Survivorship Bias 방지 = 핵심 요구사항 |
| B-2 #6 | 상장폐지 종목 포함 | `SurvivorshipBiasGuard.get_universe()` |
| B-2 #7 | 인덱스 히스토리컬 구성 | `SurvivorshipBiasGuard.get_index_constituents()` |
| B-2 #8 | 크립토 디리스팅 반영 | `SurvivorshipBiasGuard.handle_crypto_delisting()` |
| B-2 #9 | 뮤추얼펀드/ETF 생존 편향 | `SurvivorshipBiasGuard.get_fund_universe()` |

---
