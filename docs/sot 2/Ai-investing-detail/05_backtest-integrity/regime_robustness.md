# 시장 레짐 변화 강건성 (Regime Robustness)
> **버전**: v1.0
> **Status**: APPROVED
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #5 백테스트 진실성
> **정본 소유 개념**: 백테스트 프레임워크 (폴더 전체)
> **기술스택 의존성**: SPEC §14 LOCK 범위 내

---

### B-5. 시장 레짐 변화 강건성 (Regime Robustness)

**현재**: 정적 Walk-Forward만 존재
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 19 | **레짐별 분할 백테스트** | Bull/Bear/Sideways/Crisis 4개 레짐 각각에서 독립 백테스트. 전략이 특정 레짐에서만 작동하는지 식별 |
| 20 | **스트레스 기간 필수 포함** | 2008 금융위기, 2020 코로나, 2022 금리 인상기 등 스트레스 기간이 반드시 테스트 기간에 포함되도록 강제 |
| 21 | **레짐 전환점 성과 분석** | 레짐이 전환되는 시점(Bull→Bear 등)에서 전략 성과 급변 여부 검증. 전환점에서 MDD 급등 = 레짐 적응 실패 |
| 22 | **비정상(Non-Stationary) 환경 테스트** | 데이터의 통계적 특성(평균, 분산, 상관)이 시간에 따라 변함을 가정한 테스트. 과거 최적 파라미터가 구조 변화 후에도 유효한지 |

---

## E1. Input - 데이터, 필수 필드, 전처리

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `returns` | `Series` | Y | 전략 일별 수익률 시계열 |
| `benchmark_returns` | `Series` | Y | 벤치마크(시장) 일별 수익률 |
| `volatility` | `Series` | N | 시장 변동성 (VIX 등) 시계열 |
| `regime_labels` | `Series` | N | 사전 분류된 레짐 라벨 (bull/bear/sideways/crisis) |
| `crisis_periods` | `list[tuple]` | Y | 위기 기간 리스트 [(start, end), ...] |
| `structural_break_test` | `str` | N | 구조변화 검정 방법 ("cusum" / "bai_perron" / "chow") |
| `regime_method` | `str` | N | 레짐 분류 방법 ("hmm" / "threshold" / "manual") |
| `min_regime_days` | `int` | N | 레짐당 최소 거래일 수 (기본값 60) |

**전처리**:
1. `crisis_periods` 필수 포함: 2008 금융위기(2007-10~2009-03), 2020 코로나(2020-02~2020-04), 2022 금리인상(2022-01~2022-10)
2. 레짐 분류 미제공 시 수익률 기반 자동 분류 (HMM 또는 threshold)
3. 각 레짐 최소 60 거래일 확보 검증

---

## E2. Algorithm - 복사→구현 가능 의사코드 with REAL formulas

```python
import numpy as np
from scipy import stats
from enum import Enum

class Regime(Enum):
    BULL = "bull"
    BEAR = "bear"
    SIDEWAYS = "sideways"
    CRISIS = "crisis"

# === 레짐 분류 (Threshold 기반) ===
def classify_regimes(
    benchmark_returns: np.ndarray,
    window: int = 63,  # 3개월 롤링
    bull_threshold: float = 0.10,    # 연간화 수익률 > 10%
    bear_threshold: float = -0.10,   # 연간화 수익률 < -10%
    crisis_vix_threshold: float = 30.0,
    volatility: np.ndarray = None
) -> np.ndarray:
    """수익률/변동성 기반 레짐 분류"""
    T = len(benchmark_returns)
    regimes = np.full(T, Regime.SIDEWAYS.value, dtype=object)

    # 롤링 연간화 수익률
    rolling_annual = np.convolve(benchmark_returns, np.ones(window)/window, mode='full')[:T] * 252  # 후행(trailing) 전용 — 미래 데이터 미포함

    for t in range(T):
        if volatility is not None and volatility[t] > crisis_vix_threshold:
            regimes[t] = Regime.CRISIS.value
        elif rolling_annual[t] > bull_threshold:
            regimes[t] = Regime.BULL.value
        elif rolling_annual[t] < bear_threshold:
            regimes[t] = Regime.BEAR.value
        else:
            regimes[t] = Regime.SIDEWAYS.value

    return regimes

# === 레짐별 분할 백테스트 ===
def regime_conditional_backtest(
    strategy_returns: np.ndarray,
    regimes: np.ndarray
) -> dict:
    """각 레짐별 독립 성과 분석"""
    results = {}
    for regime in [r.value for r in Regime]:
        mask = regimes == regime
        if mask.sum() < 20:  # 최소 20일
            results[regime] = {'sharpe': None, 'n_days': int(mask.sum()), 'insufficient': True}
            continue

        r = strategy_returns[mask]
        sharpe = np.sqrt(252) * np.mean(r) / np.std(r, ddof=1) if np.std(r) > 0 else 0.0
        mdd = compute_max_drawdown(r)
        results[regime] = {
            'sharpe': float(sharpe),
            'annual_return': float(np.mean(r) * 252),
            'annual_vol': float(np.std(r, ddof=1) * np.sqrt(252)),
            'max_drawdown': float(mdd),
            'n_days': int(mask.sum()),
            'insufficient': False
        }
    return results

def compute_max_drawdown(returns: np.ndarray) -> float:
    """최대 낙폭 계산"""
    cumulative = np.cumprod(1 + returns)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    return float(np.min(drawdown))

# === 스트레스 기간 필수 포함 검증 ===
REQUIRED_CRISIS_PERIODS = [
    ("2008 금융위기", "2007-10-01", "2009-03-31"),
    ("2020 코로나", "2020-02-01", "2020-04-30"),
    ("2022 금리인상", "2022-01-01", "2022-10-31"),
]

def verify_stress_period_coverage(
    backtest_start: str, backtest_end: str, crisis_periods: list[tuple]
) -> list[dict]:
    """스트레스 기간이 백테스트에 포함되는지 검증"""
    from datetime import datetime
    bt_start = datetime.strptime(backtest_start, "%Y-%m-%d")
    bt_end   = datetime.strptime(backtest_end, "%Y-%m-%d")

    coverage = []
    for name, cs, ce in crisis_periods:
        cs_dt = datetime.strptime(cs, "%Y-%m-%d")
        ce_dt = datetime.strptime(ce, "%Y-%m-%d")
        included = bt_start <= cs_dt and bt_end >= ce_dt
        coverage.append({
            'crisis': name,
            'start': cs,
            'end': ce,
            'included': included
        })
    return coverage

# === 레짐 전환점 성과 분석 ===
def analyze_regime_transitions(
    strategy_returns: np.ndarray,
    regimes: np.ndarray,
    window: int = 10  # 전환점 전후 10일
) -> list[dict]:
    """레짐 전환 시점에서 전략 성과 분석"""
    transitions = []
    for t in range(1, len(regimes)):
        if regimes[t] != regimes[t-1]:
            pre  = strategy_returns[max(0, t-window):t]
            post = strategy_returns[t:min(len(strategy_returns), t+window)]

            pre_mdd  = compute_max_drawdown(pre) if len(pre) > 1 else 0.0
            post_mdd = compute_max_drawdown(post) if len(post) > 1 else 0.0

            transitions.append({
                'date_idx': t,
                'from_regime': regimes[t-1],
                'to_regime': regimes[t],
                'pre_mdd': pre_mdd,
                'post_mdd': post_mdd,
                'mdd_spike': abs(pre_mdd) > 1e-9 and post_mdd < pre_mdd * 2,  # 전환 후 MDD 2배 이상 악화? (pre_mdd≈0 가드)
                'adaptation_failure': post_mdd < -0.10  # 전환 후 MDD > 10%
            })
    return transitions

# === 구조 변화(Structural Break) 검정 ===
def detect_structural_breaks(
    returns: np.ndarray,
    method: str = "cusum"
) -> list[int]:
    """구조 변화 시점 탐지"""
    if method == "cusum":
        # CUSUM 검정: 누적합이 임계값 초과하는 시점
        cumsum = np.cumsum(returns - np.mean(returns))
        std_r = np.std(returns)
        threshold = 2.0 * std_r * np.sqrt(len(returns))  # 95% 신뢰수준
        breaks = []
        for t in range(1, len(cumsum)):
            if abs(cumsum[t]) > threshold:
                breaks.append(t)
                # 리셋
                cumsum[t:] -= cumsum[t]
        return breaks
    # 다른 방법은 확장 가능
    return []
```

---

## E3. Output - @dataclass, confidence, 소비자

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class RegimePerformance:
    regime: str
    sharpe: float
    annual_return: float
    annual_vol: float
    max_drawdown: float
    n_days: int

@dataclass
class RegimeTransition:
    date_idx: int
    from_regime: str
    to_regime: str
    pre_mdd: float
    post_mdd: float
    adaptation_failure: bool

@dataclass
class RegimeRobustnessReport:
    """레짐 강건성 검증 리포트"""
    regime_performances: list[RegimePerformance] = field(default_factory=list)
    crisis_coverage: list[dict] = field(default_factory=list)
    transitions: list[RegimeTransition] = field(default_factory=list)
    structural_breaks: list[int] = field(default_factory=list)
    worst_regime: str = ""
    worst_regime_sharpe: float = 0.0
    all_crises_covered: bool = False
    transition_failures: int = 0
    confidence: float = 0.0
    passed: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    def compute_confidence(self):
        """레짐별 성과 + 위기 커버리지 + 전환점 안정성 종합"""
        scores = []
        # 1) 모든 레짐에서 Sharpe > 0
        positive_regimes = sum(1 for rp in self.regime_performances if rp.sharpe and rp.sharpe > 0)
        scores.append(positive_regimes / max(len(self.regime_performances), 1))
        # 2) 위기 기간 100% 포함
        scores.append(1.0 if self.all_crises_covered else 0.0)
        # 3) 전환점 적응 실패율 < 20%
        if self.transitions:
            fail_rate = self.transition_failures / len(self.transitions)
            scores.append(1.0 - fail_rate)
        else:
            scores.append(0.5)
        self.confidence = sum(scores) / len(scores)
        self.passed = self.confidence >= 0.7
```

**소비자**: 전략 검증 파이프라인, 리스크 관리 시스템, 포트폴리오 배분 엔진

---

## E4. Class/API Design - class with methods

```python
class RegimeRobustnessChecker:
    """시장 레짐 변화 강건성 검증 클래스"""

    def __init__(
        self,
        crisis_periods: list[tuple] = None,
        regime_method: str = "threshold",
        min_regime_days: int = 60
    ):
        self.crisis_periods = crisis_periods or REQUIRED_CRISIS_PERIODS
        self.regime_method = regime_method
        self.min_regime_days = min_regime_days

    # --- 레짐 분류 ---
    def classify(self, benchmark_returns: Series, volatility: Series = None) -> Series:
        """시장 레짐 자동 분류 (bull/bear/sideways/crisis)"""
        ...

    # --- 레짐별 백테스트 ---
    def test_by_regime(self, strategy_returns: Series, regimes: Series) -> dict:
        """각 레짐별 독립 성과 분석"""
        ...

    # --- 스트레스 기간 검증 ---
    def verify_crisis_coverage(self, backtest_start: str, backtest_end: str) -> list[dict]:
        """필수 위기 기간 포함 여부 확인"""
        ...

    # --- 레짐 전환점 분석 ---
    def analyze_transitions(self, strategy_returns: Series, regimes: Series) -> list[dict]:
        """레짐 전환 시점 성과 분석"""
        ...

    # --- 구조 변화 검정 ---
    def detect_breaks(self, returns: Series, method: str = "cusum") -> list[int]:
        """구조 변화 시점 탐지"""
        ...

    # --- 비정상 환경 테스트 ---
    def test_non_stationarity(self, returns: Series, window: int = 252) -> dict:
        """롤링 통계량 변화 분석 (평균, 분산, 상관)"""
        ...

    # --- 통합 감사 ---
    def full_audit(self, strategy_returns: Series, benchmark_returns: Series) -> RegimeRobustnessReport:
        """전체 레짐 강건성 감사"""
        ...
```

---

## E5. Tech Stack Dependency

| 구성 요소 | 기술 | 버전 | 용도 |
|-----------|------|------|------|
| 레짐 분류 (HMM) | hmmlearn | ≥0.3 | Hidden Markov Model 레짐 분류 |
| 통계 검정 | SciPy `stats` | ≥1.11 | CUSUM, 구조변화 검정 |
| 수치 계산 | NumPy | ≥1.24 | 수익률 계산, 롤링 통계 |
| 데이터 처리 | Pandas | ≥2.0 | 시계열 필터링, 레짐 마스킹 |
| 시각화 | Matplotlib / Plotly | - | 레짐별 성과 차트, 전환점 시각화 |
| SPEC 참조 | LOCK §14 | - | 기술스택 범위 제약 |

---

## E6. Performance Requirements

| 지표 | 목표 | 허용 한계 | 측정 방법 |
|------|------|-----------|-----------|
| 레짐 분류 (threshold) | < 1s | < 5s | 10년(2,520일) 데이터 |
| 레짐 분류 (HMM) | < 10s | < 30s | 10년 데이터, 4-state HMM |
| 레짐별 백테스트 (4 레짐) | < 5s | < 15s | 각 레짐 독립 성과 계산 |
| 전환점 분석 | < 2s | < 10s | 전체 전환점 탐지 + 분석 |
| 구조 변화 검정 (CUSUM) | < 3s | < 10s | 10년 데이터 |
| 메모리 사용량 | < 500MB | < 1GB | 전체 파이프라인 |

---

## E7. Error Handling

| 에러 코드 | 상황 | 처리 방법 | 심각도 |
|-----------|------|-----------|--------|
| `RGM-001` | 레짐당 데이터 < 60일 | 해당 레짐 결과 "insufficient" 표시 | WARNING |
| `RGM-002` | 필수 위기 기간 미포함 | 백테스트 기간 연장 권고, CRITICAL 경고 | CRITICAL |
| `RGM-003` | HMM 수렴 실패 | threshold 방법으로 폴백 | WARNING |
| `RGM-004` | 전환점 전후 데이터 부족 | window 축소, 분석 가능 범위 내 수행 | WARNING |
| `RGM-005` | 모든 레짐에서 음수 Sharpe | 전략 전면 재검토 권고 | CRITICAL |
| `RGM-006` | 구조 변화점 과다 검출 (>20개/년) | 임계값 상향, 유의수준 조정 | WARNING |

---

## E8. Test Criteria - Unit / Integration / Acceptance

**Unit Tests**:
- `test_regime_classification_bull`: 연간화 수익률 > 10% 구간 → BULL 분류 확인
- `test_regime_classification_crisis`: VIX > 30 구간 → CRISIS 분류 확인
- `test_crisis_coverage_2008`: 2005~2015 백테스트 → 2008 금융위기 포함 확인
- `test_crisis_coverage_fail`: 2015~2020-01 백테스트 → 코로나 미포함 탐지
- `test_transition_detection`: Bull→Bear 전환 시점 정확 탐지

**Integration Tests**:
- `test_full_regime_audit`: 전체 4레짐 + 위기 커버리지 + 전환점 분석 통합 실행
- `test_hmm_vs_threshold_consistency`: 두 방법 레짐 분류 결과 70% 이상 일치
- `test_structural_break_integration`: 구조 변화 검정 → 레짐 재분류 연동

**Acceptance Tests**:
- 2005~2025 백테스트: 3개 필수 위기 기간 모두 포함
- 4개 레짐 모두에서 성과 보고서 생성
- 전환점 적응 실패율 < 20%

---

## E9. LOCK References

| LOCK 항목 | 참조 | 연관 |
|-----------|------|------|
| SPEC §14 | 기술스택 범위 | NumPy, SciPy, hmmlearn 범위 내 |
| SPEC §5 | 백테스트 진실성 | 레짐 강건성 = 핵심 요구사항 |
| B-5 #19 | 레짐별 분할 백테스트 | `RegimeRobustnessChecker.test_by_regime()` |
| B-5 #20 | 스트레스 기간 필수 포함 | `RegimeRobustnessChecker.verify_crisis_coverage()` |
| B-5 #21 | 레짐 전환점 성과 분석 | `RegimeRobustnessChecker.analyze_transitions()` |
| B-5 #22 | 비정상 환경 테스트 | `RegimeRobustnessChecker.test_non_stationarity()` |

---
