# 리밸런싱 최적화

> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #6 실행 최적화
> **정본 소유 개념**: 리밸런싱 실행 엔진
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-6. 리밸런싱 최적화

| # | 항목 | 상세 |
|---|------|------|
| 22 | **리밸런싱 트리거 규칙** | 정기(월간/분기) + 비정기(비중 ±5% 이탈 시) 하이브리드. 과도한 리밸런싱(비용 낭비) vs 과소 리밸런싱(리스크 누적) 균형 |
| 23 | **세금 효율적 리밸런싱** | 매도 시 세금 영향 고려. 장기 보유(양도세 감면) vs 단기 보유 구분. Tax-Loss Harvesting 우선 매도 |
| 24 | **거래 비용 인지 리밸런싱** | 리밸런싱 이득 > 거래 비용일 때만 실행. 비중 이탈이 작으면 리밸런싱 보류(비용 대비 불리) |
| 25 | **다자산 동시 리밸런싱** | 미국 주식/한국 주식/크립토 동시 리밸런싱 시 환율, 시간대, 시장 영업시간 차이 고려. 주문 순서 최적화 |

---

## E1. Input

- **Kafka Topics**:
  - `portfolio.positions.current` — 현재 포트폴리오 포지션 (자산별 비중)
  - `portfolio.target.weights` — 목표 포트폴리오 비중 (전략 엔진 산출)
  - `market.prices.realtime` — 실시간 시세 (체결가, 호가)
  - `market.fx.rates` — 실시간 환율 (USD/KRW)
  - `market.calendar.status` — 시장 영업 상태 (개장/폐장/동시호가)
- **필수 필드**:
  - `symbol`: str — 종목/코인 심볼
  - `asset_class`: str — "US_STOCK" | "KR_STOCK" | "CRYPTO"
  - `current_weight`: float — 현재 비중 (0.0~1.0)
  - `target_weight`: float — 목표 비중 (0.0~1.0)
  - `current_price`: float — 현재가
  - `avg_daily_volume`: float — 일평균 거래량
  - `holding_days`: int — 보유 일수
  - `unrealized_pnl`: float — 미실현 손익
  - `tax_rate`: float — 적용 세율
  - `estimated_fee`: float — 예상 거래 비용 (슬리피지 + 수수료)
  - `fx_rate`: float — 환율 (원/달러)
- **TimescaleDB Schema**:
  ```sql
  CREATE TABLE rebalancing_history (
      id             BIGSERIAL,
      timestamp      TIMESTAMPTZ NOT NULL,
      portfolio_id   TEXT NOT NULL,
      trigger_type   TEXT NOT NULL,        -- 'CALENDAR' | 'THRESHOLD' | 'HYBRID'
      pre_weights    JSONB NOT NULL,       -- {"AAPL": 0.12, "005930": 0.08, ...}
      target_weights JSONB NOT NULL,
      post_weights   JSONB NOT NULL,
      total_cost     DOUBLE PRECISION,     -- 총 거래 비용
      tax_impact     DOUBLE PRECISION,     -- 세금 영향
      net_benefit    DOUBLE PRECISION,     -- 리밸런싱 순이득
      execution_ms   INTEGER,
      PRIMARY KEY (id, timestamp)
  );
  SELECT create_hypertable('rebalancing_history', 'timestamp');

  CREATE TABLE rebalancing_orders (
      id             BIGSERIAL,
      timestamp      TIMESTAMPTZ NOT NULL,
      rebalance_id   BIGINT NOT NULL,
      symbol         TEXT NOT NULL,
      asset_class    TEXT NOT NULL,
      side           TEXT NOT NULL,        -- 'BUY' | 'SELL'
      quantity       DOUBLE PRECISION,
      target_price   DOUBLE PRECISION,
      filled_price   DOUBLE PRECISION,
      status         TEXT NOT NULL,
      execution_seq  INTEGER,             -- 실행 순서
      PRIMARY KEY (id, timestamp)
  );
  SELECT create_hypertable('rebalancing_orders', 'timestamp');
  ```
- **전처리**:
  - 비중 합계 정규화: sum(target_weights) = 1.0 검증
  - 현재가 NaN → 직전 종가 대체, 2회 연속 NaN → 해당 종목 리밸런싱 제외
  - 환율 데이터: 5초 이내 데이터만 사용, 초과 시 마지막 유효값 + WARNING
  - 최소 데이터 요건: ADV 20일 이상 이력 필요

## E2. Algorithm

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional
import math

# === 데이터 클래스 ===

class TriggerType(Enum):
    CALENDAR = "CALENDAR"        # 정기 리밸런싱
    THRESHOLD = "THRESHOLD"      # 비중 이탈 트리거
    HYBRID = "HYBRID"            # 복합 트리거

class AssetClass(Enum):
    US_STOCK = "US_STOCK"
    KR_STOCK = "KR_STOCK"
    CRYPTO = "CRYPTO"

@dataclass
class Position:
    symbol: str
    asset_class: AssetClass
    current_weight: float
    target_weight: float
    current_price: float
    avg_daily_volume: float
    holding_days: int
    unrealized_pnl: float
    tax_rate: float
    estimated_fee: float       # 슬리피지 + 수수료 (비율)

@dataclass
class RebalanceOrder:
    symbol: str
    asset_class: AssetClass
    side: str                  # "BUY" | "SELL"
    weight_delta: float        # 비중 변화량
    dollar_amount: float       # 금액
    quantity: int
    execution_seq: int         # 실행 순서
    estimated_cost: float      # 예상 비용
    tax_impact: float          # 세금 영향

@dataclass
class RebalanceResult:
    trigger_type: TriggerType
    should_rebalance: bool
    orders: list[RebalanceOrder]
    total_cost: float
    total_tax: float
    net_benefit: float         # tracking_error_reduction - total_cost - total_tax
    tracking_error_before: float
    tracking_error_after: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)

# === #22: 리밸런싱 트리거 규칙 ===

# 임계값 설정
WEIGHT_DEVIATION_THRESHOLD = 0.05   # ±5% 비중 이탈
CALENDAR_INTERVAL_DAYS = 30         # 월간 정기
MIN_REBALANCE_INTERVAL_DAYS = 7     # 최소 리밸런싱 간격 (과도 방지)

def check_rebalance_trigger(
    positions: list[Position],
    last_rebalance_date: datetime,
    now: datetime
) -> tuple[bool, TriggerType]:
    """하이브리드 리밸런싱 트리거 판단"""

    days_since_last = (now - last_rebalance_date).days

    # 최소 간격 미달 → 리밸런싱 보류
    if days_since_last < MIN_REBALANCE_INTERVAL_DAYS:
        return False, TriggerType.CALENDAR

    # (1) 임계값 기반 트리거
    threshold_triggered = False
    for pos in positions:
        deviation = abs(pos.current_weight - pos.target_weight)
        if deviation > WEIGHT_DEVIATION_THRESHOLD:
            threshold_triggered = True
            break

    # (2) 정기(캘린더) 트리거
    calendar_triggered = (days_since_last >= CALENDAR_INTERVAL_DAYS)

    # (3) 하이브리드 판단
    if threshold_triggered and calendar_triggered:
        return True, TriggerType.HYBRID
    elif threshold_triggered:
        return True, TriggerType.THRESHOLD
    elif calendar_triggered:
        return True, TriggerType.CALENDAR
    else:
        return False, TriggerType.CALENDAR

# === #23: 세금 효율적 리밸런싱 ===

# 한국: 양도세 대주주 기준, 미국: STCG/LTCG 구분, 크립토: 250만원 초과 과세
LONG_TERM_HOLDING_DAYS_US = 365     # 미국 장기보유 기준
LONG_TERM_HOLDING_DAYS_KR = 365     # 한국 장기보유 기준
CRYPTO_TAX_FREE_KRW = 2_500_000     # 크립토 비과세 한도 (원)

def calculate_tax_impact(pos: Position, sell_amount: float) -> float:
    """매도 시 세금 영향 계산"""
    if pos.unrealized_pnl <= 0:
        # 손실 포지션 → 세금 없음 (Tax-Loss Harvesting 후보)
        return 0.0

    taxable_gain = pos.unrealized_pnl * (sell_amount / (pos.current_weight * 1.0))

    if pos.asset_class == AssetClass.US_STOCK:
        if pos.holding_days >= LONG_TERM_HOLDING_DAYS_US:
            # LTCG: 15% (미국 원천징수)
            return taxable_gain * 0.15
        else:
            # STCG: 22% (한국 양도세율)
            return taxable_gain * 0.22

    elif pos.asset_class == AssetClass.KR_STOCK:
        # 대주주 아닌 경우 국내 주식 양도세 면제 (2025 기준)
        # 대주주: 22% (3억 이하) / 27.5% (3억 초과)
        return 0.0  # 소액투자자 기준

    elif pos.asset_class == AssetClass.CRYPTO:
        # 250만원 초과분 22% 과세
        if taxable_gain > CRYPTO_TAX_FREE_KRW:
            return (taxable_gain - CRYPTO_TAX_FREE_KRW) * 0.22
        return 0.0

    return 0.0

def select_tax_efficient_sells(
    positions: list[Position],
    required_sell_weight: float
) -> list[Position]:
    """Tax-Loss Harvesting 우선 매도 순서 결정"""
    # 우선순위: (1) 손실 포지션 (TLH) → (2) 장기보유 → (3) 단기보유
    loss_positions = [p for p in positions if p.unrealized_pnl < 0]
    long_term = [p for p in positions if p.unrealized_pnl >= 0
                 and p.holding_days >= LONG_TERM_HOLDING_DAYS_US]
    short_term = [p for p in positions if p.unrealized_pnl >= 0
                  and p.holding_days < LONG_TERM_HOLDING_DAYS_US]

    # 손실 큰 순 → 보유기간 긴 순
    loss_positions.sort(key=lambda p: p.unrealized_pnl)
    long_term.sort(key=lambda p: p.unrealized_pnl)
    short_term.sort(key=lambda p: p.unrealized_pnl)

    return loss_positions + long_term + short_term

# === #24: 거래 비용 인지 리밸런싱 ===

def calculate_rebalance_benefit(
    positions: list[Position],
    portfolio_value: float,
    risk_aversion: float = 2.0
) -> tuple[float, float]:
    """
    리밸런싱 이득 vs 비용 비교.
    이득 = Tracking Error 감소에 의한 기대 리스크 절감
    비용 = 거래 비용 + 세금
    Returns: (net_benefit, total_cost)
    """
    # Tracking Error (TE) 계산: sqrt(sum((w_i - w_i*)^2))
    te_before = math.sqrt(sum(
        (p.current_weight - p.target_weight) ** 2 for p in positions
    ))

    # 리밸런싱 후 TE = 0 (완전 리밸런싱) 가정
    te_after = 0.0

    # 리스크 감소 이득 (연율 기대 효용 증가)
    # benefit = 0.5 * risk_aversion * (TE_before^2 - TE_after^2) * portfolio_value
    risk_benefit = 0.5 * risk_aversion * (te_before ** 2 - te_after ** 2) * portfolio_value

    # 총 거래 비용 계산
    total_cost = 0.0
    total_tax = 0.0
    for p in positions:
        weight_delta = abs(p.current_weight - p.target_weight)
        if weight_delta < 0.001:  # 0.1% 미만 무시
            continue
        trade_amount = weight_delta * portfolio_value
        cost = trade_amount * p.estimated_fee
        total_cost += cost

        if p.current_weight > p.target_weight:  # 매도
            total_tax += calculate_tax_impact(p, weight_delta)

    net_benefit = risk_benefit - total_cost - total_tax
    return net_benefit, total_cost + total_tax

def apply_cost_aware_filter(
    positions: list[Position],
    portfolio_value: float
) -> list[Position]:
    """비용 대비 이득이 없는 종목은 리밸런싱에서 제외"""
    filtered = []
    for p in positions:
        weight_delta = abs(p.current_weight - p.target_weight)
        if weight_delta < 0.001:
            continue

        trade_amount = weight_delta * portfolio_value
        cost = trade_amount * p.estimated_fee
        tax = calculate_tax_impact(p, weight_delta) if p.current_weight > p.target_weight else 0.0

        # 개별 종목 단위: 리스크 감소 > 비용 + 세금
        risk_reduction = 0.5 * 2.0 * (weight_delta ** 2) * portfolio_value
        if risk_reduction > (cost + tax):
            filtered.append(p)

    return filtered

# === #25: 다자산 동시 리밸런싱 ===

# 시장 영업시간 (UTC)
MARKET_HOURS = {
    AssetClass.KR_STOCK: {"open": "00:00", "close": "06:30"},   # KST 09:00~15:30 → UTC
    AssetClass.US_STOCK: {"open": "14:30", "close": "21:00"},   # EST 09:30~16:00 → UTC
    AssetClass.CRYPTO:   {"open": "00:00", "close": "23:59"},   # 24/7
}

def determine_execution_sequence(
    orders: list[RebalanceOrder],
    current_utc: datetime,
    fx_rate: float
) -> list[RebalanceOrder]:
    """
    다자산 실행 순서 최적화.
    원칙:
    1. 매도 우선 (현금 확보)
    2. 현재 개장 중인 시장 우선
    3. 환전 필요 시 매도→환전→매수 순서
    4. 크립토는 브릿지 역할 (어떤 시간대든 실행 가능)
    """
    # Step 1: 매도/매수 분리
    sells = [o for o in orders if o.side == "SELL"]
    buys = [o for o in orders if o.side == "BUY"]

    # Step 2: 매도 주문 정렬 (현재 개장 시장 우선)
    def market_priority(order: RebalanceOrder) -> int:
        if order.asset_class == AssetClass.CRYPTO:
            return 1  # 항상 실행 가능
        hours = MARKET_HOURS[order.asset_class]
        # 개장 중이면 우선순위 높음
        current_time = current_utc.strftime("%H:%M")
        if hours["open"] <= current_time <= hours["close"]:
            return 0  # 최우선
        return 2  # 폐장

    sells.sort(key=market_priority)
    buys.sort(key=market_priority)

    # Step 3: 실행 순서 부여 (매도 → 매수)
    seq = 1
    for order in sells + buys:
        order.execution_seq = seq
        seq += 1

    return sells + buys

# === 메인 리밸런싱 엔진 ===

def execute_rebalancing(
    positions: list[Position],
    portfolio_value: float,
    last_rebalance_date: datetime,
    fx_rate: float,
    now: datetime
) -> RebalanceResult:
    """리밸런싱 전체 파이프라인"""

    # Step 1: 트리거 판단
    should_rebalance, trigger_type = check_rebalance_trigger(
        positions, last_rebalance_date, now
    )

    if not should_rebalance:
        return RebalanceResult(
            trigger_type=trigger_type,
            should_rebalance=False,
            orders=[],
            total_cost=0.0,
            total_tax=0.0,
            net_benefit=0.0,
            tracking_error_before=math.sqrt(sum(
                (p.current_weight - p.target_weight) ** 2 for p in positions
            )),
            tracking_error_after=0.0,
            confidence=0.0
        )

    # Step 2: 비용 인지 필터링
    filtered_positions = apply_cost_aware_filter(positions, portfolio_value)

    # Step 3: 순이득 확인
    net_benefit, total_expense = calculate_rebalance_benefit(
        filtered_positions, portfolio_value
    )

    if net_benefit <= 0:
        return RebalanceResult(
            trigger_type=trigger_type,
            should_rebalance=False,
            orders=[],
            total_cost=total_expense,
            total_tax=0.0,
            net_benefit=net_benefit,
            tracking_error_before=math.sqrt(sum(
                (p.current_weight - p.target_weight) ** 2 for p in positions
            )),
            tracking_error_after=0.0,
            confidence=0.0
        )

    # Step 4: 매도 순서 결정 (세금 효율)
    sell_candidates = [p for p in filtered_positions
                       if p.current_weight > p.target_weight]
    sell_order = select_tax_efficient_sells(
        sell_candidates,
        sum(p.current_weight - p.target_weight
            for p in sell_candidates if p.current_weight > p.target_weight)
    )

    # Step 5: 주문 생성
    orders = []
    total_cost = 0.0
    total_tax = 0.0
    for p in filtered_positions:
        weight_delta = p.target_weight - p.current_weight
        if abs(weight_delta) < 0.001:
            continue

        side = "BUY" if weight_delta > 0 else "SELL"
        dollar_amount = abs(weight_delta) * portfolio_value
        quantity = int(dollar_amount / p.current_price)

        cost = dollar_amount * p.estimated_fee
        tax = calculate_tax_impact(p, abs(weight_delta)) if side == "SELL" else 0.0

        orders.append(RebalanceOrder(
            symbol=p.symbol,
            asset_class=p.asset_class,
            side=side,
            weight_delta=weight_delta,
            dollar_amount=dollar_amount,
            quantity=quantity,
            execution_seq=0,
            estimated_cost=cost,
            tax_impact=tax
        ))
        total_cost += cost
        total_tax += tax

    # Step 6: 다자산 실행 순서 최적화
    orders = determine_execution_sequence(orders, now, fx_rate)

    # Step 7: TE 계산
    te_before = math.sqrt(sum(
        (p.current_weight - p.target_weight) ** 2 for p in positions
    ))

    # Confidence: 필터링된 종목 비율 * 시장 개장 비율
    open_ratio = sum(1 for o in orders
                     if o.asset_class == AssetClass.CRYPTO) / max(len(orders), 1)
    confidence = min(0.95, 0.5 + 0.3 * (len(filtered_positions) / max(len(positions), 1))
                     + 0.15 * open_ratio)

    return RebalanceResult(
        trigger_type=trigger_type,
        should_rebalance=True,
        orders=orders,
        total_cost=total_cost,
        total_tax=total_tax,
        net_benefit=net_benefit,
        tracking_error_before=te_before,
        tracking_error_after=0.0,
        confidence=confidence
    )
```

## E3. Output

- **스키마**:
  ```python
  @dataclass
  class RebalanceResult:
      trigger_type: TriggerType       # CALENDAR | THRESHOLD | HYBRID
      should_rebalance: bool          # 리밸런싱 실행 여부
      orders: list[RebalanceOrder]    # 실행할 주문 목록
      total_cost: float               # 총 거래 비용
      total_tax: float                # 총 세금 영향
      net_benefit: float              # 순이득 (리스크감소 - 비용 - 세금)
      tracking_error_before: float    # 리밸런싱 전 TE
      tracking_error_after: float     # 리밸런싱 후 TE
      confidence: float               # 0.0~1.0
      timestamp: datetime
  ```
- **Kafka Output Topic**: `execution.rebalancing.orders`
- **confidence 계산**: `0.5 + 0.3*(filtered_ratio) + 0.15*(market_open_ratio)` — 필터링 통과 비율 + 시장 개장 비율 기반. net_benefit > 0 일 때만 실행.
- **소비자**:
  - `OrderManager` — 리밸런싱 주문 실행
  - `TCAModule` — 리밸런싱 비용 사후 분석
  - `PortfolioTracker` — 비중 업데이트
  - `AlertService` — 리밸런싱 실행/보류 알림

## E4. Class/API Design

```python
from execution.base import BaseExecutionEngine
from portfolio.state import PortfolioState
from market.data import MarketDataGateway

class RebalancingEngine(BaseExecutionEngine):
    """리밸런싱 엔진.

    하이브리드 트리거 (캘린더 + 임계값), 세금 효율, 비용 인지,
    다자산 동시 실행을 통합 관리.
    """

    # 설정
    WEIGHT_DEVIATION_THRESHOLD: float = 0.05
    CALENDAR_INTERVAL_DAYS: int = 30
    MIN_REBALANCE_INTERVAL_DAYS: int = 7
    RISK_AVERSION: float = 2.0

    def __init__(
        self,
        portfolio_state: PortfolioState,
        market_data: MarketDataGateway,
        order_manager: "OrderManager",
        tca_module: "TCAModule",
        alert_service: "AlertService"
    ):
        self.portfolio_state = portfolio_state
        self.market_data = market_data
        self.order_manager = order_manager
        self.tca_module = tca_module
        self.alert_service = alert_service

    def check_trigger(self) -> tuple[bool, TriggerType]:
        """하이브리드 리밸런싱 트리거 판단."""
        ...

    def calculate_tax_impact(self, position: Position, sell_weight: float) -> float:
        """매도 시 세금 영향 계산 (자산군별 상이)."""
        ...

    def select_tax_efficient_sells(self, positions: list[Position]) -> list[Position]:
        """Tax-Loss Harvesting 우선 매도 순서 결정."""
        ...

    def evaluate_cost_benefit(self, positions: list[Position]) -> tuple[float, float]:
        """리밸런싱 순이득 vs 비용 비교."""
        ...

    def determine_execution_sequence(self, orders: list[RebalanceOrder]) -> list[RebalanceOrder]:
        """다자산 실행 순서 최적화 (매도 우선, 개장 시장 우선)."""
        ...

    def execute(self) -> RebalanceResult:
        """리밸런싱 전체 파이프라인 실행."""
        ...

    def rollback(self, rebalance_id: int, reason: str) -> None:
        """리밸런싱 실패 시 롤백 (실행된 주문 반대 매매)."""
        ...


class CalendarRebalancer(RebalancingEngine):
    """정기 리밸런싱 전용. 월간/분기 스케줄."""

    def check_trigger(self) -> tuple[bool, TriggerType]:
        """캘린더 기반 트리거만 체크."""
        ...


class ThresholdRebalancer(RebalancingEngine):
    """비중 이탈 트리거 전용. 실시간 모니터링."""

    def check_trigger(self) -> tuple[bool, TriggerType]:
        """임계값 기반 트리거만 체크."""
        ...
```

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | >= 2.0 | Yes | 포지션 데이터 처리, 비중 계산 |
| numpy | >= 1.24 | Yes | Tracking Error 계산, 수학 연산 |
| confluent-kafka | >= 2.3 | Yes | Kafka 토픽 소비/발행 |
| psycopg2 | >= 2.9 | Yes | TimescaleDB 기록 |
| asyncio | stdlib | Yes | 비동기 다자산 동시 실행 |
| schedule | >= 1.2 | Yes | 정기 리밸런싱 스케줄러 |

## E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 트리거 판단 지연 | < 50ms | 포지션 수 100개 기준 |
| 비용/세금 계산 | < 200ms | 전체 포트폴리오 기준 |
| 주문 생성 | < 100ms | 주문 목록 생성까지 |
| 다자산 실행 총 시간 | < 5s | 매도→환전→매수 전체 파이프라인 (주문 전송까지) |
| 메모리 사용 | < 256MB | 포지션 500개 이하 기준 |
| 동시 리밸런싱 | 1건 | 중복 실행 방지 (distributed lock) |

## E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 목표 비중 합계 ≠ 1.0 | 정규화 처리 후 WARNING 로그, 0.01 초과 차이 시 거부 | HIGH |
| 환율 데이터 미수신 | 마지막 유효 환율 사용 + WARNING. 30분 초과 시 다자산 리밸런싱 보류 | HIGH |
| 시장 폐장 중 주문 시도 | 해당 자산 주문 보류, 개장 시 자동 재시도 큐 등록 | MEDIUM |
| 매도 주문 실패 (잔고 부족) | 실제 잔고 재조회 → 주문 수량 재계산 → 재시도 | HIGH |
| 매수 주문 실패 (현금 부족) | 매도 완료 대기 후 재시도. 타임아웃 3분 | HIGH |
| 부분 체결 리밸런싱 | 미체결분 추적, 다음 사이클에서 잔여분 처리 | MEDIUM |
| DB 기록 실패 | 3회 재시도 → 실패 시 로컬 파일 백업 + 알림 | MEDIUM |
| 동시 리밸런싱 충돌 | distributed lock 획득 실패 → 스킵 + 다음 사이클 대기 | LOW |

## E8. Test Criteria

- **Unit**:
  - `RB-U-01`: 비중 이탈 6% → THRESHOLD 트리거 발동 확인
  - `RB-U-02`: 비중 이탈 4% → 트리거 미발동 확인
  - `RB-U-03`: 캘린더 30일 경과 + 이탈 3% → CALENDAR 트리거
  - `RB-U-04`: 캘린더 30일 경과 + 이탈 6% → HYBRID 트리거
  - `RB-U-05`: 최소 간격 7일 미달 → 트리거 미발동
  - `RB-U-06`: 손실 포지션 매도 시 tax_impact = 0.0
  - `RB-U-07`: 미국 장기보유(366일) 이익 포지션 → 15% 세율 적용
  - `RB-U-08`: 크립토 250만원 이하 이익 → 세금 0
  - `RB-U-09`: net_benefit < 0 → should_rebalance = False
  - `RB-U-10`: 매도 우선 정렬 (손실 → 장기 → 단기) 순서 확인
- **Integration**:
  - `RB-I-01`: 포트폴리오 10종목 → 트리거 → 주문 생성 → OrderManager 전달 E2E
  - `RB-I-02`: 다자산(KR+US+CRYPTO) 동시 리밸런싱 → 실행 순서 검증
  - `RB-I-03`: 매도 완료 → 환전 → 매수 파이프라인 순차 실행
  - `RB-I-04`: TimescaleDB 기록 → 조회 일관성
- **Acceptance**:
  - 리밸런싱 후 Tracking Error 90% 이상 감소
  - 세금 효율 매도 시 단순 매도 대비 세금 20% 이상 절감
  - 과도 리밸런싱 방지: 월 최대 4회 이내

## E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 비중 이탈 임계값 ±5% | SPEC §6.4 | 리밸런싱 트리거 기준 |
| 최소 현금 비중 20% | SPEC §10.2 | 리밸런싱 후 현금 비중 유지 |
| 단일 종목 최대 10% | SPEC §10.2 | 리밸런싱 목표 비중 제약 |
| P2 HITL 승인 | D2.0-07 (I-19) | 대규모 리밸런싱(포트폴리오 30% 이상 변경) 시 승인 필요 |
| 기술스택 | SPEC §14 | 라이브러리 버전 LOCK |

---

> **L3 판정**: 9요소 전수 기재 완료 (E1~E9). **L3 PASS**.
> - E1 ✅ Kafka topics, TimescaleDB schema, 전처리 규칙
> - E2 ✅ 4개 항목(#22~#25) 전체 알고리즘, 실제 수식, dataclass
> - E3 ✅ 출력 스키마, Kafka output, confidence 계산, 소비자
> - E4 ✅ BaseExecutionEngine 상속, 메서드 시그니처, 서브클래스
> - E5 ✅ 라이브러리 6종 LOCK 상태
> - E6 ✅ 레이턴시, 메모리, 동시성 기준
> - E7 ✅ 8개 에러 시나리오, 복구 로직, 심각도
> - E8 ✅ Unit 10건, Integration 4건, Acceptance 3건
> - E9 ✅ LOCK 참조 5건
> **검증일**: 2026-03-22
