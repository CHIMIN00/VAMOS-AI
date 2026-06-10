# Data Snooping & Multiple Testing 보정
> **버전**: v1.0
> **Status**: APPROVED
> **L3 완성도**: ☑E1 ☑E2 ☑E3 ☑E4 ☑E5 ☑E6 ☑E7 ☑E8 ☑E9
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #5 백테스트 진실성
> **정본 소유 개념**: 백테스트 프레임워크 (폴더 전체)
> **기술스택 의존성**: SPEC §14 LOCK 범위 내

---

### B-3. Data Snooping & Multiple Testing 보정

**현재**: 완전히 없음
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 10 | **다중 비교 보정(Multiple Testing Correction)** | 96개 전략을 동시 테스트하면 우연히 좋은 전략 발견 확률 높음. Bonferroni / Holm / BH(FDR) 보정 적용 → 조정 p-value 기준 전략 채택 |
| 11 | **White's Reality Check** | 전략이 "데이터 마이닝으로 발견된 것"인지 검증. Bootstrap으로 모든 전략의 우연한 최고 성과 분포 생성 → 실제 최고 전략이 이 분포를 유의하게 초과하는지 |
| 12 | **Hansen's SPA(Superior Predictive Ability) 테스트** | White's RC 개선판. 벤치마크 대비 통계적으로 유의한 전략만 채택 |
| 13 | **전략 개발 히스토리 기록** | 몇 개의 전략을 시도했고, 몇 개를 폐기했는지 기록. "100개 시도 중 5개 채택" → 실질 유의수준 보정 필요 |

---

## E1. Input - 데이터, 필수 필드, 전처리

| 필드 | 타입 | 필수 | 설명 |
|------|------|------|------|
| `strategy_returns` | `DataFrame` | Y | N개 전략의 일별 수익률 시계열 (columns=전략명) |
| `benchmark_returns` | `Series` | Y | 벤치마크 일별 수익률 |
| `n_strategies_tested` | `int` | Y | 총 테스트한 전략 수 (폐기 포함) |
| `n_strategies_selected` | `int` | Y | 최종 채택 전략 수 |
| `alpha` | `float` | N | 유의수준 (기본값 0.05) |
| `n_bootstrap` | `int` | N | Bootstrap 반복 횟수 (기본값 10,000) |
| `block_size` | `int` | N | Block bootstrap 블록 크기 (기본값 20 거래일) |
| `correction_method` | `str` | N | "bonferroni" / "holm" / "bh_fdr" / "romano_wolf" |
| `strategy_dev_log` | `list[dict]` | N | 전략 개발 히스토리 (시도일, 전략명, 결과) |

**전처리**:
1. 수익률 시계열 NaN 검증 → 결측 > 5% 전략은 제외
2. 벤치마크와 전략 수익률 날짜 정렬 (교집합)
3. 초과수익률 계산: `excess_returns = strategy_returns - benchmark_returns`

---

## E2. Algorithm - 복사→구현 가능 의사코드 with REAL formulas

```python
import numpy as np
from scipy import stats

# === Bonferroni 보정 ===
def bonferroni_correction(p_values: list[float], alpha: float = 0.05) -> list[dict]:
    """Bonferroni 다중비교 보정: adjusted_alpha = alpha / n"""
    n = len(p_values)
    adjusted_alpha = alpha / n
    results = []
    for i, p in enumerate(p_values):
        results.append({
            'strategy_idx': i,
            'raw_p': p,
            'adjusted_alpha': adjusted_alpha,
            'significant': p < adjusted_alpha
        })
    return results

# === Holm-Bonferroni 단계별 보정 ===
def holm_correction(p_values: list[float], alpha: float = 0.05) -> list[dict]:
    """Holm stepdown: 정렬 후 단계별 alpha 조정"""
    n = len(p_values)
    sorted_idx = np.argsort(p_values)
    results = [None] * n
    stopped = False
    for rank, idx in enumerate(sorted_idx):
        adjusted_alpha = alpha / (n - rank)
        if not stopped and p_values[idx] < adjusted_alpha:
            significant = True
        else:
            significant = False
            stopped = True  # 첫 비기각 이후 모든 후속 가설 비기각 (FWER 보존)
        results[idx] = {
            'strategy_idx': idx,
            'raw_p': p_values[idx],
            'adjusted_alpha': adjusted_alpha,
            'rank': rank + 1,
            'significant': significant
        }
    return results

# === White's Reality Check ===
def whites_reality_check(
    excess_returns: np.ndarray,  # shape: (T, N) T=기간, N=전략 수
    n_bootstrap: int = 10_000,
    block_size: int = 20
) -> dict:
    """
    H0: 최고 전략의 성과가 우연에 의한 것
    검정통계량: V_bar = max_k (mean(f_k))  (f_k = 전략 k의 초과수익)
    Bootstrap 분포에서 p-value 산출
    """
    T, N = excess_returns.shape
    # 실제 검정통계량
    mean_excess = excess_returns.mean(axis=0)  # 각 전략 평균 초과수익
    V_bar = np.max(mean_excess)                # 최고 전략의 평균 초과수익

    # Block Bootstrap으로 null 분포 생성
    V_bar_bootstrap = np.zeros(n_bootstrap)
    for b in range(n_bootstrap):
        # 블록 부트스트랩 인덱스 생성
        n_blocks = T // block_size + 1
        block_starts = np.random.randint(0, T - block_size, size=n_blocks)
        boot_idx = np.concatenate([np.arange(s, s + block_size) for s in block_starts])[:T]

        boot_excess = excess_returns[boot_idx, :]
        # 센터링: H0 하에서 평균 초과수익 = 0
        boot_mean = boot_excess.mean(axis=0) - mean_excess
        V_bar_bootstrap[b] = np.max(boot_mean)

    # p-value: bootstrap 분포에서 실제 V_bar 이상 비율
    p_value = np.mean(V_bar_bootstrap >= V_bar)
    return {
        'test': "White's Reality Check",
        'V_bar': float(V_bar),
        'p_value': float(p_value),
        'significant': p_value < 0.05,
        'best_strategy_idx': int(np.argmax(mean_excess)),
        'n_bootstrap': n_bootstrap
    }

# === Hansen's SPA (Superior Predictive Ability) Test ===
def hansens_spa_test(
    excess_returns: np.ndarray,
    n_bootstrap: int = 10_000,
    block_size: int = 20
) -> dict:
    """
    White's RC 개선: 성과 나쁜 전략 제외하여 검정력 향상
    T_SPA = max_k (sqrt(T) * mean(f_k) / std(f_k))
    """
    T, N = excess_returns.shape
    mean_excess = excess_returns.mean(axis=0)
    std_excess = excess_returns.std(axis=0, ddof=1)
    std_excess[std_excess == 0] = 1e-10  # 0 방지

    # 표준화 검정통계량
    t_stats = np.sqrt(T) * mean_excess / std_excess
    T_SPA = np.max(t_stats)

    # Bootstrap (성과 나쁜 전략 제외 후 센터링)
    # 양수 평균만 센터링 (SPA의 핵심 차이점)
    centering = np.where(mean_excess > 0, mean_excess, 0)

    T_SPA_bootstrap = np.zeros(n_bootstrap)
    for b in range(n_bootstrap):
        n_blocks = T // block_size + 1
        block_starts = np.random.randint(0, T - block_size, size=n_blocks)
        boot_idx = np.concatenate([np.arange(s, s + block_size) for s in block_starts])[:T]

        boot_excess = excess_returns[boot_idx, :]
        boot_mean = boot_excess.mean(axis=0) - centering
        boot_std = boot_excess.std(axis=0, ddof=1)
        boot_std[boot_std == 0] = 1e-10
        boot_t = np.sqrt(T) * boot_mean / boot_std
        T_SPA_bootstrap[b] = np.max(boot_t)

    p_value = np.mean(T_SPA_bootstrap >= T_SPA)
    return {
        'test': "Hansen's SPA",
        'T_SPA': float(T_SPA),
        'p_value': float(p_value),
        'significant': p_value < 0.05,
        'best_strategy_idx': int(np.argmax(t_stats)),
        'n_bootstrap': n_bootstrap
    }

# === Romano-Wolf Stepdown ===
def romano_wolf_stepdown(
    excess_returns: np.ndarray,
    alpha: float = 0.05,
    n_bootstrap: int = 10_000,
    block_size: int = 20
) -> list[dict]:
    """개별 전략 유의성을 순차적으로 검정 (FWE 제어)"""
    T, N = excess_returns.shape
    mean_excess = excess_returns.mean(axis=0)
    std_excess = excess_returns.std(axis=0, ddof=1)
    std_excess[std_excess == 0] = 1e-10
    t_stats = np.sqrt(T) * mean_excess / std_excess

    # 내림차순 정렬
    sorted_idx = np.argsort(-t_stats)
    results = [None] * N
    rejected = set()

    for step in range(N):
        remaining = [i for i in sorted_idx if i not in rejected]
        if not remaining:
            break
        # Bootstrap max-t 분포 (remaining 전략들에 대해)
        max_t_boot = np.zeros(n_bootstrap)
        for b in range(n_bootstrap):
            n_blocks = T // block_size + 1
            block_starts = np.random.randint(0, T - block_size, size=n_blocks)
            boot_idx = np.concatenate([np.arange(s, s + block_size) for s in block_starts])[:T]
            boot_excess = excess_returns[boot_idx][:, remaining]
            boot_mean = boot_excess.mean(axis=0) - mean_excess[remaining]
            boot_std = boot_excess.std(axis=0, ddof=1)
            boot_std[boot_std == 0] = 1e-10
            boot_t = np.sqrt(T) * boot_mean / boot_std
            max_t_boot[b] = np.max(boot_t)

        critical_value = np.quantile(max_t_boot, 1 - alpha)
        current_idx = remaining[0]
        if t_stats[current_idx] > critical_value:
            rejected.add(current_idx)
            results[current_idx] = {'strategy_idx': current_idx, 'significant': True, 'step': step + 1}
        else:
            for idx in remaining:
                if results[idx] is None:
                    results[idx] = {'strategy_idx': idx, 'significant': False, 'step': step + 1}
            break
    return [r for r in results if r is not None]
```

---

## E3. Output - @dataclass, confidence, 소비자

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class StrategyTestResult:
    strategy_name: str
    raw_p_value: float
    adjusted_p_value: float
    significant: bool
    correction_method: str

@dataclass
class DataSnoopingReport:
    """Data Snooping 보정 최종 리포트"""
    n_strategies_tested: int = 0
    n_strategies_selected: int = 0
    n_significant_after_correction: int = 0
    correction_method: str = ""
    whites_rc_p_value: float = 0.0
    hansens_spa_p_value: float = 0.0
    romano_wolf_results: list[dict] = field(default_factory=list)
    individual_results: list[StrategyTestResult] = field(default_factory=list)
    confidence: float = 0.0  # 0.0~1.0
    passed: bool = False
    dev_history_logged: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

    def compute_confidence(self):
        """SPA/RC 검정 통과 + 개별 전략 유의성 기반"""
        if self.hansens_spa_p_value > 0:
            self.confidence = 1.0 - self.hansens_spa_p_value
        elif self.whites_rc_p_value > 0:
            self.confidence = 1.0 - self.whites_rc_p_value
        self.passed = (self.confidence >= 0.95) and (self.n_significant_after_correction > 0)
```

**소비자**: 전략 선정 파이프라인, 리스크 관리 대시보드, 전략 승인 위원회 보고서

---

## E4. Class/API Design - class with methods

```python
class DataSnoopingCorrector:
    """Data Snooping & Multiple Testing 보정 통합 클래스"""

    def __init__(self, alpha: float = 0.05, n_bootstrap: int = 10_000, block_size: int = 20):
        self.alpha = alpha
        self.n_bootstrap = n_bootstrap
        self.block_size = block_size
        self._dev_history: list[dict] = []

    # --- 다중비교 보정 ---
    def bonferroni(self, p_values: list[float]) -> list[dict]:
        """Bonferroni 보정 적용"""
        ...

    def holm(self, p_values: list[float]) -> list[dict]:
        """Holm-Bonferroni stepdown 보정"""
        ...

    def bh_fdr(self, p_values: list[float]) -> list[dict]:
        """Benjamini-Hochberg FDR 보정"""
        ...

    # --- Bootstrap 기반 검정 ---
    def whites_reality_check(self, excess_returns: np.ndarray) -> dict:
        """White's Reality Check"""
        ...

    def hansens_spa(self, excess_returns: np.ndarray) -> dict:
        """Hansen's SPA 검정"""
        ...

    def romano_wolf(self, excess_returns: np.ndarray) -> list[dict]:
        """Romano-Wolf stepdown 개별 전략 검정"""
        ...

    # --- 전략 개발 히스토리 ---
    def log_strategy_attempt(self, strategy_name: str, result: str, date: datetime):
        """전략 시도 기록"""
        ...

    def get_effective_alpha(self) -> float:
        """실질 유의수준 = alpha / n_tested"""
        ...

    # --- 통합 검증 ---
    def full_correction(self, strategy_returns: DataFrame, benchmark_returns: Series) -> DataSnoopingReport:
        """전체 data snooping 보정 파이프라인"""
        ...
```

---

## E5. Tech Stack Dependency

| 구성 요소 | 기술 | 버전 | 용도 |
|-----------|------|------|------|
| 통계 검정 | SciPy `stats` | ≥1.11 | p-value 계산, 분포 함수 |
| Bootstrap 엔진 | NumPy | ≥1.24 | Block bootstrap, 난수 생성 |
| 데이터 처리 | Pandas | ≥2.0 | 수익률 시계열 정렬/필터 |
| 시각화 | Matplotlib / Plotly | - | Bootstrap 분포, p-value 히스토그램 |
| 개발 히스토리 DB | SQLite / PostgreSQL | - | 전략 시도 기록 저장 |
| SPEC 참조 | LOCK §14 | - | 기술스택 범위 제약 |

---

## E6. Performance Requirements

| 지표 | 목표 | 허용 한계 | 측정 방법 |
|------|------|-----------|-----------|
| White's RC (10,000 bootstrap) | < 30s | < 120s | N=100 전략, T=2,520일 |
| Hansen's SPA (10,000 bootstrap) | < 45s | < 180s | N=100 전략, T=2,520일 |
| Romano-Wolf stepdown | < 120s | < 300s | N=100 전략 순차 검정 |
| Bonferroni / Holm 보정 | < 1ms | < 10ms | p-value 리스트 처리 |
| 메모리 사용량 | < 2GB | < 4GB | 10,000 bootstrap × 100 전략 |
| Bootstrap 재현성 | 100% | 100% | 동일 seed → 동일 결과 |

---

## E7. Error Handling

| 에러 코드 | 상황 | 처리 방법 | 심각도 |
|-----------|------|-----------|--------|
| `DSN-001` | 전략 수익률 NaN > 5% | 해당 전략 제외, WARNING 로그 | WARNING |
| `DSN-002` | n_strategies_tested 미기록 | 전략 개발 히스토리에서 추정, WARNING | WARNING |
| `DSN-003` | Bootstrap 메모리 초과 | block_size 증가 또는 n_bootstrap 축소 | WARNING |
| `DSN-004` | 모든 전략 초과수익 ≤ 0 | "유의한 전략 없음" 보고, 정상 종료 | INFO |
| `DSN-005` | 전략 개발 히스토리 미기록 | 보정 불완전 경고, 최소 n_selected 기반 보정 | CRITICAL |
| `DSN-006` | Bootstrap 수렴 실패 | n_bootstrap 2배 증가 후 재실행 | WARNING |

---

## E8. Test Criteria - Unit / Integration / Acceptance

**Unit Tests**:
- `test_bonferroni_100_strategies`: 100개 p-value → adjusted_alpha = 0.0005 확인
- `test_holm_stepdown_ordering`: 정렬 순서 및 단계별 alpha 정확성
- `test_whites_rc_known_null`: 순수 랜덤 전략 → p-value > 0.05 확인
- `test_whites_rc_known_signal`: 확실한 시그널 전략 → p-value < 0.05 확인
- `test_hansens_spa_better_power`: 동일 데이터에서 SPA p-value ≤ RC p-value 확인

**Integration Tests**:
- `test_full_correction_pipeline`: 전략 수익률 → 보정 → 리포트 생성 전체 흐름
- `test_dev_history_integration`: 전략 시도 기록 → 실질 유의수준 보정 반영
- `test_bootstrap_reproducibility`: 동일 seed → 동일 p-value 재현

**Acceptance Tests**:
- 100개 순수 랜덤 전략 중 유의한 전략 0개 (FWE 제어 확인)
- 실제 알파 전략 포함 시 해당 전략만 유의하게 식별
- 전략 개발 히스토리 기록 → 보정된 유의수준 적용 확인

---

## E9. LOCK References

| LOCK 항목 | 참조 | 연관 |
|-----------|------|------|
| SPEC §14 | 기술스택 범위 | SciPy, NumPy 사용 범위 내 |
| SPEC §5 | 백테스트 진실성 | Data Snooping 보정 = 핵심 요구사항 |
| B-3 #10 | 다중비교 보정 | `DataSnoopingCorrector.bonferroni/holm/bh_fdr()` |
| B-3 #11 | White's Reality Check | `DataSnoopingCorrector.whites_reality_check()` |
| B-3 #12 | Hansen's SPA 테스트 | `DataSnoopingCorrector.hansens_spa()` |
| B-3 #13 | 전략 개발 히스토리 | `DataSnoopingCorrector.log_strategy_attempt()` |

---
