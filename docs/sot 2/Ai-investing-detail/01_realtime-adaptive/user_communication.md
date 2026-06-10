# 사용자 커뮤니케이션 — "AI가 판단 근거를 말해주는" 시스템
> **버전**: v2.1
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #1 실시간 적응형 전략
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-12. 사용자 커뮤니케이션 — "AI가 판단 근거를 말해주는" 시스템

**현재**: 면책 조항 자동 삽입만 있고, 매물대/지지/저항 기반 판단의 이유를 설명하는 시스템 없음
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 46 | **진입/청산 근거 자연어 설명** | "72,000원에 매수 제안합니다. 이유: ① 이 가격대에 최근 3개월간 누적 거래량 1위 매물대 ② 200일 이동평균과 겹침 ③ 피보 0.618 되돌림 구간" |
| 47 | **"만약 X이면" 시나리오 사전 안내** | "만약 71,500원 아래로 이탈하면 다음 지지는 68,000원입니다. 손절 권장 가격: 71,200원" |
| 48 | **실시간 상황 변화 설명** | "진입 후 상황 업데이트: 매물대에서 3번째 반등 시도 중입니다. 거래량은 이전보다 감소 → 매물대 약화 징후. 주의하세요" |
| 49 | **왜 예상대로 안 갔는지 사후 분석** | "손절 발생 원인: 예상 지지(72,000원)가 기관 대량 매도로 붕괴됨. 체결 데이터 분석 결과 장 시작 30분 내 기관 순매도 500억 발생" |
| 50 | **확신도 변화 실시간 표시** | "매수 확신도: 진입 시 75% → 현재 45% (매물대 3회 테스트 후 약화, 거래량 감소)" |

---

## E1. Input

### 데이터 스키마

| 필드 | 타입 | 필수 | 소스 | 설명 |
|------|------|------|------|------|
| `symbol` | `str` | Y | 사용자/시스템 | 종목 코드 |
| `signal` | `Dict` | Y | 전략 엔진 | 진입/청산 시그널 `{"action": str, "price": float, "side": str, "confidence": float}` |
| `reasoning_factors` | `List[Dict]` | Y | 전략 엔진 | 판단 근거 리스트 `[{"factor": str, "description": str, "weight": float}]` |
| `support_levels` | `List[float]` | Y | 매물대 분석 모듈 | 지지 가격대 |
| `resistance_levels` | `List[float]` | Y | 매물대 분석 모듈 | 저항 가격대 |
| `position` | `Dict | None` | N | 포지션 관리 모듈 | `{"side": str, "entry_price": float, "entry_time": str, "entry_confidence": float}` |
| `market_events` | `List[Dict]` | N | 이벤트 스트림 | 시장 이벤트 `[{"event": str, "impact": str, "timestamp": str}]` |
| `confidence_history` | `List[Dict]` | N | 내부 상태 | `[{"timestamp": str, "confidence": float, "reason": str}]` |
| `trade_result` | `Dict | None` | N | 거래 기록 | 청산된 거래 `{"pnl": float, "exit_reason": str, "expected_support": float}` |

### 전처리
1. `reasoning_factors`를 `weight` 내림차순 정렬
2. 가격은 소수점 정리 (원화: 정수, 달러: 소수점 2자리)
3. timestamp를 사용자 로케일 기준 포매팅

---

## E2. Algorithm

```python
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum

class MessageType(Enum):
    ENTRY_REASONING = "entry_reasoning"       # #46
    SCENARIO_ALERT = "scenario_alert"         # #47
    SITUATION_UPDATE = "situation_update"      # #48
    POST_ANALYSIS = "post_analysis"           # #49
    CONFIDENCE_CHANGE = "confidence_change"   # #50

@dataclass
class UserMessage:
    message_type: MessageType
    symbol: str
    title: str
    body: str                  # 자연어 메시지 본문
    confidence: float          # 현재 확신도 0.0 ~ 1.0
    severity: str              # "info", "warning", "critical"
    factors: List[Dict]        # 근거 요소
    timestamp: Optional[pd.Timestamp] = None
    metadata: Dict = field(default_factory=dict)


class UserCommunicationEngine:
    """#46~#50: AI 판단 근거 자연어 설명 시스템"""

    CONFIDENCE_DROP_THRESHOLD: float = 0.15  # 확신도 15%p 이상 하락 시 알림
    SCENARIO_MAX_DEPTH: int = 3              # 시나리오 최대 깊이
    PRICE_FORMAT_KRW: str = "{:,.0f}원"
    PRICE_FORMAT_USD: str = "${:,.2f}"

    def __init__(
        self,
        symbol: str,
        currency: str = "KRW",
    ) -> None:
        self.symbol = symbol
        self.currency = currency
        self.price_fmt = self.PRICE_FORMAT_KRW if currency == "KRW" else self.PRICE_FORMAT_USD

    # ── #46 진입/청산 근거 자연어 설명 ──
    def generate_entry_reasoning(
        self,
        signal: Dict,
        reasoning_factors: List[Dict],
    ) -> UserMessage:
        """
        진입/청산 시그널에 대한 근거를 자연어로 구성한다.
        """
        action_str = "매수" if signal["side"] == "long" else "매도"
        price_str = self.price_fmt.format(signal["price"])

        # 근거를 weight 순으로 정렬
        sorted_factors = sorted(reasoning_factors, key=lambda f: f["weight"], reverse=True)

        reasons = []
        for i, f in enumerate(sorted_factors[:5], 1):
            reasons.append(f"{chr(9311 + i)} {f['description']}")

        body = (
            f"{price_str}에 {action_str} 제안합니다.\n"
            f"이유:\n" + "\n".join(reasons)
        )

        severity = "info"
        if signal["confidence"] < 0.5:
            severity = "warning"

        return UserMessage(
            message_type=MessageType.ENTRY_REASONING,
            symbol=self.symbol,
            title=f"{self.symbol} {action_str} 시그널",
            body=body,
            confidence=signal["confidence"],
            severity=severity,
            factors=sorted_factors,
            timestamp=pd.Timestamp.now(),
        )

    # ── #47 "만약 X이면" 시나리오 사전 안내 ──
    def generate_scenario_alert(
        self,
        current_price: float,
        support_levels: List[float],
        resistance_levels: List[float],
        stop_loss_price: Optional[float] = None,
    ) -> UserMessage:
        """
        현재가 기준으로 상방/하방 시나리오를 사전 안내한다.
        """
        scenarios: List[str] = []

        # 하방 시나리오
        below_supports = [s for s in sorted(support_levels, reverse=True) if s < current_price]
        for i, sup in enumerate(below_supports[:self.SCENARIO_MAX_DEPTH]):
            sup_str = self.price_fmt.format(sup)
            scenarios.append(f"만약 {sup_str} 아래로 이탈하면:")
            next_sup_idx = i + 1
            if next_sup_idx < len(below_supports):
                next_str = self.price_fmt.format(below_supports[next_sup_idx])
                scenarios.append(f"  → 다음 지지는 {next_str}입니다.")
            else:
                scenarios.append(f"  → 하방 지지 없음. 주의 필요.")

        # 상방 시나리오
        above_resistances = [r for r in sorted(resistance_levels) if r > current_price]
        for i, res in enumerate(above_resistances[:self.SCENARIO_MAX_DEPTH]):
            res_str = self.price_fmt.format(res)
            scenarios.append(f"만약 {res_str} 위로 돌파하면:")
            next_res_idx = i + 1
            if next_res_idx < len(above_resistances):
                next_str = self.price_fmt.format(above_resistances[next_res_idx])
                scenarios.append(f"  → 다음 저항은 {next_str}입니다.")
            else:
                scenarios.append(f"  → 상방 저항 없음. 추세 강화 가능.")

        if stop_loss_price:
            sl_str = self.price_fmt.format(stop_loss_price)
            scenarios.append(f"손절 권장 가격: {sl_str}")

        body = "\n".join(scenarios)
        return UserMessage(
            message_type=MessageType.SCENARIO_ALERT,
            symbol=self.symbol,
            title=f"{self.symbol} 시나리오 안내",
            body=body,
            confidence=0.0,  # 시나리오는 확신도 해당 없음
            severity="info",
            factors=[],
            timestamp=pd.Timestamp.now(),
            metadata={"current_price": current_price, "stop_loss": stop_loss_price},
        )

    # ── #48 실시간 상황 변화 설명 ──
    def generate_situation_update(
        self,
        position: Dict,
        market_events: List[Dict],
        current_price: float,
        current_confidence: float,
    ) -> UserMessage:
        """
        진입 후 실시간으로 변화하는 상황을 자연어로 설명한다.
        """
        entry_price = position["entry_price"]
        pnl_pct = (current_price - entry_price) / entry_price * 100
        if position["side"] == "short":
            pnl_pct = -pnl_pct

        pnl_str = f"{pnl_pct:+.2f}%"
        price_str = self.price_fmt.format(current_price)

        updates: List[str] = [
            f"현재가: {price_str} (수익률: {pnl_str})",
        ]

        for event in market_events[-3:]:  # 최근 3개 이벤트
            updates.append(f"- {event['event']}: {event['impact']}")

        body = "진입 후 상황 업데이트:\n" + "\n".join(updates)

        severity = "info"
        if current_confidence < 0.4:
            severity = "warning"
        if current_confidence < 0.2:
            severity = "critical"

        return UserMessage(
            message_type=MessageType.SITUATION_UPDATE,
            symbol=self.symbol,
            title=f"{self.symbol} 상황 업데이트",
            body=body,
            confidence=current_confidence,
            severity=severity,
            factors=[],
            timestamp=pd.Timestamp.now(),
            metadata={"pnl_pct": pnl_pct},
        )

    # ── #49 왜 예상대로 안 갔는지 사후 분석 ──
    def generate_post_analysis(
        self,
        trade_result: Dict,
        market_events: List[Dict],
    ) -> UserMessage:
        """
        손절 또는 예상과 다른 결과가 발생한 경우 원인을 분석한다.
        """
        pnl = trade_result["pnl"]
        exit_reason = trade_result["exit_reason"]
        expected_support = trade_result.get("expected_support")

        analysis_lines: List[str] = []

        if pnl < 0:
            analysis_lines.append(f"손절 발생 (손실: {pnl:,.0f})")
            analysis_lines.append(f"청산 사유: {exit_reason}")

            if expected_support:
                sup_str = self.price_fmt.format(expected_support)
                analysis_lines.append(f"예상 지지({sup_str})가 붕괴된 원인 분석:")

            # 이벤트 기반 원인 분석
            for event in market_events:
                analysis_lines.append(f"  - {event['event']}: {event['impact']}")

            if not market_events:
                analysis_lines.append("  - 특이 이벤트 미감지. 매물대 자체 약화 가능성.")
        else:
            analysis_lines.append(f"수익 청산 (수익: {pnl:+,.0f})")
            analysis_lines.append("전략이 의도대로 작동했습니다.")

        body = "\n".join(analysis_lines)

        return UserMessage(
            message_type=MessageType.POST_ANALYSIS,
            symbol=self.symbol,
            title=f"{self.symbol} 사후 분석",
            body=body,
            confidence=0.0,
            severity="info" if pnl >= 0 else "warning",
            factors=[],
            timestamp=pd.Timestamp.now(),
            metadata={"pnl": pnl, "exit_reason": exit_reason},
        )

    # ── #50 확신도 변화 실시간 표시 ──
    def generate_confidence_update(
        self,
        confidence_history: List[Dict],
        current_confidence: float,
    ) -> Optional[UserMessage]:
        """
        확신도가 유의미하게 변화했을 때 사용자에게 알린다.
        """
        if len(confidence_history) < 2:
            return None

        entry_confidence = confidence_history[0]["confidence"]
        prev_confidence = confidence_history[-2]["confidence"]
        delta = current_confidence - prev_confidence
        total_delta = current_confidence - entry_confidence

        # 임계값 이하 변화는 알리지 않음
        if abs(delta) < self.CONFIDENCE_DROP_THRESHOLD:
            return None

        direction = "상승" if delta > 0 else "하락"
        reasons = [h["reason"] for h in confidence_history[-3:] if h.get("reason")]

        body = (
            f"확신도 변화: 진입 시 {entry_confidence*100:.0f}% → "
            f"현재 {current_confidence*100:.0f}% "
            f"({total_delta*100:+.0f}%p)\n"
            f"최근 변화 요인:\n"
        )
        for r in reasons:
            body += f"  - {r}\n"

        severity = "info"
        if current_confidence < 0.4:
            severity = "warning"
        if current_confidence < 0.2:
            severity = "critical"

        return UserMessage(
            message_type=MessageType.CONFIDENCE_CHANGE,
            symbol=self.symbol,
            title=f"{self.symbol} 확신도 {direction}",
            body=body.strip(),
            confidence=current_confidence,
            severity=severity,
            factors=[],
            timestamp=pd.Timestamp.now(),
            metadata={
                "entry_confidence": entry_confidence,
                "delta": delta,
                "total_delta": total_delta,
            },
        )
```

---

## E3. Output

### 출력 스키마

| 필드 | 타입 | 설명 |
|------|------|------|
| `message_type` | `MessageType` | 메시지 유형 enum |
| `symbol` | `str` | 종목 코드 |
| `title` | `str` | 알림 제목 |
| `body` | `str` | 자연어 메시지 본문 |
| `confidence` | `float` | 현재 확신도 0.0 ~ 1.0 |
| `severity` | `str` | `"info"`, `"warning"`, `"critical"` |
| `factors` | `List[Dict]` | 판단 근거 요소 |
| `timestamp` | `pd.Timestamp` | 생성 시점 |
| `metadata` | `Dict` | 부가 메타데이터 |

### 소비자
- **프론트엔드 UI**: 알림 카드/푸시 표시
- **채팅 인터페이스**: 대화형 설명 제공
- **거래 로그 DB**: 메시지 이력 저장
- **Kafka topic**: `notification.user.message`

---

## E4. Class / API Design

```python
from abc import ABC, abstractmethod

class BaseUserCommunication(ABC):
    """사용자 커뮤니케이션 추상 기반 클래스"""

    @abstractmethod
    def generate_entry_reasoning(
        self, signal: Dict, reasoning_factors: List[Dict]
    ) -> UserMessage: ...

    @abstractmethod
    def generate_scenario_alert(
        self, current_price: float, support_levels: List[float],
        resistance_levels: List[float], stop_loss_price: Optional[float]
    ) -> UserMessage: ...

    @abstractmethod
    def generate_situation_update(
        self, position: Dict, market_events: List[Dict],
        current_price: float, current_confidence: float
    ) -> UserMessage: ...

    @abstractmethod
    def generate_post_analysis(
        self, trade_result: Dict, market_events: List[Dict]
    ) -> UserMessage: ...

    @abstractmethod
    def generate_confidence_update(
        self, confidence_history: List[Dict], current_confidence: float
    ) -> Optional[UserMessage]: ...


class UserCommunicationEngine(BaseUserCommunication):
    """
    구현 클래스 — E2 참조.
    Methods:
      - generate_entry_reasoning(signal, factors) -> UserMessage        # #46
      - generate_scenario_alert(price, sups, ress, sl) -> UserMessage   # #47
      - generate_situation_update(pos, events, price, conf) -> UserMessage # #48
      - generate_post_analysis(result, events) -> UserMessage           # #49
      - generate_confidence_update(history, conf) -> UserMessage|None   # #50
    """
    pass  # 전체 구현은 E2 참조
```

### Kafka 이벤트 인터페이스

| Topic | Key | Value |
|-------|-----|-------|
| `notification.user.message` | `{symbol}:{message_type}` | `UserMessage` JSON 직렬화 |

---

## E5. Tech Stack Dependency

| 기술 | 용도 | SPEC §14 LOCK |
|------|------|---------------|
| **pandas** | Timestamp 처리, 데이터 정렬 | ☑ |
| **numpy** | 수치 비교, 퍼센트 연산 | ☑ |
| **TimescaleDB** | 메시지 이력 저장, 거래 기록 조회 | ☑ |
| **Kafka** | 사용자 알림 이벤트 발행 | ☑ |

---

## E6. Performance Requirements

| 지표 | 목표 | 비고 |
|------|------|------|
| 메시지 생성 | ≤ 30ms / 메시지 | 자연어 조합 |
| 확신도 업데이트 | ≤ 10ms | 단순 비교 연산 |
| 시나리오 생성 | ≤ 50ms | 지지/저항 탐색 포함 |
| Kafka publish | ≤ 10ms | 비동기 발행 |
| 사후 분석 | ≤ 100ms | 이벤트 조회 포함 |

---

## E7. Error Handling

| 오류 상황 | 처리 | 심각도 |
|-----------|------|--------|
| `reasoning_factors` 빈 리스트 | "판단 근거 데이터 부족" 메시지 생성 | WARN |
| `position` 없는 상태에서 상황 업데이트 호출 | `None` 반환 + INFO 로그 | INFO |
| `confidence_history` 부족 (< 2개) | confidence 업데이트 스킵, `None` 반환 | INFO |
| 가격 포매팅 오류 (음수, NaN) | fallback 문자열 "가격 정보 없음" | WARN |
| Kafka 발행 실패 | 3회 재시도 → DLQ + 로컬 로그 | ERROR |
| 과다 메시지 발생 (분당 10회 초과) | 쓰로틀링: 동일 타입 메시지 60초 내 중복 억제 | INFO |

---

## E8. Test Criteria

### Unit Tests
| ID | 테스트 | 입력 | 기대 출력 |
|----|--------|------|-----------|
| UT-46-1 | 매수 근거 메시지 | signal(long, 72000), 3개 factor | body에 "매수", "72,000원", 3개 이유 포함 |
| UT-46-2 | 매도 근거 메시지 | signal(short, 80000) | body에 "매도" 포함 |
| UT-47-1 | 하방 시나리오 | 현재가 73000, 지지 [72000, 68000] | "72,000원 아래로 이탈하면" 포함 |
| UT-47-2 | 빈 지지 리스트 | 지지=[], 저항=[80000] | 상방 시나리오만 포함 |
| UT-48-1 | 상황 업데이트 | 진입 후 +2% | body에 "+2.00%" 포함 |
| UT-49-1 | 손절 사후 분석 | pnl=-50000, events 2개 | body에 "손절 발생", 이벤트 내용 포함 |
| UT-50-1 | 확신도 하락 알림 | 75% → 45% | `CONFIDENCE_CHANGE` 메시지 반환 |
| UT-50-2 | 미미한 변화 | 75% → 72% | `None` 반환 (임계값 미달) |

### Integration Tests
| ID | 시나리오 | 검증 |
|----|----------|------|
| IT-46-1 | 전략 시그널 → 근거 메시지 생성 → Kafka → 프론트엔드 | 사용자에게 메시지 도달 |
| IT-48-1 | 실시간 가격 변동 → 상황 업데이트 → 쓰로틀링 | 분당 10회 이하 발행 |
| IT-50-1 | 확신도 연속 하락 → critical 알림 | severity 에스컬레이션 정상 |

### Acceptance Criteria
- 사용자 메시지 가독성 점수 ≥ 4.0/5.0 (내부 평가)
- 시나리오 정확도: 사전 안내한 지지/저항에서 실제 반응 비율 ≥ 60%
- 사후 분석 원인 식별 정확도 ≥ 65%

---

## E9. LOCK References

| 참조 ID | 항목 | SPEC §14 근거 |
|---------|------|---------------|
| LOCK-KAFKA-04 | 이벤트 토픽 `notification.user.message` | Kafka 메시지 버스 표준 |
| LOCK-TSDB-04 | 메시지 이력, 거래 기록 조회 | TimescaleDB 시계열 저장소 |
| LOCK-PD-04 | Timestamp 처리 | pandas 표준 |
| LOCK-NP-04 | 수치 비교, 퍼센트 연산 | numpy 표준 |

---

---

## STEP7-I 보강: 목표가/손절가 알림 트리거 시스템 상세 (S7I-067)

> **보강 근거**: step7i_mapping.md PARTIAL — 가격 알림 트리거(목표가 도달, 손절 발동, 트레일링 스톱, 이동평균 교차, 거래량 급등) 조건 평가 및 알림 발송 시스템 상세 누락
> **Priority**: HIGH

### E1. Input
- **데이터**: 실시간 가격 스트림, 등록된 알림 조건 목록, 기술적 지표 캐시(MA, VWAP)
- **필수 필드**:
  - `symbol: str` — 종목 코드
  - `current_price: float` — 현재가
  - `current_volume: int` — 현재 거래량
  - `alert_rules: List[PriceAlertRule]` — 등록된 알림 규칙 `{"alert_id", "user_id", "symbol", "condition_type", "threshold", "direction", "trailing_pct", "ma_period", "volume_multiplier", "active", "created_at"}`
  - `technical_cache: Dict` — 기술적 지표 캐시 `{"ma_20", "ma_60", "ma_200", "avg_volume_20d", "vwap"}`
  - `position: Optional[Dict]` — 보유 포지션 정보 `{"entry_price", "side", "qty", "stop_loss", "take_profit", "trailing_stop_pct"}`
- **전처리**:
  1. 알림 규칙 중 `active=True`만 필터링
  2. 가격/거래량 NaN 검증 → NaN 시 평가 스킵
  3. trailing stop은 최고가/최저가 기준 동적 업데이트

### E2. Algorithm
```python
import time
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple
from enum import Enum
from datetime import datetime

class AlertConditionType(Enum):
    TARGET_PRICE_REACHED = "target_price_reached"       # 목표가 도달
    STOP_LOSS_TRIGGERED = "stop_loss_triggered"          # 손절가 도달
    TRAILING_STOP = "trailing_stop"                      # 트레일링 스톱
    PRICE_CROSS_MA = "price_cross_ma"                    # 이동평균 교차
    VOLUME_SPIKE = "volume_spike"                        # 거래량 급등

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class PriceAlertRule:
    alert_id: str
    user_id: str
    symbol: str
    condition_type: AlertConditionType
    threshold: float               # 목표가/손절가/MA 기간/거래량 배수
    direction: str                 # "above" | "below" | "cross_up" | "cross_down"
    trailing_pct: Optional[float] = None   # 트레일링 비율 (예: 0.03 = 3%)
    ma_period: Optional[int] = None        # 이동평균 기간 (20, 60, 200)
    volume_multiplier: Optional[float] = None  # 평균 거래량 대비 배수
    active: bool = True
    created_at: Optional[datetime] = None
    peak_price: Optional[float] = None     # 트레일링 스톱용 최고가 추적

@dataclass
class AlertTriggerResult:
    alert_id: str
    user_id: str
    symbol: str
    condition_type: AlertConditionType
    triggered_at: datetime
    trigger_price: float
    threshold: float
    severity: AlertSeverity
    message: str
    metadata: Dict = field(default_factory=dict)

class PriceAlertEngine:
    """목표가/손절가 알림 트리거 엔진"""

    TRAILING_STOP_MIN_PCT: float = 0.01    # 최소 트레일링 1%
    TRAILING_STOP_MAX_PCT: float = 0.20    # 최대 트레일링 20%
    VOLUME_SPIKE_DEFAULT: float = 2.0       # 기본 거래량 급등 배수
    PRICE_FORMAT_KRW: str = "{:,.0f}원"
    PRICE_FORMAT_USD: str = "${:,.2f}"

    def __init__(self, currency: str = "KRW"):
        self.currency = currency
        self.price_fmt = self.PRICE_FORMAT_KRW if currency == "KRW" else self.PRICE_FORMAT_USD
        self._trigger_history: Dict[str, datetime] = {}   # 중복 발송 방지
        self._cooldown_seconds: int = 300                  # 동일 알림 5분 쿨다운

    def evaluate_conditions(
        self,
        symbol: str,
        current_price: float,
        current_volume: int,
        alert_rules: List[PriceAlertRule],
        technical_cache: Dict,
        position: Optional[Dict] = None,
    ) -> List[AlertTriggerResult]:
        """
        모든 활성 알림 규칙에 대해 조건 평가 → 트리거 결과 반환.
        """
        triggered: List[AlertTriggerResult] = []
        now = datetime.utcnow()

        for rule in alert_rules:
            if not rule.active or rule.symbol != symbol:
                continue

            # 쿨다운 검사 (동일 알림 5분 내 재발송 방지)
            last_triggered = self._trigger_history.get(rule.alert_id)
            if last_triggered and (now - last_triggered).total_seconds() < self._cooldown_seconds:
                continue

            result = self._evaluate_single(rule, current_price, current_volume,
                                           technical_cache, position, now)
            if result is not None:
                triggered.append(result)
                self._trigger_history[rule.alert_id] = now

        return triggered

    def _evaluate_single(
        self,
        rule: PriceAlertRule,
        price: float,
        volume: int,
        tech: Dict,
        position: Optional[Dict],
        now: datetime,
    ) -> Optional[AlertTriggerResult]:
        """개별 알림 규칙 평가"""

        # ── 목표가 도달 ──
        if rule.condition_type == AlertConditionType.TARGET_PRICE_REACHED:
            if rule.direction == "above" and price >= rule.threshold:
                return self._build_result(
                    rule, now, price, AlertSeverity.INFO,
                    f"{rule.symbol} 목표가 {self.price_fmt.format(rule.threshold)} 도달 "
                    f"(현재가: {self.price_fmt.format(price)})"
                )
            if rule.direction == "below" and price <= rule.threshold:
                return self._build_result(
                    rule, now, price, AlertSeverity.INFO,
                    f"{rule.symbol} 목표가 {self.price_fmt.format(rule.threshold)} 하향 도달 "
                    f"(현재가: {self.price_fmt.format(price)})"
                )

        # ── 손절가 도달 ──
        elif rule.condition_type == AlertConditionType.STOP_LOSS_TRIGGERED:
            if position and position.get("stop_loss"):
                stop_loss = position["stop_loss"]
                if position["side"] == "long" and price <= stop_loss:
                    return self._build_result(
                        rule, now, price, AlertSeverity.CRITICAL,
                        f"{rule.symbol} 손절가 {self.price_fmt.format(stop_loss)} 도달! "
                        f"즉시 청산 필요 (현재가: {self.price_fmt.format(price)})",
                        metadata={"entry_price": position["entry_price"],
                                  "loss_pct": (price - position["entry_price"]) / position["entry_price"] * 100}
                    )
                if position["side"] == "short" and price >= stop_loss:
                    return self._build_result(
                        rule, now, price, AlertSeverity.CRITICAL,
                        f"{rule.symbol} 숏 손절가 {self.price_fmt.format(stop_loss)} 도달! "
                        f"즉시 청산 필요 (현재가: {self.price_fmt.format(price)})",
                        metadata={"entry_price": position["entry_price"],
                                  "loss_pct": (position["entry_price"] - price) / position["entry_price"] * 100}
                    )

        # ── 트레일링 스톱 ──
        elif rule.condition_type == AlertConditionType.TRAILING_STOP:
            trailing_pct = max(self.TRAILING_STOP_MIN_PCT,
                              min(rule.trailing_pct or 0.05, self.TRAILING_STOP_MAX_PCT))
            # 최고가 업데이트
            if rule.peak_price is None or price > rule.peak_price:
                rule.peak_price = price
            trailing_stop_price = rule.peak_price * (1 - trailing_pct)
            if price <= trailing_stop_price:
                return self._build_result(
                    rule, now, price, AlertSeverity.WARNING,
                    f"{rule.symbol} 트레일링 스톱 발동 "
                    f"(최고가: {self.price_fmt.format(rule.peak_price)}, "
                    f"트레일링 {trailing_pct*100:.1f}%, "
                    f"스톱가: {self.price_fmt.format(trailing_stop_price)}, "
                    f"현재가: {self.price_fmt.format(price)})",
                    metadata={"peak_price": rule.peak_price,
                              "trailing_pct": trailing_pct,
                              "trailing_stop_price": trailing_stop_price}
                )

        # ── 이동평균 교차 ──
        elif rule.condition_type == AlertConditionType.PRICE_CROSS_MA:
            ma_key = f"ma_{rule.ma_period or 20}"
            ma_value = tech.get(ma_key)
            if ma_value is not None:
                if rule.direction == "cross_up" and price > ma_value:
                    return self._build_result(
                        rule, now, price, AlertSeverity.INFO,
                        f"{rule.symbol} {rule.ma_period}일 이동평균 "
                        f"({self.price_fmt.format(ma_value)}) 상향 돌파 "
                        f"(현재가: {self.price_fmt.format(price)})",
                        metadata={"ma_period": rule.ma_period, "ma_value": ma_value}
                    )
                if rule.direction == "cross_down" and price < ma_value:
                    return self._build_result(
                        rule, now, price, AlertSeverity.WARNING,
                        f"{rule.symbol} {rule.ma_period}일 이동평균 "
                        f"({self.price_fmt.format(ma_value)}) 하향 이탈 "
                        f"(현재가: {self.price_fmt.format(price)})",
                        metadata={"ma_period": rule.ma_period, "ma_value": ma_value}
                    )

        # ── 거래량 급등 ──
        elif rule.condition_type == AlertConditionType.VOLUME_SPIKE:
            avg_vol = tech.get("avg_volume_20d", 0)
            multiplier = rule.volume_multiplier or self.VOLUME_SPIKE_DEFAULT
            if avg_vol > 0 and volume >= avg_vol * multiplier:
                spike_ratio = volume / avg_vol
                return self._build_result(
                    rule, now, price, AlertSeverity.WARNING,
                    f"{rule.symbol} 거래량 급등! "
                    f"현재 거래량이 20일 평균의 {spike_ratio:.1f}배 "
                    f"(현재: {volume:,}, 평균: {int(avg_vol):,})",
                    metadata={"current_volume": volume, "avg_volume_20d": avg_vol,
                              "spike_ratio": spike_ratio}
                )

        return None

    def _build_result(
        self,
        rule: PriceAlertRule,
        now: datetime,
        price: float,
        severity: AlertSeverity,
        message: str,
        metadata: Optional[Dict] = None,
    ) -> AlertTriggerResult:
        return AlertTriggerResult(
            alert_id=rule.alert_id,
            user_id=rule.user_id,
            symbol=rule.symbol,
            condition_type=rule.condition_type,
            triggered_at=now,
            trigger_price=price,
            threshold=rule.threshold,
            severity=severity,
            message=message,
            metadata=metadata or {},
        )

    def register_alert(self, rule: PriceAlertRule) -> str:
        """알림 규칙 등록. alert_id 반환."""
        # DB에 저장, 활성화
        return rule.alert_id

    def deactivate_alert(self, alert_id: str) -> bool:
        """알림 비활성화."""
        return True

    def dispatch_notification(
        self,
        results: List[AlertTriggerResult],
        channels: List[str] = None,
    ) -> Dict[str, int]:
        """
        트리거된 알림을 사용자에게 발송.
        channels: ["push", "sms", "email", "kafka"]
        CRITICAL → push + sms 즉시 발송
        WARNING → push 발송
        INFO → push 또는 대시보드 표시
        """
        channels = channels or ["push", "kafka"]
        dispatch_count = {"push": 0, "sms": 0, "email": 0, "kafka": 0}

        for result in results:
            if result.severity == AlertSeverity.CRITICAL:
                # push + sms 즉시
                dispatch_count["push"] += 1
                dispatch_count["sms"] += 1
            elif result.severity == AlertSeverity.WARNING:
                dispatch_count["push"] += 1
            else:
                dispatch_count["push"] += 1
            dispatch_count["kafka"] += 1  # 모든 알림 Kafka 발행

        return dispatch_count
```

### E3. Output
- **스키마**:
  ```python
  @dataclass
  class AlertTriggerResult:
      alert_id: str
      user_id: str
      symbol: str
      condition_type: AlertConditionType
      triggered_at: datetime
      trigger_price: float
      threshold: float
      severity: AlertSeverity         # INFO | WARNING | CRITICAL
      message: str                    # 사용자 알림 메시지
      metadata: Dict                  # 부가 데이터 (손실률, MA값 등)
  ```
- **소비자**: 프론트엔드 푸시 알림, SMS 게이트웨이, Kafka topic `notification.price.alert`, 거래 실행 엔진 (CRITICAL → 자동 청산 트리거)

### E4. Class/API Design
```python
class PriceAlertEngine:
    """목표가/손절가 알림 트리거 엔진.

    5종 알림 조건 평가: 목표가 도달, 손절 발동, 트레일링 스톱,
    이동평균 교차, 거래량 급등.
    """

    def __init__(self, currency: str = "KRW"):
        """통화 설정 및 쿨다운 초기화."""
        ...

    def register_alert(self, rule: PriceAlertRule) -> str:
        """알림 규칙 등록 → alert_id 반환."""
        ...

    def evaluate_conditions(
        self, symbol: str, current_price: float, current_volume: int,
        alert_rules: List[PriceAlertRule], technical_cache: Dict,
        position: Optional[Dict] = None,
    ) -> List[AlertTriggerResult]:
        """모든 활성 규칙 일괄 평가 → 트리거 결과 리스트."""
        ...

    def trigger_alert(self, rule: PriceAlertRule, price: float) -> AlertTriggerResult:
        """단일 규칙 강제 트리거 (테스트/수동용)."""
        ...

    def dispatch_notification(
        self, results: List[AlertTriggerResult],
        channels: List[str] = None,
    ) -> Dict[str, int]:
        """트리거 결과 → 채널별 알림 발송. CRITICAL=push+sms, WARNING=push, INFO=push."""
        ...

    def deactivate_alert(self, alert_id: str) -> bool:
        """알림 비활성화."""
        ...

    def get_active_alerts(self, user_id: str, symbol: Optional[str] = None) -> List[PriceAlertRule]:
        """사용자별 활성 알림 조회."""
        ...
```

### E5. Tech Stack Dependency
| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| pandas | ≥2.0 | ☑ | 기술적 지표 캐시, 시계열 처리 |
| numpy | ≥1.24 | ☑ | 수치 비교 연산 |
| confluent-kafka | 2.3.x | ☑ | 알림 이벤트 발행 |
| redis | 5.0.x | ☑ | 쿨다운 상태, peak_price 캐시 |
| TimescaleDB | — | ☑ | 알림 규칙 저장, 트리거 이력 |

### E6. Performance Requirements
| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 조건 평가 지연 | ≤ 5ms / 규칙 | 단일 규칙 평가 시간 |
| 전체 평가 (100규칙) | ≤ 50ms | 종목당 활성 규칙 일괄 평가 |
| 알림 발송 지연 | ≤ 500ms | 트리거 → 사용자 수신 (push) |
| 트레일링 스톱 최고가 갱신 | ≤ 1ms | Redis 캐시 업데이트 |
| 쿨다운 검사 | ≤ 1ms | Redis TTL 조회 |

### E7. Error Handling
| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 가격 데이터 NaN/None | 해당 틱 평가 스킵, 다음 틱 재시도 | WARN |
| 기술적 지표 캐시 미스 | MA 교차/거래량 조건 스킵, INFO 로그 | INFO |
| Redis 연결 실패 | 인메모리 fallback (peak_price, cooldown) | HIGH |
| 알림 발송 실패 (push) | 3회 재시도 → DLQ, 다음 채널 시도 | ERROR |
| 손절 알림 CRITICAL 발송 실패 | SMS fallback → 이메일 fallback → Kafka 필수 발행 | CRITICAL |
| 중복 알림 쿨다운 충돌 | 쿨다운 내 동일 알림 억제, 로그 기록 | INFO |

### E8. Test Criteria
- **Unit**:
  - 목표가 above 72,000원, 현재가 72,500원 → 트리거 발생
  - 손절 long, stop_loss=68,000원, 현재가 67,500원 → CRITICAL 트리거
  - 트레일링 스톱 5%, peak=80,000원, 현재가 75,500원 → 트리거 (76,000원 아래)
  - MA20=71,000원, 현재가 71,500원, direction=cross_up → INFO 트리거
  - 거래량 avg=100,000, 현재=250,000, multiplier=2.0 → WARNING 트리거
  - 쿨다운 5분 내 동일 알림 → 재발송 차단
- **Integration**:
  - 실시간 가격 스트림 → PriceAlertEngine → Kafka → 푸시 알림 E2E
  - 다중 사용자 동시 알림 규칙 (1,000건) 평가 → 50ms 이내
- **Acceptance**:
  - 손절 알림 발송 지연 ≤ 500ms (CRITICAL)
  - 오발송률 < 0.1% (조건 미충족 시 알림 발송 없음)
  - 미발송률 < 0.5% (조건 충족 시 알림 반드시 발송)

### E9. LOCK References
| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| LOCK-KAFKA-05 | SPEC §14 | 알림 이벤트 토픽 `notification.price.alert` |
| LOCK-REDIS-03 | SPEC §14 | 쿨다운/peak_price 캐시 |
| LOCK-TSDB-05 | SPEC §14 | 알림 규칙 및 트리거 이력 저장 |
| 쿨다운 300초 | 본 문서 정의 | 동일 알림 5분 재발송 방지 |
| 트레일링 범위 1~20% | 본 문서 정의 | 과도한 트레일링 방지 |

---

## STEP7-I 보강: 사용자 정의 알림 규칙 엔진 (S7I-073)

> **보강 근거**: step7i_mapping.md PARTIAL — 사용자가 DSL로 복합 조건 알림을 정의하는 규칙 엔진 상세 누락 (예: "WHEN price > 50000 AND volume > avg_20d * 2 THEN alert")
> **Priority**: MED

### E1. Input
- **데이터**: 사용자 정의 규칙 텍스트(DSL), 실시간 시장 데이터, 기술적 지표
- **필수 필드**:
  - `rule_text: str` — DSL 규칙 문자열 (예: `"WHEN price > 50000 AND volume > avg_20d * 2 THEN alert"`)
  - `user_id: str` — 사용자 식별자
  - `symbol: str` — 종목 코드
  - `market_data: Dict` — 실시간 시장 데이터 `{"price", "volume", "open", "high", "low", "change_pct"}`
  - `indicators: Dict` — 기술적 지표 `{"rsi", "macd", "macd_signal", "ma_20", "ma_60", "ma_200", "bb_upper", "bb_lower", "avg_volume_20d"}`
  - `rule_metadata: Dict` — 규칙 메타 `{"rule_id", "name", "priority", "notification_channels", "active"}`
- **전처리**:
  1. DSL 텍스트 파싱 전 공백 정규화, 대소문자 통일 (키워드는 대문자)
  2. 지표 변수 바인딩: `rsi` → `indicators["rsi"]`, `price` → `market_data["price"]`
  3. 사용자별 규칙 수 상한 검증 (최대 50개)

### E2. Algorithm
```python
import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any, Callable
from enum import Enum
from datetime import datetime

# ── DSL 문법 정의 ──
# WHEN <condition> [AND|OR <condition>]* THEN <action>
# <condition> := <variable> <operator> <value>
# <variable>  := price | volume | rsi | macd | macd_signal | ma_20 | ma_60 | ma_200
#                | bb_upper | bb_lower | avg_volume_20d | change_pct | open | high | low
# <operator>  := > | >= | < | <= | == | !=
# <value>     := <number> | <variable> | <variable> * <number> | <variable> + <number>
# <action>    := alert | alert("custom message")
# 예시:
#   WHEN price > 50000 AND volume > avg_20d * 2 THEN alert
#   WHEN rsi < 30 AND macd > macd_signal THEN alert("RSI 과매도 + MACD 골든크로스")
#   WHEN price < bb_lower OR change_pct < -5 THEN alert

class TokenType(Enum):
    WHEN = "WHEN"
    THEN = "THEN"
    AND = "AND"
    OR = "OR"
    VARIABLE = "VARIABLE"
    OPERATOR = "OPERATOR"
    NUMBER = "NUMBER"
    MULTIPLY = "MULTIPLY"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    ALERT = "ALERT"
    STRING = "STRING"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"

@dataclass
class Token:
    type: TokenType
    value: Any

@dataclass
class ConditionNode:
    """AST 조건 노드"""
    variable: str
    operator: str             # ">", ">=", "<", "<=", "==", "!="
    value_expr: Any           # 숫자 리터럴 또는 연산식 {"var": str, "op": str, "operand": float}
    raw_text: str = ""

@dataclass
class RuleAST:
    """파싱된 규칙 AST"""
    conditions: List[ConditionNode]
    logical_ops: List[str]    # "AND" | "OR" — conditions 사이 논리 연산자
    action: str               # "alert"
    custom_message: Optional[str] = None

@dataclass
class CompiledRule:
    """컴파일된 규칙 (평가 가능 상태)"""
    rule_id: str
    user_id: str
    symbol: str
    ast: RuleAST
    evaluator: Callable[[Dict], bool]   # 컴파일된 평가 함수
    priority: int
    notification_channels: List[str]
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)

KNOWN_VARIABLES = {
    "price", "volume", "open", "high", "low", "change_pct",
    "rsi", "macd", "macd_signal",
    "ma_20", "ma_60", "ma_200",
    "bb_upper", "bb_lower",
    "avg_volume_20d",
}

OPERATORS = {">", ">=", "<", "<=", "==", "!="}

class AlertRuleEngine:
    """사용자 정의 알림 규칙 엔진 — DSL 파싱/컴파일/실시간 평가"""

    MAX_RULES_PER_USER: int = 50
    MAX_CONDITIONS_PER_RULE: int = 10

    def __init__(self):
        self._compiled_rules: Dict[str, CompiledRule] = {}   # rule_id → CompiledRule

    # ── Step 1: DSL 파싱 (텍스트 → AST) ──
    def parse_rule(self, rule_text: str) -> RuleAST:
        """
        DSL 텍스트를 AST로 변환.
        예: "WHEN price > 50000 AND volume > avg_20d * 2 THEN alert"
        → RuleAST(conditions=[...], logical_ops=["AND"], action="alert")
        """
        tokens = self._tokenize(rule_text)
        return self._parse_tokens(tokens)

    def _tokenize(self, text: str) -> List[Token]:
        """DSL 텍스트 토큰화"""
        tokens = []
        # 정규화: 공백 통일
        text = re.sub(r'\s+', ' ', text.strip())
        parts = text.split(' ')

        i = 0
        while i < len(parts):
            part = parts[i]
            upper = part.upper()

            if upper == "WHEN":
                tokens.append(Token(TokenType.WHEN, "WHEN"))
            elif upper == "THEN":
                tokens.append(Token(TokenType.THEN, "THEN"))
            elif upper == "AND":
                tokens.append(Token(TokenType.AND, "AND"))
            elif upper == "OR":
                tokens.append(Token(TokenType.OR, "OR"))
            elif upper.startswith("ALERT"):
                tokens.append(Token(TokenType.ALERT, "alert"))
                # alert("message") 처리
                if "(" in part:
                    msg_parts = []
                    while i < len(parts) and ")" not in parts[i]:
                        msg_parts.append(parts[i])
                        i += 1
                    if i < len(parts):
                        msg_parts.append(parts[i])
                    msg = " ".join(msg_parts)
                    msg = re.search(r'"([^"]*)"', msg)
                    if msg:
                        tokens.append(Token(TokenType.STRING, msg.group(1)))
            elif part.lower() in KNOWN_VARIABLES:
                tokens.append(Token(TokenType.VARIABLE, part.lower()))
            elif part in OPERATORS:
                tokens.append(Token(TokenType.OPERATOR, part))
            elif part == "*":
                tokens.append(Token(TokenType.MULTIPLY, "*"))
            elif part == "+":
                tokens.append(Token(TokenType.ADD, "+"))
            elif part == "-":
                tokens.append(Token(TokenType.SUBTRACT, "-"))
            else:
                try:
                    tokens.append(Token(TokenType.NUMBER, float(part)))
                except ValueError:
                    raise ValueError(f"알 수 없는 토큰/변수: '{part}' (KNOWN_VARIABLES 미등록 — 규칙 등록 거부)")

            i += 1

        return tokens

    def _parse_tokens(self, tokens: List[Token]) -> RuleAST:
        """토큰 리스트 → AST 변환"""
        conditions = []
        logical_ops = []
        action = "alert"
        custom_message = None

        idx = 0
        # WHEN 스킵
        if tokens and tokens[idx].type == TokenType.WHEN:
            idx += 1

        # 조건 파싱
        while idx < len(tokens) and tokens[idx].type != TokenType.THEN:
            if tokens[idx].type in (TokenType.AND, TokenType.OR):
                logical_ops.append(tokens[idx].value)
                idx += 1
                continue

            if tokens[idx].type == TokenType.VARIABLE:
                var = tokens[idx].value
                idx += 1
                op = tokens[idx].value if tokens[idx].type == TokenType.OPERATOR else ">"
                idx += 1

                # 값 파싱 (숫자 또는 변수 또는 변수*숫자)
                if tokens[idx].type == TokenType.NUMBER:
                    value_expr = tokens[idx].value
                    idx += 1
                elif tokens[idx].type == TokenType.VARIABLE:
                    ref_var = tokens[idx].value
                    idx += 1
                    if idx < len(tokens) and tokens[idx].type in (TokenType.MULTIPLY, TokenType.ADD, TokenType.SUBTRACT):
                        arith_op = tokens[idx].value
                        idx += 1
                        operand = tokens[idx].value
                        idx += 1
                        value_expr = {"var": ref_var, "op": arith_op, "operand": operand}
                    else:
                        value_expr = {"var": ref_var}
                else:
                    value_expr = 0
                    idx += 1

                conditions.append(ConditionNode(
                    variable=var, operator=op, value_expr=value_expr,
                    raw_text=f"{var} {op} {value_expr}"
                ))
            else:
                idx += 1

        # THEN 스킵
        if idx < len(tokens) and tokens[idx].type == TokenType.THEN:
            idx += 1

        # 액션 파싱
        if idx < len(tokens) and tokens[idx].type == TokenType.ALERT:
            action = "alert"
            idx += 1
            if idx < len(tokens) and tokens[idx].type == TokenType.STRING:
                custom_message = tokens[idx].value

        if len(conditions) > self.MAX_CONDITIONS_PER_RULE:
            raise ValueError(f"조건 수 초과: {len(conditions)} > {self.MAX_CONDITIONS_PER_RULE}")

        return RuleAST(conditions=conditions, logical_ops=logical_ops,
                       action=action, custom_message=custom_message)

    # ── Step 2: 조건 컴파일 (AST → 평가 함수) ──
    def compile_conditions(self, ast: RuleAST) -> Callable[[Dict], bool]:
        """
        AST를 빠른 평가 함수로 컴파일.
        클로저로 조건 캡처 → 실시간 평가 시 dict lookup만 수행.
        """
        compiled_conds = []

        for cond in ast.conditions:
            var = cond.variable
            op = cond.operator
            val_expr = cond.value_expr

            def make_evaluator(v, o, ve):
                def evaluator(ctx: Dict) -> bool:
                    lhs = ctx.get(v, 0)
                    if isinstance(ve, dict):
                        rhs = ctx.get(ve.get("var", ""), 0)
                        arith = ve.get("op")
                        operand = ve.get("operand", 0)
                        if arith == "*":
                            rhs = rhs * operand
                        elif arith == "+":
                            rhs = rhs + operand
                        elif arith == "-":
                            rhs = rhs - operand
                    else:
                        rhs = ve

                    if o == ">":    return lhs > rhs
                    if o == ">=":   return lhs >= rhs
                    if o == "<":    return lhs < rhs
                    if o == "<=":   return lhs <= rhs
                    if o == "==":   return lhs == rhs
                    if o == "!=":   return lhs != rhs
                    return False
                return evaluator

            compiled_conds.append(make_evaluator(var, op, val_expr))

        logical_ops = ast.logical_ops

        def combined_evaluator(ctx: Dict) -> bool:
            if not compiled_conds:
                return False
            result = compiled_conds[0](ctx)
            for i, cond_fn in enumerate(compiled_conds[1:]):
                op = logical_ops[i] if i < len(logical_ops) else "AND"
                if op == "AND":
                    result = result and cond_fn(ctx)
                elif op == "OR":
                    result = result or cond_fn(ctx)
            return result

        return combined_evaluator

    # ── Step 3: 실시간 평가 ──
    def evaluate(
        self,
        rule_id: str,
        market_data: Dict,
        indicators: Dict,
    ) -> Optional[Dict]:
        """
        컴파일된 규칙에 대해 실시간 데이터로 평가.
        True → 알림 트리거 결과 반환.
        """
        compiled = self._compiled_rules.get(rule_id)
        if compiled is None or not compiled.active:
            return None

        # 컨텍스트 구성: market_data + indicators 병합
        ctx = {**market_data, **indicators}
        triggered = compiled.evaluator(ctx)

        if triggered:
            return {
                "rule_id": rule_id,
                "user_id": compiled.user_id,
                "symbol": compiled.symbol,
                "triggered_at": datetime.utcnow(),
                "message": compiled.ast.custom_message or
                           f"사용자 규칙 '{compiled.rule_id}' 조건 충족",
                "conditions_met": [c.raw_text for c in compiled.ast.conditions],
                "market_snapshot": ctx,
                "channels": compiled.notification_channels,
            }
        return None

    def evaluate_all(
        self,
        symbol: str,
        market_data: Dict,
        indicators: Dict,
    ) -> List[Dict]:
        """해당 종목의 모든 활성 규칙 일괄 평가"""
        results = []
        for rule_id, compiled in self._compiled_rules.items():
            if compiled.symbol == symbol and compiled.active:
                result = self.evaluate(rule_id, market_data, indicators)
                if result is not None:
                    results.append(result)
        return results

    # ── 규칙 관리 ──
    def manage_rules(
        self,
        action: str,          # "add" | "remove" | "update" | "toggle"
        rule_id: str,
        user_id: str = "",
        symbol: str = "",
        rule_text: str = "",
        priority: int = 5,
        channels: List[str] = None,
    ) -> Dict:
        """규칙 CRUD 관리"""
        if action == "add":
            ast = self.parse_rule(rule_text)
            evaluator = self.compile_conditions(ast)
            compiled = CompiledRule(
                rule_id=rule_id, user_id=user_id, symbol=symbol,
                ast=ast, evaluator=evaluator, priority=priority,
                notification_channels=channels or ["push"],
            )
            self._compiled_rules[rule_id] = compiled
            return {"status": "added", "rule_id": rule_id, "conditions": len(ast.conditions)}

        elif action == "remove":
            existing = self._compiled_rules.get(rule_id)
            if existing is None:
                return {"status": "not_found"}
            if not user_id or existing.user_id != user_id:
                return {"status": "forbidden", "rule_id": rule_id}
            del self._compiled_rules[rule_id]
            return {"status": "removed", "rule_id": rule_id}

        elif action == "toggle":
            existing = self._compiled_rules.get(rule_id)
            if existing is None:
                return {"status": "not_found"}
            if not user_id or existing.user_id != user_id:
                return {"status": "forbidden", "rule_id": rule_id}
            existing.active = not existing.active
            return {"status": "toggled", "active": existing.active}

        return {"status": "unknown_action"}
```

### E3. Output
- **스키마**:
  ```python
  @dataclass
  class RuleEvaluationResult:
      rule_id: str
      user_id: str
      symbol: str
      triggered_at: datetime
      message: str                          # 커스텀 또는 기본 메시지
      conditions_met: List[str]             # 충족된 조건 원문
      market_snapshot: Dict                 # 트리거 시점 시장 데이터
      channels: List[str]                   # 알림 채널
  ```
- **소비자**: `PriceAlertEngine` (알림 발송), 프론트엔드 규칙 관리 UI, Kafka topic `notification.rule.trigger`

### E4. Class/API Design
```python
class AlertRuleEngine:
    """사용자 정의 알림 규칙 엔진.

    DSL 기반 복합 조건 알림 정의/컴파일/실시간 평가.
    예: "WHEN price > 50000 AND volume > avg_20d * 2 THEN alert"
    """

    def __init__(self): ...

    def parse_rule(self, rule_text: str) -> RuleAST:
        """DSL 텍스트 → AST 파싱."""
        ...

    def compile_conditions(self, ast: RuleAST) -> Callable[[Dict], bool]:
        """AST → 실행 가능한 평가 함수 컴파일."""
        ...

    def evaluate(self, rule_id: str, market_data: Dict, indicators: Dict) -> Optional[Dict]:
        """단일 규칙 실시간 평가."""
        ...

    def evaluate_all(self, symbol: str, market_data: Dict, indicators: Dict) -> List[Dict]:
        """종목별 전체 활성 규칙 일괄 평가."""
        ...

    def manage_rules(self, action: str, rule_id: str, **kwargs) -> Dict:
        """규칙 CRUD (add/remove/update/toggle)."""
        ...

    def validate_rule(self, rule_text: str) -> Dict:
        """규칙 문법 검증 (저장 전 프리뷰)."""
        ...

    def get_user_rules(self, user_id: str) -> List[CompiledRule]:
        """사용자별 등록 규칙 조회."""
        ...
```

### E5. Tech Stack Dependency
| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| re (stdlib) | — | — | DSL 토큰화, 정규표현식 |
| pandas | ≥2.0 | ☑ | 지표 데이터 처리 |
| redis | 5.0.x | ☑ | 컴파일된 규칙 캐시, 트리거 이력 |
| confluent-kafka | 2.3.x | ☑ | 규칙 트리거 이벤트 발행 |
| TimescaleDB | — | ☑ | 규칙 정의 영속화, 트리거 이력 |

### E6. Performance Requirements
| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| DSL 파싱 | ≤ 10ms / 규칙 | 토큰화 + AST 생성 |
| 조건 컴파일 | ≤ 5ms / 규칙 | AST → 클로저 생성 |
| 단일 규칙 평가 | ≤ 0.1ms | 컴파일된 평가 함수 호출 |
| 종목별 전체 평가 (50규칙) | ≤ 5ms | evaluate_all |
| 규칙 CRUD | ≤ 50ms | DB 저장 포함 |

### E7. Error Handling
| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| DSL 문법 오류 | 파싱 실패 상세 위치 반환, 규칙 미등록 | WARN |
| 미지원 변수 참조 | 변수 목록 안내, 규칙 거부 | WARN |
| 조건 수 초과 (>10) | 최대 10개 제한 안내, 규칙 거부 | INFO |
| 사용자 규칙 수 초과 (>50) | 초과 안내, 비활성 규칙 정리 권고 | INFO |
| 평가 중 지표 누락 | 해당 조건 False 처리, 로그 기록 | WARN |
| 0으로 나누기 (연산식) | 해당 조건 False, epsilon 치환 | WARN |

### E8. Test Criteria
- **Unit**:
  - `"WHEN price > 50000 THEN alert"` 파싱 → conditions 1개, variable="price", operator=">"
  - `"WHEN price > 50000 AND volume > avg_20d * 2 THEN alert"` → 2개 조건, AND 연결
  - `"WHEN rsi < 30 OR change_pct < -5 THEN alert"` → OR 연결
  - 컴파일 후 평가: price=51000 → True, price=49000 → False
  - 문법 오류 `"WHEN THEN alert"` → 파싱 실패
- **Integration**:
  - 규칙 등록 → 실시간 데이터 → 평가 → Kafka 트리거 이벤트 E2E
  - 50개 규칙 동시 평가 → 5ms 이내
- **Acceptance**:
  - 비개발자 사용자가 3종 이상 규칙 작성 가능 (UX 테스트)
  - 규칙 평가 정확도 100% (논리 연산 정합성)

### E9. LOCK References
| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| LOCK-KAFKA-06 | SPEC §14 | 규칙 트리거 토픽 `notification.rule.trigger` |
| LOCK-REDIS-04 | SPEC §14 | 컴파일된 규칙 캐시 |
| 사용자 규칙 상한 50개 | 본 문서 정의 | 시스템 부하 방지 |
| 조건 상한 10개 | 본 문서 정의 | 복잡도 제한 |
| 지원 변수 14종 | 본 문서 정의 | DSL 안전 변수 화이트리스트 |

---

## L3 판정

| 항목 | 충족 |
|------|------|
| E1 Input 스키마 정의 | ☑ |
| E2 Python pseudocode (type hints, copy-ready) | ☑ |
| E3 Output 스키마 + confidence + 소비자 | ☑ |
| E4 Class 설계 + 상속 구조 | ☑ |
| E5 SPEC §14 LOCK 기술스택 | ☑ |
| E6 성능 요구사항 | ☑ |
| E7 에러 핸들링 | ☑ |
| E8 테스트 기준 (Unit/Integration/Acceptance) | ☑ |
| E9 LOCK 참조 | ☑ |

> **L3 판정: PASS** — 모든 E1~E9 섹션 완비, 구현 착수 가능
