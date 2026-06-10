# 뉴스 심리 임팩트 분석 (News Sentiment Impact)
> **버전**: v2.1
> **Status**: APPROVED
> **작성일**: 2026-03-22
> **Last-reviewed**: 2026-03-23
> **원본 관점**: #2 투자 심리학 & 행동재무학
> **정본 소유 개념**: FinBERT / NLP 감성 분석
> **기술스택 의존성**: SPEC §14 LOCK 범위 내
> **L3 완성도**: E1 ☑ | E2 ☑ | E3 ☑ | E4 ☑ | E5 ☑ | E6 ☑ | E7 ☑ | E8 ☑ | E9 ☑

---

### B-5. 뉴스 심리 임팩트 분석 (News Sentiment Impact)

**현재**: FinBERT 감성 분류만 있고, 심리적 영향도 분석 없음
**필요한 것**:

| # | 항목 | 상세 |
|---|------|------|
| 21 | **뉴스 심리 임팩트 점수** | 뉴스 감성 × 도달 범위 × 반복 빈도 = 임팩트 스코어. 같은 부정 뉴스도 헤드라인 1회 vs 24시간 연속 보도는 심리 영향 다름 |
| 22 | **내러티브(Narrative) 추적기** | 시장을 움직이는 "이야기"(AI 버블, 금리 인하 기대, 연착륙 등) 추적. 내러티브 전환점 감지 → 심리 변곡점 예측 |
| 23 | **뉴스 피로도(News Fatigue) 감지** | 반복 뉴스에 시장이 둔감해지는 시점 감지. 동일 주제 뉴스 N회 이상 → 가격 반응 감소 패턴 → "뉴스 이미 가격에 반영됨" 판단 |
| 24 | **서프라이즈 팩터(Surprise Factor)** | 시장 컨센서스 대비 실제 결과 괴리도. 실적/경제지표가 예상보다 +/- 일 때 심리적 충격 크기 정량화 → 포지션 조절 규모 결정 |

---

## 결함 극복

### D-04: 감성 분석 부재 (Medium)

**결함**: 뉴스/SNS 데이터 미반영. 시장 심리 정량화 수단 없음.

**극복 방안**: FinBERT 감성 분석 통합

- FinBERT 파인튜닝: 금융 도메인 특화 감성 분류 (긍정/부정/중립)
- 입력 소스: 뉴스 헤드라인, 실적 발표 컨퍼런스 콜, SEC 공시, 소셜 미디어
- 감성 점수 → 투자 시그널 변환:
  - 종목별 감성 점수 시계열 생성
  - 급격한 감성 변화(sentiment shift) 감지 → 포지션 조절 트리거
  - 감성 모멘텀: 감성 점수의 이동평균 추세
- VAMOS_EVENT 스키마(SPEC §4.2) 연동: event_type="sentiment"

> **SPEC 참조**: SPEC §17 D-04

---

## E1. Input

### 데이터 스키마

```yaml
news_article:
  article_id: str           # UUID, 필수
  headline: str              # 뉴스 제목, 필수
  body: str                  # 뉴스 본문, 선택 (없으면 headline만 분석)
  source: str                # 출처 (reuters, bloomberg 등), 필수
  published_at: datetime     # 발행 시각 UTC, 필수
  ticker_symbols: list[str]  # 관련 종목 코드, 필수 (최소 1개)
  reach_score: float         # 매체 도달범위 0.0~1.0, 필수
  category: str              # 카테고리 (earnings, macro, geopolitical 등), 선택

consensus_data:
  ticker: str                # 종목 코드, 필수
  metric_type: str           # eps, revenue, gdp, cpi 등, 필수
  consensus_value: float     # 컨센서스 값, 필수
  actual_value: float | None # 실제 발표 값 (발표 후), 선택
  report_date: datetime      # 발표 예정/실제 일자, 필수

price_reaction:
  ticker: str                # 종목 코드, 필수
  timestamp: datetime        # 가격 시점, 필수
  price: float               # 현재가, 필수
  volume: int                # 거래량, 필수
```

### 필수 필드
- `article_id`, `headline`, `source`, `published_at`, `ticker_symbols`, `reach_score`
- `consensus_data.ticker`, `consensus_data.metric_type`, `consensus_data.consensus_value`

### 전처리
1. 뉴스 본문 정규화: HTML 태그 제거, 유니코드 정규화(NFC)
2. 중복 기사 dedup: headline TF-IDF cosine similarity > 0.85 → 동일 기사로 병합
3. 시간 정규화: 모든 timestamp → UTC 변환
4. reach_score 누락 시 소스별 기본값 매핑 (reuters=0.9, unknown=0.3)

---

## E2. Algorithm

```python
import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


@dataclass
class SentimentResult:
    sentiment: float          # -1.0 ~ 1.0
    confidence: float         # 0.0 ~ 1.0
    label: str                # "positive" | "negative" | "neutral"


@dataclass
class ImpactScore:
    article_id: str
    ticker: str
    sentiment: float
    reach: float
    repetition_factor: float
    impact: float             # sentiment × reach × repetition_factor
    computed_at: datetime


@dataclass
class NarrativeCluster:
    narrative_id: str
    theme: str                # e.g., "AI_bubble", "rate_cut_expectation"
    keywords: list[str]
    article_count: int
    avg_sentiment: float
    trend: str                # "rising" | "stable" | "declining"
    pivot_detected: bool


@dataclass
class FatigueSignal:
    ticker: str
    topic: str
    repetition_count: int
    price_reaction_decay: float   # 가격 반응 감소율
    is_fatigued: bool
    fatigue_onset: Optional[datetime]


@dataclass
class SurpriseResult:
    ticker: str
    metric_type: str
    consensus: float
    actual: float
    surprise_pct: float           # (actual - consensus) / |consensus| × 100
    shock_magnitude: float        # 표준화된 충격 크기 0~1
    position_adjustment: float    # 포지션 조절 비율 -1.0~1.0


class NewsSentimentAnalyzer:
    """#21~24: 뉴스 심리 임팩트 분석 통합 클래스"""

    FATIGUE_THRESHOLD: int = 10          # 동일 주제 기사 N개 이상
    FATIGUE_DECAY_THRESHOLD: float = 0.3 # 가격반응 감소율 30% 이하
    SURPRISE_SIGMA_SCALE: float = 2.0    # 서프라이즈 정규화 스케일
    NARRATIVE_WINDOW_DAYS: int = 14      # 내러티브 추적 윈도우

    def __init__(self, finbert_model, historical_surprises: pd.DataFrame):
        """
        Args:
            finbert_model: 사전 학습된 FinBERT 감성 분류 모델
            historical_surprises: 과거 서프라이즈 데이터 (정규화용)
        """
        self._model = finbert_model
        self._hist_surprises = historical_surprises
        self._narrative_buffer: dict[str, list[dict]] = {}
        self._article_history: pd.DataFrame = pd.DataFrame()

    # ── #21 뉴스 심리 임팩트 점수 ──────────────────────────
    def compute_impact_score(
        self,
        article: dict,
        window_hours: int = 24
    ) -> ImpactScore:
        """감성 × 도달범위 × 반복빈도 = 임팩트 스코어 산출"""
        sentiment_result: SentimentResult = self._run_sentiment(article["headline"], article.get("body"))
        reach: float = article["reach_score"]

        # 반복 빈도: 최근 window_hours 내 동일 주제 기사 수 기반
        cutoff: datetime = datetime.utcnow() - timedelta(hours=window_hours)
        recent: pd.DataFrame = self._article_history[
            (self._article_history["published_at"] >= cutoff) &
            (self._article_history["ticker"].isin(article["ticker_symbols"]))
        ]
        repetition_count: int = len(recent) + 1
        # 반복 빈도 팩터: log 스케일 (1→1.0, 10→2.3, 100→4.6)
        repetition_factor: float = float(np.log1p(repetition_count))

        impact: float = sentiment_result.sentiment * reach * repetition_factor
        impact = float(np.clip(impact, -10.0, 10.0))

        # 반복 빈도 누적: 본 기사 이력을 저장하여 후속 호출에서 repetition_count 반영
        self._article_history = pd.concat([
            self._article_history,
            pd.DataFrame([{
                "article_id": article["article_id"],
                "ticker": article["ticker_symbols"][0],
                "published_at": article.get("published_at", datetime.utcnow()),
            }]),
        ], ignore_index=True)

        return ImpactScore(
            article_id=article["article_id"],
            ticker=article["ticker_symbols"][0],
            sentiment=sentiment_result.sentiment,
            reach=reach,
            repetition_factor=repetition_factor,
            impact=impact,
            computed_at=datetime.utcnow()
        )

    # ── #22 내러티브 추적기 ──────────────────────────────
    def track_narrative(
        self,
        articles: list[dict],
        n_clusters: int = 8
    ) -> list[NarrativeCluster]:
        """시장 내러티브 클러스터링 및 전환점 감지"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans

        texts: list[str] = [a["headline"] + " " + a.get("body", "") for a in articles]
        vectorizer = TfidfVectorizer(max_features=5000, stop_words="english")
        tfidf_matrix = vectorizer.fit_transform(texts)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(tfidf_matrix)

        feature_names: list[str] = vectorizer.get_feature_names_out().tolist()
        clusters: list[NarrativeCluster] = []

        for cluster_id in range(n_clusters):
            mask = labels == cluster_id
            cluster_articles = [a for a, m in zip(articles, mask) if m]
            if not cluster_articles:
                continue

            # 클러스터 키워드 추출 (상위 5개)
            center = kmeans.cluster_centers_[cluster_id]
            top_indices = center.argsort()[-5:][::-1]
            keywords = [feature_names[i] for i in top_indices]

            # 감성 추세 분석
            sentiments = [self._run_sentiment(a["headline"]).sentiment for a in cluster_articles]
            avg_sentiment: float = float(np.mean(sentiments))

            # 전환점 감지: 최근 3일 vs 이전 감성 비교
            recent_cutoff = datetime.utcnow() - timedelta(days=3)
            recent_sents = [s for a, s in zip(cluster_articles, sentiments)
                           if a["published_at"] >= recent_cutoff]
            older_sents = [s for a, s in zip(cluster_articles, sentiments)
                          if a["published_at"] < recent_cutoff]

            if recent_sents and older_sents:
                delta = np.mean(recent_sents) - np.mean(older_sents)
                if delta > 0.2:
                    trend = "rising"
                elif delta < -0.2:
                    trend = "declining"
                else:
                    trend = "stable"
                pivot_detected = abs(delta) > 0.4
            else:
                trend = "stable"
                pivot_detected = False

            clusters.append(NarrativeCluster(
                narrative_id=f"NR-{cluster_id:03d}",
                theme="_".join(keywords[:3]),
                keywords=keywords,
                article_count=len(cluster_articles),
                avg_sentiment=avg_sentiment,
                trend=trend,
                pivot_detected=pivot_detected
            ))

        return clusters

    # ── #23 뉴스 피로도 감지 ──────────────────────────────
    def detect_fatigue(
        self,
        ticker: str,
        topic: str,
        articles: list[dict],
        price_reactions: pd.DataFrame
    ) -> FatigueSignal:
        """반복 뉴스에 대한 시장 둔감화 시점 감지"""
        # 시간순 정렬
        sorted_articles = sorted(articles, key=lambda a: a["published_at"])
        repetition_count: int = len(sorted_articles)

        if repetition_count < 3 or price_reactions.empty:
            return FatigueSignal(
                ticker=ticker, topic=topic,
                repetition_count=repetition_count,
                price_reaction_decay=1.0,
                is_fatigued=False, fatigue_onset=None
            )

        # 각 기사 발행 후 30분 가격 변동률 계산
        reactions: list[float] = []
        for art in sorted_articles:
            t0 = art["published_at"]
            t1 = t0 + timedelta(minutes=30)
            window = price_reactions[
                (price_reactions["timestamp"] >= t0) &
                (price_reactions["timestamp"] <= t1)
            ]
            if len(window) >= 2:
                pct_change = abs(
                    (window["price"].iloc[-1] - window["price"].iloc[0])
                    / window["price"].iloc[0]
                )
                reactions.append(pct_change)

        if len(reactions) < 3:
            return FatigueSignal(
                ticker=ticker, topic=topic,
                repetition_count=repetition_count,
                price_reaction_decay=1.0,
                is_fatigued=False, fatigue_onset=None
            )

        # 초반 vs 최근 반응 비교
        first_half = np.mean(reactions[:len(reactions)//2])
        second_half = np.mean(reactions[len(reactions)//2:])
        decay: float = second_half / first_half if first_half > 0 else 1.0

        is_fatigued: bool = (
            repetition_count >= self.FATIGUE_THRESHOLD and
            decay <= self.FATIGUE_DECAY_THRESHOLD
        )
        fatigue_onset: Optional[datetime] = (
            sorted_articles[self.FATIGUE_THRESHOLD - 1]["published_at"]
            if is_fatigued else None
        )

        return FatigueSignal(
            ticker=ticker, topic=topic,
            repetition_count=repetition_count,
            price_reaction_decay=float(decay),
            is_fatigued=is_fatigued,
            fatigue_onset=fatigue_onset
        )

    # ── #24 서프라이즈 팩터 ──────────────────────────────
    def compute_surprise(
        self,
        consensus: dict
    ) -> SurpriseResult:
        """컨센서스 대비 실제 결과 괴리도 정량화"""
        actual: float = consensus["actual_value"]
        expected: float = consensus["consensus_value"]

        if expected == 0:
            surprise_pct = 0.0
        else:
            surprise_pct = ((actual - expected) / abs(expected)) * 100.0

        # 과거 서프라이즈 분포 기반 정규화
        hist = self._hist_surprises[
            self._hist_surprises["metric_type"] == consensus["metric_type"]
        ]["surprise_pct"]
        if len(hist) > 10:
            mu = float(hist.mean())
            sigma = float(hist.std())
            z_score = (surprise_pct - mu) / sigma if sigma > 0 else 0.0
            shock_magnitude = float(np.clip(
                abs(z_score) / self.SURPRISE_SIGMA_SCALE, 0.0, 1.0
            ))
        else:
            shock_magnitude = float(np.clip(abs(surprise_pct) / 20.0, 0.0, 1.0))

        # 포지션 조절 비율: 방향 × 충격 크기
        direction = 1.0 if surprise_pct > 0 else -1.0
        position_adjustment = direction * shock_magnitude

        return SurpriseResult(
            ticker=consensus["ticker"],
            metric_type=consensus["metric_type"],
            consensus=expected,
            actual=actual,
            surprise_pct=float(surprise_pct),
            shock_magnitude=shock_magnitude,
            position_adjustment=float(position_adjustment)
        )

    # ── 내부 헬퍼 ──────────────────────────────────────
    def _run_sentiment(
        self,
        headline: str,
        body: Optional[str] = None
    ) -> SentimentResult:
        """FinBERT 모델 호출 래퍼"""
        text = headline if body is None else f"{headline}. {body[:512]}"
        raw = self._model.predict(text)  # -> {"label": str, "score": float}
        label_map = {"positive": 1.0, "negative": -1.0, "neutral": 0.0}
        sentiment_val = label_map.get(raw["label"], 0.0) * raw["score"]
        return SentimentResult(
            sentiment=sentiment_val,
            confidence=raw["score"],
            label=raw["label"]
        )
```

---

## E3. Output

### 출력 스키마

```yaml
impact_score_output:
  article_id: str
  ticker: str
  sentiment: float            # -1.0 ~ 1.0
  reach: float                # 0.0 ~ 1.0
  repetition_factor: float    # 1.0+
  impact: float               # -10.0 ~ 10.0
  confidence: float           # FinBERT 감성 신뢰도 0.0~1.0
  computed_at: datetime

narrative_output:
  narrative_id: str
  theme: str
  keywords: list[str]
  article_count: int
  avg_sentiment: float
  trend: str                  # "rising" | "stable" | "declining"
  pivot_detected: bool
  confidence: float           # 클러스터 응집도 기반 0.0~1.0

fatigue_output:
  ticker: str
  topic: str
  repetition_count: int
  price_reaction_decay: float
  is_fatigued: bool
  fatigue_onset: datetime | null
  confidence: float           # 반응 데이터 포인트 수 기반

surprise_output:
  ticker: str
  metric_type: str
  surprise_pct: float
  shock_magnitude: float      # 0.0 ~ 1.0
  position_adjustment: float  # -1.0 ~ 1.0
  confidence: float           # 과거 분포 샘플 수 기반
```

### Confidence 산출
- **임팩트 점수**: FinBERT 모델 confidence 직접 사용
- **내러티브**: 클러스터 내 silhouette score 기반
- **피로도**: min(1.0, price_reaction_data_points / 20)
- **서프라이즈**: min(1.0, historical_sample_count / 100)

### 소비자
- `03_portfolio-strategy`: 포지션 조절 시그널
- `05_risk-management`: 이벤트 리스크 평가
- Kafka topic: `vamos.sentiment.impact`, `vamos.sentiment.narrative`, `vamos.sentiment.fatigue`, `vamos.sentiment.surprise`

---

## E4. Class/API Design

```python
from abc import ABC, abstractmethod


class BaseSentimentAnalyzer(ABC):
    """감성 분석 기반 클래스"""

    @abstractmethod
    def analyze(self, data: dict) -> dict:
        ...

    @abstractmethod
    def get_confidence(self) -> float:
        ...


class NewsSentimentAnalyzer(BaseSentimentAnalyzer):
    """
    #21~24 통합 클래스
    Inherits: BaseSentimentAnalyzer

    Public Methods:
        compute_impact_score(article: dict, window_hours: int = 24) -> ImpactScore
        track_narrative(articles: list[dict], n_clusters: int = 8) -> list[NarrativeCluster]
        detect_fatigue(ticker: str, topic: str, articles: list[dict], price_reactions: pd.DataFrame) -> FatigueSignal
        compute_surprise(consensus: dict) -> SurpriseResult
        analyze(data: dict) -> dict           # 통합 진입점
        get_confidence() -> float

    Kafka Produce:
        vamos.sentiment.impact
        vamos.sentiment.narrative
        vamos.sentiment.fatigue
        vamos.sentiment.surprise

    Kafka Consume:
        vamos.news.raw
        vamos.market.consensus
        vamos.market.price
    """
    pass
```

---

## E5. Tech Stack Dependency

| 구분 | 기술 | 용도 | SPEC §14 LOCK |
|------|------|------|---------------|
| 메시징 | **Kafka** | 뉴스 이벤트 스트림 수신/발행 | ☑ LOCKED |
| 시계열DB | **TimescaleDB** | 임팩트 스코어·피로도 시계열 저장 | ☑ LOCKED |
| 데이터 처리 | **pandas** | 뉴스 기사·가격 반응 DataFrame 처리 | ☑ LOCKED |
| 수치 연산 | **numpy** | 감성 점수 정규화, 통계 연산 | ☑ LOCKED |
| ML | **scikit-learn** | TF-IDF 벡터화, KMeans 클러스터링 | ☑ LOCKED |
| NLP 모델 | FinBERT | 금융 도메인 감성 분류 | 외부 모델 (LOCK 외) |

---

## E6. Performance Requirements

| 지표 | 목표 | 비고 |
|------|------|------|
| 단건 임팩트 스코어 산출 | ≤ 200ms | FinBERT 추론 포함 |
| 내러티브 클러스터링 (1000건) | ≤ 5s | 일 1회 배치 허용 |
| 피로도 감지 | ≤ 500ms | 실시간 스트림 |
| 서프라이즈 팩터 산출 | ≤ 100ms | 발표 시점 즉시 |
| Kafka 메시지 처리 throughput | ≥ 500 msg/s | 뉴스 피크 시간대 |
| TimescaleDB 쓰기 | ≤ 50ms/row | 배치 insert 권장 |

---

## E7. Error Handling

| 오류 상황 | 처리 방식 | Fallback |
|-----------|-----------|----------|
| FinBERT 모델 로드 실패 | 서비스 시작 차단, 알림 | 룰 기반 키워드 감성 사전 |
| 뉴스 API 타임아웃 | 3회 재시도 (exponential backoff) | 캐시된 최근 기사 사용 |
| consensus_data 누락 | 서프라이즈 계산 스킵 | confidence=0 반환 |
| 가격 데이터 부족 (피로도) | 최소 3개 미만 시 피로도 미판정 | is_fatigued=False 반환 |
| Kafka 발행 실패 | DLQ(Dead Letter Queue) 전송 | 로컬 파일 버퍼 |
| TF-IDF 빈 입력 | 빈 클러스터 리스트 반환 | 로그 WARNING |
| 0 나눗기 (surprise_pct) | consensus=0 시 surprise_pct=0 | 별도 플래그 표시 |

---

## E8. Test Criteria

### Unit Tests
- [ ] `compute_impact_score`: 긍정 뉴스 + 높은 reach → impact > 0 확인
- [ ] `compute_impact_score`: 반복 빈도 증가 시 repetition_factor 로그 스케일 증가 확인
- [ ] `track_narrative`: 동일 주제 기사 → 하나의 클러스터로 그룹핑 확인
- [ ] `track_narrative`: 감성 급변 시 pivot_detected=True 확인
- [ ] `detect_fatigue`: 10회 이상 반복 + 가격 반응 30% 이하 → is_fatigued=True
- [ ] `detect_fatigue`: 데이터 부족 시 is_fatigued=False 반환
- [ ] `compute_surprise`: actual > consensus → positive surprise_pct
- [ ] `compute_surprise`: shock_magnitude 범위 0.0~1.0 클리핑 확인
- [ ] `_run_sentiment`: FinBERT 래퍼 정상 label 매핑 확인

### Integration Tests
- [ ] Kafka `vamos.news.raw` 수신 → `vamos.sentiment.impact` 발행 E2E
- [ ] TimescaleDB에 임팩트 스코어 시계열 저장/조회
- [ ] 내러티브 배치 → 클러스터 결과 DB 저장

### Acceptance Tests
- [ ] 실제 뉴스 100건 대상 임팩트 스코어 분포 합리성 검증 (평균 절대값 < 5.0)
- [ ] 뉴스 피로도 감지: 과거 사례 (연준 금리 동결 반복 보도) 재현 시 is_fatigued=True
- [ ] 서프라이즈 팩터: 과거 실적 발표 데이터 대비 shock_magnitude 순위 정합성

---

## E9. LOCK References

| SPEC 참조 | 내용 |
|-----------|------|
| SPEC §4.2 | VAMOS_EVENT 스키마 연동 (event_type="sentiment") |
| SPEC §14 | 기술스택 LOCK (Kafka, TimescaleDB, pandas, numpy, scikit-learn) |
| SPEC §17 D-04 | 감성 분석 부재 결함 극복 |

---

## STEP7-I 보강: 한국어 FinGPT/KoFinBERT 확장 상세, LoRA 파인튜닝 절차 (S7I-002)

> **보강 근거**: step7i_mapping.md PARTIAL — 한국어 금융 감성 분석 모델(KoFinBERT) 및 LoRA 파인튜닝 파이프라인 상세 누락
> **Priority**: HIGH

### E1. Input
- **데이터**: Pre-trained KoFinBERT base model (snunlp/KR-FinBert 기반), 한국어 금융 코퍼스 (금감원 공시, 증권사 리포트, 경제 뉴스), LoRA adapter config (rank, alpha, target modules)
- **필수 필드**:
  - `base_model_name`: str — HuggingFace 모델 경로 (e.g., "snunlp/KR-FinBert-SC")
  - `train_dataset`: List[Dict] — `{"text": str, "label": int}` (0=부정, 1=중립, 2=긍정)
  - `lora_config`: Dict — `{"r": 8, "lora_alpha": 32, "target_modules": ["query", "value"], "lora_dropout": 0.05}`
  - `max_length`: int — 토큰 최대 길이 (default 512)
- **전처리**:
  - 한국어 형태소 분석(Mecab-ko) → 불용어 제거 → 금융 도메인 특수 토큰 추가
  - 레이블 불균형 처리: 소수 클래스 오버샘플링 (SMOTE 또는 back-translation augmentation)
  - Train/Val/Test split = 8:1:1, stratified by label

### E2. Algorithm
```python
# 의사코드 — KoFinBERT LoRA 파인튜닝 파이프라인
# 복사→구현 가능 수준

from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import LoraConfig, get_peft_model, TaskType, PeftModel
from torch.utils.data import DataLoader
import torch

class KoFinBertLoRATrainer:
    """한국어 금융 감성 분석 LoRA 파인튜닝 파이프라인"""

    def __init__(self, base_model_name: str, lora_config: dict, device: str = "cuda"):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(base_model_name)
        self.base_model = AutoModelForSequenceClassification.from_pretrained(
            base_model_name, num_labels=3  # 부정/중립/긍정
        )
        # LoRA 어댑터 설정
        peft_config = LoraConfig(
            task_type=TaskType.SEQ_CLS,
            r=lora_config.get("r", 8),
            lora_alpha=lora_config.get("lora_alpha", 32),
            target_modules=lora_config.get("target_modules", ["query", "value"]),
            lora_dropout=lora_config.get("lora_dropout", 0.05),
            bias="none",
        )
        # 기존 가중치 freeze → LoRA 어댑터만 학습 가능
        self.model = get_peft_model(self.base_model, peft_config)
        self.model.print_trainable_parameters()  # 학습 파라미터 수 확인 (~0.5% of total)

    def _prepare_dataset(self, dataset: list[dict], max_length: int = 512) -> DataLoader:
        """한국어 금융 텍스트 토큰화 및 DataLoader 생성"""
        encodings = self.tokenizer(
            [item["text"] for item in dataset],
            truncation=True, padding="max_length",
            max_length=max_length, return_tensors="pt"
        )
        labels = torch.tensor([item["label"] for item in dataset])
        torch_dataset = torch.utils.data.TensorDataset(
            encodings["input_ids"], encodings["attention_mask"], labels
        )
        return DataLoader(torch_dataset, batch_size=16, shuffle=True)

    def fine_tune(self, train_data: list[dict], val_data: list[dict],
                  epochs: int = 5, lr: float = 2e-4, max_length: int = 512) -> dict:
        """LoRA 파인튜닝 실행"""
        train_loader = self._prepare_dataset(train_data, max_length)
        val_loader = self._prepare_dataset(val_data, max_length)

        optimizer = torch.optim.AdamW(self.model.parameters(), lr=lr)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
        best_val_f1 = 0.0

        for epoch in range(epochs):
            # --- Training ---
            self.model.train()
            total_loss = 0.0
            for batch in train_loader:
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                loss = outputs.loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                optimizer.step()
                optimizer.zero_grad()
                total_loss += loss.item()

            scheduler.step()

            # --- Validation ---
            val_f1 = self._evaluate(val_loader)
            if val_f1 > best_val_f1:
                best_val_f1 = val_f1
                self.model.save_pretrained("checkpoints/kofinbert-lora-best")

        return {"best_val_f1": best_val_f1, "epochs_trained": epochs}

    def _evaluate(self, data_loader: DataLoader) -> float:
        """F1-score 기반 검증"""
        from sklearn.metrics import f1_score
        self.model.eval()
        all_preds, all_labels = [], []
        with torch.no_grad():
            for batch in data_loader:
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                outputs = self.model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=-1)
                all_preds.extend(preds.cpu().tolist())
                all_labels.extend(labels.cpu().tolist())
        return f1_score(all_labels, all_preds, average="macro")

    def merge_and_export(self, output_path: str) -> str:
        """LoRA 어댑터를 base model에 병합 후 배포용 모델 저장"""
        merged_model = self.model.merge_and_unload()
        merged_model.save_pretrained(output_path)
        self.tokenizer.save_pretrained(output_path)
        return output_path

    def predict(self, text: str) -> dict:
        """단건 추론"""
        self.model.eval()
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                max_length=512, padding="max_length").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0]
        label_map = {0: "부정", 1: "중립", 2: "긍정"}
        pred_idx = torch.argmax(probs).item()
        return {
            "label": label_map[pred_idx],
            "score": round(probs[pred_idx].item(), 4),
            "probabilities": {label_map[i]: round(p.item(), 4) for i, p in enumerate(probs)},
        }
```

### E3. Output
- **스키마**:
```python
@dataclass
class KoFinBertResult:
    text: str                          # 입력 원문
    label: str                         # "긍정" | "중립" | "부정"
    score: float                       # 예측 확률 (0.0~1.0)
    probabilities: dict[str, float]    # {"긍정": 0.85, "중립": 0.10, "부정": 0.05}
    model_version: str                 # "kofinbert-lora-v1.2"
    domain_entities: list[str]         # 추출된 금융 엔티티 ["삼성전자", "영업이익", "컨센서스"]
    inference_time_ms: float           # 추론 소요 시간
    timestamp: datetime                # 분석 시점
```
- **소비자**: `SentimentImpactCalculator` (임팩트 스코어 산출), `NarrativeTracker` (내러티브 클러스터링 입력), `vamos.sentiment.impact` Kafka 토픽

### E4. Class/API Design
```python
class KoFinBertSentimentAnalyzer:
    """한국어 금융 감성 분석 통합 클래스 — LoRA 파인튜닝 + 추론"""

    def __init__(self, model_path: str, device: str = "cuda"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(device).eval()
        self.device = device
        self._label_map = {0: "부정", 1: "중립", 2: "긍정"}

    @classmethod
    def fine_tune(cls, base_model: str, train_data: list[dict],
                  val_data: list[dict], lora_config: dict,
                  output_path: str, epochs: int = 5) -> "KoFinBertSentimentAnalyzer":
        """LoRA 파인튜닝 후 병합된 모델로 인스턴스 반환"""
        trainer = KoFinBertLoRATrainer(base_model, lora_config)
        result = trainer.fine_tune(train_data, val_data, epochs=epochs)
        trainer.merge_and_export(output_path)
        return cls(output_path)

    def predict(self, text: str) -> KoFinBertResult:
        """단건 감성 분석"""
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True,
                                max_length=512, padding="max_length").to(self.device)
        start = time.perf_counter()
        with torch.no_grad():
            outputs = self.model(**inputs)
        elapsed_ms = (time.perf_counter() - start) * 1000

        probs = torch.softmax(outputs.logits, dim=-1)[0]
        pred_idx = torch.argmax(probs).item()
        return KoFinBertResult(
            text=text, label=self._label_map[pred_idx],
            score=round(probs[pred_idx].item(), 4),
            probabilities={self._label_map[i]: round(p.item(), 4) for i, p in enumerate(probs)},
            model_version=self._get_model_version(),
            domain_entities=self._extract_entities(text),
            inference_time_ms=round(elapsed_ms, 2),
            timestamp=datetime.utcnow(),
        )

    def batch_predict(self, texts: list[str], batch_size: int = 32) -> list[KoFinBertResult]:
        """배치 감성 분석 — GPU 활용 최적화"""
        results = []
        for i in range(0, len(texts), batch_size):
            batch_texts = texts[i:i + batch_size]
            inputs = self.tokenizer(batch_texts, return_tensors="pt", truncation=True,
                                    max_length=512, padding=True).to(self.device)
            with torch.no_grad():
                outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=-1)
            for j, text in enumerate(batch_texts):
                pred_idx = torch.argmax(probs[j]).item()
                results.append(KoFinBertResult(
                    text=text, label=self._label_map[pred_idx],
                    score=round(probs[j][pred_idx].item(), 4),
                    probabilities={self._label_map[k]: round(p.item(), 4) for k, p in enumerate(probs[j])},
                    model_version=self._get_model_version(),
                    domain_entities=self._extract_entities(text),
                    inference_time_ms=0.0,  # 배치 모드에서는 개별 측정 불가
                    timestamp=datetime.utcnow(),
                ))
        return results

    def _extract_entities(self, text: str) -> list[str]:
        """금융 도메인 엔티티 추출 (종목명, 지표명 등)"""
        # KoreanFinancialTokenizer 연동 (S7I-035)
        pass

    def _get_model_version(self) -> str:
        return "kofinbert-lora-v1.0"
```

### E5. Tech Stack Dependency
| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| transformers | ≥4.36.0 | ☑ | KoFinBERT 모델 로딩, 토크나이저 |
| peft | ≥0.7.0 | ☑ | LoRA 어댑터 생성/학습/병합 |
| torch | ≥2.1.0 | ☑ | GPU 학습/추론 백엔드 |
| konlpy | ≥0.6.0 | ☑ | 한국어 형태소 분석 (전처리) |
| scikit-learn | ≥1.3.0 | ☑ | F1-score 평가, 데이터 분할 |
| accelerate | ≥0.25.0 | ☑ | 멀티 GPU / mixed precision 지원 |

### E6. Performance Requirements
| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 단건 추론 지연 | < 50ms / article | `time.perf_counter()` 기준, GPU warm-up 후 측정 |
| 배치 추론 처리량 | ≥ 200 articles/sec (batch=32) | 1000건 배치 추론 평균 |
| LoRA 파인튜닝 시간 | < 4시간 (single A100 GPU) | 10만건 학습 데이터 기준 |
| 모델 메모리 사용량 | < 4GB VRAM (추론 시) | `torch.cuda.max_memory_allocated()` |
| LoRA 어댑터 크기 | < 50MB | 디스크 저장 크기 기준 |

### E7. Error Handling
| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| GPU OOM (Out of Memory) | batch_size 자동 축소 (32→16→8), 실패 시 CPU fallback | HIGH |
| 모델 버전 불일치 | model_version + 콘텐츠 해시 검증 → 승인된 레지스트리의 서명 확인 + 명시적 인간 승인 후에만 교체 (자동 다운로드 금지, 버전 핀 고정) | HIGH |
| 미등록 한국어 금융 용어 | UNK 토큰 비율 > 10% 시 경고 로그, 사용자 사전 업데이트 권고 | LOW |
| LoRA 어댑터 로드 실패 | base model fallback (LoRA 없이 추론) + 알림 | HIGH |
| 토크나이저 인코딩 오류 | UTF-8 정규화 후 재시도, 실패 시 해당 텍스트 스킵 + 로그 | MEDIUM |
| 학습 데이터 레이블 불균형 | 클래스별 비율 체크 → 10% 미만 클래스 존재 시 오버샘플링 자동 적용 | MEDIUM |

### E8. Test Criteria
- **Unit**:
  - [ ] LoRA 어댑터 정상 부착 확인 (trainable params < 1% of total)
  - [ ] `predict()` 단건 추론 — 레이블/확률 형식 검증
  - [ ] `batch_predict()` — 입력 N건 = 출력 N건 일치
  - [ ] `merge_and_export()` — 병합 후 모델 로드 가능 확인
- **Integration**:
  - [ ] 파인튜닝 E2E: train → evaluate → merge → predict 파이프라인 정상 동작
  - [ ] `SentimentImpactCalculator` 연동 — KoFinBertResult → 임팩트 스코어 변환
  - [ ] Kafka `vamos.sentiment.impact` 토픽 발행 확인
- **Acceptance**:
  - [ ] 한국어 금융 감성 벤치마크 F1-score ≥ 0.85 (macro average)
  - [ ] 실제 한국 경제 뉴스 500건 대상 감성 분류 정확도 수동 검증
  - [ ] 추론 지연 < 50ms (P95) on NVIDIA A100

### E9. LOCK References
| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| transformers ≥4.36.0 | SPEC §14 | KoFinBERT 모델 로딩 및 추론 |
| peft ≥0.7.0 | SPEC §14 | LoRA 파인튜닝 프레임워크 |
| torch ≥2.1.0 | SPEC §14 | GPU 학습/추론 엔진 |
| VAMOS_EVENT schema | SPEC §4.2 | event_type="ko_sentiment" 이벤트 발행 |
| D-04 극복 | SPEC §17 | 한국어 금융 감성 분석 확장 |

---

## STEP7-I 보강: 한국어 금융 NLP 사전, 형태소 분석기 연동 (S7I-035)

> **보강 근거**: step7i_mapping.md PARTIAL — 한국어 금융 전문 용어 사전 구축 및 형태소 분석기(Mecab-ko) 연동 상세 누락
> **Priority**: MEDIUM

### E1. Input
- **데이터**: 한국어 금융 용어 사전 소스 (금융감독원 용어집, KRX 종목 사전, 증권사 리포트 용어), Mecab-ko 설정 파일, 사용자 정의 사전(user dictionary)
- **필수 필드**:
  - `term`: str — 금융 용어 (e.g., "공매도", "유상증자", "전환사채")
  - `pos_tag`: str — 품사 태그 (NNG: 일반명사, NNP: 고유명사)
  - `reading`: str — 발음 (Mecab 형식)
  - `cost`: int — 사전 내 우선순위 비용 (낮을수록 우선)
  - `category`: str — 분류 ("주식", "채권", "파생상품", "거시경제", "회계")
  - `synonyms`: list[str] — 동의어 목록
- **전처리**:
  - 금융 용어 수집 → 중복 제거 → Mecab 사용자 사전 형식 변환
  - 형태소 분석 결과 검증: 금융 복합어 정상 분리 여부 확인
  - 사전 버전 관리: Git 기반 변경 이력 추적

### E2. Algorithm
```python
# 의사코드 — 한국어 금융 NLP 사전 구축 및 형태소 분석기 연동
# 복사→구현 가능 수준

import csv
import subprocess
from dataclasses import dataclass, field
from konlpy.tag import Mecab

@dataclass
class FinancialTerm:
    """금융 용어 엔트리"""
    term: str               # "전환사채"
    pos_tag: str            # "NNG"
    reading: str            # "전환사채"
    cost: int               # -10 (낮을수록 우선)
    category: str           # "채권"
    synonyms: list[str] = field(default_factory=list)  # ["CB", "convertible bond"]

class KoreanFinancialDictionaryBuilder:
    """한국어 금융 NLP 사전 구축 파이프라인"""

    MECAB_USER_DIC_PATH = "/usr/local/lib/mecab/dic/user-finance.csv"
    MECAB_COMPILED_DIC_PATH = "/usr/local/lib/mecab/dic/user-finance.dic"

    def __init__(self):
        self.terms: list[FinancialTerm] = []
        self._category_index: dict[str, list[FinancialTerm]] = {}

    def collect_terms_from_source(self, source_type: str, source_path: str) -> int:
        """금융 용어 수집 — 소스별 파서"""
        parsers = {
            "fss_glossary": self._parse_fss_glossary,    # 금감원 용어집
            "krx_stock_list": self._parse_krx_stocks,    # KRX 종목명
            "analyst_reports": self._parse_analyst_terms, # 증권사 리포트
            "custom_csv": self._parse_custom_csv,         # CSV 직접 입력
        }
        parser = parsers.get(source_type)
        if not parser:
            raise ValueError(f"Unknown source type: {source_type}")
        new_terms = parser(source_path)
        self.terms.extend(new_terms)
        return len(new_terms)

    def _parse_fss_glossary(self, path: str) -> list[FinancialTerm]:
        """금융감독원 금융용어사전 파싱"""
        terms = []
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                terms.append(FinancialTerm(
                    term=row["용어"], pos_tag="NNG",
                    reading=row["용어"], cost=-10,
                    category=row.get("분류", "기타"),
                    synonyms=[s.strip() for s in row.get("영문명", "").split(",") if s.strip()],
                ))
        return terms

    def _parse_krx_stocks(self, path: str) -> list[FinancialTerm]:
        """KRX 상장 종목명 파싱 → 고유명사(NNP)로 등록"""
        terms = []
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                terms.append(FinancialTerm(
                    term=row["종목명"], pos_tag="NNP",
                    reading=row["종목명"], cost=-20,  # 종목명은 최우선
                    category="주식",
                    synonyms=[row.get("종목코드", "")],
                ))
        return terms

    def deduplicate(self) -> int:
        """중복 용어 제거 — 동일 term은 cost 낮은 것 우선"""
        seen: dict[str, FinancialTerm] = {}
        for t in self.terms:
            if t.term not in seen or t.cost < seen[t.term].cost:
                seen[t.term] = t
        removed = len(self.terms) - len(seen)
        self.terms = list(seen.values())
        self._rebuild_category_index()
        return removed

    def _rebuild_category_index(self):
        self._category_index.clear()
        for t in self.terms:
            self._category_index.setdefault(t.category, []).append(t)

    def build_mecab_user_dictionary(self) -> str:
        """Mecab 사용자 사전 CSV 생성 및 컴파일"""
        # 1. CSV 형식 출력 (Mecab-ko user dict format)
        # surface,left_id,right_id,cost,pos,semantic,has_jongseong,reading,type,start_pos,end_pos,expression
        with open(self.MECAB_USER_DIC_PATH, "w", encoding="utf-8") as f:
            for t in self.terms:
                has_jongseong = "T" if self._has_final_consonant(t.term[-1]) else "F"
                f.write(
                    f"{t.term},,,"
                    f"{t.cost},"
                    f"{t.pos_tag},*,"
                    f"{has_jongseong},"
                    f"{t.reading},*,*,*,*\n"
                )

        # 2. Mecab 사전 컴파일
        result = subprocess.run(
            ["/usr/local/libexec/mecab/mecab-dict-index",
             "-d", "/usr/local/lib/mecab/dic/mecab-ko-dic",
             "-u", self.MECAB_COMPILED_DIC_PATH,
             "-f", "utf-8", "-t", "utf-8",
             self.MECAB_USER_DIC_PATH],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            raise RuntimeError(f"Mecab dict compile failed: {result.stderr}")

        return self.MECAB_COMPILED_DIC_PATH

    @staticmethod
    def _has_final_consonant(char: str) -> bool:
        """한글 받침 존재 여부 확인"""
        code = ord(char) - 0xAC00
        if code < 0 or code > 11171:
            return False
        return (code % 28) != 0

class KoreanFinancialTokenizer:
    """한국어 금융 텍스트 토크나이저 — Mecab-ko + 금융 사전 연동"""

    def __init__(self, user_dic_path: str = None):
        dic_path = user_dic_path or KoreanFinancialDictionaryBuilder.MECAB_COMPILED_DIC_PATH
        self.mecab = Mecab(dicpath="/usr/local/lib/mecab/dic/mecab-ko-dic")
        self._financial_terms: set[str] = set()
        self._load_financial_terms(dic_path)

    def _load_financial_terms(self, dic_path: str):
        """컴파일된 사전에서 금융 용어 set 로딩"""
        csv_path = dic_path.replace(".dic", ".csv")
        with open(csv_path, encoding="utf-8") as f:
            for line in f:
                term = line.split(",")[0]
                self._financial_terms.add(term)

    def tokenize(self, text: str) -> list[dict]:
        """형태소 분석 + 금융 엔티티 태깅"""
        morphs = self.mecab.pos(text)
        tokens = []
        for surface, pos in morphs:
            is_financial = surface in self._financial_terms
            tokens.append({
                "surface": surface,
                "pos": pos,
                "is_financial_entity": is_financial,
                "entity_tag": "FIN" if is_financial else "O",
            })
        return tokens

    def extract_financial_entities(self, text: str) -> list[str]:
        """텍스트에서 금융 도메인 엔티티만 추출"""
        tokens = self.tokenize(text)
        return [t["surface"] for t in tokens if t["is_financial_entity"]]

    def validate_tokenization(self, text: str, expected_tokens: list[str]) -> dict:
        """토큰화 결과 검증 — 기대 토큰 목록과 비교"""
        actual = [t["surface"] for t in self.tokenize(text)]
        matched = sum(1 for e in expected_tokens if e in actual)
        return {
            "accuracy": matched / len(expected_tokens) if expected_tokens else 1.0,
            "expected": expected_tokens,
            "actual": actual,
            "missing": [e for e in expected_tokens if e not in actual],
        }
```

### E3. Output
- **스키마**:
```python
@dataclass
class TokenizedFinancialText:
    original_text: str                  # 입력 원문
    tokens: list[dict]                  # [{"surface": "공매도", "pos": "NNG", "is_financial_entity": True, "entity_tag": "FIN"}, ...]
    pos_tags: list[tuple[str, str]]     # [("공매도", "NNG"), ("잔고", "NNG"), ...]
    financial_entities: list[str]       # ["공매도", "코스피", "삼성전자"]
    token_count: int                    # 총 토큰 수
    financial_entity_ratio: float       # 금융 엔티티 비율 (0.0~1.0)
    dictionary_version: str             # "fin-dict-v2.3"
    tokenization_time_ms: float         # 처리 소요 시간
```
- **소비자**: `KoFinBertSentimentAnalyzer` (S7I-002, 전처리 입력), `NarrativeTracker` (키워드 추출), 금융 엔티티 기반 종목 매핑 모듈

### E4. Class/API Design
```python
class KoreanFinancialTokenizer:
    """한국어 금융 텍스트 토크나이저 — 공개 API"""

    def __init__(self, user_dic_path: str = None):
        """Mecab-ko 초기화 + 금융 사용자 사전 로딩"""
        ...

    def build_dictionary(self, sources: list[dict]) -> str:
        """금융 용어 사전 구축 파이프라인
        Args:
            sources: [{"type": "fss_glossary", "path": "/data/fss.csv"}, ...]
        Returns:
            컴파일된 사전 경로
        """
        builder = KoreanFinancialDictionaryBuilder()
        for src in sources:
            builder.collect_terms_from_source(src["type"], src["path"])
        builder.deduplicate()
        return builder.build_mecab_user_dictionary()

    def tokenize(self, text: str) -> TokenizedFinancialText:
        """형태소 분석 + 금융 엔티티 태깅 → TokenizedFinancialText 반환"""
        ...

    def extract_financial_entities(self, text: str) -> list[str]:
        """금융 도메인 엔티티만 추출"""
        ...

    def batch_tokenize(self, texts: list[str]) -> list[TokenizedFinancialText]:
        """배치 토큰화"""
        return [self.tokenize(t) for t in texts]

    def get_dictionary_stats(self) -> dict:
        """사전 통계 반환 — 총 용어 수, 카테고리별 분포"""
        ...
```

### E5. Tech Stack Dependency
| 라이브러리 | 버전 | SPEC §14 LOCK | 용도 |
|-----------|------|--------------|------|
| konlpy | ≥0.6.0 | ☑ | 한국어 형태소 분석 프레임워크 |
| mecab-ko | ≥0.996-ko-0.9.2 | ☑ | 형태소 분석 엔진 (C++ 기반) |
| mecab-ko-dic | ≥2.1.1 | ☑ | 기본 한국어 사전 |
| custom financial dictionary | v1.0+ | ☑ | 금융 도메인 사용자 사전 (자체 구축) |

### E6. Performance Requirements
| 지표 | 기준 | 측정 방법 |
|------|------|----------|
| 단건 토큰화 지연 | < 5ms / sentence | `time.perf_counter()` 1000문장 평균 |
| 사전 lookup 지연 | < 1ms | 금융 용어 존재 여부 확인 (set lookup) |
| 사전 구축 시간 | < 30분 (10만 용어) | 전체 파이프라인 (수집→중복제거→컴파일) |
| 사전 메모리 사용량 | < 200MB | 사전 로딩 후 프로세스 RSS 측정 |
| 배치 토큰화 처리량 | ≥ 5,000 sentences/sec | 10,000문장 배치 처리 평균 |

### E7. Error Handling
| 예외 시나리오 | 복구 로직 | 심각도 |
|-------------|----------|--------|
| 미등록 금융 용어 (OOV) | UNK 비율 모니터링 → 임계치(10%) 초과 시 사전 업데이트 알림 | MEDIUM |
| 인코딩 오류 (EUC-KR/UTF-8 혼재) | UTF-8 정규화 시도 → 실패 시 chardet 자동 감지 후 변환 | MEDIUM |
| 사전 버전 불일치 | 사전 해시 검증 → 불일치 시 재컴파일 트리거 | HIGH |
| Mecab 프로세스 크래시 | 자동 재시작 (최대 3회) → 실패 시 Python 기반 fallback 토크나이저 사용 | HIGH |
| 사전 컴파일 실패 | 오류 로그 출력 → 이전 버전 사전으로 롤백 | HIGH |
| 복합 금융 용어 분리 오류 | 검증 테스트 셋 자동 실행 → 정확도 하락 시 사전 항목 cost 조정 | LOW |

### E8. Test Criteria
- **Unit**:
  - [ ] `build_dictionary()` — 소스 파싱 후 Mecab CSV 형식 정합성 검증
  - [ ] `tokenize()` — "삼성전자 공매도 잔고 증가" → 금융 엔티티 정상 태깅
  - [ ] `extract_financial_entities()` — 금융 용어만 필터링 확인
  - [ ] `deduplicate()` — 중복 용어 제거 후 cost 기준 우선순위 정상 동작
- **Integration**:
  - [ ] Mecab 사용자 사전 컴파일 → 로딩 → 토큰화 E2E 파이프라인
  - [ ] `KoFinBertSentimentAnalyzer`(S7I-002) 전처리 입력으로 연동
  - [ ] 사전 업데이트 후 기존 토큰화 결과 회귀 테스트
- **Acceptance**:
  - [ ] 한국어 금융 텍스트 벤치마크 토큰화 정확도 ≥ 95%
  - [ ] 금감원 공시 100건 대상 금융 엔티티 추출 재현율(recall) ≥ 90%
  - [ ] 토큰화 지연 < 5ms (P95) per sentence

### E9. LOCK References
| LOCK 값 | 출처 | 적용 방식 |
|---------|------|----------|
| konlpy ≥0.6.0 | SPEC §14 | 한국어 NLP 프레임워크 |
| mecab-ko ≥0.996 | SPEC §14 | 형태소 분석 엔진 |
| mecab-ko-dic ≥2.1.1 | SPEC §14 | 기본 한국어 사전 |
| VAMOS_EVENT schema | SPEC §4.2 | 토큰화 결과 이벤트 연동 |
| D-04 극복 | SPEC §17 | 한국어 금융 NLP 기반 감성 분석 지원 |

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
