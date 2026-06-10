# 시장 레짐(Market Regime) 실시간 감지 엔진
> **버전**: v1.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #1 실시간 적응형 전략
> **정본 소유 개념**: 시장 레짐 감지
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9

---

### B-5. 시장 레짐(Market Regime) 실시간 감지 엔진

**현재**: S7I-065에 한 줄 ("이동평균, VIX, 추세 지표 조합") — 상세 전무
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 16 | **레짐 분류 모델** | 현재 시장 상태를 실시간 분류: ① 강한 상승 추세 ② 약한 상승 ③ 횡보(레인지) ④ 약한 하락 ⑤ 강한 하락 ⑥ 고변동성(카오스) — 6가지 상태 머신 |
| 17 | **레짐 전이 감지** | "상승→횡보로 바뀌고 있다", "횡보→하락 진입 초기" — 전이 과정 실시간 감지. HMM(Hidden Markov Model) 또는 클러스터링 기반 |
| 18 | **레짐별 전략 자동 매핑** | 레짐 변경 감지 → 해당 레짐에 적합한 전략으로 자동 전환 제안. 현재 §7.9 정적 테이블을 동적 엔진으로 승격 |
| 19 | **레짐 전이 속도 분석** | 천천히 바뀌는 건지(점진적 추세 전환) vs 갑자기 바뀌는 건지(블랙 스완) — 속도에 따른 대응 차등 |

---

## E1. Input

- **데이터**: `OHLCV_PLUS` + `VOLATILITY_INDEX` from TimescaleDB / Kafka real-time stream
- **필수 필드**:
  - `close` (float64) — 종가 시계열
  - `high` (float64) — 고가
  - `low` (float64) — 저가
  - `volume` (int64) — 거래량
  - `timestamp` (datetime) — 봉 시각
  - `vix` (float64) — 변동성 지수 (VIX/VKOSPI, 시장별)
- **선택 필드**: `atr` (float64), `rsi` (float64) — 사전 계산된 지표
- **전처리**:
  - NaN/Null: forward-fill 후 잔여 NaN drop
  - 최소 120봉 확보 필수 (HMM 수렴 + 이동평균 안정화)
  - 타임스탬프 ascending 정렬
  - 수익률 계산: `returns = close.pct_change()`
  - 변동성 정규화: 20일 rolling std → z-score

## E2. Algorithm

```python
# 시장 레짐 감지 엔진 의사코드 — 복사 → 구현 가능
import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

class RegimeState(IntEnum):
    STRONG_BULL = 0    # 강한 상승
    WEAK_BULL = 1      # 약한 상승
    SIDEWAYS = 2       # 횡보
    WEAK_BEAR = 3      # 약한 하락
    STRONG_BEAR = 4    # 강한 하락
    HIGH_VOLATILITY = 5  # 고변동성(카오스)

# --- #16: 레짐 분류 모델 ---
def classify_regime(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    volume: pd.Series,
    vix: pd.Series,
    n_regimes: int = 6,
    lookback: int = 120,
) -> dict:
    """
    HMM 기반 6-상태 레짐 분류.
    Features: [returns, volatility, volume_change, vix_level]
    """
    # Step 1: 특성 엔지니어링
    returns = close.pct_change().dropna()
    volatility = returns.rolling(window=20).std()
    volume_change = volume.pct_change()
    atr = (high - low).rolling(window=14).mean()

    features = pd.DataFrame({
        "returns": returns,
        "volatility": volatility,
        "volume_change": volume_change,
        "vix_norm": (vix - vix.rolling(60).mean()) / vix.rolling(60).std(),
    }).dropna().tail(lookback)

    X = features.values  # shape: (lookback, 4)

    # Step 2: HMM 피팅
    model = GaussianHMM(
        n_components=n_regimes,
        covariance_type="full",
        n_iter=100,
        random_state=42,
    )
    model.fit(X)

    # Step 3: 현재 상태 예측
    hidden_states = model.predict(X)
    current_state_raw = hidden_states[-1]

    # Step 4: HMM 상태를 의미 있는 레짐으로 매핑
    #   각 상태의 평균 수익률/변동성으로 정렬하여 라벨링
    state_means = {}
    for s in range(n_regimes):
        mask = hidden_states == s
        state_means[s] = {
            "mean_return": features["returns"].values[mask].mean(),
            "mean_vol": features["volatility"].values[mask].mean(),
        }

    regime = _map_state_to_regime(current_state_raw, state_means)
    state_probs = model.predict_proba(X)[-1]  # 현재 시점 상태 확률

    return {
        "regime": regime,
        "state_probabilities": dict(enumerate(state_probs)),
        "confidence": float(max(state_probs)),
        "model": model,
        "hidden_states": hidden_states,
    }


def _map_state_to_regime(
    raw_state: int,
    state_means: dict,
) -> RegimeState:
    """HMM raw 상태를 6가지 레짐으로 매핑 (수익률/변동성 기반 정렬)."""
    sorted_by_return = sorted(
        state_means.items(),
        key=lambda x: x[1]["mean_return"],
    )
    # 가장 높은 변동성 상태 → HIGH_VOLATILITY
    vol_sorted = sorted(
        state_means.items(),
        key=lambda x: x[1]["mean_vol"],
        reverse=True,
    )
    high_vol_state = vol_sorted[0][0]

    if raw_state == high_vol_state and state_means[raw_state]["mean_vol"] > 0.03:
        return RegimeState.HIGH_VOLATILITY

    # 수익률 순서로 나머지 매핑 (고변동성 상태 제외 → 6상태를 5버킷에 정합)
    return_rank = [s[0] for s in sorted_by_return if s[0] != high_vol_state]
    if raw_state not in return_rank:
        return RegimeState.HIGH_VOLATILITY
    idx = return_rank.index(raw_state)
    ratio = idx / (len(return_rank) - 1) if len(return_rank) > 1 else 0.5  # 0.0 ~ 1.0

    if ratio >= 0.8:
        return RegimeState.STRONG_BULL
    elif ratio >= 0.6:
        return RegimeState.WEAK_BULL
    elif ratio >= 0.4:
        return RegimeState.SIDEWAYS
    elif ratio >= 0.2:
        return RegimeState.WEAK_BEAR
    else:
        return RegimeState.STRONG_BEAR


# --- #17: 레짐 전이 감지 ---
def detect_regime_transition(
    hidden_states: np.ndarray,
    model: GaussianHMM,
    window: int = 10,
) -> dict:
    """
    전이 행렬 기반 레짐 전이 감지.
    현재 상태와 최근 window 내 상태 변화를 분석.
    """
    transition_matrix = model.transmat_  # shape: (n, n)
    current = hidden_states[-1]
    recent = hidden_states[-window:]

    # 최근 window 내 상태 변화 횟수
    transitions = sum(
        1 for i in range(1, len(recent)) if recent[i] != recent[i - 1]
    )

    # 다음 가능 상태와 확률
    next_state_probs = transition_matrix[current]
    most_likely_next = int(np.argmax(next_state_probs))
    is_transitioning = (most_likely_next != current) and (
        next_state_probs[most_likely_next] > 0.3
    )

    return {
        "is_transitioning": is_transitioning,
        "from_state": int(current),
        "to_state": most_likely_next if is_transitioning else None,
        "transition_probability": float(next_state_probs[most_likely_next]),
        "recent_transition_count": transitions,
        "transition_matrix": transition_matrix.tolist(),
    }


# --- #18: 레짐별 전략 자동 매핑 ---
REGIME_STRATEGY_MAP: dict[RegimeState, list[str]] = {
    RegimeState.STRONG_BULL: ["momentum", "breakout", "pyramiding"],
    RegimeState.WEAK_BULL: ["momentum_conservative", "scale_in"],
    RegimeState.SIDEWAYS: ["mean_reversion", "range_trading", "grid"],
    RegimeState.WEAK_BEAR: ["defensive", "hedge_partial", "scale_out"],
    RegimeState.STRONG_BEAR: ["short_only", "hedge_full", "cash"],
    RegimeState.HIGH_VOLATILITY: ["volatility_selling", "straddle", "reduce_size"],
}

def map_regime_to_strategy(
    regime: RegimeState,
    current_strategies: list[str],
    portfolio_exposure: float,
) -> dict:
    """
    레짐 변경 → 전략 전환 제안.
    현재 활성 전략과 새 레짐 적합 전략을 비교하여 전환 액션 생성.
    """
    recommended = REGIME_STRATEGY_MAP.get(regime, ["hold"])
    to_activate = [s for s in recommended if s not in current_strategies]
    to_deactivate = [s for s in current_strategies if s not in recommended]

    # 포지션 크기 조정 배율
    size_multiplier = {
        RegimeState.STRONG_BULL: 1.2,
        RegimeState.WEAK_BULL: 1.0,
        RegimeState.SIDEWAYS: 0.7,
        RegimeState.WEAK_BEAR: 0.5,
        RegimeState.STRONG_BEAR: 0.2,
        RegimeState.HIGH_VOLATILITY: 0.3,
    }

    return {
        "regime": regime.name,
        "recommended_strategies": recommended,
        "activate": to_activate,
        "deactivate": to_deactivate,
        "position_size_multiplier": size_multiplier.get(regime, 1.0),
        "urgency": "HIGH" if regime in (
            RegimeState.STRONG_BEAR, RegimeState.HIGH_VOLATILITY
        ) else "NORMAL",
    }


# --- #19: 레짐 전이 속도 분석 ---
def analyze_transition_speed(
    hidden_states: np.ndarray,
    timestamps: pd.DatetimeIndex,
    window: int = 20,
) -> dict:
    """
    전이 속도 분석: 점진적(gradual) vs 급격(sudden).
    최근 window 내 상태 변화 빈도와 간격을 기반으로 판정.
    """
    recent_states = hidden_states[-window:]
    recent_times = timestamps[-window:]

    transitions = []
    for i in range(1, len(recent_states)):
        if recent_states[i] != recent_states[i - 1]:
            transitions.append({
                "from": int(recent_states[i - 1]),
                "to": int(recent_states[i]),
                "timestamp": recent_times[i],
            })

    if len(transitions) == 0:
        return {
            "speed": "STABLE",
            "transition_count": 0,
            "avg_duration_bars": window,
            "is_black_swan": False,
        }

    # 전이 간 간격 (봉 수)
    intervals = []
    for i in range(1, len(transitions)):
        idx_curr = list(recent_times).index(transitions[i]["timestamp"])
        idx_prev = list(recent_times).index(transitions[i - 1]["timestamp"])
        intervals.append(idx_curr - idx_prev)

    avg_interval = np.mean(intervals) if intervals else window
    transition_rate = len(transitions) / window

    # 급격 전환: 3봉 이내 2단계 이상 점프
    is_sudden = any(
        abs(t["to"] - t["from"]) >= 2 for t in transitions[-3:]
    )
    is_black_swan = is_sudden and transition_rate > 0.3

    if transition_rate > 0.25:
        speed = "RAPID"
    elif transition_rate > 0.10:
        speed = "GRADUAL"
    else:
        speed = "SLOW"

    return {
        "speed": speed,
        "transition_count": len(transitions),
        "avg_duration_bars": float(avg_interval),
        "transition_rate": round(transition_rate, 4),
        "is_black_swan": is_black_swan,
        "response_action": "EMERGENCY_HEDGE" if is_black_swan else "NORMAL_SWITCH",
    }
```

## E3. Output

- **스키마**:
  ```python
  @dataclass
  class RegimeResult:
      symbol: str                      # e.g., "005930.KS"
      regime: RegimeState              # 현재 레짐 (6가지 중 하나)
      confidence: float                # 0.0 ~ 1.0
      is_transitioning: bool           # 전이 중 여부
      transition_to: Optional[RegimeState]  # 전이 목표 레짐
      transition_speed: str            # "STABLE" | "SLOW" | "GRADUAL" | "RAPID"
      recommended_strategies: list[str]     # 권장 전략 목록
      position_size_multiplier: float       # 포지션 크기 배율
      timestamp: datetime              # 분석 시각
      metadata: dict                   # 전이 행렬, 상태 확률 등 상세
  ```
- **confidence 계산**: HMM `predict_proba()`의 현재 상태 확률 (max probability)
- **소비자**: `StrategyOrchestrator` (전략 전환) / `PositionSizer` (크기 조정) / `RiskManager` (긴급 헤지) / `51% Gate`

## E4. Class/API Design

```python
from engines.base import BaseEngine
from models.regime import RegimeResult, RegimeState
from hmmlearn.hmm import GaussianHMM
import pandas as pd
import numpy as np
from typing import Optional

class MarketRegimeEngine(BaseEngine):
    """시장 레짐 실시간 감지 엔진.

    SPEC §7.9 정적 레짐 테이블을 동적 HMM 기반 엔진으로 승격.
    Items: #16 레짐 분류, #17 전이 감지, #18 전략 매핑, #19 전이 속도.
    """

    # LOCK 파라미터 (SPEC §14)
    N_REGIMES: int = 6
    MIN_BARS: int = 120
    HMM_ITERATIONS: int = 100
    TRANSITION_WINDOW: int = 10
    SPEED_WINDOW: int = 20

    REGIME_STRATEGY_MAP: dict[RegimeState, list[str]] = {
        RegimeState.STRONG_BULL: ["momentum", "breakout", "pyramiding"],
        RegimeState.WEAK_BULL: ["momentum_conservative", "scale_in"],
        RegimeState.SIDEWAYS: ["mean_reversion", "range_trading", "grid"],
        RegimeState.WEAK_BEAR: ["defensive", "hedge_partial", "scale_out"],
        RegimeState.STRONG_BEAR: ["short_only", "hedge_full", "cash"],
        RegimeState.HIGH_VOLATILITY: ["volatility_selling", "straddle", "reduce_size"],
    }

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "MarketRegimeEngine"
        self._hmm_model: Optional[GaussianHMM] = None

    def validate_input(self, df: pd.DataFrame) -> bool:
        """입력 데이터 유효성 검증."""
        required = ["close", "high", "low", "volume", "vix"]
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        if len(df) < self.MIN_BARS:
            raise ValueError(f"Insufficient bars: {len(df)} < {self.MIN_BARS}")
        return True

    def classify_regime(self, df: pd.DataFrame) -> dict:
        """#16: HMM 기반 6-상태 레짐 분류."""
        ...

    def detect_transition(self, hidden_states: np.ndarray) -> dict:
        """#17: 전이 행렬 기반 레짐 전이 실시간 감지."""
        ...

    def map_strategy(
        self, regime: RegimeState, current_strategies: list[str], exposure: float
    ) -> dict:
        """#18: 레짐 → 전략 동적 매핑 (§7.9 승격)."""
        ...

    def analyze_transition_speed(
        self, hidden_states: np.ndarray, timestamps: pd.DatetimeIndex
    ) -> dict:
        """#19: 점진적 vs 급격 전환 판별 + 블랙스완 감지."""
        ...

    def generate_signal(self, df: pd.DataFrame) -> RegimeResult:
        """통합 실행: 레짐 분류 → 전이 감지 → 전략 매핑 → 속도 분석."""
        self.validate_input(df)
        classification = self.classify_regime(df)
        transition = self.detect_transition(classification["hidden_states"])
        strategy = self.map_strategy(
            classification["regime"], [], 0.0
        )
        speed = self.analyze_transition_speed(
            classification["hidden_states"], df.index
        )
        return RegimeResult(
            symbol=df.attrs.get("symbol", "UNKNOWN"),
            regime=classification["regime"],
            confidence=classification["confidence"],
            is_transitioning=transition["is_transitioning"],
            transition_to=transition.get("to_state"),
            transition_speed=speed["speed"],
            recommended_strategies=strategy["recommended_strategies"],
            position_size_multiplier=strategy["position_size_multiplier"],
            timestamp=df.index[-1],
            metadata={
                "state_probabilities": classification["state_probabilities"],
                "transition_matrix": transition["transition_matrix"],
                "transition_rate": speed.get("transition_rate", 0.0),
                "is_black_swan": speed["is_black_swan"],
            },
        )
```

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | >= 2.0 | Yes | DataFrame, rolling 통계 |
| numpy | >= 1.24 | Yes | 행렬 연산, 상태 매핑 |
| hmmlearn | >= 0.3.0 | Yes | GaussianHMM 모델 학습/예측 |
| scikit-learn | >= 1.3 | Yes | 전처리 (StandardScaler), 검증 |
| kafka-python | >= 2.0 | Yes | 실시간 스트림 수신 |
| TimescaleDB | >= 2.11 | Yes | OHLCV + VIX 시계열 저장 |

## E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 단일 심볼 레짐 분류 | < 200ms | `time.perf_counter()`, 120봉 기준 |
| HMM 모델 재학습 | < 5s | 일 1회 배치 재학습 기준 |
| 전이 감지 (증분) | < 50ms | 기학습 모델에 새 봉 predict만 |
| 메모리 | < 50MB / 모델 | `tracemalloc` 프로파일링 |
| 전략 매핑 응답 | < 10ms | 룩업 테이블 기반 |

## E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| VIX 데이터 누락 | 최근 20일 rolling std로 대체 proxy 생성 | WARNING |
| HMM 수렴 실패 (n_iter 초과) | 이전 학습 모델 유지, 재학습 스케줄 등록 | HIGH |
| 최소 봉수 미달 (< 120) | `ValueError` raise (호출자가 포착, 레짐 미산출 — UNKNOWN 반환 없음; RegimeState 6상태 고정) | CRITICAL |
| 전이 행렬 NaN/Inf | 균등 확률 (1/6) 대체, 경고 로깅 | HIGH |
| 블랙스완 감지 | `EMERGENCY_HEDGE` 액션 + RiskManager 즉시 알림 | CRITICAL |
| Kafka 스트림 단절 | 최근 캐시 데이터로 fallback, 3회 재연결 시도 | HIGH |

## E8. Test Criteria

- **Unit**:
  - HMM 6-상태 분류: 시뮬레이션 데이터 (명확한 추세 구간) 대비 레짐 라벨 정확도 >= 80%
  - 전이 감지: 알려진 전이 시점 (상승→하락) 감지 성공 여부
  - 전략 매핑: 6개 레짐 각각에 대해 올바른 전략 리스트 반환 검증
  - 전이 속도: RAPID/GRADUAL/SLOW 분류가 known-answer와 일치
- **Integration**:
  - Kafka → TimescaleDB → RegimeEngine → StrategyOrchestrator E2E 파이프라인
  - 레짐 변경 시 StrategyOrchestrator에 전략 전환 메시지 정상 전달
  - RiskManager 긴급 알림 (블랙스완) 트리거 테스트
- **Acceptance**:
  - 51% Gate: 레짐 기반 전략 전환이 단일 전략 대비 승률 >= 51% 개선
  - 백테스트 (2020-2024): 코로나 하락, 회복, 횡보 구간에서 레짐 정확도 >= 70%
  - 블랙스완 감지: 2020-03 COVID 크래시 데이터에서 EMERGENCY 트리거 확인

## E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 51% Gate threshold = 0.51 | SPEC §6.1 | 레짐 기반 전략 전환 후 승률 51% 이상 유지 필수 |
| Circuit Breaker -3% | SPEC §10.2 | 일일 손실 -3% 시 전 레짐 무관 강제 방어모드 |
| N_REGIMES = 6 | SPEC §14 | 6-상태 모델 고정, 변경 시 LOCK 해제 절차 |
| HMM n_iter = 100 | SPEC §14 | 학습 반복 횟수 고정 |
| MIN_BARS = 120 | SPEC §14 | 최소 데이터 요구량 고정 |

---

> **L3 판정**: 9요소 전수 기재 완료 (E1~E9). **L3 PASS**.
> **검증일**: 2026-03-22
