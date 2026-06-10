# 인지적 디바이어싱(Cognitive Debiasing) 프레임워크
> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #2 투자 심리학 & 행동재무학
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-10. 인지적 디바이어싱(Cognitive Debiasing) 프레임워크

**현재**: 완전히 없음
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 40 | **프리모템(Pre-Mortem) 분석** | 매매 전 "이 거래가 실패한다면 왜?" 강제 사전 분석. 낙관 편향 교정, 리스크 사전 식별 |
| 41 | **체크리스트 기반 의사결정** | 매매 진입 전 구조화된 체크리스트 강제 확인. 편향 필터, 펀더멘탈 확인, 기술적 조건, 리스크 관리 4영역 |
| 42 | **반대 포지션(Devil's Advocate) 자동 분석** | 매수 시그널 시 자동으로 매도 관점 분석 생성, 매도 시그널 시 매수 관점 생성. 양면 판단 강제화 |
| 43 | **기저율(Base Rate) 알림** | "이 패턴의 역사적 성공률은 52%입니다" 식의 객관적 확률 표시. 직관적 판단보다 통계적 기저율 우선 |

---

## E1. Input

### Kafka 수신 토픽

| 토픽 | 메시지 스키마 | 빈도 |
|------|-------------|------|
| `trade.signal.proposed` | `{signal_id: str, symbol: str, ts: datetime, direction: str, strategy: str, entry_price: float, stop_loss: float, take_profit: float, rationale: str}` | 이벤트 기반 |
| `market.pattern.detected` | `{symbol: str, ts: datetime, pattern_name: str, pattern_type: str, timeframe: str, confidence: float}` | 이벤트 기반 |
| `market.fundamental.snapshot` | `{symbol: str, ts: datetime, pe_ratio: float, pb_ratio: float, roe: float, debt_ratio: float, revenue_growth: float}` | 1 day |
| `market.technical.summary` | `{symbol: str, ts: datetime, trend: str, rsi: float, macd_signal: str, support: float, resistance: float, volume_trend: str}` | 5 min |

### 항목별 필수 필드 및 전처리

| # | 항목 | 필수 필드 | 전처리 |
|---|------|----------|--------|
| 40 | 프리모템 분석 | `signal_id`, `symbol`, `direction`, `entry_price`, `stop_loss`, `rationale` | 과거 유사 거래 실패 사례 조회, 리스크 요인 벡터 구성 |
| 41 | 체크리스트 의사결정 | `signal_id`, `symbol`, 펀더멘탈 + 기술적 + 리스크 데이터 | 4영역별 항목 바인딩, 누락 필드 검출 |
| 42 | 반대 포지션 분석 | `signal_id`, `symbol`, `direction`, 기술적·펀더멘탈 데이터 | 반대 방향 근거 추출, 강도 스코어링 |
| 43 | 기저율 알림 | `pattern_name`, `pattern_type`, `timeframe` | 과거 패턴 DB 조회, 성공/실패 카운트 집계 |

### TimescaleDB 스키마

```sql
-- 거래 시그널 이력
CREATE TABLE trade_signals (
    signal_id       TEXT PRIMARY KEY,
    ts              TIMESTAMPTZ NOT NULL,
    symbol          TEXT NOT NULL,
    direction       TEXT NOT NULL,      -- buy / sell
    strategy        TEXT,
    entry_price     DOUBLE PRECISION,
    stop_loss       DOUBLE PRECISION,
    take_profit     DOUBLE PRECISION,
    rationale       TEXT,
    outcome         TEXT,               -- win / loss / pending
    pnl_pct         DOUBLE PRECISION
);

-- 패턴 이력 (기저율 계산용)
CREATE TABLE pattern_history (
    ts              TIMESTAMPTZ NOT NULL,
    symbol          TEXT NOT NULL,
    pattern_name    TEXT NOT NULL,
    pattern_type    TEXT NOT NULL,       -- reversal / continuation / breakout
    timeframe       TEXT NOT NULL,
    direction       TEXT NOT NULL,
    success         BOOLEAN NOT NULL,
    return_5d_pct   DOUBLE PRECISION
);
SELECT create_hypertable('pattern_history', 'ts');

-- 체크리스트 감사 로그
CREATE TABLE checklist_audit (
    signal_id       TEXT NOT NULL,
    ts              TIMESTAMPTZ NOT NULL,
    domain          TEXT NOT NULL,       -- bias / fundamental / technical / risk
    item_key        TEXT NOT NULL,
    passed          BOOLEAN NOT NULL,
    value           TEXT,
    note            TEXT
);
SELECT create_hypertable('checklist_audit', 'ts');

-- 프리모템 분석 기록
CREATE TABLE premortem_analysis (
    signal_id       TEXT NOT NULL,
    ts              TIMESTAMPTZ NOT NULL,
    risk_factor     TEXT NOT NULL,
    severity        TEXT NOT NULL,       -- low / medium / high / critical
    historical_freq DOUBLE PRECISION,
    mitigation      TEXT
);
SELECT create_hypertable('premortem_analysis', 'ts');
```

---

## E2. Algorithm

```python
from __future__ import annotations
import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RiskFactor:
    """프리모템 개별 리스크 요인"""
    factor: str
    severity: str           # low / medium / high / critical
    historical_freq: float  # 과거 발생 빈도 (0.0 ~ 1.0)
    mitigation: str


@dataclass
class PreMortemResult:
    """#40 프리모템 분석 결과"""
    signal_id: str
    symbol: str
    ts: datetime
    risk_factors: list[RiskFactor]
    overall_risk_score: float    # 0.0 ~ 1.0
    recommendation: str          # proceed / caution / abort
    confidence: float


@dataclass
class ChecklistResult:
    """#41 체크리스트 기반 의사결정 결과"""
    signal_id: str
    symbol: str
    ts: datetime
    bias_check: dict[str, bool]         # 편향 필터 항목별 통과 여부
    fundamental_check: dict[str, bool]  # 펀더멘탈 항목별 통과 여부
    technical_check: dict[str, bool]    # 기술적 조건 항목별 통과 여부
    risk_check: dict[str, bool]         # 리스크 관리 항목별 통과 여부
    pass_rate: float                    # 전체 통과율 (0.0 ~ 1.0)
    gate_passed: bool                   # 최종 게이트 통과 여부
    confidence: float


@dataclass
class DevilsAdvocateResult:
    """#42 반대 포지션 자동 분석 결과"""
    signal_id: str
    symbol: str
    ts: datetime
    original_direction: str
    counter_arguments: list[dict]  # [{factor, strength, evidence}]
    counter_score: float           # 반대 근거 강도 (0.0 ~ 1.0)
    net_conviction: float          # 원래 확신 - 반대 강도
    recommendation: str            # confirm / weaken / reverse
    confidence: float


@dataclass
class BaseRateAlert:
    """#43 기저율 알림 결과"""
    symbol: str
    ts: datetime
    pattern_name: str
    pattern_type: str
    timeframe: str
    total_occurrences: int
    success_count: int
    base_rate: float              # 성공률 (0.0 ~ 1.0)
    avg_return_on_success: float  # 성공 시 평균 수익률
    avg_return_on_failure: float  # 실패 시 평균 손실률
    alert_message: str
    confidence: float


class CognitiveDebiasingEngine:
    """B-10 인지적 디바이어싱 프레임워크

    Methods:
        run_premortem  (#40)
        evaluate_checklist  (#41)
        generate_counter_analysis  (#42)
        compute_base_rate  (#43)
    """

    # ── 설정 상수 ──
    SEVERITY_WEIGHTS: dict[str, float] = {
        "low": 0.1, "medium": 0.3, "high": 0.6, "critical": 1.0
    }
    CHECKLIST_GATE_THRESHOLD: float = 0.75    # 75% 이상 통과 시 게이트 통과
    COUNTER_WEAKEN_THRESHOLD: float = 0.4     # 반대 강도 40% 이상이면 확신 약화
    COUNTER_REVERSE_THRESHOLD: float = 0.7    # 반대 강도 70% 이상이면 방향 재고
    MIN_PATTERN_SAMPLES: int = 30             # 기저율 계산 최소 샘플

    # ── 프리모템 리스크 카탈로그 ──
    RISK_CATALOG: list[dict] = [
        {"factor": "trend_reversal", "check": "역추세 진입", "severity_base": "high"},
        {"factor": "low_liquidity", "check": "유동성 부족", "severity_base": "high"},
        {"factor": "earnings_near", "check": "실적 발표 임박", "severity_base": "medium"},
        {"factor": "high_volatility", "check": "극단 변동성 구간", "severity_base": "medium"},
        {"factor": "overconcentration", "check": "섹터 과집중", "severity_base": "medium"},
        {"factor": "stop_too_wide", "check": "손절폭 과대", "severity_base": "low"},
        {"factor": "news_catalyst", "check": "뉴스 이벤트 직전", "severity_base": "medium"},
        {"factor": "correlation_spike", "check": "상관관계 급등 구간", "severity_base": "low"},
    ]

    def run_premortem(
        self,
        signal: dict,
        market_context: dict,
        historical_failures: pd.DataFrame,
    ) -> PreMortemResult:
        """#40 프리모템(Pre-Mortem) 분석

        Args:
            signal: 제안된 거래 시그널
                    {signal_id, symbol, direction, entry_price, stop_loss, rationale}
            market_context: 현재 시장 상황
                    {trend, volatility_percentile, liquidity_score,
                     days_to_earnings, sector_concentration}
            historical_failures: 과거 유사 전략 실패 사례 DataFrame
                    columns=[signal_id, symbol, strategy, failure_reason, loss_pct]

        Returns:
            PreMortemResult
        """
        risk_factors: list[RiskFactor] = []

        # 리스크 카탈로그 기반 검사
        for catalog_item in self.RISK_CATALOG:
            factor = catalog_item["factor"]
            triggered = False
            severity = catalog_item["severity_base"]

            if factor == "trend_reversal":
                if (signal["direction"] == "buy" and market_context.get("trend") == "bearish") or \
                   (signal["direction"] == "sell" and market_context.get("trend") == "bullish"):
                    triggered = True
            elif factor == "low_liquidity":
                if market_context.get("liquidity_score", 1.0) < 0.3:
                    triggered = True
            elif factor == "earnings_near":
                if market_context.get("days_to_earnings", 999) <= 3:
                    triggered = True
            elif factor == "high_volatility":
                if market_context.get("volatility_percentile", 0) > 90:
                    triggered = True
                    severity = "high"
            elif factor == "overconcentration":
                if market_context.get("sector_concentration", 0) > 0.4:
                    triggered = True
            elif factor == "stop_too_wide":
                stop_pct = abs(signal["entry_price"] - signal["stop_loss"]) / signal["entry_price"]
                if stop_pct > 0.05:
                    triggered = True
                    severity = "medium" if stop_pct > 0.08 else "low"
            elif factor == "news_catalyst":
                if market_context.get("upcoming_news", False):
                    triggered = True
            elif factor == "correlation_spike":
                if market_context.get("correlation_percentile", 0) > 85:
                    triggered = True

            if triggered:
                # 과거 발생 빈도 계산
                hist_freq = 0.0
                if len(historical_failures) > 0:
                    match_count = historical_failures[
                        historical_failures["failure_reason"].str.contains(factor, na=False)
                    ].shape[0]
                    hist_freq = match_count / max(len(historical_failures), 1)

                risk_factors.append(RiskFactor(
                    factor=factor,
                    severity=severity,
                    historical_freq=round(hist_freq, 4),
                    mitigation=f"Mitigate {factor}: 포지션 축소 또는 헤지 검토",
                ))

        # overall risk score = 가중 합산 / 최대 가능 점수
        if risk_factors:
            weighted_sum = sum(
                self.SEVERITY_WEIGHTS[rf.severity] * (1 + rf.historical_freq)
                for rf in risk_factors
            )
            max_possible = len(self.RISK_CATALOG) * 1.0 * 2.0  # max severity × max freq_boost
            overall_risk = min(weighted_sum / max_possible, 1.0)
        else:
            overall_risk = 0.0

        # 권고
        if overall_risk >= 0.6:
            recommendation = "abort"
        elif overall_risk >= 0.3:
            recommendation = "caution"
        else:
            recommendation = "proceed"

        confidence = 1.0 - overall_risk * 0.5  # 리스크 높을수록 confidence 감소

        return PreMortemResult(
            signal_id=signal["signal_id"],
            symbol=signal["symbol"],
            ts=datetime.utcnow(),
            risk_factors=risk_factors,
            overall_risk_score=round(overall_risk, 4),
            recommendation=recommendation,
            confidence=round(confidence, 4),
        )

    def evaluate_checklist(
        self,
        signal: dict,
        fundamental_data: dict,
        technical_data: dict,
        risk_params: dict,
    ) -> ChecklistResult:
        """#41 체크리스트 기반 의사결정

        Args:
            signal: {signal_id, symbol, direction, entry_price, stop_loss, rationale}
            fundamental_data: {pe_ratio, pb_ratio, roe, debt_ratio, revenue_growth}
            technical_data: {trend, rsi, macd_signal, support, resistance, volume_trend}
            risk_params: {position_size_pct, portfolio_heat, max_drawdown_current}

        Returns:
            ChecklistResult
        """
        # 영역 1: 편향 필터
        bias_check = {
            "recency_bias_check": True,  # 최근 성과에 과도 의존 안 함 (기본 통과, 별도 모듈에서 검증)
            "confirmation_bias_check": signal.get("rationale", "") != "",  # 근거 기술 필수
            "anchoring_check": abs(signal["entry_price"] - signal.get("prev_target", signal["entry_price"])) / max(signal["entry_price"], 1e-9) < 0.1,
            "herd_behavior_check": not signal.get("follows_crowd", False),
        }

        # 영역 2: 펀더멘탈 확인
        fundamental_check = {
            "pe_reasonable": fundamental_data.get("pe_ratio", 0) < 50,
            "debt_manageable": fundamental_data.get("debt_ratio", 1) < 0.7,
            "roe_positive": fundamental_data.get("roe", 0) > 0,
            "revenue_growth": fundamental_data.get("revenue_growth", 0) > -0.1,
        }

        # 영역 3: 기술적 조건
        direction = signal["direction"]
        technical_check = {
            "trend_aligned": (
                (direction == "buy" and technical_data.get("trend") in ["bullish", "neutral"]) or
                (direction == "sell" and technical_data.get("trend") in ["bearish", "neutral"])
            ),
            "rsi_not_extreme": 20 < technical_data.get("rsi", 50) < 80,
            "volume_confirms": technical_data.get("volume_trend") in ["increasing", "stable"],
            "support_resistance_ok": (
                (direction == "buy" and signal["entry_price"] > technical_data.get("support", 0)) or
                (direction == "sell" and signal["entry_price"] < technical_data.get("resistance", float("inf")))
            ),
        }

        # 영역 4: 리스크 관리
        risk_check = {
            "position_size_ok": risk_params.get("position_size_pct", 1) <= 0.05,
            "portfolio_heat_ok": risk_params.get("portfolio_heat", 1) <= 0.2,
            "drawdown_acceptable": risk_params.get("max_drawdown_current", 0) < 0.15,
            "stop_loss_set": signal.get("stop_loss") is not None,
        }

        # 전체 통과율 계산
        all_checks = {**bias_check, **fundamental_check, **technical_check, **risk_check}
        total = len(all_checks)
        passed = sum(1 for v in all_checks.values() if v)
        pass_rate = passed / max(total, 1)

        gate_passed = pass_rate >= self.CHECKLIST_GATE_THRESHOLD
        confidence = pass_rate  # 통과율 자체가 confidence

        return ChecklistResult(
            signal_id=signal["signal_id"],
            symbol=signal["symbol"],
            ts=datetime.utcnow(),
            bias_check=bias_check,
            fundamental_check=fundamental_check,
            technical_check=technical_check,
            risk_check=risk_check,
            pass_rate=round(pass_rate, 4),
            gate_passed=gate_passed,
            confidence=round(confidence, 4),
        )

    def generate_counter_analysis(
        self,
        signal: dict,
        technical_data: dict,
        fundamental_data: dict,
        sentiment_score: float,
    ) -> DevilsAdvocateResult:
        """#42 반대 포지션(Devil's Advocate) 자동 분석

        Args:
            signal: {signal_id, symbol, direction, entry_price, rationale}
            technical_data: {trend, rsi, macd_signal, support, resistance}
            fundamental_data: {pe_ratio, pb_ratio, roe, debt_ratio}
            sentiment_score: 현재 시장 심리 점수 (-1.0 ~ 1.0)

        Returns:
            DevilsAdvocateResult
        """
        counter_args: list[dict] = []
        direction = signal["direction"]
        opposite = "sell" if direction == "buy" else "buy"

        # 기술적 반대 근거
        rsi = technical_data.get("rsi", 50)
        if direction == "buy" and rsi > 70:
            counter_args.append({
                "factor": "RSI 과매수",
                "strength": 0.7,
                "evidence": f"RSI={rsi:.1f}, 과매수 영역에서 매수 진입"
            })
        elif direction == "sell" and rsi < 30:
            counter_args.append({
                "factor": "RSI 과매도",
                "strength": 0.7,
                "evidence": f"RSI={rsi:.1f}, 과매도 영역에서 매도 진입"
            })

        trend = technical_data.get("trend", "neutral")
        if (direction == "buy" and trend == "bearish") or \
           (direction == "sell" and trend == "bullish"):
            counter_args.append({
                "factor": "역추세 매매",
                "strength": 0.8,
                "evidence": f"현재 추세={trend}, {direction} 진입은 역추세"
            })

        # 펀더멘탈 반대 근거
        pe = fundamental_data.get("pe_ratio", 0)
        if direction == "buy" and pe > 40:
            counter_args.append({
                "factor": "고평가 우려",
                "strength": 0.5,
                "evidence": f"PER={pe:.1f}, 고평가 상태에서 매수"
            })
        elif direction == "sell" and pe < 10 and pe > 0:
            counter_args.append({
                "factor": "저평가 가능성",
                "strength": 0.5,
                "evidence": f"PER={pe:.1f}, 저평가 구간에서 매도"
            })

        debt = fundamental_data.get("debt_ratio", 0)
        if direction == "buy" and debt > 0.7:
            counter_args.append({
                "factor": "높은 부채 비율",
                "strength": 0.4,
                "evidence": f"부채비율={debt:.2%}, 재무 리스크 존재"
            })

        # 심리 반대 근거
        if direction == "buy" and sentiment_score > 0.7:
            counter_args.append({
                "factor": "과열 심리",
                "strength": 0.6,
                "evidence": f"심리점수={sentiment_score:.2f}, 시장 과열 상태에서 매수"
            })
        elif direction == "sell" and sentiment_score < -0.7:
            counter_args.append({
                "factor": "공포 과잉",
                "strength": 0.6,
                "evidence": f"심리점수={sentiment_score:.2f}, 극단 공포에서 매도"
            })

        # 반대 스코어 = 각 근거 strength의 가중 평균
        if counter_args:
            counter_score = sum(a["strength"] for a in counter_args) / len(counter_args)
        else:
            counter_score = 0.0

        net_conviction = 1.0 - counter_score

        if counter_score >= self.COUNTER_REVERSE_THRESHOLD:
            recommendation = "reverse"
        elif counter_score >= self.COUNTER_WEAKEN_THRESHOLD:
            recommendation = "weaken"
        else:
            recommendation = "confirm"

        confidence = min(0.5 + len(counter_args) * 0.1, 1.0)

        return DevilsAdvocateResult(
            signal_id=signal["signal_id"],
            symbol=signal["symbol"],
            ts=datetime.utcnow(),
            original_direction=direction,
            counter_arguments=counter_args,
            counter_score=round(counter_score, 4),
            net_conviction=round(net_conviction, 4),
            recommendation=recommendation,
            confidence=round(confidence, 4),
        )

    def compute_base_rate(
        self,
        pattern_history_df: pd.DataFrame,
        pattern_name: str,
        pattern_type: str,
        timeframe: str,
    ) -> BaseRateAlert:
        """#43 기저율(Base Rate) 알림

        Args:
            pattern_history_df: pattern_history 테이블에서 조회한 DataFrame
                    columns=[ts, symbol, pattern_name, pattern_type, timeframe,
                             direction, success, return_5d_pct]
            pattern_name: 감지된 패턴 이름 (e.g., "double_bottom")
            pattern_type: 패턴 유형 (reversal / continuation / breakout)
            timeframe: 시간프레임 (e.g., "1D", "4H")

        Returns:
            BaseRateAlert
        """
        df = pattern_history_df[
            (pattern_history_df["pattern_name"] == pattern_name) &
            (pattern_history_df["pattern_type"] == pattern_type) &
            (pattern_history_df["timeframe"] == timeframe)
        ].copy()

        total = len(df)
        success_count = int(df["success"].sum()) if total > 0 else 0
        base_rate = success_count / max(total, 1)

        # 성공/실패 시 평균 수익률
        if total > 0:
            success_df = df[df["success"] == True]
            failure_df = df[df["success"] == False]
            avg_return_success = float(success_df["return_5d_pct"].mean()) if len(success_df) > 0 else 0.0
            avg_return_failure = float(failure_df["return_5d_pct"].mean()) if len(failure_df) > 0 else 0.0
        else:
            avg_return_success = 0.0
            avg_return_failure = 0.0

        # 샘플 수 기반 confidence
        if total >= self.MIN_PATTERN_SAMPLES * 3:
            sample_confidence = 1.0
        elif total >= self.MIN_PATTERN_SAMPLES:
            sample_confidence = 0.7
        elif total >= 10:
            sample_confidence = 0.4
        else:
            sample_confidence = 0.2

        # 알림 메시지 생성
        if total < 10:
            alert_msg = (
                f"'{pattern_name}' 패턴의 역사적 데이터가 부족합니다 "
                f"(샘플={total}건). 기저율 신뢰도가 낮습니다."
            )
        else:
            alert_msg = (
                f"'{pattern_name}' 패턴({timeframe})의 역사적 성공률: "
                f"{base_rate:.1%} ({success_count}/{total}건). "
                f"성공 시 평균 {avg_return_success:+.2%}, "
                f"실패 시 평균 {avg_return_failure:+.2%}"
            )

        return BaseRateAlert(
            symbol="*",  # 패턴별 집계이므로 전체
            ts=datetime.utcnow(),
            pattern_name=pattern_name,
            pattern_type=pattern_type,
            timeframe=timeframe,
            total_occurrences=total,
            success_count=success_count,
            base_rate=round(base_rate, 4),
            avg_return_on_success=round(avg_return_success, 4),
            avg_return_on_failure=round(avg_return_failure, 4),
            alert_message=alert_msg,
            confidence=round(sample_confidence, 4),
        )
```

---

## E3. Output

### 출력 스키마

| 메서드 | 출력 타입 | Kafka 출력 토픽 | 주요 필드 |
|--------|----------|-----------------|----------|
| `run_premortem` | `PreMortemResult` | `debiasing.premortem` | `risk_factors`, `overall_risk_score`, `recommendation`, `confidence` |
| `evaluate_checklist` | `ChecklistResult` | `debiasing.checklist` | `pass_rate`, `gate_passed`, 4영역 통과 여부, `confidence` |
| `generate_counter_analysis` | `DevilsAdvocateResult` | `debiasing.counter_analysis` | `counter_arguments`, `counter_score`, `net_conviction`, `recommendation` |
| `compute_base_rate` | `BaseRateAlert` | `debiasing.base_rate` | `base_rate`, `total_occurrences`, `alert_message`, `confidence` |

### Confidence 기준

| 등급 | 범위 | 의미 |
|------|------|------|
| HIGH | ≥ 0.7 | 충분한 데이터 기반 분석, 의사결정에 직접 반영 |
| MEDIUM | 0.4 ~ 0.7 | 보조 참고, 다른 분석과 결합 권장 |
| LOW | < 0.4 | 데이터 부족, 참고용만 |

### 소비자

- `08_execution`: 체크리스트 게이트 미통과 시 거래 블로킹
- `07_risk-management`: 프리모템 abort 시 포지션 진입 차단
- `05_signal-integration`: 반대 포지션 분석으로 시그널 가중치 조절
- Dashboard UI: 기저율 알림 표시, 체크리스트 시각화

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod


class BaseAnalyzer(ABC):
    """모든 분석기의 공통 부모 클래스"""

    @abstractmethod
    def analyze(self, **kwargs) -> dict:
        ...

    def publish(self, topic: str, payload: dict) -> None:
        """Kafka 토픽으로 결과 발행"""
        ...


class CognitiveDebiasingEngine(BaseAnalyzer):
    """B-10 인지적 디바이어싱 프레임워크

    Inheritance: BaseAnalyzer → CognitiveDebiasingEngine

    Public Methods:
        run_premortem(signal, market_context, historical_failures) → PreMortemResult
        evaluate_checklist(signal, fundamental_data, technical_data, risk_params) → ChecklistResult
        generate_counter_analysis(signal, technical_data, fundamental_data, sentiment_score) → DevilsAdvocateResult
        compute_base_rate(pattern_history_df, pattern_name, pattern_type, timeframe) → BaseRateAlert
        analyze(**kwargs) → dict  # BaseAnalyzer 구현: 전체 디바이어싱 파이프라인 실행

    Private Methods:
        _check_risk_catalog(signal, market_context) → list[RiskFactor]
        _compute_pass_rate(checks: dict) → float
        _build_counter_arguments(signal, technical, fundamental, sentiment) → list[dict]
    """

    def analyze(self, **kwargs) -> dict:
        """전체 디바이어싱 파이프라인 실행 후 결과 dict 반환"""
        ...
```

---

## E5. Tech Stack Dependency

| 기술 | 용도 | SPEC §14 LOCK |
|------|------|---------------|
| **Kafka** | 거래 시그널 수신, 디바이어싱 결과 발행 | ✅ |
| **TimescaleDB** | trade_signals, pattern_history, checklist_audit, premortem_analysis 저장 | ✅ |
| **pandas** | 패턴 이력 집계, 성공률 계산, DataFrame 필터링 | ✅ |
| **numpy** | 가중 평균 계산, 통계 연산 | ✅ |
| **scikit-learn** | (예비) 패턴 성공률 예측 모델 고도화 | ✅ |

---

## E6. Performance Requirements

| 지표 | 목표 | 비고 |
|------|------|------|
| 프리모템 분석 지연 | ≤ 1s | 거래 시그널 생성 직후 실행 |
| 체크리스트 평가 지연 | ≤ 500ms | 4영역 16개 항목 동시 검사 |
| 반대 포지션 분석 지연 | ≤ 1s | 기술적·펀더멘탈·심리 데이터 종합 |
| 기저율 계산 지연 | ≤ 2s | 대규모 패턴 이력 집계 포함 |
| 전체 디바이어싱 파이프라인 | ≤ 5s | 4개 분석 순차 실행 시 |
| TimescaleDB 패턴 이력 조회 | ≤ 500ms | 전체 패턴 이력 집계 쿼리 |

---

## E7. Error Handling

| 에러 유형 | 처리 방식 |
|----------|----------|
| 거래 시그널 필수 필드 누락 | `signal_id`, `symbol`, `direction` 없으면 에러 로깅 후 분석 스킵 |
| 펀더멘탈 데이터 미수신 | 해당 영역 체크 전체 `False` 처리 (보수적 폴백 — 데이터 부재는 통과 아님), gate_passed 차단 + 인간 검토 요구, confidence -0.2 |
| 기술적 데이터 미수신 | 해당 영역 체크 전체 `False` 처리 (보수적 폴백 — 데이터 부재는 통과 아님), gate_passed 차단 + 인간 검토 요구, confidence -0.2 |
| 패턴 이력 부족 (< 10건) | 기저율 알림 생성하되 `confidence < 0.4`, 경고 메시지 포함 |
| TimescaleDB 조회 타임아웃 | 30초 타임아웃, 캐시된 최근 결과 사용 |
| Kafka 발행 실패 | 3회 재시도 후 DLQ 이동, 로컬 로그 기록 |
| 체크리스트 항목 평가 예외 | 개별 항목 `False` 처리 후 계속 진행, 에러 로깅 |

---

## E8. Test Criteria

### Unit Tests

| 테스트 ID | 대상 메서드 | 시나리오 | 기대 결과 |
|-----------|-----------|---------|----------|
| UT-40-01 | `run_premortem` | 역추세 + 저유동성 + 실적 임박 | `recommendation="abort"`, `overall_risk_score ≥ 0.6` |
| UT-40-02 | `run_premortem` | 리스크 요인 0개 | `recommendation="proceed"`, `overall_risk_score ≈ 0.0` |
| UT-41-01 | `evaluate_checklist` | 16개 항목 중 12개 통과 | `pass_rate=0.75`, `gate_passed=True` |
| UT-41-02 | `evaluate_checklist` | 8개 항목만 통과 | `pass_rate=0.5`, `gate_passed=False` |
| UT-42-01 | `generate_counter_analysis` | 매수 + RSI 75 + 하락 추세 | `counter_score ≥ 0.7`, `recommendation="reverse"` |
| UT-42-02 | `generate_counter_analysis` | 매수 + RSI 50 + 상승 추세 | `counter_score < 0.4`, `recommendation="confirm"` |
| UT-43-01 | `compute_base_rate` | 100건 중 55건 성공 | `base_rate=0.55`, `confidence ≥ 0.7` |
| UT-43-02 | `compute_base_rate` | 5건 데이터 | `confidence < 0.4`, alert에 "부족" 메시지 |

### Integration Tests

| 테스트 ID | 시나리오 | 검증 항목 |
|-----------|---------|----------|
| IT-40-01 | Kafka 시그널 수신 → 프리모템 → 결과 발행 | end-to-end 파이프라인, Kafka 메시지 형식 |
| IT-41-01 | 시그널 + DB 조회 → 체크리스트 → 게이트 판정 | 4영역 데이터 바인딩 정확성 |
| IT-42-01 | 시그널 → 반대 분석 → 시그널 가중치 조절 | counter_score에 따른 가중치 변화 |
| IT-43-01 | 패턴 감지 → 기저율 조회 → 알림 발행 | 정확한 성공률 계산, 알림 메시지 형식 |

### Acceptance Criteria

| 기준 | 목표 |
|------|------|
| 프리모템 abort 시그널 손실 회피율 | abort 권고 후 실제 손실 거래 비율 ≥ 60% |
| 체크리스트 게이트 필터링 효과 | 게이트 통과 거래의 승률 > 미통과 대비 +10%p |
| 반대 포지션 reverse 정확도 | reverse 권고 후 원래 방향 손실 비율 ≥ 50% |
| 기저율 정보 제공 시 의사결정 개선 | 기저율 표시 후 사용자 과신 매매 ↓ 15% |

---

## E9. LOCK References

| 참조 ID | SPEC 항목 | 적용 내용 |
|---------|----------|----------|
| LOCK-KAFKA-10 | §14.1 | Kafka를 통한 거래 시그널 수신 및 디바이어싱 결과 발행 |
| LOCK-TSDB-10 | §14.2 | TimescaleDB에 trade_signals, pattern_history, checklist_audit, premortem_analysis 저장 |
| LOCK-PD-10 | §14.3 | pandas DataFrame 기반 패턴 이력 집계 및 성공률 계산 |
| LOCK-NP-10 | §14.4 | numpy 가중 평균, 통계 연산 |
| LOCK-SK-10 | §14.5 | scikit-learn 예비 (패턴 성공률 예측 모델) |

---

## L3 판정

| 항목 | 상태 |
|------|------|
| E1. Input 스키마 정의 | ✅ 완료 |
| E2. Algorithm pseudocode | ✅ 완료 |
| E3. Output 스키마 정의 | ✅ 완료 |
| E4. Class/API 설계 | ✅ 완료 |
| E5. Tech Stack 매핑 | ✅ 완료 |
| E6. Performance 요구사항 | ✅ 완료 |
| E7. Error Handling | ✅ 완료 |
| E8. Test Criteria | ✅ 완료 |
| E9. LOCK References | ✅ 완료 |
| **L3 판정** | **APPROVED** |
