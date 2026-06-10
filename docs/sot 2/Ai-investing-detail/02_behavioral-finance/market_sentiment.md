# 시장 심리 지표 엔진 (Market Sentiment Engine)
> **버전**: v2.0
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #2 투자 심리학 & 행동재무학
> **정본 소유 개념**: —
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1☑ E2☑ E3☑ E4☑ E5☑ E6☑ E7☑ E8☑ E9☑

---

### B-1. 시장 심리 지표 엔진 (Market Sentiment Engine)

**현재**: Fear & Greed Index가 데이터 소스 목록에만 존재
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 1 | **Fear & Greed Index 통합 엔진** | CNN Fear & Greed, Alternative.me Crypto Fear & Greed를 실시간 수집 → 0~100 정규화 스코어 → 전략 가중치 조절 연동. Extreme Fear(<20) 시 역발상 매수 시그널, Extreme Greed(>80) 시 포지션 축소 시그널 |
| 2 | **풋/콜 비율(Put/Call Ratio) 모니터** | CBOE 풋/콜 비율 실시간 추적. 비율 >1.2 = 과도한 공포(역발상 매수 기회), <0.5 = 과도한 낙관(경계 시그널) |
| 3 | **VIX 텀 스트럭처 분석** | VIX 현물 vs VIX 선물 기간 구조. 백워데이션(현물>선물) = 단기 공포 극단, 콘탱고(선물>현물) = 안도감. 전략 공격성 조절에 직결 |
| 4 | **AAII 투자자 심리 조사 연동** | 주간 개인 투자자 Bull/Bear/Neutral 비율. 극단적 약세(Bull<20%) → 역사적 반등 확률 높음 → 전략 반영 |
| 5 | **소셜 미디어 심리 지표** | Reddit(r/wallstreetbets), Twitter/X 투자 관련 키워드 빈도 & 감성. 급증 = 군중 형성 시그널. 크립토: Telegram/Discord 채널 모니터링 |

---

## E1. Input

### 데이터 스키마

```yaml
FearGreedInput:
  source: enum[CNN, ALTERNATIVE_ME]
  raw_score: float          # 원본 스코어 (0~100)
  timestamp: datetime       # UTC 기준 수집 시각
  components:               # CNN 하위 지표 (7개)
    - name: str
      value: float
      weight: float

PutCallInput:
  source: literal["CBOE"]
  total_put_volume: int
  total_call_volume: int
  equity_put_call_ratio: float
  index_put_call_ratio: float
  timestamp: datetime

VIXTermInput:
  vix_spot: float           # VIX 현물
  vix_futures:              # VIX 선물 (월별)
    - month: int            # 1~8개월
      price: float
      expiry: date
  timestamp: datetime

AAIISentimentInput:
  survey_date: date         # 매주 목요일 발표
  bullish_pct: float        # 0~100
  bearish_pct: float        # 0~100
  neutral_pct: float        # 0~100

SocialSentimentInput:
  platform: enum[REDDIT, TWITTER, TELEGRAM, DISCORD]
  keyword: str
  mention_count: int        # 집계 구간 내 언급 수
  sentiment_score: float    # -1.0 ~ +1.0
  interval_minutes: int     # 집계 구간 (기본 60분)
  timestamp: datetime
```

### 필수 필드
- 모든 Input: `timestamp` (UTC), `source`
- FearGreedInput: `raw_score`
- PutCallInput: `equity_put_call_ratio`
- VIXTermInput: `vix_spot`, 최소 2개월 선물 데이터
- AAIISentimentInput: `bullish_pct`, `bearish_pct`
- SocialSentimentInput: `mention_count`, `sentiment_score`

### 전처리
1. 결측값: 직전 유효값 forward-fill, 3회 연속 결측 시 해당 지표 비활성
2. 이상치: Fear & Greed raw_score가 [0, 100] 범위 벗어나면 클리핑
3. 타임존: 모든 입력을 UTC로 통일 후 처리
4. 소셜 데이터: 봇/스팸 필터 적용 후 sentiment_score 재계산

---

## E2. Algorithm

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class SentimentZone(Enum):
    EXTREME_FEAR = "extreme_fear"      # 0~20
    FEAR = "fear"                       # 20~40
    NEUTRAL = "neutral"                 # 40~60
    GREED = "greed"                     # 60~80
    EXTREME_GREED = "extreme_greed"     # 80~100

class VIXStructure(Enum):
    BACKWARDATION = "backwardation"     # 현물 > 선물 (공포)
    CONTANGO = "contango"              # 선물 > 현물 (안도)
    FLAT = "flat"                       # 차이 < 임계값

@dataclass
class SentimentResult:
    composite_score: float              # 0~100
    zone: SentimentZone
    fear_greed_normalized: float
    put_call_signal: str                # "fear" | "neutral" | "greed"
    vix_structure: VIXStructure
    aaii_contrarian_flag: bool
    social_surge_detected: bool
    confidence: float                   # 0~1
    timestamp: str                      # ISO-8601

class MarketSentimentEngine:
    """시장 심리 지표 통합 엔진 - 5개 하위 모듈 통합."""

    WEIGHTS: dict[str, float] = {
        "fear_greed": 0.30,
        "put_call": 0.20,
        "vix_term": 0.20,
        "aaii": 0.15,
        "social": 0.15,
    }

    # ── 항목 1: Fear & Greed Index 통합 ──
    def compute_fear_greed(
        self, raw_scores: list[dict]
    ) -> float:
        """CNN + Alternative.me 스코어를 가중 평균 → 0~100 정규화."""
        if not raw_scores:
            raise ValueError("empty fear_greed input")
        scores: list[float] = []
        for src in raw_scores:
            s = float(src["raw_score"])
            s = np.clip(s, 0.0, 100.0)
            scores.append(s)
        # 다중 소스 평균
        normalized: float = float(np.mean(scores))
        return round(normalized, 2)

    # ── 항목 2: 풋/콜 비율 모니터 ──
    def evaluate_put_call(
        self, equity_pcr: float, index_pcr: float
    ) -> tuple[str, float]:
        """Put/Call Ratio → 신호 및 0~100 환산 스코어 반환."""
        blended: float = 0.6 * equity_pcr + 0.4 * index_pcr
        if blended > 1.2:
            signal = "fear"
            score = max(0.0, -(blended - 1.2) * 100)
        elif blended < 0.5:
            signal = "greed"
            score = min(100.0, 100.0 - (0.5 - blended) * 200)
        else:
            signal = "neutral"
            # 선형 보간: 0.5→100, 1.2→0 범위를 0~100으로
            score = 100.0 * (1.2 - blended) / 0.7
        return signal, round(np.clip(score, 0.0, 100.0), 2)

    # ── 항목 3: VIX 텀 스트럭처 분석 ──
    def analyze_vix_term_structure(
        self, vix_spot: float, futures: list[dict]
    ) -> tuple[VIXStructure, float]:
        """백워데이션/콘탱고 감지, 0~100 환산."""
        if len(futures) < 2:
            raise ValueError("need >=2 futures months")
        front_month: float = futures[0]["price"]
        spread: float = (front_month - vix_spot) / vix_spot
        threshold: float = 0.02  # 2% 이내 = flat

        if spread < -threshold:
            structure = VIXStructure.BACKWARDATION
            score = max(0.0, 50.0 - abs(spread) * 500)
        elif spread > threshold:
            structure = VIXStructure.CONTANGO
            score = min(100.0, 50.0 + spread * 500)
        else:
            structure = VIXStructure.FLAT
            score = 50.0
        return structure, round(np.clip(score, 0.0, 100.0), 2)

    # ── 항목 4: AAII 투자자 심리 조사 연동 ──
    def evaluate_aaii(
        self, bullish_pct: float, bearish_pct: float
    ) -> tuple[bool, float]:
        """Bull/Bear 비율 → 역발상 플래그, 0~100 환산."""
        bull_bear_spread: float = bullish_pct - bearish_pct
        # 극단 약세: Bull < 20% → contrarian buy
        contrarian_flag: bool = bullish_pct < 20.0
        # -60 ~ +60 스프레드를 0~100으로 매핑
        score: float = 50.0 + (bull_bear_spread / 60.0) * 50.0
        return contrarian_flag, round(np.clip(score, 0.0, 100.0), 2)

    # ── 항목 5: 소셜 미디어 심리 지표 ──
    def evaluate_social_sentiment(
        self, records: list[dict], surge_threshold: float = 3.0
    ) -> tuple[bool, float]:
        """키워드 빈도 & 감성 집계 → 군중 형성 시그널."""
        if not records:
            return False, 50.0
        df = pd.DataFrame(records)
        avg_sentiment: float = float(df["sentiment_score"].mean())
        # 언급량 급증 감지: 최근 1시간 vs 이전 24시간 평균 대비 배율
        recent = df.sort_values("timestamp").tail(1)["mention_count"].sum()
        historical_avg = df["mention_count"].mean()
        surge_ratio: float = recent / max(historical_avg, 1.0)
        surge_detected: bool = surge_ratio >= surge_threshold
        # sentiment -1~+1 → 0~100
        score: float = (avg_sentiment + 1.0) / 2.0 * 100.0
        return surge_detected, round(np.clip(score, 0.0, 100.0), 2)

    # ── 종합 스코어 ──
    def compute_composite(
        self,
        fear_greed_input: list[dict],
        put_call_input: dict,
        vix_input: dict,
        aaii_input: dict,
        social_input: list[dict],
    ) -> SentimentResult:
        """5개 지표를 가중 합산하여 종합 심리 스코어 산출."""
        fg_score = self.compute_fear_greed(fear_greed_input)
        pc_signal, pc_score = self.evaluate_put_call(
            put_call_input["equity_put_call_ratio"],
            put_call_input["index_put_call_ratio"],
        )
        vix_struct, vix_score = self.analyze_vix_term_structure(
            vix_input["vix_spot"], vix_input["vix_futures"]
        )
        aaii_flag, aaii_score = self.evaluate_aaii(
            aaii_input["bullish_pct"], aaii_input["bearish_pct"]
        )
        social_surge, social_score = self.evaluate_social_sentiment(social_input)

        scores = {
            "fear_greed": fg_score,
            "put_call": pc_score,
            "vix_term": vix_score,
            "aaii": aaii_score,
            "social": social_score,
        }
        # 가중 평균
        composite: float = sum(
            scores[k] * self.WEIGHTS[k] for k in self.WEIGHTS
        )
        composite = round(np.clip(composite, 0.0, 100.0), 2)

        # Zone 판정
        if composite < 20:
            zone = SentimentZone.EXTREME_FEAR
        elif composite < 40:
            zone = SentimentZone.FEAR
        elif composite < 60:
            zone = SentimentZone.NEUTRAL
        elif composite < 80:
            zone = SentimentZone.GREED
        else:
            zone = SentimentZone.EXTREME_GREED

        # Confidence: 데이터 소스 가용 비율
        available = sum(1 for v in scores.values() if v != 50.0)
        confidence = round(available / len(scores), 2)

        return SentimentResult(
            composite_score=composite,
            zone=zone,
            fear_greed_normalized=fg_score,
            put_call_signal=pc_signal,
            vix_structure=vix_struct,
            aaii_contrarian_flag=aaii_flag,
            social_surge_detected=social_surge,
            confidence=confidence,
            timestamp=pd.Timestamp.utcnow().isoformat(),
        )
```

---

## E3. Output

### 출력 스키마

```yaml
SentimentResult:
  composite_score: float        # 0~100, 종합 심리 스코어
  zone: SentimentZone           # extreme_fear / fear / neutral / greed / extreme_greed
  fear_greed_normalized: float  # 0~100, Fear & Greed 정규화 값
  put_call_signal: str          # "fear" | "neutral" | "greed"
  vix_structure: VIXStructure   # backwardation | contango | flat
  aaii_contrarian_flag: bool    # True = 극단 약세 → 역발상 매수 조건
  social_surge_detected: bool   # True = 소셜 언급 급증 감지
  confidence: float             # 0.0~1.0, 데이터 소스 가용 비율
  timestamp: str                # ISO-8601 UTC
```

### Confidence 정의
| confidence 범위 | 의미 |
|-----------------|------|
| 0.8~1.0 | 5개 지표 모두 활성, 높은 신뢰도 |
| 0.6~0.8 | 4개 지표 활성, 양호 |
| 0.4~0.6 | 3개 지표 활성, 주의 필요 |
| < 0.4 | 과반 지표 비활성, 시그널 억제 권고 |

### 소비자
- `PortfolioWeightAdjuster`: composite_score → 전략 공격성/방어성 가중치 조절
- `ContrarianSignalEngine` (#16): extreme zone 시 역발상 시그널 발동
- `MarketPsychologyCycleDetector` (#18): 복합 지표로 사이클 단계 추정
- Kafka Topic: `sentiment.composite.v1`

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod

class BaseSentimentIndicator(ABC):
    """심리 지표 기본 인터페이스."""

    @abstractmethod
    def evaluate(self, data: dict) -> tuple[str, float]:
        """지표 평가 → (signal, score 0~100)."""
        ...

    @abstractmethod
    def validate_input(self, data: dict) -> bool:
        """입력 데이터 유효성 검증."""
        ...

class MarketSentimentEngine:
    """
    시장 심리 지표 통합 엔진.
    Inherits: -
    Consumed by: PortfolioWeightAdjuster, ContrarianSignalEngine

    Methods:
        compute_fear_greed(raw_scores: list[dict]) -> float
        evaluate_put_call(equity_pcr: float, index_pcr: float) -> tuple[str, float]
        analyze_vix_term_structure(vix_spot: float, futures: list[dict]) -> tuple[VIXStructure, float]
        evaluate_aaii(bullish_pct: float, bearish_pct: float) -> tuple[bool, float]
        evaluate_social_sentiment(records: list[dict], surge_threshold: float) -> tuple[bool, float]
        compute_composite(...) -> SentimentResult
    """

    def publish_to_kafka(self, result: SentimentResult, topic: str = "sentiment.composite.v1") -> None:
        """Kafka로 결과 발행."""
        ...

    def store_to_timescaledb(self, result: SentimentResult) -> None:
        """TimescaleDB hypertable에 저장."""
        ...
```

---

## E5. Tech Stack Dependency

| 기술 | 용도 | SPEC §14 LOCK |
|------|------|---------------|
| **Kafka** | 실시간 심리 지표 스트리밍 (topic: `sentiment.*`) | ☑ |
| **TimescaleDB** | 시계열 심리 스코어 저장 (hypertable: `sentiment_scores`) | ☑ |
| **pandas** | 소셜 데이터 집계, forward-fill 전처리 | ☑ |
| **numpy** | 수치 연산, 클리핑, 통계 | ☑ |
| **scikit-learn** | 소셜 감성 분류기 (향후 확장) | ☑ |

---

## E6. Performance Requirements

| 지표 | 목표 | 비고 |
|------|------|------|
| 종합 스코어 산출 지연 | < 500ms | 5개 지표 가중합 기준 |
| Fear & Greed 수집 주기 | 5분 | API rate limit 준수 |
| 소셜 감성 집계 주기 | 1시간 | 봇 필터 포함 |
| AAII 갱신 주기 | 주 1회 (목요일) | 소스 업데이트 주기 |
| VIX 데이터 지연 | < 1초 | 장중 실시간 |
| 동시 처리 | 50 종목 이상 소셜 모니터링 | Kafka consumer group |

---

## E7. Error Handling

| 오류 상황 | 처리 방식 | 폴백 |
|-----------|-----------|------|
| Fear & Greed API 장애 | 3회 재시도 (exponential backoff) | 직전 유효값 사용, confidence 차감 |
| CBOE 데이터 지연 | 30초 타임아웃 후 캐시 값 | put_call weight를 0으로 설정 |
| VIX 선물 데이터 부족 | 최소 2개월 미만 시 경고 | VIX 지표 비활성, 나머지 가중치 재분배 |
| AAII 미발표 | 이전 주 데이터 유지 | confidence 소폭 차감 |
| 소셜 API rate limit | 큐잉 후 다음 윈도우에 재수집 | 이전 집계 결과 유지 |
| 전체 입력 부재 | composite_score = NaN, zone = NEUTRAL | 시그널 발행 중단, 알림 |

---

## E8. Test Criteria

### Unit Tests
- `test_compute_fear_greed_normalization`: CNN 85, Alt.me 75 → 평균 80.0
- `test_put_call_fear_signal`: PCR 1.5 → signal="fear"
- `test_put_call_greed_signal`: PCR 0.3 → signal="greed"
- `test_vix_backwardation`: spot=30, front=25 → BACKWARDATION
- `test_vix_contango`: spot=15, front=20 → CONTANGO
- `test_aaii_contrarian`: bullish=15% → contrarian_flag=True
- `test_social_surge_detection`: recent 3x avg → surge=True
- `test_score_clipping`: raw_score=120 → clipped to 100

### Integration Tests
- `test_composite_all_sources`: 5개 소스 모두 투입 → confidence=1.0
- `test_composite_partial_sources`: 3개 소스만 → confidence=0.6
- `test_kafka_publish`: SentimentResult → Kafka topic 발행 확인
- `test_timescaledb_store`: 결과 저장 후 조회 일치 확인

### Acceptance Tests
- 2020-03 코로나 폭락 데이터 → zone=EXTREME_FEAR
- 2021-01 GameStop 사태 → social_surge_detected=True
- 정상 시장 데이터 → zone=NEUTRAL ±1 등급

---

## E9. LOCK References

| LOCK 항목 | 본 문서 적용 |
|-----------|-------------|
| SPEC §14 Kafka | `sentiment.composite.v1` topic, consumer group `sentiment-engine` |
| SPEC §14 TimescaleDB | hypertable `sentiment_scores`, 파티션 키 `timestamp` |
| SPEC §14 pandas | 소셜 데이터 DataFrame 집계, forward-fill 전처리 |
| SPEC §14 numpy | np.clip, np.mean 수치 연산 |
| SPEC §14 scikit-learn | 향후 소셜 감성 분류 모델 확장 예약 |

---

> **L3 판정**
> - E1~E9 전 항목 작성 완료 ☑
> - Python pseudocode copy-to-implement 가능 ☑
> - SPEC §14 LOCK 기술스택 준수 ☑
> - 판정: **L3 APPROVED**
