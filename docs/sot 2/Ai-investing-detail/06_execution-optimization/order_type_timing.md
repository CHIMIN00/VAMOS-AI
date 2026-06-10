# 주문 유형 & 타이밍 최적화

> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #6 실행 최적화
> **정본 소유 개념**: 주문 유형 & 타이밍 최적화
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-3. 주문 유형 & 타이밍 최적화

| # | 항목 | 상세 |
|---|------|------|
| 10 | **지정가 vs 시장가 자동 결정** | 긴급도 높음 → 시장가(확실한 체결), 긴급도 낮음 → 지정가(가격 개선). 현재 스프레드/변동성 기반 자동 결정 |
| 11 | **주문 타이밍 최적화** | 장 중 최적 시간대 분석. 스프레드가 좁고 유동성 높은 시간대 우선 체결. 장 개시 직후/마감 직전 변동성 회피 |
| 12 | **조건부 주문 체인** | "A 종목 매도 체결 → B 종목 매수" 연쇄 주문. 포트폴리오 리밸런싱 시 매도→매수 순서 최적화 |
| 13 | **크립토 24/7 타이밍** | 아시아/유럽/미국 세션별 유동성 차이 활용. 주말 저유동성 시간대 대량 주문 회피. 펀딩 레이트 정산 시점(8시간마다) 활용 |

---

## E1. Input

### Kafka Topics

| Topic | 용도 | 파티션 키 |
|-------|------|-----------|
| `order.type.request` | 주문 유형 결정 요청 | `symbol` |
| `market.orderbook.l2` | 실시간 호가창 | `symbol` |
| `market.spread.realtime` | 실시간 스프레드 | `symbol` |
| `market.volume.intraday` | 장 중 거래량 패턴 | `symbol` |
| `market.funding.rate` | 크립토 펀딩 레이트 | `symbol` |
| `execution.chain.request` | 조건부 주문 체인 요청 | `chain_id` |

### 필수 필드

```python
# order.type.request
{
    "request_id": str,          # UUID
    "symbol": str,
    "asset_class": str,         # "US_STOCK" | "KR_STOCK" | "CRYPTO"
    "side": str,                # "BUY" | "SELL"
    "qty": float,
    "urgency": float,           # 0.0 ~ 1.0
    "signal_confidence": float, # 원본 시그널 신뢰도
    "timestamp": datetime
}

# market.spread.realtime
{
    "symbol": str,
    "bid": float,
    "ask": float,
    "spread": float,
    "spread_bps": float,
    "volatility_1h": float,     # 1시간 변동성
    "avg_spread_30m": float,    # 30분 평균 스프레드
    "timestamp": datetime
}

# market.volume.intraday
{
    "symbol": str,
    "time_bucket": str,         # "09:00" ~ "15:30" (30분 단위)
    "avg_volume": float,
    "avg_spread_bps": float,
    "liquidity_score": float,   # 0.0 ~ 1.0
    "timestamp": datetime
}

# execution.chain.request
{
    "chain_id": str,
    "orders": list[dict],       # [{symbol, side, qty, priority}, ...]
    "chain_type": str,          # "SEQUENTIAL" | "CONDITIONAL"
    "condition": str,           # e.g., "SELL_FILLED_THEN_BUY"
    "timestamp": datetime
}

# market.funding.rate
{
    "symbol": str,
    "exchange": str,
    "funding_rate": float,      # e.g., 0.01 (= 1%)
    "next_settlement": datetime,
    "timestamp": datetime
}
```

### TimescaleDB Schema

```sql
CREATE TABLE order_type_decisions (
    decision_id     UUID PRIMARY KEY,
    request_id      UUID NOT NULL,
    symbol          TEXT NOT NULL,
    asset_class     TEXT NOT NULL,
    side            TEXT NOT NULL,
    decided_type    TEXT NOT NULL,        -- MARKET | LIMIT | CONDITIONAL_LIMIT
    decided_price   DOUBLE PRECISION,
    urgency         DOUBLE PRECISION,
    spread_bps      DOUBLE PRECISION,
    volatility      DOUBLE PRECISION,
    confidence      DOUBLE PRECISION,
    reason          TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('order_type_decisions', 'created_at');

CREATE TABLE timing_scores (
    symbol          TEXT NOT NULL,
    asset_class     TEXT NOT NULL,
    time_bucket     TEXT NOT NULL,        -- "09:00", "09:30", ...
    timing_score    DOUBLE PRECISION,     -- 0.0 ~ 1.0 (높을수록 유리)
    avg_spread_bps  DOUBLE PRECISION,
    avg_volume      DOUBLE PRECISION,
    liquidity_score DOUBLE PRECISION,
    updated_at      TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (symbol, time_bucket)
);

CREATE TABLE order_chains (
    chain_id        UUID PRIMARY KEY,
    chain_type      TEXT NOT NULL,
    total_orders    INTEGER NOT NULL,
    completed_orders INTEGER DEFAULT 0,
    status          TEXT DEFAULT 'PENDING',  -- PENDING | IN_PROGRESS | COMPLETED | FAILED
    orders_json     JSONB NOT NULL,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
SELECT create_hypertable('order_chains', 'created_at');
```

### 전처리

- 스프레드: 비정상 스프레드 (> 500bps) 필터링, 이전 값 대체
- 거래량 프로파일: 최근 20거래일 30분 단위 평균, NaN은 전체 평균으로 대체
- 크립토 펀딩 레이트: 정산 시각 전후 30분 구간 표시, 이상치 (> 1%) 경고
- 조건부 체인: 주문 수 1~10개 제한, 순환 참조 검출

---

## E2. Algorithm

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
from typing import Optional
import numpy as np


@dataclass
class OrderTypeDecision:
    """주문 유형 결정 결과"""
    request_id: str
    symbol: str
    side: str
    decided_type: str          # "MARKET" | "LIMIT" | "CONDITIONAL_LIMIT_BEST" | "LIMIT_IOC"
    limit_price: float | None  # LIMIT 주문 시 지정가
    urgency: float
    spread_bps: float
    volatility: float
    reason: str
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TimingRecommendation:
    """최적 타이밍 권고"""
    symbol: str
    asset_class: str
    recommended_window: str      # e.g., "10:00~10:30"
    timing_score: float          # 0.0 ~ 1.0
    avoid_windows: list[str]     # 회피 구간
    current_score: float         # 현재 시점 점수
    should_wait: bool            # True면 대기 권고
    wait_until: datetime | None
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class OrderChainPlan:
    """조건부 주문 체인 실행 계획"""
    chain_id: str
    orders: list[dict]           # [{symbol, side, qty, order_type, priority, depends_on}, ...]
    chain_type: str              # "SEQUENTIAL" | "CONDITIONAL"
    estimated_duration_sec: float
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CryptoTimingDecision:
    """크립토 24/7 타이밍 결정"""
    symbol: str
    current_session: str         # "ASIA" | "EUROPE" | "US"
    session_liquidity_score: float
    is_weekend: bool
    funding_rate: float
    next_funding_settlement: datetime
    avoid_funding_window: bool   # 정산 전후 30분 회피
    recommended_action: str      # "EXECUTE_NOW" | "WAIT" | "REDUCE_SIZE"
    confidence: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


# ──────────────────────────────────────────────
# 10. 지정가 vs 시장가 자동 결정
# ──────────────────────────────────────────────
def decide_order_type(
    urgency: float,
    spread_bps: float,
    volatility_1h: float,
    signal_confidence: float,
    side: str,
    mid_price: float,
    asset_class: str = "US_STOCK"
) -> OrderTypeDecision:
    """
    지정가 vs 시장가 자동 결정.

    Decision Logic:
    score = w_urg * urgency + w_spread * spread_factor + w_vol * vol_factor

    w_urg = 0.5, w_spread = 0.3, w_vol = 0.2
    spread_factor = min(spread_bps / 50, 1.0)   -- 스프레드 넓을수록 지정가 선호
    vol_factor = min(volatility_1h / 0.03, 1.0)  -- 변동성 높을수록 시장가 선호

    시장가 조건: urgency >= 0.7 OR (urgency >= 0.5 AND vol_factor >= 0.7)
    조건부지정가: spread_bps < 20 AND urgency < 0.7
    지정가: 그 외

    지정가 계산:
    BUY:  limit = mid_price - spread * aggression_offset
    SELL: limit = mid_price + spread * aggression_offset
    aggression_offset = 0.3 * (1 - urgency)  -- urgency 높으면 공격적 (mid에 가까움)
    """
    W_URG = 0.5
    W_SPREAD = 0.3
    W_VOL = 0.2

    spread_factor = min(spread_bps / 50.0, 1.0)
    vol_factor = min(volatility_1h / 0.03, 1.0)

    score = W_URG * urgency + W_SPREAD * spread_factor + W_VOL * vol_factor

    # 시장가 결정
    if urgency >= 0.7 or (urgency >= 0.5 and vol_factor >= 0.7):
        return OrderTypeDecision(
            request_id="",
            symbol="",
            side=side,
            decided_type="MARKET",
            limit_price=None,
            urgency=urgency,
            spread_bps=spread_bps,
            volatility=volatility_1h,
            reason=f"높은 긴급도({urgency:.2f}) 또는 변동성({volatility_1h:.4f}) → 시장가",
            confidence=round(min(0.7 + urgency * 0.3, 1.0), 4),
        )

    # 조건부 지정가 (좁은 스프레드)
    if spread_bps < 20 and urgency < 0.7:
        return OrderTypeDecision(
            request_id="",
            symbol="",
            side=side,
            decided_type="CONDITIONAL_LIMIT_BEST",
            limit_price=mid_price,  # 최유리 조건부
            urgency=urgency,
            spread_bps=spread_bps,
            volatility=volatility_1h,
            reason=f"좁은 스프레드({spread_bps:.1f}bps) → 조건부지정가(최유리)",
            confidence=round(0.8 - spread_bps / 200, 4),
        )

    # 지정가
    spread_abs = mid_price * spread_bps / 10000
    aggression_offset = 0.3 * (1.0 - urgency)
    if side == "BUY":
        limit_price = mid_price - spread_abs * aggression_offset
    else:
        limit_price = mid_price + spread_abs * aggression_offset

    return OrderTypeDecision(
        request_id="",
        symbol="",
        side=side,
        decided_type="LIMIT",
        limit_price=round(limit_price, 4),
        urgency=urgency,
        spread_bps=spread_bps,
        volatility=volatility_1h,
        reason=f"일반 조건 → 지정가 (offset={aggression_offset:.2f})",
        confidence=round(0.6 + signal_confidence * 0.2, 4),
    )


# ──────────────────────────────────────────────
# 11. 주문 타이밍 최적화
# ──────────────────────────────────────────────
def compute_timing_scores(
    intraday_data: list[dict],
    asset_class: str = "US_STOCK"
) -> list[dict]:
    """
    장 중 시간대별 타이밍 점수 계산.

    timing_score = w1 * liquidity_norm + w2 * (1 - spread_norm) + w3 * (1 - vol_norm)
    w1 = 0.4, w2 = 0.35, w3 = 0.25

    liquidity_norm = volume_i / max(volume)
    spread_norm = spread_i / max(spread)
    vol_norm = vol_i / max(vol)  (추정 변동성)
    """
    W_LIQ = 0.4
    W_SPREAD = 0.35
    W_VOL = 0.25

    if not intraday_data:
        return []

    max_vol = max(d.get("avg_volume", 1) for d in intraday_data)
    max_spread = max(d.get("avg_spread_bps", 1) for d in intraday_data)
    max_liquidity = max(d.get("liquidity_score", 0.01) for d in intraday_data)

    scores = []
    for d in intraday_data:
        liq_norm = d.get("liquidity_score", 0) / max(max_liquidity, 1e-8)
        spread_norm = d.get("avg_spread_bps", 0) / max(max_spread, 1e-8)
        # 변동성 proxy: 스프레드와 거래량의 역수 조합
        vol_proxy = spread_norm

        timing_score = W_LIQ * liq_norm + W_SPREAD * (1 - spread_norm) + W_VOL * (1 - vol_proxy)
        timing_score = round(min(max(timing_score, 0.0), 1.0), 4)

        scores.append({
            "time_bucket": d["time_bucket"],
            "timing_score": timing_score,
            "avg_volume": d.get("avg_volume", 0),
            "avg_spread_bps": d.get("avg_spread_bps", 0),
            "liquidity_score": d.get("liquidity_score", 0),
        })

    return sorted(scores, key=lambda x: x["timing_score"], reverse=True)


def recommend_timing(
    timing_scores: list[dict],
    current_time_bucket: str,
    urgency: float,
    asset_class: str = "US_STOCK"
) -> TimingRecommendation:
    """
    최적 실행 타이밍 권고.

    Rules:
    - urgency >= 0.8 → 즉시 실행 (대기 없음)
    - 현재 timing_score >= 0.7 → 즉시 실행
    - 현재 timing_score < 0.5 → 더 좋은 구간까지 대기 권고
    - 장 개시 직후 (09:00~09:30 KR, 09:30~10:00 US) → 변동성 회피 구간
    - 장 마감 직전 (15:00~15:30 KR, 15:30~16:00 US) → 변동성 회피 구간
    """
    AVOID_WINDOWS = {
        "KR_STOCK": ["09:00", "15:00"],
        "US_STOCK": ["09:30", "15:30"],
        "CRYPTO": [],  # 크립토는 별도 (B-13)
    }

    current_score = 0.5
    for s in timing_scores:
        if s["time_bucket"] == current_time_bucket:
            current_score = s["timing_score"]
            break

    best = timing_scores[0] if timing_scores else {"time_bucket": current_time_bucket, "timing_score": 0.5}
    avoid = AVOID_WINDOWS.get(asset_class, [])

    should_wait = False
    wait_until = None

    if urgency < 0.8 and current_score < 0.5 and best["timing_score"] > current_score + 0.2:
        should_wait = True
        # 다음 더 좋은 구간 찾기
        for s in timing_scores:
            if s["time_bucket"] > current_time_bucket and s["timing_score"] >= 0.6:
                wait_until = s["time_bucket"]
                break

    return TimingRecommendation(
        symbol="",
        asset_class=asset_class,
        recommended_window=f"{best['time_bucket']}~+30m",
        timing_score=best["timing_score"],
        avoid_windows=avoid,
        current_score=current_score,
        should_wait=should_wait,
        wait_until=wait_until,
        confidence=round(current_score * 0.7 + (1 - urgency) * 0.3, 4),
    )


# ──────────────────────────────────────────────
# 12. 조건부 주문 체인
# ──────────────────────────────────────────────
def build_order_chain(
    orders: list[dict],
    chain_type: str = "SEQUENTIAL"
) -> OrderChainPlan:
    """
    조건부 주문 체인 구성.

    SEQUENTIAL: 순차 실행 (A 체결 → B 실행 → C 실행)
    CONDITIONAL: 조건부 실행 (A 체결 시에만 B 실행)

    포트폴리오 리밸런싱 최적 순서:
    1. 매도 주문 먼저 (현금 확보)
    2. 매수 주문 (확보된 현금으로)
    3. 동일 방향 주문: 소형 → 대형 순서 (유동성 부족 조기 탐지)

    dependency graph:
    order[i].depends_on = order[j].order_id (j < i)
    """
    if not orders:
        raise ValueError("Empty order chain")
    if len(orders) > 10:
        raise ValueError("Order chain max 10 orders")

    # 매도 우선 정렬 (리밸런싱 최적화)
    sells = [o for o in orders if o.get("side") == "SELL"]
    buys = [o for o in orders if o.get("side") == "BUY"]

    # 매도: 소형 → 대형 (빠른 체결 우선)
    sells.sort(key=lambda x: x.get("qty", 0))
    # 매수: 소형 → 대형
    buys.sort(key=lambda x: x.get("qty", 0))

    sorted_orders = []
    prev_id = None
    for i, o in enumerate(sells + buys):
        order_entry = {
            "symbol": o["symbol"],
            "side": o["side"],
            "qty": o["qty"],
            "priority": i,
            "depends_on": prev_id if chain_type == "SEQUENTIAL" else None,
        }
        sorted_orders.append(order_entry)
        prev_id = o.get("order_id", f"chain_order_{i}")

    # 예상 실행 시간: 주문당 ~30초 (체결 대기)
    est_duration = len(sorted_orders) * 30.0

    return OrderChainPlan(
        chain_id="",
        orders=sorted_orders,
        chain_type=chain_type,
        estimated_duration_sec=est_duration,
        confidence=round(0.9 - len(sorted_orders) * 0.02, 4),
    )


# ──────────────────────────────────────────────
# 13. 크립토 24/7 타이밍
# ──────────────────────────────────────────────
def get_crypto_session(utc_hour: int) -> tuple[str, float]:
    """
    크립토 세션 판정 및 유동성 점수.

    Asia Session:   00:00~08:00 UTC → liquidity_score = 0.7
    Europe Session: 08:00~16:00 UTC → liquidity_score = 0.9
    US Session:     16:00~24:00 UTC → liquidity_score = 1.0

    Overlap (US+Asia): 00:00~02:00 UTC → 0.85
    Overlap (Asia+EU): 08:00~10:00 UTC → 0.95
    Overlap (EU+US):   14:00~16:00 UTC → 1.0
    """
    if 0 <= utc_hour < 2:
        return ("ASIA_US_OVERLAP", 0.85)
    elif 2 <= utc_hour < 8:
        return ("ASIA", 0.7)
    elif 8 <= utc_hour < 10:
        return ("ASIA_EU_OVERLAP", 0.95)
    elif 10 <= utc_hour < 14:
        return ("EUROPE", 0.9)
    elif 14 <= utc_hour < 16:
        return ("EU_US_OVERLAP", 1.0)
    elif 16 <= utc_hour < 24:
        return ("US", 1.0)
    return ("UNKNOWN", 0.5)


def decide_crypto_timing(
    symbol: str,
    qty: float,
    adv: float,
    utc_now: datetime,
    funding_rate: float,
    next_funding_settlement: datetime,
    is_weekend: bool = False
) -> CryptoTimingDecision:
    """
    크립토 24/7 타이밍 결정.

    Rules:
    1. 주말 + 대량 주문 (qty/ADV > 3%) → 수량 축소 권고
    2. 펀딩 정산 전후 30분 → 변동성 높음 → 회피 권고
    3. 아시아 세션 (비 overlap) + 대량 → 대기 권고
    4. EU/US 세션 → 즉시 실행

    funding_window_avoid: |now - next_settlement| < 30분
    weekend_penalty: 유동성 20% 감소 추정
    """
    session, base_liq_score = get_crypto_session(utc_now.hour)
    liquidity_ratio = qty / max(adv, 1)

    # 주말 패널티
    if is_weekend:
        base_liq_score *= 0.8

    # 펀딩 정산 구간 회피
    time_to_funding = abs((next_funding_settlement - utc_now).total_seconds())
    avoid_funding = time_to_funding < 1800  # 30분 이내

    # 결정
    if avoid_funding and liquidity_ratio > 0.01:
        action = "WAIT"
        reason_detail = "펀딩 정산 전후 30분 — 대기 권고"
    elif is_weekend and liquidity_ratio > 0.03:
        action = "REDUCE_SIZE"
        reason_detail = "주말 저유동성 + 대량 주문 — 수량 축소"
    elif base_liq_score < 0.75 and liquidity_ratio > 0.02:
        action = "WAIT"
        reason_detail = f"저유동성 세션({session}) — 유동성 높은 세션까지 대기"
    else:
        action = "EXECUTE_NOW"
        reason_detail = f"정상 유동성({session}) — 즉시 실행"

    confidence = round(base_liq_score * (1 - min(liquidity_ratio, 0.1) * 5), 4)

    return CryptoTimingDecision(
        symbol=symbol,
        current_session=session,
        session_liquidity_score=base_liq_score,
        is_weekend=is_weekend,
        funding_rate=funding_rate,
        next_funding_settlement=next_funding_settlement,
        avoid_funding_window=avoid_funding,
        recommended_action=action,
        confidence=max(confidence, 0.0),
    )
```

---

## E3. Output

### Output Schema

```python
@dataclass
class OrderTimingOutput:
    request_id: str
    symbol: str
    asset_class: str
    side: str
    order_type_decision: dict    # {decided_type, limit_price, reason}
    timing_recommendation: dict  # {recommended_window, timing_score, should_wait}
    chain_plan: dict | None      # 조건부 체인 시에만
    crypto_timing: dict | None   # 크립토 전용
    confidence: float
    timestamp: datetime
```

### Kafka Output Topics

| Topic | 내용 | 파티션 키 |
|-------|------|-----------|
| `order.type.decided` | 주문 유형 결정 완료 | `request_id` |
| `order.timing.recommendation` | 타이밍 권고 | `symbol` |
| `order.chain.plan` | 체인 실행 계획 | `chain_id` |
| `order.chain.step.completed` | 체인 단계별 완료 이벤트 | `chain_id` |
| `order.crypto.timing` | 크립토 타이밍 결정 | `symbol` |

### Confidence Levels

| 구간 | 의미 | 후속 액션 |
|------|------|-----------|
| ≥ 0.8 | 높은 신뢰도 — 즉시 실행 적합 | 결정된 주문 유형으로 즉시 실행 |
| 0.5 ~ 0.8 | 중간 — 타이밍 대기 권고 | 더 좋은 구간까지 대기 또는 수량 조정 |
| < 0.5 | 낮음 — 시장 비정상 | 주문 보류, 수동 확인 |

### 소비자

- `ExecutionAlgoEngine` (B-1): 결정된 주문 유형으로 실행
- `SmartOrderRouter` (B-2): 라우팅에 주문 유형 전달
- `RebalancingEngine`: 리밸런싱 체인 실행
- `DashboardService`: 타이밍 권고 및 체인 상태 표시

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod


class BaseOrderTypeDecider(ABC):
    """주문 유형 결정 기반 클래스."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}

    @abstractmethod
    def decide(self, request: dict, market_data: dict) -> OrderTypeDecision:
        pass

    @abstractmethod
    def recommend_timing(self, symbol: str, market_data: dict) -> TimingRecommendation:
        pass


class StockOrderTypeDecider(BaseOrderTypeDecider):
    """주식 (한국/미국) 주문 유형 결정기."""

    def decide(self, request: dict, market_data: dict) -> OrderTypeDecision:
        decision = decide_order_type(
            urgency=request["urgency"],
            spread_bps=market_data["spread_bps"],
            volatility_1h=market_data["volatility_1h"],
            signal_confidence=request.get("signal_confidence", 0.5),
            side=request["side"],
            mid_price=market_data["mid_price"],
            asset_class=request["asset_class"],
        )
        decision.request_id = request["request_id"]
        decision.symbol = request["symbol"]
        return decision

    def recommend_timing(self, symbol: str, market_data: dict) -> TimingRecommendation:
        scores = compute_timing_scores(
            market_data.get("intraday_data", []),
            market_data.get("asset_class", "US_STOCK"),
        )
        return recommend_timing(
            scores,
            market_data.get("current_time_bucket", "10:00"),
            market_data.get("urgency", 0.5),
            market_data.get("asset_class", "US_STOCK"),
        )


class CryptoOrderTypeDecider(BaseOrderTypeDecider):
    """크립토 주문 유형 + 24/7 타이밍 결정기."""

    def decide(self, request: dict, market_data: dict) -> OrderTypeDecision:
        decision = decide_order_type(
            urgency=request["urgency"],
            spread_bps=market_data["spread_bps"],
            volatility_1h=market_data["volatility_1h"],
            signal_confidence=request.get("signal_confidence", 0.5),
            side=request["side"],
            mid_price=market_data["mid_price"],
            asset_class="CRYPTO",
        )
        decision.request_id = request["request_id"]
        decision.symbol = request["symbol"]
        return decision

    def recommend_timing(self, symbol: str, market_data: dict) -> TimingRecommendation:
        # 크립토: 세션 기반 타이밍
        crypto_decision = decide_crypto_timing(
            symbol=symbol,
            qty=market_data.get("qty", 0),
            adv=market_data.get("adv", 1_000_000),
            utc_now=datetime.utcnow(),
            funding_rate=market_data.get("funding_rate", 0),
            next_funding_settlement=market_data.get("next_funding_settlement", datetime.utcnow()),
            is_weekend=market_data.get("is_weekend", False),
        )
        return TimingRecommendation(
            symbol=symbol,
            asset_class="CRYPTO",
            recommended_window=crypto_decision.current_session,
            timing_score=crypto_decision.session_liquidity_score,
            avoid_windows=["FUNDING_SETTLEMENT"] if crypto_decision.avoid_funding_window else [],
            current_score=crypto_decision.session_liquidity_score,
            should_wait=(crypto_decision.recommended_action != "EXECUTE_NOW"),
            wait_until=None,
            confidence=crypto_decision.confidence,
        )


class OrderChainManager:
    """조건부 주문 체인 관리자."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.active_chains: dict[str, OrderChainPlan] = {}

    def create_chain(self, orders: list[dict], chain_type: str = "SEQUENTIAL") -> OrderChainPlan:
        return build_order_chain(orders, chain_type)

    def on_step_completed(self, chain_id: str, order_index: int, fill_info: dict) -> dict | None:
        """체인 단계 완료 시 다음 주문 반환."""
        chain = self.active_chains.get(chain_id)
        if not chain:
            return None
        if order_index + 1 < len(chain.orders):
            return chain.orders[order_index + 1]
        return None  # 체인 완료

    def on_step_failed(self, chain_id: str, order_index: int, error: str) -> str:
        """체인 단계 실패 처리. 전체 체인 중단 또는 skip."""
        return "CHAIN_ABORTED"
```

---

## E5. Tech Stack Dependency

| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | >= 2.0 | Yes | 장 중 데이터 분석 |
| numpy | >= 1.24 | Yes | 점수 정규화, 수치 연산 |
| confluent-kafka | >= 2.3 | Yes | Kafka 토픽 연동 |
| psycopg2 | >= 2.9 | Yes | TimescaleDB 접속 |
| pytz | >= 2024.1 | Yes | 타임존 변환 (KST/EST/UTC) |
| asyncio | stdlib | Yes | 비동기 체인 실행 |

---

## E6. Performance Requirements

| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 주문 유형 결정 지연 | < 5ms | `time.perf_counter()` — 1건 기준 |
| 타이밍 스코어 계산 | < 10ms | 30분 단위 × 13구간 (KR) |
| 체인 계획 생성 | < 5ms | 10개 주문 체인 |
| 크립토 타이밍 결정 | < 3ms | 단일 심볼 |
| 동시 처리 | 200건/초 | asyncio 기반 |
| 메모리 | < 20MB | `tracemalloc` |

---

## E7. Error Handling

| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 스프레드 데이터 누락 | 기본값 20bps 사용 + 경고 | WARNING |
| 변동성 데이터 누락 | 기본값 0.02 사용 + 경고 | WARNING |
| 장 중 데이터 전체 누락 | 타이밍 권고 불가 → 즉시 실행 fallback | HIGH |
| 체인 순환 참조 탐지 | `ValueError` raise, 체인 거부 | CRITICAL |
| 체인 주문 수 > 10 | `ValueError` raise, 체인 거부 | HIGH |
| 체인 중간 단계 체결 실패 | 전체 체인 중단, 잔여 주문 취소 | HIGH |
| 펀딩 레이트 데이터 누락 | funding_rate=0 대체, 정산 회피 비활성 | WARNING |
| 타임존 변환 실패 | UTC 기준 fallback | MEDIUM |

---

## E8. Test Criteria

### Unit Tests

| Test ID | 시나리오 | 기대 결과 |
|---------|---------|-----------|
| OTT-U01 | urgency=0.9, spread=10bps | decided_type = "MARKET" |
| OTT-U02 | urgency=0.3, spread=15bps | decided_type = "CONDITIONAL_LIMIT_BEST" |
| OTT-U03 | urgency=0.4, spread=60bps | decided_type = "LIMIT" |
| OTT-U04 | LIMIT BUY, mid=100, spread=50bps | limit_price < 100 |
| OTT-U05 | timing_scores: 10:00=0.9, 09:00=0.3 | best = "10:00" |
| OTT-U06 | current=0.3, best=0.9, urg=0.4 | should_wait = True |
| OTT-U07 | urgency=0.9 → 타이밍 무시 | should_wait = False |
| OTT-U08 | chain: SELL A, BUY B, BUY C | 순서: SELL A → BUY B → BUY C |
| OTT-U09 | chain 11 orders | ValueError |
| OTT-U10 | crypto UTC 17:00, weekday | session="US", liq=1.0 |
| OTT-U11 | crypto weekend, qty/adv=4% | action="REDUCE_SIZE" |
| OTT-U12 | crypto funding 15분 전, qty/adv=2% | action="WAIT" |

### Integration Tests

| Test ID | 시나리오 | 기대 결과 |
|---------|---------|-----------|
| OTT-I01 | Kafka 요청 → 유형 결정 → 타이밍 권고 E2E | 파이프라인 정상 |
| OTT-I02 | 체인: SELL→BUY 순차 실행 → 전체 완료 | chain status = COMPLETED |
| OTT-I03 | 체인 중간 실패 → 잔여 취소 | chain status = FAILED, 잔여 CANCELLED |
| OTT-I04 | TimescaleDB 결정 이력 저장 | order_type_decisions 정합성 |

### Acceptance Criteria

- 지정가 주문 체결률: >= 85% (30분 이내 체결)
- 시장가 대비 지정가 가격 개선: 평균 3bps 이상
- 타이밍 최적화 효과: 랜덤 시점 대비 평균 슬리피지 5bps 감소
- 체인 실행 성공률: >= 95% (정상 시장)

---

## E9. LOCK References

| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| 시장가 전환 urgency 임계치 = 0.7 | SPEC §14 | 주문 유형 분기 기준 LOCK |
| 조건부지정가 스프레드 임계치 = 20bps | SPEC §14 | 좁은 스프레드 판정 LOCK |
| 타이밍 가중치 (0.4, 0.35, 0.25) | SPEC §14 | timing_score 계산 LOCK |
| 체인 최대 주문 수 = 10 | SPEC §14 | 주문 체인 제한 LOCK |
| 크립토 세션 유동성 점수 | SPEC §14 | Asia=0.7, EU=0.9, US=1.0 LOCK |
| 펀딩 정산 회피 구간 = 30분 | SPEC §14 | 정산 전후 회피 LOCK |
| Circuit Breaker -3% | SPEC §10.2 | 일일 손실 -3% 시 주문 중단 |

---

> **L3 판정**: 9요소 전수 기재 완료 (E1~E9). **L3 PASS**. ✅
> **검증일**: 2026-03-22
