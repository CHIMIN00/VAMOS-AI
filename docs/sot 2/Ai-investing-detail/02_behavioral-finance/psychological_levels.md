# 심리적 가격 수준 분석 (Psychological Price Levels)
> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #2 투자 심리학 & 행동재무학
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-7. 심리적 가격 수준 분석 (Psychological Price Levels)

**현재**: 완전히 없음
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 29 | **라운드 넘버(Round Number) 효과 분석** | $100, $50, ₩50,000 등 심리적 가격대에서의 지지/저항 강화 효과. 주문 장부에서 라운드 넘버 근처 주문 집중도 분석 |
| 30 | **역사적 고점/저점 심리 효과** | 52주 신고가/신저가, 전고점, IPO 가격 등 심리적 기준점. 전고점 돌파 시 "심리적 저항 해소 → 추가 상승 가능성" 분석 |
| 31 | **갭(Gap) 심리 분석** | 갭 상승/하락 후 투자자 심리 변화. "갭 메우기" 심리(Gap Fill) 확률 통계 + 갭 이후 추세 지속/반전 패턴 |

---

## E1. Input

### 데이터 스키마

```yaml
price_ohlcv:
  ticker: str                 # 종목 코드, 필수
  date: date                  # 거래일, 필수
  open: float                 # 시가, 필수
  high: float                 # 고가, 필수
  low: float                  # 저가, 필수
  close: float                # 종가, 필수
  volume: int                 # 거래량, 필수

orderbook_snapshot:
  ticker: str                 # 종목 코드, 필수
  timestamp: datetime         # 스냅샷 시각, 필수
  bids: list[tuple[float, int]]  # (가격, 수량) 매수 호가, 필수
  asks: list[tuple[float, int]]  # (가격, 수량) 매도 호가, 필수

historical_extremes:
  ticker: str                 # 종목 코드, 필수
  high_52w: float             # 52주 최고가, 필수
  low_52w: float              # 52주 최저가, 필수
  all_time_high: float        # 역대 최고가, 필수
  all_time_low: float         # 역대 최저가, 필수
  ipo_price: float | None     # IPO 가격, 선택
  previous_peaks: list[float] # 주요 전고점 리스트, 선택
  previous_troughs: list[float] # 주요 전저점 리스트, 선택

currency_info:
  ticker: str                 # 종목 코드, 필수
  currency: str               # "USD" | "KRW" | "EUR" 등, 필수
  price_unit: float           # 최소 호가 단위, 필수
```

### 필수 필드
- `price_ohlcv`: ticker, date, open, high, low, close, volume
- `historical_extremes`: ticker, high_52w, low_52w, all_time_high, all_time_low

### 전처리
1. OHLCV 데이터 결측 제거: 거래 정지일 필터링
2. 수정주가(adjusted close) 변환: 액면분할/배당 조정
3. 통화별 라운드 넘버 단위 자동 결정 (USD: $10/$50/$100, KRW: ₩1000/₩5000/₩50000)
4. 과거 52주 고/저 rolling 계산

---

## E2. Algorithm

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class RoundNumberLevel:
    ticker: str
    price_level: float        # 라운드 넘버 가격
    level_type: str           # "support" | "resistance"
    distance_pct: float       # 현재가 대비 거리 %
    order_concentration: float  # 주문 집중도 0.0~1.0
    historical_touch_count: int  # 과거 접근 횟수
    historical_bounce_rate: float  # 반등/반락 비율 0.0~1.0
    strength: float           # 종합 강도 0.0~1.0


@dataclass
class HistoricalLevelEffect:
    ticker: str
    level_type: str           # "52w_high" | "52w_low" | "all_time_high" | "previous_peak" | "ipo_price"
    price_level: float
    current_price: float
    distance_pct: float
    proximity_zone: bool      # 현재가가 ±2% 이내
    breakout_probability: float  # 돌파 확률 0.0~1.0 (과거 통계 기반)
    post_breakout_avg_move: float  # 돌파 후 평균 이동률 %
    signal: str               # "approaching_resistance" | "breakout" | "support_test" | "neutral"


@dataclass
class GapAnalysis:
    ticker: str
    gap_date: date
    gap_type: str             # "up" | "down"
    gap_start: float          # 갭 시작 가격 (전일 종가 or 당일 시가)
    gap_end: float            # 갭 끝 가격
    gap_size_pct: float       # 갭 크기 %
    is_filled: bool           # 갭 메워졌는지
    fill_days: int | None     # 갭 메워지기까지 일수
    fill_probability: float   # 유사 갭 메우기 확률
    post_gap_trend: str       # "continuation" | "reversal" | "neutral"
    post_gap_5d_return: float # 갭 후 5일 수익률


class PsychologicalLevelAnalyzer:
    """#29~31: 심리적 가격 수준 분석 통합 클래스"""

    PROXIMITY_PCT: float = 2.0         # 가격 근접 판단 ±2%
    ROUND_NUMBER_UNITS: dict = {
        "USD": [10, 25, 50, 100, 250, 500, 1000],
        "KRW": [1000, 5000, 10000, 50000, 100000],
        "EUR": [10, 25, 50, 100, 250, 500],
    }
    GAP_MIN_PCT: float = 0.5          # 갭 최소 크기 %
    LOOKBACK_DAYS: int = 252          # 1년 영업일

    def __init__(self):
        pass

    # ── #29 라운드 넘버 효과 분석 ──────────────────────────
    def analyze_round_numbers(
        self,
        ticker: str,
        current_price: float,
        currency: str,
        ohlcv: pd.DataFrame,
        orderbook: Optional[dict] = None
    ) -> list[RoundNumberLevel]:
        """심리적 가격대 지지/저항 효과 분석"""
        units = self.ROUND_NUMBER_UNITS.get(currency, self.ROUND_NUMBER_UNITS["USD"])
        levels: list[RoundNumberLevel] = []

        for unit in units:
            # 현재가 근처 라운드 넘버 찾기
            lower = (current_price // unit) * unit
            upper = lower + unit

            for price_level in [lower, upper]:
                if price_level <= 0:
                    continue

                distance_pct = ((price_level - current_price) / current_price) * 100.0

                # ±10% 범위 내만 분석
                if abs(distance_pct) > 10.0:
                    continue

                # 과거 접근 횟수 및 반등률
                touch_count, bounce_rate = self._calc_historical_touches(
                    ohlcv, price_level, tolerance_pct=0.5
                )

                # 주문장 집중도
                order_concentration = 0.5  # 기본값
                if orderbook:
                    order_concentration = self._calc_order_concentration(
                        orderbook, price_level, tolerance_pct=0.5
                    )

                # 종합 강도: 접근횟수 × 반등률 × 주문집중도
                strength = float(np.clip(
                    (min(touch_count, 10) / 10.0) * 0.4 +
                    bounce_rate * 0.3 +
                    order_concentration * 0.3,
                    0.0, 1.0
                ))

                level_type = "support" if price_level < current_price else "resistance"

                levels.append(RoundNumberLevel(
                    ticker=ticker,
                    price_level=price_level,
                    level_type=level_type,
                    distance_pct=float(distance_pct),
                    order_concentration=order_concentration,
                    historical_touch_count=touch_count,
                    historical_bounce_rate=bounce_rate,
                    strength=strength
                ))

        # 강도 내림차순 정렬
        return sorted(levels, key=lambda l: l.strength, reverse=True)

    # ── #30 역사적 고점/저점 심리 효과 ────────────────────
    def analyze_historical_levels(
        self,
        ticker: str,
        current_price: float,
        extremes: dict,
        ohlcv: pd.DataFrame
    ) -> list[HistoricalLevelEffect]:
        """52주 고/저, 전고점, IPO 가격 등 심리적 기준점 분석"""
        results: list[HistoricalLevelEffect] = []

        level_definitions = [
            ("52w_high", extremes["high_52w"]),
            ("52w_low", extremes["low_52w"]),
            ("all_time_high", extremes["all_time_high"]),
        ]
        if extremes.get("ipo_price"):
            level_definitions.append(("ipo_price", extremes["ipo_price"]))
        for i, peak in enumerate(extremes.get("previous_peaks", [])):
            level_definitions.append((f"previous_peak_{i}", peak))

        for level_type, price_level in level_definitions:
            distance_pct = ((current_price - price_level) / price_level) * 100.0
            proximity_zone = abs(distance_pct) <= self.PROXIMITY_PCT

            # 돌파 확률: 과거 유사 접근 시 돌파 빈도
            breakout_prob, post_breakout_move = self._calc_breakout_stats(
                ohlcv, price_level
            )

            # 시그널 결정
            if distance_pct > self.PROXIMITY_PCT:
                signal = "breakout" if "high" in level_type or "peak" in level_type else "neutral"
            elif distance_pct < -self.PROXIMITY_PCT:
                signal = "neutral"
            else:
                if "high" in level_type or "peak" in level_type:
                    signal = "approaching_resistance"
                else:
                    signal = "support_test"

            results.append(HistoricalLevelEffect(
                ticker=ticker,
                level_type=level_type.split("_")[0] if "_" in level_type else level_type,
                price_level=price_level,
                current_price=current_price,
                distance_pct=float(distance_pct),
                proximity_zone=proximity_zone,
                breakout_probability=breakout_prob,
                post_breakout_avg_move=post_breakout_move,
                signal=signal
            ))

        return results

    # ── #31 갭 심리 분석 ──────────────────────────────────
    def analyze_gaps(
        self,
        ticker: str,
        ohlcv: pd.DataFrame,
        lookback_days: int = 252
    ) -> list[GapAnalysis]:
        """갭 상승/하락 감지, Gap Fill 확률, 갭 후 추세 분석"""
        df = ohlcv.sort_values("date").tail(lookback_days).copy()
        if len(df) < 2:
            return []

        gaps: list[GapAnalysis] = []
        df = df.reset_index(drop=True)

        for i in range(1, len(df)):
            prev_close = df.iloc[i - 1]["close"]
            curr_open = df.iloc[i]["open"]

            gap_pct = ((curr_open - prev_close) / prev_close) * 100.0

            if abs(gap_pct) < self.GAP_MIN_PCT:
                continue

            gap_type = "up" if gap_pct > 0 else "down"
            gap_start = prev_close
            gap_end = curr_open
            gap_date = df.iloc[i]["date"]

            # 갭 메우기 확인
            is_filled = False
            fill_days: Optional[int] = None
            future = df.iloc[i:]
            for j, row in future.iterrows():
                if gap_type == "up" and row["low"] <= gap_start:
                    is_filled = True
                    fill_days = int(j - i)
                    break
                elif gap_type == "down" and row["high"] >= gap_start:
                    is_filled = True
                    fill_days = int(j - i)
                    break

            # 갭 후 5일 수익률
            if i + 5 < len(df):
                post_5d_return = ((df.iloc[i + 5]["close"] - curr_open) / curr_open) * 100.0
            else:
                post_5d_return = 0.0

            # 추세 판단: 갭 방향과 5일 수익률 방향 일치 여부
            if abs(post_5d_return) < 0.5:
                post_gap_trend = "neutral"
            elif (gap_type == "up" and post_5d_return > 0) or (gap_type == "down" and post_5d_return < 0):
                post_gap_trend = "continuation"
            else:
                post_gap_trend = "reversal"

            gaps.append(GapAnalysis(
                ticker=ticker,
                gap_date=gap_date,
                gap_type=gap_type,
                gap_start=gap_start,
                gap_end=gap_end,
                gap_size_pct=float(abs(gap_pct)),
                is_filled=is_filled,
                fill_days=fill_days,
                fill_probability=0.0,  # 아래에서 통계적으로 계산
                post_gap_trend=post_gap_trend,
                post_gap_5d_return=float(post_5d_return)
            ))

        # Gap Fill 확률: 동일 방향/크기 갭의 과거 메우기 비율
        if gaps:
            for k, gap in enumerate(gaps):
                prior_same_type = [g for g in gaps[:k] if g.gap_type == gap.gap_type]
                filled = [g for g in prior_same_type if g.is_filled]
                gap.fill_probability = len(filled) / len(prior_same_type) if prior_same_type else 0.0

        return gaps

    # ── 내부 헬퍼 ──────────────────────────────────────
    def _calc_historical_touches(
        self,
        ohlcv: pd.DataFrame,
        price_level: float,
        tolerance_pct: float = 0.5
    ) -> tuple[int, float]:
        """과거 가격이 특정 레벨에 접근한 횟수 및 반등률"""
        tol = price_level * (tolerance_pct / 100.0)
        touches = ohlcv[
            (ohlcv["low"] <= price_level + tol) &
            (ohlcv["high"] >= price_level - tol)
        ]
        touch_count = len(touches)
        if touch_count == 0:
            return 0, 0.0

        # 반등: 접근 후 다음 날 종가가 레벨 반대편으로 이동
        bounce_count = 0
        for idx in touches.index:
            next_idx = idx + 1
            if next_idx in ohlcv.index:
                next_close = ohlcv.loc[next_idx, "close"]
                if ohlcv.loc[idx, "close"] < price_level and next_close > price_level:
                    bounce_count += 1
                elif ohlcv.loc[idx, "close"] > price_level and next_close < price_level:
                    bounce_count += 1

        bounce_rate = bounce_count / touch_count
        return touch_count, float(bounce_rate)

    def _calc_order_concentration(
        self,
        orderbook: dict,
        price_level: float,
        tolerance_pct: float = 0.5
    ) -> float:
        """주문장에서 특정 가격 근처 주문 집중도"""
        tol = price_level * (tolerance_pct / 100.0)
        total_volume = 0
        level_volume = 0

        for price, qty in orderbook.get("bids", []) + orderbook.get("asks", []):
            total_volume += qty
            if abs(price - price_level) <= tol:
                level_volume += qty

        return level_volume / total_volume if total_volume > 0 else 0.0

    def _calc_breakout_stats(
        self,
        ohlcv: pd.DataFrame,
        price_level: float
    ) -> tuple[float, float]:
        """특정 가격 레벨 돌파 확률 및 돌파 후 평균 이동률"""
        tol = price_level * (self.PROXIMITY_PCT / 100.0)

        approaches = ohlcv[
            (ohlcv["high"] >= price_level - tol) &
            (ohlcv["low"] <= price_level + tol)
        ]
        if len(approaches) == 0:
            return 0.5, 0.0  # 기본값

        breakout_count = 0
        breakout_moves: list[float] = []

        for idx in approaches.index:
            # 접근 후 5일 내 돌파 확인
            future = ohlcv.loc[idx + 1:idx + 5] if idx + 5 in ohlcv.index else ohlcv.loc[idx + 1:]
            if not future.empty and future["close"].iloc[-1] > price_level + tol:
                breakout_count += 1
                move_pct = ((future["close"].iloc[-1] - price_level) / price_level) * 100.0
                breakout_moves.append(move_pct)

        breakout_prob = breakout_count / len(approaches)
        avg_move = float(np.mean(breakout_moves)) if breakout_moves else 0.0

        return float(breakout_prob), avg_move
```

---

## E3. Output

### 출력 스키마

```yaml
round_number_output:
  ticker: str
  price_level: float
  level_type: str             # "support" | "resistance"
  distance_pct: float
  order_concentration: float
  historical_touch_count: int
  historical_bounce_rate: float
  strength: float             # 0.0 ~ 1.0
  confidence: float           # touch_count 기반

historical_level_output:
  ticker: str
  level_type: str
  price_level: float
  current_price: float
  distance_pct: float
  proximity_zone: bool
  breakout_probability: float
  post_breakout_avg_move: float
  signal: str
  confidence: float           # approach_count 기반

gap_analysis_output:
  ticker: str
  gap_date: date
  gap_type: str               # "up" | "down"
  gap_size_pct: float
  is_filled: bool
  fill_days: int | null
  fill_probability: float     # 0.0 ~ 1.0
  post_gap_trend: str         # "continuation" | "reversal" | "neutral"
  post_gap_5d_return: float
  confidence: float           # 동일 유형 갭 샘플 수 기반
```

### Confidence 산출
- **라운드 넘버**: min(1.0, historical_touch_count / 20)
- **역사적 고/저**: min(1.0, approach_count / 15)
- **갭 분석**: min(1.0, same_type_gap_count / 10)

### 소비자
- `03_portfolio-strategy`: 진입/청산 가격 결정 보조
- `04_technical-analysis`: 지지/저항 레벨 통합
- Kafka topic: `vamos.psych.round_number`, `vamos.psych.historical_level`, `vamos.psych.gap`

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod


class BasePriceLevelAnalyzer(ABC):
    """가격 수준 분석 기반 클래스"""

    @abstractmethod
    def analyze(self, ticker: str, data: dict) -> dict:
        ...

    @abstractmethod
    def get_confidence(self) -> float:
        ...


class PsychologicalLevelAnalyzer(BasePriceLevelAnalyzer):
    """
    #29~31 통합 클래스
    Inherits: BasePriceLevelAnalyzer

    Public Methods:
        analyze_round_numbers(ticker: str, current_price: float, currency: str, ohlcv: pd.DataFrame, orderbook: Optional[dict]) -> list[RoundNumberLevel]
        analyze_historical_levels(ticker: str, current_price: float, extremes: dict, ohlcv: pd.DataFrame) -> list[HistoricalLevelEffect]
        analyze_gaps(ticker: str, ohlcv: pd.DataFrame, lookback_days: int = 252) -> list[GapAnalysis]
        analyze(ticker: str, data: dict) -> dict   # 통합 진입점
        get_confidence() -> float

    Kafka Produce:
        vamos.psych.round_number
        vamos.psych.historical_level
        vamos.psych.gap

    Kafka Consume:
        vamos.market.ohlcv
        vamos.market.orderbook
        vamos.market.extremes
    """
    pass
```

---

## E5. Tech Stack Dependency

| 구분 | 기술 | 용도 | SPEC §14 LOCK |
|------|------|------|---------------|
| 메시징 | **Kafka** | 가격 데이터 수신, 분석 결과 발행 | ☑ LOCKED |
| 시계열DB | **TimescaleDB** | OHLCV 시계열, 분석 결과 저장 | ☑ LOCKED |
| 데이터 처리 | **pandas** | OHLCV DataFrame, 갭 탐색 | ☑ LOCKED |
| 수치 연산 | **numpy** | 통계 연산, 강도 계산 | ☑ LOCKED |
| ML | **scikit-learn** | 향후 라운드넘버 효과 ML 모델 확장용 | ☑ LOCKED |

---

## E6. Performance Requirements

| 지표 | 목표 | 비고 |
|------|------|------|
| 라운드 넘버 분석 (단일 종목) | ≤ 200ms | 실시간 |
| 역사적 고/저 분석 | ≤ 300ms | 1년 OHLCV 기준 |
| 갭 분석 (1년 데이터) | ≤ 500ms | 일 1회 배치 허용 |
| 주문장 집중도 계산 | ≤ 50ms | 실시간 호가 변경 |
| TimescaleDB 조회 | ≤ 100ms | 인덱스 ticker + date |
| 전 종목 배치 분석 (500종목) | ≤ 5min | 장 시작 전 사전 계산 |

---

## E7. Error Handling

| 오류 상황 | 처리 방식 | Fallback |
|-----------|-----------|----------|
| OHLCV 데이터 부족 (< 20일) | 분석 스킵, 로그 WARNING | confidence=0 반환 |
| 주문장 데이터 없음 | order_concentration=0.5 기본값 | 과거 데이터만 사용 |
| 52주 고/저 계산 오류 | rolling 재계산 | 캐시된 이전 값 사용 |
| 통화 미지원 | USD 단위 기본 적용 | 로그 WARNING |
| 갭 계산 시 0 나눗기 | prev_close=0 건 필터 | 해당 갭 스킵 |
| Kafka 발행 실패 | DLQ 전송, 3회 재시도 | 로컬 파일 버퍼 |

---

## E8. Test Criteria

### Unit Tests
- [ ] `analyze_round_numbers`: USD $100 근처 → $100 레벨 포함 확인
- [ ] `analyze_round_numbers`: KRW ₩50,000 근처 → ₩50,000 레벨 포함 확인
- [ ] `analyze_round_numbers`: 접근 횟수 높을수록 strength 증가 확인
- [ ] `analyze_historical_levels`: 52주 신고가 ±2% 내 → proximity_zone=True
- [ ] `analyze_historical_levels`: 전고점 돌파 → signal="breakout" 확인
- [ ] `analyze_gaps`: 갭 크기 ≥ 0.5% 감지 확인
- [ ] `analyze_gaps`: 갭 메우기 완료 → is_filled=True, fill_days 정확
- [ ] `analyze_gaps`: fill_probability 범위 0.0~1.0 확인
- [ ] `_calc_historical_touches`: 빈 OHLCV → (0, 0.0) 반환

### Integration Tests
- [ ] TimescaleDB OHLCV 조회 → 라운드 넘버 분석 → 결과 저장 E2E
- [ ] Kafka `vamos.market.ohlcv` 수신 → 갭 분석 → `vamos.psych.gap` 발행
- [ ] 주문장 실시간 스냅샷 → 집중도 업데이트

### Acceptance Tests
- [ ] S&P 500 종목 대상 라운드 넘버 레벨 vs 실제 지지/저항 일치율 ≥ 60%
- [ ] 52주 신고가 돌파 후 5일 추가 상승 확률 통계 검증
- [ ] 갭 메우기 확률: 과거 1년 갭 대상 fill_probability vs 실제 메우기 비율 오차 < 10%

---

## E9. LOCK References

| SPEC 참조 | 내용 |
|-----------|------|
| SPEC §14 | 기술스택 LOCK (Kafka, TimescaleDB, pandas, numpy, scikit-learn) |
| B-5 연동 | 뉴스 심리 임팩트 → 갭 발생 원인 분석 참조 |
| 04_technical-analysis | 기술적 지지/저항 레벨과 심리적 레벨 교차 검증 |

---

## L3 판정

| 항목 | 상태 |
|------|------|
| E1. Input 스키마 정의 | ☑ 완료 |
| E2. Algorithm pseudocode | ☑ 완료 |
| E3. Output 스키마 + confidence | ☑ 완료 |
| E4. Class/API 설계 | ☑ 완료 |
| E5. Tech Stack LOCK 준수 | ☑ 완료 |
| E6. 성능 요구사항 | ☑ 완료 |
| E7. 오류 처리 | ☑ 완료 |
| E8. 테스트 기준 | ☑ 완료 |
| E9. LOCK References | ☑ 완료 |
| **L3 판정** | **APPROVED** |
