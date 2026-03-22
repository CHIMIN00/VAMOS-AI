---
session: 23
sections: [29]
status: complete
---

# §29. AI Investing — 투자 분석 시스템

> **비유**: 여러분이 세계 최고의 **투자 분석 회사**를 운영한다고 상상해보세요. 이 회사에는 7개 부서가 있습니다 — 데이터 수집팀, 데이터 정제팀, 저장소 관리팀, 전략 연구팀, 거래 실행팀, 감시팀, 자동화 운영팀. 83개 뉴스/데이터 채널에서 정보를 모으고, 96가지 투자 전략을 분석하고, 신뢰도 51% 미만이면 자동으로 거부합니다. VAMOS의 **AI Investing**은 바로 이 회사를 소프트웨어로 구현한 것입니다.

[근거: AI_INVESTING_SPEC §1, §2]

---

## §29.1 시스템 개요 & 7-Layer 데이터 아키텍처

### 비유: 투자 분석 회사의 부서 구조

투자 분석 회사를 떠올려 보세요. 1층에는 신문/뉴스를 모아오는 **수집팀**, 2층에는 거짓 정보를 걸러내는 **검증팀**, 3층에는 모든 자료를 보관하는 **자료실**, 4층에는 투자 전략을 연구하는 **전략팀**, 5층에는 실제 매매를 수행하는 **트레이딩팀**, 6층에는 성과를 모니터링하는 **감시팀**, 7층에는 이 모든 과정을 자동으로 돌리는 **자동화팀**이 있습니다.

VAMOS AI Investing도 정확히 이 7개 층(Layer) 구조로 동작합니다.

### 핵심 목표

| 항목 | 내용 |
|:--|:--|
| 핵심 지표 | 승률 >= 51%, Sharpe Ratio (위험 대비 수익률) >= 1.0 |
| 대상 자산 | 미국 주식 (SPY, QQQ), 한국 주식, 암호화폐 (BTC-USD) |
| 운영 모드 | Paper Trading (모의 거래) → 실전 거래 |
| 기술 스택 | Python 3.12, Airflow, Kafka, TimescaleDB, ChromaDB, Grafana |

[근거: AI_INVESTING_SPEC §1.1]

### 7-Layer 아키텍처 구조도

```
Layer 1: 데이터 수집    →  Primary API + Scraper + Knowledge Base (83개 소스)
Layer 2: 데이터 처리    →  Contract Validator → Transform → Quarantine Zone (격리)
Layer 3: 저장           →  TimescaleDB (시계열) + ChromaDB (벡터) + S3/MinIO (파일)
Layer 4: 전략 엔진      →  전략 실행 → 법적 검증 → 신호 생성
Layer 5: 실행           →  주문 생성 → 거래 실행 → 결과 기록
Layer 6: 모니터링       →  Grafana Dashboard (실시간 감시)
Layer 7: 자동화 오케스트레이션  →  Airflow + Kafka + Scraper Manager
```

### 각 Layer의 핵심 구성요소

| Layer | 구성요소 | 역할 (비유) | 핵심 파일 |
|:--|:--|:--|:--|
| 1 | contracts.py | 데이터 형태 검증 — "입장 시 신분증 확인" | `contracts.py` |
| 2 | Pipeline Targets | 수집 대상 메타데이터 — "수집할 뉴스 채널 목록" | `sources.yaml` |
| 3 | Airflow DAG | 정기 수집 자동화 — "매일 아침 신문 배달" | `vamos_dag_factory.py` |
| 4 | Stream Gateway | 실시간 데이터 수신 — "속보 뉴스 즉시 전달" | `vamos_stream_gateway.py` |
| 5 | Scraper Manager | 웹 스크래핑 — "인터넷 기사 자동 수집" | `scraper_drift_handler.py` |
| 6 | Knowledge Base | 데이터 저장소 — "회사 자료실" | TimescaleDB + ChromaDB |
| 7 | Monitoring | Grafana 대시보드 — "관제 센터 모니터" | Grafana >= 10.0 |

[근거: AI_INVESTING_SPEC §2]

### Multi-Agent 워크플로우 (5개 AI 분업)

| AI | 역할 | 비유 |
|:--|:--|:--|
| **Perplexity** | 데이터 소스 발굴, 리서치 | 정보 수집 기자 |
| **Gemini** | 분류, 기술 분석, PM | 분석관 |
| **ChatGPT** | 전략 로직, 코드 작성 | 전략 개발자 |
| **Claude** | 검증, 감사, Gate 판정 | 감사관 |
| **VS Code Copilot** | 코드 구현 보조 | 프로그래밍 보조원 |

[근거: AI_INVESTING_SPEC §1.2]

### 버전별 비용 계획

| 항목 | V1 (~$30/월, 실비용 ~$0) | V2 (~$70/월) | V3 (~$200/월) |
|:--|:--|:--|:--|
| 데이터 | yfinance 무료 | Alpha Vantage $29 | Polygon Pro $79 |
| 인프라 | Docker Compose | Docker Compose (Hetzner CX31 권장) $30 | AWS t3.large $60 |
| LLM | 미사용 | GPT-4o mini $20 | GPT-4o $50 |

> **참고**: 위 비용은 AI Investing 도메인 전용 서브예산이며, VAMOS 전체 LOCK 상한 (V1 ₩40,000 / V2 ₩93,000 / V3 ₩266,000)과는 별도 산정됩니다.

> **v26 Hetzner 경로 업데이트**: V3에서 AWS 대신 Hetzner CX31 + RunPod Serverless를 선택하면 서버 비용이 ~$60→~$8+$6-15/월로 대폭 절감됩니다. AI Investing 모듈은 Docker 네트워크 `vamos-network`에서 ORANGE CORE, BLUE NODE와 localhost 통신하며, PostgreSQL(스키마 분리), Redis(DB 번호 분리), LLM API 키(I-9 통합 추적)를 공유합니다. [근거: PART2 V3-Phase 1 인프라 대안, v26 메이커에반 개선안 7]

[근거: AI_INVESTING_SPEC §18.6]

**핵심 요약 (3줄)**
1. VAMOS AI Investing은 83개 데이터 소스에서 정보를 수집하고 96개 전략으로 분석하는 자율 투자 관리 시스템입니다.
2. 7-Layer 아키텍처 (수집 → 처리 → 저장 → 전략 → 실행 → 모니터링 → 자동화)로 구성됩니다.
3. 5개 AI (Perplexity, Gemini, ChatGPT, Claude, Copilot)가 역할을 나누어 협업합니다.

---

## §29.2 83개 데이터 소스 (P0/P1/TIER-0/TIER-1/KB)

### 비유: 83개 뉴스 채널 구독

투자 분석 회사가 정보를 얻기 위해 83개 채널을 구독한다고 생각해보세요. 가장 중요한 채널 (P0)은 반드시 매일 확인하고, 중요한 채널 (P1)은 자주 확인하며, 웹에서 직접 긁어오는 채널 (TIER-0/TIER-1)은 스크래퍼가 자동으로 수집하고, 나머지 참고 자료 (KB)는 도서관에 보관합니다.

### 카테고리별 데이터 소스 분류

| 카테고리 | 개수 | 설명 | 수집 방식 |
|:--|:--:|:--|:--|
| **P0 (Critical)** | 16개 | 절대 필수 — 없으면 시스템 작동 불가 | API 직접 호출 |
| **P1 (High)** | 9개 | 중요 — 분석 품질 향상 | API 호출 |
| **TIER-0 (Critical Scraper)** | 9개 | 웹 스크래핑 필수 대상 | Playwright 스크래퍼 |
| **TIER-1 (High Scraper)** | 8개 | 웹 스크래핑 보조 대상 | Playwright 스크래퍼 |
| **KB (Knowledge Base)** | 41개+ | 참고 자료 | 수동/자동 갱신 |
| **합계** | **83개** | | |

> **TIER-0/TIER-1 명칭 변경**: 원래 S0/S1이었지만, VAMOS 메인 상태머신의 S0_RECEIVED/S1_INTENT_PARSED와 명칭이 충돌하여 TIER-0/TIER-1로 변경되었습니다. **[LOCK — 변경 불가]**

[근거: AI_INVESTING_SPEC §3, PART1 AI-01]

### P0 (Critical) — 16개 핵심 소스

| # | 소스 | 데이터 유형 | 쉬운 설명 |
|:--|:--|:--|:--|
| 1 | FRED (St. Louis Fed) | 미국 거시경제 | 미국 중앙은행 경제 데이터 |
| 2 | ECOS (Bank of Korea) | 한국 거시경제 | 한국은행 경제 데이터 |
| 3 | KRX Data System | 한국 주식 | 한국거래소 주식 데이터 |
| 4 | CME Market Data | 선물/옵션 | 시카고 상품거래소 파생상품 |
| 5 | Cboe VIX Historical | 변동성 지수 | "공포 지수" 역사 데이터 |
| 6 | Nasdaq Data Link | 대체 데이터 | 나스닥 대체 데이터 |
| 7 | Dune Analytics | 블록체인 SQL | 블록체인 데이터 분석 |
| 8 | Etherscan | 이더리움 탐색 | 이더리움 거래 내역 조회 |
| 9 | DeFiLlama | DeFi TVL | 탈중앙 금융 예치금 추적 |
| 10 | Glassnode Studio | 온체인 메트릭 | 블록체인 투자자 행동 분석 |
| 11 | SEC EDGAR | 미국 공시 | 미국 증권거래위원회 공시 |
| 12 | DART (OpenAPI) | 한국 공시 | 한국 전자공시시스템 |
| 13 | Stocktwits | 소셜 감성 | 투자자 SNS 감성 분석 |
| 14 | ApeWisdom | Reddit 감성 | Reddit 투자 커뮤니티 감성 |
| 15 | iShares Product List | ETF 구성 | ETF 포함 종목 목록 |
| 16 | AWS Data Exchange | 클라우드 데이터 | AWS 데이터 마켓플레이스 |

### P1 (High) — 9개

Federal Register, arXiv (q-fin), FCA Warning List, PR Newswire, Business Wire, EIA (Energy Stats), NOAA Climate Data, SEC Form D Search, Token Terminal

### TIER-0 (Critical Scraper) — 9개

Goldman Sachs Insights, TradingView Ideas, SwaggyStocks, OptionStrat, Earnings Whispers, BamSEC, US Treasury Rates, OpenInsider, FINRA Short Interest

### TIER-1 (High Scraper) — 8개

FINRA OTC Transparency, Investing.com Earnings, Asian Bond Online, World Gov Bonds, ShortSqueeze, ETF.com Screener, Walter Bloomberg (X), LME Market Data

### KB (Knowledge Base) — 41개+

IRS 세금 가이드, 거래소 규정집, IMF Data Portal, Eurostat 등 (Scope 1~23의 나머지 소스)

[근거: AI_INVESTING_SPEC §3.1~§3.4]

**핵심 요약 (3줄)**
1. 총 83개 데이터 소스가 5개 카테고리 (P0 16개, P1 9개, TIER-0 9개, TIER-1 8개, KB 41개+)로 분류됩니다.
2. P0은 API 직접 호출, TIER-0/TIER-1은 Playwright 기반 웹 스크래핑으로 수집합니다.
3. TIER-0/TIER-1 명칭은 메인 상태머신과의 충돌 방지를 위해 S0/S1에서 변경된 것입니다.

---

## §29.3 96개 투자 전략 (기술/퀀트/옵션/ML)

### 비유: 96명의 투자 전문가

투자 분석 회사에 96명의 전문가가 있다고 생각해보세요. 40명은 **차트 분석가** (기술적 분석), 26명은 **수학/통계 전문가** (퀀트/팩터/옵션), 8명은 **AI 연구원** (ML/AI), 나머지는 이벤트/암호화폐/포트폴리오 전문가입니다. 각 전문가는 자기만의 방법으로 "지금 사야 할까? 팔아야 할까?"를 분석합니다.

### 4개 카테고리별 전략 수

| 카테고리 | 전략 수 | 주요 분류 |
|:--|:--:|:--|
| **기술적 분석 (Technical Analysis)** | 40개 | 추세 추종 7, 모멘텀 5, 변동성 6, 거래량 3, 복합 4, 차트 패턴 15 |
| **퀀트/팩터/옵션 (Quant/Factor/Options)** | 30개 | 퀀트/통계 12, 팩터 8, 옵션 10 |
| **이벤트/암호화폐/포트폴리오** | 18개 | 이벤트 6, 암호화폐 6, 포트폴리오/리스크 6 |
| **ML/AI** | 8개 | LSTM, RL, Random Forest, XGBoost 등 |
| **합계** | **96개** | |

[근거: AI_INVESTING_SPEC §7, §8]

### 기술적 분석 (40개) — 주요 전략 예시

| 분류 | 전략 수 | 대표 전략 | 쉬운 설명 |
|:--|:--:|:--|:--|
| 추세 추종 | 7 | MACD Crossover, MA Crossover, Ichimoku Cloud | 주가 흐름을 따라가는 전략 |
| 모멘텀/오실레이터 | 5 | Stochastic, Williams %R, CCI | 과매수/과매도 (너무 많이 오르거나 떨어진 상태) 감지 |
| 변동성 기반 | 6 | Fibonacci, ATR Breakout, Squeeze Momentum | 가격 변동 폭을 이용한 전략 |
| 거래량 기반 | 3 | Volume Profile, VWAP, OBV | 거래량 변화로 매매 신호 파악 |
| 복합 | 4 | Pivot Points, Renko, Triple Screen | 여러 지표를 조합한 전략 |
| 차트 패턴-반전 | 7 | Head & Shoulders, Double Top/Bottom | 추세가 바뀌는 패턴 감지 |
| 차트 패턴-지속 | 8 | Cup & Handle, Flag, Triangle | 추세가 계속되는 패턴 감지 |

### 퀀트/팩터/옵션/ML (56개) — 카테고리별 예시

| 분류 | 전략 수 | 대표 전략 | 쉬운 설명 |
|:--|:--:|:--|:--|
| 퀀트/통계 | 12 | Mean Reversion, Pairs Trading, Kalman Filter | 통계적 법칙으로 매매 |
| 팩터 투자 | 8 | Value, Momentum, Quality, Multi-Factor | 특정 요인 (저평가, 성장성 등)으로 종목 선정 |
| 옵션 | 10 | Covered Call, Iron Condor, Bull Call Spread | 옵션 (주식 사고팔 권리) 활용 전략 |
| 이벤트 기반 | 6 | Earnings Momentum, Merger Arbitrage, FOMC | 기업 실적/합병/금리 발표 등 이벤트 활용 |
| ML/AI | 8 | LSTM, RL (DQN/PPO), FinBERT, XGBoost | 인공지능/기계학습 예측 |
| 암호화폐 | 6 | Grid Trading, DCA, DeFi Yield, Whale Tracking | 암호화폐 전용 전략 |
| 포트폴리오/리스크 | 6 | Kelly Criterion, Risk Parity, Black-Litterman | 자산 배분 및 위험 관리 |

### 시장 상황별 전략 선택 가이드

| 시장 상황 | 권장 전략 | 회피 전략 |
|:--|:--|:--|
| 강한 상승 추세 | MACD, MA Crossover, Supertrend | Mean Reversion (평균 회귀) |
| 강한 하락 추세 | Parabolic SAR, Ichimoku | 역추세 매수 |
| 횡보장 (옆으로) | RSI_BB, Stochastic | 추세 추종 |
| 변동성 급증 | ATR Breakout, Squeeze Momentum | Grid Trading |

[근거: AI_INVESTING_SPEC §7.9]

### 유일한 구현 완료 전략: RSI_BB

현재 96개 전략 중 **RSI_BB만 구현 완료**되었습니다.

- **진입 조건**: RSI(상대강도지수) < 과매도 AND 종가 < 볼린저 밴드 하단
- **청산 조건**: RSI > (100 - 과매도) OR 종가 > 볼린저 밴드 상단
- **파라미터**: 27가지 조합 (RSI 기간 3가지 × 과매도 기준 3가지 × BB 기간 3가지)
- **현재 상태**: 전 심볼 INSUFFICIENT_SAMPLE (샘플 부족)

[근거: AI_INVESTING_SPEC §9]

### 버전별 전략 활성 여부

| 항목 | V0 (현재) | V1 | V2 | V3 |
|:--|:--|:--|:--|:--|
| 구현 전략 | RSI_BB 1개 | +MACD, MA 등 3개+ | +ML 전략 추가 | 전략 다양화 완성 |
| 51% Gate | 미통과 | PASS 목표 | 다수 PASS | 전략 앙상블 |
| Paper Trading | 미착수 | 시작 | 2주 운영 | 실전 전환 |

[근거: AI_INVESTING_SPEC §18]

**핵심 요약 (3줄)**
1. 총 96개 투자 전략이 기술적 분석(40), 퀀트/팩터/옵션(30), 이벤트/암호화폐/포트폴리오(18), ML/AI(8) 4개 카테고리로 분류됩니다.
2. 현재 RSI_BB 1개만 구현 완료이며, 나머지 95개는 설계만 완료된 상태입니다.
3. 시장 상황 (상승/하락/횡보/변동성)에 따라 적합한 전략이 다르며, 자동 선택 시스템을 목표로 합니다.

---

## §29.4 51% Gate & 백테스팅 엔진

### 비유: 시험 합격 기준

대학교 시험에서 51점 이상이어야 합격하는 것처럼, VAMOS의 모든 투자 전략도 **51% Gate**를 통과해야 실전에 투입됩니다. "과거 데이터로 시뮬레이션해서 51% 이상 맞추지 못하면, 실전에서는 절대 쓰지 않는다"는 안전장치입니다.

### 51% Gate 통과 조건 — **[LOCK — 변경 불가]**

| 조건 | 기준값 | 쉬운 설명 |
|:--|:--|:--|
| **승률** | >= 51% | 100번 중 51번 이상 맞춰야 함 |
| **Sharpe Ratio** | >= 1.0 | 위험 대비 수익이 충분해야 함 |
| **Decay Rate** | < 30% | 학습 성적 대비 시험 성적이 30% 이상 떨어지면 안 됨 |
| **최소 거래 수** | >= 30건 | 최소 30번 이상 거래 샘플이 있어야 함 |
| **데이터 분할** | Train 70% / Test 30% | 과거 70%로 학습, 나머지 30%로 검증 |

> **승률 >= 51%는 LOCK (변경 불가)입니다.** 51% 미만인 전략은 어떤 경우에도 실전 투입할 수 없습니다.

[근거: AI_INVESTING_SPEC §6.1]

### 백테스팅 엔진 설정

```
수수료: 0.0 (Paper Trading이므로)
슬리피지: 0.0
무위험 수익률: 연 5%
분석 빈도: 일일 (1d)
대상: SPY, QQQ, BTC-USD (2018년 1월 1일 ~)
```

### Sharpe Ratio 공식 (수학적 검증 완료)

```
Sharpe = (평균수익률 - 무위험수익률) / 표본표준편차 × √252
```

- ddof=1: 표본 표준편차 사용 (통계학 정석)
- √252: 연율화 팩터 (1년 거래일 = 252일)
- **4차 크로스체크 완료 — 전건 정확** [LOCK]

[근거: AI_INVESTING_SPEC §6.2, §16.1]

### Decay Rate (과적합 감지 공식)

```
Decay = max(0, (Sharpe_Train - Sharpe_Test) / |Sharpe_Train|)
```

- Train(학습) 성적은 좋은데 Test(검증) 성적이 많이 떨어지면 → 과적합 (Overfitting) 의심
- Decay < 30% 이어야 통과

### 현재 결과

RSI_BB → 전 심볼 **INSUFFICIENT_SAMPLE** (데이터 부족). 파라미터 조정 또는 전략 추가로 Gate 통과를 목표로 합니다.

[근거: AI_INVESTING_SPEC §6.3]

**핵심 요약 (3줄)**
1. 51% Gate는 승률 51% 이상, Sharpe >= 1.0, Decay < 30%, 최소 30건을 모두 충족해야 통과하는 안전장치입니다 — **LOCK (변경 불가)**.
2. 백테스팅 엔진은 과거 데이터를 70/30으로 나누어 학습과 검증을 분리합니다.
3. 현재 RSI_BB 전략은 샘플 부족으로 Gate 미통과 상태이며, 데이터 확장과 파라미터 튜닝이 필요합니다.

---

## §29.5 Circuit Breaker (서킷 브레이커)

### 비유: 전기 차단기

집에서 전기가 과부하되면 차단기가 자동으로 내려가서 화재를 막듯, 투자에서도 시장이 급변하거나 손실이 커지면 **자동으로 거래를 중단**합니다. 감정에 휘둘려 더 큰 손실을 보는 것을 기계적으로 막아줍니다.

### Circuit Breaker 규칙 — **[LOCK — 변경 불가]**

| 규칙 | 임계값 | 동작 | 쉬운 설명 |
|:--|:--|:--|:--|
| 일일 손실 한도 | -3% | 당일 거래 중단 | 하루에 3% 이상 잃으면 그날은 멈춤 |
| VIX 임계 | > 40 | 매수 중단 | "공포 지수"가 40 넘으면 사지 않음 |
| 포지션 손실 | -10% | 강제 청산 | 한 종목이 10% 이상 빠지면 자동 매도 |
| 최소 현금 비율 | 20% | 신규 매수 차단 | 전체 자산의 20%는 항상 현금으로 보유 |
| 단일 종목 한도 | 10% | 추가 매수 차단 | 한 종목에 전체 자산의 10%까지만 투자 |

[근거: AI_INVESTING_SPEC §10.2, §22.4]

### Circuit Breaker 코드 구조

```python
class CircuitBreaker:
    RULES = {
        "daily_loss_limit": -0.03,      # 일일 -3%
        "position_stop_loss": -0.10,    # 포지션 -10%
        "vix_threshold": 40,            # VIX > 40
        "min_cash_ratio": 0.20,         # 현금 20%
        "max_position_size": 0.10,      # 단일 종목 10%
    }
```

### Grafana 알림 연동

| 상황 | 알림 채널 | 동작 |
|:--|:--|:--|
| 수집 실패 3회 | Slack | 수동 확인 요청 |
| Quarantine 10건 | 긴급 알림 | 데이터 품질 점검 |
| 승률 49% 이하 | 검토 알림 | 전략 재검토 |
| VIX > 40 | CB 가동 | 자동 매수 중단 |

[근거: AI_INVESTING_SPEC §11, §17.2 D-13]

**핵심 요약 (3줄)**
1. Circuit Breaker는 일일 손실 -3%, VIX > 40, 포지션 -10% 등 5가지 규칙으로 자동 거래 중단을 수행합니다.
2. 감정적 판단을 배제하고 기계적으로 손실을 제한하는 안전장치입니다.
3. Grafana 대시보드와 Slack 알림을 통해 실시간으로 상태를 모니터링합니다.

---

## §29.6 법적 제약 (Wash Sale, PDT, Uptick)

### 비유: 교통 법규

도로에서 신호등과 속도 제한을 지켜야 하듯, 주식 시장에도 반드시 지켜야 하는 법적 규칙이 있습니다. VAMOS는 이 규칙을 시스템에 내장하여, **위반하는 주문은 자동으로 차단**합니다.

### 3대 법적 제약 규칙

| 규칙 | 국가 | 내용 | 위반 시 동작 | 쉬운 설명 |
|:--|:--|:--|:--|:--|
| **Wash Sale Rule** | 미국 | 손실 매도 후 30일 내 재매수 금지 | 주문 차단 | 세금 혜택을 위해 일부러 팔았다가 바로 다시 사는 것을 금지 |
| **PDT Rule** | 미국 | $25,000 미만 계좌는 5영업일 내 3회 데이트레이딩 제한 | 주문 차단 | 소액 투자자의 과도한 단기 매매 제한 |
| **Uptick Rule** | 한국 | 공매도 (빌려서 파는 것)는 직전가 이상에서만 가능 | 주문 차단 | 주가 하락을 인위적으로 가속하는 것을 방지 |

> **법적 제약 우회 불가**: BASE LAYER 불변 원칙에 따라, Wash Sale/PDT/Uptick Rule은 어떤 경우에도 우회할 수 없습니다. **[LOCK — 변경 불가]**

[근거: AI_INVESTING_SPEC §10.1, §22.1~§22.2]

### Non-goal 강제 메커니즘 흐름

```
[사용자 요청]
    ↓
[Front Mini LLM] 의도/보안/도메인 판별
    ↓
[ORANGE CORE] Non-goal 체크
    ├── Non-goal 해당 → 차단 + 사유 안내
    └── Non-goal 미해당 → 다음 단계 진행
        ↓
[BLUE NODE] 실행
    ├── P0/P1 도메인 → 즉시 실행
    └── P2 (Trading) → 2단계 승인 요청 → 승인 시 실행
```

[근거: AI_INVESTING_SPEC §22.3]

**핵심 요약 (3줄)**
1. Wash Sale (30일 내 재매수 금지), PDT ($25K 미만 3회 제한), Uptick (공매도 가격 제한) 3가지 법적 규칙이 시스템에 내장되어 있습니다.
2. 이 규칙을 위반하는 주문은 자동으로 차단되며, 어떤 경우에도 우회할 수 없습니다 — **LOCK (변경 불가)**.
3. P2 Trading 도메인은 반드시 2단계 사용자 승인이 필요하며, 실거래 연결은 Non-goal (금지 사항)입니다.

---

## §29.7 데이터 스키마 (VAMOS_OHLCV_PLUS, VAMOS_EVENT)

### 비유: 데이터의 신분증 양식

병원에서 환자마다 같은 양식의 차트를 쓰듯, 투자 데이터도 통일된 양식(스키마)을 사용해야 합니다. VAMOS는 두 가지 핵심 양식 — **OHLCV_PLUS** (가격 데이터용)와 **EVENT** (이벤트 데이터용) — 을 정의합니다.

### VAMOS_OHLCV_PLUS (가격 데이터 스키마)

```json
{
  "entity_id": "SPY",                           // 종목 코드
  "timestamp_utc": "2026-02-03T00:00:00Z",      // 시간 (UTC)
  "timezone": "America/New_York",               // 시간대
  "data_type": "candle",                        // 데이터 유형
  "sequence_id": 0,                             // 순서 번호
  "values": {
    "open": "485.20",    // 시가 (문자열 — 소수점 정확도 보장)
    "high": "487.50",    // 고가
    "low": "484.10",     // 저가
    "close": "486.80",   // 종가
    "volume": "52341000", // 거래량
    "vwap": "485.90",    // 거래량가중평균가격
    "open_interest": null,
    "economic_value": null
  },
  "metadata": {
    "source": "yfinance",
    "confidence": 0.95,   // 신뢰도 (0~1)
    "frequency": "1d"     // 빈도 (일일)
  }
}
```

> **Decimal-safe 문자열**: 가격은 숫자가 아닌 **문자열**로 저장합니다. 컴퓨터에서 소수점 계산 시 미세한 오차가 발생할 수 있기 때문입니다 (예: 0.1 + 0.2 = 0.30000000000000004). **[LOCK]**

### data_type별 필수 필드

| data_type | 필수 필드 |
|:--|:--|
| candle (캔들/봉) | open, high, low, close, volume |
| tick (틱) | close, volume |
| economic (경제지표) | economic_value |
| onchain (블록체인) | close, volume |

### VAMOS_EVENT (이벤트 데이터 스키마)

```json
{
  "event_id": "evt_abc123",
  "timestamp_utc": "2026-02-03T14:30:00Z",
  "event_type": "news",          // 6가지 중 하나
  "sentiment_score": 0.65,       // 감성 점수 (-1.0 ~ 1.0)
  "impact_level": 3,             // 영향도 (1 ~ 5)
  "entities": ["AAPL", "MSFT"],  // 관련 종목
  "content": {
    "headline": "Apple announces new product launch",
    "summary": "Apple Inc. revealed plans for...",
    "url": "https://example.com/news/..."
  }
}
```

### event_type 6가지

| event_type | 쉬운 설명 |
|:--|:--|
| filing | 기업 공시 (예: SEC 보고서) |
| news | 뉴스 기사 |
| sentiment | 시장 감성 분석 결과 |
| corporate_action | 기업 활동 (배당, 분할 등) |
| reference_update | 참조 데이터 갱신 |
| kb_derived | Knowledge Base에서 파생된 이벤트 |

### 저장소 구조

| 저장소 | 용도 | 특징 |
|:--|:--|:--|
| **TimescaleDB** | OHLCV 시계열 데이터 | 시간 기반 자동 파티셔닝 |
| **ChromaDB** | 문서 임베딩 + RAG 검색 | 1024차원 벡터, BGE-M3 **[LOCK]** |
| **S3/MinIO** | 파일 저장 | raw/ (원본), quarantine/ (격리), backtest/ (결과), logs/ (로그) |

[근거: AI_INVESTING_SPEC §4.1~§4.3]

**핵심 요약 (3줄)**
1. VAMOS_OHLCV_PLUS는 가격 데이터, VAMOS_EVENT는 이벤트 데이터의 표준 양식(스키마)입니다.
2. 가격은 Decimal-safe 문자열로 저장하여 소수점 오차를 방지합니다 — **LOCK (변경 불가)**.
3. 데이터는 TimescaleDB (시계열), ChromaDB (벡터), S3/MinIO (파일) 3곳에 분산 저장됩니다.

---

## §29.8 Scraper Manager (17개 웹 스크래핑 대상)

### 비유: 인터넷 신문 스크랩 로봇

매일 아침 신문을 스크랩해서 중요 기사를 잘라내는 직원이 있다고 생각해보세요. Scraper Manager는 이 일을 자동으로 하는 로봇입니다. 17개 웹사이트에서 투자 관련 데이터를 자동으로 수집하되, **rate limiting** (요청 속도 제한)과 **robots.txt** (웹사이트의 "스크래핑 허용 규칙")를 준수합니다.

### 기술 스택

- **Playwright 기반 헤드리스 브라우저** (화면 없이 동작하는 웹 브라우저)
- 핵심 파일: `scraper_drift_handler.py`

### 핵심 기능 4가지

```
1. 정기 스크래핑      →  Cron (정해진 시간) 기반 자동 수집
2. Schema Drift 감지  →  웹 페이지 구조 변경 자동 탐지
3. LLM Fallback 파싱  →  구조 변경 시 AI가 새 구조 파악
4. 자동 재시도        →  실패 시 3회 재시도 → 실패 시 격리 (Quarantine)
```

### Schema Drift Detection (웹 구조 변경 감지)

웹사이트가 디자인을 바꾸면 기존 스크래핑이 깨집니다. Scraper Manager는 이를 자동으로 감지하고 대응합니다:

```
1단계: 기존 CSS 셀렉터 / XPath 실패 → Drift Alert (변경 감지!)
2단계: LLM에 페이지 HTML 전달 → 새 셀렉터 추출 시도 (AI가 새 구조 파악)
3단계: 실패 시 → S3 Quarantine 격리 → Grafana 알림 → 수동 검토
```

### 17개 대상 소스

| 등급 | 개수 | 대상 |
|:--|:--:|:--|
| **TIER-0 (Critical)** | 9개 | Goldman Sachs Insights, TradingView Ideas, SwaggyStocks, OptionStrat, Earnings Whispers, BamSEC, US Treasury Rates, OpenInsider, FINRA Short Interest |
| **TIER-1 (High)** | 8개 | FINRA OTC Transparency, Investing.com Earnings, Asian Bond Online, World Gov Bonds, ShortSqueeze, ETF.com Screener, Walter Bloomberg (X), LME Market Data |

[근거: AI_INVESTING_SPEC §21]

**핵심 요약 (3줄)**
1. Scraper Manager는 Playwright 기반으로 17개 웹사이트 (TIER-0 9개, TIER-1 8개)에서 데이터를 자동 수집합니다.
2. Schema Drift Detection으로 웹 구조 변경을 감지하고, LLM Fallback으로 자동 복구를 시도합니다.
3. rate limiting과 robots.txt를 준수하며, 실패 시 Quarantine 격리 → Grafana 알림 → 수동 검토 순서로 처리합니다.

---

## §29.9 ML/AI 스택 (FinBERT, LSTM, RL)

### 비유: AI 연구소의 전문 장비

투자 분석 회사 안에 AI 연구소가 있다고 생각해보세요. 이 연구소에는 여러 전문 장비가 있습니다 — 뉴스 감성을 읽는 장비 (FinBERT), 시계열 패턴을 학습하는 장비 (LSTM), 시행착오로 스스로 전략을 배우는 장비 (RL), 결정 이유를 설명해주는 장비 (SHAP/LIME).

### ML/AI 스택 구성

| 카테고리 | 기술 | 용도 | 쉬운 설명 |
|:--|:--|:--|:--|
| **딥러닝** | TensorFlow / PyTorch | LSTM, Transformer 모델 | 복잡한 패턴 학습 프레임워크 |
| **NLP (자연어처리)** | Hugging Face Transformers | FinBERT (ProsusAI/finbert) | 금융 뉴스의 긍정/부정 판단 |
| **ML (기계학습)** | scikit-learn | 분류/회귀 기본 | 기본적인 예측 모델 |
| **부스팅** | XGBoost, LightGBM | 그래디언트 부스팅 | 표 형태 데이터에 강력한 예측 |
| **강화학습** | Stable-Baselines3 | PPO, DQN 에이전트 | 시행착오로 최적 매매 학습 |
| **설명가능성** | SHAP, LIME | AI 결정 해석 | "왜 이렇게 결정했는지" 설명 |

[근거: AI_INVESTING_SPEC §15]

### 각 모델의 역할

**FinBERT** (금융 특화 자연어처리):
- 뉴스 기사를 읽고 긍정/부정/중립 감성 점수를 매김
- 예: "Apple announces record earnings" → 긍정 (0.85)
- Phase 3 (1-2개월 내) 도입 예정

**LSTM** (Long Short-Term Memory, 장단기 기억 네트워크):
- 시계열 데이터 (주가 흐름)의 패턴을 학습
- 내일/다음 주 가격 방향을 예측
- Phase 4 (3-6개월 내) 도입 예정, 목표: 방향 예측 정확도 > 55%

**RL** (Reinforcement Learning, 강화학습):
- 게임하듯 시행착오를 반복하며 최적의 매매 전략을 스스로 학습
- PPO (Proximal Policy Optimization), DQN (Deep Q-Network) 알고리즘 사용
- Phase 4 (3-6개월 내) 실험 예정

### ML 전용 데이터 소스 우선순위

| 순위 | 소스 | 데이터 유형 |
|:--:|:--|:--|
| 1 | yfinance | 미국 주식 OHLCV |
| 2 | Alpha Vantage | 글로벌 주식, 환율 |
| 3 | Polygon.io | 실시간 + 히스토리 |
| 4 | KRX Open API | 한국 주식 |
| 5 | FRED | 거시경제 지표 |
| 6 | ccxt | 암호화폐 |
| 7 | finnhub | 뉴스, 감성 |

[근거: AI_INVESTING_SPEC §15.1]

**핵심 요약 (3줄)**
1. ML/AI 스택은 FinBERT (뉴스 감성), LSTM (가격 예측), RL (자율 학습), XGBoost (부스팅) 등으로 구성됩니다.
2. SHAP/LIME으로 AI 결정의 이유를 설명할 수 있어, 블랙박스 문제를 해결합니다.
3. ML 모델은 Phase 3~4 (1-6개월)에 순차 도입 예정이며, 7개 데이터 소스를 우선순위에 따라 활용합니다.

---

## §29.10 Real-Time News 연동 (RT-BNP ↔ Investing)

### 비유: 속보 뉴스 즉시 전달

TV 뉴스 속보가 나오면 즉시 투자 판단에 반영하듯, VAMOS는 실시간 뉴스와 이벤트를 즉시 전략 엔진에 전달합니다.

### 실시간 Stream Gateway 아키텍처

```
[외부 데이터 소스] → WebSocket → Kafka Topic → Consumer → TimescaleDB
```

### 지원 소스

| 소스 | 데이터 유형 | 상태 |
|:--|:--|:--|
| Etherscan | 블록 이벤트 (온체인) | 구현 완료 |
| 거래소 실시간 호가 | 주가/체결 | 향후 확장 |

### 실시간 이벤트 처리 흐름

```
[Etherscan WebSocket] 대규모 전송 감지
    ↓
[Stream Gateway] Kafka로 전달
    ↓
[Consumer] VAMOS_EVENT 변환 (event_type: "onchain", impact_level: 4)
    ↓
[Strategy Engine] 이벤트 기반 전략 평가
    ↓
(현재 이벤트 기반 전략 미구현 — DEFER)
```

### Airflow DAG 스케줄링 (일일 배치)

```
06:00 fetch_market_data   →  데이터 수집
06:05 validate            →  검증
06:10 transform           →  변환
06:15 store               →  저장
06:20 strategy            →  전략 실행
06:25 legal_check         →  법적 검증
06:30 signals             →  신호 생성
06:35 orders              →  주문 실행
```

| 처리 유형 | 시간 | 설명 |
|:--|:--|:--|
| 일일 배치 | 06:00 UTC | 메인 파이프라인 |
| 실시간 스트림 | 장중 | WebSocket 기반 |
| 웹 스크래핑 | 소스별 | TIER-0/TIER-1 |
| 문서 갱신 | 이벤트 기반 | KB 업데이트 시 |

[근거: AI_INVESTING_SPEC §12, §13]

**핵심 요약 (3줄)**
1. Stream Gateway는 WebSocket → Kafka → TimescaleDB 구조로 실시간 데이터를 처리합니다.
2. 현재 Etherscan 블록 이벤트만 구현 완료이며, 거래소 실시간 호가는 향후 확장 예정입니다.
3. 일일 배치 (06:00 UTC)와 실시간 스트림이 병행 운영되며, Airflow가 스케줄링을 담당합니다.

---

## §29.11 VAMOS CORE 통합 (I-2, I-6, I-8, I-9, I-18)

### 비유: 본사 부서와의 업무 연결

투자 분석팀(AI Investing)이 독립적으로 일하는 것이 아니라, 본사(VAMOS CORE)의 여러 부서와 유기적으로 연결되어 있습니다. 감사팀(I-6)이 결과를 검증하고, 정책팀(I-8)이 승인하고, 재무팀(I-9)이 비용을 관리합니다.

### VAMOS AI 기능 → 투자 시스템 매핑

| VAMOS AI 기능 | 모듈 ID | 투자 시스템 적용 | 쉬운 설명 |
|:--|:--|:--|:--|
| **RAG** (검색증강생성) | I-2 | 과거 거래 패턴, 시장 뉴스 검색 | 과거 데이터에서 관련 정보를 찾아주는 도서관 사서 |
| **Self-check Engine** (자기검증) | I-6 | 전략 결과 검증, 환각 방지 | AI가 자기 답을 다시 확인하는 감사관 |
| **Policy Engine** (정책엔진) | I-8 | P2 도메인 승인 강제, 실거래 차단 | 규정 준수를 감시하는 정책팀 |
| **Cost Manager** (비용관리) | I-9 | LLM 호출 비용 추적 (V1/V2/V3) | 예산 초과를 막는 재무팀 |
| **Self-evo Engine** (자기진화) | I-18 | 실패 전략 분석 → 파라미터 개선 제안 | 실패에서 배우는 학습 시스템 |
| 메모리 관리 | I-3 | 프로젝트별 거래 이력 독립 저장 | 각 프로젝트 전용 파일함 |
| **Self-check Engine** (검증 로그) | S-1 | 투자 의사결정 검증 결과 기록 · 감사 추적 | 검증 결과를 기록하는 감사 일지 |

> **[PART1 SP-03]** 모듈 ID는 D2.0-01 정본(CLAUDE.md §6) 기준. I-7=Project/Session Manager, I-8=Policy Engine, I-9=Cost Manager.

[근거: AI_INVESTING_SPEC §20.2]

### 아키텍처 연동 구조

```
VAMOS AI (ORANGE CORE)
       │
       ├── 정책 관리: 비용 상한 (V1: 4만원/월)
       ├── 승인 관리: P2 Trading 2단계 승인
       ├── Self-evo: 전략 개선 제안 (적용은 사용자 승인)
       │
       ▼
BLUE NODE: Trading/Quant
       │
       ├── 데이터 파이프라인 (83개 소스)
       ├── 전략 엔진 (RSI_BB, MAX_PAIN 등)
       ├── 백테스팅 엔진 (51% Gate)
       ├── 법적 제약 검증
       └── 신호 생성 → 주문 실행 (Paper/Real)
```

### 도메인 우선순위

| 등급 | 도메인 | 설명 | Self-evo 변경 |
|:--|:--|:--|:--|
| **P0** | Dev/System, Research, Productivity | 핵심 | 불가 |
| **P1** | Content, Data & Quant | 확장 | 승인 후 활성화 |
| **P2** | Trading Strategy | 위험 | **2단계 승인 필수**, 실거래 금지 |

### VAMOS AI vs 기존 플랫폼 차별화

| 기존 플랫폼 | VAMOS AI |
|:--|:--|
| 투자만 집중 | 범용 AGI 프레임워크 + 투자 모듈 |
| 단일 AI | Multi-Agent 협업 (5개 AI 분업) |
| 블랙박스 | Self-check + 근거 기반 출력 |
| 자동 실행 | Human-in-the-loop (P2 2단계 승인) |
| 비용 무제한 | 비용 상한 관리 (V1/V2/V3) |

### 통합 로드맵

| Phase | 기간 | 작업 내용 |
|:--|:--|:--|
| **A** | 1주 | 연동 인터페이스 정의 (Trading Node 스키마, 통신 규약, P2 승인 플로우) |
| **B** | 2-3주 | AI INVESTING 완성 (contracts.py 정렬, Docker, PoC 검증) |
| **C** | 4-6주 | VAMOS CORE 최소 기능 (I-6, I-7, I-8, I-9) |
| **D** | 2-3개월 | 통합 운영 (Trading Node 연결, Self-evo, 대시보드) |

[근거: AI_INVESTING_SPEC §20.3~§20.5]

**핵심 요약 (3줄)**
1. AI Investing은 VAMOS CORE의 I-2(RAG), I-6(Self-check), I-8(Policy), I-9(Cost), I-18(Self-evo) 모듈과 연동됩니다.
2. P2 Trading 도메인은 반드시 2단계 사용자 승인이 필요하며, 실거래 연결은 금지입니다.
3. 기존 플랫폼과 달리 Multi-Agent 협업, Self-check, Human-in-the-loop, 비용 상한 관리를 제공합니다.

---

## §29.12 ★Walk-Forward Validation & Z-Session — GAP-12

### 비유: 모의고사를 여러 번 치르며 실력 확인

수능 대비로 모의고사를 한 번만 치르면 운이 좋았는지 실력인지 알 수 없습니다. Walk-Forward Validation은 **시험지를 계속 바꿔가며 여러 번 모의고사를 치르는** 것입니다. 그리고 Z-Session은 **돈 한 푼 안 걸고 진행하는 완전 무위험 시뮬레이션**입니다.

### Walk-Forward Validation (걸어가며 검증하기)

기존 백테스팅 (Train 70% / Test 30%)의 한계를 보완하는 방법론입니다.

```
기존 방법 (단일 분할):
[=======Train 70%=======][===Test 30%===]
→ 한 번의 결과에 운이 개입할 수 있음

Walk-Forward (여러 번 분할):
[===Train===][=Test=]
    [===Train===][=Test=]
        [===Train===][=Test=]
            [===Train===][=Test=]
→ 여러 구간에서 반복 검증 → 진짜 실력 확인
```

| 항목 | 기존 백테스팅 | Walk-Forward |
|:--|:--|:--|
| 검증 횟수 | 1회 | N회 (여러 번) |
| 과적합 위험 | 높음 | 낮음 |
| 실전 괴리 | 클 수 있음 | 줄어듦 |
| 신뢰도 | 보통 | 높음 |

### Z-Session: 제로 리스크 시뮬레이션

**Z-Session**은 암호화폐 자동 트레이딩 전략 생성/실행/관리 시스템입니다. "실제 돈을 걸지 않고" 전략의 성능을 검증합니다.

| 항목 | 내용 |
|:--|:--|
| 정의 | 심볼 단위 점수화 → 전략 독립 생성/분석 → 분산 매매 시뮬레이션 |
| 최신 버전 | v3.6 |
| 지원 심볼 | BTCUSDT, ETHUSDT, SOLUSDT, ARBUSDT, LINKUSDT, MATICUSDT, OPUSDT |
| 전략 파일 | 56개+ 생성 |
| 현재 성과 | 승률 61.8%, PF 1.74, 기대값 2.3, MDD 6.9% |
| 판단 | **keep** (유지) |

### Z-Session 세션(단계) 구조

| 세션 | 명칭 | 역할 | 비유 |
|:--|:--|:--|:--|
| **A** | 전략 설계 및 분석 | 심볼 분석, 점수화, 전략 설계 | 투자 리서치 |
| **B** | 전략 코드 생성 | 기술적 지표 → Pine Script 자동 생성 | 코드 개발 |
| **C** | 전략 검증/시뮬레이션 | 자산 분산 백테스트, 리스크 분석 | 모의 시험 |
| **D** | 자동화 연동 | AlertCondition, JSON 웹훅, 실행 기록 | 자동화 셋업 |
| **E** | 고급 필터링 | 온체인, SMC, 엘리엇 파동, 하모닉 | 정밀 분석 |
| **F** | 대시보드/시각화 | 백테스트 결과, 실시간 포지션, 수익률 | 관제 센터 |
| **G** | 비전 분석 | 차트 이미지 패턴 인식 (GPT Vision) | 눈으로 차트 보기 |
| **Q** | 오류 처리 | Pine Script 오류 감지 + AI 수정 | 버그 수정 |
| **X** | 전략 재생성 | 실패 전략 재생성 루프 | 재도전 |

### 타임프레임별 전략 분산

| 프레임 | 분석 범위 | 전략 성격 | 거래소 |
|:--|:--|:--|:--|
| 15m | 단기/초단타 | 고속 매수매도 | Binance |
| 1h~4h | 중단기 트렌드 | 스윙 트레이딩 | Bybit |
| 12h~1d | 중장기 추세 | 추세 추적형 | OKX |
| 3d~1w | 장기 투자 | 포트폴리오 기반 | Bitget |

### 전략 성능 기준

| 지표 | 기준 | 설명 |
|:--|:--|:--|
| 승률 | > 60% | 우수 전략 |
| PF (Profit Factor) | >= 1.5 | 수익이 손실의 1.5배 이상 |
| 기대값 (EV) | > 0.2 | 거래당 평균 수익 |
| MDD (최대낙폭) | < 10% | 최고점에서 최대 10%까지만 하락 허용 |

판단: **keep** (유지) / **hold** (보류) / **exclude** (제외)

[근거: AI_INVESTING_SPEC §17, §24]

**핵심 요약 (3줄)**
1. Walk-Forward Validation은 데이터를 여러 구간으로 나누어 반복 검증함으로써 과적합 위험을 줄이는 방법론입니다.
2. Z-Session (v3.6)은 실제 돈 없이 전략을 검증하는 제로 리스크 시뮬레이션으로, 현재 승률 61.8%, PF 1.74 성과를 보입니다.
3. A~G+Q+X 9개 세션으로 전략 설계부터 재생성까지 전 과정을 자동화합니다.

---

## §29.13 ★참조 플랫폼 35개 & 알려진 결함 15개 — GAP-12

### 비유: 경쟁사 분석 & 자기 진단

새 회사를 차릴 때 경쟁사 35곳을 분석하고, 자기 회사의 약점 15가지를 정리하는 것과 같습니다. VAMOS는 이 분석을 바탕으로 장점은 벤치마킹하고, 약점은 로드맵에 따라 체계적으로 극복합니다.

### 참조 플랫폼 35개 — 3개 카테고리

#### 주식/ETF 중심 플랫폼 (15개)

| # | 플랫폼 | 주요 기능 | VAMOS 적용 포인트 | 비용 |
|:--|:--|:--|:--|:--|
| 1 | **QuantConnect** | 오픈소스 LEAN 엔진 | 백테스팅 아키텍처 참고 | $0-60/월 |
| 2 | **Trade Ideas** | Holly AI, 실시간 스캔 | Self-evo 시뮬레이션 | $167/월 |
| 3 | **Alpaca** | 수수료 무료 API | REST API 설계 참고 | 무료 |
| 4 | **Composer** | No-code 전략 빌더 | UI/UX Builder View | $50/월 |
| 5 | **TradingView** | 최고의 차트, 소셜 | 차트 시각화 참고 | $12-60/월 |
| 6 | **Kavout** | Kai Score AI 점수화 | 종목 스코어링 | 문의 |
| 7 | **LevelFields** | 이벤트 기반 AI | Event-Driven 전략 | $49/월 |
| 8 | **Tickeron** | AI 패턴 인식 | 차트 패턴 자동 탐지 | $15-200/월 |
| 9 | **Danelfin** | AI 종목 스코어 | Factor 기반 점수화 | $60/월 |
| 10 | **Stock Hero** | 클라우드 봇 | 모바일 UX 참고 | $40/월 |
| 11 | **Capitalise.ai** | 자연어 전략 작성 | NLP 전략 생성 | 무료-49/월 |
| 12 | **VectorVest** | 매수/매도/보유 점수 | 신호 시스템 참고 | $69/월 |
| 13 | **Ziggma** | 포트폴리오 분석 | 대시보드 참고 | 무료-30/월 |
| 14 | **Portfolio123** | 팩터 백테스팅 | Factor Investing 엔진 | $83-250/월 |
| 15 | **FinBrain** | AI 가격 예측 | ML 예측 모델 참고 | $29-99/월 |

#### 암호화폐 중심 플랫폼 (12개)

| # | 플랫폼 | 주요 기능 | VAMOS 적용 포인트 | 비용 |
|:--|:--|:--|:--|:--|
| 16 | **Cryptohopper** | 멀티 전략 블렌딩 | 전략 앙상블 방식 | $19-99/월 |
| 17 | **3Commas** | DCA, Grid, Signal Bot | 다양한 봇 유형 참고 | $49/월 |
| 18 | **Pionex** | 18개 무료 봇 | Grid Trading 구현 | 무료 |
| 19 | **TradeSanta** | 간편 Long/Short | 사용자 친화적 UI | $18-45/월 |
| 20 | **Zignaly** | 시그널 복사 거래 | Copy Trading | 무료 |
| 21 | **Bitsgap** | 아비트라지 봇 | 아비트라지 로직 | $29-149/월 |
| 22 | **HaasOnline** | 고급 스크립팅 | 커스텀 전략 언어 | $7.50-30/월 |
| 23 | **Coinrule** | If-Then 규칙 | 규칙 엔진 설계 | 무료-450/월 |
| 24 | **Shrimpy** | 자동 리밸런싱 | 리밸런싱 로직 | $15-63/월 |
| 25 | **Quadency** | 통합 대시보드 | 멀티 거래소 통합 | 무료-99/월 |
| 26 | **WunderTrading** | TradingView 연동 | 외부 신호 통합 | 무료-39/월 |
| 27 | **Altrady** | 스마트 거래 터미널 | 거래 터미널 UX | $17-50/월 |

#### 기관/전문가 플랫폼 (8개)

| # | 플랫폼 | 주요 기능 | VAMOS 적용 포인트 | 비용 |
|:--|:--|:--|:--|:--|
| 28 | **Kensho** | S&P Global 소유, NLP | 기관급 NLP 참고 | 엔터프라이즈 |
| 29 | **Bloomberg Terminal** | 업계 표준 데이터 | 데이터 표준화 | $24,000/년 |
| 30 | **Refinitiv Eikon** | Reuters 데이터 | 대체 데이터 소스 | $22,000/년 |
| 31 | **Numerai** | 크라우드소싱 헤지펀드 | 토너먼트 모델 | 무료 |
| 32 | **Quantopian (Archive)** | 교육 자료 | 오픈소스 Zipline | 종료 |
| 33 | **Hudson & Thames** | 학술 논문 구현 | mlfinlab 라이브러리 | $799/년 |
| 34 | **WorldQuant** | 알파 팩터 연구 | 팩터 연구 방법론 | 채용 |
| 35 | **Two Sigma** | ML 기반 헤지펀드 | ML 아키텍처 참고 | 기관 |

> **AI 투자 시장 규모**: 2024년 $23.48B → 2034년 $75.5B (연평균 성장률 20.7%)

[근거: AI_INVESTING_SPEC §19]

### 도입 우선순위

| 우선순위 | 플랫폼 | 참고 대상 |
|:--|:--|:--|
| **P0-P1 (필수/권장)** | QuantConnect, Alpaca, 3Commas, TradingView | 백테스팅, API, 봇, 차트 |
| **P2 (장기)** | Trade Ideas, Composer, Cryptohopper | Holly AI, No-code, 전략 마켓 |
| **P3 (참고)** | Hudson & Thames, Numerai, Kensho | 학술, 토너먼트, NLP |

### 알려진 결함 15개

| # | 카테고리 | 심각도 | 상세 | 극복 방안 |
|:--|:--|:--:|:--|:--|
| D-01 | 전략 다양성 부족 | High | RSI_BB만 구현 | MACD, MA 추가 (2주) |
| D-02 | API 단일 의존성 | High | yfinance 장애 시 전체 중단 | Fallback Chain (2주) |
| D-03 | 실시간 처리 미흡 | Medium | 일일 배치 중심 | WebSocket 확장 |
| D-04 | 감성 분석 부재 | Medium | 뉴스/SNS 미반영 | FinBERT 통합 (3주) |
| D-05 | 포트폴리오 관리 없음 | High | 자산 배분 로직 부재 | Kelly Criterion |
| D-06 | 백테스팅 샘플 부족 | Medium | INSUFFICIENT_SAMPLE | 데이터 3년→5년 |
| D-07 | 옵션/파생 데이터 미확보 | Medium | MAX_PAIN 불가 | 옵션 API 확보 |
| D-08 | 거시경제 데이터 미연동 | Medium | MACRO_ROTATION 불가 | FRED 연동 |
| D-09 | 다중 자산 미지원 | Medium | 주식만 | 암호화폐/FX 확장 |
| D-10 | contracts.py 불일치 | High | JSON Schema 12건 불일치 | 즉시 정렬 (P0) |
| D-11 | 환경 미구축 | High | Docker, API 키 미확보 | Docker Compose (1주) |
| D-12 | 슬리피지/수수료 실측 부족 | Medium | 백테스트 vs 실전 괴리 | 실측 데이터 수집 |
| D-13 | Black Swan 대응 없음 | High | 급락/Flash Crash 방어 부재 | Circuit Breaker (1주) |
| D-14 | Model Explainability 부재 | Medium | AI 결정 근거 불투명 | SHAP/LIME (3주) |
| D-15 | A/B 테스트 체계 없음 | Low | 전략 변경 효과 측정 어려움 | A/B 프레임워크 |

### 극복 일정 요약

| 단점 | 방안 | 기간 |
|:--|:--|:--|
| D-10 contracts.py | 12건 정렬 | 즉시 |
| D-11 환경 | Docker Compose | 1주 |
| D-01 전략 | MACD, MA 추가 | 2주 |
| D-02 API | Fallback Chain | 2주 |
| D-06 샘플 | 데이터 3년→5년 | 1주 |
| D-04 감성 | FinBERT 통합 | 3주 |
| D-13 Black Swan | Circuit Breaker | 1주 |
| D-14 Explainability | SHAP/LIME | 3주 |

[근거: AI_INVESTING_SPEC §17, §19]

**핵심 요약 (3줄)**
1. 35개 참조 플랫폼을 주식/ETF(15), 암호화폐(12), 기관(8) 카테고리로 분석하여 벤치마킹합니다.
2. 15개 알려진 결함 중 D-10(contracts.py 12건 불일치)과 D-11(환경 미구축)이 최우선 해결 대상입니다.
3. Phase 1~4 로드맵에 따라 즉시(1-2주)부터 장기(3-6개월)까지 체계적으로 결함을 극복합니다.

---

## §29 전체 검증 체크리스트

| # | 검증 항목 | 상태 | 해당 섹션 |
|:--|:--|:--:|:--|
| 1 | 7-Layer 아키텍처 | ✅ | §29.1 |
| 2 | 83개 소스 카테고리별 | ✅ | §29.2 |
| 3 | 96개 전략 카테고리별 | ✅ | §29.3 |
| 4 | 51% Gate LOCK | ✅ | §29.4 |
| 5 | Circuit Breaker | ✅ | §29.5 |
| 6 | 법적 제약 3가지 | ✅ | §29.6 |
| 7 | ML 스택 | ✅ | §29.9 |
| 8 | ★Walk-Forward GAP-12 | ✅ | §29.12 |
| 9 | ★참조 플랫폼 35개 GAP-12 | ✅ | §29.13 |
| 10 | 비유 설명 포함 | ✅ | 전 섹션 |
| 11 | 근거 SOT 참조 표기 | ✅ | 전 섹션 |
