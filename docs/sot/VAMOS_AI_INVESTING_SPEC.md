# VAMOS AI INVESTING 통합 명세서

> **문서 버전**: v2.0
> **작성일**: 2026-02-23
> **원본 소스**: `AI INVESTING` 디렉토리 전체 (16+ 파일)
> **범위**: 24개 섹션 + 부록 (ZERO 누락 원칙)

> **V1 LOCK 기술스택 관계**: 본 문서의 투자 분석 시스템은 VAMOS V1 전체 LOCK 기술스택(Python 3.11+, LangGraph, Pydantic v2, Tauri 2.0+React 18, BGE-M3, Chroma 등)을 기반으로 구축됩니다. 비용 상한은 D2.0-07 정본(V1: $30/월, V2: $70/월, V3: $200/월)을 따르며, 본 문서 §14 "14-Item Locked 기술 스택"은 AI Investing 도메인 전용 스택으로 VAMOS 전체 LOCK과 병행 적용됩니다.

---

## 목차

1. [시스템 개요](#1-시스템-개요)
2. [7-Layer 데이터 아키텍처](#2-7-layer-데이터-아키텍처)
3. [83개 데이터 소스](#3-83개-데이터-소스)
4. [데이터 스키마](#4-데이터-스키마)
5. [DQ Validation](#5-dq-validation)
6. [백테스팅 엔진 및 51% Gate](#6-백테스팅-엔진-및-51-gate)
7. [투자 전략 -- 기술적 분석 (40개)](#7-투자-전략--기술적-분석)
8. [투자 전략 -- 퀀트/팩터/옵션/ML (56개)](#8-투자-전략--퀀트팩터옵션ml)
9. [RSI_BB 전략 구현 상세](#9-rsi_bb-전략-구현-상세)
10. [법적 제약 시스템](#10-법적-제약-시스템)
11. [Grafana 모니터링](#11-grafana-모니터링)
12. [Airflow DAG 스케줄링](#12-airflow-dag-스케줄링)
13. [실시간 Stream Gateway](#13-실시간-stream-gateway)
14. [14-Item Locked 기술 스택](#14-14-item-locked-기술-스택)
15. [ML/AI 스택](#15-mlai-스택)
16. [수학 공식 전수 검증](#16-수학-공식-전수-검증)
17. [15개 결함 및 극복 방안](#17-15개-결함-및-극복-방안)
18. [4-Phase 로드맵](#18-4-phase-로드맵)
19. [STEP 7-I 참고 사이트 (35개)](#19-step-7-i-참고-사이트)
20. [VAMOS Core 통합](#20-vamos-core-통합)
21. [Scraper Manager](#21-scraper-manager)
22. [Non-goal 강제 규칙](#22-non-goal-강제-규칙)
23. [contracts.py 검토 보고서 (26건)](#23-contractspy-검토-보고서)
24. [Z-Session 통합](#24-z-session-통합)
- [부록 A: 파일 구조](#부록-a-파일-구조)
- [부록 B: 현황 요약](#부록-b-현황-요약)

---

## 1. 시스템 개요

VAMOS AI는 **자율 투자 관리 시스템**(Autonomous Investment Management System)입니다.

### 1.1 핵심 목표

| 항목 | 내용 |
|:--|:--|
| 핵심 지표 | 승률 >= 51%, Sharpe Ratio >= 1.0 |
| 대상 자산 | 미국 주식(SPY, QQQ), 한국 주식, 암호화폐(BTC-USD) |
| 운영 모드 | Paper Trading -> 실전 거래 |
| 기술 스택 | Python 3.12, Airflow, Kafka, TimescaleDB, ChromaDB, Grafana |

### 1.2 Multi-Agent 워크플로우

| AI | 역할 | STEP |
|:--|:--|:--|
| **Perplexity** | 데이터 소스 발굴, 리서치 | STEP 1.1 |
| **Gemini** | 분류, 기술 분석, PM | STEP 2, 2.5, 6 |
| **ChatGPT** | 전략 로직, 코드 작성 | STEP 3, 4 |
| **Claude** | 검증, 감사, Gate 판정 | STEP 4.5, 5 |
| **VS Code Copilot** | 코드 구현 보조 | STEP 4 |

### 1.3 4 PHASE / 10 STEP 구조

```
PHASE 1 (기초): STEP 1.1~1.6 (소스 발굴 -> 전략 추출 -> 51% Gate -> KB 통합)
PHASE 2 (골조): STEP 2~3 (기술 스택 식별 -> 채택 결정)
PHASE 3 (검수): STEP 4~5 (PoC -> 감사)
PHASE 4 (준공): STEP 6 (최종 문서화, Backport)
```

### 1.4 4-Layer 아키텍처

```
[BASE LAYER]   절대 변경 불가: 정체성, Non-goal, 법/윤리, 비용 상한, Self-evo 제한
[PLAN LAYER]   도메인 구조, 멀티모달, 메모리, 위험 정책, LLM 라우팅
[DESIGN LAYER] ORANGE CORE / BLUE NODE / INFRA 상세 설계
[IMPLEMENTATION -> OPERATIONS]
```

### 1.5 ORANGE CORE + BLUE NODE

```
Front Mini LLM -> ORANGE CORE (정책/비용/Self-check/라우팅)
  -> BLUE NODE: Dev(P0), Research(P0), Productivity(P0),
                Content(P1), Data&Quant(P1), Trading(P2 승인필수)
  -> OTHER BRAINS (RAG, 크롤러, 코드 실행기)
  -> Main LLM (최종 출력)
```

---

## 2. 7-Layer 데이터 아키텍처

```
Layer 1: 데이터 수집 (Primary API + Scraper + Knowledge Base)
Layer 2: 데이터 처리 (Contract Validator -> Transform -> Quarantine Zone)
Layer 3: 저장 (TimescaleDB + ChromaDB + S3/MinIO)
Layer 4: 전략 엔진 (전략 실행 -> 법적 검증 -> 신호 생성)
Layer 5: 실행 (주문 생성 -> 거래 실행 -> 결과 기록)
Layer 6: 모니터링 (Grafana Dashboard)
Layer 7: 자동화 오케스트레이션 (Airflow + Kafka + Scraper Manager)
```

| Component | 역할 | 파일 |
|:--|:--|:--|
| 1. contracts.py | 데이터 형태 검증 (관문) | `contracts.py` |
| 2. Pipeline Targets | 수집 대상 메타데이터 | `sources.yaml` |
| 3. Airflow DAG | 정기 수집 자동화 | `vamos_dag_factory.py` |
| 4. Stream Gateway | 실시간 데이터 수신 | `vamos_stream_gateway.py` |
| 5. Scraper Manager | 웹 스크래핑 (자동 복구) | `scraper_drift_handler.py` |
| 6. Knowledge Base | 데이터 저장소 | TimescaleDB + ChromaDB |
| 7. Monitoring | Grafana 대시보드 | Grafana >= 10.0 |

---

## 3. 83개 데이터 소스

### 3.1 P0 (Critical) -- 16개

| # | 소스 | 데이터 유형 |
|:--|:--|:--|
| 1 | FRED (St. Louis Fed) | 미국 거시경제 |
| 2 | ECOS (Bank of Korea) | 한국 거시경제 |
| 3 | KRX Data System | 한국 주식 |
| 4 | CME Market Data | 선물/옵션 |
| 5 | Cboe VIX Historical | 변동성 지수 |
| 6 | Nasdaq Data Link | 대체 데이터 |
| 7 | Dune Analytics | 블록체인 SQL |
| 8 | Etherscan | 이더리움 탐색 |
| 9 | DeFiLlama | DeFi TVL |
| 10 | Glassnode Studio | 온체인 메트릭 |
| 11 | SEC EDGAR | 미국 공시 |
| 12 | DART (OpenAPI) | 한국 공시 |
| 13 | Stocktwits | 소셜 감성 |
| 14 | ApeWisdom | Reddit 감성 |
| 15 | iShares Product List | ETF 구성 |
| 16 | AWS Data Exchange | 클라우드 데이터 |

### 3.2 P1 (High) -- 9개

Federal Register, arXiv (q-fin), FCA Warning List, PR Newswire, Business Wire, EIA (Energy Stats), NOAA Climate Data, SEC Form D Search, Token Terminal

### 3.3 TIER-0/TIER-1 (Scraper) -- 17개

> **[PART1 AI-01]** 스크래퍼 우선순위 명칭을 S0/S1에서 TIER-0/TIER-1로 리네이밍. 메인 상태머신(S0_RECEIVED/S1_INTENT_PARSED)과의 명칭 충돌 방지.

**TIER-0 (Critical)**: Goldman Sachs Insights, TradingView Ideas, SwaggyStocks, OptionStrat, Earnings Whispers, BamSEC, US Treasury Rates, OpenInsider, FINRA Short Interest

**TIER-1 (High)**: FINRA OTC Transparency, Investing.com Earnings, Asian Bond Online, World Gov Bonds, ShortSqueeze, ETF.com Screener, Walter Bloomberg (X), LME Market Data

### 3.4 Knowledge Base (KB) -- 41개+

IRS 세금 가이드, 거래소 규정집, IMF Data Portal, Eurostat 등 (Scope 1~23의 나머지 소스)

---

## 4. 데이터 스키마

### 4.1 VAMOS_OHLCV_PLUS

```json
{
  "entity_id": "SPY",
  "timestamp_utc": "2026-02-03T00:00:00Z",
  "timezone": "America/New_York",
  "data_type": "candle",
  "sequence_id": 0,
  "values": {
    "open": "485.20", "high": "487.50", "low": "484.10",
    "close": "486.80", "volume": "52341000",
    "vwap": "485.90", "open_interest": null, "economic_value": null
  },
  "metadata": {
    "source": "yfinance", "confidence": 0.95,
    "original_id": "SPY", "frequency": "1d", "is_simulated": false
  }
}
```

**data_type별 조건부 required**: candle(open,high,low,close,volume), tick(close,volume), economic(economic_value), onchain(close,volume)

### 4.2 VAMOS_EVENT

```json
{
  "event_id": "evt_abc123",
  "timestamp_utc": "2026-02-03T14:30:00Z",
  "event_type": "news",
  "sentiment_score": 0.65,
  "impact_level": 3,
  "entities": ["AAPL", "MSFT"],
  "content": {
    "headline": "Apple announces new product launch",
    "summary": "Apple Inc. revealed plans for...",
    "url": "https://example.com/news/..."
  }
}
```

- `event_type`: Literal 6개 (filing, news, sentiment, corporate_action, reference_update, kb_derived)
- `sentiment_score`: -1.0 ~ 1.0 / `impact_level`: 1 ~ 5

### 4.3 저장소 구조

**TimescaleDB**:
```sql
CREATE TABLE ohlcv_plus (
    entity_id TEXT NOT NULL, timestamp_utc TIMESTAMPTZ NOT NULL,
    data_type TEXT NOT NULL, open NUMERIC, high NUMERIC, low NUMERIC,
    close NUMERIC, volume NUMERIC, source TEXT, confidence FLOAT,
    PRIMARY KEY (entity_id, timestamp_utc)
);
SELECT create_hypertable('ohlcv_plus', 'timestamp_utc');
```

**ChromaDB**: 문서 임베딩 + RAG 검색 (1024차원 벡터, LOCK: BGE-M3)

**S3/MinIO 버킷**: raw/ (원본), quarantine/ (격리), backtest/ (결과), logs/ (로그)

---

## 5. DQ Validation

| 검증 항목 | 실패 시 동작 |
|:--|:--|
| 타임스탬프 ISO8601 UTC(Z) | HARD_FAIL |
| decimal-safe 문자열 | HARD_FAIL |
| 필수 필드 누락 | HARD_FAIL |
| 타입 불일치 | SOFT_FAIL (격리) |
| 중복 데이터 | SOFT_FAIL (중복 제거) |

**Quarantine 흐름**: API 오류 -> 자동 재시도 3회 -> 실패 시 S3 격리 -> 수동 검토

---

## 6. 백테스팅 엔진 및 51% Gate

### 6.1 51% Gate 통과 조건

승률 >= 51%, Sharpe >= 1.0, Decay < 30%, 최소 거래 >= 30건, Train 70% / Test 30%

### 6.2 엔진 설정

```python
EngineConfig(fee_rate=0.0, slippage_rate=0.0,
             risk_free_rate_annualized=0.05, frequency="1d")
```

대상: SPY, QQQ, BTC-USD (2018-01-01~). Sharpe: ddof=1, rf: compound 변환.

### 6.3 현재 결과

RSI_BB -> 전 심볼 INSUFFICIENT_SAMPLE. 파라미터 조정 또는 전략 추가로 Gate 통과 가능.

---

## 7. 투자 전략 -- 기술적 분석 (40개)

총 40개: 기술적 분석 25개 + 차트 패턴 15개

### 7.1 추세 추종 (7개)

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/technical/trend_following.md`

| # | 전략명 | 설명 | 적합 시장 |
|:--|:--|:--|:--|
| 1 | **MACD Crossover** | MACD/시그널선 교차 매매 | 추세장 |
| 2 | **MA Crossover** | 단기/장기 MA 교차 매매 | 추세장 |
| 3 | **Ichimoku Cloud** | 구름 돌파/이탈 매매 | 추세장 |
| 4 | **ADX** | ADX > 25 추세 확인 진입 | 추세장 |
| 5 | **Parabolic SAR** | SAR 점 전환 매매 | 추세장 |
| 6 | **Donchian Channel** | N일 최고/최저가 돌파 | 추세장 |
| 7 | **Supertrend** | ATR 기반 동적 추세선 | 추세장 |

### 7.2 모멘텀/오실레이터 (5개): Stochastic, Williams %R, CCI, MFI, Elder Ray

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/technical/momentum_oscillator.md`

### 7.3 변동성 기반 (6개): Fibonacci, Breakout, Support Bounce, ATR Breakout, Keltner Channel, Squeeze Momentum

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/technical/volatility.md`

### 7.4 거래량 기반 (3개): Volume Profile, VWAP, OBV

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/technical/volume.md`

### 7.5 복합 (4개): Pivot Points, Renko, Heikin-Ashi, Triple Screen

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/technical/composite.md`

### 7.6 차트 패턴 -- 반전 (7개): Head & Shoulders, Inverse H&S, Double Top/Bottom, Triple Top/Bottom, Rising/Falling Wedge

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/technical/chart_pattern_reversal.md`

### 7.7 차트 패턴 -- 지속 (8개): Cup & Handle, Ascending/Descending/Symmetrical Triangle, Bull/Bear Flag, Pennant, Rectangle, Harmonic Patterns

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/technical/chart_pattern_continuation.md`

### 7.8 Harmonic Patterns

> **MIGRATED**: 패턴 상세는 `sot 2/Ai-investing-detail/20_strategy-detail/technical/harmonic.md` 참조.
> 아래는 이전 전 원본의 요약 색인입니다.

5개 패턴: Gartley (XA 0.618, 70%), Bat (XA 0.382-0.5, 75%), Butterfly (XA 0.786, 65%), Crab (XA 0.382-0.618, 60%), Shark (XA 0.446-0.618, 65%)

### 7.9 시장 상황별 전략 선택

> **MIGRATED**: 전략 선택 상세는 `sot 2/Ai-investing-detail/01_realtime-adaptive/strategy_selection.md` 참조.
> 아래는 이전 전 원본의 요약 색인입니다.

4유형 정적 테이블: 강한 상승(MACD, MA Crossover), 강한 하락(SAR, Ichimoku), 횡보(RSI_BB, Stochastic), 변동성 급증(ATR Breakout, Squeeze)

---

## 8. 투자 전략 -- 퀀트/팩터/옵션/ML (56개)

### 8.1 퀀트/통계 (12개): Mean Reversion, Z-Score, Pairs Trading, Cointegration, Momentum, Cross-Sectional/Time-Series/Factor Momentum, Statistical/Triangular Arbitrage, Kalman Filter, PCA Trading

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/quant/statistical.md`

### 8.2 팩터 투자 (8개): Value, Momentum, Quality, Size, Low Volatility, Dividend Yield, Carry, Multi-Factor

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/quant/factor.md`

### 8.3 옵션 (10개): Covered Call, Cash-Secured Put, Long Straddle/Strangle, Iron Condor/Butterfly, Bull Call/Bear Put Spread, Calendar Spread, MAX_PAIN

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/quant/options.md`

### 8.4 이벤트 기반 (6개): Earnings Momentum, Merger Arbitrage, Spin-off, Index Rebalancing, Dividend Capture, FOMC

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/quant/event_driven.md`

### 8.5 ML/AI (8개): LSTM, RL (DQN/PPO), Random Forest, XGBoost/LightGBM, FinBERT Sentiment, CNN Image, Transformer, Ensemble

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/quant/ml_ai.md`

### 8.6 암호화폐 (6개): Grid Trading, DCA, Funding Arbitrage, DeFi Yield, Whale Tracking, Exchange Arbitrage

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/quant/crypto.md`

### 8.7 포트폴리오/리스크 (6개): Kelly Criterion, Risk Parity, Mean-Variance, Black-Litterman, ATR Position Sizing, Trailing Stop

> Detail: `sot 2/Ai-investing-detail/20_strategy-detail/quant/portfolio_risk.md`

### 8.8 전략 총계: 96개 (RSI_BB 제외)

---

## 9. RSI_BB 전략 구현 상세

> **MIGRATED**: 구현 상세는 `sot 2/Ai-investing-detail/20_strategy-detail/technical/rsi_bb.md` 참조.
> 아래는 이전 전 원본의 요약 색인입니다.

유일한 구현 완료 전략. `strategies.py` RSIBBAdapter. 진입: RSI < oversold AND close < BB_lower. 청산: RSI > (100-oversold) OR close > BB_upper. 파라미터 27조합, Wilder RSI (SMA seed + EMA), BB ddof=0 2.0σ.

---

## 10. 법적 제약 시스템

### 10.1 규칙

| 규칙 | 국가 | 내용 | 위반 시 |
|:--|:--|:--|:--|
| Wash Sale Rule | 미국 | 손실 매도 후 30일 내 재매수 금지 | 주문 차단 |
| PDT Rule | 미국 | $25K 미만 5일 3회 제한 | 주문 차단 |
| Uptick Rule | 한국 | 공매도 직전가 이상만 | 주문 차단 |

### 10.2 Circuit Breaker

일일 손실 -3% 중단, VIX>40 매수 중단, 포지션 -10% 강제 청산, 현금 20% 최소, 단일종목 10% 한도

---

## 11. Grafana 모니터링

패널: Pipeline Health, Drift Alerts, Stream Latency, Quarantine Queue, Data Freshness, Active Strategy Count, Portfolio P&L, Win Rate

알림: 수집 실패 3회 -> Slack, Quarantine 10건 -> 긴급, 승률 49% 이하 -> 검토, VIX>40 -> CB 가동

---

## 12. Airflow DAG 스케줄링

```
06:00 fetch_market_data -> 06:05 validate -> 06:10 transform -> 06:15 store
-> 06:20 strategy -> 06:25 legal_check -> 06:30 signals -> 06:35 orders
```

일일 배치(06:00 UTC), 실시간 스트림(장중), 웹 스크래핑(소스별), 문서 갱신(이벤트)

---

## 13. 실시간 Stream Gateway

### 13.1 아키텍처

```
WebSocket -> Kafka Topic -> Consumer -> TimescaleDB
```

### 13.2 지원 소스

| 소스 | 데이터 유형 | 상태 |
|:--|:--|:--|
| Etherscan | 블록 이벤트 (온체인) | 구현 완료 |
| 거래소 실시간 호가 | 주가/체결 | 향후 확장 |

### 13.3 파일

`vamos_stream_gateway.py` (~90줄)

### 13.4 실시간 이벤트 처리 흐름

```
[Etherscan WebSocket] 대규모 전송 감지
  -> [Stream Gateway] Kafka로 전달
  -> [Consumer] VAMOS_EVENT 변환 (event_type: "onchain", impact_level: 4)
  -> [Strategy Engine] 이벤트 기반 전략 평가
  -> (현재 이벤트 기반 전략 미구현 -- DEFER)
```

---

## 14. 14-Item Locked 기술 스택

프로젝트 전체에서 **변경 금지** (LOCKED).

| # | Component | Version | 용도 |
|:--|:--|:--|:--|
| 1 | Apache Airflow | >= 2.8.0 | DAG 스케줄링 |
| 2 | asyncio | Python 표준 | 비동기 처리 |
| 3 | Kafka | >= 3.6 | 메시지 큐/스트림 |
| 4 | TimescaleDB | >= 2.13 | 시계열 DB |
| 5 | ChromaDB | >= 0.4 | 벡터 DB / RAG |
| 6 | PostgreSQL | >= 16 | 메타데이터 DB |
| 7 | S3 / MinIO | latest | 오브젝트 스토리지 |
| 8 | Grafana | >= 10.0 | 모니터링 대시보드 |
| 9 | Pydantic v2 | >= 2.5 | 데이터 검증 |
| 10 | Decimal-safe | -- | 가격 문자열 보장 |
| 11 | Schema Drift Detection | -- | 웹 구조 변경 감지 |
| 12 | Quarantine Zone | -- | 불량 데이터 격리 |
| 13 | Bitnami Helm Chart | -- | Kafka 배포 |
| 14 | Docker Compose | -- | 로컬 배포 |

### 14.1 STEP 3 주요 결정

| 결정 ID | 내용 |
|:--|:--|
| D-S3-01 | asyncio LOCK (Python 표준 비동기) |
| D-S3-02 | yfinance 조건부 ADOPT (V1 무료, 장애 대비책 마련) |
| D-S3-03 | LLM Parser 개념 ADOPT (구체 모델은 후결정) |
| D-S3-04 | Redpanda DROP (Kafka와 중복) |
| D-S3-05 | VectorBT 조건부 ADOPT (전략 3개 이상 시 도입) |

### 14.2 STEP 5 감사 결정

| 결정 ID | 문제 | 해결 |
|:--|:--|:--|
| D-S5-01 | Python 3.11 vs 3.12 | 3.12 확정 |
| D-S5-02 | yfinance 장애 대응 | Quarantine 트리거 정의 |
| D-S5-03 | VectorBT 전환 추적 | Grafana 메트릭 추가 |
| D-S5-04 | API 키 저장 | env(dev) / K8s Secrets(prod) |
| D-S5-05 | 미국 주식 fallback | V1 한계 명시적 허용 |
| D-S5-06 | PoC OHLCV 타입 불일치 | 프로덕션 str+Decimal 의무화 |

---

## 15. ML/AI 스택

| 카테고리 | 기술 | 용도 |
|:--|:--|:--|
| 딥러닝 | TensorFlow / PyTorch | LSTM, Transformer 모델 |
| NLP | Hugging Face Transformers | FinBERT (ProsusAI/finbert) |
| ML | scikit-learn | 분류/회귀 기본 |
| 부스팅 | XGBoost, LightGBM | 그래디언트 부스팅 |
| 강화학습 | Stable-Baselines3 | PPO, DQN 에이전트 |
| Explainability | SHAP, LIME | AI 결정 해석 |

### 15.1 데이터 소스 우선순위 (ML용)

| 소스 | 데이터 유형 | 우선순위 |
|:--|:--|:--:|
| yfinance | 미국 주식 OHLCV | 1 |
| Alpha Vantage | 글로벌 주식, 환율 | 2 |
| Polygon.io | 실시간 + 히스토리 | 3 |
| KRX Open API | 한국 주식 | 4 |
| FRED | 거시경제 지표 | 5 |
| ccxt | 암호화폐 | 6 |
| finnhub | 뉴스, 감성 | 7 |

---

## 16. 수학 공식 전수 검증

4차 크로스체크 완료. **전건 정확**.

### 16.1 Sharpe Ratio (연율화)

```
Sharpe = (mean_r - rf_per_period) / std(ddof=1) * sqrt(N)
```

- ddof=1: 표본 표준편차 사용 (F-01 BLOCKER 해소)
- N (annualization): 1d=sqrt(252), 1h=sqrt(1638), 1m=sqrt(98280)

### 16.2 Wilder RSI

```
SMA seed(period) -> EMA smoothing
RSI = 100 - 100/(1 + RS), RS = avg_gain / avg_loss
```

Wilder 원전 일치.

### 16.3 Bollinger Bands

```
mid = SMA(close, period)
upper/lower = mid +/- 2.0 * std(ddof=0)
```

John Bollinger 원전 일치. ddof=0 (모집단 표준편차).

### 16.4 Decay Rate

```
decay = max(0, (sharpe_train - sharpe_test) / abs(sharpe_train))
```

sharpe_train=0이면 FAIL (decay 미정의).

### 16.5 연율화 팩터

| 빈도 | 값 |
|:--|:--|
| 1d | sqrt(252) |
| 1h | sqrt(252 * 6.5) = sqrt(1638) |
| 1m | sqrt(252 * 390) = sqrt(98280) |

### 16.6 무위험 수익률 변환

```
rf_per_period = (1 + rf_annual)^(1/ppy) - 1
```

복리 변환 정석.

---

## 17. 15개 결함 및 극복 방안

> **MIGRATED**: 15개 결함의 상세 극복 방안은 sot 2/Ai-investing-detail/ 해당 관점 폴더로 분배됨.
> 아래 목록은 인덱스로 보존합니다.
>
> | 결함# | 분배 대상 |
> |-------|----------|
> | D-01 | 20_strategy-detail/ (Phase 2 L3 작업) |
> | D-02 | 18_data-quality/data_source_quality.md |
> | D-03 | 01_realtime-adaptive/ (전체) |
> | D-04 | 02_behavioral-finance/news_sentiment.md |
> | D-05 | 15_portfolio-advanced/portfolio_optimization.md |
> | D-06 | 05_backtest-integrity/data_quality_preprocess.md |
> | D-07 | 13_asset-class-deep/derivatives_strategies.md |
> | D-08 | 03_macro-sector-stock/macro_regime.md |
> | D-09 | 08_cross-asset/ + 13_asset-class-deep/ |
> | D-10 | *SPEC §23 관할 (sot 2/ 범위 외)* |
> | D-11 | *SPEC 관할 (sot 2/ 범위 외)* |
> | D-12 | 06_execution-optimization/slippage_model.md + 11_tca/cost_components.md |
> | D-13 | 15_portfolio-advanced/hedge_tail_risk.md + 19_liquidity-cash/emergency_liquidity.md |
> | D-14 | 17_explainability/decision_explanation.md |
> | D-15 | 09_model-governance/mlops.md |

### 17.1 결함 목록

| # | 카테고리 | 심각도 | 상세 |
|:--|:--|:--:|:--|
| D-01 | 전략 다양성 부족 | High | RSI_BB만 구현, MAX_PAIN/MACRO_ROTATION DEFER |
| D-02 | API 단일 의존성 | High | yfinance 장애 시 전체 중단 |
| D-03 | 실시간 처리 미흡 | Medium | 일일 배치 중심 |
| D-04 | 감성 분석 부재 | Medium | 뉴스/SNS 미반영 |
| D-05 | 포트폴리오 관리 없음 | High | 자산 배분 로직 부재 |
| D-06 | 백테스팅 샘플 부족 | Medium | INSUFFICIENT_SAMPLE |
| D-07 | 옵션/파생 데이터 미확보 | Medium | MAX_PAIN 불가 |
| D-08 | 거시경제 데이터 미연동 | Medium | MACRO_ROTATION 불가 |
| D-09 | 다중 자산 미지원 | Medium | 주식만, 암호화폐/FX 미지원 |
| D-10 | contracts.py 불일치 | High | JSON Schema 12건 불일치 (P0) |
| D-11 | 환경 미구축 | High | Docker, API 키 미확보 |
| D-12 | 슬리피지/수수료 실측 부족 | Medium | 백테스트 vs 실전 괴리 |
| D-13 | Black Swan 대응 없음 | High | 급락/Flash Crash 방어 부재 |
| D-14 | Model Explainability 부재 | Medium | AI 결정 근거 불투명 |
| D-15 | A/B 테스트 체계 없음 | Low | 전략 변경 효과 측정 어려움 |

### 17.2 주요 극복 방안

**D-02 API Fallback Chain:**
```python
data_sources = [
    {"name": "yfinance",       "priority": 1, "timeout": 10},
    {"name": "Alpha Vantage",  "priority": 2, "timeout": 15},
    {"name": "Polygon.io",     "priority": 3, "timeout": 15},
    {"name": "KRX Open API",   "priority": 4, "timeout": 20}
]
```

**D-05 Kelly Criterion:**
```python
def kelly_fraction(win_rate, win_loss_ratio):
    b, p, q = win_loss_ratio, win_rate, 1 - win_rate
    full_kelly = (b * p - q) / b
    half_kelly = full_kelly / 2
    return max(0, min(half_kelly, 0.25))  # Half-Kelly, 25% cap
```

**D-05 Risk Parity:**
```python
def risk_parity_weights(returns):
    inverse_vol = 1 / returns.std()
    return inverse_vol / inverse_vol.sum()
```

**D-13 Circuit Breaker:**
```python
class CircuitBreaker:
    RULES = {
        "daily_loss_limit": -0.03,
        "position_stop_loss": -0.10,
        "vix_threshold": 40,
        "min_cash_ratio": 0.20,
        "max_position_size": 0.10,
    }
```

### 17.3 극복 일정 요약

| 단점 | 방안 | 기간 |
|:--|:--|:--|
| D-10 contracts.py | 12건 정렬 | 즉시 |
| D-11 환경 | Docker Compose | 1주 |
| D-01 전략 | MACD, MA 추가 | 2주 |
| D-02 API | Fallback Chain | 2주 |
| D-06 샘플 | 데이터 3년->5년 | 1주 |
| D-04 감성 | FinBERT 통합 | 3주 |
| D-13 Black Swan | Circuit Breaker | 1주 |
| D-14 Explainability | SHAP/LIME | 3주 |

---

## 18. 4-Phase 로드맵

> **HISTORICAL**: 이 로드맵은 초기 계획 기록입니다. 현행 Phase 일정은
> PART2 §6.8이 정본입니다. 아래 내용은 역사적 참조용으로만 보존합니다.

### 18.1 전체 타임라인

```
Phase 1 (1-2주)  -> P0 Blocker 해소, PoC 검증
Phase 2 (2-4주)  -> 전략 다양화, 리스크 관리
Phase 3 (1-2개월) -> ML/AI 도입, 실시간 처리
Phase 4 (3-6개월) -> VAMOS CORE 통합, 실전 운영
```

### 18.2 Phase 1: 즉시 시작 (1-2주)

| 작업 | 산출물 |
|:--|:--|
| contracts.py 12건 정렬 | 정렬된 contracts.py |
| Docker Compose 작성 | docker-compose.yml |
| API 키 확보 | .env 파일 |
| PoC 5건 실행 | PoC 검증 보고서 |
| RSI_BB 파라미터 튜닝 | 51% Gate 시도 |

**완료 조건**: contracts.py 100% 일치, Docker DAG 실행, PoC PASS

### 18.3 Phase 2: 단기 (2-4주)

| 작업 | 산출물 |
|:--|:--|
| MACD/MA Crossover 전략 | strategies.py |
| Kelly Criterion | position_sizing.py |
| API Fallback Chain | data_fetcher.py |
| ATR Trailing Stop | risk_manager.py |
| Mean-Variance Optimization | portfolio_optimizer.py |

**완료 조건**: 전략 3개 51% Gate PASS, Kelly 작동, Fallback 3소스+

### 18.4 Phase 3: 중기 (1-2개월)

| 작업 | 산출물 | 기간 |
|:--|:--|:--|
| FinBERT 감성 분석 | sentiment_analyzer.py | 2주 |
| Circuit Breaker | circuit_breaker.py | 1주 |
| Pairs Trading | strategies.py | 2주 |
| WebSocket 실시간 | realtime_engine.py | 2주 |
| SHAP/LIME | explainer.py | 1주 |
| Paper Trading 운영 | 보고서 | 2주 |

**완료 조건**: FinBERT 반영, VIX>40 자동 중단, Paper 2주 수익>0

### 18.5 Phase 4: 장기 (3-6개월)

| 작업 | 산출물 | 기간 |
|:--|:--|:--|
| VAMOS CORE I-6/I-7/I-8/I-9 | 연동 코드 | 6주 |
| LSTM 가격 예측 | lstm_predictor.py | 4주 |
| RL 실험 | rl_agent.py | 4주 |
| 옵션 데이터 + MAX_PAIN | options_data.py | 4주 |
| No-code Builder View | frontend/ | 6주 |
| 실전 거래 소액 시작 | 실전 보고서 | 지속 |

**완료 조건**: CORE 4기능 연동, LSTM 방향>55%, 실전 1개월 수익>0

### 18.6 비용 계획

| 항목 | V1 (상한 ~$30/월, 실비용 ~$0) | V2 (~$70/월) | V3 (~$200/월) |
|:--|:--|:--|:--|
| 데이터 | yfinance 무료 | Alpha Vantage $29 | Polygon Pro $79 |
| 인프라 | Docker Compose | AWS t3.medium $30 | AWS t3.large $60 |
| LLM | 미사용 | GPT-4o mini $20 | GPT-4o $50 |
> **[AI-04]** 위 비용은 AI Investing 도메인 전용 서브예산(데이터+인프라+LLM)이며, VAMOS 전체 LOCK 상한(V1 ₩40,000/V2 $70/V3 $200)과는 별도 산정. 전체 상한 내 배분은 D2.0-07 §4.2 참조.

---

## 19. STEP 7-I 참고 사이트 (35개)

AI 투자 시장 규모: **2024년 $23.48B -> 2034년 $75.5B** (CAGR 20.7%).

### 19.1 주식/ETF 중심 플랫폼 (15개)

| # | 플랫폼 | 주요 기능 | VAMOS AI 적용 포인트 | 비용 |
|:--|:--|:--|:--|:--|
| 1 | **QuantConnect** | 오픈소스 LEAN 엔진, Python/C# | 백테스팅 아키텍처 참고 | $0-60/월 |
| 2 | **Trade Ideas** | Holly AI, 실시간 스캔 | Self-evo 시뮬레이션 방식 | $167/월 |
| 3 | **Alpaca** | 수수료 무료 API | REST API 설계 참고 | 무료 |
| 4 | **Composer** | No-code 전략 빌더 | UI/UX Builder View | $50/월 |
| 5 | **TradingView** | 최고의 차트, 소셜 네트워크 | 차트 시각화 참고 | $12-60/월 |
| 6 | **Kavout** | Kai Score AI 점수화 | 종목 스코어링 시스템 | 문의 |
| 7 | **LevelFields** | 이벤트 기반 AI 분석 | Event-Driven 전략 참고 | $49/월 |
| 8 | **Tickeron** | AI 패턴 인식 | 차트 패턴 자동 탐지 | $15-200/월 |
| 9 | **Danelfin** | AI 종목 스코어 | Factor 기반 점수화 | $60/월 |
| 10 | **Stock Hero** | 클라우드 봇, 간편 UI | 모바일 UX 참고 | $40/월 |
| 11 | **Capitalise.ai** | 자연어 전략 작성 | NLP 기반 전략 생성 | 무료-49/월 |
| 12 | **VectorVest** | 매수/매도/보유 점수 | 신호 시스템 참고 | $69/월 |
| 13 | **Ziggma** | 포트폴리오 분석 | 포트폴리오 대시보드 | 무료-30/월 |
| 14 | **Portfolio123** | 팩터 백테스팅 | Factor Investing 엔진 | $83-250/월 |
| 15 | **FinBrain** | AI 가격 예측 | ML 예측 모델 참고 | $29-99/월 |

### 19.2 암호화폐 중심 플랫폼 (12개)

| # | 플랫폼 | 주요 기능 | VAMOS AI 적용 포인트 | 비용 |
|:--|:--|:--|:--|:--|
| 16 | **Cryptohopper** | 멀티 전략 블렌딩 | 전략 앙상블 방식 | $19-99/월 |
| 17 | **3Commas** | DCA, Grid, Signal Bot | 다양한 봇 유형 참고 | $49/월 |
| 18 | **Pionex** | 18개 무료 봇 | Grid Trading 구현 | 무료 |
| 19 | **TradeSanta** | 간편 Long/Short | 사용자 친화적 UI | $18-45/월 |
| 20 | **Zignaly** | 시그널 복사 거래 | Copy Trading 기능 | 무료 |
| 21 | **Bitsgap** | 아비트라지 봇 | 아비트라지 로직 참고 | $29-149/월 |
| 22 | **HaasOnline** | 고급 스크립팅 | 커스텀 전략 언어 | $7.50-30/월 |
| 23 | **Coinrule** | If-Then 규칙 기반 | 규칙 엔진 설계 | 무료-450/월 |
| 24 | **Shrimpy** | 포트폴리오 자동 리밸런싱 | 리밸런싱 로직 | $15-63/월 |
| 25 | **Quadency** | 통합 대시보드 | 멀티 거래소 통합 | 무료-99/월 |
| 26 | **WunderTrading** | TradingView 연동 | 외부 신호 통합 | 무료-39/월 |
| 27 | **Altrady** | 스마트 거래 터미널 | 거래 터미널 UX | $17-50/월 |

### 19.3 기관/전문가 플랫폼 (8개)

| # | 플랫폼 | 주요 기능 | VAMOS AI 적용 포인트 | 비용 |
|:--|:--|:--|:--|:--|
| 28 | **Kensho** | S&P Global 소유, NLP 분석 | 기관급 NLP 참고 | 엔터프라이즈 |
| 29 | **Bloomberg Terminal** | 업계 표준 데이터 | 데이터 표준화 참고 | $24,000/년 |
| 30 | **Refinitiv Eikon** | Reuters 데이터 | 대체 데이터 소스 | $22,000/년 |
| 31 | **Numerai** | 크라우드소싱 헤지펀드 | 토너먼트 모델 | 무료 |
| 32 | **Quantopian (Archive)** | 교육 자료 | 오픈소스 Zipline | 종료 |
| 33 | **Hudson & Thames** | 학술 논문 구현 | mlfinlab 라이브러리 | $799/년 |
| 34 | **WorldQuant** | 알파 팩터 연구 | 팩터 연구 방법론 | 채용 |
| 35 | **Two Sigma** | ML 기반 헤지펀드 | ML 아키텍처 참고 | 기관 |

### 19.4 플랫폼별 상세 분석

**QuantConnect** (Rating: 5/5):
- 오픈소스 LEAN 엔진, 400TB+ 히스토리 데이터, 20+ 브로커 연동
- VAMOS AI 적용: 백테스팅 엔진 아키텍처, 데이터 구조, API 설계 벤치마크
- 가격: Free $0 / Researcher $20 / Team $60 / Institution $1,080

**Trade Ideas** (Rating: 4/5):
- Holly AI: 매일 수백만 시뮬레이션 실행, 실시간 스캔 + 자동 거래
- VAMOS AI 적용: Self-evo 실시간 전략 시뮬레이션 방식
- 가격: Standard $84 / Premium $167

**Pionex** (Rating: 5/5):
- 18개 무료 봇, 0.05% 거래 수수료 (업계 최저), 미국/싱가포르 라이센스
- 봇: Grid Trading, DCA, Rebalancing, Arbitrage, Smart Trade 등
- VAMOS AI 적용: Grid Trading 구현, 무료 봇 비즈니스 모델

### 19.5 기능별 비교 매트릭스

| 기능 | QuantConnect | Trade Ideas | Alpaca | Pionex | 3Commas | VAMOS |
|:--|:--:|:--:|:--:|:--:|:--:|:--:|
| 주식 | O | O | O | X | X | O |
| 암호화폐 | O | X | O | O | O | O |
| 백테스팅 | O | O | - | - | - | O |
| 실시간 | O | O | O | O | O | 개발중 |
| No-code | X | - | X | O | O | 개발중 |
| API | O | - | O | - | O | O |
| 무료 티어 | O | X | O | O | O | O |

### 19.6 도입 우선순위

**P0-P1 (필수/권장)**:
- QuantConnect: LEAN 백테스팅 구조 -> 엔진 아키텍처 참고
- Alpaca: REST API 설계 -> API 표준화
- 3Commas: DCA/Grid Bot -> 봇 유형 다양화
- TradingView: 차트 시각화 -> Grafana 대시보드

**P2 (장기)**:
- Trade Ideas: Holly AI 스캔 -> Self-evo 실시간 모드
- Composer: No-code 빌더 -> Builder View UI
- Cryptohopper: 전략 마켓플레이스 -> 전략 템플릿 스토어

**P3 (참고)**:
- Hudson & Thames: mlfinlab -> 학술 전략 구현
- Numerai: 토너먼트 모델 -> 커뮤니티 경쟁
- Kensho: 기관급 NLP -> 고급 텍스트 분석

### 19.7 VAMOS 목표 가격

| 플랜 | 가격 |
|:--|:--|
| Free | $0 |
| Basic | ~40,000원 |
| Pro | ~80,000원 |
| Enterprise | 별도 |

---

## 20. VAMOS Core 통합

### 20.1 아키텍처 연동 구조

```
VAMOS AI (ORANGE CORE)
       |
       +-- 정책 관리: 비용 상한 (V1: 4만원/월)
       +-- 승인 관리: P2 Trading 2단계 승인
       +-- Self-evo: 전략 개선 제안 (적용은 사용자 승인)
       |
       v
BLUE NODE: Trading/Quant
       |
       +-- 데이터 파이프라인 (83개 소스)
       +-- 전략 엔진 (RSI_BB, MAX_PAIN 등)
       +-- 백테스팅 엔진 (51% Gate)
       +-- 법적 제약 검증
       +-- 신호 생성 -> 주문 실행 (Paper/Real)
```

### 20.2 VAMOS AI 기능 -> 투자 시스템 매핑

> **[PART1 SP-03]** 모듈 ID는 D2.0-01 정본(CLAUDE.md §6) 기준으로 정정됨. I-7=Project/Session Manager, I-8=Policy Engine, I-9=Cost Manager.

| VAMOS AI 기능 | ID | 투자 시스템 적용 |
|:--|:--|:--|
| Self-check | I-6 | 전략 결과 검증, 환각 방지 |
| Self-evo | I-18 | 실패 전략 분석 -> 파라미터 개선 제안 |
| 메모리 관리 | I-3 | 프로젝트별 거래 이력 독립 저장 |
| 비용 관리 | I-9 | LLM 호출 비용 추적 (V1/V2/V3) |
| 안전(정책) 관리 | I-8 | P2 도메인 승인 강제, 실거래 차단 |
| RAG | I-2 | 과거 거래 패턴, 시장 뉴스 검색 |
| 로그 | S-1 | 모든 의사결정 기록 |

### 20.3 도메인 우선순위

| 등급 | 도메인 | 설명 |
|:--|:--|:--|
| **P0** | Dev/System, Research, Productivity | 핵심 -- Self-evo로 변경 불가 |
| **P1** | Content, Data & Quant | 확장 -- 승인 후 활성화 |
| **P2** | Trading Strategy | 위험 -- 2단계 승인 필수, 실거래 금지 |

### 20.4 VAMOS AI 차별화 포인트

| 기존 플랫폼 | VAMOS AI |
|:--|:--|
| 투자만 집중 | 범용 AGI 프레임워크 + 투자 모듈 |
| 단일 AI | Multi-Agent 협업 (5개 AI 분업) |
| 블랙박스 | Self-check + 근거 기반 출력 |
| 자동 실행 | Human-in-the-loop (P2 2단계 승인) |
| 비용 무제한 | 비용 상한 관리 (V1/V2/V3) |

### 20.5 통합 로드맵

| Phase | 기간 | 작업 내용 |
|:--|:--|:--|
| **A** | 1주 | 연동 인터페이스 정의 (Trading Node 스키마, 통신 규약, P2 승인 플로우) |
| **B** | 2-3주 | AI INVESTING 완성 (contracts.py 정렬, Docker, PoC 검증) |
| **C** | 4-6주 | VAMOS CORE 최소 기능 (I-6, I-7, I-8, I-9) |
| **D** | 2-3개월 | 통합 운영 (Trading Node 연결, Self-evo, 대시보드) |

---

## 21. Scraper Manager

### 21.1 개요

Playwright 기반 헤드리스 브라우저로 TIER-0/TIER-1 소스 17개를 수집합니다.

### 21.2 핵심 기능

```
Playwright 기반 헤드리스 브라우저

기능:
+-- 정기 스크래핑 (Cron 기반)
+-- Schema Drift 감지 (페이지 구조 변경 탐지)
+-- LLM Fallback 파싱 (구조 변경 시)
+-- 자동 재시도 + Quarantine
```

### 21.3 Schema Drift Detection

웹 페이지 구조가 변경될 경우:

1. **감지**: 기존 CSS 셀렉터 / XPath 실패 -> Drift Alert
2. **LLM Fallback**: LLM에 페이지 HTML 전달 -> 새 셀렉터 추출 시도
3. **실패 시**: S3 Quarantine 격리 -> Grafana 알림 -> 수동 검토

### 21.4 대상 소스

**TIER-0 (Critical -- 9개)**: Goldman Sachs Insights, TradingView Ideas, SwaggyStocks, OptionStrat, Earnings Whispers, BamSEC, US Treasury Rates, OpenInsider, FINRA Short Interest

**TIER-1 (High -- 8개)**: FINRA OTC Transparency, Investing.com Earnings, Asian Bond Online, World Gov Bonds, ShortSqueeze, ETF.com Screener, Walter Bloomberg (X), LME Market Data

### 21.5 파일

`scraper_drift_handler.py` -- Scraper 자동 복구 핸들러

---

## 22. Non-goal 강제 규칙

### 22.1 BASE LAYER 불변 원칙

BASE LAYER는 **절대 변경 불가** 영역입니다. 시스템의 모든 결정은 이 레이어의 제약 내에서만 이루어집니다.

### 22.2 불변 항목

| 항목 | 규칙 |
|:--|:--|
| **정체성 (Identity)** | VAMOS AI의 핵심 목표 및 가치관 변경 불가 |
| **Non-goal** | 정의된 Non-goal 범위 자동 차단 |
| **법/윤리 기준** | 법적 제약 (Wash Sale, PDT, Uptick) 우회 불가 |
| **비용 상한** | V1/V2/V3 비용 한도 초과 불가 |
| **Self-evo 제한** | AI 자율 진화 범위 제한, 사용자 승인 필수 |
| **Human-in-the-loop** | P2 Trading 도메인은 반드시 2단계 사용자 승인 |

### 22.3 Non-goal 강제 메커니즘

```
[사용자 요청]
    |
    v
[Front Mini LLM] 의도/보안/도메인 판별
    |
    v
[ORANGE CORE] Non-goal 체크
    |
    +-- Non-goal 해당 -> 차단 + 사유 안내
    +-- Non-goal 미해당 -> 다음 단계 진행
    |
    v
[BLUE NODE] 실행
    |
    +-- P0/P1 도메인 -> 즉시 실행
    +-- P2 (Trading) -> 2단계 승인 요청 -> 승인 시 실행
```

### 22.4 Circuit Breaker (안전 장치)

Non-goal과 별개로 운영되는 자동 안전 장치:

| 규칙 | 임계값 | 동작 |
|:--|:--|:--|
| 일일 손실 한도 | -3% | 당일 거래 중단 |
| VIX 임계 | > 40 | 매수 중단 |
| 포지션 손실 | -10% | 강제 청산 |
| 최소 현금 비율 | 20% | 신규 매수 차단 |
| 단일 종목 한도 | 10% | 추가 매수 차단 |

---

## 23. contracts.py 검토 보고서 (26건)

### 23.1 검토 개요

| 항목 | 내용 |
|:--|:--|
| 대상 문서 | `실행_단계_FINAL (1).md` (6,883 lines, ~265KB) |
| 검토 범위 | PHASE 1-4 전체 (STEP 1.1 ~ STEP 6) |
| 검토 횟수 | 총 4회 (1차 15건 -> 2차 70건+ -> 3차/4차 통합) |
| 검토자 | Claude (Opus 4.5) |
| 최종 보고일 | 2026-02-03 (4차 갱신) |

### 23.2 요약

| 구분 | 건수 |
|:--|--:|
| 기존 보고서 통합 (1차+2차) | 14건 |
| 3차 신규 발견 | 9건 |
| 4차 크로스체크 신규 발견 | 4건 |
| 4차 기존 항목 정정 (C 다운그레이드) | -1건 |
| **합계** | **26건** |

Blocker 수준 없음. **카테고리 D (contracts.py 불일치) 12건이 최고 우선순위**.

### 23.3 카테고리별 발견사항 (10개 카테고리)

| ID | 카테고리 | 심각도 | 건수 | 조치 시점 |
|:--|:--|:--|--:|:--|
| A | Source Mapping Gap | Medium | 1 | 코드 생성 전 |
| B | Key Content Focus 미추출 | Low | 1 | 선택적 |
| ~~C~~ | ~~Gap Analysis 완화조치 부재~~ | ~~Low~~ | ~~1~~ | **해소됨 (4차 정정)** |
| **D** | **contracts.py vs JSON Schema** | **High** | **12** | **코드 생성 전 필수** |
| E | DEFER 항목 관리 | Low | 1 | 선택적 |
| F | KB Chunking 설정 미완성 | Medium | 1 | 코드 생성 전 |
| G | Grafana Dashboard 패널 누락 | Medium | 1 | 코드 생성 전 |
| H | STEP 1.3 event_type 미갱신 | Medium | 1 | 코드 생성 전 |
| I | datetime.utcnow() Deprecated | Low | 1 | 코드 생성 시 |
| J | datetime.now() 비UTC 사용 | Low | 1 | 코드 생성 시 |

### 23.4 D 카테고리 상세 (12건)

| ID | 문제 | 위치 | 수정안 | 조치 상태 |
|:--|:--|:--|:--|:--|
| D-1 | OutputProfile에 RAW_ONLY 잔존 | line 3348 | RAW_ONLY 제거 (JSON Schema가 SOT) | [ACTION-REQUIRED: 구현 Phase A에서 해소] contracts.py에서 RAW_ONLY 리터럴 삭제, JSON Schema SOT 기준 정렬 |
| D-2 | ConnectorRequest.priority에 TIER-0/TIER-1 포함 | line 3446 | `Literal["P0", "P1"]`로 축소 | [ACTION-REQUIRED: 구현 Phase A에서 해소] TIER-0/TIER-1 리터럴 제거 후 P0/P1만 유지 |
| D-3 | VAMOS_EVENT.event_type -- enum 미적용 | line 3423 | `Literal[6개]` 적용 | [ACTION-REQUIRED: 구현 Phase A에서 해소] event_type 필드를 Literal 6종으로 제약 |
| D-4 | sentiment_score/impact_level 범위 누락 | line 3426-27 | `Field(ge=, le=)` 추가 | [ACTION-REQUIRED: 구현 Phase A에서 해소] Pydantic Field 범위 제약 추가 (sentiment: -1.0~1.0, impact: 1~5) — §4.2 SOT 기준 |
| D-5 | VAMOS_EVENT.content 비구조화 | line 3424 | `EventContent` 서브모델 생성 | [ACTION-REQUIRED: 구현 Phase A에서 해소] EventContent 서브모델 정의 후 content 필드 타입 교체 |
| D-6 | KB_EMBEDDING_RECORD 필드 누락 | line 3430-37 | `vector_dim`, `embedded_at_utc` 추가 | [ACTION-REQUIRED: 구현 Phase A에서 해소] 두 필드를 Optional로 추가, JSON Schema와 동기화 |
| D-7 | ConnectorRequest 필드 누락 | line 3442-50 | `trace_id`, `symbols`, `granularity` Optional 추가 | [ACTION-REQUIRED: 구현 Phase A에서 해소] 3개 Optional 필드 추가 |
| D-8 | OHLCV_PLUS sequence_id 위치 불일치 | line 1290 | JSON Schema도 최상위로 이동 | [ACTION-REQUIRED: 구현 Phase A에서 해소] JSON Schema에서 sequence_id를 최상위 properties로 이동 |
| D-9 | OHLCV_Values docstring "7 required" 오류 | line 3355 | "5 required + 3 optional"로 수정 | [RESOLVED] docstring 수정 완료 예정 -- 단순 텍스트 교체 |
| D-10 | Intent Literal에 "other" 누락 | line 3349 | `"other"` 추가 (4개로) | [ACTION-REQUIRED: 구현 Phase A에서 해소] Intent Literal에 "other" 추가 |
| D-11 | OHLCV_Values 조건부 required 불일치 | line 3354-63 | `Optional` + `model_validator`로 변경 | [ACTION-REQUIRED: 구현 Phase A에서 해소] Optional 타입 + model_validator 패턴으로 리팩터링 |
| D-12 | ConnectorResponse Pydantic 모델 부재 | line 1190-1230 | `ConnectorResponse` 모델 신규 생성 | [ACTION-REQUIRED: 구현 Phase A에서 해소] ConnectorResponse Pydantic 모델 신규 작성 |

### 23.5 수학 공식 검증 결과

**전수 검증 완료, 전건 정확.**

| 공식 | 검증 결과 | 비고 |
|:--|:--:|:--|
| Sharpe Ratio (연율화) | 정확 | ddof=1 표본 표준편차, 정석 구현 |
| Wilder RSI | 정확 | SMA seed + EMA smoothing, Wilder 원전 일치 |
| Bollinger Bands | 정확 | ddof=0 모집단 표준편차, BB 원전 일치 |
| Decay Rate | 정확 | 음수 방지 + 0 분모 처리 |
| 연율화 팩터 | 정확 | 1d=sqrt(252), 1h=sqrt(1638), 1m=sqrt(98280) |
| rf 변환 | 정확 | 복리 변환 정석 |

### 23.6 STEP 6 Backport 검증 결과

소급 반영 12건 + 신규 삽입 6건: **전건 적용 완료**.

**소급 반영 12건**:
1. PATCH 주석 삭제, 2. Selenium/Puppeteer -> Playwright (3건), 3. Airflow/Dagster -> Airflow (2건), 4. Kafka/RabbitMQ -> Kafka, 5. Kafka/Redpanda -> Kafka (2건), 6. Python 3.11 -> 3.12, 7. 대안 소스 정정

**신규 삽입 6건**: yfinance Quarantine 트리거, Grafana 메트릭 추가, 마이그레이션 추적, API 키 관리, V1 Fallback 한계, PoC OHLCV 타입 정렬

### 23.7 우선순위별 권고사항

**P0 (코드 생성 전 필수)**: contracts.py Pydantic 모델 -> JSON Schema 완전 정렬 (D-1~D-12, 12건)

**P1 (코드 생성 전 권장)**:
- Grafana Dashboard JSON 보완 (G)
- STEP 1.3 event_type 갱신 (H)
- KB Chunking 플레이스홀더 해소 (F)
- Source Mapping 기본 규칙 추가 (A)

**P2 (선택적 개선)**:
- datetime.utcnow() 교체 (I) + datetime.now() UTC 통일 (J)
- Key Content Focus 트레이서빌리티 (B)
- DEFER Registry 생성 (E)

### 23.8 전체 작업 체크리스트

| 우선순위 | 건수 | 범위 |
|:--|:--:|:--|
| P0 | 11건 | contracts.py + JSON Schema |
| P1 | 4건 | 문서 수정 |
| P2 | 3건 | 선택적 개선 |
| **합계** | **18건** | |

---

## 24. Z-Session 통합

### 24.1 프로젝트 개요

**Z_Session**은 **암호화폐 자동 트레이딩 전략 생성/실행/관리 시스템**입니다.

> "심볼 단위로 점수화된 코인을 추출한 뒤, 각 프레임마다 전략을 독립적으로 생성/분석하고, 이를 각기 다른 거래소에 자동 분산 매매시키며 전략 생존 여부를 실시간으로 판단하고 추적하는 완전 자동화 트레이딩 시스템"

### 24.2 버전 현황

| 경로 | 버전 | 설명 |
|:--|:--|:--|
| `D:\Z_session_project_v3_6` | v3.6 (최신) | 기준표 3.6 기반, A/B 세션 구조화 |
| `D:\Z_session_project_v3_0` | v3.0 | 통합 실행기, 다중 세션(A~G) 구조 |
| `D:\Z_session_project_v2_8` | v2.8 | 기준표 2.8 기반, GUI 대시보드 |
| `D:\Z_session_dashboard_project` | - | FastAPI+React 웹 대시보드 |

### 24.3 세션(단계) 구조 (A~G + Q + X)

| 세션 | 명칭 | 역할 |
|:--|:--|:--|
| **A** | 전략 설계 및 분석 | 심볼 분석, 점수화, 매크로/거시지표, 고급 필터링, 전략간 상호작용 |
| **B** | 전략 코드 생성 | 기술적 지표 분석, 조건 조합, GPT -> Pine Script 자동 생성 |
| **C** | 전략 검증/시뮬레이션 | 자산 분산 백테스트, 리스크/보상 비율, 감정적 오류 검토 |
| **D** | 자동화 연동 | AlertCondition, JSON 웹훅, 실행 내역 기록 |
| **E** | 고급 필터링 | 온체인 분석, SMC, 엘리엇 파동, 하모닉 패턴, DeFi TVL |
| **F** | 대시보드/시각화 | 백테스트 결과, 실시간 포지션, 수익률 현황 |
| **G** | 비전 분석 | 차트 이미지 기반 패턴 인식 (GPT Vision) |
| **Q** | 오류 처리 | Pine Script 오류 자동 감지 + GPT 기반 수정 |
| **X** | 전략 재생성 | 실패 전략 재생성 루프, 조건 생명주기, 우선순위 큐 |

### 24.4 핵심 파이프라인

```
[A단계] 심볼 분석 -> 점수화 -> 상위 N개 선정
    |
[B단계] 조건 생성 -> Pine Script 자동 생성
    |
[C단계] 백테스트 -> 성능 평가 (PF, 승률, MDD)
    |
[D단계] Webhook/Alert 연동 -> 자동 주문
    |
[E단계] 고급 필터 적용 -> 정밀도 향상
    |
[F단계] 대시보드 시각화 -> 전략 유지/제외 판단
    |
[X단계] 실패 전략 -> 재생성 루프
```

### 24.5 타임프레임별 전략 분산

| 프레임 | 분석 범위 | 전략 성격 | 거래소 |
|:--|:--|:--|:--|
| 15m | 단기/초단타 | 고속 매수매도 | Binance |
| 1h~4h | 중단기 트렌드 | 스윙 트레이딩 | Bybit |
| 12h~1d | 중장기 추세 | 추세 추적형 | OKX |
| 3d~1w | 장기 투자 | 포트폴리오 기반 | Bitget |

**실행 흐름 예시**:
```
BTC (Top 10 심볼에 포함)
+-- BTC_15m -> Binance 자동 단타 진입 (cond_0012)
+-- BTC_1h -> Bybit 자동 스윙 진입 (cond_0008)
+-- BTC_1d -> OKX 자동 추세 진입 (cond_0019)
+-- BTC_1w -> Bitget 자동 장기 진입 (cond_0034)
```

### 24.6 조건 ID 체계

```
{심볼}_{프레임}_cond_{번호}
예: BTC_15m_cond_0003
    ETH_1d_cond_0007
```

### 24.7 전략 성능 기준

| 지표 | 기준 | 설명 |
|:--|:--|:--|
| 승률 | > 60% | 우수 전략 |
| PF (Profit Factor) | >= 1.5 | 수익성 있음 |
| 기대값 (EV) | > 0.2 | 거래당 평균 수익 |
| MDD | < 10% | 최대 낙폭 허용치 |

판단: **keep** (유지) / **hold** (보류) / **exclude** (제외)

### 24.8 현재 성과 (v3.6)

- 지원 심볼: BTCUSDT, ETHUSDT, SOLUSDT, ARBUSDT, LINKUSDT, MATICUSDT, OPUSDT
- 총 56개+ 전략 파일 생성
- 성능: 승률 61.8%, PF 1.74, 기대값 2.3, MDD 6.9%
- 판단: **keep** (유지)

### 24.9 사용 도구

| 도구 | 용도 |
|:--|:--|
| ChatGPT | 전략/계획 구성, Pine Script/Python 코드 생성 |
| VS Code | 전략 코드 편집/실행/테스트 |
| OpenAI API | 코드 실행/테스트, 오류 분석 및 수정 |
| GitHub | 코드 버전 관리 및 백업 |
| Python | 백테스트 및 자동화 처리 |
| Pine Script (TradingView) | 전략 시각화 및 실전 테스트 |

### 24.10 대시보드 시스템

**GUI 대시보드 (Tkinter)**: 전략 상태 실시간 표시, 상태 변경 (더블클릭), 새로고침

**웹 대시보드 (Flask -- port 7860)**: 전략 필터 결과, 오류 건수, 실시간 예측, 매매 트리거/결과

**관리 대시보드 (FastAPI+React)**: `/api/server`, `/api/venv`, `/api/sync`, `/api/resource`, `/api/cleanup`, `/api/ssh`

### 24.11 리스크 및 고려사항

| # | 리스크 | 극복 방안 |
|:--|:--|:--|
| 1 | 다중 거래소 API 차이 (심볼 표기) | adapter 모듈 |
| 2 | 동일 코인 4프레임 동시 매수/매도 | 잔고 체크 + 라우팅 |
| 3 | 프레임별 전략 평가 격차 (15m vs 1w) | 조건 차등 적용 |
| 4 | 시그널 동시 발생 | 포지션 락 + 비동기 큐 |
| 5 | 전략 수 급증 (10코인x4프레임x4거래소=160) | 전략 메타 관리 강화 |
| 6 | Rate Limit 초과 | 호출 스로틀 + 큐 처리 |
| 7 | 슬리피지/실거래 오차 | 거래 로그 + 슬리피지 추적기 |
| 8 | 시스템 장애 위험 | 모듈화 + 예외 핸들러 |
| 9 | 조건 재생성 과부하 | 큐 제한 + 우선순위 관리 |

### 24.12 TradingView 대체 구조

| 기능 | TradingView | VS Code 대체 |
|:--|:--|:--|
| 차트 표시 | Web Widget | Plotly, Dash, Matplotlib |
| 전략 적용 | Pine Script | Python (talib, backtrader) |
| 진입/청산 시뮬레이션 | strategy.entry() | Pandas + 조건 로직 |
| 성능 지표 | 자동 계산 | bt, backtrader, quantstats, pyfolio |
| 전략 유지 판단 | 수동 | auto_decision_controller.py |
| 생명주기 추적 | 없음 | condition_lifecycle_tracker.json |

### 24.13 Pine Script 전략 템플릿

**기술적 지표 조건 (Long)**:
```pinescript
strategy('Long Strategy', overlay=true)
entry_condition = (rsi(close, 14) < 30)
if entry_condition
    strategy.entry('Long Entry', strategy.long)
tp = 1.02
sl = 0.98
```

**조합형 조건 (RSI + MACD)**:
```pinescript
strategy('Composite Strategy', overlay=true)
rsi_cond = ta.rsi(close, 14) < 30
[macdLine, signalLine, _] = ta.macd(close, 12, 26, 9)
macd_cross = ta.crossover(macdLine, signalLine)
entry_condition = rsi_cond and macd_cross
if entry_condition
    strategy.entry('Composite Entry', strategy.long)
```

### 24.14 마인드셋

- **심볼**은 분석 단위
- **프레임**은 전략 단위
- **거래소**는 실행 경로
- **조건**은 시그널 트리거
- **전략**은 생명주기를 갖고 경쟁하며 유지된다

---

## 부록 A: 파일 구조

### A.1 VAMOS AI INVESTING 핵심 파일

```
vamos/
+-- contracts.py              # 데이터 계약 (Pydantic 모델)
+-- vamos_dag_factory.py      # Airflow DAG 생성
+-- vamos_stream_gateway.py   # 실시간 스트림 수신
+-- scraper_drift_handler.py  # 스크래퍼 자동 복구
|
+-- backtest/
|   +-- run_backtest.py       # 백테스트 진입점
|   +-- data_loader.py        # 데이터 로더
|   +-- strategies.py         # 전략 구현
|   +-- backtest_engine.py    # 핵심 엔진
|
+-- config/
|   +-- sources.yaml          # 데이터 소스 설정
|   +-- strategies.yaml       # 전략 파라미터
|   +-- alerts.yaml           # 알림 설정
|
+-- docker/
    +-- docker-compose.yml    # 전체 스택 구성
```

### A.2 Z-Session v3.6 파일 구조

```
Z_session_project_v3_6/
+-- run_integrated_z.py              # 통합 실행기
+-- logs/
|   +-- x_update_log.md
+-- Zsession_A_restructured/         # A세션
|   +-- strategy_runner_all.py
|   +-- x_runner_dynamic.py
|   +-- evaluators/                  # 평가 모듈
|   |   +-- a_score_evaluator.py
|   |   +-- a_validator.py
|   |   +-- adaptive_threshold_updater.py
|   |   +-- feedback_retrainer.py
|   |   +-- pre_auto_validator.py
|   +-- normalizers/                 # 정규화 모듈
|   |   +-- condition_id_generator.py
|   |   +-- condition_tracker.py
|   |   +-- lifecycle_tracker.py
|   +-- trackers/                    # 추적 모듈
|       +-- category_correlation_analyzer.py
|       +-- marketcap_classifier.py
+-- Zsession_B_strategies/           # B세션
    +-- generators/
    |   +-- strategy_generator.py
    |   +-- prompt_updater.py
    +-- validators/
    |   +-- pine_checker_main.py
    +-- testers/
    |   +-- signal_test_runner.py
    |   +-- auto_decision_controller.py
    +-- templates/
    |   +-- prompt_templates.json
    +-- output/
        +-- strategy_*.pinescript
```

### A.3 소스 문서 목록 (16+ 파일)

| # | 파일명 | 내용 |
|:--|:--|:--|
| 1 | VAMOS_System_Architecture.md | 시스템 아키텍처, 6-Layer 구조 |
| 2 | VAMOS_Complete_Guide.md | PHASE 1-4 전체 가이드 |
| 3 | 01_시스템_구조_및_현황.md | 4-Layer 아키텍처, ORANGE CORE + BLUE NODE |
| 4 | 02_단점_및_극복방안.md | 15개 결함 D-01~D-15 |
| 5 | 03_참고_AI_투자_플랫폼.md | 35개 참고 플랫폼 |
| 6 | 04A_투자전략_기술적분석.md | 기술적 분석 40개 |
| 7 | 04B_투자전략_퀀트_ML.md | 퀀트/팩터/옵션/ML 56개 |
| 8 | 05_통합_로드맵.md | 4-Phase 로드맵, ML/AI 스택 |
| 9 | Z_session_종합정리.md | Z-Session 암호화폐 자동 트레이딩 |
| 10 | VAMOS_실행단계_FINAL_검토보고서.md | 26건 검토 보고서 |
| 11 | strategies.py | RSI_BB, MAX_PAIN, MACRO_ROTATION |
| 12 | backtest_engine.py | 백테스팅 엔진, 51% Gate |

---

## 부록 B: 현황 요약

### B.1 완성 현황

| 항목 | 상태 | 비고 |
|:--|:--:|:--|
| Multi-Agent 워크플로우 (5 AI) | 완료 | Perplexity -> Gemini -> ChatGPT -> Claude -> Copilot |
| 83개 데이터 소스 분류 | 완료 | P0(16), P1(9), TIER-0/TIER-1(17), KB(41+) |
| 데이터 스키마 (OHLCV_PLUS, EVENT) | 완료 | JSON Schema + Pydantic (12건 불일치 잔존) |
| DQ Validation 체계 | 완료 | HARD_FAIL / SOFT_FAIL / Quarantine |
| 백테스팅 엔진 | 완료 | 51% Gate, Sharpe(ddof=1), 70/30 분할 |
| RSI_BB 전략 구현 | 완료 | 27조합 파라미터 그리드 (현재 INSUFFICIENT_SAMPLE) |
| 96개 투자 전략 설계 | 완료 | 기술(40) + 퀀트/팩터/옵션/ML(56) |
| 법적 제약 시스템 | 완료 | Wash Sale, PDT, Uptick Rule |
| 14-Item Locked 기술 스택 | 완료 | 변경 금지 |
| 수학 공식 검증 | 완료 | 4차 크로스체크, 전건 정확 |
| STEP 6 Backport | 완료 | 12건 소급 + 6건 신규, 전건 적용 |
| Z-Session (v3.6) | 완료 | 56개+ 전략, 승률 61.8% |

### B.2 미완료 항목 (P0 Blocker)

| 항목 | 상태 | 차단 요인 | 해소 일정 | 해소 방법 |
|:--|:--:|:--|:--|:--|
| contracts.py <-> JSON Schema 정렬 | 미완료 | 12건 불일치 (D-1~D-12) | Phase A 1주차 (즉시) | D-1~D-12 항목별 수정안 적용, JSON Schema SOT 기준 Pydantic 모델 일괄 정렬. 상세: 23.4절 조치 상태 참조 |
| Docker 환경 구축 | 미착수 | docker-compose.yml 미작성 | Phase A 1주차 (즉시) | docker-compose.yml 작성 (TimescaleDB + ChromaDB + Airflow + Kafka + Grafana), .env.example 포함 |
| API 키 확보 | 미착수 | KRX, OpenAI 등 | Phase A 1~2주차 | 필수 키(yfinance: 불필요, Alpha Vantage: V2, OpenAI: V2) 단계별 확보. V1은 무료 소스만 사용하므로 차단 아님 |
| PoC 실행 검증 | 미착수 | 환경 미구축 | Phase A 2주차 | Docker 환경 + contracts.py 정렬 완료 후 PoC 5건(OHLCV 수집, DQ 검증, RSI_BB 백테스트, Grafana 대시보드, 51% Gate) 순차 실행 |

### B.3 다음 단계

> **HISTORICAL**: 아래 일정은 초기 계획 시점의 기록입니다.
> 현행 일정은 PART2 §6.8을 참조하세요.

```
즉시 (1-2주):
  1. contracts.py 12건 정렬 -> P0 해소
  2. Docker Compose 작성
  3. API 키 확보 + PoC 5건 실행
  4. RSI_BB 파라미터 튜닝

단기 (2-4주):
  5. MACD/MA Crossover 전략 추가
  6. Kelly Criterion + API Fallback Chain
  7. 전략 3개 51% Gate PASS 달성

중기 (1-2개월):
  8. FinBERT 감성 분석 통합
  9. Circuit Breaker 구현
  10. Paper Trading 2주 운영

장기 (3-6개월):
  11. VAMOS CORE 통합 (I-6, I-7, I-8, I-9)
  12. LSTM 가격 예측 + RL 실험
  13. 실전 거래 소액 시작
```

---

> **문서 끝** -- VAMOS AI INVESTING 통합 명세서 v2.0
> 총 24개 섹션 + 부록 A, B | ZERO 누락 원칙 적용
> 작성일: 2026-02-23

---

<\!-- END OF DOCUMENT -->
