# COND-103: FinGPT 금융AI — L2+ 상세 명세

> **모듈 ID**: COND-103
> **카테고리**: CAT-A (AI/ML Engine)
> **이름**: FinGPT 금융AI
> **우선순위**: MEDIUM
> **Phase**: Phase 0
> **L-Level**: L2+ (Performance Benchmark·Integration Test Spec은 Phase 1/2 보강)
> **LOCK 준수**: LOCK-CD-03 BaseModule ABC, LOCK-CD-04 Runnable, LOCK-CD-05 ErrorHandlingStandard, LOCK-CD-06 VamosError 필드, LOCK-CD-10 ModuleConfig

---

## E1. Input Schema

```python
from pydantic import BaseModel, Field
from typing import Literal, Optional

class FinancialContext(BaseModel):
    """금융 컨텍스트"""
    ticker: str = Field(..., description="종목 티커 (e.g., AAPL, 005930.KS)")
    timeframe: Literal["1d", "1w", "1m", "3m", "6m", "1y", "3y"] = Field(
        default="1m", description="분석 기간"
    )
    data_sources: list[Literal["sec_filing", "earnings_call", "news", "social", "analyst_report"]] = Field(
        default=["news", "sec_filing"],
        description="분석에 사용할 데이터 소스"
    )
    market: Optional[Literal["US", "KR", "JP", "CN", "EU"]] = Field(
        default=None, description="시장 구분"
    )
    include_peers: bool = Field(default=False, description="동종 업계 비교 포함 여부")

class FinGptRequest(BaseModel):
    """COND-103 입력 스키마"""
    query: str = Field(
        ..., description="금융 분석 질의"
    )
    financial_context: FinancialContext = Field(
        ..., description="금융 컨텍스트 정보"
    )
    task: Literal["sentiment", "analysis", "research"] = Field(
        default="analysis",
        description="수행할 금융 AI 태스크"
    )
    depth: Literal["quick", "standard", "deep"] = Field(
        default="standard",
        description="분석 깊이"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "애플의 최근 실적 발표를 분석하고 투자 전망을 제시하세요.",
                "financial_context": {
                    "ticker": "AAPL",
                    "timeframe": "3m",
                    "data_sources": ["sec_filing", "earnings_call", "news"],
                    "market": "US",
                    "include_peers": True
                },
                "task": "analysis",
                "depth": "standard"
            }
        }
```

---

## E2. Output Schema

```python
class SourceRef(BaseModel):
    source_type: Literal["sec_filing", "earnings_call", "news", "social", "analyst_report"]
    title: str = Field(description="출처 제목")
    url: Optional[str] = Field(default=None, description="출처 URL")
    date: str = Field(description="출처 날짜 (ISO 8601)")
    relevance_score: float = Field(ge=0.0, le=1.0, description="관련도 점수")

class FinancialAnalysis(BaseModel):
    summary: str = Field(description="분석 요약")
    key_findings: list[str] = Field(description="핵심 발견 사항")
    risk_factors: list[str] = Field(default_factory=list, description="리스크 요인")
    recommendation: Optional[Literal["strong_buy", "buy", "hold", "sell", "strong_sell"]] = Field(
        default=None, description="투자 의견 (research 태스크에서만)"
    )
    confidence: float = Field(ge=0.0, le=1.0, description="분석 신뢰도")

class FinGptResponse(BaseModel):
    """COND-103 출력 스키마"""
    analysis: FinancialAnalysis = Field(
        description="금융 분석 결과"
    )
    sentiment_score: float = Field(
        ge=-1.0, le=1.0,
        description="심리 점수 (-1: 극도 부정, 0: 중립, +1: 극도 긍정)"
    )
    sources: list[SourceRef] = Field(
        description="참조 출처 리스트"
    )
    execution_time_ms: int = Field(description="실행 시간 (밀리초)")

    class Config:
        json_schema_extra = {
            "example": {
                "analysis": {
                    "summary": "애플은 최근 분기에 매출 948억 달러를 기록하며 시장 예상을 상회했습니다.",
                    "key_findings": [
                        "서비스 부문 매출이 전년 대비 14% 성장",
                        "iPhone 매출은 소폭 감소했으나 ASP 상승으로 상쇄",
                        "자사주 매입 200억 달러 추가 승인"
                    ],
                    "risk_factors": [
                        "중국 시장 경쟁 심화",
                        "반독점 규제 리스크"
                    ],
                    "recommendation": "buy",
                    "confidence": 0.82
                },
                "sentiment_score": 0.65,
                "sources": [
                    {
                        "source_type": "sec_filing",
                        "title": "Apple Inc. 10-Q Filing Q1 2026",
                        "url": "https://sec.gov/...",
                        "date": "2026-02-01",
                        "relevance_score": 0.95
                    }
                ],
                "execution_time_ms": 4500
            }
        }
```

---

## E3. Algorithm Pseudocode

```
FUNCTION execute(request: FinGptRequest) -> FinGptResponse:
    # 1. 티커 유효성 검증
    ticker_info = TickerRegistry.lookup(request.financial_context.ticker)
    IF ticker_info is None:
        RETURN Err(VamosError("COND_103_TICKER_NOT_FOUND", ...))

    # 2. 데이터 소스 수집
    collected_data = {}
    FOR source IN request.financial_context.data_sources:
        TRY:
            IF source == "sec_filing":
                data = SECFilingParser.fetch(ticker_info, request.financial_context.timeframe)
            ELIF source == "earnings_call":
                data = EarningsCallParser.fetch(ticker_info, request.financial_context.timeframe)
            ELIF source == "news":
                data = NewsAggregator.fetch(ticker_info, request.financial_context.timeframe)
            ELIF source == "social":
                data = SocialSentimentCollector.fetch(ticker_info)
            ELIF source == "analyst_report":
                data = AnalystReportParser.fetch(ticker_info)
            collected_data[source] = data
        CATCH DataSourceError:
            log_warning(f"Data source {source} unavailable")
            IF len(collected_data) == 0 AND source == request.financial_context.data_sources[-1]:
                RETURN Err(VamosError("COND_103_DATA_SOURCE_UNAVAILABLE", ...))

    # 3. 태스크별 처리
    IF request.task == "sentiment":
        # 심리 분석 — 뉴스/소셜 중심
        sentiment_result = FinGptSentimentModel.analyze(collected_data, ticker_info)
        analysis = build_sentiment_analysis(sentiment_result)

    ELIF request.task == "analysis":
        # 재무 분석 — SEC 파일링 + 실적 중심
        financial_entities = FinancialNER.extract(collected_data)
        analysis = FinGptAnalysisModel.analyze(
            entities=financial_entities,
            context=request.financial_context,
            depth=request.depth
        )

    ELIF request.task == "research":
        # 투자 리서치 — 종합 분석 + 투자 의견
        financial_entities = FinancialNER.extract(collected_data)
        IF request.financial_context.include_peers:
            peer_data = PeerComparison.analyze(ticker_info)
            financial_entities.merge(peer_data)
        analysis = FinGptResearchModel.generate(
            entities=financial_entities,
            context=request.financial_context,
            depth=request.depth
        )

    # 4. 심리 점수 산출
    sentiment_score = compute_aggregate_sentiment(collected_data, analysis)

    # 5. 출처 참조 구성
    sources = build_source_refs(collected_data, relevance_threshold=0.3)
    sources.sort(key=lambda s: s.relevance_score, reverse=True)

    RETURN Ok(FinGptResponse(
        analysis=analysis,
        sentiment_score=sentiment_score,
        sources=sources,
        execution_time_ms=elapsed_ms()
    ))
```

---

## E4. Error Handling

> LOCK (D2.0-02 §0.3): `Result<T, VamosError>`, 예외 throw 금지

| FailureCode | 조건 | fallback_id | 사용자 메시지 |
|-------------|------|------------|--------------|
| `COND_103_DATA_SOURCE_UNAVAILABLE` | 모든 요청 데이터 소스가 접근 불가 | `F-103-01` | "금융 데이터 소스에 접근할 수 없습니다." |
| `COND_103_TICKER_NOT_FOUND` | 지정된 티커가 레지스트리에 없음 | `F-103-02` | "해당 종목 티커를 찾을 수 없습니다." |
| `COND_103_ANALYSIS_TIMEOUT` | 분석이 timeout_ms 내에 완료되지 않음 | `F-103-03` | "금융 분석 시간이 초과되었습니다. 분석 깊이를 줄여 주세요." |
| `COND_103_SENTIMENT_PARSE_FAILED` | 심리 분석 모델 파싱 실패 | `F-103-04` | "심리 분석 결과를 해석할 수 없습니다." |
| `COND_103_SEC_FILING_ERROR` | SEC 파일링 파서 오류 또는 형식 불일치 | `F-103-05` | "SEC 공시 문서 처리 중 오류가 발생했습니다." |

### VamosError 구조
```python
VamosError(
    failure_code="COND_103_TICKER_NOT_FOUND",
    message="Ticker not found in registry: INVALID_TICKER",
    fallback_id="F-103-02",
    trace_id=context.trace_id
)
```

---

## E5. Dependency Map

> §A 의존성 매트릭스 (P0-1 산출물) 반영

### CAT-A 내부 의존 (§A.2.1)
| 관계 | 의존 모듈 | 의존 내용 | 추출 기준 |
|------|-----------|----------|----------|
| — | — | **완전 독립** (Level 0) — CAT-A 내부 의존 없음 | — |

### I-Series 소비 (§A.2.4)
| I-Module | 용도 | 공통/추가 |
|----------|------|----------|
| I-1 (Intent) | 의도 해석 | 공통 (26개 전체) |
| I-5 (Decision) | 라우팅/결정 | 공통 |
| I-6 (Self-check) | 자기 검증 | 공통 |
| I-9 (Logging) | 로깅 | 공통 |
| **I-8 (Cost)** | LLM 추론 비용 관리 | **추가** |

### 외부 라이브러리
| 라이브러리 | 버전 | 용도 |
|-----------|------|------|
| `fingpt` | ≥0.3 | FinGPT 프레임워크 |
| `transformers` | ≥4.40 | 모델 로딩/추론 |
| `sec-edgar-downloader` | ≥5.0 | SEC 공시 다운로드 |
| `yfinance` | ≥0.2 | 시장 데이터 조회 |
| `spacy` | ≥3.7 | Financial NER |
| `beautifulsoup4` | ≥4.12 | 문서 파싱 |

### 인프라
| 인프라 | 용도 |
|--------|------|
| GPU (권장) | FinGPT 추론 가속 |
| 메모리 ≥ 8GB | 모델 가중치 + 데이터 버퍼 |
| 인터넷 연결 | SEC EDGAR, 뉴스 API, 시장 데이터 접근 |

---

## E6. Performance Benchmark

> Phase 1 보강 예정

| 메트릭 | 기준 | 측정 방법 |
|--------|------|----------|
| **Sentiment 분석** | ≤ 3,000ms | 뉴스 10건 + 소셜 50건 기준 |
| **Standard 분석** | ≤ 10,000ms | SEC 파일링 1건 + 뉴스 10건 |
| **Deep 분석 (research)** | ≤ 30,000ms | 전체 소스 + 피어 비교 포함 |
| **데이터 수집** | ≤ 5,000ms | 단일 데이터 소스 당 |
| **심리 점수 정확도** | ≥ 0.75 F1 | 레이블링된 검증 데이터셋 |
| **NER 정확도** | ≥ 0.85 F1 | 금융 엔티티 추출 |

---

## E7. Integration Test Spec

> Phase 2 보강 예정

### 시나리오 1: 기본 심리 분석
```yaml
name: "fingpt_sentiment_analysis"
setup:
  - mock_data_source("news", ticker="AAPL", articles=10)
  - mock_data_source("social", ticker="AAPL", posts=50)
input:
  query: "애플 주식에 대한 시장 심리를 분석하세요."
  financial_context:
    ticker: "AAPL"
    timeframe: "1w"
    data_sources: ["news", "social"]
    market: "US"
  task: "sentiment"
expected:
  - sentiment_score >= -1.0 and sentiment_score <= 1.0
  - analysis.summary is not empty
  - analysis.confidence > 0
  - sources.length > 0
  - execution_time_ms < 10000
```

### 시나리오 2: 투자 리서치 (피어 비교 포함)
```yaml
name: "fingpt_research_with_peers"
setup:
  - mock_data_source("sec_filing", ticker="AAPL")
  - mock_data_source("earnings_call", ticker="AAPL")
  - mock_data_source("news", ticker="AAPL", articles=20)
  - mock_peer_data(ticker="AAPL", peers=["MSFT", "GOOGL"])
input:
  query: "애플의 투자 전망을 종합 분석하세요."
  financial_context:
    ticker: "AAPL"
    timeframe: "3m"
    data_sources: ["sec_filing", "earnings_call", "news"]
    market: "US"
    include_peers: true
  task: "research"
  depth: "deep"
expected:
  - analysis.recommendation in ["strong_buy", "buy", "hold", "sell", "strong_sell"]
  - analysis.key_findings.length >= 2
  - analysis.risk_factors.length >= 1
  - sources.length >= 3
```

### 시나리오 3: 에러 — 티커 미존재
```yaml
name: "error_ticker_not_found"
input:
  query: "분석해주세요"
  financial_context:
    ticker: "ZZZZZ_INVALID"
    timeframe: "1m"
    data_sources: ["news"]
  task: "sentiment"
expected:
  - error.failure_code == "COND_103_TICKER_NOT_FOUND"
  - error.fallback_id == "F-103-02"
```

---

## E8. Blue Node Integration

> §B.6.1 CAT-A 연동 프로토콜 (P0-2 산출물) 반영
> > LOCK (D2.0-03 §1.1): NODE는 CORE 규칙 상속, **독립 실행 불가** (LOCK-CD-08)

### 연동 프로토콜 (§B.6.1)
| 항목 | 값 |
|------|-----|
| **연동 Blue Node** | Quant Node |
| **Permission Level** | P0 (기본 활성) |
| **게이트 요구** | policy, cost, evidence |
| **우선순위** | MEDIUM |

### 호출 패턴
```
User → "삼성전자 최근 실적 분석해줘"
  → ORANGE CORE (I-1 Intent 해석: financial_analysis)
    → I-5 라우팅 → Quant Node
      → Quant Node: COND-103.execute(query="...", financial_context={ticker: "005930.KS", ...}, task="analysis")
        → 5-Gate 평가 (§B.7.1):
          [1] PolicyGate ✅ (정책 위반 없음)
          [2] CostGate ✅ (I-8 비용 한도 내)
          [3] EvidenceGate ✅ (근거 출처 충족)
          → COND-103 실행 → FinGptResponse 반환
            → Quant Node → ORANGE CORE → User
```

### 이벤트 매핑 (§B.4 lower.dot 네이밍, §B.4.1 LogEvent 8필드)

| 이벤트 | event_type | 트리거 |
|--------|-----------|--------|
| 모듈 초기화 | `cond.a.103.initialized` | initialize() 완료 |
| 분석 시작 | `cond.a.103.execute_start` | execute() 진입 |
| 분석 완료 | `cond.a.103.execute_done` | 정상 반환 |
| 분석 실패 | `cond.a.103.execute_fail` | VamosError 발생 |
| 헬스체크 | `cond.a.103.health` | health_check() 호출 |
| 모듈 종료 | `cond.a.103.shutdown` | shutdown() 호출 |

### Decision 기록 연결 (§B.8, D2.0-03 §6.0 LOCK)
- **실행 전**: `ModuleRequest.decision_id` → Decision 레코드에 참조 기록
- **실행 후**: `Decision.optional_signals` ← `{ "cond_module_id": "COND-103", "execution_ms": N, "result_type": "financial_analysis" }`
- **trace_id 필수**: decision_id 부재 시에도 trace_id로 추적 (D2.0-03 §5.2)

---

## E9. BaseModule ABC 적합성

> LOCK (§3.4 LOCK-CD-03): `initialize() / execute() / health_check() / shutdown()`
> LOCK (§3.4 LOCK-CD-04): Runnable 프로토콜 `run(input) → output, get_metadata(), health_check()`
> **CD-03 ↔ CD-04 관계**: execute()는 내부적으로 Runnable.run()을 위임, initialize()/shutdown()은 Runnable에 없는 생명주기 확장

```python
class Cond103FinGptFinance(BaseModule):
    """COND-103 FinGPT 금융AI"""

    async def initialize(self) -> Result[None, VamosError]:
        """FinGPT 모델 로드, 데이터 소스 커넥터 초기화, NER 모델 준비"""
        self._fingpt_model = await FinGptModel.load(self.config.model_variant)
        self._data_connectors = await DataConnectorFactory.create_all(
            self.config.enabled_sources
        )
        self._ner_model = await FinancialNER.load()
        self._ticker_registry = await TickerRegistry.connect()
        self._emit_event("cond.a.103.initialized")
        return Ok(None)

    async def execute(self, request: FinGptRequest) -> Result[FinGptResponse, VamosError]:
        """Runnable.run() 위임 — 금융 AI 분석 실행"""
        return await self.run(request)

    async def health_check(self) -> Result[HealthStatus, VamosError]:
        """FinGPT 모델 상태 + 데이터 소스 연결 확인"""
        model_ok = self._fingpt_model.is_loaded()
        sources_ok = all(c.is_connected() for c in self._data_connectors.values())
        return Ok(HealthStatus(healthy=model_ok and sources_ok, latency_ms=elapsed))

    async def shutdown(self) -> Result[None, VamosError]:
        """모델 해제, 데이터 커넥터 종료"""
        await self._fingpt_model.unload()
        for connector in self._data_connectors.values():
            await connector.disconnect()
        self._emit_event("cond.a.103.shutdown")
        return Ok(None)

    def get_metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            id="COND-103", version="1.0.0",
            capabilities=["sentiment_analysis", "financial_analysis", "investment_research", "sec_filing_parse"]
        )
```

---

## E10. Configuration

> LOCK (종합명세 §공통 / LOCK-CD-10): ModuleConfig 표준 필드

```python
class Cond103Config(ModuleConfig):
    """COND-103 모듈 설정"""
    # ModuleConfig 상속 (enabled, priority, max_concurrent, timeout_ms, retry_policy)
    enabled: bool = True
    priority: Literal["critical", "high", "medium", "low"] = "medium"
    max_concurrent: int = 4
    timeout_ms: int = 30000
    retry_policy: RetryPolicy = RetryPolicy(max_retries=2, backoff_ms=3000)

    # COND-103 전용 설정
    model_variant: str = "fingpt-forecaster-v3"
    enabled_sources: list[str] = ["sec_filing", "earnings_call", "news", "social", "analyst_report"]
    sec_edgar_api_key: Optional[str] = None
    news_api_endpoint: str = "https://api.financialnews.example.com"
    max_articles_per_query: int = 50
    sentiment_model: str = "fingpt-sentiment-v2"
    ner_model: str = "fin-ner-spacy-v3"
    peer_comparison_depth: int = 5
    confidence_threshold: float = 0.6
    cost_tracking_enabled: bool = True
```
