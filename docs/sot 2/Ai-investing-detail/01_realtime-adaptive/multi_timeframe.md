# 멀티 타임프레임(MTF) 통합 분석
> **버전**: v1.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #1 실시간 적응형 전략
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9

---

### B-6. 멀티 타임프레임(MTF) 통합 분석

**현재**: Z-Session에서 15m/1h/4h/1d 분산 실행만 있고, 시간대 간 통합 분석은 없음
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 20 | **상위-하위 타임프레임 정합성 검증** | "일봉은 상승 추세인데 5분봉에서 매도 시그널" → 상위 추세 우선 원칙 적용 |
| 21 | **MTF Confluence 시그널** | 일봉 지지 + 4시간봉 RSI 과매도 + 1시간봉 거래량 급증 = 강한 매수 시그널. 단일 시간대만 보는 게 아닌 다중 시간대 합의 |
| 22 | **진입 시간대 vs 관리 시간대 분리** | 일봉으로 방향 판단 → 4시간봉으로 구간 설정 → 15분봉으로 정밀 진입 (Top-Down 분석) |
| 23 | **코인 24/7 특화** | 코인은 장 마감이 없으므로 4시간/8시간/일봉의 의미가 주식과 다름. UTC 기준 봉 형성 시점에 따른 매물대 차이 |

---

## E1. Input

- **데이터**: `OHLCV_PLUS` from TimescaleDB (다중 타임프레임 동시 조회)
- **필수 필드**:
  - `close` (float64) — 종가
  - `high` (float64) — 고가
  - `low` (float64) — 저가
  - `open` (float64) — 시가
  - `volume` (int64) — 거래량
  - `timestamp` (datetime) — 봉 시각
  - `timeframe` (str) — "1m" | "5m" | "15m" | "1h" | "4h" | "8h" | "1d"
- **선택 필드**: `rsi` (float64), `ema_20` (float64), `ema_50` (float64) — 사전 계산 지표
- **전처리**:
  - NaN/Null: forward-fill 후 잔여 NaN drop
  - 각 타임프레임별 최소 봉 수: 1d=60봉, 4h=120봉, 1h=240봉, 15m=480봉
  - 타임스탬프 정렬 ascending + 타임프레임별 그룹 분리
  - 코인 시장: UTC 00:00 기준 일봉 정렬 (거래소별 차이 보정)

## E2. Algorithm

```python
# 멀티 타임프레임 통합 분석 의사코드 — 복사 → 구현 가능
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class TrendDirection(Enum):
    STRONG_UP = "STRONG_UP"
    UP = "UP"
    NEUTRAL = "NEUTRAL"
    DOWN = "DOWN"
    STRONG_DOWN = "STRONG_DOWN"

class MarketType(Enum):
    STOCK_KR = "STOCK_KR"    # 한국 주식 (09:00-15:30 KST)
    STOCK_US = "STOCK_US"    # 미국 주식 (09:30-16:00 EST)
    CRYPTO = "CRYPTO"        # 코인 24/7

TIMEFRAME_HIERARCHY: dict[MarketType, list[str]] = {
    MarketType.STOCK_KR: ["1d", "4h", "1h", "15m", "5m"],
    MarketType.STOCK_US: ["1d", "4h", "1h", "15m", "5m"],
    MarketType.CRYPTO: ["1d", "8h", "4h", "1h", "15m", "5m", "1m"],
}


# --- #20: 상위-하위 타임프레임 정합성 검증 ---
def check_timeframe_alignment(
    tf_data: dict[str, pd.DataFrame],
    market_type: MarketType,
) -> dict:
    """
    상위 TF 추세 vs 하위 TF 시그널 정합성 검증.
    상위 추세와 일치하는 하위 시그널만 유효 처리.
    """
    hierarchy = TIMEFRAME_HIERARCHY[market_type]
    trends: dict[str, TrendDirection] = {}

    for tf in hierarchy:
        if tf not in tf_data:
            continue
        df = tf_data[tf]
        ema_20 = df["close"].ewm(span=20, adjust=False).mean()
        ema_50 = df["close"].ewm(span=50, adjust=False).mean()
        rsi = _compute_rsi(df["close"], period=14)

        current_close = df["close"].iloc[-1]
        if current_close > ema_20.iloc[-1] > ema_50.iloc[-1] and rsi.iloc[-1] > 60:
            trends[tf] = TrendDirection.STRONG_UP
        elif current_close > ema_50.iloc[-1]:
            trends[tf] = TrendDirection.UP
        elif current_close < ema_20.iloc[-1] < ema_50.iloc[-1] and rsi.iloc[-1] < 40:
            trends[tf] = TrendDirection.STRONG_DOWN
        elif current_close < ema_50.iloc[-1]:
            trends[tf] = TrendDirection.DOWN
        else:
            trends[tf] = TrendDirection.NEUTRAL

    # 정합성 판정: 상위 2개 TF 추세 방향 일치 여부
    upper_tfs = [tf for tf in hierarchy[:2] if tf in trends]
    upper_direction = trends.get(upper_tfs[0]) if upper_tfs else TrendDirection.NEUTRAL

    alignment_score = 0.0
    directional = [tf for tf in trends if trends[tf] != TrendDirection.NEUTRAL]
    for tf in directional:
        a = trends[tf]
        b = upper_direction
        if (a in {TrendDirection.STRONG_UP, TrendDirection.UP} and b in {TrendDirection.STRONG_UP, TrendDirection.UP}) or \
           (a in {TrendDirection.STRONG_DOWN, TrendDirection.DOWN} and b in {TrendDirection.STRONG_DOWN, TrendDirection.DOWN}):
            alignment_score += 1.0
    alignment_score /= max(len(directional), 1)

    return {
        "trends": {tf: t.value for tf, t in trends.items()},
        "upper_trend": upper_direction.value,
        "alignment_score": round(alignment_score, 4),
        "is_aligned": alignment_score >= 0.6,
        "conflict_tfs": [
            tf for tf, t in trends.items()
            if not _same_direction(t, upper_direction)
        ],
    }


def _compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(window=period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100.0 - (100.0 / (1.0 + rs))


def _same_direction(a: TrendDirection, b: TrendDirection) -> bool:
    up_set = {TrendDirection.STRONG_UP, TrendDirection.UP}
    down_set = {TrendDirection.STRONG_DOWN, TrendDirection.DOWN}
    return (a in up_set and b in up_set) or (a in down_set and b in down_set) or (
        a == TrendDirection.NEUTRAL or b == TrendDirection.NEUTRAL
    )


# --- #21: MTF Confluence 시그널 ---
def compute_mtf_confluence(
    tf_data: dict[str, pd.DataFrame],
    market_type: MarketType,
) -> dict:
    """
    다중 시간대 합의 시그널.
    각 TF별 개별 시그널을 가중 합산하여 최종 confluence score 산출.
    """
    hierarchy = TIMEFRAME_HIERARCHY[market_type]

    # TF별 가중치 (상위 TF일수록 높음)
    weights = {}
    for i, tf in enumerate(hierarchy):
        weights[tf] = 1.0 / (i + 1)  # 1d=1.0, 4h=0.5, 1h=0.33, ...

    signals: list[dict] = []
    total_weight = 0.0
    weighted_score = 0.0  # -1.0 ~ +1.0 scale

    for tf in hierarchy:
        if tf not in tf_data:
            continue
        df = tf_data[tf]
        sig = _analyze_single_tf(df)
        sig["timeframe"] = tf
        sig["weight"] = weights[tf]
        signals.append(sig)

        # score: BUY=+1, SELL=-1, HOLD=0, 강도 반영
        score = sig["direction_score"] * sig["strength"]
        weighted_score += score * weights[tf]
        total_weight += weights[tf]

    confluence_score = weighted_score / total_weight if total_weight > 0 else 0.0

    if confluence_score > 0.5:
        action = "STRONG_BUY"
    elif confluence_score > 0.2:
        action = "BUY"
    elif confluence_score < -0.5:
        action = "STRONG_SELL"
    elif confluence_score < -0.2:
        action = "SELL"
    else:
        action = "HOLD"

    return {
        "action": action,
        "confluence_score": round(confluence_score, 4),
        "confidence": round(abs(confluence_score), 4),
        "tf_signals": signals,
        "agreeing_tfs": sum(
            1 for s in signals
            if (s["direction_score"] > 0) == (confluence_score > 0)
        ),
        "total_tfs": len(signals),
    }


def _analyze_single_tf(df: pd.DataFrame) -> dict:
    """개별 타임프레임 시그널 분석 (RSI + EMA crossover + volume)."""
    close = df["close"]
    rsi = _compute_rsi(close, 14)
    ema_fast = close.ewm(span=20, adjust=False).mean()
    ema_slow = close.ewm(span=50, adjust=False).mean()
    vol_ratio = df["volume"].iloc[-1] / df["volume"].rolling(20).mean().iloc[-1]

    # 방향 점수
    if ema_fast.iloc[-1] > ema_slow.iloc[-1]:
        direction_score = 1.0
    elif ema_fast.iloc[-1] < ema_slow.iloc[-1]:
        direction_score = -1.0
    else:
        direction_score = 0.0

    # RSI 과매수/과매도 보정
    if rsi.iloc[-1] > 70:
        direction_score *= 0.5   # 과매수 → 매수 신뢰도 감소
    elif rsi.iloc[-1] < 30:
        direction_score *= 0.5   # 과매도 → 매도 신뢰도 감소

    # 강도: volume spike 반영
    strength = min(vol_ratio / 2.0, 1.0) if vol_ratio > 0 else 0.5

    return {
        "direction_score": direction_score,
        "strength": round(strength, 4),
        "rsi": round(float(rsi.iloc[-1]), 2),
        "ema_cross": "BULLISH" if direction_score > 0 else "BEARISH",
        "volume_spike": vol_ratio > 2.0,
    }


# --- #22: 진입 시간대 vs 관리 시간대 분리 (Top-Down) ---
def top_down_analysis(
    tf_data: dict[str, pd.DataFrame],
    market_type: MarketType,
) -> dict:
    """
    Top-Down 분석: 일봉(방향) → 4시간봉(구간) → 15분봉(진입).
    각 단계별 역할을 분리하여 계층적 의사결정.
    """
    hierarchy = TIMEFRAME_HIERARCHY[market_type]

    # 역할 매핑: direction(방향) → zone(구간) → entry(진입)
    role_map = {
        "direction": hierarchy[0],   # 1d
        "zone": hierarchy[1] if len(hierarchy) > 1 else hierarchy[0],  # 4h
        "entry": hierarchy[3] if len(hierarchy) > 3 else hierarchy[-1],  # 15m
    }

    # Step 1: 방향 판단 (일봉)
    dir_df = tf_data.get(role_map["direction"])
    if dir_df is None or dir_df.empty:
        return {"error": f"Missing direction TF: {role_map['direction']}"}

    direction_trend = _get_trend(dir_df)

    # Step 2: 구간 설정 (4시간봉) — 지지/저항 구간
    zone_df = tf_data.get(role_map["zone"])
    support, resistance = _find_sr_levels(zone_df) if zone_df is not None else (0, 0)

    # Step 3: 진입 타이밍 (15분봉) — 정밀 엔트리
    entry_df = tf_data.get(role_map["entry"])
    entry_signal = _analyze_single_tf(entry_df) if entry_df is not None else None

    # 정합성: 방향과 진입이 일치해야 유효
    is_valid = (
        entry_signal is not None
        and (
            (direction_trend == "UP" and entry_signal["direction_score"] > 0)
            or (direction_trend == "DOWN" and entry_signal["direction_score"] < 0)
        )
    )

    return {
        "direction_tf": role_map["direction"],
        "direction_trend": direction_trend,
        "zone_tf": role_map["zone"],
        "support": support,
        "resistance": resistance,
        "entry_tf": role_map["entry"],
        "entry_signal": entry_signal,
        "is_valid_entry": is_valid,
        "management_tf": role_map["zone"],  # 관리는 zone TF에서
    }


def _get_trend(df: pd.DataFrame) -> str:
    ema50 = df["close"].ewm(span=50, adjust=False).mean()
    return "UP" if df["close"].iloc[-1] > ema50.iloc[-1] else "DOWN"


def _find_sr_levels(df: pd.DataFrame) -> tuple[float, float]:
    """최근 고가/저가 기반 간이 지지/저항."""
    recent = df.tail(60)
    support = recent["low"].rolling(20).min().iloc[-1]
    resistance = recent["high"].rolling(20).max().iloc[-1]
    return float(support), float(resistance)


# --- #23: 코인 24/7 특화 ---
def adjust_crypto_timeframes(
    tf_data: dict[str, pd.DataFrame],
    utc_candle_base: str = "00:00",
) -> dict[str, pd.DataFrame]:
    """
    코인 24/7 봉 보정.
    - UTC 00:00 기준 일봉 정렬
    - 8시간봉 추가 (주식에는 없는 TF)
    - 거래소별 봉 시작 시간 차이 보정
    """
    adjusted = {}
    for tf, df in tf_data.items():
        df = df.copy()
        # UTC 기준 정렬
        if hasattr(df.index, "tz") and df.index.tz is not None:
            df.index = df.index.tz_convert("UTC")
        else:
            df.index = pd.to_datetime(df.index, utc=True)

        # 일봉: UTC 00:00 기준 resample
        if tf == "1d":
            df = df.resample("1D", offset=utc_candle_base).agg({
                "open": "first", "high": "max",
                "low": "min", "close": "last", "volume": "sum",
            }).dropna()

        # 8시간봉: 코인 특화
        if tf == "8h":
            df = df.resample("8H").agg({
                "open": "first", "high": "max",
                "low": "min", "close": "last", "volume": "sum",
            }).dropna()

        adjusted[tf] = df

    return adjusted
```

## E3. Output

- **스키마**:
  ```python
  @dataclass
  class MTFSignal:
      symbol: str                    # e.g., "BTC/USDT"
      action: str                    # "STRONG_BUY" | "BUY" | "HOLD" | "SELL" | "STRONG_SELL"
      confluence_score: float        # -1.0 ~ +1.0
      confidence: float              # 0.0 ~ 1.0
      alignment_score: float         # 0.0 ~ 1.0 (TF 정합성)
      direction_tf: str              # 방향 판단 TF (e.g., "1d")
      entry_tf: str                  # 진입 판단 TF (e.g., "15m")
      management_tf: str             # 관리 TF (e.g., "4h")
      is_valid_entry: bool           # Top-Down 정합성 통과 여부
      support: float                 # zone TF 기반 지지선
      resistance: float              # zone TF 기반 저항선
      timestamp: datetime
      metadata: dict                 # TF별 개별 시그널 상세
  ```
- **confidence 계산**: `abs(confluence_score)` — 다중 TF 합의도가 높을수록 신뢰도 상승
- **소비자**: `StrategyOrchestrator` (진입 판단) / `OrderManager` (주문 생성) / `51% Gate`

## E4. Class/API Design

```python
from engines.base import BaseEngine
from models.mtf import MTFSignal, TrendDirection, MarketType
import pandas as pd
import numpy as np
from typing import Optional

class MultiTimeframeEngine(BaseEngine):
    """멀티 타임프레임 통합 분석 엔진.

    Items: #20 정합성 검증, #21 Confluence, #22 Top-Down, #23 코인 24/7.
    """

    # LOCK 파라미터 (SPEC §14)
    ALIGNMENT_THRESHOLD: float = 0.6
    CONFLUENCE_BUY_THRESHOLD: float = 0.2
    CONFLUENCE_STRONG_THRESHOLD: float = 0.5
    EMA_FAST: int = 20
    EMA_SLOW: int = 50
    RSI_PERIOD: int = 14
    MIN_BARS: dict[str, int] = {
        "1d": 60, "8h": 90, "4h": 120, "1h": 240, "15m": 480,
    }

    TIMEFRAME_HIERARCHY: dict[MarketType, list[str]] = {
        MarketType.STOCK_KR: ["1d", "4h", "1h", "15m", "5m"],
        MarketType.STOCK_US: ["1d", "4h", "1h", "15m", "5m"],
        MarketType.CRYPTO: ["1d", "8h", "4h", "1h", "15m", "5m", "1m"],
    }

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "MultiTimeframeEngine"

    def validate_input(self, tf_data: dict[str, pd.DataFrame]) -> bool:
        """다중 타임프레임 입력 데이터 유효성 검증."""
        if len(tf_data) < 2:
            raise ValueError("At least 2 timeframes required")
        for tf, df in tf_data.items():
            required = ["close", "high", "low", "open", "volume"]
            missing = [c for c in required if c not in df.columns]
            if missing:
                raise ValueError(f"TF '{tf}' missing columns: {missing}")
        return True

    def check_alignment(
        self, tf_data: dict[str, pd.DataFrame], market_type: MarketType
    ) -> dict:
        """#20: 상위-하위 타임프레임 정합성 검증 (상위 추세 우선)."""
        ...

    def compute_confluence(
        self, tf_data: dict[str, pd.DataFrame], market_type: MarketType
    ) -> dict:
        """#21: 다중 시간대 가중 합의 시그널 생성."""
        ...

    def top_down_analysis(
        self, tf_data: dict[str, pd.DataFrame], market_type: MarketType
    ) -> dict:
        """#22: 방향(일봉) → 구간(4h) → 진입(15m) Top-Down 분석."""
        ...

    def adjust_crypto_timeframes(
        self, tf_data: dict[str, pd.DataFrame], utc_base: str = "00:00"
    ) -> dict[str, pd.DataFrame]:
        """#23: 코인 24/7 UTC 기준 봉 보정 + 8시간봉 생성."""
        ...

    def generate_signal(
        self, tf_data: dict[str, pd.DataFrame], market_type: MarketType
    ) -> MTFSignal:
        """통합 실행: 코인 보정 → 정합성 → Confluence → Top-Down → 시그널."""
        self.validate_input(tf_data)
        if market_type == MarketType.CRYPTO:
            tf_data = self.adjust_crypto_timeframes(tf_data)
        alignment = self.check_alignment(tf_data, market_type)
        confluence = self.compute_confluence(tf_data, market_type)
        top_down = self.top_down_analysis(tf_data, market_type)

        return MTFSignal(
            symbol=list(tf_data.values())[0].attrs.get("symbol", "UNKNOWN"),
            action=confluence["action"],
            confluence_score=confluence["confluence_score"],
            confidence=confluence["confidence"],
            alignment_score=alignment["alignment_score"],
            direction_tf=top_down.get("direction_tf", "1d"),
            entry_tf=top_down.get("entry_tf", "15m"),
            management_tf=top_down.get("management_tf", "4h"),
            is_valid_entry=top_down.get("is_valid_entry", False),
            support=top_down.get("support", 0.0),
            resistance=top_down.get("resistance", 0.0),
            timestamp=pd.Timestamp.utcnow(),
            metadata={
                "alignment": alignment,
                "tf_signals": confluence["tf_signals"],
                "top_down": top_down,
            },
        )
```

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | >= 2.0 | Yes | DataFrame, resample, EWM |
| numpy | >= 1.24 | Yes | 수치 연산 |
| kafka-python | >= 2.0 | Yes | 실시간 다중 TF 스트림 수신 |
| TimescaleDB | >= 2.11 | Yes | 다중 타임프레임 OHLCV 저장/조회 |
| pytz | >= 2023.3 | Yes | UTC 타임존 변환 (코인 24/7) |

## E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 단일 심볼 MTF 분석 (5 TF) | < 300ms | `time.perf_counter()`, TF당 최대 봉수 기준 |
| Confluence 계산 | < 100ms | 가중 합산 + RSI/EMA 계산 포함 |
| 코인 봉 보정 (resample) | < 200ms | 1d + 8h resample 기준 |
| 메모리 | < 30MB / 심볼 | 5 TF 동시 적재 기준 |
| 배치 50 심볼 | < 15s | 순차 기준 (병렬 시 < 5s) |

## E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 특정 TF 데이터 누락 | 해당 TF 제외, 나머지로 분석 (최소 2개 TF 필수) | WARNING |
| TF < 2개 | `ValueError` raise, 분석 불가 | CRITICAL |
| 최소 봉수 미달 (특정 TF) | 해당 TF 제외 + 경고 로깅 | WARNING |
| 타임존 미설정 (코인) | UTC 강제 변환, 경고 로깅 | LOW |
| 정합성 실패 (alignment < 0.6) | 시그널 생성하되 confidence 50% 감산 | HIGH |
| volume 0 (거래 없는 봉) | volume_ratio 계산 시 fallback=0.5 | LOW |
| 거래소별 봉 시작 시간 불일치 | UTC 기준 resample로 통일 | WARNING |

## E8. Test Criteria

- **Unit**:
  - 정합성 검증: 상승/하락/혼합 추세 시뮬레이션 → alignment_score 정확성
  - Confluence: 5개 TF 전부 매수 시그널 → STRONG_BUY, 혼합 시 HOLD 확인
  - Top-Down: 일봉 상승 + 15분 매수 → valid=True, 일봉 상승 + 15분 매도 → valid=False
  - 코인 보정: UTC 00:00 기준 resample 결과가 올바른 OHLCV 반환
  - RSI 계산: known-answer 대조 (소수점 2자리 일치)
- **Integration**:
  - Kafka → TimescaleDB (다중 TF) → MTFEngine → StrategyOrchestrator E2E
  - MTFSignal → OrderManager 전달 테스트
  - 코인/주식 market_type 분기 정상 동작 확인
- **Acceptance**:
  - 51% Gate: MTF Confluence 기반 진입이 단일 TF 대비 승률 >= 51%
  - 백테스트 (2020-2024): 상위 TF 추세 준수 진입의 수익률이 무시 진입 대비 유의미 개선
  - 코인 24/7: BTC/ETH UTC 봉 기준 분석이 거래소 기본 봉 대비 일관성 유지

## E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 51% Gate threshold = 0.51 | SPEC §6.1 | MTF Confluence 시그널 confidence >= 0.51 필수 |
| Circuit Breaker -3% | SPEC §10.2 | 일일 손실 -3% 시 전 TF 시그널 무시 |
| EMA 기간 (20, 50) | SPEC §14 | TF별 추세 판단 기준 파라미터 고정 |
| ALIGNMENT_THRESHOLD = 0.6 | SPEC §14 | 정합성 최소 기준값 고정 |
| RSI_PERIOD = 14 | SPEC §14 | 모든 TF 공통 RSI 기간 고정 |

---

> **L3 판정**: 9요소 전수 기재 완료 (E1~E9). **L3 PASS**.
> **검증일**: 2026-03-22
