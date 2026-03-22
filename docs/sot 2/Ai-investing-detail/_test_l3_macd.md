# MACD Crossover Strategy (L3 Template Test)

> **버전**: v1.0
> **Status**: DRAFT
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-22
> **원본 관점**: #1 실시간 적응형 전략
> **정본 소유 개념**: MACD Crossover 전략 상세
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **LOCK 참조**: `> LOCK (PART2 §6.8): 51% Gate threshold = 0.51`
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9

---

## E1. Input

- **데이터**: `OHLCV_PLUS` from TimescaleDB
- **필수 필드**: `close` (float64), `timestamp` (datetime)
- **선택 필드**: `volume` (int64) — 확인용, MACD 계산 자체에는 미사용
- **전처리**:
  - NaN/Null 행 제거 (forward-fill 후 잔여 NaN drop)
  - 최소 35봉 확보 필수 (EMA26 수렴에 ~26봉 + signal EMA9에 추가 9봉)
  - 타임스탬프 정렬 (ascending)

## E2. Algorithm

```python
# MACD Crossover 의사코드 — 복사 → 구현 가능
def compute_macd(close: pd.Series) -> dict:
    """
    MACD = EMA(close, 12) - EMA(close, 26)
    Signal = EMA(MACD, 9)
    Histogram = MACD - Signal
    """
    # Step 1: Fast EMA (12-period)
    ema_fast = close.ewm(span=12, adjust=False).mean()

    # Step 2: Slow EMA (26-period)
    ema_slow = close.ewm(span=26, adjust=False).mean()

    # Step 3: MACD Line
    macd_line = ema_fast - ema_slow

    # Step 4: Signal Line (9-period EMA of MACD)
    signal_line = macd_line.ewm(span=9, adjust=False).mean()

    # Step 5: Histogram
    histogram = macd_line - signal_line

    return {
        "macd": macd_line,
        "signal": signal_line,
        "histogram": histogram,
    }


def generate_signal(close: pd.Series) -> str:
    """
    Crossover 판정:
    - BUY:  MACD가 Signal을 상향 돌파 (이전봉 MACD < Signal, 현재봉 MACD >= Signal)
    - SELL: MACD가 Signal을 하향 돌파 (이전봉 MACD > Signal, 현재봉 MACD <= Signal)
    - HOLD: 그 외
    """
    result = compute_macd(close)
    macd = result["macd"]
    signal = result["signal"]

    prev_diff = macd.iloc[-2] - signal.iloc[-2]
    curr_diff = macd.iloc[-1] - signal.iloc[-1]

    if prev_diff < 0 and curr_diff >= 0:
        return "BUY"
    elif prev_diff > 0 and curr_diff <= 0:
        return "SELL"
    else:
        return "HOLD"
```

## E3. Output

- **스키마**:
  ```python
  @dataclass
  class Signal:
      symbol: str           # e.g., "005930.KS"
      action: str           # "BUY" | "SELL" | "HOLD"
      confidence: float     # 0.0 ~ 1.0 (histogram 크기 기반)
      timestamp: datetime   # 신호 생성 시각
      metadata: dict        # {"macd": float, "signal": float, "histogram": float}
  ```
- **소비자**: `OrderManager` (주문 생성) / `51% Gate` (신호 검증)

## E4. Class/API Design

```python
from strategies.base import BaseStrategy
from models.signal import Signal

class MACDAdapter(BaseStrategy):
    """MACD Crossover 전략 어댑터.

    SPEC §7 전략 인덱스: MACD Crossover
    구현 우선순위: P0 (V1 대상)
    """

    # LOCK 파라미터 (SPEC §14)
    FAST_PERIOD: int = 12
    SLOW_PERIOD: int = 26
    SIGNAL_PERIOD: int = 9
    MIN_BARS: int = 35

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "MACD_Crossover"

    def validate_input(self, df: pd.DataFrame) -> bool:
        """입력 데이터 유효성 검증.

        Returns:
            True if valid, raises ValueError otherwise.
        """
        if "close" not in df.columns:
            raise ValueError("Missing required column: 'close'")
        if len(df) < self.MIN_BARS:
            raise ValueError(f"Insufficient bars: {len(df)} < {self.MIN_BARS}")
        return True

    def compute(self, df: pd.DataFrame) -> dict:
        """MACD, Signal, Histogram 계산.

        Args:
            df: OHLCV_PLUS DataFrame with 'close' column.

        Returns:
            dict with keys: 'macd', 'signal', 'histogram' (each pd.Series).
        """
        close = df["close"]
        ema_fast = close.ewm(span=self.FAST_PERIOD, adjust=False).mean()
        ema_slow = close.ewm(span=self.SLOW_PERIOD, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.SIGNAL_PERIOD, adjust=False).mean()
        histogram = macd_line - signal_line
        return {"macd": macd_line, "signal": signal_line, "histogram": histogram}

    def generate_signal(self, df: pd.DataFrame) -> Signal:
        """MACD Crossover 기반 매매 신호 생성.

        Args:
            df: OHLCV_PLUS DataFrame (최소 35봉).

        Returns:
            Signal dataclass instance.
        """
        self.validate_input(df)
        result = self.compute(df)
        macd = result["macd"]
        signal = result["signal"]
        histogram = result["histogram"]

        prev_diff = macd.iloc[-2] - signal.iloc[-2]
        curr_diff = macd.iloc[-1] - signal.iloc[-1]

        if prev_diff < 0 and curr_diff >= 0:
            action = "BUY"
        elif prev_diff > 0 and curr_diff <= 0:
            action = "SELL"
        else:
            action = "HOLD"

        # confidence: histogram 크기를 정규화 (0~1)
        hist_abs = abs(histogram.iloc[-1])
        hist_max = histogram.abs().rolling(window=50, min_periods=1).max().iloc[-1]
        confidence = min(hist_abs / hist_max, 1.0) if hist_max > 0 else 0.0

        return Signal(
            symbol=df.attrs.get("symbol", "UNKNOWN"),
            action=action,
            confidence=round(confidence, 4),
            timestamp=df.index[-1],
            metadata={
                "macd": round(float(macd.iloc[-1]), 6),
                "signal": round(float(signal.iloc[-1]), 6),
                "histogram": round(float(histogram.iloc[-1]), 6),
            },
        )
```

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | >= 2.0 | Yes | DataFrame, EWM 계산 |
| numpy | >= 1.24 | Yes | 수치 연산 보조 |
| ta-lib | >= 0.4.28 | Yes | 검증용 크로스체크 (선택적) |

## E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 단일 심볼 지연 | < 50ms | `time.perf_counter()` 래핑, 1000봉 기준 |
| 배치 100 심볼 | < 5s | 순차 처리 기준 (병렬 시 < 2s) |
| 메모리 | < 10MB / 심볼 | `tracemalloc` 프로파일링 |

## E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| `close` 컬럼 누락 | `ValueError` raise, 신호 미생성 | CRITICAL |
| NaN 존재 (close 내) | `ffill()` → 잔여 NaN `dropna()` | WARNING |
| 최소 봉수 미달 (< 35) | `ValueError` raise, SKIP 처리 | HIGH |
| EMA 초기값 불안정 (첫 26봉) | 자연 수렴 허용 — 35봉 최소 보장으로 해결 | LOW |
| 0 나눗기 (confidence 계산) | `hist_max == 0` 분기 → confidence = 0.0 | LOW |
| 타임스탬프 미정렬 | `sort_index()` 자동 적용 | WARNING |

## E8. Test Criteria

- **Unit**:
  - MACD 계산 검증: 알려진 종가 시퀀스 [44, 44.34, 44.09, 43.61, 44.33, 44.83, 45.10, 45.42, 45.84, ...] 대비 MACD 값이 소수점 4자리까지 일치
  - EMA 계산 검증: `pandas.ewm` 결과 vs 수동 Wilder 방식 비교
  - Crossover 판정: BUY/SELL/HOLD 각 케이스별 known-answer 테스트
  - Edge case: 정확히 35봉, NaN 포함 입력, 빈 DataFrame
- **Integration**:
  - 51% Gate 통과: MACD 신호 → 51% Gate 검증 파이프라인 연결 테스트
  - `Signal` 객체가 `OrderManager`에 정상 전달되는지 확인
  - TimescaleDB에서 실시간 데이터 fetch → MACD 계산 → Signal 생성 E2E
- **Acceptance**:
  - 51% Gate 통과율: 백테스트 기간 (2020-2024) 전 종목 대상 BUY 신호 승률 >= 51%
  - 성능: 100 심볼 배치 < 5s 확인

## E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 51% Gate threshold = 0.51 | SPEC §6.1 | 신호 confidence >= 0.51이어야 OrderManager에 전달 |
| Circuit Breaker -3% | SPEC §10.2 | 일일 손실 -3% 도달 시 MACD 신호 무시 (전략 비활성화) |
| EMA 기간 (12, 26, 9) | SPEC §14 (기술스택 LOCK) | 파라미터 변경 불가 — LOCK 해제 절차 필요 |

---

> **L3 판정**: 9요소 전수 기재 완료 (E1~E9). L3 PASS 기준 충족.
> **검증일**: 2026-03-22