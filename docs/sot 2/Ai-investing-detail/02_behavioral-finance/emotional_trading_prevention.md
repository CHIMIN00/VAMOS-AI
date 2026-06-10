# 감정 매매 방지 메커니즘 (Emotional Trading Prevention)
> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #2 투자 심리학 & 행동재무학
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-8. 감정 매매 방지 메커니즘 (Emotional Trading Prevention)

**현재**: S7NP-110 이름만 존재
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 32 | **쿨다운 타이머(Cooldown Timer)** | 큰 손실 후 즉각적 "복수 매매(Revenge Trading)" 방지. 일정 손실(-5% 이상) 발생 시 N분간 신규 주문 유예 또는 확인 단계 추가 |
| 33 | **연속 거래 제한기** | 단시간 다수 매매(과잉 매매/Overtrading) 감지. 시간당 거래 횟수 임계치 → 초과 시 "매매 빈도 과다" 경고 + 자동 속도 제한 |
| 34 | **급등/급락 시 강제 냉각 프로토콜** | 시장 급변 시 자동 대응 아닌 "판단 유보" 모드. 5분 급등/급락 > 3% 시 → AI 분석 완료까지 수동 주문 보류 권고 |
| 35 | **야간/주말 심리 변동 필터** | 장 마감 후 뉴스에 의한 과잉 반응 방지. 프리마켓/애프터마켓 심리 변동을 정규 장 심리와 분리 분석 |

---

## E1. Input

### 데이터 스키마

```yaml
trade_event:
  trade_id: str               # UUID, 필수
  user_id: str                # 사용자 ID, 필수
  ticker: str                 # 종목 코드, 필수
  action: str                 # "buy" | "sell", 필수
  quantity: int               # 수량, 필수
  price: float                # 체결/주문 가격, 필수
  executed_at: datetime       # 체결 시각 UTC, 필수
  pnl: float | None           # 실현 손익 (sell 시), 선택
  pnl_pct: float | None       # 실현 손익률 (sell 시), 선택
  order_status: str           # "pending" | "executed" | "blocked", 필수

user_trade_history:
  user_id: str                # 사용자 ID, 필수
  recent_trades: list[dict]   # 최근 거래 리스트, 필수
  recent_pnl_total: float     # 최근 N시간 누적 손익, 필수
  trade_count_1h: int         # 최근 1시간 거래 횟수, 필수
  trade_count_24h: int        # 최근 24시간 거래 횟수, 필수
  last_loss_pct: float | None # 직전 손실률, 선택

market_volatility:
  ticker: str                 # 종목 코드, 필수
  timestamp: datetime         # 시각, 필수
  price: float                # 현재가, 필수
  change_5min_pct: float      # 최근 5분 변동률 %, 필수
  change_1h_pct: float        # 최근 1시간 변동률 %, 필수
  is_regular_hours: bool      # 정규 거래시간 여부, 필수
  session_type: str           # "regular" | "pre_market" | "after_hours" | "weekend", 필수
  vix: float | None           # 변동성 지수, 선택

sentiment_shift:
  ticker: str                 # 종목 코드, 필수
  timestamp: datetime         # 시각, 필수
  session_type: str           # "regular" | "pre_market" | "after_hours", 필수
  sentiment_score: float      # 감성 점수 -1.0~1.0, 필수
  sentiment_delta: float      # 감성 변화량, 필수
```

### 필수 필드
- `trade_event`: trade_id, user_id, ticker, action, quantity, price, executed_at, order_status
- `market_volatility`: ticker, timestamp, price, change_5min_pct, is_regular_hours, session_type

### 전처리
1. 거래 이벤트 시간 정렬: executed_at ASC
2. 사용자별 rolling window 거래 집계 (1h, 24h)
3. 시장 변동률 실시간 스트림 계산 (5분 rolling)
4. 세션 분류: 거래소 운영시간 기반 자동 매핑

---

## E2. Algorithm

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class BlockAction(Enum):
    ALLOW = "allow"                    # 정상 진행
    WARN = "warn"                      # 경고 후 확인 요청
    COOLDOWN = "cooldown"              # 일정 시간 유예
    BLOCK = "block"                    # 주문 보류
    THROTTLE = "throttle"              # 속도 제한


@dataclass
class CooldownState:
    user_id: str
    is_active: bool
    reason: str
    triggered_at: datetime
    expires_at: datetime
    remaining_seconds: int
    trigger_loss_pct: float


@dataclass
class TradeLimitState:
    user_id: str
    trade_count_1h: int
    hourly_limit: int
    is_throttled: bool
    throttle_until: Optional[datetime]
    warning_message: str


@dataclass
class MarketCoolingSignal:
    ticker: str
    is_cooling: bool
    trigger_type: str          # "surge" | "plunge" | "none"
    change_pct: float
    cooling_until: Optional[datetime]
    recommendation: str        # "hold_manual_orders" | "proceed_with_caution" | "normal"


@dataclass
class SessionSentimentFilter:
    ticker: str
    regular_sentiment: float    # 정규 장 감성
    off_hours_sentiment: float  # 장외 시간 감성
    divergence: float           # 차이
    is_overreaction: bool       # 과잉 반응 판정
    adjusted_sentiment: float   # 보정된 감성 점수


@dataclass
class EmotionalTradeDecision:
    trade_id: str
    user_id: str
    action: BlockAction
    reasons: list[str]
    cooldown_state: Optional[CooldownState]
    limit_state: Optional[TradeLimitState]
    cooling_signal: Optional[MarketCoolingSignal]
    session_filter: Optional[SessionSentimentFilter]


class EmotionalTradingPrevention:
    """#32~35: 감정 매매 방지 메커니즘 통합 클래스"""

    # ── 쿨다운 설정 ──
    LOSS_THRESHOLD_PCT: float = -5.0        # 쿨다운 트리거 손실률
    COOLDOWN_MINUTES: int = 30              # 쿨다운 시간 (분)
    SEVERE_LOSS_THRESHOLD_PCT: float = -10.0
    SEVERE_COOLDOWN_MINUTES: int = 60

    # ── 연속 거래 설정 ──
    HOURLY_TRADE_LIMIT: int = 10            # 시간당 최대 거래 횟수
    DAILY_TRADE_LIMIT: int = 50             # 일간 최대 거래 횟수
    THROTTLE_MINUTES: int = 15              # 속도 제한 시간

    # ── 급변 냉각 설정 ──
    SURGE_THRESHOLD_5MIN: float = 3.0       # 5분 급등/급락 %
    COOLING_MINUTES: int = 10               # 냉각 시간

    # ── 장외 필터 설정 ──
    OFF_HOURS_DIVERGENCE_THRESHOLD: float = 0.4  # 장외 감성 괴리 임계치
    OFF_HOURS_DISCOUNT_FACTOR: float = 0.5       # 장외 감성 할인율

    def __init__(self):
        self._cooldowns: dict[str, CooldownState] = {}   # user_id -> state
        self._throttles: dict[str, TradeLimitState] = {}

    # ── 통합 판단 진입점 ──────────────────────────────────
    def evaluate_trade(
        self,
        trade: dict,
        user_history: dict,
        market: dict,
        sentiment: Optional[dict] = None
    ) -> EmotionalTradeDecision:
        """매매 요청에 대한 감정 매매 종합 판단"""
        reasons: list[str] = []
        action = BlockAction.ALLOW

        # #32 쿨다운 체크
        cooldown = self.check_cooldown(
            trade["user_id"],
            user_history.get("last_loss_pct")
        )
        if cooldown.is_active:
            reasons.append(f"쿨다운 활성: {cooldown.reason}")
            action = BlockAction.COOLDOWN

        # #33 연속 거래 제한 체크
        limit = self.check_trade_limit(
            trade["user_id"],
            user_history["trade_count_1h"],
            user_history.get("trade_count_24h", 0)
        )
        if limit.is_throttled:
            reasons.append(f"거래 제한: {limit.warning_message}")
            if action == BlockAction.ALLOW:
                action = BlockAction.THROTTLE

        # #34 급변 냉각 체크
        cooling = self.check_market_cooling(
            trade["ticker"],
            market["change_5min_pct"]
        )
        if cooling.is_cooling:
            reasons.append(f"시장 냉각: {cooling.trigger_type} {cooling.change_pct:.1f}%")
            if action in (BlockAction.ALLOW, BlockAction.WARN, BlockAction.COOLDOWN):
                action = BlockAction.BLOCK

        # #35 장외 심리 필터
        session_filter: Optional[SessionSentimentFilter] = None
        if sentiment and not market.get("is_regular_hours", True):
            session_filter = self.filter_off_hours_sentiment(
                trade["ticker"],
                sentiment.get("regular_sentiment", 0.0),
                sentiment.get("off_hours_sentiment", 0.0)
            )
            if session_filter.is_overreaction:
                reasons.append("장외 시간 과잉 반응 감지")
                if action == BlockAction.ALLOW:
                    action = BlockAction.WARN

        if not reasons:
            reasons.append("감정 매매 위험 없음")

        return EmotionalTradeDecision(
            trade_id=trade["trade_id"],
            user_id=trade["user_id"],
            action=action,
            reasons=reasons,
            cooldown_state=cooldown if cooldown.is_active else None,
            limit_state=limit if limit.is_throttled else None,
            cooling_signal=cooling if cooling.is_cooling else None,
            session_filter=session_filter
        )

    # ── #32 쿨다운 타이머 ──────────────────────────────────
    def check_cooldown(
        self,
        user_id: str,
        last_loss_pct: Optional[float]
    ) -> CooldownState:
        """큰 손실 후 복수 매매 방지 쿨다운"""
        now = datetime.utcnow()

        # 기존 쿨다운 유효성 확인
        if user_id in self._cooldowns:
            existing = self._cooldowns[user_id]
            if existing.expires_at > now:
                existing.remaining_seconds = int((existing.expires_at - now).total_seconds())
                return existing
            else:
                del self._cooldowns[user_id]

        # 새 쿨다운 트리거
        if last_loss_pct is not None and last_loss_pct <= self.LOSS_THRESHOLD_PCT:
            if last_loss_pct <= self.SEVERE_LOSS_THRESHOLD_PCT:
                minutes = self.SEVERE_COOLDOWN_MINUTES
                reason = f"심각한 손실 ({last_loss_pct:.1f}%) → {minutes}분 쿨다운"
            else:
                minutes = self.COOLDOWN_MINUTES
                reason = f"손실 ({last_loss_pct:.1f}%) → {minutes}분 쿨다운"

            state = CooldownState(
                user_id=user_id,
                is_active=True,
                reason=reason,
                triggered_at=now,
                expires_at=now + timedelta(minutes=minutes),
                remaining_seconds=minutes * 60,
                trigger_loss_pct=last_loss_pct
            )
            self._cooldowns[user_id] = state
            return state

        return CooldownState(
            user_id=user_id,
            is_active=False,
            reason="",
            triggered_at=now,
            expires_at=now,
            remaining_seconds=0,
            trigger_loss_pct=0.0
        )

    # ── #33 연속 거래 제한기 ──────────────────────────────
    def check_trade_limit(
        self,
        user_id: str,
        trade_count_1h: int,
        trade_count_24h: int = 0
    ) -> TradeLimitState:
        """단시간 과잉 매매 감지 및 속도 제한"""
        now = datetime.utcnow()

        # 기존 throttle 유효성 확인
        if user_id in self._throttles:
            existing = self._throttles[user_id]
            if existing.throttle_until and existing.throttle_until > now:
                existing.trade_count_1h = trade_count_1h
                return existing
            else:
                del self._throttles[user_id]

        is_throttled = False
        warning_msg = ""

        if trade_count_1h >= self.HOURLY_TRADE_LIMIT:
            is_throttled = True
            warning_msg = f"시간당 거래 {trade_count_1h}회 (한도 {self.HOURLY_TRADE_LIMIT}회 초과). {self.THROTTLE_MINUTES}분간 속도 제한."
        elif trade_count_24h >= self.DAILY_TRADE_LIMIT:
            is_throttled = True
            warning_msg = f"일간 거래 {trade_count_24h}회 (한도 {self.DAILY_TRADE_LIMIT}회 초과). 금일 추가 거래 제한."
        elif trade_count_1h >= self.HOURLY_TRADE_LIMIT * 0.8:
            warning_msg = f"시간당 거래 {trade_count_1h}회. 한도({self.HOURLY_TRADE_LIMIT}회)에 근접 중."

        throttle_until = now + timedelta(minutes=self.THROTTLE_MINUTES) if is_throttled else None

        state = TradeLimitState(
            user_id=user_id,
            trade_count_1h=trade_count_1h,
            hourly_limit=self.HOURLY_TRADE_LIMIT,
            is_throttled=is_throttled,
            throttle_until=throttle_until,
            warning_message=warning_msg
        )

        if is_throttled:
            self._throttles[user_id] = state

        return state

    # ── #34 급등/급락 시 강제 냉각 프로토콜 ──────────────────
    def check_market_cooling(
        self,
        ticker: str,
        change_5min_pct: float
    ) -> MarketCoolingSignal:
        """시장 급변 시 판단 유보 모드"""
        now = datetime.utcnow()

        if abs(change_5min_pct) >= self.SURGE_THRESHOLD_5MIN:
            trigger_type = "surge" if change_5min_pct > 0 else "plunge"
            return MarketCoolingSignal(
                ticker=ticker,
                is_cooling=True,
                trigger_type=trigger_type,
                change_pct=change_5min_pct,
                cooling_until=now + timedelta(minutes=self.COOLING_MINUTES),
                recommendation="hold_manual_orders"
            )

        if abs(change_5min_pct) >= self.SURGE_THRESHOLD_5MIN * 0.7:
            return MarketCoolingSignal(
                ticker=ticker,
                is_cooling=False,
                trigger_type="none",
                change_pct=change_5min_pct,
                cooling_until=None,
                recommendation="proceed_with_caution"
            )

        return MarketCoolingSignal(
            ticker=ticker,
            is_cooling=False,
            trigger_type="none",
            change_pct=change_5min_pct,
            cooling_until=None,
            recommendation="normal"
        )

    # ── #35 야간/주말 심리 변동 필터 ──────────────────────
    def filter_off_hours_sentiment(
        self,
        ticker: str,
        regular_sentiment: float,
        off_hours_sentiment: float
    ) -> SessionSentimentFilter:
        """장외 시간 감성 변동을 정규 장과 분리 분석"""
        divergence = abs(off_hours_sentiment - regular_sentiment)
        is_overreaction = divergence >= self.OFF_HOURS_DIVERGENCE_THRESHOLD

        # 보정된 감성: 장외 감성에 할인율 적용
        if is_overreaction:
            adjusted = (
                regular_sentiment * (1 - self.OFF_HOURS_DISCOUNT_FACTOR) +
                off_hours_sentiment * self.OFF_HOURS_DISCOUNT_FACTOR
            )
        else:
            adjusted = off_hours_sentiment

        return SessionSentimentFilter(
            ticker=ticker,
            regular_sentiment=regular_sentiment,
            off_hours_sentiment=off_hours_sentiment,
            divergence=float(divergence),
            is_overreaction=is_overreaction,
            adjusted_sentiment=float(adjusted)
        )
```

---

## E3. Output

### 출력 스키마

```yaml
emotional_trade_decision:
  trade_id: str
  user_id: str
  action: str                 # "allow" | "warn" | "cooldown" | "block" | "throttle"
  reasons: list[str]
  confidence: float           # 판단 확신도 0.0~1.0

cooldown_output:
  user_id: str
  is_active: bool
  reason: str
  triggered_at: datetime
  expires_at: datetime
  remaining_seconds: int
  trigger_loss_pct: float

trade_limit_output:
  user_id: str
  trade_count_1h: int
  hourly_limit: int
  is_throttled: bool
  throttle_until: datetime | null
  warning_message: str

market_cooling_output:
  ticker: str
  is_cooling: bool
  trigger_type: str           # "surge" | "plunge" | "none"
  change_pct: float
  cooling_until: datetime | null
  recommendation: str

session_filter_output:
  ticker: str
  regular_sentiment: float
  off_hours_sentiment: float
  divergence: float
  is_overreaction: bool
  adjusted_sentiment: float
```

### Confidence 산출
- **쿨다운**: 1.0 (규칙 기반, 확정적)
- **연속 거래 제한**: 1.0 (규칙 기반, 확정적)
- **급변 냉각**: min(1.0, abs(change_5min_pct) / SURGE_THRESHOLD_5MIN)
- **장외 필터**: min(1.0, data_points_count / 10) — 장외 감성 데이터 충분성

### 소비자
- `order-execution`: 주문 실행 전 게이트키퍼
- `05_risk-management`: 감정 리스크 점수
- Kafka topic: `vamos.prevention.decision`, `vamos.prevention.cooldown`, `vamos.prevention.cooling`

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod


class BaseTradeGuard(ABC):
    """매매 방어 기반 클래스"""

    @abstractmethod
    def evaluate(self, trade: dict) -> dict:
        ...

    @abstractmethod
    def get_active_blocks(self, user_id: str) -> list:
        ...


class EmotionalTradingPrevention(BaseTradeGuard):
    """
    #32~35 통합 클래스
    Inherits: BaseTradeGuard

    Public Methods:
        evaluate_trade(trade: dict, user_history: dict, market: dict, sentiment: Optional[dict]) -> EmotionalTradeDecision
        check_cooldown(user_id: str, last_loss_pct: Optional[float]) -> CooldownState
        check_trade_limit(user_id: str, trade_count_1h: int, trade_count_24h: int) -> TradeLimitState
        check_market_cooling(ticker: str, change_5min_pct: float) -> MarketCoolingSignal
        filter_off_hours_sentiment(ticker: str, regular_sentiment: float, off_hours_sentiment: float) -> SessionSentimentFilter
        evaluate(trade: dict) -> dict           # 통합 진입점
        get_active_blocks(user_id: str) -> list

    Kafka Produce:
        vamos.prevention.decision
        vamos.prevention.cooldown
        vamos.prevention.cooling

    Kafka Consume:
        vamos.trade.pending
        vamos.market.volatility
        vamos.sentiment.impact (from B-5)
    """
    pass
```

---

## E5. Tech Stack Dependency

| 구분 | 기술 | 용도 | SPEC §14 LOCK |
|------|------|------|---------------|
| 메시징 | **Kafka** | 매매 이벤트 수신, 차단 결정 발행 | ☑ LOCKED |
| 시계열DB | **TimescaleDB** | 쿨다운 상태·거래 빈도 시계열 | ☑ LOCKED |
| 데이터 처리 | **pandas** | 거래 이력 집계 | ☑ LOCKED |
| 수치 연산 | **numpy** | 변동률 계산 | ☑ LOCKED |
| ML | **scikit-learn** | 향후 감정 패턴 분류 확장용 | ☑ LOCKED |

---

## E6. Performance Requirements

| 지표 | 목표 | 비고 |
|------|------|------|
| evaluate_trade 종합 판단 | ≤ 50ms | **실시간 필수** — 주문 게이트키퍼 |
| check_cooldown | ≤ 10ms | 인메모리 상태 조회 |
| check_trade_limit | ≤ 10ms | 인메모리 카운터 |
| check_market_cooling | ≤ 10ms | 실시간 가격 스트림 |
| filter_off_hours_sentiment | ≤ 20ms | 감성 데이터 조회 |
| Kafka 메시지 처리 | ≥ 1000 msg/s | 주문 피크 시간대 |
| 상태 동기화 (쿨다운/throttle) | ≤ 100ms | 다중 인스턴스 간 |

---

## E7. Error Handling

| 오류 상황 | 처리 방식 | Fallback |
|-----------|-----------|----------|
| 거래 이력 조회 실패 | 보수적 판단 (WARN 발행) | 캐시된 마지막 상태 사용 |
| 시장 변동률 데이터 지연 | 최근 캐시값 사용 (TTL 30s) | cooling 미적용 (ALLOW) |
| 감성 데이터 없음 | 장외 필터 스킵 | 필터 미적용 |
| 쿨다운 상태 동기화 실패 | 로컬 상태 우선, 비동기 동기화 | 보수적으로 쿨다운 유지 |
| Kafka 발행 실패 | DLQ 전송, 3회 재시도 | 로컬 로그 + 알림 |
| 인메모리 상태 유실 (재시작) | TimescaleDB에서 활성 상태 복원 | 모든 쿨다운/throttle 초기화 |
| 동시 주문 race condition | 낙관적 잠금 + 원자적 카운터 | Redis 분산 잠금 |

---

## E8. Test Criteria

### Unit Tests
- [ ] `check_cooldown`: 손실 -5% → 30분 쿨다운 활성화
- [ ] `check_cooldown`: 손실 -10% → 60분 쿨다운 활성화
- [ ] `check_cooldown`: 쿨다운 만료 후 → is_active=False
- [ ] `check_cooldown`: 손실 없음 → 쿨다운 미활성
- [ ] `check_trade_limit`: 시간당 10회 → is_throttled=True
- [ ] `check_trade_limit`: 시간당 8회 → 근접 경고만 (is_throttled=False)
- [ ] `check_market_cooling`: 5분 +3.5% → is_cooling=True, trigger_type="surge"
- [ ] `check_market_cooling`: 5분 -4% → is_cooling=True, trigger_type="plunge"
- [ ] `check_market_cooling`: 5분 +1% → is_cooling=False, recommendation="normal"
- [ ] `filter_off_hours_sentiment`: 괴리 0.5 → is_overreaction=True, 할인 적용
- [ ] `filter_off_hours_sentiment`: 괴리 0.2 → is_overreaction=False
- [ ] `evaluate_trade`: 복합 조건 (쿨다운 + 급변) → BLOCK 우선

### Integration Tests
- [ ] Kafka `vamos.trade.pending` 수신 → evaluate_trade → decision 발행 E2E
- [ ] 쿨다운 상태 TimescaleDB 저장 → 서비스 재시작 → 상태 복원
- [ ] 다중 인스턴스 간 쿨다운 상태 동기화

### Acceptance Tests
- [ ] 시뮬레이션: 큰 손실(-5%) 직후 매매 시도 → 100% 쿨다운 작동
- [ ] 시뮬레이션: 시간당 15회 거래 시도 → 10회 이후 throttle 작동
- [ ] 급등/급락 3% 이벤트 10건 → 100% 냉각 프로토콜 발동
- [ ] 장외 시간 과잉 반응 시나리오 → 보정된 감성 점수 합리성 검증

---

## E9. LOCK References

| SPEC 참조 | 내용 |
|-----------|------|
| SPEC §14 | 기술스택 LOCK (Kafka, TimescaleDB, pandas, numpy, scikit-learn) |
| S7NP-110 | 감정 매매 방지 기존 명세 참조 |
| B-5 연동 | 뉴스 심리 임팩트 → 장외 심리 필터 입력 |
| B-6 연동 | 투자자 행동 패턴 → 과잉 매매 프로파일 참조 |

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
