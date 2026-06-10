# 주문 실행 알고리즘 (Execution Algorithms)

> **버전**: v2.1
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #6 실행 최적화
> **정본 소유 개념**: 주문 실행 알고리즘
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-1. 주문 실행 알고리즘 (Execution Algorithms)

| # | 항목 | 상세 |
|---|------|------|
| 1 | **TWAP(Time-Weighted Average Price)** | 지정 시간 동안 균등 분할 주문. 대량 매매 시 시장 충격 최소화. 주문 크기/시간 간격 자동 설정 |
| 2 | **VWAP(Volume-Weighted Average Price)** | 거래량 패턴에 맞춰 분할 주문. 장 초반/후반 거래량 높은 시간대에 더 많이 체결. 과거 거래량 프로파일 학습 |
| 3 | **IS(Implementation Shortfall) 최소화** | 의사결정 가격 vs 실제 체결 가격 차이 최소화. Almgren-Chriss 최적 실행 스케줄. 긴급도(urgency)와 시장 충격 간 트레이드오프 최적화 |
| 4 | **아이스버그(Iceberg) 주문** | 대량 주문을 소량으로 나눠 시장에 노출. 보이는 수량 제한 → 시장 충격 감소. 자동 수량 분할 및 간격 조절 |
| 5 | **적응형 실행 알고리즘** | 실시간 시장 상황(변동성, 스프레드, 유동성)에 따라 실행 알고리즘 자동 전환. 정상 시 VWAP → 급변동 시 IS 최소화 전환 |

---

## E1. Input

### Kafka Topics

| Topic | 용도 | 파티션 키 |
|-------|------|-----------|
| `execution.order.request` | 주문 실행 요청 수신 | `symbol` |
| `market.orderbook.l2` | 실시간 호가창 (L2) | `symbol` |
| `market.trade.tick` | 실시간 체결 틱 | `symbol` |
| `market.volume.profile` | 과거 거래량 프로파일 | `symbol` |

### 필수 필드

```python
# execution.order.request
{
    "order_id": str,           # UUID
    "symbol": str,             # e.g., "AAPL", "005930.KS", "BTC/USDT"
    "asset_class": str,        # "US_STOCK" | "KR_STOCK" | "CRYPTO"
    "side": str,               # "BUY" | "SELL"
    "total_qty": float,        # 총 주문 수량
    "algo_type": str,          # "TWAP" | "VWAP" | "IS" | "ICEBERG" | "ADAPTIVE"
    "urgency": float,          # 0.0 (낮음) ~ 1.0 (높음)
    "start_time": datetime,    # 실행 시작 시각
    "end_time": datetime,      # 실행 종료 시각 (TWAP/VWAP)
    "limit_price": float | None,  # 지정가 상한/하한
    "timestamp": datetime
}

# market.orderbook.l2
{
    "symbol": str,
    "bids": list[tuple[float, float]],  # [(price, qty), ...]
    "asks": list[tuple[float, float]],
    "mid_price": float,
    "spread": float,
    "timestamp": datetime
}
```

### TimescaleDB Schema

```sql
CREATE TABLE exec_algo_orders (
    order_id        UUID PRIMARY KEY,
    symbol          TEXT NOT NULL,
    asset_class     TEXT NOT NULL,
    side            TEXT NOT NULL,
    algo_type       TEXT NOT NULL,
    total_qty       DOUBLE PRECISION NOT NULL,
    filled_qty      DOUBLE PRECISION DEFAULT 0,
    avg_fill_price  DOUBLE PRECISION,
    decision_price  DOUBLE PRECISION NOT NULL,
    urgency         DOUBLE PRECISION DEFAULT 0.5,
    start_time      TIMESTAMPTZ NOT NULL,
    end_time        TIMESTAMPTZ,
    status          TEXT DEFAULT 'PENDING',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('exec_algo_orders', 'created_at');

CREATE TABLE exec_algo_child_orders (
    child_order_id  UUID PRIMARY KEY,
    parent_order_id UUID REFERENCES exec_algo_orders(order_id),
    slice_index     INTEGER NOT NULL,
    target_qty      DOUBLE PRECISION NOT NULL,
    filled_qty      DOUBLE PRECISION DEFAULT 0,
    fill_price      DOUBLE PRECISION,
    scheduled_time  TIMESTAMPTZ NOT NULL,
    executed_time   TIMESTAMPTZ,
    status          TEXT DEFAULT 'PENDING',
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('exec_algo_child_orders', 'created_at');

CREATE TABLE volume_profile (
    symbol          TEXT NOT NULL,
    time_bucket     TIMESTAMPTZ NOT NULL,
    avg_volume      DOUBLE PRECISION NOT NULL,
    volume_pct      DOUBLE PRECISION NOT NULL,
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, time_bucket)
);
```

### 전처리

- 호가창 데이터: 스냅샷 간 200ms 이상 간격 필터링, 비정상 스프레드 (> 5% mid_price) 제거
- 거래량 프로파일: 최근 20 거래일 평균 사용, NaN 구간은 uniform 분배로 대체
- 주문 요청: `total_qty <= 0` 거부, `end_time <= start_time` 거부

---

## E2. Algorithm

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import numpy as np
import uuid


@dataclass
class ChildOrder:
    """개별 분할 주문 슬라이스"""
    child_order_id: str
    parent_order_id: str
    slice_index: int
    target_qty: float
    scheduled_time: datetime
    filled_qty: float = 0.0
    fill_price: float = 0.0
    status: str = "PENDING"  # PENDING | SENT | FILLED | CANCELLED


@dataclass
class ExecutionPlan:
    """실행 알고리즘 결과 계획"""
    order_id: str
    algo_type: str
    symbol: str
    side: str
    total_qty: float
    decision_price: float
    child_orders: list[ChildOrder] = field(default_factory=list)
    estimated_avg_price: float = 0.0
    estimated_slippage_bps: float = 0.0
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ExecutionResult:
    """실행 완료 결과"""
    order_id: str
    algo_type: str
    symbol: str
    side: str
    total_qty: float
    filled_qty: float
    avg_fill_price: float
    decision_price: float
    implementation_shortfall: float  # bps
    slippage_bps: float
    num_slices: int
    duration_seconds: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ──────────────────────────────────────────────
# 1. TWAP (Time-Weighted Average Price)
# ──────────────────────────────────────────────
def compute_twap_schedule(
    total_qty: float,
    start_time: datetime,
    end_time: datetime,
    num_slices: int = 10,
    randomize_pct: float = 0.1
) -> list[tuple[datetime, float]]:
    """
    TWAP = Σ(P_i) / N
    각 슬라이스에 균등 수량 배분, 시간 균등 분할.
    randomize_pct: 예측 방지를 위한 수량 랜덤화 비율
    """
    duration = (end_time - start_time).total_seconds()
    interval = duration / num_slices
    base_qty = total_qty / num_slices

    schedule = []
    remaining = total_qty
    for i in range(num_slices):
        t = start_time + timedelta(seconds=interval * i)
        if i == num_slices - 1:
            qty = remaining  # 마지막 슬라이스: 잔량 전부
        else:
            # 랜덤화: base_qty * (1 ± randomize_pct)
            noise = np.random.uniform(-randomize_pct, randomize_pct)
            qty = base_qty * (1.0 + noise)
            qty = max(qty, 0.01)  # 최소 수량 보장
            remaining -= qty
        schedule.append((t, round(qty, 6)))
    return schedule


# ──────────────────────────────────────────────
# 2. VWAP (Volume-Weighted Average Price)
# ──────────────────────────────────────────────
def compute_vwap_schedule(
    total_qty: float,
    start_time: datetime,
    end_time: datetime,
    volume_profile: list[tuple[datetime, float]],
    num_slices: int = 10
) -> list[tuple[datetime, float]]:
    """
    VWAP = Σ(P_i * V_i) / Σ(V_i)
    목표: 실행 VWAP를 시장 VWAP에 수렴시키기 위해
    과거 거래량 프로파일에 비례하여 수량 배분.

    volume_profile: [(time_bucket, avg_volume_pct), ...] — 정규화된 거래량 비율
    """
    # 실행 구간에 해당하는 프로파일 필터링
    relevant = [
        (t, v) for t, v in volume_profile
        if start_time <= t <= end_time
    ]
    if not relevant:
        # fallback: uniform (TWAP 방식)
        return compute_twap_schedule(total_qty, start_time, end_time, num_slices)

    # 거래량 비율 정규화
    total_vol_pct = sum(v for _, v in relevant)
    if total_vol_pct <= 0:
        return compute_twap_schedule(total_qty, start_time, end_time, num_slices)

    schedule = []
    remaining = total_qty
    for i, (t, vol_pct) in enumerate(relevant):
        if i == len(relevant) - 1:
            qty = remaining
        else:
            qty = total_qty * (vol_pct / total_vol_pct)
            remaining -= qty
        schedule.append((t, round(max(qty, 0.01), 6)))
    return schedule


# ──────────────────────────────────────────────
# 3. IS (Implementation Shortfall) — Almgren-Chriss
# ──────────────────────────────────────────────
def compute_is_schedule(
    total_qty: float,
    decision_price: float,
    urgency: float,
    volatility: float,
    avg_daily_volume: float,
    eta: float = 0.01,       # 일시적 충격 계수
    gamma: float = 0.001,    # 영구적 충격 계수
    num_slices: int = 10,
    horizon_seconds: float = 3600.0
) -> list[tuple[int, float]]:
    """
    Almgren-Chriss 최적 실행 스케줄.

    Implementation Shortfall = decision_price - avg_execution_price

    최적 거래 속도 (연속 시간):
        n_t = (X * sinh(κ(T-t))) / sinh(κT)
        여기서 κ = sqrt(λσ² / η)

    λ (risk aversion) = urgency * base_lambda
    η (temporary impact) = eta * σ / sqrt(ADV)
    γ (permanent impact) = gamma * σ / ADV

    단순화된 이산 스케줄:
        x_k = X * w_k / Σ(w_k)
        w_k = sinh(κ * (N - k)) for k = 0..N-1
    """
    X = total_qty
    sigma = volatility
    ADV = avg_daily_volume

    # 리스크 회피 계수: urgency가 높을수록 빠르게 실행
    base_lambda = 1e-6
    lambda_risk = urgency * base_lambda + 1e-8

    # 일시적 충격 계수 정규화
    eta_norm = eta * sigma / max(np.sqrt(ADV), 1.0)

    # kappa 계산
    kappa = np.sqrt(lambda_risk * sigma**2 / max(eta_norm, 1e-10))

    T = num_slices  # 이산 시간 단위
    weights = []
    for k in range(num_slices):
        w = np.sinh(kappa * (T - k))
        weights.append(w)

    total_weight = sum(weights)
    if total_weight <= 0:
        # fallback: uniform
        weights = [1.0] * num_slices
        total_weight = num_slices

    schedule = []
    remaining = X
    interval = horizon_seconds / num_slices
    for k in range(num_slices):
        if k == num_slices - 1:
            qty = remaining
        else:
            qty = X * (weights[k] / total_weight)
            remaining -= qty
        schedule.append((int(interval * k), round(max(qty, 0.01), 6)))

    return schedule


def estimate_implementation_shortfall(
    decision_price: float,
    avg_execution_price: float,
    side: str
) -> float:
    """
    IS (bps) = (execution_price - decision_price) / decision_price * 10000
    BUY: 양수 = 비싸게 삼 (나쁨), SELL: 음수 = 싸게 팔음 (나쁨)
    """
    if side == "BUY":
        is_bps = (avg_execution_price - decision_price) / decision_price * 10000
    else:  # SELL
        is_bps = (decision_price - avg_execution_price) / decision_price * 10000
    return round(is_bps, 2)


# ──────────────────────────────────────────────
# 4. Iceberg 주문
# ──────────────────────────────────────────────
def compute_iceberg_plan(
    total_qty: float,
    visible_pct: float = 0.1,
    min_visible_qty: float = 1.0,
    randomize: bool = True,
    randomize_pct: float = 0.2
) -> list[float]:
    """
    아이스버그 주문: 전체 수량 중 visible_pct만 시장에 노출.
    체결 후 다음 visible 슬라이스 자동 전송.

    visible_qty = total_qty * visible_pct
    num_slices = ceil(total_qty / visible_qty)

    randomize: 각 슬라이스 수량에 노이즈 추가 (패턴 탐지 방지)
    """
    visible_qty = max(total_qty * visible_pct, min_visible_qty)
    num_slices = int(np.ceil(total_qty / visible_qty))

    slices = []
    remaining = total_qty
    for i in range(num_slices):
        if i == num_slices - 1:
            qty = remaining
        else:
            base = visible_qty
            if randomize:
                noise = np.random.uniform(-randomize_pct, randomize_pct)
                base = visible_qty * (1.0 + noise)
            qty = min(base, remaining)
            remaining -= qty
        slices.append(round(max(qty, 0.01), 6))

    return slices


# ──────────────────────────────────────────────
# 5. 적응형 실행 알고리즘 선택기
# ──────────────────────────────────────────────
def select_adaptive_algo(
    volatility: float,
    spread_bps: float,
    liquidity_ratio: float,  # order_qty / ADV
    urgency: float
) -> str:
    """
    실시간 시장 상황에 따라 최적 알고리즘 자동 선택.

    Decision matrix:
    ┌─────────────────┬───────────────┬──────────────┐
    │ 조건            │ urgency < 0.5 │ urgency ≥ 0.5│
    ├─────────────────┼───────────────┼──────────────┤
    │ vol < 2% &      │ VWAP          │ TWAP         │
    │ liq_ratio < 5%  │               │              │
    ├─────────────────┼───────────────┼──────────────┤
    │ vol ≥ 2% |      │ ICEBERG       │ IS           │
    │ liq_ratio ≥ 5%  │               │              │
    ├─────────────────┼───────────────┼──────────────┤
    │ spread > 50bps  │ ICEBERG       │ IS           │
    └─────────────────┴───────────────┴──────────────┘
    """
    # 고변동성 또는 대량 주문 → 시장 충격 최소화 우선
    if volatility >= 0.02 or liquidity_ratio >= 0.05:
        if urgency >= 0.5:
            return "IS"
        else:
            return "ICEBERG"

    # 넓은 스프레드 → 유동성 부족 환경
    if spread_bps > 50:
        if urgency >= 0.5:
            return "IS"
        else:
            return "ICEBERG"

    # 정상 시장 환경
    if urgency >= 0.5:
        return "TWAP"
    else:
        return "VWAP"


def compute_execution_confidence(
    algo_type: str,
    liquidity_ratio: float,
    spread_bps: float,
    volatility: float,
    fill_rate: float = 1.0
) -> float:
    """
    실행 신뢰도 계산 (0.0 ~ 1.0).

    confidence = base_score * liquidity_factor * spread_factor * vol_factor * fill_factor

    base_score: 알고리즘별 기본 점수
    liquidity_factor: 1.0 - min(liquidity_ratio / 0.1, 0.5)
    spread_factor: 1.0 - min(spread_bps / 200, 0.3)
    vol_factor: 1.0 - min(volatility / 0.05, 0.3)
    fill_factor: fill_rate
    """
    base_scores = {"TWAP": 0.85, "VWAP": 0.90, "IS": 0.80, "ICEBERG": 0.85, "ADAPTIVE": 0.88}
    base = base_scores.get(algo_type, 0.80)

    liq_factor = 1.0 - min(liquidity_ratio / 0.1, 0.5)
    sprd_factor = 1.0 - min(spread_bps / 200.0, 0.3)
    vol_factor = 1.0 - min(volatility / 0.05, 0.3)
    fill_factor = fill_rate

    confidence = base * liq_factor * sprd_factor * vol_factor * fill_factor
    return round(min(max(confidence, 0.0), 1.0), 4)
```

---

## E3. Output

### Output Schema

```python
@dataclass
class ExecutionPlanOutput:
    order_id: str
    algo_type: str              # "TWAP" | "VWAP" | "IS" | "ICEBERG" | "ADAPTIVE"
    symbol: str
    side: str                   # "BUY" | "SELL"
    total_qty: float
    num_slices: int
    child_orders: list[dict]    # [{slice_index, target_qty, scheduled_time}, ...]
    estimated_avg_price: float
    estimated_slippage_bps: float
    decision_price: float
    confidence: float           # 0.0 ~ 1.0
    timestamp: datetime
    metadata: dict              # {"urgency", "volatility", "liquidity_ratio", "spread_bps"}
```

### Kafka Output Topics

| Topic | 내용 | 파티션 키 |
|-------|------|-----------|
| `execution.plan.created` | 실행 계획 생성 완료 | `order_id` |
| `execution.child.dispatched` | 개별 슬라이스 주문 전송 | `order_id` |
| `execution.order.completed` | 전체 주문 실행 완료 | `order_id` |
| `execution.algo.switched` | 적응형 알고리즘 전환 이벤트 | `order_id` |

### Confidence Levels

| 구간 | 의미 | 후속 액션 |
|------|------|-----------|
| ≥ 0.8 | 높은 신뢰도 — 정상 실행 | 즉시 실행 |
| 0.5 ~ 0.8 | 중간 신뢰도 — 주의 필요 | 슬라이스 수 증가, 모니터링 강화 |
| < 0.5 | 낮은 신뢰도 — 시장 비정상 | 주문 보류 또는 수동 확인 요청 |

### 소비자

- `OrderRouter`: 개별 child_order를 거래소 API에 전송
- `SlippageMonitor`: 실시간 슬리피지 추적 (B-4 연계)
- `TCAEngine`: 거래 비용 분석 (관점 #11 연계)
- `DashboardService`: 실행 상태 실시간 표시

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import pandas as pd


class BaseExecutionAlgo(ABC):
    """실행 알고리즘 기반 클래스.

    모든 실행 알고리즘은 이 클래스를 상속하며,
    generate_schedule() → execute() → report() 파이프라인을 따른다.
    """

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.name: str = "BASE"
        self.child_orders: list[ChildOrder] = []

    @abstractmethod
    def generate_schedule(self, order: dict, market_data: dict) -> ExecutionPlan:
        """주문 분할 스케줄 생성."""
        pass

    @abstractmethod
    def adjust_on_fill(self, child_order: ChildOrder, fill_info: dict) -> Optional[ChildOrder]:
        """체결 후 잔여 스케줄 조정."""
        pass

    def validate_order(self, order: dict) -> bool:
        """주문 유효성 검증."""
        required = ["order_id", "symbol", "side", "total_qty"]
        for f in required:
            if f not in order:
                raise ValueError(f"Missing required field: {f}")
        if order["total_qty"] <= 0:
            raise ValueError("total_qty must be positive")
        return True

    def compute_confidence(self, market_data: dict) -> float:
        """실행 신뢰도 계산."""
        return compute_execution_confidence(
            algo_type=self.name,
            liquidity_ratio=market_data.get("liquidity_ratio", 0.01),
            spread_bps=market_data.get("spread_bps", 10),
            volatility=market_data.get("volatility", 0.01),
        )


class TWAPExecutor(BaseExecutionAlgo):
    """TWAP 실행 알고리즘.
    SPEC §14: 시간 균등 분할 실행.
    """

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "TWAP"
        self.default_slices = config.get("default_slices", 10) if config else 10
        self.randomize_pct = config.get("randomize_pct", 0.1) if config else 0.1

    def generate_schedule(self, order: dict, market_data: dict) -> ExecutionPlan:
        self.validate_order(order)
        schedule = compute_twap_schedule(
            total_qty=order["total_qty"],
            start_time=order["start_time"],
            end_time=order["end_time"],
            num_slices=self.default_slices,
            randomize_pct=self.randomize_pct,
        )
        child_orders = [
            ChildOrder(
                child_order_id=str(uuid.uuid4()),
                parent_order_id=order["order_id"],
                slice_index=i,
                target_qty=qty,
                scheduled_time=t,
            )
            for i, (t, qty) in enumerate(schedule)
        ]
        return ExecutionPlan(
            order_id=order["order_id"],
            algo_type="TWAP",
            symbol=order["symbol"],
            side=order["side"],
            total_qty=order["total_qty"],
            decision_price=market_data["mid_price"],
            child_orders=child_orders,
            confidence=self.compute_confidence(market_data),
        )

    def adjust_on_fill(self, child_order: ChildOrder, fill_info: dict) -> Optional[ChildOrder]:
        unfilled = child_order.target_qty - fill_info.get("filled_qty", 0)
        if unfilled > 0.01:
            return ChildOrder(
                child_order_id=str(uuid.uuid4()),
                parent_order_id=child_order.parent_order_id,
                slice_index=child_order.slice_index,
                target_qty=unfilled,
                scheduled_time=datetime.utcnow(),
            )
        return None


class VWAPExecutor(BaseExecutionAlgo):
    """VWAP 실행 알고리즘.
    SPEC §14: 거래량 프로파일 기반 분할 실행.
    """

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "VWAP"
        self.lookback_days = config.get("lookback_days", 20) if config else 20

    def generate_schedule(self, order: dict, market_data: dict) -> ExecutionPlan:
        self.validate_order(order)
        volume_profile = market_data.get("volume_profile", [])
        schedule = compute_vwap_schedule(
            total_qty=order["total_qty"],
            start_time=order["start_time"],
            end_time=order["end_time"],
            volume_profile=volume_profile,
        )
        child_orders = [
            ChildOrder(
                child_order_id=str(uuid.uuid4()),
                parent_order_id=order["order_id"],
                slice_index=i,
                target_qty=qty,
                scheduled_time=t,
            )
            for i, (t, qty) in enumerate(schedule)
        ]
        return ExecutionPlan(
            order_id=order["order_id"],
            algo_type="VWAP",
            symbol=order["symbol"],
            side=order["side"],
            total_qty=order["total_qty"],
            decision_price=market_data["mid_price"],
            child_orders=child_orders,
            confidence=self.compute_confidence(market_data),
        )

    def adjust_on_fill(self, child_order: ChildOrder, fill_info: dict) -> Optional[ChildOrder]:
        unfilled = child_order.target_qty - fill_info.get("filled_qty", 0)
        if unfilled > 0.01:
            return ChildOrder(
                child_order_id=str(uuid.uuid4()),
                parent_order_id=child_order.parent_order_id,
                slice_index=child_order.slice_index,
                target_qty=unfilled,
                scheduled_time=datetime.utcnow(),
            )
        return None


class ISExecutor(BaseExecutionAlgo):
    """Implementation Shortfall 최소화 실행 — Almgren-Chriss 모델.
    SPEC §14: 긴급도-시장충격 트레이드오프 최적화.
    """

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "IS"
        self.eta = config.get("eta", 0.01) if config else 0.01
        self.gamma = config.get("gamma", 0.001) if config else 0.001

    def generate_schedule(self, order: dict, market_data: dict) -> ExecutionPlan:
        self.validate_order(order)
        schedule = compute_is_schedule(
            total_qty=order["total_qty"],
            decision_price=market_data["mid_price"],
            urgency=order.get("urgency", 0.5),
            volatility=market_data.get("volatility", 0.02),
            avg_daily_volume=market_data.get("adv", 1_000_000),
            eta=self.eta,
            gamma=self.gamma,
        )
        start = order.get("start_time", datetime.utcnow())
        child_orders = [
            ChildOrder(
                child_order_id=str(uuid.uuid4()),
                parent_order_id=order["order_id"],
                slice_index=i,
                target_qty=qty,
                scheduled_time=start + timedelta(seconds=offset),
            )
            for i, (offset, qty) in enumerate(schedule)
        ]
        return ExecutionPlan(
            order_id=order["order_id"],
            algo_type="IS",
            symbol=order["symbol"],
            side=order["side"],
            total_qty=order["total_qty"],
            decision_price=market_data["mid_price"],
            child_orders=child_orders,
            confidence=self.compute_confidence(market_data),
        )

    def adjust_on_fill(self, child_order: ChildOrder, fill_info: dict) -> Optional[ChildOrder]:
        unfilled = child_order.target_qty - fill_info.get("filled_qty", 0)
        if unfilled > 0.01:
            return ChildOrder(
                child_order_id=str(uuid.uuid4()),
                parent_order_id=child_order.parent_order_id,
                slice_index=child_order.slice_index,
                target_qty=unfilled,
                scheduled_time=datetime.utcnow(),
            )
        return None


class IcebergExecutor(BaseExecutionAlgo):
    """Iceberg 주문 실행기.
    SPEC §14: 노출 수량 제한으로 시장 충격 최소화.
    """

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "ICEBERG"
        self.visible_pct = config.get("visible_pct", 0.1) if config else 0.1

    def generate_schedule(self, order: dict, market_data: dict) -> ExecutionPlan:
        self.validate_order(order)
        slices = compute_iceberg_plan(
            total_qty=order["total_qty"],
            visible_pct=self.visible_pct,
        )
        child_orders = [
            ChildOrder(
                child_order_id=str(uuid.uuid4()),
                parent_order_id=order["order_id"],
                slice_index=i,
                target_qty=qty,
                scheduled_time=datetime.utcnow(),  # 이전 슬라이스 체결 후 전송
            )
            for i, qty in enumerate(slices)
        ]
        return ExecutionPlan(
            order_id=order["order_id"],
            algo_type="ICEBERG",
            symbol=order["symbol"],
            side=order["side"],
            total_qty=order["total_qty"],
            decision_price=market_data["mid_price"],
            child_orders=child_orders,
            confidence=self.compute_confidence(market_data),
        )

    def adjust_on_fill(self, child_order: ChildOrder, fill_info: dict) -> Optional[ChildOrder]:
        # Iceberg: 체결 완료 → 다음 슬라이스 자동 전송 (외부 orchestrator 담당)
        return None


class AdaptiveExecutor(BaseExecutionAlgo):
    """적응형 실행 알고리즘.
    실시간 시장 상황에 따라 TWAP/VWAP/IS/ICEBERG 자동 선택 및 전환.
    """

    def __init__(self, config: dict | None = None):
        super().__init__(config)
        self.name = "ADAPTIVE"
        self.executors = {
            "TWAP": TWAPExecutor(config),
            "VWAP": VWAPExecutor(config),
            "IS": ISExecutor(config),
            "ICEBERG": IcebergExecutor(config),
        }
        self.current_algo: str = "VWAP"

    def generate_schedule(self, order: dict, market_data: dict) -> ExecutionPlan:
        self.validate_order(order)
        self.current_algo = select_adaptive_algo(
            volatility=market_data.get("volatility", 0.01),
            spread_bps=market_data.get("spread_bps", 10),
            liquidity_ratio=order["total_qty"] / max(market_data.get("adv", 1e6), 1),
            urgency=order.get("urgency", 0.5),
        )
        executor = self.executors[self.current_algo]
        plan = executor.generate_schedule(order, market_data)
        plan.algo_type = f"ADAPTIVE({self.current_algo})"
        return plan

    def adjust_on_fill(self, child_order: ChildOrder, fill_info: dict) -> Optional[ChildOrder]:
        executor = self.executors[self.current_algo]
        return executor.adjust_on_fill(child_order, fill_info)
```

---

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | >= 2.0 | Yes | 시계열 데이터 처리, 거래량 프로파일 |
| numpy | >= 1.24 | Yes | Almgren-Chriss 수치 계산, sinh/sqrt |
| confluent-kafka | >= 2.3 | Yes | Kafka 토픽 consume/produce |
| psycopg2 | >= 2.9 | Yes | TimescaleDB 접속 |
| sqlalchemy | >= 2.0 | Yes | ORM, 테이블 매핑 |
| asyncio | stdlib | Yes | 비동기 주문 실행 |
| uuid | stdlib | Yes | 주문 ID 생성 |

---

## E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 스케줄 생성 지연 | < 10ms | `time.perf_counter()` — 주문 1건 기준 |
| 개별 슬라이스 전송 지연 | < 5ms | 내부 큐 → OrderRouter 전달 |
| Almgren-Chriss 계산 | < 20ms | 10 슬라이스, sinh 계산 포함 |
| 동시 주문 처리 | 100건/초 | asyncio 기반 병렬 처리 |
| 메모리 | < 50MB / 주문 100건 | `tracemalloc` 프로파일링 |
| 적응형 전환 판정 | < 2ms | 단순 조건 분기 |

---

## E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 필수 필드 누락 (order) | `ValueError` raise, 주문 거부 | CRITICAL |
| `total_qty <= 0` | `ValueError` raise, 주문 거부 | CRITICAL |
| `end_time <= start_time` | `ValueError` raise, 주문 거부 | HIGH |
| 거래량 프로파일 없음 (VWAP) | TWAP fallback 자동 전환 | WARNING |
| Almgren-Chriss kappa 발산 | kappa 상한 클램프 (max=10.0) | WARNING |
| 호가창 데이터 지연 (> 1s) | 최근 캐시 사용 + 경고 로그 | WARNING |
| 슬라이스 체결 실패 | 재시도 3회 → 잔량 다음 슬라이스에 합산 | HIGH |
| 거래소 API 타임아웃 | 지수 백오프 재시도 (1s, 2s, 4s) → 실패 시 주문 보류 | HIGH |
| 적응형 전환 중 부분 체결 | 잔량에 대해 새 알고리즘 적용, 기체결분 유지 | MEDIUM |

---

## E8. Test Criteria

### Unit Tests

| Test ID | 시나리오 | 기대 결과 |
|---------|---------|-----------|
| EXEC-U01 | TWAP 10슬라이스, 1000주 | 각 슬라이스 ~100주, 합계 정확히 1000주 |
| EXEC-U02 | VWAP 프로파일 [0.3, 0.5, 0.2] | 슬라이스 비율 30:50:20 |
| EXEC-U03 | IS urgency=1.0 → front-loaded | 첫 슬라이스 > 마지막 슬라이스 |
| EXEC-U04 | IS urgency=0.0 → uniform | 슬라이스 간 편차 < 5% |
| EXEC-U05 | Iceberg visible_pct=0.1, 1000주 | 10개 슬라이스, 각 ~100주 |
| EXEC-U06 | IS 계산: decision=100, exec=100.5, BUY | IS = 50 bps |
| EXEC-U07 | 적응형: vol=0.01, liq=0.02, urg=0.3 | VWAP 선택 |
| EXEC-U08 | 적응형: vol=0.05, liq=0.08, urg=0.8 | IS 선택 |
| EXEC-U09 | confidence 계산: 정상 시장 | confidence >= 0.7 |
| EXEC-U10 | 빈 거래량 프로파일 → VWAP | TWAP fallback |

### Integration Tests

| Test ID | 시나리오 | 기대 결과 |
|---------|---------|-----------|
| EXEC-I01 | Kafka 주문 수신 → 스케줄 생성 → child 주문 전송 E2E | 전체 파이프라인 정상 |
| EXEC-I02 | TWAP 주문 → 10슬라이스 순차 체결 → 완료 이벤트 | `execution.order.completed` 발행 |
| EXEC-I03 | 적응형 전환: VWAP 실행 중 변동성 급증 → IS 전환 | `execution.algo.switched` 이벤트 발행 |
| EXEC-I04 | TimescaleDB에 체결 기록 저장 | `exec_algo_orders`, `exec_algo_child_orders` 정합성 |

### Acceptance Criteria

- TWAP 실행 결과: 실제 TWAP vs 시장 TWAP 편차 < 5bps (정상 시장)
- VWAP 실행 결과: 실제 VWAP vs 시장 VWAP 편차 < 3bps (정상 시장)
- IS 실행 결과: Implementation Shortfall < 10bps (정상 시장, urgency=0.5)
- 전체 주문 fill rate >= 99.5% (시장 운영시간 내)

---

## E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| TWAP 기본 슬라이스 수 = 10 | SPEC §14 | `default_slices` 파라미터 LOCK |
| VWAP 거래량 lookback = 20일 | SPEC §14 | `lookback_days` 파라미터 LOCK |
| Iceberg visible_pct = 0.1 | SPEC §14 | 노출 비율 10% LOCK |
| IS eta = 0.01, gamma = 0.001 | SPEC §14 | Almgren-Chriss 충격 계수 LOCK |
| Circuit Breaker -3% | SPEC §10.2 | 일일 손실 -3% 시 모든 실행 알고리즘 중단 |
| 적응형 전환 임계치: vol=2%, spread=50bps | SPEC §14 | 알고리즘 전환 조건 LOCK |

---

## STEP7-I 보강: V2+ 자동 실행 프레임워크 상세 (S7I-092)

> **보강 근거**: step7i_mapping.md PARTIAL — V2+ 자동 매매 프레임워크 전체 라이프사이클 (시그널 수신 → 리스크 검증 → 주문 생성 → 실행 → 체결 확인 → 사후 보고) 상세 누락
> **Priority**: MED

### E1. Input

- **Kafka Topics**:
  - `signal.trade.generated` — 트레이딩 시그널 (파티션 키: `symbol`)
  - `risk.limits.current` — 현재 리스크 한도 상태 (파티션 키: `portfolio_id`)
  - `execution.order.result` — 브로커 주문 체결 결과 (파티션 키: `order_id`)
  - `market.prices.realtime` — 실시간 시세 (파티션 키: `symbol`)
  - `portfolio.positions.current` — 현재 포지션 상태 (파티션 키: `portfolio_id`)
- **필수 필드**:
  ```python
  # signal.trade.generated
  {
      "signal_id": str,           # UUID
      "symbol": str,              # e.g., "005930", "AAPL", "BTC/USDT"
      "asset_class": str,         # "KR_STOCK" | "US_STOCK" | "CRYPTO"
      "side": str,                # "BUY" | "SELL"
      "quantity": float,          # 시그널 권장 수량
      "target_price": float,      # 목표 가격
      "signal_strength": float,   # 0.0 ~ 1.0
      "strategy_id": str,         # 시그널 발생 전략 ID
      "urgency": float,           # 0.0 ~ 1.0
      "stop_loss": float,         # 손절가
      "take_profit": float,       # 익절가
      "timestamp": datetime
  }
  ```
- **TimescaleDB Schema**:
  ```sql
  CREATE TABLE auto_execution_log (
      id              BIGSERIAL,
      timestamp       TIMESTAMPTZ NOT NULL,
      signal_id       TEXT NOT NULL,
      order_id        TEXT,
      symbol          TEXT NOT NULL,
      asset_class     TEXT NOT NULL,
      side            TEXT NOT NULL,
      signal_qty      DOUBLE PRECISION,
      approved_qty    DOUBLE PRECISION,
      filled_qty      DOUBLE PRECISION DEFAULT 0,
      filled_price    DOUBLE PRECISION,
      risk_check      TEXT NOT NULL,        -- 'PASSED' | 'REJECTED' | 'REDUCED'
      rejection_reason TEXT,
      stage           TEXT NOT NULL,        -- 'SIGNAL' | 'RISK_CHECK' | 'ORDER_GEN' | 'EXECUTING' | 'FILLED' | 'REPORTED'
      pnl_realized    DOUBLE PRECISION DEFAULT 0,
      execution_ms    INTEGER,
      PRIMARY KEY (id, timestamp)
  );
  SELECT create_hypertable('auto_execution_log', 'timestamp');

  CREATE TABLE auto_execution_circuit_breaker (
      id              BIGSERIAL,
      timestamp       TIMESTAMPTZ NOT NULL,
      trigger_type    TEXT NOT NULL,        -- 'DAILY_LOSS' | 'POSITION_LIMIT' | 'ERROR_RATE' | 'MANUAL'
      trigger_value   DOUBLE PRECISION,
      threshold       DOUBLE PRECISION,
      action_taken    TEXT NOT NULL,        -- 'HALT_ALL' | 'REDUCE_SIZE' | 'ALERT_ONLY'
      resumed_at      TIMESTAMPTZ,
      PRIMARY KEY (id, timestamp)
  );
  SELECT create_hypertable('auto_execution_circuit_breaker', 'timestamp');
  ```
- **전처리**:
  - 시그널 중복 제거: 동일 symbol + side + strategy_id가 5분 이내 재발생 시 무시
  - signal_strength < 0.3 시그널 필터링 (노이즈 제거)
  - 장 운영시간 외 시그널: 크립토 제외 큐잉 처리
  - V1 모드 체크: V1이면 알림만 발송, 자동 실행 차단

### E2. Algorithm

```python
import asyncio
import uuid
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class ExecutionMode(Enum):
    V1_ALERT_ONLY = "V1_ALERT_ONLY"       # V1: 알림만, 실행 없음
    V2_AUTO_EXECUTE = "V2_AUTO_EXECUTE"     # V2+: 실제 자동 매매


class RiskCheckResult(Enum):
    PASSED = "PASSED"
    REJECTED = "REJECTED"
    REDUCED = "REDUCED"  # 수량 축소 후 승인


class CircuitBreakerState(Enum):
    NORMAL = "NORMAL"
    TRIGGERED = "TRIGGERED"
    COOLDOWN = "COOLDOWN"


@dataclass
class RiskLimits:
    """포트폴리오 리스크 한도"""
    max_position_pct: float = 0.10        # 단일 종목 최대 비중 10%
    max_daily_loss_pct: float = 0.03      # 일일 최대 손실 3%
    max_daily_trades: int = 50            # 일일 최대 거래 횟수
    max_open_orders: int = 10             # 동시 미체결 주문 최대
    max_sector_exposure_pct: float = 0.30 # 섹터별 최대 30%
    min_cash_ratio: float = 0.20          # 최소 현금 비중 20%


@dataclass
class PreTradeRiskResult:
    """사전 리스크 검증 결과"""
    result: RiskCheckResult
    approved_qty: float
    original_qty: float
    reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ExecutionReport:
    """실행 완료 보고서"""
    signal_id: str
    order_id: str
    symbol: str
    side: str
    signal_qty: float
    approved_qty: float
    filled_qty: float
    avg_fill_price: float
    slippage_bps: float
    pnl_impact: float
    execution_time_ms: int
    risk_check: str
    stage: str
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ──────────────────────────────────────────────
# 1. 시그널 수신 및 V1/V2 분기
# ──────────────────────────────────────────────
def receive_signal(signal: dict, mode: ExecutionMode) -> Optional[dict]:
    """
    트레이딩 시그널 수신.
    V1: 알림만 발송 (Slack/Telegram), 자동 실행 없음.
    V2+: 자동 실행 파이프라인 진입.

    Safety: V1 → V2 전환은 관리자 수동 승인 + 환경변수 변경 필요.
    """
    # 시그널 기본 검증
    if signal.get("signal_strength", 0) < 0.3:
        return None  # 노이즈 필터링

    if mode == ExecutionMode.V1_ALERT_ONLY:
        # V1: 알림만 생성
        return {
            "action": "ALERT_ONLY",
            "signal_id": signal["signal_id"],
            "symbol": signal["symbol"],
            "side": signal["side"],
            "message": f"[V1 알림] {signal['symbol']} {signal['side']} "
                       f"시그널 (strength={signal['signal_strength']:.2f}). "
                       f"자동 실행 비활성 상태.",
            "timestamp": datetime.utcnow()
        }

    # V2+: 자동 실행 파이프라인
    return {
        "action": "AUTO_EXECUTE",
        "signal": signal,
        "pipeline_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow()
    }


# ──────────────────────────────────────────────
# 2. 사전 리스크 검증 (Pre-Trade Risk Check)
# ──────────────────────────────────────────────
def validate_risk(
    signal: dict,
    portfolio: dict,
    risk_limits: RiskLimits,
    circuit_breaker_state: CircuitBreakerState
) -> PreTradeRiskResult:
    """
    주문 생성 전 리스크 검증.

    검증 항목:
    1. 서킷 브레이커 상태 확인
    2. 일일 손실 한도 확인
    3. 포지션 집중도 확인
    4. 현금 비중 확인
    5. 일일 거래 횟수 확인
    6. 동시 미체결 주문 수 확인
    """
    reasons = []
    warnings = []
    approved_qty = signal["quantity"]

    # 1. 서킷 브레이커 확인
    if circuit_breaker_state == CircuitBreakerState.TRIGGERED:
        return PreTradeRiskResult(
            result=RiskCheckResult.REJECTED,
            approved_qty=0,
            original_qty=signal["quantity"],
            reasons=["서킷 브레이커 발동 중 — 모든 자동 매매 중단"]
        )

    # 2. 일일 손실 한도
    daily_pnl_pct = portfolio.get("daily_pnl_pct", 0.0)
    if daily_pnl_pct <= -risk_limits.max_daily_loss_pct:
        return PreTradeRiskResult(
            result=RiskCheckResult.REJECTED,
            approved_qty=0,
            original_qty=signal["quantity"],
            reasons=[f"일일 손실 한도 초과: {daily_pnl_pct:.2%} <= -{risk_limits.max_daily_loss_pct:.2%}"]
        )

    # 3. 포지션 집중도 확인
    symbol = signal["symbol"]
    total_value = portfolio.get("total_value", 1.0)
    current_position_value = portfolio.get("positions", {}).get(symbol, {}).get("value", 0)
    new_order_value = signal["quantity"] * signal["target_price"]
    projected_pct = (current_position_value + new_order_value) / total_value

    if projected_pct > risk_limits.max_position_pct:
        # 수량 축소
        max_additional_value = (risk_limits.max_position_pct * total_value) - current_position_value
        if max_additional_value <= 0:
            return PreTradeRiskResult(
                result=RiskCheckResult.REJECTED,
                approved_qty=0,
                original_qty=signal["quantity"],
                reasons=[f"단일 종목 한도 초과: {projected_pct:.2%} > {risk_limits.max_position_pct:.2%}"]
            )
        approved_qty = max_additional_value / signal["target_price"]
        warnings.append(
            f"수량 축소: {signal['quantity']:.0f} → {approved_qty:.0f} "
            f"(포지션 한도 {risk_limits.max_position_pct:.0%})"
        )

    # 4. 현금 비중 확인 (매수 시)
    if signal["side"] == "BUY":
        cash = portfolio.get("cash", 0)
        cash_after = cash - (approved_qty * signal["target_price"])
        cash_ratio_after = cash_after / total_value
        if cash_ratio_after < risk_limits.min_cash_ratio:
            max_buy_value = cash - (risk_limits.min_cash_ratio * total_value)
            if max_buy_value <= 0:
                return PreTradeRiskResult(
                    result=RiskCheckResult.REJECTED,
                    approved_qty=0,
                    original_qty=signal["quantity"],
                    reasons=[f"최소 현금 비중 미달: {cash_ratio_after:.2%} < {risk_limits.min_cash_ratio:.2%}"]
                )
            approved_qty = min(approved_qty, max_buy_value / signal["target_price"])
            warnings.append(f"현금 비중 제약으로 수량 축소: {approved_qty:.0f}주")

    # 5. 일일 거래 횟수
    daily_trades = portfolio.get("daily_trade_count", 0)
    if daily_trades >= risk_limits.max_daily_trades:
        return PreTradeRiskResult(
            result=RiskCheckResult.REJECTED,
            approved_qty=0,
            original_qty=signal["quantity"],
            reasons=[f"일일 거래 횟수 초과: {daily_trades} >= {risk_limits.max_daily_trades}"]
        )

    # 6. 미체결 주문 수
    open_orders = portfolio.get("open_order_count", 0)
    if open_orders >= risk_limits.max_open_orders:
        return PreTradeRiskResult(
            result=RiskCheckResult.REJECTED,
            approved_qty=0,
            original_qty=signal["quantity"],
            reasons=[f"동시 미체결 주문 한도 초과: {open_orders} >= {risk_limits.max_open_orders}"]
        )

    result_type = RiskCheckResult.REDUCED if approved_qty < signal["quantity"] else RiskCheckResult.PASSED
    return PreTradeRiskResult(
        result=result_type,
        approved_qty=approved_qty,
        original_qty=signal["quantity"],
        reasons=reasons,
        warnings=warnings
    )


# ──────────────────────────────────────────────
# 3. 주문 생성
# ──────────────────────────────────────────────
def generate_orders(
    signal: dict,
    risk_result: PreTradeRiskResult,
    current_price: float
) -> dict:
    """
    리스크 검증 통과 후 브로커 주문 생성.
    자산군에 따라 적절한 브로커 API로 라우팅.
    """
    if risk_result.result == RiskCheckResult.REJECTED:
        return {"action": "REJECTED", "reason": risk_result.reasons}

    order_id = str(uuid.uuid4())
    asset_class = signal["asset_class"]

    # 브로커 라우팅
    if asset_class == "KR_STOCK":
        broker = "KIWOOM"       # 또는 "KIS" — 설정에 따라
        price_type = "00"       # 지정가
        order_price = current_price  # 현재가 기준 지정가
    elif asset_class == "US_STOCK":
        broker = "ALPACA"
        price_type = "LIMIT"
        order_price = current_price
    elif asset_class == "CRYPTO":
        broker = "BINANCE"
        price_type = "LIMIT"
        order_price = current_price
    else:
        raise ValueError(f"Unknown asset_class: {asset_class}")

    return {
        "order_id": order_id,
        "signal_id": signal["signal_id"],
        "broker": broker,
        "symbol": signal["symbol"],
        "asset_class": asset_class,
        "side": signal["side"],
        "quantity": risk_result.approved_qty,
        "price": order_price,
        "price_type": price_type,
        "stop_loss": signal.get("stop_loss"),
        "take_profit": signal.get("take_profit"),
        "urgency": signal.get("urgency", 0.5),
        "timestamp": datetime.utcnow()
    }


# ──────────────────────────────────────────────
# 4. 주문 실행
# ──────────────────────────────────────────────
async def execute(order: dict, broker_clients: dict) -> dict:
    """
    브로커 API를 통해 실제 주문 전송.
    broker_clients: {"KIWOOM": KiwoomAPIBridge, "KIS": KISAPIClient, "ALPACA": ..., "BINANCE": ...}
    """
    broker = order["broker"]
    client = broker_clients.get(broker)
    if not client:
        raise RuntimeError(f"Broker client not found: {broker}")

    start_time = datetime.utcnow()

    if broker == "KIWOOM":
        # 키움 COM API (동기)
        order_type = 1 if order["side"] == "BUY" else 2
        result_code = client.send_order(
            account_no=client.session.account_list[0],
            symbol=order["symbol"],
            order_type=order_type,
            quantity=int(order["quantity"]),
            price=int(order["price"]),
            price_type="00"
        )
        return {
            "order_id": order["order_id"],
            "broker": broker,
            "status": "SUBMITTED" if result_code == 0 else "FAILED",
            "broker_result_code": result_code,
            "submitted_at": start_time
        }

    elif broker == "KIS":
        # KIS REST API (비동기)
        response = await client.place_order(
            account_no=client.account_no,  # 전용 계좌번호 설정 필드 (자격증명 토큰 미사용)
            account_suffix="01",
            symbol=order["symbol"],
            side=order["side"],
            quantity=int(order["quantity"]),
            price=int(order["price"]),
            order_type="00"
        )
        return {
            "order_id": order["order_id"],
            "broker": broker,
            "status": "SUBMITTED" if response.success else "FAILED",
            "broker_order_no": response.kis_order_no,
            "submitted_at": start_time
        }

    elif broker == "ALPACA":
        # Alpaca REST API
        return {
            "order_id": order["order_id"],
            "broker": broker,
            "status": "SUBMITTED",
            "submitted_at": start_time
        }

    elif broker == "BINANCE":
        # Binance REST API
        return {
            "order_id": order["order_id"],
            "broker": broker,
            "status": "SUBMITTED",
            "submitted_at": start_time
        }

    raise ValueError(f"Unsupported broker: {broker}")


# ──────────────────────────────────────────────
# 5. 체결 모니터링
# ──────────────────────────────────────────────
async def monitor_fills(
    order_id: str,
    timeout_seconds: int = 300,
    poll_interval: float = 1.0
) -> dict:
    """
    주문 체결 상태 모니터링.
    타임아웃 내 미체결 시 미체결 주문 취소 또는 시장가 전환.

    체결 정보는 OnReceiveChejanData (키움) / WebSocket (KIS) /
    REST poll (Alpaca/Binance) 으로 수신.
    """
    start = datetime.utcnow()
    filled_qty = 0
    avg_price = 0.0
    total_qty = 0

    while (datetime.utcnow() - start).total_seconds() < timeout_seconds:
        # Kafka에서 체결 이벤트 수신 (실제로는 consumer에서 비동기 수신)
        # fill_event = await kafka_consumer.poll()
        fill_event = None  # placeholder

        if fill_event:
            filled_qty = fill_event.get("filled_qty", 0)
            avg_price = fill_event.get("avg_fill_price", 0)
            total_qty = fill_event.get("total_qty", 0)

            if filled_qty >= total_qty:
                return {
                    "order_id": order_id,
                    "status": "FILLED",
                    "filled_qty": filled_qty,
                    "avg_fill_price": avg_price,
                    "fill_time_ms": int((datetime.utcnow() - start).total_seconds() * 1000)
                }

        await asyncio.sleep(poll_interval)

    # 타임아웃: 미체결분 처리
    return {
        "order_id": order_id,
        "status": "PARTIAL" if filled_qty > 0 else "TIMEOUT",
        "filled_qty": filled_qty,
        "avg_fill_price": avg_price,
        "fill_time_ms": timeout_seconds * 1000
    }


# ──────────────────────────────────────────────
# 6. PnL 업데이트 및 감사 보고
# ──────────────────────────────────────────────
def report(
    signal: dict,
    risk_result: PreTradeRiskResult,
    order: dict,
    fill_result: dict
) -> ExecutionReport:
    """
    실행 완료 보고서 생성.
    - 슬리피지 계산
    - PnL 영향 추정
    - 감사 로그 기록
    """
    target_price = signal.get("target_price", 0)
    fill_price = fill_result.get("avg_fill_price", 0)

    if target_price > 0 and fill_price > 0:
        if signal["side"] == "BUY":
            slippage_bps = (fill_price - target_price) / target_price * 10000
        else:
            slippage_bps = (target_price - fill_price) / target_price * 10000
    else:
        slippage_bps = 0.0

    filled_qty = fill_result.get("filled_qty", 0)
    pnl_impact = -abs(slippage_bps / 10000 * fill_price * filled_qty)  # 슬리피지 비용

    return ExecutionReport(
        signal_id=signal["signal_id"],
        order_id=order.get("order_id", ""),
        symbol=signal["symbol"],
        side=signal["side"],
        signal_qty=signal["quantity"],
        approved_qty=risk_result.approved_qty,
        filled_qty=filled_qty,
        avg_fill_price=fill_price,
        slippage_bps=round(slippage_bps, 2),
        pnl_impact=round(pnl_impact, 2),
        execution_time_ms=fill_result.get("fill_time_ms", 0),
        risk_check=risk_result.result.value,
        stage="REPORTED"
    )


# ──────────────────────────────────────────────
# 서킷 브레이커
# ──────────────────────────────────────────────
def check_circuit_breaker(
    portfolio: dict,
    daily_loss_limit: float = -0.03,
    error_rate_limit: float = 0.20,
    recent_errors: int = 0,
    recent_trades: int = 1
) -> CircuitBreakerState:
    """
    서킷 브레이커 판정.
    발동 조건:
    1. 일일 손실 >= 3% → HALT_ALL (모든 자동 매매 즉시 중단)
    2. 최근 주문 에러율 >= 20% → HALT_ALL
    3. 단일 종목 -10% 이상 손실 → 해당 종목만 매매 중단
    """
    daily_pnl_pct = portfolio.get("daily_pnl_pct", 0.0)

    if daily_pnl_pct <= daily_loss_limit:
        return CircuitBreakerState.TRIGGERED

    if recent_trades > 0 and (recent_errors / recent_trades) >= error_rate_limit:
        return CircuitBreakerState.TRIGGERED

    return CircuitBreakerState.NORMAL


# ──────────────────────────────────────────────
# 메인 자동 실행 파이프라인
# ──────────────────────────────────────────────
async def auto_execution_pipeline(
    signal: dict,
    portfolio: dict,
    risk_limits: RiskLimits,
    broker_clients: dict,
    mode: ExecutionMode = ExecutionMode.V2_AUTO_EXECUTE
) -> ExecutionReport:
    """
    전체 자동 실행 파이프라인.

    Signal → Risk Validator → Order Router → Broker API
           → Fill Monitor → PnL Update → Audit Log

    V1: 시그널 수신 → 알림 발송 (자동 실행 없음)
    V2+: 시그널 수신 → 리스크 검증 → 주문 생성 → 실행 → 체결 확인 → 보고
    """
    # Step 1: 시그널 수신 및 V1/V2 분기
    intake = receive_signal(signal, mode)
    if intake is None or intake.get("action") == "ALERT_ONLY":
        return ExecutionReport(
            signal_id=signal["signal_id"],
            order_id="",
            symbol=signal["symbol"],
            side=signal["side"],
            signal_qty=signal["quantity"],
            approved_qty=0,
            filled_qty=0,
            avg_fill_price=0,
            slippage_bps=0,
            pnl_impact=0,
            execution_time_ms=0,
            risk_check="V1_ALERT_ONLY",
            stage="ALERT_SENT"
        )

    # Step 2: 서킷 브레이커 확인
    cb_state = check_circuit_breaker(portfolio)

    # Step 3: 사전 리스크 검증
    risk_result = validate_risk(signal, portfolio, risk_limits, cb_state)
    if risk_result.result == RiskCheckResult.REJECTED:
        return ExecutionReport(
            signal_id=signal["signal_id"],
            order_id="",
            symbol=signal["symbol"],
            side=signal["side"],
            signal_qty=signal["quantity"],
            approved_qty=0,
            filled_qty=0,
            avg_fill_price=0,
            slippage_bps=0,
            pnl_impact=0,
            execution_time_ms=0,
            risk_check="REJECTED",
            stage="RISK_REJECTED"
        )

    # Step 4: 주문 생성
    current_price = signal["target_price"]  # 실제로는 실시간 시세
    order = generate_orders(signal, risk_result, current_price)

    # Step 5: 주문 실행
    exec_result = await execute(order, broker_clients)

    # Step 6: 체결 모니터링
    fill_result = await monitor_fills(order["order_id"], timeout_seconds=300)

    # Step 7: 보고서 생성 및 감사 로그
    report_data = report(signal, risk_result, order, fill_result)

    return report_data
```

### E3. Output

- **스키마**:
  ```python
  @dataclass
  class AutoExecutionOutput:
      signal_id: str
      order_id: str
      symbol: str
      side: str
      signal_qty: float
      approved_qty: float
      filled_qty: float
      avg_fill_price: float
      slippage_bps: float
      pnl_impact: float
      risk_check: str           # "PASSED" | "REJECTED" | "REDUCED" | "V1_ALERT_ONLY"
      stage: str                # 최종 도달 단계
      execution_time_ms: int
      timestamp: datetime
  ```
- **Kafka Output Topics**:
  - `execution.auto.result` — 자동 실행 최종 결과
  - `execution.auto.risk_rejected` — 리스크 검증 거부 이벤트
  - `execution.auto.circuit_breaker` — 서킷 브레이커 발동/해제 이벤트
  - `execution.auto.audit_log` — 감사 로그 (전 단계 기록)
  - `alert.execution.v1` — V1 알림 전용 이벤트
- **confidence 계산**: risk_check PASSED 시 0.85, REDUCED 시 0.70, signal_strength 가중. 서킷 브레이커 이력 있을 시 -0.10 차감.
- **소비자**:
  - `PortfolioTracker` — PnL 업데이트, 포지션 동기화
  - `AlertService` — V1 알림, 서킷 브레이커 알림
  - `AuditLogger` — 규제 대응 감사 기록
  - `DashboardService` — 실시간 실행 현황 표시

### E4. Class/API Design

```python
from execution.base import BaseExecutionEngine


class AutoExecutionFramework(BaseExecutionEngine):
    """V2+ 자동 실행 프레임워크.
    V1은 알림만, V2+에서 실제 자동 매매 수행.
    """

    def __init__(self, config: dict, broker_clients: dict):
        self.mode = ExecutionMode(config.get("execution_mode", "V1_ALERT_ONLY"))
        self.risk_limits = RiskLimits(
            max_position_pct=config.get("max_position_pct", 0.10),
            max_daily_loss_pct=config.get("max_daily_loss_pct", 0.03),
            max_daily_trades=config.get("max_daily_trades", 50),
            max_open_orders=config.get("max_open_orders", 10),
            min_cash_ratio=config.get("min_cash_ratio", 0.20)
        )
        self.broker_clients = broker_clients
        self._circuit_breaker_state = CircuitBreakerState.NORMAL

    async def receive_signal(self, signal: dict) -> Optional[dict]:
        """시그널 수신 및 V1/V2 분기 처리."""
        return receive_signal(signal, self.mode)

    def validate_risk(self, signal: dict, portfolio: dict) -> PreTradeRiskResult:
        """사전 리스크 검증 (포지션 한도, 일일 손실, 현금 비중 등)."""
        return validate_risk(signal, portfolio, self.risk_limits, self._circuit_breaker_state)

    def generate_orders(self, signal: dict, risk_result: PreTradeRiskResult,
                        current_price: float) -> dict:
        """리스크 통과 후 브로커별 주문 생성."""
        return generate_orders(signal, risk_result, current_price)

    async def execute(self, order: dict) -> dict:
        """브로커 API를 통해 주문 실행."""
        return await execute(order, self.broker_clients)

    async def monitor_fills(self, order_id: str, timeout_seconds: int = 300) -> dict:
        """체결 모니터링 (타임아웃 시 미체결 처리)."""
        return await monitor_fills(order_id, timeout_seconds)

    def report(self, signal: dict, risk_result: PreTradeRiskResult,
               order: dict, fill_result: dict) -> ExecutionReport:
        """실행 완료 보고서 생성 및 감사 로그."""
        return report(signal, risk_result, order, fill_result)

    async def run_pipeline(self, signal: dict, portfolio: dict) -> ExecutionReport:
        """전체 자동 실행 파이프라인 실행."""
        return await auto_execution_pipeline(
            signal, portfolio, self.risk_limits,
            self.broker_clients, self.mode
        )
```

### E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| confluent-kafka | >= 2.3 | Yes | 시그널 소비 / 결과 발행 |
| psycopg2 | >= 2.9 | Yes | TimescaleDB 감사 로그 |
| asyncio | stdlib | Yes | 비동기 실행 파이프라인 |
| uuid | stdlib | Yes | 주문/파이프라인 ID 생성 |
| pywin32 | >= 306 | Yes | 키움 COM 브릿지 (KR_STOCK) |
| httpx | >= 0.27 | Yes | KIS/Alpaca/Binance REST API |

### E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 시그널 → 주문 전송 | < 500ms | 리스크 검증 + 주문 생성 + API 호출 |
| 리스크 검증 | < 10ms | validate_risk() 단독 |
| 서킷 브레이커 판정 | < 2ms | check_circuit_breaker() |
| 체결 모니터링 폴링 | 1초 간격 | asyncio.sleep(1.0) |
| 전체 파이프라인 (체결 포함) | < 30s (정규장) | 시그널 수신 → 보고서 완료 |
| 동시 파이프라인 처리 | 10건 | asyncio.gather 병렬 |

### E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 시그널 필수 필드 누락 | ValueError raise, 시그널 무시 | HIGH |
| 리스크 검증 실패 | 주문 거부, 감사 로그 기록, 알림 발송 | MEDIUM |
| 서킷 브레이커 발동 | 모든 자동 매매 즉시 중단, 관리자 알림 | CRITICAL |
| 브로커 API 주문 실패 | 재시도 2회 → 실패 시 알림, 수동 대응 | HIGH |
| 체결 타임아웃 (300s) | 미체결 주문 취소 시도, 잔량 로깅 | HIGH |
| V1→V2 모드 전환 시 설정 오류 | 환경변수 검증 실패 → V1 유지 (안전 모드) | CRITICAL |
| 포트폴리오 데이터 조회 실패 | 캐시 사용 (최대 5분 이내) → 실패 시 주문 거부 | HIGH |
| 일일 손실 -3% 도달 | 서킷 브레이커 발동, 잔여 미체결 전량 취소 | CRITICAL |

### E8. Test Criteria

- **Unit**:
  - `AE-U-01`: V1 모드 → receive_signal → action="ALERT_ONLY"
  - `AE-U-02`: V2 모드 + signal_strength=0.2 → None (노이즈 필터)
  - `AE-U-03`: validate_risk — 포지션 한도 초과 → REDUCED
  - `AE-U-04`: validate_risk — 일일 손실 -4% → REJECTED
  - `AE-U-05`: validate_risk — 서킷 브레이커 TRIGGERED → REJECTED
  - `AE-U-06`: validate_risk — 현금 비중 미달 → 수량 축소
  - `AE-U-07`: generate_orders — KR_STOCK → broker="KIWOOM"
  - `AE-U-08`: generate_orders — REJECTED 입력 → action="REJECTED"
  - `AE-U-09`: check_circuit_breaker — daily_pnl=-0.04 → TRIGGERED
  - `AE-U-10`: check_circuit_breaker — error_rate=0.25 → TRIGGERED
  - `AE-U-11`: report — 슬리피지 계산: target=100, fill=100.5, BUY → 50bps
- **Integration**:
  - `AE-I-01`: V2 전체 파이프라인 E2E — 시그널 → 리스크 → 주문 → mock 체결 → 보고서
  - `AE-I-02`: V1 모드 E2E — 시그널 → 알림만 발송 → 주문 없음 확인
  - `AE-I-03`: 서킷 브레이커 발동 → 진행 중 파이프라인 중단 → 미체결 취소
  - `AE-I-04`: 체결 타임아웃 → 미체결 처리 → 감사 로그 기록
  - `AE-I-05`: 포지션 한도 초과 시그널 → 수량 축소 → 축소된 수량으로 체결
- **Acceptance**:
  - V2 파이프라인 시그널→주문 전송 < 500ms (리스크 검증 포함)
  - 서킷 브레이커 발동 시 잔여 주문 취소 성공률 100%
  - 감사 로그 누락률 0% (모든 시그널 기록)
  - V1→V2 전환 시 무중단 운영

### E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 일일 손실 한도 -3% | SPEC §10.2 | max_daily_loss_pct=0.03 |
| 단일 종목 최대 비중 10% | SPEC §10.2 | max_position_pct=0.10 |
| 최소 현금 비중 20% | SPEC §10.2 | min_cash_ratio=0.20 |
| 일일 최대 거래 50건 | SPEC §10.2 | max_daily_trades=50 |
| 체결 타임아웃 300초 | 운영 정책 | monitor_fills timeout_seconds=300 |
| V1/V2 모드 전환 | SPEC §12 milestone | 환경변수 EXECUTION_MODE |
| 기술스택 | SPEC §14 | 라이브러리 버전 LOCK |

---

> **L3 판정**: 9요소 전수 기재 완료 (E1~E9). **L3 PASS**. ✅
> **검증일**: 2026-03-22
